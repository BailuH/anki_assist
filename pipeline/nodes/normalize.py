import re
from typing import List
from models.schemas import Document


def normalize_and_segment(doc: Document) -> List[str]:
    text = doc.text
    # 去除多余空白与页码样式（简单启发式）
    text = re.sub(r"\u00a0", " ", text)
    text = re.sub(r"\s+", " ", text)
    # 分句：中文标点 + 换行
    sentences = re.split(r"(?<=[。！？；])\s+", text)
    # 保留较长句子
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences
