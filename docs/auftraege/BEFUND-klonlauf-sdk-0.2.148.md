<!-- ROLLE: befund-klonlauf-sdk -->
# Probelauf im Klon: SDK 0.2.127 → 0.2.148

**Stichtag:** 29.08.2026, 04:1x · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Mick · **Klon:** `../probe-sdk`, eigene venv, Python 3.12.13
**Grundlage:** `2026-08-29_bauauftrag-offene-updates-einspielen.md`, Schritt 2

## Vorbedingung war erfüllt

Der Auftrag sperrt diesen Schritt, solange Rang A offen ist: *„Ein Netz mit
bekannter Masche darf nicht gespannt werden, während man darüber läuft."*
Alle acht Rang-A-Stellen sind vorher repariert worden — **einschließlich
Stelle 7, dem Start-Wächter selbst**, der im abgekoppelten Betrieb Erfolg
meldete, ohne dass jemand wachte. Genau der Wächter, der diesen Sprung
absichern soll.

## Ergebnis in Zahlen

| | vor dem Sprung | nach dem Sprung |
|---|---|---|
| `claude-agent-sdk` | 0.2.127 | **0.2.148** |
| `mcp` (Mitzieher) | 1.27.1 | **1.29.1** |
| Regressionslauf im Klon | 59/59 | **58/59** |

Die eine rote Zeile ist **kein Bruch, sondern der Wächter bei der Arbeit**:
*Pin-Divergenz (C2): installiert 0.2.148 ≠ gepinnt 0.2.127.* Sie verschwindet,
sobald der Pin nachgezogen wird — und sie hätte laut gemeldet, wenn jemand
das Update ohne Pin eingespielt hätte.

## Der Fund, für den der Klon da war

**Ein Zugangsfehler wäre unerkannt geblieben.** Ab 0.2.140 wirft das SDK
`ResultError` mit strukturierter Nutzlast; steht der Anbietertext nur in
`data` statt in der Meldung, sah `str(exc)` nur noch `Command failed`.

Gemessen mit 0.2.148, beide Formen — Einzelheiten und Folgen stehen im Commit
`72466ac`. Der Fix ist **fassungsunabhängig** und liegt bereits im Hauptbaum:
Er wirkt mit 0.2.127 genauso und hängt nicht an der Entscheidung über den
Sprung.

## Die drei Pflichtprüfungen aus dem Vorab-Befund

1. **`ResultError` durch `is_auth_error` / `is_context_overflow`** — gefahren,
   Lücke gefunden, geschlossen, mit drei Entkernungen gegengeprobt.
2. **Der eigene MCP-Suchserver** (0.2.140 hat den In-Process-Transport von
   handgeschriebenem JSON-RPC auf mcps eigenen umgebaut) — ausgeführt:
   Server steht, Werkzeug `web_search` läuft, Rückgabeform stimmt
   (`{"content": [...]}`), und ein nicht erreichbarer Zulieferer führt zu
   einer **verständlichen Meldung statt zu einer Ausnahme**.
3. **Die WebSearch-Kostenschranke** — im Klon Teil des Regressionslaufs und
   dort grün.

## Was dieser Lauf NICHT belegt — die ehrliche Grenze

Der In-Process-Transport wurde **bis zum Werkzeug** geprüft, nicht **bis zur
CLI**. Ein vollständiger Nachweis bräuchte einen echten Modell-Lauf; der
kostet Kontingent und lässt sich nachts nicht sinnvoll bewerten. Sollte der
Transport zwischen SDK und CLI brechen, zeigte es sich beim ersten echten
Sucheinsatz — laut, nicht still.

Ebenso ungeprüft: die **globale CLI** (`@anthropic-ai/claude-code` 2.1.209 auf
dem VPS). Sie gehört laut Auftrag in denselben Block, ist aber ein
npm-Eingriff mit root-Rechten — **das ist Adams Hand**, nicht meine.

## Vorschlag

**Der Sprung ist tragfähig, aber er bleibt eine Entscheidung.** Zwei Punkte
liegen bei Adam (siehe `ENTSCHEIDUNGEN-FUER-ADAM-2026-08-29.md`): ob auf
0.2.148 statt 0.2.144 gesprungen wird, und wann deployt wird.

Deshalb ist der **Pin nicht nachgezogen** und die Mac-venv nicht angehoben.
Der Klon bleibt stehen, bis entschieden ist — wieder aufgeräumt wird er mit
`git worktree remove ../probe-sdk`.
