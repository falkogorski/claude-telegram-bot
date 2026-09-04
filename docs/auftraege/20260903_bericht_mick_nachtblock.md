> **Zweck: WEITERGABE → Engywuck** · **Zu tun:** lesen. Zwei Stellen brauchen
> deinen Blick (unten markiert), der Rest ist Bericht.

# Bericht — Nacht zum 03.09.2026

**Stichtag:** 03.09.2026, 01:41 · **Stand:** `064a062`, gepusht
**Läufe:** 72/72 · Zielumgebung 41/43 (2 übersprungen, benannt)
**Nenner:** Nachtblock 6 von 6 · deine drei Zusagen 3 von 3 · dazu Adams
Rechnung und der Umzug, beides nicht im Auftrag · **0 Deploys**

---

## Nachtblock — sechs von sechs

**N-1 Freigabe-Erinnerungen.** Frist 60 min, Erinnerung nach 15/30/45, jede als
Reply auf die Anfrage. Wartezeit in Abschnitte geteilt, kein Zeitgeber. Die
Schleife ist aus dem Rückruf **herausgezogen** (`warte_auf_freigabe`) — mitten
darin war sie nur mit laufendem Bot messbar. `asyncio.shield` ist Pflicht: ohne
stirbt der Prüfstand sofort, Adams Knopfdruck liefe ins Leere.

**Der Prüfstand fand drei eigene Fehler:** ein Fließkomma-Rest (`2.7e-17 > 0`)
ließ einen Abschnitt zu viel laufen · ein werfender Erinnerer riss die Anfrage
mit · eine Prüfzeile stolperte über ihren **eigenen Erklärkommentar**, der die
alte Zahl zitiert.

**N-2 Freigabedialog deutsch.** Satz „was geschieht" aus `tool_name` und Pfad —
**nie** aus `description`; das ist die Sicherheitsgrenze und die wird
ausgeführt gemessen. Grund wird ergänzt, nie ersetzt. Quittung im Partizip.
Eine bestehende Zeile **umgestellt statt aufgeweicht**: „Fremdtext baut den
Dialog nicht um" verlangte `len(kopf) == 2` — die Zahl war die Umsetzung der
Zusage, nicht die Zusage. Sie misst jetzt den Unterschied zum Aufruf ohne
Fremdtext.

**N-3/N-4.** ✈️ statt ⚡ (dreifach belegt), Alt-Beschriftung als Alias in
Menge **und** Handler, Stichpunktliste, Umlaute. Der Umlaut-Prüfer **existierte
und erreichte die Stelle nicht** — Meldungstexte sind jetzt Modulkonstanten,
damit der vorhandene Prüfer sie sieht. **Die Wortliste führte `aendern`, und
`aendert` enthält das nicht** — genau Adams drei Wörter fehlten. Jetzt Stämme.

**N-5/N-6.** Ablage, Aufschiebe-Knopf als Gedanke (kein Bau), fünf Blaupausen.
Die vier roten Prüfstände waren nachmittags erledigt; der Rest — Pfad-Prüfer
auf `~/Projects` und Pfade mitten in Zeichenketten — kam dazu, Gegenprobe nach
deiner Vorgabe gefahren.

## Deine drei Zusagen — drei von drei

**Z-1** Meldung nach der Ablage über das Postfach (nur bei `_tief > 0`) +
Alterszeile im Tagescheck. Vier Lagen gemessen. **Das Alter wird gestaffelt,
nicht gerechnet** — `find -printf`/`stat -c %Y` sind GNU-eigen, scheiterten am
Mac still und meldeten „seit 20698 Tagen".

**Z-2** `~/workspace` und `~/postfach` als Bäume, Ausschlüsse statt
Einschlüsse. **Dieselbe Falle noch einmal:** `--exclude='.venv'` maß 1,1 GB und
14.343 Dateien, weil `~/workspace/.nemo-test/` eine Python-Umgebung mit anderem
Namen ist. Auf `site-packages` umgestellt → **393 Dateien, 174 MB.**

**Z-3** `docs/entscheidungsvorlagen/ablage_auf_dem_server.md`, kein Bau. Drei
Wege, die drei unbezifferten Kostenpunkte benannt, Ultracode-Prüfstelle
genannt. Empfehlung: Weg ① wenn überhaupt — **ehrlicher: noch nicht jetzt**,
mit der Bedingung dabei, woran erkennbar wäre, dass es so weit ist.

## Nicht im Auftrag, aber Adams Nacht

**017-26 und die Aufstellung liegen fertig in iCloud** (1.404,80 €, Datum
03.09., Ziel 10.09.). Aus Claudias Daten, nichts neu konstruiert. Adams
Korrekturen alle drin: Sammelposition, kein Verweis aufs Beiblatt, keine
Referenzzeile, keine Personen-Klammer, Spesen mit Prozent, LKW-Rabatte
ausgewiesen.

**Der Umzug ist durch** (Schritte 2–4, kein root). **Der Vergleichslauf hat
sich gelohnt:** Der Dienst-PATH kennt `~/.local/bin` nicht — gelöst im
Generator statt am Dienst. Und Helvetica **und** Arial fehlten; typst setzte in
Serifen. Liberation Sans als dritter Name, im Bild nachgemessen.

**`RECHNUNGSREGELN.md` liegt im Rechnungsprojekt** — Adams Frage *„gelten die
dann genauso für Claudia?"* war die wichtigste des Abends. Zehn Regeln, die
sonst mit dieser Sitzung gestorben wären. **Ergänzt, ersetzt nichts** (seine
Auflage).

---

## 🔴 Zwei Stellen für deinen Blick

**① Mein eigener Fehler, vom Prüfer gefangen, während ich ihn erklärte.** Ich
schrieb `${RECHNUNGEN_AUSGANG:-$HOME/...}` in `daily_check.sh` — zwei Zeilen
unter `BOTHOME=/home/claudebot`, wo der Vorfall vom 29.07. im Kommentar steht.
Die Zielumgebung meldete es sofort. Behoben, aber die Frage bleibt: **Wie oft
schreibt jemand `$HOME` in eine Datei, die es ausdrücklich verbietet?** Ein
Prüfer über alle Betriebsskripte existiert und hat gegriffen — dieser Fall ist
also gedeckt. Ich nenne ihn, weil er die Klasse belegt.

**② Die Spesen-Staffelung ist bei Adam, nicht entschieden.** Aktuell 50/80/30 %
auf die volle Tagespauschale (14,00 · 22,40 · 8,40). Er hat selbst gesagt:
*„streng genommen müsstest Du mich so was abfragen."* Steht als offene Frage in
`RECHNUNGSREGELN.md`, nicht geraten.

## Klein und offen

Fußnote „LKW-Sätze wie besprochen" — das Aufstellungs-Template kennt kein
Bemerkungsfeld · die übrigen Verben der Umlaut-Liste stehen als Vollform
(Konvergenz-Bremse, bewusst nicht angefasst) · F-21 (`echo` in zwei Listen) ·
`git init` im Rechnungsprojekt liegt bei Adam.

**Deploy:** liegt bei Adam, **mit Neustart** — Produktivcode dabei.
