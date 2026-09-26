#!/usr/bin/env python3
# <!-- ROLLE: test-sprachausgabe-lokal -->
"""9.2 lokale Stimme für Rotes — Prüfer (26.09.2026).

Ausführend: echte Sendestelle des Bots (`_send_tts_chunk`, `send_answer_to_user`),
echte Ampel, echte Zahlen-Aufbereitung, echter Tagescheck-Abschnitt, echtes
Ladeskript. Attrappen nur an den Rändern: Piper (für die Weichen), edge-tts,
der HTTP-Aufruf an Azure, Telegram, curl.

Dazu ein **echter** Lauf der Stimme, wenn sie auf diesem Rechner liegt — sonst
wird die Zeile als übersprungen genannt und nicht mitgezählt.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
_TMP = Path(tempfile.mkdtemp(prefix="lokal-"))
_ECHTES_MODELL = os.environ.pop("TTS_LOKAL_MODELL", None)   # fuer den echten Lauf unten
os.environ.update({
    "TELEGRAM_BOT_TOKEN": "1:test", "ALLOWED_USER_IDS": "1",
    "USER_PREFS_FILE": str(_TMP / "prefs.json"),
    "QUESTIONS_FILE": str(_TMP / "q.json"), "PENDING_DIR": str(_TMP / "pending"),
    "CONVERSATION_LOG_DIR": str(_TMP / "logs"),
    "TTS_AZURE_ZAEHLER": str(_TMP / "zaehler.json"),
    "POSTFACH_DIR": str(_TMP / "postfach"),
    "TTS_BACKEND": "edge", "TTS_ROT_LOKAL": "an",
    "TTS_LOKAL_MODELL": str(_TMP / "keine-stimme.onnx"),
})
os.environ.pop("AZURE_SPEECH_KEY", None)

_EDGE: list[str] = []


class _Stimme:
    def __init__(self, text, stimme):
        _EDGE.append(text)

    async def save(self, pfad):
        Path(pfad).write_bytes(b"ID3edge")


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=_Stimme)
sys.path.insert(0, str(WURZEL))
import sprachausgabe_azure as az  # noqa: E402
import sprachausgabe_lokal as lok  # noqa: E402
import bot  # noqa: E402

fehler: list[str] = []
zeilen = 0
uebersprungen: list[str] = []


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    print(("  ✅ " if bedingung else "  ❌ ") + name + ("" if bedingung else f" — {gemessen}"))
    if not bedingung:
        fehler.append(name)


# ── Raender ─────────────────────────────────────────────────────────────────
_AZURE: list[str] = []


async def _abruf(ssml):
    _AZURE.append(ssml)
    return 200, b"ID3azure", 0.0


az._abruf = _abruf
_LOKAL: list[str] = []
_LOKAL_FEHLER = [False]
_echt = {"bereit": lok.bereit, "sprechen": lok.sprechen}


def _lokal_attrappe(an: bool) -> None:
    if an:
        lok.bereit = lambda: True

        def sprechen(text):
            _LOKAL.append(text)
            if _LOKAL_FEHLER[0]:
                raise RuntimeError("Piper abgestuerzt")
            return b"OggS-lokal"
        lok.sprechen = sprechen
    else:
        lok.bereit, lok.sprechen = _echt["bereit"], _echt["sprechen"]


class _Nachricht:
    def __init__(self, mid):
        self.message_id = mid


class _Telegram:
    def __init__(self):
        self.stimmen: list[tuple[bytes, str]] = []
        self.texte: list[str] = []

    async def send_voice(self, **kw):
        self.stimmen.append((kw["voice"].read(), Path(kw["voice"].name).suffix))
        return _Nachricht(len(self.stimmen))

    async def send_message(self, **kw):
        self.texte.append(kw.get("text", ""))
        return _Nachricht(100 + len(self.texte))


def _neu():
    _EDGE.clear(); _AZURE.clear(); _LOKAL.clear(); _LOKAL_FEHLER[0] = False
    return _Telegram()


ROT = "Dein Passwort steht im Befund vom 22.06.2026."
GRUEN = "Das Wetter ist heute freundlich."

# ── A. Bereitschaft ─────────────────────────────────────────────────────────
print("== A. Wann die lokale Stimme bereit ist ==")
os.environ["TTS_ROT_LOKAL"] = "aus"
zeile("ausgeschaltet: nicht bereit, Grund genannt", "ausgeschaltet" in lok.grund())
os.environ["TTS_ROT_LOKAL"] = "an"
_g = lok.grund()
zeile("ohne Stimme (oder ohne Piper): nicht bereit, Grund genannt",
      not lok.bereit() and ("Stimme fehlt" in _g or "piper-tts" in _g), gemessen=_g)
_alt_ff = lok.ffmpeg
(_TMP / "stimme.onnx").write_bytes(b"x")
(_TMP / "stimme.onnx.json").write_text("{}")
os.environ["TTS_LOKAL_MODELL"] = str(_TMP / "stimme.onnx")
lok.ffmpeg = lambda: None
_g = lok.grund()
lok.ffmpeg = _alt_ff
os.environ["TTS_LOKAL_MODELL"] = str(_TMP / "keine-stimme.onnx")
zeile("ohne ffmpeg: nicht bereit (Telegram nimmt kein WAV)",
      "ffmpeg" in _g or "piper-tts" in _g, gemessen=_g)

# ── B. Die Sendestelle ──────────────────────────────────────────────────────
print("== B. Die Sendestelle ==")
os.environ.update({"TTS_BACKEND": "azure", "AZURE_SPEECH_KEY": "test"})
_lokal_attrappe(True)
tg = _neu()
r = asyncio.run(bot._send_tts_chunk(tg, 1, ROT))
zeile("rot + bereit: die lokale Stimme spricht, weder Azure noch edge-tts",
      r is not None and tg.stimmen == [(b"OggS-lokal", ".ogg")] and not _AZURE and not _EDGE,
      gemessen=f"stimmen={tg.stimmen} azure={len(_AZURE)} edge={len(_EDGE)}")
zeile("und bekommt die Zahlen aufbereitet (Ordinaltag statt Satzende)",
      _LOKAL and "zweiundzwanzigsten Juni" in _LOKAL[0], gemessen=str(_LOKAL))
tg = _neu()
asyncio.run(bot._send_tts_chunk(tg, 1, GRUEN))
zeile("gruen: die lokale Stimme bleibt still, Azure spricht",
      not _LOKAL and tg.stimmen == [(b"ID3azure", ".mp3")], gemessen=f"{tg.stimmen} lokal={_LOKAL}")
tg = _neu()
_LOKAL_FEHLER[0] = True
r = asyncio.run(bot._send_tts_chunk(tg, 1, ROT))
zeile("rot + lokale Stimme scheitert: KEIN Cloud-Rueckfall, kein Ton",
      r is None and not tg.stimmen and not _AZURE and not _EDGE,
      gemessen=f"r={r} azure={len(_AZURE)} edge={len(_EDGE)}")
_lokal_attrappe(False)
tg = _neu()
asyncio.run(bot._send_tts_chunk(tg, 1, ROT))
zeile("rot, aber keine lokale Stimme eingerichtet: wie vor 9.2 edge-tts, nie Azure",
      tg.stimmen == [(b"ID3edge", ".mp3")] and not _AZURE, gemessen=f"{tg.stimmen} azure={len(_AZURE)}")

# ── C. Der Antwortweg: eine Antwort, eine Stimme ────────────────────────────
print("== C. Eine Antwort, eine Stimme ==")


def _sitzung(tg):
    bot._USER_PREFS.setdefault("1", {})["link_vorschau"] = False
    s = bot.UserSession(client=None, user_id=1, chat_id=1)
    s.bot = tg
    s.tts_enabled = True
    return s


_lokal_attrappe(True)
ABSATZ = ("Hier folgt ein ruhiger Absatz ohne jedes heikle Wort, nur zum Lesen. " * 8).strip()
LANG = f"Dein Passwort gehoert nicht in den Chat.\n\n{ABSATZ}\n\n{ABSATZ}"
tg = _neu()
ok = asyncio.run(bot.send_answer_to_user(_sitzung(tg), 1, LANG))
zeile("lange rote Antwort: JEDES Teilstueck spricht lokal, auch das ohne rotes Wort",
      ok and len(tg.stimmen) >= 2 and all(s == (b"OggS-lokal", ".ogg") for s in tg.stimmen)
      and not _AZURE and not _EDGE, gemessen=f"{[s[1] for s in tg.stimmen]} azure={len(_AZURE)}")
tg = _neu()
_LOKAL_FEHLER[0] = True
ok = asyncio.run(bot.send_answer_to_user(_sitzung(tg), 1, "Dein Passwort: kurz gesagt, nein."))
zeile("rote Antwort, lokale Stimme faellt aus: der Text kommt trotzdem an (nie Stille)",
      ok and tg.texte and "Passwort" in tg.texte[-1] and not tg.stimmen and not _AZURE,
      gemessen=f"ok={ok} texte={tg.texte} stimmen={len(tg.stimmen)}")
_lokal_attrappe(False)
tg = _neu()
ok = asyncio.run(bot.send_answer_to_user(_sitzung(tg), 1, LANG))
zeile("rote Antwort ohne lokale Stimme: auch das harmlose Teilstueck geht nicht an Azure",
      ok and tg.stimmen and not _AZURE, gemessen=f"azure={len(_AZURE)} stimmen={len(tg.stimmen)}")
os.environ["TTS_BACKEND"] = "edge"
os.environ.pop("AZURE_SPEECH_KEY", None)

# ── D. Die Zahlen fuer Piper ────────────────────────────────────────────────
print("== D. Zahlen, wie Piper sie braucht ==")
for roh, soll in (("am 22.06.2026", "am zweiundzwanzigsten Juni 2026"),
                  ("am 1. März und am 3. Mai", "am ersten März und am dritten Mai"),
                  ("Endstand 3-1", "Endstand 3 zu 1"),
                  ("um 20:05 Uhr", "um 20 Uhr 5"),
                  ("Rechnung 017-26", "Rechnung 017-26"),
                  ("1.250 Euro und Python 3.12", "1.250 Euro und Python 3.12"),
                  ("im Jahr 1998", "im Jahr neunzehnhundertachtundneunzig")):
    ist = bot._fuer_lokale_stimme(roh)
    zeile(f"{roh!r} -> {soll!r}", ist == soll, gemessen=repr(ist))

# ── E. Tagescheck 9s ────────────────────────────────────────────────────────
print("== E. Tagescheck 9s ==")
import re  # noqa: E402
_dc = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
_m = re.search(r"# >>> LOKALSTIMME\n(.*?)# <<< LOKALSTIMME", _dc, re.S)
_abschnitt = _m.group(1) if _m else ""


def _tagescheck(ausgabe: str) -> str:
    attrappe = _TMP / "py"
    attrappe.write_text(f"#!/bin/bash\necho '{ausgabe}'\n")
    attrappe.chmod(0o755)
    vorspann = ('set -uo pipefail\nadd() { echo "ADD:$1"; }\nintern() { echo "INTERN:$1"; }\n'
                'sudo() { shift 2; "$@"; }\n'
                f'BOTDIR="{WURZEL}"\nVENVPY="{attrappe}"\nBOTHOME="$HOME"\n')
    return subprocess.run(["bash", "-c", vorspann + _abschnitt], capture_output=True,
                          text=True).stdout


zeile("Tagescheck 9s ist markiert und ruft die Probe", "--probe" in _abschnitt)
_a = _tagescheck("OK Lokale Stimme spricht: 5.0 s Ton in 0.5 s (10-fach Echtzeit)")
zeile("9s: spricht sie, steht die Geschwindigkeit im Protokoll",
      "ADD:🗣️ Lokale Stimme spricht" in _a, gemessen=_a)
_a = _tagescheck("AUS Stimme fehlt")
zeile("9s: nicht eingerichtet ist kein Alarm", "ADD:" in _a and "INTERN" not in _a, gemessen=_a)
_a = _tagescheck("FEHLER RuntimeError: kaputt")
zeile("9s: spricht sie nicht, erfaehrt es die Kontrolle",
      "INTERN:Lokale Stimme spricht nicht" in _a, gemessen=_a)

# ── F. Das Ladeskript ───────────────────────────────────────────────────────
print("== F. Ladeskript mit Prüfsumme ==")
_bin = _TMP / "bin"
_bin.mkdir()
(_bin / "curl").write_text('#!/bin/bash\nwhile [ $# -gt 0 ]; do [ "$1" = "-o" ] && ziel="$2"; shift; done\n'
                           'echo "fremder Inhalt" > "$ziel"\n')
(_bin / "curl").chmod(0o755)
_ziel = _TMP / "laden" / "de_DE-thorsten-medium.onnx"
r = subprocess.run(["bash", str(WURZEL / "scripts" / "lokale_stimme_laden.sh")], capture_output=True,
                   text=True, env={**os.environ, "PATH": f"{_bin}:{os.environ['PATH']}",
                                   "TTS_LOKAL_MODELL": str(_ziel)})
zeile("falsche Pruefsumme: Abbruch, nichts am Ort, kein Rest",
      r.returncode != 0 and "Pruefsumme stimmt nicht" in r.stdout and not _ziel.exists()
      and not list(_ziel.parent.glob(".teil-*")), gemessen=f"rc={r.returncode} {r.stdout[-120:]!r}")

# ── G. Die echte Stimme ─────────────────────────────────────────────────────
print("== G. Die echte Stimme (wenn sie auf diesem Rechner liegt) ==")
if _ECHTES_MODELL:
    os.environ["TTS_LOKAL_MODELL"] = _ECHTES_MODELL
else:
    os.environ.pop("TTS_LOKAL_MODELL", None)
if lok.bereit():
    p = lok.probe()
    zeile("die Probe spricht und nennt ihre Geschwindigkeit", p.startswith("OK "), gemessen=p)
    ton = lok.sprechen(bot._fuer_lokale_stimme("Am 22.06.2026 um 20:05 Uhr."))
    zeile("der Ton ist OGG/Opus, wie Telegram ihn fuer Sprachnachrichten nimmt",
          ton.startswith(b"OggS") and len(ton) > 2000, gemessen=f"{ton[:8]!r} {len(ton)} Bytes")
else:
    uebersprungen.append(f"echte Stimme: {lok.grund()}")

import shutil  # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
for u in uebersprungen:
    print(f"  ⏭️ übersprungen: {u}")
print(f"== Ergebnis: {zeilen - len(fehler)}/{zeilen}"
      + (f", {len(uebersprungen)} übersprungen" if uebersprungen else "") + " ==")
sys.exit(1 if fehler else 0)
