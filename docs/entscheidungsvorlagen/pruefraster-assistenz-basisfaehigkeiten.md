<!-- ROLLE: pruefraster-basisfaehigkeiten -->
# Prüfraster: Basisfähigkeiten der Assistenz

> **Gültigkeits-Kopf** (Regel ⑪)
> **Stichtag:** 25.07.2026, 05:47 (geprüfte Zeit) · gegen den Code erhoben, nicht
> gegen Berichte (Regel ⑫)
> **Überholt durch:** —
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
| **Große Dateien empfangen** | 🕳️ | 20-MB-Grenze von Telegram · Vorlage 5.34 liegt, Messung erledigt |
| **Kalender lesen und schreiben** | 🕳️ | Nichts vorhanden. AppleScript-Weg fällt auf Linux weg → iCloud/CalDAV, beim Bau verifizieren (5.19) |
| **E-Mail lesen und senden** | 🕳️ | Nichts vorhanden (9.5). „Schick raus" geht heute nicht |
| **Erinnern zur richtigen Zeit** | 🔄 | 7.3 dokumentiert, nicht gebaut. Zeit-Trigger müssen ohne Modell-Aufruf laufen (AGB) |

## SOLL — macht sie brauchbar statt nur funktionsfähig

| Fähigkeit | Stand | Beleg / Lücke |
|---|---|---|
| Aufgaben der Reihe nach abarbeiten | ✅ | FIFO-Warteschlange (5.5), Unterbrechungs-Erkennung |
| Ohne Klick-Nachfragen recherchieren | ✅ | Herkunfts-Schranke (5.25) |
| Reaktionen als Kurzsprache verstehen | ✅ | Vokabular v2.2, H3-Quittung |
| Sich selbst prüfen | ✅ | 23 Selbstcheck-Zeilen, Regressionslauf 20/20 |
| Sich selbst aktualisieren | ✅ | Monitor (5.21) + Updater + Nachzieher (C1) |
| Nach Absturz sauber hochkommen | ✅ | Start-Wächter (B1), systemd `Restart=always` |
| Mehrere Themen getrennt halten | 🔄 | Kanal-Routing gebaut (Phase 6), **vier Gruppen fehlen noch** |
| **Sammelstelle für Links/Fundstücke** | 🕳️ | 5.14 Link-Inbox, nicht gebaut |
| **Bilder/Diagramme selbst erzeugen** | 🕳️ | Nichts vorhanden. Nicht dringend, aber bislang nie benannt |
| **Tabellen/Rechenblätter erzeugen** | 🔄 | Rechnungs-Werkzeuge existieren extern (5.19), im Bot nicht angebunden |
| **Mehrere Sitzungen gleichzeitig** | 🔄 | 5.1, nach Phase 3 |
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

## Die sechs echten Lücken, nach Nutzen sortiert

1. **Kalender** — die häufigste Alltagsbitte überhaupt, und es gibt nichts.
2. **E-Mail** — „schick raus" ist Adams ausdrückliches Zielbild (9.5).
3. **Erinnerungen zur Zeit** — dokumentiert, ungebaut; Voraussetzung fürs
   Sekretärin-Bild.
4. **Große Dateien** — Vorlage liegt entscheidungsreif (5.34).
5. **Link-Sammelstelle** (5.14) — klein, hoher Alltagsnutzen.
6. **Rechenblätter/Rechnungen im Bot** — Werkzeuge existieren, nur nicht angebunden.

**Was dieses Raster bewusst NICHT tut:** Es vergleicht nicht mit anderen
Assistenzen. Das ist der nächste Schritt — und er ist jetzt beantwortbar, weil
die Suchfrage steht: nicht „was können andere?", sondern „schließt es eine
dieser sechs Lücken besser, als wir es planen?"
