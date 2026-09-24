**Zweck: ANSICHT + ENTSCHEID** · **Zu tun: Abschnitt [Wartet auf Adam] lesen; jeder Punkt dort blockiert nichts davor.**

# Nachtbericht Mick — Durchlauf 23./24.09.2026

Stand: 24.09.2026, 02:1x (wird je Block fortgeschrieben). Live: `d54b272`. **Nichts davon ist deployt.**

**Nenner:** Engywucks Übergabe Fassung 3 mit den Blöcken 1 bis 6 (Block 6 bis Fassung 5), dazu Vormerkung 6b. Gebaut: 1b, 2, 3 (Teil 1), 4, 5, 6 (Teile 1 und 2) — sieben Zweige. Geparkt, begründet: drei Punkte (unten). Offen aus der Übergabe: D8.

## Je Block

| Block | Zweig · Commit | Prüfer (Zeilen · Gegenproben) | Lauf | Deploy braucht |
|---|---|---|---|---|
| 1b Sammelnachricht | `probe-sammel` · `ab046c5` | test_sammelnachricht (21 · 6) | 86/86 | nichts Besonderes |
| 2 Darstellung, Link-Vorschau, Kopiertext | `probe-darstellung` · `9d10d9f` | test_darstellung (24 · 6) | 86/86 | `pip install -r requirements.txt` (telegramify-markdown, pyromark) |
| 3 Meldungen, Teil 1 | `probe-meldungen` · `7c87bc3` | test_meldungen_adressat (14 · 4), H-3 angepasst | 86/86 | nichts Besonderes |
| 4 Modellwächter | `probe-modell` · `e17d8ba`, `4a26924` — **setzt auf Block 3 auf** | test_modellwaechter (22 · 6) | 87/87 | **Abo-Probe vorher**, siehe unten |
| 5 Zimmerliste | `probe-zimmer` · `366b394` | test_zimmerliste (17 · 6) | 86/86 | nichts Besonderes |
| 6 Frische, Teil 1 | `probe-frische` · `a621e29` | test_frische (21 · 8), Zielumgebung | 86/86 | nichts Besonderes |
| 6 Frische, Teil 2 | `probe-frische` · `544fd7a` | test_transkript_wissen (13 · 5) | 87/87 | `pip install -r requirements.txt` (youtube-transcript-api u. a.) |

Einzelheiten je Block stehen in `MIGRATION.md`, Einträge (57) bis (63), je im jeweiligen Zweig.

**Schritt 0 jedes Deploy-Blocks** (Regel vom 10.09.): `git log --oneline HEAD..<ziel>` zeigt nur die Commits dieses Blocks, sonst nicht ziehen. Für Block 4 heißt das: Block 3 kommt mit, weil 4 darauf aufsetzt.

## Wartet auf Adam

1. **Block 4, vor dem Deploy — Abo-Probe auf dem VPS als claudebot** (Adams Entscheid 23.09.): `claude -p --model claude-opus-5-5 'ok'`. Erst bei Erfolg deployen. Die Kennung selbst ist am Release-Notes-Feed gemessen (Start 22.09.); ob sie im Abo läuft, zeigt nur diese Probe. **Beim ersten Wächterlauf nach dem Deploy wird Fable auf `claude-fable-5-1` umgestellt** (im Feed seit 01.09.) — mit Meldung und Rückweg-Knopf; die erste Nachricht an Fable ist die Probe.
2. **Transkript-Dienst, Kenntnis:** Ohne Konto **20 Abrufe je Stunde** (die 50 waren befristet bis 19.09.), und die Anfragen laufen **über Cloudflare (USA)**. Für öffentliche Videos gelb und tragbar, für eigenes Material nie. Kein Handlungsbedarf, außer du willst es anders.
3. **Heimtunnel:** Claudia stuft ihn wieder hoch — er wäre der einzige eigene Weg für Untertitel (Direktabruf 1 von 31). Dein Entscheid, kein Teil dieser Blöcke.
4. **Kurs-Videos (6.4):** Weg Mac → VPS. Vorschlag: du kopierst per `rsync` in einen Eingangsordner des Bots, er transkribiert lokal mit faster-whisper und legt unter `wissen/kurse/` ab. Grob eine Stunde Bau. **Kein Bau ohne dein Wort.**
5. **Zielkonflikt H-3, zur Kenntnis:** Die Frist am Stichtag geht jetzt an die Kontrolle (⚙️ im Protokoll) statt an dich — nach deinem Wortlaut vom 19.09. Der Hotfix vom 10.09. verlangte das Gegenteil; sein Kern (keine ungelesene Zeile) bleibt gemessen.

## Geparkt, begründet

- **Block 3, Auftrag 3** (stiller Neustart) und das **Stundenblumen-Prüfmoment**: Engywucks Ergänzung „Zähler, ab dem dritten laut" nennt keinen Zeitraum; Grundlage `20260919_nachtlese.md` fehlt mir.
- **Block 5, Auftrag 4 zweiter Halbsatz:** ein in Telegram gelöschtes Thema beim nächsten Zugriff bemerken — hängt an allen Sendestellen, eigener kleiner Block.
- **F-Punkte** „Belegkette nie gerollt", „Gedächtnis-Pfad im Prompt": Grundlage ebenfalls die Nachtlese vom 19.09.

## Nächste Schritte in dieser Nacht (wird fortgeschrieben)

- D8 (Node/SDK Klon-Probe) aus Engywucks Teil C.
- Ein Integrationszweig, der alle Blöcke zusammenführt und den Regressionslauf über das Ganze fährt — damit die Deploy-Reihenfolge keine Überraschung bringt.
- Dienst B (`youtube-transcript.ai`): Lesepflicht; die Messung vom VPS erst danach.

## Weiterarbeiten ohne Adams Hand

Zwei Wecker in dieser Sitzung (05:17 und 10:23, je einmal), falls das Kontingent greift. **Grenze:** Sie leben nur, solange diese Sitzung in der App offen ist.
