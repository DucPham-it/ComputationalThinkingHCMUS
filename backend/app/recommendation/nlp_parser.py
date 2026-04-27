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

# ĐÃ CHỈNH SƠ QUA 7 HÀM NGAY BÊN DƯỚI

ENTERTAINMENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "restaurant": (
        "ăn", "an", "eat",
        "quán ăn", "quan an", "restaurant",
        "nhà hàng", "nha hang", "dining",
        "đồ ăn", "do an", "food",
        "ăn uống", "an uong", "meal"
    ),

    "cafe": (
        "cà phê", "ca phe", "coffee",
        "quán cafe", "quan cafe", "cafe",
        "tiệm cafe", "tiem cafe", "coffee shop",
        "chill"
    ),

    "movie_theater": (
        "rạp phim", "rap phim", "cinema",
        "xem phim", "movie"
    ),

    "park": (
        "công viên", "cong vien", "park",
        "đi dạo", "di dao", "walk"
    ),

    "mall": (
        "trung tâm thương mại", "trung tam thuong mai", "mall",
        "mua sắm", "mua sam", "shopping"
    ),

    "hotel": (
        "khách sạn", "khach san", "hotel",
        "nghỉ dưỡng", "nghi duong", "resort"
    ),
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
    "low": (
        "rẻ", "cheap",
        "bình dân", "binh dan", "budget",
        "giá rẻ", "gia re", "low price",
        "tiết kiệm", "tiet kiem", "saving"
    ),

    "medium": (
        "vừa", "vua", "moderate",
        "tầm trung", "tam trung", "mid range",
        "ổn", "on", "ok", "oke", "okey", "oki", "okii","okay",
    ),

    "premium": (
        "đắt", "dat", "expensive",
        "mắc", "mac", "pricey",
        "cao cấp", "cao cap", "premium",
        "sang trọng", "sang trong", "luxury",
        "đắt đỏ", "dat do", "high-end"
    ),
}

COMPANION_PATTERNS: dict[str, tuple[str, ...]] = {
    "solo": (
        "một mình", "mot minh", "alone"
    ),

    "couple": (
        "cặp đôi", "cap doi", "couple",
        "người yêu", "nguoi yeu", "lover",
        "hẹn hò", "hen ho", "dating"
    ),

    "family": (
        "gia đình", "gia dinh", "family",
        "trẻ em", "tre em", "kids",
        "cha mẹ", "cha me", "parents"
    ),

    "friends": (
        "bạn bè", "ban be", "friends",
        "nhóm", "nhom", "group",
        "team",
        "hội bạn", "hoi ban", "crew"
    ),
}

TIME_PATTERNS: dict[str, tuple[str, ...]] = {
    "morning": (
        "sáng", "sang", "morning",
        "buổi sáng", "buoi sang", "early"
    ),

    "afternoon": (
        "trưa", "trua", "noon",
        "chiều", "chieu", "afternoon"
    ),

    "evening": (
        "tối", "toi", "evening",
        "đêm", "dem", "night",
        "tối nay", "toi nay", "tonight", "overnight",
    ),
}

DISTANCE_KEYWORDS = { # bổ sung
    "near": (
        "gần", "gan", "near",
        "gần đây", "gan day", "nearby"
    ),
    "far": (
        "xa", "far",
        "xa quá", "xa qua", "far away"
    )
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
    "trên", 
    "tren",
    "sao",
    "nay",
    "là", 
    "la",
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


"""def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(
        re.search(rf"(?<!\w){re.escape(pattern)}(?!\w)", text) is not None
        for pattern in patterns
    )""" # Hàm này tạm bỏ vì không xử lí đúng cho trường hợp "Quán ăn đắt cho cặp đôi trên 3 sao"

def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    words = text.split()
    for p in patterns:
        p_words = p.split()

        # check multi-word phrase
        for i in range(len(words) - len(p_words) + 1):
            if words[i:i+len(p_words)] == p_words:
                return True

    return False


"""def _extract_first_match(text: str, pattern_map: dict[str, tuple[str, ...]]) -> str | None:
    for label, patterns in pattern_map.items():
        if _contains_any(text, patterns):
            return label
    return None""" # Hàm này tạm bỏ vì không xử lí đúng cho trường hợp "Quán ăn đắt cho cặp đôi trên 3 sao"

def _extract_first_match(text: str, pattern_map: dict[str, tuple[str, ...]]) -> str | None:
    matches = []

    for label, patterns in pattern_map.items():
        for p in patterns:
            normalized_p = _normalize_text(p)
            if normalized_p in text:
                matches.append((label, normalized_p))

    if not matches:
        return None

    # chọn pattern dài nhất (ưu tiên "cap doi" > "cap")
    matches.sort(key=lambda x: len(x[1]), reverse=True)

    return matches[0][0]


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


def parse_recommendation_language_contract(query: str) -> dict: #working
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
      # ===== 1. handle empty =====
    if not query or not query.strip():
        return {
            "intent": "unknown",
            "entertainment_type": None,
            "budget_level": None,
            "companion_type": None,
            "time_slot": None,
            "location_hint": None,
            "distance_hint_km": None,
            "require_open_now": False,
            "min_rating": None,
            "keywords": [],
            "confidence": 0.0,
            "missing_fields": [],
        }

    # ===== 2. base parsing =====
    base = parse_search_text(query)
    text = base.get("normalized_query", "")

    # ===== helper: match phrase đúng word =====
    def contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
        return any(re.search(rf"\b{re.escape(p)}\b", text) for p in phrases)

    # ===== 3. DISTANCE =====
    distance_hint_km = None

    # "5km"
    match_km = re.search(r"(\d+)\s*km", text)
    if match_km:
        distance_hint_km = int(match_km.group(1))

    elif contains_phrase(text, DISTANCE_KEYWORDS["near"]):
        distance_hint_km = 1

    elif contains_phrase(text, DISTANCE_KEYWORDS["far"]):
        distance_hint_km = 10

    # ===== 4. RATING =====
    min_rating = None
    rating_match = re.search(r"(\d(\.\d)?)\s*sao", text)
    if rating_match:
        try:
            min_rating = float(rating_match.group(1))
        except ValueError:
            pass

    # ===== 5. OPEN NOW =====
    require_open_now = contains_phrase(text, (
        "dang mo", "mo cua", "open now", "con mo", "available"
    ))

    # ===== 6. LOCATION =====
    location_hint = None

    match_quan = re.search(r"quan\s*\d+", text)
    if match_quan:
        location_hint = match_quan.group(0)

    else:
        match_district = re.search(r"district\s*\d+", text)
        if match_district:
            location_hint = match_district.group(0)

    # ===== 7. KEYWORDS CLEAN =====
    keywords = [
        k for k in base.get("content_terms", [])
        if k not in STOP_WORDS
    ]

    # ===== 8. CONFIDENCE =====
    score = 0

    if base.get("entertainment_type"):
        score += 1
    if base.get("budget_level"):
        score += 1
    if base.get("companion_type"):
        score += 1
    if base.get("time_slot"):
        score += 1
    if distance_hint_km is not None:
        score += 1
    if min_rating is not None:
        score += 1
    if require_open_now:
        score += 1

    confidence = min(1.0, 0.2 + score * 0.1)

    # ===== 9. MISSING FIELDS =====
    missing_fields = []

    if not base.get("entertainment_type"):
        missing_fields.append("entertainment_type")

    if distance_hint_km is None:
        missing_fields.append("distance")

    if not base.get("time_slot"):
        missing_fields.append("time")

    # ===== 10. RETURN =====
    return {
        "intent": "recommend_place",
        "entertainment_type": base.get("entertainment_type"),
        "budget_level": base.get("budget_level"),
        "companion_type": base.get("companion_type"),
        "time_slot": base.get("time_slot"),
        "location_hint": location_hint,
        "distance_hint_km": distance_hint_km,
        "require_open_now": require_open_now,
        "min_rating": min_rating,
        "keywords": keywords,
        "confidence": confidence,
        "missing_fields": missing_fields,
    }


def extract_filter_fields_from_text(query: str) -> dict: #working
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
    if not query or not query.strip():
        return {}

    parsed = parse_recommendation_language_contract(query)

    filters = {
        "max_distance_km": parsed.get("distance_hint_km"),
        "min_rating": parsed.get("min_rating"),
        "budget_level": parsed.get("budget_level"),
        "preferred_types": None,
        "require_open_now": parsed.get("require_open_now"),
        "companion_type": parsed.get("companion_type"),
        "time_slot": parsed.get("time_slot"),
    }

    # convert type → list
    if parsed.get("entertainment_type"):
        filters["preferred_types"] = [parsed["entertainment_type"]]

    # remove None
    return {k: v for k, v in filters.items() if v is not None}
