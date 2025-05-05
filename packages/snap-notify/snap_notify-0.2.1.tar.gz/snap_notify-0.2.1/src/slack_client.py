from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()


class Slack:
    def __init__(self, token=None):
        token = token or os.getenv("SLACK_BOT_TOKEN")
        if not token:
            raise EnvironmentError("Slack bot token must be provided.")
        self.client = WebClient(token=token)

    def send_message(self, payload: dict):
        return self.client.chat_postMessage(**payload)
