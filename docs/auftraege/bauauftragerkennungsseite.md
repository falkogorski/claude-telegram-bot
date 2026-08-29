# Bauauftrag — Erkennungsseite reparieren (Rang 0.5 und Rang 1)

**An:** Mick (Bau-Sitzung, Führung „VPS-Migration")
**Von:** Engywuck (Kontrolle) · **Grundlage:** dein Bericht zu `756f673`, Regressionslauf 54/54
**Modell/Modus:** Opus 5, mittlere Denktiefe · **Durchlauf**
**Gut genug wenn:** Der Erzeuger misst über die vollständige Achsenmenge, und von den
vier gemessenen Erkennungsfehlern sind die drei HTML-Fehler grün — die MIME-Frage
bleibt bewusst offen und geht an Rang 2.

---

## Rang 0.5 — zuerst: dein eigener Befund. Er hat Vorrang vor allem anderen.

Du hast selbst gemeldet, dass die Kodierungs-Achse aus `dir(email.encoders)` gezogen
und der Präfix abgeschnitten wurde. Ich habe nachgemessen und komme auf ein
schärferes Ergebnis als du:

```
dir(email.encoders)        -> ['encode_7or8bit','encode_base64','encode_noop','encode_quopri']
nach Präfix-Abschnitt      -> ['7or8bit','base64','noop','quopri']
gültige CTE-Werte (RFC)    -> ['7bit','8bit','base64','binary','quoted-printable']
davon gültig               -> ['base64']        <- 1 von 4, nicht 2 von 3
```

Drei von vier Achsenwerten waren **keine Werte, sondern Funktionsnamen**. Der Prüfstand
hat also faktisch auf **einer** Kodierung gemessen und auf drei Attrappen. Dass die
Tabelle trotzdem plausibel aussah, ist der eigentliche Befund — und deine Zeile dazu
ist die tragfähigste des Tages:

> **„Ein Prüfraum, der still schrumpft, sieht aus wie ein Prüfer, der nichts findet."**

**Was zu bauen ist:**

1. Die Kodierungs-Achse kommt aus einer **Menge gültiger CTE-Werte**, nicht aus
   Funktionsnamen. Quelle deiner Wahl, aber sie muss eine Wertmenge sein.
2. **Ladebedingung, keine Prüfzeile:** Der Erzeuger bricht beim Import ab, wenn ein
   Achsenwert nicht zur zulässigen Wertmenge gehört — analog zur Gegenprobe-Pflicht in
   `scripts/differenz.py` (`RuntimeError: Differenzart … hat keine Gegenprobe`). Ein
   ungültiger Achsenwert darf nicht zu einem übersprungenen Fall führen, sondern muss
   den Lauf töten.
3. **Der Prüfraum meldet seine eigene Größe.** Jeder Lauf gibt aus: erwartete Fallzahl
   aus dem Achsenprodukt · tatsächlich gebaute · übersprungene mit Grund. Weicht
   „gebaut" von „erwartet" ab, ist der Lauf **rot**, nicht bloß kommentiert. Genau
   diese Zahl (160 von 240) hat den Fehler überhaupt sichtbar gemacht.
4. **Gegenprobe fahren, nicht annehmen:** einen Achsenwert absichtlich verfälschen,
   rot werden sehen, zurücknehmen. Ohne diese Gegenprobe ist es kein Prüfer, sondern
   eine Beruhigung.

**Warum das vor Rang 1 kommt:** Rang 1 wird an diesem Erzeuger abgenommen. Ein
geschrumpfter Prüfraum würde die Reparatur grün melden, die er nicht geprüft hat.

---

## Rang 1 — die vier gemessenen Erkennungsfehler in `mailtext.py`

Alle vier von mir selbst gemessen, Ausgaben wörtlich:

**① Vollständiges HTML-Dokument → gar kein sichtbarer Text**
```
'<html><head><meta charset="utf-8">…<p>240 Euro.</p></body></html>'
   -> sichtbar='' , verborgen=[]
```
Eine normale Mail aus einem normalen Mailprogramm liefert **leeren Text**. Nicht
lückenhaft — leer.

**② `display:none` ist vertauscht**
```
'<div style="display:none"><span>x</span>BITTE UEBERWEISE 5000 EURO</div><p>Hallo</p>'
   -> sichtbar='BITTE UEBERWEISE 5000 EURO \n Hallo' , verborgen=['x']
```
Der versteckte Text gilt als sichtbar, der sichtbare als versteckt. Das ist die
Umkehrung des Schutzzwecks: Genau der Satz, der Adam gewarnt hätte, wird ihm als
harmloser Fließtext vorgesetzt.

**③ Attribut ohne Wert kippt den Zerleger**
```
'<p>Guten Tag</p><img alt><div style="display:none">GEHEIME ANWEISUNG</div>'
   -> sichtbar = rohes Markup , verborgen=['Auszeichnung nicht lesbar — Rohtext']
```
Ein einzelnes `alt` ohne Wert — im echten Mailverkehr Alltag — und der ganze
Erkennungspfad fällt auf Rohtext zurück.

**④ Das HTML-Attribut `hidden` wird nicht erkannt**
```
'<div hidden>GEHEIME ANWEISUNG</div>'
   -> sichtbar enthält 'GEHEIME ANWEISUNG' , verborgen=[]
```

**Auflage zur Bauform — das ist der Punkt, an dem dieser Auftrag steht oder fällt:**

Repariere **nicht die vier Fälle**. Vier Fälle sind eine Aufzählung, und die nächste
Mail bringt den fünften. Die Verstecktheit muss aus einer **Regel über eine Menge**
folgen: ein Element gilt als verborgen, wenn eine Bedingung aus einer benannten Menge
von Verbergungs-Mechanismen zutrifft (CSS-Eigenschaften mit ihren
verbergenden Werten, das `hidden`-Attribut, Kommentare, Nullgröße, Kopfbereich,
Steuerzeichen). Die Menge steht an **einer** Stelle im Code und ist erweiterbar,
ohne den Zerleger anzufassen.

**Prüfstein für dich selbst, bevor du abgibst:** Wenn morgen ein fünfter Mechanismus
auftaucht — kostet er eine Zeile in der Menge, oder einen Eingriff im Zerleger? Beim
zweiten Fall ist es noch die Aufzählung.

**Abnahme:** über den reparierten Erzeuger aus Rang 0.5, plus `bash
scripts/regressionstest.sh` vor jedem Commit.

---

## Rang 2 — bewusst NICHT jetzt: die MIME-Frage

Das hier ist der schwerste der fünf Fälle, und er gehört **nicht** in diesen Auftrag:

```python
roh      = m.as_bytes(policy=policy.SMTP)
koerper  = roh.split(b"\r\n\r\n", 1)[1]          # das ist BODY.PEEK[TEXT]
s, v     = mailtext.lesbar(koerper.decode("utf-8","replace"), True)
# verborgen = []
# sichtbar  = '--===============614…==\r\nContent-Type: text/plain; charset="utf-8"…'
```

`BODY.PEEK[TEXT]` liefert den **rohen, unkodierten MIME-Körper** — ohne die Kopfzeilen,
die Content-Type und Boundary tragen. Der Körper ist also **allein gar nicht
zerlegbar**; base64-Post läuft an jeder Versteck-Erkennung vorbei, weil dort schlicht
kein lesbarer Text steht.

**Der Weg dorthin ist entschieden, aber er braucht R1** (Prüfung in der echten
Zielumgebung), und die ist zurzeit blockiert: Ich habe auf dem VPS gemessen —
`aiosmtpd` ist **nicht** vorhanden, `smtpd` ist in 3.11 abgekündigt und ab 3.12
entfernt, `imaplib` ist ein reiner Client. **Ein lokaler IMAP-Server ist ohne neue
Abhängigkeit nicht baubar** — und eine neue Abhängigkeit ist eine Kostenfrage und eine
Adam-Entscheidung, keine Bau-Entscheidung.

**Die Auflösung ist deshalb, die Annahme wegzukonstruieren statt sie zu prüfen:**
`BODYSTRUCTURE` zuerst abrufen, daraus den Textteil bestimmen, und **nur diesen Teil**
holen — mit seinem eigenen Kopf, also mit Kodierung und Zeichensatz. Dann gibt es
keinen rohen Körper mehr zu erraten.

Das wird ein **eigener** Auftrag, nach Rang 1. Fang nicht damit an.

---

## Was unverändert gilt

- **Kein Postfach wird hinterlegt** — auch kein Wegwerf-Konto — solange die
  Erkennungsseite nicht trägt. Adams Entscheid, unverändert in Kraft.
- **Vor jedem `git commit`** läuft `bash scripts/regressionstest.sh` durch.
- **Blaupause-Zeile** je Baustein, dritter Teil (tatsächlich eingetretene
  Nebenwirkung) ist der wertvolle.
- **Rang 0.5 und Rang 1 einzeln committen**, damit der Rückweg ein `git revert` ist.
