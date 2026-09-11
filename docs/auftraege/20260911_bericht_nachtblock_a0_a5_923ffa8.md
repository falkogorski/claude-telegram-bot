> **An Adam, zur Weitergabe an Engywuck** · Mick · 11.09.2026, 06:01 · gebaut: `048ed6e..923ffa8` (11 Commits) · Regressionslauf 84/84 · **kein Deploy**

**Zweck: ANSICHT + WEITERGABE → Engywuck** · **Zu tun: Adam nichts — weiterreichen, wenn er mag**

# Nachtblock A0 bis A5: vollständig, mit zwei Berichtigungen an deinem Papier

**Nenner:** sechs Punkte beauftragt, sechs gebaut. 22 neue Prüfzeilen, 25
Gegenproben gefahren. Prüfer im Lauf: 82 → 84.

## Zuerst das Dringende: dein Root-Block hätte eine Schleife gebaut

**A0, zweiter Teil, sofort erledigt** (`048ed6e`), weil Adam ihn ausführen
wollte: Die drei `workspace`-Zeilen sind raus. Nachgemessen statt übernommen —
`log_sync.sh` schreibt seine Quittung bei **jedem** Lauf in den Arbeitsordner
(Z. 220/232), also: Lauf → Quittung → Feuer → Lauf.

**Und der Pfad stimmte ohnehin nicht.** `~/workspace/ausarbeitungen` gibt es
nicht; das Skript gleicht `~/workspace` als **Wurzel** ab, „ausarbeitungen" ist
der Name im **Ziel**. Am Bestand des Log-Repos gemessen: 140 von 180 liegen
direkt in der Wurzel, 39 unter `ablage/`, eine unter `an-mick/`.

Nach A5 darf der Arbeitsordner wieder hinein — die Tempdatei liegt jetzt in
`$WORK/.quittung/`, und `PathModified` ist nicht rekursiv. **Erst nach dem
Deploy**, vorher wäre die Schleife wieder da.

## A0, erster Teil: dein Befund hat gesessen

Du hattest recht, und ich hatte die Frage in meinem eigenen Bericht als Frage
an dich formuliert, statt sie zu messen. **Prüfzeile 8** misst jetzt über echte
`ast.Call`-Knoten, dass `_menue_nachziehen` als `TypeHandler` in `group=99`
registriert **ist**. Zwei Gegenproben: Registrierung entfernt → rot;
Registrierung durch einen **Kommentar** ersetzt → ebenfalls rot. Die zweite ist
die eigentliche Probe.

## A1 bis A5

| | gebaut | Gegenproben |
|---|---|---|
| **A1** Knopf · `/empfang_an` und `/empfang_aus` · Urheber in der Kontext-Zeile | `487f273`, `8e9e50c`, `b50409d` | 8, alle rot |
| **A2** Nutzungszahlen wie der Herzschlag | `99db60c` | 3 (siehe unten) |
| **A3** Briefing der Sekretärin | `21a4561` | 4, alle rot |
| **A4** PDF: `cwd` und Schriften | `f55c9ba` | 3 (siehe unten) |
| **A5** Log-Abgleich unter dem Minutentakt | `12eb332`, `f59c16f` | 4 (siehe unten) |

**Der Doku-Spiegel hat den Knopf sofort gefangen** — *„/hilfe behauptet 11
Knöpfe, Tastatur zeigt 12"*, genau wie du es vorhergesagt hast.

**Beim Briefing eine Zeile, die ich für die wichtigste halte:** Sie misst, dass
die Von-außen-Schranke **unverändert** danebensteht. „Adams eigene Nachricht ist
immer ein Auftrag" ist ihre andere Hälfte, nicht ihre Aufweichung — sein Satz
ist die Anweisung, die weitergereichte Datei bleibt Information.

## A5: Adams Messung führte auf einen dritten Fund

Schloss (`flock -n`), Tempdatei-Umzug, `-prune` und `${f##*/}` sind gebaut. In
der Gegenprobe kam dazu: **`--exclude='.*'` hielt `.venv` draußen,
`venv/lib/README.md` und `node_modules/paket/README.md` kamen ins Log-Repo.**
Der Ausschluss hing am Punkt, nicht an der Sache — dritter Fall dieser Klasse
in diesem Projekt.

## Drei Stellen, an denen ICH danebenlag — sie gehören in den Kurs-Blick

1. **Mein Geschwister-Kommentar rutschte zwischen die `rsync`-Fortsetzungs­zeilen
   und wurde zum Argument.** Der Transport lieferte danach **nichts** mehr.
   `bash -n` sagt dazu nichts, es ist gültige Syntax. Gefunden hat es eine
   Prüfzeile, die eine Minute vorher entstanden war.
2. **Meine erste A5-Zeile 1 maß den falschen Moment** — sie sah nach, was nach
   dem Lauf im Ordner *liegt*; die alte Tempdatei wurde ohnehin umbenannt. Die
   Gegenprobe blieb grün. Jetzt gemessen: Ein Lauf ohne Änderung verändert das
   Verzeichnis nicht, Inhalt und Zeitstempel.
3. **Meine A4-Zeile wartete auf ihren Fall, statt ihn herzustellen.** „Ein
   leerer Ordner gilt nicht als Schriftordner" war grün, und die Gegenprobe
   auch — auf diesem Mac steht zufällig ein voller Ordner vorn. Jetzt wird der
   leere über `XDG_DATA_HOME` an den Listenanfang gesetzt.

Der gemeinsame Nenner: **Wenn eine Gegenprobe nicht rot wird, ist die Prüfzeile
der Befund.** Steht als Blaupause-Zeile.

Dazu eine vierte, kleinere: Mein Schlosshalter war ein `Popen`-Unterprozess;
`test_pruefumgebung` hat ihn gemeldet. Dabei repariert — jener Wächter suchte
den **Namen im Text** und schlug deshalb auch bei einem Kommentar an. Er zählt
jetzt echte Aufrufknoten, also strenger: Wer den Aufruf durch eine
Kommentarzeile ersetzte, kam vorher durch. Gegenprobe mit echtem `Popen`: rot.

## Zwei Stellen, die ich gemessen und anders gefunden habe als dein Papier

1. **DejaVu ist auf diesem Mac nicht vorhanden**, `/usr/share/fonts` auch
   nicht. `/System/Library/Fonts` trägt 370 Schriften. Daher eine
   Kandidatenliste je Plattform **plus** die Prüfung, ob wirklich Schriften
   darin liegen — ein vorhandener, leerer Ordner ist derselbe Fehler in grün.
2. **Der Log-Sync-Pfad**, siehe oben.

## Adams vier Entscheide sind eingetragen (`fafcf3b`)

Riegel geschlossen (`SCHARF: nein`, mit seinen gezählten Zahlen: 7 in der
zweiten Probezeit, 14 gesamt, alle gelb, null Übergaben) · Write/Edit unter
`~/workspace` für die drei Reichweiten **vermerkt, nicht gebaut**, direkt an
`_NO_ALWAYS_TOOLS` · **F-23** angelegt (Hygiene-Neustart wartet bis dreißig
Minuten) · kein Deploy.

## Was zu prüfen wäre

1. **Das Briefing ist eine Textmessung.** Ich halte sie hier für zulässig — der
   Gegenstand *ist* Text —, aber es ist die Ausnahme von der Regel vom 22.08.,
   und du solltest sie selbst beurteilen.
2. **`_schriftordner` bricht den Baumlauf nach zwei Ebenen ab.** Ein Ordner,
   der seine Schriften tiefer legt, gilt als leer. Bewusst, aber ungemessen.
3. **Die Pfad-Wache im Tagescheck** läuft am Mac nicht (kein `systemctl`). Sie
   ist `bash -n`-geprüft; ihre Wirkung zeigt der erste Tagescheck auf dem VPS.
4. **A5 Zeile 2 meldet am Mac „NICHT GEMESSEN"** (kein `flock(1)`). Auf dem VPS
   misst sie. Das ist Absicht nach der A1-Regel, aber es heißt: Das Schloss ist
   hier nie im Betrieb gemessen worden.

## Nicht getan, mit Absicht

Kein Deploy (Adams Entscheid). Keine Sammelnachricht — eigener Block nach
seiner Rückkehr. Dein Teil B und C nur gelesen.
