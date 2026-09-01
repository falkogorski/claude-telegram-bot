> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren. **Adams Freigabe
> liegt vor.** Ein Bauschritt, klein, aber mit einer Falle — Abschnitt 2.

# Bauauftrag: Der Weg nach draußen bleibt im Dialog, auch im Auto-Modus

**Stichtag:** 01.09.2026, 06:19 MESZ · **Von:** Engywuck (Kontrolle)
**Adams Freigabe:** 01.09.2026 — *„ja, curl-Sperre freigegeben, mach fertig für
Mick"*
**Herkunft:** Micks Fund vom Nachtblock, von mir am Code bestätigt.

---

## 1 · Warum

**Adams Bedingung für den Auto-Modus, am 31.08. um 12:00 im Wortlaut:**

> *„Die Baukastenstufe ja. Gerne, **wenn die Sperren vorher als Verbotsregeln
> hinterlegt werden.**"*

**Gemessen in `bashfreigabe.py`:** `curl` und `wget` kommen dort **nicht vor.**
Die Abweisungen decken Geheimnis-Pfade, eine weitere Stelle und `cd` unter
`.claude`. Ein unbekannter Befehl fällt in den **Dialog** — und den ersetzt die
Bash-Dauerfreigabe durch **Erlauben**.

**Damit ist Adams Bedingung zur Hälfte offen:** Für einen Auto-Modus ist der
ausgehende Kanal die naheliegendste Verbotsregel, und es gibt keine. Es berührt
zudem seinen Grundsatz vom 21.08. in der zweiten Richtung — *„Hinaus: sensible
Daten verlassen das System nicht."*

**Was unverändert hält und nicht angefasst wird:** Repo-Schreibsperre (8.7),
Geheimnis-Schranke, Kosten-Werkzeuge, die Abweisungen aus `bashfreigabe.py`.

---

## 2 · 🔴 Die Falle: ein DIALOG-Urteil wirkt hier NICHT

**Das ist der wichtigste Satz dieses Auftrags.** Der naheliegende Bau — in
`bashfreigabe.entscheiden` für `curl` ein `Entscheid(DIALOG, …)` zurückgeben —
**wäre wirkungslos.**

**Gemessen am Ablauf in `bot.py`:**

| Zeile | was geschieht |
|---|---|
| 3091 | `ABWEISEN` → `PermissionResultDeny` |
| 3100 | `FREI` → `PermissionResultAllow` |
| 3101–3103 | Kommentar: *„Alles Übrige fällt weiter unten in den Dialog"* |
| **3164** | **`always_allowed_tools` … → `PermissionResultAllow`** |

**Ein DIALOG-Urteil fällt genau in die Zeile, die die Dauerfreigabe abfängt.**
Der Kommentar bei 3101 stimmt seit heute Nacht nicht mehr — er stammt aus der
Zeit, als Bash gesperrt war.

**`ABWEISEN` wäre die falsche Antwort in die andere Richtung:** Adam könnte
einen `curl` dann auch bewusst nicht mehr freigeben. Er will **Rückfrage**,
nicht Verbot.

---

## 3 · Der Bau — dem vorhandenen Muster folgen

**Es gibt bereits genau dieses Muster im Code**, direkt darunter: Der
Geheimnis-Schutz ist mit dem Kommentar versehen *„vor jeder Auto-Freigabe
geprüft, **auch vor Always-Allow**"*. Er wirkt, weil der Kurzschluss selbst
`and not sensitive` verlangt.

**Also dasselbe noch einmal, nicht anders:**

1. Ein zweites Merkmal neben `sensitive` bestimmen — Vorschlag
   `spricht_nach_draussen`, aus demselben verbundenen Feld-Text (`_ref`)
   ermittelt wie `sensitive`.
2. Die Bedingung bei **Zeile 3164** um **`and not spricht_nach_draussen`**
   erweitern.
3. **Nichts anderes ändern.** Kein Eingriff in `bashfreigabe.py`, keine neue
   Prüfstelle, keine Umstellung der Reihenfolge.

**Anfangsbestand der Liste, bewusst knapp:**
`curl` · `wget` · `nc` · `ssh` · `scp` · `telnet`

**Und die Mengen-Regel richtig herum** — dasselbe Prinzip wie bei
`POSTFACH_GRENZEN`: **Eingetragen wird, wer mehr darf, nie wer weniger darf.**
Hier heißt das: Die Liste nennt die gesperrten Befehle ausdrücklich; ein
Befehl, der morgen dazukommt und nach draußen spricht, ist **nicht**
automatisch erfasst. **Das ist die ehrliche Grenze dieses Baus und gehört als
Zeile in den Kommentar** — sie ist bewusst so, weil eine Erkennung „spricht
das nach draußen?" Inhalt prüfen müsste, und Inhalt lässt sich tarnen.

**Warum knapp und nicht lang:** Adams Ausgangspunkt war, dass das Drücken
aufhören soll. Eine lange Liste höhlt den Auto-Modus wieder aus. Sechs Befehle
sind der tragbare Preis.

---

## 4 · Der Prüfer — Verhalten, nicht Text

**Die Prüfzeile misst:** Ein Bash-Aufruf mit `curl …` **bei gesetzter
Dauerfreigabe** ergibt einen **Dialog**, kein Erlauben.

**Gegenprobe, und sie ist Pflicht:** Die Bedingung `and not
spricht_nach_draussen` aus Zeile 3164 entfernen → **die Prüfzeile muss rot
werden.**

**Die drei Handgriffe davor, weil an dieser Stelle schon einmal ein
Geisterbefund entstanden ist:**
- **`__pycache__` löschen**, sonst misst du eine übersetzte Vorfassung.
- **Den Eingriff verifizieren** (`assert alt in t` vor der Ersetzung) — eine
  Ersetzung, deren Suchtext nicht vorkommt, ändert nichts und liest sich
  hinterher wie „der Schutz hält".
- **Die erwartete rote Zeile vorher hinschreiben**, sonst nimmt man jede
  beliebige rote Zeile als Bestätigung.

**Zusätzlich eine Zeile in die Gegenrichtung:** Ein gewöhnlicher Lesebefehl
(`cat` im Arbeitsbereich) bleibt bei gesetzter Dauerfreigabe **frei**. Ohne
diese zweite Zeile belegt der Prüfer nur, dass etwas blockiert — nicht, dass
der Auto-Modus noch funktioniert.

---

## 5 · Doku-Spiegel im selben Commit

- **Der Kommentar bei `bot.py:3101–3103** — *„Alles Übrige fällt weiter unten
  in den Dialog"* — **stimmt seit heute Nacht nicht mehr.** Bitte richtigstellen:
  Er fällt in den Dialog, **außer** die Dauerfreigabe greift.
- **`/hilfe` und die Beschreibung des Auto-Knopfes**: dass ausgehende Befehle
  auch im Auto-Zustand nachfragen. Adam soll nicht überrascht werden, wenn
  ausgerechnet dort ein Dialog erscheint.

---

## Auflagen

- **Nur die drei Schritte aus Abschnitt 3.** Kein Eingriff in `bashfreigabe.py`.
- **Prüfer verhaltensbasiert**, beide Richtungen, Gegenprobe gefahren.
- **Die ehrliche Grenze als Kommentar** — die Liste ist eine Aufzählung, kein
  Erkennungsverfahren.
- 💰 keine Kostenquelle berührt.
- **Regressionslauf vor dem Commit.**

**Was dieser Bau NICHT leistet, und das gehört Adam gesagt:** Er schützt gegen
Versehen und gegen einen Befehl, der über einen bekannten Weg hinausspricht.
Er schützt **nicht** gegen einen ausgehenden Weg, der morgen dazukommt und
nicht in der Liste steht. Die vollständige Antwort darauf ist die
Eingangs-Absicherung, die als eigener Strang aussteht — nicht diese sechs
Zeilen.
