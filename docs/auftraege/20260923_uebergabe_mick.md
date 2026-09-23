**Zweck: WEITERGABE → Mick** · **Zu tun: unverändert an Mick; Adams Entscheide stehen in Teil D. Claudias Zettel ist eine eigene Datei.**

# Übergabe an Mick — Stand 23.09.2026, 15:0x (Fassung 3: Claudias Stand bis 14:53 eingearbeitet)

**Nenner:** Gelesen Logs 19.–23.09. (23.09. von 12:07 bis 14:53), fünf offene Bauaufträge von Claudia (13.09. Zimmerliste, 19.09. Meldungen, 23.09. Darstellung, 23.09. Modellwächter Fassung 2, 23.09. Link-Vorschau), ein Anregungspapier (11.09. HTML), Sammelblatt seit 11.09. Am Code geprüft: bot.py (`origin/mac-produktivstand` 8ca2783), components.json, log_sync.sh, test_eingangsschranken.py. Server läuft auf d54b272, Empfang aus.

**Vorab, weil es den Rest ordnet:** Zwei von Claudias Aussagen vom 23.09. tragen nicht, beide am Code gemessen (Teil B). Die Aufträge selbst tragen.

---

## A. Reihenfolge für Mick — fünf Blöcke, je etwa zwei Stunden

### Block 1 — Ein Knopf statt zwei, mit Sammelnachricht

Entscheide liegen in `docs/auftraege/20260911_entscheide_adam.md`. Neu ist die Messung vom 21.09.: Der Schreib-Knopf lebt nur im Speicher (`_SCHREIBEN_FREI`, stirbt beim Hygiene-Neustart 04:00), die Sitzung begann 04:30 ohne ihn, zwei Edit-Dialoge warteten je `FREIGABE_FRIST_S` = 3600 s ins Leere, Schlusswort erst 06:45, Register-Kopf ungeschrieben. Das ist der Punkt, den Adam jeden Morgen spürt.

- Auto-Knopf deckt Bash **und** Write/Edit unter `~/workspace`; `schreiben_ohne_frage` bleibt die Funktion, nur die erste Bedingung liest den Auto-Zustand statt des Speicherflags.
- Reichweite: **dauerhaft in den Vorlieben** (Adams Entscheid 23.09., gegen meine Empfehlung [bis Neustart]). Damit fällt das Speicherflag `_SCHREIBEN_FREI` weg; der Auto-Zustand in `prefs.json` trägt beides. Der Vermerk im Code sagt, dass die August-Fassung genau daran fiel, und dass die harten Grenzen (nächster Punkt) der Ausgleich sind.
- Gedächtnis-Ordner und Repo bleiben hart (`_is_sensitive_ref(schreibend=True)` steht davor, nicht ersetzen).
- Sammelnachricht der Genehmigungen im selben Block.
- **Gut genug wenn:** Eine Sitzung nach 04:00 mit Auto an fragt für kein Write/Edit unter `~/workspace`; ein Write nach `~/.claude/memory` fragt weiterhin. Beides als ausführende Prüfzeile, Gegenprobe: Riegel entfernen → rot.

### Block 2 — Darstellung im Antwortweg (Claudia 23.09. + Anregung 11.09., zusammengelegt)

Befund stimmt: `send_answer_to_user` sendet ohne `parse_mode` (bot.py 15441), `send_chunked` (2917) setzt keinen. Es gibt jetzt **zwei Papiere für dasselbe Problem** — HTML (11.09.) und MarkdownV2 über `telegramify-markdown` (23.09.). Ein Weg, nicht zwei; Entscheid in Teil D.

**Adams Entscheid 23.09.: Mick wählt den Transport nach Probe.** Zuerst `telegramify-markdown` (MarkdownV2), Probenachricht mit allen Merkmalen an Adam, bei Haken HTML als zweiter Anlauf. Das Bild ist bei beiden dasselbe; Adam hat beide Beispiele gesehen.

**Hausstil, festgeschrieben (Claudias sechs Merkmale vom 23.09. plus Adams drei):** Fettdruck auf der Aussage, nicht auf der Überschrift · Kausalketten als eigener Block, in Wörtern statt Pfeilen · kurze Absätze mit Luft · kursiv für Werktitel · nummerierte Punkte mit fetter Überschrift · Schlüsselbegriff am Zeilenanfang fett · Sprungmarken ins Video unter jedem Punkt · Quellen am Wort verlinkt · Videolink als Text am Schluss. Das ist Claudias Schreibregel, kein Bau; Mick trägt sie ins Drehbuch (Teil C).

**Link-Vorschau — Adams Entscheid, zuletzt 14:44/14:51 in Claudias Chat, ersetzt den Hostlisten-Entscheid von 14:0x:** Vorschau überall im Antwortweg, wo sie hilft; Schalter im Menü, Vorgabe ein; Freigabedialog und Wächter-Meldungen bleiben ohne. Grundlage ist Claudias Auftrag `2026-09-23_bauauftrag-linkvorschau.md` (vier Aufträge, dreistufige Regel). Er trägt. Vier Auflagen von mir:
- **Die Steuerangabe darf nur eine Adresse nennen, die im Text steht.** Die Steuerzeile ist Modellausgabe; fremdes Material kann sie beeinflussen. Ohne diese Prüfung könnte eine Karte für eine Adresse erscheinen, die Adam im Text nie sieht. Steht die Adresse nicht im Text → Stufe 2/3, nicht die Angabe. Das ist der eine Riegel, der die Öffnung trägt.
- Die Steuerzeile wird vor dem Senden entfernt **und** vor `_strip_markdown_for_tts` — sonst liest Katja sie vor. Eine Prüfzeile für beides.
- Der Schalter geht in `_SCHALTER` (Menü zeigt den Stand, Prüfzeile 8 Verdrahtung) und in den Statusblock des Startberichts, wie Claudia schreibt.
- Voreinstellung `is_disabled=True` (15565) und die Prüfzeile [Link-Vorschau programmweit aus] bleiben unverändert. Neue Prüfzeilen ausführend: (a) Antwort mit Steuerangabe → Vorschau auf genau diese Adresse; (b) Steuerangabe mit fremder Adresse → ignoriert, Stufe 3 greift; (c) Dialogpfad → `is_disabled` bleibt wahr; (d) Schalter aus → keine Vorschau. Gegenprobe zu (b): Textprüfung entfernen → rot.

Auflagen, die im Auftrag fehlen oder nur angedeutet sind:
- **Reihenfolge Schneiden/Umwandeln:** `_find_safe_cut` schneidet am Rohtext; die Umwandlung verlängert (Maskierung). Umwandeln **je Stück nach dem Schnitt** und das Stück vorher so bemessen, dass es nach Umwandlung unter `TELEGRAM_MSG_LIMIT` bleibt. Sonst zerreißt ein Paar oder Telegram lehnt ab.
- **Rückfall (Auftrag 2) ist Pflicht** und protokolliert über Claudias ⚙️-Marker aus dem 19.09.-Auftrag, nicht an Adam.
- **Sprachausgabe:** `_strip_markdown_for_tts` (14439) läuft auf dem Rohtext, vor der Umwandlung. Prüfzeile dafür.
- **Geltungsbereich** wie im Auftrag: 15441 und die Bildunterschrift 15493. `/zimmer`, `/status`, Link-Ablage bleiben ohne `parse_mode` (B2-2, H-5).
- **Neues pip-Paket:** Fassung pinnen in `requirements.txt`, Lizenz nennen, Register-Zeile in `ABHAENGIGKEITEN.md` (Prüfbefehl: der Selbsttest). Kostenfrei, läuft lokal.
- **Prüfzeilen ausführend:** Attrappe für `bot.send_message`, echter Code dazwischen. (1) Text mit Fett, Link, Unterstrich, einzelnem Stern → Aufruf trägt `parse_mode=MarkdownV2`. (2) Attrappe wirft `BadRequest` → zweiter Aufruf ohne `parse_mode`, gleicher Text. Gegenprobe: Rückfall entfernen → Zeile 2 rot.
- Vorschaukarte: siehe oben, gehört in diesen Block (Claudias Auftrag Link-Vorschau).

### Block 3 — Meldungen nur, was Adam betrifft (Claudia 19.09.)

Geprüft am 19.09. (`20260919_nachtlese.md`, Teil 3): trägt, drei Ergänzungen dort (⚙️-Marker im Protokoll statt neuer Kanal · Zähler stiller Neustarts, ab dem dritten laut · zwei Verhaltens-Prüfzeilen). Neu dazu:
- Die Meldung „📁 3 Datei(en) nach iCloud gelegt" kommt vom Mac-Skript `rechnungen_ablegen.sh`, Z. 270; sie nennt ihren Auslöser nicht. Halbsatz „nach dem Mac-Lauf" anhängen. Adam hat gefragt, was das ist — die Meldung betrifft ihn, sie bleibt laut.
- Fristmelder (Riegel `GILT-BIS` trotz `SCHARF: nein`, täglich rot seit 09.09.) und Stundenblumen-Prüfmoment gehen in diesem Block auf.

### Block 4 — Modellwächter (Claudia 23.09.)

**Zuerst, Adams Entscheid: Opus jetzt von Hand auf `claude-opus-5-5`.** Erste Zeile dieses Blocks: `_MODEL_ALIASES["opus"]` anheben, vor dem Neustart auf dem VPS als `claudebot` eine Abo-Probe (`claude -p --model claude-opus-5-5 'ok'`), erst bei Erfolg deployen. Fable/Sonnet/Haiku unverändert, bis der Wächter meldet.

**Auftrag 1 mit einer Berichtigung:** Claudia schreibt [Umgebungsdatei] — das ist `/etc/claude-telegram-bot.env`, root-eigen und Geheimnispfad; der Bot darf sie weder lesen noch schreiben, ein Knopf könnte dort nie wirken. Richtig ist der Plan vom 22.07. (MIGRATION 5.21, Baustein [Modell-Aktualität automatisch]): **`models.json` neben `prefs.json`** unter `~/.config/claude-telegram-bot/`, vom Bot schreibbar, außerhalb des Repos; `_MODEL_ALIASES` bleibt als Rückfall im Code. Aufträge 3 und 4 tragen.

**Adams Entscheid zur Automatik: umstellen von selbst, mit drei Sicherungen** (der Schalter (d) aus dem 22.07.-Plan steht damit auf AN): (1) Der Wächter schreibt nur `models.json` und meldet laut [umgestellt auf X], mit Rückweg-Knopf. (2) Adams nächste echte Nachricht ist die Probe; scheitert der erste Aufruf an der neuen Kennung (unbekannt, nicht im Abo), fällt der Bot **von selbst** auf die vorige Kennung zurück und meldet es. (3) Der Wächter ruft aus dem Zeitgeber nie ein Modell auf. Prüfzeilen ausführend für (2): Attrappe lässt den ersten Aufruf mit der neuen Kennung scheitern → zweiter Aufruf trägt die alte, Meldung gesendet; Gegenprobe: Rückfall entfernen → rot.

Auftrag 2 in Claudias Fassung 2 (14:36) trägt den Register-Hinweis bereits; es bleiben zwei Punkte:
- **Kandidat 1 (Modell-Liste über die Anbieter-Schnittstelle), Adams Entscheid: Mick misst zuerst, ob der Endpunkt den Abo-Token annimmt.** Ja → nutzen. Nur mit API-Schlüssel → **Halt, kein Schlüssel auf dem Server**, Rückfrage an Adam; dann Kandidat 3.
- **Prüfweg ohne Schlüssel:** Modellseite der Anbieter-Doku abrufen (derselbe Netzzugriff, den der Monitor für PyPI und npm ohnehin macht) und die Kennung gegen die Kandidaten-Liste halten; die Abo-Probe bleibt Adams Hand oder eine Sitzung, nie der 4-Uhr-Lauf (Modell-Aufruf aus Zeit-Trigger, AGB-Regel).
- **„Opus 5.5 seit 22.09., `claude-opus-5-5`"** ist eine Fremdaussage aus einer Nachrichtenseite, von mir nicht gemessen. Vor dem Umstellen die Abo-Probe; Grundeinstellung bleibt Adams Entscheid (Modell-Autonomie-Regel).
- Prüfzeilen ausführend: „Umstellen" schreibt die Umgebungsdatei und ein frischer Leser liefert den neuen Wert; ohne Knopfdruck ändert sich nichts (Gegenprobe: automatische Übernahme einbauen → rot).

### Block 5 — Kleinkram, je einzeln committet

- `scripts/konzept_pdf.py`: `-V mainfont`/`-V monofont` fehlen; zweimal gebissen (11.09., 21.09. „dokumentierter Umweg").
- Aufstellungs-Generator bricht bei Schrägstrich im Dateinamen ab (Claudias Zettel, 20.09.); Schrägstrich ersetzen statt abbrechen.
- **`log_sync.sh`, Wirkungs-Regel:** Der Abgleich vom 23.09. hat aus `~/workspace/werkzeuge/yt-transkript/lib/python3.13/site-packages/…` vierzehn `.txt`-Dateien (Lizenzen, entry_points) ins Log-Repo getragen — der Ausschluss kennt `venv/` und `.venv/`, nicht `lib/` oder `site-packages/`. Ausschluss `--exclude='site-packages/'` **vor** den Includes, Dateiliste danach ansehen.
- Register-Zeilen: `youtube-transcript-api` (eigene venv unter `~/workspace/werkzeuge/yt-transkript`, gemessen 23.09.: gewöhnliches Video 6 Spuren/61 Zeilen, Livestream-Aufzeichnung abgewiesen) und der Fremddienst `freetranscriptapi.com` als Ausweichweg (Adam-Freigabe 23.09. 12:41, [in dieser Phase], nicht für eigenes Material). **Kostenfrage, Stand 14:36 (Claudias Auskunft):** kein Konto, kein Schlüssel, 50 Abrufe je Stunde, Grundnutzung kostenfrei; eine Abbuchung ist ohne Konto nicht möglich → für Einzelabrufe geschlossen. Offen: Befristung [bis 19.09.] auf der Anbieterseite (Abruf lief am 23.09. trotzdem) und ungelesene Datenschutzbedingungen → **vor einem festen Ablauf** lesen; Ausweichanbieter derselben Gattung ist Selmas `youtube-transcript.ai`.
- TTS-Kopiertext (16.09.), F-Punkte: Belegkette seit 18.08. nie gerollt; Gedächtnis-Pfad im Prompt.

## B. Zwei Berichtigungen zu Claudias Aussagen vom 23.09.

**B1. „Die Vorschau wird an genau einer Stelle unterdrückt, der gewöhnliche Antwortweg lässt sie zu"** — falsch. bot.py 15565: `Defaults(link_preview_options=LinkPreviewOptions(is_disabled=True))`, programmweit, seit der Eingangs-Absicherung 23.08. (Glied 7), mit ausführender Prüfzeile „Link-Vorschau programmweit aus" in `scripts/test_eingangsschranken.py`. Adam wird **keine** Vorschaukarte sehen, auch nach Block 2 nicht. Sie einzuschalten ist eine Schranken-Änderung → Entscheid D1.

**B2. „In den Zetteln steht nichts zu Modellfassungen"** — falsch, siehe Block 4: `components.json` führt `claude-modelle` seit dem 25.07.

Dazu eine Lücke, kein Fehler: **Der Fremddienst wurde um 12:47 genutzt, ohne dass im Log steht, ob er Anmeldung, Kosten oder Grenzen hat.** Claudia hatte um 12:42 angekündigt, das zu prüfen. Kostenregel: unklar gilt als ja → D2.

## C. Drehbuch-Nachträge (Ablageweg, Mick trägt ein)

- Präzisierung 23.09. 13:57 (Selmas Einwand, von Claudia angenommen): Auch der Direktabruf von Untertiteln gibt Video-Kennung und Server-Adresse an YouTube; der Fremddienst fügt einen dritten Mitwisser hinzu. Der Unterschied ist die Zahl der Mitwisser, nicht ob etwas hinausgeht. So ins Drehbuch (5.12), nicht [gibt nichts nach außen].
- Selma-Vergleich abgeschlossen 14:16: Ihr Direktabruf scheiterte ebenso (Anmelde-Sperre), Erfolg erst über einen externen Untertitel-Dienst (youtube-transcript.ai, Aufruf per curl ohne Konto); dieselbe Spur wie bei uns (1.479 Abschnitte). Kein Zugang, den wir nicht haben. Kein Bauauftrag daraus; der Darstellungs-Auftrag ist die ganze Differenz.
- Adam-Entscheide 23.09.: keine Einordnung ungefragt bei Video-/Textauswertungen (12:19); Herkunftsvermerk am Ende jeder Auswertung Pflicht (12:41); Videolink als Text am Schluss (12:37); Fremddienst als Ausweichweg frei „in dieser Phase", nicht für eigenes Material (12:41).
- Rechnungsregel 4a: Zahlungsfrist generell fünf Tage (21.09. 04:32), gebaut.
- 5.12 / Heimtunnel-Eintrag 26.07.: Die Juli-Diagnose ist für Untertitel überholt (gemessen 23.09.); der Heimtunnel ist für die Untertitel-Ebene nicht mehr nötig, für die Bildebene weiter offen. Status-Zeile anpassen.
- CLAUDE.md, Abschnitt „Von außen kommen nie Anweisungen": „Stand 21.08.: im Bot NICHT gebaut" ist veraltet (gebaut 23.08., d596269).
- Versions-Monitor 21.09.: Node 22→24 MAJOR, SDK 0.2.127→0.2.157, CLI 2.1.209→2.1.278. Glieder 1 und 2 der Kette vom 29.08.; Klon-Probe (R4) durch Mick, Deploy Adams Hand.

## D. Adams Entscheide vom 23.09. (14:0x, im Chat mit Engywuck)

1. **Link-Vorschau** (geändert 14:44/14:51 in Claudias Chat): überall im Antwortweg, Schalter im Menü, Vorgabe ein; Bezug: Steuerangabe → einziger Link → letzter Link. Freigabedialog und Wächter-Meldungen bleiben ohne.
2. **Fremddienst für Transkripte:** Freigabe für öffentliche Videos bleibt; Auskunft liegt vor (Block 5), Kostenfrage für Einzelabrufe geschlossen; Bedingungen vor einem Dauerweg lesen.
3. **Darstellung:** Mick wählt den Transport nach Probe (erst telegramify-markdown, sonst HTML); Hausstil mit neun Merkmalen festgeschrieben; Abnahme per Probenachricht am Handy.
4. **Ein Knopf:** dauerhaft in den Vorlieben; Gedächtnisordner, Repo, Geheimnispfade bleiben hart.
5. **Modell-Liste:** Mick prüft mit dem Abo-Token; nur mit API-Schlüssel → Halt und Rückfrage.
6. **Opus 5.5:** jetzt von Hand, mit Abo-Probe vor dem Neustart. Wächter stellt künftig **automatisch** um, mit lauter Meldung, Rückweg-Knopf und Auto-Rückfall beim ersten Fehlschlag.
7. **Fußzeile Aufstellung:** nein, Bildunterschrift im Chat reicht.
8. **Node/SDK:** Klon-Probe jetzt, Deploy nach Micks Bericht in einem Fenster von Adams Wahl.

## E. Text an Mick

> Übergabe 23.09. von Engywuck, Blöcke 1 bis 5 in Teil A, Reihenfolge so. Adams acht Entscheide stehen in Teil D und sind in die Blöcke eingearbeitet. Drehbuch-Nachträge in C bitte im ersten Commit. Vor jedem Commit `bash scripts/regressionstest.sh`; neue Prüfzeilen ausführend, Gegenprobe rot. Deploy-Block je Block mit Schritt 0 (`git log --oneline HEAD..<ziel>`).
