#!/usr/bin/env python3
# <!-- ROLLE: test-websuche-check -->
"""Die Daempfung des Websuche-Waechters — **ausgefuehrt, nicht gelesen.**

Ein Waechter, der bei jeder Drosselung rot meldet, wird binnen zwei Tagen
abgeschaltet. Einer, der nie meldet, ist die Lage vom 27.08. Zwischen beidem
liegt genau diese Funktion, und sie ist deshalb herausgezogen.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import websuche_check as wc  # noqa: E402

fails: list[str] = []


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


JETZT = 1_700_000_000.0


def _totalausfall_meldet_sofort():
    """Alle tot ist kein Rauschen — da wird nicht gedaempft."""
    stufe, schwach = wc.beurteilen("ausgefallen", 0, {}, JETZT)
    assert stufe == "rot", f"Totalausfall meldet nur {stufe!r}"
    assert schwach is True


def _erste_schwaeche_meldet_noch_nicht():
    """Drosselung ist voruebergehend — erst beim zweiten Mal."""
    stufe, schwach = wc.beurteilen("duenn", 1, {}, JETZT)
    assert stufe == "gelb", f"erste Schwaeche meldet schon {stufe!r}"
    assert schwach is True, "die Schwaeche wird nicht fuer morgen vermerkt"


def _zweite_schwaeche_meldet():
    """Zweimal hintereinander ist kein Zufall mehr."""
    vorher = {"schwach": True, "zeit": JETZT - 24 * 3600}
    stufe, _ = wc.beurteilen("duenn", 1, vorher, JETZT)
    assert stufe == "rot", f"zweite Schwaeche meldet nur {stufe!r}"


def _alte_schwaeche_zaehlt_nicht_mehr():
    """**Die Gegenrichtung.** Ein Ausfall vor drei Wochen darf heute nicht
    rot faerben — sonst bleibt der Waechter fuer immer rot."""
    vorher = {"schwach": True, "zeit": JETZT - 21 * 24 * 3600}
    stufe, _ = wc.beurteilen("duenn", 1, vorher, JETZT)
    assert stufe == "gelb", f"eine drei Wochen alte Schwaeche faerbt rot ({stufe!r})"


def _gesunder_stand_loescht_den_vermerk():
    """Sonst haengt eine einmalige Drosselung ewig nach."""
    vorher = {"schwach": True, "zeit": JETZT - 3600}
    stufe, schwach = wc.beurteilen("ok", 12, vorher, JETZT)
    assert stufe == "gruen", f"gesunder Stand meldet {stufe!r}"
    assert schwach is False, "der Vermerk bleibt trotz Erholung stehen"


def _ohne_zahl_keine_falsche_roete():
    """Ist die Zulieferer-Zahl nicht ermittelbar, wird nicht geraten."""
    stufe, schwach = wc.beurteilen("duenn", None, {}, JETZT)
    assert stufe == "gruen" and schwach is False, \
        f"ohne Zahl wird eine Schwaeche behauptet: {stufe!r}"


def _der_pruefer_ruft_kein_modell():
    """**AGB-Leitplanke:** Zeitgesteuerte Laeufe loesen keinen Modell-Aufruf
    aus. Gemessen ueber echte Aufrufknoten, nicht ueber Wortsuche."""
    import ast
    baum = ast.parse(Path(wc.__file__).read_text(encoding="utf-8"))
    verboten = {"query", "ClaudeSDKClient", "process_user_text", "anthropic"}
    for k in ast.walk(baum):
        if isinstance(k, ast.Call):
            name = getattr(k.func, "id", None) or getattr(k.func, "attr", None)
            assert name not in verboten, f"Modell-Aufruf im Tagescheck: {name}"


check("Totalausfall meldet sofort", _totalausfall_meldet_sofort)
check("erste Schwaeche meldet noch nicht", _erste_schwaeche_meldet_noch_nicht)
check("zweite Schwaeche meldet", _zweite_schwaeche_meldet)
check("alte Schwaeche zaehlt nicht mehr (Gegenrichtung)", _alte_schwaeche_zaehlt_nicht_mehr)
check("gesunder Stand loescht den Vermerk", _gesunder_stand_loescht_den_vermerk)
check("ohne Zahl keine falsche Roete", _ohne_zahl_keine_falsche_roete)
check("der Pruefer ruft kein Modell", _der_pruefer_ruft_kein_modell)

print()
if fails:
    print(f"❌ {len(fails)} Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Websuche-Waechter-Tests bestanden.")
