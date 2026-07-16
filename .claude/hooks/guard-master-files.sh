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

case "$FILE" in
  */MIGRATION.md|*/CLAUDE.md|MIGRATION.md|CLAUDE.md) ;;
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
