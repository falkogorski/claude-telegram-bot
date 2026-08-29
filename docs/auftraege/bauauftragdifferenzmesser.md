# BAUAUFTRAG — Der Differenzmesser (Bezugs-Integrität)

**Von:** Engywuck (Kontrolle) · **An:** Mick (Bau) · **Stand:** 23.08.2026
**Grundlage:** Studie mit 15 Agenten — 5 Bestandsmessungen, 3 konkurrierende
Entwürfe, 6 Widerlegungen, 1 Synthese. Bestand: **84 Posten, 52 stilllegend
oder sicherheitsrelevant, 45 Verstöße gegen die Mengen-Regel.**
**Alle Zahlen unten habe ich selbst am Code nachgemessen.**

---

## REIHENFOLGE ZUM LAUFENDEN AUFTRAG

**Dieser Auftrag kommt NACH Rang 1 und 2 der Eingangs-Absicherung.**
Nicht parallel. Zwei Aufträge gleichzeitig heißt beide halb.

**Gut genug wenn:** Schritt 0, 1 und 2 stehen, jeder mit gefahrener Gegenprobe
(Schutz entfernen → Prüfer MUSS rot werden). Danach ist Schluss. Schritt 3–5
gehen in den Backlog und werden am 25.08. gegen Einkommensarbeit abgewogen —
nicht angehängt, weil sie gerade danebenliegen.

**Aufwand:** anderthalb Blöcke für 0+1+2. Nicht mehr.

---

## DIE DIAGNOSE IN EINEM SATZ

Die Ablage ist eine **zweite, handgepflegte Kopie von Tatsachen, die im Code
schon stehen** — und jede handgepflegte Kopie driftet. Deshalb hilft nicht
„besser pflegen", sondern **weniger Kopien**: ableiten, was ableitbar ist.

Adams Mengen-Regel ist dabei nicht eine Verbesserung, sondern die
**Hauptdiagnose**: 45 der 84 Befunde sind Aufzählungen, wo eine Menge hingehört.

---

## SCHRITT 0 — Die Falschaussage berichtigen (zuerst, ~20 Minuten)

`CLAUDE.md:883-885` behauptet, die Selbstcheck-Zeile „Register-Vollständigkeit"
laufe **„über JEDES eigene Modul und fand deshalb beim ersten Lauf sofort eine
Lücke (`ampel.py`)"**.

Gemessen (`bot.py:7045`):

```python
for modul in ("channels.py", "media.py", "pending.py", "presend.py",
              "reactions.py", "ampel.py", "transcribe.py"):
```

Eine fest verdrahtete Siebenerliste. **`ampel.py` steht darin** — es wurde
gefunden, WEIL es eingetragen war, nicht durch Mengenbildung. Es gibt **17**
eigene Wurzelmodule; der Prüfer erfasst sieben.

**Wichtige Präzisierung, damit niemand den Satz verstärkt weitergibt:** Alle 17
Module stehen heute im Register — durch Disziplin, nicht durch Prüfung. Die
Lücke ist noch nicht aufgeschlagen. **Modul Nummer 18 ist ungeschützt.**

**Warum das zuerst kommt:** Der Satz, mit dem das Projekt seine wichtigste Regel
begründet, ist ihr Gegenbeispiel. Er wird in jedem Auftrag weitergereicht —
**ich habe ihn Adam selbst als Beleg vorgehalten.** Solange er steht, zitiert
die nächste Sitzung eine Aufzählung als Beweis für die Mengen-Regel.

**Im selben Commit:** der Docstring von `_c_register_vollstaendig`, der dieselbe
Behauptung trägt.

---

## SCHRITT 1 — Das Gerüst + Differenzart A (~40 Zeilen)

**Ein Modul, `scripts/differenz.py`.** Kein neuer Wächter, kein Zeitgeber, keine
neue Ablage, kein Modellaufruf, kein Netz, keine Kostenquelle.

### Einhängung

Gerufen vom Selbstcheck in `bot.py`, an der Stelle, an der heute
`_c_register_vollstaendig` steht. Der Selbstcheck läuft an drei Orten:
`bot.py:7207`/`7493` (jeder Bot-Start, also nach jedem Deploy **auf dem VPS**),
`scripts/start_waechter.py:125`, `scripts/regressionstest.sh:104` (und darüber
`daily_check.sh:132` um vier Uhr).

**Das ist der Punkt:** Die Messung läuft in der **Zielumgebung**. Alle drei
Entwürfe wollten am Mac erzeugen und mussten einräumen, weniger zu messen als
sie behaupten — dieselbe Klasse wie der `$HOME`-Fehler vom 29.07.

**Damit ist der Kurs-Regel-Nachweis geführt: ein bestehender Wächter ist
erweiterbar, also wird keiner gebaut.**

### Bauart

Für jedes Paar (Istmenge, Sollmenge) die **Differenz** bilden, bei nicht-leerer
Differenz brechen. **Nie Mitgliedschaft, nie Textsuche nach einem Namen.**

Jede Differenzart ist eine Funktion mit der Namensendung `_differenz`. Das Modul
sammelt sie über den **eigenen Syntaxbaum** ein — es gibt keine Stelle, an der
man eine neue eintragen müsste, und keine, an der man sie vergessen kann.

Jede Art gibt drei Dinge zurück, **alle drei Pflicht**:

1. die Differenzmenge
2. eine **Härte** (bricht / meldet nur) — Pflichtfeld, damit Art Nummer sieben
   nicht stillschweigend auf „folgenlos" fällt
3. eine **Gegenprobe**: ein Aufruf, der die Lücke künstlich erzeugt und rot
   werden lassen muss. **Fehlt sie, weigert sich der Sammler, die Art zu laden.**

Punkt 3 ist die einzige geduldete Prüfung über den Prüfer — und sie ist keine:
eine Ladebedingung, kein Lauf.

### Differenzart A — Wurzelmodule gegen Register

- **Ist:** jede versionierte `*.py` im Wurzelverzeichnis, auf die `test_` nicht
  passt und die nicht `bot.py` ist (`git ls-files`, nicht Endungsmuster — das
  heilt zugleich die Mac/VPS-Divergenz bei gitignorierten Dateien).
- **Soll:** eine **Tabellenzeile** in `ABHAENGIGKEITEN.md`, deren erste Spalte
  den Dateinamen trägt — **nicht** bloße Erwähnung. Der heutige Prüfer misst
  `name not in inhalt`; eine Nennung in einem Warnsatz genügt ihm.

**A findet am Bautag nichts. Das ist kein Mangel, sondern der Normalzustand
eines Riegels** — und genau deshalb ist sie richtig zuerst: Sie beweist den
Mechanismus auf leerer Fläche, ohne dass gleichzeitig repariert werden muss.

**Gegenprobe im Klon, beide Richtungen:**
- eine Registerzeile entfernen → rot sehen
- ein Modul anlegen **ohne** Registerzeile → rot sehen
  ← **das ist die wichtige**; daran wäre einer der drei Entwürfe gebrochen

### Was NICHT gebaut wird, mit Grund

- **Kein pre-commit-Hook, kein `.githooks`, kein `core.hooksPath`.** Gemessen:
  `core.hooksPath` zu setzen **verdrängt `.git/hooks/pre-commit` vollständig** —
  das ist git-Semantik, kein Randfall. Damit wäre Schutzschicht 3 der
  Governance 8.7 lautlos abgeschaltet. Und der Riegel hätte nichts zu tun:
  **0 gelöschte Dateien in 148 Commits** (gemessen).
- **Keine erzeugte, eingecheckte Datei im Repo** — divergiert bauartbedingt
  zwischen Mac und VPS und macht den 4-Uhr-Lauf dauerrot.
- **Kein „Registerzeile ja/nein" als Spalte.** Heute steht dort
  `assert not fehlt` — ein hartes `assert`. Es darf keine Chronik werden.
  Ein Prüfer, der grün wird, wo er rot war, ist ein Rückschritt.

---

## SCHRITT 2 — Differenzart B (der teuerste, und der EINZIGE mit Schaden nach außen)

**Das ist kein Innenwert. Prüfläufe schreiben heute in Adams echte Ablagen.**

Selbst gemessen: der Produktivcode liest **28** Zustands-Schlüssel, der
Regressionslauf leitet **sechs** um (`POSTFACH_DIR`, `FREIGABE_DIR`, `HORA_DIR`,
`BLUMEN_DIR`, `AUFTRAGSBUCH_DIR`, `PENDING_DIR`).

**Nicht umgeleitet — nach Schwere geordnet:**

| Schlüssel | was dranhängt |
|---|---|
| `AMPEL_RULES_PATH`, `AMPEL_CUSTOM_PATH`, `AMPEL_STATE_PATH`, `AMPEL_LOG_PATH` | **die Ampel** — laut CLAUDE.md das Heikelste im Projekt (Klienten-Namen), ausdrücklich cloud-frei zu pflegen |
| `CLAUDE_MEMORY_DIR` | geht in den **System-Prompt jeder künftigen Sitzung** |
| `CONVERSATION_LOG_DIR` | Adams echte Gesprächsprotokolle |
| `USER_PREFS_FILE` | die Attrappe — `bot.py:96` liest sie nie, schreibt nach `Path.home()` |
| `ERINNERUNG_DIR`, `LINK_INBOX_DIR`, `UPDATER_STATE_DIR`, `UPLOAD_DIR`, `WACHPOSTEN_DIR`, `WACHPOSTEN_LOGDIR`, `LIMIT_*`, `QUESTIONS_FILE`, `PRESEND_LOG_PATH` | Zustand der Wächter und Ablagen |

Dazu **fest verdrahtete `Path.home()`-Pfade in 16 Produktivmodulen** — die fasst
kein Umgebungsschlüssel.

### Die Ist-Menge wird NICHT über die Endung gebildet

Ausdrücklich **nicht** „Schlüssel mit Endung `_DIR`" — das ist eine Aufzählung
mit Regex-Anstrich und verfehlt `_PREFS_FILE`, `AMPEL_STATE_PATH`,
`LIMIT_STAND_FILE` und alles, was nicht zufällig so heißt.

**Ist:** jeder Zustandspfad, den ein Produktivmodul aus `Path.home()` bildet
**oder** aus einem Umgebungsschlüssel liest.

### Reihenfolge innerhalb von Schritt 2

1. Die nicht umgeleiteten Ordner **einzeln entscheiden** — schreibt das Skript
   wirklich, oder liest es nur?
2. Läufer anpassen, Regressionslauf grün.
3. **Dann** scharfstellen. Regel ①a: gebaut-und-ruhend darf warten,
   gebaut-und-wachend nicht.
4. Die `Path.home()`-Klasse wird **gemeldet, nicht gebrochen** — sonst ist der
   Bot-Start ab Tag eins rot.

### Mit erledigt: die Reparatur der prefs.json

`_PREFS_FILE` (`bot.py:96`) aus der Umgebung lesen lassen. **Danach** die
Testdaten aus der echten Datei auf dem VPS entfernen:

```
"output_channel_title": "Fremder Kanal"
"output_channel_id" / "summary_channel_id" / "tts_channel_id" = -1001234567890
Test-Nutzer "1", "4711", "4712", "4713", "9002"
```

**Erst der Fix, dann das Aufräumen** — sonst schreibt der nächste 4-Uhr-Lauf
alles zurück. Der vollständige Vorzustand steht im Gesprächsprotokoll
`conversations/2026-08-23.md` im Log-Repo; eine gesonderte Sicherung ist
unnötig. Adams eigener Eintrag (`304455165`) ist unbeschädigt und bleibt.

Gemessene Folge, solange es steht: `get_output_channel()`,
`get_summary_channel()` und `get_tts_channel()` lesen alle drei **zuerst**
`output_channel_id` — Ablage, Zusammenfassungen und Sprachausgabe zeigen auf
einen Kanal, den es nicht gibt.

---

## DANN STOPP

**Schritt 3 (Postfach-Schreiber), 4 (Prüfer gegen Läufer) und 5
(Entdeckungsregel) gehen in den Backlog.** Begründung, gemessen:

- Läufer-Vollständigkeit hält heute 37 von 37 — durch Disziplin, ungeprüft.
- Die Postfach-Lücke ist durch `botenpost.ABSENDER` zweitgesichert.
- Die Entdeckungsregel findet 3 von 45 Fällen und erzeugt bei gelockerter
  Schwelle 18 Fehltreffer, die von Hand zu sortieren sind. **Werkzeugbau am
  Werkzeug.**

**Dieser Auftrag hört nach anderthalb Blöcken von selbst auf, statt sich seine
nächste Runde zu verdienen.** Das ist die ehrliche Antwort auf „drehen wir uns
im Kreis": zum Teil ja.

---

## EIGENER BEFUND, EIGENER AUFTRAG — NICHT hier anhängen

`scripts/hora.py:666` fährt

```python
subprocess.run(["bash", "-lc", befehl], cwd=str(REPO), timeout=7200)
```

auf Einträge des **Auftragsbuchs** — und `hora.py` läuft aus `daily_check.sh`.
Damit ist ein zeitgesteuerter Pfad in der Lage, beliebige Shell auszuführen,
und es gibt für `hora.py` **keinen** der Modellfrei-Prüfer, die andere
Betriebsskripte tragen.

**Ich behaupte hier keinen Exploit** — wer ins Auftragsbuch schreiben darf, ist
zu klären, und der Wachposten-Knopf legt dort Befunde ab, die aus **Logs**
stammen. Genau diese Kette berührt den Grundsatz mit Vorrang („von außen kommen
nie Anweisungen"). **Das gehört untersucht, bevor daran gebaut wird**, und es
ist ein eigener Auftrag, kein Anhängsel.

---

## ENTRÜMPELUNG — als Zugehörigkeitsregel, nicht als Liste

**Sofort entfernbar** ist jede Definition, die **alle drei** Bedingungen erfüllt:
kein erreichbarer `ast.Call`-Aufrufer in Produktivcode · keine Nennung in einer
`*.md` · keine Nennung in einem Prüfer.

**Vier Fälle ausdrücklich NICHT löschen:**

| Ort | warum nicht | was stattdessen |
|---|---|---|
| `_kontingent_frisch_messen_alt` (`bot.py:3725`) | `test_eingangsschranken.py:227` nennt sie in einem `not in`-Konstrukt. Löschen schrumpft den Wachposten gegen handgebaute Agent-Optionen **still auf einen Eintrag** — ein Name, den es nicht mehr gibt, wirft dort keinen Fehler | **erst** die Wachliste auf eine Zugehörigkeitsregel umbauen (jede Funktion, die `ClaudeSDKClient` instanziiert und nicht über `werkzeugfreie_optionen` geht), **dann** löschen |
| `_repo_read_grund` (`bot.py:2368`) | Zweitfassung der Freigabelogik, dem Original um zwei Härtungen hinterher. Liefert für `find … -delete` und Fremdpfad-neben-Repo den leeren String = „auto-freigegeben". `ABHAENGIGKEITEN.md:124` führt sie als aktiv. **Wer sie verdrahtet, baut die H6-Lücke wieder ein** | umbauen: sie befragt `_is_repo_read_cmd` und formatiert nur den Grund. Eine Quelle statt zwei |
| `AUSFALL_SCHWELLE` (`scripts/kontingent.py:80`) | einziger Träger der Selbstausfall-Meldung, die der Modulkopf verspricht. Der Kommentar beschreibt Verhalten, das es nicht gibt | verdrahten: Fehlversuche zählen, bei Schwelle **eine** `botenpost.legen` — deterministisch, ohne Modellstart, AGB unberührt |
| `freigaben.unbeantwortet` + `scripts/entscheidungs_protokoll.py` | letzter Schenkel der Leitung, die CLAUDE.md als „die fehlende Leitung" führt. Der Test belegt, dass es funktioniert — nicht, dass es läuft | Auslöser setzen |

**Verfahren, unverhandelbar:** nur nach grünem Regressionslauf · jede Streichung
**einzeln** committet und einzeln testbar · **kein Sammel-Commit „Aufräumen"**.

---

## WAS OFFEN BLEIBT (ohne diese Liste wäre der Auftrag unehrlich)

1. **Falsche Verneinungen.** `CLAUDE.md:1281` und `MIGRATION.md:35` sagen, die
   Eingangs-Absicherung sei nicht gebaut — sie ist es seit dem 22.08. Daraus
   folgt ein bis heute geltendes Tor („bis dahin keine Mail-Konten"), das 9.5
   blockiert. **Dafür wird nichts gebaut** — ein Wächter wäre dritter Ordnung.
   Es gehört als **eine Zeile in den Kurs-Blick am 25.08.**: *Welcher Satz in
   der Ablage sagt, etwas sei nicht gebaut?* — und dann von Hand nachgesehen.
2. **Zahlen in Prosa.** Alle bisher gefundenen Falschaussagen waren Zahlen. Der
   Mechanismus fasst sie nicht. Empfehlung ist keine Automatik, sondern eine
   **einmalige Handstreichung**: die Zusagen der Form „→ N Zeilen" im Register
   **ersatzlos löschen**, nicht korrigieren. Der Prüfbefehl daneben trägt die
   Information; die Zahl trug nie eine. **Was nicht dasteht, kann nicht falsch
   werden.**
3. **Inhaltlich falsche Gültigkeits-Köpfe.** Anwesenheit messbar (8 von 17
   vollständig), Wahrheit nicht.
4. **Prosa ohne Muster** — rund die Hälfte der 611 prüfbaren Behauptungen.
5. **Laufzeit-Kanten** (geerbte Umgebungsvariablen, transitive pip-Pakete,
   Versionsdivergenz). Die Einhängung am Selbstcheck **mildert** das, weil er
   auf dem VPS läuft — sie heilt es nicht.
6. **Semantischer Bruch bei gleichbleibendem Namen** — unsichtbar.
7. **Die übrigen textlesenden Prüfzeilen: 54 von 416.** Dieser Auftrag fasst
   zwei davon an. Der Rest bleibt umgehbar, darunter die beiden einzigen
   Modellfrei-Prüfer der AGB-Leitplanke.
8. **Der Mechanismus prüft sich selbst nicht.** Ob `differenz.py` noch gerufen
   wird, hängt an der Selbstcheck-Zeile, die er ersetzt. Dagegen hilft die
   Gegenprobe beim Bauen — kein Wächter.
