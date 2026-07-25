#!/usr/bin/env python3
# <!-- ROLLE: start-waechter -->
"""B1 — Start-Wächter außerhalb des Bot-Prozesses.

**Die Lücke, die er schließt (Conni, 25.07.):** Die Sicherheitskette des
Updaters (A1–A7) kann alles zurückrollen — außer den einen Fall, der sie selbst
lahmlegt: *der Bot startet nach dem Neustart nicht mehr*. Ein Rollback braucht
einen laufenden Prozess. Bislang war **Adam** dieser Wächter, weil er den
Neustart von Hand auslöst und hinsieht; ein automatischer Neustart (B2) nähme
ihn aus der Schleife, ohne Ersatz.

Deshalb läuft dieser Wächter **losgelöst vom Bot** (eigener, abgekoppelter
Prozess): Er überlebt dessen Tod, wartet eine Frist auf einen sauberen
Hochlauf und rollt sonst die Umgebung auf den eingefrorenen Stand zurück,
startet erneut und meldet — über das Boten-Postfach, das der Bot nach seiner
Genesung abarbeitet.

**„Sauber hoch" heißt hier dreierlei**, und zwar in dieser Reihenfolge:
1. ein Bot-Prozess **lebt**,
2. der Dienst gilt als **aktiv** (wo systemd vorhanden ist),
3. die **Selbstcheck-Invarianten** laufen durch — gemessen in einem eigenen
   Prozess, nicht erfragt.

Ein lebender Prozess allein genügt ausdrücklich nicht: Der Bot kann laufen und
trotzdem in einer kaputten Umgebung sitzen. Gemessen wird, nicht erzählt.

**Aufruf** (der Updater setzt ihn vor einem Neustart scharf):

    python3 scripts/start_waechter.py --freeze /pfad/zum/freeze.txt \\
        [--venv …] [--frist 240] [--grund "SDK-Update 0.2.130"] [--detach]

Deterministisch, ohne Modell-Aufruf, ohne Netz (außer pip beim Rollback) —
und damit ohne Kosten.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE_DIR = Path(os.environ.get("UPDATER_STATE_DIR")
                 or (Path.home() / ".claude" / "updater"))
BERICHT = STATE_DIR / "startwaechter.json"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"
UNIT = os.environ.get("BOT_UNIT") or "claude-telegram-bot"
TAKT = 6.0            # Sekunden zwischen zwei Prüfrunden
NACHFRIST = 150       # zweite Frist nach dem Rollback


# ---------------------------------------------------------------- Messungen --
def bot_prozess() -> int | None:
    """PID des laufenden Bots (None, wenn keiner läuft).

    Bewusst über den Interpreter-Pfad statt über ein loses „bot.py"-Muster:
    ein `pgrep -f "python bot.py"` zählt sonst den eigenen Aufruf mit — genau
    dieses Messartefakt hat am 24.07. eine Phantom-Zweitinstanz vorgetäuscht.
    """
    try:
        out = subprocess.run(["pgrep", "-af", "bot[.]py"], capture_output=True,
                             text=True, timeout=15).stdout
    except Exception:
        return None
    eigen = os.getpid()
    for zeile in out.splitlines():
        teile = zeile.split(None, 1)
        if len(teile) != 2 or "start_waechter" in teile[1]:
            continue
        try:
            pid = int(teile[0])
        except ValueError:
            continue
        if pid != eigen:
            return pid
    return None


def dienst_aktiv() -> bool | None:
    """True/False laut systemd; None, wenn es hier kein systemd gibt (Mac)."""
    if not shutil.which("systemctl"):
        return None
    try:
        out = subprocess.run(["systemctl", "is-active", UNIT],
                             capture_output=True, text=True, timeout=15)
        return out.stdout.strip() == "active"
    except Exception:
        return None


def selbstcheck(venv: Path) -> tuple[bool, str]:
    """Selbstcheck-Invarianten in EIGENEM Prozess — misst statt zu fragen.

    Platzhalter-Zugangsdaten reichen: der Check nimmt keinen Telegram-Kontakt
    auf. Sie werden nur für diesen Aufruf gesetzt, nie global exportiert
    (Kollisions-Lehre 23.07.).
    """
    py = venv / "bin" / "python3"
    if not py.exists():
        py = Path(sys.executable)
    umgebung = dict(os.environ)
    umgebung.setdefault("TELEGRAM_BOT_TOKEN", "000000:startwaechter-dummy")
    umgebung.setdefault("ALLOWED_USER_IDS", "1")
    try:
        p = subprocess.run(
            [str(py), "-c",
             "import bot,sys;ok,l=bot.run_self_check();"
             "print('\\n'.join(l));sys.exit(0 if ok else 1)"],
            cwd=str(REPO), env=umgebung, capture_output=True, text=True,
            timeout=180)
    except Exception as e:
        return False, f"Selbstcheck nicht ausführbar: {e}"
    if p.returncode == 0:
        return True, ""
    fehler = [z for z in (p.stdout or "").splitlines() if z.startswith("✗")]
    return False, "; ".join(fehler) or (p.stderr or "")[-400:]


def sauber_hoch(venv: Path) -> tuple[bool, str]:
    """Alle drei Bedingungen zusammen — mit Klartext-Grund beim ersten Nein."""
    if bot_prozess() is None:
        return False, "kein Bot-Prozess"
    aktiv = dienst_aktiv()
    if aktiv is False:
        return False, f"Dienst {UNIT} nicht aktiv"
    ok, grund = selbstcheck(venv)
    if not ok:
        return False, f"Selbstcheck rot: {grund}"
    return True, ""


# ---------------------------------------------------------------- Handlungen --
def zurueckrollen(venv: Path, freeze: Path) -> tuple[bool, str]:
    """Vollständiger Umgebungs-Rückbau auf den eingefrorenen Stand (wie A1)."""
    if not freeze.exists():
        return False, f"Freeze-Datei fehlt: {freeze}"
    pip = venv / "bin" / "pip"
    if not pip.exists():
        return False, f"pip nicht gefunden: {pip}"
    try:
        p = subprocess.run([str(pip), "install", "-r", str(freeze)],
                           capture_output=True, text=True, timeout=1800)
        return p.returncode == 0, (p.stderr or "")[-600:]
    except Exception as e:
        return False, str(e)


def neustart_ausloesen() -> str:
    """Sanftes SIGTERM — systemd (Restart=always) holt den Bot zurück.

    Bewusst kein `systemctl restart`: das verlangte root. Der Wächter läuft
    unter demselben Nutzer wie der Bot und kommt so ohne erweiterte Rechte aus
    — eine Rettung, die selbst Sonderrechte bräuchte, wäre die schlechtere.
    """
    pid = bot_prozess()
    if pid is None:
        return "kein Prozess zum Beenden (systemd startet ihn ohnehin neu)"
    try:
        os.kill(pid, signal.SIGTERM)
        return f"Prozess {pid} sanft beendet"
    except Exception as e:
        return f"Beenden fehlgeschlagen: {e}"


def melden(text: str) -> None:
    """Bericht ablegen: Postfach (für Adam) + Zustandsdatei (für 8.1).

    Doppelt mit Absicht — der Bot kann beim Schreiben noch tot sein; dann holt
    der tägliche Funktionscheck den Befund aus der Zustandsdatei nach.
    """
    ziel = (os.environ.get("ALLOWED_USER_IDS") or "").split(",")[0].strip()
    if ziel.isdigit():
        try:
            POSTFACH.mkdir(parents=True, exist_ok=True)
            tmp = POSTFACH / f".{time.time_ns()}.tmp"
            tmp.write_text(json.dumps({"target_chat_id": int(ziel), "text": text},
                                      ensure_ascii=False), encoding="utf-8")
            tmp.rename(POSTFACH / f"{time.time_ns()}.json")
        except Exception:
            pass
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        BERICHT.write_text(json.dumps(
            {"zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "text": text},
            ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def warte_auf_hochlauf(venv: Path, frist: int) -> tuple[bool, str]:
    ende = time.monotonic() + frist
    grund = "Frist abgelaufen, bevor eine Prüfung griff"
    while time.monotonic() < ende:
        ok, grund = sauber_hoch(venv)
        if ok:
            return True, ""
        time.sleep(TAKT)
    return False, grund


def bewachen(venv: Path, freeze: Path, frist: int, grund_text: str) -> int:
    ok, grund = warte_auf_hochlauf(venv, frist)
    if ok:
        melden(f"✅ Start-Wächter: Der Bot ist nach „{grund_text}“ sauber "
               f"hochgekommen (Prozess, Dienst und Selbstcheck geprüft).")
        return 0

    # Der Fall, für den es diesen Wächter gibt.
    zurueck_ok, zurueck_fehler = zurueckrollen(venv, freeze)
    neustart = neustart_ausloesen()
    zweite_ok, zweiter_grund = warte_auf_hochlauf(venv, NACHFRIST)

    if zweite_ok and zurueck_ok:
        melden(f"🔴 Start-Wächter: Nach „{grund_text}“ kam der Bot nicht sauber "
               f"hoch ({grund}). Ich habe die Umgebung auf den eingefrorenen "
               f"Stand zurückgesetzt und neu gestartet — er läuft wieder. "
               f"Das Update ist damit rückgängig; es braucht einen zweiten Blick, "
               f"bevor es erneut eingespielt wird.")
        return 1
    melden(f"🔴🔴 Start-Wächter: Nach „{grund_text}“ kam der Bot nicht hoch "
           f"({grund}). Die Rettung hat NICHT vollständig gegriffen — "
           f"Rückbau: {'ok' if zurueck_ok else 'FEHLGESCHLAGEN: ' + zurueck_fehler}; "
           f"{neustart}; danach: {zweiter_grund or 'weiterhin nicht sauber'}. "
           f"Hier ist ein Eingriff von Hand nötig.")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description="B1 Start-Wächter")
    ap.add_argument("--freeze", required=True,
                    help="pip-freeze-Datei des Zustands VOR dem Eingriff")
    ap.add_argument("--venv", default=str(REPO / ".venv"))
    ap.add_argument("--frist", type=int, default=240,
                    help="Sekunden, die der Bot zum sauberen Hochlauf hat")
    ap.add_argument("--grund", default="dem letzten Eingriff")
    ap.add_argument("--detach", action="store_true",
                    help="sich selbst abkoppeln und im Hintergrund weiterwachen")
    a = ap.parse_args()

    if a.detach:
        # Abkoppeln, damit der Wächter den Tod des Bots (und der aufrufenden
        # Sitzung) überlebt — genau das ist seine Daseinsberechtigung.
        argumente = [x for x in sys.argv[1:] if x != "--detach"]
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), *argumente],
                         start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Start-Wächter abgekoppelt gestartet.")
        return 0

    return bewachen(Path(a.venv), Path(a.freeze), a.frist, a.grund)


if __name__ == "__main__":
    sys.exit(main())
