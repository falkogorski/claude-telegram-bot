> **Zweck: WEITERGABE → Mick** (Abschnitt 2 für Claudia, über Adam) ·
> **Zu tun:** fünf Entscheide Adams umsetzen, dazu M-4 mit Werkzeugkette.
> Reihenfolge wie nummeriert. Ergänzt die Abnahme `e3596fd` von heute Vormittag.

# Adams Entscheide vom 09.09. — und was sie auslösen

**Stichtag:** 09.09.2026, 12:03 (`date`, Berlin) · **Adams Wort, per
Auswahl:** ① ja zu den fünf Punkten des fließenden Dialogs · ② `git init`
auf dem Server · ③ Riegel zu lassen · ④ Regeln und Register nach
`Business/_Regeln`, eine Ebene über Deko · ⑤ Hardware nicht jetzt, Entscheid
bei Stufe ④ · dazu M-4: **pandoc + typst**.

## 1 · An Mick

**E-1 — Fließender Dialog: alle fünf Punkte entschieden.** Drehbuch: die
Wiedervorlage-Zeile (Kap. „Offene Wiedervorlagen") auf **entschieden 09.09.**,
mit den fünf Antworten in einem Satz je Punkt; Punkt 5.1 Multi-Session
bekommt den Verweis auf Claudias Konzept „Sitzung je Zimmer" als seine
konkrete Form und den Zusatz **„Zielbild: Sekretärin als eigene, werkzeuglose
Dialogsitzung neben den Zimmern — F1 bleibt"** (mein Papier vom 06.09. liegt
unter `docs/auftraege/`). Kein Bau — der Zimmer-Bauauftrag kommt von Claudia,
ich prüfe ihn gegen den Zuschnitt, dann baust du. Gedanke „zweiter Chat"
(02.09.): die offene Frage *Sitzung oder Ansicht* ist damit **Sitzung** —
eintragen, nicht neu fragen.

**E-2 — `git init` im Rechnungsprojekt, auf dem Server (M-10).** Als
`claudebot` per SSH, kein root: `.gitignore` mit `.venv/`, `output/`,
`ausgang/`, `__pycache__/`; erster Commit „Stand 09.09.2026"; **kein Remote,
nie GitHub** — `daten/` trägt Bank und Steuernummer. Mac: `~/Projects/rechnungen`
wird zu `~/Projects/rechnungen-alt-20260903` und ein Klon tritt an seine
Stelle (`git clone claudebot:~/workspace/rechnungen`). **Wer committet?**
Claudia soll dafür kein `git` in die Hand nehmen — Empfehlung: der Tagescheck
(4 Uhr, modellfrei) macht einen Tagesstand-Commit, wenn etwas geändert ist;
das gibt Historie ohne neue Regel für sie. Deine Bauform, wenn du eine
bessere siehst. Register-Zeile *„Mac-Kopie ist Vorlage und Rückweg"* →
*„Server ist Master mit Historie, Mac ist Klon"*; Änderungsdoku vom 02.09.
bekommt den Schlusssatz, dass der Rückweg jetzt `git log` heißt. Backup Z-2
deckt `.git/` mit ab — nachmessen im Trockenlauf. **Prüfzeile:**
`ssh claudebot 'git -C ~/workspace/rechnungen log --oneline | head -3'`.

**E-3 — Riegel: zu lassen (M-11).** Nichts setzen. Drehbuch: Probezeit
25.08.–09.09. ausgewertet, **0 von 14 grün**, Riegel schließt sich am 10.09.
selbst; wieder öffnen, wenn das Freigabe-Postfach benutzt wird. Dazu die
Kleinigkeit aus der Abnahme: Tagescheck-Wortlaut am Stichtag „läuft heute
ab", danach „abgelaufen".

**E-4 — `Business/_Regeln`, eine Ebene über Deko.** In
`rechnungen_ablegen.sh` **eine benannte Ausnahme, kein zweiter Wurzelpfad:**
relative Pfade, die mit `_Regeln/` beginnen, landen unter
`$(dirname "$ZIEL")/_Regeln/` statt unter `$ZIEL/_Regeln/`. Alles andere
unverändert, `-u` überschreibt Neueres — genau eine Fassung je Datei.
**Prüfer (im vorhandenen `test_rechnungen_ablegen.py`):** Datei unter
`ausgang/_Regeln/Rechnungsregeln.pdf` → liegt unter `Business/_Regeln/`,
**nichts** unter `Business/Deko/_Regeln/`; zweiter Lauf mit neuerer Fassung
→ ersetzt, kein Doppel. Gegenprobe: Ausnahme entfernen → genau diese Zeile
rot. Der Ordner `Business/_Regeln` wird **nicht** angelegt (Adams Ablage) —
fehlt er, gilt die bestehende 78-Regel; Adam legt ihn einmal an.

**E-5 — Hardware: nicht jetzt.** Drehbuch-Zeile bei 5.31/Heimtunnel:
*„Entscheid bei Stufe ④ (lokaler Dialogstrang), Adam 09.09."* Sonst nichts.

**M-4 — PDF-Skript, meine Einschätzung: pandoc + typst.** Drei Gründe:
typst liegt schon auf dem Server (Rechnungen, Liberation Sans, `~/.local/bin`),
es wird **eine** Kette statt zwei, und typst hat außer Paketimporten keinen
Netzweg. **Auflagen, an der richtigen Stelle:** kein `#import "@preview/…"`
(typst lädt Pakete beim ersten Gebrauch aus dem Netz — das Skript weist
Markdown mit Paketimport benannt ab oder läuft mit gefülltem
`--package-path`); `--root` auf den Arbeitsbereich, damit `#image()` nichts
außerhalb liest; `--font-path` auf den Projekt-Schriftordner **plus**
`--ignore-system-fonts`, damit Mac und Server dieselbe PDF erzeugen (Micks
Hinweis, richtig); pandoc ohne `--extract-media` von URLs. **Was sich ändert
und Adam wissen soll:** Claudias Papiere sehen danach aus wie deine
Doppel-Lieferungen, nicht mehr wie ihr `.konzept-style.css` — gewollt
(„wie bei den anderen Dateien"). **Prüfer:** Markdown mit Netzbild → PDF
entsteht ohne Netzzugriff (Attrappe); Markdown mit `@preview`-Import →
benannt abgewiesen; Ausgabe nur in Arbeitsbereiche. Dann in
`BENANNTE_SKRIPTE`, wie das Postfach-Skript.

**Reihenfolge:** E-4 (klein, Adam wartet darauf) → E-2 → E-1/E-3/E-5
(Ablage, ein Commit) → M-4 → M-8 (Fable, klein) → **eigener Block:** M-9 → M-7.

## 2 · Für Claudia — über Adam, drei Zeilen

1. **Der Zimmer-Bauauftrag kann jetzt geschrieben werden** — Adam hat alle
   fünf Punkte entschieden; Zuschnitt: Sitzung je Zimmer (dein Konzept vom
   05.09.), Sekretärin als eigene werkzeuglose Dialogsitzung **neben** den
   Zimmern, Verteiler ist Code. Ich prüfe ihn, Mick baut.
2. **Register und Rechnungsregeln als PDF nach `ausgang/_Regeln/`** legen,
   bei jeder Änderung neu — Route A trägt sie nach `Business/_Regeln/` und
   ersetzt die alte Fassung. Kein neuer Weg, der Chat-Versand bleibt daneben.
   Route A ist seit dem 04.09. gebaut; der Stand eines Bauauftrags steht im
   Drehbuch, nicht in deiner Liste.
3. **Pfade immer in Anführungszeichen** — ein Ordner mit `&` im Namen hat am
   07.09. zwei Dialoge erzeugt, die kein Fehler der Schranke waren.

## Bei mir

Zimmer-Bauauftrag prüfen, sobald er da ist · Nachprüfung E-2/E-4/M-4 am
Code · Wochenauswertung 16.09.: die erste gemessene Dialogzahl.
