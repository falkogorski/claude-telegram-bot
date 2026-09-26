# Bauauftrag: Eine Sprachnachricht je Text

**Zustand:** gültig · Weg: Claudia → Engywuck → Mick
**Fassung:** 26.09.2026
**Wunsch:** Adam am 26.09.2026, 17:32 Uhr

## Adams Wunsch

„Ein Text, ein großer Text, dann kommt darunter eine Sprachnachricht pro Text.“
Seit Text und Stimme getrennt gesendet werden, wirkt die in Stücke geschnittene
Stimme zerrissen.

## Ursache, gemessen in `bot.py`

- `send_answer_to_user` (ab Zeile 17204) sendet den Text seit dem 26.09.2026
  (Block 2b, Auftrag G) als eigene Nachricht, sobald er nicht als **eine**
  Bildunterschrift passt (`getrennt`, Zeile 17320).
- Die Stimme wird danach trotzdem weiter in der Schleife ab Zeile 17365 nach
  `TTS_SYNC_CHUNK = 1024` Zeichen (Zeile 715) geschnitten. Jedes Stück wird zu
  einer eigenen Sprachnachricht.
- Der Grund für die 1024 war die Bildunterschrift, die Telegram bei 1024
  Zeichen begrenzt. Im getrennten Weg trägt die Stimme aber keine
  Bildunterschrift mehr (`_roh_unterschrift = None`, Zeile 17391). Die Grenze
  wirkt dort also ohne Anlass weiter.

## Auftrag

**Im getrennten Weg (`getrennt` wahr) und bei `force_tts` wird die Stimme
nicht mehr nach `TTS_SYNC_CHUNK` geschnitten.** Eine Antwort ergibt dann eine
Sprachnachricht.

- Als Obergrenze gilt eine großzügige Sicherheitsgrenze, etwa die vorhandene
  `TTS_CHUNK_CHARS = 4000` (Zeile 714) oder ein höherer Wert, den Mick misst.
  Erst darüber wird geteilt, und zwar am Absatz.
- Der Weg mit Text als Bildunterschrift (kurze Antworten) bleibt unverändert.
  Dort passt ohnehin alles in ein Stück.
- Der Quellenhinweis („Die Quellen sind im Text verlinkt.“) steht weiterhin
  genau einmal am Ende der Stimme.

## Vor dem Bauen zu messen (Mick)

1. **Erzeugungsdauer:** Wie lange brauchen edge-tts und die lokale Stimme
   (Thorsten, rote Antworten) für 4000 Zeichen auf dem Server? Die lokale
   Stimme läuft auf der CPU. Eine lange Antwort kann die Zustellung spürbar
   verzögern.
2. **Zeitgrenzen:** Greift eine Zeitgrenze im Aufruf von `_send_tts_chunk`
   oder der TTS-Bibliothek, bevor ein langes Stück fertig ist?
3. **Dateigröße:** Telegram nimmt von Bots Sprachnachrichten bis 50 MB an
   (ungeprüft, bitte gegenlesen). Zehn Minuten Opus-Sprache liegen
   erfahrungsgemäß weit darunter.

Ergibt die Messung, dass 4000 Zeichen zu langsam sind, kommt der kleinste
Wert, der noch trägt. Adam bekommt dazu einen Satz mit dem Grund.

## Was brechen kann und wer es merkt

- **Zeitüberschreitung bei langer Erzeugung:** Die Stimme fehlt dann ganz.
  Das ist schlechter als eine geteilte Stimme. → Der Ausfall muss denselben
  Rückweg nehmen wie heute (Zeile 17406 ff.: Text steht, nur die Stimme fehlt)
  und im Protokoll landen.
- **Reihenfolge Text vor Stimme:** Durch die längere Erzeugung wächst der
  Abstand zwischen Text und Stimme. Das ist gewollt, weil der Text gesichert
  ist. Es muss aber im Selbsttest abgedeckt sein, dass die Stimme als Antwort
  auf den Text ankommt.
- **Stiller Rückfall:** Ein späterer Eingriff setzt die 1024 wieder als Grenze
  für alle Wege. → Der Selbsttest im Sendepfad (`scripts/test_sendepfad_rauch.py`)
  bekommt einen Fall: eine Antwort mit 2500 Zeichen, TTS an → genau
  **eine** Sprachnachricht.

## Reichweite

Dieselbe Frage stellt sich an allen Stellen, die Stimme erzeugen: Antwortweg,
PDF-Vorlesen (`TTS_CHUNK_CHARS`), Startmeldung (Zeile 13344, dort ebenfalls
1024), Sekretärin. Empfehlung: **eine gemeinsame Regel** („Stimme ohne
Bildunterschrift → bis zur Sicherheitsgrenze ungeteilt“) statt einer Korrektur
nur im Antwortweg. Sonst bleibt die Startmeldung zerstückelt.
