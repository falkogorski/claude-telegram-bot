**Zweck: ANSICHT + ENTSCHEID** · **Zu tun: Teil 5 beantworten (vier Fragen); danach wird daraus ein Auftrag für Claudia und ein Block für Mick.**

# Frische-Strang: am Zahn der Zeit bleiben, ohne den Rahmen zu brechen

Stand 23.09.2026, 15:06 · Engywuck · Anlass: Adams Wunsch von 15:0x (Alternativen regelmäßig prüfen, Nachrichtenzufluss, Vorschläge, Blaupause ohne Festschreibung)

## 1. Was es schon gibt (geprüft, bevor etwas Neues entsteht)

- **Versions-Monitor 5.21** mit `components.json`: 19 Einträge in 6 Arten (pip, npm, node, systempaket, docker, manual). Läuft wöchentlich, deterministisch, meldet Updates und stellt `manual`-Einträge nach Ablauf ihres Intervalls **zur Sichtung vor** (so heute `claude-modelle`, `verfahren-medien`, `anthropic-legal`). Dazu der Updater mit Ampel und Freigabeknopf.
- **Regel [Aktualität als Qualitätskriterium]** in CLAUDE.md: gilt ausdrücklich für **Verfahren**, nicht nur Versionsnummern. Sie hat als Mechanik nur die `manual`-Einträge.
- **Kurs-Blick** wöchentlich (Engywuck an Adam).

**Was fehlt, in drei Worten:** Alternativen · Zufluss · Vorschlagsweg. Das Register kennt je Bauteil nur die Version, nicht den Ersatz. Von außen kommt nichts herein, außer Adam trägt es. Und ein Fund hat keinen Weg zu einem Vorschlag mit Knopf.

## 2. Der Rahmen, der nicht verhandelbar ist

- **Zufluss deterministisch, Bewertung mensch-initiiert.** Ein Zeitgeber darf Feeds holen und ablegen; er darf kein Modell rufen (AGB-Regel, CLAUDE.md). Die Bewertung läuft, wenn Adam fragt, oder im Kurs-Blick.
- **Kein Postfach vor Ultracode** (Kette 29.08.). Newsletter per E-Mail scheiden bis dahin aus. Web-Feeds (RSS/Atom) nicht.
- **Kostenfrei ist der Standard.** RSS und GitHub-Feeds kosten nichts. WebSearch der Sitzungen kostet (CLAUDE.md: rund 10 $ je 1000 Suchen, Nennwert); SearxNG auf dem VPS kostet nichts.
- **Keine Wortlisten als Filter** (Adam 28.08.). Die Quellenliste ist der Filter, nicht ein Stichwortsieb.

## 3. Drei Schichten

### A. Fähigkeits-Register: jedes Bauteil kennt seinen Ersatz

`components.json` bekommt je Eintrag drei Felder: `zweck` (welche Fähigkeit), `alternativen` (Liste mit Namen und Stand der letzten Sichtung), `ersatz_aufwand` (Stunden, grob). Der Monitor meldet wie heute bei `manual`: **[Alternativen fällig]** nach Intervall. Erste Einträge: Fremddienst Transkripte (freetranscriptapi.com; Alternative youtube-transcript.ai; Befristung 19.09. offen), Websuche-Anbieter in SearxNG, Sprachausgabe (edge-tts), Spracherkennung (faster-whisper), PDF-Weg (pandoc/weasyprint), Modelle.

**Blaupause-Zeile:** Ein Bauteil ohne benannten Ersatz ist festgeschrieben. Das Register macht die Ersetzbarkeit sichtbar, bevor sie gebraucht wird.

### B. Zufluss: Nachrichten holen, nicht lesen

`scripts/zufluss.py`, deterministisch, am Wochen-Zeitgeber des Monitors: holt RSS/Atom aus `quellen.json` (Adams Hand, wie das Register), legt neue Einträge mit Kennung, Datum, Titel, Adresse in `~/.claude/zufluss/eingang.jsonl`, entdoppelt, hält 60 Tage. Kein Modell, keine Bewertung, kein Telegram. Der Log-Kurier trägt die Datei ins Log-Repo, damit Engywuck sie liest.

**Quellenarten, gemessen und ungemessen:** GitHub-Release-Feeds (`releases.atom`) der eingesetzten Projekte (Claude Code, SearxNG, faster-whisper, PySceneDetect, python-telegram-bot) und PyPI-Release-Feeds decken die Bauteile. Für die Landschaft: Nachrichtenquellen mit Feed. Von meiner Maschine aus erreichbar gemessen: PyPI-Feed und anthropic.com (200); GitHub-Feeds und hnrss von hier gesperrt (403/000) — das sagt über den VPS nichts, dort muss es gemessen werden. Namen von Nachrichtenquellen nenne ich hier bewusst nicht aus dem Gedächtnis; die Liste ist Recherche (Teil 5, Frage 2).

### C. Vorschlagsweg: vom Fund zum Knopf

- **`/neues`** (Adams Hand): Claudia liest den Eingang seit der letzten Sichtung, gruppiert nach Bauteil und Landschaft, nennt je Fund den Bezug zum Fähigkeits-Register (betrifft welches Bauteil, welche Alternative) und macht höchstens drei Vorschläge. Modellaufruf nur hier.
- **Wirkung:** jeder Vorschlag mit Knopf **[in den Laufplan]** → Eintrag ins Auftragsbuch/Freigabe-Postfach, deterministisch. Keine Frage ohne Wirkung.
- **Kurs-Blick:** bekommt eine feste Zeile [Neu am Markt, für uns relevant] aus demselben Eingang. Zweiter Blick, anderer Schnitt.

**Ein Zusatz, der Adams Satz [unserer Zeit ein wenig voraus] trägt:** Vorschläge werden nicht nur bei Funden gemacht. Im Kurs-Blick steht je Woche **eine** Frage: *Welche Fähigkeit fehlt, die es inzwischen fertig gibt?* Das ist der Blick, den ein Feed nicht liefert.

## 4. Was ich nicht getan habe, und warum

Keine Websuche. Sie kostet nach der Kostenregel, und die Frage ist offen, ob sie in dieser Sitzung über das Abo läuft. Die bessere Stelle für die Recherche ist ohnehin Claudia: SearxNG kostet nichts, und die Erreichbarkeit der Feeds muss vom VPS gemessen werden, nicht von meiner Maschine.

## 5. Entscheide

1. **Everlast:** Ich kenne unter diesem Namen keinen Nachrichtendienst zur digitalen Welt. Bitte den genauen Namen oder die Adresse, dann kommt er als erste Quelle in die Liste.
2. **Recherche der Quellen:** durch Claudia über SearxNG, mit Erreichbarkeitsmessung vom VPS (Empfehlung) — oder durch mich mit WebSearch (Nennwert grob 0,30 $ für 30 Suchen, Deckung durch das Abo unklar → Freigabe nötig).
3. **Bewertung:** mensch-initiiert per `/neues` plus Kurs-Blick-Zeile (Empfehlung) — oder ein automatischer Wochenbericht (Modellaufruf am Zeitgeber, AGB-Grauzone, nicht empfohlen).
4. **Einordnung:** als Block 6 nach den fünf laufenden Blöcken (Empfehlung) — oder vorziehen.

Nach den Antworten: Auftrag an Claudia (Quellenliste, Messung, `/neues`-Form) und Block 6 für Mick (Register-Felder, `zufluss.py`, Knopf mit Wirkung, Prüfzeilen ausführend).
