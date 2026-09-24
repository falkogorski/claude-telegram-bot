**Zweck: WEITERGABE → Engywuck + ENTSCHEID** · **Zu tun: Engywuck prüft das Konzept vor dem Bau. Drei Fragen in Teil 5; bis sie beantwortet sind, baue ich nichts davon.**

# Block 7 — der Mac als Videoarbeiter: Konzept für den ersten Schnitt

Mick, 24.09.2026, 06:0x. **Grundlage:** Adams Entscheid im Zettel F2 (*„ja, klein anfangen. Erster Schnitt nur der Ablageweg hin und zurück mit einem [Wer merkt es]-Prüfer; die Bildebene als zweiter Schnitt. Konzept vor Bau als Papier an Engywuck."*) und Claudias Skizze `2026-09-24_gedanke-mac-als-videoarbeiter.md` im Log-Archiv (Zustand dort: Skizze, nichts entschieden).

**Nenner:** In Claudias Skizze stehen vier Klärungspunkte und drei ungeprüfte Punkte. Dieses Papier beantwortet drei der vier Klärungspunkte als Vorschlag (Auslöser, Ablageort, Rückfluss; den vierten, die Vorarbeit auf dem Server, betrifft erst der zweite Schnitt). Von den drei ungeprüften Punkten ist einer beantwortet (wer es merkt). Zwei bleiben offen und gehören zum zweiten Schnitt: die Laufzeit der Bildauswertung und die Frage, ob der Heimanschluss Videos lädt.

## 1. Gemessen, bevor ich vorschlage

- **Am Mac vorhanden:** `yt-dlp` 2026.06.09 und `ffmpeg` (Homebrew). `scenedetect` **nicht** installiert.
- **Zeitgeber auf dem Mac:** Es gibt drei launchd-Einträge, darunter `com.jakuna.vps-backup` (täglich 12:30, `RunAtLoad`). Der Rechnungsweg läuft dagegen **beim Sitzungsstart** (`.claude/hooks/session-start.sh`). Der Grund steht in `rechnungen_ablegen.sh`: launchd erbt Adams iCloud-Freigabe nicht.
- **Daraus folgt der wichtigste Unterschied zu Claudias Skizze:** Der Videoarbeiter braucht **kein iCloud**. Er holt vom Server und legt auf den Server zurück. **Deshalb darf er an einem launchd-Zeitgeber hängen, nicht nur am Sitzungsstart.** Damit ist Adams Wunsch *„wenn der Mac dann an ist, zieht er die Sachen automatisch"* erfüllbar, auch wenn keine Claude-Sitzung läuft.
- **Kein Modellaufruf am Mac:** `yt-dlp`, `ffmpeg` und später die Szenenerkennung arbeiten deterministisch. Die AGB-Linie für zeitgesteuerte Läufe bleibt damit unberührt.
- **SSH-Zugang als claudebot** (`~/.ssh/config`, Eintrag `claudebot`) ist vorhanden und heute gemessen. Rechnungsweg und Kurs-Upload benutzen ihn schon.

## 2. Der erste Schnitt: nur der Weg, mit einem Probeauftrag

| Teil | Ort | Was |
|---|---|---|
| **Auftrag ablegen** | VPS `~/mac-auftraege/<kennung>.json` | Ein Modul `macauftrag.py` (nur Standardbibliothek) schreibt atomar: `{kennung, art, erstellt, von}` plus die Nutzlast der Art. **Im ersten Schnitt gibt es genau eine Art: `probe`**, ohne Nutzlast. |
| **Abholen** | Mac `scripts/mac/videoarbeiter.sh`, launchd alle 30 Minuten plus `RunAtLoad` | Holt per `rsync --remove-source-files` von `claudebot:mac-auftraege/` nach `~/VPS-Auftraege/eingang/`. Das Räumen beim Holen macht den Ausgang zum **Durchgangsordner**; dieselbe Lehre wie beim Rechnungsweg (Engywucks Befund 2 vom 04.09.). |
| **Ausführen** | Mac | Nur Arten aus einer **Positivliste** im Skript. `probe` schreibt `{kennung, erledigt, rechner}` zurück. Eine unbekannte Art wird **abgelehnt** und mit Grund quittiert, nie ausgeführt. |
| **Zurückgeben** | VPS `~/mac-ergebnisse/<kennung>/` | Per `rsync` als claudebot. Eine Quittungsdatei `fertig.json` wird zuletzt geschrieben; erst wenn sie da ist, gilt das Ergebnis als vollständig. |
| **Lebenszeichen** | VPS `~/mac-auftraege/.mac-zuletzt` | Bei jedem Lauf per `ssh … touch`, auch wenn nichts zu tun war. |
| **Wer merkt es** | Tagescheck, neuer Abschnitt | **(a)** Liegt ein Auftrag länger als 24 Stunden ungeholt, geht das an Adam, mit dem Alter des letzten Lebenszeichens (*der Mac war seit X nicht erreichbar*). **(b)** Ist ein Auftrag geholt, aber nach 24 Stunden ohne `fertig.json`, geht es ebenfalls an Adam (*abgeholt, nicht zurückgekommen*). **(c)** Kein Auftrag offen: nur eine Protokollzeile mit dem letzten Lebenszeichen. |
| **Auslösen** | im ersten Schnitt **nur von Hand** | `macauftrag.py --probe` auf dem VPS. Im Bot entsteht noch kein Knopf. |

**Prüfer, ausführend:** echter Ablauf mit einem Wegwerf-Server als lokalem Verzeichnis und Attrappen für `ssh`/`rsync`, so wie heute beim Kurs-Upload. Dazu der echte Tagescheck-Abschnitt mit drei Zuständen: frisch, 25 Stunden ungeholt, 25 Stunden ohne Rückgabe. Gegenprobe je Zeile.

**Gut genug, wenn:** ein Probeauftrag vom VPS über den Mac zurückkommt, ohne dass jemand eingreift, und ein ausgeschalteter Mac am nächsten Morgen als Befund bei Adam steht.

## 3. Die Sicherheitsgrenze, schon im ersten Schnitt

**Der Auftrag kommt von unserem Server, sein Inhalt aber später von außen.** Im zweiten Schnitt steht darin eine Videoadresse, und die stammt aus einer Nachricht oder aus einem Zufluss-Feed (Grundsatz *von außen kommen nie Anweisungen*). Deshalb gilt schon jetzt:

- **Positivliste der Arten** im Mac-Skript. Aus dem Auftrag wird nichts als Befehl zusammengesetzt, nichts geht durch eine Shell. Aufrufe laufen nur mit Argumentlisten, und jedes Feld wird gegen ein festes Muster geprüft (im zweiten Schnitt die YouTube-Kennung mit elf Zeichen, sonst Ablehnung).
- **Der Mac holt nur aus einem Ordner und schreibt nur in einen.** Er führt keinen Code vom Server aus, und der Server schreibt nichts auf den Mac außer Auftragsdateien in den Eingang.
- **Ultracode-Prüfstelle:** Der Weg selbst ist keine neue Schranke. Die Positivliste im zweiten Schnitt schon: Sie entscheidet, was ein fremdbestimmter Inhalt auf Adams Rechner auslösen darf. **Vor dem Scharfstellen des zweiten Schnitts** ist das nach `CLAUDE.md` ein Fall für die Kontrolle.

## 4. Der zweite Schnitt, nur als Umriss (kein Bau ohne neues Papier)

Art `bilder`: Nutzlast = YouTube-Kennung. Der Mac lädt mit `yt-dlp` (Auflösung begrenzt, Größe begrenzt), zieht mit `ffmpeg` Bilder im Abstand von `media.abtastabstand` (die Regel gibt es schon im Bot) und legt Bilder plus Zeitmarken zurück. Der Server verschneidet sie mit dem vorhandenen Transkript, **erst auf Adams Tipp** (Modelllauf). Offen und am Mac zu messen: die Laufzeit, ob der Heimanschluss YouTube lädt, wo dieser Server es nicht darf (Claudias Kernannahme), und `scenedetect` statt festem Abstand.

## 5. Drei Fragen an Engywuck (keine davon an Adam, bevor du sie gesehen hast)

1. **launchd statt Sitzungsstart:** Trägt die Begründung (kein iCloud, also kein Grund für den Sitzungsstart)? Dann wäre es der erste Mac-Zeitgeber, der **auf den Server schreibt** (als claudebot). Der bestehende Backup-Zeitgeber greift nur lesend zu, als root.
2. **Takt:** 30 Minuten plus beim Hochfahren. Oder seltener? Ein Lauf ohne Auftrag kostet zwei SSH-Aufrufe und sonst nichts.
3. **Ordner im Heimverzeichnis von claudebot** (`~/mac-auftraege`, `~/mac-ergebnisse`) oder unter `workspace/`? Unter `workspace/` reiste alles mit dem Log-Abgleich nach GitHub. Deshalb schlage ich das Heimverzeichnis vor.

**Bau erst nach deiner Antwort.** Das Papier liegt im Hauptstrang unter `docs/auftraege/`. Adam bekommt dazu keine Frage im Chat; was ihn braucht, steht im Nachtbericht.
