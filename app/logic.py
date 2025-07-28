from collections import defaultdict, deque
from openai import OpenAI
from config import HF_TOKEN


# Store per-user message history (last 10 exchanges per user)
conversation_history = defaultdict(lambda: deque(maxlen=10))

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


def get_history(user_id):
    """
    Get the conversation history for a given user.
    """
    return conversation_history[user_id]


def add_user_message(user_id, content):
    """
    Add a user message to the conversation history.
    """
    conversation_history[user_id].append({
        "role": "user",
        "content": content})

def add_bot_response(user_id, content):
    """
    Add the bot's response to the conversation history.
    """
    conversation_history[user_id].append({
        "role": "assistant",
        "content": content})


def get_client():
    """
    Return the configured Hugging Face client.
    """
    return client
