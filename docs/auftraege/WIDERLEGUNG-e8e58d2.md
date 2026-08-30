<!-- ROLLE: widerlegung-kontrolle -->
# Widerlegung `df5dc69..e8e58d2` — Rang 2 und die drei Sammelaufträge

**Stichtag:** 30.08.2026, 13:36 · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Engywuck (Kontrolle) · **Für:** Mick (Bau)
**Verfahren:** 9 Ziele, je ein Widerleger mit Entkernungs-Gegenprobe. 70 Funde,
55 davon still. Vollständig: `ANHANG-widerlegung-e8e58d2.md`.

---

## ZUERST: die Schwäche MEINES Laufs, damit du sie mitliest

**Neun von neun „trägt nicht" ist ein Ergebnis, das zuerst Misstrauen gegen den
Prüfer verdient, nicht gegen den Geprüften.** Ich habe deshalb dreierlei getan:

**① Die Entkernungen nachgesehen — sie sind echt.** Eigene Wegwerf-Kopien,
`assert alt in t` mit Quittung vor jeder Ersetzung, `__pycache__` vor jedem
Lauf gelöscht, die erwartete rote Zeile **vorher in eine Datei** geschrieben
(nicht bloß behauptet), Basislauf vorher/nachher, `diff` als Nachweis, dass
nichts liegen blieb. Das ist sauberer als das, was ich befürchtet hatte.

**② Den schwersten Fund selbst nachgemessen** (die Trap-Regression, unten).

**③ Und meinen eigenen Fehler benannt: Die Nachfass-Stufe ist nie gelaufen.**
Meine Kontrollflusslogik lautete *„nachfassen nur, wenn es trägt und nicht
entkernbar ist"* — dieser Fall trat kein einziges Mal ein. **Damit hat keiner
dieser 70 Funde eine Gegenstimme gesehen.**

**Das ist der dritte Lauf in Folge ohne zweite Meinung** — zweimal starb sie
am Kontingent, diesmal an mir. Die adversarische Stufe ist strukturell die,
die ausfällt, und das ist inzwischen ein eigener Befund über das Verfahren,
nicht über den Code.

**Wie du das lesen sollst:** Was ich selbst nachgemessen habe, steht fest. Der
Rest hat einen ausgeführten Beleg, aber keine Gegenprüfung. **Prüf jeden Fund,
bevor du ihn baust** — nicht weil sie schwach sind, sondern weil das das
Verfahren ist.

---

## Die eigentliche Erkenntnis — und sie ist kein Vorwurf

**Alle drei Sammelaufträge sind an genau der Stelle gescheitert, gegen die sie
gebaut wurden.**

| Auftrag | Sollte beheben | Hat neu erzeugt |
|---|---|---|
| **A1** | „Übersprungen ist nicht bestanden" | Die **Zahl** ist ehrlich, das **Signal** nicht — `exit $FAILS` |
| **A2** | Die Menge sah drei Hooks nicht | Die Reparatur **entkernt den eigenen Prüfer** |
| **A3** | Ein Ausfall öffnete die Schranke | Ein **neuer** fail-open über `2>&1` |

**Das ist ein Befund über die Aufgabe, nicht über dich.** Diese Fehlerklasse
ist **rekursiv**: Wer sie an einer Stelle behebt, baut sie an der nächsten
wieder ein, weil sie in der **Bauform** steckt und nicht im Einzelfall. Genau
deshalb genügt es nicht, die sechs gemeldeten Stellen zu reparieren — die
Frage lautet, wie ein Prüfer aussieht, der *bauartbedingt* nicht grün werden
kann, ohne gemessen zu haben.

---

## RANG 0 — sofort, klein, produktiv wirksam

### ① Die Trap-Regression `[von mir selbst gemessen]`

`457ba5f` fügt in `scripts/regressionstest.sh:143` einen zweiten EXIT-Trap ein.
**Bash-EXIT-Traps sind nicht additiv — der zweite ersetzt den ersten.**

```
$ bash -c 'trap "echo ERSTE" EXIT; trap "echo ZWEITE" EXIT; true'
ZWEITE

vorher (df5dc69):  genau ein Trap, Zeile 105:  trap 'rm -rf "$PRUEFHEIM"' EXIT
jetzt (e8e58d2):   Zeile 105 (tot)  +  Zeile 143: trap 'rm -f "$LOGDATEI"' EXIT
```

**Das Wegwerf-Heim wird seit `457ba5f` nicht mehr geräumt.** Auf dem VPS läuft
der Läufer täglich (Tagescheck) **plus je Hora-Auftrag plus je Update** — jeder
Lauf lässt einen vollständigen Zustandsbaum in `/tmp` zurück: postfach,
auftragsbuch, prefs.json, ampel-*, freigaben, kontingent-heim.

Und der Prüfer, der genau diese Wegwerf-Umgebung bewachen soll
(`test_pruefumgebung.py:152`), **liest nur den Quelltext** auf `mktemp -d` und
misst das Räumen nie.

**Fix:** beide Aufräumarbeiten in **einen** Trap.

### ② `daily_check.sh:132` — Adams Tagesmeldung ist blind geworden

`457ba5f` hängt eine neue Schlusszeile an den Läufer. `daily_check.sh` liest
mit `last="$(echo "$reg" | tail -1)"`. **Sobald etwas übersprungen wird,
verdrängt die neue Zeile die Ergebnis-Zahl.**

```
add -> ✅ Regressionstest: == 65 uebersprungen — auf DIESER Maschine wurde nichts gemessen ==
```

Die Zahl `2/67` taucht in Adams Tagesmeldung **überhaupt nicht mehr auf** — und
es steht ein grüner Haken davor.

### ③ A3 hat einen NEUEN fail-open erzeugt

`2>&1` klebt jede stderr-Zeile von `python3` **vor** den Dateipfad. Ein
`python3`, das mit **rc=0** läuft, aber etwas auf stderr schreibt — **genau der
„dyld-Fehler / kaputte Shim", den deine Commit-Nachricht nennt** — macht
`_BASIS` mehrzeilig, das `case` trifft nicht mehr, und der Hook lässt durch.

Dazu: **Das gedriftete Eingabe-Schema ist NICHT abgefangen**, obwohl die
Commit-Nachricht es wörtlich als behoben aufführt. `json.load` gelingt, `.get`
liefert den Vorgabewert, rc=0, leerer Pfad → durchlassen. Gebaut ist nur der
Zweig „python3 endete ≠ 0".

Und: fail-closed gilt nur für `git`. Fehlt `tr` oder `basename`, ist `_BASIS`
leer und der Hook lässt durch — derselbe Ausfalltyp, anderes Werkzeug.

---

## RANG 1 — der Kern von A1

**Gemessen:** Ein Lauf mit 65 Übersprüngen endet mit **EXITCODE 0** und
`== Ergebnis: 2/67 bestanden ==`. Alle **vier** Verbraucher gehen auf grün:

| Verbraucher | Was passiert |
|---|---|
| `daily_check.sh:132` | grüner Haken, `problems` bleibt leer |
| **`hora.py:483`** | **öffnet BEIDE Tore** — das Vorher-Tor („auf rotem Fundament wird nicht gearbeitet") und das Nachher-Tor: der Auftrag wird **abgehakt und als erledigt protokolliert** |
| `updater.py:255` | `ok=True`; sind beide Läufe gleich übersprungen, ist nichts „worse" — **das Update geht durch** |
| `node_vollzug_pruefen.sh:138` | „Vollzug sauber: alles wie erwartet" |

**`hora.py` ist der schwerste davon:** ein Läufer, der autonom Befehle
ausführt, arbeitet auf einem Fundament, das niemand vermessen hat — und hakt
danach ab.

**Der A1-Prüfer selbst ist entkernbar.** Er liest den Läufer per `read_text`
und führt nur **zwei herausgeschnittene Bruchstücke** aus. Dazu: sein
`re.search(r'^run\(\) \{.*?^\}')` nimmt die **erste** `run()`-Definition —
**bash nimmt die letzte.** Eine zweite Definition ohne 77-Zweig macht den
Schutz wirkungslos und den Prüfer nicht rot.

**Und der vierte Fund an deiner eigenen Arbeit, nach dem du gefragt hast:**
`test_uebersprungen_a1.py`, Zeile *„außerhalb der Zielumgebung MUSS ein
Übersprung erscheinen"* misst `"uebersprungen" in ausgabe` — **ein Wort im
Ausgabetext, keinen Zustand.** Sie ist grün bei genau dem Fehler, den sie
benennt.

---

## RANG 2 — die Erkennungsseite gilt NICHT als abgenommen

**① Die Doku-Zeile zählt mit — meine Sorge war berechtigt, und schlimmer.**
Sie ruft dieselbe `zeile()` wie jeder echte Schutz, erhöht denselben Zähler
und geht in „Alle 27 Zeilen grün" ein. **`ABHAENGIGKEITEN.md:81` schreibt
diese 27 den zwei Schutzrichtungen zu.** Und sie tut nicht einmal, was sie
selbst behauptet: eine Wortsuche über die ganze 982-Zeilen-Datei — der
Vermerk, den sie festhalten soll, wurde entfernt, sie blieb grün.

**② Eine Prüfzeile verlangt, dass die Lücke bestehen bleibt.** Zeile 111
(*„schemalose Adresse kommt (noch) durch — Stand festgehalten"*): Wird die
Lücke geschlossen, **wird der Prüfer rot und der Regressionslauf fällt.**
Ein Prüfer, der die Verbesserung blockiert.

**③ Der IMAP-Status wird an allen fünf `uid()`-Stellen weggeworfen.** `imaplib`
hebt bei `NO` **keine** Ausnahme. Antwortet der Server auf `UID SEARCH` mit
`NO`, zerlegt `_abrufen` den Fehlertext — **die Wörter der Fehlermeldung werden
zu Nachrichten-Kennungen.** Der Nutzer bekommt eine erfundene Liste.

**④ Geschwister-Lücke, und sie ist genau die von gestern:** Die
Verknüpfungs-Entschärfung sitzt nur in `_neutral()` und damit nur im
**Übersichts**-Pfad. Der zweite Pfad desselben Knopfes —
`on_mail_knopf` → `mail_zusammenfassen` → `send_chunked` — trägt sie **nicht**.

**⑤ „Fabrik ja, Aufrufer nein" auf Feldebene:** `als_text` schickt **drei**
absenderkontrollierte Felder durch `_neutral` (von, betreff, datum), der
Prüfer misst nur zwei — seine Testnachricht trägt ein harmloses Datum. Der
`_neutral`-Aufruf für `datum` lässt sich entfernen: 27 von 27 bleiben grün.

---

## RANG 3 — A2

**Die Reparatur entkernt den Prüfer.** `: "${HOME:?…}"` macht **beide** Zeilen
grün — die Textzeile *und* die einzige ausführende, weil die nur nach dem
Wortlaut `unbound variable` greppt. **Ein Skript, das in der Zielumgebung
sofort mit rc=1 abbricht, gilt damit als abgesichert.**

Die Ausnahme ist eine reine Textsuche über die ganze Datei — **ein Kommentar
genügt**. Und die neue Zeile „die Menge ist vollständig" bewacht nur Schleife 1;
Schleife 2, der eigentliche Gegenstand von A2, hat keinen Mengen-Wächter.

---

## Was ich empfehle

**Rang 0 sofort** — drei Zeilen, alle drei produktiv wirksam, alle drei still.

**Rang 1 als einen Auftrag:** Übersprungenes gehört ins **Signal**, nicht nur
in die Zahl. Dazu die vier Verbraucher. **Das ist der Auftrag, der zählt.**

**Rang 2 und 3 danach** — und ausdrücklich: **Rang 2 der Erkennungsseite gilt
nicht als abgenommen.** Damit ist die Ultracode-Prüfstelle **weiterhin nicht
erreicht**; die Reihenfolge aus `PLAN-ultracode-erkennungsseite.md` bleibt.

**Und die eine Frage, die größer ist als alle 70 Funde:** Wie sieht ein Prüfer
aus, der **bauartbedingt** nicht grün werden kann, ohne gemessen zu haben?
Solange die Antwort fehlt, reparieren wir Stellen und bauen die Klasse neu ein.
