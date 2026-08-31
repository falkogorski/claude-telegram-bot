> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren. **Adams Freigabe
> liegt vor.** Dieses Papier steht für sich — Claudias Originale erreichen ihn
> nicht, deshalb sind ihre Auflagen hier im Wortlaut enthalten.

# Freigabe: drei Bauaufträge Claudias, geprüft und mit Auflagen

**Stichtag:** 01.09.2026, 00:58 MESZ · **Von:** Engywuck (Kontrolle)
**Adams Freigabe:** 31.08.2026, kurz vor Mitternacht — *„ja, würde ich gerne
freigeben"*, auf meinen Prüfbericht hin.
**Geprüft am Code**, Branch `mac-produktivstand`, Stand `2c167ad`.

**Warum dieses Papier so ausführlich ist:** Du hast meinen Prüfbericht, aber
**nicht Claudias Originale** — der Weg Claudia → Mick existiert nicht
(gemessen 31.08.). Ein Prüfbericht ohne Gegenstand ist keine Grundlage.
Deshalb steht hier alles, was du brauchst.

---

# ① Deutsche Beschriftung — Adams Dringendes, hängt an nichts

**Anlass:** Adam am 31.08., 10:08 — *„warum stehen die nicht auf Deutsch?"*
Rein sprachlich, **keine Verhaltensänderung.** In `bot.py`:

| Zeile | heute | künftig |
|---|---|---|
| 3272 | `🔐 Permission request` | `🔐 Genehmigungs-Anfrage` |
| 3246 | `✅ Allow` | `✅ Genehmigen` |
| 3247 | `❌ Deny` | `❌ Verweigern` |
| 3264 | `🔓 Always allow {tool}` | `🔓 {tool} immer genehmigen` |
| 3293 | `⌛ Permission request nach 30 min abgelaufen` | `⌛ Genehmigungs-Anfrage nach 30 Minuten abgelaufen` |
| 3942 | `Permission-Anfragen: Buttons *oder* 👍 (Allow) / 👎 (Deny)` | `Genehmigungs-Anfragen: Knöpfe *oder* 👍 (genehmigen) / 👎 (verweigern)` |

**Claudias Auflage, die ich unterstreiche:** *Beim Umbenennen mitprüfen, ob ein
Prüfer auf die englischen Zeichenketten testet. Ein Test, der `"Allow"` im
Quelltext sucht, bricht sonst still.*

**⚠️ Ein Zählfehler in ihrem Papier:** Sie schreibt *„Vier Stellen"* und listet
**sechs**. Bitte alle sechs — wer die Vier für bare Münze nimmt, hört nach der
vierten auf.

**Zur Sprachfrage im Größeren:** Claudia hat ihre erste Empfehlung (deutsche
Zweitnamen im Quelltext) selbst zurückgenommen und auf **Trennung von Text und
Code** umgestellt (`gettext`/`Fluent`). Fachlich richtig — **aber nicht jetzt
bauen.** Das ist ein Umbau quer durch über zwölftausend Zeilen und nach der
Kurs-Regel reine Innenarbeit, solange es einen Nutzer gibt. Diese sechs
Textänderungen so bauen, **dass sie einer späteren Trennung nicht im Weg
stehen** — mehr nicht.

---

# ② `anthropic` aus Register und venv entfernen — ✅ unbedenklich

**Befund:** `requirements.txt` Zeile 32–35 trägt Adams Entscheid vom 28.08.:
`anthropic` ist die Bibliothek der **kostenpflichtigen** Schnittstelle, das Abo
läuft über `claude-agent-sdk`. **Zwei Pakete, zwei Geldtöpfe.** Die
Entscheidung ist nur zur Hälfte abgelegt — aus der Anforderungsliste
verschwunden, im Register und in der venv geblieben.

**Ihre Messung, von mir nachgemessen und bestätigt:**

| Prüfung | Ergebnis |
|---|---|
| Import irgendwo im Repo | **kein Treffer** |
| `claude-agent-sdk 0.2.127` verlangt | `anyio`, `mcp`, `sniffio` — **nicht** `anthropic` |
| SDK-Pin in `requirements.txt` | `0.2.127` — genau die geprüfte Fassung |
| Registereintrag | `components.json`, Zeile 33 |

**Die Gefahr, die sie nicht geprüft hat, habe ich geprüft:** LiteLLM zieht in
manchen Zusammenstellungen `anthropic` mit. **Es liegt in einer eigenen venv**
(`/home/claudebot/litellm/venv`) — die Deinstallation kann es nicht treffen.

**Auflage (ihre, unverändert):**
1. Registereintrag `anthropic` aus `components.json` entfernen.
2. Paket aus `/home/claudebot/claude-telegram-bot/.venv` deinstallieren.
3. **In dieser Reihenfolge mit Nachweis:** `pip check` → Regressionstest →
   Neustart → echter Durchlauf. Rücknahme: `pip install anthropic==0.120.0`.
4. Keinen Ersatzeintrag anlegen.

**Meine Ergänzung:** Wird der **SDK-Sprung auf 0.2.148** vorher vollzogen, ist
ihre Messung veraltet. Schritt 3 fängt das ab — **nicht abkürzen.**

---

# ③ Bash-Dauerfreigabe + sichtbarer Umschalter — ✅ mit zwei harten Auflagen

## Was gebaut wird

**(a)** `Bash` aus `_NO_ALWAYS_TOOLS` (Zeile 2278) entfernen. `Write`, `Edit`,
`MultiEdit`, `NotebookEdit`, `WebFetch` und die Kosten-Werkzeuge **bleiben
drin.**

**(b)** In Zeile 3 der Tastatur (ab `bot.py:1101`) **ein Knopf mit
Zustandsanzeige**, nach dem Muster des STT-Umschalters:
- `🔐 Genehmigen` — Rückfrage bei allem außerhalb der Positivliste. **Grundzustand.**
- `⚡ Auto ✓` — Bash gilt als dauerfreigegeben; Sperren und Abweisungen bleiben.
- `📋 Planen` — `permission_mode="plan"`, nichts wird ausgeführt.

**Ein Zustand, zwei Bedienwege:** Der Knopf „immer genehmigen" unter einer
Anfrage schaltet **denselben** Zustand wie die Tastatur.

## Warum das sicher ist — am Code gemessen, nicht angenommen

| Prüfstelle | Zeile | Ergebnis |
|---|---|---|
| Repo-Schreibsperre (8.7) | **3051** | `PermissionResultDeny` |
| `bashfreigabe.entscheiden` → ABWEISEN | **3091** | Deny |
| **Dauerfreigabe-Kurzschluss** | **3164** | `PermissionResultAllow` |

**Beide Sperren stehen rund hundert Zeilen VOR dem Kurzschluss.** Der Knopf
öffnet die **Dialog**-Klasse, nicht die **Abweis**-Klasse. Zusätzlich verlangt
der Kurzschluss selbst `not sensitive`.

## 🔴 Auflage A — Rang 2 und Rang 3 gehören in EINEN Commit

Die **gesamte** Rechtfertigung für das Aufheben der Sperre lautet: *sie ist
nicht mehr unsichtbar.* Geht (a) raus und (b) rutscht auf morgen, steht genau
der Zustand da, gegen den die Sperre gebaut wurde — **eine unsichtbare
Dauerfreigabe für das mächtigste Werkzeug.** Getrennt bauen ist hier nicht
schrittweise, sondern riskant.

## 🔴 Auflage B — der Ersatz-Prüfer muss Verhalten messen

Keine allgemeine Mahnung — **an genau dieser Stelle ist es schon passiert.**
Der Docstring von `darf_dauerfreigabe` (Zeile 2286) hält fest: Der alte Prüfer
verlangte `src.count("_NO_ALWAYS_TOOLS") >= 3` — **drei Kommentarzeilen
erfüllten die Schwelle.** Wer die Sperre aus dem Zweig entfernte und den Namen
im Kommentar stehen ließ, bekam einen grünen Prüfer und eine pauschal
freigegebene WebSearch.

**Der neue Prüfer misst:** Ein Bash-Befehl **mit** gesetzter Dauerfreigabe, der
ins Repo schreibt, **wird weiterhin abgelehnt.** Gegenprobe fahren: Zeile 3051
entfernen, der Prüfer muss rot werden. **`__pycache__` vorher löschen, den
Eingriff verifizieren, die erwartete rote Zeile vorher hinschreiben.**

## Was ausdrücklich NICHT gebaut wird

**`bypassPermissions` gehört nicht auf diesen Knopf.** Die SDK-Dokumentation
(`types.py`, Zeile 1704) sagt: *auto-approves every tool call … **before the
callback is consulted**.* Der Rückruf würde **nie** gerufen — Repo-Sperre,
Geheimnis-Schranke und alle Abweisungen fielen weg. Das Projekt hat diesen
Fehler am 22.08. schon einmal gemacht (`bot.py` ab Zeile 4360). **Claudias
Absage ist richtig und bleibt.**

---

# ④ Pipe- und Semikolon-Zerlegung — ✅ **nur mit der Boden-Bedingung**

## Was gebaut wird

1. Den Befehl an `|` **und an `;`** in Glieder zerlegen.
2. **Jedes Glied einzeln** durch die bestehende Prüfung.
3. **Frei nur, wenn jedes Glied frei ist** — ein einziges Dialog- oder
   Abweis-Urteil entscheidet für den ganzen Befehl, mit dem Grund des
   betroffenen Glieds.

**Bleibt unverändert:** `$(…)`/Backticks/`<(…)`/`${…}` (Inhalt zur Prüfzeit
unbekannt) · `||` (Bedingung, kein Datenstrom) · Umlenkungen `>`/`>>` samt
Zielprüfung · Repo-Sperre und Geheimnis-Schranke stehen weiterhin **darüber**.

## 🔴 Die Bedingung, ohne die es ein Loch ist

**Gemessen:** `_aufloesen` (`bashfreigabe.py:214`) ist
`Path(roh).expanduser().resolve()` — aufgelöst gegen das **Arbeitsverzeichnis
des Bot-Prozesses**, nicht gegen ein `cd` im selben Befehl. Damit gilt für die
Zerlegung:

```
cd /etc ; cat passwd
```
- Glied 1 `cd /etc` — für sich harmlos.
- Glied 2 `cat passwd` — aufgelöst zu `<Arbeitsverzeichnis>/passwd` → **frei.**
- **Die Shell liest `/etc/passwd`.**

**Die Prüfung urteilt über einen anderen Pfad als den, der gelesen wird** —
derselbe Fehlertyp wie die `..`-Umgehung vom 23.08., nur über die Verkettung.

> **Zerlegen ist erlaubt, solange kein Glied den Boden verschiebt.**
> In den Dialog fällt jedes Glied, das den Zustand der folgenden Prüfungen
> ändert: **`cd`, `pushd`/`popd`, `export`, `set`, `source` und `.`, sowie
> Zuweisungen der Form `NAME=wert`.**

**Gegenprobe, die dazugehört:** `cd /etc ; cat passwd` **und**
`cd /etc && cat passwd` müssen nach dem Umbau **beide** im Dialog oder in der
Abweisung landen. Steht das nicht als Prüfzeile, ist der Fix nicht belegt.

**Claudias Erwartung „neun von zehn Proben gehen durch" ist neu zu messen** —
ihre Proben können ein `cd`-Glied enthalten.

## Ihre Frage an mich, beantwortet

Sie fragte, warum heute **genau ein** `&&` erlaubt ist. **Die Eins ist keine
Zahl, sie ist eine Form:** `bashfreigabe.py` ab Zeile 493 lässt ausschließlich
`cd <aufgelöster, geprüfter Pfad> && <ein Befehl>` durch — der Kopf **muss**
wörtlich `cd` sein, mit genau einem Ziel, geprüft gegen die erlaubten Bereiche
und `.claude`.

**Der Grund, der sich nicht verallgemeinern lässt:** `cd` verschiebt den Boden.
Deshalb genau einmal, ganz vorn, geprüft. **`|` und `;` verschieben ihn
nicht** — ein Maß, zwei Anwendungen, keine drei verschiedenen.

## Die zwei Anschluss-Aufträge, beide sinnvoll

**Befehlsart überall mitschreiben** (die Bestimmung des ersten Worts **vor** die
Vorprüfungen ziehen, bei einer Pipe die Art des auslösenden Glieds mitgeben) —
✅ **richtig und nicht nachrangig.** Ohne ihn bleibt die Auswertung blind und
Auftrag ④ wäre eine einmalige Korrektur statt eines Mechanismus.

**Das Maß auf den Anteil umstellen** — ✅ **richtig.** Ihr Befund: Die
Auswertung meldete *„Maß erreicht"* bei **91 Prozent Dialoganteil**, weil sie
eine absolute Wochenzahl misst. Eine ruhige Woche meldet grün, auch wenn nichts
durchgeht. **Das ist ein Prüfer, der die falsche Frage beantwortet** — dieselbe
Klasse wie der Regressionslauf mit eingetippter Gesamtzahl.

---

# Was NICHT freigegeben ist

| Auftrag | Stand |
|---|---|
| Freigaben-Erinnerung + Postfach-Skript | **ungeprüft** — meine Prüfung folgt |
| Sitzungsstart legt den Stand vor | **ungeprüft** — meine Prüfung folgt |
| Sprach-Trennung (`gettext`/`Fluent`) | **zurückgestellt**, siehe ① |

**Bitte nichts davon bauen**, bis die Prüfung vorliegt.

---

# Auflagen für alle vier

- **Regressionslauf vor jedem Commit** — auch bei den reinen Textänderungen.
- **③ in einem Commit** (Auflage A), **④ erst mit der Boden-Bedingung.**
- 💰 **Keine Kostenquelle berührt.** ② entfernt die Bibliothek des
  kostenpflichtigen Wegs — das spart nichts und kostet nichts, es räumt auf.
- Bei ③ und ④ **Gegenprobe fahren**, `__pycache__` löschen, erwartete rote
  Zeile vorher hinschreiben.
