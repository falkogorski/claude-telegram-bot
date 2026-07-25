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


# --- Leitplanke 5: Fail-safe = Ablehnen ------------------------------------
def _frist_gilt_als_ablehnung():
    _leeren()
    a = _stellen()
    spaeter = time.time() + f.FRIST_STUNDEN * 3600 + 60
    assert a.abgelaufen(spaeter), "Frist greift nicht"
    # Auch ein „ja" nach Fristablauf endet als Ablehnung.
    e = f.urteilen(a.kennung, True, "Adam", jetzt=spaeter)
    assert e["urteil"] == "abgelehnt", "Zustimmung nach Frist wurde angenommen!"
    assert "Frist" in e["grund"], f"Grund unklar: {e['grund']}"


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
    assert "gilt: abgelehnt" in t, "die Übersicht sagt nicht, was ohne Antwort gilt"
    assert " h" in t, "keine Restfrist genannt"


check("Aktion und Titel sind Pflicht (Konkret vor Label)", _aktion_ist_pflicht)
check("Geheimnisse werden abgewiesen, nicht angezeigt", _geheimnisse_werden_abgewiesen)
check("Frist abgelaufen → gilt als abgelehnt, auch bei Ja", _frist_gilt_als_ablehnung)
check("unbekannte Anfrage wird abgewiesen", _unbekannte_anfrage_wird_abgewiesen)
check("nur reversibles Grün ist bündelbar", _nur_gruen_mit_rueckweg_buendelbar)
check("jedes Urteil erzeugt einen Protokoll-Eintrag", _urteil_erzeugt_protokoll)
check("Protokoll-Zeile sprengt die Tabelle nicht", _protokoll_zeile_sprengt_keine_tabelle)
check("Herkunft wird geführt", _herkunft_wird_gefuehrt)
check("Übersicht nennt Frist und Folge", _uebersicht_nennt_die_frist)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle 9.4-Freigabe-Tests bestanden.")
