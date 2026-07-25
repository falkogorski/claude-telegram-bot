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

## Schritt 4 — Arbeitsspeicher absichern (C1) · **vor der Abreise**

**Warum das dazugekommen ist:** Die Messung am 25.07. ergab Spitzenwerte von
zusammen **7,53 GiB bei 7,75 GiB vorhanden** — und **keinen Swap**. Ohne
Auslagerung hat der Kernel bei Speichermangel nur den OOM-Killer; mit Swap wird
dieselbe Lage langsam statt tödlich. Einzelheiten:
`docs/entscheidungsvorlagen/arbeitsspeicher-messung-c1.md`.

**4a — Auslagerungsdatei anlegen (4 GiB, dauerhaft):**

```bash
sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

```bash
grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

```bash
free -m | head -3 && swapon --show
```

**Prüfzeile:** `swapon --show` nennt `/swapfile` mit 4 GiB, und `free -m` zeigt
eine Swap-Zeile ungleich null. · **Rückweg:**

```bash
sudo swapoff /swapfile && sudo sed -i '/^\/swapfile/d' /etc/fstab && sudo rm -f /swapfile
```

**4a-2 — Die Bremse dazu: Swap als Netz, nicht als Ausweichfläche.**
Standardmäßig lagert Linux schon aus, wenn noch Speicher frei ist. Das wollen
wir hier ausdrücklich **nicht**: Der Swap soll den Notfall abfangen, nicht den
Alltag verlangsamen — sonst hätten wir ein Tempo-Problem gegen ein
Speicher-Problem getauscht.

```bash
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf && sudo sysctl --system | tail -3
```

```bash
cat /proc/sys/vm/swappiness
```

**Prüfzeile:** Die Ausgabe lautet `10`. · **Rückweg:**

```bash
sudo rm -f /etc/sysctl.d/99-swappiness.conf && sudo sysctl -w vm.swappiness=60
```

**4b — Ollama für die Abwesenheit anhalten** (fünf GiB Spitze frei, null Euro;
es ist ein Fallback, den in Adams Abwesenheit ohnehin niemand bediente):

```bash
sudo systemctl disable --now ollama && systemctl is-active ollama
```

**Prüfzeile:** Die Ausgabe lautet `inactive`. · **Rückweg (nach der Rückkehr):**

```bash
sudo systemctl enable --now ollama
```

> ⚠️ **Fußnote zu 4b — die Nebenwirkung, die man leicht übersieht.** Die
> Neben-Inferenzen (Kapitel-Labels beim Vorlesen, 2.6) gehen über LiteLLM auf
> `127.0.0.1:4000` und von dort an Ollama. Hält man **nur** Ollama an, nimmt
> LiteLLM die Anfrage weiterhin an, und der Bot wartet **bis zu 90 Sekunden**,
> bevor er still auf „kein Label" zurückfällt — und zwar **je Abschnitt**. Der
> stille Rückfall ist richtig; die 90 Sekunden Bedenkzeit sind es nicht.
> Deshalb LiteLLM im selben Zug mit anhalten:
>
> ```bash
> sudo systemctl disable --now litellm && systemctl is-active litellm
> ```
>
> **Prüfzeile:** `inactive`; das Vorlesen läuft weiter, nur ohne Kapitel-Labels.
> · **Rückweg:** `sudo systemctl enable --now litellm`

---

## Schritt 4c — Webhook-Port auf Telegrams Netze beschränken (1.9 C.1)

**Gefunden in der Nacht zum 26.07. beim Bau der Härtungsprüfung.** Der Webhook
läuft, und Port **8443 ist von jeder Adresse der Welt erreichbar** — das habe
ich von hier aus nachgemessen, nicht vermutet.

**Zur Einordnung, ohne Dramatik:** Zwei der drei roten Auflagen greifen bereits,
und zwar hart — der Bot **startet nicht**, wenn Geheimnis-Token oder
unerratbarer Pfad fehlen. Ein fremder Ruf auf den Port wird ohne den richtigen
Kopfzeilen-Wert verworfen. Dass der Port auf allen Adressen lauscht, ist bei
der Self-Signed-Betriebsart **so vorgesehen** (Telegram muss ihn ja erreichen);
die „nur 127.0.0.1"-Auflage gilt der Reverse-Proxy-Variante.

**Was fehlt, ist die dritte Auflage:** die Beschränkung auf Telegrams Netze.
Sie nimmt die Angriffsfläche von „die ganze Welt darf klopfen" auf „nur Telegram
darf klopfen" — der Unterschied zwischen einem Schloss und einem Schloss hinter
einer Tür.

```bash
sudo ufw allow from 149.154.160.0/20 to any port 8443 proto tcp && sudo ufw allow from 91.108.4.0/22 to any port 8443 proto tcp
```

```bash
sudo ufw delete allow 8443/tcp 2>/dev/null; sudo ufw status numbered | grep 8443
```

**Prüfzeile:** In der Liste stehen **zwei** Regeln für 8443, beide mit einer
Herkunft (`149.154.160.0/20` bzw. `91.108.4.0/22`) — und **keine** ohne. Danach
muss der Bot weiter antworten: Schick ihm eine Nachricht, sie muss ankommen.

> ⚠️ **Wenn keine Antwort mehr kommt, sofort den Rückweg gehen** — ein Bot, der
> vierzehn Tage keine Nachrichten annimmt, ist teurer als der Gewinn dieser
> Regel. **Rückweg:**
>
> ```bash
> sudo ufw allow 8443/tcp && sudo ufw status | grep 8443
> ```
>
> **Deshalb dieser Schritt bewusst NICHT am Abreisetag**, sondern wenn Adam
> danach noch eine Weile am Rechner sitzt und es merken würde.

---

## Schritt 5 (später) — Große Dateien: eigener Bot-API-Server (5.34)

**Zurückgehalten, bis 1 bis 3 sitzen.** Die Bot-Seite ist gebaut und geprüft
(Umschalter `TELEGRAM_API_BASE`, Aufräum-Pflege mit 30-GiB-Deckel,
Deckel-Prüfung im 4-Uhr-Check, Geheimnis-Marker gesetzt). Er braucht zusätzlich
Adams `api_id`/`api_hash` von `my.telegram.org` — die gehören in eine
root-geschützte Datei und **nicht in den Chat**; den Weg dafür sage ich, wenn es
dran ist.
