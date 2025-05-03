import datetime
import os
from dataclasses import dataclass
from typing import Callable, List, Optional, Union

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from strideutils.stride_config import Environment as e
from strideutils.stride_config import get_env_or_raise


@dataclass
class SlackMessage:
    timestamp: datetime.datetime
    timestamp_id: str
    thread_ts: Optional[str]
    sender: str
    text: str
    reactions: List[tuple[str, str]]
    # reactions is a list of tuples of the form (user_id, reaction_name)

    @classmethod
    def from_dict(cls, message: dict):
        # reaction is of the form {'name': 'thumbsup', 'users': ['U01RZ9Q4G3Z'], 'count': 1}
        # we want to parse it to a list of tuples of the form (user_id, reaction_name)
        reactions = [
            (user, reaction["name"]) for reaction in message.get("reactions", []) for user in reaction["users"]
        ]
        return cls(
            timestamp=datetime.datetime.fromtimestamp(float(message["ts"])),
            timestamp_id=message["ts"],
            thread_ts=message.get("thread_ts", None),
            sender=message["user"],
            text=message["text"],
            reactions=reactions,
        )


class SlackClient:
    """
    Singleton client used to post messages to slack
    """

    _instance = None

    def __new__(cls):
        # Creates a new instance if one does not already exist
        if cls._instance is None:
            cls._instance = super(SlackClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization if a client has already been created
        if hasattr(self, "client"):
            return

        self.api_token = get_env_or_raise(e.STRIDEBOT_API_TOKEN)
        self.client = WebClient(token=self.api_token)
        self.socket_mode_client: SocketModeClient | None = None

    def setup_for_listening(self):
        """
        Sets up the client for listening to slack messages using SocketMode.
        Without calling this function, a Socket Mode client will not be created.

        We don't create the client in the constructor to avoid unnecessary overhead,
        as not all processes will want to initiate socket connections.
        """
        self.app_token = get_env_or_raise(e.STRIDEBOT_APP_TOKEN)
        socket_mode_client = SocketModeClient(app_token=self.app_token, web_client=self.client)
        print("Socket mode client created")
        self.socket_mode_client = socket_mode_client

    def post_message(
        self,
        message: Union[str, List[str]],
        channel: str,
        botname: Optional[str] = None,
        thread_ts: Optional[str] = None,
        markdown_enabled: bool = False,
    ):
        """
        Posts a slack message to the given channel
        If the message is an array, this will post each element of the array as a thread

        Returns the thread_ts to allow chaining messages
        """
        # Allow optional channel overrides via an environment variable
        channel = os.environ.get(e.SLACK_CHANNEL_OVERRIDE, default=channel)

        # Listify
        messages = [message] if type(message) is str else message

        # Post each message, threading with the previous
        thread_ts = None or thread_ts
        for msg in messages:
            response = self.client.chat_postMessage(
                channel=channel,
                text=msg,
                thread_ts=thread_ts,
                username=botname,
                mrkdwn=markdown_enabled,
            )
            if thread_ts is None:  # API advises to use parent IDs instead of child's
                thread_ts = response["ts"]

        return thread_ts

    def upload_file(self, file_name: str, content: str) -> str:
        """
        This uploads a file and returns a link that can be used to embed a file in slack
        Ex:
            url = upload_file("test.txt", "Hello World")
            post_msg(f"<{url}|This is a file>", channel="#alerts-debug")
        """
        slack_file = self.client.files_upload_v2(filename=file_name, content=content)
        file_link = slack_file["file"]["permalink"]
        return file_link

    def listen_to_channel(
        self, message_callback: Callable[[BaseSocketModeClient, dict], None], target_channel: str
    ) -> None:
        """
        Starts a listener for slack messages in the specified channel using SocketMode.
        Calls `message_callback` with the event data when a message is received.
        """
        if not self.socket_mode_client:
            self.setup_for_listening()
        assert self.socket_mode_client is not None, "Failed to initialize socket mode client"

        def handle_message(client: BaseSocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # ack the request immediately
                response = SocketModeResponse(envelope_id=req.envelope_id)
                if req.payload["event"]["channel"] == target_channel:
                    client.send_socket_mode_response(response)
                    message_callback(client, req.payload["event"])

        self.socket_mode_client.socket_mode_request_listeners.append(handle_message)
        self.socket_mode_client.connect()

    def get_prior_messages_in_channel(self, channel: str, limit: int = 200, max_age=-1) -> List[List[SlackMessage]]:
        """
        Fetch the most recent messages from a Slack channel.
        Args:
            channel (str): ID of the Slack channel.
            limit (int): Maximum number of messages to fetch (default: 100).
            max_age (int): Maximum age in seconds of messages to fetch (default: -1, fetch all messages).
        Returns:
            List[List[SlackMessages]]: A list of list of message objects.
                Each element in the array is a list of messages in that thread.
        """
        # fetch message history
        response = self.client.conversations_history(channel=channel, limit=limit)

        raw_messages = response.get("messages", [])
        channel_messages: list[list[SlackMessage]] = []
        now_time = datetime.datetime.now()
        for raw_message in raw_messages:
            # check if message is too old
            if max_age > 0:
                message_time = datetime.datetime.fromtimestamp(float(raw_message["ts"]))
                if (now_time - message_time).total_seconds() > max_age:
                    continue

            if 'thread_ts' in raw_message:
                # make sure we haven't processed this thread already.
                # This happens when multiple messages from the same thread are returned in `response`.
                # After we process the first message, because we call `conversations_replies` below,
                # we will have already processed the whole thread.
                thread_ts = raw_message['thread_ts']
                if thread_ts in [msg[0].thread_ts for msg in channel_messages]:
                    continue

                # this is a thread, fetch the full thread
                thread_replies = self.client.conversations_replies(channel=channel, ts=thread_ts)
                thread_msgs = []
                for reply in thread_replies["messages"]:
                    thread_msg = SlackMessage.from_dict(reply)
                    thread_msgs.append(thread_msg)
                channel_messages.append(thread_msgs)

            else:
                # this is not a thread
                slack_msg = SlackMessage.from_dict(raw_message)
                channel_messages.append([slack_msg])

        return channel_messages

    def get_messages_in_thread(self, channel: str, thread_ts: str) -> List[SlackMessage]:
        """
        Fetch all the messages in a thread, ordered by timestamp.
        Args:
            channel (str): ID of the Slack channel.
            thread_ts (str): ID of the thread to fetch.
        Returns:
            List[SlackMessages]]: A list of messages in that thread.
        """
        response = self.client.conversations_replies(channel=channel, ts=thread_ts)
        return [SlackMessage.from_dict(msg) for msg in response["messages"]]
