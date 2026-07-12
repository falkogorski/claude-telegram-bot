# MIGRATION.md — Drehbuch: Telegram-Bot vom Mac auf den Server

> **Für das ausführende Modell:** Dieses Drehbuch ist so geschrieben, dass es
> Schritt für Schritt abgearbeitet werden kann, ohne eigene Architektur-
> Entscheidungen treffen zu müssen. **Lies zuerst `CLAUDE.md`** (Kostenregel +
> Workflow-Regeln — sie gelten für JEDEN Schritt hier). Weiche nicht vom
> Drehbuch ab; bei Unklarheiten oder abweichenden Ist-Zuständen: **STOPP und
> den Nutzer fragen.** Jeder Schritt hat eine „Erwartete Ausgabe" — stimmt sie
> nicht, NICHT weitermachen.

---

## ✅ ENTSCHEIDUNGSKASTEN (vom Nutzer bestätigt)

| # | Entscheidung | Festlegung | Status |
|---|---|---|---|
| E1 | **Ziel-Server** | **VPS ist vorhanden** (bereits gemietet). Zugangsdaten (Host, SSH-User) trägt der Nutzer zu Beginn von Phase 2 ein. | ✅ |
| E2 | **Voice/STT auf dem Server** | **Bleibt nutzbar wie bisher** — schrittweise umgesetzt: Umschalten zunächst mit `STT_BACKEND=off` (Parität testen), **direkt danach Phase 6** aktiviert Voice. Kurze Voice-Lücke nur zwischen Phase 5 und 6. | ✅ |
| E3 | **Modell** | **Sonnet als Grundeinstellung** (per `.env` umstellbar). **Automatische Modellwahl je Aufgabe** (Haiku/Sonnet/Opus/ggf. Fable) ist als Post-Migration-Optimierung fest eingeplant → Anhang A.1. | ✅ |
| E4 | **Approval-Hub** (alle Sitzungs-Freigaben in Telegram bündeln) | **Separates Projekt NACH der Migration** (Anhang C). | ✅ |

> **Leitprinzip (Nutzer-Vorgabe):** Die Migration stellt zuerst den **heutigen
> Funktionsumfang 1:1 auf dem Server** her (Parität, inkl. Voice). Direkt
> danach wird **optimiert und verbessert** — der Verbesserungs-Backlog steht
> in Anhang A und darf nicht verloren gehen.

---

## Eiserne Regeln (gelten für das gesamte Drehbuch)

1. **💰 Kostenregel (aus CLAUDE.md):** Auth ausschließlich über den Abo-Token
   `CLAUDE_CODE_OAUTH_TOKEN`. **NIEMALS** `ANTHROPIC_API_KEY` setzen, empfehlen
   oder stehen lassen. Vor jedem Schritt, der Geld kosten könnte (Server-Miete,
   API, kostenpflichtige Dienste): **ausdrücklich warnen und fragen.**
2. **Nutzer-Workflow (aus CLAUDE.md):** Ein Schritt pro Nachricht; keine
   `#`-Kommentare in Befehlsblöcken (zsh am Mac!); bei Secrets die
   pbpaste-Reihenfolge ansagen; Secrets nie in den Chat; jede Anweisung mit
   „Erwartete Ausgabe" abschließen.
3. **Nur EINE Bot-Instanz** darf gleichzeitig mit dem Telegram-Token laufen.
   Zwei Instanzen ⇒ `Conflict: terminated by other getUpdates request` und der
   Bot antwortet unzuverlässig. Deshalb: Server erst KOMPLETT fertig bauen und
   testen (Phase 2–4), **dann** harter Umschalt-Moment (Phase 5).
4. **Rollback ist immer möglich** (Phase 7) — im Zweifel zurück auf den Mac
   schalten, nichts überstürzen.

---

## Phase 0 — Voraussetzungen (auf dem Mac, mit dem Nutzer)

### 0.1 Echte bot.py ins Repo bringen ⚠️ KRITISCH

Das GitHub-Repo enthält eine **veraltete** `bot.py` (~460 Zeilen). Die echte,
produktive Version auf dem Mac hat **~2000+ Zeilen** (Watchdog, Heartbeat,
`_wait_for_network()`, Conversation-Logs, Bot-Username-Cache …). ALLE
Code-Änderungen in Phase 1 müssen gegen die echte Version erfolgen.

Nutzer führt auf dem Mac aus (ein Block, keine Kommentare):

```bash
cd ~/Projects/claude-telegram-bot
git checkout -b mac-produktivstand
git add bot.py transcribe.py guardian.sh requirements.txt run.sh
git commit -m "Produktivstand vom Mac (bot.py, guardian, transcribe)"
git push -u origin mac-produktivstand
```

**Erwartete Ausgabe:** `* [new branch] mac-produktivstand -> mac-produktivstand`

**Plausibilitäts-Check danach (ausführendes Modell):**
`wc -l bot.py` auf dem Branch muss **> 1500** ergeben. Wenn nicht: falsche
Datei erwischt → STOPP, mit Nutzer klären.

### 0.2 Ist-Zustand-Audit der echten bot.py

Nach dem Push auf dem Branch prüfen (ausführendes Modell):

```
grep -n "Users/jakuna\|Mobile Documents\|/opt/homebrew\|iCloud" bot.py
grep -n "ANTHROPIC_API_KEY" bot.py transcribe.py
grep -n "system_prompt" bot.py
grep -n "model" bot.py | grep -i "claude\|opus\|sonnet\|option"
```

Erkenntnisse dokumentieren. Bekannt aus Logs: Conversation-Log geht nach
`~/Library/Mobile Documents/com~apple~CloudDocs/Claude-Logs/` — **existiert auf
Linux nicht** und MUSS in Phase 1.3 konfigurierbar werden.

### 0.3 Referenz-Implementierungen sichten

Auf Branch `claude/telegram-bot-auth-401-g6yqrr` liegen fertig:
- `is_auth_error()` + `AUTH_HELP` + Session-Verwurf bei 401 (bot.py)
- Abo-Token-first-Doku (README, .env.example, Plist-Beispiel)

Diese Logik wird in Phase 1.1 in die **echte** bot.py portiert (nicht kopieren
und alte Datei überschreiben — die echte Version hat eine andere Struktur!).

---

## Phase 1 — Code-Anpassungen (an der ECHTEN bot.py, auf eigenem Branch)

> Alle Änderungen auf Branch `server-migration` (von `mac-produktivstand`
> abzweigen). Nach jeder Änderung: `python -m py_compile bot.py`.
> **Backtest vor Deploy:** Der Nutzer startet den Bot einmal manuell auf dem
> Mac von diesem Branch (`./run.sh`, launchd/Guardian vorher stoppen!) und
> testet in Telegram: Textnachricht, `/status`, `/reset`, Permission-Buttons.
> Erst wenn das läuft, gilt Phase 1 als abgeschlossen. Danach Mac wieder auf
> den Produktiv-Stand zurückschalten, bis Phase 5 (Umschalten) kommt.

### 1.1 Freundliche Fehlermeldungen (401 & Co.)
Aus der Referenz portieren: `is_auth_error()`, `AUTH_HELP` (Abo-Token-first!),
und im Fehlerpfad von `process_user_text` (bzw. dem Äquivalent in der echten
Datei): bei Auth-Fehler Hinweis senden + kaputte Session verwerfen statt roher
SDK-Fehlermeldung. Gleicher Stil für weitere bekannte Fehlerklassen, sofern
die echte bot.py dort rohe Exceptions durchreicht.

### 1.2 Neutrale Begrüßung (keine Kontext-Annahmen)
Im System-Prompt der `ClaudeAgentOptions` ergänzen (Preset behalten, Zusatz
anhängen — das SDK unterstützt `{"type": "preset", "preset": "claude_code",
"append": "..."}`):

> „Du bist ein Telegram-Bot. Nimm nicht an, wo oder an welchem Gerät der
> Nutzer gerade sitzt (kein ‚schön, dich am Desktop zu sehen'). Der Nutzer
> arbeitet parallel an mehreren Geräten. Begrüßungen und Antworten neutral
> halten."

### 1.3 Alle Mac-Pfade konfigurierbar machen
Ergebnisse aus Audit 0.2 abarbeiten. Mindestens:
- **Conversation-Log-Verzeichnis** → env `CONVERSATION_LOG_DIR`
  (Default: `./logs/conversations`, Mac darf weiter iCloud nutzen via .env).
- Heartbeat-Pfad prüfen (`~/.claude/bot-heartbeat.txt` ist portabel — nur
  sicherstellen, dass das Verzeichnis angelegt wird).
- Keine `/opt/homebrew`- oder `/Users/…`-Pfade mehr hart im Code.

### 1.4 Modell per .env (Entscheidung E3)
`CLAUDE_MODEL` aus env lesen (Default laut E3, Standard: `sonnet`) und in
`ClaudeAgentOptions(model=…)` setzen. `.env.example` ergänzen.

### 1.5 Voice-Schalter (Entscheidung E2)
Nichts zu coden — die Umschaltung läuft rein über `STT_BACKEND` in der .env
(NullTranscriber liefert bei `off` bereits den Hinweis „bitte als Text").
Der Server startet in Phase 5 mit `off` (ein Fehlerfaktor weniger beim
Umschalten) und bekommt Voice **direkt danach in Phase 6** — Voice ist
Pflichtteil der Migration, keine Option. Nur `.env.example`-Kommentar prüfen.

### 1.6 Abschluss Phase 1
`py_compile` grün, Mac-Backtest laut Kasten oben bestanden, Branch gepusht.

---

## Phase 2 — Server vorbereiten (Entscheidung E1)

> Annahme: Debian 12 / Ubuntu 24.04, SSH-Zugang als root oder sudo-User.
> **Falls noch kein Server existiert: STOPP — Rücksprache (laufende Kosten!).**

```bash
sudo adduser --disabled-password --gecos "" botuser
sudo apt-get update && sudo apt-get install -y python3 python3-venv git
sudo -u botuser bash -c 'mkdir -p ~/workspace ~/.claude'
sudo -u botuser git clone https://github.com/falkogorski/claude-telegram-bot.git /home/botuser/claude-telegram-bot
cd /home/botuser/claude-telegram-bot && sudo -u botuser git checkout server-migration
sudo -u botuser python3 -m venv /home/botuser/claude-telegram-bot/.venv
sudo -u botuser /home/botuser/claude-telegram-bot/.venv/bin/pip install -r /home/botuser/claude-telegram-bot/requirements.txt
```

**Erwartete Ausgabe:** pip endet mit `Successfully installed …` (u. a.
`claude-agent-sdk`, `python-telegram-bot`). Das SDK bringt die Claude-CLI
gebündelt mit — **kein** separates Claude-Code-Install nötig.

Basics (kurz, nicht überspringen): SSH-Key-Login statt Passwort,
`ufw allow OpenSSH && ufw enable`, `unattended-upgrades` aktivieren.

---

## Phase 3 — Auth & Konfiguration auf dem Server

### 3.1 Eigenen Abo-Token für den Server erzeugen
Auf dem **Mac** (getrennt vom Mac-Token — unabhängig widerrufbar):
`claude setup-token` → Token (`sk-ant-oat…`) in die Zwischenablage.
**pbpaste-Reihenfolge beachten** (CLAUDE.md): erst Befehl einfügen, dann Token
kopieren, dann Enter. Übertragung z. B. per im-Terminal-zusammengebautem
`ssh`-Befehl — der Token darf **nie** im Chat landen.

### 3.2 EnvironmentFile anlegen (auf dem Server)

`/etc/claude-telegram-bot.env`, Rechte `600`, Besitzer root:

```
TELEGRAM_BOT_TOKEN=…
ALLOWED_USER_IDS=304455165
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat…
CLAUDE_WORKDIR=/home/botuser/workspace
CLAUDE_MODEL=sonnet
STT_BACKEND=off
CONVERSATION_LOG_DIR=/home/botuser/claude-telegram-bot/logs/conversations
VOICE_LANGUAGE=de
```

(`TELEGRAM_BOT_TOKEN` ist derselbe wie am Mac — der Bot „zieht um", behält
aber seine Identität `@jakuna_cc_bot`. `STT_BACKEND=off` ist nur der
Startzustand — wird in Phase 6 auf `whisper_cpp` umgestellt.)

**Check:** `sudo ls -l /etc/claude-telegram-bot.env` → `-rw------- 1 root root`.

### 3.3 Auth-Smoke-Test VOR dem Bot-Start

```bash
sudo -u botuser bash -c 'set -a; . /etc/claude-telegram-bot.env 2>/dev/null; set +a; /home/botuser/claude-telegram-bot/.venv/bin/python - <<PY
import anyio
from claude_agent_sdk import query, AssistantMessage, TextBlock
async def main():
    async for m in query(prompt="Sag nur: OK"):
        if isinstance(m, AssistantMessage):
            print("".join(b.text for b in m.content if isinstance(b, TextBlock)))
anyio.run(main)
PY'
```

**Erwartete Ausgabe:** `OK` (o. ä.). Bei 401 → Token prüfen, NICHT auf
API-Key ausweichen (Kostenregel!).

---

## Phase 4 — systemd-Dienst (ersetzt launchd + Guardian)

> Der Mac-Guardian (`guardian.sh` + eigenes Plist) wird auf dem Server **nicht
> nachgebaut**: `Restart=always` von systemd + der bot-interne Watchdog decken
> dieselben Fälle ab. Weniger Teile = weniger Fehlerquellen.

`/etc/systemd/system/claude-telegram-bot.service`:

```ini
[Unit]
Description=Claude Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/claude-telegram-bot
EnvironmentFile=/etc/claude-telegram-bot.env
ExecStart=/home/botuser/claude-telegram-bot/.venv/bin/python bot.py
Restart=always
RestartSec=5
StandardOutput=append:/home/botuser/claude-telegram-bot/logs/bot.out.log
StandardError=append:/home/botuser/claude-telegram-bot/logs/bot.err.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /home/botuser/claude-telegram-bot/logs && sudo chown botuser: /home/botuser/claude-telegram-bot/logs
sudo systemctl daemon-reload
sudo systemctl enable claude-telegram-bot
```

**NOCH NICHT STARTEN** — erst Phase 5 (sonst Telegram-Conflict mit dem Mac).

---

## Phase 5 — Umschalten (der einzige heikle Moment)

Reihenfolge strikt einhalten, Nutzer sitzt am Mac:

1. **Mac-Bot stoppen** (Guardian zuerst, sonst startet er ihn neu):
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.jakuna.claude-telegram-bot-guardian.plist
   launchctl unload ~/Library/LaunchAgents/com.jakuna.claude-telegram-bot.plist
   pkill -f bot.py 2>/dev/null
   pgrep -fl bot.py
   ```
   **Erwartet:** `pgrep` gibt NICHTS aus.
2. **Server-Bot starten:** `sudo systemctl start claude-telegram-bot`
3. **Verifizieren (Server):** `systemctl status claude-telegram-bot` →
   `active (running)`; `tail -n 30 …/logs/bot.err.log` → `Application started`,
   **kein** `401`, **kein** `Conflict`.
4. **Telegram-Test (Nutzer, vom Handy):** `/reset`, dann „hallo", dann eine
   kleine Tool-Aufgabe (z. B. „liste Dateien in deinem Workspace") →
   Permission-Buttons erscheinen und funktionieren.
5. **48-h-Kontrolle:** console.anthropic.com → Usage darf **nicht** steigen
   (beweist: Abo, nicht API).

---

## Phase 6 — Voice/STT auf dem Server aktivieren (Entscheidung E2)

> Direkt im Anschluss an Phase 5, sobald der Text-Betrieb stabil läuft
> (gleicher Tag ist okay — die Voice-Lücke soll kurz bleiben).

1. Pakete: `sudo apt-get install -y ffmpeg build-essential cmake git`
2. whisper.cpp bauen (als botuser):
   ```bash
   sudo -u botuser git clone https://github.com/ggerganov/whisper.cpp /home/botuser/whisper.cpp
   cd /home/botuser/whisper.cpp && sudo -u botuser cmake -B build && sudo -u botuser cmake --build build -j --config Release
   sudo ln -sf /home/botuser/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli
   whisper-cli --help | head -n 3
   ```
   **Erwartete Ausgabe:** usage-Zeilen von whisper-cli (kein „command not found").
3. Modell laden (~480 MB, dauert je nach Leitung ein paar Minuten):
   ```bash
   sudo -u botuser mkdir -p /home/botuser/claude-telegram-bot/models
   sudo -u botuser curl -L -o /home/botuser/claude-telegram-bot/models/ggml-small.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
   ls -lh /home/botuser/claude-telegram-bot/models/ggml-small.bin
   ```
   **Erwartete Ausgabe:** Dateigröße ~466M–488M.
4. `/etc/claude-telegram-bot.env` anpassen: `STT_BACKEND=whisper_cpp` und
   `WHISPER_MODEL_PATH=/home/botuser/claude-telegram-bot/models/ggml-small.bin`,
   dann `sudo systemctl restart claude-telegram-bot`.
5. **Test (Nutzer, vom Handy):** Sprachnachricht an den Bot → er echot den
   erkannten Text (`🎙️ …`) und beantwortet ihn.
   Hinweis: Auf kleinem VPS kann die Transkription 10–30 s dauern — das ist
   normal und kein Fehler. Wird es störend: größeres Modell vermeiden,
   `ggml-base.bin` (~145 MB) als schnellere Alternative testen.

---

## Phase 7 — Aufräumen (erst nach ein paar stabilen Tagen)

- Mac: Plists in einen Backup-Ordner verschieben (nicht löschen) —
  `~/Library/LaunchAgents/_deaktiviert/`.
- `main`-Branch aktualisieren: `server-migration` mergen.
- CLAUDE.md: Migrations-Status aktualisieren.
- Mac-Server-Token getrennt lassen (unabhängig widerrufbar).

---

## Phase 8 — Rollback (falls der Server zickt)

```bash
sudo systemctl stop claude-telegram-bot
```
Dann am Mac beide Plists wieder `launchctl load` (Bot zuerst, dann Guardian).
Der Mac-Stand bleibt bis Phase 7 unangetastet — Rollback dauert < 2 Minuten.

---

## Anhang A — Post-Migration-Optimierungen (Backlog, NICHT verlieren!)

> Nutzer-Vorgabe: Nach der Migration soll alles **besser** laufen als bisher.
> Diese Punkte werden nach stabiler Migration der Reihe nach angegangen —
> jeweils als eigener, kleiner Schritt mit Test.

### A.1 Automatische Modellwahl je Aufgabe (Entscheidung E3, fest eingeplant)
Der Bot soll je nach Aufgabe selbst das passende Modell wählen, statt fix auf
einem zu stehen: **Haiku** für Alltags-/Kurzanfragen, **Sonnet** als Standard,
**Opus** (bzw. **Fable**, falls im Abo verfügbar) für anspruchsvolle Aufgaben.
Umsetzungsskizze: leichtgewichtiger Router in `bot.py` — vor dem Query eine
schnelle Einstufung der Nachricht (Heuristik oder Mini-Haiku-Call), dann
`ClaudeAgentOptions(model=…)` pro Session/Anfrage setzen; Override-Befehle im
Chat (`/model opus` etc.) für manuelle Kontrolle. Kostenregel beachten: alles
bleibt im Abo — Modellwahl betrifft nur das Kontingent, nie den Geldbeutel.

### A.2 Weitere Verbesserungen (gesammelt)
- Freundliche Fehlermeldungen für weitere Fehlerklassen ausbauen (über 401
  hinaus: Netz weg, Rate-Limit/Kontingent erschöpft, Telegram-Timeouts).
- `/status` erweitern: aktives Modell, Session-Alter, Kontingent-Hinweise.
- Conversation-Logs vom Server zugänglich machen (z. B. tägliche Zusammenfassung
  per Telegram statt iCloud-Datei).
- Approval-Hub (Anhang C) als nächstes großes Projekt.

Neue Wünsche des Nutzers hier ergänzen, statt sie nur im Chat zu lassen.

## Anhang B — Mac-Dateien vom Server aus bearbeiten (optional)
Standard: Server-Workspace ist leer/eigenständig. Wer Mac-Dateien braucht:
Syncthing (bidirektional, robust) oder SSHFS (live, fragiler). Eigene
Entscheidung, nicht Teil der Migration.

## Anhang C — Approval-Hub (separates Projekt, nach Migration — Entscheidung E4)
Ziel: Permission-Anfragen **beliebiger** Claude-Sitzungen (Desktop, Web) mit
Sitzungs-Kennung in den Telegram-Bot leiten und per Button freigeben.
Skizze: kleiner HTTP-Endpoint im Bot (Server ist dann ja 24/7 erreichbar) +
pro Sitzung ein Hook/Wrapper, der `can_use_tool`-Entscheidungen dorthin
delegiert. Wird NACH stabiler Migration als eigenes Drehbuch geplant.
Bis dahin: Aufgaben über den Bot starten + „Always allow"; Web-Sitzungen über
die Claude-iPhone-App freigeben.
