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
    except Exception as e:
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
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


class _AttrappenBot:
    """Der Rand: was hinausgegangen waere. Erfindet nichts."""

    def __init__(self):
        self.texte = []

    async def send_message(self, chat_id=None, text=None, **kw):
        self.texte.append(text)
        return type("M", (), {"message_id": 1})()


def _sitzung(attrappe):
    s = object.__new__(bot.UserSession)
    s.bot = attrappe
    s.user_id = 1
    return s


def _melden(info):
    """Ruft die Meldefunktion auf und faengt ab, was an Adam gegangen waere.

    **KORRIGIERT 18.08.2026.** Die urspruengliche Fassung ersetzte
    `bot.send_chunked` durch eine Attrappe mit der Signatur
    `(chat_id, text, **kw)` — also mit **genau der falschen Arität, die der
    Fehler im Code hatte**. Damit war der Fehler per Konstruktion unsichtbar:
    Zehn gruene Zeilen ueber eine Funktion, die in Wirklichkeit vor dem ersten
    `await` mit TypeError abbrach und nullmal meldete.

    Jetzt laeuft das ECHTE `send_chunked`; die Attrappe sitzt eine Ebene
    tiefer, am Telegram-Rand. Wer die Signatur der geprueften Funktion selbst
    neu definiert, prueft nichts.
    """
    b = _AttrappenBot()
    asyncio.run(bot._limit_warnung_melden(_sitzung(b), 1, None, _Ereignis(info)))
    return b.texte


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



# ---------- B7: Sparmodus — gebaut und ruhend --------------------------------
def _sparmodus_ist_standardmaessig_AUS():
    """**Der wichtigste Teil dieser Stufe.**

    Ein Bot, der von sich aus die Arbeitstiefe senkt, ändert sein Verhalten in
    dem Moment, in dem Adam am wenigsten damit rechnet — mitten in einer
    Antwort, ohne dass er den Anlass sieht. Von außen sähe das aus wie ein
    schlechter gewordener Assistent. Die Verrohrung darf da sein; scharf
    stellt sie Adam.
    """
    assert bot.SPARMODUS_STANDARD is False, "der Sparmodus ist scharfgestellt"
    bot._USER_PREFS.pop("9001", None)
    assert not bot._sparmodus_an(9001), "er greift ohne Zutun"
    assert bot._sparmodus_greifen(9001) is None, "er senkt die Tiefe ungefragt"


def _eingeschaltet_senkt_er_die_tiefe_genau_einmal():
    uid = 9002
    bot._USER_PREFS[str(uid)] = {"sparmodus": True, "effort": None}
    assert bot._sparmodus_greifen(uid) == "low", "eingeschaltet greift er nicht"
    assert bot._USER_PREFS[str(uid)]["effort"] == "low"
    # Wer ohnehin sparsam arbeitet, braucht keine Meldung darüber.
    assert bot._sparmodus_greifen(uid) is None, \
        "er meldet die Umstellung erneut, obwohl schon umgestellt ist"


def _die_umstellung_wird_immer_genannt():
    """Eine Tiefe, die sich unbemerkt senkt, ist schlimmer als eine, die
    bleibt — man sucht den Fehler dann bei der Qualität."""
    quelle = Path(bot.__file__).read_text(encoding="utf-8")
    block = quelle.split("async def _limit_warnung_melden")[1].split("\ndef ")[0]
    assert "_sparmodus_greifen" in block and "Sparmodus greift" in block, \
        "der Sparmodus wirkt, ohne dass die Meldung es sagt"


check("Sparmodus ist standardmäßig AUS (gebaut und ruhend)",
      _sparmodus_ist_standardmaessig_AUS)
check("eingeschaltet senkt er die Tiefe genau einmal",
      _eingeschaltet_senkt_er_die_tiefe_genau_einmal)
check("die Umstellung wird immer genannt, nie stillschweigend",
      _die_umstellung_wird_immer_genannt)

if fails:
    print(f"\n❌ {len(fails)} B4/B7-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("\nAlle B4/B7-Tests bestanden.")
