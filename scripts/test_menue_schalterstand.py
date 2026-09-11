#!/usr/bin/env python3
# <!-- ROLLE: test-menue-schalterstand -->
"""Der Schalterstand im „/"-Menü: Tabelle, Beschreibung, Auslöser, Fehlschlag.

**Was hier ausgeführt und was gemessen wird.** Die Beschreibungen werden
**erzeugt**, nicht im Quelltext gesucht, und der Auslöser wird **gefahren** —
Attrappen sitzen nur an den Rändern (Telegram-Aufruf, Update-Objekt), die Mitte
ist der Code, der im Betrieb läuft. Ein Textscan über `bot.py` hätte hier
keinerlei Wert: Eine Tabelle, die dasteht, sagt nichts darüber, ob der Stand,
den sie erzeugt, mit dem Zustandsgeber übereinstimmt.

**Jeder Schalter wird in BEIDEN Stellungen gemessen.** Ein Text, der immer
„an" sagt, bestünde eine einseitige Prüfung.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="menue-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                        # noqa: E402
import ast as _ast                                                # noqa: E402

_QUELLE = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")

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
print("== Schalterstand im Menue ==")

# Eine echte Sitzung, damit `/quiet` einen Zustand HAT. Ohne offene Sitzung
# gilt die Vorgabe — das ist richtig so, aber dann misst die Stellung „still"
# nichts.
_SESS = bot.UserSession(client=None, user_id=UID)
bot.SESSIONS[bot.faden(UID, None)] = _SESS


def _prefs() -> dict:
    return bot._USER_PREFS.setdefault(str(UID), {})


def setz(name: str, an: bool) -> None:
    """Setzt den Zustand ueber die QUELLE, aus der der Geber liest."""
    p = _prefs()
    if name == "empfang":
        p["empfang"] = an
    elif name == "tts":
        p["tts_enabled"] = an
    elif name == "spur":
        p["trace_off"] = not an          # Spur an == trace_off aus
    elif name == "technik":
        p["raw_tools"] = an
    elif name in ("quiet", "verbose"):
        _SESS.quiet = an
    else:
        raise AssertionError(f"unbekannter Schalter {name}")


# ── 1. Jeder Eintrag in _SCHALTER hat einen Befehl MIT Menue-Beschreibung ────
_menue = {name: kurz for name, kurz, _lang in bot._BEFEHLE}
_ohne_befehl = [n for n in bot._SCHALTER if not _menue.get(n)]
zeile("jeder Schalter hat einen Befehl mit Menue-Beschreibung",
      not _ohne_befehl, gemessen=", ".join(_ohne_befehl))

# ── 2. Die Gegenrichtung, und sie ist die wichtigere ─────────────────────────
# Ein Befehl, der sich im eigenen Text als Umschalter zu erkennen gibt, aber
# nicht in `_SCHALTER` steht, waere der naechste Schalter ohne Stand — und
# niemand merkt es. Ausnahmen sind erlaubt, muessen aber hier begruendet
# dastehen; heute gibt es keine.
_AUSNAHMEN: dict[str, str] = {}
_MUSTER = ("an/aus", "aus/an", "umschalten", "toggle")
_verdaechtig = []
for _name, _kurz, _lang in bot._BEFEHLE:
    if _name in bot._SCHALTER or _name in _AUSNAHMEN:
        continue
    _text = f"{_kurz or ''} {_lang}".lower()
    if any(m in _text for m in _MUSTER):
        _verdaechtig.append(_name)
zeile("kein Umschalter ausserhalb von _SCHALTER",
      not _verdaechtig, gemessen=", ".join(_verdaechtig))

# ── 3. Jede erzeugte Beschreibung bleibt im Telegram-Rahmen ──────────────────
# Telegram lehnt bei Ueberlaenge den GANZEN Aufruf ab; dann bliebe das Menue
# stumm auf dem alten Stand stehen. Gemessen wird deshalb nicht nur der heutige
# Bestand, sondern auch ein bewusst zu langer Text.
_laengen = [len(bot._menue_beschreibung(n, k, UID))
            for n, k, _l in bot._BEFEHLE if k]
_lang_test = bot._menue_beschreibung("empfang", "x" * 400, UID)
zeile("jede Beschreibung ist 1 bis 256 Zeichen lang",
      _laengen and min(_laengen) >= 1 and max(_laengen) <= 256
      and 1 <= len(_lang_test) <= 256,
      gemessen=f"Bestand {min(_laengen)}..{max(_laengen)}, Langtest {len(_lang_test)}")

# ── 4. Die Signatur aendert sich, wenn ein Zustand kippt ─────────────────────
# Ohne diese Zeile waere der Ausloeser eine Attrappe: Er schreibt nur bei
# Unterschied, und wenn die Signatur sich nie unterscheidet, schreibt er nie.
_stumpf = []
for _name in bot._SCHALTER:
    setz(_name, False)
    _aus = bot._schalter_signatur(UID)
    setz(_name, True)
    _an = bot._schalter_signatur(UID)
    if _aus == _an:
        _stumpf.append(_name)
    setz(_name, False)
zeile("die Signatur kippt mit jedem einzelnen Schalter",
      not _stumpf, gemessen=", ".join(_stumpf))

# ── 5. Der angezeigte Stand stimmt mit dem Geber — in BEIDEN Stellungen ──────
_falsch = []
for _name, (_geber, _wort_an, _wort_aus) in bot._SCHALTER.items():
    for _soll in (True, False):
        setz(_name, _soll)
        _ist = bool(_geber(UID))
        _text = bot._menue_beschreibung(_name, _menue[_name], UID)
        _erwartet = f"{'●' if _soll else '○'} {_wort_an if _soll else _wort_aus} · "
        if _ist is not _soll or not _text.startswith(_erwartet):
            _falsch.append(f"{_name}={_soll}: {_text[:40]}")
    setz(_name, False)
zeile("der angezeigte Stand stimmt in beiden Stellungen",
      not _falsch, gemessen=" | ".join(_falsch))


# ── 6. Ein Fehlschlag VERWIRFT die Signatur ──────────────────────────────────
# Ein Menue, das luegt, ist schlechter als eines ohne Stand. Scheitert der
# Schreibaufruf, darf der Bot den Stand nicht fuer geschrieben halten — sonst
# schreibt er ihn nie wieder, weil die Signatur ja angeblich stimmt.
class _Bot:
    def __init__(self, wirft: bool) -> None:
        self.wirft = wirft
        self.aufrufe = 0

    async def set_my_commands(self, befehle, scope=None):
        self.aufrufe += 1
        if self.wirft:
            raise RuntimeError("Telegram sagt nein")


class _Update:
    def __init__(self, uid: int) -> None:
        self.effective_user = type("U", (), {"id": uid})()


class _Ctx:
    def __init__(self, bot_obj) -> None:
        self.bot = bot_obj


async def _fahre() -> tuple:
    # Der Fehlschlag unten ist GEWOLLT. Ohne diese Daempfung landet sein
    # Traceback im Pruefer-Ausgang und liest sich wie ein echter Bruch.
    import logging
    _log = logging.getLogger("claude-tg-bot")
    _vorher = _log.level
    _log.setLevel(logging.CRITICAL)
    try:
        return await _fahre_leise()
    finally:
        _log.setLevel(_vorher)


async def _fahre_leise() -> tuple:
    bot._MENUE_STAND.pop(UID, None)
    setz("empfang", False)

    schlecht = _Bot(wirft=True)
    await bot._menue_nachziehen(_Update(UID), _Ctx(schlecht))
    nach_fehlschlag = UID in bot._MENUE_STAND

    gut = _Bot(wirft=False)
    await bot._menue_nachziehen(_Update(UID), _Ctx(gut))
    nach_erfolg = UID in bot._MENUE_STAND

    # Zweiter Durchgang ohne Aenderung: kein zweiter Schreibaufruf.
    await bot._menue_nachziehen(_Update(UID), _Ctx(gut))
    unveraendert = gut.aufrufe

    # Und nach echtem Umlegen wieder einer.
    setz("empfang", True)
    await bot._menue_nachziehen(_Update(UID), _Ctx(gut))
    nach_umlegen = gut.aufrufe
    return nach_fehlschlag, nach_erfolg, unveraendert, nach_umlegen, schlecht.aufrufe


_f, _e, _u, _um, _versuche = asyncio.run(_fahre())
zeile("Fehlschlag verwirft die Signatur, Erfolg haelt sie, nur Aenderung schreibt",
      _versuche == 1 and _f is False and _e is True and _u == 1 and _um == 2,
      gemessen=f"Fehlversuche={_versuche} nach_Fehlschlag={_f} nach_Erfolg={_e} "
               f"ohne_Aenderung={_u} nach_Umlegen={_um}")


# ── 7. Dieselbe Gegenrichtung, aber als MENGE statt als Wortliste ────────────
# **Ergänzung über den Auftrag hinaus, und sie ist gemessen, nicht vermutet:**
# Zeile 2 findet einen Schalter nur, wenn er sich im eigenen Beschreibungstext
# verrät. Von den sechs heutigen tun das **drei** — `technik` („Klartext ↔
# Rohform"), `quiet` („Tipp-Indikator aus") und `verbose` („wieder an") nicht.
# Eine Prüfzeile, die die Hälfte ihrer Fälle nicht sieht, ist die Art
# Beruhigung, gegen die dieses Haus gebaut ist.
#
# Diese Zeile misst stattdessen eine **Menge**: Welcher Befehls-Handler legt
# einen Zustand UM (`x = not …`)? Das Befehl-Handler-Paar kommt aus den
# `CommandHandler`-Registrierungen, nicht aus einer gepflegten Liste.
# Gemessen beim Bau: vier Treffer, alle bereits in `_SCHALTER`, **kein
# Fehlalarm** — deshalb braucht diese Zeile keine Ausnahmeliste.
#
# **Was auch sie nicht fängt, und das gehört dazu:** `/quiet` und `/verbose`
# sind ein PAAR, kein Umschalter — sie setzen auf feste Werte. Ein künftiger
# Paar-Befehl mit unauffälligem Text fiele durch beide Raster. Dafür einen
# dritten Prüfer zu bauen wäre der Wächter dritter Ordnung; die Grenze steht
# stattdessen hier und im Register.
_baum = _ast.parse(_QUELLE)
_paare: dict = {}
for _k in _ast.walk(_baum):
    if isinstance(_k, _ast.Call) and getattr(_k.func, "id", None) == "CommandHandler" \
            and len(_k.args) >= 2 and isinstance(_k.args[0], _ast.Constant):
        _paare[_k.args[0].value] = getattr(_k.args[1], "id", None)

_umleger: set = set()
for _fn in _ast.walk(_baum):
    if not isinstance(_fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
        continue
    for _k in _ast.walk(_fn):
        _ist = (isinstance(_k, _ast.Assign)
                and isinstance(_k.value, _ast.UnaryOp)
                and isinstance(_k.value.op, _ast.Not))
        if isinstance(_k, _ast.Call):
            for _a in list(_k.args) + [kw.value for kw in _k.keywords]:
                if isinstance(_a, _ast.UnaryOp) and isinstance(_a.op, _ast.Not):
                    _ist = True
        if _ist:
            _umleger.add(_fn.name)
            break

_ohne_stand = sorted(b for b, h in _paare.items()
                     if h in _umleger and b not in bot._SCHALTER)
zeile("kein Befehl legt einen Zustand um, ohne in _SCHALTER zu stehen",
      not _ohne_stand, gemessen=", ".join(_ohne_stand))


# ── 8. Ruft der Bot den Ausloeser ueberhaupt? ────────────────────────────────
# **Engywucks Gegenprobe vom 11.09., und sie hat gesessen:** Entfernt man die
# Registrierung `app.add_handler(TypeHandler(Update, _menue_nachziehen),
# group=99)`, bleiben die sieben Zeilen darueber **gruen**. Sie rufen
# `_menue_nachziehen` naemlich selbst — niemand misst, ob der Bot ihn ruft.
# Fabrik ja, Aufrufer nein; genau der Fall vom 22.08.
#
# Gemessen wird deshalb die **Abwesenheit** ueber echte Aufrufknoten, nicht
# ueber Zeilen mit dem Namen: Ein Kommentar steht nicht im Syntaxbaum.
_registriert = []
for _k in _ast.walk(_baum):
    if not isinstance(_k, _ast.Call) or getattr(_k.func, "attr", None) != "add_handler":
        continue
    _grp = next((kw.value for kw in _k.keywords if kw.arg == "group"), None)
    if not (isinstance(_grp, _ast.Constant) and _grp.value == 99):
        continue
    for _arg in _k.args:
        if not (isinstance(_arg, _ast.Call)
                and getattr(_arg.func, "id", None) == "TypeHandler"):
            continue
        if any(getattr(_a, "id", None) == "_menue_nachziehen" for _a in _arg.args):
            _registriert.append(_k.lineno)
zeile("der Ausloeser ist als TypeHandler in group=99 registriert",
      len(_registriert) == 1,
      gemessen=f"{len(_registriert)} Registrierungen: {_registriert}")

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
