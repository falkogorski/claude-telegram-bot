> **Zweck: WEITERGABE → Claudia (und Mick, bevor gebaut wird)** · **Zu tun:**
> weiterreichen. **Ein Auftrag darf so NICHT gebaut werden** — Abschnitt 3.

# Prüfung von Claudias Bauaufträgen vom 31.08.

**Stichtag:** 31.08.2026, 23:46 MESZ · **Von:** Engywuck (Kontrolle)
**Auftrag Adams (10:14 Uhr):** *„Es muss auf jeden Fall von Engywuck nochmal
intensiv auf **Plausibilität**, auf **Aktualität** und auf **Notwendigkeit**
hin geprüft werden."*
**Geprüft am Code**, Branch `mac-produktivstand`, Stand `2c167ad`.

**Ehrlich zum Umfang:** Ich habe **drei von fünf** Aufträgen tief geprüft —
die drei, die die Freigabestelle oder die Umgebung berühren. Die beiden
übrigen (Freigaben-Erinnerung, Sitzungsstart) folgen; sie tragen kein
Sicherheitsrisiko, das ein Warten rechtfertigt.

---

# 1 · `anthropic` entfernen — ✅ **plausibel, aktuell, notwendig**

**Ihre Messung habe ich nachgemessen, alles bestätigt:**

| Prüfung | Mein Ergebnis |
|---|---|
| Import irgendwo im Repo | **kein Treffer** (`import anthropic` über alle `*.py`) |
| `requirements.txt` | Zeile 32–35 trägt den Entscheid vom 28.08. samt Begründung; **SDK ist auf `0.2.127` gepinnt** — also genau die Fassung, gegen die sie gemessen hat |
| Registereintrag | vorhanden, `components.json` Zeile 33 |

**Und die eine Gefahr, die sie nicht geprüft hat, habe ich geprüft:** LiteLLM
zieht in manchen Zusammenstellungen `anthropic` mit. **Es liegt in einer
eigenen venv** (`/home/claudebot/litellm/venv` gegen
`/home/claudebot/claude-telegram-bot/.venv`) — die Deinstallation kann es also
nicht treffen. **Kein Einwand.**

**Eine Auflage ergänze ich:** Es liegt eine Prüfliste für den **SDK-Sprung auf
0.2.148** im Repo. Wird der **vor** dieser Deinstallation vollzogen, ist ihre
Messung veraltet — eine neuere Fassung kann Abhängigkeiten hinzugefügt haben.
Ihr eigener Schritt 3 (`pip check` vor dem Regressionstest) fängt das ab;
**bitte in dieser Reihenfolge bleiben und nicht abkürzen.**

---

# 2 · Bash-Dauerfreigabe — ✅ **die Begründung trägt, am Code bestätigt**

Das war der Auftrag, bei dem ich mit dem größten Misstrauen angefangen habe.
Ihre Kernbehauptung: Der Knopf öffnet die **Dialog**-Klasse, nicht die
**Abweis**-Klasse. **Das habe ich an den Zeilennummern nachgemessen:**

| Prüfstelle | Zeile | Ergebnis |
|---|---|---|
| Repo-Schreibsperre (8.7) | **3051** | `PermissionResultDeny` |
| `bashfreigabe.entscheiden` → ABWEISEN | **3091** | Deny |
| **Dauerfreigabe-Kurzschluss** | **3164** | `PermissionResultAllow` |

**Beide Sperren stehen rund hundert Zeilen VOR dem Kurzschluss.** Eine
Bash-Dauerfreigabe kann sie also nicht überspringen — sie erspart die
Rückfrage, nicht die Ablehnung. Die dritte Bedingung `not sensitive` steht
ebenfalls im Kurzschluss selbst.

**Ihre Absage an `bypassPermissions` ist richtig und wichtig.** Der Rückruf
würde nie gerufen; alle drei Prüfstellen fielen weg. Der Vorfall vom 22.08.
steht in `bot.py` ab Zeile 4360 — er ist der Beleg, nicht die Anekdote.

## Zwei Auflagen, die ich hinzufüge

**① Rang 2 und Rang 3 gehören in EINEN Commit.** Die gesamte Rechtfertigung
für das Aufheben der Sperre lautet: *sie ist nicht mehr unsichtbar*. Geht
Rang 2 raus und Rang 3 rutscht auf morgen, steht **genau der Zustand**, gegen
den die Sperre gebaut wurde — eine unsichtbare Dauerfreigabe für das
mächtigste Werkzeug. **Getrennt bauen ist hier nicht „schrittweise", sondern
riskant.**

**② Der Ersatz-Prüfer muss Verhalten messen, nicht Text.** Das ist keine
allgemeine Mahnung — **an genau dieser Stelle ist es schon einmal passiert.**
Der Docstring von `darf_dauerfreigabe` (Zeile 2286) hält es fest: Der alte
Prüfer verlangte `src.count("_NO_ALWAYS_TOOLS") >= 3` — **drei Kommentarzeilen
erfüllten die Schwelle.** Wer die Sperre aus dem Zweig entfernte und den Namen
im Kommentar stehen ließ, bekam einen grünen Prüfer und eine pauschal
freigegebene WebSearch.

**Der neue Prüfer muss also messen:** Ein Bash-Befehl mit gesetzter
Dauerfreigabe, der ins Repo schreibt, **wird weiterhin abgelehnt** — und der
Prüfer muss rot werden, wenn man Zeile 3051 entfernt. **Gegenprobe fahren,
`__pycache__` vorher löschen, die erwartete rote Zeile vorher hinschreiben.**

---

# 3 · 🔴 Pipe- und Semikolon-Zerlegung — **so nicht bauen**

Der Auftrag ist gut gedacht und trifft ein echtes Ärgernis. **Aber er hat ein
Loch, und es ist dasselbe, das ihre eigene Frage an mich schon umkreist.**

## Ihre Frage, beantwortet am Code

Sie fragt, warum heute **genau ein** `&&` erlaubt ist, und ob diese Eins noch
begründbar wäre, wenn `;` und `|` beliebig zerlegt werden.

**Die Eins ist keine Zahl — sie ist eine Form.** `bashfreigabe.py` ab Zeile
493 lässt **ausschließlich** dieses Muster durch:

```
cd <aufgelöster, geprüfter Pfad>  &&  <ein Befehl>
```

Der Kopf **muss** wörtlich `cd` sein, mit **genau einem** Ziel, das aufgelöst
und gegen die erlaubten Bereiche und `.claude` geprüft wird. Alles andere vor
dem `&&` fällt in den Dialog.

**Und darin steckt der Grund, der sich nicht verallgemeinern lässt:** `cd`
**verschiebt den Boden, auf dem jede folgende Pfadprüfung steht.** Deshalb darf
es genau einmal vorkommen, ganz vorn, und geprüft.

## Das Loch, das daraus folgt

`_aufloesen` (Zeile 214) ist `Path(roh).expanduser().resolve()` — **aufgelöst
gegen das aktuelle Arbeitsverzeichnis des Bot-Prozesses**, nicht gegen ein `cd`
im selben Befehl. Damit gilt für die vorgeschlagene Zerlegung:

```
cd /etc ; cat passwd
```

- **Glied 1:** `cd /etc` — für sich harmlos.
- **Glied 2:** `cat passwd` — `passwd` wird aufgelöst zu
  `<Arbeitsverzeichnis>/passwd`. Das liegt im erlaubten Bereich → **frei.**
- **Die Shell liest `/etc/passwd`.**

**Die Prüfung urteilt über einen anderen Pfad als den, der gelesen wird.** Das
ist derselbe Fehlertyp wie die `..`-Umgehung vom 23.08., nur über die
Verkettung statt über den Pfad.

## Die Bedingung, die den Auftrag rettet

Die Zerlegung ist richtig — **sie braucht nur eine Bedingung**, und die folgt
direkt aus der obigen Einsicht:

> **Zerlegen ist erlaubt, solange kein Glied den Boden verschiebt.**
> Jedes Glied, das den Zustand der folgenden Prüfungen ändert, fällt in den
> Dialog: `cd`, `pushd`/`popd`, `export`, `set`, `source` und `.`, sowie
> Zuweisungen der Form `NAME=wert`.

Damit ist auch ihre Frage sauber beantwortet, ohne drei verschiedene Maße:
**`|` und `;` verschieben den Boden nicht — `&&` mit `cd` davor tut es genau
einmal und geprüft.** Ein Maß, zwei Anwendungen.

**Ihre Erwartung „neun von zehn Proben gehen durch" ist damit neu zu
messen** — die Proben können ein `cd`-Glied enthalten.

**Und die Gegenprobe, die dazugehört:** `cd /etc ; cat passwd` und
`cd /etc && cat passwd` müssen nach dem Umbau **beide** im Dialog oder in der
Abweisung landen. Steht das nicht als Prüfzeile, ist der Fix nicht belegt.

---

# 4 · Zur Sprachfrage — ihre Revision ist richtig, mit einer Einschränkung

Sie hat ihre eigene Empfehlung von 23:25 zurückgenommen (deutsche Zweitnamen
im Quelltext) und auf **Trennung von Text und Code** umgestellt, mit `gettext`
oder `Fluent`. **Fachlich richtig**, und es passt zu Adams Begründung (das
spätere Produkt, „möglicherweise sämtliche Sprachen").

**Meine Einschränkung:** Das ist ein **Umbau quer durch `bot.py`** — über
zwölftausend Zeilen mit hunderten Textstellen. Nach der Regel *Probelauf im
Klon* (R4) ist das ein Musterfall, und nach der Kurs-Regel ist es **reine
Innenarbeit ohne Erlösbezug**, solange es genau einen Nutzer gibt.

**Empfehlung:** Die vier Textänderungen aus Auftrag 2b jetzt bauen — **so, dass
sie einer späteren Trennung nicht im Weg stehen**, genau wie sie schreibt. Die
Trennung selbst **nicht jetzt**, sondern gebündelt mit 9.6/9.18, wenn ein
zweiter Nutzer real wird. Vorher ist sie eine Wette auf einen Zeitpunkt, den
niemand kennt.

---

# Zusammenfassung

| Auftrag | Urteil |
|---|---|
| `anthropic` entfernen | ✅ bauen, Reihenfolge einhalten |
| Bash-Dauerfreigabe (Rang 2+3) | ✅ bauen — **in EINEM Commit**, Prüfer verhaltensbasiert |
| `bypassPermissions` ablehnen | ✅ bestätigt, richtig begründet |
| **Pipe/Semikolon zerlegen** | 🔴 **erst nach der Boden-Bedingung** (Abschnitt 3) |
| Sprach-Trennung (gettext/Fluent) | ⏭️ Textfixes ja, Umbau später |
| Freigaben-Erinnerung, Sitzungsstart | ⏳ Prüfung folgt |

**Zur Qualität, weil es fair ist, das zu sagen:** Diese Aufträge sind sorgfältig
gemessen, mit Zeilennummern belegt und tragen ihre eigenen Berichtigungen im
Kopf (die erfundene 180-Tage-Schwelle hat sie selbst gestrichen). **Der eine
Fund in Abschnitt 3 war nur zu finden, weil sie die richtige Frage selbst
gestellt hat** — sie hat die Stelle bezeichnet, an der es klemmt, und dann
darum gebeten, dass jemand anders sie prüft. Genau so soll das laufen.
