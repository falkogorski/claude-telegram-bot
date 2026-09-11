# Nachtlese 11.09. — erste Routine-Lese

**11.09.2026, 05:35** (date) · Engywuck → Adam (→ Mick, → Claudia) · Log-Repo bis 05:32 (Zeile 948),
Bot-Repo bis `f59c16f` (05:26) · Live-Stand unverändert `495ca45`, kein Deploy.

## 1. Claudia (Log 05:06–05:32)

Sie hat beide Berichtigungen aus meinem Papier übernommen: Rechnungs-Fix ist live,
die „zwei Zustände" tragen nicht, die Anfragen kamen aus Write/Edit. Register und
Tagescheck-Papier nachgezogen. **Ein Vorschlag von ihr, der von Adams Entscheid
abweicht:** Write/Edit nur für **Vorgang und Sitzung**, nicht „bis zum Neustart", und
der Gedächtnis-Ordner bleibt außen vor. Beides ist enger als Adams „ja" und die
sicherere Lesart. Mick hat Adams Wortlaut (alle drei) an `_NO_ALWAYS_TOOLS` vermerkt.
→ **Entscheid Adam, ein Wort:** alle drei Reichweiten, oder Claudias engere Fassung
(nur Vorgang und Sitzung, Gedächtnis-Ordner hart)? Mein Rat: **Claudias Fassung.**
Sonst nichts Neues; keine Fehler in `bot-errors.log`, Tagescheck seit 04:10 unverändert.

## 2. Mick (sechs Commits seit meiner letzten Prüfung, 04:51–05:26)

| Commit | Was | Nachprüfung |
|---|---|---|
| faa3e15, 048ed6e | Befehlsblöcke Log-Takt, Selbstauslösung berichtigt (nur `conversations`) | stimmt mit dem VPS-Stand überein |
| 537809c | **Prüfzeile 8:** Auslöser als `TypeHandler group=99` registriert, über `ast.Call` | 8/8 grün; Mick fuhr beide Gegenproben (Aufruf weg, Kommentar-Variante) rot |
| fafcf3b | Adams vier Entscheide: Riegel `SCHARF: nein` mit den Zahlen (7/14, null grün), Vermerk an `_NO_ALWAYS_TOOLS`, F-23 Hygiene-Neustart wartet (Aufschub 30 min, `arbeitende_zimmer()`) | Wortlaut korrekt, Zahlen stimmen mit deiner Zählung |
| 12eb332 | **A5:** `flock -n` auf Schloss, Quittung per `mktemp` unter `/.quittung/`, `find -prune` für venv/node_modules/.git, `${f##*/}` statt `basename`, rsync schließt `venv/`, `node_modules/` aus | `bash -n` ok; Prüfer `test_log_sync_takt.py` 5/5 |
| f59c16f | Tagescheck sieht Pfad-Einheiten (`list-unit-files --type=path`, abgeschaltet = bewusst), Register, Blaupause | Code gelesen, trägt |

**Zwei Befunde an A5, beide klein:**

1. **Meine Gegenprobe: `-prune` entfernt → 5/5 bleiben grün.** Mick schreibt das
   selbst in den Prüfer („diese Zeile misst NICHT das -prune … Laufzeit lässt sich
   nicht flackerfrei messen"). Es geht aber ohne Zeit: Die Attrappe hat bereits
   `venv/lib/README.md`. Ohne `-prune` erscheint die Datei in der Quittung als
   „unklar — bitte melden", mit `-prune` nicht. **Prüfzeile:** „venv/lib/README.md
   steht nicht in der Quittung". Gegenprobe: `-prune` weg → rot. Deterministisch.
2. **Das Schloss liegt unter `/tmp`.** Läuft der Dienst mit `PrivateTmp` (für den
   Bot-Dienst gemessen, für den Log-Sync-Dienst nicht dokumentiert), sehen Dienst und
   Handlauf zwei verschiedene `/tmp` — dann schützt das Schloss genau den Fall
   nicht, den Adam um 05:0x gemessen hat. Schloss nach `$HOME/logsync/.lock`
   (oder `$REPO/../.lock`), unabhängig von der Dienst-Härtung.

Beides gehört noch in diesen Nachtblock (Nachprüfung, keine dritte Runde).

**Noch offen bei Mick:** A1 (Empfangs-Knopf, `/empfang_an`/`/empfang_aus`,
Kontext-Zeile Urheber), A2 (usage.json wie Heartbeat), A3 (Sekretärin-Briefing),
A4 (konzept_pdf cwd + Schrift). Laufplan lief um 05:26 noch.

## 3. Für Adam, je ein Satz

- Write/Edit-Reichweite: alle drei oder Claudias engere Fassung? (Rat: engere.)
- Sonst nichts. Deploy nach der Rückkehr: ein ff mit Schritt-0-Zeile, F-22 draußen.

## 4. Texte

**An Mick:** Nachtlese 05:35: A0/A5 geprüft, trägt. Zwei Nachträge zu A5 im selben
Block: (1) Prüfzeile „venv/lib/README.md steht nicht in der Quittung" (misst -prune
ohne Uhr; Gegenprobe -prune weg → rot). (2) Schloss aus /tmp nach $HOME/logsync/.lock,
weil PrivateTmp Dienst und Handlauf trennt. Danach A1–A4 wie im Papier.

**An Claudia:** Deine engere Fassung (Write/Edit nur Vorgang + Sitzung, Gedächtnis-
Ordner hart) liegt Adam als Entscheid vor, mit meiner Empfehlung dafür. Riegel ist
geschlossen (fafcf3b, Zahlen aus Adams Zählung). Log-Abgleich ist ab dem nächsten
Deploy in Sekunden statt 30.
