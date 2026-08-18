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

## Die Rueckfrage ist beantwortet — Engywuck, 18.08. spaet (Lesestand a4257c5)

Wortlaut-Regel und Gatekeeper-Regel zogen gegeneinander; hier steht, wie es
aufgeloest wird. **Beide Entscheidungen sind verbindlich.**

### (1) Die Ampel ist der Filter — keine Zweitliste

`ampel.classify()` ist importierbar und abhaengigkeitsfrei (**nachgemessen
19.08.**: Import mit `env -i`, nur Standardbibliothek, kein Bot-Kontext
noetig). Eine eigene Musterliste fuer diesen Zweck waere eine zweite Wahrheit
ueber dieselbe Frage — G1-Lehre.

Drei Auflagen:

- **Nur ROT wird zurueckgehalten.** Gelb und Gruen gehen im Wortlaut hinaus.
- **Ein Einstufungs-Ausfall zaehlt als ROT.** Faellt die Ampel aus, wird
  zurueckgehalten, nicht durchgelassen — dieselbe Bauart wie beim Riegel: Wer
  im Zweifel oeffnet, sichert nichts.
- **Die Meldung nennt bei Rot nur das Kategorien-Label, NIE das Muster.**
  Konkret gemessen: `classify()` liefert `{color, rules, matches}` — `matches`
  enthaelt die **Treffer selbst**. Es wird ausschliesslich `rules` verwendet;
  `matches` darf die Meldung nie beruehren, sonst zitierte sie genau das rote
  Wort, das sie zurueckhaelt.

### (2) Bei Rot wird gemeldet — der Wortlaut sichtbar zurueckgehalten

Gemeldet wird **Quelle + Zeitstempel als Fundstelle**, dazu der ausdrueckliche
Hinweis, dass der Wortlaut zurueckgehalten wurde. Kein Sicherkanal in v1 —
aber als **[spaeter pruefen]** in die Auswertung, damit aus [fuer jetzt] nicht
stillschweigend [fuer immer] wird.

- **Der Pruefer misst BEIDE Richtungen:** geseedete rote Zeile → Meldung OHNE
  Wortlaut · auffaellige harmlose Zeile → Meldung MIT Wortlaut.
- **Nach dem Scharfstellen einmal die Wirkungs-Regel fahren:** eine echte rote
  Probe durchschicken und die **angekommene** Meldung ansehen. Nicht die
  Konfiguration lesen — nachmessen, was ankam.
- **Die Zurueckhaltung gilt fuer BEIDE Quellen**, auch `bot-errors.log`
  (Geschwister-Regel). Ein Fix an einem Pfad ist erst fertig, wenn die
  Schwesterpfade geprueft sind.

### Nachtrag zu meinem Hinweis „halber Kontrollweg" — er war falsch

Ich hatte geschrieben, es gebe keinen Weg von mir zu Engywuck und sein
Log-Repo-Zugriff sei offen. **Beides war tradiert, nicht gemessen** — aus
Connis Liste uebernommen. Engywuck hat es richtiggestellt und belegt: Er hat
diese Rueckfrage vierzehn Minuten nach meinem Push im frisch geholten Repo
gelesen, und Claudias Erstfracht am selben Abend aus dem Log-Repo.

Der Weg existiert also, und ich habe ihn benutzt, waehrend ich behauptete, es
gebe ihn nicht. Einseitig ist nur **seine** Ausgangsrichtung, und die laeuft
mit Absicht ueber Adam: **Vier-Augen-Prinzip, kein fehlender Bau.** Das
fehlende Viertel wollen wir nicht bauen.

