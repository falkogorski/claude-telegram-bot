> **An Adam, zur Weitergabe an Mick** · Engywuck · 10.09.2026, 19:44 · geprüft: `606ce26..d9742f0` (bot.py-Diff gelesen), Prüfer ausgeführt, eigene Proben an Befehlszeile, Herkunft, Stoppwort und Sendestellen

# Block 3b (d9742f0): abgenommen bis auf einen Punkt aus A-2. Kein eigener Deploy, zusammen mit 3c.

## Gemessen, alles grün

| Was | Ergebnis |
|---|---|
| `test_empfang_block3` 79 Zeilen · Regressionslauf hier | grün (78/80, die bekannten Umgebungs-Roten) |
| **A-3, Befehlszeile der Sekretärin** aus `sekretaerin_optionen` über den SDK-Transport gebaut | `--setting-sources=` (leer) · `--strict-mcp-config` · `--max-turns 6` · `--tools ''` · `--allowedTools mcp__empfang__zettel_ablegen` · `--permission-mode dontAsk` |
| **A-3, Herkunft** `empfang_darf_weitergeben` | eigenes Wort → darf · weitergeleitet (`forward_date`) → darf nicht |
| **A-3, Stoppwort** bei eingeschaltetem Knopf | „stopp, das ist falsch" → geht nicht an den Empfang, normale Nachricht → geht |
| **A-5** per `ast` über `_run_job`, `_notify_job_failed`, `_handle_stalled_session` | null Sendestellen ohne Faden |
| **A-2** Kennung mit `zettel_schluessel`, `_neuere_wartende` mit `zettel_schluessel`, `output_thread_id` fällt auf `thread_id`, Ursprungsnachricht wird persistiert und beim Antworten aufgelöst (das schließt auch den Voice-Platzhalter), Link-Callback abgefangen, `send_chunked` | im Diff gelesen, Prüfer grün |
| **A-1** Schloss, Verwerfen bei Zeitüberlauf, `connect` in der Zeitgrenze, Selbstcheck „Empfang wohlgeformt" | in 606ce26, bereits live |
| `darf_einschlafen` mit `thread_id` pflichtig (d9742f0) | ja |

Micks Abweichung bei A-1 (Client verwerfen, Eintrag mit Schloss behalten) ist richtig, seine Begründung stimmt: Wartende Läufe halten das Schloss.

## Was fehlt, ein Punkt

**Der Auftrag, den die Sekretärin per Werkzeug ins Zimmer legt, wird nicht persistiert.** `auftrag_einreihen` (5835 bis 5894) enthält kein `pending.record`, und `_zettel_ablegen` auch nicht. Persistiert wird jetzt die **Ursprungsnachricht** Adams, aber die wird beim Antworten aufgelöst. Ein Neustart, bevor das Zimmer den Auftrag abarbeitet, verliert ihn, und Adam hat „Abgelegt in …, Position N" als Zusage. Das war A-2, Punkt zwei, im Ultracode-Befund (F6, A8-2). Klein: synthetischer Schlüssel aus `zettel_id`, `pending.record` mit `thread_id` und `output_chat_id`, `pending_key` in den Job, Prüfzeile mit Reconcile. **Vor dem ersten `/empfang an`.**

## Zwei Antworten auf Micks offene Fragen

**presend:** Ja anschließen, aber nur die eine Hälfte. `check_and_fix` hat zwei Teile: den Vollständigkeits-Vermerk über wartende Nachrichten, der ist für den Empfang gegenstandslos, und den Wächter für scharfe Befehle in der Ausgabe. Der zweite gilt hier besonders: Die Sekretärin hat kein Bash, aber sie kann Adam einen Befehlsblock schreiben, den er ins Terminal setzt. Also `check_and_fix(antwort, pending_newer=0, eingearbeitet=0)`, ohne Korrekturrunde, vor dem Senden. In 3c.

**Die Herkunftsprüfung erkennt Telegram-Weiterleitungen**, nicht kopierten Text. Das ist die Grenze der Bauart, und sie ist vertretbar: Wer Text hineinkopiert, hat ihn selbst gesendet. Ins Register, nicht in den Bau.

## Deploy

**Kein eigener Deploy für 3b.** Der Empfang bleibt aus, bis 3c steht; von 3b wirkt ohne Knopf nur A-5 (Meldungen bleiben im Zimmer) und das pflichtige `thread_id`, beides heute unerheblich, weil es nur den Hauptfaden gibt. Ein Deploy kostet Adam einen Neustart, und Adam mag keine halbfertigen Sachen. Also: 3c bauen (A-6, die zehn Prüfzeilen, F-22, die Persistenz oben, presend), meine Nachprüfung, dann **ein** Deploy, dann `/empfang an` mit der Prüfzeile aus Micks Deploy-Block (Antwort mit 👩‍💼 in Sekunden, und der Auftrag steht wirklich im Zimmer).

Die eine Messung, die nur der Betrieb liefern kann, bleibt benannt: ob die CLI der Sekretärin ihr Werkzeug im Betrieb anbietet. Das ist die erste Prüfzeile nach dem Einschalten.
