<!-- ROLLE: bauauftrag -->
# Bauauftrag — Sitzung je Zimmer, und die Sekretärin am Empfang

> **Zweck: BAUEN** · **Zu tun:** Echtes Nebeneinander im Bot herstellen — eine
> Sitzung je Zimmer, daneben eine werkzeuglose Dialogsitzung, dazwischen ein
> Verteiler aus Code. **Weg:** Claudia → Engywuck → Mick.

**Zustand: freigegeben, liegt bei Mick in vier Blöcken** (Engywuck, 09.09.2026).
**Grundlage:** `2026-09-05_konzept-sitzung-je-zimmer.md` (die sieben Bausteine)
und `2026-09-06_entscheidungsvorlage-fliessender-dialog.md` (fünf Punkte).

## Änderungsverlauf

**09.09.2026, 12:45 Uhr** — Fassung 2 nach Engywucks Prüfung. Drei Änderungen,
alle drei übernommen und im Text eingearbeitet:

1. **Die Übergabe wird ein typisiertes Werkzeug**, kein Textmarker. Ein Marker
   im Fließtext könnte aus zitiertem Fremdtext zum Befehl werden (Auftrag 3,
   Regel 3).
2. **Das Kontingent bleibt je Person**, nicht je Zimmer (Auftrag 5).
3. **Der Leitstand kommt vor der Sekretärin.** Sonst startet sie ohne Stand —
   die erste Zeile meiner eigenen Bruchstellen-Tabelle (Reihenfolge).
4. Adams Entscheid dazu: **Sonnet 5 für die Sekretärin**, als Standardwert je
   Rolle. Ihr Zeichen ist **👩‍💼**, bewusst als Person gewählt.

**09.09.2026, 12:35 Uhr** — Fassung 1, aus Adams Entscheid zu den fünf Punkten.

---

## Adams Entscheid

Alle fünf Punkte der Entscheidungsvorlage sind beantwortet. Drei Sätze legen
den Bau fest:

1. **Sitzung je Zimmer** nach dem Konzept vom 05.09.
2. **Die Sekretärin** ist eine **eigene, werkzeuglose Dialogsitzung** neben den
   Zimmern.
3. **Der Verteiler ist Code** — keine KI-Instanz vor dem Hauptagenten.

Damit sind die Punkte im Einzelnen erledigt: Punkt 1 — die Architektur-Leitplanke
vom 12.07. bleibt, jeder Strang läuft direkt am Abo, der Verteiler ist ein
deterministisches Stück Programm. Punkt 2 — der gemeinsame Zustand liegt auf dem
Server. Punkt 3 — gebaut wird der volle Zimmer-Umbau, und die Sekretärin ist der
Dialogstrang darin. Punkt 4 — Telegram bleibt, eine Sprech-Oberfläche steht
hinten an. Punkt 5 — der Dirigent bleibt Zielbild und Merkposten.

## Es wird einmal gebaut, nicht zweimal

Engywuck war gebeten, auf die Deckung zwischen Zimmer-Blaupause und
Zwei-Strängen zu achten. Adams Entscheid löst die Frage auf: **Die Sekretärin
ist der Dialogstrang, die Zimmer sind die Arbeitsstränge.** Ein Bau, ein
Zustandsspeicher, ein Verteiler. Der frühere „Zwei-Stränge-Anfang" hat damit
keinen eigenen Auftrag mehr.

## Gemessener Stand (09.09.2026, im Quelltext nachgesehen)

| Stelle | Was dort steht |
|---|---|
| `bot.py:1569` | `SESSIONS: dict[int, UserSession]` — ein Schlüssel je Person |
| `bot.py:1669` | `MAILBOXES: dict[int, Mailbox]` — eine Warteschlange je Person |
| `bot.py:1756` | `_ensure_worker(user_id)` — ein Arbeiter je Warteschlange |
| `bot.py:1555`, `:1622` | `thread_id` steuert heute allein die Rückadresse |
| `channels.py` | Vier Häuser, 13 Zimmer, Anlege- und Zuordnungslogik fertig |
| `MIGRATION.md` 5.1 | Multi-Session, offen |

Die Zeilennummern aus dem Konzept vom 05.09. gelten unverändert.

---

## Auftrag 1 — Der Schlüssel-Umbau

Sitzung, Warteschlange und Arbeiter wandern vom Schlüssel `user_id` auf das Paar
`(user_id, thread_id)`. Jedes Zimmer bekommt eigenen Gesprächsfaden, eigenes
Gedächtnis, eigene Warteschlange, eigenen Arbeiter. Der Hauptchat ohne Thema
behält seinen Platz als eigener Faden.

**Das ist der Kern.** Alles Weitere hängt daran.

## Auftrag 2 — Die Sekretärin

Eine eigene Claude-Sitzung mit eigenem Schlüssel, eigener Warteschlange, eigenem
Arbeiter — technisch ein Zimmer wie jedes andere, mit einem Unterschied:

**Sie hat keine Systemwerkzeuge.** Kein Bash, kein Lesen, kein Schreiben, kein
Netz. Daraus folgt ihre Eigenschaft: Sie braucht für eine Antwort Sekunden, nie
Minuten, und sie kann nicht blockieren. Sie ist damit jederzeit ansprechbar,
auch wenn alle Zimmer rechnen.

**Die eine Ausnahme, und ihre Grenze gehört festgeschrieben:** Sie hat genau ein
Werkzeug, die typisierte Übergabe aus Auftrag 3. Es reicht einen Auftrag in eine
Warteschlange, sonst nichts — es liest nicht, schreibt nicht, ruft nichts auf,
und es kehrt sofort zurück. Ihre Eigenschaft „blockiert nie" bleibt damit
unangetastet.

**Diese Ausnahme ist keine Tür.** Wer später erwägt, ihr ein zweites Werkzeug zu
geben, hebt den Zweck dieser Rolle auf: Ein Empfang, der selbst arbeitet, lässt
den Wartenden wieder warten. Die Rolle heißt werkzeuglos, und die Übergabe ist
der einzige benannte Ausgang.

**Sonnet 5 ist ihr Modell** (Adams Entscheid vom 09.09.), als Standardwert je
Rolle gesetzt und umschaltbar. Ihr Zeichen ist **👩‍💼**, bewusst als Person
gewählt; es gehört ins Reaktions- und Signaturen-Vokabular, sobald es gebaut
ist.

**Was sie braucht, damit sie etwas weiß:** Da sie nicht lesen kann, muss ihr der
Code den Stand **in den Kontext legen** — bei jedem Zug neu:

- das gemeinsame Gedächtnis (dasselbe wie bei den Zimmern),
- die Leitstand-Übersicht aus Auftrag 6: welche Zimmer wach sind, woran sie
  arbeiten, seit wann, was zuletzt fertig wurde,
- die Kurzfassung jedes abgeschlossenen Zimmer-Auftrags, sobald er fertig ist.

**Ohne diese Einspeisung ist sie ahnungslos** und erfindet Antworten. Die
Einspeisung ist deshalb Teil dieses Auftrags, keine spätere Verfeinerung.

**Ihre Aufgabe:** antworten, einordnen, den Faden halten, Aufträge annehmen und
weiterreichen. Rechnen, suchen, bauen tun die Zimmer.

## Auftrag 3 — Der Verteiler, ein Stück Code

Er entscheidet nach **Herkunft und Zustand**, nicht nach Inhalt. Damit ist er
prüfbar und wiederholbar.

**Regel 1 — Wohin eine Nachricht geht:**

| Eingang | Ziel |
|---|---|
| Nachricht in einem Zimmer-Thema | die Sitzung dieses Zimmers |
| Nachricht im Hauptchat oder im General-Bereich eines Hauses | die Sekretärin |

**Regel 2 — Wenn das Zimmer beschäftigt ist:** Schreibt Adam in ein Zimmer, das
gerade arbeitet, reiht der Verteiler die Nachricht dort ein **und** gibt sie der
Sekretärin für eine sofortige Zwischenantwort. Adam bekommt binnen Sekunden eine
Rückmeldung, und sein Anliegen steht trotzdem in der Reihe. Das ist der
Alltagsnutzen, um den es geht.

**Regel 3 — Die Übergabe von der Sekretärin ins Zimmer: ein typisiertes
Werkzeug.** `[GEÄNDERT 09.09., Engywuck]` Die Sekretärin ruft eine benannte
Übergabe mit zwei Feldern auf — Zimmer und Auftragstext. Der Verteiler nimmt
ausschließlich diesen Aufruf als Auftrag entgegen; ihr Fließtext geht an Adam
und wird nie als Befehl gelesen.

**Warum kein Textmarker:** Eine Zeile wie `::AUFTRAG …` im Text lässt sich von
außen einschleusen. Adam leitet Fremdtext weiter, ein Zimmer zitiert eine Datei,
eine Webseite steht im Kontext — und aus zitiertem Text würde ein ausgeführter
Auftrag. Ein Werkzeugaufruf entsteht dagegen nur durch eine Entscheidung des
Modells und trägt seine Felder getrennt vom Fließtext. Die Prüfung dafür ist
maschinell, nicht heuristisch.

**Was der Verteiler prüft:** Das Zimmer muss in `channels.py` auflösbar sein.
Ist es das nicht, geht der Auftrag **nicht** verloren: Er landet im Hauptfaden
mit der Adresse, die sich nicht auflösen ließ.

**Regel 4 — Der Rückweg:** Das Ergebnis eines Zimmers geht über den Code in das
Thema dieses Zimmers. Eine Kurzfassung wandert zusätzlich in den Kontext der
Sekretärin, damit sie den Stand kennt.

## Auftrag 4 — Der Multisession-Knopf

Ein Schalter je Person, wie Modell und Sprachausgabe, in den Prefs gespeichert
und nach Neustart erhalten.

- **Aus** = die klassische Arbeitsweise, alles ein Faden.
- **An** = je Zimmer eine eigene Sitzung, Sekretärin am Empfang.

Der Wechsel wirkt auf neue Aufträge; laufende Fäden bleiben unberührt. Der
Startreport nimmt den Schalter in seine Statuszeile auf, und der Moduswechsel
meldet sich als Stichpunktliste mit Haken und Kreuzen.

## Auftrag 5 — Haushalt

- **Das Kontingent bleibt je Person, nicht je Zimmer.** `[GEÄNDERT 09.09.,
  Engywuck]` Messung, Warnung und Rücklage bei erreichtem Limit hängen am Konto
  und werden nicht je Zimmer nachgebaut — vier Zimmer sähen sonst vier
  Teilbilder desselben einen Kontingents, und keines davon wäre richtig. Der
  vorhandene Weg über `RateLimitEvent` bleibt, wie er ist.
- Obergrenze gleichzeitig wacher Zimmer — eine Zahl **je Person**, die begrenzt,
  wie viele ihrer Zimmer zugleich rechnen. **Startwert drei bis vier, aus einer
  Probe zu bestimmen**, nicht aus Wunschdenken: Wie viele parallele Anfragen
  trägt das Abo, bevor gedrosselt wird? Die Probe gehört in den Bau.
- Einschlafen nach Leerlauf, Startwert 30 Minuten; Wecken beim nächsten Auftrag.
- **Die Sekretärin schläft nicht.** Sie ist der Empfang; ein schlafender Empfang
  hebt den Zweck auf.
- Greift die Drossel, wird das gemeldet. Ein stilles Schlangestehen sieht von
  außen wie Ruhe aus.

## Auftrag 6 — Protokoll je Zimmer und Leitstand

Jedes Zimmer schreibt seine eigene Protokolldatei, sofort, mit der vorhandenen
Logger-Mechanik (`ConversationLogger`, `bot.py:1389` ff.). Der Leitstand liest
die Gesamtsicht und beantwortet: welche Zimmer wach sind, woran sie arbeiten,
seit wann, was zuletzt fertig wurde.

Abrufbar per Befehl (etwa `/zimmer`). Jede Meldung trägt ihren Antwortweg — eine
Frage ohne Wirkung wird nicht gestellt.

**Der Leitstand ist zugleich die Quelle für den Kontext der Sekretärin** aus
Auftrag 2. Er wird einmal gebaut und zweimal genutzt.

**Grenze, die genannt gehört:** Echtzeit gilt lokal auf dem Server. Wer aus dem
Log-Repo liest — etwa die Mac-Sitzung —, sieht weiterhin den Stundentakt.

## Auftrag 7 — Zimmerfunk und gemeinsames Wissen

**Zimmerfunk:** Nachrichten von Zimmer zu Zimmer und an den Leitstand über das
bewährte Postfach-Muster, eine Ebene tiefer — ein lokaler Austauschordner auf
dem Server, Zustellung in Sekunden.

**Gemeinsames Wissen:** Eine geteilte Regel-Ablage, die jede Zimmer-Sitzung beim
Start liest. Der Weg hinein führt über eine **Sammelstelle**: Ein Zimmer legt
ein Learning als Vorschlag ab, die Aufnahme geschieht an einer Stelle. Schrieben
alle Zimmer direkt hinein, entstünden Widersprüche, die niemand bemerkt.

---

## Was bei der Person bleibt

Freigaben, Modellwahl, Sprachausgabe, dauerhaft erlaubte Werkzeuge und der
Multisession-Schalter gelten je Person. Sonst erteilt Adam dieselbe Freigabe
viermal.

## Sichtbarkeit

Heute läuft alles über Adams Zugang; zwischen den eigenen Zimmern gibt es kein
Vertraulichkeitsproblem, die Ampel steht auf grün. Die Leitplanke für später
kostet jetzt einen Schalter: **ein Sichtbarkeits-Flag je Zimmer, Standard
„teilen".** Führt ein Zimmer echte Klientendaten — angelegt ist dafür „Kunden &
Piloten" im Nirgendhaus —, wird es auf „privat" gestellt: sein Faden bleibt aus
dem gemeinsamen Wissen draußen, Zimmerfunk heraus nur nach Freigabe. Unverändert
gilt: Rote Inhalte gehören nicht im Klartext über Telegram.

---

## Entschieden und noch offen

**Entschieden am 09.09.:** Die Sekretärin läuft auf **Sonnet 5**, die Zimmer auf
dem höchsten verfügbaren Modell — als Standardwert **je Rolle**, jederzeit
umschaltbar. Das ist eine bewusste Ausnahme von Adams Grundregel „immer das
höchste Modell": Der Empfang wird an Geschwindigkeit gemessen, und das
Kontingent, das er nicht verbraucht, steht den Zimmern zur Verfügung.

**Noch offen: die Obergrenze wacher Zimmer.** Sie steht erst nach der
Parallel-Probe fest, wird gemessen und dann eingetragen.

---

## Was kann brechen und wer merkt es

| Bruchstelle | Folge | Prüfer |
|---|---|---|
| Sekretärin ohne eingespeisten Stand | sie erfindet Auskünfte über die Zimmer | Testfall: Zimmer arbeitet, Frage an den Empfang, Antwort muss den echten Stand nennen |
| Zu viele wache Zimmer | Kontingent schwindet, Anthropic drosselt | Obergrenze plus Leitstand-Anzeige; Drosselung wird gemeldet |
| Stall-Wächter misst je Person | ein hängendes Zimmer gilt als lebendig, weil ein anderes tippt | Umstellung auf Zimmer-Messung, mit Testfall |
| Zwei Freigabe-Dialoge aus zwei Zimmern | Knöpfe ohne Faden-Kenntnis vertauschen die Antworten | Testfall: zwei offene Fragen, kreuzweise beantwortet |
| Übergabe an ein unbekanntes Zimmer | ein Auftrag verschwindet still | Regel 3: Rückfall in den Hauptfaden mit benannter Adresse |
| Eingeschleuster Auftrag aus zitiertem Fremdtext | fremder Text löst eine Handlung aus | typisiertes Werkzeug statt Textmarker; Testfall: eine Nachricht, die den Aufruf wörtlich zitiert, darf nichts auslösen |
| Gemeinsames Wissen als Schreib-Freifahrt | Widersprüche ohne Prüfer | Sammelstelle als einziger Schreibweg |
| Ein Zimmer stirbt still | niemand merkt es | Leitstand zeigt „seit X ohne Lebenszeichen" |
| Sync-Verwechslung | jemand hält das Log-Repo für Echtzeit | wird benannt, wo es jemanden betrifft |

Die Fehlerklasse, auf die zuerst zu sehen ist: **ein Ausbleiben, das wie Ruhe
aussieht** — eine Meldung, die nie kommt, ein Auftrag, der nie ankommt, ein
Zimmer, das nie antwortet.

## Gut genug, wenn

- Zwei Zimmer antworten nachweislich gleichzeitig, mit der Stoppuhr an zwei
  parallelen Fragen gemessen.
- Die Sekretärin antwortet, **während** ein Zimmer rechnet, und nennt dabei
  richtig, woran das Zimmer arbeitet.
- Eine Nachricht in ein beschäftigtes Zimmer bekommt binnen Sekunden eine
  Zwischenantwort und steht trotzdem in dessen Reihe.
- Ein Auftrag wandert über die typisierte Übergabe aus dem Empfang in ein
  Zimmer, wird dort abgearbeitet, und das Ergebnis kommt im richtigen Thema an.
- Eine Nachricht, die einen Übergabe-Aufruf **wörtlich zitiert**, löst nichts
  aus und wird als Text ausgeliefert.
- Der Knopf schaltet beide Richtungen; der Startreport zeigt seinen Stand.
- Der Leitstand zeigt die wachen Zimmer korrekt, die Obergrenze greift sichtbar.
- Ein Learning wandert aus Zimmer A über die Sammelstelle in die gemeinsame
  Ablage und ist in Zimmer B beim nächsten Start präsent.
- Der Stall-Wächter meldet ein absichtlich aufgehängtes Zimmer, während ein
  anderes weiterarbeitet.

## Reihenfolge `[GEÄNDERT 09.09., Engywuck]`

1. **Kern** — Schlüssel-Umbau, Knopf, Haushalt. Danach arbeiten die Zimmer
   nebeneinander.
2. **Sicht** — Protokoll je Zimmer und Leitstand. **Vor der Sekretärin**, weil
   der Leitstand die Quelle ihres Kontexts ist.
3. **Empfang** — Sekretärin, Verteiler, typisierte Übergabe. Sie startet damit
   auf einem Stand, den sie nennen kann.
4. **Verbund** — Zimmerfunk, gemeinsames Wissen mit Sammelstelle.
5. **Feinschliff** nach dem Anlegen der Telegram-Gruppen: Routing, Hausschilder,
   General-Bereiche.

**Meine erste Fassung hatte die Sekretärin in Schritt 1 und den Leitstand in
Schritt 2** — während dieselbe Fassung „Sekretärin ohne eingespeisten Stand" als
erste Bruchstelle führte. Engywucks Umstellung räumt den Widerspruch aus.

Der Schnitt in vier Baublöcke bei Mick geht vor dieser Aufzählung; sie sagt die
Abhängigkeiten, nicht die Arbeitspakete.

**Die Abschnitte 1 bis 3 brauchen die Häuser nicht.** Ein bestehendes Thema mit
`thread_id` genügt zum Bauen und Prüfen; der Hauptchat tut es auch. Die Häuser
liefern später nur mehr Adressen.
