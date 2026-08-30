#!/usr/bin/env python3
"""Der Zustandspruefer gegen Karteileichen — ausgefuehrt, nicht gelesen.

**Claudias Bauauftrag vom 28.08., Auftrag 1.** Gemessen wird an einem
Wegwerf-Ordner, damit die Zeilen unabhaengig davon gelten, was gerade wirklich
im Log-Repo liegt.

**Die Daempfung ist der Gegenstand, nicht der Fund.** Ein Pruefer, der taeglich
dieselben fuenfundvierzig Namen meldet, wird binnen zwei Tagen ueberlesen — und
mit ihm die eine Zeile, die spaeter zaehlt. Deshalb steht hier fuer jede
Fundart auch die Gegenrichtung: *er schweigt, wenn nichts neu ist.*
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

_TMP = Path(tempfile.mkdtemp(prefix="ausarb-"))
os.environ["AUSARBEITUNGEN_DIR"] = str(_TMP / "papiere")
os.environ["AUSARBEITUNGEN_STAND"] = str(_TMP / "stand.json")
os.environ["AUSARBEITUNGEN_ALTER_TAGE"] = "21"
(_TMP / "papiere").mkdir(parents=True, exist_ok=True)

import ausarbeitungen_pruefen as ap                            # noqa: E402

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


def papier(name: str, kopf: str | None = None, alter_tage: float = 0) -> Path:
    p = _TMP / "papiere" / name
    text = "# Ein Papier\n\n"
    if kopf is not None:
        text = f"# Ein Papier\n\nSTAND: {kopf}\n\nInhalt\n"
    p.write_text(text, encoding="utf-8")
    if alter_tage:
        alt = time.time() - alter_tage * 86400
        os.utime(p, (alt, alt))
    return p


def stand_loeschen() -> None:
    try:
        Path(os.environ["AUSARBEITUNGEN_STAND"]).unlink()
    except OSError:
        pass


print("\n① Was gefunden wird")

papier("ohne-kopf.md")
papier("mit-kopf.md", "gültig")
papier("alt.md", "gültig", alter_tage=30)
papier("ueberholt-und-alt.md", "überholt durch x.md", alter_tage=99)

b = ap.pruefen()
zeile("ein Papier ohne Zustandskopf wird gefunden",
      b["ohne_kopf"] == ["ohne-kopf.md"], gemessen=str(b["ohne_kopf"]))
zeile("ein altes [gültig] wird zur Sichtung vorgelegt",
      b["zu_alt"] == ["alt.md"], gemessen=str(b["zu_alt"]))
# **Die Gegenrichtung, und sie ist der Grund, warum das Altersmass nur fuer
# „gueltig" gilt:** Ein Papier, das ausdruecklich als ueberholt vermerkt ist,
# ist bereits eingeordnet. Es taeglich vorzulegen waere Rauschen.
zeile("ein als überholt vermerktes Papier wird NICHT vorgelegt, auch wenn alt",
      "ueberholt-und-alt.md" not in b["zu_alt"], gemessen=str(b["zu_alt"]))
zeile("ein frisches [gültig] wird nicht vorgelegt",
      "mit-kopf.md" not in b["zu_alt"] and "mit-kopf.md" not in b["ohne_kopf"])

# **Der Kopf steht OBEN, sonst ist er keiner.** Am lebenden Fall gefunden: Im
# Bauauftrag selbst steht ein BEISPIEL-Block mit drei STAND-Zeilen, in Zeile 61.
# Ein Pruefer, der die ganze Datei durchsucht, haette ihn als Zustandskopf
# gezaehlt — und das Papier faelschlich als gepflegt gefuehrt.
tief = _TMP / "papiere" / "beispiel-tief.md"
tief.write_text("# Titel\n" + "\n" * 30 + "STAND: gültig\n", encoding="utf-8")
b = ap.pruefen()
zeile("ein STAND-Vorkommen tief im Text zaehlt NICHT als Kopf",
      "beispiel-tief.md" in b["ohne_kopf"], gemessen=str(b["ohne_kopf"]))


print("\n② Die Daempfung — der eigentliche Gegenstand")

stand_loeschen()
erste = ap.meldung()
zeile("der erste Lauf nennt die Grundlinie als ZAHL",
      "eingerichtet" in erste and "Zugaenge" in erste, gemessen=erste)
zeile("und er nennt KEINE Namensliste",
      "ohne-kopf.md" not in erste, gemessen=erste[:120])

zweite = ap.meldung()
zeile("der zweite Lauf schweigt, wenn nichts neu ist", zweite == "",
      gemessen=repr(zweite))

papier("frisch-dazu.md")
dritte = ap.meldung()
zeile("ein Zugang wird gemeldet", "frisch-dazu.md" in dritte, gemessen=dritte)
zeile("und der Bestand wird NICHT wiederholt",
      "ohne-kopf.md" not in dritte, gemessen=dritte)

vierte = ap.meldung()
zeile("danach schweigt er wieder", vierte == "", gemessen=repr(vierte))

# Und der Zustand wird auch dann fortgeschrieben, wenn nichts gemeldet wird —
# sonst waere ein Papier, das seinen Kopf verliert, nicht mehr „neu".
papier("frisch-dazu.md", "gültig")          # bekommt einen Kopf
ap.meldung()
papier("frisch-dazu.md")                    # und verliert ihn wieder
zeile("ein wieder verlorener Kopf gilt erneut als Zugang",
      "frisch-dazu.md" in ap.meldung())


print("\n③ Was der Pruefer NICHT kann — benannt statt verschwiegen")

# Claudias eigener Vorfall: Das Papier war EINEN TAG alt und trug einen
# ueberholten Satz. Dieser Pruefer misst Alter und Anwesenheit, nicht Inhalt.
stand_loeschen()
papier("frisch-aber-falsch.md", "gültig", alter_tage=1)
ap.meldung()
b = ap.pruefen()
zeile("ein frisches Papier mit ueberholtem INHALT wird nicht gefunden",
      "frisch-aber-falsch.md" not in b["zu_alt"]
      and "frisch-aber-falsch.md" not in b["ohne_kopf"],
      gemessen="das ist kein Mangel, sondern die Grenze — Auftrag 2 traegt sie")

# Und ein unerreichbarer Ordner meldet NICHTS GEMESSEN, statt zu schweigen —
# dieselbe Klasse wie A1.
os.environ["AUSARBEITUNGEN_DIR"] = str(_TMP / "gibtesnicht")
import importlib                                               # noqa: E402
importlib.reload(ap)
zeile("ein unerreichbarer Ordner meldet, dass NICHTS gemessen wurde",
      "NICHTS" in ap.meldung().upper(), gemessen=ap.meldung()[:110])
os.environ["AUSARBEITUNGEN_DIR"] = str(_TMP / "papiere")
importlib.reload(ap)


print("\n④ Der Weg zur Kontrolle — nicht zu Adam")

buch = _TMP / "auftragsbuch"
os.environ["AUFTRAGSBUCH_DIR"] = str(buch)
stand_loeschen()
e = subprocess.run([str(ROOT / ".venv" / "bin" / "python"),
                    str(ROOT / "scripts" / "ausarbeitungen_pruefen.py"),
                    "--ins-auftragsbuch"],
                   capture_output=True, text=True, env=dict(os.environ),
                   cwd=str(ROOT))
zeile("der Befund wird ins Auftragsbuch gelegt", e.stdout.strip() == "GELEGT",
      gemessen=f"{e.stdout.strip()!r} {e.stderr.strip()[:80]}")
# **Der Zustand wird ZURUECKGESETZT, sonst misst die naechste Zeile die
# Daempfung statt des Dublettenschutzes.** Genau so war sie zuerst gebaut: Der
# zweite Lauf meldete ohnehin nichts Neues und kam gar nicht bis zum
# Auftragsbuch — die Zeile war gruen, ohne den Schutz je erreicht zu haben.
# Gefunden durch die Entkernung, die nichts rot machte.
stand_loeschen()
e2 = subprocess.run([str(ROOT / ".venv" / "bin" / "python"),
                     str(ROOT / "scripts" / "ausarbeitungen_pruefen.py"),
                     "--ins-auftragsbuch"],
                    capture_output=True, text=True, env=dict(os.environ),
                    cwd=str(ROOT))
# Ein zweiter Lauf darf keinen zweiten Eintrag erzeugen — ein Stapel
# gleichlautender Eintraege wird als Ganzes ignoriert, und dann haette der
# Pruefer sich selbst abgeschaltet.
zeile("ein zweiter Lauf legt keinen zweiten Eintrag",
      e2.stdout.strip() == "SCHON-DA", gemessen=repr(e2.stdout.strip()))
eintraege = list((buch / "eingang").glob("*.json")) if (buch / "eingang").is_dir() else []
zeile("und im Auftragsbuch liegt genau EIN Eintrag",
      len(eintraege) == 1, gemessen=f"{len(eintraege)} Eintraege")

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {fehler}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen gruen — Zustandspruefer der Ausarbeitungen.")
