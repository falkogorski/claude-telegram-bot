> **Zweck: WEITERGABE → Mick** (Adam: Abschnitt „Bevor du den Befehlsblock
> fährst" lesen) · **Zu tun:** Befehlsblock an vier Stellen berichtigen,
> Befunde 1–3 bauen, eine Messung nennen. Befund 4 ist **abgenommen**.

# Nachprüfung Stand `2bc7ce9` — Befund 4 abgenommen, drei Befunde offen

**Stichtag:** 04.09.2026, 20:50 (`date`, Berlin) · **Geprüft:** Diff `360c10b..2bc7ce9`
am Code, Log-Repo `82c9fec` als Zielmessung · **Nenner:** 4 Befunde der
Gegenprüfung — **1 gebaut und abgenommen, 3 unangetastet** ·
Befehlsblock Teil A: **4 Stellen**, an denen Adam anhielte oder Falsches
misst · **1 eigene Falschaussage** (8,40).

## Befund 4 — abgenommen

`--exclude='rechnungen/'` steht **vor** den Includes; der Prüfer fährt das
echte Skript und misst am Zielordner **und** an der Quittung, drei Gegenproben
mit vorher notierter roter Zeile. **Micks Abweichung ist richtig, meine
Vorgabe war falsch:** Ein lautloser Ausschluss wäre die nächste Stille, eine
Zeile je Rechnung die Falschauskunft vom 20.08. Eine Sammelzeile mit Grund
ist die dritte Form, und sie ist die tragfähige. Register und Blaupause
stimmen. **Fertig im Sinn der Konvergenz-Bremse: grün, gegengeprüft,
einsortiert.**

## Befunde 1–3 — nicht angefasst

`git diff --stat 360c10b..2bc7ce9 -- scripts/mac/rechnungen_ablegen.sh
scripts/daily_check.sh scripts/postfach_ablegen.py` ist **leer.** Micks
Bericht nennt als Grundlage nur *„dein Nachtrag hatte zwei Punkte"*, und die
Gegenprüfung `20260904_gegenpruefung_mick_064a062.md` liegt **nicht** unter
`docs/auftraege/`. Nach dem Code hat Mick sie nicht — er hat Befund 4 aus
dem Verweis im Nachtrag gebaut. **Adam: bitte die Gegenprüfung nachreichen.**
Offen bleiben:

1. **Z-1a meldet bei jedem Mac-Start erneut** — Bestand statt Kopiertes gezählt.
2. **Tagescheck 9j zählt einen Ausgang, der nie leer wird** — Durchgangsordner.
3. **Apostroph im Ordnernamen zerreißt den Fernbefehl** — Text über stdin,
   Zeichenmenge als elfter Pfadfall.

Alle drei ohne root, ohne Neustart. Deploy danach per `git pull`.

## 8,40 — meine Falschaussage, und was daraus folgt

Ich schrieb *„kommt nirgends vor"* und hatte nur `RECHNUNGSREGELN.md` und den
Bericht gelesen; die Aufstellung zu 017-26 liegt außerhalb des Repos, und dort
steht sie. **Eine Nirgends-Aussage über eine Menge, die ich nicht ganz gelesen
hatte** — dieselbe Klasse wie mein 25-von-25. Mick hat recht, Adam hat
entschieden: *8,40 gilt, wie in 017-26.*

Und die Zahl ist nicht nur Adams Wahl, sie ist die Regel selbst: **Kürzungen
bemessen sich immer an der vollen Pauschale**, auch am An- und Abreisetag.
Damit fällt der Widerspruch zu `saetze.json` weg — **11,20 ist kein
Abreisetag-Satz**, sondern der volle Tag mit Frühstück und einer Hauptmahlzeit
(28 − 5,60 − 11,20). Das Etikett *„etablierter Abreisetag-Satz, Präzedenz
Dieburg/Landsberg"* ist die Karteileiche, nicht die Zahl.

**Statt eines weiteren Kürzels eine Formel — die Kürzelliste ist eine
Aufzählung, die beim nächsten Fall bricht:**

```
Grund      = 28,00 (voller Tag)  |  14,00 (An-/Abreisetag mit Übernachtung, Tagesfahrt > 8 h)
Kürzung    = 5,60 je gestelltem Frühstück · 11,20 je gestelltem Mittag · 11,20 je gestelltem Abend
Betrag     = max(0, Grund − Kürzungen)
Beschriftung = "Spesen <Betrag/28 in %>"        → 28 = 100 %, 22,40 = 80 %, 14 = 50 %, 11,20 = 40 %, 8,40 = 30 %
```

Das erzeugt alle bisherigen Zahlen und den Abreisetag mit Frühstück und
Mittag (14 − 5,60 − 11,20 → 0), ohne dass jemand ein Kürzel nachträgt. Wenn
der Generator die Formel kennt, sind `Spesen_klein/80/40` nur noch
Schreibabkürzungen. **Mick: Formel in Regel 5a, Etikett in `saetze.json`
berichtigen, `Custom:Spesen 30 %` wird ein regulärer Fall.**

## Bevor du den Befehlsblock fährst — vier Stellen (Adam liest, Mick berichtigt)

**A1, Prüfzeile falsch für den Server.** Der Regressionslauf überspringt bei
laufendem Bot die Heartbeat-Wache und druckt — gemessen an
`regressionstest.sh:439–441` —

```
== Ergebnis: 71/72 bestanden ==
== 1 uebersprungen — auf DIESER Maschine wurde dort nichts gemessen ==
```

A1 verlangt `72/72` und sagt bei weniger *„nicht neu starten, Ausgabe
schicken"*. Adam bliebe am erwarteten Ergebnis hängen — derselbe Fehlalarm wie
am 03.09. um 00:2x. **Richtige Prüfzeile: `71/72 bestanden` + `1
uebersprungen`, kein ❌.**

**A1, Neustart unnötig.** Seit `d6b8190` (Adams Neustart 03.09.) ist keine
`.py`-Datei geändert; Erinnerungen und deutscher Dialog **laufen bereits**
(✈️ war nach dem Neustart im Chat sichtbar). Neu auf dem Server sind nur
Tagescheck und Log-Abgleich — Skripte, die beim nächsten Lauf gelesen werden.
**`git pull` genügt.** Ein Neustart schadet nicht, bricht aber Claudia
mitten im Zug ab, wenn sie gerade arbeitet.

**A2.1, Takt.** Der Abgleich läuft **alle fünf Minuten**, nicht stündlich
(Commit-Zeiten 19:20 · 19:25 · 19:30 · 19:35 · 19:40 · 19:45). Adam muss nach
dem Pull fünf Minuten warten, nicht sechzig. Der Zeitgeber-Name
`claude-log-sync.timer` steht nirgends im Repo — nicht prüfbar von hier;
erscheint bei A2.3 kein `inactive`, hilft `systemctl list-timers | grep -i log`.

**A2.4, Klon-Adresse.** `git clone https://github.com/…` verlangt bei einem
privaten Repo Anmeldedaten im Terminal — Adams Mac-Klon nutzt vielleicht SSH.
Robust: die funktionierende Adresse übernehmen —
`git clone "$(git -C ~/Projects/claude-bot-logs remote get-url origin)"
/tmp/logs-clean` und dieselbe bei `git remote add origin`.

**Dritter Klon: meiner.** Diese Sitzung hält einen Lesekopie des Log-Repos.
Sie pusht nie — nach dem Umschreiben ziehe ich sie mit `fetch` und
`reset --hard` nach, und sage es, wenn es geschehen ist. Damit sind es drei
bekannte Klone.

## A3 und die Rechnungsnummer — ein Widerspruch, gemessen

Teil B des Befehlsblocks sagt: *„das Rechnungsprojekt liegt auf dem Server
und hat die Rechnung 017-26 dort erzeugt."* Das Log-Repo sagt etwas anderes:
Der Abgleich nimmt bis heute jede PDF unter `~/workspace/rechnungen` mit
(der Ausschluss ist noch nicht deployt); die letzte Änderung an
`ausarbeitungen/` ist vom **03.09., 01:05**, und **keine Datei mit 017-26
hat das Log-Repo je erreicht** (`git log --all -- '*017-26*'` → 0). Wäre
017-26 auf dem Server erzeugt worden, läge sie dort — wie 012-26.

**Also entstand 017-26 auf dem Mac**, wie der Nachtbericht sagt („liegt
fertig in iCloud"), und das Projekt ging um 00:59 per rsync auf den Server.
Ob `rechnungsnummern.json` **auf dem Server** 017-26 kennt, hängt an der
Reihenfolge dieser beiden Schritte. Kennt es sie nicht, vergibt Claudia
017-26 ein zweites Mal — der Fall aus Regel 8. **A3 bekommt eine Prüfzeile:**

```bash
ssh claudebot 'grep -c "017-26" ~/workspace/rechnungen/daten/rechnungsnummern.json'
```

**Prüfzeile: `1`.** Bei `0`: die Nummer dort nachtragen (Mick, eine Zeile,
nicht der ganze Ordner — A3 sagt zu Recht, warum). Und Teil B berichtigen:
Zwischenschritte archivieren, aber nicht falsch.

## Claudias Rechnungs-Papiere im Log-Repo (Micks Beobachtung)

`2026-09-02_rechnung-norderney-livesetup.md/.pdf`: Kunde und Beträge, keine
Bank, keine Steuernummer. **Meine Empfehlung: liegen lassen.** Das Repo ist
privat, die Gesprächsprotokolle darin tragen ohnehin mehr, und diese Papiere
sind der Weg, auf dem ich Adams Vorgänge lese. Adams Entscheid, wenn er
anders will.

## Bei mir

Nach Micks Commit zu 1–3: **Nachprüfung, dann Ende dieser Kette.** Nach dem
Umschreiben: meinen Klon nachziehen und melden.
