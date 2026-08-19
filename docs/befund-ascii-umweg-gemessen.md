<!-- ROLLE: befund-ascii-umweg -->
# Befund: Der ASCII-Umweg im Postfach existiert nicht — und war nicht die Bruchursache

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich ist diese
Datei** · **Anlass:** Engywucks Auftrag ⑤ vom 20.08. („Umweg messen; wenn er
noch existiert, entfernen") · **Grundlage:** Claudias Nebenfund im
Wachposten-Dämpfer-Befund

## Das Ergebnis in einem Satz

**Beide Hälften der Annahme haben der Messung nicht standgehalten:** Einen
ASCII-Umweg gibt es im Code nicht, und der Auftrag vom 27.07. ist auch nicht
daran zerbrochen.

## Was gemessen wurde

**① Schreibt irgendein Pfad ASCII-umschrieben?** Nein. Jede Stelle, die eine
Auftrags- oder Postfachdatei schreibt, setzt ausdrücklich `ensure_ascii=False`
— `botenpost.legen()` (Zeile 94) ebenso wie Hora, Stundenblume, Updater,
Wartungsfenster, Versions-Monitor und der Wachposten selbst. Eine Umschreibung
von Umlauten findet sich im gesamten eigenen Code **nirgends**.

**② Überlebt schwieriger Text den Weg?** Ja. Gegenprobe mit genau den Zeichen,
die am 27.07. beteiligt waren — Umlaute, typographische Anführungszeichen,
Gedankenstrich, und ausdrücklich das **gemischte Paar** aus `„` und `"`:

```
geschrieben: {"text": "gültige Anführungszeichen: „so\" und ähnlich – prüfe"}
gelesen    : gültige Anführungszeichen: „so" und ähnlich – prüfe
```

Unbeschadet. Das gerade Anführungszeichen wird korrekt maskiert.

## Woran der Auftrag wirklich zerbrach

Die Datei `~/postfach/failed/1785146271313508170.json` (667 Zeichen) bricht bei
**Zeichen 369** mitten im Wort „gültige":

```
... oft die guelt", "ige), ziehe die Querverweise nach ...
```

Das ist kein Zeichensatz-Problem. Dort steht ein **Einschub `", "` inmitten
einer Zeichenkette** — die Signatur eines Textes, der beim Schreiben
**gesplittet und wieder zusammengesetzt** wurde. Entfernt man genau diesen
Einschub, lädt die Datei fehlerfrei; beide Schlüssel (`target_chat_id`, `text`)
sind vollständig da.

**Der Kopf derselben Datei widerlegt die ASCII-These zusätzlich:** Er lautet
*„Verstanden, Adam — ich stelle das jetzt um."* — mit Gedankenstrich. Die Datei
ist **teils** umschrieben („Datumspraefix", „pruefe"), teils nicht. Ein
maschineller Umweg wäre durchgängig gewesen. Es war Handarbeit.

## Die eigentliche Lehre

**Die Datei wurde nicht über `botenpost.legen()` gelegt, sondern von Hand
geschrieben.** Wer den Weg benutzt, kann diesen Fehler nicht machen —
`json.dumps` bricht keine Zeichenketten um. Wer die Datei direkt schreibt,
umgeht damit auch die einzige Stelle, die für ihre Wohlgeformtheit einsteht.

Das ist **dieselbe Familie** wie die Heredoc-Regel in `CLAUDE.md`: Ein
Werkzeug, das den Text zwischen die Finger nimmt, verdirbt ihn irgendwann —
und der Schaden zeigt sich nicht dort, wo er entsteht.

**Kein Handgriff nötig.** Es gibt nichts zu entfernen. Die Auflage lautet
stattdessen: **Auftrags- und Postfachdateien werden ausschließlich über
`botenpost.legen()` erzeugt**, nie von Hand und nie über einen Heredoc.

## Was der Fall über die Meldekette sagt

Der `JSONDecodeError` **wurde** protokolliert — am 27.07. um 11:58 in
`bot-errors.log`. Er stand dort **vierundzwanzig Tage**, ohne dass ihn jemand
las, und mit ihm die Spur zu einer Ansage an Adam, die nie ankam.

Die Kette hat also funktioniert und trotzdem versagt: **Protokollieren ist
nicht Melden.** Genau diese Lücke schließt der Log-Wachposten — er hat die
Zeile am 19.08. als erste überhaupt sichtbar gemacht. Der Fall ist damit weniger
ein Defekt als der **Beleg, wofür der Posten gebaut wurde**.
