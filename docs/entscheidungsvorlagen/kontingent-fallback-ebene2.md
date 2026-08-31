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
| **A — API-Zweitweg** | 🟢 | Derselbe Anbieter, anderer Geldtopf: `ANTHROPIC_API_KEY` statt Abo-Token. Technisch der kürzeste Weg, weil der Code beide Wege ohnehin kennt. 💰 **Kostet pro Token** — nur mit ausdrücklicher Freigabe und Ausgabengrenze. **Trägt Adams Stopp-Auflage vom 26.07. (siehe unten).** |
| **B — lokales Modell** | 🟢 | Ollama läuft bereits auf dem VPS. Datenschutzfreundlich und kostenfrei, aber der Server hat **keine GPU**; für ein Modell, das den Hauptagenten ersetzen könnte, fehlt schlicht die Rechenleistung. Taugt für Neben-Inferenzen, nicht als Vertretung. |
| **C — Zweit-Konto** | 🟡 | Ein zweites Abo verdoppelt das Kontingent. Kostet eine weitere Grundgebühr und wirft die Frage auf, ob zwei Konten für eine Person im Sinne der Nutzungsbedingungen sind. |
| **D — Fremdanbieter** | 🟡–🔴 | Anderer Hersteller über LiteLLM. Neuer Datenabfluss, neue Vertragslage, andere Antwortqualität — und die Ampel-Regeln müssten für ihn neu durchdacht werden. |
| **E — Zusatzguthaben** | 🟡 | Adams eigene Ergänzung: Kontingent zukaufen statt ausweichen. Der ehrlichste Weg, weil nichts am Verhalten geändert wird — 💰 aber vor jedem Kauf eine Kostenschätzung. **Trägt Adams Auflage vom 26.07. (siehe unten).** |

## Adams Auflagen an die Wege A und E `[NACHGETRAGEN 2026-08-31]`

Beide stammen aus dem Bot-Chat vom **26.07.2026** und sind über einen Monat
alt — sie standen bis heute nirgends in der Ablage. Herkunft: die Gesamtprüfung
der Bot-Protokolle, Wortlaut aus dem Protokoll gelesen.

### Weg E darf nur im Notfall an — *weil man sein Greifen nicht sieht*

**Adam am 26.07., 15:33:**

> *„Das wäre natürlich ein wichtiger Punkt. Das zu wissen. Und wenn man das
> nicht weiß, kann man damit halt so … natürlich nicht arbeiten. Das heißt,
> man muss es deaktiviert lassen. Nur als Notfall einschalten sozusagen."*

**Die Auflage:** Zusatzguthaben bleibt **deaktiviert** und wird **nur als
Notfall eingeschaltet**. **Die Begründung ist der eigentliche Wert:** Weil
nicht sichtbar ist, wann der Zukauf greift. **Ein Ausweichweg, dessen Greifen
man nicht sieht, ist nicht benutzbar** — dieselbe Logik wie bei der ehrlichen
Grenze der Vorwarnung weiter unten: eine Zahl, die vertrauenswürdig aussieht
und es nicht ist, ist schlimmer als keine.

### Laufende Prozesse stoppen — bei A und E, nicht bei Ebene 1

**Adam am 26.07., 15:11:**

> *„Das halt laufende Prozesse, die … größeres Kontingent verbrauchen,
> möglichst automatisch gestoppt werden … weil das dann schlicht einfach nur
> das Geld verpulvert."*

**Der Unterschied zu 5.31, und er ist der Punkt:** Für **Ebene 1 ist das
erfüllt** — der Auftrag geht zurück in die Warteschlange, der Worker schläft.
Solange nur pausiert wird, kostet Weiterlaufen nichts.

**Sobald ein bezahlter Topf dahinterliegt, läuft die Uhr mit Geld.** Genau
dafür steht die Auflage bislang nirgends. Sie gehört an die **Wege A und E** —
als Bedingung ihrer Einrichtung, nicht als eigener Bauauftrag: Wer A oder E
scharfstellt, baut im selben Zug das Stoppen laufender Prozesse mit ein.

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
