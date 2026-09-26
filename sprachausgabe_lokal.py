#!/usr/bin/env python3
# <!-- ROLLE: sprachausgabe-lokal -->
"""Die lokale Stimme für Rotes — Drehbuch 9.2 (26.09.2026).

**Wozu:** Was die Ampel als rot einstuft, verlässt das Haus nicht — auch nicht
als Ton. Azure und edge-tts sind Microsoft-Dienste; diese Stimme rechnet auf
dem eigenen Rechner (Piper, Modell `de_DE-thorsten-medium`, Datensatz CC0).

**Adams Anforderung vom 25.08.:** *„zwei unterschiedliche Sprecher. Damit wird
sofort klar, wenn etwas über Rot läuft."* Deshalb eine Männerstimme neben
Katja: Der Unterschied ist zum Hören da, nicht zum Lesen.

**Adams Wort zum Download:** 26.09.2026, 16:0x (Drehbuch (80)).

Telegram nimmt für Sprachnachrichten OGG/Opus, MP3 oder M4A — kein WAV.
Piper liefert WAV; `ffmpeg` macht daraus Opus. Fehlt eines davon, ist die
Stimme nicht bereit, und der Bot verhält sich wie vor 9.2.

Einstellungen (Umgebung):
    TTS_ROT_LOKAL      an (Vorgabe) | aus
    TTS_LOKAL_MODELL   Pfad zur .onnx-Datei (Vorgabe: ~/.local/share/piper-stimmen/
                       de_DE-thorsten-medium.onnx; die .onnx.json daneben)

Aufruf `python3 sprachausgabe_lokal.py --probe` (Tagescheck 9s):
    OK <Zeile>  |  AUS <Grund>  |  FEHLER <Grund>
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

MODELL_NAME = "de_DE-thorsten-medium.onnx"
# Pruefsumme der Datei bei Hugging Face (rhasspy/piper-voices), am 26.09.2026
# gegen den Download gehalten.
MODELL_SHA256 = "7e64762d8e5118bb578f2eea6207e1a35a8e0c30595010b666f983fc87bb7819"
PROBESATZ = "Guten Tag. Die lokale Stimme ist bereit, am zweiundzwanzigsten Juni um zwanzig Uhr fünf."

_stimme = None
_sperre = threading.Lock()


def schalter() -> bool:
    return (os.environ.get("TTS_ROT_LOKAL") or "an").strip().lower() not in ("aus", "0", "nein", "off")


def modell() -> Path:
    wert = os.environ.get("TTS_LOKAL_MODELL")
    return Path(wert) if wert else Path.home() / ".local" / "share" / "piper-stimmen" / MODELL_NAME


def ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def grund() -> str:
    """Warum die Stimme NICHT bereit ist — leer, wenn sie es ist."""
    if not schalter():
        return "ausgeschaltet (TTS_ROT_LOKAL=aus)"
    try:
        import piper  # noqa: F401
    except Exception:
        return "piper-tts nicht installiert"
    m = modell()
    if not m.is_file() or not Path(str(m) + ".json").is_file():
        return f"Stimme fehlt ({m.name} samt .json)"
    if not ffmpeg():
        return "ffmpeg fehlt"
    return ""


def bereit() -> bool:
    return grund() == ""


def _laden():
    global _stimme
    with _sperre:
        if _stimme is None:
            from piper import PiperVoice
            _stimme = PiperVoice.load(str(modell()))
        return _stimme


def wav(text: str) -> bytes:
    stimme = _laden()
    puffer = io.BytesIO()
    with wave.open(puffer, "wb") as w:
        stimme.synthesize_wav(text, w)
    return puffer.getvalue()


def sprechen(text: str) -> bytes:
    """Text → OGG/Opus für Telegram. Blockiert; der Bot ruft es in einem Faden."""
    roh = wav(text)
    lauf = subprocess.run(
        [ffmpeg() or "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "wav", "-i", "pipe:0",
         "-c:a", "libopus", "-b:a", "32k", "-f", "ogg", "pipe:1"],
        input=roh, capture_output=True, timeout=120)
    if lauf.returncode != 0 or not lauf.stdout.startswith(b"OggS"):
        raise RuntimeError(f"ffmpeg rc={lauf.returncode}: {lauf.stderr.decode(errors='replace')[-160:]}")
    return lauf.stdout


def probe() -> str:
    """Eine Zeile für den Tagescheck: spricht die Stimme, und wie schnell?"""
    g = grund()
    if g:
        return f"AUS {g}"
    try:
        _laden()                     # das Laden zaehlt nicht zur Sprechzeit
        t0 = time.monotonic()
        roh = wav(PROBESATZ)
        dauer = time.monotonic() - t0
        with wave.open(io.BytesIO(roh)) as w:
            sekunden = w.getnframes() / w.getframerate()
        sprechen("Probe.")
    except Exception as e:
        return f"FEHLER {type(e).__name__}: {e}"
    faktor = sekunden / dauer if dauer > 0 else 0
    return (f"OK Lokale Stimme spricht: {sekunden:.1f} s Ton in {dauer:.1f} s "
            f"({faktor:.0f}-fach Echtzeit)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--probe"]:
        print(probe())
        sys.exit(0)
    print(__doc__.split("Aufruf")[1], file=sys.stderr)
    sys.exit(2)
