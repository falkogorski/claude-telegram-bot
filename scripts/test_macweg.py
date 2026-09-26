#!/usr/bin/env python3
# <!-- ROLLE: test-macweg -->
"""Block 7, erster Schnitt: der Weg VPS → Mac → VPS — **ausgeführt** (26.09.2026).

Echter Code in der Mitte (`macauftrag.py`, `scripts/mac/videoarbeiter.py`, der
Tagescheck-Abschnitt 9r). Am Rand: `ssh` und `rsync` als Attrappen, die sich
wie `rrsync` auf dem Server verhalten — der Holschlüssel darf nur lesen, der
Bringschlüssel nur schreiben, und **ein Aufruf ohne `-F /dev/null` fällt
durch**: Er hätte den vollen Schlüssel aus `~/.ssh/config` mit angeboten.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
_TMP = Path(tempfile.mkdtemp(prefix="macweg-"))
SERVER_A, SERVER_E = _TMP / "srv" / "mac-auftraege", _TMP / "srv" / "mac-ergebnisse"
os.environ["MAC_AUFTRAEGE"] = str(SERVER_A)
os.environ["MAC_ERGEBNISSE"] = str(SERVER_E)
import macauftrag                                               # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


# ── Der Rand ────────────────────────────────────────────────────────────────
BIN = _TMP / "bin"
BIN.mkdir()
SCHL = _TMP / "ssh"
SCHL.mkdir()
(BIN / "ssh").write_text(
    "#!/bin/bash\n"
    'if [ "$1" = "-G" ]; then printf "user claudebot\\nhostname pruefserver\\nport 22\\n'
    'userknownhostsfile /x/kh /x/kh2\\nidentityfile ~/.ssh/id_ed25519\\n"; exit 0; fi\n'
    "exit 1\n")
(BIN / "rsync").write_text(f"""#!{sys.executable}
import sys, shutil, pathlib, fnmatch
a = sys.argv[1:]
e = a[a.index("-e") + 1]
open("{_TMP}/rsync.log", "a").write(" ".join(a) + "\\n")
if "-F /dev/null" not in e or "IdentitiesOnly=yes" not in e:
    print("voller Schluessel angeboten", file=sys.stderr); sys.exit(99)
teile = e.split()
schluessel = teile[teile.index("-i") + 1]
quelle, ziel = a[-2], a[-1]
entfernt_quelle = ":" in quelle
if schluessel.endswith("videoarbeiter_holen"):
    if not entfernt_quelle:
        print("rrsync: sending to read-only server is not allowed", file=sys.stderr); sys.exit(1)
    src = pathlib.Path("{SERVER_A}")
    for f in src.glob("*"):
        if f.is_file() and not f.name.startswith("."):
            shutil.copy2(f, pathlib.Path(ziel) / f.name)
elif schluessel.endswith("videoarbeiter_bringen"):
    if entfernt_quelle:
        print("rrsync: reading from write-only server is not allowed", file=sys.stderr); sys.exit(1)
    shutil.copytree(quelle, "{SERVER_E}", dirs_exist_ok=True)
else:
    sys.exit(98)
""")
for b in ("ssh", "rsync"):
    (BIN / b).chmod(0o755)

HEIM = _TMP / "mac"
UMGEBUNG = {**os.environ, "VIDEOARBEITER_HEIM": str(HEIM),
            "VIDEOARBEITER_RSYNC": str(BIN / "rsync"), "VIDEOARBEITER_SSH": str(BIN / "ssh"),
            "VIDEOARBEITER_SCHLUESSEL": str(SCHL)}


def mac_lauf() -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(WURZEL / "scripts" / "mac" / "videoarbeiter.py")],
                       capture_output=True, text=True, env=UMGEBUNG, timeout=60)
    return r.returncode, r.stdout + r.stderr


def zuruecksetzen():
    for d in (SERVER_A.parent, HEIM):
        shutil.rmtree(d, ignore_errors=True)
    for k in SCHL.glob("*"):
        k.unlink()
    (_TMP / "rsync.log").unlink(missing_ok=True)


def schluessel_da():
    for n in ("videoarbeiter_holen", "videoarbeiter_bringen"):
        (SCHL / n).write_text("attrappe")


# ── 1. Ablegen ──────────────────────────────────────────────────────────────
print("== 1. Auftrag ablegen (Server) ==")
zuruecksetzen()
st = macauftrag.stand()
zeile("ohne Auftragsordner: nur eine Protokollzeile, kein Alarm",
      st and all(a == "ok" for a, _ in st) and "nicht eingerichtet" in st[0][1], gemessen=str(st))
k = macauftrag.ablegen("probe")
zeile("Probeauftrag liegt mit gueltiger Kennung, kein halber Rest",
      (SERVER_A / f"{k}.json").is_file() and macauftrag.KENNUNG.match(k)
      and not list(SERVER_A.glob(".teil-*")), gemessen=k)
try:
    macauftrag.ablegen("shell")
    zeile("unbekannte Art wird gar nicht erst abgelegt", False)
except ValueError:
    zeile("unbekannte Art wird gar nicht erst abgelegt", True)

# ── 2. Ohne Schluessel ──────────────────────────────────────────────────────
print("== 2. Nicht eingerichtet ==")
rc, aus = mac_lauf()
zeile("ohne eigene Schluessel: ehrlicher Abbruch, kein rsync-Aufruf",
      rc == 78 and "nicht eingerichtet" in aus and not (_TMP / "rsync.log").exists(),
      gemessen=f"rc={rc} {aus[-120:]!r}")

# ── 3. Hin und zurueck ──────────────────────────────────────────────────────
print("== 3. Hin und zurück ==")
schluessel_da()
rc, aus = mac_lauf()
fertig = SERVER_E / k / "fertig.json"
daten = json.loads(fertig.read_text()) if fertig.is_file() else {}
zeile("Probeauftrag kommt mit Quittung zurueck", rc == 0 and daten.get("art") == "probe"
      and daten.get("kennung") == k and (SERVER_E / k / "geholt.json").is_file(),
      gemessen=f"rc={rc} {daten} {aus[-200:]!r}")
zeile("Lebenszeichen liegt beim Server", (SERVER_E / ".mac-zuletzt").is_file())
log = (_TMP / "rsync.log").read_text() if (_TMP / "rsync.log").exists() else ""
zeile("jeder Aufruf bietet nur den eigenen Schluessel an (-F /dev/null)",
      log and all("-F /dev/null" in z for z in log.splitlines()), gemessen=log[-200:])
zeile("kein halber Auftrag wird geholt (Punkt-Dateien ausgeschlossen)",
      all("--exclude .*" in z for z in log.splitlines() if "videoarbeiter_holen" in z))
rc2, aus2 = mac_lauf()
zeile("ein schon bearbeiteter Auftrag wird nicht noch einmal ausgefuehrt",
      rc2 == 0 and "erledigt:" not in aus2, gemessen=aus2[-160:])
st = macauftrag.stand()
zeile("der Server raeumt den quittierten Auftrag weg (der Mac darf nicht)",
      not (SERVER_A / f"{k}.json").exists()
      and any("zurueckgekommen" in t for _, t in st), gemessen=str(st))

# ── 4. Positivliste und Muster ──────────────────────────────────────────────
print("== 4. Positivliste ==")
fremd = macauftrag.neue_kennung()
(SERVER_A / f"{fremd}.json").write_text(json.dumps(
    {"kennung": fremd, "art": "shell", "befehl": "touch " + str(_TMP / "AUSGEFUEHRT")}))
falsch = macauftrag.neue_kennung()
(SERVER_A / f"{falsch}.json").write_text(json.dumps({"kennung": "anders", "art": "probe"}))
(SERVER_A / "boese; touch x.json").write_text("{}")
rc, aus = mac_lauf()
q_fremd = json.loads((SERVER_E / fremd / "fertig.json").read_text()) \
    if (SERVER_E / fremd / "fertig.json").is_file() else {}
q_falsch = json.loads((SERVER_E / falsch / "fertig.json").read_text()) \
    if (SERVER_E / falsch / "fertig.json").is_file() else {}
zeile("unbekannte Art: abgelehnt und quittiert, nie ausgefuehrt",
      "Positivliste" in q_fremd.get("abgelehnt", "") and "rechner" not in q_fremd
      and not (_TMP / "AUSGEFUEHRT").exists(), gemessen=str(q_fremd))
zeile("Kennung im Auftrag weicht vom Namen ab: abgelehnt",
      "weicht" in q_falsch.get("abgelehnt", ""), gemessen=str(q_falsch))
_namen = [p.name for p in SERVER_E.iterdir()] if SERVER_E.is_dir() else []
zeile("Dateiname ausserhalb des Musters: keine Quittung, kein Ordner, kein Absturz",
      rc == 0 and _namen and not any("boese" in n for n in _namen),
      gemessen=f"rc={rc} {_namen}")

# ── 5. Wer merkt es ─────────────────────────────────────────────────────────
print("== 5. Wer merkt es (24 Stunden) ==")
zuruecksetzen()
alt = macauftrag.ablegen("probe")
jetzt = time.time()
os.utime(SERVER_A / f"{alt}.json", (jetzt - 25 * 3600, jetzt - 25 * 3600))
st = macauftrag.stand(jetzt)
rot = [t for a, t in st if a == "rot"]
zeile("25 Stunden ungeholt: an Adam, mit dem letzten Lebenszeichen",
      len(rot) == 1 and "ungeholt" in rot[0] and "noch nie" in rot[0], gemessen=str(st))
(SERVER_E / alt).mkdir(parents=True)
(SERVER_E / alt / "geholt.json").write_text("{}")
st = macauftrag.stand(jetzt)
rot = [t for a, t in st if a == "rot"]
zeile("geholt, aber 25 Stunden ohne Quittung: an Adam",
      len(rot) == 1 and "nicht zurueckgekommen" in rot[0], gemessen=str(st))
frisch = macauftrag.ablegen("probe")
os.utime(SERVER_A / f"{alt}.json", None)
st = macauftrag.stand()
zeile("frische Auftraege sind kein Alarm", not [t for a, t in st if a == "rot"],
      gemessen=str(st))

# ── 6. Tagescheck 9r ────────────────────────────────────────────────────────
print("== 6. Tagescheck 9r ==")
import re                                                       # noqa: E402
_dc = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
_m = re.search(r"# >>> MACWEG\n(.*?)# <<< MACWEG", _dc, re.S)
_abschnitt = _m.group(1) if _m else ""
zeile("Tagescheck 9r ist markiert und ruft macauftrag.py --stand",
      "macauftrag.py" in _abschnitt and "--stand" in _abschnitt)


def _tagescheck() -> str:
    vorspann = ('set -uo pipefail\n'
                'add() { echo "ADD:$1"; }\nintern() { echo "INTERN:$1"; }\n'
                'red() { echo "RED:$1"; }\n'
                f'BOTDIR="{WURZEL}"\nVENVPY="{sys.executable}"\n'
                f'BOTENV=(env MAC_AUFTRAEGE="{SERVER_A}" MAC_ERGEBNISSE="{SERVER_E}")\n')
    return subprocess.run(["bash", "-c", vorspann + _abschnitt],
                          capture_output=True, text=True).stdout


os.utime(SERVER_A / f"{alt}.json", (jetzt - 25 * 3600, jetzt - 25 * 3600))
_a = _tagescheck()
zeile("Tagescheck 9r: haengender Auftrag geht rot an Adam",
      "RED:Mac-Auftrag" in _a and "nicht zurueckgekommen" in _a, gemessen=_a[-200:])
zeile("Tagescheck 9r: dazu die Protokollzeile mit dem Stand", "ADD:🖥️ Mac-Weg:" in _a,
      gemessen=_a[-200:])
zuruecksetzen()
_a = _tagescheck()
zeile("Tagescheck 9r: nicht eingerichtet ist kein Alarm",
      "RED:" not in _a and "INTERN:" not in _a and "nicht eingerichtet" in _a, gemessen=_a)

# ── 7. Einrichtung ──────────────────────────────────────────────────────────
print("== 7. Einrichtung ==")
e = WURZEL / "scripts" / "mac" / "videoarbeiter_einrichten.sh"
r = subprocess.run(["bash", "-n", str(e)], capture_output=True, text=True)
zeile("Einrichtungs-Skript ist gueltiges bash", r.returncode == 0, gemessen=r.stderr)
text = e.read_text(encoding="utf-8")
# Reihenfolge ist hier die Sicherung: scharf erst NACH bestandener Probe.
pos_probe = text.find("zurueckgekommen")
pos_scharf = text.find("launchctl bootstrap")
zeile("scharfgestellt wird erst nach dem bestandenen Probeauftrag",
      0 < pos_probe < pos_scharf, gemessen=f"{pos_probe} / {pos_scharf}")

shutil.rmtree(_TMP, ignore_errors=True)
print(f"== Ergebnis: {zeilen - len(fehler)}/{zeilen} ==")
sys.exit(1 if fehler else 0)
