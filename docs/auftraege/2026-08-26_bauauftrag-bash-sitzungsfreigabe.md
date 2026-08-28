# Bauauftrag: Bash-Freigabe für die laufende Sitzung umschaltbar machen

**Stichtag:** 2026-08-26 · **überholt durch:** — · **maßgeblich ist diese Datei**

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau).

**Anlass:** Adam am 26.08.2026 um 11:55 Uhr. Er möchte einen Menü-Befehl, der
zwischen „Bash manuell" und „Bash automatisch" umschaltet, sodass Bash für die
**laufende Sitzung** dauerhaft akzeptiert wird. Begründung wörtlich: Bei
Bauaufträgen sei ohnehin klar, dass alles sicher ist — „ich muss jetzt tausend
Mal drücken bei solchen Prozessen hier und das muss ja nicht sein." Mit einer
neuen Sitzung soll es sich von selbst wieder auf manuell stellen.

---

## Erster Befund: Die Mechanik existiert bereits — mit der falschen Lebensdauer

Vor dem Bauen wurde nachgesehen, ob es das schon gibt. Es gibt es.

Der Freigabedialog hat neben „Erlauben" und „Ablehnen" einen dritten Knopf,
`always:`. Er trägt das Werkzeug in `sess.always_allowed_tools` ein — und
zusätzlich in `prefs["always_allow"]` **auf die Platte** (`bot.py`, Zeile 2986
folgend, Vermerk „5.25 (c): dauerhaft merken — überlebt Reset/Neustart").

**Gemessen im Bestand:** In Adams Einstellungen steht heute genau ein Eintrag,
`Read`. Bash ist nicht dabei — deshalb die vielen Rückfragen.

**Daraus folgt der eigentliche Punkt:** Würde Adam bei der nächsten
Bash-Rückfrage einfach „Immer erlauben" drücken, wäre Bash **für immer**
freigegeben, über jeden Neustart hinweg. Das ist genau das, was er *nicht*
will. Sein Wunsch ist die **flüchtige** Variante derselben Mechanik.

Der Auftrag ist damit kleiner als gedacht: **kein neuer Freigabeweg, sondern
eine zweite, sitzungsgebundene Liste neben der dauerhaften.**

## Zweiter Befund: Der Schutz bleibt von selbst erhalten — wenn richtig angedockt

Die bestehende Prüfung lautet (Zeile 2840):

```
if (tool_name in sess.always_allowed_tools
        and tool_name not in _NO_ALWAYS_TOOLS and not sensitive):
    return PermissionResultAllow()
```

Entscheidend ist `not sensitive`. Die Einstufung stammt aus
`_is_sensitive_ref` und greift **vor** jeder Dauerfreigabe: Befehle, die auf
Geheimnisse zielen (`.env`, `printenv`, verschleierte Schreibweisen wie `.[e]nv`,
Platzhalter, die einen Geheimnis-Namen buchstabieren) oder auf Pfade mit
Dauerwirkung, gehen weiterhin in den Dialog.

**Auflage daraus:** Der neue Schalter wird eine **weitere Bedingung an genau
dieser Stelle**, unterhalb der Sensibilitätsprüfung — niemals davor und niemals
über `permission_mode`. Der Riegel bleibt `can_use_tool`, wie es der Vermerk bei
Zeile 3354 ausdrücklich festhält.

---

## Der Sicherheitsvorbehalt, der vor das Bauen gehört

Adam hat entschieden, und die Begründung trägt: Bei einem Bauauftrag weiß er,
was läuft. Trotzdem gehört das Risiko benannt, bevor gebaut wird.

**Eine pauschale Bash-Freigabe verschiebt die Angriffsfläche.** Solange Adam
jeden Befehl sieht, ist er der Prüfer. Fällt das weg, läuft ein eingeschleuster
Befehl ohne Rückfrage — und eingeschleust werden kann er über jeden Inhalt, den
die Sitzung liest: eine Webseite, eine weitergeleitete Nachricht, eine Datei,
eine Fehlermeldung eines fremden Werkzeugs.

Die Sensibilitätsprüfung fängt davon einen Teil, aber nicht alles. Sie zielt auf
Geheimnisse und Dauerwirkung. Sie fängt **nicht**: Löschen (`rm -rf`),
Rechteänderungen (`chmod`, `sudo`), Netzabrufe, die ihr Ergebnis ausführen
(`curl … | bash`), Veröffentlichen (`git push`), Dienststeuerung
(`systemctl`).

**Deshalb drei Auflagen, ohne die der Schalter nicht gebaut werden sollte:**

1. **Rot-Wort-Bremse.** Eine kurze, benannte Liste zerstörerischer oder nach
  außen wirkender Befehlsmuster bleibt **immer** rückfragepflichtig, auch im
  Auto-Modus. Vorbild und möglicherweise wiederverwendbar: die Rot-Wort-Liste
  im Auftragsbuch, die dort denselben Zweck erfüllt. Die Liste ist kurz zu
  halten — eine lange Liste erzeugt Dialoge, wo der Schalter gerade welche
  sparen soll.
2. **Zeitablauf zusätzlich zum Sitzungsende.** Adam spricht von „dem ganzen
  Prozess". Ein Prozess dauert Minuten bis Stunden, eine Sitzung kann Tage
  laufen. Vorschlag: **60 Minuten**, danach still zurück auf manuell, mit einer
  Zeile Meldung. Das ist mein Vorschlag, keine Vorgabe Adams — er kann jede
  andere Dauer setzen oder den Ablauf streichen.
3. **Nicht auf die Platte.** Der Zustand lebt ausschließlich in der Sitzung
  (`UserSession`), nicht in `prefs`. Das ist zugleich Adams ausdrücklicher
  Wunsch und die Sicherung: Ein Neustart, ein `/reset`, ein Absturz — jedes
  Mal steht der Schalter wieder auf manuell. **Genau hier unterscheidet sich
  der neue Weg vom vorhandenen.**

---

## Auflage

### (1) Zustand in der Sitzung

In `UserSession` ein Feld ergänzen, etwa `bash_auto_bis: float | None = None` —
der Zeitpunkt, bis zu dem der Auto-Modus gilt. `None` heißt manuell. Ein
Zeitstempel statt eines Ja-Nein-Schalters, damit der Ablauf aus (2) ohne
Zeitgeber auskommt: Er wird bei der nächsten Anfrage einfach mitgeprüft.

### (2) Prüfung im Freigabeweg

In `can_use_tool`, **unter** der Sensibilitätsprüfung und neben der
bestehenden Always-Zeile: Ist das Werkzeug `Bash`, ist der Auto-Modus nicht
abgelaufen, greift keine Rot-Wort-Bremse und ist der Aufruf nicht sensibel →
`PermissionResultAllow()`. Sonst wie bisher in den Dialog.

Ist der Zeitpunkt überschritten, wird das Feld beim selben Durchgang auf `None`
gesetzt und Adam bekommt eine Zeile: der Auto-Modus ist abgelaufen, es wird
wieder gefragt. **Stillschweigend zurückfallen wäre der schlechtere Weg** — er
sähe aus wie ein Fehler des Schalters.

### (3) Menü-Befehl

Ein Befehl, Vorschlag `/bash`, der zwischen den beiden Zuständen umschaltet und
den neuen Zustand bestätigt — mit Restdauer, wenn er eingeschaltet wird. Die
Bestätigung ist Pflicht, nicht Zierde ([[feedback-command-confirmation]]).

Beim Einschalten gehört ein Satz dazu, was weiterhin gefragt wird: Geheimnisse
und die Rot-Wort-Liste. Sonst entsteht der Eindruck, es sei alles offen.

### (4) Sichtbarkeit im Startbericht

Der Zustand gehört in den Status-Block des Startberichts, neben Modell und
Sprachausgabe. Regel: Jede neue umschaltbare Option wird dort mit aufgenommen.
Da er bei jeder neuen Sitzung ohnehin auf manuell steht, ist die Zeile im
Normalfall unauffällig — sie fällt nur auf, wenn etwas nicht stimmt.

---

## Was kann brechen und wer merkt es

- **Der Schalter dockt versehentlich über der Sensibilitätsprüfung an.** Dann
  liefe `cat .env` ohne Rückfrage. Merkt: niemand, bis es passiert. **Das ist
  der gefährlichste Fall dieses Auftrags.** Gegenmittel: ein Prüfer, der die
  Reihenfolge im Quelltext festschreibt — genau so, wie es Zeile 7231 heute
  schon für `sensitive = _is_sensitive_ref` tut. Dieser Prüfer ist Teil des
  Auftrags, nicht optional.
- **Der Zustand landet doch in `prefs`.** Dann überlebt er den Neustart und
  Adams ausdrückliche Bedingung ist verletzt. Merkt: niemand — ein stiller
  Fehlschlag, der wie Bequemlichkeit aussieht. Gegenmittel: ein Prüfer, der
  belegt, dass nach einem simulierten Neustart der Schalter auf manuell steht.
- **Die Rot-Wort-Liste wird zu lang.** Dann fragt der Bot im Auto-Modus doch
  ständig, und der Schalter ist wertlos. Merkt: Adam sofort, im Alltag.
- **Die Rot-Wort-Liste wird zu kurz oder umgangen** (`r''m`, Variablen,
  Umwege). Merkt: niemand. Ehrliche Grenze: Eine Textprüfung auf Befehle ist
  nie vollständig — sie ist eine Bremse, kein Tor. Deshalb der Zeitablauf als
  zweite, von der Texterkennung unabhängige Sicherung.
- **Der Zeitablauf greift mitten in einem langen Bauauftrag.** Dann steht der
  Vorgang und wartet auf einen Klick. Ärgerlich, aber harmlos — und Adam sieht
  die Meldung. Er kann jederzeit neu einschalten.

---

## Was dieser Auftrag NICHT tut

- Er ändert **nichts** an der bestehenden dauerhaften Freigabeliste. `Read`
  bleibt, wie es ist.
- Er berührt `permission_mode` nicht. Der Modus bleibt `default`, der Riegel
  bleibt `can_use_tool`.
- Er gibt **kein** anderes Werkzeug frei. Nur Bash.

## Verhältnis zum Freigabedialog-Auftrag vom 25.08.

Der gestrige Auftrag betrifft die **Verständlichkeit** des Dialogs, dieser
seine **Häufigkeit**. Sie widersprechen sich nicht, berühren aber dieselbe
Stelle im Quelltext. Wer beide baut, sollte sie in derselben Runde anfassen —
sonst arbeitet der zweite gegen die Änderungen des ersten.
