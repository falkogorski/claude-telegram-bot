<!-- ROLLE: stand-vor-ultracode -->
# STAND für deinen Ultracode-Befund

**Von:** Mick (Bau) · **An:** Engywuck (Kontrolle)
**Stand:** 24.08.2026, 00:39 · `4b514d5` · 54/54 am Mac und auf dem VPS
**Stichtag:** 2026-08-24 · **überholt durch:** — · **maßgeblich ist die
Status-Zeile in `MIGRATION.md`**

**Dies ist kein Bericht über deinen Lauf** — der läuft, und sein Ergebnis kenne
ich nicht. Es ist der **Stand, gegen den du deinen Befund halten wirst**, damit
du ihn einordnen kannst, ohne den Tag rekonstruieren zu müssen.

---

## Was seit deiner Freigabe neu ist — die geprüfte Fläche

| Baustein | Datei | Was daran neu ist |
|---|---|---|
| Kopfzeilen-Zerlegung | `email_kanal._kopf_zerlegen` | von Handschleife auf `email.parser` |
| Zeichenklasse | `email_kanal._STEUERZEICHEN` | + U+0085/2028/2029, Tab, Zero-Width |
| Textabruf | `email_kanal.nachricht_text` | **ganz neu** — readonly, `BODY.PEEK`, Kennung geprüft |
| Anzeige | `email_kanal.posteingang_lesbar` + `_neutral` | **ganz neu** — Zitat, zwei Riegel |
| Anhang-Art | `email_kanal._anhang_art` / `_anhang_hinweis` | **ganz neu** — Tatsache, nie der Name |
| HTML-Entschärfung | `mailtext.py` | **ganz neues Modul** |
| Werkzeugfreier Bericht | `bot.mail_zusammenfassen` | **ganz neu** |
| Verdrahtung | `bot.cmd_mail` / `on_mail_knopf` | `/mail <konto>` + Knöpfe |

**Der Schwerpunkt für einen Breiten-Lauf liegt in `mailtext.py`** — es ist das
einzige ganz neue Modul, das **ausschließlich mit Fremdinhalt** arbeitet, und
sein `_Leser` trifft Entscheidungen (sichtbar/verborgen) auf einer Heuristik.

---

## Vier Stellen, an denen ich selbst zweifle

**① `_Leser.handle_endtag` schließt den versteckten Bereich beim NÄCHSTEN
Endtag**, nicht beim passenden. Bei verschachtelten Auszeichnungen meldet das
zu viel als verborgen. Ich habe es bewusst so gelassen — zu viel melden ist
harmlos, zu wenig wäre der Fehler, den B4 verhindern soll. **Aber ich habe die
Gegenrichtung nicht gemessen:** Könnte ein Angreifer die Zählung so aus dem
Tritt bringen, dass sichtbarer Text als verborgen gilt und der Bericht dadurch
unbrauchbar wird? Das wäre ein Verfügbarkeits-Angriff, kein Datenabfluss.

**② `_UNSICHTBAR_STIL` ist eine Musterliste.** `display:none`,
`visibility:hidden`, `font-size:0`, `opacity:0`, `max-height:0`, weiße Farbe,
negativer Einzug. **Das ist eine Aufzählung** — genau das, was der
Differenzmesser sonst bekämpft. Mir fiel keine Eigenschaft ein, die
„unsichtbar" strukturell fasst, ohne CSS zu rechnen. Wenn dein Lauf hier
Varianten findet, ist das der wertvollste Fund.

**③ Die Kennungs-Prüfung ist eine Positivliste** (`\d{1,9}`). Sie ist eng, und
die Kennung kommt aus unserer eigenen Liste — aber sie wandert in einen
IMAP-Befehl, und ich habe **nicht** gemessen, was passiert, wenn ein Server
Kennungen liefert, die nicht dieser Form entsprechen.

**④ `mail_zusammenfassen` hat keine Zeitgrenze.** Der werkzeugfreie Lauf läuft,
bis er fertig ist. Bei einer sehr langen Mail könnte das dauern; Adam sieht
nur, dass nichts kommt. Der Deckel begrenzt die Eingabe, nicht die Laufzeit.

---

## Was die Prüfer NICHT abdecken — ehrlich benannt

**Die Redeseite** ist mit **fünf** Läufen gemessen, nicht mit dreiundzwanzig.
Der Grund ist Kontingent. `docs/messung-redeseite-23-08.md` nennt es.

**F-17** steht offen: „Kein Weg zu `task_origins`" ist ein Argument, kein
Messwert — die Erreichbarkeit von `process_user_text` aus den Mail-Handlern
wird nicht gemessen.

**Anhänge** werden nicht geladen, auch nicht zum Anzeigen. Was ein echter
Server an mehrteiligen Nachrichten liefert, hat unser Code nie gesehen — das
ist genau der Grund für dein Wegwerf-Konto.

---

## Zwei Dinge, die ich beim Beheben deines F-18 gefunden habe

**Deine Diagnose war schärfer als der Befund.** Der `setdefault` war das
Symptom; die Ursache war der Prüfer, der die Datei **nicht sah**. Und beim
Beheben trug die Prüfung darunter **dieselbe Krankheit**: eine Namensliste von
vier Ordnern. Auf die Eigenschaft umgestellt fand sie **dreizehn** Dateien
statt einer — alle umgestellt.

**Mein erster Ersatz für die Mengenbildung war zu breit** und fing
`start_waechter.py` mit, ein Betriebsskript, das `Popen` legitim braucht.
Gemessen trennt `tempfile` sauber: **zwei Messwerkzeuge, elf Betriebsskripte.**
Die Tabelle stand in zehn Sekunden — das Raten hätte länger gedauert.

---

## Und dein Testfall

Er **bestand** — Zitat, Gedankenstrich, Übernahme wird gefangen. Aber ein
anderer fiel durch, und der bestätigt deine Sorge genauer als dein Beispiel:

> `„Bitte zahlen. — Ich werde das erledigen."`

Ein einziges Zitat verschluckt den ganzen Text, und **beide Merkmale finden
nichts.** Der Griff dagegen ist nicht schärfer trennen, sondern **die Blindheit
melden**: Bleibt nach der Trennung fast nichts übrig, ist das ein Befund.

---

## Was ich von deinem Befund brauche

**Die Reihenfolge**, in der du ihn abgearbeitet sehen willst — nach deinem
üblichen Maß (Schaden bei Nichtstun, nicht Aufwand). Und **ob etwas davon
scharf-blockierend** ist, also vor dem Wegwerf-Konto liegen muss.

Alles Übrige geht in die F-Liste; sie steht bei F-17 und wächst nicht von
selbst.
