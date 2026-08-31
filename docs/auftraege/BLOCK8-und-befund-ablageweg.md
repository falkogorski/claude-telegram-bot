# Block 8 von 18 — und der Befund, der aus Block 7 und 8 zusammen entsteht

**Stichtag:** 31.08.2026, 22:30 MESZ (Systemuhr abgelesen; Container läuft auf UTC)
**Gelesen:** 28 Nachrichten, 26.07. 17:33 bis 22:46 · überwiegend Waschmaschine
**Kandidaten:** 6 · **Lücken:** 2 · **gedeckt:** 3 · **ein Befund über beide Blöcke**

---

## Der Hauptbefund: Verhaltensregeln haben keinen Ablageweg

**Er entsteht erst aus beiden Blöcken zusammen**, deshalb steht er hier und
nicht in einem der beiden. Adam hat am 26.07. **sechs** Dinge gesagt, die den
Bot dauerhaft anders arbeiten lassen sollen:

| | Wortlaut, verkürzt | Uhrzeit |
|---|---|---|
| 1 | Die Ansage (was, wie lange) kommt **zuerst**, nicht gebündelt mit dem Ergebnis | 15:26 |
| 2 | **Zügig antworten** — „muss eine Grundregel sein … nachhaltig festzuhalten" | 15:39 |
| 3 | **Erst nachschauen, ob es dazu schon etwas gab** — statt zu fragen | 22:39 |
| 4 | Und zwar **„bei allen Themen, nicht nur bei Sachthemen"** | 22:45 |
| 5 | **Keine Markdown-Listen** an ihn — „da reicht eine PDF" | 18:02 |
| 6 | **„Ich bin meine Wahrheit" — „Bitte merken"** | 22:21 |

**Gemessen im Repo: keine einzige davon ist auffindbar.** Nicht im
Systemprompt (`_QUALITY_GUIDANCE` deckt Antwortqualität, Quellenpflicht und
Repo-Zugriff — sonst nichts), nicht im Drehbuch, nicht in `CLAUDE.md`.

**Sie sind aber sehr wahrscheinlich nicht verloren.** Sie liegen im
**Bot-Gedächtnis** unter `_MEMORY_DIR` (`bot.py:563`) — auf dem VPS, per
`CLAUDE_MEMORY_DIR` gesetzt. Das ist die Stelle, an die der Bot solche Dinge
schreibt, und sie wird von 4.1 mitgesichert.

**Genau das ist der Befund.** Das Gedächtnis ist eine **Fremdfläche** in dem
Sinn, den Conni am 31.08. beschrieben hat:

- Es liegt **außerhalb beider Repos** — kein Commit, keine Historie, kein
  Vier-Augen-Blick.
- **Kein Wächter misst es.** Die Register-Vollständigkeit prüft Module,
  nicht Gedächtnisinhalte; keine Prüfzeile weiß, welche Regeln dort stehen
  sollten.
- **Es kann nichts fehlen**, weil niemand eine Sollliste hat. Eine Regel, die
  bei einem Neuaufsetzen nicht mitkommt, verschwindet **ohne Meldung**.

**Der belegte Einzelfall dazu ist Nummer 3/4, und er ist der schärfste,**
weil dort eine **Behauptung** steht, die sich prüfen lässt. Adam am 26.07. um
22:45: *„Eigentlich bei allen Themen, nicht nur bei Sachthemen."* Die Antwort
des Bots, in der Reaktionszeile mitprotokolliert:

> *„Angenommen, bei allen Themen. Ich ziehe es in der Regel nach. **Steht
> drin**, bei allen Themen, nicht nur den technischen."*

**Im Repo steht es nicht.** Am nächsten kommt eine Zeile im Mitschrift-Kopf
(`bot.py:3495`): *„frage NICHT neu, worum es ging oder wofür ein Test war."*
Das ist **enger** — es hält den aktuellen Faden, es schlägt nichts nach. Und
es gilt nur für den mitgelieferten jüngsten Verlauf, nicht für *„egal ob
heute, gestern oder vor einem Jahr"*.

**Ich behaupte nicht, dass der Bot gelogen hat.** Ich behaupte: *„Steht drin"*
ist von hier aus **nicht nachprüfbar**, und das ist der Mangel. Eine Zusage
an Adam, deren Einlösung niemand messen kann, ist genau die Klasse, die
dieses Projekt in der eigenen Ablage schon mehrfach gefunden hat.

### Was ich daraus vorschlage — ein Griff, kein Wächter

**Keine neue Prüfschicht** (Konvergenz-Bremse). Stattdessen **eine Messung**,
die Mick in wenigen Minuten fahren kann, und die den Verdacht in beide
Richtungen auflöst:

> `ls -la $CLAUDE_MEMORY_DIR` und darin nach den sechs Punkten greppen.
> Ergebnis: **welche stehen drin, welche nicht.**

Danach ist zu entscheiden — und das ist Adams Entscheidung, nicht meine —,
ob die Verhaltensregeln **einen Ort im Repo** bekommen. Meine Empfehlung:
**ja, aber als Spiegel, nicht als zweite Wahrheit.** Ein Abschnitt im
Drehbuch, der die Regeln *nennt*; das Gedächtnis bleibt die wirksame Stelle.
Zwei Stellen, die beide gelten, wären der schlimmere Zustand.

---

## Die zwei Lücken des Blocks

### ⑥ Der GPS-Gedanke — ausdrücklich zum Festhalten gegeben, nirgends festgehalten

**Wortlaut (22:35):** *„Es gibt doch bestimmte Möglichkeiten GPS einzubinden …
Das ist allerdings ein sehr kritisches Ding, weil das ist für mich eine
**superrote Datenschutzampelgeschichte** … **Das ist ein Gedanke, den mal
festhalten bitte.**"*

Und der Anlass war konkret (22:42): Der Bot rechnete Adams Wegzeiten falsch,
weil er nicht weiß, wo Adam ist. *„Ich lebe halt eben nicht so getaktet nach
Zeit. Ich lebe nach einem inneren Tag."*

**Gemessen:** `gps`, `standort`, `ortung` kommen in `MIGRATION.md` und in
`docs/` **nicht vor** — die einzigen Treffer betreffen die *Selbstverortung
des Bots* (Mac vs. VPS), ein anderes Thema.

**Warum ich das trotz der roten Ampel als Lücke führe:** Adam hat nicht um
den Bau gebeten, sondern ums **Festhalten** — samt seiner eigenen Bedenken.
Und die Bedenken sind der wertvolle Teil: *„wenn ich was baue, was Datenschutz
hochhält … der Mensch selber entscheidet, was er teilen möchte."* Das ist
Material für die Werte-Charta, nicht nur eine Feature-Idee.

### ⑦ Die Ausgabeform-Vorliebe (Nr. 5 oben)

Klein, aber ein Musterfall für **Selbstlernende Assistenz**: eine geäußerte
Vorliebe, die künftig gelten soll, ohne dass Adam sie wiederholt. Sie fällt
unter denselben Hauptbefund.

---

## Was gedeckt ist

**Adams große Frage nach der Verdichtung (22:39)** — *„Wechselts bleibt für
immer in einer Sitzung … würde es nicht Sinn machen, dass du in gewissen
Abständen automatisch eine neue Sitzung eröffnest … und die alten
archiviert?"* — **hat eine Antwort, und zwar seit dem 15.07.:**

**5.24 Proaktive Session-Rotation bei Füllstand ~80 % (mit Übergabe)**, Status
OFFEN. Genau sein Gedanke, nur ohne das Wort Blockchain: ab ~80 % Füllstand
sanft in eine neue Sitzung mit Übergabe-Zusammenfassung, transparent, ohne
Antwortverlust. Der Protokoll-Teil („von jeder Sitzung ein Protokoll") läuft
über den Tageslog und den Log-Abgleich.

**Die PDF-Lieferung auf Zuruf** (18:00, *„Kannst Du mir die Liste … bitte
schnell als PDF fertig machen?!"*) — funktioniert, Adam bedankt sich um 18:07
für die Liste. Unter 5.25 als *Datei-Direktausgabe (PDF) existiert bereits*
vermerkt.

**Der Recall-Anspruch** hinter Nr. 3 hat einen Punkt: **5.11 Gesamtmemory &
Suche**, Status OFFEN, mit Adams Vision im Wortlaut (*„wir hatten doch mal was
zu X"*). **Die Fähigkeit ist verplant — die Regel, sie von selbst zu benutzen,
bevor gefragt wird, ist es nicht.** Das ist der Unterschied, um den es oben
geht.

---

## Laufender Stand

| | |
|---|---|
| Blöcke gelesen | **8 von 18** |
| Zeitraum | 13.07. – 26.07. |
| Kandidaten gedeckt | 18 |
| **Lücken gesamt** | **15** (8 + 5 + 2) |
| davon durch **eine** Messung klärbar | **6** (der Gedächtnis-Griff oben) |

**Nächster Block:** 9 von 18, ab 27.07. — Adams „busy day" vor der Abreise
zum Vipassana. Erwartungsgemäß dicht an Absprachen.
