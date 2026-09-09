> **Zweck: WEITERGABE → Mick** · **Zu tun:** drei Kleinigkeiten, kein
> Umbau. **M-1, M-2, M-3, M-5, M-6: abgenommen.** Die Reihenfolge für den
> Rest steht unten, sobald Adams Entscheide da sind (sie kommen mit diesem
> Papier oder kurz danach).

# Abnahme Stand `e3596fd` — fünf von fünf gebauten Punkten gemessen

**Stichtag:** 09.09.2026, 11:56 (`date`, Berlin) · **Gemessen im Klon:**
`test_bashfreigabe.py` **141/141**, `test_postfach_wiederaufgriff.py` 13/13,
`test_rechnungen_ablegen.py` 5/5 · **Zwei Gegenproben, erwartete Zeile vorher
notiert, Eingriff verifiziert:** Vorgabe `herkunft` entfernt → **genau** „das
Skript nennt seinen Absender" rot; Sofortmeldung entfernt → **genau** „die
Drossel meldet sofort, und nur einmal" rot. `dialog_gezeigt` an der
Sendestelle über `ast.Call` gemessen (Abwesenheits-Form, tragfähig).
`mv`/`cp` im Arbeitsbereich: Prüfzeile 104 existiert, mein Auftragspunkt war
überholt — richtig gemeldet statt gebaut.

**Deine drei Zahlen sind angekommen und ändern zwei Dinge:** Auto war an,
also gibt es einen Dialogpfad, den keiner von uns sieht — **ab jetzt misst
ihn M-3**, und die Wochenauswertung am 16.09. ist die erste, die zählt.
Mein `2>&1` war falsch; ein Ordner mit `&` im Namen ist die plausible Quelle.
Rang A repariert seit 29.08. — M-9 hat keine Vorbedingung mehr.

## Drei Kleinigkeiten

1. **Riegel-Datum, eine Ungleichung.** `auftragsbuch.py:76` schließt bei
   `heute > GILT-BIS`, der Tagescheck (`daily_check.sh:315`) meldet
   „abgelaufen" schon bei `heute >= GILT-BIS`. Am 09.09. sagt der Tagescheck
   „abgelaufen", der Riegel ist bis 23:59 offen. Dein Bericht übernahm die
   Tagescheck-Zeile. **Fix:** Tagescheck-Wortlaut am Stichtag „läuft heute
   ab", ab dem Folgetag „abgelaufen". Kein Umbau der Logik.
2. **Der `&`-Ordner ist kein Befund an der Positivliste** — gequotet läuft
   er frei (Zeile „gequotetes & im Dateinamen" grün). Es ist eine
   Verhaltensregel für Claudia: **Pfade immer in Anführungszeichen.** Das
   geht über Adam an sie, nicht über dich; ich nenne es hier, damit du es
   nicht als offenen Punkt führst.
3. **M-4 nach Adams Wort: `pandoc` + `typst`, wie bei den Doppel-Lieferungen.**
   Damit wandert meine Netz-Auflage vom `url_fetcher` (weasyprint) an die
   Stelle, die bei typst nach draußen geht: **`@preview`-Paketimporte lädt
   typst beim ersten Gebrauch aus dem Netz.** Auflage also: das Skript
   erlaubt keine Paketimporte (oder läuft mit gefülltem `--package-path`
   ohne Netz), pandoc ohne `--extract-media` von URLs. Prüfer: Markdown mit
   Netzbild und mit `#import "@preview/…"` → PDF entsteht bzw. wird benannt
   abgewiesen, **kein** Netzzugriff (Attrappe). Danach in
   `BENANNTE_SKRIPTE`.

## Reihenfolge, sobald Adams Entscheide da sind

M-10 (git init Server, nach seinem Ja) → M-11 (Riegel nach seinem Wort) →
M-4 → M-8 (Fable, klein) → **eigener Block:** M-9 (SDK+CLI im Klon) → M-7.
