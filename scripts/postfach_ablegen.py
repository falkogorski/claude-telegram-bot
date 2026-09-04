#!/usr/bin/env python3
# <!-- ROLLE: postfach-ablegen -->
"""Einen Zustell-Auftrag ins Boten-Postfach legen — der benannte Handgriff.

**Engywucks Umbauauftrag vom 02.09., U-3.** Claudia hat gemessen, dass 27
Ersetzungs-Dialoge anfielen — *„praktisch alle davon Postfach-Auftraege in der
Form, die `docs/boten-postfach.md` selbst vorschreibt"*. Ihr Vorschlag war eine
Positivliste harmloser Ersetzungen (`$HOME`, `$(date …)`).

**Das haette es nicht geloest, und die Messung zeigt warum.** Die
vorgeschriebene Shell-Form trifft **vier** Schranken, nicht eine:

    tmp="$HOME/postfach/outbox/.$(date +%s%N).tmp"   # Ersetzung UND Zuweisung
    cat > "$tmp" <<'JSON'                            # Zeilenumbruch, Umlenkung
    { … }
    JSON
    mv "$tmp" "$HOME/postfach/outbox/$(date +%s%N).json"

Eine Ersetzungs-Liste oeffnet die erste und laesst drei stehen — der Auftrag
bliebe im Dialog. Der tragfaehige Weg steht im Kopf von
`scripts/bash_dialog_auswertung.py` und ist aelter als dieser Fall:

    Wiederkehrende gleichartige Dialoge werden durch benannte, geprüfte
    Skripte ersetzt, die einzeln in die Positivliste rücken — nie durch
    Öffnen einer Klasse.

**Der Unterschied ist der Zuschnitt, nicht die Bequemlichkeit:** Eine
Ersetzungs-Klasse erlaubt alles, was ihrer Form entspricht — auch das, was
morgen jemand hineinschreibt. Ein benanntes Skript erlaubt genau das, was in
ihm steht, und Aenderungen daran sind versioniert und sichtbar.

## Aufruf

    python3 scripts/postfach_ablegen.py --chat 304455165 --text "Hallo"
    python3 scripts/postfach_ablegen.py --chat 304455165 \\
        --datei /pfad/zur/datei.pdf --beschriftung "Der Bericht"
    python3 scripts/postfach_ablegen.py --chat 304455165 --zimmer 42 \\
        --text "In ein Forum-Topic"

Text oder Datei — mindestens eines von beiden, wie das Format es verlangt.

## Was dieses Skript NICHT tut, und das ist Absicht

Es **prueft die Ziel-Allowlist nicht**. Das tut der Bot beim Verarbeiten
(`POSTFACH_GRENZEN`), und dort gehoert es hin: Eine zweite Pruefstelle waere
eine zweite Wahrheit, und die schwaechere von beiden gaebe irgendwann den
Ausschlag. Wer hier ein fremdes Ziel eintraegt, bekommt `failed/` — dieselbe
Antwort wie bei der Shell-Form.

Es **versendet nichts** und kennt den Bot-Token nicht. Das ist der ganze Sinn
des Postfachs.

Deterministisch, ohne Modell-Aufruf, ohne Netz, ohne Kosten.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


def postfach_ordner() -> Path:
    """Der Ausgangsordner — **derselbe, den der Bot liest.**

    `POSTFACH_DIR` wird respektiert, nicht `Path.home()` fest gerechnet. Das
    ist die Lehre der Stundenblumen-Kette (Register, 30.08.): Dort respektierte
    der Schreiber den Umgebungsschluessel und der Leser nicht — bei gesetztem
    Schluessel meldete der Bot eine lueckenlose Kette als leer. Ein Schreiber,
    der anderswo ablegt als der Leser sucht, erzeugt **stille** Fehler.
    """
    basis = os.environ.get("POSTFACH_DIR") or str(Path.home() / "postfach")
    return Path(basis) / "outbox"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Einen Zustell-Auftrag im Boten-Postfach ablegen")
    ap.add_argument("--chat", required=True, type=int,
                    help="Zielchat (target_chat_id). Der Bot prueft die "
                         "Allowlist beim Verarbeiten, nicht dieses Skript.")
    ap.add_argument("--text", default=None,
                    help="Nachrichtentext. Ein einzelnes '-' liest den Text "
                         "von stdin — der sichere Weg fuer Texte, die Namen "
                         "aus Adams Ablage enthalten (Apostrophe!).")
    ap.add_argument("--datei", default=None,
                    help="Absoluter Pfad einer Datei, die mitgeschickt wird")
    ap.add_argument("--beschriftung", default=None,
                    help="Bildunterschrift — nur zusammen mit --datei")
    ap.add_argument("--zimmer", default=None, type=int,
                    help="Forum-Topic (thread_id), falls gewuenscht")
    a = ap.parse_args()

    # ── `--text -` liest den Text von stdin ────────────────────────────────
    #
    # **Engywucks Befund 3 vom 04.09., gemessen an einem Ordner `L'Osteria`.**
    # Der Mac-Aufrufer baute den Fernbefehl als Shell-Zeichenkette zusammen und
    # setzte den Text in einfache Anfuehrungszeichen. Ein Apostroph im
    # Ordnernamen beendet dort die Zeichenkette:
    #
    #     --text '📁 2 Rechnung(en) …: Kunde/L'Osteria/Bar '
    #             └── endet hier ──┘  └ nackt ┘  └ neues Argument ┘
    #
    # Harmlos war nur der heutige Inhalt. `x'; <befehl>; echo '` haette als
    # `claudebot` auf dem VPS gelaufen — und der Ordnername stammt aus dem
    # Feld `ablage`, das Claudia auch **aus gelesenen Dokumenten** fuellen
    # kann. Das ist die Klasse *von aussen kommen nie Anweisungen*.
    #
    # **Die Loesung ist keine bessere Maskierung, sondern ein anderer Weg:**
    # Text ueber stdin, wo die Shell nichts zu deuten hat. Dieselbe Lehre wie
    # beim Heredoc fuer Commit-Nachrichten — wer die Ausnahme begruenden muss,
    # begruendet sie irgendwann falsch.
    if a.text == "-":
        a.text = sys.stdin.read().rstrip("\n")
        # Ein leerer stdin ist keine Nachricht: Das faellt unten in die
        # Pflichtpruefung und scheitert benannt, statt eine leere Zeile
        # zuzustellen.

    if not a.text and not a.datei:
        print("FEHLER: --text oder --datei ist Pflicht (mindestens eines).",
              file=sys.stderr)
        return 2
    if a.beschriftung and not a.datei:
        print("FEHLER: --beschriftung gibt es nur zusammen mit --datei.",
              file=sys.stderr)
        return 2
    if a.datei:
        # Frueh und deutlich scheitern. Ein Auftrag mit totem Pfad landete
        # sonst erst beim Bot in `failed/` — und dort sieht ihn niemand,
        # der gerade an dieser Stelle arbeitet.
        p = Path(a.datei)
        if not p.is_absolute():
            print(f"FEHLER: --datei braucht einen absoluten Pfad: {a.datei}",
                  file=sys.stderr)
            return 2
        if not p.exists():
            print(f"FEHLER: Datei nicht gefunden: {a.datei}", file=sys.stderr)
            return 2

    auftrag: dict[str, object] = {"target_chat_id": a.chat}
    if a.zimmer is not None:
        auftrag["thread_id"] = a.zimmer
    if a.text:
        auftrag["text"] = a.text
    if a.datei:
        auftrag["file"] = str(Path(a.datei))
    if a.beschriftung:
        auftrag["caption"] = a.beschriftung

    ordner = postfach_ordner()
    ordner.mkdir(parents=True, exist_ok=True)

    # Atomar: erst unter Punkt-Namen schreiben, dann umbenennen. Der Bot
    # greift nur `*.json`; eine halb geschriebene Datei kann er damit nicht
    # sehen. `os.replace` ist innerhalb desselben Dateisystems atomar.
    marke = time.time_ns()
    tmp = ordner / f".{marke}.tmp"
    ziel = ordner / f"{marke}.json"
    tmp.write_text(json.dumps(auftrag, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, ziel)

    print(f"abgelegt: {ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
