**Zweck: WEITERGABE → Mick** · **Zu tun: unverändert an Mick. Ersetzt f1 vollständig. Einreihen nach dem laufenden Deploy (Schritte 2 und 3), vor Azure mit Schlüssel.**

# Bauauftrag „Nebenfaden" — Nachrichten während eines laufenden Vorgangs — 26.09.2026, 17:56 (Fassung 2)

**Neu in f2 gegenüber f1:** Teil 7 (Bündel) und Teil 8 (neues Thema, eigene Nachricht), beide aus Adams Fotos und Sprachnachricht von 17:37 bis 17:42 sowie Claudias Befund `2026-09-26_befund-themenwechsel-und-schnitt.md`. Teile 1 bis 6 unverändert.

**Adams Anlass (26.09., 17:24, Bot-Chat):** Während die Alfa-Romeo-Liste lief, fragte er nach einem sicheren Passwort. Antwort: „Notiert, ich reiche es dem laufenden Vorgang hinein … sonst danach als eigene Aufgabe (Position 1)." Sein Wunsch, sinngemäß: *Die schneller zu beantwortende Frage vorziehen, während die andere im Hintergrund weiterläuft, Antwort mit Bezug auf meine Frage. Zur Not mich fragen, mit anklickbaren Kästchen: einarbeiten, vorziehen, anreihen.*

**Adams Entscheide (26.09., 17:3x–17:4x, hier):**
1. **Vorgabe ohne Knopfdruck: kurze, eigenständige Fragen automatisch nebenbei.** Der Bot schätzt selbst ein; Knöpfe bleiben zum Übersteuern.
2. **Vier Knöpfe, in dieser Reihenfolge: Vorrang · Nebenbei · Einarbeiten · Anreihen.** Kein Knopf „Vorrang mit Stopp": Stoppen geht weiter über das Wort (`INTERRUPT_PREFIXES`).
3. Das ist der **erste Baustein des Dirigenten** (Moderationssitzung verteilt, beliebig viele Sitzungen parallel, Meldung zurück). Bau so, dass die Entscheidung des Empfangs später mehr Ausgänge bekommen kann, nicht als Sonderweg.

## Ist-Stand, gemessen (mac-produktivstand)

- Nachricht bei laufendem Vorgang: `mb.queue.append(job)` (bot.py ~13711) **und** Zettel in den laufenden Auftrag über `nachsteuer_schreiben` (nächste Werkzeuggrenze); ist der Zettel beantwortet, wird der Zwilling übersprungen (`zettel_erledigt`). Meldung „📨 Notiert … Position n".
- **Empfang** (empfang.py, Block 3 vom 10.09.): eigene SDK-Sitzung, Vorgabe Sonnet, werkzeuglos bis auf `zettel_ablegen` in ein Zimmer, `dontAsk`. Bei laufendem Vorgang wird sie mit `nur_antworten=True` gerufen (13738): antwortet kurz, reicht nichts weiter. Adam hat den Empfang **aus**.
- Vorziehen: `mb.queue.appendleft(job)` existiert nur im Korrektur-Zweig (mit `interrupt()`).
- Antworten zitieren die Frage bereits (`reply_to` im Worker, 2849).
- Zimmer = eine Sitzung je Faden `(user_id, thread_id)`, mehrere Worker laufen heute schon parallel (5.1).

## Auftrag

### 1 · Vier Ausgänge, eine Entscheidung

Bei einer Nachricht während eines laufenden Vorgangs im selben Zimmer entscheidet der Bot über genau einen von vier Wegen:

| Weg | Was geschieht | Heute vorhanden |
|---|---|---|
| **Vorrang** | Zwilling an die **Spitze** der Warteschlange, ohne Stopp; Zettel wird **nicht** gelegt (sonst doppelt) | `appendleft` ja, ohne Stopp nein |
| **Nebenbei** | eigener **Nebenfaden** antwortet sofort (Teil 3); Zwilling bleibt als Rückfall liegen, bis der Nebenfaden geantwortet hat, dann `erledigt` | nein |
| **Einarbeiten** | wie heute: Zettel in den laufenden Vorgang + Zwilling als Sicherung | ja |
| **Anreihen** | Zwilling ans Ende, **kein** Zettel | teilweise (heute immer mit Zettel) |

Die Entscheidung ist **eine Funktion mit vier Rückgabewerten**, ohne Bot-Zustand, in `empfang.py` oder einem eigenen Modul, damit ein Prüfer sie ausführen kann.

### 2 · Die automatische Einschätzung

- **Erste Stufe deterministisch, ohne Modell:** Korrekturwörter → heutiger Stopp-Weg (unverändert). Nachricht ist Antwort auf eine offene Frage des laufenden Vorgangs (`reply_to` zeigt auf dessen Nachricht, oder offene Frage registriert) → **Einarbeiten**, kein Modellurteil.
- **Zweite Stufe, der Empfang:** Für alles andere fragt der Bot die Empfangssitzung mit dem laufenden Auftrag als Kontext (Vorschau wie heute `_job_preview`) und der neuen Nachricht: *Ist die Nachricht ohne Kenntnis des laufenden Vorgangs vollständig beantwortbar?* Ja → **Nebenbei**. Nein, bezieht sich darauf → **Einarbeiten**. Nein, eigener größerer Auftrag → **Anreihen**. **Vorrang** vergibt die Automatik nicht, nur Adam per Knopf. Rückgabe ist ein Wort aus vier, alles andere gilt als Einarbeiten (heutiger Weg = sicherer Rückfall). Zeitgrenze wie `SEKRETAERIN_ZEITGRENZE_S`; läuft sie ab → Einarbeiten.
- **Empfang aus** (Adams Schalter): dann ohne Modellurteil immer Einarbeiten, wie heute; die Knöpfe gibt es trotzdem. So bleibt der Schalter, was er ist.
- **Kein Modellaufruf, wenn kein Vorgang läuft.** Die Einschätzung kostet nur dann einen Lauf, wenn es etwas zu entscheiden gibt.

### 3 · Der Nebenfaden

- Ein **Nebenzimmer**: eigene Mailbox mit eigenem Worker und eigener Sitzung, Schlüssel z. B. `(user_id, "neben")`, Ausgabe in denselben Chat, `reply_to` = Adams Nachricht. Damit läuft er über den vorhandenen Worker-Pfad (Ampel, Freigaben, Sendeweg, Protokoll) und nicht über einen zweiten Sendemechanismus.
- **Höchstens ein Nebenfaden je Zimmer** zugleich; ist er belegt, gilt Einarbeiten.
- **Keine Schreibwerkzeuge** im Nebenfaden (Write, Edit, MultiEdit, schreibendes Bash): zwei Sitzungen, die dieselben Dateien anfassen, sind das Risiko, das dieser Bau nicht eingehen soll. Lesen, Suchen, Netz mit den üblichen Freigaben ja.
- Der Nebenfaden **kennt den laufenden Vorgang nicht** (Absicht). Seine Sitzung endet nach der Antwort; kein Gedächtnis über den Lauf hinaus außer dem, was der Sendeweg ohnehin protokolliert.
- **Buchführung im Code:** Antwort zugestellt → Zwilling `erledigt`, Zettel (falls schon gelegt) zurückgezogen. Fehler oder Zeitgrenze → Zwilling bleibt, eine ⚙️-Zeile, Adam bekommt die Antwort auf dem heutigen Weg. Buchführung in eigener Klammer, hinter der Zustellung (Regel 10.09.).

### 4 · Die Knöpfe

Unter der Notiert-Meldung vier Inline-Knöpfe in Adams Reihenfolge: **⏫ Vorrang · ⏩ Nebenbei · 📎 Einarbeiten · ⏳ Anreihen**. Die Meldung nennt den automatisch gewählten Weg („Ich beantworte das nebenbei" / „Ich reiche es hinein" / „Reiht sich ein"). Ein Tipp setzt den Weg um, solange er noch umsetzbar ist: Zwilling verschieben, Zettel legen oder zurückziehen, Nebenfaden starten oder dessen Ergebnis verwerfen, wenn noch nichts zugestellt ist. Ist der Weg schon zu Ende (Antwort zugestellt), antwortet der Knopf „schon beantwortet" und verschwindet. Callback deterministisch, kein Modellaufruf (Regel „keine Frage ohne Wirkung": jeder Knopf tut etwas).

### 5 · Mitschreiben für das Lernen (nur Ablage, kein Bau)

Je Entscheidung eine Zeile in der Empfangs-Ablage (`_empfang_protokoll` ist da): automatisch gewählter Weg, von Adam übersteuert zu welchem Weg, Zeit. **Keine Anpassung der Schwelle in diesem Block.** Die Auswertung nach vierzehn Tagen entscheidet, ob und wie gelernt wird (Selbstlernende Assistenz, zweiter Schnitt).

### 6 · Wer merkt es

Tagescheck-Zeile: Nebenfäden gestartet / zugestellt / zurückgefallen in 24 h; Einschätzungen: nebenbei / einarbeiten / anreihen / übersteuert. Rückfälle > 0 sind `intern`, kein Adam-Alarm. `/status` zeigt einen laufenden Nebenfaden als eigene Zeile.

### 7 · Ein Bündel ist ein Auftrag

Adam schickt Bildschirmfotos zu fünft. Heute: fünf Aufträge, fünf Zettel, fünfmal „📨 Notiert … Position 1 bis 5" (Fotos 17:41). Gemessen: `media_group_id` kommt in bot.py nicht vor; jedes Foto eines Telegram-Albums läuft einzeln.

- Nachrichten mit derselben `media_group_id` werden **gesammelt** (Telegram liefert sie binnen etwa einer Sekunde) und als **ein** Auftrag mit allen Anhängen eingereiht; bei laufendem Vorgang **ein** Zettel, **eine** Notiert-Meldung, **eine** Knopfreihe. Die Bildunterschrift des Albums (steht am ersten Foto) ist der Text des Auftrags.
- Die Einschätzung (Teil 2) läuft für das Bündel einmal. Angekündigte oder erbetene Fotos („schick mir die Screenshots") sind der Normalfall **Einarbeiten**; das ergibt sich aus dem laufenden Vorgang im Kontext der Einschätzung, keine eigene Regel nötig.
- Prüfzeile: fünf Fotos mit gleicher Gruppen-Kennung bei laufendem Vorgang → ein Zettel, eine Meldung; ohne Gruppen-Kennung wie bisher.
- Geschwister: Dateien und Videos in Alben ebenso; Sprachnachrichten kommen nie als Album.

### 8 · Ein neues Thema bekommt eine eigene Nachricht

Adam, 17:37: *In allen Sitzungen, die an Telegram ausgeben: Fragen mit neuem Thema werden nicht integriert, sondern beginnen eine neue Nachricht als Antwort.* Anlass: Die Passwort-Antwort hing an der Alfa-Liste, der Längenschnitt bei 4000 fiel mitten in die Passwort-Liste, Adam sah zuerst nur die zweite Hälfte.

- **Nebenbei (Teil 3) löst den Normalfall:** Ein neues Thema wird nicht eingearbeitet, sondern im Nebenfaden beantwortet, mit Zitat der Frage. Die Einschätzung ist damit auch die Themenerkennung; im Zweifel trennen (Claudias Befund, Punkt 1).
- **Wird trotzdem eingearbeitet** (Adam tippt Einarbeiten, Empfang aus, Nebenfaden belegt): Die Antwort auf den Zettel geht als **eigene Nachricht mit Zitat der Zettel-Frage**, nicht als Absatz unter der laufenden Antwort. Bauform wie `<kopie>`: eine Steuerangabe `<antwort auf="<message_id>">…</antwort>`, die der Sendeweg an der Eingangsstelle (wo `vorschau_angabe_trennen` sitzt) herauslöst und als getrenntes Stück mit `reply_to` sendet. Der Zettel nennt der Sitzung die Kennung, damit sie sie setzen kann. Ohne Angabe: heutiges Verhalten.
- **Schnitt am Themenwechsel** (Claudias Punkt 4, klein, unabhängig): `_find_safe_cut` bevorzugt Trennlinie oder Überschrift als Schnittstelle, wenn sie in der zweiten Hälfte des Fensters liegt. Die 4096-Grenze bleibt; man bestimmt nur, wo geschnitten wird.
- Prüfzeilen: Zettel-Antwort mit Steuerangabe → zwei Nachrichten, die zweite zitiert die Zettel-Frage; Text mit Trennlinie bei 3000 von 5000 Zeichen → Schnitt an der Trennlinie; Steuerangabe wird nie vorgelesen und nie als Text sichtbar.

## Prüfer, ausführend

`scripts/test_nebenfaden.py`, Attrappen nur an den Rändern (Telegram, Empfangsantwort, Nebenfaden-Sitzung), Mitte echt:
1. Vorgang läuft, Einschätzung „nebenbei" → Nebenzimmer bekommt den Auftrag, Zwilling liegt, nach Zustellung `erledigt`, kein zweiter Lauf.
2. Einschätzung „einarbeiten" → Zettel gelegt, Zwilling liegt, wie heute.
3. Einschätzung „anreihen" → Zwilling am Ende, **kein** Zettel.
4. Knopf Vorrang → Zwilling an Position 1, laufender Vorgang nicht unterbrochen (`interrupt` nicht gerufen), Zettel zurückgezogen.
5. Nebenfaden scheitert → Zwilling läuft danach, eine ⚙️-Zeile.
6. Zweite „nebenbei"-Nachricht bei belegtem Nebenfaden → Einarbeiten.
7. Nebenfaden mit Write-Aufruf → verweigert.
8. Empfang aus → Einarbeiten ohne Modellaufruf (Empfangsattrappe wird nicht gerufen).
9. Kein laufender Vorgang → keine Einschätzung, kein Empfangsaufruf.
10. Unbekanntes Wort aus der Einschätzung → Einarbeiten.
Gegenproben mit vorab benannter Zeile: Buchführung entfernen → Zeile 1 rot (Doppellauf); Schreibsperre entfernen → 7 rot; `interrupt` in Vorrang einbauen → 4 rot.

## Grenzen und Regeln

- **Kosten:** Abo, kein neuer Dienst. Zwei Läufe zugleich ziehen am gemeinsamen Kontingent, dazu ein Empfangslauf je Entscheidung (Sonnet). Kein Modellaufruf ohne Adams Nachricht (Automatik-Regel: mensch-initiiert).
- **Fenster-Regel:** Der Zwilling bleibt bis zur Zustellung liegen; die Nachricht ist zu keinem Zeitpunkt nur im Nebenfaden.
- **Geschwister:** Sprachnachrichten, Fotos, Dateien während eines Vorgangs nehmen denselben Weg wie Text; im Prüfer eine Zeile je Geschwister.
- **Doku-Spiegel:** `/hilfe` und die Notiert-Meldung im selben Commit; Drehbuch 5.1 (Multi-Session) bekommt den Baustein „Nebenfaden" mit Adams drei Entscheiden; Register: neues Modul oder neue Funktionen in `ABHAENGIGKEITEN.md`; Blaupause-Zeile (Dirigent, Baustein 1, universell).
- **Klon-Probe (R4):** ja, der Eingriff berührt Warteschlange, Worker und Empfang.

**Gut genug wenn:** Eine kurze eigenständige Frage während eines langen Vorgangs ist binnen einer halben Minute beantwortet, zitiert, kommt nicht doppelt; ein Knopf ändert die Behandlung; fünf Fotos erzeugen eine Meldung; eine eingearbeitete Frage mit neuem Thema kommt als eigene Nachricht mit Zitat; bei Empfang aus verhält sich der Bot wie heute; Prüfzeilen grün, Gegenproben rot. **Nicht in diesem Block:** Lernen der Schwelle, mehr als ein Nebenfaden, Zuordnung zu anderen Zimmern (Dirigent, nächster Baustein).
