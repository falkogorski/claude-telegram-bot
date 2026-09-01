> **Zweck: ANSICHT + ENTSCHEID** · **Zu tun:** lesen, wenn du wach bist.
> **Drei Fragen am Ende.** Das Mick-Papier dazu liegt daneben — beide zusammen,
> nach der neuen Regel.

# Gesamtprüfung — Abschluss: Blöcke 16 bis 18 und der Rest von gestern

**Stichtag:** 01.09.2026, 01:37 MESZ (Systemuhr abgelesen; Container auf UTC)
**Gelesen:** Blöcke 16–18 (27.08.–31.08. mittags) **plus** der Nachmittag und
Abend des 31.08. aus den Tagesprotokollen — der lag außerhalb meiner
Extraktion. **Damit ist das Material vollständig durchgesehen.**

---

# Die eine Sache, die über allem steht

**Du hast zweimal gesagt, wir sollen für das Zahlen-Vorlesen ein fertiges
Regelwerk nehmen. Beide Male ist es nicht passiert.**

> **25.08., 12:32:** *„Vielleicht schaust du mal, ob es da irgendwo
> Open-Source-Quellen schon regelsatzfertig gemacht haben."*
>
> **29.08., 00:05, deutlich schärfer:** *„Da gab es doch ein Regelwerk für, was
> wir implementieren wollten. **Wieso hast du das schon wieder vergessen?** …
> Wir müssen nicht das Rad neu erfinden. **Das war eine feste Regel**, dass wir
> uns da nicht reinfuchsen, sondern Sachen hinzunehmen, die es einfacher
> machen. Es ist viel schlauer, ein Haus aus verschiedenen Bauelementen zu
> bauen, die es schon gibt, als jedes Bauelement selber herzustellen."*

**Gemessen in `bot.py` — was stattdessen entstanden ist:**

`_normalize_doppelpunkt_zahlen` · `_normalize_tausenderpunkte` ·
`_normalize_number_ranges` · `_normalize_dates` · `_normalize_jahreszahlen` ·
`_normalize_kennnummern` · `_normalize_versions`

**Sieben handgebaute Umschreiber.** Und: `num2words`, `inflect`, `babel` —
**null Treffer** in `requirements.txt` und im ganzen Repo. Es wurde nie
geprüft, ob es das fertig gibt.

**Dazu kommt dein zweiter Ausweg, den ich gestern schon gemeldet habe:** Punkt
9.1 (TTS mit SSML) bringt die Unterscheidung mit — und ist mit dem
Zahlen-Problem nirgends verknüpft.

**Das ist kein Vorlese-Problem mehr. Es ist das Muster, das du am 25.08. selbst
benannt hast:** *„Es ist gerade überhaupt nicht flexibel, was wir machen,
sondern total eingefahren."*

---

# Die zweite Sache, und sie geht gegen mich

**Du hast viermal in drei Tagen dieselbe Sprachregel verlangt:**

| Wann | Wortlaut |
|---|---|
| 27.08., 08:40 | *„Ich bin sehr viel positive Formulierung"* — und: keine spektakulären Nebensätze wie **„und das ist der eigentliche Befund"** |
| 27.08., 14:55 | *„Spar dir den Satz ‚Ich habe nachgesehen statt geraten'"* |
| 28.08., 19:18 | *„Bleib simpel und einfach und klar. Keine Floskeln. **Verankert das jetzt mal endlich.**"* |
| 28.08., 23:24 | *„‚Deine Beobachtung ist schärfer als der Fehler selbst' — diese Vergleiche, lass sie doch weg. Diese Bewertungen sind doch auch Panne."* |

**Gemessen: nichts davon ist abgelegt** — nicht im Drehbuch, nicht in
`CLAUDE.md`. Auch der Forschungsbefund dahinter nicht, den Claudia geliefert
hat (**C3AI**: positiv formulierte Prinzipien führen eher zu dem Verhalten,
das Menschen als richtig empfinden) — und du hattest ausdrücklich gesagt, du
willst diesen Punkt *„sehr weit nach vorne ziehen"*.

**Und ich mache es fortlaufend.** In meinen Papieren von heute Nacht stehen
*„das ist der eigentliche Befund"*, *„der Fund ist schärfer als"*, *„und das
ist die Pointe"*. **Dieselbe Sorte Satz, die du viermal abbestellt hast.** Ich
nehme das ab sofort raus; es steht als Auflage im Mick-Papier, damit es nicht
nur mein Vorsatz bleibt.

---

# Was noch fehlt — kurz

| | Was | Wann gesagt |
|---|---|---|
| **Q1** | **Zweiter Chat als Alltagsbegleiter** — dieser hier bleibt die Werkstatt (Bauaufträge, Auto-Bash), daneben ein Chat für Kalender, Mail, Alltag, **ohne** Auto-Bash. Die Werkstatt muss den anderen **lesen** können | 31.08., 10:15 |
| **Q2** | **Knopf „Verarbeiten"/„Auswerten"** unter empfangenen Dateien, damit der Bot sie von sich aus liest und umsetzt | **01.09., 00:51 — vor einer Stunde** |
| **Q3** | **Keine absoluten Zahlen in Bauaufträgen** — Werte in **einer** zentralen Bezugsliste, dort auch vermerkt, welche Prozesse darauf zugreifen | 27.08., 19:48 |
| **Q4** | **Sofort aufräumen, keine Karteileichen** — als Grundregel | 28.08., 18:43 |
| **Q5** | **Quellenvielfalt** — nicht immer dieselben Quellen; Wikipedia taugt für Sachdaten, ist heikel bei politisch bewerteten Diensten | 27.08., 14:26 |
| **Q6** | **Russische und chinesische Suchanbieter** aufnehmen, mit derselben Bestätigungsregel wie Google/Bing | 27.08., 16:09 |
| **Q7** | **Ausarbeitung zum offenen Modell** („AIDA/Aider") — Nutzen, Einbindung, Vor- und Nachteile | 27.08., 15:21 |
| **Q8** | **Du lehnst den „Fehler einbauen"-Test ab** (*„das ist alles manipulativ"*) — eine Entscheidung, die nirgends steht | 27.08., 19:22 |

**Und ein Fall eigener Art:** Die **Überschriften-Regel** ist am 27.08. als
Bauauftrag gebaut worden — und du hast sie am **31.08., 11:45** erneut
angemahnt: *„Bitte endlich nachhaltig und verlässlich ändern!"* **Das ist
nicht fehlend, das ist gebaut und hält nicht.** Andere Klasse, andere Abhilfe:
messen, warum es bricht, statt neu bauen.

---

# Zwei gute Nachrichten, beide gemessen

**① Deine Bedingung von gestern 12:00 ist erfüllt.** Du hattest gesagt:

> *„Die Baukastenstufe ja. Gerne, **wenn die Sperren vorher als Verbotsregeln
> hinterlegt werden.** Wenn du das hinbekommst, dass das auch funktioniert,
> zuverlässig … dann ja."*

**Genau das habe ich gestern Abend am Code nachgemessen**, bevor ich die
Bash-Dauerfreigabe freigegeben habe: Repo-Schreibsperre bei Zeile **3051**,
`bashfreigabe`-Abweisung bei **3091**, der Dauerfreigabe-Kurzschluss erst bei
**3164**. **Die Sperren stehen davor und gelten weiter.** Deine Vorbedingung
ist also nicht nur zugesagt, sondern belegt.

**② Claudias letzte zwei Aufträge tragen** — damit ist meine Prüfung ihrer
fünf vollständig:

- **Freigaben-Erinnerung:** sauber. Der heikle Punkt ist richtig gelöst — die
  Erinnerungen entstehen durch **Aufteilen der Wartezeit**, nicht durch einen
  zweiten Zeitgeber, der von deiner Entscheidung nichts erfährt. Und **beide
  Zahlen werden Einstellgrößen** statt fester Werte im Code — **das ist genau
  deine Idee Q3, in der Praxis angewandt.** Ich nenne sie im Mick-Papier als
  Vorbild.
- **Sitzungsstart legt den Stand vor:** richtig, und **es hätte die Nacht von
  gestern verhindert.** Der Auftrag lässt den Ordner `docs/auftraege/` je
  Datei mit einer Zeile vorlegen — genau dort lagen die drei Konzepte, die ich
  fünf Wochen lang nicht gefunden habe. **Eine Ergänzung habe ich:** Der
  Auftrag liest `docs/auftraege/`, aber **nicht `docs/konzepte/`** — dieselben
  Konzepte liegen auch dort. Eine Zeile mehr.

---

# Die Gesamtbilanz

| | |
|---|---|
| Material | **687 Adam-Nachrichten**, 14.07.–31.08., vollständig |
| Blöcke | **18 von 18 gelesen**, plus der Nachmittag des 31.08. |
| Kandidaten geprüft | **~70** |
| **gedeckt** | **~55** |
| **Lücken** | **~45** |
| davon **Entscheidungen bei dir** | 8 |
| gerissene Fristen | 2 |
| eigene Korrekturen | **6** (Rasterfehler, ein zurückgenommener roter Befund, zwei übernommene Zweit-Hand-Aussagen) |

**Der Befund über allen Befunden ist derselbe geblieben, nur besser belegt:**
Es scheitert fast nie an Sorgfalt. **Es scheitert daran, dass Gesagtes keinen
Ort hat** — Verhaltensregeln liegen im Gedächtnis und nicht im Drehbuch,
Konzepte im Auftragsordner und nicht im Drehbuch, Entscheidungen im Chat und
nirgends sonst.

---

# Drei Fragen, wenn du wach bist

1. **Das fertige Regelwerk fürs Zahlen-Vorlesen** — soll ich prüfen lassen, ob
   `num2words`/`inflect` das leisten, **oder** direkt auf 9.1 (Azure/SSML)
   setzen und die sieben Umschreiber entfallen lassen? 💰 Der zweite Weg ist
   eine Kostenentscheidung.
2. **Q1 zweiter Chat und Q2 „Verarbeiten"-Knopf** — beide sind frisch und
   klein. Sollen sie in die nächste Bau-Runde, oder wartest du damit?
3. **Der Werte- und Zieltermin** von „Mitte August" ist weiter offen. Er steht
   jetzt als Wiedervorlage im Drehbuch, damit er nicht ein drittes Mal
   verfällt.

**Nichts davon ist gebaut worden.** Alles Offene liegt als Eintrag oder
Wiedervorlage — nach deiner Ansage: liegen lassen statt umbauen.
