<!-- ROLLE: befund-pruefraster -->
# Befund: das Fähigkeiten-Raster ist das richtige Instrument — und es widerspricht sich selbst

**Kopf:** 31.08.2026, 00:50 (Systemuhr abgelesen) · Kontroll-Sitzung · gemessen an
`origin/mac-produktivstand` @ `1168363`
**Gegenstand:** `docs/entscheidungsvorlagen/pruefraster-assistenz-basisfaehigkeiten.md`

---

## Vorweg, weil es mir selbst fast passiert wäre

Ich habe das Raster zuerst von `claude/remote-control-2an15f` gelesen. **Dieser
Zweig steht seit dem 20.08. still — 203 Commits hinter `mac-produktivstand`, null
davor.** Beinahe hätte ich eine elf Tage alte Fassung als Stand gemeldet.

Für alle Sitzungen: **`mac-produktivstand` ist der lebende Zweig.** Wer
`remote-control` liest, liest Geschichte.

---

## ① Die Zählung stimmt — und eine Kategorie fehlt in der Meldung

Nachgezählt über alle drei Tabellen:

| Teil | ✅ | 🔄 | 🕳️ | Summe |
|---|---|---|---|---|
| MUSS | 11 | 4 | 0 | 15 |
| SOLL | 7 | 4 | 1 | 12 |
| KÜR | 1 | 4 | 1 | 6 |
| **gesamt** | **19** | **12** | **2** | **33** |

Micks „19 grüne und 12 laufende" ist exakt. **Die zwei echten Lücken hat er
nicht mitgenannt** — Bilder/Diagramme erzeugen (SOLL) und eigene Oberfläche
(KÜR). Beide bewusst offen, aber sie gehören in die Zahl, sonst ist der Nenner
31 statt 33.

---

## ② Der eigentliche Befund: die Fußliste widerlegt die Tabelle über ihr

Das Raster trägt Stichtag **25.07.** Am **28.07.** wurden vier Zeilen der
Tabellen mit `[K4]`-Vermerken nachgezogen. **Die Schlussliste „Die sechs echten
Lücken" wurde dabei nicht angefasst** — sie steht heute unverändert im Stand vom
25.07. und behauptet das Gegenteil dessen, was zwanzig Zeilen weiter oben steht:

| Fußliste sagt | Tabelle desselben Dokuments sagt |
|---|---|
| 1. „**Kalender** — es gibt nichts" | „**Gebaut** (7.5, `kalender.py`, CalDAV), sechs Prüfungen" |
| 2. „**E-Mail**" als Lücke | „**Gebaut** (9.5, `email_kanal.py`), 14 Prüfungen" |
| 3. „**Erinnerungen** — dokumentiert, ungebaut" | *(siehe ③ — hier ist auch die Tabelle falsch)* |
| 4. „**Große Dateien** — Vorlage liegt entscheidungsreif" | „**Bot-Seite gebaut** (5.34)" |
| 5. „**Link-Sammelstelle**" als Lücke | ✅ „**Gebaut** (5.14, `linkinbox.py`)" |
| 6. Rechenblätter | 🔄 — **die einzige Zeile, die noch trägt** |

**Fünf von sechs.** Wer nur die Zusammenfassung liest — und Zusammenfassungen
werden gelesen, dafür sind sie da — bekommt einen Stand von Ende Juli.

Das ist dieselbe Klasse wie der Nachtblock-Fehler von heute Nacht: **ein
Dokument, das den Stand behauptet, statt ihn zu messen.** Nur diesmal
widerspricht es sich innerhalb einer Datei.

---

## ③ Eine Zeile ist auch in der Tabelle falsch

> „**Erinnern zur richtigen Zeit** | 🔄 | 7.3 dokumentiert, nicht gebaut."

**Gemessen:** `scripts/erinnerungen.py` liegt auf `mac-produktivstand`, **220
Zeilen**, seit dem 20.08. gebaut, neun Prüfungen, im Drehbuch als
*„GEBAUT UND RUHEND"* geführt. Und die Nummer stimmt nicht: Der Läufer ist
**7.2**, 7.3 ist die Kalenderquelle.

Richtig wäre: *gebaut und ruhend; es fehlen der Kanal (7.1), der Kalenderzugang
(7.3) und der Zeitgeber-Block.*

---

## ④ Die folgenreichste Veraltung — und sie geht in die falsche Richtung

> „**E-Mail lesen und senden** … **Wartet auf zwei Dinge:** die App-Kennwörter
> der beiden Konten."

**Das ist heute nicht der Grund, warum kein Postfach hinterlegt ist.** Adams
stehende Regel lautet: *kein Postfach, auch kein Wegwerf-Konto, solange die
Erkennungsseite nicht trägt.* Davor stehen Rang 2 und 3 der Widerlegung und die
Ultracode-Prüfstelle.

**Das Raster erwähnt diesen ganzen Komplex genau einmal** — und nicht in dieser
Zeile. Es lässt E-Mail wie ein Kennwort entfernt aussehen, während in Wahrheit
eine Sicherheitsschranke davorsteht, die Adam ausdrücklich angeordnet hat.

**Die Fehlerrichtung ist die gefährliche:** Ein Raster, das eine Fähigkeit als
fast fertig ausweist, lädt dazu ein, den letzten Schritt zu tun.

---

## ⑤ Was daraus zu tun ist — klein, kein neuer Wächter

1. **Die Fußliste streichen oder neu erheben.** Streichen ist die bessere
   Antwort: Sie dupliziert die Tabellen und driftet genau deshalb. *Eine Quelle
   statt zwei* — dieselbe Lehre wie beim Befehlsmenü.
2. **Die vier Zeilen aus ②/③/④ nachziehen**, mit Datumsvermerk wie bei `[K4]`.
3. **„vier Gruppen fehlen noch"** → **fünf** (Erinnerungskanal, Befund von
   heute Nacht).
4. **Gültigkeits-Kopf nachziehen** — Stichtag bleibt 25.07., aber
   „**zuletzt nachgezogen: 31.08.**" gehört daneben. Der Kopf ist vorbildlich
   gebaut und war trotzdem kein Schutz: **er sagt, ab wann etwas gilt, nicht ob
   es noch stimmt.**

**Ausdrücklich nicht:** ein Prüfer, der das Raster gegen den Code misst. Das
wäre der Wächter dritter Ordnung. Der Ort dafür ist die stehende Stichprobe des
Kurs-Blicks — zehn Ablage-Behauptungen gegen den Code, wöchentlich. **Dieses
Raster gehört ab jetzt in deren Ziehungsmenge.**
