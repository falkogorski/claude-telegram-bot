#!/bin/bash
# <!-- ROLLE: mac-videoarbeiter-einrichten -->
# Block 7, erster Schnitt: den Videoarbeiter einrichten (26.09.2026).
#
# **Adams Hand, einmal, am Mac** — und erst NACH dem Deploy, der `macauftrag.py`
# auf den Server bringt. Das Skript
#   1. erzeugt zwei Schluessel ohne Passwort (der Lauf ist unbeaufsichtigt;
#      was sie duerfen, begrenzt der Server, nicht das Passwort),
#   2. traegt sie beim Server ein, jeden an GENAU einen Ordner gebunden
#      (Engywucks Auflage: `rrsync`, `restrict` = kein Terminal, keine
#      Weiterleitung). Dafuer benutzt es EINMAL den vorhandenen Zugang als
#      claudebot, kein root,
#   3. prueft, dass die neuen Schluessel nichts anderes koennen (`ls ~` wird
#      abgelehnt),
#   4. faehrt einen Probeauftrag hin und zurueck,
#   5. stellt erst dann den Zeitgeber scharf (launchd, 30 Minuten + Anmelden).
# Jeder Schritt bricht bei einem Fehler ab; nichts wird halb scharf.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
RSYNC=/opt/homebrew/bin/rsync
PY=/opt/homebrew/bin/python3
HOLEN="$HOME/.ssh/videoarbeiter_holen"
BRINGEN="$HOME/.ssh/videoarbeiter_bringen"
PLIST="$HOME/Library/LaunchAgents/com.jakuna.videoarbeiter.plist"
LOG="$HOME/Library/Logs/videoarbeiter.log"

schritt() { printf '\n== %s ==\n' "$1"; }

schritt "1. Voraussetzungen"
[ -x "$RSYNC" ] || { echo "rsync aus Homebrew fehlt: brew install rsync"; exit 1; }
[ -x "$PY" ] || { echo "python3 aus Homebrew fehlt"; exit 1; }
ssh -o BatchMode=yes claudebot 'test -f ~/claude-telegram-bot/macauftrag.py' \
  || { echo "macauftrag.py liegt noch nicht auf dem Server — erst deployen"; exit 1; }
echo "ok"

schritt "2. Schluessel"
for k in "$HOLEN" "$BRINGEN"; do
  if [ ! -f "$k" ]; then
    ssh-keygen -q -t ed25519 -N "" -C "videoarbeiter-$(basename "$k" | cut -d_ -f2)@mac" -f "$k"
    echo "erzeugt: $k"
  else
    echo "vorhanden: $k"
  fi
done

schritt "3. Beim Server eintragen (als claudebot)"
PUB_HOLEN="$(cat "$HOLEN.pub")"
PUB_BRINGEN="$(cat "$BRINGEN.pub")"
# ssh fuegt die Argumente zu EINER Befehlszeile zusammen — ohne %q zerfiele
# jeder Schluessel an seinen Leerzeichen.
ssh -o BatchMode=yes claudebot \
  "bash -s -- $(printf '%q' "$PUB_HOLEN") $(printf '%q' "$PUB_BRINGEN")" <<'FERN'
set -euo pipefail
mkdir -p "$HOME/mac-auftraege" "$HOME/mac-ergebnisse"
chmod 700 "$HOME/mac-auftraege" "$HOME/mac-ergebnisse"
ak="$HOME/.ssh/authorized_keys"
eintragen() {
  local modus="$1" ordner="$2" pub="$3"
  local schluessel; schluessel="$(printf '%s' "$pub" | awk '{print $2}')"
  if grep -qF "$schluessel" "$ak"; then echo "schon eingetragen: $ordner"; return; fi
  printf 'restrict,command="/usr/bin/rrsync %s %s" %s\n' "$modus" "$HOME/$ordner" "$pub" >> "$ak"
  echo "eingetragen: $modus $ordner"
}
eintragen -ro mac-auftraege "$1"
eintragen -wo mac-ergebnisse "$2"
FERN

schritt "4. Gegenprobe: die neuen Schluessel koennen nichts anderes"
eval "$(ssh -G claudebot | awk '$1=="user"{print "U="$2} $1=="hostname"{print "H="$2} $1=="port"{print "P="$2}')"
for k in "$HOLEN" "$BRINGEN"; do
  aus="$(ssh -F /dev/null -i "$k" -o IdentitiesOnly=yes -o BatchMode=yes \
         -o UserKnownHostsFile="$HOME/.ssh/known_hosts" -p "$P" "$U@$H" 'ls ~' 2>&1 || true)"
  if printf '%s' "$aus" | grep -q "claude-telegram-bot"; then
    echo "ABBRUCH: $(basename "$k") darf eine Shell benutzen — der Eintrag greift nicht"; exit 1
  fi
  echo "$(basename "$k"): ls ~ abgelehnt ($(printf '%s' "$aus" | head -1))"
done

schritt "5. Probeauftrag hin und zurueck"
KENNUNG="$(ssh -o BatchMode=yes claudebot 'cd ~/claude-telegram-bot && .venv/bin/python macauftrag.py --probe')"
echo "abgelegt: $KENNUNG"
"$PY" "$REPO/scripts/mac/videoarbeiter.py"
STAND="$(ssh -o BatchMode=yes claudebot 'cd ~/claude-telegram-bot && .venv/bin/python macauftrag.py --stand')"
printf '%s\n' "$STAND"
printf '%s' "$STAND" | grep -q "$KENNUNG zurueckgekommen" \
  || { echo "ABBRUCH: der Probeauftrag kam nicht zurueck — Zeitgeber NICHT scharf"; exit 1; }

schritt "6. Zeitgeber scharfstellen"
mkdir -p "$(dirname "$PLIST")" "$(dirname "$LOG")"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.jakuna.videoarbeiter</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$REPO/scripts/mac/videoarbeiter.py</string></array>
  <key>StartInterval</key><integer>1800</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PL
launchctl bootout "gui/$(id -u)/com.jakuna.videoarbeiter" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "scharf: alle 30 Minuten und beim Anmelden. Protokoll: $LOG"
