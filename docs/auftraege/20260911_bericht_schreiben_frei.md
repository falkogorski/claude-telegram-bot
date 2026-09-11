> **An Adam, zur Weitergabe an Engywuck** · Mick · 11.09.2026, 10:44 · gebaut: `73d378a` · Regressionslauf 85/85 · **kein Deploy**

**Zweck: ANSICHT + WEITERGABE → Engywuck** · **Zu tun: Adam — der Knopf wirkt erst nach einem Deploy**

# „✍️ Schreiben frei → bis Neustart" — gebaut, geprüft, nicht deployt

**Nenner:** ein Auftrag, fünf Prüfzeilen, sechs Gegenproben. Zwei vorhandene
Wächter haben den Bau gemeldet, beide zu Recht.

## Was gebaut ist

Ein dritter Umschalter in der Dauer-Tastatur, Muster wie Auto und Empfang: Der
Haken sagt den Stand, der Pfeil den Tipp-Effekt, **und die Beschriftung nennt
die Reichweite** — der Knopf ist der einzige Ort, an dem Adam sieht, dass die
Freigabe mit dem Neustart endet.

Vier Bedingungen, jede ein eigener Riegel: Flag an · eines der drei
Schreibwerkzeuge · **jeder** Pfad unter dem Arbeitsordner · nichts Heikles
berührt. Der Zweig steht **vor** der Always-Liste; `_NO_ALWAYS_TOOLS` bleibt
unverändert.

**Warum das keine Dauerfreigabe ist, und daran hängt der ganze Bau:** Das Flag
lebt **nur im Speicher**. Es endet mit dem Prozess, also spätestens beim
Hygiene-Neustart um vier. Die Fassung, die im August gefallen ist, lag in den
Vorlieben und überlebte ihn. Das Aufnahmekriterium jener Sperrliste lautet *„ein
Klick gilt danach unsichtbar fort"* — für eine sichtbare, örtlich begrenzte,
von selbst endende Reichweite trifft es nicht zu.

## Die sechs Gegenproben — drei davon haben etwas gezeigt

| Eingriff | Ergebnis |
|---|---|
| Geheimnis-Prüfung entfällt | rot: „Geheimnis" durchgerutscht |
| Arbeitsordner-Prüfung entfällt | rot: „Repo-Klon", „außerhalb" durchgerutscht |
| Flag wird nicht mehr gefragt | rot: alle drei Werkzeuge ohne Flag erlaubt |
| **Flag in die Vorlieben** | **erst beim zweiten Anlauf rot** |
| **`resolve()` entfällt** | **erst beim dritten Anlauf an der richtigen Zeile** |
| Knopf-Verdrahtung | über den Tastatur-Prüfstand mitgemessen |

**Der vierte Eingriff war zuerst gar keiner.** Ich hatte das Flag zusätzlich in
ein Dict im Speicher geschrieben — das überlebt den Prozess so wenig wie
vorher, also blieb die Zeile grün. Erst mit echtem Speichern auf die Platte
wurde sie rot. *Ein Eingriff, der dasselbe tut wie der Originalzustand, ist
keine Gegenprobe, und die Verwechslung sieht wie ein Ergebnis aus.*

**Der fünfte hat einen echten Fehler in meiner Prüfzeile gefunden.** Mein
`..`-Fall zielte aus dem Arbeitsordner in den Gedächtnis-Ordner. Entfernt man
die Pfadauflösung, bleibt er **trotzdem** gesperrt — gefangen von der
Geheimnis-Prüfung, nicht von der Pfadprüfung, die er messen sollte. Ein
zweites, **harmlos benanntes** `..`-Ziel machte den Unterschied sichtbar.
*Wo mehrere Riegel hintereinanderliegen, braucht jede Prüfzeile einen Fall, den
nur ihr Riegel fängt.*

Davor lag noch ein dritter Anlauf: Der Prüfstand lag unter `/var`, also hinter
einem Symlink, und verglich Aufgelöstes mit Nicht-Aufgelöstem. Bereinigt.

## Zwei Wächter haben gemeldet

- **Doku-Spiegel:** *„/hilfe behauptet 12 Knöpfe, Tastatur zeigt 13."*
- **Hermetik-Wächter:** `CLAUDE_ARBEITSORDNER` ohne Riegel im Läufer — ein
  Prüfer hätte gegen den **echten** `~/workspace` gemessen. Das ist die
  unangenehmere der beiden Meldungen.

Beides im selben Commit behoben.

## Was zu prüfen wäre

1. **`_im_arbeitsordner` erkennt Pfade über einen regulären Ausdruck**
   (`[~/]…`). Ein Aufruf, der seinen Pfad anders schreibt — relativ, ohne
   führenden Schrägstrich —, liefert **keinen Kandidaten** und fällt damit auf
   „nein". Das ist die sichere Richtung, aber es heißt: Solche Aufrufe fragen
   weiter, auch im Arbeitsordner. Ob `Write`/`Edit` je relative Pfade liefern,
   habe ich **nicht gemessen**.
2. **`NotebookEdit` ist bewusst draußen.** Es kommt im Alltag nicht vor; was
   nicht drückt, braucht keine Freigabe. Wenn du das anders siehst, ist es eine
   Zeile.
3. **Der Knopf schaltet, ohne den Agenten zu fragen** — er liegt im
   Tastatur-Zweig vor jedem Modelllauf. Gewollt, aber es heißt: Ein Druck
   kostet kein Kontingent und erscheint in keinem Protokoll außer dem Log.

## Und die Bedingung, die alles trägt

**Der Knopf wirkt erst nach einem Deploy.** Live läuft `495ca45`; dieser Bau
liegt im Hauptbaum. Solange nicht deployt ist, drückt Adam unterwegs genauso
viel wie vorher — das gehört ihm gesagt, bevor er sich darauf verlässt.
