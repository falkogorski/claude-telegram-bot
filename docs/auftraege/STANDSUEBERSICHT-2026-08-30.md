<!-- ROLLE: standsuebersicht -->
# Drehbuch-Stand — Gesamtübersicht

**Stichtag:** 30.08.2026, 23:41 (Systemuhr abgelesen) · **Grundlage:** `MIGRATION.md` @ `fb6bc6f` (1.470 Zeilen)
**Fassung:** vierte, dreimal auf Adams Nachfrage nachgeprüft und einmal neu gebaut
**Erstellt von:** Kontroll-Sitzung (Engywuck) · Format nach der Statusübersicht-Regel in `CLAUDE.md`
**Grafische Fassung:** https://claude.ai/code/artifact/d07904a0-f40a-4c91-84d6-04ee2ef29cff

**Gültigkeit (Regel ⑪):** überholt durch — · **Maßgeblich ist die Status-Zeile im
Drehbuch**, nicht diese Übersicht. Sie ist eine Momentaufnahme vom Stichtag und
veraltet mit jedem Statuswechsel in `MIGRATION.md`.

> **Gemessen, nicht behauptet.** Jeder Stand hier ist am Drehbuch oder am Code
> geprüft. Wo eine Zahl auf meinem Urteil beruht (die Phasengewichte), steht das
> ausdrücklich dabei. Die Chronik der Prüfung samt meiner eigenen Fehler steht
> im Anhang — sie gehört dazu, damit der Nächste sie nicht wiederholt.

**Gesamtstand: 57 % gebaut (gewichtet) · ~62 % nach Adams Handgriffen**

---

## Das Wichtigste in drei Sätzen

1. **Die Migration selbst ist fertig.** Phase 0 und 1 stehen bei 100 %, der Bot
   läuft seit Wochen produktiv auf dem VPS.
2. **Zehn Punkte sind gebaut und warten nur auf Adam**, allen voran die fünf
   Telegram-Kanäle. Das sind Minuten, keine Bautage — und rund fünf Prozentpunkte.
3. **Der Einkommensstrang hat keinen Punkt im Drehbuch.** Beide Momo-Papiere
   existieren, aber als Papier, nicht als Vorhaben. Das ist der wichtigste Fund
   dieser Prüfung.

---

## 1 · Was Adam tut

Nach Wirkung geordnet. Die ersten drei zusammen sind unter einer Stunde und
schalten mehr frei als ein Bautag.

### ① Fünf Telegram-Kanäle anlegen — größter Hebel, ~25 Minuten

**Die vier Häuser:** 🔧 Werkstatt · 🕰️ Nirgendhaus · 🏛️ Handelshaus · 📚 Bibliothek.
Je Gruppe den Forum-Modus einschalten und den Bot einladen — die dreizehn Zimmer
legt er selbst an (`_provision_house`, ratenbegrenzt, idempotent, Verhaltenstest 7/7).
Struktur seit 24.07. final entschieden (v3), Routing-Tabelle steht.

**Und der Erinnerungskanal (7.1) — er kommt zusätzlich.** Gemessen am 30.08.:
Er steht in der 6.6-Struktur nicht drin, ist also **kein Zimmer, sondern ein
eigener Kanal**. Akzeptanzkriterium laut Drehbuch: *„Kanal existiert; Bot ist
Admin mit Schreibrechten."* `scripts/erinnerungen.py` ist gebaut und sagt an
drei Stellen selbst: ohne Kanal hat der Läufer kein Ziel.

**Das entblockt vier Punkte unmittelbar** — 6.5 (Zimmer anlegen), 6.1 (Ausgaben
routen), 4.3 (Ordnerspiegelung) und 7.1 (Kanal selbst) — **und gibt dem ruhenden
Erinnerungs-Läufer 7.2 sein Ziel.**

⚠️ **7.2 wird davon aber noch nicht fertig.** Er braucht zusätzlich den
Kalender-Zugang (7.3) und den Zeitgeber-Block, der bis heute mit dem Vermerk
„NOCH NICHT EINSPIELEN" in `docs/befehlsbloecke-root.md` liegt. Beides ebenfalls
Adams Hand.

*Punkte: 6.6 · 6.5 · 6.1 · 4.3 · 7.1*

### ② Node 22 → 24 auf dem VPS — root, ~15 Minuten

Vorbereitet: Ist-Stand eingefroren, Rückweg aufgeschrieben, Probelauf unter
Node 24 ohne root gefahren (62/62). Ein Prüfskript zieht Adams Anteil auf drei
Befehle zusammen — *vorher*, zwei root-Zeilen, *nachher*.

### ③ Vier kleine Freigaben — zusammen ~15 Minuten, vier Punkte

| Punkt | Was Adam tut | Stand |
|---|---|---|
| 7.3 / 7.4 | Kalender-Zugangsdaten (`ICLOUD_CALDAV_USER`, `…_APP_PASSWORT`) | `kalender.py` steht seit 25.07., „ein Handgriff" |
| 5.14 | Drei Testlinks für die Link-Inbox schicken | gebaut, wartet auf Material |
| 5.36 | Ein Wort zum Wartungsfenster | läuft als Probelauf |
| 6.2 | Eine Entscheidung am iPhone zum Deep-Link | „jetzt ist es eine Zeile" |

### ④ Zwei Entscheidungen, die kein Handgriff sind

- **Wo bekommt der Einkommensstrang seinen Punkt?** Die Momo-Papiere brauchen
  eine Phase — Phase 9 oder eine eigene. Adams Entscheidung, keine Bauentscheidung.
- **iCloud ADP aktivieren** (4.5, seit je offen).

### ⑤ Später, aber nur Adam kann es auslösen

- **Ultracode auf die Eingangs-Absicherung** — erst wenn die Erkennungsseite
  trägt (siehe Kette).
- **Der Gegenleser** (drei Handgriffe: Limit, Datenlöschung, Schlüssel).
- **Der Postfach-Nachweis** als PDF.
- **Die 23 Endlager-Aufträge**, Listenvorschlag steht.

---

## 2 · Die Kette bis zum ersten fremden Postfach

Nach Abhängigkeit geordnet, nicht nach Wunsch — jedes Glied setzt das vorige
voraus. Diese Reihenfolge ist festgeschrieben und ändert sich nicht.

| # | Glied | Wer | Anmerkung |
|---|---|---|---|
| 1 | **Node 22 → 24** | Adams Hand · root | Der einzige Schritt, der heute wirklich wartet. Alles vorbereitet, Rückweg liegt. |
| 2 | **SDK-Fenster** | Mick | Drei Zeilen in `requirements.txt`: SDK 0.2.148, `mcp` und `anyio` auf die im Klon geprüfte Paarung. Werte abgelesen statt getippt. Getrennt vom Node-Sprung. |
| 3 | **Rang 2 der Erkennungsseite abnehmen** | Mick + Kontrolle | Gebaut, aber nicht abgenommen. Die Widerlegung steht darauf: Doku-Zeile zählt in der Bilanz mit, eine Prüfzeile verlangt den Fortbestand der Lücke, der IMAP-Status wird an allen fünf Stellen weggeworfen. |
| 4 | **Ultracode auf die Eingangs-Absicherung** | nur Adam kann starten | Die Prüfstelle, die alle vier Bedingungen deutlicher erfüllt als alles andere im Projekt — und die noch nicht bedient ist. Auslöser ist ein **Zustand, kein Datum**: wenn die Erkennungsseite trägt. Opus 5, maximaler Aufwand. |
| 5 | **Das erste fremde Postfach** | Adam | Stehende Regel: kein Postfach, auch kein Wegwerf-Konto, solange die Erkennungsseite nicht trägt. |

---

## 3 · Die zwölf Phasen

Gewichtet nach **Arbeitsumfang**, nicht nach Punktzahl.
✅ verifiziert · 🔄 läuft/teilweise · ⬜ offen · ⏭️ zurückgestellt

| Phase | Name | Punkte | Verteilung | Grad |
|---|---|---|---|---|
| 0 | Code- & Repo-Vorbereitung | 8 | 8 ✅ | **100 %** |
| 1 | Server-Grundgerüst | 13 | 13 ✅ — *die Migration selbst* | **100 %** |
| 2 | KI-Orchestrierung & Datenschutz | 7 | 4 ✅ · 2 🔄 · 0 ⬜ · 1 ⏭️ | **71 %** |
| 3 | Interfaces | 2 | 0 ✅ · 1 🔄 · 1 ⬜ | **25 %** |
| 4 | Backup & Reproduzierbarkeit | 5 | 2 ✅ · 1 🔄 · 2 ⬜ | **50 %** |
| 5 | Bot-Features | 36 | 17 ✅ · 7 🔄 · 12 ⬜ — *die größte Phase* | **57 %** |
| 6 | Kanal-Routing / Ablage | 6 | 1 ✅ · 4 🔄 · 1 ⬜ — *wartet auf die Gruppen* | **50 %** |
| 7 | Erinnerungskanal | 5 | 1 ✅ · 3 🔄 · 1 ⬜ | **50 %** |
| 8 | Tests & Selbstüberwachung | 7 | 0 ✅ · 6 🔄 · 1 ⬜ — *produktiv, formal offen* | **65 %** |
| 9 | Danach — auf fertige Struktur | 15 | 3 ✅ · 5 🔄 · 7 ⬜ | **37 %** |
| 10 | Abschluss-Audit | 1 | bewusst das Letzte | **0 %** |
| 11 | Backlog | ~16 | erst nach dem Phasen-Audit | — |

**Gesamt: 57 %** (gewichtet) · 104 Punkte · 49 verifiziert · 29 laufend ·
26 offen · 1 zurückgestellt

---

## 4 · Was Mick baut

| Wann | Was |
|---|---|
| **jetzt** | Die verlorene Regel in `CLAUDE.md` eintragen (Wortlaut liegt vor) · Statusfeld **WARTET AUF ADAM** einführen · 5.34-Status berichtigen · Doppelnummer 7.4 auflösen |
| **nach der Kette** | Rang 2 und 3 der Widerlegung — sechs Punkte, im Laufplan notiert. Ohne sie trägt die Erkennungsseite nicht. |
| **Phase 6 · 7** | Erinnerungskanal, anklickbare Original-Datei — die letzten größeren Alltags-Bausteine |
| **Phase 5, Rest** | Zwölf offene Punkte: Multi-Session, TTS opt-in, Recall Stufe 2, Reverse-Navigation, Arbeitsmodus-Umschalter. Alle Komfort, keiner tragend. |
| **Phase 10** | Gesamtaudit — dorthin gehören: Aufräumpass (`bot.py` auf 12.190 Zeilen), Modularisierung, die Nachmessung aller OFFEN-Stände, die 25 fehlenden Drehbuch-Einträge, die 18 Punkte ohne Akzeptanzkriterium |
| **Phase 9.6** | Die Blaupause — das übertragbare Grundwerk. Nach dem Audit. |

---

## 5 · Was in der Ablage nicht stimmt

Vier Prüfdurchgänge mit vier verschiedenen Methoden haben das hier gefunden.
**Nichts davon ist gefährlich — alles davon lässt Arbeit unsichtbar werden.**
Belege im Anhang.

| Zahl | Befund | wohin |
|---|---|---|
| **2** | **Die Momo-Einkommenspapiere haben keinen Punkt.** Der Kurs-Blick maß fünf Wochen ohne Erlösbezug und suchte die Ursache im Arbeitsverhalten — sie liegt in der Ablage. *Was keinen Punkt hat, wird nicht abgearbeitet.* | **Adam** |
| **1** | **Die verlorene Regel.** Am 10.08. richtig erkannt, im Gesprächsverlauf aufgeschrieben — und damit verloren. Steht bis heute nirgends. | **Mick, jetzt** |
| **5** | Gebaute Bausteine ohne jede Drehbuch-Erwähnung — `wachmuster.py` · `mailtext.py` · `mailgestalten.py` · `mail_konto_anlegen.sh` · `node_vollzug_pruefen.sh` | Audit 10.1 |
| **8** | Weitere Bausteine nur im Fließtext erwähnt, ohne eigenen Punkt — darunter `wachposten.py` mit 14 Erwähnungen | Audit 10.1 |
| **12** | von 25 Papieren unter `docs/` stehen nicht im Drehbuch (zwei davon reine Messprotokolle, unkritisch) | Audit 10.1 |
| **18** | Punkte ohne Akzeptanzkriterium, neun davon auch ohne Test-Feld | Audit 10.1 |
| **8** | Punkte auf VERIFIZIERT ohne Verifizierungsdatum — 4.2 · 5.10 · 5.13 · 5.14 · 5.20 · 5.22 · 5.23 · 7.4 | Audit 10.1 |
| **6** | Phasen-Audits nie eingeholt — 3→4, 4→5, 6→7, 7→8, 8→9, 9→Abschluss. Pflicht-Tore mit leeren Feldern. | Adam + Kontrolle |
| **2** | Ablage-Defekte: Nummer **7.4 doppelt vergeben** · **5.34 steht auf OFFEN**, obwohl die Bot-Seite gebaut ist | **Mick, jetzt** |

---
---

# Anhang — Chronik der Prüfung

Wie dieser Stand entstanden ist, was jede Methode gefunden hat und welche Fehler
dabei mir unterlaufen sind. Für Mick zum Nachhalten und für den nächsten, der
dasselbe prüfen muss.

## Die Ausgangslage

Adam bat um einen Gesamtüberblick. Ich habe ihn an `MIGRATION.md` (Commit
`fb6bc6f`, 1.470 Zeilen) gemessen. **Dreimal hat Adam danach nachgehakt, und
dreimal kam etwas heraus** — jedes Mal, weil meine Methode etwas strukturell
nicht sehen konnte.

### Erste Methode — die Punkt-Struktur lesen · Ergebnis: 57 %

Auszählung der Statuswerte (VERIFIZIERT · LÄUFT · OFFEN · BLOCKIERT) über alle
Punkte, gewichtet nach Bauumfang, „läuft" als halb. Ergebnis: 49 verifiziert,
29 laufend, 26 offen, 1 zurückgestellt.

**Ein Stichprobenfund:** Punkt 5.34 steht auf OFFEN — bewusst noch nicht gebaut.
Gemessen: Das Register sagt „Bot-Seite gebaut", `bot.py` enthält acht Stellen
dazu, im Regressionslauf steht `✓ Große Dateien (5.34)` grün.

*Was diese Methode strukturell nicht sehen konnte:* alles, was nicht dem Muster
`### N.N` folgt.

### Zweite Methode — auf Lücken prüfen · Ergebnis: 3 Funde

Nicht mehr die Punkte lesen, sondern die **Nummernvergabe** prüfen: Lücken,
Doppelungen, Position gegen Nummer.

**①** Die Nummer **7.4 ist doppelt vergeben** — Zeile 941 „Kalender und
Erinnerungen über CalDAV", Zeile 1072 „Direkte Links in Erinnerungen". Zwei
Punkte, eine Nummer. `CLAUDE.md` warnt vor genau dem unter *„gleiche Wörter,
andere Bedeutung"* — dort für Nummern zwischen Dokumenten; hier wiederholen sie
sich **innerhalb** eines.

**②** Drei Punkte stehen physisch in Phase 5, obwohl ihre Nummer anderswohin
zeigt: 7.4, 9.8 (Hora), 9.9 (Stundenblumen) — bewusst vorgezogen und dort
einsortiert, wo sie gebaut wurden. **Die Platzierung ist Absicht, die
Doppelnummer nicht.**

**③ Mein Zählfehler daraus:** Mein Parser leitete die Phase aus der *Position*
im Dokument ab statt aus der *Nummer*. Richtig ist: Phase 5 hat 36 Punkte (nicht
39), Phase 7 fünf (nicht vier), Phase 9 fünfzehn (nicht dreizehn).

*Ebenfalls geprüft, ohne Fund:* `MIGRATION-DREHBUCH-ARCHIV.md` (433 Zeilen)
trägt keine Punktnummern und ist im Kopf als überholt gekennzeichnet. **Es gibt
kein zweites gültiges Drehbuch.**

### Dritte Methode — von außen nach innen · Ergebnis: 6 Befundklassen

Die Frage umgedreht: nicht *„stimmt der Status dieses Punktes?"*, sondern
*„was ist gebaut, entschieden oder zugesagt — und hat keinen Punkt?"*
Drei Quellen: der Code-Bestand, die 25 Papiere unter `docs/`, und die 29
Bot-Protokolle vom 14.07. bis 29.08.

**Fünf gebaute Bausteine kommen im Drehbuch überhaupt nicht vor:**
`wachmuster.py` · `mailtext.py` · `mailgestalten.py` · `mail_konto_anlegen.sh` ·
`node_vollzug_pruefen.sh`. Acht weitere sind nur im Fließtext erwähnt, darunter
`wachposten.py` mit **14 Erwähnungen** — ein ganzer Wächter ohne Plan-Eintrag.

**Zwölf von 25 Papieren stehen nicht im Drehbuch**, darunter
`momo-business-skizze` und `momo-gruendungserzaehlung`. Zwei sind reine
Messprotokolle und unkritisch; `bauauftrag-gruendlich-umschalter` ist ein
Bauauftrag ohne Punkt.

**Zwei Chat-Zusagen sind nie in der Ablage angekommen.** Der
Tausenderpunkte-Filter: am 17.07. vereinbart, am 29.07. vom Bot selbst als „nie
gebaut worden" erkannt, am 30.08. schließlich gebaut — und bis heute weder im
Drehbuch noch im Register.

**Und der Fund, der alle anderen erklärt.** Am 10.08. stellte die Bot-Sitzung
fest, dass eine Vereinbarung zwischen Adam und Mick „es in keines der beiden
gemeinsamen Dokumente geschafft" hatte. Sie zog die richtige Lehre:

> „Entscheidungen, die das Verhalten systemweit ändern, gehören ins Drehbuch,
> nicht nur in den Gesprächsverlauf einer einzelnen Sitzung."

**Und schrieb sie in den Gesprächsverlauf.** Gemessen am 30.08.: null Treffer in
`CLAUDE.md`, null im Drehbuch. *Die Lehre aus dem Verlust ist selbst verloren
gegangen, auf genau dem Weg, vor dem sie warnt.*

### Vierte Methode — Audit auf Schlüssigkeit · Ergebnis: 3 Befundklassen

Auf Adams Bitte um ein Gesamtaudit: nicht mehr suchen, *was fehlt*, sondern
prüfen, *ob das Vorhandene in sich stimmt*. Vier Dimensionen, alle mechanisch.

**①** Acht Punkte auf VERIFIZIERT **ohne Verifizierungsdatum** — 4.2, 5.10,
5.13, 5.14, 5.20, 5.22, 5.23, 7.4. Das Feld gehört zum Format; leer heißt:
niemand weiß, wer wann abgenommen hat.

**②** 18 Punkte **ohne Akzeptanzkriterium**, neun davon auch ohne Test-Feld.
Betroffen vor allem die spät hinzugekommenen (5.31–5.36, 9.10–9.15). Ohne
Akzeptanzkriterium ist nicht bestimmbar, wann ein Punkt fertig ist — und genau
das erklärt, warum Phase 8 seit Wochen produktiv läuft und trotzdem auf null
verifizierten Punkten steht.

**③ Bezugsprüfung: sauber.** Keine Verweise auf nicht existierende Punkte. 33
Treffer meines Suchmusters waren durchweg Datumsangaben und Versionsnummern —
einzeln geprüft und verworfen.

**Und sieben scheinbare Status-Widersprüche waren Falsch-Positive.** Mein Muster
suchte „gebaut/steht/läuft" im Blocktext; bei 3.2, 5.19, 9.2, 9.6, 9.11 und 10.1
stammten die Wörter aus dem Kontext, nicht aus einer Fertigmeldung. **Nur 5.34
ist ein echter Widerspruch.**

### Fünfte Methode — die OFFEN-Punkte gegen den Code · Ergebnis: 1 Korrektur, 1 Lücke

Auf Adams Einwand hin vorgezogen, statt sie dem Gesamtaudit zu überlassen: alle
104 Punkte gegen den Code-Bestand gehalten. Das geht, weil der Code die
Punktnummern selbst nennt — in Selbstcheck-Zeilen, Prüfernamen und
Register-Einträgen.

**77 von 104 Punkten werden im Bestand namentlich genannt.** Von den 26
OFFEN-Punkten kamen zehn im Code vor; sieben davon waren Selbstreferenzen des
Drehbuchs, drei wurden einzeln geprüft.

- **5.34 steht falsch auf OFFEN** (Bot-Seite gebaut) — bestätigt die Methode 1.
- **7.1 steht zu Recht auf OFFEN, war aber unvollständig erfasst:** Der
  Erinnerungskanal ist eine **fünfte** Telegram-Gruppe und fehlte in der
  Handlungsliste. Das ist die vollständige Antwort auf Adams Frage nach den
  Gruppen „zusätzlich zum Erinnerungskanal".
- **5.15 und 5.19 sind sauber** — die Code-Treffer waren Verweise, keine
  Fertigmeldungen. (Die „Log-Repo-Ampel (5.19)" ist eine Prüfzeile *innerhalb*
  von 5.19, keine dritte Doppelnummer.)

Damit bleibt **57 % eine Untergrenze, aber eine gemessene**: ein falscher Status
von 104, nicht 26 ungeprüfte.

---

## Was ich dabei falsch gemacht habe

Vier Fehler, alle derselben Familie — und sie gehören hierher, weil der nächste,
der dasselbe prüft, sie sonst wiederholt.

| Fehler | Was passiert ist |
|---|---|
| **Raster zu eng** | Punktmenge über `### N.N` gebildet — elf Phasen-Audits lagen außerhalb, und die Kategorie „wartet auf Adam" steht in keinem Statusfeld, sondern im Fließtext. |
| **Position statt Identität** | Die Phase aus der Stelle im Dokument abgeleitet statt aus der Nummer. Drei vorgezogene Punkte landeten in der falschen Phase. |
| **Prüfschleife ohne Kontrollfall** | Eine Messung meldete „alle Papiere erfasst" — **weil sie nichts prüfte**. Aufgefallen nur durch den Widerspruch zu einer früheren Messung. |
| **Angebaut statt eingearbeitet** | Die ersten drei Nachträge kamen als neue Abschnitte dazu, ohne dass ich die bestehenden nachzog. Die Telegram-Häuser standen im Befund, aber nicht in der Handlungsliste. Diese Fassung ist deshalb **neu gebaut, nicht ergänzt**. |

**Die gemeinsame Ursache:** Ein Suchraster kann nie beweisen, dass außerhalb
seiner selbst nichts liegt. Dafür braucht es ein zweites, das anders geschnitten
ist. Genau deshalb hat die dritte Methode gefunden, was die ersten beiden
strukturell nicht finden konnten — die vierte, was die dritte nicht suchte, und
die fünfte, was keine der vier maß.

---

## Wie die Zahlen zustande kommen

**Quelle:** die Statuswerte des Drehbuchs, maschinell über alle 104 Punkte
ausgezählt (105 Überschriften, eine Nummer doppelt).

**Gewichtung:** „läuft" zählt als halb. Die Phasengewichte sind **mein Urteil
über den Bauumfang**, nicht aus dem Dokument abgelesen — Phase 5 trägt 35 %,
weil dort 36 Punkte und der größte Teil des Codes liegen; Phase 10 nur 3 %,
obwohl ihr Kapitel das längste ist. *Wer anders gewichtet, kommt auf eine andere
Zahl, nicht auf eine andere Größenordnung.*

**Die zweite Zahl (~62 %)** schätzt, wo der Stand nach Adams zehn Handgriffen
läge — im Wesentlichen Phase 6 und 7, die heute fertig gebaut sind und nur auf
Freigaben warten.

**Die Nachmessung ist gefahren** (fünfte Methode, oben). 57 % ist damit eine
gemessene Untergrenze, keine geschätzte.
