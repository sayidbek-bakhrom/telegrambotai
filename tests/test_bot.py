import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from bot.handlers import start_command, help_command, handle_message, handle_callback_query
from bot import utils


@pytest.mark.asyncio
async def test_start_command_authorized():
    update = MagicMock()
    update.effective_user.id = 123
    update.effective_user.mention_html.return_value = "<a>TestUser</a>"
    update.message.reply_html = AsyncMock()
    context = MagicMock()

    with patch("bot.handlers.is_user_whitelisted", return_value=True), \
         patch("bot.handlers.log_user_input"):
        await start_command(update, context)

    update.message.reply_html.assert_called_once()
    args, kwargs = update.message.reply_html.call_args
    assert "Hi" in args[0]


@pytest.mark.asyncio
async def test_help_command_authorized():
    update = MagicMock()
    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    with patch("bot.handlers.is_user_whitelisted", return_value=True), \
         patch("bot.handlers.log_user_input"):
        await help_command(update, context)

    update.message.reply_text.assert_called_once_with("Use buttons or type your question.")


@pytest.mark.asyncio
async def test_handle_message_summarize_mode():
    update = MagicMock()
    update.effective_user.id = 123
    update.message.text = "This is long text."
    update.message.chat.send_action = AsyncMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()

    with patch("bot.handlers.is_user_whitelisted", return_value=True), \
         patch("bot.handlers.log_user_input"), \
         patch("bot.handlers.user_modes", {123: "summarize"}), \
         patch("bot.handlers.httpx.AsyncClient") as mock_client_class:

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post.return_value.json.return_value = {"summary": "Short version"}
        mock_client.__aenter__.return_value.post.return_value.raise_for_status = MagicMock()
        mock_client_class.return_value = mock_client

        await handle_message(update, context)

    update.message.reply_text.assert_called_once_with("Short version")


@pytest.mark.asyncio
async def test_callback_query_joke():
    update = MagicMock()
    update.effective_user.id = 123
    update.callback_query.data = "joke"
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    context = MagicMock()

    with patch("bot.handlers.is_user_whitelisted", return_value=True), \
         patch("bot.handlers.httpx.AsyncClient") as mock_client_class:

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.post.return_value.json.return_value = {"response": "Funny joke!"}
        mock_client.__aenter__.return_value.post.return_value.raise_for_status = MagicMock()
        mock_client_class.return_value = mock_client

        await handle_callback_query(update, context)

    update.callback_query.edit_message_text.assert_called_once_with(text="Funny joke!")


@pytest.mark.asyncio
async def test_callback_query_summarize_mode_switch():
    update = MagicMock()
    update.effective_user.id = 123
    update.callback_query.data = "summarize"
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    context = MagicMock()

    with patch("bot.handlers.is_user_whitelisted", return_value=True):
        await handle_callback_query(update, context)

    assert utils.user_modes[123] == "summarize"
    update.callback_query.edit_message_text.assert_called_once_with("📄 Send text to summarize.")
