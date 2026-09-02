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

# **[NEU 30.08.] HOME wird BENANNT eingefordert** (Faecher-Fund [19], A2).
# Unter `set -u` bricht `$HOME` ohne HOME mit "unbound variable" ab — auch
# innerhalb eines Rueckfalls wie `${VAR:-$HOME/x}`, denn dort wird $HOME
# expandiert, sobald VAR fehlt. Genau daran starb am 29.07. ein Waechter,
# einundzwanzig Tage unbemerkt. Diese Zeile macht daraus einen Abbruch mit
# Grund statt einer Fehlermeldung, die niemand einem fehlenden Zuhause
# zuordnet — und sie sichert alle folgenden $HOME-Stellen auf einmal.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"

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

# ---------------------------------------------------------------- Z-2 (03.09.)
#
# **Was sich aendert, wird gesichert — nicht, was jemand aufgezaehlt hat.**
#
# Adams Wort: *„beim Server-Backup natuerlich alle Ordner mitlaufen, die sich
# veraendert haben zumindest, sonst ist es ja kein vernuenftiges Backup."*
#
# `ITEMS` oben ist eine **Aufzaehlung** — die Bauform, die beim naechsten
# Ordner still versagt. Am 02.09. war es beinahe soweit: Ab dem 03.09. ist der
# Server die Stelle fuer Rechnungsnummern, und `workspace/rechnungen/daten/`
# mit Stammdaten und Nummernzaehler stand **nicht** in der Liste. Faellt der
# Zaehler weg, ist die naechste Rechnungsnummer geraten.
#
# **Ausschluesse statt Einschluesse, und die Fehlerrichtung ist der Grund:**
# Ein vergessener Ausschluss kostet Plattenplatz. Ein vergessener Einschluss
# verliert Daten. Ausgeschlossen wird nur, was **reproduzierbar** ist —
# gemessen am 03.09.: `vhd/` sind Einzelbilder einer Medienanalyse (212 MB),
# `.npy` ein Zwischenergebnis (12 MB), `.venv` ist neu installierbar.
BAEUME=(
  "/home/claudebot/workspace/|workspace"
  "/home/claudebot/postfach/|postfach"
)
# **`site-packages` statt `.venv` — eine Eigenschaft, kein Name.**
# Der erste Anlauf schloss `.venv` aus und mass trotzdem 1,1 GB: Unter
# `~/workspace/.nemo-test/` liegt eine Python-Umgebung, die schlicht anders
# heisst. **Dieselbe Falle wie bei jeder Aufzaehlung** — sie schuetzt, was
# darin steht, und nichts sonst. `site-packages` gibt es in JEDER
# Python-Umgebung, egal wie ihr Ordner heisst.
BAUM_AUS=(--exclude='site-packages' --exclude='__pycache__' --exclude='*.tmp'
          --exclude='vhd/' --exclude='*.npy' --exclude='node_modules'
          --exclude='*.so' --exclude='*.pyc')
for item in "${BAEUME[@]}"; do
  src="${item%%|*}"; grp="${item##*|}"
  if "${RSYNC[@]}" "${BAUM_AUS[@]}" "$SSH_HOST:$src" "$DEST/$grp/" 2>>"$LOG"; then
    echo "  Baum gesichert: $src" >>"$LOG"
  else
    echo "  (Baum uebersprungen/nicht vorhanden: $src)" >>"$LOG"
  fi
done
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
