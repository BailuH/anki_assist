import json
import re
from typing import Any, Optional


CODE_FENCE_PATTERN = re.compile(r"```(?:json|jsonc|JSON)?\s*([\s\S]*?)```", re.IGNORECASE)


def _find_balanced(text: str, open_ch: str, close_ch: str) -> Optional[str]:
    start = text.find(open_ch)
    if start == -1:
        return None
    i = start
    depth = 0
    in_str = False
    escape = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        i += 1
    return None


def safe_json_loads_any(text: str) -> Optional[Any]:
    if not text:
        return None
    # 1) fenced code block
    m = CODE_FENCE_PATTERN.search(text)
    if m:
        candidate = m.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass
    # 2) first balanced object
    obj = _find_balanced(text, "{", "}")
    if obj:
        try:
            return json.loads(obj)
        except Exception:
            pass
    # 3) first balanced list
    arr = _find_balanced(text, "[", "]")
    if arr:
        try:
            return json.loads(arr)
        except Exception:
            pass
    # 4) crude cleanup: strip leading/trailing non-json
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except Exception:
            pass
    if text.startswith("[") and text.endswith("]"):
        try:
            return json.loads(text)
        except Exception:
            pass
    return None
