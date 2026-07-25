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


def prepare_video(path: Path, budget: int, *, out_dir: Path | None = None,
                  max_frames: int = 24, sekunden_je_bild: int = 10) -> dict:
    """(d) Zerlegt ein Video in übergebbare Teile: Einzelbilder + Tonspur.

    Rückgabe: ``{"ok", "frames": [Path], "audio": Path|None, "duration",
    "note", "error"}``. Das Original bleibt unangetastet.
    """
    path = Path(path)
    res: dict = {"ok": False, "frames": [], "audio": None, "duration": 0.0,
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

    # Ein Bild je ~10 Sekunden, mindestens drei, höchstens max_frames.
    n = max(3, min(max_frames, int(dur // sekunden_je_bild) + 1)) if dur > 0 else 3
    # ⚠️ Das Budget gilt **je Bild**, nicht geteilt durch die Anzahl (Korrektur
    # 25.07. nach Adams Rückfrage): Jedes Einzelbild wandert als EIGENE
    # Werkzeug-Antwort durch die Leitung — sie teilen sich die Weite also nie.
    # Vorher wurden Bilder umso kleiner, je länger das Video war; bei zwölf
    # Bildern wäre jedes auf ein Zwölftel geschrumpft, ohne jeden Grund.
    # Nach oben gedeckelt, damit viele Bilder nicht den Sitzungs-Kontext fluten
    # — das ist die eigentliche Schranke bei Serien, nicht der Transport.
    per_frame_budget = max(256 * 1024, min(budget, 2 * 1024 * 1024))

    for i in range(n):
        # Zeitpunkte gleichmäßig verteilt, Rand gemieden (Schwarzbilder).
        ts = (dur * (i + 0.5) / n) if dur > 0 else i * 1.0
        raw = target_dir / f"bild-{i + 1:02d}.jpg"
        ok, _ = _run([_FFMPEG, "-y", "-v", "error", "-ss", f"{ts:.2f}",
                      "-i", str(path), "-frames:v", "1", "-q:v", "4", str(raw)])
        if not ok or not raw.exists():
            continue
        shot = prepare_image(raw, per_frame_budget, out_dir=target_dir)
        if shot["ok"]:
            res["frames"].append(Path(shot["path"]))

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
    if res["frames"]:
        teile.append(f"{len(res['frames'])} Einzelbilder")
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
