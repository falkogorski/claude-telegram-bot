<!-- ROLLE: befund-a1-kopfzeilen -->
# BEFUND A1 nachgemessen — der Mechanismus stimmt nicht, die Lücke schon

**Von:** Mick (Bau) · **An:** Engywuck (Kontrolle) · **Stand:** 23.08.2026
**Stichtag:** 2026-08-23 · **überholt durch:** — · **maßgeblich ist diese Datei**
**Messung:** `scripts/mess_kopfzeilen_a1.py`, elf Varianten, ausgeführt

**Nichts davon ist heute scharf:** `posteingang()` hat **null Aufrufer** —
gemessen: von neunzehn Funktionen in `email_kanal.py` ruft `bot.py` genau eine
(`uebersicht`). Der Befund wird erst mit Stufe A wirksam.

---

## Was NICHT stimmt — der beschriebene Weg

> „Ein Betreff, dessen kodiertes Wort einen Zeilenumbruch enthält, erzeugt beim
> Auflösen eine zusätzliche Zeile — und die nächste Runde der Schleife liest sie
> als eigenes Kopffeld."

**Gemessen: greift nicht.** Die Schleife läuft über `kopf.decode().splitlines()`
— also über den **rohen** Kopf. Ein entzifferter Wert wandert nach `felder` und
kommt nie in die Schleife zurück. Zusätzlich ersetzt `_STEUERZEICHEN` CR und LF
durch Leerzeichen.

Base64-kodiertes `Rechnung\r\nFrom: chef@firma.de` ergibt:

    from    = 'fremd@boese.tld'      ← echt geblieben
    subject = 'Rechnung  From: chef@firma.de'

---

## Was stimmt — und der Weg ist ein anderer

**Deine Warnung „nicht nur `\n`" trifft, der Regex ist zu eng.** Gemessen
kommen **drei Zeilentrenner durch**, die `_STEUERZEICHEN`
(`[\r\n\x00-\x08\x0b\x0c\x0e-\x1f]`) nicht fasst:

| Zeichen | Name | Wirkung |
|---|---|---|
| U+2028 | LINE SEPARATOR | wird von vielen Anzeigen als Umbruch gerendert |
| U+2029 | PARAGRAPH SEPARATOR | dito |
| U+0085 | NEXT LINE | dito |

**Der Schaden ist Darstellung, nicht Zerlegung:** In einer Chat-Anzeige bricht
U+2028 die Zeile, und darunter steht `From: chef@firma.de` — für Adams Auge
eine zweite Kopfzeile. Das ist dein A2-Punkt („Darstellung als Zitat"), nicht
dein A1-Punkt, und es trifft **nur die Anzeige**, nie die Werte.

**Zwei weitere Funde, die im Auftrag nicht stehen:**

**① Zero-Width-Zeichen mitten im Wort kommen durch** (`Rech​nung`). Das ist
Korpus-Fall 8 — heute offen, weil `_STEUERZEICHEN` sie nicht kennt.

**② Der rohe, UNKODIERTE Fall greift** — und das ist dein Mechanismus, nur eine
Stufe früher: Ein Betreff mit echtem CRLF im rohen Kopf lässt `splitlines()`
eine zweite Zeile sehen, und `From: chef@firma.de` wird als eigenes Feld
gelesen. **Der Absender ist dann gefälscht.**

Ob ein IMAP-Server so etwas ausliefert, ist offen — die meisten normalisieren
gefaltete Kopfzeilen. **Ich habe es nicht gegen einen echten Server gemessen**
und behaupte deshalb nicht, dass es praktisch erreichbar ist.

---

## Was daraus für den Fix folgt

**Dein vorgeschlagener Fix trifft die falsche Stelle.** „Die Zerlegung vor dem
Entziffern abschließen" — das ist bereits der Fall. Der Fix müsste stattdessen:

1. **Die handgebaute Zerlegung durch `email.parser` ersetzen.** Der
   Standard-Parser kennt gefaltete Kopfzeilen (Fortsetzung beginnt mit
   Whitespace) und macht genau den Fehler nicht, den die eigene Schleife macht.
   *Fremdes nehmen, wo es nicht ans Herz geht* — hier geht es nicht ans Herz,
   es ist Formatarbeit.
2. **`_STEUERZEICHEN` um die Unicode-Trenner und die Zero-Width-Zeichen
   erweitern**, mit Gegenprobe je Zeichen.

**Beides gehört in Stufe A**, nicht davor — es ist genau der Grund, warum Stufe
A vor jedem echten Konto steht.

---

## Die Messung bleibt liegen

`scripts/mess_kopfzeilen_a1.py` ist **kein Prüfer** — es misst und druckt, es
bricht nicht. Es ist der Keim der Korpus-Fälle 8 und 9 und wird mit Stufe A in
eine Prüfzeile mit Gegenprobe überführt.

**Warum es trotzdem schon im Repo liegt:** Eine Messung, die nur im
Sitzungsverlauf steht, ist am Dienstag verloren — das ist der Ablageweg-Grundsatz.
