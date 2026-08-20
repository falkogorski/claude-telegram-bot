#!/usr/bin/env bash
# <!-- ROLLE: regressionstest-minimal -->
# 8.2-Minimaltest (Rotes-Team-Bericht, Top-3-Massnahme 2): buendelt die
# vorhandenen Pruefungen zu EINEM abrufbaren Regressionslauf.
# Pflicht VOR jedem Fundament-Update (CLI/SDK) und nach groesseren Aenderungen.
# Aufruf: bash scripts/regressionstest.sh   (im Repo-Wurzelverzeichnis,
#         auf dem VPS als claudebot im Klon /home/claudebot/claude-telegram-bot)
set -u
# HOME mit Rueckfall: Der Tagescheck ruft diesen Lauf, und er laeuft als
# root-Systemdienst ohne HOME. Ohne den Rueckfall bricht `set -u` hier mitten
# im Lauf ab - nach den ersten Pruefungen, deren Ergebnis dann verloren ist.
cd "$(dirname "$0")/.."

PY="python3"
if [ -x ".venv/bin/python3" ]; then PY=".venv/bin/python3"; fi

# --- Der Prüflauf bekommt eine WEGWERF-Umgebung -----------------------------
# BELEGTER VORFALL (26.07.2026, 01:44): Ein Regressionslauf auf dem VPS hat
# Adam nachts um Viertel vor zwei eine Meldung geschickt — „Der Bot ist nach
# dem Update von demo sauber hochgekommen". Es gab kein Update und kein „demo";
# es war ein Testszenario, das ins ECHTE Boten-Postfach schrieb, aus dem der
# Bot alles zustellt, was er dort findet.
#
# Vierzehn Tage Abwesenheit mal zwei Hora-Läufe am Tag mal jeder Auftrag — das
# wären Dutzende sinnloser Nachrichten gewesen, die niemand einordnen kann.
# Und der Schaden ist nicht die Menge, sondern die Gewöhnung: Wer gelernt hat,
# Meldungen dieses Absenders zu überlesen, überliest auch die echte.
#
# Die Ursache war NICHT ein einzelner nachlässiger Test — die meisten setzen
# ihr Postfach ordentlich selbst. Sie war, dass es überhaupt möglich ist. Also
# der strukturelle Riegel statt vierzehn einzelner: Der Läufer legt für ALLE
# Prüfungen ein Wegwerf-Verzeichnis an. Was ein Test dorthin schreibt, sieht
# nie ein Mensch. (Regel: Wo Struktur und Prüfer beide möglich sind, gewinnt
# die Struktur — ein Prüfer meldet Drift, eine gemeinsame Quelle lässt sie
# nicht entstehen.)
PRUEFHEIM="$(mktemp -d "${TMPDIR:-/tmp}/regress-XXXXXX")"
export POSTFACH_DIR="$PRUEFHEIM/postfach"
export FREIGABE_DIR="$PRUEFHEIM/freigaben"
export HORA_DIR="$PRUEFHEIM/hora"
export BLUMEN_DIR="$PRUEFHEIM/blumen"
mkdir -p "$POSTFACH_DIR/outbox" "$FREIGABE_DIR" "$HORA_DIR" "$BLUMEN_DIR"
trap 'rm -rf "$PRUEFHEIM"' EXIT

# Stand des ECHTEN Postfachs VOR dem Lauf — der Nachweis am Ende vergleicht.
ECHTPOST="${HOME:-/home/claudebot}/postfach/outbox"
POST_VORHER="$(ls -A "$ECHTPOST" 2>/dev/null | wc -l | tr -d ' ')"

FAILS=0
# GESAMT wird GEZAEHLT, nicht getippt. Vorher stand die Zahl fest im
# Schlusssatz — beim Aufnehmen der 9.5-Pruefung meldete der Lauf "29/29",
# obwohl 30 Pruefungen gruen waren, und bei einem Fehlschlag haette er
# ebenso falsch gerechnet. Eine Kennzahl, die von Hand nachgepflegt werden
# muss, wird irgendwann nicht nachgepflegt.
GESAMT=0
run() {
  local name="$1"; shift
  GESAMT=$((GESAMT+1))
  if "$@" >/tmp/regress_last.log 2>&1; then
    echo "✅ $name"
  else
    echo "❌ $name — Log:"
    tail -20 /tmp/regress_last.log
    FAILS=$((FAILS+1))
  fi
}

echo "== 8.2-Minimaltest ($(date '+%Y-%m-%d %H:%M')) =="
run "Syntax bot.py (py_compile)"        "$PY" -m py_compile bot.py
run "Syntax transcribe.py"              "$PY" -m py_compile transcribe.py
run "Syntax reactions.py"               "$PY" -m py_compile reactions.py
run "Syntax channels.py"                "$PY" -m py_compile channels.py
run "Syntax media.py"                   "$PY" -m py_compile media.py
run "Syntax kalender.py"                "$PY" -m py_compile kalender.py
run "Syntax linkinbox.py"               "$PY" -m py_compile linkinbox.py
run "Syntax freigaben.py"               "$PY" -m py_compile freigaben.py
run "Syntax pending.py"                 "$PY" -m py_compile pending.py
run "Syntax presend.py"                 "$PY" -m py_compile presend.py
# Auf dem VPS liegen die echten Envs nur in der root-geschuetzten systemd-Env —
# fuer den reinen Invarianten-Check reichen Platzhalter (kein Telegram-Kontakt).
# WICHTIG: nur fuer DIESEN einen Aufruf setzen, nicht global exportieren —
# die Verhaltenstests bringen eigene Fixture-Envs mit (Kollisions-Lehre 23.07.).
MEMDIR="${CLAUDE_MEMORY_DIR:-}"
if [ -z "$MEMDIR" ] && [ -f "${HOME:-/home/claudebot}/.claude/memory/MEMORY.md" ]; then
  MEMDIR="${HOME:-/home/claudebot}/.claude/memory"
fi
run "Selbstcheck-Invarianten (run_self_check)" env \
  TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-000000:selfcheck-dummy}" \
  ALLOWED_USER_IDS="${ALLOWED_USER_IDS:-1}" \
  ${MEMDIR:+CLAUDE_MEMORY_DIR="$MEMDIR"} \
  "$PY" -c "
import bot
ok, lines = bot.run_self_check()
print('\n'.join(lines))
raise SystemExit(0 if ok else 1)
"
run "Log-Rollover (Tageswechsel)"       "$PY" scripts/test_conversation_log_rollover.py
run "Reaktionen 5.9"                    "$PY" scripts/test_reactions_5_9.py
run "Voice-Eingangs-Schutz"             "$PY" scripts/test_voice_entry_guard.py
run "Session-Waechter 5.18"             "$PY" scripts/test_stall_5_18.py
run "Kanal-Routing Phase 6"             "$PY" scripts/test_channels_6.py
run "Warteschlange FIFO 5.5"            "$PY" scripts/test_queue_order_5_5.py
run "Updater-Haertung A1-A7"            "$PY" scripts/test_updater_haertung.py
run "Medien-Transport H1 (Bild/Video)"  "$PY" scripts/test_media_h1.py
run "Start-Waechter B1"                 "$PY" scripts/test_start_waechter_b1.py
run "Kontingent-Limit H2"               "$PY" scripts/test_session_limit_h2.py
run "Nachzieher C1"                     "$PY" scripts/test_nachzieher_c1.py
run "Kalender/CalDAV (7.x)"             "$PY" scripts/test_kalender_caldav.py
run "Wartungsfenster B2/B3"             "$PY" scripts/test_wartungsfenster_b3.py
run "Link-Inbox 5.14"                   "$PY" scripts/test_linkinbox_5_14.py
run "E-Mail-Kanal 9.5"                  "$PY" scripts/test_email_9_5.py
run "Freigabe-Postfach 9.4"             "$PY" scripts/test_freigaben_9_4.py
run "Hora (autonomer Laeufer)"          "$PY" scripts/test_hora.py
run "Stundenblumen (Belegkette)"        "$PY" scripts/test_stundenblumen.py
run "Zustell-Waechter (erreicht uns TG?)" "$PY" scripts/test_zustellwaechter.py
run "Pruefumgebung (Riegel 3)"          "$PY" scripts/test_pruefumgebung.py
run "Versions-Monitor (5.21)"           "$PY" scripts/test_version_monitor.py
run "Update-Textbefehl (E4)"           "$PY" scripts/test_update_textbefehl.py
run "Wachposten (Log-Waechter)"        "$PY" scripts/test_wachposten.py
run "Postfach-Wiederaufgriff (A1)"     "$PY" scripts/test_postfach_wiederaufgriff.py
run "Abgleich-Quittung (log_sync)"     "$PY" scripts/test_log_sync_quittung.py
run "Wecker nach Limit (A3)"           "$PY" scripts/test_wecker_a3.py
run "Zielumgebung (bash -n + env -i)"  bash scripts/test_zielumgebung.sh
run "Sendepfad-Rauchtest (Pflicht 1)"  "$PY" scripts/test_sendepfad_rauch.py
run "Gruendlich-Umschalter (B3)"        "$PY" scripts/test_gruendlich_b3.py
run "Limit-Vorwarnung 5.20 (B4)"        "$PY" scripts/test_limitwarnung_b4.py
run "Vorlese-Regeln (B5)"               "$PY" scripts/test_vorlese_b5.py
run "Blinde-Flecken-Verfahren (B6)"     "$PY" scripts/test_blinde_flecken_b6.py
run "Auftragsbuch B8 (ruhend)"          "$PY" scripts/test_auftragsbuch_b8.py
run "Doku-Spiegel (/hilfe/Buttons)"     "$PY" scripts/check_hilfe_buttons.py

# Der Nachweis, dass die Wegwerf-Umgebung wirklich gegriffen hat. Nachmessen,
# was ankam — nicht die Konfiguration lesen (Wirkungs-Regel). Steht bewusst am
# ENDE, nach allen Prüfungen: Erst dann ist etwas zu sehen, falls ein Test die
# Umgebung doch umgangen hat.
# Gemessen wird der ZUWACHS, nicht der Bestand: Im echten Postfach kann eine
# echte, noch nicht zugestellte Nachricht liegen — die ist kein Fehler. Ein
# Prüfer, der darüber rot wird, ist ein Dauer-Alarm und binnen zwei Tagen
# abgeschaltet. (Derselbe Grund, aus dem die Speicher-Wache MemAvailable misst
# und nicht MemFree.)
GESAMT=$((GESAMT+1))
POST_NACHHER="$(ls -A "$ECHTPOST" 2>/dev/null | wc -l | tr -d ' ')"
if [ "$POST_NACHHER" -gt "$POST_VORHER" ]; then
  echo "❌ Eine Pruefung hat ins ECHTE Postfach geschrieben ($((POST_NACHHER-POST_VORHER)) neu)."
  echo "   Ein Testszenario wuerde damit als echte Nachricht bei Adam landen —"
  echo "   belegt am 26.07. um 01:44 mit einer Meldung ueber ein 'Update von demo'."
  FAILS=$((FAILS+1))
else
  echo "✅ Wegwerf-Umgebung: keine Pruefung hat ins echte Postfach geschrieben"
fi

echo "== Ergebnis: $((GESAMT-FAILS))/$GESAMT bestanden =="
exit $FAILS
