<!-- ROLLE: entscheidungsvorlage-rotes-team -->
# Rotes Team: Wo irren wir? — Prüfbericht gegen die eigene Architektur

**Erstellt:** 23.07.2026, unabhängige Prüf-Sitzung mit Widerspruchs-Auftrag (Worktree, nur lesend im Repo)
**Auftrag:** Aktiv nach Gründen suchen, warum unsere Architektur ein Fehler sein könnte. Vier Prüffragen (A–D), Risiko-Register, ehrliches Gesamturteil. Keine Entscheidung — Vorlage für Adam + Kontrollsitzung.
**Methode:** Ausschließlich kostenfreie Recherche (WebFetch; keine WebSearch). Primärquellen wo möglich (GitHub-API, offizielle Changelogs/Doku), Sekundärquellen gekennzeichnet. **Alles als „ungeprüft" Markierte bitte nicht als Fakt weiterverwenden.**
**Frische-Check:** `CLAUDE.md` wurde heute 15:40 von der führenden Sitzung aktualisiert (9.7 ruht bis Audit; Gruppen-/Topic-Vorlage) — kein Widerspruch zu diesem Auftrag.

---

## Gesamturteil vorab

**Sackgasse: NEIN — unter drei Bedingungen.** Die Architektur ist kein Sonderweg, sondern ein etabliertes Community-Muster, das wir überdurchschnittlich robust ausgebaut haben. Die drei Bedingungen: (1) Die **Auth-/Limit-Flanke** (AGB-Grauzone, Token-Ablauf, Limit-Volatilität) wird aktiv überwacht statt nur ertragen; (2) **Updates des Fundaments** (Claude-Code-CLI) laufen kontrolliert (Pinning + Testfenster), nicht automatisch; (3) **Kundenfähigkeit** wird als Klon-pro-Kunde mit API-Backend gedacht, nie als Multi-Tenant-Umbau des Einzelnutzer-Bots. Details und Top-3-Maßnahmen am Ende.

---

## A) „Warum baut das sonst kaum jemand so?" — stimmt die Prämisse überhaupt?

### A.1 Befund: Die Prämisse ist falsch — es ist eine lebendige Nische

Die GitHub-Suche zeigt ein etabliertes Muster „Claude Code/Agent SDK + Telegram, Einzelnutzer, eigener Server" (Metriken GitHub-API, 23.07.2026):

| Projekt | Sterne | Stand | Muster |
|---|---|---|---|
| RichardAtCT/**claude-code-telegram** | 2.737 | aktiv (Push 03/2026) | Python, Remote-Zugriff auf Claude Code — engster Verwandter unseres Bots |
| op7418/**Claude-to-IM-skill** | 2.826 | aktiv | Claude → Messenger-Brücken (mehrere Plattformen) |
| hanxiao/**claudecode-telegram** | 606 | ruhend seit 01/2026 | Minimal-Bridge |
| **claude-telegram-relay** | 328 | ein Monat Aktivität (02/2026) | „always-on"-Muster-Demo |
| **claudeclaw** | 160 | aktiv | „Claude Code CLI als persönlicher Telegram-Bot — Voice, Memory, geplante Tasks" (fast unser Funktionsumfang) |

Dazu OpenClaw (383.873 Sterne) als Massenphänomen derselben Idee. **Rote-Team-Schluss:** Wir irren nicht durch Exotik. Die richtige Frage ist nicht „warum baut das niemand", sondern „woran leiden die, die es bauen".

### A.2 Strukturelle Gründe, die uns NICHT treffen (entwarnt)

1. **Produkte-für-viele dürfen kein Abo-Routing** (AGB, seit 04.04.2026 auch technisch blockiert) — deshalb baut kein kommerzielles Produkt auf Max-OAuth. Wir sind Einzelnutzer-Eigenbetrieb über die offizielle CLI unterm SDK; die Abo-Limits sind laut offizieller Doku ausdrücklich für „ordinary, individual usage of Claude Code and the Agent SDK" ausgelegt.
2. **Firmen brauchen Multi-Tenant, Compliance, SLAs** — Anforderungen, die wir nicht haben und nicht bezahlen müssen.
3. **Die meisten Bastler scheuen den 24/7-Betrieb.** Wörtlich aus der Community: „the agent works great when you're watching it. But the moment you close your laptop … it stops." Viele Projekte bleiben Laptop-Demos und schlafen nach Wochen ein (siehe hanxiao, relay). Unser VPS-Betrieb mit Wächtern ist genau die Antwort darauf.

### A.3 Gründe, die uns SEHR WOHL treffen (dokumentierte Schmerzen der Szene)

Aus den offenen Issues der zwei größten Vergleichsprojekte (Rohdaten in Quellen):

| Schmerz der Szene | Beleg | Bei uns |
|---|---|---|
| Daemon-/Dienst-Stabilität ist Problemklasse Nr. 1 | Claude-to-IM: 4 von 12 Issues zu launchd/Daemon-Start | gelöst-robust (Guardian + 5.18-Wächter, systemd geplant) |
| Geplante Jobs verpasst, wenn der Bot beschäftigt ist | claude-code-telegram #174, #175 | trifft uns bei Phase 7 (Erinnerungskanal) — **Merker für 7.2: Scheduler vom Agenten entkoppeln** |
| Falsche „fertig"-Meldungen / Timeouts | #172 | adressiert (Zustellnachweis, 8.5 Pre-Send) |
| Sessions nicht wiederaufnehmbar | #149 | adressiert (5.2 Persistenz + Recall) |
| Telegram-Chunking zerreißt Inhalte | #186 | gelöst (Splitter + Heading-Regel) |
| Einzel-Maintainer-Verwaisung ist der Normalfall | ruhende Repos oben | **trifft uns**: Bus-Faktor 1 (Adam+Claude). Gegenmittel Blaupause/WIEDERANLAUF existiert, ersetzt aber keinen zweiten Menschen |
| Kosten-Überraschungen (API-Nutzer): Cache-Bugs sollen Token-Rechnungen 10–20× aufgebläht haben (Sekundärquelle, **ungeprüft**) | Limit-Recherche | trifft uns kaum — Abo-Festpreis schützt; relevant erst für API-Klienten-Klone (Spend-Limits setzen!) |

---

## B) Technische blinde Flecken des Fundaments

### B.1 Claude Code / Agent SDK im Dauerbetrieb — die Changelog-Autopsie

Analyse der offiziellen Versionshistorie (2.1.x, 2025–2026) nach Dauerbetriebs-Bugklassen — das ist unser Fundament, und es bewegt sich schnell:

| Bugklasse | Beispiele (Version) | Relevanz für uns |
|---|---|---|
| **OAuth-/Auth-Staleness** — kehrt „alle 2–3 Releases" wieder | Auto-Mode verweigert nach Token-Rotation (2.1.216); Hintergrund-Sessions unbrauchbar bei stale Token (2.1.203); Sammel-Logout nach Wake (2.1.211) | **hoch** — genau unser Betriebsmodus (Daemon, langlebiger Setup-Token). 5.20 (Token-Frühwarner) ist noch nicht gebaut |
| **Memory-Leaks in Langzeit-Sessions** | MCP-stderr wächst auf 64 MB je Server (2.1.208, „30+ day sessions"); Tool-Result-Payloads quadratisch im Headless (2.1.208) | **hoch** — wir fahren MCP (SearxNG-Suche) im Dauerbetrieb; Prozess-Neustart-Hygiene nötig |
| **Session-Resume-Korruption** | Resume-TypeErrors, defekte Transkripte (2.1.214–217); Daemon löscht Socket des Nachfolgers (2.1.211) | mittel — 5.18-Wächter fängt Symptome, heilt aber keine korrupten Transkripte |
| **Compaction-Ausfälle** | /compact stallt nach Uhr-Sprung (2.1.206); Auto-Compact triggert nicht (2.1.217) | mittel — 5.24 (Rotation bei 80 %) ist die richtige eigene Antwort, noch offen |
| **Breaking Changes in Konfig/Verhalten** | settings-Auflösung geändert (2.1.207), Permission-Regel-Semantik `dir/**` geändert (2.1.214), Tool-Entfernungen (2.1.178) | **hoch** — ein unbedachtes CLI-Update kann Permissions/Hooks still umdeuten |

**Rote-Team-Schluss:** Unser Fundament ist ein wöchentlich release-tes Produkt mit dokumentierten Verhaltensänderungen. **Ungeprüft, ob die CLI-Version auf dem VPS gepinnt ist** — falls Auto-Update: das ist unsere größte stille Bruchstelle.

### B.2 Abo-Limits: dreimal Richtungswechsel in zehn Monaten

Zeitlinie (Sekundärquellen, im Detail **ungeprüft**): 08/2025 Einführung Wochenlimits (Backlash), 27.03.2026 Peak-Hour-Drosselung (13–19 Uhr UTC schnellerer Verbrauch), 06.05.2026 Rücknahme + Verdopplung der 5-Stunden-Limits. **Schluss:** Die Geschäftsgrundlage „Abo-Kontingent" ist volatil — planbar ist nur, dass sie sich ändert. Wir haben dafür heute **keine Sichtbarkeit** (kein Limit-/Verbrauchs-Monitor im Bot) und keinen definierten Degradations-Pfad („bei Drosselung → Sonnet/kürzere Kontexte/lokal").

### B.3 Modell-Abkündigungen

Belegte Retirement-Zyklen von ~12–18 Monaten je Modellgeneration (offizielle Tabelle). Abgesichert durch 5.21-Monitor + „Modellwahl ist Konfiguration" — sofern 5.21 gebaut wird.

### B.4 Telegram-Plattformrisiken (offizielle Bot-FAQ)

| Limit | Wert | Trifft uns |
|---|---|---|
| Nachrichten pro Chat | ~1/Sekunde, Bursts → 429 | **ja** — unsere Streaming-Edits und TTS+Text-Doppel senden schnell hintereinander; 429-Handling/Backoff prüfen (**ungeprüft**, ob implementiert) |
| Nachrichten pro Gruppe | 20/Minute | **ja, künftig** — Phase 6 (Kanal-Routing) + Phase 7 (Erinnerungskanal) schreiben in Gruppen/Topics; Ratenplanung nötig |
| Datei-Download durch Bot | **20 MB** | **ja** — große PDFs/Videos von Adam schlagen fehl. Bekannter Ausweg: selbst gehosteter Bot-API-Server (bis 2 GB; Aufwand mittel, **ungeprüft**) |
| Datei-Upload durch Bot | 50 MB | selten relevant (lange TTS/Videos) |
| Sperr-Praxis | FAQ nennt keine Kriterien | Restunsicherheit; ein privater Ein-Personen-Bot ist untypisches Ziel (Einschätzung, **ungeprüft**). Absicherung = Zweitinterface (3.2 Matrix, geplant) |

---

## C) Betriebs- und Sicherheitsrisiken der Bauform

### C.1 Anatomie des OpenClaw-Vorfalls — sind wir strukturell gefeit oder zufällig?

Ursachenkette laut Berichten (Zahlen variieren stark, 15.000–40.000+ exponierte Instanzen; **ungeprüft**): (1) **öffentlich erreichbare Web-Control-Panels ohne Authentifizierung** — ein Deployment-/Default-Problem, kein Kern-Bug; (2) zusätzlich eine echte Schwachstelle (CVE-2026-25253); (3) **bösartige Erweiterungen im Skill-Store**. Geleakt: API-Keys, Chat-Historien, volle Systemzugriffe.

**Strukturvergleich mit uns:**

| OpenClaw-Ursache | Bei uns | Urteil |
|---|---|---|
| Öffentliches Web-Panel | existiert nicht; Zugang nur über Telegram-Auth + `ALLOWED_USER_IDS`; ufw lässt nur Port 22 | **strukturell gefeit** |
| Skill-Store / fremde Erweiterungen | existiert nicht; Code kommt nur aus unserem Repo, Deploys nur per `git pull` durch Adam (8.7) | **strukturell gefeit** |
| Kern-CVE | eigener, kleiner Code statt Masse-Framework — weniger Angriffsfläche, aber auch weniger fremde Augen | neutral |

**Aber — zwei kommende Punkte würden genau die OpenClaw-Falle nachbauen:**
1. **1.9 Webhook-Umstellung** öffnet erstmals Port 443. Auflagen gehören ins Drehbuch: Telegram-`secret_token`-Prüfung, Pfad nicht erratbar, idealerweise Firewall auf Telegram-Netzbereiche.
2. **3.1 LobeChat-PWA** wäre exakt ein Web-Control-Panel auf dem VPS. Wenn es kommt: **nie öffentlich** — nur via VPN/SSH-Tunnel oder mit harter Auth davor. Diese Auflage sollte als roter Vermerk an 3.1.

### C.2 Ein Agent mit Shell auf dem eigenen Server

Der Bot führt als `claudebot` Werkzeuge inklusive Bash aus. Unsere 5.25-Schranken (Herkunfts-Schranke, Klartext-Werkzeugspur, Geheimnis-Schutz) und die Ampel sind gute **Erkennungs- und Autorisierungs**-Schichten — aber die Kette „präparierte Webseite → Agent lässt sich zu erlaubten, schädlichen Aktionen überreden" bleibt prinzipiell offen; die Werkzeugspur macht sie sichtbar, nicht unmöglich. Es gibt **keine Container-/Sandbox-Isolation** (anders als Agent Zero/Hermes-Container). Billige Härtung vorhanden, aber ungenutzt: systemd-Sandboxing (`NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `ReadWritePaths` nur auf Arbeitsverzeichnisse) würde den Schadensradius eines übernommenen Agenten deutlich begrenzen. **Status: OFFEN.**

### C.3 Langzeit-Degradation

Memory-/Log-Wachstum ist adressiert (5.23 Kontext-Diät, 4.2-Rotation, 5.24 geplant). Neu aus B.1: Die **Prozess-Ebene** degradiert auch (MCP-stderr-Leak, Session-Alterung). Billige Hygiene: geplanter nächtlicher Prozess-Neustart im 4-Uhr-Fenster (verträgt sich mit der „kein Neustart in Abwesenheit ohne Not"-Regel, wenn er ins Check-Fenster fällt und die Startmeldung unterdrückt/gebündelt wird).

### C.4 Einzel-VPS als Single Point of Failure

Abgesichert: tägliches Backup mit Restore-Probe (4.1), switch-fähig Richtung Mac, Rollback-Pfad (1.12), Offline-Bundles. **Offen:** Der Umschalt-Drill wurde nie unter realistischen Bedingungen geprobt (Wiederanlaufzeit unbekannt), und Telegram bleibt als Interface-SPOF bis 3.2 (Matrix) existiert.

---

## D) Sackgassen-Check nach vorn

Bewertung: Welche heutige Entscheidung wäre bei den Zielen (Blaupause, Klienten-Klone per API, Multi-Interface, spätere Skalierung) am teuersten zu korrigieren — und was kostet die Vorbeugung heute?

| Bauentscheidung heute | Teuer bei Ziel … | Späterer Umbau | Billige Maßnahme JETZT |
|---|---|---|---|
| Telegram-spezifische UX (Inline-Buttons, Reaktions-Vokabular, Topics) | Multi-Interface (Matrix, Web) | hoch — UX-Logik quer durch bot.py | Blaupause-Linie „Bedürfnis statt Telegram-Lösung" konsequent halten (existiert); im Code die Gateway-Grenze sauber am **einen Sendepfad** (5.8) festmachen — neue Features nie an Telegram-Objekten vorbei bauen |
| Einzelnutzer-Annahmen (globale Prefs, `ALLOWED_USER_IDS`, ein Memory) | Klienten-Klone / Mehrbenutzer | hoch, WENN Multi-Tenant | **Grundsatzentscheid dokumentieren: Klon-pro-Kunde** (eigener Prozess, eigener Bot-Token, API-Backend, eigene Ablage — Fanpost-Muster). Dann ist Einzelnutzer-Design keine Sackgasse, sondern die Blaupausen-Einheit. Zusätzlich: keine NEUEN globalen Singletons; `user_id` in neuen Funktionen als Parameter führen |
| Hauptagent fest auf Abo-OAuth | Kundenfähigkeit (AGB: API-Pflicht) + AGB-Restrisiko | mittel | Backend-Schalter nach Fanpost-Vorbild (`abo\|api` per env) als vorgesehene Sollbruchstelle einplanen — dokumentieren reicht zunächst, kein Umbau |
| `bot.py`-Monolith (~3.900 Zeilen) ohne Regressions-Netz | jede größere Änderung, Aufräumpass 8.4 | wächst mit jeder Woche | **8.2-Minimalnetz vorziehen** (die schon verankerten Selbstchecks als abrufbarer Testlauf bündeln), erst danach modular schneiden |
| Dateibasierte Ablage (Memory/Logs/TOML statt DB) | Skalierung >1 Nutzer | mittel | keine — für Einzelnutzer korrekt; die Blaupause beschreibt das Muster, nicht die Datei |
| CLI-Version ungepinnt? (**ungeprüft**) | Dauerbetrieb | — | Pinning + bewusstes Update-Fenster mit Regressionstest (siehe B.1) |

---

## Risiko-Register

**Legende:** W = Eintrittswahrscheinlichkeit, S = Schadenshöhe (gering/mittel/hoch); „GM?" = Gegenmaßnahme vorhanden.

### I. Strukturell entwarnt

| Risiko | W | S | Trifft uns … | GM? | Empfehlung |
|---|---|---|---|---|---|
| „Niemand baut das" = versteckter Konstruktionsfehler | — | — | **nicht**: lebendige Nische (2.700+-Sterne-Projekte, gleiches Muster) | — | keine |
| Abo-Routing-Verbot für Produkte | gering | hoch | **nicht direkt**: Einzelnutzer-Eigenbetrieb, offizielle CLI; Verbot zielt auf Drittanbieter-Produkte | teils | AGB-Wachposten (s. Bericht Strategie D.2) |
| OpenClaw-Klasse „offenes Web-Panel + Skill-Store" | gering | hoch | **nicht**: kein Panel, kein Store, Governance 8.7 | ✅ | Auflagen für 1.9/3.1 (s. III) |
| Kosten-Explosion durch API-Cache-Bugs | gering | mittel | **nicht**: Abo-Festpreis | ✅ | erst bei API-Klonen: Spend-Limits |

### II. Real, aber abgesichert

| Risiko | W | S | Trifft uns weil … | GM? | Empfehlung |
|---|---|---|---|---|---|
| Nachrichtenverlust bei Absturz | mittel | mittel | Daemon-Betrieb | ✅ 5.2 Persistenz + Queue | Beibehalten; 8.2 testet es |
| Session-Tod / Zombie-Agent | mittel | mittel | dokumentierte Bugklasse im Fundament | ✅ 5.18 Zwei-Ebenen-Wächter | Beibehalten |
| VPS-Totalausfall | gering | hoch | Einzel-Server | ✅ 4.1 Backup + Restore-Probe, switch-fähig | **Umschalt-Drill einmal proben** (Wiederanlaufzeit messen) |
| Modell-Abkündigung | hoch (zyklisch) | gering | Anbieter-Zyklen 12–18 Monate | ✅ Modellwahl=Konfig; 5.21 geplant | 5.21 wie geplant |
| Telegram-Zeichenlimit/Chunking | hoch | gering | 4096-Zeichen-Limit | ✅ Splitter + Heading-Regel | keine |
| Prompt-Injection über gelesene Inhalte | mittel | hoch | Agent liest Web/Mails | teils: 5.25-Schranken, Ampel, Werkzeugspur | Rest-Risiko in III (Sandbox) |

### III. Real und OFFEN

| Risiko | W | S | Trifft uns weil … | GM? | Empfohlene Maßnahme |
|---|---|---|---|---|---|
| **OAuth-/Token-Staleness im Daemon** (Bugklasse kehrt wieder; Setup-Token läuft jährlich ab) | hoch | mittel | langlebiger Token + Hintergrundbetrieb = exakt die dokumentierte Bruchstelle | ❌ (5.20 nur geplant) | **5.20 vorziehen**: Ablauf-Frühwarner + definierter Re-Auth-Ablauf; Verhalten bei Token-Rotation einmal testen |
| **Unkontrollierte CLI-Updates / Breaking Changes** | mittel | hoch | wöchentliche Releases, dokumentierte Semantik-Änderungen (Permissions, Settings) | ❓ ungeprüft ob gepinnt | Version pinnen; Update nur im Wartungsfenster nach 8.2-Minimaltest |
| **Abo-Limit-Volatilität / Drosselung** | mittel | mittel | drei Kurswechsel in zehn Monaten | ❌ | Verbrauchs-/Limit-Sichtbarkeit in den Bot (Statuszeile), definierter Degradations-Pfad (Sonnet/lokal), sonst: akzeptieren |
| **Kein Sandboxing des Agenten-Prozesses** | gering–mittel | hoch | Shell-Werkzeuge auf dem Produktiv-VPS; Injection-Restrisiko | ❌ | systemd-Härtung der Unit (NoNewPrivileges, ProtectSystem=strict, ReadWritePaths); später Container erwägen |
| **1.9 Webhook öffnet Port 443** | (bei Umsetzung) | hoch | erste öffentliche Angriffsfläche | ❌ (noch nicht im Drehbuch) | Auflagen in 1.9: `secret_token`, unerratbarer Pfad, Firewall-Eingrenzung |
| **3.1 LobeChat = potenzielles OpenClaw-Panel** | (bei Umsetzung) | hoch | genau die Vorfalls-Klasse | ❌ | Roter Vermerk an 3.1: nur via VPN/Tunnel, nie öffentlich |
| **Telegram-20-MB-Download-Limit** | mittel | gering–mittel | große PDFs/Videos scheitern kommentarlos | ❌ | kurzfristig: saubere Fehlermeldung; mittelfristig: self-hosted Bot-API-Server prüfen (bis 2 GB, ungeprüft) |
| **429/Flood-Limits bei Streaming-Edits & Gruppen-Routing** | mittel | gering | 1 msg/s pro Chat, 20/min pro Gruppe | ❓ ungeprüft | Backoff-Verhalten prüfen; Ratenplanung in Phase 6/7 einbauen |
| **Scheduler vs. beschäftigter Agent** (Szene-Schmerz #174) | (Phase 7) | mittel | Erinnerungskanal geplant | teils (AGB-Leitplanke: deterministisch) | 7.2 deterministisch UND vom Agenten-Prozess entkoppelt bauen |
| **Bus-Faktor 1 / Verwaisung** | gering | hoch | Einzelperson + KI | teils (Blaupause, WIEDERANLAUF) | Blaupause 9.6 ernsthaft zu Ende führen; Restore-Drill dokumentiert |
| **Prozess-Degradation (MCP-Leaks, Alterung)** | mittel | gering | Dauerbetrieb mit MCP | teils (5.24 geplant) | nächtlicher Hygiene-Neustart im 4-Uhr-Fenster |
| **Interface-SPOF Telegram** | gering | mittel | einziges Interface bis 3.2 | teils (3.2 geplant) | 3.2 nicht streichen; Reihenfolge beim Audit bestätigen |

---

## Top-3-Maßnahmen (Aufwand geschätzt)

1. **Auth-Flanke schließen (5.20 vorziehen + Limit-Sichtbarkeit):** Token-Ablauf-Frühwarner, dokumentierter Re-Auth-Ablauf, Verbrauchs-/Drosselungs-Anzeige im Statusreport. *Aufwand: wenige Stunden; größter Zugewinn an Betriebssicherheit pro Stunde.*
2. **Fundament einfrieren statt treiben lassen:** CLI-Version auf dem VPS pinnen, Updates nur im Wartungsfenster nach einem gebündelten 8.2-Minimal-Regressionslauf (die vorhandenen Selbstchecks als ein abrufbares Skript). *Aufwand: ~halber Tag einmalig.*
3. **Schadensradius begrenzen:** systemd-Sandboxing der Bot-Unit + die zwei roten Auflagen ins Drehbuch schreiben (1.9 Webhook-`secret_token`/Firewall; 3.1 LobeChat nie öffentlich). *Aufwand: wenige Stunden, überwiegend Doku + Unit-Zeilen.*

*(Alle drei sind Vorschläge an die führende Sitzung — diese Prüf-Sitzung ändert nichts am Produktivsystem.)*

---

## Quellen

1. Vergleichsprojekte (GitHub-API + Issue-Listen, 23.07.2026): `RichardAtCT/claude-code-telegram` (+Issues #138–#209), `op7418/Claude-to-IM-skill` (+Issues), `hanxiao/claudecode-telegram`, `claude-telegram-relay`, `claudeclaw`, GitHub-Repo-Suche „claude telegram bot"
2. Claude-Code-Versionshistorie: `raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` (Analyse der 2.1.x-Serie)
3. Abo-Limit-Zeitlinie (Sekundärquellen via DuckDuckGo-Suche; **im Detail ungeprüft**): u. a. VentureBeat (08/2025), Berichte zu Peak-Drosselung 03/2026 und Rücknahme 05/2026
4. OpenClaw-Vorfall (Sekundärquellen, Zahlen variieren; **ungeprüft**): Berichte zu exponierten Instanzen, CVE-2026-25253, Skill-Store-Malware; SecurityScorecard/DECLAWED-Zählungen
5. Telegram-Limits: `core.telegram.org/bots/faq` (offiziell)
6. AGB-/Auth-Primärquelle: `code.claude.com/docs/en/legal-and-compliance` (siehe Schwester-Bericht „Modell- und Plattform-Strategie", Branch `recherche/modell-plattform-strategie`)
7. Modell-Retirement-Zyklen: offizielle Modell-/Migrationstabellen (Anthropic-Referenz, Cache-Stand 06/2026)
8. Interne Grundlagen: `CLAUDE.md` (Stand heute 15:40), `blaupause-notizen.md`, `MIGRATION.md` (Phasen 1–9), Schwester-Bericht Branch `recherche/modell-plattform-strategie`
