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


def hook_roh(eingabe: str, *, pfad_umgebung: str | None = None):
    """Wie oben, aber mit **beliebiger** Eingabe und wahlweise verbogenem PATH.

    Braucht es, weil die gefaehrlichste Frage nicht lautet „blockiert er die
    richtige Datei?", sondern **„was tut er, wenn er gar nicht urteilen
    kann?"** — und die liess sich mit der bisherigen Hilfsfunktion nicht
    stellen, weil sie immer gueltiges JSON erzeugte.
    """
    umgebung = dict(os.environ)
    if pfad_umgebung is not None:
        umgebung["PATH"] = pfad_umgebung
    return subprocess.run(["bash", str(HOOK)], input=eingabe, env=umgebung,
                          capture_output=True, text=True, timeout=60)


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

    # --- Der Ausfall. Bis zum 30.08. prüfte diese Frage niemand.
    print("-- ein Ausfall sieht NICHT mehr wie eine Freigabe aus (A3) --")

    # ① Unlesbares JSON. Vorher: `except: print('')` → leerer Pfad → exit 0.
    r = hook_roh("das ist kein JSON")
    zeile("unlesbare Eingabe blockiert", r.returncode == 2,
          gemessen=f"exit {r.returncode} — 0 hiesse: Ausfall = Freigabe")
    zeile("und sie sagt, warum", "auswerten" in r.stderr.lower(),
          gemessen=r.stderr.strip()[:110])

    # ② Gar kein python3 im PATH — der kaputte Shim aus dem Befund.
    leer = tempfile.mkdtemp(prefix="ohne-python-")
    for werkzeug in ("bash", "git", "basename", "dirname", "tr", "cat",
                     "printf", "command"):
        quelle = shutil.which(werkzeug)
        if quelle:
            try:
                os.symlink(quelle, Path(leer) / werkzeug)
            except OSError:
                pass
    r = hook_roh(json.dumps({"tool_input": {"file_path": str(arbeit / "CLAUDE.md")}}),
                 pfad_umgebung=leer)
    zeile("ohne python3 blockiert der Hook", r.returncode == 2,
          gemessen=f"exit {r.returncode}: {(r.stderr or '').strip()[:90]}")

    # ②b Und ohne **git** — der zweite Ausfall, der urteilsunfaehig macht.
    ohne_git = tempfile.mkdtemp(prefix="ohne-git-")
    # **Nur bash und python3** — und das ist die eigentliche Messung, nicht
    # Sparsamkeit: Braucht der Hook ein weiteres Programm, faellt er hier
    # durch, statt still durchzulassen. So wurde `sed` gefunden, das ich beim
    # Entfernen von `basename`/`tr` eine Zeile spaeter neu eingesetzt hatte.
    for werkzeug in ("bash", "python3"):
        quelle = shutil.which(werkzeug)
        if quelle:
            try:
                os.symlink(quelle, Path(ohne_git) / werkzeug)
            except OSError:
                pass
    r = hook_roh(json.dumps({"tool_input": {"file_path": str(arbeit / "CLAUDE.md")}}),
                 pfad_umgebung=ohne_git)
    # **Der GRUND wird mitgemessen, nicht nur der Rückgabewert.** Diese Zeile
    # war grün, ohne je den git-Zweig erreicht zu haben: Der Hook las seine
    # Eingabe mit `cat`, das im werkzeuglosen PATH ebenfalls fehlt — er
    # blockierte also schon eine Stufe früher. Ein Prüfer, der nur „blockiert"
    # misst, kann nicht unterscheiden, WORAN er blockiert hat.
    zeile("ohne git blockiert der Hook — und zwar wegen git",
          r.returncode == 2 and "git ist auf dieser Maschine nicht auffindbar" in (r.stderr or ""),
          gemessen=f"exit {r.returncode}: {(r.stderr or '').strip()[:110]}")

    # ②c Ein misslungener VERGLEICH. Vorher endete jeder rev-list-Fehler in
    #     `|| echo 0` — also in „die Kopie ist aktuell", der beruhigendsten
    #     aller Falschauskuenfte. Nachgestellt mit einem Repo, das die
    #     Gegenstelle kennt, aber selbst noch keinen Commit hat.
    kaputt = basis / "ohne-head"
    kaputt.mkdir()
    git("init", "--quiet", str(kaputt))
    git("fetch", "--quiet", str(ursprung),
        "mac-produktivstand:refs/remotes/origin/mac-produktivstand", cwd=kaputt)
    (kaputt / "CLAUDE.md").write_text("noch nie committet\n", encoding="utf-8")
    probe = git("rev-list", "HEAD..origin/mac-produktivstand", "--count", cwd=kaputt)
    zeile("der Pruefstand erzeugt wirklich einen Vergleichsfehler",
          probe.returncode != 0,
          gemessen=f"rc={probe.returncode} — sonst misst die naechste Zeile ins Leere")
    rc = hook_auf(str(kaputt / "CLAUDE.md"))
    zeile("ein misslungener Vergleich blockiert (statt 0 zu melden)", rc == 2,
          gemessen=f"exit {rc} — 0 hiesse: „die Kopie ist aktuell“")

    # ②d **Ein python3, das auf stderr schwatzt** — Engywucks Widerlegung
    #     Rang 0 ③. Die erste fail-closed-Fassung fing stderr mit `2>&1` ein;
    #     eine Bibliothekswarnung klebte damit am Dateipfad, `basename` lieferte
    #     eine mehrzeilige Zeichenkette, das `case` traf nicht — **der
    #     fail-closed-Umbau hatte einen neuen fail-open erzeugt.** Und der
    #     Ausloeser war genau der, den die Commit-Nachricht nannte: ein
    #     kaputter Shim, der mit rc=0 endet und auf stderr schreibt.
    schwatzend = Path(tempfile.mkdtemp(prefix="schwatzendes-python-"))
    echtes_python = shutil.which("python3") or sys.executable
    (schwatzend / "python3").write_text(
        "#!/bin/sh\n"
        "echo 'objc[4711]: dyld warnung aus einer Bibliothek' >&2\n"
        f"exec {echtes_python} \"$@\"\n", encoding="utf-8")
    (schwatzend / "python3").chmod(0o755)
    for werkzeug in ("bash", "git"):
        quelle = shutil.which(werkzeug)
        if quelle:
            try:
                os.symlink(quelle, schwatzend / werkzeug)
            except OSError:
                pass
    r = hook_roh(json.dumps({"tool_name": "Edit",
                             "tool_input": {"file_path": str(arbeit / "CLAUDE.md")}}),
                 pfad_umgebung=f"{schwatzend}:{os.environ.get('PATH','')}")
    zeile("eine Warnung auf stderr oeffnet die Schranke NICHT", r.returncode == 2,
          gemessen=f"exit {r.returncode} — 0 hiesse: eine Bibliothekswarnung "
                   f"haengt den Riegel aus")

    # ②e **Das gedriftete Schema** — in der A3-Commit-Nachricht als behoben
    #     aufgefuehrt, gebaut war es nicht. Ein Schreib-Werkzeug ohne Dateipfad
    #     gibt es nicht; kommt es doch, hat sich das Schema geaendert.
    r = hook_roh(json.dumps({"tool_name": "Edit", "tool_input": {"pfad": "/x/CLAUDE.md"}}))
    zeile("ein Schreib-Werkzeug ohne Dateipfad blockiert (Schema-Drift)",
          r.returncode == 2, gemessen=f"exit {r.returncode}: {r.stderr.strip()[:90]}")

    # ③ Die Gegenrichtung, und ohne sie waere ① wertlos: Eine gueltige Anfrage
    #    OHNE Dateipfad ist der Normalfall anderer Werkzeuge und muss durch.
    r = hook_roh(json.dumps({"tool_input": {"command": "ls"}}))
    zeile("gueltige Anfrage ohne Dateipfad laeuft durch", r.returncode == 0,
          gemessen=f"exit {r.returncode} — sonst blockiert der Hook alles")

    # ④ Ein FREMDES Repo mit eigener CLAUDE.md darf nicht blockiert werden.
    #    Ohne diese Zeile waere der fail-closed-Umbau ein Arbeitsverbot in
    #    jedem anderen Projekt Adams.
    fremd = basis / "fremdes-projekt"
    fremd.mkdir()
    git("init", "--quiet", str(fremd))
    (fremd / "CLAUDE.md").write_text("anderes Projekt\n", encoding="utf-8")
    git("add", "-A", cwd=fremd)
    git("-c", "user.email=f@f", "-c", "user.name=F", "commit", "--quiet",
        "-m", "eins", cwd=fremd)
    rc = hook_auf(str(fremd / "CLAUDE.md"))
    zeile("ein fremdes Projekt ohne diesen Zweig laeuft durch", rc == 0,
          gemessen=f"exit {rc} — sonst waere der Hook dort ein Arbeitsverbot")

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
