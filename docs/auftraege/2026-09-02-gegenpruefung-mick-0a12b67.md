> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren. **Ein** Nachtrag,
> klein, kein Sicherheitspfad. Alles andere ist bestanden.

# Gegenprüfung des Nachmittagsblocks — 25 von 25, ein Doku-Befund

**Stichtag:** 02.09.2026, 15:31 MESZ · **Von:** Engywuck (Kontrolle)
**Geprüft:** `0a12b67` — `bashfreigabe.py`, `scripts/postfach_ablegen.py`,
`scripts/mac/rechnungen_ablegen.sh`, `docs/befehlsbloecke-adam.md`,
`docs/boten-postfach.md`, CLAUDE.md-Abschnitt, F-19, 9.NN-S, 5.19,
ABHAENGIGKEITEN.md · **Geprüft auf Fable 5.1.**
**Nenner:** 8 Commits · 25 Prüffälle **ausgeführt** (nicht gelesen), 25 wie
erwartet · 1 Befund · 0 Sicherheitsbefunde.

**Ausgeführt, nicht gelesen** — eigener Prüfstand: `bashfreigabe.py` von
`0a12b67` in einem Wegwerf-Repo mit vier Bereichen, **Arbeitsverzeichnis
absichtlich nicht das Repo** (wie auf dem VPS: `cwd=WORKDIR`, bot.py
Z. 3996/4585). Geheimnis-Prüfung als Attrappe über die Marker-Liste — Rand,
nicht Mitte.

## Was hält — gemessen

| Fall | Urteil | Grund |
|---|---|---|
| `ls <ws> && wc -l <ws>/x` | frei | — |
| `cd <ws> && ls` · `cd <ws>&&ls` | frei | die Form bleibt |
| `ls <ws> && cd /etc && cat passwd` | dialog | Boden |
| `cd /etc && cat passwd` | dialog | Ziel außerhalb |
| `cd <ws> && cd /etc && cat /etc/passwd` | dialog | Boden |
| `ls <ws> \|\| cd /etc && cat passwd` | dialog | Boden |
| `cd <ws> && cat ../../../../etc/passwd` | dialog | außerhalb — **A2 trägt** |
| `python3 -c 'print(1)'` · `-m http.server` | dialog | Schalter — **ohne Geheimnis in der Nutzlast**, also aus dem richtigen Grund |
| `python3 /tmp/postfach_ablegen.py` | dialog | nicht unter scripts/ |
| `python3 <repo>/scripts/mac/postfach_ablegen.py` | dialog | nicht **direkt** unter scripts/ |
| `python3 <repo>/scripts/verweis.py` → Symlink nach /tmp | dialog | aufgelöst, nicht verglichen |
| `python3 <repo>/scripts/irgendwas.py` | dialog | nicht benannt |
| `… postfach_ablegen.py; cat <repo>/.env` | dialog | Geheimnis über den ganzen Befehl |
| `… postfach_ablegen.py --datei <repo>/.env` | **abweisen** | Geheimnis-Pfad |
| `bash <repo>/scripts/postfach_ablegen.py` | dialog | bash kein Deuter |
| `grep x … \| head` | frei, **art=grep** | U-4 |
| `cat $HOME/x` | dialog, **art=cat** | U-4: Art steht auch an der Vorprüfung |

**Route A** (`rechnungen_ablegen.sh`): kein `--delete` in beiden Hälften ·
jeder Lauf schreibt eine Zeile · `exit 78` mit Klartext bei fehlendem
iCloud-Elternordner und bei TCC · Hälfte 1 „übersprungen" ist als Normalfall
vor dem Umzug benannt, nicht als Alarm. **Trägt.** Deine Abweichung — kein
Zeitgeber für Hälfte 1 — ist richtig begründet: Ein Timer, der auf einen
Sitzungsstart wartet, beschleunigt nichts und wäre eine zweite still
ausfallende Stelle.

**Adams Befehlsblock:** `--ff-only`, Regressionslauf vor dem Neustart,
Rückweg `reset --hard 5d2590d`, typst ohne root, PATH-Falle benannt,
Vergleichslauf als Schritt 4 mit Abbruchkriterium. **Gut.**

---

# Der eine Befund: die Doku schreibt den Weg vor, der im Dialog landet

`docs/boten-postfach.md`, Z. 36–37, der neue vorgeschriebene Aufruf:

```
python3 scripts/postfach_ablegen.py --chat 304455165 --text "…"
```

**Relativer Pfad.** Der Bot startet Bash mit `cwd=WORKDIR` — auf dem VPS ist
das `/home/claudebot/workspace` (Sitzungskopf im Log: `Session · … ·
/home/claudebot/workspace`). `_aufloesen` löst ohne vorangehendes `cd` gegen
genau dieses Verzeichnis auf. Ergebnis, ausgeführt mit cwd ≠ Repo:

```
dialog  art=python3 | python3 scripts/postfach_ablegen.py --chat 1 --text x
                    | [postfach_ablegen.py] liegt nicht direkt unter scripts/
```

**Claudia kopiert diesen Aufruf aus der Doku — und bekommt den Dialog, den
das Skript abschaffen sollte.** Bei dir läuft es grün, weil dein
Arbeitsverzeichnis das Repo ist: *am Mac lief alles*, die Klasse vom 29.07.

**Beide Formen, die tragen, sind gemessen frei:**

```
python3 /home/claudebot/claude-telegram-bot/scripts/postfach_ablegen.py --chat … --text …
cd /home/claudebot/claude-telegram-bot && python3 scripts/postfach_ablegen.py --chat … --text …
```

## Was zu tun ist — klein

1. **`boten-postfach.md`:** den absoluten Pfad in die beiden Beispielzeilen.
   Die `cd`-Form als zweite Möglichkeit nennen. Ein Satz dazu, warum: *das
   Arbeitsverzeichnis der Sitzung ist nicht das Repo.*
2. **Eine Prüfzeile in `test_bashfreigabe.py`**, die den **dokumentierten**
   Aufruf mit `cwd` außerhalb des Repos misst — so, dass sie rot wird, wenn
   die Doku wieder einen relativen Pfad zeigt. Der Prüfer liest die Zeile aus
   der Doku, nicht aus dem Test; sonst prüft er die Schreibweise, nicht die
   Wirkung.
3. **Claudias Kurier-Abmachung** (`docs/kurier-abmachung.md`): falls dort
   ein Aufruf steht, derselbe Griff.

**Nicht tun:** `_aufloesen` gegen das Repo statt gegen cwd auflösen. Das wäre
eine Sicherheitsänderung (der Boden, auf dem alle Pfadprüfungen stehen), um
einen Doku-Fehler zu heilen. Die Doku ist die richtige Stelle.

---

# Was bei Adam liegt — unverändert, in einer Zeile

Der Deploy (seine Hand) · der iCloud-Zielordner (deine Frage) · zwei offene
Punktnummern. **Nichts davon hält U-1 bis U-6 auf.**

**Konvergenz-Bremse:** Das war die Gegenprüfung. Der Nachtrag ist die
Nachprüfung. **Danach ist Schluss** — was dann noch auffällt, geht in die
F-Liste.
