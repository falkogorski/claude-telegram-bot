#!/usr/bin/env python3
"""9.1 Azure-Stimme — Prüfer (26.09.2026).

Claudias Auftrag *stimmwechsel-azure* mit Engywucks Berichtigungen (Zettel
26.09., Fassung 3, Teil 2). Ausführend: echte SSML, echter Zähler mit Riegel,
echter Wiederholungsweg, echte Sendestelle des Bots. Attrappen nur an den
Rändern: der HTTP-Aufruf an Azure, edge-tts, Telegram.

**Nicht gemessen, weil ohne Schlüssel nicht messbar:** wie Azure die SSML
tatsächlich spricht („20:05" ohne das Wort „Uhr" dahinter ist eine Annahme)
und ob Azure die Auszeichnung mitzählt. Beides beim ersten Hören mit Adams
Schlüssel prüfen, den Zähler gegen das Portal halten.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import types
import xml.etree.ElementTree as ET
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
_TMP = Path(tempfile.mkdtemp(prefix="azure-"))
os.environ.update({
    "TELEGRAM_BOT_TOKEN": "1:test", "ALLOWED_USER_IDS": "1",
    "USER_PREFS_FILE": str(_TMP / "prefs.json"),
    "QUESTIONS_FILE": str(_TMP / "q.json"), "PENDING_DIR": str(_TMP / "pending"),
    "CONVERSATION_LOG_DIR": str(_TMP / "logs"),
    "TTS_AZURE_ZAEHLER": str(_TMP / "zaehler.json"),
    "POSTFACH_DIR": str(_TMP / "postfach"),
    "TTS_BACKEND": "edge",
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
import bot  # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    print(("  ✅ " if bedingung else "  ❌ ") + name + ("" if bedingung else f" — {gemessen}"))
    if not bedingung:
        fehler.append(name)


# ---- Rand: der HTTP-Aufruf ---------------------------------------------------
_ANTWORTEN: list[int] = []
_GESENDET: list[str] = []


async def _abruf(ssml):
    _GESENDET.append(ssml)
    code = _ANTWORTEN.pop(0) if _ANTWORTEN else 200
    return code, (b"ID3azure" if code == 200 else b""), 0.0


az._abruf = _abruf
az.WARTEN_429 = (0.0, 0.0, 0.0)


def _azure(an: bool) -> None:
    os.environ["TTS_BACKEND"] = "azure" if an else "edge"
    if an:
        os.environ["AZURE_SPEECH_KEY"] = "test-schluessel"
    else:
        os.environ.pop("AZURE_SPEECH_KEY", None)


def _zaehler(zeichen: int = 0, **mehr) -> None:
    Path(os.environ["TTS_AZURE_ZAEHLER"]).write_text(json.dumps(
        {"monat": time.strftime("%Y-%m"), "zeichen": zeichen, "gewarnt": [],
         "gesperrt": False, **mehr}), encoding="utf-8")


def _postfach() -> list[dict]:
    d = Path(os.environ["POSTFACH_DIR"])
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.rglob("*.json"))] \
        if d.exists() else []


print("== A. SSML: Adams sechs Prüffälle, gegen ein festes Bild ==")
ERWARTET = {
    "800.000": '<say-as interpret-as="cardinal">800000</say-as>',
    "9290131": '<say-as interpret-as="number_digit">9290131</say-as>',
    "2.000": '<say-as interpret-as="cardinal">2000</say-as>',
    "20:05 Uhr": '<say-as interpret-as="time" format="hms24">20:05</say-as>',
    "Python 3.12": "Python 3 Punkt 12",
    "2019": '<say-as interpret-as="date" format="y">2019</say-as>',
}
for roh, soll in ERWARTET.items():
    ist = az.ssml_text(roh)
    zeile(f"{roh!r}", ist == soll, gemessen=ist)
zeile("ein Datum wird Wort, sein Jahr nicht noch einmal ausgezeichnet",
      az.ssml_text("am 22.06.2026") == "am 22. Juni 2026", gemessen=az.ssml_text("am 22.06.2026"))
_doc = az.ssml_bauen("A & B <c> 800.000 um 20:05 Uhr", "de-DE-KatjaNeural")
try:
    ET.fromstring(_doc)
    _wohl = True
except ET.ParseError as e:
    _wohl = str(e)
zeile("die SSML ist wohlgeformt, auch mit & und <", _wohl is True, gemessen=str(_wohl))

print("== B. Der Riegel bei fünf Euro ==")
_deckel = az.deckel_zeichen()
zeile("Deckel = Freikontingent + 5 € / Preis", _deckel == 500_000 + int(5 / 16 * 1_000_000),
      gemessen=str(_deckel))
_zaehler(_deckel - 10)
_azure(True)
ok1, m1 = az.pruefen_und_buchen(20)
ok2, m2 = az.pruefen_und_buchen(20)
zeile("über der Grenze: kein Aufruf erlaubt, eine Meldung", not ok1 and len(m1) == 1, gemessen=str(m1))
zeile("die Meldung kommt genau einmal", not ok2 and m2 == [], gemessen=str(m2))
zeile("danach ist Azure nicht mehr bereit", not az.bereit())

print("== C. Vorwarnungen bei 50 und 80 Prozent ==")
_zaehler(0)
_halb = az.FREI_ZEICHEN + int(0.5 * 5 / 16 * 1_000_000)
_, m = az.pruefen_und_buchen(_halb)
zeile("bei der Hälfte: eine Vorwarnung", len(m) == 1 and "50 %" in m[0], gemessen=str(m))
_, m = az.pruefen_und_buchen(10)
zeile("danach nicht noch einmal", m == [], gemessen=str(m))
_, m = az.pruefen_und_buchen(int(0.3 * 5 / 16 * 1_000_000) + 10)
zeile("bei achtzig Prozent: die zweite", len(m) == 1 and "80 %" in m[0], gemessen=str(m))

print("== D. Der Monat wechselt ==")
_zaehler(_deckel, gesperrt=True, monat="2000-01")
zeile("ein neuer Monat beginnt bei null und entsperrt",
      az.stand()["zeichen"] == 0 and az.bereit())

print("== E. Die Ratengrenze ==")
_ANTWORTEN[:] = [429, 429, 200]
_GESENDET.clear()
try:
    _ton = asyncio.run(az.sprechen("<speak/>"))
except Exception as e:
    _ton = e
zeile("429, 429, 200: nach Wiederholung kommt der Ton", _ton == b"ID3azure" and len(_GESENDET) == 3,
      gemessen=f"{_ton!r} nach {len(_GESENDET)} Aufrufen")
_ANTWORTEN[:] = [429, 429, 429, 429]
try:
    asyncio.run(az.sprechen("<speak/>"))
    _wirft = False
except az.AzureFehler:
    _wirft = True
zeile("viermal 429: der Aufruf gibt auf (der Bot spricht dann mit edge-tts)", _wirft)


# ---- Die Sendestelle des Bots -------------------------------------------------
class _Nachricht:
    message_id = 7


class _Telegram:
    def __init__(self):
        self.stimmen = []

    async def send_voice(self, **kw):
        self.stimmen.append(kw["voice"].read())
        return _Nachricht()


def _senden(text: str) -> "tuple[_Telegram, object]":
    tg = _Telegram()
    _EDGE.clear()
    _GESENDET.clear()
    r = asyncio.run(bot._send_tts_chunk(tg, 1, text))
    return tg, r


print("== F. Die Sendestelle ==")
_zaehler(0)
_azure(True)
_ANTWORTEN[:] = [200]
tg, r = _senden("Es kostet 800.000 Euro.")
zeile("Azure an: Azure spricht, edge-tts nicht", tg.stimmen == [b"ID3azure"] and not _EDGE,
      gemessen=f"stimmen={tg.stimmen} edge={_EDGE}")
zeile("und der Zähler hat gebucht", az.stand()["zeichen"] == len("Es kostet 800.000 Euro."),
      gemessen=str(az.stand()))
_ANTWORTEN[:] = [500]
tg, r = _senden("Es kostet 800.000 Euro.")
zeile("Azure fällt aus: edge-tts spricht, keine Stille", tg.stimmen == [b"ID3edge"] and _EDGE,
      gemessen=f"stimmen={tg.stimmen}")
zeile("und bekommt die Zahlen-Umschreiber nachgeholt", _EDGE and "800.000" not in _EDGE[0],
      gemessen=str(_EDGE))
_ANTWORTEN[:] = [200]
_zaehler(0)
tg, r = _senden("Dein Passwort steht im Befund vom Arzt.")
zeile("rot eingestuft: kein Text geht an Azure, edge-tts spricht wie bisher",
      not _GESENDET and tg.stimmen == [b"ID3edge"] and az.stand()["zeichen"] == 0,
      gemessen=f"an Azure: {len(_GESENDET)}, gebucht {az.stand()}")
_alt_klass = bot.ampel.classify
bot.ampel.classify = lambda t: (_ for _ in ()).throw(RuntimeError("Regeldatei kaputt"))
try:
    tg, r = _senden("Es kostet 800.000 Euro.")
finally:
    bot.ampel.classify = _alt_klass
zeile("scheitert die Einstufung, gilt es als rot (nicht zu Azure)",
      not _GESENDET and tg.stimmen == [b"ID3edge"], gemessen=f"an Azure: {len(_GESENDET)}")
_azure(False)
tg, r = _senden("Es kostet 800.000 Euro.")
zeile("Schalter aus: kein Text geht an Azure", not _GESENDET and tg.stimmen == [b"ID3edge"],
      gemessen=f"an Azure: {len(_GESENDET)}")

print("== G. Die Umschreiber je Backend ==")
_azure(True)
_zaehler(0)
_mit = bot._strip_markdown_for_tts("Es kostet 800.000 Euro.")
_azure(False)
_ohne = bot._strip_markdown_for_tts("Es kostet 800.000 Euro.")
zeile("Azure: die Zahl bleibt für die SSML stehen", "800.000" in _mit, gemessen=_mit)
zeile("edge-tts: die Umschreiber laufen weiter", "800.000" not in _ohne, gemessen=_ohne)

print("== H. Der Riegel an der Sendestelle ==")
_azure(True)
_zaehler(_deckel - 5)
_vorher = len(_postfach())
tg, r = _senden("Ein Satz mit mehr als fünf Zeichen.")
_neu = _postfach()[_vorher:]
zeile("an der Grenze: kein Aufruf, edge-tts spricht", not _GESENDET and tg.stimmen == [b"ID3edge"],
      gemessen=f"an Azure: {len(_GESENDET)}")
zeile("Adam bekommt die Meldung über die Botenpost",
      len(_neu) == 1 and "abgeschaltet" in _neu[0].get("text", ""), gemessen=str(_neu)[:160])
_senden("Noch ein Satz.")
zeile("und nicht bei jedem weiteren Satz", len(_postfach()) - _vorher == 1)

print("== I. Tagescheck 9p (echter Abschnitt) ==")
_dc = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
_m = re.search(r"# >>> AZURE\n(.*?)# <<< AZURE", _dc, re.S)
_rumpf = ('set -uo pipefail\nadd() { echo "ADD:$1"; }\nintern() { echo "INTERN:$1"; }\n'
          f'BOTENV=(env)\nBOTDIR="{WURZEL}"\nVENVPY="{sys.executable}"\n' + (_m.group(1) if _m else ""))
_zaehler(1234)
_aus = subprocess.run(["bash", "-c", _rumpf], capture_output=True, text=True,
                      env={**os.environ}).stdout
zeile("mit Schalter und Schlüssel: der Zählerstand steht im Protokoll",
      "ADD:🔊 Sprachausgabe:" in _aus and "1.234 Zeichen" in _aus, gemessen=_aus)
_env = {**os.environ, "TTS_BACKEND": "azure"}
_env.pop("AZURE_SPEECH_KEY", None)
_aus = subprocess.run(["bash", "-c", _rumpf], capture_output=True, text=True, env=_env).stdout
zeile("Schalter an, Schlüssel fehlt: an die Kontrolle", "INTERN:Sprachausgabe:" in _aus,
      gemessen=_aus)

import shutil  # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Azure-Stimme bestanden.")
