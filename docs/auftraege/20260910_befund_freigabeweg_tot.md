> **An Adam, zur Weitergabe an Mick** · Engywuck · 10.09.2026, 01:09 · geprüft: `bot.py@211b383` Zeile 3943 und Umfeld, Import-Stellen, `pyflakes` über die ganze Datei, Vergleich mit `e335c23`

# Der Freigabeweg für Schreibwerkzeuge ist tot, seit heute Abend. Claudia hat recht.

## Was gemessen ist

- `bot.py:3943` (in `can_use_tool`, ab Zeile 3588): `datetime.now()` ohne `datetime` im Namensraum. Kein Modul-Import, die sieben lokalen Importe liegen in anderen Funktionen. Ergebnis: `NameError` bei **jedem** gezeigten Dialog.
- Die Zeile steht **innerhalb** der `try`-Klammer, die das Senden absichert. Der `except` antwortet mit `PermissionResultDeny("bot failed to ask user")`. Also: Dialog wird gesendet, Adam drückt, das Werkzeug ist trotzdem verweigert. Genau Claudias Ablauf um 01:03:44.
- Herkunft `bcb3a01` (M-3, 09.09. 11:21). Live seit dem **ersten** Deploy heute Abend (23d01d6, 19:26), nicht erst seit 211b383. Aufgefallen ist es nicht, weil seither kein Edit oder Write gefragt hat; Bash läuft im Auto-Zustand am Dialog vorbei.
- `pyflakes bot.py`: **genau eine** Meldung „undefined name" in der ganzen Datei, diese. Bei `e335c23` (vor M-3): null.

## Warum es niemand gesehen hat, und das ist der eigentliche Befund

Das ist der **zweite NameError in einem abgesicherten Pfad** in drei Wochen. Der erste war am 18.08. im Sendepfad. Beide Male grüner Regressionslauf, beide Male ein `except`, das den Fehler in Ruhe verwandelt. Der Regressionslauf führt den Dialog-Sendepfad nicht aus, und ein `try/except` um Buchführung macht aus einem Buchführungsfehler eine Verweigerung.

**Mein Anteil:** Ich habe M-3 am 09.09. abgenommen. Ich habe per `ast` gemessen, dass `dialog_gezeigt` an der Sendestelle **aufgerufen** wird. Ob die Zeile **läuft**, habe ich nicht gemessen. Ein Aufrufknoten im Baum ist kein ausgeführter Pfad, das steht in unserer eigenen Regel vom 22.08. Kurs-Blick-Zeile.

## Fix, drei Teile, alle klein

1. `from datetime import datetime` am Modulkopf, die sieben lokalen Importe dürfen bleiben.
2. `dialog_gezeigt(...)` in eine **eigene** `try/except`-Klammer mit `log.exception`, nach dem Senden. Ein Fehler in der Messung darf nie ein Werkzeug verweigern. Das ist die Regel hinter dem Fix: **Buchführung sitzt nie in der Klammer, die eine Entscheidung trägt.**
3. **Zwei Prüfer**, weil zwei Klassen:
   - **Statisch, für die ganze Klasse:** `pyflakes` in `scripts/regressionstest.sh`, gefiltert auf `undefined name`, rot bei jedem Treffer. Deterministisch, unter einer Sekunde, hätte beide NameErrors gefunden, bevor sie committet waren. `pyflakes` in die `requirements.txt` (PyPI, kostenfrei, reines Python). Sieben weitere Meldungen gibt es heute (ungenutzte Importe), die werden **nicht** rot, sonst schaltet der Prüfer sich binnen einer Woche selbst ab.
   - **Verhalten, für diesen Pfad:** ein Prüfer, der `make_permission_callback(uid, None)` baut, eine Sitzung mit Bot-Attrappe einhängt (deren `send_message` ein Objekt mit `message_id` zurückgibt), die Freigabe aus einem zweiten Task beantwortet und misst: Ergebnis ist `PermissionResultAllow`, **und** die `dialog_gezeigt`-Zeile steht im jsonl. Gegenprobe: Import wieder entfernen, Zeile rot.

## Zwei Wege für heute Nacht, meine Empfehlung: warten

- **Jetzt:** Mick war um 01:06 noch aktiv. Fix, Prüfer, Regressionslauf, Push, Deploy mit Neustart. Etwa eine Stunde, um zwei Uhr nachts. Der letzte Fehler dieser Art (c398d24, Commit ohne gelesenen Lauf) entstand unter genau solchem Druck.
- **Morgen früh, vor Block 3:** Über Nacht braucht nichts einen Dialog. Bash im Auto-Zustand läuft, der 4-Uhr-Check ist modellfrei, Claudia liest und misst. Nur ihr Register-Eintrag wartet. **Das ist mein Rat.** Kein Rollback: vor `bcb3a01` liegen Block 1b und 2.

**Prüfzeile nach dem Deploy:** Claudia bittet um einen Edit (den Register-Eintrag), Adam drückt Genehmigen, die Datei ist geändert, und `bash_dialog_auswertung.py` zählt den Dialog als „TATSÄCHLICH vorgelegt". Beides zusammen, sonst ist nur die Hälfte repariert.
