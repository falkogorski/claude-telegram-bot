> **An Adam, zur Weitergabe an Mick** · Engywuck · 09.09.2026, 19:26 · geprüft am Code: `4854f64` (Deploy-Block), `23d01d6`, `f3d1b58`

# Nachtrag zu Micks Deploy-Block (09.09., 19:20)

**Urteil: Schritte 1 bis 3 tragen. Der Rückweg trägt nicht — bitte vor dem Deploy ersetzen.** Drei Befunde, einer davon ein echter Fehlpfad.

## Befund 1 — `git revert f3d1b58` auf dem Server ist eine Falle (ersetzen)

Mick nennt als Rückweg für den Hook: `git revert f3d1b58` im VPS-Klon. Das scheitert zweifach, und zwar erst **nach** dem Eingriff:

- Ein Revert ist ein **Commit**. Der VPS-Klon hat nach 8.7 bewusst **keine git-Identity** und einen **pre-commit-Blocker** (MIGRATION.md, 23.07., „live getestet, Exit 1"). Git wendet die Änderung an, kann den Commit nicht schreiben und lässt den Klon im Zustand „Revert nicht abgeschlossen" zurück. Der nächste `merge --ff-only` verweigert dann. Adam stünde mit einem halb zurückgedrehten Arbeitsbaum da und bräuchte `git revert --abort`.
- „Nur der Hook, nicht der ganze Block" stimmt nicht: `f3d1b58` ist **153 Zeilen bot.py** und enthält **Limit je Person und den Hook**. Der Revert nähme beides.

**Ersatz, für Adam ein einziger Rückweg:** `reset --hard` auf den Stand aus Schritt 0 (unten), dann Neustart. Ein Rückweg „nur der Hook" existiert nur über Mick: Revert am Mac, pushen, Adam zieht mit `--ff-only`. Das ist der einzige governance-konforme Weg für einen Teil-Rückbau.

## Befund 2 — „`0270fd7` ist der Stand, der heute läuft" ist eine Annahme

Mein Stand sagt `e335c23` (04.09., 22:17); Mick sagt `0270fd7` (04.09., 21:40). Die Differenz ist ein Doku-Commit, der Rückweg funktioniert so oder so. Aber keiner von uns hat es **gemessen**, und ein Rückweg auf einen geratenen Stand ist genau die Klasse Fehler, die wie Ruhe aussieht. Deshalb ein Schritt 0, der den Wert **abliest**.

## Befund 3 — die Zahl „74/75" ist meine Container-Messung, nicht die des VPS

Hier fehlt ffmpeg, also ist H1 übersprungen. Auf dem VPS ist ffmpeg da, dafür läuft der Bot während Schritt 1, und dann ist die **Heartbeat-Wache** übersprungen (regressionstest.sh, Zeile ~427, gemessen). Vermutlich wieder 74/75 mit einer Übersprungenen, aber aus anderem Grund. Die tragfähige Prüfzeile hängt nicht an der Zahl, sondern am **Rückgabewert**: 0 = alles grün, 77 = grün mit Übersprungenem, alles andere = Fehlschlag. Micks `| tail -5` verschluckt den Rückgabewert und kann ein ❌ weiter oben verdecken.

## Was ich entkräftet habe

Das SDK auf dem Server ist `0.2.127` (Pin bei `23d01d6`, unverändert). Ich habe **gemessen**, dass diese Version das Feld `hooks` in `ClaudeAgentOptions` und `HookMatcher` kennt. Ein Startbruch beim Bau der Optionen ist damit ausgeschlossen. Was bleibt, ist Micks Schritt 3: der erste echte Durchlauf des Hooks durch das SDK.

## Die ersetzten Zeilen für Adam (Schritt 0 und 1 neu, Rückweg neu; Schritte 2 und 3 wie bei Mick)

Schritt 0, Stand ablesen und **den Hash notieren**:

```bash
ssh claudebot 'git -C ~/claude-telegram-bot log -1 --format="%h %ad %s" --date=format:"%d.%m. %H:%M"'
```

Schritt 1, Stand ziehen und prüfen:

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 23d01d6 && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`. Jede andere Zahl: **nicht neu starten**, mir `/tmp/reg.log` schicken (`ssh claudebot cat /tmp/reg.log`).

Rückweg, falls Schritt 2 oder 3 hakt, mit dem Hash aus Schritt 0:

```bash
ssh claudebot 'git -C ~/claude-telegram-bot reset --hard <HASH-AUS-SCHRITT-0>'
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Eine Zeile an Mick

Rückwege für den VPS-Klon sind immer `reset --hard` auf einen abgelesenen Stand oder ein Push vom Mac. Nie ein Befehl, der dort einen Commit erzeugt. Das gehört als Satz in `docs/befehlsbloecke-adam.md`, damit die nächste Vorlage ihn nicht wieder erfindet.
