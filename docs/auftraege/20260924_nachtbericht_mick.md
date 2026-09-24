**Zweck: ANSICHT + ENTSCHEID** · **Zu tun: Abschnitt [Wartet auf Adam] lesen; jeder Punkt dort blockiert nichts davor.**

# Nachtbericht Mick — Durchlauf 23./24.09.2026

Stand: 24.09.2026, 02:4x — **Übergabe abgearbeitet.** Live: `d54b272`. **Nichts davon ist deployt.**

**Nenner:** Engywucks Übergabe Fassung 3 mit den Blöcken 1 bis 6 (Block 6 bis Fassung 5), dazu Vormerkung 6b. Gebaut: 1b, 2, 3 (Teil 1), 4, 5, 6 (Teile 1 und 2) — sieben Zweige. Geparkt, begründet: drei Punkte (unten). D8 erledigt, dazu Integrationszweig (92/92), Lesepflicht Dienst B, Lesenotiz 6b.

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
| D8 SDK-Klonprobe | `probe-sdk` · `9667f08` (Reparatur), `1cf5da3` (Pin) | test_fehlererkennung_sdk (+4 · 1) | 85/85 mit 0.2.127 und mit 0.2.159 | Reparatur: nichts; Pin: dein Fenster, **nach Node** |

Einzelheiten je Block stehen in `MIGRATION.md`, Einträge (57) bis (63), je im jeweiligen Zweig.

**Schritt 0 jedes Deploy-Blocks** (Regel vom 10.09.): `git log --oneline HEAD..<ziel>` zeigt nur die Commits dieses Blocks, sonst nicht ziehen. Für Block 4 heißt das: Block 3 kommt mit, weil 4 darauf aufsetzt.

## Wartet auf Adam

1. **Block 4, vor dem Deploy — Abo-Probe auf dem VPS als claudebot** (Adams Entscheid 23.09.): `claude -p --model claude-opus-5-5 'ok'`. Erst bei Erfolg deployen. Die Kennung selbst ist am Release-Notes-Feed gemessen (Start 22.09.); ob sie im Abo läuft, zeigt nur diese Probe. **Beim ersten Wächterlauf nach dem Deploy wird Fable auf `claude-fable-5-1` umgestellt** (im Feed seit 01.09.) — mit Meldung und Rückweg-Knopf; die erste Nachricht an Fable ist die Probe.
2. **Transkript-Dienst, Kenntnis:** Ohne Konto **20 Abrufe je Stunde** (die 50 waren befristet bis 19.09.), und die Anfragen laufen **über Cloudflare (USA)**. Für öffentliche Videos gelb und tragbar, für eigenes Material nie. Kein Handlungsbedarf, außer du willst es anders.
3. **Heimtunnel:** Claudia stuft ihn wieder hoch — er wäre der einzige eigene Weg für Untertitel (Direktabruf 1 von 31). Dein Entscheid, kein Teil dieser Blöcke.
4. **Kurs-Videos (6.4):** Weg Mac → VPS. Vorschlag: du kopierst per `rsync` in einen Eingangsordner des Bots, er transkribiert lokal mit faster-whisper und legt unter `wissen/kurse/` ab. Grob eine Stunde Bau. **Kein Bau ohne dein Wort.**
5. **Zielkonflikt H-3, zur Kenntnis:** Die Frist am Stichtag geht jetzt an die Kontrolle (⚙️ im Protokoll) statt an dich — nach deinem Wortlaut vom 19.09. Der Hotfix vom 10.09. verlangte das Gegenteil; sein Kern (keine ungelesene Zeile) bleibt gemessen.

6. **D8, SDK-Sprung 0.2.127 → 0.2.159:** Klonprobe grün, Paarung abgelesen (`mcp` 1.30.0, `anyio` 4.15.1, CLI 2.1.281). **Beim Messen gefunden und repariert:** Die Kontingent-Erkennung las die Nutzlast der neuen Fehlerart nicht — mit dem Sprung wäre die Rücklage (Rang A) blind geworden. **Die Reparatur `9667f08` ist ohne den Sprung deploybar; ich empfehle, sie mit dem nächsten Block mitzunehmen.** Den Sprung selbst: in einem Fenster deiner Wahl, nach Node. Befund: `docs/auftraege/20260924_befund_sdk_klonprobe.md` (Zweig `probe-sdk`).

7. **Dienst B (`youtube-transcript.ai`), Lesepflicht erfüllt — Urteil: geht nicht, nicht aufnehmen.** Betreiber, Land und Impressum fehlen; es gilt „das Recht am Sitz des Betreibers", und der Sitz steht nirgends; DSGVO nicht erwähnt. Keine dokumentierte Schnittstelle (Web-Werkzeug; Selmas `curl` nutzt einen inoffiziellen Endpunkt). Analytik über PostHog mit pseudonymer Besucherkennung. **Deshalb auch keine Messung vom VPS** — sie gäbe genau die Daten an einen unbekannten Betreiber, die die Lesepflicht schützen soll. Die Freigabe in `quellen.json` steht auf nein und bleibt dort. Wenn du einen zweiten Dienst willst, suche ich einen mit benanntem Betreiber in der EU.

## Geparkt, begründet

- **Block 3, Auftrag 3** (stiller Neustart) und das **Stundenblumen-Prüfmoment**: Engywucks Ergänzung „Zähler, ab dem dritten laut" nennt keinen Zeitraum; Grundlage `20260919_nachtlese.md` fehlt mir.
- **Block 5, Auftrag 4 zweiter Halbsatz:** ein in Telegram gelöschtes Thema beim nächsten Zugriff bemerken. Er ändert dieselbe Sendefunktion wie Block 2 — **gehört deshalb nach dessen Deploy**, sonst zwei Umbauten an einer Stelle.
- **F-Punkte** „Belegkette nie gerollt", „Gedächtnis-Pfad im Prompt": Grundlage ebenfalls die Nachtlese vom 19.09.

## Nächste Schritte in dieser Nacht (wird fortgeschrieben)

- ~~D8~~ erledigt (siehe oben). Node bleibt Adams Fenster mit dem Vollzugs-Zettel.
- ~~Integrationszweig~~ erledigt: **`probe-gesamt` (`202564e`) führt 1b, 2, 3, 4, 5, 6 und die Limit-Reparatur zusammen — 92/92.** Konflikte gab es nur dort, wo zwei Blöcke an derselben Stelle eingetragen haben (Drehbuch, Register, Blaupause, `requirements.txt`) und zweimal im Code, beide additiv (je eine Selbstcheck-Zeile und ein Tagescheck-Abschnitt nebeneinander). **Eine Stelle war inhaltlich:** Der Registereintrag `claude-modelle` trägt jetzt die angehobene Notiz aus Block 4 **und** die Fähigkeitsfelder aus Block 6. **Für dich heißt das:** Du kannst Block für Block deployen, oder `probe-gesamt` in einem Zug — dann aber **zuerst die Abo-Probe für Opus 5.5** (Punkt 1 oben), weil Block 4 darin steckt.
- ~~Dienst B~~ gelesen, Urteil oben (Punkt 7).

## Gelesen für Vormerkung 6b (WhatsApp, W4) — nichts gebaut

Ursprungs-Repo `WhiskeySockets/Baileys`, `src/Socket/newsletter.ts` (SafeDep-Auflage: nie eine Abspaltung). **Für das Lesen eines Kanals genügen zwei Funktionen:** `newsletterMetadata('invite', code)` (Einladungscode → Kennung) und `newsletterFetchMessages(jid, count, since, after)`. **Alle übrigen schreiben** — auch `newsletterFollow`, das den Kanal mit der Nummer des Kontos abonniert, also ein Schritt nach außen ist; dazu Anlegen, Umbenennen, Reagieren, Löschen, Besitzwechsel. **Für den späteren Bau:** Der Dienst darf nur die zwei lesenden erreichen (Positivliste, kein Verbot einzelner); ob das Abrufen ohne Folgen geht, ist zu messen. Grenzen für Abrufe nennt der Quelltext keine.

## Aufräumen, wartet auf dein Ja

Neun Arbeitsbäume neben dem Hauptbaum (`probe-sammel`, `-darstellung`, `-meldungen`, `-modell`, `-zimmer`, `-frische`, `-sdk`, `-gesamt`, dazu der alte `probe-f22`). Alle Zweige sind gepusht; an den Bäumen hängt nichts. `probe-sdk` trägt eine eigene venv (rund 1 GB). **Löschen frage ich vorher** — ein Ja genügt, dann räume ich sie mit `git worktree remove`.

## Weiterarbeiten ohne Adams Hand

Zwei Wecker waren gesetzt (05:17 und 10:23). **Zurückgenommen um 02:4x**, weil die Übergabe abgearbeitet ist: Ein Wecker ohne offene Arbeit hätte nur einen Modelllauf ohne Grund ausgelöst. **Für künftige Nächte gemessen:** Das Werkzeug (`CronCreate`) weckt diese Sitzung nach einem Kontingent-Stopp von selbst — solange sie in der App offen bleibt; auf die Platte schreibt es nichts. Je Unterbrechung setze ich einen Wecker, keinen Dauertakt (Kontingent-Regel in `CLAUDE.md`).
