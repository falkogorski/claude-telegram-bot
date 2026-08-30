#!/usr/bin/env bash
# PreToolUse-Hook für Edit/Write auf MIGRATION.md / CLAUDE.md:
# blockiert den Schreibzugriff (Exit 2), wenn das Repo, in dem die Datei liegt,
# HINTER origin/mac-produktivstand steht — erst pullen, dann schreiben.
# Schützt vor veralteten/kollidierenden Sitzungsständen (CLAUDE.md → Führungs-Register).
set -uo pipefail

# **[NEU 30.08.] Fail-closed: eine misslungene Auswertung blockiert.**
#
# Faecher-Funde [32] [41] [60] [61]. Der Dateipfad kam aus einem
# python3-Einzeiler mit `2>/dev/null`, und jeder Ausfall — kaputter Shim,
# dyld-Fehler, gedriftetes Eingabe-Schema, unlesbares JSON — endete in
# **exit 0 und leerer Ausgabe: exakt wie beim legitimen Durchlassen.**
# Nicht unterscheidbar. In zwei Fassungen dieses Hooks gab es keinen
# fail-closed-Zweig.
#
# Der Unterschied, auf den es ankommt:
#   gelungen + kein Pfad  -> anderes Werkzeug, durchlassen (haeufig, harmlos)
#   MISSLUNGEN            -> wir wissen nicht, was geschrieben wird -> Stopp
#
# Eine Schranke, deren Ausfall wie eine Freigabe aussieht, ist keine Schranke.
# **Auch das Einlesen ohne externes Programm** `[BERICHTIGT 30.08.]`.
# `INPUT=$(cat)` war die dritte Werkzeug-Abhaengigkeit im Erkennungspfad — und
# die heimtueckischste: Sie liess die Pruefzeile „ohne git blockiert der Hook"
# **gruen aus dem falschen Grund** durchgehen. Ohne `cat` scheiterte schon das
# Einlesen, der Hook blockierte, und niemand hat je den git-Zweig gemessen.
# Gefunden durch die Gegenprobe, nicht durch Nachdenken.
IFS= read -r -d '' INPUT || true

# **[BERICHTIGT 30.08., Engywucks Widerlegung Rang 0 ③]** — mein eigener
# fail-closed-Umbau hatte einen neuen fail-OPEN erzeugt.
#
# Die erste Fassung fing stderr mit `2>&1` ein, um es in die Meldung zu
# schreiben. **Damit klebte jede Bibliothekswarnung am Dateipfad.** Gemessen:
#
#   "/pfad/CLAUDE.md\nobjc[123]: warnung"  ->  basename ergibt eine
#   mehrzeilige Zeichenkette, das `case` trifft nicht  ->  DURCHGELASSEN
#
# Und genau der Auslöser, den meine eigene Commit-Nachricht nannte — ein
# kaputter Shim, ein dyld-Fehler — schreibt auf stderr und endet mit rc=0.
# **Der Schutz haengt am Rueckgabewert, nicht an der Meldung**; also wird
# stderr verworfen. Zwei Zeilen Text sind den Riss nicht wert.
FILE=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_name', ''))
print(d.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null)
_RC=$?
if [ "$_RC" -ne 0 ]; then
  echo "BLOCKIERT (Führungs-Register): Die Anfrage liess sich nicht auswerten (python3 endete mit $_RC). Solange unklar ist, WELCHE Datei geschrieben wird, kann die Schranke nicht urteilen — und ein Ausfall darf nicht wie eine Freigabe aussehen." >&2
  exit 2
fi

# Erste Zeile Werkzeugname, zweite Zeile Dateipfad — mehr darf nicht kommen.
#
# **Mit `read` statt `sed`**, und das ist kein Stilfrage: Mein erster Anlauf
# nahm `sed -n '1p'` — und fiel prompt in der eigenen Pruefzeile „ohne git
# blockiert der Hook" durch, weil in jenem PATH auch `sed` fehlt. Ich hatte
# `basename` und `tr` aus dem Pfad genommen und eine Zeile spaeter `sed` neu
# hineingesetzt: **derselbe Fehler, eine Zeile weiter.** `read` ist eingebaut.
{ IFS= read -r _WERKZEUG || true
  IFS= read -r _PFAD || true
  IFS= read -r _REST || true
} <<EOF
$FILE
EOF
if [ -n "$_REST" ]; then
  echo "BLOCKIERT (Führungs-Register): Die Auswertung lieferte mehr als Werkzeug und Pfad — da hat etwas mitgeschrieben. Ungeprueft wird nicht durchgelassen." >&2
  exit 2
fi

# **Das gedriftete Eingabe-Schema, jetzt wirklich gefasst.** Meine
# Commit-Nachricht zu A3 fuehrte diesen Fall als behoben auf, gebaut war nur
# der Zweig „python3 endete ungleich null" — eine Falschaussage in der eigenen
# Ablage, von Engywuck gefunden. Ein Schreib-Werkzeug OHNE Dateipfad gibt es
# nicht; kommt es doch, hat sich das Schema geaendert und niemand weiss mehr,
# was geschrieben wird. Andere Werkzeuge (Bash, Read …) haben legitim keinen.
case "$_WERKZEUG" in
  Edit|Write|MultiEdit|NotebookEdit)
    if [ -z "$_PFAD" ]; then
      echo "BLOCKIERT (Führungs-Register): $_WERKZEUG ohne Dateipfad — das Eingabe-Schema passt nicht mehr zu dieser Schranke." >&2
      exit 2
    fi ;;
esac
FILE="$_PFAD"

# **[BERICHTIGT 29.08., Engywucks Maschinen-Gleichstand, Fund ③]**
#
# Hier stand der Vergleich auf `$FILE` direkt. `case` in bash ist
# **schreibweisenempfindlich**, und wer nicht passt, faellt in `*) exit 0` —
# also **durchlassen**, nicht blockieren.
#
# Auf Adams Mac ist das Dateisystem schreibweisen-**un**empfindlich: Ein
# Zugriff auf `claude.md` trifft dieselbe Datei, umgeht aber beide Muster.
# **Damit war die dritte Schicht der Fuehrungs-Register-Absicherung
# ausgerechnet auf der Maschine loechrig, auf der die fuehrende Sitzung
# schreibt.** Fail-open statt fail-closed.
#
# Auf VPS und Container entstand kein Loch — dort existiert die Datei unter
# dem anderen Namen schlicht nicht. Genau die Sorte Divergenz, die Adams
# Gleichstands-Regel meint.
#
# Verglichen wird jetzt der **kleingeschriebene Dateiname**. `tr` statt
# `${VAR,,}`, weil `/bin/bash` auf macOS die Fassung 3.2 ist und die
# Kleinschreibungs-Erweiterung erst mit 4.0 kam — eine Loesung, die nur auf
# einer Maschine laeuft, waere hier besonders absurd.
# **[BERICHTIGT 30.08.] Ohne externe Werkzeuge** — Engywucks Rang 0 ③, zweiter
# Teil: Fehlte `basename` oder `tr`, blieb `_BASIS` leer und der Hook liess
# durch. Derselbe Ausfalltyp wie beim fehlenden `python3`, nur unbemerkt.
#
# Beides geht mit Bordmitteln: `${FILE##*/}` ist der Dateiname, und die
# Schreibweisen-Unabhaengigkeit traegt das Muster selbst. **Ein Erkennungspfad
# ohne aufgerufene Programme kann durch kein fehlendes Programm aufgehen.**
# (`[Cc]`-Klassen statt `${VAR,,}`, weil `/bin/bash` auf macOS die Fassung 3.2
# ist — dieselbe Ueberlegung wie beim `tr` zuvor, nur konsequenter.)
_BASIS=${FILE##*/}
case "$_BASIS" in
  [Mm][Ii][Gg][Rr][Aa][Tt][Ii][Oo][Nn].[Mm][Dd]) ;;
  [Cc][Ll][Aa][Uu][Dd][Ee].[Mm][Dd]) ;;
  *) exit 0 ;;
esac

# Auch hier Bordmittel statt `dirname` — dasselbe Argument wie oben. Der
# Sonderfall „Datei ohne Verzeichnisteil" wird zu „.", genau wie bei dirname.
DIR=${FILE%/*}
[ "$DIR" = "$FILE" ] && DIR="."

# **Fehlt git selbst, kann niemand urteilen** — auch das ist ein Ausfall und
# keine Freigabe. (Ein Verzeichnis OHNE Repo ist dagegen legitim: dort gibt es
# keine veraltete Kopie, die zu blockieren waere.)
command -v git >/dev/null 2>&1 || {
  echo "BLOCKIERT (Führungs-Register): git ist auf dieser Maschine nicht auffindbar — der Stand der Kopie laesst sich nicht pruefen." >&2
  exit 2
}
git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# **Ein FREMDES Projekt wird durchgelassen, und diese Zeile ist noetig.**
# Adam hat mehrere Projekte mit einer CLAUDE.md. Ohne diese Pruefung wuerde der
# fail-closed-Umbau unten dort JEDES Schreiben blockieren — der Waechter waere
# binnen eines Tages abgeschaltet. Fehlt der Zweig, ist es nicht dieses Repo.
git -C "$DIR" rev-parse --verify --quiet origin/mac-produktivstand >/dev/null 2>&1 || exit 0

# **Offline bleibt eine bewusste Ausnahme.** Ohne Netz zu blockieren hiesse,
# die ganze Arbeit an der Erreichbarkeit von GitHub aufzuhaengen. Der Vergleich
# laeuft dann gegen den letzten bekannten Stand — schlechter als frisch, aber
# besser als nichts, und es ist der einzige Zweig, der bewusst offen bleibt.
git -C "$DIR" fetch origin --quiet 2>/dev/null || true

# **Und der Vergleich selbst: misslungen heisst blockieren, nicht `echo 0`.**
# Vorher endete jeder Fehler von `rev-list` in einer gemeldeten Null — also in
# "die Kopie ist aktuell", der beruhigendsten aller Falschauskuenfte.
BEHIND=$(git -C "$DIR" rev-list HEAD..origin/mac-produktivstand --count 2>&1) || {
  echo "BLOCKIERT (Führungs-Register): Der Vergleich mit origin/mac-produktivstand ist misslungen: $BEHIND" >&2
  exit 2
}
case "$BEHIND" in
  ''|*[!0-9]*)
    echo "BLOCKIERT (Führungs-Register): Der Vergleich lieferte keine Zahl, sondern: $BEHIND" >&2
    exit 2 ;;
esac
if [ "$BEHIND" -gt 0 ]; then
  echo "BLOCKIERT (Führungs-Register): Die Kopie von $(basename "$FILE") in $DIR ist ${BEHIND} Commit(s) hinter origin/mac-produktivstand. Erst 'git pull origin mac-produktivstand' (bzw. in Nebensitzungen: NICHT schreiben, Änderungswunsch an die führende Migrations-Sitzung geben), dann erneut versuchen." >&2
  exit 2
fi
exit 0
