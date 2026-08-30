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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# **[NEU 30.08.] Fehlt das Werkzeug, wird das GESAGT — nicht die Quittung
# beschuldigt.** Ohne rsync meldete dieser Prüfer zwei Zeilen rot, die beide
# auf die Quittungslogik zeigten; das fehlende Werkzeug kam nirgends vor.
if not shutil.which("rsync"):
    print("⏭️ rsync fehlt auf dieser Maschine — die Quittung wurde NICHT "
          "GEMESSEN (kein Fehlschlag, aber auch kein Bestehen)")
    sys.exit(77)

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
    """Das echte Skript, mit umgebogenen Pfaden.

    ## `[GEÄNDERT 30.08.]` Rückgabewert und Fehlerstrom werden ausgewertet

    **Fächer-Fund [71].** Vorher warf diese Funktion beides weg. Fehlte
    `rsync`, lief das Skript durch, kopierte nichts und endete mit 0 — und
    dieser Prüfer meldete daraufhin zwei Zeilen rot, die beide die
    **Quittungslogik** beschuldigten. Das fehlende Werkzeug kam nirgends vor.

    *Ein Prüfer mit falschem Schild ist teurer als einer, der schweigt:* Er
    schickt den Suchenden an die falsche Stelle. In diesem Projekt hätte das
    eine Stunde gekostet.
    """
    umgebung = dict(os.environ)
    umgebung.update({
        "LOG_SYNC_SRC": str(SRC),
        "LOG_SYNC_REPO": str(REPO),
        "LOG_SYNC_WORK": str(WORK),
        "HOME": str(_TMP),
    })
    e = subprocess.run(["bash", str(ROOT / "scripts" / "log_sync.sh")],
                       env=umgebung, capture_output=True, text=True)
    # **Geduldet wird GENAU EIN Abbruch: der Push ohne Gegenstelle.** Der
    # Wegwerf-Baum hat kein `origin`, das Skript endet dort mit 128 — das ist
    # der Aufbau, nicht ein Befund. Erst gemessen, dann eingegrenzt: Mein
    # erster Anlauf verwarf jeden Rückgabewert ungleich null und machte damit
    # den gewollten Abbruch zum Fehlschlag. **Eine Ausnahme, die einen
    # bekannten Fall benennt, ist tragfähig; eine, die eine Zahlenliste
    # pflegt, veraltet** — deshalb hängt sie am Wortlaut der Gegenstelle.
    push_ohne_gegenstelle = "Could not read from remote repository" in (e.stderr or "")
    if e.returncode != 0 and not push_ohne_gegenstelle:
        raise RuntimeError(
            f"log_sync.sh endete mit {e.returncode}: "
            + (e.stderr or e.stdout or "ohne Ausgabe").strip()[-300:])
    # Auch bei Rückgabewert 0 kann der Fehlerstrom das Entscheidende tragen —
    # genau so verhielt sich das Skript ohne rsync.
    if "command not found" in (e.stderr or ""):
        raise RuntimeError(
            "log_sync.sh vermisst ein Werkzeug: " + e.stderr.strip()[-300:])


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
