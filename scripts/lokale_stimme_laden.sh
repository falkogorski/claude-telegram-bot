#!/bin/bash
# <!-- ROLLE: lokale-stimme-laden -->
# 9.2: die Stimme Thorsten (Piper, Datensatz CC0) laden — Adams Hand beim
# Deploy, als claudebot auf dem VPS (oder am Mac). Adams Wort zum Download:
# 26.09.2026, 16:0x.
#
# Holt Modell und Beschreibung von Hugging Face (rhasspy/piper-voices) und
# prueft die Pruefsumme gegen den Wert in sprachausgabe_lokal.py. Stimmt sie
# nicht, wird die Datei verworfen — eine fremde Datei liegt nie am Ort, von
# dem der Bot liest. Ein zweiter Aufruf mit passender Datei tut nichts.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ZIEL="${TTS_LOKAL_MODELL:-$HOME/.local/share/piper-stimmen/de_DE-thorsten-medium.onnx}"
QUELLE="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium"
SOLL="$(sed -n 's/^MODELL_SHA256 = "\([0-9a-f]*\)"$/\1/p' "$REPO/sprachausgabe_lokal.py")"
[ ${#SOLL} -eq 64 ] || { echo "Pruefsumme in sprachausgabe_lokal.py nicht gefunden"; exit 1; }
summe() { if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -c1-64; else shasum -a 256 "$1" | cut -c1-64; fi; }

mkdir -p "$(dirname "$ZIEL")"
if [ -f "$ZIEL" ] && [ "$(summe "$ZIEL")" = "$SOLL" ] && [ -f "$ZIEL.json" ]; then
  echo "Stimme liegt schon, Pruefsumme stimmt: $ZIEL"; exit 0
fi
teil="$(mktemp "$(dirname "$ZIEL")/.teil-XXXXXX")"
trap 'rm -f "$teil" "$teil.json"' EXIT
curl -sfL -m 600 -o "$teil" "$QUELLE/$(basename "$ZIEL")"
curl -sfL -m 60 -o "$teil.json" "$QUELLE/$(basename "$ZIEL").json"
IST="$(summe "$teil")"
[ "$IST" = "$SOLL" ] || { echo "ABBRUCH: Pruefsumme stimmt nicht ($IST) — nichts abgelegt"; exit 1; }
mv "$teil.json" "$ZIEL.json"
mv "$teil" "$ZIEL"
echo "Stimme abgelegt, Pruefsumme stimmt: $ZIEL"
