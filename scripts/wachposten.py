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
        ende = fh.tell()
    # **W4: nur bis zum letzten Zeilenumbruch** (Engywuck 19.08.). Wird eine
    # Zeile gerade geschrieben, läse der Posten sie halb — und ein zerrissener
    # Fehler trifft womöglich kein Muster. Der Rest wartet auf den nächsten
    # Lauf, fünf Minuten später; das ist billiger als eine verlorene Hälfte.
    schnitt = text.rfind("\n")
    if schnitt < 0:
        return ([], alt)                   # noch keine vollständige Zeile
    vollstaendig = text[:schnitt + 1]
    neu = alt + len(vollstaendig.encode("utf-8"))
    return ([z for z in vollstaendig.splitlines() if z.strip()], neu)


def _daempf_schluessel(kennung: str, zeile: str) -> str:
    """Woran der Dämpfer eine Wiederholung erkennt.

    **W1, gemessen von Engywuck am 19.08. und hier nachgestellt:** Der erste
    Entwurf dämpfte allein über die Kennung. In einer Fehlerdatei tragen aber
    **alle** Zeilen dieselbe (`fehlerdatei`) — drei verschiedene neue Fehler
    ergaben genau **eine** Meldung, und für die folgende Stunde verschwand
    jeder weitere endgültig, weil die Offsets fortgeschrieben waren. Ein
    Fehlersturm sah aus wie ein Einzelfall, und das widersprach dem eigenen
    Satz „in einer Fehlerdatei ist jede neue Zeile bereits der Befund".

    Der Schlüssel trägt deshalb einen **stabilen Hash der Zeile** — kein Text,
    keine Zeitangabe. Damit bleibt die 28.07.-Lehre gewahrt: Gedämpft wird
    nicht über den Wortlaut (ein Zeitstempel darin hebelte damals den Dämpfer
    aus), sondern über eine Kennung, die sich bei gleicher Zeile nicht ändert.
    """
    import hashlib
    if kennung != "fehlerdatei":
        return kennung
    kurz = hashlib.sha256((zeile or "").encode("utf-8")).hexdigest()[:12]
    return f"{kennung}:{kurz}"


def _daempfen(befunde: list[tuple[str, str, str]], stand: dict
              ) -> list[tuple[str, str, str]]:
    """Dieselbe Meldung frühestens nach WIEDERVORLAGE_S erneut.

    **Der Dämpfer wirkt ZWISCHEN Läufen, nicht innerhalb** (W1). Was ein Lauf
    an verschiedenen Befunden findet, gehört in dieselbe Meldung — dafür gibt
    es `MAX_ZEILEN` und die „(und N weitere)"-Zeile. Vorher konnte die nie
    feuern, weil gleiche Kennungen schon vorher weggedämpft wurden.
    """
    jetzt = time.time()
    bekannt = stand.setdefault("_gemeldet", {})
    raus, in_diesem_lauf = [], set()
    for kennung, anzeige, zeile in befunde:
        schluessel = _daempf_schluessel(kennung, zeile)
        if schluessel in in_diesem_lauf:
            continue                       # exakt dieselbe Zeile zweimal
        if jetzt - float(bekannt.get(schluessel, 0)) < WIEDERVORLAGE_S:
            continue
        in_diesem_lauf.add(schluessel)
        bekannt[schluessel] = jetzt
        raus.append((kennung, anzeige, zeile))
    # Der Merkzettel darf nicht unbegrenzt wachsen — Hashes altern.
    if len(bekannt) > 500:
        alt_genug = [k for k, v in bekannt.items()
                     if jetzt - float(v) > WIEDERVORLAGE_S * 4]
        for k in alt_genug:
            bekannt.pop(k, None)
    return raus


def _melde_zeile(anzeige: str, zeile: str, quelle: str, classify,
                 nr: int | None = None) -> str:
    """Eine Meldezeile — bei Rot ohne Wortlaut.

    **Engywucks Auflagen:** nur Rot zurückhalten · Einstufungs-Ausfall zählt
    als Rot · bei Rot nur das Kategorien-Label, **nie das Muster**.
    `classify()` liefert `{color, rules, matches}` — `matches` enthält die
    Treffer selbst und darf diese Meldung nie berühren, sonst zitierte sie
    genau das rote Wort, das sie zurückhält.
    """
    farbe, labels, ampel_weg = "rot", [], False
    if classify is None:
        ampel_weg = True
    else:
        try:
            urteil = classify(zeile)
            farbe = urteil.get("color", "rot")
            labels = list(urteil.get("rules", []))
        except Exception:
            farbe, labels, ampel_weg = "rot", [], True   # Ausfall zählt als Rot

    # **W3 (Engywuck 19.08.): Die Fundstelle ist bei zurückgehaltenem Wortlaut
    # das Einzige, was Adam hat.** Die Doku versprach „Quelle, Zeit und Label";
    # die Meldung nannte nur den Dateinamen. Eine Beschreibung, die mehr
    # verspricht als der Bau — dieselbe Klasse, die dieser Posten aufdecken soll.
    stelle = f"{quelle}, Zeile {nr}" if nr else quelle
    stelle += f", gesehen {time.strftime('%H:%M')}"

    if farbe == "rot":
        if ampel_weg:
            # **W5: Der Ausfall wird BENANNT.** Sonst sähe Adam lauter rote
            # Meldungen ohne den Grund und hielte den Inhalt für heikel, wo in
            # Wahrheit nur die Ampel fehlt.
            etikett = "Ampel nicht ladbar — im Zweifel zurückgehalten"
        else:
            etikett = ("Ampel rot: " + ", ".join(labels)) if labels \
                else "Ampel rot, ohne nähere Angabe"
        return (f"🔴 {anzeige} in {stelle}\n"
                f"   Wortlaut zurückgehalten ({etikett}) — "
                f"der Text bleibt im Log, die Fundstelle steht hier.")
    gekuerzt = zeile if len(zeile) <= 240 else zeile[:239] + "…"
    return f"• {anzeige} in {stelle}\n   {gekuerzt}"


def lauf(trocken: bool = False) -> int:
    stand = _stand_laden()
    beschaedigt = stand.pop("_beschaedigt", False)
    classify = _ampel()
    befunde: list[tuple[str, str, str]] = []
    quellen_namen: dict[str, str] = {}
    zeilen_nr: dict[str, int] = {}

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
        # Die Nummer zählt ab dem gemerkten Stand — sie sagt „die soundsovielte
        # neue Zeile", nicht die absolute Position. Das genügt zum Wiederfinden
        # und kostet kein erneutes Lesen der ganzen Datei.
        for i, zeile in enumerate(zeilen, start=1):
            for kennung, anzeige in wachmuster.treffer(zeile, datei.name):
                befunde.append((kennung, anzeige, zeile))
                quellen_namen[zeile] = datei.name
                zeilen_nr[zeile] = i
        stand[datei.name] = neuer_offset

    if beschaedigt:
        befunde.insert(0, ("stand-beschaedigt",
                           "Mein Merkzettel war unlesbar — ich habe von vorn "
                           "gelesen und melde das, statt still stehenzubleiben",
                           ""))

    zu_melden = _daempfen(befunde, stand)

    # **W2 (Engywuck 19.08.): Der Befund darf nicht verbraucht sein, bevor die
    # Meldung sicher ist.** Vorher stand hier `_stand_schreiben` VOR der
    # Zustellung: Schlug das Legen fehl, waren Offset und Dämpfer schon
    # fortgeschrieben, und die Warnung landete als `print` im Journal — die
    # A2-Klasse, eine Zeile im Log, die niemand liest.
    #
    # Jetzt wird der Stand erst geschrieben, wenn zugestellt ist. Misslingt es,
    # bleibt alles stehen und der nächste Lauf findet dieselben Zeilen erneut.
    # Lieber eine Meldung doppelt als eine verloren.
    if not zu_melden:
        if not trocken:
            _stand_schreiben(stand)
        return 0

    rest = len(zu_melden) - MAX_ZEILEN
    zeilen = [_melde_zeile(a, z, quellen_namen.get(z, "—"), classify,
                          zeilen_nr.get(z))
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
        # NICHT den Stand schreiben: Der nächste Lauf soll dieselben Zeilen
        # wiederfinden und es erneut versuchen.
        print(f"WARNUNG: Befund gefunden, Meldung fehlgeschlagen "
              f"({type(e).__name__}) — Stand NICHT fortgeschrieben, "
              f"der naechste Lauf versucht es erneut")
        return len(zu_melden)
    _stand_schreiben(stand)
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
