"""Pluggable Speech-to-Text backend.

Drop-in interface — swap WhisperCppTranscriber for an OpenAI/cloud variant later
by changing STT_BACKEND in .env. All implementations take a raw audio file path
and return the transcribed text (or raise).

Audio coming from Telegram is OGG/Opus; ffmpeg converts to the 16 kHz mono WAV
that whisper.cpp expects.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

log = logging.getLogger("claude-tg-bot.transcribe")

# Whisper nutzt alle CPU-Kerne (threads = cpu_count) — mehrere parallele Läufe
# verdrängen sich gegenseitig und werden ZUSAMMEN langsamer als nacheinander
# (live 22.07.: drei schnell hintereinander gesendete Voices → Stau, drei
# whisper-Prozesse gleichzeitig). Ein Semaphore serialisiert die CPU-gebundene
# Transkription; die billige ffmpeg-Konvertierung läuft bewusst AUSSERHALB der
# Sperre, damit Wartende ihre WAV schon fertig haben, wenn sie drankommen.
_WHISPER_SEM = asyncio.Semaphore(1)


class Transcriber(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        """Return transcribed text from an audio file. Raise on failure."""


class WhisperCppTranscriber(Transcriber):
    """Local whisper.cpp via the `whisper-cli` binary (brew install whisper-cpp).

    Audio is converted to 16 kHz mono WAV via ffmpeg before transcription.
    """

    def __init__(
        self,
        model_path: Path,
        binary: str = "whisper-cli",
        ffmpeg: str = "ffmpeg",
        threads: int | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise FileNotFoundError(f"whisper model not found: {self.model_path}")
        self.binary = shutil.which(binary) or binary
        self.ffmpeg = shutil.which(ffmpeg) or ffmpeg
        # Standard: ALLE CPU-Kerne (Transkription ist die vom Nutzer erwartete
        # Wartezeit — der Bot hat währenddessen kaum anderes zu tun). Frühere
        # Heuristik cpu_count()-2 verschenkte auf dem 4-Kern-VPS die Hälfte.
        # Override per WHISPER_THREADS env, falls doch Kopf-Raum gewünscht.
        env_threads = 0
        try:
            env_threads = int(os.environ.get("WHISPER_THREADS") or 0)
        except ValueError:
            env_threads = 0
        self.threads = threads or env_threads or (os.cpu_count() or 4)

    def set_model(self, model_path: str | Path) -> None:
        """Aktives Modell zur Laufzeit wechseln (STT-Umschalter). Prüft Existenz."""
        p = Path(model_path)
        if not p.is_file():
            raise FileNotFoundError(f"whisper model not found: {p}")
        self.model_path = p

    async def _convert_to_wav(self, src: Path) -> Path:
        wav = src.with_suffix(".wav")
        # 16-bit signed PCM, mono, 16 kHz — what whisper.cpp wants
        cmd = [
            self.ffmpeg,
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(src),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(wav),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {stderr.decode(errors='replace')[:400]}")
        return wav

    async def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        # Wird als Zeichenkette übergeben, greift `with_suffix` nicht — beim
        # Gegenmessen am 25.07. genau so aufgelaufen. Der Bot übergibt zwar
        # immer einen Pfad, aber eine Schnittstelle, die nur bei einem von zwei
        # Backends str verträgt, ist eine Falle für den nächsten Aufrufer.
        wav = await self._convert_to_wav(Path(audio_path))
        try:
            cmd = [
                self.binary,
                "-m", str(self.model_path),
                "-f", str(wav),
                "-t", str(self.threads),
                "-nt",          # no timestamps
                "-np",          # no print of progress/info
                "-otxt",        # write <wav>.txt
            ]
            if language:
                cmd += ["-l", language]
            # Serialisierung CPU-gebundener Arbeit: immer nur EIN whisper-Prozess.
            async with _WHISPER_SEM:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(
                    f"whisper-cli failed: {stderr.decode(errors='replace')[:400]}"
                )
            txt_file = wav.with_suffix(".wav.txt")
            text = ""
            if txt_file.is_file():
                text = txt_file.read_text(encoding="utf-8", errors="replace").strip()
                txt_file.unlink(missing_ok=True)
            if not text:
                # fallback: whisper-cli also prints to stdout when -otxt isn't honored
                text = stdout.decode(errors="replace").strip()
            return text
        finally:
            wav.unlink(missing_ok=True)


class FasterWhisperTranscriber(Transcriber):
    """Lokale Transkription über faster-whisper (CTranslate2) — Adam-Entscheid 25.07.

    **Warum umgestellt wurde:** Der abgenommene Benchmark auf dem VPS (4 Threads,
    int8, echte Adam-Sprachnachrichten) ergab bei gleicher Modellstufe
    **6,3-fach** (131-Sekunden-Voice: 36,8 s → 21,0 s) bzw. **7,1-fach**
    (9-Minuten-Voice: 143 s → 75 s) schnellere Verarbeitung bei gleicher oder
    leicht besserer Textqualität. Die Transkription war laut Adams eigenem
    Befund der einzige spürbare Engpass der Antwortkette.

    Drei Eigenschaften bleiben bewusst erhalten:
    * **Dieselbe Sperre `_WHISPER_SEM`** — das Abhängigkeits-Register warnt
      ausdrücklich, dass ein Tempo-Ausbau sie übernehmen MUSS; ohne sie kehrt
      der Ressourcen-Kollaps vom 22.07. zurück.
    * **Lokal und kostenfrei** — kein Netz zur Laufzeit, keine Gebühren.
    * **Das Modell wird einmal geladen** und bleibt im Speicher; der
      Lade-Aufwand fällt im Dauerbetrieb also nur beim ersten Mal an.
    """

    # Modellstufen des Umschalters (5.22) → faster-whisper-Bezeichner.
    _STUFEN = {"small": "small", "medium": "medium", "large": "large-v3",
               "base": "base", "tiny": "tiny"}

    def __init__(self, model_size: str = "small", threads: int | None = None,
                 compute_type: str = "int8") -> None:
        try:
            from faster_whisper import WhisperModel     # noqa: PLC0415
        except ImportError as e:                        # pragma: no cover
            raise RuntimeError(
                "faster-whisper ist nicht installiert — "
                "`pip install faster-whisper` in der venv des Bots") from e
        env_threads = 0
        try:
            env_threads = int(os.environ.get("WHISPER_THREADS") or 0)
        except ValueError:
            env_threads = 0
        self.threads = threads or env_threads or (os.cpu_count() or 4)
        self.compute_type = compute_type
        self._WhisperModel = WhisperModel
        self.model_size = self._STUFEN.get(model_size, model_size)
        self.model = self._laden(self.model_size)

    def _laden(self, size: str):
        return self._WhisperModel(size, device="cpu",
                                  compute_type=self.compute_type,
                                  cpu_threads=self.threads)

    def set_model(self, model_path: str | Path) -> None:
        """Stufe wechseln (5.22). Nimmt „small"/„medium" ODER einen Dateipfad an.

        Der Umschalter im Bot übergibt historisch **Pfade** zu ggml-Dateien.
        Damit der Knopf weiter funktioniert, wird die Stufe aus dem Dateinamen
        gelesen — ein Umbau der Oberfläche wäre sonst Bedingung für den
        Backend-Wechsel gewesen, und das wäre die falsche Reihenfolge.
        """
        wunsch = str(model_path)
        stufe = None
        for name in self._STUFEN:
            if name in wunsch.lower():
                stufe = name
                break
        stufe = self._STUFEN.get(stufe or wunsch, wunsch)
        if stufe == self.model_size:
            return
        self.model = self._laden(stufe)       # erst laden, dann übernehmen
        self.model_size = stufe

    def _lauf(self, audio_path: Path, language: str | None) -> str:
        segmente, _info = self.model.transcribe(
            str(audio_path), language=language, beam_size=5,
            vad_filter=True)                  # Stille überspringen
        return " ".join(s.text.strip() for s in segmente).strip()

    async def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        # Rechenarbeit in einen Faden auslagern, damit der Bot antwortfähig
        # bleibt; die Sperre serialisiert wie bisher auf EINEN Lauf.
        async with _WHISPER_SEM:
            return await asyncio.to_thread(self._lauf, Path(audio_path), language)


class NullTranscriber(Transcriber):
    """Used when STT is disabled; surfaces a user-facing hint."""

    async def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        raise RuntimeError("STT backend is disabled (STT_BACKEND=off). Send text instead.")


def build_transcriber() -> Transcriber:
    """Factory — reads .env and returns the configured backend.

    Add a new STT_BACKEND value here (e.g. "openai") to wire in another impl;
    the rest of the bot doesn't change.
    """
    # Vorgabe seit Adams Entscheid 25.07.: faster-whisper. whisper.cpp bleibt
    # als Rückweg genau eine Umgebungsvariable entfernt (STT_BACKEND=whisper_cpp).
    backend = (os.environ.get("STT_BACKEND") or "faster_whisper").lower().strip()

    if backend == "off":
        return NullTranscriber()

    if backend == "faster_whisper":
        stufe = os.environ.get("STT_MODEL_SIZE") or "small"
        try:
            return FasterWhisperTranscriber(model_size=stufe)
        except Exception as e:
            # Kein stiller Ausfall der Voice-Kette: Wenn faster-whisper hier
            # nicht trägt, wird auf den bewährten Weg zurückgefallen — aber
            # LAUT, damit der Rückfall nicht als Normalzustand durchgeht.
            logging.getLogger(__name__).error(
                "faster-whisper nicht verfügbar (%s) — falle auf whisper.cpp "
                "zurück. Das ist ein Befund, kein Normalzustand.", e)
            backend = "whisper_cpp"

    if backend == "whisper_cpp":
        default_model = (
            Path(__file__).parent / "models" / "ggml-small.bin"
        )
        model_path = Path(
            os.environ.get("WHISPER_MODEL_PATH") or str(default_model)
        ).expanduser()
        return WhisperCppTranscriber(model_path=model_path)

    if backend == "openai":
        # Placeholder — implement OpenAIWhisperTranscriber when needed.
        # Requires OPENAI_API_KEY env var and `openai` python package.
        raise NotImplementedError(
            "STT_BACKEND=openai is stubbed but not implemented yet. "
            "Use whisper_cpp for now."
        )

    raise ValueError(f"unknown STT_BACKEND: {backend!r}")
