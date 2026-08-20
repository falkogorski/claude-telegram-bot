<!-- ROLLE: messbefund-phase7 -->
# Messbefund Phase 7 — was wirklich steht, und der Nachtblock daraus

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich sind die
Status-Zeilen in `MIGRATION.md`** · **Anlass:** Engywucks Auftrag ③ vom 20.08.
(„erst messen, dann bauen")

## Das Ergebnis vorweg

**Von vier Status-Zeilen stand genau eine falsch.** Der Verdacht, dass Phase 7
weiter ist als das Drehbuch sagt, trifft zu — aber nur für **7.3**, und dort
deutlich: Der Bau steht seit dem 25.07. vollständig, es fehlt allein Adams
Zugang. Die anderen drei Punkte sind zu Recht offen; dort ist **nichts**
gebaut.

Das ist der Grund, warum diese Regel „Status ist ein Befund" heißt und nicht
„Status ist meist zu pessimistisch": Hätte ich aus dem einen Fund geschlossen,
die Phase sei fast fertig, wäre der nächste Fehler schon gesetzt.

## Gemessen, Punkt für Punkt

| Punkt | Status-Zeile sagte | Gemessen | Urteil |
|---|---|---|---|
| **7.1** Erinnerungskanal | OFFEN | Kein Kanal, keine Anbindung im Code | **stimmt** |
| **7.2** Scheduler 24/7 | OFFEN | Kein APScheduler, kein Erinnerungs-Zeitgeber auf dem VPS | **stimmt** |
| **7.3** CalDAV-Quelle | OFFEN | `kalender.py` 207 Zeilen, lesen **und** schreiben, Termine **und** Aufgaben · `/termine` + `/aufgaben` registriert · `caldav` 3.2.1 installiert · Prüfer im Regressionslauf | **falsch** → berichtigt |
| **7.4** Direkte Links | OFFEN | Keine Link-Extraktion in `kalender.py` | **stimmt** |

**Was bei 7.3 wirklich fehlt:** `zugang_vorhanden()` meldet `False` —
`ICLOUD_CALDAV_USER` und `ICLOUD_CALDAV_APP_PASSWORT` sind nicht gesetzt.

**Was der vorhandene Prüfer NICHT leistet, und das sagt er selbst:** Seine
sechs Zeilen laufen **ohne Netz und ohne Zugangsdaten**. Er prüft Formatierung
und Fehlerverhalten — dass ein fehlender Zugang zu einer deutlichen Meldung
führt statt zu Leerlauf. **Er prüft nicht, dass die Verbindung trägt.** Ein
grüner Lauf ist hier kein Beleg für eine funktionierende Anbindung, und das
gehört benannt, bevor jemand ihn dafür hält.

## Der Nachtblock

**Gut genug wenn:** 7.4 ist gebaut und mit einer Gegenprobe belegt; 7.2 hat
sein Skript samt Zeitgeber-Vorlage **im Repo, ruhend**; die Status-Zeilen sind
berichtigt; alles, was Adams Hand braucht, steht in der Arbeitsliste. **Nicht**
Teil des Kriteriums: eine laufende Kalenderverbindung — die hängt an Adam.

### Was ohne Adam läuft

1. **7.4 — Links aus Terminen ziehen.** Zoom-/YouTube-/Meet-Adressen aus
   Beschreibung, Ort und Anhang extrahieren und an die lesbare Form anhängen.
   Rein textlich, ohne Netz prüfbar. **Gegenprobe:** ein Termin ohne Link darf
   keine leere Zeile erzeugen. Achtung Vorlese-Kette: Adressen gehören **nicht**
   in die Sprachausgabe (`_strip_markdown_for_tts` filtert sie bereits) — beim
   Bau prüfen, dass die Termin-Zeile diesen Filter nicht umgeht.
2. **7.2 — der Erinnerungs-Läufer, ruhend.** Ein Skript, das fällige Termine
   und Aufgaben liest und in den Kanal legt, dazu eine Zeitgeber-Vorlage in
   `docs/befehlsbloecke-root.md` mit **„NOCH NICHT EINSPIELEN"**.
   **Deterministisch, kein Modell im Pfad** — ein Zeit-Trigger, der ein Modell
   startet, ist AGB-Grauzone (`CLAUDE.md`, Auth-Passage). Zustellung über
   `botenpost.legen()`, nicht selbst gebaut.
   ⚠️ **Ohne 7.1 hat er kein Ziel** — bis dahin legt er in Adams Chat und nennt
   das ausdrücklich in seiner Meldung, statt Vollständigkeit vorzutäuschen.
3. **Fenster-Regel mitdenken:** Der Läufer verlängert keinen bestehenden
   Ablauf, aber er ist ein neuer Absender — die Postfach-Obergrenze von sechs
   Nachrichten je Stunde gilt auch für ihn, und ein Tag mit vielen Terminen ist
   genau der Fall, in dem sie greift. Beim Bau die Bündelung **eine Meldung je
   Lauf** vorsehen, nicht eine je Termin.

### Was Adams Hand braucht (in der Arbeitsliste)

- **iCloud-Zugang für 7.3** — anwendungsspezifisches Kennwort aus dem
  Apple-Konto. **Nicht in den Chat**; der Weg führt über die geschützte
  Umgebung auf dem VPS.
- **Erinnerungskanal für 7.1** — Kanal anlegen, Bot als Administrator, Kennung
  nennen. Ohne ihn bleibt 7.2 ohne Ziel.

## Was ich bewusst nicht getan habe

**Nicht gebaut.** Engywucks Auflage war ausdrücklich: erst der Messbefund. Der
Nachtblock steht als Plan im Laufplan und wartet auf Adams Abend-Anstoß —
diese Sitzung hat keinen eigenen Zeitgeber, das ist am 19.08. gemessen worden.
