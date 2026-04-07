#!/usr/bin/env python3

import re
import math
import json
from typing import Union, Dict, List, Any

# Matches bare NaN / Infinity / -Infinity tokens that are NOT inside a JSON string
_NAN_RE = re.compile(r'(?<!["\w\-])(-?(?:NaN|Infinity))(?!["\w])')


def parse_json(raw_content: Union[str, list]) -> Union[Dict, List]:
    """
    This function parses a raw LLM response into a Python dict or list.
    It handles both plain strings and list content-block responses
    like [{"type": "text", "text": "..."}]) returned by the new
    langchain.agents create_agent / Gemini API.
    Strips markdown code fences if present.
    """
    # Resolve list content-blocks to a single string
    if isinstance(raw_content, list):
        text_parts = []
        for block in raw_content:
            if isinstance(block, dict):
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        raw_content = "".join(text_parts)

    cleaned = raw_content.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return sanitize_nan(parsed)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON: {e}\nRaw content (first 300 chars): {cleaned[:300]}")
        return {}


def safe_json_dumps(data: Any) -> str:
    """
    This function serialize *data* to a JSON string that is safe for strict parsers like Gemini.
    Two-pass approach:
      1. sanitize_nan() – replace float NaN/Infinity Python objects with None
      2. regex – replace any remaining bare NaN/Infinity tokens in the output string
    """
    cleaned = sanitize_nan(data)
    raw = json.dumps(cleaned)
    return _NAN_RE.sub("null", raw)


def sanitize_nan(obj: Any) -> Any:
    """
    This function recursively replace float NaN / Infinity values with None so the data
    can be safely serialized to strict JSON for Gemini API.
    """
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {k: sanitize_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_nan(v) for v in obj]
    return obj
