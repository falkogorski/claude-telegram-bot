# Bauauftrag: Die Websuche fällt still aus

**Stichtag:** 2026-08-27 · **überholt durch:** — · **maßgeblich ist diese Datei**

## Änderungsverlauf

**2026-08-27 14:20** — erste Fassung, nach Adams Freigabe um 13:52 Uhr
(„Macht den mal … bitte raus").

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau).

**Anlass:** Am 27.08.2026 zwischen 13:30 und 14:00 Uhr lieferte unsere Websuche
bei zwölf von fünfzehn Anfragen „Keine Treffer". Ich hielt das für „nichts
gefunden" und schrieb Adam, ich könne einen Teil der Recherche nicht belegen.
Erst eine Direktabfrage zeigte: **Es hatte gar keiner gesucht.** Alle vier
Zulieferer für allgemeine Websuche waren ausgefallen.

**Diese Sitzung hat kein Schreibrecht im Projektarchiv.** Der Konfigurationsteil
(Auftrag 2) liegt allerdings außerhalb des Archivs und wäre von hier aus
machbar — siehe dort.

---

## Lage — gemessen, nicht vermutet

Die Direktabfrage gegen den Suchdienst gab aus:

```
Treffer: 0
Unresponsive: [['brave', 'Suspended: too many requests'],
               ['duckduckgo', 'CAPTCHA'],
               ['google cse', 'unexpected crash'],
               ['startpage', 'unexpected crash']]
```

Der Dienst hat **dreiundachtzig aktive Zulieferer**. Für die Kategorie
allgemeine Websuche sind es aber genau diese vier — der Rest bedient Bilder,
Videos, Nachrichten, Wissenschaft, Pakete, Karten.

**Zwei drosseln unter Last, zwei stürzen dauerhaft ab.** Die Absturzursache ist
**ungeprüft**; die Konfiguration beider steht ohne Zugangsdaten in der
Standarddatei, was bei Google CSE eine naheliegende, aber unbelegte Erklärung
wäre.

### Warum es niemandem auffiel

`bot.py`, Zeilen 3211 bis 3213:

```python
results = (data.get("results") or [])[:8]
if not results:
    return {"content": [{"type": "text", "text": f"Keine Treffer für „{q}“."}]}
```

Der Suchdienst liefert im selben JSON das Feld `unresponsive_engines` mit — **es
wird nirgends ausgewertet.** Ein Totalausfall aller Zulieferer ist für den
Aufrufer daher nicht von „das Netz weiß nichts dazu" zu unterscheiden.

Das ist die Fehlerklasse, die Adam am 27.07. benannt hat: **ein Ausbleiben, das
wie Ruhe aussieht.** Kein Absturz, keine Fehlermeldung, kein Protokolleintrag —
nur eine Antwort, die höflich klingt und falsch ist.

**Die Folge ist keine theoretische.** Ich habe Adam an diesem Vormittag
geschrieben, ich könne die Funktionen zweier Assistenten „nicht belegt" sagen.
Richtig wäre gewesen: „Unsere Suche ist ausgefallen."

---

## Auftrag 1 — Der Ausfall muss sich melden (der Kern)

**Stelle:** `bot.py`, `_searxng_search_tool`, Zeilen 3196 bis 3214.

**Auflage:** Bei null Treffern wird geprüft, ob überhaupt ein Zulieferer der
Kategorie allgemeine Websuche geantwortet hat. Wenn nicht, sagt das Werkzeug
genau das — mit den Namen der ausgefallenen Zulieferer und ihrem Grund, damit
die Ursache im Protokoll steht.

**Erwarteter Wortlaut, sinngemäß:**

> Die Suche konnte nicht ausgeführt werden — kein Zulieferer hat geantwortet
> (brave: zu viele Anfragen, duckduckgo: Captcha, google cse: Absturz,
> startpage: Absturz). Das ist kein „nichts gefunden".

**Wichtig für die Formulierung:** Der Unterschied muss auch für ein Modell
eindeutig sein, das den Text liest — ich habe heute vier Stunden lang die
falsche Auskunft weitergegeben, weil sie plausibel klang.

**Zusätzlich:** Auch bei Teil-Ausfall (es antworten weniger als zwei) gehört ein
kurzer Vermerk an die Trefferliste. Ergebnisse aus einem einzigen Zulieferer
sind schmaler, als sie aussehen.

---

## Auftrag 2 — Die Basis verbreitern

**Stelle:** `/home/claudebot/searxng/settings.yml` — **außerhalb des
Projektarchivs**, also nicht Micks Zuständigkeit im engeren Sinn.

**Befund:** Fünf brauchbare Zulieferer für allgemeine Websuche liegen als Modul
vor, sind aber **nicht aktiviert**: `bing`, `mojeek`, `marginalia`, `mwmbl`,
`yep`. Von Bing laufen heute nur die Bild-, Nachrichten- und Video-Varianten —
die Websuche selbst nicht.

**Vorschlag:** Bing und Mojeek aktivieren. Beide brauchen keine Zugangsdaten,
und Mojeek betreibt einen eigenen Index, drosselt also unabhängig von den
anderen. Marginalia und mwmbl sind Spezialisten für abseitige Fundstellen —
nützlich, aber nicht als Grundversorgung.

🔴 **Vorher zu klären, und das ist Adams Entscheidung:** Jeder zusätzliche
Zulieferer bekommt unsere Suchanfragen zu sehen. Der Dienst leitet sie zwar
ohne Nutzerkennung weiter, aber der Inhalt der Anfrage geht dorthin. Bei
Microsoft ist das eine bewusste Abwägung wert; Mojeek ist ein kleiner
britischer Anbieter mit eigenem Index.

**Wenn Adam zustimmt, kann diese Sitzung Auftrag 2 selbst ausführen** — die
Datei liegt in Reichweite. Der Dienst braucht danach einen Neustart.

---

## Auftrag 3 — Die abstürzenden zwei

Klären, warum `google cse` und `startpage` abstürzen. Zwei Wege:

1. **Reparieren**, falls es an fehlenden Zugangsdaten oder einer veralteten
   Abfrageform liegt.
2. **Abschalten**, falls nicht. Ein Zulieferer, der bei jeder Anfrage abstürzt,
   kostet Wartezeit und verschmutzt die Ausfallliste, ohne je etwas zu liefern.

Die Entscheidung gehört ins Protokoll, damit in einem halben Jahr niemand
rätselt, warum dort nur zwei Namen stehen.

---

## Auftrag 4 — Der Prüfer, der bisher fehlt

Im Vier-Uhr-Lauf eine Testsuche mit einem festen Begriff. **Rot**, wenn weniger
als zwei Zulieferer der allgemeinen Websuche antworten.

**Einstufung der Meldung:** Sie betrifft Adam — eine ausgefallene Suche ändert,
was ich ihm beantworten kann. Sie gehört also in den Telegram-Weg, nicht nur
ins Protokoll.

**Damit der Prüfer nicht selbst zur Plage wird:** Drosselung ist ein
vorübergehender Zustand. Erst rot melden, wenn der Ausfall an zwei
aufeinanderfolgenden Tagen auftritt oder alle vier gleichzeitig ausfallen.

---

## Was kann brechen und wer merkt es

| Bruchstelle | Wer merkt es |
|---|---|
| Auftrag 1 wird gebaut, aber die Meldung klingt weiter nach „nichts gefunden" | **Niemand** — deshalb steht der Wortlaut oben ausdrücklich im Auftrag |
| Neue Zulieferer liefern Werbemüll und verwässern die Treffer | Ich beim Lesen, aber erst nach einer Weile |
| Der Prüfer meldet täglich rot, weil Drosselung normal ist | Adam, binnen zwei Tagen — dann wird er abgeschaltet und wir haben einen blinden Wächter |
| Suche fällt weiterhin still aus, weil nur Auftrag 2 gebaut wurde | Niemand. **Auftrag 1 ist der Kern, nicht Auftrag 2** |

**Die Rangfolge, falls nur eines gebaut wird:** Auftrag 1. Eine breitere Basis
ohne Ausfallmeldung verschiebt das Problem nur nach hinten; eine Ausfallmeldung
ohne breitere Basis macht es wenigstens sichtbar.

---

## `[NACHTRAG 28.08.2026, Mick]` Stand bei der Umsetzung — drei Abweichungen

**Auftrag 1 gebaut** (`c3c25e0`), **Auftrag 4 gebaut** (`254aa10`), in der
Zielumgebung gemessen: `✅ Websuche: 10 von 15 Zulieferer antworten, 30 Treffer`.

**Der beschriebene Zustand hat sich seit dem 27.08. veraendert.** Gemessen am
28.08. gegen den laufenden Dienst:

| Behauptung im Auftrag | gemessen am 28.08. |
|---|---|
| `google cse` stuerzt ab | **bereits deaktiviert** (`enabled=false`) — Auftrag 3 insoweit erledigt |
| `startpage` stuerzt ab (`unexpected crash`) | aktiv, faellt nur zeitweise mit **CAPTCHA** aus — Drosselung, kein Absturz |
| `bing`, `mojeek`, `marginalia`, `mwmbl`, `yep` nicht aktiviert | **`mojeek`, `mwmbl` und `yep` sind aktiv** |
| vier Zulieferer der Kategorie allgemein | **fuenfzehn** aktiv (die Zahl kommt jetzt aus `/config`, nicht aus einer Liste) |

**Die Lehre daraus steht im Blaupausen-Heft:** Ein Auftrag ist eine
**Momentaufnahme** des Systems, kein Abbild davon. Haette ich die
Zulieferer-Namen aus diesem Papier abgeschrieben, waere die Pruefliste vom
ersten Tag an falsch gewesen — deshalb erfragt `_websuche_gesamt()` die Menge
beim Dienst.

**Auftrag 3 verbleibend:** Nichts stuerzt mehr ab; die verbliebenen Ausfaelle
sind CAPTCHA-Drosselungen bei `duckduckgo`, `qwant`, `startpage` und ein
`access denied` bei `yep`. Das ist der voruebergehende Zustand, fuer den die
Zwei-Tage-Daempfung gebaut wurde — **kein Handlungsbedarf, aber im Protokoll
vermerkt**, damit in einem halben Jahr niemand raetselt.

**Auftrag 2 bleibt offen und ist Adams Entscheidung** (roter Punkt: jeder
zusaetzliche Zulieferer sieht unsere Suchanfragen). Er ist heute **weniger
dringend** als am 27.08., weil bereits fuenfzehn statt vier Zulieferer
antworten.
