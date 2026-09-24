#!/usr/bin/env python3
# <!-- ROLLE: test-zimmerliste -->
"""Zimmerliste aus dem Code — **ausgeführt** (Block 5, 24.09.2026).

Claudias Auftrag vom 13.09.: Adam legt Zimmer selbst an und benennt sie um,
aus dem Chat, ohne Deploy. Jede Zeile hier misst eine Bruchstelle aus ihrer
Tabelle:
  · Datei fehlt → Erstbefüllung; Datei beschädigt → eingebaute Liste, gemeldet
  · gleicher Name im selben Haus → Absage; im anderen Haus → Rückfrage
  · Umbenennen zieht Liste, Kennung UND Route nach — sonst Dublette oder Stille
  · scheitert das Schreiben, geht Telegram zurück (ein Vorgang)
  · nur Adam
Echter Code (`channels`, die Befehle im Bot); Attrappe nur für Telegram.
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_TMP = Path(tempfile.mkdtemp(prefix="zimmer-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["KANAELE_FILE"] = str(_TMP / "kanaele.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import channels                                                 # noqa: E402
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


DATEI = Path(os.environ["KANAELE_FILE"])

print("== Die Liste ist Daten ==")
DATEI.unlink(missing_ok=True)
zeile("ohne Datei gilt die Erstbefüllung — kein leerer Zustand",
      "Fanpost" in channels.zimmer_for("werkstatt") and not channels.beschaedigt())
zeile("Lesen legt keine Datei an (der Tagescheck läuft als root)", not DATEI.exists())
zeile("der Bot legt sie beim Start an", channels.erstbefuellen() and DATEI.exists())
d = json.loads(DATEI.read_text(encoding="utf-8"))
d["houses"]["werkstatt"]["zimmer"].append("Von Hand")
DATEI.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
zeile("eine Änderung in der Datei gilt ohne Deploy",
      "Von Hand" in channels.zimmer_for("werkstatt"))
DATEI.write_text("{kaputt", encoding="utf-8")
zeile("eine beschädigte Datei: es gilt die eingebaute Liste, und es wird gesagt",
      channels.beschaedigt() and channels.zimmer_for("werkstatt") == channels.HOUSES["werkstatt"]["zimmer"])
DATEI.unlink()
channels.erstbefuellen()


class _Tg:
    def __init__(self, scheitert=False):
        self.angelegt, self.umbenannt, self.geschlossen = [], [], []
        self.scheitert = scheitert

    async def create_forum_topic(self, chat_id, name):
        if self.scheitert:
            from telegram.error import TelegramError
            raise TelegramError("Forum nicht erreichbar")
        self.angelegt.append(name)
        return SimpleNamespace(message_thread_id=900 + len(self.angelegt))

    async def edit_forum_topic(self, chat_id, message_thread_id, name):
        self.umbenannt.append((message_thread_id, name))

    async def close_forum_topic(self, chat_id, message_thread_id):
        self.geschlossen.append(message_thread_id)


def _befehl(fn, args, tg, uid=4711):
    antworten = []

    async def _reply(text, **kw):
        antworten.append({"text": text, **kw})

    upd = SimpleNamespace(effective_user=SimpleNamespace(id=uid),
                          message=SimpleNamespace(reply_text=_reply))
    ctx = SimpleNamespace(args=args, bot=tg)
    asyncio.run(fn(upd, ctx))
    return antworten


# Häuser registriert, wie nach `_provision_house`
bot._USER_PREFS.clear()
channels.register_house(bot._USER_PREFS, "werkstatt", -100, "🔧 Werkstatt", True)
channels.register_house(bot._USER_PREFS, "bibliothek", -200, "📚 Bibliothek", True)
channels.record_topic(bot._USER_PREFS, "werkstatt", "Offene Punkte", 44)

print("== /zimmer_neu ==")
tg = _Tg()
a = _befehl(bot.cmd_zimmer_neu, ["Werkstatt", "Neues", "Zimmer"], tg)
zeile("ein Zimmer wird in Telegram angelegt und eingetragen",
      tg.angelegt == ["Neues Zimmer"] and "Neues Zimmer" in channels.zimmer_for("werkstatt")
      and bot._USER_PREFS["channels"]["houses"]["werkstatt"]["topics"].get("Neues Zimmer") == 901,
      gemessen=f"{tg.angelegt} {a}")
tg = _Tg()
a = _befehl(bot.cmd_zimmer_neu, ["werkstatt", "Neues", "Zimmer"], tg)
zeile("derselbe Name im selben Haus: Absage, kein Telegram-Aufruf",
      not tg.angelegt and a and a[0]["text"].startswith("❌"), gemessen=str(a))
tg = _Tg()
a = _befehl(bot.cmd_zimmer_neu, ["Bibliothek", "Fanpost"], tg)
zeile("derselbe Name in einem ANDEREN Haus: Rückfrage mit Knopf, noch nichts angelegt",
      not tg.angelegt and a and "reply_markup" in a[0] and "Sekretärin" in a[0]["text"],
      gemessen=str(a)[:160])
kennung = next(iter(bot._ZIMMER_RUECKFRAGEN))
bearbeitet = []


async def _antwort(*x, **k):
    return None


async def _edit(text=None, **kw):
    bearbeitet.append(text)

q = SimpleNamespace(data=f"zn:{kennung}:ja", answer=_antwort,
                    message=SimpleNamespace(text="⚠️ …"), edit_message_text=_edit)
asyncio.run(bot.on_zimmer_knopf(SimpleNamespace(callback_query=q,
                                                effective_user=SimpleNamespace(id=4711)),
                                SimpleNamespace(bot=tg)))
zeile("„Ja, anlegen“ legt es danach an", tg.angelegt == ["Fanpost"]
      and "Fanpost" in channels.zimmer_for("bibliothek"), gemessen=str(bearbeitet))
tg = _Tg(scheitert=True)
a = _befehl(bot.cmd_zimmer_neu, ["Werkstatt", "Geht", "nicht"], tg)
zeile("lehnt Telegram ab, wird nichts eingetragen (keine Lücke für eine Dublette)",
      "Geht nicht" not in channels.zimmer_for("werkstatt") and a[0]["text"].startswith("❌"),
      gemessen=str(a))
tg = _Tg()
a = _befehl(bot.cmd_zimmer_neu, ["Werkstatt", "Fremd"], tg, uid=999)
zeile("nur Adam", not tg.angelegt and not a and "Fremd" not in channels.zimmer_for("werkstatt"))

print("== /zimmer_umbenennen ==")
vorher_route = channels.resolve_route(bot._USER_PREFS, "unassigned")
tg = _Tg()
a = _befehl(bot.cmd_zimmer_umbenennen, "Offene Punkte | Offene Fäden".split(" "), tg)
topics = bot._USER_PREFS["channels"]["houses"]["werkstatt"]["topics"]
zeile("Telegram-Thema umbenannt, dieselbe Kennung", tg.umbenannt == [(44, "Offene Fäden")],
      gemessen=str(tg.umbenannt))
zeile("die Liste trägt den neuen Namen",
      "Offene Fäden" in channels.zimmer_for("werkstatt")
      and "Offene Punkte" not in channels.zimmer_for("werkstatt"))
zeile("die Kennung wandert mit — sonst legte der nächste Durchlauf eine Dublette an",
      topics.get("Offene Fäden") == 44 and "Offene Punkte" not in topics
      and "Offene Fäden" not in channels.missing_zimmer(bot._USER_PREFS, "werkstatt"),
      gemessen=str(topics))
zeile("die Route zieht mit und trifft weiter — sonst bliebe es still",
      channels.resolve_route(bot._USER_PREFS, "unassigned") == vorher_route == (-100, 44)
      and channels.routen_pruefen() == [],
      gemessen=f"{channels.resolve_route(bot._USER_PREFS, 'unassigned')} {channels.routen_pruefen()}")

tg = _Tg()
_echt = channels.speichern
channels.speichern = lambda d: (_ for _ in ()).throw(OSError("Platte voll"))
try:
    a = _befehl(bot.cmd_zimmer_umbenennen, "Offene Fäden | Kaputt".split(" "), tg)
finally:
    channels.speichern = _echt
zeile("scheitert das Schreiben, geht Telegram zurück — ein Vorgang",
      tg.umbenannt == [(44, "Kaputt"), (44, "Offene Fäden")]
      and "Offene Fäden" in channels.zimmer_for("werkstatt")
      and topics.get("Offene Fäden") == 44, gemessen=f"{tg.umbenannt} {a}")

print("== Routen prüfen ==")
d = json.loads(DATEI.read_text(encoding="utf-8"))
d["routes"]["research"] = ["bibliothek", "Gibt es nicht"]
DATEI.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
zeile("eine Route ins Leere wird gefunden",
      any("Gibt es nicht" in k for k in channels.routen_pruefen()), gemessen=str(channels.routen_pruefen()))

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Zimmerliste bestanden.")
