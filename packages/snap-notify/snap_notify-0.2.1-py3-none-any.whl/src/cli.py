import click
from src import SnapNotifyClient


def parse_key_value(ctx, param, value):
    """
    Convert --data key=value CLI args into a dictionary.
    """
    result = {}
    for pair in value:
        if "=" not in pair:
            raise click.BadParameter(f"Data value '{pair}' is not in key=value format.")
        key, val = pair.split("=", 1)
        result[key] = val
    return result


@click.command()
@click.option(
    "--file", "-f", "file_path", required=True, help="Path to the template file."
)
@click.option(
    "--format", "-t", "file_type", default="yaml", help="Template format (yaml)."
)
@click.option(
    "--data",
    "-d",
    multiple=True,
    callback=parse_key_value,
    help="Interpolation variables (e.g., -d ticker=AAPL -d price=100)",
)
def send(file_path, file_type, data):
    """
    Send a Slack message using a modular DSL template with optional interpolation data.
    """
    try:
        client = SnapNotifyClient()
        client.send(file_path=file_path, file_type=file_type, data=data)
    except Exception as e:
        raise click.ClickException(f"Slack message dispatch failed: {str(e)}")


def main():
    send()
