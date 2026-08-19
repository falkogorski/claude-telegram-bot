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
    assert "neunzehnhundert" == bot._normalize_jahreszahlen("anno 1900").split()[-1]
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


def _gliederungsnummer_ist_kein_datum():
    """**F-1, der Befund mit dem größten Schaden.** `Punkt 9.4.` wurde zu
    `9. April` — eine Falschauskunft über den eigenen Projektstand, gesprochen
    mit voller Bestimmtheit. `MIGRATION.md` besteht aus solchen Nummern, und
    der Dokument-Vorlesepfad schickt Dokumentinhalt durch dieselbe Kette."""
    for gliederung in ("Punkt 9.4. ist offen", "siehe Phase 5.21.",
                       "Abschnitt 3.12.", "Regel 2.1.", "Schritt 1.3."):
        assert bot._normalize_dates(gliederung) == gliederung, \
            f"eine Gliederungsnummer wurde zum Datum: {gliederung}"
    # Gegenprobe: ein echtes Datum muss weiterhin durchkommen.
    assert bot._normalize_dates("am 22.06. kommt er") == "am 22. Juni kommt er"


def _tag_muss_es_geben():
    """Geprüft wurde bisher nur der Monat — `Punkt 40.5.` ergab `40. Mai`.
    Das war schärfer als der notierte Befund."""
    for unmoeglich in ("40.5.", "0.7.", "99.12."):
        assert bot._normalize_dates(unmoeglich) == unmoeglich, \
            f"ein Tag außerhalb des Kalenders wurde zum Datum: {unmoeglich}"
    assert bot._normalize_dates("31.12.") == "31. Dezember"


def _menge_schlaegt_jahreshinweis():
    """`von`, `bis` und `ab` sind im Deutschen überwiegend MENGEN-Wörter. Steht
    hinter der Zahl eine Einheit, gewinnt sie — sie ist die spezifischere
    Aussage."""
    for menge in ("bis 1500 Zeichen", "von 1200 Wörter", "ab 1800 Euro",
                  "seit 1500 Zeilen"):
        assert bot._normalize_jahreszahlen(menge) == menge, \
            f"eine Menge wurde zum Jahrhundert: {menge}"
    # Gegenprobe in beide Richtungen: ohne Einheit bleibt es ein Jahr.
    assert "neunzehnhundert" in bot._normalize_jahreszahlen("von 1985 bis 1990")


def _im_ist_kein_jahreshinweis():
    """`im` trug nie allein einen Jahresbezug — „im Jahr 1985" wird schon von
    `jahr` erfasst, „im 1985" sagt niemand. Was es erfasste, waren Mengen."""
    assert bot._normalize_jahreszahlen("im 1500-Zeichen-Fenster") == \
        "im 1500-Zeichen-Fenster"
    assert "neunzehnhundert" in bot._normalize_jahreszahlen("im Jahr 1985")


def _die_eins_steht_allein():
    """Die Eins ist das einzige deutsche Zahlwort mit zwei Formen: gebunden
    „einundzwanzig", freistehend „eins". `seit 1901` ergab
    „neunzehnhundertein" — ein Wort, das es nicht gibt."""
    assert "neunzehnhunderteins" in bot._normalize_jahreszahlen("seit 1901")
    # Gegenprobe: gebunden bleibt die Eins „ein".
    assert "neunzehnhunderteinundzwanzig" in bot._normalize_jahreszahlen("seit 1921")


def _satzende_verdeckt_nichts():
    """Die häufigste Stellung überhaupt — und die einzige, die gar nicht
    griff. Punkt und Komma dürfen nur blocken, wenn eine ZIFFER folgt."""
    assert "4 7 1 1 8 2 9." in bot._normalize_kennnummern("Bestellnummer 4711829.")
    assert "neunzehnhunderteins" in bot._normalize_jahreszahlen("gegründet 1901.")
    # Gegenprobe: eine Dezimalzahl bleibt heil, sonst wäre der Fix ein Rückschritt.
    assert bot._normalize_kennnummern("Kundennummer 12345,67") == \
        "Kundennummer 12345,67"
    assert bot._normalize_kennnummern("Beleg 12345.67") == "Beleg 12345.67"


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
check("F-1: Gliederungsnummer ist kein Datum", _gliederungsnummer_ist_kein_datum)
check("F-1: den Tag muss es im Kalender geben", _tag_muss_es_geben)
check("F-1: Menge schlägt Jahres-Hinweis", _menge_schlaegt_jahreshinweis)
check("F-1: „im“ ist kein Jahres-Hinweis", _im_ist_kein_jahreshinweis)
check("F-1: die Eins steht allein als „eins“", _die_eins_steht_allein)
check("F-1: das Satzende verdeckt nichts mehr", _satzende_verdeckt_nichts)


def _die_bereichsform_wird_einheitlich_gelesen():
    """**Der F-1-Rest, an seiner geplanten Stelle.** In „1985 bis 1990" trug
    nur die ZWEITE Zahl einen Hinweis davor — die erste blieb Ziffernfolge, und
    der Satz klang halb uebersetzt. Kein Fehler, aber eine Unsauberkeit, die
    beim Hoeren auffaellt.

    Geprueft wird die GANZE Kette, nicht die Einzelregel: Den Bindestrich
    wandelt `_normalize_number_ranges` bereits vorher in ein „bis" um, und
    genau dieses Zusammenspiel ist der Punkt."""
    aus = bot._strip_markdown_for_tts("Saison 1985-1990 war stark")
    assert "neunzehnhundertfünfundachtzig bis neunzehnhundertneunzig" in aus, \
        f"die Bereichsform bleibt halb: {aus}"
    # Gegenprobe: ein MENGEN-Bereich bleibt unangetastet, auch wenn die
    # Einheit erst hinter der zweiten Zahl steht.
    assert bot._normalize_jahreszahlen("1500 bis 1800 Zeichen") == \
        "1500 bis 1800 Zeichen", "ein Mengenbereich wurde zum Jahrhundert"


check("F-5: die Bereichsform wird einheitlich gelesen (F-1-Rest)",
      _die_bereichsform_wird_einheitlich_gelesen)
check("die bestehenden Regeln greifen weiter (Geschwister)",
      _bestehende_regeln_stehen_noch)

print()
if fails:
    print(f"❌ {len(fails)} B5-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B5-Vorlese-Tests bestanden.")
