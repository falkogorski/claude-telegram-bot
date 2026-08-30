#!/usr/bin/env python3
"""Uebersprungen ist nicht bestanden — auf allen vier Ebenen gemessen.

**Sammelauftrag A1 aus dem Faecher-Befund vom 30.08.** Sechs der neununddreissig
Funde sagten dasselbe: *Ein Pruefer meldet gruen, ohne gemessen zu haben.* Das
ist woertlich die Fehlerform, die dieses Projekt an einem einzigen Tag dreimal
gefunden hat — die leere Menge im Differenzmesser, der Vergleich gegen nichts
im Node-Skript, und hier der **Pin-Waechter, der sich selbst abschaltet**.

**Warum ein Haken schlimmer ist als gar keine Zeile:** Er beantwortet die
Frage. Wer "✅ Medien-Transport H1" liest, hakt die Medienkette ab — auch wenn
in diesem Lauf zwoelf Pruefzeilen nie ausgefuehrt wurden.

Vier Ebenen, jede einzeln ausgefuehrt:

    ① der Selbstcheck        (bot.py, NichtsGemessen)
    ② der Laeufer            (regressionstest.sh, Rueckgabewert 77)
    ③ die Pruefer            (media, log_sync — sagen 77 statt 0)
    ④ ein Shell-Pruefer      (test_zielumgebung.sh, melde skip)

**Zur Ebene ②, offen gesagt:** Die Funktion `run()` steht mitten im Laeufer und
laesst sich nicht aufrufen, ohne den ganzen Lauf zu starten. Sie wird deshalb
aus der Datei geschnitten und **ausgefuehrt** — der gemessene Code ist der
echte, aber der Schnitt haengt am Funktionskopf. Findet er nichts, meldet diese
Zeile rot statt gruen; das ist die einzige Fehlerrichtung, die hier taugt.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"

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


# ---------------------------------------------------------------------------
# ① Der Selbstcheck: eine Zeile ohne Messung meldet nicht gruen
# ---------------------------------------------------------------------------
print("\n① Der Selbstcheck kennt einen dritten Zustand")

import bot                                                     # noqa: E402

zeile("es gibt eine eigene Ausnahme dafuer",
      isinstance(getattr(bot, "NichtsGemessen", None), type))


def _pin_zeile(requirements: str | None) -> str:
    """Faehrt run_self_check gegen ein umgebogenes Repo und liefert die
    Pin-Zeile. `None` heisst: gar keine requirements.txt."""
    tmp = Path(tempfile.mkdtemp(prefix="pin-"))
    if requirements is not None:
        (tmp / "requirements.txt").write_text(requirements, encoding="utf-8")
    echt = bot._REPO_DIR
    bot._REPO_DIR = tmp
    try:
        _ok, liste = bot.run_self_check()
    finally:
        bot._REPO_DIR = echt
    return next((z for z in liste if "Pin-Divergenz" in z), "(keine Zeile)")


echt_req = (ROOT / "requirements.txt").read_text(encoding="utf-8")

# Der Normalfall muss gruen bleiben — sonst misst die Zeile nur Laerm.
zeile("mit echtem Pin bleibt die Zeile gruen",
      _pin_zeile(echt_req).startswith("✓"), gemessen=_pin_zeile(echt_req))

# Fund [26], erste Haelfte: Pin von == auf >= gelockert.
gelockert = echt_req.replace("==", ">=")
z = _pin_zeile(gelockert)
zeile("ohne jede Pin-Zeile meldet der Waechter NICHT gruen",
      not z.startswith("✓"), gemessen=z)
zeile("und er sagt, dass nichts gemessen wurde",
      "NICHTS GEMESSEN" in z, gemessen=z)

# Fund [26], zweite Haelfte: Pin auf ein Paket, das es hier nicht gibt.
z = _pin_zeile(echt_req + "\ngibtesnicht==9.9.9\n")
zeile("ein Pin auf ein nicht installiertes Paket meldet NICHT gruen",
      not z.startswith("✓"), gemessen=z)

# Und die fehlende Datei.
z = _pin_zeile(None)
zeile("eine fehlende requirements.txt meldet NICHT gruen",
      not z.startswith("✓"), gemessen=z)

# Die Gegenrichtung, damit „nicht gruen" nicht durch Zufall entsteht:
# eine echte Abweichung muss weiterhin als FEHLER erscheinen, nicht als
# Uebersprung — die beiden Zustaende duerfen nicht verschmelzen.
z = _pin_zeile("claude-agent-sdk==0.0.1\n")
zeile("eine echte Pin-Abweichung bleibt ein Fehler, kein Uebersprung",
      z.startswith("✗") and "NICHTS GEMESSEN" not in z, gemessen=z)


# ---------------------------------------------------------------------------
# ② Der Laeufer: Rueckgabewert 77 zaehlt nicht als bestanden
# ---------------------------------------------------------------------------
print("\n② Der Laeufer zaehlt einen Uebersprung nicht als bestanden")

laeufer = (ROOT / "scripts" / "regressionstest.sh").read_text(encoding="utf-8")
schnitt = re.search(r"^run\(\) \{.*?^\}", laeufer, re.S | re.M)
zeile("die Funktion run() liess sich aus dem Laeufer schneiden",
      schnitt is not None,
      gemessen="Funktionskopf 'run() {' nicht gefunden — Schnitt angepasst?")

if schnitt:
    probe = f"""
    set -u
    FAILS=0; GESAMT=0; UEBERSPRUNGEN=0
    LOGDATEI="$(mktemp "${{TMPDIR:-/tmp}}/probe.XXXXXX")"
    {schnitt.group(0)}
    run "gruen"         /bin/sh -c 'echo "✓ etwas gemessen"; exit 0'
    run "uebersprungen" /bin/sh -c 'echo nichts gemessen; exit 77'
    run "rot"           /bin/sh -c 'exit 1'
    run "stiller erfolg" /bin/sh -c 'exit 0' scripts/attrappe.py
    run "fremdes werkzeug" /bin/sh -c 'exit 0'
    echo "ZAEHLER gesamt=$GESAMT fails=$FAILS uebersprungen=$UEBERSPRUNGEN"
    rm -f "$LOGDATEI"
    """
    e = subprocess.run(["bash", "-c", probe], capture_output=True, text=True)
    ausgabe = e.stdout
    m = re.search(r"ZAEHLER gesamt=(\d+) fails=(\d+) uebersprungen=(\d+)", ausgabe)
    zeile("die geschnittene Funktion liess sich ausfuehren", m is not None,
          gemessen=(e.stderr or ausgabe)[:160])
    if m:
        gesamt, fails, uebersprungen = (int(x) for x in m.groups())
        # Vier Prueflinge: gruen, uebersprungen (77), rot, **stiller Erfolg**.
        # Der letzte endet mit 0 und schweigt — genau die Form, in der die
        # sechs Faecher-Faelle durchkamen. Er MUSS als Uebersprung zaehlen.
        #
        # Das Argument `scripts/attrappe.py` ist kein Beiwerk: Die Schranke im
        # Laeufer gilt nur fuer eigene Pruefskripte, weil `py_compile` bei
        # Erfolg konventionell schweigt und sonst zehnmal je Lauf falsch
        # anschluege. `sh -c 'exit 0' <arg0>` fuehrt nichts davon aus — es
        # setzt nur den Namen, an dem die Schranke den eigenen Pruefer erkennt.
        zeile("der gemeldete Uebersprung UND der stille zaehlen beide",
              uebersprungen == 2, gemessen=ausgabe.strip()[-90:])
        zeile("er zaehlt NICHT als Fehlschlag (nur der echte tut das)",
              fails == 1, gemessen=f"fails={fails}")
        # Fuenf Prueflinge, davon bestehen genau zwei: der gruene und das
        # fremde Werkzeug. Uebrig bleiben ein Fehlschlag und zwei Uebersprünge.
        zeile("und beide zaehlen NICHT als bestanden",
              gesamt - fails - uebersprungen == 2,
              gemessen=f"bestanden={gesamt - fails - uebersprungen} von {gesamt}")
        zeile("ein Pruefer, der schweigt, wird als solcher benannt",
              "kein einziges Haekchen" in ausgabe,
              gemessen=ausgabe.strip()[-140:])
        # **Die Gegenrichtung, und sie ist der teurere Fehler:** Ein fremdes
        # Werkzeug (`py_compile`, `bash -n`) schweigt bei Erfolg — das ist dort
        # Konvention und keine fehlende Messung. Ohne diese Zeile koennte die
        # Einschraenkung still verschwinden, und der Lauf meldete bei jedem
        # Durchgang zehn falsche Uebersprünge. Genau so lief mein erster
        # Anlauf.
        zeile("ein fremdes Werkzeug darf schweigen, ohne als Uebersprung zu gelten",
              gesamt == 5 and uebersprungen == 2,
              gemessen=f"{gesamt} Laeufe, {uebersprungen} uebersprungen")
    zeile("der Uebersprung ist in der Ausgabe als solcher erkennbar",
          "UEBERSPRUNGEN" in ausgabe and "✅ uebersprungen" not in ausgabe,
          gemessen=ausgabe.strip()[:160])

# **Und die Schlussbilanz — sie war mein eigener blinder Fleck.** Die
# Gegenprobe „Uebersprungene wieder mitzaehlen" liess ALLE Zeilen gruen: Der
# Pruefer mass `run()`, aber nie die Zeile, die daraus die Zahl bildet. Also
# wird auch sie geschnitten und ausgefuehrt, mit gesetzten Zaehlern.
bilanzzeile = next((z for z in laeufer.splitlines()
                    if "Ergebnis:" in z and "echo" in z), "")
e = subprocess.run(["bash", "-c",
                    f"GESAMT=3; FAILS=1; UEBERSPRUNGEN=1\n{bilanzzeile}"],
                   capture_output=True, text=True)
zeile("die Bilanz des Laeufers zaehlt Uebersprungene nicht als bestanden",
      "1/3" in e.stdout, gemessen=e.stdout.strip() or e.stderr.strip()[:100])

# Fund [70]: kein fester Pfad in /tmp mehr, den ein zweiter Nutzer nicht
# beschreiben kann. Gemessen wird die Abwesenheit im Quelltext — hier
# ausnahmsweise richtig, weil ein FESTER Pfad genau eine Zeichenkette IST.
zeile("der Laeufer schreibt sein Protokoll nicht mehr an einen festen Ort",
      "/tmp/regress_last.log" not in laeufer and "mktemp" in laeufer)


# ---------------------------------------------------------------------------
# ③ Die Pruefer sagen 77, wenn ihr Werkzeug fehlt
# ---------------------------------------------------------------------------
print("\n③ Ein Pruefer ohne sein Werkzeug sagt 77, nicht 0")


def _ohne(werkzeuge: list[str], skript: str) -> subprocess.CompletedProcess:
    """Faehrt einen Pruefer in einem PATH, in dem die Werkzeuge fehlen."""
    leer = tempfile.mkdtemp(prefix="leerer-pfad-")
    # Der venv-Ordner bleibt drin, sonst fehlt python selbst.
    umgebung = dict(os.environ, PATH=f"{ROOT / '.venv' / 'bin'}:{leer}")
    return subprocess.run([str(ROOT / ".venv" / "bin" / "python"),
                           str(ROOT / "scripts" / skript)],
                          env=umgebung, capture_output=True, text=True)


e = _ohne(["ffmpeg", "ffprobe"], "test_media_h1.py")
zeile("ohne ffmpeg sagt der Medien-Pruefer 77", e.returncode == 77,
      gemessen=f"rc={e.returncode}: {(e.stdout or e.stderr).strip()[:90]}")
zeile("und er sagt im Klartext, dass nichts gemessen wurde",
      "NICHT GEMESSEN" in e.stdout.upper(), gemessen=e.stdout.strip()[:120])

e = _ohne(["rsync"], "test_log_sync_quittung.py")
zeile("ohne rsync sagt der Quittungs-Pruefer 77", e.returncode == 77,
      gemessen=f"rc={e.returncode}: {(e.stdout or e.stderr).strip()[:90]}")
zeile("er beschuldigt nicht mehr die Quittungslogik",
      "Quittung wurde NICHT" in e.stdout or "rsync fehlt" in e.stdout,
      gemessen=e.stdout.strip()[:140])

# **Der stille Teil eine Ebene tiefer: das Abgleich-Skript selbst.** Es lief
# ohne rsync durch, kopierte nichts und endete mit 0 samt „Keine
# Log-Aenderungen" — ein Abgleich, der nichts kopiert, sah aus wie einer, bei
# dem es nichts zu kopieren gab.
#
# Gefahren mit LEEREM PATH und absolutem Pfad zur Shell: Bis zur Schranke
# braucht das Skript nur eingebaute Befehle, danach kaeme rsync. Wer die
# Schranke entfernt, faellt hier also auf einen ANDEREN Fehler — deshalb wird
# nicht nur „ungleich null", sondern der eigene Rueckgabewert 3 gemessen.
leer = tempfile.mkdtemp(prefix="leerer-pfad-")
e = subprocess.run(["/bin/bash", str(ROOT / "scripts" / "log_sync.sh")],
                   env={"PATH": leer, "HOME": leer,
                        "LOG_SYNC_SRC": leer, "LOG_SYNC_REPO": leer},
                   capture_output=True, text=True)
zeile("der Abgleich selbst bricht ohne rsync mit seinem eigenen Grund ab",
      e.returncode == 3 and "rsync fehlt" in e.stderr,
      gemessen=f"rc={e.returncode}: {(e.stderr or e.stdout).strip()[:110]}")
zeile("und er sagt, dass NICHTS abgeglichen wurde",
      "NICHTS abgeglichen" in e.stderr, gemessen=e.stderr.strip()[:110])


# ---------------------------------------------------------------------------
# ④ Ein Shell-Pruefer: der Uebersprung erzeugt eine Zahlendifferenz
# ---------------------------------------------------------------------------
print("\n④ Der Uebersprung erzeugt die Zahlendifferenz, die gefehlt hat")

e = subprocess.run(["bash", str(ROOT / "scripts" / "test_zielumgebung.sh")],
                   cwd=ROOT, capture_output=True, text=True)
ausgabe = e.stdout
bilanz = next((z for z in ausgabe.splitlines() if "Zielumgebung:" in z), "")
m = re.search(r"(\d+)/(\d+) bestanden", bilanz)
zeile("der Pruefer nennt eine Bilanz", m is not None, gemessen=bilanz)

# **Die Maschine wird BESTIMMT, nicht erfragt** — mein zweiter blinder Fleck.
# Vorher verzweigte diese Stelle auf „steht 'uebersprungen' in der Ausgabe?",
# und genau das machte sie blind: Die Gegenprobe (`melde skip` zurueck auf
# `melde ok`) liess sie in den anderen Zweig laufen, der dann eine volle
# Bilanz erwartete — und die war voll. Eine Verzweigung ueber das, was man
# messen will, misst nichts.
# **Der Ort kommt aus dem Prüfling, nicht aus meinem Gedächtnis.** Mein erster
# Anlauf schrieb den Betriebspfad hier fest hin — und wurde prompt vom
# Differenzmesser gemeldet („Prüfer mit fest verdrahtetem Betriebspfad"). Zu
# Recht: Das wären zwei Wahrheiten für dieselbe Frage gewesen, und die eine
# hätte sich beim ersten Umzug von der anderen entfernt. Der Prüfling selbst
# weiß, wo die Zielumgebung liegt.
_zielumgebung_quelle = (ROOT / "scripts" / "test_zielumgebung.sh").read_text(encoding="utf-8")
_m_bot = re.search(r'^_bot="([^"]+)"', _zielumgebung_quelle, re.M)
zeile("der Ort der Zielumgebung liess sich aus dem Pruefling lesen",
      _m_bot is not None, gemessen="Zeile '_bot=\"...\"' nicht gefunden")
in_zielumgebung = bool(_m_bot) and Path(_m_bot.group(1), ".venv/bin/python3").exists()
if in_zielumgebung:
    zeile("in der Zielumgebung laeuft der Normalfall wirklich — Bilanz voll",
          bool(m) and m.group(1) == m.group(2), gemessen=bilanz)
else:
    bestanden, gesamt = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    zeile("ausserhalb der Zielumgebung MUSS ein Uebersprung erscheinen",
          "uebersprungen" in ausgabe, gemessen=bilanz)
    zeile("uebersprungene Zeilen fehlen in der Bestanden-Zahl",
          bool(m) and bestanden < gesamt, gemessen=bilanz)
    zeile("und der Uebersprung wird ausdruecklich genannt",
          "nichts gemessen" in ausgabe, gemessen=bilanz)

zeile("der Pruefer selbst bleibt gruen (ein Uebersprung ist kein Fehlschlag)",
      e.returncode == 0, gemessen=f"rc={e.returncode}")

print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {fehler}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen gruen — Uebersprungen ist nicht bestanden (A1).")
