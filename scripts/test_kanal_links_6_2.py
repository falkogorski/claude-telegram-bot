#!/usr/bin/env python3
# <!-- ROLLE: test-kanal-links -->
"""Punkt 6.2/6.4 — wie Kanal-Verweise gebaut werden.

**Der eigentliche Befund war nicht ein Fehler, sondern eine Gabelung.** Für
denselben Zweck — Adam einen Kanal verlinken — gab es zwei Wege: die zentrale
Funktion ``_channel_title_link_html`` (drei Stellen) und einen von Hand
gebauten Anchor um ``_channel_url`` (zwei Stellen). **Zwei Wege für dieselbe
Sache heißt, dass einer von beiden falsch ist und niemand merkt, welcher.**

**Was hier ausdrücklich NICHT behauptet wird:** dass ``tg://`` besser sei als
``https://t.me/c/``. Das lässt sich am Mac nicht messen — es hängt am
Verhalten der Telegram-App auf Adams iPhone. Ein Hinweis spricht sogar
dagegen: Der Kommentar an ``_channel_post_markup`` hält fest, dass
**tg://-Textlinks einen „Link öffnen?"-Dialog auslösen**, Buttons dagegen
nicht. Diese Prüfung sichert deshalb nur, dass es **eine** Stelle gibt, an der
die Entscheidung fällt — dann ist ein späterer Wechsel eine Zeile statt fünf.

**Ein Wort zur Entstehung, weil es die Lehre trägt:** Die vierte Prüfung
verlangte zuerst, Inline-Knöpfe müssten beim ``https``-Weg bleiben — ich hatte
jenen Kommentar als Vorschrift gelesen. Er ist aber eine **Begründung**: Weil
Knöpfe den Dialog nicht auslösen, dürfen sie ``tg://`` gefahrlos nutzen, und
genau das tun sie. Der Prüfer wurde rot und hat **meine Lesart widerlegt, nicht
den Code.** Ein Prüfer, der nur bestätigt, was der Schreiber ohnehin glaubt,
hätte hier geschwiegen.
"""
import os
import re
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="k62-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

QUELLE = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
fails = []


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


def _privater_kanal_bekommt_den_deep_link():
    """Ausgeführt: was die Funktion tatsächlich zurückgibt."""
    html = bot._channel_title_link_html(-1001234567890, "Werkstatt")
    assert "tg://privatepost?channel=1234567890" in html, \
        f"kein Deep-Link für den privaten Kanal: {html}"
    assert "Werkstatt" in html, "der Titel fehlt im Link"


def _oeffentlicher_kanal_bekommt_die_adresse():
    html = bot._channel_title_link_html(-1001234567890, "Werkstatt",
                                        username="werkstatt")
    assert "https://t.me/werkstatt" in html, \
        f"öffentlicher Kanal ohne t.me-Adresse: {html}"
    assert "tg://" not in html, "öffentlicher Kanal sollte keinen tg://-Link tragen"


def _der_titel_wird_maskiert():
    """Ein Kanalname mit spitzen Klammern darf das HTML nicht zerreißen."""
    html = bot._channel_title_link_html(-1001234567890, "<b>böse</b>")
    assert "&lt;b&gt;" in html, f"der Titel wurde nicht maskiert: {html}"


def _der_knopf_springt_auf_den_beitrag():
    """**Diese Prüfung hat mich beim Schreiben selbst korrigiert.**

    Ihre erste Fassung verlangte, Inline-Knöpfe müssten beim ``https``-Weg
    bleiben — ich hatte den Kommentar an ``_channel_post_markup`` so gelesen.
    Er sagt aber etwas anderes: **Buttons lösen den Dialog nicht aus, anders
    als tg://-Textlinks.** Das ist keine Vorschrift für den Knopf, sondern die
    Begründung, warum der Knopf ``tg://`` gefahrlos nutzen darf.

    Damit dreht sich die Frage um: Nicht der Knopf ist der Zweifelsfall,
    sondern der **Textlink** — dort kostet der Deep-Link einen zusätzlichen
    Tipp. Ob das den direkten Sprung wert ist, entscheidet Adams Test am
    iPhone, nicht diese Datei.

    Geprüft wird deshalb nur, was feststeht: Mit Beitrags-Bezug springt der
    Knopf auf den **Beitrag**, ohne Bezug in den **Kanal**.
    """
    mit = bot._channel_post_markup(-1001234567890, 42)
    adressen = [b.url for reihe in mit.inline_keyboard for b in reihe if b.url]
    assert adressen, "der Knopf trägt keine Adresse"
    assert "post=42" in adressen[0], \
        f"der Knopf springt nicht auf den Beitrag: {adressen[0]}"

    ohne = bot._channel_post_markup(-1001234567890)
    a2 = [b.url for reihe in ohne.inline_keyboard for b in reihe if b.url][0]
    assert "post=" not in a2, f"ohne Beitrags-Bezug darf kein Beitrag stehen: {a2}"


def _nur_eine_stelle_entscheidet_ueber_die_linkart():
    """Kein handgebauter Anchor mehr neben der zentralen Funktion.

    **Zugegeben ein Text-Prüfer** — die Alternative wäre, zwei Telegram-Handler
    mit vollem Attrappen-Gerüst zu fahren, und das prüfte am Ende die Attrappe.
    Gesucht wird ein Anchor, dessen Adresse aus ``_channel_url`` stammt.
    """
    handgebaut = re.findall(r'<a href="\{url\}"', QUELLE)
    assert not handgebaut, (
        f"{len(handgebaut)} handgebaute Kanal-Anchor gefunden — die Linkart "
        "wird wieder an mehreren Stellen entschieden")


check("privater Kanal bekommt den Deep-Link", _privater_kanal_bekommt_den_deep_link)
check("öffentlicher Kanal bekommt die Adresse", _oeffentlicher_kanal_bekommt_die_adresse)
check("der Titel wird maskiert", _der_titel_wird_maskiert)
check("der Knopf springt auf den Beitrag", _der_knopf_springt_auf_den_beitrag)
check("nur eine Stelle entscheidet", _nur_eine_stelle_entscheidet_ueber_die_linkart)

print()
if fails:
    print(f"❌ {len(fails)} Kanal-Link-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Kanal-Link-Tests bestanden.")
