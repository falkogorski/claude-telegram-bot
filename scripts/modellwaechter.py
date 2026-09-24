#!/usr/bin/env python3
# <!-- ROLLE: modellwaechter -->
"""Modellwächter — erkennt neue Claude-Fassungen und stellt um (Block 4).

`[NEU 24.09.2026]` Claudias Auftrag vom 23.09.; Bezugsquelle nach Engywucks
Berichtigung (Block 6, Fassung 2): der Anthropic-Release-Notes-Feed —
kostenfrei, ohne Schlüssel. Die Abo-Token-Messung gegen eine Modell-Liste
entfällt damit.

**Adams Entscheid vom 23.09.: umstellen von selbst, mit drei Sicherungen.**
Dieses Skript trägt (1) und (3):
  (1) Es schreibt NUR `models.json` und meldet laut über die Botenpost — mit
      einem Rückweg-Knopf, der ohne Modellstart wirkt.
  (3) Es ruft nie ein Modell auf. Es liest einen Feed und vergleicht
      Zeichenketten.
Sicherung (2), der Rückfall bei gescheiterter erster Nachricht, sitzt im Bot.

Aufruf aus dem Tagescheck, als claudebot (dessen `models.json`, dessen
Postfach). Eine Zeile Ausgabe, die der Tagescheck einstuft:
  UNVERAENDERT …      — nur Protokoll
  UMGESTELLT …        — an Adam (die Botenpost-Meldung trägt den Knopf)
  FEHLER …            — an die Kontrolle (⚙️): Schweigt die Quelle, sähe das
                        sonst aus wie „nichts Neues" (Claudias Tabelle)

`--trocken`: liest und vergleicht, schreibt und meldet nichts.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import modellwahl                                               # noqa: E402

ZEITLIMIT_S = 20
_ANZEIGE = {"opus": "Opus", "sonnet": "Sonnet", "haiku": "Haiku", "fable": "Fable"}


def abrufen(url: str = modellwahl.FEED) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-telegram-bot/modellwaechter"})
    with urllib.request.urlopen(req, timeout=ZEITLIMIT_S) as r:
        if r.status != 200:
            raise RuntimeError(f"Antwort {r.status}")
        return r.read(2_000_000).decode("utf-8", errors="replace")


def seit_wann(text: str, kennung: str) -> str:
    """Das Datum des ersten Feed-Eintrags, der die Kennung nennt — oder leer.

    Per Muster, nicht per XML-Zerleger: Ein Zerleger löst Entitäten auf, und
    fremdes XML mit Entitäten-Kaskaden ist eine bekannte Falle. Hier wird nur
    gesucht, nichts aufgelöst.
    """
    for block in re.findall(r"<item>(.*?)</item>", text, re.S):
        if kennung in block:
            m = re.search(r"<pubDate>\w{3}, (\d{1,2} \w{3} \d{4})", block)
            return m.group(1) if m else ""
    return ""


def meldung(stufe: str, alt: str, neu: str, datum: str) -> str:
    name = _ANZEIGE.get(stufe, stufe)
    return (f"🔄 Neues Modell übernommen: {name} läuft ab der nächsten Sitzung "
            f"auf {neu} (bisher {alt})."
            + (f" Laut Anthropic seit {datum} verfügbar." if datum else "")
            + "\n\nDeine nächste Nachricht an diese Stufe ist die Probe: Läuft "
            "die neue Kennung im Abo nicht, gehe ich von selbst zurück und sage "
            "es dir. Soll es gleich die alte bleiben, genügt der Knopf.")


def lauf(trocken: bool = False, text: "str | None" = None) -> "tuple[int, str]":
    try:
        text = abrufen() if text is None else text
    except Exception as e:
        return 3, f"FEHLER Abruf der Release-Notes: {type(e).__name__}: {e}"[:300]
    if not modellwahl.kennungen_im_text(text):
        # Eine Seite ohne jede Kennung ist kein „nichts Neues", sondern ein
        # geändertes Format — und das soll auffallen.
        return 3, "FEHLER Release-Notes ohne eine einzige Modellkennung — Format geändert?"
    neu = modellwahl.neuere(text)
    if not neu:
        stand = ", ".join(f"{s} {modellwahl.kennung(s)}" for s in modellwahl.FAMILIEN)
        return 0, f"UNVERAENDERT {stand}"
    zeilen = []
    for stufe, alt, kennung in neu:
        if trocken:
            zeilen.append(f"{stufe} {alt} -> {kennung} (trocken, nicht geschrieben)")
            continue
        modellwahl.umstellen(stufe, kennung)
        try:
            import botenpost
            botenpost.legen(meldung(stufe, alt, kennung, seit_wann(text, kennung)),
                            "waechter",
                            knopf={"art": "modell_zurueck", "kennung": stufe,
                                   "beschriftung": f"↩️ Zurück auf {alt}"[:60]})
        except Exception as e:
            # Umgestellt ist umgestellt — die Zeile an den Tagescheck sagt es
            # trotzdem, und der geht auf einem eigenen Weg an Adam.
            zeilen.append(f"{stufe} {alt} -> {kennung} (Botenpost scheiterte: {e})")
            continue
        zeilen.append(f"{stufe} {alt} -> {kennung}")
    return 0, "UMGESTELLT " + " · ".join(zeilen)


def main() -> int:
    rc, zeile = lauf(trocken="--trocken" in sys.argv)
    print(zeile)
    return rc


if __name__ == "__main__":
    sys.exit(main())
