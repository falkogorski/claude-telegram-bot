#!/usr/bin/env python3
# <!-- ROLLE: test-hotfix-h3-h5 -->
"""Hotfix H-3 bis H-5 aus dem Ultracode-Befund vom 10.09.2026.

Drei Funde, ein Muster: **Eine Meldung, die nie ankommt.** Am Stichtag ging
sie nur ins Log, beim Postfach an Telegram vorbei — und beide Male hielt ein
Dämpfer oder ein `else` den Zustand für erledigt.

Gemessen wird **ausgeführt**: der Frist-Block wird aus dem Tagescheck
geschnitten und mit Attrappen für `red`/`add` gefahren; die Drossel-Meldung
läuft mit einer Bot-Attrappe, die sich wie Telegram verhält, wenn ein
Unterstrich im Namen steht.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_TMP = Path(tempfile.mkdtemp(prefix="hotfix-")).resolve()
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
import bot                                                      # noqa: E402

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


print("== Hotfix H-3 bis H-5 ==")

# ── H-3: Am Stichtag muss Adam erreicht werden ──────────────────────────────
#
# `add` landet nur im Log; gesendet wird ausschliesslich, was `red` sammelt.
# Die Berichtigung vom 09.09. stellte den Wortlaut richtig und kappte dabei
# den Meldeweg — genau am Tag, an dem noch etwas zu entscheiden ist.
CHECK = ROOT / "scripts" / "daily_check.sh"
quelle = CHECK.read_text(encoding="utf-8")
block = re.search(r'^  if \[ "\$HEUTE_ISO" = "\$bis" \]; then.*?^  fi$',
                  quelle, re.S | re.M)
zeile("H-3: der Frist-Block ist im Tagescheck auffindbar", block is not None)

if block is not None:
    def frist(heute: str, bis: str) -> str:
        """Faehrt den ECHTEN Block mit Attrappen fuer red/add."""
        skript = (
            'red() { printf "RED:%s\\n" "$*"; }\n'
            'add() { printf "ADD:%s\\n" "$*"; }\n'
            f'HEUTE_ISO="{heute}"\nbis="{bis}"\nfrist_datei="/tmp/f.json"\n'
            + block.group(0).replace("  if [", "if [", 1)
        )
        e = subprocess.run(["/bin/bash", "-c", skript],
                           capture_output=True, text=True)
        return (e.stdout or "") + (e.stderr or "")

    _stichtag = frist("2026-09-10", "2026-09-10")
    zeile("H-3: AM Stichtag geht die Meldung an Adam (rot), nicht nur ins Log",
          _stichtag.startswith("RED:") and "HEUTE ab" in _stichtag,
          gemessen=_stichtag.strip()[:120])
    _danach = frist("2026-09-11", "2026-09-10")
    zeile("H-3: danach weiterhin rot", _danach.startswith("RED:"),
          gemessen=_danach.strip()[:80])
    _davor = frist("2026-09-09", "2026-09-10")
    zeile("H-3: davor bleibt es eine Log-Zeile (Gegenrichtung)",
          _davor.startswith("ADD:"), gemessen=_davor.strip()[:80])

# ── H-4: Ohne Angabe gilt die strengste Grenze, nicht die höchste ──────────
#
# Eingetragen wird, wer MEHR darf. Eine Vorgabe, die 100 je Stunde bedeutet,
# drehte die Regel um: Jeder Aufrufer ohne Schalter bekam sie.
ABLEGEN = ROOT / "scripts" / "postfach_ablegen.py"


def ablegen(*args) -> dict:
    ordner = Path(tempfile.mkdtemp(prefix="postfach-", dir=_TMP))
    umgebung = dict(os.environ, POSTFACH_DIR=str(ordner))
    subprocess.run([sys.executable, str(ABLEGEN), "--chat", "4711",
                    "--text", "hallo", *args],
                   env=umgebung, capture_output=True, text=True)
    dateien = sorted((ordner / "ausgang").glob("*.json")) if (ordner / "ausgang").is_dir() \
        else sorted(ordner.rglob("*.json"))
    return json.loads(dateien[0].read_text(encoding="utf-8")) if dateien else {}


_ohne = ablegen()
zeile("H-4: ohne Angabe steht kein fremder Name im Auftrag",
      _ohne.get("herkunft") == "ohne Absender", gemessen=str(_ohne))
zeile("H-4: und damit gilt die strengste Grenze, nicht die höchste",
      bot._postfach_grenze_fuer("ohne Absender") == bot.POSTFACH_GRENZE
      and bot.POSTFACH_GRENZE < bot._postfach_grenze_fuer("claudia"),
      gemessen=f"{bot._postfach_grenze_fuer('ohne Absender')} vs "
               f"{bot._postfach_grenze_fuer('claudia')}")
_mit = ablegen("--herkunft", "claudia")
zeile("H-4: wer sich nennt, bekommt seine Grenze (Gegenrichtung)",
      _mit.get("herkunft") == "claudia"
      and bot._postfach_grenze_fuer("claudia") > bot.POSTFACH_GRENZE,
      gemessen=str(_mit))

# Der Aufrufer, der es ausgelöst hat: `rechnungen_ablegen.sh` setzte nichts.
_rsh = (ROOT / "scripts" / "mac" / "rechnungen_ablegen.sh").read_text(encoding="utf-8")
zeile("H-4: der Rechnungs-Aufrufer nennt sich ausdrücklich",
      "--herkunft mac-rechnungen" in _rsh)

# ── H-5: Die Meldung über den Stau darf nicht selbst im Stau steckenbleiben ─
class _BotAttrappe:
    """Verhält sich wie Telegram: lehnt Markdown mit unpaarigem `_` ab."""

    def __init__(self):
        self.gesendet = []

    async def send_message(self, **kw):
        if kw.get("parse_mode") and "_" in (kw.get("text") or ""):
            raise RuntimeError("Can't parse entities: unmatched underscore")
        self.gesendet.append(kw)


class _App:
    def __init__(self):
        self.bot = _BotAttrappe()


def melden(herkunft: str) -> tuple[_App, bool]:
    bot._postfach_drossel_gemeldet.clear()
    app = _App()
    asyncio.run(bot._postfach_drossel_sofort_melden(app, 4711, herkunft))
    return app, herkunft in bot._postfach_drossel_gemeldet


_app, _gedaempft = melden("mac_rechnungen")
zeile("H-5: ein Unterstrich im Absendernamen bricht die Meldung nicht mehr",
      len(_app.bot.gesendet) == 1, gemessen=str(_app.bot.gesendet)[:150])
zeile("H-5: gesendet wird ohne parse_mode",
      _app.bot.gesendet and _app.bot.gesendet[0].get("parse_mode") is None)
zeile("H-5: nach erfolgreichem Senden ist der Dämpfer gesetzt", _gedaempft)

# Die Gegenrichtung, und sie ist der Kern: Scheitert das Senden wirklich,
# darf der Dämpfer die nächste Stunde NICHT sperren.
class _StummerBot(_BotAttrappe):
    async def send_message(self, **kw):
        raise RuntimeError("Telegram nicht erreichbar")


bot._postfach_drossel_gemeldet.clear()
_app2 = _App()
_app2.bot = _StummerBot()
asyncio.run(bot._postfach_drossel_sofort_melden(_app2, 4711, "blume"))
zeile("H-5: scheitert das Senden, sperrt der Dämpfer NICHT die nächste Stunde",
      "blume" not in bot._postfach_drossel_gemeldet,
      gemessen=str(dict(bot._postfach_drossel_gemeldet)))

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
