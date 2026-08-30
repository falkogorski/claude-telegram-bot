#!/usr/bin/env python3
"""Kein Werkzeug, kein Urteil — der Tagescheck sagt nicht Gruen ins Blaue.

**F-Listen-Fund [65], von Engywuck vorgezogen.** Die Netzwerk-Pruefung schrieb
im `else`-Zweig *„Nach aussen lauschen nur SSH und der Webhook-Port"*. Fehlt
`ss`, liefert die Pipeline leer — und genau dieser Zweig greift.

**Das Gruen hing an der Anwesenheit des Werkzeugs, nicht am Zustand der
Maschine.** Und die Folge ist keine fehlende Meldung, sondern eine **falsche**:
Ein Pruefer, der schweigt, ist aergerlich; einer, der Adam eine Zusage ueber
die Sicherheitslage des Servers macht, ohne sie gemessen zu haben, ist etwas
anderes — er verlaesst sich darauf.

## Die Menge, gezaehlt statt geraten

Engywucks Auflage vor dem Bau: *Wie viele weitere Zeilen schreiben eine
positive Aussage im `else`-Zweig einer Pruefung, deren Werkzeug fehlen kann?*
Gezaehlt: **vier** `else`-Zweige mit positiver Aussage, davon **zwei** an einem
Werkzeug — `ss` und `git`. Die anderen beiden pruefen eine Datei bzw. brechen
vorher ab.

Gemessen wird **ausgefuehrt**: Der Tagescheck laeuft im Trockenlauf mit einem
PATH, in dem das jeweilige Werkzeug fehlt.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "daily_check.sh"

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


def lauf(ohne: tuple[str, ...]) -> str:
    """Faehrt die beiden ECHTEN Bloecke mit einem PATH ohne diese Werkzeuge.

    **Geschnitten statt ganz gestartet, und der Grund ist gemessen:** Der
    Tagescheck schreibt seine Zeilen ins Protokoll unter
    `/home/claudebot/claude-telegram-bot/logs` — dort, wo er laeuft. Am
    Bau-Rechner gibt es diesen Pfad nicht, die Zeilen waeren nicht lesbar. Der
    gemessene Code ist trotzdem der echte: `werkzeug_da` und die beiden
    `if`-Bloecke werden aus der Datei geschnitten und ausgefuehrt.
    """
    quelle = CHECK.read_text(encoding="utf-8")
    fn = re.search(r"^werkzeug_da\(\) \{.*?^\}", quelle, re.S | re.M)
    netz = re.search(r'^if werkzeug_da ss .*?^fi$', quelle, re.S | re.M)
    klon = re.search(r'^if ! werkzeug_da git .*?^fi\nfi$', quelle, re.S | re.M)
    fehlt = [n for n, m in (("werkzeug_da", fn), ("ss-Block", netz),
                            ("git-Block", klon)) if m is None]
    if fehlt:
        return "SCHNITT-FEHLGESCHLAGEN: " + ", ".join(fehlt)

    pfad = Path(tempfile.mkdtemp(prefix="ohne-werkzeug-"))
    gesehen = set()
    for ordner in ("/usr/bin", "/bin", "/usr/sbin", "/sbin"):
        if not os.path.isdir(ordner):
            continue
        for name in os.listdir(ordner):
            if name in ohne or name in gesehen:
                continue
            quelle_w = shutil.which(name)
            if quelle_w:
                gesehen.add(name)
                try:
                    os.symlink(quelle_w, pfad / name)
                except OSError:
                    pass
    # Kein f-string fuer den Shell-Block: Er ist voller geschweifter Klammern,
    # und die haben beim ersten Anlauf prompt den Ausdruck zerlegt.
    probe = "\n".join([
        "set -u",
        "lines=(); problems=()",
        "merken() { :; }",
        'add() { lines+=("$1"); echo "$1"; }',
        'red() { problems+=("$1"); echo "ROT $1"; }',
        'BOTDIR="' + str(ROOT) + '"',
        fn.group(0), netz.group(0), klon.group(0),
    ])
    e = subprocess.run(["/bin/bash", "-c", probe],
                       env={"PATH": str(pfad)}, capture_output=True,
                       text=True, timeout=120)
    return (e.stdout or "") + (e.stderr or "")


print("\nDie Menge — gezaehlt, nicht geraten")

quelle = CHECK.read_text(encoding="utf-8")
zeilen_txt = quelle.splitlines()
positiv = []
for i, z in enumerate(zeilen_txt):
    if re.match(r"\s*else\s*$", z):
        for j in range(i + 1, min(i + 4, len(zeilen_txt))):
            if re.search(r'add\s+"[✅✓]', zeilen_txt[j]):
                positiv.append(j + 1)
                break
# **Diese Zeile liest Quelltext und ist damit kein Schutz — sie haelt die
# Zahl fest.** Waechst sie, ist zu pruefen, ob die neue Stelle an einem
# Werkzeug haengt. Ohne sie waere der naechste Fall wieder ein Einzelfund.
zeile("die Zahl der positiven else-Zweige ist unveraendert (4)",
      len(positiv) == 4,
      gemessen=f"{len(positiv)} gefunden, Zeilen {positiv} — pruefen, ob die "
               f"neue an einem Werkzeug haengt")


print("\nOhne `ss` gibt es keine Zusage ueber offene Anschluesse")

ausgabe = lauf(("ss",))
zeile("die Zusage erscheint NICHT", "Nach aussen lauschen nur SSH" not in ausgabe,
      gemessen=[z for z in ausgabe.splitlines() if "lauschen" in z][:2])
zeile("stattdessen wird gesagt, dass nichts gemessen wurde",
      "NICHT GEMESSEN" in ausgabe and "ss ist auf dieser Maschine" in ausgabe,
      gemessen=[z for z in ausgabe.splitlines() if "NICHT GEMESSEN" in z][:2])


print("\nOhne `git` gibt es keine Zusage ueber den Klon")

ausgabe = lauf(("git",))
zeile("die Zusage erscheint NICHT", "VPS-Klon sauber" not in ausgabe,
      gemessen=[z for z in ausgabe.splitlines() if "Klon" in z][:2])
zeile("stattdessen wird gesagt, dass nichts gemessen wurde",
      "git ist auf dieser Maschine" in ausgabe,
      gemessen=[z for z in ausgabe.splitlines() if "NICHT GEMESSEN" in z][:2])


print("\nDie Gegenrichtung — mit Werkzeug wird wirklich gemessen")

# **Ohne diese Zeilen waere alles oben mit einem `return 1` zu erfuellen.** Ein
# Pruefer, der nur das Ausbleiben misst, koennte auch ein Skript loben, das gar
# nichts mehr tut.
#
# **Und sie gilt nur fuer Werkzeuge, die es auf DIESER Maschine gibt.** `ss` ist
# ein Linux-Werkzeug; am Bau-Rechner existiert es nicht, dort waere die
# Gegenrichtung nicht messbar. Das wird GESAGT statt gruen gemeldet — die
# Kategorie dafuer ist heute Vormittag entstanden: *Uebersprungen ist nicht
# bestanden.*
ausgabe = lauf(())
for werkzeug, zusage in (("ss", "Nach aussen lauschen nur SSH"),
                         ("git", "VPS-Klon sauber")):
    if shutil.which(werkzeug) is None:
        print(f"  ⏭️  Gegenrichtung fuer {werkzeug}: auf dieser Maschine NICHT "
              f"MESSBAR ({werkzeug} fehlt hier) — in der Zielumgebung gemessen")
        continue
    zeile(f"mit {werkzeug} erscheint wieder eine echte Aussage",
          f"{werkzeug} ist auf dieser Maschine" not in ausgabe,
          gemessen=[z for z in ausgabe.splitlines()
                    if werkzeug in z and "NICHT GEMESSEN" in z][:2])

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {fehler}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen gruen — kein Werkzeug, kein Urteil ([65]).")
