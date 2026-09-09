> **An Adam, zur Weitergabe an Mick** · Engywuck · 09.09.2026, 21:01 · geprüft am Code: `b30a460` (Diff bot.py 806 Zeilen vollständig gelesen, Tests gelesen), Prüfer hier ausgeführt, eigene Gegenprobe gefahren, CLI-Bündel 2.1.219 durchsucht

# Block 1b: abgenommen. Deploy mit Neustart, drei Prüfzeilen, eine davon ist der Hook-Beweis.

## Was ich gemessen habe

| Messung | Ergebnis |
|---|---|
| `test_zimmer_block1.py` im Wegwerf-Baum | 40/40 grün |
| `test_stall_5_18.py` (Fall 5, hängendes Zimmer 7) | grün, Hauptfaden unberührt |
| Regressionslauf im Wegwerf-Baum | 71/75, die vier Roten sind Container-Artefakte: kein `.venv`, kein `MEMORY.md`, kein ffmpeg, kein Whisper-Modell. Die zwei venv-abhängigen Prüfer nachgefahren mit Verweis auf python3: 40/40 und 17/17 grün. Nichts davon berührt Block 1b. |
| Eigene Gegenprobe der Mengen-Zeile: `_mb_opt(user_id, job.thread_id)` in `_count_newer_pending` entkernt, `__pycache__` weg, Eingriff per assert verifiziert, erwartete Zeile vorher notiert | rot genau dort: `jede Ein-Argument-Tuer ist als Hauptfaden BEGRUENDET — _mb_opt:2076`. Der Prüfer misst. |
| Die vier verbliebenen Ein-Argument-Stellen | alle vier mit `# Hauptfaden:` und Grund, alle vier Gründe tragen (Reaktion ohne Thema, Autorun ohne Absender, Startnachricht ohne Absender, Vorlese-Zustand der Person) |
| CLI 2.1.219 im SDK-Bündel 0.2.127: kennt sie `additionalContext` bei `PreToolUse`? | Ja, im Schema gemessen: `hookEventName: "PreToolUse" … additionalContext: string`. Damit ist der Weg des Zettels auf der CLI-Seite vorhanden. Bewiesen ist er erst live (unten). |

## Die sechs Stellen und die zwei Funde: richtig

Alle Rücklagen in `_run_job` nehmen `job.thread_id`, nicht die lokale Variable. Das ist die richtige Wahl, Micks Begründung (Cross-Chat-Ablage) stimmt. Freigabe-Rückruf je Zimmer mit Suche über `request_id`: eindeutig, fail-closed, `callback_data` wächst nicht. Stopp-Pfad, Wiederaufnahme, Stall-Neustart mit Faden von der Mailbox: richtig. `thread_id` am Stall-Wächter pflichtig statt vorbelegt ist die richtige Lehre, sie gilt allgemein: **Ein Vorgabewert, der das alte Verhalten weiterlaufen lässt, ist die Lücke.**

Reaktionspfad geprüft: Der Freigabe-Zweig kehrt auf jedem Weg zurück, danach ist `sess` immer der Hauptfaden. Kein gemischter Zustand.

## Der Zettel-Schreiber: das Design trägt, mit einer benannten Grenze

Ich habe die Fälle durchgespielt: Nachricht während Werkzeuglauf (Zettel kommt an, Zwilling wird übersprungen) · Nachricht ohne weiteren Werkzeugaufruf (Zettel nie gelesen, Zwilling läuft) · Auftrag scheitert (Zwilling läuft) · zwei Nachrichten hintereinander (beide im selben Zettelsatz, beide übersprungen) · Neustart dazwischen (Register leer, Zwilling läuft, im schlimmsten Fall doppelt gearbeitet). Kein Weg verliert eine Nachricht. Zwischen `busy` und dem Schreiben liegt kein `await`, der laufende Auftrag kann nicht wechseln. `outcome` ist vor dem `try` gebunden, das `finally` kann nicht brechen.

**Die Grenze, die im Design steckt und die Adam kennen sollte:** „Gelesen" heißt: an einer Werkzeuggrenze hineingereicht. Es heißt nicht: im Ergebnis berücksichtigt. Kommt der Zettel beim letzten Werkzeugaufruf an, kann die Antwort ihn nur noch streifen, und der Zwilling wird trotzdem übersprungen. Das ist der Preis des fließenden Dialogs, den Adam am 09.09. bewusst gewählt hat. Ich nenne ihn, damit er nicht als Fehler gemeldet wird, wenn er das erste Mal auftritt.

## Zu Micks Frage: kein SDK-Doppelgänger

Die Mengen-Zeile misst die Abwesenheit des Arguments, ich habe das richtige Argument an allen Stellen gelesen. Nach der Konvergenz-Bremse endet die Kette hier. Was ein Prüfer nicht sieht: ein vorhandenes, aber falsches Argument. Das ist die Fächerung für Ultracode nach Block 3, nicht eine dritte Runde jetzt.

## Zwei Kleinigkeiten in die F-Liste, kein Halt

- Nach einem Neustart nennt die Startnachricht nur einen laufenden Auftrag des Hauptfadens. Ein Zimmer-Auftrag bleibt unerwähnt. Das deckt Block 2 (Leitstand), nicht Block 1b.
- Ein übersprungener Zwilling landet nicht in `done_log`. Für `/status` unsichtbar, harmlos.

## Deploy: jetzt, mit Neustart, drei Prüfzeilen

Schritt 0 bis 2 wie im berichtigten Deploy-Block (Stand ablesen und notieren, `merge --ff-only b30a460`, Regressionslauf mit `rc=0` oder `rc=77`, Neustart, `active`). Auf dem VPS erwarte ich 74/75 mit der Heartbeat-Übersprungenen.

**Schritt 3, der Hook-Beweis, in beide Richtungen:**

1. Dem Bot einen Auftrag mit mehreren Werkzeugschritten geben, etwa: *„Lies nacheinander die letzten drei Dateien in `docs/auftraege` und fasse jede in einem Satz zusammen."*
2. Sofort danach, während er arbeitet, eine zweite Nachricht: *„Und nenne bei jeder auch das Datum aus dem Dateinamen."*
3. Die Quittung auf die zweite Nachricht muss lauten: *„📨 Notiert — ich reiche es dem laufenden Vorgang gleich hinein, ohne ihn zu stoppen."*

Danach:

```bash
ssh claudebot 'grep -h "Nachsteuern" ~/claude-telegram-bot/logs/bot.err.log | tail -5'
```

**Prüfzeile:** zwei Zeilen: `Nachsteuern: N Zeichen an den laufenden Auftrag gereicht (Zimmer haupt)` und `Nachsteuern: Auftrag <id> uebersprungen`. Und im Chat **genau eine** Antwort, die die Daten nennt. Zwei Antworten, oder eine ohne Daten, oder keine „uebersprungen"-Zeile: an mich, nicht neu deployen. Rückweg wie gehabt: `reset --hard` auf den Stand aus Schritt 0.

Erst diese Zeilen schließen das Risiko, das seit dem Deploy von 23d01d6 offen steht.

## Dann Block 2

Nach grünem Schritt 3 kann Mick Block 2 beginnen (Leitstand-Minimum, `/zimmer`, Protokoll je Zimmer). Zu Micks Frage an Adam, ob heute noch: Das ist Adams Kontingent und Adams Abend. Meine Empfehlung: Deploy und Schritt 3 heute, weil sie den offenen Beweis liefern; Block 2 morgen, weil er ein voller Zwei-Stunden-Block ist.
