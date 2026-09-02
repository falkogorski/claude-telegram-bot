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

# Der Name kommt aus `~/.ssh/config` (Eintrag `claudebot`, User claudebot),
# NICHT aus einer erfundenen Adresse. `vps_backup.sh` macht es mit
# `claudevps` (root) genauso. **Am 02.09. stand hier `claudebot@vps` —
# ein Name, den dieser Rechner nicht aufloest.** Haelfte 1 haette still
# jedes Mal "uebersprungen" protokolliert, und niemand haette gemerkt,
# dass es nie am Server lag: der Ausfall haette wie Ruhe ausgesehen.
SSH_HOST="${RECHNUNGEN_SSH_HOST:-claudebot}"
FERN="${RECHNUNGEN_FERN:-/home/claudebot/workspace/rechnungen/ausgang/}"
LOKAL="${RECHNUNGEN_LOKAL:-$HOME/VPS-Backup/rechnungen}"
# **Der Kundenzweig, NICHT ein Kundenordner** — Adams Entscheid vom 02.09.:
# *„unter deko-service nur rechnungen an deko-service … ordner für aktuelle
# rechnung lautet livesetup"*. Ein fester Zielordner kann nie richtig sein:
# Das Ziel haengt an Kunde und Projekt, und das weiss nur der Generator.
ZIEL="${RECHNUNGEN_ICLOUD:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/Business/Deko}"
# Wohin flache Dateien gehen, die KEINEN Unterordner mitbringen. Ausdruecklich
# nicht unter einen Kundenordner — Adams Regel gilt auch im Fehlerfall.
AUFFANG="${RECHNUNGEN_AUFFANG:-_Aus-dem-Server}"
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

# **Erreichbarkeit ZUERST, und getrennt** — sonst tragen zwei sehr
# verschiedene Lagen dieselbe Meldung: *Server weg* ist ein Alarm, *Ordner
# fehlt noch* ist vor dem Umzug der Normalfall. Eine Sammelzeile
# („nicht erreichbar oder Ordner fehlt") liesse den echten Ausfall wie den
# Normalfall aussehen — genau die Fehlerklasse, gegen die dieses Skript
# gebaut ist.
#
# **Der Anlass ist gemessen und war peinlich genug, um ihn hinzuschreiben:**
# Am 02.09. stand hier der Hostname `claudebot@vps`, den dieser Rechner nicht
# aufloest. Haelfte 1 haette **jeden Lauf** mit der Sammelzeile quittiert, und
# niemand haette gemerkt, dass es nie am Server lag.
if ! command -v rsync >/dev/null 2>&1; then
  sag "Haelfte 1 UEBERSPRUNGEN: rsync fehlt auf diesem Rechner"
elif ! ssh -o BatchMode=yes -o ConnectTimeout=10 "$SSH_HOST" true 2>>"$LOG"; then
  sag "Haelfte 1 FEHLER: [$SSH_HOST] antwortet nicht — Name in ~/.ssh/config?"
  sag "        Das ist KEIN Normalfall. Ohne den Server kommen keine"
  sag "        Rechnungen an, auch wenn Haelfte 2 gleich sauber durchlaeuft."
elif ! ssh -o BatchMode=yes "$SSH_HOST" "test -d '$FERN'" 2>>"$LOG"; then
  sag "Haelfte 1 uebersprungen: Server da, Ausgangsordner fehlt noch ($FERN)"
  sag "        Normalfall, solange das Rechnungsprojekt nicht umgezogen ist."
elif rsync -az --timeout=20 -e "ssh -o BatchMode=yes -o ConnectTimeout=10" \
        "$SSH_HOST:$FERN" "$LOKAL/" 2>>"$LOG"; then
  sag "Haelfte 1: vom Server geholt ($SSH_HOST:$FERN)"
else
  sag "Haelfte 1 FEHLER: Ordner da, Uebertragung gescheitert — siehe oben"
fi

# ---------------------------------------------------------------- Haelfte 2
#
# Mac-Platte → iCloud. **Nur hier greift Adams TCC-Freigabe** — dieses Skript
# laeuft unter Claude.app, nicht unter `launchd`. Die beiden Vorbilder
# (`icloud_spiegel.sh`, `icloud_backup.sh`) LESEN aus iCloud; dieses schreibt
# hinein. **Die Freigabe gilt in beide Richtungen — beim ersten Lauf geprueft,
# nicht angenommen.**
# **Der Zielordner muss EXISTIEREN — er wird nicht angelegt.** Das ist Adams
# gewachsener Kundenzweig; wenn er fehlt, ist iCloud nicht eingehaengt, die
# Freigabe fehlt, oder die Ablage heisst anders. Ein `mkdir -p` legte dann
# stillschweigend eine zweite Wahrheit neben die echte.
if [ ! -d "$ZIEL" ]; then
  sag "FEHLER: iCloud-Zielordner fehlt — $ZIEL"
  sag "        Er wird ABSICHTLICH nicht angelegt: Das ist Adams gewachsener"
  sag "        Kundenzweig. Fehlt er, ist iCloud nicht da oder die Freigabe"
  sag "        fehlt. NICHT geraten — setze RECHNUNGEN_ICLOUD."
  exit 78
fi

_anzahl=$(find "$LOKAL" -type f ! -name '.*' 2>/dev/null | wc -l | tr -d ' ')
if [ "$_anzahl" -eq 0 ]; then
  sag "nichts abzulegen (Uebergabeordner leer) — Lauf war trotzdem da"
  exit 0
fi

# ---- (a) Alles MIT Unterordner: der relative Pfad wird DURCHGEREICHT
#
# **Nicht interpretiert, und das ist der Kern.** Gemessen am 02.09. schwankt
# Adams Ablagetiefe je Kunde: `Goldhut` haelt Rechnungen direkt, `DEKO-Service`
# eine Ebene tiefer, und `LiveSetup/Volvo/Business Modul/Norderney` sind
# **drei** Ebenen — Adams „Volvo Business Modul Norderney" ist kein
# Ordnername, sondern ein Pfad. **Ein festes Schema kann es also nicht
# geben.** Genau deshalb reicht dieses Skript den relativen Pfad durch:
# `ausgang/LiveSetup/Volvo/Business Modul/Norderney/x.pdf` landet unter
# `Business/Deko/LiveSetup/Volvo/Business Modul/Norderney/x.pdf`, bei jeder
# Tiefe, ohne dass hier jemand die Struktur kennen muss.
#
# **Kein `--delete`** — der Lauf legt nur ab, was er mitbringt, und ruehrt
# fremde Kundenordner nicht an. `-u`: Neueres ueberschreibt Aelteres; die
# Rechnungsnummer steht im Dateinamen, ein echter Doppelgaenger kann also nur
# dieselbe Rechnung sein.
_tief=0
if rsync -a -u --exclude='.*' --include='*/' --include='*/**' --exclude='*' \
        "$LOKAL/" "$ZIEL/" 2>>"$LOG"; then
  _tief=$(find "$LOKAL" -mindepth 2 -type f ! -name '.*' 2>/dev/null | wc -l | tr -d ' ')
  [ "$_tief" -gt 0 ] && sag "Haelfte 2: $_tief Datei(en) in ihre Kundenordner gelegt"
else
  sag "FEHLER: Ablage nach iCloud gescheitert — $ZIEL"
  exit 78
fi

# ---- (b) Flache Dateien in den Auffangordner, NICHT in einen Kundenordner
#
# Eine Datei ohne Unterordner weiss nicht, zu wem sie gehoert. Sie unter
# `DEKO-Service` zu legen waere genau das, was Adam ausschliesst — **also
# gehoert sie in einen neutralen Auffang, und dort faellt sie auf.**
_flach=$(find "$LOKAL" -maxdepth 1 -type f ! -name '.*' 2>/dev/null | wc -l | tr -d ' ')
if [ "$_flach" -gt 0 ]; then
  if rsync -a -u --exclude='.*' --exclude='*/' "$LOKAL/" "$ZIEL/$AUFFANG/" 2>>"$LOG"; then
    sag "Haelfte 2: $_flach Datei(en) OHNE Kundenordner → $AUFFANG (bitte ansehen)"
  else
    sag "FEHLER: Auffang-Ablage gescheitert — $ZIEL/$AUFFANG"
    exit 78
  fi
fi
