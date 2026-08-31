<!-- ROLLE: befund-entkernung -->
**Stichtag:** 2026-08-25 · **ueberholt durch:** — · **massgeblich ist die Status-Zeile in `MIGRATION.md`**

# Befund — Prüfer-Entkernung: 61 von 116 Prüfzeilen bemerken ihren Schutzverlust nicht

**An:** Mick (Bau) · zur Kenntnis: Adam
**Von:** Engywuck (Kontrolle) · **Stand:** HEAD `1817c86` (24.08.2026, 01:33)
**Vollkatalog:** `entkernung-katalog.md` (liegt daneben — alle 116 Messungen mit
Behauptung, Eingriff, Ergebnis, wörtlich)

---

## Was gemessen wurde, und wie ehrlich die Zahl ist

56 getrennte Sitzungen haben je Prüfzeile den **bewachten Schutz entfernt oder
verfälscht** und den Prüfer danach **ausgeführt** — die Gegenprobe „Schutz raus,
rot sehen", die die Projektregel seit dem 22.08. für jeden *neuen* Prüfer
verlangt, hier rückwirkend über den Bestand. Alle Eingriffe in Arbeitskopien
unter `/tmp/entkern-*`; das Repo wurde nur gelesen, `git status` ist leer
(selbst nachgemessen).

**Ergebnis: 116 Prüfzeilen gemessen · 57 blieben grün, obwohl ihr Schutz weg
war · 4 schlagen falsch an (Fehlalarm-Bauart) · 16 zu eng · 39 in Ordnung.**

Drei Ehrlichkeits-Vermerke, bevor die Zahl wandert:

1. **116 ist nicht der Bestand.** Einige Dateien wurden vollständig
   durchgemessen, andere als Stichprobe nach Verdacht (z. B.
   `test_eingangsschranken.py`: 4 von 60 Zeilen). Die Quote 61/116 gilt für die
   gemessene Menge, nicht für „alle Prüfer des Projekts".
2. **Gruppe 6 trägt keinen zweiten Nachweis.** Der Nachweis-Agent dieser Gruppe
   und die Synthese fielen dem Kontingent-Limit zum Opfer (diese Synthese habe
   ich nachgeholt). Vor einem Fix an Gruppe-6-Befunden: kurz selbst nachmessen.
3. **Geisterbefund-Falle, selbst gemessen:** Wer Prüfer durch Patchen misst und
   `__pycache__` nicht vor jedem Lauf löscht, bekommt das Ergebnis des
   *vorherigen* Eingriffs serviert (mtime-Sekunde + Größe zufällig gleich).
   Alle Katalog-Messungen liefen mit Cache-Löschung; jede Nacharbeit muss das
   auch.

## Die fünf Krankheiten (Mengen, nicht Einzelfälle)

**K1 — Die Prüfzeile liest Quelltext.** Kommentar zählt als Vorhandensein
(auskommentierter Wächter-Start bleibt „✓", `_NO_ALWAYS_TOOLS`-Zählschwelle wird
von drei Kommentarzeilen erfüllt); historische Zeichenkette statt Eigenschaft
(neu getippte Sekundenangabe passiert „keine Sekunden"); Formatzwang
(`min(30.0` als Pflicht-Schreibweise). Die größte Klasse — die bekannte Regel
„jede lesende Prüfzeile ist umgehbar", jetzt am Bestand quantifiziert.

**K2 — Der Prüfer misst eine Nachbildung seiner selbst.** `test_queue_order`
baut eine eigene deque und ruft selbst `append`/`appendleft`; `test_stall` ruft
den Wächter selbst auf und misst nie, ob ihn jemand startet;
`test_session_limit_h2:134` ruft die Rücklage selbst auf. Diese Prüfer messen
Python-Semantik, nicht bot.py.

**K3 — Mengen-Schwelle über die Datei statt Zuordnung je Pfad.** „≥2
Fabrik-Aufrufe" bleibt erfüllt, wenn ausgerechnet der Mail-Pfad die Fabrik
umgeht (3 Aufrufe → 2). Die Schwelle zählt, sie ordnet nicht zu.

**K4 — Die Menge hat keine Untergrenze.** `festpfade_differenz` →
`festpfade_pruefung_alt` umbenannt: verlässt die `_differenz`-Menge, die
gemeldete Zahl schrumpft still von 4 auf 3, alles grün. **Dieselbe Krankheit
wie dein Encoder-Achsen-Befund vom selben Tag:** „Ein Prüfraum, der still
schrumpft, sieht aus wie ein Prüfer, der nichts findet."

**K5 — Verbots-Wortlisten.** „kein Netzabruf" kennt `http.client` nicht; „kein
Modell-Aufruf" kennt den Umweg über das eigene bot-Modul nicht. Eine Wortliste
für Verbotenes ist konstruktiv unvollständig — Abwesenheit misst man über
Verhalten oder echte `ast.Call`-Knoten, nicht über Schreibweisen.

## Rang A — die acht sicherheitstragenden Stellen (EIN Block, ~2 h)

Kriterium: der bewachte Schutz ist selbst sicherheits- oder verlusttragend, und
sein Ausfall sähe wie Ruhe aus. Nur diese acht werden jetzt repariert:

| # | Prüfzeile | Was der blinde Prüfer decken würde |
|---|---|---|
| 1 | bot.py:7284 „Boten-Postfach (B)" | `.env`/Token-Datei geht **hinaus**, Schranke nur noch Warnung — Ausfuhr-Richtung des Grundsatzes „nach außen keine sensiblen Daten" |
| 2 | bot.py:7210 „Reibungslose Recherche (5.25)" | WebSearch/WebFetch pauschal dauerfreigebbar — die 💰-Kostenschranke |
| 3 | bot.py:7059 „Zustellnachweis" | `delivered = True` hart — stiller Nachrichtenverlust (der 19.07. zurück) |
| 4 | bot.py:7311 + 7079 „Wächter werden gestartet" | auskommentierter `create_task` für stall_watchdog/zustell_worker bleibt „✓" — toter Wächter, der Zustand vom 23.06. |
| 5 | bot.py:7604 „Medien-Eingangsschutz (5.2)" | `_media_eingang` auf `return None` gekürzt — das Fenster vom 25.07. wieder offen |
| 6 | test_session_limit_h2.py:134/180 | Nachrichtenverlust beim Limit / A1-Rücklage — misst sich selbst statt bot.py |
| 7 | test_start_waechter_b1.py:167 | im `--detach`-Betrieb meldet der Wächter „sauber hochgekommen" über einem toten Bot |
| 8 | test_kalender_caldav.py:178 | hartkodiertes App-Passwort passiert die Geheimnis-Suche |

**`[ERLEDIGT 2026-08-29, nachgetragen 2026-08-31]` Rang A vollständig — alle
acht.** Die Reparatur lief im Nachtpaket vom 29.08.; **der Vermerk hier fehlte,
und das hat Folgen gehabt.** Am 31.08. um kurz nach drei stand dieser Block als
*substanziellste offene Arbeit im Projekt* in einem Nachtauftrag — gemessen war
er da seit zwei Tagen erledigt. Fundstellen, jede mit Reparatur-Vermerk im Code:

| # | Wo die Reparatur steht |
|---|---|
| 1 | `bot.py:6739` (herausgezogene Funktion) + `bot.py:8092` (ausgeführt statt gelesen) |
| 2 | `bot.py:2285` + `bot.py:7960` (ausgeführt statt gezählt) |
| 3 | `bot.py:7783` (der Name genügt nicht) |
| 4 | `bot.py:8145` (über den Syntaxbaum, nicht über den Text) |
| 5 | `bot.py` `_c_medien_eingang` (Verhalten **und** echte Aufrufknoten) |
| 6 | `bot.py:944` + `scripts/test_session_limit_h2.py:102/126` |
| 7 | `scripts/start_waechter.py:54` + `scripts/test_start_waechter_b1.py:178` |
| 8 | `scripts/test_kalender_caldav.py:93` (samt Gegenprobe, dass die Suche *finden kann*) |

**Die Lehre ist die des Katalogs selbst, eine Ebene höher:** Ein Prüfer, der
grün meldet, ohne gemessen zu haben, und eine Ablage, die offen meldet, ohne
nachgesehen zu haben, sind derselbe Fehler. Der zweite kostet keine Sicherheit,
aber Arbeitszeit — und Vertrauen in jede andere Zeile derselben Ablage.

**Bauform je Fix — die zwei tragfähigen Formen, keine dritte:** Verhalten
ausführen (nötigenfalls die Entscheidung in eine eigene Funktion ziehen, damit
ein Prüfer sie erreicht), oder Abwesenheit über echte `ast.Call`-Knoten samt
**Wert** des Arguments, nicht nur Namen. **Je Fix die Entkernungs-Gegenprobe
fahren** — Schutz raus, rot sehen, Schutz rein, `__pycache__` vorher löschen —
und `bash scripts/regressionstest.sh` vor jedem Commit. Jede Stelle einzeln
committen.

## Rang B — die vier Fehlalarme (klein, aber abschaltgefährdend)

Ein Prüfer, der falsch anschlägt, wird binnen einer Woche abgeschaltet — darum
vor dem Rest: **(a)** `test_eingangsschranken` „Alltag ohne Dialog" misst den
**Ordnernamen** mit — in jedem R4-Klon (`git worktree add ../probe-…`) rot;
Prüfer und R4-Regel widersprechen einander. **(b)** `test_wecker_a3:157`
verlangt die Schreibweise `min(30.0` — eine benannte Konstante macht ihn rot
bei intaktem Schutz. **(c)** `test_update_textbefehl:264` (Katalog). **(d)** der
Geisterbefund-Mechanismus als Auflage in die Prüf-Doku.

**`[ERLEDIGT 2026-08-29]` Rang B vollständig.** (a) und (b) waren am 28.08. geschlossen. **(c) hat sich mitgeschlossen**, ohne dass es jemand einzeln reparieren musste: Die abgeleiteten Repo-Marken aus (a) — `_REPO_MARKEN` folgt `__file__` statt einer festen Zeichenkette — decken denselben Fall. **Gemessen statt behauptet:** `test_update_textbefehl.py` läuft im Klon `probe-sdk`, der nachweislich anders heißt, vollständig grün. (d) steht jetzt als **Auflage** in `CLAUDE.md` beim Abschnitt über Verhaltens-Prüfer — mit allen drei Handgriffen (`__pycache__` löschen · Eingriff verifizieren · erwartete Zeile vorher hinschreiben) und je einem Beleg, warum jeder einzelne nötig ist. **Alle drei Fehler sehen wie ein Ergebnis aus** — deshalb Auflage, nicht Empfehlung.

## Rang C — alles Übrige in die F-Liste

Die verbleibenden ~45 Funde (nicht sicherheitstragende K1/K2-Fälle, die 16
„zu eng") gehen **als Katalogverweis in die F-Liste** — repariert wird dort
nur, was ohnehin angefasst wird, dann in der tragfähigen Bauform.
**Ausdrücklich kein Meta-Prüfer, der Prüfer prüft** (Kurs-Regel: keine Wächter
dritter Ordnung). Der Ersatz ist billiger und existiert schon als Regel: die
Entkernungs-Gegenprobe je neuem und je angefasstem Prüfer.

**Konvergenz-Bremse:** Dieser Katalog ist die Gegenprüfung des
Prüfer-Bestands. Nach deinem Rang-A/B-Fix folgt **eine** Nachprüfung
(Entkernung nur der acht reparierten Stellen), dann ist Schluss — was die noch
findet und nicht scharf-blockierend ist, geht in die F-Liste, keine dritte
Runde.

## Einordnung und Reihenfolge

**Der Bot ist heute nicht kaputter als gestern.** Alle Eingriffe geschahen in
Wegwerf-Kopien; gemessen wurde, was die Prüfer **bemerken würden**, nicht was
im Code fehlt. Kaputt ist die zweite Verteidigungslinie: 61 Zeilen, die einen
künftigen stillen Bruch decken würden. Und 39 Zeilen haben die Entkernung
bestanden — darunter die Freigabe-Prüfer (9.4), der Sendepfad-Rauchtest und
die Updater-Härtung; auch das ist ein Messergebnis, kein Zufall.

**Die Reihenfolge bleibt:** zuerst der laufende Auftrag Erkennungsseite
(Rang 0.5 + Rang 1 aus `bauauftrag-erkennungsseite.md`) — dort ist heute
tatsächlich etwas kaputt. Danach Rang A als eigener Block, dann Rang B.
Adam entscheidet, ob und wann die Blöcke laufen.
