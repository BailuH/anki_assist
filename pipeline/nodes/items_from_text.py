from typing import List
from models.schemas import Document, ExtractedItem


def chunk_documents_to_items(documents: List[Document], chunk_chars: int = 1000, overlap: int = 100) -> List[ExtractedItem]:
    items: List[ExtractedItem] = []
    for doc in documents:
        text = doc.text or ""
        n = len(text)
        if n == 0:
            continue
        start = 0
        while start < n:
            end = min(n, start + chunk_chars)
            chunk = text[start:end].strip()
            if chunk:
                items.append(
                    ExtractedItem(
                        type="RawText",
                        text=chunk,
                        docName=doc.name,
                        section=None,
                        articleNo=None,
                    )
                )
            if end == n:
                break
            start = end - overlap
            if start < 0:
                start = 0
    return items
