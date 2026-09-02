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
# **Hermetik (Lehre aus dem Abhaengigkeits-Register, Punkt 4).** Die Umgebung
# wird ERZWUNGEN, nicht ergaenzt. Ohne diese Zeilen laeuft der Pruefer nur
# dort, wo zufaellig eine `.env` liegt — im Probelauf-Klon vom 29.08. ist er
# genau daran gescheitert, waehrend er im Hauptbaum gruen war. Ein Pruefer,
# der von einer nicht versionierten Datei abhaengt, misst die Maschine und
# nicht den Code.
import os as _os
_os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
_os.environ["ALLOWED_USER_IDS"] = "4711"

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
# macOS unter `/var/folders/…` an — und `/var` ist dort ein symbolischer
# Verweis auf `/private/var`. Diese eine Aufloesung ueberlagerte in der
# Gegenprobe jede andere: Beim Entkernen von `resolve()` wurden zwanzig Zeilen
# rot, aber ausgerechnet die Symlink-Zeile blieb gruen — sie wurde vom
# `/var`-Effekt mitgefangen statt von dem, was sie messen soll.
#
# **`[BERICHTIGT 29.08., Engywucks Gegenpruefung]` Die Diagnose war richtig,
# die Medizin falsch.** Hier stand `dir="/private/tmp"` — und **den Pfad gibt
# es nur auf macOS.** Auf dem VPS starb dieser Pruefer beim Import, bevor eine
# einzige Zeile lief. Der Betriebscode war einwandfrei; **tot war der
# Pruefer** — und zwar stumm, nicht laut. Die neue Sicherheitsschranke waere
# auf den VPS gegangen und dort ungeprueft im Betrieb gestanden.
#
# `resolve()` allein loest den `/var`-Verweis auf **jedem** System auf. Der
# Effekt, der ausgeschlossen werden sollte, ist damit weg, ohne einen
# macOS-Pfad festzuschreiben.
tmp = Path(tempfile.mkdtemp(prefix="bashfrei-")).resolve()
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
# **`[UMGESTELLT 02.09.2026, U-3b]` Diese zwei Zeilen hiessen bis heute
# „etwas anderes als cd vor && ist nicht frei" und „zwei && sind nicht frei".
# Beides galt und gilt nicht mehr — `&&` wird jetzt zerlegt wie `;`.**
#
# Sie werden UMGESTELLT statt geloescht, weil sie die eigentliche Zusage
# tragen: Die Zerlegung darf nicht dazu fuehren, dass mehr durchgeht als die
# Summe der einzelnen Glieder. Geloescht waere die Zusage weg gewesen;
# umgestellt misst sie weiter, nur die richtige Sache.
zeile("etwas anderes als cd vor && wird zerlegt, nicht pauschal frei",
      u(f"grep x {repo}/README.md && ls {ws}") == bf.FREI
      and u(f"grep x {repo}/README.md && rm {ws}/x") == bf.DIALOG,
      gemessen=e(f"grep x {repo}/README.md && rm {ws}/x").grund)
zeile("zwei && sind erlaubt — aber jedes Glied wird einzeln geprueft",
      u(f"ls {ws} && ls {repo} && ls {ws}") == bf.FREI
      and u(f"ls {ws} && ls {draussen} && ls {ws}") == bf.DIALOG,
      gemessen=e(f"ls {ws} && ls {draussen} && ls {ws}").grund)

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


# ---------------------------------------------------------------- Auftrag 5 (Auswertung)
print("-- Auftrag 5: die Auswertung legt von selbst vor")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bash_dialog_auswertung as bda                            # noqa: E402

# `beurteilen` ist eine reine Funktion — messbar ohne Datei und ohne Uhr.
PROBE = (
    [{"urteil": "frei", "art": "grep", "bereich": "repo"}] * 100
    + [{"urteil": "dialog", "art": "python3", "bereich": "workspace"}] * 12
    + [{"urteil": "dialog", "art": "curl", "bereich": "—"}] * 6
    + [{"urteil": "dialog", "art": "jq", "bereich": "workspace"}] * 2
    + [{"urteil": "abweisen", "art": "cat", "bereich": "—"}] * 3
)
b = bda.beurteilen(PROBE)
zeile("zaehlt die Urteile getrennt",
      (b["gesamt"], b["frei"], b["dialog"], b["abgewiesen"]) == (123, 100, 20, 3),
      gemessen=str((b["gesamt"], b["frei"], b["dialog"], b["abgewiesen"])))
zeile("erkennt den Wiederkehrer", b["wiederkehrer"][0][0] == "python3",
      gemessen=str(b["wiederkehrer"][:2]))
zeile("seltene Auslöser erzeugen keinen Vorschlag",
      not any("jq" in v for v in b["vorschlaege"]), gemessen=str(b["vorschlaege"]))

# **Die wichtigste Zeile: die Stossrichtung darf nicht kippen.**
_pv = " ".join(b["vorschlaege"])
zeile("bei python3 wird NICHT die Klasse geoeffnet",
      "NICHT die Klasse" in _pv and "benanntes Skript" in _pv, gemessen=_pv[:120])
# **`[UMGESTELLT 02.09.2026, U-4]` Das Maß hing an einer absoluten Wochenzahl
# (`SCHWELLE_DIALOGE = 50`) und meldete am 31.08. Gruen bei 91 % Dialoganteil
# — weil in jener Woche wenig gearbeitet wurde. Jetzt haengt es am ANTEIL.**
#
# Drei Lagen statt zwei, und die dritte ist der Grund fuer die Umstellung:
# `None` heisst „zu wenig gemessen", nicht „Maß verfehlt".
_viele_frei = ([{"urteil": "frei", "art": "ls", "bereich": "repo"}] * 90
               + [{"urteil": "dialog", "art": "curl", "bereich": "—"}] * 10)
_viele_dialog = ([{"urteil": "frei", "art": "ls", "bereich": "repo"}] * 10
                 + [{"urteil": "dialog", "art": "curl", "bereich": "—"}] * 90)
_wenige = [{"urteil": "dialog", "art": "curl", "bereich": "—"}] * 3

zeile("niedriger Dialoganteil gilt als erreicht",
      bda.beurteilen(_viele_frei)["ziel_erreicht"] is True,
      gemessen=f"Anteil {bda.beurteilen(_viele_frei)['anteil']:.0%}")
zeile("hoher Dialoganteil gilt als NICHT erreicht — auch bei viel Arbeit",
      bda.beurteilen(_viele_dialog)["ziel_erreicht"] is False,
      gemessen=f"Anteil {bda.beurteilen(_viele_dialog)['anteil']:.0%}")
zeile("zu wenig Aufrufe faellen KEIN Urteil (weder gut noch schlecht)",
      bda.beurteilen(_wenige)["ziel_erreicht"] is None
      and "KEIN Urteil" in bda.bericht(bda.beurteilen(_wenige)),
      gemessen=bda.bericht(bda.beurteilen(_wenige)).splitlines()[-1][:80])
# Der alte Fehler, ausdruecklich gemessen: WENIGE Dialoge bei INSGESAMT wenig
# Arbeit duerfen nicht mehr als Erfolg durchgehen.
zeile("die alte Falle: wenig Arbeit ist kein erreichtes Mass",
      bda.beurteilen([{"urteil": "dialog", "art": "curl", "bereich": "—"}] * 11
                     )["ziel_erreicht"] is not True)

# Eine unlesbare Ablage ist ein Befund, kein Abbruch.
b2 = bda.beurteilen([{"urteil": "_kaputt", "anzahl": 4}])
zeile("unlesbare Zeilen werden gemeldet, nicht verschluckt",
      b2["kaputte_zeilen"] == 4 and "unlesbare" in bda.bericht(b2))
zeile("leere Ablage sagt es ausdruecklich",
      "Keine Aufrufe" in bda.bericht(bda.beurteilen([])))

# Und das Ablegen selbst: Zeitpunkt, Urteil, Art, Bereich — sonst nichts.
import json as _json                                            # noqa: E402
protokoll = tmp / "protokoll.jsonl"
import os as _os                                                # noqa: E402
_os.environ["BASHFREI_PROTOKOLL"] = str(protokoll)
bf.protokollieren(e(f"grep x {ws}/datei.txt"), zeit="2026-08-29 03:40:00")
_z = _json.loads(protokoll.read_text(encoding="utf-8").strip())
zeile("Protokoll legt genau vier Felder ab",
      set(_z) == {"zeit", "urteil", "art", "bereich"}, gemessen=str(sorted(_z)))
zeile("Protokoll enthaelt KEINEN Grund und KEINE Pfade",
      "grund" not in _z and str(ws) not in protokoll.read_text(encoding="utf-8"))

# ---------------------------------------------------------------- Zerlegung
#
# **Ausgefuehrt, nicht gelesen.** Eine Zeile, die `_BODEN_BEFEHLE` im Quelltext
# sucht, ist umgehbar — acht von acht gemessenen Faellen. Hier laeuft der Pfad.
print()
print("== Zerlegung an ; und | (01.09.) ==")

zeile("eine harmlose Pipe ist frei",
      e(f"grep x {ws}/datei.txt | head -5").urteil == bf.FREI,
      gemessen=e(f"grep x {ws}/datei.txt | head -5").grund)
zeile("ein Semikolon zwischen zwei freien Gliedern ist frei",
      e(f"cat {ws}/datei.txt ; ls -la {ws}").urteil == bf.FREI)
zeile("ein einziges dialogpflichtiges Glied entscheidet fuer den ganzen Befehl",
      e(f"grep x {ws}/datei.txt | chmod 644 {ws}/datei.txt").urteil == bf.DIALOG)

# **Die Zeile, die bei der Gegenprobe rot werden muss.** Ohne die
# Boden-Bedingung wuerde `cd /etc` als eigenes Glied gepruft, faende sich
# nicht auf der Positivliste und ergaebe von selbst einen Dialog — deshalb
# misst diese Zeile den GRUND, nicht nur das Urteil.
_boden = e("cd /etc | cat passwd")
zeile("ein bodenverschiebendes Glied faellt aus dem RICHTIGEN Grund in den Dialog",
      _boden.urteil == bf.DIALOG and "verschiebt den Boden" in _boden.grund,
      gemessen=f"{_boden.urteil} · {_boden.grund[:60]}")
_zuweisung = e("X=1 ; env")
zeile("auch eine Zuweisung verschiebt den Boden",
      _zuweisung.urteil == bf.DIALOG and "verschiebt den Boden" in _zuweisung.grund,
      gemessen=f"{_zuweisung.urteil} · {_zuweisung.grund[:60]}")

zeile("ein Zeilenumbruch bleibt Dialog (nicht beauftragt, konservativ)",
      e(f"ls {ws}\ncat {ws}/datei.txt").urteil == bf.DIALOG)
zeile("die eine erlaubte cd-Form bleibt unangetastet",
      e(f"cd {ws} && ls -la").urteil == bf.FREI,
      gemessen=e(f"cd {ws} && ls -la").grund)

# ---------------------------------------------------------------- A2
print()
print("== cd-Ziel als Aufloesungsbasis (A2, 02.09.) ==")

# **Der Kern in einem Satz:** Vorher urteilte die Pruefung ueber einen anderen
# Pfad als den, den die Shell liest. Ein relativer Pfad nach `cd X` wurde gegen
# das Arbeitsverzeichnis des Bot-Prozesses aufgeloest.
zeile("ein relativer Pfad loest gegen das cd-Ziel auf",
      bf._aufloesen("unterordner/x.txt", ws) == (ws / "unterordner/x.txt"),
      gemessen=str(bf._aufloesen("unterordner/x.txt", ws)))
zeile("ein absoluter Pfad bleibt von der Basis unberuehrt",
      bf._aufloesen(f"{ws}/x.txt", Path("/etc")) == (ws / "x.txt"))
zeile("ohne Basis bleibt es beim Arbeitsverzeichnis (keine stille Aenderung)",
      bf._aufloesen("x.txt") == Path("x.txt").expanduser().resolve())

# **Die Zeile fuer die Gegenprobe.** Sie misst die Wirkung im echten Pfad:
# `cd <bereich> && cat <relativ>` ist frei, WEIL der relative Pfad jetzt im
# Bereich landet. Ohne A2 fiele er ausserhalb und ergaebe einen Dialog.
# **`[BERICHTIGT beim Gegenproben]` Diese Zeile mass zuerst nur das URTEIL —
# und blieb bei entkernter Basis-Aufloesung gruen.** Der Grund ist lehrreich:
# Ohne Basis loest `datei.txt` gegen das Arbeitsverzeichnis auf, und **das ist
# selbst ein erlaubter Bereich**. Das Urteil war also aus dem falschen Grund
# richtig. Gemessen wird jetzt der PFAD, ueber den geurteilt wurde.
# Ein Argument MIT Schraegstrich, denn nur solche prueft `_pfad_artig` —
# beim Gegenproben aufgefallen: `datei.txt` wird uebersprungen, die Zeile
# haette dann eine leere Pfadliste gemessen und nie etwas belegt.
_nach_cd = e(f"cd {ws} && cat unterordner/datei.txt")
zeile("nach cd wird der relative Pfad im richtigen Bereich gemessen",
      _nach_cd.urteil == bf.FREI
      and any(str(ws) in _p for _p in _nach_cd.pfade),
      gemessen=f"{_nach_cd.urteil} · Pfade: {_nach_cd.pfade}")

# ══════════════════════════════════════════════════════════════════════════
# U-3: benannte Skripte — die einzige Stelle, an der ein Deuter frei laeuft
#
# Gemessen wird nicht nur das URTEIL, sondern der GRUND. Ein `python3 -c …`
# faellt auch dann in den Dialog, wenn die Geheimnis-Schranke zuerst greift —
# und eine Zeile, die nur das Urteil misst, waere aus dem falschen Grund
# gruen. Dieselbe Lehre wie bei der Boden-Bedingung.
(_skripte := repo / "scripts").mkdir(exist_ok=True)
(_skripte / "postfach_ablegen.py").write_text("x")
(_skripte / "irgendwas.py").write_text("x")
(_unter := _skripte / "unterordner").mkdir(exist_ok=True)
(_unter / "postfach_ablegen.py").write_text("x")

_frei = e(f"python3 {_skripte}/postfach_ablegen.py --chat 1 --text x")
zeile("ein benanntes Skript laeuft ohne Rueckfrage (U-3)",
      _frei.urteil == bf.FREI, gemessen=f"{_frei.urteil} · {_frei.grund}")

for _cmd, _erwartet_im_grund, _was in [
    (f"python3 {_skripte}/irgendwas.py", "nicht unter den benannten",
     "ein anderes Skript im selben Ordner"),
    (f"python3 {draussen}/postfach_ablegen.py", "nicht direkt unter scripts",
     "derselbe Name ausserhalb"),
    (f"python3 {_unter}/postfach_ablegen.py", "nicht direkt unter scripts",
     "derselbe Name im Unterordner"),
    ('python3 -c "print(1)"', "Schalter statt eines Skripts",
     "der Deuter mit -c"),
    ("python3 -m http.server", "Schalter statt eines Skripts",
     "der Deuter mit -m"),
    ("python3", "ohne Skript", "der Deuter ganz ohne Skript"),
]:
    _e = e(_cmd)
    zeile(f"U-3 haelt: [{_was}] bleibt im Dialog — aus dem richtigen Grund",
          _e.urteil == bf.DIALOG and _erwartet_im_grund in _e.grund,
          gemessen=f"{_e.urteil} · {_e.grund}")

# Die Geheimnis-Schranke greift ueber den GANZEN Befehl, vor der Zerlegung —
# ein benanntes Skript hebelt sie nicht aus.
zeile("U-3 oeffnet die Geheimnis-Schranke nicht",
      u(f"python3 {_skripte}/postfach_ablegen.py; cat {MARKE}") != bf.FREI,
      gemessen=e(f"python3 {_skripte}/postfach_ablegen.py; cat {MARKE}").grund)

# ══════════════════════════════════════════════════════════════════════════
# U-3b: `&&` wird zerlegt wie `;` — mit `cd` als einziger benannter Ausnahme
#
# Die vier Zeilen sind Engywucks Gegenprobe, VOR dem Bau hingeschrieben:
# geht eine davon anders aus, wird nicht gebaut, sondern gemeldet.
zeile("&& wird zerlegt: [ls && wc] laeuft (U-3b)",
      u(f"ls && wc -l {repo}/README.md") == bf.FREI,
      gemessen=e(f"ls && wc -l {repo}/README.md").grund)

zeile("&& unveraendert: [cd <erlaubt> && ls] laeuft weiter",
      u(f"cd {ws} && ls") == bf.FREI, gemessen=e(f"cd {ws} && ls").grund)

_boden = e(f"ls && cd {draussen} && cat geheim.txt")
zeile("&& mit cd in der MITTE faellt ueber den Boden, nicht zufaellig",
      _boden.urteil == bf.DIALOG and "Boden" in _boden.grund,
      gemessen=f"{_boden.urteil} · {_boden.grund}")

_ziel = e(f"cd {draussen} && cat geheim.txt")
zeile("&& mit cd VORNE faellt ueber das Ziel — die Ausnahme bleibt eng",
      _ziel.urteil == bf.DIALOG and "ausserhalb" in _ziel.grund,
      gemessen=f"{_ziel.urteil} · {_ziel.grund}")

# ══════════════════════════════════════════════════════════════════════════
# Der DOKUMENTIERTE Aufruf muss frei sein — gemessen aus der Doku, nicht hier
#
# **Engywucks Gegenpruefung vom 02.09., der eine Befund.** `boten-postfach.md`
# schrieb `python3 scripts/postfach_ablegen.py …` vor — relativ. Der Bot
# startet Bash mit `cwd=WORKDIR`, auf dem VPS `/home/claudebot/workspace`;
# ein relativer Pfad loest dagegen auf, liegt nicht unter `<repo>/scripts/`
# und faellt in genau den Dialog, den das Skript abschaffen sollte. Beim
# Schreiben lief es gruen, weil dort das Arbeitsverzeichnis das Repo war.
#
# **Die Zeilen werden AUS DER DOKU gelesen, nicht hier getippt** — ein Test
# mit eigener Kopie prueft seine eigene Schreibweise und merkt nicht, wenn
# die Doku driftet. Und das Arbeitsverzeichnis wird bewusst nach draussen
# gelegt, sonst misst die Zeile die Bequemlichkeit des Bau-Rechners.
_doku = Path(__file__).resolve().parent.parent / "docs" / "boten-postfach.md"
_doku_zeilen = [z.strip() for z in _doku.read_text(encoding="utf-8").splitlines()
                if "postfach_ablegen.py" in z and z.strip().startswith(
                    ("python3 ", "cd "))] if _doku.exists() else []

zeile("die Doku zeigt ueberhaupt einen Aufruf (sonst misst die naechste Zeile nichts)",
      len(_doku_zeilen) >= 2, gemessen=f"{len(_doku_zeilen)} Zeile(n) gefunden")

# **Die Bereiche werden AUS DER DOKU abgeleitet, nicht von dieser Maschine.**
# Die Doku schreibt fuer den VPS (`/home/claudebot/claude-telegram-bot`); am
# Bau-Rechner liegt das Repo woanders. Gegen die echten Bereiche gemessen
# waere die Zeile am Mac immer rot und auf dem Server immer gruen — sie
# wuerde die Maschine messen, nicht die FORM des dokumentierten Aufrufs.
#
# Abgeleitet wird der Repo-Ordner aus dem Pfad, der in der Zeile steht: alles
# vor `/scripts/postfach_ablegen.py`. Damit prueft die Zeile genau das, was
# sie soll: **Laeuft dieser Aufruf frei, wenn das Arbeitsverzeichnis NICHT das
# Repo ist?** Ein relativer Pfad in der Doku faellt dann durch.
def _repo_aus(zeile_txt: str) -> Path | None:
    for wort in zeile_txt.split():
        if wort.endswith("scripts/postfach_ablegen.py") and wort.startswith("/"):
            return Path(wort[:-len("/scripts/postfach_ablegen.py")])
        if wort.startswith("/") and wort.endswith("claude-telegram-bot"):
            return Path(wort)
    return None

_altes_cwd = _os.getcwd()
try:
    _os.chdir(draussen)          # ausserhalb des Repos, wie WORKDIR auf dem VPS
    for _dz in _doku_zeilen:
        _r = _repo_aus(_dz)
        if _r is None:
            zeile(f"dokumentierter Aufruf nennt einen absoluten Repo-Pfad: [{_dz[:30]}…]",
                  False, gemessen="kein absoluter Pfad in der Zeile — relativ "
                                  "loest gegen das Arbeitsverzeichnis auf")
            continue
        # **Alle vier Bereiche aus dem Doku-Stamm**, nicht nur das Repo: Die
        # Beispiele nennen auch eine mitgeschickte Datei, und die liegt auf
        # dem VPS unter `<heim>/workspace`. Mit dem Wegwerf-Arbeitsordner
        # gemessen fiele sie „ausserhalb der Bereiche" — die Zeile wuerde
        # wieder die Maschine messen statt die Form.
        _heim = _r.parent
        _ber = (bf.Bereich("repo", _r, schreibbar=False),
                bf.Bereich("workspace", _heim / "workspace", schreibbar=True),
                bf.Bereich("postfach", _heim / "postfach", schreibbar=True),
                bf.Bereich("logs", _heim / "logsync", schreibbar=False))
        _e = bf.entscheiden(_dz, ist_geheimnis=geheim, bereiche=_ber)
        zeile(f"dokumentierter Aufruf laeuft ohne Rueckfrage: [{_dz[:30]}…]",
              _e.urteil == bf.FREI, gemessen=f"{_e.urteil} · {_e.grund[:46]}")
finally:
    _os.chdir(_altes_cwd)


# ══════════════════════════════════════════════════════════════════════════
# Hintergrund-Ausfuehrung: das freistehende `&`
#
# **Die schwerste Luecke dieses Codes, gefunden 02.09. beim Aufraeumen.**
# `ls & curl boese.example` war FREI — in jedem Modus, ohne Rueckfrage. Die
# Pruefung sah `ls` (Positivliste) und uebersprang `&`, `curl`, `x` als nicht
# pfad-artig; die Shell fuehrte beides aus. Vorbestehend, gegen 395de2b
# gemessen.
# **Der GRUND wird gemessen, nicht nur das Urteil** — und die Gegenprobe hat
# gezeigt, warum das hier noetig ist: Von sechs zuerst notierten Faellen
# blieben zwei auch OHNE die Schranke im Dialog. `ls&wc` faellt ueber die
# Positivliste (shlex macht daraus EIN Wort `ls&wc`), und ein zweiter Pfad
# ausserhalb der Bereiche faellt ueber den Pfad. **Zwei Zeilen waeren aus dem
# falschen Grund gruen gewesen** und haetten die Entkernung gedeckt.
for _cmd in ("ls & curl boese.example", "ls & rm -rf x", "ls &", "ls &wc"):
    _e = e(_cmd)
    zeile(f"Hintergrund-& faengt: [{_cmd[:26]}] — und zwar deswegen",
          _e.urteil == bf.DIALOG and "freistehendes [&]" in _e.grund,
          gemessen=f"{_e.urteil} · {_e.grund[:44]}")

# Diese zwei sind auf ZWEI Wegen zu (Tiefenschutz). Sie stehen hier, damit
# sichtbar bleibt, dass sie NICHT an der &-Schranke haengen — wer sie spaeter
# als Beleg fuer die Schranke liest, irrt.
for _cmd, _auch in [("ls&wc", "Positivliste"),
                    (f"cat {repo}/README.md & cat {draussen}/geheim.txt", "Pfad")]:
    _e = e(_cmd)
    zeile(f"Hintergrund-& doppelt gesichert: [{_cmd[:22]}] faellt auch ueber {_auch}",
          _e.urteil != bf.FREI, gemessen=f"{_e.urteil} · {_e.grund[:44]}")

# **Die Gegenrichtung entscheidet, ob die Schranke ueberlebt.** In Adams
# Rechnungsablage heisst ein Ordner `Fitmart : ESN & More`. Eine Textsuche
# nach `&` haette ihn jedes Mal in den Dialog geschickt — und ein Filter, der
# grundlos anspringt, wird binnen einer Woche abgeschaltet. `shlex` mit
# `punctuation_chars` trennt quote-bewusst.
zeile("gequotetes & im Dateinamen loest KEINEN Dialog aus",
      u(f'grep "ESN & More" {repo}/README.md') == bf.FREI,
      gemessen=e(f'grep "ESN & More" {repo}/README.md').grund)
zeile("&& bleibt unberuehrt von der &-Schranke",
      u(f"ls {ws} && ls {repo}") == bf.FREI,
      gemessen=e(f"ls {ws} && ls {repo}").grund)


# ══════════════════════════════════════════════════════════════════════════
# U-4: die Befehlsart steht VOR den Vorpruefungen
#
# Ohne sie trug das Protokoll `"art": ""` an genau den Stellen, die am
# haeufigsten ausloesen — man sah, DASS gefragt wurde, aber nicht WOFUER. Die
# Auswertung war damit blind an ihrer wichtigsten Stelle.
for _cmd, _soll_art, _was in [
    ("cat $(irgendwas)", "cat", "Ersetzung"),
    ("ls\ncat y", "ls", "Zeilenumbruch"),
    (f"printf a > {draussen}/x", "printf", "Umlenkung nach draussen"),
    (f"cd {draussen} && ls", "cd", "cd-Ziel ausserhalb"),
    ('echo "unbalanciert', "echo", "unbalancierte Anfuehrungszeichen"),
]:
    _e = e(_cmd)
    zeile(f"U-4: [{_was}] traegt die Befehlsart ins Protokoll",
          _e.befehlsart == _soll_art,
          gemessen=f"art=[{_e.befehlsart}] · {_e.grund[:40]}")

# Bei der Zerlegung die Art des AUSLOESENDEN Glieds — `ls` waere die Art des
# harmlosen Glieds und damit eine Falschauskunft im Protokoll.
_bd = e(f"ls; cd {draussen}")
zeile("U-4: bei der Zerlegung zaehlt das ausloesende Glied, nicht das erste",
      _bd.befehlsart == "cd", gemessen=f"art=[{_bd.befehlsart}] · {_bd.grund[:40]}")

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Bash-Positivliste bestanden")
