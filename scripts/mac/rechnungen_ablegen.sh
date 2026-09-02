#!/bin/bash
# <!-- ROLLE: rechnungen-ablegen -->
#
# Holt fertige Rechnungen und Aufstellungen vom Server und legt sie in iCloud
# ab — **Route A** aus Claudias Bauauftrag vom 02.09., Adams Entscheid
# („zunaechst Route A, spaeter B").
#
# ══════════════════════════════════════════════════════════════════════════
# WARUM BEIDE HAELFTEN IN EINEM SKRIPT LAUFEN — Abweichung von der Vorlage
# ══════════════════════════════════════════════════════════════════════════
#
# Engywucks Nachtrag sah zwei getrennte Haelften vor: Server → Mac-Platte als
# **Zeitgeber** (darf), Mac-Platte → iCloud unter **Claude Code** (muss, weil
# `launchd` Adams iCloud-Freigabe nicht erbt).
#
# **Die Trennung stimmt, der Zeitgeber bringt nichts.** Wenn die zweite
# Haelfte ohnehin auf den Sitzungsstart wartet, ist die Kette genau so
# schnell wie der Sitzungsstart — ein Zeitgeber davor beschleunigt nichts,
# er erzeugt nur eine zweite Stelle, die stillschweigend ausfallen kann.
# Genau das war der `mirror-ki`: 330 Laeufe, alle gescheitert, drei Monate
# unbemerkt.
#
# Deshalb: **beide Haelften hier, beide beim Sitzungsstart und auf Zuruf.**
# Als Sicherheitsnetz laeuft der Ausgangsordner zusaetzlich im taeglichen
# `vps_backup.sh` mit (eine Zeile in dessen ITEMS) — falls tagelang keine
# Sitzung startet, liegen die Dateien wenigstens auf der Platte.
#
# ══════════════════════════════════════════════════════════════════════════
# WAS ADAM WISSEN MUSS — ehrlich, weil es seine Erwartung betrifft
# ══════════════════════════════════════════════════════════════════════════
#
# Die Rechnung liegt in iCloud, **sobald die naechste Sitzung startet oder
# Adam „ablegen" sagt** — nicht Minuten nach dem Erzeugen. Fuer eine Rechnung,
# die am selben Tag rausgeht, reicht das. Ein naechtlicher Lauf ohne Sitzung
# legt nichts ab. **Genau deshalb hat Adam „spaeter B" gesagt, und das bleibt
# richtig.**
#
# ══════════════════════════════════════════════════════════════════════════
# DAS ZIEL IN iCLOUD IST EIN UEBERGABEORDNER, KEINE ABLAGE
# ══════════════════════════════════════════════════════════════════════════
#
# Gemessen am 02.09.: In iCloud gibt es **keinen** Rechnungsordner. Es gibt
# eine gewachsene Kundenstruktur (`Business/Deko/DEKO-Service/<Kunde>/`), und
# der Generator kennt sie nicht — er legt nach `output/` ab, mehr nicht. Das
# Einsortier-Schema aus 5.19 („Benennungsschema je Zweig") ist NICHT gebaut.
#
# **Ein geratener Zielordner haette in Adams gewachsene Ablage
# hineingeschrieben.** Deshalb stellt dieses Skript zu und sortiert nicht ein:
# Alles landet in EINEM Uebergabeordner, aus dem Adam einsortiert — oder er
# sagt, wohin direkt, dann wird `RECHNUNGEN_ICLOUD` gesetzt. Zustellen ja,
# Einsortieren nein.
#
# GRUNDSATZ, aus `icloud_spiegel.sh`: **kopieren, nie loeschen.** Kein
# `--delete`. Eine Datei zu viel ist harmlos, eine fehlende nicht.
#
# JEDER LAUF SCHREIBT EINE ZEILE — auch ohne Arbeit, erst recht bei Scheitern.
# Eine Logdatei, die nicht mehr waechst, ist selbst das Alarmzeichen.

set -u

# HOME benannt einfordern: Unter `set -u` bricht `$HOME` ohne HOME mit
# "unbound variable" ab — auch in einem Rueckfall wie `${VAR:-$HOME/x}`.
# Daran starb am 29.07. ein Waechter, einundzwanzig Tage unbemerkt.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"

SSH_HOST="${RECHNUNGEN_SSH_HOST:-claudebot@vps}"
FERN="${RECHNUNGEN_FERN:-/home/claudebot/workspace/rechnungen/ausgang/}"
LOKAL="${RECHNUNGEN_LOKAL:-$HOME/VPS-Backup/rechnungen}"
ZIEL="${RECHNUNGEN_ICLOUD:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/Business/Deko/DEKO-Service/_Aus-dem-Server}"
LOG="${RECHNUNGEN_LOG:-$HOME/.claude/rechnungen-ablegen.log}"

mkdir -p "$(dirname "$LOG")" 2>/dev/null
sag() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

# ---------------------------------------------------------------- Haelfte 1
#
# Server → Mac-Platte. Darf scheitern, ohne die zweite Haelfte aufzuhalten:
# Ein ausgeschalteter Mac, ein fehlender SSH-Schluessel oder ein noch nicht
# umgezogenes Projekt sind kein Grund, liegengebliebene Dateien nicht
# abzulegen. **Aber es steht im Protokoll** — stilles Scheitern ist der
# Fehler, gegen den dieses ganze Skript gebaut ist.
mkdir -p "$LOKAL" 2>/dev/null || { sag "FEHLER: Uebergabeordner nicht anlegbar — $LOKAL"; exit 78; }

if command -v rsync >/dev/null 2>&1; then
  if rsync -az --timeout=20 -e "ssh -o BatchMode=yes -o ConnectTimeout=10" \
      "$SSH_HOST:$FERN" "$LOKAL/" 2>>"$LOG"; then
    sag "Haelfte 1: vom Server geholt ($SSH_HOST:$FERN)"
  else
    sag "Haelfte 1 UEBERSPRUNGEN: Server nicht erreichbar oder Ordner fehlt"
    sag "        (Solange das Rechnungsprojekt nicht umgezogen ist, ist das"
    sag "         der Normalfall — nicht der Alarm.)"
  fi
else
  sag "Haelfte 1 UEBERSPRUNGEN: rsync fehlt auf diesem Rechner"
fi

# ---------------------------------------------------------------- Haelfte 2
#
# Mac-Platte → iCloud. **Nur hier greift Adams TCC-Freigabe** — dieses Skript
# laeuft unter Claude.app, nicht unter `launchd`. Die beiden Vorbilder
# (`icloud_spiegel.sh`, `icloud_backup.sh`) LESEN aus iCloud; dieses schreibt
# hinein. **Die Freigabe gilt in beide Richtungen — beim ersten Lauf geprueft,
# nicht angenommen.**
_eltern="$(dirname "$ZIEL")"
if [ ! -d "$_eltern" ]; then
  sag "FEHLER: iCloud-Elternordner fehlt — $_eltern"
  sag "        Entweder ist iCloud nicht eingehaengt, oder die Freigabe fehlt,"
  sag "        oder Adams Ablage heisst inzwischen anders. NICHT geraten:"
  sag "        setze RECHNUNGEN_ICLOUD auf den gewuenschten Ordner."
  exit 78
fi
if ! mkdir -p "$ZIEL" 2>>"$LOG"; then
  sag "FEHLER: iCloud-Zielordner nicht anlegbar (TCC?) — $ZIEL"
  exit 78
fi

_anzahl=$(find "$LOKAL" -type f ! -name '.*' 2>/dev/null | wc -l | tr -d ' ')
if [ "$_anzahl" -eq 0 ]; then
  sag "nichts abzulegen (Uebergabeordner leer) — Lauf war trotzdem da"
  exit 0
fi

# Kein --delete, und `-u`: Neueres ueberschreibt Aelteres, Gleichnamiges mit
# gleicher Zeit bleibt liegen. Die Rechnungsnummer steht im Dateinamen, ein
# echter Doppelgaenger kann also nur dieselbe Rechnung sein.
if rsync -a -u --exclude='.*' "$LOKAL/" "$ZIEL/" 2>>"$LOG"; then
  sag "Haelfte 2: $_anzahl Datei(en) nach iCloud gelegt — $ZIEL"
else
  sag "FEHLER: Ablage nach iCloud gescheitert — $ZIEL"
  exit 78
fi
