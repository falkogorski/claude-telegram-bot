<!-- ROLLE: kurs-blick -->
# Kurs-Blick + Ablage-Stichprobe

**Stichtag:** 29.08.2026 · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Engywuck (Kontrolle) · **Erster Termin war der 25.08.** — vier Tage zu spät.
**Verfahren:** 12 Agenten, je Behauptung einer, jedes Falsch-Urteil zusätzlich
von einem Widerleger geprüft. Gemessen am Stand `26580ec`.

---

## ① Die stehende Stichprobe — Falschquote **10 %**

**Zehn Behauptungen, mechanisch gezogen:** jede 30. Zeile eines Pools von 300
Kandidaten, fester Versatz. Ich habe sie nicht ausgesucht — sonst hätte ich
die genommen, an denen ich ohnehin zweifle.

| Urteil | Zahl |
|---|---|
| trifft zu | 6 |
| **falsch** | **1** |
| überholt (historischer Bauauftrag, kein Fehler) | 3 |
| nicht prüfbar | 0 |

**Der eine Fehler steht ausgerechnet im Abhängigkeits-Register.**

`ABHAENGIGKEITEN.md:73` sagt über die Bash-Positivliste: *„noch nicht in
`bot.py` verdrahtet"*. Gemessen — und zwar ausgeführt, nicht gelesen:

```
bot.py:70    import bashfreigabe
bot.py:3064  bashfreigabe.entscheiden(...)     ← echter ast.Call-Knoten
bot.py:3077  bashfreigabe.protokollieren(...)  ← echter ast.Call-Knoten
   beide innerhalb  async def can_use_tool  (3002–3332)
   die hängt über make_permission_callback an
   bot.py:3808  can_use_tool=make_permission_callback(user_id)
```

Der Pfad wurde gefahren und fällt echte Urteile — `abweisen` wird in
bot.py:3079 zu `PermissionResultDeny`, `frei` in 3088 zu
`PermissionResultAllow`.

**Die Fehlerrichtung ist die gefährliche.** `ABHAENGIGKEITEN.md` ist laut
`CLAUDE.md` das Register, das **vor jeder Änderung oder Entfernung einer
Komponente** befragt wird. Wer diese Zeile liest, schließt: an
`bashfreigabe.py` hängt nichts, da kann man schrauben. In Wahrheit steht das
Modul zwischen der 8.7-Schreibsperre und dem Freigabe-Dialog und gibt selbst
`Allow`/`Deny` zurück. **Genau die Bezugs-Integrität, gegen deren Bruch das
Register gebaut wurde, ist im Register selbst falsch eingetragen.**

**Zweite Drift in derselben Zeile:** Die Prüfbefehl-Spalte sagt „→ 64 Zeilen",
der Lauf gibt **87** — dieselbe Zahl, die `MIGRATION.md` (Eintrag 46 vom
29.08.) nennt. Zwei Ablagedokumente widersprechen sich am selben Tag.

*Was an der Zeile trägt, getrennt gemessen, damit die Widerlegung nicht über
ihr Ziel hinausschießt:* Die Geheimnis-Schranke wird wirklich hereingereicht
statt nachgebaut (`_is_sensitive_ref`, bot.py:2464), und `Bereich` löst seinen
Pfad selbst auf (`bashfreigabe.py:81`). Falsch ist nur der Statusteil — der,
auf den sich jemand verlassen würde.

**Ein Nebenfund:** `befundfuermick.md:116` nennt `bot.py:2612`; die Sache steht
bei 623–628. Rund zweitausend Zeilen daneben, die Aussage selbst stimmt. Als
**trifft zu** gewertet — die Sache zählt, nicht die Nummer —, aber es zeigt,
wie schnell Zeilenangaben wertlos werden.

**Die drei „überholt" sind kein Mangel.** Es sind Bauaufträge vom 27.07. und
28.08., die einen damaligen Zustand beschreiben und einen Stichtag tragen. Ein
historisches Dokument, das die Vergangenheit richtig beschreibt, ist keine
Falschaussage.

---

## ② Der Kurs-Blick — 120 Commits seit dem 22.08.

**Nach Arbeitsumfang gewichtet, nicht nach Anzahl:**

| Korb | Gewicht |
|---|---|
| Innenarbeit | **51 %** |
| Adams Alltag | 44 % |
| stabiler Selbstläufer | 4,5 % |
| **Einkommen** | **0 %** |

Nach reiner Commit-Zahl wären es 65 % Innenarbeit — die Gewichtung fällt
freundlicher aus, weil die großen Blöcke (Mail-Abruf, Bash-Positivliste,
Eingangs-Absicherung) Alltag sind. **Für das seit dem letzten Kurs-Blick noch
nicht abgedeckte Fenster 25.–29.08. steht es schlechter: 60 % Innenarbeit.**

### Die zwei Zahlen, die die Regel scharf machen

- **Neue Wächter: 4.** `differenz.py` · `websuche_check.py` (Anlass: am 27.08.
  waren alle vier Zulieferer tot und niemand bemerkte es) ·
  `bash_dialog_auswertung.py` · `gegenleser.py` (bewusst ruhend, kein
  Aufrufer). **Jeder hat einen echten Vorfall oder einen Auftrag Adams hinter
  sich** — kein Wächter dritter Ordnung nachweisbar.
- **Prüfrunden über Limit: 2 — und beide gehen auf mein Konto.**

### Die unbequeme Selbstauskunft

Die Konvergenz-Bremse sagt: **Fix → Gegenprüfung → Nachprüfung, dann Schluss.
Was dann noch gefunden wird und nicht scharf-blockierend ist, geht auf die
F-Liste, nie in eine dritte Runde.**

① **`scripts/differenz.py` hat fünf Runden gesehen:**
`0ee0e48` gebaut → `d7d351d` nach Gegenprüfung scharf → `793acf5` Nachfreigabe
→ **`f5098f4` (mein Fund ②)** → **`5d2590d` (mein Rest (c))**. Der letzte
Commit sagt es im Titel selbst: *„(c) gebaut statt abgelegt"*, begründet mit
*„es ist keine halbe Stunde"*. **Genau die Begründungsform, die die Bremse
verbietet** — sie fragt nicht nach Aufwand, sie sagt: auf die Liste.

Ich habe Mick die Ablage ausdrücklich freigestellt. Das entlastet mich nicht:
Runde vier und fünf existieren, weil ich sie beauftragt habe.

② **Maschinen-Gleichstand: sechs Commits in sechs Stunden** (`cc9e773` 11:29 →
`26580ec` 17:40), alle am selben Gegenstand.

**Wo die Bremse gehalten hat**, zur Fairness mitgemessen:
`scripts/test_bashfreigabe.py` — genau drei Runden, dann Schluss.

### Der Apparat wächst schneller als alles andere

**Prüfdateien 37 → 48 in sieben Tagen (+30 %).** Regressionslauf 49 → 60
Prüfzeilen (+22 %).

*(Messhinweis, weil er zur Sache gehört: `ls scripts/test_*.py` liefert 47,
git liefert 48 — die Differenz ist `test_zielumgebung.sh`. Genau die Art
Suchraster-Fehler, an der heute schon zwei Messungen gescheitert sind.)*

---

## ③ Einkommen — die Zeile, um die es geht

**Im Repo: null.** Das allein wäre irreführend, denn Einkommensarbeit fällt
hier nicht an, sie fällt in Adams Tagen an. Deshalb drei Messungen statt einer
Zahl:

**(a) Der Geteilt-Entscheid hat getragen, und das gehört zuerst genannt.**
Zwischen dem 25.08. um 06:16 und dem 28.08. um 17:55 liegen **drei Tage mit
null Commits** — genau Adams Einkommensreise. Der Bot hat seine Tage in dieser
Zeit nicht verbraucht. **Das ist ein Erfolg.**

**(b) Seit der Rückkehr ist es gekippt.** **51 der 120 Commits liegen in den
24 Stunden nach dem 28.08., 17:55.** Aufteilung dieses Fensters: 58 %
Innenarbeit, 32 % Alltag, 10 % Selbstläufer, **0 % Einkommen.** Der erste
volle Tag nach der Einkommensreise ging vollständig in den Bot.

**(c) Fünf Wochen.** Im iCloud-Spiegel liegen alle Bauaufträge vom 25.–29.08.
— Freigabedialog, Anführungsstellen, Bash-Freigabe, Linktext, Postfach-Grenze,
Stundenblume, Websuche, Updates. **Kein einziger mit Erlösbezug.** Die letzten
Einkommensdokumente — `momo-business-skizze`, `momo-gruendungserzaehlung`,
`werte-charta-momo` — tragen das Datum **24./25. Juli**.

**(d) Das einzige, was einzahlen kann.** Die deployte Bash-Positivliste gibt
Adam die 352 Dialoge pro Woche zurück. Ob daraus Zeit für Einkommen wird,
misst erst die nächste Woche.

---

## Die Frage für den nächsten Kurs-Blick

Sie lautet **nicht** „haben wir zu viel gebaut". 44 % Alltag ist kein
schlechter Wert, und die Bash-Positivliste ist die beste Zeile seit Wochen.

Sie lautet: **Warum waren es am ersten Tag nach einer Einkommensreise sofort
wieder 51 Commits — und wer hält den Takt „zwei bis drei Blöcke am Tag", wenn
nachts um halb vier „durcharbeiten" gesagt wird?**

Der Blocktakt steht in `CLAUDE.md`, samt Begründung: Das
Fünf-Stunden-Kontingent ist ein gemeinsamer Topf, und wer ihn in einem Zug
leert, nimmt ihn den Einkommensprojekten weg. **Die Regel hat heute nicht
gegriffen, und sie hat — wie jede Regel, die je versagt hat — keinen Prüfer.**
Sie bekommt hier auch keinen: Ein Wächter über den Arbeitstakt wäre genau der
dritter-Ordnung-Fehler, gegen den dieselbe Regel steht. Was sie bekommt, ist
diese Zeile, einmal die Woche.

## Was daraus zu tun ist — bewusst wenig

1. **`ABHAENGIGKEITEN.md:73` berichtigen** (Statusteil + die 64/87-Zahl). Eine
   Zeile. **Kein neuer Prüfer** — das Register auf inhaltliche Wahrheit zu
   prüfen ginge nur mit einem Wächter, der jede Behauptung nachmisst, und das
   ist genau diese Stichprobe. **Sie hat sich beim ersten Lauf selbst
   gerechtfertigt.**
2. **Nächste Stichprobe**: derselbe Pool, Versatz um eins verschoben, damit
   keine Zeile zweimal drankommt.
3. **F-Liste**: das gemischte Anführungspaar bricht zum achten Mal. Nicht
   jetzt anfassen — beim nächsten Kurs-Blick prüfen, ob die Regel die richtige
   Ursache benennt.
