<!-- ROLLE: befund-auswerten-knopf-kollision -->
> **Zweck: ABLAGE** · **Zu tun:** nichts mehr — **Adam hat am 02.09.
> entschieden.** Der Knopf ist **vertagt, nicht abgelehnt**; bis zur
> Herkunfts-Signatur schreibt er eine Beschriftung dazu. Was unten als offene
> Wahl steht, ist ab dem Abschnitt *Die Entscheidung* aufgelöst.

# Der „Auswerten"-Knopf lässt sich nicht bauen, ohne Befund C anzufassen

**Stichtag:** 02.09.2026 · **Block B des Nachtblocks**
**Ergebnis: gebaut, gemessen, zurückgebaut.** Der Arbeitsbaum ist sauber.

---

## Was gebaut war

Ein vierter Knopf im vorhandenen Dokument-Dialog, **nur bei Adams eigenen
Dateien** (`if not weitergeleitet`), der den Text setzt, den Adam sonst tippt,
und ihn durch `process_user_text` schickt — also durch denselben Trichter wie
jede Nachricht, mit Warteschlange, Persistenz und allen Schranken.

**Das entsprach dem Auftrag**: kein neuer Pfad, keine neue Schranke, der
Eingangsschutz bleibt davor.

## Woran es scheitert

`scripts/test_eingangsschranken.py`, Zeile **„der Ausweichpfad zur
Hauptsitzung ist zu"**, misst über den Syntaxbaum:

> Im Dokument-Rückruf `on_pdf_callback` darf **`process_user_text` nicht
> vorkommen** — über echte Aufrufknoten gemessen, nicht über Namen im Text.

**Sie ist absichtlich absolut.** Sie stammt aus **Befund C** (Engywucks
Ultracode-Lauf, 24.08.): Der `else`-Zweig gab Fremddokumente an die
Hauptsitzung; `.html` ist der Kanonträger für `display:none`, `.docx` ein
Archiv mit XML darin. Die Wache kennt kein Ermessen, und das ist ihr Wert —
eine Wache mit Ermessen ist eine Bitte.

**Mein Knopf verletzt sie**, obwohl er nur bei eigenen Dateien erscheint. Die
Wache kann das nicht unterscheiden, weil sie am Aufrufknoten misst und nicht an
der Bedingung darüber.

## Warum ich sie nicht angepasst habe

**Eine Sicherheitswache, die eine frühere Instanz nach einem echten Befund
gebaut hat, wird nicht nachts aufgeweicht, um einen Komfort-Knopf zu bauen.**
Das ist der Selbstläufer, gegen den der Deckel steht: *Ein abgeleiteter Auftrag
wird in dieser Rolle zu echtem Code.*

Dazu kommt: Der Auftrag nennt als **erste** Auflage *„Der Eingangsschutz bleibt
vor dem Knopf. Der Knopf darf keinen Weg eröffnen, der an der Prüfung
vorbeiführt."* Nach dem Urteil der bestehenden Wache tut er genau das. **Wenn
die Auflage und die Wache dasselbe sagen, ist das kein Zufall.**

---

## Drei Wege — die Wahl gehört Adam und der Kontrolle

**① Die Wache präzisieren.** Sie misst dann nicht mehr *„kommt
`process_user_text` vor"*, sondern *„erreicht ein **weitergeleitetes** Dokument
`process_user_text`"* — ausgeführt, mit beiden Richtungen. **Das ist der
technisch sauberste Weg und zugleich der heikelste:** Wer eine Wache
verfeinert, macht sie unterscheidungsfähig — und damit umgehbar durch eine
Bedingung, die morgen jemand ändert. Braucht eine Gegenprüfung durch eine
frische Sitzung, nicht meine eigene.

**② Ein eigener Weg am Rückruf vorbei.** Der Knopf hinterlegt den Auftrag, und
die nächste normale Nachrichtenverarbeitung nimmt ihn auf. Die Wache bliebe
unberührt. **Aber es ist ein neuer Pfad**, und der Auftrag sagt ausdrücklich
*„kein neuer Pfad"*.

**③ Den Knopf anders schneiden.** Statt „Auswerten" (Inhalt in die Sitzung)
ein vierter Knopf, der wie die drei vorhandenen am **geschützten Leseweg**
arbeitet — etwa „Worum geht es?" über `_summarize_pdf_direct`. Das erfüllt
Adams eigentliches Anliegen (*nicht nach jedem Dokument erst schreiben müssen*)
**ohne jede Schranke zu berühren.** Der Unterschied zum vorhandenen
„Zusammenfassen" wäre allerdings klein — womöglich ist der Wunsch dort schon
zu drei Vierteln erfüllt, und die Frage lautet eher, ob **„Zusammenfassen"
umbenannt** gehört.

**Meine Einschätzung, ausdrücklich als solche:** ③ zuerst prüfen. Wenn Adams
Anliegen ist, *weniger tippen zu müssen*, dann ist es billig erfüllbar. Wenn
sein Anliegen ist, dass die Sitzung **dem Inhalt folgt und Konsequenzen zieht**
— sein Wortlaut legt das nahe —, dann führt kein Weg an ① vorbei, und der
gehört gegengeprüft, nicht nachts gebaut.

---

## Die Entscheidung `[02.09.2026, Adam]`

**Adams Wortlaut vom 01.09., der die Wahl auflöst:** *„dass Sie die Datei
verarbeitet und den Inhalt daraus umsetzt … Ich muss ja möglich sein, dass ich
einen Auftrag weiterleiten und der ausgelesen wird. Ansonsten kann ich halt
keine Dateien nutzen dafür."*

**Es geht um Ausführung, nicht um Darstellung.** Damit:

| Weg | Stand |
|---|---|
| **③ Am geschützten Leseweg** (*„Worum geht es?"*) | **entfällt** — es ist Darstellung, und die gibt es schon |
| **② Eigener Weg am Rückruf vorbei** | **entfällt** — wäre ein neuer Pfad, den der Auftrag ausschließt |
| **① Die Wache präzisieren** | **kommt später — und dann auf dem richtigen Merkmal** |

**Warum ① nicht heute geht, und das ist der eigentliche Ertrag dieses Befunds:**
Die Wache ließe sich nur auf *„ist das weitergeleitet?"* verfeinern — auf die
Pfeil-Geste. Die trägt nicht: Lädt Adam eine Datei frisch hoch, die er zwei
Minuten vorher per Mail bekam, gilt sie als seine. **Die richtige
Unterscheidung ist *stammt das aus unserem eigenen Haus?*, und dafür existiert
heute kein Merkmal.** Es entsteht mit `9.NN-S Herkunfts-Signatur` im Drehbuch.

**Bis dahin gilt Adams Übergangsweg**, und er ist kein Notbehelf: **Er schreibt
eine Beschriftung dazu.** Fünf Wörter, funktioniert heute — und es ist genau
der Akt, der den Inhalt zu **seinem** Auftrag macht. Der Knopf hätte diesen Akt
ersetzt; das war seine Bequemlichkeit und zugleich sein Problem.

**Die Wache bleibt unangetastet.** Sie hat richtig gehalten. Dass sie am
Aufrufknoten misst und nicht am Auftrag, ist ihre **Grenze, nicht ihr Fehler** —
und die Grenze löst der Signatur-Punkt auf, nicht eine Verfeinerung.

**Was der Beschriftungsweg heute offenlässt**, gehört der Vollständigkeit halber
dazu: Er ist als **F-19** eingetragen (`docs/f-befunde-reihenfolge.md`) — mit
der gemessenen Reichweite und der Feststellung, dass seine ursprüngliche
Begründung entfallen ist.
