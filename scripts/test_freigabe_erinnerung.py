#!/usr/bin/env python3
"""Prueft die Freigabe-Erinnerungen — AUSGEFUEHRT, nicht gelesen (N-1).

**Adams Anlass, 31.08. 22:47:** *„Ich hatte eben den Permission Request
uebersehen … Bevor du den auslaufen laesst, koennte es noch zwei Reminder
geben."* Und der Grund: *„Man ist mal mit was anderem beschaeftigt, wird
abgelenkt, hat ein Telefonat."*

**Die zweite Zeile ist die wichtigere.** Eine Erinnerung, die nach der
Entscheidung weiterschreibt, ist schlimmer als keine — Adam nennt so etwas
„sehr stoerend", und ein stoerender Mechanismus wird abgeschaltet. Deshalb
misst dieser Pruefstand beide Richtungen: dass erinnert wird, **und dass es
sofort aufhoert**.

Gefahren wird in Sekunden statt Minuten (`frist_s`/`takt_s`) — die Logik ist
dieselbe, der Lauf dauert Sekundenbruchteile.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Hermetik wie in den Geschwister-Pruefstaenden: erzwungen, nicht ergaenzt.
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"

import bot  # noqa: E402

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


print("== Freigabe-Erinnerungen (N-1) ==")


async def _lauf():
    # ---- ① Es wird erinnert, solange niemand entscheidet
    gerufen: list[int] = []

    async def merken(minuten: int) -> None:
        gerufen.append(minuten)

    fut = asyncio.get_running_loop().create_future()
    erg = await bot.warte_auf_freigabe(fut, merken, frist_s=0.4, takt_s=0.1)
    zeile("ohne Entscheidung wird erinnert", len(gerufen) >= 2,
          gemessen=f"{len(gerufen)} Erinnerung(en): {gerufen}")
    zeile("nach Fristablauf ist die Antwort None (= verweigern)",
          erg is None, gemessen=repr(erg))
    zeile("die letzte Erinnerung kommt NICHT auf den Fristablauf",
          len(gerufen) == 3,
          gemessen=f"{len(gerufen)} statt 3 bei 4 Abschnitten — die letzte "
                   "waere eine Erinnerung ohne verbleibende Zeit")

    # ---- ② Sie verstummen sofort bei der Entscheidung
    #
    # **Die Zeile, die Adam sofort merken wuerde, wenn sie fehlt.** Ein eigener
    # Zeitgeber wuerde hier weiterschreiben.
    gerufen2: list[int] = []

    async def merken2(minuten: int) -> None:
        gerufen2.append(minuten)

    fut2 = asyncio.get_running_loop().create_future()
    asyncio.get_running_loop().call_later(0.15, lambda: fut2.set_result("allow"))
    erg2 = await bot.warte_auf_freigabe(fut2, merken2, frist_s=2.0, takt_s=0.1)
    zeile("die Entscheidung kommt an", erg2 == "allow", gemessen=repr(erg2))
    zeile("nach der Entscheidung wird NICHT weiter erinnert",
          len(gerufen2) <= 2,
          gemessen=f"{len(gerufen2)} Erinnerungen trotz Entscheidung nach "
                   "1,5 Abschnitten — sie muessten sofort aufhoeren")

    # ---- ③ Das Future ueberlebt die Abschnitte (shield)
    #
    # Ohne `asyncio.shield` bricht `wait_for` beim ersten Zeitablauf das Future
    # ab. Adams Knopfdruck liefe dann ins Leere — die Anfrage waere schlechter
    # dran als mit einem einzigen langen Warten.
    gerufen3: list[int] = []

    async def merken3(_m: int) -> None:
        gerufen3.append(_m)

    fut3 = asyncio.get_running_loop().create_future()
    asyncio.get_running_loop().call_later(0.25, lambda: (
        None if fut3.done() else fut3.set_result("deny")))
    # **`CancelledError` wird gefangen, damit die Zeile ROT wird statt den Lauf
    # zu toeten.** Die Gegenprobe (shield entfernen) hat genau das gezeigt: Ohne
    # Schild bricht `wait_for` das Future ab, der Fehler steigt durch und der
    # Pruefstand stirbt mit einem Traceback. Ein abstuerzender Pruefer meldet
    # zwar auch „nicht gruen", aber im Regressionslauf ist eine benannte Zeile
    # die brauchbarere Auskunft.
    try:
        erg3 = await bot.warte_auf_freigabe(fut3, merken3, frist_s=2.0, takt_s=0.1)
        _ueberlebt = erg3 == "deny" and not fut3.cancelled()
        _wie = f"erg={erg3!r} cancelled={fut3.cancelled()}"
    except asyncio.CancelledError:
        _ueberlebt = False
        _wie = "CancelledError — das Future wurde abgebrochen (shield fehlt)"
    zeile("das Future ueberlebt mehrere Abschnitte (shield greift)",
          _ueberlebt, gemessen=_wie)

    # ---- ④ Eine misslungene Erinnerung beendet die Anfrage nicht
    #
    # Sie ist Beiwerk; das Warten ist die Sache. Im Rueckruf faengt ein
    # try/except — hier wird gemessen, dass die Schleife selbst nicht stirbt,
    # wenn der Erinnerer wirft.
    async def wirft(_m: int) -> None:
        raise RuntimeError("Telegram nicht erreichbar")

    fut4 = asyncio.get_running_loop().create_future()
    asyncio.get_running_loop().call_later(0.25, lambda: (
        None if fut4.done() else fut4.set_result("allow")))
    try:
        erg4 = await bot.warte_auf_freigabe(
            fut4, lambda m: wirft(m), frist_s=2.0, takt_s=0.1)
        _lief_durch = erg4 == "allow"
        _grund = repr(erg4)
    except Exception as e:                                   # noqa: BLE001
        _lief_durch = False
        _grund = f"{type(e).__name__}: {e}"
    zeile("ein werfender Erinnerer beendet die Anfrage NICHT",
          _lief_durch, gemessen=_grund)


asyncio.run(_lauf())

# ---- ⑤ Die drei Zahlen kommen aus EINER Groesse
#
# Vorher standen `1800`, „nach 30 Minuten" und „did not respond in 3 min"
# nebeneinander — drei Zahlen, zwei davon falsch. Gemessen wird der Quelltext
# des Rueckrufs: keine nackte Frist-Zahl mehr, und beide Texte rechnen aus
# derselben Konstanten.
_quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
zeile("die Frist ist eine Einstellgroesse",
      "FREIGABE_FRIST_S = int(os.environ" in _quelle)
zeile("Ablauf-Meldung und Abweisungstext rechnen aus derselben Groesse",
      _quelle.count("_frist_min") >= 3,
      gemessen=f"_frist_min kommt {_quelle.count('_frist_min')}-mal vor")
# **Gemessen wird die Rueckgabe, nicht das Vorkommen der Zahl im Text.**
# Die erste Fassung suchte die alte Zeichenkette im ganzen Quelltext — und
# stolperte ueber den Erklaerkommentar, der sie zitiert. Das ist die Regel
# „ein Pruefer darf die Beschreibung seines eigenen Gegenstands nicht
# anschlagen"; wer sie bricht, baut einen Pruefer, der binnen einer Woche
# abgeschaltet wird.
zeile("der Abweisungstext rechnet, statt eine Zahl zu tragen",
      'f"user did not respond in {_frist_min} min"' in _quelle,
      gemessen="der Text traegt keine berechnete Frist")

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Freigabe-Erinnerungen bestanden")
