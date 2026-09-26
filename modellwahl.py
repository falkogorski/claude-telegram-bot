# <!-- ROLLE: modellwahl -->
"""Modellwahl — welche Kennung hinter Opus, Sonnet, Haiku und Fable steht.

`[NEU 24.09.2026, Block 4]` Claudias Auftrag „Modellwächter" vom 23.09.,
berichtigt von Engywuck, mit Adams Entscheid zur Automatik.

**Warum ein eigenes Modul:** Bot und Wächter müssen dieselbe Frage
beantworten — *welche Kennung gilt?* — und dieselbe Datei schreiben. Stünde
die Antwort zweimal, liefe sie auseinander (G1-Lehre). Hier steht sie einmal.

**Warum eine Datei und nicht der Quelltext:** Die Kennung stand fest in
`bot.py`, und der Bot schreibt sein Repo nie (8.7). Ein Knopf „umstellen"
hätte nichts auslösen können. `models.json` liegt neben den Vorlieben, außerhalb
des Repos, und der Bot darf sie schreiben. `VORGABE` bleibt der Rückfall, wenn
die Datei fehlt oder nichts für eine Stufe sagt.

**Adams Entscheid (23.09.): umstellen von selbst, mit drei Sicherungen.**
  (1) Der Wächter schreibt NUR diese Datei und meldet laut, mit Rückweg-Knopf.
  (2) Die erste echte Nachricht ist die Probe: Scheitert der Aufruf an der
      neuen Kennung, fällt der Bot von selbst zurück und sagt es.
  (3) Der Wächter ruft aus dem Zeitgeber nie ein Modell auf.

Deterministisch, kein Modellaufruf, kein Netz — das Netz hat allein der
Wächter (`scripts/modellwaechter.py`).
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

VORGABE: dict[str, str] = {
    # angehoben 24.09. (Block 4, Adams Entscheid 23.09.): Opus 5.5 seit 22.09.
    # laut Release-Notes-Feed (gemessen). Deploy NUR nach Abo-Probe auf dem VPS.
    "opus":   "claude-opus-5-5",
    "sonnet": "claude-sonnet-5",   # angehoben 22.07. nach OAuth-Probe (war 4-6)
    "haiku":  "claude-haiku-4-5-20251001",
    "fable":  "claude-fable-5",
}
FAMILIEN = tuple(VORGABE)

# Die Bezugsquelle (Engywuck, Block 6 Fassung 2): kostenfrei, ohne Schlüssel,
# führt Modelle und Claude Code. Am 24.09. gemessen: 200, 188 KB.
FEED = "https://platform.claude.com/docs/en/release-notes/feed.xml"

# Eine Kennung, genau so und nicht als Teil einer längeren: `claude-opus-5-5`
# ja, `claude-opus-5-5-fast` nein. Die Nebenstelle hat ein bis zwei Ziffern —
# sonst läse `claude-opus-4-20250514` das Datum als Fassung 4.20250514.
_KENNUNG = re.compile(
    r"(?<![\w-])claude-(opus|sonnet|haiku|fable)-(\d{1,2})(?:-(\d{1,2}))?"
    r"(?:-(\d{8}))?(?![\w-])")


def datei() -> Path:
    roh = os.environ.get("MODELS_FILE")
    if roh:
        return Path(roh)
    prefs = os.environ.get("USER_PREFS_FILE")
    basis = (Path(prefs).parent if prefs
             else Path.home() / ".config" / "claude-telegram-bot")
    return basis / "models.json"


def lesen() -> dict:
    """Der Inhalt — oder leer. Eine kaputte Datei ist kein Absturz, sondern
    der Rückfall auf die Vorgabe."""
    try:
        d = json.loads(datei().read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def schreiben(d: dict) -> None:
    ziel = datei()
    ziel.parent.mkdir(parents=True, exist_ok=True)
    tmp = ziel.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ziel)


def kennung(kurz: str) -> str:
    """Die geltende Kennung einer Stufe — frisch gelesen, bei jedem Aufruf.

    Frisch, weil der Wächter die Datei von außen schreibt: Ein beim Start
    gemerkter Wert wüsste nichts davon.
    """
    k = (lesen().get("kennungen") or {}).get(kurz)
    if isinstance(k, str) and _KENNUNG.fullmatch(k):
        return k
    return VORGABE.get(kurz, kurz)


def fassung(k: str) -> "tuple[int, int] | None":
    m = _KENNUNG.fullmatch(k or "")
    if not m:
        return None
    return int(m.group(2)), int(m.group(3) or 0)


def kennungen_im_text(text: str) -> set[str]:
    return {m.group(0) for m in _KENNUNG.finditer(text or "")}


def neuere(text: str) -> "list[tuple[str, str, str]]":
    """Je Stufe: (stufe, geltend, neuer) — nur wo der Text eine HÖHERE Fassung
    nennt und sie nicht schon einmal zurückgenommen wurde.

    **Fremdinhalt ist Daten:** Aus dem Text wird allein eine Kennung nach
    festem Muster gelesen. Nichts darin wird ausgeführt oder befolgt.
    """
    d = lesen()
    zurueck = set(d.get("zurueckgenommen") or [])
    alle = kennungen_im_text(text)
    ergebnis = []
    for stufe in FAMILIEN:
        geltend = kennung(stufe)
        kandidaten = [k for k in alle if k.startswith(f"claude-{stufe}-")
                      and k not in zurueck]
        if not kandidaten:
            continue
        best = max(kandidaten, key=lambda k: (fassung(k), k))
        if fassung(best) > (fassung(geltend) or (0, 0)):
            ergebnis.append((stufe, geltend, best))
    return ergebnis


def umstellen(stufe: str, neu: str) -> str:
    """Neue Kennung eintragen; die bisherige wird Rückweg. Gibt die bisherige
    zurück. **Die Probe ist damit offen** — Sicherung (2)."""
    d = lesen()
    alt = kennung(stufe)
    d.setdefault("kennungen", {})[stufe] = neu
    d.setdefault("vorige", {})[stufe] = alt
    d.setdefault("probe_offen", {})[stufe] = neu
    d.setdefault("verlauf", []).append(
        {"zeit": int(time.time()), "stufe": stufe, "von": alt, "auf": neu})
    d["verlauf"] = d["verlauf"][-50:]
    schreiben(d)
    return alt


def zuruecknehmen(stufe: str, grund: str) -> "tuple[str, str] | None":
    """Zurück auf die vorige Kennung — per Knopf oder nach gescheiterter Probe.

    Die zurückgenommene Kennung wird gemerkt, damit der Wächter sie am nächsten
    Morgen nicht wieder einträgt: Ein Hin und Her jeden Tag wäre schlimmer als
    ein veraltetes Modell. Gibt (von, auf) zurück, oder None ohne Rückweg.
    """
    d = lesen()
    vor = (d.get("vorige") or {}).get(stufe)
    jetzt = kennung(stufe)
    if not vor or vor == jetzt:
        return None
    d.setdefault("kennungen", {})[stufe] = vor
    (d.get("vorige") or {}).pop(stufe, None)
    (d.get("probe_offen") or {}).pop(stufe, None)
    zurueck = d.setdefault("zurueckgenommen", [])
    if jetzt not in zurueck:
        zurueck.append(jetzt)
    d.setdefault("verlauf", []).append(
        {"zeit": int(time.time()), "stufe": stufe, "von": jetzt, "auf": vor,
         "grund": grund})
    d["verlauf"] = d["verlauf"][-50:]
    schreiben(d)
    return jetzt, vor


def probe_offen(stufe: str) -> "str | None":
    return (lesen().get("probe_offen") or {}).get(stufe)


def probe_bestanden(stufe: str, voll: str) -> bool:
    """Die neue Kennung hat einmal geantwortet — der Rückfall ist nicht mehr
    nötig. Der Rückweg-Knopf bleibt davon unberührt."""
    d = lesen()
    if (d.get("probe_offen") or {}).get(stufe) != voll:
        return False
    d["probe_offen"].pop(stufe, None)
    schreiben(d)
    return True


_MODELL_WORTE = ("not_found", "not found", "invalid", "does not exist",
                 "not available", "unknown", "not allowed", "not supported",
                 "permission",
                 # `[NEU 26.09.2026]` GEMESSEN bei Adams Abo-Probe auf dem VPS:
                 # "API Error: 400 Claude Code 2.1.219 does not support this
                 # model; version 2.1.280 or newer is required." — die Form
                 # „not supported" deckte das NICHT; jede Opus-Anfrage waere
                 # nach dem Deploy mit 400 gescheitert, ohne Rueckfall.
                 "does not support")


def ist_modellfehler(text: str, voll: str) -> bool:
    """Sagt dieser Fehlertext, dass die KENNUNG nicht angenommen wurde?

    ⚠️ **Nur teilweise gemessen:** Eine Form ist seit dem 26.09. bekannt — die
    CLI ist zu alt fuer das Modell (`_MODELL_WORTE`, letzter Eintrag). Wie sie
    einen unbekannten Namen meldet, hat niemand gesehen. Deshalb zwei Wege: Die Kennung selbst steht im Text, oder
    das Wort „model" steht neben einem der Ablehnungswörter. Ein Anmeldefehler
    kommt hier nicht an — der Anmelde-Zweig im Bot steht davor.
    """
    t = (text or "").lower()
    if voll and voll.lower() in t and any(w in t for w in _MODELL_WORTE):
        return True
    return "model" in t and any(w in t for w in _MODELL_WORTE)
