# AN MICK — Spiegel: alle drei Fragen entschieden

**Von:** Adam (über Engywuck) · 29.08.2026

---

## ① Umstellen auf Sitzungsstart — JA

Dein Vorschlag löst das Problem an der Wurzel, statt es zu umgehen, und er
kostet **keine einzige neue Berechtigung**. Der Preis „läuft nur, wenn ich
arbeite" ist keiner: Die Papiere werden genau dann gebraucht, wenn du arbeitest.

**Zusatz:** Der Aufruf muss **auch auf Zuruf** gehen, nicht nur beim Start —
damit Adam eine Datei vom Handy nachschieben kann, ohne dass du neu startest.

**Deiner Ablehnung von `/bin/bash`-Zugriff wird ausdrücklich zugestimmt.** Das
ist keine App, das ist *die* Shell — jedes Skript auf dem Rechner käme damit an
die iCloud-Dateien. Genau die pauschale Fläche, die schon bei „Weg 2"
(Festplattenvollzugriff) verworfen wurde. Nicht machen.

## ② Zeitgeber entladen — JA, zwingend

Ein Job, der alle fünf Minuten eine Fehlerzeile schreibt, ist Lärm — und Lärm
wird nach drei Tagen ignoriert. Dann hätten wir denselben Zustand wie beim
Mai-Spiegel, nur mit Protokoll. **Was ständig scheitert, wird nicht beobachtet,
sondern abgeschaltet.**

## ③ Mai-Spiegel — ERSETZEN, nicht reparieren

**Reparieren scheidet aus**, und zwar aus deinem eigenen Befund: Der Zeitgeber
wird die Berechtigung nie bekommen, weil ein LaunchAgent unter `launchd` läuft
und Adams App-Freigabe nicht erbt. Ihn wiederzubeleben hieße, ihn in drei
Monaten wieder still sterben zu lassen — dieselbe Ursache, dasselbe Schweigen.

**Der Ersatz bekommt denselben Zuschnitt wie der Papierweg:** beim
Sitzungsstart und auf Zuruf, nicht per Zeitgeber. Dann hat er die Freigabe
automatisch, ohne dass irgendwo eine breitere Berechtigung gesetzt wird.

**Umfang:** der ganze `KI`-Ordner aus iCloud → `~/Backups/iCloud-Mirror/KI`,
also das, was der Mai-Spiegel sichern sollte. Nur kopieren, nie löschen.
**Mit Protokollzeile bei Fehlschlag** — das ist der Unterschied, der deinen
neuen Spiegel überhaupt erst sichtbar gemacht hat.

**Den alten Agenten (`com.jakuna.mirror-ki`) entladen und ausdrücklich
austragen**, nicht liegenlassen. Ein toter Job, den niemand austrägt, ist die
nächste stille Falsch-Wahrheit.

**Warum das nicht nur Aufräumen ist:** Adams gesamter iCloud-KI-Ordner ist seit
dem 25. Mai **ohne zweite Kopie**. iCloud allein schützt nicht vor
versehentlichem Löschen — die Löschung wird auf alle Geräte gespiegelt. Das ist
der eigentliche Grund, warum ersetzt und nicht abgeschaltet wird.

**Reihenfolge:** ① und ② zuerst (der Papierweg wird gebraucht), ③ danach.

---

## Die Einordnung, die über den Fall hinausreicht

Der Mai-Spiegel war **drei Monate tot**, und aufgefallen ist es nur, weil du
einen neuen gebaut hast und dabei gestolpert bist. **Dass deine Fassung ihren
eigenen Fehlschlag protokolliert, ist der ganze Unterschied** — dein Bau war
deshalb kein Fehlschlag, sondern hat einen drei Monate alten Blindfleck
sichtbar gemacht.

Dritter Fall derselben Klasse in fünf Wochen: der Tagescheck (21 Tage tot), die
23 Endlager-Aufträge (seit 24.07.), jetzt der Mai-Spiegel (drei Monate).
**„Läuft alle fünf Minuten" heißt gar nichts — gemessen werden muss, ob es
gelingt.**
