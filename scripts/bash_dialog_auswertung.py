#!/usr/bin/env python3
"""Legt nach sieben Tagen den Befund zur Bash-Positivliste von selbst vor.
<!-- ROLLE: bash-dialog-auswertung -->

**Adams Nachtrag vom 29.08.2026, 01:2x:** *„Sie werden über kurz oder lang
nerven. Messdaten proaktiv hinzuziehen bitte!"* — Engywuck hat daraus eine
Bringschuld gemacht: Der Befund kommt von selbst, statt darauf zu warten,
dass jemand nachfragt.

**Modellfrei, wie die Kostenregel es verlangt.** Kein Claude-Aufruf, kein
Netz, keine Kosten — reines Zählen. Damit ist der Zeitgeber auch AGB-seitig
unbedenklich (siehe `CLAUDE.md`, Abschnitt zur Automatik-Regel).

## Die Stoßrichtung der Vorschläge ist festgelegt

Engywuck hat sie ausdrücklich vorgegeben, damit sie nicht in die falsche
Richtung wachsen:

> Wiederkehrende gleichartige Dialoge werden durch **benannte, geprüfte
> Skripte** ersetzt, die einzeln in die Positivliste rücken — **nie durch
> Öffnen einer Klasse.** `python3 <beliebig>` bleibt dialogpflichtig, ein
> benanntes `scripts/<zweck>.py` mit fester Funktion kann freigegeben werden.

**So sinken die verbleibenden ~40 Dialoge weiter, ohne dass die Grenze fällt,
die die ganze Konstruktion trägt.**

## Was dieses Skript NICHT tut

Es ändert nichts. Es schlägt vor. Jede Erweiterung der Positivliste ist ein
Bauauftrag, keine Zeile nebenbei — so steht es im Auftrag, und so bleibt es.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

# Benannte Größen, nicht hart im Code (Engywucks Entscheid 4 zu den 50):
TAKT_TAGE = int(os.environ.get("BASHFREI_TAKT_TAGE") or 7)
SCHWELLE_DIALOGE = int(os.environ.get("BASHFREI_SCHWELLE") or 50)
# Ab wann eine Befehlsart als „Wiederkehrer" gilt, der einen Vorschlag verdient.
WIEDERKEHRER_AB = int(os.environ.get("BASHFREI_WIEDERKEHRER_AB") or 5)


def _datei() -> Path:
    roh = os.environ.get("BASHFREI_PROTOKOLL")
    if roh:
        return Path(roh).expanduser()
    heim = Path(os.environ.get("BASHFREI_HEIM") or Path.home()).expanduser()
    return heim / ".claude" / "bash-freigaben.jsonl"


def lesen(datei: Path, seit: datetime) -> list[dict]:
    """Die Zeilen ab `seit`. Eine kaputte Zeile wird übersprungen, nicht
    verschluckt — sie erscheint als Zählwert im Bericht."""
    zeilen: list[dict] = []
    kaputt = 0
    try:
        text = datei.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    for roh in text.splitlines():
        if not roh.strip():
            continue
        try:
            d = json.loads(roh)
            wann = datetime.strptime(d["zeit"], "%Y-%m-%d %H:%M:%S")
        except Exception:
            kaputt += 1
            continue
        if wann >= seit:
            zeilen.append(d)
    if kaputt:
        zeilen.append({"urteil": "_kaputt", "art": "", "bereich": "", "anzahl": kaputt})
    return zeilen


def beurteilen(zeilen: list[dict]) -> dict:
    """Reine Funktion — damit ein Prüfer sie ohne Datei und ohne Uhr messen kann.

    Dieselbe Bauform wie `beurteilen()` im Websuche-Wächter: Die Entscheidung
    liegt getrennt vom Einlesen, sonst könnte ein Prüfer sie nur über
    Textsuche erreichen.
    """
    kaputt = sum(z.get("anzahl", 0) for z in zeilen if z.get("urteil") == "_kaputt")
    echte = [z for z in zeilen if z.get("urteil") != "_kaputt"]
    nach_urteil = Counter(z.get("urteil", "?") for z in echte)
    dialoge = [z for z in echte if z.get("urteil") == "dialog"]
    wiederkehrer = Counter(z.get("art", "?") for z in dialoge)

    vorschlaege: list[str] = []
    for art, wieviel in wiederkehrer.most_common():
        if wieviel < WIEDERKEHRER_AB:
            continue
        if art in ("python3", "python", "bash", "sh", "node", "perl", "make"):
            vorschlaege.append(
                f"[{art}] {wieviel}× — NICHT die Klasse öffnen. Stattdessen die "
                f"wiederkehrenden Aufrufe in ein benanntes Skript unter "
                f"scripts/ fassen und DIESES einzeln freigeben.")
        else:
            vorschlaege.append(
                f"[{art}] {wieviel}× — prüfen, ob dieses Verb auf die "
                f"Positivliste gehört. Erweiterung ist ein Bauauftrag, keine "
                f"Zeile nebenbei.")

    return {
        "gesamt": len(echte),
        "frei": nach_urteil.get("frei", 0),
        "dialog": nach_urteil.get("dialog", 0),
        "abgewiesen": nach_urteil.get("abweisen", 0),
        "kaputte_zeilen": kaputt,
        "wiederkehrer": wiederkehrer.most_common(10),
        "vorschlaege": vorschlaege,
        "ziel_erreicht": nach_urteil.get("dialog", 0) < SCHWELLE_DIALOGE,
    }


def bericht(b: dict) -> str:
    z = [f"Bash-Freigaben der letzten {TAKT_TAGE} Tage", ""]
    if b["gesamt"] == 0:
        # **Der Prüflauf hat hier einen stillen Fehler gefunden.** Eine Ablage
        # aus lauter unlesbaren Zeilen hat `gesamt == 0` — und meldete damit
        # „keine Aufrufe verzeichnet", also Ruhe. Das ist die schlimmste
        # Auskunft, die dieser Bericht geben kann: Er hätte eine kaputte
        # Messung als ruhige Woche ausgegeben.
        if b["kaputte_zeilen"]:
            z.append(f"KEINE lesbare Zeile, aber {b['kaputte_zeilen']} unlesbare. "
                     "Die Ablage ist beschädigt — das ist kein ruhiger Zeitraum, "
                     "sondern ein Befund.")
            return "\n".join(z)
        z.append("Keine Aufrufe verzeichnet. Entweder war es ruhig — oder die "
                 "Ablage wird nicht mehr beschrieben. Beides ist einen Blick wert.")
        return "\n".join(z)
    z.append(f"{b['gesamt']} Aufrufe: {b['frei']} ohne Rückfrage, "
             f"{b['dialog']} mit Dialog, {b['abgewiesen']} abgewiesen.")
    z.append("")
    if b["ziel_erreicht"]:
        z.append(f"Das Maß ist erreicht: unter {SCHWELLE_DIALOGE} Dialoge je Woche.")
    else:
        z.append(f"Das Maß ist NICHT erreicht: {b['dialog']} Dialoge, "
                 f"vorgesehen waren unter {SCHWELLE_DIALOGE}.")
    if b["wiederkehrer"]:
        z += ["", "Häufigste Dialog-Auslöser:"]
        z += [f"  {art}: {n}×" for art, n in b["wiederkehrer"]]
    if b["vorschlaege"]:
        z += ["", "Vorschläge:"]
        z += [f"  · {v}" for v in b["vorschlaege"]]
    if b["kaputte_zeilen"]:
        z += ["", f"{b['kaputte_zeilen']} unlesbare Zeile(n) übersprungen — "
                  "eine unlesbare Ablage ist ein Befund, kein Abbruch."]
    return "\n".join(z)


def main() -> int:
    jetzt = datetime.now()
    zeilen = lesen(_datei(), jetzt - timedelta(days=TAKT_TAGE))
    print(bericht(beurteilen(zeilen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
