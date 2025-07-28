import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update

load_dotenv()
# Directory where logs will be saved
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

WHITELISTED_USERS = set(
    map(int, filter(None, os.getenv("WHITELISTED_USERS", "").split(",")))
)



def log_user_input(user_id: int, content: str):
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")
    log_path = os.path.join(LOG_DIR, f"{date_str}.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{time_str}] User {user_id}: {content.strip()}\n")

async def is_user_whitelisted(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id not in WHITELISTED_USERS:
        if update.message:
            await update.message.reply_text("🚫 You are not authorized to use this bot.")
        elif update.callback_query:
            await update.callback_query.answer("🚫 Not authorized.")
        return False
    return True
