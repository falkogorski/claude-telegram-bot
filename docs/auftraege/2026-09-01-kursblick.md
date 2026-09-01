<!-- ROLLE: kursblick -->
# KURS-BLICK — 29.08. bis 01.09.2026

**Wofür diese Datei da ist:** Adams wöchentlicher Kurs-Blick (CLAUDE.md, Kurs-Regel ①).
**Für dich zur Ansicht.** Kein Auftrag, keine Weitergabe an Mick.
Der Teil, der Mick betrifft, steht am Schluss als **eine** Zeile.

**Stichtag:** 01.09.2026, 23:31 · **Letzter Commit:** 01.09.2026, 21:55 · `6d379fe`
**Fenster:** 29.08.2026, 19:11 (Commit des letzten Kurs-Blicks) bis 01.09.2026, 21:55
**Nenner:** 85 Commits, 3 Tage · **Vorlage:** `KURSBLICK-2026-08-29.md`

---

## ⚠️ Zwei Berichtigungen vorweg — beide meine

**① Dies ist nicht der erste Kurs-Blick.** Ich hatte dir heute Nacht angeboten,
„den ersten" zu machen, weil ich meinte, der Termin vom 25.08. sei ausgefallen.
Falsch: `docs/auftraege/KURSBLICK-2026-08-29.md` liegt im Repo, dazu
`docs/kursblick-zahlen-2026-08-25.md`. **Das hier ist der zweite**, und er misst
gegen den ersten. Gefunden habe ich es, weil ich vor dem Schreiben nachgesehen
habe — die Prüfregel *Status ist ein Befund* hat gehalten.

**② Die Leitfrage dieses Kurs-Blicks stimmt nicht mehr.** Sie lautet seit dem
19.08.: *„Was haben wir diese Woche für Einkommen getan?"* — **Du hast sie am
31.08. selbst außer Kraft gesetzt:** *„Das hier ist noch weit weg von
Einkommensgenerierung."* Deine laufenden Einkommensprojekte sind ein anderer
Ort, der Name *Einkommensstrang* ist zurückgezogen (Drehbuch 9.18). Ich messe
die Zahl unten trotzdem, weil sie eine andere Frage beantwortet, und schlage am
Schluss eine neue Leitfrage vor. **Die Frage gehört dir, nicht mir.**

---

## 1 · Die vier Körbe

Gewichtet nach **Arbeitsumfang** (1 klein / 2 mittel / 4 groß, geteilte Commits
geteilt eingetragen). **Nenner: 85 Commits = 144 Gewichtspunkte.**

| Korb | Gewicht | Anteil | 29.08. | Richtung |
|---|---:|---:|---:|---|
| ⬜ **Einkommen** | 0 | **0,0 %** | 0 % | gleich |
| 🔄 **Stabiler Selbstläufer** | 13 | **9,0 %** | 4,5 % | ↗ doppelt |
| 🔄 **Adams Alltag** | 14 | **9,7 %** | 44 % | ↘ stark gefallen |
| ✅ **Innenarbeit** | 117 | **81,2 %** | 51 % | ↗ stark gestiegen |

**Gegenprobe ohne Gewichtung** (jeder Commit zählt 1): Innenarbeit **85,3 %**,
Selbstläufer 8,2 %, Alltag 6,5 %, Einkommen 0 %. **Die beiden Verfahren liegen
vier Punkte auseinander** — die 81 % sind also kein Artefakt meiner Gewichtung.

**Was das nüchtern heißt:** Vier von fünf Arbeitseinheiten dieser drei Tage
gingen in Befunde, Prüfer, Drehbuch und Ablage. Das ist der höchste Wert, den
dieser Kurs-Blick je gemessen hat — 51 % vorige Woche, 60 % in deren engstem
Fenster, jetzt 81 %.

**Und was ihn erklärt, bevor du ihn als Alarm liest:** Diese drei Tage waren
per Auftrag Innenarbeit. Du hast die Gesamtprüfung aller Logs angeordnet und
sie ausdrücklich auf *alle* Logs ausgeweitet. Eine Woche, die aus einem Audit
besteht, misst 81 % Innenarbeit, ohne dass jemand vom Kurs abgekommen wäre.
**Der Wert ist richtig gemessen und als Alarm falsch gelesen.**

**Der Wert, den ich stattdessen ernst nehme, ist der Alltags-Korb: 44 % → 9,7 %.**
Was dort ankam, ist trotzdem greifbar — der **Genehmigungs-Umschalter** (5.27:
ein Knopf, der zwischen Rückfrage und Auto umschaltet) und der **dritte Knopf**
im Freigabe-Postfach (9.4: du schreibst die Zeile selbst, über die du urteilst).
Zwei Dinge, die du in der Hand hast. Aber es sind zwei.

---

## 2 · Die Zahlen der Kurs-Regel

| Messgröße | Diese Woche | 29.08. | Bewertung |
|---|---:|---:|---|
| **Neue Wächter** | **1** | 4 | ✅ deutlich gebremst |
| **Prüfrunden über Limit** | **0** | 2 | ✅ Bremse hat gehalten |
| **Prüfdateien** (`scripts/test_*`) | 49 → **55** | 37 → 48 | 🔄 +12 % statt +30 % |
| **Prüfzeilen im Regressionslauf** | 62 → **68** | 49 → 60 | 🔄 +10 % statt +22 % |

**Der eine neue Wächter** ist `scripts/ausarbeitungen_pruefen.py` — der Prüfer
gegen Karteileichen in der Ablage. Er läuft im Tagescheck und schreibt ins
Auftragsbuch. Ein echter Vorfall stand dahinter (Papiere, die seit Wochen als
„in Arbeit" geführt wurden), und kein bestehender Wächter war erweiterbar.
**Die Bedingung der Kurs-Regel ist erfüllt.**

**Die Konvergenz-Bremse hat zweimal sichtbar gegriffen** — und das ist der
Befund, über den ich mich am meisten freue:
- **F-16** wurde gemessen und **zurückgenommen**: der vorgeschlagene Einzeiler
  war in Wahrheit eine Architekturfrage.
- **F-9 wurde gekippt**: die vorgeschlagene Reparatur hätte die Kostenschranke
  gebrochen.

Zweimal ist ein Befund gemessen und **nicht gebaut** worden. Genau dafür ist die
Bremse da. Vorige Woche hat sie zweimal versagt; diese Woche kein einziges Mal.

**Ehrlich zur Messmethode:** „Prüfrunden über Limit" lässt sich aus
Commit-Titeln nicht sauber ablesen. Ich habe deshalb wie vorige Woche über
**Dateien mit vier oder mehr Berührungen** gemessen — es sind zwei
(`test_zielumgebung.sh`, `test_uebersprungen_a1.py`) — und jede einzeln
angesehen. Beide tragen **verschiedene** Befunde, nicht denselben mehrfach. Der
einzige echte Reparatur-der-Reparatur-Fall (`Rang 3: meine eigene Reparatur
hatte den Prüfer blind gemacht`) ist Runde drei und damit **am** Limit, nicht
darüber.

---

## 3 · Die beiden Vormerkungen vom 20.08.

### ① Stehende Stichprobe gegen die Ablage — **Falschquote 0 %** (0 von 10)

Zehn zufällig gezogene Ablage-Behauptungen, jede am Code gehalten. **Alle zehn
stimmen** — `test_stall_5_18.py`, `check_hilfe_buttons.py` in beide Richtungen,
`process_user_text` als ein Trichter (sechs Aufrufer), `last_activity` monoton
je Mailbox, die Siebenerliste in `_c_register_vollstaendig`, `reactions.py` mit
genau 24 Einträgen und VS16-Normalisierung, `ampel.py` samt registriertem
`/ampel`, die Meta-Zeile „🎙️ Sprachnachricht (M:SS)" im Gesprächs-Log,
`QueuedJob` mit `update=None`. Vorige Woche: 10 %.

**Und jetzt der Teil, der mehr wert ist als die Quote — denn die Stichprobe hat
einen Schlagseiten-Fehler, den ich selbst gebaut habe.** Ich habe aus Zeilen
gezogen, die einen **Datei- oder Funktionsnamen** nennen. Das sind die am
leichtesten prüfbaren und deshalb die am besten gepflegten Behauptungen. **Null
Prozent misst hier nicht die Ablage, sondern meine Ziehung.**

Denn im selben Fenster wurden **dreizehn** Falschaussagen in der Ablage gefunden
und berichtigt — und **keine einzige davon war eine Code-Referenz.** Alle
dreizehn waren Prosa über Status und Struktur: dass es einen AGB-Wachposten
gebe (es gab ihn nicht) · dass 4.3 die Ordnerspiegelung sei · eine
Entrümpelungs-Regel mit einer Zahl von vorgestern · ein Nachtblock, der längst
gebaut war, ohne dass Katalog und Betriebslage es wussten · eine Doppelnummer
7.4 · ein Erinnerungskanal, der als Zimmer geführt wurde · sechs falsche Zeilen
im Raster · eine Nummernkollision bei 9.17/9.18 · ein Register-Eintrag für ein
Paket, das nicht mehr da ist · ein Wachposten-Eintrag, der sagte, was er *nicht*
tut.

**Daraus die Änderung für nächste Woche, und sie ist der eigentliche Ertrag
dieser Zeile:** Die Ziehung wechselt von Code-Referenzen auf **Status- und
Strukturaussagen** — „ist gebaut", „läuft", „ist Punkt X", „seit". Dort sitzen
die Fehler. **Die Ablage irrt sich nicht über den Code, sondern über sich
selbst.**

### ② Adams Stutzen — **5 Eingriffe, davon 3 gekippte Befunde, in einer Nacht**

Die Vormerkung fragt, woran deine Treffer erkennbar sind, **bevor** du sie
aussprichst. Diese Nacht liefert die erste harte Zahl — und sie ist unbequem:

| Deine Frage | Was sie umgestoßen hat |
|---|---|
| „aus den Erkenntnissen der Blöcke 14–15 erfolgt nichts für Mick?" | Ein Auftragspapier fehlte, das ich für erledigt hielt |
| „warum und seit wann muss ich so etwas nachfragen?" | Fünf von acht Julilücken waren nie beauftragt |
| „Ist es dann auch wirklich komplett? Alles, Bisher?" | Claudias Sitzung ungeprüft; von fünf Papieren ein Viertel eines Papiers gelesen |
| „das konnte Conni irgendwie besser" (MD-Kennzeichnung) | Eine fehlende Gewohnheit, kein gekippter Befund |
| „Passiert hier noch was?" | Die Sitzung stand still |

**Das Muster ist in allen drei gekippten Fällen dasselbe, und es ist benennbar:
Ich melde Vollständigkeit für den Teil, den ich gerade bearbeitet habe, und
prüfe die Menge nicht, zu der er gehört.** Blöcke 14–15 ✓ — aber „hat jeder
Block ein Auftragspapier?" ungefragt. Julilücken gefunden ✓ — aber „ist jede
beauftragt?" ungefragt. Claudias Papier gelesen ✓ — aber „wie viele sind es?"
ungefragt.

**Das ist die Mengen-Regel dieses Projekts, angewandt auf meine eigene
Arbeitsmeldung** — dieselbe Regel, deren Verletzung ich diese Woche bei
`_c_register_vollstaendig` als Befund aufgeschrieben habe. Ich habe sie am Code
gemessen und an mir selbst nicht.

**Antwort auf die Vormerkungsfrage, so konkret ich sie geben kann:** Deine
Treffer sind daran erkennbar, dass meine Fertigmeldung **einen Bearbeitungsstand
nennt statt einer Menge**. Die Prüffrage vor jedem „fertig" lautet ab sofort:
*Wie viele sind es insgesamt, und habe ich alle?* Sie steht als N-30 in
CLAUDE.md — und dies ist die Messung, die sie rechtfertigt.

---

## 4 · Die Einkommens-Zeile

**Gemessen: 0 %.** Sechste Woche in Folge.

**Aber der Grund hat diese Woche seinen Namen gewechselt, und das ist der Fund:**
Der Kurs-Blick hatte fünf Wochen lang null Erlösbezug gemessen und die Ursache
im **Arbeitsverhalten** gesucht — wir arbeiten zu viel nach innen. Am 30.08. hat
ein quer geschnittenes Suchraster gefunden, dass sie in der **Ablage** lag:
`momo-business-skizze.md` und `momo-gruendungserzaehlung.md` standen bis zum
31.08. **ohne jeden Drehbuch-Eintrag** da. Was keinen Punkt hat, wird nicht
abgearbeitet.

**Seit dem 31.08. haben sie einen** — Punkt **9.18 Weitergabe**, aus deinem
Entscheid, mit deiner Korrektur darin: der Punkt trägt nur Status und Verweis,
die Ausarbeitung entsteht **extern**, Geschäft und Technik bleiben getrennt,
Status ausdrücklich **nicht terminiert**.

**Damit ist die Null erklärt und nicht mehr besorgniserregend — und die
Leitfrage dieses Kurs-Blicks trifft ins Leere.** „Was haben wir für Einkommen
getan?" fragt nach etwas, das dieses Projekt laut deiner eigenen Festlegung
nicht liefern soll.

**Mein Vorschlag für die neue Leitfrage — deine Entscheidung:**

> **„Hat dieses Projekt diese Woche Zeit oder Kontingent verbraucht, die deine
> Einkommensprojekte gebraucht hätten?"**

Das ist die W-Regel in ihrer tragfähigen Form: nicht *zahlt es ein*, sondern
*nimmt es weg*. Und sie ist messbar — der Blocktakt vom 20.08. ist genau dafür
gebaut („nicht durchballern", Raum für andere Prozesse). **Für diese Woche kann
ich sie nicht beantworten:** Ich sehe die Commits dieses Projekts, nicht deinen
Kontingentstand über alle Sitzungen. Wenn du sie beantwortet haben willst,
braucht sie eine Messstelle.

---

## 5 · Der Blick auf die Kurs-Regel selbst

**Sie greift.** Beide Zahlen, die sie überwacht, gehen in die richtige Richtung
— neue Wächter 4 → 1, Prüfrunden über Limit 2 → 0. Das Wachstum der Prüfmenge
hat sich mehr als halbiert (+30 % → +12 %). Und die Bremse hat zweimal
sichtbar gehalten, statt einen Befund in Code zu verwandeln.

**Der 81-Prozent-Wert ist trotzdem der, den ich in vier Tagen wieder messen
will** — nicht als Alarm für diese Woche, in der ein Audit beauftragt war,
sondern als Frage an die nächste: Wenn eine Woche ohne Audit-Auftrag wieder
über 60 % Innenarbeit liegt, ist es kein Auftrag mehr, sondern ein Kurs.

---

## 6 · Offene Entscheidungen und Wartepunkte

| # | Was | Zustand |
|---|---|---|
| 1 | **Leitfrage des Kurs-Blicks** ersetzen (Abschnitt 4) | ⬜ **wartet auf dich** |
| 2 | **Vorlese-Weg**: `num2words` jetzt oder 9.1 Azure abwarten | ⬜ wartet — 💰 bei Azure |
| 3 | **Kontingent-Warnstufen**: meine Empfehlung nur 80 und 95 | ⬜ wartet |
| 4 | **venv-Befehlsblock** (root) — deine Hand | ⬜ wartet |
| 5 | **Fließender Dialog** — vertagt, Wiedervorlage 05.09. | ⏭️ liegt terminiert |
| 6 | **Werte-/Zieltermin** — Wiedervorlage | ⏭️ liegt terminiert |

---

## 7 · Die eine Zeile für Mick

**Nichts.** Dieser Kurs-Blick erzeugt keinen Bauauftrag — er misst, er baut
nicht. Die Änderung an der Stichproben-Ziehung (Abschnitt 3 ①) ist meine
eigene Arbeitsweise und gehört in keine fremde Sitzung.

**Freigegeben und weiter bei Mick liegend** (aus den Nachtblöcken, unverändert):
Pipe-Zerlegung mit der Boden-Bedingung · zweiter Chat · „Auswerten"-Knopf.
