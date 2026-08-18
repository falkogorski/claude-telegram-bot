#!/usr/bin/env python3
# <!-- ROLLE: test-medien -->
"""Verhaltenstest H1 — großer Bild- und Videofall (Conni-Auftrag 25.07.).

Erzeugt mit ffmpeg selbst eine große Vorlage und ein kurzes Video; prüft dann,
dass die Aufbereitung sie unter die Transportgrenze bringt, das Original dabei
unangetastet lässt und ein Video in Teile zerlegt. Kein Netz, kein Modell-Aufruf.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import media  # noqa: E402

fails = []
TMP = Path(tempfile.mkdtemp(prefix="mediatest-"))


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


if not media.tools_available():
    print("⚠ ffmpeg/ffprobe fehlen — H1-Test übersprungen (kein Fehlschlag)")
    sys.exit(0)


def _make_image(path: Path, w=4000, h=3000) -> None:
    """Rauschbild — lässt sich kaum komprimieren, taugt daher als großer Fall."""
    media._run([media._FFMPEG, "-y", "-v", "error", "-f", "lavfi",
                "-i", f"nullsrc=s={w}x{h}", "-vf",
                "geq=random(1)*255:128:128", "-frames:v", "1",
                "-q:v", "1", str(path)])


def _make_video(path: Path, seconds=6) -> None:
    media._run([media._FFMPEG, "-y", "-v", "error",
                "-f", "lavfi", "-i", f"testsrc=size=640x480:rate=15:d={seconds}",
                "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(path)])


BIG = TMP / "gross.jpg"
_make_image(BIG)
assert BIG.exists() and BIG.stat().st_size > 0, "Testbild konnte nicht erzeugt werden"
BIG_BYTES = BIG.stat().st_size


# --- Haushalt: Budget wächst mit dem Puffer, bleibt aber darunter -----------
def _budget_folgt_puffer():
    klein = media.transport_budget(1 * 1024 * 1024)
    gross = media.transport_budget(32 * 1024 * 1024)
    assert gross > klein * 10, "Budget folgt dem Puffer nicht"
    assert gross < 32 * 1024 * 1024, "Budget schöpft den Puffer voll aus (kein Spielraum)"


# --- Passt es schon: Original unangetastet durchreichen ---------------------
def _passt_bleibt_original():
    r = media.prepare_image(BIG, BIG_BYTES + 1, out_dir=TMP / "out1")
    assert r["ok"], r["error"]
    assert not r["shrunk"], "unnötig verkleinert"
    assert Path(r["path"]) == BIG, "Pfad zeigt nicht auf das Original"


# --- Zu groß: verkleinerte Zweitfassung, Original unberührt ----------------
def _zu_gross_wird_verkleinert():
    budget = max(60_000, BIG_BYTES // 8)
    r = media.prepare_image(BIG, budget, out_dir=TMP / "out2")
    assert r["ok"], r["error"]
    assert r["shrunk"], "es wurde nicht verkleinert"
    assert r["bytes"] <= budget, f"Zweitfassung immer noch zu groß: {r['bytes']} > {budget}"
    assert Path(r["path"]) != BIG, "das Original wurde als Transportfassung ausgegeben"
    assert BIG.stat().st_size == BIG_BYTES, "das ORIGINAL wurde verändert!"
    assert Path(r["path"]).exists(), "Transportfassung fehlt auf der Platte"


# --- „so groß wie möglich": großzügiges Budget ⇒ größere Fassung -----------
def _so_gross_wie_moeglich():
    knapp = media.prepare_image(BIG, 80_000, out_dir=TMP / "out3")
    weit = media.prepare_image(BIG, max(300_000, BIG_BYTES // 3), out_dir=TMP / "out4")
    assert knapp["ok"] and weit["ok"], "eine der beiden Fassungen fehlt"
    assert weit["bytes"] > knapp["bytes"], \
        "größeres Budget führte nicht zu einer größeren Fassung"


# --- Unlesbare Vorlage: ehrlicher Fehler statt Absturz ---------------------
def _fehlt_wird_ehrlich():
    r = media.prepare_image(TMP / "gibtsnicht.jpg", 1_000_000, out_dir=TMP / "out5")
    assert not r["ok"], "nicht vorhandene Datei galt als erfolgreich"
    assert r["error"], "kein Klartext-Grund geliefert"


# --- Video: in Teile zerlegt (Einzelbilder + Tonspur) ----------------------
VID = TMP / "clip.mp4"
_make_video(VID)


def _video_wird_zerlegt():
    assert VID.exists(), "Testvideo konnte nicht erzeugt werden"
    r = media.prepare_video(VID, media.transport_budget(32 * 1024 * 1024),
                            out_dir=TMP / "teile")
    assert r["ok"], r["error"]
    assert len(r["frames"]) >= 3, f"zu wenige Einzelbilder: {len(r['frames'])}"
    assert all(Path(p).exists() for p in r["frames"]), "Einzelbild fehlt auf der Platte"
    assert r["audio"] is not None and Path(r["audio"]).exists(), "Tonspur fehlt"
    assert r["duration"] > 0, "Laufzeit nicht ermittelt"


def _videoteile_passen_ins_budget():
    budget = 400_000
    r = media.prepare_video(VID, budget, out_dir=TMP / "teile2")
    assert r["ok"], r["error"]
    for p in r["frames"]:
        assert Path(p).stat().st_size <= max(262_144, budget), \
            f"Einzelbild sprengt das Budget: {p}"


def _budget_gilt_je_bild():
    """Korrektur 25.07.: Mehr Bilder duerfen die einzelnen NICHT schrumpfen.

    Jedes Bild geht als eigene Werkzeug-Antwort durch die Leitung — sie teilen
    sich deren Weite nie. Vorher wurde durch die Anzahl geteilt.
    """
    budget = media.transport_budget(32 * 1024 * 1024)
    wenige = media.prepare_video(VID, budget, out_dir=TMP / "wenige", max_frames=3)
    viele = media.prepare_video(VID, budget, out_dir=TMP / "viele",
                                max_frames=24, sekunden_je_bild=1)
    assert wenige["ok"] and viele["ok"], "eine der beiden Zerlegungen fehlt"
    assert len(viele["frames"]) > len(wenige["frames"]), \
        "die feinere Zerlegung lieferte nicht mehr Bilder"
    gr_wenige = max(Path(p).stat().st_size for p in wenige["frames"])
    gr_viele = max(Path(p).stat().st_size for p in viele["frames"])
    assert gr_viele >= gr_wenige * 0.9, \
        (f"mehr Bilder machten die einzelnen kleiner ({gr_viele} < {gr_wenige}) "
         "— das Budget wird faelschlich geteilt")


def _dichte_nach_adams_vorgabe():
    """Adam 25.07.: 30 s → jede Sekunde, 2 min → mindestens alle 2 Sekunden."""
    assert media.abtastabstand(30) <= 1.0, "30-Sekunden-Video nicht sekundengenau"
    assert media.abtastabstand(120) <= 2.0, "Zwei-Minuten-Video gröber als 2 s"
    assert media.abtastabstand(130) <= 2.0, "knapp über 2 min fällt zu grob ab"
    # Bei langen Videos darf es abnehmen — aber nicht ins Grobe kippen.
    assert media.abtastabstand(1800) <= 5.0, "halbe Stunde gröber als 5 s"
    assert media.abtastabstand(3600) <= 10.0, "eine Stunde gröber als 10 s"
    # Monoton: länger darf nie feiner werden.
    werte = [media.abtastabstand(d) for d in (10, 30, 120, 300, 900, 1800, 5400)]
    assert werte == sorted(werte), f"Staffelung nicht monoton: {werte}"


def _uebersichtsboegen_entstehen():
    """Der Kniff gegen den Zielkonflikt: viele Bilder, wenige Übergaben."""
    r = media.prepare_video(VID, media.transport_budget(32 * 1024 * 1024),
                            out_dir=TMP / "boegen")
    assert r["ok"], r["error"]
    assert r["boegen"], "keine Übersichtsbögen erzeugt"
    assert all(Path(b).exists() for b in r["boegen"]), "Bogen fehlt auf der Platte"
    assert len(r["boegen"]) < len(r["frames"]), \
        "die Bögen fassen nicht zusammen (so viele Bögen wie Bilder)"
    assert r["zeitmarken"] and Path(r["zeitmarken"]).exists(), \
        "kein Zeitmarken-Verzeichnis — gezieltes Nachlesen wäre Raten"
    zeilen = Path(r["zeitmarken"]).read_text(encoding="utf-8").splitlines()
    assert len(zeilen) == len(r["frames"]), "Zeitmarken decken nicht alle Bilder ab"
    assert ":" in zeilen[0] and ".jpg" in zeilen[0], f"Zeitmarke unbrauchbar: {zeilen[0]}"



def _ausschnitt_ist_schaerfer():
    """Nachtrag V ④: Details als Ausschnitt in Originalauflösung.

    Der Nachweis, auf den es ankommt: Der Ausschnitt trägt MEHR Bildpunkte je
    Fläche als die verkleinerte Gesamtfassung — sonst hilft er bei
    Kleingedrucktem nicht.
    """
    budget = 400_000
    gesamt = media.prepare_image(BIG, budget, out_dir=TMP / "asA")
    assert gesamt["ok"] and gesamt["shrunk"], "Testaufbau: Bild wurde nicht verkleinert"
    feld = media.ausschnitt(BIG, budget, spalte=2, zeile=2, out_dir=TMP / "asB")
    assert feld["ok"], feld["error"]
    assert Path(feld["path"]).exists(), "Ausschnitt fehlt auf der Platte"
    assert BIG.stat().st_size == BIG_BYTES, "das ORIGINAL wurde verändert!"

    def _kanten(p):
        aus = media._run([media._FFPROBE, "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height", "-of", "csv=p=0",
                          str(p)])
        return aus

    # Ein Neuntel der Fläche bei ähnlichem Budget ⇒ deutlich feinere Auflösung.
    import subprocess
    def _breite(p):
        r = subprocess.run([media._FFPROBE, "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True)
        return int((r.stdout or "0").strip() or 0)
    b_gesamt, b_feld = _breite(gesamt["path"]), _breite(feld["path"])
    # Das Feld zeigt ein Drittel der Bildbreite. Damit es schärfer ist, muss
    # seine Pixelbreite mehr als ein Drittel der Gesamt-Pixelbreite betragen.
    assert b_feld > b_gesamt / 3, \
        (f"Ausschnitt ist nicht feiner als die Gesamtfassung "
         f"(Feld {b_feld} px für ein Drittel Bildbreite, Gesamt {b_gesamt} px)")


def _ausschnitt_bleibt_im_raster():
    """Unsinnige Felder werden begrenzt, nicht abgelehnt — und nie geraten."""
    a = media.ausschnitt(BIG, 2_000_000, spalte=99, zeile=0, out_dir=TMP / "asC")
    assert a["ok"], a["error"]
    assert "3" in a["note"], f"Rasterangabe fehlt in der Notiz: {a['note']}"

check("Budget folgt dem Puffer, ohne ihn auszuschöpfen", _budget_folgt_puffer)
check("passendes Bild bleibt Original", _passt_bleibt_original)
check("großes Bild wird verkleinert, Original unberührt", _zu_gross_wird_verkleinert)
check("so groß wie möglich, so klein wie nötig", _so_gross_wie_moeglich)
check("fehlende Vorlage → ehrlicher Grund", _fehlt_wird_ehrlich)
check("Video wird in Einzelbilder + Tonspur zerlegt", _video_wird_zerlegt)
check("Videoteile passen einzeln ins Budget", _videoteile_passen_ins_budget)
check("Budget gilt je Bild, nicht geteilt", _budget_gilt_je_bild)
check("Abtastdichte nach Adams Vorgabe", _dichte_nach_adams_vorgabe)
check("Übersichtsbögen + Zeitmarken entstehen", _uebersichtsboegen_entstehen)
check("Ausschnitt ist feiner als die Gesamtfassung", _ausschnitt_ist_schaerfer)
check("Ausschnitt bleibt im Raster", _ausschnitt_bleibt_im_raster)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle H1-Medientests bestanden.")
