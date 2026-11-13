"""Shared helpers for exporters."""
import os
import re


def bool_to_str(value):
    """Render a boolean the way spreadsheets expect."""
    return "true" if value else "false"


def chunked(items, size):
    """Yield successive chunks of ``size`` items."""
    for start in range(0, len(items), size):
        yield items[start:start + size]


def slugify(text):
    """Turn arbitrary text into a filesystem-friendly slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def ensure_dir(path):
    """Create the parent directory of ``path`` if it is missing."""
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    return path
