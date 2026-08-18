<!-- ROLLE: grundregeln -->
# CLAUDE.md — Projekt-Notizen

**Neu in einer Rolle?** → `WIEDERANLAUF.md` (ROLLE: `wiederanlauf`) setzt eine
neue Planungs-/Kontrollsitzung vollständig ein — Leseordnung, Rituale, Landkarte.

## 🗺️ MIGRATION — Status & Drehbuch

- **Das verbindliche Drehbuch ist `MIGRATION.md` (MASTER, zusammengeführt
  2026-07-12):** die 11-Phasen-Struktur aus der Telegram-Sitzung (Netcup-VPS,
  Status/Akzeptanz/Test/Adam-Bestätigung pro Punkt, sequenziell) + Phase 0
  (Code-/Repo-Vorbereitung), Anhang D (Ausführungsbefehle) und
  Kostenregel-Wächter aus dieser Sitzung. Die Repo-Version ist die Hoheits-
  Fassung; die Telegram-Sitzung übernimmt sie als Arbeitsdokument (Punkt 0.8).
- **Entscheidungen E1–E4 und F1 bestätigt** (Kasten in MIGRATION.md). F1:
  LiteLLM nur für Neben-Inferenzen (Ollama/Groq); der Claude-Agent bleibt
  direkt am Abo-SDK — keine Anthropic-Route in LiteLLM (Kostenregel!).
  Server-Zugangsdaten werden in Punkt 1.0 übermittelt/verifiziert.
- Wichtigste Stolperfallen: echte bot.py (~2000+ Zeilen) noch NICHT im Repo
  (Punkt 0.1, KRITISCH — Repo-Version ist veraltet); iCloud-Log-Pfad existiert
  auf Linux nicht (0.5); nie zwei Bot-Instanzen parallel; Webhook-Setzen (1.9)
  IST der Umschaltmoment; Auth NUR per Abo-Token (Kostenregel unten).
- Erledigt vorab: 401-Handling-Referenz + Abo-Token-first-Doku auf Branch
  `claude/telegram-bot-auth-401-g6yqrr`.

## 💰💰💰 KOSTEN-REGEL — HÖCHSTE PRIORITÄT 💰💰💰

**Die Warnpflicht gilt UNIVERSELL — für JEDE Art möglicher Extra-Kosten, egal
aus welcher Quelle** (Adam-Anweisung 2026-07-15):
- **API-/Token-Verbrauch** (Anthropic-API pay-per-token; `ANTHROPIC_API_KEY` statt Abo)
- **Werkzeug-Gebühren** (z. B. WebSearch ~$10/1000 Suchen)
- **Drittanbieter-Dienste** (Groq, Azure, Such-/Cloud-Dienste, …)
- **Abos / Grundgebühren**
- **Server-/Infrastruktur-Kosten**
- **Speicher- / Traffic-Kosten**
- **auch scheinbare Kleinstbeträge — Cent-Beträge zählen!**

**Vor JEDER Aktion, Tool-Einbindung oder Dienst-Einrichtung aktiv prüfen:**
> „Kann hierdurch irgendwo Geld abgebucht werden — jetzt oder später, einmalig
> oder laufend?"

**Falls ja ODER unklar → STOPP:** Kostenquelle + geschätzte Höhe nennen, Adams
**ausdrückliche Freigabe abwarten. „Unklar" gilt als „ja".**

Diese Prüfpflicht gilt für **alle Instanzen** und ausdrücklich **auch für die
Recherche-Tools der Sitzungen selbst** (z. B. WebSearch). **Neue Dienste/Tools
zuerst auf versteckte Zusatzgebühren prüfen** (wie bei Groq geschehen) —
**Abo/kostenfrei ist der Standard.**

### Hintergrund (Spezialfall Anthropic: zwei getrennte Geldtöpfe)
- **Max-Abo** (~100 €/Monat): Auth via OAuth / `claude login` /
  `CLAUDE_CODE_OAUTH_TOKEN`. Im Abo enthalten, **keine** Extra-Kosten.
- **API-Schlüssel** (`ANTHROPIC_API_KEY`): bucht **IMMER extra** ab,
  völlig getrennt vom Abo. Hat Vorrang vor OAuth, wenn gesetzt.
- **Standard-Auth für diesen Bot: Abo-Token (`CLAUDE_CODE_OAUTH_TOKEN`),
  NICHT `ANTHROPIC_API_KEY`.** Alles möglichst über das **Abo (kostenfrei)**,
  solange es nicht „professionell/produktiv" wird.

### AGB-Grenze des Abos — Automatik-Regel (Stand 07/2026, Primärquelle geprüft)

**Aktualisiert 23.07.2026** gegen die Primärquelle
`code.claude.com/docs/en/legal-and-compliance` (Abschnitt „Authentication and
credential use", via Strategie-Bericht `docs/entscheidungsvorlagen/
modell-plattform-strategie-bericht.md` A.2/D.1): OAuth-Auth ist „intended
exclusively … to support ordinary use of Claude Code and other native Anthropic
applications"; die Abo-Limits decken ausdrücklich „ordinary, individual usage
of Claude Code and the Agent SDK". **Verboten ist Drittanbieter-Routing** „on
behalf of their users" (seit 04.04.2026 auch technisch durchgesetzt, Sperrungen
„without prior notice"). **Unser Einzelnutzer-Eigenbetrieb über die offizielle
CLI/SDK ist die verträglichste Lesart — Restrisiko nicht null.** Der
AGB-Wachposten (5.21) überwacht die Legal-Seite auf Änderungen der
Auth-Passage. Als Bau-Leitplanke gilt:

- **Erlaubt (Abo):** mensch-initiierte Steuerung — Adam schickt eine Nachricht,
  daraus folgt ein Modell-Aufruf. Genau so arbeitet der Bot heute.
- **Grauzone bis Verstoß (Abo):** reine Zeit-Trigger, die ohne Adams Zutun
  regelmäßig Modell-Aufrufe auslösen („alle fünf Minuten Mails checken").
- **Konsequenz für zeitgesteuerte Routinen** (4-Uhr-Check 8.1, Erinnerungskanal,
  geplante Läufe): deterministisch bauen — Skripte ohne Modell-Aufruf — ODER
  bewusst auf API-Pay-per-Token legen; dann greift die 💰-Warnpflicht
  (Kostenquelle + Höhe + Adams Freigabe). Bei der Umsetzung von 8.1 ausdrücklich
  mitprüfen, ob der Erreichbarkeits-Check einen Modell-Aufruf enthält.

## ▶️ ARBEITSMODUS — Durchlauf ist der Normalfall (Adam 2026-07-25)

**Geprüft, bevor diese Regel entstand:** „Nächte arbeiten, Tage entscheiden"
regelt **wann** gearbeitet wird, nicht **ob nach einem Bericht angehalten wird**.
Die Lücke war echt, deshalb diese Ergänzung — und deshalb nur diese eine.

**Zwei Modi, am Anfang eines Auftrags zu benennen:**

- **Durchlauf (Vorgabe, wenn nichts gesagt wird):** Ich arbeite die Reihe
  selbstständig ab. **Ein Weitergabe-Block ist ein Meilenstein, kein
  Halteschild** — ich schreibe ihn und mache weiter. Alles, was Adams Zutun
  braucht, wandert **ans Ende** (bzw. seit 9.4 ins Freigabe-Postfach) und
  blockiert nichts davor.
- **Schritt (nur auf ausdrückliche Ansage):** Nach jedem Block halte ich an und
  warte auf Adams Zug. Sinnvoll, wenn er ohnehin am Rechner sitzt und
  zwischendurch steuern will.

**Warum die Vorgabe „Durchlauf" ist:** Sitzt Adam am Rechner, kostet ein
unnötiger Halt nur Zeit. Sitzt er **nicht** am Rechner, läuft die Sitzung leer —
und das ist der teurere Fehler, weil dann gar nichts geschieht. Anlass: Ich habe
am 25.07. nach dem 9.4-Block angehalten, obwohl ich hätte weiterarbeiten können.

**Umgekehrt gilt:** Auch im Durchlauf bleibe ich **aufnahmebereit**. Kommt
mitten im Lauf ein neuer Auftrag, wird er eingearbeitet, nicht aufgeschoben.

### Der Prüfer dazu — `durchlauf-wache.sh` `[NEU 2026-07-25, nach der dritten Erinnerung]`

Diese Regel stand hier und hat **dreimal nicht gegriffen**. Der Grund ist
strukturell und derselbe wie bei den vier anderen Fällen dieses Tages:
**`CLAUDE.md` wird beim SITZUNGSSTART gelesen, der Fehler passiert aber am
ZUGENDE** — dort feuert kein Dokument. Eine vierte Ermahnung hätte daran nichts
geändert.

Deshalb ein **Stop-Hook**: `.claude/hooks/durchlauf-wache.sh` liest
`.claude/laufplan.md` und **blockiert das Anhalten**, solange dort ein Punkt
offen ist — mit der Liste der offenen Punkte in der Meldung.

**Zwei Notbremsen, damit der Wächter nicht selbst zum Hindernis wird:**
`WARTET: ja` in der ersten Zeile des Laufplans hält ihn an (für Fälle, in denen
wirklich nur Adams Zug weiterhilft), und **nach zwei Blockaden in Folge lässt er
durch** — wenn zweimaliges Erinnern nichts bewirkt, liegt das Hindernis
woanders, und Festhalten macht es schlimmer.

**Pflicht daraus:** Der Laufplan wird **gepflegt** — Erledigtes sofort abhaken,
Neues anhängen. Ein Wächter, der einen veralteten Plan liest, ist schlimmer als
keiner.

## 🛡️ KONTROLLE WÄHREND DER ABWESENHEIT (Adam/Conni 2026-07-28, verbindlich)

Gilt vom 28.07. bis zur Rückkehr (~13.–15.08.), solange die Kontrollsitzung
nicht erreichbar ist.

**① Widerlegungs-Gegenprüfung je gebautem Punkt.** Jeder abgeschlossene Punkt
bekommt **vor dem Abhaken** eine Gegenprüfung durch eine **frische, getrennte
Sitzung** mit dem ausdrücklichen Auftrag: **„Finde, was daran nicht trägt"** —
nicht „prüfe, ob es stimmt". *Wer bestätigen soll, bestätigt.* Der Befund wird
committet. **Eine Gegenprüfung, die nie etwas findet, ist selbst der Befund.**

**①a Zwei Präzisierungen `[NEU 2026-07-28, Conni]`.** *Die Selbst-Widerlegung
beim Bauen zählt NICHT als diese Gegenprüfung* — sie ist derselbe Blickwinkel,
nur ehrlich. Auch ein Punkt, bei dem ich beim Bauen selbst einen Fehler gefunden
habe, bekommt die frische Sitzung mit Widerlegungs-Auftrag. Und: *Vor jedem
**Scharfstellen** (Zeitgeber starten, Wächter aktivieren) muss die Gegenprüfung
des betroffenen Punkts **vorher** gelaufen sein* — nicht am Blockende.
**Gebaut-und-ruhend darf warten; gebaut-und-wachend nicht.**

**② Nachlaufende Gesamtabnahme.** Nichts, was in der Abwesenheit entsteht,
erhält den Status **VERIFIZIERT** — höchstens **„GEBAUT (Abwesenheit, Abnahme
ausstehend)"**. Bis dahin gilt: **jeder Punkt einzeln committet, Rückweg
dokumentiert** — im schlimmsten Fall ist die Reparatur ein `git revert`, kein
Wiederaufbau.

**③ Der Deckel bleibt hart.** Nichts Neues, nichts mit root, nichts nach außen,
keine Kostenquelle, keine Architekturänderung. **Im Zweifel ist Liegenlassen
richtig** — eine geparkte Idee kostet nichts, eine ungeprüft gebaute kostet
Vertrauen.

## 😴 RUHEMODUS (Conni-Entscheid 2026-07-28 abends, gilt bis ~15.08.)

**Nur Wächter. Kein Bauen, kein Deploy, keine neuen Aufträge.** Der VPS bleibt
auf `6ed4b91`; alles vom 28.07. liegt geprüft und ruhend auf dem Mac und wartet
auf die Gesamtabnahme.

- **Der Kurier-Ordner wird gelesen, Neues wird GEPARKT, nicht gebaut.** Auch
  wenn es klein aussieht und der Lösungsweg klar ist — die Ausnahme für
  Wächter-Befunde aus dem Bauauftrags-Regime gilt hier **nicht** mehr.
- **Läuft ein Wächter rot: anhalten und melden schlägt reparieren.** Eine
  ungeprüfte Reparatur in einer Abwesenheit ist teurer als eine liegende
  Störung — niemand kann sie gegenlesen.
- **Zwei Entscheide, damit sie nicht erneut aufgeworfen werden:** Der
  Abo-Token wird **nicht** erneuert (ausgestellt 14.07.2026, Gültigkeit rund
  ein Jahr — gemessen; die C2-Sofortmeldung beim Kippen bleibt das Netz). Und
  Horas **Wiederholungs-Merkmal wird nicht gebaut** — „nichts Neues" gilt auch
  für uns; die Stundenblumen tragen die Dauerwache.

**Rückkehr-Punkt Nr. 3:** Die Rundenlisten-Idee gehört zur Entwicklungskette
und wird dort zusammen mit den `haengt_an`-Bezügen entworfen — Adams Gedanke
ist die Vorgabe dafür, nicht ein nachträglicher Anbau an Hora.

## 🎚️ MODELL- UND MODUS-AUTONOMIE (Adam 2026-07-28, dauerhaft und projektweit)

**Grundeinstellung: Opus 5, mittlere Denktiefe.** Innerhalb dieses Rahmens
gilt: **Das Werkzeug passt sich der Aufgabe an, nicht umgekehrt — selbsttätig.**

- **Runterschalten ist ausdrücklich erwünscht.** Mechanische Teilschritte
  (Umbenennen, Doku-Commits, Formatarbeit, Massenänderungen) dürfen an
  Unter-Sitzungen auf Sonnet gehen. **Sparsamkeit ist hier Qualität, kein Geiz.**
- **Denktiefe je Schritt selbst dosieren.** Heikle Einzelstellen — Eingriffe in
  Fehlerpfade, Änderungen, deren Bruch **wie Ruhe aussieht** — gründlich
  durchdenken; Routineschritte im Normalgang. **Kein Dauermaximum.**
- **Hochschalten auf Fable ist die Ausnahme**, nicht der Normalfall: nur bei
  erkennbarer Urteils- oder Entwurfstiefe (Architektur, Gesamtabnahmen, harte
  Widerlegungsprüfungen). **Vorher den Kontingentstand deterministisch prüfen** —
  kein Hochschalten nahe am Limit oder während einer Autonomiephase, in der das
  Kontingent die Maschine trägt. Und **als Unter-Sitzung, nicht als Dauerzustand.**
- **Sichtbarkeit:** Wurde etwas auf einem anderen Modell gebaut oder geprüft als
  dem eingestellten, steht das im Bericht — eine Zeile genügt. *Unsichtbar ist
  die Mechanik, sichtbar die Auswirkung.*
- **Adams Vorrang bleibt:** Sagt er „nimm X", gilt X. Die Autonomie füllt nur
  den Raum, in dem nicht entschieden wurde.

**Einordnung:** Das ist der Dirigenten-Gedanke im Kleinen — auf die eigene
Werkzeugwahl angewandt, **bevor** er als Architektur gebaut wird. Gilt sinngemäß
auch für **Hora** (dessen frische Sitzungen nehmen das jeweils kleinste
taugliche Modell) und für künftige Instanzen.

## 🌙 ARBEITSPRINZIP „NÄCHTE ARBEITEN, TAGE ENTSCHEIDEN" (Adam/Kontrolle 2026-07-23)

Automatisierbares läuft **bevorzugt nachts autonom**; Adams Tageszeit ist für
**Entscheidungen, Abnahmen und die Vorbereitung des nächsten Nachtblocks**
reserviert.

**Nacht = Präferenz, nicht Pflicht (Adam 24.07.):** Das Arbeitspferd darf
**tagsüber genauso voll durcharbeiten** — nicht „nur in kurzen Zügen". Nächte
sind bevorzugt, weil (a) Adam nicht verfügbar ist (lange kontrollfreie Läufe)
und (b) sie die Kontingent-Last über die 5-Stunden-Fenster verteilen. Aber bei
**Zeit + Kontingent tagsüber wird voll gearbeitet** — keine Zeit verlieren. Gilt
für alle Prozesse/Automationen. Regeln:

- **Schwere Blöcke früh in die Nacht** legen; bei Kontingent-Stopp Stand
  sichern und im nächsten Fenster bzw. nach Morgen-Anstoß nahtlos weiter.
- **Jeder Nachtblock endet mit einem Morgen-Bericht** (erledigt / geparkt /
  Fragen / heutige Adam-Aufgaben, max. 10 Zeilen).
- **Akzeptanzkriterien sind unantastbar** — bei Zeitnot wird hinten gekürzt,
  nie gepfuscht.
- Nach der Migration: wiederkehrende Läufe **serverseitig** verankern
  (Backlog „Cowork/Mac-Unabhängigkeit", Audit 9→10). Im Sprint bleibt der
  Mac nachts an.

### Kontingent-Ökonomie bei Nachtläufen (Adam-Nachtrag 23.07.)

Autonome Nachtblöcke laufen standardmäßig auf **normaler/mittlerer
Aufwandsstufe ohne Schnellmodus** — Durchhalten schlägt Klotzen: Ein Fenster,
das acht Stunden trägt, schafft mehr als eine Maximalstufe, die nach 90
Minuten leer ist. Stößt die Sitzung nachts auf eine Aufgabe, die erkennbar
eine höhere Stufe oder ein stärkeres Modell bräuchte (hartes Debugging,
Architektur-Abwägung): **Punkt parken** und im Morgen-Bericht mit Begründung
als **„Eskalations-Kandidat"** melden — Adam schaltet dann gezielt für diese
eine Aufgabe hoch (analog zur Park-Regel für Entscheidungsfragen).
Abweichungen vom Standard nur, wenn Adam sie **vor** einem Lauf ausdrücklich
festlegt. Gilt für alle künftigen Nacht-/Autonomie-Läufe.

## 🧠 SELBSTLERNENDE ASSISTENZ (Adam-Grundprinzip 2026-07-24)

Der Assistent lernt mit der Zeit Adams Vorlieben (Kategorisierung, Reihenfolge,
Formulierung) und **fragt/erfragt immer seltener** — „**Nachfragen ist
Startzustand, nicht Dauerzustand**". Am Anfang wird viel geklärt; je länger die
Zusammenarbeit, desto mehr entscheidet der Assistent im Sinne Adams von selbst.

**Einordnung (wichtig, klar trennen):** Das ist eine **Dienst-/Servicequalität**
— der Diener lernt, **besser zu dienen**. Es ist ein **Quermerkmal, das ALLE
Rollen hebt** (Butler, Coach, Ideengeber, Werkzeug …) und gehört **nicht der
Coach-Rolle allein**. Zwei verschiedene Lernrichtungen nicht vermischen:
- **Coach** = vermittelt dem Menschen Wissen (**lehrt** den Menschen).
- **Selbstlernen** = der Assistent verfeinert seinen **eigenen Dienst** (lernt
  **über** den Menschen, um besser zu dienen).

**How to apply:** Beobachtete Präferenzen als Memory/Regel festhalten und künftig
anwenden statt erneut zu fragen; bei Unsicherheit weiter fragen, aber die
Trefferquote über die Zeit erhöhen. Gilt interface- und rollenübergreifend. Für
das spätere Produkt (Momo) ist genau das ein Kernversprechen. Blaupause-Zeile
gesetzt.

## 🪄 UNSICHTBARE KOMPLEXITÄT (Adam-Grundprinzip 2026-07-24, hohe Priorität)

Eine der **Grundideen des ganzen Projekts** — von Anfang an mitzudenken, nicht
nebenbei. Der spätere Endnutzer (Maßfigur „Oma Lieschen": kann gerade einen
Messenger bedienen) bekommt von der dahinterliegenden Komplexität **nichts** mit
— keine Sitzungen, Chats/Protokolle, Drehbücher, Tool-/Modellnamen, APIs oder
Rechte-Verwaltung. Er interagiert mit **jemandem, der sich menschlich verhält**,
sagt, was er braucht — der Rest geschieht unsichtbar. **Das System sucht selbst
nach Lösungen**, statt Optionen und Limitierungen vorzutragen; Sätze wie „darauf
habe ich keinen Zugriff" oder „dafür fehlen mir Rechte" gehören **nie** in die
Endausbaustufe beim Kunden (es wählt selbst das passende Werkzeug/Modell, Vorbild
Perplexity/Manus).

**Blaupause-Zeile:** „Komplexität gehört dem System, Einfachheit dem Menschen."

**Ausnahme Entwicklungsmodus:** Zwischen Adam und mir sind technische Sichtbarkeit
und Entwickler-Schalter (`/spur`, `/technik`, Modell-/Effort-Knöpfe, Klartext-
Werkzeugspur) ausdrücklich erwünscht und bleiben — das ist die bewusste Ausnahme,
nicht der Normalfall für Endnutzer. Verzahnt mit „Selbstlernende Assistenz",
Kanal-Routing (ein Kern, mehrere Frontends → perspektivisch eigene App statt
Telegram-Pflicht) und der Werte-Charta (`docs/entscheidungsvorlagen/werte-charta-momo.md` §7).

## 🧪 PROBELAUF IM KLON (R4, 2026-07-25)

**Eingriffe mit Kettenwirkung werden zuerst in einem Klon geprobt, nicht am
laufenden Stand.** Gemeint sind Eingriffe, die mehrere Komponenten berühren oder
deren Rückweg selbst aufwendig ist — Fundament-Updates, Backend-Wechsel,
Umbauten an Sendepfad oder Persistenz, Systempaket-Sprünge.

**Ausdrücklich NICHT für Kleinkram.** Ein Tippfehler, eine Textzeile, ein
zusätzlicher Test brauchen keinen Klon; die Regel würde sich sonst selbst
entwerten, weil niemand sie mehr befolgt. Der Prüfstein: *Kann ich diesen
Eingriff in einer Minute rückgängig machen, ohne nachzudenken?* Wenn ja, kein
Klon.

**Wie:** `git worktree add ../probe-<name> <branch>` — eigener Arbeitsbaum,
eigene venv, dort bauen und den Regressionslauf fahren; erst danach im
Hauptbaum. Der Klon wird nach dem Lauf entfernt (`git worktree remove`), damit
keine Streu-Bäume liegen bleiben (die gab es schon einmal, sie wurden am 23.07.
mit aufgeräumt).

**Was der Klon NICHT ersetzt:** die Prüfung in der **echten Zielumgebung** (R1).
Ein Klon zeigt Syntax- und Logikbrüche, aber nicht die Umgebung des VPS — der
Fehlalarm des Start-Wächters kam genau daher.

## 🧹 ENTRÜMPELUNG — terminiert, nicht jetzt (R5, 2026-07-25)

`bot.py` ist auf **über 7000 Zeilen** gewachsen. Gesucht wird beim
Abschluss-Audit (Phase 10), **nicht zwischendurch**: tote Pfade aus revidierten
Entscheidungen · sich aufhebende Parameter · doppelte Regeln.

**Zwei harte Auflagen, weil Aufräumen die gefährlichere Art von Arbeit ist:**
Verschlanken **nur nach grünem Regressionslauf**, und **jede Streichung einzeln
testbar** — eine Aufräumaktion, die etwas mitreißt, ist schlimmer als der
Wildwuchs, den sie beseitigt. Kein Sammel-Commit „Aufräumen".

## 🧬 BLAUPAUSE-PFLICHT je Baustein (R6, 2026-07-25)

Je abgeschlossenem Baustein **eine** Zeile: **was gebaut · welche Kettenwirkung
geprüft · welche Nebenwirkung tatsächlich auftrat.**

**Der dritte Teil ist der wertvolle.** „Was gebaut" steht im Commit, „geprüft"
im Test — aber die tatsächlich eingetretene Nebenwirkung weiß nur, wer dabei
war, und sie ist nach einer Woche verloren. Beispiele aus diesem Projekt: dass
der Selbstcheck eine **zweite** Options-Stelle aufdeckte · dass die
Prozess-Zählung sich **selbst** mitzählte · dass die Ausschluss-Regel existierte
und nur nie **gemessen** wurde. Keine dieser Erkenntnisse stand in der Absicht.

**Zwischenschritte archivieren, nicht glätten:** Der Weg zum Ergebnis ist die
Lehre; ein rückwirkend geradegezogener Verlauf sieht kompetenter aus und trägt
weniger.

## 🪟 FENSTER-REGEL und GESCHWISTER-REGEL (Adam & Conni 2026-07-25)

**Jede Änderung, die einen Ablauf verlängert, vergrößert jedes Fenster, das in
diesem Ablauf offen steht.** Anlass: H1 hat den Medienpfad um Zerlegung und
Tonspur-Transkription verlängert — und damit ausgerechnet das Fenster
vergrößert, in dem eine Nachricht noch nicht gesichert war. Das Video von 05:07
fiel hinein. Die Verbesserung war richtig; übersehen wurde, dass sie eine
bestehende Lücke mit dehnt.

**How to apply:** Bei jeder Verlängerung eines Ablaufs fragen: *Was ist während
dieser Zeit ungeschützt?* Nicht „ist die Änderung gut", sondern „wovon liegt
jetzt länger etwas offen".

**Ein Fix an einem Pfad ist erst fertig, wenn geprüft ist, welche Geschwister
denselben Fehler haben.** Anlass: Der Voice-Pfad wurde am 20.07. abgesichert —
Fotos, Videos und Dateien blieben zurück und trugen den Fehler noch fünf Wochen.

**How to apply:** Nach jedem Fix die Schwesterpfade **benennen** (nicht nur
denken) und einzeln prüfen. Wo möglich, den Prüfer so bauen, dass er alle
Geschwister zugleich erfasst — die Selbstcheck-Zeile „Medien-Eingangsschutz"
prüft deshalb Foto, Video **und** Datei in einer Schleife.

## 🔧 FREMDES NEHMEN, WO ES NICHT ANS HERZ GEHT (Adam 2026-07-25)

**Ohne Sicherheits- oder Werte-Berührung: Vorhandenes nehmen und anpassen
schlägt Selbstbauen.** Mit solcher Berührung — Freigaben, Geheimnisse, Ampel,
Datenhoheit — **bauen wir selbst**, weil dort jede fremde Annahme eine ist, die
wir nicht geprüft haben.

**„Gut genug für jetzt" ist eine erlaubte Antwort**, solange zwei Dinge gelten:
der **Rückweg bleibt offen**, und der Punkt ist als **„später prüfen"
vermerkt** — sonst wird aus „für jetzt" stillschweigend „für immer".

## ⚖️ EINE REGEL, DIE NIEMAND BEFOLGEN KANN, IST SCHLECHTER ALS KEINE

Verallgemeinerung des R4-Prüfsteins. **Vor jeder neuen Regel prüfen:** Deckt
eine vorhandene den Fall schon ab? Und: Ist sie im Alltag befolgbar, oder
verlangt sie Aufmerksamkeit, die niemand dauerhaft aufbringt?

Wo eine Regel Aufmerksamkeit verlangt, gehört ein **Prüfer** dazu (R2) — sonst
ist sie eine Bitte. Wo kein Prüfer möglich ist, gehört die Regel **klein**
gehalten, damit sie überhaupt eine Chance hat.

## 🪟
## 🔬 BELEG-GRUNDSATZ — und das Auflösungs-Budget bei Bildern (2026-07-25)

**Eine Aufzählung von Belegen ist keine Beweisführung, solange nicht geprüft
ist, ob die Belege im Material überhaupt vorhanden sein können.**

**Anlass:** Ich habe ein Fahrzeug als „Renault Arkana — neun Merkmale, neun
Treffer, kein Widerspruch" bestimmt. Es war ein VW ID.5. Die eigene Nachmessung
danach: 67 Bildpunkte Fahrzeugbreite, ein Punkt ≈ 2,8 cm, das Emblem 4 Punkte,
der Schriftzug 10 Punkte breit und unter 1 Punkt hoch. **Die neun Merkmale
konnten physikalisch nicht existieren.** Das war keine Bestimmung, das war eine
Erzählung mit dem Anstrich einer Beweisführung.

Dritter Fall desselben Musters binnen vierundzwanzig Stunden — neben der
Kennzahl ohne Einheit (Echtzeit-Faktor ≠ Beschleunigung) und der als gültig
zitierten Momentaufnahme. Deshalb als Grundsatz, nicht als Bild-Sonderregel.

**Fünf Griffe bei Bildern:**

1. **Auflösungs-Budget vor der Behauptung.** Vor der Nennung eines Merkmals
   ausrechnen, wie viele Bildpunkte es einnimmt. **Merkmale unterhalb der
   Auflösungsgrenze existieren nicht** und dürfen nicht als Beleg auftreten —
   auch nicht abgeschwächt („könnte ein Schriftzug sein").
2. **Vergleichsmaterial in derselben Perspektive** — sonst vergleicht man
   Blickwinkel, nicht Objekte.
3. **Sicherheitsgrad benennen, nie Gewissheit behaupten.**
4. **Prüfen, ob das Merkmal überhaupt unterscheiden kann.** Bei ID.5 und Arkana
   liegen die Breiten-Höhen-Verhältnisse unter einem Prozent auseinander — die
   Silhouette war **strukturell untauglich**, nicht bloß knapp.
5. **Adams Anschauung schlägt die Rechnung**, wenn er das Objekt kennt.

**Der Weg statt des Ratens:** Überblick verkleinert, **Details als Ausschnitt in
Originalauflösung** nachreichen (`media.ausschnitt`) — und wenn auch das nicht
trägt, das ehrliche „das gibt das Bild nicht her".

## 🚧 EIN GESCHEITERTER WEG BEWEIST KEINE UNMÖGLICHKEIT (V, 2026-07-25)

**Bevor „geht nicht" gesagt wird, muss geprüft sein, ob es einen anderen Weg
gibt — und benannt werden, welcher genau gescheitert ist.** „Instagram geht
nicht" und „der Webseiten-Weg zu Instagram ist gesperrt" sind zwei verschiedene
Aussagen; nur die zweite ist wahr, und nur sie lässt die Frage offen, ob ein
dritter Weg trägt.

**Zweimal an einem Tag aufgetreten:** Instagram-Reels galten als gesperrt, weil
nur der Webseiten-Weg probiert war — die Medienschnittstelle liefert ohne
Anmeldung (gemessen: 80 Sekunden Tonspur in 21 Sekunden transkribiert). Und die
YouTube-Diagnose enthielt **zwei übereinanderliegende Hürden**, von denen eine
hausgemacht war (fehlende JavaScript-Laufzeit); erst nach deren Beseitigung war
die verbliebene Ursache überhaupt sauber zu benennen.

**How to apply:** Ein „geht nicht" trägt immer drei Teile — **welcher Weg**
probiert wurde, **woran** er scheiterte, und **welche Wege noch offen** sind.
Fehlt der dritte Teil, ist es keine Diagnose, sondern eine Aufgabe. Umgekehrt
gilt: Wenn wirklich alle geprüften Wege scheitern, ist **der ehrliche Fehlschlag
das Ergebnis** — kein Ersatzbau, der so tut, als ginge es doch.

## 💶 ERLÖSBEZUG MITPRÜFEN (W, 2026-07-25)

**Adams wirtschaftliche Lage ist ein gleichrangiger Grund, kein Nebenmotiv:
Einkommen ist Voraussetzung des Aufbaus, nicht sein Ergebnis.**

**How to apply:** Bei jedem Vorhaben mitprüfen, ob es auf Einkommen einzahlt
oder es verzögert. **Perfektionierung ohne Erlösbezug kostet unter diesen
Umständen Zeit, die nicht da ist** — das ist kein Verbot von Sorgfalt, sondern
eine Priorisierung zwischen zwei sorgfältigen Wegen. Verzahnt mit der
Coach-Haltung (Meta-Ebene, „wofür machen wir das gerade").

**Zum Ethik-Kompromiss beim Business-Start:** Bewährtes zuerst übernehmen, dann
verfeinern — mit **Protokollpflicht für jede bewusste Abweichung** (was, warum,
ab wann, und woran erkennbar ist, dass sie zurück kann). **Vorher aber prüfen,
ob der Zielkonflikt überhaupt besteht:** Beim Empfehlungsmarketing trägt der
Kern (Reichweite, Vertrauen, passendes Produkt); das ethisch Heikle ist meist
Beiwerk, das der Wiederkaufrate ohnehin schadet. **Kennzeichnung ist Gesetz,
nicht Feinschliff.**

## 🧪 WIRKUNGS-REGEL — nach jeder Filter-/Sync-Änderung das Ergebnis prüfen (2026-07-25)

**Nach jeder Änderung an einem Filter oder einem Abgleich wird geprüft, was
tatsächlich ankam — nicht, was die Konfiguration beabsichtigt.**

**Anlass:** Die Ausschluss-Regel für `CLAUDE.md` im Log-Abgleich **existierte** —
sie wurde nur nie nachgemessen. rsync nimmt die erste zutreffende Regel, die
Ausschlüsse standen hinter den Einschlüssen, und 146 KB Sitzungskontext wanderten
ins Log-Repo. Gefunden wurde es beim Gegenprüfen des ersten Laufs — das war
Sorgfalt, soll aber kein Glücksfall bleiben, sondern Verfahren.

**Vierter Fall derselben Klasse in zwei Tagen:** Register-Pflicht ohne Prüfer,
Vorlagen ohne Gültigkeits-Vermerk, Audit-Tor ohne Einholung, Filter ohne
Wirkungsprüfung. Das Muster ist immer: **Die Vorgabe war da, die Prüfung fehlte.**

**How to apply:** Ein Abgleich gilt erst als gebaut, wenn einmal geprüft wurde,
**was im Ziel liegt** — Dateiliste ansehen, nicht Konfiguration lesen. Wo möglich
zusätzlich eine Nachweis-Löschung oder Selbstcheck-Zeile, damit die Prüfung nicht
an Aufmerksamkeit hängt.

## 🛤️ ABLAGEWEG-GRUNDSATZ (Adam & Conni 2026-07-25)

**Eine Entscheidung, die keinen Weg in die Ablage hat, ist verloren — egal wie
klar sie getroffen wurde.**

**Anlass:** Der Gesamtdaumen für das Phasen-Audit war nie eingeholt worden, und
Adams erinnerte Zustimmung zum LobeChat-Ausbau stand nirgends im Drehbuch. Kein
Verfahrensfehler — es fehlte eine **Leitung**: Adam entscheidet häufig per
Reaktion oder Sprachnachricht im Bot-Chat, und die Bot-Sitzung darf nicht ins
Repo schreiben (8.7). Also blieb jede dort getroffene Entscheidung im
Bot-Gedächtnis liegen, bis ein Mensch sie übertrug.

**Dritter Fall derselben Klasse binnen vierundzwanzig Stunden:** erst fehlte der
**Prüfer** (R2 — eine Regel ohne Prüfer ist eine Bitte), dann der
**Gültigkeits-Vermerk** (⑪ — eine alte Fassung liest sich wie der gültige
Stand), jetzt der **Ablageweg**. Das Muster: Eine Vorgabe ohne technische
Entsprechung verfällt still.

**How to apply:**
- **Bei jeder neuen Regel, Rolle oder Entscheidungsart mitfragen:** Wer prüft
  sie? Wo wird sie sichtbar? **Und auf welchem Weg kommt sie in die Ablage?**
  Fehlt eine der drei Antworten, ist die Vorgabe unvollständig.
- **Solange 9.4 nicht steht**, trägt diese Lücke meine Aufmerksamkeit: Jede
  Entscheidung, die Adam im Bot-Chat trifft, muss ich beim nächsten Zug in
  `MIGRATION.md` nachtragen — mit geprüftem Zeitstempel. Nicht „später".
- **9.4 ist deshalb hoch eingeordnet:** nicht als Bequemlichkeit, sondern als
  die fehlende Leitung selbst.

## 🔍 PRÜFREGEL — Status ist ein Befund, keine Behauptung (Adam 2026-07-25)

Gilt für **alle Instanzen**. Ein Punkt gilt **nicht** deshalb als offen, weil
eine Status-Zeile „OFFEN" sagt — und **nicht** deshalb als fertig, weil ein
Bericht es behauptet. **Vor jeder Vorlage an Adam** ist zusätzlich zu prüfen:

1. **Changelog-Einträge seit dem letzten Statuswechsel** — dort steht oft, dass
   etwas längst entschieden oder gebaut wurde.
2. **Teilbauten und Zwischenschritte** — ein Punkt kann zu drei Vierteln stehen,
   ohne dass die Status-Zeile es weiß.
3. **Erfahrungswerte** aus Berichten, Bot-Protokollen und Weitergabe-Blöcken.
4. **Der Code selbst** — die letzte Instanz. Was dort steht, gilt.

Erst danach gilt eine Aussage. **Anlass:** `docs/AUDIT-STATUS-phase5.md` trug
keinen Überholt-Vermerk; vier längst entschiedene Punkte (6.6-Zimmer,
Webhook-Weg, Emoji-Ersatz, Log-Sync-Repo) galten dadurch weiter als offen.

### Gültigkeits-Kopf für jede Entscheidungsvorlage (Regel ⑪)

Jede Vorlage unter `docs/entscheidungsvorlagen/` trägt im Kopf: **Stichtag** ·
**„überholt durch X"** (oder ein ausdrückliches „—") · **„maßgeblich ist die
Status-Zeile im Drehbuch"**. Vorbildlich gelöst ist das bei der 6.6-Vorlage
(„v3 ersetzt v2 vollständig", mit Konfliktvermerk) und im
Reaktions-Vokabular (Änderungshistorie im Kopf). Ohne diesen Kopf liest sich
jede alte Fassung wie der gültige Stand.

## 🕒 FORMAT-REGEL — Zeitstempel im Kopf von Übergaben (Adam 2026-07-24)

Übergabe-Blöcke und Kontroll-/Sitzungs-Ausgaben tragen im **Kopf einen geprüften
Zeitstempel** im Format **`TT.MM.JJJJ, HH:MM`** — per `date`/Systemuhr **geprüft,
nie geschätzt** (Messbarkeits-Regel: Messbares wird gemessen, nicht erzählt).

**[VERSCHÄRFT 2026-07-25, Conni ③]: Die Blockzeit wird aus dem Commit
ÜBERNOMMEN, nicht getippt.** „`date` vor jedem Block" war richtig, hing aber
wieder an Aufmerksamkeit — derselben Schwäche, die den Versatz erzeugt hat (zwei
Blöcke lagen 14 bzw. 45 Minuten in der Zukunft). Der Blockkopf nennt ohnehin den
Commit, und **Commit-Zeiten sind maschinell und lassen sich nicht schätzen** —
an ihnen wurde der Versatz gemessen. Also:

```bash
git log -1 --format='%ad · %h' --date=format:'%d.%m.%Y, %H:%M'
```

Dieser Wert wandert unverändert in den Kopf. Gibt es keinen frischen Commit,
tritt `date` ein — dann aber ausgeführt, nicht erinnert. So kann die Zeit nicht
mehr driften: Sie ist dann ein **abgelesener** Wert, kein behaupteter.
Bei mehreren Blöcken kurz hintereinander gilt der mit dem **späteren
Zeitstempel**. Gilt für **alle Instanzen**, damit die Chronologie zwischen den
Sitzungen eindeutig bleibt.

## 🔗 BEZUGS-INTEGRITÄT — Abhängigkeits-Register (Adam-Anweisung 2026-07-16)

Schutz gegen stille Abhängigkeits-Brüche (das „Excel-`#BEZUG!`-Problem"): Eine
Komponente wird geändert/entfernt, und woanders bricht unbemerkt etwas, das
davon abhing. **Register: `ABHAENGIGKEITEN.md` im Repo** (Komponente → wird
benötigt von → Prüfbefehl).

1. **VOR jeder Änderung oder Entfernung einer Komponente** zuerst das Register
   prüfen: Wer hängt davon ab?
2. **DANACH die abhängigen Komponenten mittesten** (Prüfbefehl aus dem Register)
   — nicht nur das Geänderte selbst.
3. **Beim Bau neuer Features deren Bezüge SOFORT ins Register eintragen** —
   nicht auf später verschieben.
4. **Wo Abhängigkeiten nicht erklärbar sind, werden sie GEMESSEN statt
   aufgelistet.** [NEU 2026-07-25] Die Regel hat dreimal nicht gegriffen, und
   jedes Mal aus demselben Grund: Der Bruch lag in einer Abhängigkeit, die kein
   Register kennen kann. (a) Eine **Umgebungsvariable** (`ALLOWED_USER_IDS`
   erbte sich in Tests und legte den 12/14-Fehlalarm), (b) **transitive
   pip-Pakete**, die erst beim Installieren entstehen (unvollständiger
   Rollback), (c) eine **stille Versions-Divergenz** (Mac testete gegen SDK
   0.2.87, produktiv lief 0.2.127 — 40 Versionen Abstand, unbemerkt). Daraus
   zwei verbindliche Griffe: **Prüfläufe laufen in der echten Zielumgebung**,
   und Tests **erzwingen** ihre Umgebung hermetisch — nie `setdefault` für
   kritische Variablen. **Der Ist-Stand vor einem Eingriff wird vollständig
   eingefroren**, nicht bloß der geänderte Teil.

**Wächter statt Bitte (R2):** Die Selbstcheck-Zeile „Register-Vollständigkeit"
meldet jedes eigene Modul und jedes Betriebsskript, das keinen Register-Eintrag
hat. Eine Regel ohne Prüfer ist eine Bitte — sie fand beim ersten Lauf sofort
eine Lücke (`ampel.py`).

Verkabelt mit **8.1** (täglicher 4-Uhr-Check arbeitet die Prüfbefehle ab, meldet
Brüche per Telegram) und **8.2** (Regressionstest nutzt das Register als
Prüfliste nach Änderungen).

## 📈 AKTUALITÄT ALS QUALITÄTSKRITERIUM (Adam-Grundprinzip 2026-07-22)

**Kontinuierliche Verbesserung ist ein Qualitätskriterium des Systems selbst:
Aktualität wird überwacht, nicht erinnert.** Neue Errungenschaften (Modelle,
Komponenten, Verfahren) werden **systematisch** erkannt und eingepflegt — über
den register-basierten Update-Monitor (5.21) mit dem E5-Komponenten-Register
als Grundlage; das Register bleibt Pflichtfeld jeder „fertig"-Definition.
💰-Rahmen unverändert: Updates/Modelle nur aus dem Abo-/Kostenlos-Topf; alles
Kostenpflichtige nur mit Vorab-Warnung an Adam.

**[ERWEITERT 2026-07-25, Adam]: Es geht nicht nur um Versionsnummern, sondern um
VERFAHREN.** Für jede Fähigkeit, die wir bauen, gilt: **qualitativ möglichst
weit oben ansiedeln** und **wiederkehrend prüfen, ob es inzwischen einen
besseren Weg gibt** — das Feld entwickelt sich rasant und wird schneller.
Adams Beispiel war das Auslesen von Videos: heute Einzelbilder plus Tonspur,
morgen vielleicht ein Verfahren, das Bewegung direkt versteht.

Zwei Leitplanken dazu, die zusammengehören:
- **Was solide läuft, wird nicht über Bord geworfen, nur weil es Neues gibt.**
  Ein Wechsel braucht einen Grund, der über Neugier hinausgeht.
- **Aber Stillstand ist auch keine Option.** Der Prüf-Rhythmus gehört in den
  bestehenden Meldeweg (5.21) — für Verfahren wie für Pakete, **eine**
  Meldelogik. Wo sich etwas offline nicht ermitteln lässt, wird das im Register
  ehrlich als „manual" vermerkt statt eine Attrappe zu bauen.

Verzahnt mit „Selbstlernende Assistenz" und der Blaupause-Sammelpflicht.

## 🧭 STRUKTUR ÜBER NAMEN (Adam-Grundprinzip 2026-07-22)

Systeme referenzieren einander über **deklarierte Rollen/Muster**, nie
ausschließlich über konkrete Datei-/Pfadnamen; jede Referenz braucht einen
Suchweg, der eine Umbenennung überlebt. Konkret: Jedes Schlüsseldokument trägt
in der ersten Zeile (bzw. direkt nach der Frontmatter) den Marker
`<!-- ROLLE: <rollen-name> -->`. Startbestand: `master-drehbuch`
(MIGRATION.md) · `grundregeln` (CLAUDE.md) · `abhaengigkeits-register`
(ABHAENGIGKEITEN.md) · `blaupause-sammlung` (blaupause-notizen.md) ·
`wiederanlauf` (WIEDERANLAUF.md) · `reaktions-vokabular`
(reaktionen-vokabular.md). **Umbenennen/Verschieben eines Schlüsseldokuments
ist eine Abhängigkeits-Änderung:** im selben Commit Rollen-Marker mitnehmen,
ABHAENGIGKEITEN.md aktualisieren, Komfort-Namen in WIEDERANLAUF.md/CLAUDE.md
nachziehen. Gilt über Dokumente hinaus — Skripte, Backups, Hooks, künftige
Plattformen.

## 💾 LAUFENDE SICHERUNG — gilt für ALLE Instanzen (Adam 2026-07-22)

Nach jedem abgeschlossenen Arbeitsblock darf **nichts Entscheidungs- oder
Auftragsrelevantes ausschließlich in einem Chatverlauf existieren** — es wird
sofort externalisiert: Weitergabe-Block, Repo-Eintrag oder ausdrücklicher
„schwebt noch"-Hinweis an Adam. Damit ist jede Kontext-Verdichtung verlustfrei.
Mechanismus je Instanz: **Migrations-Sitzung** → Kontext-Kompass + MIGRATION.md
(besteht, s. u.) · **Web-/Planungs-/Kontrollsitzungen** → diese Regel ·
**Bot** → technische Sicherung (5.2, last-task, Memory; 5.24 ergänzt die
Rotation). Sitzungen **ohne Repo-Zugang sind nicht bindbar** — dort keine
Entscheidungsarbeit; Ergebnisse in eine angebundene Sitzung übertragen
(Zuständigkeits-Matrix unten).

## 🧭 Zuständigkeiten der Instanzen — ANTI-PING-PONG-REGEL

Der Nutzer arbeitet parallel mit mehreren Claude-Instanzen. Es ist passiert,
dass Instanzen ihn gegenseitig aneinander verwiesen haben („frag den Bot" ↔
„das gehört in die Desktop-Session"). Das darf nicht wieder vorkommen.

**Zuständigkeiten:**
- **Code-Sitzung am Mac** (Claude Code im Repo-Ordner): führt die Migration
  aus — Code, Git, Server-Arbeit, Status-Pflege in MIGRATION.md.
- **Telegram-Bot:** Alltagsaufgaben, Unterwegs-Nutzung, Permission-Freigaben.
- **Web-/Planungs-Sitzungen:** Drehbuch/Doku-Pflege im Repo; haben KEINEN
  Zugriff auf Mac oder andere Chats.

**Regel für JEDE Instanz:** Liegt ein Anliegen außerhalb der eigenen Rolle,
den Nutzer NIEMALS bloß weiterverweisen. Stattdessen: (1) selbst erledigen,
was mit eigenen Mitteln geht (Repo-Dateien lesen geht fast immer — MIGRATION.md
und CLAUDE.md im Repo sind die gemeinsame Wahrheit), (2) sonst dem Nutzer eine
FERTIGE Lösung mitgeben (exakte Befehle zum Selbst-Ausführen oder einen
fertigen Nachrichtentext inkl. Empfänger-Instanz) — nie nur „frag woanders".

**Frisch lesen vor Reden/Schreiben:** Vor jeder Aussage über oder jedem
Schreibzugriff auf geteilte Projekt-Dateien zuerst den frischen Stand aus
Repo/Dateien lesen — nie aus altem Sitzungsgedächtnis schreiben.

### 📌 Führungs-Register (pro Vorgang genau EINE führende Sitzung)

- **Vorgang „VPS-Migration" (aktuell): die Migrations-/Code-Sitzung am Mac
  führt.** Nur sie schreibt MIGRATION.md, CLAUDE.md und Code / pusht.
- **Alle anderen Sitzungen: NUR LESEN.** Änderungswünsche als Text an Adam
  bzw. an die führende Sitzung übergeben (fertiger Vorschlag, kein Direkt-Edit).
- **Führungswechsel nur ausdrücklich:** Dieser Registereintrag wird geändert
  und committet — erst danach schreibt die neue führende Sitzung.
- Durchsetzung: SessionStart-/PreToolUse-Hooks in `.claude/settings.json`
  (Warnbanner, Schreibschutz bei veraltetem Stand).

**Datenschutz-Hinweis Ampel-Regelpflege:** Heikelste Muster (z. B. Klienten-
Namen) NUR über den cloud-freien Weg eintragen — Telegram-Button-Dialog unter
`/ampel` oder Textbefehl `/ampel rot …` (beides wird deterministisch in bot.py
verarbeitet, ohne Claude-Beteiligung). Natürlichsprachige Pflege („nimm X als
Klient auf") ist erlaubt, läuft aber durch den Claude-Agenten (Cloud) — für
weniger heikle Begriffe okay, für das Heikelste den Button-Weg nutzen.

## Zusammenarbeit / Workflow (macOS, nicht-technischer Nutzer)

- **`pbpaste`-Befehle (Token/Key aus Zwischenablage):** Reihenfolge IMMER klar
  mitansagen → (1) Befehl ins Terminal einfügen **ohne** Enter, (2) **dann** den
  Token/Key kopieren (Doppelklick → `Cmd-C`), (3) **dann** Enter. Sonst
  überschreibt der eingefügte Befehl den Token in der Zwischenablage.
- **Ein Schritt pro Nachricht**, klar nummeriert. Kein `nano`/Hand-Editieren von
  Konfigdateien (zu fehleranfällig) — lieber per Befehl (`PlistBuddy` etc.).
- **Secrets nie in den Chat posten lassen** — vorher klipp und klar sagen.
- **Shell ist `zsh`:** KEINE `#`-Kommentarzeilen in Befehlsblöcken — zsh führt
  `#` interaktiv als Befehl aus („command not found: #"). Nur reine Befehle
  geben, Erklärungen außerhalb des Code-Blocks.
- **Deutsche Anführungszeichen sprengen Python-Einzeiler** (**6× passiert**,
  25.–28.07.): Ein Skript, das eine Zeile mit `„…"` per `t.replace("…„X"…")`
  sucht, bricht mit SyntaxError ab — das schließende `"` ist zugleich das
  Python-Stringende. **Regel: Dateien mit deutschen Anführungszeichen nur über
  Edit/Write ändern, nie über Inline-Python mit doppelt gequoteten Strings.**

  **`[VERSCHÄRFT 2026-07-28]` Der harmlose und der gefährliche Fall gehören
  getrennt** — die Regel hat dreimal an einem Tag nicht gehalten, aber nur eine
  der drei Verletzungen hat Schaden angerichtet:
  - **Harmlos:** Der SyntaxError kommt sofort, nichts ist geschehen, ein
    zweiter Anlauf genügt. Kostet eine Minute.
  - **Gefährlich:** `python - <<PY … PY && git commit …` — hier läuft der
    **Commit-Teil weiter, obwohl der Datei-Teil abgebrochen ist.** Der Commit
    ist durch, die Änderung fehlt still, und im Repo steht eine Nachricht, die
    etwas behauptet, das nicht darin ist. Genau so am 28.07. um 17:04.
  - **Daraus die eigentliche Auflage: `git commit` wird NIE an einen
    dateiändernden Heredoc gekettet.** Erst ändern, Ergebnis ansehen, dann in
    einem eigenen Aufruf committen. Das ist die Hälfte der Regel, die sich
    einhalten lässt, auch wenn man die andere gerade vergisst — und sie
    verwandelt den gefährlichen Fall zurück in den harmlosen.

  **`[KORRIGIERT 2026-07-28]` Die Regel hatte den Täter zweimal falsch
  benannt — und beide Male zu breit.** Erst hieß es „liegt am Werkzeug, nimm
  Edit/Write" — dann sprengte ein **frisch geschriebenes** `Write` genau
  daran. Dann hieß es „keine deutschen Anführungszeichen in Zeichenketten" —
  auch das war zu grob, denn `bot.py` enthält mehrere sauber gesetzte Paare,
  die nie etwas gebrochen haben.

  **Die tragfähige Fassung:** Der Bruch entsteht ausschließlich beim
  **gemischten Paar** — typographischer Öffner `„` und gerader Schließer `"`.
  Das gerade Zeichen beendet die Zeichenkette, der Rest der Zeile hängt in der
  Luft. Also: **typographische Anführungszeichen in Zeichenketten paarweise
  (`„…“`) oder gar nicht** — eckige Klammern (`[{wert}]`) tun in Meldungen
  denselben Dienst. In Docstrings und Kommentaren ist alles erlaubt.

  **Der Prüfer dazu** (`scripts/test_blinde_flecken_b6.py`, Zeile
  „kein gemischtes Anfuehrungspaar") meldet genau das Ungleichgewicht — ein
  breiterer schlüge dreimal täglich grundlos an und wäre binnen einer Woche
  abgeschaltet. **Lehre über die Regel hinaus: Wenn eine Regel wiederholt
  bricht, ist zuerst zu prüfen, ob sie die richtige Ursache benennt** — nicht,
  ob man sie strenger formulieren kann.

## 🔤 STICHWORT-FILTER: auf BEIDEN Seiten keine Wortgrenze

**`[KORRIGIERT 2026-08-18]` Diese Regel war in ihrer ersten Fassung falsch —
geschrieben von der Bau-Sitzung, abgenommen von der Kontrolle. Beide haben
denselben Denkfehler gemacht, und erst eine frische Gegenprüfung hat ihn
gefunden.**

**Gilt für jeden Textfilter, den wir bauen** — Ampel-Regeln, Rot-Bremsen,
Vorlese-Ausnahmen, Suchmuster.

Der Auslöser war „Klientendaten": `\bklient\b` traf es nicht. Die erste
Korrektur strich nur die **hintere** Wortgrenze — und verallgemeinerte damit
einen Einzelfall. Denn „Klient" steht in „Klientendaten" **zufällig vorn**; im
Deutschen steht das Grundwort dagegen **hinten**. Gemessen mit der halben
Korrektur, alle **ohne** Treffer:

> Serverpasswort · Zugangsschlüssel · Zugriffstoken · Systemschlüssel ·
> Bestandskunden · Datenbankpasswort

Das waren genau die Fälle, für die die Bremse gebaut wurde.

**Regel: keine Wortgrenze auf beiden Seiten** — `(klient|kunde|token)`, nicht
`\b…` und nicht `…\b`. Dasselbe gilt für die **Ausnahmeliste**: Auch dort
kostete ein schließendes `\b` sofort einen Treffer, weil „kostenlose" eine
Beugungsendung trägt.

**Der Preis sind Fehlalarme, und der ist nicht gratis.** „above" enthält „abo",
„Abort" enthält „abo", „kostenlos" enthält „kosten". Bei einer **Bremse** ist
das die richtige Fehlerrichtung — aber Rot heißt *Warten auf Adams Daumen*, und
in einer Abwesenheit heißt das *gar nichts*. Darum: offene Grenzen **plus** eine
kurze, ausdrücklich benannte Ausnahmeliste, die vor der Suche entfernt wird.
Eine lange Ausnahmeliste höhlt die Bremse aus; jede Zeile darin ist eine
Entscheidung, kein Automatismus.

Der Prüfer dazu: `scripts/test_auftragsbuch_b8.py`, Zeilen „rote Worte treffen
deutsche Zusammensetzungen" und „häufige harmlose Träger bremsen nicht" — beide
Richtungen gemessen.

## 🧪 VERHALTENS-PRÜFER: ausführen, nicht lesen (Conni 2026-08-18)

**Ein Prüfer, der nur Text sucht, prüft die Schreibweise — nicht die Wirkung.**
Kritische Pfade werden **ausgeführt**: Attrappen an den Rändern, echter Code in
der Mitte.

Belegt an einem Tag, dreifach:

- Eine AST-Regel verlangte `user_id=` an jeder Aufrufstelle und maß nur, **ob
  das Schlüsselwort dasteht**. Sie hat den schwersten Fehler des Projekts
  **erzeugt** (`NameError` im zentralen Sendepfad) und anschließend **gedeckt**.
- Ein Prüfer ersetzte die geprüfte Funktion durch eine Attrappe mit **genau der
  falschen Signatur, die der Fehler hatte** — damit war er per Konstruktion
  unsichtbar.
- Ein Wächter-Prüfer verlangte nur, dass ein Funktionsname im Text vorkommt.
  Entfernt man den **Aufruf** und lässt eine Kommentarzeile stehen, bleibt er
  grün und die Wache ist tot.

**Und die Zielumgebung ist die Prüfumgebung.** Der 29.07. war der Beweis: Ein
`$HOME` in einem Skript, das als root-Dienst ohne HOME läuft, tötete einen
täglichen Wächter einundzwanzig Tage lang. Am Mac lief alles.
`scripts/test_zielumgebung.sh` fährt deshalb `bash -n` über jedes Skript und
**startet** die zeitgesteuerten mit `env -i`.

**Zwei Regeln für den Prüfer selbst**, beide an einem Tag zweimal gebrochen:
Er darf **keine Formatierung verlangen** (Schreibweise offenlassen, Umfeld in
beide Richtungen lesen), und er darf **die Beschreibung seines eigenen
Gegenstands nicht anschlagen** — ein Prüfer, der über seinen Erklärkommentar
stolpert, wird binnen einer Woche abgeschaltet.

## 💵 KOSTENZAHLEN NUR MIT DEM WORT „NENNWERT" (Conni 2026-07-28)

`total_cost_usd` ist der Listenpreis, den dieselbe Arbeit über die API gekostet
hätte. **Gemessen über vierzehn Tage: rund 3400 Dollar, von denen nie einer
abgebucht wurde** — wir laufen über das Abo. Ohne das Wort daneben liest sich
die Zahl wie eine Rechnung und erschreckt irgendwann jemanden zu Recht.

Der Hinweis steht **am Ursprung** (`_record_usage`) und an jeder Anzeigestelle.
Ein Prüfer hält es fest: `scripts/test_blinde_flecken_b6.py`, Zeile
„Kostenzahl nie ohne das Wort Nennwert" — Gegenprobe gefahren.

## Remote-/Mobil-Weiterführung von Sitzungen (WICHTIG)

- Nutzer startet oft Prozesse, die Berechtigungen/Bestätigungen brauchen, muss
  dann weg → Prozesse stocken. Ziel: Sitzungen/Prozesse **von unterwegs
  fortsetzen** und **Freigaben erteilen** können.
- **Bereits möglich:** (a) Aufgaben, die **über den Telegram-Bot** laufen,
  schicken Permission-Prompts als Inline-Buttons (Allow/Deny/Always allow) aufs
  Handy — „Always allow <Tool>" verhindert wiederholtes Nachfragen. (b)
  Claude-Code-**Web**-Sitzungen lassen sich über die **Claude-App** (iPhone)
  fortsetzen — auch diese hier.
- **Wunsch (größere Sache, ggf. Migration):** Permission-Freigaben **beliebiger**
  Sitzungen gebündelt in den Telegram-Bot leiten, mit Sitzungs-Kennung, sodass
  alles per Telegram-Button freigegeben werden kann.

## Bot-Verhalten (bei Migration in `bot.py` einbauen)

- Der Telegram-Bot darf **nicht annehmen, in welchem Kontext der Nutzer gerade
  sitzt** (z. B. „schön, dich am Desktop zu sehen"). Der Nutzer ist parallel an
  mehreren Geräten/Sitzungen; eine solche Annahme ist irreführend. Begrüßungen
  und Antworten **neutral** halten. Umsetzung: kurzer Zusatz im System-Prompt
  des Bots (`bot.py`, `ClaudeAgentOptions`), z. B. „Du bist ein Telegram-Bot;
  nimm nicht an, wo oder an welchem Gerät der Nutzer sitzt."

## 🪞 DOKU-SPIEGEL — nutzerseitige Texte im SELBEN Commit (Adam 2026-07-19)

**Jede Feature-Änderung aktualisiert ihre nutzerseitigen Texte im selben
Commit** — `/hilfe`, `/start`, Startnachricht, Button-Beschriftungen,
`setMyCommands`. Kein „mach ich gleich noch".

**Warum:** Am 17.07. wurde die Tastatur von 12 auf 9 Buttons verschlankt, der
`/hilfe`-Text blieb stehen — der Bot beschrieb Adam ein Layout, das es nicht
mehr gab (gefunden erst am 19.07. bei einer Video-Analyse; es waren am Ende
gleich drei Abweichungen plus zwei fehlende Befehle). Diese Drift ist tückisch,
weil sie **nichts kaputt macht** und deshalb in keinem Test auffällt — sie
untergräbt still das Vertrauen in jede Auskunft des Bots.

**Gilt auch für Status-Quellen:** Was der Bot beim Start als „noch offen"
meldet, kommt aus `~/.claude/memory/pending-items.md` **auf dem VPS** — auch das
ist ein nutzerseitiger Text. Erledigtes dort abhaken, sonst begrüßt der Bot mit
einem veralteten Projektstand (genau so mit 4.1/8.5 passiert). Automatische
Absicherung folgt mit Punkt **8.6** (Prüfskript `check_hilfe_buttons.py`).

## 🧬 BLAUPAUSE-SAMMELPFLICHT — Teil der „fertig"-Definition (Adam 2026-07-19)

Entsteht bei einem Punkt ein Mechanismus oder eine Regel, die erkennbar
**übertragbar** ODER erkennbar **plattformgebunden** ist, kommt **sofort** eine
Zeile nach `blaupause-notizen.md` — Format `Was · Punkt-Nr. · Einschätzung`
(universell / anpassbar / plattformgebunden). Keine Ausarbeitung, nur die
Inventur-Zeile; ausgearbeitet wird erst mit Punkt **9.6** nach dem Gesamtaudit.

Das ist **fester Teil der „fertig"-Definition jedes Punkts** — analog zum
Abhängigkeits-Register. Nachträgliches Sammeln funktioniert nicht: Die
Einschätzung „warum haben wir es so und nicht anders gebaut" ist genau dann
präsent, wenn die Entscheidung fällt, und danach nie wieder.

## 📊 STATUSÜBERSICHT — festes Format (Adam 2026-07-19)

Statusberichte an Adam folgen dem Format **„Migrations-Inhaltsverzeichnis"**:

- Tabelle(n) mit **einer Zeile pro Punkt**, jeweils in **Kurzsatz-Form**
  (kein Stichwort-Telegramm, kein Absatz).
- Symbole: **✅** fertig · **🔄** läuft/teilweise · **⬜** offen ·
  **⏭️** bewusst zurückgestellt.
- Je Phase ein **Fertigstellungsgrad in Prozent nach Arbeitsumfang**,
  nicht nach Punktzahl (zehn Kleinigkeiten sind nicht mehr als eine Migration).
- Ein **gewichteter Gesamt-Prozentwert**.
- Am Schluss die **Liste offener Entscheidungen und Wartepunkte**.

Gilt für spätere Migrations-Stände **und künftige Prozesse gleichermaßen**.

## 🔒 GOVERNANCE — der Bot editiert sein eigenes Repo NIE (Adam 2026-07-19)

Die Regel „Bot editiert das Bot-Repo nicht" gilt **ausdrücklich auch für die
VPS-Kopie `/home/claudebot/claude-telegram-bot`**: **lesen ja — editieren,
committen oder pushen niemals.** Deploys laufen **ausschließlich** über
`git pull`, ausgelöst von Adam.

**Warum:** Ein Selbst-Edit auf dem VPS lässt Repo-Stand und laufenden Code
auseinanderlaufen; der nächste `git pull` kollidiert dann oder überschreibt
stillschweigend Handarbeit. Details + technische Verankerung: Punkt **8.7**.

**[GEÄNDERT 2026-07-24] — Lesen wiederhergestellt (Adam-Entscheid, keine
Aufweichung):** „Lesen ja, schreiben nie" heißt jetzt technisch, was es sagt.
Der frühere Zustand übererfüllte die Governance — auch `ls`/`cat`/`git log`/
Read fielen in den Freigabe-Dialog und waren für die Bot-Sitzung praktisch
gesperrt. Neu: **Lesen/Auflisten von Code, Doku, Skripten, Logs ist FREI**
(Read/Grep/Glob im Repo-Verzeichnis + einzelne, verkettungsfreie Bash-Lese-
Befehle). **Unverändert ZU (Vier-Augen-Prinzip):** Schreiben/Committen bleibt
dreischichtig gesperrt (Callback-Deny Edit/Write + `_is_repo_write_cmd` für Bash
+ pre-commit-Blocker im VPS-Klon), und **Geheimnis-Pfade** (`.env`,
`/etc/claude-telegram-bot.env`, credentials, token/secret/key-Dateien) bleiben
**auch fürs Lesen gesperrt**. Selbstcheck „Repo NUR-LESEN (8.7)" prüft alle drei
Wege (Lesen offen · Schreiben zu · Geheimnis zu).

## 🧠 Kontext-Kompass bei dieser (langen) Migration — FESTER RHYTHMUS

Vereinbarung mit Adam (2026-07-16): Diese zusammenhängende Migration in **einer**
Sitzung weiterführen, **nicht** in Zweit-Sitzungen aufspalten (`/clear` = Neustart
bei null, `/resume` lädt den ganzen Verlauf zurück — kein Zwischenweg). Der
Kontext-Rhythmus ist ab jetzt fest:

1. **VOR jeder neuen Phase** (oder sobald der Kontext knapp wird): gesteuert
   verdichten mit `/compact focus on <die offenen, jüngsten Punkte>` — **nicht**
   aufs automatische Verdichten warten. So bleibt der Fokus auf dem noch
   Unabgeschlossenen scharf; das Erledigte wird eingedampft.
2. **NACH jeder Phase und VOR jedem Verdichten:** den Stand in `MIGRATION.md`
   zurückschreiben. Das ist das verdichtungssichere Langzeitgedächtnis —
   `CLAUDE.md`, `MIGRATION.md` und `MEMORY.md` werden bei jeder Verdichtung ohnehin
   frisch neu eingespielt, die Gesprächs-Historie dagegen komprimiert.
3. **Große Lese-/Rechercheaufgaben** (Logs, Configs, Audits) an **Subagenten**
   delegieren — sie lesen in eigenem Kontext und liefern nur die Zusammenfassung
   zurück, der Hauptkontext bleibt schlank.

Hinweis zur Ehrlichkeit: Ein echter Auto-Trigger, der `/compact` von selbst mit
sinnvollem Fokus auslöst, ist technisch nicht machbar (braucht inhaltliches
Urteil). Diese Regel steht bewusst **hier** in `CLAUDE.md`, weil sie so bei jedem
Sitzungsstart und nach jeder Verdichtung neu präsent ist. Details:
Memory `strategy-context-management-large-sessions`.
