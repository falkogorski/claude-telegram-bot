#!/usr/bin/env python3
# <!-- ROLLE: log-wachposten -->
"""Der Log-Wachposten — meldet Auffälliges, ohne dass jemand fragen muss.

**Wofür** (Engywucks Bauauftrag, Adams Daumen 18.08.): Adam wünscht eine
Instanz, die **unaufgefordert** warnt. Vollautonomes Modell-Wachen ist
AGB-Grauzone — deshalb ein **deterministischer** Posten: Er liest neue
Log-Zeilen, prüft sie gegen `wachmuster.py` und legt Auffälliges ins
Boten-Postfach. **Kein Anthropic-Aufruf im Pfad, Kosten null.**

Adams Fingertipp weckt dann Engywuck. Der Posten urteilt nicht — er zeigt.

## Zwei Dinge, die er bewusst NICHT tut

**Er liest Adams Gespräche nur auf ausdrücklichen Schalter** (`WACHPOSTEN_
GESPRAECHE=ja`, Vorgabe **aus**). Die Fehlerdatei ist der eigentliche Zweck;
die Gesprächsprotokolle bringen vor allem die Kategorien „Freigabe offen" und
„Kosten" — und sie sind das, was Adam privat schreibt. Der Schalter ist seine
Entscheidung, nicht meine.

**Er zitiert bei ROT keinen Wortlaut.** Die Ampel entscheidet; bei Rot gehen
nur Quelle, Zeit und das Kategorien-Label hinaus, nie das gefundene Muster.
Sichtbar zurückgehalten ist ehrlich und sicher — lautlos wäre es die nächste
Stille, die wie Ruhe aussieht.

Aufruf: ``python3 scripts/wachposten.py [--trocken]``
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import botenpost  # noqa: E402
import wachmuster  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LOGDIR = Path(os.environ.get("WACHPOSTEN_LOGDIR") or (REPO / "logs"))
ZUSTAND = Path(os.environ.get("WACHPOSTEN_DIR")
               or (Path.home() / ".claude" / "wachposten"))
MARKE = ZUSTAND / "stand.json"

# Vorgabe AUS — Adams Entscheidung, nicht meine (siehe Kopf).
GESPRAECHE_LESEN = os.environ.get("WACHPOSTEN_GESPRAECHE") == "ja"

# Dämpfer wie bei den Stundenblumen: dieselbe Kennung frühestens nach einer
# Stunde erneut. Ohne ihn meldete ein stehender Fehler alle fünf Minuten —
# zwölfmal je Stunde, und wer diesen Absender überliest, überliest auch den
# einen, der zählt.
WIEDERVORLAGE_S = int(os.environ.get("WACHPOSTEN_WIEDERVORLAGE") or 3600)

# Kein Roman je Lauf. Mehr als das liest niemand, und die ersten sagen das
# Meiste — dieselbe Grenze wie bei Horas Fehlgrund.
MAX_ZEILEN = 5


def _ampel():
    """Die Ampel als Filter — **keine Zweitliste** (Engywucks Auflage, G1).

    Fällt sie aus, gilt ROT: Wer im Zweifel öffnet, sichert nichts.
    """
    try:
        sys.path.insert(0, str(REPO))
        import ampel
        return ampel.classify
    except Exception:
        return None


def _stand_laden() -> dict:
    try:
        return json.loads(MARKE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except Exception:
        # **Unlesbarer Zustand = von vorn lesen UND melden** (Lehre
        # Versions-Monitor, 18.08.): Dort legte ein kaputter Zeitstempel einen
        # Eintrag dauerhaft still, während das Protokoll „vor 0 Tagen gesehen"
        # meldete. Stillstehen ist hier die schlechteste aller Antworten.
        return {"_beschaedigt": True}


def _stand_schreiben(stand: dict) -> None:
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        tmp = MARKE.with_suffix(".tmp")
        tmp.write_text(json.dumps(stand, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.replace(MARKE)
    except Exception as e:
        print(f"WARNUNG: Stand nicht gesichert ({type(e).__name__})")


def _quellen() -> list[Path]:
    """Die Fehlerdatei immer, die Gespräche nur auf Schalter."""
    raus = []
    fehler = LOGDIR / "bot-errors.log"
    if fehler.exists():
        raus.append(fehler)
    if GESPRAECHE_LESEN:
        heute = LOGDIR / "conversations" / f"{time.strftime('%Y-%m-%d')}.md"
        if heute.exists():
            raus.append(heute)
    return raus


def _neue_zeilen(datei: Path, stand: dict) -> tuple[list[str], int]:
    """Zeilen ab dem gemerkten Offset. Schrumpft die Datei (Rotation), wird
    von vorn gelesen — sonst übersprängen wir alles bis zur alten Marke."""
    schluessel = datei.name
    alt = int(stand.get(schluessel, 0))
    groesse = datei.stat().st_size
    if groesse < alt:
        alt = 0
    with datei.open("r", encoding="utf-8", errors="replace") as fh:
        fh.seek(alt)
        text = fh.read()
        neu = fh.tell()
    return ([z for z in text.splitlines() if z.strip()], neu)


def _daempfen(befunde: list[tuple[str, str, str]], stand: dict
              ) -> list[tuple[str, str, str]]:
    """Dieselbe Kennung frühestens nach WIEDERVORLAGE_S erneut.

    Gedämpft wird über die **Kennung**, nie über den Text: Am 28.07. hebelte
    ein Zeitstempel im Befundtext den Dämpfer aus — „seit 9 Min" gegen „seit
    10 Min" galt als neuer Befund UND als weggefallener, und der Dämpfer
    verdoppelte den Lärm, statt ihn zu dämpfen.
    """
    jetzt = time.time()
    bekannt = stand.setdefault("_gemeldet", {})
    raus = []
    for kennung, anzeige, zeile in befunde:
        if jetzt - float(bekannt.get(kennung, 0)) < WIEDERVORLAGE_S:
            continue
        bekannt[kennung] = jetzt
        raus.append((kennung, anzeige, zeile))
    return raus


def _melde_zeile(anzeige: str, zeile: str, quelle: str, classify) -> str:
    """Eine Meldezeile — bei Rot ohne Wortlaut.

    **Engywucks Auflagen:** nur Rot zurückhalten · Einstufungs-Ausfall zählt
    als Rot · bei Rot nur das Kategorien-Label, **nie das Muster**.
    `classify()` liefert `{color, rules, matches}` — `matches` enthält die
    Treffer selbst und darf diese Meldung nie berühren, sonst zitierte sie
    genau das rote Wort, das sie zurückhält.
    """
    farbe, labels = "rot", []
    if classify is not None:
        try:
            urteil = classify(zeile)
            farbe = urteil.get("color", "rot")
            labels = list(urteil.get("rules", []))
        except Exception:
            farbe, labels = "rot", []          # Ausfall zählt als Rot
    if farbe == "rot":
        etikett = ", ".join(labels) if labels else "ohne nähere Angabe"
        return (f"🔴 {anzeige} in {quelle}\n"
                f"   Wortlaut zurückgehalten (Ampel rot: {etikett}) — "
                f"die Fundstelle steht oben, der Text bleibt im Log.")
    gekuerzt = zeile if len(zeile) <= 240 else zeile[:239] + "…"
    return f"• {anzeige} in {quelle}\n   {gekuerzt}"


def lauf(trocken: bool = False) -> int:
    stand = _stand_laden()
    beschaedigt = stand.pop("_beschaedigt", False)
    classify = _ampel()
    befunde: list[tuple[str, str, str]] = []
    quellen_namen: dict[str, str] = {}

    for datei in _quellen():
        try:
            zeilen, neuer_offset = _neue_zeilen(datei, stand)
        except Exception as e:
            # **Eine Ausnahme ist ein Befund, kein Abbruch** (Lehre der 21
            # Prüfskripte): Bricht der Posten hier ab, bleiben die übrigen
            # Quellen ungelesen und ihre Befunde gehen still verloren.
            befunde.append(("lesefehler", f"Quelle nicht lesbar ({type(e).__name__})",
                            datei.name))
            continue
        for zeile in zeilen:
            for kennung, anzeige in wachmuster.treffer(zeile, datei.name):
                befunde.append((kennung, anzeige, zeile))
                quellen_namen[zeile] = datei.name
        stand[datei.name] = neuer_offset

    if beschaedigt:
        befunde.insert(0, ("stand-beschaedigt",
                           "Mein Merkzettel war unlesbar — ich habe von vorn "
                           "gelesen und melde das, statt still stehenzubleiben",
                           ""))

    zu_melden = _daempfen(befunde, stand)
    if not trocken:
        _stand_schreiben(stand)

    if not zu_melden:
        return 0

    rest = len(zu_melden) - MAX_ZEILEN
    zeilen = [_melde_zeile(a, z, quellen_namen.get(z, "—"), classify)
              for _, a, z in zu_melden[:MAX_ZEILEN]]
    text = ("👁️ Wachposten — Auffälliges in den Protokollen:\n\n"
            + "\n".join(zeilen))
    if rest > 0:
        text += f"\n\n(und {rest} weitere — im Log vollständig)"
    text += "\n\nEngywuck wecken?"

    if trocken:
        print(text)
        return len(zu_melden)
    try:
        botenpost.legen(text, absender="wachposten")
    except Exception as e:
        print(f"WARNUNG: Befund gefunden, Meldung fehlgeschlagen ({type(e).__name__})")
    return len(zu_melden)


def main() -> int:
    ap = argparse.ArgumentParser(description="Log-Wachposten")
    ap.add_argument("--trocken", action="store_true",
                    help="nur anzeigen, nichts ablegen und nichts merken")
    args = ap.parse_args()
    n = lauf(trocken=args.trocken)
    print(f"{n} Befund(e)." if n else "Nichts Auffälliges.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
