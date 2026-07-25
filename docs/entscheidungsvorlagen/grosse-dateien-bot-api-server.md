<!-- ROLLE: entscheidungsvorlage-grosse-dateien -->
# Große Dateien: eigener Bot-API-Server (5.34)

> **Gültigkeits-Kopf** (Regel ⑪)
> **Stichtag:** 25.07.2026, 05:31 (geprüfte Zeit) · **Messung auf dem VPS an
> diesem Tag durchgeführt**
> **Überholt durch:** — (noch keine Nachfolge-Fassung)
> **Maßgeblich ist die Status-Zeile zu Punkt 5.34 im Master-Drehbuch
> `MIGRATION.md`.** Weicht dieses Dokument davon ab, gilt das Drehbuch.

## Worum es geht

Telegram gibt Bots über die öffentliche Schnittstelle höchstens **20 MB** pro
Datei heraus. Das ist **nicht unsere Grenze** — sie lässt sich nur umgehen,
indem man den **Bot-API-Server selbst betreibt**; Telegram stellt ihn als
quelloffene Software bereit. Damit steigt die Grenze auf **2 GB** pro Datei.
Für den Bot ist das eine Adresse in der Konfiguration, kein Umbau der Handler.

Adams Anlass (25.07., nach dem ersten Video-Test): „Wir brauchen auf jeden Fall
eine Funktion, wo auch große Videos und große Fotos oder Dateien generell
hochgeladen werden."

## 💰 Die Kostenfrage — gemessen, nicht geschätzt

**Ergebnis: keine zusätzlichen Kosten. Keine Aufrüstung nötig.**

| Was | Gemessen am 25.07.2026 | Bedarf des Dienstes | Urteil |
|---|---|---|---|
| Plattenplatz | **225 GB frei** von 251 GB (7 % belegt) | Zwischenlager, realistisch 20–50 GB | reicht mit großem Abstand |
| Arbeitsspeicher | **5,9 GB verfügbar** von 7,9 GB | einige hundert MB | reicht |
| Kerne | 4 | unkritisch | reicht |

**Gebühren:** Die Software ist kostenfrei, die Zugangsdaten von
`my.telegram.org` ebenfalls. **Telegram verlangt nichts.** Der Netcup-Server
ist bereits bezahlt und muss nicht vergrößert werden — es entsteht also
**kein einziger Cent zusätzlich.**

**Die eine Bedingung:** Das Zwischenlager muss begrenzt und aufgeräumt werden.
Ohne Aufräum-Regel wächst es unbemerkt, und 225 GB sind irgendwann auch voll.
Vorschlag: Obergrenze **30 GB**, Dateien nach **sieben Tagen** entfernen,
Füllstand in den täglichen Funktionscheck (8.1) aufnehmen — dann meldet sich
das System selbst, bevor es eng wird.

## Drei Punkte, die Conni zu Recht vorab sehen wollte

**🔐 Der Token lebt dann an einer zweiten Stelle.** Der eigene Server braucht
Bot-Token und die `my.telegram.org`-Zugangsdaten. Das erweitert die
Geheimnis-Fläche und gehört in die Geheimnis-Regel und in den Selbstcheck:
eigene, root-geschützte Umgebungsdatei, Leserechte nur für den Dienstnutzer,
und `_is_sensitive_ref` muss den neuen Pfad kennen — sonst ist er der einzige
Geheimnis-Ort, den der Bot lesen dürfte.

**🚦 Das Zwischenlager enthält alle Medien.** Fotos, Videos und
Sprachnachrichten liegen dann auf unserem Server statt nur bei Telegram — für
die Datenhoheit ein **Gewinn**, aber ein neuer Ort mit persönlichen Inhalten.
Er braucht eine Ampel-Einordnung und die oben genannte Aufräum-Regel; im
Zweifel gilt die vorsichtigere Einstufung.

**💾 Backup-Ausnahme — strukturell schon erfüllt.** Nachgesehen statt
angenommen: `scripts/vps_backup.sh` sichert eine **ausdrückliche Liste** von
Pfaden (Memory, Ampel-Regeln, Logs, zwei Konfigurationsdateien), nicht den
Baum. Ein neues Zwischenlager landet also **nur** im Backup, wenn jemand es
dort einträgt — was niemand tun soll. Der Punkt gehört trotzdem als Warnung ins
Abhängigkeits-Register, damit ein späterer „sichern wir doch alles"-Impuls
nicht 4.1 kippt.

## Bedienung, wie Adam sie vorgegeben hat

**Aktiv schaltbar**, mit dem Kostenhinweis davor. Da die Messung „null Euro"
ergibt, lautet der Hinweis beim Einschalten nicht „das kostet X", sondern
ehrlich: *keine Gebühren, kein Aufrüstungsbedarf; belegt wird Plattenplatz, bis
zu 30 GB, mit automatischem Aufräumen nach sieben Tagen.* Ausschalten führt
zurück auf den öffentlichen Weg mit der 20-MB-Grenze — der Rückweg bleibt also
immer offen.

## Was zu entscheiden ist

Nur eines: **Soll ich es einrichten?** Die Zahl steht, der Rückweg steht, die
drei Auflagen sind benannt. Gebaut wird erst nach Adams Ja.
