**Zweck: ABLAGE** · **Zu tun: nichts. Die nächste Sitzung findet hier, wie sie nach einem Kontingent-Stopp von selbst weiterarbeitet.**

# Wiederaufnahme nach Kontingent-Stopp — Mechanik

Stand 24.09.2026, 05:4x. Auftrag: Engywucks Zettel F1, Teil 2 (Adams Wort: *„was auch immer dafür gebaut werden muss, soll er bauen"*). Rahmen: `CLAUDE.md`, Präzisierung vom 20.08. Eine Automatik beginnt keine Arbeit von sich aus. Eine Arbeit, die Adam begonnen hat, darf sie zu Ende führen.

## Was es dafür gibt, gemessen

1. **Den Kontingentstand lesen, deterministisch:** Das Werkzeug `get_usage` der App liefert je Fenster den Verbrauch in Prozent und die **Rückstellzeit** (`resetsAt`). Am 24.09. um 05:4x gemessen: Fünf-Stunden-Fenster bei 29 %, Rückstellung 08:10 UTC, also 10:10 Ortszeit. **Mehrverbrauch ist abgeschaltet** (`extraUsage.enabled: false`). Am Limit bleibt die Sitzung also stehen, und es wird nichts abgebucht. Den Schalter stellt nur Adam um; bleibt er aus, gilt die 💰-Regel gar nicht erst.
2. **Einen Wecker stellen:** `CronCreate` einmalig (`recurring: false`). Er reiht einen Auftrag in die Sitzung ein, sobald sie ruht. Das wurde in der Nacht zum 24.09. gemessen. **Grenze:** Der Wecker gilt nur für diese Sitzung und nur, solange die App offen ist. Auf die Platte kommt nichts.

## Der Ablauf

**Der Wecker muss vor dem Stopp stehen.** Nach dem Stopp kann die Sitzung nichts mehr tun, auch keinen Wecker stellen. „Je Unterbrechung ein Wecker" heißt deshalb: Einer steht auf die Rückstellzeit des Fensters, in dem gerade gearbeitet wird.

1. **Beim Beginn eines unbeaufsichtigten Blocks** oder spätestens bei 80 % des Fünf-Stunden-Fensters: `get_usage` lesen und einen Wecker auf `resetsAt` plus drei Minuten stellen.
2. **Im Kopf des Laufplans eine Zeile**, damit Adam es sieht: `# WIEDERAUFNAHME aktiv bis <Uhrzeit>` (Wecker-Kennung dahinter).
3. **Der Auftrag des Weckers** lautet: `.claude/laufplan.md` lesen. Steht dort `WARTET: ja` oder ist kein Punkt offen, sofort enden und nichts tun. Sonst am ersten offenen Punkt weitermachen. Regressionslauf vor jedem Commit, Bericht in der Berichtsdatei des Laufs, **kein Deploy**.
4. **Beim Aufwachen:** Hat die Sitzung weitergearbeitet, einen neuen Wecker für das neue Fenster stellen. So entsteht eine Kette, aber kein Dauertakt.
5. **Ist die Arbeit fertig:** Wecker zurücknehmen (`CronDelete`), Kopfzeile entfernen, `WARTET: ja` setzen. **Ein Wecker ohne offene Arbeit würde einen Modelllauf ohne Grund auslösen.**

## Was nicht gebaut wurde, und warum

- **Kein Zeitgeber auf dem Mac, der die Sitzung von außen weckt.** Laut Zettel wird das am ersten echten Stopp gemessen, nicht vorher. Nötig wäre er nur, wenn der Wecker den Stopp nicht übersteht. Er wäre ein eigener Baustein mit Zugang zur App, also eine zweite Stelle mit Zugriff.
- **Kein API-Schlüssel, keine zweite Stelle mit dem Abo-Token.** Die Sitzung arbeitet in der App mit ihrem eigenen Abo-Zugang weiter.
- **Heute kein Wecker gestellt:** Nach Block 3 Teil 2 und dem Belegketten-Punkt ist nichts mehr offen, das ohne Adam ginge. Block 5, Auftrag 4b wartet auf den Deploy von Block 2. Der Punkt „Gedächtnis-Pfad im Prompt" hat keinen Wortlaut. **Ein Wecker jetzt wäre ein Lauf ohne Grund.**

## Beim ersten echten Stopp messen

- Feuert der Wecker nach dem Stopp, und nimmt die Sitzung den Auftrag an?
- Wie meldet die App das Limit mitten in einem Zug: Bricht er ab, oder endet er sauber?
- Wird ein Zug, der abbricht, beim Aufwachen wiederholt, oder bleibt er halb stehen? Halb Geschriebenes zeigt `git status`, und wegen der Regel *kein Commit neben einer Dateiänderung* ist dabei nie ein halber Commit.
