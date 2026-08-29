# LETZTER RUN vor dem Einfrieren — drei Dinge, sonst nichts

**An:** Mick · **Von:** Engywuck · **Stand:** 25.08.2026, 05:34 MESZ · HEAD `e9dfa07`
**Lage:** Adam friert ein und ist ~3 Tage weg. **Das ist dein letzter Zug.**
**Gut genug wenn:** Der Anführungsprüfer meldet nur noch echte Stellen, die
Betriebslage steht mit benannten eingefrorenen Fixes, und der Regressionslauf
ist grün oder sein Rotstand ist dokumentiert.

---

## ① Der Fragment-Fix — der einzige Bau, und er ist dringend

**Warum ausgerechnet der:** Der Anführungsprüfer ist **jetzt scharf und laut
falsch** — 64 Meldungen für 32 korrekt gepaarte Zeilen (meine Messung, Datei
`gegenpruefung-anfuehrungspruefer.md`). Drei Tage lang ist der Regressionslauf
rot aus einem Grund, der nicht stimmt. **Ein Wächter im Dauer-Fehlalarm ist
schlimmer als kein Wächter**: Er gewöhnt den nächsten Leser an Rot, und er lädt
dazu ein, 32 korrekte Stellen „zu reparieren".

**Was zu bauen ist:** Die `FSTRING_MIDDLE`-Stücke zwischen `FSTRING_START` und
`FSTRING_END` **sammeln und verketten**, erst den zusammengesetzten Text auf
Ausgewogenheit prüfen. Ein Stapel über die f-String-Verschachtelung, wie du ihn
im Zerleger schon gebaut hast — *ein Fragment bildet Verschachtelung nicht ab*,
dieselbe Lehre, andere Stelle.

**Die Abnahme, ohne dass du eine zweite Python-Version brauchst** — als
ausgeführte Gegenprobe, nicht als Zusage:

1. Eine Wegwerf-Datei mit **zwei** Zeilen prüfen lassen: `f'Haus „{x}“ da'`
   (korrekt gepaart, **darf nicht** gemeldet werden) und `f'Haus „{x}" da'`
   (gemischt, **muss** gemeldet werden). Beide Richtungen laufen lassen.
2. Danach über den Bestand: **keine gemeldete Zeile darf als ganzes ausgewogen
   sein.** Das ist die Zusicherung, nicht eine Zielzahl — eine Zahl würde beim
   nächsten Commit veralten.
3. **Die Doppelmeldung muss weg.** `hora.py:628, hora.py:628` war die Signatur
   des Fehlers; steht sie noch da, ist der Fix nicht fertig.

**Nicht** die fünf echten Stellen reparieren. Die sind Handarbeit für den
nächsten Block, und um halb sechs vor einer Abreise wird daraus ein Fehler.

## ② Die Betriebslage eintragen — Pflicht, nicht Kür

`CLAUDE.md` verlangt die Vorlage **mit** der Zeile über eingefrorene
Wächter-Fixes. Das ist die Lehre aus dem 29.07.: Damals lag ein fertiger
Wächter-Fix ungedeployt, sein Wächter starb, und es fiel einundzwanzig Tage
nicht auf — **weil ausgerechnet die Wache im Ruhemodus lag.**

```
**Stichtag:** 25.08.2026, ~05:40 · **Lage:** RUHE
**Gilt bis:** Adams Rückkehr (~28.08.), ausdrücklich ausgetragen
**Eingefrorene Wächter-Fixes:**
  · Rang A — 8 sicherheitstragende Prüfzeilen sind blind gemessen und NICHT
    repariert (Boten-Postfach-Geheimnisschranke, WebSearch-Kostenschranke,
    Zustellnachweis, Wächter-Start, Medien-Eingangsschutz, Limit-Rücklage,
    Start-Wächter im Detach, Kalender-Geheimnissuche). Katalog:
    `befund-entkernung.md`. **In dieser Zeit deckt keiner dieser Prüfer
    einen stillen Bruch.**
  · Rang B (c) und (d) — offen, klein.
  · 5 echte gemischte Anführungspaare — unrepariert, harmlos solange niemand
    die Zeilen auf doppelte Quotes umschreibt.
  · Erkennungsseite Rang 2 (MIME/BODYSTRUCTURE) — bewusst zu, braucht R1.
**Ausgetragen:** offen
```

**Und die Gegenrichtung, damit der Eintrag nicht selbst zur Falle wird:** Trag
in denselben Commit, **woran** das Austragen hängt — Adams Rückkehr, nicht ein
Datum. Ein Eintrag ohne Austragsbedingung ist die nächste stille Falsch-Wahrheit.

## ③ Adams Update-Hinweis in die Ablage — er darf nicht im Chat verfallen

Adam meldet: **Es stehen Updates aus, inzwischen auch rot markierte
(grundlegende)**, und er hält es für bald fällig. Das ist eine Entscheidung
im Bot-Chat, und nach dem Ablageweg-Grundsatz verfällt sie still, wenn sie
niemand überträgt.

Als Punkt anlegen, mit den drei Leitplanken, die dafür schon gelten:
- **💰 Kostenregel:** nur aus dem Abo-/Kostenlos-Topf; alles Kostenpflichtige
  braucht Adams Freigabe **vorher**.
- **R4 Probelauf im Klon:** Fundament-Updates sind der Musterfall — eigener
  Arbeitsbaum, eigene venv, Regressionslauf dort. Und **neben** dem Repo, nicht
  darunter (die Lehre von heute Nacht).
- **Versions-Divergenz messen, nicht annehmen:** Mac 3.12.13, VPS 3.13.5, dieser
  Container 3.11.15 — heute Nacht hat genau dieser Unterschied einen Prüfer
  blind gemacht. **Vor dem Update den Ist-Stand aller drei einfrieren.**

---

## Was ausdrücklich NICHT passiert

**Rang A wird nicht angefangen.** Acht Stellen, zwei Stunden, sicherheitstragend
— das ist ein eigener Block mit wacher Kontrolle, nicht der Rest einer Nacht.
Der Deckel der Abwesenheits-Regel gilt: nichts Neues, nichts nach außen, im
Zweifel Liegenlassen.

**Kein Postfach wird hinterlegt.** Unverändert Adams Entscheid.

**Nach diesem Run ist Schluss** — auch wenn noch Zeit wäre. Das ist kein Halt
mittendrin, das ist ein Blockende: `WARTET: ja` in den Laufplan, Grund
„Blockende, Adam abgereist".
