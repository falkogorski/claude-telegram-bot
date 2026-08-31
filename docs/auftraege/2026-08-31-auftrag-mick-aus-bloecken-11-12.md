> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren.
> **Fünf Ablage-Einträge, kein Code.** Punktnummern entscheidet Adam.

# Auftrag an Mick — fünf Nachträge aus den Blöcken 11 und 12 (27./28.07.)

**Stichtag:** 31.08.2026, 22:58 MESZ · **Von:** Engywuck (Kontrolle)
**Herkunft:** Gesamtprüfung der Bot-Protokolle. **Alle Zitate im Wortlaut aus
dem Protokoll**, keine Ableitung.

**Vorab, weil es hier besonders gilt:** In denselben Blöcken habe ich **sechs
Wünsche gemessen, die exakt so gebaut wurden, wie Adam sie gesagt hat**
(Gründlich-Toggle, die drei Emojis, der Meldungs-Dämpfer, der Bau-Kommentar,
die Graue-Herren-Prüffrage, der Job-Abbruch). **Das ist kein Sorgfaltsproblem.**
Es fehlen die Sachen, die keinen Ort haben — nicht die, die einen hatten.

---

## N-4 · Die Dateinamen-Regel — nach `CLAUDE.md`

**Adam am 27.07., 11:56 (Wortlaut):**

> *„Ich habe eine Bitte. **Alle Dateien, die du hier produzierst — das soll
> eine feste Regel sein — müssen durchnummeriert sein, und zwar am Anfang.**
> Gerne einfach mit Datum, und zwar erst Jahr, dann Monat, dann Tag, sodass
> sie in jedem Ordner sortierbar sind, also chronologisch sortierbar. … Da
> geht es nur um Sachen, die für unser Konzept wichtig sind, die ich auch
> weitergeben will — **nicht** um Zusammenfassungen oder Checklisten."*

**Gemessen:** kein Namensschema in `MIGRATION.md`, `CLAUDE.md` oder `docs/`.

**Einzutragen** (kurzer Abschnitt, die Eingrenzung gehört dazu):

> **Dateien an Adam tragen das Datum vorn:** `JJJJ-MM-TT-<name>.md`. Gilt für
> Konzept- und Weitergabe-Papiere, **nicht** für Alltags-Zusammenfassungen und
> Checklisten. Grund: In einem Ordner abgelegt sollen sie chronologisch
> sortieren — der Telegram-Verlauf tut das von selbst, der Ordner nicht.

**Selbstauskunft, damit die Regel nicht hohl steht:** Ich habe sie heute den
ganzen Tag verletzt (`BLOCK7-…`, `AUFTRAG-MICK-…`, `NACHMESSUNG-…`). Ab dieser
Datei nicht mehr — sie heißt `2026-08-31-auftrag-mick-aus-bloecken-11-12.md`.

## N-5 · Unterbrechbarkeit gehört an **9.8 Hora**

**Adam am 28.07., 08:50 (Wortlaut, gekürzt):**

> *„Wenn du mal so weit bist, dass du wirklich durcharbeitest — dass ich auch
> eine Möglichkeit habe, **dich zu unterbrechen** … Wenn ich schreibe
> ‚unterbrich bitte den Prozess', muss das funktionieren, zumindest am
> nächsten Wegpunkt. **Das gilt dann auch für weitere Sitzungen und
> zukünftige Prozesse, die durchlaufen** … Die **Befehlshoheit** haben
> sozusagen — es kann nicht sein, dass Prozesse einfach weiterlaufen und wir
> keine Möglichkeit haben, einzugreifen."*

**Gemessen:**
- **5.5 deckt den Bot-Job vollständig ab** — `INTERRUPT_PREFIXES`
  (korrektur/stopp/halt/brich das ab/…) plus `/stopp`, Test
  `test_queue_order_5_5.py`. **Nichts daran ist zu ändern.**
- **9.8 Hora enthält `unterbrech`, `stopp`, `abbruch`, `anhalten`,
  `befehlshoheit` kein einziges Mal.**

**Einzutragen:** an 9.8 eine Anforderungszeile — *ein laufender Hora-Lauf muss
sich am nächsten Wegpunkt anhalten lassen; Adams Befehlshoheit gilt auch für
autonome Läufer*, mit Adams Zitat und dem Verweis auf 5.5 als Vorbild.

**⚠️ Ausdrücklich nur eintragen, nicht bauen.** Ob und wie ein Hora-Stopp
gebaut wird, ist ein eigener Entwurf mit eigener Sicherheitsfrage.

## N-6 · Der Übergabeweg zwischen den Sitzungen — Ort fehlt

**Adam am 28.07., 10:57 (Wortlaut, gekürzt):**

> *„Ich bin in den Sitzungen drin und hin und her und muss dies und das
> kopieren und raussuchen … **Auch dieses Sich-hin-und-her-Schicken in die
> Kontrollsitzung, dass es durchkontrolliert wird — das muss alleine gehen.**
> … Sonst bin ich ein **Sklave dieses Entwicklungsprojekts**, und dann habe
> ich die grauen Herren über die Hintertür KI doch bekommen."*

**Gemessen — halb gebaut, nie als Ganzes entworfen:**
- `log_sync.sh` spiegelt **Claudias Ausarbeitungen** VPS → Log-Repo (eine
  Richtung, eine Sitzung, Gedächtnis und Geheimnisse hart ausgeschlossen).
- Einige meiner Papiere erreichen dich **ohne Adams Zutun** (du hast heute
  `ZWISCHENBERICHT-gesamtpruefung.md` und `RUECKFRAGE-CONNI.md` im Spiegel
  gefunden), andere nicht. **Wie dieser Spiegel auswählt, ist nirgends
  beschrieben** — bitte beim Eintragen kurz benennen, was du dazu weißt.
- **9.4** deckt den Weg für **Entscheidungen** (Freigabe-Postfach → datierte
  Drehbuchzeile, Phase A gebaut) — **nicht** den für Papiere zwischen
  Sitzungen.

**Einzutragen:** als eigenes Papier `gedanke-uebergabeweg-sitzungen.md`
(Muster: `gedanke-gps-standort.md`), **ohne Punktnummer**, mit Adams Zitat, dem
gemessenen Ist-Stand oben und der offenen Frage, ob es ein eigener Punkt wird
oder ein Ausbau von 9.4.

## N-7 · Der „Vertrag" zwischen Adam und der Assistenz

**Adam am 28.07., 08:30:** *„Ich habe den Impuls, dass wir für unsere Sitzungen
und Projekte **Verträge aufsetzen** … was die festen Regeln sind, an die es
sich zu halten gilt, vor allem von deiner Seite. Ich mag Verträge eigentlich
nicht so gerne, aber sie helfen, gewisse Dinge fest einzuhalten. **Das können
wir mal festhalten und die Idee behalten.**"*

**Gemessen:** `Vertrag` nur im geschäftlichen Sinn.

**Einzutragen:** dasselbe Muster, `gedanke-vertrag-regelwerk.md`, mit dem
Vermerk aus meiner Prüfung: **`CLAUDE.md` ist dieses Regelwerk bereits — es
heißt nur nicht so.** Was fehlt, ist sein Kern: **Verbindlichkeit mit
Prüfung.** Ein „Vertrag" ohne Prüfer wäre die nächste Bitte.

## N-8 · Personen-Namen — **Befund, ausdrücklich kein Auftrag**

Adam korrigiert am 28.07. binnen Minuten dreimal: **Claus, nicht Karl** ·
**Frank ≠ Frankie** · *„Was es mit Renate auf sich hat, weiß ich nicht."*

**Gemessen:** kein Personen-Register.

**🔴 Bitte NICHTS bauen und nichts eintragen, was Namen enthält.** Namen von
Angehörigen sind exakt die Kategorie, die `CLAUDE.md` als **heikelste Muster**
führt und die **nur über den cloud-freien Weg** gepflegt werden darf
(`/ampel`-Button oder `/ampel rot …`, beides deterministisch ohne
Claude-Beteiligung). Ein Personen-Register ist deshalb eine
**Datenschutz-Entscheidung Adams**, kein Komfort-Feature.

**Einzutragen ist nur der Befund** — dass wiederholte Namensverwechslungen
gemessen wurden und dass die Lösung, falls Adam sie will, über den
Ampel-Button-Weg gehen muss. **Ohne Namen im Text.**

---

## Ein Befund ohne Auftrag — bewusst so

**Zeitschätzungen** (Adam rügt sie am 28.07. **zweimal**: *„wenn du sagst 15
Minuten und bist in zwei fertig, das passt nicht"* und *„rechne nicht zu knapp
… merk dir das grundsätzlich: eher zu viel als zu wenig"*).

**Gemessen: keine Regel dazu, nirgends.** Ich gebe dafür **keinen Auftrag**,
weil die Stelle unklar ist: Es ist eine **Verhaltensregel des Bots**, und die
wirkt über Gedächtnis oder Systemprompt — nicht über einen Drehbuch-Eintrag.
**Wo Verhaltensregeln künftig hingehören, ist eine offene Entscheidung Adams**
(mein Vorschlag an ihn: Spiegel im Drehbuch, Gedächtnis bleibt wirksam). Bis
die entschieden ist, wäre jeder Eintrag geraten.

**Der zweite Teil ist der wichtigere und gehört mit in die Notiz, wenn sie
irgendwann geschrieben wird:** Adam sagt selbst, er **unterschätzt** Dauer.
Die Hilfe besteht darin, **dagegen** zu rechnen, nicht mit ihm.

---

## Auflagen

- **Kein Code.** Fünf Ablage-Einträge, sonst nichts.
- **Keine Punktnummern vergeben** — Adams Entscheidung.
- **N-8 ohne Namen.**
- 💰 **Keine Kostenquelle berührt.**
- **Regressionslauf vor dem Commit**, auch bei reiner Doku — deine Lehre vom
  23.08.
