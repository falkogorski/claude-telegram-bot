<!-- ROLLE: bauauftrag-gestalten-erzeuger -->
**Stichtag:** 2026-08-24 · **ueberholt durch:** — · **massgeblich ist die
Status-Zeile in `MIGRATION.md`** · **Status: OFFEN, Bau am 25.08.**

# BAUAUFTRAG — Der Gestalten-Erzeuger (Rang 0 des Mail-Umbaus)

**Von:** Engywuck · **An:** Mick · **Stand:** 24.08.2026, gegen `1817c86`
**Grundlage:** Studie mit 11 Agenten — 1 Bestandsmessung, 3 unabhängige
Erzeuger-Entwürfe, 6 Widerlegungen, 1 Synthese. Ein Entwurf trug.

---

## DER BEWEIS, den ich selbst nachgemessen habe

Eine **völlig gewöhnliche** Mail, mit `EmailMessage` gebaut wie jedes
Mailprogramm sie baut, mit einem `display:none`-Block darin:

```
verborgen = []                       ← die Anweisung gilt als nicht versteckt
sichtbar  = '--===============614…==\r\nContent-Type: text/plain; …'
                                     ← MIME-Schutt als "sichtbarer Text"
```

**Die Erkennungsseite hat nicht Lücken — bei normaler Post arbeitet sie
nicht.** Elf Zeilen genügen für den Nachweis. Genau deshalb war der alte
Korpus grün: Er enthält keine einzige Mail dieser Bauart.

---

## GUT GENUG WENN

Der Erzeuger steht, läuft als **eigener Befehl** (nicht im Regressionslauf),
und liefert die Liste, gegen die repariert wird. **Ein Block. Dann Schluss** —
die Reparatur ist der nächste Auftrag, nicht dieser.

**Das Verhältnis ist Absicht: 1 Block Prüfer zu 3–4 Blöcken Reparatur.** Das
ist die Umkehrung des Musters, das die Kurs-Regel ausgelöst hat.

---

## WAS GEBAUT WIRD

**`scripts/mailgestalten.py`.** Nur Standardbibliothek: `email`,
`xml.etree.ElementTree`, `unicodedata`, `encodings.aliases`, `itertools`,
`re`, `ast`. Kein Netz, kein Konto, kein Schlüssel, kein Modell im Pfad.
**Kosten: null, geprüft nicht geschätzt.**

### Die Achsen — und woher jede kommt

| Achse | Quelle | Werte |
|---|---|---|
| Aufbau | `dir(EmailMessage)` → die `add_*`-Verben | plain, alternative, mixed, related-in-alt |
| CTE | `email.encoders` | 4 |
| Zeichensatz | `encodings.aliases` | 98 kanonisch, 90 mit ASCII-Marke baubar |
| Anhangsart | `mimetypes.types_map` | 1201 |
| Zeichenklasse | `unicodedata.category` | 163 Cf · 65 Cc · 17 Zs |
| **Leere Elemente** | **`mailtext._STUMM ∩ ET.HTML_EMPTY`** | **`{link, meta}`** |
| Verbergungsart | `mailtext._UNSICHTBAR_STIL`, `hidden`, `alt`/`title` | aus dem eigenen Code |
| Attributform | HTML-Syntax, geschlossen | mit Wert · leer · **ohne Wert** |
| Marken-Platzierung | relativ zu einem Kind, geschlossen | vor · im · **nach** dem Kind |

**Die `_STUMM ∩ HTML_EMPTY`-Zeile ist der eleganteste Fund der Studie**, und
ich habe sie nachgemessen: `ET.HTML_EMPTY` führt 17 Leerelemente als
Stdlib-Menge. Damit ist „schreibt man `<meta …>` oder `<meta …></meta>`?"
**keine Handentscheidung mehr, sondern eine Mengenoperation** — und genau
daran hing Befund 1.

### Die Entnahme — sie ist der Kern

```python
roh = msg.as_bytes(policy=policy.SMTP)
koerper = roh.split(b"\r\n\r\n", 1)[1]        # das IST BODY.PEEK[TEXT]
mailtext.lesbar(koerper.decode("utf-8", "replace"))
```

Damit sieht der Prüfer den **rohen, undekodierten MIME-Rumpf** — die Schicht,
die der alte Korpus in **0 von 23** Dateien kennt.

### Die sechs Orakelzeilen

| # | Zusage | fängt |
|---|---|---|
| a | **Seitentreue, gerichtet**: `S<n>` muss in `sichtbar` und nicht in `verborgen`; `V<n>` umgekehrt | 1, 2, 4, 5 |
| b | **Kein Notpfad**: „Auszeichnung nicht lesbar — Rohtext" darf nie erscheinen | 3 |
| c | **Kein Schutt**: kein Byte aus dem Kopfbereich der gebauten Nachricht in `sichtbar` | 5, 6 |
| d | **Gegenrichtung**: Gestalt ohne gepflanztes Versteck ⇒ `verborgen == []` | Fehlalarm-Bremse |
| e | **Berichtsgrammatik**: kein `bericht()`-Marker erscheint öfter, als `bericht()` ihn erzeugt | 7 |
| f | **Zeichenklassen**: kein gepflanzter Cf/Cc/Zs-Punkt erreicht die Ausgabe unersetzt | 9 |

**Zeile a ist GERICHTET, nicht als Erhaltungssatz.** Gemessen: Der
ODER-Satz („Marke steht in sichtbar *oder* verborgen") ist bei B4-umgekehrt
und bei `<div hidden>` **grün**. Gerichtet ist er bei beiden **rot**. Das ist
der Unterschied zwischen einem Prüfer und einer Beruhigung.

**Zeile d ist die, die man vergisst** — ohne sie belohnt der Prüfer
Übermelden.

---

## DREI AUFLAGEN, die keine Zeit kosten

1. **NICHT in `scripts/regressionstest.sh`**, bis die Fixes durch sind. Der
   Erzeuger ist ab Tag eins rot; im Regressionslauf blockierte er jeden
   Commit oder erzwänge eine Liste bekannt-roter Gestalten — **genau die
   Handauswahl, gegen die er antritt, nur mit Freibrief.**
2. **Registereintrag und Blaupause-Zeile im selben Commit.**
3. **Regressionslauf vor dem Commit** — auch vor einem Messwerkzeug. Genau
   diese Ausnahme hat am 23.08. zwei rote Zeilen auf dem VPS erzeugt.

---

## WAS DER ERZEUGER FÄNGT — acht von elf

Von selbst gefangen, jeweils am echten Modul gemessen: **1** (`<meta>`),
**2** (B4 umgekehrt), **3** (wertloses Attribut), **4** (`<div hidden>`),
**5** (roher MIME-Rumpf — 180 von 180 rot), **6** (Dateiname + Nutzlast),
**7** (gefälschte Gliederung), **9** (Bidi).

**Der ehrliche Rest, drei Stück:**

- **8 · Phantom-Anhänge** aus dem BODYSTRUCTURE-Ausdruck. Der Erzeuger baut
  Mails, kein IMAP. Eine BODYSTRUCTURE selbst zu formulieren wäre eine
  handgeschriebene Zweitimplementierung eines Formats — **dieselbe Falle eine
  Etage höher.** Eigener kleiner Block, dann mit dem einen mechanischen
  Orakel: *gemeldete Anhangszahl == gebaute*.
- **10 · Buchhaltungsnotiz vs. echtes Versteck.** Rangfrage, keine Formfrage.
  Ein Form-Erzeuger kann Legitimität nicht beurteilen und soll es nicht
  versuchen. **Das gehört zur Absichtshälfte — den 23 Handfällen.**
- **11 · IMAP-Status verworfen.** Andere Achse. Hier ist eine Handliste
  ausnahmsweise legitim, weil **geschlossen**: OK/NO/BAD/BYE/PREAUTH.

**Die 23 Handfälle bleiben liegen wo sie sind.** Sie sind die
**Absichts**hälfte, der Erzeuger die **Form**hälfte. Er ersetzt sie nicht.

---

## WO DIE HANDAUSWAHL BLEIBT — und das ist der wichtigste Absatz

**① Welche Stelle „verborgen" heißt.** Der Erzeuger pflanzt seine Marke
dorthin, wo *unser Code* eine Verbergung erkennt. Ein Register des
Für-das-Auge-Unsichtbaren gibt es nicht — das wäre ein Renderer.

**Folge, ausgesprochen:** Der Erzeuger schließt die Klasse *„der Code hat
einen Zweig und rechnet falsch"* — dort sitzen 1, 2, 3, 4. Er schließt
**nicht** die Klasse *„der Code hat gar keinen Zweig"*: `<style>`-Klasse,
`<font color="#FFFFFF">`, `aria-hidden`, `position:absolute;left:-9999px`,
`width="0"` bleiben strukturell außer Reichweite.

**Das darf nie als geschlossen berichtet werden.** Die zweite Klasse hat
genau eine Tür — echte Post —, und die ist bis zur fertigen Absicherung zu.

Dazu vier kleinere: die sieben Achsen-**Namen** (Achsenzahl gehört in jeden
Bericht, damit ein stiller Bruch sichtbar wird) · die Marken-Zeichenkette
(gemessen: `S1` → 90 von 98 Codecs baubar, `»K-1«` → nur 59; **rein ASCII,
und jede Baufehlschlagung wird gezählt, nie still übersprungen**) · die
Tiefenkappe · die Definition von „Kopfbereich" in Zeile c.

**Der Satz für den Bericht:** Dieser Vorschlag verlegt die Handauswahl von
den **Fällen** auf die **Verbergungsarten**. Das ist ein echter Fortschritt —
eine Handauswahl in einer Achse erzeugt hunderte Fälle statt einem — aber sie
ist da, und sie sitzt ausgerechnet in der Schicht, in der die Fehler wohnen.

---

## ZWEI DINGE, DIE UNGEPRÜFT SIND

Sie stehen hier, damit sie nicht in vier Wochen als geprüft zitiert werden.

1. **Ob `BODY.PEEK[TEXT]` eines echten Servers wirklich das liefert, was
   `roh.split(b"\r\n\r\n",1)[1]` modelliert.** Es deckt sich mit RFC 3501,
   ist aber gegen keinen Server gehalten. **Ein einziger lesender Abruf gegen
   ein Postfach klärt es, kostet nichts, und gehört VOR die Fixes** — sonst
   steht ein Architekturumbau auf einer ungeprüften Zeile (R1: die Prüfung in
   der echten Zielumgebung).
2. **Ob `mimetypes` auf dem VPS dieselbe Menge liefert** (hier 1201, gelesen
   aus `/etc/mime.types`). Fehlt das Paket dort, ist der Korpus dort ein
   anderer. **Der Achsenstand gehört in jeden Bericht** — sonst ist nicht
   unterscheidbar, ob der Erzeuger etwas gefunden hat oder die Maschine sich
   geändert hat.

---

## DANACH — die Reparatur, in dieser Reihenfolge

**① Der MIME-Zerleger — kein Bugfix, sondern Architektur.**
`BODY.PEEK[TEXT]` liefert den Rumpf **ohne** die Kopfzeilen, in denen
Content-Type und Boundary stehen; **der Rumpf allein ist gar nicht
zerlegbar.** Die Reparatur ändert den Abruf und berührt `_anhang_arten` →
**Probelauf im Klon (R4), eigener Block.**

**② Die vier kleinen**, jede einzeln testbar und einzeln committet: leere
Elemente in `_STUMM` · das Endtag-Zählwerk · das wertlose Attribut · die
Phantom-Anhänge.

**③ Erst danach** die Aufnahme in `regressionstest.sh`.

**Später und getrennt:** IMAP-Attrappe (8, 11) · Byte-Beschädiger ·
Abdeckungs-Tor (nur bei echtem Vorfall) · Ernte aus echter Post (nur mit
Adams ausdrücklicher Freigabe, **privates** Postfach, lokaler Export, nach
Abnahme der Erkennungsseite).

---

## WOFÜR ES SICH RECHNET — ehrlich

**Der Erzeuger allein zahlt auf gar nichts ein.** Ein Korpus, der rot ist und
rot bleibt, ist keine Verbesserung gegenüber einem, der grün ist und nichts
prüft. **Was nützt, sind die Fixes.**

**Der Erlösbezug ist mittelbar, aber real:** Adams Entscheid vom 21.08.
sperrt jedes fremde Postfach, bis die Absicherung steht. Ohne tragfähigen
Korpus keine Absicherung, also kein Mail-Kanal, also kein Nutzen aus allem,
was seit dem 23.08. gebaut wurde. **Der Erzeuger ist der Türöffner, nicht der
Selbstzweck.**

**Für den Kurs-Blick gehört er trotzdem in die Spalte „Innenarbeit."** Und
die Zeile daneben: *Aus drei Erzeuger-Entwürfen mit sechs Gegenprüfungen ist
EIN Block Bau übriggeblieben.* Die Entwürfe nannten fünf bis acht Blöcke
allein für den Erzeuger. **Das ist der Ertrag der Konvergenz-Bremse, und er
sollte gezählt werden.**
