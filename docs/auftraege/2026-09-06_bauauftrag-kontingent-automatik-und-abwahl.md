# Bauauftrag: Kontingent-Automatik wiederherstellen + Abwahl-Knopf

**Zustand: gültig, ergänzt am 09.09.2026 um den Nachtrag zur Signatur (`RateLimitEvent`) · Von:** Claudia (VPS-Bot-Sitzung) · **Angelegt:** 06.09.2026, kurz nach Mitternacht · **Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau) · **Freigabe:** Adam hat die Richtung am 06.09. um 00:22 Uhr beauftragt („überleg mal bitte, wie das am besten zu machen ist" + Wunsch Abwahlmöglichkeit)

---

## 1. Der Befund vom 05.09.2026 — die Automatik existiert und griff nicht

**Was Adam erlebt hat:** Um 18:43, 18:55 und 19:10 Uhr kam dreimal die englische Meldung „You've hit your session limit · resets 7:40pm (Europe/Berlin)" als normale Antwort in den Chat. Nach dem Reset um 19:40 Uhr geschah nichts; Adam musste um 19:43 Uhr manuell anstoßen, damit die liegengebliebenen Nachrichten abgearbeitet wurden.

**Was der Bestand eigentlich kann (beides gemessen):**
- **MIGRATION.md 5.31** (verifiziert 25.07.): Eigener Kontingent-Zweig in `_run_job` — Nachricht zurück an den **Kopf** der Warteschlange, `pausiert_bis` aus `parse_reset_zeit()`, Status „offen", deutsche ⏳-Meldung mit Reset-Uhrzeit, Worker wartet in 30-Sekunden-Häppchen und spielt danach alles der Reihe nach nach.
- **Befund A3** (20.08., `docs/befund-a3-wecker-existiert.md`): Genau dieses Verhalten wurde mit `scripts/test_wecker_a3.py` in sechs Prüfungen belegt. „Es gibt keinen Weckruf, weil niemand einschläft."

**Warum es trotzdem nicht griff — die Diagnose:** Der gesamte Mechanismus hängt am **Fehlerzweig**: `bot.py:2064` prüft `is_session_limit(e)` in der `except`-Behandlung von `_run_job`. Am 05.09. kam das Limit aber **nicht als Fehler**, sondern als **reguläre Ergebnis-Antwort** durch den Antwortpfad — der Bot hat sie wie eine inhaltliche Claude-Antwort ausgeliefert (Beleg: Konversationslog 05.09., die Meldung steht dort als normale Claude-Zeile; keine ⏳-Meldung, keine Rückstellung, kein Nachspielen). Installierte CLI: 2.1.209.

**Messauftrag an Mick (vor dem Bau, nicht raten):** In `logs/bot.out.log` vom 05.09. gegen 18:43 Uhr nachsehen, in welcher Form das SDK das Limit geliefert hat — Ergebnistyp, Fehler-Kennzeichen (`is_error`, Result-Subtype o. Ä.), exakter Wortlaut. Die Erkennung wird an dieser gemessenen Signatur festgemacht.

### `[NACHTRAG 09.09.2026 — Engywuck]` Die enge Signatur heißt `RateLimitEvent`

**Die Frage an das Protokoll lautet zuerst: Kam am 05.09. um 18:43 Uhr ein `RateLimitEvent`?** Nicht: wie war der englische Wortlaut.

**Im Quelltext nachgesehen am 09.09.:** Das SDK liefert den Kontingent-Zustand als eigenes Ereignis, und der Bot verarbeitet es bereits an **genau zwei Stellen** — `bot.py:4892` und `bot.py:12829`, beide über den weichen Import in `bot.py:62`. `RateLimitInfo` trägt `status` (`allowed` / `allowed_warning` / `rejected`), `utilization`, `resets_at` und `rate_limit_type`.

**Was das für Auftrag 1 bedeutet:** Kam das Ereignis mit `status = rejected`, hängt die Erkennung daran — an einem typisierten Feld, nicht an Text. Dann entfällt jede Wortfolgen-Prüfung, und mit ihr die Gefahr, dass eine inhaltliche Antwort über Limits verschluckt wird. Der Textweg bleibt allein als Rückfall für den Fall, dass das Ereignis nachweislich **nicht** kam.

**Der Bezug zur Bruchstellen-Tabelle unten:** Die Zeile „Erkennung zu eng (SDK ändert Wortlaut erneut)" verliert damit ihre Schärfe — ein typisiertes Feld überlebt eine Formulierungsänderung. Die Messpflicht nach jedem CLI-Sprung bleibt trotzdem: Ereignistypen können sich ebenfalls ändern, nur seltener und sichtbarer.

## 2. Auftrag 1 — Limit-Erkennung auch im Antwortpfad

Vor der Auslieferung einer Claude-Antwort prüfen, ob sie die Kontingent-Meldung **ist** (nicht bloß enthält). Bei Treffer wird sie **nicht ausgeliefert**; stattdessen läuft derselbe Weg wie im Fehlerzweig: `limit_ruecklage()` (Kopf der Schlange, `pausiert_bis`, Status „offen") + die bestehende deutsche ⏳-Meldung.

**Auflage — enge Signatur, sonst frisst der Filter Inhalte:** Eine Antwort, die über Limits **spricht** oder die Meldung **zitiert** (so eine Antwort ging am 05.09. um 20:16 Uhr legitim raus), muss normal ausgeliefert werden. Die Erkennung stützt sich daher auf das vom SDK gemessene Fehler-Kennzeichen **oder** darauf, dass die Antwort im Wesentlichen **nur** aus der Meldung besteht (Meldungsanfang + Länge), nicht auf bloßes Vorkommen der Wortfolge.

## 3. Auftrag 2 — Abwahlmöglichkeit (Adams Wunsch vom 06.09., 00:22 Uhr)

Vorbild ist die Claude-Code-Oberfläche: Dort erscheint beim Limit ein vorgesetzter Haken „automatisch fortsetzen, sobald das Kontingent zurück ist". Übertragen auf den Bot:

- **Standard bleibt: Automatik AN.** Die ⏳-Meldung sagt künftig ausdrücklich dazu: „Ich mache um HH:MM Uhr automatisch weiter."
- **An der ⏳-Meldung hängt ein Inline-Knopf:** „⏸ Diesmal nicht automatisch weitermachen". Drückt Adam ihn, unterbleibt das automatische Nachspielen **für diese eine Pause**; nach dem Reset kommt stattdessen eine kurze Meldung „Kontingent ist wieder da — weitermachen?" mit Ja-Knopf.
- **Beide Knöpfe müssen registriert wirken** (Frage-mit-Wirkung-Regel): Der Druck muss den Zustand nachweislich ändern; ein Daumen ohne Strecke genügt nicht.
- **Neustart-fest:** Die Abwahl wird persistiert, damit ein Bot-Neustart während der Pause sie nicht vergisst (Zusammenspiel mit dem Startup-Reconcile aus 5.31/A3 prüfen — der holt Status „offen" heute automatisch nach und würde die Abwahl sonst überfahren).

## 4. Auftrag 3 — Die englische Rohmeldung verlässt den Bot nie

Nach Auftrag 1 gegenprüfen, dass es **keinen weiteren Pfad** gibt, auf dem die englische Meldung als Antwort durchläuft (auch nicht bei fehlender Reset-Zeit in der Meldung — dort gilt weiter der ehrliche Satz plus Viertelstunden-Wiederholung).

## 5. Auftrag 4 — Tests und Prüfer

`scripts/test_session_limit_h2.py` erweitern (heute 7 Prüfungen):
1. **Limit als Ergebnis-Antwort** (der Fall vom 05.09.) → Rückstellung, deutsche Meldung, kein Durchreichen.
2. **Gegenprobe:** inhaltliche Antwort, die die Limit-Wortfolge zitiert → wird normal ausgeliefert.
3. **Abwahl-Knopf:** Druck → kein automatisches Nachspielen, stattdessen Nachfrage mit wirksamem Ja-Knopf; ohne Druck → Automatik wie gehabt.
4. **Neustart während abgewählter Pause** → Abwahl überlebt, Reconcile spielt nicht eigenmächtig nach.

Aufnahme in Regressionslauf und 4-Uhr-Check.

## 6. Einordnung: Claudes eigene Funktion — was sie deckt und was nicht

Geprüft am 06.09. (Quellen: offizieller Claude-Code-Änderungsverlauf; Ankündigung Mitte August 2026):
- Das automatische Fortsetzen beim Limit-Reset mit vorgesetztem Haken ist eine Funktion der **interaktiven Oberfläche** (Desktop/Terminal-Ansicht; Einstellung „Continue automatically at usage limit" in /config). Sie greift in Micks Mac-Sitzungen — dort nutzen wir sie einfach mit.
- Für **nicht-interaktive** Läufe (Print-Modus, Agent SDK — so läuft der Bot) dokumentiert der Änderungsverlauf nur automatisches Fortsetzen bei **Verbindungsabbrüchen mitten im Stream** (Version 2.1.260), **nicht** beim Kontingent-Limit. Die genaue Versionsnummer des Oberflächen-Features ließ sich aus dem Änderungsverlauf nicht festnageln (zwei gezielte Abfragen ohne Treffer) — für diesen Auftrag ohne Belang, fürs Protokoll als Unsicherheit vermerkt.
- **Folge:** Für den Bot bleibt unser eigener H2-Mechanismus zuständig — das ist zugleich modellunabhängig, wie Adam es für künftige andere Modelle verlangt. Ein zweiter Wecker daneben wird ausdrücklich **nicht** gebaut (Begründung in Befund A3: zwei Nachspieler erzeugen Doppelantworten).

**Bündelung mit dem CLI-Update:** Der Zettel `2026-08-29_bauauftrag-offene-updates-einspielen.md` liegt bereits vor; wir sind auf 2.1.209. Nach dem Versionssprung die Limit-Signatur im SDK **erneut messen** (sie hat sich schon einmal geändert — genau das ist die Wurzel dieses Befunds) und den neuen Testfall 1 gegen die reale neue Signatur halten.

## 7. Was kann brechen — und wer merkt es

| Bruchstelle | Wirkung | Sicherung |
|---|---|---|
| Erkennung zu breit | Inhaltliche Antworten über Limits werden verschluckt | Testfall 2 (Zitat-Gegenprobe), enge Signatur statt Wortfolge |
| Erkennung zu eng (SDK ändert Wortlaut/Format erneut) | Englische Meldung rutscht wieder durch, Automatik steht | Messpflicht nach jedem CLI-Sprung im Update-Zettel; Testfall 1 an realer Signatur |
| Abwahl-Knopf ohne registrierte Wirkung | Adam wählt ab, Bot spielt trotzdem nach | Testfall 3; Knopf-Registrierung wie bei Freigaben |
| Reconcile überfährt die Abwahl nach Neustart | Abgewählte Pause wird doch automatisch nachgespielt | Testfall 4 |
| Meldung ohne Reset-Zeit | Falsche Uhrzeit wäre schlimmer als keine | Bestehende Regel bleibt: nur lesen, nie raten; Viertelstunden-Wiederholung |

---

*Ablage im Arbeitsordner; der Kurier trägt sie zur Kontrollsitzung. Rückfragen an Claudia über den Chat.*
