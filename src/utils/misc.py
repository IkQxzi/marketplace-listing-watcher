import time


def get_timestamp() -> str:
    """Get filename-friendly timestamp (accurate to minutes)."""

    # Uses dash instead of dot between H & M
    # to prevent suffix problems with pathlib
    return time.strftime("%Y-%m-%d_%H-%M")


def get_text_timestamp() -> str:
    """Get non-filename-friendly timestamp (accurate to seconds)"""

    return time.strftime("%Y-%m-%d at %H:%M:%S")


def snake_to_camel_case(s: str) -> str:
    """Convert a string from snake-case to camel-case."""

    s_parts = s.split("_")

    # First letter uncapitalised
    return s_parts[0] + "".join([part.capitalize() for part in s_parts[1:]])
