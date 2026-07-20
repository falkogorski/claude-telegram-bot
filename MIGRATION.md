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

- **➡️ AKTUELLER ARBEITSSTRANG (20.07.2026):** **Phase 1 abgeschlossen** (1.11 verifiziert; nur 1.9 Webhooks bewusst zurückgestellt). **5.2 VERIFIZIERT** (Kill-Test bestanden). **5.18 gebaut, lokal verifiziert — offen ist nur noch Adams VPS-Test.** Danach in dieser Reihenfolge die Aufträge vom 19.07.: **5.9** (Emoji-Reaktionen auf ALLE Bot-Fragen, Vokabular: `reaktionen-vokabular.md`), **8.6 (b)** (Prüfskript `check_hilfe_buttons.py`), **8.7** (technische Verankerung Schreibschutz VPS-Repo). Erst danach Phase 3 (LobeChat). ~~Weiter mit 5.22/5.23~~ *(erledigt: STT-Umschalter live, Session-Diät umgesetzt)*.
- **2026-07-20 (2)** — **5.18 Session-Wächter gebaut** („Bot lebt, Claude-Session tot"). Zweite Wächter-Schleife neben der bestehenden; Lebenszeichen bei jeder SDK-Nachricht, Abbruch **lockfrei**, Nachricht über den 5.2-Record gerettet, Adam wird aktiv benachrichtigt. Drei Fallen bewusst umgangen: die Sperre (ein wartender Wächter ist ein wirkungsloser), wartende Freigaben (Stille ist dort gewollt), Endlos-Wiederholung (max. 1 Anlauf, sonst frisst ein Problemfall dauerhaft Abo-Kontingent). Selbstcheck **13/13**; zusätzlich Verhaltenstest `scripts/test_stall_5_18.py` (alle Zweige bestanden). Die neue Selbstcheck-Zeile schlug beim ersten Lauf **gegen mich selbst** an — der verbotene Sperr-Aufruf stand wörtlich im Docstring; genau dafür ist sie da. Offen: Adams Test auf dem VPS. Nächst danach: 5.9 / 8.6b / 8.7.
- **2026-07-20** — **5.2 VERIFIZIERT (Kill-Test bestanden) + stiller Antwortverlust behoben.** Adams Kill-Test auf dem VPS: „Blume" (Status `offen`) **automatisch nachgeholt**, die lange Frage (`in_bearbeitung`) **nur gemeldet** — beide Hybrid-Zweige wie beschlossen, jede Antwort genau einmal, `logs/pending/` danach leer. **Nebenbefund:** Die beiden Schutznetze ergänzen sich lückenlos (eigene Persistenz für Empfangenes, Telegram-Nachzustellung für noch nicht Angekommenes — s. Beleg in 5.2). **Vorher aufgedeckt und behoben (`be6023a`):** stiller Antwortverlust bei TTS-Ausfall — `_send_tts_chunk` gab bei Netzwerkfehler `None` zurück, der Sendepfad prüfte es nicht und hatte keinen Text-Fallback, `_run_job` hakte trotzdem „beantwortet" ab und löschte den Record (live passiert am 19.07. mit „Nenn mir eine Stadt"). Jetzt: **Text-Fallback** + **Zustellnachweis** (`send_answer_to_user -> bool`), beides im Register verankert. Selbstcheck **12/12**. ⚠️ Beim ersten Testlauf lief unbemerkt noch der alte Stand (Selbstcheck sagte 10) — **Merkregel: vor jedem Test die Selbstcheck-Zahl als Deploy-Beweis lesen.** Nächst: 5.18.
- **2026-07-19** — **Phase 1 GESCHLOSSEN + 5.2 Schritt 1 live + Doku-Spiegel-Drift behoben + drei neue Aufträge aufgenommen.** (a) **1.11 verifiziert** (Adam: 48-h-Kostenkontrolle ohne Usage-Wachstum → Abo-Beweis 💰) → **Phase 1 abgeschlossen**, nur 1.9 (Webhooks) bleibt bewusst zurückgestellt. (b) **5.2 Schritt 1 deployt & abgenommen:** Selbstcheck **10/10** auf dem VPS, `/status` zeigt korrekt keine Records nach sauberer Abarbeitung. (c) **Doku-Spiegel-Drift (neuer Punkt 8.6):** `/hilfe` zeigte noch das 12-Button-Layout — Ursache **nicht** ein VPS-Live-Fix (Klon ist sauber, geprüft), sondern der nie nachgezogene Text im Repo; korrigiert, dabei zwei weitere Lücken gefunden (`/ampel`, `/presend` fehlten) **plus zweite Drift-Quelle**: die Startup-Begrüßung meldete 4.1/8.5 als „noch offen" (aus `pending-items.md` im VPS-Memory) → abgehakt, Bot meldet jetzt 0 offene Punkte. Regel dazu in CLAUDE.md („nutzerseitige Texte im selben Commit"); Prüfskript `check_hilfe_buttons.py` bleibt offen als 8.6 (b). (d) **Neuer Punkt 8.7 Governance:** Bot editiert die VPS-Repo-Kopie nie (nur lesen; Deploy ausschließlich per `git pull` durch Adam) — Regel in CLAUDE.md, technische Verankerung offen. (e) **5.9 erweitert:** Reaktionen sollen JEDE Bot-Frage beantworten können; Pin-Liste 1:1 als [`reaktionen-vokabular.md`](reaktionen-vokabular.md) im Repo und dort verbindlich verlinkt (inkl. Vorbehalt: Telegram gibt die erlaubten Reaktions-Emoji vor → beim Bau messen, für Nicht-Unterstütztes gleichwertigen Weg vorsehen).
- **2026-07-17 (4)** — **5.2 Schritt 1 gebaut & lokal verifiziert (Nachrichten-Persistenz).** Neues Modul `pending.py` (atomare Per-Nachricht-JSON in `logs/pending/`, tmp+`os.replace`, fehlertolerant). Persistenz im Trichter `process_user_text` (nur serialisierbare Primitive; Anhang-Pfad steckt bereits im `text` → kein Sonderfall). `_run_job` gibt jetzt seinen **Ausgang** zurück (`beantwortet`/`aufgegeben`/`offen`/`fehler`); der Worker zieht daran den Status nach bzw. löscht den Record. Selbstcheck erweitert → **10/10 grün** (neue Invariante „Nachrichten-Persistenz (5.2)", record→set_status→resolve-Roundtrip); `/status` zeigt liegende Records. Register (`ABHAENGIGKEITEN.md`) um die neue Kette ergänzt (⚠️ die vier `_run_job`-Rückgabe-Strings sind ein stiller Bezug). **Rein additiv, Hauptpfad unverändert.** Nächst: Deploy + Adam-Test (Selbstcheck grün, `/status`-Persistenz „atmet"), dann **Schritt 2** (Startup-Reconcile Hybrid) + **5.18** (Watchdog).
- **2026-07-17 (3)** — **Post-Deploy-Feinschliff + `._`-Backup-Hygiene + 5.2/5.18-Vorbereitung.** 8.5 auf VPS deployt & getestet (Adam: alle 3 grün — 🔧-Spur, Tipp-Indikator, „/"-Menü). Nachgezogen: **Default verbose** (`quiet=False`, Tipp-Indikator läuft von Haus aus; `90d0ac1`), **Tastatur verschlankt 12→9** (Neustart/TTS/Info nur noch im „/"-Menü; `426a7f3`). **`._`-Mini-Punkt erledigt:** `--exclude='._*'`+`.DS_Store` im Backup-Skript, Mac-Kopie + VPS-Quelle bereinigt, Herkunft = tar-Migration 14.07. **5.2/5.18:** Architektur per Subagent kartiert, Umsetzungsplan verdichtungsfest eingetragen; **Adam-Entscheid Neustart-Verhalten = Hybrid** (offen→auto nachbearbeiten mit Vermerk, in-Bearbeitung→nur melden). Nächst: `/compact`, dann 5.2-Bau; 1.11 meldet Adam morgen.
- **2026-07-17 (2)** — **8.5-Nachbesserungen + Backup voll verifiziert + Worktree-Falle beseitigt (Adam-Aufträge).** (a) **8.5:** 🔧-Werkzeug-Spur jetzt IMMER sichtbar (quiet-Sperre raus, Kern der Puffer-Option 1) + Tipp-Indikator (`TYPING`-Keepalive) für werkzeuglose Turns; `/quiet`/`/verbose` dämpfen jetzt den Indikator, Texte ehrlich nachgezogen; **`setMyCommands`** macht `/presend` & Co. auffindbar. Selbstcheck 9/9 ok. (b) **4.1 Restore-Probe BESTANDEN** → Backup voll verifiziert: `ampel_rules.toml` tomllib-parsebar, MEMORY.md-Links 71/71 auflösbar; Nebenbefund `._`-AppleDouble-Ballast (Empfehlung `--exclude='._*'`). (c) **Worktree-Falle:** Sitzung startete im Streu-Worktree `migration-md-location` (Stand VOR den Schutz-Hooks, ohne die 8.5-Arbeit) — erkannt, **bevor** etwas Falsches gebaut wurde, korrigiert auf `mac-produktivstand`; Streu-Worktree(s) am Sitzungsende entfernt inkl. Branch. (d) **Zwischen-Audit vor Phase 3** als Pflicht-Tor am Phase-3-Kopf eingetragen (5.1/5.2/5.18-Vorzieh-Abwägung; Empfehlung liegt vor: 5.2+5.18 vorziehen ~1–1,5 T, 5.1 später ~1–2 T; Adam entscheidet).
- **2026-07-17** — **8.5 Pre-Send-Hook v1 LIVE (`91950ef`) + Sendepfad-Umbau (Vorstufe 5.8).** `stream_response` sammelt jetzt statt blockweise zu senden → erstmals vollständiger Text vor dem Senden; `presend.py` (Wochentag-Autofix, Vollständigkeit→Korrekturrunde, Rest nur Log), `/presend`-Kennzahlen. Analyse per Subagenten deckte 3 Fallen auf (Zeitbasen-Falle, lügende Zeitzeile, Autorun-Stumm) — alle behoben, Bezüge im Register. Adam-Grundtests ✅. Offen klein: 🔧-Spur unsichtbar (quiet=True Default), `/presend` in setMyCommands. v2: Bezugs-Check + Sicherheits-Check (im Gründlich-Modus). **Adam-Aufträge 17.07. dokumentiert:** Restore-Probe (4.1 → LÄUFT bis dahin), Backlog VPS-Software-Wartung (→8.1/5.21), 1.11-Abschluss nach 48h-Console-Check. **Bezugs-Integritäts-Register (`ABHAENGIGKEITEN.md`) angelegt** (Vortag-Auftrag), mit 8.1/8.2 verkabelt.
- **2026-07-16 (4)** — **Koordinations- & UX-Paket (Adam-Auftrag):** (a) CLAUDE.md: Kontext-Kompass (aus Neben-Sitzung reviewt+committet), „Frisch lesen"-Regel, **Führungs-Register**, Ampel-Datenschutz-Abstufung. (b) **Durchsetzungsschicht** `.claude/settings.json`: SessionStart-Banner+Warnung (hinter Master / dirty Master-Dateien), PreToolUse-**Schreibschutz** für MIGRATION.md/CLAUDE.md bei veraltetem Stand — Blocktest bestanden. (c) bot.py: Repo für Bot **NUR-LESEN** (Prompt + hartes Permission-Deny), Statusfragen immer frisch lesen. (d) **/ampel Button-Menü** mit cloud-freiem Regel-Dialog (60s-TTL); Lern-Schleife für Enforcement vorgemerkt; Mini-App → Backlog. Danach: **8.5 Pre-Send-Hook** (nächster Punkt).
- **2026-07-16 (3)** — **Phasen-Audit 2→3 bestanden.** Adam-Reihenfolge festgelegt: (1) **4.1 Backup** vorgezogen (nächster Schritt — Gedächtnis+Ampel-Regeln+Env nur auf VPS), (2) **8.5 Pre-Send-Hook**, (3) Phase 3 (LobeChat). 2.2 läuft bis ~16.08., 2.6-Rest → 5.14.
- **2026-07-16 (2)** — **2.7 SearxNG VERIFIZIERT (private kostenfreie Websuche):** SearxNG lokal (systemd), als `web_search`-Tool im Bot; Anthropic-WebSearch via `disallowed_tools` deaktiviert. E2E: Agent recherchiert lokal + antwortet mit Quelle, kein WebSearch. Board-Buttons auf gleichmäßig 3/Zeile. **Phase 2 damit weitgehend abgeschlossen** (2.2 Ampel-Beobachtung läuft weiter; 2.6 lange Summaries offen bis 5.14).
- **2026-07-16** — **Kostenregel verschärft + WebSearch-Kostenkontrolle + Antwortqualität (`2f37658`, Adam-Auftrag):** CLAUDE.md-💰-Regel jetzt UNIVERSELL (jede Kostenquelle, Cent zählt, „unklar=ja", gilt auch für Recherche-Tools; neue Dienste vorab auf versteckte Gebühren prüfen). WebSearch in Bot-Sessions kostenpflichtig-abgesichert (kein Always-Allow, Kostenhinweis). Antwortqualitäts-Leitplanke im System-Prompt + 🎯 Gründlich-Modus. Neu im Drehbuch: **2.7** SearxNG (kostenfreie private Suche), **8.5 hochgestuft**, Vermerke 5.6.
- **2026-07-15 (4)** — **Robustere Kontext-Behandlung + Ampel-Regelverwaltung (`e2ff813`, Adam-Spec):** (A1) Kontext-Überlauf → Session auto-verwerfen + Nachricht automatisch neu (Statuszeile, kein Verlust); (A3) Skill-Ladungen in Bot-Sessions abgelehnt (Kontextschutz); (B) `/ampel regeln|rot|gelb|weg` — Regelverwaltung rein lokal ohne Claude (Klienten-Namen nie in die Cloud), Log zeigt Label. Neu: **5.24** (proaktive Rotation ~80 %) ins Drehbuch; **4.1** um Backup der lokalen Nicht-Git-Dateien (env, Memory, Ampel-Regeln) ergänzt.
- **2026-07-15 (3)** — **Phase 2 gestartet:** 2.1 LiteLLM-Proxy ✅, 2.3 Ollama+Phi-4-Mini ✅ (LiteLLM-Route 1 s), 2.2 Datenschutz-Ampel als **Beobachtungsphase** live (regelbasiert, nur Log, kein Umrouten; Ende 4W4T4h/444 → dann Trimmen + Enforcement mit `!cloud`/`!lokal`-Overrides). Modell-Einstufung → Backlog.
- **2026-07-15 (2)** — **5.23 Session-Diät implementiert + E2E bewiesen:** Memory-Loader lädt nur Kern (Identität+Verhaltensregeln+Index), Projekt/Referenz on-demand (Agent liest via Read, Memory-Ordner via `add_dirs`, Lesen ohne Rückfrage). VPS-Messung: Kern-Frage 4,2 s, On-demand 7,3 s (Read genutzt, korrekt) — erste Session-Antwort ~60 s→~4 s. Adam-Telegram-Test offen.
- **2026-07-15** — **5.22 VERIFIZIERT (Adam: „funktioniert sehr gut"):** Threads-Fix (medium 47→25 s) + STT-Umschalter 🎙️ Genau/Flott live.
- **2026-07-14 (17)** — **Nach Livegang:** 48h-Kostenkontroll-Reminder als VPS-systemd-Timer→Telegram eingerichtet (Adam-Wunsch). STT-Analyse: VPS nutzt medium mit nur 2/4 Threads (Quick Win →4), keine GPU; Bot gab fälschlich Mac/Metal-Rat → Selbstverortung veraltet, in 5.22 vermerkt.
- **2026-07-14 (16)** — **1.12 Rollback-Trockenlauf bestanden → PHASE 1 funktional abgeschlossen.** Beide Richtungen bewiesen (→Mac ~1 Min, →VPS zurück), kein Doppel-Polling. Phasen-Audit 1→2 vorbehaltlich bestanden. Offen: 48h-Kostenkontrolle, 1.9 Webhooks (bewusst später). Bot läuft produktiv auf dem VPS.
- **2026-07-14 (15)** — **Kritischer Fund in 1.11 behoben:** Session-Start scheiterte am Linux-128-KiB-Arg-Limit (Memory 280 KB als `--append-system-prompt`). Fix `bc48004`: Kontext als `CLAUDE.md`-Datei + `setting_sources=["project"]` — verlustfrei, E2E auf VPS bewiesen. Rollback-Test wartet auf Adams Gegenprobe.
- **2026-07-14 (14)** — **1.11 Funktionstests bestanden + Memory-Lücke geschlossen:** Text/Voice/Tool-Buttons ✅ in Telegram. Bot-Selbstcheck fand fehlendes Memory → Bot-Gedächtnis (72 Dateien) Mac→VPS migriert, `CLAUDE_MEMORY_DIR` gesetzt, Selbstcheck jetzt sauber (schließt 0.4-Vormerkung). Offen: 48h-Kostenkontrolle. Nächstes: 1.12 Rollback-Trockenlauf.
- **2026-07-14 (13)** — **UMSCHALTUNG VOLLZOGEN (D.4):** Mac-Bot gestoppt + Plists gesichert (1.10 ✅), VPS-Dienst enabled+gestartet, Telegram verbunden ohne Konflikt, Auto-Restart-Test bestanden (1.8 ✅). Der Bot läuft jetzt produktiv auf dem VPS. Offen: 1.11 (Adam-Telegram-Tests + 48h-Kostenkontrolle), 1.12 (Rollback-Trockenlauf). 1.9 (Webhooks) bewusst später.
- **2026-07-14 (12)** — **1.8 systemd-Unit vorbereitet (LÄUFT):** Unit installiert + `systemd-analyze verify` OK; bewusst NICHT gestartet/enabled bis zum Umschalt-Moment (Schutz des laufenden Mac-Bots vor Telegram-409). Nächstes: Umschalt-Sequenz D.4 (Mac-Stopp → VPS-Start) — Adam-Timing.
- **2026-07-14 (11)** — **1.7 Bot-Code auf Server VERIFIZIERT:** privates Repo via Deploy-Key geklont (Server-HEAD = Mac-HEAD `60692c6`), venv mit Python 3.13 + alle Deps, SDK-Smoke-Test `query()` → `OK` (Python→SDK→Claude über Abo). Nächster Punkt: 1.8 systemd-Dienst.
- **2026-07-14 (10)** — **1.6 Headless-Auth VERIFIZIERT:** OAuth-Token (Abo, kein API-Key) in Server-Env, `claude -p "1+1="` → `2` ohne Browser. Token-Ausstelldatum-Sidecar für 5.20 angelegt. Zudem E5 + 5.20/5.21 (proaktive Wartung/Token-Erneuerung, register-basierter Update-Monitor) ins Drehbuch aufgenommen. Nächster Punkt: 1.7 Bot-Code auf Server.
- **2026-07-14 (9)** — **1.5 globales claude-CLI VERIFIZIERT:** v2.1.209; Node auf 22.23.1 LTS angehoben (CLI verlangt ≥22). CLI erreicht Auth-Check, wartet auf Token. Nächster Punkt: 1.6 Headless-Auth (CLAUDE_CODE_OAUTH_TOKEN).
- **2026-07-14 (8)** — **1.4 Whisper medium VERIFIZIERT + F2 entschieden (medium):** medium klar genauer bei Deutsch, Laufzeit ~45–48 s/30-Sek-Probe (unter 60-Sek-Schwelle). Offen bis 1.6: `WHISPER_MODEL_PATH` in Server-Env auf medium setzen. Nächster Punkt: 1.5 globales claude-CLI.
- **2026-07-14 (7)** — **1.3 Python/ffmpeg/whisper.cpp VERIFIZIERT:** Python 3.13.5 (Adam-Entscheid statt 3.12, siehe 1.3), ffmpeg 7.1.5, whisper.cpp gebaut; gemischt de/en-Transkription wortgenau. `small`-Modell liegt am Modellpfad. Nächster Punkt: 1.4 Modell-Upgrade small → medium.
- **2026-07-14 (6)** — **1.2 User `claudebot` VERIFIZIERT:** unprivilegiert (kein sudo), eigenes Home, Key-Login. Nächster Punkt: 1.3 Python 3.12 / ffmpeg / whisper.cpp (Build).
- **2026-07-14 (5)** — **1.1 System härten VERIFIZIERT:** full-upgrade sauber, `ufw` active (nur 22/tcp), `fail2ban` aktiv (bannte live einen Brute-Force-Bot), `unattended-upgrades` mit Security-Origins scharf. Nächster Punkt: 1.2 User `claudebot`.
- **2026-07-14 (4)** — **1.0 VERIFIZIERT → Phase 1 gestartet.** VPS war nicht frisch (33d Uptime, Root-PW unbekannt) → sauberer Reinstall Debian 13.6 UEFI Minimal mit SSH-Key + deaktivierter Passwort-Auth. Key-Login verifiziert, Fingerprints gegen Netcup-Panel abgeglichen, Alias `claudevps` in `~/.ssh/config`. Nächster Punkt: 1.1 System härten.
- **2026-07-14 (3)** — **0.7 VERIFIZIERT (am Produktivbetrieb, Adam-Entscheid) → Phase 0 KOMPLETT; Phasen-Audit 0→1 bestanden.** Live-Tests durch Adam alle grün; Modell zurück auf Sonnet; Backlog-Fund: unbekannte Kommandos stumm ignoriert. Nächster Punkt: 1.0 Server-Zugang.
- **2026-07-14 (2)** — **0.1–0.6 VERIFIZIERT** (Akzeptanzkriterien einzeln geprüft: Zeilenzahl/Hash, Audit-Greps, py_compile, env-Pfade/Modell; Belege je Punkt). **0.7 auf LÄUFT:** Adam-Entscheid — Verifikation am Produktivbetrieb statt erneutem Stopp; Wächter-Kriterium (launchd+Guardian geladen, pgrep = 1 Instanz) bereits erfüllt, Live-Tests durch Adam offen.
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
| E5 | Wartung & Erneuerung proaktiv automatisieren | ✅ **Entschieden (Adam, 2026-07-14):** Das Gesamtsystem muss sich selbst überwachen und Adam frühzeitig warnen — nicht erst reagieren, wenn etwas ausgefallen ist. (a) **Token-Erneuerungs-Frühwarner** → Punkt **5.20**: OAuth-Token (~1 Jahr gültig) proaktiv überwachen, Erinnerung ab ~10 Monaten, **mind. 1 Monat Vorlauf**. (b) **Versions-/Update-Monitor** → Punkt **5.21**: regelmäßiger Check auf neue Versionen — **register-basiert, nicht als feste Liste**: erfasst ALLE aktuell UND künftig installierten versionierten Komponenten; **jede neue versionierte Komponente MUSS beim Einbau ins Monitor-Register eingetragen werden (fester Teil der „fertig"-Definition jedes künftigen Punkts)**. Telegram-Hinweis, **größere Versionssprünge hervorgehoben**. Beide Wächter laufen **bot-unabhängig** (eigener systemd-Timer + direkter Telegram-Ping via Bot-API), damit ein liegender Bot die Warnung nicht mitreißt. Token-Erneuerung selbst bleibt manuell (Browser-OAuth), die Warnung davor ist automatisch und früh. |

---

## Phase 0 — Code- & Repo-Vorbereitung (am Mac) `[NEU 2026-07-12]`

> Grund: Das GitHub-Repo enthält eine **veraltete** `bot.py` (~460 Zeilen). Die echte, produktive Version auf dem Mac hat **~2000+ Zeilen** (Watchdog, Heartbeat, TTS-Pfade, PDF/Foto/Link-Handling, Conversation-Logs …). Ohne Phase 0 klont Phase 1.7 den falschen Stand auf den Server. Referenz-Implementierungen (401-Handling, Abo-Token-Doku) liegen auf Branch `claude/telegram-bot-auth-401-g6yqrr`.

### 0.1 Echte bot.py + Zubehör ins Repo (KRITISCH)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Branch `mac-produktivstand` auf GitHub enthält die produktive `bot.py` (Plausibilität: `wc -l bot.py` > 1500), `transcribe.py`, `guardian.sh`, `requirements.txt`, `run.sh`; Commit-Hash Mac = GitHub.
- **Test:** `git log -1` lokal vs. GitHub; Zeilenzahl-Check. Befehle: Anhang D.0.
- **Adam-Bestätigung:** ✅ 14.07.2026 (Arbeit war seit 13.07. real erledigt, Status-Pflege nachgeholt)
- **Verifiziert am:** 14.07.2026 — Beleg: `wc -l bot.py` = 3890; alle 5 Dateien vorhanden; Hash lokal = GitHub (`18899cc`).

### 0.2 Ist-Audit der echten bot.py
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Liste aller Mac-/Hardcoded-Pfade und Auth-Stellen liegt vor (`grep` nach `Users/jakuna`, `Mobile Documents`, `/opt/homebrew`, `ANTHROPIC_API_KEY`, `system_prompt`, Modell-Strings). Bekannt: Conversation-Log geht nach iCloud (`~/Library/Mobile Documents/…/Claude-Logs/`) — existiert auf Linux nicht.
- **Test:** Grep-Läufe (Anhang D.0) dokumentiert.
- **Adam-Bestätigung:** ✅ 14.07.2026
- **Verifiziert am:** 14.07.2026 — Beleg: Grep-Läufe sauber; verbleibende Treffer sind nur Kommentare (Z. 172/401) + optionale Neben-Inferenz `_ai_topic_label` (Z. 3476, nutzt `ANTHROPIC_API_KEY` NUR falls gesetzt; in `.env` NICHT gesetzt → fällt still auf "" zurück, keine Kosten). Hinweis für 2.6: diese Neben-Inferenz später auf LiteLLM umziehen.

### 0.3 401-/Fehler-Handling in echte bot.py portieren
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `is_auth_error()` + `AUTH_HELP` (Abo-Token-first!) + automatischer Session-Verwurf bei Auth-Fehlern in der echten bot.py; rohe SDK-Fehler erreichen Adam nicht mehr unkommentiert.
- **Test:** `py_compile` grün; simulierter 401 (Token kurz invalidieren) zeigt die freundliche Meldung.
- **Adam-Bestätigung:** ✅ 14.07.2026
- **Verifiziert am:** 14.07.2026 — Beleg: `is_auth_error()` (Z. 242), `AUTH_HELP` (Z. 258), Auth-Fehler → `AUTH_HELP` senden + `close_session()` (Z. 626–632); auch generische Fehler kommen kommentiert an („Session-Fehler … frische Session"); `py_compile` grün. (401-Simulation nicht wiederholt — Handling war auf dem Auth-Branch entwickelt/getestet.)

### 0.4 Neutrale Begrüßung (keine Kontext-Annahmen)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** System-Prompt-Zusatz via `{"type": "preset", "preset": "claude_code", "append": "…"}`: Bot nimmt nicht an, wo/an welchem Gerät Adam sitzt (kein „schön, dich am Desktop zu sehen").
- **Test:** Frische Session, Begrüßung prüfen.
- **Adam-Bestätigung:** ✅ 14.07.2026
- **Verifiziert am:** 14.07.2026 — Beleg: preset+append-Struktur in `ensure_session()` (Z. 979–983); Neutralitäts-Regel wird über den Memory-Loader eingespeist (`user-interfaces.md`, im MEMORY.md-Index, Auslöser-Vorfall 26.06. behoben). **Abweichung vom Wortlaut:** Regel liegt im Memory, nicht hart im Code. ⚠️ **VPS-Hinweis für 1.7:** `CLAUDE_MEMORY_DIR` muss auf dem Server gesetzt sein und das Memory mitwandern, sonst lädt die Regel dort nicht.

### 0.5 Mac-Pfade konfigurierbar machen (v. a. iCloud-Log)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Conversation-Log-Verzeichnis via env `CONVERSATION_LOG_DIR` (Mac darf weiter iCloud nutzen, Server nutzt lokalen Pfad); keine `/Users/…`- oder `/opt/homebrew`-Pfade mehr hart im Code; benötigte Verzeichnisse werden beim Start angelegt.
- **Test:** Audit-Liste aus 0.2 vollständig abgearbeitet; Bot startet mit gesetztem Alternativ-Pfad.
- **Adam-Bestätigung:** ✅ 14.07.2026
- **Verifiziert am:** 14.07.2026 — Beleg: `CONVERSATION_LOG_DIR` mit VPS-tauglichem Fallback `~/claude-logs` (Z. 172–173); keine harten `/Users/…`-/`/opt/homebrew`-Pfade mehr (Grep 0.2); `mkdir(parents=True, exist_ok=True)` an allen Schreibpfaden (Z. 72/96/405/455/1740/1804).

### 0.6 Modell per .env (Sonnet-Default, E3)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `CLAUDE_MODEL` (Default `sonnet`) wird gelesen und in `ClaudeAgentOptions(model=…)` gesetzt; `.env.example` dokumentiert.
- **Test:** Mit und ohne env-Variable starten, aktives Modell im Log/`/status` prüfen.
- **Adam-Bestätigung:** ✅ 14.07.2026
- **Verifiziert am:** 14.07.2026 — Beleg: `DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")` (Z. 181), fließt via `_MODEL_ALIASES` in `ClaudeAgentOptions(model=…)` (Z. 977); `.env.example` Z. 24 dokumentiert; Produktivbetrieb läuft damit.

### 0.7 Mac-Backtest des vorbereiteten Stands
- **Status:** VERIFIZIERT — **am Produktivbetrieb verifiziert, Adam-Entscheid** `[2026-07-14]`: KEIN erneutes Stoppen des Bots — der vorbereitete Branch läuft seit 13.07. produktiv unter launchd; Verifikation erfolgte AM Produktivbetrieb (der Vorfall vom 12.07. entstand gerade durch den unterbrochenen manuellen Backtest).
- **Akzeptanzkriterium:** Bot läuft vom vorbereiteten Branch einmal manuell am Mac (launchd/Guardian währenddessen gestoppt!): Text, `/status`, `/reset`, Voice, Permission-Buttons — alles wie gewohnt. Danach Mac zurück auf Produktivstand bis zum Umschalten. **Der Punkt ist erst grün, wenn launchd + Guardian wieder GELADEN sind und `pgrep -fl bot.py` genau eine laufende Instanz zeigt** — ein gestoppter Wächter darf NIE über das Test-Fenster hinaus bestehen bleiben (Vorfall 2026-07-12: Bot blieb nach unterbrochenem Backtest down, weil der Guardian planmäßig aus war und niemand neu lud).
- **Test:** Die fünf genannten Interaktionen einzeln in Telegram.
- **Adam-Bestätigung:** ✅ 14.07.2026 — Live-Tests selbst durchgeführt, Ergebnisse an führende Sitzung gemeldet.
- **Verifiziert am:** 14.07.2026 — Belege: Wächter-Kriterium (launchd-Bot PID-Check, Guardian geladen, `pgrep -fl bot.py` = genau 1 Instanz) ✅; `/status` ✅; Text ✅; Voice/Transkription ✅; Neutralität bestätigt (Voice ohne Geräte-Nennung → Antwort ohne Kontext-Annahme; 0.4 hält) ✅; Permission-Buttons mit schreibender Aktion (ping.txt anlegen → Allow → Datei da) ✅; Modell auf Sonnet zurückgestellt (via Inline-Buttons; Erst-Test mit Read-only-Aufgabe zeigte erwartungsgemäß keine Buttons — SDK fragt im default-Modus bei Lese-Tools nicht). Erkenntnis → Backlog: kein `/model`-Textbefehl vorhanden, unbekannte Kommandos werden stumm ignoriert.

### 0.8 (Adam-Task) Master-Drehbuch der führenden Migrations-Sitzung übergeben
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Die **führende Migrations-Sitzung** (die Code-Sitzung am Mac, die Phase 0 ausführt) arbeitet nachweislich mit dieser Repo-Fassung (`git fetch` + aktuelle MIGRATION.md im Arbeitsordner) und betreibt die Status-Pflege hier. Falls die Telegram-Sitzung ein eigenes Drehbuch-Memory hält: durch Verweis auf die Repo-Fassung ersetzen (Zuständigkeiten: siehe CLAUDE.md → Anti-Ping-Pong-Regel).
- **Test:** Führende Sitzung nach Phase/Punkt fragen — Antwort deckt sich mit diesem Dokument (inkl. nachgeschärftem 0.7 und Alt-Log-Übernahme in 4.2).
- **Adam-Bestätigung:** ✅ 13.07.2026 — „Das aktuelle Drehbuch liegt als MIGRATION.md im Projektordner — bitte damit arbeiten und dort auch die Status pflegen."
- **Verifiziert am:** 13.07.2026 17:26 Uhr

### Phasen-Audit 0 → 1
- **Audit-Status:** ✅ 14.07.2026 — Alle Punkte 0.1–0.8 VERIFIZIERT (0.1–0.6 mit Einzelbelegen nachgezogen, 0.7 am Produktivbetrieb per Adam-Entscheid, 0.8 seit 13.07.). Ein Fund in den Backlog übertragen (unbekannte Kommandos stumm). Keine offenen Reste in Phase 0.
- **Strategie-Recheck:** ✅ 14.07.2026 — Reihenfolge Phase 1 bleibt sinnvoll (1.0 Zugang → Härten → Runtime → Auth → Code → Dienst → Umschalten → Rollback). Zwei Mitnahmen für Phase 1: (a) aus 0.4: `CLAUDE_MEMORY_DIR` + Memory-Bestand müssen auf den VPS mitwandern (betrifft 1.7, ggf. auch 4.3); (b) aus 0.2: Neben-Inferenz `_ai_topic_label` nutzt direkt die Anthropic-API falls Key gesetzt — auf dem VPS keinen `ANTHROPIC_API_KEY` setzen (Kostenregel), Umzug auf LiteLLM in 2.6. Eintrag ins Strategie-Audit-Log unten.

---

## Phase 1 — Server-Grundgerüst

### 1.0 Server-Zugang übermitteln & verifizieren `[NEU 2026-07-12]`
- **Status:** VERIFIZIERT
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
- **Adam-Bestätigung:** ✅ 14.07.2026 — VPS neu aufgesetzt (siehe unten), Root-Passwort im Passwort-Manager gesichert.
- **Verifiziert am:** 14.07.2026 — Belege: Key-Login ohne Passwort läuft (`ssh … "hostname && uname -a"` → `v2202606366899469275` / `Linux 6.12.95+deb13-amd64 … Debian … x86_64`); Host-Key-Fingerprints (RSA `…OJxU5Xzw8`, ECDSA `…AKjI8+BK/c`) = Netcup-Installationsergebnis (MITM ausgeschlossen); Zugang als SSH-Alias `claudevps` in `~/.ssh/config` + Passwort-Manager (nicht im Repo-Klartext); SCP-Panel + VNC-Konsole („Bildschirm") als Notzugang bekannt.
- **Ausgangslage-Hinweis `[NEU 2026-07-14]`:** Der VPS war NICHT frisch (33 Tage Uptime, unbekanntes Root-Passwort — SCP-Resets griffen nicht). Lösung: sauberer **Reinstall Debian 13.6 UEFI (Minimal)** über SCP → Medien → Images, mit vorab hinterlegtem SSH-Key (`mac-adam` im SCP) und **deaktivierter SSH-Passwort-Authentifizierung** (Härtung 1.1 damit vorweggenommen). Sprache `en_US.UTF-8` (bessere Log-Diagnose), Zeitzone Europe/Berlin. Kein Zusatz-User (kommt in 1.2 als `claudebot`).

### 1.1 System härten (Updates, ufw, fail2ban, unattended-upgrades)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `apt-get upgrade` ohne offene Pakete; `ufw status` = active mit nur den freigegebenen Ports; `fail2ban-client status` läuft; `unattended-upgrades --dry-run` zeigt aktive Konfiguration.
- **Test:** SSH auf VPS, vier Kommandos ausführen, jeweils erwartete Ausgabe sichten.
- **Adam-Bestätigung:** ✅ 14.07.2026 (Freigabe „Ja bitte", von führender Sitzung ausgeführt)
- **Verifiziert am:** 14.07.2026 — Belege: `full-upgrade` = 0 ausstehende Pakete; `ufw` active, nur `22/tcp` (SSH) offen (IPv4+IPv6), Default deny incoming; `fail2ban` active, sshd-Jail (systemd/journald-Backend) mit bantime 1h/maxretry 5 — bannte live bereits Angreifer-IP `91.92.40.36`; `unattended-upgrades` enabled, Periodic 1/1, Origins Debian + Debian-Security, Dry-run bestätigt aktive Config; apt-daily/-upgrade-Timer active. **Hinweis:** SSH-Passwort-Auth war bereits beim Reinstall (1.0) deaktiviert.

### 1.2 Unprivilegierter User claudebot
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `id claudebot` existiert, eigenes Home, **kein** sudo-Recht.
- **Test:** `id claudebot` + `sudo -u claudebot sudo -l` muss fehlschlagen.
- **Adam-Bestätigung:** ✅ 14.07.2026 (von führender Sitzung ausgeführt)
- **Verifiziert am:** 14.07.2026 — Belege: `id claudebot` = uid 1000, groups `claudebot,users` (kein sudo); Home `/home/claudebot`; `sudo -u claudebot sudo -n -l` scheitert („a password is required"). Login-Only-per-Key (kein Passwort gesetzt); SSH-Key hinterlegt, direkter Login als `claudebot` verifiziert (Alias `claudebot` in `~/.ssh/config`).

### 1.3 Python 3.13, ffmpeg, whisper.cpp
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `python3 --version` = 3.13.x `[GEÄNDERT 2026-07-14: war 3.12 — Debian 13 liefert 3.13, 3.12 nicht mehr in den Repos; Bot pinnt keine feste Version. Adam-Entscheid: 3.13 nehmen]`; `ffmpeg -version` läuft; `whisper-cli` (bzw. `main`) Binary vorhanden und ausführbar als claudebot.
- **Test:** Drei Kommandos, plus kurze Beispiel-Audio (deutsch+englisch gemischt) durch whisper jagen. Build-Befehle: Anhang D.1.
- **Adam-Bestätigung:** ✅ 14.07.2026 (Python-3.13-Entscheid + Freigabe, von führender Sitzung ausgeführt)
- **Verifiziert am:** 14.07.2026 — Belege: `python3` = 3.13.5; `ffmpeg` = 7.1.5; whisper.cpp als `claudebot` gebaut (`/home/claudebot/whisper.cpp/build/bin/whisper-cli`, global verlinkt `/usr/local/bin/whisper-cli`); Transkription einer gemischt de/en-Sprachprobe (small-Modell, `-l auto`) **wortgenau inkl. Umlaute**. Hinweis: `small`-Modell liegt bereits unter `/home/claudebot/claude-telegram-bot/models/ggml-small.bin` (Basis für 1.4-Upgrade).

### 1.4 Whisper-Modell-Upgrade small → medium
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `ggml-medium.bin` (~1,5 GB) am Modellpfad; Bot-Konfig nutzt es; vergleichende Transkription deutlich präziser als mit small. `[NEU 2026-07-12]` Zusätzlich: Laufzeit pro 30-Sek.-Probe auf VPS-CPU messen und festhalten; wird sie praxisuntauglich (> ~60 s), Entscheidung small vs. medium mit Adam (F2).
- **Test:** Eine deutsche und eine englische Sprachprobe (~30 Sek.) transkribieren, Output gegen small-Lauf vergleichen + Laufzeit notieren.
- **Adam-Bestätigung:** ✅ 14.07.2026 — **F2 entschieden: medium.** (Deutsch ist Hauptsprache; ~15–30 s Wartezeit bei kurzen Nachrichten akzeptabel.)
- **Verifiziert am:** 14.07.2026 — Belege: `ggml-medium.bin` (1,5 GB) unter `/home/claudebot/claude-telegram-bot/models/`; Vergleich small vs. medium auf VPS-CPU (`-t 4`): **Laufzeit** medium 48 s (de, 34 s Probe) / 45 s (en, 31 s Probe) — **unter der 60-Sek-Schwelle**, small 17 s / 13 s; **Genauigkeit** medium klar besser bei Deutsch (Umlaute ä/ö/ü korrekt, alle Sätze vollständig; small verwechselt ä→„er" und verschluckt Wörter im letzten Satz).
- **⚠️ Konfig-Anbindung → offen bis 1.6:** Der Bot liest den Modellpfad aus `WHISPER_MODEL_PATH` (transcribe.py; Default sonst `models/ggml-small.bin`). In die Server-Env (`/etc/claude-telegram-bot.env`, Punkt 1.6) muss: `WHISPER_MODEL_PATH=/home/claudebot/claude-telegram-bot/models/ggml-medium.bin`. Endgültiger End-to-End-Nachweis („Bot nutzt medium") beim Bot-Smoke-Test.

### 1.5 Globales claude-CLI
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `claude --version` auf VPS läuft, aktuelle Version. `[NEU 2026-07-12]` Hinweis: Das Agent-SDK bringt eine gebündelte CLI mit — das globale CLI dient v. a. Setup/Debugging (`claude -p "hallo"`-Gegentest).
- **Test:** Kommando ausführen + Mini-Anfrage gegen Test-Endpunkt.
- **Adam-Bestätigung:** ✅ 14.07.2026 (Freigabe „Ja bitte", von führender Sitzung ausgeführt)
- **Verifiziert am:** 14.07.2026 — Belege: `claude --version` = 2.1.209 (Claude Code), Binary `/usr/local/bin/claude`, auch als `claudebot` aufrufbar. `claude -p "1+1="` erreicht sauber den Auth-Check („Not logged in · Please run /login") → CLI korrekt verdrahtet, Mini-Inferenz folgt in 1.6 nach Token. **Node-Upgrade `[NEU 2026-07-14]`:** CLI verlangt Node ≥22, Debian 13 liefert nur Node 20 → auf **Node 22.23.1 LTS** (NodeSource) angehoben, npm 10.9.8; Engine-Anforderung jetzt erfüllt.

### 1.6 Headless-Auth (CLAUDE_CODE_OAUTH_TOKEN per setup-token)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Token gesetzt; `claude` antwortet auf Test-Inferenz ohne Browser-Flow. `[NEU 2026-07-12]` Eigener Token für den Server (getrennt vom Mac-Token, unabhängig widerrufbar); Ablage in `/etc/claude-telegram-bot.env` (root, `600`); 💰 NIEMALS `ANTHROPIC_API_KEY` als Ausweichlösung.
- **Test:** Mini-Inferenz "1+1=" → erwartet "2". SDK-Smoke-Test: Anhang D.2.
- **Adam-Bestätigung:** ✅ 14.07.2026 — Token via `claude setup-token` am Mac erzeugt, sicher (verschlüsselt, ohne Chat-Kontakt) in die Server-Env übertragen.
- **Verifiziert am:** 14.07.2026 — Belege: `claude -p "1+1="` als `claudebot` mit Token aus Env → **`2`**, ohne Browser, über Abo. Env-Datei `/etc/claude-telegram-bot.env` root:root `600`, **kein `ANTHROPIC_API_KEY`** (weder in Datei noch Shell). Token-Ausstelldatum in Sidecar `/etc/claude-telegram-bot.token-issued` (14.07.2026, Ablauf ~14.07.2027 → speist 5.20-Frühwarner). **Stolperfalle dokumentiert:** Erst-Übertragung ergab 401 — Token war beim Kopieren an der 80-Spalten-Terminalbreite abgeschnitten (79 statt 108 Zeichen); Fenster breit ziehen / vollständig markieren löst es.
- **SDK-Smoke-Test (Anhang D.2):** ✅ in 1.7 nachgeholt (nach venv-Aufbau) — `claude_agent_sdk.query()` → `OK`.

### 1.7 Bot-Code auf Server (privates git-Repo)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Privates Repo auf VPS geklont; letzter Commit-Hash identisch mit Mac. `[NEU 2026-07-12]` Voraussetzung: Phase 0 abgeschlossen — sonst landet die veraltete bot.py auf dem Server!
- **Test:** `git log -1` auf beiden Seiten — gleicher Hash.
- **Adam-Bestätigung:** ✅ 14.07.2026 — Read-only Deploy-Key bei GitHub hinterlegt.
- **Verifiziert am:** 14.07.2026 — Belege: Klon nach `/home/claudebot/claude-telegram-bot` (Branch `mac-produktivstand`), Server-HEAD = Mac-HEAD `60692c6`. Zugang über read-only GitHub-**Deploy-Key** (`~/.ssh/github_deploy`, SSH-Config-Eintrag) → Server kann künftig selbst `git pull`. `models/` + `logs/` bleiben (gitignored) erhalten. **venv** unter `.venv` mit Python 3.13.5; alle `requirements.txt`-Pakete installiert, Kern-Importe (`claude_agent_sdk`, `telegram`, `anyio`) OK → 3.13-Kompatibilität bestätigt. **SDK-Smoke-Test (Anhang D.2, war offen aus 1.6) nachgeholt:** `claude_agent_sdk.query()` als `claudebot` mit Token aus Env → Antwort **`OK`** (voller Python→SDK→Claude-Pfad über Abo).

### 1.8 systemd-Dienst statt launchd
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `systemctl status claude-telegram-bot` = active (running); Auto-Restart nach Kill greift. (Guardian wird auf dem Server NICHT nachgebaut — `Restart=always` + bot-interner Watchdog decken das ab.)
- **Test:** Dienst killen → spätestens nach 30 Sek. wieder active. Unit-Vorlage: Anhang D.3.
- **Zwischenstand `[2026-07-14]`:** `/etc/systemd/system/claude-telegram-bot.service` geschrieben (exakt D.3), `daemon-reload` + `systemd-analyze verify` = **Syntax OK**. Bewusst **nicht gestartet und nicht `enable`d** — ein Start würde Polling beginnen und mit dem noch laufenden Mac-Bot kollidieren (Telegram 409). `enable` + `start` + Kill/Restart-Test erfolgen zusammen im **Umschalt-Moment (D.4 / Punkt 1.10)**. (Kleine, sicherheitsmotivierte Abweichung von D.3: auch `enable` erst beim Umschalten, damit ein ungeplanter VPS-Reboot vorher keinen Zweit-Poller startet.)
- **Adam-Bestätigung:** ✅ 14.07.2026 — „los" für den Umschalt-Moment.
- **Verifiziert am:** 14.07.2026 — Belege: `systemctl enable --now` → **active (running)**, PID 22610, `Started claude-telegram-bot.service`; Bot verbindet Telegram (`@jakuna_cc_bot` gecached), `Application started`, kein 401/Conflict. **Auto-Restart-Test:** `kill -9` MainPID → nach ~5 s automatisch neue PID 22681, `is-active=active`, `NRestarts=1`, Telegram wieder verbunden. (Logs unter `logs/bot.{out,err}.log` per Unit-Umleitung.)

### 1.9 Polling → Webhooks (HTTPS via Caddy oder nginx)
- **Status:** OFFEN
- **Akzeptanzkriterium:** Telegram `getWebhookInfo` zeigt VPS-URL, letzter Fehler leer; Test-Nachricht trifft Bot in unter zwei Sekunden. `[NEU 2026-07-12]` Reihenfolge zwingend nach Anhang D.4: Der Umschalt-Arbeitsgang läuft zuerst über Mac-Stopp (1.10) + VPS-Start im Polling-Modus; die Webhook-Umstellung folgt als eigener Schritt erst nach stabilem Betrieb (erfordert Code-Anpassung run_polling → Webhook-Modus + Domain/TLS). Achtung bei Abweichung: Ein gesetzter Webhook deaktiviert getUpdates sofort — nie setzen, solange der Mac-Bot noch pollt.
- **Test:** Eine Telegram-Nachricht senden, Logs prüfen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 1.10 Mac-Bot abschalten
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** `launchctl list | grep telegram-bot` leer; Guardian-Plist ebenfalls deaktiviert; Telegram-Nachricht trifft NUR VPS-Bot (kein Token-Konflikt). `[NEU 2026-07-12]` Reihenfolge am Mac: Guardian zuerst entladen (sonst startet er den Bot neu), dann Bot-Plist, dann `pkill -f bot.py`, dann `pgrep -fl bot.py` = leer. Plists in `~/Library/LaunchAgents/_deaktiviert/` verschieben, nicht löschen (Rollback!).
- **Test:** Drei Kommandos + eine Test-Nachricht; Logs auf Mac bleiben still.
- **Adam-Bestätigung:** ✅ 14.07.2026 — Einverständnis, Mac-Stopp durch führende Sitzung ausgeführt.
- **Verifiziert am:** 14.07.2026 — Belege: Reihenfolge eingehalten (Guardian zuerst entladen, dann Bot-Plist, dann `pkill -f bot.py`); `pgrep -f bot.py` = **0**, Bot-Agents vollständig ausgebootet (verbleibender launchctl-Treffer war die Telegram-**Desktop-App**, nicht der Bot). Plists nach `~/Library/LaunchAgents/_deaktiviert/` verschoben (nicht gelöscht → Rollback). Kein Token-Konflikt: VPS-Bot pollt ohne 409. ⚠️ Guardian-Plist am Mac ist mitdeaktiviert — beim etwaigen Rollback (1.12) beide Plists zurückladen.

### 1.11 Abschlusstest Phase 1
- **Status:** ✅ **VERIFIZIERT — 19.07.2026 (Adam bestätigt: „1.11 bestätigt, Phase 1 endgültig schließen")**. 3 Funktionstests ✅ + 48-h-Kostenkontrolle bestanden (kein Usage-Wachstum in der Console → **Beweis: Abo-Token, nicht API** 💰). **Damit ist Phase 1 abgeschlossen**; einziger bewusst zurückgestellter Phase-1-Punkt bleibt **1.9 (Webhooks)** — Polling läuft stabil, kein Handlungsdruck.
- **Akzeptanzkriterium:** Telegram-Text → Antwort; Voice → Transkription; ein Tool-Use-Schritt mit Permission-Buttons funktioniert. `[NEU 2026-07-12]` Plus 48-h-Kostenkontrolle: console.anthropic.com → Usage darf nicht steigen (Beweis: Abo, nicht API).
- **Test:** Drei konkrete Eingaben aus Telegram, jede einzeln beobachtet.
- **Adam-Bestätigung:** ✅ 14.07.2026 — Tests selbst durchgeführt (Telegram).
- **Verifiziert am (Funktion):** 14.07.2026 — Belege: **Text** → Antwort ✅; **Voice** → korrekt transkribiert („…ob Sprachnachrichten funktionieren") + Antwort ✅ (medium-Modell auf VPS); **Tool+Buttons** → `test.txt` per Allow angelegt, per Allow (Bash `rm`) gelöscht ✅.
- **⚠️ Beim Test gefunden & geschlossen — Memory-Migration:** Bot-Selbstcheck meldete „MEMORY.md fehlt" (das in 0.4 vorgemerkte `CLAUDE_MEMORY_DIR`/Memory-Umzug war offen). Behoben: Bot-Gedächtnis (72 Dateien inkl. MEMORY.md + Neutralitäts-Regel `user-interfaces.md`) per `tar`-über-SSH Mac→VPS nach `/home/claudebot/.claude/memory`, `CLAUDE_MEMORY_DIR` in Server-Env gesetzt, Neustart → Selbstcheck sauber. **Memory ist ab jetzt VPS-autoritativ** (der VPS-Bot pflegt es dort weiter). `[erledigt 2026-07-14]`
- **⚠️ Beim Test gefunden & geschlossen (2) — Session-Start scheiterte an Linux-Arg-Limit:** Adams Gedächtnis-Testfrage (19:42) blieb unbeantwortet; Log: `CLIConnectionError … [Errno 7] Argument list too long`. Ursache: Bot übergab Memory+Recall (280 KB nach Memory-Migration) als EIN `--append-system-prompt`-Argument — Linux begrenzt einzelne exec-Argumente auf 128 KiB (`MAX_ARG_STRLEN`); macOS kennt das Limit nicht, daher am Mac nie aufgefallen. **Fix (Commit `bc48004`):** Kontext wird als `CLAUDE.md` ins WORKDIR geschrieben und via `setting_sources=["project"]` geladen (kein Limit, **kein Informationsverlust**); Fallback argv-Pfad mit 100-KB-Budget. E2E-Beweis auf VPS: Session mit vollem 280-KB-Kontext gestartet, Gedächtnis-Frage korrekt beantwortet („Adam …, primärer Kanal Telegram-Bot"). `[erledigt 2026-07-14]`
- **➡️ Abschluss-Vermerk (Adam 17.07.):** Adam prüft die Console in **48 h**; zeigt Usage **0-Wachstum**, wird **Phase 1 endgültig abgeschlossen** (1.11 → VERIFIZIERT). Einziger dann noch offener Phase-1-Punkt bleibt **1.9 (Webhooks)** — bewusst zurückgestellt, Polling läuft stabil.
- **Offen:** 48-h-Kostenkontrolle (Adam beobachtet console.anthropic.com/Usage → darf nicht steigen). `[NEU 2026-07-14]` **Automatischer Reminder eingerichtet:** systemd-Timer `kostenkontrolle-reminder` auf dem VPS schickt Adam alle 8 h eine Telegram-Erinnerung (bot-unabhängig, curl→Bot-API), self-disabling nach Deadline **16.07. 23:06**. (Kleiner Vorläufer des E5/5.20-Musters.)

### 1.12 Rollback-Pfad verifiziert `[NEU 2026-07-12]`
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Dokumentierter Rollback (Anhang D.5): VPS-Dienst stoppen, Telegram-Webhook löschen (`deleteWebhook`), Mac-Plists wieder laden → Mac-Bot antwortet binnen 2 Minuten. Einmal trocken durchgespielt, BEVOR Phase 2 beginnt.
- **Test:** Rollback ausführen, Mac-Bot antwortet; danach wieder auf VPS umschalten.
- **Adam-Bestätigung:** ✅ 14.07.2026 — „Leg los" für den Trockenlauf.
- **Verifiziert am:** 14.07.2026 — Trockenlauf durchgespielt. **Phase A (→ Mac):** VPS `systemctl stop` → Mac-Plists aus `_deaktiviert/` zurück + geladen (Bot, dann Guardian) → Mac-Bot in ~1 Min aktiv, Telegram verbunden (`@jakuna_cc_bot`, `Application started`), stabil (python3.12). **Phase B (→ VPS, Normalzustand):** Mac gestoppt (Guardian zuerst), Plists zurück nach `_deaktiviert/`, VPS `systemctl start` → active PID 26144, Telegram verbunden. `deleteWebhook` nicht nötig (Polling-Modus). Kein Doppel-Polling zu keinem Zeitpunkt (strikte Stop-vor-Start-Reihenfolge).

### Phasen-Audit 1 → 2
- **Audit-Status:** ✅ 14.07.2026 (vorbehaltlich) — Phase 1 funktional vollständig: 1.0–1.8, 1.10, 1.12 VERIFIZIERT; 1.11 Funktionsteil ✅. **Bot läuft produktiv auf dem VPS** (Text/Voice/Tool-Buttons, Memory, Auto-Restart, Rollback getestet). **Offen vor endgültigem Abschluss:** (a) 1.11 **48-h-Kostenkontrolle** (console.anthropic.com/Usage darf nicht steigen — Abo-Beweis); (b) **1.9 Webhooks** bewusst zurückgestellt (läuft vorerst im Polling-Modus — funktioniert, aber Punkt bleibt offen). Zwei Live-Funde sauber behoben: Memory-Migration (`CLAUDE_MEMORY_DIR`) und Linux-Arg-Limit (`bc48004`).
- **Strategie-Recheck:** ✅ 14.07.2026 — Phase-2-Reihenfolge bleibt sinnvoll. **Vorgezogene Priorität aus Praxis:** Transkriptions-Tempo (5.22) und Session-Start-Diät (5.23) sind für den Alltag spürbar wichtiger als ihre Nummer suggeriert — beim Phasen-Audit vor Phase 5 (bzw. schon früher, falls Adam wünscht) hochziehen. Reihenfolge sonst unverändert; keine Streichungen.

---

## Phase 2 — KI-Orchestrierung & Datenschutz

> **💰 Architektur-Leitplanke (F1, von Adam entschieden 2026-07-12):** Der Claude-**Agent** (Tools, Permission-Buttons) läuft über das Abo-SDK und wird NICHT durch LiteLLM ersetzt; LiteLLM orchestriert ausschließlich **Neben-Inferenzen** (Ampel, Zusammenfassungen, Link-Inbox) über Ollama/Groq. Rote Anfragen werden vor dem Claude-Agenten abgefangen. Keine Anthropic-Route in LiteLLM, kein `ANTHROPIC_API_KEY` im Stack.

### 2.1 LiteLLM-Proxy im SQLite-Modus
- **Status:** VERIFIZIERT (Proxy läuft; Test-Inferenz folgt mit 2.3)
- **Akzeptanzkriterium:** LiteLLM-Dienst läuft als systemd-Unit; `/health`-Endpoint antwortet 200; SQLite-Datei initialisiert; kein Redis/Postgres.
- **Test:** Curl gegen `/health` + eine Test-Inferenz über LiteLLM.
- **Verifiziert am:** 15.07.2026 — Belege: LiteLLM **1.92.0** in eigenem venv (`/home/claudebot/litellm/venv`), systemd-Unit `litellm.service` (User claudebot, `--host 127.0.0.1 --port 4000`, active+enabled); `curl /health/liveliness` → **HTTP 200**; Config `config.yaml` mit Ollama-Route (Backend kommt in 2.3). **Interpretation „SQLite-Modus":** Für reines Routing braucht LiteLLM **keine** DB → DB-los betrieben (noch leichter als SQLite, erfüllt „kein Redis/Postgres"). Nur lokal gebunden (ufw lässt ohnehin nur Port 22). Echte Test-Inferenz über den Proxy = mit 2.3 (dann existiert ein Backend).
- **Adam-Bestätigung:** —

### 2.2 Datenschutz-Ampel als Gatekeeper (grün/gelb/rot)
- **Status:** LÄUFT — **Beobachtungsphase aktiv seit 15.07.2026 17:43** (erste eingestufte Nachricht). Wird erst VERIFIZIERT, wenn das Enforcement aktiv **und getestet** ist.
- **Akzeptanzkriterium:** Klassifizierer pro Anfrage liefert Farbe; rote Anfragen werden hart auf lokales Modell geroutet, niemals Richtung Cloud; Routing-Entscheidung im Log nachvollziehbar.
- **Test:** Drei Beispielanfragen (grün, gelb, rot) durchschicken, jeweils das gewählte Backend im Log prüfen.
- **Design-Entscheid Adam (15.07.) — zweistufig:**
  1. **BEOBACHTUNGSPHASE (jetzt):** regelbasierte Einstufung 🟢🟡🔴 läuft mit + wird protokolliert (Regel-Treffer + Nachrichtentext, lokal/privat), **noch KEIN Umrouten** — Status quo bleibt. Regeln bewusst **breit** (Fehlalarme kosten hier nichts, liefern Lerndaten). **Ende:** 4 Wochen + 4 Tage + 4 Stunden **ODER 444 Einstufungen** (was zuerst kommt; ca. **16.08.2026** bei Dauer-Kriterium). Dann **Auswertung** (welche Nachrichten wären rot, welche Regel griff, Fehlalarm-Quote) → Regeln **eng trimmen** (lieber seltener Durchrutscher als Fehlalarme, die im Enforcement Claude „wegnehmen").
  2. **ENFORCEMENT (danach):** Rot → automatisch lokal (Phi-4-Mini), Kennzeichnung „🔴 lokal beantwortet — Regel: X"; **Overrides pro Nachricht:** Präfix `!cloud` erzwingt Claude trotz Rot, `!lokal` erzwingt lokal. `[NEU 2026-07-16]` **Mit dem Enforcement zusammen umsetzen — Lern-Schleife:** Nach einem `!lokal`/`!cloud`-Override einmalig per Buttons anbieten, daraus eine dauerhafte Regel zu machen — NIE ungefragt bei normalen Nachrichten.
- **Regelpflege-UX `[NEU 2026-07-16, umgesetzt `6b6913f`]`:** `/ampel` ist jetzt ein **Button-Menü** (➕ Neue Regel | 📋 Regeln zeigen | 🗑 Regel löschen). „Neue Regel" als Dialog: Farbwahl 🔴🟡(🟢=Hinweis „Standard") → nächste Nachricht wird **deterministisch ohne Claude** (cloud-frei) in die lokale Regeldatei übernommen; Erfassungsmodus klar gekennzeichnet, verfällt nach 60 s, Tastatur-Buttons brechen ab; Bestätigung zeigt Label. Textbefehle bleiben als Kurzweg. **Datenschutz-Abstufung** (auch in CLAUDE.md): heikelste Namen NUR über Button-Dialog/Textbefehl (cloud-frei); natürlichsprachige Pflege via Claude erlaubt, aber Cloud-berührt.
- **Umsetzung 15.07. (`6f34891`):** `ampel.py` (regelbasiert), Hook in `process_user_text` (Text+Voice, rein beobachtend), `/ampel`-Kommando (count/444, Enddatum, Farbverteilung, Top-Regeln). **Regeldatei** editierbar als TOML unter `/home/claudebot/.claude/ampel_rules.toml` (VPS-lokal, **nicht in Git** wegen Klienten-Namen; Vorlage `ampel_rules.example.toml` im Repo). Live verifiziert: echte Nachricht → grün, korrekt geloggt. Muster: IBAN/Konto/Kreditkarte-Regex, Gesundheits-/Zugangsdaten-/Finanz-Stichwörter, Klienten-Namensliste (Adam pflegt lokal).
- **Adam-Bestätigung (Enforcement):** — (nach Auswertung)

### 2.3 Lokales Fallback-Modell (Ollama + Phi-4 Mini Q4)
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Ollama-Dienst läuft; `phi4-mini` geladen (~4 GB); LiteLLM-Route auf Ollama funktioniert.
- **Test:** Eine Inferenz explizit über das lokale Modell anfordern, Antwort kommt zurück.
- **Adam-Bestätigung:** ✅ 15.07.2026 — Ollama-Installer (offizielles Script, ollama.com) nach Script-Prüfung freigegeben.
- **Verifiziert am:** 15.07.2026 — Belege: Ollama **0.32.0** als systemd-Dienst (eigener unprivilegierter User `ollama`, CPU-Modus, `127.0.0.1:11434`, active+enabled); `phi4-mini` (2,5 GB) geladen; Direkt-Inferenz „Paris." (7 s inkl. Erst-Ladung); **über LiteLLM-Route `local` → „Vier." in 1 s** (= zugleich Test-Inferenz für 2.1). Script vor Ausführung analysiert (nur offizielle Quelle, kein GPU/CUDA nötig).

### 2.4 Groq als Cloud-Fallback (nur grün/gelb)
- **Status:** BEWUSST ÜBERSPRUNGEN (Adam 15.07.) — jederzeit nachrüstbar.
- **Akzeptanzkriterium:** Groq-API-Key in LiteLLM eingetragen; Route aktiv; rote Anfragen werden hier explizit verweigert. `[NEU 2026-07-12]` 💰 Groq ist ein bezahlter/limitierter Fremd-Dienst — vor Einrichtung Kosten/Free-Tier mit Adam bestätigen (Kostenregel).
- **💰-Prüfung erledigt (15.07.):** Groq Free-Tier ist **kostenlos ohne Kreditkarte** (nur Rate-Limits: 30 RPM / 6.000 TPM / **1.000 Anfragen/Tag** pro Org; Kosten nur bei freiwilligem Karten-Hinterlegen). Für Einzelnutzer-Neben-Inferenzen weit ausreichend, kein Kostenrisiko.
- **Adam-Entscheid 15.07.:** **Vorerst überspringen** — Neben-Inferenzen laufen alle über das lokale Phi-4-Mini (maximal privat, keine externe Abhängigkeit, kein Key zu verwalten). **Merker:** Bei **2.6** (Verkabelung) und spätestens **5.14** (Link-Inbox) neu bewerten, ob Phi-4-Mini für **längere Zusammenfassungen** qualitativ reicht; falls nicht → Groq gezielt nachrüsten (Free-Tier ohne Karte ist bestätigt).

### 2.5 Kein OpenAI im Stack
- **Status:** VERIFIZIERT
- **Akzeptanzkriterium:** Keine OpenAI-Route in LiteLLM, kein OpenAI-Key gesetzt.
- **Test:** `litellm` Routenliste durchgehen.
- **Verifiziert am:** 15.07.2026 — LiteLLM-Config hat nur die `local`-Route (Ollama); kein `OPENAI` in Config, Env-Datei oder Shell-Env. Zusätzlich: letzte direkte Anthropic-API-Nutzung aus dem Bot-Code entfernt (2.6) — kein Cloud-KI-Provider außer dem Abo-SDK (Haupt-Agent) im Stack.
- **Adam-Bestätigung:** ✅ implizit (Grundsatz E-Werte, „kein OpenAI im Stack").

### 2.6 Neben-Inferenzen des Bots auf LiteLLM umstellen (F1 entschieden)
- **Status:** LÄUFT — Kern umgesetzt, Entscheidung zu langen Zusammenfassungen offen (Neubewertung 5.14).
- ~~**Akzeptanzkriterium (Original):** Bot ruft Inferenzen nur noch über LiteLLM auf (kein direkter Anthropic-Endpoint im Code); Modellwahl funktioniert wie zuvor.~~ `[GESTRICHEN 2026-07-12 — hätte Claude-Verkehr vom Abo auf die bezahlte API verlagert und den Agent-Modus gebrochen]`
- **Akzeptanzkriterium:** Neben-Inferenzen des Bots (Ampel-Klassifizierung, Link-/Video-Zusammenfassungen, TTS-Vorstufen) laufen über LiteLLM (Ollama/Groq); der Claude-Agent (Kern-Sessions mit Tools/Permissions) bleibt direkt am Abo-SDK (`CLAUDE_CODE_OAUTH_TOKEN`). Kein `ANTHROPIC_API_KEY` im Stack. Rote Anfragen werden VOR dem Agenten abgefangen und lokal beantwortet.
- **Test:** Eine Anfrage in Telegram → LiteLLM-Log zeigt Treffer (für Neben-Inferenz); Agent-Anfrage läuft weiter über SDK; Usage-Konsole (console.anthropic.com) bleibt bei 0.
- **Umsetzung 15.07. (`bfdeae1`):** Helfer `_litellm_complete()` (ruft lokalen LiteLLM-Proxy, nie den Agenten). **`_ai_topic_label` (TTS-Kapitel-Labels) auf lokal umgestellt** → **letzte direkte Anthropic-API-Nutzung (`ANTHROPIC_API_KEY`) aus dem Code entfernt**; Label-Erzeugung wieder aktiv (lokal, ohne Key). Live getestet: Label kam über Ollama. Ampel-Klassifizierung ist regelbasiert (kein LLM-Call) → noch privater.
- **⚠️ Offene Entscheidung — lange Zusammenfassungen** (`_summarize_pdf_direct`, künftig Link-/Video-Summaries 5.14): Qualitätstest 15.07. zeigte, dass **Phi-4-Mini für längere Zusammenfassungen unzuverlässig** ist (inhaltlicher Kern gut, aber entgleist danach — Prompt-Template wiederholt/laberte). Daher **vorerst auf dem Abo-SDK belassen** (hohe Qualität, kostenneutral = Abo). Neubewertung bei **5.14**: entweder Phi-4-Mini per Prompt/Stop-Sequenzen zähmen ODER Groq-Free-Tier nachrüsten (bestätigt kostenlos). Bis dahin bewusste, qualitätsgetriebene Abweichung von „alle Neben-Inferenzen via LiteLLM".
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 2.7 Kostenfreie private Websuche (SearxNG) `[NEU 2026-07-16]`
- **Status:** VERIFIZIERT (Funktion E2E; 💰-Konsolencheck = Adam-Stichprobe)
- **Verifiziert am:** 16.07.2026 — Belege: **SearxNG** nativ (venv+granian) als systemd-Dienst `searxng` (nur `127.0.0.1:8888`, JSON-API, limiter aus, secret_key gesetzt), 💰 **kostenlos** (freie Software, keine API-Keys). Test-Query „Netcup VPS" → 39 Treffer. **Bot-Anbindung:** In-Process SDK-MCP-Tool `web_search` → SearxNG; `ClaudeAgentOptions.mcp_servers` + `disallowed_tools=["WebSearch"]`; Such-Tool auto-allowed (kostenfrei). **E2E-Beweis (`b62d9e0`):** Recherchefrage im Agent → nutzte `mcp__suche__web_search` (2×) + WebFetch, **nie WebSearch**, Antwort mit korrekter Quell-URL. Qualitäts-Leitplanke im Prompt bewirbt `web_search`. Sofortmaßnahme (Kostenhinweis/kein Always-Allow für WebSearch) bleibt als Gürtel-und-Hosenträger, ist aber durch `disallowed_tools` faktisch moot.
- **Offen (Adam-Stichprobe):** console.anthropic.com → Usage nach ein paar echten Recherchen weiterhin 0 (Architektur garantiert es: WebSearch deaktiviert, Suche lokal, Inferenz übers Abo).
- **Hintergrund:** Anthropic-**WebSearch kostet** (~$10/1000 Suchen ≈ 1 Cent/Suche) → verstößt gegen die Kostenregel. **Sofortmaßnahme 16.07. bereits umgesetzt (`2f37658`):** WebSearch in Bot-Sessions aus Always-Allow entfernt, Kostenhinweis im Permission-Prompt („💰 ~1 Cent/Suche"), kein „Always allow"-Button. WebFetch bleibt frei (keine Extra-Gebühr).
- **Akzeptanzkriterium:** **SearxNG** als Docker- **oder** systemd-Dienst auf dem VPS, **nur lokal** erreichbar (127.0.0.1, kein öffentlicher Port); dem Bot als Such-Werkzeug angebunden (MCP-Tool oder Custom-Tool in bot.py: Anfrage → SearxNG → Treffer-Liste → Seiten per WebFetch lesen). Danach **Anthropic-WebSearch in Bot-Sessions komplett deaktivieren** (via `disallowed_tools` o. Ä.). Eine Recherche-Testfrage im Bot liefert Antwort **mit Quellen**, UND console.anthropic.com → **Usage bleibt 0** (💰-Beweis: keine Werkzeug-Gebühr).
- **Test:** Recherchefrage im Bot → sinnvolle Antwort mit Quellenlinks; parallel Usage-Konsole = 0.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### Phasen-Audit 2 → 3
- **Audit-Status:** ✅ 16.07.2026 — Phase 2 im Kern abgeschlossen. **VERIFIZIERT:** 2.1 LiteLLM, 2.3 Ollama+Phi-4-Mini, 2.5 kein OpenAI, 2.7 SearxNG (private kostenfreie Suche, Anthropic-WebSearch deaktiviert). **2.4** bewusst übersprungen (Groq, jederzeit nachrüstbar). **Laufende/offene Fäden (bewusst, keine Blocker):** 2.2 Datenschutz-Ampel in Beobachtungsphase (zeitgesteuert bis **~16.08.2026 / 444 Nachrichten** → dann Auswertung + Enforcement); 2.6 Neben-Inferenzen Kern fertig, **lange Zusammenfassungen verschoben nach 5.14**. Querschnitt: 💰-Kostenregel in CLAUDE.md universell verschärft; Antwortqualität + 🎯 Gründlich + robuste Kontext-Recovery umgesetzt.
- **Strategie-Recheck:** ✅ 16.07.2026 — **Adam-Entscheid zur Folge-Reihenfolge (weicht bewusst von der Nummerierung ab):**
  1. **4.1 Backup ZUERST vorziehen** — Gedächtnis, Chat-Logs, **Ampel-Regeldatei (Klienten-Namen!)**, Configs und Env liegen aktuell **nur auf dem VPS** = größtes Verlustrisiko. Backup muss Regeldatei **und** Gedächtnis ausdrücklich einschließen (siehe 4.1).
  2. **8.5 Pre-Send-Hook** — Adams Verlässlichkeits-Schwerpunkt (bereits hochgestuft).
  3. **Phase 3 (LobeChat) erst danach.**
  2.2 läuft parallel zeitgesteuert; 2.6-Rest bei 5.14 mitziehen.

---

## Phase 3 — Interfaces

### 🔒 Zwischen-Audit vor Phase 3 (Adam-Auftrag 17.07.) — PFLICHT-TOR
**Bevor Phase 3 (LobeChat) startet:** kurzer Zwischen-Audit nach Abschluss von 8.5
mit einer bewussten Abwägung — sollen die **Robustheits-Kernpunkte 5.1 (Multi-Session),
5.2 (Nachrichten-Queue-Persistenz) und 5.18 (Session-Watchdog) vor LobeChat vorgezogen**
werden? Sie beheben die **real erlebte** Fehlerklasse **„Bot lebt, Claude-Session tot"**
(23.06. live: Bot munter, Session weg, Adam fragte ins Leere; 8.5 stützt sich für den
Absturzfall ausdrücklich auf 5.18).

**Empfehlung (17.07., Adam entscheidet):**
- **5.2 + 5.18 vorziehen — ja.** Größter Verlässlichkeits-Gewinn pro Aufwand. **5.2**
  (jede eingehende Nachricht sofort persistiert + Status) ist die Grundlage; darauf ist
  **5.18** (Stall-Erkennung pro Nachricht → melden, Session frisch, Nachricht zurück auf
  „offen") klein, weil das Watchdog-Gerüst schon läuft (`watchdog()` in `post_init`).
  **Bonus:** 5.2 repariert genau die Datenlage (echte Empfangszeit, Chunk-IDs), die
  **8.5 v2** (Bezugs-Check) heute blockiert → ein Vorziehen entriegelt zwei Punkte.
  Schätzung: **5.2 ≈ 0,5–1 Tag, 5.18 ≈ 0,5 Tag** (zusammen ~1–1,5 Tage).
- **5.1 (volle Multi-Session) nicht zwingend vorziehen.** Größter Brocken (**~1–2 Tage**;
  heikel: SDK-Session über Neustart „wiederbeleben" vs. Kontext neu aufbauen — Design-
  Entscheid nötig). LobeChat als zweites Frontend informiert die Multi-Session-UX ohnehin
  → eher nach/parallel zu Phase 3, außer Adam will parallele Bot-Sessions früher.
- **Reihenfolge-Vorschlag falls vorgezogen:** 5.2 → 5.18 (= „nichts geht verloren + tote
  Session fängt sich selbst"), 5.1 später. → **Adam-Entscheid offen.**

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
- **Status:** ✅ **VERIFIZIERT** — Sicherung (16.07.) **und** Restore-Probe (17.07.) bestanden; damit ist 4.1 voll verifiziert (Adam-Kriterium: erst mit bewiesener **Rückrichtung**).
- **✅ Restore-Probe durchgeführt (17.07.2026):** Regeldatei + Gedächtnis aus `~/VPS-Backup/latest` in ein **Testverzeichnis** zurückgespielt (Originale unberührt); Prüfskript spiegelt die **echte** Bot-Auflösung (`load_user_memory`-Regex, index-getrieben). **Ergebnis BESTANDEN:** `ampel_rules.toml` per `tomllib` parsebar (Top-Level `rot`/`gelb` heil); `MEMORY.md` vorhanden, **alle 71 verlinkten Dateien auflösbar** (keine still verschwindende Memory-Datei). **⚠️ Nebenbefund:** Das Memory-Backup enthält je Datei eine `._`-**AppleDouble-Ballastdatei** (73 echt + 73 `._`); der index-getriebene Lader ignoriert sie (**ungefährlich**), aber es ist Backup-Müll. **✅ erledigt (17.07.):** `--exclude='._*'`+`.DS_Store` im Backup-Skript (`scripts/vps_backup.sh`), Mac-Backup-Kopie bereinigt (73 entfernt, 73 echte `.md` unversehrt), VPS-Quelle einmalig geleert; **Herkunft geklärt:** stammten aus der tar-Migration Mac→VPS am 14.07. (macOS-`tar`, `COPYFILE_DISABLE` nicht gesetzt) — der Linux-Bot erzeugt keine neuen. Prüfkriterium steht im Abhängigkeits-Register (Restore-Fähigkeit).
- **Akzeptanzkriterium:** Cron-Job läuft täglich; Ziel in Config-Datei konfigurierbar; Trockenlauf zeigt erwartete Dateien. `[NEU 2026-07-15]` **Muss die NICHT-in-Git-liegenden lokalen Dateien einschließen:** `/etc/claude-telegram-bot.env`, `/etc/claude-telegram-bot.token-issued`, das **Bot-Gedächtnis** `/home/claudebot/.claude/memory/`, und die **Ampel-Regeldateien** `/home/claudebot/.claude/ampel_rules.toml` + `/home/claudebot/.claude/ampel_custom.json` (enthält Klienten-Namen — nur lokal!). Diese sind sonst nirgends gesichert.
- **Test:** Eine Testdatei auf VPS, Backup auslösen, Datei am Mac suchen. Plus: Ampel-Regeldatei + Memory im Backup vorhanden.
- **Verifiziert am:** 16.07.2026 — Belege: Skript `scripts/vps_backup.sh` (im Repo, **Mac zieht per rsync/SSH vom VPS** als `claudevps`=root, liest alle Pfade). rsync 3.4.1 auf VPS nachinstalliert (`apt`). **Switch-fähig:** Ziel/Host in `~/.claude/vps-backup.conf` (`BACKUP_DIR`, default `~/VPS-Backup`). Sichert: `/etc/*.env` + `token-issued`, **Gedächtnis** `~/.claude/memory/`, **Ampel** `ampel_rules.toml`+`ampel_custom.json`, **Chat-Logs** `logs/`, Configs (searxng/litellm). Trockenlauf + echter Lauf = **892 K** (MEMORY.md ✅, ampel_rules.toml ✅, env ✅, conversations ✅). **Täglich via launchd** `com.jakuna.vps-backup` (12:30, verpasste Läufe beim Aufwachen; per `kickstart` verifiziert). Erreichbarkeits-Guard (VPS/Mac offline → sauberer Skip). Mac-rsync ist alt (2.6.9) → pro Pfad eigener Aufruf (kein `--ignore-missing-args`).
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
- **Status:** ✅ **VERIFIZIERT — 20.07.2026 (Kill-Test auf dem VPS bestanden, Adam durchgeführt)**. Beide Hybrid-Zweige griffen wie beschlossen; Log: `Reconcile: 1 nachgeholt, 1 gemeldet, 0 aufgegeben`, danach `logs/pending/` leer (keine Leichen).
- **Akzeptanzkriterium:** Jede eingehende Nachricht (Text, Voice, Foto, PDF, Link) wird beim Empfang sofort persistiert; Status (offen/in Bearbeitung/beantwortet) wird mitgeführt; Reboot mitten in der Bearbeitung verschluckt nichts.
- **Test:** Drei Nachrichten kurz hintereinander; während Verarbeitung Bot killen → Restart greift offene Nachrichten auf. *(Der Aufgreif-Teil kommt mit Schritt 2; Schritt 1 macht die Persistenz sichtbar über `/status` + Selbstcheck.)*
- **🏗 Umsetzungsplan (17.07., aus Architektur-Analyse):** Persistenz im **einen Trichter `process_user_text`** (alle 5 Nachrichtentypen). `QueuedJob.update` (lebendes `telegram.Update`) ist **nicht serialisierbar** → gespeichert werden nur die **Primitive** (user_id, chat_id, message_id, thread_id, text, force_tts/output_chat_id/reply_to/thorough) + `status` + Zeitstempel (`time.time()`, NICHT monotonic — überlebt Reboot). **Anhänge sind kein Sonderfall:** ihr lokaler Pfad liegt bereits IM `text` (`[Bild hochgeladen: …]`) und die Datei bleibt dauerhaft in `UPLOAD_DIR` — der Reconcile schickt den `text` einfach neu durch. **Format:** atomare Per-Nachricht-Datei `logs/pending/<key>.json` (tmp+`os.replace`, key=`chat_id_message_id`); beim Beantworten löschen, „offen" = liegt noch da. Neues Modul `pending.py` (analog `ampel.py`/`presend.py`, aber atomar).
  - **✅ Schritt 1 — fertig 17.07. (dieser Commit):** `pending.py`; `QueuedJob.pending_key`; `record()` im Trichter; Status-Übergänge im Worker, gesteuert vom neuen **`_run_job`-Rückgabewert** (`beantwortet`/`aufgegeben`→löschen, `offen`=Kontext-Retry→bleibt, `fehler`→bleibt); Selbstcheck-Invariante „Nachrichten-Persistenz (5.2)" (jetzt 10/10 grün); `/status` zeigt liegende Records. Rein additiv, Hauptpfad unverändert.
  - **✅ Schritt 2 — gebaut 19.07. (lokal verifiziert, Kill-Test auf VPS offen):** `_reconcile_pending(app)` läuft in `post_init` **vor** der Startup-Nachricht und hängt seine Meldung oben an. **HYBRID (Adam-Entscheid 17.07.)** wie beschlossen: `offen` (nie begonnen, also sicher keine halbe Antwort draußen) → **automatisch nachgeholt**, chronologisch (die laufende Queue ist LIFO — nachgeholte Nachrichten bewusst FIFO, sonst liest sich eine Unterhaltung rückwärts) und mit `_RESUMED_PREFIX` im Prompt; `in_bearbeitung`/`fehler` → **nur gemeldet** und aufgelöst (bliebe der Record liegen, meldete der Bot ihn bei jedem Start erneut). Der ganze Job-Pfad liest jetzt **nur noch Primitive** (`_run_job`/`_presend_gate` ohne `job.update.*`); die echte **Sendezeit** wird als `message_date` mitpersistiert, damit die Zeitzeile bei nachgeholten Nachrichten nicht lügt.
  - **🛡 Zwei Fallen, die beim Bau aufgefallen sind und mitgelöst wurden:** (1) **Doppelantwort:** Telegram stellt nach einem Kill dieselben Nachrichten erneut zu (`DROP_PENDING_UPDATES=False` — gewollt), sie kämen also einmal aus der Persistenz und einmal frisch → **Dedup-Sperre `_RESUMED_KEYS`** im Trichter. (2) **Neustart-Schleife:** Eine Nachricht, die den Bot reproduzierbar mitreißt, würde bei jedem Start erneut nachgeholt → **Versuchszähler** (`pending.bump_attempts`, Grenze `_MAX_RESUME_ATTEMPTS`=3), danach wird sie nur noch gemeldet. Zusätzlich beim Bau gefunden: eine lokale Variable `pending` überschattete an zwei Stellen das gleichnamige Modul — umbenannt, bevor daraus ein stiller Fehler wurde.
  - **🔴 Am 19.07. beim Kill-Test aufgedeckt — stiller Antwortverlust (älter als 5.2, aber von 5.2 zugedeckt):** Adams Test lief (unbemerkt) noch gegen Schritt 1, förderte aber einen **gravierenderen** Fehler zutage: Die Antwort auf „Nenn mir eine Stadt" wurde erzeugt, kam aber **nie an**. Ursache: `_send_tts_chunk` gibt bei Fehler `None` zurück (edge-tts war kurz nicht erreichbar — httpx-Verbindungsfehler im Log), `send_answer_to_user` **prüfte den Rückgabewert nicht** und hatte **keinen Text-Fallback**; `_run_job` meldete „beantwortet" und der Persistenz-Record wurde gelöscht → Antwort spurlos weg, während der Agent zu Recht glaubte, geantwortet zu haben (der Text stand in seinem Sitzungs-Kontext). **Behoben zweifach:** (1) **Text-Fallback** — scheitert die Sprachausgabe, geht der Chunk als Text raus (eine gelesene Antwort schlägt keine Antwort); (2) **Zustellnachweis** — `send_answer_to_user` gibt jetzt `bool` zurück, und ohne Zustellung ist der Job-Ausgang „fehler", der Record bleibt liegen (sichtbar in `/status`, gemeldet beim nächsten Start). Beide im Register verankert.
  - **Selbstcheck:** 12/12 (neu: „Wiederaufgreif-Pfad (5.2)" — Job muss **ohne** lebendes `Update` baubar sein; „Zustellnachweis + TTS-Fallback" — fängt die Rückstufung auf den stillen Verlust ab).
- **✅ Abnahme-Beleg (Kill-Test 20.07.2026, `SIGKILL` mitten in der Bearbeitung):** Drei Nachrichten — eine lange Erklärfrage (lief gerade), „Nenn mir eine Blume" (wartete), „Nenn mir einen Fluss" (kam unmittelbar vor dem Kill). Ergebnis nach dem Neustart: **Blume** war persistiert mit Status `offen` → **automatisch nachgeholt** („Die Rose."); **die lange Frage** war `in_bearbeitung` → **nur gemeldet**, nicht wiederholt; **jede Antwort genau einmal**, keine Doppelung.
- **🔎 Lehrreicher Nebenbefund — die beiden Schutznetze greifen ineinander:** Der **Fluss** tauchte in der Nachhol-Liste **nicht** auf, wurde aber trotzdem beantwortet („Der Rhein."). Erklärung: Er erreichte den Bot vor dem Kill nicht mehr, war also nie persistiert — dafür hatte Telegram ihn noch nicht als abgeholt verbucht und lieferte ihn nach dem Neustart erneut aus (`DROP_PENDING_UPDATES=False`, Punkt 8.3). **Die Abdeckung ist damit lückenlos:** was der Bot schon hatte, rettet die eigene Persistenz (5.2); was ihn noch nicht erreicht hatte, liefert Telegram nach. Die Dedup-Sperre musste hier nicht eingreifen (keine `dedup`-Zeile im Log) — sie ist für den Überlappungsfall da, dass Telegram eine **bereits persistierte** Nachricht ein zweites Mal zustellt.
- **🔧 Nachgeschärft nach Adams Rückfrage (20.07., „warum wurde die Brot-Frage weder beantwortet noch nachgeholt?"):** Berechtigt — der Bot war unnötig vorsichtig. `in_bearbeitung` warf zwei verschiedene Zustände in einen Topf: „Claude denkt noch" und „Antwort ist im Versand". Da `stream_response` die Antwort **nur sammelt** und erst danach am Stück verschickt (Vorstufe 5.8), kann im ersten Zustand **nachweislich nichts** beim Nutzer sein — die Nachricht ist gefahrlos nachholbar. **Neuer Status `sendet` (`STATUS_SENDING`)**, gesetzt unmittelbar vor `send_answer_to_user`. **Reconcile holt jetzt `offen` UND `in_bearbeitung` automatisch nach**; nur ab `sendet`/`fehler` wird gemeldet — dort und nur dort ist unklar, ob (bei mehreren TTS-Häppchen) schon etwas ankam. Adams Hybrid-Entscheid bleibt unverändert gültig, die Grenze liegt jetzt nur dort, wo die Unsicherheit **wirklich** beginnt. Die Schleifen-Bremse (max. 3 Anläufe) schützt weiter den Fall, dass genau diese Nachricht den Bot beim Bearbeiten mitreißt. Selbstcheck prüft die Sendemarke mit.
- **✅ Nachschärfung verifiziert (20.07., zweiter Kill-Test):** Die lange Frage stand diesmal in der **Nachhol-Liste** und wurde automatisch beantwortet. Der Agent erkannte dabei selbst, dass er sie kurz zuvor schon ausführlich beantwortet hatte, und lieferte bewusst nur eine Kurzfassung statt einer Dopplung.
- **🔧 Dabei aufgefallen & behoben — der 8.5-Vollständigkeitscheck fragte nach bereits Vorliegendem:** Der Bot schrieb sinngemäß „zwei weitere Nachrichten sind eingegangen, kannst du sie mir zeigen oder wiederholen?" — und beantwortete dieselben Nachrichten zwei Sekunden später selbst. Ursache: Der Vollständigkeits-Befund war als `korrektur` eingestuft und löste eine Korrekturrunde aus. Die ist **per Konstruktion vergeblich**, denn die wartenden Nachrichten liegen in der Queue und sind für den Agenten gar nicht sichtbar — also schloss er, er müsse danach fragen. Kostete zusätzlich eine Claude-Anfrage je gestauter Antwort. **Jetzt neue Befund-Art `vermerk`** (`presend.needs_notice`): keine Korrekturrunde mehr, stattdessen ein ruhiger Hinweis an Adam („ℹ️ 2 neuere Nachrichten von dir sind inzwischen eingegangen — die beantworte ich gleich einzeln"). Merksatz fürs Register: **Ein Befund, den der Agent grundsätzlich nicht beheben kann, darf keine Korrekturrunde auslösen.**
- **🔴 Zweiter, blinder Nachhol-Mechanismus entdeckt & abgeschaltet (20.07.):** Nach dem Deploy-Neustart um 18:56 beantwortete der Bot die **längst beantwortete** Brot-Frage ein zweites Mal — obwohl `logs/pending/` leer war und der Reconcile gar nicht lief (kein Log-Eintrag). Ursache: `_detect_pending_item` **Fall B** riet aus den Chat-Logs („wer war zuletzt dran?"), ob Adams letzte Nachricht unbeantwortet blieb, und startete sie per Autorun neu. Die durch den Kill-Test entstandene `## Session`-Grenze im Log hatte die Heuristik getäuscht. **Das war vor 5.2 die einzige Rettung — jetzt ein zweiter Mechanismus, der nichts von den Persistenz-Records weiß** und die Zusage „jede Nachricht genau einmal" unterläuft. **Fall B abgeschaltet** (samt zweier dadurch verwaister Helfer); Fall A (Claude wartet auf Adams Reaktion) bleibt, er deckt einen anderen Zweck ab. Registerzeile: **`_reconcile_pending` ist die einzige Instanz, die unbeantwortete Nachrichten aufgreift — geraten wird nicht mehr.**
- **Adam-Bestätigung:** ✅ 20.07.2026 — Test selbst durchgeführt (Screenshot mit beiden Meldezweigen).
- **Verifiziert am:** 20.07.2026 (Nachschärfung `sendet` am selben Tag, erneuter Kill-Test empfohlen)

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
- **`[NEU 2026-07-16]` Verwandt — 🎯 Gründlich-Modus (umgesetzt `2f37658`):** Ein-Klick-Button, der die NÄCHSTE Anfrage einmalig mit Opus + hohem Effort + Pflicht-Quellencheck beantwortet, danach zurück zu Standard. Adressiert (mit 8.5) Adams **Verlässlichkeits-Anforderung**: für wichtige Fragen bewusst „auf Nummer sicher".
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.7 TTS opt-in (inkl. Bestätigungen, Voice + Text Kopplung)
- **Status:** OFFEN
- **Akzeptanzkriterium:** TTS-Toggle gilt für ALLE Bot→Adam-Pfade (auch Restart-/Status-Meldungen, vgl. `feedback-tts-also-confirmations`); bei aktivem TTS kommt Voice + Text mit Caption.
- **Test:** Eine inhaltliche Antwort + ein Restart triggern, beides mit Audio.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.8 Einheitlicher Sendepfad mit TTS-Hook (Refactor)
- **Status:** LÄUFT — **Vorstufe gebaut (17.07., `91950ef`)**, Rest offen.
- **Vorstufe fertig:** `send_answer_to_user()` ist der zentrale Sendepfad für **Antworttext** (inkl. TTS-Chunking); `stream_response` sammelt nur noch, der Pre-Send-Hook (8.5) dockt bereits zentral an. **Noch offen:** die ~30 verstreuten `reply_text`-Stellen (Kommandos, PDF-Antworten, Restart, Voice-Echo) laufen weiterhin an diesem Pfad vorbei → die sind der eigentliche 5.8-Rest.
- **Akzeptanzkriterium:** Alle ~30 verstreuten `reply_text`-Stellen laufen über zentralen `send_to_user`-Helper; Pre-Send-Hook (s. Punkt 8.5) dockt zentral an.
- **Test:** Code-Review + Stichprobentest mehrerer Pfade (PDF-Antwort, Restart, Voice-Echo).
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.9 Emoji-Reaktionen (Ja/Nein/erledigt)
- **Status:** OFFEN
- **Akzeptanzkriterium:** `message_reaction` Update-Typ wird ausgewertet; Vokabular gemäß Pin-Liste; Permission-Prompts behalten Inline-Buttons.
- **Test:** Auf eine Ja/Nein-Frage 👍 reagieren → wird als Ja erkannt; auf Aufgabe ✅ → „erledigt".
- **`[NEU 2026-07-19]` Auftrag aus der Web-Planungssitzung — 5.9 vervollständigen:** Reaktionen sollen **JEDE Frage des Bots** beantworten können (Rückfragen, Entscheidungsfragen, Ja/Nein, Optionswahl) — **zusätzlich** zu Text, nicht statt Text. **Stand heute:** `message_reaction`-Updates sind bereits abonniert, ausgewertet werden sie aber **nur im Permission-Flow** (`sess.message_permissions` bildet Telegram-`message_id` → `request_id` ab). **Es fehlt:** dieselbe Zuordnung für „normale" wartende Fragen — d. h. eine Registratur „Bot-Nachricht X ist eine offene Frage der Art Y", auf die eine eingehende Reaktion abgebildet wird. Baut natürlich auf der 5.2-Persistenzschicht auf (die Frage muss einen Neustart überleben).
- **📌 Verbindliche Vokabular-Referenz:** [`reaktionen-vokabular.md`](reaktionen-vokabular.md) — die Telegram-Pin-Liste (v1), 1:1 im Repo. **Vollständig Teil des Akzeptanzkriteriums, nichts davon wird gestrichen** (Adam 19.07.). Dort steht auch der technische Vorbehalt: Telegram gibt den Satz erlaubter Reaktions-Emoji serverseitig vor (`Chat.available_reactions`) — beim Bau **messen statt raten** und für nicht anbietbare Einträge (Verdacht ⭐, 🕐, 1️⃣–9️⃣) einen gleichwertigen Weg (Inline-Button/Textbefehl) vorsehen, damit keine Bedeutung verlorengeht.
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
- **Status:** GEBAUT (20.07.2026) — lokal verifiziert, **Adam-Test auf dem VPS steht aus**
- **✅ Umsetzung 20.07.:** `stall_watchdog()` läuft als zweite Wächter-Schleife neben `watchdog()` (Start in `post_init`, Intervall `STALL_CHECK_INTERVAL` = 30 s). Stall-Maß = `now - max(mb.current_started, sess.last_activity)`; `last_activity` wird in `stream_response` bei **jeder** eingehenden SDK-Nachricht gesetzt (Text, Werkzeug-Aufruf, Werkzeug-Ergebnis) — ein langer, arbeitender Turn gilt damit nie als tot. Ab `STALL_LIMIT` (300 s) greift `_handle_stalled_session()`: Session aus `SESSIONS` raus → Permissions auflösen → `disconnect()` **im Hintergrund mit Zeitlimit** → Worker-Task `cancel()` → Nachricht via 5.2-Record zurück auf `offen` und vorn wieder eingereiht → Meldung an Adam → frischer Worker (neue Session beim nächsten Job).
- **Drei bewusste Entscheidungen (jede war eine Falle):**
  1. **Lockfrei.** `_run_job` hält `sess.lock` über Anfrage *und* Antwortstrom. Ein Wächter, der auf diese Sperre wartet, wartet auf genau den Vorgang, der hängt — er wäre wirkungslos und würde es nie melden. Im Register als Bruchstelle markiert, im Selbstcheck geprüft.
  2. **Wartende Freigaben sind kein Stall.** Steht eine Permission-Anfrage offen, ist Stille **gewollt** (Adam überlegt). Ohne diese Ausnahme zöge der Wächter ihm nach 5 Minuten die Sitzung unter dem Stuhl weg.
  3. **Nur ein automatischer Wiederholungsversuch** (`MAX_STALL_RETRIES` = 1). Hängt es zweimal an derselben Nachricht, liegt es vermutlich an ihr → ehrlich melden statt endlos wiederholen (jeder Anlauf kostet Abo-Kontingent).
- **Lokal bewiesen:** Selbstcheck **13/13** (neue Zeile „Session-Wächter (5.18)" prüft alle drei Teile der Kette + die Lockfreiheit — sie schlug beim ersten Lauf zu Recht an, weil der Musterfall wörtlich im Docstring stand). Zusätzlich Verhaltenstest `scripts/test_stall_5_18.py`: simuliert eine hängende Session und prüft alle Zweige — wartende Freigabe schützt, Session wird entmachtet, Worker abgebrochen, Nachricht wieder eingereiht, Persistenz-Status zurück auf `offen`, Meldung korrekt formuliert, zweiter Stall wiederholt nicht mehr. Alle bestanden.
- **Nachgeschärft beim Test-Aufbau (20.07.):** Der Wächter brach ab, wenn zum laufenden Job **gar kein Session-Objekt** existierte — dabei ist genau das ein Hänger: der Session-*Aufbau* klemmt (`ensure_session` kehrt nie zurück), der Job läuft unbegrenzt weiter, Adam fragt ins Leere. Für ihn ist das vom toten-Session-Fall nicht zu unterscheiden, also gehört es in denselben Schutz. Jetzt greift der Wächter auch dort, mit eigenem Meldungstext („ließ sich nicht einmal starten"); ein normaler Aufbau dauert 1–3 s, Minuten ohne Session sind zweifelsfrei kaputt. **Gefunden, weil der geplante Testablauf den Claude-Prozess VOR dem Session-Start einfriert** — der Test hätte sonst am Wächter vorbeigeprüft und wäre grün-durchgefallen.
- **Sichtbar für Adam:** `/status` zeigt bei einer stillen Session „⏱️ letzte Regung vor Xs (Wächter greift ab 300s)" — sonst ließe sich „läuft seit 4 Minuten" nicht von „hängt seit 4 Minuten" unterscheiden.
- **Hintergrund:** Heartbeat (`bot.py` + `guardian.sh`, fertig am Migrationstag-Vormittag) deckt nur die Bot-Wedge ab. Der seltenere, aber sehr ärgerliche Fall „Bot lebt, aber meine Claude-Agent-Session ist tot" (live demonstriert am 23.06. ab 16:11 — Bot munter, Session weg, Adam fragte ins Leere) wird strukturell mit der Multi-Session/Queue gelöst.
- **Akzeptanzkriterium:** Pro User-Nachricht wird der letzte Streaming-/Antwort-Zeitpunkt mitgeführt. Liegt für eine Nachricht im Status „in Bearbeitung" länger als ein konfigurierbares Limit (Default 5 Min) kein Streaming + keine Antwort vor: Bot meldet Adam aktiv „Claude-Session reagiert nicht — starte neu, bitte letzte Nachricht ggf. nochmal", beendet die hängende Session sauber und legt eine frische an. Status der Nachricht wird auf „erneut offen" gesetzt, damit nichts verloren geht.
- **🏗 Umsetzungsplan (17.07.):** `last_activity` (monotonic) je `Mailbox`, aktualisiert in `stream_response` bei jedem TextBlock/ToolUseBlock; `current_started` liefert den Beginn. Stall-Prüfschleife neben `watchdog()` in `post_init` (Intervall ~30 s, Limit `STALL_LIMIT` Default 300 s). Bei Stall: Adam melden → hängende Session **lockfrei** beenden (Vorbild `client.interrupt()`-Pfad, NICHT auf `sess.lock` warten) → Job über den 5.2-Record auf „offen" zurück → frische Session beim nächsten Job. Sitzt großteils auf vorhandenen Bausteinen auf (`close_session`, Kontext-Rotation-Re-Enqueue, `interrupt`). **Setzt 5.2 voraus** (Persistenz-/Status-Schicht).
- **Test:** (a) *lokal, erledigt:* `scripts/test_stall_5_18.py` simuliert die hängende Session vollständig. (b) *auf dem VPS, mit Adam:* Limit kurzzeitig herabsetzen (`STALL_LIMIT=60` in der Env, Neustart), eine Frage stellen, die den Agenten länger arbeiten lässt — der Wächter darf **nicht** zuschlagen, solange 🔧-Spuren kommen. Danach echter Hänger-Test: den **Claude-CLI-Subprozess** der laufenden Session gezielt killen, während ein Job läuft → innerhalb von Limit + 30 s muss die Meldung kommen und die Nachricht automatisch nochmal drankommen. ⚠️ **Vorher** mit `pgrep -u claudebot -af claude` den genauen Prozess heraussuchen — ein pauschales `pkill -f claude` träfe auch `bot.py` selbst (der Pfad enthält „claude"!) und wäre ein Bot-Neustart statt eines Session-Hängers, also der falsche Test. Anschließend `STALL_LIMIT` zurück auf 300.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.19 Rechnungs-Workflow per Sprache (Aufstellung + Rechnung aus dem Bot) `[NEU 2026-07-13]`
- **Status:** OFFEN
- **Hintergrund:** Beide Generatoren sind fertig und real erprobt (Desktop-Session „Rechnungs-Automatisierung", `~/Projects/rechnungen`: `scripts/generate_aufstellung.py` = Postenaufstellung Excel+PDF, `scripts/generate_rechnung.py` = Rechnungs-PDF im Markenlayout mit Auto-Nummer pro Jahr; Rechnungen 014-26/015-26 damit produktiv erstellt und in iCloud abgelegt). Hier fehlt nur die Bot-Anbindung. Details/Konventionen: Memory `project-rechnungs-automatisierung`.
- **Akzeptanzkriterium:** Adam gibt per Sprachnachricht Tage/Tätigkeiten durch; Bot fragt Variables gezielt nach (Tagessatz, Spesen In-/Ausland, Übernachtung, Fahrzeug/Pauschalen), erzeugt über die vorhandenen Generatoren Aufstellung (Excel+PDF) + Rechnung (PDF), legt beides nach Abnicken im richtigen iCloud-Projektordner ab (Benennungsschema je Zweig) UND postet die Dateien zur schnellen Kontrolle in den Ausgabekanal (Phase 6). Rechnungsnummer fortlaufend (Register), mit Bestätigungs-Rückfrage vor Vergabe.
- **Test:** Eine komplette Rechnung per Sprache vom iPhone: Zuruf → Rückfragen → Dateien liegen im iCloud-Ordner + im Ausgabekanal → Beträge und Nummer stimmen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.20 Token-Erneuerungs-Frühwarner (OAuth-Token läuft jährlich ab) `[NEU 2026-07-14]`
- **Status:** OFFEN
- **Hintergrund:** `CLAUDE_CODE_OAUTH_TOKEN` ist ~1 Jahr gültig; **ohne gültigen Token läuft der Agent GAR NICHT** (harter Ausfall, keine Antworten). Erzeugung nur manuell (Browser-OAuth via `claude setup-token`) → die Warnung muss früh und verlässlich kommen. Umsetzt E5.
- **Akzeptanzkriterium:** Token-Ausstelldatum wird bei jedem Setzen festgehalten (Sidecar `/etc/claude-telegram-bot.token-issued`). Ein **bot-unabhängiger** systemd-Timer (täglich) prüft das Alter und schickt Adam ab **~10 Monaten** (spätestens **30 Tage Vorlauf**) eine Telegram-Nachricht direkt über die Bot-API (`curl`), zunehmend dringlicher je näher der Ablauf. Renewal-Prozedur (neuer Token → Env-Zeile ersetzen → `systemctl restart` → alter Token wird ersetzt, **Zero-Downtime** solange vor Ablauf) dokumentiert.
- **Test:** Timer mit künstlich vordatiertem Ausstelldatum → Warn-Nachricht trifft in Telegram ein; Renewal-Prozedur einmal trocken durchgespielt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.21 Versions-/Update-Monitor (nicht-automatische Komponenten) `[NEU 2026-07-14]`
- **Status:** OFFEN
- **Hintergrund:** `unattended-upgrades` deckt nur Debian-OS-Sicherheit ab. whisper.cpp (Eigenbau), `claude`-CLI (npm), Node.js (NodeSource), Bot-Python-Deps (venv) entwickeln sich unterschiedlich schnell; **große Versionssprünge** (neue Node-Major, SDK-Bruch) sollen bewusst und früh sichtbar werden — wie „App-Update verfügbar". Umsetzt E5, löst die frühere Backlog-Notiz „Wartungs-/Update-Routine" ab.
- **Design (register-basiert, Adam-Vorgabe 14.07.):** Der Monitor arbeitet gegen ein **zentrales Komponenten-Register** (Manifest, z. B. `components.yaml`) — je Eintrag: Name, aktuelle-Version-ermitteln (Befehl), verfügbare-Version-ermitteln (Quelle: apt/npm/GitHub-Releases/PyPI), Major-Schwelle. So werden **alle künftig hinzugefügten** Systeme/Komponenten automatisch mitgeprüft — Bedingung: **jede neue versionierte Komponente wird beim Einbau ins Register eingetragen** (verbindliche „fertig"-Regel, siehe E5). Startbestand: Node.js, `@anthropic-ai/claude-code`, whisper.cpp, alle `requirements.txt`-Pakete, Debian-Release.
- **Akzeptanzkriterium:** Regelmäßiger (z. B. wöchentlicher) automatischer Versionscheck über ALLE Register-Einträge; bei neueren Versionen Telegram-Hinweis mit „aktuell vs. verfügbar", **Major-Sprünge markiert** (dringlicher). Neue Komponente ins Register aufnehmen → erscheint ohne Code-Änderung im nächsten Check. Reine Info/Reminder — **Installation bleibt bestätigt/manuell** (kein eigenmächtiges Major-Upgrade, deckt sich mit E3/„Empfehlung statt eigenmächtigem Wechsel").
- **Test:** Check läuft, listet mind. eine Komponente mit Versionsvergleich; simulierte neue Version löst Telegram-Hinweis aus.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.22 STT-Schnellumschalter small↔medium + Tempo-Button-UX `[NEU 2026-07-14]`
- **Status:** VERIFIZIERT (Kern) — **5.22a Threads ✅** (`efba6d9`: alle 4 Kerne, medium 47 s→25 s), **5.22b Umschalter ✅** (`3404f84`). **Adam 15.07.: „Funktioniert sehr gut."** Offen nur noch die optionale Button-Ausdünnung — **Adam 15.07.: „machen wir später"** (evtl. ohnehin zusammen mit neuen Phase-2-Features). Zurückgestellt, kein Blocker.
- **Umsetzung 15.07.:** Neue Tastatur-Zeile `🎙️ Genau (medium) / 🎙️ Flott (small)` mit ✓ am Aktiven; Umschaltung **zur Laufzeit ohne Neustart** (globaler `_ACTIVE_STT`, in Prefs persistiert, `transcriber.set_model()` vor jeder Voice); aktives Modell auch in `/status`. Register-basiert (`_discover_stt_models` findet, was unter `models/` liegt).
- **Hintergrund:** Adam-Wunsch nach VPS-Livegang: Whisper `medium` ist präzise, aber ~45 s/30-s-Voice auf VPS-CPU; für eilige Alltags-Voice soll per Knopf auf `small` (~15 s) umschaltbar sein (beide Modelle liegen schon unter `models/`). Zudem Button-Leisten-Ausdünnung prüfen: Tempo evtl. als EIN Toggle (⚡ Schnell ↔ 🚀 Max) statt drei Effort-Buttons — Entscheidung nach Praxisphase mit ⚡ Schnell. Aufklärung 14.07. dokumentiert: Effort-Buttons steuern Denk-Tiefe (Schnell=low=schnellste Antworten, Max=max=gründlich+langsam) — nicht verwechseln.
- **Ist-Analyse VPS 14.07. (gemessen):** Aktives Modell = **medium** (`WHISPER_MODEL_PATH`), NICHT small. Threads: `transcribe.py` nutzt `cpu_count()-2` → auf dem 4-Kern-VPS nur **2 von 4 Kernen** (`-t 2`). **Quick Win: auf `-t 4` (bzw. 3) anheben** → deutlich schneller ohne Qualitätsverlust; erster Griff für 5.22. **Keine GPU** (nur virtuelle VGA `1234:1111`) → **Metal/CUDA unmöglich**. `[⚠️ Kongruenz-Hinweis:` Der Telegram-Bot riet Adam am 14.07. zu **Apple-Metal + Mac-Pfaden** und behauptete, er nutze „small" — beides falsch: **der Bot weiß noch nicht, dass er auf dem Linux-VPS läuft** (Selbstverortung veraltet). Nur seine Vorschläge „kleineres Modell" + „mehr Threads" sind übertragbar/kongruent zu 5.22. **Bot-Selbstverortung korrigiert `[✅ erledigt 14.07.]`:** Memory-Notiz `deployment-vps-hosting.md` in die VPS-Memory eingefügt + im MEMORY.md-Index verankert (Bot läuft auf Linux-VPS, kein GPU/Metal, Server-Pfade, STT medium/CPU) — Laden verifiziert; greift ab nächster Session.`]`
- **Bestätigt Adam 14.07. (nach Livegang):** Flaschenhals ist **eindeutig die Transkription** — getippte Nachrichten und Antworten NACH der Transkription kommen zügig; nur das Verwandeln der Voice in Text dauert. Adam nimmt für Alltagstempo **gern etwas geringere Genauigkeit** in Kauf (medium versteht ihn zwar meist gut, ist aber zu langsam für schnelle Dialoge). Zwei Stoßrichtungen bewerten: (1) **schneller bei guter Qualität** — z. B. mehr Threads/`-t`, `small`+Prompt-Bias, quantisierte/`q5`-Modelle, oder externe schnellere STT, solange 💰/Datenschutz passen; (2) **verlässlicher Schnell-Umschalter** als Minimum. Wunsch: „nicht so eingeschränkt sein, wenn ich schnelle Dialoge führen will."
- **Akzeptanzkriterium:** Knopf/Kommando wechselt `WHISPER_MODEL_PATH`-Nutzung zur Laufzeit (ohne Neustart), aktives STT-Modell sichtbar (Button-Häkchen und/oder `/status`); Umschaltung wirkt ab der nächsten Voice.
- **Test:** Voice mit medium, umschalten, gleiche Voice mit small — beide transkribiert, Tempo-Unterschied messbar.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.23 Session-Start-Diät (Memory-on-demand statt 280-KB-Vorladung) `[NEU 2026-07-14]`
- **Status:** VERIFIZIERT — **Adam 15.07.: „mit dem Test bin ich so weit zufrieden."** Implementiert + auf VPS E2E bewiesen (`d2b3037`).
- **Umsetzung 15.07.:** `load_user_memory()` lädt jetzt nur den **Kern voll** (Typ `user`+`feedback`+Index = Identität & Verhaltensregeln, ~135 KB inkl. Recall) und listet `project`+`reference` (dickes Detailwissen) als **„bei Bedarf nachlesen"** mit Dateipfad. Agent bekommt den Memory-Ordner via `add_dirs`; Lesen dort ist im Permission-Callback **ohne Rückfrage** erlaubt. **E2E-Messung VPS:** Kern-Frage (Identität) **4,2 s** korrekt; On-demand-Frage (Projekt-Detail) **7,3 s**, Agent nutzte **Read** und antwortete korrekt (`generate_aufstellung.py`). Erste Session-Antwort damit von ~60 s → ~4 s. 💰 Zudem ~halbierter Token-Verbrauch pro Session-Start.
- **Bewusste Abweichung vom <30-KB-Ziel:** Kern bleibt bei ~135 KB, weil **alle Verhaltensregeln voll geladen** bleiben (Verlässlichkeit vor maximalem Tempo — Adam-Priorität). Latenz-Ziel (<30 s) trotzdem klar erreicht. Aggressiveres Trimmen (Regeln nur als Index-Hooks) wäre möglich, aber erst nach Adam-Freigabe wegen Regel-Risiko.
- **⚠️ Betriebs-Hinweis:** `CLAUDE.md` im WORKDIR muss `claudebot` gehören (der Dienst schreibt sie pro Session). Ein versehentlich als root angelegtes `CLAUDE.md` blockiert das Schreiben → Fallback auf gekürzten argv-Pfad. Bei Tests als root vermeiden / danach `chown claudebot`.
- **Hintergrund:** Erste Antwort einer frischen Session dauerte ~1 Min (Adam, 14.07., 20:53) — Hauptanteil: kompletter Memory-Bestand (280 KB ≈ 70k Token) wird bei JEDEM Session-Start als Kontext eingelesen (seit Fix `bc48004` via CLAUDE.md-Datei). Verschärft sich mit wachsendem Memory. 💰 Kostet zudem Abo-Kontingent pro Session-Start.
- **Akzeptanzkriterium:** Session-Start lädt nur einen schlanken Kern (Identität/Präferenzen/aktive Projekte + MEMORY.md-Index, Ziel < 30 KB); alles Weitere liest der Agent bei Bedarf selbst per Read-Tool aus `CLAUDE_MEMORY_DIR` (Index verweist auf die Dateien). Erste Antwort einer frischen Session spürbar schneller (Ziel: < 30 s bei einfacher Frage); Gedächtnis-Qualität bleibt (Stichproben-Fragen wie 14.07. weiterhin korrekt).
- **Test:** Frische Session, einfache Frage → Latenz messen (vorher/nachher); danach Detail-Frage, deren Antwort NUR in einer nachgelagerten Memory-Datei steht → Agent liest nach und antwortet korrekt.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 5.24 Proaktive Session-Rotation bei Füllstand ~80 % (mit Übergabe) `[NEU 2026-07-15]`
- **Status:** OFFEN
- **Hintergrund:** Reaktive Auto-Recovery bei Kontext-Überlauf ist umgesetzt (15.07., `is_context_overflow` → Session verwerfen + Nachricht automatisch neu, Statuszeile „📏 Kontext war voll …"; Skill-Ladungen in Bot-Sessions abgelehnt). **Vorbeugung fehlt noch:** bevor das Fenster voll ist, sanft rotieren.
- **Akzeptanzkriterium:** Session-Füllstand wird aus den **Usage-Daten des SDK** (`ResultMessage`/Token-Zähler) mitgeführt; ab **~80 %** proaktiv neue Session mit **Übergabe-Zusammenfassung** (kurzer Kontext-Übertrag), transparent für Adam, ohne Antwortverlust. Passt zu 5.1 (Multi-Session), 5.2 (Queue/Persistenz), 5.18 (Watchdog).
- **Test:** Lange Session künstlich füllen → Rotation greift vor dem harten Überlauf; Folgeantwort kennt den Gesprächsfaden noch.
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
- **Akzeptanzkriterium:** Systemd-Timer um 04:00 MEZ; prüft Token gültig, API erreichbar, TTS-Cleanup-Selbsttest, Migrations-Endpunkte; Bericht ins Bot-Log + bei Fehler Telegram-Hinweis. `[NEU 2026-07-16]` **Arbeitet die Prüfbefehle des Abhängigkeits-Registers (`ABHAENGIGKEITEN.md`) ab** und meldet **Bezugs-Brüche proaktiv per Telegram** (Schutz vor stillen `#BEZUG!`-Fehlern). Das Register ist die Prüfliste — neue Komponenten dort eintragen heißt automatisch: ab dem nächsten 4-Uhr-Lauf mitgeprüft.
- **Test:** Manueller Auslöser → Bericht erscheint. Plus: eine Register-Abhängigkeit künstlich brechen (z. B. `searxng` stoppen) → Check meldet den Bruch per Telegram.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.2 Regressionstest nach jeder größeren Änderung
- **Status:** OFFEN
- **Akzeptanzkriterium:** Isolierter Read-only-Test-Lauf, der nach einem Deploy/Change automatisch durchgezogen wird; Ergebnis sichtbar. `[NEU 2026-07-16]` **Nutzt das Abhängigkeits-Register (`ABHAENGIGKEITEN.md`) als Prüfliste:** nach jeder Änderung werden die Prüfbefehle der betroffenen UND der davon abhängigen Komponenten durchlaufen — so fällt ein `#BEZUG!`-Bruch sofort auf, nicht erst Wochen später.
- **Test:** Eine simulierte Änderung → Regressionstest läuft + meldet grün/rot. Plus: Register-Kette prüfen (z. B. Whisper-`small`-Modell entfernen → Test meldet „STT-Umschalter verliert Button-Zeile").
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
- **Status:** LÄUFT — **v1 LIVE seit 17.07.2026 (`91950ef`), Adam-Grundtests bestanden; kleine Nachbesserungen 17.07. erledigt** (Werkzeug-Spur immer sichtbar + Tipp-Indikator + `setMyCommands`). VERIFIZIERT erst mit v2 (Bezugs- + Sicherheits-Check).
- **🏗 Architektur-Umbau (Adam-Entscheid 17.07., Kern des Punktes):** Es gab **keinen Moment, in dem der vollständige Antworttext bekannt war, bevor er den Nutzer erreichte** — `stream_response` sendete jeden TextBlock sofort und leerte den Puffer. Ein *Pre*-Send-Hook war damit unmöglich. **Umbau:** `stream_response` **sammelt** den Turn-Text und gibt ihn zurück; gesendet wird erst nach der Prüfung über den neuen zentralen `send_answer_to_user()` (= **Vorstufe von 5.8**, dort dockt später TTS/alles an). Werkzeug-Spur (🔧) bleibt live als Lebenszeichen. Absturzfall deckt der Watchdog (5.18) ab.
- **v1-Umfang (Adams drei Schutzgeländer):** (1) **Wochentag↔Datum → AUTO-FIX** ohne Schleife/Latenz (selbsttragend prüfbar: `date(y,m,d).weekday()` braucht kein Systemdatum; Auto-Korrektur nur im ±370-Tage-Fenster → historische/zitierte Daten werden nur geloggt, kein fremder Wortlaut geändert; „Sonnabend"=Samstag erzeugt keinen Fehlalarm). (2) **Vollständigkeit** (neuere Nachrichten in der Queue) → **EINE** Korrekturrunde mit konkretem Befund; greift sie nicht → Senden **mit ⚠️-Vermerk**, nie hängen lassen. (3) **Tentativ-Sprache → nur Log** (Hedging kann berechtigt sein). Alle Treffer geloggt → **`/presend`** zeigt die Fehlalarm-Quote.
- **Adam-Tests 17.07.:** normale Frage ✅ · Recherchefrage ✅ · Sprachnachricht ✅ (Stimmqualität = späterer Punkt) · **Datums-Test ✅** (falscher Wochentag wird still korrigiert). Fazit Adam: „Grundbetrieb läuft."
- **✅ Nachbesserungen erledigt (17.07., Adam-Auftrag):** (a) **Werkzeug-Spur jetzt IMMER sichtbar** — die `if not sess.quiet`-Sperre ist raus; die 🔧-Spur ist als fester Bestandteil der Puffer-Option 1 das Lebenszeichen bei langen Turns. **Zusätzlich Tipp-Indikator** (`ChatAction.TYPING`-Keepalive-Task, alle 4 s) für Turns ganz ohne Werkzeug — **Default jetzt verbose**, damit der Indikator von Haus aus läuft (sonst zeigte eine reine Textfrage nichts); `/quiet` schaltet nur ihn ab, die 🔧-Spur bleibt. **Folge:** `/quiet`/`/verbose` dämpfen jetzt den Tipp-Indikator (nicht mehr die 🔧-Spur); Hilfe-/Menütexte ehrlich nachgezogen. *(→ Adam-Entscheid nötig, falls `/quiet` wieder ALLES stummschalten soll.)* (b) **`setMyCommands`** in `post_init` registriert das Befehlsmenü → `/presend` & Co. per „/"-Autovervollständigung; kein blindes Vertippen mehr. **Selbstcheck nach den Änderungen: 9/9 Kernfunktionen ok.**
- **v2-Vormerkungen:** **(b) Nachrichten-Bezugs-Check** bewusst NICHT in v1 — mit der heutigen Datenlage nicht fehlalarm-frei: BOT_MSGS hält bei Antworten >4096 Zeichen nur die **erste** Chunk-ID (send_chunked gibt nur `first_msg` zurück → Replies auf Folge-Chunks resolven still zu ''), ist RAM-only + FIFO-gedeckelt (400); die **echte Empfangszeit** sieht das Modell nie. → erst Datenlage reparieren, dann v2. **(e) Sicherheits-Gegencheck** → v2 **im Gründlich-Modus** (starkes Modell mit Quellen), ausdrücklich NICHT über Phi-4-Mini (das schwächste Modell soll nicht die Urteile des stärksten kontrollieren).
- **🔍 Nebenbei behobene Analyse-Funde (17.07.):** (1) **Zeitzeile log:** `_current_datetime_context()` behauptete „Systemzeit beim **Eingang** dieser Nachricht", rechnete aber mit dem **Bearbeitungs-Start** → nutzt jetzt `update.message.date` (echte Empfangszeit); bei Queue-Wartezeit >2 Min werden **Eingang UND Jetzt** genannt. Ohne diesen Fix hätte der Hook gegen eine falsche Referenz geprüft und **korrekte Antworten „korrigiert"**. (2) **Zeitbasen-Falle:** `current_started`=`monotonic()` vs. `received_at`=`time()` — ein Vergleich wirft keinen Fehler, wäre aber **immer wahr** (Fehlalarm bei JEDER Antwort) → Vollständigkeit vergleicht nur `received_at` gegen `received_at`. (3) **Autorun-Pfad** hätte nach dem Umbau **still keine Antworten mehr gesendet** → gefixt (prüft + sendet selbst). Alle drei Bezüge stehen jetzt in `ABHAENGIGKEITEN.md`.
- **Alt-Status:** OFFEN — **Kernpunkt, PRIORITÄT HOCHGESTUFT (Adam 16.07.)** — adressiert Adams Verlässlichkeits-Anforderung strukturell (nicht nur per Aufmerksamkeit). Vorziehen, sobald Phase 2/3 stabil. Zwischenschritte 16.07. bereits umgesetzt: Antwortqualitäts-Leitplanke fest im Session-System-Prompt (Quellen prüfen, Unsicherheit kennzeichnen, keine ungeprüften Behauptungen) + 🎯 Gründlich-Modus (Opus+Max+Pflicht-Quellencheck für wichtige Fragen). Der volle Hook am Sendepfad ersetzt/ergänzt diese Disziplin durch eine harte Garantie.
- **Akzeptanzkriterium:** Zentraler Hook am Sendepfad; (a) zeitliche Aussagen gegen Systemdatum verifiziert, (b) Bezug auf Nachricht prüft Absender+Uhrzeit+Inhalt, (c) Vollständigkeits-Check seit letzter Antwort, (d) erweiterbar.
- **Test:** Bewusst eine falsche Datumsangabe formulieren → Hook blockiert/korrigiert; gleiches für falsche Nachrichten-Referenz.
- **Adam-Bestätigung:** —
- **Verifiziert am:** —

### 8.6 Doku-Spiegel-Integrität (nutzerseitige Texte dürfen nicht driften) `[NEU 2026-07-19]`
- **Status:** TEILWEISE — **Sofort-Korrekturen erledigt 19.07.**, Prüfskript offen.
- **Hintergrund (Adam-Auftrag aus der Web-Planungssitzung 19.07.):** Bei der Video-Analyse fiel auf, dass `/hilfe` noch das **alte 12-Button-Layout** zeigte, obwohl die 9-Button-Tastatur längst deployt war. Klasse „**der Bot erzählt etwas anderes, als er tut**".
- **✅ (a) VPS-Klon geprüft — Entwarnung:** Die Vermutung „uncommitteter lokaler Live-Fix an `bot.py` auf dem VPS" **trifft nicht zu**. `git status` im Klon: sauber, `mac-produktivstand` synchron mit origin. Nichts abzugleichen, nichts überschrieben. **Die Drift saß im Repo-Code selbst** (der `/hilfe`-Text wurde beim Tastatur-Umbau `426a7f3` nicht mitgezogen).
- **✅ Sofort behoben (19.07.):** (1) `/hilfe` an die Wirklichkeit nachgezogen — es waren **drei** Abweichungen, nicht eine: Haiku fehlte in der Modellzeile, die ganze Zeile 🎙️ Genau/Flott + 🎯 Gründlich fehlte, und die längst entfernte Zeile „🔄 Neustart / 🔊🔇 TTS / ℹ️ Info" stand noch drin; zusätzlich fehlten `/ampel` und `/presend` in der Befehlsliste. (2) **Zweite Drift-Quelle gefunden und behoben:** die Startup-Begrüßung meldete bei **jedem** Neustart „Noch offen: 4.1 Backup … 8.5 Pre-Send-Hook" — beides seit 17.07. erledigt. Quelle: `_read_pending_items()` liest offene `[ ]`-Punkte aus `~/.claude/memory/pending-items.md` **auf dem VPS**; die zwei Punkte dort abgehakt (Datei gelesen, gezielt geändert, Rest unangetastet) → Bot meldet jetzt 0 offene Punkte.
- **▶ (b) Offen — Prüfskript `scripts/check_hilfe_buttons.py`:** vergleicht die in `bot.py` **tatsächlich definierten** Buttons/Kommandos (`_main_keyboard`, `setMyCommands`) mit den in den Nutzertexten (`/hilfe`, `/start`, Startnachricht) genannten; **Abweichung = Fehler**. In den Selbstcheck bzw. 8.1 einhängen und in `ABHAENGIGKEITEN.md` registrieren. *(Erst dann fängt die Prüfung solche Fälle automatisch — die heutigen Korrekturen waren Handarbeit.)*
- **✅ (c) Regel in CLAUDE.md:** „Jede Feature-Änderung aktualisiert ihre nutzerseitigen Texte (`/hilfe`, `/start`, Startnachricht) im **selben Commit**" — eingetragen 19.07.
- **Test:** Button/Kommando in `bot.py` ändern, ohne den Hilfetext anzufassen → Prüfskript/Selbstcheck muss anschlagen.
- **Adam-Bestätigung:** —
- **Verifiziert am:** (a)+(c) 19.07.2026; (b) —

### 8.7 Governance: VPS-Repo-Kopie ist für den Bot schreibgeschützt `[NEU 2026-07-19]`
- **Status:** TEILWEISE — Regel dokumentiert 19.07., technische Verankerung offen.
- **Akzeptanzkriterium (Adam-Auftrag 19.07.):** Die bestehende Regel „**der Bot editiert das Bot-Repo nicht**" gilt ausdrücklich auch für die **VPS-Kopie `/home/claudebot/claude-telegram-bot`**: **lesen ja, editieren/committen niemals**. Deploys laufen **ausschließlich** über `git pull`, ausgelöst von Adam. Verankert in CLAUDE.md/Drehbuch und — soweit machbar — im **System-Prompt** bzw. **Permission-Callback** des Bots.
- **Warum:** Ein Selbst-Edit auf dem VPS erzeugt genau die Divergenz, die 8.6 (a) heute noch als Verdacht hatte — Repo-Stand und laufender Code laufen auseinander, und der nächste `git pull` kollidiert oder überschreibt stillschweigend Handarbeit.
- **✅ Erledigt:** Regel in CLAUDE.md aufgenommen (Abschnitt Governance).
- **▶ Offen:** technische Durchsetzung im Bot (System-Prompt-Zusatz + hartes Deny im Permission-Callback für Schreibzugriffe unterhalb `/home/claudebot/claude-telegram-bot`), Registerzeile in `ABHAENGIGKEITEN.md`.
- **Test:** Den Bot bitten, eine Datei im VPS-Repo zu ändern → muss ablehnen und auf den `git pull`-Weg verweisen.
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
- `[NEU 2026-07-14]` **Unbekannte Bot-Kommandos nicht stumm ignorieren** (Fund aus 0.7): `/model sonnet` blieb ohne jede Reaktion, weil kein solcher Befehl existiert und der Text-Handler Commands ausschließt. Wunsch: Catch-all für unbekannte `/…`-Kommandos mit Hinweis + ggf. `/model <name>` als Textbefehl parallel zu den Inline-Buttons.
- `[GEKLÄRT 2026-07-14]` ~~Wartungs-/Update-Routine für nicht-automatische Komponenten~~ → **zu konkreten Punkten 5.20 (Token-Frühwarner) + 5.21 (Update-Monitor) unter Grundsatz E5 aufgewertet.** Konkrete Update-Befehle je Komponente dort bzw. quartalsweise: `npm update -g @anthropic-ai/claude-code`; `git pull` + whisper.cpp neu bauen; `pip install -U -r requirements.txt` im venv; `apt full-upgrade`.
- `[NEU 2026-07-17]` **VPS-Software-Wartung** (Adam-Auftrag): `unattended-upgrades` deckt **nur das OS** ab — NICHT die selbst gepflegte Software: `pip`-Pakete der beiden venvs (Bot inkl. **claude-agent-sdk**, LiteLLM), **SearxNG** (git-Klon + requirements), **Ollama**/Modelle, whisper.cpp (Eigenbau), globales `claude`-CLI (npm), Node (NodeSource). Braucht eine periodische Update-Routine mit Bestätigung (kein eigenmächtiges Major-Upgrade, E3/E5). **Später in den 4-Uhr-Check (8.1) integrieren** — dort Versionsstände melden; überschneidet sich bewusst mit **5.21** (register-basierter Update-Monitor), 5.21 bleibt die Umsetzung, 8.1 der Auslöser.
- `[NEU 2026-07-16]` **Telegram-Mini-App für Ampel-Regelpflege** (Komfort-Ausbau): kleine Web-Oberfläche direkt in Telegram (Regeln listen/anlegen/löschen, Kennzahlen). **Abhängig vom HTTPS-Endpoint aus 1.9** (Webhook/TLS) — erst danach sinnvoll.
- `[NEU 2026-07-15]` **Ampel-Zweitstufe: modellbasierte Einstufung für Grenzfälle** (Adam-Entscheid 15.07.): Die regelbasierte Ampel (2.2) bleibt die schnelle, deterministische erste Stufe. Als späterer Ausbau: für unklare Fälle (kein Regel-Treffer, aber potenziell sensibel) eine zweite Stufe per lokalem Modell (Phi-4-Mini) einstufen lassen — nur lokal, nie Cloud. Erst nach Praxiserfahrung mit den getrimmten Regeln bewerten.
- `[NEU 2026-07-14]` **Cowork Mac-unabhängig nutzbar machen** (Prüf-/Ausbaupunkt, nach Migration): Ziel: Cowork-artige Arbeit (Claude mit Zugriff auf Adams Dateien) auch bei ausgeschaltetem Mac. Erkenntnisstand 07/2026: Cowork-Sitzungen laufen remote, aber der Datei-Zugriff hängt an der geöffneten Desktop-App des jeweiligen Rechners (nur macOS/Windows — Linux-VPS scheidet als Host aus). Optionen: (a) pragmatisch: Cowork-Arbeitsordner in synchronisierten Speicher legen — bevorzugt Nextcloud auf unserem VPS (passt zum Datenschutz-Entscheid „weg von iCloud"), Sync-Client auf dem Mac; bei iCloud-Nutzung „Speicher optimieren" für den Ordner deaktivieren; (b) Bastellösung Windows-VPS/Cloud-Mac mit dauerhaft offener Desktop-App — wegen Pflegeaufwand + Sicherheitsbedenken vorerst verworfen; (c) beim Phasen-Audit 9→10 neu bewerten, ob Anthropic inzwischen Headless-/Linux-Unterstützung bietet. Teilbedarf wird ohnehin durch VPS-Bot + Approval-Hub (9.4) abgedeckt.

---

## Nacharbeiten

*Punkte, die am Ende offen geblieben sind und Schritt für Schritt nachgeholt werden.*

(leer)

---

## Strategie-Audit-Log

*Pro Phasenwechsel: kurzes Resümee + Anpassungen der Folge-Phasen.*

- **2026-07-14 — Audit 0 → 1:** Phase 0 vollständig grün. Besonderheit: 0.7 abweichend vom Wortlaut am Produktivbetrieb verifiziert (Adam-Entscheid; der Branch lief bereits seit 13.07. produktiv — erneuter Stopp hätte nur Risiko wiederholt, das den Vorfall vom 12.07. auslöste). Folge-Phasen unverändert; zwei Mitnahmen an Phase 1/2 notiert (Memory-Umzug für 0.4-Regel → 1.7; kein `ANTHROPIC_API_KEY` auf VPS, `_ai_topic_label` → 2.6). Nächster Punkt: **1.0 Server-Zugang**.

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
