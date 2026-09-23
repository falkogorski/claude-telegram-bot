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

import copy
import json
import os
import re
import unicodedata
from pathlib import Path

# --- Haus-/Zimmer-Definitionen (FINAL v3) -------------------------------------
# key = stabiler interner Bezeichner (= 4.3-Ordnername); title = Anzeigename;
# emoji = Hausschild; zimmer = geordnete Liste der Topic-Namen (= Unterordner).
#
# **[GEAENDERT 24.09.2026, Block 5, Claudias Auftrag 13.09.] Das ist jetzt die
# ERSTBEFUELLUNG, nicht mehr die geltende Liste.** Adam: *„Ich möchte nicht
# jedes Mal über Mick gehen, wenn ich ein Zimmer hinzufügen oder verändern
# will."* Die geltende Liste steht in `kanaele.json` neben den Vorlieben und
# wird mit `haeuser()` / `routen()` gelesen. Fehlt die Datei, schreibt der Bot
# sie beim Start hieraus; ist sie beschaedigt, gilt diese Liste. **Wer hier
# etwas aendert, aendert nur den Anfang — nicht den laufenden Stand.**
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
# Ebenfalls Erstbefuellung (Block 5): Die Routen zeigen auf Zimmer NAMEN, und
# ein Umbenennen muss sie nachziehen koennen — aus dem Code heraus ginge das nicht.
ROUTES: dict[str, tuple[str, str]] = {
    "bot_status": ("werkstatt", "Migration & Technik"),
    "research": ("bibliothek", "Recherchen & Referenzen"),
    "unassigned": ("werkstatt", "Offene Punkte"),
}


# --- Die geltende Liste: Daten statt Code  [NEU 24.09.2026, Block 5] ---------
def datei() -> Path:
    roh = os.environ.get("KANAELE_FILE")
    if roh:
        return Path(roh)
    prefs = os.environ.get("USER_PREFS_FILE")
    basis = (Path(prefs).parent if prefs
             else Path.home() / ".config" / "claude-telegram-bot")
    return basis / "kanaele.json"


def _erstbefuellung() -> dict:
    return {"houses": copy.deepcopy(HOUSES),
            "routes": {k: list(v) for k, v in ROUTES.items()}}


_ZWISCHENSPEICHER: dict = {"mtime": None, "daten": None, "beschaedigt": False}


def _laden() -> dict:
    """Die geltende Liste — aus der Datei, sonst die Erstbefuellung.

    **Liest nur, schreibt nie.** Anlegen darf allein der Bot
    (`erstbefuellen`): Der Tagescheck laeuft als root, und eine von root
    angelegte Datei koennte der Bot danach nicht mehr schreiben.

    Beschaedigt → Erstbefuellung, und `beschaedigt()` sagt es. Ein unlesbares
    Woerterbuch darf das Routing nicht stillschweigend abschalten.
    """
    pfad = datei()
    try:
        mtime = pfad.stat().st_mtime
    except OSError:
        _ZWISCHENSPEICHER.update(mtime=None, daten=None, beschaedigt=False)
        return _erstbefuellung()
    if _ZWISCHENSPEICHER["mtime"] == mtime and _ZWISCHENSPEICHER["daten"] is not None:
        return _ZWISCHENSPEICHER["daten"]
    try:
        d = json.loads(pfad.read_text(encoding="utf-8"))
        ok = (isinstance(d, dict) and isinstance(d.get("houses"), dict)
              and isinstance(d.get("routes"), dict)
              and all(isinstance(h, dict) and isinstance(h.get("zimmer"), list)
                      and h.get("title") for h in d["houses"].values()))
    except Exception:
        ok = False
    if not ok:
        _ZWISCHENSPEICHER.update(mtime=mtime, daten=_erstbefuellung(), beschaedigt=True)
        return _ZWISCHENSPEICHER["daten"]
    _ZWISCHENSPEICHER.update(mtime=mtime, daten=d, beschaedigt=False)
    return d


def haeuser() -> dict:
    return _laden()["houses"]


def routen() -> dict:
    return {k: tuple(v) for k, v in _laden()["routes"].items()}


def beschaedigt() -> bool:
    _laden()
    return bool(_ZWISCHENSPEICHER["beschaedigt"])


def speichern(daten: dict) -> None:
    pfad = datei()
    pfad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pfad.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(pfad)
    _ZWISCHENSPEICHER.update(mtime=None, daten=None)


def erstbefuellen() -> bool:
    """Beim Bot-Start: Fehlt die Datei, wird sie aus der Erstbefuellung
    geschrieben — kein leerer Zustand, kein Verlust beim ersten Start nach dem
    Umbau. Eine vorhandene (auch beschaedigte) Datei bleibt unberuehrt."""
    if datei().exists():
        return False
    speichern(_erstbefuellung())
    return True


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
    for key, spec in haeuser().items():
        if _norm(spec["title"]) in n:
            return key
    return None


def zimmer_for(house_key: str) -> list[str]:
    """Geordnete Zimmerliste eines Hauses (leer bei unbekanntem Haus)."""
    spec = haeuser().get(house_key)
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
    route = routen().get(source)
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


def zimmer_name_fuer(prefs: dict, chat_id: "int | None",
                     thread_id: "int | None") -> "str | None":
    """Aus `(chat_id, thread_id)` den Klarnamen -- oder `None`.

    **[NEU 09.09.2026, Block 2]** Der Leitstand soll „Werkstatt · Migration &
    Technik" zeigen, nicht `thread_id 47`. Die Zuordnung steht bereits in den
    Vorlieben (`record_topic`), sie wurde nur nie rueckwaerts gelesen.

    **`chat_id` ist noetig, nicht schmueckend:** Themen-Kennungen sind nur
    INNERHALB eines Chats eindeutig. Zwei Haeuser koennen dieselbe tragen; ohne
    den Chat waere der Name geraten. Fehlt er, wird `None` zurueckgegeben --
    lieber die nackte Zahl als ein falscher Name.
    """
    if thread_id is None or chat_id is None:
        return None
    for key, entry in (_channels_root(prefs)["houses"]).items():
        if int(entry.get("chat_id") or 0) != int(chat_id):
            continue
        for zimmer, tid in (entry.get("topics") or {}).items():
            if int(tid) == int(thread_id):
                titel = entry.get("title") or (haeuser().get(key) or {}).get("title") or key
                return f"{titel} · {zimmer}"
    return None


def house_overview(prefs: dict) -> list[dict]:
    """Für /status u. ä.: kompakte Übersicht aller registrierten Häuser."""
    houses = _channels_root(prefs)["houses"]
    out = []
    for key, spec in haeuser().items():
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


def zimmer_aufloesen(prefs: dict, name: str) -> "tuple[int, int, str] | None":
    """Klarname → `(chat_id, thread_id, voller Name)` — oder `None`.

    **[NEU 10.09.2026, Block 3]** Das Gegenstück zu `zimmer_name_fuer`. Die
    Sekretärin nennt ein Zimmer beim Namen; der Code muss daraus eine Adresse
    machen, **bevor** irgendetwas eingereiht wird.

    Drei Eigenschaften, jede aus einer eigenen Bruchstelle:

    * **Schreibweise ist egal, Bedeutung nicht.** Verglichen wird über
      `folder_name` — „Migration & Technik", „migration-technik" und
      „Migration und Technik" sind dasselbe Zimmer. Ein Modell tippt Namen
      selten zeichengenau ab; daran darf ein Auftrag nicht scheitern.
    * **Mehrdeutig heißt `None`.** Trägt derselbe Name in zwei Häusern ein
      Zimmer, wird **nicht** geraten. Ein Auftrag im falschen Haus ist
      schlimmer als ein Auftrag, der zurückkommt.
    * **Der volle Name wird zurückgegeben**, nicht der getippte. Was der
      Aufrufer meldet, ist damit die Adresse, die wirklich getroffen wurde.

    Der Haus-Name allein löst **nicht** auf: „Werkstatt" ist kein Zimmer.
    """
    gesucht = folder_name(name or "")
    if not gesucht:
        return None
    treffer: list[tuple[int, int, str]] = []
    for key, entry in (_channels_root(prefs)["houses"]).items():
        chat_id = entry.get("chat_id")
        if chat_id is None:
            continue
        titel = entry.get("title") or (haeuser().get(key) or {}).get("title") or key
        for zimmer, tid in (entry.get("topics") or {}).items():
            if folder_name(zimmer) != gesucht:
                continue
            treffer.append((int(chat_id), int(tid), f"{titel} · {zimmer}"))
    if len(treffer) != 1:
        return None
    return treffer[0]


def zimmer_namen(prefs: dict) -> list[str]:
    """Alle angelegten Zimmer als Klarnamen — für Auskunft und Fehlermeldung.

    Wer ein unbekanntes Zimmer nennt, bekommt die Liste der bekannten zurück.
    Eine Fehlermeldung ohne Alternativen zwingt zum Raten.
    """
    namen: list[str] = []
    for key, entry in (_channels_root(prefs)["houses"]).items():
        titel = entry.get("title") or (haeuser().get(key) or {}).get("title") or key
        for zimmer in (entry.get("topics") or {}):
            namen.append(f"{titel} · {zimmer}")
    return sorted(namen)


# --- Zimmer anlegen und umbenennen  [NEU 24.09.2026, Block 5] ---------------
#
# Reine Datenlogik — die Telegram-Seite (Thema anlegen, umbenennen) macht der
# Bot. Die Reihenfolge dort ist: erst Telegram, dann die Daten; scheitert das
# Schreiben, nimmt der Bot die Telegram-Seite zurueck. So entsteht nie eine
# Dublette (Claudias Tabelle: `missing_zimmer` haelt ein Zimmer ohne
# Kennung fuer fehlend und legte es ein zweites Mal an).

def haus_finden(name: str) -> "str | None":
    """„Werkstatt", „werkstatt", „🔧 Werkstatt" → `werkstatt`; sonst None."""
    n = _norm(name or "")
    if not n:
        return None
    for key, spec in haeuser().items():
        if n in (_norm(key), _norm(spec.get("title", ""))):
            return key
    return None


def anlegen_pruefen(prefs: dict, haus_key: str, name: str) -> "tuple[str | None, str | None]":
    """(Absage, Warnung) fuer ein neues Zimmer. Beide `None` heisst: los.

    **Gleicher Name im selben Haus: Absage.** **Im anderen Haus: Warnung** —
    Claudias Auflage: gemeldet, nicht verhindert. `zimmer_aufloesen` gibt bei
    zwei Treffern bewusst `None`; beide Zimmer waeren fuer die Sekretaerin
    dann unadressierbar, und das soll Adam vorher wissen.
    """
    name = (name or "").strip()
    if not name:
        return "Kein Zimmername angegeben.", None
    if len(name) > 128:
        return "Der Name ist zu lang (Telegram erlaubt 128 Zeichen).", None
    if haus_key not in haeuser():
        return "Dieses Haus kenne ich nicht.", None
    eintrag = (_channels_root(prefs)["houses"]).get(haus_key) or {}
    if eintrag.get("chat_id") is None:
        return "Das Haus ist noch nicht eingerichtet (der Bot ist dort noch nicht Mitglied).", None
    if not eintrag.get("is_forum"):
        return "Das Haus hat den Forum-Modus (Themen) nicht an — ohne ihn gibt es keine Zimmer.", None
    gesucht = folder_name(name)
    if any(folder_name(z) == gesucht for z in zimmer_for(haus_key)):
        return "Ein Zimmer dieses Namens gibt es in diesem Haus schon.", None
    anderswo = [haeuser()[k]["title"] for k in haeuser() if k != haus_key
                and any(folder_name(z) == gesucht for z in zimmer_for(k))]
    if anderswo:
        return None, (f"Ein Zimmer „{name}“ gibt es schon in {', '.join(anderswo)}. "
                      "Mit zwei gleichnamigen Zimmern kann die Sekretärin BEIDE nicht "
                      "mehr beim Namen ansprechen.")
    return None, None


def zimmer_eintragen(haus_key: str, name: str) -> None:
    d = copy.deepcopy(_laden())
    liste = d["houses"][haus_key]["zimmer"]
    if name not in liste:
        liste.append(name)
    speichern(d)


def umbenennen_finden(prefs: dict, alt: str) -> "tuple[str, str, int | None] | str":
    """Das umzubenennende Zimmer: (Haus, genauer alter Name, Thema-Kennung)
    — oder ein Satz, warum es nicht eindeutig ist. Geraten wird nie."""
    gesucht = folder_name(alt or "")
    treffer = [(k, z) for k in haeuser() for z in zimmer_for(k)
               if folder_name(z) == gesucht]
    if not treffer:
        return "Ein Zimmer dieses Namens kenne ich nicht."
    if len(treffer) > 1:
        return ("Den Namen gibt es in mehreren Häusern: "
                + ", ".join(haeuser()[k]["title"] for k, _ in treffer)
                + ". Bitte zuerst eines davon in Telegram umbenennen.")
    haus, genau = treffer[0]
    tid = ((_channels_root(prefs)["houses"].get(haus) or {}).get("topics") or {}).get(genau)
    return haus, genau, (int(tid) if tid is not None else None)


def umbenennen_anwenden(prefs: dict, haus: str, alt: str, neu: str) -> dict:
    """Alle Stellen, an denen der Name der Schluessel ist, in EINEM Zug:
    Hausliste, `topics` in den Vorlieben, Routen. Gibt einen Schnappschuss
    zurueck, mit dem `umbenennen_zuruecknehmen` den Stand wiederherstellt.

    Die Vorlieben werden hier nur im Speicher geaendert — speichern muss der
    Aufrufer (der Bot besitzt die Datei)."""
    vorher = {"daten": copy.deepcopy(_laden()),
              "topics": copy.deepcopy((_channels_root(prefs)["houses"].get(haus) or {})
                                      .get("topics") or {})}
    d = copy.deepcopy(_laden())
    liste = d["houses"][haus]["zimmer"]
    d["houses"][haus]["zimmer"] = [neu if z == alt else z for z in liste]
    for quelle, (h, z) in list(d["routes"].items()):
        if h == haus and z == alt:
            d["routes"][quelle] = [haus, neu]
    speichern(d)
    topics = (_channels_root(prefs)["houses"].setdefault(haus, {})
              .setdefault("topics", {}))
    if alt in topics:
        topics[neu] = topics.pop(alt)
    return vorher


def umbenennen_zuruecknehmen(prefs: dict, haus: str, vorher: dict) -> None:
    speichern(vorher["daten"])
    (_channels_root(prefs)["houses"].setdefault(haus, {}))["topics"] = vorher["topics"]


def routen_pruefen() -> "list[str]":
    """Jede Route muss auf ein Zimmer zeigen, das in der Liste steht.

    **Claudias Auftrag 5:** Zeigt eine Route ins Leere, bleiben Berichte still
    im Bot-Chat — ein Bruch, der aussieht wie Ruhe. Ob das Zimmer in Telegram
    schon angelegt ist, prueft diese Zeile NICHT: Ein noch nicht eingerichtetes
    Haus ist ein gewollter Zustand (`resolve_route` → None, bleibt im Bot-Chat).
    """
    kaputt = []
    for quelle, (haus, zimmer) in routen().items():
        if haus not in haeuser():
            kaputt.append(f"{quelle} → unbekanntes Haus {haus}")
        elif zimmer not in zimmer_for(haus):
            kaputt.append(f"{quelle} → {haeuser()[haus]['title']} · {zimmer} (steht nicht in der Liste)")
    return kaputt
