<!-- ROLLE: aenderung-rechnungsprojekt -->
> **Zweck: ANSICHT + BELEG** · **Zu tun:** die Frage am Schluss beantworten
> (`git init` im Rechnungsprojekt — ja oder nein). Sonst nichts.

# Was am 02.09.2026 im Rechnungsprojekt geändert wurde — und warum es hier steht

**Das geänderte Projekt ist `~/Projects/rechnungen`, nicht dieses Repo.** Der
Eintrag liegt trotzdem hier, weil dort **kein Versionsstand existiert**: Es gibt
keine Git-Historie, also auch keinen `git log`, in dem diese Änderung
auffindbar wäre. Ohne dieses Papier wäre sie nach einer Woche nicht mehr
zuzuordnen.

## ⚠️ Der Befund zuerst, und er ist meiner

**Ich habe geändert, bevor ich geprüft habe, ob es einen Rückweg gibt.** Die
Auflage lautet *jede Stelle einzeln committet, Rückweg dokumentiert* — im
Rechnungsprojekt ist der erste Teil nicht möglich, und den zweiten hole ich
hiermit nach statt ihn vorauszusetzen.

**Was den Schaden begrenzt** (gemessen, nicht gehofft): Alle drei Änderungen
sind **additiv**. Ohne das neue Feld `ablage` verhalten sich beide Generatoren
exakt wie vorher — nachgewiesen durch einen Lauf mit der unveränderten Datei
`rechnung_012-26.json`, der wie zuvor nur nach `output/` schrieb.

## Die drei Stellen

| Datei | Änderung | Rückweg |
|---|---|---|
| `scripts/ablage.py` | **neu** — die Zustell-Logik, eine Stelle für beide Generatoren | Datei löschen |
| `scripts/generate_rechnung.py` | zwei Einfügungen: `import ablage` nach `ROOT = …`, und nach `registriere_nummer(…)` der Aufruf `ablage.zustellen(out, r)` | beide Blöcke entfernen |
| `scripts/generate_aufstellung.py` | dieselben zwei Einfügungen; der Ausgabeteil sammelt die erzeugten Dateien in `erzeugt` und reicht sie durch | Block ersetzen durch das ursprüngliche `if not args.no_pdf: … return 0` |

**Nichts wurde entfernt oder umgeschrieben** — nur ergänzt.

## Warum ein Feld und kein Schema

Engywucks Auftrag sah `ausgang/<Kunde>/<Projekt>/` vor. **Gemessen am 02.09.
trägt das nicht:** Adams Ablagetiefe schwankt je Kunde.

```
Business/Deko/Goldhut/Rechnung 25039.pdf                    (0 Ebenen)
Business/Deko/DEKO-Service/Volvo/…                          (1 Ebene)
Business/Deko/LiveSetup/Volvo/Business Modul/Norderney/…    (3 Ebenen)
```

Sein *„Volvo Business Modul Norderney"* ist **kein Ordnername, sondern ein
Pfad**. Ein festes Zwei-Ebenen-Schema hätte zwei von drei Fällen verfehlt.
Deshalb ein ausdrückliches Feld mit dem **relativen Pfad**, der von der
Rechnungsdatei bis nach iCloud **durchgereicht statt interpretiert** wird —
dieselbe Bauform wie in `scripts/mac/rechnungen_ablegen.sh`.

```json
"ablage": "LiveSetup/Volvo/Business Modul/Norderney"
```

Fehlt das Feld, ändert sich nichts. Die Datei liegt dann nur in `output/`, und
beim Abholen fängt sie der Auffangordner `_Aus-dem-Server` — ausdrücklich
**nicht** ein fremder Kundenordner, wie Adam es verlangt hat.

## Was gemessen wurde

**Die Pfadprüfung, zehn Fälle, beide Richtungen** — und sie hat **einen eigenen
Fehler gefunden**: Die erste Fassung strippte die Schrägstriche **vor** der
Absolut-Prüfung, aus `/etc` wurde `etc`, und die Zustellung wäre unter
`ausgang/etc/` gelandet. Kein Ausbruch, aber die Prüfung tat nicht, was sie
behauptete. Jetzt wird am rohen Wert geprüft; danach zehn von zehn richtig.

### Die elf Fälle, ausgeschrieben `[NACHGETRAGEN 04.09.2026]`

**Sie standen nirgends** — die Doku nannte drei plus den gefundenen Fehler.
Das Projekt ist unversioniert; diese Datei ist die einzige Ablage des Prüfers.
Wer nicht weiß, was geprüft wird, baut es beim nächsten Umbau versehentlich ab.

| # | Eingabe | Ergebnis | Warum |
|---|---|---|---|
| 1 | `LiveSetup/Volvo/Business Modul/Norderney` | durchgereicht | der Normalfall, drei Ebenen |
| 2 | `Goldhut` | durchgereicht | null Ebenen, auch ein Normalfall |
| 3 | *(Feld fehlt)* | `None`, still | kein Fehler — die Datei bleibt in `output/` |
| 4 | `""` / `"   "` | `None`, still | leer ist wie fehlend |
| 5 | `/etc` | abgewiesen | absolut, **am rohen Wert** geprüft |
| 6 | `~/woanders` | abgewiesen | Tilde, ebenso roh geprüft |
| 7 | `../oben` | abgewiesen | Ausbruch aus dem Ausgang |
| 8 | `Kunde/../../oben` | abgewiesen | Ausbruch in der Mitte |
| 9 | `/Kunde/Projekt/` | **abgewiesen** | führendes `/` — Fall 5 greift **vor** dem Strippen, genau das war der gefundene Fehler |
| 10 | `Kunde//Projekt` | durchgereicht, **unverändert** | doppelter Trenner; `_saeubern` normalisiert ihn **nicht**, erst `Path` beim Zusammensetzen |
| **11** | `L'Osteria/Bar` · `x'; id; echo '` | **abgewiesen, gemeldet** | **`[NEU 04.09.]`** Zeichenmenge |

**Fall elf ist Engywucks Befund 3.** Die zehn davor prüfen die **Form** des
Pfades — welche **Zeichen** darin stehen, prüfte keiner. Der Ordnername wanderte
in einen Fernbefehl und zerriss dort die Shell-Zeichenkette; mit anderem Inhalt
wäre ein Befehl als `claudebot` gelaufen. Das Feld füllt Claudia auch **aus
gelesenen Dokumenten** — die Klasse *von außen kommen nie Anweisungen*.

Erlaubt sind Buchstaben (mit Umlauten und Akzenten), Ziffern, Leerzeichen und
`- _ . ( ) & /`. **Eine Menge, keine Verbotsliste** — eine Verbotsliste vergisst
das Zeichen, das nächstes Jahr gefährlich wird.

**Der Preis steht dabei:** Ein Kunde `L'Osteria` wird abgewiesen und landet im
Auffangordner statt im richtigen Zweig. Das ist die richtige Fehlerrichtung, und
**die Abweisung wird auf stderr gemeldet**, nicht verschluckt: Sonst läge die
Datei in `output/`, der Ausgang bliebe leer, und niemand wüsste warum.

**Die Kette Ende zu Ende**, gegen einen Wegwerf-Zweig (Adams echte Ablage
unberührt):

```
Generator  →  ausgang/LiveSetup/Volvo/Business Modul/Norderney/Rechnung 012-26.pdf
Ablage     →  Business/Deko/LiveSetup/Volvo/Business Modul/Norderney/Rechnung 012-26.pdf
             Dateien unter DEKO-Service: 0
```

## Die Frage an Adam

**Soll `~/Projects/rechnungen` unter Versionskontrolle?** Ein `git init` mit
einer `.gitignore` für `output/`, `ausgang/`, `.venv` und **`daten/`** (dort
liegen Stammdaten und echte Rechnungen) gäbe dem Projekt einen Rückweg und eine
Historie. **Das ist eine Struktur-Entscheidung in deinem Projekt, deshalb
frage ich statt zu tun.**

Solange es sie nicht gibt, ist dieses Papier der Rückweg.

---

# Nachtrag 03.09.2026 — der Umzug ist vollzogen

**Schritte 2 bis 4 aus dem Befehlsblock gefahren**, auf Adams Bitte von mir
statt von ihm (kein root nötig, nur SSH):

| Schritt | Ergebnis |
|---|---|
| **Projekt auf den Server** | `~/workspace/rechnungen/` — ohne `.venv`, `output`, `ausgang` |
| **`typst`** | 0.15.1 nach `~/.local/bin`, ohne root |
| **Vergleichslauf 012-26** | bestanden, **aber erst im zweiten Anlauf** |
| **Claudias Provisorium** | `~/rechnungen-uebergang` gelöscht — es hat einen Tag getragen |

## Zwei Befunde, die nur der Vergleichslauf finden konnte

**① Der Dienst-PATH kennt `~/.local/bin` nicht.** Gemessen am laufenden
Bot-Prozess: `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin`. Die
Positivliste hätte `typst` freigegeben, die Shell hätte *command not found*
gesagt — die Klasse *am Mac lief alles*. **Gelöst im Generator, nicht am
Dienst** (der bräuchte root): `typst_pfad()` sucht in dieser Reihenfolge
`TYPST_BIN`, `PATH`, `~/.local/bin/typst`. Auf beiden Maschinen gemessen.

**② Auf dem Server fehlten Helvetica Neue und Arial.** typst fiel auf seine
Serifen-Standardschrift zurück — dieselbe Rechnung sah vom Server völlig anders
aus als vom Mac. **Genau der Fall, für den Claudia den Vergleichslauf verlangt
hat.** Gelöst mit **Liberation Sans** (metrisch kompatibel zu Arial, frei, ohne
root unter `~/.local/share/fonts`), als dritter Name hinter den beiden
Mac-Schriften: Wo die da sind, ändert sich nichts. Nachgemessen im Bild, nicht
in der Warnung.

**③ `openpyxl` fehlte** (nur für die Aufstellung, `.xlsx`). Debian 13 sperrt
`pip --user` (PEP 668), deshalb eine **venv im Projekt** — dieselbe Bauform wie
am Mac. Kein `--break-system-packages`.

## Und die Regeln ziehen mit

Neu: **`RECHNUNGSREGELN.md` im Rechnungsprojekt.** Adams Frage dazu war die
wichtigere des Abends: *„Ist denn das jetzt eigene Regeln oder gelten die dann
genauso für Claudia?"* — Bis dahin galten sie nur im Kopf dieser Sitzung.

Die Datei **ergänzt und ersetzt nichts** (Adams ausdrückliche Auflage): Was
Claudia von ihm gelernt hat, gilt weiter; hier steht nur, was in dieser Nacht
neu entschieden wurde. Sie liegt im Projekt, zieht also mit und wird gelesen —
das ist der Ablageweg, den eine Regel im Sitzungsgedächtnis nicht hat.

---

## Nachtrag 04.09.2026 — Spesen als Formel, Fall elf

**Zwei Eingriffe mehr im unversionierten Projekt.** Der Rückweg gehört hierher,
weil es dort kein `git log` gibt.

**① `scripts/generate_aufstellung.py`, Kürzel-Auflösung.** Vier feste Spesen-
Fälle (`klein`, `voll`, `80`, `40`) sind durch **eine Formel** ersetzt:
`Spesen:<prozent>` rechnet den Anteil der vollen Tagespauschale von 28,00 €,
und die Beschriftung trägt immer die Prozentzahl. `Spesen:klein` und
`Spesen:voll` bleiben als Schreibabkürzungen für 50 % und 100 %.

*Warum:* Beim ersten Fall, den die Liste nicht kannte — Abreisetag mit
gestelltem Frühstück, 8,40 € — musste die Aufstellung zu 017-26 auf
`Custom:Spesen 30 %:8.40` ausweichen, einen von Hand eingetippten Betrag.
**Eine Aufzählung bricht beim nächsten Fall, eine Formel nicht.**

*Gemessen:* 100/80/50/40/30 % ergeben 28,00 · 22,40 · 14,00 · 11,20 · 8,40.
Über die drei Custom-Posten der 017-26-Aufstellung gerechnet: **Beschriftung
und Summe unverändert.** `Spesen:800` wird benannt abgewiesen, `Spesen:quatsch`
fällt in den vorhandenen Unbekannt-Zweig.

*Rückweg:* Der ersetzte Block steht im Kommentar darüber vollständig
beschrieben; die vier alten `if`-Zeilen lasen `saetze["Spesen_klein"]`,
`["Spesen_voll"]`, `["Spesen_80"]`, `["Spesen_40"]` und gaben deren
`bezeichnung` zurück. Alle vier Schlüssel stehen weiterhin in `saetze.json`.

**② `daten/saetze.json`, Etikett von `Spesen_40`.** Dort stand *„etablierter
Abreisetag-Satz"*. **Das war das Etikett, nicht die Zahl:** 11,20 € ist ein
**voller** Tag mit zwei gestellten Mahlzeiten; ein Abreisetag mit Frühstück
sind 8,40 €. Der alte Wortlaut steht im neuen Hinweis zitiert.

**③ `scripts/ablage.py`, Fall elf** — siehe die Tabelle oben.
