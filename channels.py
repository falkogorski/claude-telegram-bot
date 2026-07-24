# <!-- ROLLE: kanal-routing -->
"""Phase-6-Kanalstruktur: Häuser (Gruppen) mit Zimmern (Forum-Topics) + Routing.

Reine Logik, KEINE Telegram-API-Aufrufe — damit vollständig unit-testbar.
Der Bot (bot.py) ruft die Telegram-Seite auf (create_forum_topic, send…) und
nutzt dieses Modul für: Haus-Erkennung am Gruppennamen, Zimmer-Planung,
Persistenz der Zuordnung in den Prefs und Auflösung „Quelle → (chat_id,
thread_id)".

Struktur final nach Audit-Entscheid 24.07.2026 (docs/entscheidungsvorlagen/
6-6-kanal-struktur-vorlage.md, v3). Jakuna-San ist Bestand und wird NICHT
automatisch bespielt (kein Auto-Topic-Anlegen, kein Auto-Routing).
"""
from __future__ import annotations

import re
import unicodedata

# --- Haus-/Zimmer-Definitionen (FINAL v3) -------------------------------------
# key = stabiler interner Bezeichner (= 4.3-Ordnername); title = Anzeigename;
# emoji = Hausschild; zimmer = geordnete Liste der Topic-Namen (= Unterordner).
HOUSES: dict[str, dict] = {
    "werkstatt": {
        "emoji": "🔧",
        "title": "Werkstatt",
        "zimmer": [
            "Migration & Technik",
            "Fanpost",
            "Rechnungen & Büro",
            "Offene Punkte",
        ],
    },
    "nirgendhaus": {
        "emoji": "🕰️",
        "title": "Nirgendhaus",
        "zimmer": [
            "Produkt & Blaupause",
            "Kunden & Piloten",
            "Vertrieb & Empfehlung",
            "Recht & Zahlen",
        ],
    },
    "handelshaus": {
        "emoji": "🏛️",
        "title": "Handelshaus",
        "zimmer": [
            "Ideen & Chancen",
            "Affiliate-Projekt",
        ],
    },
    "bibliothek": {
        "emoji": "📚",
        "title": "Bibliothek",
        "zimmer": [
            "Recherchen & Referenzen",
            "Link-Inbox",
            "Interessen",
        ],
    },
}

# Bestand — nur registrieren, nie automatisch bespielen.
BESTAND_HAUS = {"key": "jakuna-san", "title": "Jakuna-San"}

# --- Routing-Tabelle: Quelle → (Haus, Zimmer) ---------------------------------
# Nur diese drei laufen automatisch; alles andere geht manuell/per Zuruf.
ROUTES: dict[str, tuple[str, str]] = {
    "bot_status": ("werkstatt", "Migration & Technik"),
    "research": ("bibliothek", "Recherchen & Referenzen"),
    "unassigned": ("werkstatt", "Offene Punkte"),
}


def _norm(text: str) -> str:
    """Kleinschreibung, Akzente/Emoji weg, nur a-z0-9 — für robusten Vergleich."""
    if not text:
        return ""
    # Unicode-Dekomposition, kombinierende Zeichen (Akzente) entfernen
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", stripped.lower())


def detect_house(group_title: str | None) -> str | None:
    """Erkennt das Haus am Gruppennamen (emoji-/schreibweisentolerant).

    Rückgabe: Haus-Key aus HOUSES oder None (inkl. Bestand Jakuna-San → None,
    weil dieser nicht automatisch bespielt wird).
    """
    n = _norm(group_title or "")
    if not n:
        return None
    # Bestand ausdrücklich NICHT als Auto-Haus behandeln.
    if _norm(BESTAND_HAUS["title"]) in n:
        return None
    for key, spec in HOUSES.items():
        if _norm(spec["title"]) in n:
            return key
    return None


def zimmer_for(house_key: str) -> list[str]:
    """Geordnete Zimmerliste eines Hauses (leer bei unbekanntem Haus)."""
    spec = HOUSES.get(house_key)
    return list(spec["zimmer"]) if spec else []


def folder_name(name: str) -> str:
    """4.3-Ordnername aus einem Haus-/Zimmertitel (identische, dateisystem-
    taugliche Schreibweise): Kleinbuchstaben, & → '', Leerzeichen → '-'."""
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    s = stripped.lower().replace("&", " ").replace("/", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


# --- Persistenz in den Prefs --------------------------------------------------
# Schema unter prefs["channels"]:
#   {"houses": {<house_key>: {
#        "chat_id": int, "title": str, "is_forum": bool,
#        "topics": {<zimmer_name>: <message_thread_id:int>}}}}
def _channels_root(prefs: dict) -> dict:
    root = prefs.get("channels")
    if not isinstance(root, dict):
        root = {"houses": {}}
        prefs["channels"] = root
    if not isinstance(root.get("houses"), dict):
        root["houses"] = {}
    return root


def register_house(prefs: dict, house_key: str, chat_id: int,
                   title: str, is_forum: bool) -> dict:
    """Legt/aktualisiert den Haus-Eintrag an (ohne Topics zu berühren)."""
    houses = _channels_root(prefs)["houses"]
    entry = houses.get(house_key) or {}
    entry.update({
        "chat_id": int(chat_id),
        "title": title,
        "is_forum": bool(is_forum),
    })
    entry.setdefault("topics", {})
    houses[house_key] = entry
    return entry


def missing_zimmer(prefs: dict, house_key: str) -> list[str]:
    """Zimmer eines Hauses, die noch KEINE gespeicherte Topic-ID haben —
    das ist die Anlage-Liste für create_forum_topic (idempotent)."""
    houses = _channels_root(prefs)["houses"]
    entry = houses.get(house_key) or {}
    have = entry.get("topics") or {}
    return [z for z in zimmer_for(house_key) if z not in have]


def record_topic(prefs: dict, house_key: str, zimmer: str,
                 thread_id: int) -> None:
    """Speichert die vom Telegram-API zurückgegebene Topic-ID."""
    houses = _channels_root(prefs)["houses"]
    entry = houses.setdefault(house_key, {"topics": {}})
    entry.setdefault("topics", {})[zimmer] = int(thread_id)


def resolve_route(prefs: dict, source: str) -> tuple[int, int] | None:
    """Quelle (z. B. 'research') → (chat_id, thread_id) oder None, wenn das
    Zielhaus/-zimmer noch nicht angelegt ist. Fällt NIE auf einen falschen
    Kanal zurück — None heißt 'kein Auto-Ziel, im Bot-Chat bleiben'."""
    route = ROUTES.get(source)
    if not route:
        return None
    house_key, zimmer = route
    entry = (_channels_root(prefs)["houses"]).get(house_key)
    if not entry:
        return None
    chat_id = entry.get("chat_id")
    thread_id = (entry.get("topics") or {}).get(zimmer)
    if chat_id is None or thread_id is None:
        return None
    return int(chat_id), int(thread_id)


def house_overview(prefs: dict) -> list[dict]:
    """Für /status u. ä.: kompakte Übersicht aller registrierten Häuser."""
    houses = _channels_root(prefs)["houses"]
    out = []
    for key, spec in HOUSES.items():
        entry = houses.get(key)
        if not entry:
            continue
        have = entry.get("topics") or {}
        out.append({
            "key": key,
            "emoji": spec["emoji"],
            "title": entry.get("title") or spec["title"],
            "chat_id": entry.get("chat_id"),
            "zimmer_total": len(spec["zimmer"]),
            "zimmer_done": sum(1 for z in spec["zimmer"] if z in have),
        })
    return out
