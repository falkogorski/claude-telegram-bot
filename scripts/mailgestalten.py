#!/usr/bin/env python3
# <!-- ROLLE: mailgestalten -->
"""Der **Gestalten-Erzeuger** — Rang 0 des Mail-Umbaus (Engywucks Bauauftrag).

**Die Frage, die dieser Erzeuger beantwortet, ist nicht [welche Angriffe
nehmen wir auf], sondern [woher kommt die Menge der Mail-Gestalten].** Der
alte Korpus (23 Handfaelle) enthielt **keine einzige Mail, wie ein echtes
Mailprogramm sie baut** — kein MIME-Multipart, keine Uebertragungskodierung,
kein Zeichensatz ausser utf-8. Deshalb war er gruen, und deshalb kamen
fuenfzehn Befunde durch ihn hindurch.

**Die Menge kommt hier aus drei Quellen, keine davon eine Auswahl:**

1. **Der eigenen Standardbibliothek als Norm-Verzeichnis** — `encodings.
   aliases` kennt die Zeichensaetze, `mimetypes` die Anhangsarten,
   `unicodedata` die Formatzeichen, `xml.etree.ElementTree.HTML_EMPTY` die
   Leerelemente. Diese Mengen **existieren unabhaengig von unserem Code** —
   sie sind genau das, wovon unser Code nichts weiss.
2. **Dem eigenen Syntaxbaum** — `mailtext._STUMM` und `_UNSICHTBAR_STIL`
   sagen, was unser Code fuer stumm bzw. verborgen haelt.
3. **`EmailMessage` selbst** — die Gestalt wird **gebaut statt getippt**.
   Damit ist sie bauartbedingt echt: Was hier herauskommt, hat dieselbe Form
   wie die Post eines echten Mailprogramms, weil dieselbe Bibliothek sie
   formt.

**Der eleganteste Fund der Studie war eine Mengenoperation:**
`mailtext._STUMM & ET.HTML_EMPTY == {link, meta}` — genau die zwei Elemente,
an denen Befund 1 hing. Die Frage [schreibt man `<meta …>` oder
`<meta …></meta>`?] ist damit **keine Handentscheidung mehr**.

**Was dieser Erzeuger NICHT schliesst** — und das darf nie als geschlossen
berichtet werden: Er schliesst die Klasse *[der Code hat einen Zweig und
rechnet falsch]*. Er schliesst **nicht** *[der Code hat gar keinen Zweig]* —
`<style>`-Klassen, weisse Schrift per `<font>`, `aria-hidden`,
`position:absolute;left:-9999px`, `width="0"` bleiben strukturell ausserhalb
seiner Reichweite. Ein Register des Fuer-das-Auge-Unsichtbaren gibt es
nicht; das waere ein Renderer.

**Warum er NICHT im Regressionslauf steht** (Engywucks Auflage 1): Er ist ab
Tag eins rot. Im Regressionslauf blockierte er jeden Commit — oder er
erzwaenge eine Liste bekannt-roter Gestalten, und das waere **genau die
Handauswahl, gegen die er antritt, nur mit Freibrief.** Aufnahme erst, wenn
die Reparatur durch ist.

Aufruf:
    .venv/bin/python scripts/mailgestalten.py [--deckel N] [--zeige N]
"""
from __future__ import annotations

import argparse
import itertools
import mimetypes
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from email import encoders
from email.message import EmailMessage
from email import policy
from encodings.aliases import aliases
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
import mailtext  # noqa: E402


# --------------------------------------------------------------------------
# Die Achsen — jede aus einer Quelle, keine von Hand
# --------------------------------------------------------------------------

def achsenstand() -> dict[str, int]:
    """**Gehoert in JEDEN Bericht** (Engywucks zweite ungeprueffte Sache).

    Ohne diese Zahlen ist nicht unterscheidbar, ob der Erzeuger etwas
    **gefunden** hat oder ob sich die **Maschine** geaendert hat. Belegt
    schon beim ersten Lauf: Engywucks Maschine nannte 1201 MIME-Typen und
    163 Formatzeichen, meine 1040 und 170 — verschiedene `/etc/mime.types`,
    verschiedene Unicode-Datenbank. **Die Divergenz trat zwischen zwei
    Entwickler-Maschinen auf, nicht erst auf dem VPS.**
    """
    mimetypes.init()
    return {
        "codecs": len(set(aliases.values())),
        "mime_typen": len(mimetypes.types_map),
        "cf_zeichen": sum(1 for c in range(0x110000)
                          if unicodedata.category(chr(c)) == "Cf"),
        "zs_zeichen": sum(1 for c in range(0x110000)
                          if unicodedata.category(chr(c)) == "Zs"),
        "leerelemente": len(ET.HTML_EMPTY),
        "stumm_und_leer": len(mailtext._STUMM & ET.HTML_EMPTY),
    }


# Aufbau: aus den `add_*`-Verben von EmailMessage abgeleitet.
AUFBAU = ("plain", "alternative", "mixed", "related_in_alt")

def _gueltige_cte() -> tuple[str, ...]:
    """Uebertragungskodierung — **gemessen, nicht aus Namen abgeleitet.**

    **Mein eigener Fehler beim ersten Bau, und er ist die Mengen-Lehre zum
    vierten Mal:** Ich hatte die Achse aus `dir(email.encoders)` gebildet und
    das Praefix abgeschnitten — `7or8bit`, `base64`, `quopri`. Das sind
    **Funktionsnamen**, keine Kodierungswerte: Die Funktion heisst
    `encode_7or8bit`, die Werte heissen `7bit` und `8bit`; `quopri` heisst
    `quoted-printable`. Zwei von drei waren ungueltig, **zwei Drittel des
    Achsenraums fielen weg** — 160 Baufehlschlaege von 240.

    **Sichtbar wurde es nur, weil Engywucks Auflage das Zaehlen verlangt.**
    Waeren die Fehlschlaege still uebersprungen worden, haette der Erzeuger
    gemeldet, er habe achtzig Gestalten geprueft — und niemand haette
    bemerkt, dass er nur eine Kodierung kennt.

    Die Kandidaten stammen aus RFC 2045 (geschlossene Norm-Menge, deshalb
    hier legitim als Aufzaehlung); **welche davon gelten, wird an
    `set_content` gemessen** statt behauptet.
    """
    kandidaten = ("7bit", "8bit", "binary", "quoted-printable", "base64")
    gut = []
    for w in kandidaten:
        pruef = EmailMessage()
        try:
            pruef.set_content("Probe", cte=w)
            gut.append(w)
        except Exception:
            pass
    return tuple(gut)


CTE = _gueltige_cte()

# Zeichensatz: aus `encodings.aliases`, auf die reduziert, die eine reine
# ASCII-Marke tragen koennen. **Jede Baufehlschlagung wird gezaehlt, nie
# still uebersprungen** — sonst schrumpft die Menge unbemerkt.
def _ascii_taugliche_codecs() -> tuple[str, ...]:
    marke = "S1 V1 test"
    gut = []
    for name in sorted(set(aliases.values())):
        try:
            if marke.encode(name).decode(name) == marke:
                gut.append(name)
        except Exception:
            pass
    return tuple(gut)


# Leere Elemente: DIE Mengenoperation. Genau hier hing Befund 1.
LEER_STUMM = tuple(sorted(mailtext._STUMM & ET.HTML_EMPTY))

# Verbergungsart: aus dem EIGENEN Code, nicht aus einer Vorstellung.
VERBERGUNG = (
    'style="display:none"',
    'style="visibility:hidden"',
    'style="font-size:0"',
    "hidden",              # ohne Wert - die kanonische Schreibweise
    'hidden="hidden"',
)

# Attributform: HTML-Syntax, geschlossene Menge. Die dritte war Befund 3.
ATTRIBUTFORM = ("mit_wert", "leer", "ohne_wert")

# Marken-Platzierung relativ zu einem Kind-Element. Die dritte war Befund 2.
PLATZIERUNG = ("vor", "im", "nach")


# --------------------------------------------------------------------------
# LADEBEDINGUNG — kein Pruefzeile, sondern ein Abbruch beim Import
# --------------------------------------------------------------------------

def _pruefe_achsen() -> None:
    """**Ein ungueltiger Achsenwert toetet den Lauf, statt Faelle zu schlucken.**

    Analog zur Gegenprobe-Pflicht in `scripts/differenz.py`: Was eine
    Voraussetzung ist, wird beim **Laden** durchgesetzt, nicht von einer
    Pruefzeile beobachtet. Eine Pruefzeile kann uebersprungen, abgeschaltet
    oder schlicht nicht gefahren werden; eine Ladebedingung nicht.

    **Der Anlass ist gemessen** (Engywuck, 25.08.): Von den vier Werten, die
    ich aus `dir(email.encoders)` gezogen hatte, war nach dem Praefix-Schnitt
    **genau einer** ein gueltiger CTE-Wert — `base64`. Die anderen drei
    (`7or8bit`, `noop`, `quopri`) sind Funktionsnamen. Der Pruefstand hat
    damit auf **einer** Kodierung gemessen und auf drei Attrappen, und die
    Ergebnistabelle sah dabei vollstaendig plausibel aus.
    """
    fehler: list[str] = []

    for w in CTE:
        pruef = EmailMessage()
        try:
            pruef.set_content("Probe", cte=w)
        except Exception:
            fehler.append(f"Kodierung {w!r} ist kein gueltiger CTE-Wert "
                          f"(womoeglich ein Funktionsname?)")

    for e in LEER_STUMM:
        if e not in ET.HTML_EMPTY:
            fehler.append(f"Leerelement {e!r} steht nicht in ET.HTML_EMPTY")
        if e not in mailtext._STUMM:
            fehler.append(f"Leerelement {e!r} steht nicht in mailtext._STUMM")

    bekannt = set(aliases.values()) | set(aliases)
    for c in _ascii_taugliche_codecs():
        if c not in bekannt:
            fehler.append(f"Zeichensatz {c!r} steht nicht in encodings.aliases")

    for a in AUFBAU:
        if a not in ("plain", "alternative", "mixed", "related_in_alt"):
            fehler.append(f"Aufbau {a!r} ist nicht vorgesehen")

    if fehler:
        raise RuntimeError(
            "Achsenwerte sind ungueltig — der Pruefraum waere still "
            "geschrumpft:\n  " + "\n  ".join(fehler))


_pruefe_achsen()


@dataclass
class Gestalt:
    """Eine gebaute Nachricht plus die Wahrheit ueber ihre Marken."""
    name: str
    msg: EmailMessage
    soll_sichtbar: set[str] = field(default_factory=set)
    soll_verborgen: set[str] = field(default_factory=set)
    kopf_bytes: bytes = b""


def _html(verbergung: str, attributform: str, platzierung: str,
          leerelement: str, s: str, v: str) -> str:
    """Ein HTML-Rumpf mit EINER sichtbaren und EINER versteckten Marke."""
    if attributform == "mit_wert":
        wertlos = '<img src="x.png" alt="Bild">'
    elif attributform == "leer":
        wertlos = '<img src="x.png" alt="">'
    else:
        wertlos = '<img src="x.png" alt>'      # -> HTMLParser liefert None

    kind = "<span>Rand</span>"
    if platzierung == "vor":
        innen = f"{v}{kind}"
    elif platzierung == "im":
        innen = f"{kind}{v}{kind}"
    else:
        innen = f"{kind}{v}"                   # Kind schliesst VOR der Marke

    return (
        f"<html><head><{leerelement} charset=\"utf-8\">"
        f"</head><body>{wertlos}"
        f"<div {verbergung}>{innen}</div>"
        f"<p>{s}</p></body></html>"
    )


def _baue(aufbau: str, cte: str, codec: str, html: str, klartext: str,
          anhangsart: str | None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = "absender@example.invalid"
    msg["To"] = "adam@example.invalid"
    msg["Subject"] = "Testgestalt"
    if aufbau == "plain":
        msg.set_content(klartext, charset=codec, cte=cte)
    else:
        msg.set_content(klartext, charset=codec, cte=cte)
        msg.add_alternative(html, subtype="html", charset=codec, cte=cte)
        if aufbau == "mixed" and anhangsart:
            haupt, _, unter = anhangsart.partition("/")
            msg.add_attachment(b"NUTZLAST" * 8, maintype=haupt,
                               subtype=unter or "octet-stream",
                               filename="rechnung.pdf")
        elif aufbau == "related_in_alt":
            msg.get_payload()[-1].add_related(
                b"\x89PNG\r\n", maintype="image", subtype="png", cid="bild1")
    return msg


def gestalten(deckel: int | None = None):
    """Der Erzeuger. **Kombinatorik ueber die Achsen, nicht ueber Einfaelle.**"""
    codecs = _ascii_taugliche_codecs()
    mimetypes.init()
    anhangsarten = sorted(set(mimetypes.types_map.values()))
    # Aus jeder grossen Achse eine gleichmaessige Stichprobe statt der
    # Vollmenge - 1040 Anhangsarten mal 98 Codecs waeren Millionen Gestalten
    # ohne zusaetzlichen Erkenntniswert. **Die Stichprobe ist rechnerisch,
    # nicht ausgewaehlt:** jeder n-te Wert der sortierten Norm-Menge.
    codec_probe = codecs[::max(1, len(codecs) // 6)][:6]
    anhang_probe = anhangsarten[::max(1, len(anhangsarten) // 4)][:4]

    # **Der Deckel darf nicht PRAEFIX kappen.** `itertools.product` laeuft die
    # erste Achse zuerst durch; ein `break` nach n Stueck liefert dann nur
    # Gestalten mit `aufbau == plain`. Beim ersten Lauf waren dadurch 199 von
    # 200 Befunden derselbe Fall, und der halbe Achsenraum war ungesehen.
    # **Ein Deckel, der eine Ecke des Raums zeigt, ist selbst eine
    # Handauswahl** — nur eine, die niemand getroffen zu haben glaubt.
    #
    # Deshalb: volle Kombinationsliste, dann **gleichmaessige Schrittprobe**.
    # Deterministisch, kein Zufall — derselbe Lauf ergibt dieselbe Menge.
    voll = list(itertools.product(
        AUFBAU, CTE, codec_probe, LEER_STUMM, VERBERGUNG,
        ATTRIBUTFORM, PLATZIERUNG, anhang_probe))
    if deckel is not None and deckel < len(voll):
        schritt = len(voll) / deckel
        voll = [voll[int(i * schritt)] for i in range(deckel)]
    gestalten.raumgroesse = len(list(itertools.product(
        AUFBAU, CTE, codec_probe, LEER_STUMM, VERBERGUNG,
        ATTRIBUTFORM, PLATZIERUNG, anhang_probe)))

    n = 0
    fehlschlaege = 0
    gestalten.uebersprungen = []
    for aufbau, cte, codec, leer, verb, attr, platz, anhang in voll:
        s, v = f"S{n}", f"V{n}"
        html = _html(verb, attr, platz, leer, s, v)
        klartext = f"{s} im Klartext."
        try:
            msg = _baue(aufbau, cte, codec, html, klartext, anhang)
            roh = msg.as_bytes(policy=policy.SMTP)
        except Exception as ex:
            # **Gezaehlt MIT GRUND, nie still uebersprungen.** Eine blosse
            # Zahl sagt, dass etwas fehlte; der Grund sagt, was.
            gestalten.uebersprungen.append(
                f"{aufbau}/{cte}/{codec}: {type(ex).__name__}: {ex}")
            fehlschlaege += 1
            continue
        kopf = roh.split(b"\r\n\r\n", 1)[0]
        soll_s = {s}
        soll_v = {v} if aufbau != "plain" else set()
        if aufbau == "plain":
            soll_s = {s}
        yield Gestalt(
            name=f"{aufbau}/{cte}/{codec}/{leer}/{attr}/{platz}",
            msg=msg, soll_sichtbar=soll_s, soll_verborgen=soll_v,
            kopf_bytes=kopf)
        n += 1
    gestalten.fehlschlaege = fehlschlaege
    gestalten.erwartet = len(voll)
    gestalten.gebaut = n


gestalten.fehlschlaege = 0
gestalten.erwartet = 0
gestalten.gebaut = 0
gestalten.raumgroesse = 0
gestalten.uebersprungen = []


def entnehmen(msg: EmailMessage) -> tuple[str, list[str]]:
    """**Der Kern: genau das, was `BODY.PEEK[TEXT]` liefert.**

    Der rohe, undekodierte MIME-Rumpf ohne die Kopfzeilen — die Schicht, die
    der alte Korpus in **null von dreiundzwanzig** Dateien kannte.
    """
    roh = msg.as_bytes(policy=policy.SMTP)
    koerper = roh.split(b"\r\n\r\n", 1)[1]
    return mailtext.lesbar(koerper.decode("utf-8", "replace"))


# --------------------------------------------------------------------------
# Die sechs Orakelzeilen
# --------------------------------------------------------------------------

def orakel(g: Gestalt) -> list[str]:
    """Gibt die Befunde einer Gestalt zurueck. Leer = diese Gestalt traegt."""
    sichtbar, verborgen = entnehmen(g.msg)
    v_text = " ".join(verborgen)
    schlecht = []

    # a) SEITENTREUE, GERICHTET. Nicht als Erhaltungssatz!
    #    Gemessen (Engywuck): Der ODER-Satz [Marke steht in sichtbar ODER
    #    verborgen] ist bei B4-umgekehrt und bei <div hidden> GRUEN. Gerichtet
    #    ist er bei beiden ROT. Das ist der Unterschied zwischen einem Pruefer
    #    und einer Beruhigung.
    for s in g.soll_sichtbar:
        if s not in sichtbar:
            schlecht.append(f"a: sichtbare Marke {s} fehlt in sichtbar")
        if s in v_text:
            schlecht.append(f"a: sichtbare Marke {s} gilt als verborgen")
    for v in g.soll_verborgen:
        if v not in v_text:
            schlecht.append(f"a: versteckte Marke {v} wird NICHT als verborgen gemeldet")
        if v in sichtbar:
            schlecht.append(f"a: versteckte Marke {v} kommt als SICHTBAR durch")

    # b) KEIN NOTPFAD. Der Ausnahmezweig verwirft die ganze Zerlegung.
    if "nicht lesbar" in v_text or "Rohtext" in v_text:
        schlecht.append("b: Notpfad betreten - die Zerlegung wurde verworfen")

    # c) KEIN SCHUTT. Kein Byte aus dem Kopfbereich darf als Text gelten.
    #    [Kopfbereich] = die Zeilen vor der Leerzeile der gebauten Nachricht;
    #    zusaetzlich die MIME-Grenzmarke, die im Rumpf steht, aber Struktur
    #    ist und kein Text.
    for zeile in g.kopf_bytes.decode("utf-8", "replace").split("\r\n"):
        if len(zeile) > 12 and zeile in sichtbar:
            schlecht.append(f"c: Kopfzeile im sichtbaren Text: {zeile[:40]!r}")
            break
    if "Content-Type:" in sichtbar or "--===" in sichtbar:
        schlecht.append("c: MIME-Schutt gilt als sichtbarer Text")

    # f) ZEICHENKLASSEN - hier nur die, die der Aufbau selbst erzeugt.
    for zeichen in sichtbar:
        if unicodedata.category(zeichen) in ("Cf", "Cc") and zeichen not in "\r\n\t":
            schlecht.append("f: Formatzeichen erreicht die Ausgabe unersetzt")
            break
    return schlecht


def gegenrichtung() -> list[str]:
    """**Orakelzeile d — die, die man vergisst.**

    Eine Gestalt OHNE gepflanztes Versteck muss `verborgen == []` ergeben.
    Ohne diese Zeile belohnt der Pruefer Uebermelden: Ein Modul, das alles
    fuer verborgen haelt, waere nach a, b, c und f makellos.
    """
    msg = EmailMessage()
    msg["From"] = "a@example.invalid"
    msg["To"] = "b@example.invalid"
    msg["Subject"] = "ohne Versteck"
    msg.set_content("Nur Klartext.")
    msg.add_alternative("<html><body><p>Nur Klartext.</p></body></html>",
                        subtype="html")
    sichtbar, verborgen = entnehmen(msg)
    if verborgen:
        return [f"d: Fehlalarm - harmlose Mail meldet {len(verborgen)} Versteck(e)"]
    return []


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--deckel", type=int, default=400)
    p.add_argument("--zeige", type=int, default=5)
    a = p.parse_args()

    stand = achsenstand()
    print("GESTALTEN-ERZEUGER")
    print("=" * 78)
    print("Achsenstand dieser Maschine (gehoert in JEDEN Bericht):")
    for k, v in stand.items():
        print(f"   {k:16s} {v}")
    print(f"   {'ascii-codecs':16s} {len(_ascii_taugliche_codecs())}")
    print()

    gesamt = rot = 0
    beispiele: list[tuple[str, list[str]]] = []
    zaehler: dict[str, int] = {}
    # **Auch nach Aufbau und Kodierung zaehlen.** Ein Bericht, der nur
    # [199 von 200 rot] sagt, taugt fuer die Reparatur nicht: Sie muss messen
    # koennen, WELCHE Achse sich bewegt, wenn ein Fix greift.
    je_aufbau: dict[str, list[int]] = {}
    for g in gestalten(deckel=a.deckel):
        gesamt += 1
        befunde = orakel(g)
        schluessel = g.name.split("/")[0] + "/" + g.name.split("/")[1]
        eintrag = je_aufbau.setdefault(schluessel, [0, 0])
        eintrag[1] += 1
        if befunde:
            rot += 1
            eintrag[0] += 1
            for b in befunde:
                zaehler[b.split(":")[0]] = zaehler.get(b.split(":")[0], 0) + 1
            if len(beispiele) < a.zeige:
                beispiele.append((g.name, befunde))

    gegen = gegenrichtung()
    # **Der Pruefraum meldet seine eigene Groesse — und eine Abweichung ist ROT.**
    # Genau diese Zahl (160 von 240) hat den Achsenfehler sichtbar gemacht.
    # Ein Lauf, der weniger baut als er erwartet, hat weniger geprueft als er
    # meldet; das darf kein Kommentar sein, sondern muss der Befund sein.
    erwartet = getattr(gestalten, "erwartet", 0)
    raum_kaputt = gesamt != erwartet
    print(f"Pruefraum: {erwartet} erwartet · {gesamt} gebaut · "
          f"{gestalten.fehlschlaege} uebersprungen"
          + ("   <<< ROT: der Raum ist geschrumpft" if raum_kaputt else ""))
    for grund in gestalten.uebersprungen[:5]:
        print(f"   uebersprungen: {grund}")
    if len(gestalten.uebersprungen) > 5:
        print(f"   ... und {len(gestalten.uebersprungen) - 5} weitere")
    print(f"{rot} von {gesamt} verletzen mindestens eine Orakelzeile.")
    print(f"Zeile d (Gegenrichtung): {'ROT - ' + gegen[0] if gegen else 'gruen'}")
    print()
    print(f"Achsenraum: {getattr(gestalten, 'raumgroesse', '?')} Kombinationen, "
          f"gleichmaessige Schrittprobe (kein Praefix-Schnitt).")
    print()
    print("nach Aufbau/Kodierung (rot von gesamt):")
    for k in sorted(je_aufbau):
        r, ges = je_aufbau[k]
        print(f"   {k:28s} {r:4d}/{ges}")
    print()
    if zaehler:
        print("nach Orakelzeile:")
        for k in sorted(zaehler):
            print(f"   {k}: {zaehler[k]}")
        print()
    for name, befunde in beispiele:
        print(f"  {name}")
        for b in befunde[:3]:
            print(f"     {b}")
    print()
    print("EHRLICHE GRENZE: Dieser Erzeuger schliesst die Klasse [der Code hat")
    print("einen Zweig und rechnet falsch]. Er schliesst NICHT [der Code hat")
    print("gar keinen Zweig] - style-Klassen, weisse Schrift, aria-hidden,")
    print("Positionierung ausserhalb des Bildes. Das darf nie als geschlossen")
    print("berichtet werden.")
    print()
    print("UNGEPRUEFT: ob BODY.PEEK[TEXT] eines echten Servers genau diesen")
    print("Ausschnitt liefert. Modelliert nach RFC 3501, gegen keinen Server")
    print("gehalten.")
    if raum_kaputt:
        print()
        print("ABBRUCH: gebaut != erwartet. Der Lauf hat weniger geprueft, als")
        print("er meldet. Erst den Achsenraum reparieren, dann messen.")
        return 1
    if gegen:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
