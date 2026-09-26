# Bauauftrag — Stimmwechsel auf Azure Neural mit SSML

> **Zustand: gültig** · erstellt 26.09.2026 · von Claudia für Engywuck (Prüfung)
> und danach Mick (Bau)
> **Kostenfreigabe erteilt: Adam am 26.09.2026, 12:33 Uhr — Standard-Stufe (S0)
> mit Kostenriegel bei fünf Euro.** Offen bleibt allein das Anlegen des Kontos,
> das Adams Karte verlangt; eingerichtet wird nichts davor.

## Änderungen

**26.09.2026, 12:40** — Stufe entschieden (S0 mit Riegel bei fünf Euro,
Auftrag 5 neu). Kostenlage um die amtlichen Fundstellen aus Messung M10
ergänzt, Preisangabe korrigiert. Auftrag 6 neu: Behandlung der Ratengrenze.
Region auf Deutschland West-Mitte konkretisiert. Bruchtabelle um zwei Zeilen.

**26.09.2026, 02:00** — erste Fassung.

## Warum jetzt

Der Punkt steht als **9.1** im Drehbuch, Status offen seit dem 12.07.2026. Er hing
nie an der Technik, sondern an einer Kostenfreigabe, die Adam nie vorgelegt wurde.
Am 25.09.2026 hat er danach gefragt: *„Und wann setzen wir das endlich um?"*

**Der Wechsel löst eine ganze Fehlerklasse auf**, nicht nur ein Klangproblem. Im
Drehbuch stehen vier Beschwerden Adams aus fünf Wochen — Tausenderpunkte,
Ziffernfolgen, Mengen, Kurse —, alle über dieselbe Sache. Seine eigene
Schlussfolgerung vom 25.08.: *„Wenn wir auf Azure wechseln, dann hat sich das
ganze Thema aufgelöst."* SSML kennt `<say-as interpret-as="digits">`,
`"cardinal"` und `"characters"` — genau die Unterscheidung, an der eine Wortliste
scheitern muss.

## Die Kostenlage

**Verbrauch, gemessen am 25.09.2026:** Ausgewertet wurden die Gesprächsprotokolle
des Septembers, allein die Bot-Antworten ohne Adams Nachrichten und ohne
Werkzeugzeilen.

| Größe | Wert |
|---|---|
| Tage mit Verkehr | 16 |
| Bot-Antworten gesamt | 331.617 Zeichen |
| je Tag | rund 20.700 Zeichen |
| hochgerechnet auf 30 Tage | rund 622.000 Zeichen |

Das ist eine **Obergrenze** — Links, Codeblöcke und Markdown fallen vor der
Ausgabe heraus, und die Sprachausgabe ist zeitweise abgeschaltet.

**Das kostenfreie Kontingent, amtlich belegt am 26.09.2026:** 0,5 Millionen
Zeichen je Monat für Neural-Stimmen, ausgewiesen auf
[Microsofts Preisseite für Azure Speech](https://azure.microsoft.com/en-us/pricing/details/speech/).
Es gilt in beiden Stufen.

**Der Preis darüber ist nicht belastbar bestätigt.** Die Preisseite zeigt an
dieser Stelle einen Platzhalter. Microsofts eigene
[Quotas-Seite](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)
rechnet in ihrer Bedarfsabschätzung mit **15 US-Dollar je einer Million
Zeichen**; fünf unabhängige Drittübersichten nennen **16**. Die erste Fassung
dieses Auftrags führte 16 als gesetzt — das war zu fest formuliert.

**Ergebnis mit beiden Werten:** rund 122.000 zahlungspflichtige Zeichen im Monat,
also **1,83 bis 1,95 US-Dollar, knapp 1,70 bis 1,80 Euro.** Bei doppeltem
Aufkommen etwa zehn bis elf Euro. **Der amtliche Eurobetrag wird beim Anlegen des
Kontos abgelesen und mit dieser Rechnung verglichen**, bevor der erste Satz
gesprochen wird.

### Warum Standard und nicht die kostenlose Stufe

Die Free-Stufe (F0) hat eine **harte Grenze ohne Abbuchung**: Nach 500.000
Zeichen werden Anfragen gedrosselt oder mit HTTP 429 abgelehnt, ein Wechsel auf
S0 muss ausdrücklich vorgenommen werden. Belegt durch die Antwort eines
Microsoft-Moderators im
[Herstellerforum vom 25.09.2025](https://learn.microsoft.com/en-us/answers/questions/5566384/azure-ai-speech-what-happens-after-free-tier-t0-ex).

Bei einem Bedarf von 622.000 Zeichen heißt das: **Sprachausgabe bis etwa zum 24.
des Monats, danach stumm.** Adam hat das am 26.09. gegen die zwei Euro abgewogen
und sich für die durchgehende Verfügbarkeit entschieden. Die Deckelung übernimmt
der Riegel in Auftrag 5 — damit hängt der Ausfall an unserem Maß und nicht an
Microsofts Monatswechsel.

**Zahlungsmittel:** Eine Karte ist zur Identitätsprüfung erforderlich, wird aber
nicht belastet; es kann eine temporäre Reservierung von einem Dollar erscheinen.
Quelle: [Microsoft Q&A vom 10.02.2022](https://learn.microsoft.com/en-us/answers/questions/730741/using-azure-free-tier-without-creditcard)
— **vier Jahre alt, beim Anlegen gegenprüfen.**

## Aufträge

### 1 · Azure als Sprachausgabe einbauen, umschaltbar

- Neues Backend neben dem bestehenden. **edge-tts bleibt vollständig erhalten**
  und ist die Rückfallebene, wenn Azure nicht antwortet oder das Kontingent
  erschöpft ist.
- Umschaltbar über eine Einstellung, ohne Code-Eingriff.
- **Der Schlüssel gehört in die Geheimnis-Ablage**, nicht ins Repo und nicht in
  eine Datei im Arbeitsbereich.
- **Region: Deutschland West-Mitte** (`germanywestcentral`). Neural-Sprachausgabe
  ist dort verfügbar, belegt in der
  [Regionenübersicht](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions)
  mit Stand 16.09.2026. Dieselbe Seite sichert zu: *„Azure Speech doesn't store or
  process your data outside the region of your Azure Speech resource."*
  Nachrangige Wahl, falls die Stufe dort nicht anlegbar ist: Westeuropa oder
  Schweden Mitte.

### 2 · SSML für Sprachumschaltung und Zahlarten

- Englische Begriffe im deutschen Satz englisch sprechen (`<lang>`).
- Zahlarten ansteuern: Kennnummern ziffernweise, Mengen als Zahlwort, Uhrzeiten
  als Uhrzeit, Jahreszahlen als Jahr.
- **Prüffälle aus Adams vier Beschwerden** als Selbsttest hinterlegen: „800.000",
  „9290131", „2.000", „20:05 Uhr", „Python 3.12", „2019".
- Grenzen der Stufe, damit der Aufbau sie nicht überschreitet: höchstens 50
  `<voice>`- und `<audio>`-Elemente, 64 KB SSML je Vorgang, höchstens zehn
  Minuten Ton je Anfrage. Gilt in beiden Stufen gleich.

### 3 · Die sieben Umschreiber stilllegen, nicht löschen

`_normalize_doppelpunkt_zahlen`, `_tausenderpunkte`, `_number_ranges`, `_dates`,
`_jahreszahlen`, `_kennnummern`, `_versions` in `bot.py`.

**Sie bleiben im Code**, weil sie für die Rückfallebene edge-tts weiterhin
gebraucht werden. Sie werden übersprungen, solange Azure spricht. Ein Löschen
wäre ein Rückschritt, sobald Azure einmal ausfällt.

### 4 · Zweite Stimme für lokale Inhalte (Drehbuch 9.2)

Im selben Zug, weil es dieselbe Stelle im Code betrifft. **Die Anforderung ist
nicht die Qualität, sondern die Unterscheidbarkeit:** Adam am 25.08. — *„auch
zwei unterschiedliche Sprecher. Damit wird sofort klar, wenn etwas über Rot läuft
und wenn etwas grün ist."* Ein Hinweis zum Hören, nicht zum Lesen.

### 5 · Kostenriegel bei fünf Euro `[NEU 26.09.2026]`

Adams Auflage zur Freigabe. Zwei Teile, beide nötig:

- **Zählen im Code.** Die gesendeten Zeichen je Kalendermonat werden mitgeschrieben
  — dieselbe Zahl, die Azure berechnet, also nach dem Abzug von Markdown, Links
  und Codeblöcken. Der Zähler überlebt einen Neustart.
- **Abschalten bei Erreichen der Grenze.** Voreinstellung fünf Euro, umschaltbar
  ohne Code-Eingriff. Wird sie erreicht, fällt die Sprachausgabe auf edge-tts
  zurück und **Adam bekommt eine Meldung** — nicht erst beim nächsten Tagescheck.
- **Zwei Vorwarnungen** bei der Hälfte und bei achtzig Prozent, damit die
  Abschaltung nicht als Störung erscheint.
- Zusätzlich im Azure-Konto selbst eine Kostenwarnung setzen. Sie ersetzt den
  Riegel im Code nicht: Sie meldet, sie stoppt nicht.

### 6 · Die Ratengrenze behandeln `[NEU 26.09.2026]`

**S0 erlaubt 30 Vorgänge je Sekunde, F0 nur 20 je 60 Sekunden** (nicht
anpassbar). Unsere Sprachausgabe zerlegt lange Antworten in Abschnitte und sendet
sie hintereinander.

- **HTTP 429 wird abgefangen und wiederholt**, mit wachsender Wartezeit. Microsoft
  nennt in der Quotas-Seite ausdrücklich das Muster 1–2–4–4 Minuten für schwere
  Fälle; für unsere Abschnittslängen genügen Sekunden.
- **Nach der letzten Wiederholung Rückfall auf edge-tts**, nicht Abbruch.
- Ohne diese Behandlung **bricht eine Sprachnachricht mitten im Satz ab** — und
  zwar genau bei den langen Antworten, für die Adam die Sprachausgabe am meisten
  braucht.

## Was kann brechen und wer merkt es

| Fall | Folge | Wer merkt es |
|---|---|---|
| **Azure antwortet nicht** | keine Sprachnachricht | **Niemand** — deshalb Pflicht: Rückfall auf edge-tts und eine Zeile im Protokoll |
| **Kontingent erschöpft** | Kosten laufen still weiter | **Niemand** ohne Auftrag 5 — der Zähler ist der einzige Ort, an dem es auffällt |
| **Schlüssel läuft ab oder wird entzogen** | Sprachausgabe tot | wie oben, derselbe Wächter |
| **SSML falsch zusammengesetzt** | Azure weist ab, Text wird gar nicht gesprochen | ein Selbsttest mit den sechs Prüffällen |
| **Umschreiber doppelt aktiv** | Zahlen werden zweimal umgeformt, Ergebnis unsinnig | Selbsttest je Backend getrennt |
| **Region falsch gesetzt** | Text verlässt die EU | keine Anzeige — deshalb einmalig nachmessen und in der Ablage vermerken |
| **Ratengrenze erreicht** `[NEU]` | Sprachnachricht endet mitten im Satz | Adam beim Hören, **ohne Hinweis auf die Ursache** — deshalb Auftrag 6 |
| **Der Zähler in Auftrag 5 läuft nicht mit** `[NEU]` | Riegel greift nie, die Freigabe wird wirkungslos | **Niemand** — der Tagescheck braucht eine Zeile, die den Zählerstand ausweist |

**Die gefährlichste Klasse ist hier dieselbe wie immer: ein Ausbleiben, das wie
Ruhe aussieht.** Eine stille Sprachausgabe unterscheidet sich für Adam nicht von
einer abgeschalteten. Deshalb ist der Rückfall auf edge-tts Teil des Auftrags und
keine spätere Verbesserung.

## Was danach entfällt

- Der Punkt **9.1** im Drehbuch samt dem gesamten Zahlen-Themenkreis.
- Der dort geführte **Weg ②** (ein fertiges Normalisierungs-Regelwerk wie
  NeMo-text-processing oder `num2words`) wird nicht mehr gebraucht, wenn SSML die
  Unterscheidung trägt. **Er bleibt die Rückfalloption**, falls sich beim Bau
  zeigt, dass SSML einen Fall nicht abdeckt.
- Die offene Anweisung Adams vom 25.08. (*„das bitte rausstreichen und
  intelligenter lösen"*) ist damit erledigt.
