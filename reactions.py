"""5.9 — Emoji-Reaktionen auf Bot-Nachrichten (Vokabular v2.1).

Zwei Bausteine:

1. **Vokabular** (verbindliche Referenz: reaktionen-vokabular.md, v2.1):
   Emoji → Bedeutung + Verhaltensklasse. Telegram sendet viele Emoji OHNE
   Variation Selector-16 (❤ statt ❤️, ✍ statt ✍️) — deshalb wird beim
   Abgleich IMMER normalisiert (VS16 entfernt), sonst gehen Treffer verloren.

2. **Fragen-Registratur**: „Bot-Nachricht X ist eine offene Frage" — persistent
   (überlebt Neustarts, 5.2-Prinzip: atomares Schreiben via tmp + os.replace).
   Eine eingehende Reaktion auf eine registrierte Frage ist deren ANTWORT und
   geht immer an den Agenten; Reaktionen auf sonstige Nachrichten nur, wenn
   ihre Klasse eine Handlung verlangt (stille Wertschätzung erzeugt keinen
   Lauf — kein Lärm, kein Kontingent-Verbrauch).
"""
from __future__ import annotations

import json
import logging
import os
import re
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("claude-tg-bot.reactions")

_VS16 = "️"


def normalize(emoji: str) -> str:
    """VS16 (U+FE0F) entfernen — Telegram-Reaktionen kommen meist ohne."""
    return (emoji or "").replace(_VS16, "")


@dataclass(frozen=True)
class Entry:
    meaning: str   # Klartext-Bedeutung laut Vokabular (geht 1:1 an den Agenten)
    kind: str      # Verhaltensklasse
    active: bool   # True = löst auch OHNE registrierte Frage einen Agenten-Lauf aus


# Vokabular v2.1 (reaktionen-vokabular.md) — Schlüssel VS16-normalisiert.
# active=False: reine Wertschätzung → ohne offene Frage nur Gesprächs-Log.
_RAW_VOCAB: dict[str, Entry] = {
    # Ja/Nein & Bestätigung
    "👍": Entry("Ja / passt / finde gut / Dank", "ja", True),
    "👌": Entry("Ja / OK / alles klar", "ja", True),
    "🫡": Entry("Ja — bzw. erledigt, wenn es eine Aufgabe für mich war", "ja", True),
    "👎": Entry("Nein", "nein", True),
    # Dank & Beziehung
    "❤️": Entry("Herzlichen Dank / Freude", "dank", False),
    "🙏": Entry("Bitte oder Danke (im Zweifel kurz nachfragen)", "dank", False),
    "🤗": Entry("Freu mich", "dank", False),
    "🎉": Entry("Lass uns feiern", "dank", False),
    # Feedback & Genuss
    "👏": Entry("Stark / Anerkennung", "dank", False),
    "💯": Entry("Genau so, voll richtig", "genau", False),
    "🍓": Entry("Lecker, süß, köstlich", "dank", False),
    "🍌": Entry("Geil", "dank", False),
    "🤔": Entry("Unsicher / lass mich überlegen (kein Ja/Nein)", "unsicher", True),
    "🤨": Entry("Versteh ich nicht / erklär nochmal", "unklar", True),
    "🤷": Entry("Versteh ich nicht / erklär nochmal", "unklar", True),
    "🤷‍♂️": Entry("Versteh ich nicht / erklär nochmal", "unklar", True),
    "🤷‍♀️": Entry("Versteh ich nicht / erklär nochmal", "unklar", True),
    # Steuerung & Tempo
    "🔥": Entry("Los geht's / lass es krachen / kann es kaum erwarten", "los", True),
    "⚡": Entry("Los geht's / lass es krachen / kann es kaum erwarten", "los", True),
    "👀": Entry("Genauer anschauen / besser hinsehen", "anschauen", True),
    "✍️": Entry("Wichtig / merk dir das", "merken", True),
    "👨‍💻": Entry("Wichtig / merk dir das", "merken", True),
    "🏆": Entry("Wichtig / merk dir das", "merken", True),
    "😴": Entry("Später / erinnere mich", "spaeter", True),
}
VOCAB: dict[str, Entry] = {normalize(k): v for k, v in _RAW_VOCAB.items()}


def lookup(emoji: str) -> Entry | None:
    return VOCAB.get(normalize(emoji))


# ---------- Fragen-Registratur (persistent, atomar) ----------

QUESTIONS_FILE = Path(
    os.environ.get("QUESTIONS_FILE")
    or str(Path(__file__).parent / "logs" / "open_questions.json")
)
_MAX_QUESTIONS = 80  # Kappung: älteste fliegen raus (Reaktionen kommen zeitnah)

# Fragezeichen im letzten Abschnitt = der Bot wartet vermutlich auf eine Antwort.
_QUESTION_TAIL = 260


def _load() -> dict[str, dict]:
    try:
        return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict[str, dict]) -> None:
    try:
        QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(QUESTIONS_FILE.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, QUESTIONS_FILE)
    except Exception:
        log.exception("Fragen-Registratur nicht speicherbar (nicht-fatal)")


def _qkey(chat_id: int, message_id: int) -> str:
    return f"{chat_id}_{message_id}"


def looks_like_question(text: str) -> bool:
    """Heuristik: Fragezeichen im Schlussteil → Bot wartet auf Antwort."""
    return "?" in (text or "")[-_QUESTION_TAIL:]


def register_question(chat_id: int, message_id: int | None, text: str) -> None:
    """Bot-Nachricht als offene Frage festhalten (nur wenn sie wie eine aussieht)."""
    if not message_id or not looks_like_question(text):
        return
    data = _load()
    data[_qkey(chat_id, message_id)] = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": " ".join((text or "").split())[-600:],
        "created": time.time(),
    }
    if len(data) > _MAX_QUESTIONS:
        for k in sorted(data, key=lambda k: data[k].get("created", 0))[: len(data) - _MAX_QUESTIONS]:
            data.pop(k, None)
    _save(data)


def pop_question(chat_id: int, message_id: int) -> dict | None:
    """Registrierte Frage zu dieser Nachricht holen UND austragen (beantwortet)."""
    data = _load()
    entry = data.pop(_qkey(chat_id, message_id), None)
    if entry is not None:
        _save(data)
    return entry


def open_count() -> int:
    return len(_load())


# ---------- Nummerierte Optionslisten (1️⃣–9️⃣ als Inline-Knöpfe) ----------

_OPTION_LINE = re.compile(r"^\s{0,3}([1-9])[\.\)]\s+\S", re.MULTILINE)


def detect_numbered_options(text: str) -> int:
    """Anzahl der Optionen einer nummerierten Liste (ab 1, lückenlos), sonst 0.

    Telegram bietet keine Ziffern-Emoji als Reaktion an — erkannte Listen
    bekommen deshalb Inline-Knöpfe direkt an der Nachricht (Adam-Entscheid,
    reaktionen-vokabular.md „Über gleichwertigen Weg")."""
    nums = [int(m.group(1)) for m in _OPTION_LINE.finditer(text or "")]
    seen: list[int] = []
    for n in nums:
        if n == len(seen) + 1:
            seen.append(n)
    return len(seen) if len(seen) >= 2 else 0
