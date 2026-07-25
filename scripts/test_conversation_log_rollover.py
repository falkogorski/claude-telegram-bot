#!/usr/bin/env python3
"""Regressionstest: Gesprächs-Log über den Tageswechsel (Fund 22.07.2026).

Der Bug: `ConversationLogger` fror die Zieldatei im __init__ ein — eine
langlebige Session schrieb tagelang in die Datei ihres Starttags
(2026-07-20.md enthielt Einträge bis in den 22.07.). Zusätzlich trugen die
Turn-Kopfzeilen kein Datum, Tagesgrenzen waren unsichtbar.

Dieser Test lässt eine Session über zwei simulierte Mitternachten laufen und
prüft: jeder Eintrag landet in der Datei seines Tages, die alte Datei erhält
eine Verweiszeile, die neue beginnt mit Kopfzeile, und jeder Turn-Kopf trägt
das volle Datum.

Aufruf:  .venv/bin/python scripts/test_conversation_log_rollover.py
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
import tempfile
import time as _real_time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = Path(tempfile.mkdtemp(prefix="convlog-"))
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP)
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"  # erzwungen: hermetisch (nie geerbte echte UID)

import bot  # noqa: E402


class FakeTime:
    """Steuerbare Uhr: strftime liefert die gestellte Zeit, alles andere
    (time(), sleep(), …) läuft unverändert gegen das echte time-Modul."""

    def __init__(self) -> None:
        self.current = _dt.datetime(2026, 7, 20, 23, 58, 0)

    def strftime(self, fmt: str, t=None) -> str:  # noqa: ANN001
        return self.current.strftime(fmt)

    def __getattr__(self, name: str):
        return getattr(_real_time, name)


def _fail(msg: str) -> None:
    print(f"✗ {msg}")
    sys.exit(1)


def main() -> None:
    clock = FakeTime()
    bot.time = clock  # ConversationLogger nutzt bots modul-globales `time`

    d20 = _TMP / "2026-07-20.md"
    d21 = _TMP / "2026-07-21.md"
    d22 = _TMP / "2026-07-22.md"

    # ── Tag 1, kurz vor Mitternacht ──────────────────────────────────────
    logger = bot.ConversationLogger(4242)
    logger.log_user("Nachricht vor Mitternacht")

    if not d20.exists():
        _fail("Tagesdatei des Starttags wurde nicht angelegt")
    t20 = d20.read_text(encoding="utf-8")
    if not t20.startswith("# Claude Telegram Log – 2026-07-20"):
        _fail("Kopfzeile der Starttag-Datei fehlt")
    if "## Session · 2026-07-20 23:58:00" not in t20:
        _fail("Session-Kopf trägt nicht das volle Datum")
    if "## Du · 2026-07-20 23:58:00" not in t20:
        _fail("Turn-Kopf trägt nicht das volle Datum")
    print("✓ Starttag: Kopfzeile, Session- und Turn-Kopf mit vollem Datum")

    # ── Mitternacht Nr. 1: dieselbe Session schreibt weiter ─────────────
    clock.current = _dt.datetime(2026, 7, 21, 0, 3, 12)
    logger.start_assistant_turn()
    logger.log_assistant_text("Antwort nach Mitternacht")
    logger.end_turn()

    if not d21.exists():
        _fail("neue Tagesdatei nach Mitternacht wurde nicht angelegt")
    t21 = d21.read_text(encoding="utf-8")
    if not t21.startswith("# Claude Telegram Log – 2026-07-21"):
        _fail("Kopfzeile der neuen Tagesdatei fehlt")
    if "## Claude · 2026-07-21 00:03:12" not in t21:
        _fail("Turn nach Mitternacht steht nicht in der Datei seines Tages")
    if "Antwort nach Mitternacht" not in t21:
        _fail("Inhalt nach Mitternacht fehlt in der neuen Tagesdatei")
    t20 = d20.read_text(encoding="utf-8")
    if "→ fortgesetzt in 2026-07-21.md" not in t20:
        _fail("Verweiszeile in der alten Tagesdatei fehlt")
    if "Antwort nach Mitternacht" in t20:
        _fail("Eintrag des neuen Tages steht fälschlich in der alten Datei (der Bug)")
    print("✓ Mitternacht 1: neuer Tag → neue Datei mit Kopfzeile, alte mit Verweis")

    # ── Gleicher Tag, weitere Einträge: keine doppelten Köpfe/Verweise ──
    clock.current = _dt.datetime(2026, 7, 21, 9, 49, 20)
    logger.log_user("Nachricht am Vormittag")
    t21 = d21.read_text(encoding="utf-8")
    if t21.count("# Claude Telegram Log – 2026-07-21") != 1:
        _fail("Datei-Kopfzeile wurde dupliziert")
    if "## Du · 2026-07-21 09:49:20" not in t21:
        _fail("Vormittags-Eintrag fehlt oder trägt falschen Stempel")
    if "fortgesetzt" in t21:
        _fail("Verweiszeile fälschlich in der laufenden Tagesdatei")
    print("✓ Folgeeinträge am selben Tag: keine Duplikate, korrekte Stempel")

    # ── Mitternacht Nr. 2: mehrtägige Session rollt erneut ──────────────
    clock.current = _dt.datetime(2026, 7, 22, 8, 11, 12)
    logger.log_user("Nachricht am dritten Tag")
    if not d22.exists():
        _fail("zweiter Tageswechsel wurde nicht behandelt")
    t22 = d22.read_text(encoding="utf-8")
    if "## Du · 2026-07-22 08:11:12" not in t22:
        _fail("Eintrag des dritten Tags steht nicht in seiner Datei")
    if "→ fortgesetzt in 2026-07-22.md" not in d21.read_text(encoding="utf-8"):
        _fail("Verweiszeile beim zweiten Tageswechsel fehlt")
    print("✓ Mitternacht 2: mehrtägige Session rollt sauber weiter")

    # ── Kompatibilität: Log-Parser erkennen die Köpfe weiterhin ─────────
    for head in ("## Session ·", "## Du ·", "## Claude ·"):
        joined = t20 + t21 + t22
        if not any(l.startswith(head) for l in joined.splitlines()):
            _fail(f"Kopf-Präfix {head!r} nicht mehr vorhanden — Parser bräche")
    print("✓ Kopf-Präfixe unverändert — startswith-Parser bleiben kompatibel")

    print("\nAlle Prüfungen bestanden.")


if __name__ == "__main__":
    main()
