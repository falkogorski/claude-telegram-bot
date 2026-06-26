# CLAUDE.md — Projekt-Notizen

## 💰💰💰 KOSTEN-REGEL — HÖCHSTE PRIORITÄT 💰💰💰

**IMMER vorher ausdrücklich warnen und um Bestätigung bitten, bevor irgendeine
Aktion zusätzliche Kosten verursachen könnte.** Keine Ausnahme. Vor allem alles,
was Nutzung auf die kostenpflichtige **Anthropic-API** (pay-per-token,
console.anthropic.com) verlagert, statt sie über das **Claude-Max-Abo** des
Nutzers laufen zu lassen.

### Hintergrund (zwei getrennte Geldtöpfe)
- **Max-Abo** (~100 €/Monat): Auth via OAuth / `claude login` /
  `CLAUDE_CODE_OAUTH_TOKEN`. Im Abo enthalten, **keine** Extra-Kosten.
- **API-Schlüssel** (`ANTHROPIC_API_KEY`): bucht **IMMER extra** ab,
  völlig getrennt vom Abo. Hat Vorrang vor OAuth, wenn gesetzt.

### Vorgaben des Nutzers
- Alles soll **möglichst über das Abo (kostenfrei)** laufen, solange es nicht
  „professionell/produktiv" wird.
- **Standard-Auth für diesen Bot: Abo-Token (`CLAUDE_CODE_OAUTH_TOKEN`),
  NICHT `ANTHROPIC_API_KEY`.**
- Bei jeder Änderung an Auth/Modell/Diensten zuerst prüfen: „Kostet das extra?
  Aus welchem Topf?" → wenn API-Topf: **vorher fragen.**

## Zusammenarbeit / Workflow (macOS, nicht-technischer Nutzer)

- **`pbpaste`-Befehle (Token/Key aus Zwischenablage):** Reihenfolge IMMER klar
  mitansagen → (1) Befehl ins Terminal einfügen **ohne** Enter, (2) **dann** den
  Token/Key kopieren (Doppelklick → `Cmd-C`), (3) **dann** Enter. Sonst
  überschreibt der eingefügte Befehl den Token in der Zwischenablage.
- **Ein Schritt pro Nachricht**, klar nummeriert. Kein `nano`/Hand-Editieren von
  Konfigdateien (zu fehleranfällig) — lieber per Befehl (`PlistBuddy` etc.).
- **Secrets nie in den Chat posten lassen** — vorher klipp und klar sagen.
