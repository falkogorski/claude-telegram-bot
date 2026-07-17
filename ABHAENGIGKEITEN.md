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
| **`presend.py`** + `presend.WEEKDAYS_DE` | Pre-Send-Hook (8.5) im `_run_job`/Autorun. **`WEEKDAYS_DE` ist die EINZIGE Wochentagsliste** — `_current_datetime_context()` referenziert sie; zweite Liste anlegen ⇒ stiller Drift zwischen Prompt und Prüfung | `python3 -c "import presend; print(presend.WEEKDAYS_DE)"`; `grep -c "weekdays_de = \[" bot.py` = **0** (keine Zweitliste!) |
| **`update.message.date`** (echte Empfangszeit) | Ehrliche Zeitzeile im Prompt (`_current_datetime_context(received_dt)`) + konsistente Referenz für den Hook. Fällt sie weg → Prompt behauptet wieder eine falsche Eingangszeit | `_run_job` reicht `job.update.message.date` durch; bei Queue-Wartezeit >2 Min nennt die Zeile Eingang UND Jetzt |
| **VPS-Zeitzone Europe/Berlin** | Alle Zeitangaben des Bots + Datums-Prüfung des Hooks. Liefe der Server auf UTC, wären Prompt UND Hook konsistent falsch (Adam würde 2 h Versatz sehen) | `timedatectl \| grep -q "Europe/Berlin"` (verifiziert 17.07.: CEST, +0200 ✅) |

---

## Änderungshistorie

- **2026-07-16** — Register angelegt (Adam-Auftrag „#BEZUG!-Sicherung"), Erstbefüllung
  mit allen zum Stand Phase 2 bestehenden Ketten. Verkabelung mit 8.1/8.2 in deren
  Akzeptanzkriterien vermerkt.
