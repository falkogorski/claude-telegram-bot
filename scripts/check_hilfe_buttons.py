#!/usr/bin/env python3
"""8.6 (b) — Doku-Spiegel-Prüfskript: /hilfe, Befehlsmenü und Tastatur dürfen
nicht auseinanderlaufen.

Hintergrund (8.6): Am 17.07. wurde die Tastatur verschlankt, der /hilfe-Text
blieb stehen — der Bot beschrieb ein Layout, das es nicht mehr gab. Diese Drift
macht nichts kaputt und fällt deshalb in keinem Funktionstest auf; sie
untergräbt still das Vertrauen in jede Auskunft des Bots. Dieses Skript macht
sie zum harten Fehler.

Prüfungen:
  (1) Jeder Befehl im setMyCommands-Menü hat einen CommandHandler.
  (2) Jeder CommandHandler ist im /hilfe-Text beschrieben — und umgekehrt
      existiert jeder in /hilfe genannte Befehl als Handler.
  (3) Jeder Tastatur-Knopf (alle Renderings) steht im /hilfe-Text als
      Marker-Begriff und die dort behauptete Knopf-Anzahl stimmt.

Aufruf:  .venv/bin/python scripts/check_hilfe_buttons.py   (Exit 0 = konsistent)
Läuft auch im 4-Uhr-Check (8.1) mit, sobald der gebaut ist.
"""
from __future__ import annotations

import inspect
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"  # erzwungen: hermetisch (nie geerbte echte UID)

import bot  # noqa: E402

FEHLER: list[str] = []


def fail(msg: str) -> None:
    FEHLER.append(msg)
    print(f"✗ {msg}")


def ok(msg: str) -> None:
    print(f"✓ {msg}")


src = Path(bot.__file__).read_text(encoding="utf-8")
handler_cmds = set(re.findall(r'CommandHandler\("(\w+)"', src))

# `[GEAENDERT 2026-08-20]` Menue und Hilfetext kommen jetzt aus EINER Quelle
# (`bot._BEFEHLE`) und werden zur Laufzeit sortiert. Damit lassen sie sich
# nicht mehr aus dem Quelltext lesen — was ein Gewinn ist: Der Pruefer misst
# seither, was tatsaechlich herauskommt, statt wie es dasteht.
#
# **Das war kein freiwilliger Umbau.** Nach der Umstellung meldete er 27
# Handler ohne /hilfe-Eintrag, obwohl alle 27 darin stehen — ein Text-Pruefer,
# dem man den Text wegnimmt, wird blind und nicht rot. Genau die Klasse vom
# 18.08.
hilfe_src = inspect.getsource(bot.cmd_hilfe)   # fuer die Tastatur-Pruefungen
befehle = bot._befehle_sortiert()
menu_cmds = {name for name, kurz, _lang in befehle if kurz}
hilfe_cmds = {name for name, _kurz, _lang in befehle}

# (1) Menü ⊆ Handler
fehlend = menu_cmds - handler_cmds
if fehlend:
    fail(f"Befehle im „/“-Menü ohne Handler: {sorted(fehlend)}")
else:
    ok(f"Befehlsmenü vollständig verdrahtet ({len(menu_cmds)} Einträge)")

# (1b) Die Sortierung — Claudias fehlender Pruefer, ausfuehrend gemessen.
# **Der erwartete Wert steht HIER, nicht in bot.py** — sonst prueft der
# Pruefer die Vorgabe gegen sich selbst und kann nie rot werden. Genau daran
# ist die erste Gegenprobe gescheitert: Wird `_BEFEHL_ZUERST` in bot.py
# geaendert, aendert sich die Erwartung mit, und der Bruch bleibt unsichtbar.
# (Dieselbe Klasse wie die pgrep-Nachstellung vom 20.08. frueh, die dasselbe
# Messartefakt erzeugte, das sie nachweisen sollte.)
ZUERST_ERWARTET = "stopp"   # Adams Ausnahme, 20.08. — bewusst hier verankert
namen = [n for n, _k, _l in befehle]
if namen[0] != ZUERST_ERWARTET:
    fail(f"/{ZUERST_ERWARTET} steht nicht vorn, sondern /{namen[0]}")
elif namen[1:] != sorted(namen[1:]):
    ersteAbweichung = next(
        (a for a, b in zip(namen[1:], sorted(namen[1:])) if a != b), "?")
    fail(f"das Befehlsmenue ist nicht alphabetisch (bei /{ersteAbweichung})")
else:
    ok(f"Menue sortiert, /{ZUERST_ERWARTET} vorangestellt ({len(namen)} Befehle)")

# (2) Handler ↔ /hilfe (beide Richtungen)
nicht_dokumentiert = handler_cmds - hilfe_cmds
if nicht_dokumentiert:
    fail(f"Handler ohne /hilfe-Eintrag: {sorted(nicht_dokumentiert)}")
else:
    ok(f"Alle {len(handler_cmds)} Befehle in /hilfe beschrieben")
geister = hilfe_cmds - handler_cmds
if geister:
    fail(f"/hilfe nennt Befehle, die es nicht gibt: {sorted(geister)}")
else:
    ok("Kein Geister-Befehl in /hilfe")

# (3) Tastatur ↔ /hilfe
bot._STT_MODELS.clear()
bot._STT_MODELS.update({"small": "x", "medium": "y"})
buttons: set[str] = set()
for active in ("small", "medium"):
    bot._ACTIVE_STT = active
    for model in ("haiku", "sonnet", "opus", "fable"):
        for effort in (None, "low", "max"):
            for row in bot._main_keyboard(False, model, effort).keyboard:
                buttons.update(b.text for b in row)

# Knopf-Anzahl einer konkreten Tastatur gegen die Behauptung in /hilfe („(9)").
eine_tastatur = [b for row in bot._main_keyboard(False, "sonnet", None).keyboard
                 for b in row]
m = re.search(r"Buttons in der Tastatur \((\d+)\)", hilfe_src)
if not m:
    fail("/hilfe nennt keine Knopf-Anzahl mehr — Abschnitt umbenannt?")
elif int(m.group(1)) != len(eine_tastatur):
    fail(f"/hilfe behauptet {m.group(1)} Knöpfe, Tastatur zeigt {len(eine_tastatur)}")
else:
    ok(f"Knopf-Anzahl stimmt ({len(eine_tastatur)})")

# Jeder Knopf muss über einen Marker in /hilfe auffindbar sein. Für Zustands-
# Varianten (✓/Pfeile) genügt der Kern-Marker.
marker = {"🟣 Haiku", "🟡 Sonnet", "🔵 Opus", "🟠 Fable",
          "⚡ Schnell", "⚖️ Normal", "🚀 Max", "🎙️", "🎯 Gründlich"}
fehlende_marker = [mk for mk in marker if mk not in hilfe_src]
if fehlende_marker:
    fail(f"Tastatur-Marker fehlen in /hilfe: {fehlende_marker}")
else:
    ok("Alle Tastatur-Gruppen in /hilfe beschrieben")
unerklaert = [b for b in buttons
              if not any(b.startswith(mk) or mk in b for mk in marker)]
if unerklaert:
    fail(f"Knöpfe ohne /hilfe-Marker: {unerklaert}")
else:
    ok(f"Alle {len(buttons)} Knopf-Varianten durch Marker abgedeckt")

if FEHLER:
    print(f"\n{len(FEHLER)} DRIFT(S) GEFUNDEN — nutzerseitige Texte anpassen!")
    sys.exit(1)
print("\nDoku-Spiegel konsistent.")
