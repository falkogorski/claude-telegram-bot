<!-- ROLLE: audit-statusuebersicht -->
# Phasen-Audit 5 → Phase 3 — Voll-Statusübersicht

> **⚠️ Gültigkeits-Kopf** (Regel ⑪, nachgetragen 25.07.2026, 05:31 geprüfte Zeit)
> **Die Statusangaben dieses Dokuments sind auf den 23.07.2026 eingefroren und
> teils überholt.**
> **Überholt durch:** Adams Entscheide vom 24. und 25.07.2026 — u. a. 6.6-Zimmer
> FINAL v3, Webhook-Weg (Self-Signed, live), Emoji-Ersatz, Log-Sync-Repo, Hermes
> Option B, faster-whisper, Node-Aufschub — sowie die neuen Punkte 5.28 bis 5.34.
> **Maßgeblich ist ausschließlich die Status-Zeile des jeweiligen Punkts im
> Master-Drehbuch `MIGRATION.md`.** Genau vier Punkte galten hier fälschlich
> weiter als offen; das ist der Schaden, den dieser Kopf künftig verhindert.
> **Der eingefrorene Nenner vom 23.07. bleibt gültig** — er ist die
> Vergleichsbasis für den Sprint, keine Statusaussage.

**Stichtag / eingefrorener Nenner: 23.07.2026.** Alles, was nach diesem Datum
neu ins Drehbuch kommt, zählt beim Prozent-Vergleich **separat** (Neuzugänge),
nicht gegen diesen Nenner — sonst „läuft der Fortschritt vor der Arbeit davon".
Fertigstellungsgrad je Phase **nach Arbeitsumfang**, nicht nach Punktzahl.

**Legende:** ✅ fertig/verifiziert · 🔄 läuft/teilweise · ⬜ offen ·
⏭️ bewusst zurückgestellt.

---

## Phase 0 — Code-/Repo-Vorbereitung — ✅ 100 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 0.1–0.8 | ✅ | Produktivstand, Audit, 401-Handling, neutrale Begrüßung, Pfade/Modell per env, Backtest, Drehbuch-Übergabe — alle acht verifiziert. |

## Phase 1 — Server-Grundgerüst — ✅ 97 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 1.0–1.8, 1.10–1.12 | ✅ | Zugang, Härtung, User, Python/Whisper, CLI, Headless-Auth, Code, systemd, Umschaltung, Rollback — alles verifiziert; Bot läuft produktiv. |
| 1.9 Webhooks | 🔄 | Code-Vorbereitung fertig (env-Schalter, rote Auflagen erzwungen, tornado installiert); Umschaltmoment bewusst offen, gemeinsam mit Adam (FR). |

## Phase 2 — KI-Orchestrierung & Datenschutz — 🔄 90 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 2.1 LiteLLM | ✅ | Proxy läuft im SQLite-Modus. |
| 2.2 Ampel | 🔄 | Beobachtungsphase seit 15.07. aktiv; Enforcement-Trimmen terminiert ~16.08. |
| 2.3 Ollama/Phi-4 | ✅ | Lokales Fallback verifiziert. |
| 2.4 Groq | ⏭️ | Bewusst übersprungen, jederzeit nachrüstbar. |
| 2.5 Kein OpenAI | ✅ | Grundsatz gewahrt. |
| 2.6 Neben-Inferenzen | 🔄 | Kern umgesetzt; lange Zusammenfassungen offen bis 5.14. |
| 2.7 SearxNG | ✅ | Private kostenfreie Websuche verifiziert. |

## Phase 3 — Interfaces — ⬜ 0 % (nächste große Phase)

| Punkt | Stand | Kurzsatz |
|---|---|---|
| Zwischen-Audit-Tor | 🔄 | Dieses Dokument ist die Zulieferung dafür. |
| 3.1 LobeChat | ⬜ | Offen; rote Auflage „nie öffentlich, nur VPN/Tunnel" im Drehbuch verankert. |
| 3.2 Matrix/Element | ⏭️ | Terminiert auf Phase 2.75 (nach RAM-Upgrade). |

## Phase 4 — Backup & Reproduzierbarkeit — 🔄 55 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 4.1 Backup VPS→Mac | ✅ | Sicherung + Restore-Probe bestanden. |
| 4.2 Zentrale Chat-Logs | 🔄 | Log-Sync ins private Repo läuft (Timer 05:10); Voll-Ausbau offen. |
| 4.3 Memory/Configs-Repo | ⬜ | Offen (mit Phase 6 Ordner-Spiegelung verzahnt). |
| 4.4 Rebuild-Doku | 🔄 | `docs/REBUILD.md` Entwurf liegt vor; Adams Durchsicht = Abnahme. |
| 4.5 iCloud ADP | ⬜ | Adam-Aktion. |

## Phase 5 — Bot-Features — 🔄 ~40 % (nach Arbeitsumfang)

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 5.2 Persistenz/Queue | ✅ | Kill-Test auf dem VPS bestanden. |
| 5.8 Sendepfad-Refactor | 🔄 | Vorstufe gebaut (Sammel-statt-Blockweise); Rest offen. |
| 5.9 Emoji-Reaktionen | ✅ | Von Adam verifiziert (23.07.). |
| 5.18 Session-Watchdog | ✅ | Hänger-Test auf dem VPS bestanden. |
| 5.22 STT-Umschalter | ✅ | Threads-Fix + Tempo-Button verifiziert. |
| 5.23 Session-Diät | ✅ | Verifiziert (Erst-Antwort ~60 s → ~4 s). |
| 5.25 Reibungslose Recherche | ✅ | Alle sechs Drehbuch-Tests von Adam bestanden (23.07.). |
| 8.5-nah: Pre-Send v1 | 🔄 | Live seit 17.07., v2 (Bezug/Sicherheit) offen. |
| 5.1,5.3–5.7,5.10–5.17,5.19–5.21,5.24,5.26,5.27 | ⬜ | Offen — der große Rest der Feature-Phase (Multi-Session, PDFs, Board, Modell-Persistenz, TTS-opt-in, Recall, Video, Link-Inbox, Token-Frühwarner, Update-Monitor, Rotation, Transkript-Sichtbarkeit, Arbeitsmodus). |

## Phase 6 — Kanal-Routing / Ablage — 🔄 10 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 6.6 Kanal-Empfehlung | 🔄 | Vorlage v2 (Gruppen/Topics) liegt vor; wartet auf Adams Zimmer-Daumen. |
| 6.1–6.5 | ⬜ | Routing-Code, Deep-Links, Topic-Anlage — offen (SA-Nacht im Sprint). |

## Phase 7 — Erinnerungskanal — ⬜ 0 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 7.1–7.4 | ⬜ | Kanal, Scheduler (deterministisch + entkoppelt bauen!), Kalenderquelle, Links — offen (MO im Sprint). |

## Phase 8 — Tests & Selbstüberwachung — 🔄 45 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 8.2 Regressionstest | 🔄 | Minimaltest `regressionstest.sh` gebaut (11/11 Mac+VPS); Auto-Anstoß offen. |
| 8.5 Pre-Send-Hook | 🔄 | v1 live; v2 offen. |
| 8.6 Doku-Spiegel | 🔄 | Prüfskript gebaut (6/6), läuft im Minimaltest mit; Abnahme offen. |
| 8.7 Repo-Governance | 🔄 | Drei Schutzschichten live; Abnahme offen. |
| 8.1,8.3,8.4 | ⬜ | 4-Uhr-Check (AGB-Gegenlese davor!), Vollständigkeits-Check, Aufräumpass — offen. |

## Phase 9 — Danach — 🔄 5 %

| Punkt | Stand | Kurzsatz |
|---|---|---|
| 9.7 Hermes | 🔄 | Prüf- + Strategiebericht liegen vor; Empfehlung Option B/„Beibehalten+Erweitern" — Entscheid heute. |
| 9.1–9.6 | ⬜ | TTS-Upgrade, Rot-Backend, Demo-Klon, Approval-Hub, E-Mail, Blaupause — offen (Blaupause sammelt laufend mit). |

---

## Gewichteter Gesamt-Fortschritt: **~62 %**

Nach Arbeitsumfang, nicht nach Punktzahl: Das schwere Fundament (Phasen 0–2,
Server + Orchestrierung) steht fast vollständig; der verbleibende Aufwand liegt
in der breiten Feature-Phase 5 und den Interface-/Routing-/Erinnerungs-Phasen.

---

## Offene Entscheidungen & Wartepunkte (für Adam beim Audit)

1. **Audit-Gesamtdaumen** — bestätigt diese Übersicht den Übergang 5 → Phase 3?
2. **Hermes-Entscheid (9.7)** — Option B als finale Linie? (Bericht empfiehlt „Beibehalten + Erweitern".)
3. **6.6-Zimmer-Daumen** — je Zimmer 👍/👎 auf die Vorlage v2 (Werkstatt: Migration&Technik / Fanpost / Business&Blaupause / Rechnungen&Büro · Archiv&Wissen: Recherchen&Referenzen / Link-Inbox / Interessen).
4. **REBUILD.md-Durchsicht** — Durchsicht = Abnahme (Entwurf liegt vor).
5. **1.9-Umschaltweg** — Domain+Caddy vs. Self-Signed auf die IP (FR gemeinsam).
6. **Sprint-Fahrplan „80 % bis Dienstag"** — bestätigt, oder Prioritäten verschieben?

### Top-3-Audit-Punkte aus dem Rotes-Team-Bericht (heute Nacht bereits angegangen)

- **Auth-Flanke** (5.20 vorziehen + Limit-Sichtbarkeit im /status) — im Drehbuch als SO-Nacht terminiert.
- **Fundament-Pinning** (CLI/SDK) — ✅ erledigt (requirements gepinnt, Minimaltest gebaut).
- **Härtung + rote Auflagen** — ✅ systemd-Sandboxing + Hygiene-Neustart live; Auflagen 1.9/3.1 im Drehbuch.
- **Nachlauf:** Umschalt-/Restore-Drill nach dem Sprint terminieren.
