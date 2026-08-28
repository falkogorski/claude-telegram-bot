# Bauauftrag — Stundenblume: melden nur bei Änderung, Bestand einmal täglich

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau)
**Angelegt:** 28.08.2026, 10:25 Uhr
**Anlass:** Adam am 28.08.2026 um 10:07 Uhr
**Umfang:** drei Eingriffe in `scripts/stundenblume.py`, einer in `scripts/daily_check.sh`,
Testanpassungen in `scripts/test_stundenblumen.py`

> **Setzt auf `2026-08-27_bauauftrag-stundenblume-auslagerung.md` auf** (Adam
> freigegeben am 27.08. um 18:04 Uhr, seit 18:30 Uhr im Log-Archiv, noch nicht
> gebaut). Jenes Papier behandelt **einen** Befund, dieses das **Meldeverhalten
> aller**. Beide greifen ineinander und sollten in einem Zug gebaut werden.

---

## Adams Wunsch, in seinen Worten

> „Die meldet jede Stunde. Können wir das vielleicht so machen, dass die nur
> meldet, wenn sich was geändert hat? Und ansonsten einmal am Tag … da kann auch
> der Stundenblumen-Bericht quasi rein. Und damit meine ich jetzt nicht die Größe
> des Auslagerungsbereiches. Ob da jetzt ein paar Megabyte mehr dazugekommen sind,
> ist egal. Es sei denn, dass das irgendwie eine kritische, plötzliche Erhöhung
> ist. Also nur das, was wirklich wichtig ist."

---

## Der Befund, gemessen

**Was Adam sieht** (`~/postfach/sent/blume-*.json`, alle Läufe seit gestern
Mittag durchgesehen): seit dem 27.08. um 14:21 Uhr **zwanzig Meldungen**, eine je
Stunde, mit demselben Satz über den Auslagerungsbereich. Der Wert wanderte
zunächst von 450 auf 619 MiB und steht seit gestern 18:23 Uhr **völlig still** —
seither sind es dreizehn wortgleiche Nachrichten.

**Warum das geschieht:** `scripts/stundenblume.py`, Zeile 598 —
`WIEDERVORLAGE_S = 3600`. Der Dämpfer schweigt eine Stunde und wertet den Befund
danach wieder als neu. Das galt im Juli als Fortschritt: Davor meldete die Blume
**minütlich**, der Dämpfer senkte es auf stündlich. Der Schritt war richtig und
ist an einem Dauerzustand zu Ende gedacht worden — er endet nie von selbst.

**Der Auslagerungsstand ist der Musterfall dafür.** Gestern nachgemessen:
`pswpin` steht bei null, in gut sechs Wochen Laufzeit wurde nichts zurückgeholt.
Der Bereich leert sich ohne Neustart nicht. Ein Befund, der nie verschwindet,
meldet unter der jetzigen Regel bis in alle Ewigkeit vierundzwanzigmal am Tag.

**Die aktuelle Lage ist unauffällig** (28.08., 10:15 Uhr): 5888 von 7940 MiB
Arbeitsspeicher verfügbar, 625 von 4095 MiB ausgelagert, `vm.swappiness` auf zehn.
Es gibt nichts zu tun — das ist ja gerade das Problem.

---

## Ein zweiter Fehler, beim Messen gefunden

**Nach einer Entwarnung meldet derselbe Befund sofort wieder** — die Stunde
Wiedervorlage greift dann nicht. Grund: `_daempfen()` schreibt in Zeile 663 nur
die **aktuellen** Kennungen zurück ins Gedächtnis. Eine entwarnte Kennung ist
danach unbekannt, und `jetzt − 0 >= 3600` trifft beim nächsten Auftreten immer zu.

**Belegt am 16.08.2026:** Zwischen 01:28 und 02:17 Uhr wechselten „Bot-Prozess
nicht vorhanden" und „erledigt" **sechsundzwanzigmal** — dreizehn Alarme,
dreizehn Entwarnungen, in fünfzig Minuten. Der Dämpfer war wirkungslos, weil
jede Entwarnung sein Gedächtnis leerte.

Das gehört mit behoben. Ohne diesen Fix würde die Umstellung unten den Fall sogar
verschärfen: Wenn die Zeitschwelle wegfällt und allein die Änderung zählt, ist ein
flatternder Befund eine ununterbrochene Änderung.

---

## Auftrag 3 — Wiedervorlage nach Zeit durch Wiedervorlage nach Änderung ersetzen

**Stelle:** `scripts/stundenblume.py`, `_daempfen()`, Zeilen 607 bis 674.

**Neue Regel:** Ein Befund wird gemeldet, wenn seine Kennung **auftritt**, und
danach nicht wieder, solange sie ununterbrochen ansteht. Fällt sie weg, wird
entwarnt. Tritt sie erneut auf, wird erneut gemeldet.

**`WIEDERVORLAGE_S` entfällt als Melde-Auslöser.** Der Wert bleibt als Größe
erhalten, bekommt aber die neue Bedeutung aus Auftrag 4 (Sperrfrist gegen
Flattern) und einen Namen, der das sagt — Vorschlag `ERNEUT_SPERRE_S`, Voreinstellung
1800 Sekunden.

**Warum die Kennung und nicht der Text der Maßstab bleibt:** Das ist die Zusage
vom 28.07. und sie trägt genau diesen Fall. Der Auslagerungstext ändert sich
mit jedem Megabyte, die Kennung `swap-benutzt` nicht. Damit erfüllt sich Adams
Vorbehalt — „ein paar Megabyte mehr" ist keine Änderung — ohne eine einzige
Sonderregel.

**Was als Änderung gilt, ist damit eine Frage der Kennung.** Wer einen Befund in
Stufen melden will, legt die Stufe in die Kennung (`speicher-hinweis` gegen
`speicher-eng` machen es heute schon richtig). Ein Stufenwechsel meldet dann von
selbst, ein Wackeln innerhalb der Stufe nicht.

---

## Auftrag 4 — Entprellung, damit Flattern nicht zum Dauerfeuer wird

**Stelle:** dieselbe Funktion.

Sobald die Zeitschwelle als Bremse wegfällt, trägt allein der Wechsel. Ein Befund,
der im Minutentakt kommt und geht, erzeugt dann pro Minute zwei Nachrichten. Genau
das ist am 16.08. geschehen, damals trotz der Zeitschwelle.

**Drei Vorkehrungen, alle drei nötig:**

1. **Verzögerte Meldung.** Ein Befund gilt erst als aufgetreten, wenn er in
   **drei aufeinanderfolgenden Läufen** steht — bei Minutentakt also nach drei
   Minuten. Kurze Zuckungen bleiben still, ein echter Ausfall meldet drei Minuten
   später.
2. **Verzögerte Entwarnung.** Eine Entwarnung ergeht erst, wenn der Befund in
   **fünf aufeinanderfolgenden Läufen** fehlt. Ein kurzes Aussetzen erzeugt kein
   „erledigt".
3. **Sperrfrist nach Entwarnung.** Nach einer Entwarnung schweigt dieselbe Kennung
   für `ERNEUT_SPERRE_S` (Vorschlag: eine halbe Stunde), auch wenn sie
   wiederkommt. Dafür behält das Gedächtnis entwarnte Kennungen mit Zeitstempel,
   statt sie zu löschen — **das ist zugleich der Fix für den Fehler oben.**

**Die Begriffe sind Handwerk, nicht Erfindung.** Prometheus kennt beides seit
Jahren: die `for`-Klausel wartet ab, ob eine Bedingung anhält, bevor ein Alarm
als ausgelöst zählt; `keep_firing_for` hält ihn nach dem Wegfall noch eine Weile,
ausdrücklich um flatternde Alarme zu verhindern (Prometheus-Dokumentation,
Abschnitt [Alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/),
gelesen am 28.08.2026). Wir übernehmen das Verfahren, nicht das Werkzeug —
siehe „Warum nicht etwas Fertiges" weiter unten.

**Das Gedächtnis bekommt dafür zwei Felder je Kennung:** die Zahl der Läufe in
Folge, in denen die Kennung gesehen wurde, und die Zahl der Läufe, in denen sie
fehlte. Beide als Zähler, nicht als Zeitstempel — dann trägt die Regel auch, wenn
der Takt einmal geändert wird.

---

## Auftrag 5 — Der Bestand einmal täglich im Vier-Uhr-Bericht

**Stelle:** `scripts/daily_check.sh`, Abschnitt 9 (Zeilen 208 bis 218), plus ein
neuer Schalter in `scripts/stundenblume.py`, `main()` (Zeilen 778 ff.).

**Heute** prüft der Tagescheck nur, ob die Belegkette lebt. Was **ansteht**,
erfährt Adam dort nicht.

**Neu:** ein Schalter `--lage`, der die derzeit anstehenden Befunde aus dem
Gedächtnis liest und je Befund eine Zeile ausgibt, mit dem Zeitpunkt des ersten
Auftretens. Der Tagescheck nimmt diese Zeilen in seinen Bericht auf.

**Damit hat jede Klasse einen Weg:**

| Was | Wohin | Wie oft |
|---|---|---|
| Ein Befund tritt auf oder fällt weg | Telegram | sofort, einmal |
| Ein Befund steht unverändert an | Vier-Uhr-Bericht | einmal täglich |
| Reine Beobachtung, Klasse `p:` | nur Kette und Protokoll | nie an Adam |

Die dritte Zeile stammt aus Auftrag 2 des gestrigen Papiers; sie ist hier nur
der Vollständigkeit halber aufgeführt.

---

## Zwei Entscheidungen für Adam

**Entscheidung 1 — Bleibt der Tagescheck an ruhigen Tagen still?**

Er tut es heute (`MIGRATION.md`, Abschnitt 8.1: „Meldung an Adam **NUR bei
Problemen**, grüne Tage bleiben still"). Adams „ansonsten einmal am Tag" lässt
sich in beide Richtungen lesen.

- **A (Empfehlung): still bleiben.** Steht etwas an, kommt der Bericht ohnehin.
  Steht nichts an, ist die Nachricht „nichts zu tun" genau das Rauschen, das weg
  soll. Der Nachweis bleibt im Protokoll und in der Belegkette lesbar.
- **B: täglich eine Zeile**, auch wenn alles ruhig ist — ein Lebenszeichen.
  Der Preis: eine Nachricht am Tag, die nie etwas bedeutet, und damit der Anfang
  desselben Musters.

**Entscheidung 2 — Erinnert ein anhaltender roter Befund zwischendurch?**

Ein 🔴-Befund, der zwölf Stunden ansteht, meldet nach Auftrag 3 genau einmal und
taucht dann erst im nächsten Tagesbericht auf.

- **A (Empfehlung): eine Erinnerung nach zwölf Stunden**, danach nur noch täglich.
  Nur für die rote Stufe — bei Gelb und Beobachtung nicht.
- **B: keine Sonderregel.** Schlichter, aber ein rotes Ereignis um 05:00 Uhr
  bliebe bis zum nächsten Morgen unwiederholt.

---

## Warum nicht etwas Fertiges

Die Frage gehört gestellt, bevor gebaut wird. Für Schwellwert-Überwachung mit
Entprellung und Wiedervorlage gibt es ausgereifte Werkzeuge — Prometheus mit
Alertmanager, Netdata, Monit. Sie können alles, was hier steht, und mehr.

**Trotzdem ist der Einbau hier richtig**, aus drei Gründen: Die Blume ist mehr
als ein Wächter — sie führt eine fingerabdruckgesicherte Belegkette, die den
Nachweis trägt, dass das System durchgehend gelebt hat. Sie meldet über das
Botenpostfach, ohne den Bot-Schlüssel zu kennen. Und sie kommt ohne Netzdienst
und ohne zweiten Dauerprozess aus. Ein Alarmierungs-Stack daneben ersetzt davon
nichts und bringt einen zweiten Ort mit eigener Pflege.

**Was wir übernehmen, ist das Verfahren**, nicht das Werkzeug: Verzögerung vor
dem Melden, Nachlauf vor dem Entwarnen, Sperrfrist gegen Wiederholung. Alle drei
sind dort seit Jahren erprobt, und keiner davon musste hier erfunden werden.

Sollte das Wachsystem später über die Maschine hinauswachsen, ist der Umstieg
eine eigene Entscheidung — im Migrationsmaster ist er nicht vorgesehen (Phase 8
kennt nur Tagescheck, Regressionstest und Pre-Send-Hook; nachgesehen am 28.08.).

---

## Was kann brechen und wer merkt es

| Was | Wer merkt es | Vorkehrung |
|---|---|---|
| **Der bestehende Test erzwingt das alte Verhalten.** `scripts/test_stundenblumen.py`, `_daempfer_wiederholt_nicht_minuetlich()`, Zeile 409: „nach einer Stunde meldet er sich nicht wieder" — dieser Test **muss** nach der Umstellung fehlschlagen. | Der Vier-Uhr-Check, laut und sofort | Test im selben Zug umschreiben: unveränderter Befund meldet über zwei Stunden genau **einmal**; Wegfall entwarnt; erneutes Auftreten nach der Sperrfrist meldet wieder |
| **Ein echter, kurzer Ausfall wird von der Entprellung verschluckt.** Ein Bot, der zwei Minuten weg ist und wiederkommt, meldet nichts. | Niemand im Chat | Die Belegkette schreibt weiter **minütlich** alles mit — nur der Mund wird leiser, nicht das Auge. Der Tagesbericht kann die Zahl unterdrückter Zuckungen ausweisen |
| **Ein Befund steht an und wird nie wiederholt**, weil der Tagescheck ausfällt. Ein Ausbleiben, das wie Ruhe aussieht. | Die Blume selbst | `tagescheck_pruefen()` (Zeile 196) prüft bereits, ob sich der Tagescheck seit sechsundzwanzig Stunden gemeldet hat, und meldet dessen Stillstand. Diese Kette ist vorhanden und trägt |
| **Das Gedächtnis wächst unbegrenzt**, weil entwarnte Kennungen jetzt aufbewahrt werden. | Niemand | Einträge, deren Entwarnung älter als sieben Tage ist, beim Schreiben verwerfen. Die Zahl der Kennungen ist zweistellig — die Grenze ist Vorsorge, keine Not |
| **Die Zähler stehen im Gedächtnis und gehen bei einem Neustart verloren.** Nach einem Neustart braucht ein anstehender Befund wieder drei Läufe. | Niemand, und es ist hinnehmbar | Drei Minuten Verzug nach einem Neustart sind kein Schaden. Ausdrücklich so gewollt und im Kommentar festhalten, damit es niemand für einen Fehler hält |
| **`--lage` gibt etwas anderes aus als gemeldet wurde**, weil Gedächtnis und Kette auseinanderlaufen. | Niemand | `--lage` liest **dieselbe** Datei, die der Dämpfer schreibt. Kein zweiter Zustand, keine zweite Wahrheit |
| **Die Umstellung wird nie eingespielt** und gilt als erledigt. | Niemand | Der Zustand bleibt *vereinbart*, bis ein Lauf gegen die neue Fassung geprüft hat. Prüfsatz: eine Kennung erzwingen, über zwei Stunden laufen lassen, genau eine Nachricht erwarten |

---

## Nachweis nach dem Bau

Drei Prüfungen, die von außen sichtbar sind:

1. **Der Regressionstest ist grün** — mit den umgeschriebenen Testfällen.
2. **Zwei Stunden Betrieb erzeugen null Wiederholungen.** Zu prüfen an
   `~/postfach/sent/blume-*.json`: nach dem Einspielen darf für eine unverändert
   anstehende Kennung keine zweite Meldung mehr entstehen.
3. **Der nächste Vier-Uhr-Bericht führt den Bestand.** Steht dort nichts, obwohl
   ein Befund ansteht, ist Auftrag 5 nicht wirksam.

---

## Randnotiz

Der Auftrag vom 27.08. liegt seit gestern 18:30 Uhr im Log-Archiv und ist damit
für die Kontrollsitzung lesbar. Er ist freigegeben, aber nicht gebaut — deshalb
erreichten Adam über Nacht weitere sechzehn Meldungen. Das ist kein Vorwurf,
sondern der Grund, beide Papiere in einem Zug zu behandeln.
