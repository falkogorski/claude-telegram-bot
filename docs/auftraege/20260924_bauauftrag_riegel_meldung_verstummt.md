# Bauauftrag: Der geschlossene Riegel meldet keine abgelaufene Frist

**Zustand: gültig** · verfasst 24.09.2026 · Claudia → Engywuck → Mick
**Anlass:** Adam am 24.09.2026, 06:15 Uhr — „Wann fliegen diese Meldungen wieder
raus?" Die Antwort war: von selbst nie.

---

## Der Befund

Der Tagescheck meldet seit dem 10.09.2026 jeden Morgen rot:

> Frist abgelaufen: auftragsbuch-riegel.md galt bis 2026-09-09 — Auswertung
> faellig, danach Riegel bewusst neu setzen oder schliessen

**Die Auswertung hat längst stattgefunden.** Adams Entscheid vom 11.09.2026,
04:57 Uhr steht im Zettel selbst: Der Riegel **wird geschlossen** — zwei
Probezeiten, 14 Einträge, alle gelb, null Übergaben; dazu Engywucks Einwand, dass
jede Übergabe an Hora ein Modelllauf ohne Adams Hand wäre. Der Zettel trägt
seither `SCHARF: nein`.

**Warum der Melder trotzdem feuert:** `scripts/daily_check.sh` Zeilen 337 bis 343
sieht ausschließlich auf die Zeile `GILT-BIS`. Ob der Riegel scharf ist, prüft er
nicht. Ein geschlossener Riegel mit alter Frist erfüllt damit dauerhaft die
Bedingung „abgelaufen".

Im Protokoll steht die Meldung 20 Mal (die frühesten aus der ersten Probezeit
Ende August, als sie berechtigt war).

## Warum das mehr ist als Kosmetik

Eine rote Meldung, zu der es nichts zu tun gibt, kommt hier zum 15. Mal. Wer sie
zwei Wochen wegwischt, wischt irgendwann die eine weg, die zählt. Die Regel, dass
Adam nur erreicht, was ihn betrifft oder eine Entscheidung braucht, ist genau
dafür gemacht — hier verletzt der Wächter sie gegen seinen eigenen Zweck.

## Auftrag 1 — der Melder achtet auf den Riegelzustand

In `scripts/daily_check.sh` vor der Fristprüfung: Steht in der Datei **nicht**
`SCHARF: ja`, ist der Riegel geschlossen und **keine Frist kann ablaufen**. Dann
keine rote Meldung, sondern eine Zeile ins Protokoll — etwa
`✅ Riegel geschlossen (SCHARF: nein), Frist ohne Belang`.

Bei `SCHARF: ja` bleibt alles wie heute: am Stichtag die Vorwarnung, danach die
rote Meldung.

**Gegengeprüft, dass nichts aufgeht:** `auftragsbuch.py` Zeilen 67 und 68 sperren
bereits an `SCHARF: nein` und lesen das Datum danach gar nicht mehr. Am Verhalten
des Riegels ändert dieser Auftrag nichts — nur am Lärm.

## Warum nicht der scheinbar kürzere Weg

Die Fristzeile aus dem Zettel zu löschen wäre ein Handgriff, **bricht aber den
Regressionstest**: `scripts/test_auftragsbuch_b8.py` Zeile 331 verlangt
ausdrücklich, dass der Riegel ein Fristdatum nennt. Ein still fehlschlagender
Test für eine Aufräumarbeit ist der schlechtere Tausch. Die Zeile bleibt also
stehen, der Melder wird klüger.

## Auftrag 2 — Selbsttest

Zwei Fälle in den 4-Uhr-Check: Eine Riegeldatei mit `SCHARF: nein` und
abgelaufener Frist erzeugt **keine** rote Meldung; eine mit `SCHARF: ja` und
abgelaufener Frist erzeugt sie weiterhin.

## Was kann brechen und wer merkt es

| Bruch | Wer merkt es |
|---|---|
| Die Meldung verstummt künftig auch dort, wo sie nötig wäre | Selbsttest, Fall zwei (`SCHARF: ja` meldet weiter) |
| Jemand setzt den Riegel scharf und übersieht die abgelaufene Frist | Unverändert der Tagescheck — dieser Weg wird nicht angefasst |
| Die Fristprüfung läuft auch über `CLAUDE.md` (Zeile 310) | Dort steht kein `SCHARF`; nach dieser Änderung würde die Datei nie mehr melden. **Beim Bau entscheiden:** entweder die Riegel-Prüfung auf Dateien mit `SCHARF`-Zeile beschränken, oder Dateien ohne `SCHARF`-Zeile weiter wie bisher behandeln. Der zweite Weg ist der sichere |

## Reichweite über diesen Auftrag hinaus

Das Muster ist älter als dieser Fall: **Ein Wächter prüft eine Bedingung und
kennt den Zustand nicht, für den sie gedacht war.** Bei Gelegenheit lohnt ein
Durchgang über die übrigen roten Melder im Tagescheck mit einer Frage je Melder:
Gibt es einen Zustand, in dem seine Bedingung dauerhaft zutrifft, ohne dass es
etwas zu tun gibt? Jeder solche Melder wird binnen zwei Wochen ignoriert — und
dann fehlt er, wenn er recht hat.
