<!-- ROLLE: schnittvorschlag-modularisierung -->
# 9.10 — Schnittvorschlag für `bot.py`

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 26.07.2026 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> **Dies ist ein Vorschlag, kein Umbau. Es wurde keine einzige Zeile
> verschoben.** Aufteilen ist die gefährlichere Art von Arbeit: Es sieht
> harmlos aus, weil sich „nichts ändert" — und genau deshalb prüft niemand
> genau hin. Entschieden wird das mit Adam, umgesetzt frühestens danach.
>
> 💰 Kostenlage: null.

## Der Befund — gemessen, nicht geschätzt

**8017 Zeilen, 179 Funktionen.** Wo das Gewicht sitzt:

| Bereich | Zeilen | Anmerkung |
|---|---:|---|
| Telegram-Handler (`cmd_*`, `on_*`) | 1827 | 40 Einstiegspunkte |
| TTS und Sprachaufbereitung | 768 | in sich geschlossen |
| Selbstcheck | 608 | **eine einzige Funktion** |
| Warteschlange und Auftragslauf | 592 | das Herz, am engsten verwoben |
| Freigaben und Rechte | 327 | sicherheitstragend |
| Medien und Upload | 252 | H1 hat hier viel gebündelt |
| Sitzung und SDK | 113 | klein, aber überall berührt |
| nicht eindeutig zugeordnet | 3455 | Hilfsfunktionen, Konstanten, Modulkopf |

**Die zehn längsten Funktionen tragen zusammen 2368 Zeilen** — knapp ein Drittel
der Datei in zehn von 179 Funktionen. `run_self_check` allein ist mit **608
Zeilen** länger als die meisten eigenständigen Module dieses Projekts.

## Was daraus folgt — und was ausdrücklich nicht

**Der auffälligste Wert ist nicht die Gesamtzahl, sondern `run_self_check`.**
Achthundert Zeilen sind für eine Datei kein Drama; eine Funktion mit 608 Zeilen
ist eine. Sie ist außerdem der **einfachste** Schnitt im ganzen Bestand: Der
Selbstcheck ruft nur, er wird von nichts gerufen, und sein Ergebnis ist eine
Liste von Zeilen. **Er hat keine Rückwirkung auf den laufenden Betrieb.**

**Der gefährlichste Schnitt wäre die Warteschlange.** Sie ist mit Sitzungen,
Persistenz, Kontingent-Behandlung und Zustellnachweis verwoben, und jeder dieser
Fäden trägt eine Zusage, die wir Adam gegeben haben („keine Nachricht geht
verloren"). Hier gilt eher das Gegenteil: **nicht anfassen**, solange kein
zwingender Grund vorliegt.

## Vorschlag in drei Stufen — jede einzeln nutzbar

**Stufe 1 — `selbstcheck.py` (empfohlen, wenn überhaupt).** 608 Zeilen heraus,
eine Import-Zeile hinein. Der Prüfstein von R4 ist erfüllt: **in einer Minute
rückgängig zu machen, ohne nachzudenken.** Nachweis wäre trivial — der Lauf muss
danach dieselbe Zahl Zeilen mit demselben Ergebnis liefern.

**Stufe 2 — `sprache.py` (TTS und Aufbereitung, ~768 Zeilen).** Ebenfalls
sauber trennbar: Text hinein, Text oder Tondatei hinaus, keine Zustandsführung.
Eigene Tests bestehen bereits.

**Stufe 3 — die Handler (~1827 Zeilen).** Wäre der größte Gewinn an Übersicht
und **der größte Aufwand**: Vierzig Einstiegspunkte greifen quer auf Sitzungen,
Vorlieben, Warteschlange und Kanal-Routing zu. Ohne einen Zwischenschritt, der
diese Zugriffe bündelt, würde ein Verschieben nur den Wirrwarr umverteilen.
**Nicht empfohlen ohne eigenen Anlass.**

## Drei Auflagen, falls es je gemacht wird

**① Nur nach grünem Regressionslauf, und jede Stufe einzeln.** Kein
Sammel-Commit „Aufräumen" — eine Aufräumaktion, die etwas mitreißt, ist
schlimmer als der Wildwuchs, den sie beseitigt.

**② Im Klon proben (R4), nicht am laufenden Stand.** Dies ist genau ein Eingriff
mit Kettenwirkung: Er berührt Importe, den Selbstcheck und die
Register-Vollständigkeit zugleich.

**③ Das Abhängigkeits-Register vorher lesen und nachher nachziehen.** Jede
verschobene Funktion, auf die eine Kette zeigt, muss dort ihren neuen Ort
bekommen — sonst entsteht genau der stille Bezugsbruch, gegen den das Register
gebaut wurde.

## Meine Empfehlung, offen gesagt

**Jetzt gar nichts, auch nicht Stufe 1.** Nicht weil es falsch wäre, sondern
weil der Zeitpunkt es ist: Adam ist ab Dienstag vierzehn Tage weg, und ein
Umbau ohne Not drei Tage davor ist dieselbe Entscheidung, die wir beim
Heimtunnel bewusst verschoben haben. **Der Wildwuchs kostet uns heute nichts** —
er kostet Lesbarkeit, und die brauche ich, nicht der laufende Betrieb.

**Wenn ein Anlass kommt** — etwa wenn `bot.py` beim Bearbeiten spürbar im Weg
steht, oder wenn eine zweite Person mitliest —, ist **Stufe 1 der richtige
erste Schnitt.** Nicht als Aufräumaktion, sondern weil eine Funktion mit
sechshundert Zeilen niemand mehr im Kopf behält.
