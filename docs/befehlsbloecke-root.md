<!-- ROLLE: befehlsbloecke-root -->
# Befehlsblöcke, die root brauchen

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** Commit-Zeit dieses Stands ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> Alles hier ist **vorbereitet und geprüft**, aber nicht ausgeführt — die
> Befehle brauchen root, und root hat nur Adam. **Einer nach dem anderen**, nicht
> alle auf einmal: Wenn etwas hakt, soll klar sein, welcher Block es war.
>
> Die Shell ist `zsh` — **keine `#`-Kommentarzeilen** in die Blöcke einfügen,
> zsh würde sie als Befehl ausführen. Erklärungen stehen deshalb außerhalb.

---

## A — Log-Abgleich stündlich statt täglich

Die **Tages-Einteilung der Log-Dateien bleibt unangetastet** — eine Datei je
Tag, nur häufiger hochgeschoben.

```bash
sudo sed -i 's|^OnCalendar=.*|OnCalendar=hourly|' /etc/systemd/system/claude-log-sync.timer
```

```bash
sudo systemctl daemon-reload && sudo systemctl restart claude-log-sync.timer
```

```bash
systemctl list-timers claude-log-sync.timer --no-pager
```

Die letzte Zeile zeigt den nächsten Lauf. **Rückweg:** dasselbe `sed` mit
`OnCalendar=*-*-* 05:10:00` statt `hourly`.

---

## B — Wartungsfenster an den 04:00-Neustart hängen

**Bewusst über eine vollständige Unit-Datei statt über `sed`:** In der
bestehenden Zeile stecken verschachtelte Anführungszeichen; eine Ersetzung
darin ist fehleranfällig, und ein zerschossener Hygiene-Neustart wäre teuer
bezahlt für gesparte Zeilen.

**Vorher den Ist-Stand sichern:**

```bash
sudo cp /etc/systemd/system/claude-bot-hygiene.service /root/claude-bot-hygiene.service.bak
```

**Dann die neue Fassung schreiben** (ein Block, in einem Stück einfügen):

```bash
sudo tee /etc/systemd/system/claude-bot-hygiene.service >/dev/null <<'UNIT'
[Unit]
Description=Naechtlicher Hygiene-Neustart des Bots + Wartungsfenster (5.36)

[Service]
Type=oneshot
ExecStart=/bin/bash -lc '/usr/bin/sudo -u claudebot /home/claudebot/claude-telegram-bot/.venv/bin/python3 /home/claudebot/claude-telegram-bot/scripts/wartungsfenster.py || true; echo "[STILL]" > /home/claudebot/.claude/bot-restart-reason.txt; chown claudebot:claudebot /home/claudebot/.claude/bot-restart-reason.txt; systemctl restart claude-telegram-bot'
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

Danach sollte eine Fenster-Meldung im Telegram-Chat ankommen und der Bot mit
einer neuen Kennung laufen. **Rückweg:**

```bash
sudo cp /root/claude-bot-hygiene.service.bak /etc/systemd/system/claude-bot-hygiene.service && sudo systemctl daemon-reload
```

---

## C — Große Dateien: eigener Bot-API-Server (5.34)

**Zurückgehalten, bis A und B sitzen.** Die Bot-Seite ist gebaut und geprüft;
dieser Block folgt, sobald die beiden einfacheren durch sind. Er braucht
zusätzlich Adams `api_id`/`api_hash` von `my.telegram.org` — die gehören in
eine root-geschützte Datei und **nicht in den Chat**; den Weg dafür sage ich,
wenn es dran ist.

Die Vorarbeit steht: `TELEGRAM_API_BASE` als Umschalter, `api_cache_pflege.sh`
mit 30-GiB-Deckel, Deckel-Prüfung im 4-Uhr-Check, Geheimnis-Marker gesetzt.
