# Claude Telegram Bot

Telegram-Bridge für Claude Code / Agent SDK. Jeder Telegram-User bekommt eine
persistente Claude-Session; Permission-Requests werden als Inline-Buttons
zurückgespiegelt (Allow / Deny / Always allow).

**Zweck:** Vom iPhone aus Claude-Code-Sessions starten, weiterführen und
Permission-Prompts bestätigen — ohne am Mac zu sitzen.

---

## Quick Start

### 1. Bot bei BotFather anlegen

1. Telegram öffnen, `@BotFather` suchen
2. `/newbot` schicken, Namen vergeben (z. B. „Mein Claude Bot")
3. Username vergeben (muss auf `bot` enden, z. B. `meinclaude_bot`)
4. **Token kopieren** — sieht aus wie `1234567890:ABCdef…`

### 2. `.env` füllen

```bash
cd ~/Projects/claude-telegram-bot
cp .env.example .env
# .env in deinem Editor öffnen und TELEGRAM_BOT_TOKEN eintragen
# ALLOWED_USER_IDS erstmal mit Dummy `1` füllen — echte ID kommt gleich
```

### 3. Eigene User-ID herausfinden

```bash
./run.sh
```

In Telegram dem Bot `/whoami` schicken — er antwortet mit deiner User-ID.
Bot stoppen (Strg-C), die ID in `.env` unter `ALLOWED_USER_IDS` eintragen
(Dummy `1` ersetzen oder mit Komma anhängen), Bot neu starten.

### 4. Loslegen

In Telegram eine Nachricht an den Bot schicken — z. B.:

> Lies den Inhalt von ~/Documents/Aufräum-Logs und fass die letzten 5 Einträge zusammen

Sobald Claude ein Tool nutzen will (Read, Bash, Edit, …), erscheint ein
Permission-Prompt mit drei Buttons.

---

## Sicherheit

**Der Bot führt Code auf deinem Mac aus.** Wer den Bot ansprechen darf, kann
über Claude beliebige Dateien lesen/schreiben und Shell-Befehle ausführen.

- `ALLOWED_USER_IDS` ist **kein optionales** Feature. Ohne Eintrag startet der
  Bot nicht (SystemExit).
- Trag *nur deine eigene* Telegram-User-ID ein. Nie Freunde, nie öffentliche IDs.
- Den Bot-Token nicht ins Git, nicht in Screenshots, nicht in Pastebins. Falls
  geleakt: bei BotFather `/revoke` + neuen Token holen.
- `bot.py` lehnt jede Nachricht von nicht-whitelisteten Usern ab und loggt sie.

---

## Commands

| Befehl | Wirkung |
|---|---|
| `/start` | Begrüßung, zeigt Workdir und Befehlsliste |
| `/whoami` | Zeigt deine Telegram-User-ID + ob du auf der Whitelist bist |
| `/status` | Aktive Session? Welche Tools auf „Always allow"? |
| `/reset` | Beendet die laufende Claude-Session. Nächste Nachricht startet eine neue. |

---

## Permission-Flow

Wenn Claude während einer Antwort ein Tool nutzen will (z. B. `Bash`,
`Read`, `Edit`), sendet der Bot eine Nachricht wie:

> 🔐 **Permission request**
>
> **Bash**
> ```
> ls -la ~/Documents/Aufräum-Logs
> ```
>
> [✅ Allow] [❌ Deny]
> [🔓 Always allow Bash]

- **Allow** — einmalig erlauben.
- **Deny** — Tool wird nicht ausgeführt, Claude wird informiert.
- **Always allow `<Tool>`** — für den Rest dieser Session ohne Rückfrage.
  Wird **nicht** auf Disk persistiert; nach `/reset` oder Bot-Neustart wieder
  gefragt. (Bewusst so im MVP — soll vermeiden, dass eine versehentliche
  „Always Bash"-Klickorgie dauerhaft hängt.)

**Timeout:** 10 Minuten ohne Klick → automatisch „Deny".

---

## launchd-Autostart (optional)

Damit der Bot beim Login automatisch startet:

```bash
# Logs-Ordner anlegen
mkdir -p ~/Projects/claude-telegram-bot/logs

# Plist-Vorlage kopieren
cp ~/Projects/claude-telegram-bot/com.user.claude-telegram-bot.plist.example \
   ~/Library/LaunchAgents/com.user.claude-telegram-bot.plist

# In der kopierten Datei den Platzhalter `__HIER_DEINEN_KEY__` durch den echten
# ANTHROPIC_API_KEY ersetzen (Wert aus `env | grep ANTHROPIC` übernehmen).
# Falls du auch ANTHROPIC_BASE_URL nutzt, den auskommentierten Block aktivieren.

# Laden + starten
launchctl load ~/Library/LaunchAgents/com.user.claude-telegram-bot.plist

# Status prüfen
launchctl list | grep claude-telegram-bot

# Logs lesen
tail -f ~/Projects/claude-telegram-bot/logs/bot.out.log
```

Zum Stoppen / Entladen:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.claude-telegram-bot.plist
```

**Wichtig:** launchd-Sessions erben die Shell-Env **nicht** — `ANTHROPIC_API_KEY`
(und ggf. `ANTHROPIC_BASE_URL`) müssen im Plist explizit unter
`EnvironmentVariables` stehen, sonst startet der SDK-Subprozess ohne Credentials.

---

## VPS-Migration (später)

Wenn der Mac nicht 24/7 läuft, ist ein VPS oder Raspberry Pi sinnvoll. Dafür
braucht's:

1. **Python 3.10+** und `pip install -r requirements.txt` auf dem Host.
2. **`ANTHROPIC_API_KEY`** (gleicher Key wie lokal).
3. **`CLAUDE_WORKDIR`** auf einen Pfad auf dem Server zeigen lassen — nicht
   automatisch dein Mac-Home. Optional: SSHFS/Syncthing wenn du Mac-Dateien
   bearbeiten willst.
4. **systemd-Unit** statt launchd-Plist (Linux).
5. **Sicherheit:** SSH absichern, Bot-Service als unprivilegierter User laufen
   lassen.

Code selbst ist plattformunabhängig — nur `run.sh`, Plist und Workdir-Logik
ändern sich.

---

## Troubleshooting

**Bot startet sofort wieder mit „ALLOWED_USER_IDS env var is empty"**
→ `.env` nicht gefunden oder Variable wirklich leer. Prüfen:
```bash
cd ~/Projects/claude-telegram-bot && grep ALLOWED_USER_IDS .env
```

**Bot startet, antwortet aber nicht auf Nachrichten**
→ Du bist nicht auf der Whitelist. Bot-Logs zeigen
`rejected message from user_id=…`. Diese ID in `.env` eintragen.

**„Connection refused" / „401" / „403" beim Tool-Use**
→ `ANTHROPIC_API_KEY` fehlt oder ist ungültig im Bot-Prozess. Bei launchd:
Plist anpassen (siehe oben).

**Permission-Buttons reagieren nicht**
→ Telegram-Callback-Query schlägt fehl. Logs prüfen, ggf. Bot neustarten. Kann
auftreten wenn der Bot zwischen Senden und Klick neugestartet wurde — Future
ist dann weg.

**„Vorherige Aufgabe läuft noch — bitte warten"**
→ Per-User-Lock ist aktiv. Wenn Claude hängt: `/reset` schickt die Session weg
und löst den Lock.

**launchd-Bot crasht ständig**
→ `~/Projects/claude-telegram-bot/logs/bot.err.log` lesen. Oft fehlende
Env-Var oder fehlgeschlagener venv-Pfad.

---

## Dateien

| Datei | Zweck |
|---|---|
| `bot.py` | Hauptbot — Handlers, Session-Mgmt, Permission-Callback |
| `requirements.txt` | Pinned Deps |
| `.env.example` | Template — nach `.env` kopieren und füllen |
| `.gitignore` | Schließt `.env`, `.venv`, Logs aus |
| `run.sh` | Convenience-Wrapper für den Bot-Start aus dem venv |
| `com.user.claude-telegram-bot.plist.example` | launchd-Vorlage |
| `README.md` | Du bist hier. |
