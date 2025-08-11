from typing import List, Dict, Any

from models.schemas import PipelineConfig, Document, ExtractedItem, Card
from llm.client import DeepSeekClient
from pipeline.nodes.ingest import load_files
from pipeline.nodes.extract import extract_from_documents
from pipeline.nodes.generate_cards import generate_cards
from pipeline.nodes.quality import quality_gate, deduplicate_cards
from pipeline.nodes.items_from_text import chunk_documents_to_items


def run_pipeline(
    file_paths: List[str],
    keywords: List[str],
    api_base: str,
    api_key: str,
    extract_model: str,
    card_model: str,
    dedup_threshold: float,
    min_quality: float,
    max_cards_per_item: int,
) -> Dict[str, Any]:
    errors: List[str] = []
    documents: List[Document] = []
    extracted_items: List[ExtractedItem] = []
    cards: List[Card] = []

    try:
        config = PipelineConfig(
            api_base=api_base,
            api_key=api_key,
            extract_model=extract_model,
            card_model=card_model,
            dedup_threshold=dedup_threshold,
            min_quality=min_quality,
            max_cards_per_item=max_cards_per_item,
        )
    except Exception as e:
        errors.append(f"配置错误: {e}")
        return {"documents": [], "extracted_items": [], "cards": [], "errors": errors}

    try:
        documents = load_files(file_paths)
    except Exception as e:
        errors.append(f"读取文件失败: {e}")
        return {"documents": [], "extracted_items": [], "cards": [], "errors": errors}

    # 关键词为空时，直接以文本分块为条目
    if not keywords:
        try:
            extracted_items = chunk_documents_to_items(documents)
        except Exception as e:
            errors.append(f"文本分块失败: {e}")
            extracted_items = []
        # 制卡
        try:
            client = DeepSeekClient(api_base=config.api_base, api_key=config.api_key, default_model=config.card_model)
            cards = generate_cards(extracted_items, client=client, model=config.card_model, max_cards_per_item=config.max_cards_per_item)
        except Exception as e:
            errors.append(f"制卡阶段失败: {e}")
            cards = []
    else:
        # 正常抽取 → 制卡
        try:
            client = DeepSeekClient(api_base=config.api_base, api_key=config.api_key, default_model=config.extract_model)
            extracted_items = extract_from_documents(documents, keywords, client, model=config.extract_model)
        except Exception as e:
            errors.append(f"抽取阶段失败: {e}")
            extracted_items = []
        try:
            cards = generate_cards(extracted_items, client=client, model=config.card_model, max_cards_per_item=config.max_cards_per_item)
        except Exception as e:
            errors.append(f"制卡阶段失败: {e}")
            cards = []

    try:
        cards = quality_gate(cards, config.min_quality)
        cards = deduplicate_cards(cards, config.dedup_threshold)
    except Exception as e:
        errors.append(f"质量过滤/去重失败: {e}")

    return {
        "documents": [d.model_dump() for d in documents],
        "extracted_items": [i.model_dump() for i in extracted_items],
        "cards": [c.model_dump() for c in cards],
        "errors": errors,
    }
