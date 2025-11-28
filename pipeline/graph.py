from models.schemas import PipelineConfig, PipelineOutput, PipelineInput
from llm.client import DeepSeekClient
from pipeline.nodes.ingest import load_files
from pipeline.nodes.extract import extract_from_documents
from pipeline.nodes.generate_cards import generate_cards
from pipeline.nodes.quality import quality_gate, deduplicate_cards
from pipeline.nodes.items_from_text import chunk_documents_to_items

from langgraph.func import entrypoint
from langgraph.checkpoint.memory import InMemorySaver

@entrypoint(checkpointer = InMemorySaver()) #内存检查点，短期
def run_pipeline(input: PipelineInput) -> PipelineOutput:
    errors = []
    try:
        config = PipelineConfig(
            api_base=input.api_base,
            api_key=input.api_key,
            extract_model=input.extract_model,
            card_model=input.card_model,
            dedup_threshold=input.dedup_threshold,
            min_quality=input.min_quality,
            max_cards_per_item=input.max_cards_per_item,
        )
    except Exception as e:
        errors.append(f"配置错误: {e}")
        return {"documents": [], "extracted_items": [], "cards": [], "errors": errors}

    try:
        documents = load_files(input.file_paths)
    except Exception as e:
        errors.append(f"读取文件失败: {e}")
        return {"documents": [], "extracted_items": [], "cards": [], "errors": errors}

    # 关键词为空时，直接以文本分块为条目
    if not input.keywords:
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
        # 正常抽取 → 制卡（使用优化后的功能）
        try:
            client = DeepSeekClient(api_base=config.api_base, api_key=config.api_key, default_model=config.extract_model)
            extracted_items = extract_from_documents(documents, input.keywords, client, model=config.extract_model)
        except Exception as e:
            errors.append(f"抽取阶段失败: {e}")
            extracted_items = []
        try:
            # 使用增强的卡片生成功能（支持LLM智慧归纳）
            cards = generate_cards(extracted_items, client=client, model=config.card_model, max_cards_per_item=config.max_cards_per_item)
        except Exception as e:
            errors.append(f"制卡阶段失败: {e}")
            cards = []

    try:
        cards = quality_gate(cards, config.min_quality)
        cards = deduplicate_cards(cards, config.dedup_threshold)
    except Exception as e:
        errors.append(f"质量过滤/去重失败: {e}")


    output = PipelineOutput(documents=[d.model_dump() for d in documents],
                            extracted_items=[i.model_dump() for i in extracted_items],
                            cards=[c.model_dump() for c in cards],
                            errors=errors)
    
    # 为了支持检查点，返回一个可json序列化的对象
    return output
