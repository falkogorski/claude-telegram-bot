<!-- ROLLE: zettel-node-vollzug -->
# Node 22 → 24: der Zettel für den Vollzug mit Adam

**Stichtag:** 29.08.2026, 04:3x · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Mick · **Auftrag:** Arbeitspaket Rang 9 / Update-Auftrag Schritt 3
**Alles auf dem VPS gemessen**, nicht auf dem Mac — die Divergenz zwischen den
Maschinen hat am 25.08. schon einmal einen blinden Prüfer erzeugt.

> **Das Ergebnis der Vorbereitung ist ein Zettel, kein Zustand.** An der
> produktiven Node-Fassung wurde nichts angefasst: kein `nvm use`, kein
> globales Upgrade, kein npm-Paket neu installiert.

---

## Der Fund, der die Risikolage ändert

**Der Auftrag begründet Adams Anwesenheit so:** *„Node trägt die
Claude-Code-CLI. Bricht sie, lebt der Bot weiter und jeder Modell-Lauf
scheitert — ein Bruch, der wie Ruhe aussieht."*

**Gemessen trifft das nicht zu. Die CLI hängt nicht an Node.**

| Messung | Ergebnis |
|---|---|
| Was ist `/usr/local/bin/claude`? | Verweis auf `…/claude-code/bin/claude.exe` |
| Was ist diese Datei? | **ELF-Binärdatei**, kein Node-Skript |
| Wogegen ist sie gelinkt? | nur `libc`, `libpthread`, `libdl`, `librt`, `ld-linux` — **keine Node-Bibliothek** |
| Läuft sie ohne Node im Pfad? | **Ja.** `env -i PATH=<ohne node> claude --version` → `2.1.209 (Claude Code)`, und `command -v node` findet in derselben Umgebung nichts |

Node wird also nur zur **Installation** über npm gebraucht, nicht zum
**Betrieb**. Das senkt das Risiko des Sprungs erheblich — es beseitigt es
nicht, denn npm bleibt der Weg für jedes künftige CLI-Update.

**Warum das den Vollzug trotzdem nicht allein macht:** Der Eingriff braucht
root, er berührt eine Paketquelle, und er ist auf einer Maschine, die den Bot
rund um die Uhr trägt. Das bleibt Adams Hand. Aber die Begründung im Zettel
ist jetzt die richtige — **root und Produktivbetrieb**, nicht eine
Abhängigkeit, die es nicht gibt.

## Der zweite Fund: die CLI ist doppelt installiert

```
/usr/lib/node_modules/@anthropic-ai/claude-code        2.1.209
/usr/local/lib/node_modules/@anthropic-ai/claude-code  2.1.209
```

Beide `package.json` sind byte-gleich (`md5` identisch), **aktiv ist die
zweite** (dorthin zeigt der Verweis in `/usr/local/bin`).

**Warum das eine Falle ist:** Ein `npm update -g` erwischt je nach Präfix
möglicherweise nur einen der beiden Orte. Dann stünde eine neue Fassung im
einen Ordner, während der Verweis auf die alte im anderen zeigt — und die
Fassungsanzeige sagt trotzdem etwas Plausibles. **Ein Update, das aussieht,
als hätte es gewirkt.**

**Beim Vollzug zu prüfen:** nach dem Update **beide** Orte vergleichen, nicht
nur `claude --version`.

---

## Ist-Stand, eingefroren

| | |
|---|---|
| Node | `v22.23.1`, Paket `22.23.1-1nodesource1` |
| npm | `10.9.8` |
| Paketquelle | `https://deb.nodesource.com/node_22.x`, Schlüssel `/usr/share/keyrings/nodesource.gpg` |
| verfügbar in der 22er-Quelle | `22.23.2-1nodesource1` |
| global installiert | `@anthropic-ai/claude-code@2.1.209`, `corepack@0.34.6`, `npm@10.9.8` |
| hängt an nodejs | `pandoc` (Rückabhängigkeit!), `nsolid` |
| Skripte, die node/npm anfassen | `scripts/version_monitor.py`, `scripts/updater.py` (+ deren Prüfer) |
| Platte | 218 GB frei von 251 GB |

**`pandoc` als Rückabhängigkeit ist zu beachten** — es erzeugt Adams PDFs.
Bricht die Paketauflösung beim Sprung, kann es mitgerissen werden.

---

## Der Rückweg, aufgeschrieben BEVOR er gebraucht wird

Ein Rückweg, der erst im Fehlerfall erfunden wird, ist keiner.

**Hinsprung (Adams Hand, als root):**
```
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt-get install -y nodejs
```

**Rückweg auf Node 22:**
```
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y --allow-downgrades nodejs=22.23.1-1nodesource1
```

**Woran man erkennt, dass es geklappt hat** — in dieser Reihenfolge:
1. `node --version` → die erwartete Fassung
2. `claude --version` → `2.1.209 (Claude Code)` (muss unverändert bleiben)
3. `pandoc --version | head -1` → vorhanden, nicht mitgerissen
4. `systemctl is-active claude-telegram-bot` → `active`
5. **Ein echter Modell-Lauf über den Bot** — eine Nachricht, eine Antwort.
   Die Schritte 1 bis 4 können alle grün sein, während genau das nicht geht.
6. `md5sum` beider `package.json` → weiterhin gleich (Doppelinstallation)

**Wenn etwas bricht:** Rückweg fahren, dann melden. Nicht reparieren.

---

## Was NICHT geprüft ist — die ehrliche Grenze

**Der Probelauf im Klon mit Node 24 wurde NICHT gefahren.** Der Auftrag nennt
ihn als dritten Punkt, und er fehlt. Der Grund ist keine Bequemlichkeit:

- Auf dem **Mac** wäre er wertlos — dort ist Node über Homebrew installiert,
  die Architektur ist arm64 statt amd64, und die CLI ist eine andere
  Binärdatei. Genau die Maschinen-Divergenz, die am 25.08. einen blinden
  Prüfer erzeugt hat.
- Auf dem **VPS** wäre er kein Klon, sondern ein Eingriff: Node lässt sich
  dort nicht ohne Weiteres zweifach installieren, ohne die Paketverwaltung
  anzufassen — und das ist genau das, was in dieser Nacht nicht geschehen soll.

**Der saubere Weg wäre ein Container** (`docker run -it node:24 …`) mit dem
Repo darin. Das ist machbar und lohnt sich, ist aber ein eigener Bauschritt
und braucht eine Docker-Installation auf dem VPS, die es dort heute nicht gibt.

**Was der fehlende Probelauf bedeutet:** Der Sprung ist weniger riskant als
gedacht (die CLI hängt nicht an Node), aber er ist nicht vorab gemessen. Wer
ihn fährt, sollte den Rückweg griffbereit haben — er steht oben.
