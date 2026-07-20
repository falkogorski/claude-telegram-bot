# CLAUDE.md — Projekt-Notizen

## 🗺️ MIGRATION — Status & Drehbuch

- **Das verbindliche Drehbuch ist `MIGRATION.md` (MASTER, zusammengeführt
  2026-07-12):** die 11-Phasen-Struktur aus der Telegram-Sitzung (Netcup-VPS,
  Status/Akzeptanz/Test/Adam-Bestätigung pro Punkt, sequenziell) + Phase 0
  (Code-/Repo-Vorbereitung), Anhang D (Ausführungsbefehle) und
  Kostenregel-Wächter aus dieser Sitzung. Die Repo-Version ist die Hoheits-
  Fassung; die Telegram-Sitzung übernimmt sie als Arbeitsdokument (Punkt 0.8).
- **Entscheidungen E1–E4 und F1 bestätigt** (Kasten in MIGRATION.md). F1:
  LiteLLM nur für Neben-Inferenzen (Ollama/Groq); der Claude-Agent bleibt
  direkt am Abo-SDK — keine Anthropic-Route in LiteLLM (Kostenregel!).
  Server-Zugangsdaten werden in Punkt 1.0 übermittelt/verifiziert.
- Wichtigste Stolperfallen: echte bot.py (~2000+ Zeilen) noch NICHT im Repo
  (Punkt 0.1, KRITISCH — Repo-Version ist veraltet); iCloud-Log-Pfad existiert
  auf Linux nicht (0.5); nie zwei Bot-Instanzen parallel; Webhook-Setzen (1.9)
  IST der Umschaltmoment; Auth NUR per Abo-Token (Kostenregel unten).
- Erledigt vorab: 401-Handling-Referenz + Abo-Token-first-Doku auf Branch
  `claude/telegram-bot-auth-401-g6yqrr`.

## 💰💰💰 KOSTEN-REGEL — HÖCHSTE PRIORITÄT 💰💰💰

**Die Warnpflicht gilt UNIVERSELL — für JEDE Art möglicher Extra-Kosten, egal
aus welcher Quelle** (Adam-Anweisung 2026-07-15):
- **API-/Token-Verbrauch** (Anthropic-API pay-per-token; `ANTHROPIC_API_KEY` statt Abo)
- **Werkzeug-Gebühren** (z. B. WebSearch ~$10/1000 Suchen)
- **Drittanbieter-Dienste** (Groq, Azure, Such-/Cloud-Dienste, …)
- **Abos / Grundgebühren**
- **Server-/Infrastruktur-Kosten**
- **Speicher- / Traffic-Kosten**
- **auch scheinbare Kleinstbeträge — Cent-Beträge zählen!**

**Vor JEDER Aktion, Tool-Einbindung oder Dienst-Einrichtung aktiv prüfen:**
> „Kann hierdurch irgendwo Geld abgebucht werden — jetzt oder später, einmalig
> oder laufend?"

**Falls ja ODER unklar → STOPP:** Kostenquelle + geschätzte Höhe nennen, Adams
**ausdrückliche Freigabe abwarten. „Unklar" gilt als „ja".**

Diese Prüfpflicht gilt für **alle Instanzen** und ausdrücklich **auch für die
Recherche-Tools der Sitzungen selbst** (z. B. WebSearch). **Neue Dienste/Tools
zuerst auf versteckte Zusatzgebühren prüfen** (wie bei Groq geschehen) —
**Abo/kostenfrei ist der Standard.**

### Hintergrund (Spezialfall Anthropic: zwei getrennte Geldtöpfe)
- **Max-Abo** (~100 €/Monat): Auth via OAuth / `claude login` /
  `CLAUDE_CODE_OAUTH_TOKEN`. Im Abo enthalten, **keine** Extra-Kosten.
- **API-Schlüssel** (`ANTHROPIC_API_KEY`): bucht **IMMER extra** ab,
  völlig getrennt vom Abo. Hat Vorrang vor OAuth, wenn gesetzt.
- **Standard-Auth für diesen Bot: Abo-Token (`CLAUDE_CODE_OAUTH_TOKEN`),
  NICHT `ANTHROPIC_API_KEY`.** Alles möglichst über das **Abo (kostenfrei)**,
  solange es nicht „professionell/produktiv" wird.

## 🔗 BEZUGS-INTEGRITÄT — Abhängigkeits-Register (Adam-Anweisung 2026-07-16)

Schutz gegen stille Abhängigkeits-Brüche (das „Excel-`#BEZUG!`-Problem"): Eine
Komponente wird geändert/entfernt, und woanders bricht unbemerkt etwas, das
davon abhing. **Register: `ABHAENGIGKEITEN.md` im Repo** (Komponente → wird
benötigt von → Prüfbefehl).

1. **VOR jeder Änderung oder Entfernung einer Komponente** zuerst das Register
   prüfen: Wer hängt davon ab?
2. **DANACH die abhängigen Komponenten mittesten** (Prüfbefehl aus dem Register)
   — nicht nur das Geänderte selbst.
3. **Beim Bau neuer Features deren Bezüge SOFORT ins Register eintragen** —
   nicht auf später verschieben.

Verkabelt mit **8.1** (täglicher 4-Uhr-Check arbeitet die Prüfbefehle ab, meldet
Brüche per Telegram) und **8.2** (Regressionstest nutzt das Register als
Prüfliste nach Änderungen).

## 🧭 Zuständigkeiten der Instanzen — ANTI-PING-PONG-REGEL

Der Nutzer arbeitet parallel mit mehreren Claude-Instanzen. Es ist passiert,
dass Instanzen ihn gegenseitig aneinander verwiesen haben („frag den Bot" ↔
„das gehört in die Desktop-Session"). Das darf nicht wieder vorkommen.

**Zuständigkeiten:**
- **Code-Sitzung am Mac** (Claude Code im Repo-Ordner): führt die Migration
  aus — Code, Git, Server-Arbeit, Status-Pflege in MIGRATION.md.
- **Telegram-Bot:** Alltagsaufgaben, Unterwegs-Nutzung, Permission-Freigaben.
- **Web-/Planungs-Sitzungen:** Drehbuch/Doku-Pflege im Repo; haben KEINEN
  Zugriff auf Mac oder andere Chats.

**Regel für JEDE Instanz:** Liegt ein Anliegen außerhalb der eigenen Rolle,
den Nutzer NIEMALS bloß weiterverweisen. Stattdessen: (1) selbst erledigen,
was mit eigenen Mitteln geht (Repo-Dateien lesen geht fast immer — MIGRATION.md
und CLAUDE.md im Repo sind die gemeinsame Wahrheit), (2) sonst dem Nutzer eine
FERTIGE Lösung mitgeben (exakte Befehle zum Selbst-Ausführen oder einen
fertigen Nachrichtentext inkl. Empfänger-Instanz) — nie nur „frag woanders".

**Frisch lesen vor Reden/Schreiben:** Vor jeder Aussage über oder jedem
Schreibzugriff auf geteilte Projekt-Dateien zuerst den frischen Stand aus
Repo/Dateien lesen — nie aus altem Sitzungsgedächtnis schreiben.

### 📌 Führungs-Register (pro Vorgang genau EINE führende Sitzung)

- **Vorgang „VPS-Migration" (aktuell): die Migrations-/Code-Sitzung am Mac
  führt.** Nur sie schreibt MIGRATION.md, CLAUDE.md und Code / pusht.
- **Alle anderen Sitzungen: NUR LESEN.** Änderungswünsche als Text an Adam
  bzw. an die führende Sitzung übergeben (fertiger Vorschlag, kein Direkt-Edit).
- **Führungswechsel nur ausdrücklich:** Dieser Registereintrag wird geändert
  und committet — erst danach schreibt die neue führende Sitzung.
- Durchsetzung: SessionStart-/PreToolUse-Hooks in `.claude/settings.json`
  (Warnbanner, Schreibschutz bei veraltetem Stand).

**Datenschutz-Hinweis Ampel-Regelpflege:** Heikelste Muster (z. B. Klienten-
Namen) NUR über den cloud-freien Weg eintragen — Telegram-Button-Dialog unter
`/ampel` oder Textbefehl `/ampel rot …` (beides wird deterministisch in bot.py
verarbeitet, ohne Claude-Beteiligung). Natürlichsprachige Pflege („nimm X als
Klient auf") ist erlaubt, läuft aber durch den Claude-Agenten (Cloud) — für
weniger heikle Begriffe okay, für das Heikelste den Button-Weg nutzen.

## Zusammenarbeit / Workflow (macOS, nicht-technischer Nutzer)

- **`pbpaste`-Befehle (Token/Key aus Zwischenablage):** Reihenfolge IMMER klar
  mitansagen → (1) Befehl ins Terminal einfügen **ohne** Enter, (2) **dann** den
  Token/Key kopieren (Doppelklick → `Cmd-C`), (3) **dann** Enter. Sonst
  überschreibt der eingefügte Befehl den Token in der Zwischenablage.
- **Ein Schritt pro Nachricht**, klar nummeriert. Kein `nano`/Hand-Editieren von
  Konfigdateien (zu fehleranfällig) — lieber per Befehl (`PlistBuddy` etc.).
- **Secrets nie in den Chat posten lassen** — vorher klipp und klar sagen.
- **Shell ist `zsh`:** KEINE `#`-Kommentarzeilen in Befehlsblöcken — zsh führt
  `#` interaktiv als Befehl aus („command not found: #"). Nur reine Befehle
  geben, Erklärungen außerhalb des Code-Blocks.

## Remote-/Mobil-Weiterführung von Sitzungen (WICHTIG)

- Nutzer startet oft Prozesse, die Berechtigungen/Bestätigungen brauchen, muss
  dann weg → Prozesse stocken. Ziel: Sitzungen/Prozesse **von unterwegs
  fortsetzen** und **Freigaben erteilen** können.
- **Bereits möglich:** (a) Aufgaben, die **über den Telegram-Bot** laufen,
  schicken Permission-Prompts als Inline-Buttons (Allow/Deny/Always allow) aufs
  Handy — „Always allow <Tool>" verhindert wiederholtes Nachfragen. (b)
  Claude-Code-**Web**-Sitzungen lassen sich über die **Claude-App** (iPhone)
  fortsetzen — auch diese hier.
- **Wunsch (größere Sache, ggf. Migration):** Permission-Freigaben **beliebiger**
  Sitzungen gebündelt in den Telegram-Bot leiten, mit Sitzungs-Kennung, sodass
  alles per Telegram-Button freigegeben werden kann.

## Bot-Verhalten (bei Migration in `bot.py` einbauen)

- Der Telegram-Bot darf **nicht annehmen, in welchem Kontext der Nutzer gerade
  sitzt** (z. B. „schön, dich am Desktop zu sehen"). Der Nutzer ist parallel an
  mehreren Geräten/Sitzungen; eine solche Annahme ist irreführend. Begrüßungen
  und Antworten **neutral** halten. Umsetzung: kurzer Zusatz im System-Prompt
  des Bots (`bot.py`, `ClaudeAgentOptions`), z. B. „Du bist ein Telegram-Bot;
  nimm nicht an, wo oder an welchem Gerät der Nutzer sitzt."

## 🪞 DOKU-SPIEGEL — nutzerseitige Texte im SELBEN Commit (Adam 2026-07-19)

**Jede Feature-Änderung aktualisiert ihre nutzerseitigen Texte im selben
Commit** — `/hilfe`, `/start`, Startnachricht, Button-Beschriftungen,
`setMyCommands`. Kein „mach ich gleich noch".

**Warum:** Am 17.07. wurde die Tastatur von 12 auf 9 Buttons verschlankt, der
`/hilfe`-Text blieb stehen — der Bot beschrieb Adam ein Layout, das es nicht
mehr gab (gefunden erst am 19.07. bei einer Video-Analyse; es waren am Ende
gleich drei Abweichungen plus zwei fehlende Befehle). Diese Drift ist tückisch,
weil sie **nichts kaputt macht** und deshalb in keinem Test auffällt — sie
untergräbt still das Vertrauen in jede Auskunft des Bots.

**Gilt auch für Status-Quellen:** Was der Bot beim Start als „noch offen"
meldet, kommt aus `~/.claude/memory/pending-items.md` **auf dem VPS** — auch das
ist ein nutzerseitiger Text. Erledigtes dort abhaken, sonst begrüßt der Bot mit
einem veralteten Projektstand (genau so mit 4.1/8.5 passiert). Automatische
Absicherung folgt mit Punkt **8.6** (Prüfskript `check_hilfe_buttons.py`).

## 🧬 BLAUPAUSE-SAMMELPFLICHT — Teil der „fertig"-Definition (Adam 2026-07-19)

Entsteht bei einem Punkt ein Mechanismus oder eine Regel, die erkennbar
**übertragbar** ODER erkennbar **plattformgebunden** ist, kommt **sofort** eine
Zeile nach `blaupause-notizen.md` — Format `Was · Punkt-Nr. · Einschätzung`
(universell / anpassbar / plattformgebunden). Keine Ausarbeitung, nur die
Inventur-Zeile; ausgearbeitet wird erst mit Punkt **9.6** nach dem Gesamtaudit.

Das ist **fester Teil der „fertig"-Definition jedes Punkts** — analog zum
Abhängigkeits-Register. Nachträgliches Sammeln funktioniert nicht: Die
Einschätzung „warum haben wir es so und nicht anders gebaut" ist genau dann
präsent, wenn die Entscheidung fällt, und danach nie wieder.

## 📊 STATUSÜBERSICHT — festes Format (Adam 2026-07-19)

Statusberichte an Adam folgen dem Format **„Migrations-Inhaltsverzeichnis"**:

- Tabelle(n) mit **einer Zeile pro Punkt**, jeweils in **Kurzsatz-Form**
  (kein Stichwort-Telegramm, kein Absatz).
- Symbole: **✅** fertig · **🔄** läuft/teilweise · **⬜** offen ·
  **⏭️** bewusst zurückgestellt.
- Je Phase ein **Fertigstellungsgrad in Prozent nach Arbeitsumfang**,
  nicht nach Punktzahl (zehn Kleinigkeiten sind nicht mehr als eine Migration).
- Ein **gewichteter Gesamt-Prozentwert**.
- Am Schluss die **Liste offener Entscheidungen und Wartepunkte**.

Gilt für spätere Migrations-Stände **und künftige Prozesse gleichermaßen**.

## 🔒 GOVERNANCE — der Bot editiert sein eigenes Repo NIE (Adam 2026-07-19)

Die Regel „Bot editiert das Bot-Repo nicht" gilt **ausdrücklich auch für die
VPS-Kopie `/home/claudebot/claude-telegram-bot`**: **lesen ja — editieren,
committen oder pushen niemals.** Deploys laufen **ausschließlich** über
`git pull`, ausgelöst von Adam.

**Warum:** Ein Selbst-Edit auf dem VPS lässt Repo-Stand und laufenden Code
auseinanderlaufen; der nächste `git pull` kollidiert dann oder überschreibt
stillschweigend Handarbeit. Details + technische Verankerung: Punkt **8.7**.

## 🧠 Kontext-Kompass bei dieser (langen) Migration — FESTER RHYTHMUS

Vereinbarung mit Adam (2026-07-16): Diese zusammenhängende Migration in **einer**
Sitzung weiterführen, **nicht** in Zweit-Sitzungen aufspalten (`/clear` = Neustart
bei null, `/resume` lädt den ganzen Verlauf zurück — kein Zwischenweg). Der
Kontext-Rhythmus ist ab jetzt fest:

1. **VOR jeder neuen Phase** (oder sobald der Kontext knapp wird): gesteuert
   verdichten mit `/compact focus on <die offenen, jüngsten Punkte>` — **nicht**
   aufs automatische Verdichten warten. So bleibt der Fokus auf dem noch
   Unabgeschlossenen scharf; das Erledigte wird eingedampft.
2. **NACH jeder Phase und VOR jedem Verdichten:** den Stand in `MIGRATION.md`
   zurückschreiben. Das ist das verdichtungssichere Langzeitgedächtnis —
   `CLAUDE.md`, `MIGRATION.md` und `MEMORY.md` werden bei jeder Verdichtung ohnehin
   frisch neu eingespielt, die Gesprächs-Historie dagegen komprimiert.
3. **Große Lese-/Rechercheaufgaben** (Logs, Configs, Audits) an **Subagenten**
   delegieren — sie lesen in eigenem Kontext und liefern nur die Zusammenfassung
   zurück, der Hauptkontext bleibt schlank.

Hinweis zur Ehrlichkeit: Ein echter Auto-Trigger, der `/compact` von selbst mit
sinnvollem Fokus auslöst, ist technisch nicht machbar (braucht inhaltliches
Urteil). Diese Regel steht bewusst **hier** in `CLAUDE.md`, weil sie so bei jedem
Sitzungsstart und nach jeder Verdichtung neu präsent ist. Details:
Memory `strategy-context-management-large-sessions`.
