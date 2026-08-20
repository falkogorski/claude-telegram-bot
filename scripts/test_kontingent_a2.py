#!/usr/bin/env python3
# <!-- ROLLE: test-kontingent-a2 -->
"""A2 — der Kontingent-Stand auf Abruf. **Ausgeführt, nicht gelesen.**

**Der Fehler, gegen den dieser Prüfer wacht, ist eine Reihenfolge.** Der
Kontingentwert lief seit F-5 durch `_limit_warnung_melden` — aber das Merken
geschah unter der Statusprüfung, und die lässt nur `allowed_warning` und
`rejected` durch. Damit war jeder **grüne** Stand weg, obwohl er da war. Wer
den Merk-Aufruf irgendwann hinter den Filter zurückschiebt, weil es dort
„logischer" aussieht, stellt genau diesen Zustand wieder her — ohne dass eine
Zeile fehlt und ohne dass etwas abstürzt.

Deshalb prüft der Kern hier nicht, **ob** der Aufruf dasteht, sondern **was
nach einem grünen Ereignis im Merker liegt.** Ein Text-Prüfer wäre bei jeder
denkbaren Reihenfolge grün geblieben.

Die zweite Klasse von Fehlern, gegen die geprüft wird: **eine Zahl ohne
Alter.** Der Wert stammt aus der letzten Antwort, die vorbeikam — er kann
Stunden alt sein. Eine Anzeige, die das verschweigt, wäre die stille
Falsch-Wahrheit in Reinform.
"""
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="a2-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["LIMIT_STAND_FILE"] = str(_TMP / "limit-stand.json")
os.environ["LIMIT_MARKE_FILE"] = str(_TMP / "limit-gemeldet.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []


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


class Info:
    """Das, was das SDK als ``RateLimitInfo`` liefert — die Felder, die zählen."""

    def __init__(self, status="allowed", art="five_hour", anteil=0.42,
                 resets_at=None):
        self.status = status
        self.rate_limit_type = art
        self.utilization = anteil
        self.resets_at = resets_at if resets_at is not None else time.time() + 3600


class Ereignis:
    def __init__(self, info):
        self.rate_limit_info = info


class Sess:
    def __init__(self):
        self.user_id = 4711
        self.bot = None


def _frisch():
    bot._LIMIT_LETZTER.clear()
    bot._LIMIT_GEMELDET.clear()


def _gruener_stand_wird_gemerkt():
    """**Der Kern.** Ein grünes Ereignis muss im Merker landen."""
    _frisch()
    bot._limit_letzten_merken(Info(status="allowed", anteil=0.31))
    assert "five_hour" in bot._LIMIT_LETZTER, \
        "der grüne Stand wurde nicht gemerkt"
    assert abs(bot._LIMIT_LETZTER["five_hour"]["anteil"] - 0.31) < 1e-9, \
        "der gemerkte Anteil stimmt nicht"


def _die_reihenfolge_in_der_meldung_stimmt():
    """**Der eigentliche Regressionsschutz — ausgeführt, nicht gelesen.**

    ``_limit_warnung_melden`` wird mit einem grünen Ereignis gefahren. Grün
    heißt: keine Meldung an Adam (richtig so) — aber der Stand muss trotzdem
    im Merker liegen. Wandert der Merk-Aufruf unter den Statusfilter, ist der
    Merker danach leer und diese Prüfung rot.
    """
    _frisch()
    asyncio.run(bot._limit_warnung_melden(
        Sess(), 4711, None, Ereignis(Info(status="allowed", anteil=0.55))))
    assert "five_hour" in bot._LIMIT_LETZTER, \
        ("ein grünes Ereignis hinterlässt keinen Stand — das Merken liegt "
         "wieder unter dem Statusfilter")


def _wertloser_eintrag_ueberschreibt_keinen_guten():
    """Ohne Zahl ist ein Eintrag wertlos; wertlos darf gut nicht verdrängen."""
    _frisch()
    bot._limit_letzten_merken(Info(anteil=0.77))
    bot._limit_letzten_merken(Info(anteil=None))
    assert abs(bot._LIMIT_LETZTER["five_hour"]["anteil"] - 0.77) < 1e-9, \
        "ein Ereignis ohne Zahl hat den guten Stand überschrieben"


def _mehrere_fenster_nebeneinander():
    """Fünf-Stunden- und Wochenfenster dürfen sich nicht gegenseitig löschen."""
    _frisch()
    bot._limit_letzten_merken(Info(art="five_hour", anteil=0.2))
    bot._limit_letzten_merken(Info(art="seven_day", anteil=0.9))
    assert len(bot._LIMIT_LETZTER) == 2, \
        f"erwartet zwei Fenster, gemerkt sind {len(bot._LIMIT_LETZTER)}"


def _stand_ueberlebt_neustart():
    """Der Merker liegt auf Platte — sonst ist er nach jedem Neustart leer."""
    _frisch()
    bot._limit_letzten_merken(Info(anteil=0.64))
    bot._LIMIT_LETZTER.clear()
    bot._limit_letzten_laden()
    assert "five_hour" in bot._LIMIT_LETZTER, \
        "der Stand hat den Neustart nicht überlebt"


def _alter_wird_in_marken_genannt():
    """Keine Sekundenzahlen — die Zeitform-Regel gilt auch hier."""
    proben = {
        0: "gerade eben",
        60 * 15: "vor etwa einer Viertelstunde",
        60 * 30: "vor einer halben Stunde",
        60 * 57: "vor einer knappen Stunde",
    }
    for alter, erwartet in proben.items():
        ist = bot._vor_wie_lange(time.time() - alter)
        assert ist == erwartet, f"{alter}s ergab [{ist}], erwartet [{erwartet}]"
    assert bot._vor_wie_lange(None) == "unbekannt", \
        "ohne Zeitstempel muss das Alter ausdrücklich unbekannt heißen"
    for alter in (0, 300, 4000, 90000):
        assert "Sekunde" not in bot._vor_wie_lange(time.time() - alter), \
            "das Alter nennt Sekunden"


def _die_anzeige_nennt_das_alter():
    """**Eine Zahl ohne Alter wäre die Falsch-Wahrheit.**

    Der Abruf wird ausgeführt; geprüft wird der Text, der bei Adam ankäme.
    """
    _frisch()
    bot._limit_letzten_merken(Info(anteil=0.42))
    gesendet = []

    class Msg:
        async def reply_text(self, text, *a, **k):
            gesendet.append(text)

    class Upd:
        message = Msg()
        effective_user = type("U", (), {"id": 4711})()
        effective_chat = type("C", (), {"id": 4711, "type": "private"})()

    echt = bot.authorized
    bot.authorized = lambda *a, **k: True
    try:
        asyncio.run(bot.cmd_kontingent(Upd(), None))
    finally:
        bot.authorized = echt

    assert gesendet, "der Abruf hat nichts gesendet"
    text = gesendet[0]
    assert "42 %" in text, f"der Prozentwert fehlt: {text[:120]}"
    assert "gesehen" in text, \
        "die Anzeige nennt das Alter des Werts nicht — sie wirkt frischer als sie ist"


def _ohne_stand_wird_nichts_erfunden():
    """Kein Wert heißt: das sagen, nicht schätzen."""
    _frisch()
    gesendet = []

    class Msg:
        async def reply_text(self, text, *a, **k):
            gesendet.append(text)

    class Upd:
        message = Msg()
        effective_user = type("U", (), {"id": 4711})()
        effective_chat = type("C", (), {"id": 4711, "type": "private"})()

    echt = bot.authorized
    bot.authorized = lambda *a, **k: True
    try:
        asyncio.run(bot.cmd_kontingent(Upd(), None))
    finally:
        bot.authorized = echt

    assert gesendet, "der Abruf hat nichts gesendet"
    assert "%" not in gesendet[0], \
        "ohne bekannten Stand wird eine Prozentzahl ausgegeben"


def _der_abruf_steht_im_menue():
    """Doku-Spiegel: ein Befehl, den das Menü nicht kennt, findet niemand."""
    namen = [b[0] for b in bot._BEFEHLE]
    assert "kontingent" in namen, "der Befehl fehlt in der Befehlstabelle"
    eintrag = [b for b in bot._BEFEHLE if b[0] == "kontingent"][0]
    assert eintrag[1], "der Befehl ist aus dem Telegram-Menü ausgeblendet"


check("der grüne Stand wird gemerkt", _gruener_stand_wird_gemerkt)
check("gemerkt wird VOR der Bewertung", _die_reihenfolge_in_der_meldung_stimmt)
check("wertlos verdrängt gut nicht", _wertloser_eintrag_ueberschreibt_keinen_guten)
check("mehrere Fenster nebeneinander", _mehrere_fenster_nebeneinander)
check("der Stand überlebt den Neustart", _stand_ueberlebt_neustart)
check("das Alter kommt in Marken", _alter_wird_in_marken_genannt)
check("die Anzeige nennt das Alter", _die_anzeige_nennt_das_alter)
check("ohne Stand wird nichts erfunden", _ohne_stand_wird_nichts_erfunden)
check("der Abruf steht im Menü", _der_abruf_steht_im_menue)

print()
if fails:
    print(f"❌ {len(fails)} A2-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle A2-Kontingent-Tests bestanden.")
