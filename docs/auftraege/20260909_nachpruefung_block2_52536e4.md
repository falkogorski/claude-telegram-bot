> **An Adam, zur Weitergabe an Mick** · Engywuck · 09.09.2026, 23:00 · geprüft: `52536e4` (Diff bot.py, channels.py, wachposten.py, beide Tests vollständig gelesen), Prüfer hier ausgeführt, eigene Gegenprobe, Claudias Protokoll `conversations/2026-09-09.md` (Log-Repo 22:55)

# Block 2: Kern abgenommen, zwei Befunde vor dem Deploy. Und Schritt 3 hat eine Lücke im Protokoll gezeigt.

## 1. Schritt 3, gelesen in Claudias Protokoll

Sichtbar ist: die erste Nachricht um 22:50:01, vier Werkzeugläufe, die Antwort um 22:50:33. Die Antwort nennt **zu jeder Datei das Datum**, genau das, was die zweite Nachricht verlangte. Das passt zu einem geglückten Zettel, beweist ihn aber nicht: Der Bot hätte die Daten auch von sich aus nennen können.

**Die zweite Nachricht steht nicht im Protokoll, und das ist bauartbedingt**, nicht Zufall: Das Gesprächsprotokoll schreibt eine Nutzernachricht nur in `_run_job` (Zeile 2312). Ein übersprungener Zwilling läuft nie, und der Hook schreibt nichts ins Gesprächsprotokoll. **Adams Nachtrag verschwindet damit aus dem einzigen Gedächtnis, das Wachposten, Mac-Sitzung und Log-Repo lesen.** Das ist Befund B2-1, unten.

**Der Beweis selbst liegt bei dir:** die zwei Zeilen aus bot.err.log, die du Mick geschickt hast (`gereicht` und `uebersprungen`). Bitte auch an mich, dann schließe ich das Risiko aus dem Deploy von 23d01d6 ab. Ohne sie bleibt es offen.

## 2. Was ich an Block 2 gemessen habe

| Messung | Ergebnis |
|---|---|
| `test_leitstand_block2.py` | 21/21 grün |
| `test_wachposten.py` | grün, neue Zeile dabei |
| Regressionslauf im Wegwerf-Baum (mit python3 als venv) | 74/76, eine übersprungen (ffmpeg), eine rot: Selbstcheck wegen fehlender MEMORY.md, ffmpeg und Whisper-Modell. Umgebung, nicht Block 2. |
| Eigene Gegenprobe: Wachposten-Glob auf `<datum>.md` zurückgesetzt, Eingriff per assert, `__pycache__` weg, erwartete Zeile notiert | rot genau dort: `auch Zimmer-Protokolle werden gelesen (Block 2): Zimmer-Protokoll fehlt`. Der Prüfer misst. |
| Zeitbasen | `last_activity` ist `monotonic` (Zeile 13489), `done_log` Wanduhr, `_vor_wie_lange` nimmt Wanduhr. Micks Trennung Dauer/Zeitpunkt stimmt. |
| Log-Abgleich | `log_sync.sh:32` kopiert das ganze Verzeichnis, die Zimmer-Dateien kommen mit. Wirkungs-Regel: nach dem ersten Zimmer-Tag im Log-Repo nachsehen. |

`leitstand()` als Daten, `/zimmer` als Formatierung, Name nur mit `chat_id`: alles richtig, alles wie in Auflage 7 gedacht. Micks Wachposten-Fund war ein echter Geschwister-Fall, richtig mitgezogen.

## 3. Befund B2-2, Halt vor dem Deploy: `/zimmer` bricht, sobald ein Zimmer an Code arbeitet

`cmd_zimmer` sendet mit `parse_mode=MARKDOWN` und setzt den **Auftragstext unverändert** hinein. Ich habe es ausgeführt: Auftrag „lies bitte datei_alt.py und fasse zusammen" ergibt eine Markdown-Nachricht mit einem einzelnen Unterstrich. Telegram lehnt unpaarige Entitäten ab („can't parse entities"), der Aufruf wirft, **die Antwort kommt nie**. Das trifft genau dann, wenn Adam am Bot arbeitet, denn `test_zimmer_block1.py` und `bot.py` sind seine Alltagswörter. Ein Leitstand, der schweigt, sobald gearbeitet wird, ist die Fehlerrichtung, gegen die er gebaut wurde.

`/status` sendet aus genau diesem Grund **ohne** `parse_mode` (Zeile 5083). Der Fix ist derselbe: ohne Markdown senden, Fettschrift weglassen. Und der Prüfer muss es sehen: Seine Attrappe verschluckt heute die Schlüsselwörter. Prüfzeile: Attrappe merkt sich `parse_mode`, Auftragstext mit Unterstrich, `parse_mode` muss `None` sein.

## 4. Befund B2-1, mit in denselben Push: der Zettel gehört ins Protokoll

Beim Hineinreichen (`_nachsteuer_hook`, wo die Zeile „Nachsteuern: N Zeichen" fällt) zusätzlich `sess.logger.log_user(...)` mit einem Kennzeichen, etwa `[nachgesteuert]`, und beim Überspringen des Zwillings ein `log_event`. Prüfzeile: Zettel hineinreichen, danach steht der Text in der Protokolldatei des Zimmers. Ohne das fehlt im Protokoll genau die Nachricht, die der fließende Dialog schneller machen sollte.

## 5. Micks Nebenbefund `chat_id` im Schlüssel: richtig gemeldet, noch nicht bauen

Heute kollidiert nichts. Aber: **Vor dem ersten Haus** muss der Schlüssel `chat_id` tragen, sonst teilen sich zwei Häuser mit derselben Themen-Kennung eine Sitzung, und niemand sieht es. Das gehört als Auflage in Block 4 (Verbund), nicht in Block 2. F-Liste mit diesem Auslöser.

## 6. Reihenfolge

B2-2 und B2-1 sind zusammen unter einer Stunde. Ein Push, ich prüfe kurz, dann Deploy von Block 2 mit dem berichtigten Deploy-Block (Stand ablesen, `--ff-only`, `rc=0/77`, Neustart) und einer Prüfzeile: `/zimmer` im Hauptchat, während ein Auftrag mit Unterstrich im Text läuft, antwortet. Danach Block 3.
