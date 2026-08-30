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
export WEBSUCHE_VERLAUF="$PRUEFHEIM/websuche-verlauf.json"
export FREIGABE_DIR="$PRUEFHEIM/freigaben"
export HORA_DIR="$PRUEFHEIM/hora"
export BLUMEN_DIR="$PRUEFHEIM/blumen"
export BASHFREI_HEIM="$PRUEFHEIM"
export BASHFREI_PROTOKOLL="$PRUEFHEIM/bash-freigaben.jsonl"
export GEGENLESER_DIR="$PRUEFHEIM/gegenleser"
# `[NEU 2026-08-20]` Das Auftragsbuch fehlte hier — und der Riegel hat prompt
# ein Loch gehabt, das sich am selben Tag zeigte: Der Zielumgebungs-Pruefer
# startet den ECHTEN Tagescheck, und der legt seit A6.1 einen Sichtungs-Vermerk
# ins Auftragsbuch. Am 20.08. um 13:58 stand dieser Eintrag im echten Buch,
# erzeugt von einem Pruflauf. Dieselbe Klasse wie der 26.07. um 01:44, als eine
# Testmeldung als echte Nachricht bei Adam ankam.
#
# **Die Lehre ist nicht „diesen Pfad nachtragen", sondern: Wer eine neue
# Zustandsablage einfuehrt, traegt sie im selben Zug in die Wegwerf-Umgebung
# ein.** Sonst waechst die Liste der Riegel langsamer als die Liste der Orte,
# an denen ein Test schreiben kann.
export AUFTRAGSBUCH_DIR="$PRUEFHEIM/auftragsbuch"
export PENDING_DIR="$PRUEFHEIM/pending"
# `[NEU 30.08.]` Der Zustandspruefer der Ausarbeitungen — **vom
# Differenzmesser gemeldet, bevor ich es bemerkt habe.** Ohne diese beiden
# Riegel schriebe ein Pruflauf seinen Merker in die ECHTE Ablage und laese den
# echten Papierordner; die naechste Meldung im Betrieb waere dann still um die
# Zugaenge aermer, die der Testlauf schon „gesehen" hat.
export AUSARBEITUNGEN_DIR="$PRUEFHEIM/ausarbeitungen"
export AUSARBEITUNGEN_STAND="$PRUEFHEIM/ausarbeitungen-stand.json"
# `[NEU 2026-08-23]` Und die Liste war weiter unvollstaendig — genau so, wie es
# der Absatz darueber vorhergesagt hat. Engywucks Befund L: `USER_PREFS_FILE`
# fehlte hier, zwoelf Testdateien setzten es einzeln, und `bot.py` LAS es gar
# nicht. Jeder Lauf beschrieb die echte `prefs.json`; auf dem VPS standen
# danach alle drei Kanal-Kennungen auf der Test-Attrappe. Ein Bruch, der wie
# Ruhe aussieht, weil ein unbekannter Kanal nichts wirft, das auffaellt.
#
# Die uebrigen vier hatten dasselbe Loch, nur ohne Vorfall. Ab jetzt meldet
# `scripts/test_hermetik.py` jede Ablage, die hier fehlt — die Liste soll nicht
# wieder langsamer wachsen als die Orte, an denen ein Test schreiben kann.
export USER_PREFS_FILE="$PRUEFHEIM/prefs.json"
export LINK_INBOX_DIR="$PRUEFHEIM/links"
export QUESTIONS_FILE="$PRUEFHEIM/open_questions.json"
export LIMIT_MARKE_FILE="$PRUEFHEIM/limit.marke"
export LIMIT_STAND_FILE="$PRUEFHEIM/limit.stand"
# Vom Hermetik-Pruefer beim ERSTEN Lauf gefunden — beide schreiben in Ablagen,
# die ein Mensch spaeter liest: Gespraechsprotokolle und hochgeladene Dateien.
export CONVERSATION_LOG_DIR="$PRUEFHEIM/claude-logs"
export UPLOAD_DIR="$PRUEFHEIM/uploads"
# `[NEU 2026-08-23]` Und WIEDER war die Liste unvollstaendig — diesmal gefunden
# durch scripts/differenz.py, das die Ist-Menge nicht mehr ueber die ENDUNG
# bildet. Meine eigene Fassung vom selben Tag suchte `_DIR` und `_FILE` und
# verfehlte damit ausgerechnet die AMPEL, die laut CLAUDE.md das Heikelste im
# Projekt fuehrt (Klienten-Namen, ausdruecklich cloud-frei zu pflegen). Ein
# Pruflauf haette ihre Regeldatei ueberschreiben koennen, lautlos.
export AMPEL_RULES_PATH="$PRUEFHEIM/ampel-regeln.json"
export AMPEL_CUSTOM_PATH="$PRUEFHEIM/ampel-eigene.json"
export AMPEL_STATE_PATH="$PRUEFHEIM/ampel-stand.json"
export AMPEL_LOG_PATH="$PRUEFHEIM/ampel.log"
export AUTH_MARKE="$PRUEFHEIM/auth-marke.json"
export ZUSTELL_MARKE="$PRUEFHEIM/zustell-marke.json"
export ERINNERUNG_DIR="$PRUEFHEIM/erinnerungen"
export HORA_LISTE="$PRUEFHEIM/hora-liste.json"
export KONTINGENT_HOME="$PRUEFHEIM/kontingent-heim"
export LOG_SYNC_REPO="$PRUEFHEIM/log-repo"
export PRESEND_LOG_PATH="$PRUEFHEIM/presend.log"
export TAGESCHECK_LOG="$PRUEFHEIM/tagescheck.log"
export UPDATER_STATE_DIR="$PRUEFHEIM/updater"
export VERSION_MONITOR_LOG="$PRUEFHEIM/version-monitor.log"
export VERSION_MONITOR_SEEN="$PRUEFHEIM/version-gesehen.json"
export WACHPOSTEN_DIR="$PRUEFHEIM/wachposten"
export WACHPOSTEN_LOGDIR="$PRUEFHEIM/wachposten-logs"
mkdir -p "$POSTFACH_DIR/outbox" "$FREIGABE_DIR" "$HORA_DIR" "$BLUMEN_DIR" \
         "$AUFTRAGSBUCH_DIR" "$PENDING_DIR" "$LINK_INBOX_DIR" \
         "$CONVERSATION_LOG_DIR" "$UPLOAD_DIR" \
         "$ERINNERUNG_DIR" "$KONTINGENT_HOME" "$LOG_SYNC_REPO" \
         "$UPDATER_STATE_DIR" "$WACHPOSTEN_DIR" "$WACHPOSTEN_LOGDIR" \
         "$AUSARBEITUNGEN_DIR"
# **[VERTEIDIGT 30.08.] Der EINZIGE EXIT-Trap dieses Skripts.**
#
# `457ba5f` hat hier einen zweiten hinzugefuegt (fuer die Protokolldatei) —
# und **Bash-EXIT-Traps sind nicht additiv: der zweite ERSETZT den ersten.**
# Gemessen: `trap "echo ERSTE" EXIT; trap "echo ZWEITE" EXIT` druckt nur
# ZWEITE. Folge: Das Wegwerf-Heim blieb bei jedem Lauf liegen; am Mac lagen
# vierzehn davon, auf dem VPS waechst die Zahl taeglich (Tagescheck) plus je
# Hora-Auftrag plus je Update — jedes mit Postfach, Auftragsbuch, prefs.json.
#
# Statt zwei Traps zu verketten liegt die Protokolldatei jetzt IM Wegwerf-Heim
# (siehe LOGDATEI weiter unten). Damit gibt es nichts mehr zu verketten — die
# Fehlerquelle ist beseitigt, nicht ausgeglichen. **Wer hier einen zweiten
# `trap ... EXIT` hinzufuegt, schaltet diese Zeile ab; die Pruefzeile
# „genau ein EXIT-Trap" in `test_pruefumgebung.py` meldet das.**
trap 'rm -rf "$PRUEFHEIM"' EXIT

# Stand des ECHTEN Postfachs VOR dem Lauf — der Nachweis am Ende vergleicht.
ECHTPOST="${HOME:-/home/claudebot}/postfach/outbox"
POST_VORHER="$(ls -A "$ECHTPOST" 2>/dev/null | wc -l | tr -d ' ')"
# Zweiter Nachweis, aus dem Vorfall vom 20.08.: Auch das echte Auftragsbuch
# darf durch einen Pruflauf nicht wachsen.
ECHTBUCH="${HOME:-/home/claudebot}/.claude/auftragsbuch/eingang"
BUCH_VORHER="$(ls -A "$ECHTBUCH" 2>/dev/null | wc -l | tr -d ' ')"

FAILS=0
# GESAMT wird GEZAEHLT, nicht getippt. Vorher stand die Zahl fest im
# Schlusssatz — beim Aufnehmen der 9.5-Pruefung meldete der Lauf "29/29",
# obwohl 30 Pruefungen gruen waren, und bei einem Fehlschlag haette er
# ebenso falsch gerechnet. Eine Kennzahl, die von Hand nachgepflegt werden
# muss, wird irgendwann nicht nachgepflegt.
GESAMT=0
# **[NEU 30.08.] Die dritte Kategorie: uebersprungen.**
#
# Der Faecher-Befund fand sechs Pruefer, die gruen meldeten, ohne gemessen zu
# haben. Der Laeufer war die Haelfte des Problems: Er kannte genau zwei
# Ausgaenge, also musste jeder Uebersprung als BESTANDEN durchgehen. So stand
# "✅ Medien-Transport H1" ueber einem Lauf, in dem zwoelf Pruefzeilen nie
# ausgefuehrt wurden — und "60/63" zaehlte ihn mit.
#
# Ein Pruefer sagt "uebersprungen" mit **Rueckgabewert 77** (die uebliche
# Kennzahl dafuer). Uebersprungenes zaehlt NICHT als bestanden, faellt aber
# auch nicht durch: Es steht als eigene Zahl da. Genau daran entsteht die
# Zahlendifferenz zwischen Mac und Zielumgebung, die bisher fehlte — auf einer
# Maschine ohne das noetige Werkzeug ist die Bilanz sichtbar unvollstaendig,
# statt gruen zu luegen.
UEBERSPRUNGEN=0
# **Der Log-Pfad haengt am Nutzer, nicht an /tmp** (Fund [70]): Ein fester
# Pfad gehoert dem ersten Nutzer, der ihn anlegt. Beim zweiten scheitert die
# Umlenkung — und bash fuehrt sie VOR dem Befehl aus, der Pruefling laeuft
# also gar nicht erst. Ergebnis waere "0/N bestanden" mit lauter Fehlschlaegen,
# die keiner ist. Gemessen und nachgestellt im Befund.
# **Im Wegwerf-Heim, nicht daneben** — damit der EINE Trap oben auch sie
# raeumt und kein zweiter noetig ist, der den ersten verdraengen wuerde.
LOGDATEI="$PRUEFHEIM/regress_last.log"
run() {
  local name="$1"; shift
  local rc=0
  GESAMT=$((GESAMT+1))
  "$@" >"$LOGDATEI" 2>&1 || rc=$?
  # **[NEU 30.08.] Ein stiller Erfolg ist auch ein Uebersprung.**
  #
  # Der 77er-Weg oben verlangt, dass ein Pruefer seinen Uebersprung SELBST
  # bemerkt und meldet. Genau das taten die sechs Faelle des Faecher-Befunds
  # nicht — sie endeten mit 0 und schwiegen. Diese Zeile faengt die Klasse
  # unabhaengig davon: **Wer nichts gemeldet hat, hat nichts gemessen.**
  #
  # **Und sie gilt nur fuer UNSERE Pruefskripte** — das ist keine Einschraenkung
  # aus Vorsicht, sondern aus einer Messung: Alle 54 Skript-Pruefer drucken
  # Haekchen; die zehn `py_compile`-Laeufe im selben Durchgang tun es nicht und
  # messen trotzdem (Schweigen ist dort die Konvention). Mein erster Anlauf
  # ohne diese Unterscheidung meldete prompt zehn falsche Uebersprünge —
  # **ich hatte die Menge gemessen, die mir am Bautag einfiel, nicht die
  # tatsaechliche.** Eine Schranke mit zehn Fehlalarmen je Lauf wird binnen
  # einer Woche abgeschaltet und nimmt die echten Funde mit.
  local _eigener=0
  for _arg in "$@"; do
    case "$_arg" in scripts/*.py|scripts/*.sh) _eigener=1 ;; esac
  done
  if [ "$_eigener" -eq 1 ] && [ "$rc" -eq 0 ] && ! grep -qE '✓|✅' "$LOGDATEI"; then
    rc=77
    echo "   (kein einziges Haekchen in der Ausgabe — als Uebersprung gewertet)" >>"$LOGDATEI"
  fi
  if [ "$rc" -eq 0 ]; then
    echo "✅ $name"
  elif [ "$rc" -eq 77 ]; then
    echo "⏭️  $name — UEBERSPRUNGEN, nichts gemessen:"
    tail -3 "$LOGDATEI"
    UEBERSPRUNGEN=$((UEBERSPRUNGEN+1))
  else
    echo "❌ $name — Log:"
    tail -20 "$LOGDATEI"
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
run "Erinnerungs-Laeufer 7.2 (ruhend)"  "$PY" scripts/test_erinnerungen_7_2.py
run "Kontingent-Stand (A2)"            "$PY" scripts/test_kontingent_a2.py
run "Kanal-Links 6.2/6.4"              "$PY" scripts/test_kanal_links_6_2.py
run "Pin-Bezug 5.13"                   "$PY" scripts/test_pin_bezug_5_13.py
run "Eingangsschranken (1)(2)"        "$PY" scripts/test_eingangsschranken.py
run "Mail-Angriffskorpus (Stufe B)"    "$PY" scripts/test_mailkorpus.py
run "Websuche meldet ihren Ausfall"   "$PY" scripts/test_websuche_ausfall.py
run "Websuche-Waechter (Daempfung)"   "$PY" scripts/test_websuche_check.py
run "Freigabedialog sagt es"          "$PY" scripts/test_freigabedialog.py
run "Bash-Positivliste"               "$PY" scripts/test_bashfreigabe.py
run "Umlaut-Ersatz am Versand"        "$PY" scripts/test_umlaut_versand.py
run "SDK-Fehlererkennung"            "$PY" scripts/test_fehlererkennung_sdk.py
run "Gegenleser (ruhend)"            "$PY" scripts/test_gegenleser.py
run "Governance-Hook (8.7)"          "$PY" scripts/test_governance_hook.py
run "Anhang-Erkennung (Rang 2)"      "$PY" scripts/test_bodystructure_rang2.py
run "UID-Kennung (Rang 2)"          "$PY" scripts/test_uid_kennung_rang2.py
run "Rangvermerk zuerst (Rang 2)"   "$PY" scripts/test_rangvermerk_rang2.py
run "Keine Verknuepfung (Rang 2)"   "$PY" scripts/test_verknuepfung_rang2.py
run "Hermetik der Pruefläufe (L)"       "$PY" scripts/test_hermetik.py
run "Zielumgebung (bash -n + env -i)"  bash scripts/test_zielumgebung.sh
run "Sendepfad-Rauchtest (Pflicht 1)"  "$PY" scripts/test_sendepfad_rauch.py
run "Gruendlich-Umschalter (B3)"        "$PY" scripts/test_gruendlich_b3.py
run "Limit-Vorwarnung 5.20 (B4)"        "$PY" scripts/test_limitwarnung_b4.py
run "Vorlese-Regeln (B5)"               "$PY" scripts/test_vorlese_b5.py
run "Blinde-Flecken-Verfahren (B6)"     "$PY" scripts/test_blinde_flecken_b6.py
run "Auftragsbuch B8 (ruhend)"          "$PY" scripts/test_auftragsbuch_b8.py
run "Doku-Spiegel (/hilfe/Buttons)"     "$PY" scripts/check_hilfe_buttons.py
run "Uebersprungen ≠ bestanden (A1)"    "$PY" scripts/test_uebersprungen_a1.py
run "Zustand der Ausarbeitungen"        "$PY" scripts/test_ausarbeitungen.py

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

GESAMT=$((GESAMT+1))
BUCH_NACHHER="$(ls -A "$ECHTBUCH" 2>/dev/null | wc -l | tr -d ' ')"
if [ "$BUCH_NACHHER" -gt "$BUCH_VORHER" ]; then
  echo "❌ Eine Pruefung hat ins ECHTE Auftragsbuch geschrieben ($((BUCH_NACHHER-BUCH_VORHER)) neu)."
  echo "   Belegt am 20.08.: Der Zielumgebungs-Pruefer startet den echten"
  echo "   Tagescheck, und der legt seit A6.1 einen Sichtungs-Vermerk."
  FAILS=$((FAILS+1))
else
  echo "✅ Wegwerf-Umgebung: keine Pruefung hat ins echte Auftragsbuch geschrieben"
fi

# **Uebersprungenes zaehlt nicht als bestanden** (30.08.). Die Bestanden-Zahl
# ist jetzt "gemessen und gruen", nicht "nicht rot".
echo "== Ergebnis: $((GESAMT-FAILS-UEBERSPRUNGEN))/$GESAMT bestanden =="
if [ "$UEBERSPRUNGEN" -gt 0 ]; then
  echo "== $UEBERSPRUNGEN uebersprungen — auf DIESER Maschine wurde dort nichts gemessen =="
fi

# **[NEU 30.08., Engywucks Widerlegung Rang 1] Uebersprungenes gehoert ins
# SIGNAL, nicht nur in die Zahl.**
#
# Die erste Fassung liess es bei `exit $FAILS`. Damit war die Zahl ehrlich und
# das Signal nicht: Ein Lauf mit 65 Uebersprüngen endete mit **0**, und alle
# vier Verbraucher gingen auf gruen — der Tagescheck mit gruenem Haken, der
# Updater liess Updates durch, der Vollzugspruefer meldete "alles wie
# erwartet". **Der schwerste ist `hora.py`:** Es oeffnet auf rc=0 BEIDE Tore —
# das Vorher-Tor „auf rotem Fundament wird nicht gearbeitet" und das
# Nachher-Tor, das den Auftrag als erledigt abhakt. Ein Laeufer, der autonom
# Befehle ausfuehrt, haette auf einem Fundament gearbeitet, das niemand
# vermessen hat.
#
# Drei Zustaende, drei Rueckgabewerte: **0 = alles gemessen und gruen ·
# 77 = gruen, aber nicht alles gemessen · sonst = Fehlschlaege.** Wer nur
# „ungleich null" prueft, faehrt automatisch die sichere Richtung.
if [ "$FAILS" -eq 0 ] && [ "$UEBERSPRUNGEN" -gt 0 ]; then
  exit 77
fi
exit $FAILS
