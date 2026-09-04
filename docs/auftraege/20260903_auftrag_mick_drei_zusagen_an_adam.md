> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren, zum Nachtblock
> dazu. **Drei Zusagen an Adam von 00:3x — hier, damit sie nicht im Chat
> sterben.** Zwei kleine Bauten, eine Entscheidungsvorlage.

# Drei Zusagen an Adam — Erinnerung, Backup, Ablage auf dem Server

**Stichtag:** 03.09.2026, 00:42 MESZ · **Von:** Engywuck (Kontrolle)
**Adams Wortlaut, 03.09., 00:3x:** *„merkt ihr das aber auch bitte, dass es von
alleine aus mir kommt und nicht untergeht … wenn Du's garantieren kannst, dass
Du's so ablegst, dass es dann auch wirklich bei den nächsten Sachen mit
passiert."* — **Die Garantie ist dieses Papier.** Ein Versprechen im Chat wäre
keine.
**Nenner:** 3 Zusagen · 2 Bauten (klein) · 1 Vorlage (kein Bau) · 0 root.
**Reihenfolge:** nach Schritt 2–4 (Rechnungsprojekt), nicht davor.

---

# Z-1 · Adam erfährt, wenn Rechnungen in iCloud gelegt wurden — und wenn sie liegen bleiben
### klein · zwei Zeilen an bestehende Wege

**Adams Wortlaut:** *„wenn das nicht geschehen darf [Zeitgeber → iCloud], dann
muss er auf jeden Fall mich erinnern … sonst bringt das ja wieder alles nix."*

**Gemessen:** `rechnungen_ablegen.sh` schreibt bei jedem Lauf eine Logzeile —
**Adam liest das Log nicht.** Und wenn tagelang keine Sitzung startet, liegen
fertige Rechnungen im Ausgang, und niemand sagt es ihm.

### ① Bestätigung nach Hälfte 2 — über das Postfach, mit dem benannten Skript

Nach einem erfolgreichen Lauf mit `_tief > 0` schickt das Mac-Skript **eine**
Nachricht an Adams Chat — über den Server, mit dem Skript aus U-3:

```
ssh claudebot 'python3 /home/claudebot/claude-telegram-bot/scripts/postfach_ablegen.py --chat <Adam> --text "📁 2 Rechnung(en) nach iCloud gelegt: LiveSetup/…/Norderney"'
```

**Deterministisch, kein Modell, kein neuer Weg** — das Postfach ist der
Meldeweg, das Skript ist seit heute auf der Positivliste. Absoluter Pfad, wie
mein Doku-Befund von 15:xx verlangt. **Keine Nachricht bei null Dateien** —
sonst ist es Rauschen, und Rauschen wird abgeschaltet.

### ② Alterszeile im Tagescheck — Claudias eigener Vorschlag von heute

`daily_check.sh`, **eine Zeile**: Liegt in `~/workspace/rechnungen/ausgang/`
eine Datei **älter als 24 Stunden**, meldet der Tagescheck: *„Eine Rechnung
wartet seit N Tagen auf die Ablage — Mac-Sitzung starten oder ‚ablegen'
sagen."* Kein neuer Wächter: der Tagescheck spricht ohnehin, das ist eine
Zeile mehr. Gemessen: heute steht dort **nichts** zu `ausgang`.

**Gegenprobe:** Datei mit altem Zeitstempel in `ausgang/`, Tagescheck läuft,
Zeile erscheint; Datei weg, Zeile weg.

---

# Z-2 · Das Server-Backup sichert alles, was sich ändert — nicht eine Liste
### klein · Sicherheitsnetz · **eine echte Lücke ab morgen**

**Adams Wortlaut:** *„beim Server-Backup natürlich alle Ordner mitlaufen, die
sich verändert haben zumindest, sonst ist es ja kein vernünftiges Backup."*

**Gemessen, `scripts/vps_backup.sh` Z. 49–64:** `ITEMS` ist eine
**Aufzählung** — acht Pfade. Du hast heute `rechnungen/ausgang/` dazugesetzt,
richtig. **Aber ab morgen ist der Server die Wahrheit für das Rechnungsprojekt
— und `rechnungen/daten/` mit Stammdaten, Rechnungsdaten und dem
Nummernzähler steht nicht in der Liste.** Erzeugt Claudia 017-26, existiert
der Zähler nur auf dem VPS. Fällt der weg, ist die nächste Nummer geraten.

**Die Mengen-Regel, wörtlich aus `CLAUDE.md`:** *„Wo Abhängigkeiten nicht
erklärbar sind, werden sie gemessen statt aufgelistet."* Eine Liste von acht
Pfaden ist die Bauform, die beim neunten Ordner still versagt — heute ist es
`daten/`, nächste Woche der nächste.

**Was zu tun ist:** `~/workspace/` **als Ganzes** in das Backup, mit
Ausschlüssen statt Einschlüssen (`.venv`, `__pycache__`, `*.tmp`). Dazu
`~/postfach/` (offene Aufträge) — prüfen, ob es schon drin ist. Die acht
Einzelzeilen bleiben, was außerhalb liegt (`/etc/…`, `.claude/…`).
**`--dry-run` zuerst**, Größe ansehen, dann scharf. Eine Zeile im Bericht:
was das Backup vorher hatte, was jetzt.

**Gegenprobe:** neue Datei unter `~/workspace/irgendwas/` anlegen → nach dem
Lauf unter `~/VPS-Backup/latest/` vorhanden, ohne dass jemand eine Zeile
ergänzt hat.

---

# Z-3 · Ablage auf dem Server statt iCloud als Mitte — Entscheidungsvorlage
### kein Bau · für Adam · 💰 mitprüfen

**Adams Ziel, 00:2x:** *„alle Aufgaben … vollumfänglich ausschöpfen können,
auch wenn der Mac aus ist"* und *„Kann man die Rechnung nicht auch auf dem
Server einfach ablegen? … Und wie bekomme ich da Zugriff drauf?"*

**Das ist Claudias Route C** aus ihrem Rechnungs-Papier von heute: *„eine
eigene Ablage auf dem Server, die der Mac einbindet … löst das Problem
dauerhaft und passt zur Leitplanke dezentral und souverän."* Sie hat es
bewusst nicht für heute vorgeschlagen — richtig. **Aber Adam beschreibt genau
das, und es darf nicht wieder als Nebensatz in einem Papier liegen.**

**Vorlage schreiben, nicht bauen** — `docs/entscheidungsvorlagen/
ablage_auf_dem_server.md`, mit Gültigkeits-Kopf (Regel ⑪), höchstens zwei
Seiten:

1. **Drei Wege, je eine Zeile Nutzen und eine Zeile Preis:** eine
   Netzfreigabe vom Server (WebDAV/SFTP, Mac und iPhone binden sie ein) ·
   ein Abgleichdienst ohne Mitte (Syncthing: Server, Mac, Handy gleichen
   sich direkt ab) · eine Cloud-Oberfläche auf dem Server (Nextcloud —
   schwerer, mehr Angriffsfläche).
2. **💰 je Weg ausdrücklich:** Software quelloffen und kostenfrei, ja — aber
   **Speicher auf dem VPS, Traffic, und ob eine App auf dem iPhone Geld
   kostet**. Cent-Beträge zählen. *Unklar gilt als ja.*
3. **Sicherheit, und das entscheidet:** Jeder dieser Wege ist **ein Dienst
   nach außen auf dem Server** — der erste, der Adams Geschäftsdaten trägt.
   Nach `CLAUDE.md`, *Wann Ultracode*: **„vor jeder weiteren Anbindung
   fremder Datenquellen … wenn dafür neue Schrankenlogik entsteht."** Hier
   entsteht sie. Die Vorlage nennt die Prüfstelle, sie umgeht sie nicht.
4. **Was mit iCloud geschieht:** bleibt die Sicht des Macs, wird nicht
   abgeschafft — der Mac bindet die Server-Ablage zusätzlich ein. Route A
   wird dann überflüssig, nicht kaputt.
5. **Empfehlung mit Begründung**, eine Zeile. Meine Neigung: der einfachste
   Weg, der ohne Apple-Passwort und ohne Web-Oberfläche auskommt — das ist
   vermutlich die Netzfreigabe. **Aber gemessen, nicht geneigt.**

**Adams Entscheid steht dann als Frage mit Wirkung im Freigabe-Postfach**, nicht
als Chatfrage. Bis dahin gilt für morgen: Rechnung über Claudia in den Chat,
Ablage über Route A, Nummern auf dem Server.

---

# Und eine Regel, die ab 017-26 gilt — bitte in 5.19 und `ABHAENGIGKEITEN.md`

> **Der Server ist ab dem 03.09.2026 die Stelle für Rechnungsnummern.** Die
> Mac-Kopie von `~/Projects/rechnungen` erzeugt keine Rechnungen mehr; sie ist
> Vorlage und Rückweg. Zwei Zähler wären irgendwann eine Nummer doppelt.

Gegenprobe dafür gibt es nicht — es ist eine Regel für Adam und für Claudia,
kein Verhalten. Deshalb steht sie an zwei Stellen und im Begrüßungstext des
Bots (`last-task`, den du heute Nacht als sechs Wochen alt gemessen hast —
**dort gehört sie hin, das ist der nutzerseitige Text**).

---

# Auflagen — wie im Nachtblock

Regressionslauf vor jedem Commit · Zielumgebung nach Z-2 (Backup läuft unter
`launchd`) · Heredoc-Commits · `ABHAENGIGKEITEN.md` · Blaupause-Zeile je Bau ·
**Bericht mit Nenner: drei von drei, oder welche fehlt** · nichts deployen.
