<!-- ROLLE: bauauftrag-log-wachposten -->
# Bauauftrag — Log-Wachposten (Stufe 2 „Mitwachen")

**Stichtag:** 2026-08-18 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile im Drehbuch**

**Für:** Mick · **Autorin:** Engywuck (erster Auftrag nach dem Stabwechsel) ·
**Adams Daumen:** erteilt 18.08. abends · **Einordnung:** nach E4/E3, es sei
denn Adam zieht es vor.

> **Herkunft dieser Datei:** aus dem Chat übernommen, 18.08. spät. Engywuck
> nennt eine Repo-Kopie maßgeblich — kommt eine über den Kurier, ist sie
> gegen diese abzugleichen und diese hier zu ersetzen.

## Zweck

Adam wünscht eine Kontrollinstanz, die **unaufgefordert** warnt. Vollautonomes
Modell-Wachen ist AGB-Grauzone — deshalb ein **deterministischer** Wachposten
auf dem VPS, der neue Log-Zeilen prüft und Auffälliges über das Boten-Postfach
meldet. Adams Fingertipp weckt dann Engywuck. **Kein Anthropic-Aufruf im Pfad,
Kosten null.**

## Bau

1. `scripts/wachposten.py` + Timer alle fünf Minuten, **`User=claudebot`**
   (Lehre B1 — nie ohne `User=`), **BOTENV-konform**. Liest
   `logs/conversations/<heute>.md` und `bot-errors.log` ab gemerktem Offset.
   **Unlesbarer Zustand = von vorn lesen und melden**, nie still stehenbleiben
   (Lehre Versions-Monitor).
2. **Stufe 2a (Pflicht):** Regelwerk deterministisch. Musterliste in **eigener
   Datei** (eine Quelle, Vorbild `authmarke.py`): rote Marker (`Traceback`,
   `❌`, „API Error", 5xx), Kosten-Wörter, Geheimnis-Marker, unbeantwortete
   Freigabe-Anfragen. **Beidseitig offene Grenzen + kurze Ausnahmeliste**
   (Stichwort-Filter-Regel, kein `\b`).
3. **Stufe 2b (optional, eigener Schalter, Vorgabe AUS):** Ollama via LiteLLM
   (F1-konform) als **Zweitmeinung** nur für Zeilen, die 2a anschlägt — **nie
   als Erstfilter.**
4. Meldung über das Boten-Postfach, **gedämpft per Kennung** (vorhandener
   Dämpfer + 6/h-Obergrenze gelten mit). **Wortlaut-Regel (Claudias Lehre):**
   Die Meldung **zitiert die beanstandete Zeile selbst** + Quelle + Zeit — nie
   nur eine vermutete Ursache. Schlusszeile: „Engywuck wecken?"
5. **Ausnahmen im Skript werden Befund, nie Abbruch** (Lehre der 21
   Prüfskripte); ein Abbruch sichert per Trap, wie weit der Lauf kam.
6. **Prüfer — ausführend, nicht lesend.** Künstliche Log-Zeilen durch die
   **echte** Prüfkette (Attrappe nur am Postfach-Rand): rote Testzeile →
   Meldung **mit Zeilen-Wortlaut** · harmlose Zeilen → Stille (Gegenprobe) ·
   entkernter Aufruf → fällt auf. Aufnahme in `test_zielumgebung.sh`
   (Start mit `env -i`).
7. ⚠️ **Geschwister-Prüfung:** Die Zeitgeber-Wache muss den neuen Timer
   erfassen — ihr ExecStart-Pfadfilter ist laut Gegenprüfung (Befund F) eine
   **Ein-Eintrag-Positivliste**. Im selben Zug erweitern, **sonst wacht
   niemand über den Wachposten.**

## Fertig-Definition

Einzeln committet · Register-Eintrag in `ABHAENGIGKEITEN.md` · Blaupause-Zeile ·
Doku-Spiegel (was gemeldet wird **und was nicht** — die Ausschluss-Sichtbarkeit
ist Claudias dritter Befund) · Abnahme durch Engywuck am Code, **danach
Widerlegungs-Gegenprüfung VOR dem Scharfstellen** (Regel ①a:
gebaut-und-wachend wartet nicht).

**Modell/Modus:** Opus, mittlere Tiefe; Mechanik (Musterliste, Timer-Dateien)
gern an eine Sonnet-Untersitzung.

## Ein Punkt, den ich vor dem Bau vorlegen werde `[Mick, 18.08. spät]`

Der Wachposten liest **Adams Gespräche** und die Meldung **zitiert die
beanstandete Zeile wörtlich** — über Telegram, das nicht Ende-zu-Ende
verschlüsselt ist. Enthält eine auffällige Zeile ein rotes Datum (Klientenname,
Finanzdetail), trüge die Meldung es genau dorthin, wo es laut Gatekeeper-Regel
nicht hingehört.

Das ist kein Einwand gegen den Auftrag, sondern eine offene Stelle in Punkt 4:
Die Wortlaut-Regel (zitieren statt vermuten) und die Gatekeeper-Regel (rote
Inhalte nicht über unsichere Kanäle) ziehen hier in verschiedene Richtungen,
und **beide haben recht**. Vorschlag zur Klärung mit Engywuck vor dem Bau: die
Zeile zitieren, aber vorher durch die vorhandene Ampel schicken — bei Rot nur
Quelle, Zeit und Kennung melden, mit dem Hinweis, dass der Wortlaut bewusst
zurückgehalten wurde. Sichtbar zurückgehalten ist ehrlich; lautlos wäre es die
nächste Stille.
