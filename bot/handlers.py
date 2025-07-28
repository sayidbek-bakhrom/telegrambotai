from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import httpx
import logging
from .utils import log_user_input, is_user_whitelisted


# URLs of Huggingface models
FASTAPI_BACKEND_URL = "http://localhost:8000/process_message"
FASTAPI_SUMMARIZE_URL = "http://localhost:8000/summarize"

logger = logging.getLogger(__name__)
user_modes = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_whitelisted(update):
        return
    user = update.effective_user
    log_user_input(user.id, "/start")

    # Create inline keyboard buttons for quick options
    keyboard = [
        [InlineKeyboardButton("🃏 Tell me a joke", callback_data="joke")],
        [InlineKeyboardButton("📄 Summarize text", callback_data="summarize")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # Greet the user and show buttons
    await update.message.reply_html(
        f"👋 Hi {user.mention_html()}! I'm your AI assistant.",
        reply_markup=markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Check whitelist
    if not await is_user_whitelisted(update):
        return
    log_user_input(update.effective_user.id, "/help")
    await update.message.reply_text("Use buttons or type your question.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_user_whitelisted(update):
        return

    user = update.effective_user
    text = update.message.text
    log_user_input(user.id, text)
    user_mode = user_modes.get(user.id, "chat")

    await update.message.chat.send_action(action="typing")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            if user_mode == "summarize":
                # Send text to summarization backend
                res = await client.post(FASTAPI_SUMMARIZE_URL, json={"text": text})
                user_modes[user.id] = "chat"
                res.raise_for_status()
                reply = res.json().get("summary", "No summary.")
            else:
                # Default chat processing
                res = await client.post(FASTAPI_BACKEND_URL, json={"user_id": user.id, "message": text})
                res.raise_for_status()
                reply = res.json().get("response", "No response.")

        # Send the AI response back to user
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error("Message handling error", exc_info=e)
        await update.message.reply_text("⚠️ Something went wrong.")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not await is_user_whitelisted(update):
        await query.answer()
        return

    data = query.data
    await query.answer()

    if data == "joke":
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    FASTAPI_BACKEND_URL,
                    json={"user_id": update.effective_user.id, "message": "Tell me a joke"},
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                joke = result.get("response", "Couldn't fetch a joke.")
        except Exception as e:
            logger.error(f"Failed to get joke: {e}")
            joke = "😕 Failed to get a joke from AI."

        await query.edit_message_text(text=joke)

    elif data == "summarize":
        user_modes[update.effective_user.id] = "summarize"
        await query.edit_message_text("📄 Send text to summarize.")
    elif data == "help_menu":
        await query.edit_message_text("Use /help for commands.")
