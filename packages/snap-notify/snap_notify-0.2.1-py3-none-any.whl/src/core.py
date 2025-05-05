def prepare_message(template: dict) -> dict:
    """
    Extracts metadata and prepares a full Slack message payload.

    Args:
        template (dict): Interpolated template dictionary.

    Returns:
        dict: Slack message payload with metadata.
    """
    channel = template.get("channel")
    thread_ts = template.get("thread_ts")  # If present, it's a reply
    blocks = template.get("blocks", [])
    is_parent = template.get("is_parent", True)

    if not channel:
        raise ValueError("Missing required 'channel' field in template.")

    payload = {
        "channel": channel,
        "blocks": blocks,
    }

    if not is_parent and thread_ts:
        payload["thread_ts"] = thread_ts

    return payload
