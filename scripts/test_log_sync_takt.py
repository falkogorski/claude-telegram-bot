#!/usr/bin/env python3
# <!-- ROLLE: test-log-sync-takt -->
"""Der Log-Abgleich unter dem neuen Takt: Schloss, Quittungs-Ort, `-prune`.

**Ausgeführt, nicht gelesen.** Das Skript läuft hier wirklich — gegen eine
Wegwerf-Umgebung aus `LOG_SYNC_SRC`, `LOG_SYNC_REPO`, `LOG_SYNC_WORK` und
`LOG_SYNC_LOCK`. Ein Textscan über `log_sync.sh` könnte nur zeigen, dass die
Wörter dastehen; gemessen werden soll, was danach im Arbeitsordner liegt und
ob ein zweiter Lauf zurücktritt.

**Warum es diesen Prüfer gibt:** Seit dem 11.09. stoßen Minutentakt **und**
Pfad-Einheit an, und ein Lauf dauert rund 32 Sekunden. Beides zusammen erzeugt
genau die zwei Fehler, die hier gemessen werden — überlappende Läufe und eine
Tempdatei, die den nächsten Lauf weckt.
"""
import fcntl
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_WURZEL = Path(__file__).resolve().parent.parent
SKRIPT = REPO_WURZEL / "scripts/log_sync.sh"

fehler: list[str] = []
uebersprungen: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


def nicht_gemessen(name: str, grund: str) -> None:
    """**Übersprungen ist nicht bestanden** (A1-Regel, 30.08.).

    Eine Zeile, die grün meldet, ohne gemessen zu haben, ist schlimmer als
    keine: Sie beruhigt genau dort, wo niemand hinsieht. Sie zählt deshalb
    weder als bestanden noch als Fehler — sie steht als eigene Zahl da.
    """
    global zeilen
    zeilen += 1
    uebersprungen.append(name)
    print(f"  ⏭️  {name} — NICHT GEMESSEN: {grund}")


print("== Log-Abgleich unter dem neuen Takt ==")

if not shutil.which("rsync"):
    print("  ⏭️  rsync fehlt — NICHT GEMESSEN (77)")
    sys.exit(77)


def baue_umgebung() -> tuple:
    """Wegwerf-Umgebung: Quelle, Log-Repo-Klon, Arbeitsordner mit Attrappen-venv."""
    tmp = Path(tempfile.mkdtemp(prefix="logtakt-"))
    src = tmp / "conversations"
    src.mkdir()
    (src / "2026-09-11.md").write_text("Testlog\n", encoding="utf-8")

    repo = tmp / "logrepo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

    work = tmp / "workspace"
    work.mkdir()
    (work / "papier.md").write_text("Inhalt\n", encoding="utf-8")
    # Attrappen-venv mit vielen Dateien: genau der Baum, den `find` bisher
    # vollstaendig durchlief.
    venv = work / ".venv" / "lib" / "site-packages" / "irgendwas"
    venv.mkdir(parents=True)
    for i in range(60):
        (venv / f"modul{i}.py").write_text("x\n", encoding="utf-8")
    # Und die GESCHWISTER des Punkt-Ordners, je mit einer Dokument-Endung:
    # genau die Form, die bis zum 11.09. ins Log-Repo wanderte.
    (work / "echt.md").write_text("echt\n", encoding="utf-8")
    for ordner in ("node_modules/paket", "venv/lib", ".venv/lib"):
        d = work / ordner
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text("fremd\n", encoding="utf-8")

    umg = dict(os.environ)
    umg.update({
        "HOME": str(tmp),
        "LOG_SYNC_SRC": str(src),
        "LOG_SYNC_REPO": str(repo),
        "LOG_SYNC_WORK": str(work),
        "LOG_SYNC_LOCK": str(tmp / "schloss"),
    })
    return tmp, work, umg


def fahre(umg: dict, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SKRIPT)], capture_output=True, text=True,
                          env=umg, timeout=timeout)


TMP, WORK, UMG = baue_umgebung()
lauf1 = fahre(UMG)

# ── 1. Ein Lauf OHNE Aenderung fasst den Arbeitsordner nicht an ──────────────
# **Die erste Fassung dieser Zeile mass den falschen Moment** und ihre
# Gegenprobe blieb gruen: Sie sah nach, was nach dem Lauf im Ordner LIEGT — und
# die alte Tempdatei wurde am Ende ohnehin umbenannt oder geloescht. Der Fehler
# war aber nicht, dass sie liegen bleibt, sondern dass sie ENTSTEHT: Jedes
# Anlegen weckt `claude-log-sync.path`, und der naechste Lauf weckt den
# uebernaechsten.
#
# Gemessen wird deshalb die Zusage selbst: **Ein zweiter Lauf, bei dem sich
# nichts geaendert hat, veraendert das Verzeichnis nicht** — weder Inhalt noch
# Zeitstempel. Genau das entscheidet, ob die Pfad-Einheit wieder feuert.
_vorher_liste = sorted(p.name for p in WORK.iterdir())
_vorher_mtime = WORK.stat().st_mtime
lauf2 = fahre(UMG)
_nachher_liste = sorted(p.name for p in WORK.iterdir())
_nachher_mtime = WORK.stat().st_mtime
zeile("ein Lauf ohne Aenderung fasst den Arbeitsordner nicht an",
      _vorher_liste == _nachher_liste and _vorher_mtime == _nachher_mtime,
      gemessen=f"vorher {_vorher_liste} ({_vorher_mtime}), "
               f"nachher {_nachher_liste} ({_nachher_mtime})")

# ── 2. Ein zweiter Lauf tritt zurueck, statt in denselben Dateien zu wuehlen ─
# Gemessen wird das Verhalten: Das Schloss wird **hier im Pruefer** gehalten
# (`fcntl.flock`, derselbe Systemaufruf, den `flock(1)` im Skript benutzt), und
# das Skript muss zuruecktreten und es SAGEN.
#
# **Kein Unterprozess als Schlosshalter.** Der erste Entwurf startete `flock -x
# … sleep 8` per `Popen` — der Waechter `test_pruefumgebung.py` hat es gemeldet,
# zu Recht: Ein Prozess, der das Testende ueberlebt, kann danach in echte
# Ordner schreiben. Der Dateideskriptor hier stirbt mit dem Pruefer.
if shutil.which("flock"):
    _sperre = open(UMG["LOG_SYNC_LOCK"], "w")
    fcntl.flock(_sperre, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        lauf_parallel = fahre(UMG, timeout=30)
    finally:
        fcntl.flock(_sperre, fcntl.LOCK_UN)
        _sperre.close()
    zeile("ein zweiter Lauf tritt zurueck und sagt es",
          "tritt zurueck" in lauf_parallel.stdout and lauf_parallel.returncode == 0,
          gemessen=f"rc={lauf_parallel.returncode}, "
                   f"Ausgabe: {lauf_parallel.stdout.strip()[:120]!r}")
else:
    # Der Mac hat kein `flock(1)`. Auf dem VPS -- der Zielumgebung, in der der
    # Wettlauf ueberhaupt entsteht -- ist es vorhanden und die Zeile misst.
    nicht_gemessen("ein zweiter Lauf tritt zurueck und sagt es",
                   "flock fehlt auf dieser Maschine (auf dem VPS vorhanden)")

# ── 3. Kein venv-Inhalt in der Quittung ──────────────────────────────────────
# **Ehrlich zur Reichweite:** Diese Zeile misst NICHT das `-prune`. Sie blieb in
# der Gegenprobe gruen, als ich es entfernte — die venv-Dateien enden auf `.py`
# und fallen ohnehin durch den Endungsfilter des Berichts. Was `-prune` zusagt,
# ist **Laufzeit**, und dafuer gibt es keine verhaltensmessende Zeile, die nicht
# flackert; gemessen hat sie Adam auf dem VPS (`real 31,9 s` vorher).
#
# Die Zusage, die HIER gemessen wird, ist trotzdem eine eigene und gilt seit dem
# 20.08.: Der Bericht meldet keinen Paket-Krempel als *„bitte melden"*.
_quittung = (WORK / "letzter-abgleich.txt").read_text(encoding="utf-8")
zeile("kein venv-Inhalt in der Quittung",
      "modul0.py" not in _quittung and "site-packages" not in _quittung,
      gemessen=_quittung[:160].replace("\n", " | "))

# ── 4. Und das Richtige kommt trotzdem an ────────────────────────────────────
# Eine Sparsamkeit, die den Transport mitkuerzt, waere schlimmer als der
# langsame Lauf. Gemessen: das Papier liegt im Log-Repo.
_ziel = Path(UMG["LOG_SYNC_REPO"]) / "ausarbeitungen" / "papier.md"
_log = Path(UMG["LOG_SYNC_REPO"]) / "conversations" / "2026-09-11.md"
zeile("Papier und Gespraechslog sind trotzdem angekommen",
      _ziel.exists() and _log.exists(),
      gemessen=f"papier={_ziel.exists()} log={_log.exists()}")

# ── 5. Fremdes Markdown bleibt draussen, eigenes kommt an ────────────────────
# **Am 11.09. gemessen, bevor es gefixt wurde:** `.venv/lib/README.md` blieb
# draussen (`--exclude='.*'`), **`venv/lib/README.md` und
# `node_modules/paket/README.md` kamen mit** — der Ausschluss hing am Punkt,
# nicht an der Sache. Diese Zeile misst beide Richtungen, denn ein Filter, der
# nur schliesst, ist genauso falsch wie einer, der nur oeffnet.
_ziel_ordner = Path(UMG["LOG_SYNC_REPO"]) / "ausarbeitungen"
_alles = sorted(str(p.relative_to(_ziel_ordner))
                for p in _ziel_ordner.rglob("*") if p.is_file())
_fremd = [x for x in _alles if x.startswith(("node_modules/", "venv/", ".venv/"))]
zeile("kein Fremd-Markdown aus venv oder node_modules im Log-Repo",
      not _fremd and "echt.md" in _alles,
      gemessen=f"fremd: {_fremd}; angekommen: {_alles}")


shutil.rmtree(TMP, ignore_errors=True)
_gemessen = zeilen - len(uebersprungen)
print(f"\n{_gemessen - len(fehler)}/{_gemessen} gemessene Zeilen grün"
      + (f", {len(uebersprungen)} NICHT GEMESSEN" if uebersprungen else ""))
sys.exit(1 if fehler else 0)
