<!-- ROLLE: entscheidungsvorlage-hermes -->
# 9.7 Hermes Agent (Nous Research) — Prüfbericht als Entscheidungsvorlage

**Erstellt:** 23.07.2026, autonomer Lauf (nur Bericht — keine Entscheidung, keine Installation)
**Quellen:** GitHub-Repo `NousResearch/Hermes-Agent` (README + Projektseite, 2 Abrufe 23.07.).
⚠️ Die Voll-Doku (`hermes-agent.nousresearch.com/docs`) konnte nicht gegengelesen werden;
Zahlenangaben stammen aus LLM-Zusammenfassungen einzelner Abrufe und sind als
**ungeprüft** zu behandeln (Lehre „Zahlen-Anker deterministisch zählen").

## K.-o.-Kriterium 1: Bleibt der Claude-Hauptagent auf dem Abo-SDK? → **NEIN, nach aktueller Faktenlage**

- Hermes bindet Modelle über **Provider-Endpoints** an: Nous Portal, OpenRouter,
  OpenAI, „Anthropic", eigene Endpoints. Die Anthropic-Anbindung ist damit der
  klassische **API-Key-Weg (`ANTHROPIC_API_KEY`, pay-per-token)** — in keiner
  gesichteten Quelle findet sich ein Hinweis auf Claude-**Abo**-Auth
  (`CLAUDE_CODE_OAUTH_TOKEN` / Claude Agent SDK). Der Abo-OAuth-Weg existiert
  nach allem, was bekannt ist, nur im Claude-Code-/Agent-SDK-Ökosystem.
- **Konsequenz (💰-Kostenregel):** Liefe unsere Haupt-Inferenz über Hermes,
  würde JEDE Nachricht bezahlte API-Tokens kosten — die rote Linie.
  **Option A (Plattformwechsel zu Hermes) ist damit tot**, solange kein
  Abo-SDK-Adapter existiert. (Rest-Unsicherheit: Voll-Doku ungelesen; sollte
  dort wider Erwarten ein Claude-Code-Backend auftauchen, wäre neu zu bewerten.)

## Weitere Prüfpunkte (nachrangig, da K.-o. bereits greift)

| Kriterium | Befund | Einordnung |
|---|---|---|
| Reifegrad/Community | Sehr hohe Aktivität laut Projektseite (Stars/Forks/Releases — Zahlen ungeprüft); Projekt jung (seit Feb. 2026), schnelle Release-Folge | Lebendig, aber jung — API-Brüche wahrscheinlich |
| Lizenz | MIT | unkritisch, erlaubt Konzept-Übernahme |
| Funktionsumfang | TUI + Gateway (Telegram/Discord/…), FTS5-Session-Suche, Skill-System mit Selbstverbesserung, Cron-Scheduler, MCP, 40+ Tools | Überschneidet sich stark mit unserem Bau (5.2/5.18/5.23/8.5 …) |
| Portierungsaufwand | Unsere verifizierten Bausteine (Persistenz, Wächter, Pre-Send, Ampel, Kostenregel) müssten in ein fremdes, sich schnell änderndes Framework portiert werden | Hoch; Verlust der bewiesenen Invarianten |
| Sicherheits-/Datenschutz-Passung | Command-Approval + Container-Isolation vorhanden; aber Datenwege über Nous Portal/OpenRouter widersprächen der Ampel-Architektur ohne Prüfung | Eigenprüfung nötig, entfällt mit K.-o. |
| ⚠️ Cron-Scheduler | Zeitgesteuerte Modell-Aufrufe kollidieren mit der AGB-Leitplanke (CLAUDE.md) — beim Abo ohnehin tabu | bestätigt unsere Regel |

## Empfehlung (Entscheid bleibt bei Adam, beim Phasen-Audit)

**Option B — Konzepte adaptieren, Plattform behalten.** Konkret lohnend:
1. **FTS5-Volltextsuche über Session-Logs** → deckt sich mit 5.11 (Recall-Index); die Tagesdateien + Log-Repo sind die fertige Datenbasis.
2. **Skill-/Playbook-Gedanke** („aus Erfahrung wiederverwendbare Abläufe machen") → passt zu 9.6-Blaupause und künftigen Routinen — bei uns als Markdown-Playbooks, nicht als Code-Selbstmodifikation.
3. **Memory-Nudges** (periodische Kuratierung) → Anregung für die bestehende Memory-Pflege, deterministisch statt zeitgesteuert-modellgetrieben (AGB!).
Option C (verwerfen) wäre unnötig hart — als Ideen-Steinbruch ist das Projekt wertvoll; Beobachtung über den 5.21-Monitor genügt.
