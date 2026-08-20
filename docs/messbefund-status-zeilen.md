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

---

# Zweiter Durchgang (20.08.2026, Abendblock) — alle 24 schlicht-OFFEN-Zeilen

Der erste Durchgang maß vier vorausgewählte Punkte. Hier sind es **alle 24**,
die eine nackte Zeile ``- **Status:** OFFEN`` tragen. (Die restlichen offenen
Punkte führen einen Zusatzvermerk und sind damit nicht stillschweigend falsch.)

**Vorgehen wie beim ersten Mal:** erst maschinell nach Code-Spuren, dann die
Verdächtigen einzeln gegen ihr **Akzeptanzkriterium**. Die Lehre des ersten
Durchgangs — *ein Fund macht noch keine Regel* — hat sich erneut bestätigt:
Mehrere Treffer waren Zufall (das Wort „Rechnung“ in „Berechnung“, das
Wort „Klient“ in einer Ampel-Regel).

## Ergebnis

**Sieben der 24 Zeilen sind Falsch-Wahrheiten.** Die übrigen siebzehn stehen
zu Recht auf OFFEN.

| Punkt | Zeile sagt | Gemessen |
|---|---|---|
| **4.2** Zentrale Chat-Logs | OFFEN | **falsch.** Der Log-Sync trägt im Punkttext selbst ein ✅ **UMGESETZT + VERIFIZIERT (23.07.)**; 21 Tagesdateien liegen im Log-Repo. Offen sind nur LobeChat-Logs, die Alt-Log-Übernahme und die iCloud-Löschung → **🔄** |
| **5.4** Sekretariats-Board | OFFEN | **falsch.** ``/status`` rendert Läuft, Warteschlange und Zuletzt erledigt. Fehlt: der Zustand **pausiert** und die Verfall-Regeln → **🔄** |
| **5.10** Konversations-Sync | OFFEN | **falsch.** Das Kriterium lautet „liegen als Markdown in einer Ablage, die Claude Code direkt lesen kann“ — genau das leistet der 4.2-Log-Sync, und die Kontrollsitzung liest daraus. **Erfüllt**, formaler Test offen |
| **5.12** Video-Analyse | OFFEN | **falsch.** ``on_video`` ist gebaut und registriert, zerlegt in Einzelbilder und transkribiert die Tonspur (H1, 25.07.). Der YouTube-Weg läuft über die Link-Inbox (5.14) → **🔄** |
| **5.13** Pinned → Memory | OFFEN | **falsch.** Handler gebaut **und registriert**, schreibt nach ``telegram-pinned.md``, dazu der Zweig für persönliche Notizen. Fehlt allein der geforderte **Zitat-Bezug** — kein Verweis auf die Originalnachricht → **🔄** |
| **6.2** Deep-Link | OFFEN | **falsch, und der lehrreichste Fund.** ``_channel_post_url`` erzeugt ``tg://privatepost``, ``_channel_title_link_html`` nutzt es. **Aber die vier Hinweis-Stellen rufen ``_channel_url`` auf** — den ``https://t.me/c/``-Weg, also genau den Browser-Umweg, den 6.2 beseitigen soll. **Gebaut, aber nicht verdrahtet** → **🔄** |
| **6.4** Kanal als Link | OFFEN | **falsch.** Kanal-Erwähnungen werden als anklickbare Links gerendert (vier Aufrufstellen). Dasselbe Verdrahtungsproblem wie 6.2 → **🔄** |

## Die siebzehn, die zu Recht offen stehen

**Ohne jede Code-Spur:** 5.1 (Multi-Session), 5.3 (mehrere PDFs), 5.11
(Gesamtmemory-Suche), 5.16 (``/woist``), 5.24 (Session-Rotation), 5.26
(Transkriptions-Sichtbarkeit), 6.3 (Original-Datei im Kanal), 9.1 (Azure-TTS),
9.2 (Piper/Kokoro lokal), 9.3 (Demo-Klon).

**Mit Spur, aber Zufallstreffer:** 5.17 (die Treffer waren Kapitel-Labels für
den Ausgabekanal, nicht Recall-Bewusstsein), 5.19 (Wortstamm „rechnung“ in
„Berechnung“).

**Sachlich richtig offen:** 5.7 (die Restart-Meldung geht **ohne** TTS hinaus,
obwohl die Regel es verlangt — hängt an 5.8), 7.1 (Adams Handgriff), 8.4
(auf Phase 10 terminiert), 10.1 (das Audit selbst), 4.3 (im ersten Durchgang
gemessen).

## Zwei Nebenbefunde, die beim Messen aufgefallen sind

**① ``/status`` gibt Sekunden aus.** Die Zeile „letzte Regung vor {n}s“
verletzt die eigene Zeitform-Regel, die Sekundenzahlen ausdrücklich aus dem
Dialog verbannt. Kleiner Eingriff, gehört aber gefixt, wenn 5.4 angefasst wird.

**② Ein Dateihandle ohne ``with``** im Pinned-Handler
(``mem_file.open("a").write(...)``). CPython schließt es über die Zählung,
sauber ist es nicht. Gehört zum 5.13-Rest.

## Die Lehre, die über die Zahlen hinausgeht

**Sechs der sieben Falsch-Wahrheiten sind Teilbauten, keine Fertigstellungen.**
Das ist kein Zufall: Ein Punkt wird zu drei Vierteln gebaut, der Rest wartet
auf etwas anderes — und weil „fertig“ nicht stimmt, bleibt „OFFEN“
stehen. **Die Status-Werte haben für diesen häufigsten aller Zustände kein
gutes Wort.** ``🔄`` gibt es, aber es fühlt sich wie eine Ausrede an, und
deshalb greift man zu OFFEN.

**Und 6.2 zeigt die schärfere Variante:** Der Code war da, funktionierte, und
wurde an der entscheidenden Stelle nicht gerufen. Eine Spurensuche, die nur
fragt „gibt es die Funktion“, hätte 6.2 als erfüllt gemeldet. Die Frage
muss lauten: **wird sie dort gerufen, wo das Kriterium es verlangt?**
