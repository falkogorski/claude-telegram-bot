# BEFUND — Maschinen-Gleichstand: drei Divergenzen, und der Lauf ist HALB

**Von:** Engywuck · **Stand:** 29.08.2026, 15:35 MESZ · geprüft gegen `76d3513`
**Anlass:** Adams Regel vom 29.08. — *„Alle Maschinen müssen immer konsequent
auf dem selben Stand sein … Querbezüge setzen."*

---

## ZUERST DIE EHRLICHKEIT: „drei Funde" heißt NICHT „es gibt drei"

Der Fächer lief mit 208 Agenten. **155 davon sind am Kontingent-Limit
gestorben** — darunter **alle drei Mechanismus-Entwürfe und die Synthese**.
Die drei Funde unten sind die, deren Widerlegungs-Prüfung noch durchkam.

**Was das bedeutet, unmissverständlich:** Die sechs Suchagenten haben deutlich
mehr gemeldet. Für die meisten Meldungen konnte kein Urteil mehr gefällt
werden — sie sind **weder bestätigt noch widerlegt**, sie sind ungeprüft.
Wer „drei Divergenzen" liest und daraus „der Bestand ist fast sauber" schließt,
zieht genau den falschen Schluss. **Das ist ein Zwischenstand, kein Ergebnis.**

Der Lauf lässt sich aus dem Zwischenstand fortsetzen; die 53 fertigen Agenten
werden dabei nicht neu bezahlt.

---

## Die drei bestätigten Divergenzen

### ① `scripts/start_waechter.py:75` — `pgrep -af` bricht auf dem Mac (LAUT)

```python
out = subprocess.run(["pgrep", "-af", "bot[.]py"], ...)
...
teile = zeile.split(None, 1)
if len(teile) != 2 or "start_waechter" in teile[1]: continue
```

**BSD/macOS-`pgrep` gibt nur nackte PIDs aus** — die Befehlszeile käme erst mit
`-l`, und `-a` bedeutet dort etwas anderes (Vorfahren einbeziehen). Damit
scheitert `len(teile) != 2` für **jede** Zeile, und `bot_prozess()` liefert
immer `None`.

**Die Folge ist nicht harmlos:** `sauber_hoch()` prüft `bot_prozess() is None`
zuerst, meldet also ewig „kein Bot-Prozess" — und nach Fristablauf spielt
`_bewachen()` per `zurueckrollen()` ein `pip install` über die venv eines
**völlig gesunden** Bots.

**Und der Mac ist ausdrücklich Zielmaschine** — ich habe es nachgesehen:
`dienst_aktiv()` (Zeile 94) hat eigens einen Zweig *„None, wenn es hier kein
systemd gibt (Mac)"*. Die Datei rechnet also mit macOS und benutzt zwei Zeilen
weiter einen GNU-only-Aufruf. **`shutil` ist bereits importiert**, ein
`which`-Zweig wäre drei Zeilen.

**UNGEPRÜFT bleibt die BSD-Seite** — hier steht nur Linux zur Verfügung. Die
GNU-Ausgabeform ist gemessen, die BSD-Form aus der Dokumentation.

### ② `scripts/differenz.py:512` — die Prüfart misst eine Positivliste (STILL)

```python
dateien = [d for d in sorted((WURZEL / "scripts").glob("test_*.py"))
           if d.name != "test_hermetik.py"] + [WURZEL / "bot.py"]
```

**Selbst ausgeführt, eben:**

```
_feste_betriebspfade()  ->  LEERE MENGE
```

**Und gleichzeitig steht im Bestand:**

```
scripts/stundenblume.py:193      "/home/claudebot/claude-telegram-bot/logs/daily-check.log"
scripts/version_monitor.py:29    "/home/claudebot/claude-telegram-bot/logs/version-monitor.log"
scripts/version_monitor.py:299   "/home/claudebot/claude-telegram-bot/logs/version-monitor-gesehen.json"
```

**Das Urteil funktioniert — die Dateimenge nicht.** Sie erfasst 45 Prüfer plus
`bot.py`; alle Betriebsskripte, alle `*.sh`, die plists und `components.json`
liegen außerhalb. **Der Prüfer, der ortsabhängige Festpfade finden soll, kann
die drei echten nicht sehen.**

Das ist die **Mengen-Regel, zum fünften Mal** — und diesmal in
`differenz.py`, dem Werkzeug, das eigens gegen Aufzählungen gebaut wurde.
Dieselbe Falle wurde in `daily_check.sh:372-380` bei den Zeitgebern schon
einmal ausgetrieben.

### ③ `.claude/hooks/guard-master-files.sh:19` — Schreibweise als Schranke (STILL)

```bash
*/MIGRATION.md|*/CLAUDE.md|MIGRATION.md|CLAUDE.md) ;;
```

`case` in bash vergleicht **schreibweisenempfindlich**; wer nicht passt, fällt
in `*) exit 0` — also **durchlassen**, nicht blockieren. Auf Adams Mac ist das
Dateisystem schreibweisen-**un**empfindlich: Ein Zugriff auf `claude.md` trifft
dieselbe Datei, umgeht aber beide Muster.

**Damit ist die dritte Schicht der Führungs-Register-Absicherung ausgerechnet
auf der Maschine löchrig, auf der die führende Sitzung schreibt.** Auf VPS und
Container entsteht kein Loch — die Datei existiert dort schlicht nicht unter
dem anderen Namen. Fail-open statt fail-closed.

---

## Was ich zu Adams Regel sage — der eine Teil, der eine Ausnahme braucht

Adams Regel hat zwei Hälften, und sie sind unterschiedlich haltbar.

**„Querbezüge setzen — wird eine aktualisiert, werden die anderen geprüft":
uneingeschränkt richtig.** Alle drei Funde oben sind genau das: eine Annahme,
die auf einer Maschine stimmt und auf der anderen nicht, ohne dass irgendetwas
den Bezug herstellt.

**„Immer auf die aktuellsten Versionen": hier widerspreche ich, benannt.**
Das **Agent-SDK ist bewusst gepinnt**, weil es die Claude-Code-CLI mitbringt —
es ist das Fundament, nicht eine Bibliothek unter vielen. Ein „immer aktuell"
ohne Ausnahme würde genau das automatisieren, was uns den Boden wegziehen kann.
Micks Nachtlauf hat das gerade belegt: Der Sprung auf 0.2.140+ **ändert die
Fehlerstruktur** (`str(exc)` liefert nur noch „Command failed"), und ohne
Vorab-Lesen der Notizen wäre die Zugangs-Rücklage still ausgefallen.

**Die tragfähige Fassung wäre:** *Alle Maschinen tragen dieselbe Fassung —
welche Fassung das ist, entscheidet der Pin, nicht der Kalender.* Gleichstand
ist die harte Regel; Aktualität ist das Ziel mit Prüfschritt davor.

## Was NICHT gemessen werden konnte

Der Fächer liest **das Repo**. Er sieht nicht, was auf Mac und VPS tatsächlich
installiert ist — Paketstände, Node-Fassungen, global installierte Werkzeuge.
**Genau dort sitzt aber die Hälfte von Adams Anliegen.** Ein Gleichstands-Prüfer
muss auf jeder Maschine laufen und seine Messung irgendwo zusammenführen; das
kann kein Repo-Scan leisten.

---

## Mein Vorschlag zum Weiterarbeiten

1. **Fund ① sofort an Mick** — er ist laut, aber sein Schaden (Rollback über
   eine gesunde venv) ist echt, und die Reparatur sind drei Zeilen mit dem
   bereits importierten `shutil`.
2. **Fund ② und ③ in denselben Zug** — beide still, beide klein, beide in
   Schutzmechanismen.
3. **Den Fächer fortsetzen**, wenn Kontingent da ist — die Entwürfe fehlen
   vollständig, und ohne sie ist Adams Regel gemessen, aber nicht beantwortet.
4. **Erst danach den Mechanismus bauen.** Ein Gleichstands-Wächter ist genau
   die Art Wächter, die still sterben kann — er gehört zuletzt gebaut und mit
   der Entkernungs-Gegenprobe, nicht schnell zwischendurch.
