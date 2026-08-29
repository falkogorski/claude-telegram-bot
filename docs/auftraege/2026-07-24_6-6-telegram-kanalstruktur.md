<!-- ROLLE: entscheidungsvorlage-kanalstruktur -->
# 6.6 Telegram-Struktur — FINAL v3 (Audit-Entscheid 24.07.2026)

**v3 ersetzt v2 vollständig** (Adam-Entscheid im Phasen-Audit 24.07.). Grundmodell
bleibt: **Gruppen als „Häuser", Themen-Topics als „Zimmer"** — keine Einzelkanäle
(Kanäle allenfalls später als reine Ausgabe-Feeds). Gegenüber v2 geändert:
die Häuser sind jetzt entlang **Lebens-/Geschäftsbereichen** benannt (projekt-
spezifische Poesie über einem universellen Muster), das Momo-Business bekommt ein
eigenes Haus, und „Offene Punkte" wird zur intelligenten Zwischenablage (6.1).

**Konfliktvermerk (nicht still aufgelöst):** v2 hatte drei Häuser
(Jakuna-San · Werkstatt · Archiv & Wissen). v3 ist eine **bewusste Ersetzung**
durch Adam — vier neue Häuser plus Bestand. Keine Zusammenführung, die alte
Fassung ist überholt.

**Anlage-Teilung:** **Gruppen erstellt Adam** (Gruppe anlegen → Bot einladen →
Themen/Topics in den Gruppen-Einstellungen aktivieren). **Zimmer legt der Bot
selbst an** (Punkt 6.5): Sobald Adam eine der vier Gruppen anlegt und den Bot
einlädt, erkennt der Bot am Gruppennamen das Haus und legt die zugehörigen
Zimmer in Minuten an. **Angelegt wird nichts ohne Adams Gruppe** — der Bot wird
nie von sich aus Gruppen erstellen.

Klammerwerte = 4.3-Ordner-Spiegelung mit **identischen Namen** („Struktur über
Namen": Häuser/Zimmer = Ordner/Unterordner).

---

## Haus 0 — 🏠 „Jakuna-San" (BESTAND — nur registrieren)

Persönliche Gruppe, der Bot ist bereits Mitglied. Wird nur **erfasst**, nicht
umgebaut, kein Auto-Routing ohne gesonderten Entscheid. Dialog-Ort neben der
Kommandobrücke. Anwendungsfall Nr. 1 des „Instanzen-Postfachs" (6.1): Gedanken
direkt hierher pinnen.

## Haus 1 — 🔧 „Werkstatt" (`werkstatt/`) — 4 Zimmer

Alles, woran aktiv gebaut wird:
- **Migration & Technik** (`werkstatt/migration-technik/`) — Statusberichte,
  Weitergabe-Blöcke, Deploy-/Testprotokolle. **Auto-Routing-Ziel für Bot-Status.**
- **Fanpost** (`werkstatt/fanpost/`) — **Startplatz** des Fanpost-Projekts;
  zieht ins Handelshaus um, sobald es klar ein Geschäft wird.
- **Rechnungen & Büro** (`werkstatt/rechnungen-buero/`) — 5.19-Ausgaben,
  Papierkram.
- **Offene Punkte** (`werkstatt/offene-punkte/`) — **die intelligente
  Zwischenablage (6.1):** Unzugeordnetes landet hier und wandert später gezielt
  weiter. **Auto-Routing-Ziel für Unzugeordnetes.**

## Haus 2 — 🕰️ „Nirgendhaus" (`nirgendhaus/`) — 4 Zimmer

Das Momo-Projekt-Haus (Name aus Meister Horas *Nirgend-Haus* in „Momo"):
- **Produkt & Blaupause** (`nirgendhaus/produkt-blaupause/`)
- **Kunden & Piloten** (`nirgendhaus/kunden-piloten/`)
- **Vertrieb & Empfehlung** (`nirgendhaus/vertrieb-empfehlung/`)
- **Recht & Zahlen** (`nirgendhaus/recht-zahlen/`)

## Haus 3 — 🏛️ „Handelshaus" (`handelshaus/`) — 2 Zimmer (klein eröffnet)

Weitere Geschäftsprojekte; **bewusst klein eröffnet, wächst durch Einzüge:**
- **Ideen & Chancen** (`handelshaus/ideen-chancen/`)
- **Affiliate-Projekt** (`handelshaus/affiliate-projekt/`)

## Haus 4 — 📚 „Bibliothek" (`bibliothek/`) — 3 Zimmer

Alles, was gefunden, bewahrt und nachgeschlagen wird (ersetzt v2 „Archiv & Wissen"):
- **Recherchen & Referenzen** (`bibliothek/recherchen-referenzen/`) —
  **Auto-Routing-Ziel für jede PDF-/Recherche-Lieferung des Bots.**
- **Link-Inbox** (`bibliothek/link-inbox/`) — Andockpunkt für 5.14.
- **Interessen** (`bibliothek/interessen/`) — inkl. Fußball/FC Köln, weitere
  Themen nach Bedarf.

---

## Routing-Regeln (6.1)

- **Bot-Status/Weitergabe** → Werkstatt · Migration & Technik (auto)
- **Recherche-/PDF-Lieferungen** → Bibliothek · Recherchen & Referenzen (auto)
- **Unzugeordnetes** → Werkstatt · Offene Punkte (auto, Zwischenablage)
- **Alles Übrige** → manuell / per Zuruf in das gewünschte Zimmer

## Bewusst NICHT dabei

Erinnerungen/Routinen (eigener Kanal in Phase 7) · rote Inhalte (laufen laut
Ampel nie durch Telegram) · ein „Sonstiges"-Müllschlucker (dafür ist „Offene
Punkte" die geordnete Zwischenablage).

## Notierte Ausbauwünsche

- **6.5-Ergänzung:** Vom Projekt-Topic direkt in die zugehörige Code-Sitzung
  springen; **vorerst: gepinnter Link je Topic.**
- Kanäle als reine Ausgabe-Feeds: erst, wenn ein Zimmer erkennbar zum
  Broadcast-Fall wird.

## Blaupause-Notiz

Die Haus-Namen (Jakuna-San / Werkstatt / Nirgendhaus / Handelshaus / Bibliothek)
sind **projektspezifische Poesie über einem universellen Muster**:
**Leben · Werkstatt · Produkt · Geschäfte · Bibliothek**. Die Blaupause
beschreibt das *Muster*; der Kunde benennt seine Häuser selbst.
