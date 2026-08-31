# Gesamtprüfung, Block 7 von 18 — 25.07. 23:16 bis 26.07. 17:25

**Stichtag:** 31.08.2026, 22:27 MESZ (Systemuhr abgelesen; Container läuft auf UTC)
**Gelesen:** 23 Nachrichten · **Kandidaten:** 8 · **Lücken:** 5 · **gedeckt:** 3
**Geprüft gegen:** `MIGRATION.md` auf `2c167ad` (Branch `mac-produktivstand`),
`bot.py`, `docs/entscheidungsvorlagen/kontingent-fallback-ebene2.md`

---

## Die Lücken

### ① Adams Entscheid zum Zusatzguthaben ist nirgends abgelegt

**Wortlaut (26.07., 15:33):** *„Das wäre natürlich ein wichtiger Punkt. Das zu
wissen. Und wenn man das nicht weiß, kann man damit halt so … natürlich nicht
arbeiten. **Das heißt, man muss es deaktiviert lassen. Nur als Notfall
einschalten sozusagen.**"*

Das ist eine **Entscheidung**, kein Gedanke: Der Zukauf von Kontingent bleibt
aus, weil **nicht sichtbar ist, wann er greift**.

**Gemessen:** `kontingent-fallback-ebene2.md` führt Weg **E — Zusatzguthaben**
neutral in der Fünfer-Tabelle, mit 💰-Hinweis, **ohne Adams Auflage**. Wer die
Vorlage heute liest, findet fünf gleichrangige Wege — und nicht, dass einer
davon bereits mit einer Bedingung versehen ist.

**Warum das mehr als Formsache ist:** Die Begründung ist der eigentliche Wert.
*Ein Ausweichweg, dessen Greifen man nicht sieht, ist nicht benutzbar* — das
ist derselbe Gedanke wie „angeboten, nie automatisch genommen", nur schärfer,
weil er ein konkretes Nein enthält.

### ② Die Auflage „laufende Prozesse werden gestoppt" fehlt

**Wortlaut (26.07., 15:11):** *„Das halt laufende Prozesse, die … größeres
Kontingent verbrauchen, möglichst automatisch gestoppt werden … weil das dann
schlicht einfach nur das Geld verpulvert."*

**Gemessen:** Für **Ebene 1** ist das erfüllt — 5.31 legt den Auftrag zurück
in die Warteschlange und schläft bis zur Rücksetzzeit. **Für Weg A und E
steht es nirgends.** Genau dort beißt es aber: Solange nur pausiert wird,
kostet Weiterlaufen nichts; sobald ein **bezahlter** Topf dahinterliegt,
läuft die Uhr mit Geld.

**Das ist eine 💰-Auflage, keine Bequemlichkeit** — und sie gehört an Weg A
und E in die Vorlage, nicht in einen Bauauftrag.

### ③ Das Heimgerät als Backup-Medium — und das trifft den Befund von heute

**Wortlaut (26.07., 15:33):** *„Hauptsache, dass mit dem Raspberry und dem
Tunnel und so weiter wird schon mal umgesetzt. **Und in dem Zuge lässt sich
das ja auch als Backup Medium schon einrichten.** … Und dafür muss natürlich
dann auch die Speichergröße treffen sein."*

**Gemessen:** Der Heimtunnel steht sauber im Drehbuch (Zeile 1471, mit Datum,
Diagnose und Aufschub-Begründung) — **aber ausschließlich als YouTube-Weg.**
`docs/konzept-heimtunnel-youtube.md` enthält die Zeichenkette *Backup*
**kein einziges Mal**.

**Und hier schließt sich der Kreis zu heute Vormittag:** Punkt 4.1 sichert
**Mac ← VPS**. Der Mac ist das **einzige** Sicherungsziel — er muss laufen,
und er ist genau die Abhängigkeit, die der Backlog-Punkt *Mac-Unabhängigkeit*
loswerden will. Adam hatte am 26.07. bereits die Lösung dafür benannt, und
sie ist **an keiner der beiden Stellen** vermerkt: nicht beim Heimtunnel,
nicht beim Backup.

**Zusammen mit dem Backup-Befund vom Vormittag** (Pfadliste als Aufzählung,
25 von 27 Ablageorten außerhalb) ergibt das **eine** Frage an Adam statt
zweier — sie steht unten.

### ④ + ⑤ Zwei Dialog-Regeln, beide ausdrücklich zum Festhalten aufgegeben

**Regel 1 (26.07., 15:26) — die Ansage kommt zuerst, ungebündelt:** *„Ihr
hilft mir aber nur was, wenn ich diese Angabe auch zeitnah bekomme … die
Sprachnachrichten … wurden erst nach dem Konzeptentwurf hier reingeschickt.
Und das ist natürlich unsinnig … **setzt das mal bitte auch … um.**"*

**Regel 2 (26.07., 15:39) — zügig antworten als Grundsatz:** *„Das hatte ich
schon mal festgelegt. **Das muss eine Grundregel sein im Dialog miteinander**
… daher bitte ich das zu beherzigen und auch **nochmal wirklich nachhaltig
festzuhalten**."*

**Gemessen in `bot.py`:** Der Systemprompt besteht aus dem `claude_code`-Preset
plus `_QUALITY_GUIDANCE` (Antwortqualität, Quellenpflicht, Repo-Zugriff) plus
Gedächtnis plus Mitschrift. **Keine der beiden Regeln steht darin.** Die
vorhandenen „das dauert…"-Ansagen sind **je Befehl fest eingetippt**
(`bot.py:4777, 4809, 5632, 5687`), keine allgemeine Verhaltensregel.

Am nächsten kommt eine Vormerkung unter 5.25: *„transparente Zwischen-Updates
bei Langläufern"* aus den Manus-Lehren — **das ist etwas anderes.** Adam
verlangt keine periodischen Fortschrittszeilen, sondern eine **Reihenfolge**:
erst die Ansage, was und wie lange, dann das Ergebnis, und beides **nicht in
einem Bündel**.

**⚠️ Meine Grenze, und ich nenne sie ausdrücklich:** Die Gedächtnisdateien des
Bots liegen unter `~/.claude/memory/` **auf dem VPS** und sind **nicht im
Repo** — ich kann sie von hier nicht lesen. Beide Regeln könnten dort stehen.
**Gemessen habe ich nur den Code.** Mick kann das in einem Griff klären; bis
dahin sind das begründete Verdachte, keine belegten Lücken.

**Nebenfund derselben Messung:** `CLAUDE.md` trägt unter *Bot-Verhalten (bei
Migration in `bot.py` einbauen)* die Anweisung, dem Systemprompt den Satz
*„Du bist ein Telegram-Bot; nimm nicht an, wo oder an welchem Gerät der Nutzer
sitzt"* hinzuzufügen. **Er steht dort nicht** — derselbe Vorbehalt gilt.

---

## Was gedeckt ist — und eine Antwort, die besser ist als der Wunsch

**Adams große Frage des Tages** (26.07., 14:53): *„Was passiert eigentlich,
wenn das Anthropics-Kontingent aufgebraucht ist? … Wir brauchen ja definitiv
dieses lokale KI-Modell, weil … dann wärst du ja sonst einfach stumm."*

**Sie ist beantwortet, und zwar besser als erhofft:**
- **Ebene 1 ist gebaut** (5.31, verifiziert 25.07.): nichts geht verloren, der
  Auftrag bleibt vorn in der Warteschlange, Rücksetzzeit wird **gelesen, nie
  geraten**.
- **Der lokale Ersatz ist gemessen und ehrlich verneint:** Weg B der Vorlage
  sagt, Ollama läuft zwar, aber *„der Server hat keine GPU; für ein Modell,
  das den Hauptagenten ersetzen könnte, fehlt schlicht die Rechenleistung."*
  **Das ist die richtige Art, einen Wunsch nicht zu erfüllen** — mit einer
  Messung statt mit einem Versprechen.
- **Der Notfallplan hat seit heute einen Ort:** 9.17, mit dem Entscheid
  *planen statt bauen*.

**Telegram-Partnerprogramm** (25.07., 23:25) und **Ernährungsassistent nach
Anthony William** (25.07., 23:16 und 23:28) sind **keine Lücken des
Technik-Drehbuchs** — sie gehören in das Einkommens-Dokument, das Adam heute
als eigenes Drehbuch entschieden hat. Sie sind der Beleg, dass dieses Dokument
**bereits Inhalt hat, bevor es angelegt ist**: ein Raum dafür existiert seit
dem 24.07. (6.6, *Handelshaus → Affiliate-Projekt*), ein Punkt nie.

**Die To-do-Bitte** („bau das mal bitte in meine Tudus ein und sortiere es")
ist eine **Nutzung**, keine Anforderung — 7.1/7.4/7.5 decken das Feld.

---

## Die eine Frage an Adam aus diesem Block

Sie ersetzt die drei Backup-Fragen von heute Vormittag **nicht**, sondern
kommt hinzu — und sie könnte zwei davon erledigen:

> **Soll das Heimgerät, wenn es für den Tunnel ohnehin angeschafft wird,
> zugleich das zweite Sicherungsziel werden?**

Damit hinge die Sicherung nicht mehr allein am eingeschalteten Mac, und die
Frage nach Größe und Kosten fiele **einmal** an statt zweimal. **Ich empfehle
ja** — aber erst, wenn der Tunnel ohnehin gebaut wird; ein Gerät nur fürs
Backup wäre eine eigene Entscheidung mit eigener Kostenfrage.

---

## Laufender Stand der Gesamtprüfung

| | |
|---|---|
| Blöcke gelesen | **7 von 18** |
| Zeitraum | 13.07. – 26.07. |
| Kandidaten gedeckt | 15 |
| **Lücken gesamt** | **13** (8 aus Blöcken 1–6, 5 aus Block 7) |
| davon mit Vorbehalt | 3 (④ ⑤ + Nebenfund — VPS-Gedächtnis nicht einsehbar) |

**Erwartung für Block 8 unverändert:** Die Trefferdichte sollte steigen, weil
der Juli über den kontrollierten Blockweg lief, der August direkter.
