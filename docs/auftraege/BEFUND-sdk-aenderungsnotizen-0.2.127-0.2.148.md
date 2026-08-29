<!-- ROLLE: befund-sdk-sprung -->
# Befund: SDK-Änderungsnotizen 0.2.127 → 0.2.148, gegen den eigenen Code gemessen

**Stichtag:** 29.08.2026, 03:0x · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Mick · **Anlass:** Nachtpaket ② — *„die SDK-Änderungsnotizen werden VOR
dem Bash-Bau gelesen … Was davon erledigt der Sprung, was bleibt bei uns?"*

## Zwei Zahlen vorweg

**Der Auftrag nennt 0.2.144 als Ziel; verfügbar ist bereits 0.2.148.** Die vier
Fassungen dazwischen sind ausschließlich CLI-Nachzüge (2.1.246 → 2.1.251), ohne
eigene SDK-Änderung. **Vorschlag: auf 0.2.148 springen**, nicht auf 0.2.144 —
derselbe Aufwand, vier Fassungen weniger Rückstand. Entscheidung liegt bei Adam
bzw. der Kontrolle; bis dahin baue ich gegen 0.2.148 und rolle zurück, falls
widersprochen wird.

## Was der Sprung für uns erledigt: NICHTS von unseren Baustellen

Keine der siebzehn Fassungen berührt Werkzeug-Freigabelisten, Positivlisten
oder die Zerlegung von Bash-Zeilen. **Die Bash-Positivliste (①) muss vollständig
bei uns gebaut werden** — der Sprung nimmt uns davon nichts ab.

## Drei Berührungspunkte, alle gemessen — und alle folgenlos

| Notiz | Berührt uns? | Messung |
|---|---|---|
| **0.2.129 (Breaking)** — Skill-Namen in `ClaudeAgentOptions.skills` werden validiert, `skills=["*"]` wirft jetzt | **Nein** | `grep -n "skills" *.py` → **kein Treffer**. Wir setzen die Option nicht. |
| **0.2.137** — `ConversationResetMessage` weitet die `Message`-Union; erschöpfendes Matching mit `assert_never` bricht | **Nein** | `grep -n "assert_never" *.py` → **kein Treffer**. Unser Stromleser matcht offen, nicht erschöpfend. |
| **0.2.140** — `can_use_tool` jetzt auch für `query()` und String-Prompts | **Nein, reine Erweiterung** | Wir nutzen durchgehend `ClaudeSDKClient` (bot.py:3723, 4380, 9665, 11324) und `client.query(...)` als Methode — nie die Freifunktion. Der Riegel bleibt, wo er ist. |
| **0.2.140** — `mcp`-Abhängigkeit auf `>=1.23.0,<3.0.0` geweitet | **Nein** | Kein `mcp`-Pin in `requirements.txt`; wird transitiv gezogen. |

## Der EINE Punkt, der im Klon AUSGEFÜHRT geprüft werden muss

**0.2.140: `ResultError` mit strukturierter Fehlerlast.** Wörtlich: *„When the
CLI exits after a terminal error result, the SDK now raises `ResultError` … so
callers can branch on failure reason without string matching."*

**Wir branchen aber genau über String-Matching** — und zwar an der Stelle, an
der ein Fehlschlag am teuersten ist:

- `is_auth_error(exc)` → `authmarke.passt(str(exc))` (bot.py:857)
- `is_context_overflow(exc)` → Wortliste über `str(exc).lower()` (bot.py:870)
- `_is_buffer_error(exc)` → dito (bot.py:948)

**Die Gefahr, und sie sieht aus wie Ruhe:** Enthält `str(ResultError)` den
Anbieter-Fehlertext nicht mehr im Wortlaut, erkennt der Bot einen kippenden
Zugang **nicht** mehr. Dann greift nicht die Zugangs-Rücklage A1 (Nachricht
zurück an die erste Stelle der Warteschlange, Marke setzen, Adam bekommt die
Anleitung), sondern der allgemeine Ausnahmezweig. **Genau der Fall, für den die
ganze Abwesenheits-Vorsorge gebaut wurde, wäre still gebrochen** — und der
Anmelde-Wächter der Stundenblume, der auf dieselbe Marke horcht, bliebe stumm.

**Auflage für den Klon-Lauf, ausführend, nicht gelesen:**

1. Eine `ResultError` der neuen Fassung mit typischer 401-Last bauen und durch
   `is_auth_error` schicken. **Erwartung: `True`.** Kommt `False`, wird der
   Sprung nicht eingespielt, bis `is_auth_error` zusätzlich die strukturierten
   Felder (`api_error_status`, `subtype`, `errors`) liest.
2. Dasselbe für `is_context_overflow`.
3. `authmarke` prüft dieselbe Wortliste für beide Leser (G1) — bricht sie, ist
   auch der Wächter betroffen. Beide Seiten in einem Zug messen.

**Das ist der Ertrag dieser zwanzig Minuten:** ein Bruch, der im
Regressionslauf nicht rot geworden wäre, weil dort keine echte SDK-Ausnahme
entsteht.

## Was NICHT angefasst wird

Der weiche Import von `RateLimitEvent` (bot.py:62) bleibt weich. Er ist
ausdrücklich so gebaut, dass ein SDK ohne dieses Signal den Bot nicht am Start
hindert — nach dem Sprung ist er vorhanden, aber die Konstruktion trägt in
beide Richtungen und wird nicht „aufgeräumt".
