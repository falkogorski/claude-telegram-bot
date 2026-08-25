<!-- ROLLE: entkernung-katalog -->
**Stichtag:** 2026-08-25 · **ueberholt durch:** — · **massgeblich ist die Status-Zeile in `MIGRATION.md`**

# Entkernungs-Katalog — vollständige Befunde (Workflow wf_a08a5b8b-94d, HEAD 1817c86)

**Methode:** je Prüfzeile wurde der bewachte Schutz entfernt oder verfälscht und der Prüfer AUSGEFÜHRT. „grün-geblieben“ = der Schutz war weg, der Prüfer meldete ihn als vorhanden. „falsche-zeile“ = der Prüfer schlägt an, obwohl der Schutz intakt ist (Fehlalarm-Bauart).

Gemessen: 116 Prüfzeilen · nicht tragfähig: 61. Zwei Agenten (nachweis:6, synthese) fielen dem Kontingent-Limit zum Opfer; deren Nachweise fehlen, die Messungen der sechs Gruppen sind vollständig.


## Gruppe 1 vollstaendig wie zugeteilt: scripts/test_eingangsschranken.py, scripts/test_kalender_caldav.py, scripts/test_gruendlich_b3.py, scripts/test_start_waechter_b1.py, scripts/test_pin_bezug_5_13.py, scripts/test_queue_order_5_5.py. Vollstaendig durchgemessen (jede Pruefzeile einzeln entkernt): test_start_waechter_b1.py (8/8), test_queue_order_5_5.py (5/5), test_pin_bezug_5_13.py (5/5). Stichprobe nach Verdacht: test_kalender_caldav.py (4 von 12), test_gruendlich_b3.py (4 von 10), test_eingangsschranken.py (4 von 60). Arbeitskopien: /tmp/entkern-1 und /tmp/entkern-1-repo/claude-telegram-bot; Eingriffsskripte unter /tmp/entkern-1/_p/, Import-Attrappen unter /tmp/entkern-1/_stubs/. Das Repo /home/user/claude-telegram-bot wurde nur gelesen (git status am Ende leer).

geprüft: 30 · gefunden: 15

Umgebung: DIE PRUEFUMGEBUNG TRAEGT FUENF DER SECHS DATEIEN NICHT. Gemessen: nur test_start_waechter_b1.py startet nativ; die anderen fuenf brechen mit ModuleNotFoundError ab, bevor eine Pruefzeile laeuft — weder python-telegram-bot noch claude-agent-sdk sind installiert, kein venv vorhanden. Ein Nachinstallieren waere ein Netzabruf gewesen und schied laut Vorgabe aus. Ich habe stattdessen minimale Import-Attrappen fuer telegram/telegram.ext/telegram.constants/telegram.error und claude_agent_sdk gebaut (/tmp/entkern-1/_stubs) und VOR jedem Eingriff die Ausgangsfarbe gemessen, damit attrappenbedingtes Rot nicht als Befund durchgeht. Das trug fuer vier der fuenf Dateien vollstaendig.

WAS DAMIT NICHT MESSBAR WAR — und das ist die wichtigste Einschraenkung dieses Berichts: In test_eingangsschranken.py bleiben drei Zeilen auch nach dem Entkernen attrappenbedingt rot und sind daher NICHT beurteilt: "Nebenlauf hat kein Werkzeug", "die Hauptsitzung genehmigt nicht vorab" (beide TypeError aus meiner Attrappe), "Link-Vorschau programmweit aus" (AttributeError). Ausgerechnet die erste ist die zentrale Sicherheitszeile: Sie baut die echte Befehlszeile ueber SubprocessCLITransport._build_command() und prueft --tools, --permission-mode und --disallowedTools. Ich habe versucht, sie ueber die Attrappe messbar zu machen, und es bewusst gelassen — eine nachgebaute _build_command haette genau das gemessen, was ich hineinlege. Nach ihrer Bauart ist sie die vorbildlichste Zeile der Gruppe (sie misst die Verdrahtung, nicht die Felder); belegt ist das hier aber nicht. Konkret offen geblieben: Beim Leeren des zweiten Riegels (disallowed_tools=[] in der Fabrik) blieb kein Pruefer rot — ob das ein Befund ist oder nur an der ausgefallenen Zeile liegt, kann ich nicht sagen. Diese eine Messung gehoert in einer Umgebung mit echtem SDK wiederholt.

NICHT GESCHAFFT: test_eingangsschranken.py 56 von 60 Zeilen, test_kalender_caldav.py 8 von 12, test_gruendlich_b3.py 6 von 10. Ich habe Vollstaendigkeit bei den drei kleinen Dateien gewaehlt und bei den grossen nach Verdacht gestochen (Quelltext lesende Zeilen zuerst) — die Trefferquote rechtfertigt das: von 13 gemessenen lesenden Zeilen waren 11 umgehbar, von 17 ausfuehrenden keine einzige.

ZWEI BEOBACHTUNGEN ZUR UMGEBUNG SELBST. (1) Der Pruefer test_eingangsschranken.py misst den Ordnernamen mit: In jedem Arbeitsbaum, der nicht "claude-telegram-bot" heisst, meldet er ohne jeden Eingriff einen Fehlalarm ("der Alltag laeuft weiter ohne Dialog"). Das kollidiert direkt mit der Projektregel R4 Probelauf im Klon, die "git worktree add ../probe-<name>" vorschreibt. Als Befund aufgenommen. (2) rsync fehlt ebenfalls, was test_log_sync_quittung.py betrifft — nicht meine Gruppe, deckt sich aber mit der Vormessung.

METHODISCHER NACHTRAG: In zwei Faellen hat die vorgeschriebene Reihenfolge — erst aufschreiben, welche Zeile rot werden soll — einen Fehlschluss verhindert. Bei test_kalender_caldav.py Zeile 178 waere ich beim ersten Lauf mit "traegt" zufrieden gewesen; sie schlug aber nur an der Mailadresse an, nicht am Geheimnis, und erst der zweite, engere Eingriff zeigte die Luecke. Bei test_gruendlich_b3.py Zeile 179 habe ich die Gegenprobe gefahren (direkter Fall ROT, refaktorierter Fall GRUEN) — ohne sie haette ich nicht belegen koennen, dass der Pruefer den Gegenstand ueberhaupt erreicht.

### scripts/test_start_waechter_b1.py:167 — "eigener Prozess zählt nicht als Bot"
**Schwere:** gruen-geblieben

**Behauptet:** Der Wächter hält seinen eigenen Prozess nicht für den Bot — der Filter `"start_waechter" in teile[1]` in `bot_prozess()` (scripts/start_waechter.py:77) schließt Wächter-Prozesse aus der pgrep-Ausgabe aus.

**Eingriff:** In scripts/start_waechter.py:77 den Namensfilter gestrichen: `if len(teile) != 2 or "start_waechter" in teile[1]:` → `if len(teile) != 2:`. Die zweite Schranke (`pid != eigen`) blieb stehen.

**Ergebnis:** GRÜN geblieben, alle 8 Zeilen, RC=0 ("Alle B1-Start-Wächter-Tests bestanden"). Ursache direkt nachgemessen: Der Prüfer legt in die vorgetäuschte pgrep-Zeile die EIGENE PID (`f"{os.getpid()} python3 scripts/start_waechter.py …"`), also fängt ihn `pid != eigen` ab. Gegenmessung mit fremder PID: `A eigene pid -> None` / `B fremde pid -> 4242`. Der reale Fall ist genau B: im `--detach`-Betrieb sieht der abgekoppelte Kindprozess den Elternprozess unter fremder PID und hält ihn für den Bot — der Wächter meldet dann „sauber hochgekommen", während der Bot tot ist.


### scripts/test_start_waechter_b1.py:220 — "Meldeziel notfalls aus der Einstellungsdatei"
**Schwere:** zu-eng

**Behauptet:** Der Rückfallweg über ~/.config/claude-telegram-bot/prefs.json greift, wenn ALLOWED_USER_IDS fehlt (start_waechter.py:195-203).

**Eingriff:** Den kompletten prefs.json-Rückfallweg in `_melde_ziel()` entfernt, `return ""` an seine Stelle gesetzt.

**Ergebnis:** ROT bei vorhandener prefs.json ("Rückfallweg über die Einstellungsdatei greift nicht") — ABER die Prüfzeile stellt ihre eigene Voraussetzung nicht her: sie prüft nur `if prefs.exists()`. Zweite Messung mit demselben Eingriff und `HOME=/tmp/leerhome`: GRÜN, RC=0, alle Tests bestanden. Der Schutz, dessen Fehlen den Wächter auf dem VPS stumm machte (Kommentar start_waechter.py:186-190), ist also nur dann bewacht, wenn die Maschine des Prüflaufs zufällig eine prefs.json hat.


### scripts/test_queue_order_5_5.py:75 — "FIFO: drei Nachrichten chronologisch"
**Schwere:** gruen-geblieben

**Behauptet:** Normale Nachrichten werden chronologisch ans Ende der Warteschlange gehängt (bot.py:8181, `mb.queue.append(job)`).

**Eingriff:** In bot.py:8181 den Normalzweig umgedreht: `mb.queue.append(job)` → `mb.queue.appendleft(job)`. Damit drängt sich jede normale Nachricht vor alle wartenden.

**Ergebnis:** GRÜN geblieben, alle 5 Zeilen, „Alle 5.5-Warteschlangentests bestanden". Grund: `_fifo_reihenfolge()` baut eine eigene `deque()` und ruft selbst `q.append(...)`. Der Prüfkörper berührt bot.py an keiner Stelle — er misst die im Prüfer nachgebaute Simulation, nicht die Verzweigung, die er im Docstring als Gegenstand nennt.


### scripts/test_queue_order_5_5.py:76 — "Interrupt kommt nach vorne"
**Schwere:** gruen-geblieben

**Behauptet:** Ein Stopp-/Korrektursignal wird vorne eingereiht (bot.py:8175, `mb.queue.appendleft(job)` im Interrupt-Zweig).

**Eingriff:** In bot.py:8175 `appendleft` → `append`. Die Korrektur landet damit hinter allen wartenden Jobs; der laufende Vorgang wird zwar abgebrochen, die Korrektur aber zuletzt bearbeitet.

**Ergebnis:** GRÜN geblieben, alle 5 Zeilen, RC=0. Gleiche Ursache: Der Prüfkörper legt selbst `q.appendleft(interrupt_msg)` in eine eigene deque und prüft danach `q[0]`. Von bot.py wird nur `_is_interrupt` berührt, nie die Einreih-Verzweigung.


### scripts/test_pin_bezug_5_13.py:85 — "/status nennt keine Sekunden"
**Schwere:** gruen-geblieben

**Behauptet:** Die Sekundenangabe in /status ist nicht zurück — geprüft über die Abwesenheit der Zeichenkette `"letzte Regung vor {silent}s"` in bot.py.

**Eingriff:** Die Sekundenangabe in bot.py:3606 wieder eingebaut, aber neu getippt statt wörtlich: `f"   ⏱️ letzte Regung vor {int(silent)} s "` ersetzt den Aufruf von `_vor_wie_lange(...)`.

**Ergebnis:** GRÜN geblieben, alle 5 Zeilen, „Alle 5.13-Pin-Bezug-Tests bestanden". Der Verstoß steht nachweislich im Code (grep: `3606: f"   ⏱️ letzte Regung vor {int(silent)} s "`). Die Zeile sucht eine exakte historische Zeichenkette und nicht die Eigenschaft, die sie im Namen führt.


### scripts/test_pin_bezug_5_13.py:86 — "kein Dateihandle ohne with"
**Schwere:** gruen-geblieben

**Behauptet:** Kein Dateihandle ohne `with` — geprüft über die Abwesenheit von `'mem_file.open("a", encoding="utf-8").write'` in bot.py.

**Eingriff:** Den `with`-Block in bot.py:5971-5973 durch genau den Fehler ersetzt, den die Zeile verbieten soll, nur unter anderem Bezeichner: `ziel = mem_file` / `ziel.open("a", encoding="utf-8").write(new_entry)`.

**Ergebnis:** GRÜN geblieben, alle 5 Zeilen, RC=0. grep bestätigt den offenen Handle in Zeile 5973. Ein Variablenname genügt, um die Zeile blind zu machen.


### scripts/test_kalender_caldav.py:178 — "keine Zugangsdaten im Quelltext"
**Schwere:** gruen-geblieben

**Behauptet:** Kein Zugangsdaten-Rest in kalender.py — gesucht wird nach `@icloud.com`, `@me.com`, `password="`, `passwort="`.

**Eingriff:** Zwei Läufe. (a) Kennung UND App-Passwort hartkodiert → ROT, aber nur wegen `@icloud.com`. (b) Realistischer: NUR das Geheimnis hartkodiert, Kennung weiter aus der Umgebung: `APP_PW = 'abcd-efgh-ijkl-mnop'   # zum Testen fest eingetragen`, `return bool(os.environ.get("ICLOUD_CALDAV_USER") and APP_PW)`.

**Ergebnis:** Lauf (b): GRÜN geblieben, alle 12 Zeilen, „Alle Kalender-Tests bestanden (ohne Netz, ohne Zugangsdaten)". Die Zeile findet die Mailadresse, aber nicht das Passwort — sie erkennt nur zwei Bezeichner-Schreibweisen (`password="`/`passwort="`) mit doppelten Anführungszeichen. Ein einfach gequotetes App-Passwort unter beliebigem Namen passiert sie ungehindert.


### scripts/test_kalender_caldav.py:184 — "7.4: der Link kommt NICHT in die Sprachausgabe"
**Schwere:** zu-eng

**Behauptet:** Der Adressfilter im Vorlese-Pfad greift (bot.py:10149, `text = re.sub(r"https?://\\S+", "", text)` in `_strip_markdown_for_tts`) und der lesbare Teil bleibt heil.

**Eingriff:** Genau diese eine Zeile stillgelegt: `text = re.sub(...)` → `pass  # URL-Filter entfernt` (Treffer geprüft: genau 1 Fundstelle, Zeile 10149).

**Ergebnis:** GRÜN geblieben, alle 12 Zeilen. Direkt nachgemessen, was ohne den Filter vorgelesen wird: `'Freitag, 21. August, 10:00, Team-Runde, https: ein Datei-Pfad'`. Die Adresse verschwindet nur, weil ein nachgelagerter Filter den Rest frisst — vorgelesen wird trotzdem genau der Unsinn, gegen den die Zeile gebaut wurde (Adams Beanstandung vom 17.06.). Die Zeile prüft `"zoom.us" not in gesprochen` und ist damit erfüllt, während ihr Gegenstand entfernt ist.


### scripts/test_gruendlich_b3.py:178 — "Tiefe wird in ensure_session erzwungen (C)"
**Schwere:** gruen-geblieben

**Behauptet:** Im Block von `ensure_session` steht die Erzwingung — geprüft über `"_thorough_on(user_id)" in block and 'effort = "max"' in block` auf dem Quelltext-Ausschnitt.

**Eingriff:** Der Griff, den ein nachlässiger Erbauer wirklich macht: auskommentieren statt löschen. bot.py:3375-3376 wurde zu `# vorerst stillgelegt:` / `# if effort_override is _UNSET and _thorough_on(user_id):` / `#     effort = "max"`.

**Ergebnis:** GRÜN geblieben. Die Textsuche zählt Kommentarzeilen als Vorhandensein — die Tiefen-Erzwingung ist wirkungslos, die Zeile meldet sie als erzwungen. Genau die Lücke, die die Projektregel vom 22.08. für Zeilenzählung beschreibt, hier bei einer reinen `in`-Suche.


### scripts/test_gruendlich_b3.py:179 — "KEIN close_session im ANTWORT-Pfad (D — der stille Fall)"
**Schwere:** gruen-geblieben

**Behauptet:** Im Antwort-Pfad wird die Sitzung nicht geschlossen — gemessen über den Syntaxbaum: `ast.If`-Knoten, deren `ast.unparse(k.test)` den Text `job.thorough` enthält und in deren Rumpf `close_session` vorkommt.

**Eingriff:** Zwei Läufe, mit Gegenprobe. (a) Direkt: `if job.thorough:` / `await close_session(job.user_id)` vor `sess.client.query(...)` eingesetzt. (b) Dieselbe Wirkung nach einem gewöhnlichen Refactor: `gruendlich = job.thorough` / `if gruendlich:` / `await close_session(job.user_id)`.

**Ergebnis:** (a) ROT — „die Sitzung wird im Antwort-Pfad geschlossen … ['Zeile 1797: job.thorough']", der Prüfer kann es also. (b) GRÜN geblieben. Eine Zwischenvariable genügt: Der Filter prüft den ENTPACKTEN TEXT der Bedingung auf den Namen `job.thorough`, nicht den Datenfluss. Das ist die von der Projektregel ausdrücklich genannte Form „AST-Prüfung, die nur nach einem Namen sucht".


### scripts/test_gruendlich_b3.py:184 — "die Tiefen-Wahl wird nicht still verworfen"
**Schwere:** gruen-geblieben

**Behauptet:** Die Tiefen-Bestätigung prüft, ob Gründlich sie überhaupt zulässt — gesucht wird `"_thorough_on(user_id)"` in den 1200 Zeichen vor der Bestätigungs-Zeichenkette.

**Eingriff:** Zwei Läufe. (a) Ehrlich: die Schranke bot.py:8693 zu `if False:  # Schranke entfernt`. (b) Mit stehengelassenem Kommentar: `# frueher: if _thorough_on(user_id):` / `if False:`.

**Ergebnis:** (a) ROT, punktgenau. (b) GRÜN geblieben — derselbe wirkungslose Zustand, nur mit der alten Zeile als Kommentar darüber. Zweite Fundstelle derselben Bauart in dieser Datei; zusätzlich ist das 1200-Zeichen-Fenster gegenüber jeder Einfügung davor unstabil.


### scripts/test_gruendlich_b3.py:186 — "Quellencheck-Zusatz bleibt unverändert"
**Schwere:** gruen-geblieben

**Behauptet:** Der Quellencheck-Zusatz ist nicht verschwunden — geprüft über `"_THOROUGH_PREFIX" in QUELLE`.

**Eingriff:** Die einzige Verwendungsstelle entfernt: bot.py:1796 `+ (_THOROUGH_PREFIX if job.thorough else ""))` → `+ "")`. Die Konstante (Zeile 783) und ihre Kommentar-Erwähnung (Zeile 1737) blieben stehen.

**Ergebnis:** GRÜN geblieben. Der Zusatz wird nachweislich nicht mehr an die Anfrage gehängt (grep zeigt nur noch Definition und Kommentar), der Prüfer meldet ihn als vorhanden. Exakt das Muster „Fabrik ja, Aufrufer nein" aus dem Probelauf vom 22.08.


### scripts/test_eingangsschranken.py:335 — "beide Nebenlaeufe nutzen die Fabrik"
**Schwere:** gruen-geblieben

**Behauptet:** Beide werkzeugfreien Neben-Läufe gehen über `werkzeugfreie_optionen` statt die Optionen von Hand zu bauen — gemessen über echte `ast.Call`-Knoten, Schwelle `len(aufrufe) >= 2`.

**Eingriff:** Im MAIL-Pfad (bot.py:9143, der Pfad, der Fremdinhalt aus fremden Postfächern verarbeitet) die Fabrik umgangen: `options = werkzeugfreie_optionen(system_prompt)` → `options = ClaudeAgentOptions(system_prompt=system_prompt)`. Damit fällt für diesen Lauf der ganze Riegel weg: kein `tools=[]`, kein `permission_mode="dontAsk"`, keine `disallowed_tools`.

**Ergebnis:** GRÜN geblieben. Ursache gemessen: Es gibt DREI Fabrikaufrufe (bot.py:4037, 9143, 10780), die Schwelle verlangt nur zwei — nach dem Eingriff sind noch zwei übrig. Die Zeile zählt eine Gesamtmenge über die ganze Datei, statt je Nebenlauf zu prüfen, dass genau dieser Pfad die Fabrik benutzt. Der Prüfer hat die Umstellung auf echte ast.Call-Knoten (Befund H10) bekommen, die Schwelle aber nicht.


### scripts/test_eingangsschranken.py:336 — "der PDF-Pfad baut nichts selbst"
**Schwere:** zu-eng

**Behauptet:** Gegentest zu H10: in einer Funktion, die Fremdinhalt verarbeitet, steht kein handgebautes `ClaudeAgentOptions(...)`.

**Eingriff:** Derselbe Lauf wie oben — handgebautes `ClaudeAgentOptions(system_prompt=system_prompt)` im Mail-Pfad (bot.py:9143).

**Ergebnis:** GRÜN geblieben. Die Zeile filtert auf eine fest verdrahtete Zweierliste von Funktionsnamen: `if knoten.name not in ("_summarize_pdf_direct", "_kontingent_frisch_messen_alt")`. Der Mail-Pfad steht nicht darin, obwohl er derselbe Fall ist — Fremdinhalt zu hundert Prozent. Eine Umbenennung oder ein dritter Fremdinhalt-Pfad entkommt ihr genauso. Dieselbe Aufzählungs-statt-Menge-Schwäche, die CLAUDE.md am 23.08. für den Register-Prüfer berichtigt hat.


### scripts/test_eingangsschranken.py — "der Alltag laeuft weiter ohne Dialog"
**Schwere:** falsche-zeile

**Behauptet:** Alltägliche Lesebefehle (cat/ls/grep/find/git log) lösen keinen Freigabe-Dialog aus (Governance-Lockerung „Lesen ja, schreiben nie").

**Eingriff:** Keiner — dies ist eine Messung des AUSGANGSZUSTANDS, gefunden beim Bestimmen der Basisfarbe.

**Ergebnis:** ROT ohne jeden Eingriff, wenn der Arbeitsbaum nicht `claude-telegram-bot` heißt: „Alltagsbefehle brauchen jetzt einen Dialog: ['cat /tmp/entkern-1/README.md', 'git -C /tmp/entkern-1 log --oneline -5', …]". Gegenprobe: identische Kopie unter /tmp/entkern-1-repo/claude-telegram-bot → GRÜN. Die Zeile misst den Ordnernamen mit. Das ist ein Fehlalarm genau in der Lage, die die Projektregel R4 („Probelauf im Klon", `git worktree add ../probe-<name>`) vorschreibt — der Prüfer und die Regel widersprechen einander.


### scripts/test_start_waechter_b1.py:161 — "sauberer Hochlauf → nichts anfassen"
**Schwere:** in-ordnung

**Behauptet:** Bei sauberem Hochlauf greift der Wächter nicht ein und meldet kurz Erfolg (rc 0, kein Rollback).

**Eingriff:** Schnellweg in `bewachen` stillgelegt: `if ok:` → `if False:` (start_waechter.py:235).

**Ergebnis:** ROT und nur diese Zeile: „Rückgabewert falsch: 1". Punktgenau.


### scripts/test_start_waechter_b1.py:162 — "kein Prozess → Rollback + Neustart"
**Schwere:** in-ordnung

**Behauptet:** Bei totem Bot wird auf den eingefrorenen Stand zurückgerollt und neu gestartet.

**Eingriff:** Die Rettung ausgebaut: `zurueck_ok, zurueck_fehler = zurueckrollen(venv, freeze)` / `neustart = neustart_ausloesen()` → feste Werte, kein Aufruf.

**Ergebnis:** ROT: „es wurde NICHT zurückgerollt, obwohl der Bot tot war". Zeilen 3 und 4 gingen als erwartbare Nachbarn mit, da sie denselben Pfad befahren.


### scripts/test_start_waechter_b1.py:163 — "Prozess lebt, Selbstcheck rot → trotzdem Rettung"
**Schwere:** in-ordnung

**Behauptet:** Ein lebender Prozess allein genügt nicht; der Selbstcheck ist dritte Bedingung in `sauber_hoch`.

**Eingriff:** Den Selbstcheck-Aufruf aus `sauber_hoch` gestrichen (start_waechter.py:144-147), `return True, ""` an seine Stelle.

**Ergebnis:** ROT, nur diese Zeile: „lebender Prozess mit rotem Selbstcheck galt als sauber!". Punktgenau.


### scripts/test_start_waechter_b1.py:164 — "gescheiterte Rettung wird doppelt laut"
**Schwere:** in-ordnung

**Behauptet:** Scheitert die Rettung, gibt es rc 2 und eine 🔴🔴-Meldung mit „FEHLGESCHLAGEN" und „von Hand".

**Eingriff:** Den Erfolgszweig unbedingt gemacht: `if zweite_ok and zurueck_ok:` → `if True:`, der laute Zweig wird nie erreicht.

**Ergebnis:** ROT, nur diese Zeile: „Rückgabewert falsch: 1". Punktgenau.


### scripts/test_start_waechter_b1.py:165 — "Bericht liegt auch für den 4-Uhr-Check bereit"
**Schwere:** in-ordnung

**Behauptet:** `melden()` legt zusätzlich zur Postfach-Nachricht eine Zustandsdatei ab, damit der Tagescheck den Befund nachholen kann.

**Eingriff:** Das `BERICHT.write_text(...)` in `melden()` durch `pass` ersetzt; die Postfach-Zustellung blieb.

**Ergebnis:** ROT, nur diese Zeile: „keine Zustandsdatei für den 4-Uhr-Check hinterlegt". Punktgenau. (Ein erster Eingriff — `try:` zu `if False:` — erzeugte einen SyntaxError statt einer Messung und wurde verworfen.)


### scripts/test_start_waechter_b1.py:166 — "kein Rückweg → nicht eingreifen, laut melden"
**Schwere:** in-ordnung

**Behauptet:** Fehlt die Freeze-Datei, wird nicht eingegriffen (kein Beenden, kein Rückbau), rc 2 und eine Meldung mit „NICHT ein…".

**Eingriff:** Den ganzen `if not freeze.exists():`-Block aus `bewachen` entfernt (start_waechter.py:246-251).

**Ergebnis:** ROT, nur diese Zeile: „der Bot wurde beendet, obwohl kein Rückweg vorlag!". Punktgenau.


### scripts/test_queue_order_5_5.py:72 — "Stopp/Korrektur-Signale erkannt"
**Schwere:** in-ordnung

**Behauptet:** `bot._is_interrupt` erkennt echte Stopp-/Korrektursignale.

**Eingriff:** `INTERRUPT_PREFIXES` (bot.py:1375) auf ein leeres Tupel gesetzt.

**Ergebnis:** ROT: „sollte Interrupt sein: 'Stopp'". Zeile 5 ging mit, weil sie `_is_interrupt` ebenfalls per assert benutzt.


### scripts/test_queue_order_5_5.py:73 — "Nachtrag/Ergänzung KEIN Interrupt"
**Schwere:** in-ordnung

**Behauptet:** Nachtrag/Ergänzung brechen den laufenden Vorgang NICHT ab.

**Eingriff:** `"nachtrag"` und `"wie"` vorn in `INTERRUPT_PREFIXES` eingefügt.

**Ergebnis:** ROT: „darf kein Interrupt sein: 'Nachtrag: auch noch X'".


### scripts/test_queue_order_5_5.py:74 — "Normale Nachrichten KEIN Interrupt"
**Schwere:** in-ordnung

**Behauptet:** Alltagsnachrichten lösen keinen Abbruch aus.

**Eingriff:** Derselbe Eingriff — `"wie"` in `INTERRUPT_PREFIXES`.

**Ergebnis:** ROT: „darf kein Interrupt sein: 'Wie spät ist es?'". Punktgenau, und die Zeile ist damit auch gegen zu weit gefasste Stoppwörter empfindlich.


### scripts/test_pin_bezug_5_13.py:82 — "Gruppe bekommt einen klickbaren Rueckweg"
**Schwere:** in-ordnung

**Behauptet:** In Gruppen (Kennung mit -100) liefert `_pin_bezug` einen Deep-Link auf die Nachricht.

**Eingriff:** Den Gruppenzweig in bot.py:5914 stillgelegt: `if cid is not None and str(cid).startswith("-100"):` → `if False:`.

**Ergebnis:** ROT, nur diese Zeile: „kein Deep-Link in der Gruppe: (↩︎ Nachricht 4242)". Punktgenau.


### scripts/test_pin_bezug_5_13.py:83 — "Privatchat bekommt KEINEN Link"
**Schwere:** in-ordnung

**Behauptet:** Im Privatchat wird kein Link erfunden, weil es dort keine adressierbare Nachricht gibt.

**Eingriff:** Die Zweigbedingung aufgeweicht: `str(cid).startswith("-100")` gestrichen, also `if cid is not None:`.

**Ergebnis:** ROT, nur diese Zeile: „im Privatchat steht ein Link, der ins Leere fuehrt: [↩︎ Original](tg://privatepost?channel=4711&post=4242)". Punktgenau.


### scripts/test_pin_bezug_5_13.py:84 — "ohne Nachricht kein Bezug"
**Schwere:** in-ordnung

**Behauptet:** Ohne Nachrichtennummer wird kein Bezug erfunden (leerer String).

**Eingriff:** Die Abfangzeile `if not mid: return ""` aus `_pin_bezug` entfernt.

**Ergebnis:** ROT, nur diese Zeile: „ohne Nachrichtennummer wird ein Bezug erfunden". Punktgenau.


### scripts/test_kalender_caldav.py:180 — "7.4: ohne Link keine leere Zeile (Gegenprobe)"
**Schwere:** in-ordnung

**Behauptet:** Ein Termin ohne Zugangslink bekommt keinen leeren Pfeil angehängt.

**Eingriff:** Die Bedingung vor dem Pfeil entfernt: `if link: teile.append(f"→ {link}")` → `teile.append(f"→ {link}")`.

**Ergebnis:** ROT, nur diese Zeile: „leerer Pfeil in der Zeile: Freitag, 21.08., 10:00 — Zahnarzt (Hauptstrasse 5) → ". Punktgenau.


### scripts/test_kalender_caldav.py:182 — "7.4: die Adresse steht nicht zweimal"
**Schwere:** in-ordnung

**Behauptet:** Steht die Adresse im Ortsfeld, wird sie dort herausgenommen statt doppelt gezeigt.

**Eingriff:** Das Herausnehmen in `Termin.lesbar()` durch `pass` ersetzt (`if link and link in ort: ort = ort.replace(...)`).

**Ergebnis:** ROT, nur diese Zeile: „die Adresse steht zweimal: … Runde (https://zoom.us/j/12345) → https://zoom.us/j/12345". Punktgenau.


### scripts/test_eingangsschranken.py — "bypassPermissions kommt nicht zurueck"
**Schwere:** in-ordnung

**Behauptet:** `bypassPermissions` taucht im ausführbaren Code nicht wieder auf (Kommentare ausgenommen).

**Eingriff:** Den Modus in der Fabrik zurückgedreht: `permission_mode="dontAsk"` → `permission_mode="bypassPermissions"` (bot.py, `werkzeugfreie_optionen`).

**Ergebnis:** ROT und punktgenau: „bypassPermissions steht wieder im Code: ['permission_mode=\"bypassPermissions\",']". Die Kommentar-Ausnahme trägt — die vier Erklärstellen in bot.py:3837/3884/3888/3935 schlagen nicht an. Diese Zeile ist gut gebaut.


## Gruppe 2 — bot.py-Selbstcheck (Z. 6854–7604), scripts/test_zielumgebung.sh, scripts/test_stall_5_18.py, scripts/test_linkinbox_5_14.py, scripts/test_zustellwaechter.py, scripts/test_channels_6.py, scripts/test_hermetik.py. Arbeitskopie /tmp/entkern-2, Erwartungen vorab in /tmp/entkern-2/_erwartungen.md (Abschnitte A–Q, jeweils VOR dem Eingriff geschrieben), Selbstcheck-Starter /tmp/entkern-2/_selfcheck_runner.py.

geprüft: 19 · gefunden: 15

Umgebung: BEFUND ZUR PRUEFUMGEBUNG — die Diagnose der vorigen Stufe stimmt im Ergebnis, aber nicht in der Ursache: Die 24 nicht startenden Pruefer scheitern NICHT an fehlendem Netz oder fehlender Beschaffbarkeit. `pip3 install` funktioniert hier ueber den Agent-Proxy. Drei Befehle genuegten, alle kostenfrei aus dem oeffentlichen Paketindex: `pip3 install python-telegram-bot cffi cryptography` und `pip3 install --ignore-installed PyJWT claude-agent-sdk==0.2.127 python-dotenv`. Zwei Stolpersteine, die eine naive Installation abbrechen lassen: (a) das Debian-eigene `cryptography` bricht ohne `_cffi_backend` mit einem pyo3-PanicException ab, (b) `pip install -r requirements.txt` stirbt an "Cannot uninstall PyJWT 2.7.0, RECORD file not found" — beides mit `cffi` bzw. `--ignore-installed PyJWT` erledigt. Danach liefen beide zuvor blockierten Pruefer meiner Gruppe (test_stall_5_18.py, test_linkinbox_5_14.py) gruen durch, und der bot.py-Selbstcheck war ueberhaupt erst messbar. Fuer die naechsten Stufen heisst das: "startet nicht" ist kein Grund, eine Datei zu ueberspringen.

AUSGANGSZUSTAND, vor jedem Eingriff gemessen (die Regel "erst Baseline, dann entkernen" hat sich gelohnt): test_zielumgebung.sh 21/21 gruen · test_zustellwaechter.py 9/9 · test_channels_6.py 7/7 · test_hermetik.py gruen · test_stall_5_18.py gruen · test_linkinbox_5_14.py 12/12 · bot.py-Selbstcheck 27/31, ROT in vier Zeilen aus reinen Umgebungsgruenden (MEMORY.md fehlt · ffmpeg/ffprobe fehlen · whisper-Modell fehlt · "Repo NUR-LESEN (8.7): Schreibmuster nicht erkannt: cd /tmp/entkern-2 && git commit -am x" — letzteres, weil der Pruefer den Repo-Pfad fest annimmt und meine Kopie anders heisst). Diese vier habe ich als bekannt-rot abgezogen und NICHT als Pruefobjekte genommen; die 27/31 sind ueber alle Eingriffe hinweg konstant geblieben, das ist der Beleg, dass die gemeldete Gruenfaerbung nicht von einer Nebenwirkung stammt. Den Selbstcheck habe ich ueber ein eigenes Startskript gefahren (/tmp/entkern-2/_selfcheck_runner.py), das nur die Umgebungsvariablen setzt und `bot.run_self_check()` aufruft — kein Eingriff in den geprueften Code.

WAS ICH NICHT GESCHAFFT HABE. Gemessen sind 19 der 99 Pruefzeilen der Gruppe. Vollstaendig ungemessen blieben: scripts/test_channels_6.py (7 Zeilen — gelesen, sie sind durchgehend ausfuehrend und arbeiten auf echten Zustands-Dicts; ich habe sie deshalb hinten angestellt, aber gemessen habe ich sie nicht, und ungemessen zaehlt nicht) sowie 15 der 16 Zeilen von test_stall_5_18.py, 10 der 12 von test_linkinbox_5_14.py, 7 der 9 von test_zustellwaechter.py, 18 der 21 von test_zielumgebung.sh und 24 der 31 Selbstcheck-Zeilen. Aus dem Selbstcheck ungemessen und nach Aktenlage verdaechtig, weil quelltextlesend: "Voice-Eingangsschutz (5.2)" (getsource(on_voice) mit Index-Vergleich und `src.count(...) >= 4` — eine Zaehlung, die eine Zusammenfassung der Abbruchzweige in ein try/finally faelschlich rot faerben wuerde), "Modellzeile in /status (⑬)" (getsource(cmd_status)), "Grosse Dateien (5.34)" (read_text auf ein Pruefskript), "Emoji-Reaktionen (5.9)" (teils getsource(send_answer_to_user)) und "Repo NUR-LESEN (8.7)" (getsource(make_permission_callback)) — letzteres ist die Governance-Zeile 8.7 und waere in einer Umgebung mit passendem Repo-Pfad der wichtigste noch offene Posten der Gruppe.

RUECKWEG. Das Original /home/user/claude-telegram-bot wurde ausschliesslich gelesen; `git status --porcelain` dort ist leer, bot.py unveraendert (md5 d8d86150a208704ffb40c171bcdac2ba). Alle Eingriffe fanden in /tmp/entkern-2 statt (angelegt per `git archive HEAD | tar -x`, eigener git-Baseline-Commit), nach jeder Messung mit `git checkout -- . && git clean -fd` zurueckgesetzt. Kein Netzabruf ausser den Paketinstallationen, keine Kostenquelle. Die vorab notierten Erwartungen stehen unveraendert in /tmp/entkern-2/_erwartungen.md.

### bot.py:7311 — Selbstcheck-Zeile "jeder Wächter wird auch gestartet"
**Schwere:** gruen-geblieben

**Behauptet:** Der Docstring sagt es woertlich: geprueft werde "nicht, ob die Funktionen da sind, sondern ob post_init sie RUFT — die einzige Stelle, an der aus einer geschriebenen Schleife ein laufender Waechter wird".

**Eingriff:** In post_init (bot.py:7788) wurde der Start des Zustell-Waechters auskommentiert: `app.create_task(zustell_worker(app), name="zustellung")` -> `# vorerst aus (Debug 24.08.): app.create_task(zustell_worker(app), name="zustellung")`. Der Waechter, der meldet, ob Telegram uns ueberhaupt noch erreicht, laeuft danach nie an.

**Ergebnis:** GRUEN. Selbstcheck unveraendert 27/31 (dieselben vier umgebungsbedingten Rotmeldungen wie im Ausgangszustand), Zeile "✓ jeder Waechter wird auch gestartet". Zusaetzlich gemessen: auch scripts/test_zustellwaechter.py blieb vollstaendig gruen (9/9). Ursache: die Mengenbildung ist korrekt, aber die Zugehoerigkeitspruefung ist eine Textsuche `f"{n}(app)" not in start` — der Name steht weiter im Kommentar.


### bot.py:7079 — Selbstcheck-Zeile "Session-Wächter (5.18)"
**Schwere:** gruen-geblieben

**Behauptet:** "greift nur, wenn ALLE drei Teile stehen: das Lebenszeichen im Antwortstrom, die Pruefschleife, und ihr Start. Fehlt eines davon, ist der Waechter still weg." Die zustaendige Zusicherung: `assert "stall_watchdog" in inspect.getsource(post_init)`.

**Eingriff:** In post_init (bot.py:7782) wurde `app.create_task(stall_watchdog(app), name="stall_watchdog")` auskommentiert. Der Waechter gegen haengende Sitzungen wird nicht mehr angeworfen — genau der Zustand vom 23.06. (Bot lebt, Session tot).

**Ergebnis:** GRUEN, Selbstcheck 27/31, Zeile "✓ Session-Waechter (5.18)". Auch scripts/test_stall_5_18.py blieb gruen — er ruft `bot.stall_watchdog(None)` selbst auf und misst deshalb nie, ob jemand ihn startet.


### bot.py:7059 — Selbstcheck-Zeile "Zustellnachweis + TTS-Fallback"
**Schwere:** gruen-geblieben

**Behauptet:** Der Kommentar davor nennt den Schaden: "Faellt er auf 'gibt nichts zurueck' zurueck, haelt _run_job jeden Sendefehler wieder fuer Erfolg und hakt die Nachricht ab (Verlust vom 19.07.)".

**Eingriff:** In _run_job (bot.py:1953) `delivered = False` -> `delivered = True`. Der nachlaessige Griff gegen einen vermeintlichen Fehlalarm. Wirft send_answer_to_user eine Ausnahme, gilt die Nachricht jetzt wieder als zugestellt, der Zweig "fehler" wird nie erreicht, _notify_job_failed entfaellt — der Verlust vom 19.07. ist zurueck.

**Ergebnis:** GRUEN, Selbstcheck 27/31, Zeile "✓ Zustellnachweis + TTS-Fallback". Gemessen wurde zusaetzlich die ganze Gruppe: test_stall, test_linkinbox, test_zustellwaechter, test_channels_6, test_hermetik, test_zielumgebung — alle sechs gruen. Der Pruefer misst Signatur-Annotation und Quelltext-Stichworte, nie die Auswertung des Rueckgabewerts.


### bot.py:7604 — Selbstcheck-Zeile "Medien-Eingangsschutz (5.2)"
**Schwere:** gruen-geblieben

**Behauptet:** "Medien werden VOR dem Download gesichert. Wie beim Voice-Schutz ist die Reihenfolge die Funktion" — je einzeln fuer Foto, Video und Datei (die Geschwister-Regel).

**Eingriff:** Der Rumpf von _media_eingang (bot.py:9373) wurde auf `return None` gekuerzt; Docstring und alle drei Aufrufstellen in on_photo/on_video/on_document bleiben unveraendert stehen. Kein Medienbeitrag wird beim Eingang mehr gesichert — das Fenster, in das am 25.07. ein Video fiel, ist wieder offen, und mit H1 ist es laenger als damals.

**Ergebnis:** GRUEN, Selbstcheck 27/31, Zeile "✓ Medien-Eingangsschutz (5.2)". Der Pruefer sucht `"_media_eingang(" in src` und vergleicht Zeichenketten-Indizes im Quelltext der Handler; ob die gerufene Funktion noch etwas tut, misst er nicht.


### bot.py:7492 — Selbstcheck-Zeile "Tastatur kennt den Nutzer (B3)"
**Schwere:** gruen-geblieben

**Behauptet:** "Jeder _main_keyboard-Aufruf muss user_id mitgeben" — und ausdruecklich: "Geprueft wird ueber den Syntaxbaum, nicht ueber ein Textmuster." Genau die Bauform, die die Projektregel vom 22.08. als tragfaehig nennt.

**Eingriff:** An einer der siebzehn Aufrufstellen (bot.py:8600) `user_id=user_id` -> `user_id=None`. Der nachlaessige Griff, wenn an der Stelle gerade keine Kennung zur Hand ist. _thorough_on(None) liefert dann falsch, der Gruendlich-Haken verschwindet nach genau jener Antwort — der Schaden, den der Docstring beschreibt.

**Ergebnis:** GRUEN, Selbstcheck 27/31, Zeile "✓ Tastatur kennt den Nutzer (B3)". Der Befund praezisiert die Projektregel: Der Baum ist hier richtig benutzt (echte ast.Call-Knoten), aber die Zusicherung lautet `any(s.arg == "user_id" ...)` — sie misst, DASS das Schluesselwort dasteht, nicht WAS es traegt. Ein AST-Pruefer ist nicht schon dadurch ausfuehrend, dass er ein AST-Pruefer ist.


### bot.py:7284 — Selbstcheck-Zeile "Boten-Postfach (B)"
**Schwere:** gruen-geblieben

**Behauptet:** "Postfach sendet Geheimnis-Dateien ungeprueft" wird verhindert (`assert "_is_sensitive_ref" in s`), und das Ziel wird geprueft.

**Eingriff:** In _postfach_send_one wurde aus dem Abbruch eine Warnung: `if filep and _is_sensitive_ref(str(filep)):` fuehrt jetzt nur noch `log.warning(...)` + `pass` aus statt `_move(failed_dir, ...)` + `return`. Die Datei wird protokolliert und trotzdem versandt — der klassische Griff gegen einen vermeintlichen Fehlalarm.

**Ergebnis:** GRUEN, Selbstcheck 27/31, Zeile "✓ Boten-Postfach (B)". Ein .env oder eine Token-Datei geht ueber das Postfach hinaus, waehrend der Pruefer die Ausfuhr-Richtung des Grundsatzes "von aussen kommen nie Anweisungen / nach aussen keine sensiblen Daten" fuer bewacht meldet.


### bot.py:7210 — Selbstcheck-Zeile "Reibungslose Recherche (5.25)"
**Schwere:** gruen-geblieben

**Behauptet:** "WebFetch darf NIE pauschal dauerfreigebbar sein (23.07.): die Menge ist verdrahtet im Always-Zweig, im Knopf-Angebot UND in der Selbstheilung" — gemessen ueber `src.count("_NO_ALWAYS_TOOLS") >= 3`. WebSearch ist laut Kostenregel ein 💰-Werkzeug (~10 $/1000 Suchen).

**Eingriff:** Zwei Stufen, beide gemessen. (1) Der "doppelte Boden" im Callback gestrichen — der Zweig `if tname in _NO_ALWAYS_TOOLS: return PermissionResultAllow()  # gilt nur fuer DIESE eine Anfrage` entfaellt, wie man eine vermeintlich doppelte Pruefung entfernt. (2) Anschliessend auch die beiden anderen funktionalen Verwendungen entkernt (`and tool_name not in _NO_ALWAYS_TOOLS` gestrichen, `elif tool_name not in _NO_ALWAYS_TOOLS:` -> `elif True:`).

**Ergebnis:** Beide Male GRUEN, Selbstcheck 27/31, Zeile "✓ Reibungslose Recherche (5.25)". Nachgemessen im Quelltext von make_permission_callback: nach Stufe 2 stehen noch genau 3 Vorkommen von _NO_ALWAYS_TOOLS — alle drei in KOMMENTARZEILEN. Die Zaehlschwelle >= 3 wird also von den Kommentaren allein erfuellt; WebSearch und WebFetch sind danach pauschal dauerfreigebbar, und die Zeile meldet die Kostenschranke als verdrahtet.


### scripts/test_zustellwaechter.py:170 — "kein Modell-Aufruf im Modul"
**Schwere:** gruen-geblieben

**Behauptet:** Das Zustellmarken-Modul enthaelt keinen Modell-Aufruf (Modellfreiheit der Waechter, Kostenregel). Verdachtsliste: ClaudeSDKClient, anthropic, query(.

**Eingriff:** In zustellmarke.py eine Funktion ergaenzt, die den Grund "schoener formulieren" laesst — `import bot; return await bot.stream_response(sess, grund)`. Ein echter Modell-Aufruf, nur nicht ueber das SDK direkt, sondern ueber das ohnehin vorhandene bot-Modul.

**Ergebnis:** GRUEN, alle 9 Zeilen bestanden, darunter "✓ kein Modell-Aufruf im Modul". Die Wortliste kennt den Weg ueber das eigene Projektmodul nicht — und genau der ist der naechstliegende, weil er keinen neuen Import braucht.


### scripts/test_zielumgebung.sh:181 — "Tagescheck schreibt Befunde beim Entstehen weg"
**Schwere:** gruen-geblieben

**Behauptet:** Connis Auflage 1: "Es muss einen laufenden Mitschrieb geben, in den waehrend des Laufs geschrieben wird, und einen Trap, der ihn bei einem Abbruch sichert. Ohne beides gilt wieder: gemessen und weggeworfen."

**Eingriff:** In scripts/daily_check.sh wurde der Rumpf von `_abbruch()` auf `:` gekuerzt. `trap _abbruch EXIT`, `LAUFDATEI` und `add()/merken` bleiben woertlich stehen. Bricht der Tagescheck ab, wird nichts mehr gesichert — exakt der Zustand, den die Auflage verbietet.

**Ergebnis:** GRUEN, "== Zielumgebung: 21/21 bestanden ==", Zeile "✓ Tagescheck schreibt Befunde beim Entstehen weg". Die Zeile besteht aus drei `grep -q` auf Namen (LAUFDATEI, trap _abbruch EXIT, add(){...merken}); die Wirkung des Traps wird nie ausgeloest.


### scripts/test_zielumgebung.sh:166 — "Python-Aufrufe tragen die Bot-Umgebung"
**Schwere:** gruen-geblieben

**Behauptet:** Der belegte Fehlalarm vom 18.08.: als root zeigt Path.home() auf /root, stundenblume.py meldete taeglich grundlos "Es gibt noch keine Kette". Deshalb: "Jede Zeile, die VENVPY mit einem unserer Python-Skripte ruft, muss BOTENV tragen."

**Eingriff:** Ein alltaeglicher Aufraeum-Refaktor in daily_check.sh: `SKRIPTDIR="$(dirname "$0")"` eingefuehrt und beide stundenblume-Aufrufe umgeschrieben auf `"$VENVPY" "$SKRIPTDIR/stundenblume.py" --pruefen` bzw. `--rollen` — dabei faellt `"${BOTENV[@]}"` weg. `bash -n` sauber; der taegliche Fehlalarm vom 18.08. ist wieder da.

**Ergebnis:** GRUEN, 21/21, Zeile "✓ Python-Aufrufe tragen die Bot-Umgebung". Das Suchmuster lautet `grep -nE '\$VENVPY" "\$\(dirname' | grep -v 'BOTENV\[@\]'` — es findet nur Aufrufe in genau DIESER Schreibweise. Wer die Pfadbildung umbaut, faellt aus der geprueften Menge heraus, statt aufzufallen. (Der Pruefer verletzt damit die eigene Projektauflage "ein Pruefer darf keine Formatierung verlangen" in ihrer schaedlichen Richtung: er verlangt sie nicht, er BRAUCHT sie.)


### scripts/test_hermetik.py:41 — "N Differenzart(en) geladen, jede mit Gegenprobe"
**Schwere:** gruen-geblieben

**Behauptet:** "Der Pruefstand belegt, dass die Ladebedingung wirkt: Eine Differenzart ohne Gegenprobe wird gar nicht erst geladen" — und ueber die Gegenproben, dass jede Art eine Luecke ueberhaupt FINDEN kann ("eine Art, die nie etwas meldet, sieht sonst aus wie eine, die passt").

**Eingriff:** In scripts/differenz.py wurde eine Differenzart stillgelegt, indem sie umbenannt wurde: `festpfade_differenz` -> `festpfade_pruefung_alt` (samt Gegenprobe). Der nachlaessige Griff gegen eine als laestig empfundene Meldung — die Funktion bleibt vollstaendig im Modul stehen, wird aber nie mehr gefahren.

**Ergebnis:** GRUEN, "✓ 3 Differenzart(en) geladen, jede mit Gegenprobe" (vorher 4), "== Hermetik: bestanden ==", exit 0. Die Menge wird ueber die Namensendung `_differenz` gebildet; wer umbenennt, verlaesst die Menge. Es gibt keine Untergrenze und keinen Vergleich gegen einen frueheren Stand — die gemeldete Zahl schrumpft still. Betroffen ist ausgerechnet die Art, die ortsabhaengige Festpfade findet.


### scripts/test_linkinbox_5_14.py:192 — "kein Netzabruf im Modul"
**Schwere:** gruen-geblieben

**Behauptet:** "Nachweis statt Vertrauen: Das Modul oeffnet keine Verbindung." Verdachtsliste: requests, urllib.request, urlopen, httpx, socket, aiohttp.

**Eingriff:** In linkinbox.py eine Funktion `_echten_titel_holen(url)` ergaenzt, die den Seitentitel ueber `http.client.HTTPSConnection` holt — der naechstliegende Griff aus der Standardbibliothek, wenn jemand echte Titel statt Behelfstitel will.

**Ergebnis:** GRUEN, alle 12 Zeilen bestanden, darunter "✓ kein Netzabruf im Modul". http.client steht nicht auf der Liste — und keine Wortliste kann vollstaendig sein. Die Zeile misst die Schreibweise des Abrufs, nicht seine Abwesenheit.


### scripts/test_linkinbox_5_14.py:182 — "Erfolg hakt ab, Misserfolg nicht (S1)"
**Schwere:** gruen-geblieben

**Behauptet:** Der Docstring sagt es ausdruecklich: "Der Pruefer sitzt am VERHALTEN, nicht am Wortlaut." Bewacht wird, dass nur ein belegter Erfolg einen Link abhakt.

**Eingriff:** In _links_nachtragen (bot.py) wurde im Misserfolgs-Zweig zusaetzlich `await asyncio.to_thread(linkinbox.abhaken, url, "aufgeraeumt")` direkt hinter das `notieren` gesetzt — der Griff eines Erbauers, den liegenbleibende Eintraege stoeren. Ein gescheiterter Lauf loescht jetzt die Links, die er nicht ausgewertet hat.

**Ergebnis:** GRUEN, 12/12, Zeile "✓ Erfolg hakt ab, Misserfolg nicht (S1)". Drei der vier Zusicherungen sind Textsuchen in bot.py (`"linkinbox.abhaken" not in kopf`, `"links_abhaken=" in kopf`, `'outcome == "beantwortet"' in nach`, `"notieren" in nach`) — alle vier Zeichenketten stehen unveraendert da. Nur die vierte Zusicherung fuehrt aus, und sie prueft `linkinbox.notieren` im Modul, nicht den Pfad in bot.py. Der Docstring behauptet also genau das Gegenteil dessen, was die Zeile tut.


### bot.py:7406 — Selbstcheck-Zeile "Register-Vollständigkeit (R2)"
**Schwere:** zu-eng

**Behauptet:** "Module und Betriebsskripte muessen im Register namentlich vorkommen" (Regel 3 der Bezugs-Integritaet).

**Eingriff:** Ein neues Wurzelmodul `neu_modul.py` angelegt und versioniert (git add), ohne Zeile in ABHAENGIGKEITEN.md — der Alltagsfall beim Bau eines neuen Bausteins.

**Ergebnis:** GRUEN, Zeile "✓ Register-Vollstaendigkeit (R2)". Erwartungsgemaess: die Modul-Haelfte ist eine fest verdrahtete Siebenerliste (channels/media/pending/presend/reactions/ampel/transcribe) und erfasst 7 von 18 Wurzelmodulen. Kein Widerspruch zum eigenen Docstring — der ist seit dem 23.08. ehrlich —, aber die Zeile traegt den bewachten Fall nicht und darf nicht als sein Waechter zitiert werden.


### bot.py:7463 — Selbstcheck-Zeile "Differenzen (Mengen statt Aufzählungen)"
**Schwere:** zu-eng

**Behauptet:** Der Docstring: "Er hat beide Richtungen gemessen — neues Modul ohne Zeile rot, Zeile eines vorhandenen entfernt rot" und schliesst laut CLAUDE.md die Luecke "Modul Nummer 19".

**Eingriff:** Neues Wurzelmodul `neu_modul.py` ohne Register-Zeile — einmal ununversioniert (nur angelegt), einmal nach `git add`.

**Ergebnis:** Zwei verschiedene Farben, deshalb der Befund: UNVERSIONIERT bleibt die Zeile GRUEN ("✓ Differenzen"); erst NACH `git add` wird sie ROT ("✗ Differenzen: Wurzelmodule ohne Tabellenzeile in ABHAENGIGKEITEN.md: neu_modul.py", Selbstcheck 26/31). Ursache gemessen: `_versionierte_wurzelmodule()` bildet die Ist-Menge aus `git ls-files *.py`. Zwischen dem Anlegen eines Moduls und seinem Staging ist die Zeile blind — und die Projektregel sagt "vor jedem git commit laeuft regressionstest.sh", also genau in diesem Fenster.


### scripts/test_zustellwaechter.py:168 — "der Schlüssel taucht NIRGENDS auf (vier Wege)"
**Schwere:** in-ordnung

**Behauptet:** Bot-Schluessel und Telegram-Adresse entkommen weder in den Befundtext noch in die Marke auf der Platte.

**Eingriff:** `zustellmarke.saeubern()` auf `return text` gekuerzt — das nachlaessige "das brauchen wir hier nicht".

**Ergebnis:** ROT, und die richtige Zeile: "✗ der Schluessel taucht NIRGENDS auf (vier Wege): der Schluessel steht in der Marke!", Gesamtergebnis "❌ 1 Zustell-Pruefung(en) fehlgeschlagen". Der Pruefer fuehrt den Pfad aus. Gegenkontrolle bestanden.


### scripts/test_zielumgebung.sh:54 — "kein ungeschuetztes $HOME: daily_check.sh"
**Schwere:** in-ordnung

**Behauptet:** Der belegte Vorfall vom 29.07.–18.08. (einundzwanzig Tage stiller Tagescheck-Tod) wird gefunden: bares $HOME in einem Skript mit set -u.

**Eingriff:** `LOGDIR2="$HOME/logs"` als Zeile 20 in scripts/daily_check.sh eingefuegt — die Zeile, die es damals wirklich gab.

**Ergebnis:** ROT und praezise: "✗ kein ungeschuetztes $HOME: daily_check.sh: 20:LOGDIR2=\"$HOME/logs\" — als root-Dienst ist HOME leer, set -u bricht ab". Die fuenf anderen Skripte blieben korrekt gruen. Gegenkontrolle bestanden.


### scripts/test_zielumgebung.sh:88 — "startet ohne HOME: daily_check.sh"
**Schwere:** in-ordnung

**Behauptet:** Der Start mit `env -i` misst, ob das Skript an einer fehlenden Variablen stirbt — die eigentliche Messung in der Zielumgebung.

**Eingriff:** Derselbe Eingriff wie zuvor (bares $HOME in daily_check.sh).

**Ergebnis:** ROT, unabhaengig von der grep-Zeile: "✗ startet ohne HOME: daily_check.sh: scripts/daily_check.sh: line 20: HOME: unbound variable". Gesamt 19/21. Zwei verschiedene Zeilen finden denselben Fehler auf zwei verschiedene Arten — die eine liest, die andere STARTET. Das ist die Bauform, die die Regel vom 22.08. meint, und sie ist in dieser Gruppe die einzige Stelle, an der sie sauber durchgehalten ist.


### scripts/test_stall_5_18.py:66 — "wartende Freigabe schützt die Session vor dem Wächter"
**Schwere:** in-ordnung

**Behauptet:** Solange eine Freigabe von Adam aussteht, ist Stille gewollt — der Stall-Waechter darf die Sitzung nicht abraeumen.

**Eingriff:** In stall_watchdog (bot.py:6624) `if sess is not None and sess.pending_permissions:` -> `if False:` — der Schutzzweig faellt weg.

**Ergebnis:** ROT, richtige Zeile: "AssertionError: FEHLER: Session trotz offener Freigabe gekillt" (test_stall_5_18.py:66). Der Pruefer baut eine echte Sitzung mit haengendem Worker und faehrt den Waechter zwei-einhalb Sekunden lang. Gegenkontrolle bestanden — dieser Pruefer misst Verhalten.


## Gruppe 3 — genau die acht dort genannten Dateien: scripts/test_reactions_5_9.py, test_vorlese_b5.py, test_mailkorpus.py, test_freigaben_9_4.py, test_update_textbefehl.py, test_session_limit_h2.py, test_wecker_a3.py, test_log_sync_quittung.py

geprüft: 20 · gefunden: 11

Umgebung: ARBEITSWEISE: /home/user/claude-telegram-bot wurde ausschliesslich gelesen (git archive). Zwei Kopien: /tmp/entkern-3 (Hauptarbeit) und /tmp/e3/claude-telegram-bot — die zweite war noetig, weil bot._is_repo_read_cmd das Repo am ORDNERNAMEN erkennt und test_update_textbefehl.py sonst grundlos rot ist (siehe Befund 11). Jede Messung lief nach dem Muster: git checkout -- . / Patchskript / Pruefer ausfuehren / Farbe + Exitcode ablesen / zuruecksetzen. Patchskripte und Vorhersagen liegen in /tmp/entkern-3/_mess/ (vorhersagen.md wurde VOR der ersten Messung geschrieben).

KORREKTUR AN DER VORSTUFE — wichtig fuer die anderen Gruppen: Die Behauptung \"24 von 40 Pruefern starten nicht (ModuleNotFoundError: telegram)\" trifft in DIESER Umgebung nicht zu. Gemessen: `python3 -c \"import telegram, claude_agent_sdk\"` laeuft durch, und alle acht Gruppe-3-Dateien starten und fuehren ihre Pruefzeilen aus — auch die sechs, die dort als \"startet nicht\" gefuehrt sind (test_reactions_5_9, test_vorlese_b5, test_mailkorpus, test_update_textbefehl, test_session_limit_h2, test_wecker_a3). Wer sich auf diese Spalte verlaesst, misst die Umgebung statt den Pruefer — in die falsche Richtung.

WAS TATSAECHLICH FEHLT: nur `rsync`. Deshalb sind in test_log_sync_quittung.py zwei Zeilen (154 \"nur Transportrelevantes gilt als ausgeschlossen\", 156 \"gleiche Lage schreibt die Quittung NICHT neu\") schon auf HEAD rot; sie taugen nicht als Gegenprobe-Objekt. Zeile 160 liess sich davon unabhaengig messen (Befund 12), Zeile 158 nicht sauber.

WAS ICH NICHT GESCHAFFT HABE: Von den 99 Pruefzeilen der Gruppe habe ich 20 gezielt entkernt und gemessen. Nicht einzeln entkernt wurden: test_reactions_5_9 (23 der 24 Zeilen — der sys.exit-Abbruch macht dort jede Messung teuer, weil je Lauf nur bis zum ersten Fehlschlag gemessen wird), test_vorlese_b5 (17 weitere; die vier gemessenen verhielten sich sauber, die Bauart ist durchgehend dieselbe), test_mailkorpus (13 weitere — darunter die beiden AST-Zeilen \"kein Ausweichzweig in die Hauptsitzung\" und \"der Bericht erreicht die Vertrauensliste nicht\", die echte ast.Call-/Name-Knoten zaehlen und deshalb als naechstes drankommen sollten), test_freigaben_9_4 (9 weitere), test_update_textbefehl (die sieben Zeilen des Vorderteils), test_session_limit_h2 (5 Erkennungs-/Parser-Zeilen), test_wecker_a3 (vollstaendig gemessen), test_log_sync_quittung (2 von 4 gemessen).

EIN BEFUND, DER UEBER GRUPPE 3 HINAUSGEHT: Der Exitcode-Befund an test_session_limit_h2.py:180 ist ein Bauart-Befund, kein Einzelfall. Ueberall dort, wo Pruefungen als \"Nachlese\" HINTER einen `if fails: sys.exit(1)`-Block gehaengt wurden, entscheidet allein ein zweiter Auswertungsblock am Dateiende darueber, ob der Regressionslauf sie ueberhaupt bemerkt — test_update_textbefehl.py hat ihn, test_session_limit_h2.py nicht. Die anderen Gruppen sollten in ihren Dateien gezielt nach `check(` NACH dem letzten `sys.exit` suchen; das ist billig zu pruefen und still im Versagen.

### scripts/test_wecker_a3.py:156 — "der Worker wartet, statt aufzugeben"
**Schwere:** gruen-geblieben

**Behauptet:** Eine beim Kontingent-Limit pausierte Warteschlange wird nach Ablauf der Pause vom Worker selbst abgearbeitet — Adams Nachricht geht nicht verloren.

**Eingriff:** In bot.py:1556-1557 die Warteschleife des echten Worker entfernt (`while mb.pausiert_bis > time.time(): await asyncio.sleep(...)`). Der Worker wartet danach gar nicht mehr und zieht die Nachricht sofort, obwohl das Kontingent leer ist.

**Ergebnis:** GRUEN geblieben. Rot wurde stattdessen Zeile 157 ("die Pause wird in Haeppchen geschlafen") — und die nur, weil mein Schnitt zufaellig auch die Zeichenkette `min(30.0` mitentfernt hat. Ursache: die Pruefzeile ruft `bot._session_worker` nie auf, sondern stellt die Warteschleife in einer eigenen `async def _lauf()` nach ("woertlich nachgestellt"). Sie misst asyncio-Semantik, nicht den Bot.


### scripts/test_wecker_a3.py:157 — "die Pause wird in Haeppchen geschlafen"
**Schwere:** falsche-zeile

**Behauptet:** Die Kontingent-Pause wird in Haeppchen geschlafen, damit ein frueher gesetzter Reset oder ein Neustart nicht ausgesessen wird.

**Eingriff:** Gegenprobe in die andere Richtung: den Schutz VOLL INTAKT gelassen und nur umgeschrieben — `min(30.0, ...)` in eine benannte Konstante gezogen (`_haeppchen_s = 30.0; min(_haeppchen_s, ...)`). Genau die Umformung, die ein Erbauer beim Aufraeumen macht.

**Ergebnis:** ROT, obwohl der Haeppchen-Schlaf unveraendert funktioniert: "die Kontingent-Pause wird nicht in Haeppchen geschlafen". Die Zeile liest `inspect.getsource` und verlangt die Zeichenkette `min(30.0` — also eine Schreibweise, nicht ein Verhalten. Sie verstoesst gegen die Projektregel "ein Pruefer darf keine Formatierung verlangen" und ist damit beides zugleich: umgehbar (Konstante behalten, Schleife loeschen) und fehlalarmierend.


### scripts/test_wecker_a3.py:161 — "hoechstens drei Weckversuche"
**Schwere:** gruen-geblieben

**Behauptet:** Adams dritte Bedingung vom 20.08.: hoechstens drei Weckversuche. Der Dateikopf sagt ausdruecklich, die drei Bedingungen wuerden hier gemessen, "damit sie nicht wieder eine Behauptung sind".

**Eingriff:** In bot.py:7680-7685 die Durchsetzung entfernt — der Block `if pending.bump_attempts(key) > _MAX_RESUME_ATTEMPTS: ... gaveup.append(r); pending.resolve(key); continue` geloescht. Die Konstante `_MAX_RESUME_ATTEMPTS = 3` blieb unveraendert stehen. Ergebnis im Betrieb: der Bot holt eine Absturz-Nachricht unbegrenzt oft nach (Startschleife).

**Ergebnis:** GRUEN geblieben — alle sechs Zeilen gruen, "Alle A3-Wecker-Tests bestanden." Die Zeile prueft `bot._MAX_RESUME_ATTEMPTS == 3`, also nur die Existenz der Zahl, nie ihre Wirkung. Genau das Muster, das CLAUDE.md fuer diese drei Bedingungen ausschliessen wollte: "harte Bedingungen im Code, keine Kommentare".


### scripts/test_wecker_a3.py:158 — "ohne Vermerk wird nichts nachgeholt"
**Schwere:** gruen-geblieben

**Behauptet:** Der Nachhol-Mechanismus beim Start (`_reconcile_pending`) erfindet ohne Vermerk nichts — Adams zweite Bedingung.

**Eingriff:** `bot._reconcile_pending` entkernt: Rumpf durch `return ""` ersetzt. Es wird nichts mehr geladen, nichts nachgeholt, nichts gemeldet — der komplette Mechanismus ist tot.

**Ergebnis:** GRUEN geblieben. Die Zeile prueft nur, dass bei leerem Vermerk-Ordner ein Leerstring zurueckkommt — das tut eine tote Funktion ebenfalls. Der Pruefer hat keine Zeile, die die Gegenrichtung misst (Vermerk vorhanden -> Job wird eingereiht).


### scripts/test_wecker_a3.py:159 — "ein offener Vermerk traegt den Status"
**Schwere:** gruen-geblieben

**Behauptet:** Dem Namen und dem Funktionsnamen `_ein_offener_vermerk_wird_nachgeholt` nach: was beim Limit auf "offen" gesetzt wurde, holt der Start automatisch nach ("die eigentliche Zusage", so der Docstring).

**Eingriff:** Derselbe Eingriff: `_reconcile_pending` gibt sofort "" zurueck, holt nichts mehr nach.

**Ergebnis:** GRUEN geblieben. Die Zeile ruft `_reconcile_pending` ueberhaupt nicht auf — sie schreibt einen Record mit `pending.record(...)` und liest ihn mit `pending.load_all()` wieder. Gemessen wird ein Datei-Roundtrip in pending.py, nicht das Nachholen. Prueferbezeichnung und Prueferinhalt fallen auseinander; zusammen mit Befund 4 ist damit Adams Bedingung 1 ("genau ein nachgeholter Lauf") vollstaendig unbewacht.


### scripts/test_wecker_a3.py:160 — "das Limit setzt Pause, Ruecklage und Vermerk"
**Schwere:** in-ordnung

**Behauptet:** Im Kontingent-Zweig stehen Pause, Ruecklage an den Kopf der Schlange und der Vermerk auf offen.

**Eingriff:** In bot.py:1855 `mb.queue.appendleft(job)` aus dem Kontingent-Zweig entfernt — die Nachricht geht beim Limit verloren.

**Ergebnis:** ROT, und die richtige Zeile: "das Limit setzt Pause, Ruecklage und Vermerk: die Nachricht geht nicht zurueck". Trotz Textsuche traegt sie hier. (Anmerkung: sie ist ueber einen 900-Zeichen-Fensterfund gebaut und damit gegen Umstellungen empfindlich, aber der gemessene Eingriff wurde gefangen.)


### scripts/test_session_limit_h2.py:134 — "Nachricht bleibt erhalten und behaelt ihren Platz"
**Schwere:** gruen-geblieben

**Behauptet:** Laut Dateikopf die eine Eigenschaft, an der alles haengt: beim Kontingent-Limit darf die Nachricht nicht verloren gehen; belegter Verlust am 24.07.

**Eingriff:** Derselbe Eingriff wie zuvor: `mb.queue.appendleft(job)` im Kontingent-Zweig von bot.py entfernt.

**Ergebnis:** GRUEN geblieben. Die Pruefzeile ruft `mb.queue.appendleft(...)` SELBST auf ("So verhaelt sich der Limit-Zweig") und behauptet danach, die Nachricht stehe vorn. Sie misst deque-Semantik. Gefangen wurde der Eingriff nur von der Nachbarzeile 135, und die ist eine reine Quelltextsuche.


### scripts/test_session_limit_h2.py:180 — "A1: Zugangsfehler legt den Auftrag zurueck, statt ihn aufzugeben"
**Schwere:** gruen-geblieben

**Behauptet:** Kippt das Token waehrend Adams Abwesenheit, ist seine Nachricht nur verzoegert, nicht fort — der Auth-Zweig legt zurueck und setzt STATUS_OPEN.

**Eingriff:** In bot.py:1828-1830 im Zweig `if is_auth_error(e):` die Zeilen `mb.queue.appendleft(job)` und `pending.set_status(..., STATUS_OPEN)` entfernt — die A1-Luecke ist damit wieder da.

**Ergebnis:** Die Zeile wird ROT ("der Auftrag wird beim Zugangsfehler NICHT zurueckgelegt — er ist fort") — aber das SKRIPT endet mit EXITCODE 0 und druckt vorher "Alle H2-Kontingent-Tests bestanden." Ursache: `check("A1: ...")` steht in Zeile 180, hinter dem einzigen `if fails: sys.exit(1)` in Zeile 137; ein zweiter Auswertungsblock am Dateiende fehlt. scripts/regressionstest.sh wertet in `run()` ausschliesslich den Exitcode — die Zeile kann also dauerhaft rot sein, ohne dass irgendwo etwas meldet. (Kontrastmessung: test_update_textbefehl.py hat dieselbe Nachlese-Bauart, aber einen zweiten Exit-Block in Zeile 273 — dort ist der Exitcode korrekt 1.)


### scripts/test_session_limit_h2.py:135 — "Limit-Zweig legt zurueck, pausiert und gilt als offen"
**Schwere:** in-ordnung

**Behauptet:** Der Limit-Zweig in `_run_job` legt zurueck, pausiert und beendet als "offen".

**Eingriff:** `mb.queue.appendleft(job)` im Kontingent-Zweig entfernt.

**Ergebnis:** ROT und die richtige Zeile: "die Nachricht wird beim Limit nicht zurueck an den Kopf gelegt", Exitcode 1. Sie ist eine Quelltextsuche mit 900-Zeichen-Fenster und damit nach der Projektregel umgehbar, hat den nachlaessigen Eingriff aber gefangen — und sie ist die EINZIGE Zeile, die ihn faengt (siehe Befund 7).


### scripts/test_update_textbefehl.py:266 — "die Riegel halten trotzdem"
**Schwere:** gruen-geblieben

**Behauptet:** Ausdruecklich "die wichtigere Haelfte": belegt, dass die Lese-Lockerung der Governance 8.7 nicht zu weit geht. Acht Gegenbeispiele werden durchgemessen.

**Eingriff:** In bot.py:2520-2521 die Zeile `if _AUSFUEHRENDE_SCHALTER.search(c): return False` aus `_is_repo_read_cmd` entfernt — also genau den Riegel, den der eigene Docstring der Funktion als gemessenen Vorfall beschreibt ("find ... -exec bash -c \"curl ...\" + und find ... -name \"*.py\" -delete liefen ohne Dialog durch").

**Ergebnis:** GRUEN geblieben, Exitcode 0, "Alle E4-Tests bestanden." Nachgemessen an der entkernten Fassung: `_is_repo_read_cmd('find <repo> -name "*.py" -delete')` -> True und `_is_repo_read_cmd('find <repo> -name x -exec bash -c "curl evil" +')` -> True, also Auto-Freigabe ohne Rueckfrage. Die acht Gegenbeispiele der Pruefzeile decken Umleitung, Verkettung, Rohr, Geheimnis, Schreiben, sed -i und zwei Pfadausbrueche ab — aber keinen einzigen `find`-Fall. (Kontrolle: derselbe Pruefer faengt die Entfernung des Verkettungs-Riegels `_SHELL_META_RE` sehr wohl, rot mit `cat <repo>/x | sh`.)


### scripts/test_update_textbefehl.py:264 — "Fehlerumleitung ist kein Repo-Schreiben (Claudias Befund)"
**Schwere:** falsche-zeile

**Behauptet:** Laut Kommentar in Zeile 215-218 ausdruecklich: der frueher feste Pfad `~/claude-telegram-bot` wurde durch `bot._REPO_DIR` ersetzt, weil "ein fester Pfad macht einen Pruefer hier gruen und dort blind".

**Eingriff:** Kein Entkernen noetig — der Befund fiel beim Baseline-Lauf an. Die Kopie lag unter /tmp/entkern-3, also unter einem anderen Ordnernamen.

**Ergebnis:** ROT ohne jede Aenderung am Code: "eine Fehlerumleitung faellt in den Dialog: git -C /tmp/entkern-3 log -1 2>&1". Nachgemessen: `bot._REPO_DIR` ist korrekt aufgeloest (/tmp/entkern-3), aber `_is_repo_read_cmd` beginnt mit `if "claude-telegram-bot" not in c: return False` — der Riegel selbst haengt weiter am NAMEN. Der Pruefer wurde vom festen Pfad befreit, die geprueft Funktion nicht; die Behauptung im Kommentar trifft also nur zur Haelfte zu. In einer zweiten Kopie unter /tmp/e3/claude-telegram-bot ist die Zeile gruen.


### scripts/test_log_sync_quittung.py:160 — "die Quittung bleibt lesbar kurz"
**Schwere:** zu-eng

**Behauptet:** "Ein Mass statt eines Gefuehls": die Ausschluss-Liste bleibt kurz genug, dass ein Mensch sie durchsieht (unter 40 Zeilen).

**Eingriff:** In scripts/log_sync.sh das `mv "$WORK/.letzter-abgleich.neu" "$WORK/letzter-abgleich.txt"` durch ein `rm -f` ersetzt — es wird ueberhaupt keine Quittung mehr geschrieben.

**Ergebnis:** GRUEN geblieben, waehrend die drei Nachbarzeilen rot wurden. `_quittung()` liefert bei fehlender Datei "", und 0 Zeilen sind kleiner als 40. Der Zeile fehlt der untere Anker: sie kann ihren Gegenstand nicht von seiner Abwesenheit unterscheiden. Fuer sich allein waere sie wertlos; sie ist nur deshalb ungefaehrlich, weil die Nachbarn den Fall fangen.


### scripts/test_reactions_5_9.py:66 (`_fail`) — betrifft alle 24 Pruefzeilen der Datei
**Schwere:** zu-eng

**Behauptet:** Der Laeufer meldet die Teilpruefungen des Reaktions-Pfads.

**Eingriff:** Den H3-Zweig in bot.py:5430-5432 entfernt (stille Quittung). Gemessen wurde dabei zugleich das Verhalten des Laeufers selbst.

**Ergebnis:** Die richtige Zeile wird rot ("👍 ohne offene Frage hat einen Modelllauf ausgeloest (H3)"), Exitcode 1 — insoweit in Ordnung. ABER: `_fail` ruft `sys.exit(1)`, und die beiden nachfolgenden Pruefungen (Zeilen 193 und 203-205) liefen danach nicht mehr. Ein Fehlschlag verdeckt hier alle spaeteren Befunde. Genau die Klasse, gegen die die uebrigen sieben Gruppe-3-Dateien in ihrem `check()` einen ausdruecklichen `except`-Zweig tragen ("Auch eine Ausnahme ist ein Befund, kein Abbruchgrund ... dieselbe Klasse wie der Tagescheck, der am 29.07. mitten im Lauf starb").


### scripts/test_freigaben_9_4.py:257 — "Geheimnisse werden abgewiesen, nicht angezeigt"
**Schwere:** in-ordnung

**Behauptet:** Leitplanke 4: Geheimnis-Bezuege erreichen den Freigabe-Kanal gar nicht erst.

**Eingriff:** `freigaben._hat_geheimnis` gibt immer False zurueck — der Filter ist aus.

**Ergebnis:** ROT und exakt diese eine Zeile: "Geheimnis-Anfrage kam durch: {'aktion': 'cat /etc/claude-telegram-bot.env'}". Alle elf Nachbarzeilen blieben gruen. Echter Verhaltenspruefer.


### scripts/test_freigaben_9_4.py:265 — "nur reversibles Gruen ist buendelbar"
**Schwere:** in-ordnung

**Behauptet:** Leitplanke 3: nur gruene Anfragen mit Rueckweg duerfen gesammelt freigegeben werden.

**Eingriff:** `freigaben.buendelbar` gibt `list(anfragen)` zurueck — alles buendelbar, auch rot und ohne Rueckweg.

**Ergebnis:** ROT und nur diese Zeile: "falsch gebuendelt: ['gelb', 'rot', 'gruen ohne Rueckweg', 'gruen mit Rueckweg']".


### scripts/test_freigaben_9_4.py:266 — "jedes Urteil erzeugt einen Protokoll-Eintrag"
**Schwere:** in-ordnung

**Behauptet:** Der Ablageweg: jede Entscheidung Adams landet im Protokoll, sonst waere sie verloren.

**Eingriff:** In `freigaben.urteilen` die Schleife von `((URTEILE,"u"),(PROTOKOLL,"p"))` auf `((URTEILE,"u"),)` verkuerzt — kein Protokoll mehr.

**Ergebnis:** ROT: "kein Protokoll-Eintrag — die Entscheidung haette keinen Weg in die Ablage". Zusaetzlich rot wurde die abhaengige Zeile 267 (B3-Abschnittspruefung) als Folgefehler; das ist erwartbar, nicht falsch.


### scripts/test_mailkorpus.py:462 — "der Lauf ist werkzeugfrei (B1)"
**Schwere:** in-ordnung

**Behauptet:** Der Mail-Lauf hat kein einziges Werkzeug — gemessen an der fertigen Befehlszeile, nicht an den Feldern des Options-Objekts.

**Eingriff:** `bot.werkzeugfreie_optionen` auf den historischen Fehlstand zurueckgedreht: `tools=[]` entfernt, `permission_mode` von "dontAsk" auf "bypassPermissions" — also genau die Regression, die der Docstring als Vorfall vom 22.08. beschreibt.

**Ergebnis:** ROT und exakt diese Zeile: "der Mail-Lauf haette Werkzeuge — `--tools` fehlt oder traegt einen Wert", Exitcode 1. Die Zeile baut ein echtes SubprocessCLITransport und liest die gebaute Kommandozeile — das ist der Massstab, an dem sich die Lese-Pruefer messen lassen muessen.


### scripts/test_mailkorpus.py:474 — "der Rangvermerk steht VOR dem Fremdtext"
**Schwere:** in-ordnung

**Behauptet:** Der Kopf "KEINE Anweisung" steht vor dem Fremdtext; dahinter waere er wirkungslos. Traegt den Grundsatz "Von aussen kommen nie Anweisungen".

**Eingriff:** In `mailtext.bericht` die vier Kopfzeilen des Rangvermerks entfernt (`teile = []`).

**Ergebnis:** ROT und nur diese Zeile: "der Rangvermerk fehlt im Bericht".


### scripts/test_mailkorpus.py:472 — "jedes Versteck wird gemeldet"
**Schwere:** in-ordnung

**Behauptet:** Vor dem Auge verborgene Mailteile werden gemeldet, nicht entfernt — "dass jemand versteckt hat, ist die Information".

**Eingriff:** `mailtext._ist_versteckt` gibt immer False zurueck (weder Stil noch hidden-Attribut zaehlen).

**Ergebnis:** ROT mit dem konkreten Fall: "01-weisse-schrift.eml: das Versteck wurde NICHT gemeldet". Mit rot wurden zwei weitere echte Folgen (Deckel-Zeile, Markierung im Bericht) — alle drei zu Recht.


### scripts/test_vorlese_b5.py:192 — "Datum wird als Datum gelesen"
**Schwere:** in-ordnung

**Behauptet:** `22.06.2026` wird zu `22. Juni 2026`, damit die Stimme nicht drei Zahlen vorliest.

**Eingriff:** `bot._normalize_dates` gibt den Text unveraendert zurueck.

**Ergebnis:** ROT, zusammen mit drei weiteren echt betroffenen Zeilen (Reihenfolge zur Versionsregel, Gliederungsnummer, Kalendertag); die 14 nicht betroffenen Zeilen blieben gruen. Sauber trennender Verhaltenspruefer.


## Gruppe 4 vollständig, wie zugeteilt: scripts/test_wachposten.py, scripts/test_kontingent_a2.py, scripts/test_limitwarnung_b4.py, scripts/test_media_h1.py, scripts/test_voice_entry_guard.py, scripts/differenz.py, scripts/test_kanal_links_6_2.py, scripts/test_pruefumgebung.py. Vollständig durchgemessen: test_pruefumgebung (5/5), differenz.py (Arten + alle 4 Gegenproben), test_media_h1 (alle 12 als Klasse). Stichproben mit Vorrang für die lesenden Zeilen: test_wachposten 5 von 25 (alle 3 klar lesenden plus 2 ausführende zur Gegenprobe), test_kanal_links 2 von 5, test_kontingent_a2 1 von 20 (die einzige lesende), test_limitwarnung_b4 1 von 15 (die entscheidende lesende), test_voice_entry_guard 2 von 9 plus die Bauart des Prüfstands.

geprüft: 34 · gefunden: 28

Umgebung: ARBEITSWEISE. Eigene Kopie unter /tmp/entkern-4 (git archive HEAD, danach git init/commit). Das Repo /home/user/claude-telegram-bot wurde ausschließlich gelesen — kein Schreiben, kein Commit, kein Push. Vor jedem Eingriff wurde die Erwartung notiert (/tmp/erw_pruefumgebung.md, /tmp/erw_differenz.md, /tmp/erw_wachposten.md, /tmp/erw_a2.md), erst danach entkernt und gemessen. Nach jeder Messung git checkout auf den Ausgangsstand.

ABWEICHUNG VON DER VORSTUFE, wichtig für die anderen Gruppen: In DIESEM Container sind python-telegram-bot UND claude-agent-sdk 0.2.127 installiert. Der Befund der Vorstufe („24 von 40 Prüfern starten nicht") gilt hier NICHT — alle acht Prüfer meiner Gruppe starteten und waren im Ausgangszustand grün. Wer die Vorstufen-Tabelle als Ausschlusskriterium liest, lässt Prüfer liegen, die messbar sind.

FEHLENDE ABHÄNGIGKEIT, gemessen: ffmpeg und ffprobe fehlen. Das ist kein Randproblem, sondern selbst ein Befund — siehe Eintrag zu test_media_h1.py: zwölf Prüfzeilen fallen still weg, und der Regressionsläufer meldet dafür ✅, weil `run()` die Ausgabe nur im Fehlerfall zeigt. rsync fehlt ebenfalls (betrifft Gruppe 3).

KOSTEN-VORFALL, den ich melden muss (Kostenregel, Abschnitt 💰 in CLAUDE.md). Bei meinem ersten Anlauf zum Wachposten-Eingriff „kein Modell im Pfad" habe ich `subprocess.run(["claude", "-p", …])` eingebaut und den Prüfer gestartet. `claude` liegt in diesem Container unter /opt/node22/bin/claude — der Aufruf ist also sehr wahrscheinlich tatsächlich gestartet und lief bis zum 120-Sekunden-Abbruch. Ich habe den Lauf beendet, auf Streuprozesse geprüft (keine mehr vorhanden) und die Messung mit einem nicht vorhandenen Binärpfad wiederholt; das gemeldete Ergebnis stammt aus dem gefahrlosen zweiten Lauf. Der Fehler war meiner: Ich habe beim Bauen eines Eingriffs, der einen Modellstart NACHSTELLEN sollte, nicht geprüft, ob er ihn AUSLÖST. Falls ein Abo-Kontingent belastet wurde, ist es genau ein angebrochener Lauf.

EIN BEINAHE-FALSCHBEFUND, weil die Methode ihn abgefangen hat. Beim Wachposten-Eingriff „keine Frage ohne Wirkung" habe ich zuerst die falsche Variable verändert: `text` ist die Archivfassung, zu Adam geht `kurz` aus `_kurzfassung()`. Der Prüfer blieb grün — zu Recht. Hätte ich das als Befund notiert, stünde jetzt eine Falschaussage im Bericht. Die Vorgabe „erst aufschreiben, welche Zeile rot werden soll" hat hier gegriffen, weil sie mich zwang, dem grünen Ergebnis zu misstrauen statt es zu verbuchen.

ZÄHLWEISE, damit die Zahlen nicht mehr behaupten als sie tragen. „geprüft: 34" zählt Prüfzeilen, an denen eine Messung tatsächlich gefahren wurde; darin sind die 12 Zeilen von test_media_h1 enthalten, bei denen die Messung genau ihr Nicht-Laufen war. „gefunden: 28" zählt ebenso auf Zeilenebene und wird von denselben 12 dominiert — ohne sie sind es 16 Prüfzeilen in 13 Befunden. Die Befundliste ist die belastbare Größe, nicht die Zahl.

NICHT GESCHAFFT. In test_wachposten.py 20 der 25 Zeilen (davon 6 weitere als lesend eingestufte), in test_kontingent_a2.py 19 von 20, in test_limitwarnung_b4.py 14 von 15, in test_voice_entry_guard.py 7 von 9, in test_kanal_links_6_2.py 3 von 5. Bei differenz.py habe ich ablagen_differenz und festpfade_differenz nicht einzeln entkernt — ihre vier Gegenproben sind aber im selben Lauf mitgemessen und teilen die Bauart, für die der Befund gilt. Wer weitermisst, sollte bei test_kontingent_a2 und test_limitwarnung_b4 ansetzen: beide gelten als überwiegend ausführend, und beide haben in meiner Stichprobe von genau einer lesenden Zeile genau eine schwere Lücke gezeigt — das ist keine Grundlage für die Annahme, der Rest sei sauber.

DAS MUSTER ÜBER DIE EINZELBEFUNDE HINWEG. Von 11 gemessenen Prüfzeilen, die Quelltext lesen, waren 11 umgehbar — mit Eingriffen, die ein nachlässiger Erbauer tatsächlich macht: eine Zeile auskommentieren, einen Aufruf eine Funktion tiefer schieben, eine Liste statt einer Zeichenkette schreiben, einfache statt doppelter Anführungszeichen. Von 9 gemessenen ausführenden Zeilen wurden 9 korrekt rot. Die Projektregel vom 22.08. wird durch diese Gruppe nicht nur bestätigt, sondern verschärft: Es gab keine einzige lesende Zeile, die gehalten hat. Zwei Lücken gehen über das Muster hinaus und sind eigener Art — die Mengenbildung in test_pruefumgebung (`os.environ` UND `tempfile`), die sieben echte Prüfstände nicht erfasst, und die Gegenproben in differenz.py, die ihre Argumente injizieren und deshalb den Sammler nie berühren, obwohl sie ausdrücklich versprechen, dass „jede Art ihre Lücke findet".

### scripts/test_pruefumgebung.py:165 — „der Läufer räumt eine Wegwerf-Umgebung ein"
**Schwere:** gruen-geblieben

**Behauptet:** Der dritte Riegel prüfe auch den ersten: regressionstest.sh setze POSTFACH_DIR, FREIGABE_DIR, HORA_DIR und BLUMEN_DIR auf einen mktemp-Ordner, damit kein Prüflauf ins echte Postfach schreibt.

**Eingriff:** In scripts/regressionstest.sh die vier Zeilen 37-40 auskommentiert (`# export POSTFACH_DIR=...`). Die Wegwerf-Umgebung ist damit vollständig abgeschaltet, jeder Prüflauf schriebe in die echten Ordner. Der gesuchte Text `export POSTFACH_DIR=` steht weiter in der Datei — im Kommentar.

**Ergebnis:** GRÜN. Keine Zeile schlug an, der Prüfstand endete mit „Prüfumgebung ist dicht." Der Prüfer sucht Zeichenketten in einer Shell-Datei und unterscheidet nicht zwischen Befehl und Kommentar.


### scripts/test_pruefumgebung.py:210 — „jede Postfach-Nachricht nennt ihren Absender"
**Schwere:** gruen-geblieben

**Behauptet:** Kein Schreiber lege mehr selbst ab; jede Meldung trage ihren Absender im Dateinamen und im Inhalt. Anlass war die anonyme Nachtmeldung vom 26.07., deren Urheber über eine Stunde Suche kostete.

**Eingriff:** In scripts/hora.py den Aufruf `botenpost.legen(text, "hora")` auskommentiert und darunter wieder von Hand geschrieben: eigenes dict, eigener Dateiname aus time_ns, ohne Absender. Genau der Rückfall, gegen den der Prüfer gebaut wurde.

**Ergebnis:** GRÜN. Beide Textprüfungen umgangen: `botenpost.legen(` steht noch im Kommentar, und die verbotene Zeichenkette `json.dumps({"target_chat_id"` war nur anders geschrieben (dict-Variable statt Literal im Aufruf).


### scripts/test_pruefumgebung.py:263 — „Postfach hat eine Obergrenze je Absender (④)"
**Schwere:** gruen-geblieben

**Behauptet:** Ein Wächter dürfe nicht zur Störquelle werden. Anlass: zwei fehlerhafte Wächter schickten am 28.07. sechsundzwanzig Nachrichten, zwei pro Minute.

**Eingriff:** In bot.py:6303 `POSTFACH_GRENZE` von 5 auf 500 gesetzt — die Drossel bleibt formal da, greift praktisch nie. Ein Wächter dürfte damit 500 Nachrichten je Stunde schicken.

**Ergebnis:** GRÜN. Der Prüfer liest seine Erwartung mit `grenze = bot.POSTFACH_GRENZE` aus genau der Konstante, die er prüfen soll, und passt seine Schleife mit an. Zusatz: die Konstante ist über die Umgebungsvariable POSTFACH_GRENZE überschreibbar, der Riegel lässt sich also ohne jede Codeänderung abschalten. Gegenprobe gefahren: schaltet man die Drossel ganz ab (`if False:` in bot.py:6319), wird die Zeile korrekt rot — die Verhaltensmessung trägt, die Konstante ist der blinde Fleck.


### scripts/test_pruefumgebung.py:161 — „kein Test startet einen überlebenden Prozess ohne Ersatz"
**Schwere:** zu-eng

**Behauptet:** Kein Prüfstand dürfe Popen/start_new_session/_waechter_scharf ohne nachweisbaren Ersatz benutzen — sonst überlebt ein Prozess das Testende und schreibt danach in echte Ordner (Vorfall 26.07., 01:44).

**Eingriff:** Zwei Messungen. (a) In scripts/test_updater_haertung.py die Ersatz-Zuweisung `u._waechter_scharf = lambda …` entfernt. (b) In scripts/test_kalender_caldav.py ein echtes `subprocess.Popen(["sleep","300"], start_new_session=True)` eingebaut, ohne jeden Ersatz.

**Ergebnis:** (a) ROT, richtige Zeile, mit Nennung der Datei. (b) GRÜN. Die Menge `_testdateien()` verlangt, dass eine Datei sowohl `os.environ` als auch `tempfile` enthält; test_kalender_caldav.py enthält kein tempfile und fällt heraus. Nachgemessen: 7 der 39 test_*.py-Dateien sind für diese Zeile unsichtbar (test_blinde_flecken_b6, test_channels_6, test_hermetik, test_kalender_caldav, test_media_h1, test_nachzieher_c1, test_queue_order_5_5).


### scripts/test_pruefumgebung.py:163 — „jede Prüfung setzt ihre schreibenden Ordner hart"
**Schwere:** zu-eng

**Behauptet:** In einem Prüfstand sei JEDES os.environ.setdefault falsch, weil es im Zweifel den echten Wert erbt und die Hermetik aufhebt (Anlass: geerbtes ALLOWED_USER_IDS, 12/14-Fehlalarm vom 25.07.).

**Eingriff:** Dasselbe setdefault (`os.environ.setdefault("POSTFACH_DIR", "/home/user/echt/outbox")`) zweimal eingebaut: einmal in scripts/test_kanal_links_6_2.py (enthält tempfile), einmal in scripts/test_kalender_caldav.py (enthält keins).

**Ergebnis:** Erster Fall ROT mit korrekter Meldung, zweiter Fall GRÜN. Dieselbe Mengen-Lücke wie oben. Bitter an der Stelle: der Docstring der Datei argumentiert ausdrücklich gegen Mengen über Namensmuster und für Mengen über eine Eigenschaft — die gewählte Eigenschaft (`tempfile` im Text) trifft aber sieben echte Prüfstände nicht.


### scripts/differenz.py:190/233/310/483 — die vier `*_gegenprobe`, gefahren über scripts/test_hermetik.py:48 („alle Gegenproben bestanden — jede Art findet ihre Lücke")
**Schwere:** gruen-geblieben

**Behauptet:** Jede Differenzart finde eine Lücke nachweislich. Der Docstring nennt das Ladebedingung: „eine Art, die nie etwas meldet, sieht genauso aus" wie eine, die funktioniert.

**Eingriff:** Zwei Messungen, beide gegen einen belegten Ausgangsfall: ein neues versioniertes Wurzelmodul `neu_modul.py` ohne Registerzeile in ABHAENGIGKEITEN.md angelegt (ungestört meldet der Messer es korrekt als Befund). (a) `_versionierte_wurzelmodule()` auf `return set()` entkernt. (b) Ohne Eingriff, aber mit `git` außerhalb des PATH — der Sammler schluckt die Ausnahme mit `except Exception: return set()`.

**Ergebnis:** Beide Male GRÜN, und zwar doppelt irreführend: „✓ alle Gegenproben bestanden — jede Art findet ihre Lücke" plus „○ module_differenz: keine Differenz", obwohl neu_modul.py ungedeckt daliegt. Die Gegenproben injizieren `ist` und `soll` als Argumente und berühren den Sammler nie; sie messen die Mengensubtraktion, nicht die Mengenbildung. Ein entkernter oder ausgefallener Sammler ist per Konstruktion unsichtbar — leere Ist-Menge und „keine Lücke" sehen identisch aus. Gegenprobe: mit intaktem Sammler schlagen kostenzuweisung_differenz und module_differenz beide korrekt an.


### scripts/test_wachposten.py:254 — „die Zurückhaltung gilt für beide Quellen (Geschwister)"
**Schwere:** gruen-geblieben

**Behauptet:** Es gebe nicht mehr als einen Weg an der Ampel-Zurückhaltung vorbei; die Zurückhaltung hänge an der Meldezeile, gelte also für Fehlerdatei UND Gespräch.

**Eingriff:** In scripts/wachposten.py in `lauf()` einen zweiten Ausgabeweg gebaut: Quellen mit Endung .md werden roh mit vollem Wortlaut ausgegeben, nur die übrigen laufen durch `_melde_zeile`. Gesprächsinhalte gehen damit an der Ampel vorbei hinaus.

**Ergebnis:** GRÜN — und der gesamte Prüfstand mit, alle 25 Zeilen, Rückgabewert 0. Der Prüfer misst `code.count("_melde_zeile") >= 2`; gezählt werden Definition plus verbliebener Aufruf, also weiter 2. Der Schwellwert ist ohnehin schon durch die Definitionszeile plus einen einzigen Aufruf erfüllt — die behauptete Aussage „beide Quellen" wird nie gemessen. Zugleich greift die Verhaltenszeile „bei Ampel-ROT kein Wortlaut" hier nicht, weil sie `_melde_zeile` direkt prüft und nicht `lauf()`.


### scripts/test_wachposten.py:256 — „kein Modell im Pfad (AGB, Kosten null)"
**Schwere:** gruen-geblieben

**Behauptet:** Der Wachposten sei deterministisch, kein Anthropic-Aufruf, Kosten null — das sei die Bedingung gewesen, unter der er überhaupt gebaut wurde.

**Eingriff:** In scripts/wachposten.py vor dem Zusammenbau der Meldung einen Modellaufruf eingebaut: `subprocess.run(["claude", "-p", …])`, das Ergebnis wird als Meldungstext verwendet. (Ausgeführt mit einem nicht vorhandenen Binärpfad, damit kein echter Lauf startet — siehe Umgebungsbericht.)

**Ergebnis:** GRÜN, und der ganze Prüfstand mit (Rückgabewert 0). Der Prüfer sucht die Zeichenketten "ClaudeSDKClient", "anthropic", "claude -p", "litellm". `subprocess` nimmt aber eine Liste, und `["claude", "-p"]` enthält die Zeichenkette "claude -p" nicht. Die Kosten- und AGB-Leitplanke wird von der naheliegendsten Schreibweise umgangen, die ein Erbauer überhaupt wählen kann.


### scripts/test_wachposten.py:545 — „der Knopf startet kein Modell"
**Schwere:** gruen-geblieben

**Behauptet:** Die Behandlung der Schaltfläche starte keinen Modelllauf — keine Sitzung, keine Warteschlange, kein Agent. Sonst wäre die stille Quittung von hinten wieder ausgehebelt.

**Eingriff:** In bot.py eine Hilfsfunktion `_knopf_nacharbeit()` angelegt, die `enqueue(...)` mit einem Auftragstext ruft, und sie aus `on_postfach_knopf` heraus aufgerufen. Jeder Tipp auf den Knopf startet damit einen Modelllauf.

**Ergebnis:** GRÜN. Der Prüfer liest per `inspect.getsource` genau zwei Funktionen (`on_postfach_knopf`, `_wachposten_hinterlegen`) und sucht darin verbotene Namen. Ein Aufruf, der eine Zeile tiefer liegt, ist außerhalb seines Sichtfelds — der Schutz endet an der Funktionsgrenze, das Verhalten nicht.


### scripts/test_media_h1.py:38 — alle 12 Prüfzeilen (Budget, Verkleinerung, Videozerlegung, Abtastdichte, Ausschnitt)
**Schwere:** gruen-geblieben

**Behauptet:** Der Medientransport halte sein Budget ein: großes Bild wird verkleinert, Videoteile passen einzeln ins Budget, das Budget gilt je Bild und schöpft den Puffer nicht aus.

**Eingriff:** In media.py `transport_budget()` entkernt: statt `max(64*1024, int(max_buffer_bytes * _BUDGET_SHARE / _BASE64_FACTOR))` schlicht `return max_buffer_bytes * 4` — der Budget-Deckel ist damit aufgehoben und vervierfacht.

**Ergebnis:** GRÜN, Rückgabewert 0, Ausgabe „⚠ ffmpeg/ffprobe fehlen — H1-Test übersprungen (kein Fehlschlag)". Keine der 12 Zeilen lief. Schwerer ist die zweite Hälfte: `scripts/regressionstest.sh` (Funktion `run`, Zeile 118-128) leitet die Ausgabe nach /tmp/regress_last.log um und zeigt sie NUR im Fehlerfall. Nachgestellt gemessen — der Läufer meldet „✅ Medien-Transport H1 (Bild/Video)". Der Übersprung hinterlässt im Regressionslauf keine sichtbare Spur; zwölf Prüfzeilen fallen still weg und zählen als bestanden.


### scripts/test_kanal_links_6_2.py:127 — „nur eine Stelle entscheidet"
**Schwere:** gruen-geblieben

**Behauptet:** Es gebe keinen handgebauten Kanal-Anchor mehr neben der zentralen Funktion. Der Docstring nennt den Grund: „Zwei Wege für dieselbe Sache heißt, dass einer von beiden falsch ist und niemand merkt, welcher."

**Eingriff:** In bot.py eine zweite Funktion `_kanal_zeile_html()` angelegt, die den Anchor von Hand baut: `f"<a href='{url}'>{titel}</a>"` mit `_channel_url(chat_id)`. Genau die Gabelung, die beseitigt werden sollte.

**Ergebnis:** GRÜN. Der Prüfer sucht per Regex `<a href="\{url\}"` — mit doppelten Anführungszeichen. Einfache Anführungszeichen, ein anderer Variablenname oder Zeichenketten-Verkettung genügen, um daran vorbeizukommen. Gegenprobe: die ausführende Zeile „der Titel wird maskiert" wird korrekt rot, wenn man `html.escape` in bot.py:1097 entfernt.


### scripts/test_kontingent_a2.py:438 — „kein anderer Pfad ruft die Messung"
**Schwere:** gruen-geblieben

**Behauptet:** Keine Automatik, kein Zeitgeber löse die Kontingent-Frischmessung aus; erlaubt seien genau zwei Aufrufstellen, Befehl und Schaltfläche, beide von Adams Tipp ausgelöst. Der Docstring sagt selbst: „ein Zeitgeber wäre ein AGB-Bruch".

**Eingriff:** In bot.py einen stündlichen Zeitgeber gebaut: `_kontingent_takt()` leert `_LIMIT_LETZTER` und ruft `cmd_kontingent(...)`, angemeldet über `app.job_queue.run_repeating(_kontingent_takt, interval=3600)`. Die Frischmessung läuft damit ohne Adams Zutun jede Stunde — der Schritt, den ein nachlässiger Erbauer macht, wenn er den Stand „nie alt aussehen" lassen will.

**Ergebnis:** GRÜN, der ganze Prüfstand bestanden. Der Prüfer zählt Zeilen, in denen `_kontingent_frisch_messen()` vorkommt, und verlangt genau zwei — mein Zeitgeber ruft die BESTEHENDE Aufrufstelle wieder, die Zahl bleibt bei zwei. Gezählt werden Aufrufstellen der Messung, nicht deren Auslöser; ein Zeitgeber ist damit per Bauart unsichtbar. Das ist die AGB-Leitplanke aus CLAUDE.md („reine Zeit-Trigger ohne Adams Zutun") und sie ist unbewacht.


### scripts/test_limitwarnung_b4.py:270/281 — „die Umstellung wird immer genannt, nie stillschweigend"
**Schwere:** gruen-geblieben

**Behauptet:** Der Sparmodus senke die Denktiefe nie unbemerkt. Der Docstring: „Eine Tiefe, die sich unbemerkt senkt, ist schlimmer als eine, die bleibt — man sucht den Fehler dann bei der Qualität."

**Eingriff:** In bot.py:540 die Bedingung zu `if _sparmodus_greifen(chat_id) and False:` geändert. Der Sparmodus greift weiter und senkt die Stufe, die Meldung an Adam unterbleibt — exakt der beschriebene Schadensfall.

**Ergebnis:** GRÜN, der ganze Prüfstand bestanden. Der Prüfer schneidet den Quelltextblock ab `async def _limit_warnung_melden` heraus und verlangt nur, dass die Zeichenketten `_sparmodus_greifen` und `Sparmodus greift` darin vorkommen. Beide stehen noch da — im toten Zweig.


### scripts/test_voice_entry_guard.py:38 (`_fail`) — die Bauart des ganzen Prüfstands, 9 Prüfzeilen
**Schwere:** zu-eng

**Behauptet:** Der Prüfstand messe neun Eigenschaften des Voice-Eingangsschutzes: Platzhalter nicht nachholen, normale Nachricht schon, Meldung mit Dauer und Verbleib, Eintrag auflösen, Abbruchzweig aufräumen, kein Wiederbeleben durch Audio-Nachtrag.

**Eingriff:** Zwei Schutzstellen gleichzeitig entkernt: in bot.py:7665 die Voice-Weiche in `_reconcile_pending` so geändert, dass der Platzhalter wieder nachgeholt wird, UND in bot.py:1485 `pending.resolve(key)` in `_resolve_voice_stage` durch `pass` ersetzt.

**Ergebnis:** Nur EIN Befund gemeldet („Platzhalter wurde nachgeholt"), Rückgabewert 1 — der zweite blieb still, weil `_fail()` mit `sys.exit(1)` sofort abbricht. Gegenprobe: entkernt man nur die zweite Stelle, wird sie korrekt gefunden. Die Zeilen sind also nicht blind, aber der erste Befund maskiert alle acht folgenden. Genau die Klasse, die die übrigen Prüfstände in ihrem `check()` ausdrücklich vermeiden („Auch eine Ausnahme ist ein Befund, kein Abbruchgrund" — Lehre vom Tagescheck, der am 29.07. mitten im Lauf starb).


### scripts/test_pruefumgebung.py:263 — Verhaltensteil derselben Zeile (Gegenprobe)
**Schwere:** in-ordnung

**Behauptet:** Über der Grenze wird zurückgehalten, gezählt und in einer Sammelmeldung genannt; ein zweiter Absender hat seinen eigenen Topf.

**Eingriff:** In bot.py:6319 `if len(fenster) >= POSTFACH_GRENZE:` durch `if False:` ersetzt — die Drossel greift nie.

**Ergebnis:** ROT, richtige Zeile, mit sprechender Meldung („über der Grenze kam etwas durch"). Der ausführende Teil dieser Prüfzeile trägt.


### scripts/test_pruefumgebung.py:210 — Verhaltensteil derselben Zeile (Gegenprobe)
**Schwere:** in-ordnung

**Behauptet:** Der Absender steht im Dateinamen der Postfach-Datei.

**Eingriff:** In botenpost.py den Dateinamen von `f"{absender}-{marke}.json"` auf `f"{marke}.json"` gekürzt.

**Ergebnis:** ROT, richtige Zeile, mit Pfadangabe. Der ausgeführte Teil greift — blind ist nur der lesende Teil über die Schreiber-Module.


### scripts/test_wachposten.py:252/253 — „bei Ampel-ROT kein Wortlaut, nur das Label" und „Ampel-Ausfall zählt als ROT"
**Schwere:** in-ordnung

**Behauptet:** Bei roter Einstufung werde nur das Kategorien-Label gezeigt, nie der Wortlaut; ein Ausfall der Ampel zähle als Rot.

**Eingriff:** In scripts/wachposten.py im Rot-Zweig von `_melde_zeile` die Zurückhaltung entfernt und stattdessen `f"({etikett}) {zeile}"` zurückgegeben.

**Ergebnis:** ROT, beide Zeilen, mit der ausgegebenen Meldung im Fehlertext. Verhaltensmessung, sie trägt.


### scripts/test_wachposten.py:550 — „keine Frage ohne Wirkung (Adams Regel 20.08.)"
**Schwere:** in-ordnung

**Behauptet:** Adams Meldung ende nicht auf eine wirkungslose Frage; „Engywuck wecken?" dürfe nicht wiederkehren.

**Eingriff:** Zwei Anläufe. Erst „Engywuck wecken?" an die Variable `text` in `lauf()` angehängt — das ist aber die Archivfassung; zu Adam geht `kurz` aus `_kurzfassung()`. Dann an der richtigen Stelle, am Ende von `_kurzfassung()`, angehängt.

**Ergebnis:** Erster Anlauf grün — zu Recht, mein Eingriff war unwirksam und wäre als Falschbefund in den Bericht gewandert, hätte ich nicht nachgesehen, was tatsächlich hinausgeht. Zweiter Anlauf ROT, richtige Zeile, mit Wortlaut. Die Zeile trägt.


### scripts/differenz.py:154/202 — kostenzuweisung_differenz und module_differenz (die Arten selbst, nicht ihre Gegenproben)
**Schwere:** in-ordnung

**Behauptet:** Keine versionierte Datei setze einen kostenpflichtigen API-Schlüssel; jedes eigene Wurzelmodul habe eine Tabellenzeile in ABHAENGIGKEITEN.md.

**Eingriff:** (a) `export ANTHROPIC_API_KEY=sk-ant-echt123` in einem eingezäunten Codeblock an README.md angehängt und versioniert. (b) Ein leeres Wurzelmodul `neu_modul.py` angelegt und versioniert, ohne Registerzeile.

**Ergebnis:** Beide ROT, richtige Zeilen, mit Datei- und Zeilenangabe (README.md:207 bzw. neu_modul.py) und brauchbarem Hinweistext. Die Arten selbst arbeiten — solange ihr Sammler arbeitet.


### scripts/test_voice_entry_guard.py:69/92 — „Platzhalter nicht nachgeholt" und „Abbruchzweig räumt den Eintrag ab"
**Schwere:** in-ordnung

**Behauptet:** Ein nie transkribierter Voice-Eintrag wird nicht als Platzhalter an Claude nachgeholt, und der Abbruchzweig räumt den Eingangs-Eintrag ab.

**Eingriff:** Beide Schutzstellen einzeln entkernt (bot.py:7665 Weiche umgedreht; bot.py:1485 `pending.resolve` durch `pass` ersetzt).

**Ergebnis:** Jeweils ROT mit der richtigen Meldung, Rückgabewert 1. Verhaltensmessungen, sie tragen — der Mangel liegt allein im Abbruchverhalten (eigener Befund oben).


## Gruppe 5 — test_stundenblumen.py, test_email_9_5.py, test_version_monitor.py, test_nachzieher_c1.py, test_erinnerungen_7_2.py, test_wartungsfenster_b3.py (genau die sechs aus der Aufteilung). 49 Entkernungen ausgefuehrt, davon 43 verschiedene Pruefzeilen getroffen.

geprüft: 43 · gefunden: 12

Umgebung: GELAUFEN IST ALLES, was ich brauchte. Entgegen der Vorstufe ('test_stundenblumen: startet nicht') starten ALLE SECHS Dateien der Gruppe 5 in dieser Umgebung und sind auf HEAD gruen: stundenblumen 31/31, email_9_5 20/20, version_monitor 17/17, nachzieher_c1 11/11, erinnerungen_7_2 9/9, wartungsfenster_b3 8/8. Der Grundzustand wurde vor jedem Eingriff gemessen, nicht angenommen. Keine der sechs braucht python-telegram-bot oder claude-agent-sdk (die tatsaechlich fehlen); test_email_9_5 versucht eine IMAP-Verbindung zu imap.example.org, faengt den Fehler aber selbst ab und prueft ihn sogar ('ein Verbindungsfehler ist keine leere Mailbox').

ARBEITSWEISE. Kopie unter /tmp/entkern-5 per 'git archive HEAD | tar -x', git init + Erst-Commit; /home/user/claude-telegram-bot ausschliesslich gelesen, nichts geschrieben, nichts committet, nichts gepusht. Kein Netzabruf, keine Kostenquelle. Reihenfolge eingehalten: fuer jeden Eingriff wurde die erwartete rote Zeile VOR dem Lauf in eine Spezifikationsdatei geschrieben (/tmp/entkern-5/_mess/spec_*.json), erst dann entkernt, ausgefuehrt und gemessen. Der Harness (/tmp/entkern-5/_mess/harness.py) setzt die Datei nach jedem Lauf zurueck und loescht __pycache__ vor jedem Start. Rohmessungen: /tmp/entkern-5/_mess/erg_*.json.

ZAHLEN. 49 Eingriffe ausgefuehrt, 43 verschiedene Pruefzeilen dabei getroffen — von rund 96 Pruefzeilen der Gruppe. Vollstaendig abgedeckt sind test_nachzieher_c1 (10 von 11), test_wartungsfenster_b3 (8 von 8) und test_email_9_5 (8 von 8, alle Sicherheitsriegel einzeln entkernt). Duenner abgedeckt: test_stundenblumen (7 von 31) und test_version_monitor (5 von 17); dort habe ich gezielt die quelltextlesenden Zeilen genommen, weil die Projektregel dort den Verdacht verortet — die uebrigen sind ungemessen und duerfen NICHT als geprueft gelten. test_erinnerungen_7_2: 5 von 9.

EIN EIGENER FEHLER, offengelegt. Bei Eingriff S7 (Schwellenkennung speicher-hinweis mit speicher-eng verschmolzen) hatte ich die falsche Pruefzeile vorhergesagt; rot wurde 'zwei Kennungen kommen beide durch' statt 'fortlaufende Zahl meldet nur EINMAL'. Der Textblock, den ich gelesen hatte, gehoerte zur Nachbarfunktion. Das ist ein Vorhersagefehler von mir, kein Befund ueber das Projekt — ich zaehle S7 als in-ordnung.

WAS DER BEFUND-STAPEL SAGT. Vier der sieben Gruen-Befunde sind EIN Muster: eine geschlossene Aufzaehlung verbotener Zeichenketten im Quelltext (Geheimniswert-Idiom, Netz-Bibliotheken, Installationsbefehl, Modell-Aufruf). Jede dieser Listen ist auf eine Schreibweise geeicht, die der eigene Code nicht benutzt — 'pip install' als zusammenhaengender Text, waehrend das Modul ueberall Argumentlisten uebergibt; 'requests'/'urlopen', waehrend socket danebensteht; 'claude_agent_sdk', waehrend das Projekt die claude-CLI fahrt. Das ist keine Nachlaessigkeit im Einzelfall, sondern eine Bauform: Verbotslisten ueber Text messen die Vergangenheit. Der Gegenentwurf steht in derselben Gruppe — test_email_9_5.py und test_wartungsfenster_b3.py fuehren den Pfad aus und wurden bei 16 von 16 Eingriffen an der richtigen Zeile rot.

### scripts/test_stundenblumen.py:488 — "nie der Wert eines Geheimnisses (C2)"
**Schwere:** gruen-geblieben

**Behauptet:** Die Anmelde-Wache prueft nur das VORHANDENSEIN eines Geheimnisses, nie seinen Wert. Zwei Textzusicherungen: 'split("=", 1)[0]' muss im Quelltext stehen, 'split("=", 1)[1]' darf nicht.

**Eingriff:** In stundenblume.py, direkt nach raus.extend(anmelde_befunde(namen)), vier Zeilen eingefuegt, die den Wert des ANTHROPIC_API_KEY aus /proc/<pid>/environ lesen und die ersten acht Zeichen in einen Befundtext legen — mit str.partition statt split. Genau das, was ein Erbauer schriebe, der zur Diagnose den Schluessel-Anfang sehen will.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine einzige rote Zeile, alle 31 Pruefungen bestanden. Direkt nachgemessen: Zusicherung 1 haelt (das [0]-Idiom steht weiter da), Zusicherung 2 haelt (kein [1]-Idiom), und der Code gibt dabei ('schluessel-anfang', 'Schluessel beginnt mit sk-ant-G') aus. Die Pruefzeile bewacht eine Schreibweise, nicht das Lesen des Wertes — jedes andere Idiom (partition, os.environ.get, dict(...)) geht durch.


### scripts/test_stundenblumen.py:501 — "kein Modell- und kein Netzaufruf im Modul"
**Schwere:** gruen-geblieben

**Behauptet:** Eine Stundenblume darf nichts Teures tun: kein Modell-Aufruf, kein Netzaufruf. Geprueft ueber fuenf verbotene Zeichenketten im Quelltext (claude_agent_sdk, anthropic, ClaudeSDKClient, requests, urlopen).

**Eingriff:** In stundenblume.py 'import socket' plus eine Funktion _erreichbar(host, port=443), die socket.create_connection() aufmacht — ein echter Netzaufruf mit einer Bibliothek, die nicht auf der Liste steht.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile. (Ein erster Anlauf wurde rot, aber aus dem falschen Grund: mein Standard-Hostname 'api.anthropic.com' enthielt das Wort 'anthropic'. Ohne dieses Wort im Code merkt die Zeile nichts.) Die Liste ist eine geschlossene Aufzaehlung — socket, http.client, ftplib, ein Netz-Aufruf per subprocess: alles faellt hindurch.


### scripts/test_erinnerungen_7_2.py:214 — "kein Modell im Pfad (AGB)"
**Schwere:** gruen-geblieben

**Behauptet:** Der zeitgesteuerte Erinnerungs-Laeufer enthaelt keinen Modell-Aufruf — das ist die AGB-Leitplanke, kein Schoenheitsfehler. Geprueft ueber vier verbotene Zeichenketten in den ausfuehrbaren Zeilen (anthropic, ClaudeSDKClient, 'query(', claude_agent_sdk).

**Eingriff:** In erinnerungen.py eine Funktion _huebscher(text) eingefuegt, die subprocess.run(["claude", "-p", ...]) aufruft, um die Erinnerungstexte vom Modell umformulieren zu lassen. Ein Modell-Aufruf ueber die CLI — genau der Weg, den dieses Projekt ohnehin ueberall benutzt.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile, alle 9 Pruefungen bestanden. Der Weg, auf dem in diesem Projekt am ehesten ein Modell gerufen wird, steht auf keiner der vier Verbotszeilen. Dritter Fall derselben Bauart in dieser Gruppe.


### scripts/test_version_monitor.py:231 — "kein Modell-Aufruf, keine Installation"
**Schwere:** gruen-geblieben

**Behauptet:** Der Update-Monitor meldet, er handelt nicht: kein Modell-Aufruf und keine Installation. Geprueft ueber fuenf verbotene Zeichenketten (ClaudeSDKClient, anthropic, 'pip install', 'npm install', 'apt install').

**Eingriff:** In version_monitor.py eine Funktion _einspielen(name) eingefuegt, die _run(["pip", "install", "-U", name]) aufruft. Die Wortfolge 'pip install' entsteht dabei nie als zusammenhaengender Text — und genau so ruft das Modul ohnehin alles auf, denn sein _run() nimmt eine Argumentliste.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile, alle 17 Pruefungen bestanden. Die Verbotsliste ist auf ein Schreibmuster geeicht, das der eigene Code an keiner Stelle benutzt.


### scripts/test_stundenblumen.py:644 — "die Verschraenkung greift in BEIDE Richtungen" (Blumen-Seite)
**Schwere:** gruen-geblieben

**Behauptet:** Die Kreuzverschraenkung zwischen Tagescheck und Belegkette wirkt in beide Richtungen. Die Blumen-Seite wird geprueft ueber: 'def tagescheck_pruefen' im Quelltext UND 'tagescheck_pruefen()' irgendwo VOR dieser Definition — also ueber das blosse Vorkommen des Namens.

**Eingriff:** Der einzige Aufruf in stundenblume.py Zeile 177 auskommentiert: '# raus.extend(tagescheck_pruefen())'. Die Wache ist damit tot, der Name steht weiter im Text.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile — auch die Nachbarzeile "Tagescheck wird von den Blumen mitbewacht" nicht, weil sie sb.tagescheck_pruefen() direkt ruft und die Verdrahtung gar nicht anfasst. Das ist woertlich der Fall, den CLAUDE.md als abschreckendes Beispiel fuehrt ("entfernt man den Aufruf und laesst eine Kommentarzeile stehen, bleibt er gruen und die Wache ist tot") — hier in der Datei, die diese Lehre dokumentiert.


### scripts/test_stundenblumen.py:644 — "die Verschraenkung greift in BEIDE Richtungen" (Tagescheck-Seite)
**Schwere:** gruen-geblieben

**Behauptet:** Dieselbe Zeile, andere Haelfte: der Tagescheck prueft die Belegkette. Geprueft ueber re.search(r"stundenblume\.py[\"']?\s+--pruefen") im Text von daily_check.sh.

**Eingriff:** In scripts/daily_check.sh Zeile 212 den Aufruf abgeklemmt: 'if false; then  # "${BOTENV[@]}" "$VENVPY" ... --pruefen'. Der Aufruf laeuft nie mehr, der Text steht als Kommentar weiter da.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile. Beide Haelften der Verschraenkung lassen sich unabhaengig voneinander stilllegen, ohne dass die Zeile, die sie bewacht, etwas merkt.


### scripts/test_stundenblumen.py:489 — "Speicher-Wache misst MemAvailable, nicht MemFree"
**Schwere:** gruen-geblieben

**Behauptet:** Die Speicher-Wache stuetzt sich auf MemAvailable, nicht auf MemFree (sonst Dauer-Alarm). Zwei Haelften: Textpruefung im Funktionsblock ('MemAvailable' muss vorkommen, 'm.get("MemFree")' darf nicht) plus vier Verhaltensmessungen mit einer _meminfo-Attrappe.

**Eingriff:** verfuegbar = m.get("MemAvailable") ersetzt durch m.get('MemFree', m.get("MemAvailable")) — MemFree wird die Hauptquelle, MemAvailable nur noch Rueckfall, geschrieben mit einfachen Anfuehrungszeichen.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile. Die Textzusicherung greift nicht, weil sie die doppelten Anfuehrungszeichen mitprueft; die vier Verhaltensmessungen greifen nicht, weil die Attrappe ueberhaupt keinen MemFree-Schluessel liefert und der Rueckfall daher immer zieht. In Produktion liefert /proc/meminfo MemFree stets — die Wache waere dort sofort Dauer-Alarm. Zur Ehrlichkeit: der schlichte Tausch (nur MemFree) WIRD rot; nur die Rueckfall-Variante schluepft durch.


### scripts/test_wartungsfenster_b3.py:174 — "(a) vormerken, sichtbar, stornierbar", Zusicherung 'Probelauf' in wf.uebersicht()
**Schwere:** zu-eng

**Behauptet:** Der Betriebsmodus des Wartungsfensters steht in der Uebersicht, die Adam per /updates sieht ('der Modus steht nicht in der Uebersicht').

**Eingriff:** In wartungsfenster.py modus = "scharf" if SCHARF.exists() else "Probelauf" fest auf "Probelauf" gesetzt. Die Uebersicht behauptet damit dauerhaft Probelauf, auch wenn das Fenster scharf ist und in derselben Nacht selbstaendig einspielt.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile, alle 8 Pruefungen bestanden. Die Zusicherung misst nur den Probelauf-Fall — den einzigen, in dem eine falsche Auskunft harmlos waere. Der scharfe Fall, in dem Adam die Anzeige braucht, wird nirgends gemessen.


### scripts/test_version_monitor.py:239 — "/updates vergleicht MIT Art, nicht der Groesse nach"
**Schwere:** zu-eng

**Behauptet:** classify() gibt die Art an den Vergleich weiter. Geprueft ueber die woertliche Zeichenkette "vm._cmp(cur, latest, kind)" im Quelltext von updater.py.

**Eingriff:** Gegenrichtung geprueft: In updater.py 'art = kind' eingefuegt und vm._cmp(cur, latest, art) gerufen — wirkungsgleich, die Art wird weiter uebergeben, nur die lokale Variable heisst anders.

**Ergebnis:** ROT, obwohl nichts kaputt ist: '✗ /updates vergleicht MIT Art, nicht der Groesse nach: classify() gibt die Art nicht an den Vergleich weiter'. Die Zeile verlangt eine Schreibweise, nicht eine Wirkung — genau das, was CLAUDE.md einem Pruefer verbietet ('er darf keine Formatierung verlangen'). Der Fehlalarm ist die Sorte, die einen Pruefer binnen einer Woche abgeschaltet bekommt. (Die richtige Richtung stimmt: laesst man die Art weg, wird dieselbe Zeile korrekt rot.)


### scripts/test_nachzieher_c1.py (ganze Datei, 11 Pruefzeilen) — Kopfzusage: 'Geprueft wird deshalb vor allem, was er ABLEHNT'
**Schwere:** zu-eng

**Behauptet:** Der Nachzieher ist der einzige Weg, auf dem eine Aenderung des Bots in eine Steuerdatei gelangt; nachzieher.py verspricht im Kopf ausdruecklich 'nachgemessen statt geglaubt' — nach dem Schreiben muss der Unterschied genau eine Zeile betreffen und die neue Zeile durch reines Ersetzen der Version aus der alten hervorgehen.

**Eingriff:** Genau diese Nachmessung in nachzieher.py entfernt: der Zeilen-Diff wird noch berechnet, aber die beiden raise-Zweige (Unterschied betrifft nicht genau eine Zeile / neue Zeile geht nicht durch reines Ersetzen hervor) sind weg.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile, alle 11 Pruefungen bestanden. Keine Pruefzeile beansprucht diesen Schutz. Dasselbe fuer die Mehrfach-Treffer-Ablehnung ('kommt mehrfach vor — von Hand klaeren'): entfernt, ebenfalls gruen. Zwei von zehn Schranken der Datei sind ungemessen; die uebrigen acht sind vorbildlich abgedeckt.


### scripts/test_wartungsfenster_b3.py (ganze Datei, 8 Pruefzeilen)
**Schwere:** zu-eng

**Behauptet:** Die Datei prueft die drei Auflagen und den Probelauf. Der Probelauf-Zaehler wird bei einem gescheiterten scharfen Lauf zurueckgesetzt (_probelauf_zaehler(False)) — ein unsauberer Lauf soll die Drei-Lauf-Frist neu starten.

**Eingriff:** In wartungsfenster.py den Aufruf _probelauf_zaehler(False) im Fehlschlag-Zweig durch 'pass' ersetzt.

**Ergebnis:** GRUEN. Rueckgabewert 0, keine rote Zeile. Kein Pruefer misst den Ruecksetzer; ein Fenster koennte nach gescheiterten Laeufen weiter als 'sauber durchgelaufen' zaehlen. Kleinerer Befund als die uebrigen, aber gemessen.


### Methodischer Befund ueber die Messung selbst (betrifft jeden, der Pruefer durch Patchen misst)
**Schwere:** falsche-zeile

**Behauptet:** Eine Messung 'Datei patchen, Pruefer starten, zuruecksetzen' misst den gepatchten Stand.

**Eingriff:** Beim ersten Durchgang der zehn nachzieher-Entkernungen ohne Loeschen von __pycache__ gemessen.

**Ergebnis:** FALSCHMESSUNG: Eingriff E6 (Gleichheitspruefung von/nach entfernt) meldete das Ergebnis des VORHERIGEN Eingriffs E5 — rot wurde '✗ Paketname mit Sonderzeichen abgelehnt' statt der erwarteten Zeile, Urteil faelschlich 'falsche-zeile'. Ursache: Python nimmt scripts/__pycache__/nachzieher.cpython-311.pyc, wenn mtime-Sekunde und Dateigroesse zufaellig uebereinstimmen. Nach Einbau eines rglob('__pycache__')-Loeschens vor jedem Lauf: Urteil 'in-ordnung', die richtige Zeile wird rot. Alle 49 Messungen dieses Berichts sind mit Cache-Loeschung gefahren. Wer diese Gegenprobe ohne das macht, erzeugt Geisterbefunde.


## Gruppe 6 wie zugeteilt, alle sieben Dateien angefasst: scripts/test_hora.py (28 Pruefzeilen) · scripts/test_auftragsbuch_b8.py (22) · scripts/test_conversation_log_rollover.py (18) · scripts/test_postfach_wiederaufgriff.py (11) · scripts/test_updater_haertung.py (9) · scripts/test_blinde_flecken_b6.py (7) · scripts/test_sendepfad_rauch.py (4). Vollstaendig durchgemessen sind test_blinde_flecken_b6.py (7/7), test_updater_haertung.py (9/9) und test_sendepfad_rauch.py (4/4); aus den vier grossen Dateien wurden 13 Zeilen einzeln entkernt und gemessen, ausgewaehlt nach Quelltext-Lesen und nach Sicherheitsgewicht. Arbeitsordner /tmp/entkern-6 (git-Kopie von HEAD 1817c86, 24.08.2026 01:33). Das Quell-Repo /home/user/claude-telegram-bot wurde ausschliesslich gelesen.

geprüft: 33 · gefunden: 10

Umgebung: EINE BERICHTIGUNG VORWEG, gemessen: Die Vorstufe meldete, 24 von 40 Pruefern starteten nicht (\"ModuleNotFoundError: No module named 'telegram'\") und es gebe kein venv. Das trifft fuer Gruppe 6 nicht zu — `python-telegram-bot` 22.8 UND `claude_agent_sdk` sind hier importierbar, und alle sieben Dateien laufen ohne Vorbereitung durch. Wer den Deckungsgrad der naechsten Stufe darauf stuetzt, stuetzt ihn auf eine Momentaufnahme einer anderen Umgebung. Was fehlt, ist `rsync` (betrifft Gruppe 3, nicht mich).

BASELINE VOR JEDEM EINGRIFF GEMESSEN, nicht angenommen: sechs der sieben Dateien sind auf HEAD gruen. test_blinde_flecken_b6.py ist ROT — echt, nicht umgebungsbedingt: vier gemischte Anfuehrungspaare in bot.py (4743, 4774, 4836, 4844). Das ist der siebte Fall derselben Klasse und steht ungefixt im Repo; er hat mir zugleich den ersten Befund geliefert, weil er Pruefzeile 7 derselben Datei totlegt.

WAS ICH NICHT GESCHAFFT HABE: In test_hora.py habe ich 1 von 28 Zeilen einzeln entkernt (die textlesende \"roter Wiederkehrer\"), in test_auftragsbuch_b8.py 7 von 22, in test_conversation_log_rollover.py 2 von 18, in test_postfach_wiederaufgriff.py 3 von 11 — zusammen 33 von 99. Die uebrigen 66 sind ungemessen; ich habe sie ausdruecklich NICHT als \"vermutlich in Ordnung\" abgelegt. Ungemessen geblieben sind vor allem die 27 restlichen Hora-Zeilen (Schloss, Leerlauf-Daempfung, Fehlgrund-Auswahl, Wiederkehr-Faelligkeit, F-2-Kuerzung) — dort lohnt die naechste Runde, weil die Datei die groesste ist und mit `hora.py`-Textlesen mindestens eine weitere lesende Stelle hat (Zeile 571 f.).

DREI DINGE, DIE ICH DER NAECHSTEN STUFE MITGEBEN WUERDE. (1) Der Zwischen-Abbruch (`sys.exit(1)` mitten in der Datei) ist in dieser Gruppe der wirksamste Blindmacher — er kostet in b8 zwoelf Waechter auf einen Schlag, darunter die drei Sicherheitszeilen der 18.08.-Gegenpruefung. Er steht in b6 (2 Stufen), b8 (3), hora (3), und die linearen Dateien haben ihn per `_fail()` ohnehin. Das laesst sich in einem Zug beheben: Befunde sammeln, einmal am Ende beenden — genau das, was der `check()`-Kommentar dieser Dateien selbst fordert. (2) Die Einordnung \"liest\" der Vorstufe zaehlt JSON-Lesen (`json.loads(p.read_text())`) als Quelltext-Lesen mit; das ist Verhaltensmessung und ueberzeichnet den Verdachtsbereich. Bei b8 und hora sind es tatsaechlich nur drei bis vier echte Quelltext-Stellen — und drei davon sind gefallen. (3) Der Postfach-Befund braucht keinen Waechter, sondern einen Fix: `bot.py:6171` wirft bei jeder gedrosselten Nachricht `KeyError: 'versuche'` und laeuft in einen `_move(failed_dir, …)`, der eine nie gescheiterte Nachricht ins Endlager schieben will. Dass sie heute liegen bleibt, ist Reihenfolge-Gunst, kein Schutz.

### scripts/test_blinde_flecken_b6.py:246 — der Zwischen-Abbruch `sys.exit(1)` vor Pruefzeile 7 ("Zeitgeber-Wache klagt keinen laufenden an")
**Schwere:** gruen-geblieben

**Behauptet:** Der Waechter meldet, wenn die Zeitgeber-Wache ihren eigenen laufenden Traeger anklagt (Fehlalarm 19.08.). Rot werden soll: "Zeitgeber-Wache klagt keinen laufenden an (Fehlalarm 19.08.)".

**Eingriff:** In scripts/daily_check.sh die SubState-Abfrage entkernt: `substate=$(systemctl show ... SubState ...)` + `if [ "$substate" = "running" ]` durch `if false; then` ersetzt.

**Ergebnis:** GRUEN geblieben — genauer: die Zeile lief GAR NICHT. Der Lauf endete nach sechs Zeilen mit dem vorhandenen Grundrot (gemischtes Anfuehrungspaar, bot.py:4743/4774/4836/4844), und `sys.exit(1)` in Zeile 246 verhinderte den siebten check(). Gegenprobe: nach Reparatur der vier Anfuehrungspaare in bot.py lief die Zeile und wurde korrekt ROT. Auf HEAD ist Pruefzeile 7 also tot, solange das Grundrot steht.


### scripts/test_auftragsbuch_b8.py:186/262 — zwei Zwischen-Abbrueche vor den Stufen 2 und 3
**Schwere:** gruen-geblieben

**Behauptet:** 22 Pruefzeilen ueber Einstufung, Riegel und Umgehungsschutz des Auftragsbuchs.

**Eingriff:** Eine einzige Zeile der ersten Stufe entkernt (in auftragsbuch.py die Rot-Wort-Suche hinter die Art-Pruefung geschoben, damit Rot nicht mehr Gruen schlaegt).

**Ergebnis:** Die richtige Zeile wurde rot, ABER: nur 11 von 22 Pruefzeilen liefen ueberhaupt (gezaehlt). Ausgefallen sind unter anderem die drei Sicherheits-Zeilen der Gegenpruefung vom 18.08. — "handgelegte Gruen-Behauptung wird nicht geglaubt", "rote Worte treffen deutsche Zusammensetzungen", "haeufige harmlose Traeger bremsen nicht" — sowie alle acht Riegel-/Uebergabe-Zeilen. Ein Fehler in Stufe 1 macht 12 Waechter unsichtbar. Dieselbe Bauart in test_hora.py (drei Stufen) und test_blinde_flecken_b6.py.


### scripts/test_blinde_flecken_b6.py — "beide Register-Auswerter melden ihre blinden Flecken (Frage ①)"
**Schwere:** gruen-geblieben

**Behauptet:** Versions-Monitor und Updater uebergehen unerreichbare Register-Quellen nicht mehr stillschweigend. Rot werden soll diese Zeile.

**Eingriff:** Zwei Eingriffe, getrennt gemessen. (a) In scripts/version_monitor.py den kompletten Meldezweig `if blind: teile.append("🕳️ Blinde Flecken im Register …")` (Zeilen 514–521) ersatzlos geloescht — die Bedingungszeile `if updates or blind:` blieb stehen. (b) In scripts/updater.py den Koerper von `blinde_flecken()` durch `return []` ersetzt.

**Ergebnis:** Beide Male GRUEN geblieben (einzige rote Zeile war das vorhandene Grundrot). Der Pruefer misst nur zwei Zeichenketten: `"if updates or blind:" in vm` und `"def blinde_flecken" in up`. Nach (a) meldet der Monitor blinde Flecken nirgends mehr; nach (b) liefert der Updater nie welche. Nebenbefund beim Nachsehen: `updater.blinde_flecken()` hat im ganzen Repo ueberhaupt keinen produktiven Aufrufer — nur test_version_monitor.py ruft es. Fabrik ja, Aufrufer nein.


### scripts/test_blinde_flecken_b6.py — "kein Träger ohne Wache — Verschränkung beidseitig (Frage ②)", Rueckrichtung
**Schwere:** gruen-geblieben

**Behauptet:** Die Verschraenkung traegt in BEIDE Richtungen: die Stundenblume bewacht den Tagescheck (ausgefuehrt), und der Tagescheck bewacht die Stundenblume (`stundenblume.py --pruefen` in daily_check.sh).

**Eingriff:** In scripts/daily_check.sh Zeile 212 den echten Aufruf `if "${BOTENV[@]}" "$VENVPY" .../stundenblume.py --pruefen …` durch `if true; then` ersetzt und den alten Aufruf als Kommentarzeile stehen lassen — genau der Eingriff, den ein nachlaessiger Erbauer macht.

**Ergebnis:** GRUEN geblieben. Der Regex `stundenblume\.py["']?\s+--pruefen` trifft die Kommentarzeile. Die Wache ist tot, der Pruefer schweigt. Bemerkenswert: der Docstring dieser Funktion beschreibt exakt diesen Fehler ("Eine Gegenpruefung hat den AUFRUF ersatzlos entfernt und eine Kommentarzeile stehen lassen") — er wurde nur fuer die VORDERE Richtung repariert. Zum Vergleich die vordere Haelfte: `tagescheck_pruefen()` auf `return []` entkernt → korrekt ROT ("ein 27 Stunden stiller Tagescheck bleibt unbemerkt").


### scripts/test_blinde_flecken_b6.py — "Kostenzahl nie ohne das Wort Nennwert (Conni 28.07.)"
**Schwere:** zu-eng

**Behauptet:** Keine Kostenzahl wird angezeigt, ohne dass das Wort "Nennwert" in ihrem Umfeld steht.

**Eingriff:** In bot.py an der Anzeigestelle 8782 ff. das Wort Nennwert entfernt UND den Zugriff von `u.get("cost_usd", 0.0)` auf `u["cost_usd"] if "cost_usd" in u else 0.0` umgeschrieben — Ausgabe bleibt `· ~$12.34`.

**Ergebnis:** GRUEN geblieben. Der Pruefer ueberspringt jede Zeile ohne `get(` (`if "get(" not in zeile: continue`). Gegenprobe zur Abgrenzung: nur das Wort entfernt, `get(` stehen gelassen → korrekt ROT mit Zeilennummer 8782. Der Waechter bewacht also eine Schreibweise des Zugriffs, nicht die Anzeige.


### scripts/test_hora.py — "ein roter Wiederkehrer rennt nicht ewig (d)"
**Schwere:** gruen-geblieben

**Behauptet:** Adams Festlegung (d): Ein wiederkehrender Auftrag, der immer wieder scheitert, wird nach einer Grenze ausgesetzt — eigener Zaehler je Auftrag, Ruecksetzung bei Erfolg.

**Eingriff:** Zwei Eingriffe, getrennt gemessen. (a) In scripts/hora.py `WIEDERKEHR_FEHLGRENZE = 3` auf `999999` gesetzt. (b) Den kompletten Zaehl- und Grenz-Zweig (Zeilen 700–711, `if wiederkehr_erlaubt(auftrag)[0]: eigen = … if eigen >= WIEDERKEHR_FEHLGRENZE: …`) durch `if False: pass` ersetzt, Konstante stehen gelassen.

**Ergebnis:** Beide Male GRUEN — rc=0, alle 28 Hora-Zeilen bestanden. Der Pruefer liest hora.py als Text und sucht drei Zeichenketten (`wiederkehr_fehler`, `WIEDERKEHR_FEHLGRENZE`, `wiederkehr_fehler=0`). Nach (b) rennt ein roter Wiederkehrer buchstaeblich ewig, und kein Waechter sagt etwas.


### scripts/test_auftragsbuch_b8.py — "die Uebergabe meldet sich ungedaempft"
**Schwere:** gruen-geblieben

**Behauptet:** Jede Gruen-Uebergabe der Probewoche meldet sich per Botenpost an Adam, mit Begruendung warum gruen. Der Docstring: "Wer sie daempft, prueft nicht die Automatik, sondern die Daempfung."

**Eingriff:** In auftragsbuch.py Zeile 368 `if gemeldet:` zu `if gemeldet and False:  # Meldung vorlaeufig gedaempft (zu viel Rauschen)` — der `botenpost.legen(...)`-Block bleibt im Quelltext stehen, wird nur nie erreicht.

**Ergebnis:** GRUEN geblieben, rc=0, alle 22 B8-Zeilen bestanden. Der Pruefer teilt auftragsbuch.py bei `def uebernehmen` und sucht `"botenpost.legen" in block`. Die Sichtbarkeit, die laut Docstring der Zweck der ganzen Probewoche ist, laesst sich mit einem `and False` abschalten, ohne dass etwas anschlaegt.


### scripts/test_auftragsbuch_b8.py — "Hora speist sich aus dem Auftragsbuch"
**Schwere:** gruen-geblieben

**Behauptet:** `uebernehmen()` hat einen Aufrufer — der Befund vom 18.08. war, dass es keinen gab und die Probewoche eine Woche gewesen waere, in der nichts geschieht.

**Eingriff:** In scripts/hora.py Zeile 570 den Aufruf auskommentiert: `# vorlaeufig aus: anzahl, meldung = auftragsbuch.uebernehmen()` und `anzahl, meldung = 0, ""` eingesetzt.

**Ergebnis:** GRUEN geblieben — sowohl test_auftragsbuch_b8.py (rc=0) als auch test_hora.py (rc=0). Der Pruefer sucht `"auftragsbuch.uebernehmen()" in hora`; die Zeichenkette steht jetzt in einem Kommentar. Der Waechter kann genau den Zustand nicht erkennen, gegen den er gebaut wurde.


### scripts/test_auftragsbuch_b8.py — "der Riegel ist eine Datei mit Frist und Kopf"
**Schwere:** zu-eng

**Behauptet:** Der Riegel der Gruen-Automatik traegt seine eigene Frist; Riegel und Probewochen-Ende sind dasselbe Dokument.

**Eingriff:** In auftragsbuch-riegel.md `GILT-BIS: 2026-08-25` auf `GILT-BIS: 2099-12-31` gesetzt — sonst nichts; der Stichtag im Kopf blieb 2026-08-18.

**Ergebnis:** GRUEN geblieben, rc=0, alle 22 Zeilen bestanden. Der Pruefer misst nur, dass die Zeichenketten `GILT-BIS:` und `Stichtag:` in der Datei vorkommen — nie, ob das Datum plausibel ist oder zum Stichtag passt. Damit laesst sich die einwoechige Probewoche der Gruen-Automatik mit einer Zeichenaenderung in einen Dauerzustand verwandeln, ohne dass ein Waechter anschlaegt. (Zur Lage: gemessen am 24.08.2026 laeuft die echte Frist morgen ab.)


### scripts/test_postfach_wiederaufgriff.py — "Gedrosseltes landet in der outbox, nicht in sent/" und "Drosselung verbraucht den Versuchszaehler nicht (Engywuck)"
**Schwere:** gruen-geblieben

**Behauptet:** Der Drossel-Pfad des Botenpostfachs stellt sauber in die outbox zurueck.

**Eingriff:** KEINER — auf unveraendertem HEAD gemessen.

**Ergebnis:** 11 von 11 Pruefzeilen GRUEN, rc=0 — waehrend der bewachte Pfad im selben Lauf 14-mal eine Ausnahme wirft: `KeyError: 'versuche'` in bot.py:6171 (`log.info("Postfach: %s zurückgestellt (Versuch %d …", orig, daten["versuche"], …)`). Im Drossel-Zweig laeuft `_zurueckstellen(..., zaehlt=False)`, das `drossel_runden` setzt und `versuche` gerade NICHT anlegt. Der `except`-Zweig greift und ruft `_move(failed_dir, ...)` — also den Weg ins Endlager fuer eine Nachricht, die nie gescheitert ist; dass sie trotzdem in der outbox bleibt, ist reine Reihenfolge-Gunst, weil `tmp.rename(outbox/orig)` zwei Zeilen frueher schon durch war. Im Protokoll steht 14-mal "postfach requeue failed" und "postfach move failed". Keine Pruefzeile sieht hin. Gegenprobe, dass die Diagnose stimmt: wird die `zaehlt`-Unterscheidung entkernt (beide Zaehler immer hochsetzen), verschwindet der KeyError — und die Zeile "Drosselung verbraucht den Versuchszaehler nicht" wird korrekt ROT.


### scripts/test_sendepfad_rauch.py — alle vier Zeilen
**Schwere:** in-ordnung

**Behauptet:** Der zentrale Sendepfad `send_answer_to_user` laeuft, auch bei aktivem Gruendlich; leerer Text ist kein Zustellfehler; keine ungebundenen Namen im Pfad.

**Eingriff:** (a) Den Originalfehler vom 28.07. wiederhergestellt: in bot.py `_main_keyboard(..., user_id=sess.user_id)` zurueck auf `user_id=user_id`. (b) Getrennt: die Leertext-Schranke `if not text: return True` entfernt.

**Ergebnis:** (a) DREI Zeilen korrekt ROT: "der Sendepfad läuft überhaupt" und "auch bei aktivem Gründlich" mit `NameError: name 'user_id' is not defined`, "keine ungebundenen Namen im Sendepfad" mit `['user_id']`. (b) genau eine Zeile ROT: "leerer Text ist kein Zustellfehler (Gegenprobe)". Diese Datei ist der Massstab der Gruppe — Attrappen am Rand, echter Code in der Mitte, jede Zeile beisst.


### scripts/test_updater_haertung.py — alle neun Zeilen A1–A7
**Schwere:** in-ordnung

**Behauptet:** Grundlinie zuerst · exakt die freigegebene Version · kein Einspielen bei Versions-Drift · Lauf-Schloss · kein Update ohne Freeze · vollstaendiger Umgebungs-Rollback · ehrliche Meldung bei unvollstaendigem Rollback · Selbst-Widerspruch aussprechen · Wiederhol-Schutz.

**Eingriff:** Neun getrennte Eingriffe in scripts/updater.py, je einer pro Zeile: Grundlinien-Ruecksprung geloescht · `_install(c["comp"], "latest")` statt der freigegebenen Version · Drift-Block geloescht · `_acquire_lock` auf `O_CREAT` ohne `O_EXCL` und ohne Altersfrage · Freeze-Fehlschlag ignoriert · `_restore_env`-Schleife zu `pass` · Rollback-Erfolg behauptet statt je Paket gemessen · `same_as_before`-Meldung geloescht · A7-Ruecksprung geloescht.

**Ergebnis:** Neun von neun Mal wurde GENAU die vorhergesagte Zeile ROT, mit passender Begruendung (z. B. "Zustand falsch: fundament_rot→rollback", "zweiter Lauf nicht abgewiesen: eingespielt", "kein vollständiger Umgebungs-Rollback (pip -r freeze) ausgeführt"). Keine Fehlanschlaege, keine stillen Nachbarn.


### scripts/test_auftragsbuch_b8.py — "Rot schlägt Grün", "Grün nur aus der geschlossenen Liste", "handgelegte Gruen-Behauptung wird nicht geglaubt", "abgelaufene/kaputte Frist schliesst den Riegel"
**Schwere:** in-ordnung

**Behauptet:** Die vier tragenden Schranken der Gruen-Automatik: Rot-Wort schlaegt harmlose Art · unbekannte Art wird nie gruen · die Ampel in der Datei ist ein Vorschlag, keine Wahrheit · ein Riegel ohne gueltige Frist ist zu.

**Eingriff:** Vier getrennte Eingriffe in auftragsbuch.py: Rot-Suche hinter die Art-Pruefung verschoben · unbekannte Art gibt `("gruen", "Art wirkt harmlos")` zurueck · in `uebernehmen()` die Neu-Einstufung `jetzt, grund = einstufen(a)` entfernt und der Datei-Ampel geglaubt (die Umgehung vom 18.08.) · `_riegel_offen()` gibt bei fehlendem GILT-BIS `(True, …)` zurueck.

**Ergebnis:** Alle vier Male korrekt ROT und mit der richtigen Begruendung: "[Token erneuern] blieb grün" · "die unbekannte Art [umbau] wurde grün" (plus drei sinnvolle Folgezeilen) · "eine handgelegte Gruen-Behauptung wurde uebergeben" · "der Riegel oeffnet sich bei [ohne Frist]". Das ist der ausfuehrende Kern der Datei, und er traegt.


### scripts/test_conversation_log_rollover.py — "Mitternacht 1: neuer Tag → neue Datei" und "alte mit Verweis"
**Schwere:** in-ordnung

**Behauptet:** Die Zieldatei des Gespraechs-Logs wird bei JEDEM Schreibvorgang aus dem aktuellen Datum bestimmt; die alte Tagesdatei bekommt eine Verweiszeile.

**Eingriff:** (a) Den Originalfehler vom 22.07. wiederhergestellt: in bot.py in `_append` den Aufruf `self._roll_if_needed()` entfernt (Pfad bleibt aus dem `__init__` eingefroren). (b) Getrennt: den Schreibblock der Verweiszeile `f.write(f"\n*→ fortgesetzt in {date_str}.md*\n")` durch `pass` ersetzt.

**Ergebnis:** (a) korrekt ROT: "neue Tagesdatei nach Mitternacht wurde nicht angelegt". (b) korrekt ROT: "Verweiszeile in der alten Tagesdatei fehlt". Randbemerkung zur Bauart: die Datei ist linear mit `_fail() → sys.exit(1)`, bei (a) liefen deshalb nur 2 der 18 Pruefzeilen — dieselbe Abbruch-Klasse wie oben, hier aber ohne eigenen Schaden, weil die richtige Zeile zuerst kam.


### scripts/test_blinde_flecken_b6.py — "die Zeitgeber-Suche ist keine Positivliste (Frage ③)", "kein Träger ohne Wache" (Vorderrichtung), "das Verfahren ist abgelegt und trägt den Gültigkeits-Kopf", "kein gemischtes Anfuehrungspaar"
**Schwere:** in-ordnung

**Behauptet:** Die vier Zeilen der Datei, die halten.

**Eingriff:** Vier getrennte Eingriffe: in daily_check.sh den ExecStart-/UNSER_PFAD-Filter durch `case "$kandidat" in claude-*|hora*|stundenblume*)` ersetzt · `stundenblume.tagescheck_pruefen()` auf `return []` · in docs/blinde-flecken-verfahren.md die Stichtag-Zeile geloescht · fuer die vierte Zeile keine Entkernung noetig, sie ist auf HEAD bereits rot.

**Ergebnis:** Drei Mal korrekt ROT mit passender Begruendung ("die Zeitgeber werden nicht am Ziel erkannt — womit dann?" · "ein 27 Stunden stiller Tagescheck bleibt unbemerkt" · "der Gültigkeits-Kopf fehlt"). Die vierte Zeile (gemischtes Anfuehrungspaar) ist auf unveraendertem HEAD ROT und benennt vier echte Stellen — bot.py:4743, 4774, 4836, 4844, jeweils `f'… „{spec["title"]}" …'`. Nach Reparatur dieser vier wird sie gruen; sie unterscheidet also sauber. Das Grundrot steht ungefixt im Repo.

