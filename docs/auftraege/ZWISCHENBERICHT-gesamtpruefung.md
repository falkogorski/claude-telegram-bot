<!-- ROLLE: zwischenbericht-gesamtpruefung -->
# Gesamtprüfung der Bot-Protokolle — Zwischenbericht 1 (Juli)

**Kopf:** 31.08.2026, 21:53 MESZ (Systemuhr abgelesen; der Container läuft auf UTC) · Kontroll-Sitzung
**Material:** 30 Protokolle, 14.07.–31.08. · **687 Adam-Nachrichten**, vollständig
extrahiert mit Kontrollzählung (687/687)
**Gelesen:** Blöcke 1–6 von 18 · **14.07. bis 25.07.**
**Geprüft gegen:** `MIGRATION.md` @ `717b059`, alle 124 Überschriften, plus `CLAUDE.md`

---

## Das Ergebnis vorweg: der Juli war gut

**Zwölfmal gesucht und gefunden, achtmal eine Lücke.** Das ist ein besseres
Verhältnis, als ich erwartet hatte — und es hat einen benennbaren Grund, den
auch Conni unabhängig gefunden hat: **Der Block-Weg über Adam an Mick hat
Entscheidungen binnen Stunden in die Ablage gedrückt.** Mehrere Anregungen
wurden **am selben Tag** zu einem Punkt.

### Gesucht, gefunden — kein Fund (12)

| Adams Anregung | landete als |
|---|---|
| Sichtbare/unsichtbare Transkription umschaltbar (22.07.) | **5.26**, angelegt am selben Tag |
| Technische Werkzeugspur ganz abschaltbar (24.07.) | **`/spur`**, 5.25 (d), eingebaut am selben Tag |
| Warteschlangen-Reihenfolge umdrehen (24.07.) | **5.5**, FIFO mit ausdrücklichem `[GEÄNDERT]` |
| Auto-/Plan-Modus statt Dauer-Rückfragen (15.07.) | **5.27** |
| „Dich selber trainieren" (24.07.) | CLAUDE.md-Grundsatz *Selbstlernende Assistenz*, datiert 24.07. |
| „Oma Lieschen merkt nichts davon" (24.07.) | CLAUDE.md-Grundsatz *Unsichtbare Komplexität*, datiert 24.07. |
| Bedeutungstragende Emojis vorlesen (24.07.) | Baustein `MIGRATION.md:1358` |
| Gesamtmemory über alle Instanzen (24.07.) | **5.11**, mit ehrlich benannter Grenze |
| Instagram-Reels wie YouTube (25.07.) | **5.14** |
| Recherche „was kann ein Assistent" (24.07.) | das **Fähigkeitsraster** vom 25.07. |
| Repo lesen dürfen (24.07.) | 8.7-Änderung vom selben Tag |
| Ethik-Kompromiss beim Business-Start (25.07.) | **W-Regel** in CLAUDE.md |

---

## Die acht Lücken

### A · Gebaut oder zugesagt, ohne jeden Eintrag

| # | Was | Ursprung | Stand |
|---|---|---|---|
| 1 | **Tausenderpunkte beim Vorlesen** — „800.000 ist 800.000, nicht 800.000 … bitte berücksichtigen und abspeichern" | **17.07., 16:20** | Gebaut (`bot.py`, `test_vorlese_b5.py`), **null Treffer** in Drehbuch und CLAUDE.md unter jedem geprüften Wort |
| 2 | **Ordnerspiegelung** — „zusätzlich zu einer Ordnerstruktur, die das Ganze nachhaltbar macht" | **22.07., 14:39** | Kein Punkt; lief unter fremder Nummer (deckt sich mit Micks Fund) |
| 3 | **Non-Apple-Kalenderanbindung** | **24.07., 12:18** | **7.3 verspricht wörtlich: *„Non-Apple-Nutzer (Produkt) = späterer eigener Punkt"*. Diesen Punkt gibt es nicht.** |
| 4 | **ChatGPT/Codex als Marktfähigkeits-Frage** — „bitte auch nachhalten und merken, dass wir das noch tun werden … kann ein kritischer Punkt sein" | **24.07., 15:22** | **Null Treffer** in beiden Dokumenten |
| 5 | **Hardware-Mitlieferung, Ausbaustufen, Paketpreis** als Produktbestandteil | **25.07., 20:54** | Kein Ort — gehört in **9.18 Weitergabe** |
| 6 | **Thumbnail-Leiste als billiger Weg zur Video-Sichtung** — „schau bitte gerne mal nach oder lass recherchieren" | **25.07., 23:04** | Null Treffer. 5.12 nennt „adaptives Sampling" als offen — die konkrete Idee steht nirgends |

### B · Zurückgestellt, ohne dass jemand sagte, woran „später" erkennbar ist

| # | Was | Stand |
|---|---|---|
| 7 | **Kontingent-Fallback Ebene 2** (anderes Modell / Zusatzguthaben / Pause zur Auswahl) | In 5.31 ausdrücklich *„bewusst NICHT gebaut"*, Möglichkeitsraum dokumentiert, Papier liegt vor — **die Entscheidung steht seit dem 25.07. bereit und wurde nie getroffen** |
| 8 | **Heimtunnel / Raspberry für YouTube** | Connis Fund 8, **an der Quelle bestätigt**: Adam am 25.07., 19:19: *„Das ist nicht verhandelbar, dass YouTube-Videos nicht ausgelesen werden können."* Beschluss steht in `MIGRATION.md:1345` — als Text, nicht als Wecker |

---

## Zwei Bemerkungen zur Methode

**Ein Rasterloch bei mir, gefangen durch Kontrollzählung:** Mein erstes Muster
fand nur **526 der 687** Nachrichten — die frühen Protokolle tragen keine
Datumsangabe im Kopf. Ohne die Gegenzählung wären 23 % des Materials
stillschweigend weggefallen.

**Und ein Fehlbefund, den ich zurücknehmen musste:** Ich meldete
„Transkriptions-Umschalter fehlt". Falsch — **5.26 existiert.** Ich hatte mit
**Adams** Worten gesucht, das Drehbuch führt es unter **seinem** Begriff. Seither
prüfe ich jeden Kandidaten gegen die vollständige Liste der 124 Überschriften,
nicht mehr über Stichwortsuche allein. Das hätte am Anfang stehen müssen.

---

## Wie es weitergeht

**Zwölf Blöcke offen — 26.07. bis 31.08.** Darin liegen die dichten Tage
(26.07. mit 69 Nachrichten, 27.08. mit 47) und die gesamte Zeit nach Adams
Rückkehr, die weder Conni noch ich bisher systematisch geprüft haben.

**Erwartung, ausdrücklich als solche:** Die Trefferdichte dürfte **steigen**.
Der Juli lief über den Block-Weg mit Kontrolle; im August lief mehr direkt
zwischen Adam und den Sitzungen — und genau dort sind heute Nacht schon drei
Lücken aufgetaucht.
