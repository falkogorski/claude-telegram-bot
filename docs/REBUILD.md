<!-- ROLLE: rebuild-anleitung -->
# REBUILD — Server bei Totalausfall neu aufsetzen (4.4)

**Stand:** 23.07.2026, aus dem Ist-Zustand dokumentiert. **Keine Secrets in
dieser Datei** — alle Geheimnisse kommen aus dem 4.1-Backup bzw. werden neu
erzeugt. Ergänzt `WIEDERANLAUF.md` (Rollen) um die technische Wiederherstellung.
Zielbild: Ein neuer VPS läuft in < 2 Stunden wieder produktiv.

## 0. Was du brauchst

- Zugriff auf das **4.1-Backup** am Mac: `~/VPS-Backup/latest/` (env, memory,
  ampel, logs, configs) + `~/VPS-Backup/bundles/` (datierte Repo-Vollkopien).
- GitHub-Zugriff auf `falkogorski/claude-telegram-bot` (Code) und
  `falkogorski/claude-bot-logs` (Logs).
- Netcup-Zugang (oder beliebiger Debian-13-VPS, ≥4 GB RAM empfohlen — Whisper).

## 1. Grundsystem (Debian 13)

1. VPS aufsetzen — **Netcup-Weg: Reinstall mit vorab hinterlegtem SSH-Key**
   (umgeht das Aussperr-Risiko der nachträglichen Härtung; Blaupause-Muster).
2. Nutzer anlegen: `adduser claudebot` (unprivilegiert — der Dienst läuft nie als root).
3. Härtung wie Punkt 1.1/1.2: ufw (nur SSH), fail2ban, unattended-upgrades.
4. Pakete: `apt install git python3 python3-venv ffmpeg rsync curl build-essential cmake`
   (cmake/build-essential für whisper.cpp) + Node.js via NodeSource (für claude-CLI-Fälle).

## 2. Code + Laufzeit

```
sudo -u claudebot git clone https://github.com/falkogorski/claude-telegram-bot.git /home/claudebot/claude-telegram-bot
cd /home/claudebot/claude-telegram-bot && sudo -u claudebot python3 -m venv .venv && sudo -u claudebot .venv/bin/pip install -r requirements.txt
```

- **whisper.cpp** bauen (`whisper-cli` ins PATH) und die Modelle
  `models/ggml-small.bin` + `ggml-medium.bin` laden — BEIDE, sonst verschwindet
  die STT-Umschaltzeile still (Register-Warnung).
- **8.7-Hook setzen** (Klon ist reine Deploy-Kopie):
  `.git/hooks/pre-commit` mit `exit 1`-Blocker, ausführbar (Wortlaut siehe
  MIGRATION.md 8.7). Keine git-Identity im Klon konfigurieren.

## 3. Umgebung & Secrets (`/etc/claude-telegram-bot.env`, root:root 0600)

Struktur (Werte aus dem 4.1-Backup `latest/etc/` zurückspielen oder neu erzeugen):

```
TELEGRAM_BOT_TOKEN=            # @BotFather (bei Kompromittierung: dort rotieren)
CLAUDE_CODE_OAUTH_TOKEN=       # `claude setup-token` am Mac — ABO, NIE ANTHROPIC_API_KEY (💰!)
ALLOWED_USER_IDS=304455165
CLAUDE_MODEL=sonnet
CLAUDE_MEMORY_DIR=/home/claudebot/.claude/memory
CONVERSATION_LOG_DIR=/home/claudebot/claude-telegram-bot/logs/conversations
UPLOAD_DIR=/home/claudebot/Downloads/claude-uploads
WHISPER_MODEL_PATH=/home/claudebot/claude-telegram-bot/models/ggml-medium.bin
```

Sidecar `/etc/claude-telegram-bot.token-issued` (Ausstelldatum, für 5.20) mit anlegen.

## 4. Nur-lokale Daten zurückspielen (aus 4.1)

Vom Mac (`~/VPS-Backup/latest/`) nach `/home/claudebot/`:
- `memory/` → `~/.claude/memory/` (**MEMORY.md-Index muss dabei sein** — ohne
  Index-Zeile wird eine Datei still nicht geladen)
- `ampel/` → `~/.claude/ampel_rules.toml` + `ampel_custom.json` (Klienten-Regeln —
  fehlen sie, stille Rückstufung auf Defaults!)
- `logs/` → `~/claude-telegram-bot/logs/` (Gesprächs-Historie; alternativ aus
  dem Log-Repo `claude-bot-logs` klonen)
- Erst Restore, DANN Dienststart — sonst begrüßt der Bot mit leerem Gedächtnis.

## 5. Dienste (systemd, als root)

- **`claude-telegram-bot.service`**: User=claudebot,
  `EnvironmentFile=/etc/claude-telegram-bot.env`,
  ExecStart=`/home/claudebot/claude-telegram-bot/.venv/bin/python bot.py`,
  WorkingDirectory=Repo, Restart=always → `enable --now`.
- **`claude-log-sync.service` + `.timer`** (täglich 05:10, Persistent=true):
  ExecStart=`scripts/log_sync.sh` als claudebot. Vorher: neuen Deploy-Key
  erzeugen (`ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_logsync`), als
  **Write-Deploy-Key NUR im Log-Repo** eintragen (Vertrauenszonen-Regel:
  niemals ein Key mit Bot-Repo-Schreibrecht auf dem Server!), SSH-Alias
  `github-logsync` in `~/.ssh/config`, Klon nach `~/logsync/claude-bot-logs`.
- Weitere Dienste des Ist-Stands: **SearxNG** (lokale Suche, 2.7), **LiteLLM**
  (2.1), **Ollama + Phi-4-Mini** (2.3) — Configs liegen im 4.1-Backup
  (`configs/`); Reihenfolge unkritisch, der Bot läuft auch ohne sie (Websuche
  fällt dann aus, Rest funktioniert).

## 6. Verifikation (Pflicht, in dieser Reihenfolge)

1. `systemctl is-active claude-telegram-bot` → active; Startnachricht kommt in Telegram an.
2. **Selbstcheck-Zahl in der Startnachricht lesen** — muss der aktuellen
   Check-Anzahl entsprechen (Deploy-Beweis; Stand 23.07.: 18).
3. `scripts/check_hilfe_buttons.py` → „Doku-Spiegel konsistent".
4. Eine Text- und eine Sprachnachricht schicken (Transkription + Antwort).
5. `systemctl list-timers claude-log-sync.timer` → nächster Lauf geplant;
   einmal `systemctl start claude-log-sync.service` → Commit im Log-Repo.
6. Mac-seitig `bash scripts/vps_backup.sh --dry-run` → alle Gruppen gelistet
   (Backup-Kette wieder geschlossen; ohne bewiesene Rückrichtung gilt 4.1 nicht).

## Fallback ohne GitHub

Die datierten **git-Bundles** (`~/VPS-Backup/bundles/*.bundle`) enthalten das
komplette Repo samt Historie: `git clone claude-telegram-bot-JJJJMMTT.bundle`
funktioniert vollständig offline — das ist der Schutz gegen das Szenario
„fehlerhafter Inhalt überall hin synchronisiert".
