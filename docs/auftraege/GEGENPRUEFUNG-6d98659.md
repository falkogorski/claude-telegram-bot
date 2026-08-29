<!-- ROLLE: gegenpruefung-kontrolle -->
# Gegenprüfung `6d98659` — drei Reste, eine erledigte Frage

**Stichtag:** 29.08.2026 · **Von:** Engywuck (Kontrolle) · **Für:** Mick (Bau)
**Geprüfter Stand:** `6d98659` (auf `f5098f4` aufsetzend)
**Vorgehen:** Dein Stand in einen eigenen Baum ausgepackt, `__pycache__`
gelöscht, beide Gegenproben **selbst noch einmal gefahren** — mit der
erwarteten roten Zeile jeweils **vorher** hingeschrieben.

**Gut genug wenn:** (a) und (b) sind repariert, (c) ist entweder gebaut oder
mit Begründung auf der F-Liste. Das ist ein halber Block, kein ganzer.

---

## Was trägt — und ich habe es nicht geglaubt, sondern gemessen

| Fund | Gegenprobe | Ergebnis |
|---|---|---|
| ① Prozesserkennung | `bot_prozess()` auf `return None` entkernt | **genau** `✗ Prozesserkennung findet einen echten Prozess`, und **nur** diese Zeile |
| ③ Governance-Hook | alten `case`-Block zurückgestellt | **genau die fünf** vorhergesagten Formen rot (`claude.md`, `Claude.md`, `CLAUDE.MD`, `migration.md`, `Migration.MD`), die zwei kanonischen grün |
| ② Festpfade | im Git-Kontext ausgeführt | 84 Dateien in der Menge, Ergebnis leer — **weil die drei Pfade wirklich weg sind** |

`test_start_waechter_b1.py` ist ein echter Verhaltens-Prüfer: startet einen
realen Prozess, misst die Erkennung auf der Maschine, auf der sie läuft. Das
hätte den Fund von Anfang an verhindert, auf beiden Systemen. Und
`test_governance_hook.py` misst beide Richtungen — `notclaude.md` und
`CLAUDE.md.bak` laufen korrekt durch.

**Nichts davon berührt den Node-Pfad.** Adam konnte parallel springen.

---

## ERLEDIGT: die `ps`-Abschneide-Frage ist gemessen und negativ

Ich hatte die Sorge aufgeworfen, BSD-`ps` könnte die Ausgabe ohne `-ww` auf
Fensterbreite kürzen — dann stünde im Prüfer `bot.py` **am Anfang** der Zeile,
beim echten Bot aber **am Ende** eines langen Pfades, und der Prüfer wäre grün
über einem blinden Ernstfall.

**Adam hat es auf dem Mac gemessen:**

```
ps -Ao pid=,args= | awk '{if(length>m)m=length}END{print m}'
5859
```

**5859 Zeichen — es wird nicht geschnitten.** Deine Form ist richtig wie sie
ist. **Kein `-ww`, keine Änderung** — eine Änderung ohne Grund wäre hier der
Fehler. Die Zahl steht hier, damit die Frage in vier Wochen nicht neu
aufgemacht wird.

*(Linux-Seite zum Vergleich, von mir gemessen: 1163 Zeichen ungekürzt durch
eine Pipe. Beide Systeme sauber.)*

---

## Drei Reste — F-Liste, ausdrücklich KEINE dritte Runde

Das hier ist die Gegenprüfung, also der zweite Schritt. Was ich finde und was
nicht scharf-blockierend ist, geht auf die Liste, nicht in eine neue Schleife.
**Nichts davon hält einen Deploy auf.**

### (a) Die leere Menge sieht immer noch aus wie ein Bestehen

```python
try:
    aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files", "*.py"], …)
except Exception:
    return []
```

**Gemessen, in einem Baum ohne `.git`:**

```
Dateien in der Menge: 0
feste Betriebspfade: LEER (= grün)
```

Dieselbe Ausgabe wie im gesunden Fall — **zwei identische Meldungen, zwei
entgegengesetzte Bedeutungen.** Genau die Form des Fehlers, den du gerade
behoben hast: Der Prüfer misst nichts und meldet grün.

Heute greift es nicht, weil VPS und Mac Git-Checkouts sind. Es greift an dem
Tag, an dem jemand aus einem Tarball ausrollt, in einem Worktree misst oder
`git` im Dienstpfad fehlt — und dann still.

**Auflage:** Eine leere Dateimenge ist ein **Befund**, kein Bestehen. Eine
Zeile.

### (b) `endswith` auf dem Pfad-String

```python
if not name or name.endswith(("test_hermetik.py", "differenz.py")):
```

**Gemessen: heute trifft es genau die zwei gewollten Dateien**, also kein
akuter Schaden. Aber es ist eine Endungs-Prüfung auf den ganzen Pfad —
`scripts/test_differenz.py`, der naheliegendste Name für einen Prüfer von
`differenz.py`, fiele damit **still mit heraus**. Der Prüfer seines eigenen
Gegenstands wäre der erste, der verschwindet.

**Auflage:** `pfad.name` gegen eine Menge, nicht `endswith` auf dem Pfad.

### (c) Die Menge ist weiterhin nur `.py`

Der Fund war „die Dateimenge ist zu eng". `git ls-files "*.py"` weitet sie
innerhalb einer Sprache. **Gemessen in den versionierten Nicht-Python-Dateien:**

```
scripts/daily_check.sh:21    BOTDIR=/home/claudebot/claude-telegram-bot
scripts/daily_check.sh:34    BOTHOME=/home/claudebot
scripts/api_cache_pflege.sh:36  "${CACHE_BERICHT:-${BOTHOME:-/home/claudebot}/…}"
components.json:9,17,23,29,35,41,114,121   "venv": "/home/claudebot/…"
```

Die beiden in `daily_check.sh` sind **harte Vorgaben ohne Rückfall** — genau
die Form, die die Prüfart sucht. Die in `api_cache_pflege.sh` ist die
abgeleitete Form mit VPS-Vorgabe, die du in den `.py`-Dateien gerade
begradigt hast.

**Ob die falsch sind, ist ein Urteil** — `daily_check.sh` ist womöglich zu
Recht VPS-only. Der Punkt ist, dass der Prüfer sie **nicht sehen kann, um
die Frage zu stellen**. `components.json` ist der interessantere Fall: Der
Update-Monitor liest es auf beiden Maschinen.

**Auflage — oder eine begründete Ablage:** Wenn die Menge auf `.sh`, `.json`
und plists geweitet wird, braucht es je Dateityp eine eigene Ableseart (der
Syntaxbaum trägt nur bei Python). Das ist mehr als eine Zeile. **Wenn du das
für unverhältnismäßig hältst, schreib es als solches auf die F-Liste** —
begründet abgelegt ist besser als stillschweigend offen.

---

## Dein `pymupdf`-Fund stützt den offenen C2-Auftrag

Das ist kein Zufall und der Zusammenhang gehört benannt: In `requirements.txt`
steht `pymupdf>=1.28.2`, und `_c_pin_divergenz` liest **ausschließlich
`==`-Zeilen**. Deshalb hat es kein Prüfer bemerkt.

Damit ist mein Auftragspunkt ③ — *der Wächter ist blind für alles, was nicht
hart gepinnt ist* — **keine Vermutung mehr, sondern hat einen gemessenen
Vorfall hinter sich.** Dein Satz *„`git pull` bringt den Code, nicht die
Pakete"* ist die richtige Zusammenfassung; der Wächter muss ihn nur messen
können.

## Mein Punkt ② war falsch — nachgemessen und zurückgezogen

**Du hast recht, ich lag daneben, und die Ursache ist unangenehm passend.**
Ich hatte behauptet, das SDK bündele keine CLI. Nachgemessen in derselben
Umgebung, in der ich das Gegenteil gemeldet habe:

```
$ ls   <sdk>/_bundled/
claude                                    (275 MB)
$ <sdk>/_bundled/claude --version
2.1.219 (Claude Code)                     ← genau, was `_cli_version.py` nennt
$ claude --version
2.1.251 (Claude Code)                     ← die System-CLI, im Betrieb ungenutzt
```

Und `_find_cli()` nimmt das Bündel **vor** `shutil.which` — ich hatte die
Funktion zehn Zeilen zu spät zu lesen begonnen und den Zweig `# First, check
for bundled CLI` übersehen.

**Wie ich zu dem Fehlschluss kam, und das ist der eigentliche Befund:** Mein
`find` suchte mit `-maxdepth 3` nach Namen, die `cli` oder `claude-code`
enthalten. Das Bündel heißt schlicht `claude` und liegt eine Ebene tiefer —
es fiel durch **beide** Raster. **Ich habe die Abwesenheit mit einem Werkzeug
gemessen, das den Fund nicht sehen konnte, und das Nichtfinden als Befund
gemeldet.** Genau die Klasse, gegen die unsere eigene Prüfregel steht.

**Damit fällt auch mein Auftragspunkt ③(a).** Ein Prüfer, der `claude --version`
gegen `__cli_version__` hält, hätte auf beiden Maschinen dauerhaft rot
gemeldet — über einer Fassung, die im Betrieb niemand aufruft. **Du hast ihn
zu Recht nicht gebaut**, und deine Ersatzform ist die richtige: Der still
gefährliche Fall ist das **fehlende** Bündel mit stillem Rückfall auf die
Systemfassung, nicht die Differenz zwischen beiden. Gegenprobe gefahren,
greift, nennt sogar die Ersatz-CLI — sauber.

**Der Pin-Kommentar in `requirements.txt` war also richtig**, nicht falsch.
Meine Berichtigung war die Falschaussage. Streich sie aus dem vorigen Auftrag.

## Noch offen aus dem Auftrag von vorhin

1. ~~Pin-Kommentar berichtigen~~ — **hinfällig, siehe oben.**
2. **③(b) trägt** und ist gebaut — mit `pymupdf` als gemessenem Vorfall
   dahinter (`>=`-Zeile, vom C2-Wächter nicht gelesen).
3. **Der Pin 0.2.148 bleibt unangetastet**, bis Adam ein Fenster setzt.
   Node zuerst, SDK danach, getrennte Fenster.

## Adams Frage: `mcp` pinnen? — ja, aber im SDK-Fenster, und nicht allein

**Empfehlung: JA — und zwar zusammen mit dem SDK-Sprung, nicht vorher.**

*Warum ja:* An `mcp` hängt der In-Process-Transport des Suchservers, und daran
hängen die WebSearch-Kostenschranke (Rang A, 💰) und die Ausfall-Erkennung.
Deine Aufzeichnung belegt jetzt, dass es bei **identischem SDK** auseinander
läuft — 1.27.1 gegen 1.28.1. Genau der Fall, den Adams Gleichstands-Regel
meint.

*Warum nicht jetzt:* `mcp` ist ein **Mitzieher** des SDK, keine eigene Wahl.
Pinnen wir heute 1.27.1 oder 1.28.1, ziehen wir es beim Sprung auf 0.2.148 in
zwei Wochen wieder um — **zwei Eingriffe am Produktivsystem statt einem**, und
der erste auf eine Fassung, die niemand ausgemessen hat. Im Klonlauf ist
0.2.148 **mit mcp 1.29.1** gefahren worden; das ist die Paarung, die geprüft
ist, und die gehört festgeschrieben.

*Und nicht allein:* `anyio` driftet mit (4.13.0 gegen 4.14.2, deine Messung)
und ist die zweite SDK-Abhängigkeit. **Beide oder keins** — sonst pinnen wir
das Paket, das gerade auffiel, und das ist wieder eine Aufzählung statt einer
Menge.

*Was bis dahin trägt:* Deine Aufzeichnung. **Das Problem war nie die
Ungleichheit, sondern ihre Unsichtbarkeit** — sichtbar-und-ungleich ist
tragbar, unsichtbar war es nicht. Adams Regel ist damit erfüllt, bevor der
Pin kommt.

*Ein Vorbehalt, den Adam kennen muss:* Ein `mcp==`-Pin bindet gegen die
SDK-Spanne (`>=1.23.0,<3.0.0`). Verlangt ein künftiges SDK mehr, kollidiert
die Auflösung — **beim Installieren, nicht im Betrieb**, also laut und im
Wartungsfenster. Das ist die richtige Fehlerrichtung, aber es macht jeden
SDK-Sprung zu einem Drei-Paket-Vorgang. Das ist der Preis, und er ist
vertretbar.

## Zur Angleichung: einverstanden, und die Richtung ist der Punkt

**Mac folgt VPS.** Der Server trägt den Betrieb, also ist er die Bezugsgröße —
und den Mac hochzuziehen ist Wartung, den VPS hochzuziehen wäre ein
Fundament-Eingriff. Die 18 Unterschiede sind eine Entscheidung fürs
Wartungsfenster, keine Reparatur; das hast du richtig eingeordnet.

Vor jedem Commit `bash scripts/regressionstest.sh`, jeder Punkt einzeln.
