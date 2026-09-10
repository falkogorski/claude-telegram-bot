#!/usr/bin/env python3
# <!-- ROLLE: konzept-pdf -->
"""Markdown zu PDF — das benannte Skript fuer Claudias Papiere (M-4).

**Adams Entscheid vom 09.09.2026:** `pandoc` + `typst`, *„wie bei den anderen
Dateien"*. Damit sehen Claudias Konzepte aus wie Adams Doppel-Lieferungen, und
es gibt **eine** Werkzeugkette statt zweier (typst liegt ohnehin auf dem
Server, fuer die Rechnungen).

## Der Riegel sitzt in der Vorpruefung, nicht in einer Option

**Gemessen am 09.09., und es widerlegt die urspruengliche Auflage:** pandoc
holt ein Bild mit `https://`-Adresse **von selbst** — ohne `--extract-media`,
und **auch mit `--sandbox`**:

    [WARNING] Could not fetch resource https://example.invalid/bild.png

Die Auflage lautete *„pandoc ohne --extract-media von URLs"*. Sie haette
nichts bewirkt: Der Netzweg haengt nicht an dieser Option. Deshalb weist
**dieses Skript** ab, was nach draussen zeigt, bevor pandoc es sieht.

Dasselbe gilt fuer typst-Paketimporte (`#import "@preview/…"`): typst laedt
das Paket beim ersten Gebrauch aus dem Netz. Auch das faengt die Vorpruefung.

**Warum eine Vorpruefung und nicht ein Netz-Riegel um den Prozess:** Ein
solcher Riegel waere plattformabhaengig (Mac und Linux verschieden) und damit
genau die Klasse *am Mac lief alles*. Eine Textpruefung ist auf beiden
Maschinen dieselbe und **ausfuehrbar messbar**.

## Was zusaetzlich gesetzt wird, und warum

* `--root` auf den Arbeitsordner der Eingabe: `#image()` erreicht nichts
  darueber hinaus.
* `--ignore-system-fonts`: Mac und Server erzeugen **dasselbe** Bild. Ohne das
  griffe jede Maschine in ihren eigenen Schriftbestand — derselbe Fehler, der
  am 03.09. dazu fuehrte, dass eine Rechnung vom Server in Serifen gesetzt war.
* Ausgabe nur in einen Arbeitsbereich (`~/workspace`, `~/postfach`, `/tmp`).

Deterministisch, ohne Modell-Aufruf, ohne Netz, ohne Kosten.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# **`[BERICHTIGT 10.09.2026, Ultracode-Befund H-2]` Diese Regexe pruefen eine
# SCHREIBWEISE, nicht die Klasse — und sie waren bis heute der einzige
# Riegel.**
#
# Gemessen sind acht Formen, die daran vorbeigehen: Referenzbild
# `![a][l]` mit `[l]: https://…` · `![a](<https://…>)` · mehrzeiliges
# `![a](\nhttps://…)` · `<img\n src=…>` · `<object data=…>` · Roh-Typst
# `#image("https://…")` · `#import"@preview/…"` ohne Leerzeichen · `#include`.
# Pandoc holt Netzbilder auch mit `--sandbox`. Das Skript steht in der
# Positivliste, laeuft also ohne Dialog: Ein Papier mit Text aus einer Mail
# oder Webseite waere damit ein Abrufkanal nach draussen gewesen.
#
# **Der Riegel ist jetzt der Netz-Namensraum** (`netzfreier_vorspann`), nicht
# diese Muster. Sie bleiben, weil sie eine **gute Fehlermeldung** geben: Wer
# ein Netzbild einbaut, erfaehrt es benannt, statt ein Papier ohne Bild zu
# bekommen. **Hoeflichkeit, nicht Sicherheit** — und der Unterschied steht
# hier, damit ihn niemand wieder verwechselt.
_NETZ_BILD = re.compile(r"!\[[^\]]*\]\(\s*(?:https?:|//)", re.IGNORECASE)
_NETZ_TAG = re.compile(r"<img[^>]+src\s*=\s*[\"']?\s*(?:https?:|//)", re.IGNORECASE)
_TYPST_PAKET = re.compile(r"#import\s+\"@preview/", re.IGNORECASE)


def arbeitsbereiche() -> list[Path]:
    """Wohin geschrieben werden darf — dieselben Orte wie in der Positivliste.

    Aus der Umgebung ableitbar, damit ein Pruefer sie auf Wegwerf-Ordner
    umbiegen kann, statt gegen Adams echte Ablage zu messen.
    """
    roh = os.environ.get("KONZEPT_PDF_BEREICHE")
    if roh:
        return [Path(p).expanduser().resolve() for p in roh.split(":") if p]
    heim = Path(os.environ.get("HOME") or Path.home())
    return [(heim / "workspace").resolve(), (heim / "postfach").resolve(),
            Path("/tmp").resolve()]


def typst_pfad() -> str | None:
    """Dieselbe Suche wie in den Rechnungsgeneratoren.

    **Der Dienst-PATH kennt `~/.local/bin` nicht** (gemessen am laufenden Bot
    am 03.09.): Die Positivliste gaebe `typst` frei, die Shell saegte
    *command not found*.
    """
    if os.environ.get("TYPST_BIN"):
        return os.environ["TYPST_BIN"]
    gefunden = shutil.which("typst")
    if gefunden:
        return gefunden
    lokal = Path(os.environ.get("HOME") or Path.home()) / ".local/bin/typst"
    return str(lokal) if lokal.exists() else None


def pruefe_quelle(text: str) -> str | None:
    """Der Grund, warum diese Datei NICHT verarbeitet wird — oder `None`.

    Ein Satz, der sagt **was** und **wo**, damit Claudia die Stelle findet,
    statt zu raten.
    """
    for nr, zeile in enumerate(text.splitlines(), 1):
        if _NETZ_BILD.search(zeile) or _NETZ_TAG.search(zeile):
            return (f"Zeile {nr} verweist auf ein Bild im Netz. Dieses Skript "
                    "laedt nichts aus dem Netz — lege das Bild neben die "
                    "Markdown-Datei und verweise relativ darauf.")
        if _TYPST_PAKET.search(zeile):
            return (f"Zeile {nr} importiert ein typst-Paket (@preview). Die "
                    "werden beim ersten Gebrauch aus dem Netz geladen; dieses "
                    "Skript arbeitet ohne Netz.")
    return None


def netzfreier_vorspann() -> "list[str] | None":
    """Der Aufruf-Vorspann, der pandoc und typst **ohne Netz** startet.

    **[NEU 10.09.2026, H-2]** `unshare -rn` legt einen eigenen
    Netz-Namensraum an — darin gibt es keine Schnittstelle ausser `lo`, und
    zwar unabhaengig davon, welche Schreibweise im Dokument steht. Das ist
    der Unterschied zwischen *einen Ausdruck verbessern* und *die Klasse
    schliessen*.

    `-r` bildet den eigenen Benutzer im Namensraum auf root ab. Das ist
    **kein** Systemrecht: Ausserhalb bleibt der Prozess derselbe
    unprivilegierte Benutzer; ohne `-r` verlangte `unshare -n` echte
    Rechte, und die hat dieser Bot nicht und soll sie nicht haben.

    **Geprueft statt vermutet:** Manche Umgebungen haben `unshare`, erlauben
    aber keine Benutzer-Namensraeume. Deshalb ein echter Probelauf, kein
    `which`-Treffer allein.

    `None` heisst: kein Netz-Riegel moeglich. Der Aufrufer **verweigert**
    dann — ein Papier nicht zu setzen ist folgenlos, ein offener Abrufkanal
    nicht.
    """
    if shutil.which("unshare") is None:
        return None
    try:
        probe = subprocess.run(["unshare", "-rn", "true"],
                               capture_output=True, timeout=10)
    except Exception:
        return None
    return ["unshare", "-rn"] if probe.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ein Markdown-Papier als PDF setzen (pandoc + typst)")
    ap.add_argument("quelle", help="die Markdown-Datei")
    ap.add_argument("-o", "--ausgabe", default=None,
                    help="Zieldatei; ohne Angabe die Quelle mit .pdf")
    a = ap.parse_args()

    quelle = Path(a.quelle).expanduser().resolve()
    if not quelle.is_file():
        print(f"FEHLER: nicht gefunden: {quelle}", file=sys.stderr)
        return 2
    ziel = (Path(a.ausgabe).expanduser().resolve() if a.ausgabe
            else quelle.with_suffix(".pdf"))

    # **Die Ausgabe bleibt in den Arbeitsbereichen.** Sonst waere dieses
    # Skript ein freigegebener Weg, irgendwohin zu schreiben — und es steht
    # in der Positivliste, also gaebe es dafuer keine Rueckfrage mehr.
    bereiche = arbeitsbereiche()
    if not any(ziel == b or b in ziel.parents for b in bereiche):
        print(f"FEHLER: Ausgabe liegt ausserhalb der Arbeitsbereiche: {ziel}",
              file=sys.stderr)
        return 2

    grund = pruefe_quelle(quelle.read_text(encoding="utf-8", errors="replace"))
    if grund:
        # **Benannt abgewiesen, nicht still uebergangen.** Wer nicht erfaehrt,
        # warum keine PDF entstand, sucht den Fehler beim Werkzeug.
        print(f"ABGEWIESEN: {grund}", file=sys.stderr)
        return 3

    typst = typst_pfad()
    if typst is None:
        print("FEHLER: typst nicht gefunden (TYPST_BIN, PATH, ~/.local/bin)",
              file=sys.stderr)
        return 4

    # **Der Riegel, H-2.** Vor pandoc, nicht in pandoc: Der Prozess bekommt
    # gar kein Netz, statt dass wir ihm das Fragen abgewoehnen wollen.
    vorspann = netzfreier_vorspann()
    if vorspann is None:
        print("FEHLER: kein Netz-Namensraum verfuegbar (unshare -rn). "
              "Dieses Skript setzt Papiere nur ohne Netz; ohne diese Zusage "
              "wird nichts gesetzt.", file=sys.stderr)
        return 6

    befehl = vorspann + [
        "pandoc", str(quelle), "-o", str(ziel),
        "--pdf-engine", typst,
        # Der Wurzelpfad ist der Ordner der Quelle: Bilder daneben ja, alles
        # darueber nein.
        "--pdf-engine-opt", f"--root={quelle.parent}",
        # Gleiches Bild auf beiden Maschinen — siehe Kopf.
        "--pdf-engine-opt", "--ignore-system-fonts",
    ]
    schriften = os.environ.get("KONZEPT_PDF_SCHRIFTEN")
    if schriften:
        befehl += ["--pdf-engine-opt", f"--font-path={schriften}"]

    e = subprocess.run(befehl, capture_output=True, text=True)
    if e.returncode != 0 or not ziel.exists():
        print(f"FEHLER: pandoc/typst endete mit {e.returncode}\n"
              f"{(e.stderr or e.stdout or '').strip()[-400:]}", file=sys.stderr)
        return 5

    print(f"PDF gesetzt: {ziel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
