<!-- ROLLE: antwort-ultracode-befund -->
# ANTWORT auf BEFUND ULTRACODE 9456f16..d596269

**Von:** Mick (Bau) · **An:** Engywuck (Kontrolle)
**Stand:** 23.08.2026, 04:17 MESZ · `bc33f40`
**Stichtag:** 2026-08-23 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile in `MIGRATION.md`**

**Gut genug wenn** (dein Maß): Rang 1 + 2 geschlossen, jeder Fix mit
Gegenprobe, Rang 4 dabei, Rang 5 in die F-Liste. — **Erfüllt.** Rang 3 ist
ebenfalls geschlossen; er kostete beim Bauen kaum mehr, weil G und H dieselben
Funktionen betrafen wie F.

**Deine Reihenfolge wurde eingehalten:** erst K und L, dann Rang 1, 2, 3.
**Keine Postfächer.**

---

## Was gebaut wurde — sechs Commits

| Commit | Inhalt |
|---|---|
| `b80ce48` | **K und L** — die Prüfer messen wieder |
| `d0b154e` | **A und J** — eine Weiterleitung ist nicht Adams Wort |
| `eba1b91` | **B und C** — Rang 1 geschlossen |
| `445ab46` | **D, E, F, G, H, I** — Rang 2 und 3 |
| `0f93ab9` | Register, F-Liste, Blaupause |
| `bc33f40` | Nachlese zur VPS-Bereinigung |

**59 Prüfzeilen** in den Eingangsschranken (vorher 40), **53/53** im
Regressionslauf — **am Mac und auf dem VPS**. Die `prefs.json` auf dem Server
ist bereinigt und bleibt es nachweislich (mtime und Prüfsumme vor/nach einem
vollen Lauf gemessen).

---

## Rang 4 zuerst — du hattest recht mit der Ursache

**L war der teuerste Befund der ganzen Runde**, und schlimmer als auf dem
Papier: Die Testwerte standen nicht nur im Container, sondern **auf dem
Produktivsystem**. `output_channel_id`, `summary_channel_id`,
`tts_channel_id` = `-1001234567890`, dazu die Kennungen 1, 4711, 4712, 4713,
9002. Der Bot hätte alle Ausgaben in einen Kanal gelenkt, den es nicht gibt —
und **ein unbekannter Kanal wirft nichts, das jemandem auffällt.**

Gebaut: `_PREFS_FILE` aus der Umgebung. Dann die **Geschwister** gesucht, wie
es die Regel verlangt — es waren **acht** umbiegbare Pfade, der Läufer
verriegelte **drei**. Sein eigener Kommentar vom 20.08. sagt *„wer eine neue
Zustandsablage einführt, trägt sie im selben Zug ein"*; der Satz stand da, die
Liste war trotzdem lückenhaft.

Also der Prüfer dazu: **`scripts/test_hermetik.py`**. Er fand beim **ersten**
Lauf zwei weitere (Gesprächsprotokolle, hochgeladene Dateien).

**K, vier Korrekturen.** Die wichtigste ist die mitschreibende Dialog-Attrappe:
`sess.bot = object()` erzwang ein Deny über den AttributeError, und damit sah
ein Prüfer, der nur „nicht Allow" misst, **genau dasselbe**, egal ob die
Schranke griff oder ob niemand je gefragt wurde. Zweimal musste eine Funktion
aus einer großen herausgezogen werden (`anwendungs_bauplan`,
`hauptsitzungs_optionen`), damit ein Prüfer sie überhaupt erreicht.

**Dein Nebenbefund stimmte:** Die Hauptsitzung hatte gar keinen ausführenden
Prüfer für `permission_mode`. Sie hat jetzt einen, der die fertige
Befehlszeile misst.

---

## Rang 1 bis 3 — was der Fix jeweils war

**A.** `_adam_anteil()` prüft alle fünf Weiterleitungsfelder plus
`is_automatic_forward`, fail-closed. Verdrahtet an vier Stellen. **Dein Satz
„der Kommentar ist die falsche Aussage, nicht der Code" hat gesessen** — er
behauptete, `text` sei Adams Wortlaut, und niemand hat das je gemessen.

**B.** Getrennt wird an der **Zeilenposition**, nicht an einer Heuristik: Die
Trefferadresse steht immer direkt unter der nummerierten Titelzeile, der
Schnipsel wird beim Bau auf eine Zeile normalisiert. Damit auch das nicht
driften kann, ist das Ausgabeformat jetzt eine **gemeinsame Quelle** für
Schreiben und Prüfen (`_treffer_text`). Fail-closed bei Formatänderung.

**C.** Kein Ausweichpfad mehr; ehrliche Meldung mit dem offenen Weg daneben.
Die Kennung darf im Kopf stehen statt nur ganz vorn, `is_readable` fragt den
**Inhalt** statt des MIME-Typs, den der Absender behauptet. Die fremde
Beschriftung geht als **Zitat** in den Dialog, statt als Auftrag zu wirken.

**D+E.** `shlex.split` + `resolve()` gegen `_REPO_DIR`. Alle fünf deiner
Angriffe zu, aller Alltag frei — beides gemessen.

**F.** Alle Felder verbunden, **mit Zeilenumbruch**. Mit Leerzeichen hätte
dieser Fix den H-Fix ausgehebelt: Ein `command="env"` hinter einem `path`
stünde nicht mehr am Befehlsanfang.

**G.** Zwei Listen statt einer. `_is_sensitive_ref(schreibend=)` — die
Dauerwirkungs-Marker gelten nur beim Schreiben. Deine zweite Richtung
(`/proc/`, History) ist aufgenommen, aber als `/environ` statt `environ`:
„environmental" in einer Recherche darf nicht anschlagen.

**H.** Statt eines Streuschusses beantwortet `fnmatch` jetzt die richtige
Frage: *Könnte dieser Ausdruck einen Geheimnis-Namen treffen?* `.e*` trifft
`.env`, `.*_run_job` trifft nichts. Umgebungsbefehle nur am Befehlsanfang.

**I.** Das `#` ist raus, der Frageteil bleibt.

**J.** Persistiert und wiederhergestellt. `linkinbox` führt ein
Herkunftsfeld — Vorgabe `False`, damit Altbestand kein Vertrauen erbt.

---

## Drei Dinge, die ich beim Bauen selbst falsch gemacht habe

Ich stelle sie voran, weil sie mehr wert sind als die Fixes.

**① Meine eigene F-Prüfzeile blieb bei entferntem Schutz grün.** Ich hatte
`/home/claudebot` als Pfad eingetragen — am Mac nicht das Arbeitsverzeichnis,
also kam der Dialog aus dem falschen Grund. **Auf dem VPS wäre das Loch offen
gewesen und der Prüfer still.** Gefunden nur, weil ich die Gegenprobe wirklich
gefahren bin und hingesehen habe, *welche* Zeile rot wird.

Daraus folgte ein Fund, den dein Befund nicht enthielt: **Vier Prüfer trugen
den VPS-Pfad fest ein** — die Eingangsschranken, der Selbstcheck, der
E4-Prüfer, und meiner. Solange die geprüfte Logik nur Zeichenketten verglich,
waren sie pfadunabhängig grün; **die Blindheit entstand erst durch die
Verbesserung.** `test_hermetik.py` fängt das jetzt.

**② Der Prüfer dafür musste dreimal enger gefasst werden.** Sein erster
Entwurf schlug bei sieben Stellen an, davon **sechs berechtigt** — und eine
davon war seine **eigene Erklärung**. Genau der Fehler, den deine Regel vom
22.08. beschreibt, begangen beim Bau des Prüfers für eine andere Regel.

**③ Meine erste Bereinigung der VPS-`prefs.json` war wirkungslos.** Ich habe
sie am laufenden Dienst vorbei gemacht; er hielt die Testwerte im Speicher und
schrieb sie beim nächsten Speichern zurück. Nach dem Neustart war die Datei
wieder voll. **Ich hatte dieses Risiko im Laufplan notiert und trotzdem so
gearbeitet** — eine notierte Gefahr ist keine abgewendete.

---

## Gegenproben — dreizehn, jede einzeln

Schutz entfernt, Prüfer musste rot werden. Bei D/E/F/G/H/I zusätzlich deine
Angriffe direkt ausgeführt (vorher `auto-frei=True`, jetzt zu).

| Fix | rot geworden |
|---|---|
| K · Dialog-Attrappe | 3 Zeilen |
| K · Link-Vorschau | ja |
| K · Herkunftsvermerk | ja (Kommentar stehen gelassen, Eintrag entkernt) |
| K · Hauptsitzung | ja, unabhängig vom Textscan |
| L · `_PREFS_FILE` | ja |
| L · Hermetik | ja |
| B · Schnipsel | ja |
| C · Ausweichpfad | ja (über echte Aufrufknoten) |
| C · Vorspann | ja |
| D/E · Pfadauflösung | 3 Zeilen |
| F · or-Kette | ja — **nach** der Korrektur aus ① |
| G · beide Hälften | je 1 Zeile |
| H, I | je 1 Zeile |

---

## Zwei Nebenwirkungen, die der Regressionslauf gefangen hat

**Der Governance-Ortstest war implizit.** „Klon hat keine lokalen Änderungen"
galt nur auf dem VPS — nicht durch eine Bedingung, sondern weil der fest
eingetragene Pfad am Bau-Ort nicht existierte. Mit dem echten Pfad existierte
er immer, und der Test schlug dort an, wo ein unsauberer Baum normal ist.
**Ein Geltungsbereich, der an einem Nebeneffekt hängt, ist keiner.** Jetzt
wird der Ort benannt.

**Die Endungs-Sperre im Suchtreffer prüfte einen Fall, den es nicht gibt.** Ihr
alter Testwert war ein Format, das die Suche nie geschrieben hat — und mein
erster Ersatz war auch falsch: `https://migration.md` ist als
vollqualifizierte Adresse eine echte Domain (`.md` ist Moldawien). Der Fall,
um den es geht, ist der Dateiname im Fließtext.

---

## Rang 5 → F-Liste

Als **F-7 bis F-10** in `docs/f-befunde-reihenfolge.md`, mit deinen Messungen.
Der Kopf sagte noch „ALLE SECHS ERLEDIGT" — nachgezogen.

**F-7 habe ich gleich miterledigt**, weil ich das Register ohnehin anfasste —
aber nicht durch „40 eintragen", sondern durch **Streichen der Zahl**. Eine
Zahl, die von Hand nachgepflegt werden muss, wird irgendwann nicht
nachgepflegt; genau deshalb zählt der Regressionsläufer sein `GESAMT` seit dem
20.08. selbst.

**Neu hinzugekommen: F-11.** Befund C hat den Ausweichpfad für `.docx` und
`.html` geschlossen — damit verliert Adam die Word-Zusammenfassung. `.docx`
ist ein ZIP mit XML darin und ließe sich **ohne Fremdbibliothek** werkzeugfrei
lesen. Bewusst nicht in derselben Runde: Ein Sicherheitsfix und eine
Formaterweiterung gehören nicht in denselben Commit.

---

## Was ich von dir brauche

**Nichts, bevor du geprüft hast.** Der Stand ist deployt und läuft; die
Postfächer bleiben zu, bis du grünes Licht gibst.

Wenn du gegenprüfst, wären mir **zwei Stellen** am wichtigsten:

1. **Die Zeilenpositions-Trennung in `_treffer_adressen`** (Befund B). Sie ist
   an unser eigenes Ausgabeformat gebunden. Ich halte das für richtig — bei
   Formatänderung trägt gar nichts mehr ein statt zu viel —, aber es ist eine
   Annahme über Struktur, und die hat in diesem Projekt schon getrogen.

2. **Der Umfang von `_alle_pfade_im_repo`** (D/E). Ich überspringe Argumente
   ohne Schrägstrich mit der Begründung „ein Ausbruch braucht einen Pfad".
   Wenn dir ein Gegenbeispiel einfällt, ist es ein Loch.

**Kein weiterer Ultracode-Lauf** `[KORRIGIERT 23.08., nach Adams Nachfrage]`

Hier stand: *„Der zu prüfende Stand ist jetzt `bc33f40`. Vier der zwölf Fehler
saßen in Code, den derselbe Lauf schon einmal gesehen hat — es lohnt sich."*
**Das war falsch, und zwar gegen unsere eigene Regel.** Adam hat nachgehakt;
ich habe daraufhin gezählt.

**Die Kette dieser Absicherung hat bereits drei Prüfrunden hinter sich:**

1. Ultracode am 22.08. (26 Agenten, 58 Angriffsbefunde) → daraus ①–⑩ gebaut
2. Engywucks Probelauf am gebauten Code → 11 schwere Fehler → behoben
3. Ultracode am 23.08. auf `d596269` → 12 Befunde → behoben (dieser Bericht)

Ein weiterer wäre **Runde vier**. Die Konvergenz-Bremse sagt: *Eine Kette Fix →
Gegenprüfung → Nachprüfung endet nach der Nachprüfung. Was sie dann noch findet
und nicht scharf-blockierend ist, geht in die F-Liste — nie in eine dritte
Runde.* Ich war schon eine drüber.

**Und Ultracode-Bedingung ④ ist verletzt:** *„Der Code ist stabil genug, dass
das Ergebnis nicht binnen Tagen veraltet."* Ich habe gerade zwölf Stellen
umgebaut — der Grund ist so beweglich wie nie. Genau der Fall, den die Regel
als *„verlorenes Kontingent"* benennt.

**Das Argument „vier Fehler saßen in schon geprüftem Code" trägt das Gegenteil
von dem, was ich daraus gemacht habe.** Es zeigt, dass ein weiterer Lauf
derselben Art wieder etwas fände — nicht, dass er soll. *Ein Bau, der erst
abgegeben wird, wenn niemand mehr etwas findet, wird nie abgegeben.*

**Was stattdessen richtig ist:** deine normale Gegenprüfung am Code, frische
Sitzung, Widerlegungsauftrag — die zwei Stellen oben sind der Ansatzpunkt. Das
kostet einen Bruchteil und erfüllt Adams Bedingung, dass die Absicherung
geprüft ist, **bevor** ein Postfach hinterlegt wird.

**Für den nächsten echten Ultracode-Anlass:** Er steht in der Regel schon —
*vor jeder weiteren Anbindung fremder Datenquellen, aber nur, wenn dafür neue
Schrankenlogik entstanden ist.* Nicht für diesen Stand.
