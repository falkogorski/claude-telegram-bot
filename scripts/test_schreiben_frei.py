#!/usr/bin/env python3
# <!-- ROLLE: test-schreiben-frei -->
"""Schreiben im Arbeitsordner — seit 23.09. Teil des Auto-Knopfs.

**Ausgeführt, nicht gelesen.** Gemessen wird die Entscheidung
(`schreiben_ohne_frage`), der Weg über den Knopf und — die Zeile, auf die es
ankommt — das Verhalten **nach einem Prozessstart**, in einem eigenen Prozess.

**Die Zusage hat sich am 23.09. umgekehrt, und dieser Prüfer mit ihr.** Bis
dahin lebte die Freigabe nur im Speicher, und Zeile 4 maß, dass sie den
Neustart **nicht** überlebt. Gemessen am 21.09. war genau das der Fehler: Die
Sitzung begann um 04:30 ohne Freigabe, zwei Schreib-Dialoge warteten je eine
Stunde ins Leere. **Adams Entscheid:** Der Auto-Zustand trägt Bash **und**
Schreiben im Arbeitsordner und liegt dauerhaft in den Vorlieben. Zeile 4 misst
jetzt das Gegenteil — umgestellt, nicht gelöscht, weil die Zusage dahinter
weiter besteht, nur in anderer Richtung.

**Der Ausgleich für die Dauer sind die harten Grenzen** (Zeile 3). Sie sind
deshalb einzeln gemessen, jede mit einem Fall, den NUR ihr Riegel fängt —
sonst misst man die Summe und hält sie für den Einzelnen (Lehre vom 11.09.).
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# `.resolve()`: Auf dem Mac liegt `/var` hinter einem Symlink auf
# `/private/var` — ohne das misst der Prüfstand den Symlink statt der Sache.
_TMP = Path(tempfile.mkdtemp(prefix="schreibfrei-")).resolve()
_ARBEIT = _TMP / "workspace"
_ARBEIT.mkdir()
_PREFS = _TMP / "prefs.json"
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_PREFS)
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
_WERKZEUGE = ("Write", "Edit", "MultiEdit")
_drin = str(_ARBEIT / "papier.md")
print("== Schreiben im Arbeitsordner (Auto-Knopf) ==")

# ── 1. Auto an: eine Aenderung im Arbeitsordner laeuft ohne Frage ───────────
bot._set_bash_auto(UID, True)
_erlaubt = [w for w in _WERKZEUGE if bot.schreiben_ohne_frage(UID, w, _drin)]
zeile("Auto an: Write, Edit und MultiEdit laufen im Arbeitsordner durch",
      _erlaubt == list(_WERKZEUGE), gemessen=f"erlaubt: {_erlaubt}")

# ── 2. Auto aus: dieselbe Aenderung fragt ───────────────────────────────────
bot._set_bash_auto(UID, False)
_ohne = [w for w in _WERKZEUGE if bot.schreiben_ohne_frage(UID, w, _drin)]
zeile("Auto aus: jede Aenderung fragt wieder",
      _ohne == [], gemessen=f"trotzdem erlaubt: {_ohne}")

# ── 3. Trotz Auto: die harten Grenzen, einzeln ──────────────────────────────
# Seit der Zustand dauerhaft ist, sind sie der ganze Ausgleich. Jede steht mit
# einem Fall da, den nur sie faengt.
bot._set_bash_auto(UID, True)
_gesperrt = {
    "Repo-Klon": str(Path.home() / "claude-telegram-bot/bot.py"),
    "Gedaechtnis": str(Path.home() / ".claude/memory/MEMORY.md"),
    "Geheimnis": str(_ARBEIT / ".env"),
    # Neu 23.09.: Die Rechnungs-Stammdaten liegen UNTER dem Arbeitsordner.
    # Nur der Geheimnis-Riegel haelt sie -- der Arbeitsordner-Riegel liesse
    # sie durch. Deshalb ein eigener Fall.
    "Stammdaten": str(_ARBEIT / "rechnungen/daten/stammdaten.json"),
    "ausserhalb": str(_TMP / "woanders/datei.md"),
    "einer von zweien draussen": f"{_drin}\n{Path.home()}/.claude/memory/x.md",
    # Der ..-Weg, zweimal: das erste Ziel faengt schon der Geheimnis-Riegel,
    # das zweite NUR die Pfadaufloesung (gemessen am 11.09.).
    "ueber .. ins Gedaechtnis": str(_ARBEIT) + "/../.claude/memory/x.md",
    "ueber .. nach nebenan": str(_ARBEIT) + "/../nebenan/datei.md",
}
_durch = [n for n, pfad in _gesperrt.items()
          if bot.schreiben_ohne_frage(UID, "Write", pfad)]
zeile("trotz Auto bleiben Repo, Gedaechtnis, Geheimnis, Stammdaten und Draussen gesperrt",
      not _durch, gemessen=f"durchgerutscht: {_durch}")

# ── 4. Nach einem Prozessstart gilt Auto weiter — in einem EIGENEN Prozess ──
# **Engywucks "Gut genug wenn" fuer Block 1, woertlich:** Eine Sitzung nach
# 04:00 mit Auto an fragt fuer kein Write/Edit unter ~/workspace; ein Write
# nach ~/.claude/memory fragt weiterhin. Der frische Prozess liest dieselbe
# Vorlieben-Datei, die der Hygiene-Neustart vorfinden wuerde.
bot._set_bash_auto(UID, True)
_gespeichert = json.loads(_PREFS.read_text(encoding="utf-8")) if _PREFS.exists() else {}
_prog = (
    "import sys\n"
    f"sys.path.insert(0, {str(Path(__file__).resolve().parent.parent)!r})\n"
    "import bot\n"
    "print('AUTO=' + str(bot._bash_auto_on(4711)))\n"
    f"print('ARBEIT=' + str(bot.schreiben_ohne_frage(4711, 'Write', {_drin!r})))\n"
    f"print('GEDAECHTNIS=' + str(bot.schreiben_ohne_frage(4711, 'Write', "
    f"{str(Path.home() / '.claude/memory/MEMORY.md')!r})))\n")
_r = subprocess.run([sys.executable, "-c", _prog], capture_output=True, text=True,
                    env=dict(os.environ))
zeile("nach einem Prozessstart: Arbeitsordner frei, Gedaechtnis fragt weiter",
      "AUTO=True" in _r.stdout and "ARBEIT=True" in _r.stdout
      and "GEDAECHTNIS=False" in _r.stdout,
      gemessen=(_r.stdout.strip().replace("\n", " ") or _r.stderr.strip()[-200:])
               + f" | Vorlieben: {_gespeichert.get(str(UID), {}).get('always_allow')}")


# ── 5. Der alte Schreib-Knopf: nicht mehr gezeichnet, aber noch bekannt ─────
# Telegram-Tastaturen leben client-seitig weiter. Ist die alte Beschriftung
# unbekannt, geht ein Druck darauf als FRAGE an Claudia (der Knopf-Bug vom
# 23.07.). Deshalb: nicht gezeichnet, aber in der Menge bekannter Knoepfe.
def _knoepfe():
    return [b.text for row in
            bot._main_keyboard(False, "sonnet", None, user_id=UID).keyboard
            for b in row]


_alle = set()
for _an in (True, False):
    bot._set_bash_auto(UID, _an)
    _alle.update(_knoepfe())
_alt = {bot._BTN_SCHREIBEN_TO_FREI, bot._BTN_SCHREIBEN_TO_FRAGEN}
zeile("der alte Schreib-Knopf wird nicht mehr gezeichnet, ist aber noch bekannt",
      not (_alt & _alle) and _alt <= bot._ALL_KEYBOARD_BTNS,
      gemessen=f"gezeichnet: {_alt & _alle}, bekannt: {_alt <= bot._ALL_KEYBOARD_BTNS}")


# ── 6. Ein Druck auf den alten Knopf schaltet NICHTS und antwortet ──────────
# Ausgefuehrt ueber den echten Tastatur-Zweig. Ein Knopf, den es nicht mehr
# gibt, darf keinen Zustand mehr aendern -- sonst schaltete die alte Tastatur
# still den neuen Auto-Zustand um.
class _Msg:
    def __init__(self, text):
        self.text = text
        self.message_thread_id = None
        self.antworten: list[str] = []

    async def reply_text(self, text, **_kw):
        self.antworten.append(text)


class _Upd:
    def __init__(self, text):
        self.effective_user = type("U", (), {"id": UID})()
        self.effective_chat = type("C", (), {"id": UID})()
        self.message = _Msg(text)
        self.effective_message = self.message


async def _druecken(text):
    u = _Upd(text)
    await bot._handle_keyboard_btn(u, text)
    return u.message.antworten


_ergebnis = []
for _vorher in (True, False):
    for _knopf in _alt:
        bot._set_bash_auto(UID, _vorher)
        _antw = asyncio.run(_druecken(_knopf))
        _ergebnis.append((_vorher, bot._bash_auto_on(UID), bool(_antw)))
zeile("ein Druck auf den alten Knopf aendert Auto nicht und bekommt eine Antwort",
      all(v == n and a for v, n, a in _ergebnis),
      gemessen=f"(vorher, nachher, geantwortet): {_ergebnis}")


# ── 7. Im ECHTEN Rueckruf, nicht nur die Funktion ───────────────────────────
# **Beim Bau gefunden:** Die Zeilen 1 bis 4 messen `schreiben_ohne_frage` fuer
# sich. Die Gegenprobe „Arbeitsordner-Riegel entfernen" liess dort den
# Repo-Klon durch -- weil der Repo-Schutz fuer Write/Edit gar nicht in dieser
# Funktion sitzt, sondern als **harter Deny oben im Rueckruf**
# (`_ist_repo_bezug`), weit vor dem Schreib-Zweig. Die Uebergabe nahm an,
# `_is_sensitive_ref` halte das Repo; das stimmt fuer `CLAUDE.md`, nicht fuer
# `bot.py`. **Im Ergebnis bleibt das Repo hart -- aber nur der Rueckruf zeigt
# es.** Eine Funktion zu messen, ohne ihren Aufrufer zu fahren, ist die Lehre
# vom 22.08.: Fabrik ja, Aufrufer nein.
#
# Gefahren wird deshalb `make_permission_callback`, Auto an. Ein simulierter
# Adam drueckt bei JEDER Rueckfrage „Ablehnen" -- so trennt sich „ohne Frage
# erlaubt" (Allow, kein Dialog) von „gefragt und abgelehnt" (Deny, Dialog).
GESENDET: list = []


class _Gesendete:
    def __init__(self, mid):
        self.message_id = mid


class _BotAttrappe:
    async def send_message(self, **kw):
        GESENDET.append(kw)
        return _Gesendete(1000 + len(GESENDET))


async def _rueckruf(pfad: str):
    GESENDET.clear()
    sess = bot.UserSession(client=None, chat_id=999)
    sess.bot = _BotAttrappe()
    sess.thread_id = None
    bot.SESSIONS[bot.faden(UID, None)] = sess
    rueckruf = bot.make_permission_callback(UID, None)

    async def _adam_lehnt_ab():
        for _ in range(100):
            if sess.pending_permissions:
                break
            await asyncio.sleep(0.01)
        else:
            return
        rid = next(iter(sess.pending_permissions))
        schleife, fut = sess.pending_permissions[rid]
        if not fut.done():
            schleife.call_soon_threadsafe(fut.set_result, "deny")

    druecker = asyncio.create_task(_adam_lehnt_ab())
    erg = await rueckruf("Write", {"file_path": pfad, "content": "x"}, None)
    await druecker
    return type(erg).__name__, bool(GESENDET), str(getattr(erg, "message", ""))[:40]


bot._set_bash_auto(UID, True)
_faelle = {
    "Arbeitsordner": (_drin, ("PermissionResultAllow", False)),
    "Repo-Klon": (str(bot._REPO_DIR / "bot.py"), ("PermissionResultDeny", False)),
    "Gedaechtnis": (str(Path.home() / ".claude/memory/MEMORY.md"),
                    ("PermissionResultDeny", True)),
}
_falsch = []
for _name, (_pfad, (_soll_typ, _soll_dialog)) in _faelle.items():
    _typ, _dialog, _msg = asyncio.run(_rueckruf(_pfad))
    if (_typ, _dialog) != (_soll_typ, _soll_dialog):
        _falsch.append(f"{_name}: {_typ}, Dialog={_dialog} {_msg}")
zeile("im echten Rueckruf: Arbeitsordner frei, Repo hart abgelehnt, Gedaechtnis fragt",
      not _falsch, gemessen=" | ".join(_falsch))

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
