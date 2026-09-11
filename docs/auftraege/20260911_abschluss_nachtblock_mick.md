# Abschluss: Nachprüfung von Micks Nachtblock A0–A5 (048ed6e..923ffa8, Bericht 14dcbce)

**11.09.2026, 09:56** (date) · Engywuck → Adam (→ Mick, → Claudia) · Live-Stand `495ca45`, kein Deploy.

## Ergebnis: abgenommen

Bericht gelesen, Klon geprüft: `py_compile` ok, keine undefinierten Namen, Prüfer
`test_empfang_block3` 116/116, `test_konzept_pdf` 22/22, `test_wegwerf_zeilen_a2` 4/4,
`test_menue_schalterstand` 8/8, Doku-Spiegel konsistent (Knopfzahl 12).

**Meine zwei Gegenproben, erwartete Zeile vorher notiert, beide rot an genau dieser Zeile:**

| Eingriff | rot |
|---|---|
| Tastatur zeichnet den Empfangs-Knopf immer als „an" | „die Tastatur zeigt den echten Empfangs-Stand" — 115/116 |
| `cwd` aus dem pandoc-Aufruf entfernt (sauber, nach einem ungültigen ersten Versuch mit SyntaxError) | „pandoc laeuft im Ordner der Quelle, auch wenn das Skript von woanders kommt" — 21/22 |

Dazu aus der Nachtlese 05:35: Prüfzeile 8 (Verdrahtung) beide Gegenproben rot.

## Micks Berichtigungen an meinem Papier — beide berechtigt

- DejaVu gibt es am Mac nicht → Kandidatenliste je Plattform mit Inhaltsprüfung
  (`_schriftordner`). Richtig gebaut; die Tiefe von zwei Ebenen ist als Grenze genannt.
- Der Pfad-Einheit-Text: mein erstes Papier nannte „den Arbeitsordner" ohne Pfad,
  Micks Block trug drei `workspace`-Zeilen — die Selbstauslösung war mein Befund,
  die Berichtigung seine. Steht so richtig in seinem Bericht.

## Seine vier offenen Punkte, beurteilt

1. Briefing als Textmessung: **zulässig** — der Gegenstand ist Text, es gibt kein
   Verhalten zu messen. Bleibt die eine Ausnahme, benannt.
2. `_schriftordner` bricht nach zwei Ebenen ab: bewusst, F-Liste, kein Bau.
3. Pfad-Wache im Tagescheck am Mac ungemessen: **R1 nach dem Deploy** (erster Tagescheck).
4. Schloss am Mac „NICHT GEMESSEN" (kein flock): **R1 nach dem Deploy**; dazu mein
   Nachtrag von 05:35: Schloss aus `/tmp` nach `$HOME` (PrivateTmp). Noch offen.

## Was jetzt wartet (nichts Neues beginnen)

- Bei Mick, klein, im selben Block: Schloss-Pfad; Prüfzeile „venv/lib/README.md
  steht nicht in der Quittung". Dann Laufplan auf Warten.
- Deploy nach Adams Rückkehr: **ein** ff `495ca45..<Spitze>` mit Schritt-0-Zeile;
  `probe-f22` bleibt draußen. R1-Prüfzeile: `/zimmer`, Menü zeigt „● an · Empfang",
  Knopf schaltet, `/empfang_an`/`/empfang_aus`, eine Freigabe, Tagescheck grün,
  Claudia setzt ein PDF aus fremdem Arbeitsverzeichnis.

## Adams Entscheid von heute Morgen (09:5x), notiert

Write/Edit unter `~/workspace` in **alle drei** Reichweiten (Vorgang, Sitzung, bis
Neustart) — der Neustart kommt ohnehin täglich um 04:00 (Hygiene), „bis Neustart"
ist also höchstens ein Tag. **Der Gedächtnis-Ordner (`~/.claude/memory`) bleibt
hart**, weil ein Schreibrecht dort in jede künftige Sitzung hineinwirkt und nicht
mit dem Vorgang endet. Claudias engere Fassung ist damit in einem Punkt übernommen
(Gedächtnis), im anderen nicht (Neustart).

## Texte

**An Mick:** Nachtblock A0–A5 abgenommen (zwei Gegenproben rot, Prüfer grün). Zwei
Kleinigkeiten in denselben Block: Schloss von /tmp nach $HOME/logsync/.lock
(PrivateTmp trennt Dienst und Handlauf); Prüfzeile „venv/lib/README.md steht nicht
in der Quittung" (misst -prune ohne Uhr). Adams Entscheid: Write/Edit unter
~/workspace in alle drei Reichweiten, Gedächtnis-Ordner hart — Vermerk an
_NO_ALWAYS_TOOLS ergänzen. Danach Laufplan auf Warten bis zum Deploy.

**An Claudia:** Dein Vorschlag ist halb übernommen: Gedächtnis-Ordner bleibt hart,
„bis Neustart" bleibt drin, weil der Hygiene-Neustart täglich um vier kommt. Nach
dem Deploy bitte R1: ein PDF aus fremdem Arbeitsverzeichnis ohne gesetzte Schrift,
Rückgabewert 0 erwartet.
