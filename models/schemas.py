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


class PipelineOutput(BaseModel):
    documents: List[Document]
    extracted_items: List[ExtractedItem]
    cards: List[Card]


class PipelineConfig(BaseModel):
    api_base: str
    api_key: str
    extract_model: str = "DeepSeek-V3"
    card_model: str = "DeepSeek-V3"
    dedup_threshold: float = 0.88
    min_quality: float = 0.65
    max_cards_per_item: int = 3
