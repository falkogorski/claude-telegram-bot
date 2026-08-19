<!-- ROLLE: kurier-abmachung -->
# Der Kurier-Weg — wie Claudia mich während der Abwesenheit erreicht

> **Gültigkeits-Kopf** (Regel ⑪) · **Stichtag:** 28.07.2026 ·
> **Überholt durch:** — · **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> 💰 Kostenlage: null. Der Weg nutzt den vorhandenen Log-Abgleich.

## Das Problem, das er löst

Die Bot-Sitzung darf das Repo **nicht beschreiben** (8.7) — richtig so, das
Vier-Augen-Prinzip hängt daran. Bisher hieß das aber auch: Alles, was Claudia
erarbeitet, blieb in ihrem Gedächtnis liegen, bis ein Mensch es übertrug. In
vierzehn Tagen ohne Adam wäre das eine tote Leitung gewesen.

**Der Weg existierte bereits, er war nur nicht als solcher benannt.** Der
stündliche Log-Abgleich spiegelt `~/workspace` ins Log-Repo — gefiltert auf
Dokument-Endungen, mit harten Ausschlüssen für alles, was nach Geheimnis
aussieht.

## Wie er läuft

**Claudia legt ab** unter `~/workspace/an-mick/` — als `.md`, gern mit `.pdf`
daneben (Adams Doppel-Format). Alles andere wird vom Filter gar nicht erst
mitgenommen.

**Der Abgleich trägt** stündlich nach `logsync/claude-bot-logs/ausarbeitungen/`.
Kein Modell, keine Automatik, kein Zutun.

**Ich sehe täglich nach** — eine Zeile im Laufplan, kein Zeitgeber. Was ich
finde, wird nach der Regel unten behandelt.

## Die Regel, die den Weg vom Selbstläufer trennt

**Der Kurier ersetzt den Transport, nie die Prüfung.** Aus Claudias Ordner
wird **ausschließlich** gebaut:

- was **Conni bereits geprüft** hat (Korb B des Arbeitsplans), **oder**
- ein **Wächter-Befund mit bekanntem Lösungsweg** — also etwas, das eine
  gebaute Prüfung selbst gemeldet hat.

**Alles darüber hinaus wird nicht gebaut**, sondern als Prüfauftrag für die
Kontrollsitzung formuliert und im Freigabe-Postfach geparkt — **auch wenn es
gut aussieht, auch wenn es klein ist.** Genau bei „klein und gut aussehend"
fängt das Abrutschen an.

**Warum diese Härte:** Ohne sie wäre der Kurier kein Transportweg, sondern eine
zweite Bauleitung ohne Gegenlesung. Das Vier-Augen-Prinzip überlebt nicht die
Bequemlichkeit, sondern nur die ausdrückliche Regel.

## Was kann brechen und wer merkt es

| Bruchstelle | Wirkung | Wer merkt es |
|---|---|---|
| Der Abgleich läuft nicht mehr | Claudias Ablagen erreichen mich nie — es sieht aus wie „sie hat nichts geschickt" | Der 4-Uhr-Lauf prüft den Zeitgeber; zusätzlich fällt es beim täglichen Nachsehen auf, weil das Datum stehenbleibt |
| Ich sehe nicht täglich nach | Dasselbe, nur von meiner Seite | **Niemand** — deshalb steht es als Zeile im Laufplan, den die Durchlauf-Wache liest |
| Ich baue etwas Ungeprüftes, weil es gut aussieht | Eine Änderung ohne Gegenlesung, in genau der Zeit, in der niemand widersprechen kann | **Niemand sofort** — die nachlaufende Gesamtabnahme (~13.–15.08.) fängt es, aber spät. Der Riegel ist die Regel oben, nicht ein Prüfer |
| Ein Geheimnis rutscht durch den Filter | Vertrauliches im Log-Repo | Die Ausschlüsse im Abgleich, **plus Nachmessen**: Am 28.07. lag dort noch ein `.pdfenv`-Verzeichnis — vom Filter längst gedeckt, aber `rsync` ohne `--delete` hatte es nie geräumt. Geprüft (keine Schlüsselmuster, null Commits), entfernt |
| Claudia legt in den falschen Ordner | Kommt nicht an, niemand vermisst es | Sie sieht es selbst — der Abgleich meldet, was er mitgenommen hat |

## Der Soll-Zustand nach der Rückkehr

Ab ~13.–15.08.: **Claudia → Kontrollsitzung prüft → ich baue**, mit direktem
Lesezugriff der Kontrollsitzung auf das Log-Repo ab Sitzungsstart. Der
Kurier-Weg bleibt dann als Transport bestehen; nur die Prüfung wandert vom
Papier in die laufende Sitzung. Das ist Rückkehr-Entscheid Nr. 2.

## Der Lesestand-Befehl — hier, nicht im Chat

**`[NEU 2026-08-18]` Befehle reisen nicht im Chat, sie stehen im Repo.** Dieser
Befehl ist beim Weiterleiten über Telegram **zweimal verschwunden** —
Codeblöcke überleben das Kopieren nicht zuverlässig. Also steht er dort, wo
Claudia ohnehin nachsieht; im Chat genügt der Verweis auf diese Stelle.

Vor jeder Ausarbeitung den eigenen Lesestand ermitteln:

    git -C ~/claude-telegram-bot log -1 --format='%h · %ad' --date=format:'%d.%m.%Y, %H:%M'

Das Ergebnis gehört in den **Kopf jeder Ausarbeitung**. Der VPS-Klon wird nur
durch einen Deploy aktualisiert und kann deshalb älter sein als das, was gilt —
ein Bauauftrag auf altem Stand kostet beide Seiten Zeit.

**Ohne Umleitung schreiben.** `git -C …` allein ist der dokumentierte Weg; ein
angehängtes `2>/dev/null` lässt der Repo-Wächter derzeit nicht durch (Claudias
Befund vom 18.08., mit dreizehn Befehlen nachgemessen — er wertet das
`>`-Zeichen als Schreibversuch, sobald ein Repo-Pfad im selben Befehl steht).
Die Regel wird geschärft; bis dahin gilt der Weg ohne Umleitung.

Ein `git fetch` ist **nicht** nötig und **nicht** erlaubt — der Repo-Zugriff
bleibt reines Lesen (8.7). Der Lesestand genügt.

## Die Quittung — was der Abgleich mitgenommen hat

`[NEU 2026-08-19]` Nach jedem Lauf liegt im Ablage-Ordner
`letzter-abgleich.txt`: Zeitstempel, **was mitkam** — und **was nicht, samt
Grund je Datei**.

**Warum es das gibt:** Diese Abmachung versprach schon vorher „der Abgleich
meldet, was er mitgenommen hat". Das Skript tat es nicht. Dritter Fund
derselben Klasse an einem Tag — eine Vorgabe, die nur auf dem Papier stand.
Claudia fragte daraufhin, ob sie „morgen nachsehen" solle, ob ihre Fracht
angekommen sei; diese Frage beantwortet die Quittung ab jetzt von selbst.

**Der Geheimnis-Namensfilter bleibt hart — aber nicht lautlos.** Eine
Ausarbeitung über „Token-Optimierung" darf ausgefiltert werden, weil ihr Name
ein Schlüsselwort trägt; nur nie stillschweigend. **Sichtbar aussortiert ist
sicher und ehrlich; lautlos aussortiert ist die nächste Stille, die wie Ruhe
aussieht.**

Steht in der Quittung eine Datei mit dem Grund „unklar — bitte melden", ist das
ein Fehler auf unserer Seite: Sie hätte mitkommen sollen. Sag Bescheid.

## Nachtrag zum Lesestand-Befehl `[19.08.2026]`

Der Repo-Wächter ist geschärft: **Fehlerumleitungen sind erlaubt.**
`git -C … log -1 2>/dev/null` und `2>&1` laufen jetzt ohne Freigabe-Dialog.

Claudias Befund war dabei genauer als meine Erwartung — sie hat ihre eigene
erste Diagnose widerlegt: Nicht das `cd` war der Auslöser, sondern das `>`, und
ihr vermeintlicher Ausweg über `git -C` lief nur, weil er zufällig keine
Umleitung enthielt.

**Zwei Präzisierungen aus der Gegenprüfung:** „Abgelehnt" hieß nie *blockiert*,
sondern *fällt in den Freigabe-Dialog* — ein Unterschied, der in der Diagnose
fehlte. Und der Fix musste an **zwei** Stellen greifen: Die Lockerung im
Lese-Zweig half zunächst gar nichts, weil er die Schreibprüfung als doppelten
Boden befragt und deren Muster das `>` ebenfalls sah.

Was weiterhin in den Dialog fällt, sagt jetzt **welches Zeichen** es war.
