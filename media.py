# <!-- ROLLE: medien-aufbereitung -->
"""H1 — transporttaugliche Aufbereitung von Bildern und Videos.

**Warum es das gibt (Befund 24.07.2026):** Adam schickte ein Foto; der Bot
antwortete viermal „JSON message exceeded maximum buffer size of 1048576
bytes" und starb danach in einen Sitzungs-Neustart — rund zwölf Minuten lang
sah es für ihn aus wie „der Bot nimmt keine Nachrichten mehr an". Die Grenze
ist eine **Transportgrenze** der SDK-Nachricht zwischen CLI-Unterprozess und
Python-Seite, KEINE Fähigkeitsgrenze: dasselbe Bild wurde später problemlos
gelesen. Große Bilder und Videos müssen also verarbeitbar bleiben — das ist
die Vorgabe, nicht der Kompromiss.

**Vorgehen (Conni-Auftrag 25.07., H1 a–e):**

a) Das **Original bleibt unangetastet** — es wird nie überschrieben oder
   verkleinert; die Transport-Fassung ist immer eine zusätzliche Datei.
b) Für die Modell-Übergabe entsteht eine Fassung, die **so groß wie möglich
   und so klein wie nötig** ist — bemessen am tatsächlich gesetzten Puffer,
   nicht an einer geratenen Zahl.
c) Der Puffer wird **zuerst hochgesetzt** (`ClaudeAgentOptions.max_buffer_size`)
   und erst danach verkleinert; Verkleinern ist die zweite Wahl, nicht die
   erste.
d) Reicht das nicht (sehr große Vorlagen, Videos): Übergabe **in Teilen** —
   Einzelbilder plus Tonspur statt einer Abweisung.
e) Nie ein Sitzungsabsturz: greift nichts, gibt es eine ehrliche Meldung.

Bewusst **deterministisch und ohne Modell-Aufruf** (AGB-Leitplanke) und ohne
neue pip-Abhängigkeit: ffmpeg/ffprobe liegen auf Mac und VPS ohnehin vor
(Tonspur-Verarbeitung). Alles hier ist reine Rechenarbeit — keine Kosten.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

# Base64 bläht Binärdaten auf vier Drittel auf; dazu kommt der JSON-Rahmen des
# Werkzeug-Ergebnisses. 1.45 ist der bewusst großzügig gewählte Faktor.
_BASE64_FACTOR = 1.45
# Vom Puffer wird nur ein Teil verplant — im selben Turn laufen weitere
# Nachrichten über dieselbe Leitung. Ein randvoll ausgereizter Puffer wäre
# genau der Fehler, den wir gerade abstellen.
_BUDGET_SHARE = 0.45

# Kantenlängen und Qualitätsstufen, die der Reihe nach probiert werden —
# absteigend, damit die ERSTE passende Fassung zugleich die größte ist.
_EDGES = (3200, 2600, 2000, 1600, 1200, 900, 640)
_QUALITIES = (3, 5, 7)          # ffmpeg -q:v (kleiner = besser)

_FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
_FFPROBE = shutil.which("ffprobe") or "ffprobe"


def tools_available() -> bool:
    """True, wenn ffmpeg UND ffprobe aufrufbar sind."""
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def transport_budget(max_buffer_bytes: int) -> int:
    """Wie viele Byte Rohdaten dürfen in EINE Werkzeug-Antwort — am Puffer bemessen."""
    return max(64 * 1024, int(max_buffer_bytes * _BUDGET_SHARE / _BASE64_FACTOR))


def _run(args: list[str], timeout: int = 120) -> tuple[bool, str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return p.returncode == 0, (p.stderr or "")[-800:]
    except FileNotFoundError:
        return False, "ffmpeg/ffprobe nicht gefunden"
    except subprocess.TimeoutExpired:
        return False, "Zeitüberschreitung"
    except Exception as e:                                   # pragma: no cover
        return False, str(e)


def probe_duration(path: Path) -> float:
    """Spieldauer in Sekunden (0.0, wenn nicht ermittelbar)."""
    ok, _ = True, None
    try:
        p = subprocess.run(
            [_FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60)
        if p.returncode != 0:
            return 0.0
        return float(json.loads(p.stdout).get("format", {}).get("duration") or 0.0)
    except Exception:
        return 0.0


def prepare_image(path: Path, budget: int, *, out_dir: Path | None = None) -> dict:
    """Liefert eine transporttaugliche Fassung des Bildes.

    Rückgabe: ``{"ok", "path", "shrunk", "orig_bytes", "bytes", "note", "error"}``
    Das Original unter ``path`` wird niemals verändert.
    """
    path = Path(path)
    res: dict = {"ok": False, "path": path, "shrunk": False, "orig_bytes": 0,
                 "bytes": 0, "note": "", "error": ""}
    try:
        res["orig_bytes"] = path.stat().st_size
    except OSError as e:
        res["error"] = f"Datei nicht lesbar: {e}"
        return res

    # (b/c) Passt es ohnehin in den (bereits erhöhten) Puffer → Original nehmen.
    if res["orig_bytes"] <= budget:
        res.update(ok=True, bytes=res["orig_bytes"],
                   note="Original in Originalgröße übergeben")
        return res

    if not tools_available():
        res["error"] = "ffmpeg fehlt — Bild kann nicht transporttauglich verkleinert werden"
        return res

    target_dir = Path(out_dir) if out_dir else path.parent
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        res["error"] = f"Zielordner nicht anlegbar: {e}"
        return res
    out = target_dir / f"{path.stem}-transport.jpg"

    # Größte Fassung zuerst — die erste, die passt, gewinnt.
    for edge in _EDGES:
        for q in _QUALITIES:
            ok, err = _run([
                _FFMPEG, "-y", "-v", "error", "-i", str(path),
                "-vf", f"scale='min({edge},iw)':'min({edge},ih)'"
                       ":force_original_aspect_ratio=decrease",
                "-q:v", str(q), str(out)])
            if not ok or not out.exists():
                continue
            size = out.stat().st_size
            if size <= budget:
                res.update(ok=True, path=out, shrunk=True, bytes=size,
                           note=f"für die Übergabe verkleinert auf max. {edge} px "
                                f"({size / 1_048_576:.1f} MB statt "
                                f"{res['orig_bytes'] / 1_048_576:.1f} MB)")
                return res
    res["error"] = ("Bild ließ sich auch stark verkleinert nicht unter die "
                    "Transportgrenze bringen")
    return res


# Abtastdichte nach Laufzeit (Adam 25.07.: „bei 30 Sekunden jedes Sekundenbild,
# bei zwei Minuten mindestens alle zwei Sekunden; bei langen Videos darf es
# abnehmen"). Erster Eintrag, dessen Grenze passt, gewinnt.
_DICHTE: tuple[tuple[float, float], ...] = (
    (30, 1.0),      # bis 30 s   → jede Sekunde
    (180, 2.0),     # bis 3 min   → alle 2 s
    (600, 3.0),     # bis 10 min  → alle 3 s
    (1800, 5.0),    # bis 30 min  → alle 5 s
    (float("inf"), 10.0),
)
# Ein Kontaktbogen fasst bis zu so viele Einzelbilder in EIN Übersichtsbild.
_BOGEN_SPALTEN = 5
_BOGEN_ZEILEN = 6
_BOGEN_KANTE = 320          # Kantenlänge je Kachel im Bogen


def abtastabstand(dauer: float) -> float:
    """Sekunden zwischen zwei Einzelbildern — laufzeitabhängig."""
    for grenze, abstand in _DICHTE:
        if dauer <= grenze:
            return abstand
    return _DICHTE[-1][1]


def _kontaktboegen(frames: list[Path], zeiten: list[float],
                   ziel: Path) -> list[Path]:
    """Fasst die Einzelbilder zu Übersichtsbögen zusammen.

    **Der Kniff, der den Zielkonflikt auflöst:** Feine Abtastung und ein
    schlanker Kontext schließen sich nur aus, wenn jedes Einzelbild einzeln
    übergeben wird. Ein Bogen zeigt dreißig Momente in EINEM Bild — das Modell
    überblickt damit den ganzen Ablauf und liest nur dort ein Einzelbild nach,
    wo tatsächlich etwas passiert.
    """
    boegen: list[Path] = []
    je_bogen = _BOGEN_SPALTEN * _BOGEN_ZEILEN
    for i in range(0, len(frames), je_bogen):
        teil = frames[i:i + je_bogen]
        liste = ziel / f".bogen-{i // je_bogen + 1}.txt"
        try:
            liste.write_text("".join(f"file '{p.name}'\n" for p in teil),
                             encoding="utf-8")
        except OSError:
            continue
        out = ziel / f"uebersicht-{i // je_bogen + 1:02d}.jpg"
        ok, _ = _run([
            _FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
            "-i", str(liste), "-vf",
            f"scale={_BOGEN_KANTE}:{_BOGEN_KANTE}:force_original_aspect_ratio=decrease,"
            f"pad={_BOGEN_KANTE}:{_BOGEN_KANTE}:-1:-1:color=black,"
            f"tile={_BOGEN_SPALTEN}x{_BOGEN_ZEILEN}",
            "-frames:v", "1", "-q:v", "4", str(out)], timeout=180)
        try:
            liste.unlink()
        except OSError:
            pass
        if ok and out.exists():
            boegen.append(out)
    return boegen


def prepare_video(path: Path, budget: int, *, out_dir: Path | None = None,
                  max_frames: int = 400, sekunden_je_bild: float | None = None) -> dict:
    """(d) Zerlegt ein Video in übergebbare Teile: Einzelbilder + Tonspur.

    Rückgabe: ``{"ok", "frames": [Path], "audio": Path|None, "duration",
    "note", "error"}``. Das Original bleibt unangetastet.
    """
    path = Path(path)
    res: dict = {"ok": False, "frames": [], "boegen": [], "audio": None,
                 "zeitmarken": None, "takt": 0.0, "duration": 0.0,
                 "note": "", "error": ""}
    if not tools_available():
        res["error"] = "ffmpeg fehlt — Video kann nicht in Teile zerlegt werden"
        return res

    dur = probe_duration(path)
    res["duration"] = dur
    target_dir = Path(out_dir) if out_dir else path.parent / f"{path.stem}-teile"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        res["error"] = f"Zielordner nicht anlegbar: {e}"
        return res

    abstand = sekunden_je_bild if sekunden_je_bild else abtastabstand(dur)
    n = max(3, min(max_frames, int(dur / abstand) + 1)) if dur > 0 else 3
    # ⚠️ Das Budget gilt **je Bild**, nicht geteilt durch die Anzahl (Korrektur
    # 25.07. nach Adams Rückfrage): Jedes Einzelbild wandert als EIGENE
    # Werkzeug-Antwort durch die Leitung — sie teilen sich die Weite also nie.
    # Vorher wurden Bilder umso kleiner, je länger das Video war; bei zwölf
    # Bildern wäre jedes auf ein Zwölftel geschrumpft, ohne jeden Grund.
    # Nach oben gedeckelt, damit viele Bilder nicht den Sitzungs-Kontext fluten
    # — das ist die eigentliche Schranke bei Serien, nicht der Transport.
    per_frame_budget = max(256 * 1024, min(budget, 2 * 1024 * 1024))

    # EIN Durchlauf statt eines ffmpeg-Aufrufs je Bild: Bei feiner Abtastung
    # sind das schnell hundert Bilder, und hundertmal neu zu positionieren
    # dauerte ein Vielfaches. Die Bildrate `1/abstand` liefert genau die
    # gewünschte Dichte, die Skalierung hält die Einzelbilder handlich.
    takt = max(0.2, (dur / n) if dur > 0 else abstand)
    _run([_FFMPEG, "-y", "-v", "error", "-i", str(path),
          "-vf", f"fps=1/{takt:.4f},scale='min(1600,iw)':-2",
          "-frames:v", str(n), "-q:v", "3",
          str(target_dir / "bild-%04d.jpg")], timeout=600)
    zeiten: list[float] = []
    for i, raw in enumerate(sorted(target_dir.glob("bild-*.jpg"))):
        shot = prepare_image(raw, per_frame_budget, out_dir=target_dir)
        if shot["ok"]:
            res["frames"].append(Path(shot["path"]))
            zeiten.append(i * takt)

    # Übersichtsbögen + Verzeichnis mit Zeitmarken: Das Modell sieht den ganzen
    # Ablauf auf wenigen Bildern und liest gezielt nach, wo etwas passiert.
    if res["frames"]:
        res["boegen"] = _kontaktboegen(res["frames"], zeiten, target_dir)
        try:
            (target_dir / "zeitmarken.txt").write_text(
                "".join(f"{int(t) // 60:02d}:{int(t) % 60:02d}  {p.name}\n"
                        for t, p in zip(zeiten, res["frames"])),
                encoding="utf-8")
            res["zeitmarken"] = target_dir / "zeitmarken.txt"
        except OSError:
            pass
    res["takt"] = takt

    # Tonspur separat — sie geht später durch die vorhandene Spracherkennung.
    audio = target_dir / "tonspur.ogg"
    ok, _ = _run([_FFMPEG, "-y", "-v", "error", "-i", str(path), "-vn",
                  "-c:a", "libopus", "-b:a", "32k", str(audio)])
    if ok and audio.exists() and audio.stat().st_size > 1024:
        res["audio"] = audio

    if not res["frames"] and res["audio"] is None:
        res["error"] = "weder Einzelbilder noch Tonspur konnten gewonnen werden"
        return res

    teile = []
    if res["boegen"]:
        teile.append(f"{len(res['boegen'])} Übersichtsbögen")
    if res["frames"]:
        teile.append(f"{len(res['frames'])} Einzelbilder "
                     f"(alle {res['takt']:.1f} s)")
    if res["audio"]:
        teile.append("Tonspur")
    res.update(ok=True, note="in Teilen übergeben: " + " und ".join(teile))
    return res


def env_max_buffer(default: int = 32 * 1024 * 1024) -> int:
    """(c) Puffergröße für die SDK-Verbindung — per Umgebung überschreibbar."""
    try:
        v = int(os.environ.get("SDK_MAX_BUFFER_BYTES") or 0)
        return v if v >= 1_048_576 else default
    except ValueError:
        return default
