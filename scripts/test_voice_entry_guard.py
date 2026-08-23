#!/usr/bin/env python3
"""Verhaltenstest zum Voice-Eingangsschutz (Befund 20.07.2026).

Prüft die eine Eigenschaft, an der alles hängt: Eine Sprachnachricht, die es
nie bis zur Transkription geschafft hat, wird beim nächsten Start **gemeldet,
aber niemals nachgeholt**. Würde sie nachgeholt, bekäme Claude den Platzhalter
statt Adams Anliegen vorgelegt — schlimmer als die Stille, die wir beheben.

Aufruf:  .venv/bin/python scripts/test_voice_entry_guard.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = tempfile.mkdtemp(prefix="voiceguard-")
os.environ["PENDING_DIR"] = _TMP
os.environ["TELEGRAM_BOT_TOKEN"] = ("1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"  # erzwungen: hermetisch (nie geerbte echte UID)

import bot          # noqa: E402
import pending      # noqa: E402


class FakeBot:
    pass


class FakeApp:
    bot = FakeBot()


def _fail(msg: str) -> None:
    print(f"✗ {msg}")
    sys.exit(1)


def main() -> None:
    uid, chat = 4242, 4242

    # (1) Eingangs-Eintrag einer Sprachnachricht, die nie transkribiert wurde.
    k_voice = pending.make_key(chat, 900)
    pending.record(k_voice, {
        "user_id": uid, "chat_id": chat, "message_id": 900,
        "text": bot.VOICE_STAGE_PLACEHOLDER, "stage": bot.VOICE_STAGE,
        "voice_duration": 42, "received_at": time.time() - 30,
        "message_date": time.time() - 30,
        "audio_path": "/home/claudebot/Downloads/claude-uploads/x_voice.oga",
    })
    # (2) Normale Textnachricht daneben — die MUSS weiterhin nachgeholt werden.
    k_text = pending.make_key(chat, 901)
    pending.record(k_text, {
        "user_id": uid, "chat_id": chat, "message_id": 901,
        "text": "Wie wird das Wetter morgen?", "received_at": time.time() - 20,
    })

    bot.MAILBOXES.clear()
    meldung = bot._reconcile_pending(FakeApp())

    queue = list(bot._get_mailbox(uid).queue)
    texte = [j.text for j in queue]

    if bot.VOICE_STAGE_PLACEHOLDER in texte:
        _fail("Platzhalter wurde nachgeholt — Claude bekäme eine leere Hülle statt Adams Anliegen")
    if "Wie wird das Wetter morgen?" not in texte:
        _fail("normale Nachricht wurde NICHT nachgeholt — Kollateralschaden")
    print("✓ Platzhalter nicht nachgeholt, normale Nachricht schon")

    if "🎙️" not in meldung:
        _fail("keine Meldung über die unterbrochene Sprachnachricht — wieder Stille")
    if "42 Sekunden" not in meldung:
        _fail("Dauer fehlt in der Meldung — Adam kann sie nicht zuordnen")
    if "verloren ist nichts" not in meldung:
        _fail("Meldung beruhigt nicht über das gesicherte Audio")
    print("✓ Meldung nennt Uhrzeit, Dauer und den Verbleib des Audios")

    if Path(_TMP, f"{k_voice}.json").exists():
        _fail("Voice-Eintrag blieb liegen — der Bot meldete ihn bei JEDEM Start erneut")
    print("✓ Eintrag aufgelöst — kein Dauer-Nörgeln bei künftigen Starts")

    # (3) Abbruchzweig: saubere Fehlermeldung an Adam → Eintrag muss weg sein.
    k_err = pending.make_key(chat, 902)
    pending.record(k_err, {"user_id": uid, "chat_id": chat, "message_id": 902,
                           "text": bot.VOICE_STAGE_PLACEHOLDER, "stage": bot.VOICE_STAGE})
    bot._resolve_voice_stage(k_err)
    if Path(_TMP, f"{k_err}.json").exists():
        _fail("Abbruchzweig räumt den Eingangs-Eintrag nicht ab")
    print("✓ Abbruch mit Fehlermeldung räumt den Eintrag ab")

    # (4) Nachtragen des Audio-Pfads darf einen erledigten Eintrag NICHT wiederbeleben.
    bot._note_voice_audio(k_err, Path("/tmp/irgendwas.oga"))
    if Path(_TMP, f"{k_err}.json").exists():
        _fail("erledigter Eintrag wurde durch den Audio-Nachtrag wiederbelebt")
    print("✓ Audio-Nachtrag belebt keinen erledigten Eintrag wieder")

    print("\nALLE TEILPRÜFUNGEN BESTANDEN")


if __name__ == "__main__":
    main()
