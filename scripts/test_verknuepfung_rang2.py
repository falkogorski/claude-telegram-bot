#!/usr/bin/env python3
"""Aus einem fremden Betreff wird keine anklickbare Verknuepfung.

**Engywucks Rang 2 der Erkennungsseite, Punkt 4.** Die Zusage „③ Keine
anklickbare Adresse" stand seit dem ersten Tag im Modul und hing an einer
falschen Annahme: dass ohne `parse_mode` alles Text bleibe. Das gilt fuer
**unsere** Auszeichnung — der Telegram-Server setzt in Klartext von sich aus
Entitaeten der Typen `url`, `email` und `phone_number`.

**Der Schaden ist nicht die Adresse, sondern die Verknuepfung:** Ein Betreff
`Rechnung http://boese.tld/x` erzeugt einen Link in einer Nachricht, die vom
Bot kommt — er sieht damit vertrauenswuerdiger aus als in der Mail selbst.

Gemessen wird beides, und die zweite Haelfte ist die wichtigere:

    ① nichts Verlinkbares kommt durch
    ② HARMLOSER Wortlaut bleibt unangetastet

Ohne ② waere die Zeile mit `return ""` zu erfuellen — und ein Filter, der
Wortlaut frisst, ist schlimmer als ein Link, den Adam als Link sieht.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = Path(tempfile.mkdtemp(prefix="verknuepfung-"))
os.environ["FREIGABE_DIR"] = str(_TMP / "freigaben")
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"

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
# ① Nichts Verlinkbares kommt durch
# --------------------------------------------------------------------------
print("\nAus Fremdtext wird nichts Anklickbares")

VERLINKBAR = [
    "Rechnung http://boese.tld/x jetzt zahlen",
    "https://boese.tld/pfad?a=1",
    "Sieh www.boese.tld an",
    "Schreib an chef@boese.tld",
    "javascript://boese.tld/x",
    "FTP://boese.tld/datei",
    "HTTPS://GROSS.TLD",
]
for roh in VERLINKBAR:
    n = ek._neutral(roh)
    zeile(f"kein Schema mehr in {roh[:34]!r}",
          "://" not in n and "www." not in n.lower(), gemessen=n)
    zeile(f"kein Klammeraffe mehr in {roh[:34]!r}", "@" not in n, gemessen=n)

# Und die Kennzeichnung: Wo etwas entfernt wurde, steht das da.
n = ek._neutral("Rechnung http://boese.tld/x jetzt zahlen")
zeile("die Entfernung ist sichtbar vermerkt", "entfernt" in n, gemessen=n)
zeile("der uebrige Wortlaut bleibt erhalten",
      "Rechnung" in n and "jetzt zahlen" in n, gemessen=n)

# Die Absenderadresse bleibt LESBAR — nur nicht mehr anklickbar.
n = ek._neutral("chef@boese.tld")
zeile("die Adresse bleibt lesbar", "chef" in n and "boese.tld" in n,
      gemessen=n)

# --------------------------------------------------------------------------
# ② Harmloser Wortlaut bleibt unangetastet
# --------------------------------------------------------------------------
print("\nHarmloser Wortlaut wird nicht angefasst")

HARMLOS = [
    "Rechnung Nr. 42",
    "z.B. die Lieferung vom 3.9.",
    "Sehr geehrte Herren.Ihre Bestellung ist unterwegs",
    "Angebot 2.0 fuer Frau Dr. Meier",
    "Termin am 1.10. um 9.30 Uhr",
]
for roh in HARMLOS:
    zeile(f"unveraendert: {roh[:38]!r}", ek._neutral(roh) == roh,
          gemessen=ek._neutral(roh))

# --------------------------------------------------------------------------
# ③ Die Restluecke ist BENANNT, nicht behauptet
# --------------------------------------------------------------------------
print("\nDie Restluecke steht im Code, nicht nur im Bericht")

quelle = Path(ek.__file__).read_text()
# **Diese eine Zeile liest Quelltext und ist damit umgehbar — sie ist KEIN
# Schutz, sondern haelt fest, dass der Vermerk nicht still verschwindet.**
# Ausdruecklich benannt, damit sie niemand als Sicherung zaehlt.
zeile("die schemalose Luecke ist im Modul vermerkt (Doku-Zeile, kein Schutz)",
      "Restlücke" in quelle and "boese.tld" in quelle)
# Und ehrlich gemessen: sie kommt tatsaechlich durch. Diese Zeile haelt den
# Stand fest — schlaegt sie eines Tages an, ist die Luecke geschlossen und
# der Vermerk oben ueberholt.
zeile("schemalose Adresse kommt (noch) durch — Stand festgehalten",
      "boese.tld" in ek._neutral("Sieh boese.tld an"),
      gemessen=ek._neutral("Sieh boese.tld an"))

# --------------------------------------------------------------------------
# ④ Der ganze Weg: die Uebersicht traegt es auch
# --------------------------------------------------------------------------
print("\nDie fertige Uebersicht traegt keine Verknuepfung")

text = ek.als_text("geschaeftlich", [{
    "kennung": "1001",
    "von": "Chef <chef@boese.tld>",
    "betreff": "Jetzt zahlen: https://boese.tld/kasse",
    "datum": "Sat, 29 Aug 2026 20:00:00 +0200",
    "anhaenge": [],
}])
zeile("in der fertigen Uebersicht steht kein Schema", "://" not in text,
      gemessen=text)
zeile("in der fertigen Uebersicht steht kein Klammeraffe",
      "@" not in text, gemessen=text)
zeile("der Rangvermerk der Uebersicht steht weiterhin zuerst",
      text.index("keine Anweisung") < text.index("Jetzt zahlen"))

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {fehler}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen gruen — Verknuepfungen (Rang 2, Punkt 4).")
