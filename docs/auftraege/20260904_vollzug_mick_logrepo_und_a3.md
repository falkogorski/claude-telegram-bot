> **Zweck: WEITERGABE → Engywuck** · **Zu tun:** deinen Klon nachziehen —
> **umgeschrieben.** Sonst nichts; die Kette ist zu Ende.

# Vollzug — Teil A vollständig, Log-Repo bereinigt

**Stichtag:** 04.09.2026, 22:15 · **Stand:** `f376372` · **Läufe:** 73/73
**Nenner:** A1, A2.1–A2.6 und A3 gefahren und je gemessen · **4 Prüfzeilen, die
die falsche Sache maßen** (drei davon meine, eine deine)

---

## Umgeschrieben

Adam hat den Force-Push gefahren: `3bb387fa → 4b2387b9`. **Beide bekannten
Klone stehen darauf**, VPS und Mac. Gemessen im nachgezogenen Klon:

```
Commits mit ausarbeitungen/rechnungen/ : 0
Objekte mit diesem Pfad                : 0
Rechnung 012-26 in der Objektliste     : 0
```

Der Zeitgeber läuft wieder; **drei Abgleiche danach** (22:06, 22:10, 22:15) —
der Zweig kommt nicht zurück, die Quittung nennt ihn als zurückgehalten.
**Dein Klon ist der dritte.**

## Deine zwei A3-Befunde

**① Das fehlende `-R` war real.** Ohne es wäre `saetze.json` flach gelandet und
der Generator hätte weiter `daten/saetze.json` gelesen — das berichtigte
Etikett wäre nie angekommen, ohne dass etwas fehlschlägt. Auf dem Server
nachgemessen: liegt in `daten/`, flach liegt nichts.

**② `ablage.py` war schon drin** — seit `fdd18f3`, eine Runde nach dem Stand,
den du geprüft hast. Fall elf greift auf dem Server: `L'Osteria/Bar` wird
abgewiesen, mit Hinweis auf stderr.

**Deine Prüfzeile dafür hätte nichts gemessen**, und das ist der vierte Fall
heute: `grep -c "Abreisetag-Satz"` liefert in **beiden** Fassungen `1`, weil
der alte Wortlaut im neuen Hinweis zitiert steht. Ersetzt durch
`BERICHTIGT 04.09.2026`.

## Vier Prüfzeilen, die die falsche Sache maßen

| | Sollte messen | Maß in Wirklichkeit |
|---|---|---|
| `grep -c "017-26"` (deine) | ob der Zähler die Nummer kennt | die Schreibweise — er speichert `17` |
| `grep -c "Abreisetag-Satz"` (deine) | ob das neue Etikett da ist | nichts, der alte Wortlaut steht zitiert |
| A2.1 „Ordner muss weg sein" (meine) | Wirkung des Filters | etwas, das nie eintritt — der Filter löscht nicht |
| `python3` statt `.venv/bin/python` (meine) | ob die Formel rechnet | ob das System-Python `openpyxl` hat |

**Alle vier hätten Adam an eine falsche Erwartung gebunden**, zwei davon mit
einem Alarm, der wie ein Befund aussieht. Deine Blaupause-Zeile trifft es —
*eine Prüfzeile über eine ungelesene Datei misst eine Vermutung*; die anderen
zwei ergänzen sie: **eine Prüfzeile muss den Zustand messen, den die Änderung
erzeugt, nicht den, den man sich vorstellt.**

Und eine fünfte Kleinigkeit derselben Familie: Dem A3-`rsync` fehlte als
einzigem Befehl im Block eine Erfolgsmeldung. Er schweigt bei Erfolg — Adam
sah einen hängenden Befehl, wo längst alles durch war.

## A3, gemessen auf dem Server

Formel rechnet 30/80/50/100 % zu 8,40 · 22,40 · 14,00 · 28,00 · Bemerkungszeile
im Template · Fall elf greift · der berichtigte Akzent ist dort
(`3 Extrastunden à 40 €`).

## Was noch offen ist

Nichts Scharfes. **F-15 und F-19** liegen bei dir bzw. in der Liste; **F-21**
ist bewusst zurückgestellt bis zur Nachmessung nach dem Deploy — der ist jetzt
gefahren, die Messung kann also stattfinden, sobald Claudia wieder gearbeitet
hat.

Der Kopf der F-Liste war übrigens falsch und ist berichtigt: Er führte vier
seit dem 31.08. erledigte Punkte als offen.
