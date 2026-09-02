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
