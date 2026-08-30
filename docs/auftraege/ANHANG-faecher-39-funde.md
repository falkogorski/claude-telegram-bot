<!-- ROLLE: befund-faecher-vollstaendig -->
# Anhang: alle 39 bestätigten Funde im Wortlaut

**Stichtag:** 30.08.2026 · **Stand:** `df5dc69` · **Von:** Engywuck
Jeder Fund einzeln beurteilt UND adversarisch gegengeprüft. Nur die zwei
kosmetischen liefen ohne Widerleger (per Bauart übersprungen).

## [6] scripts/daily_check.sh — LAUT
**Maschine:** beide

Die Zeile steht unveraendert (heute Zeile 128, nie angefasst seit 025ef8b). Aber der gemeldete Bruch ist der falsche: (a) Auf dem Mac hat die rote Falschaussage KEINE Wirkung — daily_check.sh wird dort ausschliesslich von test_zielumgebung.sh gestartet, mit TROCKENLAUF=1 (merken() schreibt nichts) und leerem ALLOWED_USER_IDS (die Sendeschleife ueberspringt jeden Empfaenger); ausserdem sind auf dem Mac die vier Zeilen darueber (systemctl) ohnehin rot. Es gibt keinen Mac-Zeitgeber fuer diesen Check. (b) Dafuer existiert an derselben Zeile ein ECHTER, bisher unbenannter Defekt auf GNU/Linux, also auf dem VPS: `pgrep -c` gibt bei null Treffern `0` aus UND beendet sich mit Code 1 — deshalb feuert `|| echo 0` ZUSAETZLICH, und n wird zu "0\n0". Die Alarmzeile zerfaellt genau im Stoerfall (Bot tot) in zwei Zeilen: `Bot-Instanzen: 0` / `0 (soll 1)`, und dieser zerrissene Text geht so auch in Adams Telegram-Meldung. Laut, nicht still — aber verstuemmelt.

**Beleg:**
```
Befehl (Skript ueber base64 erzeugt, damit die Suchzeichenkette nicht in der Harness-Befehlszeile steht und pgrep -f sich nicht selbst zaehlt):
$ cat g7-daily/z3.sh
#!/usr/bin/env bash
set -uo pipefail
n="$(pgrep -c -f 'python bot.py' 2>/dev/null || echo 0)"
printf 'n=<%s>\n' "$n"
if [ "$n" = "1" ]; then echo "GRUEN"; else echo "ROT: Bot-Instanzen: $n (soll 1)"; fi
$ env -i "PATH=/usr/bin:/bin" /bin/bash g7-daily/z3.sh
n=<0
0>
ROT: Bot-Instanzen: 0
0 (soll 1)
$ env -i "PATH=$M/bsdbin:/usr/bin:/bin" /bin/bash g7-daily/z3.sh    # BSD-Attrappe: "illegal option -- c", exit 2
n=<0>
ROT: Bot-Instanzen: 0 (soll 1)
VollLauf des echten Skripts (Linux, kein Bot) -> Protokollzeilen 6-7:
  ❌ Bot-Instanzen: 0
  0 (soll 1)
Wirkungslosigkeit auf dem Mac belegt in scripts/test_zielumgebung.sh:77-89: `env -i TROCKENLAUF=1 ... ALLOWED_USER_IDS= /bin/bash "$f"` und danach nur `if echo "$ausgabe" | grep -q 'unbound variable'`.
git log -S'pgrep -c -f' --oneline -- scripts/daily_check.sh -> 025ef8b (Ersteinbau, keine Reparatur)
```

**Widerleger (hält):** Widerlegungsversuch gescheitert — alle vier Angriffswege, die den Fund haetten kippen koennen, sind selbst gemessen und bestaetigen ihn.

(1) LAENGST REPARIERT? Nein. Zeile 128 ist in der Arbeitskopie, in df5dc69 UND im heutigen Repo-HEAD 76d3513 (29.08.) zeichengleich. `git log -L 128,129:scripts/daily_check.sh` nennt genau einen Commit: 025ef8b (Ersteinbau). Kein Reparatur-Commit dazwischen. Die Vorsitzung hat nicht an der falschen Stelle gesucht.

(2) IST DER ZWEIG ERREICHBAR? Ja. `set -uo pipefail`, kein `set -e`; Abschnitt 1 (systemctl) und Abschnitt 2 sind unabhaengig. `red()` reicht `$1` ROH in `problems` weiter — nirgends `tr`, `xargs` oder eine andere Normalisierung. Der Sendeblock am Dateiende ist erreichbar, weil TELEGRAM_BOT_TOKEN/ALLOWED_USER_IDS erst in Abschnitt 5 (`set -a; . "$ENVFILE"`) gesetzt werden, also NACH Zeile 128 und VOR dem Report; `curl --data-urlencode "text=${report}"` kodiert den Umbruch als %0A und Telegram rendert ihn.

(3) TRIFFT DAS SUCHMUSTER UEBERHAUPT? Ja — und genau das schliesst die bequemste Ausrede aus. ExecStart ist `/home/claudebot/claude-telegram-bot/.venv/bin/python bot.py` (MIGRATION.md:1440; run.sh: `exec .venv/bin/python bot.py`) — e

---

## [70] scripts/regressionstest.sh — LAUT
**Maschine:** beide (nur bei zwei Nutzern im selben /tmp)

Der Mechanismus ist real und nachgestellt: Bash führt die Umlenkung VOR dem Befehl aus, der Prüfer läuft gar nicht, jede Zeile zählt als Fehlschlag — mein Attrappen-Befehl /bin/echo hat nie gedruckt, das Ergebnis war '0/1 bestanden'. Der feste Pfad /tmp/regress_last.log steht heute unverändert in run() (Zeile 125). ZWEI EINSCHRÄNKUNGEN gegen die Meldung: (1) Der Bruch ist LAUT, nicht still — alles rot plus 'Permission denied' auf stderr; die Meldung wiegt ihn schwerer, als er wiegt. (2) Die behauptete VPS-Abwechslung root/claudebot ist im heutigen Code NICHT belegt: daily_check.sh:132 ruft den Läufer ausdrücklich als `sudo -u claudebot`, und die dokumentierten Aufrufe laufen alle ohne root (docs/node-major-befehlsblock.md:37 'Vor dem Fenster (ohne root)', Zeile 75 wieder sudo -u claudebot; der Probelauf im ZETTEL ausdrücklich 'ohne root'). Es bleibt die latente Falle: ein einziger manueller root-Lauf legt die Datei mit umask 022 root-eigen an und tötet danach jeden claudebot-Lauf dauerhaft.

**Beleg:**
```
$ touch /tmp/rl_test.log; chmod 600 /tmp/rl_test.log; chown root:root /tmp/rl_test.log; su -s /bin/bash nobody -c 'true >/tmp/rl_test.log'
->  bash: line 1: /tmp/rl_test.log: Permission denied   EXIT=1
$ cat /tmp/simrun.sh  (run() woertlich nachgebaut, Pruefling /bin/echo "ich-wurde-ausgefuehrt")
$ su -s /bin/bash nobody -c 'bash /tmp/simrun.sh'
->  /tmp/simrun.sh: line 6: /tmp/rl_test.log: Permission denied
->  FAIL Syntax bot.py — Log:
->  tail: cannot open '/tmp/rl_test.log' for reading: Permission denied
->  Ergebnis: 0/1 bestanden
(die Ausgabe 'ich-wurde-ausgefuehrt' fehlt: der Pruefling lief nie)
$ grep -n 'sudo -u claudebot' scripts/daily_check.sh
->  132:if reg="$(sudo -u claudebot bash "$BOTDIR/scripts/regressionstest.sh" 2>&1)"; then
$ umask -> 0022
```

**Widerleger (hält):** Ich habe alle vier Entkraeftungswege gefahren und keiner traegt. (1) NICHT REPARIERT: Der Festpfad steht unveraendert in run(), Zeile 125/129 — sowohl in der Arbeitskopie (md5-identisch mit df5dc69) als auch im heutigen HEAD 76d3513. `git log -S"regress_last" -- scripts/regressionstest.sh` liefert genau EINEN Commit (025ef8b, die Einfuehrung); danach hat die Stelle niemand angefasst. (2) ZWEIG ERREICHBAR: run() ist einmal definiert und traegt 61 Pruefaufrufe; es gibt keinen zweiten Log-Pfad, keine Env-Variable, keinen Wrapper — nichts faengt den Zweig vorher ab. (3) MECHANISMUS BESTAETIGT UND SCHAERFER ALS GEMELDET: Ich habe die Nachstellung ohne `chmod 600` gefahren — eine root-eigene Datei mit den gewoehnlichen umask-022-Rechten 644 genuegt bereits; als `nobody` bricht die Umlenkung mit "Permission denied" ab, die Attrappe /bin/echo druckt nie, Ergebnis "0/1". Die Falle springt also schon beim ganz normalen root-Lauf. (4) KEIN PRUEFER DECKT ES: differenz.py::festpfade_differenz bildet seine Ist-Menge in `_produktivmodule()` ausschliesslich ueber *.py-Dateien — ein Shell-Skript liegt ausserhalb des Suchrasters; ablagen_differenz misst export-Zeilen, nicht Festpfade. Diese Zeile wu

---

## [58] scripts/test_media_h1.py — LAUT
**Maschine:** beide (Code identisch); Auswirkung nur auf Maschinen ohne ffmpeg/ffprobe — im Kontroll-Container gemessen, Mac und VPS von hier nicht pruefbar

Der Tatbestand steht: `python3 scripts/test_media_h1.py` endet im Kontroll-Container mit EXITCODE=0 und der Laeufer schreibt `✅ Medien-Transport H1 (Bild/Video)`, obwohl alle zwoelf Pruefzeilen (Transportgrenze, Verkleinerung mit unangetastetem Original, Videozerlegung, Tonspur, Abtastdichte, Uebersichtsboegen, Ausschnitt) ungeprueft bleiben. Was an der Meldung NICHT traegt, ist ihre Einordnung als stiller Bruch: Die Meldung nennt die Selbstcheck-Zeile selbst nur als Vergleichsfall, sie ist aber Teil DESSELBEN Regressionslaufs (regressionstest.sh, Zeile `Selbstcheck-Invarianten (run_self_check)`) und faellt auf exakt denselben Praedikat-Aufruf `media.tools_available()`. Gemessen: der Lauf endet `== Ergebnis: 60/63 bestanden ==` und druckt die Ursache woertlich — `✗ Medien-Transport (H1): ffmpeg/ffprobe fehlen — große Bilder und alle Videos blieben liegen`. Die Annahme der Meldung (`ffmpeg liegt auf jeder Maschine im PATH`) ist damit im Container widerlegt, aber die Verletzung dieser Annahme wird sofort und benannt gemeldet — sie kostet eine Stunde, nicht Wochen. Gegenprobe gefahren, damit kein Zwischenzustand uebrig bleibt: mit Attrappen-Binaries (`exit 0`) im PATH wird `tools_available()` wahr, die Selbstcheck-Zeile also gruen — dann laeuft der H1-Test aber wirklich und stirbt laut mit `AssertionError: Testbild konnte nicht erzeugt werden`, EXITCODE=1. Es gibt somit keinen Zustand, in dem die Medienkette unbemerkt ungeprueft durchgeht. Der zu reparierende Rest ist derselbe wie bei Meldung 45 und ist Buchfuehrung, nicht Blindheit: der Skip sollte statt `sys.exit(0)` einen eigenen, sichtbaren Nicht-Bestanden-Zustand liefern (oder der Laeufer eine dritte Kategorie `uebersprungen` fuehren), damit `60/63` nicht eine Zeile mitzaehlt, die nichts gemessen hat.

**Beleg:**
```
$ cd <stand-aktuell-ro> && python3 -c "import sys;sys.path.insert(0,'.');import media;print('tools_available:',media.tools_available())"
tools_available: False

$ python3 scripts/test_media_h1.py; echo EXITCODE=$?
⚠ ffmpeg/ffprobe fehlen — H1-Test übersprungen (kein Fehlschlag)
EXITCODE=0

$ env TELEGRAM_BOT_TOKEN=000000:selfcheck-dummy ALLOWED_USER_IDS=1 python3 -c "import bot; ok,l=bot.run_self_check(); print('OK=',ok); [print(x) for x in l if 'Medien' in x]"
OK= False
✗ Medien-Transport (H1): ffmpeg/ffprobe fehlen — große Bilder und alle Videos blieben liegen
✓ Medien-Eingangsschutz (5.2)

$ timeout 900 bash scripts/regressionstest.sh 2>&1 | grep -E "Medien|Selbstcheck|Ergebnis"
❌ Selbstcheck-Invarianten (run_self_check) — Log:
✗ Medien-Transport (H1): ffmpeg/ffprobe fehlen — große Bilder und alle Videos blieben liegen
✅ Medien-Transport H1 (Bild/Video)
== Ergebnis: 60/63 bestanden ==

GEGENPROBE (Attrappen im PATH, damit tools_available() wahr wird):
$ mkdir -p /tmp/.../fakebin && printf '#!/bin/sh\nexit 0\n' > fakebin/ffmpeg && cp fakebin/ffmpeg fakebin/ffprobe && chmod +x fakebin/*
$ PATH="$D:$PATH" python3 scripts/test_media_h1.py; echo EXITCODE=$?
Traceback (most recent call last):
  File ".../scripts/test_media_h1.py", line 59, in <module>
    assert BIG.exists() and BIG.stat().st_size > 0, "Testbild konnte nicht erzeugt werden"
AssertionError: Testbild konnte nicht erzeugt werden
EXITCODE=1

$ sed -n '36,38p' scripts/test_media_h1.py   (Stelle heute unveraendert, Zeilennummer identisch)
if not media.tools_available():
    print("⚠ ffmpeg/ffprobe fehlen — H1-Test übersprungen (kein Fehlschlag)")
    sys.exit(0)
```

**Widerleger (hält):** Der Tatbestand haelt — ich habe ihn Zeile fuer Zeile nachgestellt und keinen Weg gefunden, ihn wegzumessen. Aber ich habe zwei Dinge widerlegt, die an der Meldung haengen, und eines davon ist neu.

WAS HAELT (selbst gemessen, nicht uebernommen)
- `scripts/test_media_h1.py:36-38` steht heute unveraendert: `if not media.tools_available(): print(...); sys.exit(0)`. Im Kontroll-Container ist `tools_available()` False (`which ffmpeg ffprobe` → Exitcode 1), der Lauf endet mit EXITCODE=0, alle zwoelf `check(...)`-Zeilen bleiben ungeprueft.
- `run()` in `scripts/regressionstest.sh:122-132` kennt genau zwei Ausgaenge: `GESAMT+1` und entweder `✅` oder `❌ + FAILS+1`. Eine dritte Kategorie „uebersprungen" gibt es nicht. Deshalb druckt der Laeufer `✅ Medien-Transport H1 (Bild/Video)` fuer einen Lauf, der nichts gemessen hat, und `60/63` zaehlt diese Zeile mit.
- Nicht repariert: `git log df5dc69..HEAD -- scripts/test_media_h1.py scripts/regressionstest.sh` ist leer, und in `HEAD` (76d3513) stehen beide Stellen woertlich gleich. Die Vorsitzung hat nicht an der falschen Stelle gesucht.

WAS NICHT HAELT — ① die Schwere „laut"
Die Meldung raeumt selbst ein, dass es kein stiller Bruch ist; ich besta

---

## [71] scripts/test_log_sync_quittung.py — LAUT
**Maschine:** beide

Der beschriebene Bruch ist unverändert reproduzierbar. `_lauf()` (heute Zeile 58–68) startet `scripts/log_sync.sh` mit `capture_output=True` und wertet WEDER `returncode` NOCH `stderr` aus. `log_sync.sh` läuft mit `set -uo pipefail` (Zeile 20) — ohne `-e` —, ruft rsync in Zeile 32 und 87 und endet trotz `rsync: command not found` mit Rückgabewert 0. Folge auf jeder Maschine ohne rsync: keine Datei wird kopiert, die Quittung hat einen leeren MITGENOMMEN-Block, `bericht.md` landet unter AUSGESCHLOSSEN mit dem Vermerk „unklar - bitte melden" — und der Prüfer meldet wörtlich die in der Meldung genannten zwei Zeilen. Er beschuldigt damit die Quittungslogik; das fehlende Werkzeug wird nirgends benannt. Kein Reparatur-Commit: `git log -S'die mitgenommene Datei fehlt unter MITGENOMMEN'` nennt allein 97e5251 (Entstehung); der spätere 590b63d hat nur den Pfad-Filter angefasst, nicht die Werkzeugprüfung. Zur Einordnung des Grades: Der Prüfer selbst wird ROT und stoppt den Regressionslauf (`scripts/regressionstest.sh:187`) — insofern laut, aber mit falschem Schild, was in diesem Projekt schon einmal eine Stunde Fehlersuche an der falschen Stelle bedeutet hätte. Der STILLE Teil sitzt eine Ebene tiefer und ist der eigentlich gefährliche: `log_sync.sh` gibt bei fehlendem rsync Rückgabewert 0 und die Meldung „Keine Log-Änderungen — nichts zu pushen" aus. Produktiv aufgerufen sähe ein Abgleich, der nichts kopiert, exakt wie ein Abgleich aus, bei dem es nichts zu kopieren gab — dieselbe Klasse wie der einundzwanzig Tage tote Tageswächter. Was ich NICHT messen kann: ob Mac und VPS rsync haben (dort wäre der Prüfer grün). Gemessen ist nur der Kontroll-Container; die Code-Schwäche — verworfener Rückgabewert, verworfenes stderr, keine `command -v rsync`-Schranke — liegt jedoch im Quelltext und gilt für alle drei Maschinen. rsync steht in ABHAENGIGKEITEN.md (Zeile 120) als Abhängigkeit, aber ohne Verfügbarkeitsprüfung.

**Beleg:**
```
$ command -v rsync ; echo rc=$?
rc=1

$ cd .../stand-aktuell-ro && python3 scripts/test_log_sync_quittung.py
✗ nur Transportrelevantes gilt als ausgeschlossen: die mitgenommene Datei fehlt unter MITGENOMMEN
✗ gleiche Lage schreibt die Quittung NICHT neu: die Quittung wurde neu geschrieben, obwohl sich nichts geändert hat
✓ eine echte Änderung schreibt sehr wohl (Gegenrichtung)
✓ die Quittung bleibt lesbar kurz
❌ 2 Quittungs-Prüfung(en) fehlgeschlagen: nur Transportrelevantes gilt als ausgeschlossen, gleiche Lage schreibt die Quittung NICHT neu

$ # direkter Lauf des Skripts mit denselben umgebogenen Pfaden, OHNE capture_output-Verlust:
$ python3 - <<'PY' ... subprocess.run(["bash", ROOT/"scripts/log_sync.sh"], env=env, capture_output=True, text=True)
returncode: 0
STDOUT: Keine Log-Änderungen — nichts zu pushen.
STDERR: .../scripts/log_sync.sh: line 32: rsync: command not found

$ # erzeugte Quittung:
Letzter Abgleich: 29.08.2026, 19:31

MITGENOMMEN:

AUSGESCHLOSSEN (haette mitkommen koennen, kam nicht):
  bericht.md — unklar - bitte melden, das sollte mitkommen

$ grep -n 'set -\|rsync' scripts/log_sync.sh | head -3
20:set -uo pipefail
32:rsync -a --exclude='._*' --exclude='.DS_Store' "$SRC/" conversations/
87:  rsync -a --prune-empty-dirs \

$ git -C /home/user/claude-telegram-bot log --oneline -S'die mitgenommene Datei fehlt unter MITGENOMMEN'
97e5251 Quittungs-Fix: 5207 Zeilen, die niemand liest, und 155 Commits, die nichts sagen
```

**Widerleger (hält):** Ich habe den Fund nicht entkraeften koennen — nur seine Reichweite korrigiert. GEMESSEN, nicht uebernommen: (1) Der Pruefer faellt in der Arbeitskopie mit exakt den zwei gemeldeten Zeilen rot. (2) Ein produktionsnaher Direktlauf von log_sync.sh mit umgebogenen Pfaden endet mit RC=0, obwohl `line 32: rsync: command not found` auf stderr steht, das Log-Repo leer bleibt und die Quittung `bericht.md — unklar - bitte melden` schreibt. (3) Ursachenbeweis statt Vermutung: Ich habe einen rsync-Ersatz (Python, beachtet --exclude/--include in Reihenfolge) auf den PATH gelegt — daraufhin sind alle vier Zeilen gruen. Die Quittungslogik ist also intakt; allein das fehlende Werkzeug erzeugt den Befund, und der Pruefer beschuldigt trotzdem die Quittung.

VIER WIDERLEGUNGSVERSUCHE, alle gescheitert: (a) ERREICHBAR? Ja — vor Zeile 32 stehen nur `[ -d "$SRC" ]` und `cd "$REPO"`, keine Werkzeugschranke. (b) REPARIERT? Nein — scripts/log_sync.sh ist byte-identisch mit 590b63d (20.08.) und mit dem heutigen HEAD (76d3513); `git grep "command -v" -- scripts/` findet im ganzen Repo nur `ufw` (daily_check.sh:536) und `md5` (icloud_spiegel.sh:124), kein rsync. (c) KEIN AUFRUFER? Nein — stuendlicher systemd-

---

## [32] .claude/hooks/guard-master-files.sh — STILL
**Maschine:** beide

Unveraendert: Z. 9-16 holen den Dateipfad ueber einen `python3`-Einzeiler, dessen Fehler durch `2>/dev/null` verschluckt werden; es gibt keinen Zweig "Auswertung misslungen -> blockieren". Ausgefuehrt gemessen mit einem PATH, der `git`, `cat`, `basename`, `tr`, `dirname` enthaelt aber KEIN `python3`: exit 0, Ausgabe voellig leer — obwohl die Eingabe auf ein CLAUDE.md in einem Klon zeigte, der nachweislich 1 Commit hinter origin/mac-produktivstand steht und mit vollem PATH exit 2 liefert. Erfolgsfall und Totalausfall sind dadurch nicht unterscheidbar: gleicher Exit-Code, gleiche leere Ausgabe. Dieselbe Fail-open-Klasse gilt fuer jedes kaputte JSON (gemessen: Eingabe `kein json` -> rc=0, leer). Der neue Pruefer test_governance_hook.py deckt diesen Fall NICHT ab — er ruft den Hook ausschliesslich mit vollem PATH auf; die Schranke bleibt an dieser Stelle ungeprueft.

**Beleg:**
```
$ printf '{"tool_input":{"file_path":"$W/work/CLAUDE.md"}}' | bash guard-master-files.sh
BLOCKIERT (Fuehrungs-Register): … ist 1 Commit(s) hinter origin/mac-produktivstand …
rc=2

$ printf '{"tool_input":{"file_path":"$W/work/CLAUDE.md"}}' | env -i PATH=$S/minbin /bin/bash guard-master-files.sh 2>&1
rc=0 out=[]
(minbin enthaelt git, cat, basename, dirname, tr — kein python3)

$ printf 'kein json' | bash guard-master-files.sh 2>&1
rc=0 out=[]

$ grep -n 'PATH\|python3' scripts/test_governance_hook.py
1:#!/usr/bin/env python3   (keine PATH-Variante im Pruefer)
```

**Widerleger (hält):** Ich habe vier Widerlegungswege versucht und keiner traegt.

**(1) Ist der Zweig erreichbar?** Ja. `.claude/settings.json` verdrahtet den Hook als `PreToolUse` fuer `Edit|Write|MultiEdit|NotebookEdit`. Im heutigen Stand (df5dc69) steht in Z. 9-16 unveraendert der `python3`-Einzeiler mit `2>/dev/null`; danach folgt sofort `basename`/`tr`/`case`, und wer nicht passt, faellt in `*) exit 0`. Es gibt **keinen** Zweig, der eine misslungene Auswertung als Blockade behandelt. Selbst gelesen und selbst ausgefuehrt.

**(2) Faengt vorher etwas ab?** Nein. Ein leerer `$FILE` ergibt `basename ""` = leer, `tr` = leer, `case ""` trifft `*)` und beendet mit 0. Kein `set -e`, kein Timeout, keine Pruefung auf leeres Ergebnis.

**(3) Laengst repariert / an falscher Stelle gesucht?** Nein. Die Datei hat in der gesamten Historie **genau zwei** Fassungen (`025ef8b` vom 26.07., `f5098f4` vom 29.08.). Beide holen den Pfad ueber denselben `python3`-Einzeiler mit `2>/dev/null`; die Aenderung vom 29.08. betraf nur die Schreibweisen-Empfindlichkeit des `case`. In keiner Fassung existiert ein Fail-closed-Zweig.

**(4) Falsche Maschine?** Der Hook laeuft ueberall, wo eine Claude-Code-Sitzung das Repo als Projekt

---

## [41] .claude/hooks/guard-master-files.sh — STILL
**Maschine:** beide

Gleiche Sache wie 32, hier mit der Maschinen-Zuordnung. Der Kern — python3 faellt aus, FILE ist leer, `case` endet in `*) exit 0`, kein Blockier-Zweig — ist heute unveraendert und wurde ausgefuehrt bestaetigt (siehe Beleg). NICHT pruefbar von hier aus ist die Zusatzbehauptung ueber die Maschine: dass der Hook-PATH am Mac vom Login-PATH abweicht und `/usr/bin/python3` dort ein Stub ohne Command Line Tools ist — das braucht Adams Mac. Der Nebenbefund der Meldung (relative Pfade -> DIR=".") traegt so NICHT: gemessen mit `file_path: "CLAUDE.md"` und cwd im Klon ergibt sich rc=2, korrekt blockiert; DIR="." ist nur dann falsch, wenn der Hook-Prozess ein anderes Arbeitsverzeichnis als das Repo hat — dann faellt er wieder still auf durchlassen (Z. 45 `rev-parse … || exit 0`).

**Beleg:**
```
$ sed -n '8,16p;44,48p' .claude/hooks/guard-master-files.sh
INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c " … except Exception: print('') " 2>/dev/null)
DIR=$(dirname "$FILE")
git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1 || exit 0

$ printf '{"tool_input":{"file_path":"$W/work/CLAUDE.md"}}' | env -i PATH=$S/minbin /bin/bash guard-master-files.sh 2>&1
rc=0 out=[]        # mit vollem PATH: rc=2 BLOCKIERT

$ cd $W/work && printf '{"tool_input":{"file_path":"CLAUDE.md"}}' | bash guard-master-files.sh
BLOCKIERT (Fuehrungs-Register): Die Kopie von CLAUDE.md in . …
rc=2      -> relativer Pfad greift, Nebenbefund traegt hier nicht
```

**Widerleger (hält):** Ich habe vier Widerlegungswege probiert; keiner traegt den Kern.

(1) ERREICHBARKEIT — bestaetigt, nicht gelesen sondern ausgefuehrt. Ich habe ein Wegwerf-Repo gebaut, das nachweislich 1 Commit hinter `origin/mac-produktivstand` steht, und den Hook aus dem Klon (df5dc69) darauf gefahren. Kontrolliertes A/B, in dem sich NUR `python3` unterscheidet, erwartete Zeile vorher hingeschrieben: mit echtem python3 im selben minimalen PATH → `rc=2` + Blockier-Meldung; mit einem python3-Stub, der wie ein CLT-Shim `exit 1` macht → `rc=0`, **kein Zeichen auf stdout, keines auf stderr**. Ebenso bei python3 ganz ausserhalb des PATH → rc=0. `set -uo pipefail` hat kein `-e`, die leere `FILE` faellt ueber `basename ""` in `case *) exit 0`. Der Bruch sieht exakt wie Ruhe aus.

(2) AUFRUFER — vorhanden. `.claude/settings.json` verdrahtet den Hook als PreToolUse auf `Edit|Write|MultiEdit|NotebookEdit`; die Datei ist eingecheckt, liegt also auf allen drei Maschinen. Kein Skript ohne Aufrufer.

(3) LAENGST REPARIERT? — nein. Der Hook wurde zuletzt in `f5098f4` (29.08., 16:56) angefasst; `f5098f4` ist Vorfahr von df5dc69, und zwischen df5dc69 und dem HEAD in /home/user liegt kein weiterer Commit auf dieser

---

## [60] .claude/hooks/guard-master-files.sh — STILL
**Maschine:** beide

Dritte Meldung zur selben Zeile 9; Befund identisch und heute unveraendert. Die von der Meldung angefuehrte Messung `env -i PATH=/nonexistent` ist allerdings unsauber: bei komplett leerem PATH scheitern zusaetzlich `cat` (Z. 8), `basename` und `tr` (Z. 38) mit sichtbaren "command not found"-Meldungen — der Hook faellt dann eben NICHT lautlos aus. Die Meldung war nur deshalb im Ergebnis richtig, weil der saubere Fall (git vorhanden, python3 fehlt) denselben Ausgang hat; das habe ich nachgemessen und dort ist die Ausgabe tatsaechlich vollstaendig leer. Der Befund traegt also, seine Messung nicht.

**Beleg:**
```
$ printf '{"tool_input":{"file_path":"$W/work/CLAUDE.md"}}' | env -i PATH=/nonexistent /bin/bash guard-master-files.sh 2>&1
rc=0 out=[guard-master-files.sh: line 8: cat: command not found
guard-master-files.sh: line 38: basename: command not found
guard-master-files.sh: line 38: tr: command not found]
   -> nicht lautlos, drei sichtbare Fehler

$ printf '{"tool_input":{"file_path":"$W/work/CLAUDE.md"}}' | env -i PATH=$S/minbin /bin/bash guard-master-files.sh 2>&1
rc=0 out=[]
   -> sauberer Fall (nur python3 fehlt): lautlos DURCHGELASSEN, obwohl 1 Commit hinter Master
```

**Widerleger (hält):** Ich habe alle vier Widerlegungswege abgeklopft und keiner traegt.

**1. Ist der Zweig erreichbar?** Ja, und er ist der einzige Weg. Zeile 9 ist der ALLEINIGE Parser des Hooks — es gibt keinen Fallback (`jq`, `sed`, Parameter-Expansion). Faellt `python3` aus, ist `FILE` leer, `_BASIS` (Z. 38) leer, `case ""` faellt in `*) exit 0` (Z. 41). `set -uo pipefail` ohne `-e` bricht nichts ab. Alles gemessen, nicht gelesen.

**2. Wird die Datei aufgerufen?** Ja. Genau eine echte Aufrufstelle: `.claude/settings.json:19`, PreToolUse-Matcher `Edit|Write|MultiEdit|NotebookEdit`. Datei ist ausfuehrbar (`-rwxrwxr-x`). Alle uebrigen Treffer auf `guard-master-files` sind Erwaehnungen in Doku/Pruefer, keine Aufrufer.

**3. Laengst repariert?** Nein. `git log --all -- .claude/hooks/guard-master-files.sh` liefert genau zwei Commits (`025ef8b` Anlage, `f5098f4` 29.08. 16:56 — die basename/tr-Korrektur, Fund ③). Zeile 9 wurde in KEINEM davon angefasst; sie steht seit der Anlage unveraendert. Auch die abweichende HEAD-Linie (`76d3513`) traegt dieselbe Zeile 9.

**4. Falsche Maschine?** Nein — der Hook ist ein Repo-Artefakt und laeuft auf jeder Maschine, auf der Claude Code im Repo arbeitet (Mac + Containe

---

## [61] .claude/hooks/guard-master-files.sh — STILL
**Maschine:** beide

Z. 50 unveraendert: `BEHIND=$(git … rev-list HEAD..origin/mac-produktivstand --count 2>/dev/null || echo 0)`. Fehlt die Referenz, ist BEHIND=0 und der Hook laesst wortlos durch — ein fehlender Vergleichsmassstab ist nicht von "Stand ist aktuell" zu unterscheiden. Ausgefuehrt an einem Klon, der 1 Commit hinter seinem Ursprung steht, dessen Ursprung aber nur `main` fuehrt: rc=0, keine Ausgabe. Der praktisch wichtigste Ausloeser ist nicht der VPS, sondern ein Umbenennen/Loeschen des Branches `mac-produktivstand` — danach ist die Schranke fuer immer dunkel, ohne dass irgendwo etwas rot wird. ZWEI Einschraenkungen an der Meldung: (a) Ihr Beleg traegt nicht — `log_sync.sh:186` pusht `origin main` in einem ANDEREN Repo (`$HOME/logsync/claude-bot-logs`, Z. 23), nicht im Bot-Repo; das sagt ueber dessen Refs nichts aus. (b) Ein normaler `git clone` holt alle Branches; im Kontroll-Container ist `origin/mac-produktivstand` vorhanden, und Worktrees teilen sich die Refs ohnehin. Die Lokalisierung "VPS-Klon fuehrt nur origin/main" ist damit unbelegt und von hier aus nicht pruefbar; der Code-Defekt selbst ist gemessen. Auch dieser Fall fehlt in test_governance_hook.py.

**Beleg:**
```
$ cd $W3/work && git branch -r
  origin/HEAD -> origin/main
  origin/main
$ git rev-list HEAD..origin/main --count
1
$ git rev-list HEAD..origin/mac-produktivstand --count
fatal: ambiguous argument 'HEAD..origin/mac-produktivstand': unknown revision …
$ printf '{"tool_input":{"file_path":"$W3/work/CLAUDE.md"}}' | bash guard-master-files.sh 2>&1
rc=0 out=[]      # 1 Commit hinter — trotzdem DURCHGELASSEN, kommentarlos

$ grep -n 'REPO=' scripts/log_sync.sh
23:REPO="${LOG_SYNC_REPO:-$HOME/logsync/claude-bot-logs}"   # anderes Repo als das Bot-Repo

$ git -C /home/user/claude-telegram-bot branch -r
  origin/claude/remote-control-2an15f
  origin/claude/telegram-bot-auth-401-g6yqrr
  origin/mac-produktivstand
  origin/main
```

**Widerleger (hält):** Der Code-Defekt besteht im heutigen Stand (df5dc69) unveraendert und ich habe ihn selbst ausgefuehrt reproduziert — nicht nur gelesen.

WAS ICH GEPRUEFT HABE, UM IHN ZU ENTKRAEFTEN (alles negativ):

(1) Ist der Zweig erreichbar? Ja. Vor Zeile 50 stehen nur zwei Abbrueche: der `case` auf den kleingeschriebenen Basisnamen (CLAUDE.md/MIGRATION.md passieren) und `fetch origin || exit 0`. Bei erfolgreichem Fetch und fehlender Referenz faellt `rev-list HEAD..origin/mac-produktivstand` mit rc!=0 durch, `|| echo 0` setzt BEHIND=0, `-gt 0` ist falsch, `exit 0`. Gemessen: rc=0, leere Ausgabe, obwohl der Klon 1 Commit hinter dem Master steht.

(2) Wird die Datei aufgerufen? Ja. `.claude/settings.json` registriert sie als PreToolUse-Hook fuer `Edit|Write|MultiEdit|NotebookEdit` ueber `$CLAUDE_PROJECT_DIR`. Der Regressionslauf ruft ihren Pruefer auf (regressionstest.sh:202).

(3) Laengst repariert? Nein. Nur zwei Commits haben die Datei je angefasst (f5098f4, 025ef8b). Die BEHIND-Zeile ist auf beiden Zweigen byte-identisch — auch auf main (76d3513) steht sie unveraendert; der Unterschied zwischen den Zweigen betrifft ausschliesslich den `case`-Block.

(4) Fehlt der Pruefer wirklich? Ja. `test_g

---

## [53] ABHAENGIGKEITEN.md — STILL
**Maschine:** beide

Der Kern traegt und ist inzwischen schlimmer als gemeldet: Zeile 39 nennt als Pruefkriterium weiterhin `bash scripts/regressionstest.sh` → 11/11 (Mac UND VPS). AUSGEFUEHRT gemessen sind es heute 63 Pruefungen (61 `run`-Zeilen + zwei eigene GESAMT-Erhoehungen in Zeile 223 und 234) — nicht 61 wie in der Meldung, und 52 mehr als das Kriterium behauptet. Die Ironie ist belegt: derselbe Laeufer begruendet in Zeile 116-121 ausfuehrlich, warum GESAMT gezaehlt und nicht getippt wird ('Eine Kennzahl, die von Hand nachgepflegt werden muss, wird irgendwann nicht nachgepflegt') — und die Registerzeile daneben ist genau so eine. Warum STILL und nicht laut: Die Zahl hat keinen maschinellen Verbraucher; sie kann daher nicht rot werden, sondern hoert nur auf, ein Kriterium zu sein. NICHT TRAGFAEHIG an der Meldung: die Behauptung, es sei 'die EINZIGE Zeile' mit einer handgepflegten Zahl. Gemessen: elf Zeilen im Register tragen ein N/N (24/7, 3x 7/7, 11/11, 71/71, 10/10, 5/6, 2/6, 1/8, dazu 0085/2028). Drei davon habe ich ausgefuehrt — test_websuche_ausfall, test_freigabedialog, test_websuche_check liefern je genau 7 gruene Zeilen, ihre 7/7 stimmen also. Die 11/11 ist der Ausreisser, nicht die Regel. Zweiter Punkt: Kein Verbraucher liest die 11 — daily_check.sh:132 prueft den Exit-Code und echot die selbst gemessene Ergebniszeile, hora.py:486-489 ebenso, updater.py:269-281 parst die Zahl, vergleicht sie aber gegen eine SELBST gemessene Grundlinie (`_fail_key`), nie gegen 11, node_vollzug_pruefen.sh:129 nutzt nur den Exit-Code. Der Bruch ist also rein menschenseitig: Er trifft den, der vor einem Fundament-Update nachschlaegt, was 'gruen' heisst.

**Beleg:**
```
$ grep -n 'regressionstest' ABHAENGIGKEITEN.md → Zeile 39: | **8.2-Minimaltest** `scripts/regressionstest.sh` | ... | `bash scripts/regressionstest.sh` → 11/11 (Mac UND VPS) |

$ grep -c 'run "' scripts/regressionstest.sh → 61
$ grep -n 'GESAMT=' scripts/regressionstest.sh → 121:GESAMT=0 / 124:  GESAMT=$((GESAMT+1)) / 223:GESAMT=$((GESAMT+1)) / 234:GESAMT=$((GESAMT+1))
$ bash -n scripts/regressionstest.sh → SYNTAX_OK

AUSGEFUEHRT (Kopie, `if "$@" ...` → `if true`, damit jede erreichbare Pruefung zaehlt, keine an fehlender .venv scheitert):
$ bash /tmp/.../zaehl.sh | tail -1 →
== Ergebnis: 63/63 bestanden ==

Gegenmessung der uebrigen Zahlen:
$ grep -on "[0-9]\+/[0-9]\+" ABHAENGIGKEITEN.md → 26:24/7 35:7/7 36:7/7 37:7/7 39:11/11 58:71/71 71:10/10 92:5/6 151:0085/2028 157:2/6 188:1/8  (elf Zeilen, nicht eine)
$ for f in test_websuche_ausfall test_freigabedialog test_websuche_check; do python3 scripts/$f.py | grep -c '^✓'; done → 7 / 7 / 7  (die drei 7/7 stimmen)

Verbraucher:
$ sed -n '132,138p' scripts/daily_check.sh → `if reg="$(sudo -u claudebot bash .../regressionstest.sh 2>&1)"; then last="$(echo "$reg" | tail -1)"; add "✅ Regressionstest: $last"` — Exit-Code + eigene Zeile, kein Vergleich mit 11
$ sed -n '486,489p' scripts/hora.py → `return p.returncode == 0, (letzte[-1] ...)`
$ sed -n '269,281p' scripts/updater.py → parst passed/total, gibt sie zurueck; `_fail_key` vergleicht gegen die selbst gemessene baseline, nicht gegen 11
```

**Widerleger (hält):** Ich habe vier Entkraeftungswege probiert; alle vier schlagen fehl, und zwei drehen sich gegen die Meldung ins Schaerfere.

(1) ERREICHBARKEIT — kein Zweig faengt etwas ab. Alle 61 `run`-Aufrufe stehen im Rumpf auf oberster Ebene; die einzigen `if`-Bloecke zwischen Zeile 121 und 246 sind der `run()`-Rumpf selbst, die MEMDIR-Vorbelegung (Zeile 150) und die beiden Nachweis-Bloecke. Kein einziger Aufruf ist bedingt. Ich habe den Laeufer AUSGEFUEHRT — und zwar UNVERAENDERT, ohne den `if true`-Eingriff der Vorsitzung: `== Ergebnis: 60/63 bestanden ==`. Der Eingriff war ueberfluessig und haette die Messung verfaelschen koennen; `GESAMT` wird in `run()` VOR dem Aufruf erhoeht (Zeile 124), Fehlschlaege aendern den Nenner also nie. Dass ich auf demselben Wert 63 lande wie sie auf ihrem, bestaetigt die Zahl auf sauberem Weg.

(2) HISTORIE — nicht laengst repariert, und schlimmer als gemeldet. Die Zeile wurde zuletzt in `025ef8b` (26.07.) angefasst. Dort hatte der Laeufer bereits 30 `run`-Zeilen. Die 11 war also schon beim letzten Anfassen falsch — es ist keine Zahl, die langsam driftete, sondern eine, die seit ueber einem Monat keinen Stand mehr beschreibt.

(3) MASCHINEN-ANNAHME — die Meldun

---

## [57] ABHAENGIGKEITEN.md — STILL
**Maschine:** Mac

Der Kern traegt und ist mit einer Gegenprobe belegt: `run.sh`, `guardian.sh`, `com.jakuna.claude-telegram-bot.plist` und `com.jakuna.claude-telegram-bot-guardian.plist` liegen im Repo-Wurzelverzeichnis und kommen im Register NULL Mal vor — kein Eintrag, kein Abhaengiger, kein Pruefbefehl. Beide Waechter melden das nicht: bot.py `_c_register_vollstaendig` (Zeile 8169-8210) prueft eine fest verdrahtete Siebenerliste plus `scripts/glob('*.py')`; scripts/differenz.py `_versionierte_wurzelmodule` (Zeile 242-249) nimmt `git ls-files '*.py'`, und `_register_tabellenzeilen` sucht in der ersten Tabellenspalte nur nach `[\w./-]+\.py`. Beide melden heute GRUEN, waehrend die vier Dateien fehlen — genau die Sorte Bruch, die wie Ordnung aussieht. ZWEI PUNKTE DER MELDUNG TRAGEN NICHT: (1) 'die beiden LaunchAgents' ist ungenau — `com.jakuna.vps-backup` steht sehr wohl im Register (Zeile 30, mit `[Mac]`-Marke und Pruefbefehl `launchctl list | grep -c vps-backup` = 1). Es fehlen die beiden Bot-/Guardian-Plists, nicht 'die LaunchAgents' insgesamt. (2) 'die Luecke folgt exakt der Maschinengrenze' ist FALSCH — sie folgt der DATEIENDUNG. Gegenprobe ausgefuehrt: ein neues `scripts/neuwaechter.sh` laesst den Selbstcheck gruen, ein `scripts/neuwaechter.py` macht ihn rot; ebenso beim Differenzmesser (`neuesmodul.py` → rot, `neuesskript.sh` → unsichtbar). Dass alle zehn `scripts/*.sh` eingetragen sind, ist also Disziplin, nicht Pruefung — das naechste Shell-Skript in `scripts/` ist genauso ungeschuetzt wie die vier Mac-Dateien. Der Waechter ist blind fuer JEDE .sh und jede .plist, egal auf welcher Maschine.

**Beleg:**
```
$ for n in guardian.sh run.sh com.jakuna.claude-telegram-bot.plist com.jakuna.claude-telegram-bot-guardian.plist com.jakuna.vps-backup.plist; do grep -c -- "$n" ABHAENGIGKEITEN.md; done →
guardian.sh : 0
run.sh : 0  (der eine Treffer war 'Änderungshistorie' in Zeile 172 — Teilstring, kein Eintrag)
com.jakuna.claude-telegram-bot.plist : 0
com.jakuna.claude-telegram-bot-guardian.plist : 0
com.jakuna.vps-backup.plist : 0  — ABER: $ grep -n 'vps-backup' ABHAENGIGKEITEN.md → Zeile 30: | **launchd `com.jakuna.vps-backup`** `[Mac]` | ... | `launchctl list | grep -c vps-backup` = `1` |  → dieser LaunchAgent IST eingetragen

$ for f in scripts/*.sh; do echo $(basename $f) $(grep -c $(basename $f) ABHAENGIGKEITEN.md); done → alle zehn ≥1 (api_cache_pflege 1, daily_check 8, log_sync 5, mail_konto_anlegen 1, md2pdf 1, node_vollzug_pruefen 1, regressionstest 6, test_zielumgebung 3, vps_backup 3, vps_schnappschuss 1)

SELBSTCHECK AUSGEFUEHRT (Funktionsrumpf bot.py:8169-8210 mit gebundenem _REPO_DIR exec'd):
Ist-Zustand: GRUEN (kein Befund)
mit scripts/neuwaechter.sh (nicht im Register): GRUEN -> blind fuer .sh
mit scripts/neuwaechter.py: ROT -> ohne Eintrag im Abhängigkeits-Register: scripts/neuwaechter.py

DIFFERENZMESSER AUSGEFUEHRT (Kopie mit git init, damit `git ls-files` traegt — im ro-Stand bricht er korrekt mit 'Die Dateimenge ist leer' ab):
$ python3 scripts/differenz.py → '✓ keine Differenz — alle Mengen decken sich'  (obwohl run.sh/guardian.sh/2 Plists fehlen)
$ touch neuesmodul.py neuesskript.sh; git add -A; python3 scripts/differenz.py →
'✗ Wurzelmodule ohne Tabellenzeile in ABHAENGIGKEITEN.md: neuesmodul.py'  — die .sh bleibt unsichtbar

$ sed -n '242,249p;255,266p' scripts/differenz.py → `git ls-files "*.py"` bzw. `re.findall(r"[\w./-]+\.py", erste_spalte)`
$ sed -n '81
```

**Widerleger (hält):** Der Kern haelt, und ich habe ihn selbst gemessen statt ihn zu uebernehmen. (1) Die vier Dateien liegen im Wurzelverzeichnis des heutigen Stands und kommen im Register NULL Mal vor — Festtext-Grep, kein Muster. (2) Beide genannten Waechter sind nachweislich .py-blind: Ich habe `_c_register_vollstaendig` per AST aus bot.py geloest, mit gebundenem `_REPO_DIR` und geloeschtem `__pycache__` ausgefuehrt und drei Gegenproben gefahren — eine neue `scripts/*.sh` laesst ihn GRUEN, eine neue Wurzel-`.plist` laesst ihn GRUEN, nur eine neue `scripts/*.py` macht ihn ROT. Der Differenzmesser bildet seine Mengen beidseitig ueber `.py` (`git ls-files "*.py"` bzw. `[\w./-]+\.py` in der ersten Tabellenspalte). (3) Es gibt keinen dritten Waechter, der die Luecke auffangen koennte: `grep -rn ABHAENGIGKEITEN` ueber alle .py/.sh liefert genau drei Stellen — bot.py:8193, differenz.py:259 und eine blosse KOMMENTARZEILE in daily_check.sh:121.

Meine Widerlegungsversuche und warum sie scheitern:
- Register nur fuer .py gedacht? Nein. Der Docstring des Pruefers sagt selbst „Module UND Betriebsskripte", und alle zehn `scripts/*.sh` stehen drin — also Disziplin, nicht Pruefung. Kein Ausschluss-Vermerk im Kopf (

---

## [24] README.md — STILL
**Maschine:** keine

Der Kern der Meldung traegt und ist heute unveraendert: README.md:147 nennt "Python 3.10+" als unterste Fassung, ampel.py:109 macht `import tomllib` (erst ab 3.11), der `except Exception:` in `_load_rules()` verschluckt den ModuleNotFoundError, und `_load_rules()` liefert dann `_DEFAULT_RULES`. GEMESSEN mit echtem python3.10 (nicht simuliert — /usr/bin/python3.10 ist hier vorhanden): eine TOML-Regel `[rot.keywords] Klienten=["mustermann"]` wird still ignoriert, `classify('Termin mit Mustermann')` liefert **gelb** statt **rot**. Genau die stille Sorte: kein Absturz, kein Alarm, nur eine Stufe zu niedrig. Bestaetigt sind auch die Nebenaussagen: tomllib ist die EINZIGE 3.11-Anforderung im Repo (ast.parse aller 87 .py mit feature_version=(3,10): 0 Fehler; Grep auf datetime.UTC/asyncio.timeout/StrEnum/except*/ExceptionGroup/Self/assert_never: nur ampel.py), und es gibt weder pyproject.toml noch setup.py. Der frueher dokumentierte zweite 3.12-Zwang (PEP-701-f-String) ist bereits repariert (bot.py:4636 ff., Kommentar belegt den Fix) — er kaeme also nicht hinzu.

WAS NICHT TRAEGT — und das ist die eigentliche Halbwahrheit der Meldung: Sie behauptet, verloren gingen "Adams eigene Ampel-Regeln — bewusst ueber den cloud-freien Button-Weg eingetragen". GEMESSEN ist das falsch. Der `/ampel`-Button-Weg schreibt nach `_CUSTOM_PATH` = ~/.claude/ampel_custom.json und wird von `_load_custom()` mit `json.loads` gelesen — ohne tomllib. Unter python3.10 liefert `classify('Termin mit knopfdruckname')` weiterhin **rot ['Klient-Custom']**. Verloren geht ausschliesslich die von Hand gepflegte TOML (`~/.claude/ampel_rules.toml`, laut ampel_rules.example.toml-Kopf serverseitig editiert), nicht der Button-Bestand. Die Meldung benennt als Schaden genau den Teil, der ueberlebt.

ZWEITE EINSCHRAENKUNG — betroffene Maschine: Heute laeuft der Bruch auf KEINER Maschine. Dokumentiert (MIGRATION.md 1.3/1.6, verifiziert 14.07.): VPS = Python 3.13.5, Mac = 3.12, Kontroll-Container = 3.11.15. Der Zweig ist auf dem VPS aber real erreichbar — scripts/vps_backup.sh:44 sichert /home/claudebot/.claude/ampel_rules.toml, die Datei existiert dort also. Der Defekt ist damit eine latente Falschzusage des README, die bei jeder Neuinstallation auf einer 3.10-Distribution (z. B. Ubuntu 22.04 LTS) sofort zuschlaegt — nicht ein aktiver Bruch. Die tatsaechliche Python-Fassung auf VPS und Mac konnte ich von hier aus nicht selbst messen, nur der Ablage entnehmen.

**Beleg:**
```
$ cd .../stand-aktuell-ro && grep -n -i python README.md
147:1. **Python 3.10+** und `pip install -r requirements.txt` auf dem Host.
(einzige Fassungsangabe im ganzen README; steht im Abschnitt "## VPS-Migration (später)")

$ grep -rn "datetime\.UTC|asyncio\.timeout|StrEnum|except\*|ExceptionGroup|typing import Self|assert_never|tomllib|add_note(" --include=*.py .
./ampel.py:109:        import tomllib
./ampel.py:111:            data = tomllib.load(f)
--- ende grep ---

$ python3 - <<'PY'  (ast.parse aller .py mit feature_version=(3,10))
geprueft: 87 syntaktisch 3.10-inkompatibel: 0
PY

$ ls -a | grep -i "pyproject|setup.py|setup.cfg"
keine

$ python3.10 -c "import tomllib"
ModuleNotFoundError: No module named 'tomllib'

$ cat rules.toml -> [rot.keywords] Klienten = ["mustermann", "erika beispiel"]
$ cat custom.json -> {"rot": [{"label": "Klient-Custom", "pattern": "knopfdruckname"}], "gelb": []}
$ AMPEL_RULES_PATH=$D/rules.toml AMPEL_CUSTOM_PATH=$D/custom.json python3.10 -c "import ampel; ..."
=========== python3.10 ===========
_load_rules ist DEFAULT? True
geladene rot-Sektionen: ['keywords', 'klienten', 'regex']
classify TOML-Name  : gelb ['Kalender:termin']
classify Knopf-Name : rot ['Klient-Custom']
=========== python3.11 ===========
_load_rules ist DEFAULT? False
geladene rot-Sektionen: ['keywords']
classify TOML-Name  : rot ['Klienten:mustermann']
classify Knopf-Name : rot ['Klient-Custom']
(-> Button-/JSON-Regeln ueberleben 3.10 unveraendert; nur die TOML faellt weg)

$ ... python3.10 -c "logging.basicConfig(level=DEBUG); import ampel; ampel._load_rules()"
ERROR:claude-tg-bot.ampel:Ampel-Regeldatei nicht ladbar — nutze Defaults
Traceback (most recent call last):
  File ".../ampel.py", line 109, in _load_rules
    import tomllib
ModuleNotFoundError: No module name
```

**Widerleger (hält):** Ich habe vier Widerlegungswege gefahren; alle vier sind gescheitert.

(1) "Laengst repariert / falscher Messpunkt." Die Vorsitzung mass gegen 76d3513, die Arbeitskopie ist df5dc69 — ein NEUERER Commit (29.08. 19:17 vs. 11:37). Das war der beste Ansatz, er traegt nicht: `git diff 76d3513 df5dc69 -- README.md ampel.py` ist LEER. Beide Dateien sind im heutigen Stand byte-gleich.

(2) "Der Zweig wird vorher abgefangen." Nein — selbst reproduziert mit echtem /usr/bin/python3.10: `_load_rules() is _DEFAULT_RULES` → True, `classify('Termin mit Mustermann')` → **gelb**, unter 3.11 und 3.13 → **rot**. Genau eine Stufe zu niedrig, ohne Absturz.

(3) "Der Fall ist unerreichbar, weil pip auf 3.10 vorher laut scheitert." Das war mein staerkster Kandidat. Gemessen: claude-agent-sdk 0.2.127 >=3.10, python-telegram-bot >=3.10, python-dotenv >=3.10, pymupdf 1.28.2 >=3.10; via PyPI edge-tts >=3.7, faster-whisper >=3.9, caldav >=3.10. **Keine einzige Abhaengigkeit sperrt 3.10** — die Installation laeuft durch, nichts faengt den Fall ab. Kein pyproject.toml/setup.py/setup.cfg/.python-version, das eine Untergrenze setzen wuerde.

(4) "Es gibt noch andere 3.11-Zwaenge, tomllib ist also nicht der Punkt" 

---

## [54] README.md — STILL
**Maschine:** keine

Dieselbe Sache wie Meldung 24, mit zwei eigenen Zusatzbehauptungen — eine haelt, eine ist ueberzogen.

HAELT: "requirements.txt enthaelt keinen python_requires-Wert" — gemessen richtig, requirements.txt ist eine reine Paketliste (claude-agent-sdk==0.2.127, python-telegram-bot[webhooks]>=22.7, python-dotenv, edge-tts, pymupdf, faster-whisper, caldav), und es gibt weder pyproject.toml noch setup.py. Die einzige Fassungsangabe im Projekt ist die README-Zeile selbst. HAELT AUCH: "Es gibt eine log.exception-Zeile und keinen Pruefer, der sie liest." Gemessen — kein Test und keine Selbstcheck-Zeile beruehrt `_load_rules`; der einzige Treffer auf "Ampel nicht ladbar" (scripts/wachposten.py:314, geprueft von test_wachposten.py:370) faengt eine **Ausnahme aus `classify()`** ab. Unter 3.10 wirft `classify()` aber nichts, es liefert nur die falsche Farbe — der Wachposten setzt `ampel_weg` gar nicht und meldet ordnungsgemaess "gelb". Der Schutz greift also genau an der Stelle nicht, an der er greifen muesste. Nebenbei gemessen und derselben Familie: scripts/regressionstest.sh:83 setzt `AMPEL_RULES_PATH="$PRUEFHEIM/ampel-regeln.json"` — ein .json-Pfad an einen TOML-Lader; auch dieser Fehlschlag faellt in denselben stillen Default-Zweig und wird von nichts bemerkt.

WAS NICHT TRAEGT: Die Folgerung "klassifiziert weiter — nur ohne Adams eigene rote Regeln, also ohne die Klienten-Namen, fuer die die Ampel gebaut wurde" ist zur Haelfte falsch. Verloren geht nur die TOML (`~/.claude/ampel_rules.toml`, inkl. `[rot.klienten]`). Die per `/ampel`-Button gepflegten Regeln liegen als JSON in `ampel_custom.json` und werden von `_load_custom()` ohne tomllib gelesen — gemessen unter python3.10: `classify('Termin mit knopfdruckname')` -> rot ['Klient-Custom']. Und CLAUDE.md verweist fuer "die heikelsten Muster, Klienten-Namen" ausdruecklich auf genau diesen Button-Weg. Der Schaden ist real, aber kleiner und anders gelagert als beschrieben.

EBENFALLS ZU KORRIGIEREN: "Auf einer 3.10-Maschine (die der README ausdruecklich einlaedt: VPS oder Raspberry Pi)" — heute existiert keine solche Maschine. Dokumentiert: VPS 3.13.5, Mac 3.12, Kontroll-Container 3.11.15; ich konnte davon nur den Container selbst messen. Der Bruch ist damit latent, nicht aktiv: eine falsche Zusage im README, die bei einer Neuinstallation auf einer 3.10-Distribution (Ubuntu 22.04 LTS, und ein Raspberry-Pi-Image dieser Generation) sofort zutraefe. Der Zweig selbst ist auf dem VPS erreichbar — die TOML wird dort gesichert (vps_backup.sh:44), existiert also.

**Beleg:**
```
$ cat requirements.txt | grep -v '^#'
claude-agent-sdk==0.2.127
python-telegram-bot[webhooks]>=22.7
python-dotenv>=1.0
edge-tts>=7.0
pymupdf>=1.28.2
faster-whisper>=1.2
caldav>=3.2
(kein python_requires; `ls -a | grep pyproject|setup.py|setup.cfg` -> keine)

$ grep -rn "version_info|python_requires|requires-python" --include=*.py --include=*.sh --include=*.txt .
(kein Treffer im Bot-Code — einzige Fassungsangabe ist README.md:147)

$ python3.10 -c "import tomllib"
ModuleNotFoundError: No module named 'tomllib'

$ AMPEL_RULES_PATH=$D/rules.toml AMPEL_CUSTOM_PATH=$D/custom.json python3.10 -c "import ampel; ..."
_load_rules ist DEFAULT? True
classify TOML-Name  : gelb ['Kalender:termin']
classify Knopf-Name : rot ['Klient-Custom']
   (dieselben Aufrufe unter python3.11: rot ['Klienten:mustermann'] / rot ['Klient-Custom'])

$ ... python3.10 -c "logging.basicConfig(level=DEBUG); import ampel; ampel._load_rules()"
ERROR:claude-tg-bot.ampel:Ampel-Regeldatei nicht ladbar — nutze Defaults
ModuleNotFoundError: No module named 'tomllib'

$ grep -rn "_load_rules|AMPEL_RULES_PATH|ampel_rules" --include=*.py --include=*.sh .
./ampel.py:34,35,105,133
./scripts/regressionstest.sh:83:export AMPEL_RULES_PATH="$PRUEFHEIM/ampel-regeln.json"
./scripts/vps_backup.sh:44
./scripts/test_hermetik.py:11 (nur Nennung im Docstring)
./scripts/differenz.py:285,311,313 (nur Ablagen-Differenz, nicht das Laden)
-> KEIN Test fuehrt _load_rules aus

$ grep -n "^def _c_|^    def _c_" bot.py   -> 31 Selbstcheck-Zeilen, keine zur Ampel-Regeldatei
   (einzige mit 'ampel' im Namen: _c_log_repo_ampel, bot.py:8340 — prueft ob Sekretariats-Code existiert, nichts am Regel-Laden)

$ sed -n '298,320p' scripts/wachposten.py
        except Exception:
            farbe, labels, ampel_weg = "rot", [], True   # Ausfall z
```

**Widerleger (hält):** Ich habe alle Entkraeftungswege selbst probiert und keiner traegt. (1) Zeile besteht: README.md:147 sagt "Python 3.10+" — unveraendert bei df5dc69 UND bei HEAD (76d3513); es ist die einzige Fassungsangabe im gesamten Projekt (kein pyproject.toml, kein setup.py, kein setup.cfg, kein python_requires). (2) Der Weg ist erreichbar und nichts faengt ihn vorher ab: `python3.10 -m compileall` ueber den ganzen Baum laeuft mit EXIT 0 durch — der Code ist 3.10-syntaxkompatibel, es gibt keinen lauten Absturz. (3) Auch die Abhaengigkeiten fangen nichts ab: importlib.metadata gibt fuer claude-agent-sdk 0.2.127, python-telegram-bot 22.8, pymupdf 1.28.2 und python-dotenv jeweils `Requires-Python >=3.10` — `pip install -r requirements.txt` gelingt auf 3.10. (4) Ausgefuehrt unter 3.10.20 gegen eine echte TOML: `_load_rules() is _DEFAULT_RULES` -> True mit log.exception; `classify()` wirft NICHT, sie liefert nur eine andere Farbe. Damit greift der Rot-Rueckfall in scripts/wachposten.py:290-299 (`except Exception` bzw. `classify is None`) nachweislich nicht — `import ampel` gelingt ja, tomllib steht erst in _load_rules. (5) Die Gegenprobe zur "kein Pruefer"-Haelfte: mit einem verifizierten sitecustomi

---

## [12] bot.py — STILL
**Maschine:** beide

Die Stelle ist heute bot.py:3029 (unverändert). Der Edit/Write-Zweig prüft weiterhin die feste, gross-/kleinschreibungsempfindliche Teilzeichenkette "/claude-telegram-bot", während der Bash-Zweig zwei Zeilen tiefer über _ist_repo_bezug/_REPO_MARKEN geht — die Asymmetrie besteht wörtlich. AUSGEFÜHRT gemessen: Ein Pfad mit anderer Gross-/Kleinschreibung (Mac, unempfindliches Dateisystem, resolve() normalisiert Schreibweise nicht) und ein R4-Probelauf-Klon (probe-mail) laufen am Riegel VORBEI. Die Asymmetrie selbst ist ebenfalls direkt gemessen: derselbe Pfad wird vom Bash-Zweig gesperrt (_is_repo_write_cmd -> True, weil _REPO_MARKEN den ABGELEITETEN Ordnernamen enthält), vom Edit-Zweig nicht. ZWEI EINSCHRÄNKUNGEN, die die Meldung nicht nennt: (a) Die Gross-/Kleinschreibungs-Lücke trifft BEIDE Zweige, denn auch _REPO_MARKEN enthält die feste Zeichenkette — die Asymmetrie zeigt sich nur, wenn der Bot selbst aus einem anders benannten Ordner läuft. (b) Der Durchrutscher landet NICHT auf 'erlaubt', sondern im Freigabe-Dialog: darf_dauerfreigabe('Edit') = False, Edit/Write stehen in _NO_ALWAYS_TOOLS, eine Dauerfreigabe ist also unmöglich. Still ist trotzdem das Richtige: dass die 8.7-Schranke NICHT gefeuert hat, ist nirgends sichtbar — Adam sieht eine ganz normale Edit-Anfrage und kann sie durchwinken. Seit Einführung (025ef8b) nicht angefasst.

**Beleg:**
```
$ python3 m12.py  (echtes make_permission_callback, Attrappe nur für die Sitzung)
Edit /home/claudebot/claude-telegram-bot/bot.py -> PermissionResultDeny
Edit /Users/jakuna/Projects/Claude-Telegram-Bot/bot.py -> PASSED-THROUGH(AttributeError)
Edit /Users/jakuna/Projects/claude-telegram-bot/bot.py -> PermissionResultDeny
Edit /Users/jakuna/Projects/probe-mail/bot.py -> PASSED-THROUGH(AttributeError)
Edit /home/claudebot/probe-mail/bot.py -> PASSED-THROUGH(AttributeError)
(PASSED-THROUGH = Zweig nicht gefeuert, Ablauf lief weiter bis bot.py:3155 sess.always_allowed_tools / 3222 sess.pending_permissions -> Dialog)

_REPO_MARKEN = ('stand-aktuell-ro', 'claude-telegram-bot')
Bash-ist_repo_bezug: False | is_repo_write: False | sed -i s/a/b/ /Users/jakuna/Projects/Claude-Telegram-Bot/bot.py
Bash-ist_repo_bezug: True  | is_repo_write: True  | sed -i s/a/b/ /home/claudebot/claude-telegram-bot/bot.py

$ python3 -c "... bot._is_repo_write_cmd('sed -i s/a/b/ <eigener Repo-Ordner>/bot.py')" -> True
   bei gleichem Pfad: Edit -> KEIN Deny (fällt in den Dialog)   == die Asymmetrie, ausgeführt

$ python3 -c "print(bot.darf_dauerfreigabe('Edit'))" -> False
$ grep -n '_NO_ALWAYS_TOOLS = ' bot.py -> 2278:_NO_ALWAYS_TOOLS = ({"WebFetch", "Bash", "Write", "Edit", "MultiEdit", "NotebookEdit"} | set(_COST_TOOLS))
$ git log --oneline df5dc69 -S'"/claude-telegram-bot" in str(Path(raw)' -- bot.py -> 025ef8b (Ersteinbringung, seither unverändert)
```

**Widerleger (hält):** Der Bruch besteht. Eigene Messung mit dem ECHTEN `make_permission_callback` (nicht gelesen, ausgeführt): Läuft bot.py aus einem R4-Probelauf-Klon (`probe-mail`), rutschen Edit UND Write auf die eigene bot.py am 8.7-Riegel vorbei in den Freigabe-Dialog, während `sed -i` und `git -C … commit` auf demselben Pfad hart abgelehnt werden. Läuft bot.py aus einem Ordner namens `claude-telegram-bot`, sind alle vier zu. Ursache wie gemeldet: Zeile 3029 prüft die feste Teilzeichenkette "/claude-telegram-bot", der Bash-Zweig (2543/2589) das ABGELEITETE `_REPO_MARKEN = (_REPO_DIR.name, "claude-telegram-bot")`. Die Rang-B-(a)-Reparatur vom 25.08. hat nur den Bash-Zweig nachgezogen — klassischer Geschwister-Fall.

Vier Widerlegungsversuche, alle gescheitert: (1) Erreichbarkeit — vor dem Edit-Zweig steht nur der Skill-Deny, danach fängt nichts Edit/Write ab (bis 3260 durchgelesen, ausgeführt bestätigt: der Durchrutscher registriert `sess.pending_permissions` und wartet auf Adams Knopf). (2) Werkzeug abgeschaltet — nein: `hauptsitzungs_optionen` (3805) setzt `permission_mode="default"`, `can_use_tool=make_permission_callback(...)`, KEINE `disallowed_tools`; Edit steht dem Agenten offen, und Repo-Les

---

## [20] bot.py — STILL
**Maschine:** beide

_blumen_zeile() liegt heute bei bot.py:4006-4042, die Zeile bei 4021 — unverändert. Der Leser rechnet fest aus Path.home(), der Schreiber scripts/stundenblume.py:66-68 respektiert BLUMEN_DIR. AUSGEFÜHRT gemessen: Bei gesetztem BLUMEN_DIR mit einer frisch geschriebenen, lückenlosen Kette meldet bot._blumen_zeile() 'noch keine Glieder (läuft der Zeitgeber?)' — falscher Pfad und tote Kette sind in /status tatsächlich nicht unterscheidbar. Regressionstest.sh:41 biegt BLUMEN_DIR um, der Leser folgt nicht. EINE KORREKTUR AN DER MELDUNG: Der Mac-Teil ist falsch begründet. Am Mac liegt kein HOME-Versatz vor (die plist setzt HOME=/Users/jakuna, und run.sh erbt es); es gibt dort schlicht KEINEN Stundenblumen-Zeitgeber — im Repo existieren nur die plists für Bot, Guardian, VPS-Backup und iCloud-Spiegel. Die Meldung 'läuft der Zeitgeber?' ist am Mac also WAHR, nicht falsch. Der echte, gemessene Bruch ist der BLUMEN_DIR-Vertrag (identisch mit Meldung 35).

**Beleg:**
```
$ HOME=<probe/heim> BLUMEN_DIR=<probe/blum> python3 -c "kette in BLUMEN_DIR mit zeit=now, befunde=[] geschrieben; import bot; print(bot._blumen_zeile())"
Path.home() = /tmp/.../probe/heim
BLUMEN_DIR  = /tmp/.../probe/blum
_blumen_zeile() -> 🪷 Belegkette: noch keine Glieder (läuft der Zeitgeber?)

$ grep -n BLUMEN_DIR scripts/regressionstest.sh
41:export BLUMEN_DIR="$PRUEFHEIM/blumen"
100:mkdir -p ... "$BLUMEN_DIR" ...
$ grep -n BLUMEN_DIR bot.py   -> (keine Ausgabe)

$ grep -n 'HOME' -A2 com.jakuna.claude-telegram-bot.plist
29:    <key>HOME</key>
30-    <string>/Users/jakuna</string>
$ for f in *.plist scripts/mac/*.plist; do grep -o '<string>[^<]*stundenblume[^<]*</string>' "$f"; done
(keine Ausgabe -> am Mac gibt es keinen Stundenblumen-Zeitgeber)
```

**Widerleger (hält):** Der Kern der Meldung haelt und ist von mir ausgefuehrt nachgemessen — ich konnte ihn nicht entkraeften, nur seine Wirkung einordnen.

HAELT (selbst gemessen, nicht uebernommen):
1. Der Code ist unveraendert. `bot.py:4021` lautet bei `df5dc69` (der Arbeitskopie, byte-identisch mit `git show df5dc69:bot.py`) UND beim lokalen HEAD `76d3513` gleich: `kette = Path.home() / ".claude" / "stundenblumen" / "kette.jsonl"`. `grep BLUMEN_DIR bot.py` ist bei beiden Staenden leer. `df5dc69` ist NICHT Vorfahr von HEAD — die Zeile steht also in zwei getrennten Straengen gleich. Kein Reparatur-Commit vorhanden (`git log -S BLUMEN_DIR -- bot.py` leer).
2. Das Verhalten ist reproduziert, nicht gelesen: bei gesetztem BLUMEN_DIR mit lueckenloser Kette DORT meldet `bot._blumen_zeile()` „noch keine Glieder (laeuft der Zeitgeber?)". Falscher Pfad und tote Kette sind in /status tatsaechlich nicht unterscheidbar — das gilt sogar unabhaengig von BLUMEN_DIR, weil `Path.home()` mit dem ausfuehrenden Benutzer wandert.
3. Ein Punkt, den die Meldung nicht nennt, der sie aber traegt: `bot.py:6522` liest `POSTFACH_DIR` per `os.environ.get` — derselbe Vertrag, dieselbe Klasse Zustandsordner, derselbe Schreiber. `_bl

---

## [26] bot.py — STILL
**Maschine:** beide

Die Stelle ist heute bot.py:8046-8049 (`except Exception: continue`) bzw. 8038 (`if not pins: return`). Beide Ausstiege existieren und führen AUSGEFÜHRT zu einer grünen Prüfzeile ohne jede Messung — gemessen mit einem umgebogenen _REPO_DIR: sowohl bei entferntem Pin (requirements.txt ohne '==') als auch bei einem Pin auf ein nicht installiertes Paket meldet run_self_check '✓ Pin-Divergenz (C2)'. DIE BEGRÜNDUNG DER MELDUNG TRÄGT ABER NICHT: Der genannte Auslöser — 'Selbstcheck läuft nicht in der Bot-venv, System-Python, Paket fehlt' — kann so nicht eintreten. bot.py importiert claude_agent_sdk unbedingt auf Modulebene (Z. 40); fehlt das Paket, scheitert schon der Import LAUT mit ImportError, run_self_check läuft gar nicht erst. Und claude-agent-sdk ist derzeit das EINZIGE gepinnte Paket. Der `continue`-Zweig ist damit heute unerreichbar; still bricht heute nur die zweite Hälfte, `if not pins: return` — wer den Pin entfernt oder auf '>=' lockert, bekommt eine dauerhaft grüne Divergenz-Wache. Das ist real, reproduziert und lautlos, aber es ist eine andere Bruchstelle als die gemeldete.

**Beleg:**
```
$ cp requirements.txt fakerepo/ && sed -i 's/^claude-agent-sdk==0.2.127/claude-agent-sdk>=0.2.127/' fakerepo/requirements.txt
$ python3 -c "import bot; bot._REPO_DIR=Path('.../fakerepo'); ok,l=bot.run_self_check(); print([x for x in l if 'Pin-Divergenz' in x])"
['✓ Pin-Divergenz (C2)']            <- kein Pin mehr vorhanden, Zeile trotzdem gruen

$ echo 'gibtesnicht==9.9.9' >> fakerepo/requirements.txt && (derselbe Aufruf)
['✓ Pin-Divergenz (C2)']            <- Pin auf nicht installiertes Paket, Zeile trotzdem gruen

$ python3 -c "import importlib.metadata as m; print(m.version('claude-agent-sdk'))" -> 0.2.127
$ grep -c '==' requirements.txt (nur Pin-Zeilen) -> genau EIN Pin: claude-agent-sdk==0.2.127
$ python3 -c "<meta_path-Blocker fuer claude_agent_sdk>; import bot"
IMPORT SCHEITERT LAUT: ImportError simuliert fehlend
$ sed -n 40p bot.py -> from claude_agent_sdk import (
```

**Widerleger (hält):** Die Meldung besteht — ich habe sie unabhaengig nachgemessen und keinen Weg gefunden, sie zu entkraeften.

GEMESSEN AM ARBEITSSTAND df5dc69 (bot.py:8032-8053, `_c_pin_divergenz`):
Der Waechter arbeitet, wenn er etwas zu messen hat (Pin auf 0.2.118 verbogen → ROT mit Klartext). Er meldet aber GRUEN ohne jede Messung, sobald requirements.txt keine `==`-Zeile mehr traegt (`if not pins: return`, Z. 8038-8039) — reproduziert. Das ist genau die gefaehrliche Fehlerrichtung: Wer den Pin auf `>=` lockert, erhoeht das Rueckfall-Risiko beim Rebuild aufs Maximum und schaltet zugleich die Wache still ab. Bruch, der wie Ruhe aussieht.

MEINE FUENF WIDERLEGUNGSVERSUCHE — alle gescheitert:
1. „Ein zweiter Waechter faengt es ab." Nein. `requirements.txt` wird in bot.py an genau EINER Stelle gelesen (Z. 8033); kein Test, kein Skript, kein Selbstcheck sichert die Existenz des Pins zu. Die 0.2.127-Treffer in scripts/ sind ausnahmslos Fixture-Daten in eigenen Temp-Dateien (test_nachzieher_c1.py, test_hora.py).
2. „Laengst repariert, Vorsitzung sah alten Code." Nein. Die Funktion ist in der Arbeitskopie df5dc69 (29.08., 19:17) und im Repo-HEAD 76d3513 im Kern zeilengleich.
3. „Falsche Maschine." Nein, be

---

## [35] bot.py — STILL
**Maschine:** beide

Bestätigt und schärfer als Meldung 20: bot.py:4021 kennt BLUMEN_DIR nicht, scripts/stundenblume.py:66-68 schon. AUSGEFÜHRT gemessen — mit gesetztem BLUMEN_DIR und einer lückenlosen, sekundenfrischen Kette liefert bot._blumen_zeile() 'noch keine Glieder (läuft der Zeitgeber?)'. Auch der zweite Teil der Meldung trägt: scripts/test_stundenblumen.py:704-732 ersetzt bot.Path.home durch eine Attrappe (`bot.Path.home = staticmethod(lambda: heim)`) und schreibt die Kette direkt unter dieses Ersatz-Heim; geprüft wird damit genau die verdrahtete Variante, der BLUMEN_DIR-Vertrag nie — obwohl dieselbe Testdatei in Zeile 17 BLUMEN_DIR auf einen anderen Ordner setzt. Der Prüfer zementiert die Annahme, statt sie zu messen. daily_check.sh:74 setzt BLUMEN_DIR ausdrücklich, weil root ein anderes Path.home() sieht — genau die Präambel, die dem Bot-Leser fehlt.

**Beleg:**
```
$ HOME=<probe/heim> BLUMEN_DIR=<probe/blum> python3 -c "(kette.jsonl in BLUMEN_DIR: {'zeit': time.time(), 'befunde': []}); import bot; print(bot._blumen_zeile())"
_blumen_zeile() -> 🪷 Belegkette: noch keine Glieder (läuft der Zeitgeber?)

$ sed -n 66,68p scripts/stundenblume.py
ZUSTAND = Path(os.environ.get("BLUMEN_DIR") or (Path.home() / ".claude" / "stundenblumen"))
KETTE = ZUSTAND / "kette.jsonl"
$ sed -n 4021p bot.py
    kette = Path.home() / ".claude" / "stundenblumen" / "kette.jsonl"

$ grep -n 'Path.home\|BLUMEN_DIR' scripts/test_stundenblumen.py
17:os.environ["BLUMEN_DIR"] = str(_TMP / "blumen")
704:    echt = bot.Path.home
707:    bot.Path.home = staticmethod(lambda: heim)
711:        assert "noch keine Glieder" in bot._blumen_zeile()
732:        bot.Path.home = echt
$ sed -n 74p scripts/daily_check.sh
            "BLUMEN_DIR=$BOTHOME/.claude/stundenblumen"
```

**Widerleger (hält):** Die Sachaussagen der Meldung halten meiner eigenen Messung stand — ihre Einstufung nicht. Getrennt:

WAS TRÄGT (selbst ausgeführt, nicht gelesen):
1. Die Asymmetrie ist echt. `scripts/stundenblume.py:66` bildet ZUSTAND aus `BLUMEN_DIR` mit Rückfall auf `Path.home()`; `bot.py:4021` kennt nur `Path.home() / ".claude" / "stundenblumen" / "kette.jsonl"`. Mit gesetztem BLUMEN_DIR schreibt die Blume nach dort, und `bot._blumen_zeile()` meldet trotz sekundenfrischer Kette „noch keine Glieder (läuft der Zeitgeber?)" — von mir mit echtem Schreiber (nicht handgelegter Datei) reproduziert.
2. Die Prüferlücke ist echt und schärfer, als die Meldung sie fasst: `scripts/test_stundenblumen.py:704-732` ersetzt `bot.Path.home` und legt die Kette per Hand unter das Ersatz-Heim. Damit misst KEIN Test, dass der Ort, an den `stundenblume.py` schreibt, derselbe ist, den `bot.py` liest. Nicht nur der BLUMEN_DIR-Vertrag bleibt ungemessen, sondern die Schreiber-Leser-Übereinstimmung überhaupt.
3. bot.py kennt die Bauform durchaus: `bot.py:6522` liest `POSTFACH_DIR` mit genau dem Rückfall-Muster für eine ebenso geteilte Ablage. BLUMEN_DIR ist die Ausnahme — Geschwister-Regel, gleicher Pfadtyp, nur eine Hälft

---

## [39] bot.py — STILL
**Maschine:** beide

bot.py:137 unverändert: _USAGE_FILE = Path.home()/'.config'/'claude-telegram-bot'/'usage.json' — ohne Umgebungsschlüssel, während die unmittelbaren Nachbarn alle einen haben (_PREFS_FILE/USER_PREFS_FILE Z.108-111, LIMIT_MARKE_FILE, LIMIT_STAND_FILE). _load_usage() (Z.140-147) schluckt jede Ausnahme und liefert {} — ein gewanderter HOME lässt die Verbrauchs-/Nennwert-Buchführung stumm bei null anfangen. Die zweite Hälfte ist ebenfalls gemessen und der härtere Teil: Der Wegwerf-Riegel des Regressionslaufs kann diese Ablage nicht umbiegen (er kennt nur Umgebungsvariablen, 30 Stück in scripts/regressionstest.sh:36-99), und scripts/differenz.py sieht sie nicht — dessen Ist-Menge entsteht ausschliesslich über os.environ.get(NAME) im Pfad-Zusammenhang (_zustandsschluessel(), Z.351-366), und _ist_ortsabhaengig() (Z.493-507) schlägt nur bei den Zeichenketten '/home/claudebot' bzw. '…claude-telegram-bot' an, nie bei Path.home(). Ausgeführt: differenz.py meldet 'keine Differenz — alle Mengen decken sich', obwohl diese Ablage ungeriegelt ist. usage.json steht auch nicht in GEWOLLT_OFFEN, ist also nicht als bewusste Ausnahme abgelegt, sondern schlicht unsichtbar. Heute wird der Schaden nur dadurch vermieden, dass EIN Test (scripts/test_limitwarnung_b4.py:203) bot._USAGE_FILE von Hand umbiegt — Disziplin, kein Riegel.

**Beleg:**
```
$ sed -n 137p bot.py
_USAGE_FILE = Path.home() / ".config" / "claude-telegram-bot" / "usage.json"
$ sed -n 108,111p bot.py
_PREFS_FILE = Path(os.environ.get("USER_PREFS_FILE") or Path.home() / ".config" / "claude-telegram-bot" / "prefs.json")
$ grep -n 'USAGE_FILE' bot.py scripts/*.py
bot.py:137,142,143,151,152 | scripts/test_limitwarnung_b4.py:203: bot._USAGE_FILE = _TMP / "usage.json"   (Handarbeit im Test)

$ (Kopie als git-Repo, damit differenz.py seine versionierte Menge bilden kann)
$ python3 scripts/differenz.py
Differenzmesser
○ ablagen_differenz
○ festpfade_differenz
○ kostenzuweisung_differenz
○ module_differenz
✓ keine Differenz — alle Mengen decken sich
$ grep -n 'GEWOLLT_OFFEN = ' -A22 scripts/differenz.py -> nur CLAUDE_MEMORY_DIR, BOT_ENVFILE, WHISPER_MODEL_PATH, AUFTRAGSBUCH_RIEGEL, CLAUDE_WORKDIR (kein usage.json)
```

**Widerleger (hält):** Widerlegung gescheitert; der harte Teil ist jetzt AUSGEFUEHRT belegt statt gelesen.

WAS ICH ZU ENTKRAEFTEN VERSUCHT HABE:

(1) "Laengst repariert / falsche Stelle gesucht?" — Nein. In df5dc69 steht bot.py:137 unveraendert ohne Umgebungsschluessel. usage.json kommt in keiner .md vor, steht nicht in GEWOLLT_OFFEN, hat keinen export in scripts/regressionstest.sh (dort 30 exports, HOME ist keiner davon — es wird nur als ${HOME:-/home/claudebot} fuer die zwei Nachweise GELESEN).

(2) "Zweig erreichbar?" — Ja. Schreibpfad: _record_usage (bot.py:157-190) -> _save_usage (149-153); einziger Produktivaufrufer bot.py:12043 (ResultMessage). Lesepfad: _usage_today (553) -> cmd_usage (4767) und Kontingent-Knopf (9603). Und ein Pruefpfad: scripts/test_limitwarnung_b4.py ruft bot._record_usage() echt auf.

(3) "Riegel greift vielleicht doch?" — GEGENPROBE GEFAHREN, das ist der Kern. Voller Lauf auf einer Kopie mit HOME=Wegwerfverzeichnis, __pycache__ vorher geloescht, Eingriff verifiziert, erwartete Zeile vorher notiert:
  - UNVERAENDERT: 60/63, im Fake-HOME landet NICHTS. Die Ruhe kommt allein von der Handarbeit in test_limitwarnung_b4.py:203.
  - MIT ENTKERNTER Handarbeit (die eine Zeile durch 

---

## [50] components.json — STILL
**Maschine:** beide

Die Meldung besteht aus zwei Haelften, und nur eine traegt. ERSTE HAELFTE (kein Maschinenfeld / venv-Pfade zeigen auf Mac und Container ins Leere): traegt NICHT mehr. Genau das wurde HEUTE, am 29.08. um 17:29 (Commit 5d2590d), gemessen und bewusst als legitim entschieden — `scripts/differenz.py::_VPS_GEBUNDEN` fuehrt `components.json` mit ausgeschriebener Begruendung: der Versions-Waechter laeuft ausschliesslich auf dem VPS (kein Zeitgeber auf dem Mac), und ein toter Pfad wird LAUT gemeldet (Befund D), nicht still. Ausgefuehrt bestaetigt. Nebenbei ist die Zaehlung falsch: der Bot-venv-Pfad steht 7x, nicht 8x (8 venv-Pfade insgesamt, der achte ist das litellm-venv). ZWEITE HAELFTE traegt vollstaendig und ist unrepariert: Es gibt keine Komponente `python`, kein Feld `maschine`, und im gesamten laufenden Code wird die Python-Fassung NIRGENDS gemessen — waehrend nodejs auf Hauptversionen ueberwacht wird. Genau diese Fassung laeuft zwischen den drei Maschinen auseinander (Mac 3.12.13 / VPS 3.13.5 / Container 3.11.15, im Bauauftrag vom 29.08. selbst als Vorbedingung notiert: "Drei Python-Fassungen bedeuten, dass ein gruener Prueflauf auf einer Maschine ueber die beiden anderen nichts aussagt"). Der Bruch ist still: das Register sieht vollstaendig aus, und niemand meldet, dass die tragende Fassung ungeprueft ist.

**Beleg:**
```
BEFEHL 1 (erste Haelfte — ausgefuehrt, nicht gelesen):
  python3 -c "import differenz as d; print(d._ist_bewusst_vps_gebunden(Path('components.json'))); print(sorted(d._feste_pfade_in_json()))"
ERGEBNIS:
  components.json bewusst VPS-gebunden? True
  feste Pfade in JSON: []
Quelle der Entscheidung: scripts/differenz.py, _VPS_GEBUNDEN["components.json"] = "Register des Versions-Waechters, der ausschliesslich auf dem VPS laeuft (kein Zeitgeber auf dem Mac). Und er meldet einen toten Pfad LAUT (`Quelle nicht erreichbar`, Befund D) — der Fall ist nicht still."
  git -C /home/user/claude-telegram-bot log -1 --format='%ad %s' --date=short 5d2590d
  -> 2026-08-29 "Engywucks drei Reste — (c) gebaut statt abgelegt, und alle elf Funde geprueft"  (Commit-Text: "components.json (8x): ... alle elf sind LEGITIM")

BEFEHL 2 (Zaehlung der Meldung):
  python3 -c "import json,collections; print(collections.Counter(c.get('venv') for c in json.load(open('components.json'))['components']))"
ERGEBNIS: Counter({None: 11, '/home/claudebot/claude-telegram-bot/.venv': 7, '/home/claudebot/litellm/venv': 1})
  -> 'achtmal' ist 7x; 19 Komponenten insgesamt.

BEFEHL 3 (zweite Haelfte — kein python-Eintrag, kein Maschinenfeld):
  python3 -c "import json; cs=json.load(open('components.json'))['components']; print([c['name'] for c in cs if c['name'].startswith('python')]); print('Feld maschine irgendwo?', any('maschine' in c for c in cs))"
ERGEBNIS:
  ['python-telegram-bot']
  Feld maschine irgendwo? False

BEFEHL 4 (Suchraster bewusst weit gefasst, damit 'nicht vorhanden' auch traegt):
  grep -rnE "sys\.version|version_info|platform\.python|python3? --version" --include="*.py" --include="*.sh" scripts bot.py run.sh guardian.sh
ERGEBNIS: (leer)
Gegenprobe, dass das Raster ueberhaupt trifft:
  grep -rn 
```

**Widerleger (hält):** Ich habe die Meldung in der vorgelegten Form (erste Haelfte tot, zweite Haelfte tragend) nicht entkraeften koennen — die zweite Haelfte haelt nach eigener Messung vollstaendig, und sie ist unrepariert.

WAS ICH BESTAETIGT HABE (alles selbst ausgefuehrt auf df5dc69 = origin/mac-produktivstand, 29.08. 19:17, der juengste Stand; das lokale HEAD 76d3513 vom Vormittag ist ein aelterer, abgezweigter Stand):

1. components.json fuehrt 19 Komponenten. Keine heisst `python` — der einzige Treffer auf "python" ist `python-telegram-bot`, also ein pip-Paket, nicht der Interpreter. Kein einziger Eintrag hat ein Feld `maschine`. Die Datei ist seit 28.07.2026 nicht mehr angefasst worden (git log -- components.json), eine python-Komponente hat es in der Historie nie gegeben. Also: nicht laengst repariert, nicht an der falschen Stelle gesucht.

2. Die Python-Fassung wird im laufenden Code NIRGENDS gemessen. Ich habe das Raster bewusst weiter gefasst als die Vorsitzung (ganzer Baum statt nur scripts/bot.py/run.sh/guardian.sh, alle Dateitypen, zusaetzlich `sys.executable`, `requires-python`, `python -V`): kein `sys.version`, kein `version_info`, kein `platform.python_version`, kein `python3 --version`

---

## [1] guardian.sh — STILL
**Maschine:** VPS + Kontroll-Container (nur bei Ausfuehrung) — im Betrieb startet das Skript dort niemand

Der beschriebene Ablauf ist heute unveraendert und exakt reproduzierbar: launchctl fehlt (127), grep -q liefert 1, das `!` macht daraus wahr, der Zweig wird betreten, `$PLIST` fehlt, und die Umleitung nach `$HOME/Projects/claude-telegram-bot/logs/guardian.log` scheitert — das Skript endet mit rc=1 OHNE Logzeile. guardian.sh ist seit 26.07.2026 nicht angefasst (letzter Commit 025ef8b), es gibt keine Plattformweiche. WAS AN DER MELDUNG NICHT TRAEGT: die Rahmung "bricht auf dem VPS". guardian.sh wird auf dem Server bewusst NICHT betrieben — MIGRATION.md:340 (Akzeptanzkriterium 1.4): "Guardian wird auf dem Server NICHT nachgebaut — Restart=always + bot-interner Watchdog decken das ab." Im Repo existiert keine systemd-Unit, kein Aufrufer in scripts/, tests/ oder run.sh, und kein Eintrag in ABHAENGIGKEITEN.md. Der Bruch ist also kein Betriebsfehler auf dem VPS, sondern eine Falle fuer den, der das Skript dort je startet — genau das, wozu Adams Regel "alle Maschinen auf demselben Stand" verleitet. Zusatzbefund: guardian.sh liegt im Repo-Wurzelverzeichnis und faellt damit durch JEDES Suchraster von scripts/test_zielumgebung.sh (dort wird nur ueber `scripts/*.sh` und `scripts/*.py` iteriert) — kein einziger Pruefer sieht diese Datei.

**Beleg:**
```
$ cd .../stand-aktuell-ro && bash guardian.sh; echo "RC=$?"
guardian.sh: line 198: launchctl: command not found
guardian.sh: line 200: /root/Projects/claude-telegram-bot/logs/guardian.log: No such file or directory
RC=1

$ bash -n guardian.sh && echo OK  ->  bash -n guardian.sh: OK  (Syntax heil, der Bruch ist Laufzeit)

$ git -C /home/user/claude-telegram-bot log -1 --format='%h %ad %s' --date=format:'%d.%m.%Y %H:%M' -- guardian.sh
025ef8b 26.07.2026 00:19 Marschordnung V: eine Wortliste statt zweier, Daempfer, Alter der Frage, S1 richtig repariert

$ md5sum guardian.sh (Arbeitskopie) / git show df5dc69:guardian.sh / git show 76d3513:guardian.sh
4cb6941a72d23fe0b2d4f3f7286b56a1  (alle drei identisch)

$ grep -rn "guardian" scripts/ tests/ run.sh
KEIN TREFFER

$ grep -n -i "guardian" ABHAENGIGKEITEN.md
(keine Ausgabe — kein Register-Eintrag)

$ grep -n "NICHT nachgebaut" MIGRATION.md
340:- **Akzeptanzkriterium:** `systemctl status claude-telegram-bot` = active (running); Auto-Restart nach Kill greift. (Guardian wird auf dem Server NICHT nachgebaut — `Restart=always` + bot-interner Watchdog decken das ab.)
```

**Widerleger (hält):** Ich habe den Bruch selbst reproduziert und finde keinen Weg, ihn zu entkraeften. Die vier Widerlegungs-Angriffe gehen alle ins Leere: (1) Der Zweig ist erreichbar — nichts faengt ihn vorher ab, gemessen mit `bash guardian.sh` unter HOME=/root: RC=1. (2) Es gibt keine Plattformweiche (`uname`, `OSTYPE`, `command -v` kommen im Skript nicht vor) und keinen ROLLE-Marker. (3) Die Historie stimmt: einziger Commit an der Datei ist 025ef8b vom 26.07.2026, md5 4cb6941a72d23fe0b2d4f3f7286b56a1. (4) Die Maschinen-Annahme ist bereits richtig gestellt — die Meldung behauptet selbst keinen Betriebsfehler auf dem VPS, sondern eine Falle bei Ausfuehrung.

ZWEI KORREKTUREN, die weitergereicht werden muessen:

(a) "endet OHNE Logzeile" ist KEINE Eigenschaft des Codes, sondern des fehlenden Verzeichnisses. Mit vorhandenem $HOME/Projects/claude-telegram-bot/logs/ schreibt das Skript sehr wohl eine klare Zeile ("plist file missing at ... — cannot recover") und beendet dann mit 1. Die Stille ist ein Artefakt der Testmaschine, nicht des Ablaufs. Die Schwere-Einstufung "still" traegt in dieser Allgemeinheit nicht.

(b) "kein einziger Pruefer sieht diese Datei" ist zu stark. scripts/differenz.py::_feste_pf

---

## [5] scripts/api_cache_pflege.sh — STILL
**Maschine:** Mac (nur latent — heute unerreichbar)

Der Code-Defekt ist real und heute unveraendert da: Z. 53 nutzt `find -printf` (GNU-only), und das beschriebene Fehlerbild habe ich mit einer BSD-find-Attrappe exakt reproduziert — Mengen-Bereinigung loescht NICHTS, die Fehlermeldung verschwindet in `2>/dev/null`, und das Skript meldet danach 'Deckel gerissen' + Exit 1, was sich wie ein Platten-Befund liest statt wie ein fehlendes Werkzeug. WAS AN DER MELDUNG NICHT TRAEGT: der Teil 'Bricht auf dem Mac'. Der Zweig ist auf dem Mac heute NICHT erreichbar. `TELEGRAM_API_DIR` wird im gesamten Repo an keiner Stelle gesetzt (nur zweimal als `${...:-}`-Vorgabe gelesen), also gilt immer der Linux-FHS-Pfad `/var/lib/telegram-bot-api`, den es auf macOS nicht gibt — die Existenz-Wache in Z. 38 beendet das Skript vorher mit Exit 0. Auch der einzige Mac-Aufrufweg (`scripts/test_zielumgebung.sh` Z. 77, `env -i`) setzt die Variable nicht. Zum Zuenden braeuchte es (a) einen lokalen Bot-API-Server auf dem Mac unter genau diesem Pfad ODER eine gesetzte Variable UND (b) ein Lager ueber 30 GB. Richtig an der Meldung bleibt: `-mtime +N -delete` (Z. 48) ist portabel und liefe weiter, das Fehlerbild ist also still. Kein Geschwister-Fund: `-printf` kommt im ganzen Repo genau einmal vor. Kein Fallback (`stat`/`ls -t`) vorhanden — bestaetigt.

**Beleg:**
```
$ sed -n '53p' scripts/api_cache_pflege.sh
  aeltest="$(find "$LAGER" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | head -1 | cut -d' ' -f2-)"

(1) Reproduktion mit BSD-find-Attrappe (Wrapper, der bei -printf 'unknown primary or operator' nach stderr wirft und mit 1 endet), Lager mit 3x2 MB, CACHE_TAGE=999 (Alters-Zweig ausgeschaltet), CACHE_DECKEL_GB=0:
$ env PATH="$LAB/bin:$PATH" TELEGRAM_API_DIR=$LAB/lager2 CACHE_TAGE=999 CACHE_DECKEL_GB=0 bash scripts/api_cache_pflege.sh
Zwischenlager: 7 MB -> 7 MB (Deckel 0 MB)
⚠️ Deckel gerissen — auch nach dem Aufräumen zu groß.
EXIT=1
--- verbliebene Dateien: f1.bin f2.bin f3.bin   (KEINE geloescht)

(2) Gegenlauf mit echtem GNU find, gleiche Bedingungen:
Zwischenlager: 7 MB -> 1 MB (Deckel 0 MB) / EXIT=1 / verbliebene Dateien: 0  (alle drei geloescht)

(3) Erreichbarkeit auf dem Mac gemessen — Vorgabepfad, BSD-find-Attrappe, nackte Umgebung:
$ env -i PATH="$LAB/bin:/usr/bin:/bin" /bin/bash scripts/api_cache_pflege.sh
Kein Zwischenlager unter /var/lib/telegram-bot-api — der eigene Bot-API-Server läuft nicht.
EXIT=0        (Z. 53 nie erreicht)

(4) $ grep -rn 'TELEGRAM_API_DIR' . --include='*.sh' --include='*.py' --include='*.md'
./scripts/api_cache_pflege.sh:33:LAGER="${TELEGRAM_API_DIR:-/var/lib/telegram-bot-api}"
./scripts/daily_check.sh:195:if [ -d "${TELEGRAM_API_DIR:-/var/lib/telegram-bot-api}" ]; then
(nirgends gesetzt)

(5) $ grep -rn -- '-printf' scripts/
./scripts/api_cache_pflege.sh:53   (genau ein Vorkommen im Repo)

(6) $ git -C /home/user/claude-telegram-bot show HEAD:scripts/api_cache_pflege.sh | diff - <Arbeitskopie>  -> IDENTISCH (unveraendert seit 059fa3c, 18.08.2026)
```

**Widerleger (hält):** Ich habe alle vier Entkraeftungswege gefahren und keiner traegt.

(1) DER DEFEKT SELBST IST DA UND UNVERAENDERT. `-printf` steht genau einmal im ganzen Repo (scripts/api_cache_pflege.sh:53), die Arbeitskopie ist byte-identisch mit HEAD (76d3513, nicht nur mit dem genannten df5dc69), und `git log` ueber die Datei zeigt nur zwei Commits — zuletzt 059fa3c. Keine Reparatur an anderer Stelle, kein `stat`/`ls -t`-Fallback. Kein Geschwister-Fund.

(2) DAS FEHLERBILD HABE ICH SELBST REPRODUZIERT, nicht uebernommen. Mit eigener BSD-find-Attrappe (wirft bei `-printf` nach stderr, Exit 1): Mengen-Bereinigung loescht NICHTS, der Fehler verschwindet in `2>/dev/null`, das Skript meldet trotzdem „Deckel gerissen" und Exit 1 — liest sich wie ein Platten-Befund, ist aber ein fehlendes Werkzeug. Gegenlauf mit echtem GNU find 4.9.0 unter identischen Bedingungen: alle drei Dateien weg. Der Unterschied liegt also wirklich an `-printf`, nicht an meinem Aufbau. Ein Aufhaenger fehlt auch nicht: `aeltest` leer -> `break`, also keine Endlosschleife, sondern der stille Durchmarsch.

(3) DIE MASCHINEN-AUSSAGE HABE ICH GEGENGEPRUEFT — sie stimmt so, wie die Vorsitzung sie bereits selbst korrigiert hat. `TELEGR

---

## [65] scripts/daily_check.sh — STILL
**Maschine:** beide

Direkt gemessen und in beide Richtungen belegt: Fehlt `ss`, liefert die Pipeline leer, `${unerwartet// /}` ist leer, und der Tagescheck schreibt die positive Sicherheitsaussage `✅ Nach aussen lauschen nur SSH und der Webhook-Port`. Mit einer ss-Attrappe, die einen oeffentlichen Lauscher meldet, wird dieselbe Zeile rot. Das Gruen haengt also allein an der Anwesenheit des Werkzeugs, nicht am Zustand der Maschine — genau die Klasse Bruch, die wie Ruhe aussieht. EINE Teilbegruendung der Meldung ist jedoch falsch und sollte nicht weitergereicht werden: `auf Debian faellt /usr/sbin aus dem eingebauten Standard-PATH, den bash ohne gesetztes PATH benutzt` stimmt nicht — gemessen liefert `env -i /bin/bash -c 'echo $PATH'` genau `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`, /usr/sbin und /sbin sind enthalten. Der `env -i`-Start von test_zielumgebung.sh entzieht `ss` also NICHT; das Falschgruen entsteht nur dort, wo iproute2 gar nicht installiert ist (dieser Kontroll-Container, macOS). Ein `command -v ss`-Riegel fehlt weiterhin — bei `ufw` gibt es ihn 15 Zeilen spaeter (536).

**Beleg:**
```
$ command -v ss || echo FEHLT
FEHLT
$ ls -l /usr/sbin/ss /sbin/ss /bin/ss
ls: cannot access '/usr/sbin/ss': No such file or directory (alle drei)
$ cd g7-daily/repo && env -i PATH=<Standard> ... /bin/bash scripts/daily_check.sh ; grep lauschen logs/daily-check.log
  ✅ Nach aussen lauschen nur SSH und der Webhook-Port
$ cat g7-daily/bin/ss
#!/bin/sh
echo 'LISTEN 0      4096   0.0.0.0:3210        0.0.0.0:*'
$ env -i "PATH=$M/bin:..." ... /bin/bash dc.sh ; grep Anschluesse logs/daily-check.log
15:❌ Unerwartet offene Anschluesse: 0.0.0.0:3210
$ env -i /bin/bash -c 'echo "PATH=[$PATH]"'
PATH=[/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin]   <- widerlegt die PATH-Begruendung der Meldung
git log -S'ss -lntH' --oneline -- scripts/daily_check.sh -> 125541d (Ersteinbau, keine Reparatur)
```

**Widerleger (hält):** Ich habe alle vier Entkraeftungswege abgeklopft und keinen tragfaehigen gefunden; die Kernaussage habe ich selbst in beide Richtungen ausgefuehrt.

ERREICHBARKEIT: Der Block sitzt auf oberster Ebene, ohne umschliessendes if (naechste Struktur-Zeilen davor: 511/513/516 = Haertungs-Block, geschlossen). Vor Zeile 521 gibt es KEIN einziges bash-`exit` — die drei Treffer auf `SystemExit` (165, 322, 334) liegen in eingebetteten Python-Heredocs. Der Kopf ist `set -uo pipefail` OHNE `-e`, der Exit-Code 127 des fehlenden `ss` bricht also nichts ab. Der Zweig ist erreichbar.

KEIN RIEGEL, NIRGENDWO: `grep -rn "command -v ss|which ss|iproute"` ueber das ganze Repo → null Treffer. Der einzige `command -v` im Skript steht in Zeile 536 bei `ufw` — die Meldung benennt das korrekt.

HISTORIE: `git log -S'ss -lntH' -- scripts/daily_check.sh` liefert genau einen Commit, 125541d (Ersteinbau). Keine Reparatur. Der Block ist im Arbeitsstand df5dc69 byte-identisch (voller diff gegen `git show df5dc69` leer) UND im heutigen HEAD 76d3513 unveraendert, dort weiterhin Zeile 521.

KEIN PRUEFER: `grep -rn "lauschen|Anschluesse|lntH"` ueber alle scripts/*.py und *.sh ausser daily_check.sh → null Treffer. Die Z

---

## [14] scripts/differenz.py — STILL
**Maschine:** beide

Die Einbahnstrasse besteht: `_ist_ortsabhaengig` (heute Z. 490-506) kennt weiterhin nur `/home/claudebot` und `~/…claude-telegram-bot`; jede Mac-Form liefert False, und die Prueflaufzeile meldet dazu woertlich 'keine Differenz'. WAS AN DER MELDUNG NICHT TRAEGT — drei Punkte: (a) Die Halbsatz-Folgerung 'ein Mac-Festpfad ist vom Waechter ungesehen' ist seit cc9e773 (29.08., 11:29) FALSCH fuer `scripts/*.py`: `test_zielumgebung.sh` Abschnitt 6 sucht dort genau `/private/tmp|/private/var|/Users/|/opt/homebrew|/Library/Mobile` und wurde von mir rot gemessen. (b) Zwei der vier genannten Beispielwerte sind untaugliche Belege: `~/.claude/projects/…` ist mit `~` gerade die PORTABLE Form, und `/etc/claude-telegram-bot.env` ist der VPS-Geheimnispfad, der ueberall gleich heisst — beide duerfen nicht True liefern. (c) Es gibt heute KEINEN aktiven Bruch: alle echten Mac-Pfade im Bestand liegen in den vier launchd-Plists und in `scripts/mac/` und sind dort bauartbedingt richtig. DIE ECHTE, VERBLEIBENDE LUECKE ist enger als gemeldet, aber real: ausserhalb von `scripts/*.py` — also in den 18 Wurzelmodulen, in `*.sh` und in `*.json` — sieht KEINER der beiden Waechter eine Mac-Form. Gegenprobe: ein `/Users/jakuna/Projects/claude-telegram-bot/logs` in `ampel.py` und in `scripts/log_sync.sh` (beides laeuft auf dem VPS) laesst beide Pruefer gruen. Das ist die stille Klasse: gruen aus dem falschen Grund.

**Beleg:**
```
$ cd .../mess && python3 -c "import sys; sys.path.insert(0,'scripts'); import differenz as d; [print(repr(w), d._ist_ortsabhaengig(w)) for w in ['/Users/jakuna/Projects/claude-telegram-bot','/opt/homebrew/bin','/Volumes/MiniPC/VPS-Backup','~/.claude/projects/-Users-jakuna/memory','/home/claudebot','/home/claudebot/claude-telegram-bot/x','~/claude-telegram-bot/y']]"
'/Users/jakuna/Projects/claude-telegram-bot' False
'/opt/homebrew/bin' False
'/Volumes/MiniPC/VPS-Backup' False
'~/.claude/projects/-Users-jakuna/memory' False
'/home/claudebot' True
'/home/claudebot/claude-telegram-bot/x' True
'~/claude-telegram-bot/y' True

$ python3 scripts/test_hermetik.py | tail -6
  o ablagen_differenz: keine Differenz
  o festpfade_differenz: keine Differenz
  o kostenzuweisung_differenz: keine Differenz
  o module_differenz: keine Differenz
== Hermetik: bestanden ==

GEGENPROBE A (Mac-Pfad in scripts/*.py -> zweiter Waechter greift):
$ printf '\nMACPFAD = "/Users/jakuna/Projects/claude-telegram-bot/logs"\n' >> scripts/test_freigabedialog.py; bash scripts/test_zielumgebung.sh | grep plattformgebunden
✗ kein Pruefer schreibt einen plattformgebundenen Pfad fest: diese Pruefer laufen nur auf einer Maschine: scripts/test_freigabedialog.py
(differenz.py dabei: FUNDE: [])

GEGENPROBE B (derselbe Pfad in ampel.py + scripts/log_sync.sh -> BEIDE blind):
$ bash scripts/test_zielumgebung.sh | grep -E 'plattformgebunden|== Ziel'
✓ kein Pruefer schreibt einen plattformgebundenen Pfad fest
== Zielumgebung: 24/24 bestanden ==
$ python3 -c "...d._feste_betriebspfade()"  ->  FUNDE: []
```

**Widerleger (hält):** Ich habe vier Widerlegungswege probiert; keiner traegt.

(1) ERREICHBARKEIT/AUFRUFER — beide Waechter sind lebendig. `festpfade_differenz` wird ueber `differenz.arten()` geladen (test_hermetik.py meldet "4 Differenzart(en) geladen"), `test_zielumgebung.sh` laeuft im Regressionslauf ("Zielumgebung (bash -n + env -i)"). Kein toter Code, also kein "bricht nirgends".

(2) GIBT ES EINEN DRITTEN WAECHTER? Nein — gemessen, nicht vermutet. Ein Grep ueber den GANZEN Bestand (`--include=*.py --include=*.sh --include=*.json`) nach `opt/homebrew|/Users/|private/tmp|Library/Mobile|/Volumes/|darwin|Darwin` liefert ausserhalb von `scripts/mac/` genau SECHS Treffer: vier Kommentarzeilen, die eigene Musterzeile in `test_zielumgebung.sh:225`, und `.claude/hooks/session-start.sh`. Es gibt im Projekt exakt EINE Stelle, die Mac-Formen kennt, und ihre Menge ist `git ls-files 'scripts/*.py'` minus `scripts/mac/` (Z. 222-227). Auch ein allgemeiner Festpfad-Pruefer existiert nicht (Grep nach festpfad/hardcod/absolut in `scripts/` findet nur Prosa).

(3) IST ES LAENGST REPARIERT? Nein. `cc9e773` (29.08.) hat Abschnitt 6 gebaut — aber nur fuer `scripts/*.py`. `_ist_ortsabhaengig` (df5dc69, Z. 490-506) ist un

---

## [69] scripts/differenz.py — STILL
**Maschine:** beide

Inhaltsgleich mit Meldung 14 (dieselbe Funktion, Z. 502-506) und mit demselben Ergebnis: die Himmelsrichtung ist weiterhin einseitig, gemessen. WAS AN DIESER FASSUNG ZUSAETZLICH NICHT TRAEGT: (a) Der Kernsatz 'ein Pruefer mit Mac-Festpfad ist auf dem VPS blind UND vom Waechter dagegen ungesehen' ist fuer Pruefer — also `scripts/*.py`, genau das Wort der Meldung — seit cc9e773 (29.08., 11:29) widerlegt; `test_zielumgebung.sh` Abschnitt 6 faengt ihn, von mir rot gemessen. Fuer PRUEFER trifft die Meldung heute also nicht mehr zu; sie trifft nur noch fuer Betriebscode ausserhalb von `scripts/*.py`. (b) `/etc/claude-telegram-bot.env` in der Beispielreihe ist kein ortsabhaengiger Pfad, sondern der ueberall gleiche VPS-Geheimnispfad — er DARF nicht anschlagen. (c) Der Verweis 'zweite Haelfte in Zeile 512' ist gegenstandslos: die Dateimenge wurde heute geweitet (f5098f4, 5d2590d). WAS BLEIBT und der eigentliche Grund fuer `besteht_noch`: In den 18 Wurzelmodulen, in `*.sh` und in `*.json` sieht KEIN Waechter eine Mac-Form — und `differenz.py` ist der einzige der beiden, der diese Dateien ueberhaupt liest. Eine Weitung von `_ist_ortsabhaengig` um die fuenf Mac-Marker waere heute fehlalarmfrei: der AST-Weg haelt Kommentare und Docstrings ohnehin draussen, und im Bestand steht ausserhalb der Plists und `scripts/mac/` kein einziger Mac-Pfad in einer Zeichenkette.

**Beleg:**
```
$ cd .../mess && python3 -c "import sys; sys.path.insert(0,'scripts'); import differenz as d; [print(repr(w), d._ist_ortsabhaengig(w)) for w in ['/Users/jakuna/Projects/claude-telegram-bot','/private/tmp','/opt/homebrew/bin','/Library/Mobile Documents','/etc/claude-telegram-bot.env']]"
'/Users/jakuna/Projects/claude-telegram-bot' False
'/private/tmp' False
'/opt/homebrew/bin' False
'/Library/Mobile Documents' False
'/etc/claude-telegram-bot.env' False

$ sed -n '220,232p' scripts/test_zielumgebung.sh
for _d in $(git ls-files 'scripts/*.py' 2>/dev/null | grep -v '^scripts/mac/'); do
  if grep -vE '^[[:space:]]*#' "$_d" | grep -qE '["'"'"'](/private/tmp|/private/var|/Users/|/opt/homebrew|/Library/Mobile)'; then
$ git -C /home/user/claude-telegram-bot log --all --oneline -S'plattformgebundenen Pfad fest' -- scripts/test_zielumgebung.sh
cc9e773 Engywucks Deploy-Auflage: zwei Pruefer waren auf dem VPS tot   (29.08.2026 11:29)

GEGENPROBE (Mac-Pfad in ampel.py und scripts/log_sync.sh — beides VPS-Code):
$ bash scripts/test_zielumgebung.sh | grep -E 'plattformgebunden|== Ziel'
✓ kein Pruefer schreibt einen plattformgebundenen Pfad fest
== Zielumgebung: 24/24 bestanden ==
$ python3 -c "...d._feste_betriebspfade()"  ->  FUNDE: []

BESTAND (git ls-files, ohne *.md und docs/, Mac-Marker):
nur die 4 launchd-Plists, scripts/mac/*, .claude/hooks/session-start.sh ($HOME-gestuetzt) und Kommentarzeilen — kein aktiver Bruch.
```

**Widerleger (hält):** Ich habe vier Entkräftungswege gefahren, alle vier scheitern.

(1) IST DER ZWEIG ERREICHBAR? Ja, und er läuft auf beiden Maschinen. `bot.py:8213 _c_differenzen` lädt `scripts/differenz.py` per importlib und ist als Selbstcheck-Zeile „Differenzen (Mengen statt Aufzählungen)" eingehängt — laut eigenem Docstring bei jedem Bot-Start auf dem VPS, im Start-Wächter, im Regressionslauf und über den Tagescheck. Zweiter Aufrufer: `scripts/test_hermetik.py`. Ein Skript ohne Aufrufer ist es also nicht.

(2) IST ES LÄNGST REPARIERT? Nein. `df5dc69` (29.08., 19:17) ist der neueste Commit über ALLE Refs; letzte Änderungen an `differenz.py` waren `f5098f4`/`5d2590d`, an `test_zielumgebung.sh` `cc9e773`. Keine davon weitet die Himmelsrichtung.

(3) FÄNGT ES EIN ANDERER WÄCHTER? Nein. Repo-weite Suche nach den Mac-Markern in `*.py`/`*.sh`/`*.json` (ohne docs/, logs/) liefert genau EINE Wächter-Stelle: `scripts/test_zielumgebung.sh:225` — und deren Dateimenge ist `git ls-files 'scripts/*.py'`. Wurzelmodule, `*.sh` und `*.json` liegen außerhalb. Die Meldung trifft hier zu.

(4) DIE ENTSCHEIDENDE GEGENPROBE (drei Mac-Pfade in echten Betriebscode injiziert, `__pycache__` vorher gelöscht, Eingriff per gr

---

## [44] scripts/regressionstest.sh — STILL
**Maschine:** beide (jede Maschine ohne .venv)

Gemessen: keine einzige Zeile mit --version, sys.version, uname, hostname oder platform im ganzen Läufer; die Kopfzeile (134) nennt nur das Datum, die Schlusszeile (245) nur die Trefferquote. Der stille Rückfall auf System-python3 ist reproduziert. EINSCHRÄNKUNG, die die Meldung nicht nennt und die sie leicht abschwächt: Die Trägerfassungen WERDEN ermittelt — bot.py loggt beim Selbstcheck 'C2: Fassungen der Traeger auf DIESER Maschine — anyio 4.14.2, claude-agent-sdk 0.2.127, httpx 0.28.1, mcp 1.29.1'. Diese Zeile fällt aber in run() in /tmp/regress_last.log und wird NUR im Fehlerfall gezeigt. Die Angabe existiert also und ist genau dann unsichtbar, wenn der Lauf grün ist — was den Befund nicht widerlegt, sondern erklärt, warum er so lange unbemerkt blieb.

**Beleg:**
```
$ grep -nEi -- "--version|sys\.version|uname|hostname|platform|\$PY\"? -V" scripts/regressionstest.sh
->  (kein Treffer)
$ grep -n '^echo' scripts/regressionstest.sh
->  134:echo "== 8.2-Minimaltest ($(date '+%Y-%m-%d %H:%M')) =="
->  245:echo "== Ergebnis: $((GESAMT-FAILS))/$GESAMT bestanden =="
$ PY="python3"; [ -x .venv/bin/python3 ] && PY=.venv/bin/python3; echo $PY; $PY -c 'import sys,platform;print(sys.version, platform.node())'; ls -d .venv
->  PY=python3
->  3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0] vm
->  ls: cannot access '.venv': No such file or directory
(Gegenmessung zur Einschraenkung, aus dem Selbstcheck-Lauf oben:) 'INFO claude-tg-bot | C2: Fassungen der Traeger auf DIESER Maschine — anyio 4.14.2, claude-agent-sdk 0.2.127, httpx 0.28.1, mcp 1.29.1' — geht in run() nach /tmp/regress_last.log, sichtbar nur bei ❌.
```

**Widerleger (hält):** Ich habe versucht, den Fund zu kippen, und keinen tragfaehigen Weg gefunden — die staerkste Gegenmessung macht ihn sogar schaerfer.

**Der Kern, ausgefuehrt statt gelesen.** Ich habe `scripts/regressionstest.sh` im Klon vollstaendig durchlaufen lassen (Container ohne `.venv`, System-python3 3.11.15). Der Lauf ging bis zum Ende durch: 80 Zeilen sichtbare Ausgabe, Schlusszeile `== Ergebnis: 60/63 bestanden ==`. Ein Grep ueber die GESAMTE sichtbare Ausgabe nach `python3|sys.version|uname|hostname|platform|\.venv|Fassungen der Traeger` liefert **keinen Treffer**. Zwei Maschinen mit verschiedenem Interpreter und verschiedenen Traeger-Fassungen erzeugen also denselben Bericht. Kopfzeile 134 nennt nur das Datum, Schlusszeile 245 nur die Trefferquote — beide Zeilennummern stimmen im heutigen 246-Zeilen-Stand.

**Die Einschraenkung der Vorsitzung ist zu GROSSZUEGIG, nicht zu streng.** Sie sagt, die C2-Fassungszeile sei „nur im Fehlerfall" sichtbar. Gemessen: Die beiden C2-Zeilen gehen als Logging auf stderr und stehen als Zeile **2 und 3** in `/tmp/regress_last.log`; `run()` zeigt aber `tail -20`. In meinem Lauf war der Selbstcheck **rot** (`❌ Selbstcheck-Invarianten`) — und die C2-Fassungs

---

## [37] scripts/start_waechter.py — STILL
**Maschine:** VPS

Die Code-Stelle steht unveraendert da (heute Z. 235 statt 200) und `USER_PREFS_FILE` wird tatsaechlich ignoriert — gemessen: mit HOME=/tmp/mz/heim und USER_PREFS_FILE=/tmp/mz/anders/prefs.json kommt '4711' aus dem HOME-Pfad zurueck, nicht '9999' aus der Variablen. Auch STATE_DIR und POSTFACH folgen bei fehlenden Umgebungsvariablen dem HOME. ABER DREI TRAGENDE TEILE DER MELDUNG HALTEN NICHT STAND: (1) `_melde_ziel()` ist im Betrieb TOTER CODE. `melden()` (Z. 246-259) ruft `botenpost.legen(text, "waechter")` OHNE Ziel; die Aufloesung macht `botenpost.ziel_finden()`. Repoweit gibt es ausser der Definition keinen einzigen Aufruf — nur `scripts/test_start_waechter_b1.py` ruft sie. Der Fehler ist also eine Kopie ohne Wirkung; wirksam ist er allein in botenpost.py. (2) Die Kausalkette ueber daily_check.sh ist ERFUNDEN: `scripts/daily_check.sh` liest `startwaechter.json` NICHT — 0 Treffer, auch bei breitem Raster (waechter|updater|startw|.claude/upd|freeze). Repoweit liest die Datei NIEMAND; die einzigen Nennungen sind die schreibende Zeile selbst und zwei Doku-Behauptungen (MIGRATION.md:868, ABHAENGIGKEITEN.md:115), die den 4-Uhr-Check als Leser ausgeben. (3) Die Vorbedingung 'wenn der Waechter nicht als claudebot laeuft' tritt im einzigen Produktionsweg nicht ein: gestartet wird er ausschliesslich von `updater._waechter_scharf()` per Popen aus dem Bot-Prozess heraus, erbt also dessen HOME. DER ECHTE, GROESSERE RESTBEFUND ist damit nicht der falsche Heimpfad, sondern: der zweite Meldeweg hat gar keinen Empfaenger, und die Pruefzeile 'Bericht liegt auch fuer den 4-Uhr-Check bereit' (test_start_waechter_b1.py:150) bescheinigt gruen einen Verbraucher, den es nicht gibt. Das ist genau die stille Sorte — es sieht aus wie ein doppelt gesicherter Meldeweg und ist ein einfacher.

**Beleg:**
```
$ sed -n '235p' scripts/start_waechter.py
    prefs = Path.home() / ".config" / "claude-telegram-bot" / "prefs.json"

AUSGEFUEHRT (USER_PREFS_FILE zeigt auf 9999, HOME-prefs auf 4711):
$ env -u ALLOWED_USER_IDS HOME=/tmp/mz/heim USER_PREFS_FILE=/tmp/mz/anders/prefs.json python3 -c "import sys; sys.path.insert(0,'scripts'); import start_waechter as sw; print(repr(sw._melde_ziel())); print(sw.STATE_DIR); print(sw.POSTFACH)"
'4711'
/tmp/mz/heim/.claude/updater
/tmp/mz/heim/postfach/outbox
(-> USER_PREFS_FILE wirkungslos)

$ env -u ALLOWED_USER_IDS HOME=/tmp/mz/leer USER_PREFS_FILE=/tmp/mz/heim/.config/claude-telegram-bot/prefs.json python3 -c "..."
''
/tmp/mz/leer/.claude/updater
/tmp/mz/leer/postfach/outbox

(1) TOTER CODE:
$ grep -rn "_melde_ziel" --include=*.py .
./scripts/test_start_waechter_b1.py:375:def _melde_ziel_aus_einstellungen():
./scripts/test_start_waechter_b1.py:380:        assert w._melde_ziel() == "" or w._melde_ziel().isdigit(), \
./scripts/test_start_waechter_b1.py:385:                assert w._melde_ziel().isdigit(), \
./scripts/test_start_waechter_b1.py:393:check("Meldeziel notfalls aus der Einstellungsdatei", _melde_ziel_aus_einstellungen)
./scripts/start_waechter.py:223:def _melde_ziel() -> str:
(kein Aufruf in melden(); Z. 252: botenpost.legen(text, "waechter"))

(2) KEIN LESER:
$ grep -c "startwaechter" scripts/daily_check.sh
0
$ grep -nEi "waechter|updater|startw|\.claude/upd|freeze" scripts/daily_check.sh
(nur Kommentarzeilen 32, 64, 265, 373, 397, 435, 436, 627, 630 — keine Leseoperation)
$ grep -rn "startwaechter" .
./scripts/start_waechter.py:53:BERICHT = STATE_DIR / "startwaechter.json"
./scripts/start_waechter.py:57:LEBENSMARKE = STATE_DIR / "startwaechter.laeuft"
./scripts/start_waechter.py:151:    umgebung.setdefault("TELEGRAM_BOT_TOKEN", 
```

**Widerleger (hält):** Jede pruefbare Aussage der Meldung habe ich am Stand df5dc69 selbst gemessen, und alle halten. Die vier Widerlegungswege liefen ins Leere:

(a) **Erreichbarkeit** — der prefs-Zweig ist erreichbar, aber folgenlos: `_melde_ziel()` (Z. 223-243) hat ueber den Syntaxbaum gezaehlt **null** Produktions-Aufrufknoten. Ich habe die Funktion in einer Kopie **vollstaendig geloescht** und die vorher hingeschriebene Erwartung getroffen: exakt eine Zeile rot ("Meldeziel notfalls aus der Einstellungsdatei", AttributeError), die uebrigen **zwoelf gruen** — darunter alle, die `bewachen()`/`melden()` mit echter Postfach-Zustellung durchlaufen. Das ist Verhaltensbeweis fuer toten Code, nicht Textsuche.

(b) **Aufrufer** — `start_waechter.py` hat repoweit genau einen Produktions-Starter: `updater._waechter_scharf()` (updater.py:376-381, `Popen(..., start_new_session=True)` **ohne** `env=`, erbt also HOME des Bot-Prozesses). Keine `.service`, keine `.timer`, kein Cron, kein Aufruf in `guardian.sh`/`run.sh`/den plists. Die Vorbedingung des urspruenglichen Funds tritt damit tatsaechlich nicht ein.

(c) **Historie** — df5dc69 ist der juengste Commit ueberhaupt (HEAD des Arbeitsverzeichnisses, 76d3513, ist 

---

## [45] scripts/test_media_h1.py — STILL
**Maschine:** beide (Code identisch auf allen drei Maschinen); ausgeloest nur dort, wo ffmpeg/ffprobe fehlen — gemessen im Kontroll-Container, fuer Mac/VPS von hier nicht pruefbar

Die beschriebene Mechanik ist heute unveraendert vorhanden und gemessen: der Skip endet mit exit 0, `run()` in regressionstest.sh:122-131 zeigt stdout NUR im Fehlerzweig, also erscheint die ⚠-Zeile nie, der Laeufer druckt `✅ Medien-Transport H1 (Bild/Video)` und GESAMT waechst um eins — eine gruene Zeile, hinter der null Messungen stehen. Auch der zweite Teil traegt: der Register-Erwartungstext (ABHAENGIGKEITEN.md, heute Zeile 114, nicht 110) wird NIRGENDS verglichen; `Alle H1-Medientests bestanden` kommt im ganzen Baum nur an der Druckstelle selbst vor, und daily_check.sh:133 nimmt vom Regressionslauf ausschliesslich `tail -1`. WAS AN DER MELDUNG NICHT TRAEGT — und das ist der Grund fuer die Herabstufung: Die unterstellte Folge `Lauf ist gruen, niemand merkt es` ist falsch. Im SELBEN Lauf faellt die Selbstcheck-Zeile `_c_medien_transport` (bot.py:8145-8167) hart auf denselben Praedikat `media.tools_available()` und macht den Lauf rot, mit der Ursache woertlich im tail-20. Gemessen: `== Ergebnis: 60/63 bestanden ==`, nicht 63/63. Die Kopplung ist hart (identische Funktion, identischer Interpreter, identischer PATH) und laesst sich nicht umgehen: mit Attrappen-Binaries im PATH wird die Selbstcheck-Zeile gruen, dafuer stirbt der H1-Test laut. Es bleibt also kein Zustand uebrig, in dem beide gruen sind und nichts gemessen wurde. Der reale Restschaden ist die falsche Buchfuehrung — 63 gezaehlte Pruefungen, von denen eine nichts geprueft hat, plus ein Register-Kriterium ohne Vergleicher —, nicht eine unentdeckte fehlende Abhaengigkeit. Ungeschuetzt bliebe das erst, wenn jemand die Selbstcheck-Zeile entfernt; dann faellt die Tarnung sofort auf niemanden mehr.

**Beleg:**
```
$ cd <stand-aktuell-ro> && which ffmpeg ffprobe; echo which-exit=$?
(keine Ausgabe)
which-exit=1

$ timeout 900 bash scripts/regressionstest.sh 2>&1 | grep -E "Medien|Selbstcheck|Ergebnis|❌"
❌ Selbstcheck-Invarianten (run_self_check) — Log:
✗ Medien-Transport (H1): ffmpeg/ffprobe fehlen — große Bilder und alle Videos blieben liegen
✓ Medien-Eingangsschutz (5.2)
✅ Medien-Transport H1 (Bild/Video)
❌ Abgleich-Quittung (log_sync) — Log:
❌ Hermetik der Pruefläufe (L) — Log:
== Ergebnis: 60/63 bestanden ==

$ sed -n '122,131p' scripts/regressionstest.sh
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

$ grep -rn "Alle H1-Medientests bestanden" scripts/ *.py *.sh
scripts/test_media_h1.py:240:print("\nAlle H1-Medientests bestanden.")
(einziger Treffer = der Druck selbst; kein Vergleicher)

$ sed -n '131,138p' scripts/daily_check.sh
if reg="$(sudo -u claudebot bash "$BOTDIR/scripts/regressionstest.sh" 2>&1)"; then
  last="$(echo "$reg" | tail -1)"
  add "✅ Regressionstest: $last"

$ git -C /home/user/claude-telegram-bot log -S'H1-Test übersprungen' --oneline
19333d1 / 4be6cc7 / 025ef8b  (letzte Beruehrung 2026-07-26; die Skip-Stelle selbst unveraendert in df5dc69)
```

**Widerleger (hält):** Ich habe fuenf Widerlegungswege probiert; keiner traegt.

(1) ERREICHBARKEIT — reproduziert. `python3 scripts/test_media_h1.py` im Arbeitsstand: Ausgabe „⚠ ffmpeg/ffprobe fehlen — H1-Test uebersprungen (kein Fehlschlag)", `H1-exit=0`. Der Skip steht auf Modulebene (Zeile 36-38), VOR jeder Messung; nichts faengt ihn vorher ab.

(2) AUFRUFSTELLE — genau eine, und sie existiert: `scripts/regressionstest.sh:170`. `run()` (Zeile 122-131, Zeilennummern stimmen) leitet stdout nach /tmp/regress_last.log und zeigt es nur im `else`-Zweig. Eigener Volllauf gefahren: die ⚠-Zeile erscheint NICHT in der Ausgabe, stattdessen `✅ Medien-Transport H1 (Bild/Video)`, und `== Ergebnis: 60/63 bestanden ==` — die Zeile ist mitgezaehlt. Deckungsgleich mit dem Beleg der Vorsitzung.

(3) LAENGST REPARIERT? — nein. `scripts/test_media_h1.py` ist zwischen HEAD des Ursprungs-Repos und df5dc69 unveraendert; die Skip-Stelle steht woertlich da. Der Punkt ist ausserdem seit dem Entkernungs-Probelauf katalogisiert und NICHT abgearbeitet: `docs/entkernung-katalog.md:851ff` beschreibt exakt denselben Sachverhalt („zwoelf Pruefzeilen fallen still weg und zaehlen als bestanden").

(4) MASCHINEN-ANNAHME — kein Hebel. De

---

## [19] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Die Meldung traegt — und ich habe sie sogar UNTERSCHAETZT gefunden. Alle drei Schleifen (bash -n Z.29, $HOME-Suche Z.42, env-i-Start Z.77) sehen nur `scripts/*.sh`. Ausserhalb liegen SIEBEN Skripte mit `set -u`: guardian.sh, run.sh, .claude/hooks/{durchlauf-wache,guard-master-files,session-start}.sh, scripts/mac/{icloud_backup,icloud_spiegel}.sh. Fuenf davon fuehren $HOME. Der staerkste Beleg ist nicht guardian.sh, sondern `.claude/hooks/session-start.sh`: vier BARE $HOME (Z.26,28,45,47) unter `set -uo pipefail` — exakt das Muster des 21-Tage-Vorfalls — und ein Start mit leerer Umgebung stirbt dort messbar. Kein `bash -n` im ganzen Repo ausser dem in dieser Datei; guardian.sh und run.sh bekommen also NIRGENDS eine Syntaxpruefung. Heute ist alles syntaktisch heil, es bricht also gerade nichts — genau das ist die stille Sorte: die Luecke faellt erst auf, wenn jemand eine dieser sieben Dateien anfasst.

**Beleg:**
```
$ ls scripts/*.sh | wc -l  →  10 (davon 9 geprueft, test_zielumgebung.sh selbst uebersprungen)
$ find . -name '*.sh' -not -path './.git/*' | sort  →  zusaetzlich: ./.claude/hooks/durchlauf-wache.sh ./.claude/hooks/guard-master-files.sh ./.claude/hooks/session-start.sh ./guardian.sh ./run.sh ./scripts/mac/icloud_backup.sh ./scripts/mac/icloud_spiegel.sh
$ grep -rn 'bash -n' --include='*.sh' --include='*.py' .  →  nur scripts/test_zielumgebung.sh:31 (plus Kommentar Z.13) und regressionstest.sh:205 als Aufrufer. Kein zweiter Syntaxpruefer im Repo.
$ for f in guardian.sh run.sh .claude/hooks/*.sh scripts/mac/*.sh; do ... done  →
  guardian.sh                       set-u=1 bareHOME=4 bash-n=OK
  run.sh                            set-u=1 bareHOME=0 bash-n=OK
  .claude/hooks/durchlauf-wache.sh  set-u=1 bareHOME=0 bash-n=OK
  .claude/hooks/guard-master-files.sh set-u=1 bareHOME=0 bash-n=OK
  .claude/hooks/session-start.sh    set-u=1 bareHOME=4 bash-n=OK
  scripts/mac/icloud_backup.sh      set-u=1 bareHOME=4 bash-n=OK
  scripts/mac/icloud_spiegel.sh     set-u=1 bareHOME=3 bash-n=OK
$ env -i /bin/bash .claude/hooks/session-start.sh  →  ".claude/hooks/session-start.sh: line 26: HOME: unbound variable"
$ env -i /bin/bash guardian.sh  →  "guardian.sh: line 14: HOME: unbound variable"
$ git -C /home/user/claude-telegram-bot log -S"for f in scripts/*.sh" --oneline  →  059fa3c (Urfassung), seither unveraendert; df5dc69==76d3513 fuer diese Datei.
```

**Widerleger (hält):** Der Kern haelt: Alle drei Schleifen von scripts/test_zielumgebung.sh sehen ausschliesslich `scripts/*.sh` (Z.29, Z.42, und Z.77 sogar nur zwei fest genannte Dateien). Der Lauf belegt es selbst — 9 Syntaxzeilen, 7 HOME-Zeilen, 2 env-i-Starts, 24/24 gruen. Ausserhalb dieses Glob liegen sieben .sh-Dateien, und einen zweiten Syntaxpruefer gibt es im Repo nicht (grep ueber *.sh/*.py/*.md: `bash -n` nur in dieser Datei und als Aufrufer in regressionstest.sh:205). CLAUDE.md:1309 behauptet dagegen, der Pruefer fahre `bash -n` "ueber jedes Skript" — das ist eine Falschaussage in der Ablage.

ZWEI KORREKTUREN an der Meldung (beide gemessen, beide entkraeften sie nicht):

(1) Es sind SECHS ohne Syntaxpruefung, nicht sieben. `.claude/hooks/guard-master-files.sh` wird von scripts/test_governance_hook.py per subprocess AUSGEFUEHRT. Gegenprobe gefahren (Eingriff vorher verifiziert, erwartete Zeile vorher notiert): Syntaxfehler an Z.7 eingesetzt → `bash -n` rc=2, Direktlauf rc=2, Pruefer rc=1, alle 16 Zeilen rot. Ein Anhaengen am Dateiende dagegen bleibt gruen, weil das Skript vorher `exit 0` erreicht — die erste, schlechter konstruierte Gegenprobe. De facto ist diese eine Datei also gedeckt.

(2)

---

## [25] scripts/test_zielumgebung.sh — STILL
**Maschine:** VPS

Traegt vollstaendig, und die Kettenwirkung ist jetzt GEMESSEN statt vermutet. Zeile 135 ist die einzige Stelle im ganzen Repo mit einer festen Python-Fassung im Pfad (repo-weiter grep: 1 Treffer); bot.py:4436 loest denselben Pfad korrekt ueber `Path(_sdk.__file__).parent` auf. Faellt der Pfad weg, wirft `os.execv` im Kindprozess, der Text landet im Pseudo-Terminal, `auslesen()` liefert `{}` und beendet mit 0 — das `2>/dev/null || true` ist dafuer nicht einmal noetig. Der Pruefer meldet dann rot mit der falschen Ursache: er beschuldigt das /usage-Layout der Oberflaeche, waehrend in Wahrheit der Interpreter gewechselt hat. Symptom laut, Ursache still — und die Divergenz selbst ist auf Mac und Kontroll-Container gar nicht sichtbar, weil `[ -d /home/claudebot/... ]` den Block dort wortlos ausschaltet. Einzige Einschraenkung: ob die VPS-venv HEUTE noch python3.13 traegt, kann ich von hier nicht messen; das aendert am Konstruktionsfehler nichts.

**Beleg:**
```
$ grep -rn 'site-packages' --include='*.py' --include='*.sh' --include='*.md' --include='*.toml' . | grep -v '^./docs'  →  ./scripts/test_zielumgebung.sh:135 (EIN Treffer)
$ grep -rn 'python3\.1[0-9]' --include='*.py' --include='*.sh' .  →  ./scripts/test_zielumgebung.sh:135 (EIN Treffer)
$ grep -n '_bundled' bot.py  →  4436: p = Path(_sdk.__file__).parent / "_bundled" / "claude"   (korrekte Aufloesung)
KETTENWIRKUNG GEMESSEN — Pfad kuenstlich weggenommen:
$ KONTINGENT_HOME=/tmp/kq-heim KONTINGENT_FRIST=4 python3 kontingent_sitzung.py /tmp/gibt-es-nicht/python3.14/claude
  {}
  rc=0
→ `_kout="{}"`, `grep -q anteil` scheitert, Zweig Z.140 feuert: "kein Wert gelesen - hat sich das Layout von /usage geaendert?" — die FALSCHE Ursache.
$ git -C /home/user/claude-telegram-bot log -S'python3.13' --oneline -- scripts/test_zielumgebung.sh  →  1199ac8 (Einfuehrung), keine Reparatur seither.
```

**Widerleger (hält):** Ich habe vier Entkraeftungswege gefahren, keiner traegt.

(1) ERREICHBARKEIT: Der Zweig ist erreichbar. `scripts/updater.py:268` setzt `umgebung = {**os.environ, "KONTINGENT_LIVE": "1"}` und startet damit `bash scripts/regressionstest.sh` (Z. 269). Dessen `run()` (Z. 122-132) fuehrt `"$@"` direkt aus, ohne `env -i` und ohne Scrubbing — die Variable erbt sich also bis in Z. 205 `run "Zielumgebung ..." bash scripts/test_zielumgebung.sh`. Nichts faengt den Zweig vorher ab.

(2) AUFRUFSTELLEN: Genau eine echte, und sie ist die richtige Maschine. `[ -d "$_bot" ]` (Z. 133) mit `_bot=/home/claudebot/claude-telegram-bot` schaltet den Block auf Mac und Kontroll-Container wortlos aus — die Maschinen-Zuordnung "VPS" der Meldung stimmt.

(3) HISTORIE: Nicht repariert. `git log -S'python3.13' -- scripts/test_zielumgebung.sh` liefert nur `1199ac8` (Einfuehrung). Zeile 135 steht wortgleich in der Arbeitskopie `df5dc69` UND im heutigen HEAD `76d3513` (`git show HEAD:scripts/test_zielumgebung.sh`). Die Zeilennummer ist in beiden Staenden dieselbe.

(4) FAENGT EIN ANDERER PRUEFER ES? Nein — und beide moeglichen Faenger sind bauartbedingt blind:
  - `scripts/differenz.py` (der Fest-Pfad-Melder) traeg

---

## [33] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Der Kern traegt und ist am echten Projektbestand nachgemessen: `${VAR:-$HOME/x}` bricht unter `set -u` bei fehlendem HOME genauso wie ein bares $HOME — der zeilenweise Filter `grep -v ':-'` wirft aber genau diese Zeilen weg. Alle acht genannten Zeilen (log_sync.sh:22,23,79 · vps_backup.sh:16,18,61 · icloud_spiegel.sh:32,33,34) verschwinden nach dem Filter restlos, und der Waechter meldet gruen. GEGENGEPRUEFT und einzuschraenken ist die zweite Haelfte der Meldung: das behauptete Bruch-Szenario (systemd ohne `User=`) trifft KEINE der acht Zeilen heute an. log_sync.sh laeuft laut eigenem Kopf unter `claude-log-sync.timer` mit `User=claudebot` (systemd setzt dann HOME), vps_backup.sh und icloud_spiegel.sh laufen ueber launchd bzw. den Sitzungsstart-Hook auf dem Mac, wo HOME steht. Der Bruch ist also die BLINDHEIT des Waechters, nicht ein heute brennender Ausfall — er kann eine kuenftige Unit ohne `User=` nicht mehr melden, und das sieht bis dahin wie Ruhe aus.

**Beleg:**
```
$ env -i /bin/bash -c 'set -u; SRC="${LOG_SYNC_SRC:-$HOME/claude-telegram-bot/logs/conversations}"; echo OK'
  /bin/bash: line 1: HOME: unbound variable      (rc=127)
→ das `:-` schuetzt NUR die Variable, nicht das $HOME im Rueckfallwert.
FILTER GEGEN DEN ECHTEN BESTAND (Rohmuster / nach Filter):
  scripts/log_sync.sh          3 Treffer (Z.22,23,79)  →  0
  scripts/vps_backup.sh        3 Treffer (Z.16,18,61)  →  0
  scripts/mac/icloud_spiegel.sh 3 Treffer (Z.32,33,34) →  0
$ env -i /bin/bash scripts/mac/icloud_spiegel.sh  →  "scripts/mac/icloud_spiegel.sh: line 32: HOME: unbound variable"
  (Z.32 ist die Form "${ICLOUD_SPIEGEL_QUELLE:-$HOME/Library/...}" — echter Bruch, vom Filter unsichtbar gemacht.)
$ bash scripts/test_zielumgebung.sh | grep 'ungeschuetztes'  →  u.a. "✓ kein ungeschuetztes $HOME: log_sync.sh", "✓ kein ungeschuetztes $HOME: vps_backup.sh"
EINSCHRAENKUNG, belegt: scripts/log_sync.sh Z.14 Kopfkommentar: "Laeuft STUENDLICH als systemd-Timer `claude-log-sync.timer` (User claudebot)" — mit `User=` setzt systemd HOME.
```

**Widerleger (hält):** Ich habe die Meldung mit allen vier vorgeschlagenen Widerlegungswegen angegriffen und keinen tragfaehig bekommen.

**(1) Ist der Zweig erreichbar? Ja — und zwar gemessen, nicht gelesen.** `${VAR:-$HOME/x}` bricht unter `set -u` ohne HOME (rc=127). Der Filter der Pruefzeile ist `grep -v ':-'` und arbeitet ZEILENWEISE, nicht am Rueckfallwert: Er wirft jede Zeile weg, die irgendwo ein `:-` traegt — also genau die Form `${VAR:-$HOME/…}`. Am echten Bestand: log_sync.sh (Z.22,23,79) und vps_backup.sh (Z.16,18,61) haben je 3 Rohtreffer, nach dem Filter 0. Beide Skripte tragen `set -uo pipefail`, werden also von der Zeile geprueft — und beide werden gruen gemeldet.

**(2) Gegenprobe in beide Richtungen, Erwartung vorher hingeschrieben.** Bares `$HOME` eingefuegt → ROT, praezise, 23/24. Die Rueckfall-Form `${IRGENDWAS:-$HOME/x}` in dasselbe Skript eingefuegt → GRUEN, 24/24 — obwohl dieselbe Zeile mit `env -i` nachweislich mit `HOME: unbound variable` stirbt. Das ist der Verhaltensbeweis der Blindheit, nicht eine Textlesung.

**(3) Laengst repariert? Nein.** `git diff df5dc69 HEAD -- scripts/test_zielumgebung.sh scripts/log_sync.sh scripts/vps_backup.sh scripts/mac/icloud_spiegel.sh` ist LEE

---

## [47] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Traegt woertlich und ist durch den Lauf belegt. `melde ok` erhoeht GESAMT (Z.24) und laesst FAILS unberuehrt; die Schlusszeile rechnet `$((GESAMT-FAILS))/$GESAMT`, der angesagte Uebersprung geht damit als BESTANDEN in die Bilanz ein. Der Selbstwiderspruch steht drei Zeilen darueber im eigenen Kommentar (Z.106-108): "ein uebersprungener Pruefer, der wie ein bestandener aussieht, ist schlimmer als keiner". Genau das tut die Zeile. Das ist die stille Sorte in Reinform: Auf Mac und Kontroll-Container — dem ueblichen Entwicklungsweg — laeuft die Gegenrichtung nie, und ein Tagescheck, der gar nichts mehr ablegt, wuerde dort trotzdem eine gruene Vollzahl liefern.

**Beleg:**
```
$ bash scripts/test_zielumgebung.sh (Kontroll-Container, kein /home/claudebot)
  ...
  ✓ Normalfall-Vermerk: uebersprungen (nicht die Zielumgebung)
  ...
  == Zielumgebung: 24/24 bestanden ==
  EXIT=0
→ 24 von 24, obwohl die Normalfall-Pruefung nicht stattfand.
Code: Z.23-26 `melde() { GESAMT=$((GESAMT+1)); if [ "$1" = "ok" ]; then echo "✓ $2"; else ...; FAILS=$((FAILS+1)); fi }`
Z.123 `melde ok "Normalfall-Vermerk: uebersprungen (nicht die Zielumgebung)"`
Z.236 `echo "== Zielumgebung: $((GESAMT-FAILS))/$GESAMT bestanden =="`
$ git -C /home/user/claude-telegram-bot log -S'Normalfall-Vermerk' --oneline  →  b7e6778 (Einfuehrung), keine Reparatur seither; Datei zwischen df5dc69 und HEAD 76d3513 unveraendert.
```

**Widerleger (hält):** Ich habe alle vier Entkraeftungswege abgeklopft; keiner traegt.

(1) ERREICHBARKEIT: Der Zweig wird genommen, nicht abgefangen. Bedingung Z.110 ist `[ -d "$_bot" ] && [ -x "$_bot/.venv/bin/python3" ]`. Im Kontroll-Container existiert `/home/claudebot/claude-telegram-bot` sogar (Detail-Abweichung zum Beleg der Vorsitzung, die "kein /home/claudebot" schrieb) — aber `.venv/bin/python3` fehlt, also greift der else-Zweig Z.122-124.

(2) AUFRUFER: Es gibt genau einen echten, `scripts/regressionstest.sh:205`. Der entlastet nicht, er verschaerft: `run()` (Z.122-132) wertet ausschliesslich den Exit-Code aus, und der ist `exit $FAILS` — durch `melde ok` unberuehrt. Damit unterscheidet WEDER die Schlusszahl NOCH der Exit-Code zwischen "gemessen" und "uebersprungen". Zusatzbefund: Beide Zweige rufen `melde` genau einmal, GESAMT ist auf VPS und Mac identisch 24 — es entsteht also nicht einmal eine Zahlendifferenz, an der jemand stutzen koennte.

(3) HISTORIE: Nicht repariert. `git diff df5dc69 76d3513 -- scripts/test_zielumgebung.sh` ist leer; die HEAD-Fassung zeigt Z.123 woertlich unveraendert. Eingefuehrt in b7e6778, danach zweimal angefasst (1199ac8, cc9e773) ohne diese Zeile.

(4) MASCHINEN

---

## [62] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Die damalige Messung ist auf dem heutigen Stand reproduzierbar — nur die Zahl hat sich geaendert (heute 24/24 statt 21/21, weil inzwischen Pruefzeilen dazugekommen sind; die Sache ist unveraendert). Der Uebersprung geht ueber `melde ok` als bestanden in die Bilanz; die Gegenrichtung "ohne Schalter muss der Vermerk wirklich entstehen" (Z.113-120) laeuft ausserhalb des VPS nie. Damit gilt die Folgerung der Meldung: Ein Regressionslauf am Mac — der uebliche Entwicklungsweg — kann einen Tagescheck, der nichts mehr ablegt, nicht bemerken; er meldet trotzdem eine gruene Vollzahl. Das ist genau die Konstellation des 21-Tage-Vorfalls, gegen den diese Datei gebaut wurde: die Wache stirbt, und ihr Tod sieht aus wie ein bestandener Lauf.

**Beleg:**
```
$ bash scripts/test_zielumgebung.sh 2>&1 | tail -3
  ✓ Abgleich quittiert Mitgenommenes und Ausgeschlossenes
  ✓ kein Pruefer schreibt einen plattformgebundenen Pfad fest
  == Zielumgebung: 24/24 bestanden ==
$ bash scripts/test_zielumgebung.sh 2>&1 | grep Normalfall
  ✓ Normalfall-Vermerk: uebersprungen (nicht die Zielumgebung)
$ ls -d /home/claudebot/claude-telegram-bot 2>&1  →  existiert hier nicht, also greift der else-Zweig Z.122-124.
Code Z.109-124 unveraendert seit b7e6778; `git diff df5dc69 76d3513 -- scripts/test_zielumgebung.sh` ist leer.
Die Zeilen 113-120 (die Gegenrichtung) wurden bei diesem Lauf NICHT ausgefuehrt — keine Ausgabe, kein Vermerk in der Bilanz ausser dem gruenen Uebersprung.
```

**Widerleger (hält):** Ich habe vier Entkraeftungswege probiert; keiner traegt.

(1) ERREICHBARKEIT — bestaetigt statt widerlegt. Das Tor ist `if [ -d "$_bot" ] && [ -x "$_bot/.venv/bin/python3" ]` (Z.109/110) auf den festen Pfad /home/claudebot/claude-telegram-bot. Der existiert hier nicht, also greift der else-Zweig Z.122-124. Selbst gefahren: die Gegenrichtung Z.113-120 erzeugt keine Ausgabe, stattdessen erscheint Z.123.

(2) BILANZ — der Kern des Funds, am Code nachgemessen. `melde()` (Z.23-26) kennt nur zwei Zustaende: jeder Aufruf erhoeht GESAMT, `ok` druckt ✓ und laesst FAILS unberuehrt. Es gibt keinen dritten Zustand "uebersprungen". Der Uebersprung geht damit als bestanden in die Schlusszahl. Die Datei widerspricht an dieser Stelle ihrem eigenen Kommentar sechs Zeilen darueber: "ein uebersprungener Pruefer, der wie ein bestandener aussieht, ist schlimmer als keiner." Erfuellt ist nur die halbe Auflage — die ZEILE sagt es, die BILANZ nicht.

(3) DIE SCHAERFSTE FASSUNG, die die Vorsitzung noch nicht gezogen hat: Weil der Uebersprung mitzaehlt, liefern VPS und Mac DIESELBE Zahl. Abschnitt 1 und 2 laufen ueber dieselbe Menge `scripts/*.sh`, Abschnitt 3 ueber dieselben zwei Skripte — auf beiden Masch

---

## [63] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Der Kern traegt, EINE Teilbehauptung muss ich aber zurueckweisen. Falsch ist die Annahme im Kopf, der Fall werde nirgends gefahren: scripts/updater.py:268 setzt KONTINGENT_LIVE=1 und ruft den Regressionstest — auf dem VPS nach jedem Update laeuft der Block also wirklich. Richtig und unrepariert ist alles uebrige: Bei Nichtausfuehrung erhoeht der Block GESAMT nicht, er verschwindet spurlos — anders als 3c, das wenigstens eine (falsch gruene) Zeile hinterlaesst. Damit bedeutet "N/N bestanden" auf verschiedenen Maschinen verschiedene Pruefmengen, ohne dass die Zahl das verraet. Bestaetigt sind auch die beiden Nebenbefunde: kein `scripts/test_*.py` importiert kontingent_sitzung direkt, und `auslesen()` wird von keinem Test ausgefuehrt (test_kontingent_a2.py ersetzt `bot._kontingent_frisch_messen` durch eine Attrappe); `scripts/kontingent.py` hat ueberhaupt keinen Pruefer. Und python3.13 steht weiterhin fest verdrahtet.

**Beleg:**
```
ZURUECKGEWIESEN — der Block IST erreichbar:
$ sed -n '259,270p' scripts/updater.py  →  "umgebung = {**os.environ, \"KONTINGENT_LIVE\": \"1\"}" ... subprocess.run(["bash", str(REGRESSION)], ..., env=umgebung)
BESTAETIGT — spurloses Verschwinden:
$ sed -n '133,143p' scripts/test_zielumgebung.sh  →  `melde` wird nur INNERHALB des if gerufen; kein else. Lauf hier: 24 Pruefungen, auf dem VPS mit LIVE waeren es 25 — die Schlusszeile sagt beide Male "N/N bestanden".
BESTAETIGT — kein Pruefer:
$ grep -ln 'kontingent_sitzung' scripts/test_*.py  →  (keiner)
$ grep -rn 'auslesen(' scripts/*.py bot.py  →  (kein Treffer; bot.py:4469 uebergibt nur die Referenz an asyncio.to_thread)
$ grep -n '_kontingent_frisch_messen' scripts/test_kontingent_a2.py  →  251/271/331/354: echt_messen gesichert, durch Attrappe ersetzt — auslesen() laeuft nie.
$ grep -rn 'kontingent' scripts/regressionstest.sh  →  nur test_kontingent_a2.py (Z.190); scripts/kontingent.py wird von keinem Skript und keinem Test gerufen.
BESTAETIGT — feste Fassung:
$ grep -rn 'python3\.1[0-9]' --include='*.py' --include='*.sh' .  →  ein Treffer, scripts/test_zielumgebung.sh:135
```

**Widerleger (hält):** Ich habe keinen Weg gefunden, den Fund zu entkraeften — im Gegenteil, die eigene Messung verschaerft ihn. (1) Erreichbarkeit: updater.py:268 setzt KONTINGENT_LIVE=1 und faehrt regressionstest.sh, das den Pruefer in Zeile 205 startet; updater.py selbst wird von wartungsfenster.py:142 und bot.py:5431 (_load_updater) gerufen. Der Zweig ist also auf dem VPS real, nichts faengt ihn vorher ab. (2) Spurloses Verschwinden ausgefuehrt gemessen: ohne Schalter 24 Pruefungen, mit Schalter 25 — der uebersprungene Block hinterlaesst KEINE Zeile, waehrend der Nachbarblock 3c in seinem else ausdruecklich `melde ok "... uebersprungen"` ruft. Die Inkonsistenz steht im selben Skript, dessen eigener Kopfkommentar verlangt, ein Ueberspringen werde GESAGT statt still getan. (3) Zusatzbefund, den die Vorsitzung nicht hatte: Die 3d-Schranke prueft nur `[ -d "$_bot" ]`, ihr fehlt das `[ -x "$_bot/.venv/bin/python3" ]` aus 3c — in diesem Kontroll-Container (Verzeichnis da, venv fehlt) wird der Block mit LIVE ROT und meldet die FALSCHE Ursache ("hat sich das Layout von /usage geaendert?") statt "kein Interpreter an diesem Pfad". Genau dieselbe Fehldiagnose erzeugt die fest verdrahtete python3.13-Zeile nach e

---

## [64] scripts/test_zielumgebung.sh — STILL
**Maschine:** beide

Beide Teillucken sind heute vorhanden und beide sind ausgefuehrt nachgemessen. (a) Die Dateimenge `scripts/*.sh` ist weder rekursiv noch auf die Repo-Wurzel ausgedehnt; sieben Skripte mit `set -u` bleiben draussen, darunter guardian.sh mit vier baren $HOME und — von der Meldung nicht genannt und schwerwiegender — .claude/hooks/session-start.sh mit ebenfalls vier baren $HOME. Beide sterben unter `env -i` messbar an genau dem Fehler, gegen den dieser Pruefer gebaut wurde. (b) Der Filter `grep -v ':-'` verwirft die ganze Zeile; fuer icloud_spiegel.sh bleiben von drei Rohtreffern null uebrig, und die Zeile 32 bricht unter fehlendem HOME trotzdem. Zu praezisieren ist nur die Reichweite von (b): die acht betroffenen Produktivzeilen laufen heute alle in Kontexten mit gesetztem HOME (systemd `User=claudebot`, launchd, Sitzungsstart-Hook) — der Bruch ist die Blindheit des Waechters fuer die kuenftige Unit, nicht ein heute brennender Ausfall.

**Beleg:**
```
(a) $ ls scripts/*.sh  →  10 Dateien, alle flach; kein scripts/mac/, kein guardian.sh, kein run.sh, keine Hooks.
$ grep -c guardian scripts/test_zielumgebung.sh scripts/regressionstest.sh  →  0 und 0
$ env -i /bin/bash guardian.sh  →  "guardian.sh: line 14: HOME: unbound variable"
$ env -i /bin/bash .claude/hooks/session-start.sh  →  ".claude/hooks/session-start.sh: line 26: HOME: unbound variable"
$ grep -nE '\$HOME([^A-Za-z_]|$)' .claude/hooks/session-start.sh  →  26,28,45,47 (alle bar, `set -uo pipefail` in Z.5)
(b) $ grep -nE '\$HOME([^A-Za-z_]|$)|\$\{HOME\}' scripts/mac/icloud_spiegel.sh  →  32,33,34 (alle "${VAR:-$HOME/...}")
$ ... | grep -v ':-' | grep -vE '^[0-9]+:[[:space:]]*#'  →  (leer)
$ env -i /bin/bash -c 'set -u; Q="${ICLOUD_SPIEGEL_QUELLE:-$HOME/Library/X}"'  →  "HOME: unbound variable", rc=127
$ env -i /bin/bash scripts/mac/icloud_spiegel.sh  →  "line 32: HOME: unbound variable"
$ bash scripts/test_zielumgebung.sh | grep 'ungeschuetztes'  →  sieben gruene Zeilen, darunter log_sync.sh und vps_backup.sh (je 3 Rohtreffer, alle vom Filter geschluckt).
```

**Widerleger (hält):** Ich habe vier Widerlegungswege probiert; keiner traegt.

**(a) Dateimenge — bestaetigt.** Abschnitt 1 und 2 laufen ueber `for f in scripts/*.sh`. Das ist flach und endet an der Ordnergrenze. Draussen bleiben genau sieben Skripte mit aktiviertem `-u`: `guardian.sh`, `run.sh`, `.claude/hooks/{durchlauf-wache,guard-master-files,session-start}.sh`, `scripts/mac/{icloud_backup,icloud_spiegel}.sh`. Vier davon tragen bare `$HOME` und sterben unter `env -i` ausgefuehrt: guardian.sh (Z.14), session-start.sh (Z.26), icloud_backup.sh (Z.47), icloud_spiegel.sh (Z.32).

**Eine Praezisierung, die die Meldung UNTERSCHAETZT:** `guardian.sh` und `run.sh` tragen `set -euo pipefail`, nicht die Zeichenkette `set -u`. Das Tor des Pruefers ist aber `grep -q 'set -u'` — guardian.sh fiele also **auch bei rekursiver Menge noch durch**. Es sind zwei Defekte, nicht einer.

**(b) Filter — bestaetigt und breiter als gemeldet.** Gemessen: `env -i bash -c 'set -u; Q="${FOO:-$HOME/x}"'` → `HOME: unbound variable`, rc=127. Nur `${HOME:-…}` ist geschuetzt; `${ANDERE:-$HOME/…}` ist ein bares $HOME. `grep -v ':-'` verwirft aber die ganze Zeile. Ergebnis: **drei** Skripte INNERHALB von scripts/ bekommen eine gruene Ze

---

## [27] requirements.txt — STILL
**Maschine:** beide

Die tragende Haelfte besteht: 6 von 7 Anforderungszeilen sind offene Untergrenzen OHNE Obergrenze, ein Wiederaufbau zieht auf Mac/VPS/Container Verschiedenes — und das ist nicht theoretisch, sondern gemessen (python-telegram-bot Mac 22.7 vs VPS 22.8, docs/auftraege/BEFUND-maschinen-gleichstand-messung.md:21). ABER zwei Teile der Meldung tragen NICHT: (1) Das Zitat 'Fundament-Pinning ... Schutz vor stillen Breaking Changes' steht so nirgends — der Kopf in requirements.txt:1 sagt 'Fundament-Pinning (Rotes-Team-Bericht B.1): Das SDK buendelt die Claude-Code-CLI', die Formel 'Schutz vor stillen Breaking Changes' steht in ABHAENGIGKEITEN.md:33; BEIDE Stellen nennen ausdruecklich nur claude-agent-sdk==0.2.127. Der Kopf verspricht also gar kein Pinning aller sieben Zeilen — das 'gebrochene Versprechen' ist in die Meldung hineingelesen. (2) 'Der Unterschied wird von keinem Pruefer benannt, weil C2 per Bauart nur ==-Zeilen kennt' ist seit Commit 8ab92e4 (29.08., Vorfahr von df5dc69) FALSCH: C2 bildet in bot.py:8098-8112 eine MENGE aller Zeilen ohne '==' und protokolliert sie namentlich. Was bleibt und der eigentliche Befund ist: diese Zeile ist ein log.info, KEIN assert (gemessen: 0 asserts im Block), sie laeuft nur auf DER Maschine, auf der sie laeuft, und der eigentliche Gleichstands-Pruefer ist im Kommentar selbst auf 'zuletzt gebaut' vertagt.

**Beleg:**
```
$ cd .../stand-aktuell-ro && grep -c '==' requirements.txt  ->  1
$ python3 -c "import re;t=open('requirements.txt').read();print(dict(re.findall(r'^([A-Za-z0-9_.\\-]+)(?:\\[[^\\]]*\\])?==([^\\s#]+)',t,re.M)))"  ->  {'claude-agent-sdk': '0.2.127'}
$ (gleiche Mengenbildung wie C2 (b))  ->  UNGEPINNT: ['python-telegram-bot','python-dotenv','edge-tts','pymupdf','faster-whisper','caldav'] 6
$ grep -n 'log.info("C2: ohne feste Fassung' bot.py  ->  8110:                log.info("C2: ohne feste Fassung angefordert (driftet zwischen "
$ awk '/_ungepinnt = \[\]/,/^        except Exception:/' bot.py | grep -c assert  ->  0
$ sed -n '1p' requirements.txt  ->  '# Fundament-Pinning (Rotes-Team-Bericht B.1): Das SDK buendelt die Claude-Code-CLI'
$ grep -n 'Breaking Change' ABHAENGIGKEITEN.md  ->  33: | **Fundament-Pinning** `requirements.txt` (`claude-agent-sdk==0.2.127` buendelt CLI 2.1.219) | Schutz vor stillen Breaking Changes ...
$ git -C /home/user/claude-telegram-bot log -S'ohne feste Fassung angefordert' --oneline --all  ->  8ab92e4 C2 erweitert ...  ; git merge-base --is-ancestor 8ab92e4 df5dc69 -> JA
$ grep -n 'python-telegram-bot' docs/auftraege/BEFUND-maschinen-gleichstand-messung.md  ->  21:| `python-telegram-bot` | 22.7 | **22.8** |
```

**Widerleger (hält):** Die tragende Haelfte haelt meiner eigenen Messung stand; ich habe keinen Weg gefunden, sie zu entkraeften — und die Entkraeftungsversuche, die ich gefahren habe, haben sie eher gehaertet.

GEMESSEN, NICHT UEBERNOMMEN (alles in stand-aktuell-ro = df5dc69):

1. 6 von 7 offen — bestaetigt durch Ausfuehrung der C2-Mengenbildung, nicht durch Lesen: ['python-telegram-bot','python-dotenv','edge-tts','pymupdf','faster-whisper','caldav']. Genau eine ==-Zeile (claude-agent-sdk==0.2.127).

2. Der strukturelle Grund, warum kein Pruefer die 6 haelt: Der einzige assert in C2 (bot.py:8036-8052) laeuft ueber `for name, pinned in pins.items()`, und `pins` entsteht aus der ==-Regex. Die 6 liegen per Bauart AUSSERHALB des asserts. Der (b)-Block darunter hat 0 asserts; ich habe seinen Code ausgefuehrt — er kehrt nach einem log.info mit None zurueck.

3. Nicht repariert: requirements.txt zuletzt in 2c516dc geaendert, seither unveraendert. 8ab92e4 ist bestaetigt Vorfahr von df5dc69 — die Selbstkorrektur der meldenden Sitzung (C2 benennt sie sehr wohl) trifft also zu.

4. Der Gleichstands-Pruefer existiert wirklich nicht: differenz.py fuehrt genau vier Differenzarten (kostenzuweisung, module, ablagen, fe

---

## [28] docs/node-major-befehlsblock.md — STILL
**Maschine:** VPS

Der Kern besteht: Zeile 13 sagt woertlich unveraendert '**Die Claude-CLI laeuft auf Node.**' und begruendet damit die Risikolage, waehrend docs/auftraege/ZETTEL-node-22-auf-24.md:21-28 am 29.08. auf dem VPS das Gegenteil MISST (ELF-Binaerdatei, nur libc/libpthread/libdl/librt, laeuft mit `env -i PATH=<ohne node>`). Zeile 5 traegt weiterhin 'Ueberholt durch: —', Zeile 71 misst nach dem Sprung weiterhin nur `node --version && npm ls -g --depth=0`, und die doppelte Installation kommt in der Datei GAR NICHT vor (grep auf node_modules|md5|_bundled|doppelt = 0 Treffer). Die Datei wurde seit 989ca88 nicht mehr angefasst. WAS AN DER MELDUNG NICHT TRAEGT — drei Stellen: (1) 'Adam bekommt den Befehlsblock aus DIESER Datei in die Hand' ist nicht belegt: die verbindliche Reihenfolge in MIGRATION.md:34-40 verweist fuer Node ausdruecklich auf den ZETTEL, nicht auf den Befehlsblock. (2) Die 'unvollstaendige Nachmessung' ist anderswo bereits geschlossen — scripts/node_vollzug_pruefen.sh (bash -n sauber) vergleicht beide node_modules-Orte per md5 und trennt claude_system von claude_bot; ABHAENGIGKEITEN.md:75 fuehrt ihn. (3) Der Vorwurf gegen components.json:54 ('CLI verlangt >=22') traegt nicht: der ZETTEL selbst haelt fest, dass Node fuer die INSTALLATION ueber npm gebraucht wird, nur nicht fuer den Betrieb — die Registerzeile behauptet keine Laufzeit-Abhaengigkeit. Der verbleibende, echte Bruch ist damit ein Regel-⑪-Bruch: zwei Dokumente zum selben Vorgang, das aeltere mit widerlegtem Kernsatz und 'Ueberholt durch: —', und MIGRATION.md:104 verlinkt weiterhin genau dieses.

**Beleg:**
```
$ sed -n '13p;71p;5p' docs/node-major-befehlsblock.md
  ->  '**Die Claude-CLI läuft auf Node.** Ein Major-Bruch nimmt also nicht ein'
  ->  'node --version && npm ls -g --depth=0'
  ->  '> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.'
$ grep -c 'node_modules\|md5\|_bundled\|doppelt' docs/node-major-befehlsblock.md  ->  0
$ sed -n '21,28p' docs/auftraege/ZETTEL-node-22-auf-24.md  ->  '**Gemessen trifft das nicht zu. Die CLI hängt nicht an Node.** ... ELF-Binärdatei ... Läuft sie ohne Node im Pfad? **Ja.** `env -i PATH=<ohne node> claude --version` -> `2.1.209 (Claude Code)`'
$ git -C /home/user/claude-telegram-bot log --oneline --all -- docs/node-major-befehlsblock.md  ->  989ca88 ... / 025ef8b ...  (keine Aenderung nach dem ZETTEL vom 29.08.)
$ sed -n '34,40p' MIGRATION.md  ->  '... `docs/auftraege/ZETTEL-node-22-auf-24.md` (Rückweg und Prüfschritte) ...'
$ bash -n scripts/node_vollzug_pruefen.sh && echo OK  ->  OK ; grep -n 'md5\|node_modules' scripts/node_vollzug_pruefen.sh -> 60/62/123/124 (beide Orte per md5)
```

**Widerleger (hält):** Ich habe die Widerlegung ernsthaft versucht und bin gescheitert — der dokumentarische Kern besteht, zwei Nebenbegruendungen der Meldung dagegen nicht.

WAS ICH SELBST GEMESSEN HABE (Arbeitskopie df5dc69, identisch mit dem Commit-Stand):
(1) Zeile 13 sagt woertlich '**Die Claude-CLI laeuft auf Node.**', Zeile 5 'Ueberholt durch: —', Zeile 71 misst nur 'node --version && npm ls -g --depth=0'. grep -ci 'node_modules|md5|_bundled|doppelt|2.1.219' auf die Datei = 0.
(2) Keine Reparatur, nirgends: 'git status --porcelain' fuer die Datei ist leer, und ueber ALLE Refs (git rev-list --all, 200 Commits) liest Zeile 5 ausnahmslos 'Ueberholt durch: —'. Letzte Beruehrung 989ca88 vom 26.07.2026, 01:00 — die ZETTEL-Commits sind 876b299 (29.08., 04:25) und 9545b58 (29.08., 17:52). Also nicht laengst repariert, und die Vorsitzung hat nicht an der falschen Stelle gesucht.

MEIN STAERKSTER WIDERLEGUNGSVERSUCH — UND ER FAELLT:
ABHAENGIGKEITEN.md:75 warnt selbst, dass es ZWEI CLIs gibt und nur die zweite den Betrieb traegt: 'claude_system' (npm-global, 2.1.209) und 'claude_bot' (die gebuendelte 2.1.219, die das SDK tatsaechlich startet) — 'wer sie zusammenwirft, baut einen Fehlalarm'. Der ZETTEL hat '/

---

## [29] docs/auftraege/2026-08-29_bauauftrag-offene-updates-einspielen.md — STILL
**Maschine:** keine

Vollstaendig bestaetigt, in allen drei Teilen. (a) Die Datei liegt heute weiterhin DREIMAL byte-gleich (md5 508a4f115e633af95c4449f20dbbfd9c) unter docs/20260829_bauauftragoffeneupdateseinspielen.md, docs/auftraege/20260829_bauauftrag-offene-updates-einspielen.md und docs/auftraege/2026-08-29_bauauftrag-offene-updates-einspielen.md. (b) Keine der drei traegt einen Gueltigkeits-Kopf nach Regel ⑪ (grep -ci auf 'überholt durch|ueberholt durch|Gültigkeits-Kopf' = 0/0/0). (c) Die Tabelle ist in BEIDEN Richtungen falsch: 'pymupdf | 1.28.0 | 1.28.2 | offen' ist erledigt (requirements.txt:31 `pymupdf>=1.28.2`, bot.py:11357ff. dokumentiert den vollzogenen fitz->pymupdf-Wechsel, MIGRATION.md-Eintrag 46 verzeichnet ihn), und 'claude-agent-sdk | 0.2.127 | 0.2.144' ist ueberholt, weil docs/auftraege/BEFUND-sdk-aenderungsnotizen-0.2.127-0.2.148.md:10 0.2.148 als verfuegbar misst und ausdruecklich vorschlaegt, dorthin zu springen. WAS NICHT TRAEGT: nur eine Zeilennummer — die Meldung nennt bot.py:11074, die Sache steht heute bei 11357; das macht sie nicht gegenstandslos. Die Meldung ueberzeichnet nichts. Still ist der Bruch, weil eine Versionstabelle mit Spalte 'Zustand: offen' wie ein Ist-Stand aussieht und nichts im Dokument den Leser warnt; wer sie befolgt, spielt SDK 0.2.144 ein und faellt hinter die bereits getroffene Entscheidung zurueck.

**Beleg:**
```
$ md5sum docs/20260829_bauauftragoffeneupdateseinspielen.md docs/auftraege/20260829_bauauftrag-offene-updates-einspielen.md docs/auftraege/2026-08-29_bauauftrag-offene-updates-einspielen.md
  ->  508a4f115e633af95c4449f20dbbfd9c  (dreimal identisch, je 7830 Bytes)
$ for f in <die drei>; do grep -ci 'überholt durch\|ueberholt durch\|Gültigkeits-Kopf' $f; done  ->  0 / 0 / 0
$ sed -n '17,18p' docs/auftraege/2026-08-29_bauauftrag-offene-updates-einspielen.md
  ->  '| `pymupdf` | 1.28.0 | 1.28.2 | offen |'
  ->  '| `claude-agent-sdk` | 0.2.127 | 0.2.144 | offen |'
$ grep -n pymupdf requirements.txt  ->  31:pymupdf>=1.28.2
$ grep -n pymupdf bot.py | head -3  ->  11357: **`pymupdf` statt `fitz` (29.08., beim Patch-Sprung auf 1.28.2 gemessen).**  / 11370:        import pymupdf as fitz
$ sed -n '10,13p' docs/auftraege/BEFUND-sdk-aenderungsnotizen-0.2.127-0.2.148.md  ->  '**Der Auftrag nennt 0.2.144 als Ziel; verfügbar ist bereits 0.2.148.** ... **Vorschlag: auf 0.2.148 springen**'
```

**Widerleger (hält):** Selbst gemessen an df5dc69, alle drei Teile bestaetigt — und ich habe keinen Weg gefunden, sie zu entkraeften.

(a) Dreifach byte-gleich: md5 508a4f115e633af95c4449f20dbbfd9c, je 7830 Bytes, und alle drei sind in df5dc69 GETRACKT (git show df5dc69:<pfad> liefert dreimal dieselbe Summe). Kein Arbeitskopie-Artefakt.

(b) Kein Gueltigkeits-Kopf: grep auf 'überholt durch|ueberholt durch|Gültigkeits-Kopf|maßgeblich|Stichtag' = 0 in allen drei, auch ueber head -8. Gemessen, nicht behauptet.

(c) Tabelle in beiden Richtungen falsch — und die SDK-Haelfte ist SCHAERFER als die Meldung wusste: Die Meldung stuetzt sich auf einen VORSCHLAG im Befund. Tatsaechlich ist es eine GETROFFENE Entscheidung: docs/auftraege/ENTSCHEIDUNGEN-FUER-ADAM-2026-08-29.md:15-17 traegt '[STAND 29.08., 17:3x] ③ und ⑥ sind entschieden: Sprung auf 0.2.148, aber im Fenster nach Node, und mcp + anyio werden mitgepinnt.' df5dc69 stammt von 19:17 desselben Tages, liegt also NACH dem Entscheid. Der Satz 'faellt hinter die bereits getroffene Entscheidung zurueck' trifft damit woertlich zu. pymupdf ebenso bestaetigt: requirements.txt:31 pymupdf>=1.28.2, bot.py _extract_pdf_text dokumentiert den vollzogenen fitz->pymupdf-Wec

---

## [36] botenpost.py — STILL
**Maschine:** beide

botenpost.ziel_finden() (heute Zeile 63-73) liest die Vorlieben weiterhin fest ueber Path.home()/.config/claude-telegram-bot/prefs.json und ignoriert USER_PREFS_FILE — anders als bot.py:108-110. Gemessen: mit USER_PREFS_FILE auf eine Wegwerf-Datei (Kennung 999999) und ohne ALLOWED_USER_IDS liefert ziel_finden() trotzdem die Kennung aus dem echten Heim. Zweite, schwerere Haelfte ebenfalls unveraendert: findet sich kein Ziel, gibt legen() stumm None zurueck (keine Ausnahme), und KEINER der sieben Aufrufer wertet den Rueckgabewert aus — auftragsbuch.py:427, hora.py:520, wachposten.py:424, start_waechter.py:252, erinnerungen.py:190, stundenblume.py:1032, wartungsfenster.py:119. Bei wachposten und erinnerungen ist das besonders tueckisch: beide umschliessen den Aufruf mit try/except und schreiben ihren Stand NUR bei einer Ausnahme nicht fort — legen() wirft aber keine, also gilt die nie gesendete Meldung als zugestellt und der naechste Lauf sucht sie nicht wieder. Es gibt repoweit keinen einzigen Pruefer fuer ziel_finden (grep: nur Definition und die eine Verwendung). Einschraenkung zur Meldung: den konkreten VPS-Fall (root ohne /root/.config) kann ich hier nicht messen — wachposten.timer laeuft laut ABHAENGIGKEITEN.md mit User=claudebot, dort existiert prefs.json vermutlich. Der Code-Defekt selbst ist maschinenunabhaengig und wurde nie angefasst (git log -- botenpost.py: letzter Commit 03e8e9e, Knopf-Erweiterung).

**Beleg:**
```
$ env -u ALLOWED_USER_IDS HOME=.../m36/echtheim USER_PREFS_FILE=.../m36/prefs.json python3 -c "import botenpost; print('ziel_finden() =', repr(botenpost.ziel_finden()))"
ziel_finden() = '111222333'      # in der Wegwerf-Datei stand 999999 — sie wurde nicht gelesen

$ env -u ALLOWED_USER_IDS HOME=.../m36/leerheim USER_PREFS_FILE=.../m36/prefs.json python3 -c "import botenpost; print(repr(botenpost.ziel_finden())); print('legen() =', repr(botenpost.legen('TESTMELDUNG Waechter','waechter')))"
ziel_finden() = ''
legen() = None -> keine Ausnahme, kein Pfad

$ grep -rn 'botenpost' --include=*.py . | grep -v scripts/test_
auftragsbuch.py:427:            botenpost.legen(
scripts/hora.py:520:    botenpost.legen(text, "hora")
scripts/wachposten.py:424:        botenpost.legen(kurz, absender="wachposten", knopf=knopf)
scripts/start_waechter.py:252:    botenpost.legen(text, "waechter")
scripts/erinnerungen.py:190:        botenpost.legen(text, absender="blume", ziel=ZIEL_KANAL or None)
scripts/stundenblume.py:1032:    botenpost.legen(text, "blume")
scripts/wartungsfenster.py:119:    botenpost.legen(text, "fenster")
(alle sieben als blosse Anweisung, kein Ziel der Zuweisung)

$ grep -rn 'ziel_finden' --include=*.py .
./botenpost.py:63:def ziel_finden() -> str:
./botenpost.py:109:    ziel = str(ziel or ziel_finden())      # kein Pruefer

$ git -C /home/user/claude-telegram-bot log --oneline -1 -- botenpost.py
03e8e9e Der Ja-Knopf: die Meldung fragt nicht mehr, sie bietet an
```

**Widerleger (hält):** Selbst gemessen, ausgefuehrt statt gelesen — der Fund haelt, und die schwere Haelfte ist BREITER als gemeldet. (1) Beide Messungen der Vorsitzung reproduzieren woertlich: ziel_finden() liefert mit HOME=echtheim und USER_PREFS_FILE=Wegwerf-Datei die Kennung 111222333 aus dem echten Heim, nicht die 999999 aus der Wegwerf-Datei; mit leerem Heim liefert es '' und legen() gibt None zurueck, ohne zu werfen. (2) Ende-zu-Ende mit dem ECHTEN wachposten.lauf(): ohne Ziel meldet lauf() einen Befund, es entsteht nicht einmal ein outbox-Ordner, der Stand wird trotzdem fortgeschrieben ({'bot-errors.log': 32, '_gemeldet': {...}}), und der ZWEITE Lauf liefert 0 — die Meldung ist verloren. (3) Der Widerlegungsversuch, der am haertesten scheiterte und den Fund zugleich ausweitet: mit GUELTIGEM Ziel (ALLOWED_USER_IDS=4711), aber blockiertem POSTFACH_DIR, gibt legen() ebenfalls None zurueck (die abschliessende Klausel `except Exception: return None  # ein Meldeweg, der klemmt, darf nichts brechen`), der Stand wird wieder fortgeschrieben, zweiter Lauf 0. Der Defekt haengt damit WEDER an prefs.json NOCH an USER_PREFS_FILE NOCH an einer Maschine: JEDER Zustellfehler von legen() ist stumm. Der W2-Pruefer 

---

## [42] scripts/api_cache_pflege.sh — KOSMETISCH
**Maschine:** beide (Textdefekt) — wirksam: keine

Der TEXTBEFUND traegt vollstaendig und ist heute unveraendert: Commit 059fa3c (18.08.2026) hat den root/systemd-Kommentarblock MITTEN in die Zeile `set -uo pipefail` gesetzt; uebrig blieb `set -u` in Z. 26 und das Fragment `o pipefail` am Ende der Kommentarzeile 31. Vor 059fa3c stand dort nachweislich `set -uo pipefail`. Gemessen: nach Einlesen des Kopfes ist pipefail 'off', nounset 'on'. WAS AN DER MELDUNG NICHT TRAEGT: die Wirkungsbehauptung. 'Die Haertung hat die Fehlerweitergabe abgeschaltet' ist falsch — es gab hier nie eine Fehlerweitergabe, die pipefail haette tragen koennen. Das Skript hat KEIN `set -e` (Z. 26 ist der einzige `set`-Aufruf), und der Exit-Status KEINER Pipeline wird irgendwo verbraucht: `_belegt_mb` wird nur in Zuweisungen (Z. 45, 58) und in `[ ... -gt ]`-Tests (Z. 52, 60) per Kommandosubstitution ausgewertet, dort zaehlt allein die AUSGABE; die Pipeline in Z. 53 landet ebenfalls nur in einer Zuweisung. A/B-Lauf mit scheiterndem `du` (Attrappe) gegen eine Fassung mit repariertem `set -uo pipefail`: byte-gleiches Verhalten, gleiche stderr-Zeilen, gleicher Bericht, gleicher Exit. Der von der Meldung gefuerchtete 'leere Wert mit Exit 0' entsteht ohnehin und wird von `[` mit 'integer expression expected' quittiert — mit wie ohne pipefail. Ergo heute kein Verhaltensbruch, weder auf dem VPS noch sonstwo. Der Defekt bleibt trotzdem einer und wird in dem Moment still gefaehrlich, in dem jemand `set -e` ergaenzt oder einen Pipeline-Status auswertet und annimmt, pipefail sei an — was die Zeile ja behauptet zu tun.

**Beleg:**
```
$ sed -n '26,31p' scripts/api_cache_pflege.sh | cat -A
set -u$
# Kein $HOME hier: ...$
...
# Zwischenlager. (Belegt 29.07.-18.08.2026.)o pipefail$

$ sed -n '1,36p' scripts/api_cache_pflege.sh > kopf.sh
$ bash -c 'set +o pipefail; source kopf.sh; shopt -o pipefail; shopt -o nounset'
pipefail       off
nounset        on

$ grep -n 'set -' scripts/api_cache_pflege.sh
26:set -u          (kein set -e im ganzen Skript)

A/B-Messung, du-Attrappe (schlaegt immer fehl, Exit 1):
A) heutiger Kopf (set -u):
  line 52: [: : integer expression expected
  line 60: [: : integer expression expected
  Zwischenlager: 0 MB -> 0 MB (Deckel 0 MB) / EXIT=0
  Bericht: belegt_mb 0, vorher_mb 0, deckel_gerissen false / Dateien: f1 f2 f3 (unangetastet)
B) reparierter Kopf (sed '26s/^set -u$/set -uo pipefail/'):
  line 52: [: : integer expression expected
  line 60: [: : integer expression expected
  Zwischenlager: 0 MB -> 0 MB (Deckel 0 MB) / EXIT=0
  Bericht: identisch / Dateien: f1 f2 f3
=> kein messbarer Unterschied

$ git -C /home/user/claude-telegram-bot log -S'2026.)o pipefail' --oneline -- scripts/api_cache_pflege.sh
059fa3c B1: der 21-Tage-Ausfall - Ursache, Architektur und der Pruefer, der ihn faengt
$ git -C /home/user/claude-telegram-bot show 025ef8b:scripts/api_cache_pflege.sh | sed -n '26p'
set -uo pipefail        (Zustand VOR 059fa3c)
$ git -C /home/user/claude-telegram-bot show HEAD:scripts/api_cache_pflege.sh | diff - <Arbeitskopie>  -> IDENTISCH
```

---

## [30] scripts/nachzieher.py — KOSMETISCH
**Maschine:** keine

Die MESSUNG reproduziert exakt — die BEWERTUNG traegt nicht. Reproduziert: components.json enthaelt kein einziges '==' (grep -c = 0), und ein korrekt gebauter Patch auf components.json wird abgelehnt (exit 1), waehrend derselbe Patch auf requirements.txt durchgeht. Der Eintrag 'components.json' in ERLAUBTE_DATEIEN ist damit tot; scripts/test_nachzieher_c1.py legt dafuer nur ein leeres `{}` an und uebt den Fall nie. VIER Gruende, warum die Meldung ihre Schwere nicht traegt: (1) Der automatische Weg kann diesen Fall gar nicht erzeugen — scripts/updater.py:339 verdrahtet in `_folge_patch` fest `"datei": "requirements.txt"`; der Zweig ist nur erreichbar, wenn ein Mensch den Patch von Hand schreibt. (2) Dann scheitert er LAUT: exit 1, klarer Text, nichts geschrieben — das ist die gewollte Wirkung einer Weissliste, kein stiller Bruch. Die Meldung nennt selbst exit 1 und stuft es trotzdem wie einen Ausfall ein. (3) Das Werkzeug verspricht die Faehigkeit nicht: sein eigener Kopf (Zeilen 21-23) sagt, veraendert werden duerfe 'ausschliesslich die Zeichenfolge der Version in einer bereits vorhandenen Pin-Zeile'. Nur der Datei-Weisslisteneintrag ist ueberzaehlig. (4) 'die Haelfte der in MIGRATION.md:1320 beauftragten Folge-Korrektur (c)' ist keine laufende Beauftragung: die Stelle steht heute in MIGRATION.md:1328 und liegt in 'Phase 11 — Backlog', deren Kopf ausdruecklich sagt 'Wird NIEMALS in den laufenden Punkt gezogen — kommt erst nach Phasen-Audit dran'. (c) wurde nie gebaut, ist also auch nicht 'strukturell unausfuehrbar geworden'. Was bleibt, ist eine tote, ungetestete Zeile in einer SICHERHEITS-Weissliste: harmlos heute, aber eine Einladung fuer den, der spaeter den Matcher lockert und dann glaubt, components.json sei bereits geprueft freigegeben.

**Beleg:**
```
$ cp -r stand-aktuell-ro m30 && cd m30
$ cat > /tmp/p30.json <<'EOF'
{"datei":"components.json","paket":"claude-agent-sdk","von":"0.2.127","nach":"0.2.148","grund":"Messung"}
EOF
$ python3 scripts/nachzieher.py --patch /tmp/p30.json --repo . --pruefen
  ->  ⛔ Abgelehnt: kein Pin claude-agent-sdk==0.2.127 in components.json gefunden   EXIT=1
$ (dasselbe mit "datei":"requirements.txt")
  ->  geprüft: requirements.txt / vorher: claude-agent-sdk==0.2.127 / nachher: claude-agent-sdk==0.2.148   EXIT=0
$ grep -c '==' components.json  ->  0
$ grep -n '"datei": "requirements.txt"' scripts/updater.py  ->  339:        auftrag = {"datei": "requirements.txt", "paket": c["name"],
$ grep -n components scripts/test_nachzieher_c1.py  ->  24:(TMP / "components.json").write_text("{}\n", encoding="utf-8")   (kein Patch-Test darauf)
$ python3 scripts/test_nachzieher_c1.py | tail -1  ->  Alle C1-Nachzieher-Tests bestanden.
$ grep -n 'Versions-Nennungen' MIGRATION.md  ->  1328 (im Abschnitt '## Phase 11 — Backlog', Kopf: 'Wird NIEMALS in den laufenden Punkt gezogen')
$ git -C /home/user/claude-telegram-bot log --oneline --all -- scripts/nachzieher.py  ->  025ef8b (seither unveraendert)
```

---
