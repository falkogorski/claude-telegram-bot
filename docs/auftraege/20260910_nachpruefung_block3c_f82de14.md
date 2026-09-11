> **An Adam, zur Weitergabe an Mick** · Engywuck · 10.09.2026, 23:36 · geprüft: `d9742f0..495ca45` (bot.py-Diff gelesen), sechs Prüfer ausgeführt, sechs eigene Entkernungen gefahren, Regressionslauf, Deploy-Block a50b4ab gelesen

# Block 3c (f82de14): abgenommen. Ein Deploy für Block 3 gesamt, dann `/empfang an` mit der zweiteiligen Prüfzeile.

## Gemessen

| | Ergebnis |
|---|---|
| Prüfer Block 1 (47), Block 2 (33), Block 3 (104), Freigabeweg (11), undefinierte Namen, Wachposten | alle grün |
| Regressionslauf hier | 78/80, die bekannten Umgebungs-Roten |
| **Sechs eigene Entkernungen** in einer Kopie, Eingriff per assert, `__pycache__` weg, Syntax geprüft, erwartete Zeile vorher notiert | **alle sechs rot an der erwarteten Stelle:** E1b `ensure_session(user_id)` plus Kommentar → `ensure_session:2523` · E2 Hook-Attrappe → „es ist WIRKLICH der Nachsteuer-Hook" · E9 Logger ohne Zimmer → `[5139]` · E4 undefinierter Name in `scripts/wachposten.py` → gefunden · E10 Dialog ohne Faden → „erscheint IM ZIMMER" · A5-1 Drossel tot → zwei Zeilen rot |
| 3c-1 Persistenz des Werkzeug-Auftrags | `pending.record` in `auftrag_einreihen`, Schlüssel aus `zettel_id`, Reconcile echt gemessen (Micks eigene Gegenprobe fand seine erste Fassung) |
| 3c-2 presend | `check_and_fix` am Empfangspfad (11622), nur die Wächter-Hälfte |
| A-6 | `vorlesen_setzen`, `dauerfreigabe_merken`: eine Tür, setzt Vorlieben und alle Sitzungen; `_set_bash_auto` und der 🔓-Knopf rufen sie |
| F-22 Teil 1 | Registerschlüssel `(chat_id, kennung)`, Dateiname trägt den Chat, Gegenrichtung beim Lesen |
| Deploy-Block a50b4ab | Schritt 0 mit der Zeile, die zeigt, was mitkommt; Rückweg; zweiteilige Prüfzeile nach dem Einschalten |

Micks Bauform für E1b ist die richtige: Kein Ein-Argument-Aufruf mehr, der Hauptfaden heißt `thread_id=None` im Code. Ein Kommentar kann nichts mehr behaupten.

**Mein Fehler dabei, für den Kurs-Blick:** Meine erste Gegenprobe zu E1b meldete „grün, blind". Sie war es nicht; ich hatte die Zeile mit falscher Einrückung eingesetzt, der Import brach ab, und mein Probelauf las „kein Rot" als grün. Das ist derselbe Fehler wie am 04.09. (Zeilenfortsetzung), und dieselbe Klasse wie Micks „Prüfer stürzt ab statt rot": Ein Eingriff, der die Datei bricht, misst nichts. Sauber wiederholt, mit `py_compile` vor dem Lauf: rot an der erwarteten Stelle.

## Micks F-22-Entscheid: richtig

Die Hälfte, die heute schadet, ist zu. Der volle Schlüsselwechsel ist gemessen 80 Aufrufe groß, gehört in einen eigenen Block mit Klon-Probe, vor dem ersten Haus. Nicht um halb zwölf.

## Deploy, jetzt, Block 3 gesamt

Micks Block a50b4ab trägt. Schritt 0 erwartet **16 Commits** zwischen `606ce26` und `495ca45`, alle aus 3b, 3c und Berichten; ich habe sie gezählt. Danach Schritt 1 und 2 wie gehabt, dann:

**Schritt 3, der Empfang:** `/empfang an`, dann eine Nachricht, die Arbeit bedeutet, etwa *„Zähl die Prüfzeilen in scripts/test_empfang_block3.py und sag mir die Zahl."* Hälfte (a): binnen Sekunden eine Antwort mit 👩‍💼. Hälfte (b), die eigentliche: `/zimmer` zeigt den Auftrag im Hauptchat, und später kommt die Antwort des Zimmers mit der Zahl. Kommt (a) ohne (b), ist es die eine Messung, die nur der Betrieb liefert: Die CLI bietet der Sekretärin ihr Werkzeug nicht an. Dann `/empfang aus` und an mich.

## Nachtblock, wenn Adam ihn freigibt

Ein Kandidat, und nur der: **F-22 voll im Klon** (`chat_id` in Schlüssel, Warteschlange, Arbeiter, Nachsteuer-Ordner), mit Morgenbericht und ohne Deploy. Das ist die Voraussetzung für das erste Haus und der einzige offene Block, der keine Entscheidung von Adam braucht. Kein weiterer Ultracode-Lauf in dieser Runde.
