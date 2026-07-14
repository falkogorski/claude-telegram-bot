---
name: migration-drehbuch
description: "Operatives Arbeitsdokument der Netcup-VPS-Migration (MASTER, zusammengeführt). Pro Punkt Status, Akzeptanzkriterium, Test, Bestätigung. Sequenziell abarbeiten — erst grün, dann weiter. Restart-resilient."
metadata:
  node_type: memory
  type: project
  originSessionId: 2a244795-6433-466d-bd0f-f9d79e0e69c4
  mergedBy: claude-code-web-session 2026-07-12
---

# Migrations-Drehbuch — Netcup-VPS (Master)

**Start:** 2026-06-23 14:29 Uhr
**Status-Werte:** OFFEN · LÄUFT · VERIFIZIERT · BLOCKIERT
**Regel:** Sequenziell. Ein Punkt nach dem anderen. Erst grün, dann der nächste. Spontanes geht in den Backlog (Phase 11 unten), nicht in den laufenden Strang. Nach jedem Phasenwechsel kurzer Audit + Strategie-Recheck.
**Zusätzlich verbindlich:** Die Regeln aus `CLAUDE.md` (💰 Kostenregel, Nutzer-Workflow: ein Schritt pro Nachricht, keine `#`-Kommentare in zsh-Blöcken, pbpaste-Reihenfolge, Secrets nie in den Chat, jede Anweisung mit „Erwartete Ausgabe").

**Dokument-Hoheit:** Diese Repo-Version (`MIGRATION.md` im Bot-Repo) ist ab 2026-07-12 der Master. **Führender Branch: `mac-produktivstand`** — dort liegt der gepflegte Stand; jede Sitzung macht vor Arbeitsbeginn `git fetch` und liest/pflegt von diesem Branch. Die Telegram-Sitzung übernimmt diese Fassung als ihr Arbeitsdokument (Punkt 0.8) und pflegt Status-Updates darin; andere Sitzungen lesen vor Arbeitsbeginn den aktuellen Stand aus dem Repo.

---

## Änderungshistorie

Versionsverlauf mit Datum + Stichpunkt — neueste oben. Inline werden Änderungen zusätzlich mit `[NEU JJJJ-MM-TT HH:MM]` bzw. `[GESTRICHEN JJJJ-MM-TT]` markiert. Frische Marker bleiben sichtbar bis zum nächsten Lese-Pass und werden danach still entfernt; gestrichene Stellen bleiben eine Generation als `~~Durchstreichung~~` sichtbar, dann gelöscht.

- **2026-07-14** — **5.19 + 9.5 wiederhergestellt:** Beim Marker-Aufräumen am 13.07. waren die aktiven Punkte 5.19 (Rechnungs-Workflow) und 9.5 (E-Mail-Anbindung) samt Messenger-Backlog-Zeile versehentlich mitgelöscht worden — aus `d363d86` zurückgeholt. Dokument-Hoheit präzisiert: führender Branch `mac-produktivstand`.
- **2026-07-13** — **0.8 VERIFIZIERT:** Führende Desktop-Sitzung arbeitet mit Repo-MIGRATION.md und pflegt Status darin (Adam-Bestätigung 17:26 Uhr).
- **2026-07-12 (2)** — **F1 von Adam entschieden:** LiteLLM nur für Neben-Inferenzen, Claude-Agent bleibt am Abo-SDK — 2.6 entsprechend umformuliert und entsperrt. Neuer Punkt **1.0 Server-Zugang** eingefügt (Übermittlung der VPS-Zugangsdaten war bisher kein eigener Punkt).
- **2026-07-12** — **Zusammenführung** mit dem Drehbuch der Claude-Code-Web-Sitzung: Phase 0 (Code-/Repo-Vorbereitung am Mac) eingefügt; Ausführungsdetails als Anhang D; Rollback-Punkt 1.12; ⚠️-Klärung F1 an 2.6 (Kostenregel/Abo vs. LiteLLM); 9.4 Approval-Hub; Hinweise an 1.6/1.7/1.9/1.10. Entscheidungen E1–E4 vom Nutzer bestätigt (Kasten unten).
- **2026-06-23 18:18** — Punkt **5.18 Agent-Session-Watchdog** eingefügt (Hintergrund: live demonstrierter Claude-Session-Tod ab 16:11 am Migrationstag; strukturelle Lösung statt vorgezogenem Workaround).

---

## ✅ Bestätigte Entscheidungen / ⚠️ Offene Klärungen

| # | Thema | Stand |
|---|---|---|
| E1 | Ziel-Server | ✅ Netcup-VPS vorhanden (gemietet); Zugangsdaten-Übermittlung + SSH-Key-Einrichtung ist Punkt **1.0**. |
| E2 | Voice/STT | ✅ Bleibt vollwertig erhalten. Reihenfolge nach diesem Drehbuch: Whisper wird VOR dem Umschalten aufgebaut (1.3/1.4) → keine Voice-Lücke. |
| E3 | Modell | ✅ Sonnet als Grundeinstellung (`CLAUDE_MODEL` in .env, Punkt 0.6). Modell-Persistenz + **Empfehlung statt eigenmächtigem Wechsel** gemäß 5.6; Vollautomatik allenfalls später als Ausbau. |
| E4 | Approval-Hub | ✅ Separates Projekt nach der Migration → Punkt 9.4. |
| F1 | 💰 LiteLLM vs. Abo (betrifft 2.6) | ✅ **Entschieden (Adam, 2026-07-12):** LiteLLM nur für Neben-Inferenzen (Ampel-Klassifizierer, Zusammenfassungen → Ollama/Groq); der Claude-Agent bleibt direkt am Abo-SDK (`CLAUDE_CODE_OAUTH_TOKEN`). Rote Anfragen werden VOR dem Agenten abgefangen und lokal beantwortet. Kein `ANTHROPIC_API_KEY` im Stack. 2.6 ist entsprechend umformuliert. |
| F2 | Whisper medium auf VPS-CPU | Mini-Klärung in 1.4: medium (~1,5 GB) ist auf kleinem VPS spürbar langsamer als small — Akzeptanztest ausdrücklich inkl. Laufzeitmessung; bei Frust: base/small als Fallback dokumentieren. |

---

## Phase 0 — Code- & Repo-Vorbereitung (am Mac) `[NEU 2026-07-12]`

> Grund: Das GitHub-Repo enthält eine **veraltete** `bot.py` (~460 Zeilen). Die echte, produktive Version auf dem Mac hat **~2000+ Zeilen** (Watchdog, Heartbeat, TTS-Pfade, PDF/Foto/Link-Handling, Conversation-Logs …). Ohne Phase 0 klont Phase 1.7 den falschen Stand auf den Server. Referenz-Implementierungen (401-Handling, Abo-Token-Doku) liegen auf Branch `claude/telegram-bot-auth-401-g6yqrr`.

### 0.1 Echte bot.py + Zubehör ins Repo (KRITISCH)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Branch `mac-produktivstand` auf GitHub enthält die produktive `bot.py` (Plausibilität: `wc -l bot.py` > 1500), `transcribe.py`, `guardian.sh`, `requirements.txt`, `run.sh`; Commit-Hash Mac = GitHub.
- **Test:** `git log -1` lokal vs. GitHub; Zeilenzahl-Check. Befehle: Anhang D.0.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.2 Ist-Audit der echten bot.py
- **Status:** OFFEN
- **Akzeptanzkriterium:** Liste aller Mac-/Hardcoded-Pfade und Auth-Stellen liegt vor (`grep` nach `Users/jakuna`, `Mobile Documents`, `/opt/homebrew`, `ANTHROPIC_API_KEY`, `system_prompt`, Modell-Strings). Bekannt: Conversation-Log geht nach iCloud (`~/Library/Mobile Documents/…/Claude-Logs/`) — existiert auf Linux nicht.
- **Test:** Grep-Läufe (Anhang D.0) dokumentiert.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.3 401-/Fehler-Handling in echte bot.py portieren
- **Status:** OFFEN
- **Akzeptanzkriterium:** `is_auth_error()` + `AUTH_HELP` (Abo-Token-first!) + automatischer Session-Verwurf bei Auth-Fehlern in der echten bot.py; rohe SDK-Fehler erreichen Adam nicht mehr unkommentiert.
- **Test:** `py_compile` grün; simulierter 401 (Token kurz invalidieren) zeigt die freundliche Meldung.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.4 Neutrale Begrüßung (keine Kontext-Annahmen)
- **Status:** OFFEN
- **Akzeptanzkriterium:** System-Prompt-Zusatz via `{"type": "preset", "preset": "claude_code", "append": "…"}`: Bot nimmt nicht an, wo/an welchem Gerät Adam sitzt (kein „schön, dich am Desktop zu sehen").
- **Test:** Frische Session, Begrüßung prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.5 Mac-Pfade konfigurierbar machen (v. a. iCloud-Log)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Conversation-Log-Verzeichnis via env `CONVERSATION_LOG_DIR` (Mac darf weiter iCloud nutzen, Server nutzt lokalen Pfad); keine `/Users/…`- oder `/opt/homebrew`-Pfade mehr hart im Code; benötigte Verzeichnisse werden beim Start angelegt.
- **Test:** Audit-Liste aus 0.2 vollständig abgearbeitet; Bot startet mit gesetztem Alternativ-Pfad.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.6 Modell per .env (Sonnet-Default, E3)
- **Status:** OFFEN
- **Akzeptanzkriterium:** `CLAUDE_MODEL` (Default `sonnet`) wird gelesen und in `ClaudeAgentOptions(model=…)` gesetzt; `.env.example` dokumentiert.
- **Test:** Mit und ohne env-Variable starten, aktives Modell im Log/`/status` prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.7 Mac-Backtest des vorbereiteten Stands
- **Status:** OFFEN
- **Akzeptanzkriterium:** Bot läuft vom vorbereiteten Branch einmal manuell am Mac (launchd/Guardian währenddessen gestoppt!): Text, `/status`, `/reset`, Voice, Permission-Buttons — alles wie gewohnt. Danach Mac zurück auf Produktivstand bis zum Umschalten. **Der Punkt ist erst grün, wenn launchd + Guardian wieder GELADEN sind und `pgrep -fl bot.py` genau eine laufende Instanz zeigt** — ein gestoppter Wächter darf NIE über das Test-Fenster hinaus bestehen bleiben (Vorfall 2026-07-12: Bot blieb nach unterbrochenem Backtest down, weil der Guardian planmäßig aus war und niemand neu lud).
- **Test:** Die fünf genannten Interaktionen einzeln in Telegram.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 0.8 (Adam-Task) Master-Drehbuch der führenden Migrations-Sitzung übergeben
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Die **führende Migrations-Sitzung** (die Code-Sitzung am Mac, die Phase 0 ausführt) arbeitet nachweislich mit dieser Repo-Fassung (`git fetch` + aktuelle MIGRATION.md im Arbeitsordner) und betreibt die Status-Pflege hier. Falls die Telegram-Sitzung ein eigenes Drehbuch-Memory hält: durch Verweis auf die Repo-Fassung ersetzen (Zuständigkeiten: siehe CLAUDE.md → Anti-Ping-Pong-Regel).
- **Test:** Führende Sitzung nach Phase/Punkt fragen — Antwort deckt sich mit diesem Dokument (inkl. nachgeschärftem 0.7 und Alt-Log-Übernahme in 4.2).
- **Adam-Bestätigung:** ✅ 13.07.2026 — „Das aktuelle Drehbuch liegt als MIGRATION.md im Projektordner — bitte damit arbeiten und dort auch die Status pflegen."
- **Verifiziert am:** 13.07.2026 17:26 Uhr

### Phasen-Audit 0 → 1
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 1 — Server-Grundgerüst

### 1.0 Server-Zugang übermitteln & verifizieren `[NEU 2026-07-12]`
- **Status:** OFFEN
- **Hintergrund:** Hier findet der „profane" Teil des Umzugs statt — ohne
  funktionierenden Zugang keine Phase 1. Adam übermittelt die
  Netcup-VPS-Daten (Host/IP, SSH-User, Zugangsweg) an die ausführende
  Sitzung. Passwörter/Keys niemals in den Chat (CLAUDE.md-Regel) — Zugang per
  SSH-Key einrichten: Key lokal erzeugen, Public-Key auf den Server, fertig.
- **Akzeptanzkriterium:** `ssh <user>@<host> "hostname && uname -a"` läuft
  ohne Passwortabfrage (Key-Login); Host/IP + User sind im sicheren Ablageort
  notiert (nicht im Repo-Klartext); Netcup-SCP-Panel-Zugang (für Notfälle/
  Konsole) ist Adam bekannt.
- **Test:** Das eine SSH-Kommando ausführen, erwartete Ausgabe: Server-Hostname
  + Linux-Kernel-Zeile.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.1 System härten (Updates, ufw, fail2ban, unattended-upgrades)
- **Status:** OFFEN
- **Akzeptanzkriterium:** `apt-get upgrade` ohne offene Pakete; `ufw status` = active mit nur den freigegebenen Ports; `fail2ban-client status` läuft; `unattended-upgrades --dry-run` zeigt aktive Konfiguration.
- **Test:** SSH auf VPS, vier Kommandos ausführen, jeweils erwartete Ausgabe sichten.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.2 Unprivilegierter User claudebot
- **Status:** OFFEN
- **Akzeptanzkriterium:** `id claudebot` existiert, eigenes Home, **kein** sudo-Recht.
- **Test:** `id claudebot` + `sudo -u claudebot sudo -l` muss fehlschlagen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.3 Python 3.12, ffmpeg, whisper.cpp
- **Status:** OFFEN
- **Akzeptanzkriterium:** `python3.12 --version` = 3.12.x; `ffmpeg -version` läuft; `whisper-cli` (bzw. `main`) Binary vorhanden und ausführbar als claudebot.
- **Test:** Drei Kommandos, plus kurze Beispiel-Audio (deutsch+englisch gemischt) durch whisper jagen. Build-Befehle: Anhang D.1.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.4 Whisper-Modell-Upgrade small → medium
- **Status:** OFFEN
- **Akzeptanzkriterium:** `ggml-medium.bin` (~1,5 GB) am Modellpfad; Bot-Konfig nutzt es; vergleichende Transkription deutlich präziser als mit small. `[NEU 2026-07-12]` Zusätzlich: Laufzeit pro 30-Sek.-Probe auf VPS-CPU messen und festhalten; wird sie praxisuntauglich (> ~60 s), Entscheidung small vs. medium mit Adam (F2).
- **Test:** Eine deutsche und eine englische Sprachprobe (~30 Sek.) transkribieren, Output gegen small-Lauf vergleichen + Laufzeit notieren.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.5 Globales claude-CLI
- **Status:** OFFEN
- **Akzeptanzkriterium:** `claude --version` auf VPS läuft, aktuelle Version. `[NEU 2026-07-12]` Hinweis: Das Agent-SDK bringt eine gebündelte CLI mit — das globale CLI dient v. a. Setup/Debugging (`claude -p "hallo"`-Gegentest).
- **Test:** Kommando ausführen + Mini-Anfrage gegen Test-Endpunkt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.6 Headless-Auth (CLAUDE_CODE_OAUTH_TOKEN per setup-token)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Token gesetzt; `claude` antwortet auf Test-Inferenz ohne Browser-Flow. `[NEU 2026-07-12]` Eigener Token für den Server (getrennt vom Mac-Token, unabhängig widerrufbar); Ablage in `/etc/claude-telegram-bot.env` (root, `600`); 💰 NIEMALS `ANTHROPIC_API_KEY` als Ausweichlösung.
- **Test:** Mini-Inferenz "1+1=" → erwartet "2". SDK-Smoke-Test: Anhang D.2.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.7 Bot-Code auf Server (privates git-Repo)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Privates Repo auf VPS geklont; letzter Commit-Hash identisch mit Mac. `[NEU 2026-07-12]` Voraussetzung: Phase 0 abgeschlossen — sonst landet die veraltete bot.py auf dem Server!
- **Test:** `git log -1` auf beiden Seiten — gleicher Hash.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.8 systemd-Dienst statt launchd
- **Status:** OFFEN
- **Akzeptanzkriterium:** `systemctl status claude-telegram-bot` = active (running); Auto-Restart nach Kill greift. (Guardian wird auf dem Server NICHT nachgebaut — `Restart=always` + bot-interner Watchdog decken das ab.)
- **Test:** Dienst killen → spätestens nach 30 Sek. wieder active. Unit-Vorlage: Anhang D.3.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.9 Polling → Webhooks (HTTPS via Caddy oder nginx)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Telegram `getWebhookInfo` zeigt VPS-URL, letzter Fehler leer; Test-Nachricht trifft Bot in unter zwei Sekunden. `[NEU 2026-07-12]` Reihenfolge zwingend nach Anhang D.4: Der Umschalt-Arbeitsgang läuft zuerst über Mac-Stopp (1.10) + VPS-Start im Polling-Modus; die Webhook-Umstellung folgt als eigener Schritt erst nach stabilem Betrieb (erfordert Code-Anpassung run_polling → Webhook-Modus + Domain/TLS). Achtung bei Abweichung: Ein gesetzter Webhook deaktiviert getUpdates sofort — nie setzen, solange der Mac-Bot noch pollt.
- **Test:** Eine Telegram-Nachricht senden, Logs prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.10 Mac-Bot abschalten
- **Status:** OFFEN
- **Akzeptanzkriterium:** `launchctl list | grep telegram-bot` leer; Guardian-Plist ebenfalls deaktiviert; Telegram-Nachricht trifft NUR VPS-Bot (kein Token-Konflikt). `[NEU 2026-07-12]` Reihenfolge am Mac: Guardian zuerst entladen (sonst startet er den Bot neu), dann Bot-Plist, dann `pkill -f bot.py`, dann `pgrep -fl bot.py` = leer. Plists in `~/Library/LaunchAgents/_deaktiviert/` verschieben, nicht löschen (Rollback!).
- **Test:** Drei Kommandos + eine Test-Nachricht; Logs auf Mac bleiben still.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.11 Abschlusstest Phase 1
- **Status:** OFFEN
- **Akzeptanzkriterium:** Telegram-Text → Antwort; Voice → Transkription; ein Tool-Use-Schritt mit Permission-Buttons funktioniert. `[NEU 2026-07-12]` Plus 48-h-Kostenkontrolle: console.anthropic.com → Usage darf nicht steigen (Beweis: Abo, nicht API).
- **Test:** Drei konkrete Eingaben aus Telegram, jede einzeln beobachtet.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.12 Rollback-Pfad verifiziert `[NEU 2026-07-12]`
- **Status:** OFFEN
- **Akzeptanzkriterium:** Dokumentierter Rollback (Anhang D.5): VPS-Dienst stoppen, Telegram-Webhook löschen (`deleteWebhook`), Mac-Plists wieder laden → Mac-Bot antwortet binnen 2 Minuten. Einmal trocken durchgespielt, BEVOR Phase 2 beginnt.
- **Test:** Rollback ausführen, Mac-Bot antwortet; danach wieder auf VPS umschalten.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 1 → 2
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 2 — KI-Orchestrierung & Datenschutz

> **💰 Architektur-Leitplanke (F1, von Adam entschieden 2026-07-12):** Der Claude-**Agent** (Tools, Permission-Buttons) läuft über das Abo-SDK und wird NICHT durch LiteLLM ersetzt; LiteLLM orchestriert ausschließlich **Neben-Inferenzen** (Ampel, Zusammenfassungen, Link-Inbox) über Ollama/Groq. Rote Anfragen werden vor dem Claude-Agenten abgefangen. Keine Anthropic-Route in LiteLLM, kein `ANTHROPIC_API_KEY` im Stack.

### 2.1 LiteLLM-Proxy im SQLite-Modus
- **Status:** OFFEN
- **Akzeptanzkriterium:** LiteLLM-Dienst läuft als systemd-Unit; `/health`-Endpoint antwortet 200; SQLite-Datei initialisiert; kein Redis/Postgres.
- **Test:** Curl gegen `/health` + eine Test-Inferenz über LiteLLM.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.2 Datenschutz-Ampel als Gatekeeper (grün/gelb/rot)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Klassifizierer pro Anfrage liefert Farbe; rote Anfragen werden hart auf lokales Modell geroutet, niemals Richtung Cloud; Routing-Entscheidung im Log nachvollziehbar.
- **Test:** Drei Beispielanfragen (grün, gelb, rot) durchschicken, jeweils das gewählte Backend im Log prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.3 Lokales Fallback-Modell (Ollama + Phi-4 Mini Q4)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Ollama-Dienst läuft; `phi4-mini` geladen (~4 GB); LiteLLM-Route auf Ollama funktioniert.
- **Test:** Eine Inferenz explizit über das lokale Modell anfordern, Antwort kommt zurück.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.4 Groq als Cloud-Fallback (nur grün/gelb)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Groq-API-Key in LiteLLM eingetragen; Route aktiv; rote Anfragen werden hier explizit verweigert. `[NEU 2026-07-12]` 💰 Groq ist ein bezahlter/limitierter Fremd-Dienst — vor Einrichtung Kosten/Free-Tier mit Adam bestätigen (Kostenregel).
- **Test:** Eine grüne Anfrage mit Groq-Route + eine rote Anfrage prüfen (rot → Block).
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.5 Kein OpenAI im Stack
- **Status:** OFFEN
- **Akzeptanzkriterium:** Keine OpenAI-Route in LiteLLM, kein OpenAI-Key gesetzt.
- **Test:** `litellm` Routenliste durchgehen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.6 Neben-Inferenzen des Bots auf LiteLLM umstellen (F1 entschieden)
- **Status:** OFFEN
- ~~**Akzeptanzkriterium (Original):** Bot ruft Inferenzen nur noch über LiteLLM auf (kein direkter Anthropic-Endpoint im Code); Modellwahl funktioniert wie zuvor.~~ `[GESTRICHEN 2026-07-12 — hätte Claude-Verkehr vom Abo auf die bezahlte API verlagert und den Agent-Modus gebrochen]`
- **Akzeptanzkriterium:** Neben-Inferenzen des Bots (Ampel-Klassifizierung, Link-/Video-Zusammenfassungen, TTS-Vorstufen) laufen über LiteLLM (Ollama/Groq); der Claude-Agent (Kern-Sessions mit Tools/Permissions) bleibt direkt am Abo-SDK (`CLAUDE_CODE_OAUTH_TOKEN`). Kein `ANTHROPIC_API_KEY` im Stack. Rote Anfragen werden VOR dem Agenten abgefangen und lokal beantwortet.
- **Test:** Eine Anfrage in Telegram → LiteLLM-Log zeigt Treffer (für Neben-Inferenz); Agent-Anfrage läuft weiter über SDK; Usage-Konsole (console.anthropic.com) bleibt bei 0.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 2 → 3
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 3 — Interfaces

### 3.1 LobeChat als PWA (Web-Interface)
- **Status:** OFFEN
- **Akzeptanzkriterium:** LobeChat unter HTTPS erreichbar; mit LiteLLM verbunden; Login geschützt.
- **Test:** Vom Mac und vom iPhone öffnen, jeweils eine kurze Anfrage stellen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 3.2 (Ausbau, Phase 2.75) Matrix/Element als Rot-Kanal
- **Status:** OFFEN — terminiert auf Phase 2.75 (nach RAM-Upgrade)
- **Akzeptanzkriterium:** Synapse läuft, Element-Client verbindet sich, E2E-Test-Chat funktioniert.
- **Test:** Eine E2E-Nachricht hin und zurück.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 3 → 4
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 4 — Backup & Reproduzierbarkeit

### 4.1 Tägliches Backup VPS → Mac (rsync, switch-fähig)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Cron-Job läuft täglich; Ziel in Config-Datei konfigurierbar; Trockenlauf zeigt erwartete Dateien.
- **Test:** Eine Testdatei auf VPS, Backup auslösen, Datei am Mac suchen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 4.2 Zentrale Chat-Logs aller Interfaces auf dem VPS
- **Status:** OFFEN
- **Akzeptanzkriterium:** Telegram- und LobeChat-Konversationen werden als Tages-Markdown auf VPS abgelegt. (Baut auf 0.5 auf: `CONVERSATION_LOG_DIR` statt iCloud.) `[NEU 2026-07-13]` **Alt-Logs mitnehmen:** Das bestehende Log-Archiv vom Mac (iCloud-Ordner `…/CloudDocs/Claude-Logs/` + `~/claude-logs/`) wird einmalig auf den VPS ins zentrale Log-Verzeichnis übernommen — der Recall-Index (5.11) braucht die Historie. Nach verifizierter Übernahme wird der iCloud-Altbestand gelöscht (Datenschutz-Entscheid: Logs nicht in iCloud).
- **Test:** Je eine Nachricht aus beiden Frontends → beide Tageslogs zeigen den Eintrag. Plus: Stichprobe aus den Alt-Logs (ein alter Tageseintrag) ist auf dem VPS auffindbar; iCloud-Ordner danach leer.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 4.3 Memory + Configs in privates git-Repo (nicht iCloud)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Privates Repo angelegt; Memory-Ordner + LiteLLM-Configs + Bot-Configs committet; .gitignore deckt Secrets ab.
- **Test:** `git status` sauber; Probe-Restore in temporäres Verzeichnis funktioniert.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 4.4 Reproduzierbares Rebuild dokumentieren
- **Status:** OFFEN
- **Akzeptanzkriterium:** Setup-Anleitung (Markdown oder Skript) liegt im Repo; deckt System-Härten + Dienste + Auth + Routing ab.
- **Test:** Trockenlauf auf zweitem Test-VPS (optional, sonst Schreibtisch-Durchsicht).
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 4.5 (Adam-Task) iCloud ADP aktivieren
- **Status:** OFFEN — Adam-Aktion
- **Akzeptanzkriterium:** Apple-ID hat „Erweiterten Datenschutz" aktiv.
- **Test:** Sichtprüfung im iPhone unter Apple-ID → Datenschutz.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 4 → 5
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 5 — Bot-Features (mit/nach Migration)

### 5.1 Multi-Session (`/new`, `/sessions`, `/switch`, `/stop`)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Mehrere parallele Sessions je User möglich; Wechsel funktioniert; State wird persistiert (überlebt Bot-Neustart).
- **Test:** Zwei Sessions parallel anlegen, dazwischen wechseln, Bot killen, wieder hoch → Sessions noch da.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.2 Nachrichten-Queue + sofort-persistieren JEDER eingehenden Nachricht
- **Status:** OFFEN
- **Akzeptanzkriterium:** Jede eingehende Nachricht (Text, Voice, Foto, PDF, Link) wird beim Empfang sofort persistiert; Status (offen/in Bearbeitung/beantwortet) wird mitgeführt; Reboot mitten in der Bearbeitung verschluckt nichts.
- **Test:** Drei Nachrichten kurz hintereinander; während Verarbeitung Bot killen → Restart greift offene Nachrichten auf.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.3 Mehrere PDFs nacheinander
- **Status:** OFFEN
- **Akzeptanzkriterium:** Mehrere PDFs in einer Folge werden alle verarbeitet (nicht nur die letzte); file_id wird sofort eingelöst.
- **Test:** Drei PDFs in Folge senden, jede einzeln verarbeitet.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.4 Sekretariats-Board + `/status`
- **Status:** OFFEN
- **Akzeptanzkriterium:** Board mit offen/läuft/pausiert/fertig; `/status` rendert Board; pausierte Prozesse verfallen automatisch nach Verfall-Regeln.
- **Test:** Mehrere Aufgaben anlegen, einen pausieren; `/status` zeigt alle korrekt; Kontext-Ende → pausierter verfällt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.5 Priorisierung & Korrektur-Stichwörter
- **Status:** OFFEN
- **Akzeptanzkriterium:** „Korrektur/Stopp/Halt/warte" pausiert sofort; „Weiterführung/Weitermachen/Zufügen/Hinzufügen" baut in laufenden Strang ein, nicht als neue Aufgabe.
- **Test:** Beide Stichwort-Klassen einzeln auslösen, beobachten.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.6 Modell-Persistenz + Modell-Empfehlung
- **Status:** OFFEN
- **Akzeptanzkriterium:** Bot startet nach Neustart im zuletzt genutzten Modell; bei neuen anspruchsvollen Prozessen kommt eine Empfehlung statt eigenmächtigem Wechsel. `[NEU 2026-07-12]` Grundeinstellung Sonnet (0.6/E3); Empfehlungen können auch nach unten zeigen („Trivial-Anfrage → eher Haiku?"). Vollautomatischer Wechsel bleibt bewusst AUS (Adam-Entscheid E3); falls später gewünscht → Backlog.
- **Test:** Modell wechseln, Bot killen, wieder hoch → gleiches Modell; eine Trivial-Anfrage in Opus → Empfehlung „eher Sonnet?".
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.7 TTS opt-in (inkl. Bestätigungen, Voice + Text Kopplung)
- **Status:** OFFEN
- **Akzeptanzkriterium:** TTS-Toggle gilt für ALLE Bot→Adam-Pfade (auch Restart-/Status-Meldungen, vgl. `feedback-tts-also-confirmations`); bei aktivem TTS kommt Voice + Text mit Caption.
- **Test:** Eine inhaltliche Antwort + ein Restart triggern, beides mit Audio.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.8 Einheitlicher Sendepfad mit TTS-Hook (Refactor)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Alle ~30 verstreuten `reply_text`-Stellen laufen über zentralen `send_to_user`-Helper; Pre-Send-Hook (s. Punkt 8.5) dockt zentral an.
- **Test:** Code-Review + Stichprobentest mehrerer Pfade (PDF-Antwort, Restart, Voice-Echo).
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.9 Emoji-Reaktionen (Ja/Nein/erledigt)
- **Status:** OFFEN
- **Akzeptanzkriterium:** `message_reaction` Update-Typ wird ausgewertet; Vokabular gemäß Pin-Liste; Permission-Prompts behalten Inline-Buttons.
- **Test:** Auf eine Ja/Nein-Frage 👍 reagieren → wird als Ja erkannt; auf Aufgabe ✅ → „erledigt".
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.10 Konversations-Sync Telegram ↔ Claude Code (Stufe 1)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Telegram-Konversationen liegen als Markdown in einer Ablage, die Claude Code direkt lesen kann.
- **Test:** Aus Claude Code einen Tageslog referenzieren.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.11 Verlässlicher Session-Recall (Stufe 2, Index-Mechanismus)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Bot baut Recall-Index aus Tageslogs; auf „weißt du noch X" wird sicher die richtige Stelle gefunden; mehrere Richtungen getestet.
- **Test:** Drei verschiedene Recall-Anfragen aus unterschiedlichen Zeiträumen, jeweils korrekter Treffer.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.12 Video-/YouTube-Analyse als Bot-Feature
- **Status:** OFFEN
- **Akzeptanzkriterium:** YouTube-URL oder Video-Datei → Pipeline (Untertitel/Whisper + Frames mit Zeitstempeln + adaptives Sampling) liefert sinnvolle Zusammenfassung.
- **Test:** Ein einfaches und ein Chart-lastiges Video durchschicken.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.13 Pinned-Nachricht → Memory-Funktion
- **Status:** OFFEN
- **Akzeptanzkriterium:** Eine angepinnte Nachricht wird automatisch als Memory abgelegt (mit Zitat-Bezug).
- **Test:** Eine Nachricht pinnen, Memory-Ordner prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.14 Link-Inbox (Zusammenfassen / Vertiefen / Volltranskript)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Beim Link-Eingang nur schlanker Index (Titel, Quelle, Dauer, Topic); drei Buttons aktiv; Routing nach Quellkanal; Verarbeitung erst auf Knopfdruck. Strukturierte Vertiefung legt Kernpunkte in Memory ab.
- **Test:** Je einen YouTube-, Instagram- und Web-Link prüfen; jeden Button einmal nutzen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.15 Sprach-Behandlung Whisper (deutsch forciert, englische Passagen separat)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Default-Sprache deutsch; längere englische Passagen werden zusätzlich englisch transkribiert + Übersetzung daneben gestellt; YouTube-Untertitel werden zuerst geprüft.
- **Test:** Eine deutsche, eine englische und eine gemischte Probe durchspielen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.16 Reverse-Navigation `/woist`
- **Status:** OFFEN
- **Akzeptanzkriterium:** Reply auf eigene Nachricht + `/woist` liefert Deep-Link auf zugehörige Antwort; falls noch in Queue → klare Meldung.
- **Test:** Drei Beispiele aus unterschiedlichen Zeiträumen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.17 Kanal-/Topic-Bewusstsein im Recall
- **Status:** OFFEN
- **Akzeptanzkriterium:** Bei Recall-Aussagen über fremde Kanäle/Topics wird Plattform + Kanal + Topic mitgenannt; fremde Sammelgruppen werden nicht in den Hauptchat hochgespült.
- **Test:** Eine Frage stellen, die ein Topic in einer anderen Gruppe berührt → Recall nennt den Ort sauber.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.18 Agent-Session-Watchdog (Claude-Session-Tod erkennen + auffangen)
- **Status:** OFFEN
- **Hintergrund:** Heartbeat (`bot.py` + `guardian.sh`, fertig am Migrationstag-Vormittag) deckt nur die Bot-Wedge ab. Der seltenere, aber sehr ärgerliche Fall „Bot lebt, aber meine Claude-Agent-Session ist tot" (live demonstriert am 23.06. ab 16:11 — Bot munter, Session weg, Adam fragte ins Leere) wird strukturell mit der Multi-Session/Queue gelöst.
- **Akzeptanzkriterium:** Pro User-Nachricht wird der letzte Streaming-/Antwort-Zeitpunkt mitgeführt. Liegt für eine Nachricht im Status „in Bearbeitung" länger als ein konfigurierbares Limit (Default 5 Min) kein Streaming + keine Antwort vor: Bot meldet Adam aktiv „Claude-Session reagiert nicht — starte neu, bitte letzte Nachricht ggf. nochmal", beendet die hängende Session sauber und legt eine frische an. Status der Nachricht wird auf „erneut offen" gesetzt, damit nichts verloren geht.
- **Test:** Künstlich hängende Session simulieren (Sleep im Tool-Handler über Limit hinaus); Watchdog muss innerhalb von max. Limit + 30 Sek. melden, Session schließen, neue starten — und die unbeantwortete Nachricht wieder in den Pending-Status setzen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.19 Rechnungs-Workflow per Sprache (Aufstellung + Rechnung aus dem Bot) `[NEU 2026-07-13]`
- **Status:** OFFEN
- **Hintergrund:** Beide Generatoren sind fertig und real erprobt (Desktop-Session „Rechnungs-Automatisierung", `~/Projects/rechnungen`: `scripts/generate_aufstellung.py` = Postenaufstellung Excel+PDF, `scripts/generate_rechnung.py` = Rechnungs-PDF im Markenlayout mit Auto-Nummer pro Jahr; Rechnungen 014-26/015-26 damit produktiv erstellt und in iCloud abgelegt). Hier fehlt nur die Bot-Anbindung. Details/Konventionen: Memory `project-rechnungs-automatisierung`.
- **Akzeptanzkriterium:** Adam gibt per Sprachnachricht Tage/Tätigkeiten durch; Bot fragt Variables gezielt nach (Tagessatz, Spesen In-/Ausland, Übernachtung, Fahrzeug/Pauschalen), erzeugt über die vorhandenen Generatoren Aufstellung (Excel+PDF) + Rechnung (PDF), legt beides nach Abnicken im richtigen iCloud-Projektordner ab (Benennungsschema je Zweig) UND postet die Dateien zur schnellen Kontrolle in den Ausgabekanal (Phase 6). Rechnungsnummer fortlaufend (Register), mit Bestätigungs-Rückfrage vor Vergabe.
- **Test:** Eine komplette Rechnung per Sprache vom iPhone: Zuruf → Rückfragen → Dateien liegen im iCloud-Ordner + im Ausgabekanal → Beträge und Nummer stimmen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 5 → 6
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 6 — Kanal-Routing / Ablage

### 6.1 Ausgabekanal generisch für ALLE Auswertungen
- **Status:** OFFEN
- **Akzeptanzkriterium:** PDF, Video, Foto, Recherche landen alle im Ausgabekanal; Hinweis im Bot-Chat mit Deep-Link.
- **Test:** Je eine Auswertung pro Typ.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 6.2 Fix: Deep-Link via `tg://privatepost`
- **Status:** OFFEN
- **Akzeptanzkriterium:** Links öffnen auf iPhone direkt in der Telegram-App, kein Browser-Umweg; Fallback `t.me/c` bleibt optional.
- **Test:** Vom iPhone tappen, ohne Web-Login direkt im Kanal landen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 6.3 Original-Datei im Ausgabekanal anklickbar
- **Status:** OFFEN
- **Akzeptanzkriterium:** Quell-Datei wird mit hochgeladen oder als klickbarer Link eingebettet (nicht nur Dateiname).
- **Test:** Ein PDF und ein Video durchgehen, Originale anklicken.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 6.4 Ausgabekanal überall als anklickbaren Link rendern
- **Status:** OFFEN
- **Akzeptanzkriterium:** Jeder Bot-Hinweis und meine eigenen Erwähnungen des Kanals sind tappbare Links zur App.
- **Test:** Drei verschiedene Auslöser, jeweils anklicken.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 6.5 (Ausbau) Kanal/Topic pro Projekt, Bot legt Topics selbst an
- **Status:** OFFEN — Ausbau, später
- **Akzeptanzkriterium:** Forum-Gruppe; Bot kann via `createForumTopic` Topics anlegen; automatisches Routing.
- **Test:** Neues Projekt anlegen → Topic erscheint → Auswertung landet dort.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 6.6 Empfehlungsliste anzulegender Kanäle liefern
- **Status:** OFFEN
- **Akzeptanzkriterium:** Vorschlagsliste mit Begründung (Kanal vs. Topic) liegt vor, Adam wählt aus.
- **Test:** Liste durchgehen, Adams Auswahl notieren.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 6 → 7
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 7 — Erinnerungskanal

### 7.1 Eigener Telegram-Erinnerungskanal
- **Status:** OFFEN
- **Akzeptanzkriterium:** Kanal existiert; Bot ist Admin mit Schreibrechten.
- **Test:** Test-Erinnerung schicken, im Kanal sichtbar.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 7.2 Scheduler (24/7 auf VPS)
- **Status:** OFFEN
- **Akzeptanzkriterium:** APScheduler oder systemd-Timer plant Jobs; läuft auch ohne Mac.
- **Test:** Erinnerung für 5 Minuten später anlegen → kommt pünktlich.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 7.3 Serverfähige Kalenderquelle (Google Calendar oder CalDAV)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Auf VPS lesbar; OAuth-Flow durchgängig; nur freigegebene Kalender filtern.
- **Test:** Termin im Quell-Kalender → Erinnerung im Kanal.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 7.4 Direkte Links in Erinnerungen
- **Status:** OFFEN
- **Akzeptanzkriterium:** Zoom-/YouTube-Links werden aus Beschreibung/Ressource extrahiert und mitgeschickt.
- **Test:** Termin mit Zoom-Link → Link kommt mit.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 7 → 8
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 8 — Tests & Selbstüberwachung

### 8.1 Täglicher 4-Uhr-Funktionscheck (zentrale Sammelstelle)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Systemd-Timer um 04:00 MEZ; prüft Token gültig, API erreichbar, TTS-Cleanup-Selbsttest, Migrations-Endpunkte; Bericht ins Bot-Log + bei Fehler Telegram-Hinweis.
- **Test:** Manueller Auslöser → Bericht erscheint.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.2 Regressionstest nach jeder größeren Änderung
- **Status:** OFFEN
- **Akzeptanzkriterium:** Isolierter Read-only-Test-Lauf, der nach einem Deploy/Change automatisch durchgezogen wird; Ergebnis sichtbar.
- **Test:** Eine simulierte Änderung → Regressionstest läuft + meldet grün/rot.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.3 Vollständigkeits-Check bei jedem Neustart
- **Status:** OFFEN
- **Akzeptanzkriterium:** Bot prüft beim Start, ob seit letzter Antwort Adam-Nachrichten unbeantwortet liegen; falls ja → Hinweis.
- **Test:** Nachricht senden während Bot down, Restart, Hinweis kommt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.4 Einmaliger Code-Aufräumpass (nur auf Vorschlag)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Karteileichen-Liste (Code + Memory) liegt vor; Adam entscheidet Punkt für Punkt; nichts wird eigenmächtig geändert.
- **Test:** Liste durchgehen, Stichproben verifizieren.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.5 Pre-Send-Hook (Datums-/Bezugs-/Vollständigkeits-Check)
- **Status:** OFFEN — Kernpunkt
- **Akzeptanzkriterium:** Zentraler Hook am Sendepfad; (a) zeitliche Aussagen gegen Systemdatum verifiziert, (b) Bezug auf Nachricht prüft Absender+Uhrzeit+Inhalt, (c) Vollständigkeits-Check seit letzter Antwort, (d) erweiterbar.
- **Test:** Bewusst eine falsche Datumsangabe formulieren → Hook blockiert/korrigiert; gleiches für falsche Nachrichten-Referenz.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 8 → 9
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 9 — Danach (Aufsetzen auf fertige Struktur)

### 9.1 TTS-Upgrade Azure Neural mit SSML-Sprach-Switch
- **Status:** OFFEN
- **Akzeptanzkriterium:** Azure-Stimme aktiv; SSML-Tags trennen deutsch/englisch sauber; Mischtext klingt korrekt. `[NEU 2026-07-12]` 💰 Azure ist ein bezahlter Dienst — vor Einrichtung Kosten mit Adam bestätigen (Kostenregel).
- **Test:** Drei Mischtexte vorlesen lassen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 9.2 Piper/Kokoro lokal als Rot-Backend
- **Status:** OFFEN
- **Akzeptanzkriterium:** Eine lokale Stimme verfügbar, läuft auf VPS-CPU, Qualität akzeptabel.
- **Test:** Eine deutsche Probe lokal sprechen lassen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 9.3 Demo-Bot-Klon für ersten Klienten
- **Status:** OFFEN
- **Akzeptanzkriterium:** Eigener Bot mit eigenem Token, leerer Memory, eigener API-Key mit Spend-Limit; Freigabeliste enthält nur Adam + Klient. (Hinweis: Hier ist ein API-Key richtig und gewollt — professioneller/kommerzieller Einsatz, getrennte Abrechnung; Spend-Limit ist Pflicht.)
- **Test:** Mit Klient gemeinsamer Testdurchlauf (Link → Auswertung).
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 9.4 Approval-Hub — Freigaben ALLER Claude-Sitzungen in Telegram `[NEU 2026-07-12]`
- **Status:** OFFEN (Entscheidung E4: nach der Migration)
- **Akzeptanzkriterium:** Permission-Anfragen beliebiger Claude-Sitzungen (Desktop, Web) laufen mit Sitzungs-Kennung im Telegram-Bot auf und sind per Button freigebbar. Skizze: kleiner HTTP-Endpoint im Bot (VPS ist 24/7 erreichbar) + pro Sitzung ein Hook/Wrapper, der `can_use_tool`-Entscheidungen dorthin delegiert.
- **Test:** Eine Desktop-Sitzung stellt Permission-Frage → Button-Prompt erscheint in Telegram mit Sitzungs-Kennung → Freigabe wirkt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 9.5 E-Mail-Anbindung (SMTP/IMAP) — Rechnungen & Anschreiben direkt versenden `[NEU 2026-07-13]`
- **Status:** OFFEN
- **Hintergrund:** Adam-Wunsch: „schick das raus" genügt — Anschreiben formulieren, Rechnung anhängen, Versand ohne Handarbeit; muss auch aus dem Telegram-Bot heraus funktionieren. Zwei Konten: `falkogorski@mailbox.org` (geschäftlich; `imap.mailbox.org:993` / `smtp.mailbox.org:465`, SSL/TLS) und `falkogorski@posteo.de` (privat; `posteo.de:993/465`, SSL/TLS). Je Konto EIN App-Passwort — gilt inkl. aller Aliasse und funktioniert auch bei aktiver 2FA; Anleitungen zum Anlegen hat Adam. Details: Memory `project-kommunikationskanaele`.
- **Akzeptanzkriterium:** Beide Konten mit App-Passwörtern verschlüsselt hinterlegt (Secrets nie im Chat, nie im Klartext-Repo — CLAUDE.md-Regel); Senden über beliebigen Alias und Lesen funktionieren. 💰 Keine Zusatzkosten (Standard-Protokolle, kein API-Abo). **Versand IMMER erst nach expliziter Adam-Bestätigung** — Empfänger, Betreff und Anhang werden vorher angezeigt.
- **Test:** Test-Mail mit PDF-Anhang von beiden Konten an Adam selbst, per Telegram ausgelöst; danach eine echte Rechnung mit Anschreiben nach Freigabe.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 9 → Abschluss
- **Audit-Status:** —
- **Strategie-Recheck:** —

---

## Phase 10 — Abschluss-Audit

### 10.1 Gesamtaudit
- **Status:** OFFEN
- **Akzeptanzkriterium:** Drehbuch von oben durchgegangen; jeder Punkt VERIFIZIERT oder explizit in „Nacharbeiten" verschoben.
- **Test:** Durchlauf zu zweit, Stichprobentests pro Phase.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

---

## Phase 11 — Backlog (während der Migration aufgetauchtes)

*Sammelstelle für spontane Ideen, neue Anforderungen, Beobachtungen. Wird NIEMALS in den laufenden Punkt gezogen — kommt erst nach Phasen-Audit dran.*

- `[NEU 2026-07-12]` Vollautomatische Modellwahl je Aufgabe (Ausbau von 5.6, nur falls Adam sie nach Praxiserfahrung mit den Empfehlungen doch wünscht).
- `[NEU 2026-07-12]` `/status` erweitern um aktives Modell + Session-Alter + Kontingent-Hinweis (falls nicht schon durch 5.4/5.6 abgedeckt).
- `[NEU 2026-07-13]` **Anti-Ping-Pong strukturell lösen:** Anliegen, die bei der „falschen" Instanz eingehen, sollen automatisch richtig landen — z. B. Bot beantwortet Drehbuch-/Statusfragen selbst aus der Repo-Fassung statt zu verweisen; perspektivisch gemeinsame Aufgaben-Inbox (verwandt: 5.10 Konversations-Sync, 9.4 Approval-Hub, CLAUDE.md-Zuständigkeitsregel).
- `[NEU 2026-07-13]` Messenger-Versand als Ausbau von 9.5 (Telegram via Bot-API machbar; WhatsApp heikel: Business-API kostenpflichtig 💰, inoffizielle Wege riskant/ToS) — erst nach stabiler E-Mail-Anbindung bewerten.

---

## Nacharbeiten

*Punkte, die am Ende offen geblieben sind und Schritt für Schritt nachgeholt werden.*

(leer)

---

## Strategie-Audit-Log

*Pro Phasenwechsel: kurzes Resümee + Anpassungen der Folge-Phasen.*

(leer)

---

## Anhang D — Ausführungsdetails `[NEU 2026-07-12]`

> Konkrete, geprüfte Befehlssequenzen für die Phasen 0–1. Für Adam gilt beim
> Ausführen: ein Block pro Nachricht, keine `#`-Kommentare (zsh!), jede
> Sequenz endet mit einem Check + erwarteter Ausgabe.

### D.0 — Phase 0.1/0.2: Produktivstand pushen + Audit

Am Mac:
```bash
cd ~/Projects/claude-telegram-bot
git checkout -b mac-produktivstand
git add bot.py transcribe.py guardian.sh requirements.txt run.sh
git commit -m "Produktivstand vom Mac"
git push -u origin mac-produktivstand
wc -l bot.py
```
Erwartet: `[new branch] mac-produktivstand`; Zeilenzahl > 1500.

Audit (ausführendes Modell, auf dem Branch):
```
grep -n "Users/jakuna\|Mobile Documents\|/opt/homebrew\|iCloud" bot.py
grep -n "ANTHROPIC_API_KEY" bot.py transcribe.py
grep -n "system_prompt" bot.py
```

### D.1 — Phase 1.3: whisper.cpp bauen (als root auf VPS)
```bash
apt-get install -y ffmpeg build-essential cmake git
sudo -u claudebot git clone https://github.com/ggerganov/whisper.cpp /home/claudebot/whisper.cpp
cd /home/claudebot/whisper.cpp && sudo -u claudebot cmake -B build && sudo -u claudebot cmake --build build -j --config Release
ln -sf /home/claudebot/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli
whisper-cli --help | head -n 3
```
Modell (Phase 1.4, medium ~1,5 GB):
```bash
sudo -u claudebot mkdir -p /home/claudebot/claude-telegram-bot/models
sudo -u claudebot curl -L -o /home/claudebot/claude-telegram-bot/models/ggml-medium.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
ls -lh /home/claudebot/claude-telegram-bot/models/ggml-medium.bin
```

### D.2 — Phase 1.6: EnvironmentFile + SDK-Smoke-Test

`/etc/claude-telegram-bot.env` (root, `chmod 600`):
```
TELEGRAM_BOT_TOKEN=…
ALLOWED_USER_IDS=304455165
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat…
CLAUDE_WORKDIR=/home/claudebot/workspace
CLAUDE_MODEL=sonnet
STT_BACKEND=whisper_cpp
WHISPER_MODEL_PATH=/home/claudebot/claude-telegram-bot/models/ggml-medium.bin
CONVERSATION_LOG_DIR=/home/claudebot/claude-telegram-bot/logs/conversations
VOICE_LANGUAGE=de
```
Server-Token separat am Mac erzeugen (`claude setup-token`), Übertragung ohne
Chat-Kontakt (pbpaste-Regel!).

Smoke-Test vor Bot-Start:
```bash
sudo -u claudebot bash -c 'set -a; . /etc/claude-telegram-bot.env; set +a; /home/claudebot/claude-telegram-bot/.venv/bin/python - <<PY
import anyio
from claude_agent_sdk import query, AssistantMessage, TextBlock
async def main():
    async for m in query(prompt="Sag nur: OK"):
        if isinstance(m, AssistantMessage):
            print("".join(b.text for b in m.content if isinstance(b, TextBlock)))
anyio.run(main)
PY'
```
Erwartet: `OK`. Bei 401: Token prüfen — NIE auf API-Key ausweichen.

### D.3 — Phase 1.8: systemd-Unit

`/etc/systemd/system/claude-telegram-bot.service`:
```ini
[Unit]
Description=Claude Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=claudebot
WorkingDirectory=/home/claudebot/claude-telegram-bot
EnvironmentFile=/etc/claude-telegram-bot.env
ExecStart=/home/claudebot/claude-telegram-bot/.venv/bin/python bot.py
Restart=always
RestartSec=5
StandardOutput=append:/home/claudebot/claude-telegram-bot/logs/bot.out.log
StandardError=append:/home/claudebot/claude-telegram-bot/logs/bot.err.log

[Install]
WantedBy=multi-user.target
```
`daemon-reload` + `enable`, aber **erst im Umschaltmoment starten** (D.4).

### D.4 — Phase 1.9/1.10: Umschalt-Sequenz (ein Arbeitsgang!)

1. Mac: Guardian entladen → Bot-Plist entladen → `pkill -f bot.py` →
   `pgrep -fl bot.py` (Erwartet: leer).
2. VPS: `systemctl start claude-telegram-bot` → Log-Check: `Application
   started`, kein `401`, kein `Conflict`.
3. Erst NACH stabilem Polling-Betrieb: Webhook-Umstellung (1.9) als eigener
   Schritt (Code-Anpassung + Caddy/TLS); `getWebhookInfo` prüfen.
4. Telegram-Tests laut 1.11.

### D.5 — Phase 1.12: Rollback
```bash
sudo systemctl stop claude-telegram-bot
```
Falls Webhook schon gesetzt: `deleteWebhook` via Bot-API aufrufen.
Mac: Bot-Plist laden, dann Guardian-Plist laden → Test-Nachricht. Dauer < 2 Min.

### D.6 — Mac-Dateien vom Server (optional, kein Migrationsbestandteil)
Syncthing (robust, bidirektional) oder SSHFS (live, fragiler). Eigene
Entscheidung nach Bedarf.
