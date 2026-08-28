<!-- ROLLE: bauauftrag-freigabedialog-klartext -->
**Stichtag:** 2026-08-25 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile in `MIGRATION.md`** · **Status: VORGELEGT, ungeprüft**

# BAUAUFTRAG — Der Freigabedialog sagt, worüber er entscheiden lässt

**Von:** Claudia (Bot-Sitzung) · **An:** Engywuck (Kontrolle) · danach Mick (Bau)
**Anlass:** Adam, 25.08.2026, 06:55 Uhr
**Stand des Repos beim Messen:** `0b4d7bc` (Betriebslage RUHE), nur gelesen

---

## DER ANLASS, in Adams Worten

> „Jetzt haust du mir hier die Permissions um die Ohren. Und ich weiß gar nicht
> genau … Ich brauche eigentlich immer eine genaue Beschreibung, was ich da
> freigebe. Das ist ja letztendlich die Instanz, die … Wir haben ja das
> Vier-Augen-Prinzip … Ansonsten haben wir alle möglichen Wächter installiert.
> Aber wenn ich natürlich gar nicht weiß, was ich da freigebe, wenn ich keine
> Erklärung dazu habe, keine präzise. Das muss jetzt nicht super lang sein,
> aber es muss halt präzise sein."

Er hat am selben Morgen zusätzlich von Dauerfreigabe auf Einzelfreigabe
umgestellt und die Mehrarbeit ausdrücklich in Kauf genommen. **Damit steigt die
Zahl der Dialoge — und der Mangel wirkt ab sofort häufiger.**

**Der Rang dieser Sache:** Der Freigabedialog ist die Stelle, an der das
Vier-Augen-Prinzip tatsächlich stattfindet. Alle Wächter des Projekts arbeiten
zu, aber sie entscheiden nicht. Entscheidet Adam ohne Entscheidungsgrundlage,
ist das zweite Augenpaar formal vorhanden und praktisch blind. Das ist derselbe
Fehlertyp, den Engywuck am 22.08. bei WebFetch benannt hat — *„aus niemand wird
gefragt wurde Adam wird gefragt, ohne etwas zu sehen"* —, nur eine Ebene
allgemeiner.

---

## BEFUND — gemessen, mit Fundstelle

**`bot.py:2689`, `format_tool_call()`** baut den Text des Freigabedialogs. Sie
kennt vier Fälle:

| Fall | Was Adam sieht |
|---|---|
| `Bash` | das Wort „Bash", darunter die rohe Befehlszeile (bis 800 Zeichen) |
| `Read` / `Edit` / `Write` | Werkzeugname und voller Pfad |
| `WebFetch` | Werkzeugname und die Adresse (seit 22.08., Engywucks H4) |
| alles Übrige | Werkzeugname und die **Namen** der Argumente |

**Was in keinem der Fälle dabeisteht:**
1. ein Satz in normaler Sprache, **was der Aufruf bewirkt**;
2. eine Einstufung: **liest nur · verändert · geht nach außen · kostet Geld**;
3. bei `Bash` eine Benennung des **betroffenen Ziels** (welche Datei, welcher
   Ordner, welcher Dienst) — die Befehlszeile enthält es, aber sie muss
   entziffert werden.

**Der Kanal existiert bereits und ist nicht angeschlossen.** Jeder `Bash`-Aufruf
trägt im Werkzeug-Eingang ein Feld `description` — eine kurze deutsche
Tätigkeitsangabe der aufrufenden Sitzung. `format_tool_call()` liest es nicht.
Auch die Klartext-Werkzeugspur (`_tool_trace_line`, `bot.py:2649`) liest es
nicht; sie baut ihre deutschen Zeilen selbst aus Werkzeugname und Argumenten.

**Damit ist der Mangel nicht durch Fleiß der aufrufenden Sitzung behebbar.**
Ich kann Beschreibungen schreiben, so gut ich will — sie erreichen Adam im
Moment der Entscheidung nicht.

**Nicht gemessen (ehrlich benannt):** Ob das Feld `description` in jedem Fall
gesetzt ist, habe ich nicht über eine Stichprobe geprüft, sondern nur aus der
Werkzeugdefinition abgeleitet. Der Bau muss den leeren Fall tragen.

---

## WAS GEBAUT WIRD

Der Dialog bekommt **drei Zeilen statt einer**, in dieser Reihenfolge:

```
<Klartextsatz: was hier geschieht>
<Einstufung> · <Ziel>
<Rohform — unverändert wie bisher>
```

**Zeile 1 — der Klartextsatz.**
- Bei `Bash`: der Inhalt von `tool_input["description"]`, unverändert
  übernommen. Fehlt er oder ist er leer: die Zeile entfällt ersatzlos (**kein
  Platzhalter, keine erfundene Beschreibung**).
- Bei allen übrigen Werkzeugen: aus Werkzeug und Argumenten **abgeleitet**,
  nach dem Muster, das `_tool_trace_line` schon beherrscht. Diese Funktion ist
  der Ort, an dem die Formulierungen bereits liegen — sie wird
  wiederverwendet, nicht nachgebaut.

**Zeile 2 — Einstufung und Ziel, deterministisch aus dem Werkzeug abgeleitet:**

| Werkzeug | Einstufung | Ziel |
|---|---|---|
| `Read`, `Grep`, `Glob` | liest nur | Dateiname oder Ordner |
| `Edit`, `Write`, `NotebookEdit` | **verändert eine Datei** | Dateiname |
| `WebFetch` | **geht nach außen** | Hostname |
| `WebSearch` | **geht nach außen · 💰 kostet** | Suchdienst |
| Websuche (lokal) | geht nach außen · kostenfrei | Suchdienst |
| `Bash` | **Shell-Befehl — Wirkung nicht maschinell bestimmbar** | — |
| Übrige | Werkzeugname | Argumentnamen |

**Zeile 3 — die Rohform bleibt vollständig erhalten**, unverändert, an
derselben Stelle wie heute.

---

## DREI AUFLAGEN — sie tragen die Sicherheit des Ganzen

**① Die Beschreibung ergänzt den Rohbefehl, sie ersetzt ihn nie.** Der
Klartextsatz stammt von der Instanz, die die Freigabe **haben will**. Könnte er
die Befehlszeile verdrängen, wäre er ein Weg, Adam etwas anderes zu zeigen als
das, was ausgeführt wird — der klassische Pfad für eingeschleusten Fremdtext,
der eine harmlos klingende Beschreibung zu einem schädlichen Befehl erzeugt.
**Die Rohform ist die Wahrheit, der Satz ist Erläuterung.** Beides steht
zugleich da; wo der Platz knapp wird, wird die **Beschreibung** gekürzt, nie
der Befehl.

**② Die Einstufung darf nicht aus der Beschreibung stammen.** Sie wird aus dem
Werkzeugnamen abgeleitet — einem Wert, den die aufrufende Sitzung nicht frei
setzt. Sonst hat sie denselben Makel wie ①.

**③ Bei `Bash` keine beruhigende Einstufung.** Naheliegend wäre, den Befehl
nach Wortlisten zu sortieren („beginnt mit `ls`, also liest nur"). **Das ist
K5 aus dem Entkernungs-Befund**: Eine Wortliste für Verbotenes oder Harmloses
ist konstruktiv unvollständig, und hier wäre sie besonders teuer, weil sie
Adams Wachsamkeit senkt, ohne sie zu verdienen. Ein Shell-Befehl bekommt
darum die ehrliche Auskunft „Wirkung nicht maschinell bestimmbar" — und
genau deshalb ist bei ihm der Klartextsatz am wichtigsten.

Die Beschreibung wird vor der Anzeige **entschärft** (Steuerzeichen,
Zeilenumbrüche, Auszeichnungssyntax), damit sie den Dialog nicht optisch
umbauen kann.

---

## WAS KANN BRECHEN UND WER MERKT ES

**① Der Klartextsatz lügt, weil die aufrufende Sitzung falsch beschreibt.**
Merkt: niemand automatisch. **Deshalb Auflage ①** — die Rohform steht daneben,
und Adam kann jederzeit vergleichen. Der Schutz liegt nicht in der Richtigkeit
des Satzes, sondern darin, dass er den Befehl nicht verdeckt.

**② Die Beschreibung fehlt, und der Dialog zeigt einen Platzhalter, der wie
eine Aussage aussieht** („keine Beschreibung" gelesen als „unbedenklich").
Merkt: niemand. **Deshalb entfällt die Zeile ersatzlos**, statt gefüllt zu
werden.

**③ Der Dialog wird zu lang und wird nicht mehr gelesen.** Merkt: Adam, aber
erst nach Wochen, und das Ergebnis wäre gedankenloses Zustimmen — schlimmer als
der heutige Zustand. **Maß:** drei Zeilen plus Rohform; die Beschreibung wird
bei mehr als etwa 200 Zeichen gekürzt.

**④ Die Ableitung der Einstufung veraltet still, wenn ein neues Werkzeug
hinzukommt.** Ein unbekanntes Werkzeug fiele in den Sammelzweig und bekäme
keine Einstufung — **das sähe aus wie Ruhe.** Deshalb: unbekannte Werkzeuge
bekommen ausdrücklich die Anzeige „**unbekanntes Werkzeug — Wirkung nicht
eingestuft**", und der Prüfer unten misst genau diesen Fall.

**⑤ Der Prüfer prüft den Erklärtext statt das Verhalten.** Die
Hauskrankheit K1. **Deshalb:** kein Prüfer, der im Quelltext nach Zeichenketten
sucht — der Prüfer **ruft `format_tool_call()` auf** und misst die Rückgabe.

---

## PRÜFER — Verhalten, nicht Quelltext

Vier Prüfzeilen, alle über den Aufruf der Funktion, keine über Textsuche:

1. **Bash mit Beschreibung** → Rückgabe enthält den Beschreibungstext **und**
   die vollständige Befehlszeile. (Gegenprobe: Beschreibung entfernen → die
   Zeile fehlt, der Befehl steht weiter da.)
2. **Bash ohne Beschreibung** → Rückgabe enthält die Befehlszeile und
   **keinen** Platzhaltersatz.
3. **`Write`** → Rückgabe enthält die Einstufung „verändert" und den
   Dateinamen. (Gegenprobe: Einstufungstabelle für `Write` entfernen → rot.)
4. **Erfundenes Werkzeug** `Frobnicate` → Rückgabe enthält „nicht eingestuft".
   **Das ist der Prüfer gegen das stille Veralten aus ④.**

**Auflagen wie üblich:** vor jeder Gegenprobe hinschreiben, **welche Zeile rot
werden soll**; `__pycache__` vor jedem Lauf löschen (Geisterbefund-Falle);
`scripts/regressionstest.sh` vollständig vor dem Commit; jede Stelle einzeln
committen.

---

## WAS NICHT GEBAUT WIRD

- **Keine Wortlisten-Bewertung von Shell-Befehlen** (Auflage ③).
- **Keine Bündelung** gleichartiger Freigaben zu einer Sammelfrage. Sie wäre
  bequem und ist genau die Rückkehr zur Dauerfreigabe, die Adam heute früh
  bewusst abgeschafft hat. Wenn, dann als eigener Entscheid von ihm.
- **Kein Umbau der Werkzeugspur.** Sie wird gelesen und wiederverwendet, nicht
  geändert — ihr Verhalten für Adam bleibt, wie es ist.

---

## EINORDNUNG IN DIE LAGE

Die Betriebslage steht seit 25.08., 05:40 auf **RUHE** bis Adams Rückkehr
(~28.08.). **Dieser Auftrag wird dort nicht eingeschoben.** Er ist vorgelegt,
nicht scharfgestellt; gebaut wird er nach der Rückkehr und nach Engywucks
Gegenlesung. Umfang geschätzt: **eine gute Stunde**, davon die Hälfte Prüfer.

**Er berührt keinen der eingefrorenen Rang-A-Punkte** und blockiert den
Mail-Strang nicht.

---

## ZWEI FRAGEN AN ENGYWUCK

**① Ist die Rangfolge im Dialog richtig herum?** Ich setze den Klartextsatz
**über** die Rohform, weil er die Einordnung liefert und Adam sonst erst
entziffert und dann liest. Das Gegenargument: Was zuerst steht, wird gelesen,
und das ist dann die Fassung der Instanz, die die Freigabe will. Umgekehrt —
Rohform zuerst, Erläuterung darunter — wäre die misstrauischere Bauweise.
**Ich halte meine Reihenfolge für die brauchbarere, aber deine für die
sicherere. Deine Entscheidung.**

**② Gehört die Einstufung auch in die Werkzeugspur?** Die Spur ist bei Adam
standardmäßig stumm und rein informativ. Mein Vorschlag: nein, sie bleibt
unberührt — eine Einstufung ohne Entscheidung erzieht zum Überlesen. Aber du
hast die Spur gebaut und siehst es womöglich anders.
