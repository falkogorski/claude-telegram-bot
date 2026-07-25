#!/usr/bin/env python3
# <!-- ROLLE: nachzieher -->
"""C1 — Folge-Korrekturen nachziehen, ohne die Governance aufzuweichen.

**Das Problem (Adam 25.07.):** Spielt der Updater eine neue Fassung ein, zeigt
`requirements.txt` weiter auf die alte. Beim nächsten Wiederaufbau fiele das
System stillschweigend zurück — genau die Abhängigkeit, die C2 als Divergenz
meldet. Jemand muss den Pin nachziehen.

**Warum nicht einfach der Bot selbst (Variante 2, abgelehnt):**
`requirements.txt` ist eine **Steuerdatei, keine Doku** — sie zu schreiben ist
wirkungsgleich mit Code schreiben. Eine Ausnahme im Schreibschutz ausgerechnet
für den Prozess, der fremden Text verarbeitet, kehrt 8.7 um.

**Variante 1, hier umgesetzt:** Der Bot erzeugt nur einen **strukturierten
Folge-Patch** (reine Felder, kein Fließtext — also nichts, worin sich eine
Anweisung verstecken ließe). Dieser Nachzieher läuft **außerhalb** des Bots,
prüft gegen **zwei Weißlisten** und wendet an:

1. **Weißliste Dateien** — nur `requirements.txt` und `components.json`.
2. **Weißliste Inhalte** — nur **Versions-Literale**. Paketname und Version
   müssen strengen Mustern genügen; verändert werden darf ausschließlich die
   Zeichenfolge der Version in einer bereits vorhandenen Pin-Zeile.

Zusätzlich wird **nachgemessen statt geglaubt**: Nach dem Schreiben muss der
Unterschied genau eine Zeile betreffen, und die neue Zeile muss aus der alten
durch Ersetzen der Version hervorgehen. Trifft das nicht zu, wird die Datei
unverändert zurückgelegt.

Aufruf:

    python3 scripts/nachzieher.py --patch ~/postfach/nachzieher/<datei>.json \\
        [--repo /pfad/zum/repo] [--commit] [--pruefen]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ── Weißliste 1: Dateien ────────────────────────────────────────────────────
ERLAUBTE_DATEIEN = {"requirements.txt", "components.json"}

# ── Weißliste 2: Inhalte (nur Versions-Literale) ────────────────────────────
PAKET_MUSTER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}$")
VERSION_MUSTER = re.compile(r"^\d+(?:\.\d+){0,3}[A-Za-z0-9.\-]{0,20}$")
PFLICHTFELDER = ("datei", "paket", "von", "nach")


class Abgelehnt(Exception):
    """Der Patch hat eine Weißliste verletzt — es wird nichts geschrieben."""


def pruefe_patch(patch: dict) -> None:
    """Beide Weißlisten, bevor irgendetwas angefasst wird."""
    if not isinstance(patch, dict):
        raise Abgelehnt("Patch ist kein Objekt")
    unbekannt = set(patch) - set(PFLICHTFELDER) - {"grund", "erzeugt"}
    if unbekannt:
        raise Abgelehnt(f"unbekannte Felder: {sorted(unbekannt)}")
    for feld in PFLICHTFELDER:
        if not isinstance(patch.get(feld), str) or not patch[feld].strip():
            raise Abgelehnt(f"Feld fehlt oder ist kein Text: {feld}")
    if patch["datei"] not in ERLAUBTE_DATEIEN:
        raise Abgelehnt(f"Datei nicht auf der Weißliste: {patch['datei']}")
    if not PAKET_MUSTER.match(patch["paket"]):
        raise Abgelehnt(f"Paketname entspricht nicht dem Muster: {patch['paket']!r}")
    for feld in ("von", "nach"):
        if not VERSION_MUSTER.match(patch[feld]):
            raise Abgelehnt(f"{feld}-Version ist kein Versions-Literal: {patch[feld]!r}")
    if patch["von"] == patch["nach"]:
        raise Abgelehnt("alte und neue Version sind gleich — nichts zu tun")
    # „grund" ist reine Nachvollziehbarkeit und wird NIE ausgeführt oder
    # weitergereicht; er darf keine Steuerzeichen tragen.
    grund = patch.get("grund", "")
    if grund and (len(grund) > 200 or any(c in grund for c in "\n\r\x00`$")):
        raise Abgelehnt("Grund-Feld unzulässig (zu lang oder mit Steuerzeichen)")


def _zeilen_diff(alt: str, neu: str) -> list[tuple[int, str, str]]:
    a, b = alt.splitlines(), neu.splitlines()
    if len(a) != len(b):
        return [(-1, "", "")]            # Zeilenzahl geändert → verdächtig
    return [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]


def wende_an(patch: dict, repo: Path, schreiben: bool = True) -> dict:
    """Ersetzt genau ein Versions-Literal — und misst danach nach."""
    pruefe_patch(patch)
    ziel = repo / patch["datei"]
    if not ziel.exists():
        raise Abgelehnt(f"Zieldatei nicht vorhanden: {ziel}")
    alt = ziel.read_text(encoding="utf-8")

    paket, von, nach = patch["paket"], patch["von"], patch["nach"]
    # Nur eine bereits vorhandene Pin-Zeile darf sich ändern — das Paket muss
    # also schon dort stehen. Neue Zeilen anzulegen ist ausdrücklich nicht
    # Aufgabe dieses Werkzeugs.
    muster = re.compile(
        r"(^|\n)(?P<zeile>\s*" + re.escape(paket) + r"(?:\[[^\]]*\])?\s*==\s*)"
        + re.escape(von) + r"(?=\s|$)")
    treffer = list(muster.finditer(alt))
    if not treffer:
        raise Abgelehnt(f"kein Pin {paket}=={von} in {patch['datei']} gefunden")
    if len(treffer) > 1:
        raise Abgelehnt(f"{paket}=={von} kommt mehrfach vor — von Hand klären")

    neu = alt[:treffer[0].start()] + treffer[0].group(0).replace(von, nach) \
        + alt[treffer[0].end():]

    unterschiede = _zeilen_diff(alt, neu)
    if len(unterschiede) != 1 or unterschiede[0][0] < 0:
        raise Abgelehnt("der Unterschied betrifft nicht genau eine Zeile")
    _, zeile_alt, zeile_neu = unterschiede[0]
    if zeile_alt.replace(von, nach) != zeile_neu:
        raise Abgelehnt("die neue Zeile geht nicht aus der alten durch reines "
                        "Ersetzen der Version hervor")

    if schreiben:
        ziel.write_text(neu, encoding="utf-8")
    return {"datei": patch["datei"], "zeile_alt": zeile_alt.strip(),
            "zeile_neu": zeile_neu.strip(), "geschrieben": schreiben}


def committe(repo: Path, dateien: list[str], text: str) -> tuple[bool, str]:
    try:
        subprocess.run(["git", "add", *dateien], cwd=str(repo), check=True,
                       capture_output=True, text=True, timeout=60)
        p = subprocess.run(["git", "commit", "-m", text], cwd=str(repo),
                           capture_output=True, text=True, timeout=120)
        return p.returncode == 0, (p.stdout + p.stderr)[-400:]
    except Exception as e:
        return False, str(e)


def main() -> int:
    ap = argparse.ArgumentParser(description="C1 Nachzieher (Variante 1)")
    ap.add_argument("--patch", required=True)
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--pruefen", action="store_true",
                    help="nur prüfen und zeigen, nichts schreiben")
    a = ap.parse_args()

    try:
        patch = json.loads(Path(a.patch).read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Patch nicht lesbar: {e}")
        return 2
    try:
        ergebnis = wende_an(patch, Path(a.repo), schreiben=not a.pruefen)
    except Abgelehnt as e:
        print(f"⛔ Abgelehnt: {e}")
        return 1

    print(f"{'geprüft' if a.pruefen else 'angewendet'}: {ergebnis['datei']}\n"
          f"  vorher:  {ergebnis['zeile_alt']}\n"
          f"  nachher: {ergebnis['zeile_neu']}")
    if a.commit and not a.pruefen:
        ok, aus = committe(Path(a.repo), [ergebnis["datei"]],
                           f"Nachzieher (C1): {patch['paket']} "
                           f"{patch['von']} → {patch['nach']}")
        print(("✅ committet" if ok else f"⚠️ Commit fehlgeschlagen: {aus}"))
        return 0 if ok else 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
