#!/usr/bin/env python3
# <!-- ROLLE: test-wartungsfenster -->
"""Verhaltenstest B2/B3 — Wartungsfenster (Conni-Freigabe 25.07.).

Geprüft werden die drei Auflagen und — vor allem — der **Probelauf**: Solange
das Fenster nicht scharf ist, darf es **nichts** einspielen, sondern nur melden,
was es getan hätte. Es wird nichts installiert und nichts versendet.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b3test-"))
os.environ["UPDATER_STATE_DIR"] = str(_TMP / "state")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["ALLOWED_USER_IDS"] = "304455165"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import wartungsfenster as wf  # noqa: E402
import updater as upd  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _reset(scharf=False):
    for p in (wf.VORGEMERKT, wf.PROBELAUF, wf.SCHARF):
        if p.exists():
            p.unlink()
    if scharf:
        wf.SCHARF.parent.mkdir(parents=True, exist_ok=True)
        wf.SCHARF.write_text("scharf", encoding="utf-8")
    ordner = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if ordner.exists():
        for f in ordner.glob("*.json"):
            f.unlink()


def _meldungen() -> list[str]:
    ordner = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if not ordner.exists():
        return []
    return [json.loads(f.read_text(encoding="utf-8"))["text"]
            for f in sorted(ordner.glob("*.json"))]


def _angebot(name="demo", version="1.1.0"):
    upd.classify = lambda: [{"name": name, "kind": "pip", "cur": "1.0.0",
                             "latest": version, "ampel": "gelb", "comp": {}}]


def _kein_einspielen():
    """Wird gleich scharf gestellt — merkt sich jeden Einspiel-Versuch."""
    versuche = []
    upd.apply_updates = lambda n, e=None: (versuche.append((n, e)),
                                           {"ok": True, "msg": "eingespielt"})[1]
    return versuche


# --- (a) Vormerken, sichtbar, stornierbar ----------------------------------
def _vormerken_und_storno():
    _reset()
    wf.vormerken("demo", "1.1.0")
    assert [e["name"] for e in wf.vormerkungen()] == ["demo"], "nicht vorgemerkt"
    assert "demo" in wf.uebersicht() and "1.1.0" in wf.uebersicht(), \
        "Vormerkung ist nicht sichtbar"
    assert "Probelauf" in wf.uebersicht(), "der Modus steht nicht in der Übersicht"
    assert wf.stornieren("demo") is True, "Storno wirkte nicht"
    assert wf.vormerkungen() == [], "nach dem Storno liegt noch etwas"
    assert wf.stornieren("demo") is False, "Storno eines Unbekannten meldet Erfolg"


def _keine_doppelten_vormerkungen():
    _reset()
    wf.vormerken("demo", "1.1.0")
    wf.vormerken("demo", "1.2.0")
    liste = wf.vormerkungen()
    assert len(liste) == 1, f"doppelte Vormerkung: {liste}"
    assert liste[0]["version"] == "1.2.0", "die neuere Freigabe hat nicht gewonnen"


# --- (c) Meldung auch bei „nichts vorgemerkt" ------------------------------
def _meldung_auch_bei_stille():
    _reset()
    _angebot()
    rc = wf.lauf()
    m = _meldungen()
    assert rc == 0 and m, "kein Bericht, obwohl das Fenster lief"
    assert "nichts war vorgemerkt" in m[0], f"Stille falsch gemeldet: {m[0]}"


# --- Der Probelauf: prüfen, melden, NICHTS einspielen ----------------------
def _probelauf_spielt_nichts_ein():
    _reset()
    _angebot()
    versuche = _kein_einspielen()
    wf.vormerken("demo", "1.1.0")
    wf.lauf()
    assert not versuche, "im Probelauf wurde eingespielt!"
    m = _meldungen()
    assert m and "HÄTTE" in m[0], f"der Probelauf sagt nicht, was er getan hätte: {m}"
    assert "1 von 3 sauber" in m[0], f"Probelauf-Zähler fehlt: {m[0]}"
    assert wf.vormerkungen(), "die Vormerkung wurde im Probelauf verbraucht"


def _nach_drei_laeufen_wird_gefragt():
    _reset()
    _angebot()
    _kein_einspielen()
    wf.vormerken("demo", "1.1.0")
    for _ in range(3):
        wf.lauf()
    m = _meldungen()[-1]
    assert "scharf schalten" in m, f"nach drei Läufen wird nicht gefragt: {m}"
    assert "von selbst tue ich diesen Schritt nicht" in m, \
        "das Fenster verspricht nicht ausdrücklich, sich nicht selbst scharfzuschalten"
    assert not wf.SCHARF.exists(), "das Fenster hat sich SELBST scharf geschaltet!"


# --- (b) Nachprüfung zur Ausführungszeit ----------------------------------
def _abweichende_fassung_wird_nicht_eingespielt():
    _reset(scharf=True)
    _angebot(version="1.5.0")            # inzwischen eine andere Fassung
    versuche = _kein_einspielen()
    wf.vormerken("demo", "1.1.0")        # freigegeben war 1.1.0
    wf.lauf()
    assert not versuche, "eine nicht freigegebene Fassung wurde eingespielt!"
    m = _meldungen()[-1]
    assert "frage neu" in m, f"die Abweichung wird nicht als Rückfrage gemeldet: {m}"
    assert wf.vormerkungen(), "die abweichende Vormerkung wurde verworfen"


def _verschwundenes_wird_uebersprungen():
    _reset(scharf=True)
    upd.classify = lambda: []            # nichts mehr angeboten
    versuche = _kein_einspielen()
    wf.vormerken("demo", "1.1.0")
    wf.lauf()
    assert not versuche, "es wurde eingespielt, obwohl nichts angeboten wird"
    assert "Nicht mehr angeboten" in _meldungen()[-1], "Übersprungenes nicht benannt"


# --- Scharf: DANN wird eingespielt, und zwar genau das Freigegebene --------
def _scharf_spielt_genau_das_freigegebene_ein():
    _reset(scharf=True)
    _angebot(version="1.1.0")
    versuche = _kein_einspielen()
    wf.vormerken("demo", "1.1.0")
    wf.lauf()
    assert versuche, "im scharfen Modus wurde nichts eingespielt"
    namen, erwartet = versuche[0]
    assert namen == ["demo"], f"falsche Auswahl: {namen}"
    assert erwartet == {"demo": "1.1.0"}, \
        f"die erwartete Fassung wurde nicht mitgegeben: {erwartet}"
    assert not wf.vormerkungen(), "die erledigte Vormerkung blieb liegen"


check("(a) vormerken, sichtbar, stornierbar", _vormerken_und_storno)
check("(a) keine doppelten Vormerkungen", _keine_doppelten_vormerkungen)
check("(c) Meldung auch wenn nichts vorgemerkt war", _meldung_auch_bei_stille)
check("Probelauf spielt NICHTS ein, meldet aber die Absicht", _probelauf_spielt_nichts_ein)
check("nach drei Läufen wird gefragt, nicht selbst geschaltet", _nach_drei_laeufen_wird_gefragt)
check("(b) abweichende Fassung → neu fragen statt einspielen",
      _abweichende_fassung_wird_nicht_eingespielt)
check("(b) verschwundenes Update wird übersprungen", _verschwundenes_wird_uebersprungen)
check("scharf: genau die freigegebene Fassung", _scharf_spielt_genau_das_freigegebene_ein)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle B2/B3-Wartungsfenster-Tests bestanden.")
