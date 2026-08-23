"""Misst A1: kann eine Kopfzeile eine zweite vortäuschen? — **elf Varianten.**

**Kein Prüfer** — es misst und druckt, es bricht nicht. Die Prüfzeilen mit
Gegenprobe stehen in `scripts/test_email_9_5.py`; dieses Werkzeug dient dazu,
eine Zeichenklasse **auszumessen**, bevor man sie festschreibt.

**Warum es im Repo liegt:** Eine Messung, die nur im Sitzungsverlauf steht, ist
am nächsten Tag verloren (Ablageweg-Grundsatz). Es ist zugleich der Keim der
Korpus-Fälle 8 und 9 für Stufe B.

Aufruf: `.venv/bin/python scripts/mess_kopfzeilen_a1.py`
"""
import base64
import os
import sys
import tempfile
from pathlib import Path

_T = Path(tempfile.mkdtemp())
os.environ.update({
    "FREIGABE_DIR": str(_T / "f"),
    "MAIL_X_ADRESSE": "a@b.de", "MAIL_X_BENUTZER": "a@b.de",
    "MAIL_X_KENNWORT": "k", "MAIL_X_IMAP": "i.b.de", "MAIL_X_SMTP": "s.b.de"})
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import email_kanal as mk  # noqa: E402


def b64(s: str) -> str:
    return "=?utf-8?B?" + base64.b64encode(s.encode()).decode() + "?="


ZIEL = "Rechnung{}From: chef@firma.de"

# Die Trenner, die es zu treffen gilt — als Zugehörigkeitsregel geschrieben,
# nicht als Aufzählung im Text: Wer einen hinzufügt, ändert eine Zeile.
TRENNER = {
    "CRLF": "\r\n", "LF": "\n", "CR": "\r",
    "U+0085 NEL": "",
    "U+2028 LINE SEP": " ",
    "U+2029 PARA SEP": " ",
    "U+000B VT": "",
    "U+000C FF": "",
}
UNSICHTBAR = {
    "U+200B ZWSP": "​", "U+200C ZWNJ": "‌",
    "U+200D ZWJ": "‍", "U+2060 WJ": "⁠", "U+FEFF BOM": "﻿",
}
# Was nach der Bereinigung nicht mehr im Wert stehen darf.
VERBOTEN = set(TRENNER.values()) | set(UNSICHTBAR.values())
# **`\ufffd` gehoert dazu** — es ist kein Angriff, aber ein Kodierungsschaden,
# und meine erste Fassung hat ihn durchgelassen: `Rechnung\ufffd\ufffdFrom:`
# galt als „dicht". Ein Messwerkzeug, das Kauderwelsch fuer heil haelt, misst
# die Haelfte.
VERBOTEN.add("\ufffd")


def zerlegen(betreff: str, zusatz: str = "") -> dict:
    kopf = ("From: fremd@boese.tld\r\nSubject: " + betreff + "\r\n"
            + zusatz + "Date: Sat, 23 Aug 2026 09:00:00 +0200\r\n")
    return mk._kopf_zerlegen(kopf.encode("utf-8"))


def zeile(name: str, felder: dict) -> bool:
    absender = (felder.get("from") or "").strip()
    betreff = felder.get("subject") or ""
    echt = absender == "fremd@boese.tld"
    rest = [c for c in betreff if c in VERBOTEN]
    dicht = echt and not rest
    grund = ""
    if not echt:
        grund = f"  ← Absender gefaelscht: {absender!r}"
    elif rest:
        grund = f"  ← Restzeichen: {[hex(ord(c)) for c in rest]}"
    print("  %-22s %-9s %r%s" % (name, "✓ dicht" if dicht else "✗ BEFUND",
                                 betreff[:44], grund))
    return dicht


def main() -> int:
    print("A1 — kann eine Kopfzeile eine zweite vortaeuschen?")
    print("=" * 78)
    alle = []

    print("\nKODIERTE Trenner im Betreff:")
    for name, t in TRENNER.items():
        alle.append(zeile(name, zerlegen(b64(ZIEL.format(t)))))

    print("\nUNSICHTBARE Zeichen mitten im Wort (Korpus-Fall 8):")
    for name, t in UNSICHTBAR.items():
        alle.append(zeile(name, zerlegen(b64("Rech" + t + "nung"))))

    print("\nROHE, unkodierte Trenner (Engywucks Weg, eine Stufe frueher):")
    for name, t in TRENNER.items():
        alle.append(zeile("roh " + name, zerlegen(ZIEL.format(t))))

    print("\nWIEDERHOLTES Feld — die erste Nennung muss gewinnen:")
    alle.append(zeile("zweites From", zerlegen("harmlos",
                                               "From: chef@firma.de\r\n")))

    # **Der Fall, der wirklich greift** (Engywuck, 23.08., nach meiner
    # Widerlegung seines ersten Mechanismus): die FALTUNG. Im Mail-Format darf
    # ein langer Wert über mehrere Zeilen laufen, wenn die Fortsetzung mit
    # Leerraum beginnt. Die alte Handschleife las eine solche Zeile als eigenes
    # Feld — weil `name.strip().lower()` **genau den Marker entfernt**, der sie
    # als Fortsetzung ausweist. Und das Wörterbuch überschreibt, also gewann
    # die spätere Nennung.
    #
    # Kein Entziffern beteiligt, reiner Rohtext. Das ist Korpus-Fall 9 in
    # seiner richtigen Fassung.
    print("\nGEFALTETER Kopf — die Fortsetzungszeile darf kein Feld werden:")
    gefaltet = ("From: fremd@boese.tld\r\n"
                "Subject: Rechnung\r\n"
                " From: chef@firma.de\r\n"
                "Date: Sat, 23 Aug 2026 09:00:00 +0200\r\n")
    alle.append(zeile("Faltung mit From:", mk._kopf_zerlegen(gefaltet.encode())))
    # Und mit Tabulator statt Leerzeichen — beides ist gültiger Leerraum.
    alle.append(zeile("Faltung mit Tab",
                      mk._kopf_zerlegen(gefaltet.replace(" From:", "\tFrom:").encode())))

    offen = len(alle) - sum(alle)
    print()
    print(f"{sum(alle)} von {len(alle)} dicht" +
          (f" — {offen} BEFUND(E)" if offen else " — keine Befunde"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
