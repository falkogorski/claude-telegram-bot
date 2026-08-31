> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren.
> **Vier Ablage-Einträge (kein Code) + ein Bauvorschlag, der Adams Freigabe
> braucht** — der ist unten getrennt ausgewiesen.

# Auftrag an Mick — aus den Blöcken 14 und 15 (20.08.–27.08.)

**Stichtag:** 01.09.2026, 01:23 MESZ · **Von:** Engywuck (Kontrolle)
**Alle Zitate im Wortlaut aus den Bot-Protokollen.** Keine Ableitung.

**Vorab und wichtig:** In diesen Blöcken ist **viel richtig gebaut worden** —
Menü alphabetisch mit `/stopp` oben, die Fünf-pro-Stunde-Grenze auf 100 **mit
der Mengen-Regel richtig herum**, der Nachhol-Lauf nach dem Kontingent-Limit.
Was folgt, sind die Reste, nicht die Bilanz.

---

## N-12 · 🔴 Der wichtigste: Adams Ausweg beim Zahlen-Vorlesen ist nicht verlinkt

**Adam am 25.08., 12:32 (Wortlaut):** *„Wenn wir auf **Azure** wechseln, dann
hat sich das ganze Thema aufgelöst."*

**Gemessen:** **Punkt 9.1 (TTS-Upgrade Azure Neural mit SSML-Sprach-Switch)
enthält kein einziges Wort zum Zahlen-Problem.** Dabei ist genau das der Kern:
SSML kennt `<say-as interpret-as="date">`, `"cardinal"` und `"digits"` — die
Unterscheidung, an der die Wortliste in `bot.py:11269` scheitert, ist dort
**eingebaut**.

**Einzutragen bei 9.1**, drei Zeilen:
1. Der Zusammenhang: **Ein TTS-Wechsel mit SSML löst das Zahlen-Vorlesen an
   der Wurzel**, statt es in `_normalize_jahreszahlen` /
   `_normalize_tausenderpunkte` weiter nachzuschärfen.
2. Adams Zitat vom 25.08. mit Datum.
3. 💰 **Der Zusammenhang ändert die Kostenabwägung:** 9.1 ist ein bezahlter
   Dienst. Bisher stand dort nur „Klang"; jetzt steht auch „löst eine
   Fehlerklasse auf". **Keine Kostenentscheidung treffen** — nur den
   vollständigen Sachverhalt hinschreiben, damit Adam ihn hat.

**Und eine Rückverweis-Zeile am Filter** in `bot.py` (Kommentar, kein
Code-Eingriff): *dass ein geplanter TTS-Wechsel diese Stelle ganz entfallen
lassen könnte.* Sonst schärft die nächste Sitzung wieder die Wortliste nach.

**⚠️ Ausdrücklich NICHT:** die Wortliste umbauen, `damals` streichen, einen
neuen Filter bauen. **Das wäre genau der Fehler, den der Eintrag verhindern
soll.** Adams Anweisung vom 25.08. (*„das bitte rausstreichen und
intelligenter lösen"*) ist unerledigt — aber die richtige Erledigung ist
möglicherweise, sie **entfallen zu lassen**, und das entscheidet Adam.

## N-13 · Zwei Stimmen als Signal — Adams Idee vom 25.08.

**Wortlaut (25.08., 13:45):** *„Ich glaube, dass es gar nicht verkehrt ist,
wenn man dann zwei Varianten hat, **auch zwei unterschiedliche Sprecher**.
Damit wird sofort klar, wenn etwas über Rot läuft und wenn etwas grün ist."*

**Gemessen:** 9.2 heißt *„Piper/Kokoro lokal als Rot-Backend"* — die
**Trennung** ist verplant. **Dass die Stimme selbst das Signal ist, steht
nirgends.** Das ist der Kern: kein Hinweis zum Lesen, sondern ein Unterschied
zum **Hören**.

**Einzutragen bei 9.2** als Anforderungszeile, mit Adams Zitat.

## N-14 · Der Grundsatz, der N-12 verhindert hätte — nach `CLAUDE.md`

**Wortlaut (25.08., 12:32):** *„Zukünftig muss von dir **sofort als Erstes**
geprüft werden: **haben wir dazu sowieso schon was vor, was wir ändern wollen,
und ist das Problem dann vielleicht gar nicht mehr existent?**"*

Eingebettet in seine Grundsatzkritik desselben Tages: *„Es ist gerade
überhaupt nicht flexibel, was wir machen, sondern total eingefahren. Das ist
jetzt mal eine generelle Kritik und ich will, dass sich das ändert."*

**Gemessen:** `CLAUDE.md` trägt *„Fremdes nehmen, wo es nicht ans Herz geht"*
(25.07.) — das deckt *nimm Vorhandenes statt selbst zu bauen*. **Der Schritt
davor fehlt.**

**Einzutragen als kurzer Zusatz an dieser vorhandenen Regel** (kein neuer
Abschnitt — die Kurs-Regel verbietet Wildwuchs):

> **Vor dem Lösen: Löst es sich von selbst?** Bevor an einer Stelle
> nachgebessert wird, prüfen, ob ein **ohnehin geplanter** Schritt das Problem
> entfallen lässt. **Musterfall:** Das Zahlen-Vorlesen wurde in einer
> Wortliste nachgeschärft, während Punkt 9.1 (TTS mit SSML) die Unterscheidung
> mitbringt. Adam am 25.08.

**Bemerkenswert und bitte mit aufnehmen:** Claudia wendet den Grundsatz seit
dem 31.08. an — ihr Update-Monitor-Papier führt *„Notwendigkeit: Braucht es
den Umbau überhaupt, oder erledigt ihn ein ohnehin geplanter Schritt?"* als
eigenes Prüfkriterium. **Sie hat ihn übernommen, ohne dass er irgendwo
stand.**

## N-15 · Die Sichtungspflicht ist enger gebaut als beauftragt

**Adam am 20.08., 10:42 (Wortlaut, gekürzt):** *„Engywuck braucht auf jeden
Fall eine Instanz **pro Tag**, in der die **[Logs]** durchgegangen und
gecheckt werden, ob dadurch ein Auftrag entsteht. Und der muss auch passieren,
**bevor Mick das macht**. … Es muss auch **unabhängig von mir** gecheckt
werden."*

**Gemessen:** `docs/pflichten-kontrollrolle.md`, Zeile 63 — *„…`an-mick/` wird
täglich gesichtet."* **Das ist der Ablage-Ordner, nicht die
Gesprächsprotokolle.**

**Einzutragen dort:** die Sichtung umfasst **auch die Tagesprotokolle**
(`logsync/claude-bot-logs/conversations/`), mit der Frage *entsteht daraus ein
Auftrag?*, und sie läuft **vor** der Bau-Sitzung.

**Der Beleg, warum das zählt, gehört in dieselbe Zeile:** Die einmalige
Gesamtprüfung vom 31.08. hat über **dreißig** Lücken gefunden — Vorhaben,
Regeln und Anweisungen, die in den Protokollen standen und nirgends sonst.
**Das ist die Rechnung dafür, dass die Sichtung nicht täglich lief.**

---

# 🔨 Bauvorschlag — braucht Adams Freigabe, deshalb hier getrennt

## Die Kontingent-Warnung kommt zu spät

**Adam am 20.08., 09:51 (Wortlaut):** *„Warnung zu spät!! Müsste schon bei
**80 %**, dann nochmal bei **85, 90 und 95 %** erfolgen!"*

**Gemessen:** Keine Warnstufen in `kontingent.py` oder `bot.py`. Es gibt
`/kontingent` **auf Abruf**, aber nichts, das von selbst meldet.

**Warum es heute billig ist:** A2 hat am 20.08. gemessen, dass der
Auslastungswert **in den Kopfzeilen jeder Antwort mitkommt** — er wird
ohnehin schon in den Merker geschrieben. Es fehlt nur die Schwelle, die auf
ihn schaut.

- **Kein neuer Abruf, kein Modelllauf, keine Kostenquelle.**
- **Kein Wächter im Sinne der Konvergenz-Bremse** — eine Anzeige an
  vorhandenen Daten, kein neuer Prüfer.
- Je Fenster **einmal** je Stufe melden (sonst flutet es bei 95 %).

**⚠️ Aber nicht ohne Adams Wort bauen.** Sein Wunsch ist **zwölf Tage alt**,
und seit dem 27.08. steht seine andere Aussage daneben: *„Ich brauche nicht
täglich eine unsinnige Fehlermeldung"* und *„später im laufenden Betrieb
möchte ich davon gar nichts mehr mitbekommen."* **Vier Warnstufen sind vier
zusätzliche Meldungen** — das kann derselbe Ärger werden. Die Frage an ihn
lautet deshalb nicht „bauen?", sondern: **welche Stufen willst du wirklich
sehen — alle vier, oder nur 80 und 95?**

---

## Auflagen

- N-12 bis N-15 sind **Ablage-Einträge, kein Code.**
- **N-12 ausdrücklich ohne Eingriff am Filter** — nur Verweis und Kommentar.
- Der Bauvorschlag **wartet auf Adams Antwort**, auch wenn er klein ist.
- 💰 Keine Kostenquelle berührt; N-12 **beschreibt** eine, entscheidet sie nicht.
- **Regressionslauf vor dem Commit**, auch bei reiner Doku.
