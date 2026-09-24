#!/usr/bin/env python3
"""Block 3 Teil 2 — stille Neustarts und das Stundenblumen-Prüfmoment.

Claudias Auftrag 3 (19.09.): Ein Neustart schweigt, wenn der Selbstcheck grün
ist, nichts nachzuholen war und nichts in der Schlange steht — gleich aus
welchem Grund. Engywucks Ergänzungen (Nachtlese 19.09., Zettel 24.09.): ab dem
dritten stillen Neustart je Tag laut, gezählt im Tagescheck, Rücksetzung um
vier; und zwei Verhaltenszeilen für die Tagescheck-Stellen.

Ausführend, wo es geht: die Entscheidung und die Zählung als echte Funktionen,
die beiden Tagescheck-Abschnitte als echter Bash-Code aus dem Skript. Die
Verkabelung im Startpfad (eine große async-Funktion) über echte Aufrufknoten.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
TAGESCHECK = WURZEL / "scripts" / "daily_check.sh"

import neustarte  # noqa: E402

zeilen = 0
fehler: list[str] = []


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    print(("✅ " if bedingung else "❌ ") + name + ("" if bedingung else f"  [{gemessen}]"))
    if not bedingung:
        fehler.append(name)


print("== A. Wann schweigt ein Neustart? ==")
sauber = dict(adam_ausgeloest=False, nachzuholen=False, selbstcheck_rot=False, auftraege=False)
zeile("sauber: still, gleich aus welchem Grund", neustarte.still(**sauber))
for feld, name in (("adam_ausgeloest", "Adams eigener /restart bleibt laut"),
                   ("nachzuholen", "liegengebliebene Nachrichten: laut"),
                   ("selbstcheck_rot", "Selbstcheck rot: laut"),
                   ("auftraege", "ein folgender Lauf (Schlange): laut")):
    zeile(name, not neustarte.still(**{**sauber, feld: True}))

print("== B. Der hinterlegte Grund ==")
g = neustarte.grund_lesen("Kurz weg — Telegram-Verbindungs-Timeout. Bin wieder da.")
zeile("Timeout: nicht planmäßig, nicht Adam, Grund bleibt erhalten",
      not g["planmaessig"] and not g["adam_ausgeloest"] and "Timeout" in g["grund"],
      gemessen=str(g))
g = neustarte.grund_lesen("[LAUT]Bin wieder da. Zuletzt erledigt: x")
zeile("[LAUT]: Adam ausgelöst, Marke aus der Meldung entfernt",
      g["adam_ausgeloest"] and not g["meldung"].startswith("[LAUT]"), gemessen=str(g))
g = neustarte.grund_lesen("[STILL]")
zeile("[STILL]: planmäßig, mit Ersatztext",
      g["planmaessig"] and "Hygiene" in g["meldung"], gemessen=str(g))
g = neustarte.grund_lesen("Bin da. [AUTORUN]: mach weiter")
zeile("[AUTORUN] bleibt in der Meldung, nicht im Vermerk",
      "[AUTORUN]:" in g["meldung"] and "AUTORUN" not in g["grund"], gemessen=str(g))

print("== C. Vermerken und zählen (Fenster bis vier Uhr) ==")
von, bis = neustarte.fenster()
with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "n.jsonl"
    for z in (von + 60, von + 7200, bis - 60):
        neustarte.vermerken("Timeout", jetzt=z, pfad=f)
    neustarte.vermerken("alt", jetzt=von - 60, pfad=f)
    neustarte.vermerken("heute", jetzt=bis + 60, pfad=f)
    n, gruende = neustarte.zaehlen(pfad=f)
    zeile("gezählt wird nur das Fenster (drei von fünf)", n == 3, gemessen=f"{n} {gruende}")
    tuer, satz = neustarte.befund(n, gruende)
    zeile("der dritte ist ein Befund an Adam, mit Grund",
          tuer == "adam" and "Timeout" in satz and "3" in satz, gemessen=f"{tuer}: {satz}")
    tuer, _ = neustarte.befund(2, ["Timeout", "Timeout"])
    zeile("zwei bleiben im Protokoll", tuer == "protokoll")
    with f.open("a", encoding="utf-8") as h:
        h.write("kaputt{\n")
    n2, _ = neustarte.zaehlen(pfad=f)
    zeile("ein unlesbarer Vermerk zählt mit", n2 == 4, gemessen=str(n2))
    for i in range(neustarte.BEHALTEN + 5):
        neustarte.vermerken("x", jetzt=von - 10_000 - i, pfad=f)
    zeile("die Datei wird gekürzt, nicht unbegrenzt länger",
          len(f.read_text(encoding="utf-8").splitlines()) == neustarte.BEHALTEN)

print("== D. Verkabelung im Startpfad (echte Aufrufknoten) ==")
baum = ast.parse((WURZEL / "bot.py").read_text(encoding="utf-8"))


def _funktion(name: str):
    for k in ast.walk(baum):
        if isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef)) and k.name == name:
            return k
    return None


def _aufrufe(knoten, attr: str) -> list[ast.Call]:
    return [c for c in ast.walk(knoten) if isinstance(c, ast.Call)
            and isinstance(c.func, ast.Attribute) and c.func.attr == attr
            and isinstance(c.func.value, ast.Name) and c.func.value.id == "neustarte"]


post = _funktion("post_init")
st = _aufrufe(post, "still") if post else []
zeile("der Start ruft neustarte.still mit allen vier Bedingungen",
      len(st) == 1 and {k.arg for k in st[0].keywords} == set(sauber),
      gemessen=str([[k.arg for k in c.keywords] for c in st]))
leer = False
for k in ast.walk(post or ast.Module(body=[], type_ignores=[])):
    if (isinstance(k, ast.If) and isinstance(k.test, ast.Name) and k.test.id == "still"):
        for s in k.body:
            if (isinstance(s, (ast.Assign, ast.AnnAssign))
                    and "send_targets" in ast.unparse(s) and ast.unparse(s).rstrip().endswith("[]")):
                leer = True
zeile("das Ergebnis leert die Empfänger", leer)
eigene = False
for k in ast.walk(post or ast.Module(body=[], type_ignores=[])):
    if isinstance(k, ast.Try) and _aufrufe(k, "vermerken"):
        # Die Klammer trägt NUR den Vermerk — sonst würde aus einem
        # Buchführungsfehler ein Startfehler (Regel vom 10.09.).
        eigene = len(k.body) == 1 and bool(_aufrufe(k.body[0], "vermerken"))
zeile("der Vermerk sitzt in eigener Klammer", eigene)
zeile("der Grund wird über neustarte.grund_lesen gelesen",
      bool(post) and len(_aufrufe(post, "grund_lesen")) == 1)
neu = _funktion("_do_restart")
laut = False
for c in ast.walk(neu or ast.Module(body=[], type_ignores=[])):
    if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr == "write_text" and c.args
            and isinstance(c.args[0], ast.BinOp)
            and isinstance(c.args[0].left, ast.Name) and c.args[0].left.id == "_LAUT_MARKE"):
        laut = True
wert = re.search(r'^_LAUT_MARKE = "([^"]+)"', (WURZEL / "bot.py").read_text(encoding="utf-8"), re.M)
zeile("/restart schreibt die [LAUT]-Marke, und sie ist dieselbe wie in neustarte",
      laut and wert is not None and wert.group(1) == neustarte.LAUT,
      gemessen=f"{laut} {wert.group(1) if wert else None}")


def _abschnitt(name: str) -> str:
    t = TAGESCHECK.read_text(encoding="utf-8")
    m = re.search(rf"# >>> {name}\n(.*?)# <<< {name}", t, re.S)
    return m.group(1) if m else ""


ADRESSAT = _abschnitt("ADRESSAT")
VORSPANN = r'''
set -uo pipefail
problems=(); lines=()
LAUFDATEI="$TMPD/lauf.txt"; : > "$LAUFDATEI"
trocken() { return 1; }
merken() { printf '%s\n' "$1" >> "$LAUFDATEI"; }
add() { lines+=("$1"); merken "$1"; }
BOTENV=(env)
'''
NACHSPANN = r'''
echo "PROBLEMS=${#problems[@]}"
for p in "${problems[@]:-}"; do echo "P:$p"; done
echo "---"; cat "$LAUFDATEI"
'''


def _bash(rumpf: str, env: dict) -> str:
    r = subprocess.run(["bash", "-c", rumpf], capture_output=True, text=True,
                       env={**os.environ, **env})
    return r.stdout + r.stderr


print("== E. Tagescheck zählt (echter Abschnitt NEUSTARTS) ==")
ns = _abschnitt("NEUSTARTS")
zeile("der Abschnitt ist im Skript markiert", bool(ns) and "neustarte.py" in ns)
for anzahl, erwartet, name in ((3, 1, "drei im Fenster erreichen Adam"),
                               (1, 0, "einer bleibt im Protokoll")):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "n.jsonl"
        for i in range(anzahl):
            neustarte.vermerken("Timeout", jetzt=von + 60 * (i + 1), pfad=f)
        aus = _bash(VORSPANN + ADRESSAT + f'BOTDIR="{WURZEL}"\nVENVPY="{sys.executable}"\n'
                    + ns + NACHSPANN, {"TMPD": d, "STILLE_NEUSTARTS": str(f)})
        protokoll = aus.split("---", 1)[-1]
        zeile(name, f"PROBLEMS={erwartet}" in aus and "Neustarts gestern" in protokoll,
              gemessen=aus[-200:])
with tempfile.TemporaryDirectory() as d:
    aus = _bash(VORSPANN + ADRESSAT + f'BOTDIR="{WURZEL}"\nVENVPY=false\n' + ns + NACHSPANN,
                {"TMPD": d})
zeile("eine abgestürzte Zählung geht an die Kontrolle, nicht in die Ruhe",
      "PROBLEMS=0" in aus and "⚙️ Zaehlung stiller Neustarts lief nicht" in aus,
      gemessen=aus[-200:])

print("== F. Stundenblumen-Prüfmoment (echter Abschnitt BLUMEN) ==")
bl = _abschnitt("BLUMEN")
zeile("der Abschnitt ist im Skript markiert", bool(bl) and "--pruefen" in bl)
for rc, satz, erwartet, name in (
        (2, "Es gibt noch keine Kette.", 0, "noch keine Kette: kein Eintrag in problems, kein Kreuz"),
        (1, "Die Kette steht still seit etwa 3 Stunden.", 1, "Kette still: Befund an Adam")):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "stundenblume.py").write_text(
            f"print({satz!r})\nraise SystemExit({rc})\n", encoding="utf-8")
        rumpf = bl.replace('$(dirname "$0")', d)
        aus = _bash(VORSPANN + ADRESSAT + f'VENVPY="{sys.executable}"\n' + rumpf + NACHSPANN,
                    {"TMPD": d})
    protokoll = aus.split("---", 1)[-1]
    ok = f"PROBLEMS={erwartet}" in aus and satz in protokoll
    if rc == 2:
        ok = ok and "❌" not in protokoll
    zeile(name, ok, gemessen=aus[-200:])

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen bestanden.")
