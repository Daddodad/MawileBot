"""
net_utils.py — Retry wrappers for Telegram API calls.

PythonAnywhere routes outbound traffic through a proxy that occasionally
returns 503 under load. Every wrapper here retries up to MAX_RETRIES times
with exponential back-off before giving up and logging the failure.

Usage:
    from net_utils import safe_reply, safe_send, safe_photo, safe_edit, safe_sticker

    await safe_reply(update, "Hello!")
    await safe_photo(context, chat_id, image_file, caption="...")
    await safe_edit(query, "New text", reply_markup=...)
"""

import asyncio
import logging
from telegram.error import NetworkError, TimedOut, RetryAfter, BadRequest

logger = logging.getLogger(__name__)

MAX_RETRIES = 4
BASE_DELAY  = 1.5   # seconds; doubles on each attempt (1.5 → 3 → 6 → 12)


async def _retry(coro_fn, context=None):
    """
    context: optional description of the call (e.g. the text/kwargs being sent),
    used only for logging when something fails.
    """
    delay = BASE_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            return await coro_fn()
        except RetryAfter as e:
            wait = e.retry_after + 1
            logger.warning("RetryAfter: sleeping %ss (attempt %d)", wait, attempt + 1)
            await asyncio.sleep(wait)
        except BadRequest as e:
            logger.error("BadRequest (not retrying): %s | context=%r", e, context)
            return None
        except (NetworkError, TimedOut) as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning("NetworkError (attempt %d/%d): %s — retrying in %.1fs",
                               attempt + 1, MAX_RETRIES, e, delay)
                await asyncio.sleep(delay)
                delay *= 2
            else:
                logger.error("NetworkError after %d attempts: %s — giving up. context=%r",
                             MAX_RETRIES, e, context)
    return None


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------

async def safe_reply(update, text, **kwargs):
    """update.message.reply_text with retries."""
    return await _retry(lambda: update.message.reply_text(text, **kwargs))


async def safe_reply_sticker(update, sticker, **kwargs):
    """update.message.reply_sticker with retries."""
    return await _retry(lambda: update.message.reply_sticker(sticker, **kwargs))


async def safe_send(context_obj, chat_id, text, **kwargs):
    """context.bot.send_message with retries."""
    return await _retry(
        lambda: context_obj.bot.send_message(chat_id=chat_id, text=text, **kwargs),
        context={"chat_id": chat_id, "text": text[:200], "kwargs": kwargs}
    )

async def safe_photo(context, chat_id, photo, caption=None, **kwargs):
    """context.bot.send_photo with retries."""
    return await _retry(lambda: context.bot.send_photo(
        chat_id=chat_id, photo=photo, caption=caption, **kwargs))


async def safe_document(context, chat_id, document, **kwargs):
    """context.bot.send_document with retries."""
    return await _retry(lambda: context.bot.send_document(
        chat_id=chat_id, document=document, **kwargs))


async def safe_audio(context, chat_id, audio, **kwargs):
    """context.bot.send_audio with retries."""
    return await _retry(lambda: context.bot.send_audio(
        chat_id=chat_id, audio=audio, **kwargs))


async def safe_video(context, chat_id, video, **kwargs):
    """context.bot.send_video with retries."""
    return await _retry(lambda: context.bot.send_video(
        chat_id=chat_id, video=video, **kwargs))


async def safe_edit(query, text=None, **kwargs):
    """
    query.edit_message_text (or edit_message_reply_markup) with retries.
    If text is None, calls edit_message_reply_markup instead.
    """
    if text is None:
        return await _retry(lambda: query.edit_message_reply_markup(**kwargs),
                             context={"kwargs": kwargs})
    return await _retry(lambda: query.edit_message_text(text=text, **kwargs),
                         context={"text": text, "kwargs": kwargs})


async def safe_effective_reply(update, text, **kwargs):
    """update.effective_message.reply_text with retries."""
    return await _retry(lambda: update.effective_message.reply_text(text, **kwargs))