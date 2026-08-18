# Handlungsfähig bleiben

**Stichtag:** 2026-07-26 · **überholt durch:** teilweise umgesetzt — Stufe 1 als B4 (8ec636b), Stufe 2 (Sparmodus) als B7 gebaut und ruhend · **maßgeblich ist die Status-Zeile im Drehbuch**


**Kontingent, Vertretung und der Dirigent — ein Konzept für ein System, das nicht verstummt**

Fassung vom 26.07.2026, 15:40 Uhr · für Adam · erstellt von Claudia (VPS-Bot-Sitzung)

---

## Änderungshistorie

**2026-07-26 15:40** — Erste Fassung. Grundlage: Adams Sprachnachricht vom 26.07., 15:09 Uhr (Reserve-Kontingent als Handlungsfähigkeit, ausgewiesener Vertreter, Dirigent über mehrere Modelle), die Vorarbeit in MIGRATION.md 5.31 / 5.20 sowie die Entscheidungsvorlage „Kontingent-Fallback Ebene 2" vom 25.07.

---

## 0. Worum es geht

Am 25. Juli lief Adam ins Nutzungslimit, und es passierte nichts mehr. Am 24. Juli ging dabei sogar eine Nachricht verloren. Der erste Teil ist seit dem 25. Juli behoben, der zweite nicht: Der Bot verliert nichts mehr, aber er antwortet auch nicht mehr, solange das Kontingent leer ist.

Adams Anspruch ist eindeutig und nicht verhandelbar: **Stille ist inakzeptabel.** Ein Assistent, der rund um die Uhr erreichbar sein soll, darf nicht davon abhängen, ob ein einzelner Anbieter gerade Kapazität übrig hat. Das ist keine Bequemlichkeitsfrage, sondern eine Grundeigenschaft — vergleichbar mit der Frage, ob ein Telefon klingelt.

Dieses Papier beschreibt drei ineinandergreifende Antworten, von der kleinsten zur größten:

1. **Der Reserve-Topf** — ein kleines, vorausbezahltes Guthaben, das nur die Handlungsfähigkeit trägt, nicht die Arbeit.
2. **Der Vertreter** — ein lokales Modell, das einspringt, sich als Vertretung zu erkennen gibt und niemals ausfallen kann.
3. **Der Dirigent** — eine Steuerung, die mehrere Modelle nach Aufgabe, Eignung und verfügbarem Kontingent verteilt.

Die drei bauen aufeinander auf, sind aber einzeln nutzbar. Man kann bei eins anfangen und bei drei aufhören, ohne dass zwischendurch etwas weggeworfen wird.

---

## 1. Wo wir stehen — belegt, nicht erinnert

### 1.1 Was gebaut und geprüft ist

**Punkt 5.31, Kontingent-Pause (seit 25.07. verifiziert).** Läuft das Kontingent leer, gilt die Nachricht nicht mehr als gescheitert, sondern als noch nicht dran. Sie geht unverändert an den Kopf der Warteschlange zurück, die chronologische Reihenfolge bleibt erhalten, und der Bot legt sich in Häppchen schlafen, bis das Kontingent zurück ist. Neue Nachrichten werden weiter angenommen. Die Reset-Uhrzeit wird aus der Anthropic-Meldung **gelesen** — steht keine darin, bekommt Adam den ehrlichen Satz, dass die Meldung nichts dazu sagt, und der Bot versucht es in einer Viertelstunde erneut. Sieben Prüfungen decken das ab, sie laufen im Regressionslauf mit.

**Punkt 2.3, lokales Modell (seit 15.07.).** Ollama läuft als eigener Dienst auf dem Server, an localhost gebunden, mit einem kleinen Modell namens phi4-mini. Es wird heute für Nebenarbeiten benutzt — Kapitel-Überschriften für die Sprachausgabe, künftig Zusammenfassungen. Der Weg dorthin führt über LiteLLM, einen Vermittler, der Anfragen an verschiedene Modelle verteilen kann. Diese Vermittlerschicht ist der spätere Dirigent; sie steht bereits, kennt aber bisher nur eine einzige Adresse.

### 1.2 Die drei Lücken

**Lücke A — der Zugangsfehler.** Beim Kontingent-Limit ist alles geregelt. Bei einem **Zugangsfehler** — abgelaufener Schlüssel, Kontosperre, Störung beim Anbieter — greift ein anderer Zweig im Code: Adam bekommt zwar eine Meldung, aber der Auftrag gilt als aufgegeben und wandert **nicht** zurück in die Warteschlange. Das ist genau der Fall, den Adam meint, wenn er sagt „wenn irgendwas mit dem Zugang ist". Die Lücke ist klein und mit wenigen Zeilen zu schließen: derselbe Rückweg wie beim Kontingent, nur mit anderer Begründung im Text.

**Lücke B — die Vorwarnung.** Am 24. Juli wurde geprüft, ob sich der Füllstand des Kontingents auslesen lässt. Ergebnis: Das Anthropic-Werkzeug meldet von sich aus, wenn sich der Status ändert — mit Auslastung in Prozent, Reset-Zeitpunkt und der Art des Limits. Der Bauplan steht in Punkt 5.20. Gebaut ist er nicht. Damit fehlt heute der Satz „achtzig Prozent verbraucht, in zwei Stunden ist Schluss" — und genau der wäre die Grundlage dafür, rechtzeitig kürzerzutreten, statt in die Wand zu fahren.

**Wichtige Unterscheidung, damit hier nichts durcheinandergerät:** Aktiv nachfragen („wie voll ist es gerade?") lässt sich über den Abo-Zugang **nicht** sauber. Durchgereicht bekommen wir die Warnung nur, während ohnehin gearbeitet wird. Ein selbst geschätzter Füllstand wäre eine Zahl, die vertrauenswürdig aussieht und es nicht ist — deshalb bleibt es dabei: **melden, was der Anbieter sagt, nichts hinzuerfinden.**

**Lücke C — kein Vertreter.** Ebene zwei ist bewusst nie gebaut worden. Die Begründung vom 25. Juli lautete, man solle erst messen, wie oft das Limit überhaupt beißt. Diese Messung hat der Alltag inzwischen erledigt: Es beißt, mehrfach, mit Verlust an Arbeitszeit. Die Vorbedingung ist damit erfüllt.

---

## 2. Der Reserve-Topf

### 2.1 Adams Idee, in einem Satz

Ein kleines Guthaben liegt bereit. Reißt das Kontingent, wird nicht abgeschaltet, sondern **umgeschaltet auf Sparbetrieb**: Das System bleibt ansprechbar, kann Auskunft geben, kann Entscheidungen einholen, kann anleiten — aber es rechnet nicht weiter an großen Aufgaben. Laufende Vorgänge werden sauber stillgelegt statt abgebrochen. Der Topf trägt die Handlungsfähigkeit, nicht die Arbeit.

Das ist ein kluger Entwurf, und er ist präziser als alles, was bisher in der Entscheidungsvorlage stand. Der entscheidende Gedanke darin ist die **Trennung von Handlungsfähigkeit und Produktion**. Sie macht aus einer teuren Notlösung eine billige.

### 2.2 Was Anthropic tatsächlich anbietet — geprüft

Der Topf existiert und heißt „Usage Credits". Belegt aus dem Anthropic-Hilfezentrum (Artikel „Manage extra usage for paid Claude plans", abgerufen am 26.07.2026):

- Er ist **vorausbezahlt**. Man aktiviert ihn in den Einstellungen unter „Usage" und lädt einen Betrag auf. Ohne Aufladung passiert nichts.
- Es gibt ein **monatliches Ausgabenlimit**, das man selbst setzt. Alternativ „unbegrenzt" — das wäre für uns die falsche Wahl.
- Automatisches Nachladen ist **optional** und lässt sich weglassen. Damit ist der Topf ein Deckel, kein Fass ohne Boden.
- Abgerechnet wird zu den **normalen Nutzungspreisen** (siehe unten).
- Er gilt **auch für Claude Code** — also für den Weg, über den unser Bot arbeitet.
- Er lässt sich jederzeit wieder abschalten.

Damit ist Adams Idee nicht nur machbar, sie ist bereits als Produkt vorhanden. Das ist die gute Nachricht.

### 2.3 Der Haken — und er ist wichtig

**Anthropic liefert den Topf, aber nicht die Steuerung.**

Ist das Guthaben aktiviert, springt es automatisch ein, sobald das Abo-Kontingent erschöpft ist. Es fragt niemanden. Es unterscheidet nicht zwischen „Adam will kurz wissen, wie der Stand ist" und „ein Bauprozess arbeitet seit vierzig Minuten mit Dutzenden Werkzeugaufrufen".

Das ist **genau das, was Adam nicht will** — und es hätte zwei unangenehme Nebenwirkungen:

Erstens würde die gebaute Kontingent-Pause nie mehr auslösen. Sie erkennt das Limit an der Fehlermeldung; kommt keine Fehlermeldung, weil das Guthaben still einspringt, läuft alles weiter, nur eben gegen Geld. Der Schutz, den wir gestern gebaut haben, wäre unbemerkt außer Kraft.

Zweitens verbrennt ausgerechnet der teuerste Betriebszustand das Guthaben am schnellsten: ein langer Arbeitslauf mit vielen Werkzeugaufrufen.

**Konsequenz:** Der Reserve-Topf darf erst aktiviert werden, **nachdem** der Sparmodus im Bot existiert. In der umgekehrten Reihenfolge wäre er keine Absicherung, sondern ein Leck.

Ich halte das für den wichtigsten einzelnen Befund dieses Papiers.

### 2.4 Was es kostet — mit Zahlen

Preise laut offizieller Anthropic-Übersicht, abgerufen am 26.07.2026, je Million Token (Eingabe / Ausgabe):

| Modell | Eingabe | Ausgabe | Bemerkung |
|---|---|---|---|
| Opus 5 | 5 $ | 25 $ | das, worauf wir heute laufen |
| Sonnet 5 | 2 $ | 10 $ | Einführungspreis bis 31.08.2026, danach 3 $ / 15 $ |
| Haiku 4.5 | 1 $ | 5 $ | das schnelle, kleine Modell |

Zwischengespeicherte Eingaben kosten nur ein Zehntel des Eingabepreises — das ist für uns erheblich, weil das Regelwerk in jeder Anfrage mitläuft und sich hervorragend zwischenspeichern lässt.

**Überschlag für einen Notbetrieb.** Eine typische Antwort von mir bringt grob 50.000 Token Eingabe mit (Regelwerk, Gedächtnis, Gesprächsverlauf) und erzeugt etwa 1.500 Token Ausgabe. Daraus ergibt sich je Antwort:

| Modell | Kosten je Antwort | 20 $ Guthaben tragen etwa |
|---|---|---|
| Opus 5 | ~0,29 $ | 70 Antworten |
| Sonnet 5 | ~0,12 $ | 170 Antworten |
| Haiku 4.5 | ~0,06 $ | 340 Antworten |

Mit aktivem Zwischenspeicher fällt der Eingabeanteil um bis zu neunzig Prozent — dann tragen 20 $ auf Haiku deutlich über tausend Antworten.

**Zum Vergleich die Gegenrechnung, die Adams Sorge belegt:** Ein einziger längerer Bauvorgang mit vielen Werkzeugaufrufen kann leicht eine halbe Million Token verbrauchen. Auf Opus sind das rund 2,50 $ — für **einen** Vorgang. Zwanzig solcher Läufe wären das ganze Notfallguthaben. Deshalb ist der Sparmodus nicht Zierrat, sondern die Bedingung dafür, dass der Topf überhaupt Sinn ergibt.

**Diese Zahlen sind Schätzungen** auf Basis geprüfter Preise. Der tatsächliche Verbrauch je Antwort ist nicht gemessen; er hängt an der Länge des Gesprächsverlaufs und daran, wie viele Dateien gelesen werden. Vor einer Aufladung sollte einmal echt gemessen werden — das kostet nichts und macht die Zahl belastbar.

### 2.5 Der Sparmodus — was gebaut werden müsste

Der Bot hat bereits eine Warteschlange, einen Arbeiter, der sie abarbeitet, und seit dem 25. Juli einen Pausenzustand. Was fehlt, ist ein **dritter Zustand zwischen „normal" und „pausiert"**.

Der Sparmodus in Stichworten:

- **Auslöser:** Die Vorwarnung meldet Erschöpfung, oder das Limit hat gerade zugeschlagen.
- **Sofortmaßnahme:** Laufende, aufwendige Vorgänge werden **angehalten statt abgebrochen** — der Zwischenstand wird gesichert, damit sie später fortsetzbar sind. Adams Formulierung „sauber abwickeln" trifft es genau.
- **Was noch erlaubt ist:** Nachrichten annehmen und beantworten, im Gedächtnis nachschlagen, Auskunft über den Zustand geben, Entscheidungen einholen, Notizen aufnehmen, Termine merken.
- **Was gesperrt ist:** lange Werkzeugketten, Dateiverarbeitung, Recherche, Codearbeit, alles Mehrstufige. Fragt Adam danach, kommt kein stilles Nein, sondern die Ansage: „Das hebe ich auf, bis das Kontingent zurück ist — soll ich es vormerken?"
- **Modellwahl im Sparmodus:** das kleinste Modell, das die Aufgabe trägt. Für Gespräch und Auskunft reicht Haiku bei Weitem.
- **Ende:** Kontingent zurück, angehaltene Vorgänge werden der Reihe nach fortgesetzt, Adam bekommt eine Zeile darüber, was nachgeholt wurde.

Das ist überschaubarer Aufwand, weil die tragenden Teile schon da sind. Der Sparmodus ist im Kern eine Erweiterung dessen, was am 25. Juli gebaut wurde.

---

## 3. Der Vertreter

### 3.1 Klang und Können sind zwei verschiedene Dinge

Adam hat das in seiner Nachricht selbst präzisiert, und die Präzisierung ist der Schlüssel zum ganzen Kapitel: Mit „trainieren" war **der Klang** gemeint, nicht die Fähigkeit. Der Vertreter soll sich anhören wie ich — und sich zugleich als Vertretung zu erkennen geben.

Das ist gut, denn es ist der leichtere Teil. Klang, Haltung und Umgangsformen stecken bei uns nicht im Modell, sondern im **Regelwerk und im Gedächtnis**: wie angesprochen wird, wie eine Antwort aufgebaut ist, was nie gesagt wird, welche Zeitangaben zulässig sind. Ein kleines Modell, das dieselben Regeln und dasselbe Gedächtnis vorgelegt bekommt, trifft den Ton bemerkenswert gut. Dafür braucht es keinen Feinschliff auf Modellebene.

Was ein kleines Modell **nicht** hat, ist Tiefe: langes Durchdenken, verlässliche Werkzeugbedienung, mehrstufige Arbeit, Genauigkeit bei Code. Das lässt sich durch Training nicht herbeiführen — Feinschliff prägt Form, nicht Vermögen. Wer ein kleines Modell auf große Aufgaben trimmt, bekommt ein kleines Modell, das selbstbewusster falsch liegt.

**Daraus folgt die Aufgabenteilung:** Der Vertreter übernimmt Gegenwart und Gespräch. Die eigentliche Arbeit wartet.

### 3.2 Was der Vertreter können muss

In der Reihenfolge ihrer Wichtigkeit:

1. **Da sein.** Antworten, quittieren, den Faden halten. Allein das beseitigt die Stille.
2. **Das Gedächtnis lesen.** Wer bin ich, was steht an, was war zuletzt. Das ist der Unterschied zwischen einem Vertreter und einem fremden Chatprogramm.
3. **Aufnehmen.** Notizen, Termine, Aufträge — alles, was später von der vollen Fassung abgearbeitet wird. Nichts geht verloren, es wartet nur.
4. **Ehrlich sein über die eigene Grenze.** „Das kann ich in dieser Besetzung nicht — ich lege es dir vor, sobald die Vertretung endet."

Nicht dazu gehören: Code, Recherche, Dateiarbeit, alles mit vielen Schritten. Der Versuch, das mitzuliefern, wäre der sichere Weg zu falschen Ergebnissen, die niemand als falsch erkennt.

### 3.3 Der eigene Name

Adams Vorschlag, dem Vertreter einen eigenen Namen zu geben, ist mehr als Kosmetik. Er löst ein Problem, das sonst hässlich wird: Wenn dieselbe Stimme mit demselben Namen plötzlich flacher antwortet, wirkt das wie ein Qualitätsverlust — oder schlimmer, wie eine Täuschung. Mit eigenem Namen ist es eine **Vertretung**, und jeder weiß, woran er ist.

Die Umsetzung ist schlicht: Der Vertreter meldet sich beim ersten Kontakt einer Vertretungsphase mit einem Satz, danach genügt eine dezente Kennzeichnung. Ich schlage vor, den Namen Adam selbst wählen zu lassen — das gehört ihm, nicht mir.

### 3.4 Die harte Grenze heute

Der Netcup-Server hat **keine Grafikeinheit**, acht Gigabyte Arbeitsspeicher und vier Kerne. Darauf läuft ein Modell mit knapp vier Milliarden Parametern — gut genug für Überschriften aus drei bis sieben Wörtern, nicht gut genug für eine Vertretung.

> **`[K2, nachgezogen 28.07.]`** Hier stand: „die Ollama-Spitze hat bereits 5,10 Gibibyte erreicht". Die Zahl war korrekt **abgelesen** und meinte etwas anderes, als ihr unterstellt wurde: `MemoryPeak` einer cgroup zählt den **Datei-Zwischenspeicher** mit, den der Kernel jederzeit hergibt. Am 26.07. nachgemessen — **2217 MiB Zwischenspeicher gegen 31 MiB echten Anwendungsspeicher**; der tatsächliche Fußabdruck beim Laden liegt bei **3017 MiB**. Herleitung und Gegenprobe in [`arbeitsspeicher-messung-c1.md`](../entscheidungsvorlagen/arbeitsspeicher-messung-c1.md).
>
> **Die Schlussfolgerung dieses Kapitels bleibt unverändert:** Acht Gigabyte tragen keinen Vertreter. Sie steht nur jetzt auf der richtigen Zahl.

**Ein tragfähiger Vertreter braucht andere Hardware.** Das ist Kapitel fünf.

---

## 4. Der Dirigent

### 4.1 Adams Vision

Aus der Sprachnachricht, sinngemäß zusammengefasst: Eine steuernde Instanz kennt die verfügbaren Modelle und die dazugehörigen Kontingente. Sie verteilt Aufgaben danach, was ein Auftrag verlangt und was gerade zur Verfügung steht. Der Anwender merkt davon nichts — außer wenn es ihn betrifft, dann wird es ihm gesagt. Wer ausdrücklich ein bestimmtes Modell will, bekommt es. Ausfallen kann das Ganze nicht, weil unten immer ein lokales Grundmodell steht.

Das ist eine gute Architektur, und sie ist nicht exotisch — sie ist die logische Fortsetzung dessen, was auf dem Server bereits läuft.

### 4.2 Was schon steht

**LiteLLM ist seit dem 15. Juli in Betrieb.** Genau dieser Vermittler ist der Dirigent. Er nimmt Anfragen entgegen und leitet sie an das passende Modell weiter, unabhängig davon, welcher Hersteller dahintersteht. Heute kennt er eine einzige Route, nämlich das lokale Modell. Mehr Routen einzutragen ist Konfigurationsarbeit, kein Umbau.

**Die Datenschutz-Ampel läuft seit dem 15. Juli in Beobachtung.** Sie stuft Anfragen regelbasiert ein und schreibt bislang nur mit, ohne umzuleiten. Die Auswertung ist für Mitte August vorgesehen. Für den Dirigenten ist sie das entscheidende Sicherheitsbauteil — dazu gleich mehr.

**Die Architektur-Leitplanke vom 12. Juli gilt weiter:** Der Hauptagent mit seinen Werkzeugen und Freigabeknöpfen läuft direkt am Abo, **nicht** durch LiteLLM. Der Vermittler steuert die Nebenarbeiten. Das ist bewusst so entschieden und sollte auch beim Ausbau bleiben — ein Dirigent, der den Hauptagenten ersetzt, wäre ein Umbau am tragenden Balken.

### 4.3 Was der Dirigent wissen muss

Damit er sinnvoll verteilen kann, braucht er vier Dinge:

**Erstens: eine Aufgabenklassifikation.** Ist das eine Plauderei, eine Auskunft, eine Recherche, eine Codearbeit, eine Bildauswertung? Daraus folgt, welches Modell überhaupt in Frage kommt.

**Zweitens: eine Vertraulichkeitseinstufung.** Das ist die Ampel. Rote Inhalte dürfen den Rechner nicht verlassen — sie gehen zwingend an das lokale Modell, egal wie viel Kontingent anderswo frei wäre. Diese Regel steht über jeder Effizienzüberlegung.

**Drittens: eine Kontingent-Buchhaltung.** Was ist bei welchem Anbieter noch verfügbar, wann füllt es sich wieder auf, was kostet ein Aufruf. Für das Abo ist das schwierig (siehe Lücke B), für nutzungsabhängige Zugänge einfach, weil dort jeder Aufruf gemessen wird.

**Viertens: eine Vorrangregel.** Wenn Adam sagt „nimm dafür X", gilt X. Punkt. Der Dirigent entscheidet nur, wo nicht entschieden wurde.

### 4.4 Unsichtbar in der Bedienung, sichtbar in der Benennung

Hier steckt eine Spannung, die Adam in seiner Nachricht bereits selbst aufgelöst hat, und ich möchte sie festhalten, weil sie leicht wieder verlorengeht.

Das Grundprinzip „unsichtbare Komplexität" besagt: Der Anwender soll nichts von Sitzungen, Schnittstellen und Kontingenten wissen müssen. Die Werte-Charta besagt zugleich: Es darf keine stillen Entscheidungen geben, deren Folgen jemand hinterher erraten muss.

Beides gilt, weil sie sich auf verschiedene Ebenen beziehen. **Unsichtbar ist die Mechanik** — welcher Weg gewählt wurde, welcher Schlüssel benutzt, wie abgerechnet wird. **Sichtbar ist die Auswirkung** — wenn eine Antwort von einer schwächeren Besetzung kommt, wird das gesagt. Nicht als Warnhinweis in jeder Zeile, sondern einmal, ruhig, beim Wechsel.

Die Faustregel: **Was den Anwender nichts angeht, bleibt weg. Was ihn betrifft, wird gesagt.**

### 4.5 Sicherheit — die Leitplanke, die nicht verhandelbar ist

Jeder zusätzliche Anbieter im Verbund ist ein **neuer Datenabfluss**. Das ist keine Formalie: Sobald ein Gespräch an einen weiteren Hersteller geht, gelten dessen Bedingungen, dessen Aufbewahrungsfristen, dessen Umgang mit Trainingsdaten — und dessen Rechtsraum.

Daraus folgen drei harte Bedingungen für den Ausbau:

1. **Die Ampel muss vor dem Dirigenten scharf sein.** Solange sie nur beobachtet, darf kein zusätzlicher Anbieter eingebunden werden. Sonst entscheidet eine Verteilungslogik über Inhalte, deren Schutzbedarf sie nicht kennt. Die Auswertung ist ohnehin für Mitte August vorgesehen — die Reihenfolge passt.
2. **Jeder neue Anbieter einzeln, mit eigener Betrachtung.** Nicht „Fremdmodelle einbinden", sondern „diesen einen, für diese Aufgabenklasse, mit dieser Einstufung". Die Leitplanke, keine OpenAI-Dienste im Stapel zu führen, bleibt bestehen, bis Adam sie ausdrücklich ändert.
3. **Rot bleibt lokal, ausnahmslos.** Kein Kontingentmangel rechtfertigt, einen roten Inhalt nach außen zu geben. Ist das lokale Modell nicht verfügbar, ist die richtige Antwort „das kann ich gerade nicht bearbeiten" — nicht ein Ausweichen an einen Dritten.

---

## 5. Hardware — welche Klasse trägt was

### 5.1 Der Zusammenhang, der zeitlich drängt

Adam schaut derzeit nach einem Heimgerät für den YouTube-Tunnel und informiert sich auf dem Gebrauchtmarkt. Für das reine Durchleiten von Netzverkehr genügt ein Raspberry Pi vollkommen — das wurde am 25. Juli geprüft und mit Herstellerangaben belegt.

Für einen **Vertreter** genügt er nicht, und zwar nicht knapp, sondern deutlich. Wenn dasselbe Gerät später beides tragen soll, ist es die falsche Klasse. Deshalb steht dieses Kapitel hier und nicht im August: **Es geht darum, einmal zu kaufen statt zweimal.**

### 5.2 Was welche Speichergröße trägt

Zusammengetragen aus mehreren Quellen (siehe Quellenteil); die Angaben decken sich im Kern, weichen an den Rändern ab. Alle Angaben beziehen sich auf gebräuchlich verkleinerte Modelle.

| Arbeitsspeicher | Was läuft | Taugt als Vertreter? |
|---|---|---|
| 8 GB (heutiger Server) | bis etwa 7 Milliarden Parameter | nein |
| 16 GB | 7 bis 13 Milliarden | grenzwertig, für Gespräch knapp brauchbar |
| 24 GB | 13 Milliarden bequem | ja, für Gespräch und Auskunft |
| 32 GB | 30 Milliarden — hier widersprechen sich die Quellen: eine nennt es „komfortabel", eine andere nur „mit starker Verkleinerung" | ja, mit Spielraum |
| 48 bis 64 GB | 70 Milliarden | ja, mit deutlichem Abstand |

Zur Geschwindigkeit: Auf einem Mac Mini mit M4-Chip liefert ein Modell mit 30 Milliarden Parametern etwa 12 bis 18 Token je Sekunde — laut Quelle „schnell genug für ein bequemes Gespräch in Echtzeit". Das entspricht ungefähr zügiger Lesegeschwindigkeit. Für eine Vertretung reicht das gut.

### 5.3 Gerätevorschläge mit Preislage

**Preise sind Momentaufnahmen vom 26.07.2026 und teils aus Sekundärquellen — vor einem Kauf verbindlich nachprüfen.**

| Klasse | Beispiel | Preis | Wofür |
|---|---|---|---|
| Nur Tunnel | Raspberry Pi 5 | 50–115 € | Netzverkehr durchleiten, Sicherungsziel |
| Einstieg Vertretung | Mac Mini M4, 16 GB | ab etwa 599 €, im Angebot 499 € | Gespräch, Auskunft, Gedächtnis |
| Empfehlung | Mac Mini M4 mit 24 bis 32 GB | grob 800–1.100 € | bequemer Vertreter mit Reserve |
| Reichlich | Mac Mini M4 Pro mit 48 GB | um 1.900 € | echte Alternative, nicht nur Notbesetzung |
| Andere Bauart | Mini-PC mit AMD-Chip, 32 GB | je nach Modell | vergleichbar, oft günstiger, mehr Einrichtungsaufwand |

Ein Rechner mit dedizierter Grafikkarte wäre schneller, ist aber laut, verbraucht unter Last mehrere hundert Watt und passt nicht neben einen Router in eine Wohnung. Für den Dauerbetrieb ist das die schlechtere Wahl.

### 5.4 Meine Empfehlung

**Zwei Geräte, nicht eines.** Der Pi bleibt, wofür er gedacht war: Tunnel und Sicherung, sparsam und lautlos, für kleines Geld. Der Vertreter kommt später auf ein eigenes Gerät, wenn er wirklich gebraucht wird.

Begründung: Ein Gerät, das beides kann, kostet das Zehn- bis Zwanzigfache des Pi. Es jetzt zu kaufen hieße, den teuren Teil zu bezahlen, bevor die Software existiert, die ihn nutzt. Der Pi dagegen wird sofort gebraucht und behält seinen Zweck auch dann, wenn später ein größeres Gerät danebensteht — als Sicherungsziel und als Netzzugang bleibt er sinnvoll.

**Falls Adam es anders sieht** und ohnehin ein größeres Gerät möchte: Dann bitte gleich mit mindestens 24 Gigabyte, besser 32. Der Unterschied im Preis ist überschaubar, der Unterschied in dem, was läuft, ist erheblich — und Speicher lässt sich bei diesen Geräten später **nicht** nachrüsten.

---

## 6. Stufenplan

Die Reihenfolge ist nicht beliebig. Jede Stufe macht die nächste erst sinnvoll.

### Stufe 1 — Die Lücken schließen (Aufwand klein, Kosten null)

- **Zugangsfehler wie Kontingentfehler behandeln.** Nachricht bleibt in der Warteschlange, Klartextmeldung, Wiederaufnahme.
- **Vorwarnung durchreichen.** Der Bauplan aus Punkt 5.20 wird umgesetzt: Meldet der Anbieter Annäherung ans Limit, kommt eine dezente Nachricht mit Reset-Uhrzeit. Kein Dauergepiepe.
- **Verbrauch einmal echt messen.** Was kostet eine typische Antwort wirklich? Damit werden aus den Schätzungen in Kapitel 2.4 belastbare Zahlen.

Das ist die Stufe, die ohne jede Entscheidung von Adam auskommt, weil sie nichts kostet und nichts Neues einführt — sie repariert und misst nur.

### Stufe 2 — Der Sparmodus (Aufwand mittel, Kosten null)

- Dritter Betriebszustand zwischen normal und pausiert.
- Laufende Vorgänge anhalten statt abbrechen, Zwischenstand sichern.
- Erlaubte und gesperrte Aufgabenklassen festlegen.
- Kleinstes taugliches Modell für den Sparbetrieb.
- Wiederaufnahme mit einer Zeile Bericht.

Diese Stufe ist die Bedingung für Stufe drei. Ohne sie wäre der Reserve-Topf ein Leck.

### Stufe 3 — Der Reserve-Topf (Aufwand klein, Kosten: was Adam auflädt)

- Guthaben aktivieren, monatliche Obergrenze setzen, automatisches Nachladen **aus**.
- Empfehlung für den Anfang: **20 $ mit einer Obergrenze von 20 $ im Monat.** Klein genug, dass ein Fehler nicht wehtut; groß genug, um mehrere Tage Sparbetrieb zu tragen.
- Nach vier Wochen auswerten: Wie oft griff er? Was hat er gekostet? Danach anpassen.

💰 **Vor der Aufladung gehört ein Kostendialog — Höhe und Quelle, wie immer.**

### Stufe 4 — Der Vertreter (Aufwand mittel, Kosten: Hardware)

- Hardware beschaffen, sobald Stufe zwei läuft und der Bedarf belegt ist.
- Regelwerk und Gedächtnis für das kleine Modell aufbereiten — gekürzt, denn ein kleines Modell verträgt keinen Regelberg.
- Zugriff aufs Gedächtnis über eine Suche, nicht über Mitgeben des Ganzen.
- Eigener Name, eigene Vorstellung, klare Grenzansage.
- Übergabe und Rückgabe geordnet: Was in der Vertretungszeit aufgenommen wurde, wird bei der Rückkehr vorgelegt.

### Stufe 5 — Der Dirigent (Aufwand groß, Kosten je nach Anbietern)

**Voraussetzung: Die Ampel ist scharf, nicht mehr in Beobachtung.**

- Aufgabenklassifikation, Kontingent-Buchhaltung, Vorrangregel.
- Anbieter einzeln aufnehmen, jeder mit eigener Betrachtung und eigener Freigabe.
- Sichtbarkeit: Wechsel wird benannt, Mechanik bleibt unsichtbar.
- Vorausschauendes Verteilen — teure Aufträge dann, wenn Kontingent da ist; Kleinkram immer auf das kleinste taugliche Modell.

Das ist der Teil, mit dem Adam nach seiner Rückkehr experimentieren will. Er ist zugleich der Teil, der am ehesten Produktcharakter hat — ein System, das mehrere Zugänge eines Anwenders bündelt und daraus mehr macht als die Summe, ist ein Verkaufsargument.

---

## 7. Was Adam entscheiden muss

Nichts davon ist eilig, außer dem letzten Punkt.

1. **Stufe 1 sofort?** Sie kostet nichts, führt nichts Neues ein und schließt eine belegte Lücke. Meine Empfehlung: ja, ohne weitere Rückfrage.
2. **Sparmodus vor Reserve-Topf — einverstanden?** Ich halte die Reihenfolge für zwingend. Wer den Topf zuerst aktiviert, hebt den gerade gebauten Schutz unbemerkt auf.
3. **Höhe des Reserve-Topfs.** Mein Vorschlag: 20 $ mit gleich hoher Monatsgrenze, danach nachsteuern.
4. **Name des Vertreters.** Adams Wahl.
5. **Hardware-Frage, und die drängt** — nicht wegen der Technik, sondern weil Adam gerade auf dem Gebrauchtmarkt schaut: Pi als reines Tunnelgerät, wie am 25. Juli geplant, und der Vertreter später auf eigenem Blech? Oder gleich ein größeres Gerät für beides? Wenn Letzteres: mindestens 24 Gigabyte, besser 32, weil nicht nachrüstbar.

---

## Quellen

**Eigene Prüfung im System (26.07.2026):** MIGRATION.md Punkte 2.1, 2.3, 5.20, 5.31, 5.32, Architektur-Leitplanke F1; `2026-07-25_kontingent-fallback-ebene2.md`; Fehlerbehandlung in `bot.py` (Zweige für Zugangsfehler, Kontingent, Transportgrenze, Kontextüberlauf).

**Anthropic, offiziell (abgerufen 26.07.2026):**
- Preisübersicht der Claude-Plattform — Modellpreise, Zwischenspeicher-Multiplikatoren, Stapelverarbeitungsrabatt.
- Hilfezentrum, „Manage extra usage for paid Claude plans" — Vorauszahlung, Ausgabengrenze, automatisches Nachladen, Geltung für Claude Code.

**Hardware (Sekundärquellen, mehrfach abgeglichen, teils widersprüchlich — vor Kauf nachprüfen):**
- SitePoint, „Local LLMs Apple Silicon Mac 2026" — Speichergrößen zu Modellklassen.
- Starmorph, „Best Mac Mini for Running Local LLMs" — Preislagen, 48 GB für 70-Milliarden-Modelle.
- Medium (Ewan Mak), „Mac Mini M4 vs AMD Mini PCs for Local AI" — 12 bis 18 Token je Sekunde bei 30 Milliarden Parametern.
- Slashskill, „Best Hardware for Running LLMs Locally in 2026" — abweichende, vorsichtigere Einschätzung zu 32 GB.
- UGREEN-Blog und skill-sprinters.de — Preislage Mac Mini M4 im deutschen Markt.

**Ungeprüft und ausdrücklich als offen gekennzeichnet:** der tatsächliche Tokenverbrauch je Antwort in unserem Betrieb; die Frage, ob das aufgeladene Guthaben über den Abo-Schlüssel des Bots genauso greift wie über die normale Anmeldung — beides sollte vor Stufe drei einmal gemessen werden.
