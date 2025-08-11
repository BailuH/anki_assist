import json
from typing import List

from llm.client import DeepSeekClient
from models.schemas import Document, ExtractResult, ExtractedItem
from pipeline.utils.json_utils import safe_json_loads_any


EXTRACT_SYSTEM = (
    "你是法律文档结构化助手。只基于提供的原文，禁止编造或补充任何未在原文出现的内容。\n"
    "任务：抽取法条/司法解释/案例/关键词命中，并返回严格 JSON，包含证据片段与定位（可用页码或字符区间）。\n"
    "要求：如果信息缺失，请留空或省略字段；items[].type ∈ {Statute, JudicialInterpretation, Case, KeywordHit}；只输出 JSON。"
)


def _build_user_prompt(text: str, keywords: List[str]) -> str:
    kwords = ", ".join(keywords)
    head = (
        f"关键词：{kwords}\n"
        "请对下列原文做结构化抽取：\n"
    )
    return head + text


def _chunk_text(text: str, chunk_size: int = 12000, overlap: int = 500) -> List[str]:
    chunks: List[str] = []
    n = len(text)
    if n <= chunk_size:
        return [text]
    start = 0
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def extract_from_documents(documents: List[Document], keywords: List[str], client: DeepSeekClient, model: str) -> List[ExtractedItem]:
    all_items: List[ExtractedItem] = []
    for doc in documents:
        for chunk in _chunk_text(doc.text):
            messages = [
                {"role": "system", "content": EXTRACT_SYSTEM},
                {"role": "user", "content": _build_user_prompt(chunk, keywords)},
            ]
            content = client.chat(messages=messages, model=model, temperature=0.0)
            if not isinstance(content, str) or not content.strip():
                continue
            data = safe_json_loads_any(content)
            if not isinstance(data, dict):
                continue
            items = data.get("items") or data.get("Items") or []
            if not isinstance(items, list):
                continue
            for it in items:
                if not isinstance(it, dict):
                    continue
                try:
                    it["docName"] = doc.name
                    all_items.append(ExtractedItem(**it))
                except Exception:
                    continue
    return all_items
