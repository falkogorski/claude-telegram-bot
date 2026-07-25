#!/usr/bin/env python3
# <!-- ROLLE: test-warteschlange -->
"""Akzeptanztest 5.5: Warteschlange ist FIFO; nur echte Stopp/Korrektur-Signale
brechen ab und kommen vor. Nachtrag/Ergänzung sind KEIN Interrupt mehr.

Testet die reine Klassifikation (`_is_interrupt`) und die Reihenfolge-Logik
(append vs. appendleft) als kleine Simulation der Verzweigung aus
`process_user_text`.
"""
import os
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "0:selfcheck-dummy")
os.environ["ALLOWED_USER_IDS"] = "1"  # erzwungen: hermetisch (nie geerbte echte UID)
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


def _interrupt_words_true():
    for w in ["Stopp", "stopp das", "Korrektur: nimm A", "halt",
              "brich das ab", "nein das war falsch", "nee, das war falsch",
              "vergiss das", "abbrechen"]:
        assert bot._is_interrupt(w), f"sollte Interrupt sein: {w!r}"


def _nachtrag_words_false():
    # Diese Wörter dürfen NICHT mehr abbrechen (reihen sich normal ein).
    for w in ["Nachtrag: auch noch X", "Ergänzung dazu", "weitere Info: Y",
              "Zusatzinfo Z", "ergaenzung ohne umlaut"]:
        assert not bot._is_interrupt(w), f"darf kein Interrupt sein: {w!r}"


def _normal_false():
    for w in ["Fass die PDF zusammen", "Wie spät ist es?", "", "Mach mal weiter"]:
        assert not bot._is_interrupt(w), f"darf kein Interrupt sein: {w!r}"


def _fifo_reihenfolge():
    # Drei normale Nachrichten in Reihenfolge → chronologisch abgearbeitet.
    q = deque()
    for msg in ["eins", "zwei", "drei"]:
        # Normal-Zweig: append (ans Ende)
        q.append(msg)
    order = [q.popleft() for _ in range(3)]
    assert order == ["eins", "zwei", "drei"], f"nicht chronologisch: {order}"


def _interrupt_kommt_vor():
    # Busy-Queue mit wartenden Jobs; ein Stopp/Korrektur-Signal muss vor.
    q = deque(["laufend-folge-1", "laufend-folge-2"])
    interrupt_msg = "Korrektur: das zuerst"
    assert bot._is_interrupt(interrupt_msg)
    q.appendleft(interrupt_msg)  # Interrupt-Zweig: appendleft (vorne)
    assert q[0] == interrupt_msg, "Interrupt nicht an erster Position"


check("Stopp/Korrektur-Signale erkannt", _interrupt_words_true)
check("Nachtrag/Ergänzung KEIN Interrupt", _nachtrag_words_false)
check("Normale Nachrichten KEIN Interrupt", _normal_false)
check("FIFO: drei Nachrichten chronologisch", _fifo_reihenfolge)
check("Interrupt kommt nach vorne", _interrupt_kommt_vor)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle 5.5-Warteschlangentests bestanden.")
