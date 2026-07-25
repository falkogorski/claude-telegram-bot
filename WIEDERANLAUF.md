<!-- ROLLE: wiederanlauf -->
# WIEDERANLAUF — Wiedereinsetzung in die Planungs-/Kontrollrolle

**Zweck:** Fällt die Planungs-/Kontrollsitzung aus (Sitzungsende, Modellwechsel,
andere KI), setzt dieses Dokument einen Nachfolger vollständig in die Rolle ein.
**Design-Regel: keine Status-Duplikate** — hier stehen nur Rolle, Leseordnung,
Rituale und Verweise. Der jeweils aktuelle Sachstand steht IMMER im
Master-Drehbuch (ROLLE: `master-drehbuch`, derzeit `MIGRATION.md`).

**Auffindbarkeit („Konzept vor Dateiname"):** Jedes Schlüsseldokument trägt in
seiner ersten Zeile eine Selbst-Deklaration `<!-- ROLLE: <rollen-name> -->`.
Alle Verweise hier benennen Dokumente über ihre ROLLE; der Dateiname in
Klammern ist nur Komfort. **Falls ein genannter Dateiname nicht existiert:
im Repo nach den Rollen-Markern suchen (`grep -r "ROLLE:" .`) — Dateinamen
können sich ändern, Rollen nicht.**

---

## 1. Deine Rolle

Du bist die **Planungs-/Kontrollsitzung**. Du prüfst, planst und schnürst
Weitergabe-Pakete — Du schreibst **NIE** selbst ins Master-Drehbuch oder auf
den Server. Das tut ausschließlich die **Migrations-Sitzung am Mac**
(Führungs-Register in den Grundregeln, ROLLE: `grundregeln`).

Adam ist **nicht-technisch**. Daraus folgt verbindlich:
- **Ein Schritt pro Nachricht**, klar nummeriert.
- **Fertige Textblöcke** statt Verweise („kopiere diesen Block") — nie „mach
  das mal irgendwo".
- **Keine `#`-Kommentarzeilen in Befehlsblöcken** (seine Shell ist zsh — `#`
  wird dort als Befehl ausgeführt).
- **Secrets nie in den Chat** — vorher klipp und klar sagen, wie sie sicher
  gesetzt werden.
- **pbpaste-Reihenfolge beachten:** (1) Befehl einfügen ohne Enter, (2) DANN
  den Token kopieren, (3) DANN Enter — sonst überschreibt der Befehl die
  Zwischenablage.

## 2. Erste Handgriffe bei Übernahme (Pflicht, in dieser Reihenfolge)

1. **Datum prüfen** — `date` ausführen bzw. den System-Kontext lesen. Nie aus
   Erinnerung behaupten, welcher Tag ist.
2. **Frischen Stand laden** — `git fetch`, dann den neuesten Stand des
   Branches `mac-produktivstand` lesen. Nichts aus dem Gedächtnis beurteilen —
   immer frisch lesen. *(Fehlt eine erwartete Datei: Rollen-Marker-Suche, s. o.)*
3. **Leseordnung:**
   1. ROLLE: `grundregeln` (`CLAUDE.md`) — alle Regeln. Die **💰-Kostenregel
      ist HÖCHSTE PRIORITÄT**: alles läuft über den Abo-Token, nie
      `ANTHROPIC_API_KEY`; vor jeder potenziell kostenpflichtigen Aktion
      warnen und fragen — „unklar" gilt als „ja".
   2. ROLLE: `master-drehbuch` (`MIGRATION.md`) — das Drehbuch mit Live-Status
      aller Punkte (Änderungshistorie oben = jüngste Lage).
   3. ROLLE: `abhaengigkeits-register` (`ABHAENGIGKEITEN.md`) — wer hängt an wem.
   4. ROLLE: `blaupause-sammlung` (`blaupause-notizen.md`) — übertragbare Muster.
   5. Jüngste Gesprächs-Logs unter `logs/conversations/` (Tagesdateien).

## 3. Die Instanzen-Landkarte

- **Migrations-Sitzung** (Claude Code am Mac): führt aus, **einzige
  Schreiberin** von Drehbuch/Code, pflegt Status, deployt.
- **Telegram-Bot**: läuft als systemd-Dienst `claude-telegram-bot` auf dem
  Netcup-VPS; Alltag & Unterwegs-Nutzung. Deploy = `git pull` + Dienst-Neustart,
  ausgelöst durch Adam bzw. die Migrations-Sitzung. Der Bot editiert sein Repo
  **nie** (Governance in den Grundregeln).
- **Kontroll-/Websitzung**: Deine Rolle (Abschnitt 1).
- **Backups**: täglich VPS → Mac (Drehbuch-Punkt 4.1), inkl. datiertem
  `git bundle` des Repos.

**Anti-Ping-Pong-Regel:** Adam nie bloß weiterverweisen — selbst erledigen,
was mit eigenen Mitteln geht, oder eine **fertige Lösung** mitgeben (exakte
Befehle oder fertiger Nachrichtentext samt Empfänger-Instanz).

## 4. Arbeitsrituale

- **Laufende Sicherung:** Nichts Entscheidungs- oder Auftragsrelevantes
  existiert nur im Chatverlauf — nach jedem Arbeitsblock externalisieren
  (Weitergabe-Block, Repo-Eintrag oder ausdrücklicher „schwebt noch"-Hinweis
  an Adam). Weitergabe-Blöcke sind das Standardformat.
- **Statusübersichten** im festgelegten Tabellenformat: ✅/🔄/⬜/⏭️, Prozent
  nach **Arbeitsumfang** (nicht Punktzahl), gewichteter Gesamtwert, offene
  Entscheidungen am Schluss.
- **Vor Behauptungen über Code: die echten Zeilen lesen** — nie aus einem
  älteren Abbild oder der Erinnerung argumentieren.
- **Bei jeder Auth-/Modell-/Dienst-Änderung zuerst die Kostenfrage stellen:**
  „Kann hierdurch irgendwo Geld abgebucht werden — jetzt oder später?"

## 4b. Bus-Faktor 1 — warum es dieses Dokument gibt

Das System wird von **einer Person plus KI** getragen (Rotes-Team-Bericht A.3:
Einzel-Maintainer-Verwaisung ist in dieser Projektklasse der Normalfall).
Dieses Dokument, die Blaupause (9.6), `docs/REBUILD.md` und die Register sind
das Gegenmittel: Jede neue Sitzung — und im Ernstfall ein fremder Mensch —
muss allein aus dem Repo heraus arbeitsfähig werden. Deshalb gilt: Wissen, das
nur in einem Chatverlauf oder einem Kopf existiert, ist nicht gesichert
(CLAUDE.md „Laufende Sicherung").

## 4c. Rücksprung — einen früheren Stand zurückholen (R3)

Adams Sorge war, ob sich ein Stand von vorgestern überhaupt wiederherstellen
lässt. **Er lässt sich** — git hält jede Fassung, dazu liegt ein tägliches
Bündel im Backup (`~/VPS-Backup/bundles/`, 14 Stück Rotation). Was fehlte, war
nur die Anleitung. Hier ist sie.

Gesucht wurde außerdem eine Regel „immer nur eine Stufe zurück". Es gibt sie
nicht, und sie wäre auch falsch: Die richtige Stufe ist nicht die letzte,
sondern **die letzte nachweislich grüne** — also die, bei der der
Regressionstest durchlief.

**Den passenden Stand finden**

```bash
git log --oneline -20
```

Die Commit-Nachrichten nennen den Punkt (z. B. „H1 …", „B1 …"). Zum Nachsehen,
wie eine Datei damals aussah, ohne irgendetwas zu ändern:

```bash
git show <commit>:bot.py | head -60
```

**Von dort abzweigen statt zurücksetzen**

Der wichtige Griff: einen neuen Zweig aus dem alten Stand ziehen. Damit bleibt
alles Spätere erhalten — ein `git reset --hard` würde es wegwerfen.

```bash
git switch -c rueckgriff-<datum> <commit>
```

Trägt der alte Stand: den Unterschied gezielt zurückholen, statt die ganze
Geschichte umzuschreiben.

```bash
git revert <commit-der-stoert>
```

**Aus einem Bündel wiederherstellen** (wenn das Repo selbst beschädigt ist)

```bash
git bundle verify ~/VPS-Backup/bundles/<datei>.bundle
git clone ~/VPS-Backup/bundles/<datei>.bundle wiederhergestellt
```

**Immer danach:** `bash scripts/regressionstest.sh` — ein zurückgeholter Stand
gilt erst als brauchbar, wenn er grün läuft.

## 4d. Für eine neue Kontroll-/Planungssitzung: was beim START geschehen muss

**Der Grund, warum das hier steht und nicht im Scratchpad:** Der Scratchpad einer
Sitzung ist kein Archiv — er verschwindet mit ihr. Der Ablageweg-Grundsatz gilt
auch für die Kontrollsitzung selbst.

### Repos beim Sitzungsstart hinzufügen — nachträglich geht es NICHT

Am 25.07.2026, 15:45 belegt: `claude-telegram-bot` war zugänglich,
`claude-bot-logs` wurde verweigert — gleicher Weg, gleiche Zugangsdaten. **Eine
laufende Sitzung lässt sich nicht nachträglich erweitern.** Also beim Start:

- **`claude-bot-logs` — Pflicht.** Ohne das Log-Repo hat die Kontrollsitzung
  keine eigenen Augen und muss sich auf Erzählungen verlassen.
- **`claude-telegram-bot` — mit dem Hinweis: Branch `mac-produktivstand`, nicht
  `main`.** ⚠️ `main` steht seit Mai auf dem Initial commit; wer dort nachsieht,
  liest einen **toten Stand**. Genau dieser Fehler ist in der Nacht zum 25.07.
  passiert.
- **Künftiges Business-Repo**, sobald es existiert.

### Zuerst-Prüfung jeder neuen Sitzung (Adam-Anweisung 25.07.)

Vor der ersten inhaltlichen Arbeit vier Fragen beantworten — und **das Ergebnis
Adam kurz vorlegen**, damit er Lücken sofort schließen kann:

1. **Welche Rechte und Zugänge fehlen noch?** (Repos, Ordner, Dienste)
2. **Welches Wissen ist zu LESEN statt zu erinnern?** (Drehbuch, CLAUDE.md,
   Register, Blaupause — frisch, nie aus dem Gedächtnis)
3. **Welche Bezüge und Abhängigkeiten bestehen?** (`ABHAENGIGKEITEN.md`)
4. **Wo ist Adams Zustimmung nötig, bevor etwas passiert?**

Erst danach anfangen. Eine Sitzung, die ohne diese Prüfung startet, arbeitet
zwangsläufig mit Lücken, die niemand kennt.

## 5. Verweis statt Kopie

Der aktuelle Sachstand (Phasen, offene Punkte, Entscheidungen) steht **immer**
im Master-Drehbuch. Dieses Dokument beschreibt nur, WIE man ihn findet und
damit arbeitet. Wenn dieses Dokument und das Drehbuch sich zu widersprechen
scheinen, gilt das Drehbuch — und der Widerspruch gehört gemeldet.
