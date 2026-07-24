"""Telegram bridge for Claude Code / Agent SDK.

One Telegram user maps to one persistent Claude session. Each incoming message
is forwarded to the agent; assistant text streams back as Telegram messages.
Tool-permission requests are rendered as inline keyboards (Allow / Deny / Always).
"""

from __future__ import annotations

import asyncio
import json as _json
import re
import logging
import os
import socket
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, ReactionTypeEmoji, ReplyKeyboardMarkup, ReplyParameters, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    MessageReactionHandler,
    filters,
)

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolPermissionContext,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    tool,
    create_sdk_mcp_server,
)

import tempfile

from transcribe import Transcriber, build_transcriber
import ampel
import channels
import pending
import presend
import reactions

load_dotenv(Path(__file__).parent / ".env")

# ---------- user prefs (überleben Session-Reset und Bot-Neustart) ----------

_PREFS_FILE = Path.home() / ".config" / "claude-telegram-bot" / "prefs.json"


def _load_prefs() -> dict:
    try:
        if _PREFS_FILE.exists():
            import json
            return json.loads(_PREFS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_prefs(prefs: dict) -> None:
    try:
        import json
        _PREFS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _PREFS_FILE.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    except Exception:
        log.exception("prefs save failed (non-fatal)")


_USER_PREFS: dict = _load_prefs()

# ---------- usage tracking ----------

_USAGE_FILE = Path.home() / ".config" / "claude-telegram-bot" / "usage.json"


def _load_usage() -> dict:
    try:
        if _USAGE_FILE.exists():
            return _json.loads(_USAGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_usage(data: dict) -> None:
    try:
        _USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _USAGE_FILE.write_text(_json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        log.exception("usage save failed (non-fatal)")


def _record_usage(model: str, result: Any) -> None:
    today = time.strftime("%Y-%m-%d")
    data = _load_usage()
    day = data.setdefault(today, {})
    bucket = day.setdefault(model, {"input": 0, "output": 0, "requests": 0, "cost_usd": 0.0})
    bucket["requests"] += 1
    if result.usage:
        bucket["input"] += result.usage.get("input_tokens", 0)
        bucket["output"] += result.usage.get("output_tokens", 0)
    if result.total_cost_usd:
        bucket["cost_usd"] = bucket.get("cost_usd", 0.0) + result.total_cost_usd
    _save_usage(data)


def _usage_today() -> dict:
    today = time.strftime("%Y-%m-%d")
    return _load_usage().get(today, {})


# ---------- memory loader ----------

_MEMORY_DIR = Path(os.environ.get("CLAUDE_MEMORY_DIR") or str(Path.home() / ".claude/projects/-Users-jakuna/memory"))
_MEMORY_CACHE: str | None = None
_MEMORY_MTIME: float = 0.0


# Session-Diät (5.23): Diese Typen werden IMMER voll geladen (Identität +
# Verhaltensregeln — dürfen nie fehlen). Alles andere (project/reference =
# dickes Detailwissen) wird nur als "bei Bedarf nachlesen"-Liste referenziert.
_MEMORY_ALWAYS_TYPES = {"user", "feedback", ""}


def _read_memory_file(path: Path) -> tuple[str, str]:
    """Gibt (type, Body-ohne-Frontmatter) einer Memory-Datei zurück."""
    import re
    text = path.read_text(encoding="utf-8")
    mtype = ""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end >= 0:
            m = re.search(r"^\s*type:\s*([A-Za-z_]+)", text[3:end], re.MULTILINE)
            if m:
                mtype = m.group(1).strip().lower()
            text = text[end + 3:].lstrip("\n")
    return mtype, text.strip()


def load_user_memory() -> str:
    """Lädt einen schlanken Kern (Identität + Verhaltensregeln + Index) voll;
    dickes Projekt-/Referenzwissen wird als 'bei Bedarf nachlesen'-Liste
    referenziert, statt bei jedem Session-Start ~280 KB vorzuladen
    (Session-Diät 5.23). Gecacht bis MEMORY.md sich ändert."""
    global _MEMORY_CACHE, _MEMORY_MTIME
    import re
    index_path = _MEMORY_DIR / "MEMORY.md"
    if not index_path.exists():
        return ""
    try:
        mtime = index_path.stat().st_mtime
        if _MEMORY_CACHE is not None and mtime == _MEMORY_MTIME:
            return _MEMORY_CACHE
        index = index_path.read_text(encoding="utf-8")
        core: list[str] = [
            "# Nutzer-Kontext — Kern (Identität & Verhaltensregeln, gelten IMMER)\n"
        ]
        ondemand: list[str] = []
        for m in re.finditer(
            r"\[([^\]]*)\]\(([^)]+\.md)\)[ \t]*(?:[—-][ \t]*([^\n]*))?", index
        ):
            title, fname, hook = m.group(1), m.group(2), (m.group(3) or "").strip()
            mem_file = _MEMORY_DIR / fname
            if not mem_file.exists():
                continue
            mtype, body = _read_memory_file(mem_file)
            if mtype in _MEMORY_ALWAYS_TYPES:
                core.append(body)
            else:
                ondemand.append(f"- **{title}** — {hook}\n  → Datei: {mem_file}")
        parts = ["\n\n---\n\n".join(core)]
        if ondemand:
            parts.append(
                "# WEITERES GEDÄCHTNIS — BEI BEDARF NACHLESEN (bewusst NICHT vorgeladen)\n"
                "Folgende Themen (v. a. Projekt-Details) liegen als einzelne Dateien im "
                "Memory-Ordner und sind aus Tempo-Gründen NICHT vorgeladen. Sobald du für "
                "die aktuelle Aufgabe Details zu einem Punkt brauchst, lies die genannte "
                "Datei mit dem Read-Tool — der Zugriff auf diesen Ordner ist ohne Rückfrage "
                "erlaubt. Rate nicht, wenn das Detail hier liegt: lies nach.\n\n"
                + "\n".join(ondemand)
            )
        _MEMORY_CACHE = "\n\n---\n\n".join(parts)
        _MEMORY_MTIME = mtime
        return _MEMORY_CACHE
    except Exception:
        logging.getLogger("claude-tg-bot").exception("load_user_memory (lean) fehlgeschlagen")
        return ""


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
log = logging.getLogger("claude-tg-bot")
logging.getLogger("httpx").setLevel(logging.WARNING)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_IDS = {
    int(uid.strip())
    for uid in os.environ["ALLOWED_USER_IDS"].split(",")
    if uid.strip()
}
WORKDIR = Path(os.environ.get("CLAUDE_WORKDIR") or str(Path.home())).expanduser()
_DEFAULT_LOG_DIR = Path.home() / "claude-logs"  # VPS-tauglicher Fallback; Mac kann CONVERSATION_LOG_DIR auf iCloud zeigen
LOG_DIR = Path(os.environ.get("CONVERSATION_LOG_DIR") or str(_DEFAULT_LOG_DIR))
TELEGRAM_MSG_LIMIT = 4000  # actual is 4096; leave headroom for formatting
VOICE_LANGUAGE = os.environ.get("VOICE_LANGUAGE") or "de"
TTS_VOICE = os.environ.get("TTS_VOICE") or "de-DE-KatjaNeural"
TTS_CHUNK_CHARS = 4000  # max. Zeichen pro Sprachnachricht (PDF-Vorlesen etc.)
TTS_SYNC_CHUNK = 1024  # max. Zeichen pro Text-Chunk wenn TTS-Sync-Modus aktiv
_RESTART_REASON_FILE = Path.home() / ".claude/bot-restart-reason.txt"
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR") or str(Path.home() / "Downloads" / "claude-uploads"))
DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")
# Kurznamen → vollständige Modell-IDs, die das SDK versteht
_MODEL_ALIASES: dict[str, str] = {
    "opus":   "claude-opus-4-8",   # angehoben 22.07. nach OAuth-Probe (war 4-7)
    "sonnet": "claude-sonnet-5",   # angehoben 22.07. nach OAuth-Probe (war 4-6)
    "haiku":  "claude-haiku-4-5-20251001",
    "fable":  "claude-fable-5",
}
# Nachrichten, die während einer Ausfallzeit (Mac-Schlaf, Neustart) reinkamen,
# MÜSSEN den Neustart überleben — sonst geht z.B. eine Sprachnachricht verloren,
# bevor sie je transkribiert/geloggt wird (für mich dann unsichtbar). Telegram
# puffert sie server-seitig ~24h; mit False holt der Bot sie beim Start nach.
# Veraltete Permission-Klicks sind kein Grund zu droppen — on_permission_callback
# fängt sie bereits sauber ab ("Session weg"/"bereits beantwortet").
DROP_PENDING_UPDATES = False

# ---------- persistente Tastatur (ReplyKeyboard) ----------
_BTN_OPUS = "🔵 Opus"
_BTN_SONNET = "🟡 Sonnet"
_BTN_HAIKU = "🟣 Haiku"
_BTN_FABLE = "🟠 Fable"
_BTN_TTS_ON = "🔊 TTS an"
_BTN_TTS_OFF = "🔇 TTS aus"
_BTN_OPUS_ACTIVE = "🔵 Opus ✓"
_BTN_SONNET_ACTIVE = "🟡 Sonnet ✓"
_BTN_HAIKU_ACTIVE = "🟣 Haiku ✓"
_BTN_FABLE_ACTIVE = "🟠 Fable ✓"
_BTN_RESTART = "🔄 Neustart"
_BTN_INFO = "ℹ️ Info"
# Thinking-Effort-Buttons: ⚖️ Normal (default) / ⚡ Schnell (low) / 🚀 Max
_BTN_EFFORT_LOW = "⚡ Schnell"
_BTN_EFFORT_MED = "⚖️ Normal"
_BTN_EFFORT_MAX = "🚀 Max"
_BTN_EFFORT_LOW_ACTIVE = "⚡ Schnell ✓"
_BTN_EFFORT_MED_ACTIVE = "⚖️ Normal ✓"
_BTN_EFFORT_MAX_ACTIVE = "🚀 Max ✓"
# STT-Tempo-Knopf — FINALE Form (Adam 23.07., zweite Runde): „🎙️ Genau ✓ → Flott"
# = Genau ist aktiv (✓), ein Tipp wechselt zu Flott. Der Pfeil steht bewusst AUF
# dem Knopf: Bei Reply-Tastaturen ist der Knopftext wortgleich die gesendete
# Nachricht — nur so zeigt Adams eigene Chat-Nachricht den Wechsel („Genau ✓ →
# Flott"), und die Bot-Bestätigung fettet den neuen Zustand.
_BTN_STT_ACC_TO_FAST = "🎙️ Genau ✓ → Flott"   # medium aktiv; Tipp → small
_BTN_STT_FAST_TO_ACC = "🎙️ Flott ✓ → Genau"   # small aktiv; Tipp → medium
# Alt-Beschriftungen (bis 23.07.): bleiben gemappt, weil Telegram-Tastaturen
# client-seitig weiterleben, bis der Client eine neue bekommt.
_BTN_STT_TO_FAST = "🎙️ Genau → Flott"
_BTN_STT_TO_ACCURATE = "🎙️ Flott → Genau"
_BTN_STT_ACCURATE = "🎙️ Genau"
_BTN_STT_FAST = "🎙️ Flott"
_BTN_STT_ACCURATE_ACTIVE = "🎙️ Genau ✓"
_BTN_STT_FAST_ACTIVE = "🎙️ Flott ✓"
# 🎯 Gründlich: einmalig die NÄCHSTE Anfrage im AKTIV gewählten Modell mit hohem
# Effort + Pflicht-Quellencheck beantworten (für wichtige Fragen, die stimmen
# müssen). Danach wieder Standard. Kein Opus-Zwang mehr (Adam-Entscheid 22.07.).
_BTN_THOROUGH = "🎯 Gründlich"
_THOROUGH_PENDING: set[int] = set()
# Ampel-Regel-Erfassungsmodus (/ampel → ➕ Neue Regel → Farbe → nächste Nachricht
# wird DETERMINISTISCH (ohne Claude) als Regel übernommen). Verfällt nach 60 s.
_AMPEL_CAPTURE: dict[int, dict] = {}
_AMPEL_CAPTURE_TTL = 60  # Sekunden
# 5.2 Schritt 2: Vermerk für nach einem Neustart nachgeholte Nachrichten. Ohne ihn
# beantwortet der Agent sie so, als kämen sie gerade eben — die Zeitzeile nennt
# zwar Eingang UND Jetzt, der Grund für die Lücke bliebe aber unerklärt.
_RESUMED_PREFIX = (
    "[NACHGEHOLT: Diese Nachricht kam vor einem Neustart an und blieb unbeantwortet — "
    "sie wird jetzt nachgeholt. Geh normal darauf ein; die Verzögerung nur erwähnen, "
    "wenn sie inhaltlich eine Rolle spielt (z. B. bei Zeitbezügen wie „heute“).]\n\n"
)
_THOROUGH_PREFIX = (
    "[GRÜNDLICH-MODUS — diese Frage muss stimmen: Prüfe Fakten AKTIV über Quellen "
    "(Websuche/Nachlesen) statt aus dem Gedächtnis; kennzeichne jede Unsicherheit "
    "ausdrücklich; keine ungeprüften Behauptungen. Nimm dir Zeit für eine "
    "sorgfältige, belegte Antwort.]\n\n"
)
# Ein-Knopf-Toggle (Layout Y; Beschriftung final 23.07., Adam-Wunsch): Der Knopf
# zeigt NUR den aktiven Modus („🎙️ Flott"), ein Tipp wechselt zum anderen —
# den Wechsel-Pfeil („Flott → Genau") trägt die BOT-Bestätigung, nicht der Knopf
# (bei Reply-Tastaturen ist der Knopftext zwangsläufig die gesendete Nachricht).
_STT_BTN_TARGET = {
    _BTN_STT_ACC_TO_FAST: "small",    # „Genau ✓ → Flott" gedrückt → Flott
    _BTN_STT_FAST_TO_ACC: "medium",   # „Flott ✓ → Genau" gedrückt → Genau
    # Übergangs-/Alt-Labels (bleiben gemappt für client-seitige Alt-Tastaturen):
    _BTN_STT_ACCURATE: "small",
    _BTN_STT_FAST: "medium",
    _BTN_STT_TO_FAST: "small",
    _BTN_STT_TO_ACCURATE: "medium",
    _BTN_STT_ACCURATE_ACTIVE: "small",
    _BTN_STT_FAST_ACTIVE: "medium",
}
_ALL_KEYBOARD_BTNS = {_BTN_OPUS, _BTN_SONNET, _BTN_HAIKU, _BTN_FABLE,
                      _BTN_TTS_ON, _BTN_TTS_OFF,
                      _BTN_OPUS_ACTIVE, _BTN_SONNET_ACTIVE, _BTN_HAIKU_ACTIVE,
                      _BTN_FABLE_ACTIVE,
                      _BTN_RESTART, _BTN_INFO,
                      _BTN_EFFORT_LOW, _BTN_EFFORT_MED, _BTN_EFFORT_MAX,
                      _BTN_EFFORT_LOW_ACTIVE, _BTN_EFFORT_MED_ACTIVE, _BTN_EFFORT_MAX_ACTIVE,
                      _BTN_STT_ACC_TO_FAST, _BTN_STT_FAST_TO_ACC,
                      _BTN_STT_TO_FAST, _BTN_STT_TO_ACCURATE,
                      _BTN_STT_ACCURATE, _BTN_STT_FAST,
                      _BTN_STT_ACCURATE_ACTIVE, _BTN_STT_FAST_ACTIVE,
                      _BTN_THOROUGH}
# Aliase statt fester Versionen → Bot nutzt automatisch das jeweils
# höchstwertige aktuelle Modell, Label muss bei neuen Versionen nicht angepasst werden.
_MODEL_IDS = {
    _BTN_OPUS: "opus",
    _BTN_OPUS_ACTIVE: "opus",
    _BTN_SONNET: "sonnet",
    _BTN_SONNET_ACTIVE: "sonnet",
    _BTN_HAIKU: "haiku",
    _BTN_HAIKU_ACTIVE: "haiku",
    _BTN_FABLE: "fable",
    _BTN_FABLE_ACTIVE: "fable",
}


def _model_btn_label(m: str) -> str:
    """Emoji-Label zu einem Modell-Kürzel/-Namen — EINE Stelle für alle Anzeigen."""
    if "opus" in m:
        return "🔵 Opus"
    if "sonnet" in m:
        return "🟡 Sonnet"
    if "haiku" in m:
        return "🟣 Haiku"
    if "fable" in m:
        return "🟠 Fable"
    return f"❓ {m}"


# Mapping Button → effort-String (None = SDK-Default)
_EFFORT_IDS: dict[str, str | None] = {
    _BTN_EFFORT_LOW: "low",
    _BTN_EFFORT_LOW_ACTIVE: "low",
    _BTN_EFFORT_MED: None,
    _BTN_EFFORT_MED_ACTIVE: None,
    _BTN_EFFORT_MAX: "max",
    _BTN_EFFORT_MAX_ACTIVE: "max",
}


# ---------- auth-error helper ----------

def is_auth_error(exc: Exception) -> bool:
    """True wenn eine Exception nach einem Anthropic-Auth-/Credentials-Fehler aussieht.
    Der Claude-Subprozess bubbles die Fehler als Text hoch — zuverlässigster Indikator."""
    msg = str(exc).lower()
    needles = (
        "401",
        "invalid authentication",
        "invalid x-api-key",
        "authentication_error",
        "failed to authenticate",
        "could not resolve authentication",
        "oauth token has expired",
    )
    return any(n in msg for n in needles)


def is_context_overflow(exc: Exception) -> bool:
    """True bei Kontextfenster-/‚prompt too long'-Fehlern (Session voll).
    Wie is_auth_error anhand des durchgereichten Fehlertexts."""
    msg = str(exc).lower()
    needles = (
        "prompt is too long",
        "context length",
        "context_length_exceeded",
        "context window",
        "maximum context",
        "too many tokens",
        "exceeds the maximum",
        "input is too long",
        "reduce the length",
    )
    return any(n in msg for n in needles)


AUTH_HELP = (
    "🔑 *Authentifizierung fehlgeschlagen* (401)\n\n"
    "Der Claude-Subprozess kann sich nicht bei Anthropic anmelden — "
    "das liegt an den Credentials, nicht am Bot.\n\n"
    "*So behebst du es (Abo-Auth, kostenfrei):*\n"
    "• Neuen Abo-Token erzeugen: `claude setup-token` — als "
    "`CLAUDE_CODE_OAUTH_TOKEN` in das systemd-EnvironmentFile (oder die launchd-Plist) eintragen.\n"
    "• Prüfen, dass NIRGENDS ein `ANTHROPIC_API_KEY` gesetzt ist — "
    "der hätte Vorrang und kostet extra (💰 Kostenregel!).\n"
    "• Test ohne Bot: `claude -p \"hallo\"` im selben Kontext.\n\n"
    "Die kaputte Session wurde verworfen — nach dem Fix einfach eine neue Nachricht schicken."
)


def _discover_stt_models() -> dict[str, str]:
    """Vorhandene Whisper-Modelle im models/-Ordner (neben WHISPER_MODEL_PATH)."""
    raw = os.environ.get("WHISPER_MODEL_PATH")
    base = Path(raw).expanduser().parent if raw else (Path(__file__).parent / "models")
    out: dict[str, str] = {}
    for name in ("tiny", "base", "small", "medium", "large"):
        p = base / f"ggml-{name}.bin"
        if p.is_file():
            out[name] = str(p)
    return out


_STT_MODELS: dict[str, str] = _discover_stt_models()


def _default_stt_name() -> str:
    raw = os.environ.get("WHISPER_MODEL_PATH", "")
    for name in _STT_MODELS:
        if f"ggml-{name}.bin" in raw:
            return name
    return "medium" if "medium" in _STT_MODELS else next(iter(_STT_MODELS), "medium")


# Global aktives STT-Modell (Einzelnutzer-Bot). Persistiert in den Prefs.
_ACTIVE_STT: str = _default_stt_name()
for _p in _USER_PREFS.values():
    if isinstance(_p, dict) and _p.get("stt_model") in _STT_MODELS:
        _ACTIVE_STT = _p["stt_model"]
        break

_STT_LABELS = {"medium": "Genau (medium)", "small": "Flott (small)",
               "base": "Sehr flott (base)", "tiny": "Turbo (tiny)", "large": "Höchste (large)"}


def _stt_label(name: str) -> str:
    return _STT_LABELS.get(name, name)


def _main_keyboard(tts_on: bool, model: str, effort: str | None = None) -> ReplyKeyboardMarkup:
    # Layout Y (Adam-Entscheid 22.07.): Zeile 1+2 = Dauer-Zustand (Modelle,
    # Effort-Stufen), Zeile 3 = Umschalter/Einmal-Aktionen (STT-Toggle, Gründlich).
    haiku_label = _BTN_HAIKU_ACTIVE if "haiku" in model else _BTN_HAIKU
    sonnet_label = _BTN_SONNET_ACTIVE if "sonnet" in model else _BTN_SONNET
    opus_label = _BTN_OPUS_ACTIVE if "opus" in model else _BTN_OPUS
    fable_label = _BTN_FABLE_ACTIVE if "fable" in model else _BTN_FABLE
    low_label = _BTN_EFFORT_LOW_ACTIVE if effort == "low" else _BTN_EFFORT_LOW
    med_label = _BTN_EFFORT_MED_ACTIVE if effort is None else _BTN_EFFORT_MED
    max_label = _BTN_EFFORT_MAX_ACTIVE if effort == "max" else _BTN_EFFORT_MAX
    rows = [
        [haiku_label, sonnet_label, opus_label, fable_label],
        [low_label, med_label, max_label],
    ]
    # Neustart / TTS / Info bewusst NICHT mehr als Dauer-Buttons (Adam 17.07.):
    # sie liegen jetzt im „/"-Befehlsmenü (setMyCommands) → Tastatur schlank.
    # `tts_on` bleibt im Signatur-Vertrag (Aufrufer geben es weiter), wird hier
    # aber nicht mehr für einen Button gebraucht — TTS via /tts.
    # STT als EIN-Knopf-Toggle (finale Form): „🎙️ Genau ✓ → Flott" = Genau aktiv,
    # Tipp wechselt zu Flott — Adams gesendete Nachricht zeigt so den Wechsel.
    # Nur wenn beide Modelle da sind.
    if "small" in _STT_MODELS and "medium" in _STT_MODELS:
        stt_toggle = (_BTN_STT_FAST_TO_ACC if _ACTIVE_STT == "small"
                      else _BTN_STT_ACC_TO_FAST)
        rows.append([stt_toggle, _BTN_THOROUGH])
    else:
        rows.append([_BTN_THOROUGH])
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
    )


_output_ch_raw = os.environ.get("OUTPUT_CHANNEL_ID", "").strip()
OUTPUT_CHANNEL_ID: int | None = int(_output_ch_raw) if _output_ch_raw else None

# Bot-Username (für Rücksprung-Links aus dem Ausgabekanal in den Bot-Chat).
# Wird in post_init einmalig via get_me() gefüllt.
_BOT_USERNAME: str | None = None


def _back_to_bot_markup() -> InlineKeyboardMarkup | None:
    """Inline-Button im Ausgabekanal: ein Tap zurück in den Bot-Chat (Kommandobrücke).
    Öffnet die App direkt im Bot-Chat, kein Browser-Umweg."""
    if not _BOT_USERNAME:
        return None
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("↩️ Zurück zur Kommandobrücke",
                               url=f"https://t.me/{_BOT_USERNAME}")]]
    )


def _channel_url(channel_id: int, username: str | None = None) -> str:
    if username:
        return f"https://t.me/{username}"
    pure = str(channel_id)[4:] if str(channel_id).startswith("-100") else str(channel_id)
    return f"https://t.me/c/{pure}/"


def _channel_post_url(channel_id: int, message_id: int) -> str:
    """Nativer In-App-Deep-Link zu einem konkreten Kanal-Post (öffnet die App, kein Browser)."""
    pure = str(channel_id)[4:] if str(channel_id).startswith("-100") else str(channel_id)
    return f"tg://privatepost?channel={pure}&post={message_id}"


def _channel_title_link_html(channel_id: int, title: str,
                              username: str | None = None,
                              message_id: int | None = None) -> str:
    """Klickbarer HTML-Anchor auf den Kanal — direkter In-App-Sprung, kein
    Browser-Umweg. Bei öffentlichem Kanal (Username) `https://t.me/<username>`,
    bei privatem Kanal `tg://privatepost?channel=...`. Mit `message_id` wird
    der Sprung auf einen konkreten Beitrag verfeinert.

    Voraussetzung beim Verwenden: parse_mode=ParseMode.HTML auf der Nachricht.
    """
    import html as _html
    safe_title = _html.escape(title or str(channel_id))
    if username:
        href = f"https://t.me/{username}"
        if message_id:
            href = f"{href}/{message_id}"
    else:
        pure = str(channel_id)[4:] if str(channel_id).startswith("-100") else str(channel_id)
        if message_id:
            href = f"tg://privatepost?channel={pure}&post={message_id}"
        else:
            href = f"tg://privatepost?channel={pure}"
    return f'<a href="{href}">{safe_title}</a>'


def _channel_post_markup(
    channel_id: int,
    message_id: int | None = None,
    username: str | None = None,
    orig_message_id: int | None = None,
) -> InlineKeyboardMarkup:
    """Inline-Button(s) für den direkten In-App-Sprung in den Kanal/Post.
    Buttons lösen KEINEN 'Link öffnen?'-Dialog aus (anders als tg://-Textlinks)."""

    def _u(mid: int | None) -> str:
        if username:
            return f"https://t.me/{username}" + (f"/{mid}" if mid else "")
        if mid:
            return _channel_post_url(channel_id, mid)
        pure = str(channel_id)[4:] if str(channel_id).startswith("-100") else str(channel_id)
        return f"https://t.me/c/{pure}"

    rows = [[InlineKeyboardButton("📂 Im Kanal öffnen", url=_u(message_id))]]
    if orig_message_id:
        rows.append([InlineKeyboardButton("📄 Original öffnen", url=_u(orig_message_id))])
    return InlineKeyboardMarkup(rows)


def get_output_channel() -> tuple[int | None, str, str]:
    """Gibt (id, title, url) des konfigurierten Output-Kanals zurück."""
    cid_raw = _USER_PREFS.get("output_channel_id") or OUTPUT_CHANNEL_ID
    if not cid_raw:
        return None, "", ""
    cid = int(cid_raw)
    title = _USER_PREFS.get("output_channel_title") or str(cid)
    url = _channel_url(cid, _USER_PREFS.get("output_channel_username"))
    return cid, title, url


def get_summary_channel() -> int | None:
    """Kanal-ID für Zusammenfassungen — nutzt gemeinsamen output_channel_id."""
    ch = _USER_PREFS.get("output_channel_id") or _USER_PREFS.get("summary_channel_id")
    return int(ch) if ch else OUTPUT_CHANNEL_ID


def get_tts_channel() -> int | None:
    """Kanal-ID für TTS-Vorlesung — nutzt gemeinsamen output_channel_id."""
    ch = _USER_PREFS.get("output_channel_id") or _USER_PREFS.get("tts_channel_id")
    return int(ch) if ch else OUTPUT_CHANNEL_ID


def route_target(source: str) -> tuple[int, int, str] | None:
    """6.1: Löst eine Auto-Routing-Quelle ('research'/'bot_status'/'unassigned')
    zu (chat_id, thread_id, ziel_url) auf — oder None, wenn das Zielhaus/-zimmer
    noch nicht existiert. Bewusst KEIN Fallback auf den Alt-Ausgabekanal: None
    heißt „kein Auto-Ziel", der Aufrufer behält sein bisheriges Verhalten."""
    hit = channels.resolve_route(_USER_PREFS, source)
    if not hit:
        return None
    chat_id, thread_id = hit
    url = _channel_url(chat_id, None)
    return chat_id, thread_id, url

# Pending PDF-Entscheidungen: user_id → dict mit Dateiinfos
_PENDING_DOCS: dict[int, dict] = {}

# Built lazily on first use so an STT misconfig only breaks /voice, not the whole bot.
_TRANSCRIBER: Transcriber | None = None


class ConversationLogger:
    """Appends each exchange to a Markdown file in iCloud (or LOG_DIR).

    Tageswechsel-Fix (22.07.2026): Die Zieldatei wird bei JEDEM Schreibvorgang
    aus dem aktuellen Datum bestimmt — zuvor wurde der Pfad einmalig im
    __init__ eingefroren, und langlebige Sessions schrieben tagelang in die
    Datei ihres Starttags (Fund: 2026-07-20.md enthielt Einträge bis 22.07.).
    Beim ersten Eintrag eines neuen Tages beginnt die neue Tagesdatei mit
    Kopfzeile; die alte erhält eine Verweiszeile. Turn-Kopfzeilen tragen das
    volle Datum, damit jeder Eintrag auch für sich genommen eindeutig ist.
    """

    def __init__(self, user_id: int) -> None:
        self._disabled = False
        self._date: str | None = None  # Tag der aktuell beschriebenen Datei
        self._path: Path | None = None
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            self._roll_if_needed()
            with self._path.open("a", encoding="utf-8") as f:
                f.write(f"## Session · {self._stamp()} · {WORKDIR}\n\n---\n\n")
            log.info("conversation log: %s", self._path)
        except Exception:
            log.exception("conversation log init failed (non-fatal)")
            self._disabled = True

    @staticmethod
    def _stamp() -> str:
        """Voller Zeitstempel inkl. Datum — Tagesgrenzen waren sonst unsichtbar."""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def log_user(self, text: str) -> None:
        self._append(f"## Du · {self._stamp()}\n\n{text}\n\n")

    def log_event(self, text: str) -> None:
        """Meta-Zeile (kursiv) vor einem Eintrag — z. B. „🎙️ Sprachnachricht (8:55)"
        oder „📎 Datei: bericht.pdf · PDF · 1,2 MB". Macht die Tagesdatei zum
        vollwertigen Screenshot-Ersatz für die Kontrollsitzung (22.07.)."""
        self._append(f"*{text}*\n\n")

    def start_assistant_turn(self) -> None:
        self._append(f"## Claude · {self._stamp()}\n\n")

    def log_assistant_text(self, text: str) -> None:
        self._append(f"{text}\n\n")

    def log_tool(self, tool_name: str) -> None:
        self._append(f"*🔧 {tool_name}*\n\n")

    def end_turn(self) -> None:
        self._append("---\n\n")

    def _roll_if_needed(self) -> None:
        """Zieldatei aus dem AKTUELLEN Datum bestimmen (Tageswechsel-Behandlung)."""
        date_str = time.strftime("%Y-%m-%d")
        if date_str == self._date and self._path is not None:
            return
        old_path = self._path
        new_path = LOG_DIR / f"{date_str}.md"
        if old_path is not None and old_path != new_path:
            # Abschlusszeile in der alten Tagesdatei — der Faden bleibt verfolgbar.
            try:
                with old_path.open("a", encoding="utf-8") as f:
                    f.write(f"\n*→ fortgesetzt in {date_str}.md*\n")
            except Exception:
                log.exception("conversation log: Verweiszeile fehlgeschlagen (non-fatal)")
        if not new_path.exists():
            with new_path.open("a", encoding="utf-8") as f:
                f.write(f"# Claude Telegram Log – {date_str}\n\n")
        self._path = new_path
        self._date = date_str

    def _append(self, text: str) -> None:
        if self._disabled:
            return
        try:
            self._roll_if_needed()
            with self._path.open("a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            log.exception("conversation log write failed (non-fatal)")


def get_transcriber() -> Transcriber:
    global _TRANSCRIBER
    if _TRANSCRIBER is None:
        _TRANSCRIBER = build_transcriber()
    return _TRANSCRIBER


# 5.15/Zuverlässigkeit (24.07.): bot-eigenes Fehlerlog — die Kontrollsitzung
# liest es über den Log-Sync, ohne journalctl-Zugriff zu brauchen.
_BOT_ERROR_LOG = Path(LOG_DIR).parent / "bot-errors.log"


def _log_bot_error(context: str, exc: BaseException) -> None:
    """Hängt einen Fehler ans bot-eigene Fehlerlog (best effort, nie fatal)."""
    try:
        _BOT_ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with _BOT_ERROR_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp} | {context} | {type(exc).__name__}: {exc}\n")
    except Exception:
        log.warning("konnte bot-errors.log nicht schreiben", exc_info=True)


async def _with_one_retry(factory, what: str, pause: float = 2.0):
    """Führt eine Netz-Operation aus; bei Fehler EINMAL nach kurzer Pause erneut.
    5.15: transiente getFile-/Download-Timeouts sollen nicht sofort scheitern —
    NUR dieser Pfad (kein globaler Retry). Scheitert auch der zweite Versuch,
    propagiert der Fehler an den Aufrufer (der die ❌-Meldung schickt)."""
    try:
        return await factory()
    except Exception as e:
        _log_bot_error(f"{what} (1. Versuch)", e)
        log.warning("%s fehlgeschlagen (%s) — ein Wiederholversuch in %.1fs",
                    what, e, pause)
        await asyncio.sleep(pause)
        return await factory()


async def _download_tg_file(file_obj, filename: str) -> Path:
    """Lädt eine Telegram-Datei in UPLOAD_DIR; gibt den lokalen Pfad zurück.

    Der Name trägt neben dem Sekunden-Zeitstempel eine eindeutige Kennung —
    kommen mehrere Dateien in DERSELBEN Sekunde an (live 22.07.: drei erneut
    gesendete Voices um 14:00:41), kollidierten die Namen sonst: die Downloads
    überschrieben sich gegenseitig, und die abgeleiteten WAV-Pfade der
    Transkription zogen sich zusätzlich gegenseitig die Datei weg."""
    out_dir = Path(UPLOAD_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    uniq = uuid.uuid4().hex[:6]
    # Sonderzeichen im Dateinamen entschärfen
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    dest = out_dir / f"{ts}-{uniq}_{safe}"
    await file_obj.download_to_drive(str(dest))
    return dest


@dataclass
class UserSession:
    client: ClaudeSDKClient
    user_id: int = 0  # Besitzer der Session — für per-User-Prefs (z. B. /spur)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    always_allowed_tools: set[str] = field(default_factory=set)
    # Default verbose: der Tipp-Indikator (Lebenszeichen bei werkzeuglosen Turns)
    # läuft nur außerhalb von quiet — bliebe der Default True, sähe man bei einer
    # reinen Textfrage gar nichts (der behobene Regress). /quiet schaltet dann
    # NUR den Indikator ab; die 🔧-Werkzeug-Spur bleibt in jedem Fall sichtbar.
    quiet: bool = False
    tts_enabled: bool = False
    # 5.25 (a) Herkunfts-Schranke: Hosts aus Adams Nachricht + Suchtreffern der
    # LAUFENDEN Aufgabe. Nur dorthin darf WebFetch ohne Rückfrage. Wird bei jedem
    # Job-Start neu befüllt (pro Aufgabe — eine wachsende Liste höhlte die
    # Schranke aus, Umsetzungs-Hinweis im Drehbuch).
    task_origins: set[str] = field(default_factory=set)
    current_model: str = field(default_factory=lambda: DEFAULT_MODEL)
    current_effort: str | None = None  # "low" / None (default) / "max"
    logger: ConversationLogger | None = None
    # value is (loop, future) — the loop the future was created on, so the
    # PTB-side callback can resolve it via call_soon_threadsafe across loops.
    pending_permissions: dict[str, tuple[asyncio.AbstractEventLoop, asyncio.Future]] = field(default_factory=dict)
    # maps Telegram message_id → request_id so emoji reactions can resolve permissions
    message_permissions: dict[int, str] = field(default_factory=dict)
    chat_id: int | None = None
    thread_id: int | None = None  # Forum-Thema (message_thread_id) des aktuellen Jobs
    bot: Any = None  # telegram.Bot, injected per-message
    started_at: float = field(default_factory=time.monotonic)
    # 5.18 Stall-Erkennung: Zeitpunkt der letzten Regung DIESER Claude-Session
    # (monotonic). Wird in `stream_response` bei JEDER eingehenden SDK-Nachricht
    # gesetzt — Text, Werkzeug-Aufruf, Werkzeug-Ergebnis. Bewusst hier und nicht
    # in `Mailbox` (so der ursprüngliche Plan): `stream_response` kennt nur die
    # Session, nicht die user_id — ein Umweg über ein zweites Feld wäre eine
    # zusätzliche Bruchstelle. Der Stall-Wächter vergleicht gegen
    # `max(mb.current_started, sess.last_activity)`, deckt also auch den Fall ab,
    # dass ein Turn losläuft und NIE etwas liefert.
    last_activity: float = field(default_factory=time.monotonic)


SESSIONS: dict[int, UserSession] = {}


# ---------- message queue / "Sekretariat" ----------
#
# Abgespeckte Variante (vor Netcup): EINE Claude-Konversation pro User, aber
# eingehende Nachrichten werden bei laufendem Task nicht mehr verworfen, sondern
# in einer Mailbox gequeued und nacheinander abgearbeitet. Die zuletzt geschickte
# Nachricht hat Vorrang (LIFO: vorne einsortiert). „Korrektur"/„weitere Info"
# stoppt den laufenden Vorgang und arbeitet den Zusatz sofort ein.
#
# Die Queue lebt im RAM — ein harter Bot-Neustart leert sie (run_polling nutzt
# drop_pending_updates). Persistenz + echte parallele Sessions kommen mit Netcup.

# 5.5 [GEÄNDERT 2026-07-24]: Warteschlange ist jetzt FIFO (chronologisch) —
# bewusste Umkehr der früheren LIFO-Entscheidung. Nur ECHTE Stopp/Korrektur-
# Signale brechen den laufenden Vorgang ab und dürfen vor. Nachtrag/Ergänzung/
# Zusatzinfo sind KEIN Interrupt mehr — sie reihen sich normal hinten ein
# (der Self-Reply-Zweig behandelt sie ohnehin als Nachtrag/Ergänzung/Widerruf).
INTERRUPT_PREFIXES = (
    "korrektur", "stopp", "stop", "halt", "abbrechen", "abbruch",
    "brich das ab", "brich ab", "brich es ab", "warte stopp", "warte, stopp",
    "nein das war falsch", "nein, das war falsch",
    "nee das war falsch", "nee, das war falsch",
    "das war falsch", "falscher auftrag", "vergiss das",
)


@dataclass
class QueuedJob:
    # update ist NUR noch Herkunftsnachweis — der Job-Pfad liest ausschließlich die
    # Primitive darunter. Bei aus der Persistenz wiederaufgenommenen Jobs (5.2
    # Reconcile) ist update None, denn ein lebendes telegram.Update überlebt keinen
    # Neustart. Wer hier wieder `job.update.…` einbaut, bricht genau diesen Pfad.
    update: Update | None
    text: str
    force_tts: bool = False
    output_chat_id: int | None = None
    reply_to_override: int | None = None
    received_at: float = field(default_factory=time.time)
    context_retry: bool = False  # True, nachdem wg. Kontext-Überlauf frisch neu gestartet
    thorough: bool = False       # 🎯 Gründlich: aktives Modell + Max + Quellencheck
    pending_key: str | None = None  # 5.2: Schlüssel des Persistenz-Records (logs/pending/<key>.json)
    # --- 5.2: Primitive statt update.* (überleben Reboot) ---
    user_id: int = 0
    chat_id: int | None = None
    message_id: int | None = None
    thread_id: int | None = None
    # 6.1: Ausgangs-Thema (Forum-Topic) bei Cross-Chat-Ablage. Anders als
    # thread_id (= Eingangsthema, geht bei Cross-Chat verloren) überlebt dieses
    # Feld den Kanalwechsel und lenkt die Ausgabe ins Ziel-Zimmer.
    output_thread_id: int | None = None
    # ECHTE Sendezeit (Telegram-Serverzeit, aus update.message.date) als Unix-Zeit.
    # Bewusst NICHT received_at: eine nach Neustart nachgeholte Nachricht wurde
    # früher gesendet als sie verarbeitet wird — der Prompt muss die Sendezeit
    # nennen (Registereintrag „update.message.date"), sonst lügt die Zeitzeile.
    message_date: float | None = None
    bot: Any = None            # telegram.Bot — beim Reconcile gesetzt (kein update vorhanden)
    resumed: bool = False      # True = aus der Persistenz nachgeholt (5.2 Schritt 2)
    # Meta-Zeile fürs Gesprächs-Log (22.07.): „🎙️ Sprachnachricht (M:SS)" bzw.
    # Dateiname/Typ/Größe bei Uploads — wird vor dem User-Eintrag geloggt.
    log_note: str | None = None
    # 5.18: Wie oft dieser Job schon einem Session-Stall zum Opfer fiel. Bremse
    # gegen die Endlosschleife „hängt → neu → hängt": ab MAX_STALL_RETRIES wird
    # nur noch gemeldet statt automatisch wiederholt.
    stall_retries: int = 0


@dataclass
class Mailbox:
    queue: deque[QueuedJob] = field(default_factory=deque)
    worker: asyncio.Task | None = None
    current_job: QueuedJob | None = None
    current_started: float = 0.0
    done_log: deque[tuple[float, str]] = field(default_factory=lambda: deque(maxlen=8))
    # Sanfter Wechsel (22.07.): Modell-/Tempo-Wechsel während eines laufenden
    # Jobs schließt die Session NICHT mehr hart (das beendete den Job als
    # „fehler" — für Adam wirkte die Antwort verloren). Stattdessen nur Prefs
    # speichern + diesen Merker setzen; der Worker schließt nach Job-Abschluss.
    switch_pending: bool = False


MAILBOXES: dict[int, Mailbox] = {}

# 5.2 Schritt 2: Schlüssel der beim Start aus der Persistenz nachgeholten
# Nachrichten. Telegram stellt dieselben Nachrichten nach einem Neustart u. U.
# NOCHMAL zu (DROP_PENDING_UPDATES=False) — dann würde ohne diese Sperre dieselbe
# Nachricht zweimal beantwortet. Einträge werden bei der Zweitzustellung
# verbraucht; was nie doppelt kommt, bleibt harmlos liegen (paar Bytes).
_RESUMED_KEYS: set[str] = set()

# Wie oft eine liegengebliebene Nachricht höchstens automatisch nachgeholt wird,
# bevor der Bot aufgibt und sie nur noch meldet (s. _reconcile_pending).
_MAX_RESUME_ATTEMPTS = int(os.environ.get("MAX_RESUME_ATTEMPTS", "3"))

# 5.2 Voice-Eingangsschutz (Befund 20.07.): Eine Sprachnachricht wird schon beim
# Eintreffen persistiert, lange bevor ihr Text bekannt ist. Solange sie diese
# Stufenmarke trägt, ist der gespeicherte „Text" nur ein Platzhalter — er darf
# NIEMALS an Claude gehen. Der Reconcile erkennt das daran und meldet statt
# nachzuholen (dieselbe Hybrid-Logik wie beim Status „sendet").
VOICE_STAGE = "voice_transkription"
VOICE_STAGE_PLACEHOLDER = "[Sprachnachricht — noch nicht transkribiert]"


def _resolve_voice_stage(key: str | None) -> None:
    """Löst den Voice-Eingangs-Eintrag auf, wenn die Verarbeitung sauber
    abgebrochen ist (Adam hat ja eine Fehlermeldung bekommen). Ohne das bliebe
    der Record liegen und der Bot meldete ihn bei jedem Start erneut."""
    if not key:
        return
    try:
        pending.resolve(key)
    except Exception:
        log.exception("Voice-Eingangs-Record nicht auflösbar (nicht-fatal)")


def _note_voice_audio(key: str | None, path: Path) -> None:
    """Trägt den Pfad der gesicherten Audiodatei in den Eingangs-Eintrag nach."""
    if not key:
        return
    pending.merge(key, {"audio_path": str(path)})

# Letzte Transkription pro User — für /ttsdemo
_LAST_TRANSCRIPTION: dict[int, str] = {}


def _get_mailbox(user_id: int) -> Mailbox:
    mb = MAILBOXES.get(user_id)
    if mb is None:
        mb = Mailbox()
        MAILBOXES[user_id] = mb
    return mb


# Map (chat_id, message_id) → Text/Inhalt einer vom Bot gesendeten Nachricht.
# Erlaubt, einen Reply des Users auf eine Bot-Nachricht wieder auf den
# ursprünglichen Inhalt zu beziehen — vor allem bei Sprachnachrichten, die in
# Telegram keinen Text tragen.
BOT_MSGS: dict[tuple[int, int], str] = {}
_BOT_MSGS_MAX = 400


def _remember_bot_msg(chat_id: int, message_id: int | None, text: str) -> None:
    if not message_id or not text:
        return
    BOT_MSGS[(chat_id, message_id)] = " ".join(text.split())
    while len(BOT_MSGS) > _BOT_MSGS_MAX:
        BOT_MSGS.pop(next(iter(BOT_MSGS)))


def _job_preview(text: str, n: int = 60) -> str:
    raw = text or ""
    # Führenden Kontext-Hinweis-Präfix entfernen, damit die Vorschau Adams
    # tatsächlichen Nachrichten-Anfang zeigt und nicht den Reply-Bezugs-Vermerk.
    if raw.lstrip().startswith("[Kontext:"):
        import re as _re
        m = _re.match(r"\s*\[Kontext:[^\]]*\]:?\s*", raw, flags=_re.DOTALL)
        if m:
            raw = raw[m.end():]
    one_line = " ".join(raw.split())
    return one_line if len(one_line) <= n else one_line[: n - 1] + "…"


def _is_interrupt(text: str) -> bool:
    """True nur bei echten Stopp-/Korrektur-Signalen (5.5) — bricht den laufenden
    Vorgang ab und reiht die Nachricht vor. Nachtrag/Ergänzung zählen NICHT."""
    return (text or "").lstrip().lower().startswith(INTERRUPT_PREFIXES)


def _ensure_worker(user_id: int) -> None:
    """Startet den Drain-Worker, falls keiner läuft. Synchron (kein await) →
    atomar gegenüber nebenläufigen Handler-Aufrufen."""
    mb = _get_mailbox(user_id)
    if mb.worker is None or mb.worker.done():
        mb.worker = asyncio.create_task(_session_worker(user_id))


async def _session_worker(user_id: int) -> None:
    mb = _get_mailbox(user_id)
    while mb.queue:
        job = mb.queue.popleft()
        mb.current_job = job
        mb.current_started = time.monotonic()
        # 5.2: Persistenz-Status auf „in Bearbeitung" (falls Reboot jetzt: Hybrid → melden).
        if job.pending_key:
            pending.set_status(job.pending_key, pending.STATUS_RUNNING)
        outcome = "fehler"
        try:
            outcome = await _run_job(user_id, job)
        except Exception:
            log.exception("worker: job failed for user_id=%s", user_id)
            # Bisher der einzige Fehler-Pfad OHNE Nachricht an Adam — der Job
            # verschwand still bis zum nächsten Neustart (22.07. behoben).
            await _notify_job_failed(job)
        finally:
            mb.done_log.append((time.time(), _job_preview(job.text)))
            mb.current_job = None
        # 5.2: Persistenz-Status nach Ausgang nachziehen.
        #   beantwortet/aufgegeben → Record löschen (raus aus pending)
        #   offen (Kontext-Retry re-enqueued) → bleibt liegen, wird gleich neu gezogen
        #   fehler → bleibt liegen (Hybrid-Reconcile meldet ihn beim nächsten Start)
        if job.pending_key:
            if outcome in ("beantwortet", "aufgegeben"):
                pending.resolve(job.pending_key)
            elif outcome == "offen":
                pending.set_status(job.pending_key, pending.STATUS_OPEN)
            else:
                pending.set_status(job.pending_key, pending.STATUS_FAILED)
        # Sanfter Wechsel (22.07.): Erst NACH Abschluss des Jobs die Session
        # schließen — der nächste Job baut sie automatisch mit den inzwischen
        # gespeicherten neuen Prefs (Modell/Tempo) auf.
        if mb.switch_pending:
            mb.switch_pending = False
            await close_session(user_id)
    mb.worker = None


async def _notify_job_failed(job: QueuedJob) -> None:
    """Kurze Sofortmeldung, wenn ein Job als „fehler" endet (22.07.): Adam
    entscheidet, ob er neu anstößt oder liegen lässt — statt erst beim nächsten
    Neustart vom Reconcile überrascht zu werden. Der 5.2-Record bleibt liegen."""
    bot_obj = job.bot or (job.update.get_bot() if job.update is not None else None)
    if bot_obj is None:
        return
    try:
        await bot_obj.send_message(
            chat_id=job.chat_id,
            text=(f"⚠️ Die Aufgabe „{_job_preview(job.text)}“ ist mit einem Fehler "
                  "abgebrochen. Schick sie neu, wenn sie noch gebraucht wird — "
                  "oder lass sie liegen."),
            reply_to_message_id=job.message_id or None,
        )
    except Exception:
        log.exception("Fehler-Sofortmeldung nicht zustellbar")


def _count_newer_pending(user_id: int, job: QueuedJob) -> int:
    """Wie viele NEUERE Nachrichten warten seit Bearbeitungsbeginn dieses Jobs?

    ACHTUNG Zeitbasen (Analyse-Befund 17.07.): `Mailbox.current_started` ist
    time.monotonic(), `QueuedJob.received_at` dagegen time.time() — ein Vergleich
    der beiden wirft KEINEN Fehler, wäre aber IMMER wahr und würde bei jeder
    Antwort Fehlalarm auslösen. Deshalb wird ausschließlich received_at gegen
    received_at verglichen (gleiche Zeitbasis).
    """
    try:
        mb = MAILBOXES.get(user_id)
        if not mb or not mb.queue:
            return 0
        return sum(1 for j in mb.queue if j.received_at > job.received_at)
    except Exception:
        log.exception("Vollständigkeits-Zählung fehlgeschlagen (nicht-fatal)")
        return 0


async def _presend_gate(
    sess: UserSession, job: QueuedJob, answer: str | None, *, chat_id: int,
    reply_to: int | None, thread_id: int | None,
) -> str | None:
    """Pre-Send-Hook (8.5): prüft den vollständigen Text, BEVOR er rausgeht.

    Adam-Spec: deterministisch Fixbares wird direkt korrigiert; verifizierbare,
    nicht auto-fixbare Befunde gehen EINMAL zur Korrektur an Claude zurück — greift
    das nicht, wird MIT ⚠️-Vermerk gesendet statt weiter zu blockieren (nie eine
    hängende Antwort). Rückgabe: der zu sendende Text.
    """
    if not answer:
        return answer
    # NICHT `pending` nennen — das würde das Modul `pending` (5.2) in dieser
    # Funktion überschatten und jeden künftigen Zugriff darauf still brechen.
    pending_newer = _count_newer_pending(job.user_id, job)
    answer, findings = presend.check_and_fix(answer, pending_newer=pending_newer)
    meta = {"user_id": job.user_id, "thorough": job.thorough}

    todo = presend.needs_correction(findings)
    # Vermerke werden angehängt, lösen aber KEINE Korrekturrunde aus (s. presend.py).
    notices = presend.needs_notice(findings)
    notice_suffix = ("\n\n" + "\n".join(f.get("hinweis", "") for f in notices)) if notices else ""
    if not todo:
        presend.log_findings(findings, meta)
        return answer + notice_suffix

    # EINE Korrekturrunde — mit konkretem Befund.
    log.info("presend: Korrekturrunde für %s Befund(e)", len(todo))
    try:
        await sess.client.query(presend.correction_prompt(todo))
        corrected = await stream_response(
            sess, chat_id, force_tts=job.force_tts,
            reply_to=reply_to, thread_id=thread_id,
        )
    except Exception:
        log.exception("presend: Korrekturrunde fehlgeschlagen")
        corrected = None

    if corrected:
        corrected, again = presend.check_and_fix(
            corrected, pending_newer=_count_newer_pending(job.user_id, job))
        if not presend.needs_correction(again):
            meta["korrektur"] = "erfolgreich"
            presend.log_findings(findings + again, meta)
            return corrected + notice_suffix
        answer, findings = corrected, findings + again

    # Korrektur griff nicht → senden MIT sichtbarem Vermerk, niemals blockieren.
    meta["korrektur"] = "fehlgeschlagen"
    presend.log_findings(findings, meta)
    hinweis = "\n\n⚠️ " + "; ".join(f.get("detail", "") for f in todo)
    return answer + hinweis + notice_suffix


async def _run_job(user_id: int, job: QueuedJob) -> str:
    """Führt EINEN Job gegen die (ggf. frisch geöffnete) Claude-Session aus.
    Body entspricht der früheren process_user_text-Logik.

    Rückgabe = Ausgang für die 5.2-Persistenz-Pflege im Worker:
      "beantwortet" — Turn lief durch (Record wird gelöscht)
      "aufgegeben"  — Auth-/finaler Kontextfehler, wird nicht erneut versucht (Record gelöscht)
      "offen"       — wg. Kontext-Überlauf re-enqueued (Record bleibt, kommt gleich neu dran)
      "fehler"      — sonstiger Session-Fehler (Record bleibt liegen → Hybrid-Reconcile meldet ihn)"""
    if job.thorough:
        # 🎯 Gründlich: max Effort + Pflicht-Quellencheck im AKTIV gewählten Modell.
        # (Zuvor war Opus hart gesetzt — jetzt modell-agnostisch: Fable+Gründlich =
        # höchste Qualitäts-Kombination, Opus+Gründlich = bewährte Tiefe. Kein
        # Auto-Upgrade — Adam wählt das Modell bewusst; Adam-Entscheid 22.07.)
        sess = await ensure_session(user_id, effort_override="max", fresh=True)
    else:
        sess = await ensure_session(user_id)
    # 5.25 (a): Herkunfts-Menge PRO AUFGABE frisch aufsetzen — Adressen aus Adams
    # Nachricht; Suchtreffer der Aufgabe kommen in stream_response dazu. Nur
    # dorthin darf WebFetch ohne Rückfrage.
    sess.task_origins = _extract_hosts(job.text)
    # AUSSCHLIESSLICH Primitive (5.2): so läuft dieser Pfad identisch für frische
    # und für nach einem Neustart wiederaufgenommene Jobs (dort gibt es kein Update).
    sess.chat_id = job.chat_id
    sess.bot = job.bot or (job.update.get_bot() if job.update is not None else None)
    effective_output_id = job.output_chat_id or job.chat_id

    same_chat = bool(job.message_id and effective_output_id == job.chat_id)
    # Antwort als Reply auf die auslösende Nachricht markieren — aber nur, wenn die
    # Antwort in denselben Chat geht (ein message_id-Bezug über Chats hinweg wäre ungültig).
    # Bei Sprachnachrichten zeigt der Override auf die lesbare Transkriptions-Nachricht
    # (🎙️ …) statt auf das reine Audio, damit das Zitat beim Scrollen lesbar bleibt.
    reply_to = (job.reply_to_override or job.message_id) if same_chat else None
    # In Forum-Gruppen: Antwort ins selbe Thema (Topic) zurückschicken. Nur sinnvoll,
    # wenn die Antwort in denselben Chat geht; bei Cross-Chat-Ablage (Ausgabekanal) None.
    # 6.1: Bei gezielter Cross-Chat-Ablage in ein Zimmer trägt output_thread_id das
    # Ziel-Topic (überlebt den Kanalwechsel, den thread_id nicht überlebt).
    if same_chat:
        thread_id = job.thread_id
    else:
        thread_id = job.output_thread_id
    sess.thread_id = thread_id  # Permission-Prompts lesen das Thema von hier

    answer: str | None = None
    async with sess.lock:
        try:
            if sess.logger:
                if job.log_note:
                    sess.logger.log_event(job.log_note)
                sess.logger.log_user(job.text)
            # Echte Sendezeit aus dem Primitiv (überlebt Neustart) — bei einer
            # nachgeholten Nachricht nennt die Zeitzeile dadurch korrekt BEIDES:
            # wann Adam sie geschickt hat und dass sie jetzt erst drankommt.
            from datetime import datetime as _dt
            received_dt = (_dt.fromtimestamp(job.message_date).astimezone()
                           if job.message_date else None)
            query_prefix = (_current_datetime_context(received_dt)
                            + (_RESUMED_PREFIX if job.resumed else "")
                            + (_THOROUGH_PREFIX if job.thorough else ""))
            await sess.client.query(query_prefix + job.text)
            answer = await stream_response(
                sess, effective_output_id, force_tts=job.force_tts,
                reply_to=reply_to, thread_id=thread_id,
            )
            answer = await _presend_gate(
                sess, job, answer, chat_id=effective_output_id,
                reply_to=reply_to, thread_id=thread_id,
            )
        except Exception as e:
            log.exception("error processing message")
            cancelled = cancel_pending_permissions(sess, reason=f"query error: {e}")
            if is_auth_error(e):
                log.error("authentication failure for user_id=%s: %s", user_id, e)
                try:
                    await send_chunked(sess.bot, sess.chat_id, AUTH_HELP, parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    log.exception("failed to send auth-error message")
                await close_session(user_id)
                return "aufgegeben"
            # Kontext-Überlauf: Session verwerfen, frisch starten und die
            # gescheiterte Nachricht AUTOMATISCH neu verarbeiten (kein Nutzer-Eingriff,
            # nichts geht verloren). Nur einmal — scheitert es erneut, klare Meldung.
            if is_context_overflow(e):
                if not job.context_retry:
                    log.warning("context overflow user_id=%s — rotiere Session + retry", user_id)
                    await close_session(user_id)
                    job.context_retry = True
                    mb = _get_mailbox(user_id)
                    mb.queue.appendleft(job)  # als Nächstes mit frischer Session
                    try:
                        await sess.bot.send_message(
                            sess.chat_id,
                            "📏 Kontext war voll — neue Session, ich beantworte deine Nachricht jetzt …",
                        )
                    except Exception:
                        log.exception("failed to send context-rotate status")
                    return "offen"
                # Auch mit frischer Session zu groß → klare Meldung.
                try:
                    await send_chunked(
                        sess.bot, sess.chat_id,
                        "📏 Auch mit frischer Session passt das nicht ins Kontextfenster. "
                        "Die Nachricht oder ein Anhang ist zu groß.\n"
                        "→ Bitte kürzen oder aufteilen (bei langen Dokumenten: relevanten "
                        "Ausschnitt schicken). Für sehr große Recherchen ist die Code-/Web-Sitzung besser geeignet.",
                    )
                except Exception:
                    log.exception("failed to send context-overflow message")
                await close_session(user_id)
                return "aufgegeben"
            try:
                await send_chunked(
                    sess.bot,
                    sess.chat_id,
                    f"❌ Session-Fehler: {e}\n"
                    + (f"({cancelled} ausstehende Permission(s) verworfen.) " if cancelled else "")
                    + "Nächste Nachricht startet eine frische Session.",
                )
            except Exception:
                log.exception("failed to send error message to user")
            await close_session(user_id)
            return "fehler"

    # Senden erst JETZT — nach der Pre-Send-Prüfung (8.5), über den zentralen
    # Sendepfad (Vorstufe 5.8; ersetzt den früheren toten _send_tts-Zweig).
    if answer and sess.bot:
        # Ab HIER kann etwas beim Nutzer ankommen (bei TTS in mehreren Häppchen).
        # Nur ein Absturz ab diesem Punkt macht ein automatisches Nachholen
        # riskant — davor ist die Nachricht gefahrlos wiederholbar.
        if job.pending_key:
            pending.set_status(job.pending_key, pending.STATUS_SENDING)
        delivered = False
        try:
            delivered = await send_answer_to_user(
                sess, effective_output_id, answer, force_tts=job.force_tts,
                reply_to=reply_to, thread_id=thread_id,
            )
        except Exception:
            log.exception("Senden der geprüften Antwort fehlgeschlagen")
        if not delivered:
            # Antwort erzeugt, aber NICHTS kam beim Nutzer an. Der Job ist damit
            # NICHT erledigt — Record bleibt liegen (Status „fehler"), damit er
            # in /status sichtbar ist und der Start-Reconcile ihn meldet. Ihn hier
            # als „beantwortet" abzuhaken hieße: Antwort spurlos verloren.
            log.error("Antwort erzeugt, aber nicht zustellbar (user_id=%s, %d Zeichen) "
                      "— Nachricht bleibt offen", user_id, len(answer))
            # Kurze Klartext-Meldung versuchen (22.07.) — der einfache Sendepfad
            # kann funktionieren, auch wenn die volle Antwort-Zustellung scheiterte.
            await _notify_job_failed(job)
            if job.thorough and user_id in SESSIONS:
                await close_session(user_id)
            return "fehler"

    # 🎯 Gründlich war einmalig: Session schließen → nächste Nachricht wieder Standard.
    if job.thorough and user_id in SESSIONS:
        await close_session(user_id)

    return "beantwortet"


# ---------- helpers ----------

def authorized(update: Update) -> bool:
    user = update.effective_user
    if user is None or user.id not in ALLOWED_USER_IDS:
        log.warning("rejected message from user_id=%s", user.id if user else None)
        return False
    return True


def _should_respond_in_chat(update: Update) -> bool:
    """In privaten Chats immer antworten. In Gruppen NUR, wenn der Bot direkt
    adressiert wird — entweder per Reply auf eine Bot-Nachricht oder per
    @-Erwähnung im Text bzw. in der Caption. Sonst würde der Bot in einer
    Diskussionsgruppe auf jeden Beitrag reagieren, was Endlos-Schleifen und
    Spam erzeugt."""
    chat = update.effective_chat
    if chat is None or chat.type == "private":
        return True
    msg = update.message
    if msg is None:
        return False
    if (
        msg.reply_to_message
        and msg.reply_to_message.from_user
        and msg.reply_to_message.from_user.is_bot
    ):
        return True
    if not _BOT_USERNAME:
        return False
    mention_target = f"@{_BOT_USERNAME.lower()}"

    def _has_mention(entities, source_text: str | None) -> bool:
        if not entities or not source_text:
            return False
        for ent in entities:
            if ent.type != MessageEntity.MENTION:
                continue
            name = source_text[ent.offset:ent.offset + ent.length]
            if name.lower() == mention_target:
                return True
        return False

    if _has_mention(msg.entities, msg.text):
        return True
    if _has_mention(msg.caption_entities, msg.caption):
        return True
    return False


def _reply_params(message_id: int | None) -> ReplyParameters | None:
    """Baut ReplyParameters für Thread-Bezug. allow_sending_without_reply=True →
    Senden schlägt nicht fehl, falls die Originalnachricht gelöscht wurde."""
    if message_id is None:
        return None
    return ReplyParameters(message_id=message_id, allow_sending_without_reply=True)


def _find_safe_cut(text: str, limit: int) -> int:
    """Split-Punkt vor `limit`, der KEINE Überschrift am Ende der Nachricht
    belässt. Heading-artige Zeilen ('# …', '## …', aber auch fettgedruckte
    Section-Header wie '**Titel:**' alleine auf einer Zeile) gehören immer
    mit ihrem folgenden Inhalt in dieselbe Nachricht — sonst landet die
    Überschrift in Telegram am Ende einer Nachricht und der Inhalt erst in
    der nächsten (schlecht zum Anpinnen / Wiederfinden).
    """
    import re
    cut = text.rfind("\n", 0, limit)
    if cut <= 0:
        return limit
    heading_patterns = (
        r"^\s*#{1,6}\s+\S",                # Markdown-Heading: # Titel
        r"^\s*\*\*[^*\n]+\*\*\s*:?\s*$",   # Fett-Section: **Titel** / **Titel:** allein
    )
    # Iterativ rückwärts: solange die Zeile direkt VOR dem Cut eine Heading
    # oder Leerzeile (die meist zur folgenden Heading gehört) ist, einen
    # Schnitt weiter nach oben rücken. Verhindert auch mehrere aufeinander-
    # folgende Headings am Nachrichten-Ende.
    while True:
        prev_nl = text.rfind("\n", 0, cut)
        last_line = text[prev_nl + 1:cut] if prev_nl >= 0 else text[:cut]
        if prev_nl <= 0:
            break
        if not last_line.strip():
            cut = prev_nl
            continue
        if any(re.match(p, last_line) for p in heading_patterns):
            cut = prev_nl
            continue
        break
    return cut


def _text_ends_with_heading(text: str) -> bool:
    """True, wenn die letzte sinntragende Zeile eine Markdown-Heading oder
    alleinstehende Fett-Section ist. Wird beim Streamen genutzt, um nicht
    mitten in einem Heading-zu-Inhalt-Übergang zu senden.
    """
    if not text:
        return False
    import re
    heading_patterns = (
        r"^\s*#{1,6}\s+\S",
        r"^\s*\*\*[^*\n]+\*\*\s*:?\s*$",
    )
    # rückwärts durch die Zeilen, Leerzeilen überspringen
    for line in reversed(text.splitlines()):
        if not line.strip():
            continue
        return any(re.match(p, line) for p in heading_patterns)
    return False


async def send_chunked(bot, chat_id: int, text: str, reply_to: int | None = None,
                       thread_id: int | None = None, **kwargs) -> None:
    """Telegram caps messages at ~4096 chars — split on newlines when needed.

    reply_to: markiert NUR die erste ausgehende Nachricht als Reply auf die
    auslösende User-Nachricht (Folge-Chunks hängen normal an, kein Zitat-Spam).
    thread_id: Forum-Thema (message_thread_id), in das ALLE Chunks gehen.
    """
    if not text:
        return None
    rp = _reply_params(reply_to)
    first_msg = None
    while text:
        if len(text) <= TELEGRAM_MSG_LIMIT:
            m = await bot.send_message(chat_id=chat_id, text=text, reply_parameters=rp,
                                       message_thread_id=thread_id, **kwargs)
            return first_msg or m
        cut = _find_safe_cut(text, TELEGRAM_MSG_LIMIT)
        m = await bot.send_message(chat_id=chat_id, text=text[:cut], reply_parameters=rp,
                                   message_thread_id=thread_id, **kwargs)
        first_msg = first_msg or m
        rp = None  # nur der erste Chunk threadet zur Ursprungsnachricht
        text = text[cut:].lstrip("\n")
    return first_msg


# Werkzeuge mit möglichen Extra-Kosten (💰-Kostenregel): NIE „always allow",
# immer mit Kostenhinweis nachfragen. WebFetch bleibt frei (keine Extra-Gebühr).
_COST_TOOLS = {
    "WebSearch": "⚠️ kostet ~1 Cent pro Suche (Anthropic-Werkzeuggebühr) — erlauben?",
}

# Werkzeuge, die NIE pauschal dauerfreigebbar sind (23.07., Adam-Entscheid nach
# Live-Fund): 💰-Tools sowieso — und WebFetch, weil ein pauschales Always genau
# den einen Wächter entfernt, den die Herkunfts-Schranke darstellt (fremde
# Seiten könnten dann klicklos Folge-Abrufe steuern/exfiltrieren). Vertrauen
# wird stattdessen PRO DOMAIN vergeben (trusted_domains in den Prefs).
_NO_ALWAYS_TOOLS = {"WebFetch"} | set(_COST_TOOLS)

# ---------- 5.25: Herkunfts-Schranke + Geheimnis-Schutz ----------

_URL_RE = re.compile(r"(?:https?://|www\.)([^\s/<>\")\]]+)", re.IGNORECASE)


def _url_host(url: str) -> str:
    """Hostname einer URL, kleingeschrieben, ohne führendes www."""
    m = _URL_RE.search(url or "")
    host = (m.group(1) if m else "").split("/")[0].split(":")[0].lower()
    return host[4:] if host.startswith("www.") else host


# Schemalose Domains („de.wikipedia.org/wiki/…", „fc.de") — so schreiben
# Menschen Adressen. Live-Fund 23.07. (Test 6): Adams Wikipedia-Angabe ohne
# https:// wurde nicht erkannt → die eigene Domain fragte fälschlich nach.
# Letztes Label muss alphabetisch sein (schließt „5.9"/„2.7" aus); harmlose
# Dateinamen-Treffer wie „bot.py" sind bewusst toleriert (niemand ruft sie ab).
_BARE_DOMAIN_RE = re.compile(
    r"(?<![\w@.\-])((?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,24})"
    r"(?=[/\s.,;:!?)\"'»«]|$)",
    re.IGNORECASE)


def _extract_hosts(text: str) -> set[str]:
    """Alle Hostnamen aus einem Text (Adams Nachricht, Suchtreffer) —
    mit UND ohne Schema/www-Präfix."""
    hosts = set()
    for m in _URL_RE.finditer(text or ""):
        h = m.group(1).split("/")[0].split(":")[0].lower()
        if h.startswith("www."):
            h = h[4:]
        if "." in h:
            hosts.add(h)
    for m in _BARE_DOMAIN_RE.finditer(text or ""):
        h = m.group(1).lower()
        if h.startswith("www."):
            h = h[4:]
        hosts.add(h)
    return hosts


# 5.25 (b) Geheimnis-Schutz: Verweise auf diese Muster werden NIE automatisch
# freigegeben — sie fallen immer in den normalen Freigabe-Dialog (Adam sieht
# und entscheidet). Kein Token darf je in Sitzungskontext oder Chat geraten.
_SENSITIVE_MARKERS = (".env", "credentials", "token", "secret", "_key", "key.",
                      "keys.", "id_ed25519", "id_rsa", "/etc/claude-telegram-bot")


def _is_sensitive_ref(raw: str) -> bool:
    s = (raw or "").lower()
    return any(m in s for m in _SENSITIVE_MARKERS)


# 8.7 Governance-Härtung: Der Bot editiert sein eigenes Repo NIE — auch nicht
# per Bash. Edit/Write dorthin lehnt der Callback längst ab; dieses Muster
# schließt den Bash-Seitenweg (git commit/push, Redirects, in-place-sed …).
# Lesen (cat, grep, git log/status/diff) bleibt frei. Bewusst konservativ:
# ein Misch-Befehl (Repo-Pfad + Schreibmuster woanders) wird ebenfalls
# abgelehnt — der Agent kann ihn aufteilen.
_REPO_WRITE_RE = re.compile(
    # git mit beliebigen Optionen (z. B. -C <pfad>) vor dem schreibenden Subcommand
    r"\bgit\b[^|;&]*\b(?:commit|push|merge|rebase|reset|checkout|restore|clean|add|rm|mv|stash|am|apply|cherry-pick)\b"
    r"|>{1,2}|\bsed\s+(?:-\S*\s+)*-i|\btee\b|\brm\b|\bmv\b|\bcp\b|\btouch\b|\bmkdir\b|\bchmod\b|\bln\b"
)


def _is_repo_write_cmd(cmd: str) -> bool:
    c = cmd or ""
    return "claude-telegram-bot" in c and bool(_REPO_WRITE_RE.search(c))


def _trace_off(user_id: int) -> bool:
    """5.25 (d) /spur: True, wenn Adam die 🔧-FYI-Werkzeug-Spur stummgeschaltet hat.
    Per-User (user_id), NICHT chat_id. Betrifft NUR die reine FYI-Zeile — die
    Allow/Deny-Rückfragen bleiben davon unberührt und immer sichtbar.
    Default AUS (Adam 24.07.): ohne gesetzte Pref ist die FYI-Spur stumm — Adam
    schaltet sie mit /spur bewusst an, wenn er beim Audit mitschauen will."""
    return bool(_USER_PREFS.get(str(user_id), {}).get("trace_off", True))


def _tool_trace_line(chat_id: int, name: str, tool_input: dict) -> str:
    """5.25 (d): Klartext-Werkzeug-Spur — deutsche Tätigkeitszeile statt Tool-Name
    und Argumente (Adam-Entscheid, bewusste Revision der 17.07.-Rohform). Rohform
    jederzeit per /technik. Jede Web-Adresse bleibt sichtbar (Herkunfts-Schranke)."""
    if _USER_PREFS.get(str(chat_id), {}).get("raw_tools"):
        return f"🔧 {name}"
    if name == _SEARCH_TOOL_NAME:
        q = " ".join(str(tool_input.get("query") or "").split())[:60]
        return f"🔎 recherchiere: „{q}“ …" if q else "🔎 recherchiere im Web …"
    if name == "WebFetch":
        host = _url_host(str(tool_input.get("url") or ""))
        return f"📄 lese {host} …" if host else "📄 lese Webseite …"
    if name == "Read":
        raw = str(tool_input.get("file_path") or "")
        try:
            if raw and _MEMORY_DIR.resolve() in Path(raw).expanduser().resolve().parents:
                return "📂 schaue in meinen Notizen nach …"
        except Exception:
            pass
        base = Path(raw).name
        return f"📖 lese {base} …" if base else "📖 lese Datei …"
    if name in ("Grep", "Glob"):
        return "🔍 durchsuche Dateien …"
    if name == "Bash":
        cmd = " ".join(str(tool_input.get("command") or "").split())[:60]
        return f"🖥️ führe aus: {cmd}" if cmd else "🖥️ führe Befehl aus …"
    if name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        base = Path(str(tool_input.get("file_path") or "")).name
        return f"✏️ bearbeite {base}" if base else "✏️ bearbeite Datei"
    if name == "TodoWrite":
        return "🗒️ aktualisiere meine Aufgabenliste"
    if name == "ToolSearch":
        return "🧰 lade Werkzeug nach …"
    if name == "ScheduleWakeup":
        return "⏲️ plane kurze Wartezeit …"
    if name == "WebSearch":
        return "🌐 Anthropic-Websuche (💰 kostenpflichtig)"
    return f"🔧 {name}"


def format_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Pretty-print a tool call for the permission prompt (plain text only)."""
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        preview = cmd if len(cmd) < 800 else cmd[:800] + "…"
        return f"Bash\n\n{preview}"
    if tool_name in ("Read", "Edit", "Write"):
        path = tool_input.get("file_path", "")
        return f"{tool_name}: {path}"
    keys = ", ".join(list(tool_input.keys())[:5])
    return f"{tool_name}\nargs: {keys}"


# ---------- permission callback ----------

def make_permission_callback(user_id: int):
    """Returns a can_use_tool callback bound to this user.

    Cross-loop safety: the SDK may invoke can_use_tool from a different event
    loop than PTB's update dispatch. We store (loop, future) pairs so the
    callback handler can resolve the future via call_soon_threadsafe on the
    right loop. Resolving a future from the wrong loop fails silently in some
    Python versions and that was masking real deadlocks.
    """

    async def can_use_tool(
        tool_name: str,
        tool_input: dict[str, Any],
        context: ToolPermissionContext,
    ):
        sess = SESSIONS.get(user_id)
        if sess is None or sess.bot is None or sess.chat_id is None:
            log.error("permission request with no active session for %s", user_id)
            return PermissionResultDeny(message="no active session")

        # Kontextschutz (Adam 15.07.): Skills laden große Wissensdateien in den
        # Kontext und waren Mit-Ursache von Überläufen. Ein Telegram-Assistent
        # braucht das nicht — Skill-Ladungen hart ablehnen. Solche Themen bei
        # Bedarf in der Code-/Web-Sitzung.
        if tool_name == "Skill":
            skill = tool_input.get("skill") or tool_input.get("command") or ""
            log.info("Skill-Load abgelehnt (Bot-Session, Kontextschutz): %s", skill)
            return PermissionResultDeny(
                message="Skills sind in der Telegram-Session deaktiviert (Kontextschutz). "
                        "Frag solche Themen bei Bedarf in der Code-/Web-Sitzung."
            )

        # Lokale private Websuche (SearxNG, 2.7): kostenfrei + lokal → ohne Rückfrage.
        if tool_name == _SEARCH_TOOL_NAME:
            return PermissionResultAllow()

        # Führungs-Register: Das Projekt-Repo ist für den Bot NUR-LESEN —
        # Schreibzugriffe dorthin hart ablehnen (nur die Migrations-Sitzung schreibt).
        if tool_name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
            raw = tool_input.get("file_path") or ""
            try:
                if raw and "/claude-telegram-bot" in str(Path(raw).expanduser().resolve()):
                    return PermissionResultDeny(
                        message="Das Projekt-Repo ist für den Bot NUR-LESEN "
                                "(Führungs-Register, CLAUDE.md). Änderungswunsch "
                                "als Text an Adam/die Migrations-Sitzung geben."
                    )
            except Exception:
                pass

        # 8.7: derselbe Schutz für den Bash-Seitenweg (git commit/push, >, sed -i …).
        if tool_name == "Bash" and _is_repo_write_cmd(str(tool_input.get("command") or "")):
            return PermissionResultDeny(
                message="Schreibender Befehl ins Bot-Repo abgelehnt (8.7: der Bot "
                        "editiert sein Repo nie — Deploys nur per git pull durch "
                        "Adam/die Migrations-Sitzung). Lesen ist weiterhin frei; "
                        "Misch-Befehle bitte aufteilen."
            )

        # 5.25 (b) Geheimnis-Schutz: Verweise auf Secrets fallen IMMER in den
        # Dialog — vor jeder Auto-Freigabe geprüft, auch vor Always-Allow.
        _ref = str(tool_input.get("file_path") or tool_input.get("path")
                   or tool_input.get("pattern") or tool_input.get("command")
                   or tool_input.get("url") or "")
        sensitive = _is_sensitive_ref(_ref)

        # Kosten-Tools + WebFetch NIE über die Always-Allow-Liste durchwinken
        # (_NO_ALWAYS_TOOLS): 💰 wegen der Kostenregel, WebFetch wegen der
        # Herkunfts-Schranke. Alt-Einträge werden beim Session-Aufbau gefiltert.
        if (tool_name in sess.always_allowed_tools
                and tool_name not in _NO_ALWAYS_TOOLS and not sensitive):
            return PermissionResultAllow()

        # 5.25 (a) WebFetch mit Herkunfts-Schranke: kostenfrei + lesend, aber nur
        # zu Adressen aus Adams Nachricht, Suchtreffern der LAUFENDEN Aufgabe —
        # oder von Adam PRO DOMAIN dauerhaft freigegebenen Quellen. Von Webseiten
        # nachgereichte fremde Ziele → Dialog (sonst könnte eine gelesene Seite
        # den Agenten zu Folge-Abrufen dirigieren). Spur bleibt immer sichtbar.
        if tool_name == "WebFetch" and not sensitive:
            host = _url_host(str(tool_input.get("url") or ""))
            trusted = set(_USER_PREFS.get(str(user_id), {}).get("trusted_domains", []))
            if host and (host in sess.task_origins or host in trusted):
                return PermissionResultAllow()

        # 5.25 (a) + Session-Diät (5.23): Lesen in Workspace + Memory-Ordner ohne
        # Rückfrage — der Agent recherchiert/liest selbst nach (nur lesend).
        # Schreibende/ausführende Werkzeuge bleiben freigabepflichtig.
        if tool_name in ("Read", "Grep", "Glob") and not sensitive:
            raw = tool_input.get("file_path") or tool_input.get("path") or ""
            try:
                if not raw:
                    # Grep/Glob ohne Pfad durchsuchen den Workspace (cwd).
                    return PermissionResultAllow()
                p = Path(raw).expanduser().resolve()
                for base in (_MEMORY_DIR.resolve(), Path(WORKDIR).expanduser().resolve()):
                    if p == base or base in p.parents:
                        return PermissionResultAllow()
            except Exception:
                pass

        request_id = uuid.uuid4().hex[:8]
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        sess.pending_permissions[request_id] = (loop, fut)
        log.info("permission requested: user=%s req=%s tool=%s",
                 user_id, request_id, tool_name)

        # 5.25 (d): Klartext zuerst, technische Details darunter.
        body = (f"{_tool_trace_line(user_id, tool_name, tool_input)}\n\n"
                f"{format_tool_call(tool_name, tool_input)}")
        if tool_name in _COST_TOOLS:
            body = f"💰 {_COST_TOOLS[tool_name]}\n\n{body}"
        rows = [
            [
                InlineKeyboardButton("✅ Allow", callback_data=f"p:{request_id}:allow"),
                InlineKeyboardButton("❌ Deny", callback_data=f"p:{request_id}:deny"),
            ],
        ]
        # „Always allow" NICHT für 💰-Tools und WebFetch anbieten (_NO_ALWAYS_TOOLS).
        # Bei WebFetch stattdessen: Vertrauen PRO DOMAIN (Adam-Entscheid 23.07.).
        if tool_name == "WebFetch":
            _host = _url_host(str(tool_input.get("url") or ""))
            if _host and len(_host) <= 40:
                rows.append([
                    InlineKeyboardButton(
                        f"🔓 {_host} immer erlauben",
                        callback_data=f"p:{request_id}:domain:{_host}",
                    ),
                ])
        elif tool_name not in _NO_ALWAYS_TOOLS:
            rows.append([
                InlineKeyboardButton(
                    f"🔓 Always allow {tool_name}",
                    callback_data=f"p:{request_id}:always:{tool_name}",
                ),
            ])
        keyboard = InlineKeyboardMarkup(rows)
        try:
            sent = await sess.bot.send_message(
                chat_id=sess.chat_id,
                text=f"🔐 Permission request\n\n{body}",
                reply_markup=keyboard,
                parse_mode=None,
                message_thread_id=sess.thread_id,
            )
            sess.message_permissions[sent.message_id] = request_id
        except Exception:
            log.exception("failed to send permission prompt")
            sess.pending_permissions.pop(request_id, None)
            return PermissionResultDeny(message="bot failed to ask user")

        # 30 min timeout — Nutzer ist nicht immer am Gerät
        try:
            decision = await asyncio.wait_for(fut, timeout=1800)
        except asyncio.TimeoutError:
            sess.pending_permissions.pop(request_id, None)
            log.warning("permission timeout: user=%s req=%s tool=%s",
                        user_id, request_id, tool_name)
            try:
                await sess.bot.send_message(
                    chat_id=sess.chat_id,
                    text="⌛ Permission request nach 30 min abgelaufen — verweigert. Schick die Anfrage nochmal.",
                    message_thread_id=sess.thread_id,
                )
            except Exception:
                pass
            return PermissionResultDeny(message="user did not respond in 3 min")

        if decision == "allow":
            return PermissionResultAllow()
        if decision == "deny":
            return PermissionResultDeny(message="denied by user")
        if decision.startswith("always:"):
            tname = decision.split(":", 1)[1]
            # Doppelter Boden: _NO_ALWAYS_TOOLS (WebFetch, 💰) sind nie pauschal
            # dauerfreigebbar — auch nicht über einen manipulierten Callback.
            if tname in _NO_ALWAYS_TOOLS:
                return PermissionResultAllow()  # gilt nur für DIESE eine Anfrage
            sess.always_allowed_tools.add(tname)
            # 5.25 (c): dauerhaft merken — überlebt Reset/Neustart.
            prefs = _USER_PREFS.setdefault(str(user_id), {})
            stored = set(prefs.get("always_allow", []))
            if tname not in stored:
                stored.add(tname)
                prefs["always_allow"] = sorted(stored)
                _save_prefs(_USER_PREFS)
            return PermissionResultAllow()
        if decision.startswith("domain:"):
            # 🔓 Domain-Merkliste (23.07.): Vertrauen pro QUELLE statt pauschal
            # pro Werkzeug — ergänzt die Herkunfts-Schranke, hebelt sie nie aus.
            host = decision.split(":", 1)[1].strip().lower()
            if host:
                prefs = _USER_PREFS.setdefault(str(user_id), {})
                trusted = set(prefs.get("trusted_domains", []))
                if host not in trusted:
                    trusted.add(host)
                    prefs["trusted_domains"] = sorted(trusted)
                    _save_prefs(_USER_PREFS)
                log.info("trusted domain hinzugefügt: user=%s host=%s", user_id, host)
            return PermissionResultAllow()
        return PermissionResultDeny(message="unknown decision")

    return can_use_tool


# ---------- session lifecycle ----------

def _current_datetime_context(received_dt=None) -> str:
    """Datum/Wochentag/Uhrzeit als Pflicht-Kontextzeile vor jeder User-Nachricht.

    Damit hat das Modell bei jedem Aufruf das Datum vor sich und muss es nicht aus
    der Memory zurückrechnen. Schließt den 'letzte/vorletzte Nacht'-Fehlerkanal.

    `received_dt`: die ECHTE, serverseitige Empfangszeit (update.message.date,
    tz-aware). Ohne sie behauptete diese Zeile früher 'Eingang dieser Nachricht',
    rechnete aber mit dem Bearbeitungs-Start — lag die Nachricht in der
    Warteschlange, bekam das Modell eine nachweislich falsche Eingangszeit
    (Analyse-Befund 17.07.2026). Wartete die Nachricht spürbar, werden BEIDE
    Zeiten genannt, statt eine davon zu verschweigen.
    """
    from datetime import datetime
    now = datetime.now()
    recv = now
    if received_dt is not None:
        try:
            recv = received_dt.astimezone().replace(tzinfo=None)
        except Exception:
            recv = now
    wd_recv = presend.WEEKDAYS_DE[recv.weekday()]
    line = (
        f"[Eingang dieser Nachricht: {wd_recv}, "
        f"{recv.strftime('%d.%m.%Y')}, {recv.strftime('%H:%M')} Uhr."
    )
    delay = (now - recv).total_seconds()
    if delay >= 120:
        wd_now = presend.WEEKDAYS_DE[now.weekday()]
        line += (
            f" JETZT ist es {wd_now}, {now.strftime('%d.%m.%Y')}, "
            f"{now.strftime('%H:%M')} Uhr — die Nachricht wartete "
            f"{int(delay // 60)} Min. in der Warteschlange."
        )
    return (
        line +
        f" Bei jeder zeitlichen Aussage (heute/gestern/letzte Nacht/in X Tagen) "
        f"diese Werte als Wahrheit nehmen — nicht aus der Memory rechnen.]\n\n"
    )


def _recent_conversation_recall(max_chars: int = 6000) -> str:
    """Jüngster Gesprächsverlauf aus den ConversationLog-Tagesdateien.

    Damit eine frisch gestartete Session sofort am letzten Faden anknüpft,
    statt nach einem Neustart zu fragen 'worum ging es?'. Es werden die
    letzten zwei Tagesdateien berücksichtigt (deckt den Mitternachts-Umbruch
    einer durchlaufenden Sitzung ab) und nur das jüngste Ende behalten.
    """
    try:
        files = sorted(LOG_DIR.glob("20*-*-*.md"))
    except Exception:
        return ""
    if not files:
        return ""
    chunks: list[str] = []
    for f in files[-2:]:
        try:
            chunks.append(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    text = "\n".join(chunks).strip()
    if not text:
        return ""
    if len(text) > max_chars:
        text = "…(älterer Verlauf gekürzt)…\n\n" + text[-max_chars:]
    return text


_QUALITY_GUIDANCE = (
    "# ANTWORTQUALITÄT (verbindlich, Adam-Priorität)\n"
    "- Bei Fakten- und Recherchefragen: **Quellen prüfen** (Websuche/Nachlesen) "
    "statt aus dem Gedächtnis zu raten. Aktuelle oder überprüfbare Fakten NIE frei erfinden.\n"
    "- **Unsicherheiten ausdrücklich kennzeichnen** ('unsicher', 'ungeprüft', "
    "'bitte gegenprüfen') — lieber ehrlich unsicher als selbstbewusst falsch.\n"
    "- **Keine ungeprüften Behauptungen** als Tatsache ausgeben.\n"
    "- Für Websuche das Tool **`web_search`** nutzen (lokale private Suche, "
    "**kostenfrei**) — die kostenpflichtige WebSearch ist reine NOTFALL-Option "
    "(nur wenn ausdrücklich verlangt oder web_search versagt; Adam bestätigt "
    "jede Nutzung einzeln im 💰-Dialog). Treffer-URLs bei Bedarf mit WebFetch "
    "vertiefen (kostenfrei).\n"
    "- **Mehrquellen-Regel für Faktenlisten** (Chronologien, Aufzählungen, "
    "Zahlenreihen): mindestens zwei unabhängige Quellen abgleichen, die Quellen "
    "in der Antwort NENNEN, Lücken und Widersprüche ausdrücklich kennzeichnen "
    "statt still zu raten. Bei erkennbaren Listen-Fragen von selbst gründlicher "
    "suchen statt aus einer Einzelquelle zu bauen.\n"
    "\n"
    "# REPO-ZUGRIFF (Führungs-Register, siehe CLAUDE.md im Repo)\n"
    "- Du darfst das Projekt-Repo (/home/claudebot/claude-telegram-bot) LESEN — "
    "bei Status-/Migrationsfragen IMMER frisch aus MIGRATION.md/CLAUDE.md lesen, "
    "nie aus dem Sitzungsgedächtnis antworten.\n"
    "- Du darfst dort NIEMALS schreiben, ändern oder committen — das tut nur die "
    "führende Migrations-Sitzung am Mac. Änderungswünsche als Textvorschlag an Adam.\n"
)


def _session_context(memory: str) -> str:
    """Antwortqualitäts-Leitplanke + Memory + jüngster Gesprächsverlauf als
    system_prompt-Append-Block."""
    recall = _recent_conversation_recall()
    if not recall:
        return f"{_QUALITY_GUIDANCE}\n\n---\n\n{memory}" if memory else _QUALITY_GUIDANCE
    header = (
        "# LETZTER GESPRÄCHSVERLAUF (vorherige Sitzung — nahtlos fortsetzen)\n"
        "Dies ist der jüngste Dialog mit Adam vor diesem (Neu-)Start. Nutze ihn, "
        "um SOFORT am letzten Thema anzuknüpfen — frage NICHT neu, worum es ging "
        "oder wofür ein Test war. Bestimme das aktuelle Thema aus den letzten "
        "Einträgen. Prüfe Datum/Uhrzeit der Einträge, bevor du etwas als 'heute' "
        "oder 'gestern' bezeichnest; referenziere Nachrichten über ihre Uhrzeit, "
        "nicht über 'letzte/vorletzte'.\n\n"
    )
    block = header + recall
    core = f"{memory}\n\n---\n\n{block}" if memory else block
    return f"{_QUALITY_GUIDANCE}\n\n---\n\n{core}"


_ARG_SAFE_BYTES = 100_000  # Puffer unter Linux MAX_ARG_STRLEN (131.072 pro exec-Argument)


def _fit_arg_bytes(text: str) -> str:
    """Notbremse: Text argv-tauglich kürzen (Anfang behalten, Memory zuerst)."""
    data = text.encode("utf-8")
    if len(data) <= _ARG_SAFE_BYTES:
        return text
    log.warning("Kontext %d Bytes > argv-Budget %d — gekürzt (Fallback-Pfad)",
                len(data), _ARG_SAFE_BYTES)
    return (data[:_ARG_SAFE_BYTES].decode("utf-8", errors="ignore")
            + "\n\n[⚠️ Kontext wegen Linux-Arg-Limit gekürzt]")


def _write_context_claude_md(context: str) -> bool:
    """Session-Kontext als CLAUDE.md ins WORKDIR schreiben.

    Linux begrenzt ein einzelnes exec-Argument auf 128 KiB (MAX_ARG_STRLEN);
    das volle Memory sprengt das und ließ den Session-Start auf dem VPS mit
    E2BIG scheitern (macOS hat dieses Limit nicht — dort fiel es nie auf).
    Eine Datei hat kein solches Limit; setting_sources=["project"] lädt sie.
    """
    path = Path(WORKDIR) / "CLAUDE.md"
    try:
        if context:
            path.write_text(context, encoding="utf-8")
        elif path.exists():
            path.unlink()  # kein Kontext → keine veraltete Datei stehen lassen
        return True
    except Exception:
        log.exception("CLAUDE.md-Kontextdatei nicht schreibbar — Fallback auf append")
        return False


# ---------- Private Websuche über SearxNG (2.7, kostenfrei/lokal) ----------
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888")


@tool(
    "web_search",
    "Durchsucht das Web über die lokale, private Metasuche (SearxNG) — KOSTENFREI. "
    "Für aktuelle oder überprüfbare Fakten immer dies nutzen, statt aus dem Gedächtnis "
    "zu raten. Gibt Titel, URL und Kurzbeschreibung der Treffer zurück; zum Vertiefen "
    "die URLs mit WebFetch lesen.",
    {"query": str},
)
async def _searxng_search_tool(args: dict) -> dict:
    q = (args.get("query") or "").strip()
    if not q:
        return {"content": [{"type": "text", "text": "Kein Suchbegriff angegeben."}]}
    import httpx
    try:
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(f"{SEARXNG_URL}/search",
                            params={"q": q, "format": "json"})
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        log.exception("SearxNG-Suche fehlgeschlagen")
        return {"content": [{"type": "text",
                             "text": f"Suche fehlgeschlagen: {e}"}]}
    results = (data.get("results") or [])[:8]
    if not results:
        return {"content": [{"type": "text", "text": f"Keine Treffer für „{q}“."}]}
    lines = [f"Suchergebnisse für „{q}“ (lokale private Suche):", ""]
    for i, res in enumerate(results, 1):
        title = " ".join((res.get("title") or "").split())
        url = (res.get("url") or "").strip()
        snippet = " ".join((res.get("content") or "").split())[:300]
        lines.append(f"{i}. {title}\n   {url}\n   {snippet}")
    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


_SEARCH_MCP = create_sdk_mcp_server(name="suche", version="1.0.0",
                                    tools=[_searxng_search_tool])
# Toolname, den der Agent sieht (für Auto-Allow + Bewerbung im Prompt):
_SEARCH_TOOL_NAME = "mcp__suche__web_search"


_UNSET = object()  # Sentinel: effort=None ist ein gültiger Wert (Normal)


async def ensure_session(
    user_id: int,
    *,
    model_override: str | None = None,
    effort_override=_UNSET,
    fresh: bool = False,
) -> UserSession:
    sess = SESSIONS.get(user_id)
    if sess is not None and not fresh:
        return sess
    if sess is not None and fresh:
        await close_session(user_id)  # frische Session mit Overrides erzwingen (🎯 Gründlich)

    memory = load_user_memory()
    context = _session_context(memory)
    user_prefs = _USER_PREFS.get(str(user_id), {})
    model_short = model_override or user_prefs.get("model", DEFAULT_MODEL)
    model_full = _MODEL_ALIASES.get(model_short, model_short)  # vollständige SDK-ID
    effort = user_prefs.get("effort", None) if effort_override is _UNSET else effort_override
    context_via_file = _write_context_claude_md(context)
    # Memory-Ordner mitgeben, damit der Agent Detailwissen bei Bedarf nachlesen
    # kann (Session-Diät 5.23) — liegt außerhalb des WORKDIR.
    add_dirs = [str(_MEMORY_DIR)] if _MEMORY_DIR.exists() else []
    options = ClaudeAgentOptions(
        cwd=str(WORKDIR),
        permission_mode="default",
        can_use_tool=make_permission_callback(user_id),
        model=model_full,
        effort=effort,
        add_dirs=add_dirs,
        # Private, kostenfreie Websuche (2.7) als Standardweg. Anthropic-WebSearch
        # ist seit 23.07. (Adam-Entscheid „Variante 2") NICHT mehr hart deaktiviert,
        # sondern bewusste Notfall-Option: _COST_TOOLS erzwingt für JEDE Nutzung
        # den 💰-Einzeldialog mit Kostenhinweis — nie Always-Allow, nie automatisch.
        mcp_servers={"suche": _SEARCH_MCP},
        setting_sources=["project"] if context_via_file else None,
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": _fit_arg_bytes(context),
        } if (context and not context_via_file) else {"type": "preset", "preset": "claude_code"},
    )
    client = ClaudeSDKClient(options=options)
    await client.connect()
    # 5.25 (c): dauerhaft gemerkte Freigaben laden — dabei SELBSTHEILUNG:
    # Einträge aus _NO_ALWAYS_TOOLS (WebFetch, 💰) werden entfernt und die
    # bereinigte Liste zurückgeschrieben (Adams Live-Klick „Always allow
    # WebFetch" vom 23.07. hätte sonst die Herkunfts-Schranke ausgehebelt).
    _stored_allow = set(user_prefs.get("always_allow", []))
    _cleaned_allow = _stored_allow - _NO_ALWAYS_TOOLS
    if _cleaned_allow != _stored_allow:
        _USER_PREFS.setdefault(str(user_id), {})["always_allow"] = sorted(_cleaned_allow)
        _save_prefs(_USER_PREFS)
        log.info("always_allow bereinigt (user=%s): %s entfernt", user_id,
                 sorted(_stored_allow - _cleaned_allow))
    sess = UserSession(
        client=client,
        user_id=user_id,
        tts_enabled=user_prefs.get("tts_enabled", False),
        current_model=model_short,  # Kurzname für Anzeige und Vergleiche
        current_effort=effort,
        logger=ConversationLogger(user_id),
        always_allowed_tools=_cleaned_allow,
    )
    SESSIONS[user_id] = sess
    log.info("opened session for user_id=%s in %s", user_id, WORKDIR)
    return sess


async def close_session(user_id: int) -> None:
    sess = SESSIONS.pop(user_id, None)
    if sess is None:
        return
    cancel_pending_permissions(sess, reason="session closed by /reset")
    try:
        await sess.client.disconnect()
    except Exception:
        log.exception("error disconnecting session for %s", user_id)


def cancel_pending_permissions(sess: UserSession, reason: str = "session ended") -> int:
    """Resolve any in-flight permission futures so awaiters don't hang forever.
    Returns count of cancelled requests. Cross-loop-safe."""
    n = 0
    for req_id, entry in list(sess.pending_permissions.items()):
        target_loop, fut = entry
        if not fut.done():
            try:
                target_loop.call_soon_threadsafe(fut.set_result, "deny")
                n += 1
            except Exception:
                log.exception("cancel: call_soon_threadsafe failed for req=%s", req_id)
    sess.pending_permissions.clear()
    sess.message_permissions.clear()
    if n:
        log.warning("cancelled %d pending permission(s) — %s", n, reason)
    return n


# ---------- telegram handlers ----------

async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    user_id = update.effective_user.id
    user_prefs = _USER_PREFS.get(str(user_id), {})
    keyboard = _main_keyboard(
        tts_on=user_prefs.get("tts_enabled", False),
        model=user_prefs.get("model", DEFAULT_MODEL),
        effort=user_prefs.get("effort", None),
    )
    await update.message.reply_text(
        "👋 Claude-Code-Bot bereit.\n\n"
        f"Workdir: `{WORKDIR}`\n"
        "Schick mir eine Nachricht und ich starte/setze deine Claude-Session fort.\n\n"
        "Unterstützte Dateitypen:\n"
        "📷 Fotos · 🎬 Videos · 🎙️ Sprachnachrichten · 📎 Dokumente (PDF, Word, …)\n\n"
        "Befehle:\n"
        "/reset — Session beenden (neue beginnt mit nächster Nachricht)\n"
        "/tts — Sprachnachricht-Modus an/aus (Text + Voice parallel)\n"
        "/quiet — Ruhiger Modus (Tipp-Indikator aus; 🔧-Spur bleibt)\n"
        "/verbose — Tipp-Indikator wieder an (🔧-Spur ist immer sichtbar)\n"
        "/status — Session-Info\n"
        "/whoami — Deine Telegram-User-ID\n\n"
        "Permission-Anfragen: Buttons *oder* 👍 (Allow) / 👎 (Deny) als Reaktion.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def cmd_whoami(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Deine Telegram-User-ID: `{user.id}`\n"
        f"Allowed: {'✅' if user.id in ALLOWED_USER_IDS else '❌'}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_whereami(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Gibt Chat-/Gruppen-ID + ggf. Thema-(Thread-)ID des aktuellen Chats aus."""
    if not authorized(update):
        return
    msg = update.effective_message
    chat = update.effective_chat
    lines = [
        f"Typ: {chat.type}",
        f"Chat-ID: `{chat.id}`",
    ]
    if chat.title:
        lines.append(f"Titel: {chat.title}")
    if str(chat.id).startswith("-100"):
        lines.append(f"Interne ID: `{str(chat.id)[4:]}`")
    thread_id = getattr(msg, "message_thread_id", None)
    if thread_id is not None:
        lines.append(f"Thema-(Thread-)ID: `{thread_id}`")
    else:
        lines.append("Thema: keins (Haupt-Chat)")
    await msg.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


async def cmd_reset(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    user_id = update.effective_user.id
    mb = MAILBOXES.get(user_id)
    dropped = 0
    if mb is not None:
        dropped = len(mb.queue)
        mb.queue.clear()
        if mb.worker is not None and not mb.worker.done():
            mb.worker.cancel()
        mb.worker = None
        mb.current_job = None
    await close_session(user_id)
    user_prefs = _USER_PREFS.get(str(user_id), {})
    keyboard = _main_keyboard(
        tts_on=user_prefs.get("tts_enabled", False),
        model=user_prefs.get("model", DEFAULT_MODEL),
        effort=user_prefs.get("effort", None),
    )
    msg = "🔄 Session beendet. Nächste Nachricht startet eine neue."
    if dropped:
        msg += f"\n🗑️ {dropped} wartende Nachricht(en) verworfen."
    await update.message.reply_text(msg, reply_markup=keyboard)


async def cmd_status(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    user_id = update.effective_user.id
    sess = SESSIONS.get(user_id)
    mb = MAILBOXES.get(user_id)

    lines: list[str] = ["📋 Übersicht", ""]

    # Läuft gerade
    if mb and mb.current_job is not None:
        elapsed = int(time.monotonic() - mb.current_started)
        lines.append(f"▶️ Läuft ({elapsed}s): „{_job_preview(mb.current_job.text)}“")
        # 5.18: sichtbar machen, wie lange die Session schon stumm ist — sonst
        # ist „läuft seit 4 Minuten" nicht von „hängt seit 4 Minuten" zu
        # unterscheiden. Erst ab der Hälfte des Limits, sonst nur Rauschen.
        if sess is not None:
            silent = int(time.monotonic() - max(mb.current_started, sess.last_activity))
            if silent > STALL_LIMIT_S // 2:
                lines.append(f"   ⏱️ letzte Regung vor {silent}s "
                             f"(Wächter greift ab {STALL_LIMIT_S}s)")
    else:
        lines.append("▶️ Läuft: nichts")

    # Warteschlange (Reihenfolge der Abarbeitung: neueste zuerst)
    if mb and mb.queue:
        lines.append("")
        lines.append(f"⏳ Warteschlange ({len(mb.queue)}):")
        for i, job in enumerate(mb.queue, 1):
            lines.append(f"  {i}. „{_job_preview(job.text)}“")
    else:
        lines.append("⏳ Warteschlange: leer")

    # Zuletzt erledigt
    if mb and mb.done_log:
        lines.append("")
        lines.append("✅ Zuletzt erledigt:")
        for _ts, preview in list(mb.done_log)[-5:]:
            lines.append(f"  • „{preview}“")

    # Session-Status
    lines.append("")
    if sess is None:
        lines.append("Session: keine aktive (nächste Nachricht startet eine).")
    else:
        lines.append(
            f"Session: aktiv · {'🔕 quiet' if sess.quiet else '🔔 verbose'} · "
            f"Pending permissions: {len(sess.pending_permissions)}"
        )

    if "small" in _STT_MODELS and "medium" in _STT_MODELS:
        lines.append(f"🎙️ Voice-Transkription: {_stt_label(_ACTIVE_STT)}")

    # 5.25 (c): dauerhaft gemerkte Freigaben sichtbar machen.
    _aa = _USER_PREFS.get(str(user_id), {}).get("always_allow", [])
    if _aa:
        lines.append(f"🔓 Dauerfreigaben: {', '.join(_aa)} (/freigaben)")

    # 5.2: liegende Persistenz-Records (Normalbetrieb: leer; nach hartem Reboot
    # zeigt sich hier, was noch nicht abgearbeitet ist).
    try:
        pc = pending.counts()
        if pc:
            total = sum(pc.values())
            detail = ", ".join(f"{n}× {s}" for s, n in sorted(pc.items()))
            lines.append(f"🗂 Persistiert (5.2): {total} ({detail})")
    except Exception:
        log.exception("pending-counts in /status übersprungen (nicht-fatal)")

    await update.message.reply_text("\n".join(lines))


async def cmd_ampel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Datenschutz-Ampel (2.2): Status + Regelverwaltung — rein lokal, ohne Claude.

    /ampel               → Kennzahlen
    /ampel regeln        → Regeln anzeigen
    /ampel rot [L:] <M>  → Rot-Regel hinzufügen (Muster M, optionales Label L)
    /ampel gelb [L:] <M> → Gelb-Regel hinzufügen
    /ampel weg <Muster>  → Regel entfernen
    Muster (z. B. Klienten-Namen) werden NUR lokal auf dem VPS gespeichert,
    nie an Claude/Cloud geschickt (dieses Kommando wird direkt hier abgefangen).
    """
    if not authorized(update):
        return
    args = list(getattr(context, "args", []) or [])
    if args:
        sub = args[0].lower()
        rest = " ".join(args[1:]).strip()
        if sub in ("regeln", "regel", "liste", "list"):
            await update.message.reply_text(ampel.list_rules())
            return
        if sub in ("rot", "gelb"):
            label, pattern = "manuell", rest
            if ":" in rest:
                lbl, pat = rest.split(":", 1)
                if pat.strip():
                    label, pattern = (lbl.strip() or "manuell"), pat.strip()
            await update.message.reply_text(ampel.add_rule(sub, pattern, label))
            return
        if sub in ("weg", "entfernen", "loeschen", "löschen", "remove", "del"):
            await update.message.reply_text(ampel.remove_rule(rest))
            return
        await update.message.reply_text(
            "Nutzung:\n"
            "/ampel — Status & Kennzahlen\n"
            "/ampel regeln — Regeln anzeigen\n"
            "/ampel rot [Label:] <Muster> — Rot-Regel hinzufügen\n"
            "/ampel gelb [Label:] <Muster> — Gelb-Regel hinzufügen\n"
            "/ampel weg <Muster> — Regel entfernen"
        )
        return
    st = ampel.status()
    L = ["🚦 Datenschutz-Ampel — Beobachtungsphase",
         "(nur Einstufung + Protokoll, noch KEIN Umrouten)", ""]
    L.append(f"Eingestuft: {st['count']} / {st['max_count']} Nachrichten")
    if st.get("end_ts"):
        end = time.strftime("%d.%m.%Y %H:%M", time.localtime(st["end_ts"]))
        rem = max(0.0, (st["end_ts"] - time.time()) / 86400)
        L.append(f"Phase endet: {end} (in ~{rem:.1f} Tagen) — oder bei {st['max_count']} Nachrichten")
    else:
        L.append("Phase startet mit der ersten eingestuften Nachricht.")
    c = st["colors"]
    L += ["", f"Verteilung: 🔴 {c.get('rot',0)}   🟡 {c.get('gelb',0)}   🟢 {c.get('gruen',0)}"]
    if st["top_rules"]:
        L.append("")
        L.append("Häufigste Regel-Treffer:")
        for r, n in st["top_rules"]:
            L.append(f"  • {r}: {n}")
    rf = "vorhanden" if st["rules_file_exists"] else "eingebaute Defaults (Datei fehlt)"
    L += ["", f"Regeldatei: {rf}"]
    if st["phase_over"]:
        L += ["", "⚠️ Beobachtungsphase ABGELAUFEN — Auswertung + Enforcement stehen an."]
    await update.message.reply_text("\n".join(L), reply_markup=_ampel_menu_markup())


def _ampel_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Neue Regel", callback_data="amp:new"),
            InlineKeyboardButton("📋 Regeln zeigen", callback_data="amp:list"),
        ],
        [InlineKeyboardButton("🗑 Regel löschen", callback_data="amp:del")],
    ])


async def on_ampel_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Ampel-Menü — rein deterministisch in bot.py, ohne Claude-Beteiligung."""
    q = update.callback_query
    user_id = q.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        await q.answer("Nicht berechtigt.")
        return
    data = q.data or ""

    if data == "amp:list":
        await q.answer()
        await q.message.reply_text(ampel.list_rules(), reply_markup=_ampel_menu_markup())
        return

    if data == "amp:new":
        await q.answer()
        await q.message.reply_text(
            "Welche Farbe soll die neue Regel bekommen?",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔴 Rot", callback_data="amp:c:rot"),
                InlineKeyboardButton("🟡 Gelb", callback_data="amp:c:gelb"),
                InlineKeyboardButton("🟢 Grün", callback_data="amp:c:gruen"),
            ]]),
        )
        return

    if data == "amp:c:gruen":
        await q.answer()
        await q.message.reply_text(
            "🟢 Grün ist der Standard (alles ohne Regel-Treffer) — Regeln gibt es "
            "nur für 🔴 Rot und 🟡 Gelb."
        )
        return

    if data in ("amp:c:rot", "amp:c:gelb"):
        color = data.rsplit(":", 1)[1]
        _AMPEL_CAPTURE[user_id] = {"color": color, "expires": time.time() + _AMPEL_CAPTURE_TTL}
        icon = "🔴" if color == "rot" else "🟡"
        await q.answer()
        await q.message.reply_text(
            f"{icon} ERFASSUNGSMODUS ({_AMPEL_CAPTURE_TTL} s): Schick jetzt den Begriff "
            f"als nächste Nachricht — optional mit Label, z. B. „Klient: Max Mustermann“.\n"
            f"Die Nachricht wird OHNE Claude-Beteiligung direkt in die lokale "
            f"Regeldatei übernommen (cloud-frei)."
        )
        return

    if data == "amp:del":
        custom = ampel._load_custom()
        rows = []
        for color in ("rot", "gelb"):
            for i, e in enumerate(custom.get(color) or []):
                label = (e.get("pattern") or "")[:24]
                icon = "🔴" if color == "rot" else "🟡"
                rows.append([InlineKeyboardButton(
                    f"🗑 {icon} {label}", callback_data=f"amp:rm:{color}:{i}")])
        await q.answer()
        if not rows:
            await q.message.reply_text("Keine eigenen Regeln vorhanden (Basis-Regeln "
                                       "liegen in der TOML-Datei auf dem Server).")
            return
        await q.message.reply_text("Welche Regel löschen?", reply_markup=InlineKeyboardMarkup(rows))
        return

    if data.startswith("amp:rm:"):
        try:
            _, _, color, idx_s = data.split(":", 3)
            idx = int(idx_s)
            custom = ampel._load_custom()
            entry = (custom.get(color) or [])[idx]
            msg = ampel.remove_rule(entry.get("pattern", ""))
        except (IndexError, ValueError):
            msg = "Regel nicht mehr vorhanden (Liste veraltet — /ampel erneut öffnen)."
        await q.answer()
        await q.message.reply_text(msg)
        return

    await q.answer()


async def cmd_presend(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Kennzahlen des Pre-Send-Hooks (8.5) — Fehlalarm-Quote im Blick behalten."""
    if not authorized(update):
        return
    st = presend.status()
    L = ["🛡 Pre-Send-Hook — Kennzahlen", ""]
    L.append(f"Antworten mit Befund: {st['antworten_mit_befund']}")
    a = st["arten"]
    L.append(f"  • automatisch korrigiert: {a.get('autofix', 0)}")
    L.append(f"  • Korrekturrunde nötig:   {a.get('korrektur', 0)}")
    L.append(f"  • nur protokolliert:      {a.get('log', 0)}")
    if st["codes"]:
        L += ["", "Nach Prüfung:"]
        for code, n in sorted(st["codes"].items(), key=lambda x: -x[1]):
            L.append(f"  • {code}: {n}")
    if st["korrektur_erfolgreich"] or st["korrektur_fehlgeschlagen"]:
        L += ["", f"Korrekturrunden: {st['korrektur_erfolgreich']} erfolgreich, "
                  f"{st['korrektur_fehlgeschlagen']} mit ⚠️-Vermerk gesendet"]
    L += ["", "v1 prüft: Wochentag↔Datum (auto-fix), Vollständigkeit (Korrektur), "
              "relative Datumsangaben + Tentativ-Sprache (nur Log)."]
    await update.message.reply_text("\n".join(L))


async def cmd_usage(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    today = _usage_today()
    if not today:
        await update.message.reply_text("📊 Noch kein Verbrauch heute (nur Bot-Kanal).")
        return
    lines = ["📊 Bot-Verbrauch heute (nur Telegram-Kanal):"]
    for mk, u in today.items():
        short = "Opus" if "opus" in mk else "Sonnet"
        inp = u.get("input", 0)
        out = u.get("output", 0)
        reqs = u.get("requests", 0)
        cost = u.get("cost_usd", 0.0)
        lines.append(f"\n{short}:")
        lines.append(f"  Input:    {inp:,} Tokens")
        lines.append(f"  Output:   {out:,} Tokens")
        lines.append(f"  Gesamt:   {inp + out:,} Tokens")
        lines.append(f"  Anfragen: {reqs}")
        if cost:
            lines.append(f"  Kosten:   ~${cost:.4f}")
    lines.append("\n⚠️ Desktop-App und claude.ai werden hier nicht erfasst.")
    await update.message.reply_text("\n".join(lines))


async def cmd_hilfe(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    text = (
        "🤖 Alle Befehle:\n\n"
        "/start — Begrüßung & Keyboard einblenden\n"
        "/reset — Session zurücksetzen\n"
        "/status — Aktuelle Queue & Session-Übersicht\n"
        "/usage — Token-Verbrauch heute (Bot-Kanal)\n"
        "/ampel — Datenschutz-Ampel: Regeln & Status\n"
        "/presend — Pre-Send-Hook: Kennzahlen\n"
        "/tts — TTS an/aus umschalten\n"
        "/ttsdemo — TTS-Testausgabe\n"
        "/quiet — Tipp-Indikator aus (🔧-Spur bleibt sichtbar)\n"
        "/verbose — Tipp-Indikator wieder an\n"
        "/setkanal — Ausgabekanal setzen\n"
        "/whereami — Kanal-Info anzeigen\n"
        "/whoami — User-Info\n"
        "/stopp — ✋ Laufende Aufgabe abbrechen\n"
        "/freigaben — Dauerfreigaben zeigen: Werkzeuge + vertraute Domains "
        "(reset zum Löschen)\n"
        "/technik — Werkzeug-Spur: Klartext ↔ technische Rohform\n"
        "/spur — Werkzeug-Spur ganz aus/an (Rückfragen bleiben)\n"
        "/restart — Bot neu starten\n"
        "/selfcheck — Selbsttest ausführen\n"
        "/hilfe — Diese Befehlsübersicht\n\n"
        "💬 Emoji-Reaktionen: Du kannst auf meine Nachrichten reagieren — "
        "ich verstehe das feste Vokabular (👍 👌 🫡 = Ja/erledigt, 👎 = Nein, "
        "🤔 = unsicher, 🤨 🤷 = erklär nochmal, 🔥 ⚡ = los geht's, 👀 = genauer "
        "anschauen, ✍ 👨‍💻 🏆 = merk dir das, 😴 = später, ❤️ 🎉 👏 💯 🍓 🍌 = "
        "Wertschätzung). Auf offene Fragen ist die Reaktion die Antwort. "
        "Nummerierte Optionslisten bekommen 1️⃣–9️⃣-Knöpfe.\n\n"
        "📌 Buttons in der Tastatur (9):\n"
        "🟣 Haiku / 🟡 Sonnet / 🔵 Opus / 🟠 Fable — Modell wechseln\n"
        "⚡ Schnell / ⚖️ Normal / 🚀 Max — Denk-Tiefe\n"
        "🎙️ Genau ✓ → Flott (bzw. umgekehrt) — Transkriptions-Tempo: ✓ markiert "
        "den aktiven Modus, ein Tipp führt den gezeigten Wechsel aus\n"
        "🎯 Gründlich — nächste Frage besonders sorgfältig "
        "(aktives Modell · max. Tiefe · Quellencheck)\n\n"
        "Neustart, TTS und Info liegen im „/“-Menü, nicht mehr in der Tastatur."
    )
    await update.message.reply_text(text)


async def cmd_tts(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    user_id = update.effective_user.id
    sess = await ensure_session(user_id)
    sess.tts_enabled = not sess.tts_enabled
    _USER_PREFS.setdefault(str(user_id), {})["tts_enabled"] = sess.tts_enabled
    _save_prefs(_USER_PREFS)
    keyboard = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
    if sess.tts_enabled:
        await update.message.reply_text(
            f"🔊 Sprachnachricht-Modus an — Stimme: {TTS_VOICE}",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text("🔇 Sprachnachricht-Modus aus.", reply_markup=keyboard)


async def cmd_ttsdemo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Sendet das letzte Transkript in allen drei TTS-Varianten als Vergleich."""
    if not authorized(update):
        return
    user_id = update.effective_user.id
    text = _LAST_TRANSCRIPTION.get(user_id)
    if not text:
        await update.message.reply_text(
            "❌ Kein Transkript gespeichert — schick zuerst eine Sprachnachricht, dann /ttsdemo."
        )
        return

    bot = update.get_bot()
    chat_id = update.effective_chat.id
    tts_text = _strip_markdown_for_tts(text)
    audio_chunk = tts_text[:TTS_CHUNK_CHARS]
    caption_full = text[:1024] if len(text) <= 1024 else text[:1021] + "…"
    short_label = (text[:80] + "…") if len(text) > 80 else text

    # Variante A: kein Live-Text, nur Sprachnachricht mit vollem Text als Caption
    await send_chunked(bot, chat_id,
        "━━━━━━━━━━━━━━━━━\n"
        "🅰 *Variante A* — Warten, dann Caption\n"
        "Kein Live-Text. Nur Stimme + voller Text als Caption.",
        parse_mode="Markdown",
    )
    await _send_tts_chunk(bot, chat_id, audio_chunk, caption=caption_full)

    await asyncio.sleep(1)

    # Variante B: Text live + danach Stimme mit gleichem Text als Caption (Doppel)
    await send_chunked(bot, chat_id,
        "━━━━━━━━━━━━━━━━━\n"
        "🅱 *Variante B* — Live-Text + Caption\n"
        "Erst Text live, dann Stimme — selber Text in Caption (Doppel).",
        parse_mode="Markdown",
    )
    await send_chunked(bot, chat_id, text)
    await _send_tts_chunk(bot, chat_id, audio_chunk, caption=caption_full)

    await asyncio.sleep(1)

    # Variante C: Text live + danach Stimme mit kurzem Label (kein Doppel)
    await send_chunked(bot, chat_id,
        "━━━━━━━━━━━━━━━━━\n"
        "🅲 *Variante C* — Live-Text + Kurz-Label\n"
        "Erst Text live, dann Stimme mit kurzem Themen-Label.",
        parse_mode="Markdown",
    )
    await send_chunked(bot, chat_id, text)
    await _send_tts_chunk(bot, chat_id, audio_chunk, caption=f"🎙️ {short_label}")

    await send_chunked(bot, chat_id, "✅ Demo fertig. Welche Variante gefällt dir am besten?")


async def _send_original_to_channel(bot, chat_id: int, path: Path, filename: str,
                                    reply_markup=None):
    """Schickt die Original-Datei in den (Ausgabe-)Kanal, damit sie dort anklickbar ist.
    Gibt das gesendete Message-Objekt zurück (oder None bei Fehler)."""
    try:
        with path.open("rb") as f:
            return await bot.send_document(chat_id=chat_id, document=f, filename=filename,
                                           reply_markup=reply_markup)
    except Exception:
        log.exception("Original-Datei in Kanal senden fehlgeschlagen")
        return None


async def on_pdf_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Verarbeitet die Auswahl Zusammenfassen / Komplett vorlesen für PDF-Dokumente."""
    query = update.callback_query
    await query.answer()
    parts = (query.data or "").split(":", 2)
    if len(parts) != 3 or parts[0] != "pdf":
        return
    user_id = int(parts[1])
    action = parts[2]

    # NICHT `pending` nennen — überschattet sonst das Modul `pending` (5.2).
    pending_doc = _PENDING_DOCS.pop(user_id, None)
    if not pending_doc:
        await query.edit_message_text("Dokument nicht mehr verfügbar — bitte erneut senden.")
        return

    doc_parts: list[str] = pending_doc["parts"]
    prefix: str = pending_doc["prefix"]
    orig_update: Update = pending_doc["update"]
    filename: str = pending_doc["filename"]
    size_mb: float = pending_doc["size_mb"]

    cid, ch_title, ch_url = get_output_channel()
    chat_id = orig_update.effective_chat.id
    in_channel = cid and cid != chat_id

    username = _USER_PREFS.get("output_channel_username")

    if action == "summary":
        summary_ch = cid or chat_id
        if in_channel:
            await query.edit_message_text(
                f"{filename} ({size_mb:.1f} MB) — Zusammenfassen, Ausgabe in {ch_title} …",
            )
        else:
            await query.edit_message_text(f"{filename} ({size_mb:.1f} MB) — Zusammenfassen …")

        local_path_str = pending_doc.get("local_path", "")
        local_path_obj = Path(local_path_str) if local_path_str else None
        bot = query.get_bot()

        if local_path_obj and local_path_obj.exists() and filename.lower().endswith(".pdf"):
            try:
                summary = await _summarize_pdf_direct(local_path_obj)
                sess = SESSIONS.get(orig_update.effective_user.id)
                tts_active = bool(sess and sess.tts_enabled)
                if tts_active:
                    # Voice + Text gekoppelt: Voice mit Text als Caption, statt zweier separater Posts.
                    first_msg = await _send_tts(bot, summary_ch, summary, coupled_text=summary)
                else:
                    first_msg = await send_chunked(bot, summary_ch, summary)
                orig_msg = None
                if in_channel:
                    orig_msg = await _send_original_to_channel(
                        bot, summary_ch, local_path_obj, filename,
                        reply_markup=_back_to_bot_markup(),
                    )
                if in_channel:
                    post_id = first_msg.message_id if first_msg else None
                    orig_id = orig_msg.message_id if orig_msg else None
                    import html as _html
                    ch_link = _channel_title_link_html(cid, ch_title, username, post_id)
                    safe_fn = _html.escape(filename)
                    await query.edit_message_text(
                        f"✅ {safe_fn} zusammengefasst — Ausgabe in {ch_link}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=_channel_post_markup(cid, post_id, username, orig_id),
                    )
            except Exception as e:
                log.exception("PDF direct summary failed")
                await send_chunked(bot, chat_id, f"❌ Zusammenfassung fehlgeschlagen: {e}")
        else:
            # Fallback für Nicht-PDF (Word, Text etc.) → Agent SDK
            instruction = "Fasse dieses Dokument bitte kurz und prägnant zusammen."
            full_parts = doc_parts + [f"Aufgabe: {instruction}"]
            await process_user_text(
                orig_update,
                prefix + "\n".join(full_parts),
                output_chat_id=summary_ch,
                log_note=f"📎 Datei: {filename} · {size_mb:.1f} MB",
            )
        return

    if action == "summary_voice":
        # Zusammenfassung + Sprachnachricht in einem Rutsch — speziell für
        # technische PDFs, die als Volltext-Vorlesen holprig wären.
        summary_ch = cid or chat_id
        if in_channel:
            await query.edit_message_text(
                f"{filename} ({size_mb:.1f} MB) — Kurzfassung wird erstellt und vorgelesen, "
                f"Ausgabe in {ch_title} …",
            )
        else:
            await query.edit_message_text(
                f"{filename} ({size_mb:.1f} MB) — Kurzfassung wird erstellt und vorgelesen …"
            )

        local_path_str = pending_doc.get("local_path", "")
        local_path_obj = Path(local_path_str) if local_path_str else None
        bot = query.get_bot()

        if local_path_obj and local_path_obj.exists() and filename.lower().endswith(".pdf"):
            try:
                summary = await _summarize_pdf_direct(local_path_obj)
                # Voice + Text gekoppelt: unabhängig vom Toggle, denn genau das ist
                # der Sinn dieses Knopfes.
                first_msg = await _send_tts(bot, summary_ch, summary, coupled_text=summary)
                orig_msg = None
                if in_channel:
                    orig_msg = await _send_original_to_channel(
                        bot, summary_ch, local_path_obj, filename,
                        reply_markup=_back_to_bot_markup(),
                    )
                if in_channel:
                    post_id = first_msg.message_id if first_msg else None
                    orig_id = orig_msg.message_id if orig_msg else None
                    import html as _html
                    ch_link = _channel_title_link_html(cid, ch_title, username, post_id)
                    safe_fn = _html.escape(filename)
                    await query.edit_message_text(
                        f"✅ {safe_fn} — Kurzfassung + Sprachnachricht in {ch_link}",
                        parse_mode=ParseMode.HTML,
                        reply_markup=_channel_post_markup(cid, post_id, username, orig_id),
                    )
            except Exception as e:
                log.exception("PDF summary_voice failed")
                await send_chunked(bot, chat_id,
                                   f"❌ Kurzfassung anhören fehlgeschlagen: {e}")
        else:
            await query.edit_message_text("❌ Kurzfassung anhören ist nur für PDFs verfügbar.")
        return

    # "full" — direkte kapitelweise TTS, kein Claude-Umweg
    local_path_str = pending_doc.get("local_path", "")
    local_path = Path(local_path_str) if local_path_str else None
    if not local_path or not local_path.exists():
        await query.edit_message_text(f"❌ Datei nicht mehr verfügbar: {local_path_str}")
        return

    try:
        pdf_text = _extract_pdf_text(local_path)
    except Exception as e:
        await query.edit_message_text(f"❌ PDF-Extraktion fehlgeschlagen: {e}")
        return

    chapters = _split_pdf_by_chapters(pdf_text)
    target = cid or chat_id
    bot = query.get_bot()
    post_id = None
    if in_channel:
        orig_msg = await _send_original_to_channel(
            bot, target, local_path, filename, reply_markup=_back_to_bot_markup()
        )
        post_id = orig_msg.message_id if orig_msg else None
        import html as _html
        ch_link = _channel_title_link_html(cid, ch_title, username, post_id)
        safe_fn = _html.escape(filename)
        await query.edit_message_text(
            f"📻 {safe_fn} ({size_mb:.1f} MB) — {len(chapters)} Kapitel, Ausgabe in {ch_link}",
            parse_mode=ParseMode.HTML,
            reply_markup=_channel_post_markup(cid, post_id, username),
        )
    else:
        await query.edit_message_text(
            f"📻 {filename} ({size_mb:.1f} MB) — {len(chapters)} Kapitel"
        )
    asyncio.create_task(
        _send_pdf_chapters_tts(bot, chat_id, target, filename, chapters, post_id)
    )


async def _provision_house(bot, chat, house_key: str) -> None:
    """6.5: Legt für ein erkanntes Haus (Forum-Gruppe) die fehlenden Zimmer
    (Topics) an — ratenbegrenzt (≈1 Anlage/Sekunde) mit 429-Backoff. Idempotent:
    bereits angelegte Zimmer werden übersprungen (Prefs führen die Topic-IDs)."""
    from telegram.error import RetryAfter, TelegramError

    spec = channels.HOUSES[house_key]
    channels.register_house(_USER_PREFS, house_key, chat.id,
                            chat.title or spec["title"],
                            bool(getattr(chat, "is_forum", False)))
    todo = channels.missing_zimmer(_USER_PREFS, house_key)
    created: list[str] = []
    failed: list[str] = []
    if not todo:
        _save_prefs(_USER_PREFS)
        for uid in ALLOWED_USER_IDS:
            try:
                await bot.send_message(
                    chat_id=uid,
                    text=(f'{spec["emoji"]} Haus „{spec["title"]}" erkannt — '
                          "alle Zimmer sind bereits angelegt."))
            except Exception:
                log.exception("house-provision notify failed for %s", uid)
        return

    for i, zimmer in enumerate(todo):
        for attempt in range(3):
            try:
                topic = await bot.create_forum_topic(chat_id=chat.id, name=zimmer)
                channels.record_topic(_USER_PREFS, house_key, zimmer,
                                      topic.message_thread_id)
                created.append(zimmer)
                break
            except RetryAfter as e:
                # Telegram-Flood-Limit: exakt so lange warten wie gefordert.
                wait = float(getattr(e, "retry_after", 2)) + 0.5
                log.warning("createForumTopic 429 — warte %.1fs (%s)", wait, zimmer)
                await asyncio.sleep(wait)
            except TelegramError:
                log.exception("createForumTopic fehlgeschlagen: %s", zimmer)
                failed.append(zimmer)
                break
        # Rate-Limit-Schonung: ~1 Anlage/Sekunde (20/min je Gruppe bleibt safe).
        if i < len(todo) - 1:
            await asyncio.sleep(1.1)

    _save_prefs(_USER_PREFS)

    done = channels.house_overview(_USER_PREFS)
    hinfo = next((h for h in done if h["key"] == house_key), None)
    lines = [f'{spec["emoji"]} Haus „{spec["title"]}" eingerichtet.']
    if created:
        lines.append("Neu angelegte Zimmer:\n• " + "\n• ".join(created))
    if failed:
        lines.append("⚠️ Nicht angelegt (bitte prüfen):\n• " + "\n• ".join(failed))
    if hinfo:
        lines.append(f'Stand: {hinfo["zimmer_done"]}/{hinfo["zimmer_total"]} Zimmer.')
    if house_key == "werkstatt":
        lines.append("Bot-Status läuft künftig automatisch ins Zimmer "
                     "Migration & Technik, Unzugeordnetes nach Offene Punkte.")
    if house_key == "bibliothek":
        lines.append("Recherche- und PDF-Lieferungen laufen künftig automatisch "
                     "ins Zimmer Recherchen & Referenzen.")
    for uid in ALLOWED_USER_IDS:
        try:
            await bot.send_message(chat_id=uid, text="\n".join(lines))
        except Exception:
            log.exception("house-provision notify failed for %s", uid)


async def on_my_chat_member(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot wurde in einen Kanal als Admin eingetragen — direkt als Output-Kanal speichern."""
    member_update = update.my_chat_member
    if not member_update:
        return
    chat = member_update.chat
    new_status = member_update.new_chat_member.status if member_update.new_chat_member else None
    if new_status not in ("administrator", "creator", "member"):
        return

    bot = update.get_bot()

    # Gruppen/Supergruppen: nur die ID melden, NICHT den Output-Kanal überschreiben.
    if chat.type in ("group", "supergroup"):
        house_key = channels.detect_house(chat.title)
        is_forum = bool(getattr(chat, "is_forum", False))
        # 6.5: Erkennt der Bot am Gruppennamen ein Haus UND ist der Forum-Modus
        # aktiv, legt er die zugehörigen Zimmer (Topics) selbst an.
        if house_key and is_forum:
            await _provision_house(bot, chat, house_key)
            return
        lines = [
            f'Gruppe „{chat.title or chat.id}" erkannt.',
            f"Gruppen-ID: {chat.id}",
        ]
        if str(chat.id).startswith("-100"):
            lines.append(f"Interne ID: {str(chat.id)[4:]}")
        if house_key and not is_forum:
            spec = channels.HOUSES[house_key]
            lines.append(
                f'Das sieht nach dem Haus {spec["emoji"]} „{spec["title"]}" aus — '
                "aber der Forum-Modus (Themen) ist noch aus. Aktiviere ihn in den "
                "Gruppen-Einstellungen, dann lege ich die Zimmer automatisch an.")
        elif is_forum:
            lines.append("Forum-Modus (Themen) aktiv — Thema-IDs holst du mit /whereami im jeweiligen Thema.")
        for uid in ALLOWED_USER_IDS:
            try:
                await bot.send_message(chat_id=uid, text="\n".join(lines))
            except Exception:
                log.exception("could not notify user %s about group", uid)
        return

    if chat.type != "channel" or new_status not in ("administrator", "creator"):
        return

    channel_id = chat.id
    channel_title = chat.title or str(channel_id)
    channel_username = chat.username  # None bei privaten Kanälen

    _USER_PREFS["output_channel_id"] = channel_id
    _USER_PREFS["output_channel_title"] = channel_title
    _USER_PREFS["output_channel_username"] = channel_username
    _USER_PREFS["summary_channel_id"] = channel_id
    _USER_PREFS["tts_channel_id"] = channel_id
    _save_prefs(_USER_PREFS)

    for uid in ALLOWED_USER_IDS:
        try:
            await bot.send_message(
                chat_id=uid,
                text=f"Kanal {channel_title} als Output-Kanal gespeichert.\nAlle Ausgaben (Zusammenfassungen + Vorlesen) gehen dorthin.",
                reply_markup=_channel_post_markup(channel_id, None, channel_username),
            )
        except Exception:
            log.exception("could not notify user %s about new channel", uid)


async def on_channel_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Speichert Kanal-Zuordnung (Legacy-Callback, setzt jetzt immer output_channel_id)."""
    query = update.callback_query
    await query.answer()
    if not authorized(update):
        return
    parts = (query.data or "").split(":", 2)
    if len(parts) != 3 or parts[0] != "ch":
        return
    channel_id = int(parts[1])

    _USER_PREFS["output_channel_id"] = channel_id
    _USER_PREFS["summary_channel_id"] = channel_id
    _USER_PREFS["tts_channel_id"] = channel_id
    _save_prefs(_USER_PREFS)

    title = _USER_PREFS.get("output_channel_title") or str(channel_id)
    url = _channel_url(channel_id, _USER_PREFS.get("output_channel_username"))
    await query.edit_message_text(
        f'Kanal <a href="{url}">{title}</a> als Output-Kanal gespeichert.',
        parse_mode=ParseMode.HTML,
    )


async def cmd_quiet(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    sess = await ensure_session(update.effective_user.id)
    sess.quiet = True
    await update.message.reply_text(
        "🔕 Ruhiger Modus an — Tipp-Indikator aus. Die 🔧-Werkzeug-Spur bleibt als "
        "Lebenszeichen sichtbar.")


async def cmd_verbose(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    sess = await ensure_session(update.effective_user.id)
    sess.quiet = False
    await update.message.reply_text(
        "🔔 Verbose-Modus an — Tipp-Indikator läuft wieder mit (die 🔧-Spur ist "
        "ohnehin immer sichtbar).")


async def cmd_spur(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """5.25 (d) /spur: schaltet die 🔧-FYI-Werkzeug-Spur pro Aufruf komplett stumm
    (Toggle, per-User). Allow/Deny-Rückfragen bleiben IMMER sichtbar."""
    if not authorized(update):
        return
    user_id = update.effective_user.id
    prefs = _USER_PREFS.setdefault(str(user_id), {})
    now_off = not prefs.get("trace_off", True)  # Default aus (24.07.)
    prefs["trace_off"] = now_off
    _save_prefs(_USER_PREFS)
    if now_off:
        await update.message.reply_text(
            "🔇 Werkzeug-Spur aus — die 🔧-FYI-Zeilen pro Tool-Aufruf sind still. "
            "Sicherheits-Rückfragen (Allow/Deny) kommen weiter. "
            "Mit /spur wieder anschalten.")
    else:
        await update.message.reply_text(
            "🔧 Werkzeug-Spur an — du siehst wieder pro Aufruf, was ich tue.")


async def cmd_setkanal(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Setzt den Output-Kanal für alle Ausgaben (Zusammenfassungen + Vorlesen).

    Verwendung:
      /setkanal -100XXXXXXXXX
      /setkanal status
    """
    if not authorized(update):
        return
    args = (update.message.text or "").split()[1:]
    if not args or args[0] == "status":
        cid, title, url = get_output_channel()
        if cid:
            await update.message.reply_text(
                f'Output-Kanal: <a href="{url}">{title}</a> ({cid})\n\nÄndern mit:\n/setkanal -100XXXXXXXXX',
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text(
                "Kein Output-Kanal konfiguriert.\nSetzen mit:\n/setkanal -100XXXXXXXXX"
            )
        return
    # Legacy-Syntax /setkanal tts|summary -100xxx weiterhin tolerieren
    if args[0] in ("tts", "summary") and len(args) >= 2:
        channel_raw = args[1]
    else:
        channel_raw = args[0]
    try:
        channel_id = int(channel_raw)
    except ValueError:
        await update.message.reply_text(
            f"Ungültige Kanal-ID: {channel_raw} — muss eine Zahl sein (z.B. -1001234567890)."
        )
        return
    _USER_PREFS["output_channel_id"] = channel_id
    _USER_PREFS["summary_channel_id"] = channel_id
    _USER_PREFS["tts_channel_id"] = channel_id
    _save_prefs(_USER_PREFS)
    url = _channel_url(channel_id, _USER_PREFS.get("output_channel_username"))
    await update.message.reply_text(
        f'Output-Kanal gespeichert: <a href="{url}">{channel_id}</a>\nAlle Ausgaben (Zusammenfassungen + Vorlesen) gehen dorthin.',
        parse_mode=ParseMode.HTML,
    )


async def on_permission_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Resolve the pending permission Future ASAP. The visual ack on the
    original message is best-effort — never let a formatting error block the
    actual permission decision from flowing back to the SDK."""
    # Entry log BEFORE auth so we can see callbacks arrive even from wrong users
    log.info("on_permission_callback ENTER: user=%s data=%r",
             update.effective_user.id if update.effective_user else None,
             update.callback_query.data if update.callback_query else None)

    if not authorized(update):
        return
    query = update.callback_query

    # 1. Always answer the callback within 15s or Telegram shows "loading… abort"
    try:
        await query.answer()
    except Exception:
        log.exception("query.answer failed")

    # 2. Parse decision
    parts = (query.data or "").split(":", 3)
    if len(parts) < 3 or parts[0] != "p":
        log.warning("unknown callback_data: %r", query.data)
        return
    request_id = parts[1]
    decision = ":".join(parts[2:])
    log.info("permission callback: user=%s req=%s decision=%s",
             update.effective_user.id, request_id, decision)

    # 3. Resolve future BEFORE any UI work — that's what actually unblocks Claude.
    # CROSS-LOOP-SAFE: the future may have been created on a different event
    # loop (the SDK's), so we use call_soon_threadsafe on its loop.
    sess = SESSIONS.get(update.effective_user.id)
    suffix = None
    if sess is None:
        suffix = "(Session weg)"
    else:
        entry = sess.pending_permissions.pop(request_id, None)
        if entry is None:
            suffix = "(bereits beantwortet oder Session-Neustart)"
        else:
            target_loop, fut = entry
            if fut.done():
                suffix = "(bereits beantwortet)"
            else:
                try:
                    target_loop.call_soon_threadsafe(fut.set_result, decision)
                except Exception:
                    log.exception("call_soon_threadsafe failed")
                    suffix = "(intern: konnte Future nicht setzen)"
                else:
                    label = {"allow": "✅ Allow", "deny": "❌ Deny"}.get(decision, decision)
                    if decision.startswith("always:"):
                        label = f"🔓 Always allow {decision.split(':', 1)[1]}"
                    suffix = f"→ {label}"

    # 4. Best-effort: append result to the original message. Plain text only —
    # no parse_mode, no markdown roundtrip (filenames with ~ or _ break it).
    try:
        original = query.message.text or ""
        new_text = f"{original}\n\n{suffix}"[:4000]
        await query.edit_message_text(text=new_text, reply_markup=None)
    except Exception:
        log.exception("edit_message_text failed (ignored — permission already resolved)")


_REACTION_DECISIONS = {"👍": "allow", "👎": "deny"}


async def on_reaction(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Reaktionen auswerten: erst Permission-Flow (Vorrang), dann 5.9-Vokabular.

    5.9 (Vokabular v2.1): Eine Reaktion auf eine registrierte offene Frage ist
    deren ANTWORT und geht immer an den Agenten. Auf sonstige Bot-Nachrichten
    lösen nur Handlungs-Klassen einen Lauf aus (ja/nein/unklar/los/…); stille
    Wertschätzung (❤️ 🎉 👏 💯 🍓 🍌 …) landet nur im Gesprächs-Log — kein
    Lärm, kein Kontingent. Unbekanntes → freundlich nachfragen, nie raten."""
    rx = update.message_reaction
    if rx is None:
        return
    user_id = rx.user.id if rx.user else None
    if user_id not in ALLOWED_USER_IDS:
        return

    sess = SESSIONS.get(user_id)

    # ── Vorrang: wartende Permission (👍 Allow / 👎 Deny) — unverändert ──
    if sess is not None:
        request_id = sess.message_permissions.get(rx.message_id)
        if request_id is not None:
            for reaction in rx.new_reaction:
                if not isinstance(reaction, ReactionTypeEmoji):
                    continue
                decision = _REACTION_DECISIONS.get(reaction.emoji)
                if decision is None:
                    continue
                sess.message_permissions.pop(rx.message_id, None)
                entry = sess.pending_permissions.pop(request_id, None)
                if entry is None:
                    return
                target_loop, fut = entry
                if not fut.done():
                    target_loop.call_soon_threadsafe(fut.set_result, decision)
                log.info("reaction permission: user=%s req=%s decision=%s",
                         user_id, request_id, decision)
                return
            return  # Permission wartet, aber Emoji war keins der beiden → ignorieren

    # ── 5.9: Vokabular-Reaktion auf beliebige Bot-Nachricht ──
    # Delta-Logik (Adam 23.07.): Telegram liefert ALTE und NEUE Reaktionsmenge.
    # Nur das DELTA zählt — Hinzugefügtes wird behandelt, Entferntes widerrufen,
    # bei Ersetzen/Ergänzen (Premium: mehrere Reaktionen) wird das benannt.
    chat_id = rx.chat.id
    old_list = [r.emoji for r in (getattr(rx, "old_reaction", None) or [])
                if isinstance(r, ReactionTypeEmoji)]
    new_list = [r.emoji for r in rx.new_reaction if isinstance(r, ReactionTypeEmoji)]
    old_set = {reactions.normalize(e) for e in old_list}
    new_set = {reactions.normalize(e) for e in new_list}
    added = [e for e in new_list if reactions.normalize(e) not in old_set]
    removed = [e for e in old_list if reactions.normalize(e) not in new_set]

    if not added and removed:
        await _handle_reaction_withdrawal(user_id, chat_id, rx.message_id,
                                          removed[0], update.get_bot(), sess)
        return
    if not added:
        return  # keine inhaltliche Änderung (z. B. Custom-Emoji)
    emoji = added[0]
    entry = reactions.lookup(emoji)
    kept = [e for e in new_list if reactions.normalize(e) != reactions.normalize(emoji)]

    frage = reactions.pop_question(chat_id, rx.message_id)
    bezug = (frage or {}).get("text") or BOT_MSGS.get((chat_id, rx.message_id), "")
    bezug_kurz = _job_preview(bezug, 220) if bezug else ""

    if entry is None:
        # Außerhalb des Vokabulars: nicht raten — freundlich nachfragen.
        try:
            await update.get_bot().send_message(
                chat_id=chat_id,
                text=(f"{emoji} — diese Reaktion kenne ich noch nicht. "
                      "Was möchtest du mir damit sagen? (Wenn sie eine feste "
                      "Bedeutung bekommen soll, nehmen wir sie ins Vokabular auf.)"),
                reply_to_message_id=rx.message_id,
            )
        except Exception:
            log.exception("Nachfrage zu unbekannter Reaktion nicht zustellbar")
        return

    # Ins Gesprächs-Log — Reaktionen sind sonst unsichtbar für die Kontrollsitzung.
    if sess is not None and sess.logger:
        sess.logger.log_event(f"{emoji} Reaktion von Adam: {entry.meaning}"
                              + (f" — auf: „{bezug_kurz}“" if bezug_kurz else ""))

    if frage is None and not entry.active:
        log.info("Reaktion %s (%s) ohne offene Frage — stille Wertschätzung, kein Lauf",
                 emoji, entry.kind)
        return

    # Antwort/Handlung → als Job an den Agenten (5.2-persistiert, Reply-Bezug).
    if removed:
        wechsel = f" Sie ERSETZT seine vorherige Reaktion {removed[0]}."
    elif kept:
        wechsel = f" Sie kam ZUSÄTZLICH zu {' '.join(kept)} dazu."
    else:
        wechsel = ""
    prompt = (
        f"[Adam hat auf deine Nachricht mit {emoji} reagiert. Bedeutung laut "
        f"verbindlichem Reaktions-Vokabular: „{entry.meaning}“.{wechsel}"
        + (f" Deine Nachricht war: „{bezug_kurz}“."
           if bezug_kurz else " (Der Wortlaut deiner Nachricht liegt nicht mehr vor.)")
        + (" Das ist die ANTWORT auf deine offene Frage — handle entsprechend."
           if frage is not None else " Reagiere angemessen knapp.")
        + "]"
    )
    _enqueue_reaction_job(user_id, chat_id, rx.message_id, prompt, update.get_bot())


async def _handle_reaction_withdrawal(user_id: int, chat_id: int, message_id: int,
                                      emoji: str, bot_obj, sess) -> None:
    """Adam nimmt eine Reaktion zurück (5.9-Widerruf, 23.07.): Wartet der
    zugehörige Auftrag noch in der Queue → stornieren; lief er schon → bei
    Handlungs-Klassen den Agenten informieren, sonst nur still verbuchen."""
    if sess is not None and sess.logger:
        sess.logger.log_event(f"{emoji} Reaktion von Adam zurückgenommen")
    mb = MAILBOXES.get(user_id)
    if mb is not None:
        for job in list(mb.queue):
            if (job.update is None and job.message_id == message_id
                    and job.text.startswith("[Adam hat")):
                mb.queue.remove(job)
                if job.pending_key:
                    pending.resolve(job.pending_key)
                try:
                    await bot_obj.send_message(
                        chat_id=chat_id,
                        text=f"{emoji} zurückgenommen — der Auftrag dazu ist storniert.",
                        reply_to_message_id=message_id)
                except Exception:
                    log.exception("Widerruf-Quittung nicht zustellbar")
                return
    entry = reactions.lookup(emoji)
    if entry is not None and entry.active:
        _enqueue_reaction_job(
            user_id, chat_id, message_id,
            f"[Adam hat seine Reaktion {emoji} („{entry.meaning}“) auf deine "
            "Nachricht ZURÜCKGENOMMEN — behandle die frühere Reaktions-Antwort "
            "als widerrufen und bestätige das knapp.]", bot_obj)


def _enqueue_reaction_job(user_id: int, chat_id: int, message_id: int,
                          text: str, bot_obj) -> None:
    """Baut aus einer Reaktion einen normalen Queue-Job (ohne Update-Objekt,
    wie die Reconcile-Jobs) — sofort 5.2-persistiert, Antwort als Reply auf
    die reagierte Nachricht."""
    key = f"{chat_id}_r{message_id}_{int(time.time())}"
    job = QueuedJob(
        update=None,
        text=text,
        user_id=user_id,
        chat_id=chat_id,
        message_id=message_id,           # → Antwort zeigt per Reply auf die Nachricht
        pending_key=key,
        bot=bot_obj,
    )
    try:
        pending.record(key, {
            "user_id": user_id, "chat_id": chat_id, "message_id": message_id,
            "text": text, "received_at": job.received_at,
            "message_date": job.received_at,
        })
    except Exception:
        log.exception("Reaktions-Job nicht persistierbar (nicht-fatal)")
    mb = _get_mailbox(user_id)
    mb.queue.append(job)
    _ensure_worker(user_id)


async def on_option_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """5.9: Ziffern-Inline-Knopf an einer nummerierten Liste → Option als
    Antwort in die Queue (Telegram bietet keine Ziffern-Reaktionen)."""
    query = update.callback_query
    user_id = query.from_user.id if query.from_user else None
    if user_id not in ALLOWED_USER_IDS:
        await query.answer()
        return
    try:
        n = int((query.data or "opt:0").split(":", 1)[1])
    except ValueError:
        await query.answer()
        return
    await query.answer(f"Option {n} gewählt")
    msg = query.message
    chat_id = msg.chat_id if msg is not None else user_id
    message_id = msg.message_id if msg is not None else 0
    bezug = ""
    if msg is not None:
        reactions.pop_question(chat_id, message_id)  # Frage gilt als beantwortet
        bezug = _job_preview(msg.text or BOT_MSGS.get((chat_id, message_id), ""), 220)
    prompt = (
        f"[Adam hat per Knopf Option {n} gewählt"
        + (f" — zu deiner Nachricht: „{bezug}“" if bezug else "")
        + ". Führe die gewählte Option aus bzw. antworte entsprechend.]"
    )
    _enqueue_reaction_job(user_id, chat_id, message_id, prompt, query.get_bot())


async def cmd_technik(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """5.25 (d): Werkzeug-Spur zwischen Klartext (Standard) und Rohform umschalten."""
    if not authorized(update):
        return
    user_id = update.effective_user.id
    prefs = _USER_PREFS.setdefault(str(user_id), {})
    prefs["raw_tools"] = not prefs.get("raw_tools", False)
    _save_prefs(_USER_PREFS)
    if prefs["raw_tools"]:
        await update.message.reply_text(
            "🔧 Werkzeug-Spur zeigt jetzt die technische Rohform (Tool-Namen). "
            "Zurück mit /technik.")
    else:
        await update.message.reply_text(
            "💬 Werkzeug-Spur zeigt jetzt Klartext (z. B. 🔎 recherchiere …). "
            "Rohform mit /technik.")


async def cmd_freigaben(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """5.25 (c): dauerhaft gemerkte Always-Allow-Freigaben zeigen / zurücksetzen."""
    if not authorized(update):
        return
    user_id = update.effective_user.id
    prefs = _USER_PREFS.setdefault(str(user_id), {})
    args = (update.message.text or "").split()
    if len(args) > 1 and args[1].lower() in ("reset", "weg", "löschen", "loeschen"):
        prefs.pop("always_allow", None)
        prefs.pop("trusted_domains", None)
        _save_prefs(_USER_PREFS)
        sess = SESSIONS.get(user_id)
        if sess is not None:
            sess.always_allowed_tools.clear()
        await update.message.reply_text(
            "🔒 Alle dauerhaften Freigaben gelöscht (Werkzeuge UND vertraute "
            "Domains) — es wird wieder gefragt.")
        return
    stored = prefs.get("always_allow", [])
    domains = prefs.get("trusted_domains", [])
    lines = []
    if stored:
        lines.append("🔓 Dauerhaft freigegebene Werkzeuge:")
        lines += [f"  • {t}" for t in stored]
    if domains:
        lines.append("🌐 Vertraute Domains (WebFetch fragt dort nie):")
        lines += [f"  • {d}" for d in domains]
    if lines:
        lines.append("\nZurücksetzen mit: /freigaben reset")
        await update.message.reply_text("\n".join(lines))
    else:
        await update.message.reply_text(
            "🔒 Keine dauerhaften Freigaben gespeichert — es wird gefragt "
            "(außer den automatisch erlaubten Lese-Werkzeugen und der "
            "Herkunfts-Schranke bei Recherchen).")


async def cmd_stopp(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """✋ Stopp (5.9): Abbruchsignal per Befehl — bewusst KEIN Reaktions-Emoji,
    weil ein Abbruch eindeutig sein muss (reaktionen-vokabular.md)."""
    if not authorized(update):
        return
    user_id = update.effective_user.id
    mb = MAILBOXES.get(user_id)
    if mb is None or mb.current_job is None:
        await update.message.reply_text("✋ Gerade läuft nichts, das ich stoppen könnte.")
        return
    stopped = _job_preview(mb.current_job.text)
    try:
        sess = SESSIONS.get(user_id)
        if sess is not None:
            await sess.client.interrupt()
        await update.message.reply_text(
            f"✋ Gestoppt: „{stopped}“ — die Aufgabe wird nicht weitergeführt. "
            "Schick sie neu, falls sie doch noch gebraucht wird.")
    except Exception:
        log.exception("Stopp-Interrupt fehlgeschlagen")
        await update.message.reply_text(
            "⚠️ Stopp-Signal gesendet, aber die Aufgabe hat nicht sauber reagiert — "
            "notfalls hilft /reset.")


_PERSONAL_NOTES_FILE = Path.home() / "notes" / "telegram-notes.md"
_PERSONAL_PREFIX = "ich:"


async def on_pinned_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Gepinnte Nachrichten in Memory (für Claude) oder persönliche Notizen speichern.

    Konvention:
      - Kein Präfix  → Claude-Memory (hohe Priorität, wird in jeder Session geladen)
      - 'ich:' Präfix → Nur persönliche Notiz (~/notes/telegram-notes.md)
    """
    if not authorized(update):
        return
    pinned = update.message.pinned_message if update.message else None
    if pinned is None:
        return

    text = (pinned.text or pinned.caption or "").strip()
    if not text:
        await update.message.reply_text("Gepinnte Nachricht hat keinen Text — nichts gespeichert.")
        return

    ts = time.strftime("%Y-%m-%d %H:%M")

    if text.lower().startswith(_PERSONAL_PREFIX):
        # Persönliche Notiz — NICHT in Claude-Memory
        note_text = text[len(_PERSONAL_PREFIX):].strip()
        try:
            _PERSONAL_NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with _PERSONAL_NOTES_FILE.open("a", encoding="utf-8") as f:
                f.write(f"\n- [{ts}] {note_text}\n")
            await update.message.reply_text(
                f"📝 Persönliche Notiz gespeichert:\n\n{note_text}\n\n(Nur für dich, nicht in meiner Memory.)"
            )
        except Exception:
            log.exception("personal note save failed")
            await update.message.reply_text("Fehler beim Speichern der Notiz.")
    else:
        # Claude-Memory — wird in jeder Session geladen
        try:
            mem_file = _MEMORY_DIR / "telegram-pinned.md"
            new_entry = f"\n- [{ts}] {text}\n"
            if mem_file.exists():
                mem_file.open("a", encoding="utf-8").write(new_entry)
            else:
                mem_file.write_text(
                    "---\nname: telegram-pinned\n"
                    "description: Vom User angepinnte Merker und Wichtigkeiten aus dem Telegram-Chat\n"
                    "metadata:\n  type: project\n---\n\n"
                    "Wichtige Merker, die der User im Telegram-Chat angepinnt hat:\n"
                    + new_entry,
                    encoding="utf-8",
                )
                # MEMORY.md-Index aktualisieren
                mem_index = _MEMORY_DIR / "MEMORY.md"
                if mem_index.exists():
                    current = mem_index.read_text(encoding="utf-8")
                    if "telegram-pinned.md" not in current:
                        with mem_index.open("a", encoding="utf-8") as f:
                            f.write("- [Telegram-Merker](telegram-pinned.md) — Vom User angepinnte Wichtigkeiten aus dem Telegram-Chat.\n")
            # Cache invalidieren
            global _MEMORY_CACHE, _MEMORY_MTIME
            _MEMORY_CACHE = None
            _MEMORY_MTIME = 0.0
            await update.message.reply_text(
                "📌 In meiner Memory gespeichert.",
                reply_to_message_id=pinned.message_id,
            )
        except Exception:
            log.exception("memory pin save failed")
            await update.message.reply_text("Fehler beim Speichern in Memory.")


async def on_telegram_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch-all so PTB doesn't drop exceptions silently."""
    log.exception("unhandled handler error: %s", context.error)


# ---------- heartbeat ----------
# Externes Lebenszeichen: alle HEARTBEAT_INTERVAL_S Sekunden schreibt der Bot
# einen Zeitstempel in eine Datei — unabhängig von Telegram-API-Calls. Der
# externe Guardian (guardian.sh) prüft das Alter; ist es zu groß, gilt der Bot
# trotz lebendem Prozess als hängend (Wedge) und wird hart neu gestartet.
# Damit fangen wir die Lücke, die der interne watchdog (siehe unten) bei
# Mac-Schlaf gelegentlich nicht greift, weil er selbst mit im Wedge hängt.
HEARTBEAT_PATH = Path.home() / ".claude" / "bot-heartbeat.txt"
HEARTBEAT_INTERVAL_S = 30


async def heartbeat_writer() -> None:
    """Schreibt regelmäßig einen Zeitstempel in HEARTBEAT_PATH.
    Reine lokale I/O — bleibt auch bei Telegram-API-Wedge funktional."""
    HEARTBEAT_PATH.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            HEARTBEAT_PATH.write_text(
                f"{int(time.time())}\n{time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                encoding="utf-8",
            )
        except Exception:
            log.warning("heartbeat write failed", exc_info=True)
        await asyncio.sleep(HEARTBEAT_INTERVAL_S)


# ---------- watchdog ----------
# Long Mac sleeps occasionally leave python-telegram-bot's getUpdates loop in
# a wedged state — process alive, polling silently dead. We periodically ping
# the Bot API; on repeated failure we exit so launchd restarts us cleanly.

WATCHDOG_INTERVAL_S = 30        # tighter loop to catch wake-from-sleep faster
WATCHDOG_TIMEOUT_S = 15
WATCHDOG_FAIL_THRESHOLD = 2
# If the event loop was paused for longer than this (= macOS sleep), the
# long-poll TCP connection is almost certainly dead even if get_me still
# works on a fresh connection. Force a restart so we re-establish polling.
WATCHDOG_CLOCK_JUMP_S = 90


async def watchdog(app: Application) -> None:
    consecutive_failures = 0
    last_tick = time.monotonic()
    while True:
        await asyncio.sleep(WATCHDOG_INTERVAL_S)
        # 1. Clock-jump detection: asyncio.sleep stops counting during macOS
        # sleep, so a much bigger gap between ticks means the system slept.
        # Telegram's long-poll connection will be stale — easier to restart
        # than to try to fix it in place.
        now = time.monotonic()
        elapsed = now - last_tick
        last_tick = now
        if elapsed > WATCHDOG_CLOCK_JUMP_S:
            log.warning(
                "watchdog: clock jump detected (%.0fs > %ds) — likely system sleep, restarting",
                elapsed, WATCHDOG_CLOCK_JUMP_S,
            )
            os._exit(1)

        # 2. Liveness check on Telegram API.
        try:
            await asyncio.wait_for(app.bot.get_me(), timeout=WATCHDOG_TIMEOUT_S)
            consecutive_failures = 0
        except Exception as e:
            consecutive_failures += 1
            log.warning(
                "watchdog: get_me failed (%d/%d): %s",
                consecutive_failures, WATCHDOG_FAIL_THRESHOLD, e,
            )
            if consecutive_failures >= WATCHDOG_FAIL_THRESHOLD:
                log.error("watchdog tripped — exiting so launchd restarts us")
                os._exit(1)


# ---------- 5.18 Agent-Session-Watchdog ----------
# Der Wächter oben deckt den Fall „Bot-Prozess wedged" ab. Dieser hier den
# selteneren, aber ärgerlicheren: **Bot lebt, die Claude-Session dahinter ist
# tot.** Live vorgeführt am 23.06.2026 ab 16:11 — der Bot war munter, nahm
# Nachrichten an, quittierte sie, und Adam fragte ins Leere, weil hinter der
# Annahme nie wieder etwas passierte. Ohne diesen Wächter merkt das NIEMAND:
# der Job bleibt „in Bearbeitung", der Worker wartet ewig, kein Fehler fällt an.

STALL_CHECK_INTERVAL_S = int(os.environ.get("STALL_CHECK_INTERVAL", "30"))
# Ab wann eine Session als tot gilt. 5 Minuten ohne JEDE Regung — kein Text,
# kein Werkzeug-Aufruf, kein Werkzeug-Ergebnis. Ein normaler Turn, der lange
# arbeitet, meldet sich über die 🔧-Spur ständig; still ist nur eine, die hängt.
STALL_LIMIT_S = int(os.environ.get("STALL_LIMIT", "300"))
# Wie oft eine Nachricht nach einem Stall automatisch neu versucht wird.
# Bewusst 1: hängt es zweimal an derselben Nachricht, liegt es vermutlich an ihr
# — dann ehrlich melden, statt endlos zu wiederholen (kostet jedes Mal
# Abo-Kontingent, s. Kostenregel).
MAX_STALL_RETRIES = int(os.environ.get("MAX_STALL_RETRIES", "1"))


async def _disconnect_quietly(sess: UserSession, user_id: int) -> None:
    """Hängende Session im Hintergrund schließen — mit Zeitlimit.

    WICHTIG: nicht direkt awaiten. `disconnect()` läuft gegen genau den Teil,
    der gerade nicht antwortet; ein blockierendes await würde den Wächter
    mitreißen. Scheitert es, ist das hinnehmbar — die Session ist bereits aus
    SESSIONS entfernt, der Prozess räumt den Rest beim nächsten Neustart auf.
    """
    try:
        await asyncio.wait_for(sess.client.disconnect(), timeout=20)
    except Exception:
        log.warning("Stall: disconnect der hängenden Session (user_id=%s) "
                    "fehlgeschlagen — ignoriert", user_id, exc_info=True)


async def _handle_stalled_session(user_id: int, mb: Mailbox, sess: UserSession | None,
                                  stalled_for: float) -> None:
    """Eine hängende Session beenden, den Job retten, frisch weitermachen.

    LOCKFREI (Kern der Umsetzung): `_run_job` hält die Session-Sperre für die
    gesamte Dauer von Anfrage + Antwortstrom. Wer hier auf sie warten würde,
    wartete bis in alle Ewigkeit — genau auf den Vorgang, der hängt. Der
    Wächter greift deshalb bewusst an der Sperre vorbei; er nimmt der Session
    ihre Zuständigkeit weg (aus SESSIONS raus) und bricht den Worker-Task ab.
    """
    job = mb.current_job
    bot = (job.bot if job is not None and job.bot is not None else None) \
        or (sess.bot if sess is not None else None)
    chat_id = (job.chat_id if job is not None else None) \
        or (sess.chat_id if sess is not None else None)
    # Dauer in ganzen Worten: unter 2 Minuten in Sekunden (bei einem 60-s-Limit
    # las sich „1 Minuten" sonst falsch UND ungenau — live gesehen 20.07.).
    dauer = (f"{int(stalled_for)} Sekunden" if stalled_for < 120
             else f"{int(stalled_for // 60)} Minuten")
    log.error("Stall erkannt: user_id=%s ohne Regung seit %.0fs (Session %s) — wird beendet",
              user_id, stalled_for, "vorhanden" if sess is not None else "nie zustande gekommen")

    # 1. Session sofort entmachten, damit nichts Neues mehr daran andockt.
    # sess kann None sein: dann hängt bereits der SESSION-AUFBAU (`ensure_session`
    # kehrt nie zurück, das Objekt existiert also noch gar nicht). Für Adam ist
    # das derselbe Fall — er fragt ins Leere —, nur gibt es hier nichts zu
    # schließen. Aufgefallen beim Vorbereiten des VPS-Tests am 20.07.
    if sess is not None:
        SESSIONS.pop(user_id, None)
        try:
            cancel_pending_permissions(sess, reason="Session-Stall (5.18)")
        except Exception:
            log.exception("Stall: Permissions-Aufräumen fehlgeschlagen (nicht-fatal)")
        asyncio.create_task(_disconnect_quietly(sess, user_id))

    # 2. Worker-Task abbrechen. Er hängt im await auf die tote Session; ein
    # cancel() löst dort CancelledError aus und beendet ihn. Reagiert er auch
    # darauf nicht, wird NICHT neu eingereiht — sonst liefe der alte Task
    # womöglich später doch noch los und Adam bekäme die Antwort doppelt.
    worker_dead = True
    task = mb.worker
    if task is not None and not task.done():
        task.cancel()
        # Bewusst asyncio.wait statt await/wait_for: es wirft weder die
        # CancelledError des Workers noch dessen Fehler an DIESE Schleife
        # weiter — der Wächter darf an einem sterbenden Task nicht mitsterben.
        try:
            await asyncio.wait([task], timeout=10)
        except Exception:
            log.exception("Stall: Warten auf Worker-Ende fehlgeschlagen")
        worker_dead = task.done()
    mb.worker = None
    mb.current_job = None
    mb.current_started = 0.0

    # 3. Die unbeantwortete Nachricht retten.
    retry = False
    if job is not None and worker_dead:
        job.stall_retries += 1
        if job.stall_retries <= MAX_STALL_RETRIES:
            job.resumed = True          # Prompt-Vermerk „nachgeholt nach Unterbrechung"
            mb.queue.appendleft(job)    # als Nächstes, mit frischer Session
            retry = True
            if job.pending_key:
                pending.set_status(job.pending_key, pending.STATUS_OPEN)
        elif job.pending_key:
            # Aufgegeben — Record auflösen, sonst meldet ihn der Startup-Reconcile
            # bei jedem künftigen Start erneut.
            pending.resolve(job.pending_key)

    # 4. Adam aktiv informieren. Schweigen wäre hier das Schlimmste: genau das
    # „ins Leere fragen" soll dieser Punkt ja abschaffen.
    if bot is not None and chat_id is not None:
        preview = _job_preview(job.text) if job is not None else ""
        msg = (f"⚠️ Meine Claude-Sitzung hat {dauer} lang nicht mehr reagiert. "
               "Ich habe sie beendet und starte eine frische."
               if sess is not None else
               f"⚠️ Meine Claude-Sitzung ließ sich seit {dauer} nicht einmal "
               "starten. Ich breche den Versuch ab und probiere es frisch.")
        if job is not None:
            msg += f"\n\nBetroffen war: „{preview}“"
            if retry:
                msg += "\n→ Ich nehme sie automatisch nochmal dran."
            elif not worker_dead:
                msg += ("\n→ Der alte Vorgang ließ sich nicht sauber stoppen. Ich hole die "
                        "Nachricht NICHT automatisch nach (sonst käme die Antwort womöglich "
                        "doppelt) — bitte schick sie nochmal, falls nichts mehr kommt.")
            else:
                msg += (f"\n→ Das war schon der {job.stall_retries}. Anlauf. Ich wiederhole sie "
                        "nicht weiter — bitte anders formuliert oder in kleineren Teilen "
                        "nochmal schicken.")
        try:
            await bot.send_message(chat_id, msg)
        except Exception:
            log.exception("Stall: Meldung an Adam konnte nicht gesendet werden")
    else:
        log.error("Stall: keine Sendemöglichkeit (bot=%s, chat_id=%s) — Meldung entfällt",
                  bot is not None, chat_id)

    # 5. Frisch weiterarbeiten. `ensure_session` legt beim nächsten Job eine neue
    # Session an, weil SESSIONS für diesen User jetzt leer ist.
    if mb.queue:
        _ensure_worker(user_id)


async def stall_watchdog(app: Application) -> None:
    """Prüfschleife: läuft ein Job zu lange ohne jede Regung der Claude-Session?"""
    while True:
        await asyncio.sleep(STALL_CHECK_INTERVAL_S)
        try:
            now = time.monotonic()
            for user_id, mb in list(MAILBOXES.items()):
                if mb.current_job is None:
                    continue
                sess = SESSIONS.get(user_id)
                # sess None = der Session-AUFBAU hängt (ensure_session kehrt nie
                # zurück). Früher wurde hier abgebrochen — genau das war eine
                # Lücke: ein Job, dessen Sitzung sich nie öffnen lässt, läuft
                # dann unbegrenzt weiter und Adam fragt ins Leere. Ein Aufbau
                # dauert normal 1–3 Sekunden; Minuten ohne Session sind kaputt.
                if sess is not None and sess.pending_permissions:
                    # Wartet der Vorgang auf eine Freigabe von Adam, ist Stille
                    # GEWOLLT — er darf sich Zeit lassen, ohne dass ihm der
                    # Wächter die Sitzung unter dem Stuhl wegzieht.
                    continue
                # Job-Beginn zählt als Regung: sonst schlüge der Wächter bei
                # einem Turn zu, der noch nie etwas geliefert hat, weil
                # last_activity dann von der Vorgänger-Nachricht stammt.
                ref = (mb.current_started if sess is None
                       else max(mb.current_started, sess.last_activity))
                stalled_for = now - ref
                if stalled_for > STALL_LIMIT_S:
                    await _handle_stalled_session(user_id, mb, sess, stalled_for)
        except Exception:
            # Ein Fehler hier darf die Schleife nie beenden — sonst wäre der
            # Wächter still weg und niemand merkte es (dieselbe Klasse Fehler,
            # gegen die er schützen soll).
            log.exception("Stall-Wächter: Durchlauf fehlgeschlagen (Schleife läuft weiter)")


def _detect_pending_item(full: bool = False) -> str:
    """Analysiert die letzten Telegram-Logs und erkennt offene Punkte.
    Zwei Fälle:
      Fall B: Adams letzte Nachricht vor dem Neustart hat keine Claude-Antwort bekommen
              → höchste Priorität, direkt aufgreifen.
      Fall A: Claude hatte eine offene Frage/Test gestellt, Adam hat noch nicht reagiert.
    full=False: kurze Beschreibung für Startup-Meldung.
    full=True:  Prompt-Text für autorun (Bot beantwortet/führt weiter).
    Gibt '' zurück wenn nichts offen ist."""
    import re as _re
    from datetime import date, timedelta

    today = date.today()
    all_lines: list[str] = []
    for d in [today - timedelta(days=1), today]:
        f = LOG_DIR / f"{d.isoformat()}.md"
        if f.exists():
            all_lines.extend(f.read_text(encoding="utf-8").splitlines())

    if not all_lines:
        return ""

    recent = all_lines[-300:]
    session_positions = [i for i, l in enumerate(recent) if l.startswith("## Session")]
    if len(session_positions) < 2:
        return ""

    boundary = session_positions[-1]

    # Alle Blöcke vor dem letzten Neustart durchlaufen;
    # letzten User-Block UND letzten Claude-Block festhalten + wer zuletzt dran war.
    in_claude = False
    in_user = False
    current_block: list[str] = []
    last_claude_block: list[str] = []
    last_user_block: list[str] = []
    last_author: str = ""  # "claude" | "user"

    for line in recent[:boundary]:
        if line.startswith("## Claude"):
            if in_user:
                last_user_block = current_block[:]
            in_user = False
            in_claude = True
            current_block = []
        elif line.startswith("## Du"):
            if in_claude:
                last_claude_block = current_block[:]
            in_claude = False
            in_user = True
            current_block = []
        elif line.startswith("## Session"):
            if in_claude:
                last_claude_block = current_block[:]
            elif in_user:
                last_user_block = current_block[:]
            in_claude = False
            in_user = False
        elif in_claude:
            current_block.append(line)
        elif in_user:
            current_block.append(line)

    if in_claude:
        last_claude_block = current_block[:]
        last_author = "claude"
    elif in_user:
        last_user_block = current_block[:]
        last_author = "user"
    elif last_user_block and last_claude_block:
        # Beide vorhanden, aber beide abgeschlossen (letzte Zeile war leer/Trenner)
        # Prüfe welcher zuletzt erschien: letztes ## Du vs ## Claude
        last_du = max((i for i, l in enumerate(recent[:boundary]) if l.startswith("## Du")), default=-1)
        last_cl = max((i for i, l in enumerate(recent[:boundary]) if l.startswith("## Claude")), default=-1)
        last_author = "user" if last_du > last_cl else "claude"

    # (Die Helfer `_clean_user_text` / `_first_meaningful` sind mit Fall B
    # entfallen — sie hatten keinen anderen Aufrufer. Historie in Git.)

    # ── Fall B: ABGESCHALTET seit 20.07.2026 — 5.2 macht das jetzt exakt ──
    #
    # Fall B riet aus dem Chat-Log („wer war zuletzt dran?"), ob Adams letzte
    # Nachricht unbeantwortet blieb, und ließ sie per Autorun neu beantworten.
    # Das war vor 5.2 die einzige Rettung — jetzt ist es ein ZWEITER, blinder
    # Nachhol-Mechanismus neben `_reconcile_pending`, der nichts von den
    # Persistenz-Records weiß und deshalb keine Ahnung hat, was bereits
    # beantwortet wurde.
    #
    # Live schiefgegangen am 20.07.: Nach dem Kill-Test lag eine „## Session"-
    # Grenze im Log, dadurch sah die längst beantwortete Brot-Frage wie der
    # letzte unbeantwortete User-Block aus — der Bot beantwortete sie beim
    # nächsten Neustart ein zweites Mal. Das unterläuft genau die Zusage von
    # 5.2 („jede Nachricht genau einmal") und kostet zusätzlich eine Anfrage.
    #
    # Die exakte Antwort auf „ist das noch offen?" steht in `logs/pending/`:
    # Record vorhanden = offen, gelöscht = beantwortet. Raten ist überflüssig.
    # Fall A unten bleibt — der deckt den ANDEREN Fall ab (Claude wartet auf
    # Adam), den 5.2 nicht kennt und auch nicht abdecken soll.

    # ── Fall A: Claude hatte Frage/Test gestellt, Adam hat noch nicht reagiert ──
    if last_author == "claude" and last_claude_block:
        last_text = "\n".join(last_claude_block).strip()
        msg_lower = last_text.lower()

        open_signals = [
            "schick mir", "schick etwas", "schick jetzt", "schick die",
            "probier", "bereit zum testen", "test 1", "test 2",
            "wofür möchtest du", "was ist dir wichtiger",
            "a oder b", "sag a oder b", "kannst du dir vorstellen",
            "willst du das so", "sollen wir", "magst du",
            "kommt dann sofort", "bin gespannt",
            "sobald du", "wenn du bereit", "sag bescheid",
        ]

        for signal in open_signals:
            if signal in msg_lower:
                if full:
                    return last_text[:800]
                meaningful = [
                    _re.sub(r"[*_`#>]", "", l).strip()
                    for l in last_text.splitlines()
                    if _re.sub(r"[*_`#>]", "", l).strip()
                    and not l.strip().startswith(("🔧", "*🔧", "##"))
                ]
                if meaningful:
                    s = meaningful[0]
                    return (s[:100] + "…") if len(s) > 100 else s
                break

    return ""


def _read_pending_items() -> list[str]:
    """Liest offene [ ]-Punkte aus pending-items.md (Memory). Terminierte Sektionen werden übersprungen."""
    pf = _MEMORY_DIR / "pending-items.md"
    if not pf.exists():
        return []
    items: list[str] = []
    in_terminated = False
    for line in pf.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_terminated = "terminiert" in stripped.lower() or "verschoben" in stripped.lower()
        if in_terminated:
            continue
        if stripped.startswith("- [ ]"):
            text = stripped[5:].strip()
            # Markdown-Fettdruck entfernen
            text = text.replace("**", "")
            if text:
                items.append(text)
    return items


def _startup_message_from_last_task() -> str:
    """Begrüßung aus last-task.md. Der YAML-Frontmatter wird KOMPLETT übersprungen,
    damit technische Kopfzeilen (node_type, type, ...) nie in der Nachricht landen."""
    import re
    last_task_file = _MEMORY_DIR / "last-task.md"
    if not last_task_file.exists():
        return "Bin wieder da, Adam."
    raw = last_task_file.read_text(encoding="utf-8")
    body = raw
    if raw.lstrip().startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            body = parts[2]
    summary = ""
    for line in body.splitlines():
        s = re.sub(r"[*_`#>]", "", line).strip()
        if s:
            summary = s
            break

    # Explizite Pending-Items aus Memory (höchste Priorität, vor log-basiertem Check)
    pending_list = _read_pending_items()
    if pending_list:
        items_text = "\n".join(f"· {it}" for it in pending_list[:3])
        suffix = f" (+ {len(pending_list) - 3} weitere)" if len(pending_list) > 3 else ""
        return f"Bin wieder da, Adam. Noch offen:\n{items_text}{suffix}"

    # Chat-Check: Lag in der letzten Session noch etwas offen?
    pending = _detect_pending_item()
    if pending:
        return f"Bin wieder da, Adam — da war noch was offen: {pending}"

    return f"Bin wieder da, Adam. Letzter Stand: {summary}" if summary else "Bin wieder da, Adam."


def run_self_check() -> tuple[bool, list[str]]:
    """Smoke-Test der Kern-Invarianten. Läuft bei jedem Start und via /selfcheck.
    Prüft, ob bestehende Funktionen weiter korrekt arbeiten (Regressionsschutz).
    Gibt (alles_ok, zeilen) zurück; jede Zeile beginnt mit '✓' oder '✗'."""
    results: list[str] = []
    state = {"ok": True}

    def check(name: str, fn) -> None:
        try:
            fn()
            results.append(f"✓ {name}")
        except Exception as e:
            state["ok"] = False
            results.append(f"✗ {name}: {e}")

    # 1. Begrüßung sauber — keine technischen Frontmatter-Reste (der Bug von 2026-06-16)
    def _c_startup() -> None:
        msg = _startup_message_from_last_task()
        for bad in ("node_type", "originSessionId", "metadata:", "name:", "description:"):
            assert bad not in msg, f"enthält '{bad}'"
        assert not msg.lstrip().startswith("---"), "beginnt mit Frontmatter"
    check("Begrüßung sauber", _c_startup)

    # 1b. Pending-Items-Leser — muss ohne Fehler laufen, egal ob Datei existiert
    def _c_pending() -> None:
        items = _read_pending_items()
        assert isinstance(items, list), "kein List zurückgegeben"
        for it in items:
            assert "[ ]" not in it, "Checkbox-Syntax blieb im Text"
            assert "**" not in it, "Markdown-Fettdruck blieb"
    check("Pending-Items-Leser", _c_pending)

    # 2. TTS-Cleanup — Emoji/Markdown raus, normale Satzzeichen bleiben
    def _c_tts() -> None:
        out = _strip_markdown_for_tts("## Titel\n**Hallo** 🚀 Welt! Test → ok")
        assert "🚀" not in out, "Emoji blieb"
        assert "*" not in out and "#" not in out, "Markdown blieb"
        assert "!" in out, "Satzzeichen verloren"
        # Markdown-Links: URL UND Label raus (Quellen-Labels stören Sprachfluss)
        link = _strip_markdown_for_tts("Siehe [heise online](https://www.heise.de/news/x-123) dazu")
        assert "http" not in link and "heise.de" not in link, "URL blieb"
        assert "heise online" not in link, "Link-Label wurde nicht entfernt"
        assert "Siehe" in link and "dazu" in link, "umgebender Text verloren"
        assert "http" not in _strip_markdown_for_tts("Quelle: https://example.com/a/b/c?d=1"), "nackte URL blieb"
        # Wikilinks (interne Memory-Verweise) raus, Slug nicht vorlesen
        wiki = _strip_markdown_for_tts("Mehr in [[telegram-bot-project]] beschrieben")
        assert "[[" not in wiki and "]]" not in wiki, "Wikilink-Klammern blieben"
        assert "telegram-bot-project" not in wiki, "Wikilink-Slug vorgelesen"
        assert "Mehr in" in wiki and "beschrieben" in wiki, "Wikilink-Umfeld verloren"
        # Nummerierte Listen als hörbare Aufzählung ("1." → "Erstens")
        lst = _strip_markdown_for_tts("1. Punkt eins\n2. Punkt zwei\n3. Punkt drei")
        assert "Erstens" in lst, "1. nicht als Erstens gesprochen"
        assert "Zweitens" in lst, "2. nicht als Zweitens gesprochen"
        assert "Drittens" in lst, "3. nicht als Drittens gesprochen"
        # Gesperrt gesetzte Wörter (Klein-/Gemischtschreibung) als Wort vorlesen
        assert "Vorbereitung" in _strip_markdown_for_tts("V o r b e r e i t u n g des Spiels"), "Sperrschrift nicht erkannt"
        assert "HUMAN" in _strip_markdown_for_tts("H U M A N Design"), "Großbuchstaben-Sperrung verloren"
        # Kurze Aufzählung (nur 2-3 Buchstaben) bleibt unangetastet
        assert _strip_markdown_for_tts("Plan a b c") == "Plan a b c", "kurze Folge fälschlich zusammengefügt"
        # Abkürzungen werden für die Sprachausgabe ausgeschrieben
        abk = _strip_markdown_for_tts("Das gilt bzw. ggf. usw., z. B. hier u. a.")
        for raw in ("bzw.", "ggf.", "usw.", "z. B.", "z.B.", "u. a."):
            assert raw not in abk, f"Abkürzung '{raw}' blieb stehen"
        assert "beziehungsweise" in abk and "zum Beispiel" in abk, "Abkürzung nicht ausgeschrieben"
        # Einzelne Zeilenumbrüche dürfen kein Satzende erzeugen (edge-tts sonst:
        # Stimme sinkt an jedem Zeilenende). Umbruch im Satz → Leerzeichen.
        nl = _strip_markdown_for_tts("Das ist ein Satz\nder einfach weitergeht.")
        assert "\n" not in nl, "Einzel-Umbruch blieb erhalten"
        assert "Satz der einfach" in nl, "Umbruch nicht zu Leerzeichen geglättet"
        # Echte Absätze (Leerzeile) bleiben als Pause erhalten
        para = _strip_markdown_for_tts("Erster Absatz.\n\nZweiter Absatz.")
        assert "\n\n" in para, "Absatz-Pause verloren"
        # Zahlen-Bindestrich: kleinere vorn → 'bis', größere vorn → 'minus',
        # Sport-Kontext → 'zu'. Nie 'Komma'. Em-Dash bleibt unverändert.
        nr = _normalize_number_ranges
        # Bereich
        assert nr("2-3 Tage") == "2 bis 3 Tage", "Bereich '2-3' nicht 'bis'"
        assert nr("5–10 Minuten") == "5 bis 10 Minuten", "En-Dash-Bereich verloren"
        # Rechnung
        assert nr("Berechnung: 10-5 ergibt 5.") == "Berechnung: 10 minus 5 ergibt 5.", \
            "Mathe nicht 'minus'"
        assert nr("3-2 ohne Kontext") == "3 minus 2 ohne Kontext", \
            "Rückwärts-Paar nicht 'minus'"
        # Sport-Kontext → 'zu'
        assert nr("Endstand 3-1 für uns.") == "Endstand 3 zu 1 für uns.", \
            "Sport-Score nicht 'zu'"
        assert nr("Bayern siegt 4-2 gegen Köln.") == "Bayern siegt 4 zu 2 gegen Köln.", \
            "Sieg nicht 'zu'"
        assert nr("Halbzeit 1-1.") == "Halbzeit 1 zu 1.", "Halbzeit nicht 'zu'"
        # Jahreszahlen NICHT als Sport lesen, selbst wenn Sport-Wort im Satz
        assert nr("Saison 2022-2023") == "Saison 2022 bis 2023", \
            "Jahres-Range fälschlich 'zu'"
        # Em-Dash bleibt unverändert (kein Operator-Charakter im Alltag)
        assert nr("Plan 10—5") == "Plan 10—5", "Em-Dash sollte unverändert bleiben"
        # End-to-End: kein 'Komma' und nicht 'minus' bei Sport
        endstand = _strip_markdown_for_tts("Endstand 3-1.")
        assert "Komma" not in endstand and " zu " in endstand, \
            "Sport-Score landete falsch"
        # Versionsnummern: 'Python 3.12' → '3 Punkt 12' (sonst liest TTS '3 Uhr 12').
        nv = _normalize_versions
        assert nv("Python 3.12 installieren") == "Python 3 Punkt 12 installieren", \
            "Versionsnummer nicht entschärft"
        assert nv("macOS 14.5 ist da") == "macOS 14 Punkt 5 ist da", \
            "macOS-Version nicht entschärft"
        # Datum (drei Zahlenblöcke) NICHT anfassen
        assert nv("am 22.06.2026 abends") == "am 22.06.2026 abends", \
            "Datum fälschlich umgeschrieben"
        # Uhrzeit-Indikator: bleibt stehen, damit TTS '3.12 Uhr' als Zeit liest
        assert nv("um 3.12 Uhr") == "um 3.12 Uhr", \
            "Uhrzeit mit 'Uhr' fälschlich umgeschrieben"
    check("TTS-Cleanup", _c_tts)

    # 3. Neustart-Meldung — natürliche Sprache, keine technischen Labels
    def _c_restart() -> None:
        uid = next(iter(ALLOWED_USER_IDS), 0)
        msg = _build_restart_reason(uid)
        for bad in ("node_type", "metadata:", "originSessionId"):
            assert bad not in msg, f"enthält '{bad}'"
    check("Neustart-Meldung sauber", _c_restart)

    # 4. Ausgabekanal-Routing — liefert 3-Tupel ohne Crash
    def _c_channel() -> None:
        r = get_output_channel()
        assert isinstance(r, tuple) and len(r) == 3, "kein 3-Tupel"
    check("Ausgabekanal-Routing", _c_channel)

    # 4b. Phase-6-Kanalstruktur (6.5/6.1): Häuser vollständig, Routing ohne
    # Falsch-Fallback, Auflösung greift erst bei angelegtem Zimmer.
    def _c_houses() -> None:
        assert set(channels.HOUSES) == {
            "werkstatt", "nirgendhaus", "handelshaus", "bibliothek"}, "Haus-Set falsch"
        total = sum(len(h["zimmer"]) for h in channels.HOUSES.values())
        assert total == 13, f"erwartet 13 Zimmer, sind {total}"
        # Erkennung tolerant, Bestand ausgenommen
        assert channels.detect_house("🔧 Werkstatt") == "werkstatt"
        assert channels.detect_house("Jakuna-San") is None
        # Routing erfindet nie ein Ziel
        assert channels.resolve_route({}, "research") is None
        assert route_target("research") is None or isinstance(route_target("research"), tuple)
    check("Phase-6-Kanalstruktur (6.5/6.1)", _c_houses)

    # 5. Memory erreichbar + ladbar
    def _c_memory() -> None:
        assert (_MEMORY_DIR / "MEMORY.md").exists(), "MEMORY.md fehlt"
        assert load_user_memory().strip(), "Memory leer"
    check("Memory erreichbar", _c_memory)

    # 6. Modell-Persistenz — Default gesetzt + Prefs ladbar
    def _c_model() -> None:
        assert DEFAULT_MODEL, "DEFAULT_MODEL leer"
        assert isinstance(_load_prefs(), dict), "Prefs nicht ladbar"
    check("Modell-Persistenz", _c_model)

    # 7. Nachrichten-Erhalt bei Neustart — Updates aus der Ausfallzeit dürfen
    # NICHT verworfen werden (sonst gehen Sprachnachrichten unbemerkt verloren).
    def _c_no_drop() -> None:
        assert DROP_PENDING_UPDATES is False, \
            "verwirft Nachrichten bei Neustart — Sprachnachrichten gehen verloren"
    check("Nachrichten-Erhalt bei Neustart", _c_no_drop)

    # 8. Session-Recall — jüngster Gesprächsverlauf wird der neuen Session
    # mitgegeben, damit nach einem Neustart nahtlos angeknüpft wird.
    def _c_recall() -> None:
        rec = _recent_conversation_recall()
        assert isinstance(rec, str), "Recall kein String"
        ctx = _session_context("MEMORY-PLATZHALTER")
        assert "MEMORY-PLATZHALTER" in ctx, "Memory ging im Kontext verloren"
        if rec:
            assert "LETZTER GESPRÄCHSVERLAUF" in ctx, "Recall-Block fehlt im Kontext"
    check("Session-Recall", _c_recall)

    # 9. Nachrichten-Persistenz (5.2) — record→set_status→resolve muss atomar
    # durchlaufen und darf keine Leiche hinterlassen. Test auf einem Wegwerf-
    # Schlüssel, der garantiert nicht mit echten Nachrichten kollidiert.
    def _c_pending_persist() -> None:
        k = pending.make_key(-1, -1)  # unmöglicher chat/message-Wert
        try:
            pending.record(k, {"text": "selfcheck", "status": pending.STATUS_OPEN})
            assert any(r.get("_key") == k for r in pending.load_all()), "Record nicht geschrieben"
            pending.set_status(k, pending.STATUS_RUNNING)
            hit = next((r for r in pending.load_all() if r.get("_key") == k), None)
            assert hit and hit.get("status") == pending.STATUS_RUNNING, "Status nicht gesetzt"
        finally:
            pending.resolve(k)
        assert not any(r.get("_key") == k for r in pending.load_all()), "Record nicht gelöscht"
    check("Nachrichten-Persistenz (5.2)", _c_pending_persist)

    # 10. Wiederaufgreif-Pfad (5.2 Schritt 2) — ein Job muss OHNE lebendes
    # telegram.Update baubar sein, sonst kann nach einem Neustart nichts
    # nachgeholt werden. Plus: die Schleifen-Bremse darf nicht abgeschaltet sein.
    def _c_resume_path() -> None:
        j = QueuedJob(update=None, text="x", user_id=1, chat_id=2, message_id=3,
                      message_date=1.0, resumed=True)
        assert j.update is None and j.chat_id == 2 and j.resumed, "Job ohne Update unbrauchbar"
        assert _MAX_RESUME_ATTEMPTS >= 1, "Schleifen-Bremse abgeschaltet"
        k = pending.make_key(-2, -2)  # Wegwerf-Schlüssel, kollidiert nie mit echten
        try:
            pending.record(k, {"text": "x", "status": pending.STATUS_OPEN})
            assert pending.bump_attempts(k) == 1 and pending.bump_attempts(k) == 2, \
                "Versuchszähler zählt nicht"
        finally:
            pending.resolve(k)
    check("Wiederaufgreif-Pfad (5.2)", _c_resume_path)

    # 11. Zustellnachweis — der zentrale Sendepfad MUSS melden, ob wirklich etwas
    # ankam. Fällt er auf „gibt nichts zurück" zurück, hält `_run_job` jeden
    # Sendefehler wieder für Erfolg und hakt die Nachricht ab (Verlust vom 19.07.).
    def _c_delivery_proof() -> None:
        import inspect
        sig = inspect.signature(send_answer_to_user)
        # Die Datei nutzt `from __future__ import annotations` → Annotationen sind
        # Strings, nicht Typ-Objekte. Beides zulassen, sonst schlägt der Check
        # fehl, obwohl der Code stimmt.
        assert sig.return_annotation in (bool, "bool"), \
            "send_answer_to_user liefert keinen Zustellnachweis (bool) mehr"
        src = inspect.getsource(send_answer_to_user)
        assert "delivered" in src and "send_chunked" in src, \
            "Text-Fallback bei TTS-Ausfall fehlt"
        # Die Sendemarke entscheidet, ob eine unterbrochene Nachricht automatisch
        # nachgeholt werden darf. Fehlt sie, landet wieder ALLES Angefangene im
        # „nur melden"-Topf — auch das, was gefahrlos wiederholbar wäre.
        assert "STATUS_SENDING" in inspect.getsource(_run_job), \
            "Sendemarke fehlt — unterbrochene Nachrichten würden unnötig liegenbleiben"
        assert pending.STATUS_SENDING != pending.STATUS_RUNNING, "Status nicht unterscheidbar"
    check("Zustellnachweis + TTS-Fallback", _c_delivery_proof)

    # 12. Session-Wächter (5.18) — greift nur, wenn ALLE drei Teile stehen:
    # das Lebenszeichen im Antwortstrom, die Prüfschleife, und ihr Start.
    # Fehlt eines davon, ist der Wächter still weg — und genau die Stille ist
    # der Fehler, gegen den er schützt (23.06.: Bot lebt, Session tot).
    def _c_stall_watchdog() -> None:
        import inspect
        assert "last_activity" in inspect.getsource(stream_response), \
            "Lebenszeichen im Antwortstrom fehlt — Wächter würde blind zuschlagen"
        assert "last_activity" in UserSession.__dataclass_fields__, "Feld last_activity fehlt"
        src = inspect.getsource(_handle_stalled_session)
        assert "async with sess.lock" not in src, \
            "Wächter wartet auf die Sperre — genau die hält der hängende Vorgang"
        assert "SESSIONS.pop" in src and "cancel()" in src, \
            "hängende Session wird nicht wirklich beendet"
        assert "stall_watchdog" in inspect.getsource(post_init), \
            "Prüfschleife wird beim Start nicht angeworfen"
        assert STALL_LIMIT_S >= 60 and STALL_CHECK_INTERVAL_S >= 5, "Limits unplausibel"
        assert MAX_STALL_RETRIES >= 0, "Wiederholungsbremse unplausibel"
    check("Session-Wächter (5.18)", _c_stall_watchdog)

    # 13. Voice-Eingangsschutz (Befund 20.07.). Die Sprachnachricht muss VOR
    # Download und Transkription festgehalten werden — sonst klafft wieder das
    # 25-Sekunden-Loch, in dem ein Neustart sie spurlos verschluckt. Und der
    # Platzhalter darf niemals nachgeholt werden, sonst legt der Reconcile
    # Claude eine leere Hülle statt Adams Anliegen vor.
    def _c_voice_entry_guard() -> None:
        import inspect
        src = inspect.getsource(on_voice)
        assert "pending.record" in src, "Sprachnachricht wird beim Eingang nicht gesichert"
        i_rec, i_dl = src.index("pending.record"), src.index("_download_tg_file")
        assert i_rec < i_dl, "Sicherung liegt hinter dem Download — Lücke wieder offen"
        assert src.count("_resolve_voice_stage") >= 4, \
            "nicht jeder Abbruchzweig räumt den Eingangs-Eintrag ab"
        rec_src = inspect.getsource(_reconcile_pending)
        assert "VOICE_STAGE" in rec_src, "Reconcile erkennt den Platzhalter nicht"
        assert VOICE_STAGE_PLACEHOLDER.startswith("["), "Platzhalter nicht als solcher erkennbar"
        assert hasattr(pending, "merge"), "pending.merge fehlt — Audio-Pfad nicht nachtragbar"
    check("Voice-Eingangsschutz (5.2)", _c_voice_entry_guard)

    # 15. Emoji-Reaktionen (5.9) — Vokabular v2.1 vollständig, VS16-normalisiert,
    # Registratur-Roundtrip funktioniert, Optionslisten werden erkannt.
    def _c_reactions() -> None:
        # Jede v2.1-Bedeutungsgruppe muss erreichbar sein (kein stilles Schrumpfen).
        for e, kind in [("👍", "ja"), ("👎", "nein"), ("🫡", "ja"), ("🤔", "unsicher"),
                        ("🤨", "unklar"), ("🤷", "unklar"), ("🔥", "los"), ("⚡", "los"),
                        ("👀", "anschauen"), ("🏆", "merken"), ("😴", "spaeter"),
                        ("💯", "genau"), ("❤️", "dank"), ("🍓", "dank"), ("🍌", "dank")]:
            entry = reactions.lookup(e)
            assert entry is not None and entry.kind == kind, f"{e} → {kind} fehlt/falsch"
        # VS16-Normalisierung: beide Formen treffen denselben Eintrag.
        assert reactions.lookup("❤") is reactions.lookup("❤️"), "VS16-Normalisierung kaputt"
        assert reactions.lookup("✍") is not None and reactions.lookup("🤷‍♂") is not None
        # Wertschätzung bleibt still (kein Kontingent-Verbrauch ohne Frage).
        assert not reactions.lookup("💯").active and reactions.lookup("👍").active
        # Registratur-Roundtrip (persistent, atomar).
        reactions.register_question(0, 999999, "Selbstcheck-Frage — passt das so?")
        q = reactions.pop_question(0, 999999)
        assert q and "Selbstcheck" in q["text"], "Registratur-Roundtrip kaputt"
        assert reactions.pop_question(0, 999999) is None, "Frage nicht ausgetragen"
        # Optionslisten-Erkennung (1️⃣–9️⃣-Knöpfe).
        assert reactions.detect_numbered_options("1. A\n2. B\nWelche?") == 2
        assert reactions.detect_numbered_options("Fließtext ohne Liste") == 0
        # Der Handler ist als Reply-Antwort verdrahtet (Registratur am Sendepfad).
        import inspect as _insp
        src = _insp.getsource(send_answer_to_user)
        assert "register_question" in src, "Sendepfad registriert keine Fragen"
    check("Emoji-Reaktionen (5.9)", _c_reactions)

    # 15b. Tastatur-Vollständigkeit — JEDER Knopf, den _main_keyboard rendern
    # kann, MUSS in _ALL_KEYBOARD_BTNS stehen (sonst geht der Druck als normale
    # Nachricht an den Agenten — live passiert am 23.07. mit dem STT-Knopf) und
    # jeder STT-Knopf zusätzlich in _STT_BTN_TARGET.
    def _c_keyboard_complete() -> None:
        global _ACTIVE_STT
        saved_models, saved_active = dict(_STT_MODELS), _ACTIVE_STT
        try:
            _STT_MODELS.clear()
            _STT_MODELS.update({"small": "x", "medium": "y"})
            for active in ("small", "medium"):
                _ACTIVE_STT = active
                for model in ("haiku", "sonnet", "opus", "fable"):
                    for effort in (None, "low", "max"):
                        for row in _main_keyboard(False, model, effort).keyboard:
                            for btn in row:
                                assert btn.text in _ALL_KEYBOARD_BTNS, \
                                    f"Knopf „{btn.text}“ fehlt in _ALL_KEYBOARD_BTNS"
                                if btn.text.startswith("🎙️"):
                                    assert btn.text in _STT_BTN_TARGET, \
                                        f"STT-Knopf „{btn.text}“ fehlt in _STT_BTN_TARGET"
        finally:
            _STT_MODELS.clear()
            _STT_MODELS.update(saved_models)
            _ACTIVE_STT = saved_active
    check("Tastatur-Vollständigkeit", _c_keyboard_complete)

    # 16. Reibungslose Recherche (5.25) — Herkunfts-Schranke + Geheimnis-Schutz.
    def _c_research() -> None:
        # Host-Extraktion (Grundlage der Herkunfts-Schranke).
        hosts = _extract_hosts("Schau mal auf https://www.kicker.de/artikel und http://fc.de/x")
        assert hosts == {"kicker.de", "fc.de"}, f"Host-Extraktion falsch: {hosts}"
        assert _url_host("https://www.heise.de/news/1.html") == "heise.de"
        # SCHEMALOSE Adressen — so schreiben Menschen (Live-Fund Test 6, 23.07.):
        bare = _extract_hosts("Ruf de.wikipedia.org/wiki/1._FC_Köln ab, dann (fc.de).")
        assert {"de.wikipedia.org", "fc.de"} <= bare, f"schemalose Domains fehlen: {bare}"
        assert _extract_hosts("Punkt 5.9 gilt, Version 2.7 auch.") == set(), \
            "Zahlen-Artefakte werden fälschlich zu Hosts"
        # Geheimnis-Schutz: sensible Verweise dürfen NIE als harmlos gelten.
        for bad in ("/home/claudebot/claude-telegram-bot/.env",
                    "/etc/claude-telegram-bot.env",
                    "/home/claudebot/.claude/.credentials.json",
                    "cat ~/.ssh/id_ed25519_logsync",
                    "logs/api_token.txt"):
            assert _is_sensitive_ref(bad), f"Geheimnis-Schutz greift nicht: {bad}"
        assert not _is_sensitive_ref("/home/claudebot/workspace/notizen.md"), \
            "Geheimnis-Schutz überzieht auf harmlose Pfade"
        # Struktur-Invarianten im Callback: Schranke + Schutz sind verdrahtet,
        # WebSearch bleibt Kosten-Dialog, Always-Allow prüft sensitive.
        import inspect as _insp
        src = _insp.getsource(make_permission_callback)
        assert "task_origins" in src, "Herkunfts-Schranke nicht im Callback"
        assert "_is_sensitive_ref" in src, "Geheimnis-Schutz nicht im Callback"
        assert "WebSearch" in _COST_TOOLS, "WebSearch-Kostendialog entfernt"
        assert src.index("sensitive = _is_sensitive_ref") < src.index(
            "sess.always_allowed_tools\n"), "Geheimnis-Check muss VOR Always-Allow stehen"
        # WebFetch darf NIE pauschal dauerfreigebbar sein (23.07.): die Menge
        # ist verdrahtet im Always-Zweig, im Knopf-Angebot UND in der
        # Selbstheilung beim Session-Aufbau; Vertrauen läuft pro Domain.
        assert "WebFetch" in _NO_ALWAYS_TOOLS and "WebSearch" in _NO_ALWAYS_TOOLS
        assert src.count("_NO_ALWAYS_TOOLS") >= 3, \
            "_NO_ALWAYS_TOOLS nicht überall verdrahtet (Always-Zweig/Knopf/Callback)"
        assert "trusted_domains" in src, "Domain-Merkliste nicht im Callback"
        assert "_NO_ALWAYS_TOOLS" in _insp.getsource(ensure_session), \
            "Selbstheilung alter Always-Einträge fehlt im Session-Aufbau"
    check("Reibungslose Recherche (5.25)", _c_research)

    # 17. Governance 8.7 — der Bot kann sein Repo nicht beschreiben, und der
    # VPS-Klon IST nachweislich unangetastet (auf dem Mac: nur Logik-Prüfung).
    def _c_repo_readonly() -> None:
        repo = "/home/claudebot/claude-telegram-bot"
        # Schreibmuster werden erkannt, Lesen bleibt frei.
        for bad in (f"cd {repo} && git commit -am x", f"git -C {repo} push",
                    f"echo x > {repo}/bot.py", f"sed -i s/a/b/ {repo}/bot.py",
                    f"rm {repo}/MIGRATION.md"):
            assert _is_repo_write_cmd(bad), f"Schreibmuster nicht erkannt: {bad}"
        for good in (f"git -C {repo} log --oneline", f"cat {repo}/MIGRATION.md",
                     f"grep -r Ampel {repo}", "echo hallo > /tmp/x.txt"):
            assert not _is_repo_write_cmd(good), f"Fehlalarm bei Lese-Befehl: {good}"
        # Auf dem VPS zusätzlich: Klon hat keine lokalen Veränderungen.
        if Path(repo).is_dir():
            import subprocess
            out = subprocess.run(["git", "-C", repo, "status", "--porcelain"],
                                 capture_output=True, text=True, timeout=20)
            dirty = [l for l in out.stdout.splitlines()
                     if l.strip() and not l.strip().endswith("logs/")]
            assert not dirty, f"VPS-Klon hat lokale Veränderungen: {dirty[:3]}"
    check("Repo NUR-LESEN (8.7)", _c_repo_readonly)

    return state["ok"], results


async def cmd_selfcheck(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Manueller Selbstcheck der Kern-Invarianten."""
    if not authorized(update):
        return
    ok, lines = run_self_check()
    header = "Selbstcheck: alles grün." if ok else "⚠️ Selbstcheck: Probleme gefunden!"
    await update.message.reply_text(header + "\n\n" + "\n".join(lines))


def _reconcile_pending(app: Application) -> str:
    """5.2 Schritt 2 — Startup-Reconcile im HYBRID-Modus (Adam-Entscheid 17.07.).

    Läuft beim Start über die liegengebliebenen Persistenz-Records:

      Status „offen" (nie begonnen)          → **automatisch nachholen**. Die
          Nachricht wurde nachweislich nie an Claude geschickt, es kann also
          keine halbe Antwort draußen sein.
      Status „in_bearbeitung"/„fehler"       → **nur melden**. Hier kann bereits
          eine (Teil-)Antwort rausgegangen sein; blind neu zu verarbeiten
          erzeugte Doppelantworten. Adam entscheidet selbst, ob er wiederholt.

    Gibt eine Meldezeile für die Startup-Nachricht zurück ("" wenn nichts anlag).
    Die Jobs werden nur EINGEREIHT — die Worker startet der Aufrufer verzögert,
    damit die Startup-Nachricht zuerst ankommt.
    """
    try:
        recs = pending.load_all()
    except Exception:
        log.exception("Reconcile: Records nicht lesbar (nicht-fatal)")
        return ""
    if not recs:
        return ""

    # Chronologisch nachholen. Die laufende Queue ist bewusst LIFO („neueste
    # zuerst"), hier gilt das Gegenteil: nachgeholte Nachrichten in ihrer
    # ursprünglichen Reihenfolge, sonst wird eine Unterhaltung rückwärts gelesen.
    recs.sort(key=lambda r: r.get("received_at") or 0)

    resumed: list[dict] = []
    reported: list[dict] = []
    gaveup: list[dict] = []
    voice_lost: list[dict] = []
    for r in recs:
        key = r.get("_key")
        uid = r.get("user_id")
        # Unbrauchbar oder fremd → auflösen statt ewig mitschleppen.
        if not key or not uid or uid not in ALLOWED_USER_IDS or not r.get("text") \
                or r.get("chat_id") is None:
            log.warning("Reconcile: Record verworfen (unvollständig/fremd): %s", key)
            pending.resolve(key or "")
            continue

        # Sprachnachricht, die es nie bis zur Transkription geschafft hat: Ihr
        # gespeicherter „Text" ist nur ein Platzhalter. Automatisch nachholen wäre
        # hier falsch — Claude bekäme den Platzhalter statt Adams Anliegen. Also
        # dieselbe Hybrid-Regel wie bei „sendet": ehrlich melden statt raten. Das
        # Audio liegt dauerhaft in UPLOAD_DIR, die Nachricht ist also nicht weg.
        if r.get("stage") == VOICE_STAGE:
            voice_lost.append(r)
            pending.resolve(key)
            continue

        # Nachholbar ist alles, bei dem der Versand nachweislich NOCH NICHT begonnen
        # hatte: `offen` (nie gestartet) und `in_bearbeitung` (Claude dachte noch —
        # `stream_response` sammelt nur, es kann also nichts beim Nutzer sein).
        # Nur ab `sendet`/`fehler` ist unklar, ob schon etwas ankam → melden.
        if r.get("status") in (pending.STATUS_OPEN, pending.STATUS_RUNNING):
            # Absturz-Schleifen-Bremse: Wurde diese Nachricht schon mehrfach
            # nachgeholt und der Bot ging jedes Mal vorher unter, ist sie
            # vermutlich die Ursache — dann nicht weiter wiederholen, sondern
            # ehrlich melden. Ohne diese Bremse startet der Bot in einer Schleife.
            if pending.bump_attempts(key) > _MAX_RESUME_ATTEMPTS:
                log.warning("Reconcile: %s nach %d Versuchen aufgegeben",
                            key, _MAX_RESUME_ATTEMPTS)
                gaveup.append(r)
                pending.resolve(key)
                continue
            job = QueuedJob(
                update=None,                       # kein lebendes Update mehr — nur Primitive
                text=r["text"],
                force_tts=bool(r.get("force_tts")),
                output_chat_id=r.get("output_chat_id"),
                reply_to_override=r.get("reply_to_override"),
                received_at=r.get("received_at") or time.time(),
                thorough=bool(r.get("thorough")),
                pending_key=key,
                user_id=uid,
                chat_id=r.get("chat_id"),
                message_id=r.get("message_id"),
                thread_id=r.get("thread_id"),
                message_date=r.get("message_date"),
                bot=app.bot,
                resumed=True,
            )
            _get_mailbox(uid).queue.append(job)    # ans Ende = chronologisch
            if r.get("message_id") is not None:
                _RESUMED_KEYS.add(key)             # gegen Telegrams Zweitzustellung
            resumed.append(r)
        else:
            reported.append(r)
            # Melden UND auflösen: bliebe der Record liegen, meldete der Bot ihn
            # bei jedem künftigen Start erneut (Dauer-Nörgeln).
            pending.resolve(key)

    lines: list[str] = []
    if resumed:
        n = len(resumed)
        lines.append(f"📨 {n} unbeantwortete {'Nachricht' if n == 1 else 'Nachrichten'} "
                     "aus dem Neustart-Fenster — ich hole sie jetzt nach:")
        lines += [f"  • „{_job_preview(r['text'])}“" for r in resumed[:5]]
        if n > 5:
            lines.append(f"  … und {n - 5} weitere")
    if reported:
        n = len(reported)
        lines.append(f"⚠️ Bei {n} {'Nachricht' if n == 1 else 'Nachrichten'} war die Antwort "
                     "schon fertig und im Versand — ob sie dich ganz erreicht hat, kann ich "
                     "nicht sicher sagen. Deshalb hole ich sie NICHT automatisch nach "
                     "(sonst bekämst du sie womöglich doppelt):")
        lines += [f"  • „{_job_preview(r['text'])}“" for r in reported[:5]]
        if n > 5:
            lines.append(f"  … und {n - 5} weitere")
        lines.append("→ Kam dazu keine Antwort, schick die Nachricht bitte nochmal.")
    if gaveup:
        n = len(gaveup)
        lines.append(f"🛑 {n} {'Nachricht' if n == 1 else 'Nachrichten'} konnte ich auch "
                     f"nach {_MAX_RESUME_ATTEMPTS} Anläufen nicht verarbeiten — ich höre "
                     "damit auf, statt es endlos zu wiederholen:")
        lines += [f"  • „{_job_preview(r['text'])}“" for r in gaveup[:5]]
        if n > 5:
            lines.append(f"  … und {n - 5} weitere")
        lines.append("→ Bitte anders formuliert oder in kleineren Teilen nochmal schicken.")
    if voice_lost:
        n = len(voice_lost)
        lines.append(f"🎙️ {n} {'Sprachnachricht' if n == 1 else 'Sprachnachrichten'} von dir "
                     f"{'war' if n == 1 else 'waren'} gerade in der Transkription, als ich "
                     "unterbrochen wurde — ich habe sie also nie verstanden:")
        for r in voice_lost[:5]:
            when = _voice_when(r)
            dur = r.get("voice_duration")
            dauer = f", {int(dur)} Sekunden lang" if isinstance(dur, (int, float)) and dur else ""
            lines.append(f"  • Sprachnachricht von {when}{dauer}")
        if n > 5:
            lines.append(f"  … und {n - 5} weitere")
        lines.append("→ Das Audio liegt gesichert vor, verloren ist nichts. "
                     "Am schnellsten geht es, wenn du sie kurz nochmal schickst.")

    log.info("Reconcile: %d nachgeholt, %d gemeldet, %d aufgegeben, %d Voice unterbrochen",
             len(resumed), len(reported), len(gaveup), len(voice_lost))
    return "\n".join(lines)


def _voice_when(rec: dict) -> str:
    """Uhrzeit einer Sprachnachricht für die Meldung — absoluter Bezug statt
    „letzte/vorletzte", damit Adam sie im Verlauf sofort wiederfindet."""
    ts = rec.get("message_date") or rec.get("received_at")
    try:
        return time.strftime("%H:%M", time.localtime(float(ts)))
    except Exception:
        return "unbekannter Zeit"


async def post_init(app: Application) -> None:
    """Started after Application.initialize() — kicks off the watchdog task."""
    app.create_task(watchdog(app), name="watchdog")
    log.info("watchdog started (interval=%ds, timeout=%ds, threshold=%d)",
             WATCHDOG_INTERVAL_S, WATCHDOG_TIMEOUT_S, WATCHDOG_FAIL_THRESHOLD)
    app.create_task(heartbeat_writer(), name="heartbeat")
    log.info("heartbeat writer started (interval=%ds, path=%s)",
             HEARTBEAT_INTERVAL_S, HEARTBEAT_PATH)
    # 5.18: zweiter Wächter — der oben prüft den Bot, dieser die Claude-Session.
    app.create_task(stall_watchdog(app), name="stall_watchdog")
    log.info("Stall-Wächter gestartet (Intervall=%ds, Limit=%ds, Wiederholungen=%d)",
             STALL_CHECK_INTERVAL_S, STALL_LIMIT_S, MAX_STALL_RETRIES)

    # Bot-Username für Rücksprung-Links (Ausgabekanal → Bot-Chat) einmalig cachen.
    global _BOT_USERNAME
    try:
        me = await app.bot.get_me()
        _BOT_USERNAME = me.username
        log.info("bot username gecached: @%s", _BOT_USERNAME)
    except Exception:
        log.warning("bot username konnte nicht ermittelt werden (Rück-Button inaktiv)")

    # Befehls-Menü in Telegram registrieren, damit die „/"-Autovervollständigung
    # die Befehle vorschlägt — sonst tippt man z.B. /presend blind und verschreibt
    # sich (genau so am 17.07.: „/present" statt „/presend"). Fehlschlag hier ist
    # unkritisch, der Bot läuft auch ohne Menü.
    try:
        await app.bot.set_my_commands([
            BotCommand("hilfe", "Alle Befehle anzeigen"),
            BotCommand("stopp", "✋ Laufende Aufgabe abbrechen"),
            BotCommand("status", "Queue & Session-Übersicht"),
            BotCommand("freigaben", "Dauerhafte Werkzeug-Freigaben"),
            BotCommand("technik", "Werkzeug-Spur: Klartext ↔ Rohform"),
            BotCommand("spur", "Werkzeug-Spur ganz aus/an"),
            BotCommand("presend", "Pre-Send-Hook — Kennzahlen"),
            BotCommand("ampel", "Ampel — Regeln & Status"),
            BotCommand("usage", "Token-Verbrauch heute"),
            BotCommand("tts", "Sprachausgabe an/aus"),
            BotCommand("quiet", "Ruhiger Modus (Tipp-Indikator aus)"),
            BotCommand("verbose", "Tipp-Indikator wieder an"),
            BotCommand("reset", "Session zurücksetzen"),
            BotCommand("selfcheck", "Selbsttest der Kernfunktionen"),
            BotCommand("setkanal", "Ausgabekanal setzen"),
            BotCommand("whereami", "Aktuellen Kanal zeigen"),
            BotCommand("restart", "Bot neu starten"),
        ])
        log.info("Telegram-Befehlsmenü registriert (setMyCommands)")
    except Exception:
        log.warning("setMyCommands fehlgeschlagen (Menü evtl. unvollständig)", exc_info=True)

    # Startup-Statusnachricht: Wenn ich (Claude) vor dem Neustart einen Grund
    # hinterlegt habe, wird er hier gelesen und als Telegram-Nachricht gesendet.
    # Ohne Datei: generische "Bot läuft"-Meldung + automatischer Chat-Check.
    # AUTORUN-Marker: Zeile "[AUTORUN]: <text>" → wird abgeschnitten und als
    # eigenständige Claude-Anfrage direkt nach der Startup-Nachricht ausgeführt.
    autorun_tasks: list[tuple[int, str]] = []  # (uid, autorun_text)
    try:
        silent_ok = False  # [STILL]-Marker: planmäßiger Hygiene-Neustart —
        # bei sauberem Start KEINE Telegram-Meldung (4-Uhr-Fenster, Rotes-Team
        # C.3); Auffälligkeiten (Selbstcheck, Reconcile, Restart-Fenster-
        # Eingänge) werden trotzdem gebündelt gemeldet.
        if _RESTART_REASON_FILE.exists():
            startup_msg = _RESTART_REASON_FILE.read_text(encoding="utf-8").strip()
            _RESTART_REASON_FILE.unlink(missing_ok=True)
            if startup_msg.startswith("[STILL]"):
                silent_ok = True
                startup_msg = startup_msg[len("[STILL]"):].strip() or (
                    "🌙 Nächtlicher Hygiene-Neustart (4-Uhr-Fenster).")
            # AUTORUN-Marker extrahieren
            if "[AUTORUN]:" in startup_msg:
                parts = startup_msg.split("[AUTORUN]:", 1)
                startup_msg = parts[0].strip()
                autorun_text = parts[1].strip()
                for uid in ALLOWED_USER_IDS:
                    autorun_tasks.append((uid, autorun_text))
        else:
            startup_msg = _startup_message_from_last_task()
            # Offene Punkte aus letzter Session? → direkt als AUTORUN aufgreifen,
            # nicht nur im Startup-Text erwähnen.
            pending_full = _detect_pending_item(full=True)
            if pending_full:
                autorun_prompt = (
                    "Direkt nach Neustart aufgreifen — das war in der letzten Session noch offen:\n\n"
                    + pending_full
                    + "\n\nBitte nahtlos dort weitermachen, ohne Neueinleitung."
                )
                for uid in ALLOWED_USER_IDS:
                    autorun_tasks.append((uid, autorun_prompt))
        # Pending-Updates-Check (Vor-Migrations-Schutzpaket, Punkt 3 von 3):
        # Beim Bot-Start einmalig nachsehen, ob am Telegram-Server Nachrichten
        # warten, die im Restart-Fenster reingekommen sind. Falls ja, Adam aktiv
        # darauf hinweisen — er soll nie raten müssen, ob etwas durchgerutscht ist.
        # Der Peek konsumiert die Updates nicht (kein Folge-getUpdates mit
        # höherem offset), das normale run_polling holt sie regulär ab und
        # verarbeitet sie über die Handler.
        # 8.3/1.9: Im WEBHOOK-Modus ist getUpdates NICHT nutzbar (Telegram gibt 409,
        # solange ein Webhook gesetzt ist) — Telegram stellt die im Restart-Fenster
        # aufgelaufenen Updates ohnehin selbst über den Webhook nach. Peek überspringen.
        pending_info_line = ""
        _webhook_mode = (os.environ.get("BOT_MODE") or "polling").strip().lower() == "webhook"
        if _webhook_mode:
            log.info("Webhook-Modus: getUpdates-Peek übersprungen (Telegram stellt "
                     "Restart-Fenster-Updates selbst nach).")
        else:
            try:
                pending_updates = await app.bot.get_updates(timeout=0, limit=100)
                relevant = [
                    u for u in pending_updates
                    if u.message is not None
                    or u.edited_message is not None
                    or u.message_reaction is not None
                ]
                if relevant:
                    n = len(relevant)
                    word = "Nachricht" if n == 1 else "Nachrichten"
                    pending_info_line = (
                        f"📨 {n} {word} aus dem Restart-Fenster — wird gleich abgearbeitet."
                    )
                    log.info("pending-updates-check: %d update(s) warten in der Pipeline", n)
            except Exception:
                log.warning("pending-updates-check failed (ignored)", exc_info=True)
        if pending_info_line:
            startup_msg = pending_info_line + "\n\n" + startup_msg

        # 5.2 Schritt 2: liegengebliebene Nachrichten aufgreifen (Hybrid). Steht
        # ganz oben in der Startup-Nachricht — es ist die wichtigste Information
        # nach einem unsauberen Neustart („ist etwas von mir untergegangen?").
        reconcile_line = ""
        try:
            reconcile_line = _reconcile_pending(app)
            if reconcile_line:
                startup_msg = reconcile_line + "\n\n" + startup_msg
        except Exception:
            log.exception("Reconcile beim Start fehlgeschlagen (nicht-fatal)")
        # Selbstcheck der Kern-Invarianten bei JEDEM Start — fängt Regressionen ab.
        # Bei Erfolg eine knappe Zeile, bei Fehler laut + auffällig.
        selfcheck_trouble = False
        try:
            ok, lines = run_self_check()
            if ok:
                startup_msg += f"\n\nSelbstcheck: alle {len(lines)} Kernfunktionen ok."
            else:
                selfcheck_trouble = True
                fails = [l for l in lines if l.startswith("✗")]
                startup_msg += ("\n\n⚠️ SELBSTCHECK-WARNUNG — bitte prüfen:\n" + "\n".join(fails))
        except Exception as e:
            selfcheck_trouble = True
            startup_msg += f"\n\n⚠️ Selbstcheck konnte nicht laufen: {e}"
        # Stiller Hygiene-Neustart: sauber (kein Befund) → nur Log, kein Telegram.
        noteworthy = bool(pending_info_line) or bool(reconcile_line) or selfcheck_trouble
        if silent_ok and not noteworthy:
            log.info("Hygiene-Neustart sauber — Startmeldung unterdrückt ([STILL]).")
            send_targets: list[int] = []
        else:
            send_targets = list(ALLOWED_USER_IDS)
        for uid in send_targets:
            try:
                prefs = _USER_PREFS.get(str(uid), {})
                kb = _main_keyboard(prefs.get("tts_enabled", False),
                                    prefs.get("model", DEFAULT_MODEL),
                                    prefs.get("effort", None))
                tts_on = prefs.get("tts_enabled", False)
                tts_clean = _strip_markdown_for_tts(startup_msg) if tts_on else ""
                if tts_on and tts_clean:
                    # Voice + Text als Caption in EINER Nachricht (konsistent zu
                    # normalen Antworten — Adam will keine getrennte Reply-Voice).
                    text_parts = _split_tts_chunks(startup_msg, max_chars=1024)
                    sent_first = None
                    for i, part in enumerate(text_parts):
                        tts_part = _strip_markdown_for_tts(part)
                        if not tts_part:
                            # Reststück ohne sprechbaren Inhalt → als normalen Text
                            m = await app.bot.send_message(
                                chat_id=uid, text=part,
                                reply_markup=kb if i == 0 else None,
                            )
                            sent_first = sent_first or m
                            continue
                        await _send_tts_chunk(
                            app.bot, uid, tts_part,
                            caption=part[:1024],
                            reply_markup=kb if i == 0 else None,
                        )
                else:
                    m = await app.bot.send_message(chat_id=uid, text=startup_msg,
                                                   reply_markup=kb)
                    # 5.9: Auch die Startnachricht ist reaktionsfähig — Bezug
                    # merken und (falls sie fragt) als offene Frage registrieren.
                    _remember_bot_msg(uid, m.message_id, startup_msg)
                    reactions.register_question(uid, m.message_id, startup_msg)
            except Exception:
                log.warning("startup message to user %s failed", uid)
        # 5.2 Schritt 2: Die Worker für nachgeholte Nachrichten erst JETZT
        # anwerfen — nach der Startup-Nachricht, damit Adam erst die Ankündigung
        # („ich hole nach: …") und dann die Antwort sieht, nicht umgekehrt.
        if any(mb.queue for mb in MAILBOXES.values()):
            async def _start_resumed_workers() -> None:
                await asyncio.sleep(2)
                for uid, mb in list(MAILBOXES.items()):
                    if mb.queue:
                        _ensure_worker(uid)
            app.create_task(_start_resumed_workers(), name="resumed-workers")

        # AUTORUN-Tasks als Hintergrundaufgaben starten (nach kurzer Pause,
        # damit die Startup-Nachricht zuerst ankommt)
        for uid, autorun_text in autorun_tasks:
            async def _do_autorun(u: int = uid, t: str = autorun_text) -> None:
                await asyncio.sleep(2)
                try:
                    sess = await ensure_session(u)
                    sess.bot = app.bot
                    sess.chat_id = u
                    if sess.logger:
                        sess.logger.log_user(t)
                    async with sess.lock:
                        await sess.client.query(t)  # war fälschlich .send_message()
                        # stream_response SAMMELT nur (Umbau 17.07.) → hier selbst
                        # prüfen und senden, sonst verschwände die Autorun-Antwort.
                        ans = await stream_response(sess, u)
                    if ans:
                        ans, fnd = presend.check_and_fix(ans)
                        presend.log_findings(fnd, {"quelle": "autorun", "user_id": u})
                        await send_answer_to_user(sess, u, ans)
                except Exception:
                    log.exception("autorun failed for uid=%s", u)
            app.create_task(_do_autorun(), name=f"autorun-{uid}")
    except Exception:
        log.exception("startup notification failed")


async def process_user_text(
    update: Update,
    text: str,
    force_tts: bool = False,
    output_chat_id: int | None = None,
    reply_to_override: int | None = None,
    log_note: str | None = None,
) -> None:
    """Shared path: authorized update + text → Claude query + streamed response.

    output_chat_id: wenn gesetzt, gehen Antworten dorthin statt in den User-Chat.
    reply_to_override: message_id, auf die Antwort/TTS als Reply zeigen sollen
    (z.B. die Transkriptions-Nachricht statt der reinen Sprachnachricht).
    """
    user_id = update.effective_user.id

    # Datenschutz-Ampel (2.2, BEOBACHTUNGSPHASE): jede Nachricht einstufen +
    # protokollieren — noch KEIN Umrouten. Enforcement (rot → lokal) folgt erst
    # nach der Auswertung. observe() ist selbst fehlertolerant.
    try:
        ampel.observe(text, meta={"user_id": user_id, "force_tts": force_tts})
    except Exception:
        log.exception("Ampel-observe übersprungen (nicht-fatal)")

    thorough = user_id in _THOROUGH_PENDING
    _THOROUGH_PENDING.discard(user_id)

    msg = update.message
    chat_id = update.effective_chat.id
    message_id = getattr(msg, "message_id", None)

    # 5.2 DEDUP: Nach einem harten Kill stellt Telegram Nachrichten aus dem
    # Restart-Fenster ERNEUT zu (DROP_PENDING_UPDATES=False, absichtlich). Hat der
    # Startup-Reconcile dieselbe Nachricht schon aus der Persistenz nachgeholt,
    # käme sie hier ein zweites Mal an → doppelte Antwort. Der Schlüssel ist je
    # Telegram-Nachricht eindeutig, also genügt er als Sperre.
    dedup_key = pending.make_key(chat_id, message_id) if message_id is not None else None
    if dedup_key and dedup_key in _RESUMED_KEYS:
        _RESUMED_KEYS.discard(dedup_key)
        log.info("dedup: Nachricht %s wird bereits aus der Persistenz nachgeholt "
                 "— Telegram-Zweitzustellung verworfen", dedup_key)
        return

    mb = _get_mailbox(user_id)
    job = QueuedJob(
        update=update,
        text=text,
        force_tts=force_tts,
        output_chat_id=output_chat_id or chat_id,
        reply_to_override=reply_to_override,
        thorough=thorough,
        user_id=user_id,
        chat_id=chat_id,
        message_id=message_id,
        thread_id=getattr(msg, "message_thread_id", None),
        message_date=(msg.date.timestamp() if msg is not None and msg.date else None),
        log_note=log_note,
    )

    # 5.2: Nachricht SOFORT persistieren (überlebt Reboot). Nur serialisierbare
    # Primitive — das lebende Update geht nicht; der Anhang-Pfad steckt bereits
    # im text (Datei liegt dauerhaft in UPLOAD_DIR). Rein additiv/fehlertolerant.
    try:
        if dedup_key is not None:
            job.pending_key = dedup_key
            pending.record(dedup_key, {
                "user_id": user_id,
                "chat_id": chat_id,
                "message_id": message_id,
                "thread_id": job.thread_id,
                "text": text,
                "force_tts": force_tts,
                "output_chat_id": job.output_chat_id,
                "reply_to_override": reply_to_override,
                "thorough": thorough,
                "received_at": job.received_at,
                "message_date": job.message_date,
            })
    except Exception:
        log.exception("5.2 Persistenz beim Empfang übersprungen (nicht-fatal)")

    busy = mb.current_job is not None
    interrupt = _is_interrupt(text)

    if interrupt and busy:
        # Echtes Stopp/Korrektur-Signal: laufenden Vorgang abbrechen (gilt als
        # hinfällig), diese Nachricht sofort als Nächstes VORNE einarbeiten.
        try:
            sess = SESSIONS.get(user_id)
            if sess is not None:
                await sess.client.interrupt()
        except Exception:
            log.exception("interrupt on correction failed")
        mb.queue.appendleft(job)
        await update.message.reply_text(
            "✋ Laufenden Vorgang gestoppt — ich nehme das jetzt vorrangig.",
            reply_parameters=_reply_params(update.message.message_id),
        )
    else:
        # 5.5 [GEÄNDERT]: FIFO — normale Nachricht chronologisch ans ENDE.
        mb.queue.append(job)
        if busy:
            running = _job_preview(mb.current_job.text) if mb.current_job else "läuft"
            pos = len(mb.queue)
            await update.message.reply_text(
                "📥 Notiert — reiht sich hinten ein (kommt der Reihe nach dran).\n"
                f"Läuft gerade: „{running}“\n"
                f"Warteschlange-Position: {pos}",
                reply_parameters=_reply_params(update.message.message_id),
            )

    _ensure_worker(user_id)


def _extract_reply_context(update: Update) -> str:
    """Gibt einen Kontext-Prefix zurück, wenn der User auf eine Nachricht geantwortet hat.

    Deckt explizit den Fall ab, dass Adam auf eine frühere Nachricht von MIR
    antwortet (Text ODER Sprachnachricht) — dann muss der Bezug klar gemacht
    werden, damit ich genau darauf eingehe. Sprachnachrichten tragen in Telegram
    keinen Text; ihr Inhalt wird über BOT_MSGS aufgelöst.
    """
    reply = getattr(update.message, "reply_to_message", None)
    if reply is None:
        return ""
    chat_id = update.effective_chat.id
    original = (reply.text or reply.caption or "").strip()
    # Voice/Audio (und allgemein leere Bot-Nachrichten) über den Speicher auflösen.
    if not original:
        original = BOT_MSGS.get((chat_id, reply.message_id), "")

    from_user = getattr(reply, "from_user", None)
    is_bot = bool(getattr(from_user, "is_bot", False))

    has_photo = bool(reply.photo)
    has_doc = reply.document is not None
    has_video = reply.video is not None or reply.video_note is not None

    preview = original if len(original) <= 600 else original[:600] + "…"

    # Medien-Replies des Users (Bild/Dokument/Video) — unverändert.
    if not is_bot and has_doc:
        fname = reply.document.file_name or "Dokument"
        return (f"[Du antwortest auf ein Dokument ({fname}) mit Beschriftung: \"{preview}\"]\n\n"
                if original else f"[Du antwortest auf ein Dokument: {fname}]\n\n")
    if not is_bot and has_video:
        return (f"[Du antwortest auf ein Video mit Beschriftung: \"{preview}\"]\n\n"
                if original else "[Du antwortest auf ein Video]\n\n")
    if not is_bot and has_photo:
        return (f"[Du antwortest auf ein Bild mit Beschriftung: \"{preview}\"]\n\n"
                if original else "[Du antwortest auf ein Bild (ohne Beschriftung)]\n\n")

    if not preview:
        return ""

    # Reply auf eine meiner eigenen (Bot-)Nachrichten → expliziter Bezug.
    if is_bot:
        return (f"[Kontext: Adam bezieht sich mit der folgenden Nachricht ausdrücklich auf deine "
                f"vorherige Nachricht: \"{preview}\". Beziehe deine Antwort genau darauf — "
                f"seine eigentliche Nachricht folgt jetzt:]\n\n")
    # Reply auf eine frühere eigene Nachricht des Users — kann Ergänzung ODER Widerruf sein.
    return (f"[Kontext: Adam zitiert seine eigene frühere Nachricht: \"{preview}\". "
            f"Lies diese zitierte Nachricht vollständig und berücksichtige sie UNBEDINGT, bevor du "
            f"handelst — seine neue Nachricht ist meist ein Nachtrag, eine Ergänzung oder ein "
            f"Widerruf genau zu diesem zitierten Inhalt. Verarbeite beides zusammen:]\n\n")


def _build_restart_reason(user_id: int) -> str:
    """Baut die Startup-Nachricht für einen vom User ausgelösten Neustart —
    als natürliche Gesprächsfortsetzung, gespeist aus dem Mailbox-Zustand.
    Schlusszeile bestätigt, dass im Restart-Fenster eingegangene Nachrichten
    automatisch nachgeholt werden (DROP_PENDING_UPDATES=False)."""
    tail = " Falls du während des Neustarts noch etwas geschickt hast, hole ich es jetzt nach."
    mb = MAILBOXES.get(user_id)
    if mb and mb.current_job is not None:
        return (f"Bin wieder da. Der Vorgang „{_job_preview(mb.current_job.text)}“ "
                "wurde durch den Neustart unterbrochen — soll ich da weitermachen?"
                + tail)
    if mb and mb.done_log:
        _ts, preview = mb.done_log[-1]
        return (f"Bin wieder da. Zuletzt erledigt: „{preview}“. Woran machen wir weiter?"
                + tail)
    return "Bin wieder da." + tail


async def _request_restart_confirm(update: Update, user_id: int) -> None:
    """Zeigt einen Inline-Bestätigungs-Dialog, BEVOR der Bot wirklich neu startet.
    Schützt gegen versehentliches Antippen des Reply-Keyboard-Buttons (passierte
    am 2026-06-23 22:08, dadurch ging eine Voice im Restart-Fenster verloren)."""
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Ja, neu starten", callback_data="rst:confirm"),
        InlineKeyboardButton("❌ Abbrechen", callback_data="rst:cancel"),
    ]])
    await update.message.reply_text(
        "🔄 Wirklich neu starten?",
        reply_markup=kb,
    )


async def on_restart_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Verarbeitet die Antwort auf den Restart-Bestätigungs-Dialog."""
    query = update.callback_query
    if query is None or not authorized(update):
        return
    await query.answer()
    user_id = update.effective_user.id
    if query.data == "rst:cancel":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            log.exception("could not remove restart-confirm buttons (cancel)")
        try:
            await query.message.reply_text("❌ Abgebrochen — Bot läuft weiter.")
        except Exception:
            log.exception("could not send restart-cancel reply")
        return
    if query.data == "rst:confirm":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            log.exception("could not remove restart-confirm buttons (confirm)")
        # _do_restart schickt die Restart-Bestätigung als Reply auf den Dialog.
        await _do_restart(update, user_id, via_callback=True)


def _mask_secrets(text: str) -> str:
    """Entfernt Geheimnisse aus Fehlertexten, BEVOR sie in einer Datei oder gar
    in einer Telegram-Nachricht landen.

    Telegram-Fehlermeldungen enthalten regelmäßig die API-URL — und darin steckt
    der Bot-Token (`https://api.telegram.org/bot<TOKEN>/…`). Ein `InvalidToken`
    zitiert ihn sogar wörtlich. Ohne diese Maske stünde er nach einem Absturz in
    `bot-restart-reason.txt` (wird gebackupt!), im Chat-Log und in der
    Startnachricht — genau das darf nie passieren (Adam-Regel: Secrets nie in
    den Chat). Beim Testcrash am 20.07. live aufgefallen."""
    import re as _re
    out = text or ""
    for secret in (TELEGRAM_BOT_TOKEN, os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")):
        if secret and len(secret) > 8:
            out = out.replace(secret, "<GEHEIM>")
    # Zusätzlich generisch: Bot-Token-Muster (Ziffern:Base64-artig), auch wenn es
    # ein anderer als der eigene ist.
    out = _re.sub(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b", "<GEHEIM>", out)
    return out


def _write_crash_restart_reason(exc: BaseException) -> None:
    """Hinterlässt bei einem ABSTURZ einen lesbaren Grund für die nächste
    Startnachricht (Auftrag Web-Sitzung 20.07.).

    Bisher schrieb nur `/restart` bzw. der Guardian einen Grund; starb der Prozess
    an einer Exception (Telegram-Timeout beim Hochfahren, Netzwerkfehler, alles
    Unerwartete), blieb die Datei leer und Adam bekam nur ein wortloses „Bin
    wieder da" — ohne Hinweis, dass überhaupt etwas schiefgegangen war.

    Bewusste Grenze: Ein sauberes SIGTERM (`systemctl restart`) fängt
    python-telegram-bot intern ab, dort greift weiterhin die normale Logik.

    Ein bereits vorhandener, SPEZIFISCHER Grund (z. B. vom /restart-Befehl) wird
    nicht überschrieben — nur der generische Guardian-Fallback („lag still")
    weicht einer genaueren Ursache.
    """
    try:
        if _RESTART_REASON_FILE.exists():
            existing = _RESTART_REASON_FILE.read_text(encoding="utf-8")
            if "lag still" not in existing:
                return
    except Exception:
        pass

    from telegram.error import TimedOut, NetworkError, RetryAfter, Forbidden, InvalidToken
    # Reihenfolge beachten: TimedOut ist eine Unterklasse von NetworkError —
    # zuerst geprüft, sonst bekäme ein Timeout die unspezifische Netzwerk-Meldung.
    if isinstance(exc, (KeyboardInterrupt, SystemExit)):
        reason = "Kurz weg — sauberer Neustart (Signal / SystemExit). Bin wieder da."
    elif isinstance(exc, InvalidToken):
        # Bewusst OHNE Fehlertext: der zitiert den Token wörtlich.
        reason = ("⚠️ Der Telegram-Zugangsschlüssel wurde vom Server abgelehnt — "
                  "ich komme so nicht hoch. Bitte die Zugangsdaten prüfen.")
    elif isinstance(exc, TimedOut):
        reason = ("Kurz weg — Telegram-Verbindungs-Timeout. "
                  "Die Verbindung war kurzfristig unterbrochen, bin wieder da.")
    elif isinstance(exc, RetryAfter):
        reason = ("Kurz weg — Telegram hat einen Rate-Limit-Fehler gemeldet "
                  "(zu viele Anfragen). Läuft wieder.")
    elif isinstance(exc, NetworkError):
        reason = (f"Kurz weg — Netzwerkfehler ({type(exc).__name__}). "
                  "Verbindung steht wieder.")
    elif isinstance(exc, Forbidden):
        reason = ("Kurz weg — Telegram hat den Zugriff vorübergehend verweigert. "
                  "Läuft wieder.")
    else:
        # str(exc) kann Geheimnisse tragen (API-URL mit Token) → immer maskieren.
        short = _mask_secrets(str(exc))[:100]
        reason = (f"Kurz weg — unerwarteter Fehler "
                  f"({type(exc).__name__}: {short}). Bin neu gestartet.")

    try:
        _RESTART_REASON_FILE.parent.mkdir(parents=True, exist_ok=True)
        _RESTART_REASON_FILE.write_text(reason, encoding="utf-8")
        log.info("crash restart reason written: %s", type(exc).__name__)
    except Exception:
        log.warning("could not write crash restart reason", exc_info=True)


async def _do_restart(update: Update, user_id: int, via_callback: bool = False) -> None:
    """Schreibt den letzten Stand in die Restart-Grund-Datei und beendet den
    Prozess sanft — launchd (KeepAlive) startet den Bot neu, der die Datei beim
    Start liest und als Nachricht sendet. Sanftes Shutdown-Fenster (3s) gibt
    eingehenden Updates eine letzte Chance, noch verarbeitet zu werden."""
    try:
        _RESTART_REASON_FILE.parent.mkdir(parents=True, exist_ok=True)
        _RESTART_REASON_FILE.write_text(_build_restart_reason(user_id), encoding="utf-8")
    except Exception:
        log.exception("could not write restart reason file")
    restart_msg = "🔄 Starte neu — ich melde mich gleich wieder."
    chat_id = update.effective_chat.id
    bot = update.get_bot()
    # Bei Callback-Bestätigung: Reply auf den ursprünglichen Restart-Dialog,
    # damit die Bestätigung sichtbar zur Anfrage gehört (kein loser Eintrag).
    reply_to_id: Optional[int] = None
    if via_callback and update.callback_query is not None and update.callback_query.message is not None:
        reply_to_id = update.callback_query.message.message_id
    m = await bot.send_message(
        chat_id=chat_id, text=restart_msg, reply_to_message_id=reply_to_id,
        allow_sending_without_reply=True,
    )
    # Bestätigung folgt dem TTS-Toggle (analog zur Startup-Bestätigung).
    try:
        sess = SESSIONS.get(user_id)
        tts_on = (sess.tts_enabled if sess is not None
                  else _USER_PREFS.get(str(user_id), {}).get("tts_enabled", False))
        if tts_on:
            tts_clean = _strip_markdown_for_tts(restart_msg)
            if tts_clean:
                await _send_tts_chunk(
                    bot, chat_id, tts_clean, reply_to=m.message_id,
                )
    except Exception:
        log.exception("restart confirmation TTS failed")

    async def _kill() -> None:
        # Sanftes Shutdown-Fenster: 3s, damit Bestätigung + ggf. Voice rausgehen
        # UND Telegram-Updates, die im letzten Moment reinkommen, noch von den
        # laufenden Handlern angenommen werden können. DROP_PENDING_UPDATES=False
        # holt verbliebene Updates beim nächsten Start automatisch nach.
        await asyncio.sleep(3.0)
        log.info("user-requested restart — exiting so launchd restarts us")
        os._exit(0)

    asyncio.create_task(_kill())


async def cmd_restart(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    await _request_restart_confirm(update, update.effective_user.id)


async def _handle_keyboard_btn(update: Update, text: str) -> None:
    """Verarbeitet Tastendrücke der persistenten ReplyKeyboard."""
    user_id = update.effective_user.id

    if text == _BTN_RESTART:
        await _request_restart_confirm(update, user_id)
        return

    if text == _BTN_THOROUGH:
        _THOROUGH_PENDING.add(user_id)
        sess = SESSIONS.get(user_id)
        _p = _USER_PREFS.get(str(user_id), {})
        tts_on = sess.tts_enabled if sess else _p.get("tts_enabled", False)
        cur_model = sess.current_model if sess else _p.get("model", DEFAULT_MODEL)
        cur_effort = sess.current_effort if sess else _p.get("effort")
        await update.message.reply_text(
            "🎯 Gründlich-Modus für deine NÄCHSTE Nachricht aktiv:\n"
            f"{_model_btn_label(cur_model)} · hoher Effort · Pflicht-Quellencheck. "
            "Schick jetzt deine Frage.\n"
            "(Danach wieder Standard.)",
            reply_markup=_main_keyboard(tts_on, cur_model, cur_effort),
        )
        return

    if text in (_BTN_TTS_ON, _BTN_TTS_OFF):
        sess = await ensure_session(user_id)
        sess.tts_enabled = (text == _BTN_TTS_ON)
        _USER_PREFS.setdefault(str(user_id), {})["tts_enabled"] = sess.tts_enabled
        _save_prefs(_USER_PREFS)
        label = "🔊 Sprachnachricht-Modus an." if sess.tts_enabled else "🔇 Sprachnachricht-Modus aus."
        keyboard = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
        await update.message.reply_text(label, reply_markup=keyboard)
        return

    new_model = _MODEL_IDS.get(text)
    if new_model is not None:
        sess = SESSIONS.get(user_id)
        if sess and sess.current_model == new_model:
            keyboard = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
            model_label = ("Opus" if "opus" in new_model
                           else "Haiku" if "haiku" in new_model
                           else "Fable" if "fable" in new_model
                           else "Sonnet")
            await update.message.reply_text(f"{model_label} ist bereits aktiv.", reply_markup=keyboard)
            return
        # Sanfter Wechsel (22.07.): Läuft gerade ein Job, wird NICHT hart
        # geschlossen (das beendete ihn als „fehler") — Prefs sofort speichern,
        # Merker setzen, der Worker schließt nach Job-Abschluss. Wartende Jobs
        # in der Queue laufen damit bereits mit der neuen Einstellung.
        _USER_PREFS.setdefault(str(user_id), {})["model"] = new_model
        _save_prefs(_USER_PREFS)
        model_label = _model_btn_label(new_model)
        mb = MAILBOXES.get(user_id)
        if mb and mb.current_job is not None:
            mb.switch_pending = True
            _p = _USER_PREFS.get(str(user_id), {})
            keyboard = _main_keyboard(_p.get("tts_enabled", False), new_model, _p.get("effort"))
            await update.message.reply_text(
                f"🔄 Vorgemerkt: {model_label} gilt ab der nächsten Aufgabe — "
                "die laufende wird noch im bisherigen Modus fertiggestellt.",
                reply_markup=keyboard,
            )
            return
        # Leerlauf: Modell wechseln, Session sofort neu starten
        await close_session(user_id)
        new_sess = await ensure_session(user_id)
        keyboard = _main_keyboard(new_sess.tts_enabled, new_sess.current_model, new_sess.current_effort)
        await update.message.reply_text(
            f"{model_label} aktiv. Session neu gestartet.",
            reply_markup=keyboard,
        )
        return

    # --- Thinking-Effort-Button ---
    if text in _EFFORT_IDS:
        new_effort = _EFFORT_IDS[text]
        sess = SESSIONS.get(user_id)
        if sess and sess.current_effort == new_effort:
            keyboard = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
            effort_name = {None: "Normal", "low": "Schnell", "max": "Max"}.get(new_effort, str(new_effort))
            await update.message.reply_text(f"Denke nach: {effort_name} ist bereits aktiv.", reply_markup=keyboard)
            return
        # Sanfter Wechsel (22.07.): identisch zum Modell-Zweig — laufender Job
        # wird nie hart abgebrochen, Prefs greifen ab der nächsten Aufgabe.
        prefs = _USER_PREFS.setdefault(str(user_id), {})
        if new_effort is None:
            prefs.pop("effort", None)
        else:
            prefs["effort"] = new_effort
        _save_prefs(_USER_PREFS)
        effort_labels = {None: "🧠 Normal", "low": "⚡ Schnell", "max": "🚀 Max"}
        effort_label = effort_labels.get(new_effort, str(new_effort))
        mb = MAILBOXES.get(user_id)
        if mb and mb.current_job is not None:
            mb.switch_pending = True
            _p = _USER_PREFS.get(str(user_id), {})
            keyboard = _main_keyboard(_p.get("tts_enabled", False),
                                      _p.get("model", DEFAULT_MODEL), new_effort)
            await update.message.reply_text(
                f"🔄 Vorgemerkt: Denke nach {effort_label} gilt ab der nächsten Aufgabe — "
                "die laufende wird noch im bisherigen Modus fertiggestellt.",
                reply_markup=keyboard,
            )
            return
        # Leerlauf: Session sofort neu starten (effort ist ein Session-Start-Parameter)
        await close_session(user_id)
        new_sess = await ensure_session(user_id)
        keyboard = _main_keyboard(new_sess.tts_enabled, new_sess.current_model, new_sess.current_effort)
        await update.message.reply_text(
            f"Denke nach: {effort_label} aktiv. Session neu gestartet.",
            reply_markup=keyboard,
        )
        return

    # --- STT-Tempo-Button (Voice-Transkription genau/flott) ---
    if text in _STT_BTN_TARGET:
        global _ACTIVE_STT
        want = _STT_BTN_TARGET[text]
        sess = SESSIONS.get(user_id)
        _p = _USER_PREFS.get(str(user_id), {})
        tts_on = sess.tts_enabled if sess else _p.get("tts_enabled", False)
        cur_model = sess.current_model if sess else _p.get("model", DEFAULT_MODEL)
        cur_effort = sess.current_effort if sess else _p.get("effort")
        kb = lambda: _main_keyboard(tts_on, cur_model, cur_effort)
        if want not in _STT_MODELS:
            await update.message.reply_text(
                f"🎙️ Modell „{want}“ ist auf dem Server nicht installiert.", reply_markup=kb())
            return
        if _ACTIVE_STT == want:
            await update.message.reply_text(
                f"🎙️ {_stt_label(want)} ist bereits aktiv.", reply_markup=kb())
            return
        old = _ACTIVE_STT
        _ACTIVE_STT = want
        _USER_PREFS.setdefault(str(user_id), {})["stt_model"] = want
        _save_prefs(_USER_PREFS)
        hint = ("präziser, etwas langsamer" if want == "medium"
                else "~2× schneller, etwas ungenauer")
        # Bestätigung mit gefettetem NEUEN Zustand (Adam 23.07.): auf einen Blick
        # erkennbar, „was gerade Phase ist" — der Rest beschreibt den Übergang.
        await update.message.reply_text(
            f"🎙️ {_stt_label(old)} → <b>{_stt_label(want)}</b> — jetzt aktiv: "
            f"<b>{_stt_label(want)}</b> ({hint}). Gilt ab der nächsten Sprachnachricht.",
            reply_markup=kb(), parse_mode=ParseMode.HTML)
        return

    # --- Info-Button ---
    if text == _BTN_INFO:
        sess = SESSIONS.get(user_id)
        mb = MAILBOXES.get(user_id)
        today = _usage_today()

        # Aktuelle Werte: aus Session wenn aktiv, sonst aus gespeicherten Prefs
        if sess:
            active_model = sess.current_model
            active_effort = sess.current_effort
            active_tts = sess.tts_enabled
        else:
            _p = _USER_PREFS.get(str(user_id), {})
            active_model = _p.get("model", DEFAULT_MODEL)
            active_effort = _p.get("effort", None)
            active_tts = _p.get("tts_enabled", False)

        model_str = _model_btn_label(active_model)
        effort_str = {None: "⚖️ Normal", "low": "⚡ Schnell", "max": "🚀 Max"}.get(active_effort, "⚖️ Normal")
        tts_str = "🔊 an" if active_tts else "🔇 aus"

        lines: list[str] = ["ℹ️ Systemstatus", ""]
        lines.append(f"Modell: {model_str}  ·  Denken: {effort_str}  ·  TTS: {tts_str}")

        if sess:
            elapsed_min = int((time.monotonic() - sess.started_at) / 60)
            lines.append(f"Session läuft seit: {elapsed_min} Min.")
        else:
            lines.append("Session: keine aktive")

        if mb and mb.current_job:
            lines.append("▶️ Läuft gerade")
        if mb and mb.queue:
            lines.append(f"⏳ Warteschlange: {len(mb.queue)}")

        if today:
            lines.append("")
            lines.append("📊 Bot-Verbrauch heute:")
            for mk, u in today.items():
                short = "Opus" if "opus" in mk else ("Haiku" if "haiku" in mk else "Sonnet")
                total = u.get("input", 0) + u.get("output", 0)
                reqs = u.get("requests", 0)
                cost = u.get("cost_usd", 0.0)
                cost_str = f"  ~${cost:.3f}" if cost else ""
                lines.append(f"  {short}: {total:,} Tok · {reqs} Anfragen{cost_str}")
        else:
            lines.append("")
            lines.append("📊 Noch kein Verbrauch heute")

        kb = _main_keyboard(
            sess.tts_enabled if sess else False,
            sess.current_model if sess else DEFAULT_MODEL,
            sess.current_effort if sess else None,
        )
        await update.message.reply_text("\n".join(lines), reply_markup=kb)
        return


async def on_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    if not _should_respond_in_chat(update):
        return
    text = update.message.text or ""
    if not text.strip():
        return
    if text.strip() in _ALL_KEYBOARD_BTNS:
        # Tastatur-Button bricht einen laufenden Ampel-Erfassungsmodus ab.
        _AMPEL_CAPTURE.pop(update.effective_user.id, None)
        await _handle_keyboard_btn(update, text.strip())
        return

    # Ampel-Erfassungsmodus (/ampel → ➕): nächste Nachricht wird DETERMINISTISCH
    # als Regel übernommen — geht NIE an Claude, zählt NICHT als normale Nachricht.
    cap = _AMPEL_CAPTURE.pop(update.effective_user.id, None)
    if cap is not None:
        if time.time() > cap["expires"]:
            await update.message.reply_text(
                "⌛ Erfassungsmodus abgelaufen — bitte /ampel → ➕ Neue Regel erneut."
            )
            return
        raw = text.strip()
        label, pattern = "manuell", raw
        if ":" in raw:
            lbl, pat = raw.split(":", 1)
            if pat.strip():
                label, pattern = (lbl.strip() or "manuell"), pat.strip()
        await update.message.reply_text(ampel.add_rule(cap["color"], pattern, label))
        return

    prefix = _extract_reply_context(update)
    await process_user_text(update, prefix + text)


async def on_voice(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    if not _should_respond_in_chat(update):
        return
    msg = update.message
    voice = msg.voice or msg.audio
    if voice is None:
        return

    # 5.2 LÜCKE GESCHLOSSEN (Befund 20.07.): Bis hierher war eine Sprachnachricht
    # durch NICHTS geschützt. Der Persistenz-Eintrag entstand erst in
    # process_user_text — also NACH Download und Transkription. Mit Whisper-medium
    # sind das rund 25 Sekunden, in denen ein Neustart oder Absturz die Nachricht
    # spurlos verschluckt: kein Eintrag, also auch kein Nachholen durch den
    # Reconcile, keine Fehlermeldung, nichts. Genau diese Stille hat Adam am
    # 20.07. erlebt (und schon einmal am 23.06., s. _request_restart_confirm).
    # Deshalb wird der Eingang jetzt SOFORT festgehalten — mit Platzhaltertext und
    # Stufenmarke. Gelingt die Transkription, überschreibt process_user_text
    # denselben Schlüssel mit dem echten Text; scheitert sie, wird der Eintrag in
    # den Fehlerzweigen unten aufgelöst. Bleibt er liegen, weiß der Reconcile beim
    # nächsten Start, dass hier eine Sprachnachricht unterwegs war.
    _vkey: str | None = None
    try:
        if msg.message_id is not None:
            _vkey = pending.make_key(msg.chat_id, msg.message_id)
            pending.record(_vkey, {
                "user_id": update.effective_user.id,
                "chat_id": msg.chat_id,
                "message_id": msg.message_id,
                "thread_id": getattr(msg, "message_thread_id", None),
                "text": VOICE_STAGE_PLACEHOLDER,
                "stage": VOICE_STAGE,
                "voice_duration": getattr(voice, "duration", None),
                "received_at": time.time(),
                "message_date": (msg.date.timestamp() if msg.date else None),
            })
    except Exception:
        log.exception("5.2 Voice-Eingang nicht persistierbar (nicht-fatal)")

    log.info("Sprachnachricht empfangen: user=%s msg=%s dauer=%ss — Eingang gesichert (%s)",
             update.effective_user.id, msg.message_id,
             getattr(voice, "duration", "?"), _vkey or "ohne Schlüssel")

    # Telegram "voice" notes are OGG/Opus, "audio" can be anything ffmpeg understands.
    await msg.reply_chat_action("typing")
    try:
        tg_file = await _with_one_retry(voice.get_file, "voice get_file")
    except Exception as e:
        log.exception("get_file failed")
        _log_bot_error("voice get_file (endgültig)", e)
        _resolve_voice_stage(_vkey)
        await msg.reply_text(f"❌ Konnte Sprachnachricht nicht laden: {e}")
        return

    # Audio dauerhaft in UPLOAD_DIR sichern statt nur temporär — so bleiben auch
    # unbearbeitete/ältere Sprachnachrichten auffindbar und nachträglich transkribierbar.
    suffix = Path(tg_file.file_path or "x.ogg").suffix or ".ogg"
    try:
        src = await _with_one_retry(
            lambda: _download_tg_file(tg_file, "voice" + suffix), "voice download")
    except Exception as e:
        log.exception("voice download failed")
        _log_bot_error("voice download (endgültig)", e)
        _resolve_voice_stage(_vkey)
        await msg.reply_text(f"❌ Download fehlgeschlagen: {e}")
        return

    # Audio-Pfad nachtragen: Geht der Bot jetzt unter, kann die Sprachnachricht
    # nachträglich aus der gesicherten Datei geholt werden — der Reconcile nennt
    # sie beim nächsten Start.
    _note_voice_audio(_vkey, src)

    try:
        transcriber = get_transcriber()
    except Exception as e:
        log.exception("transcriber init failed")
        _resolve_voice_stage(_vkey)
        await msg.reply_text(f"❌ STT nicht konfiguriert: {e}")
        return

    # Aktuell gewähltes STT-Modell anwenden (Umschalter 🎙️ Genau/Flott)
    try:
        if hasattr(transcriber, "set_model") and _ACTIVE_STT in _STT_MODELS:
            transcriber.set_model(_STT_MODELS[_ACTIVE_STT])
    except Exception:
        log.exception("STT-Modellwahl fehlgeschlagen — nutze Default")

    try:
        text = await transcriber.transcribe(src, language=VOICE_LANGUAGE)
    except Exception as e:
        log.exception("transcription failed")
        _resolve_voice_stage(_vkey)
        await msg.reply_text(f"❌ Transkription fehlgeschlagen: {e}")
        return

    text = (text or "").strip()
    if not text:
        _resolve_voice_stage(_vkey)
        await msg.reply_text("❌ Konnte nichts verstehen — bitte nochmal.")
        return

    # Transkription für /ttsdemo merken
    _LAST_TRANSCRIPTION[update.effective_user.id] = text

    # Echo so user sees what was understood before Claude starts.
    # Als Reply auf die Sprachnachricht selbst, damit der Bezug klar ist.
    echo_msg = None
    try:
        echo_msg = await send_chunked(msg.get_bot(), msg.chat_id, f"🎙️ {text}", reply_to=msg.message_id)
    except Exception:
        log.exception("voice echo failed (ignored)")
    prefix = _extract_reply_context(update)
    # Antwort + TTS sollen auf die lesbare Transkription zeigen, nicht auf das Audio.
    reply_override = echo_msg.message_id if echo_msg is not None else None
    _dur = getattr(voice, "duration", None)
    _note = (f"🎙️ Sprachnachricht ({_dur // 60}:{_dur % 60:02d})"
             if isinstance(_dur, int) else "🎙️ Sprachnachricht")
    await process_user_text(update, prefix + text, reply_to_override=reply_override,
                            log_note=_note)


async def on_photo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    if not _should_respond_in_chat(update):
        return
    msg = update.message
    caption = (msg.caption or "").strip()
    prefix = _extract_reply_context(update)

    await msg.reply_chat_action("upload_photo")
    try:
        tg_file = await msg.photo[-1].get_file()  # letztes = höchste Auflösung
        local_path = await _download_tg_file(tg_file, "photo.jpg")
    except Exception as e:
        log.exception("photo download failed")
        await msg.reply_text(f"❌ Bild-Download fehlgeschlagen: {e}")
        return

    parts = [f"[Bild hochgeladen: {local_path}]"]
    if caption:
        parts.append(f"Beschriftung: {caption}")
    await process_user_text(update, prefix + "\n".join(parts),
                            log_note=f"📷 Foto: {local_path.name}")


async def on_document(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    if not _should_respond_in_chat(update):
        return
    msg = update.message
    doc = msg.document
    caption = (msg.caption or "").strip()
    prefix = _extract_reply_context(update)

    filename = doc.file_name or f"document_{doc.file_unique_id}"
    mime = doc.mime_type or "application/octet-stream"
    size_mb = (doc.file_size or 0) / 1_048_576

    if (doc.file_size or 0) > 20 * 1_048_576:
        await msg.reply_text(
            f"❌ Datei zu groß ({size_mb:.1f} MB) — Telegram Bot API erlaubt max. 20 MB."
        )
        return

    await msg.reply_chat_action("upload_document")
    try:
        tg_file = await doc.get_file()
        local_path = await _download_tg_file(tg_file, filename)
    except Exception as e:
        log.exception("document download failed")
        await msg.reply_text(f"❌ Datei-Download fehlgeschlagen: {e}")
        return

    parts = [
        f"[Datei hochgeladen: {local_path}]",
        f"Dateiname: {filename}",
        f"Typ: {mime}",
    ]
    if caption:
        parts.append(f"Beschriftung: {caption}")

    # Bei lesbaren Dokumenten ohne Beschriftung: immer fragen ob Zusammenfassung oder Vorlesen
    user_id = update.effective_user.id
    is_readable = mime in ("application/pdf", "text/plain", "application/msword",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    if is_readable and not caption:
        _PENDING_DOCS[user_id] = {
            "parts": parts,
            "prefix": prefix,
            "update": update,
            "filename": filename,
            "size_mb": size_mb,
            "local_path": str(local_path),
        }
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Zusammenfassen", callback_data=f"pdf:{user_id}:summary"),
                InlineKeyboardButton("Komplett vorlesen", callback_data=f"pdf:{user_id}:full"),
            ],
            [InlineKeyboardButton("Kurzfassung anhören",
                                  callback_data=f"pdf:{user_id}:summary_voice")],
        ])
        await msg.reply_text(
            f"{filename} ({size_mb:.1f} MB) empfangen.\nWie soll ich vorgehen?",
            reply_markup=keyboard,
        )
        return

    await msg.reply_text(f"{filename} ({size_mb:.1f} MB) empfangen — weiterleiten …")
    await process_user_text(update, prefix + "\n".join(parts),
                            log_note=f"📎 Datei: {filename} · {mime} · {size_mb:.1f} MB")


async def on_video(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    if not _should_respond_in_chat(update):
        return
    msg = update.message
    is_note = msg.video_note is not None
    media = msg.video_note if is_note else msg.video
    caption = (msg.caption or "").strip()
    prefix = _extract_reply_context(update)

    filename = getattr(media, "file_name", None) or \
        f"{'videonote' if is_note else 'video'}_{media.file_unique_id}.mp4"
    size_mb = (media.file_size or 0) / 1_048_576

    if (media.file_size or 0) > 20 * 1_048_576:
        await msg.reply_text(
            f"❌ Video zu groß ({size_mb:.1f} MB) — Telegram Bot API erlaubt max. 20 MB."
        )
        return

    await msg.reply_chat_action("upload_video")
    try:
        tg_file = await media.get_file()
        local_path = await _download_tg_file(tg_file, filename)
    except Exception as e:
        log.exception("video download failed")
        await msg.reply_text(f"❌ Video-Download fehlgeschlagen: {e}")
        return

    label = "Video-Notiz" if is_note else "Video"
    parts = [f"[{label} hochgeladen: {local_path}]"]
    if not is_note:
        parts.append(f"Dateiname: {filename}")
    if caption:
        parts.append(f"Beschriftung: {caption}")
    await msg.reply_text(f"🎬 {label} ({size_mb:.1f} MB) empfangen — weiterleiten …")
    await process_user_text(update, prefix + "\n".join(parts),
                            log_note=f"🎬 {label}: {filename} · {size_mb:.1f} MB")


# Gängige Abkürzungen für die Sprachausgabe ausschreiben — sonst liest edge-tts
# "bzw Punkt". Mehrteilige (z. B. "i. d. R.") zuerst, damit kürzere nicht vorgreifen.
# Einbuchstabige/mehrdeutige Kürzel ("n.", "min.", "S." ohne Zahl) bewusst NICHT
# auflösen, weil ihre Bedeutung vom Kontext abhängt und Fehldeutungen riskiert.
_TTS_ABBREVIATIONS: list[tuple[str, str]] = [
    (r"i\.\s*d\.\s*R\.", "in der Regel"),
    (r"u\.\s*v\.\s*m\.", "und vieles mehr"),
    (r"z\.\s*B\.", "zum Beispiel"),
    (r"d\.\s*h\.", "das heißt"),
    (r"u\.\s*a\.", "unter anderem"),
    (r"u\.\s*U\.", "unter Umständen"),
    (r"z\.\s*T\.", "zum Teil"),
    (r"o\.\s*ä\.", "oder ähnliches"),
    (r"s\.\s*o\.", "siehe oben"),
    (r"s\.\s*u\.", "siehe unten"),
    (r"bzw\.", "beziehungsweise"),
    (r"ggf\.", "gegebenenfalls"),
    (r"usw\.", "und so weiter"),
    (r"etc\.", "und so weiter"),
    (r"evtl\.", "eventuell"),
    (r"inkl\.", "inklusive"),
    (r"exkl\.", "exklusive"),
    (r"bzgl\.", "bezüglich"),
    (r"vgl\.", "vergleiche"),
    (r"sog\.", "sogenannt"),
    (r"ca\.", "circa"),
    (r"max\.", "maximal"),
    (r"Mio\.", "Millionen"),
    (r"Mrd\.", "Milliarden"),
    (r"Nr\.", "Nummer"),
    (r"Abb\.", "Abbildung"),
    (r"Kap\.", "Kapitel"),
    (r"S\.\s*(?=\d)", "Seite "),  # nur "S." direkt vor einer Zahl → Seite
]


def _expand_abbreviations(text: str) -> str:
    """Schreibt gängige deutsche Abkürzungen für die Sprachausgabe aus."""
    import re
    for pat, repl in _TTS_ABBREVIATIONS:
        text = re.sub(r"\b" + pat, repl, text, flags=re.IGNORECASE)
    return text


def _chunk_snippet(text: str, max_len: int = 60) -> str:
    """Kurzer Einstiegs-Ausschnitt als Orientierung, wenn ein Abschnitt keinen Titel hat."""
    s = " ".join(text.split())
    if len(s) <= max_len:
        return s.rstrip(".,;:!? ")
    cut = s.rfind(" ", 0, max_len)
    if cut < max_len // 2:
        cut = max_len
    return s[:cut].rstrip(".,;:!? ")


# Aussprache-Wörterbuch für hartnäckige Mixed-Case-/Englisch-Begriffe, die edge-tts
# auch mit Multilingual-Stimme falsch ausspricht (z.B. „Sync" als Akronym buchstabiert).
# Phonetisch deutsch geschriebene Ersatzform → klingt sauber. Bei Bedarf erweitern.
TTS_PRONUNCIATION = {
    "Sync": "Synk",
    "sync": "synk",
}


def _apply_tts_pronunciation(text: str) -> str:
    """Wörterbuch-Ersetzung für hartnäckige Aussprachefälle vor TTS."""
    import re
    for src, repl in TTS_PRONUNCIATION.items():
        text = re.sub(rf"\b{re.escape(src)}\b", repl, text)
    return text


def _normalize_number_ranges(text: str) -> str:
    """Zahlen mit Bindestrich für TTS sinngemäß umschreiben:
    - Sport-Kontext (Endstand/Spielstand/Sieg/Halbzeit/...) → 'zu':
      'Endstand 3-1' → '3 zu 1' (deutsches Sportergebnis)
    - sonst kleinere vorn → 'bis' (Bereich): '2-3' → '2 bis 3'
    - sonst größere vorn → 'minus' (Rechnung): '3-2' → '3 minus 2'
    Em-Dash (—) wird absichtlich NICHT behandelt – er ist im Alltag fast
    nie ein Operator, sondern Gedankenstrich. Jahreszahlen (>= 1000)
    werden nie als Sportergebnis gelesen, damit 'Saison 2022-2023'
    nicht 'Saison 2022 zu 2023' wird.
    """
    import re
    sport_re = re.compile(
        r"\b(endstand|spielstand|halbzeit(?:stand)?|pausenstand|"
        r"ergebnis|spielergebnis|resultat|schlussstand|"
        r"gewinnt|gewann|gewonnen|siegt|siegte|schl[aä]gt|schlug|schlugen|"
        r"besiegt|besiegte|verlor|verloren|verliert|unterlag|unterlegen|"
        r"sieg|niederlage|remis|unentschieden|"
        r"tor|tore|treffer|match|partie|spiel|begegnung|"
        r"halbfinale|viertelfinale|achtelfinale|finale|pokal|"
        r"bundesliga|liga|saison)\b",
        re.IGNORECASE,
    )

    def repl(m):
        a, b = int(m.group(1)), int(m.group(2))
        # Satz-Fenster für Kontext-Suche (Trenner: . ! ? \n)
        start, end = m.start(), m.end()
        seg_start = max(
            text.rfind(".", 0, start),
            text.rfind("!", 0, start),
            text.rfind("?", 0, start),
            text.rfind("\n", 0, start),
        ) + 1
        ends = [p for p in (text.find(c, end) for c in ".!?\n") if p != -1]
        seg_end = min(ends) if ends else len(text)
        sentence = text[seg_start:seg_end]
        # Jahreszahlen ausschließen, sonst Sport-Kontext prüfen
        if a < 1000 and b < 1000 and sport_re.search(sentence):
            return f"{a} zu {b}"
        if a < b:
            return f"{a} bis {b}"
        return f"{a} minus {b}"

    return re.sub(r"(\d+)\s*[-–]\s*(\d+)", repl, text)


def _normalize_versions(text: str) -> str:
    """'Python 3.12' → 'Python 3 Punkt 12' (sonst liest TTS '3 Uhr 12').
    Datum (22.06.2026), bereits getrennte Zahlen und Uhrzeit-Indikatoren
    (Uhr / nachgestelltes h) werden ausgelassen.
    """
    import re
    return re.sub(
        r"(?<![\d.])(\d+)\.(\d+)(?![\d.])(?!\s*(?:Uhr\b|h\b))",
        r"\1 Punkt \2",
        text,
    )


def _strip_markdown_for_tts(text: str) -> str:
    """Entfernt Markdown-Formatierungszeichen und Emojis für saubere TTS-Ausgabe."""
    import re
    # Vorab: Aussprache-Wörterbuch + Zahlen-Bindestrich-Regel + Versionsnummern
    text = _apply_tts_pronunciation(text)
    text = _normalize_number_ranges(text)
    text = _normalize_versions(text)
    # Code-Blöcke werden NICHT zeichengenau vorgelesen, sondern durch eine
    # knappe Inhaltsbeschreibung ersetzt. Sprache aus dem Fence-Hinweis
    # (z.B. ```bash) wird übernommen, um die Beschreibung treffsicherer zu
    # machen. Adam 2026-06-22: „Das artet komplett aus".
    def _describe_code_block(m):
        lang = (m.group(1) or "").strip().lower()
        lang_map = {
            "bash": "im Terminal",
            "sh": "im Terminal",
            "shell": "im Terminal",
            "zsh": "im Terminal",
            "python": "in Python",
            "py": "in Python",
            "json": "im JSON-Format",
            "yaml": "im YAML-Format",
            "yml": "im YAML-Format",
            "toml": "im TOML-Format",
            "markdown": "in Markdown",
            "md": "in Markdown",
        }
        suffix = lang_map.get(lang, "")
        if suffix:
            return f" Es folgt ein Codeblock {suffix}. "
        return " Es folgt ein Codeblock. "
    text = re.sub(r"```(\w*)[^\n]*\n.*?```", _describe_code_block, text, flags=re.DOTALL)
    # Inline-Code: Backticks entfernen, kurze Tokens bleiben als Wort. Lange
    # oder Pfad-/Sonderzeichen-lastige Inhalte werden komplett entfernt, weil
    # sie sonst zeichenweise gelesen werden.
    def _inline_code(m):
        inner = m.group(1)
        if "/" in inner or len(inner) > 24:
            return ""
        return inner
    text = re.sub(r"`([^`]+)`", _inline_code, text)
    # Wikilinks [[name]] (interne Memory-Verweise) komplett raus — Slugs wie
    # "telegram-bot-project" haben in der Sprachausgabe keinen Mehrwert.
    text = re.sub(r"\[\[[^\]]+\]\]", "", text)
    # Markdown-Links [Titel](url) komplett raus — Titel sind meist Quellen-/
    # Linkverweise (Adam: "Internet-Links, die nun nicht vorliegen") und stören
    # den Sprachfluss. Runde Klammern mit erklärendem Inhalt bleiben unberührt.
    text = re.sub(r"\[[^\]]+\]\([^)]*\)", "", text)
    # Nackte URLs vor der Pfad-Regel entfernen — sonst frisst die Pfad-Regex den
    # Mittelteil (etwa "//example.com/a/b/c") und lässt das Schema "https:" plus
    # eventuelle Query-Reste ("?d=1") als Müll stehen.
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\bwww\.\S+", "", text)
    # Datei- und Ordnerpfade (führendes ~/, /, ./, ../) durch eine generische
    # Bezeichnung ersetzen, statt jeden Schrägstrich vorzulesen.
    text = re.sub(
        r"(?<![\w/])(?:~/|\.{1,2}/|/)[\w./~\-]+",
        " ein Datei-Pfad ",
        text,
    )
    # Lange ID-/Hash-Ketten (UUIDs, Hex) nicht vorlesen
    text = re.sub(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{8,}\b", "", text)
    # Abkürzungen ausschreiben (vor dem Satz-Splitting, damit "z.B." keine
    # falsche Satzgrenze erzeugt)
    text = _expand_abbreviations(text)
    # Fett (**text** und __text__)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    # Kursiv (*text* und _text_)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    text = re.sub(r"_([^_\n]+)_", r"\1", text)
    # Überschriften (# am Zeilenanfang): Marker entfernen, mit Punkt + Absatz
    # abschließen, damit die Stimme danach eine echte Pause macht statt nahtlos
    # in den Fließtext zu rutschen.
    def _md_heading_pause(m):
        h = m.group(1).strip().rstrip(":")
        if h and h[-1] not in ".!?":
            h += "."
        return "\n\n" + h + "\n\n"
    text = re.sub(r"^#{1,6}[ \t]+(.+?)[ \t]*$", _md_heading_pause, text, flags=re.MULTILINE)
    # Aufzählungszeichen (-, *, + am Zeilenanfang)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Nummerierte Listen: Nummer als gesprochenes Aufzählungswort vorlesen,
    # damit Struktur hörbar bleibt ("1. Foo" → "Erstens. Foo"). Sonst verliert
    # eine Liste in der Sprachausgabe ihre Gliederung und klingt wie ein
    # zusammenhangloser Wortfluss.
    _list_num_words = {
        1: "Erstens", 2: "Zweitens", 3: "Drittens", 4: "Viertens",
        5: "Fünftens", 6: "Sechstens", 7: "Siebtens", 8: "Achtens",
        9: "Neuntens", 10: "Zehntens",
    }
    def _spoken_list_num(m):
        n = int(m.group(1))
        return f"{_list_num_words.get(n, f'Punkt {n}')}. "
    text = re.sub(r"^\s*(\d+)\.\s+", _spoken_list_num, text, flags=re.MULTILINE)
    # Pfeile, Gedankenstriche und Sonderzeichen
    text = text.replace("→", ",").replace("->", ",").replace("=>", ",")
    text = text.replace("←", "").replace("<-", "")
    text = text.replace("—", ",").replace("–", ",").replace("~", "")
    text = text.replace("✅", "").replace("⬜", "").replace("❌", "").replace("⚠", "")
    # Tabellen-Pipes und Trennzeilen
    text = re.sub(r"^\s*\|.*\|\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-|:]+\s*$", "", text, flags=re.MULTILINE)
    # Alle Emojis entfernen (Unicode Emoji-Ranges)
    text = re.sub(
        r"[\U0001F600-\U0001F64F"  # Gesichter
        r"\U0001F300-\U0001F5FF"  # Symbole & Piktogramme
        r"\U0001F680-\U0001F6FF"  # Transport & Karte
        r"\U0001F700-\U0001F77F"  # Alchemische Symbole
        r"\U0001F780-\U0001F7FF"  # Geometrische Formen
        r"\U0001F800-\U0001F8FF"  # Supplemental Arrows
        r"\U0001F900-\U0001F9FF"  # Supplemental Symbole
        r"\U0001FA00-\U0001FA6F"  # Schach-Symbole
        r"\U0001FA70-\U0001FAFF"  # Symbole und Piktogramme erweitert
        r"\U00002702-\U000027B0"  # Dingbats
        r"\U000024C2-\U0001F251"  # Verschiedene Symbole
        r"]+",
        " ", text
    )
    # Typografisch gespaced-out Wörter zusammenführen (Human Design PDFs):
    # Thin-Space (U+2009) und En-Space (U+2002) zwischen Großbuchstaben entfernen
    _thin = " "
    _en   = " "
    upper = "A-ZÜÄÖ"
    text = re.sub(f"([{upper}])[{_thin}{_en}](?=[{upper}])", r"\1", text)
    # Reguläre Leerzeichen: Folge von 3+ einzelnen Großbuchstaben → zusammenführen
    # "H U M A N" → "HUMAN", aber "A B" (nur 2) bleibt unangetastet
    text = re.sub(
        r"(?<![A-ZÜÄÖ\w])([A-ZÜÄÖ])( [A-ZÜÄÖ]){2,}(?![A-ZÜÄÖ\w])",
        lambda m: m.group(0).replace(" ", ""),
        text,
    )
    # Gesperrt gesetzte Wörter mit Klein-/Gemischtschreibung zusammenführen:
    # "V o r b e r e i t u n g" → "Vorbereitung". Mind. 4 Buchstaben, damit kurze
    # Aufzählungen ("a b c") unberührt bleiben. Ein Doppel-Leerzeichen (Wortgrenze
    # im Sperrsatz) bricht die Folge → benachbarte Wörter bleiben getrennt.
    _ltr = "A-Za-zÀ-ÖØ-öø-ÿ"
    text = re.sub(
        rf"(?<![{_ltr}])([{_ltr}](?: [{_ltr}]){{3,}})(?![{_ltr}])",
        lambda m: m.group(1).replace(" ", ""),
        text,
    )
    # Am Zeilenende getrennte Wörter wieder zusammenfügen: "natür-\nlich" → "natürlich"
    # (fließend gelesen, keine Pause). Nur bei Kleinbuchstabe auf beiden Seiten =
    # echte Silbentrennung; Großbuchstabe danach = Kompositum ("Nord-\nSüd") → bleibt.
    text = re.sub(r"([a-zäöüß])-[ \t]*\n[ \t]*([a-zäöüß])", r"\1\2", text)
    # Eigenständige Überschriften-Zeilen (durch Leerzeile abgesetzt, kurz, ohne
    # Satzzeichen am Ende, gefolgt von Großbuchstabe) → Punkt + Absatz = Pause.
    def _plain_heading_pause(m):
        h = m.group(1).strip()
        if not h or h[-1] in ".!?:;,–-":
            return m.group(0)
        if len(h) > 60 or len(h.split()) > 8:
            return m.group(0)
        return "\n\n" + h + ".\n\n"
    text = re.sub(r"(?<=\n\n)([^\n]{1,60})\n(?=[A-ZÄÖÜ])", _plain_heading_pause, text)
    # Einzelne Zeilenumbrüche dürfen kein Satzende erzeugen: edge-tts senkt sonst
    # an JEDEM Zeilenende die Stimme, als wäre der Satz vorbei – auch wenn dort kein
    # Satzzeichen steht. Die Prosodie soll sich nach Punkt/Komma richten, nicht nach
    # dem Umbruch. Darum einzelne Umbrüche zu Leerzeichen machen; nur echte Absätze
    # (Leerzeile) als Pause behalten.
    text = re.sub(r"\n{2,}", " ", text)        # Absätze vormerken
    text = re.sub(r"[ \t]*\n[ \t]*", " ", text)     # einzelne Umbrüche → Leerzeichen
    text = text.replace(" ", "\n\n")           # Absätze wiederherstellen
    # Mehrfache Leerzeichen zusammenfassen
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _split_tts_chunks(text: str, max_chars: int = TTS_CHUNK_CHARS) -> list[str]:
    """Teilt Text an Satzgrenzen in Chunks für mehrere Sprachnachrichten."""
    import re
    if len(text) <= max_chars:
        return [text]
    # Trennpunkte: Absätze, dann Satzenden
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", "]
    chunks: list[str] = []
    remaining = text
    while len(remaining) > max_chars:
        cut = max_chars
        for sep in separators:
            pos = remaining.rfind(sep, 0, max_chars)
            if pos > max_chars // 2:  # nur sinnvolle Schnittstellen
                cut = pos + len(sep)
                break
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def _extract_pdf_text(path: Path) -> str:
    """Extrahiert den Text eines PDFs seitenweise via PyMuPDF."""
    import fitz, re
    doc = fitz.open(str(path))
    pages = [page.get_text() for page in doc]
    doc.close()
    text = "\n".join(pages)
    # Manche PDFs kodieren (dekorative) Überschriften mit NUL-Bytes zwischen den
    # Buchstaben ("V\x00O\x00R..."). Das lässt edge-tts jeden Buchstaben einzeln
    # vorlesen. C0-Steuerzeichen entfernen (außer \t und \n).
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", "", text)
    return text


def _normalize_spaced_text(text: str) -> str:
    """Normalisiert Unicode-gespaced-out-Überschriften für die Kapitel-Erkennung.

    Typografische PDFs kodieren Überschriften mit Thin-Spaces (U+2009) zwischen
    Buchstaben und En-Spaces (U+2002) zwischen Wörtern:
      - U+2009 zwischen Großbuchstaben entfernen  -> ERSTER
      - U+2002 zwischen Großbuchstaben -> Leerzeichen -> ERSTER TEIL
    """
    import re as _re
    _thin = "\u2009"  # THIN SPACE (U+2009)
    _en   = "\u2002"  # EN SPACE   (U+2002)
    upper = "A-Z\u00dc\u00c4\u00d6\u00dc"  # A-ZÜÄÖÜ
    result = _re.sub(f"([{upper}]){_thin}(?=[{upper}])", r"\1", text)
    result = _re.sub(f"([{upper}]){_en}(?=[{upper}])", r"\1 ", result)
    return result


import re as _re_mod

# Strukturierte Überschriften (hohe Sicherheit) — pro Zeile geprüft.
_STRUCT_HEADING_PATTERNS = [
    _re_mod.compile(
        r"^(?:ERSTER|ZWEITER|DRITTER|VIERTER|FÜNFTER|SECHSTER|SIEBTER|ACHTER|NEUNTER|ZEHNTER)"
        r"\s+(?:TEIL|ABSCHNITT|KAPITEL)\b"),
    _re_mod.compile(r"^(?:EINFÜHRUNG|EINLEITUNG|VORWORT|NACHWORT|ZUSAMMENFASSUNG|ANHANG)$"),
    _re_mod.compile(r"^(?:Teil|Kapitel|Chapter|Abschnitt|Section)\s+[\dIVXLivxl]+\b", _re_mod.IGNORECASE),
    _re_mod.compile(r"^\d{1,2}\.\s+[A-ZÄÖÜ]"),            # "1. Einleitung"
    _re_mod.compile(r"^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\s+\S"),  # "1.2 Unterabschnitt"
    _re_mod.compile(r"^#{1,3}\s+\S"),                     # Markdown
]


def _is_structural_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 80:
        return False
    return any(p.match(s) for p in _STRUCT_HEADING_PATTERNS)


def _clean_title(s: str) -> str:
    """Normalisiert eine Überschriftszeile für Caption und gesprochene Ausgabe.

    Gesperrt gesetzte Großbuchstaben-Titel ("T E I L E I N S") → Spaces raus →
    "TEILEINS", danach TEIL/KAPITEL/ABSCHNITT + Ordinalwort wieder trennen
    ("TEIL EINS"). Entfernt führende #/Aufzählungszeichen und Doppelpunkt am Ende.
    """
    s = s.strip().lstrip("#").strip()
    if _re_mod.fullmatch(r"(?:[A-ZÄÖÜ] )+[A-ZÄÖÜ]", s):
        s = s.replace(" ", "")
    s = _re_mod.sub(
        r"^(TEIL|KAPITEL|ABSCHNITT)(EINS|ZWEI|DREI|VIER|FÜNF|SECHS|SIEBEN|ACHT|NEUN|ZEHN|ELF|ZWÖLF)\b",
        r"\1 \2", s)
    return s.rstrip(":").strip()


def _is_heading_line(line: str, prev: str, nxt: str) -> bool:
    """Heuristik für kurze Title-Case-Überschriften ohne Nummerierung.

    Solche Überschriften ("Was Vipassana ist:", "Die Regeln") sind kurz, beginnen
    mit einem Großbuchstaben, enden NICHT mit Satz-/Umbruchzeichen, stehen hinter
    einem abgeschlossenen Satz (oder Seitenzahl) und vor neuem Fließtext. Bewusst
    streng, um Fließtext, Zeittabellen und Datumszeilen nicht zu zerstückeln.
    """
    s = line.strip()
    if not s or len(s) > 64:
        return False
    words = s.split()
    if not (1 <= len(words) <= 8):
        return False
    if s[-1] in ".,;–—-":          # Satzende oder Zeilenumbruch-Trennung → kein Titel
        return False
    if not s[0].isalpha() or not s[0].isupper():
        return False               # nur Buchstaben-Start (killt "04:00", "31.01.2020")
    if len(words) == 1 and s.lower().rstrip(":") in _GERMAN_STOPWORDS:
        return False
    p = prev.strip()
    if p and p[-1] not in ".:!?" and not p.isdigit():
        return False               # mitten im Absatz → kein Titel
    n = nxt.strip()
    if n and not (n[0].isupper() or n[0].isdigit() or n[0] in "•-*–"):
        return False               # nächster Block beginnt nicht neu → kein Titel
    return True


def _split_pdf_by_chapters(text: str) -> list[tuple[str, str]]:
    """Erkennt Kapitel/Abschnitte im PDF-Text. Gibt (Titel, Inhalt)-Paare zurück.

    Trennt bevorzugt an bereits vorhandenen Überschriften — sowohl strukturierten
    (Teil/Kapitel/Nummern/Markdown) als auch kurzen Title-Case-Abschnittstiteln.
    Die Überschrift bleibt im Inhalt (wird also mit vorgelesen) und gibt der
    Sprachnachricht ihren Namen. Lieber mehrere kleine Abschnitte als ein
    nummerierter Block. Findet < 2 Überschriften → Dokument am Stück zurück.
    """
    norm = _normalize_spaced_text(text)
    # Reine Seitenzahl-Zeilen (1–3-stellig) raus: verfälschen TTS und unterbrechen
    # die Überschriften-Erkennung (Titel steht oft direkt nach der Seitenzahl).
    lines = [ln for ln in norm.split("\n") if not _re_mod.fullmatch(r"\s*\d{1,3}\s*", ln)]

    heading_idx: list[int] = []
    for i, ln in enumerate(lines):
        prev = lines[i - 1] if i > 0 else ""
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if _is_structural_heading(ln) or _is_heading_line(ln, prev, nxt):
            heading_idx.append(i)

    if len(heading_idx) < 2:
        return [("Dokument", "\n".join(lines).strip())]

    raw: list[tuple[str, str]] = []
    preamble = "\n".join(lines[: heading_idx[0]]).strip()
    if len(preamble) > 200:
        pt = next((l.strip() for l in lines[: heading_idx[0]] if l.strip()), "Einleitung")
        raw.append((_clean_title(pt)[:64] or "Einleitung", preamble))
    for k, hi in enumerate(heading_idx):
        end = heading_idx[k + 1] if k + 1 < len(heading_idx) else len(lines)
        title = _clean_title(lines[hi])[:64] or "Abschnitt"
        # gesäuberte Überschrift in den Inhalt übernehmen (wird mitgelesen)
        body = "\n".join(lines[hi + 1:end]).strip()
        content = (title + ("\n\n" + body if body else "")).strip()
        raw.append((title, content))

    # Mini-Fragmente (z.B. Zeittabellen-Zeilen) in den vorigen Abschnitt falten,
    # damit aus einem Tagesablauf nicht 20 Sprachschnipsel werden.
    merged: list[tuple[str, str]] = []
    for title, content in raw:
        if merged and len(content) < 40:
            pt, pc = merged[-1]
            merged[-1] = (pt, (pc + "\n\n" + content).strip())
        else:
            merged.append((title, content))
    return merged or [("Dokument", "\n".join(lines).strip())]


_GERMAN_STOPWORDS = {
    "der", "die", "das", "und", "oder", "aber", "ein", "eine", "einen", "einem",
    "einer", "eines", "ich", "auch", "schon", "noch", "nur", "sehr", "mehr",
    "sich", "uns", "mein", "dein", "sein", "ihre", "ihren", "ihrem", "seine",
    "seinen", "seinem", "ist", "sind", "war", "waren", "wird", "werden", "hat",
    "habe", "haben", "hatte", "hatten", "kann", "koennen", "können", "muss",
    "muessen", "müssen", "soll", "sollen", "wollen", "wuerde", "würde", "im",
    "den", "dem", "des", "als", "wenn", "dann", "weil", "dass", "wie", "was",
    "wer", "wann", "nicht", "kein", "keine", "man", "diese", "dieser", "dieses",
    "alle", "allen", "aller", "wieder", "immer", "hier", "dort", "etwas", "wird",
    "ueber", "über", "unter", "durch", "fuer", "für", "gegen", "ohne", "von",
    "vor", "nach", "bei", "mit", "aus", "auf", "zur", "zum", "selbst", "schon",
}


def _section_topic_label(text: str, max_words: int = 5) -> str:
    """Lokales Kurz-Thema (1-max_words Wörter) aus den häufigsten Schlüsselwörtern.

    Komplett lokal — kein Datenabfluss, auch für sensible (rote) PDFs sicher.
    Liefert "" wenn kein sinnvolles Wort gefunden wird.
    """
    import re
    words = re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", text)
    counts: dict[str, int] = {}
    order: list[str] = []
    for w in words:
        lw = w.lower()
        if lw in _GERMAN_STOPWORDS:
            continue
        if lw not in counts:
            order.append(w)
        counts[lw] = counts.get(lw, 0) + 1
    if not order:
        return ""
    ranked = sorted(order, key=lambda w: (-counts[w.lower()], order.index(w)))
    top = ranked[:max_words]
    top.sort(key=lambda w: order.index(w))  # Lesereihenfolge wiederherstellen
    return " ".join(top)


def _caption_topic(chunk_clean: str, max_words: int = 7) -> str:
    """Knappe, in sich sinnvolle Überschrift für die Caption — bevorzugt die
    Überschrift des Abschnitts selbst.

    Nimmt den ersten Absatz des (bereits TTS-bereinigten) Chunks, wenn er kurz
    genug ist (≤ max_words Wörter) → das ist nach der Überschriften-Pausen-Logik
    in _strip_markdown_for_tts typischerweise genau die Überschrift. Liefert ""
    wenn keine knappe Überschrift erkennbar ist (dann lieber gar nichts anhängen).
    Komplett lokal, kein Datenabfluss.
    """
    first_para = chunk_clean.split("\n\n", 1)[0].strip()
    first_para = first_para.split("\n", 1)[0].strip()
    label = first_para.rstrip(".!?:;, ").strip()
    if not label:
        return ""
    words = label.split()
    if 1 <= len(words) <= max_words:
        return label
    return ""


# ---------- Neben-Inferenzen über LiteLLM (2.6, F1-Leitplanke) ----------
# Kleine Hilfs-Inferenzen (Kapitel-Labels etc.) laufen über den lokalen
# LiteLLM-Proxy (→ Ollama/Phi-4-Mini), NICHT über den Claude-Agenten/das Abo.
LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "http://127.0.0.1:4000")
LITELLM_LOCAL_MODEL = os.environ.get("LITELLM_LOCAL_MODEL", "local")


async def _litellm_complete(user: str, system: str = "", max_tokens: int = 256,
                            model: str | None = None) -> str:
    """Neben-Inferenz über den lokalen LiteLLM-Proxy. Nie der Haupt-Agent.

    Fällt bei JEDEM Fehler still auf "" zurück — Neben-Inferenzen dürfen den Bot
    nie blockieren. Rote Daten haben hier ohnehin nichts verloren (Aufrufer prüfen).
    """
    import httpx
    msgs: list[dict] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": user})
    payload = {
        "model": model or LITELLM_LOCAL_MODEL,
        "messages": msgs,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    try:
        async with httpx.AsyncClient(timeout=90) as c:
            r = await c.post(f"{LITELLM_BASE_URL}/v1/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
            return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        log.exception("LiteLLM-Neben-Inferenz fehlgeschlagen")
        return ""


async def _ai_topic_label(text: str, max_words: int = 7) -> str:
    """Kurzes Inhalts-Thema (3-7 Wörter) für einen Abschnitt — via lokales Modell
    (LiteLLM/Ollama, 2.6), NICHT über das Abo. Still auf "" bei jedem Fehler,
    damit das Vorlesen nie blockiert.
    """
    system = (
        "Du benennst das Hauptthema eines Textabschnitts in 3 bis 7 deutschen "
        "Wörtern — wie eine knappe, in sich abgeschlossene Kapitelüberschrift, "
        "die den Inhalt erkennbar macht und nicht abgeschnitten wirkt. Gib NUR "
        "die Überschrift aus, ohne Anführungszeichen und ohne Satzzeichen am Ende."
    )
    out = await _litellm_complete(
        user=f"Worum geht es in diesem Abschnitt?\n\n{text[:2000]}",
        system=system, max_tokens=24,
    )
    label = " ".join(out.split()).strip(' "„“.')
    if not label:
        return ""
    words = label.split()
    return " ".join(words[:max_words]) if len(words) > max_words else label


async def _send_pdf_chapters_tts(
    bot,
    chat_id: int,
    target_id: int,
    filename: str,
    chapters: list[tuple[str, str]],
    channel_post_id: int | None = None,
) -> None:
    """Sendet PDF kapitelweise als Sprachnachrichten. target_id = Kanal oder Chat."""
    if target_id != chat_id:
        cid, ch_title, _ = get_output_channel()
        username = _USER_PREFS.get("output_channel_username")
        await bot.send_message(
            chat_id=chat_id,
            text=f"Lese {filename} in {len(chapters)} Kapitel(n) vor — Sprachnachrichten gehen in {ch_title or 'Ausgabekanal'}.",
            reply_markup=_channel_post_markup(cid or target_id, channel_post_id, username),
        )
    total = len(chapters)
    stem = Path(filename).stem.strip()
    # Kein erkanntes Kapitel → jede Sprachnachricht ist ein nummerierter Teil des Ganzen.
    single_blob = total == 1 and chapters[0][0] == "Dokument"
    for i, (title, content) in enumerate(chapters, 1):
        clean = _strip_markdown_for_tts(content)
        if not clean.strip():
            continue

        chunks = _split_tts_chunks(clean)
        n = len(chunks)
        for j, chunk in enumerate(chunks, 1):
            # Caption beginnt IMMER mit dem Dateititel → alphabetisch sortierbar,
            # Herkunft sofort erkennbar.
            if single_blob:
                # Ohne erkennbare Überschriften (reiner Fließtext): Teil j/n +
                # knappe Überschrift — bevorzugt der Abschnittsanfang (lokal),
                # sonst KI-Thema, sonst nichts.
                topic = _caption_topic(chunk)
                if not topic:
                    topic = await _ai_topic_label(chunk)
                cap = f"{stem} {j:02d}/{n}" + (f" — {topic}" if topic else "")
            else:
                # Mit Überschrift: nullgepolsterte Reihenfolge (alphabetisch =
                # chronologisch) + echte Überschrift; geteilter Abschnitt → "(j/n)".
                base = f"{stem} {i:02d} — {title}"
                cap = base if n == 1 else f"{base} ({j}/{n})"
            await _send_tts_chunk(bot, target_id, chunk, caption=cap)


async def _send_tts_chunk(
    bot, chat_id: int, chunk: str, caption: str | None = None, reply_to: int | None = None,
    thread_id: int | None = None, reply_markup=None,
):
    """Generiert und sendet einen einzelnen TTS-Chunk als Telegram-Voice.
    Gibt das gesendete Message-Objekt zurück (oder None bei Fehler)."""
    import edge_tts
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = Path(f.name)
    try:
        communicate = edge_tts.Communicate(chunk, TTS_VOICE)
        await communicate.save(str(tmp_path))
        with tmp_path.open("rb") as audio:
            sent = await bot.send_voice(
                chat_id=chat_id, voice=audio, caption=caption,
                reply_parameters=_reply_params(reply_to),
                message_thread_id=thread_id,
                reply_markup=reply_markup,
            )
        if sent is not None:
            _remember_bot_msg(chat_id, sent.message_id, chunk)
        return sent
    except Exception:
        log.exception("TTS-Generierung fehlgeschlagen")
        return None
    finally:
        tmp_path.unlink(missing_ok=True)


async def _send_tts(bot, chat_id: int, text: str, reply_to: int | None = None,
                    thread_id: int | None = None,
                    coupled_text: str | None = None):
    """Generiert Sprachnachrichten via edge-tts — bei langen Texten in mehreren Chunks.

    reply_to: markiert nur die erste Sprachnachricht als Reply auf die
    auslösende User-Nachricht.
    thread_id: Forum-Thema, in das alle Sprach-Chunks gehen.
    coupled_text: Wenn gesetzt, wird der Originaltext auf die erste Voice-Nachricht
    als Caption gerendert (max 1024 Zeichen Telegram-Limit). Überschuss kommt als
    Textnachricht direkt darunter. So entsteht eine gekoppelte Voice+Text-Einheit,
    statt zweier separater Posts.

    Gibt das erste gesendete Message-Objekt zurück (Voice oder Text), oder None.
    """
    cleaned = _strip_markdown_for_tts(text)
    first_msg = None
    if not cleaned:
        if coupled_text:
            first_msg = await send_chunked(bot, chat_id, coupled_text,
                                           reply_to=reply_to, thread_id=thread_id)
        return first_msg
    chunks = _split_tts_chunks(cleaned)
    caption_for_first: str | None = None
    rest_text = ""
    if coupled_text:
        caption_for_first = coupled_text[:1024]
        if len(coupled_text) > 1024:
            rest_text = coupled_text[1024:].lstrip()
    for i, chunk in enumerate(chunks):
        sent = await _send_tts_chunk(
            bot, chat_id, chunk,
            caption=caption_for_first if i == 0 else None,
            reply_to=reply_to if i == 0 else None,
            thread_id=thread_id,
        )
        if first_msg is None:
            first_msg = sent
    if rest_text:
        tail = await send_chunked(bot, chat_id, rest_text, thread_id=thread_id)
        if first_msg is None:
            first_msg = tail
    return first_msg


async def _summarize_pdf_direct(local_path: Path) -> str:
    """Fasst ein PDF über das Agent SDK zusammen — nutzt den CLAUDE_CODE_OAUTH_TOKEN
    (Abo) wie der restliche Bot, kein separater ANTHROPIC_API_KEY mehr."""
    pdf_text = _extract_pdf_text(local_path)
    if not pdf_text.strip():
        raise RuntimeError("PDF enthält keinen lesbaren Text.")

    if len(pdf_text) > 50000:
        pdf_text = pdf_text[:50000] + "\n\n[… Dokument gekürzt auf 50.000 Zeichen …]"

    system_prompt = (
        "Du fasst Dokumente auf Deutsch zusammen — in fließendem, gehobenem, gut "
        "vorlesbarem Stil. Schreibe vollständige Sätze, keine Aufzählungen mit Symbolen, "
        "keine Datei-Pfade, keine URLs, keine Code-Blöcke, keine Kommandozeilen, keine "
        "Versionsnummern oder Sonderzeichen-Salat. Technische Inhalte beschreibst du "
        "sinngemäß in Worten (was sie bewirken oder enthalten), nicht wörtlich. "
        "Halte die Zusammenfassung prägnant — etwa fünf bis zehn Sätze, je nach Umfang. "
        "Antworte ausschließlich mit der Zusammenfassung selbst, ohne Vorrede, ohne "
        "Überschrift, ohne abschließende Meta-Bemerkung."
    )

    options = ClaudeAgentOptions(
        cwd=str(WORKDIR),
        permission_mode="bypassPermissions",
        allowed_tools=[],
        system_prompt=system_prompt,
    )
    client = ClaudeSDKClient(options=options)
    await client.connect()
    try:
        await client.query(
            "Fasse dieses Dokument prägnant und gut vorlesbar zusammen:\n\n" + pdf_text
        )
        parts: list[str] = []
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
            elif isinstance(msg, ResultMessage):
                break
    finally:
        try:
            await client.disconnect()
        except Exception:
            log.exception("disconnect of summary client failed")

    summary = "".join(parts).strip()
    if not summary:
        raise RuntimeError("Zusammenfassung leer geblieben — bitte erneut versuchen.")
    return summary


async def _typing_keepalive(bot, chat_id: int, thread_id: int | None) -> None:
    """Hält Telegrams „tippt…" wach, solange ein Turn läuft — zusätzliches
    Lebenszeichen neben der 🔧-Werkzeug-Spur, das auch Turns OHNE Werkzeug-Aufruf
    abdeckt (reine Textantworten, bei denen sonst gar nichts zu sehen wäre). Der
    Status verfällt nach ~5 s, deshalb alle 4 s auffrischen. Fehler hier dürfen
    den Turn nie stören → alles defensiv, Abbruch nur über cancel()."""
    try:
        while True:
            try:
                await bot.send_chat_action(chat_id, ChatAction.TYPING,
                                           message_thread_id=thread_id)
            except Exception:
                pass
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


async def stream_response(
    sess: UserSession, chat_id: int, force_tts: bool = False, reply_to: int | None = None,
    thread_id: int | None = None,
) -> str | None:
    """SAMMELT den Antworttext eines Turns und gibt ihn ZURÜCK — sendet ihn NICHT.

    Umbau 17.07.2026 (Adam-Entscheid, Vorstufe des einheitlichen Sendepfads 5.8):
    Früher ging jeder TextBlock sofort raus (text_buffer wurde nach jedem Send
    geleert) — dadurch gab es KEINEN Moment, in dem der vollständige Text bekannt
    war, bevor er den Nutzer erreichte. Ein Pre-Send-Hook (8.5) war so unmöglich.
    Jetzt: Text sammeln → Aufrufer prüft (presend) → Aufrufer sendet.

    LEBENSZEICHEN während langer Turns (Adam-Entscheid 17.07., fester Bestandteil
    der Puffer-Option 1): Seit der Text gesammelt statt live gestreamt wird, gäbe
    es sonst minutenlang nichts zu sehen. Zwei Signale:
      • 🔧-Werkzeug-Spur pro Tool-Aufruf — IMMER sichtbar, auch im quiet-Modus.
      • Telegram-„tippt…" als Dauer-Indikator — deckt Turns ganz ohne Werkzeug ab;
        im quiet-Modus abgeschaltet (wer Ruhe will, behält nur die 🔧-Spur).

    Rückgabe: der vollständige Antworttext (oder None, wenn der Turn keinen lieferte).
    """
    claude_turn_started = False
    parts: list[str] = []

    # Tipp-Indikator nur außerhalb des quiet-Modus (die 🔧-Spur läuft unabhängig).
    typing_task = (
        asyncio.create_task(_typing_keepalive(sess.bot, chat_id, thread_id))
        if not sess.quiet else None
    )
    try:
        async for msg in sess.client.receive_response():
            # 5.18: JEDE eingehende SDK-Nachricht ist ein Lebenszeichen der
            # Session — Text, Werkzeug-Aufruf, Werkzeug-Ergebnis, Zwischenstand.
            # Bewusst hier oben und nicht nur bei Text/Tool-Blöcken: ein Turn,
            # der lange in einem Werkzeug steckt, ist NICHT tot, und der
            # Stall-Wächter darf ihm nicht die Sitzung abschießen.
            sess.last_activity = time.monotonic()
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        if not claude_turn_started and sess.logger:
                            sess.logger.start_assistant_turn()
                            claude_turn_started = True
                        if sess.logger:
                            sess.logger.log_assistant_text(block.text)
                        parts.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        # Werkzeug-Lebenszeichen — BEWUSST unabhängig von quiet:
                        # ohne Live-Textstrom ist die Spur bei langen Recherche-
                        # Turns das einzige Zeichen, dass gearbeitet wird.
                        # 5.25 (d): Klartext statt Tool-Name; Rohform via /technik.
                        # /spur schaltet NUR diese FYI-Zeile stumm (Allow/Deny bleibt).
                        if not _trace_off(sess.user_id):
                            await send_chunked(
                                sess.bot, chat_id,
                                _tool_trace_line(chat_id, block.name, block.input or {}),
                                thread_id=thread_id)
                        if sess.logger:
                            sess.logger.log_tool(block.name)
            elif isinstance(msg, UserMessage):
                # 5.25 (a): Suchtreffer der laufenden Aufgabe erweitern die
                # Herkunfts-Menge — deren Adressen darf WebFetch ohne Klick abrufen.
                sess.last_activity = time.monotonic()
                try:
                    for block in (getattr(msg, "content", None) or []):
                        if isinstance(block, ToolResultBlock):
                            sess.task_origins |= _extract_hosts(str(block.content))
                except Exception:
                    pass
            elif isinstance(msg, ResultMessage):
                if sess.logger and claude_turn_started:
                    sess.logger.end_turn()
                _record_usage(sess.current_model, msg)
                return "".join(parts).strip() or None
        # Fallback: kein ResultMessage (z.B. Abbruch) — trotzdem sauber abschließen.
        if sess.logger and claude_turn_started:
            sess.logger.end_turn()
        return "".join(parts).strip() or None
    finally:
        if typing_task is not None:
            typing_task.cancel()


async def send_answer_to_user(
    sess: UserSession, chat_id: int, text: str, *, force_tts: bool = False,
    reply_to: int | None = None, thread_id: int | None = None,
) -> bool:
    """ZENTRALER Sendepfad für Antworttext (Vorstufe 5.8) — nach dem Pre-Send-Hook.

    Bei aktivem TTS wird der Text in TTS_SYNC_CHUNK-Stücke geschnitten; jedes
    bekommt seine eigene Sprachnachricht (Text als Caption; bei force_tts nur Audio).
    Sonst: als Text senden (send_chunked splittet am Telegram-Limit).

    **Rückgabe = Zustellnachweis** (seit 19.07.): True, wenn mindestens ein Stück
    tatsächlich rausging. Der Aufrufer entscheidet daran, ob die Nachricht als
    beantwortet gilt. Vorher gab diese Funktion nichts zurück und ein
    fehlgeschlagener Versand sah für den Aufrufer aus wie ein erfolgreicher —
    am 19.07. live passiert: edge-tts war kurz nicht erreichbar, die Antwort
    („Nenn mir eine Stadt") wurde erzeugt, nie zugestellt und trotzdem als
    erledigt abgehakt. Genau der stille Verlust, den 5.2 ausschließen soll.
    """
    text = (text or "").strip()
    if not text:
        return True  # nichts zu senden ist kein Zustellfehler
    use_tts = sess.tts_enabled or force_tts
    first_pending = reply_to is not None
    kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)

    # 5.9: Nummerierte Optionsliste → Inline-Ziffern-Knöpfe direkt an der
    # Nachricht (Telegram bietet keine Ziffern-Reaktionen; Adam-Entscheid).
    # Nur im Text-Modus — bei TTS bleibt die Wahl per Text/Reaktion.
    n_opts = reactions.detect_numbered_options(text) if not use_tts else 0
    opt_kb = None
    if n_opts:
        digits = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        row = [InlineKeyboardButton(digits[i], callback_data=f"opt:{i + 1}")
               for i in range(n_opts)]
        opt_kb = InlineKeyboardMarkup([row[:5], row[5:]] if n_opts > 5 else [row])

    if not use_tts:
        sent = await send_chunked(
            sess.bot, chat_id, text, reply_markup=opt_kb or kb,
            reply_to=reply_to if first_pending else None,
            thread_id=thread_id,
        )
        if sent is not None:
            _remember_bot_msg(chat_id, sent.message_id, text)
            # 5.9: Sieht die Antwort nach einer offenen Frage aus → registrieren,
            # damit eine spätere Reaktion ihr zugeordnet werden kann (persistent).
            reactions.register_question(chat_id, sent.message_id, text)
        return sent is not None

    delivered = False
    last_sent_id: int | None = None
    rest = text
    while rest:
        if len(rest) <= TTS_SYNC_CHUNK:
            chunk, rest = rest, ""
        else:
            cut = TTS_SYNC_CHUNK
            for sep in ("\n\n", "\n", ". ", "! ", "? ", "; ", ", "):
                pos = rest.rfind(sep, 0, TTS_SYNC_CHUNK)
                if pos > TTS_SYNC_CHUNK // 2:
                    cut = pos + len(sep)
                    break
            chunk, rest = rest[:cut], rest[cut:]
        chunk = chunk.strip()
        if not chunk:
            continue
        tts_clean = _strip_markdown_for_tts(chunk)
        sent = None
        if tts_clean:
            sent = await _send_tts_chunk(
                sess.bot, chat_id, tts_clean,
                caption=None if force_tts else chunk[:1024],
                reply_to=reply_to if first_pending else None,
                thread_id=thread_id,
                reply_markup=None if force_tts else kb,
            )
        if sent is None:
            # Sprachausgabe ausgefallen (edge-tts nicht erreichbar o. ä.) ODER der
            # Chunk war nicht sprechbar: NIEMALS still verschlucken — als Text
            # zustellen. Eine gelesene Antwort ist unendlich viel besser als keine.
            # (Ohne diesen Zweig verschwand am 19.07. eine fertige Antwort spurlos.)
            if tts_clean:
                log.warning("TTS-Chunk fehlgeschlagen — Text-Fallback für %d Zeichen", len(chunk))
            sent = await send_chunked(
                sess.bot, chat_id, chunk, reply_markup=kb,
                reply_to=reply_to if first_pending else None,
                thread_id=thread_id,
            )
            if sent is not None:
                _remember_bot_msg(chat_id, sent.message_id, chunk)
        delivered = delivered or (sent is not None)
        if sent is not None:
            last_sent_id = getattr(sent, "message_id", None) or last_sent_id
        first_pending = False

    # 5.9: Auch im TTS-Modus muss eine offene Frage registriert werden — die
    # Reaktion landet auf der LETZTEN gesendeten Nachricht (dort steht der Schluss).
    if delivered and last_sent_id is not None:
        reactions.register_question(chat_id, last_sent_id, text)

    return delivered


# ---------- entry ----------

def _wait_for_network(host: str = "api.telegram.org", port: int = 443,
                      timeout: float = 5.0, max_wait: int = 120) -> None:
    """Block until TCP to host:port succeeds or max_wait seconds elapsed.

    After Mac wake-from-sleep, DNS resolution can take 10-30s to recover.
    Without this, launchd restarts the bot, it immediately crashes on DNS,
    and the ThrottleInterval + crash loop wastes another 30s each round.
    """
    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return
        except OSError:
            time.sleep(3)
    log.warning("network not available after %ds — starting anyway", max_wait)


def main() -> None:
    if not ALLOWED_USER_IDS:
        raise SystemExit("ALLOWED_USER_IDS env var is empty — refusing to start (open bot is dangerous).")
    _wait_for_network()
    log.info("starting bot — workdir=%s allowed=%s", WORKDIR, sorted(ALLOWED_USER_IDS))
    # concurrent_updates=True is THE critical fix for the permission-button
    # deadlock: without it, PTB processes updates sequentially across the whole
    # application, so a text message handler that's awaiting a permission
    # future blocks the callback_query update that would resolve it.
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .concurrent_updates(True)
        .build()
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("whereami", cmd_whereami))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("tts", cmd_tts))
    app.add_handler(CommandHandler("ttsdemo", cmd_ttsdemo))
    app.add_handler(CommandHandler("quiet", cmd_quiet))
    app.add_handler(CommandHandler("verbose", cmd_verbose))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("ampel", cmd_ampel))
    app.add_handler(CommandHandler("presend", cmd_presend))
    app.add_handler(CommandHandler("usage", cmd_usage))
    app.add_handler(CommandHandler("hilfe", cmd_hilfe))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("setkanal", cmd_setkanal))
    app.add_handler(CommandHandler("selfcheck", cmd_selfcheck))
    app.add_handler(CommandHandler("stopp", cmd_stopp))
    app.add_handler(CommandHandler("technik", cmd_technik))
    app.add_handler(CommandHandler("spur", cmd_spur))
    app.add_handler(CommandHandler("freigaben", cmd_freigaben))
    app.add_handler(CallbackQueryHandler(on_option_callback, pattern=r"^opt:"))
    app.add_handler(CallbackQueryHandler(on_permission_callback, pattern=r"^p:"))
    app.add_handler(CallbackQueryHandler(on_ampel_callback, pattern=r"^amp:"))
    app.add_handler(CallbackQueryHandler(on_pdf_callback, pattern=r"^pdf:"))
    app.add_handler(CallbackQueryHandler(on_channel_callback, pattern=r"^ch:"))
    app.add_handler(CallbackQueryHandler(on_restart_callback, pattern=r"^rst:"))
    app.add_handler(ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageReactionHandler(on_reaction))
    app.add_handler(MessageHandler(filters.StatusUpdate.PINNED_MESSAGE, on_pinned_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, on_voice))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, on_document))
    app.add_handler(MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, on_video))
    app.add_error_handler(on_telegram_error)
    # drop_pending_updates=False: Nachrichten aus der Ausfallzeit (Mac-Schlaf/
    # Neustart) werden beim Start nachgeholt statt verworfen — sonst geht eine
    # während der Downtime gesendete Sprach-/Textnachricht verloren, bevor sie
    # je transkribiert/geloggt wird. Veraltete Permission-Klicks sind ungefährlich,
    # weil on_permission_callback fehlende Futures sauber abfängt.
    # 1.9 (23.07.2026): Webhook-Modus als env-Schalter — Default bleibt Polling.
    # Umschalten NUR gemeinsam mit Adam (Umschaltmoment!). Rote Auflagen
    # (Rotes-Team C.1): secret_token Pflicht, unerratbarer Pfad, Firewall auf
    # Telegram-Netze (149.154.160.0/20, 91.108.4.0/22).
    # Zwei Betriebsarten:
    #  (a) Self-Signed direkt auf die IP — WEBHOOK_CERT + WEBHOOK_KEY gesetzt:
    #      der Bot terminiert TLS selbst (listen 0.0.0.0), Telegram bekommt das
    #      Zertifikat via setWebhook hochgeladen. Kein Reverse-Proxy nötig.
    #  (b) Reverse-Proxy (Domain/Let's Encrypt) — ohne CERT/KEY: listen 127.0.0.1,
    #      TLS macht Caddy/nginx davor.
    bot_mode = (os.environ.get("BOT_MODE") or "polling").strip().lower()
    if bot_mode == "webhook":
        webhook_url = os.environ.get("WEBHOOK_URL", "").strip()
        secret_token = os.environ.get("WEBHOOK_SECRET_TOKEN", "").strip()
        url_path = os.environ.get("WEBHOOK_PATH", "").strip().lstrip("/")
        cert_path = os.environ.get("WEBHOOK_CERT", "").strip()
        key_path = os.environ.get("WEBHOOK_KEY", "").strip()
        self_signed = bool(cert_path and key_path)
        listen_port = int(os.environ.get("WEBHOOK_LISTEN_PORT")
                          or ("8443" if self_signed else "8081"))
        missing = [n for n, v in (("WEBHOOK_URL", webhook_url),
                                  ("WEBHOOK_SECRET_TOKEN", secret_token),
                                  ("WEBHOOK_PATH", url_path)) if not v]
        if missing:
            raise SystemExit(
                "BOT_MODE=webhook, aber Pflicht-Envs fehlen (rote Auflagen 1.9): "
                + ", ".join(missing))
        kwargs = dict(
            port=listen_port,
            url_path=url_path,
            webhook_url=webhook_url.rstrip("/") + "/" + url_path,
            secret_token=secret_token,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=DROP_PENDING_UPDATES,
        )
        if self_signed:
            # Direkte TLS-Terminierung mit Self-Signed-Zertifikat auf der IP.
            kwargs.update(listen="0.0.0.0", cert=cert_path, key=key_path)
            log.info("Starte im WEBHOOK-Modus (Self-Signed direkt, Port %d, Pfad /%s…)",
                     listen_port, url_path[:8])
        else:
            kwargs.update(listen="127.0.0.1")
            log.info("Starte im WEBHOOK-Modus (Reverse-Proxy, Port %d, Pfad /%s…)",
                     listen_port, url_path[:8])
        app.run_webhook(**kwargs)
    else:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=DROP_PENDING_UPDATES,
        )


if __name__ == "__main__":
    # Stirbt der Prozess an einer Exception, bleibt ein lesbarer Grund für die
    # nächste Startnachricht zurück — sonst meldet der Bot nach einem Absturz
    # nur wortlos „Bin wieder da" und Adam erfährt nie, dass etwas schiefging.
    try:
        main()
    except BaseException as exc:
        _write_crash_restart_reason(exc)
        raise
