#!/usr/bin/env python3
# <!-- ROLLE: stundenblumen -->
"""Stundenblumen — die dauerlaufende Belegkette.

**Das Problem, das sie lösen:** Alle bisherigen Prüfungen sind
**Zeitpunkt**-Prüfungen — der 4-Uhr-Check, der Selbstcheck beim Start, der
Regressionslauf. Steht der Prüfer selbst still, merkt es niemand. Ein Wächter,
der schweigt, ist von einem Wächter, der nichts zu melden hat, nicht zu
unterscheiden.

**Die Umkehrung:** Kurze, billige Prüfläufe in dichter Folge, die einander
anstoßen. **Das Ausbleiben der Übergabe ist selbst der Alarm.** Nicht der Befund
meldet sich, sondern die Lücke.

**Warum das minütlich geht:** Eine Blume ruft **kein Modell** auf. Sie kostet
nichts und darf deshalb laufen, so oft sie will. Sieht sie etwas Auffälliges,
weckt sie ein Modell — billig immer, teuer nur bei Anlass.

**Die Kette ist git-artig, keine Blockchain.** Jede Blume trägt den Fingerabdruck
der vorigen; eine nachträglich veränderte Blume bricht die Kette sichtbar.
**Ehrlich dazu:** Das ist manipulations-**sichtbar**, nicht manipulations-**sicher**
— wer die ganze Kette neu rechnet, hinterlässt keine Spur. Für unser Problem
genügt das: Wir sichern gegen **Ausfall und Versehen**, nicht gegen einen
Fälscher im eigenen Haus. Blockchain löst Misstrauen zwischen Fremden; dieses
Problem haben wir nicht. Die Stufe darüber wären signierte Commits — vorgemerkt,
nicht jetzt.

**Ruhezeiten von Anfang an.** Neustart, Wartung, Netzhänger dürfen **keinen**
Alarm auslösen. Ein Wächter, dem niemand mehr glaubt, ist schlimmer als keiner —
deshalb sind die Ruhefenster Teil des ersten Entwurfs, nicht ein späterer Aufsatz.

**Die Rollen bleiben getrennt:** Hora **arbeitet** · die Stundenblumen **belegen,
dass das System lebt** · Kassiopeia **prüft Inhalte**.

Aufruf: ``python3 scripts/stundenblume.py`` (je Lauf eine Blume)
        ``python3 scripts/stundenblume.py --pruefen`` (Kette bewerten, für 8.1)
        ``python3 scripts/stundenblume.py --ruhe 20`` (20 Minuten Ruhe)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ZUSTAND = Path(os.environ.get("BLUMEN_DIR")
               or (Path.home() / ".claude" / "stundenblumen"))
KETTE = ZUSTAND / "kette.jsonl"
RUHE = ZUSTAND / "ruhe_bis"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"

# Takt und Toleranz. Die Toleranz ist bewusst großzügig: Lieber eine Lücke
# übersehen als jede Woche ein Fehlalarm — Vertrauen ist die knappere Ressource.
TAKT_S = int(os.environ.get("BLUMEN_TAKT") or 60)
TOLERANZ_S = int(os.environ.get("BLUMEN_TOLERANZ") or 300)
# Das nächtliche Hygiene-Fenster (04:00) ist ein bekannter Unterbruch.
RUHE_STUNDEN = {4}


def _in_ruhe(jetzt: float | None = None) -> str:
    """Warum gerade keine Meldung fällig ist — leerer Text heißt: keine Ruhe."""
    jetzt = jetzt or time.time()
    try:
        bis = float(RUHE.read_text(encoding="utf-8").strip())
        if jetzt < bis:
            rest = int((bis - jetzt) / 60)
            return f"angeordnete Ruhe (noch {rest} min)"
    except Exception:
        pass
    if time.localtime(jetzt).tm_hour in RUHE_STUNDEN:
        return "nächtliches Wartungsfenster"
    return ""


def ruhe_setzen(minuten: int) -> None:
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    RUHE.write_text(str(time.time() + minuten * 60), encoding="utf-8")


def _letzte() -> dict | None:
    try:
        with KETTE.open("rb") as f:
            f.seek(0, 2)
            groesse = f.tell()
            f.seek(max(0, groesse - 4096))
            zeilen = f.read().decode("utf-8", "replace").splitlines()
        for z in reversed(zeilen):
            if z.strip():
                return json.loads(z)
    except Exception:
        return None
    return None


def _fingerabdruck(eintrag: dict) -> str:
    roh = json.dumps({k: eintrag[k] for k in sorted(eintrag) if k != "abdruck"},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(roh.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------- die Prüfungen --
def _befunde() -> list[str]:
    """Billige, deterministische Prüfungen — kein Modell, kein Netz.

    Bewusst klein gehalten: Eine Blume, die eine Minute rechnet, ist keine
    Blume mehr. Was teuer zu prüfen ist, gehört in den 4-Uhr-Check.
    """
    raus: list[str] = []
    # 1. Lebt der Bot? (die verlässliche Auskunft, nicht die selbstzählende)
    if shutil.which("systemctl"):
        try:
            p = subprocess.run(["systemctl", "show", "claude-telegram-bot",
                                "-p", "MainPID", "--value"],
                               capture_output=True, text=True, timeout=10)
            pid = (p.stdout or "").strip()
            if not pid or pid == "0":
                raus.append("Bot-Prozess nicht vorhanden")
        except Exception as e:
            raus.append(f"Dienst nicht abfragbar: {e}")
    # 2. Läuft die Platte voll?
    try:
        s = os.statvfs("/")
        frei = s.f_bavail * s.f_frsize / (1024 ** 3)
        if frei < 5:
            raus.append(f"nur noch {frei:.1f} GiB Plattenplatz frei")
    except Exception:
        pass
    # 3. Staut sich das Boten-Postfach? (ein Zeichen, dass der Bot nicht arbeitet)
    try:
        wartend = len(list(POSTFACH.glob("*.json")))
        if wartend > 20:
            raus.append(f"{wartend} unzugestellte Postfach-Aufträge")
    except Exception:
        pass
    return raus


def bluehen(jetzt: float | None = None) -> dict:
    """Eine Blume: Lücke bewerten, prüfen, Glied anhängen, ggf. melden."""
    jetzt = jetzt or time.time()
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    vorige = _letzte()
    ruhegrund = _in_ruhe(jetzt)

    luecke = None
    if vorige is not None:
        luecke = jetzt - float(vorige.get("zeit", jetzt))

    eintrag = {
        "zeit": round(jetzt, 3),
        "menschlich": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(jetzt)),
        "vorher": (vorige or {}).get("abdruck", "—"),
        "luecke_s": round(luecke, 1) if luecke is not None else None,
        "ruhe": ruhegrund,
        "befunde": _befunde(),
    }
    eintrag["abdruck"] = _fingerabdruck(eintrag)
    try:
        with KETTE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # Melden: nur bei echtem Anlass, nie in der Ruhe.
    if not ruhegrund:
        gruende = list(eintrag["befunde"])
        if luecke is not None and luecke > TOLERANZ_S:
            gruende.insert(0, f"Die Kette hatte eine Lücke von "
                              f"{luecke / 60:.0f} Minuten — in dieser Zeit hat "
                              "niemand belegt, dass das System lebt.")
        if gruende:
            melden("🌼 Stundenblume " + eintrag["menschlich"] + ":\n• "
                   + "\n• ".join(gruende))
    return eintrag


def kette_pruefen(jetzt: float | None = None) -> dict:
    """Bewertet die Kette — für den 4-Uhr-Check (8.1).

    Prüft zweierlei: **Ist sie frisch?** (blüht überhaupt noch etwas) und **ist
    sie unversehrt?** (passen die Fingerabdrücke aneinander).
    """
    jetzt = jetzt or time.time()
    if not KETTE.exists():
        return {"ok": False, "grund": "Es gibt noch keine Kette."}
    letzte = _letzte()
    if letzte is None:
        return {"ok": False, "grund": "Die Kette ist leer."}
    alter = jetzt - float(letzte.get("zeit", 0))
    frisch = alter <= TOLERANZ_S or bool(_in_ruhe(jetzt))

    # Unversehrtheit — zwei Prüfungen, und die zweite ist die eigentliche:
    #   (a) zeigt jedes Glied auf das vorige?
    #   (b) passt der gespeicherte Abdruck noch zum INHALT des Glieds?
    # Ohne (b) wäre die Kette Zierde: Wer ein Glied verändert, ohne seinen
    # Abdruck anzufassen, bliebe unsichtbar — genau das hat der erste Testlauf
    # am 25.07. aufgedeckt. Ein Fingerabdruck, der nie nachgerechnet wird,
    # belegt nichts.
    brueche, vorher = 0, None
    try:
        with KETTE.open(encoding="utf-8") as f:
            for z in f:
                if not z.strip():
                    continue
                e = json.loads(z)
                if _fingerabdruck(e) != e.get("abdruck"):
                    brueche += 1                      # (b) Inhalt verändert
                elif vorher is not None and e.get("vorher") != vorher:
                    brueche += 1                      # (a) Glied ausgetauscht
                vorher = e.get("abdruck")
    except Exception as e:
        return {"ok": False, "grund": f"Kette nicht lesbar: {e}"}

    ok = frisch and brueche == 0
    grund = ""
    if not frisch:
        grund = (f"Die jüngste Blume ist {alter / 60:.0f} Minuten alt — "
                 "die Kette steht still.")
    elif brueche:
        grund = (f"{brueche} Bruchstelle(n) in der Kette — ein Glied zeigt nicht "
                 "auf das vorige. Das ist sichtbar gemacht, nicht verhindert.")
    return {"ok": ok, "grund": grund, "alter_s": round(alter),
            "brueche": brueche}


def melden(text: str) -> None:
    ziel = (os.environ.get("ALLOWED_USER_IDS") or "").split(",")[0].strip()
    if not ziel.isdigit():
        try:
            prefs = json.loads((Path.home() / ".config" / "claude-telegram-bot"
                                / "prefs.json").read_text(encoding="utf-8"))
            ziel = next((str(k) for k in prefs if str(k).isdigit()), "")
        except Exception:
            ziel = ""
    if not ziel.isdigit():
        return
    try:
        POSTFACH.mkdir(parents=True, exist_ok=True)
        tmp = POSTFACH / f".blume{time.time_ns()}.tmp"
        tmp.write_text(json.dumps({"target_chat_id": int(ziel), "text": text},
                                  ensure_ascii=False), encoding="utf-8")
        tmp.rename(POSTFACH / f"blume-{time.time_ns()}.json")
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Stundenblumen — Belegkette")
    ap.add_argument("--pruefen", action="store_true", help="Kette bewerten")
    ap.add_argument("--ruhe", type=int, metavar="MINUTEN",
                    help="Ruhefenster setzen (kein Alarm)")
    a = ap.parse_args()
    if a.ruhe:
        ruhe_setzen(a.ruhe)
        print(f"Ruhe für {a.ruhe} Minuten gesetzt.")
        return 0
    if a.pruefen:
        e = kette_pruefen()
        print(("✅ Kette lebt" if e["ok"] else f"❌ {e['grund']}")
              + f" (jüngste Blume vor {e.get('alter_s', '?')} s, "
                f"{e.get('brueche', 0)} Bruchstelle(n))")
        return 0 if e["ok"] else 1
    e = bluehen()
    print(f"🌼 {e['menschlich']} · {e['abdruck']} · "
          + (", ".join(e["befunde"]) if e["befunde"] else "nichts Auffälliges")
          + (f" · {e['ruhe']}" if e["ruhe"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
