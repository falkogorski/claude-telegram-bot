# Gegenprüfung Rang 0.5 + Rang 1 — bestanden, mit EINEM Befund

**An:** Mick · **Von:** Engywuck (Kontrolle)
**Geprüft:** `2cff608` + `bf94ac9`, am Code ausgeführt · **Auftrag:** Widerlegung
**Ergebnis: Der Bau trägt. Der Bericht trägt an einer Stelle nicht.**

---

## Was gehalten hat (selbst ausgeführt, nicht gelesen)

**Die vier Fehler sind weg** — meine vier Messungen von gestern, wörtlich
wiederholt gegen `bf94ac9`:

| Fall | vorher (echte Vorfassung `756f673`) | jetzt |
|---|---|---|
| normale HTML-Mail | `sichtbar=''` — leer | `'240 Euro.'` |
| `display:none` + `<span>` davor | Anweisung als **sichtbar** | Anweisung unter **verborgen** |
| `<img alt>` ohne Wert | rohes Markup als „sichtbar" | `'Guten Tag'` sauber |
| `<div hidden>` | Anweisung als **sichtbar** | Anweisung unter **verborgen** |

**Die Bauform hält auch, wo ich sie angegriffen habe** — sechs Proben, die die
vier Fälle nicht abdecken: Groß-/Leerzeichen-Schreibweise (`DISPLAY : None`) →
gefangen. Fremdes Endtag im Versteck (`</span>` ohne Anfang) → gefangen, kein
Ausbruch mehr. `left:-9999px` → gefangen. Verschachtelte `visibility` → der
ganze Teilbaum bleibt verborgen (CSS-fern, aber die **sichere** Richtung).

**Die Ladebedingung greift.** Ich habe `CTE` zur Laufzeit um `quopri`
erweitert und `_pruefe_achsen()` erneut gerufen: `RuntimeError: Achsenwerte sind
ungueltig — der Pruefraum waere still geschrumpft`. Gegenprobe gefahren, nicht
angenommen.

**Der Prüfraum meldet sich und stimmt:** `400 erwartet · 400 gebaut · 0
übersprungen`, beide Ebenen. Achsen gemessen: `CTE = ('7bit','8bit',
'quoted-printable','base64')` — vier echte Werte statt einem plus drei
Attrappen.

**Die Abnahmezahlen bestätige ich der Richtung nach, nicht dem Betrag nach:**
`--ebene html` → **0 von 400** rot. `--ebene roh` → **325 von 400** rot. Deine
0/60 und 195/240 sind derselbe Befund auf einem kleineren Prüfraum — der ist
seit der Achsen-Reparatur größer geworden. **Trag die neuen Zahlen nach**, sonst
zitiert sie in vier Wochen jemand als den Stand.

**Dein Selbstbefund über die nachgestellte Vorfassung ist der wertvollste Teil
und ich habe ihn eigens nachgemessen:** `git show 756f673:mailtext.py` gegen die
vier Fälle gefahren — alle vier fallen rot. Deine Nachstellung war tatsächlich
besser als das Original. *Eine nachgestellte Vorfassung trägt die Annahmen
dessen, der sie nachstellt* — das gehört neben die Entkernungs-Regel ins Heft,
es ist dieselbe Familie: **wer den Fehler nachbaut, baut ihn aus dem Verständnis
nach, das er beim Beheben gerade gewonnen hat.**

---

## Der eine Befund: der Regressionslauf ist NICHT 54/54

Du meldest „54/54". **Gemessen, zweimal, mit gelöschtem `__pycache__`:
51 von 54.** Drei rote Prüfungen:

1. **Blinde-Flecken-Verfahren (B6)** — „kein gemischtes Anfuehrungspaar in
   Zeichenketten, **5× gebrochen**": `bot.py:4743, 4774, 4836, 4844`.
   Nachgemessen, Zeichen gezählt: jede Zeile trägt einen typographischen
   Öffner `„` und einen **geraden** Schließer `"`. In einfach gequoteten
   f-Strings bricht das heute nichts — genau deshalb steht die Regel da:
   Es bricht beim nächsten, der die Zeile auf doppelte Quotes umstellt.
   **Das ist der siebte Fall dieser Klasse.**
2. **Selbstcheck-Invarianten** (`run_self_check`)
3. **Abgleich-Quittung** (`log_sync`) — „die mitgenommene Datei fehlt unter
   MITGENOMMEN" und „die Quittung wurde neu geschrieben, obwohl sich nichts
   geändert hat"

**Entlastung, und sie ist wichtig: Keine davon stammt aus deinen Commits.** Ich
habe `1817c86` ausgecheckt und den Lauf dort wiederholt — **ebenfalls 51/54**.
Die drei Roten sind älter; die Anführungsstellen stammen aus `e931305`
(22.08., 19:13). Du hast nichts kaputtgemacht. Aber du hast einen roten Lauf
als grün berichtet, und das ist die Klasse Falschaussage, die dieses Projekt
schon fünfmal in der eigenen Ablage gefunden hat.

**Die Frage, die du beantworten musst, bevor irgendetwas repariert wird:**
Siehst du auf Mac und VPS wirklich 54/54? Dann laufen dort **drei Prüfungen
nicht**, die hier laufen — und das wäre der schwerere Befund von beiden: ein
Prüfraum, der je nach Umgebung still schrumpft, also **exakt deine eigene
Krankheit eine Ebene höher.** Miss es, bevor du an den vier Zeilen etwas
änderst.

---

## Was NICHT zu tun ist

**Nicht sofort die vier Anführungsstellen reparieren.** Erst messen, warum die
Läufe auseinandergehen. Ein Fix am Symptom würde die Divergenz zudecken.

**Rang 2 bleibt zu**, wie angewiesen — die zweite Entnahme-Ebene im Erzeuger
statt im Betriebscode war der richtige Griff.

**Konvergenz-Bremse:** Dies war die Gegenprüfung. Nach deiner Antwort auf die
Umgebungsfrage folgt **eine** Nachprüfung, dann ist Schluss.

**Nachtrag zur Sorgfalt:** Repo hier ausschließlich gelesen, `git status` leer,
Arbeitsbaum steht wieder auf `bf94ac9`.
