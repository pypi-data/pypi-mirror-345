import datetime
from _typeshed import Incomplete
from dataclasses import dataclass
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.client import BaseSocketModeClient
from strideutils.stride_config import get_env_or_raise as get_env_or_raise
from typing import Callable

@dataclass
class SlackMessage:
    timestamp: datetime.datetime
    timestamp_id: str
    thread_ts: str | None
    sender: str
    text: str
    reactions: list[tuple[str, str]]
    @classmethod
    def from_dict(cls, message: dict): ...

class SlackClient:
    def __new__(cls): ...
    api_token: Incomplete
    client: Incomplete
    socket_mode_client: SocketModeClient | None
    def __init__(self) -> None: ...
    app_token: Incomplete
    def setup_for_listening(self) -> None: ...
    def post_message(self, message: str | list[str], channel: str, botname: str | None = None, thread_ts: str | None = None, markdown_enabled: bool = False): ...
    def upload_file(self, file_name: str, content: str) -> str: ...
    def listen_to_channel(self, message_callback: Callable[[BaseSocketModeClient, dict], None], target_channel: str) -> None: ...
    def get_prior_messages_in_channel(self, channel: str, limit: int = 200, max_age: int = -1) -> list[list[SlackMessage]]: ...
    def get_messages_in_thread(self, channel: str, thread_ts: str) -> list[SlackMessage]: ...
