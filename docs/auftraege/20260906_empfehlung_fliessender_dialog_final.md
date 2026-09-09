> **Zweck: ANSICHT + ENTSCHEID (Adam)** · danach Grundlage für Claudias
> Bauauftrag „Sitzung je Zimmer" und meinen Prüfauftrag an Mick ·
> **Zu tun:** die fünf Punkte entscheiden — oder mit mir streiten, vor allem
> über die Vermittlerin. Nichts davon ist gebaut.

# Der fließende Dialog — finale Empfehlung, mit dem Stand vom 05./06.09.

**Stichtag:** 06.09.2026, 01:54 (`date`, Berlin) · **Grundlage:** Konzept 27.07.
(Kap. 7/8), Claudias Vorlage 06.09., Konzept „Sitzung je Zimmer" 05.09., deine
Nachrichten 05.09. 16:11–19:43 und 06.09. 00:24–01:05 im Wortlaut, Code
`e335c23` (Bot-Repo unverändert seit 04.09.) · **Nenner:** 8 neue Dinge seit
dem 31.08. · 5 Empfehlungen · 2 Bauaufträge Claudias geprüft · 2 Prüfbitten
beantwortet · 1 Frage weiterhin bei dir (Hardware).

---

## 1 · Was seit dem 31.08. dazugekommen ist

| Wann | Was | Wo es liegt |
|---|---|---|
| 05.09. 16:11–17:20 | **Dein Freund, „Super Chat", und die Erkenntnis: eine Sitzung je Thema** — Parallelität über Supergruppen-Themen; Multisession-Knopf; Generalchat weiß, was in den Zimmern läuft; Zimmer tauschen Learnings; Echtzeit-Protokoll, nicht Fünf-Minuten-Takt | Claudias Konzept „Sitzung je Zimmer" (7 Bausteine), Blaupause für den Freund, Nachricht an ihn |
| 05.09. 16:58 / 18:07 / 18:38 | **Fable 5.1 + Modell-Aktualität automatisch**, ohne Bauauftrag je Wechsel, mit Hinweis danach und Rückweg — für alle Knöpfe | Claudias Bauauftrag 05.09. (an mich, s. Abschnitt 6) |
| 05.09. 18:25 | **Dein Zielbild im Wortlaut:** der eigentliche Chat baut später nicht mehr selbst, läuft über lokale KI, moderiert wie eine Sekretärin, weist Sitzungen/Agenten an, meldet „ist fertig, liegt da, mit Link"; Auslagerungssitzungen je Thema; alles gebündelt zurück ins richtige Zimmer. **Der Multisession-Knopf ist dir eine Zwischenlösung.** | Gespräch 05.09. |
| 05.09. 18:55 | **Nachsteuern im laufenden Vorgang:** stoppen, pausieren, optimieren, zurücknehmen — „gehört bei uns auf jeden Fall mit rein" | Gespräch 05.09. |
| 05.09. 18:38 | **„Ja, bau das jetzt"** zu Sitzung je Zimmer — Claudia soll den Bauauftrag fertigmachen, Rückfragen vorher | Gespräch 05.09. |
| 05.09. 18:43–19:43 | **Kontingent-Limit dreimal englisch durchgereicht, kein Nachspielen** — du musstest anstoßen | Claudias Bauauftrag 06.09. (an mich, Abschnitt 6) |
| 06.09. 00:24 | **Abwahl-Knopf** für das automatische Weitermachen, Vorbild Claude-Code-Haken; Wecker bleibt, weil modellunabhängig | dito |
| 06.09. 00:34 | **„Immer noch viel zu viele Genehmigungen, obwohl Auto"** | Claudias Nachtrag an mich (Abschnitt 5) |

**Was sich davon von allein erledigt hat:** die drei Konzepte stehen im
Drehbuch (meine Gesamtempfehlung vom 31.08.). **Was sich verschoben hat:**
Punkt 1 der fünf ist durch deine Nachricht von 18:25 nicht mehr abstrakt —
du hast die Vermittlerin beschrieben, wie du sie im Alltag willst. Darum geht
es unten zuerst.

---

## 2 · Die Vermittlerin — worüber wir streiten sollten, und meine Position

**Dein Bild (18:25):** eine Sekretärin, mit der du sprichst. Sie baut nichts.
Sie verteilt an Sitzungen und Agenten, sagt „ist fertig, liegt da", fragt
nach, wenn unklar ist, wohin etwas gehört. Später läuft sie lokal.

**Das Konzept vom 27.07. hat dieses Bild an EINER Stelle falsch übersetzt** —
und diese eine Stelle ist der ganze Konflikt mit der Leitplanke F1: Es sagt
*„Der Vermittler-Dienst LiteLLM … soll den Dialog halten und die Arbeit
weiterreichen."* Das macht aus der Sekretärin einen **Proxy, durch den die
Arbeitssitzungen laufen.** Genau das verbietet F1 — nicht aus
Architekturgeschmack, sondern weil es Drittanbieter-Routing der Abo-Zugangs-
daten ist (AGB, seit 04.04. technisch durchgesetzt, Sperrung ohne Vorwarnung).

**Deine Sekretärin muss aber gar nicht VOR den Arbeitssitzungen stehen. Sie
steht NEBEN ihnen.** Das ist keine Abschwächung deines Bildes, es ist dein
Bild: Eine Sekretärin sitzt nicht in der Telefonleitung zwischen dir und dem
Handwerker. Sie sitzt am eigenen Schreibtisch, nimmt an, schreibt Zettel,
meldet zurück.

**So sieht das gebaut aus, und alles davon existiert schon im Ansatz:**

- **Der Dialogstrang ist eine eigene Sitzung** — der Generalchat eines Hauses,
  später der Hauptchat. Sie hat **keine Werkzeuge, mit denen man bauen kann**:
  kein Bash, kein Write, kein Edit. Das ist keine Verhaltensregel („bitte nicht
  bauen"), es ist Bauart — die Sitzung *kann* nicht. Genau das ist übrigens
  dein zweiter Chat vom 31.08.: *„Alltag, ohne Auto-Bash, die Werkstatt liest
  ihn"*. **Zwei Wünsche, ein Bauteil.** Und die offene Frage vom 02.09. — *trennt
  der zweite Chat die Sitzung oder nur die Ansicht?* — ist damit beantwortet:
  **die Sitzung.** Sonst wäre „ohne Bash" eine Anzeigeregel.
- **Die Arbeitssitzungen sind die Zimmer** — je Thema eine, direkt am Abo, mit
  Werkzeugen. Nichts sitzt zwischen ihnen und Anthropic. F1 unangetastet.
- **Dazwischen kein Modell, sondern Code:** Der Dialogstrang legt einen Zettel
  ins Postfach („Zimmer Rechnungen: 018-26 für DEKO-Service"), der Bot stellt
  ihn dem Zimmer zu; das Zimmer legt „fertig, liegt unter …" zurück, der
  Dialogstrang sagt es dir beiläufig. **Der Verteiler ist deterministisch**, so
  wie das Postfach heute. Ein Modell im Verteiler wäre ein zweiter Wächter
  ohne Prüfer.
- **Der Dialogstrang darf klein sein.** Er muss nicht Fable sein — er redet,
  er rechnet nicht. Sonnet reicht, Haiku vielleicht. **Und er ist die einzige
  Stelle, die später ohne Umbau auf ein lokales Modell wechseln kann**, weil an
  ihr kein Werkzeugpfad hängt. Dein „später lokal" ist damit ein Modellwechsel
  an einer Stelle, keine Architekturänderung.

**Wo ich ehrlich bin, damit du dagegenhalten kannst:**

1. **Jeder Halbsatz kostet einen Modellaufruf** — aus dem gemeinsamen
   Fünf-Stunden-Topf. Ein kleiner Dialogstrang kostet wenig, aber nicht
   nichts. Heute kostet ein Halbsatz dasselbe, er wartet nur. Netto: gleiche
   Aufrufe, andere Reihenfolge — bis der Strang lokal läuft.
2. **Beim Kontingent-Limit schweigt die Sekretärin genau dann, wenn viel
   Arbeit läuft.** Der Wecker (H2) fängt das; der Abwahl-Knopf gehört deshalb
   an den Dialogstrang, nicht an die Zimmer.
3. **Die Sekretärin weiß nur, was in der Ablage steht.** Ein Zimmer, das nicht
   fortlaufend schreibt, ist für sie unsichtbar. Deshalb ist Echtzeit-Protokoll
   je Zimmer (Claudias Baustein 6) keine Kür, sondern die Bedingung, unter der
   die Sekretärin überhaupt Auskunft geben kann. Das Protokoll schreibt heute
   schon lokal im Moment des Ereignisses (gemessen, `ConversationLogger`).
4. **„Nachfragen, wohin es gehört" braucht einen Ort, an dem die Antwort
   ankommt** (Frage-mit-Wirkung-Regel). Der Zettel im Postfach ist dieser Ort;
   eine Rückfrage im Chat, die niemand einem Zettel zuordnet, wäre die Falle
   vom 20.08.

**Meine Position in einem Satz:** *Ja zur Vermittlerin — als eigene, werkzeug-
lose Dialogsitzung neben den Zimmern, mit Code als Verteiler. Nein zur
Vermittlerin als Proxy vor den Arbeitssitzungen.* Wenn du an dem Bild etwas
anders siehst, ist genau das der Punkt, über den wir reden sollten.

---

## 3 · Die fünf Punkte — final

| # | Frage | Empfehlung | Warum jetzt so |
|---|---|---|---|
| **1** | Vermittler-Instanz vor dem Hauptagenten? | **Ja zur Rolle, als Dialogstrang NEBEN den Zimmern, ohne Werkzeuge. F1 bleibt.** | Abschnitt 2. Claudias „Anfang ohne Vermittlerin" ist richtig für Stufe 1, aber dein Zielbild vom 18:25 gehört jetzt schon in den Zuschnitt — sonst baut Stufe 1 den Generalchat als Arbeiter, und die Sekretärin muss ihn später wieder herauslösen. |
| **2** | Gemeinsamer Zustand — VPS oder Heim? | **VPS jetzt; Umzugsweg beim Bau mitschreiben.** | Alles, was hineinkommt, liegt dort schon (Protokolle, Warteschlangen, Postfach). Der Heimtunnel ist nicht gebaut; daran zu hängen blockiert. Roter Inhalt bleibt draußen wie bisher. |
| **3** | Wie viel Parallelität? | **Sitzung je Zimmer, mit Obergrenze 3–4 wachen Zimmern und Einschlafen nach Leerlauf** (Claudias Baustein 7). | Das ist Kapitel 8 in der Form, die du am 05.09. selbst beschrieben hast — nicht „zwei Stränge" als Zahl, sondern **ein Dialogstrang + so viele Zimmer, wie der Topf trägt.** Die Parallel-Probe gegen dein Abo gehört in den Bau, nicht ins Wunschdenken. |
| **4** | Oberfläche? | **Zurückstellen. Telegram mit Häusern und Zimmern IST die Oberfläche für diese Stufe.** | Der Dialogstrang lebt im Generalchat, die Zimmer in den Themen. Durchgehendes Sprechen entscheidet sich, wenn der Faden nachweislich trägt — vorher wäre es das teuerste Stück für eine ungeprüfte Annahme. |
| **5** | Reihenfolge Vermittlerin/Dirigent? | **Zielbild gemeinsam festschreiben (ein Absatz im Drehbuch), bauen in Stufen: ① Zimmer-Kern → ② Nachsteuern → ③ Dialogstrang → ④ lokal/Dirigent.** | Der Dirigent (Modell nach Aufgabe wählen) ist die Entscheidung, die der Dialogstrang später *trifft* — er braucht ihn als Ort. Vorher gebaut wäre er ein Wächter ohne Stelle. **Sparmodus vor Reserve-Topf bleibt**, unabhängig davon. |

**Was du entscheidest, und was es auslöst:** Ein „ja zu 1 bis 5" → ich prüfe
Claudias Bauauftrag „Sitzung je Zimmer" gegen diesen Zuschnitt (Deckung, nicht
Doppelbau), Mick baut ①; ② und ③ folgen als eigene Aufträge mit je einer
„Gut genug wenn"-Zeile. Ein „nein zu 1" → dann reden wir zuerst, weil alles
andere davon abhängt.

---

## 4 · Was die Umsetzung braucht — am Code gemessen, nicht geschätzt

**① Zimmer-Kern (= Drehbuch 5.1 Multi-Session, heute OFFEN).**
`SESSIONS` (`bot.py:1569`), die Postfächer/Warteschlangen (`:1669`) und
`_ensure_worker` (`:1756`) hängen an `user_id`; `thread_id` (`:1555`) ist
nur Rückadresse. Der Umbau ist ein **Schlüsselwechsel auf `(user_id,
thread_id)`** an drei Stellen plus allem, was daraus liest. Klein im Diff,
groß in der Kettenwirkung — **Probelauf im Klon (R4), zwingend.** Mitzuziehen:
Stall-Wächter je Faden · Freigabe-Knöpfe kennen ihren Faden (heute: ein
Dialog je Person) · Prefs bleiben je Person (Auto, Modell, Sprache) ·
Startup-Reconcile (`:9485`, `_start_resumed_workers`) je Faden ·
Wecker/H2 je Faden (`pausiert_bis` liegt heute am Person-Postfach `:1666`).
**Gut genug wenn:** zwei Zimmer antworten gleichzeitig (Stoppuhr), ein
absichtlich aufgehängtes Zimmer wird gemeldet, während ein anderes tippt.

**② Nachsteuern (dein 18:55).** Zwei Hälften, beide klein:
- **Stoppen/Pausieren:** `sess.client.interrupt()` gibt es und wird an zwei
  Stellen gerufen (`:6872`, `:9697`, hinter `/stop`). Es fehlt nur der
  Weg vom Chat in den richtigen Faden — mit ① gratis.
- **Optimieren/Zurücknehmen während des Laufs:** heute Modellverhalten
  (Claudia „entdeckte" eine Nachricht im Puffer). **Deterministisch:** Eine
  Nachricht, die eintrifft, während der Faden arbeitet, landet als Zettel in
  `~/postfach/nachsteuern/<faden>/`; ein **PreToolUse-Hook** liest den
  Ordner vor jedem Werkzeugaufruf und reicht den Inhalt als Systemnotiz
  hinein („Adam hat nachgesteuert: …"). Das Modell muss nichts entdecken; die
  Nachricht kommt an der nächsten Werkzeuggrenze an — spätestens nach
  Sekunden. **Prüfer:** Zettel ablegen, Werkzeugaufruf auslösen, Notiz im
  Kontext messen. **Gut genug wenn:** ein „stopp, andere Farbe" mitten im
  Bau kommt vor dem nächsten Werkzeugaufruf an.

**③ Dialogstrang.** Eine Sitzung mit `allowed_tools` = Lesen im Postfach,
sonst nichts; System-Prompt „du baust nicht, du verteilst und meldest";
Modell klein; Zettel raus über das benannte Postfach-Skript; Fertigmeldungen
der Zimmer über Zimmerfunk (Claudias Baustein 5, dasselbe Postfach-Muster
eine Ebene tiefer). **Prüfer, ausführend:** Der Dialogstrang bekommt „bau
mir X" → im Kontext entsteht ein Zettel, **kein** Werkzeugaufruf außer
Postfach. **Gut genug wenn:** ein Halbsatz wird in < 10 s beantwortet,
während ein Zimmer sichtbar arbeitet, und „ist fertig, liegt da" kommt
beiläufig im Gespräch.

**④ Später:** Dialogstrang auf lokales Modell (Hardware-Frage), Dirigent als
seine Modellwahl-Regel. Nichts davon jetzt.

**Was NICHT gebaut wird:** kein LiteLLM vor Claude-Sitzungen · kein Modell im
Verteiler · keine Sonderregel „kurze Nachrichten überholen" (dein Entscheid
vom 24.07. bleibt — die Trennung ersetzt die Sortierung).

---

## 5 · Claudias zwei Prüfbitten (Dialogflut der Nacht) — am Code beantwortet

**① „Warum fragt der Auto-Modus überhaupt?" — die 16 sind keine Dialoge.**
`bashfreigabe.protokollieren` (`:638`) schreibt **das Urteil der
Positivliste**, nicht ob ein Dialog gezeigt wurde. Im Auto-Zustand fällt ein
DIALOG-Urteil in den Dauerfreigabe-Kurzschluss (`bot.py:3445`) und wird
**still erlaubt** — außer bei Geheimnis-Verweis oder ausgehendem Befehl
(`curl|wget|nc|ssh|scp|telnet`, `:2357`). Auto überlebt den Neustart
(Prefs + Wiederherstellung `:4230`); Hypothese 2 fällt. **Was Adam sah, waren
also entweder Geheimnis-/Ausgehend-Treffer — oder Dialoge aus einer anderen
Sitzung (Mick am Mac).** Von hier nicht trennbar, weil das Protokoll das
Gezeigte nicht kennt.

**Daraus ein Befund, der mich selbst trifft:** `bash_dialog_auswertung.py`
misst dasselbe Feld. **Seit Auto am 01.09. misst die Wochenauswertung
Urteile, keine Dialoge** — die 76 % der Nacht sind Urteile, meine „≤ 20 %"-
Wiedervorlage ebenso. **Fix, klein:** `protokollieren` bekommt ein Feld
`gezeigt` (ja / nein / auto), gesetzt vom Rückruf, der es weiß; die
Auswertung zählt `gezeigt=ja`. Dann ist die Zahl, die am 09.09. kommt, eine
Messung. **An Mick.**

**② Benanntes Skript für die PDF-Erzeugung: ja, mit einer Auflage.**
`scripts/konzept_pdf.py` in `BENANNTE_SKRIPTE`, wie das Postfach-Skript.
**Auflage:** weasyprint lädt aus HTML heraus entfernte Ressourcen (Bilder,
Schriften) — das Skript muss das abschalten (`url_fetcher`, der alles außer
lokalen Pfaden abweist), sonst ist die „kein Netz"-Bedingung eine Behauptung.
Prüfer: ein Markdown mit `<img src="https://…">` → PDF entsteht, kein
Netzzugriff (Attrappe). **An Mick.**

---

## 6 · Claudias zwei Bauaufträge — geprüft

**Kontingent-Automatik + Abwahl (06.09.):** Diagnose am Code bestätigt —
`is_session_limit` (`:1057`) sieht nur Ausnahmen, die `ResultMessage`-Zweige
(`:4901`, `:10755`, `:12684`, `:12840`) prüfen kein `is_error`/`subtype`.
**Zwei Ergänzungen:** (a) Die enge Signatur zuerst am `ResultMessage`
selbst festmachen (`is_error`, `subtype`), Wortlaut nur als Rückfall —
Mick misst im `bot.out.log` vom 05.09. 18:43, wie Claudia verlangt.
(b) Der Abwahl-Knopf gehört an den **Dialogstrang** (Abschnitt 2), sobald es
ihn gibt; bis dahin an die Person. **Freigabe zum Bau: ja, nach ①.**

**Fable 5.1 + Modell-Aktualität automatisch (05.09.):** Auftrag 1 (Knopf
auf `claude-fable-5-1`, mit Probe) und Auftrag 2 (Kennungen in eine
Datendatei, Code bleibt Micks) sind sauber und lösen 8.7 richtig auf.
**Auftrag 3 hat eine AGB-Stelle:** Die „Vorab-Probe" ist ein **Modellaufruf
aus einem Zeitgeber** — genau die Grauzone aus CLAUDE.md (*„Keine Automatik
beginnt von sich aus Arbeit"*). Klein und selten, aber die Regel ist
kategorisch. **Umbau, der beides erfüllt:** Der Monitor erkennt und
**vermerkt** die neue Kennung (modellfrei). Die Umstellung geschieht beim
**nächsten von Adam ausgelösten Lauf** — seine erste Nachricht läuft schon
auf dem neuen Modell und *ist* die Probe; scheitert sie, fällt der Lauf auf
die alte Kennung zurück und meldet es; gelingt sie, kommt danach „auf 5.1
hochgerüstet" mit Rückschalt-Knopf. Kein Aufruf ohne Adam, kein Bauauftrag
je Wechsel, Rückweg sofort. 💰: kein Kostenpunkt (Abo, Docs-Seite
kostenfrei). **Freigabe zum Bau: ja, mit diesem Umbau von Auftrag 3.**

---

## 7 · Bei dir

- **Die fünf Punkte** (Abschnitt 3) — oder der Streit über Abschnitt 2.
- **Hardware** — unverändert offen seit dem 26.07.; ab Stufe ④ blockierend,
  vorher nicht.
- **Claudias Bauauftrag „Sitzung je Zimmer"** kommt zu mir zur Prüfung, sobald
  sie ihn fertig hat; ich prüfe ihn gegen Abschnitt 4 ①.

## Bei mir

Prüfauftrag an Mick (Abschnitt 5 ①/②, Abschnitt 6) nach deinem Wort ·
Nachmessung Dialoganteil erst nach dem `gezeigt`-Feld · Kurs-Blick.
