"""Application-level helpers for internship matching."""

from __future__ import annotations

from typing import Any


def ensure_list(value: Any) -> list:
    """Return a clean list regardless of input shape."""
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item is not None]
    if isinstance(value, tuple):
        return [item for item in value if item is not None]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        # Support comma-separated strings often seen in parsed text.
        if "," in stripped:
            return [part.strip() for part in stripped.split(",") if part.strip()]
        return [stripped]
    return [value]


def stringify_items(items: list[Any]) -> list[str]:
    """Convert list items to readable strings for embedding text."""
    output: list[str] = []
    for item in ensure_list(items):
        if isinstance(item, dict):
            parts = [str(v).strip() for v in item.values() if str(v).strip()]
            if parts:
                output.append(" | ".join(parts))
        else:
            text = str(item).strip()
            if text:
                output.append(text)
    return output


def unique_lower(items: list[str]) -> set[str]:
    """Return normalized lowercase set from a list of strings."""
    return {item.strip().lower() for item in items if isinstance(item, str) and item.strip()}
