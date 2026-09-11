> **An Adam, zur Weitergabe an Engywuck** · Mick · 11.09.2026, 10:59 · gebaut: `ad943ad` · Regressionslauf 85/85 · **kein Deploy**

**Zweck: ANSICHT + WEITERGABE → Engywuck** · **Zu tun: Adam nichts — weiterreichen**

# Adams zwei R1-Befunde — und zwei Geschwister, die dabei auffielen

**Nenner:** zwei Befunde beauftragt, **vier** Stellen behoben. Zwei neue
Prüfzeilen, drei Gegenproben. Der Empfangs-Prüfer steht bei 118 Zeilen.

## ① Der Empfangs-Knopf sitzt jetzt neben dem Auto-Knopf

Ich hatte beide auf eigene Zeilen gelegt, mit der Begründung, der
Genehmigungs-Zustand sei eine Sicherheitsaussage und solle nicht zwischen
anderen Knöpfen untergehen. **Adam hat es am fertigen Gerät gesehen und anders
entschieden.** Das ist seine Wahl, und sie sticht meine Begründung — beides
steht so im Code, damit niemand es später „zurückverbessert".

Die Tastatur hat damit fünf Zeilen: Modelle · Tiefe · Gründlich und Kontingent ·
**Genehmigen und Empfang** · Schreiben frei. Hilfetext im selben Commit.

## ② Keine rohen Sternchen — und die Geschwister-Regel

`cmd_empfang` sendet **ohne** `parse_mode`, und das ist Absicht: Zimmernamen und
Auftragstexte können Unterstriche tragen, die Telegram den ganzen Aufruf
ablehnen lassen; die Antwort käme nie an. Dann kommen aber auch die `**` beim
Leser an. Genau so hat Adam es nach dem Deploy gesehen.

**Zwei weitere Stellen, beide echt, beide durch die Geschwister-Prüfung:**

| Stelle | Was Adam sieht |
|---|---|
| `cmd_status` | „Gründlich ist \*\*an\*\*", „Empfang ist \*\*an\*\*" — ein Sendeaufruf, ohne `parse_mode` |
| `cmd_hilfe` | „\*\*Befehle, die nach draußen sprechen\*\*" — **seit dem 03.09.** in seinem eigenen Hilfetext |

Die dritte fand ich erst, als die Prüfzeile scharf genug war. Das ist der
eigentliche Ertrag dieses kleinen Auftrags.

## Die zwei Prüfzeilen — und der Weg dorthin, der länger war als das Ergebnis

**Zeile 1 wird ausgeführt:** `cmd_empfang` läuft mit Attrappen, der erzeugte
Text wird gemessen. Kein Textscan.

**Zeile 2 ist eine Menge** — aber nur dort, wo die Zuordnung eindeutig ist:
**genau ein Sendeaufruf in der Funktion, und dieser ohne `parse_mode`.** Dann
gehört der Text dieser Funktion zu diesem Aufruf, ohne dass man es raten muss.

Drei Fassungen, und jede Verwerfung hatte einen gemessenen Grund:

1. *Jede Funktion, die nie `parse_mode` setzt* → **elf Fehlalarme**, alles
   Docstrings. `ast.get_docstring` normalisiert die Einrückung, mein
   Textvergleich lief ins Leere. Über den **Knoten** gelöst.
2. Danach **vier Fehlalarme** — verschachtelte Funktionen (deren Docstrings der
   äußeren zugerechnet wurden) und lange verkettete Texte, in denen irgendwo
   `**` steht. Auf „genau ein Sendeaufruf" eingeengt.
3. Danach **einer**: `send_chunked` ist ein **Funktionsaufruf**, kein Attribut,
   und fiel durch meinen Sender-Filter. Erst danach blieb `cmd_hilfe` als
   einziger echter Treffer stehen.

**Warum ich nicht die breitere Fassung genommen habe:** Eine Prüfzeile mit vier
Fehlalarmen wird binnen einer Woche abgeschaltet. Die enge fängt den klaren
Fall und sagt selbst, was sie nicht fängt.

**Drei Gegenproben, alle wie vorher notiert:** Sternchen zurück in
`cmd_empfang` → Zeile 1 rot. Sternchen zurück in `cmd_status` → Zeile 2 rot.
Empfangs-Knopf zurück in eigene Zeile → Tastatur hat sechs statt fünf Zeilen.

## Ein Fund in eigener Sache

**Mein Laufplan behauptete, live sei `495ca45`.** Per `ssh` nachgemessen: Live
ist **`a6cabbf`** — Adam hat heute Vormittag deployt, und ich habe es aus
seinem Papier übernommen, statt es zu prüfen. Berichtigt, samt der Zeile, dass
der Wert **gemessen** ist.

Es ist dieselbe Klasse wie die Falschaussagen, die dieses Projekt in der
eigenen Ablage gefunden hat — nur in einer Datei, die nicht versioniert ist und
deshalb keinen Verlauf hat, an dem es jemandem auffiele.

## Was zu prüfen wäre

1. **Zeile 2 erreicht Funktionen mit gemischten Sendewegen nicht** (mal mit,
   mal ohne `parse_mode`). Dort ist die Zuordnung Text/Aufruf per Syntaxbaum
   nicht sicher herstellbar. Gemessen: Im ganzen Modul gibt es heute keinen
   Fall, der dadurch durchfiele — aber das ist eine Momentaufnahme.
2. **`cmd_status` und `cmd_hilfe` sind jetzt sternchenfrei, aber weiterhin
   ohne `parse_mode`.** Wer dort künftig Auszeichnung einbaut, wird von Zeile 2
   gefangen — vorausgesetzt, die Funktion behält ihren einen Sendeaufruf.
3. **Der Empfangs-Knopf teilt sich die Zeile mit dem Auto-Knopf.** Auf schmalen
   Geräten bricht Telegram Beschriftungen um; wie es dort aussieht, habe ich
   **nicht gemessen** — das sieht nur Adam.

## Nicht getan, mit Absicht

Kein Deploy. Der Schreiben-frei-Knopf (`73d378a`) und diese Befunde liegen
zusammen im Hauptbaum, drei Commits über dem Serverstand.
