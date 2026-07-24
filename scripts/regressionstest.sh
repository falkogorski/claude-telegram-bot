#!/usr/bin/env bash
# <!-- ROLLE: regressionstest-minimal -->
# 8.2-Minimaltest (Rotes-Team-Bericht, Top-3-Massnahme 2): buendelt die
# vorhandenen Pruefungen zu EINEM abrufbaren Regressionslauf.
# Pflicht VOR jedem Fundament-Update (CLI/SDK) und nach groesseren Aenderungen.
# Aufruf: bash scripts/regressionstest.sh   (im Repo-Wurzelverzeichnis,
#         auf dem VPS als claudebot im Klon /home/claudebot/claude-telegram-bot)
set -u
cd "$(dirname "$0")/.."

PY="python3"
if [ -x ".venv/bin/python3" ]; then PY=".venv/bin/python3"; fi

FAILS=0
run() {
  local name="$1"; shift
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
run "Syntax pending.py"                 "$PY" -m py_compile pending.py
run "Syntax presend.py"                 "$PY" -m py_compile presend.py
# Auf dem VPS liegen die echten Envs nur in der root-geschuetzten systemd-Env —
# fuer den reinen Invarianten-Check reichen Platzhalter (kein Telegram-Kontakt).
# WICHTIG: nur fuer DIESEN einen Aufruf setzen, nicht global exportieren —
# die Verhaltenstests bringen eigene Fixture-Envs mit (Kollisions-Lehre 23.07.).
MEMDIR="${CLAUDE_MEMORY_DIR:-}"
if [ -z "$MEMDIR" ] && [ -f "$HOME/.claude/memory/MEMORY.md" ]; then
  MEMDIR="$HOME/.claude/memory"
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
run "Doku-Spiegel (/hilfe/Buttons)"     "$PY" scripts/check_hilfe_buttons.py

echo "== Ergebnis: $((14-FAILS))/14 bestanden =="
exit $FAILS
