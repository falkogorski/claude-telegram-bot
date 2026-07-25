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
# Läuft STÜNDLICH als systemd-Timer `claude-log-sync.timer` (User claudebot);
# umgestellt am 25.07.2026 von täglich. Wichtig: Die **Tages-Einteilung der
# Log-Dateien bleibt unverändert** — eine Datei je Tag, nur häufiger
# hochgeschoben. Adams Übersicht („einen ganzen Tag am Stück lesen können") ist
# ausdrücklich Teil der Vorgabe und darf nicht angetastet werden.
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

# Bot-eigenes Fehlerlog mitsyncen (5.15, 24.07.) — die Kontrollsitzung liest
# Fehler ohne journalctl-Zugriff. Liegt neben conversations/ (logs/bot-errors.log).
ERRLOG="${LOG_SYNC_ERRLOG:-$(dirname "$SRC")/bot-errors.log}"
if [ -f "$ERRLOG" ]; then
  cp "$ERRLOG" bot-errors.log
fi
# 8.1: tägliches Check-Protokoll mitsyncen (Kontrollsitzung sieht die 4-Uhr-Läufe).
CHECKLOG="${LOG_SYNC_CHECKLOG:-$(dirname "$SRC")/daily-check.log}"
if [ -f "$CHECKLOG" ]; then
  cp "$CHECKLOG" daily-check.log
fi
# 5.21: Versions-Monitor-Protokoll mitsyncen.
VLOG="${LOG_SYNC_VLOG:-$(dirname "$SRC")/version-monitor.log}"
if [ -f "$VLOG" ]; then
  cp "$VLOG" version-monitor.log
fi

# ---------------------------------------------------------------------------
# Claudias Ausarbeitungen mitnehmen (Adam & Conni, 25.07.2026)
#
# Warum: Was Claudia erarbeitet (PDFs, Markdown-Berichte), entstand bisher nur
# in ihrem Arbeitsordner auf dem VPS und erreichte niemanden außer Adam per
# Telegram — Conni konnte es nicht lesen, Adam musste es von Hand anhängen.
# Das ist dieselbe Klasse wie der Ablageweg-Grundsatz: Was keinen Weg aus dem
# Arbeitsordner hat, ist verloren.
#
# Streng abgegrenzt — mitgenommen wird NUR Erarbeitetes:
#   * ausschließlich Dokument-Endungen (.md, .pdf, .txt, .csv, .html)
#   * NICHT das Gedächtnis (liegt außerhalb, in ~/.claude/memory)
#   * NICHT Geheimnis-Pfade (Muster unten, hart ausgeschlossen)
#   * NICHT Arbeits-Zwischendateien (Punkt-Dateien, .tmp, CLAUDE.md des Kontexts)
# Eigener Unterordner, damit Logs und Ausarbeitungen sich nicht vermischen.
# ---------------------------------------------------------------------------
WORK="${LOG_SYNC_WORK:-$HOME/workspace}"
if [ -d "$WORK" ]; then
  mkdir -p ausarbeitungen
  rsync -a --prune-empty-dirs \
    --include='*/' \
    --include='*.md' --include='*.pdf' --include='*.txt' \
    --include='*.csv' --include='*.html' \
    --exclude='*' \
    --exclude='.*' --exclude='*.tmp' --exclude='CLAUDE.md' \
    --exclude='*secret*' --exclude='*token*' --exclude='*credential*' \
    --exclude='*passwor*' --exclude='*.env' --exclude='*key*' \
    "$WORK/" ausarbeitungen/ 2>/dev/null || true
fi


git add -A
if git diff --cached --quiet; then
  echo "Keine Log-Änderungen — nichts zu pushen."
  exit 0
fi
git commit -q -m "Log-Sync $(date '+%Y-%m-%d %H:%M')"
git push -q origin main && echo "Log-Sync gepusht: $(date '+%Y-%m-%d %H:%M')"
