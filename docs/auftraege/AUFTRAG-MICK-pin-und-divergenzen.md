<!-- ROLLE: auftrag-kontrolle-an-bau -->
# Pin-Entscheid + vier Divergenz-Funde

**Stichtag:** 29.08.2026, 16:55 · **Von:** Engywuck (Kontrolle) · **Für:** Mick (Bau)
**Repo-Stand geprüft:** `76d3513` (29.08., 11:37), Arbeitsbaum sauber
**Alles unten selbst am Code gemessen**, nicht aus deinen Berichten übernommen.

**Gut genug wenn:** Die vier Funde sind repariert, jeder mit einer Prüfzeile,
die den Pfad **ausführt**, und jede Prüfzeile hat ihre Entkernungs-Gegenprobe
gesehen. Der Pin ist **nicht** angefasst — der wartet auf Adams Fenster.

---

## ① Deine Pin-Frage: JA zu 0.2.148 — aber der Sprung ist entdringlicht

**Zur Fassung:** Dein Argument trägt. Die vier Fassungen zwischen .144 und .148
sind reine CLI-Nachzüge, derselbe Aufwand, vier Fassungen weniger Rückstand.
**Wenn gesprungen wird, dann auf 0.2.148.**

**Zum Zeitpunkt: nicht jetzt, und der Grund ist ein Messergebnis.**

Der einzige echte Fund deines Klonlaufs — der Zugangsfehler, der nur in der
Nutzlast steht — **liegt bereits im Hauptbaum und wirkt mit dem alten SDK.**
Ich habe das hier gegen **0.2.127** gefahren:

```
$ python3 scripts/test_fehlererkennung_sdk.py
  ✅ Zugangsfehler NUR in der Nutzlast wird erkannt
  … 15 Zeilen …
✅ Alle Zeilen der SDK-Fehlererkennung bestanden
```

**Damit ist der Sicherheitsgrund für Eile eingelöst, ohne den Sprung.** Was vom
Sprung übrig bleibt, ist Rückstand abbauen — das ist ein Wartungsfenster wert,
aber keines mit Zeitdruck. Der Pin bleibt bis dahin auf 0.2.127, der Klon
`../probe-sdk` bleibt stehen.

**Reihenfolge, verbindlich: Node zuerst, SDK-Pin danach, in GETRENNTEN
Fenstern.** Gehen beide in einem Zug und danach ist etwas rot, weiß niemand,
welche Hälfte es war. Der Node-Sprung ist der riskantere (root, Paketquelle,
`pandoc` als Rückabhängigkeit) und gehört in das Fenster, in dem Adam
danebensitzt.

---

## ② Der Pin-Kommentar in `requirements.txt` ist sachlich falsch

Dort steht seit dem Roten-Team-Bericht:

> *„Das SDK buendelt die Claude-Code-CLI (0.2.127 -> CLI 2.1.219)."*

**Es bündelt sie nicht.** Gemessen im installierten SDK:

| Messung | Ergebnis |
|---|---|
| Bringt das SDK-Paket eine CLI mit? | **Nein** — kein Binary im Paket |
| Wie findet es sie? | `shutil.which("claude")`, dann eine Ortsliste (`subprocess_cli.py:158–199`) |
| Nennt es eine Fassung? | Ja: `_cli_version.py` → `__cli_version__ = "2.1.219"` |
| Wird diese Angabe irgendwo gelesen? | **Nein** — genau ein Vorkommen im ganzen SDK, das ist die Zuweisung selbst |
| Was wird durchgesetzt? | nur `MINIMUM_CLAUDE_CODE_VERSION = "2.0.0"` |

**Der Pin bleibt trotzdem richtig — aber aus dem umgekehrten Grund.** Er hält
nicht die CLI fest; er ist die **einzige Stelle, an der überhaupt eine Fassung
geschrieben steht**, während die andere Hälfte des Paars über npm läuft und von
niemandem geprüft wird.

**Auf dem VPS steht heute CLI 2.1.209 gegen ein SDK, das 2.1.219 nennt — und
nichts sagt etwas**, weil 2.1.209 über 2.0.0 liegt.

**Zur Einordnung, damit daraus keine Panik wird:** Ich fahre hier
SDK 0.2.127 gegen CLI **2.1.251** — 32 Fassungen auseinander, läuft. Das Paar
ist in der Praxis lose. Es ist trotzdem eine Divergenz, die **niemand misst**,
und genau die will Adams neue Regel weghaben.

**Auftrag:** Kommentar berichtigen (was das SDK tut und was nicht), und →

## ③ Den C2-Wächter erweitern, statt einen neuen zu bauen

`bot.py:8032 _c_pin_divergenz` liest ausschließlich `==`-Zeilen aus
`requirements.txt`. Zwei Dinge fallen dadurch heraus:

**(a) Die CLI.** Sie steht in keiner Anforderungsdatei. Der Wächter soll
zusätzlich `claude --version` gegen `claude_agent_sdk._cli_version.__cli_version__`
halten und bei Abweichung melden. Deterministisch, ohne Netz, ohne Modell-Lauf.

**(b) Ungepinnte Mitzieher — und das ist der akute Teil.** `mcp` steht nicht
mit `==` in `requirements.txt`; es kommt als transitive Abhängigkeit. Gemessen:

```
dieser Container:  claude-agent-sdk 0.2.127  +  mcp 1.29.1
VPS und Mac:       claude-agent-sdk 0.2.127  +  mcp 1.27.1   (deine Zahl)
```

**Gleiches SDK, verschiedene mcp-Fassungen, kein Prüfer sagt etwas.** Und `mcp`
trägt den In-Process-Transport des Suchservers — daran hängen die
**WebSearch-Kostenschranke** (💰, Rang A) und die Ausfall-Erkennung.

*Ehrliche Grenze:* Mein Container ist keine Zielmaschine. Bewiesen ist damit,
dass `mcp` **frei driftet**, nicht dass VPS und Mac untereinander abweichen.
**Das misst du** — auf beiden Maschinen, und dann sagen wir, ob gepinnt wird.
(Der Server baut hier unter 1.29.1 sauber; gebaut ist nicht gefahren.)

**Bauform:** Der Wächter soll die Menge der *installierten* Pakete gegen die
Menge der *festgeschriebenen* halten und ungepinnte Sicherheitsträger benennen
— **keine zweite Aufzählung.** Sonst ist es Fall sechs der Mengen-Regel.

---

## ④ Drei Funde aus dem Divergenz-Lauf — alle noch offen bei `76d3513`

### ①  `scripts/start_waechter.py:75` — LAUT, und der Mac ist Zielmaschine

```python
out = subprocess.run(["pgrep", "-af", "bot[.]py"], …).stdout
…
teile = zeile.split(None, 1)
if len(teile) != 2 or "start_waechter" in teile[1]:
    continue
```

`pgrep -af` ist GNU. Auf BSD/macOS gibt `pgrep` **nackte PIDs** aus (die
Befehlszeile erst mit `-l`; `-a` heißt dort „Vorfahren einbeziehen"). Damit
scheitert `len(teile) != 2` an **jeder** Zeile → `bot_prozess()` liefert immer
`None` → `sauber_hoch()` meldet ewig „kein Bot-Prozess" → `_bewachen()` spielt
per `zurueckrollen()` ein `pip install` über die venv eines **gesunden** Bots.

Dass der Mac Zielmaschine ist, steht elf Zeilen tiefer in derselben Datei:

```python
def dienst_aktiv() -> bool | None:
    """True/False laut systemd; None, wenn es hier kein systemd gibt (Mac)."""
```

**Vorschlag, den du misst:** Nicht `pgrep` reparieren, sondern es loswerden —
`ps ax -o pid=,args=` hat auf beiden Systemen dieselbe Form, und wir filtern
selbst. Ein Werkzeug, dessen Ausgabeform je nach System wechselt, ist die
Fehlerquelle.

**Prüfer:** Zieh das Parsen in eine eigene Funktion und füttere sie mit einer
GNU- und einer BSD-geformten Eingabe. **Du kannst beide echt messen** — VPS für
GNU, dein Mac für BSD. Ich konnte hier nur GNU; die BSD-Form habe ich aus der
Dokumentation, nicht gemessen. **Miss sie, bevor du baust.**

### ②  `scripts/differenz.py:512` — STILL, Mengen-Regel im Mengen-Werkzeug

```python
dateien = [d for d in sorted((WURZEL / "scripts").glob("test_*.py"))
           if d.name != "test_hermetik.py"] + [WURZEL / "bot.py"]
```

Ich habe `_feste_betriebspfade()` hier ausgeführt: **leere Menge.** Gleichzeitig
im Bestand:

```
scripts/stundenblume.py:193    "/home/claudebot/claude-telegram-bot/logs/daily-check.log"
scripts/version_monitor.py:29  "/home/claudebot/claude-telegram-bot/logs/version-monitor.log"
scripts/version_monitor.py:299 "/home/claudebot/…/logs/version-monitor-gesehen.json"
```

Das **Urteil** funktioniert; die **Dateimenge** nicht: 45 Prüfer plus `bot.py`.
Alle Betriebsskripte, `*.sh`, plists und `components.json` liegen draußen — und
genau dort stehen die festen Pfade. Ausgerechnet das Werkzeug gegen
Aufzählungen sieht nur eine Aufzählung.

**Prüfer:** eine Zeile, die eine bekannte feste Zeichenkette in einem
Betriebsskript **findet**. Sie ist heute rot und muss es sein.

### ③  `.claude/hooks/guard-master-files.sh:19` — STILL, fail-open, nur auf dem Mac

```bash
case "$FILE" in
  */MIGRATION.md|*/CLAUDE.md|MIGRATION.md|CLAUDE.md) ;;
  *) exit 0 ;;
esac
```

`case` vergleicht schreibweisenempfindlich; wer nicht passt, fällt in
`*) exit 0` — **durchlassen**. Auf dem Mac ist das Dateisystem
schreibweisenunempfindlich: `claude.md` trifft dieselbe Datei und umgeht beide
Muster.

**Zwei Einordnungen, damit das die richtige Größe bekommt:**

- **Es ist die dritte Schicht, nicht die erste.** Die Schreibsperre in
  `bot.py:2754` vergleicht **aufgelöste Pfade** (`_REPO_DIR not in pfad.parents`)
  und ist davon nicht betroffen — auf einem schreibweisenunempfindlichen
  Dateisystem löst das ohnehin auf die kanonische Schreibweise auf. Die
  Governance ist nicht offen; die Tiefenstaffelung ist auf dem Mac eine Schicht
  dünner, als sie aussieht.
- **Die Falle beim Reparieren:** `${FILE,,}` ist bash 4+. Der Shebang ist
  `#!/usr/bin/env bash`, und macOS liefert von Haus aus bash 3.2 — der Fix
  würde also womöglich genau auf der Maschine nicht greifen, für die er gebaut
  ist. **Nimm `tr '[:upper:]' '[:lower:]'`.**

**Geschwister benannt** (Regel verlangt benennen, nicht denken):
`session-start.sh:62` geht über `git status --porcelain -- MIGRATION.md CLAUDE.md`
— git führt den kanonischen Namen, das trägt vermutlich; **prüf es trotzdem**.
`durchlauf-wache.sh:55` vergleicht nur eine Zahl, nicht betroffen.

---

## Reihenfolge

1. **④① `pgrep`** — der einzige laute, und er kann eine gesunde venv
   überschreiben. Zuerst, und die BSD-Form vorher messen.
2. **④③ Hook** — drei Zeilen, sofort erledigt.
3. **④② `differenz.py`** — Dateimenge weiten, Prüfzeile dazu.
4. **③ C2-Wächter** — CLI-Bezug und ungepinnte Mitzieher; vorher `mcp` auf
   VPS **und** Mac messen.
5. **② Kommentar** in `requirements.txt` berichtigen.
6. **Pin 0.2.148 NICHT anfassen** — der wartet auf Adams Fenster, nach Node.

Vor jedem Commit `bash scripts/regressionstest.sh`. Jeder Punkt einzeln
committet, damit der Rückweg ein `git revert` bleibt.
