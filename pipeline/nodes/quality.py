from typing import List
from rapidfuzz import fuzz

from models.schemas import Card


def quality_gate(cards: List[Card], min_quality: float) -> List[Card]:
    return [c for c in cards if (c.quality or 0.0) >= min_quality and c.Question and c.Answer]


def deduplicate_cards(cards: List[Card], threshold: float) -> List[Card]:
    kept: List[Card] = []
    for c in cards:
        is_dup = False
        for kc in kept:
            q_sim = fuzz.token_set_ratio(c.Question, kc.Question) / 100.0
            a_sim = fuzz.token_set_ratio(c.Answer, kc.Answer) / 100.0
            if max(q_sim, a_sim) >= threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(c)
    return kept
