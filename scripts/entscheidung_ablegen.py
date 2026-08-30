#!/usr/bin/env python3
# <!-- ROLLE: entscheidung-ablegen -->
"""Eine im Gespraech gefallene Entscheidung ablegen — der bewusste Handgriff.

**Claudias Bauauftrag vom 28.08., Auftrag 2.** Das Entscheidungs-Protokoll war
gebaut und leer: null Eintraege, die Ordner seit dem 25.07. unveraendert. Der
Grund war kein Fehler, sondern ein Zuschnitt — es erfasst Urteile aus dem
**Freigabe-Postfach**, also Antworten auf formelle Anfragen. Adams
Entscheidungen fallen aber ueberwiegend **frei im Gespraech**, als
Sprachnachricht, und hatten keinen Weg in die Ablage.

Der eigene Kopfsatz des Protokolls galt damit gegen es selbst:
*Eine Entscheidung, die keinen Weg in die Ablage hat, ist verloren.*

## Handgriff, nicht Automatik — und das ist die Setzung

Claudia hat diese Frage ausdruecklich Engywuck ueberlassen. Gebaut ist die
**sichere Haelfte**: Die Sitzung, die eine Entscheidung entgegennimmt, legt sie
ab. Automatik erzeugte hier leicht erfundene Urteile; der Fall dazu ist belegt
und derselbe Tag: Claudias erste Formulierung machte aus Adams *bedingter*
Ablehnung eine grundsaetzliche. Bei automatischer Ablage staende jetzt eine zu
weit gefasste Entscheidung im Protokoll — die etwas verboete, das er erlaubt
hat.

## Aufruf

    python3 scripts/entscheidung_ablegen.py \\
        --zitat "Das mit Fehlern zu machen, das ist alles manipulativ" \\
        --sache "Eingebaute Maengel im Gegenleser-Pruefverfahren" \\
        --urteil abgelehnt \\
        --am "2026-08-27 18:11"

Danach traegt `scripts/entscheidungs_protokoll.py` die Zeile ins Drehbuch —
derselbe Weg wie fuer Postfach-Urteile, nicht ein zweiter. **Erst mit einer
gefuehrten Liste abgelehnter Punkte wird eine Gegenpruefung ueberhaupt
moeglich**; ohne sie gibt es nichts, wogegen man pruefen koennte.

Deterministisch, ohne Modell-Aufruf, ohne Kosten.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import freigaben  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Eine im Gespraech gefallene Entscheidung ins Protokoll legen")
    ap.add_argument("--zitat", required=True,
                    help="WOERTLICH, was Adam gesagt hat. Pflicht: Eine "
                         "zusammengefasste Entscheidung ist eine Auslegung.")
    ap.add_argument("--sache", required=True, help="Worum es ging")
    ap.add_argument("--urteil", required=True,
                    choices=("freigegeben", "abgelehnt", "festgelegt"))
    ap.add_argument("--am", default="",
                    help="Zeitpunkt der Entscheidung, z. B. '2026-08-27 18:11'. "
                         "Ohne Angabe: jetzt.")
    ap.add_argument("--von", default="Adam", help="Wer entschieden hat")
    ap.add_argument("--herkunft", default="Gespräch",
                    help="Wo die Entscheidung fiel (Bot-Chat, Sprachnachricht …)")
    a = ap.parse_args()
    try:
        e = freigaben.gespraechsentscheidung(
            zitat=a.zitat, sache=a.sache, urteil=a.urteil, von=a.von,
            gefallen_am=a.am, herkunft=a.herkunft)
    except freigaben.Abgewiesen as fehler:
        print(f"❌ {fehler}", file=sys.stderr)
        return 2
    print(f"✅ Abgelegt: {e['kennung']}\n"
          f"   {e['beantwortet_am']} · {e['urteil']} · {e['titel']}\n"
          f"   {e['grund']}\n\n"
          "Naechster Schritt: python3 scripts/entscheidungs_protokoll.py "
          "--commit  (traegt die Zeile ins Drehbuch)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
