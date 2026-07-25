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


def _keine_zugangsdaten_im_quelltext():
    """Geheimnis-Regel: nichts Verräterisches im Modul."""
    quelle = (Path(__file__).resolve().parent.parent / "kalender.py").read_text(
        encoding="utf-8").lower()
    for verdacht in ("@icloud.com", "@me.com", 'password="', 'passwort="'):
        assert verdacht not in quelle, \
            f"möglicher Zugangsdaten-Rest im Quelltext: {verdacht}"
    assert "os.environ" in quelle, "Zugang kommt nicht aus der Umgebung"


check("ohne Zugang: deutlicher Fehler statt Leerlauf", _ohne_zugang_deutlicher_fehler)
check("Termin liest sich wie gesprochen", _termin_lesbar)
check("ganztägig nennt keine Uhrzeit", _ganztags_sagt_ganztaegig)
check("Aufgabe ohne Frist bleibt schlicht", _aufgabe_ohne_frist_bleibt_schlicht)
check("unbekannte Sammlung wird benannt, nicht ersetzt", _falscher_name_wird_benannt)
check("keine Zugangsdaten im Quelltext", _keine_zugangsdaten_im_quelltext)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Kalender-Tests bestanden (ohne Netz, ohne Zugangsdaten).")
