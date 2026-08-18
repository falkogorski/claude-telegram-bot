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
    except Exception as e:
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _nicht_scharfgestellt():
    """**Der Riegel nennt seinen Zustand — welcher es auch sei.**

    KORRIGIERT 18.08.2026: Die erste Fassung verlangte `SCHARF is False`, setzte
    also den ruhenden Zustand voraus und fiel um, als Adam scharf stellte. Der
    eigentliche Anspruch ist ein anderer und gilt in BEIDE Richtungen: Ein
    Uebergang, der leise nichts tut, sieht aus wie einer, der leise alles tut.
    Also wird gemessen, dass er es SAGT.
    """
    zuvor = ab.SCHARF
    try:
        ab.SCHARF = False
        ab.legen({"titel": "Kleinigkeit richten", "art": "fehlerbehebung"}, "claudia")
        anzahl, meldung = ab.uebernehmen()
        assert anzahl == 0, "es wurde übergeben, obwohl der Riegel zu ist"
        assert "nicht scharfgestellt" in meldung, (
            "der Riegel schweigt — ein Übergang, der leise nichts tut, sieht aus "
            "wie einer, der leise alles tut")
        assert "1" in meldung, "die Meldung sagt nicht, wie viel wartet"
    finally:
        ab.SCHARF = zuvor


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
    # **KORRIGIERT 18.08.2026:** Diese Zeile nahm die Art "doku" als Beispiel -
    # also aus dem Bestand, den sie absichern soll. Als Adams Entscheid sie aus
    # der Gruen-Liste strich, fiel die Pruefung um. Jetzt nimmt sie irgendeine
    # Art, die gerade gruen ist, statt einer namentlich genannten.
    art = next(iter(ab.GRUENE_ARTEN))
    p = ab.legen({"titel": "Beispielauftrag", "art": art}, "claudia")
    satz = json.loads(p.read_text(encoding="utf-8"))
    assert satz["ampel"] == "gruen" and satz["ampel_grund"], "die Regel fehlt"
    assert "2026-" in satz["ampel_grund"], \
        "das Prüfdatum der Grün-Art wird nicht mitgeschrieben"


def _uebersicht_ist_eine_zeile_je_auftrag():
    """Das Konzept verspricht Adam EINE Zeile statt eines Dokuments — mehr
    wäre wieder Transport."""
    text = ab.uebersicht()
    assert "Auftragsbuch" in text and "🟢" in text and "🟡" in text
    # **KORRIGIERT 18.08.2026:** Vorher verlangte die Zeile das Wort "nicht
    # scharfgestellt" - sie setzte also den ruhenden Zustand voraus und fiel um,
    # als der Riegel oeffnete. Geprueft wird jetzt, dass die Uebersicht den
    # Zustand NENNT, welcher es auch sei. Das ist der eigentliche Anspruch:
    # Ein Uebergang, der leise nichts tut, sieht aus wie einer, der leise alles
    # tut - und andersherum genauso.
    assert ("scharfgestellt" in text.lower() or "riegel" in text.lower()), \
        "die Übersicht verschweigt den Zustand des Riegels"


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


check("der Riegel nennt seinen Zustand, welcher es auch sei", _nicht_scharfgestellt)
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


# ---------- Gegenprüfungs-Befunde vom 18.08.2026 ----------------------------
def _handgelegte_gruen_behauptung_wird_nicht_geglaubt():
    """**Die Umgehung, die eine frische Sitzung gefunden hat.**

    `uebernehmen()` las die Ampel aus der DATEI. Wer eine Datei von Hand in den
    Eingang legte, konnte sich sein eigenes Gruen ausstellen — die Gegenpruefung
    hat so einen Auftrag mit unbekannter Art, unbekanntem Absender und dem
    Rot-Wort [Root-Zugang] im Titel an Hora durchgereicht.

    Die Ampel im Eintrag ist ein Vorschlag, nie eine Wahrheit.
    """
    import json
    import auftragsbuch as ab
    heim = Path(tempfile.mkdtemp(prefix="umgehung-"))
    eingang = heim / "eingang"
    eingang.mkdir()
    alt_dir, alt_scharf = ab.EINGANG, ab.SCHARF
    ab.EINGANG, ab.SCHARF = eingang, True
    try:
        (eingang / "boese.json").write_text(json.dumps({
            "titel": "Root-Zugang einrichten",
            "art": "architektur",          # keine Gruen-Art
            "absender": "niemand",         # kein bekannter Absender
            "ampel": "gruen",              # die Behauptung
        }), encoding="utf-8")
        ziel = heim / "hora.json"
        ziel.write_text("[]", encoding="utf-8")
        anzahl, meldung = ab.uebernehmen(hora_liste=ziel)
        liste = json.loads(ziel.read_text(encoding="utf-8"))
        assert anzahl == 0, (
            f"eine handgelegte Gruen-Behauptung wurde uebergeben: {meldung}")
        assert not liste, f"der Auftrag steht in Horas Liste: {liste}"
    finally:
        ab.EINGANG, ab.SCHARF = alt_dir, alt_scharf


def _rote_worte_treffen_deutsche_zusammensetzungen():
    """**Die Regel war auf der falschen Seite geoeffnet.**

    [Klient] steht in [Klientendaten] zufaellig vorn — im Deutschen steht das
    Grundwort hinten. Mit nur hinten geoeffneter Wortgrenze blieben genau die
    Faelle blind, fuer die die Bremse gebaut wurde. Alle hier gemessen.
    """
    import auftragsbuch as ab
    for muss_rot in ("Serverpasswort erneuern", "Zugangsschluessel tauschen",
                     "Zugriffstoken erneuern", "Systemschluessel pruefen",
                     "Bestandskunden anschreiben", "Klientendaten sichern",
                     "Datenbankpasswort rotieren"):
        ampel, _ = ab.einstufen({"titel": muss_rot})
        assert ampel == "rot", f"[{muss_rot}] wird nicht gebremst"


def _haeufige_harmlose_traeger_bremsen_nicht():
    """Der Preis der offenen Grenzen sind Fehlalarme. Bei einer Bremse ist das
    die richtige Fehlerrichtung — aber nicht gratis: Rot heisst Warten auf
    Adams Daumen, und in einer Abwesenheit heisst das gar nichts."""
    import auftragsbuch as ab
    for harmlos in ("siehe above im Text", "Abort bei Fehler abfangen",
                    "kostenlose Variante pruefen", "kostenfreie Loesung",
                    "Dokumentation aktualisieren"):
        ampel, grund = ab.einstufen({"titel": harmlos})
        assert ampel != "rot", f"[{harmlos}] wird faelschlich gebremst: {grund}"


check("handgelegte Gruen-Behauptung wird nicht geglaubt (Umgehung 18.08.)",
      _handgelegte_gruen_behauptung_wird_nicht_geglaubt)
check("rote Worte treffen deutsche Zusammensetzungen",
      _rote_worte_treffen_deutsche_zusammensetzungen)
check("haeufige harmlose Traeger bremsen nicht",
      _haeufige_harmlose_traeger_bremsen_nicht)

if fails:
    print(f"\n❌ {len(fails)} B8-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    raise SystemExit(1)


# ---------- E1: Grün-Liste scharf, mit Frist (Adams Entscheid 18.08.) --------
def _riegel_ist_eine_datei_mit_frist():
    """**Der Riegel liegt dort, wo man ihn sucht — und schliesst sich selbst.**

    Bis zum 18.08. war er eine Umgebungsvariable, und an drei Stellen stand
    faelschlich "SCHARF = False". Jetzt traegt er seine eigene Frist: Riegel und
    Probewochen-Ende sind dasselbe Dokument.
    """
    import auftragsbuch as ab
    assert ab.RIEGEL.exists(), "die Riegel-Datei fehlt"
    text = ab.RIEGEL.read_text(encoding="utf-8")
    assert "GILT-BIS:" in text, "der Riegel nennt kein Fristdatum"
    assert "Stichtag:" in text, "der Riegel traegt keinen Gueltigkeits-Kopf"


def _abgelaufene_frist_schliesst_den_riegel():
    """**Ein Riegel, der sich im Zweifel oeffnet, ist keiner.** Vier Wege in die
    Sperre, alle gemessen: abgelaufen, kein Datum, unlesbares Datum, keine
    Datei."""
    import auftragsbuch as ab
    heim = Path(tempfile.mkdtemp(prefix="riegel-"))
    alt_riegel, alt_env = ab.RIEGEL, os.environ.pop("AUFTRAGSBUCH_SCHARF", None)
    try:
        faelle = {
            "SCHARF: ja\nGILT-BIS: 2020-01-01\n": "abgelaufen",
            "SCHARF: ja\n": "ohne Frist",
            "SCHARF: ja\nGILT-BIS: irgendwann\n": "unlesbares Datum",
            "GILT-BIS: 2099-01-01\n": "ohne SCHARF",
        }
        for inhalt, was in faelle.items():
            ab.RIEGEL = heim / "r.md"
            ab.RIEGEL.write_text(inhalt, encoding="utf-8")
            offen, grund = ab._riegel_offen()
            assert not offen, f"der Riegel oeffnet sich bei [{was}]: {grund}"

        ab.RIEGEL = heim / "fehlt.md"
        offen, _ = ab._riegel_offen()
        assert not offen, "eine fehlende Riegel-Datei oeffnet den Riegel"

        # Und die Gegenrichtung: gueltige Frist oeffnet ihn.
        ab.RIEGEL = heim / "gut.md"
        ab.RIEGEL.write_text("SCHARF: ja\nGILT-BIS: 2099-12-31\n", encoding="utf-8")
        offen, grund = ab._riegel_offen()
        assert offen, f"ein gueltiger Riegel bleibt zu: {grund}"
    finally:
        ab.RIEGEL = alt_riegel
        if alt_env is not None:
            os.environ["AUFTRAGSBUCH_SCHARF"] = alt_env


def _gruen_liste_traegt_adams_vier_arten():
    """Adams Entscheid nennt vier Arten. `doku` ist NICHT darunter und wurde
    gestrichen — bei einer geschlossenen Liste ist jede stille Ergaenzung genau
    der Fehler, den die Liste verhindern soll."""
    import auftragsbuch as ab
    assert set(ab.GRUENE_ARTEN) == {"fehlerbehebung", "zeichenwechsel",
                                    "aufraeumen", "test"}, \
        f"die Gruen-Liste weicht von Adams Entscheid ab: {sorted(ab.GRUENE_ARTEN)}"
    for art, datum in ab.GRUENE_ARTEN.items():
        assert datum >= "2026-08-18", f"[{art}] traegt ein altes Pruefdatum: {datum}"


def _uebergabe_meldet_sich_ungedaempft():
    """**Die Sichtbarkeit IST der Zweck der Probewoche.** Wer sie daempft,
    prueft nicht die Automatik, sondern die Daempfung."""
    quelle = Path(__file__).resolve().parent.parent / "auftragsbuch.py"
    block = quelle.read_text(encoding="utf-8").split("def uebernehmen")[1]
    assert "botenpost.legen" in block, "die Uebergabe meldet sich nicht an Adam"
    assert "warum grün" in block.lower() or "grün, weil" in block, \
        "die Meldung nennt nicht, WARUM der Auftrag gruen war"


def _hora_speist_sich_aus_dem_auftragsbuch():
    """**GEFUNDEN 18.08.:** `uebernehmen()` hatte gar keinen Aufrufer. Scharf
    stellen allein haette nichts bewirkt - die Probewoche waere eine Woche
    gewesen, in der nichts geschieht."""
    hora = (Path(__file__).resolve().parent / "hora.py").read_text(encoding="utf-8")
    assert "auftragsbuch.uebernehmen()" in hora, \
        "Hora ruft das Auftragsbuch nicht - der Riegel haette keine Wirkung"
    block = hora.split("def _lauf")[1][:2000]
    assert "except Exception" in block, \
        "ein Fehlschlag des Auftragsbuchs wuerde Horas Lauf verhindern"


check("der Riegel ist eine Datei mit Frist und Kopf", _riegel_ist_eine_datei_mit_frist)
check("abgelaufene/kaputte Frist schliesst den Riegel (4 Wege)",
      _abgelaufene_frist_schliesst_den_riegel)
check("Gruen-Liste traegt Adams vier Arten", _gruen_liste_traegt_adams_vier_arten)
check("die Uebergabe meldet sich ungedaempft", _uebergabe_meldet_sich_ungedaempft)
check("Hora speist sich aus dem Auftragsbuch", _hora_speist_sich_aus_dem_auftragsbuch)

if fails:
    print(f"\n❌ {len(fails)} B8-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    raise SystemExit(1)
print("\nAlle B8-Auftragsbuch-Tests bestanden.")
