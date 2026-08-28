# Bauauftrag: Überschrift landet weiterhin am Nachrichtenende

**Weg:** Claudia → Engywuck (Prüfung) → Mick (Umsetzung)
**Anlass:** Adam am 27.08.2026, 14:33 Uhr — zum wiederholten Mal. Die Regel steht
seit dem 23.06.2026 fest, der Schutz greift trotzdem nicht.

## Was Adam sieht

Eine Überschrift steht als letzte Zeile einer Telegram-Nachricht, der zugehörige
Text erst in der nächsten. Milderer Fall: Überschrift plus erster Satz am Ende,
der Rest des Abschnitts wandert. Beides macht das Anpinnen und Wiederfinden
kaputt — genau der Zweck, für den die Regel einmal geschrieben wurde.

## Befund 1 — harter Zeichenschnitt bei 1024 (der Hauptverursacher)

`bot.py`, Zeilen 10697 bis 10699, in `_send_tts`:

```python
caption_for_first = coupled_text[:1024]
if len(coupled_text) > 1024:
    rest_text = coupled_text[1024:].lstrip()
```

Bei eingeschalteter Sprachausgabe wird der Antworttext als Bildunterschrift an
die erste Sprachnachricht gehängt. Telegram lässt dort 1024 Zeichen zu — und der
Text wird **an genau dieser Zeichenzahl abgeschnitten**, ohne Rücksicht auf
Zeilen, Absätze oder Überschriften. Mitten im Wort ist ebenso möglich wie
zwischen Überschrift und erstem Satz.

`_find_safe_cut` läuft erst danach, auf `rest_text` (Zeile 10710) — also auf dem
bereits falsch abgetrennten Rest. Der Schutz kommt zu spät.

**Warum es gerade jetzt auffällt:** Fast jede inhaltliche Antwort ist länger als
1024 Zeichen. Der Schnitt greift damit praktisch immer, sobald die Sprachausgabe
an ist. Der 4000-Zeichen-Schnitt in `send_chunked`, für den der Schutz gebaut
wurde, greift dagegen selten.

## Befund 2 — der Streaming-Wächter ist nie verkabelt worden

`_text_ends_with_heading` (`bot.py`, Zeile 2073) prüft, ob ein Text mit einer
Überschrift endet. Gesucht im gesamten Repo über alle Python- und
Markdown-Dateien: **genau eine Fundstelle, nämlich die Definition selbst.** Kein
Aufruf, kein Test, keine Erwähnung in der Dokumentation.

Die Funktion trägt einen Docstring, der ihren Zweck beschreibt („wird beim
Streamen genutzt"). Sie wird nicht genutzt. Das ist der Fall aus
[[feedback-vereinbarung-braucht-zustand]] in Reinform: gebaut, aber nicht
angeschlossen — von außen nicht von „funktioniert" zu unterscheiden.

## Auflage

**Zu Befund 1:** Der Schnitt bei 1024 Zeichen muss dieselbe Sicherung bekommen
wie der bei 4000 — also über `_find_safe_cut(coupled_text, 1024)` laufen statt
über einen Zeichenindex. Damit fällt der Schnitt auf eine Zeilengrenze und rückt
vor einer Überschrift zurück.

Zu bedenken: `_find_safe_cut` gibt bei einem Text ohne Zeilenumbruch vor dem
Limit den Grenzwert selbst zurück (Zeile 2049). Für einen zusammenhängenden
Absatz von über 1024 Zeichen bleibt es also beim harten Schnitt. Das ist
hinnehmbar — mitten im Absatz zu trennen stört weit weniger, als eine
Überschrift abzureißen.

**Zu Befund 2:** Entweder anschließen oder entfernen. Eine Funktion, die
vorgibt zu schützen und nicht aufgerufen wird, ist schlimmer als keine — sie
lässt bei der Suche nach der Ursache glauben, der Fall sei abgedeckt. Genau das
ist hier passiert.

## Was kann brechen und wer merkt es

- **Die Bildunterschrift wird kürzer als bisher.** Der Rest wandert in die
  Textnachricht darunter. Kein Verlust, nur eine andere Verteilung. Fällt
  niemandem negativ auf.
- **Ein sehr langer Absatz ohne Umbruch** bricht weiterhin hart. Bekannt und
  bewusst hingenommen, siehe oben.
- **Stiller Rückfall, wenn niemand prüft.** Der Fall wäre schon zweimal
  aufgefallen, wenn ein Test ihn abdeckte. Deshalb gehört ein Selbsttest dazu:
  ein Text mit einer Überschrift kurz vor Zeichen 1024, geprüft wird, dass die
  Überschrift **nicht** am Ende der Bildunterschrift steht. Anzuhängen an den
  Vier-Uhr-Funktionscheck.
- **Der Prüfer selbst kann still ausfallen.** Sein Ergebnis gehört ins
  Tagesprotokoll, nicht nur in den Ausgang.

## Was ich bis dahin selbst tue

Antworten so knapp halten, dass sie unter 1024 Zeichen bleiben. Was länger ist,
geht als Datei statt als Chattext. Das trägt die Regel, solange der Code sie
nicht trägt — aber es ist Disziplin, kein Mechanismus.
