# Bauauftrag: Der Linktext gehört gesprochen

**Stichtag:** 2026-08-27 · **überholt durch:** — · **maßgeblich ist diese Datei**

## Änderungsverlauf

**2026-08-27 13:50** — erste Fassung, nach Adams Wahl „Variante 1" um 13:45 Uhr.

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau).

**Anlass:** Adam am 27.08.2026 um 13:22 Uhr. Die Sprachausgabe las den Satz „Im
[Prüfraster der Basisfähigkeiten](…) steht eine echte Lücke" als **„Im steht
eine echte Lücke"** vor. Sein Urteil: „Das hättest du mit vorlesen müssen, sonst
ergibt der Satz keinen Sinn." Um 13:45 Uhr hat er Variante 1 gewählt — Linktext
sprechen, Quellenhinweis einmal am Ende.

**Vorgeschichte, die zum Auftrag gehört:** Ich hatte Adam am selben Morgen um
09:11 Uhr das Gegenteil gesagt — die Sprachausgabe reduziere einen Link auf
seinen Text. Er hat seine bevorzugte Form auf dieser falschen Auskunft
aufgebaut. Die Form bleibt richtig; der Code muss nachziehen.

**Diese Sitzung hat kein Schreibrecht im Projektarchiv.** Alles hier ist
ausgearbeitet, nichts ist gebaut.

---

## Lage

In `bot.py` Zeile 10179 steht:

```python
text = re.sub(r"\[[^\]]+\]\([^)]*\)", "", text)
```

Der Ausdruck löscht **den gesamten Link samt Linktext**. Der Kommentar darüber
(Zeilen 10176 bis 10178) begründet das ausdrücklich damit, dass Quellen-Titel
den Sprachfluss stören. Der Selbsttest in Zeile 6908 zementiert es:

```python
assert "heise online" not in link, "Link-Label wurde nicht entfernt"
```

Die Annahme war, ein Linktext sei immer nur ein Quellenverweis am Satzrand. Sie
trifft nicht zu: Der Linktext ist häufig **satztragend** — ein Subjekt, ein
Objekt, ein Eigenname. Fällt er weg, bleibt ein Satzrumpf.

---

## Auftrag 1 — Linktext stehen lassen

**Stelle:** `bot.py`, Zeile 10179 samt Kommentar darüber.

**Neu:**

```python
# Markdown-Links [Titel](url): Die Adresse fliegt, der Titel bleibt stehen.
# Der Linktext ist oft satztragend — ohne ihn bricht der Satz mitten entzwei
# (Adam 27.08.2026: „Im steht eine echte Lücke").
text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
```

**Warum die Reihenfolge trägt und nichts nachgezogen werden muss:** Wikilinks
(Zeile 10175) sind vorher schon weg. Ist der Linktext selbst eine Adresse oder
ein Pfad, greifen die Regeln danach — nackte Adressen in den Zeilen 10183 und
10184, Pfade in Zeile 10187. Beide laufen **nach** dieser Stelle, also bleibt
kein Zeichensalat übrig.

---

## Auftrag 2 — Den Selbsttest umdrehen (Pflicht, nicht Kür)

**Stelle:** `bot.py`, Zeilen 6905 bis 6909.

Ohne diesen Handgriff schlägt der Vier-Uhr-Lauf ab dem nächsten Morgen fehl,
weil er das alte Verhalten erzwingt.

**Neu:**

```python
# Markdown-Links: Adresse raus, Linktext bleibt — er trägt oft den Satz
link = _strip_markdown_for_tts("Siehe [heise online](https://www.heise.de/news/x-123) dazu")
assert "http" not in link and "heise.de" not in link, "URL blieb"
assert "heise online" in link, "Linktext wurde verschluckt"
assert "Siehe" in link and "dazu" in link, "umgebender Text verloren"
```

---

## Auftrag 3 — Der Quellenhinweis, genau einmal je Nachricht

**Adams Wahl (Variante 1):** Am Ende der gesprochenen Nachricht steht einmal
„Die Quellen sind im Text verlinkt." — nicht an jeder einzelnen Stelle. Sein
Grund und meiner decken sich: Bei fünf Quellen wird ein Marker je Stelle zur
Litanei.

### Die Falle, die es hier zu umgehen gilt

**Der Satz darf NICHT in `_strip_markdown_for_tts` eingebaut werden.** Diese
Funktion läuft zweimal über denselben Text:

- Zeile 11073 im Sendepfad — **je Chunk**, nicht je Nachricht,
- Zeile 10686 in `_send_tts_chunk` — auf dem bereits gereinigten Text erneut.

Solange die Funktion nur entfernt, ist die Doppelung harmlos. Sobald sie etwas
**anhängt**, käme der Satz doppelt und zusätzlich nach jedem Teilstück.

### Die Stelle, die trägt

Im Sendepfad ab Zeile 11056, in der Schleife `while rest:`. Nur wenn zwei
Bedingungen zugleich gelten:

1. Es ist das **letzte** Teilstück (`rest` ist nach dem Zuschnitt leer),
2. der **Gesamttext** enthielt mindestens einen Markdown-Link.

Dann an `tts_clean` anhängen — **niemals an `chunk`**, denn `chunk` wird in
Zeile 11078 als Bildunterschrift gesendet. Der Satz gehört ins Ohr, nicht ins
Auge.

**Wortlaut nach Anzahl:** bei einem Link „Die Quelle ist im Text verlinkt.",
ab zwei „Die Quellen sind im Text verlinkt."

### Bewusste Grenze

Die übrigen Sendestellen (Startmeldung in den Zeilen 7960 und 7967,
Neustartmeldung in Zeile 8532, Vorlese-Pfad in Zeile 10617) bekommen den Hinweis
**nicht**. Dort stehen selten Links, und jede weitere Einbaustelle vervielfacht
die Doppelungsgefahr aus dem vorigen Abschnitt. Das ist eine Entscheidung, kein
Versehen — wenn dort später Links auftauchen, wird nachgezogen.

---

## Was kann brechen und wer merkt es

| Bruchstelle | Wer merkt es |
|---|---|
| Vier-Uhr-Lauf schlägt fehl, weil Auftrag 2 vergessen wurde | Der Tagescheck, am nächsten Morgen — laut |
| Der Hinweis kommt doppelt oder nach jedem Teilstück | **Niemand.** Adam hört es und muss es melden — deshalb Auftrag 4 |
| Linktext bleibt weiterhin verschluckt, weil nur der Test geändert wurde | Adam beim Hören, wieder |
| Der Hinweis landet in der Bildunterschrift statt nur in der Stimme | Adam beim Lesen |

Die stille Fehlerklasse ist die zweite: Ein doppelter Satz stürzt nichts ab und
steht in keinem Protokoll. Ohne Prüfer fällt er nur Adam auf — genau das soll
er nicht müssen.

## Auftrag 4 — Der Prüfer, der bisher fehlt

Ein Testfall im bestehenden TTS-Block, der beides absichert:

```python
# Quellenhinweis: genau einmal, und nur wenn ein Link da war
mit_link = _tts_mit_quellenhinweis("Siehe [Prüfraster](https://example.com/a) dazu")
assert mit_link.count("im Text verlinkt") == 1, "Hinweis fehlt oder kam doppelt"
ohne_link = _tts_mit_quellenhinweis("Ein Satz ganz ohne Verweis.")
assert "verlinkt" not in ohne_link, "Hinweis kam ohne Anlass"
```

Der Name der Hilfsfunktion ist ein Vorschlag; maßgeblich ist, dass die
Einmaligkeit **maschinell** geprüft wird und nicht an Adams Ohr hängt.

---

## Abnahme

Eine Antwort mit zwei Markdown-Links vorlesen lassen. Erwartet:

1. Beide Linktexte werden gesprochen, die Adressen nicht.
2. Am Ende steht genau einmal „Die Quellen sind im Text verlinkt."
3. Bei einer Antwort ohne Link fehlt der Hinweis vollständig.
4. Der Vier-Uhr-Lauf meldet am Folgetag grün.
