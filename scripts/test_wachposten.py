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
_postfach_ersetzt = False


def _postfach_stellen():
    """Der RAND — hier würde etwas zu Adam hinausgehen."""
    import botenpost
    echt = botenpost.legen

    def _fang(text, absender, ziel=None, thread_id=None):
        _GESENDET.append(text)
        return Path("/dev/null")
    botenpost.legen = _fang
    wachposten.botenpost = botenpost
    return echt


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
    assert "Traceback" in _GESENDET[0], \
        f"der Wortlaut fehlt in der Meldung: {_GESENDET[0][:200]}"
    assert "Engywuck wecken" in _GESENDET[0], "die Schlusszeile fehlt"


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
    assert _GESENDET and "Merkzettel" in _GESENDET[0], \
        f"der beschädigte Stand wird verschwiegen: {_GESENDET[:1]}"


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


_postfach_stellen()   # der Rand wird EINMAL gestellt, vor allen Pruefungen

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
print("Alle Wachposten-Tests bestanden.")
