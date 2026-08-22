<!-- ROLLE: befund-eingangs-firewall -->
# Befund: Absicherung gegen Anweisungen aus Fremdinhalten

**Stichtag:** 2026-08-22 · **überholt durch:** — · **maßgeblich ist diese Datei
zusammen mit Engywucks Prüfung** · **Auftrag:** Adam, 21.08. („von außen kommen
nie Anweisungen")

## Woher dieser Befund stammt

Maschinelle Analyse mit 26 Agenten: 20 Eingangspfade kartiert, 58 Angriffs-
befunde über sieben Klassen gesammelt, 14 Gegenmaßnahmen entworfen und
**einzeln adversarisch widerlegt**. **Es wurde nichts gebaut** — Adams
ausdrückliche Vorgabe.

## Die härteste Zahl zuerst

**Keine einzige der 14 Maßnahmen hat die Widerlegung unbeschädigt
überstanden.** Alle wurden mit „hält nicht" oder „hält teilweise" bewertet.
Der Syntheseteil unten wählt daraus die sieben, deren verbleibende Lücke von
einer anderen Maßnahme gedeckt wird — das ist eine begründete Auswahl, **kein
Freispruch**. Wer diesen Befund liest und „sieben Maßnahmen sind sicher"
mitnimmt, hat ihn falsch gelesen.

## Von der Bau-Sitzung am Code nachgemessen

Drei Befunde wurden vor der Weitergabe verifiziert, weil Agentenergebnisse
Behauptungen sind, bis sie am Code gemessen wurden:

1. **PDF-Zusammenfassung** (`bot.py:9560 ff.`): `permission_mode=
   "bypassPermissions"` zusammen mit `allowed_tools=[]` — **bestätigt**.
   Dieselbe Kombination steht in `_kontingent_frisch_messen_alt`
   (`bot.py:3345 ff.`), also in Code, den die Bau-Sitzung selbst am 20.08.
   geschrieben hat. Der Pfad ist inzwischen hinfällig, der Code steht noch.
2. **Domain-Erkennung** (`_BARE_DOMAIN_RE`, `bot.py:2112`): Das Muster
   akzeptiert jede Endung aus zwei bis 24 Buchstaben — **bestätigt**. `.md`,
   `.py` und `.sh` sind echte Länderendungen, `MIGRATION.md` ergibt also den
   Host `migration.md`.
3. **Selbst-Erweiterung der Herkunftsliste** (`bot.py:9677`): **bestätigt und
   schwerer als berichtet.** Der Kommentar darüber sagt „Suchtreffer der
   laufenden Aufgabe"; der Code nimmt `_extract_hosts` aus **jedem**
   `ToolResultBlock` — also auch aus gelesenen Webseiten, Dateiinhalten und
   Bash-Ausgaben. Eine gelesene Seite kann sich damit den nächsten Abruf
   selbst freischalten.

### Nachtrag 22.08. — der Kalender ist ebenfalls ein Fremdeingang (Adams Frage)

Adam hat gefragt, ob **abonnierte** Kalender unter dieselbe Regel fallen. Sie
tun es, und die Messung zeigt eine Nuance, die schwerer wiegt als die Frage:

**`kalender.py` liest genau EINE Sammlung — aber es ist nicht festgelegt,
welche.** `/termine` ruft `termine_lesen()` ohne Kalendernamen;
`_kalender_waehlen` nimmt dann `sammlungen[0]` (Zeile 179), also die erste
Sammlung, die der Server liefert. **Die Reihenfolge bestimmt iCloud, nicht
wir.** Steht ein abonnierter Kalender vorn, wird genau der gelesen.

Titel, Ort und Notiz landen im Modellkontext (`Termin.lesbar()`). Ein
Kalendereintrag ist dabei **unauffälliger als eine Mail**: Niemand liest einen
Termintitel als Text, der etwas bewirken könnte.

**Ausdrücklich UNGEPRÜFT:** ob iCloud abonnierte Kalender über CalDAV
überhaupt anbietet — ICS-Abos liegen bei Apple teilweise nur lokal auf den
Geräten. Das ist vor einer Entscheidung zu messen, nicht anzunehmen.

**Vorgeschlagenes Vorgehen ohne Bau:** Zugang freischalten, dann einmal
`sammlungen_auflisten()` abfragen (reine Lesung). Stehen dort nur eigene
Kalender, ist `/termine` unkritisch. Steht Fremdes dabei, gehört ein FESTER
Kalendername in die Konfiguration statt „der erste, der kommt" — eine Zeile,
die mit dem Sicherheitsbau kommt, nicht davor.

**Für Engywuck:** Bitte die acht Fragen auch auf diesen Pfad anwenden. Er ist
im Bericht unter den 20 Eingangspfaden erfasst, aber die Unbestimmtheit der
Sammlungswahl steht dort nicht.

---

# Unsichtbare Anweisungen: was sich absichern lässt und was nicht

## 1. Die kurze Antwort

Nein — kategorisch absichern lässt sich das nicht, solange der Bot fremde Inhalte lesen soll. Aber die Grenze verläuft nicht dort, wo man sie vermutet, und sie ist schärfer, als das „nein" klingt.

Kategorisch absicherbar ist die **Handlungsseite**: dass aus einem fremden Text ohne deinen Daumen eine Handlung folgt — ein Befehl, ein Abruf nach außen, ein Schreibzugriff — lässt sich mit deterministischen Riegeln ausschließen. Nicht mit Filtern, die im Text nach Anweisungen suchen (die verlieren dieses Rennen immer), sondern mit Schranken an den Werkzeugen selbst.

Nicht absicherbar ist die **Redeseite**: Was in der Antwort steht, die du liest oder vorgelesen bekommst, kann ein fremder Text färben. Eine Zusammenfassung, die eine Zahl verdreht. Ein Link in der Antwort, den du anklickst. Ein Befehlsblock, den du ins Terminal kopierst. Dort endet jede technische Sicherheit, weil der Weg nach draußen dann durch dich führt und nicht durch die Maschine.

Die ehrliche Formel lautet also: **kein Schaden ohne deinen Daumen — und jeder Daumen mit ehrlicher Anzeige.** Das ist erreichbar. „Hundertprozentig sicher" wäre nur ein System, das fremde Inhalte gar nicht liest — und das wäre ein System ohne den Nutzen, für den wir es bauen.

## 2. Die drei gefährlichsten Befunde

**Erstens: Die PDF-Zusammenfassung hat keine Bremse.** Wenn du ein PDF schickst und „zusammenfassen" drückst, startet der Bot dafür einen eigenen, zweiten Arbeitsgang. In dessen Einstellung steht „keine Rückfragen" und „keine Werkzeuge" — aber das zweite ist ein Irrtum im Bau: eine leere Werkzeugliste wird vom darunterliegenden System als „nichts eingeschränkt" gelesen, nicht als „nichts erlaubt". Es geht also der volle Werkzeugsatz hinein, bei abgeschalteter Rückfrage, und gefüttert wird dieser Arbeitsgang zu hundert Prozent mit dem Text des fremden Dokuments — einschließlich Text, den du im PDF gar nicht sehen kannst, weil er weiß auf weiß oder in Schriftgröße null gesetzt ist. *Konkret könnte passieren:* Ein PDF, das du zur Zusammenfassung schickst, liest im Hintergrund eine Datei aus deinem Rechner und schickt sie in einer Web-Adresse nach draußen, während du eine unauffällige Zusammenfassung angezeigt bekommst.

**Zweitens: Die Schranke für Web-Abrufe öffnet sich selbst.** Der Bot darf eine Web-Adresse nur ohne Rückfrage abrufen, wenn sie aus deiner Nachricht oder aus Suchtreffern stammt — so steht es im Kommentar im Code. Gebaut ist etwas anderes: **jedes** Werkzeug-Ergebnis erweitert diese Liste, auch der Inhalt einer bereits gelesenen Seite. Eine Seite kann also in ihrem Text weitere Adressen nennen und sich damit den nächsten Abruf selbst freischalten. Verschärfend kommt hinzu, dass die Erkennung auch bloße Wortpaare als Adressen liest: `MIGRATION.md`, `bot.py`, `guardian.sh` gelten als Domains, weil `.md`, `.py` und `.sh` echte Länderkürzel sind. Da wir diese Dateinamen in praktisch jeder Nachricht nennen, steht „migration.md" dauerhaft auf der Freigabeliste. *Konkret könnte passieren:* Wer diese Domain registriert, bekommt einen stillen, unbegrenzten Kanal, über den der Bot ohne jede Rückfrage abruft — und in der Adresse lassen sich Daten mitschicken.

**Drittens: Fremder Text wird dauerhaft zu deinem Wort.** Angepinnte Nachrichten wandern ungeprüft und ohne Herkunftsvermerk ins Dauergedächtnis und von dort in die Projekt-Anweisungsdatei, die bei jedem Start mit erhöhter Verbindlichkeit gelesen wird. Zusätzlich wird das Gesprächsprotokoll zwei Tage lang in den Startkontext jeder neuen Sitzung gespiegelt, überschrieben mit „Dies ist der jüngste Dialog mit Adam" — und die Kopfzeilen darin (`## Du ·`) sind einfacher Text, den jeder Inhalt mitschreiben kann. *Konkret könnte passieren:* Eine einmal eingeschleuste Anweisung überlebt Neustart, Zurücksetzen und Sitzungswechsel und wird bei jedem Start neu eingespielt — als hättest du sie selbst geschrieben. Das ist die haltbarste Form des Angriffs im ganzen System, und sie ist zugleich die unauffälligste.

Ein vierter Punkt gehört als Randnotiz dazu, weil er nichts mit unsichtbarem Text zu tun hat und trotzdem offen steht: Wer den Bot irgendwo als Kanal-Verwalter einträgt, biegt damit ohne Absenderprüfung den Ausgabekanal für Zusammenfassungen, Dateien und Sprachausgabe auf seinen eigenen Kanal um. Das ist kein Einschleusen, das ist der Rückweg — und es ist ein Dreizeiler zu beheben.

## 3. Die kleinste Kette, die trägt

Ich nenne sie in Baureihenfolge; jede einzelne ist billig, prüfbar und im Alltag nicht spürbar. Das ist Absicht: Von den zwölf durchgerechneten Vorschlägen haben genau diese die Widerlegung überstanden.

**① Absenderprüfung beim Kanal-Eintrag** — *kategorisch.* Nur deine Kennung darf einen Ausgabekanal setzen. Kein Modell beteiligt, kein Klickpreis, keine Nebenwirkung.

**② Der zweite Arbeitsgang bekommt eine echte Werkzeug-Sperre** — *kategorisch für diesen Pfad.* Wichtig sind zwei Details, die der Prüflauf zutage gefördert hat: Es muss eine **Positivliste** sein (eine Liste des Verbotenen altert gegen jedes neue Werkzeug), und die Sperre darf nicht am Freigabe-Rückruf hängen, weil dieser bei abgeschalteten Rückfragen bauartbedingt nie aufgerufen wird. Das schließt den kürzesten Weg von außen nach außen. Es schließt *nicht* den Weg über die Hauptsitzung — den decken ③ und ④.

**③ Die Herkunftsliste für Web-Abrufe wird verengt** — *kategorisch gegen die Selbstfreischaltung, heuristisch gegenüber der Adresse selbst.* Sie darf nur noch aus deiner Nachricht und aus Suchtreffern gespeist werden, nicht mehr aus dem Inhalt gelesener Seiten und Dateien. Dazu zwei Ergänzungen, ohne die es nicht trägt: eine Prüfung gegen die echten Länderkürzel, damit Dateinamen keine Domains mehr sind, und eine Prüfung der **vollständigen** Adresse statt nur des Namensteils — heute lässt sich an jede vertraute Adresse ein beliebiger Datenanhang hängen.

**④ Das Suchwerkzeug wandert hinter die Geheimnis-Prüfung** — *kategorisch, kostenlos.* Heute steht seine bedingungslose Freigabe als allererste Regel, noch vor jeder Prüfung. Eine Suchanfrage ist ein freier Kanal nach draußen; sie muss dieselben Prüfungen durchlaufen wie alles andere. (Die zusätzlich vorgeschlagene Längen- und Zeichengrenze ist gefallen — sie sperrt normale deutsche Fragen und lässt einen Zugangsschlüssel unverändert durch.)

**⑤ Der Rückweg vom Protokoll in den Systemrang wird gekappt** — *kategorisch.* Der eingespielte Gesprächsverlauf darf nicht mehr als „Dialog mit Adam" eingeleitet werden, die Kopfzeilen im geschriebenen Protokoll werden entwertet, und angepinnte Texte bekommen einen Herkunftsvermerk statt roher Übernahme in die Anweisungsdatei. Das ist der Punkt, an dem aus einmaligem Fremdtext dauerhafte Autorität wird — und der einzige, der Neustarts überlebt.

**⑥ Die Lücke in der Geheimnis-Sperre schließen** — *heuristisch, aber gemessen.* Die Sperre prüft Zeichenketten im Befehl; Platzhalter wie `.e*` oder `.[e]nv` laufen daran vorbei und werden ohne Rückfrage ausgeführt. Die fehlenden Zeichen gehören in die Prüfung. Ebenso: das Auslesen der Prozessumgebung trägt keinen einzigen der geprüften Marker und gilt deshalb heute als harmlos.

**⑦ Link-Vorschau abschalten — aber auf der richtigen Ebene** — *kategorisch für Textwege.* Nicht an einer einzelnen Sendefunktion (das deckt eine von rund hundertsechzig Stellen), sondern als Voreinstellung am Programm selbst. Und die eigentliche Wunde liegt daneben: Im Freigabedialog steht der vollständige Befehl samt Adresse, und die Nachricht geht hinaus, **bevor** du sie siehst — der Abruf ist also schon passiert, wenn du „ablehnen" drückst.

Zu jeder dieser sieben gehört ein Prüfer, der sie **ausführt** statt sie zu lesen. Das ist keine Formalie: In diesem Projekt haben Prüfer, die nur nach Textstellen suchten, schon zweimal einen schweren Fehler zugleich erzeugt und gedeckt.

## 4. Was auch danach offen bleibt

Die Antwort selbst bleibt beeinflussbar. Wenn du ein Dokument zusammenfassen lässt, kann das Dokument die Zusammenfassung färben — eine verdrehte Zahl, ein weggelassener Punkt, ein Rat, der nicht deiner ist. Dagegen hilft keine Schranke, weil genau das die bestellte Leistung ist.

Du bleibst der letzte Riegel, und zwar an der ungünstigsten Stelle. Der Weg über kopierte Befehlsblöcke ins Terminal ist in diesem Projekt Alltag und hat weder Dialog noch Spur. Ein angeklickter Link führt über dein Gerät und deine Anmeldungen. Und jede Maßnahme, die Klicks erzeugt, macht diesen Riegel schwächer statt stärker — das ist der Grund, warum die Kette oben ohne einen einzigen zusätzlichen Klick auskommt.

Die erlaubten Ausgänge tragen Daten. Telegram selbst, der stündliche Abgleich der Protokolle nach GitHub, die Suche — über jeden davon können Inhalte hinausgehen, ohne dass ein Werkzeug auffällig würde. Eine Netzsperre um den Arbeitsprozess herum verschiebt den Abfluss auf genau diese Kanäle und macht ihn dabei **schwerer erkennbar**, weil er dann wie normaler Betrieb aussieht.

Der Zeitversatz bleibt. Der Gesprächsfaden überlebt den einzelnen Zug bewusst — deshalb ist jede Sperre, die „nur für diesen Zug" gilt, mit einer Nachricht Verzögerung umgehbar.

Und der Unterschied zwischen Mac und Server bleibt eine Blindstelle: Was nur auf dem Server gilt, existiert am Mac nicht — dieselbe Art von Divergenz, die den Tagescheck einundzwanzig Tage lang unbemerkt tot liegen ließ.

Zum E-Mail-Punkt, weil er ansteht: Der Nachrichtentext von Mails erreicht heute weder das Modell noch den Chat — es werden ausschließlich Kopfzeilen gelesen. Der gefährlichste Träger dieser ganzen Angriffsklasse, die HTML-Mail mit unsichtbarem Vorschautext, existiert also noch gar nicht. Sobald Punkt 9.5 den Nachrichtentext nachreicht, entsteht er neu — und trifft dann gebündelt auf alle Befunde oben. Das Hinterlegen von Postfächern ist deshalb keine Kleinigkeit, sondern eine bewusste Erweiterung der Angriffsfläche, die nach ①–⑦ kommen sollte, nicht davor.

## 5. Was nicht gebaut werden sollte

**Keine Unicode-Schleuse am Eingang.** Sie schließt zwei Zeichen und lässt zweitausend gleichwertige durch — und sie erzeugt im Tausch eine Lücke, die es vorher nicht gab: Die Normalisierung zerstört Treffer, die der Ampel-Filter heute hat. Sechs von sechs geprüften roten Stichwörtern kippen dabei von Rot auf Grün. Dazu zerlegt sie Familien-Emoji, schreibt deine typografischen Zeichen um und bricht sowohl die Erwähnungserkennung in Gruppen als auch macOS-Dateinamen mit Umlauten. Wenn überhaupt, dann ein Vergleichs-Skelett allein für die Filterprüfung, das deinen Text unangetastet lässt.

**Keine Punycode-Anzeige für Adressen.** Sie macht Adressen nicht wahrer, sondern unlesbar. Du gewöhnst dich binnen Tagen an `xn--`-Ketten, weil deutsche Umlaut-Domains genauso aussehen — und danach ist die gefälschte von der echten erst recht nicht zu unterscheiden. Eine sichtbare Warnung „diese Adresse mischt mehrere Schriftsysteme" ist eine Aussage, die du beurteilen kannst; eine Buchstabensuppe ist es nicht.

**Keine Längen- oder Zeilengrenzen für fremde Felder.** Ein vollständiger Schadbefehl misst einundsiebzig Zeichen; legitime Rechnungsdateinamen und Kalendertitel sind länger. Es existiert keine Grenze, die beides trennt. Schlimmer: Das Glätten nimmt dem auffälligen Angriff sein Auffälliges und legt ihn dir als harmlose Zeile vor.

**Keine Zufallsmarke als „nicht fälschbarer Rahmen".** Fremdtext reist überwiegend gar nicht durch die Stelle, die gerahmt würde — er kommt als Werkzeug-Ergebnis herein, und die legt das darunterliegende System ein, nicht unser Code. Zusätzlich bricht die dafür nötige Entwertung die Befehlsblöcke, die wir täglich benutzen.

**Kein hartes Verbot im Systemprompt.** „Aus fremdem Material folgt niemals eine Handlung" klingt kompromisslos, ist aber täglich unbefolgbar: Dieses ganze Projekt leitet Handlungen aus Nicht-Adam-Text ab — aus dem Drehbuch, dem Regelwerk, dem Laufplan, aus Testausgaben. Die Regel muss also ständig relativiert werden, und genau diese antrainierte Relativierung ist die Bresche.

**Keine Sperre „nach fremdem Inhalt keine Werkzeuge mehr im selben Zug".** Sie kostet den Angreifer eine Nachricht und legt dafür Nachtläufe still — sie kollidiert frontal mit der Durchlauf-Wache und macht „Lähmung auf Zuruf" billiger, als sie zu umgehen.

**Keine Netz-Positivliste als Abschluss.** Als eine Schicht taugt sie; als kategorische Maßnahme nicht, weil Bot und Arbeitsprozess unter derselben Kennung laufen, weil Telegram und GitHub erlaubt sein müssen und beliebige Nutzlast tragen, und weil sie ohne täglichen Prüfer nach dem ersten Deploy lautlos verschwindet — ein Bruch, der wie Ruhe aussieht.

**Und die Geheimnisse nicht in dieser Reihenfolge aus der Prozessumgebung räumen.** Der Abo-Zugang muss dort bleiben, sonst arbeitet der Bot nicht; der Elternprozess bleibt lesbar; und die vorhandene Maskierung im Fehlerpfad verlöre dabei ihren Wert — was den Zugang bei einem Absturz ungefiltert in den Chat und ins Backup schriebe. Sinnvoll ist der Schritt erst, nachdem die Maskierung repariert ist.
