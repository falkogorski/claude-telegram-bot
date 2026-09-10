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
ssh claudebot 'cd ~/claude-telegram-bot && git pull --ff-only && bash scripts/regressionstest.sh 2>&1 | tail -4'
```

**Prüfzeile — und sie sieht anders aus als am Mac:**

```
== Ergebnis: 72/73 bestanden ==
== 1 uebersprungen — auf DIESER Maschine wurde dort nichts gemessen ==
```

**Das ist der Normalfall auf dem Server, kein Fehler.** Die Heartbeat-Wache
lässt sich bei laufendem Bot nicht scharf messen und meldet sich deshalb als
übersprungen. Erst ein `❌` oder eine kleinere Zahl ist ein Befund — dann die
Ausgabe schicken.

**Ein Neustart ist diesmal nicht nötig.** Nachgemessen (`git diff --stat`
gegen deinen Neustart-Stand): **`bot.py` ist unverändert.** Geändert haben sich
nur der Log-Abgleich, der Tagescheck, das Ablege-Skript und
`postfach_ablegen.py` — Skripte, die bei ihrem nächsten Lauf frisch gelesen
werden. Ein Neustart schadet nicht, bricht aber Claudia mitten im Zug ab, falls
sie gerade arbeitet.

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

### A2.1 — Die Dateien aus dem aktuellen Stand nehmen

**Der Filter (mit A1 ausgespielt) verhindert neuen Zulauf — er löscht nichts.**
Der Abgleich läuft ohne `--delete`; was einmal drin ist, bleibt drin, bis es
jemand entfernt. Genau das ist dieser Schritt.

✅ **Dass er wirkt, ist bereits gemessen** (04.09., 21:50, erster Lauf nach
deinem Pull): Die Quittung auf dem Server ist frisch und trägt die Zeile
*„rechnungen/ — ganzer Zweig zurueckgehalten"*. Vorher stand dort noch der
Stand vom 03.09.

⚠️ **Hier stand vorher eine Prüfzeile, die dich hätte hängen lassen:** *„Nach
dem Abgleich muss der Ordner weg sein."* Das wird er nicht — die Reihenfolge
ist Filter, dann Entfernen, dann prüfen, dass er **nicht zurückkommt**. Der
Filter allein bewirkt nichts Sichtbares.

```bash
ssh claudebot 'cd ~/logsync/claude-bot-logs && git rm -r --cached -q ausarbeitungen/rechnungen && rm -rf ausarbeitungen/rechnungen && git commit -q -m "Rechnungszweig entfernt (Befund 4)" && git push -q origin main && echo ENTFERNT'
```

**Prüfzeile:** `ENTFERNT`. Danach ist die Datei aus dem *aktuellen* Stand
weg — **aus der Historie noch nicht.** Dafür ist A2.3 da.

### A2.2 — Messen, dass der Zweig nicht zurückkommt

**Das ist die eigentliche Prüfung des Filters.** Der Abgleich läuft **alle fünf
Minuten** (an den Commit-Zeiten gemessen, nicht stündlich). Also einen Lauf
abwarten, dann:

```bash
ssh claudebot 'ls ~/logsync/claude-bot-logs/ausarbeitungen/rechnungen 2>&1 | head -2; echo "--- Quittung ---"; grep "ganzer Zweig" ~/workspace/letzter-abgleich.txt'
```

**Prüfzeile:** *No such file or directory* — **und** darunter die Zeile
*„rechnungen/ — ganzer Zweig zurueckgehalten"*. Beide gehören zusammen: Die
erste zeigt, dass er weg ist; die zweite, dass er **sichtbar** zurückgehalten
wird und nicht lautlos verschwindet.

⚠️ Kommt der Ordner zurück, ist der Filter nicht wirksam — **dann aufhören und
Bescheid sagen**, nicht weitermachen: Das Umschreiben der Historie wäre
umsonst, weil der nächste Abgleich die Datei erneut hineinträgt.

✅ **Erledigt und gemessen** (04.09., 21:55, erster Abgleich nach deinem
`git rm`): Der Ordner ist weg und bleibt weg, die Quittung nennt
*„rechnungen/ — ganzer Zweig zurueckgehalten: Bank und Steuernummer"*.

### A2.3 — Den Zeitgeber anhalten

**Das braucht root, also deine Hand.** Ohne diesen Schritt schiebt der
Abgleich mitten in das Umschreiben hinein.

```bash
ssh claudevps 'systemctl stop claude-log-sync.timer && systemctl is-active claude-log-sync.timer'
```

**Prüfzeile:** `inactive`. **Kommt stattdessen eine Fehlermeldung**, heißt der
Zeitgeber anders — der Name steht im Register, aber nirgends im Code, also ist
er von hier nicht prüfbar. Dann hilft:

```bash
ssh claudevps 'systemctl list-timers --all | grep -i log'
```

### A2.4 — Die Historie umschreiben (Mac)

`git-filter-repo` fehlt hier noch. Es ist quelloffen und **kostenfrei**
(💰: keine Kostenquelle):

```bash
brew install git-filter-repo
```

Dann auf einem **frischen** Klon — `filter-repo` verlangt das und hat recht
damit, ein umgeschriebener Klon lässt sich nicht mehr sauber weiterverwenden:

```bash
ADR=$(git -C ~/Projects/claude-bot-logs remote get-url origin) && cd /tmp && rm -rf logs-clean && git clone "$ADR" logs-clean && cd logs-clean && git filter-repo --path ausarbeitungen/rechnungen/ --invert-paths && git remote add origin "$ADR" && git push --force origin main && echo UMGESCHRIEBEN
```

**Die Adresse wird aus deinem vorhandenen Klon übernommen, nicht hier
eingetippt** — so gilt genau der Zugangsweg, der bei dir schon funktioniert
(SSH oder HTTPS), und du wirst nicht mitten im Ablauf nach Anmeldedaten
gefragt.

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

**Prüfzeile:** beide Meldungen.

✅ **Erledigt und gemessen** (04.09., 22:0x): Beide Klone stehen auf `4b2387b9`.
Im Repo sind **null** Commits und **null** Objekte, die den Rechnungszweig
tragen; die `Rechnung 012-26.pdf` ist auch über die Objektliste nicht mehr
auffindbar.

**Es gibt einen dritten, und er hat sich selbst gemeldet:** Engywucks
Kontrollsitzung hält eine Lesekopie des Log-Repos. Sie pusht nie und zieht sich
nach dem Umschreiben selbst nach — er sagt Bescheid, wenn es geschehen ist.
**Kennst du einen vierten** — auf einem anderen Rechner, in einem alten
Ordner —, sag es, bevor A2.6 läuft: Ein Klon mit alter Historie, der einmal
pusht, macht die ganze Arbeit rückgängig.

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

## Schritt A3 — Die Spesen-Regel auf den Server nachziehen

Du hast am 04.09. die steuerliche Staffel bestätigt. Sie steht jetzt als
**Regel 5a** in `RECHNUNGSREGELN.md`, und die Kürzel-Tabelle im `README.md`
nennt endlich auch `Spesen:voll`. Beides liegt bisher **nur am Mac** — der
Server hat die Fassung vom 03.09.

Dazu kommen die Sätze, der Generator und das Aufstellungs-Template. Drei
Änderungen stecken darin: Der Generator **rechnet die Spesen jetzt selbst**
(`Spesen:30` statt eines von Hand eingetippten Betrags), die Aufstellung kann
endlich die **Bemerkungszeile** tragen, die Regel 6 seit dem 03.09. verlangt
(*„LKW-Sätze wie für dieses Projekt besprochen"*), und `ablage.py` bekommt den
elften Pfadfall aus Befund 3.

```bash
cd ~/Projects/rechnungen && rsync -azR RECHNUNGSREGELN.md README.md daten/saetze.json scripts/ablage.py scripts/generate_aufstellung.py templates/aufstellung.typ claudebot:~/workspace/rechnungen/ && echo FERTIG
```

⚠️ **Das `&& echo FERTIG` ist nicht Zierde:** `rsync` schweigt bei Erfolg, und
ein stiller Befehl sieht aus wie ein hängender. Genau so ist es am 04.09.
passiert — der Lauf war längst durch, es sah nur nicht so aus. **Jeder Befehl
in diesem Block endet auf eine Meldung**, dieser hatte sie als einziger nicht.

⚠️ **Das `-R` ist nicht Kosmetik, sondern der Unterschied zwischen wirkt und
wirkt nicht** (Engywucks Fund an meiner ersten Fassung): Ohne `-R` legt rsync
bei mehreren Quellen nur die **Basisnamen** ins Ziel — `saetze.json` läge dann
flach unter `~/workspace/rechnungen/`, während der Generator `daten/saetze.json`
liest. **Das berichtigte Etikett wäre nie angekommen, ohne dass etwas
fehlschlägt.**

⚠️ **`saetze.json` geht mit, `rechnungsnummern.json` nicht** — sie liegen im
selben Ordner, aber der Zähler gehört dem Server.

**Zwei Prüfzeilen, und jede misst die Sache statt der Schreibweise:**

```bash
ssh claudebot 'grep -c "BERICHTIGT 04.09.2026" ~/workspace/rechnungen/daten/saetze.json'
```

**Prüfzeile:** `1`. *(Engywuck hatte hier `grep -c "Abreisetag-Satz"`
vorgeschlagen — nachgemessen liefert das in **beiden** Fassungen `1`, weil der
alte Wortlaut im neuen Hinweis zitiert steht. Die Zeile hätte nichts gemessen.)*

```bash
ssh claudebot 'cd ~/workspace/rechnungen && .venv/bin/python -c "import sys;sys.path.insert(0,\"scripts\");import ablage;print(\"ABGEWIESEN\" if ablage._saeubern(\"L\"+chr(39)+\"Osteria/Bar\") is None else \"DURCHGELASSEN\")"'
```

*(Der Apostroph entsteht im Python als `chr(39)` — er kommt in der Befehlszeile
gar nicht vor. Sonst wäre die Prüfzeile selbst an dem Zeichen zerbrochen, das
sie misst.)*

⚠️ **`.venv/bin/python`, nicht `python3`** — auf dem Server liegt `openpyxl`
in der venv des Projekts, nicht im System-Python. Meine erste Fassung rief
`python3` und meldete `ModuleNotFoundError`; das sah nach einer fehlenden
Umgebung aus, war aber der falsche Aufruf. **Die venv ist da und vollständig.**

✅ **A3 ist erledigt und gemessen** (04.09., 22:0x): Etikett berichtigt,
`saetze.json` liegt in `daten/` (nicht flach), die Formel rechnet auf dem
Server 30/80/50/100 % zu 8,40 · 22,40 · 14,00 · 28,00, die Bemerkungszeile
steht im Template, Fall elf weist `L'Osteria/Bar` ab — und der berichtigte
Akzent ist auch dort (`3 Extrastunden à 40 €`).

**Prüfzeile:** `ABGEWIESEN`, davor eine `HINWEIS:`-Zeile. Das ist Fall elf —
die Server-Hälfte von Befund 3. **Kommt `DURCHGELASSEN`**, ist nur die
Mac-Seite angekommen; dann fängt der Apostroph zwar niemanden mehr, aber die
zweite Schicht fehlt — sag Bescheid.

Kommt bei einer der Zeilen ein `ModuleNotFoundError: openpyxl`, fehlt dort die
venv — eine eigene Sache und kein Grund weiterzumachen.

⚠️ **Bewusst nur diese zwei Dateien, kein Voll-Abgleich.** Seit dem 03.09.
ist der Server die Stelle für Rechnungsnummern; ein `rsync` des ganzen
Ordners würde `daten/rechnungsnummern.json` mit dem Mac-Stand überschreiben
und irgendwann eine Nummer doppelt vergeben.

**Die Spesen-Frage hast du am 04.09. entschieden** — *8,40 gilt, wie in
017-26.* Die Regel trägt jetzt die Rechenformel statt einer Kürzelliste, und
das falsche Etikett in `saetze.json` ist berichtigt.

### Und eine Sorge, die sich beim Nachmessen aufgelöst hat

Engywuck fragte, ob der **Server-Zähler** die Nummer 017-26 kennt — kennt er
sie nicht, vergäbe Claudia sie ein zweites Mal (Regel 8). **Nachgesehen:
Mac und Server sind identisch, beide führen die `17`.** Nichts zu tun.

Seine vorgeschlagene Prüfzeile (`grep -c "017-26"`) hätte **null** geliefert
und einen Fehlalarm ausgelöst: Der Zähler speichert die nackte Zahl, nicht die
Nummer als Text. Wer nachsehen will, sieht die Liste an:

```bash
ssh claudebot 'cat ~/workspace/rechnungen/daten/rechnungsnummern.json'
```

**Prüfzeile:** unter `"26"` steht die `17`.

---

# Teil B · 02.09.2026 — erledigt am 03.09.

> **Ausgeführt und abgeschlossen.** Deploy, Umzug, `typst` und der
> Vergleichslauf sind durch; das Rechnungsprojekt liegt auf dem Server. Der
> Abschnitt bleibt als **Verlauf** stehen — Zwischenschritte werden archiviert,
> nicht geglättet.
>
> **Berichtigt am 04.09.:** Hier stand, der Server habe *„die Rechnung 017-26
> dort erzeugt"*. **Er hat sie nicht.** 017-26 entstand auf dem Mac und lag
> fertig in iCloud, bevor das Projekt um 00:59 auf den Server ging; der
> Vergleichslauf dort erzeugte 012-26. Gemessen im Log-Repo: keine einzige
> Datei mit `017-26` hat es je erreicht, wohl aber die 012-26. **Ein Verlauf
> darf alt sein, aber nicht falsch.**

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

---

# 09.09.2026, 19:20 — Deploy Block 1 (Stand `23d01d6`)

**Warum jetzt:** Engywucks Nachprüfung ist da. Der Kern von Block 1 ist
abgenommen; der Deploy ist heute **verhaltensneutral** (dein Chat ist privat,
`message_thread_id` ist überall leer — jeder Weg landet im Hauptfaden wie
bisher). Was er **bringt**: die Postfach-Drossel meldet ihren Stau sofort ·
die Rechnungsskripte laufen ohne Dialog · die Dialogzahl wird zum ersten Mal
gemessen · das Kontingent-Ereignis steht im Protokoll · das PDF-Skript ·
`_Regeln` eine Ebene höher.

**`bot.py` ist geändert → diesmal mit Neustart.**

## Schritt 1 — Stand ziehen und prüfen

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 23d01d6 && bash scripts/regressionstest.sh 2>&1 | tail -5'
```

**Warum hier `merge --ff-only 23d01d6` statt `git pull` steht:** Ich baue
parallel an Block 1b weiter. Der feste Stand holt genau das Geprüfte und
nichts, was danach entsteht.

**Prüfzeile:** Der Lauf endet ohne `❌`. Engywuck erwartet `74/75 bestanden`
mit einer übersprungenen Zeile (Heartbeat-Wache) — das ist seine Messung, nicht
meine; ich habe keinen Serverzugriff. Kommt eine kleinere Zahl oder ein `❌`:
**nicht neu starten**, Ausgabe schicken.

## Schritt 2 — Neustart

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

**Prüfzeile:** `active`.

## Schritt 3 — die eine Zeile, die wirklich neu ist

Schreib dem Bot eine normale Nachricht, die einen Werkzeuglauf auslöst (etwa:
*„lies mir die letzten drei Zeilen aus dem Tagescheck-Protokoll vor"*).

**Worauf es ankommt:** Er antwortet. Damit läuft der Nachsteuer-Hook zum
**ersten Mal durch das SDK** — mein Prüfstand ruft ihn direkt auf, das ist
nicht dasselbe. Danach:

```bash
ssh claudebot 'tail -20 ~/claude-telegram-bot/logs/bot.err.log'
```

**Prüfzeile:** keine Hook-Fehlerzeile.

## Rückweg — `[BERICHTIGT 09.09.2026, 19:45 nach Engywucks Nachtrag]`

Hier stand `git revert f3d1b58` auf dem Server. **Das ist ein Fehlpfad, und er
schlägt erst nach dem Eingriff zu:** Ein Revert ist ein Commit, und der
VPS-Klon hat nach 8.7 bewusst **keine git-Identity und einen pre-commit-Blocker**
(MIGRATION.md, 23.07., „live getestet, Exit 1"). Git wendet die Änderung an,
kann sie nicht abschließen und lässt den Klon im Zustand *Revert nicht
abgeschlossen* zurück — der nächste `merge --ff-only` verweigert dann. Dazu
war die Beschreibung falsch: `f3d1b58` trägt **Limit je Person UND den Hook**,
ein Revert nähme beides.

**Der Grundsatz, damit die nächste Vorlage ihn nicht wieder erfindet:**

> **Rückwege für den VPS-Klon sind `reset --hard` auf einen ABGELESENEN Stand
> oder ein Push vom Mac. Nie ein Befehl, der dort einen Commit erzeugt.**

Also vor jedem Deploy den laufenden Stand **ablesen und notieren**:

```bash
ssh claudebot 'git -C ~/claude-telegram-bot log -1 --format="%h %ad %s" --date=format:"%d.%m. %H:%M"'
```

und im Notfall:

```bash
ssh claudebot 'git -C ~/claude-telegram-bot reset --hard <HASH-VON-VORHER>'
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

Ein Rückweg „nur ein Teil" existiert allein über den Mac: dort revertieren,
pushen, Adam zieht mit `--ff-only`.

## Und die Prüfzeile hängt am Rückgabewert, nicht an einer Zahl

`| tail -5` verschluckt den Rückgabewert und kann ein `❌` weiter oben
verdecken. Künftig:

```bash
ssh claudebot 'cd ~/claude-telegram-bot && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**`rc=0`** (alles grün) oder **`rc=77`** (grün mit Übersprungenem) sind gut,
jede andere Zahl nicht. Die Zahl `74/75` hängt an der Maschine: im Container
fehlt ffmpeg, auf dem VPS läuft der Bot — beide Male eine übersprungene Zeile,
aber aus verschiedenen Gründen.

---

# 09.09.2026, 21:11 — Deploy Block 1b (Stand `b30a460`)

Engywuck hat abgenommen. **Schritt 3 ist diesmal der Beweis, der seit dem
Deploy von `23d01d6` offen steht** — der Hook durch das SDK, in beide
Richtungen. Ich baue parallel an Block 2; sollte Schritt 3 rot sein, wird der
Hook in 1b repariert, nicht Block 2 zurückgedreht.

## Schritt 0 — den laufenden Stand ablesen und notieren

```bash
ssh claudebot 'git -C ~/claude-telegram-bot log -1 --format="%h %ad %s" --date=format:"%d.%m. %H:%M"'
```

Das ist der Rückweg. Erwartet: `23d01d6`.

## Schritt 1 — ziehen und prüfen

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 6f9aefe && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`. Alles andere: nicht neu starten, `/tmp/reg.log`
schicken.

## Schritt 2 — Neustart

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Schritt 3 — der Hook-Beweis (Engywucks Wortlaut)

**Erst ein Auftrag mit mehreren Werkzeugschritten:**

> Lies nacheinander die letzten drei Dateien in `docs/auftraege` und fasse jede
> in einem Satz zusammen.

**Sofort danach, während er arbeitet, eine zweite Nachricht:**

> Und nenne bei jeder auch das Datum aus dem Dateinamen.

**Die Quittung auf die zweite Nachricht muss lauten:** „📨 Notiert — ich reiche
es dem laufenden Vorgang gleich hinein, ohne ihn zu stoppen."

Danach:

```bash
ssh claudebot 'grep -h "Nachsteuern" ~/claude-telegram-bot/logs/bot.err.log | tail -5'
```

**Prüfzeile — zwei Zeilen:**

```
Nachsteuern: N Zeichen an den laufenden Auftrag gereicht (Zimmer haupt)
Nachsteuern: Auftrag <id> uebersprungen — als Zettel bereits …
```

Und im Chat **genau eine** Antwort, die die Daten nennt. Zwei Antworten, oder
eine ohne Daten, oder keine „uebersprungen"-Zeile → an Engywuck, nicht neu
deployen.

**Eine Grenze, die kein Fehler ist** (Engywuck hat sie benannt): „Hineingereicht"
heißt nicht „berücksichtigt". Kommt der Nachtrag erst beim letzten
Werkzeugschritt an, streift die Antwort ihn nur. Das ist der Preis des
fließenden Dialogs.

**Rückweg:** `reset --hard` auf den Hash aus Schritt 0, dann Neustart.

---

# 09.09.2026, 23:15 — Deploy Block 2 (Leitstand), Stand `590b7e8`

Engywuck hat Block 2 abgenommen; seine zwei Befunde sind **vor** dem Deploy
behoben (`/zimmer` ohne Markdown, Zettel im Protokoll). Schritte 0 bis 2 wie
gehabt:

```bash
ssh claudebot 'git -C ~/claude-telegram-bot log -1 --format="%h %ad %s" --date=format:"%d.%m. %H:%M"'
```

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 590b7e8 && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`. Erwartet: `75/76` mit einer übersprungenen
(Heartbeat).

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Schritt 3 — die Prüfzeile, die den behobenen Fehler misst

**Erst einen Auftrag mit einem Unterstrich im Text starten:**

> Lies `scripts/test_zimmer_block1.py` und sag mir in zwei Sätzen, was der
> Prüfer misst.

**Während er arbeitet, in denselben Chat:**

```
/zimmer
```

**Prüfzeile:** Es kommt eine Antwort, und sie nennt den Auftrag **mitsamt
Dateinamen**. Genau hier brach die erste Fassung: Telegram lehnte die Nachricht
wegen des einzelnen Unterstrichs ab, und der Leitstand schwieg — ausgerechnet
während gearbeitet wurde.

**Danach**, wenn der Auftrag durch ist:

```bash
ssh claudebot 'ls -la ~/claude-telegram-bot/logs/conversations/ | tail -5'
```

Im Privatchat bleibt es bei der einen Tagesdatei — Zimmer-Dateien entstehen
erst mit Themen. Der Blick lohnt trotzdem: Er zeigt, dass am Namen des
Hauptprotokolls nichts geändert wurde.

**`[NACHGETRAGEN 10.09.2026, 01:05]` Live ist `211b383`, nicht `590b7e8`.**
Der Block oben nennt den Stand, der beim Schreiben galt; deployt wurde am Ende
`211b383` (B2-3, die Schlusszeile). Vorher-Stand abgelesen: `590b7e8` ·
`rc=77`, 75/76 · Neustart `active` um 00:56 · `/zimmer` hat live geantwortet,
während ein Auftrag lief.

**Eine Prüfzeile ist damit noch NICHT scharf gefahren:** Der Auftragstext im
Test war `ssh claudevps 'systemctl restart …'` — darin steht **kein
Unterstrich**. Genau der war der Befund B2-2. Im Prüfstand ist der Fall
gemessen (mit `test_zimmer_block1.py` als Auftragstext), im Betrieb noch nicht.
Der Nachtest kostet eine halbe Minute:

> Lies `scripts/test_zimmer_block1.py` und sag mir in zwei Sätzen, was der
> Prüfer misst.

und währenddessen `/zimmer`. Kommt die Übersicht mit dem Dateinamen darin,
ist der Fall auch im Betrieb belegt.

---

# 10.09.2026, 01:45 — Deploy Freigabeweg-Fix (Stand `30fca43`)

**Dringlich, weil der Freigabeweg für Schreibwerkzeuge seit 19:26 tot ist:**
Jeder Dialog für Edit oder Write endet in einer Verweigerung, egal was du
drückst. Ursache war eine Zeile aus M-3 (meine), die in der falschen Klammer
saß.

## Schritt 0 — Stand ablesen, Hash notieren

```bash
ssh claudebot 'git -C ~/claude-telegram-bot log -1 --format="%h %ad %s" --date=format:"%d.%m. %H:%M"'
```

Erwartet: `211b383`. Das ist der Rückweg.

## Schritt 1 — ziehen, pyflakes einspielen, prüfen

**Neu in diesem Deploy: `pyflakes`.** Reines Python von PyPI, kostenfrei,
keine Laufzeit-Abhängigkeit — es läuft nur im Regressionstest. Ohne die
Installation bleibt die neue Prüfzeile dauerhaft „übersprungen", also stumm.

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 30fca43 && .venv/bin/pip install -q pyflakes && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`. In der Ausgabe müssen die zwei neuen Zeilen
stehen: „Keine undefinierten Namen" und „Freigabeweg (Genehmigen=erlaubt)".

## Schritt 2 — Neustart

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Schritt 3 — die Prüfzeile, die beide offenen Punkte zugleich schließt

Claudia hält ihren Register-Eintrag bereit. Bitte sie, ihn zu schreiben — sie
braucht dafür ein Schreibwerkzeug, also kommt der Dialog:

> Schreib jetzt bitte deinen Register-Eintrag.

**Erwartet:** Du bekommst die Genehmigungs-Anfrage, drückst „Genehmigen",
**und die Datei ist danach wirklich geändert.** Genau das ging seit 19:26
nicht. Laut Claudia folgen drei Genehmigungen nacheinander (Text, PDF, Ablage
im Ausgang).

Danach ist auch die Dialog-Messung wieder belegbar:

```bash
ssh claudebot 'cd ~/claude-telegram-bot && .venv/bin/python scripts/bash_dialog_auswertung.py 2>&1 | tail -12'
```

**Und der offene Nachtest von gestern gleich mit** (Befund B2-2, `/zimmer` mit
einem Unterstrich im Auftragstext):

> Lies `scripts/test_zimmer_block1.py` und sag mir in zwei Sätzen, was der
> Prüfer misst.

und währenddessen `/zimmer` — die Übersicht muss kommen und den Dateinamen
nennen.

**Rückweg:** `reset --hard` auf den Hash aus Schritt 0, dann Neustart.

---

# Deploy Block 3 „Empfang" — **erst nach Engywucks Ultracode-Lauf**

**Stand:** 10.09.2026, 11:57 · **Zielstand:** `8436945` · **Server läuft
heute auf `33d7cdf`** — dazwischen liegen Block 3, der Haushalt, der Bericht
und die Prüfer-Namen.

**Nicht vorziehen.** Engywuck startet `/code-review ultra` auf `d87dc64`;
der Deploy kommt danach, so abgesprochen. Der Block steht hier fertig, damit
er nicht erst geschrieben werden muss, wenn es soweit ist.

## Schritt 0 — den jetzigen Stand ABLESEN (das ist der Rückweg)

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git rev-parse --short HEAD'
```

## Schritt 1 — holen und prüfen

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 8436945 && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`, und in der Ausgabe steht die neue Zeile
„Empfang / Sekretaerin (Block 3)".

## Schritt 2 — Neustart

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Schritt 3 — der Nachtest, und er hat **zwei** Hälften

Der Empfang steht nach dem Deploy auf **aus** — es ändert sich also zunächst
nichts. Einschalten:

> `/empfang an`

**Erwartet:** eine Liste mit Haken und Kreuzen, was sie kann und was nicht.
`/status` nennt den Empfang jetzt in der Übersicht.

Dann eine Nachricht im **Hauptchat**, die Arbeit bedeutet:

> Lies bitte MIGRATION.md und sag mir, was bei 5.1 als Nächstes offen ist.

**Hälfte (a):** Binnen Sekunden kommt eine Antwort mit **👩‍💼** davor — nicht
das Ergebnis, sondern die Sekretärin, die sagt, dass sie es weitergibt.

**Hälfte (b), und die ist die eigentliche Prüfzeile:** Der Auftrag muss danach
**wirklich im Zimmer stehen**. Gleich danach:

> `/zimmer`

Dort muss der Auftrag auftauchen. **Kommt (a) ohne (b)**, ist die Ursache
genau die eine Frage, die ich am Mac nicht messen konnte: ob die Oberfläche
der Sekretärin ihr einziges Werkzeug überhaupt anbietet (die Anmeldung am Mac
war abgelaufen). Dann bitte melden — der Fix wäre klein, aber er muss gemessen
werden, nicht geraten.

**Wieder ausschalten**, wenn du normal weiterarbeiten willst:

> `/empfang aus`

**Rückweg:** `reset --hard` auf den Hash aus Schritt 0, dann Neustart.

---

# Die Karteileiche in der Startnachricht (offen seit gestern)

Der Bot begrüßt mit „Letzter Task — Stand 2026-07-23 Nacht". Die Datei liegt
auf dem VPS unter `~/.claude/memory/last-task.md` und wird bei jedem Start
gelesen. **Sie zu löschen wäre der schlechtere Weg** — dann käme eine
generische Meldung. Besser überschreiben:

```bash
ssh claudebot 'cat > ~/.claude/memory/last-task.md <<EOF
# Letzter Task

Zimmer-Umbau: eine Sitzung je Thema, Leitstand, und der Empfang mit der
Sekretaerin. Bloecke 1, 1b und 2 laufen; Block 3 ist gebaut und wartet auf
die Pruefung. Der Empfang steht auf aus, bis du ihn mit /empfang an
einschaltest.
EOF
echo geschrieben'
```

**Prüfzeile:** Beim nächsten Neustart nennt die Startnachricht diesen Stand
statt des Julis.

**Warum du das ausführst und nicht ich:** Server-Eingriffe löst du aus — auch
die kleinen, auch außerhalb des Repos.


---

# Deploy A-4 — der Haushalt, der ohne den Knopf läuft

**Stand:** 10.09.2026, 13:56 · **Zielstand:** `606ce26` · **Server läuft auf
`9801c64`** · **Dringlichkeit: heute** — vier Punkte aus A-4 wirken seit dem
letzten Deploy im Betrieb, der auffälligste lässt Adams Gesprächsfaden nach
dreißig Minuten Stille verschwinden.

## Schritt 0 — **erst sehen, was mitkommt** `[NEU 10.09., Engywuck]`

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git log --oneline HEAD..606ce26'
```

**Prüfzeile: Es dürfen NUR die Commits dieses Blocks dastehen.** Steht etwas
darunter, das nicht dazugehört, wird **nicht gezogen** — ein `--ff-only`-Merge
bringt die ganze Kette mit, nicht nur den genannten Stand. Genau so ist Block 3
am 10.09. mit einem Hotfix live gegangen.

**Erwartet hier: genau EINE Zeile**, `606ce26`. Gemessen mit
`git log --oneline 9801c64..606ce26`. `[BERICHTIGT 10.09., 14:40]` Hier
stand, es kämen zwei Commits — falsch: `62f153d` liegt **nach**
`606ce26`, nicht davor. Die Prüfzeile selbst hat den Fehler gefangen,
beim ersten Gebrauch.

Und den jetzigen Stand ablesen, das ist der Rückweg:

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git rev-parse --short HEAD'
```

## Schritt 1 — holen und prüfen

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git merge --ff-only 606ce26 && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

**Prüfzeile:** `rc=0` oder `rc=77`.

## Schritt 2 — Neustart

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

## Schritt 3 — die Prüfzeile, und sie braucht Geduld

Schreib etwas im **Hauptchat**, lass den Chat **über eine halbe Stunde** ruhen,
schreib dann wieder. **Der Faden muss noch da sein** — keine Antwort, die bei
null beginnt. Ein **Zimmer** darf in derselben Zeit einschlafen; dort kommt
dann eine 💤-Zeile, die es ankündigt.

**Rückweg:** `reset --hard` auf den Hash aus Schritt 0, dann Neustart.
