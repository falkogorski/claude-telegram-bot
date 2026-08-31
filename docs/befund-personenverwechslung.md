<!-- ROLLE: befund-personenverwechslung -->
> **Zweck: ABLAGE + ENTSCHEID** · **Zu tun:** entscheiden, ob ein
> Personen-Register gewünscht ist. **Es enthält bewusst keine Namen.**

# Befund: wiederholte Personenverwechslungen — und warum hier nichts gebaut wird

**Herkunft:** Gesamtprüfung der Bot-Protokolle, Block 12 (**28.07.2026**).
Nachgetragen am 31.08.

---

## Der Befund

**Adam hat am 28.07. innerhalb weniger Minuten dreimal eine Person richtiggestellt**
— zwei Verwechslungen von Menschen aus seinem Umfeld und einen Fall, in dem die
Zuordnung überhaupt nicht stimmte.

**Gemessen: es gibt kein Personen-Register.** Der Bot hält Menschen aus Adams
Umfeld nirgends strukturiert fest; was er über sie weiß, stammt aus dem
laufenden Gespräch und aus verstreuten Gedächtnis-Notizen. **Verwechslungen
sind damit nicht ein Versehen, sondern die zu erwartende Folge.**

## Warum dieses Papier keine Namen enthält

**🔴 Namen von Angehörigen sind die heikelste Datenklasse, die dieses System
kennt.** `CLAUDE.md` führt sie ausdrücklich als *heikelste Muster*, die **nur
über den cloud-freien Weg** gepflegt werden dürfen: der `/ampel`-Button-Dialog
oder `/ampel rot …` — beides wird deterministisch in `bot.py` verarbeitet,
**ohne Claude-Beteiligung**.

Ein Papier, das die Verwechslungen mit Namen belegt, hätte genau diese Regel
gebrochen — im selben Zug, in dem es sie zitiert. **Der Befund trägt auch
ohne.**

## Was daraus folgt — und wem die Entscheidung gehört

**Ein Personen-Register ist eine Datenschutz-Entscheidung Adams, kein
Komfort-Feature.** Es würde Namen, Beziehungen und Zuordnungen dauerhaft
festhalten; wo diese Daten liegen und wer sie sieht, ist die eigentliche Frage,
nicht ob es die Verwechslungen beheben würde.

**Falls Adam es will**, führt der Weg über den **Ampel-Button** — nicht über
eine natürlichsprachige Pflege durch mich, weil die durch die Cloud liefe.

**Von dieser Sitzung wird dazu nichts gebaut und nichts eingetragen, was Namen
enthält.**
