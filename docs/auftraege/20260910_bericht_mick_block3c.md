> **Zweck: WEITERGABE → Engywuck** (Nachprüfung, danach **ein** Deploy) ·
> **Zu tun:** Prüfen auf `f82de14`. Danach Deploy von Block 3 gesamt und
> `/empfang an` mit der Prüfzeile.

# Block 3c — Commit `f82de14`

**Stichtag:** 10.09.2026, 23:1x · **Abendblock, 22:07 bis 23:20** ·
**Nenner:** 6 Punkte deiner Liste, **5 vollständig, 1 zur Hälfte** (F-22, siehe
unten) · Prüfzeilen: Block 1 **47** (von 40), Block 2 **33**, Block 3 **104**
(von 60), Freigabeweg **11** (von 6), Wachposten +1 · Regressionslauf 80/80.

## Die zehn blinden Prüfzeilen — jede einzeln nachgestellt

**E1b, und er war der wichtigste.** Ein Kommentar `# Hauptfaden:` entwaffnete
zwei Zeilen. Gemessen wurde, dass jemand etwas **behauptet** — nicht, dass es
stimmt.

Statt eines ausgeführten Nachweises habe ich die **Bauform** genommen, die du
als Alternative nanntest: **kein Ein-Argument-Aufruf mehr, Punkt.** Es kostete
vier Zeilen — so viele Stellen gab es. Wer den Hauptfaden meint, schreibt
`thread_id=None` hin; das ist dieselbe Aussage, nur im Code statt im Kommentar,
und sie lässt sich nicht behaupten, sondern nur setzen. Deinen Fall
nachgestellt (`ensure_session(user_id)` plus Kommentar): **zwei rote Zeilen**,
vorher 40/40 grün.

**E4** — pyflakes über `scripts/`, als Menge. Der erste Lauf fand sofort einen
echten undefinierten Namen **in meinem eigenen Prüfer von zwei Stunden vorher**.

**A5-1** — der Haushalt an der Aufrufstelle, ausgeführt: Arbeiter und Wächter
laufen wirklich. Beide Schleifen totgelegt → drei rote Zeilen.

**E2** Hook ausgeführt statt gezählt · **E6** der Server nennt sein Werkzeug
statt nur seinen Schlüssel · **E9** der echte Logger-Weg statt selbstgebauter ·
**E5** der Wachposten **liest** beide Quellen, nicht nur seine Liste stimmt ·
**E3b** die Protokollzeile als Datensatz gelesen (das alte `or "dialog" in
inhalt` war fast immer wahr) · **E8** der Bash-Zweig wird gefahren · **E10** der
Dialog wird mit einem Faden gefahren.

**Eine Nebenlehre, zweimal aufgetreten:** Ein Bruch im geprüften Pfad ließ den
Prüfer **abstürzen** statt rot zu werden — und ein abstürzender Prüfer verdeckt
alles darunter. Beide Stellen fangen ihn jetzt ab und machen daraus eine Zeile.

## A-6 — eine Tür je Zustand

`vorlesen_setzen` und `dauerfreigabe_merken` setzen Vorlieben **und** alle
offenen Sitzungen. Die Reparatur war nicht, die zweite Stelle nachzuziehen:
Dann gäbe es wieder zwei, die dasselbe wissen müssen.

**Der Prüferlauf hat mir dabei etwas gemeldet, bevor ich es bemerkt habe:**
`_set_bash_auto` kann eine Freigabe auch **zurücknehmen** — meine erste Tür
konnte nur hinzufügen, also wäre sie eine zweite Tür geblieben. Die
Mengen-Zeile („niemand setzt den Zustand an der Tür vorbei") fand es.

## 3c-1 und 3c-2 — deine beiden Punkte aus der 3b-Nachprüfung

**Der weitergereichte Auftrag überlebt den Neustart.** Schlüssel aus
`zettel_id`, negativ und damit kollisionsfrei; die Kennung wird jetzt **immer**
vergeben, nicht nur bei besetztem Zimmer.

**Und eine falsche Prüfzeile von mir, von der Gegenprobe gefunden:** Meine
erste Fassung baute den Job **selbst** aus dem Datensatz. Entfernte man
`zettel_id` aus dem echten Reconcile, blieb sie grün — genau die Klasse aus
deinem Abschnitt P, mitten im Block, der ihn abarbeiten soll. Jetzt läuft der
echte Reconcile.

**presend** angeschlossen, halb, wie beschlossen. Deine Begründung trug weiter
als meine: Ich hatte auf die fehlende Warteschlange gesehen, du auf den
Befehlsblock, den sie Adam schreiben kann.

## F-22 — die eine Hälfte, die heute schon schadet

**Gebaut: der Chat im Registerschlüssel.** `message_id` ist nur je Chat
eindeutig; Nummer 42 im Privatchat und 42 in einer Gruppe waren **derselbe
Eintrag**. Ein Auftrag aus dem einen Chat konnte den Zwilling des anderen als
„schon beantwortet" überspringen lassen — **Adams Nachricht wäre spurlos
verschwunden.** Auch der Dateiname trägt den Chat, denn der Hauptfaden-Ordner
deckt Privatchat und Gruppen zugleich ab.

**NICHT gebaut: der volle Schlüsselwechsel.** `chat_id` in Sitzung,
Warteschlange und Arbeiter. **Gemessen, nicht geschätzt:** 80 Aufrufe der
sieben Türen, 26 Schlüsselzugriffe, 16 Registerstellen. Das ist die Größe von
Block 1 — der einen ganzen Block gekostet und mit 1b eine Nachbesserung
gebraucht hat.

**Ich habe ihn nicht um halb zwölf nachts angefangen.** Ein halbfertiger
Schlüsselwechsel ist schlimmer als keiner, und die Klon-Probe (R4) gehört
dazu. Er ist ein eigener Block, und ich schlage vor: **vor dem ersten Haus**,
wie ursprünglich als F-22 vermerkt — der Deploy von Block 3 braucht ihn nicht.

## Was der Deploy jetzt braucht

Ein Stand: **`f82de14`**. Er enthält Block 3, 3b, 3c und den Hotfix. Der
Empfang steht auf **aus**; die Prüfzeile nach dem Einschalten steht im
Deploy-Block.

**Die eine Messung, die nur der Betrieb liefert**, bleibt unverändert offen: ob
die Oberfläche der Sekretärin ihr Werkzeug wirklich anbietet.

## Nebenbei, gehört in den Bericht

**Der achte Fall der Anführungsregel — und der gefährliche Teil trat ein.** Ein
Skript starb an einem gemischten Paar, und der `git commit` in der **nächsten
Zeile** lief trotzdem: Ein Zeilenumbruch trennt nicht. Die Commit-Nachricht
behauptete einen Register-Eintrag, den es nicht gab; ich habe ihn nachgetragen
und die Regel geschärft — **kein `git commit` im selben Aufruf wie eine
Dateiänderung**, nicht nur nicht verkettet, sondern nicht daneben.

Dazu Connis Auftrag zu den bash-Schaltern: erledigt, Befund im neuen
`docs/fremdflaechen-inventar.md`. **Das Backup ist nicht ausgefallen** — zwei
Läufe heute, keine Lücke seit dem 1. September.
