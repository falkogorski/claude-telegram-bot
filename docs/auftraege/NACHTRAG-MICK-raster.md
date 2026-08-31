<!-- ROLLE: nachtrag-nachtblock-2 -->
# Nachtrag zu `NACHTBLOCK-2-MICK.md` — ein vorgezogener Punkt

**Kopf:** 31.08.2026, 00:50 (Systemuhr abgelesen) · Kontroll-Sitzung
**Gemessen an:** `origin/mac-produktivstand` @ `1168363`
**Beilage:** `BEFUND-pruefraster.md` (die Messung im Einzelnen)

---

## Einordnung in die laufende Reihenfolge

**Dieser Punkt kommt zwischen F-11 und F-10.** Er ist klein (~20 Minuten,
reine Ablage), und er hat zwei Gründe, die F-10 nicht hat: Adam hat heute Nacht
ausdrücklich danach gefragt, und eine der falschen Zeilen zeigt in eine
sicherheitsrelevante Richtung.

**Falls F-11 sich als groß erweist:** diesen Punkt **vorher** erledigen. Er ist
bounded, F-11 ist es nicht.

---

## Der Auftrag: das Fähigkeiten-Raster nachziehen

`docs/entscheidungsvorlagen/pruefraster-assistenz-basisfaehigkeiten.md`

Du hattest es selbst als geparkten Punkt notiert („Fähigkeiten-Raster
nachziehen"). **Ich habe es inzwischen durchgemessen, damit du nicht neu
erheben musst.** Fünf Eingriffe:

### 1. Die Fußliste „Die sechs echten Lücken" streichen

**Fünf ihrer sechs Einträge werden von den Tabellen desselben Dokuments
widerlegt** — Kalender, E-Mail, Große Dateien und Link-Sammelstelle stehen dort
längst als gebaut, Erinnerungen ebenfalls (siehe 2.). Nur „Rechenblätter" trägt
noch.

Ursache: Am 28.07. wurden die Tabellen mit `[K4]`-Vermerken nachgezogen, die
Fußliste nicht. **Streichen statt neu erheben** — sie dupliziert die Tabellen und
driftet genau deshalb. *Eine Quelle statt zwei*, dieselbe Lehre wie bei deinem
Befehlsmenü-Commit.

### 2. Die Zeile „Erinnern zur richtigen Zeit" berichtigen

Steht dort als *„7.3 dokumentiert, nicht gebaut"*. **Gemessen:**
`scripts/erinnerungen.py`, **220 Zeilen**, seit 20.08. gebaut, neun Prüfungen,
im Drehbuch als „GEBAUT UND RUHEND". Und die Nummer ist falsch — der Läufer ist
**7.2**, 7.3 ist die Kalenderquelle.

Richtig: *gebaut und ruhend; es fehlen Kanal (7.1), Kalenderzugang (7.3) und der
Zeitgeber-Block.* **Das Symbol 🔄 bleibt richtig** — nur der Text war falsch.

### 3. Die E-Mail-Zeile — der folgenreichste Fehler

Sie sagt: *„Wartet auf zwei Dinge: die App-Kennwörter der beiden Konten."*

**Das ist heute nicht der Grund.** Adams stehende Regel: *kein Postfach, auch
kein Wegwerf-Konto, solange die Erkennungsseite nicht trägt.* Davor stehen Rang
2 und 3 der Widerlegung und die Ultracode-Prüfstelle. Das Raster erwähnt diesen
ganzen Komplex **genau einmal** und nicht in dieser Zeile.

**Die Fehlerrichtung ist die gefährliche:** Es lässt E-Mail wie ein Kennwort
entfernt aussehen und lädt damit ein, den letzten Schritt zu tun. Die Schranke
gehört in die Zeile, vor die Kennwörter.

### 4. „vier Gruppen fehlen noch" → fünf

Zeile „Mehrere Themen getrennt halten". Der Erinnerungskanal kommt hinzu —
dein eigener Fund von heute Nacht, hier noch nicht nachgezogen.

### 5. Den Gültigkeits-Kopf um eine Zeile ergänzen

Stichtag bleibt 25.07. Daneben gehört **„zuletzt nachgezogen: 31.08."**

**Die Lehre daraus ist die eigentliche Ausbeute:** Der Kopf war vorbildlich
gebaut — Regel ⑪ vollständig, „überholt durch —", Verweis auf die maßgebliche
Quelle. **Und er hat trotzdem nicht geschützt, weil er sagt, ab wann etwas gilt,
nicht ob es noch stimmt.** Ein „gültig ab" ohne „zuletzt geprüft" ist eine halbe
Auskunft.

---

## Was ausdrücklich NICHT gebaut wird

**Kein Prüfer, der das Raster gegen den Code misst.** Das wäre der Wächter
dritter Ordnung, und die Kurs-Regel verbietet ihn. Der vorhandene Ort ist die
stehende Stichprobe des Kurs-Blicks — zehn Ablage-Behauptungen gegen den Code,
wöchentlich, Falschquote berichtet. **Trag dieses Raster in deren Ziehungsmenge
ein**, mehr nicht. Ein Eintrag in eine bestehende Menge ist kein neuer Wächter.

---

## Und ein Hinweis, der über diesen Punkt hinausgeht

Ich habe das Raster zuerst von `claude/remote-control-2an15f` gelesen. **Der
Zweig steht seit dem 20.08. still — 203 Commits hinter `mac-produktivstand`,
null davor.** Beinahe hätte ich eine elf Tage alte Fassung als Stand gemeldet.

Falls es dafür keinen Grund gibt: **er gehört gelöscht oder als überholt
markiert.** Ein Zweig, der wie ein Arbeitszweig heißt und Geschichte enthält,
ist dieselbe Falle wie ein Papier ohne Gültigkeits-Kopf — nur schlechter
sichtbar. Ist das eine Entscheidung, die dir nicht zusteht: **melden, nicht
löschen.**

---

**Gut genug wenn:** Die Fußliste ist weg oder stimmt, die vier Zeilen sind
nachgezogen, der Kopf trägt ein „zuletzt nachgezogen", das Raster steht in der
Ziehungsmenge des Kurs-Blicks — **und im Bericht steht, ob du beim Nachziehen
weitere Zeilen gefunden hast, die ich übersehen habe.** Ich habe die fünf
MUSS/SOLL-Zeilen geprüft, die diese Nacht berührt hat; **die KÜR-Zeilen habe ich
nicht nachgemessen.** Das ist eine benannte Grenze, keine Zusage.
