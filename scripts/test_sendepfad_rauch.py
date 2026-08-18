#!/usr/bin/env python3
# <!-- ROLLE: test-sendepfad-rauchtest -->
"""Rauchtest des zentralen Sendepfads — Pflicht-Prüfer Nr. 1 (Conni, Auflage ③).

**Warum es diesen Prüfer gibt.** Am 18.08.2026 fand eine Gegenprüfung, dass
`send_answer_to_user` seit dem 28.07. bei JEDEM Aufruf mit `NameError` stirbt:
Die Funktion reichte ein `user_id` an die Tastatur weiter, das in ihrem
Namensraum nicht existiert. Der Fehler lag drei Wochen im Repo, kein
Regressionslauf und kein Selbstcheck hat ihn berührt — beide rufen diesen Pfad
nicht auf. Nach einem Deploy hätte der Bot jede Nachricht verarbeitet, die
Antwort erzeugt und wäre gestorben, bevor ein Zeichen hinausgeht.

Erzeugt hat ihn ausgerechnet ein Prüfer: Eine AST-Regel verlangte `user_id=` an
jeder `_main_keyboard`-Aufrufstelle und maß nur, **ob das Schlüsselwort
dasteht** — nie, ob es dort einen Wert hat.

**Daraus der Grundsatz, den dieser Prüfer verkörpert:** Ein Prüfer, der nur
Text sucht, prüft die Schreibweise, nicht die Wirkung. Kritische Pfade werden
**ausgeführt** — Attrappen an den Rändern, echter Code in der Mitte.

Der Rand ist hier alles, was nach Telegram hinausgeht. Die Mitte ist der
echte, unveränderte `send_answer_to_user`.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="rauch-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:                      # ← der eigentliche Zweck
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


class _Nachricht:
    """Was Telegram zurückgibt — nur so viel, wie der Pfad wirklich anfasst."""
    message_id = 4242


class _AttrappenBot:
    """Der RAND. Sammelt, was hinausgegangen wäre, und erfindet nichts."""

    def __init__(self):
        self.texte = []
        self.stimmen = []

    async def send_message(self, chat_id=None, text=None, **kw):
        self.texte.append(text)
        return _Nachricht()

    async def send_voice(self, chat_id=None, voice=None, **kw):
        self.stimmen.append(kw.get("caption"))
        return _Nachricht()

    async def send_chat_action(self, **kw):
        return True


def _sitzung(user_id=1, tts=False, attrappe=None):
    """Eine Sitzung ohne SDK-Client — der wird auf diesem Pfad nicht berührt.

    Der Attrappen-Bot haengt AN DER SITZUNG, weil der echte Pfad ihn genau
    dort holt (`sess.bot`). Wer ihn woanders einspeist, prueft eine Verdrahtung,
    die es nicht gibt.
    """
    s = object.__new__(bot.UserSession)
    s.bot = attrappe if attrappe is not None else _AttrappenBot()
    s.client = None
    s.user_id = user_id
    s.tts_enabled = tts
    s.current_model = bot.DEFAULT_MODEL
    s.current_effort = None
    s.logger = None
    s.quiet = True
    return s


def _der_pfad_laeuft_ueberhaupt():
    """**Der Kern.** Ein Aufruf, mehr nicht — genau das, was drei Wochen fehlte.

    Diese eine Zeile hätte den Fehler am ersten Tag gefangen. Sie prüft kein
    Feinverhalten, sondern die Frage, die niemand gestellt hat: *Läuft es?*
    """
    b = _AttrappenBot()
    ergebnis = asyncio.run(bot.send_answer_to_user(
        _sitzung(attrappe=b), 1, "Eine ganz gewöhnliche Antwort."))
    assert ergebnis is not False, "der Sendepfad meldet einen Zustellfehler"
    assert b.texte or b.stimmen, "es ging nichts hinaus"
    assert "gewöhnliche Antwort" in (b.texte[0] or ""), \
        f"der Text kam verändert an: {b.texte[:1]}"


def _auch_mit_aktivem_gruendlich():
    """Der Zweig, der den Fehler eingeschleppt hat: Die Tastatur fragt bei
    aktivem Gründlich die Vorlieben ab — dafür braucht sie eine echte Kennung."""
    bot._set_thorough(1, True)
    try:
        b = _AttrappenBot()
        asyncio.run(bot.send_answer_to_user(
            _sitzung(attrappe=b), 1, "Zweiter Durchgang."))
        assert b.texte, "bei aktivem Gründlich ging nichts hinaus"
    finally:
        bot._set_thorough(1, False)


def _leerer_text_ist_kein_zustellfehler():
    """Die Gegenprobe — sonst würde der Prüfer nur den Erfolgsfall kennen."""
    b = _AttrappenBot()
    assert asyncio.run(bot.send_answer_to_user(
        _sitzung(attrappe=b), 1, "   ")) is True
    assert not b.texte, "für leeren Text wurde etwas gesendet"


def _keine_freien_namen_im_sendepfad():
    """Der Riegel gegen die Wiederkehr: Sucht ALLE Namen, die im Sendepfad
    gelesen, aber nirgends gebunden werden — der Fehler war genau das, und ein
    Textprüfer hätte ihn nicht gesehen."""
    import symtable
    quelle = Path(bot.__file__).read_text(encoding="utf-8")
    tab = symtable.symtable(quelle, "bot.py", "exec")

    def finde(t, name):
        for k in t.get_children():
            if k.get_name() == name:
                return k
            tr = finde(k, name)
            if tr:
                return tr

    modul = {s.get_name() for s in tab.get_symbols()}
    import builtins
    eingebaut = set(dir(builtins))
    for fname in ("send_answer_to_user", "stream_response"):
        f = finde(tab, fname)
        assert f, f"{fname} nicht gefunden"
        frei = [s.get_name() for s in f.get_symbols()
                if s.is_global() and not s.is_assigned()
                and s.get_name() not in modul
                and s.get_name() not in eingebaut]
        assert not frei, (
            f"{fname} liest Namen, die nirgends gebunden sind: {frei} — "
            "genau der Fehler vom 28.07., der drei Wochen lag")


check("der Sendepfad läuft überhaupt (der Fehler vom 28.07.)",
      _der_pfad_laeuft_ueberhaupt)
check("auch bei aktivem Gründlich", _auch_mit_aktivem_gruendlich)
check("leerer Text ist kein Zustellfehler (Gegenprobe)",
      _leerer_text_ist_kein_zustellfehler)
check("keine ungebundenen Namen im Sendepfad", _keine_freien_namen_im_sendepfad)

print()
if fails:
    print(f"❌ {len(fails)} Rauchtest-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Sendepfad-Rauchtest bestanden.")
