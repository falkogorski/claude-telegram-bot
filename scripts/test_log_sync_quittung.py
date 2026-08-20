#!/usr/bin/env python3
# <!-- ROLLE: test-log-sync-quittung -->
"""Verhaltenstest der Abgleich-Quittung — **das Skript läuft echt.**

**Zwei Befunde Engywucks vom 20.08.**, beide gemessen und beide seine eigenen
Abnahmefehler: Die Ausschluss-Liste lief über den **ganzen** Arbeitsbaum
(5.207 Zeilen, 564 KB), und die Quittung wurde bei **jedem** Lauf neu
geschrieben, weil ihre Kopfzeile die Uhrzeit trägt — 155 Commits an einem
halben Tag.

**Warum das mehr ist als Kosmetik:** Der Sinn der Quittung war, aussortierte
Dateien **sichtbar** zu machen. Eine Liste mit fünftausend Zeilen liest
niemand, und was niemand liest, meldet nichts. Und ein Verlauf, in dem jeder
Eintrag dasselbe sagt, verdeckt die Änderungen, die etwas bedeuten.

Gefahren wird gegen einen Wegwerf-Baum: eigener Arbeitsordner, eigenes
Log-Repo, kein Netz, kein `git push` (das Skript bricht beim Push ab — für
diese Prüfungen genügt, was **vorher** geschieht).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_TMP = Path(tempfile.mkdtemp(prefix="quittung-"))
WORK = _TMP / "workspace"
REPO = _TMP / "logrepo"
SRC = _TMP / "bot" / "logs" / "conversations"
for d in (WORK, REPO, SRC):
    d.mkdir(parents=True, exist_ok=True)

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _git(*args):
    subprocess.run(["git", *args], cwd=REPO, capture_output=True, check=False)


_git("init", "-q")
_git("config", "user.email", "t@t")
_git("config", "user.name", "Test")


def _lauf() -> None:
    """Das echte Skript, mit umgebogenen Pfaden."""
    umgebung = dict(os.environ)
    umgebung.update({
        "LOG_SYNC_SRC": str(SRC),
        "LOG_SYNC_REPO": str(REPO),
        "LOG_SYNC_WORK": str(WORK),
        "HOME": str(_TMP),
    })
    subprocess.run(["bash", str(ROOT / "scripts" / "log_sync.sh")],
                   env=umgebung, capture_output=True)


def _quittung() -> str:
    p = WORK / "letzter-abgleich.txt"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _vorbereiten():
    for f in WORK.rglob("*"):
        if f.is_file():
            f.unlink()
    (SRC / "2026-08-20.md").write_text("Gespräch\n", encoding="utf-8")


# ── Die Prüfungen ───────────────────────────────────────────────────────────
def _nur_transportrelevantes_wird_als_ausgeschlossen_gemeldet():
    """**Engywucks erster Befund.** Punkt-Dateien und Zwischenprodukte sind
    kein Befund, sondern die Absicht — sie gehören nicht in eine Liste, die
    Aufmerksamkeit verlangt."""
    _vorbereiten()
    (WORK / "bericht.md").write_text("kommt mit\n", encoding="utf-8")
    (WORK / ".zwischenstand").write_text("egal\n", encoding="utf-8")
    # **Ein verstecktes VERZEICHNIS mit harmlos benannten Dateien darin.**
    # Genau das hat den ersten Fix ueberlebt: Der Filter sah nur den
    # Dateinamen, rsync schliesst aber den ganzen Pfad aus — 120 Zeilen
    # Pip-Metadaten mit dem Vermerk „bitte melden, das sollte mitkommen".
    (WORK / ".pdfenv" / "lib").mkdir(parents=True, exist_ok=True)
    (WORK / ".pdfenv" / "lib" / "top_level.txt").write_text("x", encoding="utf-8")
    (WORK / "arbeit.tmp").write_text("egal\n", encoding="utf-8")
    (WORK / "bild.png").write_bytes(b"\x89PNG")
    (WORK / "mein-token-plan.md").write_text("heikel\n", encoding="utf-8")
    _lauf()
    q = _quittung()
    assert q, "es wurde gar keine Quittung geschrieben"
    kopf, _, rumpf = q.partition("AUSGESCHLOSSEN")
    for still in (".zwischenstand", "arbeit.tmp", "bild.png", "top_level.txt"):
        assert still not in rumpf, \
            f"{still} steht in der Ausschluss-Liste, obwohl es nie vorgesehen war"
    # Die Gegenrichtung: Der Geheimnis-Filter bleibt SICHTBAR.
    assert "mein-token-plan.md" in rumpf, \
        "der Geheimnis-Filter arbeitet wieder lautlos"
    assert "bericht.md" in kopf, "die mitgenommene Datei fehlt unter MITGENOMMEN"


def _gleiche_lage_schreibt_die_quittung_nicht_neu():
    """**Engywucks zweiter Befund.** Nur der Zeitstempel ändert sich — das ist
    keine Änderung, sondern eine Uhr."""
    _vorbereiten()
    (WORK / "bericht.md").write_text("kommt mit\n", encoding="utf-8")
    _lauf()
    vorher = (WORK / "letzter-abgleich.txt").stat().st_mtime_ns
    erste = _quittung()
    _lauf()
    nachher = (WORK / "letzter-abgleich.txt").stat().st_mtime_ns
    assert vorher == nachher, \
        "die Quittung wurde neu geschrieben, obwohl sich nichts geändert hat"
    assert _quittung() == erste, "der Inhalt hat sich verändert"


def _echte_aenderung_schreibt_sehr_wohl():
    """**Die Gegenrichtung, und ohne sie wäre der Fix gefährlich:** Eine
    Quittung, die sich nie mehr ändert, meldet auch echte Änderungen nicht."""
    _vorbereiten()
    (WORK / "bericht.md").write_text("kommt mit\n", encoding="utf-8")
    _lauf()
    erste = _quittung()
    (WORK / "neuer-bericht.md").write_text("auch neu\n", encoding="utf-8")
    _lauf()
    zweite = _quittung()
    assert zweite != erste, "eine echte Änderung wurde nicht quittiert"
    assert "neuer-bericht.md" in zweite, "die neue Datei fehlt in der Quittung"


def _die_quittung_bleibt_lesbar_kurz():
    """Ein Maß statt eines Gefühls: Die Ausschluss-Liste zählt nur, was ein
    Mensch tatsächlich durchsehen würde."""
    _vorbereiten()
    for i in range(200):
        (WORK / f".arbeit-{i}").write_text("x", encoding="utf-8")
    (WORK / "eins.md").write_text("mit\n", encoding="utf-8")
    _lauf()
    zeilen = _quittung().count("\n")
    assert zeilen < 40, f"die Quittung ist wieder aufgeblaeht: {zeilen} Zeilen"


check("nur Transportrelevantes gilt als ausgeschlossen",
      _nur_transportrelevantes_wird_als_ausgeschlossen_gemeldet)
check("gleiche Lage schreibt die Quittung NICHT neu",
      _gleiche_lage_schreibt_die_quittung_nicht_neu)
check("eine echte Änderung schreibt sehr wohl (Gegenrichtung)",
      _echte_aenderung_schreibt_sehr_wohl)
check("die Quittung bleibt lesbar kurz", _die_quittung_bleibt_lesbar_kurz)

print()
if fails:
    print(f"❌ {len(fails)} Quittungs-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Quittungs-Tests bestanden.")
