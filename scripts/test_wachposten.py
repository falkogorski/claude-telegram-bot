#!/usr/bin/env python3
# <!-- ROLLE: test-log-wachposten -->
"""Verhaltenstest des Log-Wachpostens — **ausführend, nicht lesend.**

Die Prüfkette läuft echt; eine Attrappe sitzt nur am **Postfach-Rand**, also
dort, wo etwas zu Adam hinausginge. Wer die geprüfte Funktion selbst durch eine
Attrappe ersetzt, prüft nichts — das hat der 18.08. dreifach gezeigt.
"""
import importlib
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_TMP = Path(tempfile.mkdtemp(prefix="wp-"))
os.environ["WACHPOSTEN_LOGDIR"] = str(_TMP / "logs")
os.environ["WACHPOSTEN_DIR"] = str(_TMP / "zustand")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
# Fuer die A5-Grenzpruefungen wird `bot` geladen — es braucht diese beiden.
os.environ["TELEGRAM_BOT_TOKEN"] = ("1:test")
os.environ["ALLOWED_USER_IDS"] = ("1")
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
(_TMP / "logs" / "conversations").mkdir(parents=True)
(_TMP / "postfach" / "outbox").mkdir(parents=True)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import wachmuster  # noqa: E402
import wachposten  # noqa: E402

_ECHT_LEGEN = None

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


_GESENDET: list[str] = []
_KNOEPFE: list[dict | None] = []
_postfach_ersetzt = False


def _postfach_stellen():
    """Der RAND — hier würde etwas zu Adam hinausgehen.

    **Die Attrappe spiegelt die ECHTE Signatur, kein `**kwargs`.** Am 18.08.
    baute ein Prüfer seine Attrappe mit genau der falschen Arität, die der
    Fehler hatte — damit war der Fehler per Konstruktion unsichtbar. Ein
    nachsichtiges `**kwargs` hätte hier dieselbe Wirkung: Ein Tippfehler im
    Aufrufnamen bliebe grün.
    """
    import botenpost
    echt = botenpost.legen

    def _fang(text, absender, ziel=None, thread_id=None, knopf=None):
        _GESENDET.append(text)
        _KNOEPFE.append(knopf)
        return Path("/dev/null")
    botenpost.legen = _fang
    wachposten.botenpost = botenpost
    return echt


def _archiv() -> str:
    """Die ausfuehrliche Fassung — seit A4 (20.08.) NICHT mehr das, was Adam
    bekommt. Der Wortlaut gehoert hierher, die Kurzfassung in seinen Chat."""
    p = _TMP / "logs" / "wachposten-archiv.log"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _fehlerdatei(*zeilen):
    p = _TMP / "logs" / "bot-errors.log"
    p.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return p


def _frisch():
    """Jede Prüfung startet ohne Gedächtnis — sonst dämpft die vorige."""
    _GESENDET.clear()
    for f in (_TMP / "zustand").glob("*"):
        f.unlink()
    (_TMP / "logs" / "bot-errors.log").unlink(missing_ok=True)
    (_TMP / "logs" / "wachposten-archiv.log").unlink(missing_ok=True)


# ---------------------------------------------------------------------------
def _rote_zeile_wird_gemeldet_mit_wortlaut():
    """Der Grundfall: Eine auffällige, aber nicht ampelrote Zeile geht mit
    ihrem Wortlaut hinaus. **Die Fundstelle allein ist keine Auskunft** — das
    war die Lehre aus Horas Halt am 28.07."""
    _frisch()
    _fehlerdatei("Traceback (most recent call last):")
    n = wachposten.lauf()
    assert n >= 1, "die Fehlerzeile wurde nicht gefunden"
    assert _GESENDET, "es ging nichts hinaus"
    # A4: Der Wortlaut steht in der AUSFUEHRLICHEN Fassung im Archiv — Adams
    # Chat bekommt einen deutschen Satz. Beides wird geprueft.
    assert "Traceback" in _archiv(), \
        f"der Wortlaut fehlt im Archiv: {_archiv()[:200]}"
    assert "Traceback" not in _GESENDET[0], \
        f"der englische Fehlertext steht in Adams Meldung: {_GESENDET[0][:200]}"
    # Die Schlusszeile nennt jetzt den Stand statt zu fragen (Adams Regel vom
    # 20.08.); geprüft wird, DASS sie steht — der Wortlaut in
    # `_keine_frage_ohne_wirkung`.
    assert "Engywuck" in _GESENDET[0], \
        "Adam erfaehrt nicht, wo der Befund liegt"


def _harmlose_zeilen_schweigen():
    """**Die Gegenprobe.** Ohne sie wüsste der Prüfer nur, dass der Posten
    meldet — nicht, dass er auch schweigen kann."""
    _frisch()
    (_TMP / "logs" / "conversations" / f"{time.strftime('%Y-%m-%d')}.md").write_text(
        "Ein ganz normaler Satz.\nUnd noch einer.\n", encoding="utf-8")
    assert wachposten.lauf() == 0, "harmlose Zeilen erzeugen eine Meldung"
    assert not _GESENDET, "es ging etwas hinaus, obwohl nichts auffällig war"


def _gespraeche_bleiben_ohne_schalter_ungelesen():
    """**Adams Entscheidung, nicht meine.** Die Gesprächsprotokolle sind das,
    was er privat schreibt — der Schalter steht auf aus, bis er ihn umlegt."""
    _frisch()
    tag = _TMP / "logs" / "conversations" / f"{time.strftime('%Y-%m-%d')}.md"
    tag.write_text("Hier steht ein Traceback und ein Passwort.\n", encoding="utf-8")
    assert not wachposten.GESPRAECHE_LESEN, "der Schalter steht auf AN"
    quellen = [q.name for q in wachposten._quellen()]
    assert tag.name not in quellen, \
        f"das Gesprächsprotokoll wird ohne Schalter gelesen: {quellen}"


def _daempfer_meldet_nicht_zwoelfmal_je_stunde():
    """Der Posten läuft alle fünf Minuten. Ohne Dämpfer meldete ein stehender
    Fehler zwölfmal je Stunde — und wer diesen Absender überliest, überliest
    auch den einen, der zählt."""
    _frisch()
    _fehlerdatei("Traceback (most recent call last):")
    assert wachposten.lauf() >= 1, "erste Meldung fehlt"
    # Dieselbe Zeile erneut anhängen: neuer Offset, gleiche Kennung.
    with (_TMP / "logs" / "bot-errors.log").open("a", encoding="utf-8") as fh:
        fh.write("Traceback (most recent call last):\n")
    vorher = len(_GESENDET)
    wachposten.lauf()
    assert len(_GESENDET) == vorher, \
        "dieselbe Kennung wurde innerhalb der Sperrfrist erneut gemeldet"


def _offset_verhindert_doppelmeldung():
    """Ohne gemerkten Stand läse der Posten alle fünf Minuten die ganze Datei
    von vorn — und meldete jeden alten Fehler wieder."""
    _frisch()
    _fehlerdatei("Traceback (most recent call last):")
    wachposten.lauf()
    stand = wachposten._stand_laden()
    assert stand.get("bot-errors.log", 0) > 0, "der Lesestand wird nicht gemerkt"


def _beschaedigter_stand_wird_gemeldet_nicht_verschwiegen():
    """**Lehre des Versions-Monitors (18.08.):** Dort legte ein kaputter
    Zeitstempel einen Eintrag DAUERHAFT still, während das Protokoll „vor 0
    Tagen gesehen" meldete. Stillstehen ist die schlechteste Antwort."""
    _frisch()
    (_TMP / "zustand").mkdir(parents=True, exist_ok=True)
    (_TMP / "zustand" / "stand.json").write_text("{kaputt", encoding="utf-8")
    _fehlerdatei("irgendwas Harmloses")
    wachposten.lauf()
    assert _GESENDET, "es ging gar nichts hinaus"
    assert "Merkzettel" in _archiv(), \
        f"der beschädigte Stand wird verschwiegen: {_archiv()[:300]}"


def _bei_ampel_rot_kein_wortlaut():
    """**Engywucks Auflage.** Bei Rot gehen nur Quelle, Zeit und das
    Kategorien-Label hinaus — nie das gefundene Muster. `classify()` liefert
    `matches` mit den Treffern; die dürfen die Meldung nie berühren."""
    _frisch()
    geheim = "Klientenakte Musterfrau"
    zeile = wachposten._melde_zeile(
        "Testbefund", geheim, "quelle.log",
        lambda t: {"color": "rot", "rules": ["klienten"], "matches": [geheim]})
    assert geheim not in zeile, f"der Wortlaut steht in der Meldung: {zeile}"
    assert "klienten" in zeile, "das Kategorien-Label fehlt"
    assert "zurückgehalten" in zeile, "die Zurückhaltung wird nicht benannt"


def _ampel_ausfall_zaehlt_als_rot():
    """Wer im Zweifel öffnet, sichert nichts — dieselbe Bauart wie der Riegel."""
    _frisch()
    def _kaputt(_):
        raise RuntimeError("Ampel weg")
    zeile = wachposten._melde_zeile("Testbefund", "geheimer Text", "q.log", _kaputt)
    assert "geheimer Text" not in zeile, \
        "bei ausgefallener Ampel wird der Wortlaut trotzdem gezeigt"
    zeile2 = wachposten._melde_zeile("Testbefund", "geheimer Text", "q.log", None)
    assert "geheimer Text" not in zeile2, "ohne Ampel wird der Wortlaut gezeigt"


def _zurueckhaltung_gilt_fuer_BEIDE_quellen():
    """**Geschwister-Regel.** Ein Fix an einem Pfad ist erst fertig, wenn die
    Schwesterpfade geprüft sind — die Zurückhaltung hängt an der Meldezeile,
    nicht an der Quelle, also gilt sie für Fehlerdatei UND Gespräch."""
    quelle = (ROOT / "scripts" / "wachposten.py").read_text(encoding="utf-8")
    code = "\n".join(z for z in quelle.splitlines()
                     if not z.lstrip().startswith("#"))
    assert code.count("_melde_zeile") >= 2, \
        "es gibt mehr als einen Weg an der Zurückhaltung vorbei"


def _kein_modell_im_pfad():
    """AGB-Leitplanke: Der Posten ist deterministisch. Kein Anthropic-Aufruf,
    Kosten null — das war die Bedingung, unter der er überhaupt gebaut wurde."""
    quelle = (ROOT / "scripts" / "wachposten.py").read_text(encoding="utf-8")
    for verboten in ("ClaudeSDKClient", "anthropic", "claude -p", "litellm"):
        assert verboten not in quelle, \
            f"der Wachposten enthält `{verboten}` — er soll zeigen, nicht urteilen"


def _quelle_bestimmt_die_schwelle():
    """**Gemessen am 19.08. an echten Daten:** Eine reale Zeile aus
    `bot-errors.log` (`TimedOut: Timed out`) traf kein einziges Muster. In
    einer FEHLERdatei ist jede neue Zeile bereits der Befund — dort nach
    Fehlermerkmalen zu suchen hiesse zu pruefen, ob ein Fehler einer ist."""
    echt = "2026-08-16 | postfach send | TimedOut: Timed out"
    assert wachmuster.treffer(echt, "bot-errors.log"), \
        "eine echte Fehlerzeile faellt durch"
    assert not wachmuster.treffer(echt, "2026-08-19.md"), \
        "dieselbe Zeile im Gespraech schlaegt an — dort braucht es Muster"


_ECHTES_LEGEN = _postfach_stellen()   # der Rand wird EINMAL gestellt, vor allen Pruefungen
# Die echte Funktion bleibt greifbar: Eine Pruefung misst ihre Abweisungen,
# und die kann nur die echte leisten (die Attrappe wuerde alles durchlassen).

check("auffällige Zeile wird MIT Wortlaut gemeldet", _rote_zeile_wird_gemeldet_mit_wortlaut)
check("harmlose Zeilen schweigen (Gegenprobe)", _harmlose_zeilen_schweigen)
check("Gespräche bleiben ohne Schalter ungelesen",
      _gespraeche_bleiben_ohne_schalter_ungelesen)
check("Dämpfer: nicht zwölfmal je Stunde", _daempfer_meldet_nicht_zwoelfmal_je_stunde)
check("Lesestand verhindert Doppelmeldung", _offset_verhindert_doppelmeldung)
check("beschädigter Stand wird gemeldet, nicht verschwiegen",
      _beschaedigter_stand_wird_gemeldet_nicht_verschwiegen)
check("bei Ampel-ROT kein Wortlaut, nur das Label", _bei_ampel_rot_kein_wortlaut)
check("Ampel-Ausfall zählt als ROT", _ampel_ausfall_zaehlt_als_rot)
check("die Zurückhaltung gilt für beide Quellen (Geschwister)",
      _zurueckhaltung_gilt_fuer_BEIDE_quellen)
check("kein Modell im Pfad (AGB, Kosten null)", _kein_modell_im_pfad)
check("die Quelle bestimmt die Schwelle (echte Daten)", _quelle_bestimmt_die_schwelle)

print()
if fails:
    print(f"❌ {len(fails)} Wachposten-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)


# ---------- Engywucks Widerlegungs-Befunde W1-W5 (19.08.) --------------------
def _ein_fehlersturm_sieht_nicht_aus_wie_ein_einzelfall():
    """**W1 — von Engywuck gemessen, hier nachgestellt.**

    In einer Fehlerdatei tragen ALLE Zeilen dieselbe Kennung (`fehlerdatei`).
    Der erste Entwurf daempfte allein darueber: Drei verschiedene neue Fehler
    ergaben genau EINE Meldung. Und weil die Offsets trotzdem fortgeschrieben
    wurden, verschwand fuer die naechste Stunde jeder weitere endgueltig.

    Das widersprach dem eigenen Satz [in einer Fehlerdatei ist jede neue Zeile
    bereits der Befund] - und die (und N weitere)-Zeile konnte fuer gleiche
    Kennungen nie feuern.
    """
    _frisch()
    _fehlerdatei("22:00:01 | TimedOut: Timed out",
                 "22:00:02 | ValueError: kaputt",
                 "22:00:03 | ConnectionError: weg")
    n = wachposten.lauf()
    assert n == 3, f"von drei neuen Fehlerzeilen kamen {n} durch"
    # A4: Die Wortlaute stehen in der ausfuehrlichen Fassung; Adams
    # Kurzfassung nennt nur die Zahl. Beides wird gemessen.
    text = _archiv()
    for muss in ("TimedOut", "ValueError", "ConnectionError"):
        assert muss in text, f"[{muss}] fehlt im Archiv — verschluckt"
    assert "3 neue" in _GESENDET[0], \
        f"Adams Kurzfassung nennt die Zahl nicht: {_GESENDET[0][:120]}"


def _dieselbe_zeile_wird_zwischen_laeufen_gedaempft():
    """Die Gegenrichtung: Der Daempfer soll ja weiter wirken - nur zwischen
    Laeufen, nicht innerhalb. Sonst waere W1 gegen einen Dauerfunk getauscht."""
    _frisch()
    _fehlerdatei("22:00:01 | immer derselbe Fehler")
    assert wachposten.lauf() == 1
    with (_TMP / "logs" / "bot-errors.log").open("a", encoding="utf-8") as fh:
        fh.write("22:00:01 | immer derselbe Fehler\n")
    vorher = len(_GESENDET)
    wachposten.lauf()
    assert len(_GESENDET) == vorher, \
        "dieselbe Zeile wurde innerhalb der Sperrfrist erneut gemeldet"


def _der_befund_wird_nicht_verbraucht_bevor_er_ankommt():
    """**W2.** Vorher wurde der Stand VOR der Zustellung geschrieben: Schlug
    das Legen fehl, waren Offset und Daempfer fort und die Warnung stand als
    print im Journal - die A2-Klasse, eine Zeile im Log, die niemand liest."""
    _frisch()
    import botenpost
    echt = botenpost.legen

    def _kaputt(*a, **kw):
        raise RuntimeError("Postfach weg")
    botenpost.legen = _kaputt
    try:
        _fehlerdatei("22:00:01 | ein wichtiger Fehler")
        wachposten.lauf()
        stand = wachposten._stand_laden()
        assert not stand.get("bot-errors.log"), \
            "der Lesestand wurde fortgeschrieben, obwohl die Meldung scheiterte"
    finally:
        botenpost.legen = echt
    # Der naechste Lauf MUSS die Zeile wiederfinden.
    _GESENDET.clear()
    assert wachposten.lauf() == 1, "die Zeile ging trotz Fehlschlag verloren"
    assert "ein wichtiger Fehler" in _archiv(), \
        "die wiedergefundene Zeile steht nicht im Archiv"


def _die_fundstelle_nennt_zeile_und_zeit():
    """**W3.** Bei zurueckgehaltenem Wortlaut ist die Fundstelle das Einzige,
    was Adam hat. Die Doku versprach Quelle, Zeit und Label - die Meldung
    nannte nur den Dateinamen. Eine Beschreibung, die mehr verspricht als der
    Bau: genau die Klasse, die dieser Posten aufdecken soll."""
    _frisch()
    _fehlerdatei("22:00:01 | irgendein Fehler")
    wachposten.lauf()
    # A4: Die Fundstelle gehoert in die ausfuehrliche Fassung — Adams
    # Kurzfassung nennt bewusst weder Zeilennummer noch Dateiname.
    text = _archiv()
    assert "Zeile 1" in text, f"die Zeilennummer fehlt: {text[:200]}"
    assert "gesehen" in text, f"die Zeit fehlt: {text[:200]}"


def _halbe_zeilen_werden_nicht_zerrissen():
    """**W4.** Wird eine Zeile gerade geschrieben, laese der Posten sie halb -
    und ein zerrissener Fehler trifft womoeglich kein Muster."""
    _frisch()
    p = _TMP / "logs" / "bot-errors.log"
    p.write_text("22:00:01 | vollstaendig\n22:00:02 | halb geschrie", encoding="utf-8")
    n = wachposten.lauf()
    assert n == 1, f"die halbe Zeile wurde mitgelesen ({n} Befunde)"
    # Wird sie fertiggeschrieben, kommt sie im naechsten Lauf vollstaendig.
    p.write_text("22:00:01 | vollstaendig\n22:00:02 | halb geschrieben ende\n",
                 encoding="utf-8")
    _GESENDET.clear()
    wachposten.lauf()
    assert _GESENDET, "es ging nichts hinaus"
    assert "halb geschrieben ende" in _archiv(), "die fertige Zeile kam nicht nach"


def _ampel_ausfall_wird_benannt():
    """**W5.** Der Ausfall zaehlt als Rot - richtig. Aber ohne Benennung saehe
    Adam lauter rote Meldungen ohne Grund und hielte den Inhalt fuer heikel,
    wo in Wahrheit nur die Ampel fehlt."""
    zeile = wachposten._melde_zeile("Testbefund", "harmloser Text", "q.log", None)
    assert "Ampel nicht ladbar" in zeile, \
        f"der Ampel-Ausfall wird nicht benannt: {zeile}"

    def _kaputt(_):
        raise RuntimeError("weg")
    zeile2 = wachposten._melde_zeile("Testbefund", "harmloser Text", "q.log", _kaputt)
    assert "Ampel nicht ladbar" in zeile2, \
        "eine ausgefallene Ampel wird als inhaltliches Rot dargestellt"


def _gedaempfte_werden_gezaehlt_und_genannt():
    """**Claudias Punkt 2 vom 19.08.** Der Lesestand wandert unabhängig vom
    Dämpfer ans Dateiende — was er zurückhält, ist danach **endgültig** fort.
    Diese Zeile ist die einzige Spur, die davon bleibt.

    Gemessen wird ausführend: erst eine Zeile melden (damit sie im Merkzettel
    steht), dann dieselbe Zeile plus eine neue anhängen. Die alte wird
    zurückgehalten, die neue kommt durch — und die Meldung muss beide Tatsachen
    tragen."""
    _frisch()
    _fehlerdatei("postfach send | TimedOut")
    wachposten.lauf()                       # erste Meldung, Zeile ist bekannt
    with (_TMP / "logs" / "bot-errors.log").open("a", encoding="utf-8") as fh:
        fh.write("postfach send | TimedOut\n")      # wird gedämpft
        fh.write("voice get_file | NetworkError\n")  # kommt durch
    wachposten.lauf()
    letzte = _GESENDET[-1]
    assert "NetworkError" in _archiv(), "der neue Befund fehlt ganz im Archiv"
    # Claudias Auflage: Die Zaehlzeile gehoert in BEIDE Fassungen — sie ist die
    # einzige Spur eines endgueltigen Verlusts.
    for wo, fassung in (("Adams Meldung", letzte), ("dem Archiv", _archiv())):
        assert "1 weitere, die der Dämpfer zurückhält" in fassung, \
            f"das Zurückgehaltene wird in {wo} verschwiegen"


def _ohne_daempfung_keine_zaehlzeile():
    """**Die Gegenrichtung.** Eine Zählzeile, die immer erscheint, sagt nichts
    — und ein Prüfer, der nur die eine Richtung misst, würde das nicht merken."""
    _frisch()
    _fehlerdatei("postfach send | TimedOut")
    wachposten.lauf()
    letzte = _GESENDET[-1]
    assert "Dämpfer zurückhält" not in letzte, \
        f"die Zählzeile erscheint, obwohl nichts gedämpft wurde: {letzte}"


def _keine_frage_ohne_wirkung():
    """**Adams Regel vom 20.08., 00:31.** Eine Frage nur, wenn sie im Chat
    beantwortbar ist und die Antwort wirkt. „Engywuck wecken?" erfüllte
    beides nicht: Der Postfach-Versand registriert keine offene Frage, Adams
    Daumen löste nur die stille Quittung aus — und einen technischen Weckruf
    gibt es gar nicht. **Eine Frage ohne Wirkung ist schlimmer als keine**,
    weil man sich darauf verlässt, entschieden zu haben."""
    _frisch()
    _fehlerdatei("Traceback (most recent call last):")
    wachposten.lauf()
    letzte = _GESENDET[-1]
    assert "wecken?" not in letzte, f"die wirkungslose Frage steht noch: {letzte}"
    assert not letzte.rstrip().endswith("?"), \
        f"die Meldung endet auf eine Frage: {letzte.rstrip()[-80:]}"
    assert "Engywuck" in letzte, "Adam erfaehrt nicht, wo der Befund liegt"


def _meldung_traegt_einen_knopf():
    """**Adams Entscheid vom 20.08., 00:38.** Die Meldung bietet an, statt zu
    fragen — und das Angebot hat einen Weg. Geprüft wird, dass der Knopf
    tatsächlich mitgeht und eine Kennung trägt; ohne sie wäre ein zweiter Tipp
    nicht als Dublette erkennbar."""
    _frisch()
    _KNOEPFE.clear()
    _fehlerdatei("Traceback (most recent call last):")
    wachposten.lauf()
    assert _KNOEPFE and _KNOEPFE[-1], "die Meldung geht ohne Knopf hinaus"
    k = _KNOEPFE[-1]
    assert k["art"] == "wachposten_hinterlegen", f"falsche Art: {k}"
    assert len(str(k.get("kennung", ""))) >= 8, f"Kennung zu schwach: {k}"


def _die_kennung_haengt_am_befund_nicht_an_der_zeit():
    """**Die 28.07.-Lehre, hier zum zweiten Mal angewandt.** Damals hebelte ein
    Zeitstempel im Text den Dämpfer aus, weil jede Meldung neu aussah. Trüge
    die Kennung die Zeit, wäre derselbe Befund nach einem Neustart eine andere
    Sache — und der Dublettenschutz liefe leer."""
    _frisch()
    _KNOEPFE.clear()
    _fehlerdatei("Traceback (most recent call last):")
    wachposten.lauf()
    erste = _KNOEPFE[-1]["kennung"]
    _frisch()                                # neuer Lauf, gleicher Befund
    _fehlerdatei("Traceback (most recent call last):")
    wachposten.lauf()
    assert _KNOEPFE[-1]["kennung"] == erste, \
        "derselbe Befund bekommt zwei verschiedene Kennungen"
    # Gegenrichtung: ein ANDERER Befund muss eine andere Kennung tragen.
    _frisch()
    _fehlerdatei("ValueError: etwas ganz anderes")
    wachposten.lauf()
    assert _KNOEPFE[-1]["kennung"] != erste, \
        "zwei verschiedene Befunde teilen sich eine Kennung"


def _botenpost_weist_erfundene_knopfarten_ab():
    """**Die geschlossene Liste, gemessen statt geglaubt.** Der Postfach-Ordner
    wird von mehreren Skripten beschrieben. Ohne diese Prüfung könnte jedes
    davon eine beliebige Schaltfläche in Adams Chat setzen."""
    import botenpost
    echt = botenpost.legen
    botenpost.legen = _ECHTES_LEGEN            # die Attrappe kurz beiseite
    try:
        for schlecht in ({"art": "alles_loeschen", "kennung": "abc12345"},
                         {"art": "wachposten_hinterlegen"}):   # ohne Kennung
            try:
                botenpost.legen("Probe", absender="probe", ziel="1",
                                knopf=schlecht)
                raise AssertionError(f"durchgelassen: {schlecht}")
            except botenpost.Abgewiesen:
                pass
    finally:
        botenpost.legen = echt


def _ohne_angeforderten_knopf_gibt_es_keinen():
    """**Claudias Leitplanke vom 24.07., als Grenze gemessen.** Bekaeme der
    Postfach-Weg PAUSCHAL die Moeglichkeit, Fragen zu registrieren, koennte
    jede zugestellte Nachricht einen Modelllauf ausloesen — an jenem Tag liefen
    so fuenf Laeufe in sechzehn Sekunden, deren ganzes Ergebnis „Passt." und
    „Gut." war.

    Deshalb ist der Knopf **angefordert, nicht Standard**: Ohne das Feld im
    Auftrag entsteht keiner."""
    import bot
    assert bot._postfach_knopf(None) is None, "ohne Anforderung entsteht ein Knopf"
    assert bot._postfach_knopf({}) is None, "ein leeres Feld erzeugt einen Knopf"
    # Und die Gegenrichtung: mit Anforderung entsteht er sehr wohl.
    echt = bot._postfach_knopf({"art": "wachposten_hinterlegen",
                                "kennung": "abc123456789"})
    assert echt is not None, "der angeforderte Knopf entsteht nicht"


def _der_knopf_startet_kein_modell():
    """**Die zweite Haelfte derselben Leitplanke.** Der Knopf darf wirken,
    aber nicht starten — sonst waere die stille Quittung von hinten wieder
    ausgehebelt. Gemessen am Quelltext der Behandlung: keine Sitzung, keine
    Warteschlange, kein Agent."""
    import inspect, bot
    quelle = inspect.getsource(bot.on_postfach_knopf) + \
        inspect.getsource(bot._wachposten_hinterlegen)
    # Nur ausfuehrbare Zeilen — ein Pruefer, der ueber seinen eigenen
    # Erklaerkommentar stolpert, wird binnen einer Woche abgeschaltet.
    code = "\n".join(z for z in quelle.splitlines()
                     if z.strip() and not z.strip().startswith("#")
                     and '"""' not in z)
    for verboten in ("query_claude", "ClaudeSDKClient", "enqueue",
                     "process_user_text", "stream_response"):
        assert verboten not in code, \
            f"der Knopf startet einen Modelllauf ueber {verboten}"


check("ein Fehlersturm sieht nicht aus wie ein Einzelfall (W1)",
      _ein_fehlersturm_sieht_nicht_aus_wie_ein_einzelfall)
check("dieselbe Zeile wird zwischen Laeufen gedaempft (Gegenrichtung)",
      _dieselbe_zeile_wird_zwischen_laeufen_gedaempft)
check("der Befund wird nicht verbraucht, bevor er ankommt (W2)",
      _der_befund_wird_nicht_verbraucht_bevor_er_ankommt)
check("die Fundstelle nennt Zeile und Zeit (W3)", _die_fundstelle_nennt_zeile_und_zeit)
check("halbe Zeilen werden nicht zerrissen (W4)", _halbe_zeilen_werden_nicht_zerrissen)
check("Ampel-Ausfall wird benannt (W5)", _ampel_ausfall_wird_benannt)
check("die Meldung traegt einen Knopf (Adams Entscheid 00:38)",
      _meldung_traegt_einen_knopf)
check("die Kennung haengt am Befund, nicht an der Zeit",
      _die_kennung_haengt_am_befund_nicht_an_der_zeit)
check("erfundene Knopfarten werden abgewiesen",
      _botenpost_weist_erfundene_knopfarten_ab)
check("ohne angeforderten Knopf gibt es keinen (Claudia 24.07.)",
      _ohne_angeforderten_knopf_gibt_es_keinen)
check("der Knopf startet kein Modell", _der_knopf_startet_kein_modell)
check("Gedaempftes wird gezaehlt und genannt (Claudia 2)",
      _gedaempfte_werden_gezaehlt_und_genannt)
check("ohne Daempfung keine Zaehlzeile (Gegenrichtung)",
      _ohne_daempfung_keine_zaehlzeile)
check("keine Frage ohne Wirkung (Adams Regel 20.08.)", _keine_frage_ohne_wirkung)

print()
if fails:
    print(f"❌ {len(fails)} Wachposten-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Wachposten-Tests bestanden.")
