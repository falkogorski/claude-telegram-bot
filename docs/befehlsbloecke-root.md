<!-- ROLLE: befehlsbloecke-root -->
# Befehlsblöcke, die root brauchen — ein Zug, drei Schritte

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** Commit-Zeit dieses Stands ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> Alles hier ist **vorbereitet und geprüft**, aber nicht ausgeführt — die
> Befehle brauchen root, und root hat nur Adam.
>
> **Reihenfolge einhalten und einzeln prüfen.** Schritt 2 nennt Skripte, die
> Schritt 3 als Zeitgeber einrichtet — die Dateien liegen bereits im Repo, also
> ist die Reihenfolge nur der Übersicht wegen fest.
>
> Die Shell ist `zsh` — **keine `#`-Kommentarzeilen** in die Blöcke einfügen,
> zsh würde sie als Befehl ausführen. Erklärungen stehen deshalb außerhalb.
>
> **Alles zusammen dauert etwa vier Minuten.** Nach jedem Schritt steht eine
> Prüfzeile; stimmt sie nicht, hör auf und sag Bescheid — der Rückweg steht
> jeweils darunter.

---

## Schritt 1 — Log-Abgleich stündlich statt täglich

Die **Tages-Einteilung der Log-Dateien bleibt unangetastet** — eine Datei je
Tag, nur häufiger hochgeschoben.

```bash
sudo sed -i 's|^OnCalendar=.*|OnCalendar=hourly|' /etc/systemd/system/claude-log-sync.timer
```

```bash
sudo systemctl daemon-reload && sudo systemctl restart claude-log-sync.timer && systemctl list-timers claude-log-sync.timer --no-pager
```

**Prüfzeile:** Die Ausgabe zeigt einen nächsten Lauf **innerhalb der nächsten
Stunde**. · **Rückweg:** dasselbe `sed` mit `*-*-* 05:10:00` statt `hourly`.

---

## Schritt 2 — Wartungsfenster an den 04:00-Neustart hängen

**Die Unit enthält gleich dreierlei** — die Ruhe-Ansage an die Stundenblumen
(damit der Neustart keinen Alarm auslöst), das Wartungsfenster (im Probelauf,
es spielt nichts ein) und den Hygiene-Neustart selbst. **Bewusst als
vollständige Datei statt über `sed`:** In der
bestehenden Zeile stecken verschachtelte Anführungszeichen; eine Ersetzung darin
ist fehleranfällig, und ein zerschossener Hygiene-Neustart wäre teuer bezahlt für
gesparte Zeilen.

**Erst sichern:**

```bash
sudo cp /etc/systemd/system/claude-bot-hygiene.service /root/claude-bot-hygiene.service.bak
```

**Dann die neue Fassung, in einem Stück einfügen:**

```bash
sudo tee /etc/systemd/system/claude-bot-hygiene.service >/dev/null <<'UNIT'
[Unit]
Description=Naechtlicher Hygiene-Neustart des Bots + Wartungsfenster (5.36)

[Service]
Type=oneshot
ExecStart=/bin/bash -lc '/usr/bin/sudo -u claudebot /home/claudebot/claude-telegram-bot/.venv/bin/python3 /home/claudebot/claude-telegram-bot/scripts/stundenblume.py --ruhe 10 || true; /usr/bin/sudo -u claudebot /home/claudebot/claude-telegram-bot/.venv/bin/python3 /home/claudebot/claude-telegram-bot/scripts/wartungsfenster.py || true; echo "[STILL]" > /home/claudebot/.claude/bot-restart-reason.txt; chown claudebot:claudebot /home/claudebot/.claude/bot-restart-reason.txt; systemctl restart claude-telegram-bot'
UNIT
```

```bash
sudo systemctl daemon-reload && systemctl cat claude-bot-hygiene.service | grep ExecStart
```

**Probe, ohne auf 04:00 zu warten** — das Fenster läuft als **Probelauf** und
spielt nichts ein:

```bash
sudo systemctl start claude-bot-hygiene.service && sleep 20 && systemctl show claude-telegram-bot -p MainPID
```

**Prüfzeile:** Eine Fenster-Meldung kommt im Telegram-Chat an, und der Bot läuft
mit einer neuen Kennung. · **Rückweg:**

```bash
sudo cp /root/claude-bot-hygiene.service.bak /etc/systemd/system/claude-bot-hygiene.service && sudo systemctl daemon-reload
```

---

## Schritt 3 — Zeitgeber für Hora und die Stundenblumen

**Hora** läuft zweimal täglich (06:30 und 18:30), die **Stundenblumen** minütlich.
Beide sind deterministisch und rufen kein Modell auf — nur Hora startet bei
Bedarf eine Arbeitssitzung, und auch die nur für das, was in seiner Liste steht.

```bash
sudo tee /etc/systemd/system/hora.service >/dev/null <<'UNIT'
[Unit]
Description=Hora - autonomer Laeufer (9.8)

[Service]
Type=oneshot
User=claudebot
WorkingDirectory=/home/claudebot/claude-telegram-bot
ExecStart=/home/claudebot/claude-telegram-bot/.venv/bin/python3 /home/claudebot/claude-telegram-bot/scripts/hora.py
UNIT
```

```bash
sudo tee /etc/systemd/system/hora.timer >/dev/null <<'UNIT'
[Unit]
Description=Hora zweimal taeglich

[Timer]
OnCalendar=*-*-* 06:30:00
OnCalendar=*-*-* 18:30:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT
```

```bash
sudo tee /etc/systemd/system/stundenblume.service >/dev/null <<'UNIT'
[Unit]
Description=Stundenblume - eine Blume der Belegkette (9.9)

[Service]
Type=oneshot
User=claudebot
WorkingDirectory=/home/claudebot/claude-telegram-bot
ExecStart=/home/claudebot/claude-telegram-bot/.venv/bin/python3 /home/claudebot/claude-telegram-bot/scripts/stundenblume.py
UNIT
```

```bash
sudo tee /etc/systemd/system/stundenblume.timer >/dev/null <<'UNIT'
[Unit]
Description=Stundenblumen minuetlich

[Timer]
OnCalendar=minutely
AccuracySec=15s
Persistent=false

[Install]
WantedBy=timers.target
UNIT
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now hora.timer stundenblume.timer && systemctl list-timers hora.timer stundenblume.timer --no-pager
```

**Prüfzeile:** Beide Zeitgeber stehen mit einem nächsten Lauf in der Liste; nach
zwei Minuten meldet `~/claude-telegram-bot/.venv/bin/python3 scripts/stundenblume.py --pruefen`
ein **„Kette lebt"**. · **Rückweg:**

```bash
sudo systemctl disable --now hora.timer stundenblume.timer
```

---

## Schritt 4 (später) — Große Dateien: eigener Bot-API-Server (5.34)

**Zurückgehalten, bis 1 bis 3 sitzen.** Die Bot-Seite ist gebaut und geprüft
(Umschalter `TELEGRAM_API_BASE`, Aufräum-Pflege mit 30-GiB-Deckel,
Deckel-Prüfung im 4-Uhr-Check, Geheimnis-Marker gesetzt). Er braucht zusätzlich
Adams `api_id`/`api_hash` von `my.telegram.org` — die gehören in eine
root-geschützte Datei und **nicht in den Chat**; den Weg dafür sage ich, wenn es
dran ist.
