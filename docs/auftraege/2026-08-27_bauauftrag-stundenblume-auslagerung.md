# Bauauftrag — Stundenblume: Auslagerung nach Aktivität messen, Meldung ins Protokoll

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau)
**Angelegt:** 27.08.2026, 18:10 Uhr
**Freigabe:** Adam am 27.08.2026 um 18:04 Uhr (Daumen hoch auf die Frage von 16:28 Uhr)
**Umfang:** zwei Eingriffe in `scripts/stundenblume.py`, ein Test in `scripts/test_stundenblumen.py`

---

## Warum — der Befund

Die Speicher-Wache meldet einen Befund `swap-benutzt`, sobald mehr als 256 MiB im
Auslagerungsbereich liegen (`scripts/stundenblume.py`, Zeilen 373 bis 381).

**Der eigene Kommentar der Funktion nennt die richtige Absicht und das falsche Maß
im selben Satz.** Zeile 350: *„Wird er im Alltag angefasst, ist das der Hinweis, dass
die Auslegung nicht mehr passt."* **Angefasst** ist eine Handlung. Gemessen wird
aber, wie viel **liegt** — ein Bestand.

### Was heute gemessen wurde (27.08.2026, 18:07 Uhr, VPS)

| Größe | Wert | Bedeutung |
|---|---|---|
| `SwapTotal − SwapFree` | 594 MiB | liegt drin, seit unbekannt |
| `pswpout` | 189911 Seiten | insgesamt ausgelagert seit Systemstart (rund 742 MiB) |
| `pswpin` | **0** | **noch nie etwas zurückgeholt** |
| Systemlaufzeit | 6 Wochen, 2 Tage | |
| `MemAvailable` | 5,8 von 7,8 GiB | von Enge keine Spur |
| Bewegung über 5 Sekunden | 0 hinein, 0 heraus | steht still |

`pswpin` gleich null ist der entscheidende Wert: In gut sechs Wochen wurde nichts
zurückgeholt. Das ist kein Notfall, sondern Aufräumen — der Kernel hat selten
benutzte Seiten weggeräumt und braucht sie seither nicht. Im Mittel sind das etwa
drei Seiten je Minute.

**Folge, wenn nichts geschieht:** Die Blume läuft minütlich (`stundenblume.timer`).
Der Dämpfer hält die Wiedervorlage bei einer Stunde. Adam bekommt diese Meldung
also **vierundzwanzigmal am Tag**, ohne dass je etwas zu tun ist — bis der Bereich
zufällig unter 256 MiB fällt, was ohne Neustart nicht passiert.

Ein Wächter, der täglich rot meldet und nie etwas zu tun gibt, ist binnen zwei Tagen
abgeschaltet. Dann steht ein blinder Wächter da, wo ein wacher stehen sollte.

---

## Auftrag 1 — Maß auf Auslagerungsaktivität umstellen

**Stelle:** `scripts/stundenblume.py`, `speicher_pruefen()`, Zeilen 373 bis 381.

**Weg:** `/proc/vmstat` liefert `pswpin` und `pswpout` als kumulative Seitenzähler.
Die Blume legt den zuletzt gesehenen Stand samt Zeitstempel in ihrem Zustandsordner
ab (`BLUMEN_DIR`, voreingestellt `~/.claude/stundenblumen`) und bildet beim nächsten
Lauf die Differenz. Kein Warten im Lauf nötig — der minütliche Takt ist das Fenster.

**Der Befund entsteht nur, wenn beides zugleich zutrifft:**

1. **Auslagerung läuft:** mehr als 1000 Seiten je Minute nach draußen (`pswpout`),
   das sind rund 4 MiB je Minute.
2. **Der Speicher ist knapp:** `MemAvailable` unter `SPEICHER_HINWEIS_MIB`
   (voreingestellt 800 MiB, Zeile 319).

**Warum die Verknüpfung trägt:** Auslagerung bei reichlich Speicher ist Hausarbeit
des Kernels. Auslagerung bei Enge ist das Vorzeichen des Kippens. Nur der zweite
Fall verdient einen Wächter.

**Zur Schwelle, offen gesagt:** Die 1000 Seiten sind eine Setzung, kein Messwert.
Belegt ist nur, dass sie im Normalbetrieb dieser Maschine nicht anschlägt — der
gemessene Mittelwert liegt rund dreihundertfach darunter. Sie gehört als
Umgebungsgröße nach außen (`BLUMEN_SWAP_SEITEN`), damit sie ohne Codeänderung
nachgezogen werden kann.

**Diese Fälle schweigen ausdrücklich:**

- **Erster Lauf** (kein vorheriger Stand vorhanden): Wert merken, nichts melden.
- **Negative Differenz** (Zähler kleiner als zuletzt): Die Maschine wurde neu
  gestartet. Wert merken, nichts melden.
- **`/proc/vmstat` nicht lesbar** (kein Linux, kein Recht): keine Aussage statt
  Raterei — dieselbe Haltung wie bei `_meminfo()` in Zeile 353.

**Neuer Kennungsname:** `swap-aktiv` statt `swap-benutzt`. Die alte Kennung
verschwindet damit aus dem Dämpfer-Gedächtnis, was den Nebeneffekt hat, dass beim
ersten Lauf nach dem Einspielen **eine Entwarnung** für `swap-benutzt` an Adam ginge
(`_daempfen`, Zeile 661: entwarnt wird alles, was im Gedächtnis steht und nicht mehr
auftritt). Zwei saubere Wege: entweder `~/.claude/stundenblumen/gemeldet.json` beim
Einspielen einmalig um den Eintrag `swap-benutzt` erleichtern, oder die Entwarnung
als einmaligen Abschluss bewusst durchlassen. **Empfehlung: durchlassen** — sie ist
sachlich richtig und erklärt sich von selbst.

---

## Auftrag 2 — Diese Meldungsklasse erreicht Adam nicht mehr

Nach der Einteilung vom 21.08.2026 gibt es drei Klassen: was Adam betrifft oder wo
er entscheiden muss, was technisch ist und ohnehin bearbeitet wird, und was reiner
Nachweis ist. Eine laufende Auslagerung bei knappem Speicher ist **technisch** — sie
gehört ins Protokoll und an die Kontrollsitzung, nicht in Adams Chat.

### Empfohlener Weg: Kennungspräfix `p:`

Eine Kennung, die mit `p:` beginnt, wird geschrieben, aber nicht gesendet.

**Warum dieser Weg und nicht ein drittes Tupelfeld:** Die Befundlisten sind heute
uneinheitlich getippt — `speicher_pruefen()` ist als `list[str]` deklariert, gibt
aber Tupel zurück; `zustellung_pruefen()` ebenso. Ein drittes Feld zwänge jede
entpackende Stelle zur Änderung und bräche stillschweigend jede, die übersehen wird.
Das Präfix kommt ohne Umbau aus.

**Warum keine zentrale Ausschlussliste:** Eine Liste an anderer Stelle wächst nicht
mit. Wer künftig einen Befund anlegt, sieht die Liste nicht und meldet an Adam,
ohne es zu wollen. Die Einstufung gehört an den Befund selbst — das Präfix steht
dort, wo der Befund entsteht, und lässt sich nicht vergessen.

### Der Filter muss an BEIDEN Ausgängen greifen

`_daempfen()` gibt zwei Listen zurück: `neu` und `entwarnt` (Zeilen 652 und 661).
**Filtert man nur `neu`, kommt die Meldung nicht an, die Entwarnung aber schon** —
Adam bekäme ein „erledigt", ohne je die Warnung gesehen zu haben.

Das ist derselbe Fehler wie am 28.07.2026, nur seitenverkehrt. Damals verglich der
Dämpfer Texte statt Kennungen und schickte Alarm und Entwarnung im selben Atemzug.

**Sauberste Stelle:** vor dem Aufruf des Dämpfers trennen — die `p:`-Befunde in die
Kette und ins Protokoll schreiben, die übrigen in den Dämpfer geben. Dann kann keine
Entwarnung entstehen, die es nicht geben darf.

**Die Kette schreibt weiter alles mit.** `kette.jsonl` bleibt vollständig; nur der
Weg zu Adam entfällt. Der Nachweis geht nicht verloren, er wird still.

---

## Was NICHT angefasst wird

**`scripts/daily_check.sh`, Zeile 562** schreibt den Auslagerungsstand täglich ins
Protokoll und meldet ihn nicht an Adam. Das ist bereits richtig gebaut und ist nach
der Umstellung die Stelle, an der die Entwicklung des Bestands ablesbar bleibt.
Unverändert lassen.

---

## Was kann brechen und wer merkt es

| Was | Wer merkt es | Vorkehrung |
|---|---|---|
| **Der bestehende Test bricht.** `scripts/test_stundenblumen.py`, Zeilen 228 bis 233, erzwingt wörtlich das alte Verhalten: *„benutzter Swap wird nicht bemerkt"*. Nach der Umstellung schlägt er fehl. | Der 4-Uhr-Check, laut und sofort | Test im selben Zug umschreiben: Aktivität ohne Enge schweigt, Aktivität mit Enge meldet, erster Lauf schweigt, Zählerrücksprung schweigt |
| **Der Zustandsspeicher lässt sich nicht schreiben** (Rechte, volle Platte). Die Blume merkt sich nie einen Vorwert und schweigt für immer — ein Ausbleiben, das wie Ruhe aussieht. | Niemand, ohne Prüfer | Schreibfehler in die Kette schreiben, nicht stillschweigend verschlucken. Der Tagescheck prüft, ob die Zustandsdatei jünger als eine Stunde ist |
| **Die Schwelle ist zu hoch gewählt.** Echte Not bleibt unbemerkt. | Niemand | Die Verknüpfung mit `MemAvailable` fängt das zweite Netz: Unter 400 MiB schlägt `speicher-eng` ohnehin an, unabhängig von der Auslagerung |
| **Das `p:`-Präfix wird beim Entwarnen übersehen.** Adam bekommt eine Entwarnung ohne vorherige Warnung. | Adam, unangenehm | Trennung vor dem Dämpfer, nicht danach. Ein Test, der einen `p:`-Befund erzeugt, verschwinden lässt und prüft, dass nichts gesendet wurde |
| **Ein künftiger Befund vergisst das Präfix** und meldet an Adam, obwohl er technisch ist. | Adam, als Rauschen | Der Wortlaut der Konvention gehört in den Dateikopf von `stundenblume.py`, wo jeder ihn sieht, der einen Befund anlegt |
| **Die Umstellung selbst wird nie eingespielt** und gilt als erledigt. | Niemand | Zustand bleibt *vereinbart*, bis ein Lauf gegen die neue Fassung geprüft hat |

---

## Randnotiz, nicht Teil des Auftrags

Beim Lesen von `scripts/daily_check.sh` sind in ausgehenden Meldungstexten
ASCII-Umschreibungen aufgefallen: „Vorraete", „verfuegbar" (Zeile 562), „Stoerung"
(Zeile 546). Das gehört zum Umlaut-Befund vom heutigen Morgen und wird dort
verfolgt, nicht hier — vermerkt, damit es nicht zweimal gefunden werden muss.
