> **Zweck: ANSICHT (Adam) + WEITERGABE → Mick (Abschnitt 4)** · **Zu tun,
> Adam:** fünf Entscheide in Abschnitt 5 — einer davon blockiert den Bau der
> Zimmer. **Zu tun, Mick:** M-1 heute, M-2/M-3 morgen, Rest in der Reihe.

# Lagebild 05.–07.09. — was mit Claudia lief, was davon Bau braucht

**Stichtag:** 07.09.2026, 21:38 (`date`, Berlin) · **Grundlage:** Log-Repo `origin/main`
(Gespräche 05.–07.09. vollständig, 62 Nachrichten von dir im Wortlaut; fünf
neue Ausarbeitungen; Claudias Register; Tagescheck und Versions-Monitor),
Bot-Repo `e335c23` (seit 04.09. unverändert) · **Nenner:** 9 Befunde, davon
3 an meiner eigenen Arbeit · 11 Punkte für Mick · 5 Entscheide bei dir.

---

## 1 · Was gelaufen ist — in Reihenfolge

| Wann | Was |
|---|---|
| 05.09. nachmittags | Dein Freund, „Super Chat", **Sitzung je Zimmer** (Konzept + Blaupause + Nachricht an ihn) · Fable 5.1 / Modell-Automatik · dein Zielbild Sekretärin · Nachsteuern · **„bau das jetzt"** für die Zimmer |
| 05.09. 18:43–19:43 | Kontingent-Limit, dreimal englisch, kein Nachspielen |
| 06.09. 00:24–01:05 | Abwahl-Knopf-Wunsch · **„immer noch viel zu viele Genehmigungen, obwohl Auto"** · Claudias Vorlage zu den fünf Punkten |
| 06.09. 20:57–22:22 | **Register + Rechnungsregeln als PDF in deine iCloud** gewünscht · Route A von dir **noch einmal** freigegeben (sie ist seit 04.09. gebaut und live, s. Befund 3) · **zweite Mahnung Genehmigungen** · Bürgerfest Bonn beauftragt |
| 07.09. 06:08–08:38 | **Rechnungsmorgen:** 017 und 018 berichtigt, 019 Jülich, 020 Salzburg/Berchtesgaden, 021 Wiesbaden · **40 Minuten Zustellstau** (Befund 1) · 17 Dialoge, 12 mit einer Ursache (Befund 2) · **dritte Mahnung** · Spracherkennung dritte Stufe (Konzept, nicht jetzt) · Zahlungsziele |
| 07.09. 14:37–16:19 | Beide Bauaufträge an mich freigegeben · Muster-Mail · **022 UPW Köln** · Ablagenamen `<Kunde>/<Projekt Ort>` · „Ausgleich bitte bis" · „Personal- und Fahrtkosten" · Extrastunden-Regel · **4.906,80 € seit Norderney** |

**Was gut lief, damit es nicht untergeht:** Sechs Rechnungen aus dem Server,
Nummern vom Server, deine Korrekturen am selben Tag als Regeln festgehalten.
Dein Wort um 14:58: *„Das klappt hervorragend gerade."* 5.19 ist im Betrieb.

**Was nicht lief:** derselbe Satz an drei Tagen — *zu viele Genehmigungen* —
und ein Stau, der dich beinahe alte Rechnungen hätte verschicken lassen.

---

## 2 · Die Befunde, am Code gemessen

### Befund 1 — Der Zustellstau: das Postfach-Skript nennt seinen Absender nicht

Claudias Diagnose stimmt, am Code nachvollzogen: `scripts/postfach_ablegen.py`
schreibt nur `target_chat_id`, `text`, `datei`, `beschriftung`, `zimmer`
(`:142 ff.`) — **kein `herkunft`.** `bot.py:7318` fällt auf „ohne Absender"
zurück, dafür gilt die Fremd-Grenze **5 je Stunde** (`:7446`, Claudia hätte
100). Zehn Aufträge lagen 40 Minuten.

**Das ist mein Fehler, nicht nur Micks:** Ich habe das Skript am 02.09.
gegengeprüft (0a12b67, „25 von 25") und die Grenze nach Absenderart, die eine
Woche vorher gebaut wurde, nie mit dem Skript zusammen gedacht.
Geschwister-Regel, nicht angewandt.

**Zweiter Teil, den Claudia nur halb hat:** Die Drossel **meldet** sich — aber
die Meldung reitet auf der nächsten Zustellung **desselben Absenders**
(`:7527`). Ist der Absender gedrosselt, wartet die Meldung mit. Gemessen im
Gespräch: das 🔇 kam um **15:52**, neun Stunden nach dem Stau.

### Befund 2 — Die Dialoge: zwölf von siebzehn haben eine Zeile als Ursache

`bashfreigabe.py:486`: `if p.parent != (repo / "scripts")`. Die
Rechnungswerkzeuge liegen unter `~/workspace/rechnungen/scripts/` — anderer
Baum, gleicher Name. Claudias Auftrag 1 (benannte Rechnungs-Skripte) ist
richtig; **die Bauform ist ein zweiter Basisordner**, keine Aufweichung.

**Aber die eigentliche Frage bleibt ungemessen, und sie ist größer:** Im
Auto-Zustand fällt ein DIALOG-Urteil in den Dauerfreigabe-Kurzschluss
(`bot.py:3445`) und wird **still erlaubt** — Bash ist nicht in
`_NO_ALWAYS_TOOLS` (`:2424`), Auto überlebt den Neustart (`:4230`), und
`generate_rechnung.py daten/…` trifft keinen Geheimnis-Marker (`:2520`).
**Nach dem Code hätte Adam von diesen zwölf keinen einzigen sehen dürfen.**
Er hat sie gesehen. Also ist entweder Auto **aus** (Prefs-Datei sagt es), oder
es gibt einen Pfad, den ich nicht sehe. **Und niemand kann es heute messen:**
Das Protokoll (`bash-freigaben.jsonl`) und die `bot.err.log`-Zeile schreiben
das **Urteil** der Positivliste; beim tatsächlich **gesendeten** Dialog
(`:3581`) gibt es **keine Protokollzeile**. Claudias „17 Dialoge" und die
Wochenauswertung zählen Urteile. **Das ist der Befund hinter den drei
Mahnungen: Wir streiten seit dem 01.09. über eine Zahl, die niemand misst.**

Dazu Claudias Hinweis auf zwei „freistehendes `&`"-Dialoge ohne `&` im Befehl
(06:51:03, 06:51:22) — von hier nicht prüfbar, Mick zieht die Befehle aus dem
Log. Meine Vermutung: `2>&1`.

### Befund 3 — Claudias Ablage liegt vier Tage hinter dem Repo

Claudias Register (06.09.) führt *„Rechnungen auf den Server, Auftrag 2 (Route
A/B/C) — **offen, hängt an dir**"*, und sie hat dich am 06.09. um 21:12 Route A
**erneut** entscheiden lassen. **Route A ist seit dem 02.09. entschieden, seit
dem 03.09. gebaut und seit dem 04.09. auf dem Server ausgespielt** (Drehbuch
5.19: *„✅ gebaut, Hälfte 2 echt durchlaufen"*, Register `Rechnungsweg Route
A`). Ihr Nachtrag an mich erfindet dazu einen launchd-Zeitgeber (kann nicht
in iCloud schreiben — gemessen 02.09., 330 stille Fehlläufe) und einen
Alters-Prüfer (existiert: Tagescheck 9j).

**Das ist keine Nachlässigkeit, sondern ein fehlender Rückweg:** Was Mick
baut, erreicht Claudias Ablage nicht. Ihre eigene Regel *„Vereinbart ist nicht
gebaut ist nicht geprüft"* hat keine Quelle, aus der sie „gebaut" lesen
könnte — außer dem Drehbuch, das sie vor dem Wort „offen" nicht gelesen hat.

**Ihr Wunsch dahinter ist trotzdem berechtigt, und er ist gratis:** Register
und Rechnungsregeln als PDF in deine iCloud. Route A trägt das heute schon —
`rsync -a -u` **überschreibt** Neueres (`rechnungen_ablegen.sh:194`), ein
zweiter Übergabeordner ist nicht nötig. Claudia legt beide Dateien unter
`ausgang/<Ordnername>/` ab, sie landen unter `Business/Deko/<Ordnername>/`
und werden bei jeder Änderung ersetzt. **Den Ordnernamen bestimmst du**
(Abschnitt 5). Einziger Schönheitsfehler: Die Meldung sagt dann „1
Rechnung(en) gelegt" — Wort ändern.

### Befund 4 — Das Rechnungsprojekt hat seit heute zwei Schreiber und keine Versionierung

Claudia hat am 07.09. auf dem Server geändert: `RECHNUNGSREGELN.md` (vier
neue Regeln), `saetze.json` (119 € Übernachtung), das Rechnungs-Template
(„Ausgleich bitte bis"), `MAIL-VORLAGE.md` neu. Mick ändert dieselben Dateien
am Mac (`~/Projects/rechnungen`). **Die Mac-Kopie ist damit kein Rückweg mehr,
sondern ein veralteter Stand** — und der nächste A3-artige `rsync` Mac →
Server überschriebe Claudias Regeln still. Das Backup (Z-2) sichert die
Server-Fassung täglich; das ist gut, ersetzt aber keine Historie.
**Empfehlung:** `git init` **auf dem Server**, Mac wird Klon. Deine Frage vom
02.09., jetzt mit Grund. Kein Remote, kein GitHub — Bank und Steuernummer
liegen in `daten/`.

### Befund 5 — Das Drehbuch widerspricht seit heute deinen Regeln

Du hast am 07.09. entschieden: *Nummernvergabe ohne Rückfrage* (06:23),
*kein z. Hd.* (06:14), *Auf- und Abbau in eine Rechnung* (15:52), *„Ausgleich
bitte bis"*, Ablagename `<Kunde>/<Projekt Ort>`, XS Modul = DEKO-Service /
Business Modul = LIVESETUP, Vorauszahlung ohne Leistungsdatum, Extrastunden
über einem Zehntel der Pauschale. Claudia hat sie in `RECHNUNGSREGELN.md`
geschrieben — **das Drehbuch 5.19 sagt weiter „Rechnungsnummern-Rückfrage
unverändert Pflicht"**, das Register ebenso, und Claudias Bauauftrag
„Rechnungswerkzeuge" verlangt *„Regel 8 muss unabhängig greifen"*. Drei
Stellen, eine davon deine Entscheidung. Nachziehen, nicht glätten.

### Befund 6 — Der Riegel der Grün-Automatik läuft am 09.09. ab

`auftragsbuch-riegel.md`: `GILT-BIS: 2026-09-09`. Danach schließt er sich
selbst (`auftragsbuch.py:76`), mit Meldung, nichts bricht. Die zwei Wochen
sollten zeigen, ob je ein grüner Auftrag übergeben wird. Aus dem Tagescheck:
täglich *„eine offene Sichtung liegt bereits"* — gelb, wie in der ersten Woche.
**Ich kann von hier nicht messen, ob eine einzige Grün-Übergabe stattfand;
Mick nennt die Zahl.** Meine Empfehlung: Riegel zu lassen, Befund in den
Kurs-Blick, wieder öffnen, wenn das Freigabe-Postfach benutzt wird.

### Befund 7 — Die Updates: ein Auftrag lag neun Tage bei mir

Claudias Bauauftrag vom **29.08.** („offene Updates einspielen") hat mich nie
erreicht, weil ich ihn nie gelesen habe. **Meine Unterlassung.** Stand heute
(Monitor 07.09.): SDK 0.2.127 → **0.2.152**, CLI 2.1.209 → **2.1.263**, Node 22
→ 24 (Major), caldav 3.2.1 → 3.3.0; `pymupdf` ist inzwischen aktuell (Schritt 1
erledigt sich). **Freigabe: Schritt 2 (SDK + CLI als Block) im Klon (R4),
danach die Limit-Signatur neu messen** — das verlangt auch der
Kontingent-Auftrag. Vorbedingung laut Auftrag: Rang A (acht blinde Prüfzeilen)
repariert. **Mick nennt den Rang-A-Stand in einer Zeile**, ich kann ihn von
hier nicht sicher ablesen. Node getrennt, später.

### Befund 8 — Die Zimmer bewegen sich nicht, weil eine Antwort fehlt

Du hast am 05.09. „bau das jetzt" gesagt. Claudia hat den Bauauftrag nicht
geschrieben, weil ihre Vorlage und mein Papier vom 06.09. auf dein Wort zu
den fünf Punkten warten. **Seit 36 Stunden liegt beides unbeantwortet.** Das
ist kein Vorwurf — du hattest Rechnungen zu schreiben —, aber es ist der
Grund, warum die Zimmer stehen.

### Befund 9 — Meine Nachprüf-Zeile war das falsche Maß

Meine Wiedervorlage „Dialoganteil ≤ 20 %" misst dasselbe Urteils-Feld wie
Claudias 76 %. Seit Auto am 01.09. sagt es nichts über gezeigte Dialoge.
Steht seit dem 06.09. in meinem Papier; heute die Zahl dazu: **null gezeigte
Dialoge sind messbar.**

---

## 3 · Zwei Dinge, die gut sind und bleiben sollen

- Claudias Nachfrage-Kalibrierung vom 07.09. (Datum, „sofort") hat dich
  überzeugt — das ist die selbstlernende Assistenz, wie sie gemeint war.
- Claudias eigene Konsequenz *„ein Befehl je Aufruf"* wirkt ohne Bau. Sie
  senkt Urteile, nicht zwingend Dialoge (Befund 2) — aber sie schadet nicht.

---

## 4 · Prüfauftrag an Mick — Reihenfolge ist Dringlichkeit

**M-1 (heute): `postfach_ablegen.py` schreibt `herkunft`**, Vorgabe
„Claudia", Schalter `--herkunft` für Blume/Hora. Prüfzeile im vorhandenen
Postfach-Test: Auftrag aus dem Skript trägt das Feld; Zustellung läuft unter
der Claudia-Grenze. Gegenprobe: Feld entfernen → genau diese Zeile rot.
**Dazu:** die 🔇-Meldung geht **sofort** an Adam, einmal je Stunde und
Absender, **unabhängig von der gedrosselten Warteschlange** — sonst meldet
die Drossel ihren Stau erst, wenn er vorbei ist.

**M-2 (morgen): zweiter Basisordner für benannte Skripte.**
`_benanntes_skript` prüft heute nur `<repo>/scripts/`. Neu: eine Menge
`SKRIPT_BASEN = {repo/scripts, workspace/rechnungen/scripts}`, je Basis eine
eigene Namensmenge (`ablage.py`, `generate_aufstellung.py`,
`generate_rechnung.py`); `DEUTER` um den **aufgelösten** Pfad
`workspace/rechnungen/.venv/bin/python` erweitert — nicht um „irgendein
python in irgendeiner venv". Die Nummernvergabe ist seit 07.09. ohne
Rückfrage (Adam) — die Auflage „Regel 8 unabhängig" entfällt, das steht dann
im Auftrag berichtigt. **`mv`/`cp` innerhalb `~/workspace/`:** ja, wenn
**beide** Pfade nach Auflösung (Symlinks, `..`) darunter liegen; `rm` bleibt
Dialog. Prüfzeilen beidseitig.

**M-3 (morgen): die Dialog-Messung, die seit dem 01.09. fehlt.**
(a) `protokollieren` bekommt `gezeigt` (ja/nein/auto), gesetzt vom Rückruf;
(b) eine `log.info("Freigabe-Dialog gesendet …")` an `bot.py:3581`;
(c) `bash_dialog_auswertung.py` zählt `gezeigt=ja`; (d) **Messung, bevor
irgendetwas gebaut wird:** Steht `"Bash"` in Adams `always_allow` in der
Prefs-Datei auf dem VPS — ja oder nein? Und die zwei `&`-Befehle von
06:51:03/06:51:22 aus `bot.err.log` im Wortlaut. Beides in den Bericht.
(e) Claudias Prüfbitte: `bash-freigaben.jsonl` für sie lesbar — **nein**;
stattdessen liest die Auswertung für sie und legt das Ergebnis nach
`~/postfach/` (Ergebnis raus, Datei zu). Ein Leserecht unter `.claude` wäre
die Klasse, die 8.7 verbietet.

**M-4: PDF-Skript** `scripts/konzept_pdf.py` in `BENANNTE_SKRIPTE`, mit
`url_fetcher`, der alles außer lokalen Pfaden abweist (weasyprint lädt sonst
aus dem Netz). Prüfer: Markdown mit `<img src="https://…">` → PDF entsteht,
kein Netzzugriff.

**M-5: Drehbuch und Register nachziehen** (Befund 5): 5.19-Akzeptanz
„Nummern-Rückfrage" → „ohne Rückfrage, Adam 07.09."; die sieben neuen Regeln
als Verweis auf `RECHNUNGSREGELN.md`; Route A: *„Adam am 06.09. erneut
freigegeben — war seit 02.09. entschieden"* als Vermerk, nicht geglättet.
**Und eine Zeile für Claudia** in ihrem Register-Abschnitt 3.4, die sie
beim nächsten Lauf liest: *„Stand eines Bauauftrags steht im Drehbuch, nicht
in dieser Liste."*

**M-6: Route-A-Meldungstext** „Rechnung(en)" → „Datei(en)"; Claudia legt
Register und Regeln unter `ausgang/<Ordnername>/` ab, sobald Adam den Namen
nennt.

**M-7: Kontingent-Automatik + Abwahl** (Claudia 06.09.), mit meinen zwei
Ergänzungen aus dem Papier vom 06.09.: Signatur zuerst am `ResultMessage`
(`is_error`/`subtype`), Wortlaut als Rückfall; Abwahl an der Person.
**Nach M-9 bauen**, weil die Signatur mit dem SDK-Sprung erneut zu messen ist.

**M-8: Fable 5.1 + Modell-Aktualität** (Claudia 05.09.), Auftrag 1 und 2 wie
geschrieben; Auftrag 3 mit dem Umbau aus meinem Papier: **keine Probe aus dem
Zeitgeber** — Umstellung beim nächsten von Adam ausgelösten Lauf, der Lauf
ist die Probe, Rückweg sofort. AGB-Grauzone vermieden, kein Bauauftrag je
Wechsel, wie Adam es will.

**M-9: Updates Schritt 2** (SDK 0.2.152 + CLI 2.1.263) im Klon (R4), voller
Regressionslauf, Pin nachziehen, danach Limit-Signatur messen und die
übersprungenen Änderungsnotizen auf den Freigabe-Auftrag lesen. **Vorher:
Rang-A-Stand in einer Zeile.** Node getrennt, eigener Termin.

**M-10: Rechnungsprojekt versionieren** — erst nach Adams Ja (Abschnitt 5).
Dann `git init` auf dem Server, `.gitignore` für `.venv/`, `output/`,
`ausgang/`, kein Remote; Mac-Kopie wird Klon; `docs/aenderung-rechnungs-
projekt-2026-09-02.md` bekommt den Schlusssatz, dass der Rückweg jetzt
`git log` heißt.

**M-11: Riegel** — nach Adams Wort (Abschnitt 5): `GILT-BIS` setzen oder
ablaufen lassen; die Zahl der Grün-Übergaben 25.08.–09.09. in den Bericht.

**Nicht in diesem Auftrag:** Spracherkennung dritte Stufe (Adam: „wann,
schauen wir"), Zimmer-Kern (wartet auf Abschnitt 5, Punkt 1), Sekretärin.

---

## 5 · Bei dir — fünf Entscheide, jeder löst etwas aus

1. **Die fünf Punkte zum fließenden Dialog** (mein Papier vom 06.09., Claudias
   Vorlage). Ein „ja zu 1–5" → Claudia schreibt den Zimmer-Bauauftrag, ich
   prüfe ihn, Mick baut. **Solange nichts kommt, steht der Bau.** Willst du
   die Sekretärin noch diskutieren, sag „später" — dann geht Zimmer-Kern ①
   trotzdem los, er ist unter jeder Antwort richtig.
2. **`git init` im Rechnungsprojekt auf dem Server** — ja oder nein.
3. **Riegel der Grün-Automatik nach dem 09.09.:** zu lassen (meine
   Empfehlung) oder verlängern bis wann.
4. **Ordnername in `Business/Deko/`** für Register und Rechnungsregeln.
5. **Hardware** — unverändert offen seit dem 26.07., blockiert erst Stufe ④.

## Bei mir

Nachprüfung M-1 bis M-3 am Code, sobald Mick pusht · Zimmer-Bauauftrag von
Claudia gegen meinen Zuschnitt prüfen · Kurs-Blick: der Update-Auftrag, der
neun Tage bei mir lag, kommt als eigene Zeile hinein.
