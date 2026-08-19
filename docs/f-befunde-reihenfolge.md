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

### F-1 · Vorlese-Kette — falsche Auskünfte im Betrieb `[offen]`

Die höchste Priorität, weil sie **falsche Aussagen erzeugt** statt bloß etwas
zu unterlassen.

- Die Datums-Regel prüft nur den **Monat**, nie den Tag: `Punkt 9.4.` wird zu
  `9. April`. `MIGRATION.md` besteht aus solchen Gliederungsnummern, und der
  Dokument-Vorlesepfad schickt Dokumentinhalt durch dieselbe Kette.
- Die Jahresregel führt `von`, `bis`, `ab`, `im` als Jahres-Hinweise — im
  Deutschen überwiegend **Mengen**-Präpositionen: `bis 1500 Zeichen` wird zu
  `bis fünfzehnhundert Zeichen`.
- `_zahlwort(1)` liefert „ein" statt „eins": `seit 1901` →
  `seit neunzehnhundertein`.
- Kennnummern am **Satzende** greifen gar nicht — die häufigste Stellung.

### F-2 · Hora: die Kürzung sitzt vor der Suche `[offen]`

Die Ausgabe wird auf die letzten 1200 Zeichen gekürzt, **bevor** `_fehlgrund`
darin sucht. Bei geschwätziger stderr fällt der Kopf weg — und die rote Zeile
mit ihm. Dazu trifft `_ROT_ZEILE` weder `Fehler:` noch `ERROR` noch `failed`,
in einem durchweg deutschsprachigen Projekt.

### F-3 · Versions-Monitor: stille Dauerausfälle `[offen]`

Ein unlesbarer Zeitstempel legt einen manuellen Eintrag **dauerhaft** still und
das Protokoll meldet „vor 0 Tagen gesehen" — eine aktive Falschauskunft. Eine
kaputte Sichtungsdatei setzt alle Fristen zurück. Ein Downgrade wird als Update
gemeldet. Ein unvollständiger Register-Eintrag tötet den Lauf **vor** Protokoll
und Versand.

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
