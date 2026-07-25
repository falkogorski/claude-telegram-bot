#!/usr/bin/env python3
# <!-- ROLLE: test-updater -->
"""Verhaltenstest der Updater-Härtung A1–A7 (Conni-Auswertung 25.07.).

Reine Logik-Prüfung mit ersetzten Systemaufrufen — es wird NICHTS installiert.
Deckt: Grundlinie-zuerst (A5), Versions-Drift (A3), Lauf-Schloss (A4),
vollständiger Freeze/Rollback (A1), ehrliche Rollback-Meldung (A2),
Selbst-Widerspruch (A6), Wiederhol-Schutz (A7).
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="updtest-"))
os.environ["UPDATER_STATE_DIR"] = str(_TMP / "state")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import updater as u  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


COMP = {"name": "demo", "kind": "pip", "ref": "demo",
        "venv": "/tmp/venv-demo"}


def _cand(cur="1.0.0", latest="1.1.0", ampel="gruen"):
    return [{"name": "demo", "kind": "pip", "cur": cur, "latest": latest,
             "ampel": ampel, "comp": COMP}]


def _patch(classify=None, regression=None, install=None, freeze=None,
           restore=None, installed=None):
    u.classify = classify or (lambda: _cand())
    u._regression = regression or (lambda: {"ok": True, "passed": 14, "total": 14,
                                            "line": "Ergebnis: 14/14", "raw_tail": ""})
    u._install = install or (lambda c, v: (True, ""))
    u._freeze_env = freeze or (lambda v: (True, "demo==1.0.0\n"))
    u._restore_env = restore or (lambda v, t: (True, ""))
    u._installed_version = installed or (lambda c: "1.0.0")


def _reset_state():
    u._clear_failure()
    u._release_lock()


# --- A5: Fundament rot → gar nichts anfassen --------------------------------
def _a5_baseline_first():
    _reset_state()
    touched = []
    _patch(regression=lambda: {"ok": False, "passed": 12, "total": 14,
                               "line": "Ergebnis: 12/14", "raw_tail": ""},
           install=lambda c, v: (touched.append(v), (True, ""))[1])
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert r["state"] == "fundament_rot", f"Zustand falsch: {r['state']}"
    assert not touched, "Es wurde installiert, obwohl das Fundament rot war!"
    assert "Erst reparieren" in r["msg"]


# --- A3: Versions-Drift → nicht einspielen, neu fragen ----------------------
def _a3_drift():
    _reset_state()
    touched = []
    _patch(classify=lambda: _cand(latest="1.2.0"),      # jetzt 1.2.0 verfügbar
           install=lambda c, v: (touched.append(v), (True, ""))[1])
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})    # angezeigt war 1.1.0
    assert r["state"] == "abweichung", f"Zustand falsch: {r['state']}"
    assert not touched, "Es wurde eine nicht freigegebene Version installiert!"


def _a3_exakte_version():
    _reset_state()
    seen = []
    _patch(install=lambda c, v: (seen.append(v), (True, ""))[1],
           installed=lambda c: "1.1.0")
    u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert seen == ["1.1.0"], f"nicht die freigegebene Version installiert: {seen}"


# --- A4: Lauf-Schloss -------------------------------------------------------
def _a4_lock():
    _reset_state()
    _patch()
    assert u._acquire_lock(), "erstes Schloss sollte greifen"
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert r["state"] == "belegt", f"zweiter Lauf nicht abgewiesen: {r['state']}"
    u._release_lock()


# --- A1: ohne Freeze kein Update -------------------------------------------
def _a1_kein_freeze():
    _reset_state()
    touched = []
    _patch(freeze=lambda v: (False, "pip kaputt"),
           install=lambda c, v: (touched.append(v), (True, ""))[1])
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert r["state"] == "kein_freeze", f"Zustand falsch: {r['state']}"
    assert not touched, "Installiert, obwohl kein Rollback-Stand gesichert war!"


def _a1_voller_rollback():
    _reset_state()
    restored = []
    reg = iter([{"ok": True, "passed": 14, "total": 14, "line": "Ergebnis: 14/14", "raw_tail": ""},
                {"ok": False, "passed": 13, "total": 14, "line": "Ergebnis: 13/14", "raw_tail": ""},
                {"ok": True, "passed": 14, "total": 14, "line": "Ergebnis: 14/14", "raw_tail": ""}])
    _patch(regression=lambda: next(reg),
           restore=lambda v, t: (restored.append((v, t)), (True, ""))[1],
           installed=lambda c: "1.0.0")
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert restored, "kein vollständiger Umgebungs-Rollback (pip -r freeze) ausgeführt"
    assert "demo==1.0.0" in restored[0][1], "Rollback nutzte nicht den Freeze-Stand"
    assert "demo" in r["rolled_back"]


# --- A2: fehlgeschlagener Rollback wird LAUT gemeldet -----------------------
def _a2_rollback_ehrlich():
    _reset_state()
    reg = iter([{"ok": True, "passed": 14, "total": 14, "line": "Ergebnis: 14/14", "raw_tail": ""},
                {"ok": False, "passed": 13, "total": 14, "line": "Ergebnis: 13/14", "raw_tail": ""},
                {"ok": False, "passed": 13, "total": 14, "line": "Ergebnis: 13/14", "raw_tail": ""}])
    _patch(regression=lambda: next(reg),
           restore=lambda v, t: (False, "Netzwerkfehler"),
           installed=lambda c: "1.1.0")   # blieb auf der NEUEN Version
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert r["state"] == "rollback_unvollstaendig", f"Zustand falsch: {r['state']}"
    assert "ROLLBACK UNVOLLSTÄNDIG" in r["msg"], "unvollständiger Rollback nicht laut gemeldet"
    assert any("1.1.0" in s for s in r["not_rolled_back"]), "Zustand je Paket fehlt"
    assert "demo" not in r["rolled_back"], "fälschlich als zurückgerollt gemeldet"


# --- A6: Selbst-Widerspruch aussprechen ------------------------------------
def _a6_widerspruch():
    _reset_state()
    reg = iter([{"ok": True, "passed": 14, "total": 14, "line": "Ergebnis: 14/14", "raw_tail": ""},
                {"ok": False, "passed": 12, "total": 14, "line": "Ergebnis: 12/14", "raw_tail": ""},
                {"ok": False, "passed": 12, "total": 14, "line": "Ergebnis: 12/14", "raw_tail": ""}])
    _patch(regression=lambda: next(reg), installed=lambda c: "1.0.0")
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})
    assert "NICHT am Update" in r["msg"], "gleicher Wert vor/nach Rollback nicht ausgesprochen"


# --- A7: Wiederhol-Schutz ---------------------------------------------------
def _a7_wiederholung():
    _reset_state()
    def _reg_fail():
        return {"ok": False, "passed": 13, "total": 14, "line": "Ergebnis: 13/14", "raw_tail": ""}
    reg = iter([{"ok": True, "passed": 14, "total": 14, "line": "Ergebnis: 14/14", "raw_tail": ""},
                _reg_fail(), _reg_fail()])
    _patch(regression=lambda: next(reg), installed=lambda c: "1.0.0")
    u.apply_updates(["demo"], {"demo": "1.1.0"})          # 1. Lauf scheitert
    _patch()                                              # Grundlinie wieder grün/gleich
    touched = []
    u._install = lambda c, v: (touched.append(v), (True, ""))[1]
    r = u.apply_updates(["demo"], {"demo": "1.1.0"})      # 2. Lauf, gleiche Lage
    assert r["state"] == "wiederholung", f"Zustand falsch: {r['state']}"
    assert not touched, "gleiche gescheiterte Kombination wurde erneut eingespielt"


check("A5 Grundlinie zuerst (rot → nichts anfassen)", _a5_baseline_first)
check("A3 Versions-Drift → nicht einspielen", _a3_drift)
check("A3 exakt die freigegebene Version", _a3_exakte_version)
check("A4 Lauf-Schloss", _a4_lock)
check("A1 ohne Freeze kein Update", _a1_kein_freeze)
check("A1 vollständiger Umgebungs-Rollback", _a1_voller_rollback)
check("A2 unvollständiger Rollback wird laut", _a2_rollback_ehrlich)
check("A6 Selbst-Widerspruch ausgesprochen", _a6_widerspruch)
check("A7 Wiederhol-Schutz", _a7_wiederholung)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Updater-Härtungstests (A1–A7) bestanden.")
