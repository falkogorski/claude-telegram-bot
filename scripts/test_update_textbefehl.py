#!/usr/bin/env python3
# <!-- ROLLE: test-update-textbefehl -->
"""Verhaltenstest E4 — Update-Auslösung per Text.

**Ein Pfad, der Pakete auf dem Server austauscht, verträgt kein Ermessen.**
Deshalb ist der Befehl exakt: Wer sich vertippt, löst nichts aus, und sein Text
geht als normale Nachricht an den Agenten wie jeder andere.

Geprüft werden Engywucks drei Fälle — **ausführend**, mit Attrappen nur an den
Rändern (Telegram und Updater).
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="e4-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []
QUELLE = Path(bot.__file__).read_text(encoding="utf-8")


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


_ANTWORTEN: list[str] = []
_EINGESPIELT: list[tuple] = []
_VORGEMERKT: list[tuple] = []


class _Nachricht:
    async def reply_text(self, text, **kw):
        _ANTWORTEN.append(text)
        return None


class _Nutzer:
    def __init__(self, uid):
        self.id = uid


class _Update:
    def __init__(self, uid):
        self.message = _Nachricht()
        self.effective_user = _Nutzer(uid)
        self.effective_chat = _Nutzer(uid)


class _Ctx:
    def __init__(self, *args):
        self.args = list(args)


class _Updater:
    """Attrappe am RAND — der echte würde Pakete austauschen."""
    @staticmethod
    def classify():
        return [{"name": "edge-tts", "latest": "7.2.3", "ampel": "gruen",
                 "kind": "pip", "cur": "7.2.0"}]

    @staticmethod
    def apply_updates(names, expected):
        _EINGESPIELT.append((tuple(names), dict(expected)))
        return {"ok": True, "msg": "eingespielt", "done": list(names)}


class _Fenster:
    @staticmethod
    def vormerken(name, version, ampel):
        _VORGEMERKT.append((name, version, ampel))

    @staticmethod
    def uebersicht():
        return ""


def _frisch():
    _ANTWORTEN.clear(); _EINGESPIELT.clear(); _VORGEMERKT.clear()


bot._load_updater = lambda: _Updater
bot._load_wartungsfenster = lambda: _Fenster


def _exaktes_kommando_von_adam_loest_aus():
    """Der Grundfall — und er muss GENAU die angezeigte Fassung freigeben."""
    _frisch()
    asyncio.run(bot.cmd_update_ja(_Update(1), _Ctx("edge-tts")))
    assert _EINGESPIELT, f"nichts eingespielt: {_ANTWORTEN}"
    namen, erwartet = _EINGESPIELT[0]
    assert namen == ("edge-tts",), f"falsches Paket: {namen}"
    assert erwartet == {"edge-tts": "7.2.3"}, (
        "die Drift-Sperre fehlt — freigegeben werden muss GENAU die Fassung, "
        f"die Adam gesehen hat: {erwartet}")


def _aehnlicher_text_loest_NICHTS_aus():
    """**Kein Fuzzy.** Wer sich vertippt oder frei formuliert, löst nichts aus.
    Der Handler bekommt solche Texte gar nicht erst — Telegram reicht nur
    exakte Kommandos an einen CommandHandler weiter. Das wird hier am
    REGISTRIERWEG geprüft, nicht an einer Nachbildung."""
    reg = QUELLE.split("app.add_handler(CommandHandler(\"update_ja\"")[1][:120]
    assert "cmd_update_ja" in reg, "der Befehl haengt nicht am CommandHandler"
    # Ein MessageHandler auf Freitext waere der Fuzzy-Weg - den darf es nicht geben.
    assert "update_ja" not in QUELLE.split("MessageHandler")[-1][:400], \
        "der Befehl haengt zusaetzlich an einem Freitext-Handler"
    # Und ohne genau ein Argument passiert nichts ausser einer Erklaerung.
    _frisch()
    asyncio.run(bot.cmd_update_ja(_Update(1), _Ctx()))
    assert not _EINGESPIELT, "ohne Argument wurde etwas eingespielt"
    asyncio.run(bot.cmd_update_ja(_Update(1), _Ctx("edge-tts", "und", "mehr")))
    assert not _EINGESPIELT, "mit mehreren Argumenten wurde etwas eingespielt"


def _unbekannter_name_spielt_nichts_ein():
    """Ein Name, für den kein Update ansteht, darf nichts auslösen — und muss
    sagen, wo die richtigen Namen stehen."""
    _frisch()
    asyncio.run(bot.cmd_update_ja(_Update(1), _Ctx("gibtsnicht")))
    assert not _EINGESPIELT, "ein unbekannter Name loeste ein Update aus"
    assert _ANTWORTEN and "/updates" in _ANTWORTEN[0], \
        f"die Antwort sagt nicht, wo die Namen stehen: {_ANTWORTEN}"


def _fremde_user_id_loest_nichts_aus():
    """**Der Sicherheitsfall.** Nur Adam. Ein exaktes Kommando von einer
    fremden Kennung darf nichts bewirken — und keine Auskunft geben."""
    _frisch()
    asyncio.run(bot.cmd_update_ja(_Update(999999), _Ctx("edge-tts")))
    assert not _EINGESPIELT, "eine fremde Kennung hat ein Update ausgeloest"
    assert not _ANTWORTEN, f"eine fremde Kennung bekam eine Antwort: {_ANTWORTEN}"
    asyncio.run(bot.cmd_update_nacht(_Update(999999), _Ctx("edge-tts")))
    assert not _VORGEMERKT, "eine fremde Kennung hat etwas vorgemerkt"


def _nacht_merkt_vor_statt_einzuspielen():
    _frisch()
    asyncio.run(bot.cmd_update_nacht(_Update(1), _Ctx("edge-tts")))
    assert _VORGEMERKT == [("edge-tts", "7.2.3", "gruen")], \
        f"nicht korrekt vorgemerkt: {_VORGEMERKT}"
    assert not _EINGESPIELT, "vormerken hat sofort eingespielt"


def _kein_modell_im_ausfuehrungspfad():
    """Adams Bedingung: deterministisch. Ein Modell, das den Befehl auslegen
    müsste, brächte Ermessen in einen Pfad, der Pakete austauscht."""
    block = QUELLE.split("async def _e4_ausloesen")[1].split("\nasync def cmd_setkanal")[0]
    for verboten in ("ClaudeSDKClient", "stream_response", "ensure_session"):
        assert verboten not in block, \
            f"der Ausfuehrungspfad enthaelt `{verboten}` — kein Ermessen hier"


def _doku_spiegel_ist_nachgezogen():
    """Doku-Spiegel-Regel: nutzerseitige Texte im SELBEN Commit."""
    assert "/update_ja <name>" in QUELLE, "der Befehl fehlt in /hilfe"
    assert 'BotCommand("update_ja"' in QUELLE, "der Befehl fehlt in setMyCommands"
    assert 'BotCommand("update_nacht"' in QUELLE, "der Nacht-Befehl fehlt im Menue"


check("exaktes Kommando von Adam loest aus (mit Drift-Sperre)",
      _exaktes_kommando_von_adam_loest_aus)
check("aehnlicher Text loest NICHTS aus (kein Fuzzy)",
      _aehnlicher_text_loest_NICHTS_aus)
check("unbekannter Name spielt nichts ein", _unbekannter_name_spielt_nichts_ein)
check("fremde user_id loest nichts aus und bekommt keine Auskunft",
      _fremde_user_id_loest_nichts_aus)
check("/update_nacht merkt vor statt einzuspielen",
      _nacht_merkt_vor_statt_einzuspielen)
check("kein Modell im Ausfuehrungspfad", _kein_modell_im_ausfuehrungspfad)
check("Doku-Spiegel ist nachgezogen", _doku_spiegel_ist_nachgezogen)

print()
if fails:
    print(f"❌ {len(fails)} E4-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle E4-Tests bestanden.")
