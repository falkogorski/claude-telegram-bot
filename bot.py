"""Telegram bridge for Claude Code / Agent SDK.

One Telegram user maps to one persistent Claude session. Each incoming message
is forwarded to the agent; assistant text streams back as Telegram messages.
Tool-permission requests are rendered as inline keyboards (Allow / Deny / Always).
"""

from __future__ import annotations

import asyncio
import json as _json
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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, ReactionTypeEmoji, ReplyKeyboardMarkup, ReplyParameters, Update
from telegram.constants import ParseMode
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
    ToolUseBlock,
)

import tempfile

from transcribe import Transcriber, build_transcriber

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

_MEMORY_DIR = Path.home() / ".claude/projects/-Users-jakuna/memory"
_MEMORY_CACHE: str | None = None
_MEMORY_MTIME: float = 0.0


def load_user_memory() -> str:
    """Liest alle Memory-Dateien als Kontext-String; gecacht bis MEMORY.md sich ändert."""
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
        parts: list[str] = ["# Nutzer-Kontext (persistente Memory)\n"]
        for match in re.finditer(r"\[.*?\]\(([^)]+\.md)\)", index):
            mem_file = _MEMORY_DIR / match.group(1)
            if not mem_file.exists():
                continue
            text = mem_file.read_text(encoding="utf-8")
            if text.startswith("---"):
                end = text.find("---", 3)
                if end >= 0:
                    text = text[end + 3:].lstrip("\n")
            parts.append(text.strip())
        _MEMORY_CACHE = "\n\n---\n\n".join(parts)
        _MEMORY_MTIME = mtime
        return _MEMORY_CACHE
    except Exception:
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
_DEFAULT_LOG_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Claude-Logs"
LOG_DIR = Path(os.environ.get("CONVERSATION_LOG_DIR") or str(_DEFAULT_LOG_DIR))
TELEGRAM_MSG_LIMIT = 4000  # actual is 4096; leave headroom for formatting
VOICE_LANGUAGE = os.environ.get("VOICE_LANGUAGE") or "de"
TTS_VOICE = os.environ.get("TTS_VOICE") or "de-DE-KatjaNeural"
TTS_CHUNK_CHARS = 4000  # max. Zeichen pro Sprachnachricht (PDF-Vorlesen etc.)
TTS_SYNC_CHUNK = 1024  # max. Zeichen pro Text-Chunk wenn TTS-Sync-Modus aktiv
_RESTART_REASON_FILE = Path.home() / ".claude/bot-restart-reason.txt"
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR") or str(Path.home() / "Downloads" / "claude-uploads"))
DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "opus")
# Kurznamen → vollständige Modell-IDs, die das SDK versteht
_MODEL_ALIASES: dict[str, str] = {
    "opus":   "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5-20251001",
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
_BTN_TTS_ON = "🔊 TTS an"
_BTN_TTS_OFF = "🔇 TTS aus"
_BTN_OPUS_ACTIVE = "🔵 Opus ✓"
_BTN_SONNET_ACTIVE = "🟡 Sonnet ✓"
_BTN_HAIKU_ACTIVE = "🟣 Haiku ✓"
_BTN_RESTART = "🔄 Neustart"
_BTN_INFO = "ℹ️ Info"
# Thinking-Effort-Buttons: ⚖️ Normal (default) / ⚡ Schnell (low) / 🚀 Max
_BTN_EFFORT_LOW = "⚡ Schnell"
_BTN_EFFORT_MED = "⚖️ Normal"
_BTN_EFFORT_MAX = "🚀 Max"
_BTN_EFFORT_LOW_ACTIVE = "⚡ Schnell ✓"
_BTN_EFFORT_MED_ACTIVE = "⚖️ Normal ✓"
_BTN_EFFORT_MAX_ACTIVE = "🚀 Max ✓"
_ALL_KEYBOARD_BTNS = {_BTN_OPUS, _BTN_SONNET, _BTN_HAIKU, _BTN_TTS_ON, _BTN_TTS_OFF,
                      _BTN_OPUS_ACTIVE, _BTN_SONNET_ACTIVE, _BTN_HAIKU_ACTIVE,
                      _BTN_RESTART, _BTN_INFO,
                      _BTN_EFFORT_LOW, _BTN_EFFORT_MED, _BTN_EFFORT_MAX,
                      _BTN_EFFORT_LOW_ACTIVE, _BTN_EFFORT_MED_ACTIVE, _BTN_EFFORT_MAX_ACTIVE}
# Aliase statt fester Versionen → Bot nutzt automatisch das jeweils
# höchstwertige aktuelle Modell, Label muss bei neuen Versionen nicht angepasst werden.
_MODEL_IDS = {
    _BTN_OPUS: "opus",
    _BTN_OPUS_ACTIVE: "opus",
    _BTN_SONNET: "sonnet",
    _BTN_SONNET_ACTIVE: "sonnet",
    _BTN_HAIKU: "haiku",
    _BTN_HAIKU_ACTIVE: "haiku",
}
# Mapping Button → effort-String (None = SDK-Default)
_EFFORT_IDS: dict[str, str | None] = {
    _BTN_EFFORT_LOW: "low",
    _BTN_EFFORT_LOW_ACTIVE: "low",
    _BTN_EFFORT_MED: None,
    _BTN_EFFORT_MED_ACTIVE: None,
    _BTN_EFFORT_MAX: "max",
    _BTN_EFFORT_MAX_ACTIVE: "max",
}


def _main_keyboard(tts_on: bool, model: str, effort: str | None = None) -> ReplyKeyboardMarkup:
    opus_label = _BTN_OPUS_ACTIVE if "opus" in model else _BTN_OPUS
    sonnet_label = _BTN_SONNET_ACTIVE if "sonnet" in model else _BTN_SONNET
    haiku_label = _BTN_HAIKU_ACTIVE if "haiku" in model else _BTN_HAIKU
    tts_label = _BTN_TTS_OFF if tts_on else _BTN_TTS_ON
    low_label = _BTN_EFFORT_LOW_ACTIVE if effort == "low" else _BTN_EFFORT_LOW
    med_label = _BTN_EFFORT_MED_ACTIVE if effort is None else _BTN_EFFORT_MED
    max_label = _BTN_EFFORT_MAX_ACTIVE if effort == "max" else _BTN_EFFORT_MAX
    return ReplyKeyboardMarkup(
        [
            [haiku_label, sonnet_label, opus_label],
            [med_label, low_label, max_label],
            [_BTN_RESTART, tts_label, _BTN_INFO],
        ],
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

# Pending PDF-Entscheidungen: user_id → dict mit Dateiinfos
_PENDING_DOCS: dict[int, dict] = {}

# Built lazily on first use so an STT misconfig only breaks /voice, not the whole bot.
_TRANSCRIBER: Transcriber | None = None


class ConversationLogger:
    """Appends each exchange to a Markdown file in iCloud (or LOG_DIR)."""

    def __init__(self, user_id: int) -> None:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            date_str = time.strftime("%Y-%m-%d")
            self._path = LOG_DIR / f"{date_str}.md"
            new_file = not self._path.exists()
            with self._path.open("a", encoding="utf-8") as f:
                if new_file:
                    f.write(f"# Claude Telegram Log – {date_str}\n\n")
                f.write(
                    f"## Session · {time.strftime('%H:%M:%S')} · {WORKDIR}\n\n---\n\n"
                )
            log.info("conversation log: %s", self._path)
        except Exception:
            log.exception("conversation log init failed (non-fatal)")
            self._path = None

    def log_user(self, text: str) -> None:
        self._append(f"## Du · {time.strftime('%H:%M:%S')}\n\n{text}\n\n")

    def start_assistant_turn(self) -> None:
        self._append(f"## Claude · {time.strftime('%H:%M:%S')}\n\n")

    def log_assistant_text(self, text: str) -> None:
        self._append(f"{text}\n\n")

    def log_tool(self, tool_name: str) -> None:
        self._append(f"*🔧 {tool_name}*\n\n")

    def end_turn(self) -> None:
        self._append("---\n\n")

    def _append(self, text: str) -> None:
        if self._path is None:
            return
        try:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            log.exception("conversation log write failed (non-fatal)")


def get_transcriber() -> Transcriber:
    global _TRANSCRIBER
    if _TRANSCRIBER is None:
        _TRANSCRIBER = build_transcriber()
    return _TRANSCRIBER


async def _download_tg_file(file_obj, filename: str) -> Path:
    """Lädt eine Telegram-Datei in UPLOAD_DIR; gibt den lokalen Pfad zurück."""
    out_dir = Path(UPLOAD_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    # Sonderzeichen im Dateinamen entschärfen
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    dest = out_dir / f"{ts}_{safe}"
    await file_obj.download_to_drive(str(dest))
    return dest


@dataclass
class UserSession:
    client: ClaudeSDKClient
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    always_allowed_tools: set[str] = field(default_factory=set)
    quiet: bool = True
    tts_enabled: bool = False
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

CORRECTION_PREFIXES = ("korrektur", "weitere info", "zusatzinfo", "nachtrag", "ergänzung", "ergaenzung")


@dataclass
class QueuedJob:
    update: Update
    text: str
    force_tts: bool = False
    output_chat_id: int | None = None
    reply_to_override: int | None = None
    received_at: float = field(default_factory=time.time)


@dataclass
class Mailbox:
    queue: deque[QueuedJob] = field(default_factory=deque)
    worker: asyncio.Task | None = None
    current_job: QueuedJob | None = None
    current_started: float = 0.0
    done_log: deque[tuple[float, str]] = field(default_factory=lambda: deque(maxlen=8))


MAILBOXES: dict[int, Mailbox] = {}

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


def _is_correction(text: str) -> bool:
    return (text or "").lstrip().lower().startswith(CORRECTION_PREFIXES)


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
        try:
            await _run_job(user_id, job)
        except Exception:
            log.exception("worker: job failed for user_id=%s", user_id)
        finally:
            mb.done_log.append((time.time(), _job_preview(job.text)))
            mb.current_job = None
    mb.worker = None


async def _run_job(user_id: int, job: QueuedJob) -> None:
    """Führt EINEN Job gegen die (ggf. frisch geöffnete) Claude-Session aus.
    Body entspricht der früheren process_user_text-Logik."""
    sess = await ensure_session(user_id)
    update = job.update
    sess.chat_id = update.effective_chat.id
    sess.bot = update.get_bot()
    effective_output_id = job.output_chat_id or update.effective_chat.id

    same_chat = bool(update.message and effective_output_id == update.effective_chat.id)
    # Antwort als Reply auf die auslösende Nachricht markieren — aber nur, wenn die
    # Antwort in denselben Chat geht (ein message_id-Bezug über Chats hinweg wäre ungültig).
    # Bei Sprachnachrichten zeigt der Override auf die lesbare Transkriptions-Nachricht
    # (🎙️ …) statt auf das reine Audio, damit das Zitat beim Scrollen lesbar bleibt.
    reply_to = (job.reply_to_override or update.message.message_id) if same_chat else None
    # In Forum-Gruppen: Antwort ins selbe Thema (Topic) zurückschicken. Nur sinnvoll,
    # wenn die Antwort in denselben Chat geht; bei Cross-Chat-Ablage (Ausgabekanal) None.
    thread_id = getattr(update.message, "message_thread_id", None) if same_chat else None
    sess.thread_id = thread_id  # Permission-Prompts lesen das Thema von hier

    tts_text: str | None = None
    async with sess.lock:
        try:
            if sess.logger:
                sess.logger.log_user(job.text)
            await sess.client.query(_current_datetime_context() + job.text)
            tts_text = await stream_response(
                sess, effective_output_id, force_tts=job.force_tts,
                reply_to=reply_to, thread_id=thread_id,
            )
        except Exception as e:
            log.exception("error processing message")
            cancelled = cancel_pending_permissions(sess, reason=f"query error: {e}")
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

    if tts_text and sess.bot:
        asyncio.create_task(_send_tts(sess.bot, effective_output_id, tts_text, reply_to=reply_to, thread_id=thread_id))


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

        if tool_name in sess.always_allowed_tools:
            return PermissionResultAllow()

        request_id = uuid.uuid4().hex[:8]
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        sess.pending_permissions[request_id] = (loop, fut)
        log.info("permission requested: user=%s req=%s tool=%s",
                 user_id, request_id, tool_name)

        body = format_tool_call(tool_name, tool_input)
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Allow", callback_data=f"p:{request_id}:allow"),
                    InlineKeyboardButton("❌ Deny", callback_data=f"p:{request_id}:deny"),
                ],
                [
                    InlineKeyboardButton(
                        f"🔓 Always allow {tool_name}",
                        callback_data=f"p:{request_id}:always:{tool_name}",
                    ),
                ],
            ]
        )
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
            sess.always_allowed_tools.add(decision.split(":", 1)[1])
            return PermissionResultAllow()
        return PermissionResultDeny(message="unknown decision")

    return can_use_tool


# ---------- session lifecycle ----------

def _current_datetime_context() -> str:
    """Liefert das aktuelle Datum, den Wochentag und die Uhrzeit als
    Pflicht-Kontextzeile, die vor jeder User-Nachricht ans Modell mitgegeben wird.

    Damit hat das Modell bei jedem Aufruf das aktuelle Datum vor sich und muss
    es nicht aus der Memory oder aus früheren Log-Einträgen zurückrechnen.
    Schließt den wiederkehrenden 'letzte/vorletzte Nacht'-Fehlerkanal.
    """
    from datetime import datetime
    now = datetime.now()
    weekdays_de = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag",
        "Freitag", "Samstag", "Sonntag",
    ]
    weekday = weekdays_de[now.weekday()]
    return (
        f"[Systemzeit beim Eingang dieser Nachricht: {weekday}, "
        f"{now.strftime('%d.%m.%Y')}, {now.strftime('%H:%M')} Uhr. "
        f"Bei jeder zeitlichen Aussage (heute/gestern/letzte Nacht/in X Tagen) "
        f"diesen Wert als Wahrheit nehmen — nicht aus der Memory rechnen.]\n\n"
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


def _session_context(memory: str) -> str:
    """Memory + jüngster Gesprächsverlauf als ein system_prompt-Append-Block."""
    recall = _recent_conversation_recall()
    if not recall:
        return memory
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
    return f"{memory}\n\n---\n\n{block}" if memory else block


async def ensure_session(user_id: int) -> UserSession:
    sess = SESSIONS.get(user_id)
    if sess is not None:
        return sess

    memory = load_user_memory()
    context = _session_context(memory)
    user_prefs = _USER_PREFS.get(str(user_id), {})
    model_short = user_prefs.get("model", DEFAULT_MODEL)
    model_full = _MODEL_ALIASES.get(model_short, model_short)  # vollständige SDK-ID
    effort = user_prefs.get("effort", None)
    options = ClaudeAgentOptions(
        cwd=str(WORKDIR),
        permission_mode="default",
        can_use_tool=make_permission_callback(user_id),
        model=model_full,
        effort=effort,
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": context,
        } if context else {"type": "preset", "preset": "claude_code"},
    )
    client = ClaudeSDKClient(options=options)
    await client.connect()
    sess = UserSession(
        client=client,
        tts_enabled=user_prefs.get("tts_enabled", False),
        current_model=model_short,  # Kurzname für Anzeige und Vergleiche
        current_effort=effort,
        logger=ConversationLogger(user_id),
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
        "/quiet — Nur Abschlussantworten (keine Tool-Meldungen)\n"
        "/verbose — Alle Tool-Meldungen anzeigen\n"
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

    await update.message.reply_text("\n".join(lines))


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
        "/tts — TTS an/aus umschalten\n"
        "/ttsdemo — TTS-Testausgabe\n"
        "/quiet — Tool-Calls ausblenden\n"
        "/verbose — Tool-Calls anzeigen\n"
        "/setkanal — Ausgabekanal setzen\n"
        "/whereami — Kanal-Info anzeigen\n"
        "/whoami — User-Info\n"
        "/restart — Bot neu starten\n"
        "/selfcheck — Selbsttest ausführen\n"
        "/hilfe — Diese Befehlsübersicht\n\n"
        "📌 Buttons in der Tastatur:\n"
        "🔵 Opus / 🟡 Sonnet — Modell wechseln\n"
        "⚖️ Normal / ⚡ Schnell / 🚀 Max — Denk-Tiefe\n"
        "🔄 Neustart / 🔊🔇 TTS / ℹ️ Info"
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

    pending = _PENDING_DOCS.pop(user_id, None)
    if not pending:
        await query.edit_message_text("Dokument nicht mehr verfügbar — bitte erneut senden.")
        return

    doc_parts: list[str] = pending["parts"]
    prefix: str = pending["prefix"]
    orig_update: Update = pending["update"]
    filename: str = pending["filename"]
    size_mb: float = pending["size_mb"]

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

        local_path_str = pending.get("local_path", "")
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

        local_path_str = pending.get("local_path", "")
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
    local_path_str = pending.get("local_path", "")
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
        lines = [
            f'Gruppe „{chat.title or chat.id}" erkannt.',
            f"Gruppen-ID: {chat.id}",
        ]
        if str(chat.id).startswith("-100"):
            lines.append(f"Interne ID: {str(chat.id)[4:]}")
        if getattr(chat, "is_forum", False):
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
    await update.message.reply_text("🔕 Quiet-Modus an — nur Abschlussantworten, keine Tool-Meldungen.")


async def cmd_verbose(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    sess = await ensure_session(update.effective_user.id)
    sess.quiet = False
    await update.message.reply_text("🔔 Verbose-Modus an — alle Tool-Meldungen sichtbar.")


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
    """Resolve a pending permission via 👍 (allow) or 👎 (deny) reaction."""
    rx = update.message_reaction
    if rx is None:
        return
    user_id = rx.user.id if rx.user else None
    if user_id not in ALLOWED_USER_IDS:
        return

    sess = SESSIONS.get(user_id)
    if sess is None:
        return

    request_id = sess.message_permissions.get(rx.message_id)
    if request_id is None:
        return

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
        log.info("reaction permission: user=%s req=%s decision=%s", user_id, request_id, decision)
        return


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

    def _clean_user_text(block: list[str]) -> str:
        """Kontext-Wrapper ('[Kontext: …]'-Zeilen) herausfiltern, echten Text zurückgeben."""
        in_ctx = False
        clean: list[str] = []
        for l in block:
            s = l.strip()
            if s.startswith("[Kontext:"):
                in_ctx = True
            if in_ctx:
                if s.endswith("]"):
                    in_ctx = False
                continue
            if s:
                clean.append(s)
        return "\n".join(clean).strip()

    def _first_meaningful(text: str, max_len: int = 100) -> str:
        lines = [
            _re.sub(r"[*_`#>]", "", l).strip()
            for l in text.splitlines()
            if _re.sub(r"[*_`#>]", "", l).strip()
        ]
        s = lines[0] if lines else text[:max_len]
        return (s[:max_len] + "…") if len(s) > max_len else s

    # ── Fall B: Adams letzte Nachricht vor dem Neustart blieb unbeantwortet ──
    if last_author == "user" and last_user_block:
        user_text = _clean_user_text(last_user_block)
        if user_text:
            if full:
                return (
                    f"Deine letzte Nachricht aus der vorherigen Session ist noch offen "
                    f"geblieben. Bitte beantworte sie jetzt:\n\n{user_text[:800]}"
                )
            return _first_meaningful(user_text)

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

    return state["ok"], results


async def cmd_selfcheck(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Manueller Selbstcheck der Kern-Invarianten."""
    if not authorized(update):
        return
    ok, lines = run_self_check()
    header = "Selbstcheck: alles grün." if ok else "⚠️ Selbstcheck: Probleme gefunden!"
    await update.message.reply_text(header + "\n\n" + "\n".join(lines))


async def post_init(app: Application) -> None:
    """Started after Application.initialize() — kicks off the watchdog task."""
    app.create_task(watchdog(app), name="watchdog")
    log.info("watchdog started (interval=%ds, timeout=%ds, threshold=%d)",
             WATCHDOG_INTERVAL_S, WATCHDOG_TIMEOUT_S, WATCHDOG_FAIL_THRESHOLD)
    app.create_task(heartbeat_writer(), name="heartbeat")
    log.info("heartbeat writer started (interval=%ds, path=%s)",
             HEARTBEAT_INTERVAL_S, HEARTBEAT_PATH)

    # Bot-Username für Rücksprung-Links (Ausgabekanal → Bot-Chat) einmalig cachen.
    global _BOT_USERNAME
    try:
        me = await app.bot.get_me()
        _BOT_USERNAME = me.username
        log.info("bot username gecached: @%s", _BOT_USERNAME)
    except Exception:
        log.warning("bot username konnte nicht ermittelt werden (Rück-Button inaktiv)")

    # Startup-Statusnachricht: Wenn ich (Claude) vor dem Neustart einen Grund
    # hinterlegt habe, wird er hier gelesen und als Telegram-Nachricht gesendet.
    # Ohne Datei: generische "Bot läuft"-Meldung + automatischer Chat-Check.
    # AUTORUN-Marker: Zeile "[AUTORUN]: <text>" → wird abgeschnitten und als
    # eigenständige Claude-Anfrage direkt nach der Startup-Nachricht ausgeführt.
    autorun_tasks: list[tuple[int, str]] = []  # (uid, autorun_text)
    try:
        if _RESTART_REASON_FILE.exists():
            startup_msg = _RESTART_REASON_FILE.read_text(encoding="utf-8").strip()
            _RESTART_REASON_FILE.unlink(missing_ok=True)
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
        pending_info_line = ""
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
        # Selbstcheck der Kern-Invarianten bei JEDEM Start — fängt Regressionen ab.
        # Bei Erfolg eine knappe Zeile, bei Fehler laut + auffällig.
        try:
            ok, lines = run_self_check()
            if ok:
                startup_msg += f"\n\nSelbstcheck: alle {len(lines)} Kernfunktionen ok."
            else:
                fails = [l for l in lines if l.startswith("✗")]
                startup_msg += ("\n\n⚠️ SELBSTCHECK-WARNUNG — bitte prüfen:\n" + "\n".join(fails))
        except Exception as e:
            startup_msg += f"\n\n⚠️ Selbstcheck konnte nicht laufen: {e}"
        for uid in ALLOWED_USER_IDS:
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
                    await app.bot.send_message(chat_id=uid, text=startup_msg, reply_markup=kb)
            except Exception:
                log.warning("startup message to user %s failed", uid)
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
                        await stream_response(sess, u)
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
) -> None:
    """Shared path: authorized update + text → Claude query + streamed response.

    output_chat_id: wenn gesetzt, gehen Antworten dorthin statt in den User-Chat.
    reply_to_override: message_id, auf die Antwort/TTS als Reply zeigen sollen
    (z.B. die Transkriptions-Nachricht statt der reinen Sprachnachricht).
    """
    user_id = update.effective_user.id
    mb = _get_mailbox(user_id)
    job = QueuedJob(
        update=update,
        text=text,
        force_tts=force_tts,
        output_chat_id=output_chat_id or update.effective_chat.id,
        reply_to_override=reply_to_override,
    )

    busy = mb.current_job is not None
    correction = _is_correction(text)

    if correction and busy:
        # Laufenden Vorgang stoppen, Zusatz sofort als Nächstes einarbeiten.
        try:
            sess = SESSIONS.get(user_id)
            if sess is not None:
                await sess.client.interrupt()
        except Exception:
            log.exception("interrupt on correction failed")
        mb.queue.appendleft(job)
        await update.message.reply_text(
            "✋ Laufenden Vorgang gestoppt — ich arbeite deine Korrektur ein.",
            reply_parameters=_reply_params(update.message.message_id),
        )
    else:
        # Neueste Nachricht hat Vorrang → vorne einsortieren (LIFO).
        mb.queue.appendleft(job)
        if busy:
            running = _job_preview(mb.current_job.text) if mb.current_job else "läuft"
            await update.message.reply_text(
                "📥 Notiert — kommt als Nächstes dran.\n"
                f"Läuft gerade: „{running}“\n"
                f"In Warteschlange: {len(mb.queue)}",
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
            model_label = "Opus" if "opus" in new_model else ("Haiku" if "haiku" in new_model else "Sonnet")
            await update.message.reply_text(f"{model_label} ist bereits aktiv.", reply_markup=keyboard)
            return
        # Modell wechseln: Session neu starten
        await close_session(user_id)
        _USER_PREFS.setdefault(str(user_id), {})["model"] = new_model
        _save_prefs(_USER_PREFS)
        new_sess = await ensure_session(user_id)
        keyboard = _main_keyboard(new_sess.tts_enabled, new_sess.current_model, new_sess.current_effort)
        model_label = "🔵 Opus" if "opus" in new_model else ("🟣 Haiku" if "haiku" in new_model else "🟡 Sonnet")
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
            await update.message.reply_text(f"Thinking: {effort_name} ist bereits aktiv.", reply_markup=keyboard)
            return
        # Effort wechseln: Session neu starten (effort ist ein Session-Start-Parameter)
        await close_session(user_id)
        prefs = _USER_PREFS.setdefault(str(user_id), {})
        if new_effort is None:
            prefs.pop("effort", None)
        else:
            prefs["effort"] = new_effort
        _save_prefs(_USER_PREFS)
        new_sess = await ensure_session(user_id)
        keyboard = _main_keyboard(new_sess.tts_enabled, new_sess.current_model, new_sess.current_effort)
        effort_labels = {None: "🧠 Normal", "low": "⚡ Schnell", "max": "🚀 Max"}
        effort_label = effort_labels.get(new_effort, str(new_effort))
        await update.message.reply_text(
            f"Thinking: {effort_label} aktiv. Session neu gestartet.",
            reply_markup=keyboard,
        )
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

        def _model_label(m: str) -> str:
            if "opus" in m:
                return "🔵 Opus"
            if "sonnet" in m:
                return "🟡 Sonnet"
            if "haiku" in m:
                return "🟣 Haiku"
            return f"❓ {m}"

        model_str = _model_label(active_model)
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
        await _handle_keyboard_btn(update, text.strip())
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

    # Telegram "voice" notes are OGG/Opus, "audio" can be anything ffmpeg understands.
    await msg.reply_chat_action("typing")
    try:
        tg_file = await voice.get_file()
    except Exception as e:
        log.exception("get_file failed")
        await msg.reply_text(f"❌ Konnte Sprachnachricht nicht laden: {e}")
        return

    # Audio dauerhaft in UPLOAD_DIR sichern statt nur temporär — so bleiben auch
    # unbearbeitete/ältere Sprachnachrichten auffindbar und nachträglich transkribierbar.
    suffix = Path(tg_file.file_path or "x.ogg").suffix or ".ogg"
    try:
        src = await _download_tg_file(tg_file, "voice" + suffix)
    except Exception as e:
        log.exception("voice download failed")
        await msg.reply_text(f"❌ Download fehlgeschlagen: {e}")
        return

    try:
        transcriber = get_transcriber()
    except Exception as e:
        log.exception("transcriber init failed")
        await msg.reply_text(f"❌ STT nicht konfiguriert: {e}")
        return

    try:
        text = await transcriber.transcribe(src, language=VOICE_LANGUAGE)
    except Exception as e:
        log.exception("transcription failed")
        await msg.reply_text(f"❌ Transkription fehlgeschlagen: {e}")
        return

    text = (text or "").strip()
    if not text:
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
    await process_user_text(update, prefix + text, reply_to_override=reply_override)


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
    await process_user_text(update, prefix + "\n".join(parts))


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
    await process_user_text(update, prefix + "\n".join(parts))


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
    await process_user_text(update, prefix + "\n".join(parts))


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


async def _ai_topic_label(text: str, max_words: int = 7) -> str:
    """Kurzes Inhalts-Thema (3-6 Wörter) für einen Abschnitt per Anthropic-API.

    Fällt bei fehlendem Key oder jedem Fehler still auf "" zurück (kein Label statt
    Stichwort-Salat — weniger ist mehr), damit das Vorlesen nie blockiert. ACHTUNG:
    schickt den Abschnitt an die Cloud-KI → nur für grün/gelb. Beim Vorlesen verlässt
    der Text den Rechner ohnehin schon via edge-tts (Microsoft).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)
        try:
            message = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=24,
                system=(
                    "Du benennst das Hauptthema eines Textabschnitts in 3 bis 7 deutschen "
                    "Wörtern — wie eine knappe, in sich abgeschlossene Kapitelüberschrift, "
                    "die den Inhalt erkennbar macht und nicht abgeschnitten wirkt. Gib NUR "
                    "die Überschrift aus, ohne Anführungszeichen und ohne Satzzeichen am Ende."
                ),
                messages=[{"role": "user", "content": f"Worum geht es in diesem Abschnitt?\n\n{text[:2000]}"}],
            )
        finally:
            await client.close()
        label = " ".join((message.content[0].text or "").split()).strip(' "„“.')
        if not label:
            return ""
        words = label.split()
        return " ".join(words[:max_words]) if len(words) > max_words else label
    except Exception:
        log.exception("KI-Themenlabel fehlgeschlagen — kein Label")
        return ""


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


async def stream_response(
    sess: UserSession, chat_id: int, force_tts: bool = False, reply_to: int | None = None,
    thread_id: int | None = None,
) -> str | None:
    """Forward assistant text + a compact tool-use trace back to Telegram.

    Wenn TTS aktiv (sess.tts_enabled oder force_tts): Text wird in Chunks von
    max. TTS_SYNC_CHUNK Zeichen aufgeteilt. Jeder Text-Chunk bekommt sofort seine
    eigene Sprachnachricht — kein separater TTS-Task mehr nötig, Rückgabe ist None.

    Wenn TTS aus: Text sofort senden, Rückgabe None.
    """
    claude_turn_started = False
    use_tts = sess.tts_enabled or force_tts
    first_text_pending = reply_to is not None
    tts_buffer: str = ""
    text_buffer: str = ""  # für nicht-TTS-Pfad: sammelt Streaming-Blöcke, hält Heading+Inhalt zusammen

    async def _flush(text: str) -> None:
        """Sendet Audio mit Text als Caption (1 Nachricht). Bei force_tts: nur Audio."""
        nonlocal first_text_pending
        text = text.strip()
        if not text:
            return
        tts_clean = _strip_markdown_for_tts(text)
        if tts_clean:
            kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
            await _send_tts_chunk(
                sess.bot, chat_id, tts_clean,
                caption=None if force_tts else text[:1024],
                reply_to=reply_to if first_text_pending else None,
                thread_id=thread_id,
                reply_markup=None if force_tts else kb,
            )
        first_text_pending = False

    async def _maybe_flush_buffer() -> None:
        """Flusht vollständige TTS_SYNC_CHUNK-Chunks aus dem Puffer."""
        nonlocal tts_buffer
        while len(tts_buffer) >= TTS_SYNC_CHUNK:
            cut = TTS_SYNC_CHUNK
            for sep in ("\n\n", "\n", ". ", "! ", "? ", "; ", ", "):
                pos = tts_buffer.rfind(sep, 0, TTS_SYNC_CHUNK)
                if pos > TTS_SYNC_CHUNK // 2:
                    cut = pos + len(sep)
                    break
            await _flush(tts_buffer[:cut])
            tts_buffer = tts_buffer[cut:]

    async for msg in sess.client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    if not claude_turn_started and sess.logger:
                        sess.logger.start_assistant_turn()
                        claude_turn_started = True
                    if sess.logger:
                        sess.logger.log_assistant_text(block.text)
                    if use_tts:
                        tts_buffer += block.text
                        await _maybe_flush_buffer()
                    else:
                        # Streaming-Blöcke puffern, damit eine Heading am Block-Ende
                        # NICHT als letzte Zeile einer Nachricht stehen bleibt.
                        text_buffer += block.text
                        if _text_ends_with_heading(text_buffer):
                            # warten auf nächsten Block, damit Heading+Inhalt zusammen senden
                            continue
                        kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
                        sent = await send_chunked(
                            sess.bot, chat_id, text_buffer, reply_markup=kb,
                            reply_to=reply_to if first_text_pending else None,
                            thread_id=thread_id,
                        )
                        if sent is not None:
                            _remember_bot_msg(chat_id, sent.message_id, text_buffer)
                        text_buffer = ""
                        first_text_pending = False
                elif isinstance(block, ToolUseBlock):
                    if use_tts and tts_buffer.strip():
                        await _flush(tts_buffer)
                        tts_buffer = ""
                    if not use_tts and text_buffer.strip():
                        # Restpuffer vor Tool-Use leeren — Heading bleibt drin, dafür Inhalt erst spät
                        kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
                        sent = await send_chunked(
                            sess.bot, chat_id, text_buffer, reply_markup=kb,
                            reply_to=reply_to if first_text_pending else None,
                            thread_id=thread_id,
                        )
                        if sent is not None:
                            _remember_bot_msg(chat_id, sent.message_id, text_buffer)
                        text_buffer = ""
                        first_text_pending = False
                    if not sess.quiet:
                        await send_chunked(sess.bot, chat_id, f"🔧 {block.name}", thread_id=thread_id)
                    if sess.logger:
                        sess.logger.log_tool(block.name)
        elif isinstance(msg, ResultMessage):
            if use_tts and tts_buffer.strip():
                await _flush(tts_buffer)
                tts_buffer = ""
            if not use_tts and text_buffer.strip():
                kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
                sent = await send_chunked(
                    sess.bot, chat_id, text_buffer, reply_markup=kb,
                    reply_to=reply_to if first_text_pending else None,
                    thread_id=thread_id,
                )
                if sent is not None:
                    _remember_bot_msg(chat_id, sent.message_id, text_buffer)
                text_buffer = ""
                first_text_pending = False
            if sess.logger and claude_turn_started:
                sess.logger.end_turn()
            _record_usage(sess.current_model, msg)
            return None  # TTS bereits inline gesendet
    # Fallback: Restpuffer leeren (falls kein ResultMessage)
    if use_tts and tts_buffer.strip():
        await _flush(tts_buffer)
    if not use_tts and text_buffer.strip():
        kb = _main_keyboard(sess.tts_enabled, sess.current_model, sess.current_effort)
        sent = await send_chunked(
            sess.bot, chat_id, text_buffer, reply_markup=kb,
            reply_to=reply_to if first_text_pending else None,
            thread_id=thread_id,
        )
        if sent is not None:
            _remember_bot_msg(chat_id, sent.message_id, text_buffer)
    if sess.logger and claude_turn_started:
        sess.logger.end_turn()
    return None


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
    app.add_handler(CommandHandler("usage", cmd_usage))
    app.add_handler(CommandHandler("hilfe", cmd_hilfe))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("setkanal", cmd_setkanal))
    app.add_handler(CommandHandler("selfcheck", cmd_selfcheck))
    app.add_handler(CallbackQueryHandler(on_permission_callback, pattern=r"^p:"))
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
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=DROP_PENDING_UPDATES,
    )


if __name__ == "__main__":
    main()
