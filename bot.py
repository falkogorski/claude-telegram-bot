"""Telegram bridge for Claude Code / Agent SDK.

One Telegram user maps to one persistent Claude session. Each incoming message
is forwarded to the agent; assistant text streams back as Telegram messages.
Tool-permission requests are rendered as inline keyboards (Allow / Deny / Always).
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
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
TELEGRAM_MSG_LIMIT = 4000  # actual is 4096; leave headroom for formatting
VOICE_LANGUAGE = os.environ.get("VOICE_LANGUAGE") or "de"

# Built lazily on first use so an STT misconfig only breaks /voice, not the whole bot.
_TRANSCRIBER: Transcriber | None = None


def get_transcriber() -> Transcriber:
    global _TRANSCRIBER
    if _TRANSCRIBER is None:
        _TRANSCRIBER = build_transcriber()
    return _TRANSCRIBER


@dataclass
class UserSession:
    client: ClaudeSDKClient
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    always_allowed_tools: set[str] = field(default_factory=set)
    pending_permissions: dict[str, asyncio.Future] = field(default_factory=dict)
    chat_id: int | None = None
    bot: Any = None  # telegram.Bot, injected per-message


SESSIONS: dict[int, UserSession] = {}


# ---------- helpers ----------

def authorized(update: Update) -> bool:
    user = update.effective_user
    if user is None or user.id not in ALLOWED_USER_IDS:
        log.warning("rejected message from user_id=%s", user.id if user else None)
        return False
    return True


async def send_chunked(bot, chat_id: int, text: str, **kwargs) -> None:
    """Telegram caps messages at ~4096 chars — split on newlines when needed."""
    if not text:
        return
    while text:
        if len(text) <= TELEGRAM_MSG_LIMIT:
            await bot.send_message(chat_id=chat_id, text=text, **kwargs)
            return
        cut = text.rfind("\n", 0, TELEGRAM_MSG_LIMIT)
        if cut <= 0:
            cut = TELEGRAM_MSG_LIMIT
        await bot.send_message(chat_id=chat_id, text=text[:cut], **kwargs)
        text = text[cut:].lstrip("\n")


def is_auth_error(exc: Exception) -> bool:
    """True if an exception looks like an Anthropic auth/credentials failure.

    These bubble up from the Claude Code subprocess the Agent SDK spawns — not
    from this bot — so the only reliable signal is the message text.
    """
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


AUTH_HELP = (
    "🔑 *Authentifizierung fehlgeschlagen* (401)\n\n"
    "Der Claude-Subprozess kann sich nicht bei Anthropic anmelden — "
    "das liegt an den Credentials, nicht am Bot.\n\n"
    "*So behebst du es (Abo-Auth, kostenfrei):*\n"
    "• Neuen Abo-Token erzeugen: `claude setup-token` — und als "
    "`CLAUDE_CODE_OAUTH_TOKEN` in die Dienst-Umgebung eintragen "
    "(launchd-Plist bzw. systemd-EnvironmentFile, nicht nur in die Shell).\n"
    "• Sicherstellen, dass NIRGENDS ein `ANTHROPIC_API_KEY` gesetzt ist — "
    "der hätte Vorrang und würde zudem extra kosten (💰 Kostenregel!).\n"
    "• Test ohne Bot: `claude -p \"hallo\"` im selben Kontext.\n\n"
    "Die kaputte Session wurde verworfen — nach dem Fix einfach neue Nachricht schicken."
)


def format_tool_call(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Pretty-print a tool call for the permission prompt."""
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        preview = cmd if len(cmd) < 800 else cmd[:800] + "…"
        return f"*Bash*\n```\n{preview}\n```"
    if tool_name in ("Read", "Edit", "Write"):
        path = tool_input.get("file_path", "")
        return f"*{tool_name}*: `{path}`"
    # generic fallback
    keys = ", ".join(list(tool_input.keys())[:5])
    return f"*{tool_name}*\nargs: {keys}"


# ---------- permission callback ----------

def make_permission_callback(user_id: int):
    """Returns a can_use_tool callback bound to this user."""

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
        sess.pending_permissions[request_id] = fut

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
            await sess.bot.send_message(
                chat_id=sess.chat_id,
                text=f"🔐 *Permission request*\n\n{body}",
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            log.exception("failed to send permission prompt")
            sess.pending_permissions.pop(request_id, None)
            return PermissionResultDeny(message="bot failed to ask user")

        try:
            decision = await asyncio.wait_for(fut, timeout=600)
        except asyncio.TimeoutError:
            sess.pending_permissions.pop(request_id, None)
            await sess.bot.send_message(
                chat_id=sess.chat_id,
                text=f"⌛ Permission request timed out — denied.",
            )
            return PermissionResultDeny(message="user did not respond in 10 min")

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

async def ensure_session(user_id: int) -> UserSession:
    sess = SESSIONS.get(user_id)
    if sess is not None:
        return sess

    options = ClaudeAgentOptions(
        cwd=str(WORKDIR),
        permission_mode="default",
        can_use_tool=make_permission_callback(user_id),
        system_prompt={"type": "preset", "preset": "claude_code"},
    )
    client = ClaudeSDKClient(options=options)
    await client.connect()
    sess = UserSession(client=client)
    SESSIONS[user_id] = sess
    log.info("opened session for user_id=%s in %s", user_id, WORKDIR)
    return sess


async def close_session(user_id: int) -> None:
    sess = SESSIONS.pop(user_id, None)
    if sess is None:
        return
    for fut in sess.pending_permissions.values():
        if not fut.done():
            fut.set_result("deny")
    try:
        await sess.client.disconnect()
    except Exception:
        log.exception("error disconnecting session for %s", user_id)


# ---------- telegram handlers ----------

async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    await update.message.reply_text(
        "👋 Claude-Code-Bot bereit.\n\n"
        f"Workdir: `{WORKDIR}`\n"
        "Schick mir eine Nachricht und ich starte/setze deine Claude-Session fort.\n\n"
        "Befehle:\n"
        "/reset — Session beenden (neue beginnt mit nächster Nachricht)\n"
        "/status — Session-Info\n"
        "/whoami — Deine Telegram-User-ID",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_whoami(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Deine Telegram-User-ID: `{user.id}`\n"
        f"Allowed: {'✅' if user.id in ALLOWED_USER_IDS else '❌'}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_reset(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    await close_session(update.effective_user.id)
    await update.message.reply_text("🔄 Session beendet. Nächste Nachricht startet eine neue.")


async def cmd_status(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    sess = SESSIONS.get(update.effective_user.id)
    if sess is None:
        await update.message.reply_text("Keine aktive Session.")
        return
    await update.message.reply_text(
        f"Aktive Session.\n"
        f"Always-allowed: {sorted(sess.always_allowed_tools) or '(keine)'}\n"
        f"Pending permissions: {len(sess.pending_permissions)}"
    )


async def on_permission_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Resolve the pending permission Future ASAP. The visual ack on the
    original message is best-effort — never let a formatting error block the
    actual permission decision from flowing back to the SDK."""
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

    # 3. Resolve future BEFORE any UI work — that's what actually unblocks Claude
    sess = SESSIONS.get(update.effective_user.id)
    suffix = None
    if sess is None:
        suffix = "(Session weg)"
    else:
        fut = sess.pending_permissions.pop(request_id, None)
        if fut is None or fut.done():
            suffix = "(bereits beantwortet)"
        else:
            try:
                fut.set_result(decision)
            except Exception:
                log.exception("set_result failed")
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


async def on_telegram_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch-all so PTB doesn't drop exceptions silently."""
    log.exception("unhandled handler error: %s", context.error)


async def process_user_text(update: Update, text: str) -> None:
    """Shared path: authorized update + text → Claude query + streamed response."""
    user_id = update.effective_user.id
    sess = await ensure_session(user_id)
    sess.chat_id = update.effective_chat.id
    sess.bot = update.get_bot()

    if sess.lock.locked():
        await update.message.reply_text("⏳ Vorherige Aufgabe läuft noch — bitte warten.")
        return

    async with sess.lock:
        try:
            await sess.client.query(text)
            await stream_response(sess, update.effective_chat.id)
        except Exception as e:
            if is_auth_error(e):
                log.error("authentication failure for user_id=%s: %s", user_id, e)
                await send_chunked(
                    sess.bot, sess.chat_id, AUTH_HELP, parse_mode=ParseMode.MARKDOWN
                )
                # Session is wedged on bad credentials — drop it so the next
                # message (after the user fixes auth) builds a fresh one.
                await close_session(user_id)
                return
            log.exception("error processing message")
            await send_chunked(sess.bot, sess.chat_id, f"❌ Error: {e}")


async def on_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
        return
    text = update.message.text or ""
    if not text.strip():
        return
    await process_user_text(update, text)


async def on_voice(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorized(update):
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

    with tempfile.TemporaryDirectory(prefix="claude-tg-voice-") as tmp:
        src = Path(tmp) / ("voice" + (Path(tg_file.file_path or "x.ogg").suffix or ".ogg"))
        try:
            await tg_file.download_to_drive(str(src))
        except Exception as e:
            log.exception("download_to_drive failed")
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

    # Echo so user sees what was understood before Claude starts.
    await msg.reply_text(f"🎙️ _{text}_", parse_mode=ParseMode.MARKDOWN)
    await process_user_text(update, text)


async def stream_response(sess: UserSession, chat_id: int) -> None:
    """Forward assistant text + a compact tool-use trace back to Telegram."""
    async for msg in sess.client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    await send_chunked(sess.bot, chat_id, block.text)
                elif isinstance(block, ToolUseBlock):
                    await send_chunked(
                        sess.bot,
                        chat_id,
                        f"🔧 {block.name}",
                    )
        elif isinstance(msg, ResultMessage):
            # signal end-of-turn
            return


# ---------- entry ----------

def main() -> None:
    if not ALLOWED_USER_IDS:
        raise SystemExit("ALLOWED_USER_IDS env var is empty — refusing to start (open bot is dangerous).")
    log.info("starting bot — workdir=%s allowed=%s", WORKDIR, sorted(ALLOWED_USER_IDS))
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(on_permission_callback, pattern=r"^p:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, on_voice))
    app.add_error_handler(on_telegram_error)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
