> **Zweck: WEITERGABE → Mick** (Adam: Abschnitt „Deploy" ist deine Hand) ·
> **Zu tun:** Deploy jetzt, dann **Block 1b** (sechs Stellen) vor Block 2.
> **Kern von Block 1: abgenommen. „Vollständig": nein.**

# Nachprüfung Block 1 — Stand `23d01d6`

**Stichtag:** 09.09.2026, 19:07 (`date`, Berlin) · **Gemessen im Klon:**
`test_zimmer_block1.py` 28/28, `test_stall_5_18.py` 10/10,
`test_rechnungen_ablegen.py` 7/7, `test_konzept_pdf.py` 14/14 — alle hier
echt gelaufen (python-telegram-bot 22.8 vorhanden) · Diff `bot.py` 376
Zeilen vollständig gelesen · **Nenner:** Kern (Schlüssel, Warteschlangen,
Arbeiter, Limit je Person, Hook-Mechanik) **trägt** · **6 Stellen**, an denen
der Faden bekannt ist und nicht ankommt · **1 fehlender Schreiber** ·
Deploy heute **verhaltensneutral** und deshalb richtig.

## Was trägt

`faden()`, `_sess()`, `_mb_opt()`, `_get_mailbox()` als eine Tür — sauber.
Worker je Faden, `_run_job` holt die Sitzung seines Zimmers, Stall-Wächter
und Wiederaufnahme iterieren über Fäden, `pause_rest_s()` ist aufrufbar und
die Person-Pause gewinnt. Micks zwei Klon-Funde (Wächter, Reconcile) waren
echte Funde; sein blinder Prüfer ist richtig umgestellt. Der Nachsteuer-Hook
entscheidet nichts, wirft nie, verbraucht Zettel, trennt Zimmer. **Das ist
die Bauform, wie sie sein soll.**

## 🔴 Sechs Stellen, ein Muster: die Tür ist da, aber mit dem alten Schlüssel begangen

Micks Satz *„Ersetzt `SESSIONS.get(user_id)` an allen Stellen — eine Tür
statt vierzig"* ist wahr und ist das Problem: Die Ersetzung war mechanisch,
`_sess(user_id)` ohne zweites Argument **ist der Hauptfaden**. An sechs
Stellen liegt der Faden im Umfeld bereit und wird nicht übergeben:

| # | Stelle | Was passiert in einem Zimmer | Heute (nur Hauptfaden) |
|---|---|---|---|
| 1 | **Freigabe-Rückruf** `make_permission_callback(user_id)` (`:3386`, gebunden `:4404`), innen `_sess(user_id)` | Ohne Hauptfaden-Sitzung: **jedes Werkzeug verweigert** („no active session"). Mit: Dialog landet im Hauptchat, Freigabe hängt an der falschen Sitzung | unverändert |
| 2 | **Stopp-Pfad** `process_user_text` (`:10020`): `_sess(user_id)` neben `_fd_thread` | Stopp-Wort in Zimmer 7 **unterbricht den Hauptfaden**, reiht aber in Zimmer 7 ein | unverändert |
| 3 | **Drei Rücklagen in `_run_job`** (`:2187` Zugang, `:2212` Kontingent, `:2274` Kontext-Überlauf): `_get_mailbox(user_id)` | Auftrag eines Zimmers wandert in die **Hauptfaden-Schlange**; bei `:2274` wird dazu `close_session(user_id)` die **falsche** Sitzung rotiert — die übergelaufene bleibt voll | unverändert |
| 4 | **Wiederaufnahme nach Neustart** (`:9556`): `_get_mailbox(uid)` — obwohl `thread_id=r.get("thread_id")` zwei Zeilen darüber steht | Alle gesicherten Zimmer-Aufträge starten im Hauptfaden | unverändert |
| 5 | **Stall-Neustart** (`:8073`): `_ensure_worker(user_id, sess.thread_id if sess else None)` — der Faden der **Mailbox** (`fd`) liegt beim Aufrufer | Hängt der Aufbau (sess None), wird der Hauptfaden-Worker geweckt, das hängende Zimmer bleibt liegen | unverändert |
| 6 | **Befehle** `/reset`, `/stopp`, `/status`, Tastatur, Neustart: `_sess(user_id)` | wirken immer auf den Hauptfaden, egal wo getippt | unverändert — und **ein Teil davon ist so gewollt** (Modell, Sprache, Auto sind je Person) |

**Dazu der fehlende Schreiber:** `nachsteuer_ordner` wird nur von
`nachsteuer_lesen` benutzt. **Niemand legt Zettel ab.** Der Empfang reiht bei
`busy and not interrupt` wie bisher ein (`:10029`). Der Hook liest einen
Ordner, den nichts füllt — Auftrag 8 ist die Hälfte, die Adam nicht sieht.

**Warum das nicht als „Mick hat schlampig gearbeitet" zu lesen ist:** Die
Prüfzeilen messen die Träger (Schlüssel, Schlangen, Sitzungen) — und die
stimmen. Sie messen nicht die **Wege**, die über die Träger laufen. Das ist
genau die Lücke zwischen „Trennung als Eigenschaft" und „Trennung im Betrieb".

## Block 1b — vor Block 2, ein Klon-Lauf

1. **Rückruf je Faden:** `make_permission_callback(user_id, thread_id)`,
   gebunden in `hauptsitzungs_optionen` mit dem Faden; `on_permission_callback`
   findet die Sitzung **über die `request_id`** (alle Fäden der Person
   durchsuchen) — so kennt der Knopf seinen Faden, ohne dass die
   Callback-Daten wachsen.
2. **Stopp-Pfad:** `_sess(user_id, _fd_thread)`.
3. **Rücklagen:** `_get_mailbox(user_id, job.thread_id)` dreimal;
   `close_session(user_id, job.thread_id)` bei Überlauf.
4. **Wiederaufnahme:** `_get_mailbox(uid, r.get("thread_id"))`.
5. **Stall-Neustart:** `_ensure_worker(fd[0], fd[1])` aus dem Aufrufer.
6. **Befehle:** je Handler **entscheiden und hinschreiben** — Hauptfaden mit
   Grund (`thread_id=None  # je Person: Modellwahl`) oder der Faden der
   Nachricht (`/stopp`, `/reset`, `/status` → das Zimmer, in dem getippt wird).
7. **Zettel-Schreiber:** bei `busy and not interrupt` **zusätzlich** ein Zettel
   nach `nachsteuer_ordner(user_id, _fd_thread)`, mit der **Kennung des
   laufenden Auftrags** im Dateinamen. Der Hook liest nur Zettel des laufenden
   Auftrags; beim Auftragsende werden Reste **gelöscht** (sonst bekommt der
   nächste Auftrag „Adam hat nachgesteuert" aus einem anderen Zusammenhang).
   **Keine Doppelantwort:** Wurde ein Zettel verbraucht, trägt der eingereihte
   Zwilling den Vermerk „bereits nachgereicht" und wird nur beantwortet, wenn
   er noch offen ist — Mick wählt die Bauform, die drei Bedingungen sind fest:
   nichts geht verloren, nichts kommt doppelt, nichts Altes kommt an.

**Der Prüfer für die ganze Klasse — eine Menge, keine Liste:** Eine
Prüfzeile zählt per `ast` jeden Aufruf von `_sess`, `_mb_opt`, `_get_mailbox`,
`_ensure_worker`, `close_session` **mit nur einem Argument** und verlangt an
jeder dieser Stellen den Kommentar `# Hauptfaden:` mit Grund. Dann ist jede
verbleibende Ein-Argument-Stelle eine **Entscheidung**, keine Vergessenheit —
und Stelle Nummer sieben wird beim Bau gefunden, nicht bei mir.

**Gut genug wenn (Block 1b):** Zimmer-Sitzung ohne Hauptfaden-Sitzung
bekommt ihre Freigabe **im eigenen Thema** · Stopp-Wort in Zimmer 7 lässt
Zimmer 8 rechnen (Attrappe zählt `interrupt()`) · Kontingent-Rücklage legt
den Auftrag in **seine** Schlange · nach Neustart liegt ein Zimmer-Auftrag im
Zimmer · ein Zettel während eines Werkzeuglaufs kommt an, ein Rest nach
Auftragsende kommt **nicht** beim nächsten an · die Mengen-Prüfzeile ist grün
und wird rot, wenn ein Argument fehlt.

## Deploy — jetzt, mit Neustart

**Verhaltensneutral heute, gemessen:** Adams Chat ist privat, Häuser gibt es
nicht, `message_thread_id` ist überall `None` → jede der sechs Stellen
landet im Hauptfaden, wie seit dem 14.07. Was der Deploy **bringt:** M-1
(Absender, Sofortmeldung), M-2 (Rechnungsskripte frei), M-3 (Dialog-Messung),
das Kontingent-Ereignis im Log (ohne das bleibt M-7 unmessbar), M-4 (PDF),
E-4 (`_Regeln`), Tagescheck-Wortlaut. **`bot.py` ist geändert → Neustart.**

**Prüfzeilen danach, in dieser Reihenfolge:** Regressionslauf auf dem Server
`74/75 + 1 übersprungen` (Heartbeat-Wache) · eine normale Nachricht mit
Werkzeuglauf antwortet (der Nachsteuer-Hook läuft damit **zum ersten Mal
durch das SDK** — Micks Prüfstand ruft ihn direkt; im `bot.err.log` darf
keine Hook-Fehlerzeile stehen) · `/status` · beim nächsten Limit die Zeile
„Kontingent-Ereignis" im Log.

**Ein Risiko, benannt:** Der Hook liefert `{}`, wenn kein Zettel liegt. Ob
das SDK 0.2.127 eine leere Antwort still schluckt, ist **nur am Prüfstand
gemessen, nicht am laufenden Bot.** Deshalb die zweite Prüfzeile oben — sie
ist der eigentliche Nachweis. Fällt sie, ist der Rückweg `git revert f3d1b58`
(nur der Hook), nicht der ganze Block.

## Bei mir

Nachprüfung Block 1b · Ultracode nach Block 3 · Wochenauswertung 16.09.
