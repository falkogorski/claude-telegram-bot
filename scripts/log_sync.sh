#!/usr/bin/env bash
# ============================================================================
# Täglicher Gesprächs-Log-Sync ins private Log-Repo (Migrations-Punkt 4.2,
# Mini-Vorzug „Kontrollsitzung bekommt eigene Augen", 22.07.2026).
#
# Kopiert logs/conversations/ des Bots in den SEPARATEN Klon des privaten
# Nur-Log-Repos (claude-bot-logs) und pusht per Deploy-Key, der AUSSCHLIESSLICH
# auf dieses Log-Repo schreiben darf (github-logsync-Alias in ~/.ssh/config).
#
# 🔒 Governance bleibt gewahrt: Der Bot-Repo-Klon wird hier nur GELESEN —
# committet/gepusht wird ausschließlich ins Log-Repo. Ein kompromittierter
# Schlüssel könnte schlimmstenfalls Logs anfassen, nie den Bot-Code.
#
# Läuft täglich als systemd-Timer `claude-log-sync.timer` (User claudebot).
# ============================================================================
set -uo pipefail

SRC="${LOG_SYNC_SRC:-$HOME/claude-telegram-bot/logs/conversations}"
REPO="${LOG_SYNC_REPO:-$HOME/logsync/claude-bot-logs}"

[ -d "$SRC" ] || { echo "Quelle fehlt: $SRC"; exit 1; }
cd "$REPO" || { echo "Log-Repo-Klon fehlt: $REPO"; exit 1; }

# Fremde Änderungen (z. B. manuell im Web gelöschte Dateien) zuerst holen.
git pull --ff-only --quiet 2>/dev/null || true

mkdir -p conversations
rsync -a --exclude='._*' --exclude='.DS_Store' "$SRC/" conversations/

git add -A
if git diff --cached --quiet; then
  echo "Keine Log-Änderungen — nichts zu pushen."
  exit 0
fi
git commit -q -m "Log-Sync $(date '+%Y-%m-%d %H:%M')"
git push -q origin main && echo "Log-Sync gepusht: $(date '+%Y-%m-%d %H:%M')"
