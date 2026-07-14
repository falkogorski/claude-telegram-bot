# Migrations-Drehbuch — Telegram-Bot vom Mac auf den Netcup-VPS

**Stand:** 2026-06-22
**Migrations-Tag (geplant):** Dienstag, 23. Juni 2026, vormittags
**Demo-Bot Pflicht-Fertigstellung:** Mittwoch, 24. Juni 2026, vormittags (erster Klienten-Termin)

---

## Übergeordnete Prinzipien

1. **Phasenweise vorgehen, einzeln testen.** Nach jeder Phase eine kurze Funktionsprüfung (Smoke-Test). Nichts wird gebündelt abgehakt; jede Phase muss bestätigt sein, bevor die nächste beginnt.
2. **Strategie-Rückblick nach jeder Phase.** Am Ende jeder Phase prüfen wir gemeinsam, ob die geplante Reihenfolge der folgenden Phasen weiterhin sinnvoll ist und ob Inhalte gestrichen, ergänzt oder umgestellt werden müssen. Pflicht-Schritt, kein optionales Beiwerk.
3. **Keine eigenmächtigen Code-Eingriffe.** Vorschlag von mir, Freigabe durch Adam, dann Umsetzung. Bei Unklarheit oder tentativen Formulierungen frage ich nach.
4. **Datenschutz-Ampel wahren.** Rot bleibt lokal, grün/gelb darf in die jeweils vorgesehene Cloud-Schicht. Jede neue Komponente bekommt eine Farbeinordnung.
5. **Reproduzierbarkeit dokumentieren.** Alle Schritte, Konfigurationen und Schlüssel an einer reproduzierbaren Stelle sichern (privates Git-Repo), damit Adam das Gesamtsystem im Notfall allein neu aufsetzen kann.
6. **Telegram-Konflikt vermeiden.** Sobald der VPS-Bot live geht, wird der Mac-Bot konsequent gestoppt — ein Token darf nur an einer Stelle pollen oder Webhooks empfangen.

---

## Phase 0 — Vorbereitung (vor dem Migrations-Tag)

**Ziel:** Schlüssel-Rotation, lokales Fix-Bündel, sodass am Migrations-Tag eine saubere Ausgangslage steht.

### Schritte

**Adam (am Mac, im Browser und Terminal):**
1. Auf `console.anthropic.com` einloggen → Settings → API Keys.
2. Den alten Schlüssel `fanpost-mac-dev` widerrufen (Revoke).
3. Zwei neue Schlüssel anlegen: `fanpost-mac-dev` und `telegram-bot`.
4. Beide Werte sicher in die jeweilige `.env`-Datei eintragen, ohne sie im Chat zu pasten. Empfohlener Befehl je Schlüssel im Terminal:

   ```bash
   # Bot-Key
   read -s -p "Bot-Key: " K; echo; \
     ENV=~/Projects/claude-telegram-bot/.env; \
     if grep -q '^ANTHROPIC_API_KEY=' "$ENV"; then \
       sed -i.bak "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$K|" "$ENV"; \
     else \
       echo "ANTHROPIC_API_KEY=$K" >> "$ENV"; \
     fi; \
     unset K; echo "Bot-Key gesetzt."
   ```

   ```bash
   # Fanpost-Key
   read -s -p "Fanpost-Key: " K; echo; \
     ENV=~/projects/fanpost/.env; \
     if grep -q '^ANTHROPIC_API_KEY=' "$ENV"; then \
       sed -i.bak "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$K|" "$ENV"; \
     else \
       echo "ANTHROPIC_API_KEY=$K" >> "$ENV"; \
     fi; \
     unset K; echo "Fanpost-Key gesetzt."
   ```

**Ich (während Adam die Schlüssel anlegt):**

Drei Mini-Edits am Bot-Code als ein Bündel, gemeinsamer Neustart mit der Schlüssel-Aktivierung:

1. **Telegram-Reply-Bezug für die „Notiert"-Meldung** (`bot.py:2127`): `update.message.reply_text(...)` um `reply_parameters` auf `update.message.message_id` ergänzen, damit das Zitat von Adams Nachricht über der Notiz erscheint.
2. **Vorschau-Korrektur in `_job_preview`** (`bot.py:488`): einen führenden Block der Form `[Kontext: …]` vor der Vorschau-Bildung entfernen, damit nicht der Kontext-Hinweis-Präfix gezeigt wird, sondern der wirkliche Anfang der Nachricht.
3. **TTS-Aufbereitung für Codeblöcke und Pfade** (`_strip_markdown_for_tts` und Helfer): mehrzeilige ```…```-Blöcke durch einen erklärenden Platzhaltersatz ersetzen, Datei- und Ordnerpfade durch eine generische Bezeichnung verallgemeinern, Inline-Backticks konservativ behandeln. Der zugehörige Selbsttest (Funktionsprüfung um vier Uhr morgens) wird entsprechend erweitert.

**Gemeinsamer Bot-Neustart:** `launchctl unload` + `launchctl load` der Bot-Plist, sobald die Schlüssel eingetragen und die drei Edits gespeichert sind.

### Funktionsprüfung (Smoke-Test) Phase 0

- Adam sendet dem Bot ein kurzes PDF.
- Erwartung: Bot zieht die Zusammenfassung und schickt sie zurück. Wenn die Antwort kommt, ist der neue Schlüssel aktiv.
- Bonus-Test: Adam sendet zwei Nachrichten in schneller Folge. Erwartung: die „Notiert"-Meldung erscheint als echter Telegram-Reply auf die zweite Nachricht und zeigt deren wirklichen Anfang in der Vorschau, nicht den Kontext-Präfix.
- Bonus-Test (TTS): Adam fordert eine Antwort an, in der ein Codeblock vorkommt. Erwartung: in der Sprachausgabe wird der Block als kurzer Beschreibungssatz ersetzt, nicht zeichengenau gesprochen.

### Strategie-Rückblick Phase 0

- Reichen die drei Mini-Edits aus, oder sind während Phase 0 weitere kleine Korrekturen aufgefallen, die sinnvoll mit diesem Neustart erledigt werden sollten?
- Schlüssel-Hygiene: ist neben dem Anthropic-Schlüssel noch ein anderer (Telegram-Token, OpenAI, Groq) zu rotieren, weil er ebenfalls in den vergangenen Sitzungen exponiert war?

---

## Phase 1 — Server-Grundgerüst auf dem Netcup-VPS

**Ziel:** Der VPS ist gehärtet, Python und Audio-Werkzeuge laufen, der Bot ist installiert und wird durch `systemd` betreut. Telegram-Anbindung erfolgt über Webhooks statt Polling.

### Schritte (ich, per SSH)

1. **System härten.** Sicherheits-Updates einspielen (`apt update && apt upgrade`), `ufw` als Firewall scharf schalten (nur SSH, HTTP, HTTPS offen), `fail2ban` installieren, `unattended-upgrades` aktivieren.
2. **Eigenen unprivilegierten Nutzer** `claudebot` anlegen, ohne `sudo`-Recht. Dienst läuft unter diesem Konto.
3. **Python 3.12 installieren** sowie `ffmpeg` und `whisper.cpp` samt Sprachmodell. Whisper-Modell von `ggml-small.bin` auf `ggml-medium.bin` heben (rund 1,5 GB, präzisere englische und gemischte Passagen). Modell auf den Server übertragen.
4. **Globale Installation des `claude`-CLI** auf dem Server.
5. **Headless-Authentifizierung.** Auf dem Mac einmalig `claude setup-token` ausführen, den ausgegebenen Long-Lived-Token als Umgebungsvariable `CLAUDE_CODE_OAUTH_TOKEN` auf dem Server hinterlegen.
6. **Bot-Code in ein privates Git-Repository übertragen** und auf den Server klonen.
7. **`systemd`-Dienst einrichten**: `claude-telegram-bot.service` mit `Restart=always` und `RestartSec=30`, läuft als Nutzer `claudebot`.
8. **Webhook-Umstellung.** Im Bot-Code von Polling auf Webhooks umstellen (`app.run_webhook(…)`), Caddy oder nginx als HTTPS-Frontend mit Let's-Encrypt-Zertifikat davorsetzen.
9. **Mac-Bot stoppen.** `launchctl unload` der lokalen Plist, damit kein Token-Konflikt entsteht.

### Adam

Bestätigt, dass der SSH-Zugang passwortfrei mit dem Schlüssel funktioniert. Stellt für den Webhook eine öffentliche Adresse bereit oder gibt das Okay, die VPS-Adresse direkt zu verwenden.

### Funktionsprüfung Phase 1

- Eine Test-Nachricht aus Telegram an den Bot.
- Eine Werkzeug-Anfrage, die einen Berechtigungs-Dialog erzeugt.
- Eine Sprachnachricht, die transkribiert zurückkommen muss.
- Erwartung in allen drei Fällen: Antwort innerhalb weniger Sekunden, keine Fehlermeldungen im Log.

### Strategie-Rückblick Phase 1

- Ist das Whisper-Modell `medium` auf der VPS-CPU performant genug, oder zeichnen sich bereits Geschwindigkeitsprobleme ab, die Phase 2 beeinflussen könnten?
- Muss eine Anpassung an Phase 4 (Backup) erfolgen, weil sich die Pfade auf dem Server anders strukturieren als auf dem Mac?

---

## Phase 2 — KI-Orchestrierung und Datenschutz-Ampel

**Ziel:** Sämtliche Modell-Anfragen laufen über einen Vermittler (LiteLLM), der je nach Datenschutz-Farbe (grün, gelb, rot) das passende Modell wählt. Lokales Fallback steht bereit; OpenAI bleibt außen vor.

### Schritte (ich)

1. **LiteLLM-Proxy** installieren, SQLite als Speicher (kein Redis oder Postgres, da der VPS mit vier Gigabyte RAM auskommen muss).
2. **Datenschutz-Ampel als Gatekeeper** vor LiteLLM einrichten. Jede Anfrage wird vor dem Routing klassifiziert (grün/gelb/rot). Rote Anfragen verlassen den VPS nie und gehen ausschließlich an das lokale Modell.
3. **Lokales Fallback-Modell.** Ollama mit Phi-4 Mini im quantisierten Format (rund vier Gigabyte). Läuft auf der CPU.
4. **Groq** als Cloud-Fallback in LiteLLM eintragen (Free-Tier), aber nur für grüne und gelbe Anfragen.
5. **Bot-Anbindung an LiteLLM.** Der Bot ruft nicht mehr direkt Anthropic auf, sondern den LiteLLM-Endpunkt.
6. **Keine Aufnahme von OpenAI** in den Stack.

### Funktionsprüfung Phase 2

- Test-Eingabe „grün" (etwa eine allgemeine Wissensfrage) — landet bei Groq, Antwort kommt schnell.
- Test-Eingabe „gelb" (etwa eine Architekturfrage) — landet bei Claude.
- Test-Eingabe „rot" (etwa eine Klienten-Notiz oder Finanzbezug) — landet nur beim lokalen Modell. Erwartung: Antwort kommt langsamer, der Bot bestätigt im Log, dass kein Cloud-Anbieter beteiligt war.

### Strategie-Rückblick Phase 2

- Trifft die Klassifikation in der Praxis? Wenn rote Anfragen versehentlich grün eingestuft werden, müssen die Regeln nachgeschärft werden, bevor Phase 5 (Bot-Features) auf LiteLLM aufsetzt.
- Reicht Phi-4 Mini qualitativ für rote Anfragen, oder ist die VPS-Aufrüstung (Phase 2.75 der allgemeinen Roadmap) bereits jetzt das eigentlich passende Folge-Projekt?

---

## Phase 3 — Web-Oberfläche LobeChat

**Ziel:** Ein zweites Frontend neben Telegram, als Progressive Web App auf Mac und iPhone installierbar, hängt am selben LiteLLM-Endpunkt — gleicher Gesprächsfaden, gleiche Memory.

### Schritte (ich)

1. **LobeChat als Container** auf dem VPS installieren, hinter dem Caddy/nginx-Frontend mit HTTPS.
2. **Anbindung an LiteLLM** als Modell-Endpunkt eintragen.
3. **Memory-Loader** so konfigurieren, dass LobeChat die gemeinsame Memory-Datei einliest, sodass die Assistentin „Claudia" sich identisch verhält wie im Bot.
4. **PWA-Installation** auf Adams Mac und iPhone testen.

### Funktionsprüfung Phase 3

- Anmeldung von Mac und iPhone aus.
- Eine Test-Antwort, die ein Detail aus einer früheren Telegram-Sitzung aufgreift — Erwartung: nahtloser Bezug, kein „worum ging es?".

### Strategie-Rückblick Phase 3

- Reicht LobeChat als rotes-fähiges Frontend, oder ist Matrix (Phase 10) doch das geeignetere Werkzeug für sensitive Inhalte?
- Soll die PWA-Konfiguration zusätzlich auf einem zweiten Gerät (iPad) eingerichtet werden, um Mobilität zu erhöhen?

---

## Phase 4 — Datensicherung und Reproduzierbarkeit

**Ziel:** Ein tägliches Backup vom VPS auf den Mac, vorbereitet für späteres Umstecken auf einen Mini-PC. Sämtliche Konfigurationen und die Memory liegen in einem privaten Git-Repository.

### Schritte (ich)

1. **Tägliches `rsync`** vom VPS zum Mac, gesteuert per `cron`. Ziel-Pfad in einer Konfigurationsdatei, sodass ein Umstecken auf einen Mini-PC nur eine Zeile ändern verlangt.
2. **Zentrale Chat-Protokolle** aller Frontends (Telegram, LobeChat) als Textdateien auf dem VPS, in das Backup eingeschlossen.
3. **Privates Git-Repository** für Memory-Dateien, Bot-Konfiguration, LiteLLM-Konfiguration. Nicht in iCloud, sondern selbst gehostet (Gitea oder vergleichbar auf dem VPS).
4. **Reproduzierbares Rebuild dokumentieren.** Eine kurze Anleitung „so setzt du das gesamte System von Null neu auf", die Adam im Notfall durchgehen kann.

### Adam

Aktiviert den Erweiterten Datenschutz (Advanced Data Protection) in iCloud, sobald er dazu kommt — sodass die iCloud-Chat-Protokolle ohnehin mit eigenem Schlüssel verschlüsselt sind. Dies ist ein separater Schritt, der die Lage unmittelbar verbessert, aber nicht von der Migration abhängt.

### Funktionsprüfung Phase 4

- Ein Backup-Lauf wird manuell angestoßen und läuft sauber durch.
- Das Git-Repository wird auf einem zweiten Rechner geklont und ist vollständig.

### Strategie-Rückblick Phase 4

- Welche Daten gehören noch ins Backup, die wir bislang nicht bedacht haben (Whisper-Modelle, Ollama-Modelle, TTS-Cache)?
- Ist die `rsync`-Frequenz (täglich) für die roten Inhalte (Klienten-Notizen, Finanzdaten) angemessen, oder müsste das engmaschiger laufen?

---

## Phase 5 — Bot-Funktionen (in vier Unter-Schritten)

**Ziel:** Die seit langem geplanten Komfort-Funktionen werden eingebaut: Mehrfach-Sitzungen, Warteschlange, Sekretariats-Tafel, modulare Modellwahl, Sprachausgabe-Verfeinerungen, Kanal-Verzweigung, Emoji-Reaktionen.

### Unter-Schritt 5a — Mehrfach-Sitzungen und Warteschlange

- `sessions[chat_id][session_id]` statt einer globalen Sitzung. Befehle: `/new`, `/sessions`, `/switch N`, `/stop N`.
- Jede eingehende Nachricht wird **sofort beim Empfang persistiert** (Datei, Sprache, Text gleichermaßen) und bekommt einen Status (offen, in Bearbeitung, beantwortet). Eine durch Neustart unterbrochene Bearbeitung lässt nichts verschwinden.
- **Mehrere PDFs nacheinander** — jede Datei wird sofort heruntergeladen (sonst läuft die Telegram-Datei-Referenz ab), dann nacheinander verarbeitet.

**Funktionsprüfung 5a:** Adam schickt drei Nachrichten in schneller Folge plus zwei PDFs. Erwartung: keine Nachricht geht verloren, jede Datei wird verarbeitet, die Warteschlange ist sichtbar.

### Unter-Schritt 5b — Modell-Persistenz, TTS-Verfeinerung, Sprachausgabe auch für kurze Meldungen

- **Modell-Persistenz:** zuletzt gewähltes Modell wird beim Neustart wieder geladen (steht bereits, wird in dieser Phase kontrolliert).
- **Sprachausgabe auch für Bestätigungs- und Restart-Meldungen,** sofern TTS aktiviert ist.
- **Englische Aussprache:** Vorbereitung auf Piper oder Kokoro lokal als künftige Stimme — saubere englische Wörter ohne deutsches Buchstabieren. Test-Implementation in der Phase, Übernahme in den Live-Betrieb nach Adams Freigabe.

**Funktionsprüfung 5b:** Adam schaltet TTS um, sendet eine Anfrage mit englischen Begriffen. Erwartung: Stimme klingt sauber, Bestätigungen werden ebenfalls vorgelesen.

### Unter-Schritt 5c — Kanal-Verzweigung und Deep-Link-Behebung

- Jede Auswertung (PDF, Video, Foto, Recherche) wandert in den Ausgabe-Kanal; im Bot-Chat erscheint ein knapper Hinweis mit Deep-Link auf den Eintrag.
- **Deep-Link-Fix:** statt `https://t.me/c/...`-Links den nativen Telegram-URI `tg://privatepost?channel=…&post=…` verwenden — öffnet sich direkt in der App, nicht im Browser.
- **Original-Datei im Ausgabe-Kanal** anklickbar mitliefern (mit-hochladen oder verlinken).

**Funktionsprüfung 5c:** Adam sendet ein PDF, der Bot wertet aus, im Bot-Chat erscheint ein Deep-Link, der vom iPhone direkt in den Ausgabe-Kanal führt. Die Original-Datei ist dort anklickbar.

### Unter-Schritt 5d — Emoji-Reaktionen und Pinned-Memory

- Emoji-Reaktionen auf Bot-Nachrichten werden als Ja/Nein/Erledigt interpretiert — der bereits vereinbarte Vokabular-Standard (👍, 👌, ✅, 👎 und so weiter).
- **Pinned-Nachricht zu Memory:** wenn Adam eine Nachricht im Bot-Chat anpinnt, wird ihr Inhalt strukturiert in die Memory übernommen.

**Funktionsprüfung 5d:** Adam reagiert auf eine Frage des Bots mit 👍. Erwartung: der Bot deutet die Reaktion als Ja und führt die Aktion aus. Adam pinnt eine Nachricht, der Bot bestätigt die Memory-Aufnahme.

### Strategie-Rückblick Phase 5

- Welche der vier Unter-Schritte hat unerwartete Komplexität gezeigt, die Phase 6 (Kanal-Routing) oder Phase 7 (Erinnerungskanal) beeinflusst?
- Sind die Unter-Schritte in der richtigen Reihenfolge, oder hat sich gezeigt, dass 5b vor 5a sinnvoller wäre?

---

## Phase 6 — Kanal-Verzweigung in der vollen Ausbaustufe

**Ziel:** Pro Projekt ein eigener Ausgabe-Kanal oder ein eigenes Thema in einer Forum-Gruppe. Der Bot wählt den passenden Kanal automatisch nach Projekt-Kontext und kann neue Themen selbst anlegen.

### Schritte (ich)

1. **Forum-Gruppe vorbereiten** (Adam legt sie an, macht den Bot zum Administrator mit `can_manage_topics`).
2. **Projekt-Register aufbauen.** Jeder bekannte Projekt-Kontext bekommt ein zugeordnetes Thema (Topic). Bot pflegt die Zuordnung auf dem VPS.
3. **Automatische Topic-Erstellung,** wenn ein bisher unbekanntes Projekt aufkommt.
4. **Routing-Regel:** Code-/Programmier-Projekte bleiben im Bot-Chat (Kommandobrücke), alle anderen Auswertungen wandern in das zuständige Topic.
5. **Empfehlungsliste für Adam:** welche Projekt-Topics initial sinnvoll sind.

### Funktionsprüfung Phase 6

- Adam stellt eine Frage zu Projekt A — Auswertung landet im Topic A.
- Adam stellt eine Frage zu Projekt B — Auswertung landet im Topic B.
- Adam nennt ein neues Projekt C — Bot legt das Topic an und nutzt es ab sofort.

### Strategie-Rückblick Phase 6

- Welche Projekte fehlen noch in der Empfehlungsliste? Gibt es Themen, die sich rückblickend zusammenlegen lassen?
- Ist die Trennung „Code im Bot-Chat, Rest im Ablage-Kanal" so klar, oder gibt es Grenzfälle, die wir explizit machen sollten?

---

## Phase 7 — Erinnerungs-Kanal

**Ziel:** Ein eigener Telegram-Kanal, in den der Bot Routinen, Tagesabläufe und ausgewählte Kalendertermine schickt — mit direkten Links zu Zoom, YouTube oder anderen Ressourcen.

### Schritte (ich)

1. **Eigenen Telegram-Kanal anlegen** (Adam legt an, macht den Bot zum Administrator).
2. **Scheduler einrichten** (APScheduler innerhalb des Bot-Prozesses oder `systemd`-Timer).
3. **Kalender-Quelle anbinden** — Google Calendar oder CalDAV, denn Apple-Kalender per AppleScript funktioniert nur lokal am Mac und nicht auf dem VPS.
4. **Filterregeln** definieren: welche Termine wandern in den Erinnerungs-Kanal, welche nicht.
5. **Link-Extraktion** aus Termin-Beschreibungen (Zoom-Link, YouTube-Link, andere Ressourcen).

### Adam

Definiert mit mir gemeinsam die wiederkehrenden Routinen (Breathwork, Training, andere) und welche Kalender-Quelle eingebunden werden soll.

### Funktionsprüfung Phase 7

- Eine Test-Erinnerung wird zur richtigen Zeit gesendet.
- Ein Termin mit Zoom-Link erscheint mit direktem Klick-Link.
- Eine Routine mit verknüpftem YouTube-Video zeigt das Video als Link.

### Strategie-Rückblick Phase 7

- Werden die Erinnerungen aufmerksamkeitsgerecht wahrgenommen, oder sind sie zu häufig/zu selten?
- Lassen sich die Routinen mit dem Tagesrhythmus-Coaching ([[feedback-bedtime-coaching]]) sinnvoll verbinden?

---

## Phase 8 — Selbstüberwachung und Tests

**Ziel:** Das System überwacht sich selbst, Fehler werden früh sichtbar. Zentraler Funktions-Check am frühen Morgen, Vollständigkeits-Prüfung bei jedem Neustart, Regressions-Test nach größeren Änderungen.

### Schritte (ich)

1. **Täglicher Funktions-Check um vier Uhr** als zentrale Sammelstelle (`launchd`-Job mit `StartCalendarInterval`). Prüft: Token gültig, API erreichbar, TTS-Aufbereitung funktioniert, Notiert-Logik liefert echten Reply, alle umsetzbaren Funktionen reagieren wie erwartet.
2. **Vollständigkeits-Check bei jedem Neustart.** Prüft die jüngsten Nachrichten daraufhin, ob alles beantwortet ist. Verbindet sich mit der „keine Nachricht darf untergehen"-Regel ([[feedback-no-message-left-behind]]).
3. **Regressions-Test nach größeren Änderungen.** Definition „größer": Eingriff in Kern-Flow, Routing, API-Calls, neue Funktionen. Test ist isoliert (eigener Prozess, kein gemeinsamer Zustand).
4. **Code-Aufräumpass.** Einmaliger Durchgang, Karteileichen entfernen, Duplikate konsolidieren — **nur auf Vorschlag, nie eigenmächtig**. Adam entscheidet, was gestrichen wird.

### Funktionsprüfung Phase 8

- Der Vier-Uhr-Check läuft einmalig manuell durch und schickt seinen Bericht.
- Ein simulierter Bot-Neustart löst den Vollständigkeits-Check aus, der eine bewusst unbeantwortete Nachricht erkennt.
- Eine kleine Code-Änderung im Routing löst den Regressions-Test aus, der eine vorhandene Funktion bestätigt.

### Strategie-Rückblick Phase 8

- Welche zusätzlichen Funktionen sind nach Phase 8 für den Vier-Uhr-Check anzudocken (Backup-Lauf, Memory-Synchronisation, Klassifikations-Genauigkeit der Ampel)?
- Sind Phase 9 (Demo-Bot) und Phase 10 (Matrix) durch die bisherigen Phasen vorbereitet, oder müssen wir vor Phase 9 noch Lücken schließen?

---

## Phase 9 — Demo-Bot-Klon (Pflicht vor Mittwoch Vormittag)

**Ziel:** Ein eigener Klon des Bots für Adams ersten Klienten — eigener Token, leere Memory, eigene Protokolle, eigene API-Begrenzung, eigener `systemd`-Dienst auf dem VPS, Freigabeliste nur Adam und der Klient.

### Adam (Vorbereitung)

1. Bei `@BotFather` einen neuen Bot anlegen (eigener Name und Token).
2. In der gemeinsamen Telegram-Gruppe ein Demo-Thema bestimmen, in dem der Bot arbeiten soll.
3. Token sicher an mich übergeben (nicht im Chat pasten).

### Ich

1. **Eigenen `systemd`-Dienst** für den Demo-Bot, getrennte Konfiguration, getrenntes Protokoll-Verzeichnis.
2. **Leere Memory** — keine von Adams roten Inhalten wandert hinüber.
3. **Auswerte-Modus.** Der Demo-Bot empfängt Links und Videos, fasst zusammen, legt das Ergebnis in einem eigenen Ablage-Kanal ab. Optional Sprachantwort.
4. **Freigabeliste** auf Adam und den Klienten beschränken.

### Adam und Klient

Machen den Bot in der Demo-Gruppe zum Administrator, mit minimalen Rechten, nur im Demo-Thema.

### Funktionsprüfung Phase 9

- Adam und ich machen einen Testlauf: ein Link rein, Zusammenfassung raus, Ablage stimmt.
- Adam und der Klient machen einen kurzen Test, bevor der echte Termin beginnt.

### Strategie-Rückblick Phase 9

- Welche Reibungspunkte sind dem Klienten aufgefallen, die in Phase 11 als Backlog-Punkte zu verankern sind?
- Lassen sich aus der Demo Hinweise ableiten, die das Produkt-Konzept ([[project-productize-system-idea]]) konkretisieren?

---

## Phase 10 — Matrix für rote Inhalte

**Ziel:** Ein sicherer, ende-zu-ende-verschlüsselter Kanal für sensitive (rote) Gespräche — Synapse als eigener Heimserver, Element als Mobil- und Desktop-Klient, die Assistentin „Claudia" auf demselben Kern.

### Schritte (ich)

1. **Synapse** auf dem VPS installieren (rund zwei Gigabyte zusätzlicher RAM-Bedarf — empfehlenswert nach VPS-Aufrüstung, Phase 2.75 der allgemeinen Roadmap).
2. **`matrix-nio`-Bibliothek** in Python einbinden, Bot mit Ende-zu-Ende-Verschlüsselung verbinden.
3. **Element-Klienten** auf Mac, iPhone, iPad einrichten.
4. **Nahtloser Wechsel.** Adam kann mitten in einem Telegram-Gespräch in den Matrix-Kanal wechseln, der gemeinsame Kern hält den Kontext (gleiche Memory, gleiche LiteLLM-Anbindung).

### Funktionsprüfung Phase 10

- Adam sendet eine rote Anfrage in Matrix — wird verarbeitet, Antwort kommt verschlüsselt zurück, keine Cloud-Schicht im Spiel.
- Wechsel von Telegram in Matrix mit laufendem Kontext: keine Wiederholung nötig.

### Strategie-Rückblick Phase 10

- Trägt die Matrix-Lösung im Alltag, oder erweist sich Element für den iPhone-Komfort als zu sperrig?
- Reicht der VPS-RAM nach Phase 10, oder muss die VPS-Aufrüstung jetzt vorgezogen werden?

---

## Phase 11 — Rückblick-Sweep und Strategie-Synchronisation

**Ziel:** Aktive Suche nach Punkten, die in den vorigen Phasen nicht dran waren, aber dran sind. Verschobene Inhalte sortieren, Karteileichen entfernen, das Gesamt-System aufeinander einschwingen lassen.

### Schritte (ich)

1. **Memory-Notizen, Pending-Items, Telegram-Anheftungen, Migrations-Checkliste** systematisch nach Lücken und Karteileichen durchgehen.
2. **Verschobene Inhalte** aus Phase 1 bis 10 in die richtige Memory oder Liste sortieren.
3. **Strategie-Synchronisation:** alle Listen aktualisieren, sodass jeder offene Punkt einmal und nur einmal vorkommt.
4. **Vorschlags-Liste** an Adam mit allem, was schlanker, fehlerärmer oder besser strukturiert aufgesetzt werden könnte. **Niemals eigenmächtig.** Adam entscheidet.

### Funktionsprüfung Phase 11

- Adam und ich gehen die aktualisierten Listen gemeinsam durch. Erwartung: Adam erkennt jeden Punkt wieder, keine Karteileiche ist übersehen, kein neuer Punkt überraschend liegen geblieben.

### Strategie-Rückblick Phase 11

- Welche Themen aus Phase 1 bis 10 verdienen rückblickend eine eigene, vertiefende Mini-Phase 12 (etwa Voice-Klon, KI-Coach, Vermögensaufbau)?
- Wie sieht der nächste große Meilenstein aus, sobald die Migration vollständig abgeschlossen ist? Vermutlich: Aufbau der Einkommens-Strecken ([[project-financial-freedom-goal]]).

---

## Anhang — Reihenfolge auf einen Blick

| Phase | Inhalt | Zeitfenster |
|------:|--------|-------------|
| 0 | Schlüssel-Rotation + drei Mini-Edits + Bot-Neustart | vor Migrations-Tag |
| 1 | Server-Grundgerüst auf VPS | Migrations-Tag, Vormittag |
| 2 | KI-Orchestrierung und Datenschutz-Ampel | Migrations-Tag, Mittag |
| 3 | LobeChat-Frontend | Migrations-Tag, Nachmittag |
| 4 | Backup und Reproduzierbarkeit | Migrations-Tag, Nachmittag |
| 5 | Bot-Funktionen (vier Unter-Schritte) | Migrations-Tag, Abend, plus Folgetag |
| 6 | Kanal-Verzweigung in Vollausbau | nach Phase 5 |
| 7 | Erinnerungs-Kanal | nach Phase 6 |
| 8 | Selbstüberwachung und Tests | nach Phase 7 |
| 9 | Demo-Bot-Klon | vor Mittwoch Vormittag |
| 10 | Matrix für rote Inhalte | nach Phase 9, kein harter Termin |
| 11 | Rückblick-Sweep und Strategie-Synchronisation | abschließend |

---

## Anhang — Was wer macht

**Adam:**
- Schlüssel anlegen, Tokens sicher übergeben
- Forum-Gruppe für Kanal-Verzweigung anlegen, Bot administrieren
- Telegram-Kanal für Erinnerungen anlegen, Bot administrieren
- Demo-Bot-Token bei BotFather anlegen
- Element-Klienten einrichten
- Erweiterten Datenschutz (ADP) in iCloud aktivieren
- Routinen definieren, Kalender-Quelle wählen
- Bei jeder Phase die Smoke-Tests bestätigen, Strategie-Rückblick mitführen

**Ich:**
- Sämtliche Server-Konfiguration per SSH
- Bot-Code-Anpassungen (Webhook-Umstellung, Notiert-Fix, TTS-Aufbereitung, Mehrfach-Sitzungen, Warteschlange, weitere Funktionen)
- LiteLLM-Aufsetzung samt Ampel-Klassifikator
- Backup-Steuerung, Git-Repository, Reproduzierbarkeits-Anleitung
- Memory-Verankerung jeder Entscheidung
- Strategie-Rückblick aktiv am Ende jeder Phase einleiten
- Sicherheitsprüfung bei jedem Schritt ([[feedback-security-review]])

---

## Anhang — Was sich ändert (mit Häkchen-Abhakliste)

Die Migrations-Checkliste ([[project-migration-checklist]]) bleibt der zentrale Index. Jeder dort aufgeführte Punkt findet sich in diesem Drehbuch wieder. Nach jedem Smoke-Test wird der entsprechende Punkt in der Checkliste als erledigt markiert (`[x]`).

---

**Schlusssatz:** Dieses Drehbuch ist die gemeinsame Spielanleitung für die Migration. Bei jeder tentativen Formulierung oder Strategie-Frage frage ich nach, bevor ich umsteuere. Bei jeder Phase warten wir auf die ausdrückliche Bestätigung, bevor wir weitergehen. Das Tempo bestimmt Adam.
