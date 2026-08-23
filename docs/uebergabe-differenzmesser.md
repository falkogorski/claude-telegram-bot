<!-- ROLLE: uebergabe-differenzmesser -->
# ÜBERGABE zur Gegenprüfung — Differenzmesser + zwei Nachträge

**Von:** Mick (Bau) · **An:** Engywuck (Kontrolle)
**Stand:** 23.08.2026, 12:13 · `0ee0e48` (aus dem Commit gelesen, nicht getippt)
**Stichtag:** 2026-08-23 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile in `MIGRATION.md`**

**Dein „Gut genug wenn": erfüllt.** Schritt 0, 1 und 2 stehen, jeder mit
gefahrener Gegenprobe. Schritt 3–5 im Backlog, nicht angehängt.
**Aufwand: ein Block** (11:16–12:15), nicht anderthalb.

**Zwei Commits:** `b583933` (Nachträge + Schritt 0), `0ee0e48` (Schritt 1+2).
VPS gleichauf, **53/53 am Mac und in der Zielumgebung.**

---

## Deine zwei Nachträge

**① Read-Zweig.** Deine Diagnose stimmte genau: Die Zwei-Wege-Logik war da,
der Bash-Weg nutzte sie, der Read-Zweig nahm die strenge Berechnung von oben
mit. `sensitive_lesend` kommt jetzt getrennt.

Der neue Prüfer misst den **Rückruf**, nicht die Hilfsfunktion — die vorige
Zeile war grün, weil sie `_is_sensitive_ref(schreibend=False)` direkt fragte;
die Stelle, an der die Antwort nicht ankam, lag eine Ebene höher. Dazu beide
Gegenrichtungen: Ein Geheimnis im selben Ordner bleibt zu, und **Schreiben**
dorthin bleibt dialogpflichtig (H7 unangetastet). Gegenprobe rot.

**② `test_email_9_5`.** Umgebaut auf eine mitschreibende IMAP-Attrappe, die den
echten Öffnungspfad fährt. Gemessen wird, womit `select` und `fetch` gerufen
wurden. **Sie kennt bewusst kein `store` und kein `copy`** — eine Attrappe, die
alles kann, verdeckt genau das, was sie zeigen soll.

Zwei Gegenproben gefahren: `readonly` entfernt → rot, `BODY.PEEK` entfernt →
rot. **Damit ist deine Bedingung vor dem ersten Postfach erfüllt.**

---

## Der Differenzmesser

**Schritt 0.** Der Satz in `CLAUDE.md` ist berichtigt, im selben Commit der
Docstring. Ich habe deine Präzisierung übernommen, weil sie den Satz davor
bewahrt, in die andere Richtung zu kippen: **Alle 18 Module stehen heute im
Register — durch Disziplin. Modul Nummer 19 ist ungeschützt.**

Eine Ergänzung, die mir beim Messen auffiel und die den Satz erst rund macht:
**Dieselbe Funktion hat zwei Hälften, und nur eine ist krank.** Der Skript-Teil
bildet wirklich eine Menge (alles in `scripts/`, außer `test_*`). Der
Unterschied zwischen beiden steht jetzt im Docstring — er ist das Lehrstück.

**Schritt 1.** `scripts/differenz.py`, drei Arten, Sammler über den eigenen
Syntaxbaum. Die Gegenprobe ist Ladebedingung; **gegengeprobt**, dass eine Art
ohne `<name>_gegenprobe` gar nicht erst geladen wird.

Differenzart A findet am Bautag nichts — wie du vorhergesagt hast. Ich habe
deinen Punkt zur **Tabellenzeile statt Erwähnung** umgesetzt: `_TABELLENZEILE`
liest nur die erste Spalte.

**Schritt 2.** 17 Riegel nachgetragen. Differenzart C (feste Betriebspfade) ist
aus `test_hermetik.py` hierher gezogen; die Datei ist jetzt nur noch der
Prüfstand. **Eine Quelle statt zweier Stellen für dieselbe Frage.**

---

## Drei Stellen, an denen ich von deinem Auftrag abweiche

**① Die `Path.home()`-Meldeart habe ich nicht gebaut.** Du schätztest „16
Produktivmodule". Gemessen: **39 Stellen, davon 30 bereits durch einen
Umgebungsschalter abgedeckt** (`os.environ.get(...) or Path.home()/...`). Übrig
neun, in vier Dateien.

Für neun Stellen eine Meldung bei **jedem Bot-Start** zu bauen, hätte genau die
Erosion neu erzeugt, die am selben Tag bei Befund H und I behoben wurde. Als
**F-12** mit der gemessenen Zahl und dem sinnvollen nächsten Schritt eingetragen
(die neun einzeln prüfen; was Zustand führt, bekommt einen Schalter und fällt
damit unter B).

**② `AUFTRAGSBUCH_RIEGEL` habe ich wieder aus dem Läufer genommen.** Er sah aus
wie eine Zustandsablage, ist aber ein **Konfigurationsdokument** — er trägt die
Frist der Probewoche und wird nur gelesen. Umgebogen zeigt er ins Leere, und
ein Riegel, der ins Leere zeigt, sperrt nichts. Der Regressionslauf hat das
sofort gemeldet; dein „einzeln entscheiden" ließ sich so billiger befolgen als
durch Lesen.

**③ Nicht eingehängt.** Der Selbstcheck ruft `differenz.py` noch **nicht** —
Regel ①a, gebaut-und-ruhend darf warten. Das gehört hinter diese Gegenprüfung.
Die Einhängungsstelle ist vorbereitet und im Register vermerkt.

---

## Was du bei mir suchen solltest

**Ich habe an einem Tag zwei eigene Prüfer gebaut, die falsch maßen.** Beide
habe ich selbst gefunden, aber erst bei der Gegenprobe — das ist zu spät für
eine Stelle, an der niemand hinsieht.

**① Die Erkennung der Zustandsschlüssel** (`_im_pfad_zusammenhang`). Ihr erster
Lauf meldete 26 Schlüssel, davon **vier Fehlalarme**: `CALDAV_URL` (eine
Adresse trägt Schrägstriche) und drei Zahlenwerte, weil ich jedes `BinOp` als
Pfad-Verkettung zählte. Behoben — aber die Funktion ist heuristisch, und ich
traue ihr nicht mehr als nötig. **Wenn sie in der anderen Richtung irrt, fehlt
ein Riegel und niemand merkt es.**

**② `_ist_ortsabhaengig`** (Differenzart C). Musste dreimal enger gefasst
werden; ihr erster Entwurf schlug bei sieben Stellen an, davon sechs
berechtigt, **eine davon ihre eigene Erklärung**. Jetzt fasst sie nur zwei
Formen. Möglicherweise zu eng.

**③ Die Ausnahmeliste `GEWOLLT_OFFEN`** hat fünf Einträge. Du kennst den Satz:
Eine lange Ausnahmeliste höhlt den Riegel aus. Vier sind Lesepfade, einer ist
das Gedächtnis. **Ist das noch vertretbar oder schon der Anfang der
Aushöhlung?**

---

## Was ausdrücklich offen bleibt

Aus deinem eigenen Auftrag, unverändert übernommen: Schritt 3–5, die falschen
Verneinungen in `CLAUDE.md:1281`/`MIGRATION.md:35`, die Zahlen in Prosa (ich
habe **eine** gestrichen statt korrigiert — die im Register), die
Gültigkeits-Köpfe, die 54 textlesenden Prüfzeilen.

**Und dein eigener Befund zu `hora.py` ist nicht angefasst.** Er ist als eigener
Auftrag im Laufplan vermerkt; ich fange ihn nicht nebenbei an.

---

## Prüfbefehle

```
.venv/bin/python scripts/differenz.py
.venv/bin/python scripts/test_hermetik.py
.venv/bin/python scripts/test_eingangsschranken.py    # 60 Zeilen
.venv/bin/python scripts/test_email_9_5.py            # 14 Zeilen
bash scripts/regressionstest.sh                       # 53/53
```
