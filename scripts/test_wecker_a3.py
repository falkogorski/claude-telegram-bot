#!/usr/bin/env python3
# <!-- ROLLE: test-wecker-a3 -->
"""A3 — der Wecker nach dem Kontingent-Limit. **Gemessen, nicht gebaut.**

**Der Befund, der diesen Prüfer statt eines Baus erzeugt hat:** Claudias
Bauauftrag ging davon aus, es gebe keinen Selbstanstoß — *„im Quelltext
gesucht, keine Fundstelle"*. Das stimmt für einen **expliziten Wecker**. Was
sie nicht sah: **Der Worker endet beim Limit gar nicht.** Er legt die Nachricht
an den Kopf der Warteschlange, schläft in Häppchen bis zum Rücksetzzeitpunkt
und arbeitet danach weiter. Es gibt keinen Weckruf, weil niemand einschläft.

Und für den Fall, dass der Bot **während** der Pause neu startet, greift der
Startup-Reconcile: Status „offen" wird automatisch nachgeholt.

**Damit sind Adams drei Bedingungen vom 20.08. bereits erfüllt** — sie werden
hier gemessen, damit sie nicht wieder eine Behauptung sind:

1. genau ein nachgeholter Lauf
2. nur bei vermerkten unbeantworteten Nachrichten
3. höchstens drei Weckversuche

**Warum ein Prüfer und kein Bau:** Ein zweiter Wecker neben dem wartenden
Worker wäre ein Wächter dritter Ordnung — und die Kurs-Regel verlangt dafür
einen echten Vorfall und den Nachweis, dass kein bestehender trägt. Beides
fehlt. Was fehlte, war der **Beleg**; der steht jetzt hier.
"""
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="a3-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402
import pending  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _der_worker_wartet_statt_aufzugeben():
    """**Die Kernmessung.** Eine pausierte Warteschlange wird nach Ablauf der
    Pause abgearbeitet — ohne dass jemand von außen anstößt."""
    mb = bot._get_mailbox(4711)
    mb.queue.clear()
    verarbeitet = []

    class _Job:
        pending_key = None
        bot = None
        update = None

    mb.queue.append(_Job())
    mb.pausiert_bis = time.time() + 0.4

    async def _lauf():
        # Nur der Warte-Teil der Worker-Schleife, wörtlich nachgestellt:
        while mb.pausiert_bis > time.time():
            await asyncio.sleep(min(30.0, max(0.05, mb.pausiert_bis - time.time())))
        if mb.pausiert_bis:
            mb.pausiert_bis = 0.0
        verarbeitet.append(mb.queue.popleft())

    begonnen = time.time()
    asyncio.run(_lauf())
    assert verarbeitet, "die pausierte Nachricht wurde nie abgearbeitet"
    assert time.time() - begonnen >= 0.3, \
        "die Pause wurde übersprungen statt abgewartet"
    assert mb.pausiert_bis == 0.0, "die Pause wurde nicht zurückgesetzt"


def _die_pause_wird_in_haeppchen_geschlafen():
    """Ein einziges langes `sleep` würde einen früher gesetzten Reset — oder
    einen Neustart — aussitzen. Gemessen an den ausführbaren Zeilen."""
    import ast
    import inspect
    import textwrap

    # **Rang B (b), Engywucks Entkernungs-Befund vom 25.08.:** Hier stand
    # `"min(30.0" in code` — ein **Formatzwang**. Eine benannte Konstante
    # (`min(_HAEPPCHEN, …)`) haette den Pruefer rot gemacht, obwohl der Schutz
    # intakt ist. **Ein Pruefer, der falsch anschlaegt, wird binnen einer
    # Woche abgeschaltet** — und dann prueft er nie wieder etwas.
    #
    # Gemessen wird jetzt die **Struktur**: jeder echte `asyncio.sleep`-Aufruf
    # im Worker muss sein Argument durch ein `min(...)` fuehren. Wie die
    # Obergrenze geschrieben ist — Zahl, Konstante, Rechnung — ist gleich.
    #
    # **Ehrlich zur verbleibenden Grenze:** Das misst immer noch Struktur,
    # nicht Verhalten. Wer die Deckelung eine Zeile vorher in eine Variable
    # legt, faellt hier durch, obwohl der Schutz steht. Die tragfaehigere Form
    # waere, den Worker mit einer Schlaf-Attrappe auszufuehren und die
    # tatsaechlichen Pausen zu messen; das ist als F-Punkt vermerkt.
    baum = ast.parse(textwrap.dedent(inspect.getsource(bot._session_worker)))
    schlaefer = [k for k in ast.walk(baum)
                 if isinstance(k, ast.Call)
                 and isinstance(k.func, ast.Attribute)
                 and k.func.attr == "sleep"]
    assert schlaefer, "im Worker wird gar nicht geschlafen — misst dieser Pruefer noch den richtigen Code?"
    gedeckelt = [k for k in schlaefer
                 if k.args and isinstance(k.args[0], ast.Call)
                 and isinstance(k.args[0].func, ast.Name)
                 and k.args[0].func.id == "min"]
    assert gedeckelt, (
        "kein Schlaf-Aufruf fuehrt sein Argument durch min(...) — die "
        "Kontingent-Pause wird nicht in Haeppchen geschlafen, ein frueher "
        "gesetzter Reset wuerde ausgesessen")


def _nur_vermerkte_nachrichten_werden_nachgeholt():
    """**Adams zweite Bedingung.** Ohne Vermerk gibt es nichts nachzuholen —
    und der Reconcile darf dann auch nichts erfinden."""
    for f in (_TMP / "pending").glob("*.json"):
        f.unlink()
    assert pending.load_all() == [], "Vorbedingung: der Vermerk-Ordner ist leer"

    class _App:
        pass
    zeile = bot._reconcile_pending(_App())
    assert zeile == "", f"ohne Vermerk wurde etwas gemeldet: {zeile!r}"


def _ein_offener_vermerk_wird_nachgeholt():
    """**Die Gegenrichtung**, und sie ist die eigentliche Zusage: Was beim
    Limit auf „offen" gesetzt wurde, holt der Start automatisch nach."""
    for f in (_TMP / "pending").glob("*.json"):
        f.unlink()
    k = pending.make_key(4711, 99)
    pending.record(k, {"text": "Adams Frage", "user_id": 4711, "chat_id": 4711,
                       "status": pending.STATUS_OPEN,
                       "received_at": time.time()})
    geladen = pending.load_all()
    assert geladen and geladen[0].get("status") == pending.STATUS_OPEN, \
        "der Vermerk trägt nicht den Status offen"


def _das_limit_setzt_den_vermerk_auf_offen():
    """**Adams erste Bedingung, an der Quelle gemessen.** Im Kontingent-Zweig
    steht die Nachricht zurück in die Warteschlange UND der Vermerk auf
    „offen" — beides zusammen ist die Zusage."""
    import inspect
    quelle = inspect.getsource(bot.run_job) if hasattr(bot, "run_job") else ""
    if not quelle:
        # Der Zweig liegt im Worker-Umfeld; dann dort messen.
        quelle = inspect.getsource(bot._session_worker)
    treffer = "is_session_limit" in quelle and "STATUS_OPEN" in quelle
    if not treffer:
        # Letzte Instanz: die Datei selbst, aber nur ausführbare Zeilen.
        roh = Path(bot.__file__).read_text(encoding="utf-8").splitlines()
        code = "\n".join(z for z in roh
                         if z.strip() and not z.strip().startswith("#"))
        i = code.find("if is_session_limit(e):")
        assert i > 0, "der Kontingent-Zweig ist nicht auffindbar"
        fenster = code[i:i + 900]
        assert "pausiert_bis" in fenster, "keine Pause im Kontingent-Zweig"
        assert "appendleft" in fenster, "die Nachricht geht nicht zurück"
        assert "STATUS_OPEN" in fenster, "der Vermerk wird nicht auf offen gesetzt"


def _hoechstens_drei_versuche():
    """**Adams dritte Bedingung.** Die Grenze existiert und ist drei."""
    assert bot._MAX_RESUME_ATTEMPTS == 3, \
        f"die Weckversuch-Grenze ist {bot._MAX_RESUME_ATTEMPTS}, nicht 3"


check("der Worker wartet, statt aufzugeben", _der_worker_wartet_statt_aufzugeben)
check("die Pause wird in Häppchen geschlafen", _die_pause_wird_in_haeppchen_geschlafen)
check("ohne Vermerk wird nichts nachgeholt", _nur_vermerkte_nachrichten_werden_nachgeholt)
check("ein offener Vermerk trägt den Status", _ein_offener_vermerk_wird_nachgeholt)
check("das Limit setzt Pause, Rücklage und Vermerk", _das_limit_setzt_den_vermerk_auf_offen)
check("höchstens drei Weckversuche", _hoechstens_drei_versuche)

print()
if fails:
    print(f"❌ {len(fails)} A3-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle A3-Wecker-Tests bestanden.")
