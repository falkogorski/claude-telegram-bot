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


async def _lauf(antwort: str = "allow"):
    sess = bot.UserSession(client=None, chat_id=999)
    sess.bot = _BotAttrappe()
    bot.SESSIONS[bot.faden(UID)] = sess

    rueckruf = bot.make_permission_callback(UID)

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
    ergebnis = await rueckruf("Write", {"file_path": str(_TMP / "ziel.txt"),
                                        "content": "x"}, None)
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

prot = Path(os.environ["BASHFREI_PROTOKOLL"])
inhalt = prot.read_text(encoding="utf-8") if prot.exists() else ""
zeile("der gezeigte Dialog steht im Protokoll (M-3)",
      "dialog_gezeigt" in inhalt or "dialog" in inhalt,
      gemessen=inhalt[-160:].replace("\n", " ") or "Protokoll leer")
zeile("und er nennt das Werkzeug",
      "Write" in inhalt, gemessen=inhalt[-160:].replace("\n", " "))

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
