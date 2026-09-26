**Zweck: WEITERGABE → Engywuck + ANSICHT** · **Zu tun: an Engywuck zur Gegenprüfung. Deploy erst nach seiner Nachprüfung, als eigener Schritt (Abschnitt 4).**

# Abendblock 26.09.2026 — Zettel f4 abgearbeitet, Nebenfaden gebaut

Mick, Stand: der Commit dieses Papiers (gepusht). **Nenner:** 13 Commits seit dem Serverstand `7099628`, dieses Papier mitgezählt. Davon ist e7fdbc0 nur das Deploy-Papier und 08a4abf die Zeitform samt Drehbuch, beide schon bekannt. **Neu sind vier Bauposten aus f4 in 9 Commits**, alle vier sind gebaut.

## 1. Was gebaut ist

| Posten | Commit | Prüfer | Gegenproben |
|---|---|---|---|
| **Eine Stimme je Text** (Claudia 17:33, f4 Teil 1) | `447b71d` | `test_darstellung.py` G, 11 Zeilen | 2 + 4 rot |
| **Schnitt am Themenwechsel** (f2 Teil 8, vorgezogen) | `cc76b60` | `test_darstellung.py` H, 6 Zeilen | 3 rot |
| **Jahreszahlen in Klammern** (Claudia 17:31, f4 Teil 2) | `1367486` | `test_jahreszahl.py`, 31 Zeilen | 2 + 3 rot |
| Widerlegung der drei Posten | `3aa5c92` | Zeilen je Befund (in den drei Prüfern oben) | 8 rot (oben mitgezählt) |
| **Nebenfaden, Teile 1 bis 8** (f2) | `5a6cc30`, `dd94699` → `a190ce1` | `test_nebenfaden.py`, 53 Zeilen | 7 + 9 rot |

**Deine Auflagen aus f4:**
- **(a) Messung der lokalen Stimme:** am Mac gemessen, 4000 Zeichen in 5,9 s (3,7 min Ton, 897 KB). Für den Server ist das nur hochgerechnet, rund 12 s nach Faktor 18, gemessen ist es dort nicht. Die Messung auf dem Server steht als Schritt 2 im Deploy. Die Grenze ist die Einstellgröße `TTS_STIMME_LOKAL`, Vorgabe 4000. Sie lässt sich ohne Code senken.
- **(b) Reichweite:** Eine Regel gilt jetzt für den Antwortweg, die Startmeldung, `_send_tts` und die PDF-Kapitel.
- **Jahreszahl:** eine reine Funktion `jahreszahl.art` für alle drei Sprechwege. Dabei zeigte sich der umgekehrte Fehler bei Azure: Es las **jede** vierstellige Zahl als Jahr, auch „(1500 Zeichen)“. Das ist behoben.
- **NeMo:** nicht als Tor behandelt, steht in der F-Liste.

**Nebenfaden: eine Abweichung von deinem Wortlaut, begründet.**
- Der Wortlaut sah den Schlüssel `(user_id, "neben")` vor. Gebaut ist ein **negativer thread-Teil**, also `-1` für den Hauptfaden und `-1 - t` für ein Thema `t`. Der Typ `Faden` bleibt damit `(int, int|None)`.
- Grund: Eine Erfassung ergab, dass der Schlüssel an 16 Stellen als Schlüssel und an 22 Stellen zugleich als Telegram-Thema dient.
- Der Auftrag im Nebenzimmer trägt deshalb sein **echtes** Thema, und nur der Schlüssel wird über `_job_faden` abgeleitet. Alle Sendestellen bleiben dadurch unberührt richtig.
- **Schlüssel und Ausgabe-Adresse sind hier zum ersten Mal getrennt.** Das ist Vorlauf für Stufe 2.
- **Bash ist im Nebenfaden ganz gesperrt**, nicht nur schreibendes Bash. Schreibendes Bash lässt sich nicht verlässlich erkennen, und gelesen wird über Read, Grep und Glob.

## 2. Widerlegung

**Zu Stimme, Schnitt und Jahreszahl** (frische Opus-Sitzung, 20 Funktionen, 183 Lesungen alt gegen neu): 1 scharfer Befund, 4 mittlere, 5 kleine. Scharf war S1: Eine Startmeldung über 4096 Zeichen kam gar nicht an. Alle Befunde sind geschlossen (`3aa5c92`), K1 und eine Klammergrenze stehen in F-25. Bei zwei meiner eigenen Befundzeilen hat erst die Gegenprobe gezeigt, dass sie nicht trugen: K5 maß Reste früherer Zeilen, K2 hatte einen zufällig passenden Probetext. Beide sind berichtigt.

**Zum Nebenfaden** (frische Opus-Sitzung, 7 Suchpunkte, 10 Messungen; der Regressionslauf lief 100/100 grün und fing keinen der Befunde): **3 scharf, alle Doppelantworten**, dazu 5 mittlere und 6 kleine Befunde.
- **S1:** Der Hauptvorgang endet, während der Empfang noch einschätzt.
- **S2:** Ein Knopfwechsel nach schon gelesenem Zettel.
- **S3:** Ein Neustart nach der Zustellung spielt den Zwilling nach.

S1 bis S3, M1 bis M5 und K2 bis K4 sind geschlossen, bei neun Gegenproben rot. **M5 betrifft mich direkt:** Drei meiner Prüfzeilen waren entkernbar, nämlich Warten, Leitstand und Drossel. Die M4-Zeile trug auch nach der Nachbesserung noch nicht, bis sie über den echten Eingang lief statt über die Hilfsfunktion. In F-25 stehen M1 ohne ausführende Zeile sowie K5 und K6 als Herleitungen.

## 3. Was du wissen musst

- **Der Empfang ist bei Adam aus.** Dann entscheidet der Nebenfaden nie selbst, sondern arbeitet ein wie bisher, mit den vier Knöpfen darunter. Das ist sein Entscheid 2 und der sichere Rückfall. Soll der Bot selbst „nebenbei“ wählen, braucht es `/empfang an`, und dann kostet jede Nachricht während eines Laufs einen Sonnet-Lauf.
- **Eigenfund:** Die Nummer F-23 war doppelt vergeben. Seit dem 11.09. trägt sie den Hygiene-Neustart, und deine Kleinigkeiten vom 26.09. stehen jetzt unter F-24 (`8b786a2`).
- **Nicht gebaut:** Lernen der Schwelle, mehr als ein Nebenfaden, Dirigent Stufe 2. Stufe 2 folgt nach deiner Nachprüfung und dem Deploy.

## 4. Deploy-Vorschlag (erst nach deiner Nachprüfung)

Schritt 0 prüft wie immer, dass genau diese Commits kommen:
```
ssh claudebot 'cd ~/claude-telegram-bot && git fetch -q origin && git log --oneline HEAD..<ziel>'
```
Erwartet sind genau die 13 Commits von `e7fdbc0` bis zum Commit dieses Papiers. Kommt nach deiner Nachprüfung ein Fix dazu, wächst die Zahl um genau diesen einen. Dann Code, Regressionslauf, Neustart. Schritt 2 misst Thorsten mit 4000 Zeichen auf der Server-CPU. Liegt das über 60 s, setzt Adam `TTS_STIMME_LOKAL=2000`, kein Code nötig. Den Befehl schreibe ich ins Deploy-Papier, sobald die Nachprüfung steht.
