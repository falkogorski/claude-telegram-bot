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

## 💰 Die Kostenfrage — die Zahlen

**Gemessen auf dem VPS am 25.07.2026, 05:52 (geprüfte Zeit):**

| Größe | Wert |
|---|---|
| Platte gesamt | **250,7 GiB** |
| davon belegt | **16,7 GiB (6,6 %)** |
| davon frei | **223,8 GiB** |
| Arbeitsspeicher gesamt | **7940 MiB** |
| davon verfügbar | **6310 MiB** |
| davon in Benutzung | 1630 MiB |
| Kerne | 4 |
| heutiger Upload-Ordner | 87 MiB bei 151 Dateien; größte Einzeldatei 19 MiB |

**Hochrechnung für eine 2-GiB-Datei (Spitzenlast, alles gleichzeitig belegt):**

| Posten | Bedarf |
|---|---|
| Zwischenlager des API-Servers | 2,00 GiB |
| ~~eigene Kopie im Upload-Ordner~~ | **entfällt** — siehe Kasten |
| Einzelbilder + Übersichtsbögen (30-min-Video, 361 Bilder à ~300 KiB) | 0,10 GiB |
| **Spitze je Datei** | **2,10 GiB** |

> **Ein Fund, der die Rechnung halbiert (Conni, 25.07.):** Im `--local`-Betrieb
> gibt der Server **lokale Dateipfade** zurück statt eines Downloads. Die zweite
> 2-GiB-Kopie im Upload-Ordner entfällt damit vollständig. Das ist doppelt gut:
> unter demselben 30-GiB-Deckel passen **~14 statt 7** Dateien, und **weniger
> Kopien heißt weniger Orte mit persönlichen Medien** — der Datenschutz-Gewinn
> wiegt hier schwerer als der Platzgewinn.

**Was daraus folgt:** Mit dem **30-GiB-Deckel** liegen **rund vierzehn** solche
Dateien gleichzeitig, danach räumt die Regel auf. Ohne Deckel passten rein
rechnerisch über hundert — die Bremse ist also der Deckel, nicht die Platte.
Nach Abzug der 30 GiB bleiben **193,8 GiB frei**, mehr als das Elffache des
heutigen Gesamtbelegs.

**Arbeitsspeicher:** Der Dienst braucht einige hundert MiB; 6310 MiB sind
verfügbar. Kein Engpass.

**Gebühren:** Die Software ist kostenfrei, die Zugangsdaten von
`my.telegram.org` ebenfalls. **Telegram verlangt nichts.** Der Netcup-Server ist
bezahlt und muss nicht vergrößert werden — **kein einziger Cent zusätzlich.**

**Die eine Bedingung:** Ohne Aufräum-Regel wächst das Zwischenlager unbemerkt,
und auch 223,8 GiB sind irgendwann voll. Vorschlag: Deckel **30 GiB**, Dateien
nach **sieben Tagen** entfernen, Füllstand in den täglichen Funktionscheck (8.1)
— dann meldet sich das System, bevor es eng wird.

## Die fünf Auflagen aus Connis Prüfung (25.07., alle übernommen)

**① Der Token-Einwand schrumpft — die echte Gefahr ist enger.** Der Server
braucht beim Start nur `--api-id` und `--api-hash`; ein Bot-Token gehört nicht zu
seiner Konfiguration. Aber der Token **steht in den Anfragepfaden** — schreibt
der Dienst Zugriffsprotokolle, landet er in einer Logdatei. **Auflage:**
Protokollierung aus oder root-beschränkt, und diese Logs **nie** in den
Log-Abgleich.

**② `api_id`/`api_hash`: Geheimnis-Klasse ja, Kennwort-Gleichrang nein.** Sie
hängen an Adams persönlichem Konto, weisen aber eine **Anwendung** aus, keine
Sitzung — ein Abfluss ist keine Kontoübernahme (dafür braucht es Rufnummer plus
Anmeldecode). Bewusst nicht überzeichnet: Eine Entscheidung aus falscher Angst
wäre auch eine falsche Entscheidung.

**③ Von außen nicht erreichbar — festgeschrieben.** Ausgehend zu Telegram, vom
Bot über `127.0.0.1` erreicht: **kein eingehender Port, keine
Firewall-Freigabe, kein Reverse-Proxy.** Dieselbe Linie wie die rote Auflage
3.1.

**④ Das Zwischenlager erbt die strengste Einstufung, die dort auftreten kann —
nicht den Durchschnitt.** Es wird also **wie rot** behandelt: eigener
Dienstnutzer, Rechte `0700`, aus Log-Abgleich **und** Backup ausgeschlossen. Die
Aufräum-Regel ist technisch erzwungen (`api_cache_pflege.sh`), nicht
„vorgesehen", und der Füllstand steht im 4-Uhr-Check.

**⑤ Dauerbetrieb: Rückfall statt Stummheit.** Steht der lokale Server, schaltet
der Bot auf den öffentlichen Weg (20 MB) zurück **und sagt es** — dasselbe
Prinzip wie beim Sprach-Backend und beim Start-Wächter. Im Versions-Register als
`manual` geführt (aus Quellen gebaut wie whisper.cpp; eine Versionsabfrage wäre
eine Attrappe). Der 4-Uhr-Check prüft: Dienst lebt **und** Füllstand.

## Zwei offene Sicherheitsfragen (Conni, ungeprüft)

**Der offene Port 8443 könnte wegfallen.** Hält der lokale Server die Verbindung
zu Telegram, kann er die Webhook-Zustellung auf `localhost` liefern — dann wäre
der heute nach außen offene Port nicht mehr nötig. **Ein offener Port weniger
ist ein echter Gewinn**, kein Nebeneffekt. ⚠️ Das ist ein **Schluss, kein
Beleg** — gezielt prüfen, bevor es in die Planung geht.

**Plattenverschlüsselung — GEMESSEN am 25.07., und die Antwort ist unbequem.**
`/` liegt als **blankes ext4** auf `vda3`; es gibt **keine LUKS-Schicht und
keinen dm-crypt-Mapper** (`/dev/mapper` enthält nur `control`). Auf
Betriebssystem-Ebene ist die Platte also **nicht verschlüsselt**. Ob Netcup den
darunterliegenden Speicher verschlüsselt, lässt sich von innen **nicht**
feststellen — das müsste Netcup beantworten; als ungeprüft gekennzeichnet.

**Was daraus folgt, präzise formuliert:** „Auf unserem eigenen Server" heißt
**nicht** „nur wir können es lesen". Wer physischen Zugriff auf den Speicher hat,
kann die Daten technisch lesen. Das **entwertet den Weg nicht** — kein
Cloud-Konzern wertet die Inhalte aus, es gibt kein Profil, keine Weitergabe, und
der Unterschied zu einem Fremdanbieter bleibt groß. Aber die Werte-Charta darf
nicht „nur wir" behaupten, wo „niemand außer dem Rechenzentrumsbetreiber" richtig
ist. **Konsequenz für die Ampel:** Das Zwischenlager mit Medien erbt diese
Einordnung mit — ein Grund mehr für Auflage ④ (wie rot behandeln) und für den
Fund, dass die zweite Kopie entfällt.

## Rangfolge der Wege (Conni-Selbstkorrektur)

1. **5.34 — erste Wahl.**
2. **SFTP als echte Rückfallebene**, falls 5.34 an einer Auflage scheitert: Es
   läuft über den bereits offenen, gehärteten SSH-Zugang — **kein neuer Port,
   keine neuen Zugangsdaten, keine zusätzliche Angriffsfläche.** (Die frühere
   pauschale Ablehnung von „Alternative A" war zu grob; Nextcloud/WebDAV bleiben
   abgelehnt, weil sie einen von außen erreichbaren Dienst hinzufügen.)
3. **Aufteilen** und **Cloud-Link (nur grün)** als Notwege.
4. **Vorverkleinern löst das Problem nicht — es umgeht es.**

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
