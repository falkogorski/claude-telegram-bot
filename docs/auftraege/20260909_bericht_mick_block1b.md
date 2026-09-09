> **Zweck: WEITERGABE → Engywuck** (Nachprüfung) · **ANSICHT** für Adam ·
> **Zu tun (Adam):** weiterreichen; Deploy erst nach Engywucks Befund.
> **Stand:** `b30a460` gepusht · 09.09.2026, 20:20

# Block 1b — die Wege, nicht nur die Träger

**Alle sechs Stellen gebaut, der fehlende Schreiber auch.** 75/75 im Klon und
im Hauptbaum, Zielumgebung 41/43 (zwei übersprungen), Klon entfernt.
**Nenner:** 6 von 6 Stellen aus deiner Nachprüfung · 1 von 1 Schreiber ·
**49** Ein-Argument-Stellen gemessen, **4** begründet übrig.

## Deine sechs Stellen

| # | Gebaut | Anmerkung |
|---|---|---|
| 1 | `make_permission_callback(user_id, thread_id)`; der Knopf findet sein Zimmer über `_sess_mit_anfrage()` | wie vorgeschlagen — die `callback_data` wächst nicht |
| 2 | `_sess(user_id, _fd_thread)` im Stopp-Pfad | |
| 3 | `_get_mailbox(user_id, job.thread_id)` **dreimal**, dazu **alle sechs** `close_session` in `_run_job` | die lokale `thread_id` ist bei Cross-Chat-Ablage `job.output_thread_id` — deshalb überall `job.thread_id` |
| 4 | `_get_mailbox(uid, r.get("thread_id"))` | |
| 5 | `_handle_stalled_session(..., *, thread_id)` — **pflichtig**, Faden von der Mailbox | dieselbe Stelle entmachtete über `SESSIONS.pop` auch die falsche Sitzung |
| 6 | je Handler entschieden und hingeschrieben | siehe unten |

**Zwei Funde, die über deine Liste hinausgehen:** `close_session(user_id)` im
**Worker** selbst (`_session_worker`, sanfter Modellwechsel) und
`_mb_opt(user_id)` in `_count_newer_pending` — beide zählten die falsche
Schlange.

## Zu Stelle 6: was Hauptfaden bleibt, und warum

**Faden der Nachricht:** `/reset`, `/status`, `/stopp`, die ganze Tastatur
(besonders die Knöpfe, die eine Sitzung schließen und neu öffnen), die
PDF-Zusammenfassung.

**Person, wirkt in JEDEM offenen Zimmer** (`_alle_sess()`): Vorlesen, Stille,
Werkzeugspur, Auto-Zustand, `/freigaben reset`. Ein Schalter, der nur ein
Zimmer trifft, ist ein Schalter, der lügt.

**Ausdrücklich Hauptfaden, mit Grund im Code:** Startnachricht nach Neustart ·
Vorlese-Zustand der Neustart-Bestätigung · Autorun · das 5.9-Vokabular bei
Reaktionen. Letzteres, weil **Telegram bei `MessageReactionUpdated` keine
`message_thread_id` liefert** — der Faden ist dort nicht ermittelbar. Die
**Freigabe-Hälfte** derselben Funktion findet ihr Zimmer trotzdem, über die
Nachricht (`_sess_mit_botnachricht()`).

## Der Zettel-Schreiber — deine drei Bedingungen, einzeln gemessen

Der Zettel heißt `<auftragskennung>__<message_id>.txt`. Der Hook liest nur die
Zettel des laufenden Auftrags; die Kennung holt er sich zur Laufzeit aus
`mb.current_job` — er läuft ja **in** diesem Auftrag.

- **Nichts Altes:** Reste werden am Auftragsende gelöscht. Gemessen auch in der
  Gegenrichtung: ein Zettel des vorigen Auftrags erreicht den nächsten nicht.
- **Nichts doppelt:** Ein RAM-Register merkt sich *gelesen* und *erledigt*.
  Übersprungen wird der eingereihte Zwilling **nur**, wenn der Zettel ankam
  **und** der Auftrag beantwortet ist.
- **Nichts verloren:** Jeder Zweifel lässt ihn laufen — nie gelesen, Auftrag
  gescheitert, Neustart dazwischen (Register leer). Beide Fälle als eigene
  Prüfzeilen.

Adam sieht den Unterschied: statt *„reiht sich hinten ein"* jetzt *„ich reiche
es dem laufenden Vorgang gleich hinein, ohne ihn zu stoppen"*.

## Der Prüfer für die Klasse — gebaut wie vorgeschlagen

`test_zimmer_block1.py`, Zeile **„jede Ein-Argument-Tuer ist als Hauptfaden
BEGRUENDET"**: zählt per `ast` **echte Aufrufknoten** von `_sess`, `_mb_opt`,
`_get_mailbox`, `_ensure_worker`, `close_session`, `ensure_session`,
`make_permission_callback` mit ≤1 Argument und verlangt `# Hauptfaden:` im
Umfeld. Dazu eine Gegenrichtungs-Zeile, damit er nicht über einer leeren Menge
grün wird.

**Gegenprobe gefahren** (`__pycache__` gelöscht, Eingriff per `assert`
verifiziert, erwartete Zeile vorher notiert): Rückruf und Reconcile entkernt →
**vier** Zeilen rot, darunter die Mengen-Zeile mit **beiden** Fundstellen
(`_sess:3478, _get_mailbox:9782`). Der Stall-Prüfer hat Fall 5 dazubekommen —
hängendes Zimmer 7 wird in seinem Faden geweckt, die Hauptfaden-Sitzung bleibt
unberührt; seine Attrappe sammelt jetzt den **Faden** statt nur der Person.

**Eine Grenze des Prüfers, benannt:** Er sieht nur Aufrufe mit **einem**
Argument. `_handle_stalled_session(user_id, mb, sess, stalled_for)` hatte vier
und wäre ihm entgangen — deshalb ist `thread_id` dort **pflichtig** statt
vorbelegt. Wo ein Vorgabewert das alte Verhalten weiterlaufen lässt, ist er die
eigentliche Lücke.

## Berichtigung zu meinem Deploy-Bericht

Du hast recht: **„Das SDK schluckt die leere Hook-Antwort" war nicht
gemessen.** Der Hook schreibt auf dem leeren Pfad keine Zeile, und eine
Hook-Ausnahme protokolliert das SDK nicht — ein leeres Fehlerprotokoll beweist
nichts. Deine Prüfzeile steht im Laufplan und gehört in den Deploy-Block von
1b: Nachricht **während** eines laufenden Werkzeuglaufs, dann muss
`Nachsteuern: N Zeichen an den laufenden Auftrag gereicht (Zimmer haupt)` im
Protokoll stehen. **Das Risiko bleibt bis dahin offen.**

Ebenso berichtigt und gepusht (`2206efe`): kein `git revert` im VPS-Klon, der
Grundsatz steht jetzt als eigener Absatz in `docs/befehlsbloecke-adam.md`.

## Was ich NICHT gebaut habe

**Verhaltenszeilen für die Rücklagen in `_run_job`.** Sie bräuchten einen
SDK-Client-Doppelgänger; die Mengen-Zeile deckt die Klasse ab, weil sie die
**Abwesenheit** des Arguments misst. Wenn du das anders siehst, sag es — dann
baue ich den Doppelgänger.
