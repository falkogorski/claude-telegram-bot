#!/usr/bin/env python3
"""Verhaltenstest 5.9 — Emoji-Reaktionen (Vokabular v2.1).

Prüft die Eigenschaften, an denen der Punkt hängt:
  (1) Reaktion auf registrierte offene Frage → Job in der Queue (= die Antwort),
      Frage ausgetragen, 5.2-Record angelegt.
  (2) Stille Wertschätzung (❤️) ohne offene Frage → KEIN Job, kein Lärm.
  (3) VS16-Normalisierung: ❤ (ohne Selector) trifft dieselbe Bedeutung.
  (4) Unbekanntes Emoji → freundliche Nachfrage, NIE ein geratener Lauf.
  (5) Permission-Vorrang: wartende Freigabe frisst 👍/👎 — kein 5.9-Job daneben.
  (6) Ziffern-Knopf (opt:N) → Job „Option N gewählt".

Aufruf:  .venv/bin/python scripts/test_reactions_5_9.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = Path(tempfile.mkdtemp(prefix="react59-"))
os.environ["PENDING_DIR"] = str(_TMP / "pending")
os.environ["QUESTIONS_FILE"] = str(_TMP / "open_questions.json")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"  # erzwungen: hermetisch (nie geerbte echte UID)

from telegram import ReactionTypeEmoji  # noqa: E402

import bot        # noqa: E402
import pending    # noqa: E402
import reactions  # noqa: E402

UID, CHAT = 4242, 4242


class FakeBot:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_message(self, **kw):
        self.sent.append(kw)
        return SimpleNamespace(message_id=777)

    async def set_message_reaction(self, **kw):
        self.reactions_set = getattr(self, "reactions_set", [])
        self.reactions_set.append(kw)


def _rx_update(emoji: str, message_id: int, fake_bot: FakeBot,
               old: list[str] | None = None):
    rx = SimpleNamespace(
        chat=SimpleNamespace(id=CHAT),
        user=SimpleNamespace(id=UID),
        message_id=message_id,
        old_reaction=[ReactionTypeEmoji(emoji=e) for e in (old or [])],
        new_reaction=[ReactionTypeEmoji(emoji=emoji)] if emoji else [],
    )
    return SimpleNamespace(message_reaction=rx, get_bot=lambda: fake_bot)


def _fail(msg: str) -> None:
    print(f"✗ {msg}")
    sys.exit(1)


async def main() -> None:
    bot._ensure_worker = lambda uid: None          # kein echter Worker im Test
    fake = FakeBot()
    mb = bot._get_mailbox(UID)

    # (1) Reaktion 👍 auf registrierte Frage → Job = Antwort
    reactions.register_question(CHAT, 500, "Soll ich das so umsetzen?")
    await bot.on_reaction(_rx_update("👍", 500, fake), None)
    if len(mb.queue) != 1:
        _fail("Reaktion auf offene Frage hat keinen Job erzeugt")
    job = mb.queue.pop()
    if "ANTWORT auf deine offene Frage" not in job.text or "Ja / passt" not in job.text:
        _fail("Job-Prompt trägt Bedeutung/Fragen-Bezug nicht")
    if reactions.pop_question(CHAT, 500) is not None:
        _fail("Frage wurde nicht ausgetragen")
    if job.pending_key is None or not pending._path(job.pending_key).exists():
        _fail("Reaktions-Job wurde nicht 5.2-persistiert")
    pending.resolve(job.pending_key)
    print("✓ Antwort-Reaktion auf offene Frage → Job mit Bedeutung + Bezug, persistiert")

    # (2) ❤️ ohne offene Frage → still (kein Job, keine Nachricht)
    await bot.on_reaction(_rx_update("❤️", 501, fake), None)
    if mb.queue or fake.sent:
        _fail("stille Wertschätzung hat Job/Nachricht erzeugt")
    print("✓ Wertschätzung ohne Frage bleibt still — kein Lauf, kein Lärm")

    # (3) ❤ OHNE VS16 auf eine offene Frage → wird erkannt und beantwortet
    reactions.register_question(CHAT, 502, "Gefällt dir der Entwurf?")
    await bot.on_reaction(_rx_update("❤", 502, fake), None)
    if len(mb.queue) != 1:
        _fail("VS16-lose Reaktion auf Frage nicht erkannt")
    job = mb.queue.pop()
    if "Herzlichen Dank" not in job.text:
        _fail("VS16-Normalisierung liefert falsche Bedeutung")
    pending.resolve(job.pending_key)
    print("✓ VS16-Normalisierung: ❤ trifft ❤️-Bedeutung")

    # (4) Unbekanntes Emoji → Nachfrage statt Raten
    await bot.on_reaction(_rx_update("😀", 503, fake), None)
    if mb.queue:
        _fail("unbekanntes Emoji hat einen Lauf ausgelöst (geraten!)")
    if not fake.sent or "kenne ich noch nicht" not in fake.sent[-1]["text"]:
        _fail("keine freundliche Nachfrage bei unbekanntem Emoji")
    print("✓ Unbekanntes Emoji → freundliche Nachfrage, kein Raten")

    # (5) Permission-Vorrang: wartende Freigabe frisst 👍
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    bot.SESSIONS[UID] = SimpleNamespace(
        message_permissions={600: "req-1"},
        pending_permissions={"req-1": (loop, fut)},
        logger=None,
    )
    await bot.on_reaction(_rx_update("👍", 600, fake), None)
    await asyncio.sleep(0)  # call_soon_threadsafe abwarten
    if not fut.done() or fut.result() != "allow":
        _fail("Permission wurde nicht per Reaktion aufgelöst")
    if mb.queue:
        _fail("Permission-Reaktion hat zusätzlich einen 5.9-Job erzeugt")
    bot.SESSIONS.pop(UID, None)
    print("✓ Permission-Vorrang: 👍 löst Freigabe, kein Doppel-Job")

    # (6) Ziffern-Knopf → Job „Option N"
    answered: list = []

    async def _answer(*a, **k):
        answered.append(a)

    q = SimpleNamespace(
        from_user=SimpleNamespace(id=UID),
        data="opt:2",
        answer=_answer,
        message=SimpleNamespace(chat_id=CHAT, message_id=700,
                                text="1. Rot\n2. Blau\nWelche Farbe?"),
        get_bot=lambda: fake,
    )
    await bot.on_option_callback(SimpleNamespace(callback_query=q), None)
    if len(mb.queue) != 1:
        _fail("Options-Knopf hat keinen Job erzeugt")
    job = mb.queue.pop()
    if "Option 2" not in job.text:
        _fail("Options-Job nennt die gewählte Option nicht")
    pending.resolve(job.pending_key)
    print("✓ Ziffern-Knopf → Job mit gewählter Option")

    # (7) Widerruf: Reaktion entfernt, Job wartet noch → storniert + Quittung
    reactions.register_question(CHAT, 800, "Passt der Plan so?")
    await bot.on_reaction(_rx_update("👍", 800, fake), None)
    assert len(mb.queue) == 1
    fake.sent.clear()
    await bot.on_reaction(_rx_update("", 800, fake, old=["👍"]), None)
    if mb.queue:
        _fail("Widerruf hat den wartenden Job nicht storniert")
    if not fake.sent or "storniert" not in fake.sent[-1]["text"]:
        _fail("Widerruf ohne Quittung")
    print("✓ Widerruf: wartender Job storniert + Quittung")

    # (8) Ersetzen: 👍 → 👎 in einem Update → neuer Job nennt die Ersetzung
    fake.sent.clear()
    bot.BOT_MSGS[(CHAT, 801)] = "Soll ich den Entwurf so lassen?"
    await bot.on_reaction(_rx_update("👎", 801, fake, old=["👍"]), None)
    if len(mb.queue) != 1:
        _fail("Ersetzte Reaktion hat keinen Job erzeugt")
    job = mb.queue.pop()
    if "ERSETZT" not in job.text or "Nein" not in job.text:
        _fail("Ersetzungs-Job nennt Wechsel/Bedeutung nicht")
    pending.resolve(job.pending_key)
    print("✓ Ersetzen: neuer Job mit Ersetzungs-Vermerk")

    # (7) H3: 👍 OHNE registrierte offene Frage → stille Quittung, KEIN Lauf
    bot.BOT_MSGS[(CHAT, 520)] = "Bin gleich soweit."
    await bot.on_reaction(_rx_update("👍", 520, fake), None)
    if mb.queue:
        _fail("👍 ohne offene Frage hat einen Modelllauf ausgelöst (H3)")
    if not getattr(fake, "reactions_set", None):
        _fail("👍 ohne offene Frage bekam keine sichtbare Quittung (H3)")
    print("✓ H3: 👍 ohne offene Frage → stille Quittung statt Modelllauf")

    # (8) H3: 👍 AUF eine registrierte Frage → weiterhin Antwort an den Agenten
    reactions.register_question(CHAT, 521, "Soll ich das so bauen?")
    await bot.on_reaction(_rx_update("👍", 521, fake), None)
    if len(mb.queue) != 1:
        _fail("👍 auf eine offene Frage löste KEINEN Lauf aus (H3 zu scharf)")
    mb.queue.clear()
    print("✓ H3: 👍 auf eine offene Frage bleibt die Antwort an den Agenten")

    # (9) H3: Handlungs-Reaktion ohne Frage UND ohne Bezugstext → nie raten,
    #     aber auch nicht verschlucken: kurze Rückfrage statt Modelllauf.
    fake.sent.clear()
    bot.BOT_MSGS.pop((CHAT, 522), None)
    await bot.on_reaction(_rx_update("👎", 522, fake), None)
    if mb.queue:
        _fail("Lauf ohne jeden Bezugstext gestartet — das ist Raten (H3)")
    if not any("bezieht sie sich" in (m.get("text") or "") for m in fake.sent):
        _fail("Reaktion ohne Bezugstext wurde stillschweigend verschluckt (H3)")
    print("✓ H3: ohne Bezugstext keine Lauf-Raterei, sondern kurze Rückfrage")

    print("\nALLE TEILPRÜFUNGEN BESTANDEN")


if __name__ == "__main__":
    asyncio.run(main())
