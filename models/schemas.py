from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class Document(BaseModel):
    name: str
    path: str
    text: str
    pages: int = 0


ItemType = Literal["Statute", "JudicialInterpretation", "Case", "KeywordHit", "RawText"]


class ExtractedItem(BaseModel):
    type: ItemType
    title: Optional[str] = None
    articleNo: Optional[str] = None
    source: Optional[str] = None
    section: Optional[str] = None
    caseName: Optional[str] = None
    court: Optional[str] = None
    judgmentDate: Optional[str] = None
    docketNo: Optional[str] = None
    holding: Optional[str] = None
    reasoning: Optional[str] = None
    text: Optional[str] = None
    pageRange: Optional[List[int]] = None
    charSpan: Optional[List[int]] = None
    keywordsHit: Optional[List[str]] = None
    docName: Optional[str] = None
    # 新增优化字段 - 语义理解相关
    semantic_matches: Optional[List[str]] = None  # 语义匹配的相关关键词
    induction_quality: Optional[float] = None  # LLM归纳质量评分
    induction_notes: Optional[str] = None  # 归纳过程说明
    structural_score: Optional[float] = None  # 文档结构重要性评分


class ExtractResult(BaseModel):
    docName: str
    items: List[ExtractedItem]


class Card(BaseModel):
    type: Literal["basic", "cloze"] = "basic"
    Question: str
    Answer: str
    SourceDoc: str
    SourceLoc: str
    Tags: List[str] = Field(default_factory=list)
    Difficulty: Optional[str] = None
    Evidence: Optional[str] = None
    quality: float = 0.0
    # 新增优化字段 - LLM智慧归纳相关
    llm_induction: str = ""  # LLM归纳过程描述
    user_confirmed: bool = False  # 用户确认状态
    confirmation_time: Optional[str] = None  # 确认时间（字符串格式避免datetime序列化问题）
    induction_prompt: str = ""  # 使用的归纳prompt版本

# 入口点（entrypoint）需要的数据类型
class PipelineInput(BaseModel):
    file_paths: List[str]
    keywords: List[str]
    api_base: str
    api_key: str
    extract_model: str
    card_model: str
    dedup_threshold: float
    min_quality: float
    max_cards_per_item: int

class PipelineOutput(BaseModel):
    documents: List[Document]
    extracted_items: List[ExtractedItem]
    cards: List[Card]
    errors : List[str]


class PipelineConfig(BaseModel):
    api_base: str
    api_key: str
    extract_model: str = "DeepSeek-V3"
    card_model: str = "DeepSeek-V3"
    dedup_threshold: float = 0.88
    min_quality: float = 0.65
    max_cards_per_item: int = 3
