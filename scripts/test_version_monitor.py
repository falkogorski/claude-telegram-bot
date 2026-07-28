#!/usr/bin/env python3
# <!-- ROLLE: test-versions-monitor -->
"""Verhaltenstest 5.21 — der Monitor und seine blinden Flecken.

**Der Schwerpunkt liegt auf dem, was er NICHT prüft.** Ein Monitor, der eine
Komponente stillschweigend überspringt, ist schlimmer als keiner: Der Eintrag
steht im Register, sieht nach Abdeckung aus, und niemand sieht ihn je an.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="vm-"))
os.environ["VERSION_MONITOR_LOG"] = str(_TMP / "monitor.log")
os.environ["BOT_ENVFILE"] = str(_TMP / "kein.env")   # kein Versand im Test
sys.path.insert(0, str(Path(__file__).resolve().parent))
import version_monitor as vm  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _lauf(components):
    """Lässt den Monitor über ein Register laufen und fängt die Meldung ab."""
    reg = _TMP / "reg.json"
    reg.write_text(json.dumps({"components": components}), encoding="utf-8")
    vm.REGISTER = reg
    gesendet = []
    vm._send_telegram = lambda t: gesendet.append(t)
    vm.main()
    return gesendet[0] if gesendet else ""


def _unbekannte_art_wird_gemeldet():
    """**Befund A.** Das Register nennt Arten, für die es keinen Handler gibt —
    `github_release` ist heute genau so ein Fall. Bisher landete das im
    Protokoll, und ein Protokoll, das niemand liest, ist kein Prüfer.
    """
    msg = _lauf([{"name": "irgendwas", "kind": "github_release",
                  "repo": "x/y"}])
    assert msg, "eine unbekannte Art erzeugte GAR KEINE Meldung"
    assert "irgendwas" in msg and "github_release" in msg, \
        f"die Komponente wird nicht beim Namen genannt: {msg[:120]}"
    assert "NICHT geprüft" in msg, \
        "die Meldung sagt nicht, dass der Eintrag ungeprüft dasteht"


def _weggebrochene_quelle_wird_gemeldet():
    """**Befund D, dieselbe Klasse.** „Es gibt nichts Neues" und „ich komme
    nicht mehr an die Auskunft" sehen von außen gleich aus — und nur das
    zweite ist ein Problem."""
    vm.HANDLERS["probe"] = (lambda c: "1.0.0", lambda c: "")   # Quelle stumm
    try:
        msg = _lauf([{"name": "quelle-weg", "kind": "probe"}])
        assert "quelle-weg" in msg and "nicht erreichbar" in msg, \
            f"die weggebrochene Quelle blieb stumm: {msg[:120]}"
    finally:
        vm.HANDLERS.pop("probe", None)


def _gesunde_lage_schweigt():
    """Die Gegenprobe — sonst wäre der Monitor ein Dauer-Alarm."""
    vm.HANDLERS["probe"] = (lambda c: "2.0.0", lambda c: "2.0.0")
    try:
        assert _lauf([{"name": "aktuell", "kind": "probe"}]) == "", \
            "bei aktueller Version wurde gemeldet"
    finally:
        vm.HANDLERS.pop("probe", None)


def _update_wird_gemeldet_major_markiert():
    vm.HANDLERS["probe"] = (lambda c: "1.9.0", lambda c: "2.0.0")
    try:
        msg = _lauf([{"name": "springt", "kind": "probe"}])
        assert "springt" in msg and "1.9.0" in msg and "2.0.0" in msg
        assert "MAJOR" in msg, "ein Major-Sprung wird nicht als solcher markiert"
    finally:
        vm.HANDLERS.pop("probe", None)


def _kein_modell_und_keine_installation():
    """Zwei harte Leitplanken: kein Modell-Aufruf (AGB, zeitgesteuert) und
    keine Installation (E3 — der Monitor meldet, er handelt nicht)."""
    quelle = Path(vm.__file__).read_text(encoding="utf-8")
    for verboten in ("ClaudeSDKClient", "anthropic", "pip install",
                     "npm install", "apt install"):
        assert verboten not in quelle, \
            f"der Monitor enthält `{verboten}` — er soll melden, nicht handeln"


check("unbekannte Art wird GEMELDET, nicht übersprungen (Befund A)",
      _unbekannte_art_wird_gemeldet)
check("weggebrochene Quelle wird gemeldet (Befund D)",
      _weggebrochene_quelle_wird_gemeldet)
check("gesunde Lage schweigt", _gesunde_lage_schweigt)
check("Update wird gemeldet, Major markiert", _update_wird_gemeldet_major_markiert)
check("kein Modell-Aufruf, keine Installation", _kein_modell_und_keine_installation)

print()
if fails:
    print(f"❌ {len(fails)} Monitor-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Versions-Monitor-Tests bestanden.")
