#!/usr/bin/env bash
# Guardian: hält den Bot lebendig — zweistufig.
#
# Stufe 1 (alt): Ist der Bot bei launchd registriert? Falls nicht → laden.
# Stufe 2 (neu): Lebt der Bot wirklich? Heartbeat-Datei wird alle 30s vom Bot
#                geschrieben. Älter als HEARTBEAT_MAX_AGE_S → Wedge erkannt:
#                Prozess hart killen (KeepAlive von launchd zieht ihn neu hoch),
#                Restart-Reason für die Telegram-Bestätigung hinterlegen.
#
# Läuft alle 60s via eigenem LaunchAgent.
set -euo pipefail

BOT_LABEL="com.jakuna.claude-telegram-bot"
PLIST="$HOME/Library/LaunchAgents/${BOT_LABEL}.plist"
LOG="$HOME/Projects/claude-telegram-bot/logs/guardian.log"
HEARTBEAT="$HOME/.claude/bot-heartbeat.txt"
RESTART_REASON="$HOME/.claude/bot-restart-reason.txt"

# Schwelle: 180s = sechs Heartbeats verpasst. Heartbeat-Intervall ist 30s,
# zwei verpasste Schreibvorgänge sind noch normales Rauschen, ab sechs gilt
# der Bot als hängend.
HEARTBEAT_MAX_AGE_S=180

# Sekunden in einen menschenlesbaren Relativ-Ausdruck verwandeln.
# Spec siehe Memory: feedback-time-statements.md (Finale Spec, Adam 2026-06-30).
# Fünf Regeln: exakte Marken pur, Nähe-Marken mit Modifier, dazwischen präzise
# Zahl, ab 2h Marken in Halb-Schritten, Tage/Wochen ohne Auflistung.
human_age() {
    local s=$1

    # --- Unter einer Minute ---
    if [ "$s" -lt 60 ]; then
        if [ "$s" -eq 1 ]; then
            printf 'vor einer Sekunde'
        elif [ "$s" -eq 30 ]; then
            printf 'vor einer halben Minute'
        else
            printf 'vor %d Sekunden' "$s"
        fi
        return
    fi

    # --- Minutenbereich (60s bis < 2h) ---
    if [ "$s" -lt 7200 ]; then
        # Kaufmännisch auf nächste Minute runden.
        local m=$(( (s + 30) / 60 ))

        # Exakte Marken — schlicht, ohne "etwa".
        case "$m" in
            1)   printf 'vor einer Minute'; return ;;
            15)  printf 'vor einer Viertelstunde'; return ;;
            30)  printf 'vor einer halben Stunde'; return ;;
            45)  printf 'vor einer Dreiviertelstunde'; return ;;
            60)  printf 'vor einer Stunde'; return ;;
            90)  printf 'vor anderthalb Stunden'; return ;;
            120) printf 'vor 2 Stunden'; return ;;
        esac

        # Marken-Nähe (±2 Min) mit Modifier.
        if [ "$m" -ge 13 ] && [ "$m" -le 17 ]; then
            printf 'vor etwa einer Viertelstunde'; return
        fi
        if [ "$m" -ge 28 ] && [ "$m" -le 32 ]; then
            printf 'vor etwa einer halben Stunde'; return
        fi
        if [ "$m" -ge 43 ] && [ "$m" -le 47 ]; then
            printf 'vor etwa einer Dreiviertelstunde'; return
        fi
        if [ "$m" -ge 55 ] && [ "$m" -le 59 ]; then
            printf 'vor einer knappen Stunde'; return
        fi
        if [ "$m" -ge 61 ] && [ "$m" -le 65 ]; then
            printf 'vor einer guten Stunde'; return
        fi
        if [ "$m" -ge 85 ] && [ "$m" -le 95 ]; then
            printf 'vor etwa anderthalb Stunden'; return
        fi
        if [ "$m" -ge 110 ] && [ "$m" -le 119 ]; then
            printf 'vor knapp 2 Stunden'; return
        fi

        # Zwischen den Marken: präzise Zahl, kein "etwa".
        if [ "$m" -lt 60 ]; then
            printf 'vor %d Minuten' "$m"; return
        fi

        # 1h bis < 2h, fernab jeder Marke: "vor einer Stunde X Minuten".
        local rem=$((m - 60))
        if [ "$rem" -eq 1 ]; then
            printf 'vor einer Stunde 1 Minute'
        else
            printf 'vor einer Stunde %d Minuten' "$rem"
        fi
        return
    fi

    # --- Stundenbereich (2h bis < 24h) ---
    if [ "$s" -lt 86400 ]; then
        local h=$((s / 3600))
        local rem_m=$(( (s % 3600) / 60 ))

        # Exakte Stunde.
        if [ "$rem_m" -eq 0 ]; then
            printf 'vor %d Stunden' "$h"; return
        fi

        # 50-59 Restminuten → "knapp h+1 Stunden".
        if [ "$rem_m" -ge 50 ]; then
            local h_next=$((h + 1))
            if [ "$h_next" -eq 24 ]; then
                printf 'vor knapp einem Tag'; return
            fi
            printf 'vor knapp %d Stunden' "$h_next"; return
        fi

        # 25-40 Restminuten → "h½ Stunden" (genau bei 30 ohne "etwa").
        if [ "$rem_m" -ge 25 ] && [ "$rem_m" -le 40 ]; then
            if [ "$rem_m" -eq 30 ]; then
                printf 'vor %d½ Stunden' "$h"; return
            fi
            printf 'vor etwa %d½ Stunden' "$h"; return
        fi

        # 41-49 → leicht über ½, noch nicht "knapp h+1".
        if [ "$rem_m" -ge 41 ] && [ "$rem_m" -le 49 ]; then
            printf 'vor etwa %d½ Stunden' "$h"; return
        fi

        # 1-24 Restminuten → "etwa h Stunden".
        printf 'vor etwa %d Stunden' "$h"; return
    fi

    # --- Tagebereich (1 Tag bis < 14 Tage) ---
    if [ "$s" -lt 1209600 ]; then
        local d=$((s / 86400))
        local rem_h=$(( (s % 86400) / 3600 ))

        # Tag 1 — gesondert, weil "anderthalb Tagen" hier sitzt.
        if [ "$d" -eq 1 ]; then
            if [ "$rem_h" -lt 6 ]; then
                printf 'vor einem Tag'; return
            elif [ "$rem_h" -le 18 ]; then
                printf 'vor anderthalb Tagen'; return
            else
                printf 'vor 2 Tagen'; return
            fi
        fi

        # Tag 2 — analog für "zweieinhalb Tagen".
        if [ "$d" -eq 2 ]; then
            if [ "$rem_h" -lt 6 ]; then
                printf 'vor 2 Tagen'; return
            elif [ "$rem_h" -le 18 ]; then
                printf 'vor zweieinhalb Tagen'; return
            else
                printf 'vor 3 Tagen'; return
            fi
        fi

        # Ab dem dritten Tag: schlichte Rundung, Restzeit ≥ 12h hebt an.
        if [ "$rem_h" -ge 12 ]; then
            d=$((d + 1))
        fi

        # Rundung kann auf 14 Tage springen — dann lieber Wochen.
        if [ "$d" -ge 14 ]; then
            printf 'vor 2 Wochen'; return
        fi

        if [ "$d" -eq 5 ] || [ "$d" -eq 6 ]; then
            printf 'vor knapp einer Woche'; return
        fi
        if [ "$d" -eq 7 ]; then
            printf 'vor einer Woche'; return
        fi

        printf 'vor %d Tagen' "$d"; return
    fi

    # --- Wochenbereich (ab 14 Tage) ---
    local w=$((s / 604800))
    local rem_d=$(( (s % 604800) / 86400 ))

    # Rest ≥ 4 Tage hebt auf nächste Woche an.
    if [ "$rem_d" -ge 4 ]; then
        w=$((w + 1))
    fi

    if [ "$w" -eq 1 ]; then
        printf 'vor einer Woche'; return
    fi
    printf 'vor %d Wochen' "$w"
}

ts() { date "+%Y-%m-%d %H:%M:%S"; }

# ---------- Stufe 1: launchd-Registrierung ----------
if ! launchctl list | grep -q "${BOT_LABEL}"; then
    if [ ! -f "$PLIST" ]; then
        echo "$(ts) plist file missing at $PLIST — cannot recover" >> "$LOG"
        exit 1
    fi
    echo "$(ts) bot not loaded — running launchctl load" >> "$LOG"
    if launchctl load "$PLIST" 2>>"$LOG"; then
        echo "$(ts) launchctl load OK" >> "$LOG"
    else
        echo "$(ts) launchctl load FAILED" >> "$LOG"
    fi
    exit 0
fi

# ---------- Stufe 2: Heartbeat-Frische ----------
# Frühphase (Bot gerade erst gestartet): Heartbeat-Datei existiert noch nicht.
# Eine Runde Schonfrist gewähren, kein Alarm.
if [ ! -f "$HEARTBEAT" ]; then
    echo "$(ts) heartbeat file missing — granting grace period" >> "$LOG"
    exit 0
fi

now=$(date +%s)
mtime=$(stat -f %m "$HEARTBEAT" 2>/dev/null || echo 0)
age=$((now - mtime))

if [ "$age" -le "$HEARTBEAT_MAX_AGE_S" ]; then
    # Alles in Ordnung — schweigsam beenden, damit das Log nicht zumüllt.
    exit 0
fi

# Wedge erkannt. PID des Bots ermitteln und hart beenden.
BOT_PID=$(launchctl list | awk -v label="$BOT_LABEL" '$3 == label {print $1}')

echo "$(ts) WEDGE: heartbeat age ${age}s > ${HEARTBEAT_MAX_AGE_S}s — killing pid=${BOT_PID}" >> "$LOG"

# Restart-Reason für die Telegram-Bestätigung hinterlegen. Wird beim Neustart
# vom Bot gelesen und gelöscht — damit Adam genau diesen Fall mitbekommt.
cat > "$RESTART_REASON" <<EOF
Der Bot lag still — ich habe ihn gerade wieder hochgefahren. Letztes Lebenszeichen: $(human_age "$age").

Wenn du gerade etwas geschickt hattest, das nicht verarbeitet wurde, schick es bitte einfach noch einmal — die Verbindung steht wieder.
EOF

if [ "$BOT_PID" != "-" ] && [ -n "${BOT_PID:-}" ]; then
    kill -9 "$BOT_PID" 2>>"$LOG" || echo "$(ts) kill -9 failed (pid=${BOT_PID})" >> "$LOG"
    echo "$(ts) sent SIGKILL — launchd KeepAlive should restart shortly" >> "$LOG"
else
    echo "$(ts) could not determine bot pid — relying on launchctl kickstart" >> "$LOG"
    launchctl kickstart -k "gui/$(id -u)/${BOT_LABEL}" 2>>"$LOG" || true
fi
