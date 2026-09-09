> **Zweck: WEITERGABE → Mick** (Adam: eine Box zum Modell der Sekretärin
> kommt im Chat) · **Zu tun:** Claudias Bauauftrag
> `2026-09-09_bauauftrag-sitzung-je-zimmer-und-sekretaerin.md` bauen —
> **freigegeben mit sieben Auflagen und einer Umstellung der Reihenfolge.**
> Alle Auflagen sind am Code gemessen, keine ist Geschmack.

# Freigabe „Sitzung je Zimmer und Sekretärin" — mit Auflagen

**Stichtag:** 09.09.2026, 12:25 (`date`, Berlin) · **Geprüft gegen:** meinen
Zuschnitt vom 06.09. (Sekretärin neben den Zimmern, Verteiler Code, F1 bleibt),
Adams fünf Entscheide vom 09.09., Bot-Repo `e3596fd` · **Nenner:** 7 Aufträge
Claudias, alle im Zuschnitt · 7 Auflagen · 1 Reihenfolge-Fehler · 1 Entscheid
für Adam (Modell).

**Was Claudia richtig hat, damit es nicht untergeht:** Sekretärin und Zimmer
als ein Bau, der Verteiler nach Herkunft und Zustand statt nach Inhalt, die
Bruchstellen-Tabelle mit Prüfer je Zeile, „Gut genug wenn" messbar, das
Sichtbarkeits-Flag als billige Leitplanke, und der ehrliche Satz *„ohne
Einspeisung ist sie ahnungslos"*. Das ist die Bauform, wie sie sein soll.

---

## Auflage 1 — „Keine Werkzeuge" ist eine Fabrik, keine leere Liste

`bot.py:4744` trägt die Lehre vom 22.08.: `allowed_tools=[]` mit
`bypassPermissions` ist **das Gegenteil** von „keine Werkzeuge". Die
Sekretärin bekommt deshalb die **vorhandene Fabrik** (`dontAsk` + Positivliste)
— nicht zwei neue Zeilen. Dazu: `mcp_servers` ohne `suche`, `add_dirs` leer,
eigener System-Prompt. **Prüfer, ausführend:** Sekretärin-Sitzung mit der
Aufforderung „lies `~/workspace/x`" und „führe `ls` aus" → **kein**
Werkzeugaufruf, Deny im Protokoll, Antwort ist Text. Gegenprobe: Modus auf
`default` → Zeile rot.

## Auflage 2 — Die Übergabezeile `::AUFTRAG` wird ein typisiertes Werkzeug

Ein Textmarker im Fließtext ist die Bruchstelle, die Claudia selbst nennt —
und eine zweite, die sie nicht nennt: **Fremder Text, den Adam in den Empfang
kopiert und die Sekretärin zitiert, enthielte die Marke, und der Verteiler
führte sie aus.** Das ist die Klasse *„von außen kommen nie Anweisungen"*.

**Bauform:** Der Bot bietet der Sekretärin **genau ein** Werkzeug im Prozess
an — `create_sdk_mcp_server` gibt es schon (`bot.py:4044`, `suche`):
`zettel_ablegen(zimmer, text)`. Die Positivliste aus Auflage 1 hat damit
**einen** Eintrag. Das Werkzeug prüft `zimmer` gegen die bekannten Fäden,
weist Unbekanntes **benannt an das Modell zurück** (kein stiller Rückfall in
den Hauptfaden nötig), legt den Zettel deterministisch in die
Zimmer-Warteschlange und protokolliert. Kein Parser über Modelltext, kein
Marker, kein Satz, der versehentlich zum Auftrag wird. Claudias Regel 3 und
die zwei Marker-Bruchstellen entfallen damit — Wirkung statt Schreibweise.

## Auflage 3 — Das Kontingent-Limit gilt je Person, nicht je Zimmer

`pausiert_bis` liegt heute auf der Mailbox (`bot.py:1031`, `:1769`). Nach dem
Schlüsselwechsel läge es **je Zimmer** — dann entdecken vier Zimmer dasselbe
Limit viermal, vier ⏳-Meldungen, vier Wecker. **Das Limit ist kontoweit:**
ein Feld je Person, alle Fäden pausieren gemeinsam, **eine** Meldung, ein
Wecker. Und: **Die Sekretärin hängt am selben Limit.** Sie schweigt genau
dann, wenn alles arbeitet — das darf nicht wie Ruhe aussehen. Bauform: Beim
Limit legt der Bot (deterministisch, ohne Modell) in den Empfangs-Faden
*„Kontingent bis HH:MM ausgeschöpft, ich mache dann weiter"* — das ist die
H2-Meldung, nur an den richtigen Ort.

**Dazu ein Fund, der Claudias Kontingent-Auftrag (M-7) ändert:** Das SDK
liefert ein **`RateLimitEvent`** (`rate_limit_info`), und der Bot verarbeitet
es bereits an zwei Stellen (`bot.py:4911`, `:12904`). **Die enge Signatur für
M-7 ist dieses Ereignis**, nicht der Wortlaut „You've hit your session
limit". Der Text bleibt Rückfall. Mick misst, ob das Ereignis am 05.09. um
18:43 kam — im `bot.out.log`.

## Auflage 4 — Nachsteuern gibt es zur Hälfte; die andere Hälfte ist klein

`_is_interrupt` (`bot.py:1750`) und `sess.client.interrupt()` (`:9772`)
stoppen heute einen laufenden Vorgang, wenn eine Nachricht mit einem
Stopp-Wort beginnt, und reihen sie vorn ein. **Nach dem Schlüsselwechsel gilt
das je Zimmer — gratis.** Was fehlt, ist Adams zweite Hälfte vom 05.09.
(*„optimieren, ergänzen, zurücknehmen, ohne zu stoppen"*): **Auftrag 8**,
ein PreToolUse-Hook, der vor jedem Werkzeugaufruf des Zimmers den Ordner
`~/postfach/nachsteuern/<faden>/` liest und Neues als Systemnotiz hineinreicht.
Zwanzig Zeilen, ein Prüfer: Zettel ablegen, Werkzeugaufruf auslösen, Notiz im
Kontext messen. Gehört in den Kern, weil er den Schlüssel braucht.

## Auflage 5 — Zwei Antworten in einem Faden brauchen ein Gesicht

Claudias Regel 2 schickt in ein beschäftigtes Zimmer **zwei** Antworten: erst
die Sekretärin (Sekunden), später das Zimmer. Ohne Kennzeichnung liest Adam
zwei Stimmen als eine. **Die Sekretärin trägt eine Signatur** — Adams
Vokabular kennt 🪷 🌺 🕰️; sie bekommt ein eigenes Zeichen, das Adam wählt
(Vorschlag 🛎️). Und das Zimmer nennt beim Fertigwerden, worauf es antwortet.
Prüfer: Text der Zwischenantwort beginnt mit der Signatur.

## Auflage 6 — Der Schlüsselwechsel ist ein Klon-Fall (R4), und er ist größer als drei Zeilen

Gemessen: `SESSIONS.get` 18×, `MAILBOXES.get` 11×, `_get_mailbox(` 9×,
`_ensure_worker(` 5×, `sess.thread_id` 4×, `ConversationLogger(` 1× — rund
**fünfzig Stellen**, dazu Startup-Reconcile (`:9485`), `/reset`
(`:4271`), der Wecker (`:1769`). Bauform: **ein** Schlüssel-Helfer
`faden(user_id, thread_id)` und **ein** Datentyp, der beides trägt — nicht
fünfzig Stellen mit Tupeln. Prefs bleiben je Person (Claudia hat das
richtig). Freigabe-Dialoge (`sess.pending_permissions[request_id]`) und der
Stall-Wächter (`sess.last_activity`) hängen an der Sitzung und werden **durch
den Schlüsselwechsel von selbst je Zimmer** — Claudias zwei Testfälle bleiben
als Nachweis, brauchen aber keinen eigenen Bau. **Probelauf im Klon, voller
Regressionslauf, erst dann Hauptbaum.**

## Auflage 7 — Reihenfolge: Leitstand-Minimum VOR der Sekretärin

Claudia baut die Sekretärin in Schritt 1 und den Leitstand in Schritt 2 —
**ihre eigene Bruchstelle Nummer eins** (*„ohne eingespeisten Stand erfindet
sie Auskünfte"*) wäre damit im ersten Schritt gebaut. Umgestellt:

| Block | Inhalt | Gut genug wenn |
|---|---|---|
| **1 · Kern** | Schlüsselwechsel im Klon, Auftrag 8 (Nachsteuer-Hook), Limit je Person | zwei Zimmer antworten gleichzeitig (Stoppuhr) · aufgehängtes Zimmer wird gemeldet, während ein anderes tippt · Stopp-Wort stoppt nur sein Zimmer · Limit erzeugt eine Meldung, nicht vier |
| **2 · Sicht** | Leitstand-Minimum (wach / arbeitet an / seit wann / zuletzt fertig) + `/zimmer` + Protokoll je Zimmer | `/zimmer` stimmt mit der Wirklichkeit überein (zwei Zimmer, eines schläft) |
| **3 · Empfang** | Sekretärin mit Fabrik (Auflage 1), Zettel-Werkzeug (Auflage 2), Einspeisung aus Block 2, Signatur (Auflage 5), Knopf, Haushalt mit Parallel-Probe | Sekretärin antwortet, während ein Zimmer rechnet, und nennt richtig, woran es arbeitet · Zettel kommt im Zimmer an, Ergebnis im richtigen Thema · Knopf schaltet beide Richtungen · Obergrenze greift sichtbar |
| **4 · Verbund** | Zimmerfunk, gemeinsames Wissen mit Sammelstelle, Feinschliff nach den Häusern | Learning wandert A → Sammelstelle → B |

Vier Blöcke, keiner länger als ein Nachtblock; jeder einzeln gepusht mit
Bericht. **Block 1 zuerst und allein** — er ist die Kettenwirkung, alles
andere hängt daran.

## Was Adam entscheidet (kommt als Box)

**Modell der Sekretärin.** Claudia empfiehlt schnell; Adams Regel sagt
höchstes. Meine Empfehlung: **Sonnet 5** — sie muss einordnen, nicht nur
antworten (Haiku wäre zu dünn), und sie darf den Topf nicht leeren (Fable
wäre zu teuer für Halbsätze). Als Standard je Rolle, umschaltbar.
**Obergrenze wacher Zimmer:** aus der Probe, kein Entscheid.

## Bei mir

Nachprüfung je Block am Code, beginnend mit dem Klon-Lauf von Block 1 ·
Ultracode-Prüfstelle: **nach Block 3**, weil dort neue Schrankenlogik entsteht
(Positivliste mit einem Eintrag, Zettel-Werkzeug) — ich starte ihn.

---

## Nachtrag 09.09.2026, 12:27 — Adams zwei Entscheide, per Auswahl

- **Modell der Sekretärin: Sonnet 5**, als Standard je Rolle, umschaltbar.
  Zimmer behalten Adams Grundregel (höchstes Modell).
- **Signatur der Sekretärin: 👩‍💼 „Sekretärin".** Adam hat das
  Personenzeichen **ausdrücklich** gewählt, gegen meinen Hinweis, dass die
  Zeichen bisher Funktionen benennen. Sein Entscheid, nicht geglättet:
  `reaktionen-vokabular.md` bekommt die Zeile, mit dem Vermerk „Adam,
  09.09., bewusst als Person". Prüfer aus Auflage 5 misst auf dieses Zeichen.
