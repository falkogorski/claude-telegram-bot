<!-- ROLLE: n2-effizienz-vor-aufstockung -->
# N2 — Effizienz vor Aufstockung: die Messung

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 26.07.2026, 03:05 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> **Auftrag:** Messen, ob die Kapitel-Überschriften wirklich den Speicher
> brauchen, der ihnen zugeschrieben wird — **bevor** über eine Aufstockung
> entschieden wird. Adams Entscheidung im August; hier stehen nur Zahlen.
>
> 💰 **Kostenlage: null.** Nur Messungen auf vorhandener Ausstattung, kein
> Download, kein bezahlter Dienst.

## Die drei Zahlen, um die es ging

| Frage | Vermutung vorher | **Gemessen am 26.07.** |
|---|---|---|
| Wie viel belegt das lokale Modell? | „5,10 GiB" | **3017 MiB** — und **nur, solange es geladen ist** |
| Wie lange bleibt es geladen? | unbekannt | **5 Minuten** nach der letzten Anfrage, dann entlädt es sich |
| Was belegt es im Ruhezustand? | „der Brocken" | **nichts.** `ollama ps` war leer; der Dienst allein ist unauffällig |

**Lage zum Messzeitpunkt:** 7940 MiB gesamt, **5907 MiB verfügbar** im
Ruhezustand. Nach dem Laden des Modells: 2890 MiB verfügbar. **Auch die Spitze
bleibt also im grünen Bereich** — sie zehrt gut die Hälfte des Freiraums auf,
aber sie erreicht die Grenze nicht.

## Der Befund, der die Frage umstellt

Die eigentliche Überraschung liegt nicht beim Speicher, sondern bei der
**Qualität**. Drei echte Kapitel-Überschriften, sauber formuliert, Temperatur
niedrig:

| Vorgelegter Inhalt | Antwort von phi4-mini | Urteil |
|---|---|---|
| Nebeneinkommen aufbauen, Warnung vor unseriösen Anbietern | „Automatisches Einkommen, Warnung, unschlüssige Anbieter." | ⚠️ **„unschlüssige"** statt „unseriöse" — falsches Wort |
| Wie man **eine Rechnung schreibt** in unter zwei Minuten | „Schnell Rechnen Üben" | ❌ **sinnentstellend** — aus dem Schreiben einer Rechnung wurde Kopfrechnen |
| Datenschutz bei KI-Diensten, welche Daten das Haus verlassen dürfen | „Diskussion über Datenschutz bei KI-Diensten und Datenerlaubnis des Hauses." | ✅ brauchbar, aber neun Wörter statt sechs |

**Einer von dreien brauchbar, einer sinnentstellend falsch.**

**Ehrlich dazu:** Ein erster, schlechter formulierter Versuch lieferte reines
Kauderwelsch („Nebenermogenutzung") — **das lag am Prompt, nicht am Modell**,
und wäre als Beleg unfair gewesen. Die Tabelle oben zeigt die Läufe *nach* der
Verbesserung. Das Modell ist besser als der erste Eindruck; für diese Aufgabe
reicht es trotzdem nicht.

## Was daraus folgt — drei Punkte

**① Die Aufstockung ist nach dieser Messung nicht nötig.** Der Speicher war nie
der Engpass: im Ruhezustand null, in der Spitze knapp die Hälfte des Freiraums,
und die Spitze dauert fünf Minuten. Die Zahl „5,10 GiB" war zu hoch gegriffen.

**② Ein kleineres Modell zu suchen, geht an der Sache vorbei.** Wenn schon
2,5 GB aus dem Schreiben einer Rechnung „Rechnen üben" macht, wird ein Modell
mit einem Bruchteil davon nicht genauer. **Der Weg über die Größe ist zu Ende,
bevor er beginnt.**

**③ Die tragende Frage ist eine andere:** Muss diese Aufgabe überhaupt lokal
laufen? Kapitel-Überschriften entstehen, **weil Adam ein Video schickt** — das
ist mensch-initiiert und damit vom Abo gedeckt (im Gegensatz zu zeitgesteuerten
Läufen). Das Hauptmodell kann es besser und kostet dafür nichts extra. **Das
lokale Modell ist der Notweg, nicht der Normalweg** — genau so, wie es im
Notbetriebs-Papier steht.

## Empfehlung

**Ollama bleibt, wird aber nicht der Weg für Inhalte, auf die es ankommt.**
Für die Abwesenheit ist es weder nötig anzuhalten (es belegt im Ruhezustand
nichts) noch schädlich, es laufen zu lassen. Wer die Spitze ganz vermeiden
will, kann den Dienst für die vierzehn Tage stoppen — **das spart aber fast
nichts und nimmt den Notweg weg.**

**Zwei Einstellungen sind trotzdem sinnvoll**, weil sie heute nur als Vorgabe
des Herstellers gelten und nicht als unsere Entscheidung — sie brauchen root
und stehen als Befehlsblock bereit:

- `OLLAMA_KEEP_ALIVE` ausdrücklich setzen (heute: fünf Minuten aus Voreinstellung)
- `OLLAMA_MAX_LOADED_MODELS=1` — damit **nie zwei** Modelle gleichzeitig liegen

**Was offen bleibt und Adams Entscheidung ist:** ob die Kapitel-Funktion
dauerhaft ans Hauptmodell wandert. Das ist keine Speicherfrage mehr, sondern
eine über Qualität — und die gehört in den August.
