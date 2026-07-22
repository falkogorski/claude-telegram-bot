#!/usr/bin/env bash
# ============================================================================
# Tägliches Backup: nur-auf-dem-VPS liegende Daten  →  Mac (rsync über SSH).
# Migrations-Punkt 4.1.
#
# Zieht per SSH vom VPS (Alias `claudevps` = root, kann alle Pfade lesen).
# SWITCH-FÄHIG: Ziel + Host über ~/.claude/vps-backup.conf überschreibbar
#   BACKUP_DIR="/Volumes/MiniPC/VPS-Backup"
#   VPS_SSH_HOST="claudevps"
#
# Aufruf:  vps_backup.sh            → echtes Backup
#          vps_backup.sh --dry-run  → nur anzeigen, was gesichert würde
# ============================================================================
set -uo pipefail

CONF="${VPS_BACKUP_CONF:-$HOME/.claude/vps-backup.conf}"
[ -f "$CONF" ] && . "$CONF"
BACKUP_DIR="${BACKUP_DIR:-$HOME/VPS-Backup}"
SSH_HOST="${VPS_SSH_HOST:-claudevps}"
DEST="$BACKUP_DIR/latest"
LOG="$BACKUP_DIR/backup.log"

mkdir -p "$DEST"/{etc,memory,ampel,logs,configs}
echo "=== VPS-Backup $(date '+%Y-%m-%d %H:%M:%S')  Host=$SSH_HOST  →  $DEST ===" >> "$LOG"

# Erreichbarkeit prüfen (Mac evtl. offline / VPS down → sauber abbrechen, kein Fehler).
if ! ssh -o BatchMode=yes -o ConnectTimeout=15 "$SSH_HOST" true 2>>"$LOG"; then
  echo "  VPS nicht erreichbar — Backup übersprungen." | tee -a "$LOG"
  exit 0
fi

RSYNC=(rsync -az --exclude='._*' --exclude='.DS_Store')
# rsync -az; Mac-rsync (2.6.9) kennt kein --ignore-missing-args → pro Pfad einzeln.
# --exclude: macOS-Müll nicht mitsichern — AppleDouble `._*` (stammten aus der
# tar-Migration Mac→VPS am 14.07., COPYFILE_DISABLE war nicht gesetzt) + `.DS_Store`.
[ "${1:-}" = "--dry-run" ] && RSYNC+=(-n --itemize-changes)

# Pfad|Zielgruppe. Jeder Pfad ein eigener rsync-Aufruf: eine fehlende Datei
# (z. B. ampel_custom.json bevor Adam Regeln anlegt) blockiert die anderen nicht.
ITEMS=(
  "/etc/claude-telegram-bot.env|etc"
  "/etc/claude-telegram-bot.token-issued|etc"
  "/home/claudebot/.claude/memory/|memory"
  "/home/claudebot/.claude/ampel_rules.toml|ampel"
  "/home/claudebot/.claude/ampel_custom.json|ampel"
  "/home/claudebot/claude-telegram-bot/logs/|logs"
  "/home/claudebot/searxng/settings.yml|configs"
  "/home/claudebot/litellm/config.yaml|configs"
)
for item in "${ITEMS[@]}"; do
  src="${item%%|*}"; grp="${item##*|}"
  if "${RSYNC[@]}" "$SSH_HOST:$src" "$DEST/$grp/" 2>>"$LOG"; then :; else
    echo "  (übersprungen/nicht vorhanden: $src)" >>"$LOG"
  fi
done

# Repo-Vollkopie als git bundle (Mini-Ergänzung 4.1, 22.07.): eine Datei =
# komplettes Repo samt Historie, datiert — Offline-Kopie unabhängig von allen
# drei Live-Klonen (schützt auch gegen „fehlerhafter Inhalt wird überall hin
# synchronisiert"). Rotation: die letzten 14 Bundles bleiben liegen.
REPO_DIR="${REPO_DIR:-$HOME/Projects/claude-telegram-bot}"
if [ -d "$REPO_DIR/.git" ] && [ "${1:-}" != "--dry-run" ]; then
  mkdir -p "$BACKUP_DIR/bundles"
  if git -C "$REPO_DIR" bundle create \
       "$BACKUP_DIR/bundles/claude-telegram-bot-$(date '+%Y%m%d').bundle" --all 2>>"$LOG"; then
    ls -t "$BACKUP_DIR/bundles"/claude-telegram-bot-*.bundle 2>/dev/null | tail -n +15 | xargs rm -f 2>/dev/null
    echo "  Repo-Bundle abgelegt (bundles/)." >>"$LOG"
  else
    echo "  Repo-Bundle fehlgeschlagen (siehe Log oben)." >>"$LOG"
  fi
fi

SIZE=$(du -sh "$DEST" 2>/dev/null | cut -f1)
echo "  fertig: $SIZE gesichert in $DEST" | tee -a "$LOG"
