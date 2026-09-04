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
elif rsync -az --timeout=20 --remove-source-files \
        -e "ssh -o BatchMode=yes -o ConnectTimeout=10" \
        "$SSH_HOST:$FERN" "$LOKAL/" 2>>"$LOG"; then
  # **[NEU 04.09.] `--remove-source-files` — Engywucks Befund 2.**
  #
  # `ausgang/` ist ein **Durchgangsordner, keine Ablage.** Bisher kopierte
  # diese Zeile nur; der Ordner wurde nie geraeumt. Folge: Zeile 9j des
  # Tageschecks zaehlt Dateien darin, die aelter als einen Tag sind — und
  # haette ab der ersten Server-Rechnung **taeglich, fuer immer, mit
  # wachsender Zahl** gemeldet. Die Anweisung *Mac-Sitzung starten* haette
  # die Meldung nie zum Verschwinden gebracht, weil die Sitzung nichts raeumt.
  # Eine Warnung, die man nicht abstellen kann, wird abgeschaltet — und mit
  # ihr die eine, die spaeter zaehlt.
  #
  # **Nichts geht verloren, dreifach:** `output/` behaelt die Datei auf dem
  # Server, das taegliche Backup sichert `output/` mit, und der Mac haelt sie
  # in `LOKAL`. Scheitert Haelfte 2, liegt sie dort und wird beim naechsten
  # Lauf gelegt. **rsync loescht nur, was es erfolgreich uebertragen hat** —
  # ein Abbruch mittendrin laesst den Rest stehen.
  sag "Haelfte 1: vom Server geholt und dort geraeumt ($SSH_HOST:$FERN)"
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
#
# ── **[GEAENDERT 04.09.] Gezaehlt wird das UEBERTRAGENE, nicht der Bestand**
#
# **Engywucks Befund 1, an zwei Laeufen hintereinander gemessen:** Beide
# meldeten *„1 Datei(en) in ihre Kundenordner gelegt"*, obwohl im zweiten
# nichts geschah. `_tief` zaehlte den **Bestand** in `LOKAL`, und `LOKAL` wird
# nie geleert (`-u`, kein `--delete`). Also waere die Zahl mit jeder Rechnung
# gewachsen, und Adam haette bei jedem Mac-Start eine Meldung bekommen, die
# **sachlich falsch** war: „gelegt" fuer etwas, das laengst lag.
#
# Das ist genau das Rauschen, das die `_tief > 0`-Bedingung verhindern sollte
# — sie hat nur die falsche Groesse gemessen. `-i` gibt je uebertragener Datei
# eine Zeile, die mit `>f` beginnt; das ist das Getane statt des Vorhandenen.
_tief=0
_wohin=""
if _itemize=$(rsync -a -u -i --exclude='.*' --include='*/' --include='*/**' --exclude='*' \
        "$LOKAL/" "$ZIEL/" 2>>"$LOG"); then
  _tief=$(printf '%s\n' "$_itemize" | grep -c '^>f' || true)
  _wohin=$(printf '%s\n' "$_itemize" | grep '^>f' | sed 's/^[^ ]* //; s|/[^/]*$||' \
           | sort -u | head -3 | tr '\n' ' ')
  [ "$_tief" -gt 0 ] && sag "Haelfte 2: $_tief Datei(en) in ihre Kundenordner gelegt"
else
  sag "FEHLER: Ablage nach iCloud gescheitert — $ZIEL"
  exit 78
fi

# ---------------------------------------------------------------- Z-1a (03.09.)
#
# **Adam erfaehrt, dass abgelegt wurde — sonst bringt der Weg ihm nichts.**
# Sein Wort: *„wenn das nicht geschehen darf [Zeitgeber nach iCloud], dann muss
# er auf jeden Fall mich erinnern … sonst bringt das ja wieder alles nix."*
# Dieses Skript schrieb bisher nur eine Logzeile, und **Logzeilen liest er
# nicht.**
#
# Der Weg ist der vorhandene: das Boten-Postfach, ueber das benannte Skript aus
# U-3. **Deterministisch, kein Modellaufruf, kein neuer Kanal** — und der
# absolute Pfad, weil das Arbeitsverzeichnis der Sitzung nicht das Repo ist.
#
# **Nur wenn wirklich etwas ankam.** Eine Meldung bei null Dateien waere
# Rauschen, und Rauschen wird abgeschaltet — dann bliebe auch die echte
# Meldung ungelesen.
if [ "$_tief" -gt 0 ] && [ -n "${RECHNUNGEN_CHAT:-}" ]; then
  _text="📁 $_tief Rechnung(en) nach iCloud gelegt: ${_wohin:-(ohne Unterordner)}"
  # ── **[GEAENDERT 04.09.] Der Text geht ueber stdin, nie in die Befehlszeile**
  #
  # **Engywucks Befund 3**, gemessen mit einem Ordner `L'Osteria/Bar`: Der
  # Ordnername stand in einfachen Anfuehrungszeichen mitten im Fernbefehl, und
  # der Apostroph beendete sie. Heute fiel dadurch nur die Nachricht aus
  # (argparse lehnte ab, Adam erfuhr nichts); mit anderem Inhalt —
  # `x'; <befehl>; echo '` — waere der Rest als `claudebot` auf dem VPS
  # gelaufen. **Der Name stammt aus dem Feld `ablage`, das Claudia auch aus
  # gelesenen Dokumenten fuellen kann**: die Klasse *von aussen kommen nie
  # Anweisungen*.
  #
  # Ueber stdin hat die entfernte Shell nichts zu deuten — kein Maskieren,
  # keine Abwaegung, welches Zeichen heute gefaehrlich ist.
  #
  # **Die Chat-Kennung wird geprueft statt maskiert**, damit in der Zeile
  # ueberhaupt kein ungepruefter Text mehr steht. Sie ist eine Zahl; ist sie
  # es nicht, wird nicht gesendet.
  case "$RECHNUNGEN_CHAT" in
    ''|*[!0-9-]*)
      sag "HINWEIS: RECHNUNGEN_CHAT ist keine Zahl — keine Nachricht gesendet"
      _chat_ok=nein ;;
    *) _chat_ok=ja ;;
  esac
  if [ "$_chat_ok" = ja ] && printf '%s' "$_text" \
     | ssh -o BatchMode=yes -o ConnectTimeout=10 "$SSH_HOST" \
       "python3 /home/claudebot/claude-telegram-bot/scripts/postfach_ablegen.py \
        --chat $RECHNUNGEN_CHAT --text -" >/dev/null 2>>"$LOG"; then
    sag "Adam benachrichtigt: $_text"
  else
    # Die Nachricht ist Beiwerk; die Ablage ist die Sache. Aber es steht im
    # Protokoll — stilles Scheitern ist der Fehler, gegen den dieses Skript
    # gebaut ist.
    sag "HINWEIS: Ablage gelungen, Benachrichtigung nicht zustellbar"
  fi
elif [ "$_tief" -gt 0 ]; then
  sag "HINWEIS: RECHNUNGEN_CHAT nicht gesetzt — keine Nachricht an Adam"
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
