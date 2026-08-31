<!-- ROLLE: freigabe-nachtblock -->
# Freigabe für den Nachtblock — Mick, Nacht zum 31.08.2026

**Kopf:** 30.08.2026, 23:58 (Systemuhr abgelesen) · von der Kontroll-Sitzung
**Gehört zu:** `AUFTRAG-MICK-standsuebersicht.md` — **diese Datei geht vor**,
wo beide sich berühren.

---

## Warum es diese Datei gibt

Der Auftrag verlangt in seinem Tor, dass du erst prüfst und dann baust. **Richtig
gedacht, aber so gebaut, dass du um halb eins stehenbleibst:** Der Weg von dir zu
mir läuft über Adam, und Adam schläft. Auf eine Freigabe von mir zu warten hieße,
die Nacht zu verlieren — und das ist der teurere Fehler.

Adam hat mir die Freigabe für genau diesen Fall ausdrücklich übertragen. Sie
steht hier, im Voraus, damit du **durchgehend arbeiten kannst, ohne auf jemanden
zu warten.**

---

## ① Die Entscheidungsregel — sie ersetzt meine Freigabe

Das Tor bleibt: **prüfen vor bauen, Punkt für Punkt.** Was danach kommt,
entscheidest du selbst, nach dieser Regel:

| Dein Prüfergebnis | Was du tust |
|---|---|
| Befund **bestätigt** | **Bau ihn.** Keine Rückfrage. Das ist der Regelfall. |
| Befund **gekippt** | **Bau ihn nicht.** Notiere, was du stattdessen gemessen hast, geh zum nächsten. Kein Halt. |
| Befund **unklar** | **Nicht bauen, parken.** Ans Ende des Berichts. Unklar ist kein Grund zu warten — nur einer, nichts anzufassen. |
| **Neuer** Fund derselben Klasse (Ablage-Defekt, klein, mechanisch) | Bau ihn mit, nenn ihn im Bericht. |
| Neuer Fund **anderer** Klasse | Nur notieren. |

**Nichts davon blockiert etwas anderes.** Ein gekippter Befund hält die übrigen
vier nicht auf — das ist die Durchlauf-Regel, angewandt auf meine eigenen
Messungen.

**Und wenn du alle fünf kippst, ist das ein gültiges Ergebnis**, kein Anlass zur
Rückfrage. Dann steht im Bericht, dass meine Übersicht auf fünf falschen Füßen
stand, und Teil C verankert sie nicht, bis das geklärt ist.

---

## ② Was den Rest der Nacht füllt

Teil A bis C sind zusammen vielleicht eine Stunde. **Der Nachtblock ist etwas
anderes, und er steht seit dem 28.08. bereit:**

### Hauptstück — die acht blinden Rang-A-Prüfzeilen

`docs/befund-entkernung.md`, Zeilen 67–90. **Acht Prüfzeilen, die einen stillen
Bruch heute nicht bemerken würden** — die Boten-Postfach-Geheimnisschranke, die
WebSearch-Kostenschranke, der Zustellnachweis, der Wächter-Start, der
Medien-Eingangsschutz, die Limit-Rücklage, der Start-Wächter im Detach-Betrieb,
die Kalender-Geheimnissuche.

Sie waren während Adams Abwesenheit eingefroren. **Die Betriebslage in
`CLAUDE.md` trägt sie seit dem 28.08. ausdrücklich wieder als Arbeitsvorrat**,
nicht mehr als hingenommene Blindstelle. Es ist die substanziellste offene
Arbeit im Projekt, sie ist genau als Zwei-Stunden-Block geschnitten, und sie
hängt an nichts, was Adam tun muss.

**Bauform, und sie ist nicht verhandelbar** (steht im Katalog, hier nur zur
Erinnerung): Verhalten ausführen — oder Abwesenheit über echte `ast.Call`-Knoten
**samt Wert** des Arguments, nie nur über den Namen. **Je Fix die
Entkernungs-Gegenprobe:** `__pycache__` löschen, Eingriff mit `assert alt in t`
verifizieren, **die erwartete rote Zeile vorher hinschreiben**, Schutz raus, rot
sehen, Schutz rein. Jede Stelle einzeln committet.

### Danach, in dieser Reihenfolge

1. **`scripts/daily_check.sh:536`** — `ss -lntH 2>/dev/null`: Fehlt `ss`, ist
   die Pipeline leer und der `else`-Zweig meldet Adam
   *„✅ Nach aussen lauschen nur SSH und der Webhook-Port"*. **Eine
   Sicherheitsbehauptung, die aus einem fehlenden Werkzeug entsteht.** Steht in
   der F-Liste, gehört aber der Wirkung nach zu Rang A.
2. **Rang B (b), (c), (d)** aus demselben Katalog — die Fehlalarme. Ein Prüfer,
   der falsch anschlägt, ist binnen einer Woche abgeschaltet.
3. **`ABHAENGIGKEITEN.md:39`** — 11/11 gegen 67, F-Liste.

**Die Konvergenz-Bremse gilt:** Nach Rang A/B folgt **eine** Nachprüfung
(Entkernung nur der acht reparierten Stellen), dann ist Schluss. Was die noch
findet und nicht scharf-blockierend ist, geht in die F-Liste. **Keine dritte
Runde, kein Prüfer für Prüfer.**

---

## ③ Die Grenzen — sie ändern sich durch die Nacht nicht

- **Nichts mit root.** Node 22→24 ist Adams Hand, ausdrücklich nicht deine.
- **Nichts nach außen.** Kein Postfach, kein Webhook-Umschalten, kein Deploy,
  der den laufenden Bot antastet.
- **Keine Kostenquelle.** Alles hier läuft im Abo — kein neuer Dienst, kein
  Werkzeug mit Gebühr, keine `ANTHROPIC_API_KEY`. Fällt dir eine Aufgabe zu, bei
  der das unklar wäre: **unklar gilt als ja**, also liegenlassen und melden.
- **Nichts Neues erfinden.** Wenn ein Punkt nicht im Wortlaut vorliegt, wird er
  nicht abgeleitet — er wird gemeldet. Auch nachts, auch wenn dadurch Zeit
  ungenutzt bleibt.
- **`bash scripts/regressionstest.sh` vor jedem Commit.** Auch bei Doku.

**Modell und Aufwand:** Nachtblöcke laufen auf **normaler Stufe ohne
Schnellmodus** — Durchhalten schlägt Klotzen. Die mechanischen Ablage-Eingriffe
gern auf Sonnet als Unter-Sitzung. Stößt du auf etwas, das erkennbar mehr
braucht: **parken und im Morgen-Bericht als Eskalations-Kandidat melden**, nicht
selbst hochschalten.

---

## ④ Der Morgen-Bericht

Höchstens zehn Zeilen, für Adam beim Aufwachen: **erledigt · geparkt · Fragen ·
was heute an ihm liegt.** Dazu die drei Zeilen, die diesmal besonders zählen:

- **Welche meiner fünf Befunde du bestätigt und welche du gekippt hast.** Das
  ist das Ergebnis der Gegenprüfung, und es ist wichtiger als die Bauarbeit.
- **Wo du gesucht und nichts gefunden hast.** Eine Gegenprüfung, die nie etwas
  findet, ist selbst der Befund — aber nur, wenn sichtbar ist, wo sie hingesehen
  hat.
- **Wie viele der acht Rang-A-Stellen stehen**, und bei welcher die Gegenprobe
  nicht rot wurde. Die ist dann interessanter als die sieben, die es wurden.

**Adams Handgriffe für morgen bleiben, was sie sind:** die fünf Telegram-Kanäle
und Node 22→24. Beide unabhängig von allem hier. Bitte im Bericht nicht
untergehen lassen.
