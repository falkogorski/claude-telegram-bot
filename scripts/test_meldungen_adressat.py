#!/usr/bin/env python3
# <!-- ROLLE: test-meldungen-adressat -->
"""Meldungen nur, was Adam betrifft — **ausgeführt** (Block 3, 24.09.2026).

Claudias Auftrag vom 19.09.: Was Adam erreicht, muss ihn betreffen oder eine
Entscheidung von ihm brauchen. Die eigentliche Gefahr dabei ist ein **blinder
Wächter** — wer die Schwelle hebt, kann sie zu hoch setzen, und dann sieht ein
echter Befund aus wie Ruhe. Deshalb misst dieser Prüfer beide Richtungen:

  A. Die drei Türen des Tagescheck (`red`, `adam`, `intern`) werden aus dem
     echten Skript geladen und ausgeführt: Was an Adam geht, landet in der
     Meldung; was intern ist, landet im Protokoll — und nirgends verschwindet.
  B. Der Frist-Block (echter Code, nachgebaute Ablage): eine abgelaufene Frist
     erreicht Adam nicht mehr, steht aber mit ⚙️ im Protokoll.
  C. Pflichtfeld: `problems` wird nur in den Türen beschrieben — ein neuer
     Prüfer ohne Einstufung fällt hier auf.
  D. Stundenblume: drei Zustände, und der Befund sagt, was daran hängt.
"""
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
TAGESCHECK = WURZEL / "scripts" / "daily_check.sh"
fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


def _abschnitt(name: str) -> str:
    """Den markierten Abschnitt aus dem ECHTEN Skript — kein Nachbau."""
    t = TAGESCHECK.read_text(encoding="utf-8")
    m = re.search(rf"# >>> {name}\n(.*?)# <<< {name}", t, re.S)
    return m.group(1) if m else ""


def _bash(rumpf: str, env: dict) -> str:
    r = subprocess.run(["bash", "-c", rumpf], capture_output=True, text=True,
                       env={**os.environ, **env})
    return r.stdout + r.stderr


VORSPANN = r'''
set -uo pipefail
problems=(); lines=()
LAUFDATEI="$TMPD/lauf.txt"; : > "$LAUFDATEI"
trocken() { return 1; }
merken() { printf '%s\n' "$1" >> "$LAUFDATEI"; }
add() { lines+=("$1"); merken "$1"; }
'''
NACHSPANN = r'''
echo "PROBLEMS=${#problems[@]}"
for p in "${problems[@]:-}"; do echo "P:$p"; done
echo "ADAM=${n_adam} INTERN=${n_intern}"
echo "---"; cat "$LAUFDATEI"
'''

adressat = _abschnitt("ADRESSAT")
frist = _abschnitt("FRIST")

print("== A. Die drei Türen ==")
with tempfile.TemporaryDirectory() as d:
    aus = _bash(VORSPANN + adressat + r'''
red "Bot tot"
adam "Zustellung gestoert"
intern "Frist abgelaufen: x"
''' + NACHSPANN, {"TMPD": d})
zeile("die drei Türen sind im Skript vorhanden und laufen",
      bool(adressat) and "ADAM=" in aus, gemessen=aus[:120])
zeile("red und adam erreichen Adam",
      "P:Bot tot" in aus and "P:Zustellung gestoert" in aus, gemessen=aus[:200])
zeile("intern erreicht Adam NICHT",
      "P:Frist" not in aus and "PROBLEMS=2" in aus, gemessen=aus[:200])
zeile("… steht aber mit ⚙️ im Protokoll — nichts verschwindet",
      "⚙️ Frist abgelaufen: x" in aus.split("---", 1)[-1], gemessen=aus[-120:])
zeile("die Zählung stimmt je Tür",
      "ADAM=2 INTERN=1" in aus, gemessen=re.findall(r"ADAM=\d+ INTERN=\d+", aus))

print("== B. Der Frist-Block (echter Code) ==")
with tempfile.TemporaryDirectory() as d:
    Path(d, "probe_riegel.md").write_text("GILT-BIS: 2026-09-09\n", encoding="utf-8")
    aus = _bash(VORSPANN + adressat + "BOTDIR=\"$TMPD\"\n" + frist + NACHSPANN,
                {"TMPD": d})
zeile("der Frist-Abschnitt ist im Skript markiert",
      bool(frist) and "GILT-BIS" in frist)
zeile("eine abgelaufene Frist erreicht Adam nicht mehr",
      "PROBLEMS=0" in aus, gemessen=re.findall(r"P:.*", aus)[:2])
zeile("sie steht mit ⚙️ im Protokoll, für die Kontrolle",
      "⚙️ Frist abgelaufen: probe_riegel.md" in aus, gemessen=aus[-150:])

# `[NEU 26.09.2026]` Claudias Auftrag vom 24.09.: Ein geschlossener Riegel hat
# keine Frist. Drei Faelle — geschlossen, scharf, und eine Datei OHNE
# SCHARF-Zeile (wie CLAUDE.md), die sich verhalten muss wie bisher.
print("== B2. Der Riegelzustand (echter Code) ==")
def _frist_lauf(inhalt):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "probe_riegel.md").write_text(inhalt, encoding="utf-8")
        return _bash(VORSPANN + adressat + "BOTDIR=\"$TMPD\"\n" + frist + NACHSPANN,
                     {"TMPD": d})
aus = _frist_lauf("SCHARF: nein\nGILT-BIS: 2026-09-09\n")
zeile("SCHARF: nein, Frist abgelaufen: keine Fristmeldung, nur eine ✅-Zeile",
      "Frist abgelaufen" not in aus and "✅ Riegel probe_riegel.md geschlossen" in aus
      and "PROBLEMS=0" in aus, gemessen=aus[-160:])
aus = _frist_lauf("SCHARF: ja\nGILT-BIS: 2026-09-09\n")
zeile("SCHARF: ja, Frist abgelaufen: die Meldung kommt weiter",
      "⚙️ Frist abgelaufen: probe_riegel.md" in aus, gemessen=aus[-160:])
aus = _frist_lauf("Kein Schalter hier.\nGILT-BIS: 2026-09-09\n")
zeile("ohne SCHARF-Zeile (wie CLAUDE.md): unverändert, die Meldung kommt",
      "⚙️ Frist abgelaufen: probe_riegel.md" in aus, gemessen=aus[-160:])

print("== C. Pflichtfeld: jeder Befund nimmt eine Tür ==")
roh = TAGESCHECK.read_text(encoding="utf-8")
code = [z for z in roh.splitlines() if not z.lstrip().startswith("#")]
schreiber = [z.strip() for z in code if "problems+=" in z]
erlaubt = [z for z in schreiber if re.match(r"^(red|adam)\(\)\s*\{", z)]
zeile("`problems` wird nur in den Türen red/adam beschrieben",
      len(schreiber) == 2 and len(erlaubt) == 2,
      gemessen=str([z[:60] for z in schreiber if z not in erlaubt]))

print("== D. Stundenblume: drei Zustände ==")
sys.path.insert(0, str(WURZEL / "scripts"))
os.environ["BLUMEN_DIR"] = tempfile.mkdtemp(prefix="blumen-")
import stundenblume as sb                                     # noqa: E402

rc, satz = sb.befund_fuer_adam({"ok": False, "zustand": "keine",
                                "grund": "Es gibt noch keine Kette."})
zeile("noch keine Kette: kein Befund, kein Kreuz",
      rc == 2 and "❌" not in satz, gemessen=f"{rc}: {satz}")
rc, satz = sb.befund_fuer_adam({"ok": False, "zustand": "still", "alter_s": 3 * 3600})
zeile("still: Befund, sagt WIE LANGE und WAS daran hängt",
      rc == 1 and "still" in satz and "etwa 3 Stunden" in satz
      and "Tageschecks" in satz, gemessen=satz)
rc, satz = sb.befund_fuer_adam({"ok": False, "zustand": "gebrochen", "brueche": 2})
zeile("gebrochen: Befund, von „still“ unterscheidbar",
      rc == 1 and "Bruchstelle" in satz and "still" not in satz, gemessen=satz)
rc, satz = sb.befund_fuer_adam({"ok": True, "zustand": "ok", "alter_s": 40})
zeile("lebt: kein Befund", rc == 0, gemessen=satz)
# Und der Zustand kommt wirklich aus der Bewertung, nicht nur aus dieser Probe:
e = sb.kette_pruefen(time.time())
zeile("die echte Bewertung liefert den Zustand mit (hier: keine Kette)",
      e.get("zustand") == "keine", gemessen=str(e))

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen bestanden.")
