<!-- ROLLE: adam-arbeitsliste -->
# Adams Arbeitsliste

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich ist diese
Datei** · **Pflege:** jede Sitzung, die einen Adam-Schritt hinterlässt

## Wofür es diese Liste gibt

Adam sagt „ich habe zwei Stunden" — und die Sitzung führt ihn **Punkt für
Punkt** hindurch, statt dass er sich zusammensuchen muss, was wo wartet.
Bisher lagen diese Handgriffe verstreut über Chats, Berichte und
Weitergabe-Blöcke; wer sie finden wollte, musste wissen, wo er suchen soll.
**Ein Handgriff, den niemand findet, ist kein wartender Punkt, sondern ein
verlorener.**

Der Zweck ist ausdrücklich **nicht** Vollständigkeit um ihrer selbst willen,
sondern **Nutzbarkeit in einem knappen Zeitfenster**: Jeder Punkt trägt eine
Minutenschätzung, damit sich ein Fenster füllen lässt, und die Angabe, **was er
freischaltet** — sonst ist jede Reihenfolge willkürlich.

## Pflicht-Regel

**Wer einen Bau abschließt, der einen Adam-Schritt hinterlässt, trägt ihn im
selben Commit hier ein.** Das ist Teil der „fertig"-Definition, wie das
Abhängigkeits-Register und die Blaupause-Zeile. Nachträglich sammeln
funktioniert nicht: Der fertige Copy-Paste-Block existiert genau dann, wenn der
Bau frisch ist, und danach muss man ihn rekonstruieren.

**Erledigtes wird sofort abgehakt** (`- [x]` mit Datum), nicht gelöscht — die
Liste soll auch zeigen, was schon durch ist, sonst fragt man dreimal nach
demselben.

## Format je Punkt

```
- [ ] **<Was zu tun ist>** · ~<Minuten> · schaltet frei: <was danach geht>
      Weg: <fertiger Block, Dateiverweis oder konkrete Schritte>
```

---

## Offen

- [ ] **Abends den Nachtblock anstoßen** (wiederkehrend) · ~1 Min · schaltet
      frei: **jede Nachtarbeit überhaupt.**
      Weg: Eine kurze Nachricht genügt — „mach den Nachtblock". Der Grund,
      warum dieser Punkt hier steht: **Diese Sitzung hat keinen eigenen
      Zeitgeber** (gemessen am 19.08.), und die Durchlauf-Wache greift nur
      innerhalb eines laufenden Zuges. Ohne deinen Anstoß läuft nachts nichts,
      egal was im Laufplan steht. Der vorbereitete Block ist meine Aufgabe,
      der Anstoß deine.

- [ ] **iCloud-Zugang für den Kalender (7.3)** · ~10 Min · schaltet frei:
      `/termine` und `/aufgaben` am lebenden Bot — **der Bau steht seit dem
      25.07. vollständig**, es fehlt nur dieser Zugang.
      Weg: Im Apple-Konto ein **anwendungsspezifisches Kennwort** erzeugen
      (das normale Apple-Kennwort funktioniert bei CalDAV nicht). **Nicht in
      den Chat schicken** — ich bereite den Befehlsblock für die geschützte
      Umgebung auf dem VPS vor, du fügst den Wert dort ein. Sag Bescheid, dann
      lege ich ihn an.

- [ ] **Erinnerungskanal anlegen (7.1)** · ~5 Min · schaltet frei: **7.2**, den
      Erinnerungs-Läufer — ohne Kanal hat er kein Ziel.
      Weg: Telegram-Kanal anlegen, Bot als Administrator mit Schreibrecht
      hinzufügen, mir die Kennung nennen. Kann zusammen mit den vier
      Live-Gruppen für Phase 6 erledigt werden — derselbe Handgriff.

- [ ] **E-Mail-Konten / 5.28-Zugang einrichten** · ~20 Min · schaltet frei:
      Punkt 9.5 (E-Mail-Kanal) kann in Betrieb gehen; der Bot kann Nachrichten
      senden und empfangen, statt es nur zu können.
      Weg: Zugangsdaten für das Postfach bereitstellen. **Kennwörter niemals in
      den Chat** — der Weg über die geschützte systemd-Umgebung auf dem VPS
      steht in `docs/befehlsbloecke-root.md`; ich bereite den Block vor, sobald
      du sagst, welches Postfach es wird.

- [ ] **Vier Live-Gruppen für Phase 6 anlegen** · ~15 Min · schaltet frei:
      **Phase 6 E2E** — und damit den nächsten Schritt im Bot-Strang überhaupt
      (Reihenfolge unter „Geteilt": 6 → 7 → 9.6 → 10).
      Weg: In Telegram vier Gruppen anlegen, den Bot je als Administrator
      hinzufügen, mir die Gruppen-Kennungen nennen. Welche vier und wofür,
      steht in Phase 6 des Drehbuchs.

- [ ] **Drei Testlinks für 5.14 schicken** · ~2 Min · schaltet frei: die
      Link-Inbox lässt sich am lebenden Bot abnehmen statt nur im Prüfer.
      Weg: Drei beliebige Links in den Bot-Chat — gern gemischt (Artikel,
      Video, Beitrag), damit die Erkennung auf verschiedenen Arten läuft.

- [ ] **RAM-Entscheid N2** · ~5 Min Entscheidung · schaltet frei: Klarheit, ob
      der VPS aufgestockt wird oder es beim Gemessenen bleibt.
      Weg: Gemessen wurde 3017 MiB im Betrieb, im Ruhezustand null — **der
      Speicher war nie der Engpass, die Qualität ist es.** Entscheidung ist
      also eher „bleibt so", außer du willst Ollama größer fahren. Sag Bescheid,
      dann trage ich es ein. 💰 Eine Aufstockung wäre kostenpflichtig — Höhe
      und Freigabe würden vorher genannt.

- [ ] **Restore-Drill 4.x terminieren** · ~45 Min am Termin selbst · schaltet
      frei: den Nachweis, dass die Sicherung nicht nur läuft, sondern **trägt**.
      Weg: Einen Termin nennen. Ein Backup, das nie zurückgespielt wurde, ist
      eine Vermutung — das ist der einzige Punkt dieser Liste, der dich vor
      einem echten Schaden bewahrt, und der einzige, den man nur vorher machen
      kann.

- [ ] **Hermes-Entscheid 9.7** · ~10 Min Entscheidung · schaltet frei: Punkt
      9.7 wird planbar statt offen.
      Weg: Die Entscheidungsvorlage liegt unter
      `docs/entscheidungsvorlagen/` — ich fasse sie dir auf Zuruf in drei
      Sätzen zusammen, wenn du nicht lesen magst.

---

## Erledigt

- [x] **Wachposten-Zeitgeber einspielen** — 19.08.2026, 23:16. Timer lief an.
- [x] **Log-Abgleich auf fünf Minuten stellen** — 19.08.2026, 23:15. Timer lief
      an. (Ersetzt den Stundentakt vom 18.08.)
- [x] **Wachposten-Merkzettel zurücksetzen** — 20.08.2026, 01:15 durch mich.
      Die sieben verschluckten Zeilen sind nachgeholt; sieben Dämpf-Schlüssel
      statt einem belegen, dass der Fix greift.
- [x] **Ja-Knopf an der Wachposten-Meldung** — 20.08.2026 gebaut. Ein Tipp
      hinterlegt den Befund im Auftragsbuch, deterministisch und ohne
      Modellstart. Deine Frage von 00:31 hat damit eine Wirkung.
