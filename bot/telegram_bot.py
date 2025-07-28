import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import start_command, help_command, handle_message, handle_callback_query


load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set!")


def main():
    # Configure logging to display INFO level messages and above
    logging.basicConfig(level=logging.INFO)

    # Ensure the bot token is available
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

    # Create the Application (bot) instance with the token
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Register message handler to process all text messages that are NOT commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register callback query handler (for inline button presses, etc.)
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    logging.info("Telegram bot running.")

    # Start polling Telegram updates; allowed_updates=[] means all update types are received
    app.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()