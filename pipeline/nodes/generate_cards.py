import json
from typing import List

from llm.client import DeepSeekClient
from models.schemas import ExtractedItem, Card
from pipeline.utils.json_utils import safe_json_loads_any
from pipeline.nodes.induction import generate_cards_with_intelligence


CARD_SYSTEM = (
    "你是法学生考试复习助手。基于提供的法律内容生成Anki卡片。\n\n"
    "要求：1）每张卡聚焦一个知识点 2）问题简洁明确 3）答案准确完整\n"
    "生成多种类型：问答/背诵/填空，适合期末考试复习。\n"
    "严格基于原文，不添加外部知识。每张卡要有不同角度。"
    "输出JSON：{cards:[{type:'basic'|'cloze',Question:'',Answer:'',Difficulty:'easy'|'medium'|'hard'}]}"
)


def _build_card_prompt(item: ExtractedItem, max_cards_per_item: int) -> str:
    evidence = item.text or ""
    content_type = "法条" if item.type == "Statute" else "案例" if item.type == "Case" else "概念"
    
    return f"""基于以下{content_type}内容，生成{max_cards_per_item}张不同的复习卡片：

内容：{evidence[:500]}  # 限制长度避免过载
来源：{item.docName or "未知"}
类型：{item.type}

要求：每张卡从不同角度考察，包含问答、背诵、填空等类型。
输出严格JSON格式。"""


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
    生成学习卡片，专为法学生期末复习设计
    支持多种卡片类型：知识问答、背诵记忆、填空题
    """
    cards: List[Card] = []
    
    for item in items:
        try:
            # 放宽卡片数量限制，提高制卡效率
            actual_max_cards = min(max_cards_per_item, 8)  # 直接使用8张上限
            
            # 构建复习导向的prompt
            messages = [
                {"role": "system", "content": CARD_SYSTEM},
                {"role": "user", "content": _build_card_prompt(item, actual_max_cards)},
            ]
            
            # 调用LLM生成多样化复习卡片
            content = client.chat(messages=messages, model=model, temperature=0.2)  # 降低温度提高稳定性
            
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
                                    
                                    # 创建复习专用卡片
                                    card = Card(
                                        type=rc.get("type", "basic"),
                                        Question=q,
                                        Answer=a,
                                        SourceDoc=item.docName or "",
                                        SourceLoc=(item.articleNo or item.section or item.docketNo or ""),
                                        Tags=_generate_review_tags(item, rc.get("type", "basic")),
                                        Difficulty=(rc.get("Difficulty", "") or "medium"),
                                        Evidence=evidence,
                                        quality=qual,
                                        llm_induction=f"复习卡({rc.get('type', 'basic')})",
                                        user_confirmed=False,
                                        confirmation_time=None,
                                        induction_prompt="law_student_review"
                                    )
                                    cards.append(card)
            
            # 只在卡片很少时补充生成背诵卡片
            if len(cards) < 3 and item.type == "Statute":
                try:
                    memory_cards = _generate_memory_cards(item, client, model)
                    cards.extend(memory_cards)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"卡片生成失败: {e}")
            continue
    
    return cards


def _calculate_optimal_card_count(item: ExtractedItem) -> int:
    """根据内容类型和长度计算最优卡片数量"""
    base_count = 2
    
    # 法条类内容可以多生成几张卡片
    if item.type == "Statute":
        base_count += 1
    
    # 内容较长的可以多生成
    text_length = len(item.text or "")
    if text_length > 500:
        base_count += 1
    
    return min(base_count, 4)  # 最多4张


def _generate_review_tags(item: ExtractedItem, card_type: str) -> List[str]:
    """生成复习标签"""
    tags = [item.type.lower(), "review", card_type]
    
    if item.type == "Statute":
        tags.append("memory")  # 需要记忆的
    elif item.type == "Case":
        tags.append("application")  # 应用类的
    
    if item.keywordsHit:
        tags.extend([f"kw:{k}" for k in item.keywordsHit])
    
    return tags


def _generate_memory_cards(item: ExtractedItem, client: DeepSeekClient, model: str) -> List[Card]:
    """专门为法条生成背诵记忆卡片"""
    memory_cards = []
    
    # 背诵卡1：法条原文填空
    if len(item.text or "") > 50:
        cloze_card = Card(
            type="cloze",
            Question=f"请背诵法条原文：{item.title or '相关法条'} {{c1::{item.text[:100]}...}}",
            Answer=item.text or "",
            SourceDoc=item.docName or "",
            SourceLoc=(item.articleNo or ""),
            Tags=["statute", "memory", "cloze"],
            Difficulty="hard",
            Evidence=item.text or "",
            quality=0.9,
            llm_induction="法条背诵填空卡",
            user_confirmed=False,
            confirmation_time=None,
            induction_prompt="statute_memory_cloze"
        )
        memory_cards.append(cloze_card)
    
    # 背诵卡2：法条要点提示
    hint_card = Card(
        type="basic",
        Question=f"[背诵] {item.title or '法条要点'} - 提示：{item.text[:30] if item.text else '核心内容'}",
        Answer=item.text or item.evidence or "详见法条",
        SourceDoc=item.docName or "",
        SourceLoc=(item.articleNo or ""),
        Tags=["statute", "memory", "hint"],
        Difficulty="medium",
        Evidence=item.text or "",
        quality=0.8,
        llm_induction="法条背诵提示卡",
        user_confirmed=False,
        confirmation_time=None,
        induction_prompt="statute_memory_hint"
    )
    memory_cards.append(hint_card)
    
    return memory_cards
