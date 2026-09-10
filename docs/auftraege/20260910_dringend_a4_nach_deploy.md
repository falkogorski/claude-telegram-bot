> **Zweck: ENTSCHEID (Adam) + WEITERGABE → Engywuck** · **Zu tun:** Adam —
> zweiter Deploy heute, `606ce26`. Engywuck — kurze Sicht darauf; es ist der
> Teil von A-4, der **ohne den Knopf** wirkt.

# Der Deploy hat Block 3 mitgebracht — der Haushalt läuft, seit 14 Uhr

**Stichtag:** 10.09.2026, 13:56 (aus dem Commit abgelesen) · **Live seit dem
Deploy:** `9801c64` · **Behoben in:** `606ce26` · **Nenner:** 4 Punkte aus
A-4, alle vier gebaut · 60 Prüfzeilen · 3 Gegenproben · 80/80.

## Was übersehen wurde, und es ist ein Reihenfolge-Fehler, kein Codefehler

`merge --ff-only 9801c64` bringt **alles** mit, was auf dem Zweig davor liegt
— also `79d8ae4` (Empfang) und `d87dc64` (Haushalt). Der Ultracode-Befund sagt
„Block 3 nicht deployen"; die Nachprüfung sagt „Deploy 9801c64". Beides
zusammen geht nicht, und aufgefallen ist es niemandem, weil der **Knopf** die
Sicherheitsleine sein sollte.

**Der Knopf trägt den Empfang, nicht den Haushalt.** `darf_starten` und
`darf_einschlafen` laufen im Arbeiter und im Stall-Wächter — ohne jede Abfrage
auf `empfang_an`. Seit dem Neustart sind sie im Betrieb.

**Mein Anteil:** Ich habe den Haushalt in denselben Block gelegt wie den
Empfang und im Bericht geschrieben, der Knopf stehe auf aus und es ändere sich
zunächst nichts. Für den Empfang stimmt das. Für den Haushalt nicht.

## Was in diesen Stunden im Betrieb möglich war

1. **Der Hauptfaden schläft nach 30 Minuten Stille ein.** Adams
   Gesprächsfaden verschwindet — still, und im Protokoll steht „closed by
   /reset", was niemand ausgelöst hat. Das ist der wahrscheinlichste von den
   vieren: eine Mittagspause reicht.
2. **Drei offene Freigabe-Dialoge blockieren jedes weitere Zimmer** bis zu
   einer Stunde. Ein Dialog darf lange offen stehen — der Stall-Wächter lässt
   ihn ausdrücklich in Ruhe —, aber er zählte als *rechnendes* Zimmer. Ein
   🚦, dann Stille; weder Wächter noch Einschlafen greifen in diesem Zustand.
3. **Ein hängender Transport hätte den ganzen Wächter stillgelegt**, für alle
   Zimmer: `close_session` im Wächter hatte keine Zeitgrenze.
4. **Der Arbeiter wäre still gestorben**, wenn die Schlange während der
   Drossel-Wartezeit geleert wird (`popleft` auf leerer Schlange).

**Nichts davon verliert Daten, und keines ist eine Sicherheitslücke.** Aber
①  sieht wie Vergessen aus und ② wie ein Hänger — beides Fehlerklassen, die
wie Ruhe aussehen.

## Behoben in `606ce26`

- **Der Hauptfaden schläft nicht ein** (Adams Entscheid ①). Zimmer schlafen
  weiter, **und beim Einschlafen geht eine Zeile an Adam** — ohne
  `parse_mode`, denn im Zimmernamen steckt Adams Ablage.
- **Wer auf eine Freigabe wartet, rechnet nicht** und zählt nicht gegen die
  Grenze.
- **`close_session` im Wächter mit Zeitgrenze** (20 s, wie
  `_disconnect_quietly` daneben seit jeher). Läuft sie ab, wird der Eintrag
  entfernt und der Wächter läuft weiter.
- **`popleft` prüft die Schlange erneut**, nach dem Warten und vor dem Zugriff.
- Dazu vereinheitlicht: **`ZIMMER_SCHLAF_NACH_S=0` heißt AUS**, wie
  `ZIMMER_GLEICHZEITIG=0`. Zwei Schalter mit derselben Null und
  entgegengesetzter Wirkung sind eine Falle, die genau einmal zuschlägt.

**Nebenbei, und es gehört in den Bericht:** `pyflakes` hat beim Bauen einen
`NameError` gefangen, bevor er committet war — ein Sentinel, der erst weiter
unten im Modul definiert ist. Genau die Klasse vom 09.09., diesmal vor dem
Commit. Der Prüfer von gestern hat sich heute bezahlt gemacht.

## Der Deploy-Block

```bash
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git merge --ff-only 606ce26 && bash scripts/regressionstest.sh > /tmp/reg.log 2>&1; echo "rc=$?"; tail -6 /tmp/reg.log'
```

```bash
ssh claudevps 'systemctl restart claude-telegram-bot && sleep 5 && systemctl is-active claude-telegram-bot'
```

**Prüfzeile danach, und sie braucht Geduld:** Schreib etwas im Hauptchat, lass
den Chat **über eine halbe Stunde** ruhen, schreib dann wieder. Der Bot muss
den Faden noch haben (kein „ich beginne frisch"). Ein **Zimmer** darf in
derselben Zeit einschlafen — dann kommt dort die 💤-Zeile.

**Der Rest von Block 3b** (A-1 Lebenszyklus des Empfangs, A-2 Ziel und
Persistenz, A-3 Fremdtext-Riegel, A-5 Meldungen ins Zimmer) liegt teils
gebaut, teils offen und **wartet auf den nächsten Push** — er berührt nur den
Empfang, und der steht auf aus.
