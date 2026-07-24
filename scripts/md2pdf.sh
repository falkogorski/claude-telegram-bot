#!/usr/bin/env bash
# <!-- ROLLE: pdf-erzeugung -->
# C (Marschordnung II): Markdown → PDF auf dem VPS.
# Kette: pandoc + weasyprint (schlank, aus Debian-Repos, KEINE Sonderrechte,
# kein LaTeX-Klotz, kein Chromium). Font DejaVu Sans (Linux-vorhanden; Helvetica
# gibt es auf Linux nicht). Erfüllt die Datei-Regel „immer Original + PDF".
#
# Aufruf: scripts/md2pdf.sh INPUT.md [OUTPUT.pdf]
set -euo pipefail

IN="${1:?Aufruf: md2pdf.sh INPUT.md [OUTPUT.pdf]}"
OUT="${2:-${IN%.md}.pdf}"
STYLE="$(cd "$(dirname "$0")" && pwd)/pdf-style.css"

[ -f "$IN" ] || { echo "Eingabe fehlt: $IN" >&2; exit 1; }
[ -f "$STYLE" ] || { echo "Stil fehlt: $STYLE" >&2; exit 1; }

pandoc "$IN" -o "$OUT" \
  --pdf-engine=weasyprint \
  --css="$STYLE" \
  --metadata pagetitle="$(basename "${IN%.md}")" \
  --standalone

echo "$OUT"
