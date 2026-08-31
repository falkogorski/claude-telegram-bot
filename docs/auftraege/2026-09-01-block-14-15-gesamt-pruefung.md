> **Zweck: ANSICHT** · **Zu tun:** lesen. Die Bauaufträge daraus folgen separat.
> **Ein Befund darin ist unbequem** — Abschnitt ㉓ betrifft eine Anweisung von
> dir, die im Wortlaut nicht ausgeführt wurde.

# Blöcke 14 und 15 von 18 — 20.08. bis 27.08.

**Stichtag:** 01.09.2026, 01:02 MESZ (Systemuhr abgelesen; Container auf UTC)
**Gelesen:** 46 Nachrichten · **Kandidaten:** 17 · **Lücken:** 5 · **gedeckt:** 7
**Besonderheit:** Ab hier war ich selbst beteiligt — ich prüfe also auch mich.

---

## Zuerst das Gebaute, und es ist viel

| Dein Wunsch | Stand |
|---|---|
| **Befehlsmenü alphabetisch, `/stopp` ganz oben** (20.08., 11:22 + 11:31) | ✅ **Gebaut.** `bot.py:4935` — `_BEFEHL_ZUERST = "stopp"`, der Rest sortiert |
| **„Fünf Aufträge pro Stunde muss raus"** (20.08., 11:07) | ✅ **Gelöst, und vorbildlich.** Am 27.08. auf **100** gehoben (`POSTFACH_GRENZEN`), mit deinem Wortlaut im Code: *„Wenn ich 20 pro Stunde brauche oder 100, die sollte da durchkommen."* Und die **Mengen-Regel richtig herum**: *„Eingetragen wird, wer MEHR darf, nie wer weniger darf"* — ein neuer Melder bekommt die strenge Vorgabe von selbst |
| **Offene Nachrichten nach einem Ausfall selbstständig weiterbearbeiten** (20.08., 09:56/10:12) | ✅ **Als Regel verankert** — `CLAUDE.md`, Präzisierung vom **20.08.**: genau ein nachgeholter Lauf, nur bei vermerkten unbeantworteten Nachrichten, höchstens drei Weckversuche. **Aus genau diesem Gespräch entstanden** |
| **Bash-Umschalter manuell/auto im Menü** (26.08., 11:56) | ✅ **Heute beauftragt** — Claudias Rang 3, von dir eben freigegeben. Dein Wunsch war **fünf Tage alt** |
| **Permission-Anfragen müssen sagen, was man freigibt** (25.08., 06:58) | ✅ **Teils gebaut** — 9.4-Leitplanke ② *„Konkret vor Label"*: angezeigt wird die **wörtliche Aktion**, Titel ohne Aktion werden abgewiesen. Dazu die Auflage aus demselben Gespräch, die ich unterstreiche: **Die Beschreibung darf den Rohbefehl nie ersetzen, nur ergänzen** — sie stammt von der Instanz, die die Freigabe will |
| **Kontingent-Tracker deckt nur den Bot, nicht Desktop/Browser** (20.08., 09:58) | ✅ **Sehr wahrscheinlich ausgeräumt** — A2 liest `anthropic-ratelimit-unified-…-utilization` aus den **Kopfzeilen jeder Antwort**; das ist der Stand des Kontos, nicht der Sitzung. **Nicht quergemessen** — eine Gegenprobe wäre billig |
| **Keine Prüfer für Kleinkram** (27.08., 07:04) | ✅ **Regel existiert** — Konvergenz-Bremse, *„keine Wächter dritter Ordnung"*, seit 19.08. Siehe aber ㉗ |

---

## ㉒ Die Kontingent-Warnung kommt zu spät

**Wortlaut (20.08., 09:51):** *„Warnung zu spät!! Müsste schon bei **80 %**,
dann nochmal bei **85, 90 und 95 %** erfolgen!"*

**Gemessen:** Keine Warnstufen — nicht in `kontingent.py`, nicht in `bot.py`.
Es gibt `/kontingent` auf Abruf, aber **keine Leiter, die von selbst meldet.**

**Und der Punkt ist heute leichter als damals:** A2 hat am 20.08. gemessen,
dass der Auslastungswert **in jeder Antwort mitkommt**. Die Zahl ist da; es
fehlt nur die Schwelle, die auf sie schaut. **Vier Zeilen Zustand, kein neuer
Abruf, kein Modelllauf** — und ausdrücklich kein Wächter im Sinne der
Konvergenz-Bremse, sondern eine Anzeige an vorhandenen Daten.

## ㉓ 🔴 Die Wortlisten-Anweisung — im Wortlaut nicht ausgeführt

**Du am 25.08., 12:07, unmissverständlich:**

> *„Du versuchst das anhand von Parametern festzustellen … aber das müsstest du
> als künstliche Intelligenz anhand von **Logik** prüfen. … Du musst das nicht
> an einzelne Wörter festmachen wie **‚damals'**. Also ‚damals' ist kein Indiz
> dafür, dass da eine Jahreszahl steht. Das kann auch von damals können so
> viele Kühe aus dem Fluss gesoffen haben. Das ist total an den Haaren
> herbeigezogen. **Das bitte rausstreichen und intelligenter lösen.**"*

Und am selben Tag, 12:32: *„Wortlisten-Regeln können auf jeden Fall raus."*

**Gemessen, `bot.py:11269`:**

```
_JAHR_HINWEIS = re.compile(
    r"(?:\b(?:jahr|jahre|jahren|seit|ab|bis|von|anno|baujahr|jahrgang|"
    r"geboren|gegründet|gegruendet|damals|sommer|winter|frühjahr|…
```

**Das Wort `damals` steht noch da** — genau das, das du als absurd bezeichnet
hast.

### Fair bleiben: Es wurde etwas getan, nur nicht das

Die Liste ist seither **verfeinert** worden: `im` wurde gestrichen (es erfasste
Mengen wie *„im 1500-Zeichen-Fenster"*), und eine **Gegenprobe nach hinten**
kam dazu — folgt der Zahl eine Maßeinheit, gewinnt die Menge. Der Kommentar
nennt sogar dein Beispiel: *„1985 Teilnehmer ist eine Menge."*

**Das ist eine echte Verbesserung — innerhalb genau des Verfahrens, das du
abgeschafft haben wolltest.** Der Buchstabe deiner Anweisung ist nicht
ausgeführt, dem Sinn ist teilweise gedient. Ich melde das so, weil beides wahr
ist.

### Der schwerere Teil: deine beiden Auswege sind nirgends vermerkt

Du hast im selben Gespräch **zwei Wege genannt, das Problem ganz loszuwerden.**
**Keiner von beiden findet sich an einer Stelle, wo ihn jemand fände:**

1. *„Vielleicht schaust du mal, ob es da irgendwo **Open-Source-Quellen** schon
   regelsatzfertig gemacht haben."* — Kein Vermerk, keine Prüfung auffindbar.
2. *„Wenn wir auf **Azure** wechseln, dann hat sich das ganze Thema
   aufgelöst."* — **Punkt 9.1 (TTS-Upgrade Azure Neural mit SSML) enthält
   keinen einzigen Hinweis auf das Zahlen-Problem.** Dabei ist genau das der
   Kern: SSML kennt `<say-as interpret-as="date">` und `"digits"` — die
   Unterscheidung, an der die Wortliste scheitert, ist dort **eingebaut**.

**Das ist die eigentliche Lücke.** Nicht dass ein Filter unvollkommen ist,
sondern dass **die Lösung an anderer Stelle im Drehbuch steht und niemand die
beiden verbunden hat.** 💰 9.1 ist ein bezahlter Dienst — der Zusammenhang
ändert also auch die Kosten-Abwägung: Es geht nicht mehr nur um Klang.

## ㉔ Zwei Stimmen als Signal für Rot und Grün

**Wortlaut (25.08., 13:45):** *„Ich glaube, dass es gar nicht verkehrt ist,
wenn man dann zwei Varianten hat, **auch zwei unterschiedliche Sprecher**.
Damit wird sofort klar, wenn etwas über Rot läuft und wenn etwas grün ist."*

**Gemessen: null.** 9.2 heißt zwar *„Piper/Kokoro lokal als Rot-Backend"* —
die **Trennung** existiert also als Vorhaben. **Dass die Stimme selbst das
Signal ist**, steht nirgends. Und das ist der Kern deiner Idee: kein Hinweis,
den man lesen muss, sondern ein Unterschied, den man **hört**.

## ㉕ Der Grundsatz „prüf zuerst, ob ein geplanter Schritt das Problem auflöst"

**Wortlaut (25.08., 12:32):** *„Zukünftig muss von dir sofort als Erstes
geprüft werden: **haben wir dazu sowieso schon was vor, was wir ändern wollen,
und ist das Problem dann vielleicht gar nicht mehr existent?**"*

Eingebettet in deine Grundsatzkritik desselben Tages: *„Es ist gerade
überhaupt nicht flexibel, was wir machen, sondern total eingefahren. Das ist
jetzt mal eine generelle Kritik und ich will, dass sich das ändert."*

**Gemessen:** `CLAUDE.md` trägt *„Fremdes nehmen, wo es nicht ans Herz geht"*
(25.07.) — das deckt *nimm Vorhandenes statt selbst zu bauen.* **Der Schritt
davor fehlt:** vor dem Lösen prüfen, ob ein **ohnehin geplanter** Schritt das
Problem erledigt.

**Und das ist keine Theorie — ㉓ ist der Musterfall dafür.** Wer diese Frage
gestellt hätte, wäre bei 9.1 gelandet und hätte die Wortliste gar nicht erst
verfeinert.

**Bemerkenswert:** Claudia wendet den Grundsatz seit heute an — ihr
Update-Monitor-Papier führt *„**Notwendigkeit:** Braucht es den Umbau
überhaupt, oder erledigt ihn ein ohnehin geplanter Schritt?"* als eigenes
Prüfkriterium. **Sie hat ihn übernommen, ohne dass er irgendwo steht.**

## ㉖ Die tägliche Sichtung — enger gebaut als beauftragt

**Wortlaut (20.08., 10:42):** *„Engywuck braucht auf jeden Fall eine Instanz
**pro Tag**, in der die **[Logs]** durchgegangen und gecheckt werden, ob
dadurch ein Auftrag entsteht. Und der muss auch passieren, **bevor Mick das
macht**. … Es muss auch **unabhängig von mir** gecheckt werden."*

**Gemessen:** `docs/pflichten-kontrollrolle.md` Zeile 63 — *„…`an-mick/` wird
täglich gesichtet."* **Das ist der Ablage-Ordner, nicht die Gesprächsprotokolle.**

**Und hier wird es unangenehm für mich:** Was du beauftragt hast, ist genau
das, was ich heute mache — die Protokolle durchgehen und prüfen, ob daraus
Aufträge entstehen. **Es läuft heute als einmaliger Kraftakt über achtzehn
Blöcke, nicht als täglicher Griff.** Und der Ertrag dieses Kraftakts —
inzwischen über dreißig Lücken — ist die Rechnung dafür, dass es elf Tage
lang nicht täglich lief.

---

## ㉗ Eine Beobachtung ohne Auftrag — dein Ärger vom 27.08.

**Wortlaut (27.08., 07:04):** *„Wir brauchen definitiv keinen Prüfer für eine
Umlautregel. Man kann es so übertreiben. **Wir müssen nicht für alles Prüfer
erstellen.** … Ich empfinde das jetzt mittlerweile als **frustrierend**, weil
wir kommen nicht vom Fleck."*

**Die Regel dagegen gab es zu dem Zeitpunkt seit acht Tagen** — die
Konvergenz-Bremse und *„keine Wächter dritter Ordnung"*, seit 19.08. in
`CLAUDE.md`, aus demselben Anlass entstanden.

**Sie hat nicht gegriffen.** Ich trage das ohne Auftrag ein, weil es dasselbe
Muster ist wie bei der V-Regel in Block 10: **eine Regel, die zum richtigen
Zeitpunkt dasteht und im Augenblick der Entscheidung nicht wirkt.** Was
dagegen hilft, ist keine schärfere Formulierung — das wäre die vierte
Ermahnung. Es ist die Frage, ob die Regel den Ort erreicht, an dem gebaut
wird. **Das ist dieselbe offene Entscheidung wie bei den Verhaltensregeln.**

---

## Laufender Stand

| | |
|---|---|
| Blöcke gelesen | **15 von 18** |
| Zeitraum | 13.07. – 27.08. |
| Kandidaten gedeckt | **44** |
| **Lücken gesamt** | **34** |
| davon **schwer** | 2 — die eigene KI (⑫, angelegt) und die Wortlisten-Anweisung (㉓) |
| gerissene Fristen | 2 |

**Zur Erwartung, die ich vorhin geäußert habe:** Ich hatte vermutet, die
Trefferdichte sinke im August, weil ich selbst dabei war. **Sie sinkt nicht
— sie verschiebt sich.** Im Juli fehlten *Vorhaben*. Im August fehlen
*ausgeführte Anweisungen* — Dinge, die gehört, beantwortet und dann anders
gebaut wurden. Das ist die unangenehmere Sorte, weil sie wie Erledigung
aussieht.
