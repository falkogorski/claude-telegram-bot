# ARBEITSPAKET FÜR MICK — durcharbeiten, eins nach dem anderen

**Von:** Engywuck (Kontrolle) · **Stand:** 28.08.2026, 17:08 MESZ
**Repo-Stand beim Schreiben:** `0b4d7bc`, Arbeitsbaum sauber
**Adams Ansage:** Fünf-Stunden-Fenster ist frei, er ist ab ~18 Uhr unterwegs und
kann **nicht** freigeben. **Alles hier ist entschieden — nichts wartet auf ihn.**

**Modus: Durchlauf.** Ein Punkt nach dem anderen, jeder einzeln committet.
**Vor jedem `git commit` läuft `bash scripts/regressionstest.sh` durch.**

**Fundort aller genannten Papiere:** `claude-bot-logs/ausarbeitungen/`

---

## RANG 0 — Ablage geradeziehen (Minuten, vor allem anderen)

**① Betriebslage RUHE austragen.** Adam am 28.08., 00:45 Uhr wörtlich:
*„Ruhemodus bitte aus, genau!"* Die Bedingung („Adams Rückkehr") ist eingetreten.
Mit dem Austrag tauen die acht Rang-A-Prüfzeilen wieder auf — **sie sind
weiterhin blind**, siehe Rang 6.

**② Karteileiche:** Der Statuskopf des Gestalten-Auftrags steht auf „offen, Bau
am 25.08."; der Bau ist erfolgt (`756f673`…`bf94ac9`). Eine Zeile.

**③ Überholt-Vermerk:** `2026-08-27_testplan-codex-gegenlesen.md` ist durch
`2026-08-27_auftrag-grundriss-vergleich.md` ersetzt (Adam hat den Kern am 27.08.
um 19:22 abgelehnt). Ohne Vermerk liest er sich in vier Wochen wie der gültige
Stand — Regel ⑪.

## RANG 1 — `anthropic` aus den Anforderungen streichen (Minuten)

**Adams Entscheid vom 28.08.** Gemessen, dreifach:

```
Import im ganzen Repo                       -> kein einziger
claude-agent-sdk 0.2.127, Abhängigkeiten    -> KEINE anthropic-Abhängigkeit
anthropic installiert?                      -> NEIN — und das SDK läuft trotzdem
```

**Das ist ein Kostenregel-Punkt, kein Aufräumen.** `anthropic` ist die Bibliothek
für die **kostenpflichtige** Schnittstelle, `claude-agent-sdk` die für Adams Abo —
zwei Pakete, zwei Geldtöpfe. Die Zeile `anthropic>=0.50` hält den Weg zur
Abrechnung pro Zeichen offen, ohne dass ihn jemand braucht.

**Auflage:** In die Liste der **direkten** Anforderungen gehört nur, was wir
selbst importieren. Sollte `litellm` das Paket transitiv ziehen, bringt es das
Elternpaket in passender Fassung mit — die direkte Zeile bleibt trotzdem falsch.

## RANG 2 — Die Websuche ist ausgefallen (akut)

**`2026-08-27_bauauftrag-websuche-faellt-still-aus.md`** · Adam frei 27.08., 13:52

Am 27.08. lieferten zwölf von fünfzehn Anfragen „Keine Treffer" — **alle vier
Zulieferer waren tot**, und niemand hat es bemerkt. Claudia hielt es für „nichts
gefunden" und hat Adam auf dieser Grundlage geschrieben.

**Meine Auflage ist der eigentliche Auftrag, nicht die Reparatur:** Ein Ausfall
aller Zulieferer muss **als Ausfall** gemeldet werden. „Gesucht, nichts gefunden"
und „gar nicht gesucht" dürfen nicht denselben Rückgabewert haben. Ohne diese
Unterscheidung ist der Anlass repariert und die Klasse offen.

## RANG 3 — Adams täglicher Schmerz (ein Block, beide zusammen)

**`2026-08-25_bauauftrag-freigabedialog-klartext.md`** — Adam hat am lebenden
Fall abgenommen (25.08., 09:36: *„das hätte mir so gereicht"*)
**`2026-08-26_bauauftrag-bash-sitzungsfreigabe.md`** — Adam 26.08., 11:55

Sie berühren dieselbe Stelle; einzeln gebaut kollidieren sie.

### Der Befund, der den Auftrag halbiert — von mir gemessen

**Die Erklärung kommt bereits an. Der Bot wirft sie weg.** Im installierten SDK
(0.2.127):

```
ToolPermissionContext trägt: decision_reason · title · display_name ·
                             description · blocked_path
bot.py:2730  async def can_use_tool(tool_name, tool_input, context: ToolPermissionContext)
grep nach context.description / .title / .display_name / .decision_reason -> KEIN Treffer
```

Der Bot nimmt den Kontext entgegen und liest **kein einziges** Feld aus.
**Der Auftrag schrumpft von „einen Kanal bauen" auf „vier Felder auslesen".**
Und er braucht das SDK-Update **nicht** — die Felder sind im laufenden Stand da.

### Meine Bauvorschrift — sie folgt aus dem Code, nicht aus Geschmack

Gemessen in `_internal/query.py:436–450`:

| Feld | Herkunft | gilt als |
|---|---|---|
| `description` (bei Bash auch `tool_input["description"]`) | **vom Modell** — der Instanz, die die Freigabe will | **behauptet** |
| `decision_reason` · `title` · `display_name` · `blocked_path` | von der Claude-Code-CLI | **gemessen** |

**Beides muss optisch getrennt sein.** Die Modell-Angabe wird als Angabe der
antragstellenden Sitzung gekennzeichnet, die CLI-Felder stehen als
Maschinen-Angabe daneben, die Rohform bleibt unverändert darunter.
`blocked_path` ist ein Geschenk: Die CLI sagt selbst, welcher Pfad den Riegel
ausgelöst hat — genau Adams „ich muss wissen, worauf zugegriffen wird".

**Erster Handgriff im Bau: einmal protokollieren, was real ankommt**, je
Werkzeugart eine Zeile. Ich habe belegt, dass die Felder existieren und
durchgereicht werden — **nicht**, dass die CLI sie überall befüllt. Bei leerem
Feld darf der Dialog nicht schlechter aussehen als heute.

### Claudias zwei Fragen an mich — beantwortet

**① Reihenfolge im Dialog:** Die Frage war falsch gestellt. In beiden Anordnungen
bleibt offen, **woher** der Satz stammt. Nicht die Reihenfolge ändern, sondern
die **Herkunft kennzeichnen** — Claudias Reihenfolge (Klartext oben) bleibt.

**② Einstufung in der Werkzeugspur:** Nein. Eine Einstufung ohne Entscheidung
erzieht zum Überlesen — Adams eigene Regel *„keine Frage ohne Wirkung"*.

### Zum Bash-Schalter — ich ersetze Claudias Auflage 1

Sie schlägt eine **Rot-Wort-Liste** vor. Das ist die falsche Bauform, und ich
habe den Beleg selbst gemessen (Entkernungs-Befund K5): **Verbots-Wortlisten sind
konstruktiv unvollständig** — „kein Netzabruf" kannte `http.client` nicht, „kein
Modell-Aufruf" kannte den Weg übers eigene Bot-Modul nicht. Bei Shell-Befehlen ist
es schlimmer, weil dieselbe Wirkung beliebig viele Schreibweisen hat.

**Stattdessen Positivliste — und sie existiert bereits.** `_is_repo_read_cmd`
macht genau das Richtige: benannte Lese-Verben, keine Verkettung, keine
ausführenden Schalter, alle Pfade im Repo, Geheimnispfade zu. **Der Auto-Modus
docket ausschließlich daran an.** Was sie nicht als harmlos erkennt, fragt.

*Der Unterschied: Ist die Positivliste zu eng, merkt Adam es sofort an einer
Rückfrage. Ist eine Verbotsliste zu kurz, merkt es niemand.*

Claudias Auflagen 2 (Zeitablauf) und 3 (**nur in der Sitzung, nie auf die
Platte**) übernehme ich unverändert. Die 60 Minuten sind ein Vorschlag — nach
Adams Bezugslisten-Gedanken gehört die Zahl als benannte Größe, nicht fest in
den Code.

## RANG 4 — Stundenblume, beide Aufträge in einem Zug

**`2026-08-27_bauauftrag-stundenblume-auslagerung.md`** · frei 27.08., 18:04
**`2026-08-28_bauauftrag-stundenblume-nur-bei-aenderung.md`** · Adam 28.08., 10:07

**Der Dämpfer-Fix ist zwingend Teil davon** — ich habe ihn am Code bestätigt: In
`_daempfen()` wird der Stand **nur über die aktuellen Gründe** gebaut; eine
entwarnte Kennung fällt heraus und ist beim nächsten Auftreten unbekannt, also
trifft `jetzt − 0 >= 3600` immer zu. Claudias Beleg vom 16.08. (26 Wechsel in 50
Minuten) passt genau. **Ohne diesen Fix verschärft die Umstellung den Fall.**

**Entscheidung 1 = A (still an ruhigen Tagen)** — und hier ist der Nachweis, der
im Auftrag fehlt und hineingehört:

Der Einwand gegen Stille steht in unserer Geschichte: Am 29.07. starb der
Tagescheck, und es fiel **einundzwanzig Tage** nicht auf. **Stille ist von Tod
nicht zu unterscheiden.** Deshalb habe ich gemessen, ob die Umstellung die
Kreuzverschränkung beschädigt — **sie tut es nicht:**

```
stundenblume.py:222/231  meldet „tagescheck-still"       (Blume bewacht Tagescheck)
daily_check.sh:208–212   ruft stundenblume.py --pruefen  (Tagescheck bewacht Blume)
stundenblume.py:565      KETTE.open("a") — VOR und UNABHÄNGIG vom Melde-Zweig
```

**Die Kette wächst aus Läufen, nicht aus Meldungen.** Damit ist Stille sicher.
Der Nachweis gehört in den Auftrag, sonst ist beim nächsten Umbau wieder offen,
ob Stille erlaubt ist.

**Entscheidung 2 = A (eine Erinnerung nach zwölf Stunden, nur bei Rot).** Rot
heißt *Warten auf Adams Daumen*; ein rotes Ereignis um 05:00 Uhr, das bis zum
nächsten Morgen schweigt, ist der stille Bruch. **Die Zwölf als benannte Größe**,
nicht fest im Code.

## RANG 5 — die vier kleinen, in einem Zug

**`2026-08-26_bauauftrag-anfuehrungsstellen-und-riegel.md`** — die vier
Anführungsstellen. **Von mir nachgemessen auf `a2ba359`, beide Python-Fassungen:**
genau `bot.py:4777, 4808, 4870, 4878`, keine Doppelmeldung, keine als Ganzes
ausgewogene Zeile darunter. Riegel und Umlaute hängen mit dran.

**`2026-08-27_bauauftrag-linktext-in-sprachausgabe.md`** — Variante 1, Adam 13:45.

**`2026-08-27_bauauftrag-ueberschrift-am-nachrichtenende.md`** — Fundstelle
bestätigt (`bot.py:10697–10699`, harter Schnitt bei 1024). Adam hat es **viermal**
gemeldet.

**`2026-08-27_bauauftrag-postfach-grenze-nach-absenderart.md`** · frei 18:32 —
**mit zwei Änderungen:**

- **Streichen:** die Auflage, zwei Meldungstexte nachzuziehen. Claudias eigene
  Berichtigung, von mir bestätigt: `bot.py:6257` setzt `POSTFACH_GRENZE` als
  Variable ein, der Text zieht mit.
- **Aufnehmen:** Am 27.08. um 20:46 fanden sich drei Aufträge mit dem Vermerk
  *„Zurückstellen fehlgeschlagen nach: gedrosselt"*. **Die Rückstellung greift
  nicht in jedem Fall** — das widerspricht der Zusage vom 20.08. Ein Riegel,
  dessen Rückstellung scheitern kann, verliert genau das, was er schützt.

*Praktischer Hinweis:* `POSTFACH_GRENZE` und `POSTFACH_FENSTER_S` kommen bereits
aus der Umgebung (`bot.py:6337/6338`) — Adams Wunsch nach mehr als fünf pro
Stunde ist schon heute per Umgebungseintrag erfüllbar.

## RANG 6 — Rang A des Entkernungs-Befunds

Acht sicherheitstragende Prüfzeilen, blind gemessen, unverändert offen. Katalog:
`befund-entkernung.md`. **Zwei tragfähige Bauformen, keine dritte:** Verhalten
ausführen, oder Abwesenheit über echte `ast.Call`-Knoten **samt Wert** des
Arguments. **Je Fix die Entkernungs-Gegenprobe fahren** — Schutz raus, rot sehen,
Schutz rein, `__pycache__` vorher löschen.

## RANG 7 — SDK/CLI-Update (nur wenn das Fenster trägt)

**Adams Entscheid vom 28.08.:** `anthropic` streichen (Rang 1), dann
**Agent-SDK 0.2.127 → 0.2.144 samt globaler CLI** im selben Zug. **Node 22 → 24
ausdrücklich NICHT** — eigener Termin, Adam muss dabei erreichbar sein.

**Auflagen:** eigener Arbeitsbaum **neben** dem Repo (nicht darunter — die Lehre
vom 25.08.), eigene virtuelle Umgebung, vollständiger Regressionslauf dort, erst
dann übernehmen, Pin nachziehen. **Bricht etwas: zurück und melden, nicht
reparieren** — Adam ist nicht erreichbar.

**`[NACHGETRAGEN 28.08., Adam]` Node 22 → 24 ist danach der NÄCHSTE Punkt** —
nicht „irgendwann", sondern der erste Vorgang, sobald Adam wieder am Rechner
ist. Was das für dieses Fenster bedeutet, steht in Rang 9.

## RANG 8 — Gegenleser vorbereiten, aber NICHT scharfstellen

**`2026-08-28_bauauftrag-gegenleser-drei-routen.md`** und
**`2026-08-28_konzept-gegenleser-ins-eigene-haus.md`**

**Der Auftrag ist gut und ich übernehme ihn — mit einer Streichung und drei
Setzungen.**

### Meine Streichung: der Vergleichstest bekommt KEINE eingebauten Mängel

Auftrag 5 sieht *„einen Bauauftrag mit drei absichtlich eingebauten Mängeln"* vor.
**Adam hat genau das am 27.08. um 19:22 Uhr abgelehnt**, und zwar als
Werte-Entscheidung:

> „Nein, diese Idee lehne ich ab. Das mit Fehlern zu machen, das ist alles
> manipulativ. … Wir versuchen uns ja positiv auszurichten und jetzt nicht zu
> manipulieren."

**Und Claudia hatte die täuschungsfreie Form selbst formuliert**, eine Minute
später: *„dieselbe echte Vorlage an beide, und wer etwas findet, hat etwas
gefunden. Kein eingebauter Fehler, keine Täuschung."*

**Ersatz, und er ist besser:** Prüfstein ist ein **echter Auftrag aus dem
Bestand** — es liegen sieben bereit. Gemessen wird, wer was findet und ob jemand
etwas findet, das die anderen übersehen. Das ist ohnehin der eigentliche Messwert,
und wir lernen zusätzlich etwas über unsere eigenen Aufträge.

*Warum das kein Detail ist: Adams Werte-Entscheidungen verfallen still, wenn sie
im nächsten Zusammenhang wiederkehren und niemand widerspricht. Vierzehn Stunden
zwischen Ablehnung und Wiederkehr.*

### Meine drei Setzungen zu Claudias offenen Punkten

1. **Grok auf Abruf statt automatisch — bestätigt.** Adams eigenes Wort, und die
   sparsamere Fehlerfläche.
2. **OVHcloud-Präferenzreihenfolge — bestätigt**, ich weiß es nicht besser. Der
   Rauchtest **vor** der Inbetriebnahme entscheidet ohnehin.
3. **Eingebaute Mängel — gestrichen**, siehe oben.

### Warum NICHT scharfstellen: Der Schlüssel ist Adams Sache

**Kein Schlüssel wird angelegt, keine Route in Betrieb genommen.** Ein Zugang zu
einem Bezahldienst ist Adams Handlung, nicht Micks. Baubar ist alles Übrige:
Verteiler-Einträge, Rauchtest-Gerüst, Prüfer gegen den stillen Fehlschlag,
Vergleichstest-Aufbau.

**💰 Ausgabenlimit: 30 € gesamt** — Adams Entscheid vom 28.08. Erwartete echte
Kosten liegen bei rund vierzig Cent bis zwei Euro; die 30 sind der Riegel gegen
Fehlläufe, kein Budget. **Das Limit wird beim Anbieter gesetzt, bevor der erste
Aufruf läuft** — nicht danach.

---

## RANG 9 — Node 22 → 24: Vorbereitung jetzt, Vollzug mit Adam

**Adams Ansage vom 28.08.:** Node ist **der nächste Punkt**, sobald er wieder am
Rechner ist. Nicht in dieses Fenster — aber die Vorbereitung gehört hinein,
damit der Vollzug dann in Minuten statt Stunden läuft.

**Warum Adam dabei sein muss, präzise:** Node trägt die **Claude-Code-CLI**.
Bricht sie, lebt der Bot weiter und **jeder Modell-Lauf scheitert** — Telegram
antwortet, die Arbeit nicht. Das ist ein Bruch, der wie Ruhe aussieht, und
genau davon hatten wir genug. Ein Rückbau braucht dann eine Hand am Rechner.

**Was JETZT ohne Risiko machbar ist — und was die Regel ohnehin verlangt**
(*„Der Ist-Stand vor einem Eingriff wird vollständig eingefroren"*):

1. **Den Ist-Stand messen und ablegen**, nicht erinnern: Node-Fassung, alle
   global installierten npm-Pakete mit Version, wo die Claude-Code-CLI
   tatsächlich herkommt (npm-Paket oder eigenes Programm), und welche Skripte
   Node überhaupt anfassen. **Auf dem VPS gemessen, nicht hier** — die
   Container-Lage ist nachweislich eine andere, und genau diese Divergenz hat
   uns am 25.08. einen blinden Prüfer beschert.
2. **Den Rückweg aufschreiben, bevor er gebraucht wird:** genauer Befehl, mit
   dem Node 22 wiederhergestellt wird, und woran man erkennt, dass es geklappt
   hat. Ein Rückweg, der erst im Fehlerfall erfunden wird, ist keiner.
3. **Den Probelauf im Klon fahren** — eigener Arbeitsbaum **neben** dem Repo,
   Node 24 dort, vollständiger Regressionslauf. Bricht etwas, wissen wir es
   vorher und ohne Schaden.

**Nicht machen:** die produktive Node-Fassung anfassen. Kein `nvm use` auf dem
laufenden System, kein globales Upgrade, kein npm-Paket neu installieren.

**Das Ergebnis der Vorbereitung ist ein Zettel, kein Zustand:** Ist-Stand,
Rückweg, Probelauf-Ergebnis. Damit dauert der Vollzug mit Adam eine Viertelstunde
statt eines Abends.

## Was ausdrücklich NICHT passiert

- **Node 22 → 24 wird JETZT nicht vollzogen** — aber vorbereitet, siehe Rang 9.
- **Kein Postfach wird hinterlegt**, auch kein Wegwerf-Konto. Unverändert.
- **Rang 2 der Erkennungsseite (MIME/BODYSTRUCTURE)** — bewusst zu, braucht R1.
- **Keine Route in Betrieb**, siehe Rang 8.

## Zum Umfang, ehrlich

**Das ist Rang 0 bis 9; ein Fünf-Stunden-Fenster reicht dafür nicht.** Die
Reihenfolge ist die Anweisung, nicht das Pensum. **Rang 0 bis 4 ist eine
realistische Erwartung für das erste Fenster** — mehr eine Orientierung als eine
Grenze.

### `[BERICHTIGT 28.08., Adam]` Es gibt hier keine Zeitnot — und deshalb wird nichts gekürzt

Ich hatte geschrieben, bei Zeitnot werde hinten gekürzt. **Das war falsch, und
Adams Korrektur trifft den Punkt:**

> „Wir haben ja nie Zeitnot, weil wenn die fünf schon voll sind, wird halt
> weitergebaut, wenn sie wieder offen sind. … Es ist nicht nötig zu kürzen,
> sondern einfach nur zu warten."

**Das Kontingent kommt zurück, die Liste läuft nicht davon.** Kürzen wäre nur
dann richtig, wenn eine Frist gegen uns liefe — hier läuft keine. Die
Kürzungs-Regel aus `CLAUDE.md` meint den Zuschnitt **innerhalb** einer Aufgabe,
nicht das Streichen von Punkten aus einer Liste; ich habe sie falsch angewandt.

**Also gilt:** Ist das Kontingent erschöpft, wird **gewartet** und an genau
derselben Stelle weitergemacht. Kein Punkt wird übersprungen, keiner
zusammengefasst, keiner „schnell noch" durchgezogen, weil das Fenster zugeht.

**Zwei Auflagen, damit das Warten sauber trägt** — sie stehen schon oben, hier
ist der Grund:

- **Jeder Punkt einzeln committet.** Dann ist der Wiedereinstieg eindeutig: Was
  committet ist, ist fertig; was nicht, wird neu begonnen. Ein halb gebauter,
  nicht committeter Punkt ist der einzige Zustand, der beim Warten schadet.
- **Ein Punkt, der nicht sauber grün wird, wird zurückgerollt, nicht
  durchgedrückt.** Adam ist nicht erreichbar; ein halb gebauter Zustand über
  Nacht ist schlechter als ein nicht gebauter. Das gilt unverändert — es ist
  keine Zeitfrage, sondern eine Qualitätsfrage.

**Gepfuscht wird ohnehin nicht** — das musste nie angeordnet werden.
