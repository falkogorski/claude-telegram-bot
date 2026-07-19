"""
pending.py — Sofort-Persistenz jeder eingehenden Nachricht (Migrations-Punkt 5.2).

Jede eingehende Nachricht wird beim Empfang als atomare Per-Nachricht-Datei
``logs/pending/<key>.json`` abgelegt und ihr Bearbeitungsstatus mitgeführt:

    offen  →  in_bearbeitung  →  beantwortet (== Datei gelöscht)

Ein Reboot mitten in der Bearbeitung verschluckt damit nichts: die noch
liegenden Records überleben und werden beim Start wieder aufgegriffen
(Startup-Reconcile → 5.2 Schritt 2 / Watchdog 5.18).

Bewusst analog zu ``ampel.py`` / ``presend.py`` (eigenes ``logs/``-Verzeichnis
relativ zum Modul, wird vom VPS-Backup miterfasst) — aber **atomar**
(tmp + ``os.replace``), weil ein Crash mitten im Schreiben nie eine halbe Datei
hinterlassen darf.

Gespeichert werden ausschließlich **serialisierbare Primitive** — niemals das
lebende ``telegram.Update`` (nicht serialisierbar). Der Wiederaufgreif-Pfad
(Schritt 2) rekonstruiert daraus, ohne ``update.*`` zu brauchen. Anhänge sind
kein Sonderfall: ihr lokaler Pfad (in ``UPLOAD_DIR``, bleibt über Reboots
liegen) steckt bereits im ``text``.

Alle Funktionen sind fehlertolerant: Persistenz darf den Bot-Flow NIE brechen —
im Zweifel wird geloggt und weitergemacht.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

log = logging.getLogger(__name__)

# Status-Werte. "beantwortet" ist bewusst KEIN gespeicherter Status:
# beantwortet == Record gelöscht (was noch liegt, ist per Definition offen).
STATUS_OPEN = "offen"
STATUS_RUNNING = "in_bearbeitung"
STATUS_FAILED = "fehler"

_DIR = Path(
    os.environ.get("PENDING_DIR")
    or str(Path(__file__).parent / "logs" / "pending")
)


def _ensure_dir() -> None:
    _DIR.mkdir(parents=True, exist_ok=True)


def make_key(chat_id: int, message_id: int) -> str:
    """Stabiler, dateisystem-sicherer Schlüssel je Telegram-Nachricht.
    ``chat_id`` + ``message_id`` ist global eindeutig (message_id nur je Chat)."""
    return f"{chat_id}_{message_id}"


def _path(key: str) -> Path:
    return _DIR / f"{key}.json"


def _atomic_write(key: str, payload: dict) -> None:
    """Schreibt tmp im selben Verzeichnis und benennt atomar um (os.replace).
    Der tmp-Name endet NICHT auf .json → wird von load_all()'s *.json-glob
    ignoriert, falls ein Crash ihn liegen lässt."""
    _ensure_dir()
    final = _path(key)
    tmp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def record(key: str, data: dict) -> None:
    """Legt (oder ersetzt) den Record atomar an. ``status`` wird auf 'offen'
    gesetzt, falls nicht mitgegeben."""
    try:
        payload = dict(data)
        payload.setdefault("status", STATUS_OPEN)
        payload.setdefault("recorded_at", time.time())
        _atomic_write(key, payload)
    except Exception:
        log.exception("pending.record fehlgeschlagen (key=%s) — nicht-fatal", key)


def set_status(key: str, status: str) -> None:
    """Ändert nur das Status-Feld eines bestehenden Records (atomar).
    Fehlt die Datei (z. B. schon resolved), passiert nichts."""
    if not key:
        return
    try:
        p = _path(key)
        if not p.exists():
            return
        payload = json.loads(p.read_text(encoding="utf-8"))
        payload["status"] = status
        payload["status_changed_at"] = time.time()
        _atomic_write(key, payload)
    except Exception:
        log.exception("pending.set_status fehlgeschlagen (key=%s) — nicht-fatal", key)


def bump_attempts(key: str) -> int:
    """Erhöht den Versuchszähler des Records und gibt den neuen Stand zurück.

    Schutz gegen Absturz-Schleifen: Eine Nachricht, die den Bot reproduzierbar
    mitreißt, würde sonst bei JEDEM Start erneut nachgeholt — und risse ihn
    wieder mit. Ab einer Obergrenze wird sie nur noch gemeldet."""
    if not key:
        return 0
    try:
        p = _path(key)
        if not p.exists():
            return 0
        payload = json.loads(p.read_text(encoding="utf-8"))
        n = int(payload.get("attempts", 0)) + 1
        payload["attempts"] = n
        _atomic_write(key, payload)
        return n
    except Exception:
        log.exception("pending.bump_attempts fehlgeschlagen (key=%s) — nicht-fatal", key)
        return 0


def resolve(key: str) -> None:
    """Nachricht erledigt (beantwortet/aufgegeben) → Record löschen."""
    if not key:
        return
    try:
        _path(key).unlink(missing_ok=True)
    except Exception:
        log.exception("pending.resolve fehlgeschlagen (key=%s) — nicht-fatal", key)


def load_all() -> list[dict]:
    """Alle noch liegenden Records (Startup-Reconcile / /status).
    Jeder Record bekommt seinen Schlüssel als ``_key`` beigelegt. Beschädigte
    Dateien werden übersprungen, nicht geworfen."""
    out: list[dict] = []
    try:
        if not _DIR.exists():
            return out
        for p in sorted(_DIR.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                d.setdefault("_key", p.stem)
                out.append(d)
            except Exception:
                log.warning("pending: beschädigter Record übersprungen: %s",
                            p.name, exc_info=True)
    except Exception:
        log.exception("pending.load_all fehlgeschlagen — nicht-fatal")
    return out


def counts() -> dict[str, int]:
    """Zählt liegende Records je Status — für /status und Selbstcheck."""
    by_status: dict[str, int] = {}
    for r in load_all():
        s = r.get("status", "?")
        by_status[s] = by_status.get(s, 0) + 1
    return by_status
