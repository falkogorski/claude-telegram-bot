#!/usr/bin/env python3
# <!-- ROLLE: test-pin-bezug -->
"""Punkt 5.13 — der Rueckweg zur angepinnten Nachricht.

**Was gefehlt hat:** Der Handler legte Zeitstempel und Text ab, aber keinen
Verweis auf das Original. Das Akzeptanzkriterium verlangt einen Zitat-Bezug,
und der Grund ist praktisch — ein Merker ohne Rueckweg laesst sich spaeter
nicht mehr im Verlauf verorten.

**Die Pruefung, auf die es ankommt, ist die zweite:** Im privaten Chat gibt es
keine adressierbare Nachricht, also **darf dort kein Link stehen**. Ein Link,
der ins Leere fuehrt, waere schlechter als die blosse Nummer — er sieht aus
wie ein Rueckweg und ist keiner.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="p513-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"\u2713 {name}")
    except AssertionError as e:
        print(f"\u2717 {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"\u2717 {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _upd(chat_id):
    return type("U", (), {"effective_chat": type("C", (), {"id": chat_id})()})()


def _pin(mid):
    return type("P", (), {"message_id": mid})()


def _gruppe_bekommt_einen_klickbaren_rueckweg():
    b = bot._pin_bezug(_upd(-1001234567890), _pin(4242))
    assert "tg://privatepost" in b, f"kein Deep-Link in der Gruppe: {b}"
    assert "post=4242" in b, f"der Bezug zeigt nicht auf die Nachricht: {b}"


def _privatchat_bekommt_KEINEN_link():
    """**Der Kern.** Im Privatchat existiert keine adressierbare Nachricht."""
    b = bot._pin_bezug(_upd(4711), _pin(4242))
    assert "tg://" not in b and "http" not in b, \
        f"im Privatchat steht ein Link, der ins Leere fuehrt: {b}"
    assert "4242" in b, f"die Nachrichtennummer fehlt: {b}"


def _ohne_nachricht_kein_bezug():
    assert bot._pin_bezug(_upd(4711), _pin(None)) == "", \
        "ohne Nachrichtennummer wird ein Bezug erfunden"


def _status_nennt_keine_sekunden():
    """Nebenbefund vom 20.08.: die Zeitform-Regel gilt auch in /status."""
    quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
    assert "letzte Regung vor {silent}s" not in quelle, \
        "die Sekundenangabe in /status ist zurueck"


def _kein_dateihandle_ohne_with():
    quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
    assert 'mem_file.open("a", encoding="utf-8").write' not in quelle, \
        "das Dateihandle ohne with ist zurueck"


check("Gruppe bekommt einen klickbaren Rueckweg", _gruppe_bekommt_einen_klickbaren_rueckweg)
check("Privatchat bekommt KEINEN Link", _privatchat_bekommt_KEINEN_link)
check("ohne Nachricht kein Bezug", _ohne_nachricht_kein_bezug)
check("/status nennt keine Sekunden", _status_nennt_keine_sekunden)
check("kein Dateihandle ohne with", _kein_dateihandle_ohne_with)

print()
if fails:
    print(f"\u274c {len(fails)} 5.13-Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle 5.13-Pin-Bezug-Tests bestanden.")
