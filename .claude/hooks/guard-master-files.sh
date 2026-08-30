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
INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('file_path', ''))
" 2>&1)
_RC=$?
if [ "$_RC" -ne 0 ]; then
  echo "BLOCKIERT (Führungs-Register): Die Anfrage liess sich nicht auswerten (python3 endete mit $_RC). Solange unklar ist, WELCHE Datei geschrieben wird, kann die Schranke nicht urteilen — und ein Ausfall darf nicht wie eine Freigabe aussehen. Meldung: ${FILE:-keine}" >&2
  exit 2
fi

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
_BASIS=$(basename "$FILE" | tr '[:upper:]' '[:lower:]')
case "$_BASIS" in
  migration.md|claude.md) ;;
  *) exit 0 ;;
esac

DIR=$(dirname "$FILE")

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
