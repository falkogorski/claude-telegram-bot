<!-- ROLLE: befund-maschinen-gleichstand-vollstaendig -->
# Der Fächer ist durch — und es sind nicht 39 Fälle, es sind drei

**Stichtag:** 30.08.2026, 03:29 · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Engywuck (Kontrolle) · **Geprüfter Stand:** `df5dc69`
**Verfahren:** 77 Agenten, 0 Ausfälle. Jede Meldung einzeln beurteilt **und**
adversarisch gegengeprüft. Vollständige Fassung: `ANHANG-faecher-39-funde.md`.

---

## Die Zahlen — und warum die erste Fassung nicht getragen hätte

| | |
|---|---|
| beurteilt | 72 |
| **besteht noch** | **39** — davon **33 still** |
| vom Widerleger gekippt | **22** |
| behoben seit der Meldung | 4 |
| nie real | 6 |
| nicht prüfbar | 1 |

**Der Widerleger kippt 37 %.** Das ist die wichtigste Zahl des Laufs, wichtiger
als die 39.

Der erste Anlauf riss das Kontingent und ließ **22 Funde ohne Widerleger**
stehen. Ich habe damals hochgerechnet: *„darin stecken grob acht, die nicht
tragen."* Nachgeholt waren es **sieben**. Die Kipprate der Nachzügler (35 %)
war praktisch identisch mit der der ersten Runde (38 %).

**Das ist der Beleg dafür, dass die Warnung keine Vorsicht war, sondern eine
Messung:** Ohne die Nacharbeit stünden hier 46 Funde, von denen sieben nicht
tragen — und niemand wüsste welche.

**Die strukturelle Lehre, zweimal hintereinander dieselbe:** In beiden Läufen
starb die **Gegenprüfungs**-Stufe, nie die Finder-Stufe. Sie steht hinten, also
wird sie geopfert. Und sie ist genau die Stufe, die den Unterschied zwischen
Befund und Erzählung macht. **Beim nächsten Fächer gehört die Reihenfolge
umgedreht: lieber acht Funde vollständig gegengeprüft als vierzig halb.**

---

## Es ist EINE Klasse, nicht neununddreißig

**Sechs der Funde sagen dasselbe: Ein Prüfer meldet grün, ohne gemessen zu
haben.** Das ist wörtlich die Fehlerform, die dieses Projekt heute schon
zweimal an anderer Stelle gefunden hat — die leere Menge in `differenz.py`,
der Vergleich gegen nichts im Node-Skript.

| Fund | Der grüne Prüfer, der nichts gemessen hat |
|---|---|
| **[26]** `bot.py:8038/8046` | **Der C2-Pin-Wächter selbst.** `if not pins: return` und `except Exception: continue` → grüne Zeile ohne jede Messung. Ausgeführt gemessen: sowohl bei entferntem Pin als auch bei einem Pin auf ein nicht installiertes Paket |
| **[58]** `test_media_h1.py` | endet mit **Exit 0** und schreibt `✅ Medien-Transport H1`, obwohl **alle zwölf Prüfzeilen ungeprüft blieben** (ffmpeg fehlt) |
| **[71]** `test_log_sync_quittung.py` | wertet **weder `returncode` noch `stderr`** aus. Fehlt `rsync`, bleibt der Prüfer grün |
| **[47] [62]** `test_zielumgebung.sh` | ein **angesagter Übersprung** geht über `melde ok` als **bestanden** in die Bilanz. Der Selbstwiderspruch steht drei Zeilen darüber im eigenen Kommentar |
| **[70]** `regressionstest.sh` | fester Pfad `/tmp/regress_last.log`: bei zwei Nutzern führt bash die Umlenkung **vor** dem Befehl aus — der Prüfer läuft gar nicht |

**Ein Griff deckt alle sechs:** *Übersprungen ist nicht bestanden, und ein
Prüfer, der nichts gemessen hat, meldet rot.* Das ist eine gemeinsame Bauform,
kein sechsfacher Einzelfix.

### Klasse zwei — die Menge ist zu eng (sechster Fall dieser Regel)

**[19] [64] [33]** `test_zielumgebung.sh` sieht in **allen drei** Schleifen nur
`scripts/*.sh` — nicht rekursiv, nicht die Repo-Wurzel. **Draußen liegen sieben
Skripte mit `set -u`**, darunter `guardian.sh` (vier bare `$HOME`) und **alle
drei `.claude/hooks/*.sh`**.

Das ist bitter: Der Prüfer, der genau gegen den 29.07.-Fehler gebaut wurde
(`$HOME` in einem Dienst ohne HOME, ein Wächter einundzwanzig Tage tot), sieht
ausgerechnet die Hooks nicht. Und der zeilenweise Filter `grep -v ':-'` wirft
`${VAR:-$HOME/x}` weg — das bricht unter `set -u` genauso wie ein bares `$HOME`.

### Klasse drei — Leser und Schreiber kennen verschiedene Orte

Das ist Adams Gleichstands-Regel im Kleinen, und sie schlägt **innerhalb einer
Maschine** zu:

- **[20] [35]** `bot.py:4021` rechnet fest aus `Path.home()`, `stundenblume.py:66`
  respektiert `BLUMEN_DIR`. Ausgeführt gemessen: bei gesetztem `BLUMEN_DIR` und
  **lückenloser, sekundenfrischer Kette** meldet der Bot *„noch keine Glieder
  (läuft der Zeitgeber?)"*
- **[39]** `_USAGE_FILE` ist der einzige Pfad ohne Umgebungsschlüssel, während
  **alle unmittelbaren Nachbarn einen haben**
- **[36]** `botenpost.ziel_finden()` liest die Vorlieben fest über `Path.home()`

### Und die vierte Schicht der Governance

**[32] [41] [60] [61]** `guard-master-files.sh`: Der Dateipfad kommt aus einem
`python3`-Einzeiler mit `2>/dev/null`. Fällt python3 aus — kaputter Shim,
dyld-Fehler, gedriftetes Eingabe-Schema, kaputtes JSON —, liefert der Hook
**exit 0 und leere Ausgabe: exakt wie beim legitimen Durchlassen.** Nicht
unterscheidbar. Es gibt in der ganzen Historie (zwei Fassungen) keinen
fail-closed-Zweig.

**[12]** dazu passend in `bot.py:3029`: Der Edit/Write-Zweig prüft eine feste,
schreibweisenempfindliche Teilzeichenkette `/claude-telegram-bot`, der
Bash-Zweig zwei Zeilen tiefer geht über `_REPO_MARKEN`. Dieselbe Frage, zwei
Wahrheiten — die G1-Lehre.

---

## Was ich EMPFEHLE — und ausdrücklich, was nicht

**Nicht 39 Aufträge.** Der Kurs-Blick von gestern hat 51 % Innenarbeit gemessen;
39 Einzelaufträge würden diesen Wert verdoppeln. Das wäre genau die Bewegung,
gegen die die Regel steht.

**Drei Sammelaufträge — sie decken 15 der 39 Funde:**

1. **„Übersprungen ist nicht bestanden."** Eine gemeinsame Bauform für alle
   Prüfer: Wer nichts gemessen hat, meldet rot. Deckt [26] [58] [71] [47] [62]
   [70]. **Das ist der wichtigste, weil er die Klasse trifft, die uns heute
   dreimal begegnet ist.**
2. **Die Mengen von `test_zielumgebung.sh` weiten** — rekursiv, Repo-Wurzel
   und `.claude/hooks/` eingeschlossen, und `${VAR:-$HOME}` nicht mehr
   wegfiltern. Deckt [19] [64] [33].
3. **`guard-master-files.sh` fail-closed.** Auswertung misslungen → blockieren.
   Deckt [32] [41] [60] [61].

**Alles Übrige geht auf die F-Liste**, nicht in einen Auftrag. Begründet:
Die Doku-Funde ([28] [29] [53] [57] [24] [54]) kosten nichts, solange sie
niemand zitiert; die Pfad-Funde ([20] [35] [39] [36]) treffen nur Läufe mit
gesetzten Umgebungsschlüsseln, also heute niemanden im Betrieb; die drei
kosmetischen sind Textdefekte.

**Zwei Ausnahmen von der F-Liste, weil sie nichts kosten:**
**[12]** ist eine Zeile (die feste Teilzeichenkette durch `_ist_repo_bezug`
ersetzen) und schließt eine Governance-Asymmetrie. Und **[20]/[35]** verdient
eine Zeile im Register, weil der Bot heute unter einer bestimmten Konfiguration
*„läuft der Zeitgeber?"* meldet, während der Zeitgeber läuft — eine
Falschauskunft an Adam, und genau die Sorte, die Vertrauen kostet.
