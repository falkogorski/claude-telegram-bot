#!/usr/bin/env bash
# SessionStart-Hook (Führungs-Register, siehe CLAUDE.md):
# Banner + unübersehbare Warnung, wenn die Arbeitskopie hinter dem Master
# liegt oder unkommittete Änderungen an den Master-Dateien vorliegen.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

echo "🧭 Master-Branch: mac-produktivstand · Führende Sitzung: Migrations-Sitzung (siehe CLAUDE.md → Führungs-Register)"
echo "   Alle anderen Sitzungen: NUR LESEN — Änderungswünsche als Text an Adam/Migrations-Sitzung."

git fetch origin --quiet 2>/dev/null || { echo "   (offline — Remote-Abgleich übersprungen)"; exit 0; }

BEHIND=$(git rev-list HEAD..origin/mac-produktivstand --count 2>/dev/null || echo 0)
if [ "${BEHIND:-0}" -gt 0 ]; then
  echo ""
  echo "🚨🚨🚨 WARNUNG: Diese Arbeitskopie ist ${BEHIND} Commit(s) HINTER origin/mac-produktivstand! 🚨🚨🚨"
  echo "🚨 ERST 'git pull origin mac-produktivstand', BEVOR irgendetwas geschrieben wird."
fi

DIRTY=$(git status --porcelain -- MIGRATION.md CLAUDE.md 2>/dev/null)
if [ -n "$DIRTY" ]; then
  echo ""
  echo "🚨 WARNUNG: Unkommittete Änderungen an Master-Dateien (MIGRATION.md/CLAUDE.md):"
  echo "$DIRTY"
  echo "🚨 Vor weiterer Arbeit klären: committen (nur führende Sitzung!) oder verwerfen."
fi
exit 0
