#!/usr/bin/env python3
# <!-- ROLLE: test-erinnerungs-laeufer -->
"""Verhaltenstest 7.2 — der Erinnerungs-Läufer. **Ausführend, ruhend gebaut.**

Der Läufer ist noch nicht scharf (kein Zeitgeber, kein Kalender-Zugang). Diese
Prüfungen messen ihn trotzdem vollständig — **gerade weil er ruht**: Was
niemand ausführt, verfällt still, und beim Scharfstellen ist die Aufmerksamkeit
längst woanders.

Der Kalender wird an seiner Modulgrenze ersetzt, alles darunter läuft echt.
"""
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_TMP = Path(tempfile.mkdtemp(prefix="e72-"))
os.environ["ERINNERUNG_DIR"] = str(_TMP / "zustand")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
(_TMP / "postfach" / "outbox").mkdir(parents=True)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import kalender  # noqa: E402
import erinnerungen  # noqa: E402

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
_ZIELE: list = []


def _postfach_stellen():
    """Der RAND. Die Attrappe spiegelt die ECHTE Signatur — kein `**kwargs`."""
    import botenpost

    def _fang(text, absender, ziel=None, thread_id=None, knopf=None):
        _GESENDET.append(text)
        _ZIELE.append(ziel)
        return Path("/dev/null")
    botenpost.legen = _fang
    erinnerungen.botenpost = botenpost


_postfach_stellen()


def _kalender_stellen(termine=(), aufgaben=(), zugang=True, wirft=False):
    erinnerungen.kalender.zugang_vorhanden = lambda: zugang

    def _termine(von=None, tage=7):
        if wirft:
            raise RuntimeError("CalDAV weg")
        return list(termine)

    def _aufgaben(liste=None):
        return list(aufgaben)
    erinnerungen.kalender.termine_lesen = _termine
    erinnerungen.kalender.aufgaben_lesen = _aufgaben


class _T:
    def __init__(self, text):
        self._t = text

    def lesbar(self):
        return self._t


def _frisch():
    _GESENDET.clear()
    _ZIELE.clear()
    for f in (_TMP / "zustand").glob("*"):
        f.unlink()


def _faelliges_wird_gemeldet():
    """Der Grundfall: Was ansteht, kommt von selbst."""
    _frisch()
    _kalender_stellen(termine=[_T("Freitag, 10:00 — Team-Runde")],
                      aufgaben=[_T("Rechnung schreiben")])
    n = erinnerungen.lauf()
    assert n == 2, f"von zwei Einträgen kamen {n}"
    assert _GESENDET and "Team-Runde" in _GESENDET[0]
    assert "Rechnung schreiben" in _GESENDET[0]


def _leerer_kalender_schweigt():
    """**Die Gegenprobe.** Ein Läufer, der auch bei nichts meldet, wird binnen
    einer Woche stummgeschaltet — und mit ihm die echten Meldungen."""
    _frisch()
    _kalender_stellen(termine=[], aufgaben=[])
    assert erinnerungen.lauf() == 0, "leerer Kalender erzeugt eine Meldung"
    assert not _GESENDET, "es ging etwas hinaus, obwohl nichts anstand"


def _eine_meldung_je_lauf_nicht_eine_je_termin():
    """**Die Postfach-Obergrenze ist der Grund.** Fünf Nachrichten je Stunde
    und Absender — ein Tag mit sechs Terminen wäre genau der Fall, in dem
    ausgerechnet die Erinnerung zurückgehalten würde."""
    _frisch()
    _kalender_stellen(termine=[_T(f"Termin {i}") for i in range(9)])
    erinnerungen.lauf()
    assert len(_GESENDET) == 1, \
        f"{len(_GESENDET)} Nachrichten statt einer gebündelten"
    assert "und 3 weitere" in _GESENDET[0], \
        f"die Restzeile fehlt: {_GESENDET[0][-120:]}"


def _derselbe_satz_wird_gedaempft():
    """Der Läufer sieht denselben Termin mehrfach, bevor er ansteht."""
    _frisch()
    _kalender_stellen(termine=[_T("Freitag, 10:00 — Team-Runde")])
    assert erinnerungen.lauf() == 1, "erste Meldung fehlt"
    vorher = len(_GESENDET)
    erinnerungen.lauf()
    assert len(_GESENDET) == vorher, "derselbe Satz wurde erneut gemeldet"


def _ein_neuer_termin_kommt_durch():
    """**Die Gegenrichtung des Dämpfers.** Sonst hätte man Ruhe statt
    Erinnerungen — dieselbe Verwechslung wie beim Wachposten-Dämpfer (W1)."""
    _frisch()
    _kalender_stellen(termine=[_T("Freitag, 10:00 — Team-Runde")])
    erinnerungen.lauf()
    _kalender_stellen(termine=[_T("Freitag, 10:00 — Team-Runde"),
                               _T("Freitag, 14:00 — Zahnarzt")])
    erinnerungen.lauf()
    assert len(_GESENDET) == 2, "der neue Termin wurde weggedämpft"
    assert "Zahnarzt" in _GESENDET[-1]


def _fehlender_zugang_wird_gesagt_nicht_als_leer_ausgegeben():
    """**Der wichtigste Fall.** Ohne Zugang „nichts anzusagen" zu melden wäre
    eine Falschauskunft: Der Kalender ist nicht leer, er ist unerreichbar."""
    _frisch()
    _kalender_stellen(zugang=False)
    n = erinnerungen.lauf()
    assert n > 0, "der fehlende Zugang wurde als leerer Kalender ausgegeben"
    assert _GESENDET and "Zugang fehlt" in _GESENDET[0], \
        f"der Grund wird nicht genannt: {_GESENDET[:1]}"


def _ausfall_einer_quelle_stoppt_die_andere_nicht():
    """Fällt der Termin-Abruf aus, sollen die Erinnerungen trotzdem kommen —
    und der Ausfall benannt werden. Ein Fehler, der beide mitnimmt, wäre die
    Stille, gegen die der Läufer gebaut ist."""
    _frisch()
    _kalender_stellen(aufgaben=[_T("Rechnung schreiben")], wirft=True)
    erinnerungen.lauf()
    assert _GESENDET, "es ging gar nichts hinaus"
    assert "Rechnung schreiben" in _GESENDET[0], "die zweite Quelle fiel mit aus"
    assert "nicht lesbar" in _GESENDET[0], "der Ausfall wird verschwiegen"


def _ohne_kanal_wird_das_gesagt():
    """**Ehrlich statt vollständig-wirkend.** Ohne 7.1 landet die Meldung im
    Bot-Chat; das zu verschweigen hieße, einen Zwischenstand als Endzustand
    auszugeben."""
    _frisch()
    erinnerungen.ZIEL_KANAL = ""
    _kalender_stellen(termine=[_T("Freitag, 10:00 — Team-Runde")])
    erinnerungen.lauf()
    assert "eigenen Erinnerungskanal" in _GESENDET[0], \
        "der fehlende Kanal wird verschwiegen"
    # Gegenrichtung: Mit Kanal entfällt der Hinweis und das Ziel wird genutzt.
    _frisch()
    erinnerungen.ZIEL_KANAL = "-100999"
    erinnerungen.lauf()
    assert "eigenen Erinnerungskanal" not in _GESENDET[0], \
        "der Hinweis steht auch mit Kanal noch da"
    assert _ZIELE[-1] == "-100999", f"das Ziel wurde nicht genutzt: {_ZIELE[-1]}"
    erinnerungen.ZIEL_KANAL = ""


def _kein_modell_im_pfad():
    """**AGB-Leitplanke.** Ein Zeit-Trigger, der ein Modell startet, ist
    Grauzone — Adams Linien-Entscheid deckt nur den nachgeholten Lauf nach
    einem Limit. Gemessen an den ausführbaren Zeilen."""
    quelle = (ROOT / "scripts" / "erinnerungen.py").read_text(encoding="utf-8")
    code = "\n".join(z for z in quelle.splitlines()
                     if z.strip() and not z.strip().startswith("#"))
    kopf_ende = code.find('"""', code.find('"""') + 3)
    code = code[kopf_ende:]
    for verboten in ("anthropic", "ClaudeSDKClient", "query(", "claude_agent_sdk"):
        assert verboten not in code, f"Modell-Aufruf im Pfad: {verboten}"


check("Fälliges wird gemeldet", _faelliges_wird_gemeldet)
check("leerer Kalender schweigt (Gegenprobe)", _leerer_kalender_schweigt)
check("eine Meldung je Lauf, nicht eine je Termin",
      _eine_meldung_je_lauf_nicht_eine_je_termin)
check("derselbe Satz wird gedämpft", _derselbe_satz_wird_gedaempft)
check("ein neuer Termin kommt durch (Gegenrichtung)", _ein_neuer_termin_kommt_durch)
check("fehlender Zugang wird gesagt, nicht als leer ausgegeben",
      _fehlender_zugang_wird_gesagt_nicht_als_leer_ausgegeben)
check("Ausfall einer Quelle stoppt die andere nicht",
      _ausfall_einer_quelle_stoppt_die_andere_nicht)
check("ohne Kanal wird das gesagt (beide Richtungen)", _ohne_kanal_wird_das_gesagt)
check("kein Modell im Pfad (AGB)", _kein_modell_im_pfad)

print()
if fails:
    print(f"❌ {len(fails)} 7.2-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle 7.2-Erinnerungs-Tests bestanden.")
