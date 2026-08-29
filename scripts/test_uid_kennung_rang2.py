#!/usr/bin/env python3
"""Eine Nachricht wird ueber ihre UID geholt — nicht ueber ihre Position.

**Engywucks Rang 2 der Erkennungsseite, Punkt 2.** Der Knopfweg holte den
Posteingang **zweimal** (einmal fuer den Text, einmal fuer die Kennungen) und
adressierte die Nachrichten ueber **Sequenznummern**. Beides zusammen ergibt
einen Fehler, der wie ein Ergebnis aussieht:

    Uebersicht 20:14   1. Rechnung   2. Termin   3. Angebot
    (eine aeltere Mail verschwindet — geloescht am Telefon)
    Knopf 3 gedrueckt  -> holt seit dem Verschwinden eine ANDERE Nachricht

**Die Art des Fehlers ist der Punkt, nicht seine Haeufigkeit.** Mit der
Position bekommt Adam stillschweigend die falsche Mail; mit der UID bekommt er
„die gibt es nicht mehr". Das eine sieht aus wie Ruhe, das andere ist eine
Auskunft.

Gemessen wird **ausgefuehrt**: Die Attrappe beantwortet ausschliesslich
`uid()`. Wer noch `search()` oder `fetch()` ruft — also weiter ueber Positionen
geht —, faellt hier hin, statt gruen zu bleiben. Kein Blick in den Quelltext.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Hermetik: die Umgebung wird ERZWUNGEN, nicht ergaenzt.
_TMP = Path(tempfile.mkdtemp(prefix="uid-rang2-"))
os.environ["FREIGABE_DIR"] = str(_TMP / "freigaben")
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
for _s, _w in {
    "MAIL_GESCHAEFTLICH_ADRESSE": "adam@example.org",
    "MAIL_GESCHAEFTLICH_BENUTZER": "adam@example.org",
    "MAIL_GESCHAEFTLICH_KENNWORT": "geheim-nur-fuer-den-test",
    "MAIL_GESCHAEFTLICH_IMAP": "imap.example.org:993",
    "MAIL_GESCHAEFTLICH_SMTP": "smtp.example.org:465",
}.items():
    os.environ[_s] = _w

import imaplib                                                 # noqa: E402
import email_kanal as ek                                       # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f"  [{gemessen}]" if gemessen else ""))
        fehler.append(name)


# --------------------------------------------------------------------------
# Die Attrappe. Sie kann NUR uid() — bewusst.
# --------------------------------------------------------------------------

class NurUID:
    """Ein Postfach, das ausschliesslich UID-Befehle beantwortet.

    `search()` und `fetch()` sind nicht etwa weggelassen, sondern **legen den
    Pruefer um** — mit einer Meldung, die sagt, was falsch war. Eine Attrappe,
    die beide Wege bedient, verdeckt genau den Unterschied, um den es geht.
    """

    #: UIDs, wie der Server sie liefert — bewusst NICHT 1,2,3, damit eine
    #: Position sich niemals zufaellig wie eine UID liest.
    UIDS = [b"1001", b"1002", b"1003"]

    def __init__(self):
        self.aufrufe: list[tuple] = []
        self.sitzungen = 0
        self.verschwunden: set[str] = set()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def login(self, benutzer, kennwort):
        self.sitzungen += 1          # eine Anmeldung = ein Abruf am Server
        self.aufrufe.append(("login", benutzer))
        return ("OK", [b""])

    def select(self, fach, readonly=False):
        self.aufrufe.append(("select", fach, readonly))
        return ("OK", [b"3"])

    def search(self, *a):
        raise AssertionError(
            "SEARCH ohne UID — die Liste haengt wieder an Positionen")

    def fetch(self, *a):
        raise AssertionError(
            "FETCH ohne UID — eine Nachricht wird ueber ihre Position geholt")

    def uid(self, befehl, *args):
        klar = tuple(a.decode() if isinstance(a, bytes) else a
                     for a in args if a is not None)
        self.aufrufe.append(("uid", befehl.upper()) + klar)
        if befehl.upper() == "SEARCH":
            return ("OK", [b" ".join(self.UIDS)])
        gefragt = klar[0] if klar else ""
        spez = klar[1] if len(klar) > 1 else ""
        if gefragt in self.verschwunden:
            # So antwortet ein Server auf eine UID, die es nicht mehr gibt:
            # OK, aber ohne Daten. KEIN Fehler — das ist der Kern des Falls.
            return ("OK", [None])
        if "BODYSTRUCTURE" in spez.upper():
            return ("OK", [b'1 (BODYSTRUCTURE ("text" "plain" ("charset" '
                           b'"utf-8") NIL NIL "7bit" 12 1))'])
        if "TEXT" in spez.upper() and "HEADER" not in spez.upper():
            return ("OK", [(b"1 (BODY[TEXT] {9}",
                            f"Text zu {gefragt}".encode()), b")"])
        kopf = (f"From: absender-{gefragt}@example.org\r\n"
                f"Subject: Nachricht {gefragt}\r\n"
                "Date: Sat, 29 Aug 2026 20:00:00 +0200\r\n").encode()
        return ("OK", [(b"1 (BODY[HEADER]", kopf), b")"])


def mit_postfach(postfach, fn):
    echt = imaplib.IMAP4_SSL
    imaplib.IMAP4_SSL = lambda *a, **k: postfach
    try:
        return fn()
    finally:
        imaplib.IMAP4_SSL = echt


# --------------------------------------------------------------------------
# 1. Der Abruf geht ueber UID — und die Kennung IST die UID
# --------------------------------------------------------------------------
print("\nDie Uebersicht adressiert ueber UIDs")

p = NurUID()
nachrichten = mit_postfach(p, lambda: ek.posteingang("geschaeftlich", 3))

zeile("der Abruf hat das Postfach ueberhaupt geoeffnet", bool(p.aufrufe))
zeile("gesucht wird mit UID SEARCH",
      any(a[:2] == ("uid", "SEARCH") for a in p.aufrufe),
      gemessen=str(p.aufrufe[:3]))
zeile("geholt wird mit UID FETCH",
      any(a[:2] == ("uid", "FETCH") for a in p.aufrufe))

kennungen = [n["kennung"] for n in nachrichten]
zeile("die Kennung ist die UID vom Server, nicht die Position",
      kennungen == ["1003", "1002", "1001"], gemessen=str(kennungen))

# Und die Gegenrichtung, damit die Zeile nicht ins Leere misst: Eine Position
# waere 1,2,3 — genau das darf hier NICHT stehen.
zeile("keine Kennung sieht aus wie eine Zaehlposition",
      not ({"1", "2", "3"} & set(kennungen)), gemessen=str(kennungen))

zeile("der Abruf bleibt nur lesend",
      all(a[2] is True for a in p.aufrufe if a[0] == "select"))

# --------------------------------------------------------------------------
# 2. Eine verschwundene Nachricht wird BENANNT, nicht ersetzt
# --------------------------------------------------------------------------
print("\nEine verschwundene Nachricht liefert keine andere")

p = NurUID()
p.verschwunden = {"1002"}
try:
    ergebnis = mit_postfach(
        p, lambda: ek.nachricht_text("geschaeftlich", "1002"))
    zeile("die verschwundene Nachricht wird benannt", False,
          gemessen=f"lieferte still ein Ergebnis: {ergebnis!r:.80}")
except ek.Abgewiesen as e:
    text = str(e)
    zeile("die verschwundene Nachricht wird benannt", True)
    zeile("der Grund steht im Text, nicht nur ein Fehlschlag",
          "nicht mehr" in text and "1002" in text, gemessen=text)
except Exception as e:
    zeile("die verschwundene Nachricht wird benannt", False,
          gemessen=f"{type(e).__name__}: {e}")
    zeile("der Grund steht im Text, nicht nur ein Fehlschlag", False)

# Die Gegenrichtung: eine vorhandene UID liefert GENAU diese Nachricht.
p = NurUID()
felder, text, _verborgen = mit_postfach(
    p, lambda: ek.nachricht_text("geschaeftlich", "1003"))
zeile("eine vorhandene UID liefert genau diese Nachricht",
      "1003" in felder.get("subject", ""), gemessen=str(felder))
gefragt = [a[2] for a in p.aufrufe if a[:2] == ("uid", "FETCH")]
zeile("gefragt wurde nach der uebergebenen UID, nach keiner anderen",
      gefragt and set(gefragt) == {"1003"}, gemessen=str(gefragt))

# --------------------------------------------------------------------------
# 3. Die Schranke passt zur UID — zehn Stellen, nicht neun
# --------------------------------------------------------------------------
print("\nDie Kennungs-Schranke passt zum Wertebereich einer UID")

p = NurUID()
p.UIDS = [b"4294967295"]                      # groesste 32-Bit-UID
try:
    mit_postfach(p, lambda: ek.nachricht_text("geschaeftlich", "4294967295"))
    zeile("die groesste moegliche UID wird angenommen", True)
except ek.Abgewiesen as e:
    zeile("die groesste moegliche UID wird angenommen", False, gemessen=str(e))

for boese in ("1 OR 1", "1*", "", "12345678901", "../1", "1\r\nLOGOUT"):
    try:
        mit_postfach(NurUID(),
                     lambda: ek.nachricht_text("geschaeftlich", boese))
        zeile(f"unbrauchbare Kennung {boese!r} wird abgewiesen", False)
    except ek.Abgewiesen:
        zeile(f"unbrauchbare Kennung {boese!r} wird abgewiesen", True)

# --------------------------------------------------------------------------
# 4. Liste und Knoepfe stammen aus EINEM Abruf
# --------------------------------------------------------------------------
print("\nListe und Knoepfe stammen aus einem einzigen Abruf")

import bot                                                     # noqa: E402


class FakeBot:
    def __init__(self):
        self.gesendet = []


class FakeNachricht:
    chat_id = 99


class FakeQuery:
    def __init__(self, daten):
        self.data = daten
        self.message = FakeNachricht()
        self._bot = FakeBot()
        self.geantwortet = False

    async def answer(self, *a, **k):
        self.geantwortet = True

    def get_bot(self):
        return self._bot


class FakeUpdate:
    def __init__(self, daten):
        self.callback_query = FakeQuery(daten)


gesendet: list[dict] = []


async def _fang(bot_, ziel, text, **k):
    gesendet.append({"text": text, "markup": k.get("reply_markup")})


p = NurUID()
echt_auth, echt_send = bot.authorized, bot.send_chunked
bot.authorized = lambda u: True
bot.send_chunked = _fang
upd = FakeUpdate("mail:geschaeftlich")
try:
    mit_postfach(p, lambda: asyncio.run(bot.on_mail_knopf(upd, None)))
finally:
    bot.authorized, bot.send_chunked = echt_auth, echt_send

zeile("der Knopfweg hat ueberhaupt etwas gesendet", bool(gesendet))
zeile("das Postfach wurde GENAU EINMAL geoeffnet", p.sitzungen == 1,
      gemessen=f"{p.sitzungen} Anmeldungen")

# Und das Entscheidende: Die Kennung im Knopf ist dieselbe wie in der Zeile.
markup = gesendet[-1]["markup"] if gesendet else None
knopfdaten = [b.callback_data for reihe in (markup.inline_keyboard if markup
                                            else []) for b in reihe]
zeile("die Knoepfe tragen die UIDs aus derselben Antwort",
      knopfdaten == ["mail:geschaeftlich:1003",
                     "mail:geschaeftlich:1002",
                     "mail:geschaeftlich:1001"],
      gemessen=str(knopfdaten))
zeile("die Liste im Text nennt dieselben Nachrichten",
      all(f"Nachricht {u}" in gesendet[-1]["text"]
          for u in ("1001", "1002", "1003")),
      gemessen=gesendet[-1]["text"][:120] if gesendet else "")

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {fehler}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen gruen — UID-Kennung (Rang 2, Punkt 2).")
