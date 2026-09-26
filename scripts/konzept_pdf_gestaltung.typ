// <!-- ROLLE: pdf-gestaltungsblatt -->
// Gestaltungsblatt fuer alle Papiere aus scripts/konzept_pdf.py (26.09.2026).
//
// Claudias Auftrag vom 24.09., Adams Wort: "eine aufgeraeumte, moderne Optik"
// — und seine Grenze: nicht uebertreiben, nicht aufhalten. EIN Blatt an einer
// Stelle; jede Aenderung hier gilt sofort fuer jedes Papier.
//
// Schrift, Groesse, Raender und Sprache kommen NICHT von hier, sondern als
// pandoc-Variablen aus konzept_pdf.py: Die pandoc-Fassungen setzen dieses
// Blatt an verschiedene Stellen (3.1 hinter die Grundeinstellungen der
// Vorlage, 3.10 davor). Was die Vorlage selbst setzt, wuerde hier je nach
// Fassung gewinnen oder verlieren — deshalb steht hier nur, was sie nicht
// anfasst.
//
// Die Rechnungen benutzen dieses Blatt NICHT (Claudias Auflage).
//
// `dokumenttitel` setzt konzept_pdf.py vor dieses Blatt.

#set par(leading: 0.78em, spacing: 1.15em)

#set page(
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 8pt, fill: luma(120))
      dokumenttitel
      v(-0.4em)
      line(length: 100%, stroke: 0.4pt + luma(210))
    }
  },
  footer: context {
    set text(size: 8pt, fill: luma(120))
    h(1fr)
    [Seite #counter(page).display() von #counter(page).final().first()]
  },
)

#show heading: set block(above: 1.5em, below: 0.7em)
#show heading: set text(hyphenate: false)
#show heading.where(level: 1): set text(size: 17pt, weight: "bold")
#show heading.where(level: 2): set text(size: 13.5pt, weight: "bold")
#show heading.where(level: 3): set text(size: 11.5pt, weight: "bold")

#set table(stroke: 0.5pt + luma(190), inset: (x: 7pt, y: 5pt))
#show table.cell.where(y: 0): set text(weight: "bold")

#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, it)
#show raw: set text(size: 8.8pt)

#show link: set text(fill: rgb("#1f5fa8"))

// Der Zustandskopf eines Papiers (Zeile "**Zustand: ...**" oder
// "**Zweck: ...**"), von konzept_pdf.py mit einer dieser Funktionen umrahmt.
#let zustand-gueltig(body) = block(
  fill: rgb("#eef4ec"), stroke: (left: 3pt + rgb("#4f8a4a")),
  inset: (x: 10pt, y: 8pt), width: 100%, body)
#let zustand-ueberholt(body) = block(
  fill: rgb("#fbefe3"), stroke: (left: 3pt + rgb("#c26a1a")),
  inset: (x: 10pt, y: 8pt), width: 100%, body)
#let zustand-kopf(body) = block(
  fill: luma(243), stroke: (left: 3pt + luma(150)),
  inset: (x: 10pt, y: 8pt), width: 100%, body)
