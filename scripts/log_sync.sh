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

# **[NEU 30.08.] HOME wird BENANNT eingefordert** (Faecher-Fund [19], A2).
# Unter `set -u` bricht `$HOME` ohne HOME mit "unbound variable" ab — auch
# innerhalb eines Rueckfalls wie `${VAR:-$HOME/x}`, denn dort wird $HOME
# expandiert, sobald VAR fehlt. Genau daran starb am 29.07. ein Waechter,
# einundzwanzig Tage unbemerkt. Diese Zeile macht daraus einen Abbruch mit
# Grund statt einer Fehlermeldung, die niemand einem fehlenden Zuhause
# zuordnet — und sie sichert alle folgenden $HOME-Stellen auf einmal.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"

SRC="${LOG_SYNC_SRC:-$HOME/claude-telegram-bot/logs/conversations}"
REPO="${LOG_SYNC_REPO:-$HOME/logsync/claude-bot-logs}"

[ -d "$SRC" ] || { echo "Quelle fehlt: $SRC"; exit 1; }
cd "$REPO" || { echo "Log-Repo-Klon fehlt: $REPO"; exit 1; }

# **[NEU 30.08.] Das Werkzeug wird geprueft, bevor darauf gebaut wird.**
#
# Faecher-Fund [71], und er benennt den gefaehrlicheren Teil richtig: Das
# Skript laeuft mit `set -uo pipefail` OHNE `-e`. Fehlte rsync, lief es
# durch, kopierte nichts und endete mit Rueckgabewert 0 samt der Meldung
# "Keine Log-Aenderungen — nichts zu pushen."
#
# **Ein Abgleich, der nichts kopiert, sah damit genauso aus wie einer, bei dem
# es nichts zu kopieren gab.** Das ist woertlich die Klasse des Tageswaechters,
# der am 29.07. starb und einundzwanzig Tage nicht auffiel: Der Bruch sieht
# aus wie Ruhe. Hier scheitert er stattdessen laut und benannt.
command -v rsync >/dev/null 2>&1 || {
  echo "rsync fehlt auf dieser Maschine — es wurde NICHTS abgeglichen." >&2
  echo "Ohne diese Zeile haette der Lauf mit 0 geendet und wie ein leerer" >&2
  echo "Abgleich ausgesehen. rsync steht als Abhaengigkeit im Register." >&2
  exit 3
}

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
# A4 (20.08.): Das ausführliche Wachposten-Archiv mitsyncen.
#
# **Ohne diese Zeile wäre A4 halb gebaut gewesen.** Die Trennung schickt Adam
# einen kurzen deutschen Satz und legt die Einzelheiten „ins Archiv, auf das
# Engywuck ohnehin zugreift" — nur griff er darauf gar nicht zu, weil der
# Kurier die Datei nicht kannte. Die Details wären auf dem Server verblieben
# und niemand hätte es bemerkt: eine Stille, die wie Ordnung aussieht.
# (Gefunden beim Nachmessen des Kuriers, nicht beim Bauen der Trennung.)
WPLOG="${LOG_SYNC_WPLOG:-$(dirname "$SRC")/wachposten-archiv.log}"
if [ -f "$WPLOG" ]; then
  cp "$WPLOG" wachposten-archiv.log
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
  # ⚠️ REIHENFOLGE IST DIE FUNKTION: rsync nimmt die ERSTE zutreffende Regel.
  # Ausschlüsse müssen daher VOR den Einschlüssen stehen — stünden sie danach,
  # gewinnt `--include='*.md'` und zieht Ausgeschlossenes doch mit. Genau so
  # ist am 25.07. die Kontext-Datei CLAUDE.md ins Log-Repo gewandert, obwohl
  # sie ausdrücklich ausgeschlossen war.
  # **[NEU 04.09.] Der Rechnungszweig kommt NICHT mit** (Engywucks Befund 4).
  #
  # Seit dem Umzug am 03.09. liegt Adams Rechnungsprojekt unter
  # `~/workspace/rechnungen` — also **im** Arbeitsordner, den dieser Block
  # abgleicht. Die erzeugten PDFs tragen **Bankverbindung und Steuernummer**;
  # `--include='*.pdf'` hätte sie ins Log-Repo getragen, und die Historie eines
  # Repos vergisst nichts von selbst.
  #
  # ⚠️ **Die Zeile steht VOR den Includes, und das ist keine Sortierfrage,
  # sondern die Funktion** — siehe den Kommentar direkt darüber. Stünde sie
  # danach, gewänne `--include='*.pdf'` und der Ausschluss wäre wirkungslos,
  # ohne dass irgendetwas rot würde.
  #
  # ⚠️ **Der Anker ist ein NAME, kein Merkmal** — dieselbe Grenze wie beim
  # Backup-Ausschluss vom 03.09., wo `.venv` nicht griff, weil der Ordner
  # anders hieß. Wird das Projekt umbenannt oder verschoben, greift diese
  # Zeile nicht mehr. Wer es umbenennt, zieht sie mit.
  rsync -a --prune-empty-dirs \
    --exclude='rechnungen/' \
    --exclude='.*' --exclude='*.tmp' \
    --exclude='CLAUDE.md' --exclude='MEMORY.md' \
    --exclude='*secret*' --exclude='*token*' --exclude='*credential*' \
    --exclude='*passwor*' --exclude='*.env' --exclude='*key*' \
    --include='*/' \
    --include='*.md' --include='*.pdf' --include='*.txt' \
    --include='*.csv' --include='*.html' \
    --exclude='*' \
    "$WORK/" ausarbeitungen/ 2>/dev/null || true
  # Nachweis statt Vertrauen: Was hier trotzdem liegt, wird entfernt.
  rm -f ausarbeitungen/CLAUDE.md ausarbeitungen/MEMORY.md 2>/dev/null || true

  # --- Die Quittung (Nachlese ② und ③, Engywuck 18.08.) --------------------
  #
  # **Die Abmachung versprach „der Abgleich meldet, was er mitgenommen hat" —
  # und das Skript tat es nicht.** Dritter Fund derselben Klasse an einem Tag:
  # eine Vorgabe, die nur auf dem Papier stand. Claudia fragte daraufhin, ob
  # sie „morgen nachsehen" solle, ob ihre Fracht angekommen sei. Diese Frage
  # beantwortet die Quittung ab jetzt von selbst.
  #
  # **Und sie nennt auch, was NICHT mitkam.** Der Geheimnis-Namensfilter bleibt
  # hart — aber nicht lautlos: Eine Ausarbeitung über „Token-Optimierung" darf
  # ausgefiltert werden, nur nie stillschweigend. Sichtbar aussortiert ist
  # sicher und ehrlich; lautlos aussortiert ist die nächste Stille, die wie
  # Ruhe aussieht.
  {
    echo "Letzter Abgleich: $(date '+%d.%m.%Y, %H:%M')"
    echo
    echo "MITGENOMMEN:"
    # Die Quittung selbst gehoert NICHT in ihre eigene Frachtliste — sie ist
    # eine Aussage ueber den Transport, kein Transportgut. Ohne diesen
    # Ausschluss aendert sie sich beim zweiten Lauf zwangslaeufig (dann liegt
    # sie im Repo und listet sich selbst) und der Nur-bei-Aenderung-Riegel
    # schwingt eine Runde lang nach. Gefunden vom Pruefer, nicht beim Bauen.
    find ausarbeitungen -type f ! -name 'letzter-abgleich.txt' 2>/dev/null \
      | sed 's|^ausarbeitungen/|  |' | sort
    echo
    echo "AUSGESCHLOSSEN (haette mitkommen koennen, kam nicht):"
    # **[NEU 04.09.] Der Rechnungszweig: sichtbar, aber EINZEILIG.**
    # Zurueckgehalten wird er bewusst (Bank, Steuernummer). Ihn Datei fuer
    # Datei zu listen hiesse, die Liste mit jeder neuen Rechnung wachsen zu
    # lassen — und was niemand liest, meldet nichts. Die Schleife unten
    # ueberspringt den Zweig deshalb; diese eine Zeile nennt ihn samt Grund.
    # Ohne sie waere der Ausschluss lautlos, mit der Schleife allein waere er
    # eine Falschauskunft (jede Rechnung als bitte melden, das sollte
    # mitkommen). Beides ist schon einmal vorgekommen.
    if [ -d "$WORK/rechnungen" ]; then
      echo "  rechnungen/ — ganzer Zweig zurueckgehalten: Bank und Steuernummer"
    fi
    # `[GEAENDERT 2026-08-20, Engywuck]` Nur noch TRANSPORTRELEVANTE
    # Kandidaten — Dateien mit Dokument-Endung, die nicht ankamen, plus alles
    # vom Geheimnis-Filter Gestoppte. Vorher lief die Schleife ueber den
    # GANZEN Baum und listete jede Punkt-Datei und jedes Zwischenprodukt:
    # 5.207 Zeilen, 564 KB. Eine Liste dieser Laenge liest niemand, und was
    # niemand liest, meldet nichts — der Sinn der Quittung war gerade,
    # aussortierte Dateien SICHTBAR zu machen.
    #
    # Punkt-Dateien und `.tmp` gehoeren nicht dazu: Dass ein Arbeits-
    # Zwischenstand nicht mitkommt, ist kein Befund, sondern die Absicht.
    find "$WORK" -type f 2>/dev/null | while read -r f; do
      name="$(basename "$f")"
      rel="${f#$WORK/}"
      [ -f "ausarbeitungen/$rel" ] && continue
      # **Der Bericht muss denselben Filter spiegeln wie der Transport.**
      # Gemessen am 20.08. nach dem ersten Fix: Er prueft nur den DATEINAMEN,
      # rsync aber schliesst ueber `--exclude='.*'` auch versteckte
      # VERZEICHNISSE aus. Ergebnis waren 120 Zeilen Pip-Metadaten aus
      # `.pdfenv/` — jede mit dem Vermerk „bitte melden, das sollte mitkommen".
      # Das ist keine Laenge mehr, das ist eine aktive Falschauskunft: Wer sie
      # liest, meldet 120 harmlose Dateien als Fehler.
      case "$rel" in
        .*|*/.*)       continue ;;   # verstecktes Verzeichnis ODER Datei
        rechnungen/*|*/rechnungen/*) continue ;;
      esac
      case "$name" in
        *.tmp)         continue ;;   # Absicht, kein Befund
        CLAUDE.md|MEMORY.md) continue ;;   # ausdruecklich unerwuenscht
        *secret*|*token*|*credential*|*passwor*|*key*|*.env)
                       grund="GEHEIMNIS-NAMENSFILTER - der Name enthaelt ein Schluesselwort" ;;
        *.md|*.pdf|*.txt|*.csv|*.html) grund="unklar - bitte melden, das sollte mitkommen" ;;
        *)             continue ;;   # keine Dokument-Endung, nie vorgesehen
      esac
      echo "  $rel — $grund"
    done
    echo
    echo "Fehlt hier etwas, das mitkommen sollte? Dann sag Bescheid —"
    echo "der Filter ist bewusst hart, aber er soll nichts Richtiges schlucken."
  } > "$WORK/.letzter-abgleich.neu" 2>/dev/null || true

  # **Nur schreiben, wenn sich mehr geaendert hat als die Uhrzeit.**
  # Gemessen am 20.08.: 155 Commits an einem halben Tag, jeder einzelne allein
  # wegen der Kopfzeile. Ein Verlauf, in dem jeder Eintrag dasselbe sagt, ist
  # kein Verlauf — er verdeckt die Aenderungen, die etwas bedeuten.
  # (Engywucks Befund; sein Abnahmefehler, hier der Ein-Zeilen-Fix.)
  if [ -f "$WORK/letzter-abgleich.txt" ] \
     && diff -q <(tail -n +2 "$WORK/letzter-abgleich.txt") \
                <(tail -n +2 "$WORK/.letzter-abgleich.neu") >/dev/null 2>&1; then
    rm -f "$WORK/.letzter-abgleich.neu"      # inhaltsgleich — Quittung bleibt
  else
    mv "$WORK/.letzter-abgleich.neu" "$WORK/letzter-abgleich.txt"
  fi
fi


git add -A
if git diff --cached --quiet; then
  echo "Keine Log-Änderungen — nichts zu pushen."
  exit 0
fi
git commit -q -m "Log-Sync $(date '+%Y-%m-%d %H:%M')"
git push -q origin main && echo "Log-Sync gepusht: $(date '+%Y-%m-%d %H:%M')"
