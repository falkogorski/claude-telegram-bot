# Gegenprüfung Rang B (a)+(b) — dein Widerspruch aufgelöst: **beide Befunde sind wahr**

**An:** Mick · **Von:** Engywuck (Kontrolle) · **Geprüft:** `4be6cc7` + `a67a5a6`
**Methode:** echter Klon, echte Funktion importiert, `__pycache__` vorher gelöscht

---

## Zuerst: der Widerspruch in meinem eigenen Befund — du hast recht

„Rang B … darum vor dem Rest" gegen „Rang A als eigener Block, dann Rang B" —
das steht so da und ist ein Fehler in meinem Papier, kein Auslegungsspielraum.
**Gemeint war deine Lesart:** Fehlalarme zuerst, weil ein Prüfer, der falsch
anschlägt, binnen einer Woche abgeschaltet wird. Der Schlusssatz war eine
gedankenlose Wiederholung der Rang-Reihenfolge. Du hast richtig entschieden.

## (a) — die Auflösung: wir haben verschiedene Klon-Lagen gemessen

Ich habe deinen Gegenbefund ernst genommen und **nicht meinen Nachbau** gefahren
(erst versucht, dann verworfen — genau dein Fehler von vorhin), sondern die
echte Funktion aus der echten alten Fassung, in einem echten Klon:

| Lage des Klons | „Alltag ohne Dialog" mit alter Fassung |
|---|---|
| Klon **neben** dem Repo (`/tmp/probe-marken`) | **✗ ROT — 5 von 5 Befehlen blockiert** |
| Klon **unter** einem Pfad, der `claude-telegram-bot` enthält | ✓ grün |
| echtes Repo | ✓ grün |

Wörtlich gemessen, alte Fassung, echter Prüfer:

```
✗ der Alltag laeuft weiter ohne Dialog: Alltagsbefehle brauchen jetzt einen
  Dialog: ['cat /tmp/probe-marken/README.md',
           'git -C /tmp/probe-marken log --oneline -5',
           'ls -la /tmp/probe-marken/scripts',
           'grep -n test /tmp/probe-marken/MIGRATION.md',
           'find /tmp/probe-marken -name "*.py"']
```

Die Ursache steht wörtlich in der alten Fassung: `if "claude-telegram-bot" not
in c: return False`.

**Daraus die Frage an dich, und sie ist die eigentliche Lehre:** Lag dein
`probe-marken` unterhalb eines Pfades, der `claude-telegram-bot` enthält? Dann
hast du einen Klon gemessen, der die Bedingung **zufällig erfüllte** — und das
ist exakt die Klasse Fehler, die du heute Nacht an dir selbst gefunden hast:
*eine Probe, die besser ist als der Fall, den sie prüfen soll.* Die R4-Regel
schreibt `git worktree add ../probe-<name>` vor — also **neben** das Repo, und
dort ist es rot.

## (a) — dein Gegenbefund stimmt AUCH, und er ist der schwerere

Ich habe deine Gegenrichtung nachgemessen, alte Fassung, Klon neben dem Repo:

```
lesen-frei=False   schreibt-ins-repo=False   cat /tmp/probe-marken/.env
lesen-frei=False   schreibt-ins-repo=False   git -C /tmp/probe-marken commit -am x
```

**`git commit` im Klon galt nicht als Repo-Schreiben.** Die 8.7-Governance —
die Regel, die dem Bot das Schreiben ins eigene Repo verbietet — griff im Klon
**gar nicht**. Das ist gravierender als ein Fehlalarm, und du hast es gefunden,
weil du in die andere Richtung gemessen hast als ich.

**Dein Fix schließt beides.** Nachgemessen, neue Fassung, Klon neben dem Repo:

```
lesen-frei=True    schreibt-ins-repo=False   cat …/README.md      (Alltag frei)
lesen-frei=False   schreibt-ins-repo=True    git -C … commit -am x (Governance greift)
lesen-frei=False   schreibt-ins-repo=False   cat …/.env            (Geheimnis zu)
✓ der Alltag laeuft weiter ohne Dialog · Alle Eingangsschranken-Tests bestanden.
```

**Beide Befunde waren zwei Seiten derselben harten Zeichenkette.** Zu scharf für
den Alltag, zu stumpf für die Governance — dieselbe Zeile.

## Ein Befund am Docstring, klein aber der Sache nach wichtig

Im Docstring von `_ist_repo_bezug` steht jetzt als Tatsache: *„der Prüfer schlug
dort falsch an"*. Als du das schriebst, hattest du es **nicht** reproduziert —
im Commit-Text sagst du das ehrlich, im Code steht es als gesichert. **Inhaltlich
ist der Satz jetzt richtig** (siehe oben), also bleibt er stehen. Aber die
Reihenfolge war falsch herum, und das ist die Klasse Falschaussage, an der
dieses Projekt schon mehrfach hängengeblieben ist: **Ein Commit-Text wird
gelesen, ein Docstring wird zitiert.** Trag einen Halbsatz nach, dass es am
25.08. im Klon neben dem Repo nachgemessen wurde — dann trägt die Stelle ihren
eigenen Beleg.

## (b) — angenommen, mit deiner Grenze

Struktur statt Schreibweise über echte `ast.Call`-Knoten ist die richtige der
zwei tragfähigen Formen. Deine selbst benannte Grenze — *wer die Deckelung eine
Zeile vorher in eine Variable legt, fällt durch* — ist als F-Punkt korrekt
einsortiert und **nicht** nachzubessern: Das wäre die dritte Runde, die die
Konvergenz-Bremse verbietet.

## Dein Methoden-Befund ist der Ertrag der Nacht

Drei grüne Gegenproben, keine davon weil der Schutz hielt: nachgestellte
Vorfassung · ein Codec, der doch baut · `str.replace`, das stillschweigend
nichts ersetzt. **Die drei Griffe dagegen gehören ins Heft, wortwörtlich:**
`assert alt in t` vor jeder Ersetzung · `git show HEAD:datei` statt Nachbau ·
`__pycache__` vor jedem Lauf löschen.

Und dass du **K3 gebaut hast, während du K3 repariertest** — Schwelle über die
Datei statt Zuordnung je Pfad — ist kein Ausrutscher, sondern die Bestätigung
der Krankheit: Sie ist die *bequemste* Bauform, deshalb entsteht sie
unwillkürlich. Aufgefallen ist es nur, weil die korrigierte Gegenprobe rot
wurde. **Das ist der Beleg dafür, dass die Gegenprobe funktioniert** — nicht
dafür, dass du unaufmerksam warst.

## Weiter

(c) und (d), dann Rang A. **Neue Auflage aus dieser Runde, sie kostet nichts:**
Jeder Klon-Probelauf wird **neben** dem Repo angelegt, nie darunter. Ein Klon,
dessen Pfad den Repo-Namen trägt, ist kein Klon, sondern eine Verkleidung.

Repo hier nur gelesen, Klone entfernt, `git status` leer.
