#!/usr/bin/env python3
# <!-- ROLLE: test-websuche-ausfall -->
"""Die Suche muss ihren eigenen Ausfall melden koennen.

**Anlass (27.08.2026):** Zwoelf von fuenfzehn Anfragen meldeten [Keine
Treffer]. In Wahrheit waren **alle vier** allgemeinen Zulieferer tot — zwei
gedrosselt, zwei abgestuerzt. Claudia hielt es fuer [nichts gefunden] und hat
Adam vier Stunden lang auf dieser Grundlage geantwortet.

**Engywucks Auflage ist die Klasse, nicht der Anlass:** *[Gesucht, nichts
gefunden] und [gar nicht gesucht] duerfen nicht denselben Rueckgabewert
haben.* Genau das wird hier gemessen — **ausgefuehrt, nicht gelesen**: Die
Entscheidung sitzt in `bot.suchlage()`, einer eigenen Funktion, damit ein
Pruefer sie erreichen kann.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="websuche-"))
# **Hart gesetzt, nie setdefault** (F-18): setdefault erbt im Zweifel den
# echten Wert aus der Umgebung, und genau das hat am 25.07. einen Fehlalarm
# erzeugt.
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails: list[str] = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


_AUS = [["brave", "Suspended: too many requests"], ["duckduckgo", "CAPTCHA"],
        ["google cse", "unexpected crash"], ["startpage", "unexpected crash"]]


def _totalausfall_ist_kein_nichts_gefunden():
    """**Der Kern.** Die genaue Lage vom 27.08., mit den echten Gruenden."""
    lage, text = bot.suchlage({"results": [], "unresponsive_engines": _AUS}, 15)
    assert lage == "ausgefallen", f"Totalausfall gilt als {lage!r}"
    assert "nicht ausgefuehrt" in text.lower() or "nicht ausgef" in text.lower(), \
        f"der Text sagt nicht, dass gar nicht gesucht wurde: {text!r}"
    for name, grund in _AUS:
        assert name in text, f"der ausgefallene Zulieferer {name} fehlt im Text"
        assert grund.split(":")[0] in text, f"der Grund fuer {name} fehlt"


def _der_text_klingt_nicht_nach_nichts_gefunden():
    """**Die Gegenrichtung, und sie ist die eigentliche Zusage.**

    Ein Modell liest diesen Text. Claudia hat vier Stunden lang die falsche
    Auskunft weitergegeben, **weil sie plausibel klang** — der Unterschied
    muss deshalb im Wortlaut stehen, nicht zwischen den Zeilen.
    """
    _, text = bot.suchlage({"results": [], "unresponsive_engines": _AUS}, 15)
    klein = text.lower()
    assert "keine treffer" not in klein, \
        "der Ausfalltext enthaelt [keine Treffer] - genau die Verwechslung"
    assert "unbeantwortet" in klein or "kein suchergebnis" in klein, \
        f"der Text sagt nicht, dass die Frage offen ist: {text!r}"


def _echt_nichts_gefunden_bleibt_nichts_gefunden():
    """Ohne Ausfaelle ist eine leere Trefferliste eine ehrliche Antwort."""
    lage, text = bot.suchlage({"results": [], "unresponsive_engines": []}, 15)
    assert lage == "ok", f"echtes Nichtfinden gilt als {lage!r}"
    assert text == "", f"unnoetiger Hinweis: {text!r}"


def _teilausfall_wird_vermerkt():
    """Treffer aus wenigen Zulieferern sind schmaler, als sie aussehen."""
    lage, text = bot.suchlage(
        {"results": [{"title": "x"}], "unresponsive_engines": _AUS}, 6)
    assert lage == "duenn", f"Teilausfall gilt als {lage!r}"
    assert "2" in text, f"die Zahl der Antwortenden fehlt: {text!r}"


def _gesunde_suche_schweigt():
    """**Ein Pruefer, der immer redet, wird ueberlesen.**"""
    lage, text = bot.suchlage(
        {"results": [{"title": "x"}], "unresponsive_engines": []}, 15)
    assert lage == "ok" and text == "", f"Fehlalarm bei gesunder Suche: {text!r}"


def _fehlende_zahl_bricht_nichts():
    """Ist die Zulieferer-Zahl nicht zu ermitteln, wird trotzdem gemeldet."""
    lage, text = bot.suchlage({"results": [], "unresponsive_engines": _AUS}, None)
    assert lage == "ausgefallen", "ohne Zahl faellt die Ausfallmeldung aus"
    lage2, text2 = bot.suchlage(
        {"results": [{"title": "x"}], "unresponsive_engines": _AUS}, None)
    assert lage2 == "duenn" and text2, "ohne Zahl faellt der Teilausfall-Vermerk aus"


def _seltsame_formen_brechen_nicht():
    """Der Dienst darf sein Format aendern, ohne dass hier etwas stirbt."""
    for roh in ([], None, ["nurname"], [["a"]], [["a", "b", "c"]]):
        lage, _ = bot.suchlage({"results": [], "unresponsive_engines": roh}, 15)
        assert lage in ("ok", "ausgefallen"), f"unerwartete Lage bei {roh!r}"


check("Totalausfall ist kein [nichts gefunden]", _totalausfall_ist_kein_nichts_gefunden)
check("der Ausfalltext ist auch fuer ein Modell eindeutig",
      _der_text_klingt_nicht_nach_nichts_gefunden)
check("echtes Nichtfinden bleibt Nichtfinden", _echt_nichts_gefunden_bleibt_nichts_gefunden)
check("Teilausfall wird vermerkt", _teilausfall_wird_vermerkt)
check("gesunde Suche schweigt (Gegenrichtung)", _gesunde_suche_schweigt)
check("fehlende Zulieferer-Zahl bricht nichts", _fehlende_zahl_bricht_nichts)
check("seltsame Formen brechen nicht", _seltsame_formen_brechen_nicht)

print()
if fails:
    print(f"❌ {len(fails)} Websuche-Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Websuche-Ausfall-Tests bestanden.")
