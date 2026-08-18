#!/usr/bin/env python3
# <!-- ROLLE: test-kanal-routing -->
"""Verhaltenstest Phase 6 (channels.py) — reine Logik, kein Telegram.

Deckt: Haus-Erkennung (emoji-/schreibweisentolerant, Bestand ausgenommen),
Zimmer-Planung/Idempotenz, Ordner-Spiegelung, Routing-Auflösung inkl.
„kein falscher Fallback"-Invariante.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import channels as c  # noqa: E402

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


def _detect():
    assert c.detect_house("🔧 Werkstatt") == "werkstatt"
    assert c.detect_house("werkstatt") == "werkstatt"
    assert c.detect_house("🕰️ Nirgendhaus") == "nirgendhaus"
    assert c.detect_house("Handelshaus (Geschäfte)") == "handelshaus"
    assert c.detect_house("📚 Bibliothek") == "bibliothek"


def _bestand_nicht_auto():
    assert c.detect_house("Jakuna-San") is None
    assert c.detect_house("🏠 Jakuna-San") is None


def _unbekannt():
    assert c.detect_house("Zufallsgruppe") is None
    assert c.detect_house(None) is None
    assert c.detect_house("") is None


def _ordner():
    assert c.folder_name("Migration & Technik") == "migration-technik"
    assert c.folder_name("Rechnungen & Büro") == "rechnungen-buro"
    assert c.folder_name("Recht & Zahlen") == "recht-zahlen"
    assert c.folder_name("Produkt & Blaupause") == "produkt-blaupause"


def _plan_und_idempotenz():
    p = {}
    c.register_house(p, "werkstatt", -100111, "Werkstatt", True)
    assert c.missing_zimmer(p, "werkstatt") == [
        "Migration & Technik", "Fanpost", "Rechnungen & Büro", "Offene Punkte"]
    c.record_topic(p, "werkstatt", "Migration & Technik", 12)
    assert "Migration & Technik" not in c.missing_zimmer(p, "werkstatt")
    # erneutes Registrieren darf Topics nicht verlieren
    c.register_house(p, "werkstatt", -100111, "🔧 Werkstatt", True)
    assert c.resolve_route(p, "bot_status") == (-100111, 12)


def _routing_kein_falschfallback():
    p = {}
    # Ohne jede Registrierung: nie ein Ziel erfinden
    assert c.resolve_route(p, "research") is None
    assert c.resolve_route(p, "bot_status") is None
    assert c.resolve_route(p, "unassigned") is None
    # Haus da, Topic fehlt → immer noch None (kein Haus-Default)
    c.register_house(p, "bibliothek", -100222, "Bibliothek", True)
    assert c.resolve_route(p, "research") is None
    c.record_topic(p, "bibliothek", "Recherchen & Referenzen", 7)
    assert c.resolve_route(p, "research") == (-100222, 7)
    # unbekannte Quelle
    assert c.resolve_route(p, "was-auch-immer") is None


def _alle_haeuser_vollstaendig():
    # 4 Häuser, 13 Zimmer gesamt (Audit-Entscheid v3)
    assert set(c.HOUSES) == {"werkstatt", "nirgendhaus", "handelshaus", "bibliothek"}
    total = sum(len(h["zimmer"]) for h in c.HOUSES.values())
    assert total == 13, f"erwartet 13 Zimmer, gefunden {total}"


check("Haus-Erkennung tolerant", _detect)
check("Bestand Jakuna-San nicht auto", _bestand_nicht_auto)
check("Unbekannte/leere Titel → None", _unbekannt)
check("Ordner-Spiegelung 4.3", _ordner)
check("Zimmer-Planung + Idempotenz", _plan_und_idempotenz)
check("Routing ohne Falsch-Fallback", _routing_kein_falschfallback)
check("Struktur vollständig (4 Häuser/13 Zimmer)", _alle_haeuser_vollstaendig)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Phase-6-Kanaltests bestanden.")
