# Bauauftrag: Ein Ausgang für alles, was an Adam geht

**Zustand: gültig** · verfasst 24.09.2026 · Claudia → Engywuck → Mick
**Erweitert:** `2026-09-23_bauauftrag-telegram-darstellung.md` — dessen Auftrag 3
(Geltungsbereich) wird durch Auftrag C dieses Zettels **ersetzt**. Aufträge 1, 2
und 4 von gestern bleiben gültig und sind hier eingearbeitet.

**Fassung 3 vom 24.09.2026, 07:20 Uhr** — Adams Entscheid zur Zielform in
Auftrag B; dazu zwei neue Aufträge (F: das volle Ausdrucksmittel-Repertoire,
G: der Text fürs Auge bei eingeschalteter Sprachausgabe) und ein Abschnitt über
die belegten Grenzen von Telegram.

**Anlass:** Adam am 24.09.2026, 06:17 Uhr — die Aufwertung solle „für den
gesamten Text hier gelten, für den gesamten Auftritt hier gelten. Nicht bloß für
ausgewählte Meldungen oder Videoanalysen." Freigabe zum Bauen um 06:46 Uhr.

---

## Der Befund: der Auftritt ist ein Flickenteppich, und zwar zählbar

Im Quelltext gezählt am 24.09.2026, `bot.py`:

| Darstellungsform | Stellen |
|---|---|
| `ParseMode.MARKDOWN` (die alte, abgekündigte Fassung) | 14 |
| die Zeichenkette `"Markdown"` (dasselbe, anders geschrieben) | 3 |
| `ParseMode.HTML` | 8 |
| ausdrücklich `parse_mode=None` | 6 |
| **ohne jede Angabe** — darunter der Hauptantwortweg | alle übrigen |

Dazu **35 Aufrufe** des Sammelsenders `send_chunked` und **27 direkte**
`send_message`-Aufrufe. Jede dieser Stellen wurde einmal für sich entschieden.

**Berichtigung zu meiner Auskunft im Chat um 06:44 Uhr:** Dort nannte ich
14 HTML-Stellen und 15 Markdown-Stellen. Richtig ist 8 zu 17; die Zählung oben
ist die gemessene. Am Befund ändert das nichts.

**Das ist die Ursache und nicht das Symptom.** Eine Form, die an 62 Stellen
einzeln eingetragen wird, ist nach dem nächsten Umbau wieder ungleich. Deshalb
steht hier der gemeinsame Durchgang vor der Formatfrage.

## Auftrag A — ein Ausgang, durch den jeder Text an Adam läuft

Eine Stelle, die **alles** Ausgehende passiert: Umwandlung, Rückfallweg,
Sprachausgabe, Protokoll. Die bestehenden Aufrufe rufen künftig diesen Durchgang,
nicht mehr Telegram unmittelbar.

**Warum das der eigentliche Auftrag ist:** Danach gilt jede künftige Regel zur
Form automatisch überall, und eine neu gebaute Meldung kann den Auftritt nicht
mehr verfehlen. Ohne diesen Schritt erzeugt die Reparatur den nächsten
Flickenteppich.

**Dieser Ausgang ist seit Juni von zwei Seiten gewünscht.** Der zweite Wunsch
kommt von der Sprachausgabe: Startmeldungen wurden nicht vorgelesen, obwohl die
Sprachausgabe eingeschaltet war, weil sie an `process_user_text` vorbei senden.
Es ist derselbe Umbau. Er wird einmal gemacht und erfüllt beide.

## Auftrag B — Zielform: Telegram-HTML

### `[ENTSCHEID Adam, 24.09.2026, 07:03]` HTML ist gesetzt

Adam auf die Vorlage: **„Okay, dann HTML."** Die Wahl der Zielform ist damit
entschieden und steht nicht mehr zur Abwägung. Was zu prüfen bleibt, ist allein
die Umsetzung — der Aufruf des Pakets und sein Verhalten im Betrieb.

**Adams Rückfrage um 07:07 Uhr und die Antwort darauf**, weil sie den Entscheid
trägt: Er wünscht „das, was mehr bietet" und vermutet, Markdown sei die
weiterentwickelte Fassung.

**Gemessen an zwei unabhängigen Stellen: Die beiden modernen Formen bieten
dasselbe.** MarkdownV2 und HTML beherrschen denselben Satz an Auszeichnungen —
fett, kursiv, unterstrichen, durchgestrichen, verdeckt, Verweis, Erwähnung,
eigenes Emoji, Code, Codeblock mit Sprachangabe, Zitatblock und aufklappbarer
Zitatblock. Die Wahl begrenzt also **nichts**; sie entscheidet allein darüber,
wie oft eine Nachricht an der Auszeichnung zerbricht — drei zu entschärfende
Zeichen gegen achtzehn.

**Adams Vermutung stimmt, sie trifft nur ein anderes Paar.** Das Veraltete ist
das **alte Markdown**, das an 17 Stellen in `bot.py` steht: Es kann kein
Unterstreichen, kein Durchstreichen, kein Verdecken, keine Zitatblöcke und keine
Verschachtelung, und es gilt als abgekündigt. Genau das fliegt hier raus.

**Und die Schreibform bleibt Markdown.** Ich schreibe weiter Markdown; das Paket
setzt es für den Transport nach HTML um. Markdown als Autorenformat ist von
dieser Entscheidung nicht berührt.

**Ein Widerspruch zwischen den Quellen, benannt statt geglättet:** Eine Seite
behauptet, HTML könne in Telegram kein Unterstreichen und kein Verdecken. Die
amtlichen Auszeichnungen dafür existieren (`<u>`, `<tg-spoiler>`), und die
übrigen Quellen führen beide als unterstützt. Ich halte die Behauptung für
falsch — **belegt wird sie beim Bau durch einen echten Sendeversuch**, nicht
durch Nachlesen.

**Abweichung vom Zettel von gestern, mit Begründung.** Dort stand MarkdownV2 als
Ziel. Telegram-HTML ist die robustere Wahl:

- **Die Bruchfläche ist kleiner.** In HTML müssen drei Zeichen entschärft werden
  (`&`, `<`, `>`), in MarkdownV2 achtzehn. Jedes nicht entschärfte Zeichen ist
  eine vollständig abgelehnte Nachricht.
- **Adams Ablage lebt in den Texten.** Dateinamen mit Unterstrich, Ordner mit
  `&`, Titel mit Klammern — in MarkdownV2 ist jedes davon ein Stolperstein, in
  HTML nur das `&`.
- **Es ist bereits die verbreitetere Form im eigenen Bestand** (8 Stellen gegen
  14 mit der abgekündigten alten Markdown-Fassung).

**Das Paket kann beides.** Laut [Projektseite von
telegramify-markdown](https://github.com/sudoskys/telegramify-markdown) liefert
`richify(markdown, mode="html")` Telegram-HTML für Absätze, Überschriften,
Auszeichnungen, Verweise, Listen, Zitate, Tabellen und Code; MIT-Lizenz, Fassung
1.0.0, aufgebaut auf `pyromark`. **Vor dem Einbau am Paket selbst nachmessen** —
diese Angaben stammen von der Projektseite, nicht aus einem eigenen Lauf.

**Nebenbefund, der Auftrag A betrifft:** Dasselbe Paket bringt
`telegramify_rich()` mit, das lange Texte selbst in sendbare Stücke teilt. Beim
Bau von Auftrag A prüfen, ob das unser `send_chunked` samt `_find_safe_cut`
ersetzt oder ergänzt. Eigene Trennlogik neben einer fertigen wäre genau die
Doppelung, gegen die die Suchregel steht — **die Überschriften-Regel darf dabei
nicht verloren gehen** (eine Überschrift steht nie am Nachrichtenende).

## Auftrag C — Geltungsbereich: alles, was Adam erreicht

Ersetzt Auftrag 3 von gestern. Eingeschlossen sind:

- der Antwortweg und die Bildunterschrift der Sprachnachricht,
- **alle** Befehlsausgaben (`/zimmer`, `/status`, Menüs, Schalterstände),
- Start-, Neustart- und Bestätigungsmeldungen,
- Freigabe- und Genehmigungsanfragen,
- die Meldungen des Tageschecks, der Wachposten und der Stundenblume,
- der Versand über das Botenpostfach.

**Die Vorsicht von gestern entfällt, und zwar begründet:** Auftrag 3 nahm
`/zimmer` und `/status` aus, weil dort Namen aus Adams Ablage stehen. Genau das
erledigt die Umwandlung — sie entschärft die Sonderzeichen. Zusammen mit dem
Rückfallweg ist der weite Geltungsbereich sicherer als die Ausnahmeliste, denn
eine Ausnahmeliste wächst nie mit.

**Zwei Grenzen bleiben, ausdrücklich:**

1. **Code-Blöcke und wörtliche Zitate** behalten ihren Inhalt unverändert. Was
   Adam kopieren soll, muss kopierbar bleiben — eine eigene Nachricht ohne
   Rahmentext, und darin nichts Entschärftes, was beim Einfügen falsch wäre.
2. **Die Sprachausgabe arbeitet auf dem Rohtext**, vor der Umwandlung. Läuft die
   Reihenfolge verkehrt, liest die Stimme Schrägstriche und spitze Klammern vor.

## Auftrag D — Rückfallweg (unverändert aus Auftrag 2 von gestern)

Sendeversuch mit Auszeichnung. Lehnt Telegram wegen der Auszeichnung ab:
**denselben Text sofort ohne Auszeichnung erneut senden** und den Vorfall
protokollieren. Der schlechteste Fall ist danach der heutige Normalzustand, nie
eine verschwundene Nachricht.

Bei einem Geltungsbereich über alle Sendestellen ist dieser Auftrag keine Zierde,
sondern die Bedingung, unter der Auftrag C überhaupt vertretbar ist.

## Auftrag E — Selbsttest im 4-Uhr-Check

Ein Text mit Fettdruck, Kursivsatz, Verweis am sprechenden Wort, Überschrift,
Tabelle, Unterstrich in einem Dateinamen, einem `&` in einem Ordnernamen und
einem einzelnen Stern läuft durch den Ausgang und wird von Telegram angenommen.
Zusätzlich: Die Sprachausgabe desselben Textes enthält keine Auszeichnungszeichen.

## Auftrag F — das Ausdrucksmittel ausschöpfen, ohne zu übertreiben

**Anlass:** Adam am 24.09.2026, 07:07 Uhr — der Auftritt solle „in frischem
Gewand" kommen, „möglichst vielseitig, möglichst optisch hochwertig, möglichst
kompatibel", und die Möglichkeiten sollen „weitestgehend ausgeschöpft" werden.
Zugleich seine Grenze: **„Wir müssen das nun nie übertreiben, weil grundsätzlich
reicht für einen Chat und einen Messenger ja auch die ganz normale Optik."**

Nach dem Umbau stehen zur Verfügung und sollen genutzt werden:

| Mittel | Wofür |
|---|---|
| **Fett** | die Aussage, und als Ersatz für Überschriften |
| *Kursiv* | Werktitel, Zitate, Betonung |
| Verweis am sprechenden Wort | Quellen, ohne nackte Adressen im Text |
| Zitatblock | fremde Aussagen, Fundstellen |
| **Aufklappbarer Zitatblock** | lange Belege und Anhänge, die den Lesefluss sonst erschlagen |
| Codeblock mit Sprachangabe | Befehle und alles, was Adam kopieren soll |
| Durchgestrichen | Überholtes, das sichtbar bleiben soll |

**Der aufklappbare Zitatblock ist der größte Gewinn** für unsere Lage: Lange
Antworten mit Belegteil lassen sich damit kurz halten, ohne etwas wegzulassen.

**Das Maß gibt die Vorlage.** Auf den Bildschirmfotos vom 23.09. arbeitet die
Vergleichs-Assistentin mit sehr wenig: Fettdruck für Zwischenüberschriften,
Kursivsatz für Buchtitel, Leerzeilen zwischen Absätzen, Verweise auf dem Wort.
Kein Schmuck. Genau diese Zurückhaltung ist das Ziel.

### Was Telegram nicht kann — damit es niemand sucht

Am 24.09. nachgelesen: **Telegram kennt keine Überschriften, keine Tabellen und
keine Schriftwahl.** Der Text erscheint in der Schrift, die der Empfänger in
seinen Einstellungen führt; eine Nachricht kann daran nichts ändern. Die einzige
abweichende Schrift ist die feste Breite in Code und Codeblock.

**Folge für Adams Wunsch nach einem moderneren Schriftbild:** Was erreichbar ist,
liegt in Rhythmus und Gliederung — Absätze, Einzug, Zitatblöcke, sparsamer
Fettdruck —, nicht in der Schriftart. Er hat die Schriftart ausdrücklich als
nicht zwingend bezeichnet.

**Tabellen** bildet das Umwandlungspaket auf eine Ersatzform ab. Beim Bau ansehen,
wie das Ergebnis auf dem Telefon aussieht; im Zweifel schreibe ich Tabellen
künftig als kurze Aufzählungen.

## Auftrag G — bei eingeschalteter Sprachausgabe gilt derselbe Maßstab fürs Auge

**Anlass:** Adams Beobachtung vom 24.09.2026, 07:07 Uhr — mit eingeschalteter
Sprachausgabe sehe der Text schlechter aus als ohne. **Die Beobachtung stimmt,
und die Ursache ist gefunden.**

`bot.py` Zeile 15493: Bei eingeschalteter Sprachausgabe geht der sichtbare Text
als **Bildunterschrift der Sprachnachricht** mit — `caption=chunk[:1024]`. Der
Schnitt kommt aus `TTS_SYNC_CHUNK` (Zeile 709, ebenfalls 1024) und ist **für das
Ohr bemessen, nicht für das Auge**: Er trennt nach etwa tausend Zeichen an der
nächstbesten Stelle, notfalls an einem Komma. Eine lange Antwort zerfällt so in
mehrere Bildunterschriften, deren Absatzbau dem Sprechtakt folgt.

**Zu tun:** Die beiden Schnitte entkoppeln. Der **Text** wird nach den Leseregeln
geteilt — an Absätzen, mit dem Schutz, dass eine Überschrift nie am Ende einer
Nachricht steht. Die **Sprachausgabe** teilt unabhängig davon nach Sprechlänge.

**Gegengeprüft:** Ein stiller Verlust entsteht heute nicht, weil das Teilstück
nie über tausend Zeichen hinausgeht. Wird der Textschnitt entkoppelt, **kann** er
die Grenze der Bildunterschrift überschreiten — dann muss der Text als eigene
Nachricht zur Sprachnachricht gehen, statt am Ende abgeschnitten zu werden.

**Adams Ausblick dazu, als Merker und nicht als Auftrag:** Er will mittelfristig
in Richtung eines flüssigen Sprachdialogs, wie große Anbieter ihn zeigen, und
weiß, dass wir dort nicht gleichziehen. Der nächste greifbare Schritt bleibt der
geplante Wechsel der Sprachausgabe mit echter Sprachumschaltung.

## Was kann brechen und wer merkt es

| Bruch | Wer merkt es |
|---|---|
| Umwandlung erzeugt ungültige Auszeichnung → Telegram lehnt ab | Rückfallweg (Auftrag D) und Protokoll. Ohne ihn: niemand, die Antwort verschwände spurlos |
| Ein Aufruf wird beim Umbau übersehen und sendet weiter unmittelbar | **Heute niemand.** Deshalb Pflicht: ein Prüfer, der zählt, dass kein `send_message`/`send_chunked` an diesem Ausgang vorbeiführt |
| Reihenfolge Umwandlung/Sprachausgabe verkehrt | Selbsttest (Auftrag E), sonst hört Adam Zeichensalat |
| Trennung langer Texte zerreißt ein Auszeichnungspaar | Selbsttest mit einem Text über der Längengrenze |
| Kopierbare Blöcke werden entschärft und sind beim Einfügen falsch | **Adam beim Einfügen — also zu spät.** Prüffall in den Selbsttest |
| Paket bricht bei einer neuen Fassung | Selbsttest |

## Reichweite über diesen Auftrag hinaus

Was hier entsteht, ist der Ort für alles, was künftig „für jede Nachricht" gelten
soll. Drei Vorhaben, die heute einzeln geführt werden, gehören danach an diese
eine Stelle und sind dort kein eigener Bau mehr: die Zahlen- und
Uhrzeitbehandlung der Sprachausgabe, die Regel gegen Überschriften am
Nachrichtenende, und die Einstufung, welche Meldung Adam überhaupt erreicht.

**Empfehlung für die Reihenfolge:** Auftrag A zuerst und allein abnehmen, danach
B bis E. Der Ausgang ist der Umbau, alles Weitere ist dann eine Zeile an einer
Stelle.
