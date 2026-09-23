#!/usr/bin/env python3
# <!-- ROLLE: test-sammelnachricht -->
"""Die Sammelnachricht für Freigaben wird **ausgeführt**, nicht gelesen.

**Adams Form (24.09.2026, 00:0x):** „neu senden, alt kürzen". Jede neue
Anfrage kommt als neue Nachricht mit Ton und trägt alle offenen Anfragen des
Zimmers; die vorige schrumpft auf Protokollzeilen. **Ein Daumen entscheidet
nur, wenn genau eine Anfrage offen ist.**

Echter Code in der Mitte: `make_permission_callback`, `on_permission_callback`,
`on_reaction`. Attrappen nur an den Rändern — Telegram (Senden, Bearbeiten)
und der Druck auf Knopf oder Daumen.

Drei Teile, weil es drei Fälle gibt:
  A. nacheinander — der gemessene Normalfall (93 Dialoge, keiner gleichzeitig)
  B. gleichzeitig — zwei offene Anfragen in einem Zimmer
  C. Erinnerung — bei mehreren offenen mahnt nur die älteste
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_TMP = Path(tempfile.mkdtemp(prefix="sammel-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
os.environ["QUESTIONS_FILE"] = str(_TMP / "open_questions.json")
os.environ["BASHFREI_HEIM"] = str(_TMP)
os.environ["BASHFREI_PROTOKOLL"] = str(_TMP / "bashfreigabe.jsonl")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from telegram import ReactionTypeEmoji                          # noqa: E402
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


class _BotAttrappe:
    """Telegram, soweit der Freigabeweg es braucht. Senden liefert eine
    fortlaufende Kennung wie die echte API; Bearbeiten wird mitgeschrieben."""

    def __init__(self):
        self.gesendet: list[dict] = []
        self.bearbeitet: list[dict] = []

    async def send_message(self, **kw):
        self.gesendet.append(kw)
        return SimpleNamespace(message_id=1000 + len(self.gesendet))

    async def edit_message_text(self, **kw):
        self.bearbeitet.append(kw)


def _knopfdaten(kw: dict) -> list[str]:
    tast = kw.get("reply_markup")
    if tast is None:
        return []
    return [k.callback_data for reihe in tast.inline_keyboard for k in reihe]


def _letzte_bearbeitung(attrappe, mid):
    for kw in reversed(attrappe.bearbeitet):
        if kw.get("message_id") == mid:
            return kw
    return None


def _zimmer(thread_id=None):
    sess = bot.UserSession(client=None, chat_id=999)
    sess.bot = _BotAttrappe()
    sess.thread_id = thread_id
    bot.SESSIONS.clear()
    bot.SESSIONS[bot.faden(UID, thread_id)] = sess
    return sess


async def _warte_bis(bedingung, schritte=300):
    for _ in range(schritte):
        if bedingung():
            return True
        await asyncio.sleep(0.01)
    return False


def _anfrage(nr: int) -> dict:
    return {"file_path": str(_TMP / f"ziel{nr}.txt"), "content": "x"}


async def _knopf(sess, rid: str, entscheid: str, mid: int):
    """Adams Knopfdruck, durch den ECHTEN `on_permission_callback`."""
    bearbeitet_q: list = []

    async def _antwort(*a, **k):
        return None

    async def _q_edit(**kw):
        bearbeitet_q.append(kw)

    q = SimpleNamespace(data=f"p:{rid}:{entscheid}", answer=_antwort,
                        message=SimpleNamespace(message_id=mid, text=""),
                        edit_message_text=_q_edit)
    upd = SimpleNamespace(effective_user=SimpleNamespace(id=UID),
                          callback_query=q)
    await bot.on_permission_callback(upd, None)
    return bearbeitet_q


async def _daumen(emoji: str, mid: int):
    rx = SimpleNamespace(chat=SimpleNamespace(id=999),
                         user=SimpleNamespace(id=UID), message_id=mid,
                         old_reaction=[],
                         new_reaction=[ReactionTypeEmoji(emoji=emoji)])
    await bot.on_reaction(SimpleNamespace(message_reaction=rx), None)


async def teil_a():
    print("== A. nacheinander — der gemessene Normalfall ==")
    sess = _zimmer()
    tg = sess.bot
    rueckruf = bot.make_permission_callback(UID, None)

    t1 = asyncio.create_task(rueckruf("Write", _anfrage(1), None))
    await _warte_bis(lambda: sess.pending_permissions and tg.gesendet)
    rid1 = next(iter(sess.pending_permissions))
    m1 = 1001
    erst = tg.gesendet[0] if tg.gesendet else {}
    zeile("eine Anfrage sieht aus wie bisher (Kopf, Klartext, zwei Knöpfe)",
          str(erst.get("text", "")).startswith("🔐 Genehmigungs-Anfrage\n\n✏️")
          and _knopfdaten(erst)[:2] == [f"p:{rid1}:allow", f"p:{rid1}:deny"],
          gemessen=repr(str(erst.get("text", ""))[:60]))

    await _knopf(sess, rid1, "allow", m1)
    erg1 = await t1
    zeile("Genehmigen heißt erlaubt",
          type(erg1).__name__ == "PermissionResultAllow",
          gemessen=type(erg1).__name__)
    b1 = _letzte_bearbeitung(tg, m1) or {}
    zeile("die beantwortete Nachricht trägt die Quittung und keine Knöpfe mehr",
          str(b1.get("text", "")).endswith("→ ✅ Genehmigt")
          and b1.get("reply_markup") is None,
          gemessen=repr(str(b1.get("text", ""))[-30:]))

    t2 = asyncio.create_task(rueckruf("Write", _anfrage(2), None))
    await _warte_bis(lambda: len(tg.gesendet) >= 2)
    zeile("die nächste Anfrage kommt als NEUE Nachricht (mit Ton)",
          len(tg.gesendet) == 2, gemessen=f"{len(tg.gesendet)} gesendet")
    zweite = tg.gesendet[1] if len(tg.gesendet) > 1 else {}
    zeile("und sie trägt nur sich selbst — die erledigte zieht nicht mit",
          str(zweite.get("text", "")).startswith("🔐 Genehmigungs-Anfrage\n\n")
          and "offen" not in str(zweite.get("text", "")).split("\n")[0],
          gemessen=repr(str(zweite.get("text", ""))[:60]))
    k1 = _letzte_bearbeitung(tg, m1) or {}
    ktext = str(k1.get("text", ""))
    zeile("die vorige schrumpft auf EINE Protokollzeile mit ihrem Entscheid",
          ktext.count("\n") == 0 and ktext.startswith("🔐 ✏️")
          and ktext.endswith("→ ✅ Genehmigt") and k1.get("reply_markup") is None,
          gemessen=repr(ktext[:80]))

    rid2 = next(iter(sess.pending_permissions))
    await _daumen("👍", 1002)
    erg2 = await asyncio.wait_for(t2, 2)
    zeile("bei genau einer offenen Anfrage entscheidet der Daumen wie bisher",
          type(erg2).__name__ == "PermissionResultAllow",
          gemessen=type(erg2).__name__)
    b2 = _letzte_bearbeitung(tg, 1002) or {}
    zeile("und nach dem Daumen verschwinden die Knöpfe (bisher blieben sie)",
          b2.get("reply_markup") is None
          and str(b2.get("text", "")).endswith("→ ✅ Genehmigt"),
          gemessen=repr(str(b2.get("text", ""))[-30:]))
    _ = rid2


async def teil_b():
    print("== B. gleichzeitig — zwei offene Anfragen in einem Zimmer ==")
    sess = _zimmer(thread_id=7)
    tg = sess.bot
    rueckruf = bot.make_permission_callback(UID, 7)

    t1 = asyncio.create_task(rueckruf("Write", _anfrage(1), None))
    await _warte_bis(lambda: len(tg.gesendet) >= 1)
    t2 = asyncio.create_task(rueckruf("Write", _anfrage(2), None))
    await _warte_bis(lambda: len(tg.gesendet) >= 2)
    rids = list(sess.pending_permissions)
    zeile("jede Anfrage ist eine eigene Sendung — zwei Anfragen, zwei Töne",
          len(tg.gesendet) == 2, gemessen=f"{len(tg.gesendet)} gesendet")
    zweite = tg.gesendet[1] if len(tg.gesendet) > 1 else {}
    daten = _knopfdaten(zweite)
    zeile("die neue Nachricht trägt BEIDE offenen Anfragen, je mit Nummer",
          str(zweite.get("text", "")).startswith("🔐 2 Genehmigungs-Anfragen offen")
          and len(rids) == 2
          and all(f"p:{r}:allow" in daten and f"p:{r}:deny" in daten
                  for r in rids),
          gemessen=f"{str(zweite.get('text', ''))[:40]!r} {daten}")
    zeile("sie steht im Zimmer, nicht im General",
          all(g.get("message_thread_id") == 7 for g in tg.gesendet),
          gemessen=str([g.get("message_thread_id") for g in tg.gesendet]))
    zeile("in einer Sammlung gibt es keine Knöpfe für Dauer-Freigaben",
          not any(":always:" in d or ":domain:" in d for d in daten),
          gemessen=str(daten))
    k1 = _letzte_bearbeitung(tg, 1001) or {}
    zeile("die erste Nachricht schrumpft und sagt, wo die Anfrage jetzt steht",
          "offen, steht in der neuen Nachricht darunter" in str(k1.get("text", ""))
          and k1.get("reply_markup") is None,
          gemessen=repr(str(k1.get("text", ""))[:80]))

    await _daumen("👍", 1001)
    await asyncio.sleep(0.02)
    zeile("ein Daumen auf der gekürzten Nachricht entscheidet nichts",
          not t1.done() and not t2.done() and len(sess.pending_permissions) == 2,
          gemessen=f"offen: {len(sess.pending_permissions)}")

    vorher = len(tg.gesendet)
    await _daumen("👍", 1002)
    await asyncio.sleep(0.02)
    zeile("bei zwei offenen entscheidet der Daumen NICHTS (Glied 8)",
          not t1.done() and not t2.done() and len(sess.pending_permissions) == 2,
          gemessen=f"offen: {len(sess.pending_permissions)}, "
                   f"t1 fertig: {t1.done()}, t2 fertig: {t2.done()}")
    hinweis = tg.gesendet[vorher:] if len(tg.gesendet) > vorher else []
    zeile("und der Bot sagt, warum — als Antwort auf die Sammelnachricht",
          len(hinweis) == 1 and "mehr als eine Anfrage offen" in hinweis[0]["text"]
          and hinweis[0].get("reply_to_message_id") == 1002,
          gemessen=str([h.get("text", "")[:40] for h in hinweis]))

    await _knopf(sess, rids[0], "allow", 1002)
    erg1 = await asyncio.wait_for(t1, 2)
    zeile("der Knopf mit der Nummer entscheidet genau seine Anfrage",
          type(erg1).__name__ == "PermissionResultAllow" and not t2.done(),
          gemessen=f"{type(erg1).__name__}, t2 fertig: {t2.done()}")
    b = _letzte_bearbeitung(tg, 1002) or {}
    bd = _knopfdaten(b)
    zeile("danach zeigt die Nachricht die erledigte als Zeile, Knöpfe nur noch für die offene",
          "→ ✅ Genehmigt" in str(b.get("text", ""))
          and not any(rids[0] in d for d in bd)
          and f"p:{rids[1]}:allow" in bd,
          gemessen=f"{str(b.get('text', ''))[:60]!r} {bd}")

    await _daumen("👎", 1002)
    erg2 = await asyncio.wait_for(t2, 2)
    zeile("ist nur noch eine offen, entscheidet der Daumen wieder",
          type(erg2).__name__ == "PermissionResultDeny",
          gemessen=type(erg2).__name__)


async def teil_c():
    print("== C. Erinnerung — nur die älteste mahnt ==")
    sess = _zimmer()
    tg = sess.bot
    alt_takt, alt_frist = bot.FREIGABE_ERINNERUNG_S, bot.FREIGABE_FRIST_S
    bot.FREIGABE_ERINNERUNG_S, bot.FREIGABE_FRIST_S = 0.1, 60
    try:
        rueckruf = bot.make_permission_callback(UID, None)
        t1 = asyncio.create_task(rueckruf("Write", _anfrage(1), None))
        await _warte_bis(lambda: len(tg.gesendet) >= 1)
        t2 = asyncio.create_task(rueckruf("Write", _anfrage(2), None))
        await _warte_bis(lambda: len(tg.gesendet) >= 2)
        await asyncio.sleep(0.35)
        mahnungen = [g for g in tg.gesendet if str(g.get("text", "")).startswith("⏳")]
        # Ohne die Regel mahnten beide: rund sechs statt drei.
        zeile("bei zwei offenen mahnt nur eine (nicht jede für sich)",
              1 <= len(mahnungen) <= 4,
              gemessen=f"{len(mahnungen)} Mahnungen")
        zeile("die Mahnung zählt die offenen und zeigt auf die Sammelnachricht",
              mahnungen and all("2 Freigaben warten" in m["text"]
                                and m.get("reply_to_message_id") == 1002
                                for m in mahnungen),
              gemessen=str([(m["text"][:25], m.get("reply_to_message_id"))
                            for m in mahnungen]))
    finally:
        bot.FREIGABE_ERINNERUNG_S, bot.FREIGABE_FRIST_S = alt_takt, alt_frist
        for t in (t1, t2):
            t.cancel()
        await asyncio.gather(t1, t2, return_exceptions=True)


async def main():
    await teil_a()
    await teil_b()
    await teil_c()


asyncio.run(main())

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Sammelnachricht bestanden.")
