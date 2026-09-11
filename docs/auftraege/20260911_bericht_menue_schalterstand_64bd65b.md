> **An Adam, zur Weitergabe an Engywuck** · Mick · 11.09.2026, 04:01 · gebaut: `d783508..64bd65b` · Regressionslauf 81/81 · **kein Deploy**

**Zweck: ANSICHT + WEITERGABE → Engywuck** · **Zu tun: Adam nichts — weiterreichen, wenn er mag**

# Nachtblock: Schalterstand im Menü (168113d) und Log-Takt (64bd65b)

## Was gebaut wurde

Claudias Auftrag, mit Engywucks vier Ergänzungen, ohne Abweichung:

| | |
|---|---|
| `_SCHALTER` als **getrennte** Tabelle neben `_BEFEHLE` | `_BEFEHLE` trägt Menü **und** Hilfetext; ein Momentwert hätte im Hilfetext nichts zu suchen |
| Je Chat statt global, `BotCommandScopeChat` | die globale Liste **ohne** Stand bleibt als Rückfall stehen |
| Auslöser ist eine **Signatur**, kein Nachziehen an den Handlern | eine Liste von Aufrufstellen hält bis zum nächsten neuen Schalter |
| Fehlschlag **verwirft** die Signatur *(Engywuck 4)* | sonst hält der Bot einen Stand für geschrieben, den Telegram nie bekam |
| `MENUE_STAND` ohne Eintrag heißt **an** *(Engywuck 1)* | die Umgebungsdatei ist root-Besitz, ein Deploy darf sie nicht brauchen |
| `_still_an` liest `_alle_sess`, ruft **nicht** `ensure_session` *(Engywuck 3)* | der Geber läuft nach jedem Update und darf keine Sitzung anlegen |
| Forum-Grenze als Kommentar an `_SCHALTER`, **nicht gebaut** *(Engywuck 2)* | es gibt kein Haus; steht auf der F-Liste |

Prüfer `scripts/test_menue_schalterstand.py`, im Regressionslauf (80 → 81).

## Die sieben Prüfzeilen, je eine Gegenprobe

Alle mit `py_compile`, gelöschtem `__pycache__` und **vorher notierter**
erwarteter Zeile; jede rot an der erwarteten Stelle.

| Gegenprobe | rot geworden |
|---|---|
| Schalter ohne Befehl eingetragen | „jeder Schalter hat einen Befehl" |
| `tts` aus der Tabelle genommen | „kein Umschalter ausserhalb von _SCHALTER" |
| Kürzung auf 256 entfernt | „1 bis 256 Zeichen" — Langtest 408 |
| Signatur konstant gemacht | „die Signatur kippt" (und Zeile 6, wie vermutet) |
| Beschreibung ignoriert den Geber | „stimmt in beiden Stellungen", alle sechs Schalter |
| Fehlschlag hält die Signatur | „Fehlschlag verwirft die Signatur" |
| `technik` aus der Tabelle genommen | „kein Befehl legt einen Zustand um, ohne in _SCHALTER zu stehen" |

## Eine Zeile über den Auftrag hinaus — gemessen, nicht vermutet

Claudias Zeile 2 ist die Gegenrichtung: *Jeder Befehl, dessen Beschreibung
„an/aus" oder „umschalten" enthält, muss in `_SCHALTER` stehen.* Sie war grün.

**Von den sechs heutigen Schaltern verraten sich drei nicht:** `technik` heißt
„Klartext ↔ Rohform", `quiet` heißt „Tipp-Indikator aus", `verbose` heißt
„wieder an". Die Zeile hätte die Hälfte ihrer Fälle nie gesehen.

Deshalb Zeile 7 als **Menge**: Welcher Befehls-Handler legt einen Zustand um
(`x = not …`)? Das Befehl-Handler-Paar kommt aus den
`CommandHandler`-Registrierungen, nicht aus einer gepflegten Liste. Gemessen:
**vier Treffer, alle bereits eingetragen, kein Fehlalarm** — deshalb ohne
Ausnahmeliste.

**Was auch sie nicht fängt, und das steht im Prüfer statt in einem dritten
Wächter:** `/quiet` und `/verbose` sind ein **Paar**, kein Umschalter — sie
setzen auf feste Werte. Ein künftiger Paar-Befehl mit unauffälligem Text fiele
durch beide Raster.

## Log-Takt: eine Behauptung war falsch

Stufe 1 (Minutentakt mit `AccuracySec=1s`) und Stufe 2 (`claude-log-sync.path`)
liegen als Befehlsblöcke in `docs/befehlsbloecke-root.md`. **Adams Hand, root,
nicht eingespielt.**

Zwei Angaben habe ich nachgemessen statt übernommen:

1. *„Kein Prüfer hängt am Fünf-Minuten-Wert"* — **stimmt.** `grep` über
   `scripts/` und `.claude/` ist leer.
2. **Der Pfad stimmte nicht.** `PathModified=~/workspace/ausarbeitungen` gibt
   es nicht: `log_sync.sh` gleicht `~/workspace` als **Wurzel** ab,
   „ausarbeitungen" ist der Name im **Ziel**. Am Bestand des Log-Repos
   gemessen: **140 von 180** Ausarbeitungen liegen direkt in dieser Wurzel, 39
   unter `ablage/`, eine unter `an-mick/`. Daher drei Zeilen für den
   Arbeitsordner statt einer.

Die Grenze steht im Block, weil sie sonst still zuschlägt: **`PathModified` ist
nicht rekursiv.** Ein neuer Unterordner fällt auf den Minutentakt zurück, ohne
dass etwas rot wird.

## Was zu prüfen wäre

1. Die **siebte Zeile** — ist die Mengen-Bildung über `CommandHandler`-Paare
   umgehbar? Sie liest den Syntaxbaum, und das ist nach der Faustregel vom
   22.08. der verdächtige Fall. Mein Gegenargument: Sie zählt keine Namen,
   sondern bildet zwei Mengen und schneidet sie. Wer den Handler umbenennt,
   ändert beide Seiten mit.
2. **`_still_an` gibt bei leerer Sitzungsmenge `False`** — richtig, weil `quiet`
   nach einem Neustart tatsächlich aus ist. Aber: Nach einem Neustart steht im
   Menü noch der alte Stand, bis Adam die erste Nachricht schickt. Der
   Start-Durchgang in `post_init` schreibt zwar — nur ist die Sitzungsmenge
   dort leer, also schreibt er „läuft mit". Das ist korrekt, sieht aber wie ein
   Rücksprung aus, wenn Adam vorher `/quiet` gesetzt hatte.
3. Ob die **Reihenfolge** stimmt: `group=99` läuft nach dem Schalter-Handler
   desselben Updates. Du hast es gelesen; gemessen habe ich es nicht — dafür
   braucht es einen laufenden Bot.

## Nicht getan, mit Absicht

**Kein Deploy.** Adam reist; das geht zusammen mit `0f4087e` und, wenn er es
entscheidet, mit F-22. Und **kein Schaltbrett** (`/schalter`) — Claudia hat es
als Vorschlag markiert, nicht als Auftrag.
