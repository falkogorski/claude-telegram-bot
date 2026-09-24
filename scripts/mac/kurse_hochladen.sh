#!/bin/bash
# <!-- ROLLE: kurse-hochladen -->
#
# Kurs-Videos vom Mac auf den VPS und dort die Transkription anstoßen.
#
# `[NEU 24.09.2026]` Adams Entscheid (Engywucks Zettel F2): Weg Mac → VPS per
# rsync, lokal transkribiert mit faster-whisper, Ablage `wissen/kurse/`.
# **Nie über einen Fremddienst** — der Transport läuft über den vorhandenen
# SSH-Zugang, sonst nichts.
#
# Aufruf:   bash scripts/mac/kurse_hochladen.sh <Ordner-oder-Datei> [Kursname]
# Beispiel: bash scripts/mac/kurse_hochladen.sh ~/Kurse/Verkaufskurs
#
# Ohne Kursname gilt der Name des Ordners. Auf dem VPS landet alles unter
# ~/kurse-eingang/<Kursname>/, als Benutzer claudebot (Eintrag `claudebot` in
# ~/.ssh/config) — also mit dessen Besitzrechten, nicht als root.
#
# Danach startet der VPS `scripts/kurse.py` im Hintergrund, mit niedrigster
# Priorität. Die Fertigmeldung kommt über den Bot. Bleibt sie aus, meldet es
# der Tagescheck nach sechs Stunden.
set -uo pipefail

SSH_HOST="${KURSE_SSH_HOST:-claudebot}"
ZIEL="kurse-eingang"
BOTDIR="/home/claudebot/claude-telegram-bot"

quelle="${1:-}"
if [ -z "$quelle" ] || [ ! -e "$quelle" ]; then
  echo "Aufruf: bash scripts/mac/kurse_hochladen.sh <Ordner-oder-Datei> [Kursname]" >&2
  exit 2
fi
kurs="${2:-$(basename "${quelle%/}")}"
[ -f "$quelle" ] && [ -z "${2:-}" ] && kurs="Einzelvideos"
# Der Kursname wird ein Ordnername auf dem Server: nur harmlose Zeichen, auch
# kein Leerzeichen — der Zielpfad geht durch die Fern-Shell, und ein
# Leerzeichen dort zerlegt ihn in zwei Argumente.
kurs="$(printf '%s' "$kurs" | tr -c 'A-Za-z0-9._-' '_' | sed 's/^[._]*//')"
[ -n "$kurs" ] || kurs="Kurs"

if ! ssh -o BatchMode=yes -o ConnectTimeout=10 "$SSH_HOST" "mkdir -p ~/$ZIEL/'$kurs'"; then
  echo "FEHLER: [$SSH_HOST] antwortet nicht — Eintrag in ~/.ssh/config?" >&2
  exit 1
fi

# -rlt statt -a: Besitzer und Gruppe nicht vom Mac übernehmen.
# --partial-dir mit Punkt vorn: Ein abgebrochener Upload großer Videos setzt
# beim nächsten Aufruf fort — und das halbe Video liegt dabei in einem
# VERSTECKTEN Ordner, den kurse.py überspringt. Mit bloßem --partial läge es
# unter seinem echten Namen, und ein späterer Lauf hätte es halb transkribiert
# und als fertig geführt. (openrsync auf dem Mac kann --partial-dir, gemessen.)
# Das Ende des Quellpfads entscheidet: Ordner → dessen INHALT, Datei → sie selbst.
if [ -d "$quelle" ]; then src="${quelle%/}/"; else src="$quelle"; fi
echo "Übertrage nach $SSH_HOST:~/$ZIEL/$kurs/ …"
if ! rsync -rlt --partial-dir=.rsync-teil --progress -e "ssh -o BatchMode=yes" \
      --exclude='.*' "$src" "$SSH_HOST:$ZIEL/$kurs/"; then
  echo "FEHLER: Übertragung abgebrochen. Erneut aufrufen setzt fort." >&2
  exit 1
fi

ssh -o BatchMode=yes "$SSH_HOST" \
  "cd $BOTDIR && nohup nice -n 19 .venv/bin/python3 scripts/kurse.py >> logs/kurse.log 2>&1 < /dev/null &"
echo "Übertragen. Die Transkription läuft auf dem VPS; die Fertigmeldung kommt über den Bot."
