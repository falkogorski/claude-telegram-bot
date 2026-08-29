<!-- ROLLE: entscheidungsvorlage-kontingent -->
# Kontingent-Limit — Ebene 2: Ausweichwege

**Status: bewusst NICHT gebaut.** Diese Seite hält den Möglichkeitsraum fest,
damit Adam entscheiden kann — sie ist keine Bauanleitung und löst nichts aus.

**Ebene 1 ist gebaut** (Punkt 5.31): Beim Kontingent-Limit geht nichts mehr
verloren. Die Nachricht bleibt vorn in der Warteschlange, der Bot sagt in
Klartext, bis wann pausiert wird, und holt danach alles der Reihe nach nach.

**Conni-Empfehlung zur Reihenfolge:** erst Ebene 1 laufen lassen und **messen,
wie oft das Limit überhaupt beißt**. Ein Ausweichweg, der zweimal im Quartal
gebraucht würde, lohnt den Aufwand und das Risiko nicht.

## Grundsatz für jeden Ausweichweg

Ein Ausweichweg wird **angeboten, nie automatisch genommen**. Ein stiller
Wechsel des Modells oder des Anbieters wäre genau die Art unsichtbarer
Entscheidung, die weder zur Kostenregel noch zur Werte-Charta passt: Adam
müsste hinterher raten, wer geantwortet hat und was es gekostet hat.

## Die fünf Wege

| Weg | Ampel | Was er bedeutet |
|---|---|---|
| **A — API-Zweitweg** | 🟢 | Derselbe Anbieter, anderer Geldtopf: `ANTHROPIC_API_KEY` statt Abo-Token. Technisch der kürzeste Weg, weil der Code beide Wege ohnehin kennt. 💰 **Kostet pro Token** — nur mit ausdrücklicher Freigabe und Ausgabengrenze. |
| **B — lokales Modell** | 🟢 | Ollama läuft bereits auf dem VPS. Datenschutzfreundlich und kostenfrei, aber der Server hat **keine GPU**; für ein Modell, das den Hauptagenten ersetzen könnte, fehlt schlicht die Rechenleistung. Taugt für Neben-Inferenzen, nicht als Vertretung. |
| **C — Zweit-Konto** | 🟡 | Ein zweites Abo verdoppelt das Kontingent. Kostet eine weitere Grundgebühr und wirft die Frage auf, ob zwei Konten für eine Person im Sinne der Nutzungsbedingungen sind. |
| **D — Fremdanbieter** | 🟡–🔴 | Anderer Hersteller über LiteLLM. Neuer Datenabfluss, neue Vertragslage, andere Antwortqualität — und die Ampel-Regeln müssten für ihn neu durchdacht werden. |
| **E — Zusatzguthaben** | 🟡 | Adams eigene Ergänzung: Kontingent zukaufen statt ausweichen. Der ehrlichste Weg, weil nichts am Verhalten geändert wird — 💰 aber vor jedem Kauf eine Kostenschätzung. |

## Ehrliche Grenze bei der Vorwarnung

Eine Vorwarnung bei etwa 80 % Verbrauch wäre wünschenswert, ist über den
Abo-Zugang aber **nicht sauber abfragbar**. Deshalb gilt: **nur Claudes eigene
Warnmeldungen durchreichen, nichts approximieren.** Ein selbst geschätzter
Füllstand wäre eine Zahl, die vertrauenswürdig aussieht und es nicht ist.

## Was als Nächstes ansteht

1. Ebene 1 im Alltag beobachten — wie oft greift die Pause tatsächlich?
2. Erst mit dieser Zahl entscheiden, ob überhaupt ein Ausweichweg gebraucht wird.
3. Fällt die Wahl auf A oder E: 💰-Dialog mit Kostenschätzung **vor** der
   Einrichtung, nicht danach.
