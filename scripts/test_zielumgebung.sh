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

# **[NEU 30.08.] Ein dritter Zustand: uebersprungen.**
#
# Faecher-Funde [47] und [62]. Drei Zeilen ueber der Stelle stand im eigenen
# Kommentar der Satz "ein uebersprungener Pruefer, der wie ein bestandener
# aussieht, ist schlimmer als keiner" — und genau darunter meldete
# `melde ok "... uebersprungen"` den Uebersprung als bestanden.
#
# **Die Folge war die fehlende Zahlendifferenz:** Mac und Zielumgebung kamen
# beide auf 24/24, obwohl auf dem Mac eine Pruefung nie lief. Ein Tagescheck,
# der nichts mehr ablegt, waere hier nicht aufgefallen — dieselbe Lage wie beim
# einundzwanzig Tage toten Waechter, gegen den diese Datei gebaut wurde.
UEBERSPRUNGEN=0
melde() {
  GESAMT=$((GESAMT+1))
  case "$1" in
    ok)   echo "✓ $2" ;;
    skip) echo "⏭️  $2: $3"; UEBERSPRUNGEN=$((UEBERSPRUNGEN+1)) ;;
    *)    echo "✗ $2: $3"; FAILS=$((FAILS+1)) ;;
  esac
}

# **[NEU 30.08.] Die Menge, gebildet ueber eine EIGENSCHAFT** (A2, Funde
# [19] [64] [33]).
#
# Alle drei Schleifen sahen `scripts/*.sh` — nicht rekursiv, nicht die
# Repo-Wurzel. Draussen lagen sieben versionierte Skripte, darunter **alle
# drei Hooks unter `.claude/hooks/`**. Das ist bitter: Der Pruefer, der genau
# gegen den 29.07.-Fehler gebaut wurde (`$HOME` in einem Dienst ohne HOME, ein
# Waechter einundzwanzig Tage tot), sah ausgerechnet die Hooks nicht.
#
# **Jede Pruefung laeuft ueber eine Menge — und es ist immer die, die dem
# Erbauer am Bautag einfiel.** Deshalb hier keine Aufzaehlung und kein
# Verzeichnismuster, sondern die Frage an git: was ist versioniert und endet
# auf `.sh`? Ohne git (ausgepacktes Archiv) traegt `find` denselben Gedanken.
if SKRIPTE="$(git ls-files '*.sh' 2>/dev/null)" && [ -n "$SKRIPTE" ]; then
  :
else
  SKRIPTE="$(find . -name '*.sh' -not -path './.venv/*' -not -path './.git/*' \
             | sed 's|^\./||')"
fi

# --- 1. Jedes Skript ist syntaktisch heil ------------------------------------
SYNTAX_GEPRUEFT=0
for f in $SKRIPTE; do
  [ "$f" = "scripts/test_zielumgebung.sh" ] && continue
  SYNTAX_GEPRUEFT=$((SYNTAX_GEPRUEFT+1))
  if ausgabe="$(bash -n "$f" 2>&1)"; then
    melde ok "Syntax: $(basename "$f")"
  else
    melde nein "Syntax: $(basename "$f")" "$ausgabe"
  fi
done

# **Die Menge prueft sich selbst** (A2, 30.08.). Ohne diese Zeile waere die
# Weitung ungeprueft: Wer `$SKRIPTE` morgen wieder auf ein Verzeichnismuster
# setzt, bekaeme weiterhin lauter gruene Zeilen — nur eben weniger davon, und
# **eine fehlende Zeile faellt niemandem auf.** Genau so lagen die drei Hooks
# fuenf Wochen ausserhalb.
_alle_skripte="$(git ls-files '*.sh' 2>/dev/null | grep -c . || echo 0)"
if [ "$_alle_skripte" -gt 0 ]; then
  if [ "$((SYNTAX_GEPRUEFT+1))" -eq "$_alle_skripte" ]; then
    melde ok "die Menge ist vollstaendig ($_alle_skripte versionierte Skripte)"
  else
    melde nein "die Menge ist vollstaendig" \
      "geprueft $((SYNTAX_GEPRUEFT+1)) von $_alle_skripte versionierten Skripten - welche fehlen?"
  fi
else
  melde skip "die Menge ist vollstaendig" "ohne git nicht vergleichbar"
fi

# --- 2. Kein bares $HOME in einem Skript mit `set -u` ------------------------
#
# Der Kern des Vorfalls. Gesucht wird das UNGESCHUETZTE $HOME - `${HOME:-...}`
# mit Rueckfall ist ausdruecklich erlaubt, denn der bricht nicht.
HOME_GEPRUEFT=0
for f in $SKRIPTE; do
  [ "$f" = "scripts/test_zielumgebung.sh" ] && continue
  grep -q 'set -u' "$f" || continue
  HOME_GEPRUEFT=$((HOME_GEPRUEFT+1))
  # **[GEAENDERT 30.08.] Der Filter warf zu viel weg** (Fund [64]): `grep -v
  # ':-'` verwarf JEDE Zeile mit einem Rueckfall — auch `${VAR:-$HOME/x}`.
  # Dort wird $HOME aber expandiert, sobald VAR fehlt, und bricht unter
  # `set -u` genauso wie ein bares $HOME. Fuenf der sechs heute gefundenen
  # Stellen hatten genau diese Form; der alte Filter sah keine davon.
  #
  # Richtig ist die Unterscheidung: `${HOME:-...}` schuetzt HOME selbst und
  # ist erlaubt — deshalb wird nur DIESE Form vorher herausgeschnitten. Und
  # ein Skript, das HOME am Anfang mit `${HOME:?...}` einfordert, ist
  # ebenfalls sicher: Es bricht dann mit einem GRUND ab statt mit
  # "unbound variable" irgendwo in der Mitte.
  # **Nur in Code-Zeilen, nicht im ganzen Text** (Rang 3): Die Suche lief
  # ueber die ganze Datei — ein Kommentar, der `HOME:?` erwaehnt, haette
  # genuegt, um das Skript als abgesichert zu fuehren. Genau die Sorte
  # Selbsttaeuschung, die dieser Pruefer verhindern soll.
  if grep -vE '^[[:space:]]*#' "$f" | grep -q 'HOME:?'; then
    melde ok "HOME abgesichert: $(basename "$f")"
    continue
  fi
  # Kommentarzeilen zaehlen NICHT - der Erklaertext zu diesem Fehler enthaelt
  # das Wort selbst, und ein Pruefer, der die Beschreibung seines eigenen
  # Gegenstands anschlaegt, wird binnen einer Woche abgeschaltet.
  treffer="$(sed 's/${HOME:-[^}]*}//g' "$f" \
             | grep -nE '\$HOME([^A-Za-z_]|$)|\$\{HOME\}' \
             | grep -vE '^[0-9]+:[[:space:]]*#' || true)"
  if [ -z "$treffer" ]; then
    melde ok "kein ungeschuetztes \$HOME: $(basename "$f")"
  else
    melde nein "kein ungeschuetztes \$HOME: $(basename "$f")" \
      "$(echo "$treffer" | head -2 | tr '\n' ' ') — als root-Dienst ist HOME leer, set -u bricht ab"
  fi
done

# **Und Schleife 2 prueft ihre Menge ebenfalls** (Rang 3, zweiter Teil): Die
# Zeile oben bewachte nur Schleife 1. Wer `$SKRIPTE` hier durch etwas anderes
# ersetzt, bekaeme weiterhin gruene Zeilen — nur weniger davon.
_mit_set_u="$(for f in $SKRIPTE; do
                [ "$f" = "scripts/test_zielumgebung.sh" ] && continue
                grep -q 'set -u' "$f" && echo x
              done | grep -c . || echo 0)"
if [ "$HOME_GEPRUEFT" -eq "$_mit_set_u" ] && [ "$HOME_GEPRUEFT" -gt 0 ]; then
  melde ok "die HOME-Pruefung sah alle $_mit_set_u Skripte mit set -u"
else
  melde nein "die HOME-Pruefung sah alle Skripte mit set -u" \
    "geprueft $HOME_GEPRUEFT von $_mit_set_u - welche fehlen?"
fi

# --- 3. Start WIE SYSTEMD: leere Umgebung, kein HOME -------------------------
#
# Die eigentliche Messung. Gestartet wird mit `env -i`, also genau so nackt,
# wie ein System-Dienst ohne `User=` startet. Geprueft wird nur, ob das Skript
# an einer FEHLENDEN VARIABLEN stirbt - dass es ohne Server, ohne venv und
# ohne Rechte nicht durchlaeuft, ist erwartbar und kein Befund.
# DREI RIEGEL, damit dieser Start nichts nach aussen tut (21.08.):
#
#   TROCKENLAUF=1          - der Schalter an den drei Ausgaengen des Tagescheck
#   AUFTRAGSBUCH_DIR=...   - die Umleitung, falls der Schalter je verrutscht
#   TELEGRAM_BOT_TOKEN=""  - kein Versand, auch wenn beides versagt
#   ALLOWED_USER_IDS=""    - und niemand, an den gesendet werden koennte
#
# Warum vier Zeilen fuer eine Sache: Gemessen am 21.08. lief dieser Start heute
# schon ins Leere - aber nur, weil ihm die DATEIRECHTE fehlten. Als root
# gestartet haette er in Adams echte Ablagen geschrieben. Das war Zufall; hier
# steht die Zusage.
_wegwerf="${TMPDIR:-/tmp}/zielumgebung-buch.$$"
mkdir -p "$_wegwerf"
# **[ERWEITERT 30.08.] Diese Liste bleibt kurz — und das ist eine Entscheidung,
# keine Nachlaessigkeit** (zu Fund [33]).
#
# Schleife 1 und 2 laufen jetzt ueber ALLE versionierten Skripte, weil sie
# nichts tun ausser lesen. Diese hier **startet** die Skripte. Ein Start ist
# eine Handlung, und sie trifft nicht jedes Skript gefahrlos: `guardian.sh`
# startet den Bot neu, `mail_konto_anlegen.sh` legt Zugaenge an. Eine Menge
# ueber alle Skripte waere hier kein besserer Pruefer, sondern ein Eingriff.
#
# Aufgenommen ist deshalb, was **zeitgesteuert ohne Mensch** laeuft — genau die
# Lage des 29.07.-Vorfalls. `log_sync.sh` fehlte bisher, obwohl es stuendlich
# als Timer laeuft; das war eine echte Luecke. Die statische $HOME-Pruefung
# oben deckt alle uebrigen ab, ohne sie anzufassen.
for f in scripts/daily_check.sh scripts/api_cache_pflege.sh scripts/log_sync.sh; do
  [ -f "$f" ] || continue
  ausgabe="$(env -i TROCKENLAUF=1 "AUFTRAGSBUCH_DIR=$_wegwerf" \
                 TELEGRAM_BOT_TOKEN= ALLOWED_USER_IDS= \
                 /bin/bash "$f" 2>&1 </dev/null | head -40 || true)"
  # **[GESCHAERFT 30.08., Engywucks Widerlegung Rang 3]** Diese Zeile suchte
  # nur den Wortlaut `unbound variable`. Meine eigene Reparatur vom selben Tag
  # hat sie damit blind gemacht: `${HOME:?...}` bricht mit einer ANDEREN
  # Meldung ab — die Zeile wurde gruen, und ein Skript, das in der Zielumgebung
  # sofort mit rc=1 stirbt, galt als abgesichert.
  #
  # **Der Unterschied, auf den es ankommt, ist nicht Abbruch gegen Durchlauf,
  # sondern KRYPTISCH gegen BENANNT.** Ein Skript ohne HOME kann seine Pfade
  # nicht bilden; dass es abbricht, ist richtig. Falsch war nur, dass niemand
  # dem Abbruch ansah, woran er lag. Also wird beides gemessen: kein
  # `unbound variable` UND, falls es abbricht, ein Grund im Klartext.
  if echo "$ausgabe" | grep -q 'unbound variable'; then
    zeile="$(echo "$ausgabe" | grep -m1 'unbound variable')"
    melde nein "startet ohne HOME: $(basename "$f")" "$zeile"
  elif echo "$ausgabe" | grep -q 'HOME ist nicht gesetzt'; then
    melde ok "bricht ohne HOME mit GRUND ab: $(basename "$f")"
  else
    melde ok "startet ohne HOME: $(basename "$f")"
  fi
done
# Nachweis statt Vertrauen: Hat der Start trotz aller Riegel etwas abgelegt?
if [ -n "$(ls -A "$_wegwerf" 2>/dev/null)" ]; then
  melde nein "Trockenlauf legt nichts ab" "$(ls -A "$_wegwerf" | head -3 | tr '\n' ' ')"
else
  melde ok "Trockenlauf legt nichts ab"
fi
rm -rf "$_wegwerf"

# --- 3c. Der NORMALFALL (Engywuck-Auflage 21.08.) ---------------------------
#
# Die Zeile darueber misst, dass im Trockenlauf NICHTS passiert. Das allein
# waere ein Pruefer, der Untaetigkeit belohnt: Ein Tagescheck, der gar nichts
# mehr legt, bestuende ihn glaenzend. Deshalb die Gegenrichtung - OHNE Schalter
# muss der Vermerk wirklich entstehen, und zwar in der Umleitung, nicht im
# echten Buch.
#
# Nur in der Zielumgebung messbar: Der Python-Block braucht Bot-Verzeichnis und
# venv. Fehlen sie, wird das GESAGT statt still uebersprungen - ein
# uebersprungener Pruefer, der wie ein bestandener aussieht, ist schlimmer als
# keiner.
_bot="/home/claudebot/claude-telegram-bot"
if [ -d "$_bot" ] && [ -x "$_bot/.venv/bin/python3" ]; then
  _norm="${TMPDIR:-/tmp}/zielumgebung-normal.$$"
  mkdir -p "$_norm"
  env -i "AUFTRAGSBUCH_DIR=$_norm" TELEGRAM_BOT_TOKEN= ALLOWED_USER_IDS= \
      /bin/bash scripts/daily_check.sh >/dev/null 2>&1 </dev/null || true
  if [ -n "$(ls -A "$_norm" 2>/dev/null)" ]; then
    melde ok "ohne Schalter entsteht der Vermerk (in der Umleitung)"
  else
    melde nein "ohne Schalter entsteht der Vermerk (in der Umleitung)" \
               "die Umleitung blieb leer - legt der Tagescheck ueberhaupt noch?"
  fi
  rm -rf "$_norm"
else
  melde skip "Normalfall-Vermerk" \
             "nicht die Zielumgebung - hier wurde NICHTS gemessen"
fi

# --- 3d. Die Sollbruchstelle der Kontingent-Abfrage (Engywuck-F-Zeile 21.08.)
#
# /kontingent liest den BILDSCHIRM der Oberflaeche. Aendert ein CLI-Update
# deren Layout, liefert die Abfrage nichts mehr - und ohne diese Zeile merkte
# es erst Adam. Der Updater setzt KONTINGENT_LIVE=1, wenn er nach einem
# Einspielen prueft; im Alltag bleibt die Zeile aus, weil sie rund eine Minute
# kostet und ein Pruefer, der jeden Lauf verlaengert, abgeschaltet wird.
if [ -n "${KONTINGENT_LIVE:-}" ] && [ -d "$_bot" ]; then
  # **[GEAENDERT 30.08.] Die Python-Fassung wird GESUCHT, nicht getippt**
  # (F-Listen-Fund [25]). Hier stand `python3.13` fest im Pfad — die einzige
  # Stelle im ganzen Repo mit einer festen Fassung. `bot.py` loest denselben
  # Pfad ueber `Path(_sdk.__file__).parent` auf; hier tut es ein Muster.
  # **Ein Python-Sprung haette diese Zeile still ins Leere laufen lassen** —
  # `2>/dev/null || true` haette den Fehler geschluckt, und die Zeile waere
  # rot geworden mit der Begruendung "Layout von /usage geaendert". Die
  # falsche Spur ist teurer als der fehlende Befund.
  _cli="$(ls -d "$_bot"/.venv/lib/python3.*/site-packages/claude_agent_sdk/_bundled/claude \
          2>/dev/null | head -1)"
  if [ -z "$_cli" ]; then
    melde skip "Kontingent-Abfrage liefert nach dem Update noch Werte" \
               "die gebuendelte CLI ist unter keinem python3.*-Pfad auffindbar"
  else
    _kout="$("$_bot/.venv/bin/python3" "$_bot/kontingent_sitzung.py" "$_cli" \
             2>/dev/null || true)"
    if echo "$_kout" | grep -q "anteil"; then
      melde ok "Kontingent-Abfrage liefert nach dem Update noch Werte"
    else
      melde nein "Kontingent-Abfrage liefert nach dem Update noch Werte" \
                 "kein Wert gelesen - hat sich das Layout von /usage geaendert?"
    fi
  fi
else
  # **[NEU 30.08.] Der Block verschwand spurlos** (F-Listen-Fund [63]): Ohne
  # `KONTINGENT_LIVE` wurde `melde` nie gerufen, GESAMT stieg nicht, und in der
  # Bilanz war von dieser Pruefung keine Spur. Auf dem VPS laeuft sie nach
  # jedem Update wirklich (`updater.py`), am Bau-Rechner nie — **und beide
  # Maschinen zeigten dieselbe Vollzahl.** Genau die fehlende Zahlendifferenz,
  # gegen die heute Vormittag die Uebersprungs-Kategorie entstanden ist.
  melde skip "Kontingent-Abfrage liefert nach dem Update noch Werte" \
             "nur nach einem Update gemessen (KONTINGENT_LIVE), kostet sonst eine Minute"
fi

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

# --- 5. Der Abgleich quittiert, was er mitnahm UND was nicht ----------------
#
# Die Kurier-Abmachung verspricht eine Meldung; bis zum 19.08. tat das Skript
# es nicht. Dritter Fund der Klasse [eine Vorgabe, die nur auf dem Papier
# steht] an einem Tag.
if grep -q 'letzter-abgleich.txt' scripts/log_sync.sh \
   && grep -q 'AUSGESCHLOSSEN' scripts/log_sync.sh \
   && grep -q 'GEHEIMNIS-NAMENSFILTER' scripts/log_sync.sh; then
  melde ok "Abgleich quittiert Mitgenommenes und Ausgeschlossenes"
else
  melde nein "Abgleich quittiert Mitgenommenes und Ausgeschlossenes" \
    "keine Quittung oder kein Grund je ausgeschlossener Datei — lautlos aussortiert"
fi

# --- 6. Kein Pruefer schreibt einen plattformgebundenen Pfad fest ----------
#
# **Engywucks Auflage vom 29.08., aus einem echten Fehlschlag.** Zwei frische
# Pruefer legten ihre Wegwerf-Ordner unter dem festen Pfad /private/tmp an —
# **den gibt es nur auf macOS.** Auf dem VPS starben beide beim Import, bevor
# eine einzige Pruefzeile lief: 57 von 61 statt 61 von 61. Der Betriebscode
# war einwandfrei; **tot war der Pruefer**, und zwar stumm.
#
# Das wiegt schwer, weil es genau die neue Sicherheitsschranke betraf: Sie
# waere auf den VPS gegangen und dort ungeprueft im Betrieb gestanden.
#
# **Dritter Fall derselben Klasse in fuenf Tagen** — PEP 701 (Python 3.11
# gegen 3.13), die iCloud-Freigabe (App gegen launchd), jetzt der macOS-Pfad.
# *Was auf einer Maschine gemessen wurde, gilt auf der anderen nicht.*
#
# Die Menge entsteht ueber `git ls-files`, nicht ueber ein Namensmuster im
# Ordner — ein Muster haette Unterordner verfehlt. `scripts/mac/` ist
# ausgenommen: Diese Skripte sind ausdruecklich Mac-gebunden.
#
# Kommentarzeilen fallen heraus, sonst stolperte die Zeile ueber ihre eigene
# Erklaerung — der sicherste Weg, binnen einer Woche abgeschaltet zu werden.
#
# **`[ERWEITERT 03.09.2026]` Zwei Luecken, beide am 02.09. aufgeschlagen.**
# Das Muster verlangte den Pfad direkt hinter einem Anfuehrungszeichen und
# kannte `~/Projects` nicht. Gemessen: `test_eingangsschranken.py` trug
# **achtmal** `"cat ~/Projects/claude-telegram-bot/README.md"` — der Pfad steht
# MITTEN in der Zeichenkette und beginnt mit der Tilde. Der Pruefer sah ihn
# nicht, und auf dem VPS zeigten alle acht Befehle aus dem Repo hinaus.
#
# **Rot wurde dort nur die eine Zeile, die ein leeres Ergebnis erwartet** — die
# anderen sieben waren aus dem falschen Grund gruen. Genau deshalb faengt diese
# Zeile hier: Sie sieht den Pfad, bevor er ein Urteil verfaelscht.
#
# Der Anker faellt weg, `~/Projects` kommt dazu. Fehlalarm-Risiko gering: Diese
# Zeichenfolgen sind auf keinem Server sinnvoll, und Kommentare fallen ohnehin
# heraus.
_gefunden=""
for _d in $(git ls-files 'scripts/*.py' 2>/dev/null | grep -v '^scripts/mac/'); do
  if grep -vE '^[[:space:]]*#' "$_d" \
     | grep -qE '(/private/tmp|/private/var|/Users/|/opt/homebrew|/Library/Mobile|~/Projects)'; then
    _gefunden="$_gefunden $_d"
  fi
done
if [ -z "$_gefunden" ]; then
  melde ok "kein Pruefer schreibt einen plattformgebundenen Pfad fest"
else
  melde nein "kein Pruefer schreibt einen plattformgebundenen Pfad fest" \
    "diese Pruefer laufen nur auf einer Maschine:$_gefunden"
fi

# --- 7. Keine feste Python-Fassung in einem Pfad --------------------------
#
# **F-Listen-Fund [25], und die Zeile darueber haette ihn nicht gefunden:** Sie
# sucht Betriebssystem-Pfade (`/Users/`, `/opt/homebrew`) und nur in `*.py`.
# Eine festgeschriebene Fassung wie `python3.13` mitten in einem Pfad faellt
# durch beide Raster — sie war die einzige Stelle im ganzen Repo.
#
# **Warum das still bricht:** Beim naechsten Python-Sprung zeigt der Pfad ins
# Leere. Wo ein `2>/dev/null` daneben steht, wird daraus kein Fehler, sondern
# ein leeres Ergebnis — und die Pruefung meldet einen falschen Grund. Die
# falsche Spur ist teurer als der fehlende Befund.
#
# Kommentarzeilen fallen heraus: Der Erklaertext hier nennt die Fassung selbst.
_fest=""
for _d in $(git ls-files '*.py' '*.sh' 2>/dev/null); do
  [ "$_d" = "scripts/test_zielumgebung.sh" ] && continue
  if grep -vE '^[[:space:]]*#' "$_d" | grep -qE 'python3\.[0-9]'; then
    _fest="$_fest $_d"
  fi
done
if [ -z "$_fest" ]; then
  melde ok "keine feste Python-Fassung in einem Pfad"
else
  melde nein "keine feste Python-Fassung in einem Pfad" \
    "beim naechsten Python-Sprung zeigen diese Pfade ins Leere:$_fest"
fi

echo "== Zielumgebung: $((GESAMT-FAILS-UEBERSPRUNGEN))/$GESAMT bestanden =="
if [ "$UEBERSPRUNGEN" -gt 0 ]; then
  echo "== $UEBERSPRUNGEN uebersprungen — hier wurde nichts gemessen =="
fi
exit $FAILS
