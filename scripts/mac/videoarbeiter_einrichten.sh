#!/bin/bash
# <!-- ROLLE: mac-videoarbeiter-einrichten -->
# Block 7, erster Schnitt: den Videoarbeiter einrichten (26.09.2026).
#
# **Adams Hand, einmal, am Mac** — und erst NACH dem Deploy, der `macauftrag.py`
# auf den Server bringt. Das Skript
#   1. prueft die Voraussetzungen,
#   2. erzeugt zwei Schluessel ohne Passwort (der Lauf ist unbeaufsichtigt;
#      was sie duerfen, begrenzt der Server, nicht das Passwort),
#   3. traegt sie beim Server ein, jeden an GENAU einen Ordner gebunden
#      (Engywucks Auflage: `rrsync`; `restrict` = kein Terminal, keine
#      Weiterleitung; `-munge` = der Bringschluessel legt keine wirksamen
#      Links an). Dafuer benutzt es EINMAL den vorhandenen Zugang als
#      claudebot, kein root,
#   4. beweist, dass die neuen Schluessel nichts anderes koennen: `ls ~` muss
#      mit der Meldung von rrsync scheitern (ein gar nicht eingetragener
#      Schluessel scheitert anders und gilt NICHT als bestanden), der
#      Holschluessel darf nicht schreiben, der Bringschluessel nicht lesen,
#   5. legt den Arbeiter an einen festen Ort (nicht der Arbeitsbaum des Repos:
#      ein Zweigwechsel legte sonst den Weg still, eine unkommittierte
#      Aenderung an der Positivliste wirkte sofort),
#   6. faehrt einen Probeauftrag hin und zurueck — erledigt, nicht abgelehnt,
#   7. stellt erst dann den Zeitgeber scharf (launchd, 30 Minuten + Anmelden).
# Jeder Schritt bricht bei einem Fehler ab; nichts wird halb scharf.
# Ein zweiter Aufruf ist unschaedlich: Vorhandenes wird geprueft, nicht
# doppelt angelegt. Nach einer Aenderung am Arbeiter bringt ein zweiter Aufruf
# die neue Fassung an den festen Ort.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
RSYNC="${VIDEOARBEITER_RSYNC:-/opt/homebrew/bin/rsync}"
PY="${VIDEOARBEITER_PY:-/opt/homebrew/bin/python3}"
HOLEN="$HOME/.ssh/videoarbeiter_holen"
BRINGEN="$HOME/.ssh/videoarbeiter_bringen"
ORT="$HOME/Library/Application Support/videoarbeiter"
PLIST="$HOME/Library/LaunchAgents/com.jakuna.videoarbeiter.plist"
LOG="$HOME/Library/Logs/videoarbeiter.log"

schritt() { printf '\n== %s ==\n' "$1"; }
abbruch() { echo "ABBRUCH: $1 — Zeitgeber NICHT scharf"; exit 1; }

schritt "1. Voraussetzungen"
[ -x "$RSYNC" ] || abbruch "rsync aus Homebrew fehlt (brew install rsync)"
# Ohne Leitung: Unter `pipefail` machte `| head -1` aus dem SIGPIPE des
# rsync einen Fehlschlag — ein echtes rsync 3 galt dann als keines.
_v="$("$RSYNC" --version 2>&1 || true)"
case "$_v" in "rsync  version 3"*) ;; *) abbruch "$RSYNC ist kein rsync 3" ;; esac
[ -x "$PY" ] || abbruch "python3 aus Homebrew fehlt"
ssh -o BatchMode=yes claudebot 'test -f ~/claude-telegram-bot/macauftrag.py' \
  || abbruch "macauftrag.py liegt noch nicht auf dem Server — erst deployen"
echo "ok"

schritt "2. Schluessel"
mkdir -p "$HOME/.ssh"
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
mkdir -p "$HOME/mac-auftraege" "$HOME/mac-ergebnisse" "$HOME/.ssh"
chmod 700 "$HOME/mac-auftraege" "$HOME/mac-ergebnisse" "$HOME/.ssh"
ak="$HOME/.ssh/authorized_keys"
touch "$ak"; chmod 600 "$ak"
# Endet die Datei ohne Zeilenumbruch, klebte der neue Eintrag an die letzte
# Zeile — der Schluessel stuende dann im Kommentarfeld, nicht als Schluessel.
if [ -s "$ak" ] && [ -n "$(tail -c1 "$ak")" ]; then echo >> "$ak"; fi
eintragen() {
  local optionen="$1" pub="$2" soll schluessel
  soll="restrict,command=\"/usr/bin/rrsync $optionen\" $pub"
  schluessel="$(printf '%s' "$pub" | awk '{print $2}')"
  if grep -qxF "$soll" "$ak"; then echo "schon eingetragen: $optionen"; return; fi
  if grep -qF "$schluessel" "$ak"; then
    echo "ABBRUCH: dieser Schluessel steht schon mit ANDEREN Angaben in authorized_keys — bitte ansehen, nichts veraendert"
    exit 1
  fi
  printf '%s\n' "$soll" >> "$ak"
  echo "eingetragen: $optionen"
}
eintragen "-ro $HOME/mac-auftraege" "$1"
eintragen "-munge -wo $HOME/mac-ergebnisse" "$2"
FERN

schritt "4. Gegenprobe: die neuen Schluessel koennen nichts anderes"
eval "$(ssh -G claudebot | awk '$1=="user"{print "U="$2} $1=="hostname"{print "H="$2} $1=="port"{print "P="$2}')"
eng() {  # ssh mit GENAU diesem Schluessel, nie einem anderen
  printf '%s ' ssh -F /dev/null -o "IdentityFile=$1" -o IdentitiesOnly=yes \
    -o IdentityAgent=none -o BatchMode=yes -o "UserKnownHostsFile=$HOME/.ssh/known_hosts" -p "$P"
}
for k in "$HOLEN" "$BRINGEN"; do
  aus="$($(eng "$k") "$U@$H" 'ls ~' 2>&1 || true)"
  grep -q "SSH_ORIGINAL_COMMAND does not run rsync" <<< "$aus" \
    || abbruch "$(basename "$k"): 'ls ~' scheiterte nicht an rrsync, sondern: $(printf '%s' "$aus" | head -1)"
  echo "$(basename "$k"): ls ~ von rrsync abgelehnt"
done
_leer="$(mktemp -d)"
aus="$("$RSYNC" -rt -e "$(eng "$HOLEN")" "$_leer/" "$U@$H:./" 2>&1 || true)"
grep -q "read-only server is not allowed" <<< "$aus" \
  || abbruch "der Holschluessel darf schreiben: $(printf '%s' "$aus" | tail -1)"
echo "Holschluessel: schreiben abgelehnt"
aus="$("$RSYNC" -rt -e "$(eng "$BRINGEN")" "$U@$H:./" "$_leer/" 2>&1 || true)"
grep -q "write-only server is not allowed" <<< "$aus" \
  || abbruch "der Bringschluessel darf lesen: $(printf '%s' "$aus" | tail -1)"
echo "Bringschluessel: lesen abgelehnt"
rm -rf "$_leer"

schritt "5. Arbeiter an seinen festen Ort"
mkdir -p "$ORT"
cp "$REPO/scripts/mac/videoarbeiter.py" "$ORT/videoarbeiter.py"
git -C "$REPO" log -1 --format='%h %ad' --date=format:'%d.%m.%Y %H:%M' \
  -- scripts/mac/videoarbeiter.py > "$ORT/FASSUNG" 2>/dev/null || true
echo "abgelegt: $ORT/videoarbeiter.py ($(cat "$ORT/FASSUNG" 2>/dev/null))"

schritt "6. Probeauftrag hin und zurueck"
KENNUNG="$(ssh -o BatchMode=yes claudebot 'cd ~/claude-telegram-bot && .venv/bin/python macauftrag.py --probe')"
echo "abgelegt: $KENNUNG"
"$PY" "$ORT/videoarbeiter.py"
STAND="$(ssh -o BatchMode=yes claudebot 'cd ~/claude-telegram-bot && .venv/bin/python macauftrag.py --stand')"
printf '%s\n' "$STAND"
grep -q "$KENNUNG zurueckgekommen, erledigt (probe)" <<< "$STAND" \
  || abbruch "der Probeauftrag kam nicht erledigt zurueck"

schritt "7. Zeitgeber scharfstellen"
mkdir -p "$(dirname "$PLIST")" "$(dirname "$LOG")"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.jakuna.videoarbeiter</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>$ORT/videoarbeiter.py</string></array>
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
