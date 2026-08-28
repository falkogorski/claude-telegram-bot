#!/usr/bin/env python3
# <!-- ROLLE: websuche-check -->
"""Taegliche Probe: Antwortet die Websuche ueberhaupt noch?

**Auftrag 4 aus `2026-08-27_bauauftrag-websuche-faellt-still-aus.md`.** Am
27.08. waren alle vier allgemeinen Zulieferer tot, und **niemand hat es
bemerkt** — der Bot meldete hoeflich [Keine Treffer]. Ein Ausfall, der wie
Ruhe aussieht, braucht eine Wache, die ihn sieht.

**Modellfrei, mit Absicht.** Der Tagescheck laeuft zeitgesteuert; nach der
AGB-Leitplanke des Projekts duerfen solche Laeufe keinen Modell-Aufruf
ausloesen. Hier wird nur der lokale Suchdienst befragt und gerechnet.

**Und die Daempfung ist Teil des Auftrags, nicht Bequemlichkeit:** Drosselung
(CAPTCHA, zu viele Anfragen) ist ein voruebergehender Zustand. Ein Pruefer,
der deshalb taeglich rot meldet, wird binnen zwei Tagen abgeschaltet — dann
haben wir einen blinden Waechter statt eines lauten. Deshalb rot nur, wenn
**alle** ausfallen (dann ist es kein Rauschen) oder der schwache Stand
**zwei Tage hintereinander** auftritt.

Aufruf:  websuche_check.py [--begriff X]   ·  Ausgabe: eine Zeile, Code 0/1/2
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888")
VERLAUF = Path(os.environ.get(
    "WEBSUCHE_VERLAUF",
    Path.home() / ".claude" / "websuche-verlauf.json"))
# Zwei Tage minus eine Stunde Spielraum: Der Tagescheck laeuft taeglich zur
# selben Zeit, aber nicht auf die Minute. Ohne Spielraum faellt ein Lauf, der
# zwei Minuten frueher kommt, aus dem Fenster.
FENSTER_S = 2 * 24 * 3600 - 3600


def _hole(pfad: str, frist: int = 25) -> dict:
    with urllib.request.urlopen(f"{SEARXNG_URL}{pfad}", timeout=frist) as r:
        return json.load(r)


def _gesamt_allgemein() -> int | None:
    """Aktive Zulieferer der Kategorie [general] — **vom Dienst erfragt.**

    Keine Namensliste: Gemessen am 28.08. waren drei Zulieferer aktiv, die der
    Bauauftrag als [nicht aktiviert] fuehrte. Eine getippte Liste haette vom
    ersten Tag an danebengelegen.
    """
    try:
        engines = _hole("/config", 10).get("engines") or []
    except Exception:
        return None
    return sum(1 for e in engines
               if e.get("enabled") and "general" in (e.get("categories") or []))


def _verlauf_lesen() -> dict:
    try:
        return json.loads(VERLAUF.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _verlauf_schreiben(stand: dict) -> None:
    try:
        VERLAUF.parent.mkdir(parents=True, exist_ok=True)
        VERLAUF.write_text(json.dumps(stand), encoding="utf-8")
    except Exception:
        pass                      # ein nicht schreibbarer Verlauf darf nichts brechen


def beurteilen(lage: str, geantwortet: int | None, vorher: dict,
               jetzt: float) -> tuple[str, bool]:
    """Aus Lage und Vorgeschichte die Meldung ableiten — **reine Funktion.**

    Herausgezogen, damit ein Pruefer sie **ausfuehren** kann, statt ihren
    Quelltext zu lesen. Gibt `(stufe, schwach)` zurueck; `stufe` ist `rot`,
    `gelb` oder `gruen`, `schwach` wandert in den Verlauf.
    """
    if lage == "ausgefallen":
        return ("rot", True)            # alle tot - kein Rauschen, sofort melden
    schwach = geantwortet is not None and geantwortet < 2
    if not schwach:
        return ("gruen", False)
    war_schwach = bool(vorher.get("schwach")) and \
        (jetzt - float(vorher.get("zeit") or 0)) <= FENSTER_S
    return ("rot" if war_schwach else "gelb", True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--begriff", default="wetter berlin")
    a = p.parse_args()
    try:
        import bot
    except Exception as e:
        print(f"❌ Websuche-Probe: bot nicht ladbar ({type(e).__name__})")
        return 2
    try:
        daten = _hole(f"/search?q={urllib.parse.quote(a.begriff)}&format=json")
    except Exception as e:
        print(f"❌ Websuche-Probe: Suchdienst nicht erreichbar ({type(e).__name__}: {e})")
        return 2

    gesamt = _gesamt_allgemein()
    lage, hinweis = bot.suchlage(daten, gesamt)
    aus = bot._such_ausfaelle(daten)
    geantwortet = (gesamt - len(aus)) if gesamt else None
    jetzt = time.time()
    stufe, schwach = beurteilen(lage, geantwortet, _verlauf_lesen(), jetzt)
    _verlauf_schreiben({"schwach": schwach, "zeit": jetzt, "lage": lage})

    wer = f"{geantwortet} von {gesamt}" if gesamt else "unbekannt viele"
    if stufe == "rot":
        print(f"❌ Websuche: {wer} Zulieferer antworten. {hinweis or ''}".strip())
        return 1
    if stufe == "gelb":
        print(f"⚠️ Websuche schwach: {wer} Zulieferer antworten — "
              f"erst bei Wiederholung morgen eine Meldung. {hinweis or ''}".strip())
        return 0
    print(f"✅ Websuche: {wer} Zulieferer antworten, "
          f"{len(daten.get('results') or [])} Treffer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
