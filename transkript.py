# <!-- ROLLE: transkript-kette -->
"""Transkript-Kette für öffentliche Videos — direkt, dann Fremddienst (Block 6, Teil 2).

`[NEU 24.09.2026]` Engywucks Block 6, Fassung 5, Abschnitt 6.0c, nach Claudias
Befund „Sperre ist die Regel" (24.09., 01:24): 30 von 30 Videos vom VPS direkt
abgewiesen, das Kontrollvideo 4 von 4 durch.

**Die Reihenfolge bleibt, die Erwartung dreht sich:**
  1. Direktabruf — kostet nichts, kein Dritter. **Sein Scheitern ist der
     Normalfall und wird nicht gemeldet, nur gezählt**, damit auffällt, wenn
     YouTube sich später wieder öffnet.
  2. Dienst A `freetranscriptapi.com` — der Regelweg. Adams Freigabe vom 23.09.
     („in dieser Phase"). Gelesen am 24.09.: Betreiber in Berlin, Hosting in
     der EU, **Weiterleitung über Cloudflare (USA)**; ohne Konto **20 Abrufe je
     Stunde** (die 50 waren befristet bis 19.09.). 429 ist ein eigener Fall mit
     Wartezeit-Hinweis an Adam, 401/402 heißt Konto oder Kosten — nie ein leeres
     Ergebnis. **Kein Konto, kein Bezahltarif.**
  3. Dienst B nur mit Freigabe-Eintrag in `quellen.json` (noch nicht: erst
     Lesepflicht und Messung vom VPS).

**Nie für Adams eigenes Material** (Kurse, eigene Videos): Das geht lokal über
den Medienpfad, nie über einen dieser Dienste. Wer diese Kette ruft, ruft sie
für Einträge aus dem Zufluss — öffentliche Videos.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIENST_A = "https://api.freetranscriptapi.com/v1/transcript"
ZEITLIMIT_S = 30


@dataclass
class Ergebnis:
    text: "str | None"        # das Transkript — oder None
    weg: str                  # "direkt" | "dienst_a" | ""
    hinweis: str = ""         # nur, wenn Adam etwas wissen muss


def video_kennung(adresse: str) -> "str | None":
    """Die elfstellige Kennung aus den üblichen Adressformen — sonst None."""
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})", adresse or "")
    if m:
        return m.group(1)
    return adresse if re.fullmatch(r"[A-Za-z0-9_-]{11}", adresse or "") else None


def _zaehlerdatei() -> Path:
    return Path(os.environ.get("ZUFLUSS_DIR") or Path.home() / ".claude" / "zufluss") \
        / "transkript-zaehler.json"


def zaehlen(feld: str) -> None:
    """Buchführung: stumm scheiternd — sie trägt keine Entscheidung."""
    try:
        p = _zaehlerdatei()
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        d[feld] = int(d.get(feld, 0)) + 1
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def zaehlerstand() -> dict:
    try:
        return json.loads(_zaehlerdatei().read_text(encoding="utf-8"))
    except Exception:
        return {}


def dienste() -> dict:
    """Welche Fremddienste freigegeben sind — aus `quellen.json` (Adams Hand)."""
    try:
        q = Path(os.environ.get("ZUFLUSS_QUELLEN") or ROOT / "quellen.json")
        return json.loads(q.read_text(encoding="utf-8")).get("dienste", {})
    except Exception:
        return {}


def direkt(kennung: str) -> "str | None":
    """youtube-transcript-api — weich geladen. Fehlt das Paket, ist der
    Direktweg nicht da; das ist kein Fehler des Aufrufs."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        zaehlen("direkt_nicht_installiert")
        return None
    try:
        teile = YouTubeTranscriptApi().fetch(kennung, languages=["de", "en"])
        text = " ".join(getattr(t, "text", "") for t in teile).strip()
        return text or None
    except Exception:
        return None


def dienst_a(kennung: str) -> "tuple[int, str | None]":
    """(Statuscode, Transkript). 0 heißt: keine Antwort."""
    url = DIENST_A + "?" + urllib.parse.urlencode({"video_url": kennung, "lang": "de"})
    req = urllib.request.Request(url, headers={"User-Agent": "claude-telegram-bot/transkript"})
    try:
        with urllib.request.urlopen(req, timeout=ZEITLIMIT_S) as r:
            d = json.loads(r.read(5_000_000).decode("utf-8", errors="replace"))
            text = " ".join(str(t.get("text", "")) for t in d.get("transcript") or []).strip()
            return r.status, (text or None)
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return 0, None


def holen(adresse: str) -> Ergebnis:
    kennung = video_kennung(adresse)
    if not kennung:
        return Ergebnis(None, "", "Das ist kein YouTube-Video — hier gibt es kein Transkript.")
    text = direkt(kennung)
    if text:
        zaehlen("direkt_ok")
        return Ergebnis(text, "direkt")
    # Der Normalfall seit dem 24.09. — gezählt, nicht gemeldet.
    zaehlen("direkt_abgewiesen")
    freigabe = dienste()
    if not (freigabe.get("freetranscriptapi") or {}).get("freigegeben"):
        return Ergebnis(None, "", "Der Direktabruf wurde abgewiesen, und kein Fremddienst ist freigegeben.")
    status, text = dienst_a(kennung)
    if status == 200 and text:
        zaehlen("dienst_a_ok")
        return Ergebnis(text, "dienst_a")
    zaehlen(f"dienst_a_{status or 'keine_antwort'}")
    if status == 429:
        hinweis = ("Der Transkript-Dienst hat seine Stundengrenze erreicht (ohne Konto 20 Abrufe "
                   "je Stunde). In etwa einer Stunde geht es wieder.")
    elif status in (401, 402):
        hinweis = ("Der Transkript-Dienst verlangt ein Konto oder Geld — ich lege keins an. "
                   "Das ist kein leeres Ergebnis, sondern eine Absage.")
    elif status == 404:
        hinweis = "Für dieses Video gibt es keine Untertitel."
    else:
        hinweis = f"Der Transkript-Dienst hat nicht geantwortet ({status or 'keine Antwort'})."
    # Dienst B nur mit eigenem Freigabe-Eintrag — und er ist noch nicht gebaut,
    # weil Lesepflicht und Messung vom VPS fehlen (Fassung 5, 6.0c Punkt 3).
    return Ergebnis(None, "", hinweis)
