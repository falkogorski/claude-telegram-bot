<!-- ROLLE: node-major-befehlsblock -->
# Node 22 → 24: vorbereiteter Befehlsblock

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** Commit-Zeit dieses Stands ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> **⛔ NICHT EINSPIELEN.** Adam-Entscheid 25.07.: **jetzt nicht.** Dieser Block
> ist vorbereitet und wartet auf ein **bewusstes Fenster mit Adam**. Er steht
> hier, damit im Fenster nichts improvisiert werden muss — nicht als Einladung.

## Warum dieser Punkt anders wiegt als andere Updates

**Die Claude-CLI läuft auf Node.** Ein Major-Bruch nimmt also nicht ein
Werkzeug, sondern **das Hirn** — auf einem System, das **root braucht, um sich
zu reparieren**. Root hat nur Adam. Geht es schief, kann sich der Bot nicht
selbst heilen: Der Start-Wächter (B1) könnte pip-Pakete zurückrollen, aber kein
Systempaket.

**Gemessener Ist-Stand (VPS, 25.07.2026):**

| | Wert |
|---|---|
| Node | **v22.23.1** (`/usr/bin/node`, root-eigen, 124,8 MB) |
| npm | 10.9.8 |
| Global daran hängend | `@anthropic-ai/claude-code@2.1.209` · `corepack@0.34.6` · `npm@10.9.8` |

Das Register benennt die Testpflicht — **es ersetzt die Messung nicht** (R1).
Deshalb steht oben, was tatsächlich installiert ist, und nicht, was vermutlich.

## Vor dem Fenster (ohne root, kann jederzeit laufen)

```bash
node --version && npm --version && npm ls -g --depth=0
```

```bash
cd ~/claude-telegram-bot && bash scripts/regressionstest.sh
```

Der Regressionslauf **muss vorher grün sein** — er nennt seinen Sollwert selbst; eine hier eingetippte Zahl wäre veraltet, sobald eine Prüfung dazukommt. Ein Update auf
ein bereits wackelndes Fundament ist der Fehler, den A5 im Updater verhindert —
hier gilt dieselbe Regel von Hand.

## Im Fenster — Adam führt aus (root)

Ein Befehl pro Zeile, keine Kommentare in den Blöcken (zsh würde `#` ausführen).

**Schritt 1 — Rückweg sichern: welche Fassung ist gerade installiert?**

```bash
apt-cache policy nodejs | head -5
```

Die dort genannte **Installed**-Fassung notieren. Sie ist der Rückrollpunkt.

**Schritt 2 — Paketquelle auf 24 umstellen**

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
```

**Schritt 3 — einspielen**

```bash
sudo apt-get install -y nodejs
```

**Schritt 4 — sofort nachmessen (die eigentliche Prüfung)**

```bash
node --version && npm ls -g --depth=0
```

```bash
sudo -u claudebot bash -c 'cd ~/claude-telegram-bot && bash scripts/regressionstest.sh'
```

```bash
sudo systemctl restart claude-telegram-bot && sleep 15 && systemctl show claude-telegram-bot -p MainPID
```

Danach eine echte Nachricht an den Bot schicken. **Erst diese Antwort beweist,
dass die CLI trägt** — der Regressionslauf prüft den Bot, nicht die Anmeldung am
Modell.

## Rückrollbefehl — gleich dabei, wie gefordert

```bash
sudo apt-get install -y --allow-downgrades nodejs=<Fassung-aus-Schritt-1>
```

```bash
sudo systemctl restart claude-telegram-bot && sleep 15 && systemctl show claude-telegram-bot -p MainPID
```

Sollte die Paketquelle den alten Stand nicht mehr anbieten, ist der zweite Weg
die Umstellung der Quelle zurück auf 22 und ein erneutes Einspielen:

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
```

```bash
sudo apt-get install -y --allow-downgrades nodejs
```

## Was im Fenster gilt

- **Nur mit Adam am Rechner.** Nichts davon läuft nachts.
- **Keine Geheimnisse** in diesen Befehlen — bewusst geprüft.
- **💰 keine Kosten:** freie Paketquelle, eigener Server.
- **Abbruchkriterium:** Bleibt der Regressionslauf nach dem Einspielen unter
  vollständig grün oder antwortet der Bot nicht auf eine echte Nachricht, wird
  **zurückgerollt**, nicht nachgebessert. Nachbessern gehört in ein zweites
  Fenster, nicht in dieses.
