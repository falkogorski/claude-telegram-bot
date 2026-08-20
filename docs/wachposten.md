<!-- ROLLE: wachposten-doku -->
# Der Log-Wachposten — was er meldet und was nicht

**Stichtag:** 2026-08-19 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile im Drehbuch**

Ein deterministischer Posten auf dem VPS. Er liest alle fünf Minuten die neuen
Zeilen der Protokolle, prüft sie gegen eine feste Musterliste und legt
Auffälliges ins Boten-Postfach. **Kein Modell im Pfad, Kosten null** — das war
die Bedingung, unter der er überhaupt gebaut wurde (Modell-Wachen ist
AGB-Grauzone).

**Er urteilt nicht, er zeigt.** Adams Fingertipp weckt dann Engywuck.

## Was er liest

| Quelle | Schwelle | Standard |
|---|---|---|
| `logs/bot-errors.log` | **jede neue Zeile** | immer an |
| `logs/conversations/<heute>.md` | nur bei Musterfund | **aus** |

**Warum die Schwelle je Quelle verschieden ist** — gemessen am 19.08. an
echten Daten: Die reale Zeile `postfach send | TimedOut: Timed out` traf kein
einziges Muster. Das war kein Musterfehler, sondern ein Denkfehler. **In einer
Fehlerdatei ist jede neue Zeile bereits der Befund**; dort nach Fehlermerkmalen
zu suchen hieße zu prüfen, ob ein Fehler auch wirklich einer ist. Im Gespräch
ist es umgekehrt — fast alles ist harmlos, erst ein Muster macht auffällig.

**Die Gesprächsprotokolle stehen auf AUS.** Sie sind das, was Adam privat
schreibt; der Schalter (`WACHPOSTEN_GESPRAECHE=ja`) ist seine Entscheidung,
nicht meine. Ohne ihn ist der Posten auf technische Fehler beschränkt — und die
sind sein eigentlicher Zweck.

## Was er meldet

Sechs Kategorien, in `wachmuster.py` als **eine Quelle** (Vorbild
`authmarke.py`): Absturz · Fehlerzeile · Anbieter-Störung · Kosten-Wörter ·
Geheimnis-Wörter · offene Freigabe-Anfragen.

Alle Muster haben **beidseitig offene Wortgrenzen** — deutsche
Zusammensetzungen hängen ihr Bestimmungswort vorn an, das Grundwort steht
hinten; `\bkosten\b` verfehlt „Zusatzkosten" ebenso wie „Kostenstelle". Der
Preis sind Fehlalarme, und die fängt eine **kurze, ausdrücklich benannte**
Ausnahmeliste ab („kostenlos", „Tokenizer", …). Eine lange Ausnahmeliste höhlt
die Wache aus.

## Was er ausdrücklich NICHT meldet — und warum sichtbar

**Bei Ampel-ROT wird kein Wortlaut zitiert.** Nur Quelle, Zeit und das
Kategorien-Label gehen hinaus, dazu der ausdrückliche Hinweis, dass der Text
zurückgehalten wurde.

Der Grund ist ein Zielkonflikt, den Engywuck am 18.08. entschieden hat: Die
Wortlaut-Regel verlangt, die beanstandete Zeile zu zitieren statt eine Ursache
zu vermuten (Lehre aus Horas Halt). Die Gatekeeper-Regel verlangt, rote Inhalte
nicht über Telegram zu tragen, das nicht Ende-zu-Ende verschlüsselt ist.
**Beide haben recht.**

Drei Auflagen dazu:

- **Nur Rot wird zurückgehalten** — Gelb und Grün gehen im Wortlaut hinaus.
- **Ein Einstufungs-Ausfall zählt als Rot.** Wer im Zweifel öffnet, sichert
  nichts.
- **Nur das Kategorien-Label, nie das Muster.** `classify()` liefert
  `{color, rules, matches}` — `matches` enthält die **Treffer selbst** und
  berührt die Meldung nie. Sonst zitierte sie genau das Wort, das sie
  zurückhält.

**Sichtbar zurückgehalten ist ehrlich und sicher; lautlos zurückgehalten wäre
die nächste Stille, die wie Ruhe aussieht.**

Kein Sicherkanal in v1 — als **[später prüfen]** in der Auswertung vermerkt,
damit aus „für jetzt" nicht stillschweigend „für immer" wird.

## Zwei Fassungen: ein Satz für Adam, die Einzelheiten fürs Archiv

`[NEU 2026-08-20, A4]` **Der Posten wurde für Engywuck und Mick gebaut,
schreibt aber an Adam.** Dessen Urteil vom 20.08., 01:18: „böhmische Dörfer" —
und er hat recht. Zeilenzitate, Dateipfade und englische Fehlertexte sagen ihm
nichts.

**Was Adam bekommt:** einen deutschen Satz. Wie viele Einträge, aus welcher
Quelle in Alltagssprache, **ob es heikel ist**, und dass die Einzelheiten
festgehalten wurden. Beispiel: *„Mir ist etwas aufgefallen: 2 neue Einträge in
der Fehlerdatei. Nichts davon ist als heikel eingestuft. Die Einzelheiten habe
ich für Engywuck festgehalten."*

**Was ins Archiv geht** (`logs/wachposten-archiv.log`): die vollständige
Fassung mit Fundstelle, Zeilennummer und Wortlaut — genau wie bisher. Der
Kurier trägt die Datei mit; **ohne diese Ergänzung wäre A4 halb gebaut
gewesen**, denn das Archiv erreichte niemanden.

**Zwei Dinge stehen in BEIDEN Fassungen**, und beide aus einem Grund:
- Die **Ampel-Einstufung in einem Wort** — ohne sie kann Adam nicht ableiten,
  ob es dringend ist, und eine Kurzfassung, aus der das nicht hervorgeht, hat
  ihren Zweck verfehlt.
- Die **Zählzeile des Dämpfers** — was er zurückhält, ist nach dem Wandern des
  Lesestands endgültig fort; sie ist die einzige Spur davon.

**Die Kurzfassung zitiert nichts** und ist damit bei roten Inhalten automatisch
auf der sicheren Seite.

## Die Schaltfläche an der Meldung

Jede Meldung trägt eine Schaltfläche **📌 Befund hinterlegen**. Ein Tipp legt
den Befund ins Auftragsbuch — **deterministisch, ohne Modellstart** — und
bestätigt es in derselben Nachricht.

**Warum es sie gibt.** Bis zum 20.08. endete jede Meldung mit „Engywuck
wecken?". Adams Daumen darauf blieb wirkungslos: Der Postfach-Versand
registriert keine offene Frage, also griff die stille Quittung — ein Häkchen,
kein Lauf. Daraus wurde Adams Regel: *Eine Frage nur, wenn sie im Chat
beantwortbar ist und die Antwort wirkt.* Die Schaltfläche ist diese Wirkung;
die Meldung fragt seither nicht mehr, sie **bietet an**.

**Der hinterlegte Auftrag ist gelb, nicht grün** — und das ist keine
Nachlässigkeit, sondern der Punkt: Adam stimmt dem **Hinterlegen** zu, nicht
dem Bauen. „wachposten-befund" steht bewusst nicht in der geschlossenen
Grün-Liste, also legt das Auftragsbuch ihn zur Vorlage. Über das Ausführen
entscheidet Engywuck.

**Zwei Riegel gegen Doppel-Einträge:** Der Knopf verschwindet nach dem Tippen,
und der Eintrag trägt eine Marke aus der Befund-Kennung, gegen die ein zweiter
Versuch geprüft wird. Der zweite Riegel ist der doppelte Boden — ein Knopf, der
stehen bleibt, lädt zum zweiten Tippen ein.

**Die Kennung hängt am Befund, nicht an der Zeit.** Trüge sie einen
Zeitstempel, wäre derselbe Befund nach einem Neustart eine andere Sache und der
Dublettenschutz liefe leer — dieselbe Lehre wie beim Dämpf-Schlüssel (28.07.).

**Erlaubte Knopf-Arten sind eine geschlossene Liste** (`botenpost.KNOPF_ARTEN`).
Der Postfach-Ordner wird von mehreren Skripten beschrieben; ohne diese Prüfung
könnte jedes davon eine beliebige Schaltfläche in Adams Chat setzen. Fällt eine
Art durch, geht die **Nachricht trotzdem hinaus, nur ohne Knopf** — ein
Meldeweg darf an einem Zierrat nicht scheitern.

## Wie er sich dämpft

Dieselbe Kennung frühestens nach einer Stunde erneut, höchstens fünf Zeilen je
Meldung. Gedämpft wird über die **Kennung**, nie über den Text: Am 28.07.
hebelte ein Zeitstempel im Befundtext den Dämpfer aus — „seit 9 Min" gegen
„seit 10 Min" galt als neuer Befund **und** als weggefallener, und der Dämpfer
verdoppelte den Lärm, statt ihn zu dämpfen.

Zusätzlich gilt die Postfach-Obergrenze von sechs Nachrichten je Absender und
Stunde.

## Was passiert, wenn er selbst stolpert

**Ein unlesbarer Merkzettel wird gemeldet, nicht verschwiegen** — er liest dann
von vorn und sagt das. Lehre des Versions-Monitors: Dort legte ein kaputter
Zeitstempel einen Eintrag dauerhaft still, während das Protokoll „vor 0 Tagen
gesehen" meldete.

**Eine Ausnahme ist ein Befund, kein Abbruch.** Bricht er bei einer Quelle ab,
bleiben die übrigen ungelesen — deshalb wird der Lesefehler selbst zum Befund.

Über ihn wacht die Zeitgeber-Wache des Tagescheck; sie erfasst seinen Timer,
weil sie nach dem Ziel sucht, nicht nach dem Namen.
