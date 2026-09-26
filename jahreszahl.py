# <!-- ROLLE: jahreszahl-erkennung -->
"""Ist eine vierstellige Zahl ein Jahr? — EINE Antwort fuer alle Sprechwege.

`[NEU 26.09.2026, Claudias Auftrag „Jahreszahlen in Klammern", Engywucks
Zettel f4 Teil 2]` Es gab drei Sprechwege, und jeder erkannte Jahre selbst:
die edge-tts-Kette und die Piper-Aufbereitung (beide ueber
`bot._normalize_jahreszahlen`) und `sprachausgabe_azure.ssml_text`. Gemessen
am 26.09.: edge und Piper lasen „RL (1922)" als Menge, Azure dagegen JEDE
vierstellige Zahl als Jahr, auch „1500 Zeichen". Derselbe Fehler in zwei
Richtungen — deshalb eine reine Funktion, die alle drei rufen.

Rueckgabe: `"jahr"`, `"menge"` oder `"unklar"`. Unklar heisst: kein Hinweis
in beide Richtungen; jeder Weg liest die Zahl dann, wie er sie ohnehin liest.

**Der Hinweis kommt aus Woertern UND aus der Satzstruktur** (Adams Grundsatz
vom 28.08.: ein einzelnes Wort traegt keinen verlaesslichen Parameter):
- ein Jahres-Wort davor (`seit`, `ab`, `Baujahr` …),
- ein Bereich ohne Einheit danach (`1985 bis 1990`, `1910–1914`),
- **allein in Klammern** `(1927)`, **am Klammeranfang vor einem Komma**
  `(1936, Kleinserie)`, **als Bereich in Klammern** `(1910–1914)`.

**Die Einheit danach gewinnt immer** — auch gegen ein Jahres-Wort: „bis 1500
Zeichen" und „(1500 Euro)" sind Mengen.

**Bekannte Grenzen** (im Pruefer dokumentiert): Eine Menge allein in
Klammern ohne Einheit, etwa „Teilnehmer (1200)", wird als Jahr gelesen, ebenso
„(1250, Spalte 3)". Das kommt seltener vor als der Jahresfall und fiele nur
beim Hoeren auf. Ein Kennungs-Wort davor („Kundennummer (1234)") schuetzt.
"""
from __future__ import annotations

import re

# Woerter, die eine vierstellige Zahl als JAHR ausweisen (F-1: `im` gestrichen,
# es erfasste nur Mengen wie „im 1500-Zeichen-Fenster").
JAHR_HINWEIS = re.compile(
    r"(?:\b(?:jahr|jahre|jahren|seit|ab|bis|von|anno|baujahr|jahrgang|"
    r"geboren|gegründet|gegruendet|damals|sommer|winter|frühjahr|fruehjahr|"
    r"herbst)\b\W{0,3})$", re.IGNORECASE)

# Folgt eine Masseinheit, ist die Zahl eine Menge (F-1).
MENGEN_EINHEIT = re.compile(
    r"^\W{0,3}(zeichen|wörter|woerter|worte|zeilen|seiten|stück|stueck|"
    r"euro|dollar|cent|meter|kilometer|km|kg|gramm|tonnen|liter|"
    r"mb|gb|kb|tb|mib|gib|kib|byte|bytes|bit|pixel|punkte|"
    r"teilnehmer|personen|leute|kunden|nutzer|mitglieder|besucher|"
    r"sekunden|minuten|stunden|tage|wochen|monate|kalorien|grad|prozent)\b",
    re.IGNORECASE)

_JAHR = r"1[1-9]\d\d|20\d\d"
_STRICH = r"(?:bis|–|—|-)"
_BEREICH_NACH = re.compile(rf"\s*{_STRICH}\s*(?:{_JAHR})\b(.{{0,20}})", re.DOTALL)
_BEREICH_VOR = re.compile(rf"(?:{_JAHR})\s*{_STRICH}\s*$")
_KLAMMER_AUF = re.compile(r"\(\s*$")
# Komma nur, wenn danach keine Zahl und kein Strich folgt (Widerlegung M3):
# `(1920, 1080)` und `(1300, 1500 Euro)` sind keine Jahre.
_KLAMMER_ZU = re.compile(r"\s*(?:\)|,(?!\s*[\d\-–]))")
# Ein Kennungs-Wort vor der Klammer macht die Zahl zur Nummer (Widerlegung
# M2): `Kundennummer (1234)`, `PIN (1234)`, `Seite (1234)`.
_KENNUNG_VOR = re.compile(
    r"\b(?:nummer|nr|kennung|kennzahl|id|pin|tan|iban|konto|kontonummer|"
    r"auftrag|beleg|sendung|telefon|rufnummer|bestellung|ticket|vorgang|"
    r"referenz|aktenzeichen|postleitzahl|plz|seite|raum|zimmer|platz|"
    r"\w*nummer|\w*nr)\.?\s*\(\s*$", re.IGNORECASE)


def art(text: str, start: int, ende: int) -> str:
    """Wie ist die Zahl `text[start:ende]` zu lesen: jahr, menge oder unklar."""
    vor = text[max(0, start - 30):start]
    nach = text[ende:ende + 30]
    if MENGEN_EINHEIT.match(nach[:20]):
        # Jahres-Wort UND Einheit: widerspruechlich — „seit 1990 Kunden" ist
        # ein Jahr, „bis 1500 Zeichen" eine Menge. Dann unklar, und jeder Weg
        # bleibt bei seiner bisherigen Lesart (Widerlegung M4).
        return "unklar" if JAHR_HINWEIS.search(vor) else "menge"
    if _KENNUNG_VOR.search(vor):
        return "menge"
    bereich = _BEREICH_NACH.match(nach)
    if bereich:
        # „1500 bis 1800 Zeichen": die Einheit am Bereichsende gilt fuer beide.
        return "menge" if MENGEN_EINHEIT.match(bereich.group(1)) else "jahr"
    if JAHR_HINWEIS.search(vor) or _BEREICH_VOR.search(vor):
        return "jahr"
    if _KLAMMER_AUF.search(vor) and _KLAMMER_ZU.match(nach):
        return "jahr"
    return "unklar"
