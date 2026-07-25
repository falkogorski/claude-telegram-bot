#!/usr/bin/env python3
# <!-- ROLLE: entscheidungs-protokoll -->
"""9.4 — trägt gefällte Urteile als datierte Zeilen ins Drehbuch.

**Das ist der Ablageweg selbst.** Der Bot fällt die Urteile entgegen, darf aber
das Repo nicht beschreiben (8.7). Also legt er sie als Dateien ab, und dieses
Werkzeug — **außerhalb** des Bot-Prozesses, wie der Nachzieher (C1) — überträgt
sie. Ohne diesen Schritt bliebe jede Entscheidung im Bot-Gedächtnis liegen, bis
ein Mensch sie abtippt; genau so ist der Gesamtdaumen fürs Phasen-Audit
verlorengegangen.

**Es schreibt nur eine Sorte Zeile**, und zwar in einen eigenen Abschnitt am
Ende des Drehbuchs. Kein Fließtext aus fremder Feder, keine Änderung an
bestehenden Zeilen — damit ein untergeschobenes Urteil höchstens eine
Protokollzeile erzeugen kann und niemals eine Regel verändert.

Aufruf: ``python3 scripts/entscheidungs_protokoll.py [--repo …] [--commit]``
Deterministisch, ohne Modell-Aufruf, ohne Kosten.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import freigaben  # noqa: E402

UEBERSCHRIFT = "## Entscheidungs-Protokoll (9.4)"
KOPF = f"""
{UEBERSCHRIFT}

Automatisch geführt: Jedes Urteil aus dem Freigabe-Postfach landet hier als
datierte Zeile — **auch ein bloßes 👍 im Bot-Chat**. Eine Entscheidung, die
keinen Weg in die Ablage hat, ist verloren.

| Zeitpunkt | Urteil | Sache | Ampel | Herkunft | beantwortet von |
|---|---|---|---|---|---|
"""

# Was in eine Tabellenzelle darf: kein Zeilenumbruch, kein senkrechter Strich
# (der würde die Tabelle sprengen), keine Steuerzeichen.
_UNSAUBER = re.compile(r"[|\n\r\x00-\x1f]")


def _zelle(text: str, laenge: int = 90) -> str:
    return _UNSAUBER.sub(" ", str(text or "")).strip()[:laenge] or "—"


def zeile(e: dict) -> str:
    sym = {"freigegeben": "✅", "abgelehnt": "⛔"}.get(e.get("urteil"), "❔")
    ampel = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}.get(e.get("ampel"), "⬜")
    grund = _zelle(e.get("grund", ""), 60)
    sache = _zelle(e.get("titel", ""), 70)
    if grund and grund != "—":
        sache = f"{sache} — {grund}"
    return (f"| {_zelle(e.get('beantwortet_am'), 20)} "
            f"| {sym} {_zelle(e.get('urteil'), 14)} "
            f"| {sache} "
            f"| {ampel} "
            f"| {_zelle(e.get('herkunft'), 30)} "
            f"| {_zelle(e.get('beantwortet_von'), 30)} |\n")


def _einfuegen(text: str, neue: str) -> str:
    """Hängt die Zeilen ans ENDE DES ABSCHNITTS — nicht ans Dateiende.

    **Warum das mehr als Feinschliff ist:** Vorher stand hier „der Abschnitt
    steht am Dateiende, also genügt Anhängen." Das war eine **Annahme über das
    Layout einer fremden Datei**, keine geprüfte Eigenschaft. Landet je ein
    Abschnitt dahinter, wandern neue Protokollzeilen still in den falschen —
    und ein Protokoll, dessen Zeilen anderswo auftauchen, ist schlimmer als
    keines, weil niemand den Fehler bemerkt.

    Deshalb wird die Stelle jetzt **gesucht statt unterstellt**: Zeilen gehen
    unmittelbar vor die nächste Überschrift nach dem Protokoll-Abschnitt; gibt
    es keine, ans Dateiende — dann stimmt die alte Annahme ja tatsächlich.
    """
    start = text.find(UEBERSCHRIFT)
    if start < 0:                       # Abschnitt fehlt: KOPF wurde eben erst
        return text.rstrip("\n") + "\n" + neue   # angehängt, Ende ist richtig
    zeilen = text.splitlines(keepends=True)
    # Zeilennummer der Überschrift bestimmen …
    lauf, beginn = 0, 0
    for i, z in enumerate(zeilen):
        if lauf >= start:
            beginn = i
            break
        lauf += len(z)
    else:
        beginn = len(zeilen)
    # … und die nächste Überschrift danach suchen.
    grenze = len(zeilen)
    for i in range(beginn + 1, len(zeilen)):
        if re.match(r"^#{1,6}\s", zeilen[i]):
            grenze = i
            break
    while grenze > beginn + 1 and not zeilen[grenze - 1].strip():
        grenze -= 1                     # Leerzeilen vor der Überschrift wahren
    kopf = "".join(zeilen[:grenze]).rstrip("\n") + "\n"
    rest = "".join(zeilen[grenze:])
    return kopf + neue + (("\n" + rest.lstrip("\n")) if rest.strip() else "")


def uebertragen(repo: Path, schreiben: bool = True) -> list[str]:
    """Hängt alle offenen Urteile an. Rückgabe: übertragene Kennungen."""
    offen = freigaben.protokoll_offen()
    if not offen:
        return []
    ziel = repo / "MIGRATION.md"
    if not ziel.exists():
        raise FileNotFoundError(f"Drehbuch nicht gefunden: {ziel}")
    text = ziel.read_text(encoding="utf-8")
    if UEBERSCHRIFT not in text:
        text = text.rstrip("\n") + "\n\n---\n" + KOPF
    neue = "".join(zeile(e) for e in offen)
    text = _einfuegen(text, neue)
    if schreiben:
        ziel.write_text(text, encoding="utf-8")
        for e in offen:
            freigaben.protokoll_erledigt(e["kennung"])
    return [e["kennung"] for e in offen]


def main() -> int:
    ap = argparse.ArgumentParser(description="9.4 Entscheidungs-Protokoll")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--pruefen", action="store_true",
                    help="nur zeigen, was übertragen würde")
    a = ap.parse_args()
    try:
        kennungen = uebertragen(Path(a.repo), schreiben=not a.pruefen)
    except Exception as e:
        print(f"❌ {e}")
        return 2
    if not kennungen:
        print("Nichts zu übertragen — keine offenen Urteile.")
        return 0
    print(("geprüft" if a.pruefen else "übertragen") +
          f": {len(kennungen)} Urteil(e) — {', '.join(kennungen)}")
    if a.commit and not a.pruefen:
        try:
            subprocess.run(["git", "add", "MIGRATION.md"], cwd=a.repo,
                           check=True, capture_output=True, timeout=60)
            p = subprocess.run(
                ["git", "commit", "-m",
                 f"Entscheidungs-Protokoll (9.4): {len(kennungen)} Urteil(e)"],
                cwd=a.repo, capture_output=True, text=True, timeout=120)
            print("✅ committet" if p.returncode == 0
                  else f"⚠️ Commit fehlgeschlagen: {(p.stdout + p.stderr)[-300:]}")
        except Exception as e:
            print(f"⚠️ Commit fehlgeschlagen: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
