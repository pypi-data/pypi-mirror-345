from _typeshed import Incomplete

from strideutils.stride_config import get_env_or_raise as get_env_or_raise

class TelegramClient:
    def __new__(cls): ...
    token: Incomplete
    bot: Incomplete
    def __init__(self) -> None: ...
    async def send_message(
        self, chat_id: int | str, message: str | list[str], parse_mode: str | None = ..., thread_id: int | None = None
    ) -> str: ...
    async def send_file(
        self,
        chat_id: int | str,
        file_path: str,
        caption: str | None = None,
        parse_mode: str | None = ...,
        thread_id: int | None = None,
    ) -> str: ...

def send_message(
    chat_id: int | str, message: str | list[str], parse_mode: str | None = ..., thread_id: int | None = None
) -> str: ...
def send_file(
    chat_id: int | str,
    file_path: str,
    caption: str | None = None,
    parse_mode: str | None = ...,
    thread_id: int | None = None,
) -> str: ...
