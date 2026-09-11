#!/usr/bin/env python3
# <!-- ROLLE: test-wegwerf-zeilen-a2 -->
"""Die zwei Wegwerf-Zeilen des Regressionslaufs: Notizen und Nutzungszahlen.

**Der Block wird AUSGESCHNITTEN und GEFAHREN**, nicht gelesen — dasselbe
Verfahren wie in `test_uebersprungen_a1.py`. Ein Textscan könnte nur zeigen,
dass die Wörter dastehen; gemessen werden soll, **wann die Wache anschlägt und
wann nicht**.

**Warum es diesen Prüfer gibt** (Claudias Befund 1 vom 11.09.): Die Wache nahm
`usage.json` und die Notizdatei in einer Prüfsumme zusammen. Die Nutzungszahlen
schreibt aber der **lebende Bot** nach jeder Antwort — fiel ein Lauf mit
Bot-Verkehr zusammen, wurde die Zeile rot, ohne dass eine Prüfung etwas
angefasst hatte. Am 02.09. war derselbe Befund schon einmal da, eine Datei
weiter (Heartbeat), und der Fix trug ausdrücklich den Satz *„Notizen und
Nutzungszahlen bleiben scharf"*.

Drei Fälle, Claudias Prüferliste 1 bis 3 — der zweite ist ein **erzwungener
Fehlschlag**: Ohne ihn wäre nicht gemessen, dass die Wache überhaupt noch
anschlagen kann.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LAEUFER = REPO / "scripts/regressionstest.sh"

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


print("== Wegwerf-Zeilen: Notizen und Nutzungszahlen (A2) ==")

quelle = LAEUFER.read_text(encoding="utf-8")


def schneide(von: str, bis: str, was: str) -> str:
    """Schneidet einen Block aus dem Läufer — mit benanntem Abbruch statt Rätsel."""
    i = quelle.find(von)
    j = quelle.find(bis, i + 1)
    if i < 0 or j < 0:
        print(f"  ❌ Block '{was}' nicht gefunden — wurde der Laeufer umgebaut?")
        sys.exit(1)
    return quelle[i:j + len(bis)]


# Teil 1: die Stempel-Funktion und die Vorher-Werte.
kopf = schneide('_stempel() {', 'HEART_VORHER="$(_stempel "$ECHTHEART")"', "Stempel")
# Teil 2: die Auswertung der drei Wegwerf-Zeilen.
rumpf = schneide('_heart_lebt=0',
                 '✅ Wegwerf-Umgebung: Heartbeat unberuehrt (Dienst gestoppt, scharf gemessen)"\nfi',
                 "Auswertung")


def fahre(*, dienst_laeuft: bool, aendere: str | None) -> tuple:
    """Fährt den Block einmal. `aendere` ist 'usage', 'notiz' oder None."""
    heim = Path(tempfile.mkdtemp(prefix="a2-"))
    (heim / "notes").mkdir()
    (heim / ".config/claude-telegram-bot").mkdir(parents=True)
    (heim / ".claude").mkdir()
    notiz = heim / "notes/telegram-notes.md"
    usage = heim / ".config/claude-telegram-bot/usage.json"
    heart = heim / ".claude/bot-heartbeat.txt"
    notiz.write_text("Notiz\n", encoding="utf-8")
    usage.write_text('{"a": 1}\n', encoding="utf-8")
    heart.write_text("lebt\n", encoding="utf-8")

    # systemctl-Attrappe: Nur so laesst sich "der Dienst laeuft" am Mac messen.
    binordner = heim / "bin"
    binordner.mkdir()
    (binordner / "systemctl").write_text(
        "#!/bin/sh\nexit %d\n" % (0 if dienst_laeuft else 3), encoding="utf-8")
    (binordner / "systemctl").chmod(0o755)

    mitte = ""
    if aendere == "usage":
        mitte = 'printf \'{"a": 2}\\n\' > "$ECHTUSAGE"\n'
    elif aendere == "notiz":
        mitte = 'printf \'Andere Notiz\\n\' > "$ECHTNOTIZ"\n'

    skript = (
        "#!/usr/bin/env bash\nset -uo pipefail\n"
        'ECHTHEART="$HOME/.claude/bot-heartbeat.txt"\n'
        'ECHTNOTIZ="$HOME/notes/telegram-notes.md"\n'
        'ECHTUSAGE="$HOME/.config/claude-telegram-bot/usage.json"\n'
        "FAILS=0\nGESAMT=0\nUEBERSPRUNGEN=0\n"
        + kopf + "\n" + mitte + rumpf
        + '\necho "BILANZ fails=$FAILS gesamt=$GESAMT uebersprungen=$UEBERSPRUNGEN"\n')
    pfad = heim / "block.sh"
    pfad.write_text(skript, encoding="utf-8")

    umg = dict(os.environ)
    umg["HOME"] = str(heim)
    umg["PATH"] = f"{binordner}:{umg.get('PATH', '')}"
    r = subprocess.run(["bash", str(pfad)], capture_output=True, text=True,
                       env=umg, timeout=60)
    m = re.search(r"BILANZ fails=(\d+) gesamt=(\d+) uebersprungen=(\d+)", r.stdout)
    shutil.rmtree(heim, ignore_errors=True)
    if not m:
        return None, None, None, r.stdout + r.stderr
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), r.stdout


# ── 1. Dienst laeuft, Nutzungszahlen aendern sich → NICHT GEMESSEN, kein Fehler
_f, _g, _u, _aus = fahre(dienst_laeuft=True, aendere="usage")
zeile("laufender Dienst: geaenderte Nutzungszahlen sind NICHT GEMESSEN, nicht rot",
      _f == 0 and _u == 2 and "Nutzungszahlen): NICHT GEMESSEN" in (_aus or ""),
      gemessen=f"fails={_f} uebersprungen={_u}")

# ── 2. ERZWUNGENER FEHLSCHLAG: Dienst gestoppt, Nutzungszahlen geaendert ─────
# Ohne diesen Fall waere nicht gemessen, dass die Wache ueberhaupt noch
# anschlagen KANN — eine Ausnahme, die immer greift, ist keine Ausnahme.
_f, _g, _u, _aus = fahre(dienst_laeuft=False, aendere="usage")
zeile("gestoppter Dienst: geaenderte Nutzungszahlen schlagen an",
      _f == 1 and "ECHTEN Nutzungszahlen veraendert" in (_aus or ""),
      gemessen=f"fails={_f}")

# ── 3. Die Notizdatei bleibt in JEDEM Zustand scharf ─────────────────────────
# Sie schreibt nur, wer etwas falsch macht — der Bot fasst sie im Normalbetrieb
# nicht an. Deshalb darf sie an der Ausnahme nicht teilhaben.
_f_an, _, _, _aus_an = fahre(dienst_laeuft=True, aendere="notiz")
_f_aus, _, _, _aus_weg = fahre(dienst_laeuft=False, aendere="notiz")
zeile("die Notizdatei ist scharf, ob der Dienst laeuft oder nicht",
      _f_an == 1 and _f_aus == 1
      and "ECHTE Notizdatei veraendert" in (_aus_an or "")
      and "ECHTE Notizdatei veraendert" in (_aus_weg or ""),
      gemessen=f"laufend fails={_f_an}, gestoppt fails={_f_aus}")

# ── 4. Und ein ruhiger Lauf bleibt gruen ─────────────────────────────────────
# Die Gegenrichtung: Eine Wache, die immer anschlaegt, wird abgeschaltet.
_f, _g, _u, _aus = fahre(dienst_laeuft=False, aendere=None)
zeile("ohne Aenderung ist alles gruen und nichts uebersprungen",
      _f == 0 and _u == 0 and _g == 3,
      gemessen=f"fails={_f} gesamt={_g} uebersprungen={_u}")

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
