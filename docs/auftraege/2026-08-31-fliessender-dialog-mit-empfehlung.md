> **Zweck: ANSICHT + ENTSCHEID** · **Zu tun:** lesen; **fünf Empfehlungen zum
> Abnicken**, plus eine Frage zur Hardware. Nicht an Mick — noch nichts zu bauen.

# Der fließende Dialog — vorgelegt mit Empfehlung

**Stichtag:** 31.08.2026, 23:39 MESZ (Systemuhr abgelesen; Container auf UTC)
**Anlass:** Deine Bitte über Claudia um 23:25 Uhr — das Konzept noch einmal
vorgelegt, *„ausdrücklich verbunden mit Empfehlungen"*.

---

# ⚠️ Zuerst der Befund über meinen eigenen Befund

**Ich habe in den letzten Stunden mehrere Dinge als „Lücke" gemeldet, die es
nicht sind.** Der Grund ist derselbe wie sechsmal zuvor: **mein Raster war zu
eng.** Ich habe `MIGRATION.md`, `CLAUDE.md`, `docs/*.md` und
`docs/entscheidungsvorlagen/` durchsucht — **aber nie `docs/auftraege/` und
`docs/konzepte/`.** Dort liegen **drei fertige Konzepte** vom 26.–28.07.

| Konzept | Umfang | Deckt meine gemeldeten „Lücken" |
|---|---|---|
| `2026-07-27_konzept-fliessender-dialog.md` | 13,2 KB | ⑧ Vermittler · ⑨ eigene Oberfläche · ⑩ Weglegbarkeit · ⑪a Werte-Termin |
| `2026-07-26_konzept-handlungsfaehigkeit.md` | 28,1 KB | ① Zusatzguthaben-Auflage · ② laufende Prozesse anhalten |
| `2026-07-28_konzept-entwicklungskette-automatisieren.md` | 9,1 KB | ⑲ Übergabeweg zwischen Sitzungen |

**Und sie sind nicht dünn.** Die Weglegbarkeit hat ein eigenes Kapitel mit dem
Satz *„Wenn eine Lösung nur funktioniert, solange sie benutzt wird, ist sie die
falsche."* Der Sparmodus steht in Stichpunkten ausformuliert — *anhalten statt
abbrechen, Zwischenstand sichern, kleinstes taugliches Modell*. Der
Reserve-Topf hat Zahlen und eine Reihenfolge-Empfehlung. **Das ist besser
ausgearbeitet als das, was ich als fehlend gemeldet habe.**

## Was daraus als Befund übrig bleibt — und er ist schärfer als meiner

**Gemessen:** Die Zeichenketten `fliessender-dialog`, `entwicklungskette` und
`konzept-handlungsfaehigkeit` kommen in `MIGRATION.md` **null Mal** vor.

> **Rund 50 KB durchdachte Konzeptarbeit, fünf Wochen alt, mit Zahlen,
> Stufenplänen und Entscheidungsfragen — und das Drehbuch kennt keines davon.**

Claudia hat denselben Befund heute Abend unabhängig gemacht: *„Deshalb lag es
fünf Wochen, ohne dass eine Sitzung es einplanen konnte."* **Zwei Sitzungen,
zwei Wege, ein Befund** — das ist die belastbarste Form, die wir haben.

**Es ist dieselbe Klasse wie alles andere heute, nur eine Größe größer:** Beim
Bot-Gedächtnis waren es sechs Verhaltensregeln ohne Weg ins Drehbuch. Hier sind
es drei ganze Konzepte. **Das Muster heißt nicht „vergessen", es heißt „kein
Ablageweg".**

## Was von meinen Lücken bleibt

**Es fallen:** ① ② ⑧ ⑨ ⑩ ⑪a ⑲ — sie existieren, sie hängen nur nicht.
**Es bleiben, geprüft auch gegen die neuen Ordner:** ⑫ eigene KI (dazu deine
Revision von heute) · ⑬ Vorlese-Regeln · ⑭ Bilder liefern · ⑮ und ⑰
Zeit-Auslegung und Zeitschätzungen · ⑯ Dateinamen-Regel *(als Regel nirgends
notiert — **aber in `docs/auftraege/` längst praktiziert**, und Claudia hält
sich daran; ich war der einzige, der es nicht tat)* · ⑱ Hora-Unterbrechbarkeit ·
⑳ Vertrag · ㉑ Personen-Namen.

**Das ändert die Zahl, nicht die Richtung** — und macht die Ursache eindeutiger.

---

# Die fünf offenen Punkte — meine Empfehlung zu jedem

## 1 · Die Leitplanke vom 12.07. — **sie bleibt, der Entwurf passt sich an**

**Der Konflikt:** Dein Entwurf verlangt eine Instanz **vor** dem Hauptagenten.
Die Leitplanke F1 legt fest, dass er **direkt am Abo-SDK** läuft und
ausdrücklich **nicht** durch LiteLLM.

**Meine Empfehlung ist hier ungewöhnlich deutlich, weil es nicht um Geschmack
geht:** Die Leitplanke ist **keine Architekturvorliebe, sondern die
Kostenregel in technischer Form.** Den Hauptagenten durch LiteLLM zu führen
hieße entweder einen API-Schlüssel (bucht Geld ab, getrennt vom Abo) oder
Abo-Zugangsdaten durch einen Vermittler zu leiten — und **genau das** benennen
die Nutzungsbedingungen als Drittanbieter-Routing, seit dem 04.04.2026
technisch durchgesetzt, Sperrungen *„without prior notice"*.

**Wörtlich umgesetzt würde dein Entwurf den Abo-Zugang riskieren.**

**Und das ist kein Nein zu deinem Gedanken**, sondern eine Verschiebung um eine
Ebene:

> **Die Vermittlerin muss nicht vor dem Modell stehen — sie kann ein zweiter
> Strang daneben sein.** Zwei Sitzungen, **beide direkt am Abo-SDK**: eine
> spricht, eine arbeitet. Dazwischen ein **deterministischer Verteiler** (Code,
> kein Modell) und der gemeinsame Zustandsspeicher. LiteLLM bleibt, wo es ist —
> bei den Neben-Inferenzen.

Das erfüllt deine Anforderung vollständig (*ein Halbsatz bekommt sofort
Antwort, während im Hintergrund gearbeitet wird*), ohne die Leitplanke
anzufassen. **Es ist zugleich genau das, was Kapitel 8 des Konzepts selbst
vorschlägt** — der Konflikt aus Punkt 1 löst sich damit auf, statt entschieden
werden zu müssen.

## 2 · Wo lebt der gemeinsame Zustand — **VPS beginnen, Heimgerät als Ziel**

Das Konzept sagt richtig: Der VPS gehört Netcup, nicht dir. **Aber den
Zustandsspeicher an den Heimtunnel zu binden, würde alles blockieren** — der
Tunnel ist seit dem 15.08. fällig und nicht gebaut.

**Empfehlung:** auf dem VPS anfangen, **den Umzugsweg beim Bau mitschreiben**,
und nichts hineinlegen, was nicht ohnehin schon dort liegt (die Tagesprotokolle
liegen es seit dem 14.07.). Dann kostet der spätere Umzug einen Tag statt eines
Neubaus.

**⚠️ Hier treffen sich drei offene Fäden an einer einzigen Entscheidung** —
und das ist der eigentliche Ertrag dieser Vorlage:

1. der **Heimtunnel** (beschlossen, überfällig),
2. mein Block-7-Fund: das **Heimgerät als zweites Sicherungsziel** (heute lässt
   4.1 die Sicherung allein am eingeschalteten Mac hängen),
3. **Kapitel 7 Punkt 5 des Handlungsfähigkeits-Konzepts**, das die
   Hardware-Frage schon am 26.07. als *drängend* markiert hat — *„mindestens
   24 Gigabyte, besser 32, weil nicht nachrüstbar."*

**Das ist eine Anschaffung, keine drei.** Die Frage dazu steht unten.

## 3 · Wie viel Parallelität — **zwei Stränge, nicht mehr**

**Uneingeschränkte Zustimmung zu Kapitel 8.** Zwei Stränge beantworten die
eigentliche Frage — *bleibt der Faden erhalten, wenn Gespräch und Arbeit
getrennt laufen?* — und zwar vollständig. Trägt es bei zweien, trägt es bei
fünf; trägt es nicht, ist wenig verloren.

**Ein Zusatzgrund, den das Konzept nicht nennt:** Das Fünf-Stunden-Kontingent
ist ein **gemeinsamer Topf aller Sitzungen**. Beliebig viele Stränge sind nicht
nur Koordinationsaufwand, sie nehmen den Einkommensprojekten das Kontingent
weg. Zwei ist auch aus diesem Grund die richtige Zahl.

## 4 · Interface — **zurückstellen, und zwar mit Begründung, nicht aus Trägheit**

**Empfehlung: nicht jetzt.** Die eigene Oberfläche ist das **teuerste und am
wenigsten umkehrbare Stück** des ganzen Entwurfs — und der Zwei-Strang-Versuch
braucht sie nicht: Über Telegram lässt sich vollständig messen, ob der Faden
die Trennung überlebt. **Erst wenn er es tut, lohnt eine Oberfläche.**

**Was dabei ausdrücklich nicht verlorengehen darf:** Deine drei begründet
verworfenen Wege stehen bereits in Kapitel 5 (kein Dauergerät am Handgelenk,
kein Knopf im Ohr, nicht ständig das Telefon in der Hand). **Das ist Vorarbeit,
die niemand zweimal leisten muss** — sie war der Grund, warum ich diesen Punkt
überhaupt als Lücke gemeldet hatte.

## 5 · Reihenfolge — **zustimmen, aber der erste Schritt ist ein anderer**

Das Konzept sagt: Vermittlerin und Dirigent sind dieselbe Sache und dürfen
nicht nacheinander gebaut werden. **Richtig, und ich stimme zu.**

**Aber der erste Schritt ist keiner von beiden.** Das
Handlungsfähigkeits-Konzept führt einen **Stufenplan**, und dort steht der
Dirigent als **Stufe 5, Aufwand groß**. Davor liegen zwei Stufen, die
**kostenfrei** sind und sofort nützen:

- **Stufe 1** — die belegten Lücken schließen. Claudias eigene Empfehlung dazu:
  *„ja, ohne weitere Rückfrage."*
- **Stufe 2 — der Sparmodus.** Genau das, was du am 26.07. verlangt und am
  28.07. nach dem verlorenen Tag wiederholt hast: *laufende aufwendige Vorgänge
  anhalten statt abbrechen, Zwischenstand sichern, Gespräch bleibt möglich.*
  **Und er hängt an keiner Architekturentscheidung.**

**Dazu die Reihenfolge-Auflage aus dem Konzept, die ich für zwingend halte:**
*Sparmodus vor Reserve-Topf. Wer den Topf zuerst aktiviert, hebt den gerade
gebauten Schutz unbemerkt auf.* Das deckt sich mit deinem eigenen Entscheid vom
26.07. — *deaktiviert lassen, nur als Notfall*.

---

# Meine Gesamtempfehlung — das eine, was zuerst geschieht

**Nicht die Architektur.** Der größte Verlust liegt gerade woanders:

> **Die drei Konzepte bekommen einen Platz im Drehbuch — heute noch, als
> Verweis, ohne dass irgendetwas gebaut wird.**

Solange sie unverlinkt liegen, wird ihr Inhalt **wieder und wieder neu
hergeleitet.** Ich habe heute mehrere Stunden damit verbracht, Dinge als fehlend
zu melden, die seit fünf Wochen ausgearbeitet dastehen. **Das ist die Rechnung
für einen fehlenden Verweis** — und sie fällt bei jeder Sitzung erneut an.

**Danach, in dieser Reihenfolge:** Stufe 1 → Sparmodus → Zwei-Strang-Versuch →
alles Weitere.

---

# Die eine Frage an dich

Alles andere oben kannst du abnicken oder ändern. **Diese eine kann ich nicht
für dich beantworten**, und sie ist seit dem 26.07. offen:

> **Hast du inzwischen ein Heimgerät gekauft — und wenn nein: soll es eines
> sein, das alle drei Aufgaben trägt?**
> Heimtunnel · zweites Sicherungsziel · später der lokale Vertreter.
> Falls ja: **mindestens 24 GB, besser 32** — nicht nachrüstbar.

**Meine Empfehlung: ein Gerät für alle drei**, sofern das Budget es hergibt.
Drei Einzelgeräte wären teurer und drei Ausfallwege statt einem.

💰 **Ausdrücklich eine Kostenfrage** — ich nenne keine Summe, weil ich keine
gemessen habe; die Preislagen stehen in Kapitel 5.3 des
Handlungsfähigkeits-Konzepts. **Nichts davon wird ohne deine ausdrückliche
Freigabe angefasst.**

---

**Und eine Vorsichtsnote zum Schluss, aus heutigem Anlass:** Diese Konzepte
sind **fünf Wochen alt**. Du hast heute Abend die eigene KI revidiert, weil sich
die Einschätzung geändert hat. **Prüf beim Abnicken bitte mit, ob die Annahmen
noch gelten** — besonders die Hardware-Preislagen und die Frage, ob der
Heimtunnel überhaupt noch der Weg ist.
