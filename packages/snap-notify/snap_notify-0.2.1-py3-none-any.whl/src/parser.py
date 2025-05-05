import yaml
from jinja2 import Template
from pathlib import Path


def load_template(file_path: str, file_type: str = "yaml") -> dict:
    """
    Loads and parses a message template file.

    Args:
        file_path (str): Path to the template file.
        file_type (str): Template format (only 'yaml' supported for now).

    Returns:
        dict: Parsed template as a dictionary.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {file_path}")

    with open(path, "r") as f:
        if file_type == "yaml":
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


def interpolate_template(template: dict) -> dict:
    """
    Interpolates variables inside Slack block content using Jinja2.

    Args:
        template (dict): The loaded message template.

    Returns:
        dict: Template with interpolated strings.
    """
    variables = template.get("interpolate", {})
    blocks = template.get("blocks", [])

    def render_text(text):
        return Template(text).render(**variables)

    for block in blocks:
        if "text" in block:
            block["text"] = render_text(block["text"])
        elif block["type"] == "context" and "elements" in block:
            for el in block["elements"]:
                if "text" in el:
                    el["text"] = render_text(el["text"])

    template["blocks"] = blocks
    return template
