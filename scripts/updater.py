#!/usr/bin/env python3
# <!-- ROLLE: updater -->
"""Updater — Gegenstück zum Versions-Monitor (5.21). WENDET Updates AN.

Strikt getrennt vom Monitor (der ERKENNT). Ebenfalls **deterministisch, KEIN
Modell-Aufruf**. Ampel-Klassifikation aus SemVer + Pin-Liste:
  🟢 grün  = Patch/Minor, nicht gepinnt → sammelbar (eine Sammelfreigabe).
  🟡 gelb  = bewusst gepinnt → nie automatisch, nur Einzel-Freigabe im Fenster.
  🔴 rot   = Major-Sprung → nie automatisch, Einzel-Freigabe + Rollback-Ansage.
  manual   = OS/whisper.cpp/lobe-chat/pandoc … → nicht Updater-Sache.

Sicherheits-Kette (Conni-Härtung 25.07., A1–A7):
  A5  Grundlinie ZUERST messen — ist das Fundament nicht grün, wird NICHTS
      angefasst („erst reparieren"). Bewertung danach per **Delta**, nie absolut.
  A1  Vollständigen Umgebungsstand einfrieren (`pip freeze`) — nicht nur die
      Register-Versionen; sonst bleiben transitive Mitzieher beim Rollback oben.
  A3  Exakt die **freigegebene** Version installieren (`==`). Weicht sie vom
      Anzeige-Stand ab → nicht einspielen, neu fragen.
  A4  Lauf-Schloss: nur ein Updater-Lauf gleichzeitig (pip auf einem venv).
  A2  Rollback-Fehler werden LAUT gemeldet, mit Zustand je Paket — nie „ausgeführt"
      behaupten, wenn er scheiterte.
  A6  Gleiche Testzahl vor und nach dem Rollback → ausdrücklich sagen, dass die
      Ursache NICHT am Update lag.
  A7  Wiederhol-Schutz: gleiches Paket, gleiches Ergebnis, unveränderte
      Grundlinie → nicht erneut einspielen, sondern die Ursache melden.

Freigabe bleibt manuell (E3/AGB). Dieses Modul wird vom Bot (/updates + upd:-
Callback) aufgerufen; es installiert nichts von selbst.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import version_monitor as vm  # noqa: E402

REGISTER = ROOT / "components.json"
REGRESSION = ROOT / "scripts" / "regressionstest.sh"
STATE_DIR = Path(os.environ.get("UPDATER_STATE_DIR")
                 or (Path.home() / ".claude" / "updater"))
LOCKFILE = STATE_DIR / "run.lock"
LASTFAIL = STATE_DIR / "last_failure.json"
LOCK_STALE_S = 1800  # 30 Min: älteres Schloss gilt als verwaist


def _load_components() -> list[dict]:
    return json.loads(REGISTER.read_text()).get("components", [])


def classify() -> list[dict]:
    """Ermittelt je Komponente cur/latest und die Ampel. Rückgabe nur für
    Komponenten mit verfügbarem Update (grün/gelb/rot); manual/aktuell fehlen."""
    out = []
    for comp in _load_components():
        kind = comp["kind"]
        if kind == "manual" or kind not in vm.HANDLERS:
            continue
        cur = vm.HANDLERS[kind][0](comp)
        latest = vm.HANDLERS[kind][1](comp)
        if not cur or not latest:
            continue
        newer, major = vm._cmp(cur, latest)
        if not newer:
            continue
        if comp.get("pinned"):
            ampel = "gelb"
        elif major:
            ampel = "rot"
        else:
            ampel = "gruen"
        out.append({"name": comp["name"], "kind": kind, "cur": cur,
                    "latest": latest, "ampel": ampel, "comp": comp})
    return out


# ---------- A4: Lauf-Schloss ------------------------------------------------
def _acquire_lock() -> bool:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if LOCKFILE.exists():
            age = time.time() - LOCKFILE.stat().st_mtime
            if age < LOCK_STALE_S:
                return False
            LOCKFILE.unlink(missing_ok=True)  # verwaistes Schloss räumen
        fd = os.open(str(LOCKFILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}\n".encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        return True  # Schloss darf den Betrieb nie ganz blockieren


def _release_lock() -> None:
    LOCKFILE.unlink(missing_ok=True)


# ---------- A1: vollständiger Umgebungs-Freeze ------------------------------
def _pip(comp: dict) -> str:
    return str(Path(comp["venv"]) / "bin" / "pip")


def _freeze_env(venv: str) -> tuple[bool, str]:
    """Vollständiger Stand EINES venv (pip freeze) — die echte Rollback-Grundlage."""
    try:
        r = subprocess.run([str(Path(venv) / "bin" / "pip"), "freeze"],
                           capture_output=True, text=True, timeout=120)
        return (r.returncode == 0, r.stdout)
    except Exception as e:
        return (False, str(e))


def _restore_env(venv: str, frozen: str) -> tuple[bool, str]:
    """Stellt den eingefrorenen Stand wieder her (inkl. transitiver Mitzieher)."""
    tmp = STATE_DIR / f"freeze-{abs(hash(venv))}.txt"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp.write_text(frozen, encoding="utf-8")
        r = subprocess.run([str(Path(venv) / "bin" / "pip"), "install",
                            "-r", str(tmp)],
                           capture_output=True, text=True, timeout=900)
        return (r.returncode == 0, (r.stderr or r.stdout)[-400:])
    except Exception as e:
        return (False, str(e))
    finally:
        tmp.unlink(missing_ok=True)


def _installed_version(comp: dict) -> str:
    kind = comp["kind"]
    if kind in vm.HANDLERS:
        return vm.HANDLERS[kind][0](comp)
    return ""


def _install(comp: dict, version: str) -> tuple[bool, str]:
    """A3: installiert GENAU die übergebene Version (nie ein blindes -U)."""
    kind, ref = comp["kind"], comp["ref"]
    if kind == "pip":
        cmd = [_pip(comp), "install", f"{ref}=={version}"]
    elif kind == "npm_global":
        cmd = ["npm", "install", "-g", f"{ref}@{version}"]
    else:
        return (False, f"kind {kind} nicht installierbar")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        return (r.returncode == 0, (r.stderr or r.stdout)[-400:])
    except Exception as e:
        return (False, str(e))


# ---------- A5: Grundlinie statt absolutem Maßstab --------------------------
_SCORE_RE = re.compile(r"Ergebnis:\s*(\d+)\s*/\s*(\d+)")


def _regression() -> dict:
    """Führt den bestehenden Regressionstest aus und liefert eine MESSBARE Zahl
    (bestanden/gesamt) statt nur ja/nein — Grundlage der Delta-Bewertung."""
    try:
        r = subprocess.run(["bash", str(REGRESSION)], capture_output=True,
                           text=True, timeout=900)
        text = r.stdout or ""
        m = None
        for line in reversed(text.strip().splitlines()):  # A8: robuster lesen
            m = _SCORE_RE.search(line)
            if m:
                break
        if not m:
            m = _SCORE_RE.search(text)
        passed, total = (int(m.group(1)), int(m.group(2))) if m else (None, None)
        line = m.group(0) if m else (text.strip().splitlines() or ["(keine Ausgabe)"])[-1]
        return {"ok": r.returncode == 0, "passed": passed, "total": total,
                "line": line, "raw_tail": text[-800:]}
    except Exception as e:
        return {"ok": False, "passed": None, "total": None,
                "line": f"Testlauf-Fehler: {e}", "raw_tail": str(e)}


# ---------- A7: Wiederhol-Schutz -------------------------------------------
def _fail_key(names: list[str], baseline: dict) -> str:
    return json.dumps({"n": sorted(names), "b": [baseline.get("passed"),
                                                 baseline.get("total")]},
                      sort_keys=True)


def _seen_failure(key: str) -> dict | None:
    try:
        data = json.loads(LASTFAIL.read_text())
        return data if data.get("key") == key else None
    except Exception:
        return None


def _remember_failure(key: str, reason: str) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        LASTFAIL.write_text(json.dumps(
            {"key": key, "reason": reason, "at": time.strftime("%Y-%m-%d %H:%M:%S")}),
            encoding="utf-8")
    except Exception:
        pass


def _clear_failure() -> None:
    LASTFAIL.unlink(missing_ok=True)


# ---------- Hauptablauf -----------------------------------------------------
def _waechter_scharf(frozen_env: dict[str, str], installed: list[str]) -> bool:
    """B1: Den Start-Wächter für den nun fälligen Neustart scharfstellen.

    Der Updater hat bis hierher alles im Griff, was sich im laufenden Betrieb
    prüfen lässt. Was er nicht abdecken kann, ist der Neustart danach: Stirbt
    der Bot dabei, gibt es keinen Prozess mehr, der zurückrollen könnte. Also
    bekommt ein abgekoppelter Wächter den eingefrorenen Stand mit, bevor der
    Neustart passiert — er wartet, prüft und rettet notfalls von außen.

    Rückgabe: True, wenn der Wächter gestartet werden konnte.
    """
    if not frozen_env:
        return False
    skript = Path(__file__).resolve().parent / "start_waechter.py"
    if not skript.exists():
        return False
    # Für den Rückweg zählt die venv des Bots — sie trägt den laufenden Dienst.
    venv, text = next(iter(frozen_env.items()))
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        freeze_datei = STATE_DIR / "freeze_vor_neustart.txt"
        freeze_datei.write_text(text, encoding="utf-8")
        subprocess.Popen(
            [sys.executable, str(skript), "--freeze", str(freeze_datei),
             "--venv", venv, "--detach",
             "--grund", "dem Update von " + ", ".join(installed or ["Komponenten"])],
            start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def apply_updates(names: list[str], expected: dict | None = None) -> dict:
    """Spielt die genannten Komponenten ein.

    Ablauf: Schloss → Grundlinie → Versions-Abgleich → Freeze → Install →
    Regressionstest (Delta) → bei Verschlechterung vollständiger Rollback.

    `expected`: {name: version} — die Adam ANGEZEIGTE Version (A3). Weicht der
    aktuelle Kandidat davon ab, wird NICHT eingespielt, sondern neu gefragt.
    """
    if not _acquire_lock():
        return {"ok": False, "state": "belegt", "done": [], "rolled_back": [],
                "msg": "Es läuft bereits ein Update-Vorgang. Bitte kurz warten "
                       "und danach erneut /updates."}
    try:
        return _apply_locked(names, expected or {})
    finally:
        _release_lock()


def _apply_locked(names: list[str], expected: dict) -> dict:
    cand = {c["name"]: c for c in classify()}
    chosen = [cand[n] for n in names if n in cand]
    if not chosen:
        return {"ok": False, "state": "nichts", "done": [], "rolled_back": [],
                "msg": "Keine passenden Updates (evtl. inzwischen aktuell)."}

    # --- A3: exakt die freigegebene Version, sonst neu fragen ---------------
    drift = [f"{c['name']}: freigegeben {expected[c['name']]}, jetzt {c['latest']}"
             for c in chosen
             if expected.get(c["name"]) and expected[c["name"]] != c["latest"]]
    if drift:
        return {"ok": False, "state": "abweichung", "done": [], "rolled_back": [],
                "msg": ("Seit der Anzeige hat sich die Version geändert — ich spiele "
                        "nichts ein, was du nicht gesehen hast:\n• "
                        + "\n• ".join(drift)
                        + "\n\nBitte /updates erneut aufrufen und neu freigeben.")}

    # --- A5: Grundlinie ZUERST — nicht grün → gar nichts anfassen -----------
    baseline = _regression()
    if not baseline["ok"]:
        return {"ok": False, "state": "fundament_rot", "done": [], "rolled_back": [],
                "baseline": baseline,
                "msg": ("Fundament ist nicht grün ({}) — ich fasse nichts an. "
                        "Erst reparieren, dann updaten.".format(baseline["line"]))}

    # --- A7: bekannte, unveränderte Fehlersituation? ------------------------
    key = _fail_key([c["name"] for c in chosen], baseline)
    seen = _seen_failure(key)
    if seen:
        return {"ok": False, "state": "wiederholung", "done": [], "rolled_back": [],
                "baseline": baseline,
                "msg": ("Dieselbe Kombination ist zuletzt schon gescheitert und an "
                        "der Ausgangslage hat sich nichts geändert — ich spiele sie "
                        "nicht erneut ein.\nGrund von damals: {}\n(Stand: {})\n\n"
                        "Erst die Ursache beheben; danach greift es wieder."
                        .format(seen.get("reason", "?"), seen.get("at", "?")))}

    # --- A1: vollständigen Umgebungsstand einfrieren ------------------------
    venvs = {c["comp"]["venv"] for c in chosen if c["kind"] == "pip"}
    frozen_env: dict[str, str] = {}
    for v in venvs:
        ok, text = _freeze_env(v)
        if not ok:
            return {"ok": False, "state": "kein_freeze", "done": [], "rolled_back": [],
                    "msg": ("Konnte den Ist-Stand nicht sichern ({}) — ohne "
                            "funktionierenden Rollback spiele ich nichts ein."
                            .format(text[:200]))}
        frozen_env[v] = text
    frozen_ver = {c["name"]: c["cur"] for c in chosen}

    # --- Einspielen (A3: exakte Version) ------------------------------------
    installed, install_log = [], []
    for c in chosen:
        ok, out = _install(c["comp"], c["latest"])
        if ok:
            installed.append(c["name"])
        else:
            install_log.append(f"{c['name']}: Install-Fehler — {out}")

    after = _regression()

    # --- Erfolg: keine Install-Fehler UND kein Rückschritt (A5-Delta) -------
    worse = (after["passed"] is not None and baseline["passed"] is not None
             and after["passed"] < baseline["passed"])
    if not install_log and after["ok"] and not worse:
        _clear_failure()
        wacht = _waechter_scharf(frozen_env, installed)
        return {"ok": True, "state": "eingespielt", "done": installed,
                "rolled_back": [], "restart_needed": True,
                "baseline": baseline, "after": after,
                "waechter": wacht,
                "msg": ("Eingespielt. Regressionstest unverändert grün ({} vorher → {} nachher)."
                        .format(baseline["line"], after["line"])
                        + ("\nDer Start-Wächter ist scharf: Kommt der Bot nach dem "
                           "Neustart nicht sauber hoch, setzt er die Umgebung "
                           "selbsttätig zurück und meldet sich." if wacht else ""))}

    # --- Fehlschlag → A1: vollständiger Rollback ---------------------------
    reason = "; ".join(install_log) if install_log else after["line"]
    rolled, failed_rollback = [], []
    for v, text in frozen_env.items():
        ok, out = _restore_env(v, text)
        if not ok:
            failed_rollback.append(f"{Path(v).name}: {out[:160]}")
    # A2: je Paket den TATSÄCHLICHEN Zustand feststellen, nichts behaupten
    still_new = []
    for c in chosen:
        now = _installed_version(c["comp"])
        if now and now == frozen_ver[c["name"]]:
            rolled.append(c["name"])
        elif now:
            still_new.append(f"{c['name']} steht noch auf {now} "
                             f"(erwartet {frozen_ver[c['name']]})")

    after_rb = _regression()
    # A6: Selbst-Widerspruch aussprechen
    same_as_before = (after_rb["passed"] is not None
                      and after_rb["passed"] == after["passed"])
    lines = [f"Fehlgeschlagen ({reason})."]
    if rolled:
        lines.append("Zurückgerollt: " + ", ".join(rolled))
    if still_new or failed_rollback:
        lines.append("🔴 ROLLBACK UNVOLLSTÄNDIG — bitte prüfen:")
        lines += [f"• {s}" for s in still_new + failed_rollback]
    lines.append(f"Regressionstest nach Rollback: {after_rb['line']}.")
    if same_as_before:
        lines.append("→ Der Rollback hat am Testergebnis nichts geändert: "
                     "die Ursache liegt NICHT am Update.")
    _remember_failure(key, reason)

    return {"ok": False,
            "state": "rollback" if not (still_new or failed_rollback) else "rollback_unvollstaendig",
            "done": [], "rolled_back": rolled, "not_rolled_back": still_new + failed_rollback,
            "restart_needed": False, "baseline": baseline, "after": after,
            "after_rollback": after_rb, "msg": "\n".join(lines)}


if __name__ == "__main__":
    # CLI: ohne Argumente klassifizieren; mit Namen anwenden (Wartungsfenster).
    if len(sys.argv) == 1:
        for u in classify():
            sym = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}[u["ampel"]]
            print(f"{sym} {u['name']}: {u['cur']} → {u['latest']}")
    else:
        print(json.dumps(apply_updates(sys.argv[1:]), ensure_ascii=False, indent=2))
