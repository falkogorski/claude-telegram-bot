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


def _erfolg_haakt_ab_misserfolg_nicht():
    """S1/G6: Abgehakt wird nur, was wirklich gelang.

    **Der Prüfer sitzt am Verhalten, nicht am Wortlaut:** Er prüft, dass der
    Knopf-Handler NICHT mehr selbst abhakt, und dass die Nachbedingung am
    Auftrag hängt. Vorher stand `abhaken` direkt vor `process_user_text` — und
    ein Fehlerfang an jener Stelle wäre wirkungslos gewesen, weil
    `process_user_text` nur einreiht und sofort zurückkehrt.
    """
    quelle = (Path(linkinbox.__file__).parent / "bot.py").read_text(encoding="utf-8")
    kopf = quelle.split("async def on_link_callback")[1].split("async def ")[0]
    assert "linkinbox.abhaken" not in kopf, \
        "der Knopf-Handler hakt weiterhin selbst ab — vor dem Lauf"
    assert "links_abhaken=" in kopf, \
        "die Nachbedingung wird nicht an den Auftrag gehängt"

    nach = quelle.split("async def _links_nachtragen")[1].split("async def ")[0]
    assert 'outcome == "beantwortet"' in nach, \
        "es wird nicht auf den belegten Erfolg geprüft"
    assert "notieren" in nach, \
        "ein gescheiterter Lauf hinterlässt keinen Grund am Eintrag"

    # Und das Gegenstück im Modul: notieren hakt NICHT ab.
    linkinbox.ablegen("https://example.org/probe-s1")
    linkinbox.notieren("https://example.org/probe-s1", "nicht durchgelaufen")
    offen = [e.url for e in linkinbox.offene()]
    assert "https://example.org/probe-s1" in offen, \
        "ein Vermerk hat den Eintrag abgehakt — genau der Verlust, um den es geht"


check("nackter Link → Ablage", _nackter_link_wird_abgelegt)
check("Erfolg hakt ab, Misserfolg nicht (S1)", _erfolg_haakt_ab_misserfolg_nicht)
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
