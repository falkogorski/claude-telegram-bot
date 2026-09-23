# Nachprüfung: Claudias Bauauftrag „Schalterstand im Menü" · Log-Takt · Berichtigung an Claudia

**11.09.2026, 03:38** (date) · Engywuck → Adam (→ Mick, → Claudia)
**Geprüft gegen:** Live-Stand `495ca45` (Server), Branch-Spitze `d783508`, Claudias
Auftrag `ausarbeitungen/2026-09-11_bauauftrag-schalterstand-im-menue.md` (Log-Sync 03:35)

---

## 1. Claudias Bauauftrag — am Code geprüft: er trägt

Jede Fundstelle nachgemessen an `495ca45`:

| Claudias Aussage | Befund |
|---|---|
| `_BEFEHLE` bei 6869, `set_my_commands` bei 11227 ohne `scope` | stimmt (6869 / 11227) |
| `BotCommandScope` kommt im Repo nicht vor | stimmt, `git grep` leer |
| Zustandsgeber `empfang_an` 5878, `vorlesen_setzen` 1706 | stimmt |
| `/spur` liest `trace_off` (Vorgabe aus), `/technik` `raw_tools`, `/quiet`+`/verbose` teilen `sess.quiet` | stimmt (7480 / 8196 / 7452+7466) |
| Dauer-Tastatur zeichnet ihren Stand bereits (Haken) | stimmt, `_main_keyboard` 1272 |
| Live-Stand „606ce26" | **veraltet** — Server steht auf `495ca45`; `bot.py` ist zwischen beiden unverändert (Diff nur Tests/Doku), die Zeilen gelten also |
| `python-telegram-bot >= 22.7` kennt `BotCommandScopeChat` | ja |
| Handler-Gruppen: `TypeHandler` in `group=99` läuft nach dem Schalter-Handler desselben Updates | ja; das Haus nutzt bereits `group=-1` (15129), `ApplicationHandlerStop` nirgends → nichts bricht die Kette ab |

**Die Bauform ist richtig:** getrennte Tabelle `_SCHALTER` statt fünftes Feld,
Signatur-Vergleich statt Aufrufstellen-Liste, globale Liste als Rückfall,
Rückweg per Umgebungsvariable. Client-Zwischenspeicher ist echt (Telegram
verteilt Befehlslisten mit Verzögerung); Claudia sagt es Adam offen. Gut.

### Vier Ergänzungen für Mick (klein, keine Umplanung)

1. **`MENUE_STAND` muss ohne Eintrag „an" bedeuten.** Die Umgebungsdatei ist
   root-Besitz; ein Deploy darf sie nicht brauchen. Vorgabe im Code `an`,
   `aus` nur als Rückweg.
2. **Forum-Zimmer zeigen KEINEN Stand.** `BotCommandScopeChat(chat_id=uid)`
   trifft nur den privaten Chat. Claudias Punkt 6.4 („im Forum zeigt das Menü
   den Stand der Person") gilt erst, wenn auch die Haus-Chat-Kennung
   registriert wird. Heute gibt es kein Haus → als Kommentar an `_SCHALTER`
   und F-Liste, nicht bauen.
3. **`_still_an(uid)` bei mehreren Sitzungen je Person:** `cmd_quiet` setzt
   alle Sitzungen (`_alle_sess`); der Geber soll dieselbe Menge lesen (any/alle),
   nicht `ensure_session` rufen — sonst legt der Menü-Abgleich Sitzungen an.
4. **Prüfzeile 6 dazu: Fehlschlag verwirft die Signatur.** Claudias Auflage in
   6.1 steht im Text, aber nicht in der Prüferliste (1–5). Gegenprobe: Schreib-
   aufruf werfen lassen → nächster Durchgang schreibt erneut. Ohne Zeile ist
   die Auflage ein Kommentar.

**Einordnung:** Kleinkram nach R4-Prüfstein? Nein — post_init, neuer Handler,
neue Tabelle. Aber Rückweg in einer Minute (`MENUE_STAND=aus` oder revert).
Kein Klon nötig, Regressionslauf + Prüfer genügen. Kein Ultracode (keine
Schranke, kein stiller Schaden).

**Wo gebaut wird:** auf `mac-produktivstand` hinter `d783508` — **nicht** auf
`probe-f22`. Dann bringt der nächste ff nur: 0ffa054, 0f4087e, Doku-Commits,
Menü-Umbau. F-22 bleibt draußen, wie beschlossen.

**Deploy:** nicht heute Nacht. Adam schläft/reist; ein Menü-Umbau in der
Nacht vor einer Abwesenheit ohne R1-Blick auf dem Handy ist der Fall vom 29.07.
Mick baut, ich prüfe nach, Deploy zusammen mit 0f4087e, wenn Adam zehn Minuten
am Handy hat (Schritt-0-Zeile zeigt genau diese Commits).

---

## 2. Berichtigung, die Claudia braucht (ihr Register ist stehengeblieben)

Claudia schrieb Adam um 03:35: *„Der Empfang selbst … ausgeschaltet und bleibt
es bis zur Abnahme … `/empfang` zeigt dir nur den Stand."* — **Das ist falsch,
und ihr eigener Lauf widerlegt es:** Adams Nachricht von 03:11 trägt die
Signatur 👩‍💼, die Sekretärin hat beide Anliegen in den Hauptchat gereicht.
Der Empfang ist seit dem 10.09., ~23:40 Uhr **an** (`/empfang an`, Adams
Hand), und der Server steht auf `495ca45`, nicht `606ce26`.

Ursache: Sie wurde am 10.09. (Log Z. 356) auf „606ce26, Empfang aus, bleibt
aus" gesetzt; die Umschaltung danach hat ihr niemand ins Register diktiert.
Kein Fehler von ihr — eine Ablage ohne Nachtrag.

Richtig ist ebenfalls: `/empfang` **ohne** Argument zeigt live nur den Stand
(0f4087e ist nicht deployt). Schalten geht getippt `/empfang an` / `/empfang aus`.

Ihre „zwei Kleinigkeiten" am PDF-Werkzeug sind mir unbekannt; H-2 (netzfrei per
`unshare -rn`) ist live. Sie soll die beiden mit Rückgabewert und Fehlerzeile ins
Register schreiben, dann sehe ich sie im nächsten Sync.

---

## 3. Log-Takt — jetzt fünf Minuten, gewünscht Echtzeit

**Gemessen:** Commits „Log-Sync" um :20, :25, :30, :35 → `OnCalendar=*:0/5`
(so in `docs/befehlsbloecke-root.md` Z. 473 gesetzt). Das Skript selbst ist
schnell und commitet nur bei Änderung („Keine Log-Änderungen — nichts zu pushen").

**Stufe 1 — sofort, Adams Hand (root), kein Code:** Takt auf jede Minute.
Zu beachten: systemd rundet Zeitgeber standardmäßig auf **eine Minute
Ungenauigkeit** (`AccuracySec`), ein Minuten-Takt ohne diese Zeile käme
irgendwann in der Minute. Deshalb zwei Zeilen statt einer.

**Stufe 2 — Mick, kleiner Bau:** Pfad-Einheit `claude-log-sync.path`
(`PathModified=` auf `logs/conversations/` und den Arbeitsordner) startet
`claude-log-sync.service` bei jeder Änderung; systemd stößt nach dem Lauf erneut
an, wenn währenddessen weiter geschrieben wurde, also natürliche Bündelung.
Timer bleibt als Rückfall (Minutentakt). Verzögerung dann ≈ Push-Dauer, ein
paar Sekunden. Unit-Text nach `docs/befehlsbloecke-root.md`, Installation
Adams Hand. Kosten: keine (privates Repo, Pushes gebührenfrei).

**Was mitzieht:** Die NOTBETRIEB-Zeile („älter als zwanzig Minuten = Alarm")
bleibt gültig, wird nur strenger. Kein Prüfer hängt am Fünf-Minuten-Wert
(`grep '0/5'` über daily_check, test_zielumgebung, wachposten: leer).

---

## 4. Texte

**An Mick (Nachtblock, Durchlauf):**
> Nachtblock: Claudias Bauauftrag „Schalterstand im Menü" (Log-Repo
> `ausarbeitungen/2026-09-11_bauauftrag-schalterstand-im-menue.md`) mit
> Engywucks vier Ergänzungen (Vorgabe `an`; Forum ohne Stand als Kommentar +
> F-Liste; `_still_an` ohne `ensure_session`; Prüfzeile 6 Fehlschlag verwirft
> Signatur). Bauen auf `mac-produktivstand` hinter d783508, NICHT auf probe-f22.
> Modell Opus, mittlere Tiefe. Gut genug wenn: Regressionslauf grün, Prüfer
> `test_menue_schalterstand.py` mit sechs Zeilen, je Zeile Gegenprobe (py_compile,
> __pycache__ weg, erwartete Zeile vorher notiert), Bericht-MD mit Hash. Dazu
> Stufe 2 Log-Takt: Unit-Text `claude-log-sync.path` in
> `docs/befehlsbloecke-root.md`, Timer bleibt. Kein Deploy heute Nacht.

**An Claudia:**
> Register nachtragen: Server steht auf 495ca45 (nicht 606ce26). Der Empfang ist
> seit 10.09., ~23:40 AN — deine Antwort von 03:11 trug selbst die Sekretärin-
> Signatur. `/empfang` ohne Argument zeigt live nur den Stand, schalten geht
> getippt an/aus; der Menü-Umschalter kommt mit dem nächsten Deploy. Dein
> Bauauftrag Schalterstand ist geprüft und bei Mick. Schreib die zwei
> PDF-Kleinigkeiten mit Rückgabewert und Fehlerzeile ins Register.
