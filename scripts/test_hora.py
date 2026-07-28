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
import time
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
    assert "Wartet auf dein Urteil" in _meldungen()[0]


def _geparktes_bleibt_in_der_liste_und_laeuft_nach_der_freigabe():
    """**Der Fund aus dem Echtlauf vom 26.07., 01:45.**

    Ein geparkter Auftrag wurde abgehakt und verschwand damit aus der Liste.
    Adams Zustimmung wäre ins Leere gelaufen — niemand hätte die Aktion je
    ausgeführt. Die Meldung versprach „ich lege es dir wieder vor", und der
    Code hatte den Auftrag schon weggeräumt.

    Der Grundsatz lautet: *Die Antwort holt den Läufer später ein, nicht
    umgekehrt.* Dafür muss etwas dasein, das eingeholt werden kann. Genau das
    prüft dieser Test — in beide Richtungen, Ja **und** Nein.
    """
    _leeren()
    _liste({"titel": "SDK anheben", "braucht_zustimmung": True,
            "aktion": "pip install claude-agent-sdk==0.3.0", "ampel": "gelb",
            "rueckweg": "pip install claude-agent-sdk==0.2.127",
            "befehl": "echo eingespielt"})

    # Lauf 1: parken — und NICHT abhaken.
    ausgefuehrt = _patch()
    hora.lauf()
    daten = json.loads(hora.LISTE.read_text(encoding="utf-8"))
    assert not daten[0].get("erledigt"), \
        "der geparkte Auftrag wurde abgehakt — Adams Ja liefe ins Leere"
    kennung = daten[0].get("freigabe_kennung")
    assert kennung, "ohne vermerkte Kennung findet Hora sein Urteil nie wieder"
    assert not ausgefuehrt, "die Aktion lief schon VOR der Freigabe"

    # Lauf 2, immer noch ohne Urteil: nicht doppelt vorlegen, nichts ausführen.
    ausgefuehrt = _patch()
    hora.lauf()
    assert len(freigaben.offene()) == 1, \
        "dieselbe Frage wurde ein zweites Mal in die Liste gelegt"
    assert not ausgefuehrt, "ohne Urteil wurde ausgeführt"

    # Adam sagt Ja → beim nächsten Lauf wird die Aktion ausgeführt und abgehakt.
    freigaben.urteilen(kennung, True, "Adam")
    ausgefuehrt = _patch()
    hora.lauf()
    assert ausgefuehrt, "nach der Freigabe geschah nichts — der Kreis ist offen"
    daten = json.loads(hora.LISTE.read_text(encoding="utf-8"))
    assert daten[0].get("erledigt"), "nach Ausführung nicht abgehakt"
    assert any("Nach deiner Freigabe" in m for m in _meldungen()), \
        "die Ausführung nach der Freigabe wird nicht berichtet"

    # Gegenprobe: ein Nein beendet den Auftrag, ohne ihn auszuführen.
    _leeren()
    _liste({"titel": "riskant", "braucht_zustimmung": True, "ampel": "gelb",
            "aktion": "rm -rf /wichtig", "befehl": "echo DAS DARF NIE LAUFEN"})
    _patch()
    hora.lauf()
    kennung = json.loads(hora.LISTE.read_text(encoding="utf-8"))[0]["freigabe_kennung"]
    freigaben.urteilen(kennung, False, "Adam")
    ausgefuehrt = _patch()
    hora.lauf()
    assert not ausgefuehrt, "ein abgelehnter Auftrag wurde ausgeführt!"
    assert json.loads(hora.LISTE.read_text(encoding="utf-8"))[0].get("erledigt"), \
        "ein abgelehnter Auftrag bleibt ewig in der Liste"


def _fehlgrund_nennt_den_befehl_nicht_die_regression():
    """**Zweiter Fund aus dem Echtlauf.** Die Meldung lautete sinngemäß
    „gescheitert (30/30 bestanden)" — die Zahl war richtig und die Aussage
    nutzlos, weil sie die falsche Frage beantwortet. Wer nachts eine
    Fehlermeldung liest, will wissen, **woran der Auftrag scheiterte**.
    """
    _leeren()
    _liste({"titel": "kaputt", "befehl": "false"})
    hora.regression = lambda: (True, "== Ergebnis: 30/30 bestanden ==")
    hora.subprocess.run = lambda cmd, **kw: type(
        "P", (), {"returncode": 1, "stdout": "",
                  "stderr": "Datei nicht gefunden: docs/fehlt.md"})()
    hora.lauf()
    zeile = next(m for m in _meldungen() if "Nicht sauber" in m)
    assert "Datei nicht gefunden" in zeile, \
        f"der Fehlgrund fehlt in der Meldung: {zeile}"
    assert "30/30 bestanden ==)" not in zeile, \
        "der Regressionsstand wird immer noch als Fehlgrund ausgegeben"


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
check("Geparktes bleibt in der Liste und laeuft nach der Freigabe",
      _geparktes_bleibt_in_der_liste_und_laeuft_nach_der_freigabe)
check("Fehlgrund nennt den Befehl, nicht den Regressionsstand",
      _fehlgrund_nennt_den_befehl_nicht_die_regression)
check("Abbruch nach drei Fehlläufen", _abbruch_nach_drei_fehllaeufen)
check("Fehlschlag hakt nichts ab", _fehlschlag_haekelt_nicht_ab)
check("Probelauf führt nichts aus", _probelauf_fuehrt_nichts_aus)
check("ohne Befehl wird nichts geraten", _ohne_befehl_kein_raten)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Hora-Tests bestanden.")


def _nur_ein_lauf_zugleich():
    """Conni ②: Bei Zweistunden-Takt kann ein verketteter Lauf länger dauern
    als der Abstand zum nächsten. Ohne Schloss liefen zwei parallel in dieselbe
    Liste — doppelte Sitzungen, zwei Läufe, die denselben Auftrag abhaken
    wollen, Kontingent doppelt belastet.
    """
    _leeren()
    hora.SCHLOSS.unlink(missing_ok=True)
    _liste({"titel": "x", "befehl": "echo x"})

    # Ein Lauf hält das Schloss: der zweite geht still weg, ohne zu arbeiten.
    assert hora._schloss_nehmen(), "das Schloss ließ sich nicht nehmen"
    ausgefuehrt = _patch()
    assert hora.lauf() == 0, "der zweite Lauf meldete einen Fehler statt zu gehen"
    assert not ausgefuehrt, "zwei Läufe arbeiteten gleichzeitig!"
    hora._schloss_geben()

    # Danach geht es wieder.
    ausgefuehrt = _patch()
    hora.lauf()
    assert ausgefuehrt, "nach Freigabe des Schlosses lief nichts mehr"
    assert not hora.SCHLOSS.exists(), "das Schloss blieb nach dem Lauf liegen"

    # Ein ABGESTÜRZTER Lauf darf das Schloss nicht ewig halten — sonst
    # schwiege Hora bis zur Rückkehr, und niemand wüsste warum.
    hora._schloss_nehmen()
    alt = time.time() - hora.SCHLOSS_ALT_S - 60
    os.utime(hora.SCHLOSS, (alt, alt))
    assert hora._schloss_nehmen(), "ein verwaistes Schloss wird nicht geräumt"
    hora._schloss_geben()

    # Und es geht auch bei einem Absturz MITTEN im Lauf wieder auf.
    def _kracht(*a, **kw):
        raise RuntimeError("Absturz mitten im Lauf")
    hora.regression = _kracht
    try:
        hora.lauf()
    except RuntimeError:
        pass
    assert not hora.SCHLOSS.exists(), \
        "nach einem Absturz blieb das Schloss liegen — Hora schwiege für immer"


def _leerlauf_wird_gedaempft():
    """Conni ③: Zwölf Läufe am Tag mal vierzehn Tage wären 168 gleichlautende
    „Liste leer"-Nachrichten. Wer diesen Absender überliest, überliest auch die
    eine, die zählt.
    """
    _leeren()
    hora.SCHLOSS.unlink(missing_ok=True)
    hora.LEERLAUF_MARKE.unlink(missing_ok=True)
    _liste()
    _patch()

    hora.lauf()
    assert len(_meldungen()) == 1, "die erste Leermeldung kam nicht"
    for _ in range(5):
        hora.lauf()
    assert len(_meldungen()) == 1, \
        f"der Leerlauf wurde {len(_meldungen())}× gemeldet statt einmal"

    # Nach einem Tag darf er wieder — die Auskunft veraltet ja.
    hora.LEERLAUF_MARKE.write_text(
        json.dumps({"zuletzt": time.time() - hora.LEERLAUF_STILLE_S - 60}),
        encoding="utf-8")
    hora.lauf()
    assert len(_meldungen()) == 2, "nach einem Tag kam keine neue Auskunft"

    # Und sobald wieder Arbeit da war, gilt die nächste Leere als neue Auskunft.
    _liste({"titel": "wieder was", "befehl": "echo x"})
    _patch()
    hora.lauf()
    assert not hora.LEERLAUF_MARKE.exists(), \
        "der Dämpfer entwarnt nicht, wenn wieder Arbeit da war"


check("nur ein Hora-Lauf zugleich (Schloss, auch nach Absturz)",
      _nur_ein_lauf_zugleich)
check("Leerlauf wird gedämpft (nicht 168× dasselbe)", _leerlauf_wird_gedaempft)
if fails:
    raise SystemExit(1)
