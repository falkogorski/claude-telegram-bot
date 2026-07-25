#!/usr/bin/env python3
# <!-- ROLLE: test-nachzieher -->
"""Verhaltenstest C1 — Nachzieher (Conni-Auftrag 25.07.).

Der Nachzieher darf genau eines: **ein Versions-Literal in einer bereits
vorhandenen Pin-Zeile ersetzen.** Geprüft wird deshalb vor allem, was er
ABLEHNT — denn er ist der einzige Weg, auf dem eine Änderung des Bots in eine
Steuerdatei gelangen kann. Nichts wird committet.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nachzieher as n  # noqa: E402

fails = []
TMP = Path(tempfile.mkdtemp(prefix="c1test-"))
(TMP / "requirements.txt").write_text(
    "python-telegram-bot[webhooks]>=22.7\n"
    "claude-agent-sdk==0.2.127\n"
    "python-dotenv>=1.0\n", encoding="utf-8")
(TMP / "components.json").write_text("{}\n", encoding="utf-8")
URFASSUNG = (TMP / "requirements.txt").read_text(encoding="utf-8")


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _zuruecksetzen():
    (TMP / "requirements.txt").write_text(URFASSUNG, encoding="utf-8")


def _gut(**abw):
    p = {"datei": "requirements.txt", "paket": "claude-agent-sdk",
         "von": "0.2.127", "nach": "0.2.130"}
    p.update(abw)
    return p


def _lehnt_ab(patch, stichwort=""):
    try:
        n.wende_an(patch, TMP)
    except n.Abgelehnt as e:
        assert not stichwort or stichwort in str(e), f"anderer Grund: {e}"
        assert (TMP / "requirements.txt").read_text(encoding="utf-8") == URFASSUNG, \
            "die Datei wurde trotz Ablehnung verändert!"
        return
    raise AssertionError("Patch wurde NICHT abgelehnt")


# --- Der erlaubte Fall -----------------------------------------------------
def _erlaubter_fall():
    _zuruecksetzen()
    r = n.wende_an(_gut(), TMP)
    inhalt = (TMP / "requirements.txt").read_text(encoding="utf-8")
    assert "claude-agent-sdk==0.2.130" in inhalt, "Version nicht ersetzt"
    assert "0.2.127" not in inhalt, "alte Version blieb stehen"
    assert inhalt.count("\n") == URFASSUNG.count("\n"), "Zeilenzahl verändert"
    assert "python-telegram-bot" in inhalt and "python-dotenv" in inhalt, \
        "andere Zeilen wurden beschädigt"
    assert r["geschrieben"] is True


def _nur_pruefen_schreibt_nicht():
    _zuruecksetzen()
    n.wende_an(_gut(), TMP, schreiben=False)
    assert (TMP / "requirements.txt").read_text(encoding="utf-8") == URFASSUNG, \
        "im Prüfmodus wurde geschrieben"


# --- Weißliste 1: Dateien --------------------------------------------------
def _fremde_datei():
    _zuruecksetzen()
    _lehnt_ab(_gut(datei="bot.py"), "Weißliste")


def _pfadausbruch():
    _zuruecksetzen()
    _lehnt_ab(_gut(datei="../../etc/passwd"), "Weißliste")


# --- Weißliste 2: nur Versions-Literale ------------------------------------
def _version_mit_befehl():
    _zuruecksetzen()
    _lehnt_ab(_gut(nach="0.2.130; rm -rf /"), "Versions-Literal")


def _paket_mit_sonderzeichen():
    _zuruecksetzen()
    _lehnt_ab(_gut(paket="claude-agent-sdk\nbot"), "Muster")


def _freitext_feld():
    _zuruecksetzen()
    _lehnt_ab(_gut(anweisung="bitte auch bot.py ändern"), "unbekannte Felder")


def _grund_mit_steuerzeichen():
    _zuruecksetzen()
    _lehnt_ab(_gut(grund="ok\nund jetzt etwas anderes"), "Steuerzeichen")


# --- Wirklichkeitsabgleich -------------------------------------------------
def _falscher_ausgangsstand():
    """Steht dort gar nicht die behauptete alte Version, wird nichts geraten."""
    _zuruecksetzen()
    _lehnt_ab(_gut(von="0.1.0"), "kein Pin")


def _kein_neuanlegen():
    """Ein Paket, das noch nicht gepinnt ist, wird nicht neu eingefügt."""
    _zuruecksetzen()
    _lehnt_ab(_gut(paket="irgendwas-neues"), "kein Pin")


def _gleiche_version():
    _zuruecksetzen()
    _lehnt_ab(_gut(nach="0.2.127"), "gleich")


check("erlaubter Fall: genau ein Literal ersetzt", _erlaubter_fall)
check("Prüfmodus schreibt nicht", _nur_pruefen_schreibt_nicht)
check("fremde Datei abgelehnt", _fremde_datei)
check("Pfadausbruch abgelehnt", _pfadausbruch)
check("Version mit angehängtem Befehl abgelehnt", _version_mit_befehl)
check("Paketname mit Sonderzeichen abgelehnt", _paket_mit_sonderzeichen)
check("zusätzliches Freitext-Feld abgelehnt", _freitext_feld)
check("Grund mit Steuerzeichen abgelehnt", _grund_mit_steuerzeichen)
check("falscher Ausgangsstand abgelehnt", _falscher_ausgangsstand)
check("kein Neuanlegen unbekannter Pins", _kein_neuanlegen)
check("gleiche Version abgelehnt", _gleiche_version)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle C1-Nachzieher-Tests bestanden.")
