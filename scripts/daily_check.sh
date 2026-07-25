#!/usr/bin/env bash
# <!-- ROLLE: taeglicher-funktionscheck -->
# ============================================================================
# 8.1 — Täglicher 4-Uhr-Funktionscheck (zentrale Sammelstelle).
#
# STRENG DETERMINISTISCH — KEIN Modell-/Claude-Aufruf (AGB-Leitplanke:
# zeitgesteuerte Routinen dürfen keine Abo-Inferenz auslösen; siehe
# docs/entscheidungsvorlagen/agb-faktensammlung.md D). Der Check nutzt nur:
# systemctl-Status, den 8.2-Regressionstest, Token-Alter, Webhook-Gesundheit.
# Meldung an Adam via Telegram-Bot-API (curl) — reiner Status, keine Inferenz.
#
# Läuft als root (systemd-Timer `claude-daily-check.timer`, 04:10), damit die
# Env (Token) und systemctl erreichbar sind. Protokolliert IMMER; schickt eine
# Telegram-Nachricht NUR bei Problemen (rot) — grüne Tage bleiben still.
# ============================================================================
set -uo pipefail
VENVPY="$(dirname "$0")/../.venv/bin/python3"
[ -x "$VENVPY" ] || VENVPY="python3"

ENVFILE=/etc/claude-telegram-bot.env
BOTDIR=/home/claudebot/claude-telegram-bot
LOGDIR="$BOTDIR/logs"
CHECKLOG="$LOGDIR/daily-check.log"
TOKEN_ISSUED=/etc/claude-telegram-bot.token-issued

mkdir -p "$LOGDIR"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
problems=()
lines=()

add() { lines+=("$1"); }
red() { problems+=("$1"); lines+=("❌ $1"); }

# --- 1. Laufzeit-Dienste (ABHAENGIGKEITEN.md) --------------------------------
for svc in claude-telegram-bot searxng ollama litellm; do
  st="$(systemctl is-active "$svc" 2>/dev/null)"
  if [ "$st" = "active" ]; then add "✅ Dienst $svc aktiv"; else red "Dienst $svc: $st"; fi
done

# --- 2. Genau EINE Bot-Instanz ----------------------------------------------
n="$(pgrep -c -f 'python bot.py' 2>/dev/null || echo 0)"
if [ "$n" = "1" ]; then add "✅ genau eine Bot-Instanz"; else red "Bot-Instanzen: $n (soll 1)"; fi

# --- 3. 8.2-Regressionstest (als claudebot, dessen venv) --------------------
if reg="$(sudo -u claudebot bash "$BOTDIR/scripts/regressionstest.sh" 2>&1)"; then
  last="$(echo "$reg" | tail -1)"
  add "✅ Regressionstest: $last"
else
  fail="$(echo "$reg" | grep '❌' | head -3 | tr '\n' ' ')"
  red "Regressionstest FEHLGESCHLAGEN: ${fail:-siehe daily-check.log}"
fi

# --- 4. Token-Alter (5.20-Sidecar) ------------------------------------------
if [ -f "$TOKEN_ISSUED" ]; then
  issued="$(cat "$TOKEN_ISSUED" 2>/dev/null)"
  iss_s="$(date -d "$issued" +%s 2>/dev/null || echo 0)"
  if [ "$iss_s" -gt 0 ]; then
    age_days=$(( ( $(date +%s) - iss_s ) / 86400 ))
    if   [ "$age_days" -ge 330 ]; then red "OAuth-Token ${age_days} Tage alt — bald erneuern (läuft ~365 T)!"
    elif [ "$age_days" -ge 300 ]; then add "⚠️ OAuth-Token ${age_days} Tage alt (Erneuerung planen)"
    else add "✅ OAuth-Token ${age_days} Tage alt"; fi
  else add "⚠️ Token-Ausstelldatum unlesbar ($issued)"; fi
else add "⚠️ kein Token-Sidecar ($TOKEN_ISSUED)"; fi

# --- 5. Webhook-Gesundheit (nur wenn BOT_MODE=webhook) ----------------------
set -a; . "$ENVFILE" 2>/dev/null; set +a
if [ "${BOT_MODE:-polling}" = "webhook" ]; then
  info="$(curl -s -m 15 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" 2>/dev/null)"
  # Gesundheits-Signal ist pending_update_count (stauen sich Updates?), NICHT das
  # Alter des letzten Fehlers: ein eingefrorener Startup-Race-Fehler bei pending=0
  # bedeutet, Telegram hat danach erfolgreich zugestellt. Rot nur bei fehlender
  # URL oder echtem Rückstau; last_error wird nur informativ mitgeführt.
  py="$(python3 - "$info" <<'PY'
import sys, json
try:
    d = json.loads(sys.argv[1]).get("result", {})
except Exception:
    print("ERR|?|"); raise SystemExit
url = bool(d.get("url"))
pending = d.get("pending_update_count") or 0
print(f"{'OK' if url else 'NOURL'}|{pending}|{d.get('last_error_message','')}")
PY
)"
  IFS='|' read -r wstat wpending wmsg <<< "$py"
  if [ "$wstat" != "OK" ]; then red "Webhook: keine URL gesetzt ($wstat)"
  elif [ "${wpending:-0}" -ge 5 ]; then red "Webhook: ${wpending} Updates gestaut (letzter Fehler: ${wmsg:-–})"
  else add "✅ Webhook gesund (pending=${wpending})"; fi
else
  add "ℹ️ Polling-Modus (kein Webhook-Check)"
fi

# --- 6. LobeChat-Sicherheits-Invariante (3.1): nur localhost, nie öffentlich --
if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^lobe-chat$'; then
  bind="$(ss -tlnH 'sport = :3210' 2>/dev/null | awk '{print $4}' | head -1)"
  if echo "$bind" | grep -q '^127\.0\.0\.1:'; then
    add "✅ LobeChat nur localhost ($bind)"
  else
    red "LobeChat lauscht NICHT nur auf localhost: '${bind:-?}' — OpenClaw-Risiko!"
  fi
  if ufw status 2>/dev/null | grep -q '3210'; then red "ufw: Port 3210 offen — LobeChat darf NIE öffentlich sein!"; fi
fi

# --- Protokoll + Meldung ------------------------------------------------------

# --- 8. Zwischenlager des eigenen Bot-API-Servers (5.34) --------------------
# 🚦 Conni-Bedingung: Der 30-GB-Deckel wird GEPRÜFT, nicht nur gesetzt.
# Ohne diesen Prüfer wäre er wieder eine Bitte — der vierte Fall dieser Klasse.
if [ -d "${TELEGRAM_API_DIR:-/var/lib/telegram-bot-api}" ]; then
  if bash "$(dirname "$0")/api_cache_pflege.sh" > /tmp/api_cache_check.log 2>&1; then
    lines+=("✅ API-Zwischenlager: $(tail -1 /tmp/api_cache_check.log)")
  else
    lines+=("❌ API-Zwischenlager: $(tail -2 /tmp/api_cache_check.log | tr '\n' ' ')")
    problems+=("Das Zwischenlager des Bot-API-Servers reisst den Deckel — auch nach dem Aufraeumen zu gross.")
  fi
else
  lines+=("~ API-Zwischenlager: kein eigener Bot-API-Server aktiv (5.34 nicht eingeschaltet)")
fi



# --- 9. Stundenblumen-Kette (lebt das System durchgehend?) ------------------
# Die Zeitpunkt-Pruefungen sagen nur etwas ueber diesen Augenblick. Die Kette
# belegt die Zeit DAZWISCHEN — und ihr Stillstand ist selbst der Befund.
if [ -f "$(dirname "$0")/stundenblume.py" ]; then
  if "$VENVPY" "$(dirname "$0")/stundenblume.py" --pruefen > /tmp/blumen_check.log 2>&1; then
    lines+=("✅ Stundenblumen: $(tail -1 /tmp/blumen_check.log)")
  else
    lines+=("❌ Stundenblumen: $(tail -1 /tmp/blumen_check.log)")
    problems+=("Die Stundenblumen-Kette steht still oder ist gebrochen: $(tail -1 /tmp/blumen_check.log)")
  fi
fi


{
  echo "===== 4-Uhr-Check $STAMP ====="
  printf '%s\n' "${lines[@]}"
} >> "$CHECKLOG"

if [ "${#problems[@]}" -gt 0 ]; then
  # Nur bei Problemen an Adam melden (grüne Tage bleiben still).
  report="🔧 4-Uhr-Check $STAMP — ${#problems[@]} Problem(e):"
  for p in "${problems[@]}"; do report="${report}"$'\n'"• ${p}"; done
  report="${report}"$'\n\n'"(Vollprotokoll: logs/daily-check.log)"
  IFS=',' read -ra uids <<< "${ALLOWED_USER_IDS:-}"
  for uid in "${uids[@]}"; do
    [ -n "$uid" ] || continue
    curl -s -m 15 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      --data-urlencode "chat_id=${uid}" \
      --data-urlencode "text=${report}" >/dev/null 2>&1
  done
  echo "Probleme gemeldet: ${#problems[@]}"
else
  echo "Alles grün — keine Meldung."
fi
