#!/usr/bin/env python3
# <!-- ROLLE: test-auftragsbuch -->
"""Verhaltenstest B8 Stufe 1 — die Verrohrung, und dass sie NICHT scharf ist.

Das Konzept benennt den gefährlichsten Fall selbst, und er ist keine
Technikfrage: **„Ich stufe einen Auftrag falsch als grün ein — etwas wird
gebaut, das Adam so nicht wollte, und niemand merkt es, bis es auffällt."**

Deshalb liegt der Schwerpunkt dieser Prüfungen nicht auf dem Transport, sondern
auf der Einstufung — und darauf, dass Grün ausschließlich aus einer
geschlossenen Liste kommt und nie aus einem Urteil im Einzelfall.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b8-"))
os.environ["AUFTRAGSBUCH_DIR"] = str(_TMP / "buch")
os.environ["HORA_LISTE"] = str(_TMP / "hora-liste.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import auftragsbuch as ab  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _nicht_scharfgestellt():
    """Connis Auflage: Verrohrung bauen, NICHT scharfstellen. Und der Deckel
    für die Abwesenheit sagt dasselbe — gebaut-und-ruhend darf warten."""
    assert ab.SCHARF is False, "das Auftragsbuch ist scharfgestellt"
    ab.legen({"titel": "Kleinigkeit richten", "art": "fehlerbehebung"}, "claudia")
    anzahl, meldung = ab.uebernehmen()
    assert anzahl == 0, "es wurde übergeben, obwohl nichts scharf ist"
    assert "nicht scharfgestellt" in meldung, (
        "der Riegel schweigt — ein Übergang, der leise nichts tut, sieht aus "
        "wie einer, der leise alles tut")
    assert "1" in meldung, "die Meldung sagt nicht, wie viel wartet"


def _gruen_nur_aus_der_geschlossenen_liste():
    """**Der Kern.** Eine unbekannte Art ist NICHT grün — auch dann nicht, wenn
    sie harmlos klingt. Wer eine neue grüne Art will, trägt sie ein."""
    assert ab.einstufen({"titel": "x", "art": "fehlerbehebung"})[0] == "gruen"
    for unbekannt in ("umbau", "architektur", "verbesserung", "kleinigkeit"):
        ampel, grund = ab.einstufen({"titel": "x", "art": unbekannt})
        assert ampel == "gelb", (
            f"die unbekannte Art [{unbekannt}] wurde grün — damit hinge Grün "
            "wieder an einem Urteil im Einzelfall")
        assert unbekannt in grund, "die Begründung nennt die Art nicht"


def _ohne_art_kein_gruen():
    ampel, grund = ab.einstufen({"titel": "irgendwas"})
    assert ampel == "gelb" and "keine Art" in grund, \
        "ein Auftrag ohne Art rutscht durch"


def _rot_schlaegt_gruen():
    """Ein Aufräum-Auftrag, der das Wort Token enthält, ist keiner mehr.

    Die Wortsuche ist eine ZUSÄTZLICHE Bremse, kein Ersatz für die
    geschlossene Liste — man kann sie unabsichtlich umgehen. Aber sie fängt
    genau die Fälle, in denen eine harmlose Art auf heikle Inhalte trifft.
    """
    for heikel in ("Token erneuern", "Firewall anpassen", "Klientendaten sortieren",
                   "Kosten prüfen", "per sudo aufräumen"):
        ampel, grund = ab.einstufen({"titel": heikel, "art": "aufraeumen"})
        assert ampel == "rot", f"[{heikel}] blieb grün, obwohl die Art harmlos ist"
        assert "[" in grund, "die Begründung nennt das auslösende Wort nicht"


def _gelb_und_rot_brauchen_zustimmung():
    p = ab.legen({"titel": "Etwas Neues bauen", "art": "umbau"}, "conni")
    satz = json.loads(p.read_text(encoding="utf-8"))
    assert satz["braucht_zustimmung"] is True, "Gelb läuft ohne Adams Daumen an"
    p2 = ab.legen({"titel": "Tippfehler richten", "art": "zeichenwechsel"}, "conni")
    assert json.loads(p2.read_text(encoding="utf-8"))["braucht_zustimmung"] is False


def _absender_steht_zweimal_drin():
    """Gelernt aus der anonymen Meldung vom 26.07., deren Urheber über eine
    Stunde Suche gekostet hat: Der Dateiname ist das, was man in einem vollen
    Ordner sieht, ohne eine Datei zu öffnen."""
    p = ab.legen({"titel": "Prüfung ergänzen", "art": "test"}, "mick")
    assert "mick" in p.name, "der Dateiname nennt den Absender nicht"
    assert json.loads(p.read_text(encoding="utf-8"))["herkunft"] == "mick"


def _fremder_absender_wird_abgewiesen():
    """Ein Absender, den sich jeder ausdenken kann, belegt nichts."""
    try:
        ab.legen({"titel": "x", "art": "test"}, "irgendwer")
    except ValueError:
        return
    raise AssertionError("ein unbekannter Absender durfte ablegen")


def _einstufung_wird_mitgeschrieben():
    """Ändert sich die Grün-Liste später, muss nachvollziehbar bleiben, unter
    welcher Regel dieser Auftrag hereinkam."""
    p = ab.legen({"titel": "Register nachziehen", "art": "doku"}, "claudia")
    satz = json.loads(p.read_text(encoding="utf-8"))
    assert satz["ampel"] == "gruen" and satz["ampel_grund"], "die Regel fehlt"
    assert "2026-" in satz["ampel_grund"], \
        "das Prüfdatum der Grün-Art wird nicht mitgeschrieben"


def _uebersicht_ist_eine_zeile_je_auftrag():
    """Das Konzept verspricht Adam EINE Zeile statt eines Dokuments — mehr
    wäre wieder Transport."""
    text = ab.uebersicht()
    assert "Auftragsbuch" in text and "🟢" in text and "🟡" in text
    assert "nicht scharfgestellt" in text, \
        "die Übersicht verschweigt, dass nichts von allein anläuft"


def _scharf_uebergibt_nur_gruen():
    """Die Gegenprobe zum Riegel: Wäre er offen, dürfte trotzdem nur Grün
    durch. Ein Prüfer, der nur den geschlossenen Zustand kennt, belegt nicht,
    dass der offene richtig wäre."""
    ab.SCHARF = True
    try:
        anzahl, _ = ab.uebernehmen()
        liste = json.loads(Path(os.environ["HORA_LISTE"]).read_text(encoding="utf-8"))
        arten = {a["titel"]: a["ampel"] for a in liste}
        assert anzahl >= 1, "scharf wurde trotzdem nichts übergeben"
        assert all(v == "gruen" for v in arten.values()), \
            f"Gelb oder Rot ist an Hora durchgerutscht: {arten}"
        assert "Etwas Neues bauen" not in arten, "ein gelber Auftrag lief an"
    finally:
        ab.SCHARF = False


check("NICHT scharfgestellt — und der Riegel sagt es", _nicht_scharfgestellt)
check("Grün nur aus der geschlossenen Liste", _gruen_nur_aus_der_geschlossenen_liste)
check("ohne Art kein Grün", _ohne_art_kein_gruen)
check("Rot schlägt Grün (zusätzliche Bremse)", _rot_schlaegt_gruen)
check("Gelb und Rot brauchen Zustimmung", _gelb_und_rot_brauchen_zustimmung)
check("der Absender steht zweimal drin", _absender_steht_zweimal_drin)
check("fremder Absender wird abgewiesen", _fremder_absender_wird_abgewiesen)
check("die Einstufung wird mitgeschrieben", _einstufung_wird_mitgeschrieben)
check("die Übersicht ist eine Zeile je Auftrag", _uebersicht_ist_eine_zeile_je_auftrag)
check("scharf übergäbe nur Grün (Gegenprobe)", _scharf_uebergibt_nur_gruen)

print()
if fails:
    print(f"❌ {len(fails)} B8-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B8-Auftragsbuch-Tests bestanden.")
