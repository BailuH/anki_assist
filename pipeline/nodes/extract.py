import json
from typing import List

from llm.client import DeepSeekClient
from models.schemas import Document, ExtractResult, ExtractedItem
from pipeline.utils.json_utils import safe_json_loads_any
from pipeline.nodes.induction import extract_with_semantic_understanding


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
    """
    从文档中抽取知识点，支持语义理解增强
    
    Args:
        documents: 文档列表
        keywords: 关键词列表
        client: LLM客户端
        model: 使用的模型名称
        
    Returns:
        抽取的知识点列表
    """
    all_items: List[ExtractedItem] = []
    
    # 优化抽取策略：根据关键词情况选择最佳方法
    if keywords:
        # 策略1：先进行传统关键词抽取（快速、高效）
        traditional_items = []
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
                        traditional_items.append(ExtractedItem(**it))
                    except Exception:
                        continue
        
        # 策略2：对结果较少的文档进行语义理解补充
        if len(traditional_items) < len(keywords) * 2:  # 如果结果较少
            # 按文档分别进行语义理解，避免上下文过长
            for doc in documents:
                if len(doc.text) < 8000:  # 只处理较短的文档
                    semantic_items = extract_with_semantic_understanding(
                        doc.text, keywords, client, model
                    )
                    # 添加语义理解结果，避免重复
                    for semantic_item in semantic_items:
                        if not any(t.evidence == semantic_item.evidence for t in traditional_items):
                            all_items.append(semantic_item)
        
        all_items.extend(traditional_items)
    
    # 无关键词时保持原有逻辑
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
                    # 如果是语义理解已经抽取的内容，避免重复
                    if not any(existing.evidence == it.get("evidence") for existing in all_items):
                        all_items.append(ExtractedItem(**it))
                except Exception:
                    continue
    
    return all_items
