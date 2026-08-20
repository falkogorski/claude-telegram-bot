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


def _eintrag_ohne_zahl_wird_trotzdem_angenommen():
    """**Diese Pruefung stand vorher auf dem Kopf — die Messung hat sie gedreht.**

    Sie verlangte frueher, dass ein Ereignis **ohne** ``utilization`` verworfen
    wird — unter der Annahme, ohne Zahl sei der Eintrag wertlos. Am 20.08. in
    der echten Bot-Umgebung gemessen: Der Anbieter schickt die Zahl gar nicht
    mit, solange der Zustand ``allowed`` ist. Es kam
    ``{status: allowed, resetsAt: …, rateLimitType: five_hour}``.

    Die alte Annahme haette also **jeden gruenen Stand** verworfen — und genau
    das tat sie: Adams Abruf meldete "frisch gemessen" ueber einer leeren
    Anzeige. **Wertlos ist nur, was keinen Fensternamen traegt.**
    """
    _frisch()
    bot._limit_letzten_merken(Info(anteil=None, resets_at=time.time() + 1800))
    assert "five_hour" in bot._LIMIT_LETZTER, \
        "ein gruener Stand ohne Prozentzahl wurde verworfen"
    assert bot._LIMIT_LETZTER["five_hour"]["anteil"] is None, \
        "eine Zahl wurde erfunden, wo der Anbieter keine schickte"
    assert bot._LIMIT_LETZTER["five_hour"]["resets_at"], \
        "der Ruecksetzzeitpunkt ging verloren — er ist die halbe Auskunft"


def _ohne_fenstername_wird_verworfen():
    """Die Gegenrichtung: ganz ohne Fenstername ist der Eintrag wirklich leer."""
    _frisch()
    assert bot._limit_letzten_merken(Info(art=None, anteil=0.5)) is False, \
        "ein Eintrag ohne Fensternamen wurde angenommen"
    assert not bot._LIMIT_LETZTER, "der leere Eintrag liegt im Merker"


def _die_anzeige_nennt_den_zustand_wenn_die_zahl_fehlt():
    """**Kein Schweigen, nur weil eine Zahl fehlt.**

    Die Anzeige muss sagen, was da ist — Zustand und Ruecksetzzeitpunkt —
    und darf keine Prozentzahl erfinden.
    """
    _frisch()
    bot._limit_letzten_merken(Info(status="allowed", anteil=None,
                                   resets_at=time.time() + 1800))
    text = bot._kontingent_text()
    assert "gr\u00fcnen Bereich" in text, \
        f"der Zustand wird nicht genannt: {text}"
    assert "%" not in text, f"eine Prozentzahl wurde erfunden: {text}"
    assert "Zur\u00fcckgesetzt" in text, "der Ruecksetzzeitpunkt fehlt"


def _das_erfolgsflag_haengt_am_ergebnis():
    """**Adams Testbefund vom 20.08., 20:23.**

    Der Abruf meldete "frisch gemessen" ueber einer leeren Anzeige, weil das
    Erfolgsflag am **Ereignis** hing statt am **Ergebnis**. Ein Merken, das
    nichts annimmt, darf keinen Erfolg melden.
    """
    _frisch()
    assert bot._limit_letzten_merken(Info(art=None, anteil=None)) is False, \
        "ein verworfenes Ereignis meldet Erfolg"
    assert bot._limit_letzten_merken(Info(anteil=0.3)) is True, \
        "ein angenommenes Ereignis meldet keinen Erfolg"


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
    """**Durch A2.2 umgebaut — und der Umbau ist der Punkt.**

    Frueher galt: kein Stand, keine Zahl. Seit A2.2 wird bei leerem Merker
    frisch gemessen — die Regel wandert also mit auf den Fall, dass die
    Messung **nichts liefert**. Der Anbieter schickt die Kopfzeilen laut
    eigener Angabe nur optional; dann darf trotzdem keine Zahl erscheinen,
    und der bereits gelaufene Verbrauch muss genannt werden.
    """
    _frisch()
    gesendet = []
    echt_messen = bot._kontingent_frisch_messen
    echt_auth = bot.authorized

    async def _messung_ohne_ergebnis():
        return False

    class Msg:
        async def reply_text(self, text, *a, **k):
            gesendet.append(text)
            return self

        async def edit_text(self, text, *a, **k):
            gesendet.append(text)
            return self

    class Upd:
        message = Msg()
        effective_user = type("U", (), {"id": 4711})()
        effective_chat = type("C", (), {"id": 4711, "type": "private"})()

    bot._kontingent_frisch_messen = _messung_ohne_ergebnis
    bot.authorized = lambda *a, **k: True
    try:
        asyncio.run(bot.cmd_kontingent(Upd(), None))
    finally:
        bot._kontingent_frisch_messen = echt_messen
        bot.authorized = echt_auth

    assert gesendet, "der Abruf hat nichts gesendet"
    letzte = gesendet[-1]
    assert "%" not in letzte, \
        f"ohne Ergebnis wird eine Prozentzahl ausgegeben: {letzte[:120]}"
    assert "gekostet" in letzte, \
        "der bereits gelaufene Verbrauch wird verschwiegen"


def _der_abruf_steht_im_menue():
    """Doku-Spiegel: ein Befehl, den das Menü nicht kennt, findet niemand."""
    namen = [b[0] for b in bot._BEFEHLE]
    assert "kontingent" in namen, "der Befehl fehlt in der Befehlstabelle"
    eintrag = [b for b in bot._BEFEHLE if b[0] == "kontingent"][0]
    assert eintrag[1], "der Befehl ist aus dem Telegram-Menü ausgeblendet"


check("der grüne Stand wird gemerkt", _gruener_stand_wird_gemerkt)
check("gemerkt wird VOR der Bewertung", _die_reihenfolge_in_der_meldung_stimmt)
check("Eintrag ohne Zahl wird angenommen", _eintrag_ohne_zahl_wird_trotzdem_angenommen)
check("ohne Fenstername wird verworfen", _ohne_fenstername_wird_verworfen)
check("Anzeige nennt den Zustand ohne Zahl", _die_anzeige_nennt_den_zustand_wenn_die_zahl_fehlt)
check("das Erfolgsflag haengt am Ergebnis", _das_erfolgsflag_haengt_am_ergebnis)
check("mehrere Fenster nebeneinander", _mehrere_fenster_nebeneinander)
check("der Stand überlebt den Neustart", _stand_ueberlebt_neustart)
check("das Alter kommt in Marken", _alter_wird_in_marken_genannt)
check("die Anzeige nennt das Alter", _die_anzeige_nennt_das_alter)
check("ohne Stand wird nichts erfunden", _ohne_stand_wird_nichts_erfunden)
check("der Abruf steht im Menü", _der_abruf_steht_im_menue)


# ---------------------------------------------------------------------------
# A2.2 — die Frischmessung auf Wunsch (Adam 20.08., Engywucks drei Auflagen)
#
# Die Erweiterung bricht bewusst die Invariante „der Abruf verbraucht
# nichts“. Zulaessig ist das, weil der Lauf mensch-initiiert ist: ein Tipp,
# ein Lauf. **Genau deshalb muss geprueft werden, dass die Ausnahme eng
# bleibt** — eine Ausnahme ohne Pruefer ist eine Absichtserklaerung.


def _bei_altem_stand_wird_NICHT_gemessen():
    """**Engywucks zweite Auflage, ausgefuehrt.**

    Ein alter Stand darf sich nicht von selbst nachmessen — sonst kostet
    jeder Blick auf den Stand Kontingent. Geprueft wird, indem die Messung
    durch eine Attrappe ersetzt wird, die mitzaehlt: Bei vorhandenem Stand
    darf sie **nie** gerufen werden.
    """
    _frisch()
    bot._limit_letzten_merken(Info(anteil=0.5))
    # kuenstlich alt machen — aelter als jede Wiedervorlage
    bot._LIMIT_LETZTER["five_hour"]["gesehen"] = time.time() - 86400
    gerufen = []
    echt_messen = bot._kontingent_frisch_messen
    echt_auth = bot.authorized

    async def _attrappe():
        gerufen.append(1)
        return True

    gesendet = []

    class Msg:
        async def reply_text(self, text, *a, **k):
            gesendet.append(text)
            return self

        async def edit_text(self, text, *a, **k):
            gesendet.append(text)
            return self

    class Upd:
        message = Msg()
        effective_user = type("U", (), {"id": 4711})()
        effective_chat = type("C", (), {"id": 4711, "type": "private"})()

    bot._kontingent_frisch_messen = _attrappe
    bot.authorized = lambda *a, **k: True
    try:
        asyncio.run(bot.cmd_kontingent(Upd(), None))
    finally:
        bot._kontingent_frisch_messen = echt_messen
        bot.authorized = echt_auth

    assert not gerufen, \
        "ein ALTER Stand hat eine Frischmessung ausgeloest — jeder Blick kostet dann"
    assert gesendet and "50 %" in gesendet[0], \
        f"der alte Stand wurde nicht angezeigt: {gesendet[:1]}"


def _bei_leerem_stand_wird_gemessen():
    """Die Gegenrichtung — sonst prueft die Zeile oben nur Untaetigkeit."""
    _frisch()
    gerufen = []
    echt_messen = bot._kontingent_frisch_messen
    echt_auth = bot.authorized

    async def _attrappe():
        gerufen.append(1)
        bot._limit_letzten_merken(Info(anteil=0.11))
        return True

    class Msg:
        async def reply_text(self, text, *a, **k):
            return self

        async def edit_text(self, text, *a, **k):
            return self

    class Upd:
        message = Msg()
        effective_user = type("U", (), {"id": 4711})()
        effective_chat = type("C", (), {"id": 4711, "type": "private"})()

    bot._kontingent_frisch_messen = _attrappe
    bot.authorized = lambda *a, **k: True
    try:
        asyncio.run(bot.cmd_kontingent(Upd(), None))
    finally:
        bot._kontingent_frisch_messen = echt_messen
        bot.authorized = echt_auth

    assert gerufen, "bei leerem Stand wurde nicht gemessen — der Befehl bliebe nutzlos"


def _die_beschreibung_wandert_mit():
    """**Engywucks erste Auflage.**

    Nach einer Frischmessung darf der Text NICHT behaupten, der Abruf
    verbrauche nichts — das waere die umgekehrte Falsch-Wahrheit: Der Bau
    tut mehr, als die Beschreibung sagt.
    """
    _frisch()
    bot._limit_letzten_merken(Info(anteil=0.4))
    frisch = bot._kontingent_text(frisch=True)
    assert "verbraucht selbst nichts" not in frisch, \
        "nach einer Frischmessung steht da noch, der Abruf verbrauche nichts"
    assert "Kontingent gekostet" in frisch, \
        f"der Verbrauch wird nicht genannt: {frisch[-120:]}"
    ruhig = bot._kontingent_text(frisch=False)
    assert "verbraucht selbst nichts" in ruhig, \
        "ohne Messung fehlt der Hinweis, dass der Abruf nichts kostet"


def _kein_anderer_pfad_ruft_die_messung():
    """**Engywucks dritte Auflage.** Keine Automatik, kein Zeitgeber.

    Text-Pruefung mit Ansage: Gezaehlt werden die Aufrufstellen im Quelltext.
    Erlaubt sind genau zwei — der Befehl und die Schaltflaeche, beide von
    Adams Tipp ausgeloest. Kommt eine dritte dazu, ist zu begruenden, wer sie
    ausloest; ein Zeitgeber waere ein AGB-Bruch.
    """
    quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
    # **Der Beobachter im Bild — beim ersten Lauf sofort aufgetreten.**
    # Die Definitionszeile `async def _kontingent_frisch_messen()` enthaelt den
    # gesuchten Text und zaehlte sich selbst als dritter Aufruf. Dasselbe
    # Muster wie die Prozess-Zaehlung, die sich mitzaehlte: Wer misst, muss
    # sich aus der Messung herausrechnen.
    zeilen = [z for z in quelle.splitlines()
              if "_kontingent_frisch_messen()" in z
              and not z.lstrip().startswith(("async def", "def"))]
    aufrufe = len(zeilen)
    assert aufrufe == 2, (
        f"{aufrufe} Aufrufstellen der Frischmessung statt zwei — erlaubt sind "
        "nur Befehl und Schaltflaeche, beide mensch-initiiert")


check("bei ALTEM Stand wird NICHT gemessen", _bei_altem_stand_wird_NICHT_gemessen)
check("bei leerem Stand wird gemessen", _bei_leerem_stand_wird_gemessen)
check("die Beschreibung wandert mit", _die_beschreibung_wandert_mit)
check("kein anderer Pfad ruft die Messung", _kein_anderer_pfad_ruft_die_messung)

print()
if fails:
    print(f"❌ {len(fails)} A2-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle A2-Kontingent-Tests bestanden.")
