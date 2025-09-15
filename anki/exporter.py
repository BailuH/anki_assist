import os
from typing import List, Any
import genanki

from .templates import basic_model, cloze_model

# 获取对象的键对应的值，如果对象没有键则返回空字符串
def _get(card: Any, key: str, default: str = "") -> Any:
    if isinstance(card, dict):
        return card.get(key, default)
    return getattr(card, key, default)

# 把任意字段规范成字符串，列表会用,连接。常用于将 Question/Answer/Tags/Evidence 等转成字符串字段供 genanki 使用。
def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        # 把**可迭代对象**里的元素用指定字符串（这里叫分隔符）拼接成一个新字符串。
        return ", ".join(str(v) for v in value)
    return str(value)


def _format_tags(card: Any) -> str:
    # Accept list or comma-separated string; render as span badges
    tags_val = _get(card, "Tags", [])
    tags: List[str]
    if isinstance(tags_val, list):
        tags = [str(t).strip() for t in tags_val if str(t).strip()]
    else:
        tags = [t.strip() for t in str(tags_val).split(",") if t.strip()]
    if not tags:
        return ""
    return " ".join(f"<span class='tag'>{t}</span>" for t in tags)


def _format_difficulty(card: Any) -> str:
    diff = _get(card, "Difficulty", "") or ""
    d = str(diff).strip().lower()
    cls = "diff-easy" if d in ("easy", "简单", "易") else (
        "diff-medium" if d in ("medium", "中等", "中") else (
            "diff-hard" if d in ("hard", "困难", "难") else "diff-unknown"
        )
    )
    label = diff if diff else ""
    return f"<span class='badge {cls}'>{label}</span>" if label else ""


def export_to_apkg(deck_name: str, cards: List[Any], output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    deck = genanki.Deck(deck_id=2059400110, name=deck_name)
    basic = basic_model()
    cloze = cloze_model()

    for c in cards:
        ctype = (_get(c, "type", "basic") or "basic").lower()
        tags_html = _format_tags(c)
        diff_html = _format_difficulty(c)
        if ctype == "cloze":
            note = genanki.Note(
                model=cloze,
                fields=[
                    _as_text(_get(c, "Answer", "")),  # Text with cloze
                    _as_text(_get(c, "SourceDoc", "")),
                    _as_text(_get(c, "SourceLoc", "")),
                    tags_html,
                    diff_html,
                    _as_text(_get(c, "Evidence", "")),
                ],
            )
        else:
            note = genanki.Note(
                model=basic,
                fields=[
                    _as_text(_get(c, "Question", "")),
                    _as_text(_get(c, "Answer", "")),
                    _as_text(_get(c, "SourceDoc", "")),
                    _as_text(_get(c, "SourceLoc", "")),
                    tags_html,
                    diff_html,
                    _as_text(_get(c, "Evidence", "")),
                ],
            )
        deck.add_note(note)

    pkg = genanki.Package(deck)
    apkg_path = os.path.join(output_dir, f"{deck_name}.apkg")
    pkg.write_to_file(apkg_path)
    return apkg_path
