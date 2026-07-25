#!/usr/bin/env python3
# <!-- ROLLE: test-stundenblumen -->
"""Verhaltenstest Stundenblumen — die dauerlaufende Belegkette.

Die Eigenschaft, an der alles hängt: **Das Ausbleiben der Übergabe ist der
Alarm.** Dazu die Gegenprobe, die genauso wichtig ist — in Ruhezeiten schweigt
die Kette, sonst glaubt ihr bald niemand mehr.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="blumen-"))
os.environ["BLUMEN_DIR"] = str(_TMP / "blumen")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["ALLOWED_USER_IDS"] = "304455165"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import stundenblume as sb  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _leeren():
    for p in (sb.KETTE, sb.RUHE):
        if p.exists():
            p.unlink()
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if out.exists():
        for f in out.glob("*.json"):
            f.unlink()
    sb._befunde = lambda: []


def _meldungen():
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if not out.exists():
        return []
    return [json.loads(f.read_text(encoding="utf-8"))["text"]
            for f in sorted(out.glob("*.json"))]


# Ein Zeitpunkt außerhalb der Ruhestunde, damit die Tageszeit nichts verfälscht.
def _t(versatz=0.0):
    basis = time.mktime(time.struct_time(
        (2026, 7, 25, 14, 0, 0, 4, 206, -1)))
    return basis + versatz


def _kette_waechst_verkettet():
    _leeren()
    a = sb.bluehen(_t(0))
    b = sb.bluehen(_t(60))
    assert a["vorher"] == "—", "die erste Blume zeigt auf etwas"
    assert b["vorher"] == a["abdruck"], "die Kette ist nicht verkettet"
    assert b["abdruck"] != a["abdruck"], "zwei Glieder mit gleichem Abdruck"
    e = sb.kette_pruefen(_t(120))
    assert e["ok"] and e["brueche"] == 0, f"frische Kette gilt als kaputt: {e}"


def _luecke_ist_der_alarm():
    """Der Kern: Nicht der Befund meldet sich, sondern die Lücke."""
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(sb.TOLERANZ_S + 600))     # zehn Minuten zu spät
    m = _meldungen()
    assert m, "die Lücke hat keinen Alarm ausgelöst"
    assert "Lücke" in m[0] and "niemand belegt" in m[0], \
        f"die Meldung benennt die Lücke nicht: {m[0]}"


def _kurze_luecke_schweigt():
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(sb.TOLERANZ_S - 30))
    assert not _meldungen(), "eine Lücke innerhalb der Toleranz hat gemeldet"


def _ruhe_schweigt():
    """Ein Wächter, dem niemand mehr glaubt, ist schlimmer als keiner."""
    _leeren()
    sb.bluehen(_t(0))
    sb.ruhe_setzen(30)
    e = sb.bluehen(_t(sb.TOLERANZ_S + 900))
    assert e["ruhe"], "die Ruhe wurde nicht erkannt"
    assert not _meldungen(), "in der Ruhezeit wurde Alarm geschlagen"


def _nachtfenster_schweigt():
    _leeren()
    nachts = time.mktime(time.struct_time((2026, 7, 25, 4, 10, 0, 4, 206, -1)))
    sb.bluehen(nachts - 3600)
    e = sb.bluehen(nachts)
    assert e["ruhe"] == "nächtliches Wartungsfenster", \
        f"das Hygiene-Fenster gilt nicht als Ruhe: {e['ruhe']!r}"
    assert not _meldungen(), "im Wartungsfenster wurde Alarm geschlagen"


def _stillstand_faellt_auf():
    """Steht die Kette, sagt die Prüfung es — auch ohne neue Blume."""
    _leeren()
    sb.bluehen(_t(0))
    e = sb.kette_pruefen(_t(sb.TOLERANZ_S + 1200))
    assert not e["ok"], "eine stillstehende Kette gilt als in Ordnung"
    assert "steht still" in e["grund"], f"Grund unklar: {e['grund']}"


def _manipulation_wird_sichtbar():
    """Manipulations-SICHTBAR, nicht -sicher — genau das wird geprüft."""
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(60))
    sb.bluehen(_t(120))
    zeilen = sb.KETTE.read_text(encoding="utf-8").splitlines()
    mitte = json.loads(zeilen[1])
    mitte["befunde"] = ["nachträglich hineingeschrieben"]
    zeilen[1] = json.dumps(mitte, ensure_ascii=False)
    sb.KETTE.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    e = sb.kette_pruefen(_t(130))
    assert not e["ok"] and e["brueche"] >= 1, \
        f"die veränderte Kette gilt als unversehrt: {e}"
    assert "sichtbar gemacht, nicht verhindert" in e["grund"], \
        "die Meldung überzeichnet die Schutzwirkung"


def _befunde_melden_sich():
    _leeren()
    sb._befunde = lambda: ["Bot-Prozess nicht vorhanden"]
    sb.bluehen(_t(0))
    m = _meldungen()
    assert m and "Bot-Prozess" in m[0], f"Befund nicht gemeldet: {m}"


def _kein_modellaufruf_im_modul():
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    for verdacht in ("claude_agent_sdk", "anthropic", "ClaudeSDKClient",
                     "requests", "urlopen"):
        assert verdacht not in quelle, \
            f"eine Blume darf nichts Teures tun, fand aber: {verdacht}"


check("Kette wächst und ist verkettet", _kette_waechst_verkettet)
check("die Lücke ist der Alarm", _luecke_ist_der_alarm)
check("kurze Lücke schweigt", _kurze_luecke_schweigt)
check("angeordnete Ruhe schweigt", _ruhe_schweigt)
check("nächtliches Wartungsfenster schweigt", _nachtfenster_schweigt)
check("Stillstand fällt bei der Prüfung auf", _stillstand_faellt_auf)
check("Veränderung wird sichtbar (nicht verhindert)", _manipulation_wird_sichtbar)
check("echte Befunde melden sich", _befunde_melden_sich)
check("kein Modell- und kein Netzaufruf im Modul", _kein_modellaufruf_im_modul)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle Stundenblumen-Tests bestanden.")
