# Bauauftrag — Weniger Freigabe-Drücke: die Wache steht am Ausgang

**Zustand: vereinbart, nicht gebaut**
**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau)
**Angelegt:** 29.08.2026, 00:45 Uhr
**Ersetzt:** die offene Rang-3b-Frage aus `2026-08-26_bauauftrag-bash-sitzungsfreigabe.md`
und beantwortet den Befund `docs/auftraege/BEFUND-bash-sitzungsfreigabe.md`
**Überholt außerdem:** `2026-08-28_bauauftrag-bash-freigaben-eindaemmen.md`
(28.08., 20:50 Uhr) — dort steht dieselbe Messung über 409 Aufrufe. Ich hatte
beim Schreiben dieser Fassung nicht nachgesehen und sie ein zweites Mal gebaut.
Der ältere Auftrag trägt seit dem 29.08., 00:50 Uhr einen Zustandskopf und ist
**nicht mehr zu bauen**. Maßgeblich ist allein diese Fassung.

**Adams Auflage vom 29.08.2026, 00:30 Uhr, wörtlich:** „So wenig Drücke wie
möglich." Davor um 00:28 Uhr die Begründung, die den Rang erklärt: „Es ist einfach
super anstrengend. Man verliert die Lust. … Ich gucke mir nicht jede Datei vorher
an, bevor ich die freigebe. Oder welche Befehle sich hinter den Hieroglyphen
befinden."

---

## Warum das ein Sicherheits- und kein Bequemlichkeitsauftrag ist

**Eine Rückfrage, die 352 Mal in sieben Tagen kommt und ungelesen bestätigt wird,
schützt nicht. Sie gewöhnt ab.** Der eine gefährliche Befehl geht genau deshalb
durch — er sieht aus wie die 351 davor.

Adams Einwand ist damit sicherheitstechnisch stärker als die bisherige Bauform.
Der Schutz gehört an eine Stelle, die unabhängig von seiner Aufmerksamkeit wirkt.

**Der reale Angriffsweg, benannt:** Nicht ein Einbruch auf dem Server, sondern
Inhalte, die die Sitzung liest — abgerufene Webseiten, weitergeleitete Bilder,
PDF-Dateien, Ablagen anderer Sitzungen. Ein Sprachmodell trennt Daten und
Anweisung nicht zuverlässig. **Eine Positivliste wirkt auch dann, wenn das Modell
hereingelegt wurde; ein Dialog, der weggedrückt wird, wirkt dann nicht.**

---

## Die Messung, auf der der Auftrag steht

Mick hat im Befund zu Recht angemerkt, dass die Bot-Protokolle nur den
Werkzeugnamen führen, nicht den Befehl. **Die Grundlage existiert an anderer
Stelle:** Die Sitzungsprotokolle unter
`~/.claude/projects/-home-claudebot-workspace/*.jsonl` führen den vollständigen
Befehl je Aufruf.

Ausgewertet am 29.08.2026, 00:20 Uhr, über die letzten sieben Tage —
**448 Bash-Aufrufe**, erstes Wort:

| Befehl | Anzahl | | Befehl | Anzahl |
|---|---:|---|---|---:|
| grep | 105 | | cat | 9 |
| cd (verkettet) | 68 | | printf | 9 |
| ls | 64 | | tail | 8 |
| Postfach-Auftrag schreiben | 44 | | python3 | 8 |
| sed | 29 | | find | 7 |
| pandoc | 21 | | python | 4 |
| systemctl | 11 | | head | 3 |
| curl | 10 | | übrige | ~48 |

**Alle 352 Dialoge liefen an `_is_repo_read_cmd` vorbei** — der Grund ist in zwei
Punkten benannt: Die Liste gilt nur für das Repo, gearbeitet wird überwiegend im
Arbeitsordner; und sie schließt Verkettungen aus, während `cd <ordner> && <lies>`
die übliche Form ist.

---

## Auftrag 1 — Vier Bereiche, in denen ohne Rückfrage gearbeitet wird

**Stelle:** `bot.py`, Berechtigungszweig um Zeile 2938 (`_is_repo_read_cmd`).

Die Bereiche, jeweils samt Unterordnern:

1. `/home/claudebot/claude-telegram-bot` — **nur lesen** (die Schreibsperre der
   Bot-Sitzung bleibt unberührt und wird hier nicht angefasst)
2. `/home/claudebot/workspace` — lesen und schreiben
3. `/home/claudebot/postfach` — lesen und schreiben
4. die Log-Ordner — **nur lesen**

**Ohne Rückfrage erlaubt:**

- **Lesen und Suchen:** `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `stat`,
  `du`, `df`, `file`, `sort`, `uniq`, `diff`
- **Lesende Repo-Abfragen:** `git log`, `git status`, `git diff`, `git show`
- **Schreiben innerhalb von Arbeitsordner und Postfach:** `sed`, `printf`, `echo`,
  `cp`, `mv`, `mkdir`, `tee` — **Quelle wie Ziel müssen in Bereich 2 oder 3 liegen**
- **Dokumentenerzeugung:** `pandoc`, `weasyprint` — Ausgabe in Bereich 2
- **Zustandsabfragen ohne Wirkung:** `free`, `uptime`, `date`, `sleep`, `which`,
  `ps`, `systemctl status` (nur `status`)
- **Eine Verkettungsform:** `cd <erlaubter Pfad> && <erlaubter Befehl>` — genau ein
  `&&`, erster Teil ausschließlich `cd`

---

## Auftrag 2 — Was gesperrt bleibt, ohne Dialog

**Diese Fälle werden abgewiesen, nicht vorgelegt.** Ein Dialog wäre hier die
falsche Antwort: Er verlagert eine Entscheidung auf Adam, die er nachts um halb
eins nicht prüfen kann.

- **Geheimnisse:** jeder Pfad, der `.env`, `credentials`, `token`, `secret`, `key`,
  `.ssh`, `.gnupg` enthält — auch lesend, auch innerhalb der vier Bereiche
- **`/home/claudebot/.claude`** samt Unterordnern (Sitzungsprotokolle, Einstellungen)
- **Alles außerhalb der vier Bereiche** fällt nicht unter die Freigabe

---

## Auftrag 3 — Was dialogpflichtig bleibt, und dort wird gelesen

Rund 40 Fälle je Woche statt 352. **Weil sie selten sind, ist der Dialog dann eine
echte Prüfung.**

- **Jeder Weg nach draußen:** `curl`, `wget`, `ssh`, `scp`, `git push`, `git pull`,
  Versand jeder Art
- **Eingriffe in den Betrieb:** `systemctl` außer `status`, `sudo`, `kill`,
  `pkill`, `chmod`, `chown`, `pip install`, Paketverwaltung
- **Löschen:** `rm`, `rmdir`, `truncate` — auch im Arbeitsordner
- **Schreiben außerhalb** von Arbeitsordner und Postfach
- **Beliebige Programmausführung:** `python`, `python3`, `bash`, `sh`, `perl`,
  `node`, `make`, `eval`, ausführbare Skripte

**Der letzte Punkt trägt die ganze Konstruktion.** Ein Skript kann jede Grenze
dieser Liste umgehen — wäre es frei, wären die Aufträge 1 und 2 wirkungslos. Das
kostet etwa zwölf Drücke je Woche und ist der Preis dafür, dass die übrigen
Freigaben verantwortbar sind.

---

## Auftrag 4 — Die Positivliste ist ein Fließtext-Problem, kein Wortlisten-Problem

**Auflage:** Die Prüfung greift auf der **zerlegten** Befehlszeile, nicht auf der
Zeichenkette. Folgendes muss zur Abweisung führen, auch wenn das erste Wort
erlaubt ist:

- weitere Verkettungen (`;`, `|`, `||`, ein zweites `&&`, Zeilenumbruch)
- Ersetzungen (`$(…)`, Rückwärtsanführung, `<(…)`)
- Umlenkung nach außerhalb der Bereiche (`>`, `>>`)
- Pfadaufstiege (`..`) und symbolische Verweise, die aus den Bereichen führen —
  **Pfade werden vor der Prüfung aufgelöst**

**Grund:** `grep muster datei; curl fremde-adresse` beginnt mit einem erlaubten
Wort. Eine Prüfung auf das erste Wort allein ist keine Grenze.

---

## Auftrag 5 — Die Befehlsart wird protokolliert

Micks Nebenbefund wird übernommen: Je Bash-Aufruf wird die **Befehlsart**
mitgeschrieben (erstes Wort ohne Argumente, dazu erlaubt/abgewiesen und der
Bereich). Damit ist nach einem Vorfall nachvollziehbar, was durchging — und die
Liste lässt sich nach einigen Wochen an der Messung nachschärfen.

**Kein Geheimnis kann darin stehen**, weil nur das erste Wort und der Bereichsname
abgelegt werden.

---

## Was kann brechen und wer merkt es

| Was | Wer merkt es | Vorkehrung |
|---|---|---|
| **Ein Pfad zeigt über einen symbolischen Verweis aus dem Bereich heraus** — die Freigabe greift auf etwas, das anderswo liegt | Niemand | Pfade vor der Prüfung auflösen, dann gegen die Bereiche halten. Ein Prüfsatz mit einem Verweis aus dem Arbeitsordner heraus gehört in den Regressionslauf |
| **Die Zerlegung übersieht eine Verkettungsform** — die Liste ist offen, ohne dass es auffällt | Niemand, bis etwas geschieht | Prüfzeilen für jede Form aus Auftrag 4, einzeln. Bei einer unbekannten Form wird abgewiesen, nicht durchgelassen |
| **Ein neues Werkzeug taucht auf** (etwa `rg`, `jq`) und landet dauerhaft im Dialog | Adam, an der wieder steigenden Zahl | Auftrag 5 macht es sichtbar. Nachtragen ist ein Handgriff |
| **Die Geheimnis-Sperre greift zu weit** und blockiert legitime Arbeit — eine Datei heißt `keywords.md` | Die Sitzung, sofort | Auf Pfadbestandteile prüfen, nicht auf Teilzeichenketten in Dateinamen. Prüfsatz mit `keywords.md` erwartet Durchlass |
| **Die Freigabe wird als „alles erlaubt" missverstanden** und später stillschweigend erweitert | Niemand | Die Liste steht an einer Stelle, mit Kommentar auf diesen Auftrag. Eine Erweiterung ist ein Bauauftrag, keine Zeile nebenbei |
| **Der Dialog bleibt trotzdem häufig** — die Messung war unvollständig | Adam, binnen eines Tages | Auftrag 5 liefert die Zahl. Nach einer Woche gegenmessen: unter 50 Dialoge je Woche gilt als erreicht |

---

## Was Engywuck entscheiden darf

1. **Ob `sed` und das Schreiben ins Postfach wirklich hineingehören.** Adams
   Auflage lautet „so wenig Drücke wie möglich", er hat den Unterschied zwischen
   Lesen und Schreiben ausdrücklich nicht beurteilen wollen. Ich habe sie
   aufgenommen, weil sie ausschließlich in Bereichen wirken, die der Sitzung
   ohnehin gehören. **Das ist meine Setzung, nicht seine Entscheidung** — wenn sie
   zu weit geht, gehört sie herausgenommen.
2. **Ob `cp` und `mv` innerhalb der Bereiche tragen.** Sie können eine Datei
   überschreiben. Innerhalb des Arbeitsordners ist das rückholbar, im Postfach
   erzeugt es einen Auftrag — und der Postfach-Versand hat eine eigene
   Geheimnisprüfung.
3. **Ob die Log-Ordner als vierter Bereich nötig sind** oder ob sie über das Repo
   ohnehin abgedeckt sind.
4. **Ob die Grenze von 50 Dialogen je Woche** als Maß taugt.

---

## Bezug zu bestehenden Aufträgen

- `docs/auftraege/BEFUND-bash-sitzungsfreigabe.md` — dieser Auftrag beantwortet die
  dort offen gelassene Wahl. Es wird **keine Verbotsliste** (mit K5 verworfen),
  sondern eine **nach Bereichen gefasste Positivliste**.
- Rang 3a ist gebaut und seit dem 29.08.2026, 00:07 Uhr in Betrieb — der Dialog
  sagt jetzt, worüber er entscheiden lässt. Die verbleibenden 40 Dialoge treffen
  damit auf einen lesbaren Text.
- `2026-08-28_bauauftrag-dritter-knopf-aendern.md` bleibt unberührt und liegt
  dahinter.
