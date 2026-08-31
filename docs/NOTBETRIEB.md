<!-- ROLLE: notbetrieb -->
# Notbetrieb — Unabhängigkeits-Stufe 1

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** Commit-Zeit dieses Stands ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.

**Zweck:** Wenn der gewohnte Weg ausfällt — Anthropic nicht erreichbar, Token
abgelaufen, Kontingent leer, Netz weg —, soll Adam nicht ratlos sein. Diese
Seite ist bewusst so geschrieben, dass sie **ohne mich** trägt.

**Die Leitlinie:** Der Bot darf **stumm** werden, aber nichts **verlieren**. Die
Nachrichten-Persistenz (5.2) und die Kontingent-Pause (5.31) sind darauf gebaut:
Was Adam schickt, liegt in der Warteschlange, bis wieder gearbeitet werden kann.

---

## 1. Rollenprofil „Hauptagent" — modellneutral

Damit ein Ersatz beurteilt werden kann, muss beschrieben sein, was die Rolle
verlangt — **ohne** einen Modellnamen zu nennen. Genau daran scheitern
Ersatz-Diskussionen sonst: Man vergleicht Namen statt Anforderungen.

| Anforderung | Warum sie zur Rolle gehört | Ohne sie passiert |
|---|---|---|
| **Werkzeuge zuverlässig aufrufen** | Der Agent arbeitet über Dateien, Suche, Befehle — nicht über Prosa | Antworten klingen richtig und bewirken nichts |
| **Lange Anweisungen aushalten** | `CLAUDE.md` plus Memory plus Auftrag sind umfangreich | Regeln fallen unbemerkt aus dem Blick |
| **Sich an Verhaltensregeln halten** | Kostenregel, Geheimnis-Schutz, Repo-Schreibverbot sind unverhandelbar | Der Schaden entsteht genau dort, wo niemand hinsieht |
| **Mehrschrittig planen** | Ein Auftrag umfasst Bauen, Prüfen, Dokumentieren, Melden | Halbe Arbeit, als fertig gemeldet |
| **Eigene Unsicherheit benennen** | „ungeprüft" muss dastehen, wenn es ungeprüft ist | Selbstbewusst falsch ist schlimmer als ehrlich unsicher |
| **Deutsch auf gehobenem Niveau** | Adams ausdrückliche Anforderung, nicht Kosmetik | Die Zusammenarbeit verliert ihren Charakter |

**Zur Einordnung:** Ein kleines lokales Modell erfüllt die ersten beiden Zeilen
schon nicht — es kann Neben-Inferenzen übernehmen (Beschriften, Einordnen), aber
nicht die Rolle. Das ist keine Wertung, sondern der Grund, warum Stufe 2 an einen
**Auslöser** gebunden ist und nicht vorgebaut wird.

## 2. Der Notweg über einen API-Schlüssel — dokumentiert, NICHT aktiviert

> 💰 **Warnung, bevor irgendetwas davon getan wird:** Ein `ANTHROPIC_API_KEY`
> bucht **pro Token** ab, vollständig getrennt vom Abo, und hat **Vorrang** vor
> dem Abo-Token, sobald er gesetzt ist. Wer ihn versehentlich dauerhaft setzt,
> bezahlt jede Nachricht doppelt — einmal im Abo, einmal auf Rechnung.
> **Deshalb liegt hier kein Schlüssel, und es ist keiner im System.**

Nur wenn Adam es ausdrücklich will:

1. Schlüssel auf `console.anthropic.com` erzeugen und dort **eine
   Ausgabengrenze** setzen — zuerst die Grenze, dann den Schlüssel benutzen.
2. Ihn **nicht** in die dauerhafte Umgebungsdatei schreiben, sondern nur für
   einen einzelnen Lauf mitgeben. So endet der bezahlte Betrieb von selbst.
3. Nach dem Notbetrieb prüfen, dass er wieder verschwunden ist:
   der Selbstcheck meldet ohnehin, wenn ein API-Schlüssel gesetzt ist.

**Der Rückweg ist wichtiger als der Notweg:** Sobald das Abo wieder trägt,
Schlüssel weg, Bot neu starten, Verbrauch auf der Konsole gegenprüfen.

## 3. Notbetriebs-Drill — die Handgriffe, geprobt

Der Drill ist **einmal wirklich durchgespielt** worden, nicht nur aufgeschrieben.
Was dabei herauskam, steht in der rechten Spalte.

| Lage | Handgriff | Geprobt am 25.07.2026 |
|---|---|---|
| „Der Bot antwortet nicht" | `systemctl is-active claude-telegram-bot` | Der Dienst gilt als aktiv, auch wenn der Prozess gerade neu startet — **die Prozessliste ist die verlässlichere Auskunft** |
| „Läuft er wirklich?" | **`systemctl show claude-telegram-bot -p MainPID`** | Die **einzige** Auskunft, die sich nicht selbst mitzählt. Liefert genau eine Kennung |
| „Ich will die Prozesse sehen" | `pgrep -af "bot[.]py" \| grep -v "pgrep\|bash -c"` | Genau **eine** Zeile ist richtig — **mit** dem Filter. Ohne ihn lügt die Zählung (siehe Kasten unten) |
| „Ist er gesund oder nur am Leben?" | `bash scripts/regressionstest.sh` | Der Lauf **nennt seinen Sollwert selbst** („30/30" am 26.07.). Hier stand einmal eine feste Zahl — sie war schon veraltet, als sie jemand brauchte. „Läuft" ist kein Gesundheitsnachweis |
| „Er läuft, aber nichts geht" | `cat ~/.claude/anmeldung-gekippt` | Liegt die Datei, ist die **Anmeldung** hin, nicht der Bot: Ein neues Abo-Token muss her (`claude setup-token`), alles andere ist gesund. Der Bot legt sie im Augenblick des Bruchs selbst an und räumt sie beim ersten gelungenen Lauf wieder weg |
| „Der Bot ist einfach weg" | `journalctl -u claude-telegram-bot \| grep -i "killed process"` | Verdacht **Speichermangel**: Der Kernel beendet ohne Vorwarnung. `free -m` zeigt die Lage; ist kein Auslagerungsbereich da, gibt es kein Abfedern (Befehlsblock Schritt 4a) |
| „Er kommt nicht hoch" | Nichts von Hand — **erst nachsehen, ob ein Rückweg da ist** | Ohne gesicherten Stand nicht eingreifen; der Start-Wächter (B1) hält sich an dieselbe Regel |
| „Ich brauche einen früheren Stand" | Anleitung in `WIEDERANLAUF.md`, Abschnitt Rücksprung | Abzweigen statt zurücksetzen; danach immer der Regressionslauf |
| „Alles ist weg" | `docs/REBUILD.md` plus das tägliche Bündel im Backup | 14 datierte Vollkopien in Rotation |

### Was der Drill zutage gebracht hat

Der eigentliche Gewinn des Probens — beides wäre sonst im Ernstfall aufgefallen,
unter Zeitdruck, mit Adam am Handy:

**1. `systemctl is-active` sagt „active", auch während der Prozess gerade neu
startet.** Als Gesundheitsauskunft ist es also wertlos; es beantwortet „ist der
Dienst eingeschaltet", nicht „arbeitet er".

**2. Die Prozess-Zählung lügt — und zwar hartnäckiger als gedacht.** Im Drill
meldete `pgrep -af "bot[.]py"` **zwei** Treffer, obwohl nur einer lief. Der
Grund: In derselben Befehlszeile stand weiter hinten die Zeichenfolge
`python bot.py` — und `pgrep -f` durchsucht die **vollständige Befehlszeile
jedes Prozesses**, also auch die der eigenen Hülle. Es ist damit **nicht** nur
das eine bekannte Muster, das täuscht: **jede** Suche, deren eigener Befehl den
gesuchten Text enthält, zählt sich selbst mit.

Die Lehre gilt über diesen Fall hinaus: **Ein Messwerkzeug, das Teil des
gemessenen Feldes ist, braucht einen Nachweis, dass es sich selbst herausrechnet.**
Deshalb steht oben `MainPID` an erster Stelle — systemd weiß, welchen Prozess es
gestartet hat, und kann sich nicht selbst verwechseln. (Der Start-Wächter aus B1
filtert aus demselben Grund seinen eigenen Prozess ausdrücklich heraus; dass
dieser Griff nötig war, ist mit dem heutigen Befund belegt statt nur vermutet.)

## 3a. „Ich bin unterwegs und will nur wissen: lebt er?" `[NEU 2026-08-31]`

> **GitHub-App (oder Browser) öffnen → privates Repo `claude-bot-logs` → Zeit
> des letzten Commits ansehen.** Der Log-Abgleich schreibt **alle fünf
> Minuten**; ist der letzte Commit älter als **zwanzig Minuten**, stimmt etwas
> nicht — Server, Abgleich oder Netz. **Das Ausbleiben der Commits ist selbst
> der Alarm**; dieser Blick braucht weder Bot noch Terminal.

**Warum zwanzig und nicht zwei Stunden.** Der Wert stammt aus einem Archivstand
vom 18.08., als der Abgleich stündlich lief. **Seit dem 19.08., 23:15 läuft er
alle fünf Minuten** (`docs/befehlsbloecke-root.md` führt die stündliche Setzung
ausdrücklich als *überholt*). Mit zwei Stunden wären **vierundzwanzig
ausgefallene Läufe** nötig, bevor die Zeile etwas sagt — das ist keine
Notfall-Auskunft mehr.

### Warum die Zeile nicht an einem ruhigen Tag falsch anschlägt

**Die Sorge war berechtigt und ist gemessen:** `scripts/log_sync.sh` committet
**nicht**, wenn sich nichts geändert hat. Eine enge Schwelle könnte also an
einem stillen Tag anschlagen, ohne dass etwas kaputt ist — und ein Wächter, der
falsch anschlägt, ist binnen einer Woche abgeschaltet.

**Gemessen am echten Verlauf (31.08.):** **805 Commits seit dem 19.08., 23:15 —
kein einziger Abstand über zwanzig Minuten**, Median fünf Minuten. Darin liegen
zwölf Tage einschließlich Adams zwölftägiger Abwesenheit, in der niemand dem
Bot schrieb.

**Und der Grund ist strukturell, nicht Glück:** In den Nacht-Commits ändert sich
**`zustand.json`** — der Lagebericht der **Stundenblume**
(`scripts/stundenblume.py`). Sie schreibt fortlaufend, unabhängig davon, ob
jemand den Bot benutzt. **Der Herzschlag, den es zu bauen gälte, existiert
bereits** — er heißt Belegkette.

**⚠️ Was diese Zusicherung trägt, und wo sie endet:** Sie hängt **an der
Stundenblume**. Steht die still — das ist am 20.08. vorgekommen —, fällt der
Herzschlag weg, und die Zwanzig-Minuten-Zeile schlägt an.

**Das ist kein Fehlalarm, sondern ein zusätzlicher echter Fall:** Eine stehende
Belegkette *ist* eine Störung, und zwar eine, die von außen wie Ruhe aussieht.
Die Notfall-Zeile erkennt damit drei Dinge statt zwei — Server, Abgleich, Netz
**und** eine stille Wache.

**Kein Herzschlag ist deshalb zu bauen.** Wer später einen einbaut, sollte
wissen, dass er damit genau diese dritte Erkennung wieder abschaltet.

---

## 4. Was Stufe 2 auslöst — der Auslöser, nicht die Route

Stufe 2 wird **nicht vorgebaut**. Sie beginnt, wenn eines davon eintritt:

- Das Kontingent-Limit greift **mehr als zweimal pro Woche** und blockiert dabei
  Arbeit, die nicht warten kann (Ebene 1 zählt das mit, siehe 5.31).
- Anthropic ist **länger als einen Tag** nicht erreichbar.
- Die Nutzungsbedingungen ändern sich so, dass der Eigenbetrieb über das Abo
  nicht mehr tragbar ist — der AGB-Wachposten (5.21) meldet das.

Bis dahin gilt: **lokal für Nebenarbeiten (steht), Abo für die Hauptrolle,
Notweg dokumentiert.** Die Cloud-Zweitroute ist mit 2.4 bewusst übersprungen.
