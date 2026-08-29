<!-- ROLLE: pruefliste-sdk-sprung -->
# Prüfliste: der SDK-Sprung, wenn Adam das Fenster setzt

**Stichtag:** 29.08.2026, 17:3x · **überholt durch:** — · **maßgeblich ist diese Datei**
**Gilt für:** Update-Auftrag `2026-08-29_bauauftrag-offene-updates-einspielen.md`, Schritt 2
**Belege:** `BEFUND-klonlauf-sdk-0.2.148.md` (Messungen), `BEFUND-sdk-aenderungsnotizen-0.2.127-0.2.148.md` (Notizen)

> **`[ERWEITERT 29.08., Adam über Engywuck]` Die ganze Kette, verbindlich:**
>
> **Node → SDK-Fenster → Rang 2 der Erkennungsseite → Ultracode → erstes Postfach.**
>
> Damit ist auch Adams Frage *[wann ist Ultracode dran?]* beantwortet: **nach**
> Rang 2 der Erkennungsseite und **vor** dem ersten Postfach — genau an der
> Stelle, die `CLAUDE.md` als Prüfstelle benennt (*nach dem Bau der
> Eingangs-Absicherung, bevor das erste fremde Postfach hinterlegt wird*).
>
> **Der Grund für diese Position, und er ist der eigentliche Punkt:** Ultracode
> misst in die Breite. Eine Breitenmessung auf einem Stand, der sich in den
> nächsten Tagen noch zweimal ändert (Node, SDK), ist verlorenes Kontingent —
> vierte Ultracode-Bedingung: *Der Code ist stabil genug, dass das Ergebnis
> nicht binnen Tagen veraltet.* Und sie muss **nach** der Erkennungsseite
> laufen, weil erst dann der Gegenstand vollständig ist.
>
> **Ausgelöst wird er von der Kontroll-Rolle, nicht von der Bau-Rolle** — der
> Befund ginge sonst zuerst an den Erbauer, der ihn über die eigene Arbeit
> bewertet. Micks Anteil ist, den zu prüfenden Commit zu benennen und gepusht
> zu haben.

> **Reihenfolge, verbindlich: Node zuerst, SDK danach — in GETRENNTEN
> Fenstern.** Gehen beide in einem Zug und danach ist etwas rot, weiß niemand,
> welche Hälfte es war. Node ist der riskantere Sprung (root, Paketquelle,
> `pandoc` als Rückabhängigkeit) und gehört in das Fenster, in dem Adam
> danebensitzt. Node-Zettel: `ZETTEL-node-22-auf-24.md`.

---

## Der Pin: DREI Zeilen, nicht eine

**Adams Auflage ① vom 29.08.:** Der Pin ist kein eigener Punkt, sondern Teil
dieser Liste — damit er nicht als loser Wunsch danebenliegt.

```
claude-agent-sdk==0.2.148
mcp==1.29.1
anyio==4.14.2
```

**Adams Auflage ②: Die Werte sind ABGELESEN, nicht getippt.** Quelle:
`../probe-sdk/.venv`, der Arbeitsbaum, in dem der Sprung am 29.08. tatsächlich
gefahren wurde (`pip freeze`, 17:37 Uhr). **Das ist die Paarung, die geprüft
ist** — nicht die, die man sich zusammenstellen würde.

Eine Beobachtung, die dabei abfiel: **`anyio 4.14.2` stimmt bereits mit dem
VPS überein** (der Mac liegt auf 4.13.0). Der Sprung zieht dort also nichts
Neues nach — nur der Mac wird angehoben, und das ist ohnehin die verabredete
Richtung.

### Warum `mcp` und `anyio` mitgepinnt werden

Sie sind **Mitzieher des SDK**, keine eigene Wahl — und genau deshalb driften
sie unbemerkt. Gemessen am 29.08. bei **identischem** SDK 0.2.127:

| | `mcp` |
|---|---|
| Mac | 1.27.1 |
| VPS | 1.28.1 |
| Engywucks Container | 1.29.1 |

An `mcp` hängt der In-Process-Transport des Suchservers — und daran hängen die
**WebSearch-Kostenschranke** (💰, Rang A) und die Ausfall-Erkennung. `anyio`
ist die zweite SDK-Abhängigkeit und driftet mit.

**Beide oder keins.** Nur das Paket zu pinnen, das gerade auffiel, wäre wieder
eine Aufzählung statt einer Menge.

### Der Vorbehalt, den Adam kennen muss

Ein `mcp==`-Pin bindet gegen die Spanne, die das SDK selbst verlangt
(`>=1.23.0,<3.0.0`). Fordert ein künftiges SDK mehr, **kollidiert die
Auflösung beim Installieren — nicht im Betrieb.** Das ist die richtige
Fehlerrichtung (laut, im Wartungsfenster), aber es macht jeden künftigen
SDK-Sprung zu einem Drei-Paket-Vorgang. Der Preis ist vertretbar; er ist hier
benannt, damit er später niemanden überrascht.

---

## Die Schritte im Fenster

1. **Ist-Stand einfrieren** — `pip freeze` auf Mac und VPS, abgelegt, bevor
   irgendetwas installiert wird. Ein Rückweg, der erst im Fehlerfall erfunden
   wird, ist keiner.
2. **Start-Wächter scharf** — er ist seit dem 29.08. repariert (Stelle 7:
   Lebensnachweis beim Abkoppeln; Engywucks Fund ①: `pgrep` durch `ps`
   ersetzt). **Vor dem Sprung prüfen, dass er einen echten Prozess findet** —
   `scripts/test_start_waechter_b1.py`, Zeile „Prozesserkennung findet einen
   echten Prozess".
3. **Die drei Zeilen in `requirements.txt`** eintragen (oben, unverändert).
4. **Installieren**, erst auf dem VPS — der trägt den Betrieb und ist die
   Bezugsgröße; der Mac folgt ihm, nicht umgekehrt.
5. **Regressionslauf auf beiden Maschinen.** Erwartung: 62/62. Die
   Pin-Divergenz-Zeile (C2) muss **grün** werden — sie ist heute der einzige
   Hinweis darauf, dass installiert und gepinnt auseinanderliegen.
6. **Den Suchpfad ausführen**, nicht nur den Lauf ansehen: Der In-Process-
   Transport wurde in 0.2.140 umgebaut, und die Kostenschranke hängt daran.
7. **Den Pin-Kommentar in `requirements.txt` nachziehen** — dort steht heute
   `0.2.127 -> CLI 2.1.219`. Nach dem Sprung ist die gebündelte CLI eine
   andere; **die Zahl ist abzulesen, nicht zu tippen**
   (`<sdk>/_bundled/claude --version`).

## Was NICHT in dieses Fenster gehört

- **Die 18 übrigen Fassungsunterschiede** zwischen Mac und VPS
  (`BEFUND-maschinen-gleichstand-messung.md`). Sie sind eine Entscheidung
  fürs Wartungsfenster, keine Reparatur — und ein `pip install --upgrade`
  über 79 Pakete am Produktivsystem ist ein eigener Vorgang.
- **Node.** Eigenes Fenster, davor.

## Der Klon

`../probe-sdk` hat den Sprung gefahren und wird **nach** dem Ablegen dieser
Liste geräumt (R4: keine Streu-Bäume). **Genau deshalb stehen die drei
Fassungen oben** — danach wäre die gemessene Paarung nur noch rekonstruierbar,
und rekonstruiert ist nicht gemessen.

Wiederaufbau, falls nötig:
`git worktree add --detach ../probe-sdk <commit>`, eigene venv, `pip install -r requirements.txt`.
