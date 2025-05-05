from .parser import load_template, interpolate_template
from .core import prepare_message
from .slack_client import Slack


class SnapNotifyClient:
    def __init__(self, token: str = None):
        self.slack = Slack(token=token)

    def send(self, file_path: str, data: dict = None, file_type: str = "yaml"):
        template = load_template(file_path, file_type)
        interpolated = interpolate_template(template, runtime_data=data)
        payload = prepare_message(interpolated)
        return self.slack.send_message(payload)
