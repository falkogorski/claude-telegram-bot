#!/usr/bin/env python3
# <!-- ROLLE: versions-monitor -->
"""5.21 — Versions-/Update-Monitor (register-basiert, DETERMINISTISCH).

Liest components.json, ermittelt je Komponente die installierte und die
verfügbare Version aus KOSTENFREIEN Quellen (PyPI, npm-Registry, nodejs.org)
und meldet neuere Versionen per Telegram — Major-Sprünge markiert. **KEIN
Modell-/Claude-Aufruf** (AGB-Leitplanke), **keine Installation** (nur Hinweis,
E3). Läuft wöchentlich als systemd-Timer; meldet nur, wenn es etwas gibt.

Aufruf (auf dem VPS, als root, damit alle venvs + der Bot-Token erreichbar sind):
    python3 scripts/version_monitor.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "components.json"
LOGFILE = Path(os.environ.get("VERSION_MONITOR_LOG")
               or "/home/claudebot/claude-telegram-bot/logs/version-monitor.log")
ENVFILE = os.environ.get("BOT_ENVFILE") or "/etc/claude-telegram-bot.env"
HTTP_TIMEOUT = 15


def _get_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "momo-version-monitor"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ""


def _vtuple(v: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", v or "")
    return tuple(int(n) for n in nums[:4]) or (0,)


def _cmp(cur: str, latest: str) -> tuple[bool, bool]:
    """(update_verfügbar, ist_major). Major = erste Zahlgruppe unterscheidet sich."""
    c, l = _vtuple(cur), _vtuple(latest)
    if not c or not l:
        return (False, False)
    newer = l > c
    major = newer and (l[0] != c[0])
    return (newer, major)


# --- Versions-Ermittlung je Kind --------------------------------------------
def cur_pip(comp: dict) -> str:
    pip = Path(comp["venv"]) / "bin" / "pip"
    out = _run([str(pip), "show", comp["ref"]])
    m = re.search(r"^Version:\s*(.+)$", out, re.MULTILINE)
    return m.group(1).strip() if m else ""


def latest_pip(comp: dict) -> str:
    d = _get_json(f"https://pypi.org/pypi/{urllib.parse.quote(comp['ref'])}/json")
    return (d or {}).get("info", {}).get("version", "") if d else ""


def cur_npm(comp: dict) -> str:
    out = _run(["npm", "ls", "-g", comp["ref"], "--depth=0"])
    m = re.search(re.escape(comp["ref"]) + r"@([0-9][^\s]*)", out)
    return m.group(1) if m else ""


def latest_npm(comp: dict) -> str:
    quoted = comp["ref"].replace("/", "%2F")
    d = _get_json(f"https://registry.npmjs.org/{quoted}")
    return (d or {}).get("dist-tags", {}).get("latest", "") if d else ""


def cur_node(_comp: dict) -> str:
    return _run(["node", "--version"]).strip()


def latest_node(_comp: dict) -> str:
    d = _get_json("https://nodejs.org/dist/index.json")
    if not isinstance(d, list):
        return ""
    for rel in d:  # neueste zuerst; erste LTS ist die aktuelle LTS-Linie
        if rel.get("lts"):
            return rel.get("version", "")
    return d[0].get("version", "") if d else ""


HANDLERS = {
    "pip": (cur_pip, latest_pip),
    "npm_global": (cur_npm, latest_npm),
    "node": (cur_node, latest_node),
}


def _send_telegram(text: str) -> None:
    env = {}
    try:
        for line in Path(ENVFILE).read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except Exception:
        return
    token = env.get("TELEGRAM_BOT_TOKEN")
    uids = [u.strip() for u in (env.get("ALLOWED_USER_IDS") or "").split(",") if u.strip()]
    if not token or not uids:
        return
    for uid in uids:
        data = urllib.parse.urlencode({"chat_id": uid, "text": text}).encode()
        try:
            urllib.request.urlopen(
                f"https://api.telegram.org/bot{token}/sendMessage", data=data,
                timeout=HTTP_TIMEOUT)
        except Exception:
            pass


def main() -> int:
    reg = json.loads(REGISTER.read_text())
    updates: list[str] = []   # meldepflichtig
    manual: list[str] = []    # nur Reminder
    loglines: list[str] = []
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for comp in reg.get("components", []):
        name, kind = comp["name"], comp["kind"]
        if kind == "manual":
            manual.append(f"• {name}: manuell prüfen — {comp.get('note', '')}")
            loglines.append(f"~ {name}: manual")
            continue
        handler = HANDLERS.get(kind)
        if not handler:
            loglines.append(f"? {name}: unbekannter kind {kind}")
            continue
        cur = handler[0](comp)
        latest = handler[1](comp)
        if not cur or not latest:
            loglines.append(f"? {name}: cur={cur or '?'} latest={latest or '?'} (Quelle n/a)")
            continue
        newer, major = _cmp(cur, latest)
        if newer:
            tag = "🔴 MAJOR" if major else "🟡"
            pin = " (gepinnt — bewusst, Wartungsfenster)" if comp.get("pinned") else ""
            updates.append(f"{tag} {name}: {cur} → {latest}{pin}")
            loglines.append(f"UPDATE {name}: {cur} -> {latest}{' MAJOR' if major else ''}")
        else:
            loglines.append(f"ok {name}: {cur} (aktuell)")

    # Protokoll immer
    try:
        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        with LOGFILE.open("a", encoding="utf-8") as fh:
            fh.write(f"===== Versions-Monitor {stamp} =====\n")
            fh.write("\n".join(loglines) + "\n")
    except Exception:
        pass

    # Meldung nur bei echten Updates (Manual-Reminder hängen wir an, wenn es
    # ohnehin eine Meldung gibt — sonst kein wöchentliches Rauschen).
    if updates:
        msg = "📦 Update-Monitor (5.21) — verfügbare Versionen:\n" + "\n".join(updates)
        msg += "\n\nInstallation bleibt manuell (E3). 🔴 = Major-Sprung, bewusst prüfen."
        if manual:
            msg += "\n\nManuell im Blick behalten:\n" + "\n".join(manual)
        _send_telegram(msg)
        print(f"{len(updates)} Update(s) gemeldet.")
    else:
        print("Keine Updates — keine Meldung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
