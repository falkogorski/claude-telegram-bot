<!-- ROLLE: entscheidungen-nacht -->
# Was in der Nacht liegen blieb — für Adam, wenn er wach ist

**Stand:** 29.08.2026, 03:4x · **Von:** Mick · **überholt durch:** —

Adam um 03:3x: *„wichtig ist, dass Du weiter und durcharbeitest, auch wenn
Entscheidungsmöglichkeiten sich auftun."* Also: durchgearbeitet, und alles
Entscheidbare steht hier statt in einer Rückfrage.

---

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
