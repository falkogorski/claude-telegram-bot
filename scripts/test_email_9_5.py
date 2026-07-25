#!/usr/bin/env python3
# <!-- ROLLE: test-email -->
"""Verhaltenstest 9.5 — E-Mail-Anbindung.

**Der Schwerpunkt liegt fast vollständig auf dem, was NICHT geschieht.** Senden
ist die einzige Fähigkeit dieses Systems, die unwiderruflich ist: Eine Mail ist
weg, sobald sie draußen ist, und keine Reue holt sie zurück. Ein Test, der vor
allem prüft, dass Senden funktioniert, prüft die falsche Seite.

Es wird **nichts versendet und nichts abgerufen** — kein Netz.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="mail-"))
os.environ["FREIGABE_DIR"] = str(_TMP / "freigaben")
for schluessel, wert in {
    "MAIL_GESCHAEFTLICH_ADRESSE": "adam@example.org",
    "MAIL_GESCHAEFTLICH_BENUTZER": "adam@example.org",
    "MAIL_GESCHAEFTLICH_KENNWORT": "geheim-nur-fuer-den-test",
    "MAIL_GESCHAEFTLICH_IMAP": "imap.example.org:993",
    "MAIL_GESCHAEFTLICH_SMTP": "smtp.example.org:465",
    # Bewusst unvollständig — darf NICHT auftauchen.
    "MAIL_HALBFERTIG_ADRESSE": "halb@example.org",
    "MAIL_HALBFERTIG_BENUTZER": "halb@example.org",
}.items():
    os.environ[schluessel] = wert

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import email_kanal as mk  # noqa: E402
import freigaben as f     # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _weist_ab(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except mk.Abgewiesen:
        return True
    return False


def _entwurf(**kw):
    daten = dict(konto="geschaeftlich", an="kunde@example.com",
                 betreff="Rechnung 2026-07", text="Anbei die Rechnung.")
    daten.update(kw)
    return mk.entwerfen(**daten)


# --- Der Riegel: ohne Freigabe geht nichts hinaus -------------------------
def _kein_versand_ohne_vorlage():
    e = _entwurf()
    assert _weist_ab(mk.senden, e), \
        "ein nie vorgelegter Entwurf ließ sich versenden!"


def _kein_versand_ohne_urteil():
    e = _entwurf()
    mk.zur_freigabe(e)
    assert _weist_ab(mk.senden, e), \
        "ein vorgelegter, aber unbeantworteter Entwurf ging hinaus!"


def _kein_versand_nach_ablehnung():
    e = _entwurf()
    k = mk.zur_freigabe(e)
    f.urteilen(k, False, "Adam")
    assert _weist_ab(mk.senden, e), "ein abgelehnter Entwurf ging hinaus!"


def _vorlage_zeigt_die_woertliche_mail():
    """Konkret vor Label — wer freigibt, muss sehen, was hinausgeht."""
    e = _entwurf(an=["kunde@example.com", "buchhaltung@example.com"])
    k = mk.zur_freigabe(e)
    a = f.finden(k)
    assert a is not None, "nichts geparkt"
    for pflicht in ("kunde@example.com", "buchhaltung@example.com",
                    "Rechnung 2026-07", "Anbei die Rechnung."):
        assert pflicht in a.aktion, f"„{pflicht}“ fehlt in der Vorlage"
    assert a.ampel == "gelb", "eine E-Mail wurde als grün eingestuft"
    assert not f.buendelbar([a]), \
        "eine E-Mail ist sammelfreigebbar — es darf keinen Dauer-Knopf geben"


# --- Kopfzeilen-Einschleusung --------------------------------------------
def _kopfzeilen_einschleusung_wird_abgewiesen():
    """Ein Umbruch im Betreff kann ein stilles Bcc erzeugen."""
    for feld, wert in (("betreff", "Hallo\r\nBcc: mitleser@fremd.example"),
                       ("betreff", "Hallo\nX-Etwas: bös"),
                       ("an", "kunde@example.com\r\nBcc: fremd@example.com")):
        assert _weist_ab(_entwurf, **{feld: wert}), \
            f"Steuerzeichen in „{feld}“ kamen durch: {wert!r}"


def _unbrauchbare_adresse_wird_abgewiesen():
    for schlecht in ("", "keine-adresse", "@example.com", "adam@", "   "):
        assert _weist_ab(_entwurf, an=schlecht), \
            f"unbrauchbare Adresse kam durch: {schlecht!r}"


# --- Anhänge --------------------------------------------------------------
def _geheimnis_anhang_wird_abgewiesen():
    """Auch auf ausdrücklichen Wunsch verlässt so etwas das Haus nicht."""
    for name in (".env", "id_ed25519", "api-token.txt"):
        p = _TMP / name
        p.write_text("egal", encoding="utf-8")
        assert _weist_ab(_entwurf, anhaenge=[str(p)]), \
            f"Geheimnis-Anhang kam durch: {name}"


def _fehlender_anhang_wird_abgewiesen():
    assert _weist_ab(_entwurf, anhaenge=[str(_TMP / "gibtsnicht.pdf")]), \
        "ein nicht vorhandener Anhang wurde stillschweigend hingenommen"


def _harmloser_anhang_geht_durch():
    p = _TMP / "rechnung.pdf"
    p.write_bytes(b"%PDF-1.4 test")
    e = _entwurf(anhaenge=[str(p)])
    assert e.anhaenge and Path(e.anhaenge[0]).name == "rechnung.pdf"
    assert "rechnung.pdf" in e.lesbar(), "der Anhang steht nicht in der Vorlage"


# --- Zugangsdaten ---------------------------------------------------------
def _kennwort_nirgends_sichtbar():
    """Ein Datensatz wandert in Protokolle und Fehlersuchen — das Kennwort nicht."""
    k = mk.konten()["geschaeftlich"]
    assert "geheim-nur-fuer-den-test" not in repr(k), \
        "das Kennwort steckt im Konto-Datensatz!"
    e = _entwurf()
    kennung = mk.zur_freigabe(e)
    a = f.finden(kennung)
    assert "geheim-nur-fuer-den-test" not in (a.aktion + a.titel + a.begruendung), \
        "das Kennwort landete in der Freigabe-Anfrage!"


def _halbfertiges_konto_wird_weggelassen():
    """Ein halb eingerichteter Versandweg ist gefährlicher als gar keiner."""
    assert "halbfertig" not in mk.konten(), \
        "ein unvollständig eingerichtetes Konto wurde als brauchbar geführt"
    assert _weist_ab(_entwurf, konto="halbfertig")


def _leere_pflichtfelder_werden_abgewiesen():
    assert _weist_ab(_entwurf, betreff="   "), "leerer Betreff kam durch"
    assert _weist_ab(_entwurf, text=""), "leerer Text kam durch"


def _absender_nur_aus_der_liste():
    """Ein frei wählbarer Absender käme einer Vollmacht gleich.

    Mailtexte entstehen hier teils aus Inhalten, die von außen kommen. Wer das
    `From` bestimmen kann, kann fremden Text unter Adams Adresse setzen —
    deshalb eine Allowlist in der geschützten Umgebung, keine freie Wahl.
    """
    os.environ["MAIL_GESCHAEFTLICH_ALIASSE"] = "info@example.org, buero@example.org"
    k = mk.konten()["geschaeftlich"]
    assert k.aliasse == ("info@example.org", "buero@example.org")

    # Erlaubt: Hauptadresse und beide Aliasse — ohne zweites Kennwort.
    for gut in ("adam@example.org", "info@example.org", "BUERO@example.org"):
        e = _entwurf(absender=gut)
        assert e.absender.lower() == gut.lower()
        assert gut.lower() in e.lesbar().lower(), \
            "der Absender steht nicht in der Vorlage"

    # Nicht erlaubt: alles andere.
    for boese in ("fremd@angreifer.example", "adam@example.org.angreifer.example",
                  "chef@grossefirma.example"):
        assert _weist_ab(_entwurf, absender=boese), \
            f"fremder Absender kam durch: {boese}"

    # Und die zweite Prüfung kurz vor dem Absenden greift auch dann, wenn die
    # Liste sich seit dem Entwurf geändert hat.
    e = _entwurf(absender="info@example.org")
    kennung = mk.zur_freigabe(e)
    f.urteilen(kennung, True, "Adam")
    os.environ["MAIL_GESCHAEFTLICH_ALIASSE"] = ""
    assert _weist_ab(mk.senden, e), \
        "ein inzwischen entfernter Absender ging trotzdem hinaus"


def _posteingang_ist_nur_lesend():
    """Fremdtext ist Datum, kein Auftrag — und der Abruf verändert nichts."""
    quelle = Path(mk.__file__).read_text(encoding="utf-8")
    assert 'readonly=True' in quelle, "der Posteingang wird nicht nur-lesend geöffnet"
    assert "BODY.PEEK" in quelle, \
        "der Abruf würde Nachrichten als gelesen markieren (PEEK fehlt)"
    assert "store" not in quelle.lower().replace("history", ""), \
        "es gibt einen verändernden IMAP-Aufruf"


check("kein Versand ohne Vorlage", _kein_versand_ohne_vorlage)
check("kein Versand ohne Urteil", _kein_versand_ohne_urteil)
check("kein Versand nach Ablehnung", _kein_versand_nach_ablehnung)
check("die Vorlage zeigt die wörtliche Mail (gelb, nicht bündelbar)",
      _vorlage_zeigt_die_woertliche_mail)
check("Kopfzeilen-Einschleusung wird abgewiesen",
      _kopfzeilen_einschleusung_wird_abgewiesen)
check("unbrauchbare Adressen werden abgewiesen", _unbrauchbare_adresse_wird_abgewiesen)
check("Geheimnis-Anhang verlässt das Haus nicht", _geheimnis_anhang_wird_abgewiesen)
check("fehlender Anhang wird abgewiesen", _fehlender_anhang_wird_abgewiesen)
check("harmloser Anhang geht durch und steht in der Vorlage",
      _harmloser_anhang_geht_durch)
check("das Kennwort taucht nirgends auf", _kennwort_nirgends_sichtbar)
check("halbfertiges Konto wird weggelassen", _halbfertiges_konto_wird_weggelassen)
check("leere Pflichtfelder werden abgewiesen", _leere_pflichtfelder_werden_abgewiesen)
check("Absender nur aus der Liste (Alias-Vollmacht)", _absender_nur_aus_der_liste)
check("Posteingang ist nur lesend", _posteingang_ist_nur_lesend)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle 9.5-E-Mail-Tests bestanden.")
