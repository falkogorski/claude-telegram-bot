> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren. **Adams Antwort
> auf deine Frage nach dem iCloud-Ziel.** Klein, kein Sicherheitspfad.

# Nachtrag — wohin die Rechnungen sollen

**Stichtag:** 02.09.2026, 16:02 MESZ · **Von:** Engywuck (Kontrolle)
**Nenner:** 1 Adam-Entscheid · 1 Änderung an `rechnungen_ablegen.sh` ·
2 Namen, die du **misst, nicht tippst.**

## Adams Wortlaut, 02.09.

> *„unter deko-service nur rechnungen an deko-service … ordner für aktuelle
> rechnung lautet livesetup"*

Und heute Morgen im Bot-Chat, 10:05: *„Ich habe ein Ordner schon angelegt …
Live Setup heißt der Ordner. Den findest du schon. Und dann lege ich da zwei
Unterordner an. Das eine ist dann … Volvo Business Modul Norderney … und da
habe ich jetzt noch für nächste Woche auch schon wieder einen Auftrag in
Ingolstadt. Deswegen lege ich den zweiten Ordner direkt schon mal an."*

## Was das für dein Ziel heißt

**Dein Vorgabewert ist falsch für diese Rechnung, und ein fester Ordner kann
nie richtig sein:** `Business/Deko/DEKO-Service/_Aus-dem-Server` legt eine
LIVESETUP-Rechnung unter DEKO-Service ab — genau das, was Adam ausschließt.
**Das Ziel hängt am Kunden und am Projekt**, also an etwas, das nur der
Generator weiß.

**Die Struktur, wie Adam sie führt:** `Business/Deko/<Kunde>/<Projekt>/`.
DEKO-Service ist ein Kunde, LIVESETUP ein anderer, Norderney und Ingolstadt
sind Projekte darunter.

## Die Änderung — der Server sagt den relativen Pfad, das Skript trägt ihn

1. **Server:** Der Generator legt nach `ausgang/<Kunde>/<Projekt>/` ab, nicht
   flach nach `ausgang/`. Er kennt Kunde und Projekt aus den Rechnungsdaten.
2. **Hälfte 2:** `RECHNUNGEN_ICLOUD` wird `…/Business/Deko`, und der rsync
   überträgt **mit relativem Pfad** — `ausgang/livesetup/Norderney…/x.pdf`
   landet unter `Business/Deko/livesetup/Norderney…/x.pdf`. Kein `--delete`,
   `-u`, `--exclude='.*'` — wie gehabt. Ohne `--delete` berührt der Lauf
   fremde Kundenordner nicht; er legt nur ab, was er mitbringt.
3. **Fail-safe, damit nichts im falschen Kundenordner landet:** Dateien, die
   **ohne** Unterordner in `ausgang/` liegen, gehen nach
   `Business/Deko/_Aus-dem-Server/` — **nicht** unter DEKO-Service. Adams
   Regel gilt auch für den Fehlerfall.

## Zwei Namen, die du misst

**Der Kundenordner heißt bei Adam „livesetup" oder „Live Setup" — er hat es
heute zweimal verschieden gesagt.** Und der Projektordner *„Volvo Business
Modul Norderney"* ist von ihm angelegt, mit einem Namen, den nur die Platte
kennt. **Beides liest du aus seinem iCloud-Ordner ab** — du hast den Mac und
die TCC-Freigabe — und trägst den **gemessenen** Namen in die Rechnungsdaten
ein. Ein getippter Name legt einen zweiten Ordner daneben an, und dann gibt es
zwei Wahrheiten. Das ist der Fall vom Prüfraster, nur in klein.

**Gegenprobe:** eine Testdatei nach `ausgang/livesetup/<Projekt>/`, ein
Durchlauf, dann nachsehen, dass sie **dort** liegt und **nicht** unter
DEKO-Service. Vorher hinschreiben, dann messen.

## Was offen bleibt — klein, bei Adam

**Die Rechnungsnummer.** Sie richtet sich nach dem Abschlussdatum, und die
vergebenen Nummern stehen in den Kundenordnern auf dem Mac — Route A kennt nur
die Richtung Server → iCloud. **Für die heutige Rechnung sagt Adam die
Nummer**; 5.19 verlangt ohnehin die Rückfrage vor der Vergabe. Ob die
vergebene Liste später den Weg zurück zum Server nimmt, ist eine eigene
Entscheidung — nicht heute.
