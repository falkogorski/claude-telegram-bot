> **Zweck: WEITERGABE → Mick** (Adam zur Ansicht, zwei Entscheide unten) ·
> **Zu tun:** vier Befunde beheben, Reihenfolge wie nummeriert; dann eine
> Nachprüfung durch mich — danach ist die Kette nach Konvergenz-Bremse zu Ende.

# Gegenprüfung Nachtblock + drei Zusagen — Stand `064a062`, Bericht `360c10b`

**Stichtag:** 04.09.2026, 19:56 (`date`, Berlin) · **Geprüft:** am Code im Klon
`360c10b`, nicht am Bericht · **Nenner:** 11 Berichtsaussagen gemessen,
7 bestätigt, 1 widerlegt (Neustart), 3 nicht messbar von hier (benannt) ·
**4 Befunde**, davon 3 gemessen ausgeführt, 1 gemessen im Ziel (Log-Repo).

**Urteil in einem Satz:** Alles Gebaute tut, was der Bericht sagt — aber
**Z-1 zählt den Bestand statt das Getane** (zweimal, in beiden Hälften),
**der Fernbefehl baut eine Shell-Zeichenkette aus Ordnernamen**, und **der
Log-Abgleich hat die Vergleichsrechnung als PDF nach GitHub getragen.** Nicht
abhaken, bevor 1–4 stehen.

---

## Bestätigt (gemessen, nicht gelesen)

- **Zielumgebung 41/43** im Klon reproduziert, 2 übersprungen mit Grund.
  `bash -n` grün für alle vier geänderten Skripte. **72/72 hier nicht
  reproduzierbar** (keine venv) — unbestätigt, nicht widerlegt.
- **Z-2** ist eine Menge: zwei Bäume, Ausschlüsse nur für Reproduzierbares,
  `site-packages` statt `.venv` — richtig herum gedacht (vergessener
  Ausschluss kostet Platz, vergessener Einschluss Daten). `ITEMS` bleibt für
  Außerhalb. Das war meine Prüffrage vom Morgen; sie ist beantwortet.
- **Z-1b** rechnet mit `$BOTHOME`, die Staffelung über `find -mtime` liefert
  ehrlich „mindestens N" (3 Tage → 2, 20 Tage → 15 — nachvollzogen an der
  Rundungsregel von `-mtime`).
- **Z-3** trägt Gültigkeits-Kopf, 💰 je Weg, die Ultracode-Prüfstelle und die
  Bedingung gegen „später = nie". Empfehlung als solche gekennzeichnet. Ich
  teile sie.
- Register, Drehbuch, vier Blaupause-Zeilen: vorhanden, konsistent.
- Chat-Nummer im Sitzungsstart-Hook: steht bereits an **13 Stellen** im Repo
  (Postfach-Skript, Doku, Prüfer) — kein neues Geheimnis.
- `RECHNUNGSREGELN.md` konnte ich lesen — **über das Log-Repo** (siehe Befund
  4). Zehn Regeln, Ergänzungs-Vorbehalt oben, Spesen als offene Frage.

---

## 🔴 Befund 4 zuerst — Wirkungs-Regel: die Vergleichsrechnung liegt auf GitHub

**Gemessen im Log-Repo `claude-bot-logs` (privat, über die GitHub-Schnittstelle
geprüft), Stand `82c9fec`:**

```
ausarbeitungen/rechnungen/README.md               3.975 B
ausarbeitungen/rechnungen/RECHNUNGSREGELN.md      6.973 B
ausarbeitungen/rechnungen/output/Rechnung 012-26.pdf   62.202 B
```

**Ursache:** `scripts/log_sync.sh` nimmt `--include='*.pdf'` und `*.md` über
den ganzen `~/workspace/`. Der Umzug hat neuen Inhalt unter einen alten Filter
gelegt — **Fenster-Regel:** Der Abgleich war richtig, das Rechnungsprojekt war
neu darunter. Ausgeschlossen werden nur Namen mit `secret|token|credential|
passwor|key|.env`; eine Rechnung heißt nicht so.

**Was drin ist:** Den PDF-Text kann ich hier nicht auslesen (kein Leser
installierbar). Nach Bauart der Vorlage — README des Projekts: *Stammdaten
(Absender, Bank, §19-Hinweis) stehen auf der Rechnung* — trägt sie
**Bankverbindung, Steuernummer, Kundenanschrift.** Der `stammdaten`-Marker
schützt die JSON; **die gerenderte PDF trägt dieselben Daten und ist das
Geschwister, das der Marker nicht sieht.** Ab der nächsten Server-Rechnung
kämen `output/` **und** `ausgang/` mit — alle fünf Minuten.

**Die Quittung hat es gesagt:** `ausarbeitungen/letzter-abgleich.txt`,
*03.09.2026, 01:00, MITGENOMMEN: rechnungen/output/Rechnung 012-26.pdf*.
Gelesen hat es niemand — auch ich nicht bis heute. Eine Quittung, die niemand
liest, ist eine Logzeile (Blaupause-Zeile, universell).

**Fix (klein):** In `log_sync.sh` `--exclude='rechnungen/'` **vor** die
Includes — Reihenfolge ist die Funktion (Lehre vom 25.07., steht als
Kommentar direkt darüber). Nachweis nach Wirkungs-Regel: nächster Abgleich,
`letzter-abgleich.txt` ohne `rechnungen/`, **und** die drei Dateien aus dem
Log-Repo entfernt (ein `git rm`, den der Abgleich mitnimmt — bitte prüfen,
ob das Skript Gelöschtes überhaupt löscht; sonst von Hand).

**Historie:** Die PDF bleibt in der Git-Historie des Log-Repos, bis sie
bereinigt wird. **Adams Entscheid** (unten). Nicht eilig — privat —, aber
nicht stillschweigend.

**Deploy:** `git pull` auf dem VPS, **kein Neustart** (Skript, kein Bot-Code).

## 🔴 Befund 3 — der Fernbefehl trägt Ordnernamen als Shell-Text

**Gemessen** (`ssh` als Attrappe, Ordner `L'Osteria/Bar` im Übergabeordner).
Was auf dem Server ankäme:

```
python3 …/postfach_ablegen.py --chat '1' --text '📁 2 Rechnung(en) nach iCloud gelegt: Kunde/Projekt L'Osteria/Bar '
```

Die Shell dort liest: Zeichenkette bis `L`, dann nacktes `Osteria/Bar`, dann
ein neues Argument `' '`. **Ergebnis heute:** argparse lehnt ab, die Nachricht
fällt aus, nur die Logzeile „nicht zustellbar" — Adam erfährt nichts, und
Apostrophe in Firmennamen sind nicht exotisch. **Ergebnis mit anderem Inhalt:**
`x'; <befehl>; echo '` läuft als `claudebot` auf dem VPS.

**Woher der Name kommt:** aus dem Feld `ablage`, das Claudia in den Datensatz
schreibt — aus Adams Angaben **oder aus Dokumenten, die sie liest.** Das ist
die Klasse *von außen*. Die Pfadprüfung in `ablage.py` kennt zehn Fälle
(`..`, absolut, Tilde); **Zeichen prüft sie nicht** — jedenfalls sagt die
Doku es nicht.

**Fix, beide Seiten:**
- **Mac-Seite:** Text nie in die Fernbefehls-Zeichenkette. Entweder
  `postfach_ablegen.py` bekommt `--text -` (liest stdin) und das Skript
  ruft `printf '%s' "$_text" | ssh … "python3 … --chat N --text -"` — oder,
  ohne das Skript anzufassen, `"… --text \"\$(cat)\""` mit dem Text auf stdin.
  **Empfehlung: stdin-Schalter** — deterministisch, prüfbar, keine
  Quoting-Abwägung mehr (dieselbe Lehre wie beim Heredoc für Commit-Texte).
- **Server-Seite, elfter Pfadfall in `ablage.py`:** Zeichenmenge **positiv**
  benennen (Buchstaben mit Umlauten, Ziffern, Leerzeichen, `- _ . / & ( )`),
  alles andere abweisen. Das ist eine Menge, keine Verbotsliste.

**Gegenprobe:** Ordner mit `'` und mit `;` → Nachricht kommt **vollständig**
an (Attrappe protokolliert ein einziges `--text`-Argument); Server weist den
Pfad ab, bevor eine Datei entsteht.

## 🔴 Befund 1 — Z-1a meldet bei jedem Sitzungsstart erneut

**Gemessen, zwei Läufe hintereinander, dazwischen nichts Neues:**

```
Lauf 1: Haelfte 2: 1 Datei(en) in ihre Kundenordner gelegt → Adam benachrichtigt: 📁 1 Rechnung(en) …
Lauf 2: Haelfte 2: 1 Datei(en) in ihre Kundenordner gelegt → Adam benachrichtigt: 📁 1 Rechnung(en) …
```

(`rsync` als Attrappe, die nur kopiert — das Zählen im Skript ist
`find`-basiert und davon unabhängig, deshalb trägt die Messung.)

**Ursache:** `_tief` zählt den **Bestand** im Übergabeordner `LOKAL`
(`find -mindepth 2`), nicht das **Kopierte**. `LOKAL` wird nie geleert
(`-u`, kein `--delete`), also wächst der Bestand, und jede Mac-Sitzung sagt
Adam „N Rechnungen gelegt" — **mit steigendem N und ohne dass etwas geschah.**
Das ist genau das Rauschen, das die Nur-bei-`_tief > 0`-Bedingung verhindern
sollte, und dazu eine **falsche Aussage** („gelegt"). `_wohin` hat denselben
Fehler: es nennt alle Ordner, die je durchliefen.

**Fix:** `_tief` und `_wohin` aus der Itemize-Ausgabe des Kopierlaufs
(`rsync -a -u -i …`, Zeilen, die mit `>f` beginnen) — dann zählt, was
tatsächlich übertragen wurde. Prüfstand-Zeile: **zwei Läufe, der zweite
still.** Das ist die Gegenprobe, die gefehlt hat: Alle drei bisherigen
(Elternordner fehlt · Ziel nicht anlegbar · leerer Ordner) messen den **ersten**
Lauf.

## 🔴 Befund 2 — Geschwister von 1: der Tagescheck zählt einen Ordner, der nie leer wird

`ausgang/` auf dem Server wird von Hälfte 1 **kopiert, nie geräumt.** Zeile 9j
zählt Dateien älter als einen Tag darin. **Folge:** Ab der ersten
Server-Rechnung meldet der 4-Uhr-Check **täglich, für immer, mit wachsender
Zahl** — und die Anweisung *„Mac-Sitzung starten"* lässt die Zeile nie
verschwinden, weil die Sitzung nichts räumt. Heute noch unsichtbar
(`daily-check.log` 03./04.09. ohne Rechnungszeile), weil `ausgang/` leer ist —
017-26 entstand auf dem Mac.

**Fix:** `ausgang/` ist ein **Durchgangsordner** — Hälfte 1 holt mit
`--remove-source-files`. Nichts geht verloren: `output/` behält die Datei auf
dem Server, das Backup (Z-2) sichert `output/`, der Mac hält `LOKAL`. Dann
misst 9j nur **Ungeholtes**, und die Meldung stimmt. Scheitert Hälfte 2, liegt
die Datei in `LOKAL` und wird beim nächsten Lauf gelegt — das zeigt die
Sitzungsstart-Zeile ohnehin an.

**Register-Zeile nachziehen:** *„Kopieren, nie löschen"* gilt für das
**iCloud-Ziel** (Adams Ablage), nicht für den Server-Ausgang. Wer das nicht
unterscheidet, streicht später den falschen Schalter.

**Gegenprobe:** Datei in `ausgang/` → Hälfte 1 → Server leer, `LOKAL` voll →
9j still.

---

## Kleiner, aber nicht weglassen

- **„Deploy mit Neustart — Produktivcode dabei" ist widerlegt.** Gemessen
  `git diff --stat d6b8190 064a062`: keine `.py`-Datei. Der Neustart vom
  03.09. 00:2x trug alles Bot-seitige. **`git pull` genügt** (Tagescheck,
  Log-Abgleich); ein Neustart ohne Grund bricht Claudia mitten im Zug ab.
- **Steht 017-26 im Server-Zähler?** 017-26 entstand auf dem Mac; das Projekt
  ging um 00:59 per rsync (mit `daten/`) auf den Server. Je nach Reihenfolge
  fehlt die Nummer dort — dann vergibt Claudia **017-26 ein zweites Mal**, der
  Fall, vor dem Regel 8 warnt. **Eine Messzeile** (Befehl im Register), bitte
  im Bericht nennen. Von hier nicht messbar.
- **Die zehn Pfadfälle** stehen nicht in der Änderungsdoku — drei genannt plus
  der gefundene Fehler. Das Projekt ist unversioniert; die Doku ist die einzige
  Ablage des Prüfers. Nachtragen, mit Fall elf (Zeichenmenge).
- **Spesen: Bericht und Datei widersprechen sich.** Bericht: *50/80/30 %
  (14,00 · 22,40 · 8,40)*. `RECHNUNGSREGELN.md`: *14,00 · 28,00 · 22,40 ·
  11,20*. Die Datei ist die Ablage; der Bericht hat eine Zahl erfunden.
- **① `$HOME`:** gedeckt durch den bestehenden Prüfer, gefangen beim Bauen —
  **kein neuer Wächter** (Konvergenz-Bremse, Wächter dritter Ordnung). Die
  Klasse steht in der Blaupause; das reicht.

## Reihenfolge und Deploy

**4 → 3 → 1+2 (ein Skript) → Kleinkram.** Vier ist eine Zeile und läuft
alle fünf Minuten weiter; drei ist die Sicherheitsstelle; eins meldet sich
beim nächsten Mac-Start von selbst. Alles ohne root, alles ohne Neustart.
Vor jedem Commit der Regressionslauf, vor jeder Gegenprobe `__pycache__`
weg und die erwartete rote Zeile vorher hingeschrieben.

---

## An Adam — zwei Entscheide, beide wirken sofort

**① Spesen-Staffel (Micks Stelle ②, Regel „nicht raten").** Was ich weiß,
ohne Netzsuche (💰): Die steuerlichen Pauschalen (§ 9 Abs. 4a EStG) sind
**28 € je vollem Abwesenheitstag, 14 € je An- und Abreisetag bei
Übernachtung — ohne Acht-Stunden-Bedingung**; die acht Stunden gelten nur
für Tage **ohne** Übernachtung. Gestellte Mahlzeiten kürzen: **Frühstück
20 %, Mittag und Abend je 40 %** — das ist genau die 80-%- und 40-%-Logik,
die im Projekt schon steht. Stand meines Wissens; eine Erhöhung auf 32/16 €
wurde 2024 nicht beschlossen. **Was du dem Kunden berechnest, ist
Vereinbarung, nicht Gesetz** — die Pauschale ist nur die übliche Bezugsgröße.

**Frage mit Wirkung:** *Gilt für die Kundenrechnung diese Staffel (28/14,
Kürzung 20/40/40)?* Ein Ja im Chat an Mick → Regel 5 wird ergänzt, die
Nachfrage „mehr als acht Stunden?" entfällt bei Übernachtungstagen. Ein Nein →
du nennst die Sätze, Mick trägt sie ein.

**② Log-Repo-Historie.** Die PDF von 012-26 bleibt in der Git-Historie des
(privaten) Log-Repos, auch nach dem Fix. *Bereinigen lassen?* Ja → Mick
liefert dir den Befehlsblock (Historie neu schreiben, einmalig, dein
Terminal). Nein → sie bleibt, bewusst.

**Zu Micks Vorlage (Z-3)** brauchst du nichts zu entscheiden, bis mehr als
Rechnungen auf den Server sollen — seine Bedingung ist die richtige.

---

## Bei mir

- **Nachprüfung** nach Micks Fix-Commit — die letzte Runde dieser Kette.
- Dialoganteil-Messung (≤ 20 %) nach einem Arbeitstag mit Claudia — es gab am
  03./04.09. **kein** Gespräch mit ihr (Log-Repo ohne `conversations/` für
  beide Tage), die Messung wartet also.
- Kurs-Blick: der ungelesene Abgleichs-Beleg gehört als Stichprobe hinein.
