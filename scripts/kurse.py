#!/usr/bin/env python3
# <!-- ROLLE: kurs-transkription -->
"""Kurs-Videos: vom Mac auf den VPS, dort lokal transkribiert, in die Wissensablage.

`[NEU 24.09.2026]` Adams Entscheid (Engywucks Zettel F2, 06:0x): **ja** zum
Vorschlag aus dem Nachtbericht — Adam kopiert per `rsync` in einen
Eingangsordner, der VPS transkribiert **lokal mit faster-whisper** und legt
unter `wissen/kurse/` ab. **Nie über einen Fremddienst; Adams Material bleibt
auf Mac und VPS.**

Was daraus folgt, und jede Zeile hat einen Grund:

- **Kein Modellaufruf.** faster-whisper läuft auf dem VPS, ohne Netz, ohne
  Kosten. Eine Zusammenfassung wäre ein Modelllauf — die gibt es nur auf
  Adams Frage, nicht hier.
- **Der Eingang wird nur gelesen.** Nichts wird verschoben oder gelöscht: Es
  ist Adams Material, und Löschen fragt man vorher. Was erledigt ist, steht in
  einer eigenen Stand-Datei (Größe und Änderungszeit — ändert sich die Datei,
  wird neu transkribiert).
- **`wissen/kurse/` reist nicht ins Log-Archiv**: Der Log-Abgleich pusht nach
  GitHub, und GitHub ist ein Fremddienst. `log_sync.sh` schließt `kurse/` aus.
- **Rücksicht auf den Bot:** Die Sprachnachrichten des Bots nutzen dieselben
  vier Kerne. Deshalb läuft dieser Lauf mit niedrigster Priorität (`nice 19`)
  und zwei Fäden, und nur einer zugleich (Sperrdatei).
- **Wer merkt es, wenn es liegen bleibt?** Der Tagescheck fragt `--pruefen`:
  Liegt ein Video länger als sechs Stunden unverarbeitet oder ist es
  gescheitert, geht das an Adam.

Aufruf: `kurse.py` (verarbeitet alles Neue) · `kurse.py --pruefen` (für den
Tagescheck, schreibt nichts).
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

ENDUNGEN = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi",
            ".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac"}
# Ab wann ein unverarbeitetes Video ein Befund ist.
FRIST_S = 6 * 3600
# Ein Absatz in der Mitschrift je so viele Sekunden — mit Sprungmarke davor.
ABSATZ_S = 60
HERKUNFT = ("Adams eigenes Kursmaterial, per rsync vom Mac auf den VPS; "
            "transkribiert auf dem VPS mit faster-whisper, nie über einen Fremddienst")


def eingang() -> Path:
    return Path(os.environ.get("KURSE_EINGANG") or Path.home() / "kurse-eingang")


def stand_datei() -> Path:
    return Path(os.environ.get("KURSE_STAND") or Path.home() / ".claude" / "kurse-stand.json")


def stand_laden() -> dict:
    try:
        return json.loads(stand_datei().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def stand_schreiben(stand: dict) -> None:
    p = stand_datei()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(stand, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def finden() -> "list[Path]":
    """Alle Medien im Eingang. Versteckte Dateien fallen weg — so legt rsync
    seine halb übertragenen an, bevor es sie umbenennt."""
    wurzel = eingang()
    if not wurzel.is_dir():
        return []
    return sorted(p for p in wurzel.rglob("*")
                  if p.is_file() and p.suffix.lower() in ENDUNGEN
                  and not any(teil.startswith(".") for teil in p.relative_to(wurzel).parts))


def _merkmal(p: Path) -> dict:
    s = p.stat()
    return {"groesse": s.st_size, "mtime": int(s.st_mtime)}


def offen(stand: dict) -> "list[Path]":
    """Was noch nicht (oder nicht in dieser Fassung) transkribiert ist."""
    wurzel = eingang()
    aus = []
    for p in finden():
        e = stand.get(p.relative_to(wurzel).as_posix()) or {}
        if e.get("status") != "fertig" or {k: e.get(k) for k in ("groesse", "mtime")} != _merkmal(p):
            aus.append(p)
    return aus


def zeitmarke(s: float) -> str:
    s = int(s)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def als_text(segmente: "list[tuple[float, str]]") -> str:
    """Absätze von etwa einer Minute, jeder mit Sprungmarke."""
    absaetze, aktuell, beginn = [], [], None
    for start, text in segmente:
        text = (text or "").strip()
        if not text:
            continue
        if beginn is None:
            beginn = start
        if start - beginn >= ABSATZ_S and aktuell:
            absaetze.append(f"[{zeitmarke(beginn)}] " + " ".join(aktuell))
            aktuell, beginn = [], start
        aktuell.append(text)
    if aktuell:
        absaetze.append(f"[{zeitmarke(beginn or 0)}] " + " ".join(aktuell))
    return "\n\n".join(absaetze)


def whisper_transkribierer(stufe: str | None = None):
    """Der echte Rand: faster-whisper, lokal. Liest das Video direkt (PyAV) —
    keine Zwischendatei."""
    from faster_whisper import WhisperModel     # noqa: PLC0415
    import transcribe                           # noqa: PLC0415
    stufe = stufe or os.environ.get("KURSE_STUFE") or os.environ.get("STT_MODEL_SIZE") or "small"
    name = transcribe.FasterWhisperTranscriber._STUFEN.get(stufe, stufe)
    modell = WhisperModel(name, device="cpu", compute_type="int8",
                          cpu_threads=int(os.environ.get("KURSE_THREADS") or 2))
    sprache = os.environ.get("KURSE_SPRACHE") or None

    def lauf(pfad: Path) -> "list[tuple[float, str]]":
        segmente, _info = modell.transcribe(str(pfad), language=sprache,
                                            beam_size=5, vad_filter=True)
        return [(s.start, s.text) for s in segmente]
    lauf.stufe = name
    return lauf


def verarbeiten(transkribierer=None, *, heute: str | None = None) -> "list[dict]":
    """Alles Offene transkribieren. Der Stand wird NACH JEDEM Video
    geschrieben — ein Abbruch mitten in einer Reihe verliert nichts Fertiges."""
    import wissen                               # noqa: PLC0415
    stand = stand_laden()
    liste = offen(stand)
    if not liste:
        return []
    transkribierer = transkribierer or whisper_transkribierer()
    stufe = getattr(transkribierer, "stufe", "?")
    wurzel = eingang()
    ergebnisse = []
    for p in liste:
        rel = p.relative_to(wurzel).as_posix()
        kurs = p.relative_to(wurzel).parts[0] if len(p.relative_to(wurzel).parts) > 1 else "Kurs"
        eintrag = {**_merkmal(p), "zeit": time.strftime("%Y-%m-%d %H:%M:%S")}
        try:
            segmente = transkribierer(p)
            text = als_text(segmente)
            if not text:
                raise ValueError("keine Sprache erkannt")
            ziel = wissen.ablegen(
                titel=p.stem, quelle=kurs, adresse=f"Kurs-Eingang: {rel}",
                datum=heute or date.today().isoformat(),
                grundlage=f"Transkript, lokal mit faster-whisper ({stufe})",
                herkunft=HERKUNFT, text=text, bereich="kurse")
            eintrag.update(status="fertig", ziel=str(ziel),
                           dauer_min=round((segmente[-1][0] if segmente else 0) / 60))
        except Exception as e:                  # ein Video darf die Reihe nicht aufhalten
            eintrag.update(status="fehler", grund=f"{type(e).__name__}: {e}"[:200])
        stand[rel] = eintrag
        stand_schreiben(stand)
        ergebnisse.append({"datei": rel, **eintrag})
    return ergebnisse


def meldung(ergebnisse: "list[dict]") -> str:
    fertig = [e for e in ergebnisse if e["status"] == "fertig"]
    fehler = [e for e in ergebnisse if e["status"] != "fertig"]
    teile = []
    if fertig:
        minuten = sum(e.get("dauer_min", 0) for e in fertig)
        teile.append(f"📚 {len(fertig)} Kurs-Video(s) transkribiert, zusammen etwa "
                     f"{minuten} Minuten. Liegen in der Wissensablage unter kurse/:\n"
                     + "\n".join(f"· {e['datei']}" for e in fertig))
    if fehler:
        teile.append(f"⚠️ {len(fehler)} Kurs-Video(s) nicht transkribiert:\n"
                     + "\n".join(f"· {e['datei']} — {e.get('grund', '')}" for e in fehler))
    return "\n\n".join(teile)


def pruefen(jetzt: float | None = None) -> str:
    """Für den Tagescheck, nur lesend: `OK …`, `LIEGT …` oder `FEHLER …`."""
    jetzt = jetzt or time.time()
    stand = stand_laden()
    wurzel = eingang()
    fehler = [rel for rel, e in stand.items() if e.get("status") == "fehler"
              and (wurzel / rel).exists()]
    liegt = [p.relative_to(wurzel).as_posix() for p in offen(stand)
             if p.relative_to(wurzel).as_posix() not in fehler
             and jetzt - p.stat().st_mtime > FRIST_S]
    if fehler:
        return f"FEHLER {len(fehler)}: " + ", ".join(fehler[:5])
    if liegt:
        return f"LIEGT {len(liegt)}: " + ", ".join(liegt[:5])
    fertig = sum(1 for e in stand.values() if e.get("status") == "fertig")
    return f"OK {fertig} transkribiert, nichts liegt"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()
    if a.pruefen:
        print(pruefen())
        return 0
    sperre = stand_datei().with_suffix(".lock")
    sperre.parent.mkdir(parents=True, exist_ok=True)
    with sperre.open("w") as h:
        try:
            fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("läuft bereits")
            return 0
        try:
            os.nice(19)
        except OSError:
            pass
        ergebnisse = verarbeiten()
        text = meldung(ergebnisse)
        print(text or "nichts Neues im Eingang")
        if text:
            import botenpost                    # noqa: PLC0415
            botenpost.legen(text, "kurse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
