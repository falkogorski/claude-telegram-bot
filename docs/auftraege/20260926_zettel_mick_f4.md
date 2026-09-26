**Zweck: WEITERGABE → Mick** · **Zu tun: unverändert an Mick, zusammen mit Claudias zwei Bauaufträgen von 17:31 und 17:33 als PDF und dem Nebenfaden-Auftrag f2.**

# Zettel an Mick — 26.09.2026, 17:56 (Fassung 4)

Ersetzt nichts, ergänzt f3. Drei Papiere von Claudia sind heute Nachmittag dazugekommen; hier steht, was davon trägt, in welcher Reihenfolge, und was ich daran geändert habe.

## 1. „Eine Sprachnachricht je Text" (Claudia 17:33) — trägt, so bauen, klein

Adams Wunsch 17:32: ein Text, eine Stimme darunter. Sechs Sprachnachrichten für eine Antwort (Fotos 17:29). Claudias Messung stimmt: Im getrennten Weg (Auftrag G) schneidet die Schleife weiter bei `TTS_SYNC_CHUNK = 1024`, obwohl die Stimme dort keine Bildunterschrift mehr trägt. **Zwei Auflagen von mir:** (a) Die Grenze für die **lokale Stimme** hängt an `sprachausgabe_lokal.ZEITGRENZE_S`; miss Thorsten auf der Server-CPU mit 4000 Zeichen, bevor du die Grenze setzt, und wähle für die lokale Stimme notfalls eine eigene, kleinere Grenze statt einer gemeinsamen. Eine fehlende Stimme ist schlechter als eine geteilte. (b) Claudias „Reichweite" gilt: eine Regel für alle Stellen ohne Bildunterschrift, auch Startmeldung (13344). Prüfzeile: 2500 Zeichen, TTS an → genau eine Sprachnachricht; Gegenprobe: Grenze wieder auf 1024 → rot.

## 2. „Jahreszahlen in Klammern" (Claudia 17:31, Adam 👍) — trägt, mit Geschwister-Auflage

Ursache stimmt: `_normalize_jahreszahlen` braucht ein Jahres-Wort davor; „(1927)" hat keins. Claudias Strukturregel (allein in Klammern, am Klammeranfang vor Komma, Bereich in Klammern; Einheit danach → Menge) ist richtig und klein. **Meine Auflage nach der Geschwister-Regel:** Es gibt jetzt **drei** Sprechwege, und jeder erkennt Jahre selbst: die edge-tts-Kette (`_normalize_jahreszahlen`), deine Piper-Aufbereitung (`_zahlwort`, Datum/Jahreszahl) und `ssml_bauen` in `sprachausgabe_azure.py` (`say-as`). Baue die Erkennung **einmal** als reine Funktion (Kontext hinein, „Jahr/Menge/unklar" heraus) und lass alle drei sie rufen; sonst hört Adam denselben Fehler in drei Fassungen. Prüfzeilen: Claudias Tabelle je Sprechweg. **Auftrag 1 (NeMo prüfen):** nicht als Tor. NeMo steht in keiner Anforderungsliste und in keinem Fenster; die Klammerregel wird jetzt gebaut, NeMo bleibt F-Liste. Das ist Adams Regel „schnelle Entscheidungen, kein Aufschub".

## 3. Befund „Nachtrag mit neuem Thema zerschnitten" (Claudia 17:42) — eingearbeitet

Adams Vorgabe 17:37 (neues Thema → eigene Nachricht) und der Schnitt am Themenwechsel stehen jetzt als Teil 8 im Nebenfaden-Auftrag f2, das Bündel-Problem (fünf Fotos, fünf Meldungen) als Teil 7. Beides gehört an dieselbe Stelle wie der Nebenfaden, deshalb kein eigenes Papier. Claudias Nebenbefund Vorschaukarte: Am Foto sichtbar hängt die Karte am **Ende des Stücks, das die Adresse trägt**, also unter dem Passwort-Anfang, nicht unter der Liste. Das ist dein Bau wie vorgesehen; ob Wikipedia für die Listenseite die Hauptseiten-Karte liefert, ist Telegrams Sache. Kein Bau.

## 4. Reihenfolge ab jetzt

Deploy Schritte 2 und 3 (Adam) → **eine Stimme je Text** (klein, sofort spürbar) → **Schnitt am Themenwechsel** (klein, Teil 8 letzter Punkt, kann vorgezogen werden) → **Jahreszahlen-Klammer** (klein) → **Nebenfaden f2** (Block, Klon-Probe) → Azure mit Schlüssel (sobald Adam das Konto hat) → Dirigent (Konzept folgt von mir, kein Bau vorher).

Vor jedem Commit der Regressionslauf, je Posten die Gegenprobe mit vorab benannter Zeile; nach dem Block eine Gegenprüfung durch mich, dann Deploy als eigener Schritt.
