import asyncio
import functools
from typing import List, Optional, Union

from telegram import Bot
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest

from strideutils.stride_config import Environment as e
from strideutils.stride_config import get_env_or_raise


def _run_async(func):
    """Decorator to run an async function synchronously."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


class TelegramClient:
    """Singleton client used to post messages to Telegram."""

    _instance = None

    def __new__(cls):
        """Creates a mew instance if one does not already exist."""
        if cls._instance is None:
            cls._instance = super(TelegramClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Prevents re-initialization if a client has already been created."""
        if hasattr(self, "bot"):
            return

        # Set up the Telegram bot with the token from environment.
        self.token = get_env_or_raise(e.TELEGRAM_BOT_TOKEN)

        # Create the bot instance with a reasonable timeout.
        request = HTTPXRequest(connection_pool_size=8, read_timeout=30, write_timeout=30)
        self.bot = Bot(token=self.token, request=request)

    @_run_async
    async def send_message(
        self,
        chat_id: Union[int, str],
        message: Union[str, List[str]],
        parse_mode: Optional[str] = ParseMode.MARKDOWN,
        thread_id: Optional[int] = None,
    ) -> str:
        """
        Sends a message to a Telegram chat. If the message is a list,
        each element is sent as a separate message, with later messages threading
        under the first message.

        Args:
            chat_id: The chat ID to send the message to.
            message: A string or list of strings to send.
            parse_mode: The parse mode for the message formatting (default: Markdown).
            thread_id: Optional thread ID to reply to

        Returns:
            The message ID of the first message sent.
        """
        # Listify the message
        messages = [message] if isinstance(message, str) else message

        # Send each message, threading with the previous
        first_message_id = None

        for msg in messages:
            result = await self.bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode=parse_mode,
                message_thread_id=thread_id,
            )

            if first_message_id is None:
                first_message_id = result.message_id

        return str(first_message_id) if first_message_id else ""

    @_run_async
    async def send_file(
        self,
        chat_id: Union[int, str],
        file_path: str,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = ParseMode.MARKDOWN,
        thread_id: Optional[int] = None,
    ) -> str:
        """
        Sends a file to a Telegram chat.

        Args:
            chat_id: The chat ID to send the file to
            file_path: The path to the file to send
            caption: Optional caption for the file
            parse_mode: The parse mode for caption formatting (default: Markdown)
            thread_id: Optional thread ID to reply to

        Returns:
            The message ID of the sent file
        """
        result = await self.bot.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=caption,
            parse_mode=parse_mode,
            message_thread_id=thread_id,
        )

        return str(result.message_id)


# Convenience functions to simplify usage.


def send_message(
    chat_id: Union[int, str],
    message: Union[str, List[str]],
    parse_mode: Optional[str] = ParseMode.MARKDOWN,
    thread_id: Optional[int] = None,
) -> str:
    """
    Synchronous function to send a Telegram message.

    Args:
        chat_id: The chat ID to send the message to
        message: A string or list of strings to send
        parse_mode: The parse mode for message formatting (default: Markdown)
        thread_id: Optional thread ID to reply to

    Returns:
        The message ID of the first message sent
    """
    client = TelegramClient()
    return client.send_message(chat_id, message, parse_mode, thread_id)  # type: ignore


def send_file(
    chat_id: Union[int, str],
    file_path: str,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = ParseMode.MARKDOWN,
    thread_id: Optional[int] = None,
) -> str:
    """
    Synchronous function to send a file via Telegram.

    Args:
        chat_id: The chat ID to send the file to
        file_path: The path to the file to send
        caption: Optional caption for the file
        parse_mode: The parse mode for caption formatting (default: Markdown)
        thread_id: Optional thread ID to reply to

    Returns:
        The message ID of the sent file
    """
    client = TelegramClient()
    return client.send_file(chat_id, file_path, caption, parse_mode, thread_id)  # type: ignore
