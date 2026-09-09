"""Trockenlauf des 5.18-Stall-Pfads — ohne Telegram, ohne Claude.

Aufruf: .venv/bin/python scripts/test_stall_5_18.py

Simuliert eine hängende Session: ein Worker-Task, der ewig schläft, während
die Session kein Lebenszeichen mehr sendet. Geprüft wird, was der Wächter tut.
"""
import asyncio, os, sys, tempfile
from pathlib import Path

os.environ["TELEGRAM_BOT_TOKEN"] = ("0:test")
os.environ["ALLOWED_USER_IDS"] = "4242"  # erzwungen: hermetisch (nie geerbte echte UID)
os.environ["PENDING_DIR"] = tempfile.mkdtemp(prefix="pending-test-")
os.environ["STALL_LIMIT"] = "2"
os.environ["STALL_CHECK_INTERVAL"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bot, pending

SENT = []


class FakeBot:
    async def send_message(self, chat_id, text, **kw):
        SENT.append((chat_id, text))
        return None


class FakeClient:
    disconnected = False

    async def disconnect(self):
        FakeClient.disconnected = True


RESTARTED = []


async def main():
    uid = 4242
    # KEIN echter Claude-Start im Test (spart Abo-Kontingent und macht das
    # Ergebnis unabhängig davon, ob die CLI gerade erreichbar ist).
    # `[GEAENDERT 09.09.2026]` Die Attrappe spiegelt die ECHTE Signatur —
    # seit dem Schluesselwechsel nimmt der Worker Person UND Faden. Eine
    # nachsichtige Attrappe (`*args`) haette den Wechsel verschluckt.
    # **Block 1b:** sie merkt sich jetzt den FADEN mit. Vorher sammelte sie nur
    # die Person — damit war nicht messbar, WELCHES Zimmer geweckt wurde, und
    # genau dort lag der Fehler.
    bot._ensure_worker = lambda u, t=None: RESTARTED.append((u, t))
    key = pending.make_key(999, 1)
    pending.record(key, {"text": "haengende Frage", "status": pending.STATUS_OPEN,
                         "user_id": uid, "chat_id": 999})

    job = bot.QueuedJob(update=None, text="haengende Frage", user_id=uid,
                        chat_id=999, message_id=1, pending_key=key, bot=FakeBot())
    mb = bot._get_mailbox(uid)
    mb.current_job = job
    mb.current_started = bot.time.monotonic() - 600      # läuft seit 10 Min
    sess = bot.UserSession(client=FakeClient(), bot=FakeBot(), chat_id=999)
    sess.last_activity = bot.time.monotonic() - 600      # seit 10 Min stumm
    bot.SESSIONS[bot.faden(uid)] = sess

    async def haengt():
        await asyncio.sleep(3600)
    mb.worker = asyncio.create_task(haengt())

    # --- Fall 1: Freigabe steht aus → Wächter muss die Finger stillhalten ---
    sess.pending_permissions["req-1"] = (asyncio.get_running_loop(),
                                         asyncio.get_running_loop().create_future())
    wd = asyncio.create_task(bot.stall_watchdog(None))
    await asyncio.sleep(2.5)
    assert bot.SESSIONS.get(bot.faden(uid)) is sess, "FEHLER: Session trotz offener Freigabe gekillt"
    assert not SENT, "FEHLER: Meldung trotz offener Freigabe"
    print("✓ wartende Freigabe schützt die Session vor dem Wächter")

    # --- Fall 2: keine Freigabe offen → Stall muss greifen ---
    sess.pending_permissions.clear()
    await asyncio.sleep(2.5)
    wd.cancel()

    assert bot.SESSIONS.get(bot.faden(uid)) is None, "FEHLER: Session nicht entmachtet"
    print("✓ hängende Session aus SESSIONS entfernt")
    assert FakeClient.disconnected, "FEHLER: disconnect nicht aufgerufen"
    print("✓ disconnect angestoßen")
    assert mb.worker is None and mb.current_job is None, "FEHLER: Mailbox nicht aufgeräumt"
    print("✓ Worker abgebrochen, Mailbox aufgeräumt")
    assert len(mb.queue) == 1 and mb.queue[0] is job, "FEHLER: Job nicht wieder eingereiht"
    assert job.resumed and job.stall_retries == 1, "FEHLER: Job-Marker fehlen"
    print("✓ Nachricht wieder eingereiht (Versuch 1, Vermerk gesetzt)")
    rec = next((r for r in pending.load_all() if r.get("_key") == key), None)
    assert rec and rec["status"] == pending.STATUS_OPEN, "FEHLER: Persistenz-Status falsch"
    print("✓ Persistenz-Record steht wieder auf offen")
    assert RESTARTED == [(uid, None)], "FEHLER: Arbeit wird nicht wieder aufgenommen"
    print("✓ frischer Worker angeworfen (neue Session beim nächsten Job)")
    assert SENT and "nicht mehr reagiert" in SENT[0][1], "FEHLER: keine Meldung an Adam"
    assert "nochmal dran" in SENT[0][1], "FEHLER: Meldung nennt die Wiederaufnahme nicht"
    print("✓ Meldung an Adam:\n    " + SENT[0][1].replace("\n", "\n    "))

    # --- Fall 3: zweiter Stall an derselben Nachricht → nur noch melden ---
    SENT.clear()
    mb.queue.clear()
    mb.current_job = job
    mb.current_started = bot.time.monotonic() - 600
    sess2 = bot.UserSession(client=FakeClient(), bot=FakeBot(), chat_id=999)
    sess2.last_activity = bot.time.monotonic() - 600
    bot.SESSIONS[bot.faden(uid)] = sess2
    mb.worker = asyncio.create_task(haengt())
    await bot._handle_stalled_session(uid, mb, sess2, 600, thread_id=None)
    assert not mb.queue, "FEHLER: Job trotz Wiederholungsbremse erneut eingereiht"
    assert not pending.load_all(), "FEHLER: Record nicht aufgelöst"
    assert "nicht weiter" in SENT[0][1], "FEHLER: Meldung nennt das Aufgeben nicht"
    print("✓ zweiter Stall: keine Wiederholung, ehrliche Meldung:\n    "
          + SENT[0][1].replace("\n", "\n    "))

    # --- Fall 4: Session kam nie zustande (ensure_session hängt) ---
    # Lücke, die beim Vorbereiten des VPS-Tests auffiel: früher brach der
    # Wächter bei `sess is None` ab — ein Job, dessen Sitzung sich nie öffnet,
    # lief damit unbegrenzt weiter, und Adam fragte ins Leere. Für ihn ist das
    # derselbe Fall wie eine tote Session.
    SENT.clear()
    RESTARTED.clear()
    bot.SESSIONS.pop(bot.faden(uid), None)
    job2 = bot.QueuedJob(update=None, text="Frage ohne Sitzung", user_id=uid,
                         chat_id=999, message_id=2, bot=FakeBot())
    mb.queue.clear()
    mb.current_job = job2
    mb.current_started = bot.time.monotonic() - 600
    mb.worker = asyncio.create_task(haengt())
    wd2 = asyncio.create_task(bot.stall_watchdog(None))
    await asyncio.sleep(2.5)
    wd2.cancel()
    assert SENT and "nicht einmal starten" in SENT[0][1], \
        "FEHLER: hängender Session-Aufbau wird nicht erkannt"
    assert len(mb.queue) == 1 and mb.queue[0] is job2, "FEHLER: Job nicht gerettet"
    print("✓ hängender Session-AUFBAU wird erkannt:\n    "
          + SENT[0][1].replace("\n", "\n    "))

    # --- Fall 5: haengendes ZIMMER, keine Sitzung -- Block 1b ---
    #
    # Die Stelle, fuer die Block 1b gebaut wurde: Haengt der Aufbau, gibt es
    # keine Sitzung, die ihren Faden nennen koennte. Vorher las der Waechter den
    # Faden aus `sess` — bei `sess is None` war das der HAUPTFADEN. Also wurde
    # der Hauptfaden entmachtet und dessen Worker geweckt, waehrend das
    # haengende Zimmer unberuehrt liegen blieb.
    #
    # Gemessen wird beides: dass Zimmer 7 geweckt wird UND dass die
    # Hauptfaden-Sitzung ueberlebt.
    SENT.clear()
    RESTARTED.clear()
    bot.SESSIONS.clear()
    bot.MAILBOXES.clear()
    haupt = bot.UserSession(client=FakeClient(), bot=FakeBot(), chat_id=999)
    haupt.last_activity = bot.time.monotonic()          # quicklebendig
    bot.SESSIONS[bot.faden(uid)] = haupt
    mb7 = bot._get_mailbox(uid, 7)
    job7 = bot.QueuedJob(update=None, text="Frage aus Zimmer 7", user_id=uid,
                         chat_id=999, message_id=7, thread_id=7, bot=FakeBot())
    mb7.current_job = job7
    mb7.current_started = bot.time.monotonic() - 600
    mb7.worker = asyncio.create_task(haengt())
    wd3 = asyncio.create_task(bot.stall_watchdog(None))
    await asyncio.sleep(2.5)
    wd3.cancel()

    assert RESTARTED == [(uid, 7)], \
        f"FEHLER: falsches Zimmer geweckt — {RESTARTED!r} statt [({uid}, 7)]"
    print("✓ haengendes Zimmer 7 wird in SEINEM Faden neu angeworfen")
    assert bot.SESSIONS.get(bot.faden(uid)) is haupt, \
        "FEHLER: Hauptfaden-Sitzung wurde mit entmachtet"
    print("✓ die Sitzung des Hauptfadens bleibt unberuehrt")
    assert len(mb7.queue) == 1 and mb7.queue[0] is job7, \
        "FEHLER: Job aus Zimmer 7 nicht gerettet"
    print("✓ die Nachricht aus Zimmer 7 liegt wieder in Zimmer 7")

    print("\nALLE TEILPRÜFUNGEN BESTANDEN")


asyncio.run(main())
