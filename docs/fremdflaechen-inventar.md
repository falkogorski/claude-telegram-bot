<!-- ROLLE: fremdflaechen-inventar -->
# Fremdflächen — was das System beeinflusst und in keinem Repo steht

> **Zweck: ABLAGE** · **Zu tun:** nichts — dies ist das Gedächtnis für Orte,
> die kein Prüfer sieht.

**Angelegt 10.09.2026 auf Connis Auftrag**, nach einem Vorfall, der genau
diese Lücke zeigte.

## Was hier hineingehört

Eine **Fremdfläche** ist ein Ort außerhalb beider Repos, an dem eine Änderung
das Verhalten des Systems verändert — **ohne dass ein Regressionslauf, ein
Selbstcheck oder ein Wächter davon erfährt.** Sie ist nicht falsch und nicht
verboten; sie ist unsichtbar, und das ist das Problem.

Der Prüfstein: *Könnte jemand hier etwas ändern, ohne dass irgendein Prüfer
dieses Projekts anschlägt?* Wenn ja, gehört der Ort hier hinein.

---

## 1 · macOS-Anmeldeobjekte und Hintergrundschalter `[10.09.2026]`

**Der Ort:** Systemeinstellungen → „Allgemein" → „Anmeldeobjekte &
Erweiterungen". Dort erscheint **jeder** `LaunchAgent` aus
`~/Library/LaunchAgents` als Schalter. Für Agenten, die `/bin/bash` starten,
zeigt macOS nur **„bash"** an — ohne Angabe, wozu er gehört.

**Der Vorfall:** Adam hat die bash-Einträge deaktiviert, weil sie
undurchsichtig aussahen. Das ist eine vernünftige Vorsichtsreaktion auf eine
Anzeige, die nichts erklärt.

**Was daran gefährlich ist:** Einer dieser Schalter trägt
`com.jakuna.vps-backup` — die tägliche Sicherung des Servers auf den Mac.
Wird er abgeschaltet, **läuft kein Backup mehr, und nichts meldet es.** Der
Bot weiß davon nichts, der Tagescheck läuft auf dem Server, und die Sicherung
schweigt genauso, wenn sie nicht läuft, wie wenn sie erfolgreich ist.

### Gemessen am 10.09.2026, 22:39

**Das Backup ist NICHT ausgefallen** — und das ist eine Berichtigung, keine
Bestätigung:

| Frage | Ergebnis |
|---|---|
| `com.jakuna.vps-backup` geladen? | ja, Status 0 |
| heute gelaufen? | **zweimal** — 12:30:05 und 22:35:38, je 182 MB |
| Lücke in den Tagen davor? | **keine** — 01.09. bis 09.09. je ein Lauf |
| frische Dateien in `latest/`? | 17 vom 10.09. |

Der Ordner `latest/` trägt selbst den 07.09. als Zeitstempel — **das ist kein
Befund:** Der mtime eines Ordners ändert sich nur, wenn Einträge auf seiner
obersten Ebene dazukommen, nicht wenn Dateien darin neu geschrieben werden.
Wer nur darauf sieht, hält ein laufendes Backup für tot.

**Die Gefahr war real, eingetreten ist sie nicht.** Beides gehört in denselben
Satz, sonst wird aus einer Vorsichtsmaßnahme rückwirkend ein Beinahe-Unfall,
den es nicht gab.

### Der zweite bash-Agent — und es war keiner der beiden vermuteten

Gesucht war `icloud-spiegel-bot` (am 29.08. ausgetragen) oder `mirror-ki`
(seit Mai tot). Beide lagen bereits in `_deaktiviert/`. Der Schalter kam von
einem **dritten**: `com.jakuna.mirror-ki-reboot-test` — ein Einmal-Testskript
vom 25.05., das beim Anmelden startet. Beim Austragen von `mirror-ki` am 29.08.
ist es übrig geblieben, weil es einen eigenen Namen trägt.

Seine Logdateien sind seit dem 25.05. **leer und unverändert**: Es lief, tat
nichts (Marker-Datei), und niemand sah hin.

**Ausgetragen am 10.09.2026:** `launchctl bootout` (rc=0), dann nach
`_deaktiviert/com.jakuna.mirror-ki-reboot-test.plist.ausgetragen-2026-09-10`
— dieselbe Form wie am 29.08. **Damit ist `com.jakuna.vps-backup` der einzige
verbliebene bash-Agent**, und der Schalter in Adams Einstellungen hat nur noch
eine Bedeutung.

### Die Lehre, die über den Fall hinausgeht

**Ein Name, der nichts sagt, wird abgeschaltet.** Das ist kein Fehler des
Menschen, sondern eine Eigenschaft der Anzeige. Daraus zwei Griffe:

- **Beim Anlegen eines LaunchAgents mitfragen: Wie heißt er in den
  Einstellungen?** Ein Agent, der dort als nacktes „bash" erscheint, ist ein
  Kandidat fürs Abschalten.
- **Beim Austragen einer Automatik alle Geschwister suchen**, nicht nur den
  Hauptnamen. `mirror-ki` wurde ausgetragen, `mirror-ki-reboot-test` blieb —
  dieselbe Klasse wie die Geschwister-Regel im Code.

### Nebenbefund, nicht beauftragt

`launchctl list` zeigt zwei Agenten mit Fehlerstatus:
`com.jakuna.sort-downloads` (**78**) und `com.jakuna.claude-remote-hub`
(**1**). Beide sind nicht Teil dieses Projekts; der Status sagt nur, dass ihr
letzter Lauf so endete. **Hier notiert, nicht angefasst** — wer fremde
Automatik ohne Auftrag repariert, verändert etwas, das ein anderer gebaut hat.

---

## 2 · Unerklärte Löschung im Arbeitsbaum `[23.09.2026, Ursache OFFEN]`

**Gemessen am 23.09.2026, 14:04**, beim ersten Zug nach Adams Rückkehr: Der
ganze Ordner `docs/entscheidungsvorlagen/` fehlte im Arbeitsbaum — **21
Dateien**, gelöscht, aber **nicht committet** und nirgends sonst abgelegt.
Adam: *„keine Absicht"*. Aus git wiederhergestellt (`git restore`),
zeichengleich mit dem letzten Stand.

**Warum es trotzdem hier steht:** Hätte jemand in diesem Zustand
`git commit -a` ausgeführt, wären die Dateien aus dem Repo verschwunden, und 22
Dateien — `CLAUDE.md` allein fünfmal — hätten ins Leere gezeigt. **Der Schaden
war einen Befehl entfernt, und nichts hätte gewarnt.**

**Ausgeschlossen, gemessen:**
- Kein Skript und kein Hook im Repo löscht oder verschiebt diesen Ordner
  (`grep` über `scripts/` und `.claude/hooks/`).
- Keine Sitzung hat committet: `origin` und der lokale Stand waren gleich,
  seit dem 11.09. kein neuer Commit.
- Der Mac-Job `com.jakuna.sort-downloads` führt in seinen Logs den Ordner
  nirgends (`~/Documents/Aufräum-Logs/`).

**Nicht ausgeschlossen:** eine andere Claude-Sitzung ohne Commit, ein Werkzeug
mit Aufräum-Funktion, eine Handbewegung im Finder. Ein Anhaltspunkt: Der
Nachbarordner `docs/auftraege` wurde am **15.09. um 02:27** verändert, während
Adam unterwegs war und keine Bau-Sitzung lief.

**Der Griff, der daraus folgt:** Beim ersten Zug nach einer Pause
`git status` lesen, bevor gebaut wird. Eine Liste gelöschter Dateien, die man
nicht selbst gelöscht hat, ist kein Aufräumen — sie ist ein Befund.

### Engywucks Hypothese gemessen — iCloud-Auslagerung: **widerlegt** `[23.09., 14:3x]`

Engywuck vermutete, iCloud habe den Ordner ausgelagert statt gelöscht. Vier
Messungen, keine trifft:

| Messung | Ergebnis |
|---|---|
| Liegt das Repo im iCloud-Bereich? | **Nein.** `~/Projects/claude-telegram-bot`, echtes Verzeichnis, kein Symlink |
| „Mac-Speicher optimieren" | **aus** (`optimize-storage = 0`) — iCloud lagert nichts aus |
| `.icloud`-Platzhalter im Baum | **keiner** |
| `git stash` · `git reflog` | leer · **kein Eintrag** zwischen 11.09., 11:29 und 23.09., 14:22 |

Der Reflog schließt dabei nur Git-Befehle aus, die einen Verweis bewegen
(`checkout`, `reset`, `commit`). Ein schlichtes Löschen ohne Git sieht er
nicht — und die Löschungen waren **nicht vorgemerkt** (` D`, nicht `D `), also
auch kein `git rm`. Es war ein Löschen am Dateisystem vorbei an Git.

### Was der Messgang stattdessen fand — zeitlich passend, **nicht bewiesen**

- **macOS-Großupdate 26 → 27, installiert am 15.09. um 08:41**
  (`softwareupdate --history`). Das Neustart-Protokoll beginnt erst mit diesem
  Update (`wtmp begins Tue Sep 15 08:45`) — was davor lag, ist nicht mehr
  sichtbar.
- **Das iCloud-Protokoll beginnt am 15.09. um 02:26** mit einem Neustart des
  Dateiversions-Dienstes (`revisiond … starting`) und einer Reihe von Fehlern
  *„failed to resolve docID … No such file or directory"*.
- **`docs/auftraege` wurde am 15.09. um 02:27 verändert** — eine Minute danach.
  Keine Datei darin trägt dieses Datum, also wurde dort etwas entfernt oder
  umbenannt, nicht angelegt.

**Die Grenze dieser Messung:** Die Pfade im Systemprotokoll sind als
`<private>` geschwärzt. Ob die Fehlermeldungen den verschwundenen Ordner
betreffen, lässt sich daraus nicht lesen — ebenso wenig, ob sie **Ursache**
oder **Folge** waren. Ein Betriebssystem-Update löscht gewöhnlich keine
Nutzerdateien; das Zusammentreffen ist ein Anhaltspunkt, kein Befund.

**Konsequenz:** Engywucks Gegenmaßnahme (Repo aus dem iCloud-Bereich nehmen,
Speicher-Optimierung abschalten) entfällt — beides ist bereits so. Es bleibt
der Griff von oben: **`git status` beim ersten Zug nach einer Pause, und beim
nächsten großen macOS-Update gezielt davor und danach.**

## Noch aufzunehmen

- Das **Gedächtnis** (`~/.claude/memory/`): außerhalb beider Repos, ohne
  Versionierung, ohne Prüfer (siehe `docs/befund-offene-verhaltensregeln.md`).
- **iCloud-Ordner** als Weg für Auftragspapiere: unterliegt dem
  macOS-Datenschutz und war am 28.08. für Werkzeuge gesperrt.
- **`~/.claude/settings.json`**: Seit dem 10.09. lädt der Empfang sie nicht
  mehr (`setting_sources=[]`) — der Hauptstrom aber sehr wohl.
