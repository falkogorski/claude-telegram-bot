#!/opt/homebrew/bin/python3
# <!-- ROLLE: mac-videoarbeiter -->
"""Der Mac als Videoarbeiter — Block 7, erster Schnitt: nur der Weg (26.09.2026).

Läuft per launchd alle 30 Minuten und beim Anmelden (Engywuck 25.09.: launchd
statt Sitzungsstart, weil kein iCloud im Spiel ist). Kein Modellaufruf.

Ein Lauf:
  1. Lebenszeichen schreiben.
  2. Aufträge holen — mit dem Schlüssel, der auf dem Server **nur lesen** darf
     (`rrsync -ro ~/mac-auftraege`).
  3. Jeden neuen Auftrag prüfen: Kennung gegen ein festes Muster, Art gegen
     die Positivliste. Unbekanntes wird **abgelehnt und quittiert, nie
     ausgeführt**. Aus einem Auftrag wird nichts als Befehl zusammengesetzt.
  4. Quittungen bringen — mit dem Schlüssel, der **nur schreiben** darf
     (`rrsync -wo ~/mac-ergebnisse`): erst `geholt.json`, zuletzt
     `fertig.json`. Erst mit `fertig.json` gilt ein Ergebnis als vollständig.

**Warum `-F /dev/null`:** Der Eintrag `claudebot` in `~/.ssh/config` bietet den
vollen Schlüssel an. Hinge dieser Lauf daran, fiele er ohne eingerichteten
Spezialschlüssel still auf den vollen Zugang zurück — und alles sähe aus, als
funktioniere es. So bietet er nur seine eigenen Schlüssel an und scheitert
ehrlich, wenn sie fehlen.

**Warum rsync aus Homebrew:** `openrsync` (macOS) schickt immer `--dirs`, und
`rrsync` lehnt das ab — am 26.09. auf dem Server gemessen.
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

ARTEN = ("probe",)                     # Positivliste — der zweite Schnitt erweitert sie
KENNUNG = re.compile(r"^\d{8}T\d{6}-[0-9a-f]{6}$")
HEIM = Path(os.environ.get("VIDEOARBEITER_HEIM") or Path.home() / "VPS-Auftraege")
RSYNC = os.environ.get("VIDEOARBEITER_RSYNC") or "/opt/homebrew/bin/rsync"
SSH = os.environ.get("VIDEOARBEITER_SSH") or "/usr/bin/ssh"
SCHLUESSEL = Path(os.environ.get("VIDEOARBEITER_SCHLUESSEL") or Path.home() / ".ssh")
HOST_EINTRAG = os.environ.get("VIDEOARBEITER_HOST") or "claudebot"


def sag(text: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), text, flush=True)


def ziel() -> tuple[str, str, str, str]:
    """(Benutzer, Rechner, Port, Bekannte-Rechner-Dateien) aus dem SSH-Eintrag.

    Nur diese vier Werte werden übernommen — nie der Schlüssel des Eintrags.
    """
    aus = subprocess.run([SSH, "-G", HOST_EINTRAG], capture_output=True,
                         text=True, timeout=20).stdout
    werte = {}
    for zeile in aus.splitlines():
        k, _, v = zeile.partition(" ")
        werte.setdefault(k.lower(), v.strip())
    return (werte.get("user", "claudebot"), werte.get("hostname", HOST_EINTRAG),
            werte.get("port", "22"), werte.get("userknownhostsfile", ""))


def ssh_befehl(schluessel: Path, port: str, bekannte: str) -> list[str]:
    befehl = [SSH, "-F", "/dev/null", "-i", str(schluessel),
              "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
              "-o", "ConnectTimeout=20", "-p", port]
    if bekannte:
        # `ssh -G` nennt mehrere Dateien, durch Leerzeichen getrennt; rsync
        # zerlegt `-e` an Leerzeichen. Die erste Datei genuegt (dort steht der
        # Server, gemessen am 26.09.).
        befehl += ["-o", f"UserKnownHostsFile={bekannte.split()[0]}"]
    return befehl


def rsync(ssh: list[str], quelle: str, ziel_pfad: str, *, holen: bool) -> bool:
    # Die ssh-Angabe geht als EIN Argument an rsync; sie enthaelt nur Pfade
    # und feste Schalter, nichts aus einem Auftrag.
    befehl = [RSYNC, "-rt", "-e", " ".join(ssh)]
    if holen:
        befehl += ["--exclude", ".*"]   # nie einen halben Auftrag (.teil-…)
    befehl += [quelle, ziel_pfad]
    lauf = subprocess.run(befehl, capture_output=True, text=True, timeout=600)
    if lauf.returncode != 0:
        sag(f"rsync {'holen' if holen else 'bringen'} rc={lauf.returncode}: "
            f"{lauf.stderr.strip()[-200:]}")
    return lauf.returncode == 0


def pruefen(datei: Path) -> tuple[dict | None, str]:
    """(Auftrag, '') wenn ausführbar, sonst (None, Grund). Liest nur, führt nichts aus."""
    if not KENNUNG.match(datei.stem):
        return None, "Kennung passt nicht zum Muster"
    try:
        daten = json.loads(datei.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, "kein lesbares JSON"
    if not isinstance(daten, dict) or daten.get("kennung") != datei.stem:
        return None, "Kennung im Auftrag weicht vom Dateinamen ab"
    if daten.get("art") not in ARTEN:
        return None, "Art nicht in der Positivliste"
    return daten, ""


def ausfuehren(daten: dict) -> dict:
    # Im ersten Schnitt die einzige Art. Sie beweist den Weg, sonst nichts.
    return {"art": "probe", "rechner": socket.gethostname().split(".")[0]}


def schreiben(pfad: Path, daten: dict) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    teil = pfad.with_name(f".teil-{pfad.name}")
    teil.write_text(json.dumps(daten, ensure_ascii=False), encoding="utf-8")
    os.replace(teil, pfad)


def lauf() -> int:
    eingang, ausgang, erledigt = HEIM / "eingang", HEIM / "ausgang", HEIM / "erledigt"
    for d in (eingang, ausgang, erledigt):
        d.mkdir(parents=True, exist_ok=True)
    holen_key, bringen_key = SCHLUESSEL / "videoarbeiter_holen", SCHLUESSEL / "videoarbeiter_bringen"
    if not holen_key.is_file() or not bringen_key.is_file():
        sag("nicht eingerichtet: Schluessel fehlen — scripts/mac/videoarbeiter_einrichten.sh")
        return 78
    if not Path(RSYNC).is_file():
        sag(f"rsync fehlt unter {RSYNC} (brew install rsync) — openrsync traegt rrsync nicht")
        return 78
    benutzer, rechner, port, bekannte = ziel()
    entfernt = f"{benutzer}@{rechner}:./"
    ssh_holen = ssh_befehl(holen_key, port, bekannte)
    ssh_bringen = ssh_befehl(bringen_key, port, bekannte)

    (ausgang / ".mac-zuletzt").write_text(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
    if not rsync(ssh_holen, entfernt, f"{eingang}/", holen=True):
        rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False)   # wenigstens das Lebenszeichen
        return 1

    neu: list[tuple[Path, dict | None, str]] = []
    for datei in sorted(eingang.glob("*.json")):
        if (erledigt / datei.stem).exists():
            datei.unlink(missing_ok=True)     # schon bearbeitet, der Server raeumt noch
            continue
        daten, grund = pruefen(datei)
        if not KENNUNG.match(datei.stem):
            # Ohne gueltige Kennung gibt es keinen sicheren Ordnernamen fuer eine
            # Quittung — nur protokollieren und liegen lassen.
            sag(f"abgelehnt ohne Quittung: {datei.name[:60]!r} ({grund})")
            datei.unlink(missing_ok=True)
            continue
        schreiben(ausgang / datei.stem / "geholt.json",
                  {"kennung": datei.stem, "geholt": time.strftime("%Y-%m-%dT%H:%M:%S")})
        neu.append((datei, daten, grund))
    if neu and not rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False):
        return 1

    for datei, daten, grund in neu:
        if daten is None:
            ergebnis = {"abgelehnt": grund}
            sag(f"abgelehnt: {datei.stem} ({grund})")
        else:
            ergebnis = ausfuehren(daten)
            sag(f"erledigt: {datei.stem} ({daten['art']})")
        ergebnis.update({"kennung": datei.stem, "erledigt": time.strftime("%Y-%m-%dT%H:%M:%S")})
        schreiben(ausgang / datei.stem / "fertig.json", ergebnis)   # zuletzt: die Quittung

    if not rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False):
        return 1
    for datei, _d, _g in neu:
        (erledigt / datei.stem).touch()
        datei.unlink(missing_ok=True)
        for f in sorted((ausgang / datei.stem).glob("*"), reverse=True):
            f.unlink(missing_ok=True)
        (ausgang / datei.stem).rmdir()
    if neu:
        sag(f"{len(neu)} Auftrag/Auftraege quittiert")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(lauf())
    except Exception as e:  # launchd sieht nur den Rueckgabewert; das Protokoll den Grund
        sag(f"Lauf abgebrochen: {type(e).__name__}: {e}")
        sys.exit(1)
