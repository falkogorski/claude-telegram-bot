# Die Entwicklungskette soll allein laufen

**Stichtag:** 2026-07-28 · **überholt durch:** Stufe 1 als B8 gebaut und ruhend (bbeb4d6); Rundenlisten-Idee ist Rückkehr-Punkt 3 · **maßgeblich ist die Status-Zeile im Drehbuch**


**Fassung:** 28.07.2026, vormittags · **Verfasst von:** Claudia (Bot-Sitzung, VPS)
**Anlass:** Adams Ansage vom 28.07., 10:56 Uhr — „Das muss alleine gehen. Von alleine
laufen, meine ich. Erstmal muss automatisiert laufen."

---

## Worum es geht

Adam ist derzeit die Leitung zwischen den Sitzungen. Ich schreibe einen Bauauftrag,
er lädt ihn herunter, trägt ihn zur Migrationssitzung, holt das Ergebnis ab, gibt es
der Kontrollsitzung, bringt deren Befund zurück. Vier Wege, jeder von Hand. Der Inhalt
der Arbeit dauert Minuten — der Transport dauert Stunden, verteilt über den Tag, und
bindet genau die Zeit, um derentwillen das ganze System gebaut wird.

Sein Bild dafür trifft es: Wenn die Entwicklung ihn bindet, hat er die grauen Herren
durch die Hintertür hereingelassen. Das Werkzeug, das Zeit schenken soll, nimmt sie.

**Die gute Nachricht vorweg:** Die schweren Teile stehen bereits. Was fehlt, ist eine
einzige Verbindung — und die ist klein.

---

## Wo die Zeit tatsächlich hängt

Vier Übergänge, alle mit einem Menschen als Träger:

1. **Claudia → Mick.** Ein Bauauftrag entsteht auf dem Server und wird als Datei in den
   Chat gelegt. Adam holt sie, öffnet die Migrationssitzung, fügt sie ein.
2. **Mick → Conni.** Das Gebaute geht zur Gegenprüfung — wieder über Adams Hände.
3. **Conni → zurück.** Der Prüfbefund muss dorthin, wo gebaut wurde.
4. **Entscheidung → Ablage.** Was Adam per Sprachnachricht entscheidet, bleibt im
   Bot-Gedächtnis liegen, bis jemand es ins Drehbuch überträgt.

Übergang vier ist bereits gelöst — dazu gleich mehr. Eins bis drei sind offen, und sie
sind der eigentliche Zeitfresser.

---

## Was schon steht — wir fangen nicht bei null an

| Baustein | Was er kann | Zustand |
|---|---|---|
| **Botenpostfach** (Ausgang) | Jede Instanz legt einen Auftrag in einen Ordner, der Bot stellt binnen 15 Sekunden zu — ohne den Token zu kennen | gebaut, läuft |
| **9.4 Freigabe-Postfach** | Entscheidungen kommen als Knopf nach Telegram; ein Übertrager hängt das Urteil als datierte Zeile ins Drehbuch | gebaut, geprüft |
| **9.8 Hora** | Ein Zeitgeber startet eine frische Sitzung, arbeitet eine freigegebene Auftragsliste ab, parkt Zustimmungspflichtiges statt zu warten, berichtet und endet | gebaut, einmal scharf gelaufen |
| **9.9 Stundenblume** | Dauerlaufende Wächterkette, meldet Befunde von selbst | gebaut, wird gerade nachgeschärft |
| **8.2 Regressionslauf** | Der Maßstab, an dem sich jeder Lauf misst — grün oder zurück | gebaut, 33 Prüfungen |

Damit existiert bereits: ein Läufer, der ohne Adam arbeitet · eine Leitung, über die er
gefragt wird, ohne dass jemand wartet · ein Prüfer, der jeden Lauf abnimmt · ein Weg,
auf dem Ergebnisse bei ihm ankommen.

**Was fehlt, ist nur eines: dass die Sitzungen einander Aufträge geben können, ohne
dass Adam sie trägt.**

---

## Die eine fehlende Verbindung: das gemeinsame Auftragsbuch

Heute schreibe ich Bauaufträge als Dokument an Adam. Künftig lege ich sie in dieselbe
Auftragsliste, aus der Hora ohnehin arbeitet — als Datei in einem Ordner, genau wie
beim Botenpostfach, nur in die andere Richtung.

Der Ablauf danach:

1. Ich erkenne einen Befund und schreibe den Auftrag — wie bisher.
2. Statt ihn Adam zu schicken, lege ich ihn in die Auftragsliste. Adam bekommt **eine
   Zeile** in den Chat: worum es geht, Ampelfarbe, ein Knopf.
3. **Grün** (Fehlerbehebung, Test, Aufräumen, Zeichenwechsel) läuft ohne Rückfrage
   an — Hora nimmt ihn beim nächsten Lauf, baut, lässt den Regressionslauf laufen,
   rollt bei Rot zurück und berichtet.
4. **Gelb und Rot** (neue Entscheidung, Sicherheit, Geld, Werte) warten auf Adams
   Daumen — über die Leitung, die seit dem 25.07. steht.

**Warum das die Schreibsperre nicht bricht:** Ich schreibe nicht ins Repo, sondern in
einen Ordner daneben. Hora ist eine getrennte Instanz mit eigenem Auftragsbuch und
eigenem Schreibrecht — dieselbe Trennung, die schon heute gilt. Der Bot bleibt Bote.

**Was das für Adam bedeutet:** Aus vier Transportwegen wird ein Knopfdruck, und der nur
dort, wo seine Entscheidung wirklich gebraucht wird.

---

## Drei Stufen — jede für sich nutzbar

### Stufe eins: Der Auftrag findet seinen Weg allein

Ich lege Aufträge in Horas Liste statt in den Chat. Adam sieht eine Zeile und drückt bei
Gelb und Rot einen Knopf.

*Aufwand:* klein — die Liste, das Postfach und die Freigabeleitung existieren; es fehlt
das Ablegen und die Ampel-Einstufung.
*Ersparnis:* die Wege eins und vier fallen weg.
*Voraussetzung:* eine ehrliche Ampel. Was ich grün nenne, läuft ohne Nachfrage — die
Einstufung ist die eigentliche Sicherheitsfrage dieser Stufe, nicht die Technik.

### Stufe zwei: Die Gegenprüfung ruft sich selbst

Nach jedem gebauten Auftrag legt Hora automatisch einen Prüfauftrag an — mit dem
ausdrücklichen Ziel, das Gebaute zu **widerlegen**, nicht abzunicken. Der Prüfbefund
geht zurück in dieselbe Liste; ist er rot, entsteht ein Nachbesserungsauftrag.

*Ersparnis:* die Wege zwei und drei.
*Der wunde Punkt:* Prüft dieselbe Instanz, die gebaut hat, findet sie ihre eigenen
blinden Flecken nicht. Deshalb eine **getrennte Sitzung mit umgekehrtem Auftrag** —
genau die Rolle, die Conni heute schon hat, nur ohne Kurier.
*Der zweite wunde Punkt:* Eine Kette, die sich selbst Aufträge erzeugt, kann kreisen.
Sie braucht eine Obergrenze — nach zwei erfolglosen Nachbesserungen wird gemeldet statt
weitergebaut. Das Muster gibt es bei Hora bereits (drei Fehlläufe, dann Halt).

### Stufe drei: Der Befund erzeugt den Auftrag

Heute meldet die Stundenblume einen Befund, und ich schreibe daraus von Hand einen
Auftrag. Bei wiederkehrenden Mustern — Dienst tot, Zeitgeber gestoppt, Test rot,
Speicher knapp — kann der Befund den Auftrag direkt tragen.

*Ersparnis:* der Weg vom Symptom zur Behebung, heute der langsamste.
*Ausdrückliche Grenze:* nur für Muster, die wir **schon einmal von Hand gelöst haben**.
Ein Automatismus, der eine unbekannte Störung behandelt, ist gefährlicher als die
Störung.

---

## Was bei Adam bleibt — und warum das kein Rest ist

Drei Dinge werden nicht automatisiert, und das ist der Zweck, nicht die Lücke:

- **Was neu entschieden wird.** Richtung, Werte, Geld, Sicherheit. Eine Kette, die
  entscheidet, ist keine Entlastung, sondern ein zweiter Herr.
- **Was das Vertrauensverhältnis berührt.** Rote Daten, fremde Zugriffe, alles, was nach
  außen geht.
- **Der Daumen bei Gelb und Rot.** Ein Knopf, nicht ein Vorgang.

Alles andere darf laufen. Der Maßstab, an dem sich das messen lässt: **Wie oft muss Adam
etwas tun, das keine Entscheidung ist?** Heute vier Mal je Auftrag. Nach Stufe eins
einmal, nach Stufe zwei bei Grün gar nicht.

---

## Was kann brechen und wer merkt es

| Bruchstelle | Wie es aussieht | Wer merkt es |
|---|---|---|
| Ich stufe einen Auftrag falsch als grün ein | Etwas wird gebaut, das Adam so nicht wollte | **Niemand** — bis es auffällt. Der gefährlichste Fall dieses Konzepts. Gegenmittel: Grün nur für eine **benannte, geschlossene Liste** von Auftragsarten, nicht nach meinem Urteil im Einzelfall |
| Die Auftragsliste wird nicht abgeholt | Aufträge sammeln sich, nichts passiert, alles sieht ruhig aus | Horas Tagesbericht meldet auch Leerlauf — aber nur, wenn Hora selbst läuft. Der Zeitgeber braucht seinen eigenen Wächter, sonst ist das Ausbleiben unsichtbar |
| Prüfsitzung nickt ab statt zu prüfen | Grüne Befunde ohne Substanz | Erst beim nächsten echten Fehler. Gegenmittel: Der Prüfauftrag verlangt einen **benannten Widerlegungsversuch**, nicht ein Urteil |
| Die Kette kreist | Bauen, prüfen, nachbessern, ohne Ende — und ohne dass es auffällt, weil jeder Schritt für sich sinnvoll aussieht | Obergrenze im Code, Meldung bei Erreichen |
| Eine geparkte Frage wird weggeräumt | Adams Zustimmung läuft ins Leere | Genau dieser Fehler ist Hora am 26.07. schon einmal unterlaufen und wurde behoben — beim Ausbau erneut prüfen |
| Ampel-Einstufung veraltet | Was vor drei Wochen grün war, ist es nach einer Architekturänderung nicht mehr | Niemand. Die Liste der grünen Auftragsarten gehört in ein Register mit Prüfdatum |

**Der gemeinsame Nenner, wieder einmal:** Kein einziger dieser Fehler stürzt ab. Jeder
sieht von außen aus wie Ruhe. Danach ist zuerst zu suchen.

---

## Vorschlag zum Vorgehen

**Stufe eins zuerst und allein.** Sie bringt den größten Teil der Ersparnis, ist die
kleinste Änderung und lässt sich zurücknehmen, ohne dass etwas verloren geht. Vor allem
zeigt sie in ein bis zwei Tagen echten Betriebs, ob meine Ampel-Einstufung trägt — und
davon hängen die Stufen zwei und drei ab.

**Was Adam dafür entscheiden muss:** die geschlossene Liste der Auftragsarten, die ohne
Rückfrage laufen dürfen. Ich schlage vor, sie eng zu beginnen — Fehlerbehebung mit
vorhandenem Test, Zeichen- und Textänderungen, Aufräumarbeiten, Tests selbst. Erweitern
lässt sie sich immer; zurücknehmen ist teurer.
