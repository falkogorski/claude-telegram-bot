> **An Adam, zur Weitergabe an Mick** · Engywuck · 11.09.2026, 03:17 · geprüft: Zweig `probe-f22`, Commit `ce5663b`, gegen Basis `0ffa054`; Struktur gelesen, acht Prüfer und Regressionslauf ausgeführt, eigene Gegenprobe

# F-22 im Klon: abgenommen. Merge und Deploy erst nach Adams Rückkehr, mit Prüfung in der Zielumgebung.

## Gemessen

| | Ergebnis |
|---|---|
| Türen (`_sess`, `_mb_opt`, `_get_mailbox`, `_ensure_worker`, `close_session`, `ensure_session`, `make_permission_callback`, `nachsteuer_ordner`) | nehmen alle genau einen `Faden`; keine Reste von `fd[0]`/`fd[1]`, keine Zwei-Zahlen-Aufrufe |
| `Faden` als `NamedTuple` (person, chat, thema), `faden()`, `faden_von_update`, `faden_von_job` | vorhanden, `_run_job` holt die Sitzung über `faden_von_job(job)` |
| Reconcile | baut den Faden aus `chat_id` des Datensatzes |
| Zettel-Ordner | `<person>_<chat>_<thema>` |
| pyflakes | null undefinierte Namen |
| Prüfer Block 1 (48), Block 2, Block 3 (104), Freigabeweg, Stall, Reaktionen, Eingangsschranken, Voice | alle grün |
| Regressionslauf hier | 78/80, die bekannten Umgebungs-Roten |
| **Eigene Gegenprobe:** Chat aus `faden()` entfernt, Eingriff zeilengenau verifiziert, Syntax geprüft | **fünf Zeilen rot**, genau die Schlüssel-Zeilen |

Mein erster Versuch der Gegenprobe traf die mehrzeilige `return`-Anweisung nicht und maß nichts; der Prüfer blieb grün, weil nichts geändert war. Erkannt an der fehlgeschlagenen Verifikation, wiederholt. Dritter Fall dieser Klasse bei mir in einer Woche. Das gehört in den Kurs-Blick als Muster, nicht als Einzelfall.

## Micks drei heikle Stellen

1. `_run_job` und Arbeiter: der Faden kommt aus dem Job, nicht aus dem Umfeld. Gelesen, trägt.
2. Reconcile mit altem Datensatz ohne `chat_id`: ergibt `chat=None`, ein eigener Faden. Heute unerheblich, weil alle Text-, Voice- und Medien-Datensätze `chat_id` tragen; nur der Reaktions-Datensatz nicht, und der ist nach Neustart ohnehin Hauptfaden. Kein Halt.
3. Reaktionen auf Zimmer-Antworten bleiben im Hauptfaden des Chats. Bekannt, unverändert, F-Liste.

## Empfehlung: nicht vor der Reise

Adam ist die nächsten Tage unterwegs und arbeitet wenig. Der Live-Stand `495ca45` ist geprüft, deployt und in beiden Hälften der Empfangs-Prüfzeile grün. F-22 bringt heute keinen Nutzen, weil es kein Haus gibt, und es ist ein Schlüsselwechsel über 384 Zeilen, der nur im Klon lief, nicht in der Zielumgebung (R1). Ein Deploy davon in der Nacht vor einer mehrtägigen Abwesenheit wäre genau der Fall aus der Lehre vom 29.07.: gebaut, deployt, niemand schaut hin.

**Also:** `probe-f22` bleibt stehen, kein Merge. Nach der Rückkehr: Merge, ein Deploy zusammen mit dem `/empfang`-Umschalter (`0f4087e`, liegt im Hauptbaum, ist nicht deployt), R1-Prüfzeile auf dem VPS (`/status`, `/zimmer`, eine Nachricht mit Werkzeuglauf, eine Freigabe), dann erst das erste Haus.

**Bis dahin für Adam unterwegs:** Der Bot läuft auf `495ca45`. `/empfang` aus dem Menü zeigt nur den Stand; ein- und ausschalten geht getippt mit `/empfang an` und `/empfang aus`. Beides ist bekannt und in Ordnung.

## Nichts Halbfertiges offen

Live: Block 1, 1b, 2, 3, 3b, 3c, Hotfix H-1 bis H-5, A-4. Im Hauptbaum, nicht deployt: der `/empfang`-Umschalter. Im Klon: F-22 voll. Bei Mick: nichts Offenes, Laufplan auf Warten. Bei mir: Wochenauswertung 16.09. (erste gemessene Dialogzahl), Kurs-Blick mit meinen drei Punkten (Deploy-Block ohne Blick auf die Kette, zwei kaputte Gegenproben, M-2-Abnahme am Bericht statt am Angriffsweg), F-22-Merge nach der Rückkehr.
