> **Zweck: WEITERGABE → Engywuck** · **Zu tun:** lesen. Zwei Stellen deines
> Nachtrags haben beim Nachmessen nicht gehalten — sie stehen unten, mit dem,
> was stattdessen gebaut wurde.

# Bericht — Spesen-Staffel und Log-Repo

**Stichtag:** 04.09.2026, 20:22 · **Stand:** `4765a02`
**Läufe:** 72/72 · **Nenner:** dein Nachtrag hatte zwei Punkte, beide erledigt
· **0 Deploys** — A1 bis A3 liegen als Befehlsblock bei Adam

---

## ① Spesen — eingetragen als Regel 5a

Die Staffel steht in `RECHNUNGSREGELN.md`, der offene Block ist ersetzt,
`Spesen:voll` ist in der README-Kürzeltabelle nachgezogen. Die Herkunft steht
dabei: § 9 Abs. 4a EStG als Bezugsgröße, Adam bestätigt am 04.09., Beträge
Kenntnisstand und **nicht per Netzsuche geprüft**.

**Deine Zeile *„Die Zahl 8,40 kommt nirgends vor — nicht eintragen"* hält
nicht.** Gemessen:

```
daten/auf_norderney-livesetup.json:37   "Custom:Spesen 30 %:8.40"
output/_aufstellung.json                27.08. · Spesen 30 % · 8,40
```

Sie steht in Adams gelieferter Aufstellung zu 017-26, am Abreisetag. Er hat
sie am 03.09. auch nicht bestritten — sein Einwand galt der Beschriftung
(*„8,40 sind nicht 60"*), nicht dem Betrag.

**Und deine eigene Regel erzeugt sie.** Kürzung an der vollen Pauschale
bemessen, auch an Teiltagen: 14,00 − 5,60 = 8,40. Damit steht sie gegen
`saetze.json`, das für denselben Fall `Spesen_40` = 11,20 als *„etablierter
Abreisetag-Satz"* mit Präzedenz Dieburg/Landsberg führt.

**Ich habe keine der beiden zur Regel erhoben** — kein Kürzel für 8,40, kein
Eingriff in `saetze.json`. Der Widerspruch steht benannt in der Datei und in
Adams Befehlsblock als Frage an ihn. Ein Satz, der aus zwei Quellen zwei
verschiedene Zahlen liefert, ist die Sorte Karteileiche, die erst bei der
übernächsten Rechnung auffällt.

**Deine Rückfrage zum Datensatz:** Er trägt **nicht** die alten
Bezeichnungen. `auf_norderney-livesetup.json` steht bereits auf Prozentzahlen,
gegen die Regel gelesen und stimmig. Nichts neu erzeugt.

## ② Log-Repo — Befund 4 ist gebaut, die Historie liegt bei Adam

**Der Filter ist drin** (`bb37523`): `--exclude='rechnungen/'` vor den
Includes, gemessen im vorhandenen Prüfer, der `log_sync.sh` echt fährt. Drei
Gegenproben, jede traf die vorher notierte rote Zeile. Kein neuer Wächter.

**Die drei Dateien, jetzt benannt statt gezählt:** `README.md`,
`RECHNUNGSREGELN.md`, `output/Rechnung 012-26.pdf`. **Nur die PDF trägt eine
echte Bankverbindung** — mit `pdftotext` gemessen, der Wert steht in keinem
Bericht. Herein kam sie am 03.09. um 00:45 mit dem Vergleichslauf.

**Eine Abweichung von deiner Prüfvorgabe, und sie ist Absicht:** Du wolltest
messen, dass `rechnungen/` in `letzter-abgleich.txt` nicht mehr erscheint. **Es
erscheint weiterhin** — als eine Sammelzeile *„ganzer Zweig zurueckgehalten:
Bank und Steuernummer"*.

Der Grund ist deine eigene Lehre vom 20.08. Ohne Spiegelung im Bericht stünde
unter **jeder** Rechnung *„bitte melden, das sollte mitkommen"* — dieselbe
Falschauskunft wie damals mit den 120 Pip-Dateien, nur mit anderem Ordner. Ein
lautloser Ausschluss wäre die andere Hälfte: ein ganzer fehlender Zweig, den
niemand bemerkt. Also: Schleife überspringt, eine Zeile nennt ihn samt Grund.
**Gemessen wird deshalb am Zielordner, nicht an der Quittung** — so steht es im
Befehlsblock.

**Der Befehlsblock** (`docs/befehlsbloecke-adam.md`, Teil A) folgt deiner
Reihenfolge: Filter deployen → messen → `git rm` → Zeitgeber anhalten →
`filter-repo` im frischen Klon → beide Klone nachziehen → Zeitgeber starten →
messen. Zwei Dinge kamen beim Messen dazu: `git-filter-repo` fehlt am Mac
(`brew`, kostenfrei), und **`filter-repo` entfernt die Gegenstelle absichtlich**
— ohne `git remote add` läuft der Push ins Leere.

**Bekannte Klone: zwei** — der Abgleichsklon auf dem VPS und Adams Mac-Klon
unter `~/Projects/claude-bot-logs` (Stand 01.09.). Beide sind im Block.

## 🔴 Eine Beobachtung, die nicht in Befund 4 gehört

Zwei Papiere liegen **außerhalb** des Zweigs und beschreiben dieselbe Rechnung:
`ausarbeitungen/2026-09-02_rechnung-norderney-livesetup.md` und `.pdf`. **Keine
Bankverbindung, keine Steuernummer** (nachgemessen), aber Kunde und Beträge.
Der Ordner-Ausschluss greift dort nicht — der Anker ist ein Name, kein Merkmal,
dieselbe Grenze wie beim `.venv`-Ausschluss des Backups.

**Das ist keine Empfehlung.** Ausarbeitungen sind der Weg, auf dem du Adams
Vorgänge überhaupt lesen kannst; sie auszuschließen nähme dir die Augen. Die
Frage, ob Rechnungsinhalte in Berichten im Log-Repo liegen dürfen, gehört Adam.

## Ins Register und in die Blaupause

Registerzeile erweitert (Log-Sync-Filter, mit dem Prüfbefehl und der
Namens-Grenze). Zwei Blaupause-Zeilen: *Eine Quittung, die niemand liest, ist
eine Logzeile* — und *Ein Ausschluss ist ein Datenschutz-Bauteil, kein
Aufräumen*: Der Umzug am 03.09. war der Zeitpunkt, an dem der Filter billig
gewesen wäre.
