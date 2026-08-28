# Bauauftrag — Botenpostfach: Grenze nach Absenderart trennen

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau)
**Angelegt:** 27.08.2026, 18:35 Uhr
**Freigabe:** Adam am 27.08.2026 um 18:32 Uhr (Daumen hoch auf die Frage von 17:09 Uhr)
**Umfang:** ein Eingriff in `bot.py`, drei Textstellen ziehen mit

---

## Warum — der Befund

Das Botenpostfach hält jeden Absender bei **fünf Sendungen je Stunde** an
(`bot.py`, Zeile 6337, gleitendes Fenster von 3600 Sekunden in
`_postfach_drosseln`, Zeile 6343).

**Der Riegel ist richtig gebaut und an der richtigen Stelle.** Am 28.07.2026 haben
zwei fehlerhafte Wächter zusammen sechsundzwanzig Nachrichten an Adam geschickt,
zwei je Minute, und nichts konnte sie stoppen. Ein Riegel an der Quelle hätte nur
der bekannten Quelle geholfen; dieser sitzt am Ausgang und hilft allen.

**Er trifft aber zwei verschiedene Dinge mit demselben Maß.** Eine Wächter-Meldung
entsteht von selbst — wenn davon fünf in einer Stunde kommen, stimmt etwas nicht.
Eine Lieferung, die Adam angefordert hat, entsteht auf seinen Wunsch. Dass davon
nur fünf je Stunde durchkommen, ist keine Sicherung, sondern eine Behinderung.

**Belegt am 27.08.2026:** Meine Ansagen und meine Lieferungen laufen unter demselben
Absender. Vier Ankündigungen am Nachmittag haben die Plätze verbraucht, die das
angeforderte PDF gebraucht hätte. Bis 18:35 Uhr warteten drei Sendungen in der
Ausgangsablage, darunter zwei Fassungen eines Bauauftrags, den Adam selbst
freigegeben hatte.

**Adams Maßstab, wörtlich am 27.08. um 17:03 Uhr:** *„Wenn ich 20 pro Stunde brauche
oder 100, die sollte da durchkommen."*

---

## Auftrag — Grenze je Absender nachschlagen statt fest

**Stelle:** `bot.py`, Zeilen 6337 bis 6358.

**Weg:** `POSTFACH_GRENZE` bleibt die **Vorgabe** und bleibt bei fünf. Daneben tritt
eine Zuordnung, die einzelnen Absendern eine eigene Grenze gibt. `_postfach_drosseln`
schlägt die Grenze für den jeweiligen Absender nach, statt die feste Zahl zu
verwenden.

**Eintrag zum Start:** `claudia` erhält **hundert**.

**Warum hundert und nicht dreißig:** In meiner Vorlage von 17:09 Uhr stand dreißig.
Adam hatte in derselben Minute selbst hundert genannt. Ich nehme seine Zahl — sie
deckt seinen Bedarf ab, und der Riegel greift trotzdem: Eine echte Endlosschleife
erzeugt Tausende, nicht Hunderte. Der Wert gehört nach außen
(`POSTFACH_GRENZE_CLAUDIA` oder eine Zuordnung als Umgebungsgröße), damit er ohne
Codeänderung nachziehbar ist.

**Die Richtung der Liste ist der entscheidende Teil.** Eingetragen wird, wer
**mehr** darf — nicht, wer weniger darf. Ein Wächter, der morgen dazukommt, steht
nicht in der Liste und bekommt damit von selbst die strenge Vorgabe. Andersherum
wäre der neue Melder ungebremst, und niemand würde es bemerken, bis er flutet.

**Der Vergleich muss unabhängig von Groß- und Kleinschreibung sein.** Die Aufträge
tragen `"herkunft": "Claudia"`, die Melder legen `blume` und `hora` ab. Ein
Nachschlagen auf den kleingeschriebenen Namen fängt beides.

---

## Was diese Änderung ausdrücklich NICHT leistet

**Sie schützt gegen Fehler, nicht gegen Absicht.** Das Feld `herkunft` wählt frei,
wer den Auftrag ablegt — wer sich `claudia` nennt, bekommt die hohe Grenze. Das war
schon vor dieser Änderung so und wird durch sie weder besser noch schlechter; wer in
die Ausgangsablage schreiben darf, hat ohnehin Zugriff auf das Konto. Es gehört
trotzdem gesagt, damit niemand den Riegel für mehr hält, als er ist.

**Sie fängt keinen Fehllauf unter meinem eigenen Namen.** Hänge ich in einer
Schleife, sind hundert Sendungen je Stunde immer noch hundert. Wer das schließen
will, braucht einen zweiten Deckel über alle Absender zusammen — als Möglichkeit
benannt, für jetzt **nicht empfohlen**, weil er ein neues Verhalten einführt, das
niemand beobachtet hat.

---

## Was kann brechen und wer merkt es

| Was | Wer merkt es | Vorkehrung |
|---|---|---|
| **Zwei Meldungstexte nennen die feste Zahl.** `bot.py` Zeile 6257 (Grund im zurückgestellten Auftrag) und Zeile 6406 (Sammelmeldung: *„mehr als 5 in einer Stunde"*). Nach der Änderung stünde dort für Claudia eine falsche Zahl. | Niemand — es liest sich plausibel | Beide Stellen auf die **für diesen Absender geltende** Grenze umstellen. Das ist Teil des Auftrags, nicht Feinschliff |
| **Ein Test besteht auf der festen Zahl fünf.** Ob es einen gibt, konnte ich nicht prüfen — der Suchlauf über den Testordner wurde abgebrochen. Ungeprüft. | Der 4-Uhr-Check, laut | Vor dem Bau `tests/` und die Selbsttests in `bot.py` auf `POSTFACH_GRENZE` und `_postfach_drosseln` durchsehen |
| **Die hohe Grenze wird zur Vorgabe für alle**, weil jemand die Zuordnung umdreht oder den Vorgabewert anhebt. Der Riegel vom 28.07. wäre still weg. | Niemand, bis es erneut flutet | Ein Test, der einen **unbekannten** Absender anlegt und prüft, dass er nach fünf Sendungen gedrosselt wird |
| **Der Zähler lebt nur im Arbeitsspeicher** (`_postfach_zaehler`, Zeile 6339). Ein Bot-Neustart setzt ihn zurück; unmittelbar danach ist die Grenze wirkungslos. | Niemand | **Bestehender Zustand, keine Regression** — hier nur vermerkt, damit er nicht als Nebenwirkung dieser Änderung gilt. Eine eigene Entscheidung, ob das bleiben soll |
| **Die Zuordnung wächst nicht mit.** Eine neue Sitzung liefert unter eigenem Namen und wird bei fünf gebremst, ohne dass klar ist, warum. | Die betroffene Sitzung, verspätet | Gewollt so — die strenge Vorgabe ist die sichere Richtung. Der Eintrag ist eine Zeile und gehört zur Einrichtung einer neuen Sitzung |

---

## Randbeobachtung, nicht Teil des Auftrags

Die Dokumentation (`docs/boten-postfach.md`) verlangt **atomares Ablegen**: erst
unter Temp-Namen schreiben, dann umbenennen, damit der Bot keine halb geschriebene
Datei greift. Beim Ablegen aus der Kommandozeile ist das leicht zu übergehen — der
Weg über `>` schreibt direkt unter den Zielnamen. Kein Befund im Code, sondern eine
Auflage an jeden, der von Hand ablegt.
