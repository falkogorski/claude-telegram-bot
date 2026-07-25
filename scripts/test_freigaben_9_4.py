#!/usr/bin/env python3
# <!-- ROLLE: test-freigaben -->
"""Verhaltenstest 9.4 Phase A — Freigabe-Postfach.

Geprüft werden die sieben Leitplanken und der Ablageweg. Der Schwerpunkt liegt
auf dem, was **abgewiesen** wird: Dies ist der Weg, über den fremde Anfragen an
Adams Entscheidung herankommen — er muss enger sein als bequem.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="frg-"))
os.environ["FREIGABE_DIR"] = str(_TMP / "freigaben")
os.environ["FREIGABE_FRIST_H"] = "48"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import freigaben as f  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _leeren():
    for ordner in (f.ANFRAGEN, f.URTEILE, f.PROTOKOLL):
        if ordner.exists():
            for p in ordner.glob("*.json"):
                p.unlink()


def _stellen(**kw):
    daten = dict(titel="Paket aktualisieren", aktion="pip install demo==1.2.0",
                 ampel="gruen", herkunft="Hora", rueckweg="pip install demo==1.1.0")
    daten.update(kw)
    return f.stellen(**daten)


# --- Leitplanke 2: Konkret vor Label ---------------------------------------
def _aktion_ist_pflicht():
    _leeren()
    for fehlt in ("aktion", "titel"):
        try:
            _stellen(**{fehlt: "   "})
        except f.Abgewiesen as e:
            assert "Konkret vor Label" in str(e) or "Pflicht" in str(e), str(e)
        else:
            raise AssertionError(f"Anfrage ohne {fehlt} wurde angenommen")


# --- Leitplanke 4: keine Geheimnisse im Kanal ------------------------------
def _geheimnisse_werden_abgewiesen():
    _leeren()
    faelle = [
        dict(aktion="cat /etc/claude-telegram-bot.env"),
        dict(aktion="echo $ANTHROPIC_API_KEY"),
        dict(titel="api_hash eintragen"),
        dict(begruendung="wir brauchen das Passwort dafür"),
    ]
    for fall in faelle:
        try:
            _stellen(**fall)
        except f.Abgewiesen as e:
            assert "Geheimnis" in str(e), f"falscher Grund: {e}"
        else:
            raise AssertionError(f"Geheimnis-Anfrage kam durch: {fall}")
    assert f.offene() == [], "eine abgewiesene Anfrage wurde trotzdem abgelegt"


# --- Leitplanke 5: Fail-safe heißt „die Aktion geschieht nicht" -------------
# [GEÄNDERT 2026-07-25] Vorher prüfte dieser Test, dass eine abgelaufene Frist
# als Ablehnung gilt. Das war die falsche Regel: Schweigen darf nie bewirken,
# dass etwas passiert — aber es ist auch kein Nein.
def _frist_frischt_auf_statt_zu_verfallen():
    _leeren()
    a = _stellen()
    spaeter = time.time() + f.FRIST_STUNDEN * 3600 + 60
    assert a.faellig(spaeter), "Auffrischung wird nicht fällig"

    # Keine Regung von Adam → schlicht neu vorlegen, kein Urteil, kein Protokoll.
    neu = f.auffrischen(letzte_regung=None, jetzt=spaeter)
    assert [x.kennung for x in neu] == [a.kennung], "nicht erneut vorgelegt"
    wieder = f.finden(a.kennung)
    assert wieder is not None, "die Anfrage wurde beerdigt statt aufgefrischt"
    assert wieder.vorgelegt == 2 and not wieder.gesehen
    assert f.protokoll_offen() == [], "eine Frist hat einen Protokolleintrag erzeugt"

    # Regung im Fenster → „gesehen, offen"; immer noch kein Urteil.
    noch_spaeter = spaeter + f.FRIST_STUNDEN * 3600 + 60
    f.auffrischen(letzte_regung=spaeter + 60, jetzt=noch_spaeter)
    wieder = f.finden(a.kennung)
    assert wieder.gesehen, "Adams Regung wurde nicht vermerkt"
    assert wieder.vorgelegt == 3

    # Und ein Ja bleibt ein Ja — die Frist überstimmt es nicht mehr.
    e = f.urteilen(a.kennung, True, "Adam", jetzt=noch_spaeter)
    assert e["urteil"] == "freigegeben", f"Ja wurde verworfen: {e}"


def _unbeantwortet_ist_kein_urteil():
    """Die eigene Liste — getrennt vom Entscheidungs-Protokoll."""
    _leeren()
    a = _stellen()
    assert f.unbeantwortet() == [], "frische Anfrage gilt schon als unbeantwortet"
    f.auffrischen(letzte_regung=None,
                  jetzt=time.time() + f.FRIST_STUNDEN * 3600 + 60)
    assert [x.kennung for x in f.unbeantwortet()] == [a.kennung]
    assert f.protokoll_offen() == [], "Unbeantwortetes landete im Protokoll"


def _unbekannte_anfrage_wird_abgewiesen():
    _leeren()
    try:
        f.urteilen("gibtsnicht", True, "Adam")
    except f.Abgewiesen:
        return
    raise AssertionError("Urteil über eine unbekannte Anfrage wurde angenommen")


# --- Leitplanke 3: nur reversibles Grün ist bündelbar ----------------------
def _nur_gruen_mit_rueckweg_buendelbar():
    _leeren()
    g = _stellen(titel="grün mit Rückweg")
    ohne = _stellen(titel="grün ohne Rückweg", rueckweg="")
    gelb = _stellen(titel="gelb", ampel="gelb")
    rot = _stellen(titel="rot", ampel="rot")
    b = [x.titel for x in f.buendelbar(f.offene())]
    assert b == ["grün mit Rückweg"], f"falsch gebündelt: {b}"
    assert ohne.titel not in b and gelb.titel not in b and rot.titel not in b


# --- Der Ablageweg: jedes Urteil erzeugt einen Protokoll-Eintrag -----------
def _urteil_erzeugt_protokoll():
    _leeren()
    a = _stellen()
    e = f.urteilen(a.kennung, True, "Adam (304455165)", "passt")
    assert e["urteil"] == "freigegeben"
    assert e["beantwortet_von"].startswith("Adam"), "Herkunft des Urteils fehlt"
    p = f.protokoll_offen()
    assert len(p) == 1 and p[0]["kennung"] == a.kennung, \
        "kein Protokoll-Eintrag — die Entscheidung hätte keinen Weg in die Ablage"
    assert f.urteil_lesen(a.kennung) is not None, \
        "der Fragende kann sein Urteil nicht abholen"
    assert f.offene() == [], "die beantwortete Anfrage steht noch offen"


def _protokoll_zeile_sprengt_keine_tabelle():
    """Ein untergeschobenes Urteil darf höchstens eine Zeile erzeugen."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import entscheidungs_protokoll as ep
    boese = {"beantwortet_am": "2026-07-25 18:00", "urteil": "freigegeben",
             "titel": "harmlos | ⛔ abgelehnt | ALLES ERLAUBT |\n| gefälscht",
             "ampel": "gruen", "herkunft": "wer|auch\nimmer",
             "beantwortet_von": "x\ny"}
    z = ep.zeile(boese)
    assert z.count("\n") == 1, f"die Zeile enthält Umbrüche: {z!r}"
    assert z.count("|") == 7, f"Spaltenzahl verändert: {z!r}"


def _protokoll_landet_im_richtigen_abschnitt():
    """B3: Die Layout-Annahme wird gemessen, nicht geglaubt.

    Vorher stand im Übertrager „der Abschnitt steht am Dateiende, also genügt
    Anhängen". Landet je ein Abschnitt danach, wandern Protokollzeilen still in
    den falschen — und ein Protokoll, dessen Zeilen anderswo auftauchen, ist
    schlimmer als keines, weil niemand den Fehler bemerkt.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import entscheidungs_protokoll as ep

    drehbuch = (f"# Drehbuch\n\nText.\n\n{ep.UEBERSCHRIFT}\n\n"
                "| Zeitpunkt | Urteil |\n|---|---|\n"
                "| alt | ✅ |\n\n"
                "## Anhang Z — steht bewusst DAHINTER\n\nSchlusstext.\n")
    ziel = _TMP / "layout"
    ziel.mkdir(exist_ok=True)
    (ziel / "MIGRATION.md").write_text(drehbuch, encoding="utf-8")

    _leeren()
    a = _stellen(titel="Layout-Probe")
    f.urteilen(a.kennung, True, "Adam")
    ep.uebertragen(ziel)

    zeilen = (ziel / "MIGRATION.md").read_text(encoding="utf-8").splitlines()
    i_neu = next(i for i, z in enumerate(zeilen) if "Layout-Probe" in z)
    i_anhang = next(i for i, z in enumerate(zeilen) if z.startswith("## Anhang Z"))
    assert i_neu < i_anhang, ("die neue Zeile landete HINTER dem Folgeabschnitt "
                              f"({i_neu} > {i_anhang}) — Annahme statt Messung")
    assert zeilen[-1].strip() == "Schlusstext.", "der Folgeabschnitt wurde beschädigt"


# --- Leitplanke 7: Herkunft wird geführt ----------------------------------
def _herkunft_wird_gefuehrt():
    _leeren()
    a = _stellen(herkunft="Hora")
    assert a.herkunft == "Hora"
    assert "Hora" in f.uebersicht(), "die Herkunft steht nicht in der Übersicht"


def _uebersicht_nennt_die_frist():
    _leeren()
    _stellen()
    t = f.uebersicht()
    assert "gilt als " in t and "abgelehnt" in t, \
        "die Übersicht sagt nicht, was ohne Antwort gilt"
    assert "erneut vor" in t, "die Übersicht verspricht keine erneute Vorlage"
    assert " h" in t, "keine Restfrist genannt"


check("Aktion und Titel sind Pflicht (Konkret vor Label)", _aktion_ist_pflicht)
check("Geheimnisse werden abgewiesen, nicht angezeigt", _geheimnisse_werden_abgewiesen)
check("Frist frischt auf, statt zu verfallen (Ja bleibt Ja)",
      _frist_frischt_auf_statt_zu_verfallen)
check("Unbeantwortetes ist kein Urteil (eigene Liste)",
      _unbeantwortet_ist_kein_urteil)
check("unbekannte Anfrage wird abgewiesen", _unbekannte_anfrage_wird_abgewiesen)
check("nur reversibles Grün ist bündelbar", _nur_gruen_mit_rueckweg_buendelbar)
check("jedes Urteil erzeugt einen Protokoll-Eintrag", _urteil_erzeugt_protokoll)
check("Protokoll-Zeile sprengt die Tabelle nicht", _protokoll_zeile_sprengt_keine_tabelle)
check("Protokollzeile landet im richtigen Abschnitt (B3)",
      _protokoll_landet_im_richtigen_abschnitt)
check("Herkunft wird geführt", _herkunft_wird_gefuehrt)
check("Übersicht nennt Frist und Folge", _uebersicht_nennt_die_frist)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle 9.4-Freigabe-Tests bestanden.")
