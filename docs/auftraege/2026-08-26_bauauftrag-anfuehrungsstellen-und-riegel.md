# Bauauftrag: die vier Anführungsstellen — und der Riegel

**Stichtag:** 2026-08-26 · **überholt durch:** — · **maßgeblich ist diese Datei**

## Änderungsverlauf

**2026-08-27 07:10** — **Auftrag 3 (Umlaute) angehängt**, auf Adams Ansage von
07:03 Uhr. Zwei Handgriffe, kein Prüfer — Adam hat einen Prüfer für diese Regel
ausdrücklich abgelehnt: „Wir müssen nicht für alles Prüfer erstellen." Die
Aufträge 1 und 2 sind seit dem 26.08., 09:28 Uhr freigegeben und noch nicht
gebaut; deshalb meldete der Tagescheck am 27.08. denselben Befund erneut.

**2026-08-26 11:55** — Adam hat Weg C gewählt (11:47 Uhr). Auftrag 2b ist damit
entschieden und ausgeschrieben; die Wahlmöglichkeit ist entfallen. Beim
Ausschreiben kam ein **zweiter Befund** hinzu, der C erst vollständig macht: Es
gibt im Auftragsbuch überhaupt keinen Weg, einen gelben Auftrag zu erledigen.
Zahl der liegenden Einträge berichtigt — es waren sieben Sichtungen und ein
Wachposten-Befund, nicht acht Sichtungen. Die sechs alten Sichtungen sind
weggeräumt.

**2026-08-26 09:44** — erste Fassung.

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau).
**Anlass:** Adams Freigabe am 26.08.2026 um 09:28 Uhr, nach dem Tagescheck-Befund
vom selben Morgen. Wörtlich zu Auftrag 1: „ja, bitte machen". Zu Auftrag 2:
„neu scharf setzen und Sichtung auf die Grünliste", mit der Begründung, eine
täglich wiederkehrende negative Meldung werde nicht nur überlesen, sie nerve
auch — „zumal die ja auch einfach behoben werden muss."

**Diese Sitzung hat kein Schreibrecht im Projektarchiv.** Alles hier ist
ausgearbeitet, nichts ist gebaut.

---

## Auftrag 1 — Die vier gemischten Anführungspaare

### Lage

Der B6-Prüfer meldet seit dem 25.08. rot. **Nichts ist kaputtgegangen; der
Prüfer ist sehend geworden.** Bis dahin war er auf Python 3.12 und neuer blind
für f-Zeichenketten, weil PEP 701 sie in mehrere Token zerlegt und er nur nach
`tokenize.STRING` suchte. Der Server läuft Python 3.13.5 — dort sah er null
Treffer und meldete grün. Die Reparatur (`ddf7011`, `a2ba359`) hat ihn geheilt,
und seither zeigt er vier echte Stellen.

Der Einfrier-Vermerk vom 25.08. um 06:16 Uhr benennt sie ausdrücklich als
bekannt: „Lauf 53/54, der eine Rote sind die vier echten Anführungsstellen —
dokumentiert, nicht übersehen." Seither steht die Betriebslage auf Ruhe.

### Die vier Stellen (alle in `bot.py`)

| Zeile | Muster |
|---|---|
| 4777 | `f'{spec["emoji"]} Haus „{spec["title"]}" erkannt — '` |
| 4808 | `f'{spec["emoji"]} Haus „{spec["title"]}" eingerichtet.'` |
| 4870 | `f'Gruppe „{chat.title or chat.id}" erkannt.'` |
| 4878 | `f'Das sieht nach dem Haus {spec["emoji"]} „{spec["title"]}" aus — '` |

Alle vier tragen einen typographischen Öffner und einen geraden Schließer.

### Wirkung heute: keine — und genau das ist die Falle

Die vier Zeichenketten sind mit **einfachen** Anführungszeichen begrenzt, das
gerade Zeichen im Inneren beendet sie also nicht. Der Bot läuft. Gefährlich
werden sie in dem Augenblick, in dem jemand den Begrenzer auf doppelte
Anführungszeichen umstellt oder die Zeile umbaut — und **genau diese Falle ist
in diesem Projekt fünfmal zugeschnappt.** Der Prüfer meldet also nicht einen
Defekt, sondern eine geladene Waffe.

### Auflage

Den geraden Schließer durch das typographische Schlusszeichen ersetzen, sodass
jedes Paar aus `„` und `“` besteht. Der Prüfer zählt genau dieses
Gleichgewicht.

Die vom Prüfer ebenfalls genannte Alternative — eckige Klammern — ist hier
schlechter: Sie verändert das Erscheinungsbild der Nachricht im Chat, während
das typographische Paar es **verbessert**. Es ist die kleinste denkbare Änderung
mit einem Nebengewinn.

### Gegenprobe vorab (bereits gelaufen)

Am Wortlaut dieser vier Zeilen hängt **kein** Test. Gesucht wurde nach den
Textbestandteilen in allen Prüfskripten; einziger Treffer ist der B6-Prüfer
selbst, und der prüft die Zeichen, nicht den Satz. Der Wortlaut ist damit frei
änderbar.

### Abnahme

- `scripts/test_blinde_flecken_b6.py` läuft grün durch.
- Der volle Regressionslauf steht wieder bei 54 von 54.
- Der Tagescheck am folgenden Morgen meldet den Regressionstest grün.

### Was kann brechen und wer merkt es

- **Ein Umlaut- oder Kodierungsfehler beim Einsetzen** — das typographische
  Schlusszeichen ist ein Mehrbyte-Zeichen. Merkt: der Regressionslauf sofort,
  weil die Datei nicht mehr übersetzt.
- **Die Ausgabe im Chat ändert sich sichtbar** (gerades zu typographischem
  Zeichen). Merkt: Adam beim nächsten Haus-Einrichten. Gewollt.
- **Der Prüfer bleibt trotz Korrektur rot**, falls eine fünfte Stelle
  hinzugekommen ist. Merkt: der Prüfer selbst, er nennt die Gesamtzahl vor der
  Liste.
- **Stiller Fehlschlag?** Keiner denkbar — der Prüfer ist der Wächter dieser
  Änderung und läuft täglich.

---

## Auftrag 2a — Der Riegel wird neu scharf gesetzt

### Lage

`auftragsbuch-riegel.md` trägt `SCHARF: ja` und `GILT-BIS: 2026-08-25`. Die
Frist ist abgelaufen, der Riegel gilt damit als geschlossen. **Das ist kein
Fehler, sondern die Bauart** — ein Schalter, der sich selbst zurücklegt, statt
darauf zu warten, dass jemand daran denkt.

### Die Auswertung der Probewoche, nachgeholt

In der ganzen Woche vom 18. bis 25.08. ist **kein einziger grüner Auftrag
übergeben worden.** Im Eingang lagen acht Einträge — sieben tägliche Sichtungen
und ein Wachposten-Befund vom 20.08. —, jeder gelb, die Sichtungen alle mit
derselben Begründung: „Art [sichtung] steht nicht auf der Grün-Liste". Einen
Ordner für Abgelegtes gab es nicht einmal, weil nie etwas abzulegen war.

**Die Probewoche konnte ihre eigene Frage nicht beantworten.** Sie sollte
zeigen, ob die Grün-Automatik trägt — beobachtet werden konnte nichts, weil sie
nie ausgelöst hat. Die im Riegel-Zettel offengehaltene Frage nach der Art `doku`
ist damit gegenstandslos: Es gab keinen einzigen `doku`-Auftrag.

### Auflage

`GILT-BIS` auf **2026-09-09** setzen (zwei Wochen). `SCHARF: ja` bleibt.

Im Abschnitt zur Probewoche vermerken, dass die erste Woche ohne eine einzige
Übergabe verlief, und **warum** — sonst liest sich die nächste Auswertung wie
die erste.

**Das Datum ist mein Vorschlag, nicht Adams Vorgabe.** Er hat „neu scharf
setzen" gesagt, ohne eine Dauer zu nennen. Zwei Wochen, weil eine Woche schon
einmal zu kurz war, um überhaupt etwas zu sehen.

### Was kann brechen und wer merkt es

- **Das Datum wird gesetzt, aber die Grün-Liste bleibt unverändert** — dann
  läuft die zweite Probewoche genauso leer wie die erste. Merkt: niemand, bis
  zum 09.09. Deshalb hängt 2b daran und darf nicht unentschieden liegen
  bleiben.
- **Ein Tippfehler im Datum** macht den Riegel sofort zu, mit Meldung. Merkt:
  der Tagescheck am nächsten Morgen.

---

## Auftrag 2b — Der Stapel im Auftragsbuch hört auf zu wachsen

**Vorgeschichte:** Adams erste Weisung um 09:28 Uhr lautete, Sichtung auf die
Grün-Liste zu setzen. Die Rückwärtsprüfung ergab, dass genau das sein Ziel
verfehlt hätte; der Befund ging um 09:37 Uhr an ihn. Um 11:47 Uhr hat er sich
für Weg C entschieden. Der Befund bleibt hier stehen, weil er die Begründung
der jetzigen Auflage trägt.

### Warum die Grün-Liste das Gegenteil bewirkt hätte

Sein Ziel ist Ruhe: keine täglich wiederkehrende Meldung, und die Sache soll
behoben werden. Rückwärts vom Ziel gerechnet, ergibt die Grün-Einstufung
folgenden Ablauf:

1. Der Tagescheck legt morgens den Sichtungs-Auftrag ab, jetzt grün eingestuft.
2. Das Auftragsbuch übergibt ihn an Hora **und meldet das an Adam** — die
  Meldung ist im Code fest verdrahtet und ausdrücklich ungedämpft
  (`auftragsbuch.py`, Zeile 366 folgend).
3. Hora nimmt ihn, findet **kein Feld `befehl`** — ein Sichtungs-Auftrag hat
  keines, er besteht nur aus Titel, Art, Marke und Beschreibung — und hakt ihn
  ab mit dem Vermerk „kein ausführbarer Befehl hinterlegt". Er erscheint als
  übersprungen in Horas Bericht.

**Ergebnis: zwei Meldungen täglich statt einer stillen gelben Ablage.** Und
abgearbeitet wäre die Sichtung trotzdem nicht — nur weggehakt.

Ein Nebenbefund zur Beruhigung: Die acht bereits liegenden Einträge tragen
`"ampel": "gelb"` in sich und würden **nicht** nachträglich mit übergeben. Das
Auftragsbuch prüft beim Übergeben beides, die Einstufung von heute und die im
Eintrag. Es gäbe also keinen Schwung von acht Meldungen auf einmal.

### Die eigentliche Ursache

**Der Sichtungs-Auftrag ist an eine denkende Sitzung gerichtet, nicht an ein
Skript.** Seine Beschreibung lautet: „Durchgang durch Tagesdatei,
Ausarbeitungen, Fehlerprotokoll und Tagescheck mit der Frage: Ist daraus ein
Auftrag entstanden?" Das kann kein Shell-Befehl leisten. Er landet im
Auftragsbuch, damit er nicht vergessen wird — aber es gibt keinen Mechanismus,
der ihn abarbeitet und wegräumt. Deshalb liegen acht Stück da.

Die Grün-Liste ist für Aufträge gebaut, die ein Befehl erledigt. Sichtung ist
keiner.

### Adams Entscheidung: Weg C (26.08.2026, 11:47 Uhr)

Sichtung **bleibt gelb** und wandert nicht auf die Grün-Liste. Stattdessen hört
der Stapel auf zu wachsen. Die beiden verworfenen Wege der Vollständigkeit
halber: die Sichtung gar nicht mehr abzulegen (verliert den Nachweis) oder sie
grün mit einem ausführbaren Befehl zu versehen (echter Bau, täglicher
Modelllauf ohne Adams Hand — eine Kosten- und Sicherheitsfrage). Weg B bleibt
als späterer Ausbau denkbar, wenn ein täglicher automatischer Lauf ohnehin
gewollt und in den Kosten geklärt ist.

### Der zweite Befund — ohne ihn wäre C nur halb

Beim Ausschreiben habe ich rückwärts gefragt, was alles wahr sein muss, damit
am Ende genau **eine** offene Sichtung im Eingang liegt. Dabei kam heraus:

**Das Auftragsbuch kennt keinen Weg, einen gelben Auftrag zu erledigen.**
Es hat `legen`, `eingang`, `einstufen`, `uebersicht` und `uebernehmen` — und
`uebernehmen` verschiebt ausschließlich **grüne** Aufträge ins Abgelegte. Für
einen gelben gibt es keine Tür nach draußen. Er liegt, bis ihn jemand von Hand
wegräumt.

Das ist die eigentliche Ursache des Stapels. Die Tagesmarke sorgt nur dafür,
dass täglich einer dazukommt; die fehlende Tür sorgt dafür, dass keiner je
geht. Ohne diese Tür läge auch nach der Marken-Änderung derselbe eine Eintrag
bis in alle Ewigkeit — nur eben still.

**Mit der Tür wird der Eintrag zum echten Fälligkeitszeichen:** Liegt eine
Sichtung im Eingang, ist sie offen. Ist keine da, ist sie erledigt, und der
Tagescheck legt am nächsten Morgen eine neue an. Das ist besser als der Zustand
vor allen Änderungen — heute sagt der Stapel gar nichts, weder über Fälligkeit
noch über Erledigung.

### Auflage — drei Teile

**(1) Die Marke verliert das Tagesdatum.**
In `scripts/daily_check.sh`, im eingebetteten Python-Abschnitt bei Zeile 324:
`marke = f"sichtung:{heute}"` wird zu `marke = "sichtung"`. Der Titel
entsprechend ohne Datum — „Sichtung der Ablagen" statt „Taegliche Sichtung der
Ablagen (2026-08-26)"; wann sie angelegt wurde, steht ohnehin im Feld
`eingang_am`. Die Doppelungssperre eine Zeile darüber vergleicht auf genau
diese Marke und greift damit unverändert.

Die Rückmeldung `SCHON-DA` bekommt einen passenden Text: statt „Sichtungs-
Vermerk liegt bereits (einer je Tag)" nun „eine offene Sichtung liegt bereits"
(Zeile 347). Der alte Text behauptet eine Tagesregel, die es dann nicht mehr
gibt.

**(2) Die fehlende Tür: eine Funktion `erledigen` im Auftragsbuch.**
Sie nimmt eine Marke oder einen Titel, verschiebt den passenden Eintrag aus
`eingang/` nach `abgelegt/` und schreibt einen Ergebnisvermerk in den Eintrag
(wer, wann, was dabei herauskam). Gebaut wie `uebernehmen`: erst schreiben,
dann wegräumen — der Befund der Gegenprüfung vom 18.08. gilt hier genauso.
Findet sie nichts, meldet sie das, statt still zu tun, als sei etwas geschehen.

**(3) Der Bestand ist bereits weggeräumt** (26.08., 11:52 Uhr, von mir): Die
sechs alten Sichtungen vom 20. bis 25.08. liegen jetzt in `abgelegt/`. Im
Eingang stehen noch die heutige Sichtung — die ist tatsächlich offen — und der
Wachposten-Befund vom 20.08.

**Der Wachposten-Befund ist ein eigener offener Punkt.** Er liegt seit sechs
Tagen unberührt im Eingang und ist keine Sichtung. Ich habe ihn nicht angefasst;
er gehört gelesen und entschieden, nicht weggeräumt.

### Abnahme

- Der Tagescheck läuft am 27.08. und meldet „eine offene Sichtung liegt
  bereits" — **kein** neuer Eintrag entsteht.
- Ein Blick in den Eingang am 28.08.: Es liegt weiterhin genau eine Sichtung da,
  nicht zwei. Dieser zweite Blick gehört ausdrücklich dazu; er ist die
  Gegenprobe gegen eine falsch gebildete Marke.
- `erledigen` wird einmal an der heutigen Sichtung erprobt: Der Eintrag landet
  in `abgelegt/` mit Vermerk, und der Tagescheck legt am Folgetag wieder einen
  neuen an.

### Was kann brechen und wer merkt es

- **Die Marke wird falsch gebildet** — dann entstehen entweder wieder täglich
  neue Einträge oder gar keiner mehr. Der zweite Fall ist der gefährlichere:
  Er sieht aus wie Ruhe. Merkt: der Blick in den Eingang am 28.08., deshalb
  steht er in der Abnahme.
- **`erledigen` räumt weg, ohne dass die Sichtung stattgefunden hat** — dann ist
  der Nachweis eine Lüge. Merkt: niemand. Gegenmittel: Der Ergebnisvermerk ist
  Pflichtfeld; ein Aufruf ohne Ergebnis wird abgewiesen.
- **`erledigen` bricht mitten im Verschieben ab** — der Eintrag wäre weg und
  nirgends verzeichnet. Merkt: niemand. Gegenmittel: erst schreiben, dann
  wegräumen, wie in `uebernehmen`.
- **Der Eintrag bleibt liegen, weil ich das Erledigen vergesse** — dann meldet
  der Tagescheck monatelang „eine offene Sichtung liegt bereits", und niemand
  stutzt. Merkt: vorerst niemand. Das ist die ehrliche Restlücke von C, und sie
  wäre einen späteren Wächter wert: eine Sichtung, die älter als drei Tage ist,
  gehört gemeldet.

---

## Auftrag 3 — Umlaute in ausgehenden Meldungen

### Lage

Der Tagescheck vom 27.08., 04:10 Uhr erreichte Adam mit „Anfuehrungspaar",
„faellig" und „schliessen". Der Text stammt nicht aus einer Chat-Antwort,
sondern aus zwei Skriptzeilen. Für Adam ist das ununterscheidbar.

**Der Grund, gemessen:** Weder `CLAUDE.md` noch `MIGRATION.md` noch
`SITZUNGSSTART.md` enthalten einen einzigen Treffer zur Umlaut-Regel. Sie steht
seit dem 28.07.2026 ausschließlich in Claudias Gedächtnis. Die Sitzungen mit
Schreibrecht kennen sie nicht.

### Zwei Handgriffe

**(1) Die beiden Meldungstexte berichtigen:**

| Datei | Zeile | ist | soll |
|---|---|---|---|
| `scripts/daily_check.sh` | 250 | `Auswertung faellig, danach Riegel bewusst neu setzen oder schliessen` | `Auswertung fällig, danach Riegel bewusst neu setzen oder schließen` |
| `scripts/test_blinde_flecken_b6.py` | 291 | `kein gemischtes Anfuehrungspaar in Zeichenketten (5x gebrochen)` | `kein gemischtes Anführungspaar in Zeichenketten (5x gebrochen)` |

Zeile 279 derselben Testdatei trägt denselben Begriff in der Begründung und
wandert mit.

**(2) Die Regel in `CLAUDE.md` eintragen**, im Abschnitt zu Sprache und Ausgabe:

> **Umlaute.** In allen Texten, die Adam erreichen — Meldungen des Tagenchecks,
> Postfach-Ansagen, Prüfzeilen-Titel, Fehlertexte —, stehen ä, ö, ü und ß
> direkt. Keine ASCII-Umschreibung. **Ausgenommen sind Bezeichner,
> Funktionsnamen und wörtliche Code-Zitate** (`_faellig`, `uebernehmen`) sowie
> Dateinamen — dort zeigte eine Korrektur auf etwas, das es nicht gibt.

### Kein Prüfer — ausdrücklich

Adam am 27.08., 07:03 Uhr: „Wir brauchen definitiv keinen Prüfer für eine
Umlautregel. Man kann es so übertreiben." Die Regel gilt durch Einhaltung, nicht
durch Kontrolle. Ein Prüfer über jede ausgehende Zeichenkette wäre teuer,
fehleranfällig an der Grenze zu Bezeichnern und würde den Tagescheck mit einer
weiteren täglichen Meldung belasten.

### Was brechen kann und wer es merkt

- **Eine spätere Sitzung schreibt wieder ASCII** — merkt: Adam, im Text. Das ist
  der bewusst gewählte Preis für den Verzicht auf einen Prüfer. Die Regel in
  `CLAUDE.md` ist das Gegenmittel: Sie wird vor jeder Arbeit gelesen.
- **Die Testdatei bricht durch die Änderung** — nein: Der Text ist reiner
  Anzeigetitel im `check()`-Aufruf, keine Vergleichsgrundlage. Gegenprobe beim
  Bau: Testlauf muss dieselbe Anzahl Zeilen liefern wie vorher.

---

## Rangfolge

0. Auftrag 3 zuerst — zwei Zeilen und ein Absatz, in Minuten erledigt.
1. Auftrag 1 sofort — unstrittig, klein, beendet das tägliche Rot.
2. Auftrag 2a zusammen damit — eine Zeile, hängt inhaltlich an 2b.
3. Auftrag 2b (1) und (3) sind klein und gehören in denselben Bau.
4. Auftrag 2b (2), die Funktion `erledigen`, ist der einzige echte Neubau
  darin — klein, aber neu. Sie darf nicht wegfallen: Ohne sie ist der Stapel
  nur eingefroren, nicht behoben.

Alles ist entschieden; es wartet nichts mehr auf Adam.
