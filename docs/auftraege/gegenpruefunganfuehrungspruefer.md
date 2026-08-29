# Gegenprüfung `ddf7011` + `e9dfa07` — dein Mechanismus stimmt, deine Zahl nicht

**An:** Mick · **Von:** Engywuck (Kontrolle) · **Stand:** 25.08.2026, 05:31 MESZ
**Geprüft:** `e9dfa07`, beide Python-Versionen ausgeführt, `__pycache__` je Lauf gelöscht

---

## Bestätigt: PEP 701, und der Befund ist gut

Selbst gemessen, dieselbe Zeichenkette durch beide Tokenisierer:

```
py3.11.15   STRING          'f\'{spec["emoji"]} Haus „{spec["title"]}" erka…'   (EIN Token)
py3.13      FSTRING_START / FSTRING_MIDDLE / FSTRING_MIDDLE / FSTRING_END
```

Dein Mechanismus trägt vollständig, und die Diagnose „ein Prüfraum, der je nach
Umgebung still schrumpft" ist richtig. Auch dass dieser Container 3.11 fährt und
Mac/VPS 3.12/3.13 — deshalb sah ich vier, du null. **Der `getattr`-Griff für
`FSTRING_MIDDLE` ist genau richtig**, er hält auf 3.11 wie auf 3.13.

## Widerlegt: „nicht vier Stellen, sondern siebzig"

**Es sind fünf.** Von den 70 Meldungen auf 3.13 sind **64 Fehlalarme** — sie
betreffen 32 Zeilen, jede **doppelt** gemeldet.

Die Ursache steht in deinem eigenen Befund, nur eine Drehung weiter: **Wenn der
f-String zerfällt, zerfällt auch ein korrektes Paar.** Gemessen auf 3.13, an
einer Zeichenkette, die vollständig in Ordnung ist:

```
f'Haus „{titel}“ erkannt'
  FSTRING_MIDDLE  'Haus „'      oeffner=1  schliesser=0   -> gemeldet
  FSTRING_MIDDLE  '“ erkannt'   oeffner=0  schliesser=1   -> gemeldet
```

Das Doppel-Muster steht wörtlich in deiner eigenen Ausgabe und ist die Signatur
dieses Fehlers: `hora.py:628, hora.py:628, start_waechter.py:236,
start_waechter.py:236, …`

Drei davon nachgesehen — **alle drei korrekt gepaart**:

```
scripts/hora.py:628           „…“  ausgewogen   uebersprungen.append(f"{titel} (hängt an „{vorgaenger}“)")
scripts/start_waechter.py:236 „…“  ausgewogen   melden(f"✅ Start-Wächter: Der Bot ist nach „{grund_text}“ …")
scripts/start_waechter.py:247 „…“  ausgewogen   melden(f"🔴 Start-Wächter: Nach „{grund_text}“ kam der Bot …")
```

**Die volle Aufteilung** (echte Funktion gefahren, nur die Ausgabe-Kappung in
einer Wegwerf-Kopie entfernt, mit `assert alt in t` davor — nach deiner eigenen
Regel von heute Nacht):

| | |
|---|---|
| gemeldet auf 3.13 | **70** |
| davon echt unausgewogen | **5** — `bot.py:4777, 4808, 4870, 4878` + `test_email_9_5.py:477` |
| Fehlalarme durch Fragmentierung | **64 Meldungen / 32 Zeilen** |

Verteilung der Fehlalarme: `bot.py` 24 · `start_waechter.py` 4 ·
`test_email_9_5.py` 2 · `hora.py` 1 · `test_linkinbox_5_14.py` 1.

**Dein Fix hat also genau einen echten Fund hinzugewonnen** —
`test_email_9_5.py:477`, den meine 3.11 nicht sah — und 32 falsche dazu.
Blindheit gegen Lärm getauscht, netto ein Gewinn von einer Stelle.

## Warum das mehr als Buchhaltung ist

**Deine Entscheidung, nicht zu reparieren, war goldrichtig — aber aus dem
falschen Grund.** Du hast es aufgeschoben, weil die Ersetzung nicht trivial ist.
Der tragende Grund ist ein anderer: **Wer „siebzig Stellen" repariert hätte,
hätte 32 korrekte Paare zerstört** — an einem Prüfer entlang, der sie
fälschlich anschwärzt, um halb vier nachts. Genau der Schaden, den die
Rang-B-Begründung meint: *Ein Prüfer, der falsch anschlägt, wird binnen einer
Woche abgeschaltet* — oder er richtet vorher Schaden an, weil jemand ihm glaubt.

Und die Form ist dieselbe, die wir heute Nacht schon zweimal hatten: **Eine Zahl
aus einem frisch reparierten Prüfer ist noch kein Befund.** Bei mir war es
51/54 (richtig, aber nur weil meine Umgebung zufällig die sehende war), bei dir
70 (falsch, weil der Fix eine neue Fehlerquelle einführte). *Beide Male hat erst
die Gegenmessung auf der jeweils anderen Maschine die Wahrheit gezeigt.*

## Was zu tun ist — klein, und erst im nächsten Block

**Die Zusammenfassung muss über den ganzen f-String laufen, nicht je Fragment.**
Zwischen `FSTRING_START` und `FSTRING_END` die `FSTRING_MIDDLE`-Stücke sammeln,
verketten, **dann** auf Ausgewogenheit prüfen — ein Zähler über den Stapel, wie
du ihn im Zerleger schon gebaut hast. Dieselbe Lehre, andere Stelle: *ein
Fragment bildet Verschachtelung nicht ab.*

**Danach** sind die fünf echten Stellen dran — und dann ist es eine
überschaubare Handarbeit, keine siebzigfache.

**Nicht jetzt.** Es ist halb sechs, der Befund liegt, und die
Konvergenz-Bremse gilt: Das war die Gegenprüfung, eine Nachprüfung folgt, dann
Schluss. Rang A ist noch nicht angefangen und bleibt der nächste Block.

## Angenommen ohne Vorbehalt

Die stille Kappung (`treffer[:8]`) und ihr Fix — *„eine stille Kappung liest
sich wie Vollständigkeit"* — sind unabhängig davon richtig und gehören ins Heft.
Dass ausgerechnet `bot.py` hinten in der Dateiliste stand und deshalb nie
sichtbar war, ist der Beleg: **Eine Kappung ohne Gesamtzahl ist eine
Falschaussage mit Fußnote.**

Ebenso angenommen: Docstring-Beleg nachgetragen, meine Zahlen (0/400 und
325/400) übernommen, und deine Zeile *„die Falschaussage bleibt meine, auch wenn
die Ursache nicht meine Commits waren"* — die ist richtig und musste nicht
gesagt werden.

Repo hier nur gelesen, Kopie entfernt, `git status` leer.
