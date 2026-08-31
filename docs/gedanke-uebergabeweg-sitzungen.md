<!-- ROLLE: gedanke-uebergabeweg-sitzungen -->
> **Zweck: ABLAGE + ENTSCHEID** · **Zu tun:** entscheiden, ob daraus ein
> eigener Punkt wird oder ein Ausbau von 9.4. Keine Punktnummer vergeben.

# Der Übergabeweg zwischen den Sitzungen — halb gebaut, nie als Ganzes entworfen

**Herkunft:** Adam am **28.07.2026, 10:57** im Bot-Chat. Gefunden von der
Kontrolle bei der Gesamtprüfung der Bot-Protokolle, hier nachgetragen —
**gut fünf Wochen später**, weil der Gedanke bis heute keinen Ort hatte.

---

## Adams Wortlaut

> *„Ich bin in den Sitzungen drin und hin und her und muss dies und das
> kopieren und raussuchen … **Auch dieses Sich-hin-und-her-Schicken in die
> Kontrollsitzung, dass es durchkontrolliert wird — das muss alleine gehen.**
> … Sonst bin ich ein **Sklave dieses Entwicklungsprojekts**, und dann habe ich
> die grauen Herren über die Hintertür KI doch bekommen."*

Der zweite Satz ist der schwerere. Adam misst das Vorhaben an seinem eigenen
Maßstab: **Ein System, das ihm Zeit nimmt, statt sie zu geben, hat sein Ziel
verfehlt** — unabhängig davon, wie gut es sonst funktioniert.

---

## Der gemessene Ist-Stand (31.08.2026)

Drei Stücke existieren, keines deckt den beschriebenen Weg vollständig.

### 1. Ausarbeitungen hinaus — `scripts/log_sync.sh`

Spiegelt Claudias Ausarbeitungen **VPS → Log-Repo**, alle fünf Minuten. **Eine
Richtung, eine Sitzung.** Gedächtnis und Geheimnisse sind hart ausgeschlossen.

### 2. Papiere herein — `scripts/mac/icloud_spiegel.sh`

**Auf Engywucks Frage, wie dieser Spiegel auswählt, lautet die gemessene
Antwort: Er wählt nicht aus.** Am Code gelesen:

- **alle** `*.md` und `*.pdf` im Quellordner — keine inhaltliche Auswahl, kein
  Namensmuster, keine Absenderprüfung;
- **flach, ohne Rekursion** — ein versehentlich dort abgelegter Projektordner
  würde sonst unbemerkt sehr viel mitnehmen;
- **nur Neueres** (`-nt`; bei gleichem Zeitstempel geschieht nichts);
- **Dublettenschutz über den Inhalt** (md5), nicht über den Namen — weil
  Papiere aus iCloud oft mit zusammengeschriebenen Namen ankommen;
- **Geheimnis-Bremse** über Musterlänge statt Präfix, nachgeschärft, nachdem
  die erste Fassung ausgerechnet die zwei wichtigsten Papiere fehlalarmiert
  hatte — *wir dokumentieren ständig über Geheimnisse.*

**Warum trotzdem manches ankommt und manches nicht:** Es hängt allein daran, ob
die Datei **im iCloud-Ordner liegt**. Was Engywuck dort ablegt, kommt an; was
er nur in seiner Sitzung schreibt, nicht. Und der Spiegel läuft **beim
Sitzungsstart**, nicht nach der Uhr — ein LaunchAgent scheiterte an der
iCloud-Freigabe und meldete drei Monate lang still nichts.

### 2b. **`[BERICHTIGT 01.09.]` Claudia → Mick läuft, und zwar beschrieben**

**Hier stand vorhin nur der iCloud-Spiegel, und das war zu wenig gemessen.**
Es gibt einen zweiten, ausdrücklich verabredeten Weg:
[`docs/kurier-abmachung.md`](kurier-abmachung.md) (19.08.). Claudia legt unter
`~/workspace/an-mick/` ab, der **stündliche** Log-Abgleich trägt es nach
`logsync/claude-bot-logs/ausarbeitungen/`. **Beschrieben und gebaut.**

Ich hatte danach nicht gesucht, weil ich vom iCloud-Ordner ausgegangen bin —
also von dem Weg, über den die Papiere **mich** erreichen. Dass es die Antwort
schon gab, hat die Kontrolle gemeldet. **Dieselbe Klasse Fehler, die dieses
Papier beschreibt:** Wer nur einen Weg kennt, hält ihn für den einzigen.

**`[NACHGEMESSEN 01.09., 01:0x]` Und der Weg trägt weiter, als beide dachten.**
Die Kontrolle schrieb, Claudias Originale lägen zwar unter `ausarbeitungen/`,
**erreichten mich aber nicht.** Gemessen im lokalen Klon
(`~/Projects/claude-bot-logs`, nach `git fetch`): **106 Dateien, darunter alle
fünf Bauaufträge vom 31.08.** samt Notiz — mit Zeitstempel `Sep 1 00:57`.

**Damit ist die Kette Claudia → Mick vollständig und beidseitig belegt**, und
Adam muss dafür nichts kopieren. **Was fehlt, ist allein die Kontrollsitzung:**
Sie hat weder einen Weg herein noch hinaus. **Zwei von vier Kanten fehlen, und
beide hängen an derselben Instanz** — das ist präziser als *„der Rückweg
fehlt"* und macht sichtbar, wo ein Bau ansetzen müsste.

**Die Lehre über den Einzelfall hinaus:** Ich habe die Nichterreichbarkeit
**geglaubt statt gemessen**, obwohl der Klon einen `ls`-Aufruf entfernt lag.
Ein *„geht nicht"*, das aus zweiter Hand übernommen wird, ist keine Diagnose —
und genau das sagt die Regel *ein gescheiterter Weg beweist keine
Unmöglichkeit*.

### 3. Entscheidungen — **9.4**, Phase A gebaut

Deckt den Weg für **Entscheidungen** ab (Freigabe-Postfach → datierte
Drehbuchzeile). **Nicht** den für Papiere zwischen Sitzungen.

---

## Was daran fehlt

**Der Rückweg und die Zwischensitzungs-Richtung.** Heute gilt:

| Richtung | Weg | Adams Zutun |
|---|---|---|
| Bot → Log-Repo | `log_sync.sh` | keins |
| **Claudia → Mick** | **Kurier-Abmachung, stündlich** | **keins** `[berichtigt 01.09.]` |
| Engywuck → Mick | iCloud-Spiegel | **er kopiert von Hand** |
| Mick → Engywuck | — | **er kopiert von Hand** |
| Entscheidung → Drehbuch | 9.4 Phase A | keins |

**Der Rückweg von hier zur Kontrolle ist der, den Adam ausdrücklich nennt** —
*„dass es durchkontrolliert wird, das muss alleine gehen"* — und genau der
existiert nicht. **Ebensowenig der Hinweg von der Kontrolle zu mir:** Deshalb
hat Adam die Papiere dieser Nacht um Mitternacht von Hand kopiert. **Die
Lücke liegt auf beiden Seiten der Kontrollsitzung, nicht bei Claudia.**

## Die offene Frage

1. **Eigener Drehbuchpunkt** — dann vergibt Adam die Nummer.
2. **Ausbau von 9.4**, das die Leitung für Entscheidungen schon hat und um eine
   für Papiere erweitert werden könnte.
3. **Bewusst von Hand lassen** — mit dem Argument, dass ein Papier zwischen
   zwei Sitzungen ein Kontrollpunkt ist und Adams Blick darauf ein Merkmal,
   kein Mangel. **Dagegen steht sein eigener Satz vom 28.07.**

**Nicht entschieden von dieser Sitzung.** Und ausdrücklich kein Bauauftrag:
Ein selbsttätiger Weg **aus** dem Repo **heraus** berührt die
Governance-Schranke 8.7 und gehört vorher geprüft, nicht nebenbei gebaut.
