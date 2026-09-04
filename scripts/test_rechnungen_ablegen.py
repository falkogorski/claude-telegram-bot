#!/usr/bin/env python3
# <!-- ROLLE: test-rechnungen-ablegen -->
"""Verhaltenstest des Ablegewegs — **das Skript laeuft echt.**

**Engywucks Befunde 1, 2 und 3 vom 04.09.2026.** Alle drei betreffen dasselbe
Skript, deshalb ein Pruefer und kein dritter Waechter (Konvergenz-Bremse).

Bisher gab es fuer `scripts/mac/rechnungen_ablegen.sh` **gar keinen** Pruefer;
die drei Gegenproben vom 03.09. waren Handmessungen und pruefen alle den
**ersten** Lauf. Genau dort lag Befund 1: Der zweite Lauf meldete dasselbe
noch einmal.

## Wie gemessen wird

Eine `ssh`-Attrappe im PATH verhaelt sich wie echtes `ssh`: Sie wirft die
`-o`-Optionen und den Hostnamen weg und uebergibt den Rest an `sh -c` — genau
das tut die echte, und deshalb traegt die Messung. Zwei Folgen:

* `rsync` kann sie als Transport benutzen. Der Zug Server → Mac laeuft damit
  **echt**, samt `--remove-source-files`.
* Der Fernaufruf erreicht das **echte** `postfach_ablegen.py`; nur der
  Server-Pfad wird auf das Repo umgebogen. Der Weg des Textes ist also
  vollstaendig gemessen, nicht nachgestellt.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if not shutil.which("rsync"):
    print("⏭️ rsync fehlt auf dieser Maschine — der Ablegeweg wurde NICHT "
          "GEMESSEN (kein Fehlschlag, aber auch kein Bestehen)")
    sys.exit(77)

_TMP = Path(tempfile.mkdtemp(prefix="ablegen-"))
FERN = _TMP / "server" / "ausgang"        # der Durchgangsordner auf dem VPS
LOKAL = _TMP / "uebergabe"                # die Mac-Platte
ZIEL = _TMP / "icloud"                    # Adams Kundenzweig
POSTFACH = _TMP / "postfach"
BIN = _TMP / "bin"
for d in (FERN, LOKAL, ZIEL, POSTFACH, BIN):
    d.mkdir(parents=True, exist_ok=True)

# ── Die ssh-Attrappe ────────────────────────────────────────────────────────
_SSH = f"""#!/bin/bash
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    -o) shift 2 ;;
    -*) shift ;;
    *)  break ;;
  esac
done
shift                     # der Hostname
[ $# -eq 0 ] && exit 0    # `ssh host true` ohne Befehl kommt hier nie an
befehl="$*"
befehl="${{befehl//\\/home\\/claudebot\\/claude-telegram-bot/{ROOT}}}"
printf '%s\\n' "$befehl" >> "{_TMP}/ssh-aufrufe.log"
exec sh -c "$befehl"
"""
(BIN / "ssh").write_text(_SSH, encoding="utf-8")
(BIN / "ssh").chmod((BIN / "ssh").stat().st_mode | stat.S_IEXEC)

fails: list[str] = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:  # noqa: BLE001
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _lauf() -> str:
    """Das echte Skript, mit umgebogenen Pfaden. Gibt das Protokoll zurueck."""
    log = _TMP / "lauf.log"
    umgebung = dict(os.environ)
    umgebung.update({
        "PATH": f"{BIN}:{os.environ.get('PATH', '')}",
        "HOME": str(_TMP),
        "RECHNUNGEN_SSH_HOST": "attrappe",
        "RECHNUNGEN_FERN": f"{FERN}/",
        "RECHNUNGEN_LOKAL": str(LOKAL),
        "RECHNUNGEN_ICLOUD": str(ZIEL),
        "RECHNUNGEN_LOG": str(log),
        "RECHNUNGEN_CHAT": "304455165",
        "POSTFACH_DIR": str(POSTFACH),
    })
    e = subprocess.run(["bash", str(ROOT / "scripts" / "mac" / "rechnungen_ablegen.sh")],
                       env=umgebung, capture_output=True, text=True)
    if e.returncode not in (0, 78):
        raise RuntimeError(f"Skript endete mit {e.returncode}: "
                           f"{(e.stderr or e.stdout or '').strip()[-300:]}")
    return log.read_text(encoding="utf-8") if log.exists() else ""


def _auftraege() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((POSTFACH / "outbox").glob("*.json"))]


def _leeren() -> None:
    for baum in (FERN, LOKAL, ZIEL, POSTFACH):
        shutil.rmtree(baum, ignore_errors=True)
        baum.mkdir(parents=True, exist_ok=True)
    (_TMP / "lauf.log").unlink(missing_ok=True)


def _rechnung(unter: str, name: str = "Rechnung 018-26.pdf") -> Path:
    p = FERN / unter / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF-1.4 test")
    return p


# ── Die Pruefungen ──────────────────────────────────────────────────────────
def _der_zweite_lauf_ist_still():
    """**Befund 1.** Gezaehlt wird das Uebertragene, nicht der Bestand.

    Die Gegenprobe, die den drei Handmessungen vom 03.09. fehlte: Sie pruefen
    alle den ersten Lauf. Der Fehler zeigte sich erst im zweiten.
    """
    _leeren()
    _rechnung("LiveSetup/Volvo/Norderney")
    erstes = _lauf()
    assert "1 Datei(en) in ihre Kundenordner gelegt" in erstes, \
        f"der erste Lauf hat nichts gemeldet:\n{erstes}"
    assert len(_auftraege()) == 1, "der erste Lauf hat Adam nicht benachrichtigt"

    (_TMP / "lauf.log").unlink()
    zweites = _lauf()
    assert "in ihre Kundenordner gelegt" not in zweites, \
        f"der zweite Lauf meldet dasselbe noch einmal:\n{zweites}"
    assert len(_auftraege()) == 1, \
        "der zweite Lauf hat Adam ein zweites Mal benachrichtigt, ohne dass " \
        "etwas geschehen ist"


def _eine_echte_neue_datei_wird_sehr_wohl_gemeldet():
    """**Die Gegenrichtung, und ohne sie waere der Fix gefaehrlich:** Ein
    Skript, das nie wieder meldet, meldet auch die echte Ablage nicht."""
    _rechnung("Goldhut", "Rechnung 019-26.pdf")
    drittes = _lauf()
    assert "1 Datei(en) in ihre Kundenordner gelegt" in drittes, \
        f"eine echte neue Rechnung wurde nicht gemeldet:\n{drittes}"
    assert len(_auftraege()) == 2, "die neue Rechnung erreichte Adam nicht"


def _der_ausgang_wird_geraeumt():
    """**Befund 2.** `ausgang/` ist ein Durchgangsordner.

    Bliebe die Datei dort liegen, meldete Zeile 9j des Tageschecks sie
    taeglich, fuer immer, mit wachsender Zahl — und keine Mac-Sitzung koennte
    die Meldung je zum Verschwinden bringen.
    """
    _leeren()
    quelle = _rechnung("DEKO-Service/Volvo")
    _lauf()
    assert not quelle.exists(), \
        "die Datei liegt noch im Serverausgang — 9j meldet sie ab morgen taeglich"
    uebrig = [p for p in LOKAL.rglob("*") if p.is_file()]
    assert uebrig, "der Ausgang wurde geraeumt, ohne dass etwas ankam — Datenverlust"
    angekommen = [p for p in ZIEL.rglob("*") if p.is_file()]
    assert angekommen, "nichts in iCloud angekommen"


def _apostroph_im_ordnernamen_kommt_vollstaendig_an():
    """**Befund 3.** Der Text geht ueber stdin, nicht durch die Shell.

    Gemessen wird am **angekommenen Auftrag**, nicht am Aufruf: Genau das ist
    der Unterschied zwischen einer Pruefung, die Schreibweise misst, und
    einer, die Wirkung misst.
    """
    _leeren()
    _rechnung("L'Osteria/Bar")
    protokoll = _lauf()
    auftraege = _auftraege()
    assert len(auftraege) == 1, \
        f"die Nachricht kam nicht an — genau der heutige Ausfall:\n{protokoll}"
    text = auftraege[0].get("text", "")
    assert "L'Osteria/Bar" in text, \
        f"der Ordnername kam zerrissen an: {text!r}"
    assert text.startswith("📁 1 Rechnung(en)"), \
        f"der Text ist beschaedigt: {text!r}"


def _ein_boesartiger_ordnername_fuehrt_keinen_befehl_aus():
    """**Die scharfe Seite von Befund 3.** `x'; <befehl>; echo '` haette als
    `claudebot` auf dem VPS gelaufen."""
    _leeren()
    beute = _TMP / "beute.txt"
    beute.unlink(missing_ok=True)
    _rechnung(f"x'; touch {beute}; echo '")
    _lauf()
    assert not beute.exists(), \
        "ein Ordnername hat einen Befehl auf der Gegenseite ausgefuehrt"
    auftraege = _auftraege()
    assert len(auftraege) == 1 and "touch" in auftraege[0].get("text", ""), \
        "der Name kam nicht als reiner Text an"


check("der zweite Lauf ist still (Befund 1)", _der_zweite_lauf_ist_still)
check("eine echte neue Datei wird sehr wohl gemeldet (Gegenrichtung)",
      _eine_echte_neue_datei_wird_sehr_wohl_gemeldet)
check("der Serverausgang wird geraeumt (Befund 2)", _der_ausgang_wird_geraeumt)
check("Apostroph im Ordnernamen kommt vollstaendig an (Befund 3)",
      _apostroph_im_ordnernamen_kommt_vollstaendig_an)
check("ein boesartiger Ordnername fuehrt keinen Befehl aus (Befund 3)",
      _ein_boesartiger_ordnername_fuehrt_keinen_befehl_aus)

shutil.rmtree(_TMP, ignore_errors=True)

print()
if fails:
    print(f"❌ {len(fails)} Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Ablegeweg-Tests bestanden.")
