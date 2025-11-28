"""
LLM智慧归纳与语义理解模块

提供LLM智慧归纳、语义理解关键词抽取功能
"""

from typing import List, Dict, Any, Optional
import json
from models.schemas import ExtractedItem, Card
from llm.client import DeepSeekClient


def generate_cards_with_intelligence(items: List[ExtractedItem], client: DeepSeekClient, 
                                   model: str, max_cards_per_item: int = 3) -> List[Card]:
    """
    使用LLM智慧归纳生成学习卡片
    """
    cards = []
    
    for item in items:
        try:
            # 构建归纳prompt
            prompt = f"""基于以下法律知识点，生成高质量的学习卡片：

知识点: {item.text or item.content or ""}
证据片段: {item.evidence or ""}
来源: {item.docName or "未知文档"}
类型: {item.type}

要求：
1. 保持原文准确性，不进行主观臆测
2. 对学习内容进行适当归纳，提升记忆效果  
3. 问题要清晰明确，答案要准确完整
4. 可以适当丰富表达方式，但不得改变原意

请生成问答卡片，返回JSON格式：
{{
    "question": "清晰的问题",
    "answer": "准确的答案", 
    "induction_process": "归纳思路说明"
}}
"""
            
            # 调用LLM进行智慧归纳
            response = client.generate(prompt, model=model)
            
            # 解析LLM响应
            card_data = parse_json_response(response)
            
            if card_data and card_data.get("question") and card_data.get("answer"):
                # 创建卡片并记录归纳信息
                card = Card(
                    type="basic",
                    Question=card_data["question"],
                    Answer=card_data["answer"],
                    SourceDoc=item.docName or "未知文档",
                    SourceLoc=f"第{item.pageRange[0]}页" if item.pageRange else "未知位置",
                    Tags=item.keywordsHit or [],
                    Evidence=item.evidence or item.text or "",
                    quality=0.8,  # 默认质量分数
                    llm_induction=card_data.get("induction_process", ""),
                    user_confirmed=False,  # 初始状态为未确认
                    confirmation_time=None,
                    induction_prompt="v1.0_induction"
                )
                cards.append(card)
                
        except Exception as e:
            print(f"LLM归纳失败: {e}")
            # 回退到简单卡片生成
            fallback_card = create_simple_card(item)
            cards.append(fallback_card)
    
    return cards


def extract_with_semantic_understanding(documents_text: str, keywords: List[str],
                                      client: DeepSeekClient, model: str) -> List[ExtractedItem]:
    """
    基于语义理解的关键词抽取 - 智能分段处理所有内容
    """
    try:
        # 根据文档大小智能选择处理策略
        text_length = len(documents_text)
        
        if text_length <= 15000:  # 小文档直接处理
            return _process_semantic_segment(documents_text, keywords, client, model)
        else:  # 大文档分段处理
            return _process_large_document(documents_text, keywords, client, model)
            
    except Exception as e:
        print(f"语义理解抽取失败: {e}")
        return []


def _process_semantic_segment(text_segment: str, keywords: List[str],
                             client: DeepSeekClient, model: str) -> List[ExtractedItem]:
    """处理单个文本段落的语义理解"""
    try:
        # 构建语义理解prompt - 动态调整内容长度
        segment_size = min(len(text_segment), 15000)  # 保证不超过合理长度
        content = text_segment[:segment_size]
        
        prompt = f"""请分析以下法律文档内容，找出与关键词"{', '.join(keywords)}"相关的知识点：

文档内容: {content}
关键词: {', '.join(keywords)}

要求：
1. 包括直接提及关键词的内容
2. 包括语义相关的内容（如同义词、相关概念）
3. 保持原文准确性，不添加外部信息

返回JSON格式：
{{
    "items": [
        {{
            "type": "Statute",
            "title": "知识点标题",
            "content": "内容摘要",
            "evidence": "原文证据",
            "semantic_matches": ["关键词1", "关键词2"]
        }}
    ]
}}
"""
        
        # 调用LLM进行语义理解
        response = client.generate(prompt, model=model)
        
        # 解析响应
        result = parse_json_response(response)
        items = []
        
        for item_data in result.get("items", []):
            item = ExtractedItem(
                type=item_data.get("type", "KeywordHit"),
                title=item_data.get("title"),
                text=item_data.get("content"),
                evidence=item_data.get("evidence"),
                docName="语义抽取结果",
                keywordsHit=item_data.get("semantic_matches", []),
                semantic_matches=item_data.get("semantic_matches", []),
                induction_quality=0.7,  # 默认质量
                induction_notes="语义理解抽取"
            )
            items.append(item)
        
        return items
        
    except Exception as e:
        print(f"段落语义理解失败: {e}")
        return []


def _process_large_document(documents_text: str, keywords: List[str],
                           client: DeepSeekClient, model: str) -> List[ExtractedItem]:
    """智能分段处理大文档"""
    all_items = []
    
    # 计算最优分段大小和重叠度
    text_length = len(documents_text)
    if text_length <= 50000:
        segment_size = 15000
        overlap = 1000
    else:
        segment_size = 20000
        overlap = 1500
    
    # 分段处理
    start_pos = 0
    segment_index = 0
    
    while start_pos < text_length:
        end_pos = min(start_pos + segment_size, text_length)
        
        # 提取段落，确保在合适的位置切分（避免切断句子）
        segment_text = documents_text[start_pos:end_pos]
        
        # 如果不是最后一段，尝试在句子边界切分
        if end_pos < text_length:
            # 寻找最后一个句号作为切分点
            last_period = segment_text.rfind('。')
            if last_period > len(segment_text) * 0.8:  # 如果在段落的后20%找到句号
                segment_text = segment_text[:last_period + 1]
                end_pos = start_pos + len(segment_text)
        
        print(f"处理文档段落 {segment_index + 1}: {start_pos}-{end_pos} ({len(segment_text)}字符)")
        
        # 处理该段落
        segment_items = _process_semantic_segment(segment_text, keywords, client, model)
        all_items.extend(segment_items)
        
        # 移动到下一段落
        start_pos = end_pos - overlap
        segment_index += 1
        
        # 避免处理过多段落（防止API调用过多）
        if segment_index >= 10:  # 最多处理10个段落
            print(f"文档过长，已处理前10个段落，总计{len(all_items)}个知识点")
            break
    
    return all_items


def parse_json_response(response: str) -> Dict[str, Any]:
    """解析JSON响应"""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # 如果不是JSON，返回空结果
        return {"items": []}


def create_simple_card(item: ExtractedItem) -> Card:
    """创建简单卡片（当LLM归纳失败时使用）"""
    return Card(
        type="basic",
        Question=f"什么是{item.title or '这个法律概念'}？",
        Answer=item.text or item.content or "暂无详细内容",
        SourceDoc=item.docName or "未知文档",
        SourceLoc="未知位置",
        Tags=item.keywordsHit or [],
        Evidence=item.evidence or item.text or "",
        quality=0.5,
        llm_induction="使用简单模板生成",
        user_confirmed=False,
        confirmation_time=None,
        induction_prompt="simple_template"
    )