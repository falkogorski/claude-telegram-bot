# <!-- ROLLE: sprachausgabe-azure -->
"""Sprachausgabe über Azure Neural mit SSML — Drehbuch 9.1.

`[NEU 26.09.2026]` Claudias Auftrag *stimmwechsel-azure* (Fassung 12:40),
geprüft von Engywuck (Zettel 26.09., Fassung 3, Teil 2). **Kostenfreigabe:
Adam am 26.09.2026, 12:33 — Stufe S0, Kostenriegel bei fünf Euro.**

Was dieses Modul trägt, und nur das:

- **Die SSML** für einen bereits gesäuberten Vorlesetext: Zahlarten über
  `<say-as>` statt über die sieben Umschreiber, die edge-tts braucht. Die
  Werte sind in Microsofts Dokumentation nachgesehen (26.09.): `cardinal`,
  `number_digit` (nicht „digits"), `time` mit `hms24`, `date` mit `y`.
- **Der Zähler und der Riegel.** Gezählt wird je Kalendermonat der
  **Vorlesetext** (Zeichen vor der SSML-Verpackung), in einer Datei neben den
  Vorlieben — sie überlebt jeden Neustart. `[BERICHTIGT 26.09., Befund 5]`
  Hier stand „was an Azure geht": Gesendet wird die SSML, bei zahlenreichem
  Text gut das Vierfache (gemessen 113 → 526 Zeichen). Ob Microsoft die
  Auszeichnung mitberechnet, ist ohne Konto nicht messbar — im ersten Monat
  wird unser Zähler gegen den Portal-Zähler gehalten. Bei
  der Hälfte und bei achtzig Prozent der Kostengrenze eine Vorwarnung, beim
  Erreichen **kein Aufruf mehr**, Rückfall auf edge-tts und eine Meldung an
  Adam, genau einmal. **Die Grenze ist Code, nicht nur eine Kontoeinstellung:**
  Die Kostenwarnung im Azure-Konto meldet, sie stoppt nicht.
- **Die Ratengrenze:** HTTP 429 wird mit wachsender Wartezeit wiederholt; nach
  der letzten Wiederholung wirft der Aufruf, und der Bot spricht mit edge-tts.

**Nicht hier:** die Entscheidung, ob Azure spricht (`bereit`), trifft der Bot
an seiner einzigen Sendestelle `_send_tts_chunk`; der Rückfall auf edge-tts
sitzt dort. Die zweite Stimme für rote Inhalte ist Drehbuch 9.2, **lokal**,
nicht Azure (Engywucks Berichtigung c).

**Der Schlüssel** liegt allein in der Geheimnis-Ablage des Dienstes und kommt
als Umgebungsvariable herein; dieses Modul liest keine Datei dafür.

Nur Standardbibliothek plus `httpx` (kommt mit python-telegram-bot).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path

# ---- Einstellgrößen — Zahlen an einer Stelle (Register: ABHAENGIGKEITEN.md) --
REGION = (os.environ.get("AZURE_SPEECH_REGION") or "germanywestcentral").strip()
DECKEL_EUR = float(os.environ.get("TTS_AZURE_DECKEL_EUR") or 5)
# `[GEAENDERT 26.09.2026, Engywucks Gegenpruefung, Befund 6]` Vorgabe NULL.
# Hier standen 500.000: Dass das Freikontingent auch auf der Stufe S0 gilt,
# stand nur in einem Papier, nicht amtlich belegt. Gilt es nicht, griffe der
# „5-Euro-Riegel" erst bei rund 13 Euro. Kostenregel: unklar gilt als ja.
# Zeigt der erste Portal-Zaehlerstand das Freikontingent auf S0, setzt Adam
# `TTS_AZURE_FREI_ZEICHEN` in der Dienst-Umgebung.
FREI_ZEICHEN = int(os.environ.get("TTS_AZURE_FREI_ZEICHEN") or 0)
# Preis je Million Zeichen über dem Freikontingent. Microsoft rechnet mit
# 15 USD, Drittübersichten nennen 16; der amtliche Eurobetrag wird beim
# Anlegen des Kontos abgelesen. **16 als Euro gelesen ist die vorsichtige
# Wahl** — der Riegel greift damit eher zu früh als zu spät.
EUR_JE_MIO = float(os.environ.get("TTS_AZURE_EUR_JE_MIO") or 16)
WARNSTUFEN = (0.5, 0.8)
WARTEN_429 = (1.0, 2.0, 4.0)
AUSGABE = "audio-24khz-48kbitrate-mono-mp3"
SSML_GRENZE = 64 * 1024

MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember")


def backend() -> str:
    """Frisch gelesen, nicht beim Import: Der Schalter soll ohne Neustart eines
    Pruefers wirken, und im Betrieb setzt ihn die Dienst-Umgebung."""
    return (os.environ.get("TTS_BACKEND") or "edge").strip().lower()


def _zahl(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _eur(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def schluessel() -> str:
    return (os.environ.get("AZURE_SPEECH_KEY") or "").strip()


def zaehler_datei() -> Path:
    roh = os.environ.get("TTS_AZURE_ZAEHLER")
    if roh:
        return Path(roh)
    prefs = os.environ.get("USER_PREFS_FILE")
    basis = Path(prefs).parent if prefs else Path.home() / ".config" / "claude-telegram-bot"
    return basis / "tts-azure-zaehler.json"


def deckel_zeichen() -> int:
    return FREI_ZEICHEN + int(DECKEL_EUR / EUR_JE_MIO * 1_000_000)


def kosten_eur(zeichen: int) -> float:
    return max(0, zeichen - FREI_ZEICHEN) / 1_000_000 * EUR_JE_MIO


# ---- Zähler -----------------------------------------------------------------
def _monat(jetzt: float | None = None) -> str:
    return time.strftime("%Y-%m", time.localtime(jetzt if jetzt is not None else time.time()))


def stand(jetzt: float | None = None) -> dict:
    """Der Stand dieses Monats. Ein neuer Monat beginnt bei null."""
    leer = {"monat": _monat(jetzt), "zeichen": 0, "gewarnt": [], "gesperrt": False}
    try:
        d = json.loads(zaehler_datei().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return leer
    if not isinstance(d, dict) or d.get("monat") != leer["monat"]:
        return leer
    return {**leer, **d}


def _schreiben(d: dict) -> None:
    p = zaehler_datei()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def bereit(jetzt: float | None = None) -> bool:
    """Spricht Azure? Schalter an, Schlüssel da, Riegel nicht erreicht."""
    return backend() == "azure" and bool(schluessel()) and not stand(jetzt)["gesperrt"]


def pruefen_und_buchen(n: int, jetzt: float | None = None) -> "tuple[bool, list[str]]":
    """VOR dem Aufruf: Darf dieser Text noch an Azure? (erlaubt, Meldungen).

    Gebucht wird hier, vor dem Aufruf: Ein Aufruf, der danach scheitert, ist
    womöglich trotzdem berechnet. Lieber einmal zu viel gezählt als einmal zu
    wenig — die Fehlerrichtung eines Riegels."""
    d = stand(jetzt)
    meldungen: list[str] = []
    if d["gesperrt"]:
        return False, meldungen
    if d["zeichen"] + n > deckel_zeichen():
        d["gesperrt"] = True
        _schreiben(d)
        meldungen.append(
            f"🔊 Die Azure-Stimme ist für {d['monat']} abgeschaltet: Die Grenze von "
            f"{_eur(DECKEL_EUR)} € ist erreicht ({_zahl(d['zeichen'])} Zeichen). Bis zum "
            "Monatswechsel spricht wieder die bisherige Stimme.")
        return False, meldungen
    d["zeichen"] += n
    for stufe in WARNSTUFEN:
        schwelle = stufe * DECKEL_EUR
        if kosten_eur(d["zeichen"]) >= schwelle and stufe not in d["gewarnt"]:
            d["gewarnt"].append(stufe)
            meldungen.append(
                f"🔊 Azure-Stimme: {int(stufe * 100)} % der Monatsgrenze erreicht — "
                f"etwa {_eur(kosten_eur(d['zeichen']))} von {_eur(DECKEL_EUR)} €. "
                "Bei der Grenze spricht wieder die bisherige Stimme.")
    _schreiben(d)
    return True, meldungen


# ---- SSML -------------------------------------------------------------------
def _xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_MUSTER = re.compile(
    r"(?P<zeit>\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b)(?P<uhr>\s*Uhr\b)?"
    r"|(?P<datum>\b(?:0?[1-9]|[12]\d|3[01])\.(?:0?[1-9]|1[0-2])\.(?:\d{4})\b)"
    r"|(?P<tausend>(?<![\d.])\d{1,3}(?:\.\d{3})+(?![\d.]))"
    r"|(?P<fassung>(?<![\d.])\d+\.\d+(?:\.\d+)*(?![\d.]))"
    r"|(?P<kennung>(?<![\d.])\d{5,}(?![\d.]))"
    r"|(?P<jahr>(?<![\d.])(?:1[5-9]\d\d|20\d\d)(?![\d.]))")


def _ersetzen(m: "re.Match") -> str:
    if m.group("zeit"):
        # „Uhr" dahinter entfällt: Die Stimme sagt es bei hms24 selbst.
        # **Ungehört** — beim ersten Mischtext mit Schlüssel prüfen.
        return f'<say-as interpret-as="time" format="hms24">{m.group("zeit")}</say-as>'
    if m.group("datum"):
        t, mo, j = m.group("datum").split(".")
        return f"{int(t)}. {MONATE[int(mo) - 1]} {j}"
    if m.group("tausend"):
        return f'<say-as interpret-as="cardinal">{m.group("tausend").replace(".", "")}</say-as>'
    if m.group("fassung"):
        return " Punkt ".join(m.group("fassung").split("."))
    if m.group("kennung"):
        return f'<say-as interpret-as="number_digit">{m.group("kennung")}</say-as>'
    return f'<say-as interpret-as="date" format="y">{m.group("jahr")}</say-as>'


def ssml_text(text: str) -> str:
    """Der Satzteil der SSML: Zeichen maskiert, Zahlarten ausgezeichnet."""
    return _MUSTER.sub(_ersetzen, _xml(text or ""))


def ssml_bauen(text: str, stimme: str, sprache: str = "de-DE") -> str:
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="{sprache}"><voice name="{_xml(stimme)}">'
            f"{ssml_text(text)}</voice></speak>")


# ---- Der Aufruf ---------------------------------------------------------------
class AzureFehler(RuntimeError):
    pass


async def _abruf(ssml: str) -> "tuple[int, bytes, float | None]":
    """Der Rand: ein HTTP-Aufruf. Prüfer ersetzen genau diese Funktion."""
    import httpx
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"https://{REGION}.tts.speech.microsoft.com/cognitiveservices/v1",
            content=ssml.encode("utf-8"),
            headers={"Ocp-Apim-Subscription-Key": schluessel(),
                     "Content-Type": "application/ssml+xml",
                     "X-Microsoft-OutputFormat": AUSGABE,
                     "User-Agent": "claudia-bot"})
        warte = r.headers.get("Retry-After")
        try:
            warte_s = float(warte) if warte else None
        except ValueError:
            warte_s = None
        return r.status_code, r.content, warte_s


async def sprechen(ssml: str) -> bytes:
    """SSML → Ton. 429 wird mit wachsender Wartezeit wiederholt (Sekunden,
    höchstens acht); alles andere und die letzte 429 werfen."""
    if len(ssml.encode("utf-8")) > SSML_GRENZE:
        raise AzureFehler("SSML über 64 KB")
    for versuch in range(len(WARTEN_429) + 1):
        code, inhalt, warte = await _abruf(ssml)
        if code == 200 and inhalt:
            return inhalt
        if code == 429 and versuch < len(WARTEN_429):
            await asyncio.sleep(min(warte or WARTEN_429[versuch], 8.0))
            continue
        raise AzureFehler(f"HTTP {code}")
    raise AzureFehler("HTTP 429 nach allen Wiederholungen")


def stand_zeile() -> str:
    """Für den Tagescheck: der Zählerstand in einer Zeile."""
    d = stand()
    if backend() != "azure":
        return "AUS Sprachausgabe über edge-tts (TTS_BACKEND nicht azure)"
    if not schluessel():
        return "OHNE Schalter auf azure, aber kein Schlüssel — es spricht edge-tts"
    return (f"AN {d['monat']}: {_zahl(d['zeichen'])} Zeichen, etwa {_eur(kosten_eur(d['zeichen']))} "
            f"von {_eur(DECKEL_EUR)} €" + (" — GESPERRT bis Monatswechsel" if d["gesperrt"] else ""))


if __name__ == "__main__":
    print(stand_zeile())
