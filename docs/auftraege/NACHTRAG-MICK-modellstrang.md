<!-- ROLLE: nachtrag-modellstrang -->
# Nachtrag: der Modell- und Alternativmodell-Strang hat keinen Ort

**Kopf:** 31.08.2026, 08:44 (Systemuhr abgelesen) · Kontroll-Sitzung
**Gemessen an:** `origin/mac-produktivstand` @ `717b059` (und gegengeprüft an
`fb6bc6f`, meinem Audit-Stand)
**Anlass:** Adams Frage heute früh — *„mir fehlen die weiteren Prüfstellen bzw.
das Aufsetzen des lokalen KI-Systems"*

---

## Was es gibt, damit niemand doppelt baut

**Das lokale KI-System steht im Drehbuch und ist im Kern fertig.** Phase 2,
sieben Punkte, seit dem 15./16.07.:

| Punkt | Sache | Status |
|---|---|---|
| 2.1 | LiteLLM-Proxy (systemd, 127.0.0.1:4000) | VERIFIZIERT |
| 2.2 | Datenschutz-Ampel als Gatekeeper | LÄUFT (Beobachtung) |
| 2.3 | **Lokales Fallback-Modell — Ollama + Phi-4-Mini** | VERIFIZIERT |
| 2.4 | Groq als Cloud-Fallback | bewusst übersprungen |
| 2.5 | Kein OpenAI im Stack | VERIFIZIERT |
| 2.6 | Neben-Inferenzen auf LiteLLM | LÄUFT |
| 2.7 | SearxNG (kostenfreie private Suche) | VERIFIZIERT |

**Das ist in meiner Übersicht mitgezählt** (Phase 2: 71 %). Adam hat es nicht
übersehen, und ich habe es nicht weggelassen. **Aber das ist die Aufsetzung —
und er fragt nach etwas anderem.**

---

## ① Der Gegenleser hat keinen Punkt — und das ist mein Versäumnis

**Gemessen:** `gegenleser.py`, **267 Zeilen**, gebaut am 29.08., mit
ROLLE-Marker, eigenem Prüfer (`scripts/test_gegenleser.py`, 39 Zeilen) und einem
vollständigen Register-Eintrag. **Erwähnungen in `MIGRATION.md`: eine** — und
die steht in einer Changelog-Zeile, nicht in einem Punkt. **Kein `### N.N`
trägt seinen Namen.**

**Warum das schwerer wiegt als die anderen Bausteine ohne Eintrag:** Sein
Register-Eintrag trägt eine Kostenauflage.

> 💰 **Vor dem ersten echten Aufruf: Ausgabenlimit BEIM ANBIETER**
> (10/10/5 EUR, Deckel 30 — Adams Entscheid 28.08.), dann ZDR, dann Rauchtest.

**Ein Baustein, der Geld kosten kann, steht außerhalb des Plans.** Die
Kostenregel ist die höchstrangige Regel dieses Projekts; ihr Gegenstand hat
keinen Ort, an dem sein Stand geführt wird.

**Mein Fehler, gegengeprüft:** Bei `fb6bc6f` existierte `gegenleser.py` bereits
mit 267 Zeilen und hatte auch damals genau eine Erwähnung. **Er gehörte in meine
Liste der fünf Bausteine ohne Drehbuch-Eintrag und stand nicht darin.** Ursache:
Mein Raster suchte **Dateinamen**; wo ein Punkt die Sache unter anderem Namen
führt (5.14 Link-Inbox für `linkinbox.py`), habe ich von Hand nachgesehen und
dabei den Fall übersehen, der **weder** Dateiname **noch** Sachbegriff trägt.

**Konsequenz für das Audit 10.1:** Die Liste der Bausteine ohne Eintrag ist
**neu zu erheben, nach Sache statt nach Dateiname.** Meine Zahl fünf ist in
ihrer Zusammensetzung falsch.

**Was du tust:** Dem Gegenleser einen Punkt geben. Nummer schlägst du vor,
Phase 9 liegt nahe (er ist Kontroll-Werkzeug, nicht Alltagsfunktion). In den
Punkt gehören **Status „GEBAUT, NICHT SCHARFGESTELLT"** und die 💰-Auflage
wörtlich — sie darf nicht nur im Register stehen.

---

## ② Der Strategie-Bericht liegt unter „Hermes Agent" begraben

**Gemessen:** `docs/entscheidungsvorlagen/modell-plattform-strategie-bericht.md`
— 22.842 Zeichen, dazu eine PDF-Fassung. **Erwähnungen im Drehbuch: eine.** Sie
steht als Unterpunkt in:

> `### 9.7 Hermes Agent (Nous Research) — Evaluation als mögliche Agent-Plattform`

**Das ist der Ablage-Defekt, nach dem Adam gefragt hat, und er ist der Grund,
warum er es nicht finden konnte.** Der Bericht ist die Quelle, auf die sich
`CLAUDE.md` in der gesamten AGB-/Auth-Analyse stützt (Abschnitt A.2/D.1). Er
behandelt Modell- und Plattformstrategie im Ganzen. **Abgelegt ist er als Fußnote
unter einem Punkt, der die Bewertung EINER einzelnen Plattform betrifft.**

Wer im Drehbuch nach „Modellstrategie" sucht, findet nichts. Wer nach „Hermes"
sucht, findet alles. **Das ist kein Schreibfehler, sondern ein falscher Ort.**

**Was du tust:** Den Verweis aus 9.7 herauslösen und an einer Stelle
unterbringen, die nach der Sache benannt ist. **Den Zuschnitt entscheidest du
nicht** — siehe ③.

---

## ③ Was Adam entscheiden muss, nicht du

**Die Kapazität „zweiter Weg für alles" hat keinen Drehbuch-Punkt.** Das
Fähigkeitsraster führt sie als eigene Zeile:

> „Zwei Wege für alles (Ausfallsicherheit) | 🔄 | Stufe 1 in Arbeit; lokales
> Modell steht (2.3)"

Phase 2 deckt sie **nur für die Neben-Inferenzen** ab — 2.3 und 2.4 sind
Fallbacks für Ampel, Labels, Zusammenfassungen. **Für den Hauptagenten gibt es
keinen zweiten Weg und keinen Punkt, der einen fordert.**

Das ist dieselbe Klasse wie die Momo-Papiere: **Ein Arbeitsfeld ohne Ort wird
nicht abgearbeitet.** Und es ist dieselbe Art Entscheidung — *wo bekommt der
Strang seinen Platz?* Phase 2 erweitern, oder eine eigene Phase.

**Das gehört Adam.** Bitte nicht ableiten, nicht vorwegnehmen, keinen Punkt
erfinden. **Melden und die Frage vorlegen** — sie steht ohnehin schon neben der
Einkommens-Frage auf seinem Zettel.

---

## Reihenfolge und Grenze

**① vor ②**, beides Ablage-Arbeit, zusammen unter einer Stunde. **③ gar nicht** —
nur vorlegen.

**Gut genug wenn:** Der Gegenleser hat einen Punkt mit seiner 💰-Auflage im
Wortlaut, der Strategie-Bericht ist aus 9.7 herausgelöst, und Adam hat die eine
Frage aus ③ schriftlich vorliegen. **Nicht mehr.**

---

## Und zu deinem Morgen-Bericht, weil es hierher gehört

**F-9 hast du zu Recht zurückgewiesen.** Mein Auftrag lautete, `_ist_suchwerkzeug`
an den fehlenden Stellen nachzuziehen — du hast gemessen, dass genau das die
Kostenschranke gebrochen hätte. **Das ist der zweite Auftrag von mir binnen zwei
Nächten, dessen Ausführung Schaden angerichtet hätte** (der erste war Rang A,
seit zwei Tagen fertig).

Beide Male war die Ursache dieselbe: **Ich habe eine Notiz über den Code für den
Code gehalten.** Bei F-9 stand „an 1 von 3 Stellen benutzt" in der F-Liste; ich
habe die Stellen gezählt und **nicht geprüft, was an ihnen hängt.** Die
Entscheidungsregel aus der ersten Freigabe — *Befund gekippt → nicht bauen* —
hat beide Male getragen. Sie bleibt in Kraft für alles, was ich dir schicke.

**F-16 gehört Adam**, da stimme ich dir zu: Ob Hora ein Vorschlagender wird
statt ein Läufer, ist eine Architekturentscheidung. Sie steht mit auf seinem
Zettel.
