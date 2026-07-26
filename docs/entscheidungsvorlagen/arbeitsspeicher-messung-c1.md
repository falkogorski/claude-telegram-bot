<!-- ROLLE: messung-arbeitsspeicher -->
# C1 — Arbeitsspeicher: gemessen, nicht geschätzt

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 25.07.2026, 23:20 ·
> **Ergänzt 26.07.2026, 03:40** (Abschnitt „Zwei Zahlen, zwei Definitionen") ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> **💰 Die Messung selbst kostet nichts.** Die einzige mögliche Kostenquelle
> wäre das Aufstocken des VPS — dazu unten ein eigener Abschnitt, ohne
> Empfehlung ins Blaue.

---

## Zwei Zahlen, zwei Definitionen — aufgelöst `[NEU 26.07., 03:40]`

Am 25.07. stand hier **5,10 GiB**, gemessen. Am 26.07. kamen **3017 MiB**
heraus, ebenfalls gemessen. Zwei Messungen, zwei Ergebnisse, beide richtig —
und die zweite hätte die erste beinahe stillschweigend überschrieben. **Genau
das ist der Fehler, den dieses Projekt viermal hatte: eine Kennzahl ohne
Definition.** Also die Definitionen nebeneinander, statt die eine durch die
andere zu ersetzen.

| | **5,10 GiB** (25.07.) | **3017 MiB** (26.07.) |
|---|---|---|
| **Was gemessen wurde** | `MemoryPeak` von Ollama | Rückgang von `MemAvailable` beim Laden eines Modells |
| **Zeitraum** | Höchststand **seit dem 15. Juli** (elf Tage) | ein einzelner Augenblick |
| **Enthält Datei-Zwischenspeicher?** | **ja** | **nein** |
| **Beantwortet die Frage** | „Wie viel hat die cgroup je gehalten?" | „Wie viel fehlt beim Laden tatsächlich?" |

### Der Beleg, dass es am Zwischenspeicher liegt

Ollama hält laut cgroup gerade 2256 MiB — **obwohl kein Modell geladen ist.**
Aufgeschlüsselt:

```
anon (echter Anwendungsspeicher):    31 MiB
file (Datei-Zwischenspeicher):     2217 MiB
slab (Kernel):                        5 MiB
```

**31 MiB gegen 2217 MiB.** Der weit überwiegende Teil ist die Modelldatei im
Lese-Zwischenspeicher — und den gibt der Kernel **jederzeit her**, sobald
jemand Speicher braucht. `MemoryPeak` zählt ihn mit, `MemAvailable` rechnet ihn
heraus. Daher die Differenz.

### Die Gegenprobe, die keine Zweifel lässt

Die Summe aller `MemoryPeak`-Werte auf dieser Maschine beträgt **23 005 MiB** —
auf einem Server mit **7940 MiB**. Eine Zahl, die das Dreifache des Vorhandenen
ergibt, kann keine Belegung sein. **Spitzenwerte sind weder addierbar noch als
gleichzeitige Belegung lesbar**; sie liegen zu verschiedenen Zeiten und
enthalten Freigebbares.

### Was daraus folgt

**Für die Frage „reicht der Speicher" ist `MemAvailable` der richtige Maßstab**,
nicht `MemoryPeak`. Die 5,10 GiB waren nicht falsch — sie beantworteten eine
andere Frage, als ihnen gestellt wurde.

**Die Empfehlung ändert sich dadurch nicht**, und das ist der Grund, warum sie
trägt: **Swap ja, aufstocken nein.** Sie stand schon bei der pessimistischeren
Zahl und steht bei der genaueren erst recht.

**Ehrlich zur Herkunft des Missverständnisses:** Die 5,10 GiB wurden ohne
Rückfrage nach ihrer Definition weitergereicht — von mir gemessen, von der
Kontrollsitzung übernommen. Keiner von uns hat gefragt, was `MemoryPeak`
eigentlich zählt. Die Zahl war korrekt abgelesen und trotzdem irreführend, und
das ist die unangenehmere Sorte Fehler: Sie besteht jede Prüfung, die nur das
Ablesen prüft.

## Wie gemessen wurde — und warum ohne Lasttest

Der Auftrag lautete, den Spitzenverbrauch **unter echter Last** zu messen. Ein
Lasttest auf der Produktivmaschine hätte allerdings genau das Ereignis auslösen
können, vor dem er warnen soll: einen OOM-Kill, der den Bot mitreißt.

Das war nicht nötig. **systemd führt die Spitzenwerte ohnehin mit** — jeder
Dienst trägt seinen Höchststand seit dem letzten Start:

```bash
systemctl show <dienst> -p MemoryPeak --value
```

Das ist ein **abgelesener** Wert aus dem realen Betrieb, kein simulierter. Damit
ist die Messung genauer als ein künstlicher Lasttest und obendrein gefahrlos.

## Der Befund

| Dienst | Spitze seit Start | gerade eben |
|---|---|---|
| **Ollama** | **5,10 GiB** | 42 MiB |
| claude-telegram-bot | 1,36 GiB | 1,26 GiB |
| Docker (LobeChat) | 0,82 GiB | 680 MiB |
| LiteLLM | 0,25 GiB | 258 MiB |
| **Summe der Spitzen** | **7,53 GiB** | |
| **Vorhanden** | **7,75 GiB** (7940 MiB) | |

**Das sind 97 Prozent.** Für Kernel, journald, fail2ban, sshd und alles Übrige
bleiben **229 MiB**.

### Drei Dinge, die daran wichtiger sind als die Zahl

**① Connis Verdacht stimmt — aber anders, als der erste Blick nahelegt.** Im
Ruhezustand belegt Ollama **42 MiB** und sieht harmlos aus. Es lädt sein Modell
(`phi4-mini`, 2,5 GB) erst bei der ersten Anfrage — und braucht dann **das
Hundertfache**. Wer nur `ps` ansieht, übersieht das vollständig. Genau deshalb
ist der Spitzenwert die richtige Kennzahl und der Momentanwert die falsche.
(Dieselbe Klasse Fehler wie die als gültig zitierte Momentaufnahme vom 24.07.)

**② Der eigentliche Befund ist nicht Ollama, sondern der fehlende Swap.**

```
swapon --show  →  kein Swap
```

Ohne Auslagerung gibt es **kein Abfedern**: Der Kernel hat bei Speichermangel
nur eine Wahl, und das ist der OOM-Killer. Mit Swap wird dieselbe Situation
*langsam* statt *tödlich*. Das ist der Unterschied zwischen „der Bot antwortet
zäh" und „der Bot ist weg, und niemand ist da, der ihn startet."

**③ Die Spitzen müssen nicht gleichzeitig aufgetreten sein.** Ich behaupte
nicht, dass die Maschine schon einmal bei 97 Prozent stand — das steht in den
Zahlen nicht drin. Was drinsteht: **jeder dieser Werte ist im echten Betrieb
erreicht worden.** Ihr Zusammentreffen ist damit möglich, und für vierzehn Tage
ohne Aufsicht ist „möglich" genug.

## Was daraus folgt — zwei Griffe, beide kostenlos

**Griff 1 (die eigentliche Lösung): Swap anlegen.** 4 GiB Auslagerungsdatei auf
einer Platte mit 223 GiB frei. Kostet nichts, ändert nichts am Betrieb, und
nimmt dem OOM-Killer die Grundlage. **Das ist die Versicherung, die unabhängig
von Ollama trägt** — auch gegen den Fall, an den wir gerade nicht denken.

**Griff 2: Ollama während der Abwesenheit anhalten.** Es ist ein Fallback für
den Fall, dass das Abo ausfällt — und in Adams Abwesenheit gibt es niemanden,
der einen Fallback bediente. Fünf GiB freizumachen, indem man einen ungenutzten
Dienst pausiert, ist der billigste Gewinn im ganzen Aufbau.

Beide Griffe stehen als **Schritt 4** in `docs/befehlsbloecke-root.md`.

## Zum Aufstocken — die ehrliche Einordnung

**Nach dieser Messung ist es nicht nötig.** Mit Swap und pausiertem Ollama liegt
die Spitzenlast bei rund 2,4 GiB von 7,75 — reichlich Luft. Die 16-GB-Empfehlung
aus der Dokumentation stammt laut Quelle aus Community-Berichten, nicht von
Anthropic, und beschreibt Maschinen **ohne** Swap unter Volllast. Genau diesen
Zustand beseitigt Griff 1.

**Wann Aufstocken doch dran wäre:** wenn Ollama dauerhaft mitlaufen soll (etwa
weil der lokale Fallback produktiv wird) oder wenn mehrere Modelle gleichzeitig
gehalten werden. Dann ist es eine Frage der Auslegung, nicht der Panik — und
dann greift die 💰-Regel mit Kostenquelle, Höhe und Adams Freigabe.
