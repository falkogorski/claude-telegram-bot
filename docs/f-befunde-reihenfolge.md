<!-- ROLLE: f-befunde-reihenfolge -->
# F-Befunde der Gegenprüfung — Reihenfolge und Stand

**Stichtag:** 2026-08-23 · **Stand: F-1 bis F-6 erledigt · F-7 bis F-11 offen**
· **überholt durch:** — · **maßgeblich ist diese Datei** (Volltext der Befunde:
`docs/gegenpruefung-2026-08-18.md`; die neuen aus
`BEFUND ULTRACODE 9456f16..d596269`, Engywuck 23.08.)

## Warum diese Datei existiert

Die F-Befunde standen im Laufplan. **Der ist bewusst `gitignored`** — er ist
der Notizzettel der laufenden Sitzung, kein Dokument. Beim Umschreiben seines
Kopfes am Abend des 18.08. sind sie herausgefallen, und weil es keinen Verlauf
gibt, hat es niemand gesehen. Aufgefallen ist es erst, als ich sie heute suchte.

**Die Lehre ist dieselbe wie beim Ablageweg-Grundsatz:** Was eine Reihenfolge
überleben soll, gehört dorthin, wo eine Änderung sichtbar wird. Ein
Notizzettel taugt für den Tag, nicht für eine Woche.

Engywucks Befund ③ verlangt genau das — hier ist es.

## Die Reihenfolge

Keiner dieser Befunde ist deploy-blockierend; sie sind nach **Schaden bei
Nichtstun** sortiert, nicht nach Aufwand.

### F-1 · Vorlese-Kette — falsche Auskünfte im Betrieb `[erledigt 19.08.2026]`

Alle vier Teilbefunde nachgemessen, behoben und mit ausführenden Prüfungen in
beide Richtungen belegt (`scripts/test_vorlese_b5.py`, sechs neue Zeilen).
**Ein Befund war schärfer als notiert:** Der Tag wurde nicht nur unvollständig
geprüft, sondern gar nicht — `Punkt 40.5.` ergab `40. Mai`.

- **Gliederungsnummern** sind gesperrt: Steht ein Wort wie `Punkt`, `Phase`,
  `Abschnitt`, `Regel` davor, ist es keine Datumsangabe. Dazu die fehlende
  Tages-Plausibilität (1–31).
- **`im` ist als Jahres-Hinweis ersatzlos gestrichen** — es trug nie allein
  einen Jahresbezug. Dazu eine **Gegenprobe nach hinten**: Folgt der Zahl eine
  Maßeinheit, gewinnt sie gegen jedes Jahres-Wort davor.
- **`_zahlwort` kennt jetzt „eins" neben „ein"** — die Eins ist das einzige
  deutsche Zahlwort mit zwei Formen.
- **Der Satzpunkt verdeckt nichts mehr**: Punkt und Komma blocken nur noch,
  wenn eine Ziffer folgt. Dezimalzahlen bleiben heil.

**Bewusst nicht behoben** (Konvergenz-Bremse, geht nach F-5): `1985 bis 1990`
wird uneinheitlich gelesen, weil nur die zweite Zahl einen Hinweis davor hat.
Das ist Stil, keine Falschaussage — und die Bereichs-Erkennung samt
Einheiten-Prüfung über den ganzen Bereich wäre teurer als der Gewinn.

### F-2 · Hora: die Kürzung sitzt vor der Suche `[erledigt 19.08.2026]`

Die Ausgabe wird auf die letzten 1200 Zeichen gekürzt, **bevor** `_fehlgrund`
darin sucht. Bei geschwätziger stderr fällt der Kopf weg — und die rote Zeile
mit ihm. Dazu trifft `_ROT_ZEILE` weder `Fehler:` noch `ERROR` noch `failed`,
in einem durchweg deutschsprachigen Projekt.


Beide Teile gemessen, beide bestätigt. **Der erste ist ein Rückfall in einen
bereits behobenen Fehler:** Die rote Zeile stand im Kopf, 200 Zeilen Geschwätz
folgten, gemeldet wurde `der Befehl meldete: ok, alles gut`. Das ist wörtlich
der Halt vom 28.07. — eine Positionsannahme statt eines Inhaltsmerkmals —, und
der Kommentar, der genau davor warnt, stand die ganze Zeit direkt über der
Stelle. Die Kürzung hatte ihn durch die Hintertür ausgehebelt.

- **`_verdichten()` behält beide Enden** und benennt die Lücke. Der Anfang
  trägt meist die Ursache, das Ende die Wirkung; eine Grenze, die nur ein Ende
  bevorzugt, ist wieder eine Positionsannahme.
- **`_ROT_ZEILE` kann jetzt Deutsch.** Gemessen waren sechs von acht typischen
  Fehlerzeilen blind — `Fehler:`, `ERROR:` (das Muster lief ohne `IGNORECASE`),
  `failed`, `abgebrochen`, `verweigert`. Grenzen beidseitig offen nach der
  Stichwort-Regel, dazu eine kurze, ausdrücklich benannte Ausnahmeliste, damit
  „✓ fehlerfrei durchgelaufen" keinen Fehler meldet.

Vier neue Prüfzeilen, jede mit Gegenprobe — die zum Kopf-Befund misst
ausdrücklich mit, dass die alte Kürzung ihn verfehlt hätte.
### F-3 · Versions-Monitor: stille Dauerausfälle `[erledigt, 20.08.2026 abgeschlossen]`

Ein unlesbarer Zeitstempel legt einen manuellen Eintrag **dauerhaft** still und
das Protokoll meldet „vor 0 Tagen gesehen" — eine aktive Falschauskunft. Eine
kaputte Sichtungsdatei setzt alle Fristen zurück. Ein Downgrade wird als Update
gemeldet. Ein unvollständiger Register-Eintrag tötet den Lauf **vor** Protokoll
und Versand.


Vier Teilbefunde, alle gemessen und behoben. **Der schwerste war der vierte:**
Ein unvollständiger Register-Eintrag — ein fehlendes `name` oder `kind` —
tötete `main()` mit einem `KeyError`, und zwar **vor Protokoll und vor
Versand**. Ein Tippfehler im Register hätte den gesamten Monitor stillgelegt,
lautlos: Wer ihn per Zeitgeber laufen lässt, sieht nur, dass keine Meldung
kommt. Jetzt scheitert höchstens der eine Eintrag, und er sagt es.

- **Unlesbarer Zeitstempel** ist jetzt **fällig** statt „gerade eben gesehen",
  und die Meldung nennt den Grund statt „seit -1 Tagen nicht geprüft".
- **Fehlende und kaputte Sichtungsdatei** sind getrennt: Fehlen ist der erste
  Lauf, Kaputtsein ein Befund. Vorher setzte eine beschädigte Datei alle
  Fristen zurück, ohne dass es jemand erfuhr.
- **Rückwärts** ist eine eigene Auskunft: Bei den vergleichbaren Arten fiel der
  Fall stumm in „aktuell", bei den Ungleich-Arten wurde er als Update mit Pfeil
  gemeldet (`1.5 → 1.2`). Er ist keins von beidem. Bei Fingerabdrücken wird
  jetzt „weicht ab" gesagt statt eine Reihenfolge zu behaupten, die es dort
  nicht gibt.

Vier neue Prüfungen, davon zwei **ausführend** — der Lauf wird mit einem
kaputten Register wirklich gefahren, nicht auf Schreibweise geprüft.

**Richtigstellung, gleichentags:** Diese F-3-Zeile nannte **vier** Teilbefunde,
der Volltext der Gegenprüfung nennt **sechs**. Ich habe den Punkt zunächst als
erledigt markiert, ohne gegen die Quelle zu prüfen — dieselbe Klasse Fehler wie
die zwei anderen dieses Tages: eine Zusammenfassung als Wahrheit genommen,
statt sie zu messen. Offen bleiben:

- **`systempaket` kann nie MAJOR werden.** Die Art liegt in
  `_VERGLEICH_UNGLEICH`, und dort wird `major` grundsätzlich als `False`
  zurückgegeben. Ein Debian-Sprung über eine Hauptversion sieht damit aus wie
  ein Wartungs-Update.
- **Der Docker-Handler misst das lokale Abbild, nicht den laufenden
  Container.** Ein gezogenes, aber nie gestartetes Abbild meldet „aktuell",
  während der Dienst weiter auf dem alten läuft.

**Abschluss am 20.08., am Code gemessen statt am Bericht geglaubt:**

- **`systempaket`/MAJOR ist behoben** — `_debian_hauptversion()` existiert und
  greift; mein Bericht stimmte.
- **Der Docker-Rand bleibt offen und ist das auch richtig.** Nachgemessen:
  `claudebot` ist nicht in der Docker-Gruppe (Gruppen: `claudebot users`), der
  Aufruf scheitert mit „permission denied". **Aber der Monitor behauptet
  deshalb nichts Falsches:** Er meldet `lobe-chat: manual` — also *muss von
  Hand geprüft werden* — statt „aktuell". Ich hatte einen stillen Dauerausfall
  vermutet; die Messung hat mich widerlegt. Der blinde Fleck ist benannt, und
  damit erfüllt er die Anforderung, die an ihn gestellt war.
### F-4 · `/updates` misst zweimal getrennt `[erledigt 19.08.2026]`

`classify()` und `blinde_flecken()` befragen jede Quelle **einzeln**. Fällt eine
im ersten Durchlauf aus und antwortet im zweiten, erscheint sie in **keiner**
Liste — das Loch, das der Fix vom 28.07. schließen wollte, ist zeitabhängig
wieder da. Nebenbei: doppelte Netzzugriffe vor Adams Augen.


Gemessen und bestätigt: Eine Komponente, deren Quelle im ersten Durchlauf
ausfällt und im zweiten antwortet, fiel aus **beiden** Listen. Für Adam sah
das aus wie „alles aktuell" — dabei war sie gar nicht beurteilt worden. Das
Loch, das der Fix vom 28.07. schließen wollte, war damit zeitabhängig wieder
da: nicht immer, sondern dann, wenn eine Quelle wackelt. Also genau dann, wenn
es darauf ankommt.

**`messen()` fragt jede Quelle einmal**, `classify()` und `blinde_flecken()`
nehmen das Ergebnis entgegen. Die Netzzugriffe je `/updates` haben sich damit
halbiert (nachgemessen: 2 → 1).

**Ein Fallstrick beim Bauen:** Der Zwischenspeicher darf einen Register-Wechsel
nicht überdauern — sonst beantwortet er eine Frage nach den alten Komponenten
und ist selbst wieder eine Falschauskunft. Der Schlüssel enthält deshalb Pfad
und Änderungszeit des Registers; eine eigene Prüfung hält es fest.
### F-5 · Kleinere Ränder `[erledigt 19.08.2026]`

Der Warteschlangen-Hinweis kam am 18.08. doppelt (einmal Text, einmal Stimme).
Der Warn-Zustand der Limit-Vorwarnung liegt prozessweit ohne Nutzerbezug —
bricht beim zweiten Nutzer. Die Entwarnung bleibt über einen Neustart hängen.


**Der Warn-Zustand hing am Prozess, nicht am Nutzer** — ein zweiter Nutzer
hätte die Warnung nie gesehen, weil sie als schon gemeldet galt. Heute ist Adam
der einzige; die Freigabeliste ist aber eine Menge, keine Person, und ein
Fehler, der erst beim zweiten Eintrag auftaucht, findet sich schwer.

**Die Entwarnung überlebte keinen Neustart.** Der Zustand lag nur im Speicher:
Nach einem Neustart wusste der Bot nicht mehr, dass gewarnt worden war, und
schwieg, als es wieder gut war. Adam bliebe mit einer Warnung zurück, die sich
nie auflöst — dieselbe Klasse Falschauskunft, nur andersherum: nicht ein
falsches Wort, sondern ein fehlendes.

**Beim Bauen sofort ein eigener Fund:** Die Sicherung schrieb `json.dumps`,
während das Modul in `bot.py` `_json` heißt. Der `NameError` verschwand im
stillen `except` — die Funktion tat lautlos nichts, und die Prüfung wäre grün
geblieben, hätte sie nur gelesen statt **ausgeführt**. Der Fehlschlag wird
jetzt protokolliert: verschluckt bleibt er, unsichtbar nicht.

**Zwei Geschwister mitgenommen:** Der B4-Prüfer trug im Kopf noch die am 18.08.
widerlegte Behauptung, der Anbieter schicke den Zustand mit jedem Lauf mit —
in `bot.py` war sie korrigiert, hier stehengeblieben. Und der Prüfer griff auf
die **echte** Marke zu; er hat jetzt seine eigene.

**Aus F-3 nachgezogen:** `systempaket` kann jetzt MAJOR werden (die Epoche vor
dem Doppelpunkt zählt dabei nicht als Hauptversion). Der Docker-Handler bleibt
bewusst beim lokalen Abbild — der Weg über den laufenden Container bräuchte
Docker-Rechte, die der Bot nicht hat, und liefe ungetestet; der **falsche
Kommentar**, der etwas anderes behauptete, war der eigentliche Schaden und ist
richtiggestellt.

**Aus F-1 nachgezogen:** Die Bereichsform (`Saison 1985-1990`) wird jetzt
einheitlich gelesen. In der Kette wandelt `_normalize_number_ranges` den
Bindestrich vorher in ein „bis" — geprüft wird deshalb die ganze Kette.

**Nicht belegt:** Der in dieser Liste zunächst genannte doppelte
Warteschlangen-Hinweis („einmal Text, einmal Stimme") steht so **nicht** im
Volltext der Gegenprüfung und ließ sich im Code nicht nachstellen. Ich habe ihn
beim Zusammenfassen hinzugefügt; er wird hier gestrichen statt stillschweigend
weitergeführt. Fällt er im Betrieb auf, kommt er als neuer Befund zurück.
### F-6 · `sudo`-Lärm im Journal `[erledigt 20.08.2026 — und er war die Spur zu etwas Schwererem]`

**Engywucks Präzisierung zuerst geprüft:** Landet die Zeile dort, wo der
Wachposten liest? **Nein** — sie steht ausschließlich im Journal (vierzehn
Vorkommen in zwei Tagen), nicht in `bot-errors.log`. Der Posten hätte nie
angeschlagen; die Sorge war unbegründet.

**Die Rückverfolgung führte woandershin.** Die Zeitstempel gehören zu meinen
eigenen Regressionsläufen: Der Zielumgebungs-Prüfer startet den **echten**
Tagescheck — und der legte seit A6.1 einen Sichtungs-Vermerk ins **echte**
Auftragsbuch. Am 20.08. um 13:58:23 stand dort ein Eintrag aus einem Prüflauf.

**Der Riegel gegen genau das existiert seit dem 26.07.** (Wegwerf-Pfade für
Postfach, Freigaben, Hora, Blumen). Das Auftragsbuch fehlte darin — nicht weil
der Riegel versagt hätte, sondern weil dieser Ort erst am selben Tag entstand.
Ergänzt, dazu `PENDING_DIR` und ein zweiter Nachweis am Laufende.

**Der Prüf-Eintrag wurde NICHT gelöscht:** Er ist inhaltlich richtig — die
Sichtung für den 20.08. steht ohnehin an. Ein gültiger Eintrag wird nicht
entfernt, weil sein Entstehungsweg unsauber war.

### F-7 bis F-10 · Rang 5 aus Engywucks Ultracode-Befund `[offen, 23.08.2026]`

Aus `BEFUND ULTRACODE 9456f16..d596269` (Engywuck, 23.08., 02:10). Er hat sie
selbst als „nicht in dieser Runde" eingestuft; Rang 1 bis 4 ist geschlossen und
committet. **Keiner davon ist deploy-blockierend.**

**F-7 · `ABHAENGIGKEITEN.md:134` sagt „17 Zeilen", es sind 40** (von ihm
gemessen). Eine Zahl, die von Hand nachgepflegt werden muss, wird irgendwann
nicht nachgepflegt — dieselbe Lehre wie beim `GESAMT`-Zähler des
Regressionsläufers, der deshalb zählt statt zu behaupten. **Der Fix ist nicht
„40 eintragen", sondern die Zahl zählen lassen oder streichen.**

**F-8 · `_repo_read_grund` hat keinen Aufrufer** und widerspricht dem Tor, das
es erklären soll. Ein Erklärtext, den niemand liest, altert unbemerkt — und
dieser hier erklärt ausgerechnet eine Sicherheitsschranke. Entweder verdrahten
(er gehört in die Ablehnungsmeldung) oder entfernen.

**F-9 · `_ist_suchwerkzeug` an 1 von 3 Stellen benutzt** — Vertrauen und
Anzeige widersprechen sich. Dieselbe Klasse wie H5 am 22.08.: Die Funktion war
richtig, ihre Verdrahtung nicht. **Gemessen wird die Funktion, nicht ihre
Verdrahtung** — der Satz, der über dieser ganzen Runde steht.

**F-10 · `presend.py`: `_SCHARFE_MUSTER` `rm` trifft 94 von 173 Dateinamen
falsch**, und `_RE_CODEBLOCK` übersieht CRLF- und Einzeilen-Blöcke. Ein Filter
mit über fünfzig Prozent Fehlalarm ist bereits abgeschaltet, auch wenn er noch
läuft — die Erosion aus Befund H, eine Datei weiter.

**Aus dieser Runde hinzugekommen (nicht von Engywuck):**

**F-11 · Der Dokument-Weg für `.docx` und `.html` ist jetzt zu.** Befund C hat
den Ausweichpfad in die Hauptsitzung geschlossen; damit verliert Adam die
Zusammenfassung von Word-Dateien. `.docx` ist ein ZIP mit XML darin und ließe
sich **ohne Fremdbibliothek** werkzeugfrei lesen (`zipfile` + `re`). Das wäre
kein Ausweichen, sondern der geschützte Weg für ein weiteres Format. Bewusst
nicht in derselben Runde gebaut: Ein Sicherheitsfix und eine Formaterweiterung
gehören nicht in denselben Commit.

**F-12 · `Path.home()` ohne Umgebungsschalter — neun Stellen** `[offen, 23.08.2026]`

Aus Engywucks Differenzmesser-Auftrag, Schritt 2, Punkt 4. Er schätzte „fest
verdrahtete `Path.home()`-Pfade in 16 Produktivmodulen". **Nachgemessen ist die
Klasse deutlich kleiner:** 39 Stellen insgesamt, davon **30 bereits durch einen
Umgebungsschalter abgedeckt** (`os.environ.get(...) or Path.home()/...`).

Übrig bleiben **neun** ohne Schalter:
`bot.py` (136, 652, 659, 3540, 5886, 6013) · `botenpost.py:69` ·
`scripts/start_waechter.py` (119, 195).

**Bewusst NICHT als Differenzart gebaut**, obwohl der Auftrag „gemeldet, nicht
gebrochen" vorsah. Eine Art, die bei jedem Bot-Start neun Stellen meldet, ist
nach einer Woche Dauerlärm — und wird dann überlesen wie jede Meldung, die
nichts ändert. Das ist exakt die Erosion, gegen die Befund H und I an diesem
Tag behoben wurden; sie hier neu einzubauen wäre widersprüchlich.

**Der sinnvolle Schritt ist stattdessen die Prüfung der neun einzeln:** Welche
davon führen Zustand, der in einem Prüflauf geschrieben würde? Die bekommen
einen Umgebungsschalter und fallen damit unter Differenzart B. Der Rest ist
kein Befund.

## Erledigt
- **Zeitgeber-Wache** (Befund B1/B4/B5): gelöschte Timer werden erfasst,
  monotone nicht mehr angeklagt, bewusst Abgeschaltetes hat einen Ausweg —
  `0498ee0` und `325a90d`.
- **Repo-Wächter** (Claudias Befund): Fehlerumleitungen sind kein Schreiben —
  `f2474d0`.
- **Quittung des Abgleichs** (Nachlese ②/③) — `f2474d0`.
