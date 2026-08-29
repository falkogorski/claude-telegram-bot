# Konzept: Heimtunnel für YouTube-Zugriff

**Erstellt** 25.07.2026, 20:05 Uhr · **Zuletzt geändert** 25.07.2026, 20:56 Uhr · **Für** Adam · **Status** Entwurf zur Entscheidung

---

## Änderungshistorie

**2026-07-25 20:56** — Zweite Überarbeitung nach Adams Rückmeldung. Aufstellungsort geklärt: Der Router steht bereits auf dem Sicherungskasten, das Gerät kann schlicht danebengelegt werden — der Einbau in den Verteiler entfällt samt Elektro-Thematik. Geräuschentwicklung ist bei Adam ohnehin unkritisch. Neuer Abschnitt „Was das Gerät leisten muss — und was nicht", der Adams Frage nach der Bild-für-Bild-Auswertung beantwortet, samt Bandbreitenrechnung und der Grenze zur serverlosen Variante. Einkaufsliste als eigener Abschnitt ergänzt. Produktgedanken sind separat in der Ideensammlung zum Produkt festgehalten, nicht hier.

**2026-07-25 20:14** — Überarbeitung nach Adams Rückmeldung. Hardware-Empfehlung von Thin Client auf Raspberry Pi umgestellt (Adams ausdrücklicher Wunsch: lautlos, klein, unauffällig platzierbar, notfalls im Verteiler). Neuer Abschnitt zum Aufstellungsort mit Elektro-Sicherheitshinweis. Vorhandener Laptop als Dauerlösung verworfen — Adams Sicherheitsbedenken aufgenommen und geteilt. YouTube-Konto entschieden: zunächst ohne. Abschnitt „Was ich von Adam brauche" entfällt, da beantwortet; dafür Speichermedium-Frage neu aufgenommen.

**2026-07-25 20:05** — Ersterstellung. Anlass: Adams Auftrag vom selben Abend, den Tunnel- und Home-Server-Weg auszuarbeiten, nachdem die Messung am Nachmittag ergeben hatte, dass die Rechenzentrums-Adresse des Servers von YouTube gesperrt wird.

---

## Worum es geht

YouTube-Videos sollen regelmäßig transkribiert und ausgewertet werden. Vom Netcup-Server aus geht das derzeit nicht. Dieses Papier beschreibt, wie sich das dauerhaft lösen lässt, was es kostet und welche Risiken damit verbunden sind.

Adams Vorgaben: möglichst günstig beginnen, aber tragfähig und vernünftig. Das Gerät soll lautlos sein, klein genug für eine unauffällige Ecke oder den Verteilerkasten, und sich per Netzwerkkabel direkt an den Internetanschluss hängen lassen. Aufrüsten soll später möglich bleiben, und die Lösung soll sich mit der ohnehin geplanten Sicherungskopie verzahnen.

---

## Die Diagnose

Am 25.07.2026 auf dem Server gemessen, nicht aus zweiter Hand übernommen.

Zwei Hürden lagen übereinander:

**Erste Hürde — behoben.** Das Abrufwerkzeug verlangt seit dem Umbau im Winter eine externe JavaScript-Laufzeit, um YouTubes Rechenaufgaben zu lösen. Sie fehlte. Nachgerüstet wurde Deno 2.9.4 als geprüftes Binärpaket mit abgeglichener Prüfsumme, dazu der zugehörige Löser. Die Warnung ist verschwunden.

**Zweite Hürde — der eigentliche Grund.** Die Adresse des Servers liegt in einem Rechenzentrum. Sechs verschiedene Zugangsvarianten wurden durchprobiert, darunter jene, die laut Herstellerdokumentation ohne Echtheitsnachweis auskommen sollen. Alle sechs enden in der Aufforderung, sich als Mensch auszuweisen.

**Warum ein hinterlegtes Konto allein nicht hilft.** YouTube bewertet den Ruf der Adresse, bevor es die Anmeldedaten überhaupt ansieht. Zwei unabhängige Quellen beschreiben das übereinstimmend: ein Erfahrungsbericht vom 03.03.2026, in dem dieselbe Anweisung am heimischen Anschluss sofort durchläuft und auf dem Mietserver trotz Konto scheitert, sowie eine Analyse vom 17.07.2026, die ergänzt, dass Sitzungsdaten von Rechenzentrums-Adressen sogar schneller entwertet werden. Die Entwickler des Werkzeugs warnen zudem ausdrücklich, dass die Verwendung des eigenen Kontos dessen Sperrung riskiert.

**Adams Beobachtung bestätigt das.** Sein Freund greift über den Firmenserver zu und hat keine Probleme. Ein Firmenanschluss ist ein gewerblicher Internetzugang, aber kein Rechenzentrum — YouTube unterscheidet zwischen beidem. Adams eigene Einordnung war zutreffend.

---

## Das Prinzip

Der Server behält seine Arbeit, leiht sich aber für YouTube-Abrufe die Adresse eines gewöhnlichen Wohnanschlusses. Ein kleines Gerät zu Hause stellt die Verbindung her; der Server schickt nur diese eine Art von Abrufen hindurch.

Alles andere bleibt unverändert. Der Bot ist weiterhin unter seiner Server-Adresse erreichbar, die Telegram-Verbindung läuft wie bisher, und wenn das Heimgerät einmal ausfällt, funktioniert der Rest des Systems ungestört weiter. Nur die YouTube-Auswertung pausiert dann.

### Die entscheidende Richtungsfrage

Wer baut die Verbindung auf? Diese Frage bestimmt, ob die Lösung überhaupt funktioniert.

**Falsch wäre:** Der Server ruft zu Hause an. Dann bräuchte der Hausanschluss eine feste, von außen erreichbare Adresse. Viele Anschlüsse haben das heute nicht mehr, weil die Anbieter Adressen unter mehreren Kunden aufteilen. Man müsste zusätzliche Dienste bemühen und wäre von der Anbieter-Konfiguration abhängig.

**Richtig ist:** Das Heimgerät ruft beim Server an und hält die Verbindung offen. Der Server nimmt entgegen — er hat ja eine feste, öffentliche Adresse. Damit spielt es keine Rolle, wie der Hausanschluss beschaffen ist, ob sich die Adresse täglich ändert oder ob sie geteilt wird. Diese Richtung funktioniert praktisch immer, und sie öffnet keinen Weg von außen ins Haus.

### Nur der YouTube-Verkehr, nicht alles

Der gesamte Serververkehr soll nicht durch den Tunnel. Das wäre langsam und würde bei jedem Ausfall zu Hause das ganze System lahmlegen.

Stattdessen läuft auf dem Server ein kleiner Vermittler, der ausschließlich dem Abrufwerkzeug zur Verfügung steht. Ein Werkzeug namens `wireproxy` leistet genau das: Es hält die Tunnelverbindung und bietet dem Abrufwerkzeug eine örtliche Übergabestelle an, ohne die Netzwerkeinstellungen des Servers anzufassen. Wird der Tunnel entfernt, bleibt kein Rückstand.

---

## Die Hardware [NEU 2026-07-25 20:14]

### Warum nicht der vorhandene Laptop

Adam hat einen älteren Rechner und einen Laptop, will sie aber nicht dauerhaft laufen lassen — mit der Begründung, dann liege bei ihm zu Hause „die ganze Zeit relativ offen alles" herum.

Das Bedenken ist berechtigt und ich teile es. Ein gewachsenes Alltagsgerät trägt Jahre an Daten, Konten und installierten Programmen mit sich. Es rund um die Uhr am Netz zu betreiben, vergrößert die Angriffsfläche um alles, was darauf liegt — und im Schadensfall steht viel mehr auf dem Spiel als der Tunnel.

Ein eigenes, minimales Gerät ist das Gegenteil: Es kennt nur eine Aufgabe, enthält keine persönlichen Daten, und wenn es je kompromittiert würde, verliert man ein Gerät für 50 Euro und nicht sein digitales Gedächtnis. Es lässt sich zudem hart abschotten, weil es nichts anderes können muss.

**Der Laptop bleibt trotzdem nützlich** — als Überbrückung für einzelne Videos, solange das eigentliche Gerät noch nicht da ist. Nur eben nicht als Dauerlösung.

### Die Empfehlung: Raspberry Pi 5

Adams Wunsch nach einem Pi trifft die Aufgabe gut. Die Preislage ist erfreulich: Der Raspberry Pi 5 ist neu ab 46,90 Euro zu haben, gebraucht werden Geräte um 43 Euro gehandelt, teils als Paket mit Netzteil und Gehäuse. Preise vom 25.07.2026 aus einem Preisvergleich und von Kleinanzeigen; sie schwanken.

**Zur Lautlosigkeit:** Der Pi 5 gilt als Gerät, das unter Last einen Lüfter braucht. Unsere Last ist aber winzig — der Tunnel hält eine Verbindung offen und leitet gelegentlich eine Tonspur durch. Das ist praktisch Leerlauf. Ein passiver Kühlkörper oder ein Aluminiumgehäuse, das die Wärme selbst abführt, genügt dafür. Damit ist das Gerät vollständig geräuschlos, weil es kein bewegliches Teil enthält.

**Wichtig — nicht auf Speicherkarte betreiben.** Der übliche Weg über eine microSD-Karte ist für Dauerbetrieb ungeeignet: Diese Karten verschleißen durch ständiges Schreiben und fallen nach Monaten bis wenigen Jahren aus. Für ein Gerät, das durchlaufen soll, gehört ein Datenträger mit längerer Lebensdauer daran — entweder eine kleine SSD über den USB-Anschluss oder eine M.2-Erweiterung. Das kostet 20 bis 40 Euro mehr und erspart den Ausfall zur Unzeit.

**Ehrliche Gesamtrechnung.** Die 46,90 Euro gelten für die nackte Platine. Betriebsbereit kommen Netzteil, Gehäuse und Datenträger hinzu; die Einzelposten stehen unten in der Einkaufsliste. Realistisch landet man bei 92 bis 115 Euro neu. Auf dem Gebrauchtmarkt sind Komplettpakete deutlich günstiger — Adams eigener Gedanke, dort zu schauen, ist der richtige und drückt das auf 50 bis 70 Euro.

**Stromverbrauch:** Im Leerlauf zieht der Pi 5 etwa vier bis sechs Watt. Das ergibt 35 bis 53 Kilowattstunden im Jahr, bei 35 Cent je Kilowattstunde also zwölf bis 18 Euro. Geschätzt, nicht gemessen.

**Nachrichtlich zur Alternative:** Ein gebrauchter Bürorechner der schlanken Bauart wäre etwas leistungsfähiger und kommt meist komplett mit Netzteil und Speicher. Er ist aber größer, teils mit Lüfter, und passt damit schlechter zu Adams Anforderung an Größe und Stille. Der Pi ist hier die richtige Wahl.

### Der Aufstellungsort — geklärt [NEU 2026-07-25 20:56]

Die Frage hat sich einfacher aufgelöst als gedacht. Adams WLAN-Router steht bereits **auf** dem Elektro-Sicherungskasten — daher kam der Gedanke an den Verteiler überhaupt erst. Das Gerät kann schlicht danebengelegt werden.

Damit entfällt die gesamte Elektro-Thematik: kein Eingriff in den Verteiler, keine Hutschienen-Montage, keine Elektrofachkraft, kein Wärmestau im geschlossenen Kasten. Das Gerät steht im Freien neben dem Router, bekommt ein Netzwerkkabel und ein Netzteil, und ist damit fertig.

Auch die Geräuschfrage hat sich entspannt: Adam merkt an, dass Lautstärke an diesem Ort ohnehin keine Einschränkung darstellt. Ein passiv gekühltes Gehäuse bleibt trotzdem die bessere Wahl — nicht wegen der Stille, sondern weil ein Lüfter das einzige bewegliche Teil wäre und damit das erste, was nach Jahren ausfällt.

*Der frühere Abschnitt zu Hutschienen-Einbau, DIN VDE 0100-410 und Verteiler-Belüftung ist damit gegenstandslos und wurde entfernt.*

---

## Was das Gerät leisten muss — und was nicht [NEU 2026-07-25 20:56]

Adam fragt, ob ein so kleines Gerät genügt, wenn wir Videos künftig nicht nur transkribieren, sondern auch Bild für Bild auswerten wollen — „manche müssen wir uns auch anschauen, da reicht die Transkription nicht". Die Sorge ist berechtigt gestellt, löst sich aber auf, sobald man ansieht, wo die Arbeit tatsächlich anfällt.

### Der Pi rechnet nicht. Er trägt.

Das Gerät zu Hause ist ein Briefträger, kein Büro. Es nimmt verschlüsselte Datenpakete entgegen und reicht sie weiter. Es öffnet sie nicht, es dekodiert kein Video, es extrahiert keine Bilder, es analysiert nichts. Die gesamte Verarbeitung — Video zerlegen, Tonspur transkribieren, Einzelbilder auswerten — geschieht dort, wo sie heute schon geschieht: auf dem Server und im KI-Modell.

Die Zahlen dazu sind eindeutig. Schon ein Raspberry Pi der vorigen Generation erreicht in Messungen aus dem Hersteller-Forum rund 874 Megabit je Sekunde durch den verschlüsselten Tunnel; ein konservativerer Praxiswert aus einem Fachleitfaden nennt 200 bis 300. Der Pi 5 liegt darüber. Jeder dieser Werte übersteigt das, was ein deutscher Hausanschluss hochladen kann, um ein Vielfaches.

### Der eigentliche Engpass ist die Leitung, nicht das Gerät

Wenn ein Video ausgewertet werden soll, nimmt es diesen Weg: YouTube schickt es an Adams Hausanschluss, der Pi reicht es durch den Tunnel weiter, der Server empfängt es. Der begrenzende Faktor ist damit Adams **Upload**-Geschwindigkeit — das, was der Anschluss nach außen abgeben kann, und das ist bei den meisten Verträgen deutlich weniger als der Download.

Eine Überschlagsrechnung: Ein zehnminütiges Video in mittlerer Auflösung wiegt etwa 150 Megabyte. Bei zehn Megabit Upload dauert die Weiterleitung rund zwei Minuten, bei 40 Megabit etwa eine halbe. Beides ist für eine Auswertung, die ohnehin im Hintergrund läuft, völlig unproblematisch. Hinzu kommt, dass sich beim Abruf gezielt eine niedrigere Auflösung anfordern lässt — für die Bildauswertung genügt meist deutlich weniger als die höchste Stufe, was die Datenmenge nochmals drückt.

**Zwischenergebnis:** Für das hier beschriebene Vorhaben ist der Pi ausreichend, und zwar mit großem Abstand. Die Bild-für-Bild-Auswertung ändert daran nichts.

### Wo die Grenze wirklich verläuft

Sie verläuft nicht bei der Bildauswertung, sondern bei Adams eigenem weiterführendem Gedanken, den Mietserver ganz wegzulassen und alles zu Hause laufen zu lassen. **Dann** kippt die Rechnung, denn dann müsste das Heimgerät die Arbeit tatsächlich selbst tragen. Drei Punkte sprechen dann gegen den Pi:

*Erstens:* Dem Pi 5 fehlt der Hardware-Baustein zum Dekodieren des gängigsten Videoformats — er beherrscht in Hardware nur das neuere Format. Das ist belegt und wird in der Fachdiskussion als bewusste Streichung gegenüber dem Vorgänger beschrieben. Videoverarbeitung müsste er also rechnerisch stemmen, was langsam wird.

*Zweitens:* Die Spracherkennung läuft heute auf dem Server ohne Grafikbeschleuniger und ist dort schon spürbar rechenintensiv. Auf einem Pi wäre sie um ein Vielfaches langsamer.

*Drittens:* Eine örtliche Bildauswertung durch ein eigenes KI-Modell bräuchte einen Grafikbeschleuniger. Den hat weder der Pi noch der heutige Server.

Adam hat das im selben Atemzug selbst richtig eingeordnet: Für echte Last brauche es „einen kleinen leistungsfähigen Minicomputer" oder einen kleinen Mac, und der Pi sei „nur die ganz schmale Sicherheitslösung". Genau so ist es. **Für den Tunnel: Pi. Für einen Server-Ersatz: eine andere Geräteklasse.** Diese Weiche ist in der Ideensammlung zum Produkt festgehalten und gehört dort vertieft, nicht in dieses Papier.

---

## Einkaufsliste [NEU 2026-07-25 20:56]

Preise vom 25.07.2026, recherchiert bei einem Fachhändler, einem Preisvergleich und auf dem Gebrauchtmarkt. Sie schwanken — als Richtwerte lesen.

### Was gebraucht wird

| Teil | Neu | Gebraucht | Anmerkung |
|---|---|---|---|
| Raspberry Pi 5, 2 GB | ab 46,90 € | ab ca. 43 € | reicht für Tunnel und Sicherung vollständig |
| Raspberry Pi 5, 4 GB | ca. 60–70 € | ca. 50 € | etwas Luft nach oben, mein Vorschlag |
| Netzteil 27 W USB-C, offiziell | ab 11,10 € | oft im Paket dabei | kein beliebiges Handy-Netzteil verwenden |
| Aluminium-Gehäuse, passiv gekühlt | ab 8,90 € | oft im Paket dabei | ohne Lüfter, kein bewegliches Teil |
| Kleine SSD über USB | ca. 20–30 € | ca. 15 € | **wichtig, siehe unten** |
| Netzwerkkabel | ca. 5 € | vorhanden | dürfte im Haus sein |
| **Summe** | **ca. 92–115 €** | **ca. 50–70 €** | |

### Was später dazukommen kann

| Teil | Preis | Wann |
|---|---|---|
| Externe Festplatte für die Sicherung | 60–150 € | Stufe zwei, nicht jetzt |

### Worauf beim Kauf zu achten ist

**Nicht auf Speicherkarte betreiben.** Der wichtigste Punkt. Die üblicherweise beiliegende microSD-Karte verschleißt im Dauerbetrieb und fällt nach Monaten bis wenigen Jahren aus. Viele Gebrauchtangebote enthalten ausschließlich eine solche Karte — beim Preisvergleich also die SSD mitrechnen. Sie ist der Unterschied zwischen einem Gerät, das jahrelang läuft, und einem, das irgendwann ohne Vorwarnung stehenbleibt.

**Gehäuse ohne Lüfter wählen.** Nicht wegen der Lautstärke, die bei Adam ohnehin unkritisch ist, sondern weil ein Lüfter das einzige bewegliche Teil im Gerät wäre und damit der wahrscheinlichste Ausfallpunkt. Ein Aluminiumgehäuse führt die Wärme selbst ab und kostet nicht mehr.

**Beim Netzteil nicht sparen.** Der Pi 5 reagiert empfindlich auf unterdimensionierte Stromversorgung und drosselt dann seine Anschlüsse. Das offizielle Netzteil kostet gut elf Euro und erspart eine schwer zu findende Fehlerquelle.

**Auf Komplettpakete achten.** Adams eigener Gedanke, auf dem Gebrauchtmarkt zu schauen, ist der richtige Hebel. Angebote mit Gerät, Netzteil und Gehäuse zusammen liegen deutlich unter der Summe der Einzelteile.

**RAM-Größe:** Für Tunnel und Sicherung genügt die kleinste Ausführung. Die mittlere kostet wenig mehr und lässt Raum, falls das Gerät später weitere Aufgaben übernimmt. Beides ist vertretbar; ich würde zur mittleren greifen, wenn der Preisunterschied gering ausfällt.

---

## Drei Ausbaustufen

### Stufe null — Überbrückung

**Kosten:** keine. **Sofort verfügbar.**

Für einzelne, dringende Videos genügt vorerst der Mac oder der vorhandene Laptop — nicht im Dauerbetrieb, sondern für den Einzelfall angeworfen. Das trägt, bis das eigentliche Gerät da ist.

### Stufe eins — der kleine Dauerläufer

**Kosten:** 50 bis 70 Euro gebraucht, 95 bis 115 Euro neu. Laufend zwölf bis 18 Euro Strom im Jahr.

Der Pi hält den Tunnel offen. Mehr braucht es zunächst nicht. Das System darauf bleibt bewusst minimal: keine Oberfläche, keine Dienste nach außen, nur die Tunnelverbindung und die Möglichkeit, sich zur Wartung darauf zu verbinden.

**Zum Vergleich:** Der käufliche Gegenentwurf, ein gemieteter Wohnanschluss-Vermittler, kostet etwa zwölf Dollar monatlich. Selbst die teure Neuvariante hat sich nach knapp neun Monaten bezahlt gemacht, die gebrauchte nach gut fünf — und läuft dann weiter, während Miete Miete bleibt.

### Stufe zwei — vom Tunnel zum Rückgrat

**Kosten:** eine Festplatte, je nach Größe 60 bis 150 Euro.

Sobald das Gerät ohnehin durchläuft, kann es mehr als nur den Tunnel halten. Die geplante Sicherungskopie findet hier ihr Ziel: Der Server schiebt seine Daten allabendlich über dieselbe Verbindung nach Hause. Damit liegt die Sicherung an einem anderen Ort als das Original, was eine Sicherung erst zu einer macht.

Weiter ausbaubar wäre das Gerät als Ausweichstelle, falls der Server ausfällt. Nichts davon muss jetzt entschieden werden — es ist der Grund, warum ich zum Pi 5 und nicht zu einem noch kleineren Modell rate: Er hat schnelle Anschlüsse für eine Festplatte und genug Luft nach oben.

---

## Sicherheitsbetrachtung

Pflichtteil, wie bei jeder Änderung am System.

**Der Tunnel selbst — grün.** Die eingesetzte Technik gilt als schlank und gut geprüft. Es entsteht kein neuer Weg von außen ins Haus, denn die Verbindung wird von innen nach außen aufgebaut. Der Server erhält keinen Zugriff auf das Heimnetz, wenn man die Freigabe eng fasst — und das ist ausdrücklich so vorgesehen: Er darf über den Tunnel ins offene Internet, aber nicht zu den Geräten im Haus. Diese Abgrenzung gehört in die Einrichtungsanleitung.

**Das eigene Kleingerät statt des Laptops — grün, und ein echter Gewinn.** Adams Entscheidung verbessert die Sicherheitslage gegenüber dem ursprünglichen Konzept. Ein Gerät ohne persönliche Daten, mit einer einzigen Aufgabe und ohne Dienste nach außen, ist leicht zu überblicken und im Schadensfall ersetzbar. Es braucht regelmäßige Aktualisierungen — das ist die einzige laufende Pflicht.

**Die Wohnanschluss-Adresse — gelb.** Ab dann erscheinen Server-Abrufe unter Adams Hausanschluss. Bei maßvoller Nutzung ist das unauffällig; bei massenhaften Abrufen könnte YouTube auch diese Adresse verstimmen, was dann den privaten Zugang mitträfe. Ein vernünftiger Umgang ist also im eigenen Interesse. Vorgesehen sind eine Wartezeit zwischen Abrufen und eine Mengenbegrenzung.

**Das YouTube-Konto — entschieden: zunächst ohne.** Adam hat zugestimmt, erst ohne Anmeldung auszuwerten. Damit entfällt das Risiko der Kontosperrung vollständig. Falls sich später zeigt, dass ein Konto nötig ist, lässt es sich nachrüsten — dann mit einem eigens angelegten Zweitkonto, dessen Verlust nichts kostet. Adams Wunsch, Abrufe im eigenen Verlauf wiederzufinden, bliebe damit erfüllbar.

**Der Aufstellungsort — grün.** Das Gerät steht frei neben dem Router auf dem Sicherungskasten, nicht darin. Kein Eingriff in die Elektroinstallation, kein Wärmestau, keine Fachkraft nötig. Die frühere gelbe Bewertung des Verteiler-Einbaus ist damit hinfällig.

**Der käufliche Gegenentwurf — rot, deshalb abgelehnt.** Der Vollständigkeit halber festgehalten: Wohnanschluss-Vermittler funktionieren, aber Sicherheitsforscher von Lumen und Trend Micro beschreiben, dass die vermieteten Adressen zu erheblichen Teilen aus Botnetzen stammen oder von Menschen, die über eingebettete Bausteine in Alltags-Apps unwissentlich ihre Leitung abgeben. Das verträgt sich nicht mit der Werte-Charta. Der eigene Tunnel vermeidet diesen Konflikt vollständig — er nutzt nur die eigene Leitung.

---

## Rechtliche Einordnung

Zwei Ebenen, die auseinanderzuhalten sind.

**Urheberrecht.** Nach Paragraph 53 des Urheberrechtsgesetzes ist die private Kopie aus nicht offensichtlich rechtswidriger Quelle zulässig. Das deckt die private Auswertung öffentlich zugänglicher Videos. Quelle: ein Übersichtsartikel von CHIP vom 27.02.2026. Das ist eine Zusammenfassung, kein Rechtsrat — bei kommerzieller Verwertung wäre eine fachliche Prüfung angezeigt.

**Nutzungsbedingungen.** Davon unabhängig untersagt YouTube den automatisierten Abruf ohne Genehmigung. Das ist kein Straftatbestand, aber ein Vertragsbruch, dessen mögliche Folge die Sperrung ist. Diese Ebene bleibt bestehen, gleich welchen technischen Weg wir wählen. Sie ist der Grund für die Zurückhaltung bei Menge und Frequenz.

Für den vorgesehenen Zweck — einzelne Videos auswerten, die Adam ohnehin ansehen würde — halte ich das für vertretbar. Bei einer späteren gewerblichen Nutzung wäre neu zu bewerten.

---

## Laufende Kosten und Vergleich

Die Anschaffungskosten stehen oben in der Einkaufsliste. Was danach bleibt:

| Posten | Betrag |
|---|---|
| Strom (4–6 W Dauerbetrieb) | 12–18 € im Jahr |
| Tunnel-Software | 0 € |
| *Nachrichtlich: gemieteter Vermittler statt eigener Lösung* | *ca. 130 € im Jahr, dauerhaft* |

Der Vergleich fällt deutlich aus: Die gebrauchte Zusammenstellung hat sich nach gut fünf Monaten bezahlt, die neue nach knapp neun — und läuft dann für zwölf bis 18 Euro im Jahr weiter, während Miete Miete bleibt.

---

## Stand der offenen Punkte [NEU 2026-07-25 20:56]

Alle Fragen des Abends sind beantwortet:

- Laptop nicht im Dauerbetrieb — entschieden, sicherheitlich der bessere Weg.
- Raspberry Pi statt Bürorechner — entschieden.
- Auswertung zunächst ohne YouTube-Konto — entschieden.
- Aufstellungsort neben dem Router auf dem Sicherungskasten — geklärt, kein Einbau nötig.
- Reicht das Gerät für Bild-für-Bild-Auswertung? — geprüft und bejaht, siehe oben.

**Zeitliche Einordnung nach Adams Vorgabe:** Nicht im ersten Ausbauschritt. Der YouTube-Zugriff ist derzeit nicht dringend genug, um andere Arbeiten zu verdrängen; er kommt in der nächsten Phase. Bis dahin kann Adam sich in Ruhe auf dem Gebrauchtmarkt umsehen.

**Weiterführender Strang, hier bewusst nicht vertieft:** Adams Überlegung, den Mietserver langfristig ganz durch ein Gerät zu Hause zu ersetzen, sowie die Hardware als Bestandteil eines späteren Kundenprodukts. Beides ist in der Ideensammlung zum Produkt festgehalten — es sind erklärtermaßen Gedanken, keine Entscheidungen.

---

## Nächste Schritte

1. Gerät beschaffen — Adam schaut auf dem Gebrauchtmarkt, Richtwert 50 bis 70 Euro als Paket.
2. Grundsystem aufsetzen, minimal halten, Fernwartung einrichten — etwa eine Stunde.
3. Tunnel auf beiden Seiten einrichten und Schlüssel austauschen — etwa eine halbe Stunde.
4. Vermittler auf dem Server einrichten, Abruf gegen ein Testvideo prüfen — etwa eine halbe Stunde.
5. Erfolgskontrolle: Ein YouTube-Video wird vollständig transkribiert, während der übrige Bot-Betrieb unverändert weiterläuft. Beides muss gleichzeitig zutreffen.
6. Anschließend als Prüfpunkt in die Sitzungen geben, damit die Bot-Seite den Weg kennt.
7. Später und getrennt davon: Stufe zwei mit der Sicherung.

Der Bot-Code bleibt bis dahin unberührt — die Änderungen betreffen den Server und das Heimgerät, nicht das Bot-Verzeichnis.

---

## Offene Unsicherheiten

Der Redlichkeit halber benannt:

- Die genannten Preise stammen vom 25.07.2026 aus einem Preisvergleich und von Kleinanzeigen. Gebrauchtpreise schwanken erheblich, die Angaben sind Richtwerte.
- Der Stromverbrauch von vier bis sechs Watt ist ein Erfahrungswert für den Leerlauf, keine Messung an Adams Gerät. Der Strompreis von 35 Cent ist ein Mittelwert.
- Ob YouTube die Wohnanschluss-Adresse dauerhaft unbehelligt lässt, ist nicht zugesichert. YouTube hat seine Haltung gegenüber Rechenzentren verschärft und könnte das ausweiten. Der Tunnel ist der beste heute verfügbare Weg, keine Garantie auf Jahre.
- Zur Wärmeentwicklung im geschlossenen Verteilerkasten liegt mir keine Messung vor. Die Einschätzung „bei geringer Last beherrschbar" ist plausibel, aber ungeprüft.
