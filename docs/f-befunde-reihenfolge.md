<!-- ROLLE: f-befunde-reihenfolge -->
# F-Befunde der Gegenprüfung — Reihenfolge und Stand

**Stichtag:** 2026-08-19 · **überholt durch:** — · **maßgeblich ist diese
Datei** (Volltext der Befunde: `docs/gegenpruefung-2026-08-18.md`)

## Warum diese Datei existiert

Die F-Befunde standen im Laufplan. **Der ist bewusst `gitignored`** — er ist
der Notizzettel der laufenden Sitzung, kein Dokument. Beim Umschreiben seines
Kopfes am Abend des 18.08. sind sie herausgefallen, und weil es keinen Verlauf
gibt, hat es niemand gesehen. Aufgefallen ist es erst, als ich sie heute suchte.

**Die Lehre ist dieselbe wie beim Ablageweg-Grundsatz:** Was eine Reihenfolge
überleben soll, gehört dorthin, wo eine Änderung sichtbar wird. Ein
Notizzettel taugt für den Tag, nicht für eine Woche.

Engywucks Befund ③ verlangt genau das — hier ist es.

## Die Reihenfolge

Keiner dieser Befunde ist deploy-blockierend; sie sind nach **Schaden bei
Nichtstun** sortiert, nicht nach Aufwand.

### F-1 · Vorlese-Kette — falsche Auskünfte im Betrieb `[erledigt 19.08.2026]`

Alle vier Teilbefunde nachgemessen, behoben und mit ausführenden Prüfungen in
beide Richtungen belegt (`scripts/test_vorlese_b5.py`, sechs neue Zeilen).
**Ein Befund war schärfer als notiert:** Der Tag wurde nicht nur unvollständig
geprüft, sondern gar nicht — `Punkt 40.5.` ergab `40. Mai`.

- **Gliederungsnummern** sind gesperrt: Steht ein Wort wie `Punkt`, `Phase`,
  `Abschnitt`, `Regel` davor, ist es keine Datumsangabe. Dazu die fehlende
  Tages-Plausibilität (1–31).
- **`im` ist als Jahres-Hinweis ersatzlos gestrichen** — es trug nie allein
  einen Jahresbezug. Dazu eine **Gegenprobe nach hinten**: Folgt der Zahl eine
  Maßeinheit, gewinnt sie gegen jedes Jahres-Wort davor.
- **`_zahlwort` kennt jetzt „eins" neben „ein"** — die Eins ist das einzige
  deutsche Zahlwort mit zwei Formen.
- **Der Satzpunkt verdeckt nichts mehr**: Punkt und Komma blocken nur noch,
  wenn eine Ziffer folgt. Dezimalzahlen bleiben heil.

**Bewusst nicht behoben** (Konvergenz-Bremse, geht nach F-5): `1985 bis 1990`
wird uneinheitlich gelesen, weil nur die zweite Zahl einen Hinweis davor hat.
Das ist Stil, keine Falschaussage — und die Bereichs-Erkennung samt
Einheiten-Prüfung über den ganzen Bereich wäre teurer als der Gewinn.

### F-2 · Hora: die Kürzung sitzt vor der Suche `[erledigt 19.08.2026]`

Die Ausgabe wird auf die letzten 1200 Zeichen gekürzt, **bevor** `_fehlgrund`
darin sucht. Bei geschwätziger stderr fällt der Kopf weg — und die rote Zeile
mit ihm. Dazu trifft `_ROT_ZEILE` weder `Fehler:` noch `ERROR` noch `failed`,
in einem durchweg deutschsprachigen Projekt.


Beide Teile gemessen, beide bestätigt. **Der erste ist ein Rückfall in einen
bereits behobenen Fehler:** Die rote Zeile stand im Kopf, 200 Zeilen Geschwätz
folgten, gemeldet wurde `der Befehl meldete: ok, alles gut`. Das ist wörtlich
der Halt vom 28.07. — eine Positionsannahme statt eines Inhaltsmerkmals —, und
der Kommentar, der genau davor warnt, stand die ganze Zeit direkt über der
Stelle. Die Kürzung hatte ihn durch die Hintertür ausgehebelt.

- **`_verdichten()` behält beide Enden** und benennt die Lücke. Der Anfang
  trägt meist die Ursache, das Ende die Wirkung; eine Grenze, die nur ein Ende
  bevorzugt, ist wieder eine Positionsannahme.
- **`_ROT_ZEILE` kann jetzt Deutsch.** Gemessen waren sechs von acht typischen
  Fehlerzeilen blind — `Fehler:`, `ERROR:` (das Muster lief ohne `IGNORECASE`),
  `failed`, `abgebrochen`, `verweigert`. Grenzen beidseitig offen nach der
  Stichwort-Regel, dazu eine kurze, ausdrücklich benannte Ausnahmeliste, damit
  „✓ fehlerfrei durchgelaufen" keinen Fehler meldet.

Vier neue Prüfzeilen, jede mit Gegenprobe — die zum Kopf-Befund misst
ausdrücklich mit, dass die alte Kürzung ihn verfehlt hätte.
### F-3 · Versions-Monitor: stille Dauerausfälle `[erledigt 19.08.2026]`

Ein unlesbarer Zeitstempel legt einen manuellen Eintrag **dauerhaft** still und
das Protokoll meldet „vor 0 Tagen gesehen" — eine aktive Falschauskunft. Eine
kaputte Sichtungsdatei setzt alle Fristen zurück. Ein Downgrade wird als Update
gemeldet. Ein unvollständiger Register-Eintrag tötet den Lauf **vor** Protokoll
und Versand.


Vier Teilbefunde, alle gemessen und behoben. **Der schwerste war der vierte:**
Ein unvollständiger Register-Eintrag — ein fehlendes `name` oder `kind` —
tötete `main()` mit einem `KeyError`, und zwar **vor Protokoll und vor
Versand**. Ein Tippfehler im Register hätte den gesamten Monitor stillgelegt,
lautlos: Wer ihn per Zeitgeber laufen lässt, sieht nur, dass keine Meldung
kommt. Jetzt scheitert höchstens der eine Eintrag, und er sagt es.

- **Unlesbarer Zeitstempel** ist jetzt **fällig** statt „gerade eben gesehen",
  und die Meldung nennt den Grund statt „seit -1 Tagen nicht geprüft".
- **Fehlende und kaputte Sichtungsdatei** sind getrennt: Fehlen ist der erste
  Lauf, Kaputtsein ein Befund. Vorher setzte eine beschädigte Datei alle
  Fristen zurück, ohne dass es jemand erfuhr.
- **Rückwärts** ist eine eigene Auskunft: Bei den vergleichbaren Arten fiel der
  Fall stumm in „aktuell", bei den Ungleich-Arten wurde er als Update mit Pfeil
  gemeldet (`1.5 → 1.2`). Er ist keins von beidem. Bei Fingerabdrücken wird
  jetzt „weicht ab" gesagt statt eine Reihenfolge zu behaupten, die es dort
  nicht gibt.

Vier neue Prüfungen, davon zwei **ausführend** — der Lauf wird mit einem
kaputten Register wirklich gefahren, nicht auf Schreibweise geprüft.
### F-4 · `/updates` misst zweimal getrennt `[offen]`

`classify()` und `blinde_flecken()` befragen jede Quelle **einzeln**. Fällt eine
im ersten Durchlauf aus und antwortet im zweiten, erscheint sie in **keiner**
Liste — das Loch, das der Fix vom 28.07. schließen wollte, ist zeitabhängig
wieder da. Nebenbei: doppelte Netzzugriffe vor Adams Augen.

### F-5 · Kleinere Ränder `[offen]`

Der Warteschlangen-Hinweis kam am 18.08. doppelt (einmal Text, einmal Stimme).
Der Warn-Zustand der Limit-Vorwarnung liegt prozessweit ohne Nutzerbezug —
bricht beim zweiten Nutzer. Die Entwarnung bleibt über einen Neustart hängen.

## Erledigt

- **Zeitgeber-Wache** (Befund B1/B4/B5): gelöschte Timer werden erfasst,
  monotone nicht mehr angeklagt, bewusst Abgeschaltetes hat einen Ausweg —
  `0498ee0` und `325a90d`.
- **Repo-Wächter** (Claudias Befund): Fehlerumleitungen sind kein Schreiben —
  `f2474d0`.
- **Quittung des Abgleichs** (Nachlese ②/③) — `f2474d0`.
