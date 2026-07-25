"""Datenschutz-Ampel (Migrations-Punkt 2.2).

Regelbasierter Klassifizierer, der jede eingehende Nutzer-Nachricht in
🟢 grün / 🟡 gelb / 🔴 rot einstuft — anhand einer *editierbaren* Regeldatei
(TOML, außerhalb des Codes und außerhalb von Git, weil sie Klienten-Namen
enthalten kann).

Ablauf laut Adam-Vorgabe (15.07.2026):
  1. BEOBACHTUNGSPHASE (jetzt): nur einstufen + protokollieren, KEIN Umrouten.
     Regeln bewusst breit. Ende: 4 Wochen 4 Tage 4 Stunden ODER 444 Einstufungen.
  2. Danach Auswertung → Regeln eng trimmen → ENFORCEMENT (rot → lokal,
     Kennzeichnung, Overrides !cloud / !lokal).

Dieses Modul macht nur Schritt 1 (observe/log/status) + die Klassifikation,
die Schritt 2 dann wiederverwendet.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path

log = logging.getLogger("claude-tg-bot.ampel")

# Beobachtungsphase: 4 Wochen + 4 Tage + 4 Stunden
OBSERVATION_SECONDS = (4 * 7 + 4) * 86400 + 4 * 3600  # 32 Tage 4 Stunden
OBSERVATION_MAX_COUNT = 444

_RULES_PATH = Path(
    os.environ.get("AMPEL_RULES_PATH")
    or str(Path.home() / ".claude" / "ampel_rules.toml")
)
_LOG_PATH = Path(
    os.environ.get("AMPEL_LOG_PATH")
    or str(Path(__file__).parent / "logs" / "ampel.jsonl")
)
_STATE_PATH = Path(
    os.environ.get("AMPEL_STATE_PATH")
    or str(Path(__file__).parent / "logs" / "ampel_state.json")
)
# Vom Nutzer per /ampel-Kommando gepflegte Regeln (z. B. Klienten-Namen).
# Bewusst als eigene, leicht schreibbare JSON-Datei — lokal, NIE in Git/Cloud.
_CUSTOM_PATH = Path(
    os.environ.get("AMPEL_CUSTOM_PATH")
    or str(Path.home() / ".claude" / "ampel_custom.json")
)

# Eingebaute Default-Regeln (greifen, falls keine Regeldatei existiert).
# Bewusst breit für die Beobachtungsphase.
_DEFAULT_RULES: dict = {
    "rot": {
        "regex": {
            "IBAN": r"\b[A-Z]{2}\d{2}[ ]?(?:[A-Za-z0-9][ ]?){10,30}\b",
            "Kontonummer": r"\b\d{8,12}\b",
            "Kreditkarte": r"\b(?:\d[ -]?){13,16}\b",
        },
        "keywords": {
            "Gesundheit": [
                "diagnose", "befund", "medikament", "krankheit", "therapie",
                "arztbrief", "rezept", "blutwert", "psych", "symptom",
            ],
            "Zugangsdaten": [
                "passwort", "api-key", "api key", "secret", "token", "zugangsdaten",
                "pin ", "geheimzahl", "private key", "seed phrase",
            ],
            "Finanzen": [
                "kontostand", "gehalt", "umsatz", "schulden", "kredit",
                "steuererklärung", "einkommen", "vermögen",
            ],
        },
        "klienten": [],  # ← echte Klienten-Namen: NUR in der lokalen Regeldatei pflegen
    },
    "gelb": {
        "keywords": {
            "Kontaktdaten": [
                "adresse", "telefonnummer", "handynummer", "e-mail-adresse",
                "geburtsdatum", "geburtstag",
            ],
            "Persönlich": [
                "beziehung", "familie", "privat", "vertraulich",
            ],
            # Kalender und Erinnerungen (Conni/Adam 25.07.2026): Sie sind die
            # DICHTESTE Quelle genau der Daten, für die die Ampel gebaut wurde —
            # Klientennamen, Adressen, Gesundheitliches. Heute liest der Bot sie
            # deterministisch und schickt sie direkt an Telegram, ohne
            # Modellaufruf; unbedenklich. Mit dem Sekretärin-Zielbild (5.19)
            # kippt das: Dann erkennt der AGENT das Auftragsende im Kalender,
            # und Termininhalte landen im Modellkontext. Die Abdeckung muss
            # VORHER stehen, nicht danach — sonst greift sie zum ersten Mal in
            # dem Moment, in dem sie schon zu spät ist.
            "Kalender": [
                "termin", "kalender", "erinnerung", "verabredung", "sitzung",
                "besprechung", "auftragsende", "fällig am", "faellig am",
                "sprechstunde", "beratungstermin", "vorgemerkt",
            ],
        },
    },
}


def _load_rules() -> dict:
    if not _RULES_PATH.is_file():
        return _DEFAULT_RULES
    try:
        import tomllib
        with _RULES_PATH.open("rb") as f:
            data = tomllib.load(f)
        # Minimal-Validierung: rot/gelb-Sektionen müssen dicts sein
        if not isinstance(data.get("rot"), dict):
            return _DEFAULT_RULES
        return data
    except Exception:
        log.exception("Ampel-Regeldatei nicht ladbar — nutze Defaults")
        return _DEFAULT_RULES


_RULES_CACHE: dict | None = None
_RULES_MTIME: float = 0.0


def _rules() -> dict:
    """Regeln gecacht bis die Datei sich ändert (Live-Edit ohne Neustart)."""
    global _RULES_CACHE, _RULES_MTIME
    try:
        mtime = _RULES_PATH.stat().st_mtime if _RULES_PATH.is_file() else 0.0
    except Exception:
        mtime = 0.0
    if _RULES_CACHE is None or mtime != _RULES_MTIME:
        _RULES_CACHE = _load_rules()
        _RULES_MTIME = mtime
    return _RULES_CACHE


def _load_custom() -> dict:
    try:
        if _CUSTOM_PATH.is_file():
            d = json.loads(_CUSTOM_PATH.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                return d
    except Exception:
        log.exception("Ampel-Custom-Regeln nicht ladbar")
    return {"rot": [], "gelb": []}


def _save_custom(d: dict) -> None:
    _CUSTOM_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CUSTOM_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def classify(text: str) -> dict:
    """Stuft einen Text ein. Gibt {color, rules:[...], matches:[(rule, snippet)]}.

    color: 'rot' | 'gelb' | 'gruen'. Bei mehreren Treffern gewinnt die höchste
    Sensibilität (rot > gelb > grün). Berücksichtigt Basis-Regeln (TOML) UND
    per /ampel gepflegte Custom-Regeln (Log zeigt deren Label, nicht das Muster).
    """
    text = text or ""
    lower = text.lower()
    rules = _rules()
    custom = _load_custom()

    def scan(section: dict) -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for name, pattern in (section.get("regex") or {}).items():
            try:
                m = re.search(pattern, text)
                if m:
                    hits.append((f"regex:{name}", m.group(0)[:60]))
            except re.error:
                continue
        kw = section.get("keywords") or {}
        for cat, words in kw.items():
            for w in (words or []):
                if w and w.lower() in lower:
                    hits.append((f"{cat}:{w}", w))
        for nm in (section.get("klienten") or []):
            if nm and nm.lower() in lower:
                hits.append((f"Klient:{nm}", nm))
        return hits

    def color_hits(color: str) -> list[tuple[str, str]]:
        hits = scan(rules.get(color) or {})
        for e in (custom.get(color) or []):
            p = (e.get("pattern") or "").lower()
            if p and p in lower:
                # Rule-Name = Label (gruppiert, verrät im Log nicht das Muster)
                hits.append((e.get("label") or "manuell", (e.get("pattern") or "")[:60]))
        return hits

    rot = color_hits("rot")
    if rot:
        return {"color": "rot", "rules": [h[0] for h in rot], "matches": rot}
    gelb = color_hits("gelb")
    if gelb:
        return {"color": "gelb", "rules": [h[0] for h in gelb], "matches": gelb}
    return {"color": "gruen", "rules": [], "matches": []}


def add_rule(color: str, pattern: str, label: str = "manuell") -> str:
    """Custom-Regel hinzufügen (für /ampel rot|gelb). Muster = Teilstring (case-insensitiv)."""
    color = "rot" if color.lower().startswith("rot") else ("gelb" if color.lower().startswith("gelb") else "")
    if not color:
        return "Farbe muss „rot“ oder „gelb“ sein."
    pattern = (pattern or "").strip()
    if not pattern:
        return "Kein Muster angegeben. Nutzung: /ampel rot [Label:] <Muster>"
    label = (label or "manuell").strip() or "manuell"
    d = _load_custom()
    lst = d.setdefault(color, [])
    if any((e.get("pattern", "").lower() == pattern.lower()) for e in lst):
        return f"Regel „{pattern}“ existiert bereits ({color})."
    lst.append({"pattern": pattern, "label": label})
    try:
        _save_custom(d)
    except Exception:
        log.exception("Custom-Regel speichern fehlgeschlagen")
        return "⚠️ Konnte die Regel nicht speichern (Dateifehler)."
    return f"✅ {color.upper()}-Regel hinzugefügt: „{pattern}“ · Label „{label}“."


def remove_rule(pattern: str) -> str:
    """Custom-Regel(n) mit exaktem Muster entfernen (für /ampel weg)."""
    pattern = (pattern or "").strip()
    if not pattern:
        return "Kein Muster angegeben. Nutzung: /ampel weg <Muster>"
    d = _load_custom()
    removed = 0
    for color in ("rot", "gelb"):
        lst = d.get(color) or []
        keep = [e for e in lst if e.get("pattern", "").lower() != pattern.lower()]
        removed += len(lst) - len(keep)
        d[color] = keep
    if not removed:
        return f"Keine Custom-Regel mit Muster „{pattern}“ gefunden."
    try:
        _save_custom(d)
    except Exception:
        log.exception("Custom-Regel entfernen fehlgeschlagen")
        return "⚠️ Konnte die Änderung nicht speichern (Dateifehler)."
    return f"🗑️ {removed} Regel(n) mit Muster „{pattern}“ entfernt."


def list_rules() -> str:
    """Textübersicht: Basis-Kategorien (aus TOML) + Custom-Regeln (für /ampel regeln)."""
    rules = _rules()
    custom = _load_custom()
    L = ["🚦 Ampel-Regeln", ""]
    for color in ("rot", "gelb"):
        sec = rules.get(color) or {}
        cats = list((sec.get("regex") or {}).keys()) + list((sec.get("keywords") or {}).keys())
        kl = len(sec.get("klienten") or [])
        base = ", ".join(cats) + (f", Klienten({kl})" if kl else "")
        L.append(f"{'🔴' if color=='rot' else '🟡'} {color.upper()} — Basis: {base or '—'}")
        cust = custom.get(color) or []
        if cust:
            for e in cust:
                L.append(f"     • „{e.get('pattern')}“  (Label: {e.get('label','manuell')})")
        else:
            L.append("     • (keine eigenen Regeln)")
        L.append("")
    L.append("Hinzufügen: /ampel rot [Label:] <Muster>   ·   Entfernen: /ampel weg <Muster>")
    return "\n".join(L)


def _load_state() -> dict:
    try:
        if _STATE_PATH.is_file():
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_state(state: dict) -> None:
    try:
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        log.exception("Ampel-State nicht speicherbar (nicht-fatal)")


def observe(text: str, meta: dict | None = None) -> dict:
    """Beobachtungsphase: klassifizieren, protokollieren, zählen. Kein Routing.

    Gibt das Klassifikations-Ergebnis + 'phase_over' zurück (für den späteren
    Enforcement-Umschalter). Fehler hier dürfen den Bot nie stören.
    """
    result = classify(text)
    try:
        state = _load_state()
        now = time.time()
        if "start_ts" not in state:
            state["start_ts"] = now
            state["count"] = 0
        state["count"] = int(state.get("count", 0)) + 1
        _save_state(state)

        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "color": result["color"],
            "rules": result["rules"],
            "matches": [list(m) for m in result["matches"]],
            "text": text,  # lokal, privat (600) — für Adams Fehlalarm-Auswertung
        }
        if meta:
            entry["meta"] = meta
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        log.exception("Ampel-observe fehlgeschlagen (nicht-fatal)")
    result["phase_over"] = phase_over()
    return result


def phase_over() -> bool:
    state = _load_state()
    if not state:
        return False
    if int(state.get("count", 0)) >= OBSERVATION_MAX_COUNT:
        return True
    start = float(state.get("start_ts", time.time()))
    return (time.time() - start) >= OBSERVATION_SECONDS


def status() -> dict:
    """Kennzahlen der Beobachtungsphase (für /ampel + spätere Auswertung)."""
    state = _load_state()
    count = int(state.get("count", 0))
    start = float(state.get("start_ts", 0)) or None
    end_ts = (start + OBSERVATION_SECONDS) if start else None
    # Farb-Verteilung + Top-Regeln aus dem Log
    colors = {"rot": 0, "gelb": 0, "gruen": 0}
    rule_counts: dict[str, int] = {}
    try:
        if _LOG_PATH.is_file():
            for line in _LOG_PATH.read_text(encoding="utf-8").splitlines():
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                colors[e.get("color", "gruen")] = colors.get(e.get("color", "gruen"), 0) + 1
                for r in e.get("rules", []):
                    rule_counts[r] = rule_counts.get(r, 0) + 1
    except Exception:
        pass
    top_rules = sorted(rule_counts.items(), key=lambda x: -x[1])[:10]
    return {
        "count": count,
        "max_count": OBSERVATION_MAX_COUNT,
        "start_ts": start,
        "end_ts": end_ts,
        "phase_over": phase_over(),
        "colors": colors,
        "top_rules": top_rules,
        "rules_path": str(_RULES_PATH),
        "rules_file_exists": _RULES_PATH.is_file(),
    }
