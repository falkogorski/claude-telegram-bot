# Bauauftrag — Der Dämpfer der Stundenblumen greift bei fast keinem Befund

**Für:** Mick (Migrationssitzung, Mac) · **Von:** Claudia (VPS-Bot-Sitzung)
**Stand:** 28.07.2026, 10:16 Uhr · **Anlass:** Adam wurde ab 09:51 Uhr im Minutentakt
mit je zwei Meldungen zugestellt.

**Zum Abgleich gedacht:** Adam hat dir denselben Vorfall gemeldet, du arbeitest bereits
daran und hast `stundenblume.timer` gestoppt. Dieses Papier ist die Diagnose vom Server
aus — nimm daraus, was deine Fassung noch nicht abdeckt, und verwirf den Rest. Conni
braucht nicht einbezogen zu werden (Adams Entscheidung, 10:06 Uhr).

---

## Änderungshistorie

**2026-07-28 10:16** — Abschnitt 7 überarbeitet: Hora bekommt die Standuhr 🕰️ statt des
Hibiskus; der Hibiskus 🌺 wandert zur Entwarnung der Stundenblume (Adams Bild von der weiter
aufgegangenen Blüte). Die erste Auslegung (Entwarnung mit Lotus und Häkchen) ist damit
hinfällig.
**2026-07-28 10:09** — Erstfassung.

---

## 1. Was Adam erlebt hat

Ab 09:51 Uhr kamen **zwei Nachrichten pro Minute**, unterschiedlichen Inhalts, zum
selben Zeitpunkt: eine Störungsmeldung und eine Entwarnung. Seine Worte: „Das muss
bitte schnell wieder aufhören. Das ist auf jeden Fall super nervig."

**Seine Leitplanke für die Behebung**, wörtlich sinngemäß (10:06 Uhr): *„Ein Warnsignal
muss nicht weg, aber das muss nicht ständig kommen."* Die Lösung darf den Wächter also
nicht leiser stellen, sondern nur seine Wiederholung.

## 2. Der Auslöser — harmlos, und deshalb lehrreich

Um 09:51:52 Uhr wurde die Zustell-Marke gesetzt:

```
{"zeit": 1785225112.08, "menschlich": "2026-07-28 09:51:52",
 "grund": "Telegram konnte vor 1 Minuten nicht zustellen: Connection refused",
 "adresse_unveraendert": true}
```

Ein einzelner abgewiesener Verbindungsversuch, mit hoher Wahrscheinlichkeit der
Bot-Neustart in genau diesem Augenblick. Die Zustellung lief danach durchgehend weiter —
Adam hat die Meldungen ja empfangen. **Der Anlass war ein Nichts. Der Lärm daraus war
das Problem.**

## 3. Befund 1 (Kern) — der Dämpfer schlägt auf den Wortlaut nach

`scripts/stundenblume.py`, `_daempfen()` ab Zeile 478:

```python
neu = [g for g in gruende
       if jetzt - float(bekannt.get(g, 0) or 0) >= WIEDERVORLAGE_S]
entwarnt = [g for g in bekannt if g not in gruende]
```

Der Schlüssel ist der **vollständige Meldetext**. Der Text der Zustell-Störung
(Zeile 218) lautet aber:

```python
return [f"📵 Zustellung gestört (seit {seit} Min): …"]
```

`seit` zählt jede Minute hoch. Damit ist der Ablauf zwangsläufig:

| Minute | Wortlaut | Folge |
|---|---|---|
| 10:00 | „seit 9 Min" | steht im Gedächtnis, schweigt |
| 10:01 | „seit 10 Min" | **unbekannt → Meldung** · „seit 9 Min" fehlt in `gruende` → **Entwarnung** |
| 10:02 | „seit 11 Min" | dasselbe, und so fort |

Das erklärt Adams Beobachtung **exakt**: zwei Nachrichten, unterschiedlichen Inhalts,
einmal je Minute. Die Bremse war vorhanden und hat ins Leere gegriffen.

### Der eigentliche Umfang — es ist nicht die Zustellung

Der Fehler betrifft **fast jeden Befund**, den es gibt. Alles mit einer mitzählenden
Zahl im Wortlaut ist betroffen:

| Quelle | Zeile | Mitzählender Teil |
|---|---|---|
| Zustell-Störung | 218 | `(seit {seit} Min)` |
| Ketten-Lücke | 454 | `Lücke von {luecke/60:.0f} Minuten` |
| Speicher eng (🔴) | 278 | `{verfuegbar} MiB … von {gesamt} MiB` |
| Speicher knapp (🟡) | 284 | dieselbe Bauart |
| Auslagerungsbereich (↔️) | 291 | `{swap_gesamt - swap_frei} MiB` |

Der Arbeitsspeicher schwankt bei jeder Messung um ein paar MiB. **Sobald er einmal unter
die Schwelle rutscht, entsteht derselbe Minutentakt** — nur mit einem anderen Text. Der
Vorfall von heute früh war kein Einzelfall, sondern die erste Gelegenheit, bei der ein
Befund lange genug angehalten hat.

### Vorhandener Test bestätigt das Muster nicht

`scripts/test_stundenblumen.py`, Zeile 401: `assert len(m) == 1, "derselbe Befund wurde
… gemeldet"`. Der Test schickt **zweimal denselben Wortlaut** und besteht deshalb. Der
realistische Fall — derselbe Befund mit fortlaufender Zahl — wird nicht geprüft.

### Empfohlene Behebung: stabile Kennung statt Wortlaut

Jeder Prüfer liefert künftig ein Paar aus **Kennung** und **Text**; der Dämpfer schlägt
auf die Kennung nach und meldet den Text.

```python
# statt list[str] künftig list[tuple[str, str]]
def zustellung_pruefen() -> list[tuple[str, str]]:
    ...
    return [("zustellung", f"🪷 Zustellung gestört (seit {seit} Min): …")]
```

Kennungen, je Befundart genau eine — **die beiden Speicherschwellen bekommen getrennte
Kennungen**, sonst verschluckt der Dämpfer die dringendere, wenn die mildere schon steht:

`zustellung` · `kette-luecke` · `speicher-eng` · `speicher-knapp` · `swap-benutzt` ·
`bot-prozess` · `anmeldung`

**Ausdrücklich nicht empfohlen:** den Wortlaut zu normalisieren, indem man Ziffern durch
einen Platzhalter ersetzt. Das wäre der Ein-Zeilen-Eingriff, aber „Nur noch 380 MiB"
und „Nur noch 720 MiB" fielen dann auf denselben Schlüssel — die letzte Warnung vor dem
Kippen käme nicht mehr durch. Der Kürzestweg wäre hier der gefährlichere.

**Zu ergänzender Test:** derselbe Befund mit fortlaufender Zahl, dreimal
hintereinander → genau **eine** Meldung, **keine** Entwarnung.

## 4. Befund 2 — ein alter Fehler gilt drei Stunden als laufende Störung

`zustellmarke.py`, `_befund()` Zeile 93:

```python
if fehler and (now - fehler_zeit) < FEHLER_FRISCH_S:      # 3 * 3600
```

Telegram behält `last_error_message` nach einem einzelnen Fehlversuch stehen. Der Code
wertet ihn drei Stunden lang als Störung, **ohne zu prüfen, ob seither erfolgreich
zugestellt wurde.** Bei einem Prüftakt von ebenfalls drei Stunden (`ZUSTELL_TAKT_S`,
`bot.py:76`) heißt das: Ein Neustart-Wackler von einer Sekunde hält die Marke bis zum
nächsten Prüflauf aufrecht — auch wenn in der Zwischenzeit hundert Nachrichten
angekommen sind.

**Behebung:** Den Beweis nehmen, der ohnehin vorliegt. Der Bot weiß, wann er zuletzt
erfolgreich gesendet hat — jede zugestellte Antwort ist einer. Liegt dieser Zeitpunkt
**nach** dem Fehlerzeitpunkt, ist der Fehler Geschichte:

```python
def _befund(info, jetzt=None, letzte_zustellung: float = 0.0):
    ...
    if fehler and (now - fehler_zeit) < FEHLER_FRISCH_S \
            and fehler_zeit > letzte_zustellung:
        ...
```

Damit bleibt der Wächter scharf für den echten Fall (nichts geht mehr raus), verstummt
aber beim Wackler. `FEHLER_FRISCH_S` kann unverändert bleiben.

## 5. Befund 3 — der Timer steht still, und das ist der gefährlichere Zustand

`systemctl list-timers` auf dem VPS, 10:10 Uhr:

```
stundenblume.timer   inactive        (von dir gestoppt)
hora.timer           active, nächster Lauf 10:16
```

Richtig als Sofortmaßnahme. **Aber:** Ein stehender Wächter sieht von außen genauso aus
wie ein zufriedener. Der 4-Uhr-Check meldet es — erst am nächsten Morgen. Deshalb gehört
zum Einspielen zwingend:

1. Fix aus Abschnitt 3 **vor** dem Wiederanschalten. Sonst geht der Lärm sofort weiter,
   nur mit der Lücken-Meldung („Die Kette hatte eine Lücke von X Minuten") — die zählt
   ebenfalls mit und trifft denselben Fehler.
2. `systemctl start stundenblume.timer` und den Start **verifizieren**, nicht annehmen.
3. Nach zwei Läufen prüfen, dass die Kette wieder wächst und **nichts** gemeldet wurde.

## 6. Was ich am VPS bereits getan habe

Damit du nicht doppelt räumst — beides um etwa 10:03 Uhr, ohne Repo-Eingriff:

- `~/.claude/zustellung-gestoert` entfernt. Eine Kopie liegt daneben als
  `zustellung-gestoert.abgeraeumt-<Zeitstempel>`.
- `~/.claude/stundenblumen/gemeldet.json` auf `{}` gesetzt, damit beim Wiederanlauf
  keine Entwarnungsflut ausgelöst wird.

**Offen gesagt, was das bedeutet:** Ich habe damit ein Warnsignal weggenommen. Vertretbar
war es, weil der Befund nachweislich veraltet war — die Zustellung lief, sonst hätte Adam
sich nicht über die Meldungen beschweren können. Der Wächter selbst bleibt scharf.

## 7. Emoji-Festlegung (Adam, 09:58 und 10:06 Uhr)

Adam legt die Zeichen verbindlich fest (Endstand 10:15 Uhr):

- **🪷 Lotusblüte** — die Stundenblume, wenn sie **aufgeht**: der neue Befund und die
  Anzeige beim manuellen Aufruf.
- **🌺 Hibiskus** — die Stundenblume in der **Entwarnung**.
- **🕰️ Standuhr** — Hora.

**Adams Bild dahinter, und es trägt:** Die Lotusblüte ist die beginnende Blüte, der
Hibiskus die schon weiter aufgegangene, gegen Ende ihres Lebens. Ein Befund, der entwarnt
wird, hat seinen Lauf vollendet — deshalb dort die geöffnete Blüte. Die beiden Zeichen sind
damit nicht zwei Farben für dasselbe, sondern zwei Lebensalter derselben Blume.

| Datei | Zeile | Anlass | bisher | künftig |
|---|---|---|---|---|
| `scripts/stundenblume.py` | 459 | neuer Befund | 🌼 | 🪷 |
| `scripts/stundenblume.py` | 462 | Entwarnung | 🌱 | 🌺 |
| `scripts/stundenblume.py` | 639 | Anzeige beim Aufruf | 🌼 | 🪷 |
| `scripts/hora.py` | 388 | Leerlauf-Meldung | 🌾 | 🕰️ |
| `scripts/hora.py` | 503 | Lauf-Bericht | 🌾 | 🕰️ |

Mehr Fundstellen gibt es nicht; ich habe das ganze Repo durchsucht. **Mehr Meldearten als
diese drei kennt die Kette nicht** — Befund, Entwarnung, Anzeige. Die Zuordnung ist damit
vollständig, es bleibt kein Fall offen.

**Zur Kenntnis, kein Einwand:** 🕰️ ist im System bereits vergeben — als Zeichen des
**Nirgendhauses** in der Kanalstruktur (`channels.py:34`, 6-6-Vorlage). Beides meint
Meister Hora, die Doppelung ist also stimmig und nicht verwechslungsgefährdet.

**Eine Auslegung, die ich getroffen habe:** Die Zustandszeichen bleiben unangetastet —
⏸️ 🔴 ✅ 🗝️ 🧪 ⏭️ 🔓 in Horas Bericht und 🟡 🔴 ↔️ 📵 in den Befunden markieren *was* los ist,
nicht *wer* spricht. Die Signatur steht vorn; die Zustandszeichen bleiben, wo sie stehen.

**Nicht vergessen:** Wenn ein Test oder der Tagescheck auf das alte Zeichen prüft, bricht
er still mit. Beim Umstellen mitsuchen.

## 8. Was kann brechen und wer merkt es

| Was schiefgehen kann | Woran man es merkt — und ob überhaupt |
|---|---|
| Zwei verschiedene Befunde teilen sich versehentlich eine Kennung | Der zweite wird **stumm** verschluckt. Von außen nicht zu sehen. → Test: zwei Befunde mit verschiedenen Kennungen gleichzeitig müssen **beide** durchkommen. |
| Der Zustellungs-Zeitstempel wird bei jedem *Versuch* gesetzt statt nur bei Erfolg | Der Wächter meldet **nie wieder** etwas — der stillste denkbare Ausfall. → Test mit simuliertem Dauerfehler: die Marke muss stehen bleiben. |
| Der Timer wird nach dem Einspielen nicht wieder gestartet | Kette steht, alle Anzeigen wirken ruhig. Der 4-Uhr-Check merkt es — **erst am nächsten Morgen**. → Nach dem Einspielen von Hand prüfen. |
| Ein künftiger Prüfer wird ohne Kennung ergänzt | Er fällt auf den alten Wortlaut-Weg zurück und lärmt wieder. → Die Signatur `list[tuple[str, str]]` erzwingen, nicht optional lassen. |
| Der Emoji-Tausch bricht einen Test, der auf 🌼 oder 🌾 prüft | Roter Testlauf, fällt sofort auf. Unkritisch, aber mitziehen. |

**Der gemeinsame Nenner aller fünf Zeilen:** Es ist nie ein Absturz, sondern **ein
Ausbleiben, das wie Ruhe aussieht.** Danach ist zuerst zu suchen, nicht nach Fehlern, die
sich melden.

## 9. Reihenfolge

1. Abschnitt 3 — Kennung statt Wortlaut, samt Test.
2. Abschnitt 4 — Zustellungsbeweis in `_befund()`.
3. Abschnitt 7 — Emojis.
4. Erst danach: `stundenblume.timer` wieder starten und den Start verifizieren.
5. Zwei Läufe später bestätigen, dass die Kette wächst und nichts gemeldet wurde.
