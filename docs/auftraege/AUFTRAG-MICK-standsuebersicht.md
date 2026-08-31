<!-- ROLLE: auftrag-standsuebersicht -->
# Auftrag an Mick — Gegenprüfung und Verankerung der Standsübersicht

**Kopf:** 30.08.2026, 23:48 (Systemuhr abgelesen) · von der Kontroll-Sitzung
**Grundlage:** `MIGRATION.md` @ `fb6bc6f`
**Beilagen:** `STANDSUEBERSICHT-2026-08-30.md` · `REGEL-fuer-CLAUDE-md.md`
**Grafische Fassung:** https://claude.ai/code/artifact/d07904a0-f40a-4c91-84d6-04ee2ef29cff

## 🛑 Das Tor: erst prüfen, dann anfassen

**Teil A wird vollständig abgearbeitet, bevor die erste Zeile aus Teil B
geändert wird.** Nicht als Empfehlung — als Bedingung.

**Der Grund, und er ist nicht formal:** *Jeder einzelne der fünf Eingriffe in
Teil B ist die Umsetzung eines Befunds von mir.* „5.34 steht falsch", „7.4 ist
doppelt", „die Regel fehlt in `CLAUDE.md`" — das sind meine Messungen, nicht
Tatsachen, die du vorfindest. **Wer sie zuerst ausführt, hat sie damit
angenommen.** Eine Gegenprüfung danach prüft ein Dokument, das schon nach meinem
Befund umgeschrieben ist — sie kann gar nichts mehr finden.

Die Eingriffe sind mechanisch und gehen schnell von der Hand. Genau deshalb
steht das hier: **die Versuchung ist, sie zuerst wegzuarbeiten.**

**Konkret heißt das, für jeden der fünf Punkte einzeln:**

| Prüf das selbst, bevor du ihn änderst | Woran |
|---|---|
| Fehlt die Regel wirklich? | `grep` über `CLAUDE.md` **und** `MIGRATION.md` — ich habe null Treffer gemessen |
| Ist 5.34 wirklich gebaut? | `bot.py`, das Register, der Regressionslauf — nicht mein Satz darüber |
| Ist 7.4 wirklich doppelt? | `MIGRATION.md` Z. 941 und Z. 1072, beide öffnen |
| Ist 7.1 wirklich kein Zimmer? | die 6.6-Struktur gegen 7.1 halten |
| Warten die zehn wirklich nur auf Adam? | am Code, nicht an der Statuszeile |

**Findest du einen Befund falsch, wird er nicht gebaut** — dann kommt er zurück
an mich, mit dem, was du stattdessen gemessen hast. Ein zurückgewiesener Befund
ist mir lieber als ein ausgeführter falscher; Letzterer schreibt meinen Irrtum
ins Drehbuch, wo ihn nach vier Wochen niemand mehr von einer Tatsache
unterscheidet.

**Teil C (die Verankerung im Repo) kommt zuletzt**, nach Teil B — sonst
verankerst du eine Fassung, die deine eigene Prüfung noch ändert.

---

## Wie du damit umgehst

**Diese Datei zuerst lesen** — die anderen beiden sind ihre Beilagen, nicht
eigenständige Aufträge.

| Datei | Was sie ist | Wohin sie geht |
|---|---|---|
| **diese** | Der Auftrag | nirgendwo — sie ist erledigt, wenn du fertig bist |
| `STANDSUEBERSICHT-2026-08-30.md` | Der Gegenstand der Prüfung | **ins Repo** als `docs/standsuebersicht-2026-08-30.md` (Teil C) |
| `REGEL-fuer-CLAUDE-md.md` | Textquelle, kein Dokument | Wortlaut wandert in `CLAUDE.md`, die Datei selbst nirgendwohin |

**Modus:** Durchlauf. Die Weitergabe-Blöcke sind Meilensteine, keine Halteschilder —
was Adams Zutun braucht, wandert ans Ende.

**Modell:** Die fünf Ablage-Eingriffe in Teil B sind mechanisch — **Sonnet als
Unter-Sitzung genügt und ist hier die richtige Wahl.** Die Gegenprüfung in Teil A
ist Urteilsarbeit und gehört auf **Opus 5, mittlere Denktiefe**. Wenn du davon
abweichst, nenn es im Bericht — eine Zeile reicht.

---

## Teil A — Der Prüfauftrag

**Finde, was daran nicht trägt.** Nicht: prüfe, ob es stimmt.

Fünf Methoden haben die Übersicht erzeugt; die fünfte hat noch etwas gefunden,
was die vier davor nicht sahen. **Die Wahrscheinlichkeit, dass eine sechste
nichts findet, ist erfahrungsgemäß niedrig** — und du bist die Instanz, die den
Code täglich anfasst und darum anders schneidet als ich.

**Vier Angriffspunkte, an denen ich selbst am wenigsten sicher bin:**

1. **Die Phasengewichte.** Sie sind *mein Urteil* über den Bauumfang, nicht aus
   dem Dokument abgelesen — Phase 5 trägt 35 %, Phase 10 nur 3 %. Du weißt
   besser, wie viel Arbeit in einem Punkt steckt. **Wenn die Gewichte grob
   danebenliegen, ist die 57 % falsch, nicht nur ungenau.**

2. **Die zehn Punkte, die „nur auf Adam warten".** Ich habe sie aus den
   Statuszeilen und dem Fließtext zusammengetragen. Prüf am Code, ob wirklich
   *nur noch* Adams Handgriff fehlt — oder ob dahinter noch Bauarbeit liegt, die
   ich übersehen habe. **Bei 7.2 ist mir das genau so passiert:** Ich hatte ihn
   als „entblockt" geführt; tatsächlich braucht er drei Dinge, nicht eines.

3. **Die 13 namenlosen Bausteine.** Fünf ohne jede Erwähnung, acht nur im
   Fließtext. Prüf, ob es mehr sind — mein Raster war der Dateibestand gegen die
   Punktnummern, und ein Raster kann nie beweisen, dass außerhalb seiner selbst
   nichts liegt.

4. **Die sieben Falsch-Positive.** Bei 3.2, 5.19, 9.2, 9.6, 9.11 und 10.1 habe
   ich Status-Widersprüche als Kontext-Treffer verworfen. **Wenn einer davon doch
   echt ist, habe ich ihn weggeprüft.** Das ist der Fehlertyp, der am
   schwersten auffällt.

**Was ich ausdrücklich nicht brauche:** eine Bestätigung, dass die Zahlen
stimmen. Wer bestätigen soll, bestätigt.

---

## Teil B — Was du änderst (Ablage, keine Bauarbeit)

Fünf Eingriffe, alle klein, alle einzeln committet.

| # | Was | Wo | Beleg |
|---|---|---|---|
| 1 | **Die verlorene Regel eintragen** | `CLAUDE.md` | Wortlaut liegt fertig in `REGEL-fuer-CLAUDE-md.md`. Am 10.08. richtig erkannt, in den Gesprächsverlauf geschrieben — und damit verloren. |
| 2 | **Statusfeld `WARTET AUF ADAM` einführen** | `MIGRATION.md`, Format-Kopf + die zehn Punkte | Heute steht „wartet auf Adam" nur im Fließtext. Deshalb hat mein erstes Raster die ganze Kategorie nicht gesehen. |
| 3 | **5.34 berichtigen** | `MIGRATION.md` | Steht auf OFFEN. Register sagt „Bot-Seite gebaut", `bot.py` hat acht Stellen, Regressionslauf zeigt `✓ Große Dateien (5.34)` grün. |
| 4 | **Doppelnummer 7.4 auflösen** | `MIGRATION.md` Z. 941 + Z. 1072 | „Kalender und Erinnerungen über CalDAV" und „Direkte Links in Erinnerungen" tragen dieselbe Nummer. Eine der beiden bekommt eine freie. |
| 5 | **7.1 als eigenen Kanal kenntlich machen** | `MIGRATION.md` 7.1 + 6.6 | Der Erinnerungskanal ist **kein Zimmer** der 6.6-Struktur, sondern eine fünfte Telegram-Gruppe. Steht heute nirgends so da — die nächste Sitzung hält ihn sonst wieder für ein Zimmer. |

**Zu 2 — die Zehn:** 6.6 · 6.5 · 6.1 · 4.3 · 7.1 · 7.3 · 5.14 · 5.36 · 6.2 ·
und der Zeitgeber-Block für 7.2 (liegt mit dem Vermerk „NOCH NICHT EINSPIELEN"
in `docs/befehlsbloecke-root.md`).

---

## Teil C — Der Nachtrag, und er ist der eigentliche Punkt

**Diese Übersicht darf nicht enden wie ihr eigener Hauptbefund.**

Sie sagt an neun Stellen dasselbe: *Was keinen Punkt hat, wird nicht
abgearbeitet.* Die Momo-Papiere, die dreizehn Bausteine, die verlorene Regel —
alle sind auf demselben Weg verschwunden. **Wenn diese Übersicht nur ein
Artefakt-Link und eine Markdown-Datei im Chat bleibt, wiederholt sie exakt den
Fehler, den sie diagnostiziert.** In vier Wochen erinnert sich niemand an sie.

Deshalb, als sechster Eingriff und ausdrücklich getrennt von den fünf oben:

**Die Übersicht kommt ins Repo**, als `docs/standsuebersicht-2026-08-30.md`,
mit Rollen-Marker `<!-- ROLLE: standsuebersicht -->` in der ersten Zeile — nach
dem Grundsatz „Struktur über Namen". Dazu:

- **Ein Verweis aus `MIGRATION.md`**, im Kopf oder bei Punkt 10.1, damit das
  Abschluss-Audit die Fundliste vorfindet statt sie neu zu erheben.
- **Ein Eintrag in `ABHAENGIGKEITEN.md`** — sie hängt an `MIGRATION.md`
  (Nummernvergabe, Statuswerte) und veraltet mit jedem Statuswechsel.
- **Ein Gültigkeits-Kopf** nach Regel ⑪: Stichtag · „überholt durch —" ·
  „maßgeblich ist die Status-Zeile im Drehbuch". Ohne den liest sich diese
  Fassung in vier Wochen wie der gültige Stand.

**Was ausdrücklich NICHT jetzt gebaut wird:** die dreizehn namenlosen Bausteine
bekommen jetzt keine dreizehn neuen Punkte, und die zwölf Papiere keine zwölf.
Das ist Arbeit für das Abschluss-Audit 10.1 — **aber sie ist ab jetzt
aufgeschrieben statt nur gemessen.** Genau das ist der Unterschied zwischen
einem Befund und einer Ablage.

---

## Teil D — Was NICHT dein Auftrag ist

- **Der Einkommensstrang.** Wo die Momo-Papiere ihren Punkt bekommen, ist Adams
  Entscheidung — Phase 9 oder eine eigene Phase. Du baust den Platz erst, wenn
  er entschieden hat. *Bitte leite das nicht ab.*
- **Die sechs nie eingeholten Phasen-Audits.** Das sind Tore zwischen Adam und
  der Kontrolle, keine Bauarbeit.
- **Ultracode.** Nutzergetriggert, und der Auslöser ist ein Zustand, kein Datum:
  wenn die Erkennungsseite trägt.

---

## Gut genug wenn:

**Teil A ist vor Teil B gelaufen** — das ist die erste Bedingung, nicht die
letzte. Dann: die fünf Ablage-Eingriffe sind committet, die Übersicht liegt mit Rollen-Marker
und Gültigkeits-Kopf im Repo und ist aus `MIGRATION.md` erreichbar — **und deine
Gegenprüfung hat entweder etwas gefunden, oder du kannst benennen, an welcher
Stelle du gesucht und nichts gefunden hast.**

Eine Gegenprüfung, die nie etwas findet, ist selbst der Befund.

**Und vor jedem Commit:** `bash scripts/regressionstest.sh`. Auch bei reiner
Doku-Arbeit — „ist ja nur ein Doku-Commit" hat dieselbe Form wie „ist ja nur ein
Messwerkzeug", und die hat am 23.08. zwei rote Prüfungen auf den VPS gebracht.
