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
os.environ["VERSION_MONITOR_SEEN"] = str(_TMP / "gesehen.json")
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
    """**Befund A.** Wer eine Komponente mit einer Art eintraegt, fuer die es
    keinen Handler gibt, bekam stille Nichtpruefung: Der Eintrag stand im
    Register, sah nach Abdeckung aus, und wurde nie angesehen.

    Der Beispielfall war urspruenglich `github_release` — und ist es seit dem
    28.07. nicht mehr, weil diese Art jetzt einen Handler hat. Deshalb steht
    hier bewusst eine Art, die es NIE geben wird: Ein Pruefer, der an einer
    Tatsache haengt, die sich aendern darf, faellt beim naechsten Ausbau um.
    """
    msg = _lauf([{"name": "irgendwas", "kind": "gibtesnicht"}])
    assert msg, "eine unbekannte Art erzeugte GAR KEINE Meldung"
    assert "irgendwas" in msg and "gibtesnicht" in msg, \
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


def _fingerabdruck_statt_nummer():
    """**Docker und apt vergleichen auf UNGLEICHHEIT, nicht auf Groesse.**

    LobeChat laeuft auf `:latest` — dort aendert sich der Inhalt, ohne dass sich
    der Name aendert. Und eine Debian-Version wie `7:5.1.6-0+deb12u1` zerfaellt
    beim Zahlenlesen in Ziffern ohne Bedeutung (die fuehrende `7` ist eine
    Epoche, keine Hauptversion). Ein Groessenvergleich haette hier still
    IMMER "aktuell" gemeldet — die gefaehrlichste Art von Fehler.
    """
    alt, neu_ = "sha256:" + "a" * 64, "sha256:" + "b" * 64
    assert vm._cmp(alt, neu_, "docker")[0], "abweichender Fingerabdruck faellt nicht auf"
    assert not vm._cmp(alt, alt, "docker")[0], "gleicher Fingerabdruck meldet faelschlich"
    # Der Beweis, dass der Zahlenweg hier versagt haette:
    assert not vm._cmp(alt, neu_)[0], (
        "der Zahlenvergleich erkennt den Unterschied doch — dann traegt die "
        "Begruendung fuer die Sonderbehandlung nicht mehr")
    # Und die Epochen-Falle bei apt, an einem echten Debian-Paar:
    assert vm._cmp("7:5.1.6-0+deb12u1", "7:5.1.7-0+deb12u1", "systempaket")[0]


def _fingerabdruck_wird_gekuerzt():
    """71 Zeichen Fingerabdruck in einer Telegram-Meldung liest niemand."""
    # Auf dem Mac laeuft kein Docker — der echte Handler laege leer und der
    # Eintrag erschiene als "Quelle nicht erreichbar". Geprueft werden soll
    # aber die DARSTELLUNG, also wird die Quelle gestellt.
    vm.HANDLERS["docker"] = (lambda c: "sha256:" + "a" * 64,
                             lambda c: "sha256:" + "b" * 64)
    try:
        txt = _lauf([{"name": "abbild", "kind": "docker", "ref": "x/y:latest"}])
    finally:
        vm.HANDLERS["docker"] = (vm.cur_docker, vm.latest_docker)
    assert "sha256:" in txt and "a" * 64 not in txt, \
        f"der Fingerabdruck steht ungekuerzt in der Meldung: {txt[:200]}"


def _manual_meldet_sich_nach_frist_von_selbst():
    """**Der eigentliche Kern dieses Umbaus.**

    Manuelle Eintraege hingen bisher als Anhaengsel an einer Meldung, die es nur
    gab, wenn ANDERSWO ein Update gefunden wurde. Laeuft alles rund, schweigt
    der Monitor — und schwieg damit auch ueber die Punkte, die NIEMAND SONST
    prueft. Ausgerechnet `claude-modelle` und `verfahren-medien`, die sich nicht
    automatisch ermitteln lassen, waren an einen fremden Fund gekoppelt.
    """
    from datetime import datetime, timedelta
    eintrag = {"name": "verfahren-x", "kind": "manual",
               "intervall_tage": 30, "note": "Urteil, keine Abfrage"}

    # Erster Lauf: NICHTS ist faellig — sonst kaeme die ganze Liste auf einen
    # Schlag, und eine Meldung mit zwoelf Punkten wird einmal ueberflogen.
    Path(os.environ["VERSION_MONITOR_SEEN"]).unlink(missing_ok=True)
    assert not _lauf([eintrag]), "der ERSTE Lauf meldet bereits — Startpunkt fehlt"

    # ... aber er merkt sich den Startpunkt.
    seen = json.loads(Path(os.environ["VERSION_MONITOR_SEEN"]).read_text())
    assert "verfahren-x" in seen, "der Startpunkt wurde nicht gemerkt"

    # Frist abgelaufen -> meldet sich von selbst, OHNE dass es sonst etwas gibt.
    alt = (datetime.now() - timedelta(days=45)).isoformat(timespec="seconds")
    Path(os.environ["VERSION_MONITOR_SEEN"]).write_text(
        json.dumps({"verfahren-x": alt}), encoding="utf-8")
    txt = _lauf([eintrag])
    assert "verfahren-x" in txt and "45 Tagen" in txt, \
        f"die abgelaufene Frist meldet sich nicht: {txt[:200]}"

    # Und danach ist Ruhe — eine Erinnerung, die jede Woche wiederkommt, wird
    # nicht gelesen, sondern abgeschaltet.
    assert not _lauf([eintrag]), "die Meldung wiederholt sich im naechsten Lauf"


check("unbekannte Art wird GEMELDET, nicht übersprungen (Befund A)",
      _unbekannte_art_wird_gemeldet)
check("weggebrochene Quelle wird gemeldet (Befund D)",
      _weggebrochene_quelle_wird_gemeldet)
check("gesunde Lage schweigt", _gesunde_lage_schweigt)
check("Update wird gemeldet, Major markiert", _update_wird_gemeldet_major_markiert)
check("kein Modell-Aufruf, keine Installation", _kein_modell_und_keine_installation)
check("Fingerabdruck/apt: Vergleich auf Ungleichheit, nicht Groesse",
      _fingerabdruck_statt_nummer)
check("Fingerabdruck wird in der Meldung gekuerzt", _fingerabdruck_wird_gekuerzt)
check("manual meldet sich nach Fristablauf VON SELBST",
      _manual_meldet_sich_nach_frist_von_selbst)

print()
if fails:
    print(f"❌ {len(fails)} Monitor-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Versions-Monitor-Tests bestanden.")
