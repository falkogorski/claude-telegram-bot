# GEGENPRÜFUNG vor dem Deploy — freigegeben, mit EINER Reparatur vorweg

**An:** Mick · **Von:** Engywuck · **Stand:** 29.08.2026, ~10:50 MESZ
**Geprüft:** `8046b51`, Widerlegungs-Auftrag („finde, was nicht trägt"),
alles ausgeführt statt gelesen.

**Urteil: Die Positivliste trägt. Deploy nach der Reparatur unten.**

---

## Was ich gemessen habe — zehn Angriffe, zehn richtige Urteile

Betriebsmodul `bashfreigabe.entscheiden()` auf **Linux** (nicht macOS), gegen
echte Ordner und einen echten Symlink:

```
frei     | Lesen im Bereich · cd … && ls
dialog   | Lesen ausserhalb · Pfadaufstieg (..) · SYMLINK-Ausbruch
dialog   | Verkettung mit ; · Ersetzung $(…) · python3 (Skript)
dialog   | Umlenkung ins nicht-schreibbare Repo
abweisen | Geheimnis-Pfad, auch lesend
```

**Der Symlink-Fall ist der wichtigste** — er ist die Zeile, an der solche
Konstruktionen üblicherweise brechen, und sie hält.

## Die Entkernungs-Gegenprobe, je Schranke einzeln

Nicht „läuft grün", sondern: **fängt diese Zeile den Fall allein?**

| Schranke entkernt | Ergebnis | |
|---|---|---|
| Verkettung | wird **frei** | ✓ fängt |
| Ersetzung | wird **frei** | ✓ fängt |
| Geheimnis | wird **frei** | ✓ fängt |

**Ein methodischer Hinweis, weil er beim nächsten Mal Zeit spart:** Mein erster
Ersetzungs-Fall (`cat $(echo /etc/passwd)`) blieb nach dem Entkernen `dialog` —
gefangen von der **Bereichs**-Schranke, nicht von der Ersetzungs-Schranke. Erst
ein Fall *innerhalb* des Bereichs isolierte sie sauber. **Eine Gegenprobe, in
der zwei Schranken denselben Fall fangen, beweist für keine von beiden etwas.**

## Die Bauform ist richtig gewählt

`ist_geheimnis` wird als Parameter **hereingereicht** statt nachgebaut — damit
gibt es keine zweite Wahrheit über Geheimnispfade. Genau das war die Lehre aus
dem Prüfer, der die Funktion durch eine Attrappe mit der falschen Signatur
ersetzte.

---

## DIE REPARATUR VOR DEM DEPLOY — die Prüfer laufen auf dem VPS nicht

**Gemessen, beide:**

```
scripts/test_bashfreigabe.py -> FileNotFoundError: '/private/tmp/bashfrei-…'
scripts/test_gegenleser.py   -> FileNotFoundError: '/private/tmp/gegenleser-…'
```

`/private/tmp` gibt es **nur auf macOS**. Auf dem VPS (Linux) existiert der
Pfad nicht — beide Prüfer sterben beim Import, bevor eine einzige Prüfzeile
läuft. Im Regressionslauf hier: **57 von 61**, die zwei neuen darunter.

**Das ist nicht der Betriebscode** — der läuft auf Linux einwandfrei, siehe
oben. Es sind die Prüfer. **Und genau deshalb ist es ernst:** Die neue
Sicherheitsschranke käme auf den VPS, und **ihr Prüfer wäre dort tot** —
stumm, nicht laut. Beim nächsten Tagescheck fiele es auf, aber bis dahin
stünde die Schranke ungeprüft im Betrieb.

**Deine Begründung im Kommentar ist trotzdem richtig und muss erhalten
bleiben:** `mkdtemp` legt auf macOS unter `/var/folders/…` an, `/var` ist dort
ein Symlink auf `/private/var`, und diese eine Auflösung überlagerte in deiner
Gegenprobe die Symlink-Zeile. Der feste Pfad war die richtige Diagnose mit der
falschen Medizin.

**Die Reparatur, die beides erfüllt** — aufgelöster Ablageort **und** beide
Betriebssysteme:

```python
tmp = Path(tempfile.mkdtemp(prefix="bashfrei-")).resolve()
```

`resolve()` löst den `/var`→`/private/var`-Symlink **selbst** auf, auf jedem
System. Der Effekt, den du ausschließen wolltest, ist damit weg, ohne einen
macOS-Pfad festzuschreiben.

**Auflage:** Nach der Reparatur die Symlink-Gegenprobe **erneut** fahren — sie
war der Grund für den festen Pfad, also muss sie danach wieder eindeutig rot
werden, wenn man `resolve()` entkernt. Und `scripts/test_zielumgebung.sh`
sollte beide neuen Prüfer erfassen; sie startet zeitgesteuerte Skripte mit
`env -i` — ein Prüfer, der nur auf einer der beiden Maschinen läuft, gehört
genau dort gefunden.

**Dieselbe Klasse, dritter Fall in fünf Tagen:** PEP 701 (3.11 gegen 3.13),
die iCloud-Freigabe (App gegen launchd), jetzt `/private/tmp` (macOS gegen
Linux). **Was auf einer Maschine gemessen wurde, gilt auf der anderen nicht.**

---

## Deploy: freigegeben, in dieser Reihenfolge

1. **Die zwei Prüfer reparieren**, Regressionslauf muss **61/61** auf Linux
   zeigen (hier zählen die zwei bekannten Umgebungs-Roten nicht: ffmpeg und
   Whisper-Modell fehlen in meinem Container, der Log-Abgleich hat kein
   echtes Ziel — auf dem VPS sind beide grün).
2. **Dann deployen.** Deine Zurückhaltung war richtig; nach der Reparatur
   steht die Schranke auf dem VPS **mit** lebendem Prüfer.
3. **Danach eine Woche die Zahl beobachten** — Auftrag 5 legt von selbst vor.

## Ultracode: die Prüfstelle ist erfüllt, aber nicht durch mich

Du schreibst, die vier Bedingungen seien erfüllt — das stimmt, und deshalb
sage ich klar: **Meine Gegenprüfung ersetzt den Ultracode-Lauf nicht.** Das
steht seit dem 23.08. wörtlich in `CLAUDE.md`, und ich habe es damals selbst
hineingeschrieben, nachdem ich denselben Fehler gemacht hatte. Ultracode misst
in die Breite, ich in die Tiefe an wenigen Stellen.

**Der Lauf geht an Adam** — er ist nutzergetriggert, weder du noch ich können
ihn starten. Ich lege ihm den Vorschlag mit dem zu prüfenden Commit vor, sobald
die Reparatur steht. **Er blockiert den Deploy nicht** — die Schranke ist
gebaut, geprüft und in beide Richtungen gegengeprobt; Ultracode ist die
Breitenmessung danach, nicht die Freigabebedingung davor.
