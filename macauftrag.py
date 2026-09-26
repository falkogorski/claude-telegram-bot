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
import shutil
import stat
import sys
import time
from pathlib import Path

ARTEN = ("probe",)
FRIST_S = 24 * 3600          # Konzept Teil 2: nach 24 Stunden meldet es sich
GROESSE_MAX = 64 * 1024     # dieselbe Grenze wie am Mac (videoarbeiter.py)
AUFHEBEN_S = 30 * 86400      # Ergebnisordner ohne Auftrag, danach geraeumt (K5)
# Nur ASCII-Ziffern, ganzer Name (Widerlegungspruefung K1).
KENNUNG = re.compile(r"[0-9]{8}T[0-9]{6}-[0-9a-f]{6}", re.ASCII)


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
        return jetzt - pfad.lstat().st_mtime
    except OSError:
        return None


def _regulaer(pfad: Path) -> bool:
    """Eine echte Datei — kein Link, kein Ordner (Widerlegungspruefung S1, S9)."""
    try:
        return stat.S_ISREG(pfad.lstat().st_mode)
    except OSError:
        return False


def menschlich(sekunden: float | None) -> str:
    if sekunden is None:
        return "noch nie"
    if sekunden < 5400:
        return f"vor {max(1, round(sekunden / 60))} Minuten"
    if sekunden < 48 * 3600:
        return f"vor etwa {round(sekunden / 3600)} Stunden"
    return f"vor {round(sekunden / 86400)} Tagen"


def _quittung(rueck: Path) -> dict | None:
    """Die `fertig.json` eines Auftrags — nur als echte, kleine Datei gelesen."""
    f = rueck / "fertig.json"
    if not _regulaer(f) or f.lstat().st_size > 64 * 1024:
        return None
    try:
        daten = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"abgelehnt": "Quittung nicht lesbar"}
    return daten if isinstance(daten, dict) else {"abgelehnt": "Quittung kein Objekt"}


def _ein_auftrag(eintrag: Path, erg: Path, jetzt: float,
                 lebenszeichen: float | None) -> tuple[list[tuple[str, str]], bool]:
    """Zeilen und ob der Auftrag noch offen ist."""
    name = eintrag.name
    stamm = name[:-5] if name.endswith(".json") else ""
    if not stamm or not KENNUNG.fullmatch(stamm) or not _regulaer(eintrag):
        return [("intern", f"fremder Eintrag im Auftragsordner: {name[:60]!r} "
                           f"(keine Auftragsdatei) — liegt und wird nicht geholt")], False
    if eintrag.lstat().st_size > GROESSE_MAX:
        # Der Mac holt nur bis 64 KB; ohne diese Zeile hiesse es nach 24
        # Stunden faelschlich „ungeholt, der Mac war aus".
        return [("intern", f"Auftrag {stamm} ist groesser als 64 KB — "
                           f"der Mac holt ihn nicht")], False
    rueck = erg / stamm
    quittung = _quittung(rueck)
    if quittung is not None:
        eintrag.unlink(missing_ok=True)       # der Mac darf nicht loeschen
        if "abgelehnt" in quittung:
            # Eine Ablehnung ist kein Erfolg (S3) — sonst verschwaende im
            # zweiten Schnitt ein Videoauftrag still, wenn die Positivlisten
            # auseinanderlaufen.
            return [("rot", f"Mac-Auftrag {stamm} vom Mac abgelehnt: "
                            f"{str(quittung.get('abgelehnt'))[:80]}")], False
        return [("ok", f"Mac-Auftrag {stamm} zurueckgekommen, erledigt "
                       f"({str(quittung.get('art', '?'))[:20]})")], False
    alter = _alter(eintrag, jetzt) or 0
    if alter < FRIST_S:
        return [], True
    if _regulaer(rueck / "geholt.json"):
        return [("rot", f"Mac-Auftrag {stamm} abgeholt, aber seit "
                        f"{menschlich(alter).removeprefix('vor ')} nicht zurueckgekommen")], True
    return [("rot", f"Mac-Auftrag {stamm} liegt seit "
                    f"{menschlich(alter).removeprefix('vor ')} ungeholt — "
                    f"der Mac meldete sich zuletzt {menschlich(lebenszeichen)}")], True


def stand(jetzt: float | None = None) -> list[tuple[str, str]]:
    """Aufräumen und den Stand melden: Liste von (Art, Text).

    `rot` heißt: Adam soll es wissen. `intern` geht an die Kontrolle, `ok` ist
    eine Protokollzeile. **Kein Eintrag bringt den Stand zum Absturz** (S1):
    Jeder wird für sich geprüft, ein Fehler wird selbst zur Zeile.
    """
    jetzt = jetzt or time.time()
    aus, erg = auftraege(), ergebnisse()
    if not aus.is_dir():
        return [("ok", "Mac-Weg nicht eingerichtet (kein Auftragsordner) — nichts zu pruefen")]
    lebenszeichen = _alter(erg / ".mac-zuletzt", jetzt) if _regulaer(erg / ".mac-zuletzt") else None
    zeilen: list[tuple[str, str]] = []
    offen = 0
    for eintrag in sorted(aus.iterdir()):
        if eintrag.name.startswith("."):
            continue                            # halbe Auftraege (.teil-…)
        try:
            neu, noch_offen = _ein_auftrag(eintrag, erg, jetzt, lebenszeichen)
        except Exception as e:
            neu, noch_offen = [("intern", f"Eintrag {eintrag.name[:60]!r} nicht pruefbar: "
                                          f"{type(e).__name__}: {e}")], False
        zeilen += neu
        offen += noch_offen
    # Ergebnisordner ohne Auftrag nach 30 Tagen raeumen (K5) — nur echte Ordner.
    if erg.is_dir():
        for d in erg.iterdir():
            try:
                if (stat.S_ISDIR(d.lstat().st_mode) and KENNUNG.fullmatch(d.name)
                        and not (aus / f"{d.name}.json").exists()
                        and (_alter(d, jetzt) or 0) > AUFHEBEN_S):
                    shutil.rmtree(d)
            except OSError:
                pass
    zeilen.append(("ok", f"Mac-Weg: {offen} Auftrag/Auftraege offen, letztes Lebenszeichen "
                         f"{menschlich(lebenszeichen)}"))
    # Eine Zeile je Befund, ohne Zeilenumbruch — sonst zerfiele sie im
    # Tagescheck in eine Zeile ohne Tuer (K1).
    return [(a, " ".join(t.split())) for a, t in zeilen]


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
