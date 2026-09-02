<!-- ROLLE: entscheidungsvorlage-ablage-server -->
> **Zweck: ANSICHT + ENTSCHEID** · **Zu tun:** einen der drei Wege wählen —
> oder „später". **Nichts davon ist gebaut.**

# Ablage auf dem Server statt iCloud als Mitte

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 03.09.2026 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile bei 5.19.

**Adams Ziel, 03.09. gegen 00:2x:** *„alle Aufgaben … vollumfänglich
ausschöpfen können, auch wenn der Mac aus ist"* und *„Kann man die Rechnung
nicht auch auf dem Server einfach ablegen? … Und wie bekomme ich da Zugriff
drauf?"*

**Das ist Claudias Route C**, die sie bewusst nicht für den 02.09. vorschlug —
richtig, denn sie ist größer als der Tagesbedarf. **Aber Adam beschreibt genau
sie**, und deshalb steht sie hier statt als Nebensatz in einem Papier.

## Was heute fehlt — und was nicht

Seit dem 03.09. läuft **alles außer der Ablage** ohne den Mac: Claudia
erzeugt Rechnung und Aufstellung auf dem Server, legt die PDF über das
Postfach in den Chat, Adam verschickt sie vom Handy.

**Nur der letzte Schritt hängt am Mac:** Ein Server kann nicht in Adams iCloud
schreiben, ohne dessen Apple-Zugangsdaten zu halten. Genau dafür hat er
„später Route B" gesagt. **Das Verschicken hängt nicht davon ab** — nur das
Einsortieren in den Kundenordner.

## Die drei Wege

| | Was es ist | Nutzen | Preis |
|---|---|---|---|
| **① Netzfreigabe** (WebDAV oder SFTP vom Server) | Mac und iPhone binden einen Server-Ordner als Laufwerk ein | Kein Apple-Passwort auf dem Server · kein zusätzlicher Dienst auf dem Mac · funktioniert vom Handy | **Ein Dienst nach außen**, der Adams Geschäftsdaten trägt. Braucht Zugangsschutz und Verschlüsselung |
| **② Abgleich ohne Mitte** (Syncthing) | Server, Mac und Handy gleichen sich direkt ab | Kein zentraler Punkt · funktioniert auch, wenn eine Seite aus ist · quelloffen | Ein weiterer Dauerdienst auf drei Geräten · Konflikte bei gleichzeitiger Änderung · iPhone-App nötig |
| **③ Cloud-Oberfläche** (Nextcloud) | Vollwertige Weboberfläche auf dem Server | Bedienbar wie iCloud · Freigaben an Kunden möglich · viele Zusatzfunktionen | **Deutlich größere Angriffsfläche** · eigene Datenbank · laufende Pflege und Updates · schwer für den Zweck |

## 💰 Kosten — je Weg ausdrücklich

**Software: alle drei quelloffen und kostenfrei.** Was Geld kosten *kann*:

- **Speicher auf dem VPS.** Heute ist Platz da; ob das mit wachsender Ablage so
  bleibt, ist **ungeprüft** — vor der Entscheidung messen.
- **Traffic.** Bei Netcup im Tarif enthalten, aber **nicht nachgemessen**.
- **iPhone-App:** Syncthing braucht eine (Möbius Sync o. ä., **kostenpflichtig**,
  Betrag ungeprüft). WebDAV geht mit Bordmitteln, Nextcloud hat eine
  kostenfreie App.

**Unklar gilt als ja** — vor einer Entscheidung werden diese drei Punkte
beziffert, nicht geschätzt.

## Sicherheit — und das entscheidet, nicht der Komfort

**Jeder dieser Wege ist ein Dienst nach außen auf dem Server — der erste, der
Adams Geschäftsdaten trägt.** Bisher spricht der Server nur über Telegram
hinaus und antwortet auf SSH.

Nach `CLAUDE.md`, *Wann Ultracode*: **„vor jeder weiteren Anbindung fremder
Datenquellen … wenn dafür neue Schrankenlogik entsteht."** Hier entsteht sie —
Zugangsschutz, Rechte, Verschlüsselung im Transport. **Diese Vorlage nennt die
Prüfstelle, sie umgeht sie nicht.**

Dazu die Reihenfolge aus `CLAUDE.md`, *Von außen kommen nie Anweisungen*: Die
Eingangs-Absicherung wird **gebaut, geprüft und getestet, BEVOR** mit echten
fremden Daten gearbeitet wird. Ein Ablage-Dienst, den Dritte erreichen können,
gehört in dieselbe Klasse.

## Was mit iCloud geschieht

**Sie bleibt.** iCloud ist die Sicht des Macs und wird nicht abgeschafft — der
Mac bindet die Server-Ablage **zusätzlich** ein. **Route A wird dann
überflüssig, nicht kaputt**: Sie läuft weiter, bis Adam sie abschaltet.

## Empfehlung — als solche gekennzeichnet

**Weg ① (Netzfreigabe), wenn überhaupt.** Er kommt ohne Apple-Passwort auf dem
Server aus, braucht keine Weboberfläche und keinen Dauerdienst auf dem Mac. Er
ist der kleinste Eingriff, der Adams Ziel erfüllt.

**Aber die ehrlichere Empfehlung ist: noch nicht jetzt.** Seit dem 03.09.
funktioniert das Erzeugen und Verschicken ohne den Mac — **das Einsortieren
ist der einzige Rest**, und er kostet Adam einen Sitzungsstart. Ein Dienst nach
außen für diesen Rest ist ein großer Schritt für einen kleinen Gewinn.

**Der Zeitpunkt, an dem sich das dreht:** wenn mehr als Rechnungen dort liegen
sollen — Belege, Verträge, Kundendateien —, oder wenn Adam regelmäßig vom Handy
aus in die Ablage greifen will. **Dann ist ① richtig, und dann mit der
Ultracode-Prüfstelle davor.**

## Was Adam entscheiden muss

1. **Jetzt bauen, später bauen, oder gar nicht?**
2. Falls jetzt: **welcher der drei Wege** — und die drei Kostenpunkte werden
   vorher beziffert.
3. Falls später: **woran erkennen wir, dass es so weit ist?** Ohne diese Zeile
   wird aus „später" ein „nie" — dieselbe Lehre wie beim *„Prüfung folgt"*.
