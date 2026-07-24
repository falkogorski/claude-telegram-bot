#!/usr/bin/env python3
# <!-- ROLLE: updater -->
"""Updater — Gegenstück zum Versions-Monitor (5.21). WENDET Updates AN.

Strikt getrennt vom Monitor (der ERKENNT). Ebenfalls **deterministisch, KEIN
Modell-Aufruf**. Ampel-Klassifikation aus SemVer + Pin-Liste:
  🟢 grün  = Patch/Minor, nicht gepinnt → sammelbar (eine Sammelfreigabe).
  🟡 gelb  = bewusst gepinnt → nie automatisch, nur Einzel-Freigabe im Fenster.
  🔴 rot   = Major-Sprung → nie automatisch, Einzel-Freigabe + Rollback-Ansage.
  manual   = OS/whisper.cpp/lobe-chat/pandoc … → nicht Updater-Sache.

Sicherheits-Pflicht vor JEDER Anwendung (nicht verhandelbar):
  1. Ist-Stand einfrieren = aktuell installierte Version je Paket merken
     (kein separater requirements.lock; die gepinnten Pakete SIND die 🟡-Kategorie).
  2. Einspielen (pip -U / npm -g).
  3. Health-Check = scripts/regressionstest.sh (der bestehende, kein zweiter).
  4. Bei Rot/Fehler → automatischer Rollback auf den eingefrorenen Stand + Meldung.
     Ohne funktionierenden Rollback kein Update.

Freigabe bleibt manuell (E3/AGB). Dieses Modul wird vom Bot (/updates + upd:-
Callback) aufgerufen; es installiert nichts von selbst.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import version_monitor as vm  # noqa: E402

REGISTER = ROOT / "components.json"
REGRESSION = ROOT / "scripts" / "regressionstest.sh"


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


def _pip(comp: dict) -> str:
    return str(Path(comp["venv"]) / "bin" / "pip")


def _install(comp: dict, version: str | None = None) -> tuple[bool, str]:
    """Installiert (oder rollt zurück, wenn version gesetzt) EIN Paket."""
    kind, ref = comp["kind"], comp["ref"]
    if kind == "pip":
        spec = f"{ref}=={version}" if version else ref
        cmd = [_pip(comp), "install", "-U", spec] if not version else [_pip(comp), "install", spec]
    elif kind == "npm_global":
        spec = f"{ref}@{version}" if version else f"{ref}@latest"
        cmd = ["npm", "install", "-g", spec]
    else:
        return (False, f"kind {kind} nicht installierbar")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return (r.returncode == 0, (r.stderr or r.stdout)[-400:])
    except Exception as e:
        return (False, str(e))


def _regression_ok() -> tuple[bool, str]:
    try:
        r = subprocess.run(["bash", str(REGRESSION)], capture_output=True,
                           text=True, timeout=600)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        return (r.returncode == 0, last)
    except Exception as e:
        return (False, str(e))


def apply_updates(names: list[str]) -> dict:
    """Spielt die genannten Komponenten ein (Freeze → Install → Regressionstest
    → Rollback bei Fehler). Rückgabe: strukturiertes Ergebnis für die Meldung."""
    cand = {c["name"]: c for c in classify()}
    chosen = [cand[n] for n in names if n in cand]
    if not chosen:
        return {"ok": False, "msg": "Keine passenden Updates (evtl. inzwischen aktuell).",
                "done": [], "rolled_back": []}

    frozen = {c["name"]: c["cur"] for c in chosen}   # Ist-Stand-Lock
    installed, install_log = [], []
    for c in chosen:
        ok, out = _install(c["comp"])
        if ok:
            installed.append(c["name"])
        else:
            install_log.append(f"{c['name']}: Install-Fehler — {out}")

    reg_ok, reg_line = _regression_ok()
    if reg_ok and not install_log:
        return {"ok": True, "msg": f"Eingespielt + Regressionstest grün ({reg_line}).",
                "done": installed, "rolled_back": [], "restart_needed": True}

    # Fehler oder roter Regressionstest → Rollback auf den eingefrorenen Stand.
    rolled = []
    for c in chosen:
        if c["name"] in installed:
            ok, _ = _install(c["comp"], version=frozen[c["name"]])
            if ok:
                rolled.append(c["name"])
    reg2_ok, reg2_line = _regression_ok()
    reason = reg_line if not reg_ok else "; ".join(install_log)
    return {"ok": False,
            "msg": (f"Fehlgeschlagen ({reason}) → Rollback ausgeführt. "
                    f"Regressionstest nach Rollback: {reg2_line}."),
            "done": [], "rolled_back": rolled, "restart_needed": False}


if __name__ == "__main__":
    # CLI: ohne Argumente klassifizieren; mit Namen anwenden (für Wartungsfenster).
    if len(sys.argv) == 1:
        for u in classify():
            sym = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}[u["ampel"]]
            print(f"{sym} {u['name']}: {u['cur']} → {u['latest']}")
    else:
        print(json.dumps(apply_updates(sys.argv[1:]), ensure_ascii=False, indent=2))
