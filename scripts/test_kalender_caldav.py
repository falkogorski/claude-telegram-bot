#!/usr/bin/env python3
# <!-- ROLLE: test-kalender -->
"""Verhaltenstest Kalender/CalDAV — läuft OHNE Zugangsdaten.

Geprüft wird, was ohne Apple-Konto prüfbar ist und trotzdem trägt: die
Aufbereitung für Menschen, die Namenswahl der Sammlung und — vor allem — dass
ein fehlender Zugang **einen deutlichen Fehler** erzeugt statt eines stillen
Leerlaufs. Ein halb verbundener Kalender wäre schlimmer als keiner, weil man
ihm glauben würde.
"""
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Zugang bewusst entfernen — der Test darf niemals an Apple funken.
os.environ.pop("ICLOUD_CALDAV_USER", None)
os.environ.pop("ICLOUD_CALDAV_APP_PASSWORT", None)

import kalender as k  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _ohne_zugang_deutlicher_fehler():
    assert not k.zugang_vorhanden(), "Testaufbau falsch: Zugang ist gesetzt"
    for aufruf in (k.sammlungen_auflisten, k.termine_lesen, k.aufgaben_lesen):
        try:
            aufruf()
        except k.NichtEingerichtet as e:
            assert "anwendungsspezifisch" in str(e).lower(), \
                "die Meldung nennt nicht das anwendungsspezifische Kennwort"
        except Exception as e:
            raise AssertionError(f"falsche Fehlerart bei {aufruf.__name__}: {e!r}")
        else:
            raise AssertionError(f"{aufruf.__name__} lief ohne Zugang durch!")


def _termin_lesbar():
    t = k.Termin(beginn=dt.datetime(2026, 7, 28, 14, 30),
                 ende=dt.datetime(2026, 7, 28, 15, 30),
                 titel="Zahnarzt", ort="Köln")
    s = t.lesbar()
    assert "Dienstag" in s, f"Wochentag falsch oder fehlt: {s}"
    assert "28.07." in s and "14:30 bis 15:30" in s, f"Zeitangabe unbrauchbar: {s}"
    assert "Köln" in s, "Ort fehlt"


def _ganztags_sagt_ganztaegig():
    t = k.Termin(beginn=dt.datetime(2026, 7, 26, 0, 0), ende=None,
                 titel="Urlaub", ganztags=True)
    assert "ganztägig" in t.lesbar(), "ganztägiger Termin nennt eine Uhrzeit"


def _aufgabe_ohne_frist_bleibt_schlicht():
    a = k.Aufgabe(titel="Reifen wechseln")
    assert a.lesbar() == "Reifen wechseln", f"unnötige Zusätze: {a.lesbar()}"
    b = k.Aufgabe(titel="Rechnung", faellig=dt.datetime(2026, 7, 30, 9, 0))
    assert "30.07." in b.lesbar() and "fällig" in b.lesbar(), b.lesbar()


def _falscher_name_wird_benannt():
    """Kein stilles Ausweichen auf eine beliebige Sammlung."""
    class _K:
        def __init__(self, n):
            self.name = n

    class _P:
        def calendars(self):
            return [_K("Privat"), _K("Arbeit")]

    assert k._kalender_waehlen(_P(), "privat").name == "Privat"
    assert k._kalender_waehlen(_P(), "ARBEIT").name == "Arbeit"
    try:
        k._kalender_waehlen(_P(), "Garten")
    except LookupError as e:
        assert "Privat" in str(e) and "Arbeit" in str(e), \
            "die Meldung nennt die vorhandenen Sammlungen nicht"
    else:
        raise AssertionError("unbekannter Name wurde stillschweigend ersetzt!")


# **[RANG A, Stelle 8 — 29.08.]** Zwei Fehler in vier Zeilen, und beide sind
# Musterfaelle aus dem Entkernungs-Befund.
#
# **(1) Sie verlangte eine Schreibweise.** Gesucht wurde `passwort="` — ohne
# Leerzeichen. Ein hartkodiertes `PASSWORT = "abcd-efgh-ijkl-mnop"`, also die
# Form, die jeder Mensch tippt, ging durch. Ein Prüfer, der Formatierung
# verlangt statt Bedeutung zu messen, ist umgehbar, ohne dass jemand ihn
# umgehen wollte.
#
# **(2) Sie las EINE Datei.** `kalender.py` war die Datei, an die man beim
# Schreiben dachte; jedes andere Modul blieb ungeprüft. Das ist die
# Mengen-Lehre dieses Projekts: *Jede Prüfung läuft über eine Menge — und es
# ist immer die, die dem Erbauer am Bautag einfiel.*
#
# Jetzt: die **Form des Geheimnisses** statt der Schreibweise der Zuweisung,
# über **alle Produktivmodule** statt über eine Datei.
import re as _re

# Vier Vierergruppen — die Form eines Apple-App-Kennworts. Sie ist
# charakteristisch genug, um ohne Schlüsselwort davor zu erkennen.
_APP_KENNWORT = _re.compile(r"""["'][a-z]{4}-[a-z]{4}-[a-z]{4}-[a-z]{4}["']""")
# Zuweisung eines Geheimnisses mit BELIEBIGEM Abstand und beliebigem
# Trennzeichen — der eine Punkt, an dem die alte Fassung scheiterte.
_ZUWEISUNG = _re.compile(
    r"""(?:password|passwort|kennwort|secret|api_?key|token)\s*[:=]\s*["'][^"'\n]{6,}["']""",
    _re.IGNORECASE)
# Erkennbare Platzhalter — sonst schlägt der Prüfer auf jedem Beispiel an und
# wird binnen einer Woche abgeschaltet.
_PLATZHALTER = _re.compile(
    r"(dein|your|hier|xxx|\.\.\.|<|\$\{|os\.environ|getenv|example|dummy|"
    r"attrappe|probe|test)", _re.IGNORECASE)


def _produktivmodule() -> list[Path]:
    """Alle Module, die im Betrieb laufen — als MENGE über eine Eigenschaft.

    Nicht über eine Namensliste (die altert) und nicht über eine Endung im
    Ordner (die verfehlt Unterordner). Prüfdateien sind ausgenommen: Sie
    enthalten notwendigerweise Beispielwerte, und ein Prüfer, der die eigenen
    Prüfstände anschlägt, wird abgeschaltet.
    """
    wurzel = Path(__file__).resolve().parent.parent
    dateien = list(wurzel.glob("*.py"))
    dateien += [d for d in (wurzel / "scripts").glob("*.py")
                if not d.name.startswith("test_")]
    return dateien


def _keine_zugangsdaten_im_quelltext():
    """Geheimnis-Regel — über alle Produktivmodule, an der Form gemessen."""
    module = _produktivmodule()
    assert len(module) >= 10, \
        f"die Modul-Menge ist verdaechtig klein ({len(module)}) — Pruefung waere bedeutungslos"

    for datei in module:
        roh = datei.read_text(encoding="utf-8", errors="replace")
        for zeilennr, zeile in enumerate(roh.splitlines(), 1):
            if zeile.lstrip().startswith("#") or _PLATZHALTER.search(zeile):
                continue
            treffer = _APP_KENNWORT.search(zeile) or _ZUWEISUNG.search(zeile)
            assert not treffer, (
                f"moegliches Zugangsdaten-Geheimnis in {datei.name}:{zeilennr} "
                f"— Form [{treffer.group(0)[:20]}…]. Zugaenge gehoeren in die "
                f"Umgebung, nie in den Quelltext.")
        # Adressen, die auf ein persoenliches Konto zeigen.
        for verdacht in ("@icloud.com", "@me.com"):
            assert verdacht not in roh.lower(), \
                f"moeglicher Zugangsdaten-Rest in {datei.name}: {verdacht}"

    quelle = (Path(__file__).resolve().parent.parent / "kalender.py").read_text(
        encoding="utf-8").lower()
    assert "os.environ" in quelle, "Zugang kommt nicht aus der Umgebung"


def _die_geheimnis_suche_findet_wirklich():
    """**Die Gegenprobe im Pruefer selbst** — sonst belegt die Zeile oben nur,
    dass nichts gefunden wurde, nicht dass etwas gefunden WERDEN kann.

    Genau die Unterscheidung, an der Stelle 8 gescheitert ist: Die alte
    Fassung war jahrelang gruen, weil sie nichts finden KONNTE.
    """
    faelle = [
        ('PASSWORT = "abcd-efgh-ijkl-mnop"', "App-Kennwort mit Leerzeichen"),
        ('passwort="abcd-efgh-ijkl-mnop"', "App-Kennwort ohne Leerzeichen"),
        ("PASSWORT: 'abcd-efgh-ijkl-mnop'", "Doppelpunkt statt Gleichheit"),
        ('CALDAV_PASSWORT   =   "gehe1mnis123"', "viele Leerzeichen"),
        ('api_key = "sk-ant-abcdefghijklmnop"', "Schluessel"),
        ('TOKEN = "1234567890abcdef"', "Token"),
    ]
    for zeile, was in faelle:
        assert _APP_KENNWORT.search(zeile) or _ZUWEISUNG.search(zeile), \
            f"die Geheimnis-Suche findet [{was}] nicht: {zeile}"

    # Und die Gegenrichtung: was NICHT anschlagen darf.
    harmlos = [
        'PASSWORT = os.environ["CALDAV_PASSWORT"]',
        'passwort = getenv("X")',
        '# passwort="beispiel-aus-der-doku"',
        'PASSWORT = "dein-app-kennwort-hier"',
        'text = "Das Passwort steht in der Umgebung."',
    ]
    for zeile in harmlos:
        if zeile.lstrip().startswith("#") or _PLATZHALTER.search(zeile):
            continue
        assert not (_APP_KENNWORT.search(zeile) or _ZUWEISUNG.search(zeile)), \
            f"Fehlalarm auf harmloser Zeile: {zeile}"


def _zugangslink_haengt_am_termin():
    """**7.4.** Ein Videotermin ohne seinen Link ist eine Erinnerung an etwas,
    das man dann erst suchen muss. Gesucht wird in Ort, Notiz und Titel."""
    def _t(**kw):
        return k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0),
                               ende=None, titel=kw.pop("titel", "T"), **kw)
    assert _t(ort="https://zoom.us/j/123").link() == "https://zoom.us/j/123"
    assert "youtu.be" in _t(notiz="Stream: https://youtu.be/abc").link()
    assert _t(titel="Los https://meet.google.com/x").link().endswith("/x")


def _ohne_link_keine_leere_zeile():
    """**Die Gegenprobe aus dem Messbefund**, wörtlich: „Ein Termin ohne Link
    darf keine leere Zeile erzeugen." Sonst trüge jeder Zahnarzttermin einen
    Pfeil ins Nichts."""
    t = k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None,
                        titel="Zahnarzt", ort="Hauptstrasse 5")
    assert t.link() == "", "aus einer Adresse ohne Link wurde einer"
    assert "→" not in t.lesbar(), f"leerer Pfeil in der Zeile: {t.lesbar()}"


def _der_zugang_gewinnt_gegen_beiwerk():
    """Eine Terminbeschreibung enthält oft mehrere Adressen — Einwahl,
    Unterlagen, Anbieter-Startseite. Gezeigt wird die, die nach **Zugang**
    aussieht, nicht die erste."""
    t = k.Termin(
        beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None, titel="Vortrag",
        notiz="Unterlagen https://example.com/pdf — Zugang https://zoom.us/j/9")
    assert "zoom.us" in t.link(), f"das Beiwerk hat gewonnen: {t.link()}"


def _die_adresse_steht_nicht_zweimal():
    """Bei Einladungen steht der Link im **Ortsfeld**. Ihn dort zu belassen und
    zusätzlich anzuhängen, zeigt ihn doppelt — beim Bauen aufgefallen, nicht
    beim Entwerfen."""
    t = k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None,
                        titel="Runde", ort="https://zoom.us/j/12345")
    assert t.lesbar().count("zoom.us") == 1, \
        f"die Adresse steht zweimal: {t.lesbar()}"
    # Gegenrichtung: Ein Ort MIT zusätzlichem Text behält seinen Text.
    t2 = k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None,
                         titel="Beirat", ort="Raum 3, https://meet.google.com/x")
    assert "(Raum 3)" in t2.lesbar(), f"der Ortstext ging verloren: {t2.lesbar()}"


def _satzzeichen_gehoeren_nicht_zur_adresse():
    """`…/abc.` am Satzende — der Punkt ist Grammatik, nicht Teil des Links."""
    t = k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None,
                        titel="X", notiz="Siehe https://meet.google.com/abc-def.")
    assert t.link().endswith("abc-def"), f"Satzzeichen mitgenommen: {t.link()}"


def _der_link_ueberlebt_die_vorlese_kette_nicht():
    """**Die Auflage aus dem Messbefund.** Adressen gehören nicht in die
    Sprachausgabe — „schräg schräg schräg Punkt Punkt HTML" ist genau das,
    was Adam am 17.06. beanstandet hat. Geprüft wird, dass der bestehende
    Filter greift **und** dass der lesbare Teil dabei heil bleibt."""
    import os
    os.environ["TELEGRAM_BOT_TOKEN"] = ("1:test")
    os.environ["ALLOWED_USER_IDS"] = ("1")
    import bot
    t = k.Termin(beginn=dt.datetime(2026, 8, 21, 10, 0), ende=None,
                        titel="Team-Runde", ort="https://zoom.us/j/12345")
    gesprochen = bot._strip_markdown_for_tts(t.lesbar())
    assert "zoom.us" not in gesprochen, \
        f"die Adresse landet in der Sprachausgabe: {gesprochen}"
    assert "Team-Runde" in gesprochen, \
        f"der lesbare Teil wurde mit weggefiltert: {gesprochen}"


check("ohne Zugang: deutlicher Fehler statt Leerlauf", _ohne_zugang_deutlicher_fehler)
check("Termin liest sich wie gesprochen", _termin_lesbar)
check("ganztägig nennt keine Uhrzeit", _ganztags_sagt_ganztaegig)
check("Aufgabe ohne Frist bleibt schlicht", _aufgabe_ohne_frist_bleibt_schlicht)
check("unbekannte Sammlung wird benannt, nicht ersetzt", _falscher_name_wird_benannt)
check("keine Zugangsdaten im Quelltext", _keine_zugangsdaten_im_quelltext)
check("die Geheimnis-Suche findet wirklich", _die_geheimnis_suche_findet_wirklich)
check("7.4: der Zugangslink haengt am Termin", _zugangslink_haengt_am_termin)
check("7.4: ohne Link keine leere Zeile (Gegenprobe)", _ohne_link_keine_leere_zeile)
check("7.4: der Zugang gewinnt gegen Beiwerk", _der_zugang_gewinnt_gegen_beiwerk)
check("7.4: die Adresse steht nicht zweimal", _die_adresse_steht_nicht_zweimal)
check("7.4: Satzzeichen gehoeren nicht zur Adresse", _satzzeichen_gehoeren_nicht_zur_adresse)
check("7.4: der Link kommt NICHT in die Sprachausgabe", _der_link_ueberlebt_die_vorlese_kette_nicht)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Kalender-Tests bestanden (ohne Netz, ohne Zugangsdaten).")
