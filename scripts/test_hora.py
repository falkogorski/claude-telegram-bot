#!/usr/bin/env python3
# <!-- ROLLE: test-hora -->
"""Verhaltenstest Hora — der autonome Läufer.

Geprüft werden die fünf Bedingungen. Der Schwerpunkt liegt auf dem, was Hora
**nicht** tut: keine Entscheidungen treffen, nicht auf rotem Fundament bauen,
nicht endlos gegen dieselbe Wand rennen. Es wird nichts ausgeführt und nichts
versendet.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="hora-"))
os.environ["HORA_DIR"] = str(_TMP / "hora")
os.environ["HORA_LISTE"] = str(_TMP / "hora" / "auftragsliste.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["FREIGABE_DIR"] = str(_TMP / "freigaben")
os.environ["ALLOWED_USER_IDS"] = "304455165"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hora  # noqa: E402
import freigaben  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _liste(*auftraege):
    hora.ZUSTAND.mkdir(parents=True, exist_ok=True)
    hora.LISTE.write_text(json.dumps(list(auftraege), ensure_ascii=False),
                          encoding="utf-8")


def _leeren():
    for p in (hora.LISTE, hora.ZUSTAND / "fehlserie.json"):
        if p.exists():
            p.unlink()
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if out.exists():
        for f in out.glob("*.json"):
            f.unlink()
    for ordner in (freigaben.ANFRAGEN, freigaben.URTEILE, freigaben.PROTOKOLL):
        if ordner.exists():
            for f in ordner.glob("*.json"):
                f.unlink()


def _meldungen():
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if not out.exists():
        return []
    return [json.loads(f.read_text(encoding="utf-8"))["text"]
            for f in sorted(out.glob("*.json"))]


def _patch(regression=(True, "Ergebnis: 27/27"), lauf_erfolg=True):
    hora.regression = lambda: regression
    ausgefuehrt = []

    class _P:
        returncode = 0 if lauf_erfolg else 1
        stdout = "ok"
        stderr = ""

    def _run(cmd, **kw):
        if cmd[:2] == ["bash", "-lc"]:
            ausgefuehrt.append(cmd[2])
        return _P()
    hora.subprocess.run = _run
    return ausgefuehrt


# --- Bedingung 2: leere Liste → melden, nichts tun -------------------------
def _leere_liste_meldet():
    _leeren()
    _liste()
    ausgefuehrt = _patch()
    assert hora.lauf() == 0
    assert not ausgefuehrt, "bei leerer Liste wurde etwas ausgeführt"
    m = _meldungen()
    assert m and "leer" in m[0], f"Leerlauf nicht gemeldet: {m}"


# --- Bedingung 3: rotes Fundament → nichts anfassen ------------------------
def _rotes_fundament_stoppt():
    _leeren()
    _liste({"titel": "irgendwas", "befehl": "echo hi"})
    ausgefuehrt = _patch(regression=(False, "Ergebnis: 25/27"))
    assert hora.lauf() == 1
    assert not ausgefuehrt, "auf rotem Fundament wurde gearbeitet!"
    assert "vor" in _meldungen()[0], "der Grund wird nicht benannt"


# --- Bedingung 1: Zustimmungspflichtiges wird GEPARKT ----------------------
def _zustimmung_wird_geparkt():
    _leeren()
    _liste({"titel": "SDK anheben", "braucht_zustimmung": True,
            "aktion": "pip install claude-agent-sdk==0.3.0", "ampel": "gelb",
            "rueckweg": "pip install claude-agent-sdk==0.2.127"})
    ausgefuehrt = _patch()
    assert hora.lauf() == 0
    assert not ausgefuehrt, "Hora hat selbst entschieden statt zu parken!"
    offen = freigaben.offene()
    assert len(offen) == 1 and offen[0].herkunft == "Hora", \
        f"nichts geparkt: {offen}"
    assert "geparkt" in _meldungen()[0]


# --- Bedingung 4: Abbruch nach drei Fehlläufen ----------------------------
def _abbruch_nach_drei_fehllaeufen():
    _leeren()
    _liste({"titel": "kaputt", "befehl": "false"})
    _patch(regression=(True, "Ergebnis: 27/27"), lauf_erfolg=False)
    # Der Auftrag scheitert; die Regression nach dem Lauf ist rot.
    hora.regression = lambda: (True, "Ergebnis: 27/27")
    for i in range(hora.FEHLGRENZE):
        hora.regression = lambda: (True, "Ergebnis: 27/27") if i < 0 else (True, "x")
        hora.subprocess.run = lambda cmd, **kw: type(
            "P", (), {"returncode": 1, "stdout": "", "stderr": "kaputt"})()
        hora.lauf()
    rc = hora.lauf()
    assert rc == 2, f"Hora läuft nach {hora.FEHLGRENZE} Fehlläufen weiter: {rc}"
    assert "hält an" in _meldungen()[-1], "der Halt wird nicht gemeldet"


# --- Fehlschlag hakt NICHTS ab -------------------------------------------
def _fehlschlag_haekelt_nicht_ab():
    _leeren()
    _liste({"titel": "wackelig", "befehl": "echo x"})
    hora.regression = lambda: (True, "Ergebnis: 27/27")
    hora.subprocess.run = lambda cmd, **kw: type(
        "P", (), {"returncode": 1, "stdout": "", "stderr": "schief"})()
    hora.lauf()
    assert hora.auftraege(), "ein gescheiterter Auftrag wurde abgehakt!"


# --- Probelauf führt nichts aus ------------------------------------------
def _probelauf_fuehrt_nichts_aus():
    _leeren()
    _liste({"titel": "test", "befehl": "echo hi"})
    ausgefuehrt = _patch()
    assert hora.lauf(trocken=True) == 0
    assert not ausgefuehrt, "der Probelauf hat ausgeführt!"
    assert "HÄTTE" in _meldungen()[0]


# --- Ohne Befehl wird nichts erfunden ------------------------------------
def _ohne_befehl_kein_raten():
    _leeren()
    _liste({"titel": "unklar formuliert"})
    ausgefuehrt = _patch()
    hora.lauf()
    assert not ausgefuehrt, "Hora hat sich einen Befehl ausgedacht!"
    m = _meldungen()
    assert m, "kein Bericht, obwohl der Auftrag unbrauchbar war"
    assert any("ausführbar" in x and "Befehl" in x for x in m), \
        f"der Grund wird nicht benannt: {m}"


# --- A1: Die Kette — mehrere Aufträge in EINEM Lauf ------------------------
def _kette_arbeitet_die_liste_leer():
    """Vorher lief genau ein Auftrag je Lauf. Das war eine Annahme über das
    Kontingent, keine Messung — und hätte in vierzehn Tagen achtundzwanzig
    Aufträge als Obergrenze gesetzt."""
    _leeren()
    _liste({"titel": "eins", "befehl": "echo 1"},
           {"titel": "zwei", "befehl": "echo 2"},
           {"titel": "drei", "befehl": "echo 3"})
    ausgefuehrt = _patch()
    assert hora.lauf() == 0
    assert ausgefuehrt == ["echo 1", "echo 2", "echo 3"], \
        f"die Kette hat nicht alles abgearbeitet: {ausgefuehrt}"
    assert hora.auftraege() == [], "es blieb etwas offen"
    m = _meldungen()
    assert len(m) == 1, f"ein Lauf, ein Bericht — nicht {len(m)}"
    assert "Erledigt (3)" in m[0], f"Bericht zählt falsch: {m[0]}"


# --- B2: Eine Frage hält den Läufer NICHT an ------------------------------
def _geparkte_frage_haelt_nicht_an():
    _leeren()
    _liste({"titel": "braucht Adam", "braucht_zustimmung": True,
            "aktion": "pip install irgendwas", "ampel": "gelb",
            "rueckweg": "pip install altes"},
           {"titel": "unabhängig", "befehl": "echo weiter"})
    ausgefuehrt = _patch()
    hora.lauf()
    assert ausgefuehrt == ["echo weiter"], \
        f"Hora ist an der Frage hängen geblieben: {ausgefuehrt}"
    assert len(freigaben.offene()) == 1, "die Frage wurde nicht geparkt"


def _abhaengiger_auftrag_wird_uebersprungen():
    """Ein Läufer, der auf einem nicht fertigen Vorgänger aufbaut, richtet mehr
    Schaden an als einer, der ihn überspringt."""
    _leeren()
    _liste({"titel": "Vorgänger", "braucht_zustimmung": True,
            "aktion": "etwas", "ampel": "gelb"},
           {"titel": "Folge", "befehl": "echo darf-nicht",
            "haengt_an": ["Vorgänger"]},
           {"titel": "Frei", "befehl": "echo darf-doch"})
    ausgefuehrt = _patch()
    hora.lauf()
    assert ausgefuehrt == ["echo darf-doch"], \
        f"der abhängige Auftrag lief trotzdem: {ausgefuehrt}"
    assert any("hängt an" in x for x in _meldungen()), \
        "der Grund fürs Überspringen wird nicht benannt"


def _kontingent_haelt_an_ohne_abzuhaken():
    """Kontingent erschöpft ist kein Fehlschlag — nichts wird abgehakt."""
    _leeren()
    _liste({"titel": "erster", "befehl": "echo x"},
           {"titel": "zweiter", "befehl": "echo y"})
    hora.regression = lambda: (True, "Ergebnis: 27/27")
    hora.subprocess.run = lambda cmd, **kw: type(
        "P", (), {"returncode": 1, "stdout": "",
                  "stderr": "Claude usage limit reached"})()
    assert hora.lauf() == 2, "Hora lief trotz erschöpftem Kontingent weiter"
    assert len(hora.auftraege()) == 2, "bei Kontingent-Halt wurde abgehakt!"
    assert "Kontingent" in _meldungen()[-1]


check("leere Liste → melden, nichts tun", _leere_liste_meldet)
check("Kette arbeitet die Liste leer (A1)", _kette_arbeitet_die_liste_leer)
check("geparkte Frage hält den Läufer nicht an (B2)", _geparkte_frage_haelt_nicht_an)
check("abhängiger Auftrag wird übersprungen (B2)", _abhaengiger_auftrag_wird_uebersprungen)
check("Kontingent-Halt hakt nichts ab", _kontingent_haelt_an_ohne_abzuhaken)
check("rotes Fundament → nicht arbeiten", _rotes_fundament_stoppt)
check("Zustimmungspflichtiges wird geparkt, nicht entschieden", _zustimmung_wird_geparkt)
check("Abbruch nach drei Fehlläufen", _abbruch_nach_drei_fehllaeufen)
check("Fehlschlag hakt nichts ab", _fehlschlag_haekelt_nicht_ab)
check("Probelauf führt nichts aus", _probelauf_fuehrt_nichts_aus)
check("ohne Befehl wird nichts geraten", _ohne_befehl_kein_raten)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Hora-Tests bestanden.")
