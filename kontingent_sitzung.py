#!/usr/bin/env python3
# <!-- ROLLE: kontingent-sitzung -->
"""Liest den Abo-Kontingentstand aus einer echten Claude-Sitzung.

**Warum dieser Umweg, und warum er sich lohnt.** Punkt A2 suchte den
Prozentwert des Fünf-Stunden- und Wochenfensters. Gemessen am 20.08. über vier
Wege — der Kontostand-Endpunkt weist das Abo-Token ab (403), das SDK-Ereignis
trägt nur Zustand und Rücksetzzeit (``utilization`` ist ``None``), die rohe
CLI im Stapelbetrieb ebenso, und die Statusline greift nur interaktiv.

Adams Screenshot seiner Oberfläche zeigte die Zahlen trotzdem — **48 %, mit
Balken.** Also gibt es sie, nur nicht auf den geprüften Wegen. Im CLI-Bündel
steht, warum: Die Prozentwerte liegen in einem eigenen Speicher, den allein
die **Oberfläche** nach außen reicht (Statusline und ``/usage``).

**Also wird hier eine echte Sitzung gefahren.** Genau Adams ursprünglicher
Gedanke: *„der Bot ist doch selber eine laufende Sitzung, warum kann der nicht
fragen?"* — nur eine Ebene tiefer, an einem Pseudo-Terminal.

## Der Befund, der alles ändert

``/usage`` ist ein **lokaler** Befehl. Die Sitzung meldet nach dem Lauf
``Total cost: $0.0000`` und ``Total duration (API): 0s`` — **es gibt keinen
Modell-Aufruf.** Damit kostet dieser Abruf **kein Kontingent** und fällt nicht
unter die AGB-Frage zeitgesteuerter Modell-Läufe. Was er kostet, ist Zeit
(rund eine Minute) und etwas Rechenlast.

## Was hier brechen kann, offen benannt

Gelesen wird ein **Bildschirm**, keine Schnittstelle. Ändert sich das Layout
der Oberfläche, liefert das Muster nichts mehr. Das ist bewusst in Kauf
genommen — die Alternative war, Adam die Zahl vorzuenthalten, die seine
eigene Oberfläche ihm zeigt. **Ein Fehlschlag ist deshalb ein sauberer
Fehlschlag:** kein Wert, kein geratener Ersatz, eine ehrliche Meldung.

Eigene Ablage (``HOME``) statt der des Bot-Kontos, damit diese Sitzung weder
Verlauf noch Konfiguration des Bots berührt.
"""
from __future__ import annotations

import os
import pty
import re
import select
import time
from pathlib import Path

# Eigene Ablage: Die Sitzung legt Verlauf und Zustand an — das gehört nicht in
# die des Bots. Nichts davon ist ein Geheimnis; das Token kommt weiterhin aus
# der geschützten Umgebung und wird hier nie berührt.
HEIM = Path(os.environ.get("KONTINGENT_HOME")
            or (Path.home() / ".claude" / "kontingent-sitzung"))

# Wie lange insgesamt gewartet wird. Der Start der Oberfläche dauert spürbar;
# unter etwa 60 Sekunden wird es unzuverlässig.
FRIST_S = float(os.environ.get("KONTINGENT_FRIST") or 90)

# Wann getippt wird. Vorher rendert die Oberfläche noch, und **schnelle
# Eingaben werden geschluckt** — beim Bauen zweimal erlebt: einmal ging die
# Eingabe im Startbildschirm unter, einmal verbrauchte sie der Vertrauensdialog.
WARTEN_VOR_EINGABE_S = 25.0
WARTEN_NACH_EINGABE_S = 25.0

_ANSI = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b[()][0-9A-B]")
# Die Oberfläche setzt Text ohne Leerzeichen zusammen („49%used"), deshalb sind
# die Muster bewusst tolerant gegenüber fehlenden Zwischenräumen.
_PROZENT = re.compile(r"(\d{1,3})\s*%\s*used", re.IGNORECASE)
_RESET = re.compile(r"Resets\s*([A-Za-z0-9 ,:.]{2,40})", re.IGNORECASE)

# Welcher Abschnitt zu welchem Fenster gehört. Die Namen stammen aus der
# Oberfläche; „Current session" ist dort das Fünf-Stunden-Fenster.
_ABSCHNITTE = (
    ("currentsession", "five_hour"),
    ("currentweek(allmodels)", "seven_day"),
    ("currentweek", "seven_day"),
    ("fable", "seven_day_fable"),
    ("opus", "seven_day_opus"),
)


def _heim_vorbereiten() -> None:
    """Legt die eigene Ablage an, damit die Sitzung ohne Rückfragen startet.

    Ohne diese Vorbereitung bleibt die Oberfläche im Einstieg stehen und
    fragt nach Farbschema, Anmeldeweg und Ordnervertrauen — **und
    verbraucht dabei die Eingabe**, die eigentlich ``/usage`` lauten sollte.
    Genau daran sind die ersten beiden Versuche gescheitert.
    """
    HEIM.mkdir(parents=True, exist_ok=True)
    marke = HEIM / ".claude.json"
    if marke.exists():
        return
    import json as _j
    marke.write_text(_j.dumps({
        "hasCompletedOnboarding": True,
        "theme": "dark",
        "projects": {str(HEIM): {"hasTrustDialogAccepted": True,
                                 "allowedTools": [], "history": []}},
    }), encoding="utf-8")


def _bildschirm_holen(cli: str) -> str:
    """Fährt die Sitzung, tippt ``/usage`` und gibt den Bildschirm zurück."""
    _heim_vorbereiten()
    pid, fd = pty.fork()
    if pid == 0:                                     # Kindprozess
        os.environ["TERM"] = "xterm-256color"
        os.environ["COLUMNS"] = "100"
        os.environ["LINES"] = "50"
        os.environ["HOME"] = str(HEIM)
        os.chdir(str(HEIM))
        os.execv(cli, [cli])
    stuecke: list[str] = []
    start = time.time()
    getippt_um = None
    try:
        while time.time() - start < FRIST_S:
            r, _, _ = select.select([fd], [], [], 0.5)
            if r:
                try:
                    d = os.read(fd, 65536)
                except OSError:
                    break
                if not d:
                    break
                stuecke.append(d.decode("utf-8", "replace"))
            if getippt_um is None and time.time() - start > WARTEN_VOR_EINGABE_S:
                # Zeichen für Zeichen — die Oberfläche verschluckt sonst Teile.
                for ch in b"/usage":
                    os.write(fd, bytes([ch]))
                    time.sleep(0.12)
                time.sleep(1.5)
                os.write(fd, b"\r")
                getippt_um = time.time()
            if getippt_um and time.time() - getippt_um > WARTEN_NACH_EINGABE_S:
                break
    finally:
        try:
            os.write(fd, b"\x03\x03")
            time.sleep(0.2)
        except Exception:
            pass
        for schliessen in (lambda: os.close(fd), lambda: os.kill(pid, 9)):
            try:
                schliessen()
            except Exception:
                pass
        # **Einsammeln, nicht einmal nachsehen** (Engywuck-Befund 21.08.):
        # ``WNOHANG`` direkt nach dem ``kill`` verpasst das Kind, wenn es noch
        # nicht gestorben ist — und hinterlässt je Abfrage einen Zombie, bis
        # der nächtliche Neustart aufräumt. Kurz wiederholt kostet nichts und
        # trifft den Normalfall sofort.
        for _ in range(20):
            try:
                weg, _st = os.waitpid(pid, os.WNOHANG)
                if weg:
                    break
            except ChildProcessError:
                break
            except Exception:
                break
            time.sleep(0.05)
    return _ANSI.sub("", "".join(stuecke))


def _fenster_zuordnen(vorlauf: str) -> str | None:
    """Welches Fenster gehört zu einem Prozentwert?

    Gesucht wird **rückwärts** vom Fundort: Die Überschrift steht vor dem
    Balken. Genommen wird die **späteste** passende Überschrift, sonst würde
    bei mehreren Abschnitten immer die erste gewinnen.
    """
    flach = re.sub(r"[\s│┃|]+", "", vorlauf).lower()
    beste, bester_platz = None, -1
    for marke, name in _ABSCHNITTE:
        platz = flach.rfind(marke)
        if platz > bester_platz:
            beste, bester_platz = name, platz
    return beste if bester_platz >= 0 else None


def auslesen(cli: str) -> dict[str, dict]:
    """Der Stand je Fenster: ``{fenster: {anteil, resets_text}}``.

    Leeres Ergebnis heißt **nicht gelesen** — nie geraten.
    """
    text = _bildschirm_holen(cli)
    ergebnis: dict[str, dict] = {}
    for m in _PROZENT.finditer(text):
        wert = int(m.group(1))
        if not 0 <= wert <= 100:
            continue
        fenster = _fenster_zuordnen(text[max(0, m.start() - 400):m.start()])
        if not fenster or fenster in ergebnis:
            continue
        nach = text[m.end():m.end() + 200]
        rm = _RESET.search(nach)
        ergebnis[fenster] = {
            "anteil": wert / 100.0,
            "resets_text": rm.group(1).strip(" .,") if rm else "",
        }
    return ergebnis


if __name__ == "__main__":
    import sys
    from pprint import pprint
    pprint(auslesen(sys.argv[1]))
