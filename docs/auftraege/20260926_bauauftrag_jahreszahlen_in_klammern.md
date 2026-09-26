# Bauauftrag: Jahreszahlen in Klammern in der Sprachausgabe

**Zustand:** gültig · Weg: Claudia → Engywuck → Mick
**Fassung:** 26.09.2026
**Freigabe:** Adam am 26.09.2026, 17:31 Uhr, mit Daumen hoch

## Anlass

Am 26.09.2026 um 17:22 Uhr lieferte Claudia eine Modellliste im Muster
„6C 1500 (1927)“. Die Sprachausgabe las jede Jahreszahl als Menge
(„eintausendneunhundertsiebenundzwanzig“). Adam hat es um 17:30 Uhr gemeldet.

## Ursache, gemessen

`bot.py`, `_normalize_jahreszahlen` (ab Zeile 15878) schreibt eine Zahl von 1100
bis 1999 nur dann als Jahr um, wenn in den 30 Zeichen davor ein Jahres-Wort
steht (`_JAHR_HINWEIS`, Zeile 15860: seit, ab, bis, von, Jahr …), oder bei der
Bereichsform „1985 bis 1990“. Eine allein stehende Zahl in Klammern hat kein
solches Wort vor sich und bleibt deshalb eine Ziffernfolge.

## Auftrag 1 — Prüfpunkt vor dem Bauen: NeMo

Die NeMo-Textnormalisierung (NVIDIA, deutsche Grammatiken, `date.py`) steht
seit dem 29.08.2026 als Ablösung der Eigenbau-Regeln im Raum
(siehe `2026-08-28_bauauftrag-zahlen-in-der-sprachausgabe.md`).

**Zu prüfen:** Wie liest NeMo „RL (1922)“ und „8C 2900 (1936, Kleinserie)“?
Liest NeMo beide Fälle richtig und steht die Einführung zeitlich an, entfällt
Auftrag 2. Andernfalls wird Auftrag 2 als Sofortlösung gebaut, weil der Fehler
heute schon hörbar ist.

## Auftrag 2 — Strukturregel für Klammern

**Regel:** Eine Zahl `1[1-9]\d\d` gilt als Jahr, wenn sie
- allein in runden Klammern steht: `(1927)`, oder
- am Anfang einer Klammer steht und ein Komma folgt: `(1936, Kleinserie)`, oder
- als Bereich in Klammern steht: `(1910–1914)`, `(1910-1914)`.

Der Hinweis kommt also aus der Satzstruktur und nicht aus einem Wort davor.
Das entspricht Adams Grundsatz vom 28.08.2026, dass ein einzelnes Wort keinen
verlässlichen Parameter trägt.

**Die bestehende Gegenprobe bleibt:** Folgt eine Maßeinheit
(`_MENGEN_EINHEIT`), bleibt die Zahl eine Menge, etwa bei „(1500 Zeichen)“.

**Erwartete Ergebnisse (für den Selbsttest):**

| Eingabe | Gesprochen |
|---|---|
| `RL (1922)` | neunzehnhundertzweiundzwanzig |
| `8C 2900 (1936, Kleinserie)` | neunzehnhundertsechsunddreißig |
| `24 HP (1910–1914)` | neunzehnhundertzehn bis neunzehnhundertvierzehn |
| `Limit (1500 Zeichen)` | unverändert, als Menge |
| `Kosten (1500 Euro)` | unverändert, als Menge |
| `Junior (2024)` | unverändert, da Jahr- und Zahlform gleich lauten |

## Was brechen kann und wer es merkt

- **Mengen in Klammern ohne Einheit**, z. B. „Teilnehmer (1200)“, würden als
  Jahr gelesen. Das kommt seltener vor als der Jahresfall, fällt aber nur beim
  Hören auf. → Den Fall als bekannte Grenze im Selbsttest dokumentieren.
- **Kennnummern in Klammern** wie „(1234)“: `_normalize_kennnummern` muss in
  der Reihenfolge vor oder nach der neuen Regel sauber greifen. → Mick prüft
  die Reihenfolge in `_strip_markdown_for_tts` bzw. an den Aufrufstellen
  (Zeilen 16048 und 16659).
- **Stiller Fehlschlag:** Greift die Regel nicht, hört Adam wieder die
  Zahlform, und sonst bemerkt es niemand. → Die Fälle aus der Tabelle gehören in
  den Selbsttest des 4-Uhr-Checks (TTS-Cleanup).

## Reichweite

Dieselbe Lücke betrifft jede Liste mit Jahreszahlen: Biografien,
Chronologien, Baujahre, Quellenangaben „(2019)“ ab dem Jahr 2000
ausgenommen. Die Regel gehört deshalb in den zentralen Normalisierer und
nicht an eine einzelne Sendestelle.

## Überbrückung bis zum Bau

Claudia schreibt in Texten, die vorgelesen werden, ein Jahres-Wort vor die
Jahreszahl („6C 1500, ab 1927“).
