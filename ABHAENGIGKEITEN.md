# 🔗 Abhängigkeits-Register

**Zweck (Adam-Auftrag 16.07.2026):** Schutz gegen stille Abhängigkeits-Brüche —
das „**Excel-`#BEZUG!`-Problem**": Eine Komponente wird geändert oder entfernt,
und irgendwo bricht unbemerkt etwas, das davon abhing.

**Verbindliche Regel (steht auch in CLAUDE.md):**
1. **Vor** jeder Änderung/Entfernung einer Komponente: hier nachsehen, wer davon abhängt.
2. **Danach** die abhängigen Komponenten mittesten (Prüfbefehl aus der Tabelle).
3. **Beim Bau neuer Features** deren Bezüge **sofort** hier eintragen — nicht später.

**Verkabelung:** Der tägliche 4-Uhr-Funktionscheck (**8.1**) arbeitet die
Prüfbefehle dieser Tabelle ab und meldet Brüche proaktiv per Telegram. Der
Regressionstest (**8.2**) nutzt sie als Prüfliste nach Änderungen.

> Lesart der Tabelle: **Komponente** → wer sie braucht → womit man prüft, dass sie trägt.
> Prüfbefehle laufen (soweit nicht anders vermerkt) **auf dem VPS**; `[Mac]` = am Mac.

---

## Laufzeit-Dienste

| Komponente | Wird benötigt von | Prüfbefehl / Prüfkriterium |
|---|---|---|
| **systemd `claude-telegram-bot`** | Alles Nutzerseitige (Telegram-Betrieb 24/7) | `systemctl is-active claude-telegram-bot` = `active` |
| **systemd `searxng`** (127.0.0.1:8888) | Bot-Websuche `web_search` (2.7) → damit die gesamte Fakten-/Quellenprüfung (Antwortqualität) | `systemctl is-active searxng` **und** `curl -s "http://127.0.0.1:8888/search?q=test&format=json" \| grep -q '"results"'` |
| **systemd `ollama`** + Modell `phi4-mini` | LiteLLM-Route `local` → Neben-Inferenzen (2.6), künftig **Ampel-Enforcement** (rot → lokal) | `systemctl is-active ollama` **und** `ollama list \| grep -q phi4-mini` |
| **systemd `litellm`** (127.0.0.1:4000) | `_litellm_complete()` → `_ai_topic_label` (TTS-Kapitel), künftige Neben-Inferenzen | `systemctl is-active litellm` **und** `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:4000/health/liveliness` = `200` |
| **launchd `com.jakuna.vps-backup`** `[Mac]` | Tägliches Backup (4.1) — einzige Sicherung der nur-lokalen VPS-Daten | `launchctl list \| grep -c vps-backup` = `1` |

## Zugänge & Geheimnisse

| Komponente | Wird benötigt von | Prüfbefehl / Prüfkriterium |
|---|---|---|
| **`CLAUDE_CODE_OAUTH_TOKEN`** (in `/etc/claude-telegram-bot.env`) | **Bot-Agent** (jede Session). **Ausnahme:** LiteLLM/Neben-Inferenzen brauchen ihn NICHT (laufen lokal über Ollama — F1-Leitplanke). 💰 Nie durch `ANTHROPIC_API_KEY` ersetzen! | Token gesetzt **und** Mini-Inferenz: als `claudebot` mit Token → `claude -p "1+1="` liefert `2`. **⏰ Läuft ~14.07.2027 ab** (Sidecar `/etc/claude-telegram-bot.token-issued`, Frühwarner = 5.20) |
| **SSH-Key `~/.ssh/id_ed25519` + Aliase `claudevps`/`claudebot`** `[Mac]` | Backup (4.1), Code-Deploy (`git pull`), gesamte Fernwartung dieser Sitzung | `ssh -o BatchMode=yes claudevps true` (Exit 0) |
| **GitHub-Deploy-Key** (`/home/claudebot/.ssh/github_deploy`, read-only) | Code-Deploy auf den VPS (`git pull origin mac-produktivstand`) | `sudo -u claudebot ssh -n -o BatchMode=yes -T git@github.com 2>&1 \| grep -q "successfully authenticated"` — **`-n` ist Pflicht!** Ohne `-n` frisst das innere `ssh` die Standardeingabe des umgebenden Skripts, alle Folge-Prüfungen fallen still aus (am 16.07. genau so passiert) |
| **Telegram-Bot-Token + `ALLOWED_USER_IDS`** | Bot-Erreichbarkeit + Zugangsschutz | Bot-Log zeigt `Application started` ohne `401`/`Conflict` |

## Daten (nur lokal — nicht in Git!)

| Komponente | Wird benötigt von | Prüfbefehl / Prüfkriterium |
|---|---|---|
| **Ampel-Regeldateien** `~/.claude/ampel_rules.toml` + `ampel_custom.json` | Ampel-Klassifizierung (2.2), `/ampel`-Menü + Textbefehle, künftiges **Enforcement**. Enthält Klienten-Namen → **nur lokal, nie Cloud/Git** | `ampel.status()["rules_file_exists"]` = `True`; `/ampel regeln` listet Regeln. **Fehlt die Datei → stille Rückstufung auf eingebaute Defaults (Klienten-Regeln weg!)** |
| **Bot-Gedächtnis** `~/.claude/memory/` (+ `MEMORY.md`-Index) | Session-Kontext (5.23), Selbstcheck, Identität/Verhaltensregeln. **Index-Zeile fehlt → Datei wird still NICHT geladen** | `load_user_memory()` liefert nicht-leer; `MEMORY.md` vorhanden; Selbstcheck ohne „MEMORY.md fehlt" |
| **Whisper-Modelle** `models/ggml-medium.bin` **und** `ggml-small.bin` | Voice-Transkription; **beide** nötig für den STT-Umschalter (5.22) — fehlt eines, **verschwindet die 🎙️-Button-Zeile still** (`_discover_stt_models`) | beide Dateien vorhanden; `bot._discover_stt_models()` enthält `small` **und** `medium` |
| **Nur-lokale VPS-Dateien gesamt** (env, token-issued, memory, ampel, logs, configs) | **Backup 4.1** — es gibt keine zweite Kopie (nicht in Git) | `[Mac]` `bash scripts/vps_backup.sh --dry-run` listet alle Gruppen; `~/VPS-Backup/latest` > 0 B |
| **Restore-Fähigkeit des Backups** (nicht nur die Sicherung!) | Der gesamte Notfall-Plan — ein Backup, aus dem nie zurückgespielt wurde, ist ein **unbewiesenes Versprechen** (Adam 17.07.) | `[Mac]` Restore-Probe in ein **Testverzeichnis** (nie über die Originale): `ampel_rules.toml` per `tomllib` parsebar, `MEMORY.md` vorhanden + die darin verlinkten Dateien auflösbar. **✅ verifiziert 17.07.** (71/71 Links auflösbar, TOML ok, dokumentiert in 4.1). Wiederholbar als 4-Uhr-Check (8.1). `._`-AppleDouble-Ballast **bereinigt 17.07.**: `--exclude='._*'`+`.DS_Store` im Backup-Skript, Mac-Kopie + VPS-Quelle geleert; Herkunft = tar-Migration 14.07. (Linux-Bot erzeugt keine neuen) |
| **Chat-Logs** `logs/conversations/` | Session-Recall (`_recent_conversation_recall`), Backup, künftig Recall-Index (5.11) | Ordner vorhanden; Tagesdatei des heutigen Datums wächst |

## Steuerung & Schutzschichten

| Komponente | Wird benötigt von | Prüfbefehl / Prüfkriterium |
|---|---|---|
| **`.claude/settings.json` + `.claude/hooks/*.sh`** `[Mac]` | SessionStart-Banner + **Schreibschutz** auf MIGRATION.md/CLAUDE.md (Führungs-Register). Fehlt/unausführbar → Schutz still weg | Hooks ausführbar (`-x`); Blocktest: veralteter Klon → `guard-master-files.sh` Exit `2` |
| **🎯 Gründlich-Modus** (Opus + Max-Effort) | **Pre-Send-Hook v2** — der Sicherheits-Gegencheck läuft dort (starkes Modell), bewusst NICHT in Phi-4-Mini | 🎯-Button in der Tastatur vorhanden; v1-Hook unabhängig davon lauffähig |
| **`_COST_TOOLS` + `disallowed_tools=["WebSearch"]`** | 💰-Kostenregel im Bot (WebSearch-Sperre). Entfernt → kostenpflichtige Suche wieder möglich | `WebSearch` in `disallowed_tools` der `ClaudeAgentOptions`; `_COST_TOOLS` enthält `WebSearch` |
| **Memory-Auto-Allow + `add_dirs`** | Session-Diät (5.23): Agent liest Detailwissen selbst nach. Fehlt → Rückfragen bei jedem Memory-Read oder gar kein Zugriff | `add_dirs` enthält Memory-Pfad; Read im Memory-Ordner ohne Permission-Prompt |
| **`stream_response()` SAMMELT nur** (seit 17.07., Vorstufe 5.8) | **Jede** Aufrufstelle muss den Rückgabetext selbst senden: `_run_job` (Hauptpfad), `_presend_gate` (Korrekturrunde), `_do_autorun` (Startup-Tasks). ⚠️ **Wer hier „wieder senden lässt", erzeugt Doppel-Antworten; wer den Rückgabewert ignoriert, verschluckt die Antwort still** (genau so beim Umbau am Autorun-Pfad passiert) | `grep -c "await stream_response(" bot.py` = **3**, und jede Stelle sendet danach via `send_answer_to_user` bzw. reicht den Text an `_run_job` zurück |
| **`send_answer_to_user()`** (zentraler Sendepfad) | Antwort-Ausgabe inkl. TTS-Chunking; **Vorstufe von 5.8** — künftige Sende-Stellen hier andocken, nicht daneben | Antwort erscheint in Telegram (Text bzw. Sprachnachricht bei TTS an) |
| **Zustellnachweis (`send_answer_to_user -> bool`) + Text-Fallback bei TTS-Ausfall** `[NEU 19.07.]` | `_run_job` entscheidet **daran**, ob die Nachricht als beantwortet gilt (`False` → Ausgang „fehler", Record bleibt liegen). ⚠️ **Live-Beleg 19.07.:** edge-tts war kurz nicht erreichbar; `_send_tts_chunk` gab `None` zurück, der Aufrufer prüfte das nicht → Antwort erzeugt, **nie zugestellt**, trotzdem als erledigt abgehakt und der Persistenz-Record gelöscht. Wer den Rückgabewert wieder ignoriert oder den Fallback entfernt, stellt genau diesen stillen Antwortverlust wieder her | Selbstcheck-Zeile „Zustellnachweis + TTS-Fallback" grün (prüft Rückgabetyp **und** das Vorhandensein des Fallbacks); im Log erscheint bei TTS-Ausfall `TTS-Chunk fehlgeschlagen — Text-Fallback` statt Stille |
| **`pending.py` + `logs/pending/<key>.json`** (5.2 Nachrichten-Persistenz, seit 17.07.) | `process_user_text` (`record` beim Empfang), `_session_worker` (Status/`resolve` je nach **`_run_job`-Ausgang**: `beantwortet`/`aufgegeben`→löschen, `offen`→bleibt=Kontext-Retry, `fehler`→bleibt liegen), `_reconcile_pending` (Start), `run_self_check`, `/status`. ⚠️ Wer die vier Rückgabe-Strings von `_run_job` umbenennt/streicht, bricht die Status-Pflege **still** (Records würden nie gelöscht → der Reconcile griffe erledigte Nachrichten erneut auf) | Selbstcheck-Zeilen „Nachrichten-Persistenz (5.2)" **und** „Wiederaufgreif-Pfad (5.2)" grün; `python3 -c "import pending"` fehlerfrei; `logs/pending/` schreibbar (record→resolve hinterlässt keine Datei) |
| **`QueuedJob`-Primitive statt `update`** (5.2 Schritt 2, seit 19.07.) | Der **gesamte** Job-Pfad: `_run_job` und `_presend_gate` lesen `job.user_id/chat_id/message_id/thread_id/message_date` — **nicht** `job.update.*`. Bei nachgeholten Jobs ist `update` **None** (ein `telegram.Update` überlebt keinen Neustart). ⚠️ Wer irgendwo wieder `job.update.…` einbaut, bricht ausschließlich den Wiederaufgreif-Pfad — im Alltag fällt das **nie** auf, erst beim nächsten harten Neustart geht die Nachricht verloren | `grep -n "job\.update" bot.py` liefert **nur** den abgesicherten Bot-Fallback in `_run_job` (`if job.update is not None`); Selbstcheck „Wiederaufgreif-Pfad (5.2)" baut einen Job mit `update=None` |
| **Crash-Restart-Grund (`_write_crash_restart_reason`) + Secret-Maske (`_mask_secrets`)** `[NEU 20.07.]` | Der `try/except BaseException` um `main()` am Dateiende — **ohne ihn stirbt der Bot wortlos** und meldet nach dem Neustart nur „Bin wieder da", ohne dass Adam vom Absturz erfährt. ⚠️ **`_mask_secrets` ist Pflicht auf jedem Fehlertext, der in Datei/Chat landet:** Telegram-Fehler zitieren die API-URL **inklusive Bot-Token** (`InvalidToken` sogar wörtlich) — ungefiltert stünde der Token in `bot-restart-reason.txt` (wird gebackupt!), im Chat-Log und in der Startnachricht. Beim Testcrash am 20.07. genau so aufgetreten und behoben | Testcrash mit ungültigem Token (lokal, `HOME` umbiegen!): Datei wird geschrieben, enthält **keinen** Token; `grep -c "_mask_secrets" bot.py` ≥ 2 |
| **`_reconcile_pending` ist die EINZIGE Instanz, die unbeantwortete Nachrichten aufgreift** `[NEU 20.07.]` | Niemand sonst darf raten, was noch offen ist. `_detect_pending_item` **Fall B** tat genau das (Heuristik „wer war zuletzt im Chat-Log dran?") und beantwortete am 20.07. eine längst beantwortete Frage ein zweites Mal — die Session-Grenze nach dem Kill-Test hatte die Heuristik getäuscht. **Fall B ist abgeschaltet**; Fall A (Claude wartet auf Adams Antwort) bleibt, er deckt einen anderen Zweck ab. ⚠️ Wer einen zweiten Nachhol-Weg einbaut (Log-Analyse, Memory-Eintrag, Autorun), bricht die Zusage „jede Nachricht genau einmal" | `grep -n "Fall B" bot.py` zeigt nur den Abschalt-Kommentar; nach einem Neustart ohne liegende Records wird **keine** alte Nachricht erneut beantwortet |
| **Dedup-Sperre `_RESUMED_KEYS`** (5.2 Schritt 2) | `process_user_text` — verwirft die **Zweitzustellung** einer Nachricht, die der Startup-Reconcile bereits nachgeholt hat. Nötig, weil `DROP_PENDING_UPDATES=False` (gewollt!) Telegram dieselben Nachrichten nach einem Kill erneut liefern lässt. Ohne die Sperre: **doppelte Antwort** auf dieselbe Frage | Kill-Test (5.2): jede Nachricht wird nach dem Neustart **genau einmal** beantwortet; Log zeigt ggf. `dedup: … Telegram-Zweitzustellung verworfen` |
| **Schleifen-Bremse `_MAX_RESUME_ATTEMPTS`** (Default 3) | `_reconcile_pending` — begrenzt, wie oft eine liegengebliebene Nachricht automatisch nachgeholt wird. ⚠️ Auf 0 gesetzt oder entfernt: Eine Nachricht, die den Bot reproduzierbar mitreißt, wird bei **jedem** Start erneut nachgeholt → Neustart-Schleife | Selbstcheck „Wiederaufgreif-Pfad (5.2)" prüft `>= 1` und den Versuchszähler (`pending.bump_attempts`) |
| **`presend.py`** + `presend.WEEKDAYS_DE` | Pre-Send-Hook (8.5) im `_run_job`/Autorun. **`WEEKDAYS_DE` ist die EINZIGE Wochentagsliste** — `_current_datetime_context()` referenziert sie; zweite Liste anlegen ⇒ stiller Drift zwischen Prompt und Prüfung | `python3 -c "import presend; print(presend.WEEKDAYS_DE)"`; `grep -c "weekdays_de = \[" bot.py` = **0** (keine Zweitliste!) |
| **Echte Sendezeit → `QueuedJob.message_date`** (seit 19.07. Primitiv statt `update.message.date`) | Ehrliche Zeitzeile im Prompt (`_current_datetime_context(received_dt)`) + konsistente Referenz für den Hook. Fällt sie weg → Prompt behauptet wieder eine falsche Eingangszeit. **Umgestellt mit 5.2 Schritt 2:** die Zeit wird beim Empfang als Unix-Zeit **persistiert**, damit auch eine nach Neustart nachgeholte Nachricht ihre echte Sendezeit behält (ein lebendes `update` gibt es dort nicht mehr). ⚠️ Nicht mit `received_at` verwechseln — das ist die Verarbeitungszeit und liegt bei nachgeholten Nachrichten deutlich später | `process_user_text` füllt `message_date` aus `msg.date.timestamp()` und schreibt es in den Record; `_run_job` baut `received_dt` daraus; bei Wartezeit >2 Min nennt die Zeile Eingang UND Jetzt |
| **Session-Wächter `stall_watchdog` + `UserSession.last_activity`** (5.18) `[NEU 20.07.]` | Der einzige Schutz gegen „Bot lebt, Claude-Session tot" (live 23.06.: Bot nahm Nachrichten an, quittierte sie, antwortete nie — **niemand merkte es**, weil kein Fehler anfällt). Drei Teile, die nur GEMEINSAM wirken: (1) `stream_response` setzt `sess.last_activity` bei **jeder** SDK-Nachricht, (2) `stall_watchdog` vergleicht gegen `max(mb.current_started, sess.last_activity)`, (3) `post_init` startet die Schleife. ⚠️ **Fällt ein Teil weg, ist der Wächter still weg** — dieselbe Klasse Fehler, gegen die er schützt. ⚠️ Der Abbruch läuft **bewusst ohne `sess.lock`** (den hält der hängende Vorgang); wer dort eine Sperre einbaut, legt den Wächter lahm. ⚠️ Sessions mit offener Permission-Anfrage werden **übersprungen** — sonst zieht der Wächter Adam die Sitzung weg, während er über einen Freigabe-Button nachdenkt | Selbstcheck-Zeile „Session-Wächter (5.18)" grün (prüft alle drei Teile + Lockfreiheit); Verhaltenstest `.venv/bin/python scripts/test_stall_5_18.py` endet mit „ALLE TEILPRÜFUNGEN BESTANDEN"; Log beim Start: `Stall-Wächter gestartet (Intervall=…)` |
| **Stall-Stellschrauben `STALL_LIMIT` / `STALL_CHECK_INTERVAL` / `MAX_STALL_RETRIES`** (5.18) `[NEU 20.07.]` | Abwägung Fehlalarm ↔ Erkennungszeit. `STALL_LIMIT` zu klein ⇒ der Wächter killt **arbeitende** Sessions (kostet Abo-Kontingent, weil die Nachricht neu gestellt wird); zu groß ⇒ Adam wartet unnötig lange. `MAX_STALL_RETRIES` (Default 1) verhindert die Endlosschleife „hängt → neu → hängt" bei einer Nachricht, die den Hänger auslöst | Selbstcheck prüft `STALL_LIMIT_S >= 60`; `/status` zeigt bei stiller Session „letzte Regung vor …s (Wächter greift ab …s)" |
| **Voice-Eingangsschutz `VOICE_STAGE` + `pending.merge()`** (5.2) `[NEU 20.07.]` | Schließt das **25-Sekunden-Loch**, in dem eine Sprachnachricht durch nichts geschützt war (Persistenz entstand erst nach Download **und** Transkription). Zwei Teile, die zusammengehören: (1) `on_voice` legt den Eintrag **vor** dem Download an, (2) `_reconcile_pending` erkennt die Stufenmarke und **meldet statt nachzuholen**. ⚠️ **Reihenfolge ist die Funktion:** rutscht `pending.record` hinter `_download_tg_file`, ist die Lücke wieder offen — der Selbstcheck vergleicht deshalb die Position im Quelltext. ⚠️ Der Platzhaltertext darf **niemals** an Claude gehen; fiele die `VOICE_STAGE`-Abfrage im Reconcile weg, bekäme das Modell eine leere Hülle statt Adams Anliegen vorgelegt. ⚠️ Jeder Abbruchzweig in `on_voice` **muss** `_resolve_voice_stage` aufrufen, sonst meldet der Bot dieselbe Sprachnachricht bei jedem künftigen Start erneut | Selbstcheck-Zeile „Voice-Eingangsschutz (5.2)" grün (prüft Reihenfolge, Abbruchzweige, Reconcile-Erkennung, Vorhandensein von `pending.merge`); Verhaltenstest `.venv/bin/python scripts/test_voice_entry_guard.py` endet mit „ALLE TEILPRÜFUNGEN BESTANDEN"; Log bei jeder Sprachnachricht: `Sprachnachricht empfangen: … Eingang gesichert` |
| **VPS-Zeitzone Europe/Berlin** | Alle Zeitangaben des Bots + Datums-Prüfung des Hooks. Liefe der Server auf UTC, wären Prompt UND Hook konsistent falsch (Adam würde 2 h Versatz sehen) | `timedatectl \| grep -q "Europe/Berlin"` (verifiziert 17.07.: CEST, +0200 ✅) |

---

## Änderungshistorie

- **2026-07-16** — Register angelegt (Adam-Auftrag „#BEZUG!-Sicherung"), Erstbefüllung
  mit allen zum Stand Phase 2 bestehenden Ketten. Verkabelung mit 8.1/8.2 in deren
  Akzeptanzkriterien vermerkt.
- **2026-07-17** — `pending.py` + `logs/pending/` als neue Kette eingetragen (5.2 Schritt 1,
  Nachrichten-Persistenz). Bezug auf die vier `_run_job`-Rückgabe-Strings markiert (stiller
  Bruch, falls umbenannt).
- **2026-07-20** — Session-Wächter (5.18) eingetragen: die Drei-Teile-Kette
  (`last_activity` → `stall_watchdog` → Start in `post_init`) und die Stellschrauben.
  Ausdrücklich vermerkt: **Lockfreiheit** ist Teil der Funktion, nicht Schlamperei, und
  wartende Permission-Anfragen sind kein Stall.
- **2026-07-20 (2)** — Voice-Eingangsschutz eingetragen. Kernpunkt der Zeile ist die
  **Reihenfolge**: Die Sicherung muss vor dem Download stehen, sonst ist sie wirkungslos —
  eine Abhängigkeit, die kein Aufruf sichtbar macht und die nur ein Test festhalten kann.
