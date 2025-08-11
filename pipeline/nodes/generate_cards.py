import json
from typing import List

from llm.client import DeepSeekClient
from models.schemas import ExtractedItem, Card
from pipeline.utils.json_utils import safe_json_loads_any


CARD_SYSTEM = (
    "你是制卡助手。只使用提供的证据片段生成学习卡片，禁止引入原文之外的解释或扩展。\n"
    "输出多种问法的 Q/A 与（可选）Cloze，覆盖法条要点、解释要点、案例裁判要旨。\n"
    "每张卡输出字段：type(\"basic\"|\"cloze\"), Question, Answer, Difficulty(可选), quality(0~1 数值)。\n"
    "Question 简洁；Answer 必须能在证据中原文核对。最多 3 张卡/知识点。严格只输出 JSON。"
)


def _build_card_prompt(item: ExtractedItem, max_cards_per_item: int) -> str:
    evidence = item.text or ""
    source = item.title or item.source or item.caseName or ""
    payload = {
        "instruction": {
            "max_cards": max_cards_per_item,
            "type": item.type,
            "source": source,
            "docName": item.docName,
            "articleNo": item.articleNo,
        },
        "evidence": evidence,
        "expected_schema": {"cards": [{"type": "basic", "Question": "...", "Answer": "...", "Difficulty": "easy|medium|hard", "quality": 0.8}]}
    }
    return json.dumps(payload, ensure_ascii=False)


def _to_float(value) -> float:
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.strip())
    except Exception:
        return 0.0
    return 0.0


def _heuristic_quality(question: str, answer: str, evidence: str) -> float:
    if not question or not answer:
        return 0.0
    ans_len = len(answer)
    cov = min(ans_len / 80.0, 1.0)
    ev_bonus = 0.1 if evidence and len(evidence) >= 20 else 0.0
    base = 0.55
    score = max(0.0, min(1.0, base + 0.35 * cov + ev_bonus))
    return score


def generate_cards(items: List[ExtractedItem], client: DeepSeekClient, model: str, max_cards_per_item: int) -> List[Card]:
    cards: List[Card] = []
    for it in items:
        messages = [
            {"role": "system", "content": CARD_SYSTEM},
            {"role": "user", "content": _build_card_prompt(it, max_cards_per_item)},
        ]
        content = client.chat(messages=messages, model=model, temperature=0.2)
        if not isinstance(content, str) or not content.strip():
            continue
        data = safe_json_loads_any(content)
        if not isinstance(data, dict):
            continue
        raw_cards = data.get("cards") or []
        if not isinstance(raw_cards, list):
            continue
        for rc in raw_cards:
            if not isinstance(rc, dict):
                continue
            try:
                q = (rc.get("Question", "") or "").strip()
                a = (rc.get("Answer", "") or "").strip()
                if not q or not a:
                    continue
                evidence = (it.text or "").strip()
                qual = _to_float(rc.get("quality"))
                if qual <= 0.0:
                    qual = _heuristic_quality(q, a, evidence)
                c = Card(
                    type=rc.get("type", "basic"),
                    Question=q,
                    Answer=a,
                    SourceDoc=it.docName or "",
                    SourceLoc=(it.articleNo or it.section or it.docketNo or ""),
                    Tags=[it.type.lower()],
                    Difficulty=(rc.get("Difficulty", "") or ""),
                    Evidence=evidence,
                    quality=qual,
                )
                if it.keywordsHit:
                    c.Tags.extend([f"kw:{k}" for k in it.keywordsHit])
                cards.append(c)
            except Exception:
                continue
    return cards
