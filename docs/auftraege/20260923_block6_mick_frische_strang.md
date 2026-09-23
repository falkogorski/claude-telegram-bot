**Zweck: WEITERGABE → Mick** · **Zu tun: nach Block 5 einplanen. Fassung 5 vom 24.09., 01:3x: ersetzt Fassung 4. Neu: Claudias Befund [Sperre ist die Regel] (01:24) in 6.0c, dazu eine Berichtigung der Übergabe Teil C.**

# Block 6 für Mick: Frische-Strang (Alternativen · Zufluss · Vorschlagsweg)

23.09.2026, 17:4x · Engywuck · Adams Entscheide von 17:3x: Block 6 nach den fünf laufenden; Bewertung nur auf Adams Wort; kein Modellaufruf am Zeitgeber. Konzept: `20260923_konzept_frische_strang.md` (bei Adam).

**Gut genug wenn:** Der Wochenlauf des Monitors legt neue Feed-Einträge ab und meldet fällige Alternativen; `/neues` liefert Adam eine Sichtung mit Knopf, der einen Laufplan-Eintrag erzeugt; kein Zeitgeber ruft ein Modell.

## 6.0b Everlast (Adams Favorit) — Claudias Nachtrag M6/M7, 24.09., 01:00 bis 01:20

- **Newsletter KI Bubble:** Substack, Feed `https://www.kibubble.news/feed` (200, 20 Einträge, jüngste Ausgabe 22.09.). In `quellen.json`, Gruppe 3, ganz oben. Kein Konto.
- **YouTube:** sechs Kanäle im Everlast-Netz, alle Feeds 200. Feed-Form `https://www.youtube.com/feeds/videos.xml?channel_id=<kennung>`, 15 Einträge je Feed. **Adams Entscheid 01:19: nur der Hauptkanal** `UC8T5gQ4U4GbI2h8kYCkEcvg`. Robotics und die übrigen vier nicht jetzt; Kennungen stehen im Nachtrag, falls später gewünscht. Kennungen der übrigen im Nachtrag `2026-09-24_whatsapp-messung-nachtrag-m6-m7.md`.
- **Transkripte:** siehe 6.0c — der Direktabruf ist die Ausnahme, der Fremddienst der Regelweg.
- **Werkzeuge im Arbeitsordner** (`yt_kanal_id.py`, `yt_feed_pruefen.py`, `feeds_messen.py`, `kanal_messen.py`): Register-Zeilen; der Kanal-ID-Abruf braucht einen Zustimmungs-Keks (YouTube liefert sonst nur die Sprachauswahl) — das gehört als Kommentar in `zufluss.py`, falls Kennungen je automatisch gesucht werden.
- **Nicht in Block 6:** der WhatsApp-Kanal (Vormerkung 6b, nach Micks Lese-Auftrag M4).

## 6.0c Claudias Befund 01:24 (`2026-09-24_befund-sperre-ist-die-regel.md`): Direktabruf ist die Ausnahme

Messanlage: je 15 Videos von Everlast AI und tagesschau, viermal das Kontrollvideo dazwischen. **30 von 30 abgewiesen, Kontrolle 4 von 4.** Keine Drossel, kein Livestream-Effekt, keine Kanalgröße, kein Altersgefälle innerhalb eines Monats. Das eine Video, das geht, ist fünfzehn Jahre alt und millionenfach abgerufen; ob Alter oder Abrufzahl zählt, ist offen (Test: altes, wenig abgerufenes Video).

**Was das für den Bau heißt:**
1. **Reihenfolge bleibt, Erwartung dreht sich:** erst Direktabruf (kostet nichts, kein Dritter), dann Fremddienst. Der Fehlschlag des Direktabrufs ist der Normalfall und wird **nicht** gemeldet — nur gezählt (Zeile im Monitor-Log), damit ein späteres Öffnen von YouTube auffällt.
2. **Der Fremddienst `freetranscriptapi.com` ist der Regelweg.** Deshalb vor dem Bau: Datenschutzerklärung und Bedingungen lesen, eine Zeile an Adam (geht / geht nicht). Die Stundengrenze (50 ohne Konto) ist der echte Engpass: Code 429 als eigener Fall mit Wartezeit-Hinweis; 401/402 als [Konto oder Kosten verlangt], nie als leeres Ergebnis. Kein Konto anlegen, kein Bezahltarif (💰).
3. **Zweiter Dienst als Rückfall:** `youtube-transcript.ai` (Selmas Weg, laut ihrem Protokoll ohne Konto per curl). Vor der Aufnahme dieselbe Lesepflicht wie bei 2, und eine Messung vom VPS an drei Videos. Dann Reihenfolge direkt → Dienst A → Dienst B.
4. **Adams eigene Videos und Kursmaterial nie über einen der beiden Dienste** (6.4).
5. **Heimtunnel:** Claudia stuft ihn wieder hoch — er wäre der einzige Weg ohne fremden Dienst. Das ist Adams Entscheid, kein Teil dieses Blocks; die Vormerkung 6b und der Drehbuch-Eintrag vom 26.07. bleiben stehen.

**Berichtigung meiner Übergabe vom 23.09., Teil C, dritter Spiegelstrich:** Dort steht, die Juli-Diagnose sei für Untertitel überholt und der Heimtunnel für die Untertitel-Ebene nicht mehr nötig. **Das war falsch** — es beruhte auf Claudias einer Stichprobe vom 23.09., und die war die Ausnahme. Richtig für 5.12: Der Direktabruf vom VPS funktioniert nur ausnahmsweise (gemessen 24.09.: 1 von 31 Videos), der Fremddienst ist der Regelweg, der Heimtunnel bleibt der einzige eigene Weg. Bitte so ins Drehbuch, nicht meine Fassung von gestern.

## 6.1 Fähigkeits-Register (Erweiterung von `components.json`, kein neues Register)

Je Eintrag drei optionale Felder: `zweck` (Fähigkeit in einem Satz), `alternativen` (Liste: Name, Adresse, zuletzt gesichtet), `ersatz_aufwand_h`. Der Monitor (`version_monitor.py`) meldet **[Alternativen fällig]** wie heute bei `manual` nach `intervall_tage`; gleiche Meldezeile, gleiche `gesehen`-Logik. Erste Einträge: Fremddienst Transkripte (freetranscriptapi.com, Alternative youtube-transcript.ai), Websuche-Anbieter, edge-tts, faster-whisper, PDF-Weg, Modelle. Register-Zeile in `ABHAENGIGKEITEN.md`.

## 6.0 Claudias Messung (24.09., 00:10 bis 00:25, vom VPS): 46 Adressen, 40 erreichbar

Papier `2026-09-24_frische-quellen.md` (Log-Archiv, flach unter `~/workspace`). Was daraus für den Bau folgt:

- **GitHub ist vom VPS offen** (zehn Release-Feeds, alle 200). Meine 403 waren meine Maschine.
- **`quellen.json`, Startbestand:** Gruppe 1 über **PyPI-Feeds** (claude-agent-sdk, python-telegram-bot, litellm, weasyprint, caldav, pymupdf, edge-tts, faster-whisper, youtube-transcript-api) und GitHub-Feeds für nodejs, lobe-chat, ffmpeg, docker (moby), whisper.cpp, pandoc, claude-code-cli; Gruppe 2 **Anthropic Release Notes** `https://platform.claude.com/docs/en/release-notes/feed.xml` (141 Einträge, jüngster 22.09.); Gruppe 3 die zehn Landschaftsquellen aus Claudias Tabelle (Simon Willison, Import AI, Ars Technica KI, MIT Technology Review, TechCrunch KI, The Verge KI, IEEE Spectrum Robotik, netzpolitik.org, Golem). **Nicht:** heise-Gesamtfeed, hnrss (Rohmenge ohne Redaktion).
- **`manual` bleiben:** Anthropic News, Telegram Bot-API-Changelog, Telegram Blog, beide Transkript-Dienste, kiberatung.de.
- **Debian-Sicherheitsfeed** `https://www.debian.org/security/dsa` ist RDF; Claudias Zähler las null Einträge → beim Bau mit einem RDF-fähigen Parser nachmessen, bevor er in die Liste kommt.
- **Prüfer-Pflicht aus ihrer Tabelle, übernommen:** je Quelle Datum des letzten erfolgreichen Abrufs mitschreiben; schweigt eine Quelle länger als ihr gemessener Takt, Meldezeile im Monitor-Log. 401/402 gesondert als [Konto/Kosten verlangt], nie als [nichts Neues].

**Berichtigung für Block 4 (Modellwächter):** Die Bezugsquelle ist geklärt und kostet nichts: der Anthropic-Release-Notes-Feed führt Modelle und Claude Code. Auftrag 2 liest diesen Feed und vergleicht Modellkennungen gegen `models.json`. Die Abo-Token-Messung gegen die Modell-Liste (Adams Entscheid 23.09.) darf entfallen; falls Mick sie trotzdem fährt, nur als Zusatz.

**kiberatung.de (Adams Quelle) ohne Feed:** kleiner Baustein in `zufluss.py`: Quellenart `seite` — Blogübersicht abrufen, Beitragslinks herauslesen, neue Links als Einträge ablegen. Kein Stichwortsieb, nur Linkvergleich. Der WhatsApp-Kanal desselben Anbieters läuft getrennt (Vormerkung 6b).

## 6.2 Zufluss `scripts/zufluss.py`

- Liest `quellen.json` (Adams Hand; Claudias Liste als Vorlage), holt RSS/Atom mit Zeitlimit je Quelle, legt neue Einträge (Kennung, Datum, Quelle, Titel, Adresse) nach `~/.claude/zufluss/eingang.jsonl`, entdoppelt über Kennung, hält 60 Tage.
- Hängt am **bestehenden** Monitor-Timer (Mo 04:20), kein eigener Zeitgeber. Kein Modell, kein Telegram. Gescheiterte Quellen als Zeile im Monitor-Log, nicht an Adam (Claudias Auftrag [Meldungen nur, was Adam betrifft]).
- Der Log-Kurier nimmt `eingang.jsonl` mit (Include-Regel prüfen, Wirkungs-Regel: Dateiliste danach ansehen).
- **Fremdinhalt ist Daten:** Titel und Adressen werden nur abgelegt, nie ausgeführt oder als Anweisung gelesen; die Datei wird bei `/neues` als Mitschrift übergeben, nicht als Stimme (Eingangs-Absicherung 23.08.).

## 6.3 `/neues` mit Wirkung

- Adams Befehl. Claudia bekommt den Eingang seit der letzten Sichtung, gruppiert nach Bauteil (über `zweck`/`alternativen`) und Landschaft, höchstens drei Vorschläge.
- Je Vorschlag Knopf **[in den Laufplan]** → deterministischer Eintrag ins Auftragsbuch/Freigabe-Postfach; kein Modelllauf beim Knopf. Merker [gesichtet bis] wird beim Antworten gesetzt.
- Kurs-Blick bekommt die Zeile [Neu am Markt, für uns relevant] aus derselben Datei (Engywuck liest sie im Log-Archiv).

## 6.4 Adams Vorgaben vom 24.09., 01:19 (Claudia-Chat) — Kontingent, Wissensdatenbank, Kurse

- **Kontingent darf teils dafür verwendet werden**, gesteuert **auf Zuruf**: `/neues` zeigt die Titel; ein Knopf **[mehr auswerten]** holt für die ausgewählten Einträge Transkript und Zusammenfassung. Wenn Adam sagt, dass zum Wochenende Kontingent übrig ist, ruft er ihn. **Kein Zeitgeber ruft ein Modell**, auch nicht bei Restkontingent — der Kontingent-Knopf zeigt den Stand, Adam entscheidet. Nicht alle Videos; Zusammenfassungen nach Bedarf (Adams Beispiel: [fass mal zusammen], wie beim Fußball).
- **Wissensdatenbank, nach und nach:** Ablage `~/workspace/wissen/<jahr>/<quelle>_<datum>_<kurztitel>.md` je Zusammenfassung, mit Kopf (Quelle, Adresse, Datum, Grundlage, Herkunftsvermerk) und einer Indexdatei `wissen/INDEX.md`, die der Bot bei Fragen liest. Das ist der Recall-Punkt des Drehbuchs (Multi-Session/Recall) in seiner kleinsten Form: Dateien und ein Index, kein neues System. Register-Zeile. Der Kurier nimmt `wissen/` ins Log-Archiv (Include prüfen, Wirkungs-Regel).
- **Adams Everlast-Kurse** (Claude-Kurs, Agentic-Marketing-Kurs; bezahlt, lebenslang): **eigenes Material — nie über den Fremddienst.** Transkription lokal mit `faster-whisper` über den vorhandenen Medienpfad, Ablage in `wissen/kurse/`. **Offen, Mick klärt:** ein Weg für große Videodateien vom Mac auf den VPS (der Bot-Weg über Telegram trägt nur kleine Dateien). Kandidaten: `scp`/`rsync` durch Adams Hand in einen Eingangsordner, den der Bot kennt; Vorschlag mit einer Zeile Aufwand an Adam, kein Bau ohne sein Wort. Rechtlich: nur Adams eigene Nutzung, nichts davon in ein anderes Repo oder an Dritte.

## Prüfzeilen, ausführend

1. Zufluss mit Attrappen-Feed: zwei Einträge, einer doppelt → genau zwei Zeilen im Eingang, zweiter Lauf fügt nichts hinzu.
2. Quelle antwortet nicht → Lauf endet grün mit Log-Zeile, kein Telegram-Aufruf (Attrappe zählt Aufrufe: 0).
3. Monitor mit Eintrag, dessen Alternativen-Sichtung älter als `intervall_tage` → Meldezeile [Alternativen fällig].
4. Knopf [in den Laufplan] → Eintrag vorhanden, kein Modellaufruf (Attrappe zählt 0). Gegenprobe: Knopf-Handler entfernen → rot.
6. Wissensdatei mit Kopf angelegt → Zeile im Index; Datei ohne Herkunftsvermerk → abgewiesen.
5. `scripts/test_zielumgebung.sh` fährt `zufluss.py` mit `env -i` (root-Dienst ohne HOME, Lehre vom 29.07.).
7. Transkript-Knopf mit Attrappen: Direktabruf wirft RequestBlocked → Dienst A wird gerufen, keine Meldung an Adam, Zähler +1; Dienst A antwortet 429 → Adam bekommt den Wartezeit-Hinweis, kein Dienst B ohne Freigabe-Eintrag in `quellen.json`. Gegenprobe: Zähler entfernen → rot.

## Was nicht dazugehört

Kein automatischer Wochenbericht, keine Stichwortfilter, keine Newsletter per Mail, keine Konten. Was eine Quelle nur per Seite bietet, wird `manual` mit Intervall.
