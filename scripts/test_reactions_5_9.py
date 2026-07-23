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
os.environ.setdefault("ALLOWED_USER_IDS", "4242")

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


def _rx_update(emoji: str, message_id: int, fake_bot: FakeBot):
    rx = SimpleNamespace(
        chat=SimpleNamespace(id=CHAT),
        user=SimpleNamespace(id=UID),
        message_id=message_id,
        new_reaction=[ReactionTypeEmoji(emoji=emoji)],
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

    print("\nALLE TEILPRÜFUNGEN BESTANDEN")


if __name__ == "__main__":
    asyncio.run(main())
