#!/usr/bin/env bash
# PreToolUse-Hook für Edit/Write auf MIGRATION.md / CLAUDE.md:
# blockiert den Schreibzugriff (Exit 2), wenn das Repo, in dem die Datei liegt,
# HINTER origin/mac-produktivstand steht — erst pullen, dann schreiben.
# Schützt vor veralteten/kollidierenden Sitzungsständen (CLAUDE.md → Führungs-Register).
set -uo pipefail

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null)

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
git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# Offline nicht blockieren (nur ohne frischen Abgleich weiterlassen).
git -C "$DIR" fetch origin --quiet 2>/dev/null || exit 0

BEHIND=$(git -C "$DIR" rev-list HEAD..origin/mac-produktivstand --count 2>/dev/null || echo 0)
if [ "${BEHIND:-0}" -gt 0 ]; then
  echo "BLOCKIERT (Führungs-Register): Die Kopie von $(basename "$FILE") in $DIR ist ${BEHIND} Commit(s) hinter origin/mac-produktivstand. Erst 'git pull origin mac-produktivstand' (bzw. in Nebensitzungen: NICHT schreiben, Änderungswunsch an die führende Migrations-Sitzung geben), dann erneut versuchen." >&2
  exit 2
fi
exit 0
