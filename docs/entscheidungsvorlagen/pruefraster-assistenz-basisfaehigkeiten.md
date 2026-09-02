<!-- ROLLE: pruefraster-basisfaehigkeiten -->
# Prüfraster: Basisfähigkeiten der Assistenz

> **Gültigkeits-Kopf** (Regel ⑪)
> **Stichtag:** 25.07.2026, 05:47 (geprüfte Zeit) · gegen den Code erhoben, nicht
> gegen Berichte (Regel ⑫)
> **Überholt durch:** —
> **Zuletzt nachgezogen:** 31.08.2026 (fünf Zeilen, gegen Code und Drehbuch)
> **Warum diese Zeile dazugehört:** Der Kopf war nach Regel ⑪ vollständig gebaut — und hat trotzdem nicht geschützt, weil er sagt, **ab wann etwas gilt, nicht ob es noch stimmt.** Ein *gültig ab* ohne *zuletzt geprüft* ist eine halbe Auskunft.
> **Maßgeblich** bleibt die Status-Zeile des jeweiligen Punkts in `MIGRATION.md`.

**Warum es dieses Raster gibt:** Anlass war die PDF-Lücke — eine
**Basis-Fähigkeit fehlte, und niemand merkte es**, weil niemand eine Liste
hatte, gegen die man prüfen konnte. Das Raster ist diese Liste. Es benennt
zuerst die Lücken; der tiefe quellenkritische Vergleich mit anderen Assistenzen
folgt danach, wenn klar ist, wonach zu suchen ist.

**Legende:** ✅ haben wir (im Code belegt) · 🕳️ **Lücke** · 🔄 geplant/teilweise

---

## MUSS — ohne das ist es keine Assistenz

| Fähigkeit | Stand | Beleg / Lücke |
|---|---|---|
| Text verstehen und beantworten | ✅ | Kernpfad `process_user_text` |
| Sprachnachricht verstehen | ✅ | `transcribe.py`, seit 25.07. faster-whisper |
| Antwort vorlesen | ✅ | TTS-Kette, Aufbereitung in `_strip_markdown_for_tts` |
| Bilder ansehen | ✅ | `on_photo` + `media.py` (H1) |
| Videos auswerten | ✅ | Einzelbilder + Übersichtsbögen + Tonspur (5.28) |
| Dokumente lesen (PDF, Text) | ✅ | `on_document`, PDF-Kette mit PyMuPDF |
| Nichts verlieren | ✅ | 5.2-Persistenz, Kontingent-Pause (5.31), Voice-Eingangsschutz |
| Im Netz nachsehen | ✅ | SearxNG lokal (2.7), kostenfrei |
| Gedächtnis über Sitzungen | ✅ | Memory-Ordner, `CLAUDE_MEMORY_DIR` |
| Eigene Fehler melden statt schweigen | ✅ | `_notify_job_failed`, `bot-errors.log`, Selbstcheck |
| **Dateien SENDEN können** | ✅ | Boten-Postfach, PDF-Paar-Regel |
| **Große Dateien empfangen** | 🔄 | `[K4, 28.07.]` **Bot-Seite gebaut** (5.34): Umschalter `TELEGRAM_API_BASE`, Aufräum-Pflege mit 30-GiB-Deckel, Deckel-Prüfung im 4-Uhr-Lauf. **Offen bleibt der Server-Teil** — er braucht Adams `api_id`/`api_hash` und root (Schritt 5 der Befehlsblöcke) |
| **Kalender lesen und schreiben** | 🔄 | `[K4, 28.07.]` **Gebaut** (7.5 — bis 31.08. 7.4, `kalender.py`, CalDAV): `/termine` und `/aufgaben` stehen, sechs Prüfungen. **Wartet auf ein Ding:** Adams anwendungsspezifisches Apple-Kennwort. Ohne es meldet das Modul `NichtEingerichtet`, statt still zu schweigen |
| **E-Mail lesen und senden** | 🔄 | `[K4, 28.07.]` **Gebaut** (9.5, `email_kanal.py`): 14 Prüfungen · Senden verlangt eine Freigabe · Kopffelder mit Steuerzeichen werden **abgewiesen statt gesäubert** · Posteingang nur-lesend · Absender nur aus einer Allowlist. **Wartet — und zwar zuerst auf etwas anderes als Kennwörter** `[BERICHTIGT 31.08.]`: Hier stand allein *die App-Kennwörter der beiden Konten*. **Davor steht Adams stehende Regel: kein Postfach, auch kein Wegwerf-Konto, solange die Erkennungsseite nicht trägt** — davor wiederum Rang 2 und 3 der Widerlegung und die Ultracode-Prüfstelle. Die alte Fassung ließ E-Mail wie ein Kennwort entfernt aussehen und lud damit ein, den letzten Schritt zu tun; **das ist die gefährliche Fehlerrichtung.** Die Kennwörter sind der letzte Handgriff, nicht der einzige |
| **Erinnern zur richtigen Zeit** | 🔄 | `[BERICHTIGT 31.08.]` **7.2**, nicht 7.3 — 7.3 ist die Kalenderquelle. **Gebaut und ruhend** seit 20.08.: `scripts/erinnerungen.py`, 220 Zeilen, neun Prüfungen. Hier stand *dokumentiert, nicht gebaut*. Es fehlen **drei** Dinge, alle aus Adams Hand: der Kanal (7.1), der Kalenderzugang (7.3) und der Zeitgeber-Block. Zeit-Trigger laufen ohne Modell-Aufruf (AGB) |

## SOLL — macht sie brauchbar statt nur funktionsfähig

| Fähigkeit | Stand | Beleg / Lücke |
|---|---|---|
| Aufgaben der Reihe nach abarbeiten | ✅ | FIFO-Warteschlange (5.5), Unterbrechungs-Erkennung |
| Ohne Klick-Nachfragen recherchieren | ✅ | Herkunfts-Schranke (5.25) |
| Reaktionen als Kurzsprache verstehen | ✅ | Vokabular v2.2, H3-Quittung |
| Sich selbst prüfen | ✅ | Selbstcheck und Regressionslauf nennen ihren Umfang selbst (Stand 26.07.: 28 Zeilen · 30 Prüfungen) — die Zahlen wachsen, deshalb hier kein fester Sollwert |
| Sich selbst aktualisieren | ✅ | Monitor (5.21) + Updater + Nachzieher (C1) |
| Nach Absturz sauber hochkommen | ✅ | Start-Wächter (B1), systemd `Restart=always` |
| Mehrere Themen getrennt halten | 🔄 | Kanal-Routing gebaut (Phase 6), **fünf Gruppen fehlen noch** `[BERICHTIGT 31.08.]` — vier Häuser plus der Erinnerungskanal (7.1), der **kein Zimmer** der 6.6-Struktur ist |
| **Sammelstelle für Links/Fundstücke** | ✅ | `[K4, 28.07.]` **Gebaut** (5.14, `linkinbox.py`): Eine Nachricht, die nur aus Adressen besteht, wird abgelegt statt verarbeitet — deterministisch, ohne Modell. **Kein Netzabruf vor Adams Knopfdruck**, und der Titel ist als *abgeleitet* gekennzeichnet, nicht als gelesen |
| **Bilder/Diagramme selbst erzeugen** | 🕳️ | Nichts vorhanden. Nicht dringend, aber bislang nie benannt |
| **Tabellen/Rechenblätter erzeugen** | 🔄 | Rechnungs-Werkzeuge existieren extern (5.19), im Bot nicht angebunden |
| **Mehrere Sitzungen gleichzeitig** | ⬜ | `[BERICHTIGT 31.08., eigener Fund]` Hier stand 🔄. **Im Drehbuch steht 5.1 auf OFFEN**, und das Akzeptanzkriterium verlangt *mehrere parallele Sitzungen je Nutzer, Wechsel, Persistenz über den Neustart* — davon existiert nichts. Die vorhandene `UserSession` führt **eine** Sitzung je Nutzer; das ist die Grundlage, kein Teil der Fähigkeit. **Der Kopf dieses Rasters sagt selbst, dass die Status-Zeile im Drehbuch maßgeblich ist** — ein 🔄 gegen ein OFFEN widerspricht der eigenen Hoheitsregel. Nach Phase 3 |
| Kosten sichtbar halten | 🔄 | `/usage` zeigt Verbrauch; die 80-%-Vorwarnung ist über das Abo **nicht sauber abfragbar** — ehrliche Grenze, keine Lücke |

## KÜR — hebt sie über den Durchschnitt

| Fähigkeit | Stand | Anmerkung |
|---|---|---|
| Zwei Wege für alles (Ausfallsicherheit) | 🔄 | Stufe 1 in Arbeit; lokales Modell steht (2.3) |
| Aus Vorlieben lernen statt zu fragen | 🔄 | Grundsatz steht in CLAUDE.md, mechanisch noch nicht verankert |
| Verfahren aktuell halten, nicht nur Versionen | ✅ | seit 25.07. in CLAUDE.md + Register `verfahren-medien` |
| Komplexität verbergen | 🔄 | Grundsatz steht; Entwicklungsmodus zeigt bewusst mehr |
| **Eigene Oberfläche statt Telegram-Pflicht** | 🕳️ | Fernziel (Momo), bewusst offen |
| **Stimme, die wie ein Mensch klingt** | 🔄 | Katja heute; SSML-Sprachwechsel mit der Migration vorgesehen |

---

## Die offene Lücke `[NACHGEZOGEN 2026-08-31]`

**Es ist noch eine, und das ist eine gute Nachricht.** Hier stand eine Liste
von sechs; **fünf davon waren zum Zeitpunkt des Nachziehens von den Tabellen
oben widerlegt** — Kalender (7.5), E-Mail (9.5), Erinnerungen (7.2), Große
Dateien (5.34) und Link-Sammelstelle (5.14) stehen dort längst als gebaut.

1. **Rechenblätter/Rechnungen im Bot** (5.19, im Drehbuch OFFEN) — die
   Werkzeuge existieren in `~/Projects/rechnungen`, sie sind nur nicht
   angebunden.

**Warum die Liste gestrichen und nicht berichtigt wurde:** Sie war eine
**zweite Quelle für dasselbe** — die Tabellen oben führen jeden Punkt bereits
mit Symbol und Stand. Am 28.07. wurden die Tabellen nachgezogen, die Fußliste
nicht, und danach behauptete dasselbe Dokument zwanzig Zeilen weiter unten das
Gegenteil von sich selbst. **Eine Liste, die eine andere spiegelt, driftet —
nicht vielleicht, sondern absehbar.** Die eine verbliebene Zeile steht hier,
weil sie eine Rangfolge trägt, die in keiner Tabellenspalte steht.

**Was dieses Raster bewusst NICHT tut:** Es vergleicht nicht mit anderen
Assistenzen. Das ist der nächste Schritt — und er ist jetzt beantwortbar, weil
die Suchfrage steht: nicht „was können andere?", sondern „schließt es eine
dieser sechs Lücken besser, als wir es planen?"

---

# TEIL 2 — ARBEITSVORGÄNGE `[NEU 2026-09-02]`

**Warum es diesen Teil gibt, und der Grund ist gemessen:** Teil 1 misst
**Basisfähigkeiten** — kann die Assistenz etwas prinzipiell. Er misst **nicht**,
ob Adam damit **arbeiten** kann. Der Unterschied ist am 02.09. aufgeschlagen:
Die Zeile *Tabellen/Rechenblätter erzeugen* stand auf 🔄, und trotzdem konnte
der Rechnungs-Vorgang beim Umzug still verschwinden — **kein Prüfer hat
angeschlagen, weil kein Prüfer den Vorgang kannte.**

Adam dazu, 11:51: *„im Moment ist es für mich ein deutlicher Rückschritt … da
haben wir vielleicht an der falschen Stelle zuerst gebaut."*

**Die Regel, die dieser Teil trägt** (`CLAUDE.md`, *Vor jeder neuen Schranke*):

> Vor jeder neuen Schranke: Welche Fähigkeit schützt sie, und läuft die heute?
> **Was schon einmal ging und heute nicht mehr geht, ist der dringendste
> Posten — dringender als jeder Neubau.**

**Die Spalte, auf die es ankommt, ist *lief zuletzt am*.** Ein ✅ ohne Datum ist
eine Behauptung; ein Datum, das älter wird, ist ein Befund. **Der Kurs-Blick
liest dieses Raster wöchentlich** — kein neuer Wächter nötig.

| Arbeitsvorgang | Stand | lief zuletzt am | woran es hängt |
|---|---|---|---|
| **Rechnung stellen** (Daten → PDF im Markenlayout) | 🔄 | **auf dem Mac zuletzt 13.07.2026**, auf dem Server **noch nie** | Umzug nach `~/workspace/rechnungen` + `typst` — Adams Hand, [`befehlsbloecke-adam.md`](../befehlsbloecke-adam.md). **Der Vergleichslauf ist der Nachweis**, nicht der Umzug |
| **Postenaufstellung erzeugen** (Excel + PDF) | 🔄 | wie oben, dieselbe Kette | dito — ein Generator, zwei Vorgänge |
| **Fertiges in die Ablage bringen** (→ iCloud) | 🔄 | Route A gebaut 02.09., **Hälfte 2 gemessen**, Gesamtkette noch nie | hängt an Vorgang 1. ⚠️ **Zielordner ist ein Übergabeordner** — das Einsortier-Schema aus 5.19 ist nicht gebaut, und geraten wird es nicht |
| **Rechnung versenden** | ⬜ | nie | 9.5, wartet auf Adams Postfach-Zugänge. Bewusst **kein** `/mail send` |

**Wie dieser Teil gepflegt wird — sonst wird er die nächste stille
Falsch-Wahrheit:** Das Datum wird **eingetragen, wenn der Vorgang tatsächlich
lief**, nicht wenn er gebaut wurde. *Gebaut* und *gelaufen* sind hier
verschiedene Dinge; genau ihre Verwechslung hat den Befund erzeugt.

**Was hier NICHT hineingehört:** Basisfähigkeiten (die stehen oben) und
Vorhaben ohne Vorgang. Ein Arbeitsvorgang ist etwas, das **Adam tut** und an
dessen Ende ein Ergebnis steht, das er verwenden kann.
