#!/usr/bin/env python3
# <!-- ROLLE: test-hermetik -->
"""Kein Prüflauf darf Betriebszustand anfassen — **die Lehre aus Befund L.**

**Was geschehen ist** (Engywuck, 23.08.): Zwölf Testdateien setzten
`USER_PREFS_FILE` und hielten sich für isoliert. `bot.py` hat die Variable
**nie gelesen** — der Pfad war fest auf `Path.home()` verdrahtet. Jeder
Regressionslauf beschrieb damit die echte `prefs.json`.

Auf dem VPS gemessen: `output_channel_id`, `summary_channel_id` und
`tts_channel_id` standen auf der Test-Attrappe `-1001234567890`, dazu eine
Dauerfreigabe für die Testkennung 4711. Der Bot hätte alle Ausgaben in einen
Kanal gelenkt, den es nicht gibt — **ohne Fehlermeldung**, weil ein unbekannter
Kanal nichts wirft, das jemandem auffällt. Ein Bruch, der wie Ruhe aussieht.

**Warum ein eigener Prüfer und nicht bloß fünf nachgetragene Zeilen:** Der
Regressionsläufer trägt seit dem 20.08. den Satz *„Wer eine neue Zustandsablage
einführt, trägt sie im selben Zug in die Wegwerf-Umgebung ein."* Der Satz stand
da — und die Liste war trotzdem an fünf Stellen unvollständig. Eine Regel ohne
Prüfer ist eine Bitte; das ist in diesem Projekt oft genug gemessen worden.

**Was er misst — und was bewusst nicht:** Er misst eine **Abwesenheit** (eine
Ablage, die im Läufer fehlt), und Abwesenheit lässt sich nicht ausführen. Das
ist der ausdrücklich erlaubte Fall der Regel vom 22.08.; die **Wirkung** — dass
die gesetzten Werte auch wirklich ankommen — misst `test_eingangsschranken.py`
in der Zeile „keine Betriebsablage wird angefasst", und zwar am Zustand der
geladenen Module. Beide zusammen decken den Befund: dieser hier die Lücke, der
andere die tote Variable.
"""
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
LAEUFER = WURZEL / "scripts" / "regressionstest.sh"

# Ablagen, die absichtlich NICHT umgebogen werden — mit dem Grund daneben.
# Jeder Eintrag hier ist eine Entscheidung, kein Automatismus: Eine lange
# Ausnahmeliste höhlt den Prüfer aus, genau wie bei den Stichwort-Filtern.
GEWOLLT_OFFEN = {
    # Der Läufer setzt es bewusst nur für EINEN Aufruf, nicht global: Ein Test
    # muss das echte Gedächtnis lesen können, ohne hineinzuschreiben.
    "CLAUDE_MEMORY_DIR": "wird gezielt pro Aufruf gesetzt, nicht global",
}

_MUSTER = re.compile(r'os\.environ\.get\(\s*["\']([A-Z][A-Z0-9_]*(?:_DIR|_FILE))["\']')


def eigene_module() -> list[Path]:
    """Nur unsere eigenen Module — keine Abhängigkeiten, kein Prüfstand."""
    return sorted(p for p in WURZEL.glob("*.py") if not p.name.startswith("test_"))


def main() -> int:
    laeufer = LAEUFER.read_text(encoding="utf-8")
    fehlt: dict[str, list[str]] = {}

    for datei in eigene_module():
        for name in _MUSTER.findall(datei.read_text(encoding="utf-8")):
            if name in GEWOLLT_OFFEN:
                continue
            if re.search(rf'^\s*export\s+{re.escape(name)}=', laeufer, re.M):
                continue
            fehlt.setdefault(name, []).append(datei.name)

    print("Hermetik der Prüfläufe")
    print("=" * 40)
    for name, grund in sorted(GEWOLLT_OFFEN.items()):
        print(f"○ {name} — bewusst offen: {grund}")

    if fehlt:
        print()
        for name, dateien in sorted(fehlt.items()):
            print(f"✗ {name} ({', '.join(dateien)}) wird im Regressionsläufer "
                  f"NICHT umgebogen — ein Lauf schreibt in den Betrieb")
        print()
        print(f"❌ {len(fehlt)} Ablage(n) ohne Riegel. Nachtragen in "
              f"scripts/regressionstest.sh, oder mit Begründung in "
              f"GEWOLLT_OFFEN aufnehmen.")
        return 1

    gezaehlt = sum(1 for d in eigene_module()
                   for _ in _MUSTER.findall(d.read_text(encoding="utf-8")))
    print()
    print(f"✓ alle {gezaehlt} umbiegbaren Ablagen sind im Läufer verriegelt")
    print("== Hermetik: bestanden ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
