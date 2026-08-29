#!/usr/bin/env python3
"""Prueft die Bash-Positivliste — AUSGEFUEHRT, nicht gelesen.

**Engywucks Auflage B (Nachtpaket 29.08.):** *„Je Pruefzeile der neuen
Zerlegung die Entkernungs-Gegenprobe … Besonders fuer jede Verkettungsform
aus Auftrag 4 einzeln und den Symlink-Fall. Das ist die Prueferklasse, bei
der 61 von 116 blind waren — nicht wieder."*

Deshalb ruft dieser Pruefer `entscheiden()` **auf** und misst das Urteil.
Keine Zeile sucht Quelltext; keine Zeile zaehlt Vorkommen. Die
Geheimnis-Schranke wird als **Attrappe** hereingereicht — so ist messbar,
dass ein Treffer wirklich abweist, statt zufaellig an etwas anderem zu
scheitern.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bashfreigabe as bf                                    # noqa: E402

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


# ---- Wegwerf-Bereiche: gemessen wird gegen Ordner, die es wirklich gibt,
#      denn `resolve()` verhaelt sich bei fehlenden Pfaden anders.
import tempfile                                              # noqa: E402
# **Der Ablageort ist Teil der Pruefung, nicht Beiwerk.** `mkdtemp` legt auf
# macOS unter `/var/folders/…` an — und `/var` ist ein symbolischer Verweis auf
# `/private/var`. Diese eine Aufloesung ueberlagerte in der Gegenprobe jede
# andere: Beim Entkernen von `resolve()` wurden zwanzig Zeilen rot, aber
# ausgerechnet die Symlink-Zeile blieb gruen — sie wurde vom `/var`-Effekt
# mitgefangen statt von dem, was sie messen soll. Also auf einem Pfad
# arbeiten, der schon aufgeloest ist.
tmp = Path(tempfile.mkdtemp(prefix="bashfrei-", dir="/private/tmp")).resolve()
(repo := tmp / "repo").mkdir()
(ws := tmp / "workspace").mkdir()
(pf := tmp / "postfach").mkdir()
(logs := tmp / "logs").mkdir()
(draussen := tmp / "draussen").mkdir()
(repo / "README.md").write_text("x")
(draussen / "geheim.txt").write_text("x")

BEREICHE = (
    bf.Bereich("repo", repo, schreibbar=False),
    bf.Bereich("workspace", ws, schreibbar=True),
    bf.Bereich("postfach", pf, schreibbar=True),
    bf.Bereich("logs", logs, schreibbar=False),
)

# Attrappe: nur DIESE Zeichenkette gilt als Geheimnis. So kann kein Treffer
# aus einem anderen Grund entstehen.
MARKE = "GEHEIMWORT"
def geheim(s: str) -> bool:
    return MARKE in (s or "")


def u(cmd: str) -> str:
    return bf.entscheiden(cmd, ist_geheimnis=geheim, bereiche=BEREICHE).urteil


def e(cmd: str):
    return bf.entscheiden(cmd, ist_geheimnis=geheim, bereiche=BEREICHE)


print("== Bash-Positivliste ==")

# ---------------------------------------------------------------- Auftrag 1
print("-- Auftrag 1: was frei laufen soll")
zeile("lesen im Repo ist frei", u(f"grep -rn muster {repo}/README.md") == bf.FREI,
      gemessen=e(f"grep -rn muster {repo}/README.md").grund)
zeile("ls im Arbeitsordner ist frei", u(f"ls -la {ws}") == bf.FREI,
      gemessen=e(f"ls -la {ws}").grund)
zeile("schreiben im Arbeitsordner ist frei", u(f"cp {ws}/a {ws}/b") == bf.FREI,
      gemessen=e(f"cp {ws}/a {ws}/b").grund)
zeile("schreiben ins Postfach ist frei", u(f"printf x > {pf}/auftrag.json") == bf.FREI,
      gemessen=e(f"printf x > {pf}/auftrag.json").grund)
zeile("git log ist frei", u(f"git -C {repo} log --oneline") == bf.FREI,
      gemessen=e(f"git -C {repo} log --oneline").grund)
zeile("systemctl status ist frei", u("systemctl status claude-bot") == bf.FREI,
      gemessen=e("systemctl status claude-bot").grund)
zeile("pandoc mit Ziel im Arbeitsordner ist frei",
      u(f"pandoc {repo}/README.md -o {ws}/out.pdf") == bf.FREI,
      gemessen=e(f"pandoc {repo}/README.md -o {ws}/out.pdf").grund)
zeile("date ohne Pfad ist frei", u("date +%s") == bf.FREI)

# ---- die EINE erlaubte Verkettungsform
zeile("cd <Bereich> && lesen ist frei", u(f"cd {ws} && ls -la") == bf.FREI,
      gemessen=e(f"cd {ws} && ls -la").grund)
zeile("cd nach draussen && lesen ist NICHT frei",
      u(f"cd {draussen} && ls -la") == bf.DIALOG)
zeile("etwas anderes als cd vor && ist nicht frei",
      u(f"grep x {repo}/README.md && ls {ws}") == bf.DIALOG)
zeile("zwei && sind nicht frei", u(f"cd {ws} && ls && ls") == bf.DIALOG)

# ---------------------------------------------------------------- Auftrag 2
print("-- Auftrag 2: was abgewiesen wird, ohne Dialog")
zeile("Geheimnis wird ABGEWIESEN, nicht vorgelegt",
      u(f"cat {ws}/{MARKE}") == bf.ABWEISEN,
      gemessen=e(f"cat {ws}/{MARKE}").grund)
# **Kein `Path.home()`, und der Differenzmesser hat den Grund gefunden.**
# Er meldete `HOME` als Zustandsablage ohne Riegel — zu Recht: Ein Prueflauf,
# der das echte Heimverzeichnis liest, misst gegen Adams echte Ordner statt
# gegen Wegwerf-Ordner. Hier war es nur lesend, aber die Regel ist richtig,
# und sie kostet nichts: `_ist_claude_ordner` prueft den PFADBESTANDTEIL
# `.claude`, nicht das Heimverzeichnis. Ein nachgebautes `.claude` unter dem
# Wegwerf-Ordner misst dasselbe — hermetisch.
heim = tmp
(heim / ".claude" / "memory").mkdir(parents=True)
(heim / ".claude" / "settings.json").write_text("{}")
(heim / ".claude" / "memory" / "MEMORY.md").write_text("x")
zeile(".claude wird abgewiesen",
      u(f"cat {heim}/.claude/settings.json") == bf.ABWEISEN,
      gemessen=e(f"cat {heim}/.claude/settings.json").grund)
zeile("Auflage A: .claude/memory bleibt LESBAR",
      u(f"cat {heim}/.claude/memory/MEMORY.md") == bf.FREI,
      gemessen=e(f"cat {heim}/.claude/memory/MEMORY.md").grund)
zeile("Auflage A: .claude/memory ist nicht SCHREIBBAR",
      u(f"cp /x {heim}/.claude/memory/neu.md") != bf.FREI)
zeile("ausserhalb der Bereiche -> nicht frei",
      u(f"cat {draussen}/geheim.txt") == bf.DIALOG,
      gemessen=e(f"cat {draussen}/geheim.txt").grund)

# ---------------------------------------------------------------- Auftrag 3
print("-- Auftrag 3: was dialogpflichtig bleibt")
for cmd, was in [
    ("curl https://example.com", "Netz"),
    (f"wget -O {ws}/x https://example.com", "Netz"),
    ("ssh vps uptime", "Netz"),
    (f"git -C {repo} push", "veroeffentlichen"),
    ("systemctl restart claude-bot", "Betrieb"),
    ("sudo -i", "Betrieb"),
    (f"rm -rf {ws}/alles", "loeschen"),
    (f"chmod 777 {ws}/x", "Rechte"),
    ("pip install irgendwas", "Paketverwaltung"),
]:
    zeile(f"{was}: [{cmd.split()[0]}] bleibt im Dialog", u(cmd) == bf.DIALOG,
          gemessen=e(cmd).grund)

# **Der Punkt, der die ganze Konstruktion traegt.**
for prog in ("python3", "python", "bash", "sh", "node", "perl", "make"):
    zeile(f"Programmausfuehrung [{prog}] bleibt im Dialog",
          u(f"{prog} {ws}/x.py") == bf.DIALOG, gemessen=e(f"{prog} {ws}/x.py").grund)

# ---------------------------------------------------------------- Auftrag 4
print("-- Auftrag 4: die zerlegte Zeile (jede Form EINZELN)")
# **Die Nutzlast traegt bewusst KEINEN Schraegstrich.**
# Erste Fassung war `curl https://fremd.example` — und die Gegenprobe hat
# gezeigt, dass diese Zeilen damit blind waren: Beim Entfernen der
# Verkettungs-Sperre blieben sie gruen, weil `https://fremd.example` einen
# Schraegstrich hat, als Pfad gilt und schon von der BEREICHS-Pruefung
# gefangen wurde. Die Zeile mass also die Bereichspruefung, nicht die
# Verkettungssperre — der Fehler, gegen den die Gegenprobe ueberhaupt
# gefahren wird.
#
# `rm -rf alles` hat keinen Schraegstrich und keinen Pfad. Ohne die
# Verkettungs-Sperre laeuft das durch.
GEFAEHRLICH = f"grep muster {repo}/README.md"
for anhang, was in [
    ("; rm -rf alles", "Strichpunkt"),
    ("| sudo tee raus", "Rohr"),
    ("|| rm -rf alles", "Oder"),
    ("&& ls && rm -rf alles", "zweites Und"),
    ("\nrm -rf alles", "Zeilenumbruch"),
]:
    zeile(f"Verkettung [{was}] wird nicht frei", u(f"{GEFAEHRLICH} {anhang}") != bf.FREI,
          gemessen=e(f"{GEFAEHRLICH} {anhang}").grund)
# Und die Form ganz ohne jeden Pfad — die schaerfste Probe der Sperre.
zeile("Verkettung ohne jeden Pfad wird nicht frei",
      u("ls ; rm -rf alles") != bf.FREI, gemessen=e("ls ; rm -rf alles").grund)

# Dieselbe Lehre wie oben: Die Ersetzung darf keinen Schraegstrich tragen,
# sonst misst die Zeile die Bereichspruefung. `$(cat liste)` hat keinen — und
# ohne die Ersetzungs-Sperre findet `grep` gar keinen Pfad, faellt in den
# Zweig „Arbeitsverzeichnis" und waere FREI.
for form, was in [
    ("$(cat liste)", "Ersetzung"),
    ("`cat liste`", "Rueckwaertsanfuehrung"),
    ("<(cat liste)", "Prozess-Ersetzung"),
    ("$ZIEL", "Variable"),
    ("${ZIEL}", "Variable in Klammern"),
]:
    zeile(f"[{was}] wird nicht frei", u(f"grep muster {form}") != bf.FREI,
          gemessen=e(f"grep muster {form}").grund)
# Der Vollstaendigkeit halber auch die Form MIT Pfad — sie ist doppelt
# gedeckt, und das ist in Ordnung, solange man weiss, was man misst.
zeile("[Variable mit Pfad] wird nicht frei",
      u("cat $HOME/.ssh/id_rsa") != bf.FREI)

zeile("Umlenkung nach draussen wird nicht frei",
      u(f"grep x {repo}/README.md > {draussen}/raus.txt") != bf.FREI,
      gemessen=e(f"grep x {repo}/README.md > {draussen}/raus.txt").grund)
zeile("Umlenkung in den Arbeitsordner bleibt frei",
      u(f"grep x {repo}/README.md > {ws}/raus.txt") == bf.FREI,
      gemessen=e(f"grep x {repo}/README.md > {ws}/raus.txt").grund)
zeile("Fehlerumleitung stoert nicht",
      u(f"ls {ws} 2>/dev/null") == bf.FREI, gemessen=e(f"ls {ws} 2>/dev/null").grund)

# Pfadaufstieg — der Fall, der am 23.08. live durchlief.
zeile("Pfadaufstieg mit .. wird nicht frei",
      u(f"cat {repo}/../draussen/geheim.txt") != bf.FREI,
      gemessen=e(f"cat {repo}/../draussen/geheim.txt").grund)

# **Symlink-Fall, Engywuck nennt ihn ausdruecklich.** Ein Verweis IM Bereich,
# der aus dem Bereich hinausfuehrt — die Zeichenkette sieht harmlos aus.
(ws / "brueckchen").symlink_to(draussen)
zeile("Symlink aus dem Bereich heraus wird nicht frei",
      u(f"cat {ws}/brueckchen/geheim.txt") != bf.FREI,
      gemessen=e(f"cat {ws}/brueckchen/geheim.txt").grund)

zeile("unbalancierte Anfuehrungszeichen -> nicht frei",
      u(f'grep "offen {repo}/README.md') != bf.FREI)
zeile("unbekanntes Verb -> Dialog, nicht frei",
      u(f"jq . {ws}/x.json") == bf.DIALOG, gemessen=e(f"jq . {ws}/x.json").grund)
zeile("find -exec wird nicht frei",
      u(f"find {ws} -name '*.py' -exec bash -c x +") != bf.FREI,
      gemessen=e(f"find {ws} -name '*.py' -exec bash -c x +").grund)
zeile("find -delete wird nicht frei",
      u(f"find {ws} -name '*.py' -delete") != bf.FREI)
zeile("sed -i (in-place) braucht einen schreibbaren Bereich",
      u(f"sed -i s/a/b/ {repo}/README.md") == bf.DIALOG,
      gemessen=e(f"sed -i s/a/b/ {repo}/README.md").grund)
zeile("sed -n (lesend) ist im Repo frei",
      u(f"sed -n 1,5p {repo}/README.md") == bf.FREI,
      gemessen=e(f"sed -n 1,5p {repo}/README.md").grund)
zeile("langer Schlaf bleibt im Dialog", u("sleep 99999") == bf.DIALOG)
zeile("kurzer Schlaf ist frei", u("sleep 2") == bf.FREI, gemessen=e("sleep 2").grund)

# ---------------------------------------------------------------- Auftrag 5
print("-- Auftrag 5: das Protokoll")
erg = e(f"grep -rn x {ws}/datei.txt")
zeile("Befehlsart wird gemeldet", erg.befehlsart == "grep", gemessen=erg.befehlsart)
zeile("Bereich wird gemeldet", erg.bereich == "workspace", gemessen=erg.bereich)
zeile("kein Geheimnis im Protokollfeld",
      MARKE not in erg.befehlsart and MARKE not in erg.bereich)
zeile("Pfad mit Verzeichnis wird als Verb protokolliert",
      e(f"/bin/ls {ws}").befehlsart == "ls")

# ---------------------------------------------------------------- fail-closed
print("-- Vorgabe ist fail-closed")
zeile("leerer Befehl -> Dialog", u("") == bf.DIALOG)
zeile("nur Leerzeichen -> Dialog", u("   ") == bf.DIALOG)

# ---------------------------------------------------------------- 8.7
print("-- 8.7: die Positivliste kann das Repo nicht oeffnen")
#
# **Der Auftrag nennt das den gefaehrlichsten Fall:** *„Der Schalter dockt
# versehentlich ueber der Sensibilitaetspruefung an … Merkt: niemand, bis es
# passiert."* Sein Vorschlag war ein Pruefer, der die REIHENFOLGE im Quelltext
# festschreibt.
#
# **Ein Reihenfolge-Pruefer waere aber genau die Klasse, die acht von acht Mal
# umgehbar war** — er liest Quelltext. Die tragfaehigere Absicherung ist ein
# doppelter Boden, der die Reihenfolge gar nicht braucht: Selbst wenn die
# Positivliste eines Tages VOR der 8.7-Sperre stuende, darf sie einen
# schreibenden Repo-Befehl nicht freigeben. Das ist ausfuehrbar messbar.
import bot                                                     # noqa: E402
ECHT = bf.bereiche_aus_umgebung()
def ue(cmd: str) -> str:
    return bf.entscheiden(cmd, ist_geheimnis=lambda s: bot._is_sensitive_ref(
        s, schreibend=False), bereiche=ECHT).urteil

REPO = str(Path(bot.__file__).resolve().parent)
for cmd, was in [
    (f"git -C {REPO} commit -m x", "git commit"),
    (f"git -C {REPO} push", "git push"),
    (f"sed -i s/a/b/ {REPO}/bot.py", "sed -i"),
    (f"printf x > {REPO}/bot.py", "Umlenkung ins Repo"),
    (f"cp /tmp/x {REPO}/bot.py", "cp ins Repo"),
    (f"rm {REPO}/bot.py", "rm im Repo"),
    (f"tee {REPO}/bot.py", "tee ins Repo"),
    (f"mv /tmp/x {REPO}/bot.py", "mv ins Repo"),
    (f"cd {REPO} && git commit -m x", "cd + git commit"),
    (f"mkdir {REPO}/neu", "mkdir im Repo"),
]:
    zeile(f"8.7 haelt: [{was}] wird NICHT frei", ue(cmd) != bf.FREI,
          gemessen=bf.entscheiden(cmd, ist_geheimnis=lambda s: bot._is_sensitive_ref(
              s, schreibend=False), bereiche=ECHT).grund)

# Und die echte Geheimnis-Schranke, nicht die Attrappe: Sie muss auch mit dem
# scharfen `_is_sensitive_ref` abweisen — sonst haette die Attrappe oben nur
# bewiesen, dass eine Attrappe funktioniert.
zeile("echte Geheimnis-Schranke weist ab (nicht nur die Attrappe)",
      ue(f"cat {REPO}/.env") == bf.ABWEISEN,
      gemessen=bf.entscheiden(f"cat {REPO}/.env",
                              ist_geheimnis=lambda s: bot._is_sensitive_ref(s, schreibend=False),
                              bereiche=ECHT).grund)

# Das zweite Netz: die Verdrahtung wird WIRKLICH gerufen. Gezaehlt werden
# echte Aufrufknoten, nicht Zeilen mit dem Namen — ein Kommentar steht im
# Syntaxbaum nicht, und genau daran war die Zeilenzaehlung frueher blind.
import ast as _ast                                             # noqa: E402
_baum = _ast.parse(Path(bot.__file__).with_suffix(".py").read_text(encoding="utf-8"))
_rufe = [k for k in _ast.walk(_baum)
         if isinstance(k, _ast.Call)
         and isinstance(k.func, _ast.Attribute)
         and k.func.attr == "entscheiden"
         and isinstance(k.func.value, _ast.Name)
         and k.func.value.id == "bashfreigabe"]
zeile("bot.py ruft bashfreigabe.entscheiden wirklich auf",
      len(_rufe) >= 1, gemessen=f"{len(_rufe)} Aufrufknoten")
zeile("der Aufruf reicht die Geheimnis-Schranke herein",
      any(any(kw.arg == "ist_geheimnis" for kw in r.keywords) for r in _rufe))

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Bash-Positivliste bestanden")
