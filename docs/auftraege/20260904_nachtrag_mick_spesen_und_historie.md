> **Zweck: WEITERGABE → Mick** · **Zu tun:** zwei Entscheide Adams umsetzen —
> eine Regel, ein Befehlsblock. Gehört hinter Befund 4 der Gegenprüfung
> `064a062`, nicht davor.

# Nachtrag: Spesen-Staffel und Log-Repo-Historie — Adams Entscheide

**Stichtag:** 04.09.2026, 20:03 (`date`, Berlin) · **Adam, Wortlaut:** *„ja zur
steuerlichen Staffel, Historie bereinigen, an Mick"*

## ① Spesen — Regel 5 in `RECHNUNGSREGELN.md` ergänzen, nichts ersetzen

Adam hat die steuerliche Staffel als Bezugsgröße der Kundenrechnung
bestätigt. Einzutragen, im Sinn der Datei (*ergänzt, ersetzt nichts*):

- **Voller Abwesenheitstag (24 h): 28,00 €.** Kürzel `Spesen:voll` — in
  `saetze.json` steht `Spesen_voll 28,00` bereits, im README-Kürzelblock
  fehlt es; nachziehen.
- **An- und Abreisetag bei Übernachtung: 14,00 €**, `Spesen:klein` —
  **ohne Acht-Stunden-Bedingung.** Die acht Stunden gelten nur für Tage
  **ohne** Übernachtung (dann ebenfalls 14,00 €, sonst nichts).
- **Gestellte Mahlzeiten kürzen den Tagessatz:** Frühstück 20 %, Mittag
  40 %, Abend 40 %. Das ist die vorhandene Logik — `Spesen:80` = Frühstück
  gestellt (22,40), `Spesen:40` = Frühstück und ein Hauptmahl gestellt
  (11,20). Ausschreiben, damit die nächste Instanz nicht rät, was 80 heißt.
- **Der offene Block „Was noch offen ist"** wird durch die Regel ersetzt;
  die Abfrage *„mehr als acht Stunden?"* entfällt bei Übernachtungstagen und
  bleibt nur für Tagesfahrten ohne Übernachtung.
- **Herkunft in die Datei:** *steuerliche Pauschalen § 9 Abs. 4a EStG als
  Bezugsgröße, Adam bestätigt 04.09.2026; Beträge Stand Kenntnis der
  Kontrolle, nicht per Netzsuche geprüft (💰).* Wer sie prüfen will, tut es
  mit Adams Freigabe, nicht nebenbei.
- Die Zahl **8,40 aus deinem Bericht** kommt nirgends vor — nicht eintragen.

Prüfer dazu: keiner nötig — es ist eine Datenregel, die der Generator über
`saetze.json` ohnehin misst. **Wohl aber:** Der Aufstellungs-Datensatz
für 017-26 trägt die alten Bezeichnungen? Dann einmal gegen die Regel
lesen, nicht neu erzeugen.

## ② Log-Repo-Historie bereinigen — Befehlsblock für Adam

**Reihenfolge ist die Funktion.** Wird die Historie vor dem Filter-Fix
umgeschrieben, bringt der nächste Abgleich die PDF in fünf Minuten zurück,
und die Arbeit war umsonst.

1. **Zuerst Befund 4:** `--exclude='rechnungen/'` vor den Includes,
   `git rm` der drei Dateien, Deploy per `git pull`, **einen Abgleich
   abwarten** und in `letzter-abgleich.txt` messen, dass `rechnungen/`
   nicht mehr erscheint. Erst dann weiter.
2. **Abgleich anhalten** für die Dauer des Umschreibens (Zeitgeber auf dem
   VPS stoppen — welcher, steht im Register), sonst schiebt er mitten hinein.
3. **Frischer Klon auf dem Mac**, dort `git filter-repo --path
   ausarbeitungen/rechnungen/ --invert-paths`, dann `git push --force
   origin main`. `git-filter-repo` ist quelloffen und kostenfrei (💰: nein);
   falls nicht installiert, `pip install git-filter-repo` in einer venv, nicht
   systemweit (PEP 668, dieselbe Lehre wie bei openpyxl).
4. **Alle Klone nachziehen, sonst kommt die alte Historie zurück:** der
   Abgleichs-Klon auf dem VPS (`git fetch && git reset --hard origin/main`),
   der Mac-Klon, und — bitte im Bericht nennen — jeder weitere, den du kennst.
   Ein Klon mit alter Historie, der einmal pusht, macht alles rückgängig.
5. **Abgleich wieder starten**, nächsten Lauf abwarten, messen:
   `git log --all --oneline -- 'ausarbeitungen/rechnungen/'` leer, **und**
   die Datei ist im GitHub-Verlauf nicht mehr erreichbar.

**Was Adam wissen soll, ehrlich:** GitHub hält überschriebene Objekte eine
Weile im Cache; für ein privates Repo ohne Fremdzugriff ist das tragbar. Wer
mehr will, bittet den GitHub-Support um eine Bereinigung — das ist dann seine
Entscheidung, kein Automatismus.

**Was in Adams Hand liegt:** der Force-Push (Historie eines Repos) und das
Anhalten/Starten des Zeitgebers auf dem VPS, wenn er als root läuft. Alles
andere darfst du vorbereiten. Kein Neustart des Bots.

## Ins Register

Eine Zeile zum Log-Abgleich: *Ausschluss `rechnungen/` — die Rechnungen
tragen Bank und Steuernummer; wer den Filter anfasst, misst danach die
Quittung, nicht die Regel.* Und die Blaupause-Zeile aus der Gegenprüfung:
**Eine Quittung, die niemand liest, ist eine Logzeile.**
