# CLAUDE.md — Projekt-Notizen

## 🗺️ MIGRATION — Status & Drehbuch

- **Das verbindliche Drehbuch ist `MIGRATION.md` (MASTER, zusammengeführt
  2026-07-12):** die 11-Phasen-Struktur aus der Telegram-Sitzung (Netcup-VPS,
  Status/Akzeptanz/Test/Adam-Bestätigung pro Punkt, sequenziell) + Phase 0
  (Code-/Repo-Vorbereitung), Anhang D (Ausführungsbefehle) und
  Kostenregel-Wächter aus dieser Sitzung. Die Repo-Version ist die Hoheits-
  Fassung; die Telegram-Sitzung übernimmt sie als Arbeitsdokument (Punkt 0.8).
- **Entscheidungen E1–E4 und F1 bestätigt** (Kasten in MIGRATION.md). F1:
  LiteLLM nur für Neben-Inferenzen (Ollama/Groq); der Claude-Agent bleibt
  direkt am Abo-SDK — keine Anthropic-Route in LiteLLM (Kostenregel!).
  Server-Zugangsdaten werden in Punkt 1.0 übermittelt/verifiziert.
- Wichtigste Stolperfallen: echte bot.py (~2000+ Zeilen) noch NICHT im Repo
  (Punkt 0.1, KRITISCH — Repo-Version ist veraltet); iCloud-Log-Pfad existiert
  auf Linux nicht (0.5); nie zwei Bot-Instanzen parallel; Webhook-Setzen (1.9)
  IST der Umschaltmoment; Auth NUR per Abo-Token (Kostenregel unten).
- Erledigt vorab: 401-Handling-Referenz + Abo-Token-first-Doku auf Branch
  `claude/telegram-bot-auth-401-g6yqrr`.
- Wichtigste Stolperfallen (Details im Drehbuch): echte bot.py (~2000+ Zeilen)
  liegt noch NICHT im Repo (Phase 0.1); iCloud-Log-Pfad existiert auf Linux
  nicht (Phase 1.3); nie zwei Bot-Instanzen parallel (Telegram-Conflict);
  Auth NUR per Abo-Token (Kostenregel unten).
- Erledigt vorab: 401-Handling-Referenz + Abo-Token-first-Doku liegen auf
  Branch `claude/telegram-bot-auth-401-g6yqrr`.

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
- **Shell ist `zsh`:** KEINE `#`-Kommentarzeilen in Befehlsblöcken — zsh führt
  `#` interaktiv als Befehl aus („command not found: #"). Nur reine Befehle
  geben, Erklärungen außerhalb des Code-Blocks.

## Remote-/Mobil-Weiterführung von Sitzungen (WICHTIG)

- Nutzer startet oft Prozesse, die Berechtigungen/Bestätigungen brauchen, muss
  dann weg → Prozesse stocken. Ziel: Sitzungen/Prozesse **von unterwegs
  fortsetzen** und **Freigaben erteilen** können.
- **Bereits möglich:** (a) Aufgaben, die **über den Telegram-Bot** laufen,
  schicken Permission-Prompts als Inline-Buttons (Allow/Deny/Always allow) aufs
  Handy — „Always allow <Tool>" verhindert wiederholtes Nachfragen. (b)
  Claude-Code-**Web**-Sitzungen lassen sich über die **Claude-App** (iPhone)
  fortsetzen — auch diese hier.
- **Wunsch (größere Sache, ggf. Migration):** Permission-Freigaben **beliebiger**
  Sitzungen gebündelt in den Telegram-Bot leiten, mit Sitzungs-Kennung, sodass
  alles per Telegram-Button freigegeben werden kann.

## Bot-Verhalten (bei Migration in `bot.py` einbauen)

- Der Telegram-Bot darf **nicht annehmen, in welchem Kontext der Nutzer gerade
  sitzt** (z. B. „schön, dich am Desktop zu sehen"). Der Nutzer ist parallel an
  mehreren Geräten/Sitzungen; eine solche Annahme ist irreführend. Begrüßungen
  und Antworten **neutral** halten. Umsetzung: kurzer Zusatz im System-Prompt
  des Bots (`bot.py`, `ClaudeAgentOptions`), z. B. „Du bist ein Telegram-Bot;
  nimm nicht an, wo oder an welchem Gerät der Nutzer sitzt."
