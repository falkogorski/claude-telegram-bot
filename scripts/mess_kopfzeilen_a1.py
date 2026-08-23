"""Misst Engywucks A1-Befund: kann eine kodierte Kopfzeile eine zweite vortaeuschen?"""
import os, sys, tempfile, base64, quopri
from pathlib import Path

_T = Path(tempfile.mkdtemp())
os.environ.update({
    "FREIGABE_DIR": str(_T / "f"),
    "MAIL_X_ADRESSE": "a@b.de", "MAIL_X_BENUTZER": "a@b.de",
    "MAIL_X_KENNWORT": "k", "MAIL_X_IMAP": "i.b.de", "MAIL_X_SMTP": "s.b.de"})
sys.path.insert(0, ".")
import email_kanal as mk


def b64(s):
    return "=?utf-8?B?" + base64.b64encode(s.encode()).decode() + "?="


def qp(s):
    return "=?utf-8?Q?" + quopri.encodestring(s.encode()).decode().replace(" ", "_") + "?="


ZIEL = "Rechnung{}From: chef@firma.de"
faelle = {
    "CRLF (base64)":         b64(ZIEL.format("\r\n")),
    "LF allein":             b64(ZIEL.format("\n")),
    "CR allein":             b64(ZIEL.format("\r")),
    "U+2028 Zeilentrenner":  b64(ZIEL.format(" ")),
    "U+2029 Absatztrenner":  b64(ZIEL.format(" ")),
    "U+0085 NEL":            b64(ZIEL.format("")),
    "U+000B Vertikaltab":    b64(ZIEL.format("")),
    "U+000C Seitenvorschub": b64(ZIEL.format("")),
    "Quoted-Printable":      qp(ZIEL.format("\r\n")),
    "Zero-Width mittendrin": b64("Rech​nung"),
    "roh, unkodiert":        ZIEL.format("\r\n"),
}

print("%-24s %-10s %s" % ("Fall", "Befund", "Betreff nach _entziffern"))
print("-" * 100)
befunde = 0
for name, betreff in faelle.items():
    kopf = "From: fremd@boese.tld\r\nSubject: " + betreff + "\r\nDate: heute\r\n"
    felder = {}
    for zeile in kopf.splitlines():
        if ":" in zeile:
            n, _, w = zeile.partition(":")
            felder[n.strip().lower()] = mk._entziffern(w)
    s = felder.get("subject", "")
    trenner = [c for c in s if c in "\r\n  "]
    unsichtbar = [c for c in s if c in "​‌‍﻿"]
    gefaelscht = felder.get("from", "").strip() != "fremd@boese.tld"
    schlimm = bool(trenner or unsichtbar or gefaelscht)
    befunde += schlimm
    print("%-24s %-10s %r" % (name, "✗ BEFUND" if schlimm else "✓ dicht", s[:52]))

print()
print(f"Befunde: {befunde} von {len(faelle)}")
