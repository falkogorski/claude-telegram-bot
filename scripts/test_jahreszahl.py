#!/usr/bin/env python3
# <!-- ROLLE: test-jahreszahl -->
"""Jahreszahlen — EINE Erkennung, drei Sprechwege (26.09.2026).

Claudias Auftrag „Jahreszahlen in Klammern" (Adam 17:31, Daumen) mit
Engywucks Auflage aus Zettel f4 Teil 2: Es gibt drei Sprechwege, und jeder
erkannte Jahre selbst — edge-tts las „RL (1922)" als Menge, Azure dagegen
jede vierstellige Zahl als Jahr. Hier laeuft Claudias Tabelle **je Sprechweg**:
edge (`_strip_markdown_for_tts`), Piper (`_fuer_lokale_stimme`), Azure
(`ssml_text`). Keine Attrappe noetig — alles reine Textfunktionen.

Gegenproben (vorab benannt): Klammerregel in `jahreszahl.art` entfernen →
die Zeilen „(1922)" und „(1936, …)" je Weg rot. Azure zurueck auf „jede Zahl
ein Jahr" → die Azure-Zeilen fuer „(1500 Zeichen)" und „(1500 Euro)" rot.
"""
import os
import sys
from pathlib import Path

os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["TTS_ROT_LOKAL"] = "aus"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                   # noqa: E402
import jahreszahl                            # noqa: E402
import sprachausgabe_azure as az             # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    print(f"  {'✅' if bedingung else '❌'} {name}" + ("" if bedingung else f" — {gemessen}"))
    if not bedingung:
        fehler.append(name)


def _az(zahl: str, art: str) -> str:
    return f'<say-as interpret-as="{art}"' + (' format="y"' if art == "date" else "") + f">{zahl}</say-as>"


# Eingabe · edge/Piper-Erwartung · Azure-Erwartung (Teilstueck)
TABELLE = [
    ("RL (1922)", "neunzehnhundertzweiundzwanzig", _az("1922", "date")),
    ("8C 2900 (1936, Kleinserie)", "neunzehnhundertsechsunddreißig, Kleinserie", _az("1936", "date")),
    ("24 HP (1910–1914)", "neunzehnhundertzehn bis neunzehnhundertvierzehn", _az("1914", "date")),
    ("Limit (1500 Zeichen)", "(1500 Zeichen)", _az("1500", "cardinal")),
    ("Kosten (1500 Euro)", "(1500 Euro)", _az("1500", "cardinal")),
    ("Junior (2024)", "(2024)", _az("2024", "date")),
]

print("== A. Claudias Tabelle, je Sprechweg ==")
for eingabe, erwartet, azure in TABELLE:
    e = bot._strip_markdown_for_tts(eingabe)
    zeile(f"edge:  {eingabe}", erwartet in e, e)
    p = bot._fuer_lokale_stimme(eingabe)
    zeile(f"Piper: {eingabe}", erwartet in p, p)
    a = az.ssml_text(eingabe)
    zeile(f"Azure: {eingabe}", azure in a, a)

print("== B. Die eine Funktion ==")
t = "Im Text (1927) und (1500 Zeichen) und 1985 Teilnehmer."
arten = [jahreszahl.art(t, t.index(z), t.index(z) + 4) for z in ("1927", "1500", "1985")]
zeile("art(): Klammer → jahr, Einheit → menge, Einheit dahinter → menge",
      arten == ["jahr", "menge", "menge"], str(arten))
t = "Sie kamen 1985 an."
zeile("art(): ohne jeden Hinweis → unklar", jahreszahl.art(t, 10, 14) == "unklar",
      jahreszahl.art(t, 10, 14))
zeile("alle drei Wege rufen dieselbe Funktion (kein eigenes Jahresmuster mehr)",
      bot._JAHR_HINWEIS is jahreszahl.JAHR_HINWEIS
      and bot._MENGEN_EINHEIT is jahreszahl.MENGEN_EINHEIT
      and "jahreszahl.art(" in Path(az.__file__).read_text(),
      "bot oder azure mit eigener Kopie")

print("== C. Nebenbefunde und Grenzen ==")
e = bot._strip_markdown_for_tts("von 1500 bis 1800 Zeichen")
zeile("Bereich mit Einheit bleibt Menge, auch mit Jahres-Wort davor (war: fünfzehnhundert)",
      "1500 bis 1800 Zeichen" in e, e)
e = bot._normalize_jahreszahlen("gegründet 1936,5 Prozent; gegründet 1901.")
zeile("Dezimalzahl bleibt Zahl, Satzpunkt verdeckt das Jahr nicht",
      "1936,5" in e and "neunzehnhunderteins" in e, e)
a = az.ssml_text("Maßstab 1985 Teilnehmer")
zeile("Azure: Menge mit Einheit nicht mehr als Jahr", _az("1985", "cardinal") in a, a)
e = bot._strip_markdown_for_tts("Teilnehmer (1200)")
zeile("BEKANNTE GRENZE (dokumentiert): Menge ohne Einheit allein in Klammern liest sich als Jahr",
      "zwölfhundert" in e, e)

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Jahreszahlen bestanden.")
