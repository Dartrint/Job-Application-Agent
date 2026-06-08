"""Helpers for parsing and normalizing LLM JSON responses"""

import json
import re


def parse_llm_json(text: str) -> dict:
    """Parse JSON from an LLM response, tolerating extra text."""
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Failed to parse LLM response as JSON")


def normalize_string_list(items: list) -> list[str]:
    """Convert mixed LLM list items (strings or dicts) to plain strings."""
    normalized = []
    for item in items:
        if isinstance(item, str):
            normalized.append(item.strip())
        elif isinstance(item, dict):
            parts = []
            for key in (
                "name",
                "degree",
                "title",
                "university",
                "achievement",
                "tech_stack",
                "description",
            ):
                value = item.get(key)
                if value:
                    if isinstance(value, list):
                        parts.append(", ".join(str(v) for v in value))
                    else:
                        parts.append(str(value))
            normalized.append(" — ".join(parts) if parts else str(item))
        elif item is not None:
            normalized.append(str(item))
    return normalized


def normalize_tips(tips: list) -> list[str]:
    """Convert LLM tip objects to plain strings."""
    normalized = []
    for item in tips:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            tip = item.get("tip", "")
            if tip:
                normalized.append(tip)
    return normalized


def normalize_string_field(value) -> str | None:
    """Normalize optional string fields from LLM output."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value)
