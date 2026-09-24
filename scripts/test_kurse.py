#!/usr/bin/env python3
"""Kurs-Videos (Adams Entscheid 24.09., Engywucks Zettel F2): Prüfer.

Ausführend: der echte Ablauf von `scripts/kurse.py` mit einer Attrappe nur am
Rand (dem Whisper-Modell), der echte Tagescheck-Abschnitt KURSE, das echte
Mac-Skript mit Attrappen für `ssh` und `rsync`. Was hier nicht geprüft wird,
steht am Ende: das Laden des echten Modells (braucht den Download, gehört in
die Probe auf dem VPS).
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
sys.path.insert(0, str(WURZEL / "scripts"))

TMP = Path(tempfile.mkdtemp(prefix="kurse-"))
os.environ["KURSE_EINGANG"] = str(TMP / "eingang")
os.environ["KURSE_STAND"] = str(TMP / "stand.json")
os.environ["WISSEN_DIR"] = str(TMP / "wissen")

import kurse  # noqa: E402

zeilen = 0
fehler: list[str] = []


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    print(("✅ " if bedingung else "❌ ") + name + ("" if bedingung else f"  [{gemessen}]"))
    if not bedingung:
        fehler.append(name)


def attrappe(pfad: Path):
    """Der Rand: statt Whisper drei Sätze über zwei Minuten."""
    if "kaputt" in pfad.name:
        raise RuntimeError("Tonspur unlesbar")
    return [(0.0, "Willkommen im Kurs."), (30.0, "Erster Gedanke."), (75.0, "Zweiter Teil.")]


attrappe.stufe = "attrappe"

E = TMP / "eingang"
(E / "Verkaufskurs").mkdir(parents=True)
v1 = E / "Verkaufskurs" / "Modul 1 – Einstieg.mp4"
v1.write_bytes(b"x" * 10)
(E / "Verkaufskurs" / ".Modul 2.mp4.Xy12").write_bytes(b"halb")   # rsync-Zwischenstand
# Versteckt MIT Video-Endung: Die Endung allein faengt das nicht — gemessen an
# der Gegenprobe, die mit dem Zwischenstand oben allein gruen blieb.
(E / "Verkaufskurs" / "._Modul 1 – Einstieg.mp4").write_bytes(b"apple")  # AppleDouble vom Mac
(E / "Verkaufskurs" / "notizen.txt").write_text("kein Video", encoding="utf-8")

print("== A. Was als Video gilt ==")
gefunden = [p.name for p in kurse.finden()]
zeile("nur das Video, kein rsync-Zwischenstand, keine Mac-Schattendatei, keine Notiz",
      gefunden == ["Modul 1 – Einstieg.mp4"], gemessen=str(gefunden))

print("== B. Transkribieren und ablegen (echter Ablauf, Attrappe nur am Modell) ==")
erg = kurse.verarbeiten(attrappe, heute="2026-09-24")
zeile("ein Video verarbeitet, Stand fertig",
      len(erg) == 1 and erg[0]["status"] == "fertig", gemessen=str(erg))
ziel = Path(erg[0].get("ziel", "")) if erg else Path("/nicht")
inhalt = ziel.read_text(encoding="utf-8") if ziel.exists() else ""
zeile("liegt unter wissen/kurse/, nicht im Jahresordner",
      ziel.parent == TMP / "wissen" / "kurse", gemessen=str(ziel))
zeile("mit Herkunftsvermerk: eigenes Material, kein Fremddienst",
      "nie über einen Fremddienst" in inhalt and "Verkaufskurs" in inhalt, gemessen=inhalt[:200])
zeile("mit Sprungmarken je Minute",
      "[00:00:00] Willkommen im Kurs. Erster Gedanke." in inhalt
      and "[00:01:15] Zweiter Teil." in inhalt, gemessen=inhalt[-120:])
zeile("eigener Index im Kursordner",
      (TMP / "wissen" / "kurse" / "INDEX.md").exists())
zeile("der gemeinsame Index (geht nach GitHub) bleibt unberührt",
      not (TMP / "wissen" / "INDEX.md").exists())
zeile("zweiter Lauf: nichts mehr offen", kurse.verarbeiten(attrappe) == [])
alt = v1.stat().st_mtime
os.utime(v1, (alt + 100, alt + 100))
zeile("geänderte Datei wird neu transkribiert", [p.name for p in kurse.offen(kurse.stand_laden())]
      == ["Modul 1 – Einstieg.mp4"])
kurse.verarbeiten(attrappe, heute="2026-09-24")

print("== C. Ein Fehler hält die Reihe nicht auf ==")
(E / "Verkaufskurs" / "Modul 3 kaputt.mp4").write_bytes(b"k")
(E / "Verkaufskurs" / "Modul 4.m4a").write_bytes(b"a")
erg = kurse.verarbeiten(attrappe, heute="2026-09-24")
stati = {e["datei"].split("/")[-1]: e["status"] for e in erg}
zeile("das kaputte scheitert, das nächste läuft trotzdem",
      stati == {"Modul 3 kaputt.mp4": "fehler", "Modul 4.m4a": "fertig"}, gemessen=str(stati))
m = kurse.meldung(erg)
zeile("die Meldung nennt beides, getrennt",
      "1 Kurs-Video(s) transkribiert" in m and "⚠️ 1 Kurs-Video(s) nicht transkribiert" in m
      and "Tonspur unlesbar" in m, gemessen=m)

print("== D. Wer merkt es: --pruefen ==")
zeile("gescheitertes Video: FEHLER", kurse.pruefen().startswith("FEHLER 1"), gemessen=kurse.pruefen())
(E / "Verkaufskurs" / "Modul 3 kaputt.mp4").unlink()
neu = E / "Verkaufskurs" / "Modul 5.mp4"
neu.write_bytes(b"5")
zeile("frisch hochgeladen: noch kein Befund", kurse.pruefen().startswith("OK"), gemessen=kurse.pruefen())
os.utime(neu, (time.time() - 7 * 3600, time.time() - 7 * 3600))
zeile("sieben Stunden unverarbeitet: LIEGT", kurse.pruefen().startswith("LIEGT 1"),
      gemessen=kurse.pruefen())


def _abschnitt(name: str) -> str:
    t = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
    m = re.search(rf"# >>> {name}\n(.*?)# <<< {name}", t, re.S)
    return m.group(1) if m else ""


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
echo "---"; cat "$LAUFDATEI"
'''

print("== E. Tagescheck, echter Abschnitt KURSE ==")
ku = _abschnitt("KURSE")
zeile("der Abschnitt ist im Skript markiert", bool(ku) and "--pruefen" in ku)
rumpf = VORSPANN + _abschnitt("ADRESSAT") + f'BOTDIR="{WURZEL}"\nVENVPY="{sys.executable}"\n' + ku + NACHSPANN
aus = subprocess.run(["bash", "-c", rumpf], capture_output=True, text=True,
                     env={**os.environ, "TMPD": str(TMP)}).stdout
zeile("liegengebliebenes Video erreicht Adam", "PROBLEMS=1" in aus and "Modul 5.mp4" in aus,
      gemessen=aus[-200:])
kurse.verarbeiten(attrappe, heute="2026-09-24")
aus = subprocess.run(["bash", "-c", rumpf], capture_output=True, text=True,
                     env={**os.environ, "TMPD": str(TMP)}).stdout
zeile("alles verarbeitet: nur eine grüne Protokollzeile",
      "PROBLEMS=0" in aus and "✅ Kurs-Videos:" in aus, gemessen=aus[-200:])

print("== F. Meldeweg ==")
import botenpost  # noqa: E402
zeile("der Absender [kurse] ist zugelassen", "kurse" in botenpost.ABSENDER)
baum = ast.parse((WURZEL / "scripts" / "kurse.py").read_text(encoding="utf-8"))
haupt = next(k for k in ast.walk(baum) if isinstance(k, ast.FunctionDef) and k.name == "main")
rufe = [c for c in ast.walk(haupt) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
        and c.func.attr == "legen" and getattr(c.func.value, "id", "") == "botenpost"]
zeile("main meldet über die Botenpost als [kurse]",
      len(rufe) == 1 and any(isinstance(a, ast.Constant) and a.value == "kurse" for a in rufe[0].args))

print("== G. Das Mac-Skript (echt, mit Attrappen für ssh und rsync) ==")
bin_ = TMP / "bin"
bin_.mkdir()
for name in ("ssh", "rsync"):
    (bin_ / name).write_text(f'#!/bin/bash\necho "{name} $*" >> "{TMP}/aufrufe.txt"\nexit 0\n',
                             encoding="utf-8")
    (bin_ / name).chmod(0o755)
quelle = TMP / "Mac" / "Verkaufs Kurs"
quelle.mkdir(parents=True)
(quelle / "a.mp4").write_bytes(b"a")
r = subprocess.run(["bash", str(WURZEL / "scripts" / "mac" / "kurse_hochladen.sh"), str(quelle)],
                   capture_output=True, text=True, env={**os.environ, "PATH": f"{bin_}:{os.environ['PATH']}"})
auf = (TMP / "aufrufe.txt").read_text(encoding="utf-8") if (TMP / "aufrufe.txt").exists() else ""
rs = [z for z in auf.splitlines() if z.startswith("rsync ")]
zeile("überträgt als claudebot, nicht als root",
      rs and "claudebot:kurse-eingang/Verkaufs_Kurs/" in rs[0] and "claudevps" not in auf,
      gemessen=auf)
zeile("ohne Besitz vom Mac (-rlt, nicht -a), fortsetzbar in einen VERSTECKTEN Teilordner",
      rs and " -rlt " in f" {rs[0]} " and " -a " not in f" {rs[0]} "
      and re.search(r"--partial-dir=\.", rs[0]) is not None,
      gemessen=rs[0] if rs else "")
zeile("startet danach kurse.py mit niedrigster Priorität",
      "nice -n 19" in auf and "scripts/kurse.py" in auf and r.returncode == 0, gemessen=auf[-200:])

print()
print("Nicht hier geprüft: das Laden des echten faster-whisper-Modells — dafür die Probe auf dem VPS.")
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen bestanden.")
