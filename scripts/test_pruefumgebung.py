#!/usr/bin/env python3
# <!-- ROLLE: test-pruefumgebung -->
"""Der Prüfsatz über die Prüfungen selbst.

**Warum es ihn gibt (Vorfall 26.07., 01:44):** Adam bekam nachts eine Meldung
über ein „Update von demo". Es gab kein Update und kein „demo" — ein Testfall
hatte den Start-Wächter als **abgekoppelten Prozess** gestartet, der das
Testende überlebte, seine Nachfrist abwartete und danach in Adams **echtes**
Boten-Postfach schrieb.

**Die drei Riegel, und warum es drei sein müssen:**

1. Der Läufer setzt für den ganzen Lauf eine Wegwerf-Umgebung. — Das hilft nur,
   solange **über ihn** gestartet wird.
2. Der Test ersetzt, was einen dauerhaften Prozess startet. — Das hilft nur für
   **diesen** Test.
3. **Dieser Prüfsatz.** Er fängt den nächsten Test, der es wieder tut, und ist
   damit der einzige der drei, der auch für das gilt, was noch niemand
   geschrieben hat.

Eine Regel ohne Prüfer ist eine Bitte. Ein Riegel an einer Stelle ist eine
Momentaufnahme.
"""
import ast
import os
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _testdateien() -> list[Path]:
    return sorted(p for p in HIER.glob("test_*.py") if p.name != Path(__file__).name)


# Module, deren Aufruf einen Prozess erzeugt, der die eigene Laufzeit überleben
# kann. Wer eines davon in einem Test benutzt, muss es ausdrücklich ersetzen.
_UEBERLEBT = {
    "_waechter_scharf": "startet den Start-Wächter abgekoppelt",
    "Popen": "startet einen Prozess, der nicht mitstirbt",
    "start_new_session": "koppelt einen Prozess ausdrücklich ab",
}


def _kein_test_startet_einen_ueberlebenden_prozess():
    """Wer etwas startet, das weiterläuft, muss es ersetzen — nachweislich."""
    suender = []
    for p in _testdateien():
        text = p.read_text(encoding="utf-8")
        for name, warum in _UEBERLEBT.items():
            if name not in text:
                continue
            # Eine Ersetzung sieht so aus: `modul.name = …` oder `name = lambda`.
            ersetzt = any(
                isinstance(k, ast.Assign) and any(
                    (isinstance(z, ast.Attribute) and z.attr == name)
                    or (isinstance(z, ast.Name) and z.id == name)
                    for z in k.targets)
                for k in ast.walk(ast.parse(text)))
            if not ersetzt:
                suender.append(f"{p.name} benutzt {name} ({warum}) ohne Ersatz")
    assert not suender, (
        "Diese Prüfungen können Prozesse hinterlassen, die das Testende "
        "überleben und danach in ECHTE Ordner schreiben:\n  "
        + "\n  ".join(suender))


def _jede_pruefung_haelt_ihre_umgebung_fest():
    """Wer schreibende Ordner benutzt, setzt sie selbst — und zwar hart.

    `setdefault` genügt nicht: Es übernimmt genau dann den Wert des Aufrufers,
    wenn dieser gesetzt ist — also im schlimmsten Fall den echten. Das ist
    dieselbe Klasse wie der geerbte `ALLOWED_USER_IDS`, der den 12/14-Fehlalarm
    erzeugt hat.
    """
    schreibend = {"POSTFACH_DIR": "postfach", "FREIGABE_DIR": "freigab",
                  "BLUMEN_DIR": "blumen", "HORA_DIR": "hora"}
    suender = []
    for p in _testdateien():
        text = p.read_text(encoding="utf-8")
        for name, spur in schreibend.items():
            benutzt = spur in text.lower() or name in text
            if not benutzt:
                continue
            if f'os.environ["{name}"]' in text:
                continue                       # hart gesetzt — richtig
            if f'os.environ.setdefault("{name}"' in text:
                suender.append(f"{p.name} setzt {name} nur per setdefault — "
                               "das erbt im Zweifel den echten Ordner")
    assert not suender, "\n  ".join([""] + suender)


def _der_laeufer_raeumt_eine_wegwerf_umgebung_ein():
    """Der dritte Riegel prüft auch den ersten — sonst verlässt sich jeder auf
    jeden."""
    laeufer = (HIER / "regressionstest.sh").read_text(encoding="utf-8")
    for name in ("POSTFACH_DIR", "FREIGABE_DIR", "HORA_DIR", "BLUMEN_DIR"):
        assert f"export {name}=" in laeufer, \
            f"der Regressionslauf setzt {name} nicht auf einen Wegwerf-Ordner"
    assert "mktemp -d" in laeufer, "der Wegwerf-Ordner ist gar keiner"
    assert "POST_VORHER" in laeufer, \
        "es wird nicht nachgemessen, ob doch ins echte Postfach geschrieben wurde"


check("kein Test startet einen überlebenden Prozess ohne Ersatz",
      _kein_test_startet_einen_ueberlebenden_prozess)
check("jede Prüfung setzt ihre schreibenden Ordner hart",
      _jede_pruefung_haelt_ihre_umgebung_fest)
check("der Läufer räumt eine Wegwerf-Umgebung ein",
      _der_laeufer_raeumt_eine_wegwerf_umgebung_ein)


def _jede_postfach_nachricht_nennt_ihren_absender():
    """Leitplanke 7 gilt jetzt auch fuer das Boten-Postfach.

    **Der Anlass:** Am 26.07. um 01:44 erreichte Adam eine anonyme Meldung. Die
    Suche nach ihrem Urheber kostete ueber eine Stunde — weder Dateiname noch
    Inhalt nannten ihn. Die Nachricht haette es selbst sagen koennen.
    """
    import importlib
    sys.path.insert(0, str(HIER.parent))
    bp = importlib.import_module("botenpost")

    # Kein Schreiber legt mehr selbst ab — sonst vergisst der naechste den Absender.
    for name in ("hora.py", "stundenblume.py", "wartungsfenster.py",
                 "start_waechter.py"):
        text = (HIER / name).read_text(encoding="utf-8")
        assert "botenpost.legen(" in text, f"{name} nutzt die Botenpost nicht"
        assert 'json.dumps({"target_chat_id"' not in text, \
            f"{name} legt WIEDER selbst ab — der Absender geht dabei verloren"

    # Der Absender steht im Dateinamen UND im Inhalt.
    import tempfile, json as _j
    tmp = Path(tempfile.mkdtemp(prefix="bp-"))
    bp.POSTFACH = tmp / "outbox"
    p = bp.legen("Probe", "probe", ziel="304455165")
    assert p is not None and p.name.startswith("probe-"), \
        f"der Absender fehlt im Dateinamen: {p}"
    assert _j.loads(p.read_text(encoding="utf-8"))["herkunft"] == "probe"

    # Ein erfundener Absender kommt nicht durch.
    try:
        bp.legen("x", "irgendwer", ziel="304455165")
        raise AssertionError("ein unbekannter Absender wurde angenommen")
    except bp.Abgewiesen:
        pass

    # Und der Bot schreibt die Herkunft beim Zustellen ins Protokoll.
    botquelle = (HIER.parent / "bot.py").read_text(encoding="utf-8")
    assert "Absender: %s" in botquelle, \
        "der Bot protokolliert die Herkunft nicht beim Zustellen"


check("jede Postfach-Nachricht nennt ihren Absender",
      _jede_postfach_nachricht_nennt_ihren_absender)

print()
if fails:
    print(f"❌ {len(fails)} Prüfung(en) über die Prüfumgebung fehlgeschlagen.")
    sys.exit(1)
print("Prüfumgebung ist dicht.")
