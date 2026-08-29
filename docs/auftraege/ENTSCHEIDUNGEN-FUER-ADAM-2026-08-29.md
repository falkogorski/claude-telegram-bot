<!-- ROLLE: entscheidungen-nacht -->
# Was in der Nacht liegen blieb — für Adam, wenn er wach ist

**Stand:** 29.08.2026, 03:4x · **Von:** Mick · **überholt durch:** —

Adam um 03:3x: *„wichtig ist, dass Du weiter und durcharbeitest, auch wenn
Entscheidungsmöglichkeiten sich auftun."* Also: durchgearbeitet, und alles
Entscheidbare steht hier statt in einer Rückfrage.

---

> **`[STAND 29.08., 11:40]` Vier Punkte sind erledigt** — ① Deploy, ④ Mai-Spiegel
> und die beiden Spiegel-Fragen aus deiner Antwort. Sie stehen unten
> durchgestrichen statt gelöscht, damit die Begründung nachlesbar bleibt.
> **`[STAND 29.08., 17:3x]` ③ und ⑥ sind entschieden:** Sprung auf 0.2.148,
> aber **im Fenster nach Node**, und `mcp` + `anyio` werden mitgepinnt. Die
> abgelesenen Werte und alle Schritte stehen in `PRUEFLISTE-sdk-sprung.md`.
> **`[STAND 29.08., 18:0x]` ② und ⑧ sind ebenfalls entschieden bzw. erledigt:**
> Ultracode läuft **nach** Rang 2 der Erkennungsseite und **vor** dem ersten
> Postfach (Einzelheiten und Begründung: `ZETTEL-ultracode-wann.md`) (Kette: Node → SDK → Erkennungsseite → Ultracode → Postfach). Der
> Container-Probelauf entfällt — er wurde **ohne root und ohne Docker**
> gefahren (Archiv entpackt, PATH nur in einer Subshell), voller
> Regressionslauf 62/62 unter Node 24.
> **Offen bleiben: ⑦ Node-Termin (heute Abend?) ·
> ⑨ die drei Gegenleser-Handgriffe · ⑩ der Postfach-Nachweis.**

## ~~① Der Deploy der Bash-Positivliste~~ — ERLEDIGT 29.08., 11:31

Engywucks Gegenprüfung hat freigegeben, nach **einer** Reparatur: Meine zwei
neuen Prüfer legten ihre Wegwerf-Ordner unter `/private/tmp` an — **den Pfad
gibt es nur auf macOS**, auf dem VPS starben beide beim Import. Der
Betriebscode war einwandfrei; **tot war der Prüfer, und zwar stumm.**

Repariert, Symlink-Gegenprobe erneut gefahren, die Klasse in
`test_zielumgebung.sh` abgefangen. Dann deployt: **61/61 auf dem VPS**, beide
Prüfer leben dort, Bot neu gestartet und aktiv.

Meine Zurückhaltung war laut Engywuck richtig — ohne sie stünde die Schranke
jetzt mit totem Prüfer im Betrieb.

## ~~④ Der tote Mai-Spiegel~~ — ENTSCHIEDEN UND ERSETZT

Ersetzt statt repariert, mit demselben Zuschnitt wie der Papierweg.
**Der erste Lauf beziffert die Lücke: 221 von 368 Dateien waren seit dem
25. Mai ohne zweite Kopie, 107 MB.** Alter Agent entladen und ausgetragen.

## ~~Spiegel-Fragen~~ — ALLE DREI UMGESETZT

Zeitgeber entladen · Papierweg an den Sitzungsstart und auf Zuruf ·
Mai-Spiegel ersetzt. Beim ersten Lauf fiel eine Dubletten-Falle auf, die
niemand gesucht hatte — sie ist geschlossen.

---

### Die ursprüngliche Begründung zu ①, zum Nachlesen

## ① Der Deploy der Bash-Positivliste — meine einzige bewusste Zurückhaltung

**Gebaut, geprüft, gepusht — aber NICHT auf den VPS gebracht.**

**Warum nicht:** Die Positivliste ändert das Verhalten des laufenden Bots
erheblich. Ein Fehler darin wirkt in beide Richtungen — sie könnte Befehle
freigeben, die in den Dialog gehören, oder die Arbeit ausbremsen. Das ist der
Fall, den die Abwesenheits-Regel mit *„gebaut-und-ruhend darf warten;
gebaut-und-wachend nicht"* meint.

**Der Gegeneinwand ist mir bewusst** und er ist gut: Am 29.07. lag ein
fertiger Wächter-Fix ungedeployt, sein Wächter starb, und es fiel
einundzwanzig Tage nicht auf. Der Unterschied: Damals bedeutete das Fehlen
**Blindheit**. Hier bedeutet das voreilige Einspielen **Risiko**. Bei einer
neuen Fähigkeit ist Warten richtig, bei einem Wächter-Fix falsch.

**Was du entscheidest:** sofort deployen, oder erst nach einer
Widerlegungs-Gegenprüfung durch Engywuck. Ich empfehle die Gegenprüfung —
das ist ein Sicherheitspfad, und die Regel ① der Abwesenheits-Kontrolle
verlangt sie ohnehin vor dem Abhaken.

Deploy-Befehl, wenn du willst:

```
ssh <vps> "cd /home/claudebot/claude-telegram-bot && git pull && systemctl restart claude-telegram-bot"
```

---

## ② Ultracode auf die Positivliste?

Die vier Bedingungen aus `CLAUDE.md` sind **alle erfüllt**: Es gibt Code · ein
Fehler bliebe still · der Schaden wäre groß und schwer rückholbar · der Code
ist stabil. Das ist genau die Sorte Schrankenlogik, für die das Werkzeug
gedacht ist.

**Ich kann es nicht selbst auslösen** — der Befehl ist nutzergetriggert, und
starten müsste ihn ohnehin die Kontroll-Rolle, nicht ich als Erbauer. Der zu
prüfende Stand ist `8908d3a`, gepusht.

---

## ③ SDK-Sprung: 0.2.148 statt 0.2.144

Der Auftrag nennt 0.2.144. Verfügbar ist **0.2.148**; die vier Fassungen
dazwischen sind reine CLI-Nachzüge ohne eigene SDK-Änderung. Derselbe
Aufwand, vier Fassungen weniger Rückstand. Befund:
`BEFUND-sdk-aenderungsnotizen-0.2.127-0.2.148.md`.

---

## ④ Der tote Mai-Spiegel

`com.jakuna.mirror-ki` läuft alle fünf Minuten, 330 Läufe verzeichnet,
Rückgabewert 78, seit dem 25.05. keine Protokollzeile. Nicht angefasst, wie
gewünscht. Die Diagnose steht im Chat; prüfbar in einer Minute, indem du die
App einmal von Hand startest.

**Zu entscheiden:** reparieren, ersetzen oder abschalten. Ein Zeitgeber, der
seit drei Monaten scheitert, ist kein Backup — er ist ein Versprechen, das
niemand einlöst.

---

## ⑤ Was Engywuck noch offen hat

Aus seinem Nachtpaket, unverändert bei ihm: dritter Knopf (Variante B) ·
Zahlen-Sprachausgabe · Karteileichen-Auftrag · Gegenleser scharfstellen
(deine Hand).

Und weiterhin bei dir: die **23 Aufträge im Endlager** (Listen-Vorschlag
steht), der **Node-Vollzugstermin**, der **Gegenleser-Schlüssel**.

---

## Was ich ohne Rückfrage entschieden habe, damit du es prüfen kannst

- **Reihenfolge geändert:** ① Bash → **Rang A** → ② Updates, statt Engywucks
  ① → ② → ③. Grund: Der Update-Auftrag sperrt den SDK-Block ausdrücklich, bis
  Rang A steht — *„Ein Netz mit bekannter Masche darf nicht gespannt werden,
  während man darüber läuft."* Das Nachtpaket hebt diese Vorbedingung nicht
  auf, also gilt sie.
- **Geheimnis-Bremse im iCloud-Spiegel** eingebaut, obwohl nicht bestellt.
  Der Zielordner ist versioniert; ein selbsttätiger Spiegel nimmt dir den
  Blick auf das, was kopiert wird. Nach dem ersten Fehlalarm auf Länge statt
  auf Präfix nachgeschärft.
- **`sleep` auf fünf Minuten gedeckelt.** Es steht in Auftrag 1 unter den
  wirkungslosen Zustandsabfragen — `sleep 99999` wäre aber eine blockierte
  Sitzung ohne Dialog. Setzung, kein Messwert.
- **Eine Sicherheits-Prüfzeile geändert** (`alte Bash-Freigabe greift nicht
  mehr`): Sie testete mit `ls -la`, das jetzt frei ist. Auf `curl`
  umgestellt und eine Gegenprobe danebengestellt, damit die Änderung nicht
  als Aufweichung durchgeht. Das ist die Stelle, die eine Gegenprüfung am
  ehesten verdient.

---

# Nachtrag, 04:3x — was in der zweiten Hälfte der Nacht dazukam

## ⑥ Der SDK-Sprung ist geprüft, aber nicht übernommen

Klon-Lauf mit 0.2.148: **58/59**, und die eine rote Zeile ist die
Pin-Divergenz — der Wächter, der genau das melden soll. Befund:
`BEFUND-klonlauf-sdk-0.2.148.md`.

**Der Pin ist bewusst nicht nachgezogen**, weil `.148` statt `.144` deine
Entscheidung ist (Punkt ③ oben). Der eigentliche Fund daraus liegt bereits im
Hauptbaum und wirkt **mit beiden Fassungen**: Ein Zugangsfehler wäre unerkannt
geblieben, wenn der Anbietertext nur in der Nutzlast steht.

**Was noch bei dir liegt:** die globale CLI auf dem VPS
(`@anthropic-ai/claude-code` 2.1.209 → 2.1.24x). Das ist ein npm-Eingriff mit
root — deine Hand, nicht meine.

## ⑦ Node: die Begründung im Auftrag stimmte nicht

Der Auftrag sagt, Node trage die Claude-CLI. **Gemessen trifft das nicht zu** —
die CLI ist eine eigenständige Binärdatei und läuft nachweislich ohne Node im
Pfad. Der Sprung ist damit deutlich harmloser als angenommen.

**Zwei Dinge bleiben trotzdem:** Er braucht root auf der Maschine, die den Bot
trägt — und die CLI ist **doppelt installiert**, was eine globale
npm-Aktualisierung stillschweigend halbieren kann. Alles im Zettel
`ZETTEL-node-22-auf-24.md`, samt Rückweg und sechs Prüfschritten.

**Zu entscheiden:** wann. Der Vollzug dauert mit dem Zettel eine
Viertelstunde.

## ⑧ Der Probelauf im Container fehlt

Rang 9 verlangt einen Probelauf mit Node 24 im Klon. Der fehlt, und der Grund
steht im Zettel: Auf dem Mac wäre er wertlos (andere Architektur, andere
Binärdatei), auf dem VPS wäre er ein Eingriff statt eines Klons.

**Der saubere Weg ist ein Container** — das ist ein eigener kleiner
Bauschritt und braucht Docker auf dem VPS, das dort heute nicht liegt.
**Zu entscheiden:** ob wir das aufsetzen oder ohne Probelauf springen.

## ⑨ Der Gegenleser wartet auf genau drei Handgriffe von dir

Gebaut ist alles, was ohne Zugang baubar ist. Was fehlt, ist ausdrücklich
deine Handlung — und in dieser Reihenfolge:

1. **Ausgabenlimit beim Anbieter setzen**, bevor ein Schlüssel im System liegt
   (10 € Mistral, 10 € OVHcloud, 5 € xAI — Deckel 30 €, dein Entscheid).
2. **Datenlöschung**: bei Mistral beantragen, bei xAI in der Konsole
   einschalten, falls verfügbar. Ist sie es nicht, liegen die Vorlagen dort
   dreißig Tage — das solltest du vorher wissen.
3. **Schlüssel anlegen.** Erst danach ein Rauchtest, erst danach einhängen.

## ⑩ Der Postfach-Nachweis für pymupdf

Der Update-Auftrag verlangt ausdrücklich mehr als einen grünen Lauf: ein PDF
über das Postfach zustellen, den Weg, den du täglich nutzt. **Der PDF-Pfad
selbst ist ausgeführt geprüft** (erzeugt, ausgelesen, Umlaute erhalten); die
Zustellung hätte dir um vier Uhr morgens eine Nachricht geschickt. Ein Wort
von dir, und ich löse sie aus.
