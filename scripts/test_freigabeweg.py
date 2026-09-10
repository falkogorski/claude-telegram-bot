#!/usr/bin/env python3
# <!-- ROLLE: test-freigabeweg -->
"""Der Freigabeweg wird **ausgeführt**: Adam drückt Genehmigen, und das
Werkzeug ist erlaubt.

**Anlass, 10.09.2026 um 01:03:** Genau das ging fünfeinhalb Stunden lang
schief. In `can_use_tool` stand seit M-3 ein `datetime.now()` ohne Import —
mitten in der `try`-Klammer, die das Senden des Dialogs absichert. Der
`NameError` fiel in den `except`, und der antwortet mit
`PermissionResultDeny("bot failed to ask user")`. **Der Dialog kam an, Adam
drückte, das Werkzeug war trotzdem verweigert.**

**Warum es niemand sah:** Der Regressionslauf führte diesen Pfad nicht aus.
Die vorhandene Prüfung mass per `ast`, dass `dialog_gezeigt` *aufgerufen wird*
— nicht, dass die Zeile *läuft*. Ein Aufrufknoten im Baum ist kein
ausgeführter Pfad; das steht seit dem 22.08. in unseren eigenen Regeln.

Hier läuft der Pfad wirklich: Attrappen sitzen nur an den Rändern (Telegram
und die Antwort auf den Knopf), die Mitte ist echter Code.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="freigabe-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
os.environ["BASHFREI_HEIM"] = str(_TMP)
os.environ["BASHFREI_PROTOKOLL"] = str(_TMP / "bashfreigabe.jsonl")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                      # noqa: E402

CHAT_PRUEF = 999


def F(person, thema=None, chat=None):
    """Ein Faden fuer den Pruefstand (F-22: der Schluessel traegt drei Teile)."""
    return bot.faden(person, CHAT_PRUEF if chat is None else chat, thema)


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
print("== Freigabeweg: Genehmigen heisst erlaubt ==")

GESENDET: list[dict] = []


class _Gesendete:
    def __init__(self, mid):
        self.message_id = mid


class _BotAttrappe:
    """Nur der Rand: Telegram. Gibt zurueck, was die echte API zurueckgibt --
    ein Objekt mit `message_id`. Eine Attrappe, die `None` liefert, haette den
    Fehler an einer anderen Stelle erzeugt als im Betrieb."""

    async def send_message(self, **kw):
        GESENDET.append(kw)
        return _Gesendete(1000 + len(GESENDET))


async def _lauf(antwort: str = "allow", werkzeug: str = "Write",
                eingabe: "dict | None" = None, thread_id=None):
    """**[ERWEITERT 10.09.2026, Ultracode-Befund E8 und E10]**

    Vorher fuhr dieser Pruefer **nur** `Write` und **nur** den Hauptfaden.
    Gemessen wurde damit: Ein Attribut-Vertipper im Bash-Zweig des Dialogs
    (`AttributeError`) liess alle zehn Pruefer gruen, und ein Dialog mit
    `message_thread_id=None` fiel niemandem auf, **weil kein Pruefer den
    Dialog je mit einem Faden fuhr.**
    """
    sess = bot.UserSession(client=None, chat_id=999)
    sess.bot = _BotAttrappe()
    sess.thread_id = thread_id
    bot.SESSIONS[F(UID, thread_id)] = sess

    rueckruf = bot.make_permission_callback(F(UID, thread_id))

    async def _adam_drueckt():
        # Wie der echte Knopf: warten, bis die Anfrage registriert ist, dann
        # das Future setzen -- genau das tut `on_permission_callback`.
        for _ in range(200):
            if sess.pending_permissions:
                break
            await asyncio.sleep(0.01)
        else:
            return
        rid = next(iter(sess.pending_permissions))
        schleife, fut = sess.pending_permissions[rid]
        if not fut.done():
            schleife.call_soon_threadsafe(fut.set_result, antwort)

    druecker = asyncio.create_task(_adam_drueckt())
    if eingabe is None:
        eingabe = {"file_path": str(_TMP / "ziel.txt"), "content": "x"}
    ergebnis = await rueckruf(werkzeug, eingabe, None)
    await druecker
    return ergebnis


erg = asyncio.run(_lauf("allow"))

zeile("ein Dialog wird überhaupt gesendet",
      bool(GESENDET), gemessen=str(GESENDET[:1])[:80])
zeile("Genehmigen heißt ERLAUBT, nicht verweigert",
      type(erg).__name__ == "PermissionResultAllow",
      gemessen=f"{type(erg).__name__}: {getattr(erg, 'message', '')}")
# **Die Zeile, an der es hing.** „bot failed to ask user" ist die Meldung aus
# dem `except`, das die Sende-Klammer traegt -- sie bedeutet im Betrieb, dass
# die BUCHFUEHRUNG gebrochen ist, nicht das Senden.
zeile("keine Verweigerung mit „bot failed to ask user“",
      "failed to ask" not in str(getattr(erg, "message", "")),
      gemessen=str(getattr(erg, "message", "")))

# **[VERSCHÄRFT 10.09.2026, Ultracode-Befund E3b]** Hier stand
# `"dialog_gezeigt" in inhalt or "dialog" in inhalt` — das zweite Stück machte
# die Zeile fast immer wahr, denn „dialog" steht in jeder zweiten Meldung.
# Jetzt wird das Protokoll **als Datensatz gelesen**, nicht als Text: genau
# ein Eintrag `dialog_gezeigt`, und er nennt das richtige Werkzeug.
import json as _json                                             # noqa: E402
prot = Path(os.environ["BASHFREI_PROTOKOLL"])
_saetze = []
if prot.exists():
    for _z in prot.read_text(encoding="utf-8").splitlines():
        try:
            _saetze.append(_json.loads(_z))
        except Exception:
            pass
_gezeigt = [s for s in _saetze if s.get("ereignis") == "dialog_gezeigt"]
zeile("der gezeigte Dialog steht als EINTRAG im Protokoll (M-3)",
      len(_gezeigt) == 1,
      gemessen=f"{len(_gezeigt)} Eintraege von {len(_saetze)} Zeilen")
zeile("und er nennt das Werkzeug",
      _gezeigt and _gezeigt[0].get("werkzeug") == "Write",
      gemessen=str(_gezeigt[:1]))

# ── E8: der Bash-Zweig des Dialogs ─────────────────────────────────────────
#
# **Gemessen im Ultracode-Probelauf:** Ein Attribut-Vertipper im Bash-Zweig
# liess **alle zehn** Pruefer gruen — dieser hier fuhr nur `Write`, und der
# Bash-Zweig hat eigenen Code (Befehlszerlegung, Auto-Zustand, 💰-Pruefung).
# Das ist die Schwesterform des Ausfalls vom 09.09.
GESENDET.clear()
for fd in list(bot.SESSIONS):
    bot.SESSIONS.pop(fd)
# **Ein Bruch im Zweig macht diese Zeile ROT, er stuerzt den Pruefer nicht
# ab.** Ein abstuerzender Pruefer verdeckt alles darunter -- derselbe Fehler,
# den mein Block-2-Pruefer am 09.09. hatte. Und er misst das Falsche: Im
# Betrieb faengt ein `except` den Bruch und macht daraus eine **Verweigerung**,
# also Ruhe statt Krach.
try:
    _erg_bash = asyncio.run(_lauf("allow", werkzeug="Bash",
                                  eingabe={"command": "ls -la /tmp"}))
except Exception as _e:
    _erg_bash = _e
# **Erst der Nachweis, dass der Zweig ueberhaupt laeuft**: `ls -la /tmp`
# liegt ausserhalb der Bereiche und geht darum in den Dialog. Ohne diese
# Zeile maesse die naechste nur einen Rueckgabewert, den es auch ohne Dialog
# gibt.
zeile("der Bash-Zweig sendet wirklich einen Dialog",
      bool(GESENDET), gemessen=str(len(GESENDET)))
zeile("und er laeuft ohne Bruch",
      not isinstance(_erg_bash, Exception)
      and "failed to ask" not in str(getattr(_erg_bash, "message", "")),
      gemessen=f"{type(_erg_bash).__name__}: "
               f"{getattr(_erg_bash, 'message', None) or _erg_bash}")
zeile("und Genehmigen heisst dort ebenfalls erlaubt",
      type(_erg_bash).__name__ == "PermissionResultAllow",
      gemessen=str(getattr(_erg_bash, "message", "")))

# ── E10: der Dialog kennt sein Zimmer ──────────────────────────────────────
#
# **Kein Pruefer fuhr den Dialog je mit `thread_id != None`.** Die Attrappe
# zeichnete die Argumente auf, aber keine Zeile las sie. Ein Dialog, der im
# General statt im Zimmer erscheint, ist genau die Klasse aus A-5 — nur an
# der Stelle, an der Adam antworten soll.
GESENDET.clear()
for fd in list(bot.SESSIONS):
    bot.SESSIONS.pop(fd)
_erg_zimmer = asyncio.run(_lauf("allow", thread_id=7))
zeile("der Freigabe-Dialog erscheint IM ZIMMER, nicht im General",
      GESENDET and GESENDET[0].get("message_thread_id") == 7,
      gemessen=str([g.get("message_thread_id") for g in GESENDET]))
zeile("und die Freigabe gilt auch dort",
      type(_erg_zimmer).__name__ == "PermissionResultAllow",
      gemessen=f"{type(_erg_zimmer).__name__}")

# Gegenrichtung: Verweigern muss verweigern -- sonst misst die Zeile darueber
# nur, dass ueberhaupt etwas zurueckkommt.
GESENDET.clear()
bot.SESSIONS.clear()
erg2 = asyncio.run(_lauf("deny"))
zeile("Verweigern heißt verweigert (Gegenrichtung)",
      type(erg2).__name__ == "PermissionResultDeny",
      gemessen=type(erg2).__name__)

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen des Freigabewegs bestanden.")
