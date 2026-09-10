> **Zweck: WEITERGABE → Engywuck** (Ultracode-Lauf) **+ ANSICHT** (Adam) ·
> **Zu tun:** Engywuck startet `/code-review ultra` auf **`d87dc64`**; Adam
> nichts, außer er will es lesen. **Deploy erst nach dem Ultracode-Lauf** —
> so abgesprochen.

# Block 3 „Empfang" ist gebaut — Commit `d87dc64`

**Stichtag:** 10.09.2026, 11:51 (aus dem Commit abgelesen) · **Vormittagsblock,
11:14 bis 11:51** · **Geprüft gegen:** Claudias Bauauftrag (Aufträge 2 bis 5),
Engywucks Freigabe (Auflagen 1, 2, 5), seine zwei Vorab-Sätze vom Morgen ·
**Nenner:** 4 Aufträge Claudias in diesem Block, 4 gebaut · 3 Auflagen, 3
erfüllt · 2 Vorab-Sätze, beide umgesetzt · 54 Prüfzeilen, 9 Gegenproben
gefahren · Regressionslauf 79/79 · **1 Messung, die hier nicht möglich war.**

## Was gebaut ist

**Die Sekretärin** ist eine werkzeuglose Sitzung neben den Zimmern — kein
Zimmer, kein Arbeiter, keine Warteschlange. Ihre Zusage „blockiert nie" trägt
damit bauartbedingt: Es gibt nichts, worin sie warten könnte. Vier
Sonderfälle entfallen dadurch (sie schläft nicht, sie hängt nicht, sie
überlebt keinen Neustart als offener Auftrag, sie steht nicht im Leitstand).

**Auflage 1 — die vorhandene Fabrik, ein Eintrag.** `werkzeugfreie_optionen`
hat einen Parameter `erlaubt` bekommen, Vorgabe leer; für jeden bestehenden
Aufrufer (PDF, Mail) ändert sich damit nichts. Der Empfang setzt genau einen
Eintrag: **den vollen Namen** `mcp__empfang__zettel_ablegen`. Deine
Begründung stimmt an beiden Enden — mit dem Kurznamen verweigert `dontAsk`
das eigene Werkzeug, mit leerer Liste unter `bypassPermissions` wäre alles
erlaubt. Dazwischen liegt genau ein richtiger Zustand.

**Auflage 2 — typisierter Aufruf.** `zettel_ablegen(zimmer, text)` als
in-Prozess-Server. Das Zimmer wird **vor** dem Einreihen aufgelöst
(`channels.zimmer_aufloesen` als Gegenstück zu `zimmer_name_fuer`, plus die
laufenden Fäden aus dem Leitstand, damit der Empfang ohne angelegte Häuser
prüfbar ist). Schreibweise darf abweichen, Bedeutung nicht; **mehrdeutig heißt
`None`** — ein Auftrag im falschen Haus wäre schlimmer als einer, der
zurückkommt. Die Absage nennt die bekannten Zimmer.

**Dein zweiter Vorab-Satz** ist die Stelle, an der ich sonst zwei Mechanismen
gebaut hätte. `auftrag_einreihen()` ist jetzt **eine** Stelle für beide
Herkünfte — Adams Nachricht und den Zettel des Empfangs. Beide gehen über
`nachsteuer_schreiben` mit Auftragskennung und Register.

**Die Einreihung des Zwillings bleibt Code — und der Riegel dagegen auch.**
Bei einer Zwischenantwort steht Adams Nachricht bereits in der Schlange; ein
Werkzeugaufruf wäre derselbe Auftrag doppelt. Das entscheidet `nur_antworten`
im Empfangs-Eintrag, nicht ein Satz im Systemprompt. Ein Satz wäre eine Bitte.

**Auflage 5 — Signatur 👩‍💼** vor jeder Antwort, nicht doppelt gesetzt.

**Der Knopf** (`/empfang`, Vorgabe **aus**) ist die Sicherheitsleine unter der
eingreifendsten Änderung, die dieser Bot bekommen hat: Sie ändert, *wer*
antwortet. Steht er aus, läuft alles Zeichen für Zeichen wie zuvor. Die Weiche
selbst ist eine eigene Funktion (`geht_an_empfang`), damit ein Prüfer sie
ausführen kann statt sie zu lesen.

**Der Haushalt** (Auftrag 5): Obergrenze **je Person**, Drossel mit Meldung,
Einschlafen nach 30 Minuten Leerlauf — Letzteres im vorhandenen Wächter, nicht
in einem zweiten Zeitgeber.

## Was ich hier NICHT messen konnte, und es ist die zentrale Zeile

**Ob die CLI bei `--tools ""` das Werkzeug im Prozess tatsächlich anbietet.**
Der echte Lauf scheiterte am Mac an der Anmeldung: *„Failed to authenticate:
OAuth session expired and could not be refreshed"*. Die CLI-Hilfe sagt zu
`--tools` ausdrücklich *„from the built-in set"*, und MCP-Werkzeuge kommen
über `--mcp-config` — **das ist gelesen, nicht gemessen**, und steht deshalb
nicht als grüne Zeile im Prüfer.

**Prüfzeile nach dem Deploy, beide Hälften:** `/empfang an`, dann eine
Nachricht, die Arbeit bedeutet. (a) Es kommt eine Antwort mit 👩‍💼 in Sekunden.
(b) Der Auftrag steht danach wirklich im Zimmer — `/zimmer` zeigt ihn. Kommt
(a) ohne (b), ist genau diese Frage die Ursache.

## Zwei Befunde über den Auftrag hinaus

**① Der Zettel unter der Null — latent seit Block 1b, von mir.**
`nachsteuer_schreiben` schrieb `_ZETTEL[int(message_id or 0)]`. Ein Zettel ohne
Telegram-Nummer stünde damit unter der **Null** — und `zettel_erledigt(None)`
liest dieselbe Null. Der nächste Auftrag ohne Telegram-Nummer (Wiederaufnahme
nach Neustart, Empfang, jeder künftige Weg) wäre stillschweigend übersprungen
worden. Aufgeschlagen ist es nie, weil bis heute jeder Zettel von einer echten
Nachricht kam. `QueuedJob.zettel_id` trennt den Registerschlüssel jetzt von der
Telegram-Nummer, `zettel_schluessel()` ist die eine Tür dorthin, und ohne
Kennung wird nichts mehr registriert.

**② Der Log-Repo-Wächter misst Dateinamen — und hat mich zu Recht gestoppt.**
Meine erste Fassung hieß `sekretariat.py`. Die Selbstcheck-Zeile
„Log-Repo-Ampel (5.19)" schlug an und verlangte die Neubewertung des
Conni-Lesezugriffs. Der Treffer war ein Namensgleichklang — gemeint ist der
**Rechnungs**-Strang —, aber der Name war tatsächlich belegt. Ich habe
**umbenannt** (`empfang.py`) und den Wächter nicht angefasst. Das Wort
„BEWERTET" habe ich **nicht** ins Drehbuch geschrieben: Es ist Adams
Entscheidung, welche Inhalte ins Log-Repo dürfen, und wer es setzt, hebt den
Wächter für 5.19 auf.

**Die gefährlichere Richtung bleibt offen:** Dieselbe Namensliste
(`rechnung`, `rechnungen`, `sekretariat`, `buchhaltung`, `invoice`) findet ein
künftiges `rechnungslauf.py` oder `spesen.py` **nicht** — dann gäbe es eine
falsche Entwarnung statt eines falschen Alarms. Das ist die schlechtere
Fehlerrichtung, und es ist eine Aufzählung an der Stelle, an der eine Menge
hingehört. Ich habe es nicht geändert, weil 5.19 nicht mein Block ist.

## Wie geprüft ist

`scripts/test_empfang_block3.py`, **54 Zeilen**, im Regressionslauf. Die
Sicherheitsentscheidung wird an der **fertigen Befehlszeile** gemessen
(`_build_command`), das Werkzeug wird **ausgeführt** — Attrappen nur an den
Rändern (Telegram, der Arbeiter). Die Entscheidungen `geht_an_empfang`,
`darf_starten` und `darf_einschlafen` sind eigens herausgezogen, damit sie
aufrufbar sind statt lesbar.

**Neun Gegenproben, jede mit vorher hingeschriebener Erwartung**, `__pycache__`
gelöscht, jeder Eingriff per `assert` verifiziert: Positivliste leeren ·
Doppelauftrag-Riegel entfernen · Kennung zurück in `message_id` · Weiche
ignoriert den Knopf · Mehrdeutigkeit wird geraten · Zimmer zählt sich selbst
mit · Drossel abgeschaltet · offene Freigabe schützt nicht mehr · arbeitendes
Zimmer schläft ein. **Alle neun rot, danach wieder grün.**

Beim Bauen fiel dadurch die **Selbstzähl-Falle** auf: Ein Zimmer, das sich in
`arbeitende_zimmer` selbst mitzählt, drosselt sich bei Grenze eins sofort aus.
In der Worker-Schleife hätte das keine Prüfzeile erreicht.

## Was offen bleibt

- **Die Parallel-Probe** (Claudias Auftrag 5): wie viele gleichzeitige
  Anfragen das Abo trägt. Braucht den laufenden Server. Bis dahin steht
  `ZIMMER_GLEICHZEITIG=3` als **Startwert, nicht als Messergebnis**.
- **Der echte Werkzeuglauf** (siehe oben) — die eine Zeile, die dieser Bau
  nicht selbst beweisen kann.
