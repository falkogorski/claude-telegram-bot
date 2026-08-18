#!/usr/bin/env python3
# <!-- ROLLE: test-gruendlich -->
"""Verhaltenstest B3 — „🎯 Gründlich" ist ein Umschalter mit sichtbarem Haken.

**Der Schwerpunkt liegt auf dem stillsten Fall.** Adams Anlass war ein Knopf,
den man nicht mehr ausschalten konnte. Die gefährlichere Hälfte des Umbaus ist
aber eine andere: Bliebe das Schließen der Sitzung stehen, hätte im Dauerbetrieb
jede Nachricht keinen Gesprächsfaden mehr — **und das meldet niemand als
Fehler, es sieht aus wie Vergesslichkeit.**
"""
import ast
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b3-"))
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
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _umschalter_statt_einmal_aktion():
    """Adams Anlass: „ich kann ihn nicht mehr ausschalten"."""
    uid = 4711
    bot._set_thorough(uid, False)
    assert not bot._thorough_on(uid)
    bot._set_thorough(uid, True)
    assert bot._thorough_on(uid), "einschalten wirkt nicht"
    bot._set_thorough(uid, False)
    assert not bot._thorough_on(uid), "AUSschalten wirkt nicht — Adams Fall"


def _zustand_ueberlebt_neustart():
    """Der alte Satz war reiner Arbeitsspeicher — der Haken wäre nach jedem
    Neustart weg gewesen, während Adam ihn für gesetzt hielt."""
    uid = 4712
    bot._set_thorough(uid, True)
    assert bot._USER_PREFS.get(str(uid), {}).get("thorough") is True, \
        "der Zustand landet nicht in den Vorlieben"
    assert "_THOROUGH_PENDING" not in QUELLE.replace(
        "Der frühere `_THOROUGH_PENDING`-Satz", ""), \
        "der alte Speicher-Satz lebt noch — zwei Wahrheiten über denselben Zustand"


def _haken_ist_sichtbar_und_ehrlich():
    """Ein Haken, der lügt, ist schlimmer als keiner: Bei Gründlich läuft alles
    auf höchster Stufe — also muss auch „🚀 Max" den Haken tragen."""
    uid = 4713
    bot._set_thorough(uid, False)
    aus = [b.text for r in bot._main_keyboard(False, "opus", None, user_id=uid).keyboard
           for b in r]
    assert bot._BTN_THOROUGH in aus and bot._BTN_THOROUGH_ACTIVE not in aus

    bot._set_thorough(uid, True)
    an = [b.text for r in bot._main_keyboard(False, "opus", None, user_id=uid).keyboard
          for b in r]
    assert bot._BTN_THOROUGH_ACTIVE in an, "der Haken erscheint nicht"
    assert bot._BTN_EFFORT_MAX_ACTIVE in an, (
        "bei Gründlich trägt nicht 'Max' den Haken — die Tastatur zeigt eine "
        "Tiefe an, in der nicht gearbeitet wird")


def _beide_beschriftungen_sind_bedienbar():
    """Sonst landet ein Druck auf den Haken-Knopf als FRAGE beim Agenten —
    am 23.07. mit dem Transkriptions-Knopf live passiert."""
    for btn in (bot._BTN_THOROUGH, bot._BTN_THOROUGH_ACTIVE):
        assert btn in bot._ALL_KEYBOARD_BTNS, (
            f"{btn} fehlt in _ALL_KEYBOARD_BTNS — der Druck ginge an den Agenten")


def _tiefe_haengt_an_ensure_session():
    """Kernpunkt C: Die Sitzung wird an mehreren Stellen neu aufgebaut. Läge die
    Regel nur im Auftragslauf, verlöre ein Modellwechsel still die Tiefe."""
    block = QUELLE.split("async def ensure_session")[1].split("\nasync def ")[0]
    assert "_thorough_on(user_id)" in block and 'effort = "max"' in block, \
        "die Tiefe wird nicht in ensure_session erzwungen"


def _kein_close_session_mehr_im_gruendlich_zweig():
    """**Kernpunkt D — der Abnahmepunkt.**

    Bliebe eine Zeile stehen, die nach jeder Anfrage die Sitzung schließt,
    hätte im Dauerbetrieb jede Nachricht keinen Gesprächsfaden mehr. Wer merkt
    es? Niemand — es sähe nach Vergesslichkeit aus.
    """
    baum = ast.parse(QUELLE)
    treffer = []
    for k in ast.walk(baum):
        # Ein `if job.thorough … close_session(...)` in irgendeiner Form.
        if not isinstance(k, ast.If):
            continue
        bed = ast.unparse(k.test)
        if "thorough" not in bed:
            continue
        rumpf = ast.unparse(k)
        if "close_session" in rumpf:
            treffer.append(f"Zeile {k.lineno}: {bed}")
    assert not treffer, (
        "die Sitzung wird bei Gründlich noch geschlossen — im Dauerbetrieb "
        f"zerschneidet das den Gesprächsfaden nach jeder Nachricht: {treffer}")

    assert "fresh=True" not in QUELLE.split("if job.thorough")[0][-2000:], \
        "es wird noch eine frische Sitzung je Anfrage erzwungen"


def _quellencheck_bleibt():
    """Was bewusst NICHT geändert wurde: der Textzusatz ist der eigentliche
    Auftrag und inhaltlich unverändert richtig."""
    assert "_THOROUGH_PREFIX" in QUELLE, "der Quellencheck-Zusatz ist verschwunden"


check("Umschalter statt Einmal-Aktion (Adams Anlass)", _umschalter_statt_einmal_aktion)
check("Zustand überlebt den Neustart, nur EINE Wahrheit", _zustand_ueberlebt_neustart)
check("Haken ist sichtbar UND ehrlich (Max trägt ihn mit)", _haken_ist_sichtbar_und_ehrlich)
check("beide Beschriftungen sind bedienbar", _beide_beschriftungen_sind_bedienbar)
check("Tiefe wird in ensure_session erzwungen (C)", _tiefe_haengt_an_ensure_session)
check("KEIN close_session mehr im Gründlich-Zweig (D — der stille Fall)",
      _kein_close_session_mehr_im_gruendlich_zweig)
check("Quellencheck-Zusatz bleibt unverändert", _quellencheck_bleibt)

print()
if fails:
    print(f"❌ {len(fails)} B3-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B3-Gründlich-Tests bestanden.")
