> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren, **zum
> Umbauauftrag von 14:21 dazu.** Adams Entscheid liegt vor (02.09., 14:2x):
> *„Zunächst Route A, später B, und ja zur CLAUDE.md-Zeile."*

# Nachtrag zum Umbauauftrag — Route A, und eine Grenze, die Claudias Papier nicht kennt

**Stichtag:** 02.09.2026, 14:26 MESZ · **Von:** Engywuck (Kontrolle)
**Gemessen an:** `scripts/mac/icloud_spiegel.sh`, `icloud_backup.sh`,
`scripts/vps_backup.sh`, `.claude/hooks/session-start.sh` @ `395de2b`
**Nenner:** 2 Entscheide · 1 Bau (Route A) · 2 Ablage-Einträge · **kein
Sicherheitspfad.**

**Ergänzt den Block um U-6 (Route A) und zwei Zeilen in U-5.** Reihenfolge
bleibt: U-1, U-2, U-3, dann U-6 — **die Ablage nützt erst, wenn das Projekt auf
dem Server liegt.**

---

# U-6 · Route A — der Abgleich über den Mac
### mittel · nach U-2 · **eine Grenze, die entscheidet, wie er gebaut wird**

**Claudias Route A, Wortlaut:** *„Der Server legt die fertigen Dateien in einen
Übergabeordner. Ein Abgleich trägt sie in den iCloud-Ordner auf dem Mac; iCloud
verteilt von dort wie gewohnt. Technisch rsync über SSH oder Syncthing,
ausgelöst vom Mac aus. Nachteil: Der Mac muss laufen."*

**Der Nachteil ist strenger, als sie ihn nennt, und das steht im Repo:**

> *„Ein LaunchAgent läuft unter `launchd` und erbt Adams iCloud-Freigabe
> nicht."* — `icloud_backup.sh`, Kopf. Der Vorgänger `com.jakuna.mirror-ki`
> lief alle fünf Minuten, **330 Läufe, alle gescheitert, drei Monate
> unbemerkt.** Deshalb dort der Entscheid: **beim Sitzungsstart und auf
> Zuruf, kein Zeitgeber** — und *ausdrücklich nicht: iCloud-Zugriff für
> `/bin/bash`.*

**Ein Zeitgeber auf dem Mac kann nicht nach iCloud schreiben.** Wer Route A
als Timer baut, baut den mirror-ki ein zweites Mal — still und wie Ruhe
aussehend. **Deshalb zwei Hälften, jede dort, wo sie laufen kann:**

### Hälfte 1 — Server → Mac-Platte, als Zeitgeber (darf)

- **Server:** Übergabeordner `~/workspace/rechnungen/ausgang/`. Der Generator
  legt Rechnung und Aufstellung dort ab. Liegt im schreibbaren Bereich.
- **Mac:** rsync über SSH nach einem **lokalen** Ordner — Ziel auf der Platte,
  nicht in iCloud. **Dafür existiert das Muster schon:** `scripts/vps_backup.sh`
  läuft täglich unter `launchd` (`com.jakuna.vps-backup.plist`) und holt
  genau so VPS-Daten nach `~/VPS-Backup/latest`. **Löst es sich von selbst:**
  prüfen, ob eine Zeile in dessen `ITEMS` reicht. Wenn der Takt zu grob ist
  (täglich), ein Geschwister mit kürzerem `StartInterval` — **gleiches Skript,
  eigener Ordner, kein zweites Verfahren.**
- **Kopieren, nie löschen** — der Grundsatz aus `icloud_spiegel.sh`. Kein
  `--delete`.

### Hälfte 2 — Mac-Platte → iCloud, unter Claude Code (muss)

- **Beim Sitzungsstart und auf Zuruf**, wie `icloud_spiegel.sh` und
  `icloud_backup.sh` — `.claude/hooks/session-start.sh` ruft beide bereits
  (Z. 36, 55). **Ein dritter Aufruf daneben**: `scripts/mac/rechnungen_ablegen.sh`,
  lokaler Übergabeordner → iCloud-Rechnungsordner, Zweig und Jahr nach dem
  Schema, das der Generator kennt (5.19: *Benennungsschema je Zweig*).
- **Neue Richtung, dieselbe Freigabe:** Die beiden vorhandenen Skripte lesen
  aus iCloud; dieses schreibt hinein. Die TCC-Freigabe gilt für Claude.app
  in beide Richtungen. **Beim ersten Lauf prüfen, nicht annehmen.**
- **Jeder Lauf schreibt eine Zeile** — auch ohne Arbeit, erst recht bei
  Scheitern. Das ist die Lehre aus mirror-ki und steht so in beiden
  Vorbildern. Der Tagescheck kann das Alter der Logdatei messen — **kein
  neuer Wächter.**

### Was das für Adam heißt — ehrlich, und es steht in meiner Nachricht an ihn

**Die Rechnung liegt in iCloud, sobald deine Sitzung das nächste Mal startet
oder Adam „ablegen" sagt** — nicht Minuten nach dem Erzeugen. Für eine
Rechnung, die am selben Tag rausgeht, reicht das; ein nächtlicher Lauf ohne
Sitzung legt nichts ab. **Genau das ist der Grund, warum Adam „später B"
gesagt hat, und er bleibt richtig.**

### Wer merkt, wenn es bricht

| Bruch | Merkt es |
|---|---|
| Hälfte 1 läuft nicht (Mac aus, SSH-Schlüssel) | Alter der ältesten Datei in `ausgang/` auf dem Server — **eine Zeile im Tagescheck**, Meldung ab einem Tag |
| Hälfte 2 läuft nicht (Freigabe fehlt) | die Klartextzeile im Log, wie bei den Vorbildern; Sitzungsstart zeigt sie |
| Datei doppelt abgelegt | rsync ohne `--delete` überschreibt nur Gleichnamiges; Rechnungsnummer ist im Namen |

**Gegenprobe:** Freigabe für den Zielordner wegnehmen → Hälfte 2 schreibt
die Scheiter-Zeile, nicht *nichts*. Vorher hinschreiben, dann messen.

---

# U-5, zwei Zeilen dazu

**A5 — „später B", als Vermerk in 5.19, nicht terminiert:**

> *Route B (rclone, direkter iCloud-Zugang vom Server) — von Adam für später
> vorgesehen. Bedingungen, wenn es so weit ist: eigene Apple-ID nur für die
> Geschäftsablage (ohne Fotos, Gerätebindung, Zahlungsmittel) · der 30-Tage-
> Ablauf des Vertrauens-Tokens wird überwacht, sonst ist B nicht abnahmefähig ·
> Bau erst nach Ultracode-Prüfstelle für die Eingangs-Absicherung (CLAUDE.md,
> Wann Ultracode — fremder Vertrauensbereich auf einem Server, der Inhalte aus
> dem Netz liest).*

**A6 — die CLAUDE.md-Zeile, von Adam bestätigt 02.09.:** Eigener Abschnitt,
mit seinem Wortlaut von 11:51 als Anlass (*„…da haben wir vielleicht an der
falschen Stelle zuerst gebaut … das ist einfach nur anstrengend"*) und
Claudias Befund von 12:25 als Messung. Die Regel:

> **Vor jeder neuen Schranke: Welche Fähigkeit schützt sie, und läuft die
> heute? Was schon einmal ging und heute nicht mehr geht, ist der dringendste
> Posten — dringender als jeder Neubau.**

**Und der Prüfer dazu, sonst ist es eine Bitte:** Teil 2 des Prüfrasters
(U-5 A3, *Arbeitsvorgänge* mit *lief zuletzt am*). Eine Regel, die auf ein
Raster zeigt, hat einen Ort, an dem sie beim Lesen greift. **Kein neuer
Wächter** — der Kurs-Blick liest das Raster ohnehin wöchentlich.

---

# Auflagen — unverändert vom Hauptpapier, plus eine

**`scripts/test_zielumgebung.sh` nach U-6** — Hälfte 1 ist ein Skript, das
unter `launchd` ohne `HOME`-Erbe läuft. Dieselbe Klasse wie der 29.07.

**Gut genug wenn:** U-6 beide Hälften gebaut, ein echter Durchlauf mit einer
Testdatei bis in den iCloud-Ordner, Scheiter-Zeile gegengeprüft, 5.19 und
CLAUDE.md nachgezogen. **Bericht mit Nenner.**
