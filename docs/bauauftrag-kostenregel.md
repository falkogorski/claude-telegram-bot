<!-- ROLLE: bauauftrag-kostenregel -->
# BAUAUFTRAG — Kostenregel, zwei kleine Punkte

**Von:** Engywuck (Kontrolle) · **An:** Mick (Bau) · **Eingegangen:** 24.08.2026, 01:1x
**Stichtag:** 2026-08-24 · **ERLEDIGT 24.08.2026, 01:33 (Commit `1817c86`)** ·
**massgeblich ist die
Status-Zeile in `MIGRATION.md`**

**Termin: Dienstag-Zug, VOR dem Mail-Umbau** (Engywucks Vorgabe: billiger).
**Gut genug wenn:** beide Punkte stehen, jeder mit gefahrener Gegenprobe.
Kein Anhaengsel, keine dritte Runde. **Halber Block, nicht mehr.**

## Lagemessung vor dem Termin (Mick, 24.08. 01:12) — der Grund, warum Dienstag traegt

Nur die **Anwesenheit der Namen** geprueft, nie ein Wert:

| Ort | Befund |
|---|---|
| `/etc/claude-telegram-bot.env` (VPS) | **nur** `CLAUDE_CODE_OAUTH_TOKEN` |
| lokale `.env` | existiert nicht |
| laufende Shell | keiner von beiden |

**Der gefaehrliche Fall ist latent, nicht eingetreten.** Nirgends stehen beide
nebeneinander; kein Archiv-Block wurde ausgefuehrt. Das rechtfertigt den
Dienstag — **und aendert nichts an der Notwendigkeit**, denn der Wert eines
Waechters bemisst sich am Tag, an dem der Fall eintritt, nicht heute.

## ① Der Pruefer schweigt im gefaehrlichen Fall

`scripts/stundenblume.py:458-464` — die Warnung sitzt **innerhalb** von
`if "CLAUDE_CODE_OAUTH_TOKEN" not in namen:`. **Sind BEIDE gesetzt, schweigt
sie** — und `.env.example:17` benennt genau das als die Gefahr: *Wenn API-Key
UND Abo-Token gesetzt sind, bevorzugt das SDK den Key.*

**Der Waechter prueft den vorgestellten Fall, nicht den nebenan dokumentierten.**
Dieselbe Klasse wie alles andere an diesem Wochenende, diesmal an der obersten
Regel des Projekts.

**Fix:** `ANTHROPIC_API_KEY in namen` **unabhaengig** vom Abo-Token pruefen,
dann warnen. Der bestehende [keine-abo-anmeldung]-Zweig bleibt daneben.

**Gegenprobe, beide Richtungen** (vorher hinschreiben, welche Zeile rot wird):
beide Namen in die Attrappe → Warnung **MUSS** kommen · nur Abo-Token →
**KEINE** Warnung. *Ohne die zweite Richtung ist die Gegenprobe halb.*

## ② Die Ablage weist einen API-Schluessel an

Gemeldet waren vier README-Stellen. **Ueber die ganze Ablage gemessen sind es
zehn, und die schwersten stehen woanders:**

- `README.md:115, 134, 146, 172` — Prosa, fuer den VPS ausdruecklich
  *gleicher Key wie lokal*
- `MIGRATION-DREHBUCH-ARCHIV.md:36-51` — **sechs Zeilen ausfuehrbare Shell**,
  die `ANTHROPIC_API_KEY=$K` in die Env-Datei schreiben. **Ein kopierbarer Block.**

**NICHT anfassen** (diese warnen oder beschreiben Dritte, sie sind richtig):
`CLAUDE.md`, `MIGRATION.md`, `WIEDERANLAUF.md`, `ABHAENGIGKEITEN.md`,
`docs/NOTBETRIEB.md`, `docs/REBUILD.md`, `docs/befund-a2-kontingent.md`,
Entscheidungsvorlagen.

**Ersetzen** durch den Abo-Weg mit der Kosten-Warnung daneben — Formulierung
wie `docs/REBUILD.md:46`, die stimmt.

## ③ Wiederkehr verhindern — eine Differenzart, KEIN neuer Waechter

Der Differenzmesser ist der bestehende Mechanismus, eine neue
`_differenz`-Funktion **seine gebaute Erweiterungsstelle**. Damit ist der
Kurs-Regel-Nachweis gefuehrt (kein Waechter dritter Ordnung).

**Ehrlich zur Reichweite, damit nicht zu viel gebaut wird:**

- **Mechanisch fassbar ist nur die ZUWEISUNG** — `ANTHROPIC_API_KEY=` in einer
  versionierten Doku-Datei. Rein syntaktisch, kein Urteil, keine Fehlalarme auf
  den Warn-Stellen. **Das faengt den Archiv-Block.**
- **Nicht fassbar ist die Prosa** ([den Key ersetzen], [gleicher Key wie
  lokal]). Dafuer gibt es keine Regel ohne Urteil, und eine Heuristik schluege
  auf den zehn korrekten Warn-Stellen an.

Also: **die Zuweisung mechanisch und hart, die Prosa einmal von Hand** — und
das bleibt der **ehrliche Rest**. Er gehoert in den Befund geschrieben, nicht
weggeheuristikt.

**Gegenprobe:** eine Zeile `ANTHROPIC_API_KEY=xyz` in eine Doku-Datei → **MUSS
rot**. Eine Warn-Zeile ohne Zuweisung → **MUSS gruen bleiben.**
