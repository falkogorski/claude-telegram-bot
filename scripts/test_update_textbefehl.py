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
    """Doku-Spiegel-Regel: nutzerseitige Texte im SELBEN Commit.

    `[GEAENDERT 2026-08-20]` **Gemessen wird jetzt die Liste, nicht der
    Quelltext.** Seit Menue und Hilfetext aus einer Quelle kommen und zur
    Laufzeit sortiert werden, steht kein `BotCommand("update_ja"` mehr in der
    Datei — diese Pruefung wurde beim Umbau prompt rot, und zwar zu Recht:
    Sie suchte eine Schreibweise, nicht die Sache. Jetzt sucht sie die Sache.
    """
    namen = {n for n, _kurz, _lang in bot._BEFEHLE}
    im_menue = {n for n, kurz, _lang in bot._BEFEHLE if kurz}
    for befehl in ("update_ja", "update_nacht"):
        assert befehl in namen, f"/{befehl} fehlt in der Befehlsliste"
        assert befehl in im_menue, f"/{befehl} fehlt im Telegram-Menue"
    lang = dict((n, l) for n, _k, l in bot._BEFEHLE)
    assert "<name>" in lang["update_ja"], \
        "die /hilfe-Zeile nennt das Argument nicht"


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


# ---------- Nachlese ①: der Repo-Wächter (Claudias Befund) ------------------
def _fehlerumleitung_ist_kein_repo_schreiben():
    """**Claudias Befund vom 18.08., dreizehn Beobachtungen — gegengeprüft.**

    Sie hat dabei ihre EIGENE erste Diagnose widerlegt: Nicht das `cd` war der
    Auslöser, sondern das `>`. Ihr vermeintlicher Ausweg über `git -C` lief nur
    deshalb, weil er zufällig keine Umleitung enthielt.

    Eine Fehlerumleitung schreibt nichts ins Repo — sie unterdrückt Rauschen.
    """
    # **`[KORRIGIERT 23.08.]`** Hier stand `~/claude-telegram-bot` — auf dem VPS
    # richtig, am Mac nicht. Solange die Pruefung Zeichenketten verglich, war
    # das gleichgueltig; seit Befund D/E loest sie Pfade auf. Ein fester Pfad
    # macht einen Pruefer hier gruen und dort blind.
    _R = str(bot._REPO_DIR)
    for frei in (f"git -C {_R} log -1 2>&1",
                 f"git -C {_R} log -1 2>/dev/null",
                 f"cat {_R}/README.md 2>/dev/null"):
        assert bot._is_repo_read_cmd(frei), \
            f"eine Fehlerumleitung faellt in den Dialog: {frei}"


def _die_riegel_halten_trotzdem():
    """**Die wichtigere Haelfte.** Eine Lockerung ist erst geprueft, wenn
    belegt ist, dass sie nicht zu weit geht."""
    _R = str(bot._REPO_DIR)
    for zu in (f"git -C {_R} log > /tmp/x",       # echte Umleitung
               f"cat {_R}/x && rm -rf /",          # Verkettung
               f"cat {_R}/x | sh",                 # Rohr
               f"cat {_R}/.env",                   # Geheimnis
               f"git -C {_R} commit -m x",         # Schreiben
               f"sed -i s/a/b/ {_R}/bot.py",
               # Neu seit Befund D/E: derselbe Riegel, anders geschrieben.
               f"cat {_R}/../../etc/passwd",
               f"cat $HOME/.bash_history {_R}/README.md"):
        assert not bot._is_repo_read_cmd(zu), f"Lese-Freigabe zu weit: {zu}"


def _beide_stellen_tragen_die_lockerung():
    """**Geschwister-Regel in Reinform.** Die Lockerung im Lese-Zweig half
    zunaechst GAR NICHT: Er fragt `_is_repo_write_cmd` als doppelten Boden, und
    dessen Muster sucht `>` — also hielt es `2>&1` weiter fuer ein
    Schreibmuster. Zwei Stellen fuer eine Ursache."""
    assert not bot._is_repo_write_cmd("git -C ~/claude-telegram-bot log 2>&1"), \
        "die Schreibpruefung haelt eine Fehlerumleitung fuer Schreiben"
    assert bot._is_repo_write_cmd("git -C ~/claude-telegram-bot log > /tmp/x"), \
        "eine echte stdout-Umleitung gilt nicht mehr als Schreiben"


def _der_grund_nennt_das_zeichen():
    """**Claudias Zusatz:** Der Meldungstext nennt das beanstandete Zeichen.
    Ohne das raet der Empfaenger — sie selbst hat daraufhin eine falsche
    Ursache diagnostiziert und einen Zufallstreffer fuer den Ausweg gehalten."""
    # `[BERICHTIGT 31.08.]` **Der Pfad kommt aus dieser Datei, nicht aus einer
    # Zeichenkette.** Hier stand `~/claude-telegram-bot` — das ist der Pfad auf
    # dem VPS; am Bau-Rechner liegt das Repo unter `~/Projects/…`. Die
    # Alle-Pfade-Pruefung sagte hier also zu Recht [zeigt aus dem Repo hinaus],
    # und die zweite Zusage war auf dieser Maschine schlicht falsch.
    #
    # **Aufgefallen ist es erst, als die Grund-Funktion vollstaendig wurde**
    # (F-8): Vorher fehlte ihr genau diese Pruefung, also war die Zeile
    # zufaellig gruen. Ein Pruefer mit fest verdrahtetem Pfad misst auf zwei
    # Maschinen zwei verschiedene Dinge — dieselbe Klasse wie der
    # `$HOME`-Fund vom 29.07.
    _repo = str(Path(__file__).resolve().parent.parent)
    grund = bot._repo_read_grund(f"cat {_repo}/x | sh")
    assert "|" in grund, f"das beanstandete Zeichen wird nicht genannt: {grund}"
    assert bot._repo_read_grund(f"git -C {_repo} log -1") == "", \
        "ein freigegebener Befehl bekommt trotzdem einen Ablehnungsgrund"


check("Fehlerumleitung ist kein Repo-Schreiben (Claudias Befund)",
      _fehlerumleitung_ist_kein_repo_schreiben)
check("die Riegel halten trotzdem", _die_riegel_halten_trotzdem)
check("beide Stellen tragen die Lockerung (Geschwister)",
      _beide_stellen_tragen_die_lockerung)
check("der Grund nennt das beanstandete Zeichen", _der_grund_nennt_das_zeichen)

if fails:
    print(f"\n❌ {len(fails)} E4-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("\nAlle E4-Tests bestanden.")
