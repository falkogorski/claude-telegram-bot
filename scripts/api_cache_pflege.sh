#!/usr/bin/env bash
# <!-- ROLLE: api-cache-pflege -->
# ============================================================================
# 5.34 — Aufräumen des Zwischenlagers des eigenen Bot-API-Servers.
#
# Warum es das gibt: Der Server legt jede heruntergeladene Datei ab. Bei
# 2-GB-Videos wächst das Lager zweistellig in Gigabyte. Ohne diese Pflege
# füllte sich die Platte still — und „still" ist genau das Wort, das in diesem
# Projekt für Ärger steht.
#
# Zwei Grenzen, bewusst getrennt:
#   * ALTER  — alles älter als CACHE_TAGE Tage geht weg (Vorgabe 7).
#   * MENGE  — reißt das Lager CACHE_DECKEL_GB, wird zusätzlich vom Ältesten
#              her gelöscht, bis es wieder darunter liegt.
#
# 🚦 Der Deckel wird GEPRÜFT, nicht nur gesetzt (Conni-Bedingung 25.07.):
# Dieses Skript gibt den Füllstand aus; der 4-Uhr-Check (8.1) liest ihn und
# meldet, wenn er reißt. Ein Deckel ohne Prüfer wäre wieder eine Bitte.
#
# 💾 Das Lager gehört NICHT ins Backup: `vps_backup.sh` sichert eine
# ausdrückliche Pfadliste, nicht den Baum — es landet also nur dort, wenn
# jemand es einträgt. Genau das soll niemand tun (Register-Warnung).
#
# Aufruf: bash scripts/api_cache_pflege.sh   (deterministisch, keine Kosten)
# ============================================================================
set -u
# Kein $HOME hier: Dieses Skript wird VOM Tagescheck gerufen und erbt dessen
# Umgebung - und der laeuft als root-Systemdienst ohne HOME. Mit `set -u` war
# das ein sofortiger Abbruch, und zwar VOR der eigenen Existenz-Wache eine
# Zeile weiter unten: Das Ergebnis war eine FALSCHE Meldung ueber ein volles
# Zwischenlager. (Belegt 29.07.-18.08.2026.)o pipefail

LAGER="${TELEGRAM_API_DIR:-/var/lib/telegram-bot-api}"
CACHE_TAGE="${CACHE_TAGE:-7}"
CACHE_DECKEL_GB="${CACHE_DECKEL_GB:-30}"
BERICHT="${CACHE_BERICHT:-${BOTHOME:-/home/claudebot}/.claude/api-cache.json}"

if [ ! -d "$LAGER" ]; then
  echo "Kein Zwischenlager unter $LAGER — der eigene Bot-API-Server läuft nicht."
  exit 0
fi

_belegt_mb() { du -sm "$LAGER" 2>/dev/null | awk '{print $1}'; }

vorher="$(_belegt_mb)"

# 1) Nach Alter
find "$LAGER" -type f -mtime "+${CACHE_TAGE}" -delete 2>/dev/null || true

# 2) Nach Menge — vom Ältesten her, bis der Deckel wieder hält.
deckel_mb=$(( CACHE_DECKEL_GB * 1024 ))
while [ "$(_belegt_mb)" -gt "$deckel_mb" ]; do
  aeltest="$(find "$LAGER" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | head -1 | cut -d' ' -f2-)"
  [ -n "$aeltest" ] || break
  rm -f "$aeltest" 2>/dev/null || break
done

nachher="$(_belegt_mb)"
reisst=false
[ "$nachher" -gt "$deckel_mb" ] && reisst=true

mkdir -p "$(dirname "$BERICHT")"
cat > "$BERICHT" <<JSON
{
  "zeit": "$(date '+%Y-%m-%d %H:%M')",
  "lager": "$LAGER",
  "belegt_mb": ${nachher:-0},
  "deckel_mb": ${deckel_mb},
  "vorher_mb": ${vorher:-0},
  "deckel_gerissen": ${reisst}
}
JSON

echo "Zwischenlager: ${vorher:-0} MB → ${nachher:-0} MB (Deckel ${deckel_mb} MB)"
if [ "$reisst" = true ]; then
  echo "⚠️ Deckel gerissen — auch nach dem Aufräumen zu groß."
  exit 1
fi
exit 0
