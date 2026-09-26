**Zweck: BELEG + ENTSCHEID** · **Zu tun: Fenster für den SDK-Sprung setzen, wenn du willst — NACH Node, in getrennten Fenstern.**

<!-- ROLLE: befund-sdk-klonprobe -->
# Befund: SDK-Klonprobe 0.2.127 → 0.2.159 (D8, Adams Entscheid 8 vom 23.09.)

**Stichtag:** 24.09.2026, 02:3x · **überholt durch:** — · **maßgeblich ist diese Datei** für Fassung und Paarung; das Verfahren im Fenster steht weiter in `PRUEFLISTE-sdk-sprung.md`.

**Nenner:** ein Sprung (SDK), vier Nahtstellen gemessen, eine Reparatur gefunden. **Node ist nicht Teil dieser Probe:** Der Sprung betrifft das Systempaket auf dem VPS und braucht root; der Vollzugs-Zettel (`ZETTEL-node-22-auf-24.md`) steht, und dort ist gemessen, dass die CLI ohne Node läuft.

## Wie gemessen

Arbeitsbaum `../probe-sdk` mit **eigener** venv (Homebrew-Python 3.12), die gemeinsame Mac-Umgebung blieb unberührt. Erst die Grundlinie mit 0.2.127, dann der Sprung — damit sich SDK-Effekt und Mitzieher-Effekt trennen.

## Ergebnis

| | Wert |
|---|---|
| Grundlinie, SDK 0.2.127 in frischer Umgebung | 85/85 |
| **nach dem Sprung, SDK 0.2.159** | **85/85** |
| gebündelte CLI (abgelesen, `_bundled/claude --version`) | **2.1.281** (vorher 2.1.219) |
| `pip freeze`-Unterschied durch den Sprung | **genau eine Zeile**, das SDK |
| Paarung für den Pin (abgelesen) | `claude-agent-sdk==0.2.159` · `mcp==1.30.0` · `anyio==4.15.1` |

**Die Mitzieher-Drift ist schon da:** Eine frische Umgebung mit dem **alten** SDK 0.2.127 zieht heute `mcp` 1.30.0 und `anyio` 4.15.1 — auf dem VPS stehen andere Fassungen (29.08. gemessen: `mcp` 1.28.1). Genau dagegen stehen die drei Pins.

## Die Nahtstellen

1. **Suchserver über die neue In-Process-Brücke** (0.2.140 hat den Transport umgebaut): `initialize`, `tools/list` → `web_search`, `tools/call` erreicht das Werkzeug des Bots. Am Mac ohne SearxNG endet der Aufruf mit „Suche fehlgeschlagen" — erwartet. **Nicht messbar ohne Modellaufruf:** ob die CLI 2.1.281 den Namen weiter als `mcp__suche__web_search` bildet, an dem Kostenschranke und Freigabe hängen. **Im Fenster: eine echte Suche.**
2. **Freigabe-Rückruf:** Aufrufform unverändert (Werkzeugname, Eingabe, Kontext); der Kontext trägt dieselben Felder, die der Bot seit dem 28.08. mitschreibt.
3. **Sitzungsoptionen:** `hauptsitzungs_optionen` und `werkzeugfreie_optionen` bauen mit 0.2.159 ohne Fehler (Modell, `max_buffer_size` 32 MiB).
4. **Neuer Nachrichtentyp** (0.2.137, `ConversationResetMessage`): Der Antwortstrom prüft Typ für Typ ohne brechenden Sonst-Zweig — wird übergangen.

## Der Fund: das dritte Geschwister

**`is_session_limit` las nur `str(exc)`**, während Anmelde- und Kontextfehler seit dem 29.08. über `fehlertext_vollstaendig` auch die Nutzlast lesen. Ab 0.2.140 bildet `ResultError` seinen Text bevorzugt aus `errors[]`; steht das Limit dann nur in `result` oder allein als Status 429, **wäre die Kontingent-Rücklage (Rang A) blind gewesen** — eine Nachricht wäre nicht vorn in der Schlange geblieben. Ebenso las die Rücklage ihre Rückkehrzeit nur aus der Meldung.

**Repariert in `9667f08`, fassungsunabhängig** (gegen 0.2.127 gefahren, 85/85) — also **auch ohne den Sprung deploybar, und das empfehle ich**: Er schließt eine Lücke, die mit dem Sprung erst aufgeht, und schadet mit dem alten SDK nichts. **Ehrliche Grenze:** Der Prüfer misst die Erkennung und die Zeitlesung; dass die Aufrufstelle im Job-Lauf den vollständigen Text übergibt, ist gelesen, nicht ausgeführt.

## Änderungsnotizen 0.2.128 bis 0.2.159, was für uns zählt

- 0.2.140 `ResultError` (siehe Fund), In-Process-Transport über `mcp` (Nahtstelle 1), `can_use_tool` auch bei Zeichenketten-Prompts (für uns ohne Wirkung).
- 0.2.137 neuer Nachrichtentyp (Nahtstelle 4), neue Felder `origin`, `resume_session_at` — ungenutzt.
- 0.2.153 `snapshot` für Systemtext-Vorgaben — ungenutzt.
- 0.2.158 `verbatim_prompts` (Vorgabe aus) — ungenutzt.
- 0.2.129 strengere Prüfung von Skill-Namen — der Bot lehnt Skills ohnehin ab.

## Für das Fenster

Das Verfahren der Prüfliste gilt, mit dieser Paarung. Reihenfolge: **Node → SDK**, getrennt. Vor dem SDK: `9667f08` (kann früher allein gehen). Nach dem SDK: eine echte Suche (Nahtstelle 1) und der Pin-Kommentar ist bereits abgelesen eingetragen.
