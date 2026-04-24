"""NLP preprocessing helpers for free-text search.

Owner:
- TV3: NLP Field Extraction.

File input:
- Raw natural-language query from recommendation search.
- Supported text can be Vietnamese with accents, Vietnamese without accents, or
  common English keywords.

File output:
- Normalized intent/filter fields used by recommender and filtering modules.
- Backward-compatible search text fields for the existing local search flow.

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
    """Extract structured fields and normalized search text from free-text query.

    Owner:
    - TV3 maintains this helper because it is the current NLP entry point.

    Input:
    - query: raw Vietnamese/English natural-language request from Home search.
      Empty string is allowed and must not raise an exception.

    Output:
    - dict with:
      - entertainment_type: normalized category or None
      - budget_level: low/medium/high or None
      - companion_type: solo/couple/family/friends or None
      - time_slot: morning/afternoon/evening/night or None
      - normalized_query: accent-stripped lowercase text
      - local_query: terms optimized for local Supabase search
      - external_query: terms reserved for external search fallback
      - content_terms: remaining meaningful tokens after intent extraction

    TODO TV3:
    - Keep this function stable for existing code.
    - Move richer parsing into parse_recommendation_language_contract.
    """
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


def parse_recommendation_language_contract(query: str) -> dict:
    """TODO TV3: full NLP contract for natural-language recommendation input.

    Owner:
    - TV3.

    Input:
    - query: raw user text, for example "toi muon quan an re gan quan 5 toi nay".
      The function must accept:
      - Vietnamese with accents
      - Vietnamese without accents
      - short English keywords
      - empty or unclear text

    Output:
    - dict with keys:
      - intent: recommendation, route, compare, unknown
      - entertainment_type: restaurant/cafe/museum/park/mall/movie_theater/hotel or None
      - budget_level: low/medium/high or None
      - companion_type: solo/couple/family/friends/kids or None
      - time_slot: morning/afternoon/evening/night/weekend or None
      - location_hint: free text location such as "quan 5"
      - distance_hint_km: numeric distance if user mentions "trong 5km", "gan day", etc.
      - require_open_now: true if user asks for places open now
      - min_rating: numeric 0..5 if user asks "tren 4 sao"
      - keywords: remaining useful words for text search
      - confidence: 0..1
      - missing_fields: list[str] that frontend can ask again

    Implementation note:
    - Keep parse_search_text backward-compatible.
    - This function is intentionally empty so AI/NLP owner can implement and test it.
    """
    pass


def extract_filter_fields_from_text(query: str) -> dict:
    """TODO TV3: extract fields that should merge with explicit UI filters.

    Owner:
    - TV3 owns extraction.
    - TV4 consumes the output in build_filter_plan.

    Input:
    - query: raw natural-language text from recommendation search.
      Examples:
      - "cafe yen tinh duoi 5km"
      - "di voi gia dinh, dang mo cua, tren 4 sao"

    Output:
    - dict containing only filter fields found in text:
      - max_distance_km
      - min_rating
      - budget_level
      - preferred_types
      - require_open_now
      - companion_type
      - start_time or time_slot

    Conflict rule:
    - UI filters win over NLP fields when both are present.
    """
    pass
