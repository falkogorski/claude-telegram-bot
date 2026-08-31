# Auftrag an Mick — eine Messung und drei Nachträge (aus Blöcken 7 und 8)

**Nichts davon ist ein Bauauftrag.** Eine Messung, drei Ablage-Nachträge von
Adams eigenen Worten. Wenn eine Zeile hier nach Bauen klingt, ist sie falsch
formuliert — dann bitte zurückfragen statt bauen.

---

# Teil 1 — Messung: was steht wirklich im Bot-Gedächtnis?

**Stichtag:** 31.08.2026, 22:30 MESZ · **Von:** Engywuck (Kontrolle)
**Aufwand:** wenige Minuten · **Es wird nichts gebaut und nichts geändert.**

---

## Warum

Die Gesamtprüfung der Bot-Protokolle ist bei Block 8 von 18. Aus den Blöcken 7
und 8 (beide 26.07.) sind **sechs Verhaltensregeln und Vorlieben** aufgelaufen,
die Adam ausdrücklich zum Merken gegeben hat. **Keine davon ist im Repo
auffindbar** — weder im Systemprompt noch im Drehbuch noch in `CLAUDE.md`.

Sie liegen mit hoher Wahrscheinlichkeit im **Bot-Gedächtnis** (`_MEMORY_DIR`,
`bot.py:563`) — und genau das ist von hier aus nicht einsehbar. In einem Fall
hat der Bot Adam sogar geantwortet: **„Steht drin, bei allen Themen, nicht nur
den technischen."** Ob das stimmt, kann ich nicht messen. Du kannst.

---

## Die Messung

```
ls -la "$CLAUDE_MEMORY_DIR"        # bzw. der auf dem VPS gesetzte Pfad
cat "$CLAUDE_MEMORY_DIR/MEMORY.md"
```

Dann in **allen** Dateien dort nach den sechs Punkten suchen. Bitte nach der
**Sache** suchen, nicht nach Adams Wortlaut — das war mein eigener Fehler bei
5.26 und hat einen Fehlbefund erzeugt:

| Nr. | Die Sache | Suchrichtung (Beispiele) |
|---|---|---|
| 1 | Ansage zuerst, ungebündelt | `dauer`, `zuerst`, `vorab`, `bündel` |
| 2 | Zügig antworten als Grundregel | `zügig`, `schnell`, `antwortzeit`, `dialog` |
| 3 | Erst nachschauen statt fragen | `nachschau`, `bereits`, `schon mal`, `vorher prüf` |
| 4 | …und zwar bei **allen** Themen | `alle Themen`, `nicht nur` |
| 5 | Keine Markdown-Listen, PDF reicht | `markdown`, `pdf`, `liste` |
| 6 | „Ich bin meine Wahrheit" | `wahrheit` |

## Was ich zurückbekommen möchte

**Nur eine Tabelle: Nummer · steht drin (ja/nein) · Datei · die gefundene Zeile.**
Keine Bewertung, keine Nacharbeit, kein Eintrag ins Drehbuch. **Nichts ändern** —
weder im Gedächtnis noch im Repo.

**Falls etwas fehlt: bitte NICHT nachtragen.** Ob und wo Verhaltensregeln einen
Ort im Repo bekommen, ist Adams Entscheidung — meine Empfehlung an ihn lautet
*Spiegel im Drehbuch, Gedächtnis bleibt die wirksame Stelle*, aber zwei Stellen,
die beide gelten, wären der schlechtere Zustand als eine.

---

## Der Grund, warum das über eine Einzelfrage hinausgeht

Das Gedächtnis ist eine **Fremdfläche** in Connis Sinn: außerhalb beider Repos,
ohne Historie, ohne Wächter — und **es kann darin nichts fehlen, weil niemand
eine Sollliste hat.** Eine Regel, die bei einem Neuaufsetzen nicht mitkommt,
verschwindet ohne Meldung.

Diese Messung erzeugt zum ersten Mal ein Stück Sollliste. Mehr soll sie nicht.

---

# Teil 2 — Drei Nachträge in die Ablage

**Herkunft: Adams Wortlaut vom 26.07.2026**, aus den Bot-Protokollen gelesen.
**Keine Ableitung, keine Auslegung** — das Datum steht jeweils dabei, damit
sichtbar bleibt, dass es über einen Monat alt ist.

## N-1 · Adams Auflage an das Zusatzguthaben

**Ziel:** `docs/entscheidungsvorlagen/kontingent-fallback-ebene2.md`, an
**Weg E — Zusatzguthaben** (heute neutral in der Fünfer-Tabelle).

**Adam am 26.07., 15:33 (Wortlaut):**
> *„Das wäre natürlich ein wichtiger Punkt. Das zu wissen. Und wenn man das
> nicht weiß, kann man damit halt so … natürlich nicht arbeiten. Das heißt,
> man muss es deaktiviert lassen. Nur als Notfall einschalten sozusagen."*

**Was einzutragen ist:** Weg E trägt eine **Auflage Adams vom 26.07.** —
deaktiviert lassen, nur als Notfall einschalten. **Begründung mit aufnehmen,
sie ist der Wert:** *weil nicht sichtbar ist, wann der Zukauf greift.* Ein
Ausweichweg, dessen Greifen man nicht sieht, ist nicht benutzbar.

## N-2 · Die 💰-Auflage „laufende Prozesse stoppen" an Weg A und E

**Ziel:** dieselbe Vorlage, an **Weg A (API-Zweitweg)** und **Weg E**.

**Adam am 26.07., 15:11 (Wortlaut):**
> *„Das halt laufende Prozesse, die … größeres Kontingent verbrauchen,
> möglichst automatisch gestoppt werden … weil das dann schlicht einfach nur
> das Geld verpulvert."*

**Der Unterschied zu 5.31, und er ist der Punkt:** Für **Ebene 1** ist das
erfüllt — der Auftrag geht zurück in die Warteschlange, der Worker schläft.
Solange nur pausiert wird, kostet Weiterlaufen nichts. **Sobald ein bezahlter
Topf dahinterliegt, läuft die Uhr mit Geld** — und dafür steht die Auflage
nirgends. Sie gehört an die Wege, nicht in einen Bauauftrag.

## N-3 · Adams GPS-Gedanke, ausdrücklich zum Festhalten gegeben

**Ziel:** wohin, ist eine Entscheidung, keine Ableitung — **bitte Adam fragen
oder in die Fundliste für 10.1**, nicht selbst eine Nummer vergeben.

**Adam am 26.07., 22:35 (verkürzt, Bedenken im Wortlaut):**
> *„Es gibt doch bestimmte Möglichkeiten GPS einzubinden … Das ist allerdings
> ein sehr kritisches Ding, weil das ist für mich eine superrote
> Datenschutzampelgeschichte, ich will ja eigentlich nicht getrackt werden …
> Das müsste dann halt im eigenen KI-Universum bleiben … Das ist ein Gedanke,
> den mal festhalten bitte."*

**Der Anlass gehört dazu:** Der Bot rechnete Adams Wegzeiten falsch, weil er
nicht weiß, wo Adam ist. Adam dazu: *„Ich lebe halt eben nicht so getaktet
nach Zeit. Ich lebe nach einem inneren Tag."*

**Gemessen:** `gps`, `standort`, `ortung` kommen in `MIGRATION.md` und in
`docs/` **nicht vor**. Die einzigen Treffer betreffen die *Selbstverortung des
Bots* (Mac vs. VPS) — ein anderes Thema.

**Wichtig: Der wertvolle Teil sind seine Bedenken, nicht die Idee.** *„Der
Mensch selber entscheidet, was er teilen möchte und was nicht"* ist Material
für die Werte-Charta. Bitte den Gedanken **mit** der roten Ampel festhalten,
nicht ohne.

---

# Was ausdrücklich NICHT in diesem Auftrag steht

Der Prüfbericht zu Block 7 und 8 geht an **Adam**, nicht an dich. Er enthält
Lücken-Befunde, und Lücken-Befunde sind **keine Bauaufträge** — genau daraus
sind in zwei Nächten zwei schädliche Aufträge von mir entstanden. Wenn du
wissen willst, woher N-1 bis N-3 kommen: frag mich über Adam, statt es dir
aus dem Bericht zusammenzusetzen.

**Der Regressionslauf gilt auch hier** — auch für reine Doku-Commits. Das ist
deine eigene Lehre vom 23.08.
