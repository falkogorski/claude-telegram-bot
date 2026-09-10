> **Zweck: WEITERGABE → Engywuck** (Nachprüfung des Klons) **+ ANSICHT** (Adam)
> · **Zu tun:** Engywuck prüft den Zweig `probe-f22`, Commit `ce5663b`.
> **Kein Deploy** — der Zweig ist nicht gemergt, `mac-produktivstand` ist
> unberührt.

# Morgenbericht — F-22 voll, im Klon

**Stichtag:** 11.09.2026, 02:5x · **Nachtblock, 23:40 bis 02:55** ·
**Zweig:** `probe-f22`, Commit `ce5663b` · **Hauptbaum unverändert** auf
`0f4087e` · **Nenner:** 80 Tür-Aufrufe, 27 Index-Zugriffe, 9 Prüfstände —
alle umgestellt · Regressionslauf im Klon **80/80** · 1 Gegenprobe.

## Was gebaut ist

**Der Faden ist ein benannter Typ mit drei Feldern:** Person, Chat, Thema.

Bis gestern fielen Privatchat, der General-Bereich einer Forum-Gruppe und
jede normale Gruppe auf **denselben** Schlüssel `(uid, None)` — eine Sitzung,
ein Protokoll, eine Warteschlange für drei verschiedene Orte.

**Benannt und nicht als längeres Tupel**, und das ist die eigentliche
Entscheidung: Ein Tupel wird über Zahlen gelesen (`fd[1]`). Beim Einfügen
eines Feldes zeigt jede dieser 27 Stellen still auf etwas anderes —
`fd.thema` kann das nicht. Der Unterschied zwischen einem Bruch, der auffällt,
und einem, der wie Ruhe aussieht.

**Und die Türen nehmen jetzt EINEN Faden statt zweier Zahlen.** Das ist der
Fix hinter dem Fix: Der Schlüssel ist ein **Wert**, den man weiterreicht,
statt zweier Teile, die man einzeln vergessen kann. Genau die Lücke, die
Block 1b so teuer gemacht hat — `_sess(user_id)` ohne zweites Argument war
der Hauptfaden, und weil `thread_id` einen Vorgabewert trug, lief jede
vergessene Stelle weiter, nur im falschen Zimmer. **Wer den Chat jetzt
weglassen will, findet keinen Weg.**

## Zwei echte Funde beim Umbau — beide vom Prüfstand gemeldet

**① Der Reaktions-Widerruf griff in den falschen Faden.** Er suchte die
Warteschlange über `sess.chat_id`; der Auftrag lag aber unter dem Chat, in
dem die **Reaktion** stand. Ohne Sitzung — oder mit einer ohne `chat_id` —
fand er den wartenden Auftrag nicht, und **der Widerruf lief still ins
Leere**: Adam nimmt seinen Daumen zurück, der Auftrag läuft trotzdem.

**② `zimmer_ziel` riet beim „Hauptchat", der Chat sei die Person.** In einer
Gruppe wäre der Auftrag der Sekretärin damit in einem Faden gelandet, den es
dort nicht gibt. Der Chat wird jetzt übergeben, nicht geraten.

Beide waren **vorbestehend** und hätten ohne den Schlüsselwechsel nicht
auffallen können — sie brauchten die Trennung, um sichtbar zu werden.

## Die Prüfzeile, die ihre Zusage gewechselt hat

Die Mengen-Zeile aus Block 1b hieß „kein Ein-Argument-Aufruf". Damals waren
Person und Thema zwei Zahlen, und ein fehlendes zweites Argument hieß: Faden
vergessen. **Jetzt ist ein Argument die richtige Form** — die alte Zeile hätte
ab sofort jeden Aufruf angeschwärzt.

Sie misst deshalb etwas anderes: **Keine Tür trägt noch einen `thread_id`-
oder `user_id`-Parameter.** Solange das gilt, kann keine Aufrufstelle den Chat
vergessen — nicht weil jemand daran denkt, sondern weil es keinen Weg gibt.

Dazu sechs neue Zeilen für den Schlüssel selbst: zwei Chats sind zwei Zimmer ·
dasselbe Thema in zwei Chats ist nicht dasselbe Zimmer · derselbe Ort bleibt
dasselbe Zimmer (Gegenrichtung) · der Faden nennt seine Teile beim Namen ·
getrennte Warteschlangen · getrennte Zettel-Ordner.

**Gegenprobe:** Chat aus dem Schlüssel entfernt → **vier rote Zeilen**.

## Was ich NICHT getan habe

**Kein Deploy, kein Merge.** Der Zweig steht für sich; `mac-produktivstand`
ist unberührt und trägt den Stand, der heute Nacht live gegangen ist.

**Keine Prüfung in der Zielumgebung (R1).** Der Klon zeigt Syntax- und
Logikbrüche, nicht die Umgebung des VPS. Das ist die Grenze, die wir seit dem
Fehlalarm des Start-Wächters kennen.

## Für die Nachprüfung, drei Stellen, die ich selbst am heikelsten finde

1. **`_run_job` und der Worker:** Sie packen den Faden in `user_id, chat_id,
   thread_id` aus. Wenn irgendwo noch eine dieser Variablen aus dem alten
   Umfeld stammt statt aus dem Faden, zeigt sie woanders hin.
2. **Der Reconcile** baut den Faden aus dem Datensatz (`chat_id` steht dort
   seit 5.2). Ein alter Datensatz ohne `chat_id` ergibt `chat=None` — das ist
   ein eigener Faden, kein Fehler, aber es sollte jemand gesehen haben.
3. **`_enqueue_reaction_job`** bildet den Faden mit `thema=None`. Reaktionen
   auf Zimmer-Antworten landen damit weiterhin im Hauptfaden des Chats —
   das war schon vorher so (dein Punkt aus Abschnitt B) und ist mit diesem
   Umbau **nicht** behoben.
