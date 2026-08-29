# NACHTPAKET FÜR MICK — geprüft und freigegeben, Adam schläft

**Von:** Engywuck · **Stand:** 29.08.2026, 01:20 MESZ
**ERSETZT vollständig:** meinen Nachtrag von 00:38 (`NACHTRAG-RANG-3B-NEU.md`)
— der baute auf der 20:50-Fassung auf, die Claudia selbst überholt hat.
**Grundlage:** `2026-08-29_bauauftrag-bash-freigaben-weniger-druecke.md` (Adams
Daumen-Abnahme 00:42) · `2026-08-29_bauauftrag-offene-updates-einspielen.md`
· Gespräch bis 01:03 gelesen.

**Reihenfolge heute Nacht: ① Bash-Positivliste → ② Updates → ③ Rang A Rest.**
Alles entschieden, nichts wartet auf Adam. Regressionslauf vor jedem Commit,
jeder Punkt einzeln, was nicht grün wird, wird zurückgerollt.

---

## ① BASH-POSITIVLISTE (Adams Vorrang) — freigegeben, mit vier Entscheiden und drei Auflagen

**Claudias Fassung von 00:45 ist die richtige Bauform** — Positivliste über die
**zerlegte** Zeile, unbekannte Form wird abgewiesen, Bereiche mit aufgelösten
Pfaden. Das erfüllt K5 und beide tragfähigen Prüfformen. Adam hat das Konzept
mit drei Daumen abgenommen (00:42).

### Ihre vier Fragen, entschieden:

1. **`sed` und Postfach-Schreiben bleiben drin.** Das Postfach ist kein freier
   Ausfuhrweg: Die Wache sitzt am **Versand** — Ziel-Allowlist, Geheimnisprüfung
   in `_postfach_send_one` (seit deiner Rang-A-Stelle 1 **ausführend** geprüft),
   Drossel je Absender. Schreiben legt nur vor, der Versand entscheidet.
2. **`cp`/`mv` innerhalb der Bereiche: ja** — mit der Auftrag-4-Mechanik
   (Quelle **und** Ziel im Bereich, nach Auflösung). Workspace ist über den
   Kurier rückholbar, Postfach fängt der Versandpfad.
3. **Log-Ordner als vierter Bereich: ja, nur lesen.** Miss beim Bau, wo sie auf
   dem VPS tatsächlich liegen; liegen sie im Repo, ist der Bereich redundant
   und schadet nicht.
4. **50 Dialoge/Woche als Maß: ja** — als benannte Größe, nicht hart im Code.

### Drei Auflagen von mir:

**A — `~/.claude/memory` bleibt LESBAR.** Claudias Sperre auf `.claude` samt
Unterordnern ist richtig für `projects/` (die Sitzungsprotokolle führen jeden
vollständigen Befehl — gerade weil sie jetzt Messquelle sind, gehören sie zu)
und für die Einstellungen. Aber sie widerspräche für `memory` der gemessenen
8.7-Zusage (G vom 23.08.: `_is_sensitive_ref(schreibend=False)` lässt den
Gedächtnis-Ordner lesend frei — der System-Prompt sagt das zu). **Also:
`.claude` zu, Ausnahme `memory` nur lesend.** Sonst bauen wir einen Widerspruch
zwischen Prompt-Zusage und Schranke — und der Bot dialogt an einer Stelle, die
ihm zugesagt ist.

**B — Je Prüfzeile der neuen Zerlegung die Entkernungs-Gegenprobe:** Schutz
raus, rot sehen, Schutz rein, `__pycache__` vorher löschen. Besonders für jede
Verkettungsform aus Auftrag 4 einzeln und den Symlink-Fall. Das ist die
Prüferklasse, bei der 61 von 116 blind waren — nicht wieder.

**C — Der Umlaut-Prüfer fällt NICHT still weg.** Er stand in der überholten
20:50-Fassung (`postfach_legen.py`), Adam hat ihn **viermal** verlangt (28.07.,
26.08., 27.08., 28.08. 20:45). Die neue Fassung ersetzt das Programm — dann
wandert der Prüfer an den **Versandpfad**: vor dem Versand prüfen, bei Fund
in den failed-Ordner mit sichtbarer Meldung statt still zustellen. Wortliste
der vorgekommenen Fälle wie von Claudia entworfen — zulässig trotz K5, weil
die Lücke hier **laut** ist (Adam meldet den neuen Fall, die Liste wächst),
nicht still wie bei einer Sicherheitsschranke. Kleiner, eigener Commit.

### Und ein Entscheid, der ausdrücklich dokumentiert gehört (Karteileichen-Regel):

**Der Sitzungs-Schalter aus Rang 3b wird NICHT gebaut.** Adams „Button hat
Vorrang!!!" von 00:13 ist durch seine Abnahme der Ausgangs-Wache um 00:42
überholt — die verbleibenden ~40 Dialoge je Woche sind genau die heiklen
(Netz, Betrieb, Löschen, Skriptausführung), und ein Auto-Fenster darüber wäre
die gefährlichste Form des Schalters. Das ist **entschieden, nicht vergessen**.
Trag den Überholt-Vermerk in `2026-08-26_bauauftrag-bash-sitzungsfreigabe.md` ein.

**Und Adams Nachtrag von 01:2x macht die Messung zur Bringschuld statt zur
Rückfallebene** — sein Wortlaut: *„Sie werden über kurz oder lang nerven.
Messdaten proaktiv hinzuziehen bitte!"* Deshalb wird Claudias Auftrag 5 um
einen Auswerteschritt erweitert, **jetzt mitgebaut, nicht später**:

- Das Befehlsart-Protokoll (erstes Wort · erlaubt/abgewiesen · Bereich) läuft
  ab dem ersten Tag — steht schon im Auftrag.
- **Neu: Nach sieben Tagen legt ein deterministisches Auswerteskript den
  Befund von selbst vor** (über den Tagescheck oder als Claudia-Vorlage an
  Adam — ohne Modell-Lauf, Kostenregel). Inhalt: Gesamtzahl der Dialoge,
  die Wiederkehrer darunter, und je Wiederkehrer der Vorschlag.
- **Die Stoßrichtung der Vorschläge ist festgelegt, damit sie nicht in die
  falsche Richtung wachsen:** Wiederkehrende gleichartige Dialoge werden
  durch **benannte, geprüfte Skripte** ersetzt, die einzeln in die
  Positivliste rücken — nie durch Öffnen einer Klasse. `python3 <beliebig>`
  bleibt dialogpflichtig, ein benanntes `scripts/<zweck>.py` mit fester
  Funktion kann freigegeben werden. So sinken die 40 weiter, ohne dass die
  Grenze fällt, die die ganze Konstruktion trägt.
- Der Sieben-Tage-Takt und die 50er-Schwelle als benannte Größen.

## ② UPDATES (`…offene-updates-einspielen.md`) — freigegeben, Reihenfolge bestätigt

`pymupdf` beiläufig → **SDK 0.2.127→0.2.144 + CLI als ein Block** (Klon neben
dem Repo, eigene venv, voller Regressionslauf dort, Pin nachziehen) → **Node
nur vorbereiten** (Ist-Stand einfrieren, Rückweg aufschreiben, Probelauf im
Klon — Vollzug mit Adam, wie in Rang 9 des Arbeitspakets).

**Claudias Auflage übernehme ich und verschärfe die Reihenfolge: die
SDK-Änderungsnotizen werden VOR dem Bash-Bau gelesen.** Siebzehn Fassungen
berühren wahrscheinlich den Freigabeweg. Zwanzig Minuten Lesen können Stunden
Doppelbau sparen. Ergebnis als eine Notiz: Was davon erledigt der Sprung, was
bleibt bei uns? **Erst dann ①.** Bricht der SDK-Block, gilt: zurückrollen,
mit dem alten Pin weiterarbeiten, ① auf dem alten Stand bauen.

## ③ DANACH: Rang A fortsetzen (Stellen 5–8)

Wie im Arbeitspaket, Bauformen unverändert, je Fix die Gegenprobe.

## Liegt bei MIR zur Prüfung, nichts davon heute Nacht:

Dritter Knopf (geprüft: Variante B, Claudias fünf Auflagen vollständig — kommt
ins nächste Paket) · Zahlen-Sprachausgabe (jetzt mit Messung — gut) ·
Karteileichen-Auftrag · Gegenleser scharfstellen (Adams Hand).

## Liegt bei ADAM, wenn er aufwacht:

Nichts Blockierendes. Zur Kenntnis: die 23 Endlager-Aufträge (Listen-Vorschlag
steht), Node-Vollzugstermin, Gegenleser-Schlüssel.
