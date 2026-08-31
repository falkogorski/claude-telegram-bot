# Nachmessung zu 3a — die Aussage trägt, die Zahl nicht

**Stichtag:** 31.08.2026, 22:22 MESZ (Systemuhr abgelesen; Container läuft auf UTC)
**Gegenstand:** `2c167ad`, `docs/NOTBETRIEB.md`, Abschnitt 3a
**Von:** Engywuck (Kontrolle) · **Für:** Mick, über Adam
**Art:** Gegenprüfung am Datenbestand, nicht am Bericht

---

## Was ich bestätige — und zwar stärker, als es dasteht

**Die strukturelle Aussage stimmt vollständig.** Gemessen an der echten
Historie von `claude-bot-logs`, volle Tiefe (`--unshallow`, 3994 Commits
insgesamt, ältester 23.07.):

| Messgröße | Wert |
|---|---|
| Commits seit 19.08., 23:15 MESZ | **3448** |
| Abstände dazwischen | 3447 |
| davon ≤ 6 Minuten | **3447 — alle** |
| davon > 20 Minuten | **0** |
| größter Abstand überhaupt | **5 Minuten** |

**Und der Herzschlag ist belegt.** Stichprobe aus der tiefsten Nacht von Adams
Abwesenheit (22.08., 01:00–05:00 UTC): **jeder** Commit berührt ausschließlich
`zustand.json`. Der Inhalt ändert sich echt, nicht nur die Commit-Zeit:

```
-  "stand": "2026-08-22 06:50:06",
+  "stand": "2026-08-22 06:55:09",
```

Damit ist bewiesen, was das Papier behauptet: **Die Belegkette der
Stundenblume trägt den Takt, unabhängig davon, ob jemand den Bot benutzt.**
Der Herzschlag existiert, er muss nicht gebaut werden. Der Verzicht darauf war
richtig.

**Der Sicherheitsabstand ist sogar größer als beschrieben.** Das Papier sagt
„kein einziger Abstand über zwanzig Minuten". Richtig, aber untertrieben:
**keiner über sechs.** Die Zwanzig-Minuten-Schwelle hat den vierfachen
Abstand zum schlechtesten gemessenen Wert — das ist der Satz, der die Zeile
gegen den Fehlalarm-Vorwurf verteidigt.

---

## Was nicht stimmt: **805**

Im Papier steht dreimal sinngemäß „805 Commits seit dem 19.08.". **Gemessen
sind es 3448** — die Zahl ist um den Faktor 4,3 zu klein.

Zur Einordnung: Bei durchgehendem Fünf-Minuten-Takt sind über zwölf Tage
rechnerisch **3456** Commits möglich. 3448 liegt praktisch auf diesem Maximum;
805 liegt weit darunter und wäre nur mit massiven Ausfällen erklärbar — also
mit genau dem Gegenteil dessen, was das Papier belegt. **Die Zahl widerspricht
der eigenen Schlussfolgerung.**

## Woher sie vermutlich kommt — ich bin in dieselbe Grube gefallen

Ich weiß nicht, wie Mick gezählt hat; das kann nur er sagen. Ich weiß aber,
wie **ich** vor zehn Minuten auf eine falsche Zahl kam, und das Muster passt:

Mein erster Klon war **flach** (`--depth 400`). Die Messung darauf ergab
„1300 Commits, größter Abstand 5,85 Minuten" — sauber aussehend, und falsch.
Der Grund: Ein flacher Klon hat eine **abgeschnittene Wurzel**. `--since`
filtert dann innerhalb eines Fensters, das gar nicht so weit zurückreicht.
Meines endete am **27.08.** — **Adams zwölftägige Abwesenheit lag komplett
außerhalb.**

Das ist die Pointe: Ausgerechnet der Zeitraum, den das Papier als *härtesten
Fall* anführt, ist derjenige, den eine flache Messung als Erstes verliert.
Aufgefallen ist es mir nur, weil ich vor dem Berichten den **ältesten Commit
im Fenster** abgefragt habe.

**Der Handgriff, der es abfängt** — eine Zeile, vor jeder Git-Zeitmessung:

```bash
git rev-parse --is-shallow-repository   # muss "false" sagen
git log --format='%ad' --date=short | tail -1   # muss VOR dem Fensteranfang liegen
```

---

## Was zu tun ist

**Ein Zahlentausch in `docs/NOTBETRIEB.md`, sonst nichts.** Die Argumentation
bleibt wie sie ist — sie wird durch die richtige Zahl nur stärker:

- **805 → 3448** an allen drei Stellen
- „kein einziger Abstand über zwanzig Minuten" → **„keiner über sechs; die
  Schwelle hat vierfachen Abstand"**
- eine Zeile dazu, dass die Messung auf **voller Historie** lief
  (`--unshallow`), weil ein flacher Klon genau die Abwesenheit verliert

**Kein neuer Prüfer.** Das ist ein Zahlenfehler in einem Papier, kein Loch im
Code — die Konvergenz-Bremse gilt.

---

## Warum ich das überhaupt melde

Die Zahl steht jetzt **als gemessene Tatsache in der Ablage**. Genau diese
Klasse hat dieses Projekt am 20.08. viermal an einem Tag gefunden, und die
stehende Stichprobe für den Kurs-Blick gibt es deswegen. Eine Zahl, die der
eigenen Schlussfolgerung widerspricht, wird in vier Wochen entweder zitiert
oder benutzt, um die Schlussfolgerung zu kippen.

**Die Arbeit selbst ist richtig.** Der Verzicht auf den Herzschlag, die
benannte Grenze der Zusicherung, der dritte Erkennungsfall — das trägt alles.
Es ist die Zahl, nicht das Urteil.
