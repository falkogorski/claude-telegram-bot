<!-- ROLLE: automatik-regelwerk -->
# Automatik-Regelwerk — unter welchen Schranken Hora nachts arbeitet

> **Gültigkeits-Kopf** (Regel ⑪)
> **Stichtag:** 31.08.2026, 12:0x · **am Code gemessen**, nicht aus Berichten
> **Gemessen an:** `8167d6b` · **Überholt durch:** —
> **Zuletzt nachgezogen:** 31.08.2026 (Erstfassung)
> **Maßgeblich** bleibt der Code; dieses Papier sammelt, was verstreut in
> `auftragsbuch.py`, `hora.py` und `CLAUDE.md` steht.

**Warum es dieses Papier gibt.** Adams Entscheid vom 31.08., sinngemäß im
Wortlaut: *„Natürlich muss Hora einen Nachtlauf machen können. Wenn alles immer
einen manuellen Daumen braucht, ist es zu krass. Wir müssen dafür klare Regeln
haben, dass da nichts schiefgehen kann."*

**Die Sicherheit kommt aus dem Regelwerk, nicht aus dem Daumen.** Es gab schon
Regeln — aber **keine Stelle, an der jemand nachlesen kann, ob sie zusammen
tragen.** Genau das ist hier.

**Es wird nichts Neues erfunden.** Wer beim Lesen merkt, dass eine Schranke
fehlt, trägt sie in **Abschnitt C** ein und **baut sie nicht** — sonst wird aus
*Regeln aufschreiben* unbemerkt *Regeln ändern*.

---

## Abschnitt A — was heute gilt, am Code belegt

| # | Schranke | Beleg (`8167d6b`) |
|---|---|---|
| 1 | **Geschlossene Absenderliste**, fünf Namen: `claudia · conni · mick · hora · stundenblume`. Unbekannt → `ValueError`, der Auftrag **entsteht gar nicht** | `auftragsbuch.py:90` (Liste), `:218` (Prüfung) |
| 2 | **Geschlossene Artenliste** (`GRUENE_ARTEN`), jede Art mit eigenem Prüfdatum. Unbekannte oder fehlende Art → **gelb**, nie grün | `auftragsbuch.py:111` |
| 3 | **Rote Wortsuche** über `titel`, `aktion`, `begruendung` **und `befehl`** — beidseitig offene Wortgrenzen, kurze benannte Ausnahmeliste | `auftragsbuch.py:165` (Muster), `:188` (die vier Felder) |
| 4 | **Die Einstufung wird MITGESCHRIEBEN**, nicht bei jedem Lesen neu gerechnet. Ändert sich die Grün-Liste, bleibt nachvollziehbar, unter welcher Regel ein Auftrag hereinkam | `auftragsbuch.py:222–232` (`ampel`, `ampel_grund`, `eingang_am`, `braucht_zustimmung`) |
| 5 | **Regressionslauf VOR dem Befehl** — auf rotem Fundament wird nicht gearbeitet | `hora.py:483` (`regression()`), Aufruf im Lauf |
| 6 | **Regressionslauf NACH dem Befehl.** Nur wenn **beide** grün sind, gilt der Auftrag als erledigt | `hora.py:697` (`erfolg and nachher_ok`) |
| 7 | **Frische Sitzung je Auftrag**, Zeitgrenze **7200 s**, Ausgabe verdichtet (`_AUSGABE_GRENZE` 200.000 Zeichen) | `hora.py:681`, `:213` |
| 8 | **Kontingent erschöpft → anhalten, nicht scheitern.** Der Auftrag bleibt offen, nichts wird abgehakt, nichts geht verloren | `hora.py:99` (Wortlaute), `:691` |
| 9 | **Schloss** — nur ein Lauf gleichzeitig, mit Alterung gegen verwaiste Schlösser (4 h); **Fehlserien-Zähler** (`FEHLGRENZE 3`) | `hora.py:119–126`, `:94` |
| 10 | **Übersprungen ist nicht bestanden.** Endet der Regressionslauf mit 77 (grün, aber nicht alles gemessen), öffnet Hora **keines** der beiden Tore | `hora.py:490` |

**Zu 10, weil es die jüngste Schranke ist:** Sie entstand am 30.08. aus einer
Widerlegung. Vorher galt „Rückgabewert 0 = alles in Ordnung" — ein Lauf mit
fünfundsechzig übersprungenen Prüfungen endete mit 0, und Hora hätte auf einem
Fundament gearbeitet, das niemand vermessen hat.

---

## Abschnitt B — die Regel über allen

Aus `CLAUDE.md`, wörtlich:

> **Keine Automatik beginnt von sich aus Arbeit.** Das **Zu-Ende-Führen** einer
> von Adam begonnenen und durch ein Limit unterbrochenen Interaktion ist
> erlaubt — **genau ein nachgeholter Lauf**, **nur bei vermerkten
> unbeantworteten Adam-Nachrichten**, **höchstens drei Weckversuche**.

**Die drei Bedingungen sind harte Bedingungen im Code, keine Kommentare.**
Zeitgesteuerte Läufe sind **deterministisch oder gar nicht**: Der Wachposten ist
modellfrei, der Tagescheck ist modellfrei, der Erinnerungs-Läufer wird
modellfrei. Hora führt **Skripte** aus, keine Modell-Läufe.

---

## Abschnitt C — die Lücken, ehrlich benannt

### C-1 · Die `art` deklariert der Schreiber selbst

**gemessen am:** 31.08.2026 · **offen seit:** 23.08.2026 (F-16) ·
**wer entscheidet:** Adam

Ein Auftrag trägt seine `art` selbst, und die Artenliste prüft nur, **ob** sie
auf der Grün-Liste steht — nicht, ob sie stimmt. **Die Absenderliste heilt das
nicht: Ein berechtigter Absender kann sich irren.**

**Bewusst nicht geschlossen.** Der naheliegende Einzeiler
(`ampel != "gruen" or bool(befehl)`) wurde am 31.08. gebaut, gemessen und
**zurückgenommen**: Er stellt jeden ausführbaren Auftrag unter
Zustimmungspflicht und brach fünf abgenommene Prüfzeilen. Das wäre ein **Umbau**
gewesen, keine Härtung — und Adams Entscheid ist, dass Hora Läufer bleibt.
Vollständige Messung: `docs/f-befunde-reihenfolge.md`, F-16.

**Was den Fall heute dämpft, gemessen:** Die rote Wortsuche läuft ausdrücklich
**auch über das `befehl`-Feld** (`auftragsbuch.py:188`). Eine falsch deklarierte
`art` umgeht also die Absender- und die Wortschranke nicht.

### C-2 · Kein Rückweg über einzelne Commits

**gemessen am:** 31.08.2026 · **offen seit:** unbekannt · **wer entscheidet:** Adam

**Gemessen: `hora.py` enthält keinen einzigen `git`-Aufruf.** Hora committet
nicht — was ein Auftrag im Arbeitsbaum hinterlässt, bleibt dort liegen, bis ein
Mensch es ansieht. **Ein `git revert` als Rückweg gibt es für einen Hora-Lauf
also nicht**, weil es nichts zu reverten gibt.

**Ob das ein Mangel ist, hängt an den Aufträgen:** Ein lesender Auftrag
hinterlässt nichts. Ein schreibender hinterlässt einen unbeobachteten
Arbeitsbaum — und der nächste Lauf fährt seinen Regressionstest darüber.

### C-3 · Keine Obergrenze für Läufe pro Nacht

**gemessen am:** 31.08.2026 · **offen seit:** unbekannt · **wer entscheidet:** Adam

**Gemessen: es gibt keine.** `FEHLGRENZE 3` begrenzt die **Fehlserie**,
`WIEDERKEHR_FEHLGRENZE 3` das Wiederholen eines scheiternden Wiederkehrers,
`_AUSGABE_GRENZE` die Protokollgröße. **Eine Obergrenze für erfolgreiche Läufe
existiert nicht** — die Begrenzung kommt heute allein aus der Länge der
Auftragsliste und aus dem Kontingent (Schranke 8).

### C-4 · Wird ein Auftrag *während* des Laufs rot?

**gemessen am:** 31.08.2026 · **beantwortet** · **wer entscheidet:** —

**Gemessen: Die Frage stellt sich so nicht.** Der Regressionslauf läuft
**vor** und **nach** dem Befehl (Schranken 5 und 6), nicht nebenher. Wird das
Fundament *durch* den Befehl rot, greift der Nachher-Lauf: `erfolg and
nachher_ok` ist dann falsch, der Auftrag wird **nicht abgehakt**, der
Fehlserien-Zähler steigt (`hora.py:697–711`).

**Die verbleibende Lücke ist eine andere und kleiner:** Zwischen Vorher-Lauf und
Befehl liegt ein Fenster, in dem ein *anderer* Vorgang das Fundament rot machen
könnte. Bei einem Schloss, das nur einen Lauf zulässt, ist der einzige Kandidat
ein Mensch am Rechner.

### C-5 · Die Zahlen, die dieses Papier belegen sollten, liegen nicht hier

**gemessen am:** 31.08.2026 · **offen** · **wer entscheidet:** Adam

Die vier Zahlen aus dem Messauftrag (grüne Läufe seit 18.08. · davon mit
`befehl` · was sie taten · wie viele unter F-16 gestoppt worden wären) sind am
Bau-Rechner **nicht messbar**: `~/.claude/hora/` und `~/.claude/auftragsbuch/`
existieren dort nicht, und **`scripts/log_sync.sh` sichert sie nicht** — es
sichert Gespräche und Ausarbeitungen.

**Damit liegt das Protokoll eines Läufers, der Befehle ausführt, an genau einem
Ort.** Fällt der Server aus, ist es weg.

---

## Abschnitt D — Zulieferung, kein Tor

Die Messung aus C-5 **hält keine Entscheidung auf.** Sie wandert hierher, wenn
sie vorliegt, und ergänzt Abschnitt C. **Regelwerk und Messung laufen
nebeneinander** — das ist die Anwendung der Regel *schnelle Entscheidungen, kein
Aufschub* (`CLAUDE.md`) auf diesen Fall.

---

## Was dieses Papier NICHT ist

**Kein Prüfer und kein Wächter.** Es ändert nichts an `hora.py` oder
`auftragsbuch.py`; beim Erstellen wurde an beiden **keine Zeile** angefasst.
Wer es liest und eine fehlende Schranke bemerkt, schreibt sie in Abschnitt C.
