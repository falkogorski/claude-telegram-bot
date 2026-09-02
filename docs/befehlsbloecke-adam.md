<!-- ROLLE: befehlsbloecke-adam -->
> **Zweck: ANSICHT** · **Zu tun:** die Blöcke der Reihe nach ausführen — sie
> brauchen deine Hand, nicht root.

# 2026-09-02 · Deploy und Rechnungsumzug — ein Zug, vier Schritte

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 02.09.2026 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> Alles hier ist **gebaut, geprüft und committet, aber nicht ausgeführt.**
> Server-Eingriffe löst Adam aus (8.7) — das ist keine Förmlichkeit: Der Bot
> darf sein eigenes Repo nie anfassen, sonst laufen Repo-Stand und laufender
> Code auseinander.
>
> Die Shell ist `zsh` — **keine `#`-Kommentarzeilen** in die Blöcke einfügen,
> zsh führt sie als Befehl aus. Erklärungen stehen deshalb außerhalb.
>
> **Zusammen etwa zehn Minuten**, der Umzug macht den größten Teil davon aus.
> Nach jedem Schritt steht eine Prüfzeile. Stimmt sie nicht: **aufhören und
> Bescheid sagen** — der Rückweg steht jeweils darunter.

---

## Warum der Deploy heute der wichtigste einzelne Handgriff ist

**Alles, was du heute verlangt hast, ist gebaut. Nichts davon läuft.** Der VPS
steht auf dem Stand vom 29.08.; seither sind die Genehmigungs-Umschaltung, die
Bash-Zerlegung, die curl-Sperre und alles von heute dazugekommen. Deine Frage
*„Ich habe gerade keinen richtigen Durchblick mehr von dem, was alles gebaut
wird"* hat genau diesen Grund — und sie beantwortet sich mit Schritt 1, nicht
mit einer Erklärung.

**Es ist die Lehre vom 29.07. zum zweiten Mal:** Damals lag ein fertiger Fix
ungedeployt, und die Wache, die es hätte melden können, sah den Branch nicht.

**`requirements.txt` ist seit dem 29.08. unverändert** — kein pip-Schritt, kein
venv-Block. Der Deploy ist `git pull` und Neustart.

### ⚠️ Seit heute Nachmittag ist ein Sicherheits-Fix dabei

Beim Aufräumen gefunden und am selben Tag behoben (**F-20**): Ein Befehl mit
einem freistehenden `&` umging die **gesamte** Positivliste.

```
ls & curl boese.example   →  lief FREI, ohne Rückfrage
ls & rm -rf x             →  lief FREI, ohne Rückfrage
```

Der Grund: Die Prüfung sah nur das erste Verb (`ls`, erlaubt) und übersprang
den Rest, weil dort kein Schrägstrich stand — **die Shell führte trotzdem
beides aus.** Das galt in **jedem** Modus, auch im Genehmigen-Zustand, und es
war **vorbestehend**, nicht neu: gegen den Stand vom 29.08. gemessen, dort
ebenso offen. **Auf dem laufenden Server ist diese Lücke also gerade offen.**

Kein Hinweis darauf, dass sie je genutzt wurde — der Angriffsweg wäre ein
Dokument oder eine Webseite, die die Sitzung liest. **Das ist der Grund, warum
der Deploy heute nicht bis morgen warten sollte.**

---

## Schritt 1 — Deploy

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git pull --ff-only && bash scripts/regressionstest.sh 2>&1 | tail -5'
```

**Prüfzeile:** Am Ende muss `== Ergebnis: 70/70 bestanden ==` stehen. Steht dort
eine kleinere Zahl oder ein `❌`: **nicht neu starten**, sondern die Ausgabe
schicken. Ein roter Lauf auf dem Server ist genau der Fall, für den er da ist.

Danach der Neustart:

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

**Prüfzeile:** `active`. Danach schreib dem Bot irgendetwas — er soll antworten.

**Rückweg**, falls etwas hakt: `git -C ~/claude-telegram-bot reset --hard 5d2590d`
auf dem Server, dann Neustart. Das ist der Stand vom 29.08., der heute läuft.

**Was du nach dem Deploy sofort siehst:** Auf der Haupttastatur liegt ein neuer
Knopf **„🔐 Genehmigen ✓ → Auto"**. Er schaltet den Auto-Zustand ein, in dem
Lese- und Bauaufträge ohne Rückfrage laufen — Websuche, Schreibrechte,
Geheimnisse und der Weg nach außen bleiben im Dialog. **Der Zustand bleibt über
Neustarts erhalten**, und derselbe Knopf schaltet zurück.

---

## Schritt 2 — Das Rechnungsprojekt zieht auf den Server

**Nichts wird nachgebaut, das Bestehende zieht um.** Vom Mac aus, damit du
nichts kopieren musst:

```bash
rsync -az --exclude '.venv' --exclude '__pycache__' --exclude 'output' ~/Projects/rechnungen/ claudebot:~/workspace/rechnungen/
```

**Warum `~/workspace/` und nicht `~/rechnungen/`:** Es gibt auf dem Server genau
vier Bereiche, in denen Befehle ohne Rückfrage laufen. `~/rechnungen` liegt in
keinem — jeder Generator-Aufruf dorthin fiele in den Dialog, also genau die
Rückfragen, die du heute abgestellt haben willst. `~/workspace` ist schreibbar.
**Kein neuer Bereich, keine Codeänderung.**

`.venv` und `output` bleiben absichtlich hier: Die virtuelle Umgebung ist an den
Mac gebunden (65 MB), und `output` ist Erzeugtes, kein Quellmaterial.

**Prüfzeile:**

```bash
ssh claudebot 'ls ~/workspace/rechnungen/ ~/workspace/rechnungen/daten/ | head -30'
```

Es müssen `scripts/`, `templates/`, `daten/`, `assets/` da sein und in `daten/`
unter anderem `stammdaten.json`, `saetze.json`, `rechnungsnummern.json`.

**Die Stammdaten sind ab dem Deploy geschützt:** `stammdaten` steht seit heute
in der Geheimnis-Liste. Wer die Datei in einem Befehl **nennt** (`cat`, `grep`),
bekommt eine Rückfrage; der Generator nennt sie nicht und läuft durch — er liest
sie selbst. Der Riegel kommt **vor** dem Umzug, nicht danach.

---

## Schritt 3 — `typst` auf den Server, ohne root

`typst` steht bereits in der Positivliste; es fehlt nur auf dem Server. Es ist
eine einzelne statische Binärdatei, quelloffen, **kostenfrei**, wenige
Megabyte.

```bash
ssh claudebot 'mkdir -p ~/.local/bin && cd /tmp && curl -fsSL https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz -o typst.tar.xz && tar -xf typst.tar.xz && mv typst-x86_64-unknown-linux-musl/typst ~/.local/bin/ && rm -rf typst.tar.xz typst-x86_64-unknown-linux-musl && ~/.local/bin/typst --version'
```

**Prüfzeile:** eine Versionsnummer, etwa `typst 0.x.y`.

**Nach `~/.local/bin`, nicht `/usr/local/bin`** — kein root nötig.

**Und die Falle, die geprüft gehört, nicht angenommen:** Der Bot läuft als
systemd-Dienst. Enthält dessen `PATH` das Verzeichnis nicht, sagt die
Positivliste ja und die Shell *command not found*. Das ist die Klasse *am Mac
lief alles* vom 29.07.

```bash
ssh claudevps 'systemctl show claude-telegram-bot -p Environment | grep -o "PATH=[^ ]*" || echo "kein PATH gesetzt -- erbt den Standard"'
```

Steht `~/.local/bin` bzw. `/home/claudebot/.local/bin` **nicht** darin: sag
Bescheid. Dann trage ich den absoluten Pfad in den Generator ein — das ist eine
Zeile und braucht keinen Dienst-Eingriff.

---

## Schritt 4 — Der Vergleichslauf, und er ist der wichtigste

**Ohne ihn weiß niemand, ob die Schriften auf dem Server dasselbe Bild
ergeben** — das ist Claudias Satz und der wichtigste in ihrem Papier.

Erzeuge eine **bestehende** Rechnung auf dem Server neu und halte sie gegen die
Mac-Fassung:

```bash
ssh claudebot 'cd ~/workspace/rechnungen && mkdir -p output ausgang && python3 scripts/generate_rechnung.py daten/rechnung_012-26.json && ls -la output/'
```

Dann herunterholen und ansehen:

```bash
rsync -az claudebot:~/workspace/rechnungen/output/ ~/Downloads/rechnung-servertest/ && open ~/Downloads/rechnung-servertest/
```

**Prüfzeile:** Die PDF sieht aus wie die vom Mac — Logo, Unterschrift,
Schriftbild, Beträge. **Weicht das Schriftbild ab, hör hier auf:** Dann fehlen
auf dem Server Schriften, und das ist eine eigene Sache, keine Kleinigkeit.

**Danach aufräumen — Claudias Provisorium darf keine zweite Wahrheit werden:**

```bash
ssh claudebot 'ls ~/rechnungen-uebergang 2>/dev/null && echo "^ das kann weg, wenn der Vergleichslauf stimmt"'
```

Löschen erst nach deinem Blick darauf, und erst wenn Schritt 4 stimmt.

---

## Was danach läuft, ohne dass du etwas tust

Sobald fertige Rechnungen in `~/workspace/rechnungen/ausgang/` liegen, holt
`scripts/mac/rechnungen_ablegen.sh` sie **beim nächsten Sitzungsstart** ab und
legt sie in iCloud ab.

**Ehrlich zur Geschwindigkeit:** Das geschieht beim Sitzungsstart oder auf
Zuruf — **nicht** Minuten nach dem Erzeugen. Für eine Rechnung, die am selben
Tag rausgeht, reicht das; ein nächtlicher Lauf ohne Sitzung legt nichts ab.
**Genau deshalb hast du „später B" gesagt, und das bleibt richtig.**

**Eine Frage, die ich nicht raten wollte:** Der Zielordner in iCloud ist
zunächst `Business/Deko/DEKO-Service/_Aus-dem-Server` — ein **Übergabeordner**,
kein Ablageort. Es gibt in iCloud keinen Rechnungsordner, sondern deine
gewachsene Kundenstruktur, und der Generator kennt kein Einsortier-Schema. Ich
stelle deshalb zu und sortiere nicht ein. **Sag mir, wohin die Dateien
sollen** — dann trage ich es fest ein.
