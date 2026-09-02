> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren.
> Adams Freigaben liegen vor („Sofort!", 10:47 · „Dringend, dringend, dringend", 10:38).
> **Zwei Dinge liegen bei Adam selbst und stehen am Schluss: der Deploy und die Route.**

# Umbauauftrag — die Freigabedialoge und die Rechnungen auf dem Server

**Stichtag:** 02.09.2026, 14:21 MESZ · **Von:** Engywuck (Kontrolle)
**Gemessen an:** Branch `395de2b` · VPS `5d2590d` (29.08., laut Drehbuch Z. 727) ·
Claudias Log und vier Papiere von heute · **Geprüft auf Fable 5.1** (Adams
Umschaltung 14:1x), nicht auf der Grundeinstellung Opus 5.
**Nenner:** 6 Adam-Aussagen im Wortlaut · 4 Claudia-Papiere gelesen, 1 nicht
(die Rechnung selbst — Adams Geschäftsdaten, für den Umbau nicht nötig) ·
5 Blöcke · 2 davon am Sicherheitspfad.

**Block:** Nachmittag, zwei Stunden. **Modell:** Opus 5, mittlere Denktiefe;
U-2 und U-3 die Denktiefe hoch.

**Gut genug wenn:** U-1 beantwortet · U-2 gebaut mit bestandenem Vergleichslauf ·
U-3 gebaut mit gefahrener Gegenprobe · Lauf grün. **U-4 und U-5 sind Nachschub.**

---

## Der Befund, der alles andere ordnet

**Alles, was Adam heute verlangt hat, ist gebaut. Nichts davon läuft.**

| Adams Forderung heute | Gebaut | Commit | Auf dem VPS |
|---|---|---|---|
| „dass die Dinger durchlaufen … Lese-, Bauaufträge frei, Websuchen mit Freigabe" | **Genehmigungs-Umschalter 5.27** — Auto-Zustand, bleibt über Neustart erhalten, Knopf auf der Haupttastatur, Websuche bleibt Dialog | `ae03f95`, 01.09. 01:41 | **nein** |
| Claudias 100 Verkettungs-Dialoge | **Zerlegung an `\|`, `;`, `\|\|`** mit Boden-Bedingung | `395de2b`-Nacht, 02.09. 00:29 | **nein** |
| „dass klar ist, dass die Sachen von mir kommen" | curl-Sperre + Signatur-Punkt (heute früh) | 01.09. / Auftrag von 10:06 | nein / Ablage |

**Der VPS steht 102 Commits hinter dem Branch, 39 davon Code.** Claudia hat
heute um 10:30 gegen die *laufende* Positivliste gemessen — das ist der Stand
vom 29.08. Ihre 82 Prozent sind richtig für das, was läuft, und sagen nichts
über das, was existiert. Adams Satz *„Ich habe gerade keinen richtigen
Durchblick mehr von dem, was alles gebaut wird"* hat genau diesen Grund.

**Das ist die Lehre vom 29.07. zum zweiten Mal:** Ein fertiger Fix lag
ungedeployt, und die Wache, die es hätte melden können, sah den Branch nicht.
`requirements.txt` ist seit dem 29.08. unverändert — **kein pip-Schritt, kein
venv-Block**, der Deploy ist `git pull` und Neustart. **Das ist Adams Hand,
nicht deine** (8.7). Die Befehle stehen in seinem Teil am Schluss.

---

# U-1 · Vor dem Deploy: zwei Zahlen, die ich von dir brauche
### zehn Minuten · kein Bau

1. **Zielumgebung 39/41** stand in deinem Morgenbericht. **Welche zwei sind
   rot, und sind es Zeilen, die nur auf dem VPS grün sein können?** Wenn ja:
   eine Zeile im Bericht genügt. Wenn nein: vor dem Deploy beheben.
2. **Der Regressionslauf auf `HEAD`** — 70/70 stand da; bitte einmal frisch,
   damit Adam nicht gegen einen Stand deployt, der drei Commits alt ist.

**Warum ich frage statt selbst zu messen:** Ich habe keinen VPS-Zugang, und ein
Deploy auf eine ungeprüfte Spitze ist genau die Klasse, die am 23.08. zwei
rote Zeilen auf dem Server hinterließ.

---

# U-2 · 🔴 Rechnungen: das Mac-Projekt zieht auf den Server
### schwer · zuerst nach U-1 · **Erlösbezug — der erste seit sechs Wochen**

**Adams Wortlaut, 10:38:** *„Ja, unbedingt gehört das auf den Server und es muss
auch eine Möglichkeit geben, dass du eine Freigabe für diese iCloud-Ordner
erhältst, weil ich möchte das nicht händisch machen. Also das bitte als
Bauauftrag sofort umzusetzen. … Ich muss die Rechnung rausbekommen, das ist
wichtig und dringend."*

**Und 10:55:** *„Ich kann dir natürlich jetzt die Rechnung schicken, damit du
die selbst neu konstruierst, aber das möchte ich ausdrücklich nicht. Ich
möchte, dass das auf der Basis der Daten geschieht, die es schon gibt."*

**Grundlage:** Claudias `2026-09-02_bauauftrag-rechnungen-auf-den-server.md`,
dritte Fassung 11:22, im Log-Repo. **Ihr Auftrag 1 ist baubar und geprüft.
Ich ändere drei Dinge, jedes gemessen:**

### Was aus ihrem Auftrag 1 unverändert gilt

- **Nichts wird nachgebaut, das Bestehende zieht um:** `~/Projects/rechnungen`
  vom Mac — `scripts/generate_rechnung.py`, `scripts/generate_aufstellung.py`,
  `templates/rechnung.typ`, `daten/stammdaten.json`, `daten/saetze.json`,
  Logo, Unterschrift. **rsync über SSH vom Mac aus**, Adam kopiert nichts.
- **Vergleichslauf mit bekanntem Ergebnis:** eine bestehende Rechnung auf dem
  Server neu erzeugen und gegen die Mac-Fassung halten. **Ohne diesen
  Vergleich weiß niemand, ob die Schriften dasselbe Bild ergeben** — Claudias
  Satz, und er ist der wichtigste in ihrem Papier.
- **Ihr Provisorium `~/rechnungen-uebergang` wird nach dem Vergleichslauf
  gelöscht.** Es hat einen Tag getragen und darf keine zweite Wahrheit werden.
- **Rechnungsnummern:** Der Generator muss die vergebenen Nummern sehen. Das
  hängt an der Ablage (U-2-Route, bei Adam) — bis dahin **Rückfrage vor jeder
  Vergabe**, wie 5.19 es ohnehin verlangt.

### Änderung ① — der Zielpfad: `~/workspace/rechnungen`, nicht `~/rechnungen`

Claudia schlägt `/home/claudebot/rechnungen` vor. **Gemessen in
`bashfreigabe.py`, `bereiche_aus_umgebung`:** Es gibt genau vier Bereiche —
`repo` (nicht schreibbar), `workspace`, `postfach` (schreibbar), `logsync`
(nicht schreibbar). **`~/rechnungen` liegt in keinem.** Jeder Bash-Befehl
dorthin fiele im Genehmigen-Zustand in den Dialog — der Generator würde also
genau die Rückfragen erzeugen, die Adam heute abgestellt haben will.

**`~/workspace/rechnungen` liegt im schreibbaren Bereich. Kein neuer Bereich,
keine Codeänderung, keine neue Zeile in einer Sicherheitsliste.** Das ist die
Regel *löst es sich von selbst* — vor dem Nachbessern prüfen, ob es ohne
Nachbessern geht. Hier geht es.

### Änderung ② — Stammdaten: ein Marker, sonst nichts

Claudia: *„chmod 600, Ordner dem Geheimnis-Riegel bekannt machen, nicht in
Git, nicht über das Postfach versendbar."* **Richtig, und so geht es konkret:**
`_GEHEIMNIS_MARKER` (`bot.py` Z. 2463) kennt `token`, `secret`, `_key`,
`.env`, `credentials` — **nicht** `stammdaten`. Ohne Eintrag ist die Datei
mit Steuernummer und Bankverbindung für `cat` frei und über das Postfach
versendbar.

- **Eintrag `"stammdaten"` in `_GEHEIMNIS_MARKER`.** Wirkung, gemessen an der
  Funktion: `cat …/stammdaten.json` → Dialog (auch lesend, weil
  `_GEHEIMNIS_MARKER` beim Lesen gilt); Postfach-Versand → `failed/`.
  **`python3 scripts/generate_rechnung.py` nennt die Datei nicht im Befehl
  und läuft durch** — der Generator liest sie selbst. Das ist der Zuschnitt,
  den Claudia meint, und er trägt.
- **Prüfzeile dazu, ausführend:** `_is_sensitive_ref("cat x/stammdaten.json",
  schreibend=False)` ist wahr; `_is_sensitive_ref("python3 generate_rechnung.py",
  schreibend=False)` ist falsch. Gegenprobe: Marker entfernen, erste Zeile rot.

### Änderung ③ — `typst` ohne root

`typst` steht bereits in `ERZEUGEN` (`bashfreigabe.py` Z. 156) — die
Positivliste kennt das Verb. **Auf dem Server ist es nicht installiert**
(Claudia, 10:30). Es ist eine einzelne statische Binärdatei.

- **Nach `~/.local/bin` des Nutzers `claudebot`, nicht nach `/usr/local/bin`.**
  Kein root, keine Adam-Hand.
- **Die eine Falle dabei:** Der Bot läuft als systemd-Dienst. **Prüfen, ob
  dessen `PATH` `~/.local/bin` enthält** — sonst sagt die Positivliste ja und
  die Shell *command not found*. Wenn nicht: absoluter Pfad im Generator.
  Das ist genau die Klasse *am Mac lief alles* vom 29.07.

**Kein Kostenpunkt:** typst ist quelloffen und kostenlos. Speicher: einstellige
Megabyte.

### Was NICHT in U-2 gehört

**Die Ablage (Claudias Auftrag 2, Route A/B/C) — Adams Entscheidung, steht
offen.** Er hat sie heute nicht getroffen; seine Nachrichten nach ihrer Frage
beantworten sie nicht. **Baue nichts davon.** Meine Empfehlung an ihn ist
Route A (Abgleich über den Mac, keine Apple-Zugangsdaten auf dem Server);
Route B ist rot und bliebe es auch mit meiner Stimme. Steht am Schluss bei ihm.

**5.19 bekommt den Status:** *🔄 Projekt auf dem Server, Ablage offen (Route
bei Adam).* Und den Grundsatz aus U-5 A1.

---

# U-3 · Die Postfach-Ablage als benanntes Skript
### mittel · Sicherheitspfad · Gegenprobe

**Claudias Messung von heute, die 27 Ersetzungs-Dialoge:** *„praktisch alle
davon Postfach-Aufträge in der Form, die `docs/boten-postfach.md` selbst
vorschreibt."* Ihr Vorschlag: eine Positivliste harmloser Ersetzungen
(`$HOME`, `$(date …)`).

**Das löst es nicht, und ich habe es an der vorgeschriebenen Form gemessen:**

```
tmp="$HOME/postfach/outbox/.$(date +%s%N).tmp"
cat > "$tmp" <<'JSON'
{ … }
JSON
mv "$tmp" "$HOME/postfach/outbox/$(date +%s%N).json"
```

Diese Form trifft **vier** Schranken, nicht eine: die Ersetzung (`$HOME`,
`$(date)`), die **Zuweisung** (`tmp=` — Boden-Bedingung, seit heute Nacht im
Code), den **Zeilenumbruch** (Heredoc — bleibt Dialog, wie du es richtig
nicht beauftragt hast), und die Umlenkung. **Claudias Liste öffnete die erste
und ließe drei stehen.** Der Auftrag bliebe im Dialog.

**Der tragfähige Weg ist der, den ich am 29.08. selbst in den Kopf von
`bash_dialog_auswertung.py` geschrieben habe:**

> *Wiederkehrende gleichartige Dialoge werden durch benannte, geprüfte Skripte
> ersetzt, die einzeln in die Positivliste rücken — nie durch Öffnen einer
> Klasse.*

### Was gebaut wird

1. **`scripts/postfach_ablegen.py`** — nimmt Zielchat und Text (oder Datei
   und Beschriftung) als Argumente, schreibt atomar (Temp-Name, dann `rename`)
   nach `~/postfach/outbox/`. **Deterministisch, ohne Modell, ohne Netz.**
   Vorbild: `scripts/entscheidung_ablegen.py` (30.08.) — dieselbe Bauform,
   derselbe Handgriff.
2. **Benannte Skripte in der Positivliste** — das gibt es noch nicht (gemessen:
   `scripts/` kommt in `bashfreigabe.py` nur in einem Kommentar vor, Z. 472).
   **Eine Menge, keine Aufzählung:** `python3 <pfad>` ist frei, wenn `<pfad>`
   aufgelöst **unter `<repo>/scripts/` liegt, versioniert ist und in einer
   Liste `BENANNTE_SKRIPTE` steht** — Positivliste, eingetragen wird, wer
   *mehr* darf. Erster Eintrag: `postfach_ablegen.py`. Zweiter:
   `entscheidung_ablegen.py` — es ist heute selbst dialogpflichtig, obwohl es
   genau für diesen Weg gebaut wurde.
3. **`docs/boten-postfach.md` nachziehen:** Das Skript ist der vorgeschriebene
   Weg, die Shell-Form bleibt als *was das Skript tut* stehen. Doku-Spiegel im
   selben Commit.

### Die Gegenprobe, vorher hingeschrieben

- **Erwartete grüne Zeile:** `python3 scripts/postfach_ablegen.py --chat 1
  --text x` → FREI.
- **Erwartete rote Zeilen:** `python3 scripts/irgendwas.py` → DIALOG (nicht in
  der Liste) · `python3 /tmp/postfach_ablegen.py` → DIALOG (nicht unter
  `scripts/`) · `python3 scripts/postfach_ablegen.py; cat .env` → nicht FREI
  (Geheimnis über den ganzen Befehl, vor der Zerlegung).
- **`__pycache__` löschen, `assert alt in t` vor der Ersetzung.**
- **Ausführend, nicht lesend:** `entscheiden()` aufrufen und das Urteil messen.

**Danach nachmessen, was von den 27 bleibt** — `bash_dialog_auswertung.py`
über das Protokoll. Ich erwarte: fast nichts. **Erst wenn etwas bleibt, ist
Claudias Ersetzungs-Liste dran** — nicht vorher. *Löst es sich von selbst.*

### U-3b · `&&`-Ketten — dieselbe Regel, ein Sonderfall

Claudias Messung: 8 Fälle *mehr als ein `&&`*, dazu ein Anteil der 100, die
`a && b` ohne `cd` sind. **Gemessen an `395de2b`:** Die Zerlegung greift an
`;`, `|`, `||` — **`&&` fällt weiter in den alten Zweig**, der nur
`cd <Pfad> && <Befehl>` kennt. `ls && echo fertig` → Dialog.

**Warum `&&` nicht einfach in den Split kann:** `cd` ist ein Boden-Befehl —
`cd x && y` würde dann als Glied `cd x` erkannt und in den Dialog geschickt.
**Die eine Form, die heute erlaubt ist, wäre weg.**

**Die Regel, die beides trägt:** `&&` wird zerlegt wie `;`. **Ausnahme: `cd`
darf als erstes Glied vor genau einem `&&` stehen, mit geprüftem Ziel, das als
Auflösungsbasis durchgereicht wird** (A2 von heute Nacht). Überall sonst ist
`cd` Boden. **Ein Maß, eine benannte Ausnahme.**

**Gegenprobe vorher:** `ls && wc -l x` → FREI · `cd <ws> && ls` → FREI
(unverändert) · `ls && cd /etc && cat passwd` → DIALOG, Grund *Boden* ·
`cd /etc && cat passwd` → DIALOG, Grund *Ziel außerhalb*. Wenn eine dieser
vier anders ausgeht, nicht bauen — melden.

---

# U-4 · Claudias Aufträge 2 und 3 — die Messung selbst
### klein · kein Sicherheitspfad

Beide aus `2026-08-31_bauauftrag-bash-nachtrag-die-pipe.md`, beide **nicht
gebaut** (gemessen): Die Vorprüfungen geben `Entscheid(DIALOG, …)` ohne
Befehlsart, das Protokoll trägt `"art": ""` — **die Auswertung ist blind**; und
`SCHWELLE_DIALOGE = 50` ist eine absolute Wochenzahl — grün bei 91 Prozent
Dialoganteil, wie am 31.08. gemessen.

1. **Befehlsart vor die Vorprüfungen ziehen**, bei Zerlegung die Art des
   auslösenden Glieds.
2. **Maß auf den Anteil:** grün unter 25 Prozent bei mindestens 20 Aufrufen;
   darunter Zahlen ausgeben, **Urteil enthalten**.

**Und die Zeile, die die Abnahme überhaupt möglich macht — gemessen und
gut:** `protokollieren()` läuft **vor** der ABWEISEN/FREI-Verzweigung (Z. 3175
vor 3177). Das Urteil der Positivliste steht also im Protokoll, **auch im
Auto-Zustand**, in dem der Dialog gar nicht mehr erscheint. **Adam kann im
Auto-Zustand arbeiten, und die Zahl wird trotzdem gemessen.** Claudias
Zielmarke — höchstens 20 Prozent Dialog bei derselben Arbeitsweise — ist
damit messbar, ohne dass jemand die Dialoge ertragen muss.

---

# U-5 · Ablage — vier Sätze von Adam, die einen Ort brauchen

**A1 — der Grundsatz, 11:19:** *„Wir brauchen eigentlich nur Zugriff. Wir
müssen diese Sitzung so behandeln, wie die Sitzung, die das erzeugt hat."*
→ **In 5.19**, mit Claudias enger Auslegung, die ich teile: Rechnungsprojekt,
Stammdaten, Geschäftsablage — ja. **Die Repo-Schreibsperre 8.7 bleibt
unberührt**; sie stand in seinem Satz nicht zur Debatte, und eine Instanz
weitet ihre eigenen Rechte nicht aus.

**A2 — 10:29:** *„wenn du eine Spracherkennung einbaust … dass du weißt, dass
ich mit dir spreche … als Sicherheitsfeature … dass klar ist, dass die Sachen
von mir kommen, die hier reinlangen."*
→ **An den Signatur-Punkt** (Auftrag von heute 10:06, M-2) als **zweites
Herkunftsmerkmal**: Die Signatur beweist *aus unserem Haus*, die Sprecher-
Erkennung *von Adam*. Beides beantwortet dieselbe Frage. **Nur Ablage, kein
Bau, keine Nummer.**

**A3 — 11:51, und das ist Kurs-Regel-Material:** *„im Moment ist es für mich
ein deutlicher Rückschritt … wenn wir alles der Sicherheit unterordnen … zu
einem Zeitpunkt, wo das gar nicht notwendig ist, da haben wir vielleicht an
der falschen Stelle zuerst gebaut … das ist einfach nur anstrengend."*
Dazu Claudias Befund, 12:25: *Das Prüfraster misst, ob die Assistenz
funktioniert, nicht ob Adam damit arbeiten kann.*

**Ihren Befund habe ich nachgemessen, und er braucht eine Berichtigung:**
Das Raster hat **eine** Zeile zu Rechnungen (Z. 55, *Tabellen/Rechenblätter
erzeugen 🔄*) — als Basisfähigkeit, nicht als Arbeitsvorgang. *„Keine einzige
Zeile"* ist zu viel; **der Punkt steht trotzdem:** Es gibt keine Zeile, die
*Rechnung stellen, Aufstellung erzeugen, ablegen* als Vorgang prüft, und
deshalb konnte die Fähigkeit beim Umzug still verschwinden.

→ **Prüfraster bekommt Teil 2: Arbeitsvorgänge** — die drei genannten, je mit
✅/🔄/⬜ und dem Satz *lief zuletzt am*. Claudia hat die Regel dazu *„als Regel
abgelegt"* — **in ihrem Gedächtnis, nicht im Repo.** Das hier ist der Weg.
→ **Vorschlag für `CLAUDE.md`, mit Adams Wortlaut, zu seiner Bestätigung** (Frage
an ihn am Schluss): *Vor jeder neuen Schranke: Welche Fähigkeit schützt sie,
und läuft die heute? Was schon einmal ging und heute nicht mehr geht, ist der
dringendste Posten — dringender als jeder Neubau.*

**A4 — 10:17:** *„Ich habe gerade keinen richtigen Durchblick mehr von dem, was
alles gebaut wird."* → Kein Eintrag. **Das ist der Befund von oben** — die
Deploy-Lücke — und er wird durch den Deploy beantwortet, nicht durch eine
Zeile.

---

# Zwei Berichtigungen, beide meine

**① `||` wird zerlegt — Claudias Auftrag sagte: bleibt Dialog.** Ihre
Begründung: *es ist keine Pipe, sondern eine Bedingung; was gelaufen ist,
hängt am Ausgang des ersten.* **Ich habe `||` in den Nachtblock geschrieben,
du hast es gebaut.** Es ist sicher — frei nur, wenn **jedes** Glied frei ist,
und dann ist gleichgültig, welches lief — aber es ist eine Abweichung von
ihrem Papier, und die gehört vermerkt, nicht verschwiegen. **Bitte eine Zeile
im Code-Kommentar und in ihrem Papier.**

**② Claudias „108 von 137" ist zu hoch**, und ich hätte es gestern prüfen
müssen: Die 8 `&&`-Fälle sind nicht gelöst (U-3b), und der `\n`-Anteil der
100 auch nicht. **Die echte Zahl kommt aus der Nachmessung nach dem Deploy**
— mit dem Werkzeug, das dafür da ist. Keine Zahl vorher.

---

# 🚫 Nicht bauen — mit Grund

| | Was | Warum |
|---|---|---|
| 1 | **Claudias Ersetzungs-Positivliste** (`$HOME`, `$(date …)`) | erst nachmessen, was nach U-3 bleibt. Ein `$(date …)`-Muster braucht eine strenge Form, sonst ist `$(date; cat /etc/passwd)` drin — und Befund E vom 23.08. war genau ein `$X`. |
| 2 | **Zeilenumbruch / Heredoc** | Der Inhalt eines Heredocs lässt sich nicht als Glieder prüfen. Mit U-3 fällt der Hauptfall weg. Bleibt Dialog. |
| 3 | **Misch-Befehl 8.7** (Claudias Fall von 10:20: Postfach schreiben + Repo auflisten in einem Befehl → abgewiesen) | Das ist die dritte Schutzschicht von 8.7, Vier-Augen-Prinzip, und sie **weist ab**, statt zu fragen. Gemessen (`_is_repo_write_cmd`): trifft nur, wenn ein Repo-Pfad **und** ein Schreibmuster im selben Befehl stehen. Der Ausweg ist trivial — zwei Befehle. Nicht lockern, schon gar nicht am Tag des Beschriftungsweg-Befunds. |
| 4 | **Ablage-Route A/B/C** | Adams Entscheidung. |
| 5 | **Die Rechnung selbst** | Adams Geschäft. Sie entsteht aus U-2 mit seinen echten Daten — sein ausdrücklicher Wunsch. |

---

# Auflagen

1. **`bash scripts/regressionstest.sh` vor jedem Commit.** Ohne Ausnahme.
2. **`bash scripts/test_zielumgebung.sh` nach U-2 und U-3** — beides berührt
   Pfade, die als Dienst ohne `HOME` laufen.
3. **Commit-Nachrichten über Heredoc** (`git commit -F - <<'EOF'`), nie `-m`.
4. **`ABHAENGIGKEITEN.md`:** `postfach_ablegen.py`, `BENANNTE_SKRIPTE`, der
   Marker `stammdaten`, der Rechnungsordner — beim Bau, nicht danach.
5. **Blaupause-Zeile je Baustein**, dritter Teil: die tatsächliche
   Nebenwirkung.
6. **Doku-Spiegel:** `boten-postfach.md`, `/hilfe` falls berührt, 5.19-Status.
7. **Bericht mit Nenner:** *fünf von fünf* oder *drei von fünf, und welche
   fehlen.* Dazu die Antwort auf U-1 und die zwei Zeilen zu den
   Berichtigungen.
8. **Nichts deployen.** Der Deploy ist Adams — und er ist heute der wichtigste
   einzelne Handgriff im Projekt.

---

# ⏸ Bei Adam — nicht bei dir

**Deploy** (seine Hand, 8.7): `git pull`, Regressionslauf, Neustart. Befehle in
meiner Nachricht an ihn. Danach der Knopf **„🔐 Genehmigen ✓ → Auto"** — das ist
seine Rückfall-Option, sie bleibt über Neustarts erhalten.

**Route A oder B** für die Ablage — mit Claudias und meiner Empfehlung A.

**Die `CLAUDE.md`-Zeile aus U-5 A3** — sein Wortlaut, seine Bestätigung.
