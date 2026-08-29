<!-- ROLLE: agb-faktensammlung -->
# AGB-Faktensammlung — Anthropic-Nutzungsbedingungen (Abo/Auth)

**Zweck:** Reine **Faktensammlung** als Vorlage für 8.1 (4-Uhr-Check) und den
AGB-Wachposten (5.21). **Keine Bewertung** — die Einordnung, was für uns daraus
folgt, macht Adam (bzw. sie steht bereits als Bau-Leitplanke in CLAUDE.md
„AGB-Grenze"). Hier stehen nur belegte Aussagen mit Quelle und Frischegrad.

**Stand:** 24.07.2026. **Primärquelle:** `code.claude.com/docs/en/legal-and-compliance`,
Abschnitt „Authentication and credential use" (gelesen/zitiert im Strategie-Bericht
[`2026-07-23_modell-plattform-strategie-bericht.md`](2026-07-23_modell-plattform-strategie-bericht.md)
A.2/D.1, 23.07.2026). Sekundärquellen sind als solche markiert und **ungeprüft**.

---

## A. Belegte Fakten (Primärquelle)

| # | Fakt (Wortlaut/Sinn) | Beleg |
|---|---|---|
| A1 | OAuth-Auth ist „intended exclusively … to support ordinary use of Claude Code and other native Anthropic applications". | Primärquelle, Auth-Abschnitt |
| A2 | Die Abo-Limits decken ausdrücklich „ordinary, individual usage of Claude Code and the Agent SDK". | Primärquelle |
| A3 | Verboten ist Drittanbieter-Routing: Anthropic „does not permit third-party developers to … route requests through Free, Pro, or Max plan credentials **on behalf of their users**". | Primärquelle |
| A4 | Entwickler, die Produkte/Dienste bauen — „including those using the Agent SDK" — sollen **API-Keys** nutzen. | Primärquelle |
| A5 | Durchsetzung erfolgt „without prior notice" (Kontosperrung möglich). | Primärquelle |

## B. Belegte Fakten (Sekundärquellen — ⚠️ ungeprüft)

| # | Fakt | Beleg / Vorbehalt |
|---|---|---|
| B1 | Technische Durchsetzung der Drittanbieter-Sperre ab **04.04.2026** (Blockade von OpenClaw, OpenCode u. a.; teils Sperrungen binnen Minuten). | Sekundärquellen (Strategie-Bericht A.2), ⚠️ ungeprüft |
| B2 | Einzelne Sekundärquellen zitieren einen schärferen Wortlaut („including the Agent SDK is not permitted"); **in der Primärquelle so nicht gefunden** — maßgeblich ist A2/A4. | Strategie-Bericht A.2, ⚠️ Widerspruch dokumentiert |
| B3 | Abo-Limit-Politik dreimal geändert in zehn Monaten (Wochenlimits 08/2025; Peak-Drosselung 27.03.2026; Rücknahme + Verdopplung 06.05.2026). | Rotes-Team-Bericht B.2, ⚠️ ungeprüft |
| B4 | „Max" heißt inzwischen „**ab** 100 $" (Preisuntergrenze, nicht Fixpreis). | Strategie-Bericht D.1 |

## C. Was daraus für den Bot-Betrieb faktisch gilt (bereits als Leitplanke verankert, keine neue Bewertung)

- **Erlaubt (Abo):** mensch-initiierte Steuerung — Adam schickt eine Nachricht,
  daraus folgt ein Modell-Aufruf. So arbeitet der Bot heute (A1/A2).
- **Grauzone bis Verstoß (Abo):** reine Zeit-Trigger, die **ohne Adams Zutun**
  regelmäßig Modell-Aufrufe auslösen.
- **Verträglichste Lesart** unseres Einzelnutzer-Eigenbetriebs über die
  offizielle CLI/SDK: gedeckt durch A2 — **Restrisiko nicht null** (A5).
- Quelle für C steht wörtlich in `CLAUDE.md` → „AGB-Grenze des Abos".

## D. Direkte Konsequenz für 8.1 (4-Uhr-Funktionscheck) — Faktenlage, nicht Bewertung

Aus A2/A3 + der Grauzonen-Regel folgt die **Bau-Anforderung** an 8.1:
- Der 4-Uhr-Check darf **keinen Modell-Aufruf** enthalten (sonst wäre er ein
  zeitgetriggerter Abo-Aufruf ohne Adams Zutun → Grauzone).
- **Deterministisch bauen:** Dienst-Status (`systemctl is-active`),
  Regressionstest (`scripts/regressionstest.sh`), Abhängigkeits-Prüfbefehle
  (ABHAENGIGKEITEN.md), Token-Alter (5.20) — alles ohne CLI-/SDK-Inferenz.
- **Meldung** über die Telegram-Bot-API per `curl` (kein Agent).
- Falls je ein Modell-Aufruf nötig würde: bewusst auf **API-Pay-per-Token**
  legen → dann greift die 💰-Warnpflicht (Kostenquelle + Höhe + Adams Freigabe).

## E. Offen für Adam (Bewertung, nicht Fakt)

1. Reicht die „verträglichste Lesart" (A2) als Betriebsgrundlage, oder soll der
   API-Key-Notweg (Strategie D.2 Stufe 1) vorbereitet dokumentiert werden?
2. Frequenz/Umfang des AGB-Wachpostens (5.21): täglicher Diff der Legal-Seite?
3. Ab welchem Nutzungsgrad gilt der Betrieb als „professionell/produktiv" (dann
   API-Pflicht nach A4)? — relevant erst für Klienten-Klone (9.3), nie über Adams Abo.
