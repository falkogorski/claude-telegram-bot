<!-- ROLLE: gegenpruefung-wiedereinstieg -->
# Widerlegungs-Gegenprüfung der ruhenden Baupunkte

**Stichtag:** 18.08.2026 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile im Drehbuch**

**Auftrag:** Conni, 18.08.2026, Schritt 1 des Wiedereinstiegs. Sechs frische,
getrennte Sitzungen, je mit dem ausdrücklichen Auftrag „Finde, was daran nicht
trägt" — nicht „prüfe, ob es stimmt". Geprüft wurden die zehn Commits nach dem
VPS-Stand `6ed4b91`.

**Ergebnis in einem Satz:** Zwei der geprüften Punkte hätten den Bot beim
Deploy funktionsunfähig gemacht, ein dritter läuft seit 21 Tagen tot im
Betrieb — und in **allen** Fällen war der zugehörige Selbstprüfer grün.

---

## Das Muster, das alles verbindet

Die Prüfer dieses Projekts sind überwiegend **Textsuchen im Quelltext**, keine
Messungen am Verhalten. Sie belegen, dass eine Zeichenkette dasteht, nicht dass
sie etwas tut. Drei Belege:

- `_c_keyboard_userid` verlangt `user_id=` an jeder Aufrufstelle und misst nur,
  **ob das Schlüsselwort dasteht** — nie, ob es dort einen Wert hat. Er hat den
  schwersten Fehler dieses Berichts **erzeugt** und anschließend **gedeckt**.
- Die B4-Prüfung ersetzt `send_chunked` durch eine Attrappe mit **genau der
  falschen Signatur, die der Fehler hat**. Damit war er per Konstruktion
  unsichtbar — zehn grüne Zeilen über eine Funktion, die nullmal meldet.
- `_kein_traeger_ohne_wache` prüft, ob der Text `tagescheck_pruefen` vorkommt.
  Entfernt man den **Aufruf** und lässt eine Kommentarzeile stehen, bleibt der
  Prüfer grün und die Wache ist tot. Gegenprobe gefahren.

**Die Lehre, die über alle Einzelbefunde hinausgeht:** Ein Prüfer, der den
geprüften Code nicht ausführt, prüft nichts. Ein `bash -n` und ein Lauf mit
leerer Umgebung hätten den 21-Tage-Ausfall am ersten Tag gefunden.

---

## A · Deploy-blockierend

### A1 — `send_answer_to_user` bricht bei jeder Antwort ab (B3)

```
async def send_answer_to_user(sess, chat_id, text, *, force_tts, reply_to, thread_id)
    kb = _main_keyboard(..., user_id=user_id)        # user_id existiert hier nicht
```

Gemessen per `symtable`: weder Parameter noch lokal noch modulweit gebunden.
`NameError` im **zentralen Sendepfad jeder Antwort**. Kein Regressionstest und
kein Selbstcheck ruft diesen Pfad auf; der Fehler hat auf den ersten Deploy
gewartet. Der Bot hätte jede Nachricht verarbeitet, die Antwort erzeugt — und
wäre gestorben, bevor ein Zeichen hinausgeht.

### A2 — Die Limit-Vorwarnung hat nie funktioniert (B4)

```
send_chunked(bot, chat_id, text, ...)     # echte Signatur
send_chunked(chat_id, text, ...)          # der Aufruf, an beiden Stellen
→ TypeError: send_chunked() missing 1 required positional argument: 'text'
```

Alle drei Ausgänge tot: Vorwarnung, „aufgebraucht", Entwarnung. Der Aufruf
liegt in einem `except`-Fang — das Kontingent wäre vollgelaufen, der Bot hätte
geschwiegen, und im Log stünde eine Zeile, die niemand liest. **Der Fangzweig
war hier kein Schutz, sondern Betäubung.**

---

## B · Im Betrieb, seit 21 Tagen

### B1 — Der Tagescheck ist seit dem 29.07. bei jedem Lauf gestorben

`scripts/daily_check.sh:276` nutzt `$HOME`; das Skript läuft mit `set -u` als
root-Systemdienst, und `claude-daily-check` setzt **kein** `User=` — systemd
liefert dort kein HOME. Gemessen: `HOME: unbound variable`, Exit 1, 21 Tage in
Folge.

**Drei Verschärfungen, die erst die Gegenprüfung gefunden hat:**

- **Der Abbruch verwirft, was der Lauf bereits gefunden hatte.** Die Messungen
  stehen ab Zeile ~140, das Protokoll wird erst ab Zeile 310 geschrieben. Der
  Regressionslauf lief jedes Mal vorher durch (28 s Rechenzeit, grün) — und das
  Ergebnis wurde weggeworfen. Es wurde nicht „nicht geprüft", sondern
  **geprüft und verschwiegen**.
- **Das ganze Skript hat genau einen Meldepunkt, ganz am Ende.** Jeder fatale
  Abbruch macht sämtliche Befunde stumm — Dienstausfälle, stillstehende
  Zeitgeber, zurückgenommene Härtung. Das ist die eigentliche Ursachenklasse,
  und sie ist mit einem `$HOME`-Fix **nicht** behoben.
- **Der Fehler ist nicht singulär.** Betroffen sind die Skripte, die unter
  einem Dienst **ohne** `User=` laufen oder von einem solchen aufgerufen
  werden: `daily_check.sh` (Zeile 276), `api_cache_pflege.sh` (31) und
  `regressionstest.sh` (80) — die beiden letzten erben die leere Umgebung vom
  Tagescheck. Nicht betroffen: `log_sync.sh`, `vps_schnappschuss.sh` (laufen
  unter `User=claudebot`, dort liefert systemd HOME).

### B2 — Warum die Gegenmaßnahme nicht griff

Die Kreuzverschränkung (`tagescheck_pruefen`, Kennung `tagescheck-still`) hätte
den Ausfall stündlich gemeldet — rund 500 Meldungen. Gemessen auf dem VPS:
**Der Code ist dort nicht vorhanden** (`grep -c tagescheck_pruefen` → 0). Sie
wurde am 28.07. gebaut und nie ausgerollt.

Die Wache selbst trägt: gegen ein künstlich gealtertes Protokoll geprüft —
25 h still, 27 h rot, fehlende Datei rot. **Aber ihre Rückrichtung wird vom
selben Fehler ausgehebelt**, den sie melden soll: Der Tagescheck misst die
Blumen bei Zeile ~140 und meldet ab 310.

---

## C · Falsche Auskünfte im Betrieb (B5, Vorlese-Regeln)

Alle Ausgaben gemessen, nicht geschätzt:

```
"Siehe Punkt 9.4. im Drehbuch"   →  "Siehe Punkt 9. April im Drehbuch"
"Punkt 8.7. ist erledigt"        →  "Punkt 8. Juli ist erledigt"
"Kapitel 2.1. und 2.2."          →  "Kapitel 2. Januar und 2. Februar"
"Der Text darf bis 1500 Zeichen" →  "bis fünfzehnhundert Zeichen"
"seit 1901"                      →  "seit neunzehnhundertein"
"Auflösung von 1920x1080"        →  "von neunzehnhundertzwanzigx1080"
```

Die Datums-Regel prüft nur den **Monat** auf Gültigkeit, nie den Tag — jede
Gliederungsnummer mit Zweitzahl bis zwölf wird zum Datum. `MIGRATION.md`
besteht aus solchen Punktnummern, und der Dokument-Vorlesepfad schickt
Dokumentinhalt durch dieselbe Kette.

Bei der Jahresregel sind „von", „bis", „ab", „im" als Jahres-Hinweise geführt —
im Deutschen überwiegend **Mengen**-Präpositionen. `_zahlwort(1)` liefert „ein"
statt „eins".

Kennnummern am **Satzende** greifen gar nicht (`(?![\d.,])` verwirft sie) —
die häufigste Stellung überhaupt.

---

## D · Die Regel, die auf einer falschen Verallgemeinerung beruht

**Betrifft `CLAUDE.md`, Abschnitt „Stichwort-Filter", von mir geschrieben und
von Conni abgenommen.** Beide haben denselben Denkfehler gemacht.

Der auslösende Fund war „Klientendaten" — ein Fall, in dem das heikle Wort
zufällig **vorn** steht. Im Deutschen steht das Grundwort jedoch **hinten**.
Gemessen gegen `ROTE_WORTE`:

| Text | Ergebnis |
|---|---|
| `Serverpasswort erneuern` | **kein Treffer** |
| `Zugangsschlüssel tauschen` | **kein Treffer** |
| `Zugriffstoken erneuern` | **kein Treffer** |
| `Bestandskunden anschreiben` | **kein Treffer** |
| `Datenbank-Passwort rotieren` | rot — nur wegen des Bindestrichs |

Gegenrichtung, ebenfalls rot: `siehe above im Text` (→ `abo`), `kostenlose
Variante`, `Rootverzeichnis des Repos`. Im Ruhemodus bedeutet Rot **Warten auf
Adams Daumen** — die Fehlerrichtung ist dort nicht „sicher", sondern „gar
nichts".

**Die Regel muss lauten: auf beiden Seiten keine Wortgrenze**, nicht nur hinten.

---

## E · Der Riegel, der anders aussieht als seine Beschreibung (B8)

```python
SCHARF = os.environ.get("AUFTRAGSBUCH_SCHARF") == "ja"
```

Commit-Text, Docstring und `ABHAENGIGKEITEN.md` behaupten dreimal
`SCHARF = False`. Tatsächlich ist es ein **Umgebungsschalter** — ein
`Environment=`-Eintrag, ein `export`, eine Zeile in einer Env-Datei öffnet ihn,
ohne dass sich eine Repo-Datei ändert. Der Prüfer `assert ab.SCHARF is False`
misst den eigenen Prozess, nicht den Betrieb.

**Und die geschlossene Grün-Liste ist umgehbar** (gemessen): `uebernehmen()`
liest `ampel` aus der Datei, statt neu einzustufen. Eine von Hand abgelegte
Datei mit unbekannter Art, unbekanntem Absender und einem Rot-Wort im Titel
wurde als grün an Hora übergeben.

---

## F · Weitere Befunde, nach Bereich

**B3 (Gründlich):** `switch_pending` wird beim Umschalten während eines Auftrags
nicht gesetzt — die Meldung „gilt ab der nächsten Aufgabe" ist falsch · bei
aktivem Gründlich wird jede Tiefen-Wahl still verworfen, während die
Bestätigung das Gegenteil sagt · Quellencheck und Tiefe hängen an
verschiedenen Zuständen (eingefrorenes Job-Feld vs. aktuelle Vorlieben) · im
Gründlich-Zweig steht **doch noch** ein `close_session`; der Prüfer filtert auf
`"thorough"` kleingeschrieben und trifft den Zweig nicht.

**B4:** Warn-Zustand prozessweit ohne Nutzerbezug (bricht beim zweiten Nutzer) ·
Entwarnung bleibt über Neustart hängen · die Dämpfer-Begründung („der Anbieter
schickt den Zustand mit jedem Lauf mit") widerspricht dem SDK, das *emitted
when rate limit info changes* sagt — **eine Behauptung im Gewand einer
Messung** · die PDF-Zusammenfassung verbraucht Kontingent und wird nirgends
gezählt.

**Versions-Monitor:** ein unlesbarer Zeitstempel legt einen manuellen Eintrag
**dauerhaft** still und das Protokoll meldet „vor 0 Tagen gesehen" · eine
kaputte Sichtungsdatei setzt alle Fristen zurück · ein Downgrade wird als
Update gemeldet · `systempaket` kann nie MAJOR werden · der Docker-Handler misst
das lokale Abbild, nicht den laufenden Container · ein unvollständiger
Register-Eintrag lässt den Monitor **vor** Protokoll und Versand sterben.

**`/updates`:** jede Komponente wird zweimal befragt (`classify` und
`blinde_flecken` messen getrennt) — und **genau daraus entsteht das Loch neu**,
das der Fix schließen wollte: Fällt eine Quelle im ersten Durchlauf aus und
antwortet im zweiten, erscheint sie in keiner der beiden Listen.

**Zeitgeber-Wache:** findet nur Zeitgeber, die systemd noch **kennt** — ein
gelöschter taucht nicht auf und gilt als in Ordnung · der ExecStart-Pfadfilter
ist selbst eine Positivliste mit einem Eintrag · monotone Zeitgeber werden
falsch angeklagt.

**Hora:** die Ausgabe wird **vor** der Suche auf die letzten 1200 Zeichen
gekürzt — bei geschwätziger stderr fällt der Kopf weg, und die rote Zeile mit
ihm · `_ROT_ZEILE` trifft weder `Fehler:` noch `ERROR` noch `failed` · die drei
Plätze werden nach Reihenfolge vergeben, nicht nach Gewicht.

**B1 (Anlagen):** alle sieben vorhanden, aber **keine** trägt einen
Gültigkeits-Kopf; zwei sind bereits überholt und sagen es nicht.

---

## Was das für den Deploy bedeutet

**Ein reiner `git pull` ist nicht möglich.** A1 und A2 müssen vorher repariert
werden, B1 ebenfalls — die `$HOME`-Zeile steht unverändert im HEAD, der Deploy
allein heilt sie nicht.

Vorschlag zur Reihenfolge, zur Freigabe durch Conni:

1. **A1, A2, B1** reparieren — je einzeln committet, je mit einem Prüfer, der
   den Code **ausführt** statt ihn zu lesen.
2. **Den fehlenden Prüfer bauen**, der die ganze Klasse abdeckt: jedes Skript
   unter leerer Umgebung starten (`env -i`), und die Meldepunkte so setzen, dass
   ein Abbruch nicht alle vorherigen Befunde verschluckt.
3. **C, D, E** reparieren (falsche Auskünfte, Wortgrenzen-Regel, Riegel).
4. Erst dann Deploy in einem Zug.

Die übrigen Befunde aus F sind nach Schwere zu sortieren; keiner davon ist
deploy-blockierend.

💰 Kostenlage: null.
