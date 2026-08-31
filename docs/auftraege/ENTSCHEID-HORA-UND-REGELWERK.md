<!-- ROLLE: entscheid-automatik -->
# Entscheid: Hora bleibt Läufer — und das Regelwerk dazu

**Kopf:** 31.08.2026, 09:42 (Systemuhr abgelesen) · Kontroll-Sitzung
**Gemessen an:** `717b059` (Micks `f48739c` war bei origin noch nicht sichtbar)
**Ersetzt:** Abschnitt ③ aus `ENTSCHEIDE-MICK-31-08.md` — dort stand „erst
messen, dann entscheiden". **Adam hat entschieden; die Messung bleibt, aber als
Zulieferung, nicht als Tor.**

---

## ⓪ Vorweg: mein Verfahrensfehler

Ich habe eine Entscheidung vertagt, die Adam treffen konnte. Seine Antwort
darauf ist eine **stehende Regel für alles**, und sie gehört ins Grundregelwerk:

> **Wir kommen möglichst auf schnelle Entscheidungen und schieben nicht auf.**
> Ausnahme nur, wenn Adam ausdrücklich sagt „das legen wir hinten ran" — oder
> wenn die Kontrolle den Aufschub **ausdrücklich empfiehlt und begründet.**

Sein Grund ist nicht Ungeduld, sondern gemessen an diesem Projekt:
*„Wir haben keine richtige Sortierung der Dringlichkeiten. Das fällt dann
irgendwie hinten rüber."* **Ein vertagter Punkt ohne Dringlichkeitsordnung ist
ein verlorener Punkt** — dieselbe Mechanik wie beim Ablageweg-Grundsatz, eine
Ebene höher.

**Auftrag B-1: Diese Regel wörtlich in `CLAUDE.md`**, unter der Arbeitsmodus-
Überschrift. Sie ist der zweite Anwendungsfall der Regel, die du heute Nacht
eingetragen hast — *systemweite Entscheidungen gehören ins Drehbuch.*

---

## ① Der Entscheid: F-16 wird verworfen, Hora bleibt Läufer

**Adams Position, sinngemäß im Wortlaut:** *„Natürlich muss Hora einen Nachtlauf
machen können. Wenn alles immer einen manuellen Daumen braucht, ist es zu krass.
Wir müssen dafür klare Regeln haben, dass da nichts schiefgehen kann."*

Das ist die Architekturentscheidung, die dir gehörte und die er jetzt getroffen
hat: **Automatik muss laufen können. Die Sicherheit kommt aus dem Regelwerk,
nicht aus dem Daumen.**

**F-16 in der Einzeiler-Form ist damit erledigt** — sie wird nicht gebaut, sie
geht nicht in eine dritte Runde. Deine Messung, dass sie fünf abgenommene
Prüfzeilen bricht, war das richtige Signal; Adams Entscheid ist die Antwort
darauf.

**Was von F-16 bleibt und ernst zu nehmen ist:** dein eigentlicher Befund, dass
die `art` der **Schreiber selbst deklariert**. Der geht nicht weg. Er gehört in
Abschnitt C des Regelwerks unten, als benannte Lücke — nicht als Grund, den
Läufer abzuschaffen.

---

## ② Das Regelwerk — Auftrag B-2

Neu: **`docs/automatik-regelwerk.md`**, ROLLE `automatik-regelwerk`, mit
Gültigkeits-Kopf nach Regel ⑪ **samt „zuletzt nachgezogen"** (die Lehre aus dem
Fähigkeitsraster).

**Es wird nichts Neues erfunden.** Fast alles steht bereits im Code — verstreut
über `auftragsbuch.py`, `hora.py` und `CLAUDE.md`. **Das Regelwerk sammelt und
benennt es an einem Ort.** Genau das fehlt heute: Es gibt Regeln, aber keine
Stelle, an der jemand nachlesen kann, ob sie zusammen tragen.

### Abschnitt A — was heute gilt (von mir am Code gemessen, `717b059`)

| # | Schranke | Beleg |
|---|---|---|
| 1 | **Geschlossene Absenderliste**, fünf Namen: `claudia · conni · mick · hora · stundenblume`. Unbekannt → `ValueError`, der Auftrag entsteht gar nicht | `auftragsbuch.py:90` |
| 2 | **Geschlossene Artenliste**, vier Arten, jede mit eigenem Prüfdatum. Unbekannte oder fehlende Art → **gelb**, nie grün | `auftragsbuch.py:111` |
| 3 | **Rote Wortsuche** über `titel`, `aktion`, `begruendung` **und `befehl`** — 20 Stichwörter, beidseitig offene Wortgrenzen, kurze benannte Ausnahmeliste | `auftragsbuch.py:165–188` |
| 4 | **Die Einstufung wird mitgeschrieben, nicht bei jedem Lesen neu gerechnet** — ändert sich die Grün-Liste, bleibt nachvollziehbar, unter welcher Regel ein Auftrag hereinkam | `auftragsbuch.py:232` |
| 5 | **Regressionslauf VOR dem Befehl.** Ist er rot, wird nicht gearbeitet — „auf rotem Fundament wird nicht gearbeitet" | `hora.py:617` |
| 6 | **Regressionslauf NACH dem Befehl.** Nur wenn beide grün sind, gilt der Auftrag als erledigt | `hora.py:696` |
| 7 | **Frische Sitzung je Auftrag**, Zeitgrenze 7200 s, Ausgabe verdichtet | `hora.py:681` |
| 8 | **Kontingent erschöpft → anhalten, nicht scheitern.** Auftrag bleibt offen, nichts wird abgehakt, nichts geht verloren | `hora.py:690` |
| 9 | **Schloss** — nur ein Lauf gleichzeitig; **Fehlserien-Zähler** | `hora.py:123, 509` |

### Abschnitt B — die Regel über allen

Aus `CLAUDE.md`, wörtlich zu übernehmen: **Keine Automatik beginnt von sich aus
Arbeit.** Zeitgesteuerte Läufe sind deterministisch oder gar nicht; der eine
zugelassene Ausnahmefall (nachgeholter Lauf nach Limit-Unterbrechung) trägt
seine drei harten Bedingungen im Code.

### Abschnitt C — die Lücken, ehrlich benannt

1. **Die `art` deklariert der Schreiber selbst** (dein F-16-Befund). Die
   Absenderliste heilt das nicht: Ein berechtigter Absender kann sich irren.
   **Als Lücke benennen, nicht schließen** — die Schließung wäre ein Umbau, und
   der braucht Adams Entscheid.
2. **Was ich nicht gemessen habe** und was hineingehört: Wird jeder Lauf einzeln
   committet, sodass ein `git revert` als Rückweg genügt? Gibt es eine
   Obergrenze für Läufe pro Nacht? Was geschieht, wenn ein Auftrag **während**
   des Laufs rot wird?
3. **Jede Lücke bekommt eine Zeile: „gemessen am / offen seit / wer entscheidet".**

### Abschnitt D — Zulieferung, kein Tor

Die vier Zahlen aus dem vorigen Auftrag (grüne Läufe seit 18.08. · davon mit
`befehl` · was sie taten · wie viele unter F-16 gestoppt worden wären)
**wandern in Abschnitt C als Beleg.** Sie halten den Entscheid nicht auf —
**Regelwerk und Messung laufen nebeneinander.**

---

## ③ Grenze — und sie ist hier wichtig

**Kein neuer Wächter, kein neuer Prüfer, keine Änderung an `hora.py` oder
`auftragsbuch.py`.** Das Regelwerk ist ein **Dokument**. Wer beim Schreiben
merkt, dass eine Schranke fehlt, **schreibt sie in Abschnitt C und baut sie
nicht** — sonst wird aus „Regeln aufschreiben" unbemerkt „Regeln ändern", und
das ist genau der Weg, auf dem F-16 fast fünf Prüfzeilen gekostet hätte.

**Und die Nummern haben sich verschoben:** Dein `f48739c` hat 9.16 an den
Gegenleser vergeben. Der Notfallplan wird damit **9.17**, die Weitergabe
**9.18** — bitte an deinem Stand nachzählen statt meiner Zahl zu vertrauen.

**Gut genug wenn:** Die schnelle-Entscheidungen-Regel steht in `CLAUDE.md`, das
Regelwerk liegt mit Rollen-Marker und Gültigkeits-Kopf im Repo, Abschnitt A ist
am Code belegt statt behauptet, Abschnitt C nennt die Lücken **einschließlich
der drei, die ich nicht gemessen habe** — und an `hora.py` wurde nichts
geändert.
