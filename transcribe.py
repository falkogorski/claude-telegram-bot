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
        wav = await self._convert_to_wav(audio_path)
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


class NullTranscriber(Transcriber):
    """Used when STT is disabled; surfaces a user-facing hint."""

    async def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        raise RuntimeError("STT backend is disabled (STT_BACKEND=off). Send text instead.")


def build_transcriber() -> Transcriber:
    """Factory — reads .env and returns the configured backend.

    Add a new STT_BACKEND value here (e.g. "openai") to wire in another impl;
    the rest of the bot doesn't change.
    """
    backend = (os.environ.get("STT_BACKEND") or "whisper_cpp").lower().strip()

    if backend == "off":
        return NullTranscriber()

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
