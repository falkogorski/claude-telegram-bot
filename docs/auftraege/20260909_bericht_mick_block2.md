> **Zweck: WEITERGABE → Engywuck** (Nachprüfung) · **ANSICHT** für Adam ·
> **Zu tun (Adam):** weiterreichen. Der Deploy von Block 1b läuft davon
> unabhängig — Block 2 kommt erst nach Engywucks Befund auf den Server.
> **Stand:** `6933dc5` gepusht · 09.09.2026, 21:42

# Block 2 — Leitstand und Protokoll je Zimmer

**Gebaut, 76/76.** Auftrag 6 vollständig: Leitstand-Minimum, `/zimmer`,
Protokoll je Zimmer. **Nenner:** 21 neue Prüfzeilen · 3 Gegenproben gefahren ·
1 Prüfer im selben Zug mitgezogen · Zielumgebung 41/43 (zwei übersprungen).

## Die eine Entscheidung, die den Rest bestimmt

**`leitstand()` gibt Daten zurück, keinen Text.** `/zimmer` formatiert sie,
Block 3 speist dieselbe Liste in die Sekretärin ein. Deine Auflage 7 sagt, der
Leitstand ist die Quelle ihres Kontexts — wäre er ein Textbaustein, hätte Block
3 eine zweite Stelle gebraucht, die dasselbe zu wissen behauptet. Die zweite
Stelle ist es, die abweicht.

Felder je Zimmer: `wach` · `arbeitet_an` · `seit_s` · `warteschlange` ·
`zuletzt_fertig` + `zuletzt_fertig_ts` · `still_s` · `pausiert_rest_s` · `name`.

## Zwei Fallen, beide vorher gemessen

**Die Zeitbasen.** `current_started` und `last_activity` sind `monotonic`,
`done_log` trägt `time.time()`. Der Vergleich über die Grenze wirft nichts und
ist immer falsch — genau der Befund vom 17.07. aus `_count_newer_pending`.
Deshalb heißen die Felder, was sie sind: `seit_s`/`still_s` sind **Dauern**,
`zuletzt_fertig_ts` ist ein **Zeitpunkt**. Die Gegenprobe (Basen vertauscht)
meldet `1787948012 s`.

**Der Wachposten.** Das Protokoll je Zimmer sah nach reiner Erweiterung aus.
Tatsächlich liest `wachposten.py` genau `<datum>.md` — Arbeit in einem Zimmer
wäre für ihn unsichtbar geblieben, und er hätte **Stille gemeldet, während
gearbeitet wird**. Das ist die eine Fehlerrichtung, gegen die er gebaut ist. Im
selben Zug mitgezogen (Geschwister-Regel), mit eigener Prüfzeile in seinem
eigenen Prüfer.

Deshalb behält der **Hauptfaden** auch seinen Dateinamen `<datum>.md`: Log-Abgleich
und die Mac-Sitzung lesen ihn seit Wochen; ein neuer Name wäre nach *Struktur
über Namen* eine Abhängigkeits-Änderung ohne Not.

## Was der Leitstand nicht tut: raten

Ein Zimmername wird nur aufgelöst, wenn `chat_id` **und** `thread_id` vorliegen
— Themen-Kennungen sind nur innerhalb eines Chats eindeutig. Ohne den Chat steht
die nackte Kennung da. Gegenprobe: Ohne die `chat_id`-Prüfung liefert ein
fremder Chat mit derselben Themen-Kennung den falschen Klarnamen.

**Ein Nebenbefund, der dir gehört:** Der Schlüssel `(user_id, thread_id)` aus
Block 1 trägt **keine `chat_id`**. Zwei Forum-Gruppen mit derselben Themen-Kennung
kollidierten im Schlüssel. Heute unerheblich (Adams Chat ist privat, Häuser gibt
es nicht), aber es ist eine echte Grenze der Bauform — ich melde sie, statt sie
zu übergehen.

## `/zimmer`

Wird im Prüfer **ausgeführt**, nicht im Quelltext gesucht: Update-Attrappe rein,
Text raus, Text geprüft. Er endet nicht mit einer Frage (deine Regel vom 20.08.),
sondern nennt den Antwortweg: *„schreib in das Thema, dessen Zimmer du meinst —
`/stopp` und `/reset` wirken dort, wo du sie tippst."* Ein Zimmer ohne
Lebenszeichen seit über einer Stunde wird als solches ausgewiesen (Risiko „ein
Zimmer stirbt still" aus dem Bauauftrag).

## Was beim Gegenprüfen auffiel

Fiel die Zimmer-Datei weg, **stürzte mein eigener Prüfer ab**, statt rot zu
werden — und verdeckte damit die Zeilen darunter. Behoben; jetzt meldet er alle
drei betroffenen Zeilen einzeln. Eine Prüfzeile war zudem falsch konstruiert
(`" s" not in text` traf auf „— schläft"); umgestellt auf einen Ausdruck, der
nackte Sekundenzahlen sucht.

## Offen

Deploy von Block 1b läuft bei Adam parallel; Block 2 geht erst nach deinem
Befund auf den Server. Danach Block 3 (Sekretärin) — der bekommt `leitstand()`
als Kontextquelle, wie in Auflage 7 vorgesehen.
