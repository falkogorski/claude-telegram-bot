#!/usr/bin/env python3
# <!-- ROLLE: test-hermetik -->
"""Der Prüfstand des Differenzmessers — **eine Quelle, nicht zwei.**

**Warum diese Datei so dünn geworden ist** (23.08., Engywucks
Differenzmesser-Auftrag): Sie trug ihre Mengenbildung bis heute Mittag selbst.
Das war die Vorwegnahme von Differenzart B, aber mit dem Fehler, gegen den der
Auftrag ausdrücklich warnt: **Die Ist-Menge wurde über die Endung gebildet**
(`_DIR`, `_FILE`) — eine Aufzählung mit Regex-Anstrich.

Gemessen, was sie damit verfehlte: `AMPEL_RULES_PATH`, `AMPEL_CUSTOM_PATH`,
`AMPEL_STATE_PATH`, `AMPEL_LOG_PATH` und `PRESEND_LOG_PATH`. **Ausgerechnet die
Ampel**, die laut `CLAUDE.md` das Heikelste im Projekt führt — Klienten-Namen,
ausdrücklich cloud-frei zu pflegen. Ein Prüflauf hätte ihre Regeldatei
überschreiben können, und der Prüfer, der genau das verhindern sollte, hätte
geschwiegen.

Die Logik liegt jetzt in `scripts/differenz.py`. Zwei Stellen für dieselbe
Frage sind eine Stelle zu viel — und die zweite driftet.

**Was hier bleibt:** das Fahren der Arten und ihrer Gegenproben. Der Prüfstand
belegt damit auch, dass die **Ladebedingung** wirkt: Eine Differenzart ohne
Gegenprobe wird gar nicht erst geladen.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import differenz  # noqa: E402


def main() -> int:
    print("Differenzmesser — Hermetik und Bezugs-Integrität")
    print("=" * 48)

    # ① Die Ladebedingung: jede Art hat eine Gegenprobe, sonst wirft `arten()`.
    try:
        arten = differenz.arten()
    except RuntimeError as e:
        print(f"✗ Ladebedingung verletzt: {e}")
        return 1
    print(f"✓ {len(arten)} Differenzart(en) geladen, jede mit Gegenprobe")

    # ② Jede Gegenprobe fahren — sie erzeugt die Lücke künstlich und muss sie
    #    finden. Das ist der Beleg, dass eine Art überhaupt etwas messen KANN;
    #    eine Art, die nie etwas meldet, sieht sonst aus wie eine, die passt.
    try:
        differenz.gegenproben_fahren()
    except AssertionError as e:
        print(f"✗ eine Gegenprobe schlug fehl: {e}")
        return 1
    print("✓ alle Gegenproben bestanden — jede Art findet ihre Lücke")

    # ③ Der eigentliche Lauf.
    befunde = differenz.messen()
    if not befunde:
        for name, _fn in arten:
            print(f"  ○ {name}: keine Differenz")
        print("== Hermetik: bestanden ==")
        return 0

    schlimm = False
    for b in befunde:
        zeichen = "✗" if b.haerte == differenz.BRICHT else "⚠"
        schlimm = schlimm or b.haerte == differenz.BRICHT
        print(f"{zeichen} {b.was}: {', '.join(sorted(b.fehlend))}")
        if b.hinweis:
            print(f"   {b.hinweis}")
    return 1 if schlimm else 0


if __name__ == "__main__":
    sys.exit(main())
