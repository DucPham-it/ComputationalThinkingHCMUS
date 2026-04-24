"""NLP preprocessing helpers for free-text search.

Purpose:
- extract structured intent from Vietnamese or English user text
- produce a normalized search plan for local DB search and external fallback
"""

from __future__ import annotations

import re
import unicodedata


ENTERTAINMENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "restaurant": (
        "ăn",
        "an",
        "quán ăn",
        "quan an",
        "nhà hàng",
        "nha hang",
        "restaurant",
        "food",
        "đồ ăn",
        "do an",
    ),
    "cafe": (
        "cafe",
        "coffee",
        "quán cafe",
        "quan cafe",
        "quán cà phê",
        "quan ca phe",
        "cà phê",
        "ca phe",
    ),
    "movie_theater": (
        "rạp",
        "rap",
        "cinema",
        "movie",
        "phim",
        "chiếu phim",
        "chieu phim",
    ),
    "park": ("công viên", "cong vien", "park"),
    "mall": (
        "trung tâm thương mại",
        "trung tam thuong mai",
        "shopping mall",
        "mall",
    ),
    "museum": ("bảo tàng", "bao tang", "museum"),
    "hotel": ("khách sạn", "khach san", "hotel"),
}

ENTERTAINMENT_LABELS: dict[str, str] = {
    "restaurant": "nha hang",
    "cafe": "quan cafe",
    "movie_theater": "rap chieu phim",
    "park": "cong vien",
    "mall": "trung tam thuong mai",
    "museum": "bao tang",
    "hotel": "khach san",
}

BUDGET_PATTERNS: dict[str, tuple[str, ...]] = {
    "low": ("rẻ", "re", "cheap", "tiết kiệm", "tiet kiem", "bình dân", "binh dan"),
    "medium": ("vừa túi tiền", "vua tui tien", "tam tam", "average"),
    "high": ("sang", "luxury", "cao cấp", "cao cap"),
}

COMPANION_PATTERNS: dict[str, tuple[str, ...]] = {
    "couple": ("2 người", "hai người", "couple", "hẹn hò", "hen ho"),
    "family": ("gia đình", "gia dinh", "family"),
    "friends": ("bạn bè", "ban be", "friends", "team"),
    "solo": ("một mình", "mot minh", "solo", "alone"),
}

TIME_PATTERNS: dict[str, tuple[str, ...]] = {
    "morning": ("sáng", "sang", "morning", "breakfast"),
    "afternoon": ("chiều", "chieu", "afternoon"),
    "evening": ("tối", "toi", "evening", "dinner"),
    "night": ("đêm", "dem", "night", "late night"),
}

STOP_WORDS = {
    "cho",
    "toi",
    "tôi",
    "minh",
    "mình",
    "o",
    "ở",
    "tai",
    "tại",
    "gan",
    "gần",
    "quanh",
    "khu",
    "vuc",
    "vực",
    "di",
    "đi",
    "choi",
    "chơi",
    "tim",
    "tìm",
    "kiem",
    "kiếm",
    "noi",
    "nơi",
    "nao",
    "nào",
    "giup",
    "giúp",
    "voi",
    "với",
    "va",
    "và",
    "the",
    "thể",
    "co",
    "có",
    "theo",
    "near",
    "around",
    "place",
    "places",
}


def _strip_accents(text: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )


def _normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = _strip_accents(lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(
        re.search(rf"(?<!\w){re.escape(pattern)}(?!\w)", text) is not None
        for pattern in patterns
    )


def _extract_first_match(text: str, pattern_map: dict[str, tuple[str, ...]]) -> str | None:
    for label, patterns in pattern_map.items():
        if _contains_any(text, patterns):
            return label
    return None


def _collect_intent_tokens(*pattern_groups: tuple[str, ...]) -> set[str]:
    tokens: set[str] = set()
    for patterns in pattern_groups:
        for phrase in patterns:
            tokens.update(token for token in phrase.split() if token)
    return tokens


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.split(r"[^\w]+", text, flags=re.UNICODE)
        if len(token) >= 2
    ]


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized_item = item.strip()
        if not normalized_item or normalized_item in seen:
            continue
        seen.add(normalized_item)
        result.append(normalized_item)
    return result


def parse_search_text(query: str) -> dict:
    """Extract structured fields and normalized search text from free-text query."""
    normalized_text = _normalize_text(query)
    entertainment_type = _extract_first_match(normalized_text, ENTERTAINMENT_PATTERNS)
    budget_level = _extract_first_match(normalized_text, BUDGET_PATTERNS)
    companion_type = _extract_first_match(normalized_text, COMPANION_PATTERNS)
    time_slot = _extract_first_match(normalized_text, TIME_PATTERNS)

    intent_tokens = set(STOP_WORDS)
    if entertainment_type:
        intent_tokens.update(_collect_intent_tokens(ENTERTAINMENT_PATTERNS[entertainment_type]))
    if budget_level:
        intent_tokens.update(_collect_intent_tokens(BUDGET_PATTERNS[budget_level]))
    if companion_type:
        intent_tokens.update(_collect_intent_tokens(COMPANION_PATTERNS[companion_type]))
    if time_slot:
        intent_tokens.update(_collect_intent_tokens(TIME_PATTERNS[time_slot]))

    query_tokens = _tokenize(normalized_text)
    content_tokens = [token for token in query_tokens if token not in intent_tokens]
    category_label = ENTERTAINMENT_LABELS.get(entertainment_type)

    local_terms = _unique(([category_label] if category_label else []) + content_tokens)
    if not local_terms and normalized_text:
        local_terms = [category_label] if category_label else [normalized_text]

    external_context_terms: list[str] = []
    if budget_level == "low":
        external_context_terms.append("gia re")
    elif budget_level == "high":
        external_context_terms.append("cao cap")
    if time_slot == "evening":
        external_context_terms.append("mo toi")
    elif time_slot == "morning":
        external_context_terms.append("buoi sang")

    external_terms = _unique(local_terms + external_context_terms)

    return {
        "entertainment_type": entertainment_type,
        "budget_level": budget_level,
        "companion_type": companion_type,
        "time_slot": time_slot,
        "normalized_query": normalized_text,
        "local_query": " ".join(local_terms).strip(),
        "external_query": " ".join(external_terms).strip(),
        "content_terms": content_tokens,
    }
