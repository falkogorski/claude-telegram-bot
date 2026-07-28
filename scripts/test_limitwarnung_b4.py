#!/usr/bin/env python3
# <!-- ROLLE: test-limitwarnung -->
"""Verhaltenstest B4 / 5.20 — die Limit-Vorwarnung des Anbieters.

**Zwei Fehler wären hier leicht zu bauen gewesen, und beide sind schon einmal
passiert.**

Der erste ist der Meldungssturm: Der Anbieter schickt seinen Limit-Zustand bei
*jedem* Lauf mit, nicht nur beim Umschlagen. Ohne Gedächtnis käme die Warnung
mit jeder Antwort — am 28.07. früh hat genau das (an anderer Stelle) zweimal je
Minute gemeldet, bis Adam es abstellen ließ.

Der zweite ist die erfundene Zahl: Ein eigener Token-Zähler kennt weder die
Höhe des Kontingents noch, was Adams Desktop-Sitzungen auf dasselbe Konto
buchen. Er sähe aus wie eine Auskunft und wäre eine Schätzung.
"""
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b4-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []
QUELLE = Path(bot.__file__).read_text(encoding="utf-8")


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


class _Info:
    def __init__(self, status, art="five_hour", anteil=None, resets_at=None):
        self.status = status
        self.rate_limit_type = art
        self.utilization = anteil
        self.resets_at = resets_at


class _Ereignis:
    def __init__(self, info):
        self.rate_limit_info = info


def _melden(info):
    """Ruft die Meldefunktion auf und fängt ab, was an Adam gegangen wäre."""
    gesendet = []
    echt = bot.send_chunked

    async def _fang(chat_id, text, **kw):
        gesendet.append(text)
    bot.send_chunked = _fang
    try:
        asyncio.run(bot._limit_warnung_melden(1, None, _Ereignis(info)))
    finally:
        bot.send_chunked = echt
    return gesendet


def _gruener_bereich_schweigt():
    bot._LIMIT_GEMELDET.clear()
    assert _melden(_Info("allowed")) == [], \
        "im grünen Bereich wird gemeldet — das wäre Dauerfunk"


def _warnung_kommt_genau_einmal():
    """**Der Kern.** Der Zustand kommt mit jeder Antwort; die Meldung darf
    es nicht."""
    bot._LIMIT_GEMELDET.clear()
    reset = time.time() + 7200
    erst = _melden(_Info("allowed_warning", anteil=0.87, resets_at=reset))
    assert len(erst) == 1, f"die erste Warnung fehlt: {erst}"
    assert "87 %" in erst[0], f"der gemeldete Anteil fehlt: {erst[0]}"

    for _ in range(5):
        assert _melden(_Info("allowed_warning", anteil=0.87, resets_at=reset)) == [], \
            "dieselbe Warnung wird wiederholt — genau der Meldungssturm"

    # Kippt der Zustand, muss sie aber wieder durchkommen.
    hart = _melden(_Info("rejected", anteil=1.0, resets_at=reset))
    assert len(hart) == 1 and "aufgebraucht" in hart[0], \
        f"die Verschärfung wird verschluckt: {hart}"


def _entwarnung_nur_nach_warnung():
    """Eine gute Nachricht ohne vorherige schlechte ist selbst das Rauschen."""
    bot._LIMIT_GEMELDET.clear()
    assert _melden(_Info("allowed")) == []
    _melden(_Info("allowed_warning", anteil=0.9, resets_at=time.time() + 600))
    zurueck = _melden(_Info("allowed"))
    assert len(zurueck) == 1 and "grünen Bereich" in zurueck[0], \
        f"nach einer Warnung fehlt die Entwarnung: {zurueck}"


def _getrennte_kontingente_verdecken_sich_nicht():
    """Fünf-Stunden-Fenster und Wochenkontingent sind zwei verschiedene Dinge.
    Ein gemeinsames Gedächtnis hätte die zweite Warnung geschluckt."""
    bot._LIMIT_GEMELDET.clear()
    a = _melden(_Info("allowed_warning", art="five_hour", resets_at=1))
    b = _melden(_Info("allowed_warning", art="seven_day_opus", resets_at=2))
    assert len(a) == 1 and len(b) == 1, "das zweite Kontingent wurde verschluckt"
    assert "Fünf-Stunden" in a[0] and "Opus" in b[0], \
        f"die Kontingente werden nicht unterschieden: {a} / {b}"


def _keine_erfundene_prozentzahl():
    """Schickt der Anbieter keinen Anteil mit, wird auch keiner genannt."""
    bot._LIMIT_GEMELDET.clear()
    txt = _melden(_Info("allowed_warning", anteil=None, resets_at=time.time() + 60))[0]
    assert "%" not in txt, f"es steht eine ausgedachte Quote in der Meldung: {txt}"


def _zeit_wird_menschlich_genannt():
    """Eine Unix-Zeit in einer Telegram-Meldung ist keine Auskunft — und
    vorgelesen vollends unbrauchbar."""
    assert "Minuten" in bot._limit_zeitspanne(time.time() + 600)
    assert "etwa einer Stunde" in bot._limit_zeitspanne(time.time() + 3600)
    assert "etwa 3 Stunden" in bot._limit_zeitspanne(time.time() + 3 * 3600)
    assert bot._limit_zeitspanne(None) == "", "ohne Zeitangabe wird etwas erfunden"
    for probe in (600, 3600, 18000):
        assert str(int(time.time() + probe))[:6] not in bot._limit_zeitspanne(
            time.time() + probe), "die rohe Unix-Zeit steht in der Meldung"


def _kein_eigener_zaehler():
    """5.20 wurde am 24.07. bewusst neu gefasst: **kein Ersatz-Zähler**, nur
    das Weiterreichen echter Anbieter-Warnungen. Eine selbstgerechnete
    Vorhersage sähe aus wie eine Auskunft und wäre geraten."""
    block = QUELLE.split("async def _limit_warnung_melden")[1].split("\ndef ")[0]
    for verboten in ("KONTINGENT_GESAMT", "geschaetzt", "* 0.8", "budget"):
        assert verboten not in block, \
            f"die Meldung rechnet selbst (`{verboten}`) statt weiterzureichen"


def _fehlendes_sdk_bricht_den_start_nicht():
    """Ein harter Import hätte aus einem fehlenden ZUSATZSIGNAL einen
    Startabbruch gemacht: Der Bot bliebe stumm, weil eine Warnung fehlt."""
    assert "except ImportError:" in QUELLE.split("RateLimitEvent as _RateLimitEvent")[1][:200], \
        "der Import der Limit-Warnung ist hart — ein älteres SDK legte den Bot lahm"
    assert "_RateLimitEvent is not None and isinstance" in QUELLE, \
        "der Zweig prüft nicht, ob das Ereignis überhaupt bekannt ist"


def _verbrauch_zaehlt_den_zwischenspeicher_mit():
    """**GEMESSEN 28.07.:** Über 442 Antworten wies der Zähler 63 Eingabe-Token
    je Antwort aus — allein der Systemprompt ist ein Vielfaches. `input_tokens`
    zählt nur den frisch übertragenen Teil; der weitaus größte Anteil kommt aus
    dem Zwischenspeicher und fehlte komplett."""
    class _R:
        usage = {"input_tokens": 10, "output_tokens": 20,
                 "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 700}
        total_cost_usd = 1.5

    bot._USAGE_FILE = _TMP / "usage.json"
    bot._record_usage("opus", _R())
    import json
    tag = list(json.loads(bot._USAGE_FILE.read_text()).values())[0]["opus"]
    assert tag.get("cache_read") == 5000 and tag.get("cache_write") == 700, \
        f"der Zwischenspeicher wird nicht mitgezählt: {tag}"
    assert tag["input"] == 10, "frische und zwischengespeicherte Eingabe werden vermischt"


def _nennwert_ist_als_solcher_gekennzeichnet():
    """Über vierzehn Tage summiert sich der Listenpreis auf gut 3400 Dollar.
    Ohne Kennzeichnung liest sich das wie eine Rechnung — im Abo wird nichts
    davon berechnet."""
    assert "Abo — nicht berechnet" in QUELLE, \
        "die Verbrauchsanzeige nennt den Nennwert wie abgebuchtes Geld"
    assert 'f"  Kosten:   ~${cost:.4f}"' not in QUELLE, \
        "die alte, missverständliche Kosten-Zeile steht noch da"


check("grüner Bereich schweigt", _gruener_bereich_schweigt)
check("Warnung kommt GENAU EINMAL je Zustand (Dämpfer)", _warnung_kommt_genau_einmal)
check("Entwarnung nur nach vorheriger Warnung", _entwarnung_nur_nach_warnung)
check("getrennte Kontingente verdecken sich nicht",
      _getrennte_kontingente_verdecken_sich_nicht)
check("keine erfundene Prozentzahl", _keine_erfundene_prozentzahl)
check("Zeit wird menschlich genannt, nicht als Unix-Zeit",
      _zeit_wird_menschlich_genannt)
check("kein eigener Zähler — nur weitergereicht (5.20-Neufassung)",
      _kein_eigener_zaehler)
check("fehlendes SDK-Signal bricht den Start nicht",
      _fehlendes_sdk_bricht_den_start_nicht)
check("Verbrauch zählt den Zwischenspeicher mit (gemessener Fehler)",
      _verbrauch_zaehlt_den_zwischenspeicher_mit)
check("Nennwert ist als Nennwert gekennzeichnet",
      _nennwert_ist_als_solcher_gekennzeichnet)

print()
if fails:
    print(f"❌ {len(fails)} B4-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B4-Limitwarnungs-Tests bestanden.")
