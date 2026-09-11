#!/usr/bin/env python3
# <!-- ROLLE: test-schreiben-frei -->
"""Der Knopf „Schreiben frei" — vier Bedingungen, vier Prüfzeilen.

**Ausgeführt, nicht gelesen.** Gemessen wird die Entscheidung
(`schreiben_ohne_frage`) und der Weg dorthin über den Knopf — nicht, ob die
Wörter im Quelltext stehen.

**Worum es geht:** Adam am 11.09. von unterwegs — *„ich will die eigentlich gar
nicht mehr drücken müssen."* Claudias Messung derselben Nacht nennt den Grund:
Nicht Bash erzeugt die Kette, sondern `Write` und `Edit`, die in
`_NO_ALWAYS_TOOLS` stehen und deshalb **jede einzelne** Änderung vorlegen.

**Warum das trotzdem keine Dauerfreigabe ist** — und das ist die Zeile, auf die
es ankommt: Das Flag lebt **nur im Speicher**. Es überlebt keinen Prozessstart,
also auch nicht den Hygiene-Neustart um vier. Genau daran ist die alte Fassung
im August gefallen: Jene lag in den Vorlieben.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# `.resolve()` auf die Wegwerf-Wurzel: Auf dem Mac liegt `/var` hinter einem
# Symlink auf `/private/var`. Ohne diese Zeile vergleicht der Pruefstand
# einen aufgeloesten mit einem nicht aufgeloesten Pfad -- und misst dann
# den Symlink statt der Sache.
_TMP = Path(tempfile.mkdtemp(prefix="schreibfrei-")).resolve()
_ARBEIT = _TMP / "workspace"
_ARBEIT.mkdir()
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
os.environ["CLAUDE_ARBEITSORDNER"] = str(_ARBEIT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                        # noqa: E402

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


UID = 4711
print("== Schreiben frei im Arbeitsordner ==")

_drin = str(_ARBEIT / "papier.md")

# ── 1. Mit Flag: eine Aenderung im Arbeitsordner laeuft ohne Frage ──────────
bot.schreiben_frei_setzen(UID, True)
_erlaubt = [w for w in ("Write", "Edit", "MultiEdit")
            if bot.schreiben_ohne_frage(UID, w, _drin)]
zeile("mit Flag laufen Write, Edit und MultiEdit im Arbeitsordner durch",
      _erlaubt == ["Write", "Edit", "MultiEdit"],
      gemessen=f"erlaubt: {_erlaubt}")

# ── 2. Ohne Flag: dieselbe Aenderung fragt ──────────────────────────────────
# Die Gegenrichtung, und ohne sie waere Zeile 1 die Haelfte einer Messung.
bot.schreiben_frei_setzen(UID, False)
_ohne = [w for w in ("Write", "Edit", "MultiEdit")
         if bot.schreiben_ohne_frage(UID, w, _drin)]
zeile("ohne Flag fragt jede Aenderung wieder",
      _ohne == [], gemessen=f"trotzdem erlaubt: {_ohne}")

# ── 3. Trotz Flag: Repo, Gedaechtnis, Geheimnis und Draussen bleiben zu ─────
# Vier Riegel, einzeln gemessen. Ein Sammelurteil wuerde verdecken, welcher
# von ihnen fehlt -- und der fehlende waere der einzige, der zaehlt.
bot.schreiben_frei_setzen(UID, True)
_gesperrt = {
    "Repo-Klon": str(Path.home() / "claude-telegram-bot/bot.py"),
    "Gedaechtnis": str(Path.home() / ".claude/memory/MEMORY.md"),
    "Geheimnis": str(_ARBEIT / ".env"),
    "ausserhalb": str(_TMP / "woanders/datei.md"),
    "einer von zweien draussen": f"{_drin}\n{Path.home()}/.claude/memory/x.md",
    # Der `..`-Weg: sieht aus wie der Arbeitsordner, fuehrt aber hinaus.
    # **Zwei Ziele, und das zweite ist das eigentliche.** Das erste
    # (Gedaechtnis) faengt schon `_is_sensitive_ref` -- gemessen in der
    # Gegenprobe: Ohne `resolve()` blieb es trotzdem gesperrt, also hat es die
    # Pfadaufloesung gar nicht geprueft. Das zweite Ziel ist harmlos benannt
    # und faellt NUR durch `resolve()` heraus.
    "ueber .. ins Gedaechtnis": str(_ARBEIT) + "/../.claude/memory/x.md",
    "ueber .. nach nebenan": str(_ARBEIT) + "/../nebenan/datei.md",
}
_durchgerutscht = [name for name, pfad in _gesperrt.items()
                   if bot.schreiben_ohne_frage(UID, "Write", pfad)]
zeile("trotz Flag bleiben Repo, Gedaechtnis, Geheimnis und Draussen gesperrt",
      not _durchgerutscht, gemessen=f"durchgerutscht: {_durchgerutscht}")

# ── 4. Das Flag ueberlebt keinen Prozessstart ───────────────────────────────
# **Die Zeile, auf die es ankommt.** Sie wird in einem EIGENEN Prozess
# gemessen: Ein frisch gestarteter Bot darf das Flag nicht kennen. Waere es in
# den Vorlieben gelandet, kaeme hier True zurueck -- und aus der Reichweite
# waere die Dauerfreigabe von damals geworden.
_prog = (
    "import os, sys\n"
    f"sys.path.insert(0, {str(Path(__file__).resolve().parent.parent)!r})\n"
    "import bot\n"
    "print('FLAG=' + str(bot.schreiben_frei(4711)))\n"
    "print('ENTSCHEID=' + str(bot.schreiben_ohne_frage(4711, 'Write', "
    f"{_drin!r})))\n")
_r = subprocess.run([sys.executable, "-c", _prog], capture_output=True, text=True,
                    env=dict(os.environ))
zeile("das Flag ueberlebt keinen Prozessstart",
      "FLAG=False" in _r.stdout and "ENTSCHEID=False" in _r.stdout,
      gemessen=(_r.stdout.strip() or _r.stderr.strip()[-200:]))

# ── 5. Der Knopf traegt den Stand und schaltet ihn ──────────────────────────
def _knoepfe():
    return [b.text for row in
            bot._main_keyboard(False, "sonnet", None, user_id=UID).keyboard
            for b in row]


bot.schreiben_frei_setzen(UID, True)
_mit = _knoepfe()
bot.schreiben_frei_setzen(UID, False)
_ohne_k = _knoepfe()
zeile("die Tastatur zeigt den echten Stand und beide Beschriftungen sind bekannt",
      bot._BTN_SCHREIBEN_TO_FRAGEN in _mit and bot._BTN_SCHREIBEN_TO_FREI in _ohne_k
      and bot._BTN_SCHREIBEN_TO_FREI not in _mit
      and bot._BTN_SCHREIBEN_TO_FREI in bot._ALL_KEYBOARD_BTNS
      and bot._BTN_SCHREIBEN_TO_FRAGEN in bot._ALL_KEYBOARD_BTNS,
      gemessen=f"frei: {[b for b in _mit if 'Schreiben' in b]}, "
               f"aus: {[b for b in _ohne_k if 'Schreiben' in b]}")

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
