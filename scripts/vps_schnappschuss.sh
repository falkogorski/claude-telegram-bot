#!/usr/bin/env bash
# <!-- ROLLE: vps-schnappschuss -->
# ============================================================================
# Ein täglicher Schnappschuss, der OHNE den Mac auskommt.
#
# DIE LÜCKE, DIE ER SCHLIESST:
# Die Sicherung 4.1 zieht der MAC vom Server (täglich 12:30, launchd). Das
# funktioniert gut, solange der Mac läuft. Schläft er — geschlossener Deckel,
# Reise, Stromausfall —, holt launchd den Lauf erst NACH dem Aufwachen nach.
# In vierzehn Tagen Abwesenheit hieße das: vierzehn Tage lang keine Sicherung,
# und niemand, der es bemerkt. Betroffen wären ausgerechnet die Dateien, die
# nur hier liegen: das Gedächtnis, Adams eigene Offen-Liste, die Ampel-Regeln.
#
# WAS ER NICHT KANN — ehrlich, damit ihn niemand für mehr hält:
# Er liegt auf DERSELBEN MASCHINE wie das, was er sichert. Gegen ein
# versehentliches Überschreiben, eine kaputte Datei oder einen missratenen
# Eingriff hilft er. Gegen den Verlust des Servers hilft er NICHT — dafür ist
# und bleibt der Mac-Zug (4.1) zuständig, und beide zusammen ergeben erst eine
# Sicherung. Ein Schnappschuss neben dem Original ist ein Rückweg, kein Backup.
#
# ⚠️ NICHTS VERLÄSST DIE MASCHINE. Das Gedächtnis und `ampel_custom.json`
# enthalten Klienten-Namen; sie werden hier nur lokal zusammengepackt.
#
# Aufruf: bash scripts/vps_schnappschuss.sh
# Deterministisch, kein Modell-Aufruf, keine Kosten.
# ============================================================================
set -uo pipefail

ZIEL="${SCHNAPPSCHUSS_DIR:-${HOME:-/home/claudebot}/schnappschuesse}"
STAENDE="${SCHNAPPSCHUSS_STAENDE:-14}"     # ein Stand je Tag der Abwesenheit
HEUTE="$(date '+%Y%m%d')"
ARCHIV="$ZIEL/stand-$HEUTE.tar.gz"

mkdir -p "$ZIEL"
chmod 700 "$ZIEL"                          # wie rot behandeln: nur der Besitzer

# Was hineingehört: alles, was NUR hier liegt und nicht aus git kommt.
QUELLEN=()
for p in "${HOME:-/home/claudebot}/.claude/memory" \
         "${HOME:-/home/claudebot}/.claude/ampel_rules.toml" \
         "${HOME:-/home/claudebot}/.claude/ampel_custom.json" \
         "${HOME:-/home/claudebot}/.claude/hora" \
         "${HOME:-/home/claudebot}/.claude/stundenblumen" \
         "${HOME:-/home/claudebot}/postfach/freigaben" \
         "${HOME:-/home/claudebot}/.config/claude-telegram-bot"; do
  [ -e "$p" ] && QUELLEN+=("${p#${HOME:-/home/claudebot}/}")
done

if [ "${#QUELLEN[@]}" -eq 0 ]; then
  echo "❌ Nichts zu sichern gefunden — das ist selbst ein Befund."
  exit 1
fi

# Ein Zwischenschritt, damit ein abgebrochener Lauf keinen halben Stand
# hinterlässt, der beim Zurückholen wie ein vollständiger aussieht.
TMP="$ARCHIV.unfertig"
if tar -czf "$TMP" -C "${HOME:-/home/claudebot}" "${QUELLEN[@]}" 2>/dev/null; then
  mv "$TMP" "$ARCHIV"
  chmod 600 "$ARCHIV"
else
  rm -f "$TMP"
  echo "❌ Der Schnappschuss ist nicht zustande gekommen."
  exit 1
fi

# Alte Stände abräumen — aber erst NACHDEM der neue liegt. Andersherum stünde
# man nach einem Fehlschlag ohne alles da.
ls -1t "$ZIEL"/stand-*.tar.gz 2>/dev/null | tail -n +$((STAENDE + 1)) | while read -r alt; do
  rm -f "$alt"
done

anzahl="$(ls -1 "$ZIEL"/stand-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')"
groesse="$(du -sh "$ZIEL" 2>/dev/null | cut -f1)"
echo "✅ Stand $HEUTE gesichert ($(du -h "$ARCHIV" | cut -f1)); $anzahl Stände, $groesse gesamt"
