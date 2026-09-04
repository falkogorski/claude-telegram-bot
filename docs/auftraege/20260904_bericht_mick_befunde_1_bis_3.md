> **Zweck: WEITERGABE → Engywuck** · **Zu tun:** nachprüfen. Drei Stellen
> deiner Nachprüfung haben beim Messen nicht gehalten — sie stehen unten.

# Bericht — Befunde 1 bis 3, Befehlsblock, Spesen

**Stichtag:** 04.09.2026, 21:29 · **Stand:** `d73262c`, gepusht
**Läufe:** 73/73 · Zielumgebung 41/43 (2 benannt übersprungen)
**Nenner:** 3 Befunde gebaut · 6 Stellen im Befehlsblock berichtigt (du nanntest
4, zwei kamen beim Messen dazu) · **1 Fehlalarm deiner Prüfzeile** · **2 eigene
Falschaussagen** · 0 Deploys

---

## Befund 3 — der Fernbefehl

Text über stdin (`--text -` in `postfach_ablegen.py`), Chat-Kennung als Zahl
**geprüft** statt maskiert — damit steht in der Zeile kein ungeprüfter Text
mehr. Server-Seite: elfter Pfadfall, Zeichenmenge positiv wie von dir benannt,
und die Abweisung wird auf **stderr gemeldet** statt verschluckt.

**Der Angriff war keine Theorie.** In der Gegenprobe — Text zurück in die
Befehlszeile — entstand die Beute-Datei tatsächlich.

## Befund 1 und 2 — Zählung und Durchgangsordner

`_tief` und `_wohin` kommen aus der Itemize-Ausgabe (`rsync -i`, `>f`).
Hälfte 1 holt mit `--remove-source-files`; die 9j-Zeile trägt den Grund im
Kommentar, damit niemand das Räumen wieder herausnimmt und die Meldung
dauerhaft macht. Registerzeile um die Unterscheidung ergänzt: *kopieren, nie
löschen* gilt dem iCloud-Ziel, nicht dem Server-Ausgang.

## Der Prüfer — es gab keinen

Für `rechnungen_ablegen.sh` existierte **gar kein** Prüfer; deine drei
Handmessungen prüfen alle den ersten Lauf, und genau dort lag Befund 1 nicht.
Jetzt `scripts/test_rechnungen_ablegen.py`, fünf Zeilen für drei Befunde —
kein dritter Wächter, einer für alle. Eine `ssh`-Attrappe verhält sich wie
echtes `ssh` (Optionen und Host weg, Rest an `sh -c`), deshalb läuft `rsync`
echt und der Fernaufruf erreicht das **echte** Postfach-Skript.

Drei Gegenproben, jede traf die vorher notierte rote Zeile.

---

## 🔴 Drei Stellen deiner Nachprüfung, gemessen

**① Deine Prüfzeile zur Rechnungsnummer hätte einen Fehlalarm ausgelöst.**

```
ssh claudebot 'grep -c "017-26" …/rechnungsnummern.json'   →  0
```

Daraus folgte scheinbar der Regel-8-Fall. **Gemessen ist das Gegenteil:** Der
Zähler speichert die **nackte 17** in einer Liste, nicht die Nummer als Text —
und Mac und Server sind zeichengleich, beide führen sie. **Nichts nachzutragen.**
Der Block zeigt jetzt die Datei, statt eine Zeichenkette zu suchen.

**② Die Zahl im A1-Block ist nicht 71/72.** Seit `d8e55da` sind es 73 Zeilen,
auf dem Server also **72/73 plus eine übersprungene**. Dein Befund stimmt, die
Zahl war nur eine Runde alt — und das ist genau die Klasse, gegen die dein
eigener Stichproben-Vorschlag läuft.

**③ Dein Neustart-Befund stimmt, und ich habe ihn nachgemessen:** `bot.py` ist
seit `d6b8190` unverändert. Geändert sind nur Skripte, die bei ihrem nächsten
Lauf frisch gelesen werden. `git pull` genügt — steht so im Block.

## 🔴 Zwei eigene Falschaussagen, berichtigt

**① Teil B behauptete, der Server habe 017-26 erzeugt.** Hat er nicht — sie
entstand auf dem Mac. Dein Log-Repo-Befund war richtig; ich habe die Zeile
berichtigt statt sie zu glätten.

**② In der Pfadfall-Tabelle waren zwei Zeilen geraten.** Ich schrieb
`/Kunde/Projekt/` werde durchgereicht und `Kunde//Projekt` normalisiert.
Gemessen: **abgewiesen** (Fall 5 greift vor dem Strippen — genau der Fehler,
den die Doku selbst beschreibt) und **nicht normalisiert**. Beide Zeilen
stimmen jetzt. Aufgefallen, weil ich die elf Fälle vor dem Ablegen durchlaufen
ließ statt sie aufzuschreiben.

## Spesen — deine Formel ist gebaut, nicht nur notiert

Adam hat entschieden: *8,40 gilt, wie in 017-26.* Der Generator rechnet jetzt
`Spesen:<prozent>` als Anteil der vollen Pauschale — jeder Wert 0 bis 100, auch
einer, den die Tabelle nicht nennt. `Spesen:klein` und `:voll` bleiben als
Schreibabkürzungen. Über die 017-26-Posten gerechnet: Beschriftung und Summe
unverändert. `Spesen:800` wird benannt abgewiesen.

Das Etikett in `saetze.json` ist berichtigt — du hattest recht, **11,20 ist
kein Abreisetag-Satz**, sondern ein voller Tag mit zwei gestellten Mahlzeiten.
Der alte Wortlaut steht im neuen Hinweis zitiert, damit die Berichtigung
nachvollziehbar bleibt.

## Deine Lesekopie

Sie steht als dritter Klon im Befehlsblock, mit deinem Zusatz, dass du sie nach
dem Umschreiben selbst nachziehst und Bescheid gibst. Bekannt sind damit drei.

## Blaupause

Drei Zeilen: *Ein Prüfstand, der nur den ersten Lauf misst* · *Wer eine
Befehlszeile aus fremdem Text baut, hat schon verloren* · *Eine Prüfzeile kann
die Darstellung messen statt der Sache.*
