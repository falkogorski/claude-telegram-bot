#!/usr/bin/env python3
# <!-- ROLLE: mac-auftrag -->
"""Aufträge an den Mac — die Serverseite von Block 7, erster Schnitt (26.09.2026).

Grundlage: Micks Konzept `docs/auftraege/20260924_konzept_mac_videoarbeiter.md`,
Engywucks Antworten im Zettel 25.09. (Teil 1), Adams Wort vom 26.09.
(„ja, bau Block 7").

Der Weg, ganz kurz: Der Server legt einen Auftrag in `~/mac-auftraege/`. Der
Mac holt ihn alle 30 Minuten mit einem Schlüssel, der **nur lesen** darf, und
legt Quittungen mit einem zweiten Schlüssel, der **nur schreiben** darf, in
`~/mac-ergebnisse/<kennung>/`. Beide Schlüssel sind auf dem Server per
`rrsync` an genau ihren Ordner gebunden (Engywucks Auflage).

**Aufgeräumt wird hier, nicht am Mac** — gemessen am 26.09.: `rrsync -ro`
sperrt `--remove-source-files`. Ein nur lesender Eingang kann kein
Durchgangsordner sein; also räumt der Server einen Auftrag weg, sobald dessen
`fertig.json` da ist. Das tut `--stand` im Tagescheck.

**Im ersten Schnitt gibt es genau eine Art: `probe`.** Kein Modellaufruf, nur
Standardbibliothek.

Aufruf (auf dem VPS, als claudebot):
    python3 macauftrag.py --probe     # einen Probeauftrag ablegen
    python3 macauftrag.py --stand     # aufräumen und den Stand melden
"""
from __future__ import annotations

import json
import os
import re
import secrets
import sys
import time
from pathlib import Path

ARTEN = ("probe",)
FRIST_S = 24 * 3600          # Konzept Teil 2: nach 24 Stunden meldet es sich
KENNUNG = re.compile(r"^\d{8}T\d{6}-[0-9a-f]{6}$")


def auftraege() -> Path:
    return Path(os.environ.get("MAC_AUFTRAEGE") or Path.home() / "mac-auftraege")


def ergebnisse() -> Path:
    return Path(os.environ.get("MAC_ERGEBNISSE") or Path.home() / "mac-ergebnisse")


def neue_kennung(jetzt: float | None = None) -> str:
    t = time.strftime("%Y%m%dT%H%M%S", time.localtime(jetzt or time.time()))
    return f"{t}-{secrets.token_hex(3)}"


def ablegen(art: str = "probe", *, jetzt: float | None = None) -> str:
    """Einen Auftrag atomar ablegen und seine Kennung zurückgeben.

    Atomar heißt: erst unter einem Punkt-Namen schreiben, dann umbenennen. Der
    Mac holt keine Punkt-Dateien — er sieht nie einen halben Auftrag.
    """
    if art not in ARTEN:
        raise ValueError(f"unbekannte Art [{art}] — erlaubt: {', '.join(ARTEN)}")
    ordner = auftraege()
    ordner.mkdir(parents=True, exist_ok=True)
    kennung = neue_kennung(jetzt)
    daten = {"kennung": kennung, "art": art, "von": "vps",
             "erstellt": time.strftime("%Y-%m-%dT%H:%M:%S",
                                       time.localtime(jetzt or time.time()))}
    teil = ordner / f".teil-{kennung}.json"
    teil.write_text(json.dumps(daten, ensure_ascii=False), encoding="utf-8")
    os.replace(teil, ordner / f"{kennung}.json")
    return kennung


def _alter(pfad: Path, jetzt: float) -> float | None:
    try:
        return jetzt - pfad.stat().st_mtime
    except OSError:
        return None


def menschlich(sekunden: float | None) -> str:
    if sekunden is None:
        return "noch nie"
    if sekunden < 5400:
        return f"vor {max(1, round(sekunden / 60))} Minuten"
    if sekunden < 48 * 3600:
        return f"vor etwa {round(sekunden / 3600)} Stunden"
    return f"vor {round(sekunden / 86400)} Tagen"


def stand(jetzt: float | None = None) -> list[tuple[str, str]]:
    """Aufräumen und den Stand melden: Liste von (Art, Text).

    Art `rot` heißt: Adam soll es wissen. `ok` ist eine Protokollzeile.
    """
    jetzt = jetzt or time.time()
    aus, erg = auftraege(), ergebnisse()
    if not aus.is_dir():
        return [("ok", "Mac-Weg nicht eingerichtet (kein Auftragsordner) — nichts zu pruefen")]
    lebenszeichen = _alter(erg / ".mac-zuletzt", jetzt)
    zeilen: list[tuple[str, str]] = []
    offen = 0
    for datei in sorted(aus.glob("*.json")):
        kennung = datei.stem
        if not KENNUNG.match(kennung):
            continue
        rueck = erg / kennung
        if (rueck / "fertig.json").is_file():
            datei.unlink(missing_ok=True)       # der Mac darf nicht loeschen
            zeilen.append(("ok", f"Mac-Auftrag {kennung} zurueckgekommen, aufgeraeumt"))
            continue
        offen += 1
        alter = _alter(datei, jetzt) or 0
        if alter < FRIST_S:
            continue
        if (rueck / "geholt.json").is_file():
            zeilen.append(("rot", f"Mac-Auftrag {kennung} abgeholt, aber seit "
                                  f"{menschlich(alter).removeprefix('vor ')} nicht zurueckgekommen"))
        else:
            zeilen.append(("rot", f"Mac-Auftrag {kennung} liegt seit "
                                  f"{menschlich(alter).removeprefix('vor ')} ungeholt — "
                                  f"der Mac meldete sich zuletzt {menschlich(lebenszeichen)}"))
    zeilen.append(("ok", f"Mac-Weg: {offen} Auftrag/Auftraege offen, letztes Lebenszeichen "
                         f"{menschlich(lebenszeichen)}"))
    return zeilen


def main(argv: list[str]) -> int:
    if argv[1:] == ["--probe"]:
        print(ablegen("probe"))
        return 0
    if argv[1:] == ["--stand"]:
        for art, text in stand():
            print(f"{art.upper()}: {text}")
        return 0
    print(__doc__.split("Aufruf")[1] if "Aufruf" in __doc__ else "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
