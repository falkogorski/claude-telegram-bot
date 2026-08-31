<!-- ROLLE: entscheide-31-08 -->
# Adams Entscheide vom 31.08. — zwei gefallen, einer wird erst gemessen

**Kopf:** 31.08.2026, 09:10 (Systemuhr abgelesen) · Kontroll-Sitzung
**Stand:** `717b059` · **Ergänzt:** `NACHTRAG-MICK-modellstrang.md`

---

## ① Modellstrang — entschieden: ein Punkt in Phase 9, Notfallplan

**Adams Entscheid:** Der zweite Weg für den Hauptagenten wird **geplant, nicht
gebaut.**

**Neuer Punkt `### 9.16`** (die erste freie Nummer — 9.1 bis 9.15 sind belegt,
nachgezählt). Vorschlag für den Namen: *„Zweiter Weg für den Hauptagenten —
Notfallplan"*.

- **Akzeptanzkriterium:** *Ein schriftlicher Plan existiert und ist aktuell* —
  ausdrücklich **nicht** „ein zweiter Weg ist gebaut". Ein gebauter zweiter Weg
  wären Wochen Versicherung gegen ein Ereignis, das vielleicht nie eintritt;
  ein Plan deckt das Risiko: Wenn der Abo-Weg zugeht, fängt Adam nicht bei null an.
- **Darunter gehören:** `9.7 Hermes` und der Strategie-Bericht. Das ist die
  richtige Hängung — der Bericht ist **Eingangsmaterial des Notfallplans**, nicht
  Fußnote einer Plattform-Bewertung. Der Verweis wird aus 9.7 herausgelöst
  (Auftrag ② des Modellstrang-Nachtrags).
- **Status:** OFFEN.

### Und der erste Inhalt dieses Punktes ist ein Befund, kein Plan

**Gemessen am Code, `717b059`:** Die Zeichenkette `legal-and-compliance` kommt
in **keiner einzigen versionierten `.py`, `.sh`, `.toml` oder `.json`** vor —
nur in acht Markdown-Dateien. `scripts/wachposten.py` trägt ROLLE
`log-wachposten`, liest Log-Zeilen gegen `wachmuster.py` und enthält **keine
einzige URL**. `5.21` ist der Versions-Monitor über `components.json`.

**`CLAUDE.md`, Zeile 71 behauptet:**
> „Der AGB-Wachposten (5.21) überwacht die Legal-Seite auf Änderungen der
> Auth-Passage."

**Es gibt ihn nicht.** Niemand beobachtet die Seite, auf der die Grundlage
dieses ganzen Projekts steht — und im Grundregelwerk steht, dass es jemand tut.

**Das ist die gefährlichste Falschaussage, die dieses Audit gefunden hat**, und
zwar aus zwei Gründen: Sie steht in `CLAUDE.md`, das jede Sitzung beim Start
liest. Und sie beruhigt in genau der Frage, in der Anthropic seit 04/2026
„without prior notice" sperrt.

**Was du tust — klein, und die Form steht schon:** `components.json` ist eine
Liste von 19 Einträgen mit den Schlüsseln `name · kind · venv · ref · pinned ·
note`, und **vier Einträge tragen bereits `manual`**. Die Legal-Seite kommt als
weiterer `manual`-Eintrag hinein; der wöchentliche Monitor legt sie Adam dann
im selben Meldeweg vor. **Kein neues Skript, kein neuer Wächter** — ein Eintrag
in eine bestehende Menge.

**Und die Zeile in `CLAUDE.md` wird berichtigt**, bevor der Eintrag steht: erst
ehrlich („noch kein Wachposten"), dann bauen. Eine Regel, die ihren eigenen
Prüfer erfindet, ist schlimmer als eine ohne.

---

## ② Weitergabe — entschieden, aber anders als ich es vorgelegt hatte

**Adams Korrektur, und sie trifft einen Denkfehler von mir:** Ich hatte zwei
Dinge unter „Einkommensstrang" vermengt.

| | gehört wohin |
|---|---|
| **Adams laufende Einkommensprojekte** — womit er heute Geld verdient | **gar nicht in dieses Drehbuch.** Andere Projekte, eigener Ort. |
| **Was aus diesem Projekt wird, wenn es trägt** — Weitergabe an Menschen, möglicherweise Open Source, irgendwann vielleicht Monetarisierung | **hierher** — aber als Verweis, nicht als Ausarbeitung |

**Der Name „Einkommensstrang" war falsch** und wird nicht verwendet. Adams
Worte: *„Das hier ist noch weit weg von Einkommensgenerierung."*

**Neuer Punkt `### 9.17` — Vorschlag: „Weitergabe"**. Er sitzt damit direkt
neben `9.6 Blaupause`, und das ist die richtige Nachbarschaft: **Die Blaupause
ist das übertragbare Grundwerk, die Weitergabe ist die Frage, wer es bekommt
und wie.** Adams Neigung ist Open Source; der Punkt hält das offen und
entscheidet es nicht.

- **Der Punkt trägt nur Status und Verweis.** Die Ausarbeitung entsteht
  **extern** — das ist Adams ausdrücklicher Wunsch, und der Grund ist der
  gleiche wie beim Strategie-Bericht: **Geschäft und Technik gehören getrennt.**
- **Verwiesen wird auf** `docs/entscheidungsvorlagen/momo-business-skizze.md`
  und `momo-gruendungserzaehlung.md` — die beiden Papiere, die heute ohne
  jeden Drehbuch-Eintrag dastehen.
- **Status:** OFFEN, ausdrücklich **nicht terminiert**. Er existiert, damit es
  nicht verloren geht — nicht, um jetzt bearbeitet zu werden.

**Falls dir ein besserer Name einfällt als „Weitergabe": vorschlagen, nicht
setzen.** Der Name gehört Adam; ich habe ihm diesen einen vorgelegt.

---

## ③ Hora — NICHT entscheiden, erst messen

**Adam konnte die Frage nicht beantworten** — sie erschließt sich von außen
nicht, und das ist kein Mangel bei ihm, sondern bei meiner Vorlage. **Also wird
sie nicht auf mein Urteil und nicht auf deines entschieden, sondern auf Zahlen.**

**Der Messauftrag, klein und begrenzt:**

Über das vorhandene Auftragsbuch-Archiv:
1. **Wie viele Aufträge liefen grün** — seit dem 18.08. (Adams Vier-Arten-Entscheid)?
2. **Wie viele davon trugen ein `befehl`-Feld?**
3. **Was taten diese Befehle** — Liste, gekürzt, ohne Geheimnisse?
4. **Wie viele wären unter F-16 zustimmungspflichtig geworden?**

**Kein Umbau, keine Änderung an Hora, kein neuer Prüfer.** Nur die vier Zahlen
und die Liste. Wenn das Archiv sie nicht hergibt, ist **das** das Ergebnis —
dann melde es so, statt zu schätzen.

**Warum diese Reihenfolge:** Die Antwort ändert die Frage. Sind es null
Befehle, ist F-16 folgenlos und kann trotzdem hinein — reine Härtung ohne
Preis. Sind es fünfzig, ist es die Entscheidung, Horas Nachtlauf abzuschaffen,
und die gehört Adam mit Zahlen vor Augen.

**Meine Neigung, damit sie auf dem Tisch liegt und nicht in mir:** Ich würde
F-16 verwerfen. Der Riegel trägt heute dreifach — geschlossene Absenderliste,
geschlossene Vier-Arten-Liste, und die Rot-Wortsuche läuft **ausdrücklich auch
über das `befehl`-Feld** (`auftragsbuch.py:188`, gemessen). Dass dein Einzeiler
fünf abgenommene Prüfzeilen bricht, lese ich als Signal, dass er die **Bauart
ändert statt sie zu härten.** Aber das ist eine Neigung aus zwanzig Minuten
Messen; deine Zahlen schlagen sie.

---

## Reihenfolge

**① vor ②**, weil ① eine Falschaussage in `CLAUDE.md` enthält. **③ zuletzt**,
weil es nur eine Messung ist.

**Und ①-Berichtigung vor ①-Eintrag** — die falsche Zeile geht raus, bevor der
Wachposten-Eintrag hineinkommt. In der umgekehrten Reihenfolge stünde für die
Dauer eines Commits eine Behauptung im Grundregelwerk, die stimmt, weil man sie
gerade wahr gemacht hat. Das ist die Art Reihenfolge, die man später nicht mehr
auseinanderhält.

**Gut genug wenn:** 9.16 und 9.17 stehen mit Status und Verweisen, der
Strategie-Bericht hängt nicht mehr unter 9.7, `CLAUDE.md:71` sagt die Wahrheit,
die Legal-Seite steht als `manual`-Eintrag in `components.json` — und die vier
Hora-Zahlen liegen vor, ohne dass an Hora etwas geändert wurde.
