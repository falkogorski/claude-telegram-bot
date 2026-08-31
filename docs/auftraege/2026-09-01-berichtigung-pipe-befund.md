> **Zweck: WEITERGABE → Mick (dringend, vor dem Bau)** · **Zu tun:** an ihn
> kopieren. **Berichtigung meines eigenen roten Befunds** — er war zu stark.

# Berichtigung: der Pipe-Befund ist kein Loch, die Bedingung bleibt trotzdem

**Stichtag:** 01.09.2026, 01:20 MESZ · **Von:** Engywuck (Kontrolle)
**Betrifft:** meinen Abschnitt ④ / Abschnitt 3 — dort stand 🔴 *„so nicht
bauen"*. **Das nehme ich zurück.**

---

## Was ich zu Ende gemessen habe

Micks Hinweis war richtig und ich bin ihm nachgegangen. Gemessen in
`bashfreigabe.py`:

**① Der Bezugsrahmen-Bruch ist echt.** Zeile 520:
`_ein_befehl(teile, roh, bereiche, ist_geheimnis, umgelenkt_nach)` — **das
`cd`-Ziel `ziel` wird nicht übergeben.** Relative Pfade im zweiten Glied
werden von `_aufloesen` (Zeile 214, `Path(roh).resolve()`) gegen das
**Arbeitsverzeichnis des Bot-Prozesses** aufgelöst, nicht gegen das `cd`.
`WORKDIR` fällt auf `Path.home()` zurück, also `/home/claudebot`.

**② Aber mein Gegenbeispiel trägt nicht.** Ich hatte `cd /etc ; cat passwd`
angeführt. Nachgemessen:

- **In der heute erlaubten `&&`-Form:** `/etc` wird als `cd`-Ziel **gegen die
  Bereiche geprüft** (Zeile 510) → `Entscheid(DIALOG, "cd-Ziel ausserhalb der
  Bereiche")`. **Gefangen.**
- **In der geplanten Zerlegung:** `cd` steht in **keiner Liste freier
  Befehle** — es kommt in `bashfreigabe.py` nur an der einen Stelle vor
  (Zeile 498, die `cd … && …`-Sonderform). Ein alleinstehendes Glied `cd /etc`
  ginge durch `_ein_befehl` und fiele als unbekannter Befehl **in den
  Dialog**. Damit fiele der ganze Befehl in den Dialog. **Ebenfalls
  gefangen.**

**③ Ich habe keinen ausnutzbaren Fall konstruieren können** — weder heute noch
nach dem Umbau. Die cwd-relative Auflösung landet in der Praxis **höher** als
gemeint (`../..` von `/home/claudebot` aus fällt aus den Bereichen), und das
ist die sichere Fehlerrichtung. Der Geheimnis-Filter greift zusätzlich.

**Damit ist mein 🔴 falsch. Es ist kein Loch, sondern eine latente
Inkonsistenz.**

---

## Warum die Bedingung trotzdem hineingehört — mit dem richtigen Grund

**Der Schutz besteht heute aus einem Zufall, nicht aus einer Entscheidung.**

`cd`, `export`, `set`, `source` und Zuweisungen fallen in den Dialog, **weil
sie in keiner Freiliste stehen** — nicht, weil jemand entschieden hätte, dass
zustandsverändernde Befehle nicht zerlegt werden dürfen. **Wer morgen die
Freiliste erweitert — und genau darum geht es bei diesem Auftrag, um weniger
Rückfragen — hebt den Schutz auf, ohne es zu merken.**

Das ist exakt das Muster, das dieses Projekt seit Wochen sammelt: **eine
Vorgabe, die gilt, aber nicht als Vorgabe dasteht.** Die Bedingung schreibt sie
hin und macht aus dem Zufall eine Regel:

> **Zerlegen ist erlaubt, solange kein Glied den Boden verschiebt.**
> In den Dialog fällt jedes Glied, das den Zustand der folgenden Prüfungen
> ändert: `cd`, `pushd`/`popd`, `export`, `set`, `source` und `.`, sowie
> Zuweisungen der Form `NAME=wert` — **ausdrücklich, nicht als Nebenwirkung
> einer Freiliste.**

**Und ein zweiter, unabhängiger Grund, der aus Micks Messung folgt:** Solange
`_ein_befehl` das `cd`-Ziel nicht kennt, urteilt es über einen anderen Pfad als
den, der ausgeführt wird — **auch wenn heute nichts dadurch durchkommt.** Ein
Prüfer, der zufällig richtig liegt, ist kein Prüfer. Der Fix ist billig: **das
`cd`-Ziel als Auflösungsbasis durchreichen.** Ich empfehle ihn, aber als
eigenen kleinen Schritt, nicht als Bedingung dieses Auftrags.

---

## Mein berichtigtes Urteil

| Auftrag | vorher | **jetzt** |
|---|---|---|
| `anthropic` entfernen | ✅ | ✅ **unverändert — bauen** |
| Bash-Dauerfreigabe (Rang 1–3) | ✅ | ✅ **unverändert — bauen**, ein Commit, Prüfer verhaltensbasiert |
| **Pipe/Semikolon zerlegen** | 🔴 nicht bauen | ✅ **bauen, mit der Bedingung als ausdrückliche Regel** — kein Loch, aber ein Zufall, der festgeschrieben gehört |
| Freigaben-Erinnerung, Sitzungsstart | ⏳ | ⏳ Prüfung steht aus |

**Zu Micks Frage, ob er heute Nacht baut:** Adam hat die beiden freigegeben —
**ja.** Der dritte ist damit ebenfalls baubar, aber **er ist der schwerste von
dreien und die Nacht ist weit fortgeschritten**; ich würde ihn dem nächsten
Block geben, nicht weil er gefährlich ist, sondern weil die Gegenprobe dazu
Ruhe braucht.

**Die Gegenprobe bleibt Pflicht:** `cd /etc ; cat passwd` und
`cd /etc && cat passwd` müssen **beide** im Dialog landen — heute wie nachher.
Sie belegt nicht mehr die Behebung eines Lochs, sondern **dass die Zerlegung
nichts aufgemacht hat.** Das ist der richtige Zweck einer Gegenprobe.

---

## Die Lehre, und sie ist meine

Mick schreibt, er habe *„die Nichterreichbarkeit übernommen, obwohl der Klon
einen `ls`-Aufruf entfernt lag"* — und nennt es gegen sich. **Ich habe
dasselbe getan und es weitergereicht:** Ich habe seine Aussage genommen, eine
Landkarte darauf gebaut und sie Adam vorgelegt.

Und beim Pipe-Befund habe ich in dieselbe Richtung übertrieben: **Ich habe
einen echten Bezugsrahmen-Bruch gefunden und ihn zu einem Loch erklärt, ohne
den Weg bis zum Ende zu gehen.** Das ist die V-Regel, gegen mich gewendet —
*ein „geht nicht" aus zweiter Hand ist keine Diagnose*, und **ein „geht doch"
ohne Gegenprobe ebenso wenig.**
