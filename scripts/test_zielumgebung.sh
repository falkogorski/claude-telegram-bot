#!/usr/bin/env bash
# <!-- ROLLE: test-zielumgebung -->
#
# DIE ZIELUMGEBUNG IST DIE PRUEFUMGEBUNG (Connis Auflage 2, 18.08.2026).
#
# BELEGTER VORFALL, 29.07. bis 18.08.2026 - einundzwanzig Tage:
# Der taegliche Vier-Uhr-Check starb bei JEDEM Lauf an einer Zeile mit $HOME.
# Das Skript laeuft mit `set -u` als root-Systemdienst; die Unit setzt kein
# `User=`, also liefert systemd kein HOME. Am Mac, wo jeder Entwickler prueft,
# ist HOME selbstverstaendlich gesetzt - dort lief alles.
#
# Kein Test hat es gefunden, weil kein Test die Skripte je GESTARTET hat. Es
# gab Textpruefer, die ihren Inhalt lasen. Ein `bash -n` und ein Start mit
# leerer Umgebung haetten den Fehler am ersten Tag gefunden.
#
# Dieser Pruefer macht genau das - und sonst nichts.
set -u
cd "$(dirname "$0")/.."

FAILS=0
GESAMT=0

melde() {
  GESAMT=$((GESAMT+1))
  if [ "$1" = "ok" ]; then echo "✓ $2"; else echo "✗ $2: $3"; FAILS=$((FAILS+1)); fi
}

# --- 1. Jedes Skript ist syntaktisch heil ------------------------------------
for f in scripts/*.sh; do
  [ "$f" = "scripts/test_zielumgebung.sh" ] && continue
  if ausgabe="$(bash -n "$f" 2>&1)"; then
    melde ok "Syntax: $(basename "$f")"
  else
    melde nein "Syntax: $(basename "$f")" "$ausgabe"
  fi
done

# --- 2. Kein bares $HOME in einem Skript mit `set -u` ------------------------
#
# Der Kern des Vorfalls. Gesucht wird das UNGESCHUETZTE $HOME - `${HOME:-...}`
# mit Rueckfall ist ausdruecklich erlaubt, denn der bricht nicht.
for f in scripts/*.sh; do
  [ "$f" = "scripts/test_zielumgebung.sh" ] && continue
  grep -q 'set -u' "$f" || continue
  # $HOME ohne folgendes ":-" und nicht als ${HOME:-...}
  # Kommentarzeilen zaehlen NICHT - der Erklaertext zu diesem Fehler enthaelt
  # das Wort selbst, und ein Pruefer, der die Beschreibung seines eigenen
  # Gegenstands anschlaegt, wird binnen einer Woche abgeschaltet.
  treffer="$(grep -nE '\$HOME([^A-Za-z_]|$)|\$\{HOME\}' "$f" | grep -v ':-' | grep -vE '^[0-9]+:[[:space:]]*#' || true)"
  if [ -z "$treffer" ]; then
    melde ok "kein ungeschuetztes \$HOME: $(basename "$f")"
  else
    melde nein "kein ungeschuetztes \$HOME: $(basename "$f")" \
      "$(echo "$treffer" | head -2 | tr '\n' ' ') — als root-Dienst ist HOME leer, set -u bricht ab"
  fi
done

# --- 3. Start WIE SYSTEMD: leere Umgebung, kein HOME -------------------------
#
# Die eigentliche Messung. Gestartet wird mit `env -i`, also genau so nackt,
# wie ein System-Dienst ohne `User=` startet. Geprueft wird nur, ob das Skript
# an einer FEHLENDEN VARIABLEN stirbt - dass es ohne Server, ohne venv und
# ohne Rechte nicht durchlaeuft, ist erwartbar und kein Befund.
for f in scripts/daily_check.sh scripts/api_cache_pflege.sh; do
  [ -f "$f" ] || continue
  ausgabe="$(env -i /bin/bash "$f" 2>&1 </dev/null | head -40 || true)"
  if echo "$ausgabe" | grep -q 'unbound variable'; then
    zeile="$(echo "$ausgabe" | grep -m1 'unbound variable')"
    melde nein "startet ohne HOME: $(basename "$f")" "$zeile"
  else
    melde ok "startet ohne HOME: $(basename "$f")"
  fi
done

# --- 3b. Python-Aufrufe des Tagescheck bekommen die Bot-Umgebung -------------
#
# GEMESSEN 18.08.2026 beim ersten echten Lauf: Der Tagescheck laeuft als root,
# `stundenblume.py` sucht ihre Kette unter `Path.home()` - also unter /root -
# und meldete "Es gibt noch keine Kette", obwohl sie lueckenlos lief. Ein
# TAEGLICHER FEHLALARM.
#
# Das ist die leise Schwester des $HOME-Fehlers: Python stuerzt nicht ab, es
# zeigt still woanders hin. Und die Wirkung ist womoeglich schlimmer - ein
# Waechter, der jeden Tag grundlos rot meldet, wird abgeschaltet.
if grep -q 'BOTENV=(env' scripts/daily_check.sh; then
  fehlend=""
  for aufruf in $(grep -oE '"\$VENVPY" "\$\(dirname "\$0"\)/[a-z_]+\.py"' scripts/daily_check.sh | sort -u); do
    :
  done
  # Jede Zeile, die VENVPY mit einem unserer Python-Skripte ruft, muss BOTENV tragen.
  fehlend="$(grep -nE '\$VENVPY" "\$\(dirname' scripts/daily_check.sh | grep -v 'BOTENV\[@\]' || true)"
  if [ -z "$fehlend" ]; then
    melde ok "Python-Aufrufe tragen die Bot-Umgebung"
  else
    melde nein "Python-Aufrufe tragen die Bot-Umgebung" \
      "$(echo "$fehlend" | head -2 | tr '\n' ' ') — als root zeigt Path.home() auf /root"
  fi
else
  melde nein "Python-Aufrufe tragen die Bot-Umgebung" "BOTENV ist nicht definiert"
fi

# --- 4. Der Tagescheck verliert bei einem Abbruch nichts Gemessenes ----------
#
# Connis Auflage 1. Geprueft wird die STRUKTUR, weil ein echter Abbruch hier
# nicht herstellbar ist: Es muss einen laufenden Mitschrieb geben, in den
# waehrend des Laufs geschrieben wird, und einen Trap, der ihn bei einem
# Abbruch sichert. Ohne beides gilt wieder: gemessen und weggeworfen.
if grep -q 'LAUFDATEI' scripts/daily_check.sh \
   && grep -q 'trap _abbruch EXIT' scripts/daily_check.sh \
   && grep -qE 'add\(\)\s*\{.*merken' scripts/daily_check.sh; then
  melde ok "Tagescheck schreibt Befunde beim Entstehen weg"
else
  melde nein "Tagescheck schreibt Befunde beim Entstehen weg" \
    "kein Mitschrieb oder kein Abbruch-Trap — ein Abbruch verliert wieder alles"
fi

echo "== Zielumgebung: $((GESAMT-FAILS))/$GESAMT bestanden =="
exit $FAILS
