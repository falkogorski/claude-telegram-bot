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


def _uhrzeit_mit_indikator():
    """**Auftrag 1, Adams berichtigte Fassung vom 29.08., 00:15 Uhr.**

    Der Ausloeser ist das nachgestellte `Uhr` oder `h` — ein **struktureller**
    Indikator, kein Wort davor. Das folgt Adams Grundsatz: *Ein Wort traegt
    nie zuverlaessig einen Parameter.* Deshalb wirkt die Regel gleich, ob
    [um], [seit], [ab] oder [bis] davorsteht — genau der Fall, in dem die
    Ausgabe bisher mal so, mal so ausging.
    """
    for roh, erwartet, was in [
        ("um 20:05 Uhr", "um 20 Uhr 5", "Grundfall"),
        ("seit 20:05 Uhr", "seit 20 Uhr 5", "anderes Wort davor"),
        ("ab 20:05 Uhr", "ab 20 Uhr 5", "drittes Wort davor"),
        ("Start 20:00 Uhr", "Start 20 Uhr", "volle Stunde ohne Null"),
        ("um 16:03 Uhr", "um 16 Uhr 3", "fuehrende Null faellt weg"),
        ("Abfahrt 7:45 h", "Abfahrt 7 Uhr 45", "h als Indikator"),
    ]:
        ist = bot._strip_markdown_for_tts(roh)
        assert erwartet in ist, f"{was}: {roh!r} -> {ist!r}, erwartet {erwartet!r}"


def _ohne_indikator_wird_zu():
    """**Die Berichtigung ist der eigentliche Inhalt dieser Zeile.**

    Claudias erster Entwurf wollte jede Doppelpunkt-Zahl mit zweistelliger
    Minute als Uhrzeit lesen. Adam hat die Grenzfaelle gehoert: [21:19] wird
    heute korrekt als [21 zu 19] gesprochen — der Entwurf haette daraus ein
    falsches [21 Uhr 19] gemacht. **Eine Regel, die einen guten Fall
    verdirbt, um einen seltenen zu retten.**
    """
    for roh, erwartet, was in [
        ("Das Format ist 16:9.", "16 zu 9", "Seitenverhaeltnis am Satzende"),
        ("Endstand 2:1", "2 zu 1", "Sportergebnis"),
        ("Es stand 21:19", "21 zu 19", "zweistellig — der gerettete Fall"),
        ("Mischung 1:3", "1 zu 3", "Mischungsverhaeltnis"),
    ]:
        ist = bot._strip_markdown_for_tts(roh)
        assert erwartet in ist, f"{was}: {roh!r} -> {ist!r}, erwartet {erwartet!r}"
    # Keine erfundene Uhrzeit, wo keine sein kann.
    assert "Uhr" not in bot._strip_markdown_for_tts("Es stand 21:19")


def _ungueltige_zeit_bleibt_stehen():
    """Was keine gueltige Zeit ist, wird nicht umgedeutet.

    Vom ersten Prueflauf gefunden: [25:61 Uhr] liess der Uhrzeit-Zweig zu
    Recht liegen — und der Verhaeltnis-Zweig griff es danach auf und machte
    [25 zu 61 Uhr] daraus. **Ein halb angewandter Filter ist schlechter als
    keiner**, weil er eine Form erzeugt, die es in keiner Lesart gibt.
    """
    for roh in ("25:61 Uhr", "99:99 Uhr"):
        assert bot._strip_markdown_for_tts(roh).strip() == roh, \
            f"ungueltige Zeit wurde umgedeutet: {roh!r} -> " \
            f"{bot._strip_markdown_for_tts(roh)!r}"


def _tausenderpunkte():
    """**Auftrag 2 — seit dem 17.07.2026 vereinbart, nie gebaut.**

    Der mehrfach gegliederte Fall ist der lehrreiche: Die erste Fassung
    ersetzte je einen Punkt und lief iterativ — und liess [1.234.567]
    **unveraendert**, weil fuer die erste Gruppe der Lookahead und fuer die
    zweite der Lookbehind blockierte. Die Iteration bekam nie einen ersten
    Treffer.
    """
    for roh, erwartet, was in [
        ("800.000 Einwohner", "800 000 Einwohner", "einfache Gliederung"),
        ("1.234.567 Zeichen", "1 234 567 Zeichen", "mehrfach gegliedert"),
        ("rund 12.500 Euro", "12 500", "vierstellig"),
    ]:
        ist = bot._strip_markdown_for_tts(roh)
        assert erwartet in ist, f"{was}: {roh!r} -> {ist!r}, erwartet {erwartet!r}"


def _tausenderregel_greift_nicht_ins_datum():
    """Der Filter laesst Datum und Fassungsnummer in Ruhe — **aus sich heraus**.

    **`[BERICHTIGT 29.08.]` Diese Zeile hiess erst [die Stellung in der Kette]
    und behauptete, ohne die richtige Reihenfolge griffe die Tausenderregel
    in [22.06.2026] auf [06.202].** Die Entkernungs-Gegenprobe hat es
    widerlegt: Den Filter VOR das Datum zu schieben laesst den Pruefer gruen,
    weil er dort schlicht nicht greift.

    Der Grund ist konstruktiv — `\d{3}` verlangt genau drei Ziffern hinter
    dem Punkt. Also misst diese Zeile jetzt, **was wirklich schuetzt**: den
    Filter allein, ohne die Kette drumherum. Das ist die staerkere Zusage,
    denn sie haelt auch, wenn jemand die Reihenfolge umstellt.
    """
    for roh in ("22.06.2026", "am 1.06.2026", "Version 1.234", "Fassung 2.100"):
        assert bot._normalize_tausenderpunkte(roh) == roh, \
            f"der Filter greift ohne die Kette in {roh!r} -> " \
            f"{bot._normalize_tausenderpunkte(roh)!r}"
    # Und der Fall, den er sehr wohl treffen muss:
    assert bot._normalize_tausenderpunkte("800.000 Euro") == "800 000 Euro", \
        "der Filter greift gar nicht mehr — die Zeile oben waere bedeutungslos"
    ist = bot._strip_markdown_for_tts("am 22.06.2026 um 9:30 Uhr")
    assert "22. Juni 2026" in ist and "9 Uhr 30" in ist, \
        f"Datum und Uhrzeit vertragen sich nicht: {ist!r}"
    assert "06 202" not in ist, f"Tausenderregel hat ins Datum gegriffen: {ist!r}"
    ist = bot._strip_markdown_for_tts("Version 1.234 ist da")
    assert "1 234" not in ist, f"Fassungsnummer als Tausenderzahl gelesen: {ist!r}"


check("Uhrzeit: Indikator entscheidet, nicht das Wort davor", _uhrzeit_mit_indikator)
check("ohne Indikator wird [zu] gelesen", _ohne_indikator_wird_zu)
check("ungueltige Zeit bleibt unangetastet", _ungueltige_zeit_bleibt_stehen)
check("Tausenderpunkte werden Leerzeichen", _tausenderpunkte)
check("Tausenderregel greift nicht ins Datum", _tausenderregel_greift_nicht_ins_datum)
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

def _linktext_bleibt_stehen():
    """**Der Linktext ist oft satztragend** (Adam, 27.08. beim Hoeren).

    Aus *[Im Pruefraster der Basisfaehigkeiten steht eine echte Luecke]* wurde
    **[Im steht eine echte Luecke]** — die alte Fassung loeschte den ganzen
    Link samt Text. Die Annahme war, ein Linktext sei immer nur ein
    Quellenverweis am Satzrand. Er ist haeufig ein Subjekt, ein Objekt, ein
    Eigenname.
    """
    aus = bot._strip_markdown_for_tts(
        "Im [Prüfraster der Basisfähigkeiten](https://x.tld/a) steht eine Lücke")
    assert "Prüfraster der Basisfähigkeiten" in aus, \
        f"der Linktext wurde verschluckt: {aus!r}"
    assert "http" not in aus and "x.tld" not in aus, f"die Adresse blieb: {aus!r}"
    assert aus.startswith("Im Prüfraster"), f"der Satz ist zerbrochen: {aus!r}"


def _die_adresse_fliegt_trotzdem():
    """**Gegenrichtung:** Es sollte der Text bleiben, nicht die Adresse."""
    aus = bot._strip_markdown_for_tts("Siehe [heise](https://www.heise.de/a?b=1) dazu")
    assert "heise.de" not in aus and "?" not in aus, \
        f"die Adresse wurde mitgesprochen: {aus!r}"
    assert "Siehe heise dazu" in aus, f"Satz unvollstaendig: {aus!r}"


def _der_quellenhinweis_steht_nicht_in_der_reinigung():
    """**Er darf NICHT in `_strip_markdown_for_tts` sitzen.**

    Die Funktion laeuft zweimal ueber denselben Text — je Teilstueck und noch
    einmal in `_send_tts_chunk`. Solange sie nur entfernt, ist das harmlos.
    Sobald sie **anhaengt**, kaeme der Satz doppelt und nach jedem Teilstueck.
    """
    aus = bot._strip_markdown_for_tts("Siehe [heise](https://www.heise.de/a) dazu")
    assert "verlinkt" not in aus, \
        f"der Quellenhinweis sitzt in der Reinigung - er kaeme mehrfach: {aus!r}"


check("Linktext bleibt stehen (Adam 27.08.)", _linktext_bleibt_stehen)
check("die Adresse fliegt trotzdem (Gegenrichtung)", _die_adresse_fliegt_trotzdem)
check("der Quellenhinweis sitzt NICHT in der Reinigung",
      _der_quellenhinweis_steht_nicht_in_der_reinigung)


def _die_bildunterschrift_reisst_keine_ueberschrift_ab():
    """**Adam hat es viermal gemeldet.**

    Bei eingeschalteter Sprachausgabe haengt der Antworttext als
    Bildunterschrift an der ersten Sprachnachricht. Dort stand ein **harter
    Zeichenindex** bei 1024 — ohne Ruecksicht auf Zeilen, Absaetze oder
    Ueberschriften. `_find_safe_cut` lief erst danach, auf dem bereits falsch
    abgetrennten Rest: **Der Schutz kam zu spaet.**

    Fast jede inhaltliche Antwort ist laenger als 1024 Zeichen — der Schnitt
    griff also praktisch immer, sobald die Sprachausgabe an war.
    """
    text = "A" * 990 + "\n\n**Der wichtige Teil:**\n\nDarum geht es wirklich."
    schnitt = bot._find_safe_cut(text, 1024)
    assert schnitt < 1024, "der Schnitt ist noch der harte Zeichenindex"
    assert not bot._text_ends_with_heading(text[:schnitt]), \
        "die Bildunterschrift endet mit einer Ueberschrift"
    assert text[schnitt:].lstrip().startswith("**Der wichtige Teil:**"), \
        "die Ueberschrift wandert nicht mit ihrem Inhalt weiter"


def _der_ueberschriften_pruefer_ist_angeschlossen():
    """**Gebaut, aber nicht angeschlossen — von aussen nicht von
    [funktioniert] zu unterscheiden.**

    `_text_ends_with_heading` kam bis zum 28.08. **genau einmal** im ganzen
    Repo vor: in seiner eigenen Definition. Kein Aufruf, kein Test. Der
    Docstring behauptete [wird beim Streamen genutzt]. Waehrenddessen trug
    `_find_safe_cut` eine **eigene Kopie** derselben Muster — zwei Kopien
    laufen frueher oder spaeter auseinander.

    Gemessen ueber echte Aufrufknoten, nicht ueber Wortsuche.
    """
    import ast
    import inspect
    import textwrap
    baum = ast.parse(textwrap.dedent(inspect.getsource(bot._find_safe_cut)))
    gerufen = {getattr(k.func, "id", None) or getattr(k.func, "attr", None)
               for k in ast.walk(baum) if isinstance(k, ast.Call)}
    assert "_text_ends_with_heading" in gerufen, \
        "_find_safe_cut ruft den Ueberschriften-Pruefer nicht - es gibt wieder " \
        "zwei Kopien derselben Regel"


check("die Bildunterschrift reisst keine Ueberschrift ab",
      _die_bildunterschrift_reisst_keine_ueberschrift_ab)
check("der Ueberschriften-Pruefer ist angeschlossen",
      _der_ueberschriften_pruefer_ist_angeschlossen)

if fails:
    print(f"❌ {len(fails)} B5-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B5-Vorlese-Tests bestanden.")


def _groessen_werden_lesbar_angezeigt():
    """**Auftrag 4 aus dem Karteileichen-Bauauftrag, Adams Befund vom 28.08.**

    Woertlich: *[0,0 bedeutet aber nichts drin. Weil 0,0 gibt es eigentlich gar
    nicht. Das ist eine falsche Bezeichnung.]* Zehn Stellen formatierten starr
    auf Megabyte — eine Datei von 17,2 KB erschien als [0,0 MB], und das
    behauptet nicht [klein], sondern **leer**.

    Die Grenzwerte stehen so im Auftrag; sie sind der Kern, weil eine
    Einheiten-Wahl genau an den Uebergaengen falsch wird.
    """
    for roh, erwartet in [
        (0, "0 B"), (1, "1 B"), (1023, "1023 B"),
        (1024, "1,0 KB"), (999999, "976,6 KB"),
        (1048576, "1,0 MB"), (17612, "17,2 KB"),
        (2000 * 1048576, "2,0 GB"),
    ]:
        ist = bot.groesse_lesbar(roh)
        assert ist == erwartet, f"{roh} B -> {ist!r}, erwartet {erwartet!r}"
    # Der ausloesende Fall, von der Megabyte-Seite her.
    assert bot.groesse_lesbar(0.0168, ist_mb=True) == "17,2 KB", \
        "der Fall, der den Auftrag ausgeloest hat, ist nicht behoben"
    # Und: **keine Stelle formatiert mehr von Hand.** Sonst weicht die elfte ab.
    from pathlib import Path as _P
    quelle = _P(bot.__file__).read_text(encoding="utf-8")
    assert "size_mb:.1f" not in quelle, \
        "es gibt noch eine handformatierte Megabyte-Stelle — genau die weicht ab"


check("Dateigroessen tragen die passende Einheit", _groessen_werden_lesbar_angezeigt)
