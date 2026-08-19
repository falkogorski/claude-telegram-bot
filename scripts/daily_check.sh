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
# Der Heimatpfad des BOT-Benutzers - ausdruecklich, nicht ueber $HOME.
#
# BELEGTER VORFALL (29.07.-18.08.2026, 21 Tage): Hier stand einmal $HOME. Das
# Skript laeuft mit `set -u` als root-Systemdienst, und die Unit setzt kein
# `User=` - systemd liefert dort KEIN HOME. Jeder Lauf starb mit
# "HOME: unbound variable", drei Wochen lang, lautlos.
#
# Und der naheliegende Fix waere falsch gewesen: Mit HOME=/root suchte die
# Zustellmarke unter /root/.claude/ - geschrieben wird sie aber vom Bot als
# claudebot. Die Zeile haette dann dauerhaft "keine Stoerung" gemeldet und
# haette NIE anschlagen koennen. Ein Waechter, der nicht anschlagen kann, ist
# schlimmer als keiner.
BOTHOME=/home/claudebot

# --- Die Umgebung des BOT-Benutzers, fuer jeden Python-Aufruf von hier ------
#
# GEMESSEN 18.08.2026, beim allerersten echten Lauf nach der Reparatur:
# Der Tagescheck laeuft als root. `stundenblume.py` sucht ihre Belegkette unter
# `Path.home()/.claude/stundenblumen` - als root also unter /root/. Ergebnis:
# "Es gibt noch keine Kette", obwohl sie als claudebot nachweislich lueckenlos
# lief. Ein TAEGLICHER FEHLALARM.
#
# Das ist dieselbe Klasse wie die $HOME-Zeile, die drei Wochen Stille
# verursacht hat - nur in Python, wo nichts abstuerzt, sondern still woanders
# hingezeigt wird. Und die Wirkung ist womoeglich schlimmer: Ein Waechter, der
# jeden Tag grundlos rot meldet, wird abgeschaltet. Ein stiller wird nur
# vergessen.
BOTENV=(env "HOME=$BOTHOME"
            "BLUMEN_DIR=$BOTHOME/.claude/stundenblumen"
            "HORA_DIR=$BOTHOME/.claude/hora"
            "POSTFACH_DIR=$BOTHOME/postfach"
            "CLAUDE_MEMORY_DIR=$BOTHOME/.claude/memory")
LOGDIR="$BOTDIR/logs"
CHECKLOG="$LOGDIR/daily-check.log"
# Der laufende Mitschrieb - waechst waehrend des Laufs, nicht erst am Ende.
LAUFDATEI="$LOGDIR/.daily-check-lauf"
TOKEN_ISSUED=/etc/claude-telegram-bot.token-issued

mkdir -p "$LOGDIR"
STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
problems=()
lines=()

# --- Befunde werden beim ENTSTEHEN weggeschrieben, nicht erst am Ende -------
#
# Connis Auflage 1 nach dem 21-Tage-Ausfall. Vorher sammelte dieses Skript
# alles in `lines`/`problems` und schrieb erst ab Zeile ~310. Der Abbruch lag
# davor - also wurden die Befunde BERECHNET UND WEGGEWORFEN. Der
# Regressionslauf lief jedes Mal 28 Sekunden gruen durch, und niemand hat es je
# erfahren. Das ist schlimmer als "nicht geprueft": Es sah aus wie Ruhe.
#
# Jetzt haengt jede Zeile sofort am Protokoll. Ein Abbruch an beliebiger Stelle
# verliert nichts Gemessenes mehr - man sieht sogar, WIE WEIT der Lauf kam.
mkdir -p "$LOGDIR" 2>/dev/null || true
: > "$LAUFDATEI" 2>/dev/null || true

merken() { printf '%s\n' "$1" >> "$LAUFDATEI" 2>/dev/null || true; }
add() { lines+=("$1"); merken "$1"; }
red() { problems+=("$1"); lines+=("❌ $1"); merken "❌ $1"; }

# Bricht das Skript unerwartet ab, sagt die letzte Zeile, wo es aufhoerte -
# statt dass der ganze Lauf spurlos verschwindet.
_abbruch() {
  code=$?
  if [ "$code" -ne 0 ]; then
    merken "❌ ABBRUCH des Tagescheck (Code $code) - alles danach wurde NICHT geprueft."
    {
      echo "===== 4-Uhr-Check $STAMP (ABGEBROCHEN) ====="
      cat "$LAUFDATEI" 2>/dev/null
    } >> "$CHECKLOG" 2>/dev/null || true
  fi
}
trap _abbruch EXIT

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
    add "✅ API-Zwischenlager: $(tail -1 /tmp/api_cache_check.log)"
  else
    add "❌ API-Zwischenlager: $(tail -2 /tmp/api_cache_check.log | tr '\n' ' ')"
    problems+=("Das Zwischenlager des Bot-API-Servers reisst den Deckel — auch nach dem Aufraeumen zu gross.")
  fi
else
  add "~ API-Zwischenlager: kein eigener Bot-API-Server aktiv (5.34 nicht eingeschaltet)"
fi



# --- 9. Stundenblumen-Kette (lebt das System durchgehend?) ------------------
# Die Zeitpunkt-Pruefungen sagen nur etwas ueber diesen Augenblick. Die Kette
# belegt die Zeit DAZWISCHEN — und ihr Stillstand ist selbst der Befund.
if [ -f "$(dirname "$0")/stundenblume.py" ]; then
  if "${BOTENV[@]}" "$VENVPY" "$(dirname "$0")/stundenblume.py" --pruefen > /tmp/blumen_check.log 2>&1; then
    add "✅ Stundenblumen: $(tail -1 /tmp/blumen_check.log)"
  else
    add "❌ Stundenblumen: $(tail -1 /tmp/blumen_check.log)"
    problems+=("Die Stundenblumen-Kette steht still oder ist gebrochen: $(tail -1 /tmp/blumen_check.log)")
  fi
fi



# Kette rollen, wenn sie zu lang wird. Gemessen: 20160 Glieder = 3,2 MiB,
# --pruefen in 0,15 s - also Vorsorge, keine Not. Die Naht sorgt dafuer, dass
# das erste Glied der neuen Datei auf das letzte der alten zeigt.
if [ -f "$(dirname "$0")/stundenblume.py" ]; then
  gerollt=$("${BOTENV[@]}" "$VENVPY" "$(dirname "$0")/stundenblume.py" --rollen 2>/dev/null)
  # Ohne die Bot-Umgebung rollte root eine LEERE Kette unter /root - und
  # haette die echte nie angefasst. Ein Aufraeumen, das am falschen Ort
  # aufraeumt, sieht von aussen genauso aus wie eines, das funktioniert.
  [ -n "$gerollt" ] && add "📜 Belegkette beiseitegelegt: $gerollt"
fi

# --- 9e. FRISTMELDER: laeuft heute eine Betriebslage ab? -------------------
#
# Adams "erinnere mich" als Mechanik statt als Vorsatz (Entscheid 1a, 18.08.).
# GENERISCH gebaut: Jede Datei, die einen GILT-BIS-Stichtag traegt, meldet ihr
# eigenes Ende - nicht nur die Probewoche. Eine Frist, an die sich jemand
# erinnern muss, ist keine Frist.
#
# Gemeldet wird am Stichtag UND danach: Ein Melder, der nur am Tag X feuert,
# schweigt fuer immer, wenn der Lauf an Tag X ausfaellt. Genau das ist am
# 29.07. passiert.
HEUTE_ISO="$(date +%F)"
for frist_datei in "$BOTDIR"/*riegel*.md "$BOTDIR"/CLAUDE.md; do
  [ -f "$frist_datei" ] || continue
  bis="$(grep -oE '^[[:space:]]*GILT-BIS:[[:space:]]*[0-9]{4}-[0-9]{2}-[0-9]{2}' "$frist_datei" 2>/dev/null \
         | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)"
  [ -n "$bis" ] || continue
  if [ "$HEUTE_ISO" \> "$bis" ] || [ "$HEUTE_ISO" = "$bis" ]; then
    red "Frist abgelaufen: $(basename "$frist_datei") galt bis $bis — Auswertung faellig, danach Riegel bewusst neu setzen oder schliessen"
  else
    add "✅ Frist $(basename "$frist_datei"): laeuft bis $bis"
  fi
done

# --- 9d. ZEITGEBER-WACHE (Befund E aus Vorlage 5.21-E) ---------------------
#
# DIE LUECKE: Dieser Check prueft die DIENSTE - und keinen einzigen ZEITGEBER.
# Faellt einer aus (Fehler, Systemupdate, versehentliches Abschalten), laeuft
# das dahinter Liegende nie wieder. Und von aussen ist das NICHT von "diese
# Woche gab es nichts zu melden" zu unterscheiden. Genau die Signatur, die
# dieses Projekt am haeufigsten trifft: ein Ausbleiben, das wie Ruhe aussieht.
#
# Drei Instanzen haben diese Luecke unabhaengig voneinander gefunden. Der
# Selbstcheck im Bot prueft nur prozessinterne Worker; LastTriggerUSec prueft
# im ganzen Repo bisher niemand.
#
# DIE ZEITGEBER WERDEN GESUCHT, NICHT AUFGEZAEHLT. Eine feste Liste waere die
# Positivlisten-Falle: Der achte Zeitgeber fiele durch, und niemand merkte es -
# derselbe Fehler, den der Register-Waechter am 27.07. bei den Modulen fand.
#
# [KORRIGIERT 2026-07-28, B6] DIESER KOMMENTAR STAND HIER - UND DARUNTER STAND
# EINE POSITIVLISTE. Gefiltert wurde auf die Namensanfaenge claude-, hora und
# stundenblume. Das ist genau die Falle, vor der der Absatz warnt, nur in
# Verkleidung: Ein neunter Zeitgeber mit anderem Namen (engywuk, fuchur, ein
# Erinnerungs-Lauf) waere durchgefallen, und der Kommentar haette behauptet,
# er sei abgedeckt. Eine Vorgabe, die im Text steht und im Code nicht gilt,
# ist schlechter als keine - man verlaesst sich auf sie.
#
# DER EHRLICHE MASSSTAB IST NICHT DER NAME, SONDERN DAS ZIEL: Was in unser
# Verzeichnis zeigt, ist unseres. Gemessen (28.07.): Alle sieben eigenen
# Zeitgeber tragen /home/claudebot in ihrem ExecStart, und KEIN einziger
# System-Zeitgeber (apt-daily, fstrim, logrotate, e2scrub_all, dpkg-db-backup,
# systemd-tmpfiles-clean) tut das. Das Merkmal trennt sauber und ueberlebt
# jede Umbenennung.
UNSER_PFAD="${UNSER_PFAD:-/home/claudebot}"
zeitgeber_still=()
while read -r t; do
  [ -n "$t" ] || continue
  # **Bewusst Abgeschaltetes ist kein Befund** (Befund B5 der Gegenpruefung,
  # sofort belegt): Die erweiterte Suche fand `kostenkontrolle-reminder.timer`
  # — eine Altlast vom 14.07., die sich nach ihrer Frist selbst deaktiviert hat
  # und seither `disabled` ist. Ohne diesen Ausweg meldete die Wache sie ab
  # heute TAEGLICH als still, und ein Waechter, der jeden Tag grundlos rot
  # meldet, wird abgeschaltet.
  #
  # Die Absicht steht in systemd selbst: Wer `disable` gesagt hat, hat es
  # gewollt. Verdaechtig ist nur `enabled` und trotzdem nicht aktiv - dann ist
  # etwas ausgefallen, statt abgestellt worden zu sein. Keine Pflegeliste
  # noetig, keine zweite Wahrheit.
  zustand=$(systemctl show "$t" -p UnitFileState --value 2>/dev/null)
  aktiv=$(systemctl is-active "$t" 2>/dev/null)
  if [ "$aktiv" != "active" ]; then
    if [ "$zustand" = "disabled" ] || [ "$zustand" = "masked" ]; then
      add "✅ Zeitgeber $t: bewusst abgeschaltet ($zustand)"
    else
      zeitgeber_still+=("$t ist $aktiv (Unit-Zustand: ${zustand:-unbekannt})")
    fi
    continue
  fi
  # GEMESSEN WIRD DER NAECHSTE LAUF, NICHT DAS ALTER DES LETZTEN.
  #
  # Mein erster Entwurf hatte eine feste Schwelle von 26 Stunden - und haette
  # beim ERSTEN Lauf einen Fehlalarm erzeugt: Der Versions-Monitor laeuft
  # WOECHENTLICH (montags), sein letzter Lauf lag also zu Recht 33 Stunden
  # zurueck. Eine geratene Schwelle kann den Takt nicht kennen; systemd kennt
  # ihn. Also fragt man systemd, statt zu rechnen.
  #
  # Ein Zeitgeber ist genau dann auffaellig, wenn sein naechster Lauf
  # UEBERFAELLIG ist - das gilt fuer minuetlich, taeglich und woechentlich
  # gleichermassen, ohne eine einzige Zahl im Code.
  # **Ein Zeitgeber, dessen Dienst GERADE LAEUFT, ist nicht still.**
  #
  # GEMESSEN 19.08.2026 im ersten automatischen Lauf nach der Reparatur: Der
  # Tagescheck klagte seinen EIGENEN Zeitgeber an - "aktiv, hat aber KEINEN
  # naechsten Lauf geplant". Die Ursache ist Selbstbezug: systemd fuehrt einen
  # Timer, dessen Dienst laeuft, im SubState `running`, und dort gibt es kein
  # NextElapse. Der Tagescheck prueft sich aber genau waehrend seines eigenen
  # Laufs - er ist der einzige Timer, der sich in diesem Zustand selbst sieht.
  # Alle anderen stehen dann auf `waiting`.
  #
  # Ein taeglicher Fehlalarm, ausgerechnet auf den Waechter, der alle anderen
  # prueft. Und Fehlalarme schalten Waechter zuverlaessiger ab als Defekte.
  substate=$(systemctl show "$t" -p SubState --value 2>/dev/null)
  if [ "$substate" = "running" ]; then
    add "✅ Zeitgeber $t: laeuft gerade"
    continue
  fi
  naechste=$(systemctl show "$t" -p NextElapseUSecRealtime --value 2>/dev/null)
  if [ -z "$naechste" ] || [ "$naechste" = "n/a" ] || [ "$naechste" = "0" ]; then
    # **Monotone Zeitgeber tragen ihren naechsten Lauf woanders** (Befund B4 der
    # Gegenpruefung): Bei OnBootSec/OnUnitActiveSec ist die Realzeit-Angabe
    # leer, nur die monotone traegt. Ohne diesen Zweig wuerde ein voellig
    # gesunder Zeitgeber taeglich angeklagt.
    mono=$(systemctl show "$t" -p NextElapseUSecMonotonic --value 2>/dev/null)
    if [ -n "$mono" ] && [ "$mono" != "0" ] && [ "$mono" != "n/a" ]; then
      add "✅ Zeitgeber $t: naechster Lauf monoton geplant"
      continue
    fi
    zeitgeber_still+=("$t ist aktiv, hat aber KEINEN naechsten Lauf geplant")
    continue
  fi
  naechste_s=$(date -d "$naechste" +%s 2>/dev/null || echo 0)
  if [ "$naechste_s" -gt 0 ]; then
    ueberfaellig=$(( ($(date +%s) - naechste_s) / 60 ))
    # Kleine Toleranz: systemd verschiebt Laeufe um Sekunden bis Minuten
    # (AccuracySec, RandomizedDelaySec). Erst ab einer Viertelstunde Verzug
    # ist es keine Ungenauigkeit mehr, sondern ein Stillstand.
    if [ "$ueberfaellig" -gt 15 ]; then
      zeitgeber_still+=("$t ist seit $ueberfaellig Minuten ueberfaellig")
    fi
  fi
done < <( { systemctl list-timers --all --no-pager 2>/dev/null \
             | awk '$NF ~ /\.(service|timer)$/ {print $NF}' \
             | sed 's/\.service$/.timer/'
           # **Auch die Zeitgeber von der PLATTE** (Befund B1 der Gegenpruefung,
           # 18.08.): `list-timers` zeigt nur, was systemd GELADEN hat. Wird eine
           # Unit-Datei geloescht oder per `disable --now` entfernt, taucht sie
           # nach dem naechsten daemon-reload gar nicht mehr auf - und die Wache
           # meldet "alle aktiv und in ihrem Takt". Das ist exakt die Signatur,
           # gegen die sie gebaut wurde, nur eine Ebene hoeher.
           ls /etc/systemd/system/*.timer 2>/dev/null | xargs -n1 basename 2>/dev/null
         } | sort -u \
         | while read -r kandidat; do
             dienst="${kandidat%.timer}.service"
             # **Kein Ein-Eintrag-Pfadfilter mehr** (Engywucks Befund F): Der
             # alte prueft nur gegen /home/claudebot. Ein eigener Zeitgeber, der
             # aus /opt oder /usr/local startet, fiele still durch - und die
             # Begruendung dafuer war eine Momentaufnahme ("alle sieben tragen
             # /home/claudebot"), zitiert als Invariante.
             ziel=$(systemctl show "$dienst" -p ExecStart --value 2>/dev/null)
             if printf '%s' "$ziel" | grep -qE "$UNSER_PFAD|/opt/|/usr/local/"; then
               echo "$kandidat"
             fi
           done)

if [ "${#zeitgeber_still[@]}" -eq 0 ]; then
  add "✅ Zeitgeber: alle aktiv und in ihrem Takt"
else
  add "❌ Zeitgeber: ${zeitgeber_still[*]}"
  problems+=("Ein Zeitgeber steht still - was dahinter haengt, laeuft nicht mehr, und das sieht von aussen aus wie Ruhe: ${zeitgeber_still[*]}")
fi

# --- 9b. Haertung: verfaellt sie still? (9.11 Punkt 1) ---------------------
# Der Sinn dieser Zeilen ist NICHT, Haertung einzurichten - die steht laengst.
# Der Sinn ist, dass eine ZURUECKGENOMMENE Haertung auffaellt. Bisher waere ein
# entfernter Schutz niemandem aufgefallen; genau das ist die Klasse "Vorgabe da,
# Pruefung fehlt", die dieses Projekt fuenfmal in zwei Tagen getroffen hat.
haertung_fehlt=()
for eigenschaft in NoNewPrivileges:yes PrivateTmp:yes ProtectSystem:strict; do
  name="${eigenschaft%%:*}"; soll="${eigenschaft##*:}"
  ist=$(systemctl show claude-telegram-bot -p "$name" --value 2>/dev/null)
  [ "$ist" = "$soll" ] || haertung_fehlt+=("$name=$ist statt $soll")
done
if systemctl is-enabled fail2ban >/dev/null 2>&1; then :; else
  haertung_fehlt+=("fail2ban nicht eingeschaltet")
fi
if [ "${#haertung_fehlt[@]}" -eq 0 ]; then
  add "✅ Haertung unveraendert (NoNewPrivileges, PrivateTmp, ProtectSystem, fail2ban)"
else
  add "❌ Haertung: ${haertung_fehlt[*]}"
  problems+=("Eine Haertung wurde zurueckgenommen: ${haertung_fehlt[*]}")
fi

# Offene Anschluesse: alles, was NICHT nur lokal lauscht, wird benannt. SSH und
# der Webhook-Port sind erwartet - jeder weitere ist ein Befund, denn nach
# CLAUDE.md gilt: kein eingehender Port ausser den ausdruecklich gewollten.
unerwartet=$(ss -lntH 2>/dev/null \
  | awk '{print $4}' \
  | grep -vE '^(127\.0\.0\.1|\[::1\])' \
  | grep -vE ':(22|8443)$' | sort -u | tr '\n' ' ')
if [ -n "${unerwartet// /}" ]; then
  add "❌ Unerwartet offene Anschluesse: $unerwartet"
  problems+=("Es lauschen Anschluesse nach aussen, die dort nicht hingehoeren: $unerwartet")
else
  add "✅ Nach aussen lauschen nur SSH und der Webhook-Port"
fi

# 1.9 rote Auflage C.1, dritter Teil: Der Webhook-Port soll auf Telegrams Netze
# beschraenkt sein. Geheimnis-Token und unerratbarer Pfad erzwingt der Bot beim
# Start selbst (er startet sonst nicht) - die Firewall-Regel tut das niemand.
if [ "${BOT_MODE:-polling}" = "webhook" ]; then
  if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q '149.154.160.0/20'; then
    add "✅ Webhook-Port auf Telegram-Netze beschraenkt"
  else
    add "~ Webhook-Port 8443 ist fuer JEDE Adresse erreichbar. Der Geheimnis-Token weist fremde Rufe ab - die Auflage 1.9 C.1 nennt zusaetzlich die Firewall-Beschraenkung auf 149.154.160.0/20 und 91.108.4.0/22. Braucht root, siehe docs/befehlsbloecke-root.md."
  fi
fi

# --- 9c. Erreicht Telegram uns noch? ---------------------------------------
# Der Bot fragt selbst nach (er hat den Schluessel ohnehin) und legt bei
# Stoerung eine Marke. Hier wird nur die Marke gelesen - kein zweiter Ort fuer
# ein Geheimnis, dieselbe Bauart wie bei der Anmeldung.
ZUSTELLMARKE="$BOTHOME/.claude/zustellung-gestoert"
if [ -f "$ZUSTELLMARKE" ]; then
  grund=$("$VENVPY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('grund','ohne Angabe'))" "$ZUSTELLMARKE" 2>/dev/null)
  add "❌ Zustellung gestoert: $grund"
  problems+=("Telegram erreicht uns nicht mehr zuverlaessig: $grund — der Bot laeuft, aber es kommt womoeglich nichts mehr an.")
else
  add "✅ Zustellung: keine Stoerung vermerkt"
fi

# --- 10. Vorraete: Speicher, Platte, Auslagerung ---------------------------
# Werte-Charta 7a: "Was vorhersehbar knapp wird, wird beobachtet, BEVOR es
# knapp ist." Der Unterschied zu den Stundenblumen ist die Absicht — die Blume
# schlaegt Alarm, wenn es eng WIRD; diese Zeile schreibt den Stand jeden Tag
# mit, damit man die ENTWICKLUNG sieht. Ein Wert, den man nur im Notfall
# ansieht, hat keine Geschichte, und ohne Geschichte gibt es keine Vorwarnung.
if [ -r /proc/meminfo ]; then
  mem_verf=$(awk '/^MemAvailable:/{print int($2/1024)}' /proc/meminfo)
  mem_ges=$(awk '/^MemTotal:/{print int($2/1024)}' /proc/meminfo)
  swap_ges=$(awk '/^SwapTotal:/{print int($2/1024)}' /proc/meminfo)
  swap_frei=$(awk '/^SwapFree:/{print int($2/1024)}' /proc/meminfo)
  swap_benutzt=$(( swap_ges - swap_frei ))
  platte_frei=$(df -BG --output=avail / 2>/dev/null | tail -1 | tr -dc '0-9')
  add "📊 Vorraete: ${mem_verf} von ${mem_ges} MiB Speicher verfuegbar · ${platte_frei:-?} GiB Platte frei · Auslagerung ${swap_benutzt} von ${swap_ges} MiB benutzt"
  if [ "${mem_verf:-9999}" -lt 400 ]; then
    problems+=("Nur noch ${mem_verf} MiB Arbeitsspeicher verfuegbar — in diesem Bereich beendet der Kernel Prozesse ohne Vorwarnung.")
  fi
  if [ "${swap_ges:-0}" -eq 0 ]; then
    add "~ Kein Auslagerungsbereich eingerichtet — bei Speichermangel gibt es kein Abfedern, nur den OOM-Killer (Befehlsblock Schritt 4a)."
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
  # `${uids[@]}` bricht bei LEEREM Array mit `set -u` ab - und zwar hier, in
  # der Meldephase. Gefunden am 18.08. vom neuen Zielumgebungs-Pruefer beim
  # allerersten Lauf. Ohne Rueckfall waere die Meldung genau dann
  # ausgeblieben, wenn die Empfaengerliste fehlt - also im Stoerfall.
  for uid in "${uids[@]:-}"; do
    [ -n "$uid" ] || continue
    [ -n "$uid" ] || continue
    curl -s -m 15 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      --data-urlencode "chat_id=${uid}" \
      --data-urlencode "text=${report}" >/dev/null 2>&1
  done
  echo "Probleme gemeldet: ${#problems[@]}"
else
  echo "Alles grün — keine Meldung."
fi
