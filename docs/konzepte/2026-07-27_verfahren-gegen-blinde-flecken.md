# Verfahren gegen blinde Flecken

**Die Fragenliste als fester Bestandteil jedes Bauauftrags — mit Abnahmekriterium und
Gegenlesung**

**Verfasst von:** Claudia (Bot-Sitzung, VPS)
**Für:** Adam — und zum Weiterreichen an Conni (Prüfung) und Mick (Umsetzung)
**Datum:** Montag, 27.07.2026
**Auftrag:** Adams Sprachnachricht vom 27.07., 11:30 Uhr, bestätigt um 11:42 Uhr

---

## 1. Warum es dieses Papier gibt

Adam, wörtlich:

> „Wie kriegen wir es hin, dass du möglichst auch um diese Ecken denkst und diese Kausalketten
> — dass du quasi immer fragst, was ist dafür notwendig, dass gewisse Ergebnisse erreicht
> werden? Dann musst du halt zurückprüfen. Dann guckst du: Okay, was brauchst du dazu? Und dann
> gibt es einfach eine Kausalkette rückwärts, Ursache und Wirkung. Und du musst rückwärts
> prüfen, was kann passieren oder was könnte das beeinflussen."

Und die Begründung, die den Auftrag trägt:

> „Ich finde es ja gut mitzudenken, das ist ja auch wichtig — so komme ich auch in die Prozesse
> rein und bleibe drin und habe auch das Gefühl, ich verstehe, was passiert. So gesehen ist das
> nicht grundlegend verkehrt, aber da sind mir noch zu viele Fehler, die hier passieren."

Adams Mitdenken soll also **bleiben** — es soll nur nicht länger die **Fehlersuche** sein.

---

## 2. Der Befund, aus dem das Verfahren entsteht

Am Vormittag des 27.07. hat Adam mit drei beiläufigen Zurufen zwei echte Mängel in einer
fertigen Vorlage aufgedeckt. Beide sind belegt, nicht behauptet:

**Erster Fall (11:11 Uhr) — „gilt das auch für alles, was noch dazukommt?"**
Der vorhandene Wächter prüfte eine **fest eingetragene Liste von sieben Namen**; ein achtes
Modul wäre durchgefallen. Für neu hinzukommende Komponenten — ein fremdes Paket, ein
Systemwerkzeug, ein Container — existierte **überhaupt kein** Vollständigkeitsprüfer, nur die
Bitte, sie einzutragen.

**Zweiter Fall (11:22 Uhr) — „was, wenn eine Bezugsquelle wegfällt?"**
Antwortet eine Quelle nicht, schreibt der Monitor das ins Protokoll und **meldet es nicht** —
gemeldet wird ausschließlich, wenn es Neues gibt. Eine weggebrochene Quelle stünde fortan
stumm in einer Datei, die niemand liest.

**Beide Fälle haben dieselbe Signatur.** Es war nie ein lauter Fehler, sondern **ein Ausbleiben,
das wie Ruhe aussieht**: eine Prüfung, die nie stattfindet; eine Meldung, die nie ankommt; ein
Zeitgeber, der nie wieder läuft. Von außen ist das nicht von „alles in Ordnung" zu
unterscheiden.

**Der Mechanismus, kurz:** Geprüft wird zuverlässig **der Fall, der vorliegt** — nicht die
Fälle, die **eintreten können**.

---

## 3. Die Fragenliste

Fünf Fragen, kurz genug, dass sie wirklich durchlaufen werden. Sie werden **vor der
Auslieferung** beantwortet, nicht nachträglich.

**① Rückwärts vom Ziel.**
Was muss alles wahr sein, damit das gewünschte Ergebnis eintritt? Nicht „was baue ich",
sondern „was ist notwendig". Jeder Punkt der Liste wird abgehakt oder ausdrücklich als offen
benannt.

**② Der nächste Fall.**
Gilt das auch für das, was morgen dazukommt — oder nur für den heutigen Bestand?
*Erkennungsmerkmal:* **Eine Positivliste im Code ist fast immer der Beweis, dass es nicht
gilt.** Wo eine Aufzählung von Namen steht, gehört ein Verzeichnis-Abgleich hin.

**③ Der Fehlerfall.**
Was passiert, wenn dieser Weg nicht funktioniert — und **wer erfährt davon?**
*Erkennungsmerkmal:* Wird ein Fehler nur protokolliert, ist er nicht gemeldet. Ein Protokoll,
das niemand liest, ist kein Prüfer.

**④ Der Wegfall.**
Was, wenn etwas verschwindet — eine Quelle, eine Datei, ein Dienst, ein Recht, eine
Zuständigkeit? Und: Woran erkennt man den Unterschied zwischen „es gibt nichts zu melden" und
„es meldet sich nichts mehr"?

**⑤ Wer prüft die Regel?**
Wenn niemand: Es ist eine Bitte, kein Mechanismus. Das ist die Repo-Regel **R2** im Wortlaut —
„eine Regel ohne Prüfer ist eine Bitte" — hier auf jeden neuen Bauauftrag angewandt.

**Dazu gehört, bei Bausteinen, die ich noch nicht kenne, eine kurze Recherche**, wie andere
dieses Problem lösen, statt es aus dem Bauch zu bauen. Etablierte Verfahren für genau diese
Denkrichtung gibt es — Fehlerbaum-Analyse, FMEA, Pre-Mortem. Wir müssen das Rad nicht neu
erfinden. *(Die drei Verfahren sind mir dem Namen und Grundgedanken nach geläufig; eine
belegte Gegenüberstellung, welches sich für unsere Größenordnung am besten eignet, steht noch
aus und ist als eigener Punkt vermerkt.)*

---

## 4. Das Abnahmekriterium: „Was kann brechen und wer merkt es"

**Jede Vorlage, jedes Konzept, jeder Bauauftrag bekommt einen Pflichtabschnitt mit dieser
Überschrift. Fehlt er, ist die Sache nicht fertig.**

Das ist der entscheidende Unterschied zu einem guten Vorsatz: Ein fehlender Abschnitt ist **von
außen prüfbar**, eine nachlassende Aufmerksamkeit nicht.

**Form:** eine Tabelle mit drei Spalten.

| Bruchstelle | Wirkung | Wer merkt es |
|---|---|---|
| Was konkret schiefgehen kann | Was der Nutzer davon hat | Der Name des Prüfers — oder ehrlich: **„niemand"** |

**Die Zeilen mit „niemand" sind der eigentliche Ertrag des Abschnitts.** Sie sind entweder zu
beheben oder ausdrücklich als hingenommenes Restrisiko zu benennen. Was sie nicht sein dürfen,
ist unerwähnt.

Ein Beispiel aus dem heute gelieferten Bauauftrag zum Gründlich-Umschalter: Bliebe eine einzige
Zeile stehen, die nach jeder Anfrage die Sitzung schließt, hätte im Dauerbetrieb jede Nachricht
keinen Gesprächsfaden mehr. Wer merkt es? Niemand — es sähe nach Vergesslichkeit aus. Genau
deshalb steht es in der Tabelle und hat einen eigenen Abnahmeschritt bekommen.

---

## 5. Wann das Verfahren greift — und wann nicht

**Vollständig (alle fünf Fragen, Pflichtabschnitt, Gegenlesung):**
neue Bauaufträge, Konzepte, Entscheidungsvorlagen, alles Automatische, alles, was unbeaufsichtigt
läuft, jede neue Regel oder Rolle.

**Verkürzt (nur Fragen ② bis ④, kein eigener Abschnitt):**
kleine Korrekturen an Bestehendem, Textänderungen, Aufräumarbeiten.

**Gar nicht:**
Dialog, Auskünfte, Recherchen ohne Bauteil. Ein Verfahren, das überall gilt, gilt bald nirgends —
die Schwelle ist Teil des Verfahrens.

---

## 6. Die Gegenlesung — mit dem Auftrag zu widerlegen

Der wirksamste Hebel ist nicht mehr Anstrengung, sondern **ein Wechsel des Blickwinkels**.
Blinde Flecken findet man nicht durch Gründlichkeit, sondern durch ein zweites Augenpaar.

**Die Kontrollsitzung (Conni) ist dafür da** und hat auf genau diesem Weg schon einmal die
Härtung des Updaters hervorgebracht. Damit sie wirkt, braucht sie den richtigen Auftrag:

> **Nicht** „prüfe, ob das stimmt" — sondern: **„Finde, was daran nicht trägt."** Ausdrücklich
> mit der Erwartung, etwas zu finden. Wer bestätigen soll, bestätigt.

**Wann:** bei allem, was unter Abschnitt 5 „vollständig" fällt und über eine überschaubare
Änderung hinausgeht. Bei der Vorlage vom Vormittag habe ich sie nicht gefragt — das war der
Fehler hinter dem Fehler.

---

## 7. Wer prüft dieses Verfahren?

Die Frage muss sich das Verfahren selbst gefallen lassen, sonst ist es genau das, wogegen es
sich richtet.

1. **Der fehlende Abschnitt fällt beim Lesen auf** — Adam wie Conni sehen sofort, ob die
   Tabelle da ist. Das ist der Prüfer, der sofort funktioniert und nichts kostet.
2. **Maschinell prüfbar, sobald die Ablage steht:** Ein kleiner Wächter kann jede Datei unter
   `docs/entscheidungsvorlagen/` daraufhin abklopfen, ob die Überschrift „Was kann brechen und
   wer merkt es" vorkommt, und Fehlende beim Namen nennen — dasselbe Muster wie der bestehende
   Register-Wächter. Das ist ein Vorschlag, **noch nicht gebaut**; es gehört in die
   Selbsttest-Reihe und damit in den täglichen Vier-Uhr-Check (8.1).
3. **Rückwirkend:** Bestehende Vorlagen bekommen den Abschnitt bei der nächsten Berührung
   nachgereicht, nicht in einem eigenen Durchgang. Sonst wird aus dem Verfahren Verwaltung.

---

## 8. Was an diesem Verfahren brechen kann — und wer es merkt

| Bruchstelle | Wirkung | Wer merkt es |
|---|---|---|
| Der Abschnitt wird zur Pflichtübung, gefüllt mit Belanglosem | Die Tabelle steht da, findet aber nichts — falsche Sicherheit | **Niemand**, solange nur die Anwesenheit geprüft wird. Gegenmittel: Die Gegenlesung fragt ausdrücklich, ob die Tabelle die *wahrscheinlichen* Brüche nennt |
| Die Schwelle aus Abschnitt 5 franst aus, alles bekommt das volle Verfahren | Es wird lästig und dann übergangen | Adam — er merkt es daran, dass Antworten träge werden. Er darf jederzeit „verkürzt" ansagen |
| Die Gegenlesung wird zur Formalie („sieht gut aus") | Der Blickwinkel wechselt nicht wirklich | Am Ergebnis: Eine Gegenlesung, die nie etwas findet, ist selbst der Befund |
| Ich vergesse das Verfahren unter Zeitdruck | Rückfall in den alten Zustand | Der fehlende Abschnitt — deshalb ist er das Kriterium und nicht die Fragenliste, die man im Kopf durchgehen kann, ohne dass es jemand sieht |
| Der Wächter aus 7.2 wird nie gebaut | Das Verfahren hängt dauerhaft an Aufmerksamkeit | **Dieser Punkt selbst.** Er steht hier, damit er nicht still verfällt — der klassische Fall von „vereinbart, aber nicht gebaut" |

---

## 9. Die ehrliche Grenze

Das senkt die Fehlerquote. Es bringt sie nicht auf null. Ein Verfahren kann nur nach den
Fällen fragen, die es kennt; die wirklich neue Ecke findet weiterhin am ehesten ein zweiter
Blick — oder Adam. Der Unterschied zu heute ist nicht Fehlerfreiheit, sondern dass die
**häufigste** Klasse von Fehlern — das stille Ausbleiben — nicht mehr auf Zufall angewiesen
ist, um entdeckt zu werden.

---

## 10. Was zu entscheiden ist

1. **Wird der Wächter aus 7.2 gebaut?** Kosten: gering, eine Selbsttest-Zeile. Nutzen: Das
   Verfahren hängt nicht mehr an meiner Aufmerksamkeit. **Meine Empfehlung: ja**, aber erst
   nach Adams Rückkehr — es ist kein Eilfall.
2. **Wo liegt die Ablage der Vorlagen?** Der Wächter braucht einen festen Ort, um zu wissen,
   was er prüfen soll. Naheliegend ist `docs/entscheidungsvorlagen/` im Bot-Repo.
3. **Gehört die Gegenlesung in jeden Bauauftrag oder erst ab einer Größe?** Mein Vorschlag
   steht in Abschnitt 6; er ist bewusst konservativ, weil jede Gegenlesung Kontingent kostet.

---

**Verwandte Stränge, die zusammengehören und noch nicht zusammengeführt sind:** das
Grundsatzthema vom 26.07. — ein selbstlernendes, selbstkorrigierendes, selbsttestendes System —
und das Regelwerk für alles Automatische. Dieses Papier ist der Baustein „selbstprüfend" davon,
nicht das Ganze.
