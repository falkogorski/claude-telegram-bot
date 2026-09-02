<!-- ROLLE: f-befunde-reihenfolge -->
# F-Befunde der Gegenprüfung — Reihenfolge und Stand

**Stichtag:** 2026-09-02 · **Stand: F-1 bis F-11 erledigt · F-12 bis F-17 offen ·
F-18 erledigt · F-19 offen · F-20 behoben** (nachgetragen 02.09., stand seit dem 23.08. nur im
Changelog)
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

### F-7 bis F-11 · Rang 5 aus Engywucks Ultracode-Befund `[ERLEDIGT 31.08.2026]`

**Alle fünf in der Nacht zum 31.08. abgearbeitet — vier gebaut, einer gekippt.**
Was dabei über den Befund hinaus gefunden wurde, steht je Punkt dabei; es ist
in drei von fünf Fällen mehr als das Gemeldete.

| | Ergebnis | über den Befund hinaus |
|---|---|---|
| **F-7** | gebaut (`1e5f47b`) | Nicht eine falsche Zahl, **sechzehn** — eine davon driftete in derselben Nacht durch meine eigene Arbeit |
| **F-8** | gebaut (`5c3deff`) | Die tote Funktion trug eine **falsche Zusage**: Ihr fehlten zwei Prüfungen, die die Entscheidung hat. Beide Fassungen sind jetzt **eine** |
| **F-9** | **GEKIPPT** (`b3af4f5`) | Die Reparatur hätte die 💰-Kostenschranke gebrochen — `WebSearch` steht in `_COST_TOOLS`, die Funktion fasst beide Suchen zusammen |
| **F-10** | gebaut (`bc130e4`) | Der Filter war in **beide** Richtungen falsch: 48 % Fehlalarm **und** `rm --recursive` wurde verfehlt |
| **F-11** | gebaut (`42f2ced`) | — der einzige Punkt der Liste, der Adam etwas zurückgibt |

**Ein Nachtrag, der nicht in die Tabelle passt:** Der Commit zu F-8 ging mit
**68/69** hinaus. Ursache war nicht Unachtsamkeit allein, sondern eine Form:
`lauf | tail -1 && git commit` — **die Pipe maskiert den Fehlschlag**, weil der
Rückgabewert der einer erfolgreichen `tail` ist. Berichtigt in `111923b`; der
rote Lauf hatte einen echten Fund enthalten (ein Prüfer mit fest verdrahtetem
VPS-Pfad, der am Mac etwas anderes maß).

---

### F-20 · Das freistehende `&` umging die ganze Positivliste `[BEHOBEN 02.09.2026, am Tag des Fundes]`

**Gefunden beim Aufräumen, nicht durch eine Prüfung** — und das ist der
eigentliche Befund. Gemessen am 02.09.:

```
ls & curl boese.example   →  FREI
ls & rm -rf x             →  FREI
ls &wc                    →  FREI
```

**Ohne Rückfrage, in jedem Modus.** `bot.py` gibt bei `FREI` sofort frei
(`bot.py:3198`); die Ausgangssperre `_AUSGEHENDE_BEFEHLE` sitzt **dahinter**
und wurde nie erreicht. Der Auto-Zustand spielte keine Rolle — dies war auch
im Genehmigen-Zustand offen.

#### Wie es hineinkam

`shlex.split("ls & curl x")` liefert `['ls', '&', 'curl', 'x']`. Das Verb ist
`ls` und steht auf der Positivliste; `&`, `curl` und `x` tragen keinen
Schrägstrich und werden von `_pfad_artig` übersprungen. **Die Shell führt
beides aus, die Prüfung sah nur das erste.**

`WEITERE_VERKETTUNG` hätte es fangen sollen und kennt `[;|]`, `\n`, `||` —
**kein `&`**. Seit der Zerlegung vom 01.09. ist jene Zeile ohnehin
**unerreichbar**: Was sie fängt, fängt die Zerlegung vorher (ausgeführt
gemessen, keine Probe erreicht sie).

**Vorbestehend, nicht neu** — gegen `395de2b` gemessen: dort ebenso frei.

#### Die Behebung, und warum sie keine Textsuche ist

`shlex` mit `punctuation_chars=True` trennt **quote-bewusst**: freies `&` wird
ein eigenes Token, `&&` bleibt `&&`, und `"ESN & More"` bleibt **ein** Token.
Der Ordner `Fitmart : ESN & More` existiert in Adams Rechnungsablage — eine
Textsuche nach `&` hätte ihn bei jedem `grep` in den Dialog geschickt, und ein
Filter, der grundlos anspringt, wird binnen einer Woche abgeschaltet.

**DIALOG, nicht Zerlegung** — dieselbe Linie wie beim Zeilenumbruch: `&` war
nicht beauftragt, und wo nichts entschieden wurde, gilt die konservative
Richtung.

#### Die Lehre, und sie wiegt schwerer als der Fund

**Die Prüfzeilen zu dieser Schranke wären beinahe selbst zahnlos gewesen.** Von
sechs zuerst notierten Fällen blieben zwei auch **ohne** die Schranke im
Dialog — `ls&wc` fällt über die Positivliste (shlex macht daraus **ein** Wort),
ein zweiter Pfad außerhalb der Bereiche über den Pfad. Zwei Zeilen wären **aus
dem falschen Grund grün** gewesen und hätten eine spätere Entkernung gedeckt.
Sie messen jetzt den **Grund**; die zwei doppelt gesicherten stehen getrennt
daneben, damit niemand sie später als Beleg für die Schranke liest.

*Wo Schutz und Zufall dasselbe Ergebnis liefern, misst man die Begründung* —
zum dritten Mal in vier Tagen dieselbe Lehre, diesmal an einer Stelle, die
scharf war.

#### Was offen bleibt

**`WEITERE_VERKETTUNG` ist toter Code** (ausgeführt gemessen). Nicht entfernt:
Aufräumen gehört ans Abschluss-Audit (Phase 10), und eine Streichung im
Sicherheitspfad am selben Tag wie eine Behebung ist genau die Art Arbeit, die
etwas mitreißt. **Vermerkt statt getan.**

---

### F-19 · Dokument mit Beschriftung geht in die Hauptsitzung `[offen, eingetragen 02.09.2026]`

**Der Befund ist vom 23.08. Er stand nie hier, obwohl der Changelog ihn hierher
verwies** — `MIGRATION.md`, Eintrag `2026-08-23 (41)`, im Wortlaut:

> *„**Bewusst offen (F-Liste):** Dokument **mit Beschriftung** geht weiter in
> die Hauptsitzung (dort greift aber der Freigabe-Dialog, und seit H7 ist
> nichts Mächtiges mehr dauerfreigebbar) sowie **25 leichtere Befunde**."*

**Gemessen 02.09.:** `f-befunde-reihenfolge.md` führte F-1 bis F-18, das Wort
*Beschriftung* kam nicht vor. Der Ablageweg war **benannt** und die Datei
existierte bereits — die Entscheidung ist trotzdem nicht angekommen. Das ist
der Ablageweg-Grundsatz an einer Stelle, an der man ihn nicht erwartet hätte.

#### Die Klammer trägt den Eintrag — und sie ist entfallen

*„seit H7 ist nichts Mächtiges mehr dauerfreigebbar"*. Gemessen an `395de2b`:

```
_NO_ALWAYS_TOOLS = ({"WebFetch", "Write", "Edit", "MultiEdit",
                     "NotebookEdit"} | set(_COST_TOOLS))
```

**`Bash` steht nicht mehr darin.** Es hat die Liste am 01.09. mit `ae03f95`
verlassen — 5.27, der Genehmigungs-Umschalter, Adams ausdrücklicher Wunsch.
Das war richtig und gegengeprüft. **Niemand ist danach zu dem Eintrag
zurückgegangen, der sich darauf stützte.**

#### Wie weit das trägt — gemessen, nicht geschätzt

Alles Folgende steht **vor** dem Dauerfreigabe-Kurzschluss (`bot.py:3287`):

| Schranke | Stelle | Wirkung |
|---|---|---|
| Repo-Schreibsperre (8.7) | `bot.py:3137` | `Deny` |
| `bashfreigabe` ABWEISEN | `bot.py:3177` | `Deny` |
| `_AUSGEHENDE_BEFEHLE` | `bot.py:3256`, seit 01.09. | `curl`, `wget`, `nc`, `ssh`, `scp`, `telnet` → Dialog |
| Geheimnis-Marker | `bot.py:3225` | zu, auch fürs Lesen |
| `_NO_ALWAYS_TOOLS` | `bot.py:2367` | `Write`/`Edit`/`WebFetch`/Kosten weiter nie dauerfreigebbar |

**Was nicht mehr hält:** Bash-Befehle, die `bashfreigabe` als **FREI** bewertet,
laufen im Auto-Zustand ohne Rückfrage — auch dann, wenn die Sitzung sie tut,
weil es in einem gelesenen Dokument stand.

**Die verbleibende Reichweite, so eng gesagt, wie sie ist:** Lesen und
Auflisten in den freien Bereichen. **Kein** Weg nach außen, **keine**
Schreibrechte, **keine** Geheimnisse. Der verbleibende Kanal ist **der Chat
selbst** — die Sitzung könnte dazu gebracht werden, Gelesenes hineinzuschreiben.
Das berührt die zweite Richtung von Adams Grundsatz vom 21.08.: *sensible Daten
verlassen das System nicht über Telegram.*

**Kein ausgenutzter und kein konstruierter Fall.** Was gemessen ist: Eine
Begründung ist entfallen, und der Eintrag, der auf ihr stand, blieb unverändert.

**Nicht zu tun, solange dieser Punkt offen ist:** den Beschriftungsweg
schließen (Adam nutzt ihn täglich, und seit dem 02.09. ist er ausdrücklich der
Weg, auf dem er Aufträge übergibt) · am Auto-Modus drehen (er ist gegengeprüft;
der Befund liegt nicht bei ihm). **Aufgelöst wird der Punkt durch den
Signatur-Punkt** — erst mit einem Herkunftsmerkmal lässt sich unterscheiden,
was *aus dem eigenen Haus* stammt.

---

### Der ursprüngliche Wortlaut des Befunds `[Stichtag 23.08.2026]`

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

**F-12 · `Path.home()` ohne Umgebungsschalter — neun Stellen** `[ERLEDIGT 31.08.2026]`

> **Neu gemessen wie verlangt — die Hälfte war keine.** Vier der neun haben
> ihren Schalter eine Zeile darüber (Postfach, Gegenleser, zweimal
> Start-Wächter); mein erstes Raster sah nur drei Zeilen Umfeld. **Drei
> schreiben**: Nutzungszahlen, **Adams persönliche Notizen** und der
> **Heartbeat des Bots** — wer den überschreibt, sagt dem Wächter *er lebt*.
> Zwei lasen an ihren eigenen Riegeln vorbei. Alle fünf haben jetzt einen
> Schalter, die drei schreibenden stehen im Wegwerf-Riegel, und ein dritter
> Nachweis misst am Ende, was tatsächlich ankam (`218ada2`).

**Ursprünglicher Wortlaut:**

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

**F-13 · Die Idiom-Menge ist eingefroren** `[GEPRÜFT, NICHT GEBAUT — 31.08.2026]`

> **Anlass zur Prüfung war die eigene Arbeit:** In derselben Nacht sind fünf
> neue Ablagen entstanden (F-12). Gemessen, ob der Differenzmesser sie
> erkennt — **er tut es**, auch in der mehrzeiligen Schreibweise
> `Path(os.environ.get("X") or (\n    Path.home() / …))`. Die Lücke bleibt also
> das, was Engywuck gemessen hat: `os.getenv`, Subscript und Zweitargument
> kommen im Produktivcode nicht als Ablage vor. **Er ist morgen blind, nicht
> heute** — und heute ist er es auch für die frischen Fälle nicht.

**Ursprünglicher Wortlaut:**

**F-13 · Die Idiom-Menge ist eingefroren** `[offen, 23.08.2026, Engywucks Gegenprüfung]`

`_environ_get_name` in `scripts/differenz.py` kennt **genau ein** Idiom:
`Path(os.environ.get("X") or "/pfad")`. Engywuck hat ein Probemodul mit sechs
Schreibweisen durch den echten Einstieg gefahren — **erkannt wird eine,
verfehlt werden fünf**: `os.getenv`, `os.environ["X"]`, die Vorgabe als zweites
Argument, ein Name als Rückfall, ein Rückfall ohne Schrägstrich (`"outbox"`).

**Nicht scharf-blockierend, und das ist gemessen, nicht vermutet:** `os.getenv`
kommt im Produktivcode null Mal vor; Subscript neun Treffer, alle keine Ablagen
(`TERM`, `HOME`, Bot-Token); Zweitargument fünfzehn Treffer, alle Modellnamen,
Zahlen, URLs oder leere Vorgaben. **Er ist morgen blind, nicht heute.**

**Die Lehre wiegt schwerer als der Befund** und steht im Blaupausen-Heft: Wer
eine Menge bildet, muss auch die Menge der **Schreibweisen** bilden, in denen
ihre Mitglieder auftreten können. Ich hatte die Dateimenge korrekt gebildet
(`git ls-files` statt Endungsmuster) und dabei die Idiom-Menge eingefroren —
dieselbe Krankheit eine Ebene tiefer, und tückischer, weil sie **nach** der
befolgten Regel auftritt und deshalb wie Sorgfalt aussieht.

**F-14 · `GEWOLLT_OFFEN`: vier Einträge, ein Grund** `[BEGRÜNDET NICHT GEBAUT — 31.08.2026]`

> **Der Fix ist teurer, als der Befund vermuten lässt.** *Lesen von Schreiben
> im Prüfer unterscheiden* verlangt eine **Datenflussanalyse**: Der Schlüssel
> wird an eine Variable gebunden, und erst deren spätere Verwendung
> (`write_text`, `open(…, "w")`, `mkdir`, `unlink`) entscheidet. Eine Näherung
> darüber erzeugt Fehlalarme — und ein Prüfer mit Fehlalarmen ist binnen einer
> Woche abgeschaltet, siehe F-10.
>
> **Nicht blockierend:** Die vier Einträge tragen ihre Begründung im Wortlaut
> daneben, jede einzeln geprüft. Der Schaden wäre eine wachsende Ausnahmeliste
> — heute fünf Zeilen. **Wenn sie wächst, ist der Zeitpunkt da.**

**Ursprünglicher Wortlaut:**

**F-14 · `GEWOLLT_OFFEN`: vier Einträge, ein Grund** `[offen, 23.08.2026]`

Fünf Einträge sind nicht zu viele — aber **vier tragen denselben Grund**
(„wird nur gelesen"). Das ist eine **Kategorie, keine vier Entscheidungen**.

Fix: Lesen von Schreiben im Prüfer unterscheiden. Dann bleibt **ein** Eintrag
(das Gedächtnis), und die Liste kann nicht mehr wachsen — statt dass jeder
Lesepfad künftig einzeln begründet dazukommt und die Ausnahme sich zur Regel
mausert.

**F-15 · Differenzart A prüft nur eine Richtung** `[offen, 23.08.2026, Engywucks eigener Fund]`

Eine Registerzeile für ein **nicht existentes** Modul bleibt grün — die
Karteileichen-Richtung, also genau das, womit Adam angefangen hat. Zweite
Differenz derselben zwei Mengen: `soll - ist` statt nur `ist - soll`.

Die Lücke steht in Engywucks Auftrag („Ist: jede versionierte `*.py` → Soll:
eine Tabellenzeile"), nicht in der Umsetzung. Er hat sie selbst gefunden.

**Härte: `meldet`**, nach seinem Kriterium — *bricht, wenn etwas Wirkendes
ungeschützt ist; meldet, wenn etwas Unwirksames herumliegt.* Eine Registerzeile
ohne Modul führt einen Leser in die Irre, bricht aber nichts.

**Die Vorbedingung ist erfüllt:** Der `meldet`-Ausgang steht seit dem 23.08. im
Selbstcheck (`bot.py`, `_c_differenzen`). Vorher wurde eine `MELDET`-Differenz
berechnet und **fallen gelassen** — F-15 wäre als erste solche Art sofort eine
Attrappe gewesen. Genau die Sorge, die ich beim Bauen geäußert hatte; Engywucks
Messung hat sie bestätigt und die Reihenfolge vorgegeben.

**F-16 · `hora.py`: der Riegel hängt an der Disziplin künftiger Schreiber** `[GEBAUT, GEMESSEN, ZURÜCKGENOMMEN — 31.08.2026]`

> ### `[MESSAUFTRAG 31.08., Adams Entscheid: erst messen, dann entscheiden]`
>
> **Die vier Zahlen sind auf diesem Rechner NICHT messbar — und das ist das
> Ergebnis, nicht eine Ausrede.** Gemessen:
>
> - `~/.claude/hora/` existiert am Mac **nicht** (kein Protokoll `laeufe.jsonl`,
>   keine Auftragsliste).
> - `~/.claude/auftragsbuch/` existiert am Mac **nicht**.
> - Das Log-Archiv (`~/Projects/claude-bot-logs`) enthält Gespräche,
>   Tagescheck, Versions- und Wachposten-Protokoll — **kein Auftragsbuch, kein
>   Hora-Protokoll.**
>
> **Der Grund steht im Abgleich selbst und ist der eigentliche Fund:**
> `scripts/log_sync.sh` sichert `logs/conversations` und die Ausarbeitungen.
> **Das Auftragsbuch und Horas Protokoll kommen darin nicht vor.** Sie liegen
> ausschließlich auf dem VPS.
>
> **Damit ist die Entscheidungsgrundlage für F-16 nicht gesichert.** Fällt der
> Server aus, ist sie weg — und mit ihr jede Möglichkeit, im Nachhinein zu
> messen, was der autonome Läufer getan hat. *Ein Läufer, der Befehle ausführt,
> und ein Protokoll, das nur an einem Ort liegt.*
>
> **Was hier belegbar ist, aus den Bot-Protokollen (10.08.):** In Adams
> zwölftägiger Abwesenheit hat Hora **nichts ausgeführt** — Ursache laut
> Protokoll: keine freigegebenen Aufträge in der Warteschlange, und zwar
> absichtlich. Dazu die Aussage: *„Es gibt bisher keine einzige Automatik, die
> ein Modell startet. Hora führt nur Skripte aus."* **Das ersetzt die vier
> Zahlen nicht** — es sagt nur, dass die Menge im fraglichen Zeitraum klein
> gewesen sein dürfte.
>
> **Nichts an Hora geändert**, wie beauftragt.


> **`[BEFUND 31.08.]` Der Einzeiler ist gebaut worden und wieder draußen. Er
> trägt nicht als Riegel-Härtung — er ist eine Architekturentscheidung.**
>
> Gemessen: `braucht_zustimmung = ampel != "gruen" or bool(auftrag.get("befehl"))`
> stellt **jeden ausführbaren Auftrag** unter Zustimmungspflicht — jeder Auftrag,
> der etwas tut, trägt einen `befehl`. Hora führte danach nichts mehr autonom
> aus, sondern legte alles vor. **Fünf abgenommene Prüfzeilen brachen sofort:**
> Kette arbeitet die Liste leer (A1) · geparkte Frage hält den Läufer nicht auf
> (B2) · abhängiger Auftrag wird übersprungen (B2) · Kontingent-Halt hakt nichts
> ab · nur ein Lauf zugleich.
>
> **Das ist nicht das, was der Befund versprach** („macht ihn unabhängig von der
> Selbstauskunft des Schreibers"). Es ist die Entscheidung, dass Hora ohne
> Adams Urteil gar nichts mehr ausführt. Die kann richtig sein — dafür ist das
> Freigabe-Postfach gebaut —, aber **sie gehört Adam, nicht einem Nachtblock.**
>
> **Auch die naheliegende Nebenkorrektur trägt nicht:** Ich hatte die
> Ausführbarkeits-Prüfung vor die Zustimmung gezogen, damit ein Auftrag ohne
> Befehl nicht vorgelegt statt gemeldet wird. Zwei weitere Zeilen brachen —
> denn **ein Auftrag ohne Befehl ist nicht unbrauchbar, er kann eine Frage
> sein** (so stellt der Wachposten seine Befunde ein). Die vorhandene
> Reihenfolge ist richtig.
>
> **Offen für Adam und die Kontrolle:** Soll Hora jeden Befehl vorlegen? Wenn
> ja, sind fünf Prüfstände mitzuziehen, und Hora ist danach kein autonomer
> Läufer mehr, sondern ein Vorschlagender. Hora ist derzeit **ruhend** (kein
> Zeitgeber am Mac, keine Auftragsliste) — es eilt nicht.



**Kein Loch — Engywuck hat den Befund selbst gefahren.** Die Kette bricht
zweimal: Der Wachposten schreibt gar keinen `befehl` (null Vorkommen im ganzen
Pfad), und `wachposten-befund` steht nicht auf der geschlossenen Grün-Liste →
gelb → wird Adam vorgelegt.

Aber der Riegel hängt daran, dass die `art` heute der **Schreiber selbst**
deklariert. Sein Einzeiler macht ihn unabhängig davon:

```python
braucht_zustimmung = ampel != "gruen" or bool(auftrag.get("befehl"))
```

**F-17 · B2 ist ein Argument, kein Messwert** `[ERLEDIGT 31.08.2026]`

> Gebaut als Erreichbarkeits-Messung über den **Aufrufgraphen** des
> Syntaxbaums, nicht über eine Textsuche — ein Umweg über eine
> Zwischenfunktion wäre der Textsuche entgangen (`6d36047`). Mit
> Gegenrichtung: Der Graph muss überhaupt etwas finden, sonst wäre die Zusage
> mit einer leeren Menge zu erfüllen.

**Ursprünglicher Wortlaut:**

**F-17 · B2 ist ein Argument, kein Messwert** `[offen, 23.08.2026, Engywucks Gegenprüfung]`

„Kein Weg zu `task_origins`" ist wahr — **solange niemand den Mail-Pfad an
`process_user_text` hängt.** Nichts misst diese Abwesenheit heute; die
vorhandene Zeile prüft nur, dass die Namen im Berichtspfad selbst nicht
vorkommen.

Eine AST-Zeile, die die **Erreichbarkeit** misst („von den Mail-Handlern aus
ist `process_user_text` nicht erreichbar"), macht daraus einen gemessenen
Befund. **Nicht blockierend** — der Zustand ist heute richtig, nur ungeprüft.

**F-18 · `setdefault` in einem Prüfstand** `[ERLEDIGT 24.08.2026, 00:39]`

Engywucks Fund vom 23.08. spät. `scripts/mess_redeseite.py` setzte
`ALLOWED_USER_IDS` per `setdefault` — die verbotene Schreibweise, auf **genau
der Variablen**, die im Register namentlich als Anlass steht (12/14-Fehlalarm
vom 25.07.).

**Der eigentliche Befund war der Prüfer:** `test_pruefumgebung.py` bildete
seine Menge als `glob("test_*.py")` — die Datei fiel heraus und blieb
unsichtbar. **Einen Tag nach dem Differenzmesser**, dessen ganze Diagnose
lautet: Mengen über eine Eigenschaft bilden.

Beim Beheben zeigte sich die Krankheit ein zweites Mal, eine Ebene tiefer: Die
Prüfung selbst trug eine **Namensliste von vier Ordnern**. Auf die Eigenschaft
umgestellt — *in einem Prüfstand ist jedes `setdefault` falsch* — fand sie
sofort **dreizehn** Dateien statt einer. Alle umgestellt.

Die Mengenbildung trennt jetzt über `tempfile`: Ein Prüfstand legt sich eine
Wegwerf-Ablage an, ein Betriebsskript arbeitet im echten Zustand. Gemessen:
zwei Messwerkzeuge, elf Betriebsskripte.

## Erledigt
- **Zeitgeber-Wache** (Befund B1/B4/B5): gelöschte Timer werden erfasst,
  monotone nicht mehr angeklagt, bewusst Abgeschaltetes hat einen Ausweg —
  `0498ee0` und `325a90d`.
- **Repo-Wächter** (Claudias Befund): Fehlerumleitungen sind kein Schreiben —
  `f2474d0`.
- **Quittung des Abgleichs** (Nachlese ②/③) — `f2474d0`.
