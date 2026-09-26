# Bauauftrag: Das PDF-Werkzeug reparieren und das Schriftbild auffrischen

**Zustand: gültig** · verfasst 24.09.2026 · Claudia → Engywuck → Mick
**Anlass:** Am 24.09.2026 um 07:00 Uhr brach die PDF-Erzeugung ab. Adam um
07:22 Uhr: „PDFs dürfen grundsätzlich auch bei der Gelegenheit etwas
aufgefrischt, aufgehübscht werden. … Wir können uns ruhig an eine aufgeräumte,
moderne Optik gewöhnen."

---

## Auftrag 1 — der Abbruch (dringend, klein)

`scripts/konzept_pdf.py` bricht mit Rückgabewert 43 ab:

```
error: font fallback list must not be empty
```

**Ursache:** Das Skript reicht keine Hauptschrift an den Setzer weiter. Die
Vorlage von pandoc übergibt daraufhin eine leere Schriftliste, und typst
verweigert die Arbeit. `KONZEPT_PDF_SCHRIFTEN` behebt das nicht — die Variable
benennt den Schriftordner, nicht die zu verwendende Schrift.

**Zu tun:** Das Skript setzt `-V mainfont` und `-V monofont` selbst, mit einem
Vorgabewert, der auf dem Server vorhanden ist. Ein Schalter erlaubt das
Überschreiben.

**Heutiger Behelf** (funktioniert, aus dem Ordner der Quelle aufgerufen):

```
unshare -rn pandoc <quelle> -o <ziel> \
  --pdf-engine /home/claudebot/.local/bin/typst \
  -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono"
```

**Warum das dringlich ist:** Es trifft **jede** Sitzung, die ein PDF erzeugt.
Wer den Behelf nicht kennt, liefert kein PDF — oder gar nichts.

## Auftrag 2 — Schriftbild und Satzspiegel auffrischen

Die Vorgabe soll ein ruhiges, modernes Buchbild ergeben. Vorschläge, über die
Engywuck entscheidet:

- **Schrift:** eine gut lesbare Serifenlose für den Fließtext statt der
  Vorgabe-Serifenschrift; für Code eine Schrift fester Breite. Auf dem Server
  vorhanden ist die DejaVu-Familie; sind Inter, Source Sans oder IBM Plex
  verfügbar oder nachinstallierbar, sind sie die moderneren Kandidaten.
- **Satzspiegel:** Zeilenlänge auf etwa 70 bis 80 Zeichen begrenzen, Ränder
  großzügig, Zeilenabstand leicht erhöht.
- **Überschriften** in derselben Familie, abgestuft über Größe und Gewicht.
- **Tabellen** mit dünnen Linien und Luft in den Zellen.
- **Kopf- und Fußzeile** mit Titel und Seitenzahl.
- **Zustandskopf** des Dokuments optisch abgesetzt, damit „gültig" und
  „überholt" auf den ersten Blick auseinandergehen.

**Ein Gestaltungsblatt statt Schalter an jedem Aufruf.** Eine Vorlage, die das
Skript immer verwendet — damit gilt jede spätere Änderung sofort für alle
Dokumente, und niemand setzt sie an einzelnen Stellen nach.

**Grenze, die Adam selbst gezogen hat:** Nicht übertreiben und sich nicht damit
aufhalten. Ein ruhiges, aufgeräumtes Bild genügt; Gestaltung ist hier Mittel,
nicht Zweck.

## Was kann brechen und wer merkt es

| Bruch | Wer merkt es |
|---|---|
| Die gewählte Schrift fehlt auf dem Server, der Setzer bricht wieder ab | **Heute niemand.** Deshalb Pflicht: ein Selbsttest im 4-Uhr-Check, der ein kleines Dokument setzt und den Rückgabewert prüft |
| Die Vorlage bricht bei einer neuen Fassung von pandoc oder typst | Derselbe Selbsttest |
| Der Netz-Riegel des Skripts fällt beim Umbau weg | Ausdrücklich prüfen: Das Skript arbeitet bewusst ohne Netz (`unshare -rn`) und verweigert den Dienst, wenn kein Namensraum verfügbar ist. **Diese Eigenschaft bleibt** |
| Umlaute oder Sonderzeichen fehlen in der neuen Schrift | Selbsttest mit einem Text, der Umlaute, ß, Anführungszeichen und Gedankenstriche enthält |

## Reichweite

Was hier entsteht, ist die Gestaltung für **alles**, was das Projekt als Dokument
ausliefert — Bauaufträge, Konzepte, Befunde, Register, Regelwerke, Rechnungen.
Deshalb ein Gestaltungsblatt an einer Stelle und keine Einstellung je Aufruf.

Die Rechnungen sind dabei gesondert zu betrachten: Sie haben ein eigenes,
gewachsenes Aussehen und gehen an Kunden. **Nicht mit umstellen**, ohne das
eigens zu entscheiden.
