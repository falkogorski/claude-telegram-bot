#!/bin/bash
# <!-- ROLLE: node-vollzug-pruefer -->
#
# Die sechs Pruefschritte des Node-Sprungs — ausfuehrbar statt als Text.
#
# **Engywucks Auflage ③ vom 29.08.:** Die Liste stand im Zettel als Prosa.
# Adam haette sechs Befehle von Hand tippen und die Ergebnisse **selbst
# vergleichen** muessen — mit Augenmass, waehrend der Dienst steht. Genau die
# Lage, in der man das Entscheidende uebersieht.
#
# Jetzt zwei Aufrufe:
#
#     bash scripts/node_vollzug_pruefen.sh vorher     # zeichnet auf
#     <Adams zwei root-Befehle: nodesource 24, apt-get install nodejs>
#     bash scripts/node_vollzug_pruefen.sh nachher    # misst und VERGLEICHT
#
# **Was verglichen wird, ist der Punkt:** Nicht [sieht gut aus], sondern jede
# einzelne Groesse gegen ihren eigenen Wert von vorher.
#
# ## Was dieses Skript NICHT tut
#
# Es springt nicht. Kein apt, keine Paketquelle, kein npm — der Vollzug bleibt
# Adams Hand, weil er root braucht und auf der Maschine laeuft, die den Bot
# rund um die Uhr traegt.

set -u

# **[NEU 30.08.] HOME wird BENANNT eingefordert** (Faecher-Fund [19], A2).
# Unter `set -u` bricht `$HOME` ohne HOME mit "unbound variable" ab — auch
# innerhalb eines Rueckfalls wie `${VAR:-$HOME/x}`, denn dort wird $HOME
# expandiert, sobald VAR fehlt. Genau daran starb am 29.07. ein Waechter,
# einundzwanzig Tage unbemerkt. Diese Zeile macht daraus einen Abbruch mit
# Grund statt einer Fehlermeldung, die niemand einem fehlenden Zuhause
# zuordnet — und sie sichert alle folgenden $HOME-Stellen auf einmal.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAND="${NODE_PRUEF_STAND:-$HOME/.claude/node-vollzug-vorher.txt}"
MODUS="${1:-}"

if [ "$MODUS" != "vorher" ] && [ "$MODUS" != "nachher" ]; then
  echo "Aufruf: $0 vorher | nachher" >&2
  exit 64
fi

# --- Die Messung. **Eine Funktion fuer beide Laeufe** — zwei getrennte waeren
#     zwei Wahrheiten, und die driften, sobald jemand nur eine anfasst.
messen() {
  echo "node=$(node --version 2>/dev/null || echo FEHLT)"
  echo "npm=$(npm --version 2>/dev/null || echo FEHLT)"
  # Die CLI, die ein MENSCH im Terminal bekommt.
  echo "claude_system=$(claude --version 2>/dev/null | head -1 || echo FEHLT)"
  # Die CLI, die der BOT startet — das ist die gebuendelte, und sie ist die
  # betriebsrelevante. Beide getrennt zu messen ist der Kern: Sie sind
  # verschieden, und nur die zweite traegt den Betrieb.
  echo "claude_bot=$(cd "$REPO" && .venv/bin/python -c "
from claude_agent_sdk._internal.transport.subprocess_cli import SubprocessCLITransport as T
import subprocess
p = T._find_cli(T.__new__(T))
print(subprocess.run([p,'--version'],capture_output=True,text=True).stdout.strip())
" 2>/dev/null || echo FEHLT)"
  echo "pandoc=$(pandoc --version 2>/dev/null | head -1 || echo FEHLT)"
  echo "dienst=$(systemctl is-active claude-telegram-bot 2>/dev/null || echo unbekannt)"
  # Die Doppelinstallation aus dem Zettel: Ein globales npm-Update kann je
  # nach Praefix nur einen der beiden Orte erwischen. Dann zeigt der Verweis
  # auf die alte Fassung, waehrend die Anzeige etwas Plausibles sagt — ein
  # Update, das aussieht, als haette es gewirkt.
  for ort in /usr/lib /usr/local/lib; do
    d="$ort/node_modules/@anthropic-ai/claude-code/package.json"
    if [ -f "$d" ]; then
      echo "md5_${ort//\//_}=$(md5sum "$d" 2>/dev/null | cut -d" " -f1)"
    else
      echo "md5_${ort//\//_}=FEHLT"
    fi
  done
  echo "symlink=$(readlink -f /usr/local/bin/claude 2>/dev/null || echo FEHLT)"
}

if [ "$MODUS" = "vorher" ]; then
  mkdir -p "$(dirname "$STAND")"
  messen > "$STAND"
  echo "Ist-Stand aufgezeichnet in $STAND:"
  sed "s/^/  /" "$STAND"
  echo
  echo "Jetzt der Sprung (Adams zwei Befehle, als root):"
  echo "  curl -fsSL https://deb.nodesource.com/setup_24.x | bash -"
  echo "  apt-get install -y nodejs"
  echo
  echo "Danach: bash scripts/node_vollzug_pruefen.sh nachher"
  exit 0
fi

# ---------------------------------------------------------------- nachher
if [ ! -f "$STAND" ]; then
  echo "🔴 Kein Vorher-Stand unter $STAND." >&2
  echo "   Ohne ihn ist ein Vergleich unmoeglich — und ein Vergleich gegen" >&2
  echo "   nichts sieht aus wie ein bestandener. Erst [vorher] fahren." >&2
  exit 78
fi

NEU="$(messen)"
FEHLER=0

hole() { printf '%s\n' "$2" | grep "^$1=" | head -1 | cut -d= -f2-; }

pruefe() {   # name | erwartet: gleich | anders | aktiv
  schluessel="$1"; erwartung="$2"; klartext="$3"
  alt="$(hole "$schluessel" "$(cat "$STAND")")"
  neu="$(hole "$schluessel" "$NEU")"
  case "$erwartung" in
    gleich)
      if [ "$alt" = "$neu" ]; then echo "  ✅ $klartext: unveraendert ($neu)"
      else echo "  ❌ $klartext: WAR [$alt], IST [$neu]"; FEHLER=$((FEHLER+1)); fi ;;
    anders)
      if [ "$alt" != "$neu" ] && [ "$neu" != "FEHLT" ]; then
        echo "  ✅ $klartext: $alt → $neu"
      else echo "  ❌ $klartext: unveraendert ($neu) — der Sprung hat nicht gewirkt"
        FEHLER=$((FEHLER+1)); fi ;;
    aktiv)
      if [ "$neu" = "active" ]; then echo "  ✅ $klartext: laeuft"
      else echo "  ❌ $klartext: [$neu]"; FEHLER=$((FEHLER+1)); fi ;;
  esac
}

echo "== Node-Vollzug: Vergleich gegen den Stand von vorher =="
pruefe node    anders "Node-Fassung"
pruefe npm     anders "npm"
pruefe claude_bot    gleich "CLI, die der BOT startet (gebuendelt)"
pruefe claude_system gleich "CLI im System (npm-global)"
pruefe pandoc  gleich "pandoc"
pruefe dienst  aktiv  "Bot-Dienst"
pruefe md5__usr_lib       gleich "claude-code unter /usr/lib"
pruefe md5__usr_local_lib gleich "claude-code unter /usr/local/lib"
pruefe symlink gleich "Ziel von /usr/local/bin/claude"

echo
echo "-- und der Nachweis, den die neun Zeilen oben NICHT ersetzen --"
(cd "$REPO" && bash scripts/regressionstest.sh >/tmp/nodevollzug.log 2>&1); _rc=$?
# Drei Zustaende (Rang 1, 30.08.): 77 = gruen, aber nicht alles gemessen.
# „Vollzug sauber" darf das nicht heissen — gemessen wurde ja gerade nicht.
if [ "$_rc" -eq 77 ]; then
  echo "  ⏭️  Regressionslauf UNVOLLSTAENDIG: $(grep '== Ergebnis:' /tmp/nodevollzug.log | tail -1)"
  grep 'uebersprungen —' /tmp/nodevollzug.log | tail -1 | sed 's/^/     /'
  echo "     (kein Vollzugsnachweis — hier wurde nicht alles gemessen)"
  FEHLER=$((FEHLER+1))
elif [ "$_rc" -eq 0 ]; then
  # Die Bilanzzeile, nicht die letzte — seit dem 30.08. kann darunter noch
  # eine Uebersprungszeile stehen.
  echo "  ✅ Regressionslauf: $(grep '== Ergebnis:' /tmp/nodevollzug.log | tail -1)"
  grep 'uebersprungen —' /tmp/nodevollzug.log | tail -1 | sed 's/^/     /'
else
  echo "  ❌ Regressionslauf ROT: $(tail -1 /tmp/nodevollzug.log)"
  echo "     (voller Mitschrieb: /tmp/nodevollzug.log)"
  FEHLER=$((FEHLER+1))
fi

echo
echo "  ℹ️  Ein echter Modell-Lauf ueber den Bot bleibt Adams Handgriff:"
echo "     eine Nachricht, eine Antwort. **Alle Zeilen oben koennen gruen"
echo "     sein, waehrend genau das nicht geht** — deshalb steht es hier."

echo
if [ $FEHLER -eq 0 ]; then
  echo "== Vollzug sauber: alles wie erwartet =="
  exit 0
fi
echo "== $FEHLER Abweichung(en) — der Rueckweg steht im Zettel =="
echo "   curl -fsSL https://deb.nodesource.com/setup_22.x | bash -"
echo "   apt-get install -y --allow-downgrades nodejs=22.23.1-1nodesource1"
exit 1
