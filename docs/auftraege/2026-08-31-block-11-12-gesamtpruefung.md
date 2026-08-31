> **Zweck: ANSICHT** · **Zu tun:** lesen. Die Bauaufträge daraus liegen separat.
> Nicht an Mick weitergeben — dafür gibt es das Auftragspapier.

# Blöcke 11 und 12 von 18 — 27.07. mittags bis 28.07. nachts

**Stichtag:** 31.08.2026, 22:56 MESZ (Systemuhr abgelesen; Container läuft auf UTC)
**Gelesen:** 36 Nachrichten · **Kandidaten:** 20 · **Lücken:** 6 · **gedeckt:** 6
· **nicht prüfbar:** 1

Diese beiden Blöcke sind Adams **letzter Tag vor der Abreise**. Er packt,
repariert, fährt Wäsche — und gibt dabei sechs Regeln, von denen keine
angekommen ist. **Bemerkenswert ist aber das Gegenteil:** In denselben Blöcken
sind **sechs Wünsche exakt so gebaut worden, wie er sie gesagt hat.** Das ist
die höchste Trefferquote bisher.

---

## Zuerst das, was gebaut wurde — weil es die Ausnahme erklärt

| Sein Wunsch | Stand |
|---|---|
| **Gründlich-Taster als An/Aus mit Haken** (27.07., 11:35 — *„ich kann ihn nicht mehr ausschalten"*) | ✅ **Gebaut.** `bot.py:9637` schaltet um statt vorzumerken, `🎯 Gründlich ✓` zeigt den Zustand. Der Code-Kommentar nennt sogar die Falle, die dabei umgangen wurde |
| **Emojis: Lotus für die Stundenblume, Uhr für Hora, Hibiskus für die Entwarnung** (28.07., 10:15, nach zwei Korrekturen) | ✅ **Gebaut, genau so.** `stundenblume.py:699` trägt den Kommentar *„🪷 Lotus für den neuen Befund, 🌺 Hibiskus für die Entwarnung"*, `hora.py` nutzt 🕰️ |
| **Die Störmeldungs-Flut muss aufhören** (28.07., 10:00 — *„zweimal pro Minute … super nervig"*) | ✅ **Behoben** am selben Tag (Dämpfer mit Entwarnung; ohne ihn hätten vierzehn Tage rechnerisch zwanzigtausend Meldungen ergeben) |
| **Unter jeden Bau eine Textnachricht, was gebaut wurde** (28.07., 10:12) | ✅ Adam widerruft es zwei Minuten später selbst: *„Aber ich sehe gerade, das hast du gerade auch gemacht. Das läuft also perfekt."* |
| **Abgrenzung zu den grauen Herren** (28.07., 09:13 — *„das darf nicht ins Gegenteil geführt werden … bitte festhalten in dem ganzen Konzept"*) | ✅ **In der Werte-Charta**, und zwar als Prüffrage: *„Der Test der grauen Herren — gibt sie Zeit zurück, oder schichtet sie nur um?"* Genau sein Gedanke, in eine Frage übersetzt |
| **Laufende Aufgabe unterbrechen können** (28.07., 08:50) | ✅ **für den Bot** — 5.5: `INTERRUPT_PREFIXES` (korrektur/stopp/halt/brich ab …) brechen den laufenden Vorgang ab, dazu `/stopp`. **Aber nur für den Bot** — siehe ⑱ |

**Was diese sechs gemeinsam haben:** Es sind **Korrekturen an etwas
Sichtbarem** — ein Knopf, ein Emoji, eine Meldung. **Was fehlt, sind
Verhaltensregeln und Vorhaben.** Dasselbe Muster wie in den Blöcken 7 bis 10,
jetzt an einem Tag mit hoher Trefferquote gemessen — also **kein
Sorgfaltsproblem, sondern ein Kanalproblem.**

---

## Die sechs Lücken

### ⑯ Die Dateinamen-Regel — und ich verletze sie in diesem Augenblick

**Wortlaut (27.07., 11:56):** *„Ich habe eine Bitte. **Alle Dateien, die du hier
produzierst — das soll eine feste Regel sein — müssen durchnummeriert sein, und
zwar am Anfang.** Gerne einfach mit Datum, und zwar erst Jahr, dann Monat, dann
Tag, sodass sie in jedem Ordner sortierbar sind, also chronologisch
sortierbar."*

Mit ausdrücklicher Eingrenzung, die er selbst mitliefert: *„Da geht es nur um
Sachen, die für unser Konzept wichtig sind, die ich auch weitergeben will —
nicht um Zusammenfassungen oder Checklisten."*

**Gemessen:** `Dateiname + Datum`, `chronologisch sortierbar`, `Namensschema` —
**null** in `MIGRATION.md`, `CLAUDE.md` und `docs/`.

**Und ich bin der Hauptverursacher.** Was heute bei dir eingegangen ist, heißt
`BLOCK7-gesamtpruefung.md`, `AUFTRAG-MICK-aus-bloecken-7-8.md`,
`NACHMESSUNG-notbetrieb-3a.md` — **kein einziges mit Datum vorn.** In deinem
Telegram-Verlauf stehen sie chronologisch; in einem Ordner abgelegt sind sie
es nicht. Genau der Fall, den du beschrieben hast.

**Ab sofort:** `2026-08-31-block-7-gesamtpruefung.md`. Das kostet mich nichts
und ist ab der nächsten Datei drin.

### ⑰ Zeitschätzungen — an einem Tag zweimal gerügt

**Erste Rüge (28.07., 10:12), zu deinen eigenen Ansagen:** *„Du musst dich
abgleichen auf das Modell, auf dem du gerade fährst … wenn du sagst, es dauert
15 Minuten, und hast das in zwei Minuten fertig, das passt nicht … weil ich ja
teilweise vom Gerät weggehe."*

**Zweite Rüge (28.07., 13:28), zu Schätzungen über deine Vorhaben:** *„Fünf
Minuten für eine Selleriesuppe … das dauert immer eine halbe Stunde so was.
**Rechne nicht zu knapp.** … Merk dir das mal grundsätzlich: rechne eher ein
bisschen zu viel ein als zu wenig. Das ist das grundsätzliche Thema bei mir,
dass ich dazu neige zu glauben, ich brauche oft länger, als ich mir vornehme."*

**Gemessen: null.** Keine Regel zu Zeitschätzungen, weder für die eigene
Arbeit noch für Adams.

**Warum das mehr ist als Genauigkeit:** Der zweite Fall ist ein
**Assistenz-Grundsatz**. Adam sagt selbst, er unterschätzt Dauer — die Hilfe
besteht darin, **dagegen** zu rechnen, nicht mit ihm. Ein Assistent, der seine
Selbstüberschätzung spiegelt, verstärkt sie.

### ⑱ Unterbrechbarkeit — für den Bot gebaut, für alles andere nicht

**Wortlaut (28.07., 08:50):** *„Wenn du mal so weit bist, dass du wirklich
durcharbeitest, dass ich auch eine Möglichkeit habe, **dich zu unterbrechen**
… Wenn ich schreibe ‚unterbrich bitte den Prozess', muss das funktionieren …
**Das gilt dann auch für weitere Sitzungen und zukünftige Prozesse, die
durchlaufen** … Die **Befehlshoheit** haben sozusagen — es kann nicht sein,
dass Prozesse einfach weiterlaufen und wir keine Möglichkeit haben,
einzugreifen."*

**Gemessen:** 5.5 deckt den **Bot-Job** vollständig ab. **9.8 Hora — der
autonome Läufer — enthält die Wörter `unterbrech`, `stopp`, `abbruch`,
`anhalten`, `befehlshoheit` kein einziges Mal.**

Das ist genau die Klasse, die Adam benannt hat: Der eine Fall ist gebaut, die
**Menge** ist es nicht. Und Hora ist der Fall, für den er die Regel wollte —
ein Läufer, der nachts stundenlang arbeitet.

### ⑲ Der Übergabeweg zwischen den Sitzungen — und er beißt gerade jetzt

**Wortlaut (28.07., 10:57), und es ist die schärfste Selbstbeobachtung des
ganzen Materials:**

> *„Jetzt war ich die ganze Zeit mit dem Aufsetzen beschäftigt … ich bin in den
> Sitzungen drin und hin und her und muss dies und das kopieren und raussuchen
> … **Auch dieses Sich-hin-und-her-Schicken in die Kontrollsitzung, dass es
> durchkontrolliert wird — das muss alleine gehen.** … Sonst bin ich ein
> **Sklave dieses Entwicklungsprojekts**, und dann habe ich die grauen Herren
> über die Hintertür KI doch bekommen. Und das will ich dringend vermeiden."*

**Gemessen — teilweise gebaut, nie als Ganzes entworfen:**
- `log_sync.sh` spiegelt **Claudias Ausarbeitungen** VPS → Log-Repo (eine
  Richtung, eine Sitzung), mit hart ausgeschlossenem Gedächtnis und
  Geheimnissen.
- Mick hat heute Abend berichtet, dass **einige meiner Papiere ihn ohne dein
  Zutun erreicht haben** (`ZWISCHENBERICHT`, `RUECKFRAGE-CONNI`) — andere
  nicht. **Wie dieser Spiegel auswählt, ist nirgends beschrieben.**
- **9.4** deckt den Weg für *Entscheidungen* (Freigabe-Postfach → datierte
  Zeile im Drehbuch, Phase A gebaut). **Nicht** den Weg für *Papiere zwischen
  Sitzungen.*

**Es gibt keinen Punkt für den Übergabeweg als Ganzes.** Und die Wirkung ist
heute Abend live messbar: Du kopierst um 23 Uhr Dateien von mir zu Mick.

### ⑳ Der „Vertrag" zwischen dir und der Assistenz

**Wortlaut (28.07., 08:30):** *„Ich habe den Impuls, dass wir für unsere
Sitzungen und Projekte **Verträge aufsetzen** … was die festen Regeln sind, an
die es sich zu halten gilt, vor allem natürlich von deiner Seite. … Ich mag
Verträge eigentlich nicht so gerne, aber sie helfen, gewisse Dinge fest
einzuhalten. **Das können wir mal festhalten und die Idee behalten.**"*

**Gemessen:** `Vertrag` kommt nur in geschäftlichem Sinn vor
(Dienstleistungsvertrag, Vertragslage bei Fremdanbietern) — **nicht** als
Regelwerk zwischen dir und der Assistenz.

**Meine Einordnung, unaufgefordert:** Der Impuls ist bereits halb umgesetzt —
`CLAUDE.md` **ist** dieses Regelwerk, es heißt nur nicht so. Was fehlt, ist
sein Kern: **Verbindlichkeit mit Prüfung.** Genau das misst diese Prüfung
gerade, und die Zwischenbilanz ist ernüchternd. Ein „Vertrag" ohne Prüfer wäre
die nächste Bitte.

### ㉑ Namen von Personen

Am 28.07. korrigierst du binnen Minuten dreimal: **Claus, nicht Karl** ·
**Frank ≠ Frankie** · *„Was es mit Renate auf sich hat, weiß ich nicht."*

**Gemessen:** kein Personen-Register.

**⚠️ Und hier rate ich zur Vorsicht statt zum Bau.** Namen von Angehörigen
sind exakt die Kategorie, die `CLAUDE.md` als **heikelste Muster** führt und
die **nur über den cloud-freien Weg** (`/ampel`-Button oder `/ampel rot …`)
gepflegt werden darf. Ein Personen-Register ist deshalb **kein kleines
Komfort-Feature**, sondern eine Datenschutz-Entscheidung. Ich lege es als
Befund vor, nicht als Auftrag.

---

## Nicht prüfbar — Sollliste Punkt 9

**Deine Erinnerung für die Rückkehr (27.07., 12:05):** *„Stell bitte noch eine
Erinnerung ein, dass wenn ich wieder da bin … ich hätte dann gerne eine
Zusammenfassung, die ich potenziell auch an NotebookLM weitergeben kann, um
mir eine Kurzpräsentation erstellen zu lassen — was wir schon gemacht haben
und was als Nächstes kommt … quasi die erste Prozess-Präsentation."*

Ob diese Erinnerung gesetzt wurde, kann ich von hier nicht messen — sie läge
im Gedächtnis oder in `pending-items.md` auf dem VPS. **Du warst Mitte August
zurück; ob die Zusammenfassung kam, weißt du besser als ich.** Kommt sie auf
Micks Sollliste als **Punkt 9**.

---

## Was diese Blöcke zur Kontingent-Frage beitragen

Am **27.07. um 13:49** fällt der Satz *„Funktionierst du noch? Kontingent ist
aufgebraucht"* — und am nächsten Morgen die Auswertung:

> *„Das zeigte sehr eindrücklich, was nicht passieren darf … **Tiefere,
> intensive Prozesse müssen immer im Vorfeld gestoppt werden, damit genügend
> Kontingent für die Alltagsaufgaben bleibt.** … Der Grundbot, der
> Gesprächspartner, der Hauptassistent, **der darf eigentlich nie schlafen
> gehen**, weil das Kontingent aufgebraucht ist."*

**Das ist derselbe Punkt wie meine Lücke ② vom 26.07., jetzt mit einem
gelebten Ausfall dahinter.** Ein ganzer Arbeitstag verloren. Und Adam merkt
zusätzlich an, dass **Zusatzkontingent aufgeladen war und nicht angerührt
wurde** — was seinen Entscheid „deaktiviert lassen" von damals bestätigt.

Mick hat N-1 und N-2 heute Abend eingetragen; **dieser Beleg gehört dazu** und
liegt im Auftragspapier.

---

## Laufender Stand

| | |
|---|---|
| Blöcke gelesen | **12 von 18** |
| Zeitraum | 13.07. – 28.07. nachts |
| Kandidaten gedeckt | **33** |
| **Lücken gesamt** | **29** |
| Sollliste Gedächtnis-Griff | **9 Punkte** |
| gerissene Termine | 1 |

**Beobachtung zur Methode:** Die Trefferquote dieser beiden Blöcke ist die
beste bisher — sechs von sechs sichtbaren Korrekturen sind gebaut. **Das
schärft den Befund, statt ihn zu entkräften:** Es scheitert nicht an Sorgfalt,
sondern daran, dass **Verhaltensregeln keinen Weg ins Drehbuch haben** und
**Vorhaben ohne Punkt keinen Ort.** Beides ist ein Kanalproblem, kein
Fleißproblem.
