#!/usr/bin/env python3
# <!-- ROLLE: test-linkinbox -->
"""Verhaltenstest 5.14 — Link-Inbox.

Die Eigenschaft, an der der Punkt hängt: **Ein abgelegter Link löst KEINEN
Modelllauf und keinen Netzabruf aus.** Dazu die Abgrenzung — schreibt Adam etwas
dazu, ist es ein Auftrag und geht den gewohnten Weg.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="li-"))
os.environ["LINK_INBOX_DIR"] = str(_TMP / "inbox")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bot        # noqa: E402
import linkinbox  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _leeren():
    if linkinbox.DATEI.exists():
        linkinbox.DATEI.unlink()


def _nackter_link_wird_abgelegt():
    """Der Kern: Link allein → Ablage, kein Auftrag."""
    for t in ("https://youtu.be/abc123",
              "  https://example.com/ein-artikel.html  ",
              "https://a.de https://b.de"):
        assert linkinbox.urls_in(t), f"keine Adresse erkannt: {t}"
        assert bot._text_ohne_links(t) == "", \
            f"Resttext falsch erkannt bei {t!r}: {bot._text_ohne_links(t)!r}"


def _link_mit_auftrag_bleibt_auftrag():
    """Ein einziges sinntragendes Wort macht daraus eine Anfrage."""
    for t in ("Schau mal: https://youtu.be/abc",
              "https://youtu.be/abc — fass das zusammen",
              "wichtig https://a.de"):
        assert bot._text_ohne_links(t) != "", \
            f"Auftrag wurde als reine Ablage gewertet: {t!r}"


def _satzzeichen_zaehlen_nicht():
    for t in ("https://a.de.", "→ https://a.de", "• https://a.de", "(https://a.de)"):
        assert bot._text_ohne_links(t) == "", f"Satzzeichen als Text gewertet: {t!r}"


def _quellen_und_arten():
    faelle = {
        "https://www.youtube.com/watch?v=x": ("YouTube", "video"),
        "https://youtu.be/x": ("YouTube", "video"),
        "https://www.instagram.com/p/x": ("Instagram", "beitrag"),
        "https://github.com/a/b": ("GitHub", "code"),
        "https://irgendwas.de/seite": ("irgendwas.de", "seite"),
    }
    for url, erwartet in faelle.items():
        assert linkinbox.einordnen(url) == erwartet, \
            f"{url} → {linkinbox.einordnen(url)}, erwartet {erwartet}"


def _titel_ist_behelf_und_lesbar():
    assert linkinbox._titel_aus_adresse(
        "https://example.com/mein-toller-artikel.html") == "mein toller artikel"
    # Nichtssagende Pfade fallen auf den Namen zurück statt Unsinn zu behaupten.
    for url in ("https://example.com/", "https://example.com/12345",
                "https://example.com/a"):
        t = linkinbox._titel_aus_adresse(url)
        assert t == "example.com", f"unbrauchbarer Behelfstitel: {t!r}"


def _ablegen_und_abhaken():
    _leeren()
    e = linkinbox.ablegen("https://youtu.be/abc", 4242, 7)
    assert e.quelle == "YouTube" and e.art == "video"
    assert len(linkinbox.offene()) == 1, "Eintrag fehlt"
    # Derselbe Link doppelt → nur einmal geführt.
    linkinbox.ablegen("https://youtu.be/abc", 4242, 8)
    assert len(linkinbox.offene()) == 1, "Link doppelt geführt"
    assert linkinbox.abhaken("https://youtu.be/abc", "verarbeitet: kurz")
    assert linkinbox.offene() == [], "abgehakter Link steht noch offen"
    assert linkinbox.finden("https://youtu.be/abc") is not None, \
        "abgehakter Eintrag ist verschwunden statt erledigt"


def _uebersicht_ohne_eintraege():
    _leeren()
    assert "leer" in linkinbox.uebersicht(), "leere Ablage wird nicht benannt"


def _kein_netzabruf_beim_ablegen():
    """Nachweis statt Vertrauen: Das Modul öffnet keine Verbindung."""
    quelle = (Path(__file__).resolve().parent.parent / "linkinbox.py").read_text(
        encoding="utf-8")
    for verdacht in ("requests", "urllib.request", "urlopen", "httpx",
                     "socket", "aiohttp"):
        assert verdacht not in quelle, \
            f"linkinbox.py greift möglicherweise aufs Netz zu: {verdacht}"


check("nackter Link → Ablage", _nackter_link_wird_abgelegt)
check("Link mit Wort → bleibt Auftrag", _link_mit_auftrag_bleibt_auftrag)
check("Satzzeichen zählen nicht als Text", _satzzeichen_zaehlen_nicht)
check("Quelle und Art aus der Adresse", _quellen_und_arten)
check("Behelfstitel lesbar, sonst Rückfall", _titel_ist_behelf_und_lesbar)
check("ablegen, nicht doppeln, abhaken", _ablegen_und_abhaken)
check("leere Ablage wird benannt", _uebersicht_ohne_eintraege)
check("kein Netzabruf im Modul", _kein_netzabruf_beim_ablegen)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle 5.14-Link-Inbox-Tests bestanden.")
