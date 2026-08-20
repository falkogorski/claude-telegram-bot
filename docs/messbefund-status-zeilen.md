<!-- ROLLE: messbefund-status-zeilen -->
# Messbefund: Wie viele Status-Zeilen sagen die Unwahrheit?

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich sind die
Status-Zeilen in `MIGRATION.md`** · **Zweck:** Vorarbeit für das Gesamtaudit
(10.1) und Grundlage für Engywucks Kurs-Blick am 25.08.

## Warum das nötig war

Am Vormittag stand **7.3** auf OFFEN, obwohl der Bau seit dem 25.07. komplett
war — es fehlte nur ein Zugang. Das warf die Frage auf, wie oft das noch der
Fall ist. **Gemessen: 106 Status-Zeilen, davon 65 nicht verifiziert, davon 36
auf schlichtem OFFEN.** Genau diese 36 sind die Verdachtsfläche, denn eine
differenzierte Zeile (🔄 mit Erklärung) trägt bereits eine Auskunft.

## Was gemessen wurde — und was bewusst nicht

**Vier Punkte gründlich gegen ihr Akzeptanzkriterium**, nicht sechsunddreißig
oberflächlich. Der Unterschied ist die Lehre des Vormittags: *Ein Fund macht
noch keine Regel* — bei drei von vier Phase-7-Zeilen war der Verdacht
unbegründet, und wer aus einem Fund auf den Rest schließt, ersetzt eine
Falschaussage durch eine größere.

| Punkt | stand auf | gemessen | Urteil |
|---|---|---|---|
| **5.20** Token-Frühwarner | OFFEN | Sidecar seit 14.07., Tagescheck prüft täglich (300 T Warnung / 330 T rot), live „37 Tage alt" | **erfüllt** → berichtigt |
| **9.5** E-Mail-Anbindung | OFFEN | `email_kanal.py` steht, `/mail` da, Prüfer im Regressionslauf — es fehlen nur Adams Zugänge | **gebaut, wartet** → berichtigt |
| **9.4** Approval-Hub | OFFEN | `freigaben.py` = Phase A (Freigabe-Postfach); der HTTP-Endpunkt für fremde Sitzungen fehlt | **halb** → berichtigt |
| **4.3** Memory + Configs ins Repo | OFFEN | Log-Repo enthält Gespräche, Protokolle, Ausarbeitungen — **kein Memory, keine Configs** | **zu Recht offen** |

**Drei von vier waren Falsch-Wahrheiten.** Bei 5.20 besonders deutlich: Der
Punkt ist **vollständig erfüllt** und stand über einen Monat als offen im
Drehbuch.

## Das Muster hinter allen dreien

**Gebaut wurde anders als skizziert — und niemand hat die Zeile nachgezogen.**
5.20 sollte einen eigenen Timer bekommen und wurde eine Zeile im vorhandenen
Tagescheck; 9.4 sollte ein HTTP-Endpunkt werden und wurde erst einmal ein
Postfach; 9.5 wurde fertig gebaut, aber der fehlende Zugang ließ es wie
„nicht angefangen" aussehen.

**Der gemeinsame Nenner ist nicht Nachlässigkeit, sondern eine fehlende
Rückkopplung:** Wer baut, schreibt den Commit — die Status-Zeile im Drehbuch
ist ein zweiter Ort, und der zweite Ort wird vergessen. Dieselbe Klasse wie
der Doku-Spiegel, nur eine Ebene höher.

## Was daraus folgt

**Für das Gesamtaudit (10.1):** Die verbleibenden **32** schlicht-OFFEN-Zeilen
sind ungemessen. Nach dieser Stichprobe ist mit weiteren Falsch-Wahrheiten zu
rechnen — aber **nicht** in gleicher Quote: Die vier hier wurden nach
Code-Spuren ausgewählt, waren also vorausgewählt.

**Für den Kurs-Blick:** Der wahre Fertigstellungsgrad liegt höher als das
Drehbuch behauptet. Das ist keine gute Nachricht, sondern eine unangenehme —
es heißt, dass die Übersicht, nach der geplant wird, ungenau ist.

**Kein neuer Wächter.** Die naheliegende Idee — ein Prüfer, der Status-Zeilen
gegen den Code hält — scheitert daran, dass „gebaut" nur gegen das
**Akzeptanzkriterium** entscheidbar ist, und das ist Prosa. Was hilft, ist die
bestehende Prüfregel: *Status ist ein Befund, keine Behauptung* — angewandt
**vor** jeder Vorlage an Adam, nicht als Automatik.
