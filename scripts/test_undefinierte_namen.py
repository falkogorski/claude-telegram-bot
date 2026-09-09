#!/usr/bin/env python3
# <!-- ROLLE: test-undefinierte-namen -->
"""Kein undefinierter Name in unseren Modulen — **die ganze Klasse auf einmal.**

**Anlass, und es ist der zweite Fall in drei Wochen:** Am 09.09. kam ein
`datetime.now()` in `can_use_tool` hinzu, ohne Import. Ergebnis: `NameError`
bei **jedem** gezeigten Dialog, gefangen von der Klammer, die das Senden
absichert — Adam drückte „Genehmigen", und das Werkzeug war trotzdem
verweigert. Fünfeinhalb Stunden lang, unbemerkt. Der erste Fall war am 18.08.
im Sendepfad.

**Warum kein Verhaltensprüfer das erledigt:** Beide Male lag der Fehler in
einem Pfad, den der Regressionslauf nicht ausführt, und beide Male hat ein
`try/except` den Fehler in Ruhe verwandelt. Ein ausführender Prüfer je Pfad
wäre richtig — aber es gibt zu viele Pfade. `pyflakes` misst die **Klasse**
in unter einer Sekunde und hätte beide gefunden, bevor sie committet waren.

**Nur `undefined name` ist rot.** Ungenutzte Importe und Ähnliches gibt es
heute sieben; sie mit anzuschlagen hieße, den Prüfer binnen einer Woche
abzuschalten — und dann fängt er auch den nächsten NameError nicht.

**Fehlt `pyflakes`, wird übersprungen (77), nicht bestanden.** Ein Prüfer, der
ohne sein Werkzeug grün meldet, ist die schlimmere Form von blind.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE = sorted(p.name for p in ROOT.glob("*.py"))

try:
    import pyflakes  # noqa: F401
except ImportError:
    print("⏭️  pyflakes ist hier nicht installiert — NICHT GEMESSEN.")
    print("    Einspielen mit: .venv/bin/pip install pyflakes")
    sys.exit(77)

lauf = subprocess.run(
    [sys.executable, "-m", "pyflakes", *MODULE],
    cwd=ROOT, capture_output=True, text=True)
zeilen = [z for z in (lauf.stdout + lauf.stderr).splitlines() if z.strip()]
undefiniert = [z for z in zeilen if "undefined name" in z]

print(f"pyflakes über {len(MODULE)} Module: {len(zeilen)} Meldungen, "
      f"davon {len(undefiniert)} undefinierte Namen.")
if undefiniert:
    print()
    for z in undefiniert:
        print(f"  ❌ {z}")
    print()
    print("Ein undefinierter Name in einem abgesicherten Pfad sieht im Betrieb")
    print("wie eine Verweigerung aus, nicht wie ein Fehler. Beheben, nicht filtern.")
    sys.exit(1)

print("✅ kein undefinierter Name")
