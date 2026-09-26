**Zweck: WEITERGABE → Mick** · **Zu tun: unverändert an Mick. Teil A ist Konzept (lesen, nicht bauen). Teil B ist der Bauauftrag für Stufe 2, einzureihen NACH dem Nebenfaden f2.**

# Der Dirigent — Konzept und Bauauftrag Stufe 2 „Anliegen-Sitzungen" — 26.09.2026, 18:17

**Adams Entscheide, 26.09., 18:0x bis 18:3x, per Klickfragen, im Wortlaut wo nötig:**

1. **Anliegen-Sitzungen vom Telegram-Thema lösen: ja.** Eine Sitzung je Anliegen, das Thema ist nur eine optionale Ausgabe-Adresse. Häuser und Zimmer werden Sortierung, keine Voraussetzung.
2. **Zuordnung: der Empfang, automatisch.** Bestehendes Anliegen, neues Anliegen oder Hauptchat; Adam lenkt per Knopf um. Start mit Nachfrage bei Unsicherheit, später seltener.
3. **Lebensdauer: schlafen nach Leerlauf, aufwecken bei Bezug.** Kein Verfall ohne Adams Wort.
4. **Obergrenze gleichzeitig wacher Sitzungen: 11.** Adam: *„Wir können auf jeden Fall direkt 10 eingeben … Nimm 11 … und dann misst du das bitte parallel."* Er geht davon aus, dass das Abo parallele Sitzungen nicht begrenzt; gemessen ist das nicht.
5. Reihenfolge der Stufen (Teil A): von Adam nicht gesondert entschieden, meine Empfehlung steht; er ändert sie, wenn er will.

Adams Begründung zur Entkopplung, sinngemäß: Sitzungen auf dem Server sind Code, beliebig viele; nicht jeder Dialog gehört in Telegram einsortiert; eine neue Frage ohne Zimmer darf nicht warten; die Sitzung hinter Claudia sieht er ohnehin nicht, sie wird trotzdem abgelegt.

## Teil A — Konzept in fünf Stufen (Grundlage: Stufenplan vom 26.09., Drehbuch 5.1/5.4/9.4/9.8, Entscheide 09.09.)

**Was gilt weiter (09.09.):** Vermittlerin werkzeuglos neben den Sitzungen, kein Proxy davor (F1). Der Verteiler ist Code, das Modell schätzt ein, der Code führt aus und bucht. Freigaben, Ampel, Geheimnisschranken in jeder Sitzung gleich. Keine Automatik beginnt von sich aus Arbeit.

**Was sich ändert:** Der Schlüssel einer Sitzung ist nicht mehr (Person, Telegram-Thema), sondern (Person, Anliegen-Kennung). Das Telegram-Thema wird ein Feld „Ausgabe-Adresse" am Anliegen, das leer sein darf. Vorlauf: dein Klon `probe-f22` vom 11.09. (Faden mit Person, Chat, Thema).

| Stufe | Inhalt | Stand |
|---|---|---|
| 1 | **Nebenfaden** (Bauauftrag f2): Verteilerin bekommt den zweiten Ausgang, Entscheidung als Funktion mit vier Wegen, Parallel-Messung | Auftrag liegt bei dir |
| 2 | **Anliegen-Sitzungen und Zuordnung** (Teil B unten) | dieser Auftrag |
| 3 | **Rückmeldung:** jedes Anliegen meldet fertig / Frage offen / gescheitert über die Botenpost mit dem Anliegen als Absender; die Moderatorin bündelt; Still-Schalter heißt sammeln und beim nächsten Zug vorlegen | Bauauftrag folgt nach 2 |
| 4 | **Austausch:** gemeinsames Wissen mit Sammelstelle, Zimmerfunk über das Postfach-Muster (Datei, kein Kanal), Sichtbarkeit je Anliegen; was ein Anliegen schreibt, ist für das nächste Information, nie Befehl | Block 4 vom 09.09., ungebaut |
| 5 | **Hintergrund ohne Adam am Chat:** Auftragsbuch und Hora scharf, Unterbrechbarkeit; Sicherheitsbetrachtung nach 9.4 schreibt die Kontrolle vorher | zuletzt |

## Teil B — Bauauftrag Stufe 2: Anliegen-Sitzungen und Zuordnung

### 1 · Das Anliegen als Einheit

- Ein **Anliegen** hat: Kennung (kurz, stabil, z. B. `a-0042`), Titel (vom Empfang vergeben, änderbar), Ausgabe-Adresse (Chat und optional Thema; leer = Hauptchat mit Zitat), Zustand (wach, schläft, fertig, Frage offen), eigenes Protokoll (wie heute je Zimmer `<datum>_zimmer-<id>.md`, Name um die Kennung ergänzt), Zeitpunkt der letzten Nachricht.
- **Schlüssel der Sitzung und der Warteschlange:** (Person, Kennung). Der Hauptchat bleibt ein Anliegen mit fester Kennung, damit heutiges Verhalten unverändert bleibt. Ein Telegram-Thema, das heute ein Zimmer ist, wird ein Anliegen mit gesetzter Ausgabe-Adresse. **Migration:** bestehende Zimmer werden beim Start einmalig in Anliegen überführt; ihre Protokolle bleiben lesbar.
- **Ausgabe:** Antwort geht an die Ausgabe-Adresse; ist keine gesetzt, in den Hauptchat als Antwort auf Adams Nachricht (`reply_to`), mit einer kurzen Kopfzeile aus dem Titel, damit Adam Anliegen unterscheiden kann, wenn mehrere gleichzeitig antworten.
- **Zustand auf der Platte** (Entscheid ② vom 09.09.): Anliegen-Liste als Datei neben den Prefs, überlebt Neustart.

### 2 · Zuordnung durch den Empfang

- Der Empfang bekommt den Stand aller Anliegen (Kennung, Titel, Zustand, letzte Nachricht) wie heute den Leitstand. Sein Urteil für eine Nachricht im Hauptchat: **bestehendes Anliegen** (Kennung) · **neues Anliegen** (mit Titel) · **Hauptchat** (Smalltalk, Befehl, Antwort auf eine offene Frage). Rückgabe strukturiert; alles Unverständliche gilt als Hauptchat (heutiges Verhalten = sicherer Rückfall).
- **Deterministisch vor dem Modell:** Antwort auf eine Nachricht eines Anliegens (`reply_to`) → dieses Anliegen, ohne Modellurteil. Befehle mit Schrägstrich → Hauptchat. Nachricht in einem Telegram-Thema → das Anliegen mit dieser Adresse.
- **Der Ausgang ist der vorhandene:** `zettel_ablegen` legt in ein Anliegen statt in ein Zimmer; neues Anliegen anlegen ist ein zweiter, ebenso enger Ausgang (Kennung vergeben, Titel setzen, sonst nichts). Der Empfang bleibt werkzeuglos darüber hinaus.
- **Nachfrage bei Unsicherheit (Adams Entscheid 2, Startzustand):** Der Empfang darf „unsicher" zurückgeben; dann Meldung mit Knöpfen: die zwei wahrscheinlichsten Anliegen, „Neu", „Hauptchat". Jeder Knopf tut etwas (keine Frage ohne Wirkung). Mitgeschrieben wird, wie Adam entschieden hat; die Schwelle bleibt in diesem Block fest.
- **Umlenken:** Unter jeder Anliegen-Antwort im Hauptchat ein Knopf „Anderes Anliegen", der dieselbe Auswahl zeigt. Keine Automatik lernt in diesem Block.

### 3 · Lebensdauer und Obergrenze

- **Schlafen** nach `ZIMMER_SCHLAF_NACH_S` (heute 30 min) wie gehabt; **Aufwecken**, wenn der Empfang eine Nachricht zuordnet. Kein Verfall; „fertig" ist ein Zustand, kein Löschen. Adam kann ein Anliegen per Knopf oder Befehl schließen; geschlossene bleiben in der Liste, ihr Protokoll bleibt.
- **Obergrenze wacher Sitzungen: `ANLIEGEN_GLEICHZEITIG = 11`** (Adam). **Dazu ein Speicher-Riegel, deterministisch:** Bevor eine weitere Sitzung geweckt oder angelegt wird, prüft der Code den freien Arbeitsspeicher (`/proc/meminfo`, MemAvailable); unter `SPEICHER_MINDESTFREI_MB` (Vorgabe 1500, Einstellgröße) wird nicht geweckt, der Auftrag wartet in der Reihe, eine ⚙️-Zeile und eine Meldung an Adam beim ersten Mal je Tag. Grund: Elf Sitzungen sind elf Prozesse; der Bedarf je Prozess ist nicht gemessen, der Server hat rund sechs von acht Gigabyte frei, und faster-whisper sowie die lokale Stimme brauchen Spitzen. Beide Zahlen ins Register (Zahlen an einer Stelle).
- **Kontingent:** Der Empfang sieht den Kontingentstand (`kontingent.py`) im Kontext und sagt Adam, wenn parallele Arbeit ihn leert; die Pause bei Limit gilt für alle Anliegen wie heute.

### 4 · Messen, parallel zum Bau (Adams Auflage)

Eine Messreihe im Klon, Ergebnis ins Drehbuch 5.1: Arbeitsspeicher je wacher Sitzung (RSS des CLI-Prozesses, im Leerlauf und unter Last) · Zeit bis zur ersten Antwort bei 1, 3, 6, 11 gleichzeitigen Läufen · Fehlermeldungen, die auf eine Parallelgrenze des Abos hindeuten (429, „concurrent", „rate"), wörtlich festhalten. Nichts davon ist eine Kostenquelle; alles Abo. Aus den Zahlen setzt Adam die Obergrenze neu oder lässt sie.

### 5 · Prüfer, ausführend (`scripts/test_anliegen.py`)

1. Nachricht ohne Bezug, Empfang sagt „neu" → Anliegen angelegt, Sitzung gestartet, Antwort im Hauptchat mit Zitat und Kopfzeile. 2. Nachricht mit `reply_to` auf eine Anliegen-Antwort → ohne Empfangsaufruf demselben Anliegen zugeordnet. 3. Empfang sagt „unsicher" → Meldung mit Knöpfen, kein Lauf bis zum Tipp. 4. Zwölftes Anliegen bei elf wachen → wartet, ⚙️-Zeile. 5. MemAvailable unter Schwelle (Attrappe) → kein Wecken, Auftrag bleibt in der Reihe. 6. Schlafendes Anliegen, Bezugsnachricht → geweckt, Sitzung fortgesetzt. 7. Telegram-Thema-Nachricht → Anliegen mit dieser Adresse, Ausgabe dorthin. 8. Neustart → Anliegen-Liste und Zustände aus der Datei. 9. Bestehendes Zimmer → nach Migration ein Anliegen, Protokoll unverändert lesbar. 10. Empfang antwortet Unsinn → Hauptchat, wie heute.
Gegenproben mit vorab benannter Zeile: Speicher-Riegel entfernen → 5 rot; Obergrenze ignorieren → 4 rot; Persistenz entfernen → 8 rot.

### 6 · Regeln

Klon-Probe (R4), Schlüsselwechsel ist die riskanteste Änderung dieses Jahres nach 5.1 Block 1 (dort stand die Lehre: alle Stellen, die den Schlüssel bilden, in einem Zug, sonst zwei Zimmer für dasselbe Thema). Register: neue Einstellgrößen, neue Datei, neue Funktionen. Doku-Spiegel: `/hilfe`, `/status`, `/zimmer` zeigen Anliegen. Drehbuch 5.1: Adams fünf Entscheide mit Datum, Stufe 2 als Block. Blaupause: „Anliegen statt Thema", universell. **Gut genug wenn:** Zehn Prüfzeilen grün, drei Gegenproben rot, ein Tag Probebetrieb mit mindestens drei gleichzeitigen Anliegen ohne Doppelantwort und ohne verlorene Nachricht, Messreihe im Drehbuch. Danach Gegenprüfung durch mich, dann Deploy als eigener Schritt. **Nicht in diesem Block:** Rückmeldung (Stufe 3), Austausch (4), Hora (5), Lernen der Zuordnung.
