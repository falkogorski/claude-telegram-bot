#!/opt/homebrew/bin/python3
# <!-- ROLLE: mac-videoarbeiter -->
"""Der Mac als Videoarbeiter — Block 7, erster Schnitt: nur der Weg (26.09.2026).

Läuft per launchd alle 30 Minuten und beim Anmelden (Engywuck 25.09.: launchd
statt Sitzungsstart, weil kein iCloud im Spiel ist). Kein Modellaufruf.

Ein Lauf:
  1. Sperre nehmen (ein Lauf zur Zeit), Lebenszeichen schreiben.
  2. Aufträge holen — mit dem Schlüssel, der auf dem Server **nur lesen** darf
     (`rrsync -ro ~/mac-auftraege`), und nur `*.json` der obersten Ebene bis
     64 KB.
  3. Jeden neuen Auftrag prüfen: nur reguläre Dateien, Kennung gegen ein
     festes Muster (nur ASCII), Größe, Art gegen die Positivliste. Unbekanntes
     wird **abgelehnt und quittiert, nie ausgeführt**. Aus einem Auftrag wird
     nichts als Befehl zusammengesetzt.
  4. Quittungen bringen — mit dem Schlüssel, der **nur schreiben** darf
     (`rrsync -munge -wo ~/mac-ergebnisse`): erst `geholt.json`, zuletzt
     `fertig.json`. Erst mit `fertig.json` gilt ein Ergebnis als vollständig.

**Nur der eigene Schlüssel** `[BERICHTIGT 26.09., Widerlegungsprüfung S2]`:
Getragen wird das von `-o IdentityFile=…` zusammen mit `IdentitiesOnly=yes`
und `IdentityAgent=none`. `-F /dev/null` hält den Eintrag `claudebot` aus
`~/.ssh/config` heraus. Die erste Fassung verließ sich auf `-i`: Fehlt die
Datei, verwirft ssh den Schalter und fällt auf die Standardschlüssel zurück,
darunter den vollen `id_ed25519` — gemessen. Mit `IdentityFile` bleibt es bei
genau dieser Datei.

**Warum rsync aus Homebrew:** `openrsync` (macOS) schickt immer `--dirs`, und
`rrsync` lehnt das ab — am 26.09. auf dem Server gemessen.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

ARTEN = ("probe",)                     # Positivliste — der zweite Schnitt erweitert sie
# Nur ASCII-Ziffern, ganzer Name (K1: `\d` traf auch arabische Ziffern, `$`
# einen Zeilenumbruch am Ende).
KENNUNG = re.compile(r"[0-9]{8}T[0-9]{6}-[0-9a-f]{6}", re.ASCII)
GROESSE_MAX = 64 * 1024                # ein Auftrag ist ein kleines JSON (S5)
AUFHEBEN_TAGE = 30                     # erledigt-Marker, danach geraeumt (K5)
PROTOKOLL_MAX = 1_000_000              # Bytes; darueber wird gekuerzt (K5)
HEIM = Path(os.environ.get("VIDEOARBEITER_HEIM") or Path.home() / "VPS-Auftraege")
RSYNC = os.environ.get("VIDEOARBEITER_RSYNC") or "/opt/homebrew/bin/rsync"
SSH = os.environ.get("VIDEOARBEITER_SSH") or "/usr/bin/ssh"
SCHLUESSEL = Path(os.environ.get("VIDEOARBEITER_SCHLUESSEL") or Path.home() / ".ssh")
HOST_EINTRAG = os.environ.get("VIDEOARBEITER_HOST") or "claudebot"
PROTOKOLL = os.environ.get("VIDEOARBEITER_PROTOKOLL") or str(
    Path.home() / "Library" / "Logs" / "videoarbeiter.log")


def sag(text: str) -> None:
    print(time.strftime("%Y-%m-%d %H:%M:%S"), text, flush=True)


def kennung_gueltig(name: str) -> bool:
    return KENNUNG.fullmatch(name) is not None


def ziel() -> tuple[str, str, str, str]:
    """(Benutzer, Rechner, Port, Bekannte-Rechner-Datei) aus dem SSH-Eintrag.

    Nur diese vier Werte werden übernommen — nie der Schlüssel des Eintrags.
    """
    aus = subprocess.run([SSH, "-G", HOST_EINTRAG], capture_output=True,
                         text=True, timeout=20).stdout
    werte: dict[str, str] = {}
    for zeile in aus.splitlines():
        k, _, v = zeile.partition(" ")
        werte.setdefault(k.lower(), v.strip())
    # `ssh -G` nennt mehrere Dateien; die erste genuegt (dort steht der Server).
    bekannte = (werte.get("userknownhostsfile", "").split() or [""])[0]
    if bekannte.startswith("~/"):
        bekannte = str(Path.home() / bekannte[2:])
    return (werte.get("user", "claudebot"), werte.get("hostname", HOST_EINTRAG),
            werte.get("port", "22"), bekannte)


def ssh_befehl(schluessel: Path, port: str, bekannte: str) -> list[str]:
    befehl = [SSH, "-F", "/dev/null",
              "-o", f"IdentityFile={schluessel}", "-o", "IdentitiesOnly=yes",
              "-o", "IdentityAgent=none", "-o", "BatchMode=yes",
              "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=15",
              "-o", "ServerAliveCountMax=2", "-p", port]
    if bekannte:
        befehl += ["-o", f"UserKnownHostsFile={bekannte}"]
    return befehl


def rsync(ssh: list[str], quelle: str, ziel_pfad: str, *, holen: bool) -> bool:
    # rsync zerlegt `-e` an Leerzeichen und versteht einfache Anfuehrungs-
    # zeichen; jeder Teil wird deshalb einzeln gequotet (K6).
    befehl = [RSYNC, "-rt", "--timeout=60", "-e", " ".join(shlex.quote(t) for t in ssh)]
    if holen:
        # Nur Auftraege der obersten Ebene, klein, nie ein halber (.teil-…):
        # Unterordner, fremde Dateien und Riesen bleiben auf dem Server (S5, S6).
        befehl += ["--include=[0-9]*.json", "--exclude=*", f"--max-size={GROESSE_MAX}"]
    befehl += [quelle, ziel_pfad]
    try:
        lauf = subprocess.run(befehl, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        sag(f"rsync {'holen' if holen else 'bringen'}: Zeitgrenze ueberschritten")
        return False
    if lauf.returncode != 0:
        sag(f"rsync {'holen' if holen else 'bringen'} rc={lauf.returncode}: "
            f"{lauf.stderr.strip()[-200:]}")
    return lauf.returncode == 0


def pruefen(datei: Path) -> tuple[dict | None, str]:
    """(Auftrag, '') wenn ausführbar, sonst (None, Grund). Liest nur, führt nichts aus."""
    if not kennung_gueltig(datei.stem):
        return None, "Kennung passt nicht zum Muster"
    if datei.is_symlink() or not datei.is_file():
        return None, "keine regulaere Datei"
    if datei.stat().st_size > GROESSE_MAX:
        return None, "Auftrag zu gross"
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


def weg(pfad: Path) -> None:
    """Einen Eintrag im Eingang entfernen — auch einen Ordner oder Link (S1)."""
    import shutil
    try:
        if pfad.is_dir() and not pfad.is_symlink():
            shutil.rmtree(pfad)
        else:
            pfad.unlink(missing_ok=True)
    except OSError as e:
        sag(f"nicht entfernbar: {pfad.name[:60]!r} ({e})")


def aufraeumen(erledigt: Path) -> None:
    grenze = time.time() - AUFHEBEN_TAGE * 86400
    for m in erledigt.iterdir():
        try:
            if m.lstat().st_mtime < grenze:
                m.unlink()
        except OSError:
            pass
    try:
        p = Path(PROTOKOLL)
        if p.is_file() and p.stat().st_size > PROTOKOLL_MAX:
            p.write_bytes(p.read_bytes()[-PROTOKOLL_MAX // 2:])
    except OSError:
        pass


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
    # Ein Lauf zur Zeit (K4): Handaufruf und Zeitgeber teilen sich sonst Ordner
    # und die rrsync-Sperre des Servers.
    sperre = open(HEIM / ".sperre", "w")
    try:
        fcntl.flock(sperre, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        sag("ein anderer Lauf ist noch aktiv — dieser endet")
        return 0
    aufraeumen(erledigt)
    benutzer, rechner, port, bekannte = ziel()
    entfernt = f"{benutzer}@{rechner}:./"
    ssh_holen = ssh_befehl(holen_key, port, bekannte)
    ssh_bringen = ssh_befehl(bringen_key, port, bekannte)

    (ausgang / ".mac-zuletzt").write_text(time.strftime("%Y-%m-%dT%H:%M:%S") + "\n")
    if not rsync(ssh_holen, entfernt, f"{eingang}/", holen=True):
        rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False)   # wenigstens das Lebenszeichen
        return 1

    neu: list[tuple[str, dict | None, str]] = []
    for datei in sorted(eingang.iterdir()):
        name = datei.name
        try:
            stamm = name[:-5] if name.endswith(".json") else name
            if not name.endswith(".json") or not kennung_gueltig(stamm):
                # Ohne gueltige Kennung gibt es keinen sicheren Ordnernamen
                # fuer eine Quittung — protokollieren und entfernen. Der Server
                # meldet solche Eintraege selbst (S6).
                sag(f"abgelehnt ohne Quittung: {name[:60]!r}")
                weg(datei)
                continue
            if (erledigt / stamm).exists():
                weg(datei)           # schon bearbeitet, der Server raeumt noch
                continue
            daten, grund = pruefen(datei)
            if not (ausgang / stamm / "geholt.json").exists():
                schreiben(ausgang / stamm / "geholt.json",
                          {"kennung": stamm, "geholt": time.strftime("%Y-%m-%dT%H:%M:%S")})
            neu.append((stamm, daten, grund))
        except Exception as e:  # ein kaputter Eintrag nimmt die anderen nicht mit (S1)
            sag(f"Eintrag {name[:60]!r} uebersprungen: {type(e).__name__}: {e}")
            weg(datei)
    if neu and not rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False):
        return 1

    for stamm, daten, grund in neu:
        fertig = ausgang / stamm / "fertig.json"
        if fertig.exists():
            # Schon ausgefuehrt, nur das Bringen scheiterte zuletzt (S4) —
            # nicht noch einmal ausfuehren.
            continue
        if daten is None:
            ergebnis = {"abgelehnt": grund}
            sag(f"abgelehnt: {stamm} ({grund})")
        else:
            ergebnis = ausfuehren(daten)
            sag(f"erledigt: {stamm} ({daten['art']})")
        ergebnis.update({"kennung": stamm, "erledigt": time.strftime("%Y-%m-%dT%H:%M:%S")})
        schreiben(fertig, ergebnis)   # zuletzt: die Quittung

    if not rsync(ssh_bringen, f"{ausgang}/", entfernt, holen=False):
        return 1
    for stamm, _d, _g in neu:
        (erledigt / stamm).touch()
        weg(eingang / f"{stamm}.json")
        weg(ausgang / stamm)
    if neu:
        sag(f"{len(neu)} Auftrag/Auftraege quittiert")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(lauf())
    except Exception as e:  # launchd sieht nur den Rueckgabewert; das Protokoll den Grund
        sag(f"Lauf abgebrochen: {type(e).__name__}: {e}")
        sys.exit(1)
