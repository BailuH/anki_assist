import json
from typing import List

from llm.client import DeepSeekClient
from models.schemas import ExtractedItem, Card
from pipeline.utils.json_utils import safe_json_loads_any
from pipeline.nodes.induction import generate_cards_with_intelligence


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
    """
    生成学习卡片，支持LLM智慧归纳
    
    Args:
        items: 知识点列表
        client: LLM客户端
        model: 使用的模型名称
        max_cards_per_item: 每个知识点最多生成的卡片数
        
    Returns:
        生成的卡片列表
    """
    cards: List[Card] = []
    
    # 智能卡片生成策略：根据知识点类型选择最佳方法
    for item in items:
        try:
            # 策略1：优先使用传统方法（快速、稳定）
            messages = [
                {"role": "system", "content": CARD_SYSTEM},
                {"role": "user", "content": _build_card_prompt(item, max_cards_per_item)},
            ]
            content = client.chat(messages=messages, model=model, temperature=0.2)
            
            if isinstance(content, str) and content.strip():
                data = safe_json_loads_any(content)
                if isinstance(data, dict):
                    raw_cards = data.get("cards") or []
                    if isinstance(raw_cards, list):
                        for rc in raw_cards:
                            if isinstance(rc, dict):
                                q = (rc.get("Question", "") or "").strip()
                                a = (rc.get("Answer", "") or "").strip()
                                if q and a:
                                    evidence = (item.text or "").strip()
                                    qual = _to_float(rc.get("quality"))
                                    if qual <= 0.0:
                                        qual = _heuristic_quality(q, a, evidence)
                                    
                                    # 基础卡片
                                    card = Card(
                                        type=rc.get("type", "basic"),
                                        Question=q,
                                        Answer=a,
                                        SourceDoc=item.docName or "",
                                        SourceLoc=(item.articleNo or item.section or item.docketNo or ""),
                                        Tags=[item.type.lower()],
                                        Difficulty=(rc.get("Difficulty", "") or ""),
                                        Evidence=evidence,
                                        quality=qual,
                                        llm_induction="传统生成方法",
                                        user_confirmed=False,
                                        confirmation_time=None,
                                        induction_prompt="traditional_generation"
                                    )
                                    if item.keywordsHit:
                                        card.Tags.extend([f"kw:{k}" for k in item.keywordsHit])
                                    cards.append(card)
            
            # 策略2：如果传统方法结果较少，且有语义匹配，尝试LLM归纳
            elif item.semantic_matches and len(cards) < max_cards_per_item:
                try:
                    intelligent_cards = generate_cards_with_intelligence([item], client, model, 1)
                    cards.extend(intelligent_cards)
                except Exception:
                    pass  # LLM归纳失败时忽略
                    
        except Exception as e:
            print(f"卡片生成失败 for item {item.title}: {e}")
            # 当前项目已经处理完成，继续下一个
            continue
    
    return cards
