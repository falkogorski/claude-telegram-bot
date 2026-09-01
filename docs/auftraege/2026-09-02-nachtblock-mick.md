> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren, dann schlafen.
> Adams Freigabe für A, B und C liegt vor. **Er ist die Nacht über nicht
> erreichbar — was seine Entscheidung braucht, steht am Schluss unter „nicht
> bauen" und bleibt dort liegen.**

# Nachtblock für Mick — Nacht zum 02.09.2026

**Stichtag:** 01.09.2026, 23:45 MESZ (geschrieben) · **Übergeben:** 02.09.2026, 00:06
**Von:** Engywuck (Kontrolle)
**Ausgangsstand:** `6d379fe`, 01.09.2026, 21:55 — Arbeitsbaum sauber, nichts deployt
**Nenner dieses Papiers:** 5 Blöcke · 3 davon mit Codeänderung · 1 Messung ·
1 Abschluss. **Nichts darin braucht Adam.**

**Modell und Modus:** Opus 5, mittlere Denktiefe. Für Block A die Denktiefe
hochnehmen — das ist ein Eingriff in einen Sicherheitspfad. Blöcke C und D
dürfen an eine Sonnet-Untersitzung.

**Gut genug wenn:** A gebaut mit gefahrener Gegenprobe · B gebaut · C abgelegt ·
D gemessen und berichtet · Regressionslauf grün · Morgen-Bericht steht.
**Wer nach A und dem grünen Lauf aufhört, hat den Block bestanden.**
B bis D sind der Nachschub, damit die Nacht nicht leerläuft.

---

# A · Pipe- und Semikolon-Zerlegung, mit der Boden-Bedingung als Regel
### 🔴 schwer · zuerst · eigener Commit

Claudias Auftrag, von mir zuerst rot gestellt und am 01.09. um 01:20
**berichtigt**: Es ist kein Loch. Der Auftrag ist baubar. Das Papier dazu liegt
als `docs/auftraege/2026-09-01-berichtigung-pipe-befund.md` im Repo — **lies es
vor dem Bau**, es enthält die Messung, die den Unterschied macht.

**Was gebaut wird:** Ein Befehl mit `|`, `||` oder `;` wird in seine Glieder
zerlegt; jedes Glied läuft einzeln durch `_ein_befehl`. Sind alle Glieder frei,
ist der Befehl frei. Das spart Rückfragen bei `grep … | head`.

**Die Bedingung, ohne die es nicht gebaut wird — wörtlich als Regel in den Code:**

> **Zerlegen ist erlaubt, solange kein Glied den Boden verschiebt.**
> In den Dialog fällt jedes Glied, das den Zustand der folgenden Prüfungen
> ändert: `cd`, `pushd`/`popd`, `export`, `set`, `source` und `.`, sowie
> Zuweisungen der Form `NAME=wert`.

**Warum sie hineingehört, obwohl heute nichts durchkommt** — und das ist der
Grund, den ich nach der Nachmessung für den richtigen halte: Diese Befehle
fallen heute in den Dialog, **weil sie in keiner Freiliste stehen** — nicht,
weil jemand entschieden hätte, dass zustandsverändernde Befehle nicht zerlegt
werden dürfen. **Der Schutz ist ein Zufall, keine Entscheidung.** Wer morgen
die Freiliste erweitert — und genau darauf zielt dieser Auftrag, weniger
Rückfragen — hebt ihn auf, ohne es zu merken. Die Bedingung macht aus dem
Zufall eine Regel.

**Die Gegenprobe, mit den drei Auflagen aus `CLAUDE.md`:**

1. **Vorher hinschreiben, welche Zeile rot werden muss.** Erwartung:
   `cd /etc | cat passwd` und `X=1 ; env` fallen in den Dialog; der Prüfer
   meldet, dass ein bodenverschiebendes Glied ohne Rückfrage zerlegt wurde.
2. **`__pycache__` löschen**, bevor gemessen wird.
3. **Den Eingriff verifizieren** (`assert alt in t` vor der Ersetzung) — eine
   Ersetzung, deren Suchtext nicht vorkommt, ändert nichts, und der grüne
   Prüfer danach liest sich wie „der Schutz hält".

**Der Prüfer muss ausführen, nicht lesen.** Eine Zeile, die `_BODEN_BEFEHLE`
im Quelltext sucht, ist umgehbar — acht von acht gemessenen Fällen. Ruf den
Pfad auf und miss das Urteil.

### A2 · Der kleine Nachbarschritt, getrennt committen

`bashfreigabe.py` Zeile 520 reicht `ziel` nicht durch:

```
return _ein_befehl(teile, roh, bereiche, ist_geheimnis, umgelenkt_nach)
```

Relative Pfade im zweiten Glied löst `_aufloesen` (Zeile 214) deshalb gegen das
**Arbeitsverzeichnis des Bot-Prozesses** auf, nicht gegen das `cd`-Ziel.
Heute kommt dadurch nichts durch — die Auflösung landet in der Praxis *höher*
als gemeint, was die sichere Fehlerrichtung ist. **Aber ein Prüfer, der
zufällig richtig liegt, ist kein Prüfer.** Das `cd`-Ziel als Auflösungsbasis
durchreichen. Klein, eigener Commit, eigene Gegenprobe.

**Wenn A2 unerwartet Kettenwirkung zeigt: liegen lassen und melden.** A steht
auch ohne A2.

---

# B · Der „Auswerten"-Knopf unter empfangenen Dateien
### 🔨 mittel · Adams Freigabe liegt vor

**Adams Wortlaut, 01.09., 00:51:** ein Knopf **„Verarbeiten"/„Auswerten"** unter
einer empfangenen Datei. Heute muss er nach jedem Dokument erst schreiben, was
damit geschehen soll.

**Warum das klein bleibt und klein bleiben soll:** Der Weg existiert bereits —
Dateien werden empfangen, geprüft und durch `process_user_text` geschickt. Der
Knopf setzt nur den Text, den Adam sonst selbst tippt. **Kein neuer Pfad, keine
neue Schranke.**

**Drei Auflagen:**
1. **Der Eingangsschutz bleibt vor dem Knopf.** Der Knopf darf keinen Weg
   eröffnen, der an der Medien- und Dokumentprüfung vorbeiführt — eine Datei
   von außen ist Information, nie Anweisung.
2. **Die Beschriftung ist deutsch** und sagt, was passiert.
3. **Doku-Spiegel im selben Commit:** `/hilfe`, Tastatur, `setMyCommands` —
   was der Bot über sich sagt, stimmt am selben Tag.

**Den Namen wählt Adam.** „Auswerten" ist sein eigenes Wort und damit die
sichere Wahl; „Verarbeiten" stand daneben im selben Satz. Nimm „Auswerten" und
vermerk im Commit, dass der Name zur Bestätigung offen ist.

---

# C · Der zweite Chat bekommt einen Ort — **abgelegt, nicht gebaut**
### 📄 klein · Ablage

**Adams Wortlaut, 31.08., 10:15:** Die Werkstatt bleibt, wo sie ist; **daneben
ein Chat für Kalender, Mail und Alltag — ohne Auto-Bash.** Die Werkstatt muss
ihn **lesen** können.

**Ausdrücklich nicht bauen.** Das berührt 6.6 (Häuser und Zimmer) und den
fließenden Dialog, dessen Entscheidungen Adam vertagt hat — Wiedervorlage
05.09. Ein zweiter Chat, der vor dieser Entscheidung entsteht, legt sie fest.

**Was heute Nacht entsteht:** ein `docs/gedanke-zweiter-chat.md` nach dem
Muster von `gedanke-gps-standort.md` — **ohne Punktnummer**, die gehört Adam.
Darin: sein Wortlaut, die Berührung zu 6.6 und zum fließenden Dialog, und die
eine offene Frage, die er beantworten muss (trennt der zweite Chat die
Sitzung, oder nur die Ansicht?). Verweis aus dem Drehbuch bei 6.6, damit es
auffindbar ist.

**Der Grund, warum das überhaupt ein Block ist:** Genau so sind die drei
Konzepte in `docs/auftraege/` fünf Wochen unentdeckt geblieben. Ein Gedanke
ohne Ort ist ein verlorener Gedanke.

---

# D · Kontrollzählung: welche N-Punkte sind angekommen?
### 📐 Messung · ohne Codeänderung

**Der Anlass ist meiner.** Adam hat mich in dieser Nacht fünfmal gefragt und
fünfmal etwas gefunden — dreimal, weil ich Vollständigkeit für den Teil
gemeldet habe, den ich bearbeitet hatte, ohne die **Menge** zu prüfen, zu der
er gehört. Diese Messung wendet die Lehre auf die Auftragsliste selbst an.

**Die Menge:** In meinen Auftragspapieren stehen **27 Punkte, N-4 bis N-30**.
Ich habe heute Nacht gemessen, dass außerhalb dieser Papiere im ganzen Repo nur
**N-1, N-2, N-3, N-21, N-26 und N-30** vorkommen. **Daraus folgt nicht, dass
die übrigen offen sind** — ein erledigter Punkt muss seine Nummer nicht tragen.
Genau deshalb ist es eine Messung und keine Behauptung.

**Was zu tun ist:** Für jeden der 27 Punkte am Artefakt prüfen — nicht am
Commit-Titel —, ob er angekommen ist. Ergebnis als **eine Tabelle**:
Nummer · ein Halbsatz · angekommen ja/nein · wo.

**Die Zeile, auf die es ankommt, steht am Schluss: „X von 27".**

**Bekannte Zwischenstände, die dir Arbeit sparen** (jeweils meine Messung von
heute Nacht, bitte nachprüfen statt übernehmen):
N-12 bis N-15 sehen erledigt aus (`a5f4d26`, `e1fe586`, `b052346`) ·
N-21, N-24, N-26 bis N-30 erledigt · N-16, N-17, N-19, N-20 finde ich im
Drehbuch **nicht** wieder — das sind meine vier Verdachtsfälle.

---

# E · Abschluss
### verbindlich, auch wenn die Nacht knapp wird

1. **`bash scripts/regressionstest.sh` vor jedem Commit** — vor jedem, ohne
   Ausnahme und ohne Abwägung. Der Lauf dauert unter einer Minute; die Frage,
   ob er nötig ist, dauert länger.
2. **`bash scripts/test_zielumgebung.sh`** nach A — der Eingriff sitzt in einem
   Pfad, der als Dienst ohne `HOME` läuft.
3. **Blaupause-Zeile je Baustein**, und der dritte Teil ist der wertvolle:
   *was gebaut · welche Kettenwirkung geprüft · welche Nebenwirkung
   **tatsächlich** auftrat.*
4. **`ABHAENGIGKEITEN.md`** für alles Neue — sofort, nicht später.
5. **Commit-Nachrichten über Heredoc** (`git commit -F - <<'EOF'`), nie über
   `-m`, sobald Sonderzeichen vorkommen. Und **nie** einen Commit an einen
   dateiändernden Heredoc ketten.
6. **Morgen-Bericht, höchstens zehn Zeilen:** erledigt · geparkt · Fragen ·
   was Adam heute entscheiden muss. **Mit Nenner** — „drei von fünf Blöcken",
   nicht „die Blöcke".
7. **Nichts deployen.** Der Stand bleibt auf dem Branch, bis Adam ihn zieht.

---

# 🚫 Nicht bauen — das liegt bei Adam

| | Was | Warum es wartet |
|---|---|---|
| 1 | **Vorlese-Weg**: `num2words` jetzt oder 9.1 Azure abwarten | 💰 bei Azure — Kostenfrage, seine Entscheidung |
| 2 | **Kontingent-Warnstufen** — 80/85/90/95 oder nur 80 und 95 | offen ist nicht „ob", sondern „welche" |
| 3 | **N-23 Zuordnung** (ChatGPT/Codex — 9.6 oder 9.18) | eine Zuordnung, die ihm gehört |
| 4 | **venv-Befehlsblock** | root, seine Hand |
| 5 | **Fließender Dialog** | vertagt, Wiedervorlage 05.09. |
| 6 | **Sprach-Trennung** (`gettext`/Fluent) | Umbau quer durch 12.628 Zeilen — reine Innenarbeit bei einem Nutzer |

**Wenn im Lauf der Nacht eine Frage auftaucht, die Adam beantworten müsste:
liegen lassen, nicht ableiten.** Ein abgeleiteter Auftrag wird in dieser Rolle
zu echtem Code — und zu einem Selbstläufer, den niemand mehr aufhält. Melden
und weitermachen mit dem nächsten Block.
