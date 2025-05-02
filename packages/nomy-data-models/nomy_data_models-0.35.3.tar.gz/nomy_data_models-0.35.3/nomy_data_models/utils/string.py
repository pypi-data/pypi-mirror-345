"""String utility functions."""

import re


def to_snake_case(text: str) -> str:
    """Convert a string to snake_case.

    Args:
        text: The string to convert

    Returns:
        str: The snake_case version of the string
    """
    # Replace any non-alphanumeric characters with underscores
    s1 = re.sub(r"[^a-zA-Z0-9]", "_", text)
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s2 = re.sub(r"([a-z])([A-Z])", r"\1_\2", s1)
    # Convert to lowercase
    return s2.lower()
