#!/usr/bin/env python3
# <!-- ROLLE: test-vorlese-regeln -->
"""Verhaltenstest B5 — Zahlen, die keine Zahlen sind.

**Der gemeinsame Nenner: Eine Ziffernfolge sagt nicht, was sie ist.** „2026"
kann ein Jahr, eine Menge oder das Ende einer Kennnummer sein. Die Stimme muss
aus dem Umfeld schließen — und wo das Umfeld nichts hergibt, darf sie nicht
raten.

**Was diese Prüfungen NICHT leisten:** Sie messen den Text, der an die Stimme
geht, nicht den Klang, der herauskommt. Ob edge-tts
„neunzehnhundertfünfundachtzig" tatsächlich sauber ausspricht, hört nur Adam.
Der Text ist das, was wir verantworten können — und der ist damit eindeutig,
was er vorher nicht war.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b5-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

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


def _datum_wird_datum():
    assert bot._normalize_dates("am 22.06.2026 um acht") == "am 22. Juni 2026 um acht"
    assert bot._normalize_dates("am 22.06. kommt er") == "am 22. Juni kommt er"
    assert bot._normalize_dates("1.1.2027") == "1. Januar 2027"


def _kein_datum_bleibt_unangetastet():
    """**Die wichtigere Hälfte.** Eine Regel, die zu viel greift, richtet mehr
    an als eine, die fehlt — sie erzeugt falsche Auskünfte statt nüchterner."""
    for harmlos in ("Python 3.12", "Version 4.7", "22.13.2026", "0.99.1"):
        assert bot._normalize_dates(harmlos) == harmlos, (
            f"{harmlos} wurde fälschlich zum Datum")


def _datum_laeuft_vor_der_versionsregel():
    """Andersherum hätte `_normalize_versions` aus `22.06.2026` zuerst
    „22 Punkt 06" gemacht — und das Datum wäre unrettbar."""
    aus = bot._strip_markdown_for_tts("Termin am 22.06.2026")
    assert "Juni" in aus and "Punkt" not in aus, f"Reihenfolge stimmt nicht: {aus}"
    # Gegenprobe: die Versionsregel muss weiter greifen.
    assert "Punkt" in bot._strip_markdown_for_tts("Python 3.12 läuft")


def _jahreszahl_nur_mit_jahresbezug():
    assert "neunzehnhundertfünfundachtzig" in bot._normalize_jahreszahlen("seit 1985")
    assert "neunzehnhundert" == bot._normalize_jahreszahlen("im 1900").split()[-1]
    # Ohne Bezug bleibt es eine Menge — „1985 Teilnehmer" ist kein Jahr.
    assert bot._normalize_jahreszahlen("1985 Teilnehmer") == "1985 Teilnehmer", \
        "eine bloße Menge wurde zum Jahrhundert erklärt"


def _ab_zweitausend_wird_nichts_veraendert():
    """Ab 2000 ist die deutsche Jahresform mit der Zahlform identisch — da gibt
    es nichts zu richten, und jede Änderung wäre nur ein neues Risiko."""
    for t in ("seit 2026", "im Jahr 2001", "ab 2030"):
        assert bot._normalize_jahreszahlen(t) == t, f"unnötig verändert: {t}"


def _kennnummer_wird_buchstabiert():
    aus = bot._normalize_kennnummern("Bestellnummer 4711829 ist offen")
    assert "4 7 1 1 8 2 9" in aus, f"die Kennung wird am Stück gelesen: {aus}"
    assert "IBAN 12345678" != bot._normalize_kennnummern("IBAN 12345678")


def _kennnummer_braucht_ein_ankuendigendes_wort():
    """Ohne diese Bremse würde jede größere Zahl zerhackt — „7940 MiB
    Arbeitsspeicher" als Ziffernfolge wäre absurd."""
    for menge in ("7940 MiB Arbeitsspeicher", "23005 Zeilen", "das kostet 12500 Euro"):
        assert bot._normalize_kennnummern(menge) == menge, \
            f"eine Menge wurde zur Kennung: {menge}"


def _kennnummer_erst_ab_fuenf_ziffern():
    """Vier Ziffern hinter „Rechnung" sind weit häufiger ein Jahr als eine
    Belegnummer. Im Zweifel nicht zerhacken."""
    assert bot._normalize_kennnummern("Rechnung 2026") == "Rechnung 2026"


def _kennnummer_laeuft_vor_der_jahresregel():
    """Sonst würde eine Kennung unterwegs in ihren letzten vier Ziffern zu
    einem Jahrhundert."""
    aus = bot._strip_markdown_for_tts("Seit Kundennummer 191985 ist er dabei")
    assert "1 9 1 9 8 5" in aus, f"die Reihenfolge kippt die Kennung: {aus}"
    assert "hundert" not in aus


def _kontext_hinweis_wird_nicht_gesprochen():
    """Der Bezugs-Vermerk ist Text für das MODELL. Vorgelesen wäre er
    Kauderwelsch."""
    roh = '[Kontext: Adam bezieht sich auf deine Nachricht: "abc"]: Und nun?'
    aus = bot._strip_markdown_for_tts(roh)
    assert "Kontext" not in aus and "Und nun" in aus, \
        f"der Bezugs-Vermerk landet in der Stimme: {aus}"


def _bestehende_regeln_stehen_noch():
    """Die Geschwister-Regel: Ein Eingriff in die Kette ist erst fertig, wenn
    geprüft ist, dass die vorhandenen Glieder noch greifen."""
    assert "zu" in bot._strip_markdown_for_tts("Endstand 3-1 im Pokal")
    assert "Punkt" in bot._strip_markdown_for_tts("macOS 14.5")
    assert "http" not in bot._strip_markdown_for_tts("Quelle: https://example.com/a")


check("Datum wird als Datum gelesen", _datum_wird_datum)
check("was KEIN Datum ist, bleibt unangetastet", _kein_datum_bleibt_unangetastet)
check("Datum läuft vor der Versionsregel", _datum_laeuft_vor_der_versionsregel)
check("Jahreszahl nur mit Jahresbezug", _jahreszahl_nur_mit_jahresbezug)
check("ab 2000 wird nichts verändert", _ab_zweitausend_wird_nichts_veraendert)
check("Kennnummer wird ziffernweise gelesen", _kennnummer_wird_buchstabiert)
check("Kennnummer braucht ein ankündigendes Wort",
      _kennnummer_braucht_ein_ankuendigendes_wort)
check("Kennnummer erst ab fünf Ziffern", _kennnummer_erst_ab_fuenf_ziffern)
check("Kennnummer läuft vor der Jahresregel", _kennnummer_laeuft_vor_der_jahresregel)
check("Kontext-Hinweis wird nicht gesprochen", _kontext_hinweis_wird_nicht_gesprochen)
check("die bestehenden Regeln greifen weiter (Geschwister)",
      _bestehende_regeln_stehen_noch)

print()
if fails:
    print(f"❌ {len(fails)} B5-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B5-Vorlese-Tests bestanden.")
