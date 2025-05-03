from typing import Generator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from telegram import Bot, Message
from telegram.constants import ParseMode

from strideutils.telegram_connector import TelegramClient, send_file, send_message

# Test fixture and constants
TEST_MESSAGE_ID: int = 12345
TEST_CHAT_ID: str = "123456789"
TEST_MESSAGE: str = "Hello, World!"

pytestmark = pytest.mark.usefixtures("mock_environ_get")


@pytest.fixture
def mock_environ_get(monkeypatch: pytest.MonkeyPatch) -> Generator[Mock, None, None]:
    """Mock environment variable access for testing."""
    mock = Mock(return_value=None)
    monkeypatch.setattr('os.environ.get', mock)
    yield mock


@pytest.fixture
def mock_bot() -> Generator[AsyncMock, None, None]:
    """Provide a mock Telegram Bot to avoid real API calls"""
    with patch('strideutils.telegram_connector.Bot') as mock_bot_class:
        mock_instance = AsyncMock(spec=Bot)
        mock_bot_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_message() -> Message:
    """Create a mock telegram.Message object"""
    message = MagicMock(spec=Message)
    message.message_id = TEST_MESSAGE_ID
    return message


@pytest.fixture
def telegram_client(mock_bot: AsyncMock) -> Generator[TelegramClient, None, None]:
    """Provide a configured TelegramClient instance with mocked dependencies"""
    with patch("strideutils.telegram_connector.get_env_or_raise", return_value="fake_token"):
        client = TelegramClient()
        client.bot = mock_bot
        yield client


@pytest.fixture
def mock_asyncio_run() -> Generator[Mock, None, None]:
    """Mock asyncio.run to avoid actually running async code"""
    with patch('strideutils.telegram_connector.asyncio.run') as mock_run:
        yield mock_run


def test_telegram_client_singleton() -> None:
    """Test that TelegramClient maintains singleton pattern and properly handles env vars"""
    # Reset singleton state
    TelegramClient._instance = None

    with (
        patch('strideutils.telegram_connector.Bot') as mock_bot,
        patch('strideutils.telegram_connector.HTTPXRequest') as mock_request,
        patch('strideutils.telegram_connector.get_env_or_raise', return_value='fake_token'),
    ):
        # Setup the mock request
        mock_request.return_value = "mock_request"

        # Create first instance
        client1 = TelegramClient()
        # Create second instance
        client2 = TelegramClient()

        # Verify singleton behavior
        assert client1 is client2
        # Verify Bot was only initialized once
        mock_bot.assert_called_once_with(token='fake_token', request='mock_request')

    # Clean up singleton state
    TelegramClient._instance = None


def test_send_message_string(
    telegram_client: TelegramClient,
    mock_bot: AsyncMock,
    mock_message: Message,
    mock_asyncio_run: Mock,
) -> None:
    """Test sending a single message string"""
    # Setup mock return values
    mock_bot.send_message.return_value = mock_message
    mock_asyncio_run.return_value = str(TEST_MESSAGE_ID)

    # Call the method
    result = telegram_client.send_message(TEST_CHAT_ID, TEST_MESSAGE)

    # Verify asyncio.run was called with the correct async function
    assert mock_asyncio_run.called

    # Result should be the message ID
    assert result == str(TEST_MESSAGE_ID)


def test_send_message_list(
    telegram_client: TelegramClient,
    mock_bot: AsyncMock,
    mock_message: Message,
    mock_asyncio_run: Mock,
) -> None:
    """Test sending a list of messages as separate messages"""
    # Directly setting the return value here instead of using side_effect with a coroutine.
    mock_asyncio_run.return_value = str(TEST_MESSAGE_ID)

    # Call with list of messages
    messages = ["Message 1", "Message 2", "Message 3"]
    result = telegram_client.send_message(TEST_CHAT_ID, messages)

    # Should return the first message's ID
    assert result == str(TEST_MESSAGE_ID)


def test_send_file(
    telegram_client: TelegramClient,
    mock_bot: AsyncMock,
    mock_message: Message,
    mock_asyncio_run: Mock,
) -> None:
    """Test file sending functionality"""
    # Setup mocks
    mock_bot.send_document.return_value = mock_message
    mock_asyncio_run.return_value = str(TEST_MESSAGE_ID)

    # Call the method
    result = telegram_client.send_file(TEST_CHAT_ID, "test.txt", caption="Test file")

    # Verify asyncio.run was called
    assert mock_asyncio_run.called

    # Result should be the message ID
    assert result == str(TEST_MESSAGE_ID)


def test_convenience_functions(
    mock_asyncio_run: Mock,
) -> None:
    """Test the convenience wrapper functions"""
    with patch('strideutils.telegram_connector.TelegramClient') as mock_client_class:
        # Setup the mock
        mock_instance = Mock()
        mock_instance.send_message.return_value = str(TEST_MESSAGE_ID)
        mock_instance.send_file.return_value = str(TEST_MESSAGE_ID)
        mock_client_class.return_value = mock_instance

        # Test send_message wrapper
        result1 = send_message(TEST_CHAT_ID, TEST_MESSAGE)
        mock_instance.send_message.assert_called_once_with(TEST_CHAT_ID, TEST_MESSAGE, ParseMode.MARKDOWN, None)
        assert result1 == str(TEST_MESSAGE_ID)

        # Test send_file wrapper
        result2 = send_file(TEST_CHAT_ID, "test.txt", "Test caption")
        mock_instance.send_file.assert_called_once_with(
            TEST_CHAT_ID, "test.txt", "Test caption", ParseMode.MARKDOWN, None
        )
        assert result2 == str(TEST_MESSAGE_ID)


def test_run_async_decorator() -> None:
    """Test the _run_async decorator works correctly"""
    with patch('strideutils.telegram_connector.asyncio.run') as mock_run:
        # Define a mock async function
        async def mock_async_func(arg1, arg2=None):
            return f"{arg1}-{arg2}"

        # Set a simple return value for the mock
        mock_run.return_value = "test-value"

        # Apply the decorator from telegram_connector
        from strideutils.telegram_connector import _run_async

        decorated = _run_async(mock_async_func)

        # Call the decorated function
        result = decorated("test", arg2="value")

        # Verify asyncio.run was called
        mock_run.assert_called_once()

        # Check the result
        assert result == "test-value"
