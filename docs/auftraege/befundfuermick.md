# BEFUND ULTRACODE — Eingangs-Absicherung 9456f16..d596269

**Von:** Engywuck (Kontrolle) · **An:** Mick (Bau)
**Stand:** 23.08.2026, 02:10 MESZ · Opus 5, xhigh
**Lauf:** `/code-review ultra`, 9 Finder-Agenten, Widerlegungsauftrag

**Gut genug wenn:** Rang 1 + 2 geschlossen, jeder Fix mit Gegenprobe
(Schutz entfernen → Prüfer MUSS rot werden). Rang 4 gehört dazu, sonst
misst nichts von dem Rest. Rang 5 in die F-Liste.

**Vorbemerkung:** Sieben Kernbefunde habe ich selbst am Code nachgemessen,
nicht aus dem Agentenbericht übernommen. Ein Agent meldete die
Vertrauensliste als „gehalten" — das war falsch, er hatte den Kommentar
gelesen statt gemessen. Die Absicherung hält an den Stellen, für die sie
Beispiele im Kommentar hat, und bricht an der Klasse darüber hinaus.

---

## RANG 1 · Fremdinhalt erreicht eine Handlung ohne Daumen

### A) `bot.py:8430` — weitergeleiteter Text speist die Vertrauensliste

Gemessen: `bot.py` enthält **null** Vorkommen von `forward_origin` /
`forward_from`. Der Handler ist `filters.TEXT & ~filters.COMMAND` —
Weiterleitungen gehen ungefiltert durch. `adam_anteil=text` ist dann
Fremdtext.

    _extract_hosts("Details unter shop-boese.tld", fuer_vertrauen=True)
    → {'shop-boese.tld'}

Der nächste `WebFetch` dorthin läuft ohne Rückfrage. Der Kommentar
darüber („`text` ist Adams eigener Wortlaut") ist die falsche Aussage,
nicht der Code.

**Fix:** `update.message.forward_origin is None` als Bedingung für
`adam_anteil`.

### B) `bot.py:3016/3035` — Suchtreffer speisen die Vertrauensliste

`_herkunft_aus_ergebnissen` nimmt `str(block.content)` — also auch die
**Schnipsel-Texte der Trefferseiten** — mit `fuer_vertrauen=True`. Damit
schaltet sich eine fremde Seite den nächsten Abruf selbst frei, indem sie
einen Hostnamen in ihrem Schnipsel nennt. Das ist wörtlich das, was der
eigene Docstring zu verhindern verspricht.

**Fix:** nur die Treffer-URLs selbst vertrauen, nie den Schnipseltext.

### C) `bot.py:4313` — der else-Zweig gibt Fremddokumente an die Hauptsitzung

    else:
        # Fallback für Nicht-PDF (Word, Text etc.) → Agent SDK

`.docx` / `.html` / `.rtf` / endungslos gehen mit **vollem Werkzeugsatz**
durch. `.html` ist der Kanonträger für `display:none`.

Zusätzlich zwei fail-open-Pfade in denselben Zweig:
- ein PDF mit Vorspann vor `%PDF-` → `_ist_direkt_lesbar` False
- ein `open()`-Fehler → `except` → False

Und: jedes Dokument **mit Beschriftung** umgeht den Dialog ganz
(`bot.py:8917`).

**Fix:** else → ehrlich scheitern, nicht ausweichen.

---

## RANG 2 · Bash-Auto-Freigabe umgehbar, kein Dialog

### D) `bot.py:2450` — `..` hebelt die Pfadprüfung aus

Selbst gemessen, alle drei `auto-frei=True`:

    cat <repo>/../../../etc/passwd
    cat <repo>/../notizen/privat.md
    tail -100 <repo>/../../var/log/auth.log

H6 hat die zwei Beispiele aus seinem eigenen Docstring geschlossen und
die Klasse darüber verfehlt. (Gegenprobe: die zwei Docstring-Fälle sind
tatsächlich zu.)

### E) `bot.py:2403` — `$VAR/` macht Pfade unsichtbar

Der Lookbehind `(?<![\w=])` greift nach dem Buchstaben einer Variable
nicht; bares `$` steht nicht in `_SHELL_META_RE`. Selbst gemessen,
`auto-frei=True`:

    cat $X/proc/self/environ claude-telegram-bot/README.md
    cat $HOME/.bash_history claude-telegram-bot/README.md

Ersteres gibt `TELEGRAM_BOT_TOKEN` und das Abo-Token aus.

**Fix für D+E gemeinsam:** `shlex.split` + `Path(..).expanduser().resolve()`
gegen `_REPO_DIR`. Der Schreibzweig 200 Zeilen tiefer (`bot.py:2670`) macht
es bereits richtig — nicht Zeichenketten vergleichen.

### F) `bot.py:2600` — die or-Kette verdeckt das Muster

    file_path or path or pattern or command or url or query

Bei `Glob(pattern=".env*", path="/home/claudebot")` gewinnt `path`,
`_ref` ist harmlos, `sensitive=False` → Geheimnis-Aufzählung ohne Dialog.

**Fix:** alle Felder verbinden, nicht das erste nehmen.

---

## RANG 3 · die Schranke höhlt sich selbst aus

### G) `bot.py:2242` — die Marker treffen das Falsche in **beide** Richtungen

Selbst gemessen, `sensitive=True` für:
- `…/.claude/memory/pending-items.md`
- `<repo>/CLAUDE.md`

Beides steht gegen den 8.7-Entscheid „Lesen ja" und gegen den
System-Prompt (`bot.py:2612`), der dem Agenten sagt, der Ordner sei ohne
Rückfrage lesbar — **DOKU-SPIEGEL gebrochen**.

Gleichzeitig `sensitive=False` für:
- `/proc/self/environ`
- `/home/claudebot/.bash_history`

Genau die Ziele aus Befund E.

**Fix:** Marker auf den Schreibpfad begrenzen; `environ`, `/proc/` und
History in die Leseliste.

### H) `bot.py:2263/2258` — Fehlalarm im Alltag

Selbst gemessen, alle `sensitive=True`:

    def .*_run_job
    logs/*.log*
    python telegram bot set webhook
    wie kann ich in python ein set benutzen
    Was ist neu in Version 2.7?

Der Kommentar zwei Zeilen darüber benennt genau diese Erosion
(„dreimal täglich grundlos").

### I) `bot.py:2656` — `hat_nutzdaten`

Die `#`-Hälfte kostet Dialoge und bringt nichts — Fragmente werden nie an
den Server gesendet. Elf von sechzehn normalen Rechercheadressen fallen in
den Dialog, YouTube und Instagram zu 100 %.

Die **Pfad-Lücke** ist im Kommentar ehrlich eingeräumt — die bleibt, das
ist in Ordnung. Nur das `#` raus.

### J) `adam_anteil` an 1 von 7 Stellen, und nicht persistiert

- Sprache (`8700`) ist Adams eigenes Wort
- `/links` (`8555`) sind seine eigenen Adressen

Beide verlieren jedes Vertrauen. Und `pending.record` (`7733`) trägt das
Feld nicht, die Wiederaufnahme nach Neustart (`7280`) kann es nicht
herstellen: **dieselbe Nachricht verhält sich vor und nach einem Neustart
verschieden.**

---

## RANG 4 · die Prüfer prüfen nicht — hier liegt die Ursache

### K) `scripts/test_eingangsschranken.py` — sechs Zeilen bleiben grün

Gegenproben gefahren, Suite jeweils `exit 0`, obwohl die bewachte Schranke
entfernt war:

| Zeile | Prüfer | wie umgangen |
|---|---|---|
| `:678` | H3-Vertrauensliste | baut den `QueuedJob` selbst, prüft den Vorgabewert — **deshalb ist Befund A durchgekommen** |
| `:450` | Link-Vorschau | `read_text`; ein Kommentar genügt |
| `:433` | Herkunftsvermerk | `getsource` + `"keine "`/`"Anweisung"` |
| `:173` | `bypassPermissions` | Textscan, per `"bypass"+"Permissions"` umgangen; die **Haupt**sitzung hat gar keinen ausführenden Prüfer für `permission_mode` |
| `:277/:319/:549` | „braucht Rückfrage" | `sess.bot = object()` erzwingt Deny; ein „niemand wird je gefragt" bleibt grün |

Das ist die eigene Regel vom 22.08., angewandt aufs eigene Werk: **jede
Prüfzeile, die Quelltext liest, ist umgehbar.**

### L) `USER_PREFS_FILE` ist eine Attrappe

Gemessen: keine Fundstelle in `bot.py`; `bot.py:96` ist fest auf
`Path.home()`. Zwölf Testdateien setzen die Variable und glauben sich
isoliert.

**Folge:** der Regressionslauf beschreibt die **echte** `prefs.json`. In
diesem Container liegt sie vor mir:

    output_channel_id / summary_channel_id / tts_channel_id
      = -1001234567890, "Fremder Kanal"
    plus always_allow für Nutzer 4711

Auf dem VPS heißt das: ein Lauf als `claudebot` lenkt alle Ausgaben in
einen Kanal, den es nicht gibt — **still**.

**Vor dem nächsten Lauf auf dem VPS die dortige `prefs.json` sichern und
ansehen.** Fix: `_PREFS_FILE` aus der Umgebung lesen.

---

## RANG 5 · F-Liste, nicht in dieser Runde

- `ABHAENGIGKEITEN.md:134` sagt „17 Zeilen" — es sind **40** (gemessen)
- `_repo_read_grund` hat keinen Aufrufer und widerspricht dem Tor, das es
  erklären soll
- `_ist_suchwerkzeug` an 1 von 3 Stellen benutzt — Vertrauen und Anzeige
  widersprechen sich
- `presend.py` `_SCHARFE_MUSTER` `rm` trifft 94 von 173 Dateinamen falsch;
  `_RE_CODEBLOCK` übersieht CRLF- und Einzeilen-Blöcke

---

## Reihenfolge

**Erst K und L** (sonst misst nichts von dem Rest), **dann Rang 1**,
**dann Rang 2**, **dann 3**.

**Keine Postfächer vorher.**
