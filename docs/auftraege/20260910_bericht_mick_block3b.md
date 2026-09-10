> **Zweck: WEITERGABE → Engywuck** (Nachprüfung) · **Zu tun:** Prüfen auf
> `2171d3b`. **Deploy erst nach A-4** — der liegt schon bei dir (`606ce26`)
> und wirkt live; dieser hier berührt nur den Empfang, und der steht auf aus.

# Block 3b — Commit `2171d3b`

**Stichtag:** 10.09.2026, 14:33 (aus dem Commit abgelesen) · **Nachmittagsblock,
13:10 bis 14:33** · **Nenner:** A-1 (6 Punkte), A-2 (6), A-3 (6), A-5 (1 Klasse
mit 9 Stellen) — **alle gebaut** · 79 Prüfzeilen (von 60) · **14 Gegenproben**
über den Tag · Regressionslauf 80/80.

## Die Reihenfolge war anders als geplant, und der Grund gehört nach vorn

**A-4 und A-5 kamen zuerst**, weil sie ohne den Knopf wirken. Das ist der
Punkt, den ich beim Bau von Block 3 übersehen hatte: Der Empfang hängt am
Schalter, **der Haushalt nicht** — `darf_starten` und `darf_einschlafen`
laufen im Arbeiter und im Wächter, und die Meldungen aus `_run_job` erst
recht. Als der Hotfix Block 3 mitzog, waren sie live.

## A-1 — Nebenläufigkeit und Lebenszyklus

**Ein Schloss je Person**, synchron angelegt (kein `await` zwischen Nachsehen
und Ablegen), um Aufbau, `query` und `receive`. Damit sind die Läufe seriell —
und erst dadurch stimmt `nur_antworten` wieder, das an der Sitzung hängt und
je Lauf gilt.

**Zeitüberlauf und Fehler verwerfen den Client**, nicht nur den Verbraucher.
Deine Diagnose war die wichtigste des Abschnitts: `wait_for` bricht das Lesen
ab, die Oberfläche rechnet weiter, und der nächste Lauf liest ihre Reste als
seine Antwort. **Die Sicherung war selbst der Auslöser.**

**Eine begründete Abweichung von deinem Vorschlag:** Du schreibst „Eintrag
entfernen". Ich verwerfe nur den **Client** und lasse den Eintrag stehen —
wartende Läufe halten bereits eine Referenz auf *dieses* Schloss. Verschwände
der Eintrag, bekäme der nächste ein neues, und die Serialisierung wäre für
genau diesen Moment aufgehoben. Das Ergebnis ist dasselbe: kein toter Client
bleibt liegen.

`connect()` liegt in der Zeitgrenze. `_empfang_protokoll` legt keine Einträge
mehr an (eigener Speicher) — und die **Selbstcheck-Zeile „Empfang wohlgeformt"**
prüft den Zustand, nicht den Quelltext: Jeder Eintrag trägt sein Schloss.

## A-3 — vier Bitten sind jetzt Bedingungen

**Fremdtext reicht nichts weiter.** `empfang_darf_weitergeben(update, text)`
fragt `_adam_anteil` — das gab es seit dem 23.08. und wurde hier nie gefragt.
Als eigene Funktion, damit ein Prüfer sie ausführt: eigenes Wort → darf,
weitergeleitet → darf nicht, keine Nachricht → fail-closed.

**Ein Stopp-Wort geht nie an den Empfang.** Statt die Reihenfolge zu tauschen,
steht die Bedingung in `geht_an_empfang` — dort, wo sie geprüft werden kann.

**Zwei Deckel je Lauf:** `max_turns` und Zettel. Beide Einstellgrößen.

**`setting_sources=[]` und `strict_mcp_config=True`.** An der Befehlszeile
gemessen: `--setting-sources=` und `--strict-mcp-config` stehen darin. Dein
Befund war präzise — `--tools ""` verengt nur den eingebauten Satz.

**Und die Kontingent-Pause:** Der Empfang läuft auf Sonnet, aber aus
demselben Topf. Steht die Pause, fragt er gar nicht erst; erkennt ein Lauf
ein Limit, setzt er die Pause für alle Fäden statt sie einzeln hineinlaufen zu
lassen.

## A-2 — die Wege eines Auftrags ohne Telegram-Nummer

Alle sechs Punkte, plus die Persistenz: Der Zweig kehrte vor `pending.record`
zurück, also verschwand eine Nachricht bei einem Neustart — und der
Voice-Datensatz blieb offen, sodass der nächste Start „nie verstanden"
gemeldet hätte. Gesendet wird über `send_chunked`, nicht `reply_text`.

## A-5 — und eine neunte Stelle, die in keiner Liste stand

Deine acht plus **`send_message` beim Kontext-Rotieren**. Gefunden hat sie die
Mengen-Prüfzeile: Sie zählt echte Aufrufknoten in `_run_job`,
`_notify_job_failed` und `_handle_stalled_session` und verlangt an jedem ein
`thread_id`. Eine Aufzählung hätte die neunte nicht gehabt.

## Was offen bleibt — für 3c

- **A-6** Schalter mit zwei Reichweiten (eine Tür je Zustand).
- **Die zehn blinden Prüfzeilen** aus deinem Abschnitt P, allen voran E1b:
  `# Hauptfaden:` als Kommentar-Konvention ist ein Ausweg aus dem Prüfer.
- **F-22** (`chat_id` in Schlüssel, Zettel-Register, Nachsteuer-Ordner).
- **Dein Punkt zu `presend`:** Die Empfangs-Antwort läuft nicht durch
  `check_and_fix`. Ich habe `send_chunked` genommen (das war der harte Teil —
  über 4096 Zeichen wirft `reply_text`), presend aber **nicht** angeschlossen:
  Seine Befunde beziehen sich auf wartende Nachrichten im Zimmer, und der
  Empfang hat keine Warteschlange. **Ob das trägt, ist deine Frage, nicht
  meine Entscheidung** — ich habe es offen gelassen statt es stillschweigend
  wegzulassen.
- **Nicht gemessen, unverändert offen:** ob die Oberfläche der Sekretärin ihr
  Werkzeug im Betrieb wirklich anbietet. Am Mac ist die Anmeldung abgelaufen.
