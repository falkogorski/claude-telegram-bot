# Für `NOTBETRIEB.md` — Connis zwei Zeilen, meine Messung dazu

**31.08.2026, 22:04 MESZ · Kontroll-Sitzung** (mein Container läuft auf UTC —
alle meine heutigen Kopfzeiten waren zwei Stunden zu früh, berichtigt)

Conni hat aus ihrem Archiv den Handy-Notfallweg fertig formuliert. **Ein Wert
darin ist überholt, und ich habe ihn nachgemessen** — bitte die berichtigte
Fassung eintragen, nicht ihre.

---

## Der Eintrag, berichtigt

> **„Ich bin unterwegs und will nur wissen: lebt er?"** — GitHub-App (oder
> Browser) öffnen → privates Repo `claude-bot-logs` → Zeit des letzten Commits
> ansehen. Der Log-Abgleich schreibt **alle fünf Minuten**; ist der letzte
> Commit älter als **zwanzig Minuten**, stimmt etwas — Server, Abgleich oder
> Netz. **Das Ausbleiben der Commits ist selbst der Alarm**; dieser Blick
> braucht weder Bot noch Terminal.

---

## Was ich gemessen habe, und warum es den Wert ändert

**Conni schrieb „stündlich" mit ausdrücklichem Vorbehalt** („mein Stand ist der
18.08."). Ihr Vorbehalt war berechtigt:

- `docs/befehlsbloecke-root.md` trägt **drei** Setzungen desselben Timers. Die
  stündliche ist überschrieben mit *„Log-Abgleich stündlich (18.08.2026) —
  EINGESPIELT, **seit 19.08. überholt**"*.
- Gültig ist *„Log-Abgleich alle fünf Minuten (19.08.2026) — EINGESPIELT
  19.08., 23:15 (gemessen)"*.
- **Am echten Verlauf belegt:** lückenlos alle fünf Minuten über Stunden,
  letzter Commit 21:55 — eine Minute vor der Messung.

**Mit „zwei Stunden" wären vierundzwanzig ausgefallene Läufe nötig, bevor die
Notfall-Zeile anschlägt.** Das ist keine Notfall-Auskunft mehr.

---

## Der eine Punkt, den du messen musst — nicht ich

`scripts/log_sync.sh:208` committet **nicht**, wenn sich nichts geändert hat:

```
if git diff --cached --quiet; then
  echo "Keine Log-Änderungen — nichts zu pushen."
```

**Im Verlauf sehe ich keine einzige Lücke** — es ändert sich offenbar immer
etwas. Aber ich messe von außen und sehe nur, was gepusht wurde. **Ob es
wirklich stille Läufe geben kann** (ein Tag ohne jede Nachricht, ohne
Ausarbeitung, ohne Fehlerzeile), weißt du besser.

**Wenn ja, ist zwanzig Minuten zu eng** und die Zeile schlägt an einem ruhigen
Tag falsch an — schlimmer als keine Zeile. Dann gehört stattdessen ein
Herzschlag in den Abgleich: eine Zeile, die auch ohne Inhalt geschrieben wird.
**Bau das nicht ungefragt** — melde es, es wäre eine Änderung an einem
laufenden Wächter.

---

**Gut genug wenn:** Die zwei Zeilen stehen in `NOTBETRIEB.md` mit der
gemessenen Schwelle, und im Bericht steht, ob stille Läufe möglich sind.
