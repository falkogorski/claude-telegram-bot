> **Zweck: WEITERGABE → Engywuck** · **Zu tun:** nachprüfen. Drei Zahlen, die
> du erbeten hast, stehen unten — eine davon entscheidet den Riegel.

# Bericht — M-1 bis M-6, und die Zahlen für deine offenen Fragen

**Stichtag:** 09.09.2026, 11:33 · **Stand:** `21867c1`, gepusht
**Läufe:** 73/73 · Zielumgebung 41/43 · **Nenner:** 11 Punkte im Auftrag —
**5 gebaut, 1 gemeldet statt gebaut, 3 warten auf Adam, 2 gehören in einen
eigenen Block** · **0 Deploys**

---

## Gebaut und gegengeprüft

**M-1 — der Absender und die stumme Drossel.** `postfach_ablegen.py` schreibt
`herkunft` (Vorgabe „Claudia", Schalter für die Melder). Dazu die zweite
Hälfte: Die 🔇-Meldung geht jetzt **sofort und direkt** über `app.bot`,
gedämpft je Absender und Fenster. Bisher ritt sie auf der nächsten Zustellung
desselben Absenders mit — war der gedrosselt, wartete die Meldung mit ihm.
Drei Gegenproben, jede traf die vorher notierte Zeile.

**M-2 — der zweite Basisordner.** Benannte Basen mit **je eigener
Namensmenge**, nicht `is_relative_to`: Der Ort entscheidet, nicht der Name.
Gemessen: `postfach_ablegen.py` bleibt in der falschen Basis dialogpflichtig.
Fünf neue Zeilen, zwei bestehende **umgestellt statt aufgeweicht** (der
Grundtext heißt jetzt „unter einem freigegebenen scripts/").

**Deinen dritten Punkt habe ich nicht gebaut, weil er schon gilt:** `mv` und
`cp` innerhalb `~/workspace/` sind frei, `rm` ist Dialog. Nachgemessen.

**M-3 — die Messung, die seit dem 01.09. fehlt.** `bashfreigabe.dialog_gezeigt`
schreibt beim tatsächlichen Senden ein **eigenes Ereignis**. Kein Feld im
Urteil, und der Grund ist die Reihenfolge: Das Urteil steht fest, bevor klar
ist, ob gefragt wird. Ein nachträglich gesetztes Feld müsste die Zeile ändern;
ein zweites Ereignis muss nur geschrieben werden — und kann nicht verwechselt
werden. Die Auswertung nennt beide Zahlen nebeneinander; ohne Messung sagt sie
**NICHT GEMESSEN** statt null.

**M-5/M-6 — die Ablage stimmt wieder.** Drehbuch und Register führten
*„Rechnungsnummern-Rückfrage unverändert Pflicht"*, Adam hat sie am 07.09.
abgeschafft. Die sieben weiteren Regeln stehen als **Verweis** auf
`RECHNUNGSREGELN.md`, nicht doppelt. Route A trägt den Vermerk zur zweiten
Freigabe, nicht geglättet. Meldungstext auf „Datei(en)".

---

## 🔴 Die drei Zahlen, die du erbeten hast

**① Steht `Bash` in Adams `always_allow`? — JA.**

```
Nutzer 304455165: always_allow = ['Bash', 'Read']
Prefs zuletzt geändert: 06.09.2026, 20:55
```

Und `_bash_auto_on` **ist** genau diese Prüfung — ein Zustand, zwei
Bedienwege. **Auto war am Rechnungsmorgen also an.** Damit fällt deine erste
Alternative; es bleibt die zweite: *es gibt einen Pfad, den ich nicht sehe.*

**Ich habe ihn gesucht und nicht gefunden** — und sage das, statt eine Ursache
zu benennen, die ich nicht messen kann. Geprüft: kein Rechnungsbefehl trifft
einen Geheimnis- oder Dauerwirkungs-Marker (`.env`, `token`, `claude.md` …);
`.venv` enthält **nicht** `.env`; die Sitzung lädt die Freigaben beim Aufbau.
**Ab jetzt ist die Frage messbar** — das ist M-3, und mehr war heute ehrlich
nicht zu holen.

**② Die zwei `&`-Befehle — deine Vermutung `2>&1` ist widerlegt.**

Gemessen an `_hat_hintergrund_und`: `2>&1`, `2>/dev/null` und Pipes ergeben
alle **False**. Es war ein echtes freistehendes `&`. Beide Zeilen sind
`art=grep` — und Adams Ablage führt einen Ordner `Fitmart : ESN & More`. Das
ist eine Vermutung, keine Messung: **Das Protokoll führt keinen Befehlstext**
(nur Zeit, Urteil, Art, Bereich), deshalb ging dein „Mick zieht die Befehle
aus dem Log" nicht.

**③ Grün-Übergaben in der Probezeit: NULL.**

```
~/.claude/auftragsbuch — 14 Einträge, 20.08. bis 03.09.
                         14× gelb, 0× grün
```

Der Tagescheck hat die abgelaufene Frist heute früh bereits gemeldet. **Deine
Empfehlung ist damit belegt:** In zwei Wochen hat die Grün-Automatik nichts
getan, was sie hätte tun können. Der Riegel schließt sich von selbst; Adams
Wort fehlt nur noch für „neu setzen oder zulassen".

**Und die vierte, die du nicht erbeten hast:** Rang A ist **seit dem 29.08.
vollständig repariert** (alle acht, Belegstellen in `docs/befund-entkernung.md`;
`CLAUDE.md` führt es unter *nachgezogen 31.08.*). Deine Vorbedingung für M-9
ist erfüllt.

## 🔴 M-4 — gemeldet statt gebaut

`scripts/konzept_pdf.py` **existiert nicht**, weder hier noch auf dem Server.
Dein Auftrag lautet „in `BENANNTE_SKRIPTE` eintragen, mit `url_fetcher`" — das
setzt ein Skript voraus, das es zu schreiben gäbe.

**Ich baue es nicht aus dem Zuschnitt, den ich mir denken könnte.** Offen sind
Eingabe und Ausgabe, das Layout — und vor allem die Werkzeugkette: Im Projekt
gibt es **zwei**, `pandoc`+`typst` (Adams Vorgabe für die Doppel-Lieferung
`.md` + PDF) und `weasyprint` (auf dem Server vorhanden, Fassung 62.3), auf das
deine `url_fetcher`-Auflage zeigt. Welche gemeint ist, entscheidet, wie die
PDF aussieht — das ist Adams Geschmack, nicht meine Ableitung.

**Deine Auflage ist unabhängig davon richtig** und gehört in den Bauauftrag:
Was aus HTML heraus nachlädt, lädt aus dem Netz — ohne `url_fetcher`, der
alles außer lokalen Pfaden abweist, ist „kein Netz" eine Behauptung.

**Adams Neigung, 09.09. 11:4x, ausdrücklich unter Vorbehalt:** *„ich schätze
pandoc und typst, wie bei den anderen Dateien, warte aber vorher noch auf
Engys Einschätzung."* Also **kein Bau, bis du dich geäußert hast.** Der
Vorbehalt gilt der Werkzeugkette, nicht deiner Auflage.

⚠️ **Falls es `typst` wird, ändert sich deine Auflage in der Form, nicht im
Ziel:** `typst` lädt nicht aus HTML nach, aber es kennt `image()` und
Paketimporte (`@preview`). Ein `url_fetcher` ist dort das falsche Werkzeug;
die entsprechende Schranke wäre `--ignore-system-fonts` samt einem
Wurzelverzeichnis (`--root`), das nichts außerhalb des Arbeitsordners
erreichbar macht. **Wer die Auflage eins zu eins überträgt, baut eine
Schranke, die es in dieser Kette nicht gibt** — und hält sie dann für gesetzt.

## Was in einen eigenen Block gehört

**M-9** (SDK 0.2.152 + CLI 2.1.263 im Klon, danach Limit-Signatur messen) und
**M-7**, das laut deiner Reihenfolge darauf wartet. Ein Fundament-Sprung mit
Probelauf im Klon ist kein Anhängsel an einen Vormittag — R4 verlangt ihn,
und die Limit-Signatur ist danach ohnehin neu zu messen.

**M-8** (Fable 5.1) wäre klein und passt in den nächsten Block; dein Umbau von
Auftrag 3 — Umstellung beim nächsten von Adam ausgelösten Lauf statt Probe aus
dem Zeitgeber — ist die richtige Auflösung der AGB-Stelle.

**M-10/M-11** warten auf Adam.

## Zwei eigene Fehler, damit sie nicht als Befund weiterleben

**① Ich bin in die Anführungszeichen-Falle gelaufen** — ein gemischtes Paar
`„…"` brach die Datei beim Schreiben eines Kommentars **über** Messgenauigkeit.
Berichtigt mit eckigen Klammern, wie die Regel es vorsieht.

**② Mein erster M-2-Prüffall war falsch konstruiert:** relatives Argument ohne
`cd`, das gegen das Arbeitsverzeichnis aufgelöst außerhalb der Bereiche liegt.
Die Schranke verhielt sich richtig, der Fall war falsch. Der Prüfstand hat es
gefangen, weil die erwartete rote Zeile vorher notiert war.
