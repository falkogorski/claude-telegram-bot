#!/usr/bin/env python3
"""Die dritte Schicht der Fuehrungs-Register-Absicherung — ausgefuehrt.

**Engywucks Maschinen-Gleichstand, Fund ③ (29.08.2026).** Der Hook
`.claude/hooks/guard-master-files.sh` blockiert Schreibzugriffe auf
`MIGRATION.md` und `CLAUDE.md`, solange die Arbeitskopie hinter dem Master
steht. Er verglich die Schreibweise **genau** — und wer nicht passte, fiel in
`*) exit 0`, also **durchlassen statt blockieren**.

Auf Adams Mac ist das Dateisystem schreibweisen-**un**empfindlich: `claude.md`
trifft dieselbe Datei, umging aber beide Muster. **Die Schranke war
ausgerechnet auf der Maschine loechrig, auf der die fuehrende Sitzung
schreibt** — auf VPS und Container entstand kein Loch, weil die Datei dort
unter dem anderen Namen nicht existiert.

**Dieser Pruefer existierte nicht.** Eine Schranke ohne Pruefer ist eine
Bitte — und diese hier hatte drei Schichten, von denen die dritte still offen
stand.

Gemessen wird das **Verhalten** an einem echten Wegwerf-Repo, das
nachweislich hinter seinem Ursprung steht. Kein Blick in den Quelltext.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
HOOK = WURZEL / ".claude" / "hooks" / "guard-master-files.sh"

fehler: list[str] = []
n = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global n
    n += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


def git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, timeout=30)


def hook_auf(pfad: str) -> int:
    """Ruft den Hook wie Claude Code es taete und gibt den Rueckgabewert."""
    eingabe = json.dumps({"tool_input": {"file_path": pfad}})
    r = subprocess.run(["bash", str(HOOK)], input=eingabe,
                       capture_output=True, text=True, timeout=60)
    return r.returncode


print("== Governance-Hook: blockiert er eine veraltete Kopie? ==")

basis = Path(tempfile.mkdtemp(prefix="governance-")).resolve()
try:
    # --- Ein Ursprung und eine Arbeitskopie, die nachweislich hinterherhinkt.
    ursprung = basis / "origin.git"
    arbeit = basis / "arbeit"
    git("init", "--quiet", "--bare", "-b", "mac-produktivstand", str(ursprung))

    vorbereitung = basis / "vorbereitung"
    git("clone", "--quiet", str(ursprung), str(vorbereitung))
    for name, inhalt in (("CLAUDE.md", "erste Fassung\n"),
                         ("MIGRATION.md", "erste Fassung\n"),
                         ("README.md", "harmlos\n")):
        (vorbereitung / name).write_text(inhalt, encoding="utf-8")
    git("add", "-A", cwd=vorbereitung)
    git("-c", "user.email=p@p", "-c", "user.name=P", "commit", "--quiet",
        "-m", "erste", cwd=vorbereitung)
    git("push", "--quiet", "origin", "HEAD:mac-produktivstand", cwd=vorbereitung)

    # Die Arbeitskopie zieht sich diesen Stand …
    git("clone", "--quiet", str(ursprung), str(arbeit))
    # … und der Ursprung geht danach weiter. Jetzt ist sie ein Commit hinten.
    (vorbereitung / "CLAUDE.md").write_text("zweite Fassung\n", encoding="utf-8")
    git("add", "-A", cwd=vorbereitung)
    git("-c", "user.email=p@p", "-c", "user.name=P", "commit", "--quiet",
        "-m", "zweite", cwd=vorbereitung)
    git("push", "--quiet", "origin", "HEAD:mac-produktivstand", cwd=vorbereitung)

    hinter = git("rev-list", "HEAD..origin/mac-produktivstand", "--count",
                 cwd=arbeit)
    git("fetch", "origin", "--quiet", cwd=arbeit)
    hinter = git("rev-list", "HEAD..origin/mac-produktivstand", "--count",
                 cwd=arbeit).stdout.strip()
    zeile("der Pruefstand steht wirklich hinter dem Ursprung", hinter == "1",
          gemessen=f"{hinter} Commit(s) — sonst waere alles darunter bedeutungslos")

    # --- Die eigentliche Messung: JEDE Schreibweise muss blockieren.
    print("-- die Schranke greift schreibweisen-unabhaengig --")
    for name in ("CLAUDE.md", "claude.md", "Claude.md", "CLAUDE.MD",
                 "MIGRATION.md", "migration.md", "Migration.MD"):
        rc = hook_auf(str(arbeit / name))
        zeile(f"[{name}] wird blockiert", rc == 2,
              gemessen=f"exit {rc} — 0 heisst DURCHGELASSEN")

    # --- Die Gegenrichtung: eine Schranke, die alles blockiert, ist keine.
    print("-- und sie greift nicht bei allem anderen --")
    for name in ("README.md", "notclaude.md", "CLAUDE.md.bak",
                 "migration.py", "bot.py"):
        rc = hook_auf(str(arbeit / name))
        zeile(f"[{name}] laeuft durch", rc == 0, gemessen=f"exit {rc}")

    # --- Und bei aktuellem Stand darf nichts blockieren.
    print("-- eine aktuelle Kopie wird nicht behindert --")
    git("pull", "--quiet", "origin", "mac-produktivstand", cwd=arbeit)
    for name in ("CLAUDE.md", "claude.md", "MIGRATION.md"):
        rc = hook_auf(str(arbeit / name))
        zeile(f"[{name}] bei aktuellem Stand frei", rc == 0,
              gemessen=f"exit {rc} — eine Schranke, die immer blockiert, "
                       "wird abgeschaltet")
finally:
    shutil.rmtree(basis, ignore_errors=True)

print()
if fehler:
    print(f"❌ {len(fehler)} von {n} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {n} Zeilen des Governance-Hook-Pruefers bestanden")
