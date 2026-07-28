<!-- ROLLE: blinde-flecken-verfahren -->

# Das Blinde-Flecken-Verfahren

**Stichtag:** 28.07.2026 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile im Drehbuch** (Punkt B6)

---

## Wozu

Dieses Projekt hat einen Lieblingsfehler, und er hat immer dieselbe Signatur:
**ein Ausbleiben, das wie Ruhe aussieht.** Ein Prüfer überspringt still, was er
nicht kann. Ein Protokolleintrag wird geschrieben, den niemand liest. Eine
Vorgabe steht im Text und gilt im Code nicht. In allen drei Fällen meldet
niemand etwas — und genau deshalb hält man es für Ordnung.

Das Tückische daran: **Diese Fehler machen nichts kaputt.** Sie fallen in
keinem Test auf, sie erzeugen keine Fehlermeldung, sie kosten nichts. Sie
entwerten nur langsam das Vertrauen in jede Auskunft, die das System gibt.

Das Verfahren ist der Versuch, sie **planmäßig** zu finden, statt zufällig.

---

## Die drei Fragen

Sie werden an **jeden** Prüfer, Wächter und Automatismus gestellt — beim Bauen,
und noch einmal beim Abnehmen.

### ① Was prüft er NICHT — und weiß er das von sich?

Nicht „prüft er richtig", sondern: Gibt es Fälle, die er stillschweigend
überspringt? Unbekannte Arten, fehlende Quellen, verweigerte Rechte,
unerreichbare Systeme.

> **Der Prüfstein:** Wenn dieser Prüfer schweigt — heißt das „alles gut" oder
> „ich konnte nicht nachsehen"? Sind die beiden von außen ununterscheidbar,
> ist der blinde Fleck da.

**Belegte Fälle:**
- Der Versions-Monitor überging Register-Einträge mit unbekannter Art. Der
  Eintrag stand da, sah nach Abdeckung aus, wurde nie angesehen. *(Befund A)*
- `/updates` übersprang eine Komponente, sobald eine ihrer beiden Auskünfte
  fehlte. Adam las „✅ Alles aktuell", während der Eintrag ungeprüft dastand —
  derselbe Fehler wie oben, nur im Geschwisterpfad, wo ihn der erste Fix nicht
  erreicht hat. *(28.07.)*

**Die Abhilfe:** Der Prüfer meldet seine eigenen blinden Flecken mit — und
zwar **auch dann, wenn er sonst nichts zu melden hat.** Ein blinder Fleck, der
nur als Anhängsel an einen anderen Fund kommt, ist keiner, der gemeldet wird.

### ② Wer trägt ihn — und wer prüft den Träger?

Jeder Prüfer läuft auf etwas: einem Zeitgeber, einem Prozess, einem Dienst.
**Was ihn trägt, kann er nicht prüfen** — das ist keine Nachlässigkeit,
sondern die Grenze jeder Selbstprüfung.

> **Der Prüfstein:** Wenn das, was diesen Prüfer startet, ausfällt — wer
> merkt es?

**Belegter Fall:** Die Zeitgeber-Wache prüft jeden Zeitgeber, außer dem, der
sie selbst startet. Sie lebt im 4-Uhr-Check, und der läuft über einen
Zeitgeber. Stirbt ausgerechnet dieser, stirbt die Wache lautlos mit ihm.
*(Conni, 28.07.)*

**Die Abhilfe ist keine bessere Selbstprüfung, sondern eine zweite Instanz mit
eigenem Antrieb.** Die Stundenblumen laufen über einen eigenen Zeitgeber; sie
bewachen den Tagescheck, er bewacht über die Ketten-Prüfung sie.
**Kreuzverschränkung statt Selbstbezug.**

### ③ Steht seine Vorgabe im Text oder im Code?

Eine Regel, die nur beschrieben ist, gilt nur so lange, wie jemand an sie
denkt. *Eine Regel ohne Prüfer ist eine Bitte.*

> **Der Prüfstein:** Lies den Kommentar, dann lies den Code darunter. Sagen
> beide dasselbe?

**Belegte Fälle:**
- Über der Zeitgeber-Suche stand „DIE ZEITGEBER WERDEN GESUCHT, NICHT
  AUFGEZÄHLT" — und darunter ein Filter auf drei Namensanfänge. Eine
  Positivliste in Verkleidung. Ein neunter Zeitgeber mit anderem Namen wäre
  durchgefallen, und der Kommentar hätte behauptet, er sei abgedeckt.
  *(gefunden 28.07. bei genau dieser Prüfung)*
- Die Ausschluss-Regel im Log-Abgleich existierte — sie wurde nur nie
  nachgemessen. *(25.07.)*
- Die Register-Pflicht stand im Text, bis ein Prüfer sie einholte und beim
  ersten Lauf sofort eine Lücke fand. *(27.07.)*

**Die Abhilfe:** Wo eine Vorgabe Aufmerksamkeit verlangt, gehört ein Prüfer
dazu. Wo keiner möglich ist, gehört die Vorgabe klein gehalten.

---

## Zwei wiederkehrende Fallen

**Die Positivliste.** Jede Aufzählung dessen, was geprüft wird, ist ein
Versprechen, das mit dem nächsten Zuwachs bricht. Wo immer möglich wird
**gesucht statt aufgezählt** — und das Suchmerkmal muss eine Umbenennung
überleben. Bei den Zeitgebern ist es deshalb nicht der Name, sondern das Ziel:
*Was in unser Verzeichnis zeigt, ist unseres.*

**Der Geschwisterpfad.** Ein Fix wandert nicht von allein dorthin, wo dieselbe
Frage ein zweites Mal beantwortet wird. Nach jedem Fix werden die
Schwesterpfade **benannt** — nicht nur gedacht — und einzeln geprüft.

---

## Wann angewandt

- **Beim Bauen** jedes Prüfers oder Wächters: die drei Fragen durchgehen,
  bevor er als fertig gilt.
- **Bei der Gegenprüfung** durch eine frische Sitzung: sie sind der Kern des
  Auftrags „finde, was daran nicht trägt".
- **Beim Abschluss-Audit** (Phase 10) über den gesamten Bestand.

## Der Prüfer dazu

`scripts/test_blinde_flecken_b6.py` — er hält die Befunde fest, die dieses
Verfahren hervorgebracht hat, damit sie nicht ein zweites Mal entstehen.
Er kann das Verfahren nicht ersetzen: **Die dritte Frage lässt sich nur von
einem Leser beantworten, nicht von einem Programm.** Was er kann, ist die
konkreten Fallen bewachen, die wir schon kennen.
