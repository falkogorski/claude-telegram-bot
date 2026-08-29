<!-- ROLLE: entscheidungsvorlage-modell-plattform-strategie -->
# Modell- und Plattform-Strategie — Entscheidungs-Bericht

**Erstellt:** 23.07.2026, Recherche-Sitzung „Modell-Plattform-Strategie" (Worktree, nur lesend im Repo)
**Auftrag:** Vier Fragen (A–D) recherchieren und rechnen — keine Entscheidung, nichts installiert, keine Kosten verursacht (Recherche ausschließlich über kostenfreies WebFetch; die kostenpflichtige WebSearch wurde nicht benutzt).
**Grundlagen gelesen:** `CLAUDE.md` (💰-Kostenregel), `blaupause-notizen.md`, `MIGRATION.md` (Phase 2, 9.6, 9.7), bestehender Hermes-Prüfbericht vom 23.07.
**Entscheidung:** Adam, mit Kontroll- und Migrations-Sitzung beim Phasen-Audit.

---

## Executive Summary

1. **Hermes (Frage A):** Das K.-o.-Kriterium bleibt bestehen — offiziell bindet Hermes Anthropic nur per bezahltem `ANTHROPIC_API_KEY` an. Es gibt zwar mehrere aktive Abo-Auth-Umbauten in der Community (Agent-SDK-Provider, `claude -p`-Backend), aber **keiner ist gemergt**, und Anthropic hat Abo-OAuth in Dritt-Tools seit April 2026 ausdrücklich verboten und technisch blockiert. Option A (Plattformwechsel) bleibt tot; Option B (Konzepte adaptieren) bestätigt.
2. **Neuer, wichtiger Nebenbefund:** Die AGB-Verschärfung vom Frühjahr 2026 berührt auch **unseren eigenen** Betrieb (Agent SDK + Abo-Token). Die offizielle Doku liest sich für den Einzelnutzer-Eigenbetrieb weiterhin verträglich, verbietet aber Drittanbieter-Routing — Einordnung und Absicherungs-Vorschlag in Abschnitt D.
3. **Alternativen (B):** „OpenAI-kompatibel" ist ein Formatstandard, keine Firmen-Bindung. Fünf Kandidaten geprüft (OpenClaw, Hermes, Letta, Agent Zero, Khoj) — **keiner** trägt unsere verifizierten Invarianten (Persistenz, Wächter, Pre-Send, Ampel) und keiner löst die Abo-Auth-Frage besser als unser jetziger Bau. Empfehlung: Plattform behalten, Muster klauen.
4. **Kosten (C):** Für unser Nutzungsprofil ist das **Max-Abo (~100 $/Monat) fast immer der günstigste Claude-Weg** — die API-Rechnung läge je nach Auslastung bei grob 40–1.100 $/Monat. Offene Modelle per Token (DeepSeek ≈ 7–90 $/Monat) sind 10- bis 15-mal billiger, aber qualitativ und datenschutzseitig kein Hauptagent-Ersatz. Für Neben-Inferenzen und Spezialistenmodelle lohnt **nie** ein Abo.
5. **Unabhängigkeit (D):** Realistisch heute: RAG/Memory + portable Struktur (haben wir) + dokumentierter Anbieter-Wechsel-Drill (fehlt als Übung). „Eigenes, sich weiterentwickelndes Modell" = heute Feintuning offener Modelle (zweistellig–dreistellig € pro Lauf, begrenzter Nutzen) — echtes Training bleibt Zukunftsmusik (Millionenbereich). Kernprinzip für die Blaupause: **Daten und Regeln sind portabel, Modellgewichte nicht.**

---

## A) Hermes Agent (Nous Research) — Tiefenprüfung

### A.1 Faktenlage Anbindung (Voll-Doku jetzt gelesen)

Die Konfigurations-Doku (`hermes-agent.nousresearch.com/docs/user-guide/configuration`) nennt als Provider: Nous Portal (OAuth), OpenRouter, OpenAI/Codex, **Anthropic via `ANTHROPIC_API_KEY`**, MiniMax, xAI Grok (OAuth für deren Abonnenten) sowie **beliebige OpenAI-kompatible Endpoints via `base_url`** — darüber laufen auch Ollama und lokale Modelle. Damit ist die Lücke des ersten Prüfberichts geschlossen: Die Anthropic-Anbindung ist offiziell der **bezahlte API-Key-Weg**, ein Abo-Weg existiert im offiziellen Funktionsumfang nicht.

### A.2 Inoffizielle Wege zum Abo-Zugang — ehrliche Bewertung

Die Issue-Lage zeigt, dass die Community genau daran arbeitet — es gibt **mindestens vier konkurrierende, allesamt ungemergte** Ansätze:

| Ansatz | Stand (23.07.2026) | Bewertung |
|---|---|---|
| PR #65982 — „claude-agent-sdk provider under subscription OAuth (fail-closed)" | offen; Maintainer-Review läuft, Grundsatzfrage (Core vs. Plugin) ungeklärt | Technisch sauberster Weg (offizielles SDK unter Hermes' eigener Schleife); nicht gemergt = bei jedem Update Bruchgefahr |
| PR #67335 — `claude -p`-CLI-Backend mit `CLAUDE_CODE_OAUTH_TOKEN` | offen (19.07.); Maintainer: „selection needed", konkurriert mit #40074/#56413 | Nutzt die offizielle CLI („first party") — derselbe Mechanismus wie unser Bot; als Fork-Pflege-Aufgabe dauerhaft |
| Credential-Pool mit `sk-ant-oat`-Tokens direkt gegen die API | teils gemergt, aber Bug-Meldungen („out of extra usage", HTTP 400) | **Genau der Weg, den Anthropic seit 04.04.2026 serverseitig blockiert** — instabil und AGB-widrig |

**AGB-Lage (Primärquelle, Claude-Code-Doku „Legal and compliance"):** OAuth-Auth ist „intended exclusively … to support ordinary use of Claude Code and other native Anthropic applications". Entwickler, die Produkte/Dienste bauen — „including those using the Agent SDK" — sollen API-Keys nutzen; Anthropic „does not permit third-party developers to … route requests through Free, Pro, or Max plan credentials **on behalf of their users**", Durchsetzung „without prior notice". Sekundärquellen dokumentieren die technische Durchsetzung ab 04.04.2026 (Blockade von OpenClaw, OpenCode u. a.; Kontosperrungen teils binnen Minuten). ⚠️ Einzelne Sekundärquellen zitieren einen schärferen Wortlaut („including the Agent SDK is not permitted") — diesen Satz habe ich in der Primärquelle so nicht gefunden; maßgeblich ist der oben zitierte Text.

**Konsequenz für Hermes:** Selbst wenn einer der PRs gemergt würde, wäre Hermes ein Dritt-Tool, das Abo-Zugang routet — die Konstellation, gegen die Anthropic aktiv vorgeht. Stabilität: abhängig von ungemergten PRs und einem Katz-und-Maus-Spiel. **AGB-Risiko: hoch (Kontosperrung möglich).** Das K.-o.-Kriterium 1 aus 9.7 greift damit doppelt: technisch (kein offizieller Abo-Weg) und rechtlich (verboten).

### A.3 Reifegrad, Community, Sicherheitslage (GitHub-API, hart gezählt)

- **Stars 219.225 · Forks 41.554 · offene Issues/PRs 24.870 · Watcher 835** — riesige, extrem aktive Community, aber die Issue-Zahl zeigt ein massives Triage-Problem.
- **Lizenz MIT, Sprache Python** — Fork-fähig und lesbar; gut für Konzept-Übernahme.
- **Repo angelegt 22.07.2025, letzter Push 23.07.2026, letztes Release v0.19.0 vom 20.07.2026.** ⚠️ Korrektur zum ersten Prüfbericht: Das Repo ist laut GitHub-API ein Jahr alt, nicht erst seit Februar 2026 (vermutlich war Februar der öffentliche Start; ungeprüft). Versionsnummer 0.x + hohe Release-Frequenz = API-Brüche wahrscheinlich.
- **Sicherheitslage:** Command-Approval und Container-Isolation vorhanden (Erstbericht); die OAuth-/Credential-Pool-Bugs zeigen aber eine noch unreife Auth-Schicht. Datenwege über Nous Portal/OpenRouter wären gegen unsere Ampel-Architektur zu prüfen — entfällt mit dem K.-o.

### A.4 Befund & Empfehlung A

**Befund:** Aussage bestätigt und verschärft — Anthropic ist in Hermes offiziell nur per bezahltem API-Key anbindbar; die Abo-Wege sind ungemergte Community-PRs mit hohem Stabilitäts- und AGB-Risiko. **Empfehlung: Option B beibehalten** (FTS5-Recall → 5.11, Playbook-Gedanke → 9.6, deterministische Memory-Kuratierung) und Hermes über den 5.21-Monitor beobachten — insbesondere, ob Anthropic je einen offiziellen Abo-Weg für Dritt-Frameworks öffnet (dann Neubewertung).

---

## B) Alternativen-Landkarte: selbst-hostbare Agent-Frameworks

### B.1 Vorab: Was „OpenAI-kompatibel" wirklich heißt

„OpenAI-kompatibel" bezeichnet den **Wire-Format-Standard** der `POST /v1/chat/completions`-Schnittstelle — de facto die lingua franca der Inferenz-Welt. Ollama, LiteLLM, vLLM, LM Studio und praktisch jeder Anbieter sprechen dieses Format. **Ein Framework, das „OpenAI-kompatible Endpoints" verlangt, bindet uns nicht an die Firma OpenAI** — unser Grundsatz „kein OpenAI im Stack" (2.5) bleibt vollständig wahrbar, indem der Endpoint auf Ollama/LiteLLM zeigt. Die eigentliche Sollbruchstelle ist eine andere: Der **Claude-Abo-Zugang** läuft *nicht* über dieses Standardformat, sondern nur über Claude Code / Agent SDK — deshalb ist „OpenAI-kompatibel als einziger Weg" gleichbedeutend mit „Claude nur gegen API-Geld" (K.-o.-Kriterium 9.7).

### B.2 Kandidaten im Kurzprofil (Metriken: GitHub-API, 23.07.2026)

| Kandidat | Stars | Lizenz | Telegram | Memory | Skills/Tools | MCP | Ollama/lokal | Community |
|---|---|---|---|---|---|---|---|---|
| **OpenClaw** (TypeScript, seit 11/2025) | 383.873 | „Other" ⚠️ prüfen | ✅ nativ (+ WhatsApp/Discord/Signal) | ✅ Markdown-Dateien | ✅ Skills | ✅ | ✅ (Ollama, LM Studio, vLLM u. a., 60+ Provider) | riesig |
| **Hermes Agent** (Python, MIT) | 219.225 | MIT | ✅ nativ | ✅ FTS5 + Kuratierung | ✅ (agentskills.io) | ✅ | ✅ via `base_url` | riesig, chaotisch |
| **Letta** (Python, seit 2023) | 23.925 | Apache-2.0 | ❌ (selbst bauen) | ✅✅ Kernkompetenz (MemGPT-Erbe, stateful) | ✅ | ✅ | ✅ | reif, fokussiert |
| **Khoj** (Python, seit 2021) | 35.940 | AGPL-3.0 ⚠️ | ❌ (WhatsApp/Web/Obsidian/Emacs) | ✅ (RAG/Second Brain) | teils (Automationen) | ungeprüft | ✅ | reif |
| **Agent Zero** (Python) | 18.493 | „NOASSERTION" ⚠️ prüfen | ❌ (Web-UI/Desktop) | ✅ (Konsolidierung, Snapshots) | ✅ | ✅ | via OpenAI-kompatibel (ungeprüft) | mittel |

**Einzeleinschätzungen:**

- **OpenClaw** ist konzeptionell der nächste Verwandte unseres Bots (persönlicher Assistent, Messenger-Gateways, Datei-Memory). Bemerkenswert: Es führt einen Provider **„Anthropic (API + Claude CLI)"** — der CLI-Modus fährt die offizielle `claude`-Binary, also denselben Mechanismus wie unser Agent SDK; der Gründer bezeichnete das nach dem April-Cut als den verbleibenden legitimen Weg. Gegenargumente: Sicherheitshistorie (Anfang 2026 massenhaft exponierte Instanzen dokumentiert), Lizenz laut GitHub-API nicht mehr als klare OSS-Lizenz ausgewiesen (prüfen!), TypeScript statt Python, und das Projekt stand im Zentrum des Anthropic-Enforcements.
- **Hermes** — siehe A; als Plattform K.-o., als Ideen-Steinbruch erstklassig.
- **Letta** ist der seriöseste Kandidat nach klassischen Kriterien (Apache-2.0, drei Jahre Reife, nur 49 offene Issues): eine **Memory-/Agent-Server-Schicht**, kein fertiger Telegram-Assistent. Für unsere Blaupause interessant als Referenzarchitektur für „stateful Memory als eigener Dienst" — ein Umstieg würde aber bedeuten, Telegram-Gateway, Ampel, Wächter usw. selbst dort hineinzubauen: gleicher Eigenbau, fremdes Fundament.
- **Khoj** ist ein „Second Brain" (Wissens-RAG) mit Assistent obendrauf — stark für Punkt „Buch des eigenen Schaffens", schwach als Steuerzentrale; kein Telegram; **AGPL** wäre bei späterer Kundenfähigkeit sorgfältig zu prüfen (Copyleft auch bei Netzwerknutzung).
- **Agent Zero** punktet mit Docker-Isolation und einem interessanten Memory-Design (Konsolidierung, „Time Travel"), hat aber kein Telegram-Gateway, eine unklare Lizenz-Auszeichnung und — bezeichnend — Claude-Code-Anbindung erst „in Planung", während Codex-OAuth schon da ist.
- **Bewusst Big-Tech-unabhängig ausgelegt** sind vor allem Khoj und Agent Zero (self-host-first, lokale Modelle als gleichwertige Bürger); OpenClaw und Hermes sind Provider-agnostisch, leben praktisch aber von den großen Anbietern.

### B.3 Befund & Empfehlung B

**Kein Kandidat besteht das K.-o.-Kriterium besser als unser Eigenbau:** Der Claude-Hauptagent über das Abo läuft nur im Claude-Code-/Agent-SDK-Ökosystem — genau dort sitzt unser Bot bereits. Alle Kandidaten würden bedeuten: verifizierte Invarianten (5.2-Persistenz, 5.18-Wächter, 8.5-Pre-Send, Ampel, Kostenregel) in fremden, schnell drehenden Code portieren. **Empfehlung:** Plattform behalten; für die Blaupause (9.6) je Kandidat das beste Muster notieren — OpenClaw: Messenger-Gateway-Abstraktion + Claude-CLI-Provider-Gedanke; Hermes: FTS5-Recall + Skill-Playbooks; Letta: Memory als eigenständige, versionierte Dienstschicht; Agent Zero: Container-Isolation des Werkzeug-Raums; Khoj: Wissens-RAG fürs „lebende Buch".

---

## C) Abo vs. Token — Modellrechnung für unser Profil

### C.1 Annahmen (offengelegt — bitte beim Audit gegenprüfen)

- **50–150 Anfragen/Tag**, 30 Tage/Monat → 1.500–4.500 Anfragen/Monat.
- Eine „Anfrage" an einen **Agenten** ist kein einzelner API-Call: Tool-Schleifen, Systemprompt und Verlauf werden je Turn mitgesendet. Ansatz pro Anfrage: **10.000–40.000 Input-Token** (inkl. Kontext/Tools, gemischt leicht/schwer) und **500–2.000 Output-Token**. Das ergibt **15–180 Mio. Input- und 0,75–9 Mio. Output-Token pro Monat**.
- Preise Claude (offizielle Referenz, Stand heute): Opus 4.8 **5/25 $**, Sonnet 5 **3/15 $** (Intro 2/10 $ bis 31.08.2026), Haiku 4.5 **1/5 $** je Mio. Input/Output; Prompt-Cache-Reads ≈ 0,1× Input; Batch −50 %. Max-Abo: **ab 100 $/Monat** (Adams Bestand: ~100 €).
- DeepSeek (offizielle Preisseite): V4-Pro **0,435/0,87 $**, V4-Flash **0,14/0,28 $** (Input Cache-Miss/Output je Mio.). Qwen/Llama über OpenRouter: Extraktion war unzuverlässig — Größenordnung „zwischen DeepSeek und Sonnet", **ungeprüft**.

### C.2 Monatskosten im Vergleich (gerundet, ohne/mit Cache)

| Weg | Untere Bande (50/Tag, leicht) | Obere Bande (150/Tag, schwer) |
|---|---|---|
| **Claude Max-Abo** | **~100 $ fix** | **~100 $ fix** (bis zur Abo-Grenze; 20x-Stufe ~200 $) |
| Claude API Opus 4.8 | ~94 $ (mit ~80 % Cache-Reads: ~40 $) | ~1.125 $ (mit Cache: ~480 $) |
| Claude API Sonnet 5 | ~56 $ (Cache: ~24 $) | ~675 $ (Cache: ~290 $) |
| Claude API Haiku 4.5 | ~19 $ | ~225 $ |
| DeepSeek V4-Pro | ~7 $ | ~86 $ |
| DeepSeek V4-Flash | ~2 $ | ~28 $ |
| Lokal (heutiger VPS, CPU) | 0 € — aber nur Kleinstmodelle (Phi-4-Mini-Klasse) | ungeeignet für Hauptagent |
| Lokal (eigene Hardware) | einmalig: gebrauchte 24-GB-GPU ~600–800 € **oder** Mac mit 64–128 GB RAM ~2.200–4.500 €; laufend Strom grob 10–30 €/Monat (**Schätzwerte, marktabhängig, ungeprüft**) | trägt 30B–120B-Klasse quantisiert — gut, aber nicht Claude-Niveau |

### C.3 Wann kippt die Rechnung?

1. **Abo vs. Claude-API:** Schon die untere Bande liegt in Opus-Qualität nahe am Abo-Preis, die obere weit darüber. **Für einen täglichen Agenten in Claude-Qualität ist das Abo praktisch immer der günstigste und planbarste Weg.** Die API gewinnt nur bei sehr geringer Nutzung (grob unter 20–30 leichten Anfragen/Tag ohne Tool-Schleifen — dann wären mit Haiku/Sonnet + Caching auch 10–40 $/Monat drin) oder wenn AGB/Skalierung sie erzwingen (Kundenbetrieb!).
2. **Claude vs. offene Modelle per Token:** Kostenseitig gewinnt DeepSeek/Qwen um Faktor 10–50. Die Rechnung kippt aber nicht über den Preis, sondern über **Qualität** (Agent-Zuverlässigkeit, Werkzeugführung, Deutsch) und **Datenschutz** (DeepSeek = chinesischer Anbieter; nach unserer Ampel allenfalls für grüne Neben-Inferenzen denkbar, und selbst das wäre ein bewusster Entscheid gegen die bisherige „lokal statt Cloud"-Linie von 2.4). 💰-Hinweis: Jede dieser Routen wäre eine neue Kostenquelle und braucht vor Einrichtung Adams Freigabe.
3. **Lokal:** Kippt erst mit eigener Hardware-Investition, und auch dann nur für Aufgaben unterhalb des Hauptagenten. Sinnvollster Zeitpunkt: wenn ein konkreter Bedarf (Rot-Inferenzen in besserer Qualität, TTS/STT, lange Zusammenfassungen) die Anschaffung rechtfertigt — nicht als Selbstzweck.
4. **„Mehrere spezialisierte Modelle parallel":** Für Neben-Rollen (Ampel-Klassifizierung, Labels, Kurz-Zusammenfassungen, Embeddings, Vision-Kleinkram) lohnt **niemals** ein eigenes Abo: Das Volumen je Rolle ist winzig, Abos bepreisen aber Dauerlast. Faustregel für die Blaupause: **Abo nur für das eine Arbeitspferd mit hohem Dauervolumen; alles Spezialisierte lokal (0 €), Free-Tier oder pay-per-token in Cent-Höhe** — Letzteres stets mit 💰-Freigabe. Genau so ist unser Stack heute schon gebaut (F1-Entscheid + Ollama).

---

## D) Unabhängigkeits-Roadmap

### D.1 Risiken der Ein-Anbieter-Abhängigkeit — konkret belegt

| Risiko | Beleg/Einordnung |
|---|---|
| **AGB-Änderung + Kontosperrung** | Real vorgeführt: Doku-Verschärfung Feb. 2026, technische Blockade von Dritt-Tools zum 04.04.2026, dokumentierte Sperrungen. **Betrifft uns indirekt:** Unser Bot fährt Agent SDK + Abo-Token — die Primärquelle deckt „ordinary, individual usage of Claude Code and the Agent SDK" über die Limit-Formulierung, verbietet aber Drittanbieter-Routing „on behalf of their users". Einzelnutzer-Eigenbetrieb über die offizielle CLI ist die verträglichste Lesart — **Restrisiko aber nicht null**, Durchsetzung „without prior notice". |
| **Preiserhöhung** | Max heißt inzwischen „**ab** 100 $"; API-Preise haben sich 2025/26 mehrfach bewegt. Kalkulation nie auf einen Preisstand festnageln. |
| **Modell-Abkündigung** | Anthropic führt belegte Retirement-Zyklen (~12–18 Monate je Modellgeneration). Unser 5.21-Monitor + „Modellwahl ist Konfiguration" fangen das ab. |
| **Werkzeug-Kopplung** | Agent-Fähigkeiten (Tools, Permissions, Sessions) sind ans Claude-Code-Ökosystem gebunden — der eigentliche Lock-in liegt weniger im Modell als im **Agent-Harness**. |

### D.2 Absicherungs-Stufen auf Basis des Bestands

**Stufe 0 — haben wir bereits:** lokales Ollama-Fallback (2.3), LiteLLM als Provider-Abstraktion der Neben-Inferenzen (2.6), SearxNG statt Anbieter-Suche (2.7), Git-Redundanz + Offline-Bundles (4.x), „Struktur über Namen", Modellwahl als Konfiguration, Blaupause-Sammlung. Das ist mehr, als die meisten Projekte je aufbauen.

**Stufe 1 — jetzt, kostenlos, gehört in die Blaupause:**
- **Notbetriebs-Drill:** einmal bewusst durchspielen (Testlauf), dass der Bot bei ausgefallenem Claude-Zugang auf „degradierten Modus" (lokales Modell, ehrliche Kennzeichnung) umschaltet — der Mechanismus existiert, die geprobte Prozedur nicht.
- **Rollenprofil „Hauptagent" modellneutral beschreiben:** Welche Fähigkeiten braucht die Rolle (Werkzeugaufrufe, Freigabe-Schleife, Streaming, Kontextgröße, Deutsch)? Damit wird jeder künftige Kandidat in Stunden statt Tagen prüfbar.
- **API-Key-Notweg dokumentieren, nicht aktivieren:** Falls der Abo-Weg je bricht, ist der geordnete Rückfall „Sonnet 5 + Caching + Spend-Limit per API-Key" — als beschriebene Prozedur mit 💰-Warnung, ohne dass ein Key im Stack liegt.
- **AGB-Wachposten:** Die Claude-Code-Legal-Seite in den 5.21-Monitor aufnehmen (Änderungen an der Auth-Passage = sofortige Meldung). Die ⚠️-Notiz in `CLAUDE.md` („AGB-Grenze ungeprüft, Quelle 14 Monate alt") kann die führende Sitzung mit dieser Recherche auf Stand 07/2026 heben.

**Stufe 2 — mittelfristig, je ein bewusster Entscheid:** Zweit-Cloud-Route für grüne Neben-Inferenzen über LiteLLM (Groq-Free bereits geprüft; DeepSeek/Qwen nur nach Datenschutz-Abwägung); stärkeres lokales Modell, sobald reale Aufgaben es verlangen.

**Stufe 3 — langfristig:** eigene Inferenz-Hardware (siehe C.2), wenn Rot-Aufgaben oder Kosten es tragen.

### D.3 „Eigenes, sich weiterentwickelndes Modell" — nüchtern

- **Training from scratch:** Zukunftsmusik. Selbst kleine brauchbare Modelle kosten im Training Rechenleistung im sechs- bis siebenstelligen Euro-Bereich plus Datenpipeline und Team — für uns auf Jahre irrelevant.
- **Feintuning offener Modelle (LoRA/QLoRA auf 7–14B):** heute machbar; ein Lauf auf gemieteten GPUs liegt grob im zweistelligen bis niedrigen dreistelligen Euro-Bereich (**Schätzwert, ungeprüft**). Realer Nutzen: Ton, Formate, feste Abläufe. Nicht erreichbar: mehr Intelligenz, aktuelles Wissen. Pflegelast: jedes Basismodell-Update erfordert neues Tuning.
- **Der ehrliche Befund:** Was Adam als „sich weiterentwickelndes Modell" anstrebt, bauen wir bereits — nur an der richtigen Stelle: **Die Weiterentwicklung liegt in Memory, Regeln, Playbooks und Logs (RAG statt Gewichte).** Diese Ebene ist modellportabel, versionierbar (Git) und überlebt jeden Anbieterwechsel; ins Modell eintrainiertes Verhalten ist all das nicht. Feintuning wird erst dann interessant, wenn eine klar umrissene, repetitive Rolle (z. B. der Coach-Klon mit festem Stil) auf einem lokalen Modell laufen soll.

---

## Entscheidungsoptionen fürs Phasen-Audit

| Option | Inhalt | Einschätzung |
|---|---|---|
| **Beibehalten** | Hauptagent auf Agent SDK + Abo; Hermes-Option B; Neben-Inferenzen lokal | Empfohlen — kein Kandidat und keine Kostenrechnung spricht für einen Wechsel |
| **Erweitern** (empfohlene Ergänzungen) | (1) AGB-Wachposten + aktualisierte AGB-Notiz in `CLAUDE.md`; (2) Notbetriebs-Drill einmal proben; (3) Rollenprofil „Hauptagent" + API-Key-Notweg in die Blaupause; (4) Muster-Übernahmen aus B.3 als Blaupause-Zeilen | geringer Aufwand, deutlicher Zugewinn an Unabhängigkeit |
| **Umbauen** | Plattformwechsel (Hermes/OpenClaw/Letta) oder Modellwechsel des Hauptagenten | Nicht empfohlen — K.-o.-Kriterium, Portierungsrisiko der verifizierten Bausteine, kein Kostenvorteil |

**Was JETZT in die Blaupause gehört, um alle Türen offen zu halten:** das Abo-Auth-K.-o.-Prüfprinzip (steht schon drin) · „Abo nur fürs Arbeitspferd, Spezialisten nie per Abo" (C.3) · modellneutrales Rollenprofil des Hauptagenten · gestufter Notbetrieb mit geprobtem Drill · „Daten und Regeln sind portabel, Gewichte nicht" · OpenAI-kompatibel = Formatstandard, nicht Firmenbindung.

---

## Quellen

1. Hermes Agent — Repo & Doku: `github.com/NousResearch/Hermes-Agent` · `hermes-agent.nousresearch.com/docs` (+ `/docs/user-guide/configuration`) · GitHub-API-Metriken 23.07.2026
2. Hermes Abo-Auth-PRs: `github.com/NousResearch/Hermes-Agent` — PR #65982, PR #67335 (dazu referenziert: #40074, #56413, Issues #65564, #65365, #63737/63738)
3. Anthropic (Primärquelle AGB): `code.claude.com/docs/en/legal-and-compliance` — Abschnitt „Authentication and credential use"
4. Enforcement/Einordnung (Sekundärquellen, teils widersprüchlich im Wortlaut): `openclaw.report/ecosystem/anthropic-bans-oauth-tokens-third-party-tools` · `kersai.com/anthropic-killed-third-party-claude-access-heres-every-workaround-that-still-works` · dev.to/thenewstack (Überschriften; Volltexte teils nicht abrufbar)
5. Alternativen (GitHub-API 23.07.2026 + Doku): `github.com/openclaw/openclaw` + `docs.openclaw.ai/providers` · `github.com/letta-ai/letta` · `github.com/frdel/agent-zero` (+ README) · `github.com/khoj-ai/khoj` + `docs.khoj.dev`
6. Preise: Claude-Modellpreise aus der offiziellen API-Referenz (Skill-Dokumentation Anthropic, Cache-Stand 06/2026) · `claude.com/pricing` (Abo-Pläne) · `api-docs.deepseek.com/quick_start/pricing` (V4-Flash/V4-Pro)
7. Als **ungeprüft** gekennzeichnet: OpenRouter-Preise für Qwen/Llama (Extraktion unzuverlässig), Hardware-/Strom-/Feintuning-Kosten (Marktschätzungen), Hermes-Start „Februar 2026".
