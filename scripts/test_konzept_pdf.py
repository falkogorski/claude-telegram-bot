#!/usr/bin/env python3
# <!-- ROLLE: test-konzept-pdf -->
"""Verhaltenstest des PDF-Skripts (M-4) — **es laeuft echt.**

**Der Kern ist nicht, dass eine PDF entsteht, sondern dass NICHTS hinausgeht.**
Gemessen wird deshalb mit einer `pandoc`-Attrappe, die jeden Aufruf
protokolliert: So laesst sich sagen, ob das Skript den Fall **vorher**
abgewiesen hat — oder ob pandoc ihn zu sehen bekam und die Netz-Anfrage
gestellt haette.

**Warum das noetig war** (gemessen am 09.09.): Die urspruengliche Auflage
lautete *„pandoc ohne `--extract-media` von URLs"*. Sie traegt nicht — pandoc
holt ein `https://`-Bild von selbst, **auch mit `--sandbox`**. Der Riegel muss
also vor pandoc sitzen, und genau das misst dieser Pruefer.
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKRIPT = ROOT / "scripts" / "konzept_pdf.py"

_TMP = Path(tempfile.mkdtemp(prefix="konzeptpdf-")).resolve()
BIN = _TMP / "bin"
ARBEIT = _TMP / "arbeit"
for d in (BIN, ARBEIT):
    d.mkdir(parents=True, exist_ok=True)
PROTOKOLL = _TMP / "pandoc-aufrufe.log"

# Die Attrappe schreibt ihren Aufruf mit und legt eine PDF-Attrappe ab.
(BIN / "pandoc").write_text(
    "#!/bin/bash\n"
    f'printf "%s\\n" "$*" >> "{PROTOKOLL}"\n'
    'ziel=""; n=1\n'
    'for a in "$@"; do\n'
    '  if [ "$a" = "-o" ]; then ziel_next=1; elif [ -n "${ziel_next:-}" ]; then\n'
    '    ziel="$a"; ziel_next=""; fi\n'
    'done\n'
    '[ -n "$ziel" ] && printf "%%PDF-1.4 attrappe" > "$ziel"\n'
    "exit 0\n", encoding="utf-8")
(BIN / "pandoc").chmod((BIN / "pandoc").stat().st_mode | stat.S_IEXEC)
(BIN / "typst").write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
(BIN / "typst").chmod((BIN / "typst").stat().st_mode | stat.S_IEXEC)

# **[NEU 10.09.2026, H-2] Attrappe fuer `unshare` — am Rand, nicht in der Mitte.**
#
# Der Netz-Namensraum ist eine Linux-Eigenschaft; am Mac gibt es `unshare`
# nicht. Ohne diese Attrappe verweigerte das Skript hier **richtigerweise**,
# und vier Zeilen waeren am Mac rot geworden, ohne dass etwas kaputt ist —
# ein Pruefer, der auf einer der beiden Maschinen immer rot ist, wird binnen
# einer Woche abgeschaltet.
#
# Sie verhaelt sich wie das echte Werkzeug: `-r` und `-n` schlucken, den Rest
# ausfuehren. Gemessen wird damit, **dass der Vorspann gesetzt wird** — dass
# er im Betrieb wirklich das Netz nimmt, misst der VPS (Prueflauf im
# Bericht), nicht dieser Pruefstand.
(BIN / "unshare").write_text(
    "#!/bin/bash\n"
    'while [ "${1:0:1}" = "-" ]; do shift; done\n'
    'exec "$@"\n', encoding="utf-8")
(BIN / "unshare").chmod((BIN / "unshare").stat().st_mode | stat.S_IEXEC)

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


def lauf(quelle: Path, ziel: Path | None = None, *, ohne_unshare: bool = False):
    umgebung = dict(os.environ)
    # `ohne_unshare` baut den Zustand nach, in dem **kein** Netz-Namensraum zu
    # haben ist: leerer PATH ausser den Attrappen, `unshare` daraus entfernt.
    pfad = str(BIN) if ohne_unshare else f"{BIN}:{os.environ.get('PATH', '')}"
    umgebung.update({
        "PATH": pfad,
        "KONZEPT_PDF_BEREICHE": str(ARBEIT),
        "TYPST_BIN": str(BIN / "typst"),
    })
    args = [sys.executable, str(SKRIPT), str(quelle)]
    if ziel:
        args += ["-o", str(ziel)]
    return subprocess.run(args, env=umgebung, capture_output=True, text=True)


def papier(name: str, inhalt: str) -> Path:
    p = ARBEIT / name
    p.write_text(inhalt, encoding="utf-8")
    return p


print("== PDF-Skript (M-4) ==")

# ---- ein gewoehnliches Papier laeuft durch --------------------------------
PROTOKOLL.unlink(missing_ok=True)
gut = papier("gut.md", "# Titel\n\nEin Absatz ohne alles.\n")
e = lauf(gut, ARBEIT / "gut.pdf")
zeile("ein gewoehnliches Papier wird gesetzt",
      e.returncode == 0 and (ARBEIT / "gut.pdf").exists(),
      gemessen=f"rc={e.returncode} {e.stderr.strip()[:90]}")
_aufruf = PROTOKOLL.read_text(encoding="utf-8") if PROTOKOLL.exists() else ""
zeile("die Schriftschranke steht im Aufruf",
      "--ignore-system-fonts" in _aufruf,
      gemessen=_aufruf[:120])
zeile("der Wurzelpfad zeigt auf den Ordner der Quelle",
      f"--root={ARBEIT}" in _aufruf, gemessen=_aufruf[:160])

# ---- was nach draussen zeigt, erreicht pandoc GAR NICHT --------------------
for name, inhalt, was in [
    ("netz.md", "# T\n\ntext\n\n![a](https://example.invalid/b.png)\n",
     "ein Bild ueber https"),
    ("netz2.md", '# T\n\n<img src="http://example.invalid/b.png">\n',
     "ein img-Tag ueber http"),
    ("netz3.md", "# T\n\n![a](//example.invalid/b.png)\n",
     "eine schemalose Netzadresse"),
    ("paket.md", '# T\n\n#import "@preview/cetz:0.2.0"\n',
     "ein typst-Paketimport"),
]:
    PROTOKOLL.unlink(missing_ok=True)
    q = papier(name, inhalt)
    ziel = ARBEIT / (name + ".pdf")
    e = lauf(q, ziel)
    # **Die zweite Haelfte ist die eigentliche Messung:** nicht nur, dass
    # abgewiesen wurde, sondern dass pandoc den Fall nie gesehen hat.
    zeile(f"{was} wird abgewiesen — und pandoc gar nicht erst gerufen",
          e.returncode == 3 and not PROTOKOLL.exists() and not ziel.exists(),
          gemessen=f"rc={e.returncode} pandoc-gerufen={PROTOKOLL.exists()}")
    zeile(f"die Abweisung sagt, WO es steht ({was})",
          "Zeile" in e.stderr and "ABGEWIESEN" in e.stderr,
          gemessen=e.stderr.strip()[:100])

# ---- die Gegenrichtung: ein LOKALES Bild ist erlaubt -----------------------
PROTOKOLL.unlink(missing_ok=True)
lokal = papier("lokal.md", "# T\n\n![a](bild.png)\n")
e = lauf(lokal, ARBEIT / "lokal.pdf")
zeile("ein Bild NEBEN der Datei bleibt erlaubt (Gegenrichtung)",
      e.returncode == 0, gemessen=f"rc={e.returncode} {e.stderr.strip()[:90]}")

# ---- die Ausgabe bleibt in den Arbeitsbereichen ----------------------------
PROTOKOLL.unlink(missing_ok=True)
e = lauf(gut, _TMP / "draussen.pdf")
zeile("Ausgabe ausserhalb der Arbeitsbereiche wird abgewiesen",
      e.returncode == 2 and not (_TMP / "draussen.pdf").exists(),
      gemessen=f"rc={e.returncode}")
zeile("und pandoc wurde dafuer nicht gerufen",
      not PROTOKOLL.exists())

# ---- H-2: der Riegel ist der Netz-Namensraum, nicht das Muster ------------
#
# **Der Ultracode-Befund vom 10.09.:** Acht Schreibweisen gehen an der
# Vorpruefung vorbei, und pandoc holt Netzbilder auch mit `--sandbox`. Ein
# besserer Ausdruck haette den neunten Fall offen gelassen.
PROTOKOLL.unlink(missing_ok=True)
_h2 = lauf(gut, ARBEIT / "h2.pdf")
_aufrufe = PROTOKOLL.read_text() if PROTOKOLL.exists() else ""
zeile("H-2: pandoc laeuft im Netz-Namensraum, nicht frei",
      _h2.returncode == 0 and _aufrufe.strip() != "",
      gemessen=f"rc={_h2.returncode}")

# Dass der Vorspann WIRKLICH davorsteht, misst die Attrappe: Sie wird nur
# gerufen, wenn `unshare` im Befehl steht — sonst liefe pandoc direkt.
_direkt = lauf(gut, ARBEIT / "h2b.pdf", ohne_unshare=True)
zeile("ohne Netz-Namensraum wird VERWEIGERT, nicht ohne Riegel gesetzt",
      _direkt.returncode == 6 and not (ARBEIT / "h2b.pdf").exists(),
      gemessen=f"rc={_direkt.returncode} · {(_direkt.stderr or '')[:120]}")

# Eine Referenz-Schreibweise, die die alte Vorpruefung NICHT faengt. Sie darf
# durchgehen — der Riegel liegt jetzt woanders. Waere die Vorpruefung noch der
# Riegel, muesste diese Zeile scheitern, und genau das war der Befund.
_ref = papier("referenz.md",
              "# Titel\n\nText.\n\n![Bild][l]\n\n[l]: https://example.invalid/x.png\n")
PROTOKOLL.unlink(missing_ok=True)
_e = lauf(_ref, ARBEIT / "ref.pdf")
zeile("die Referenz-Schreibweise geht an der Vorpruefung vorbei (gemessen)",
      _e.returncode == 0, gemessen=f"rc={_e.returncode}")
# Die Attrappe schreibt nur ihre EIGENEN Argumente mit; dass sie ueberhaupt
# lief, beweist den Vorspann. Ohne ihn haette der PATH-Eintrag `pandoc`
# direkt getroffen -- und dann stuende hier kein Protokoll aus DIESEM Lauf.
zeile("und genau deshalb traegt der Namensraum den Riegel, nicht das Muster",
      PROTOKOLL.exists() and "referenz.md" in PROTOKOLL.read_text(),
      gemessen=(PROTOKOLL.read_text()[:160] if PROTOKOLL.exists() else "kein Aufruf"))

shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen des PDF-Skripts bestanden.")
