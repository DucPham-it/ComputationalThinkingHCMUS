"""NLP preprocessing helpers for free-text search.

Owner:
- TV3: NLP Field Extraction.

File input:
- Raw natural-language query from recommendation search.
- Supported text: Vietnamese with accents, Vietnamese without accents,
  common English keywords.

File output:
- Normalized intent/filter fields used by recommender and filtering modules.
- Backward-compatible search text fields for the existing local search flow.

Approach — Hybrid (Rule-based → TF-IDF → Fuzzy Edit Distance):
  Layer 1 (Rule): exact phrase-match against ENTERTAINMENT_PATTERNS dict.
                  Fast and high-precision for known keywords.
  Layer 2 (TF-IDF): cosine similarity of query token bag against per-category
                    corpus.  Handles synonyms and paraphrases that share
                    vocabulary with the corpus.
  Layer 3 (Fuzzy): per-token Levenshtein edit-distance against a curated
                   set of anchor words per category.  Catches typos,
                   transliterations, and loanwords (espresso → cafe,
                   cofee → cafe, resturant → restaurant).

When all three layers return None the function returns None (no forced guess).
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any

# ============================================================
# PATTERN DICTIONARIES
# ============================================================

ENTERTAINMENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "restaurant": (
        "ăn", "an", "eat",
        "quán ăn", "quan an", "restaurant",
        "nhà hàng", "nha hang", "dining",
        "đồ ăn", "do an", "food",
        "ăn uống", "an uong", "meal",
        "bun", "pho", "com", "banh", "lau", "nuong",
        "bún", "phở", "cơm", "bánh", "lẩu", "nướng",
        "pizza", "burger", "sushi", "noodle",
    ),
    "cafe": (
        "cà phê", "ca phe", "coffee",
        "quán cafe", "quan cafe", "cafe",
        "tiệm cafe", "tiem cafe", "coffee shop",
        "chill", "tra sua", "trà sữa", "tra da", "trà đá",
        "espresso", "latte", "cappuccino", "matcha", "beverage",
    ),
    "movie_theater": (
        "rạp phim", "rap phim", "cinema",
        "xem phim", "movie", "film",
    ),
    "park": (
        "công viên", "cong vien", "park",
        "đi dạo", "di dao", "walk", "picnic", "outdoor", "garden",
    ),
    "mall": (
        "trung tâm thương mại", "trung tam thuong mai", "mall",
        "mua sắm", "mua sam", "shopping", "siêu thị", "sieu thi",
    ),
    "hotel": (
        "khách sạn", "khach san", "hotel",
        "nghỉ dưỡng", "nghi duong", "resort", "hostel",
    ),
    "museum": (
        "bảo tàng", "bao tang", "museum",
        "triển lãm", "trien lam", "exhibition",
    ),
    "bar": (
        "bar", "pub", "beer", "bia", "club",
        "nightlife", "ban dem", "ban đêm",
    ),
    "spa": (
        "spa", "massage", "mát xa", "mat xa",
        "thư giãn", "thu gian", "relaxation",
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
    "bar": "bar quan nhau",
    "spa": "spa massage",
}

BUDGET_PATTERNS: dict[str, tuple[str, ...]] = {
    "low": (
        "rẻ", "re", "cheap", "tiết kiệm", "tiet kiem",
        "bình dân", "binh dan", "budget", "giá rẻ", "gia re",
        "low price", "saving",
    ),
    "medium": (
        "vừa túi tiền", "vua tui tien", "tam tam", "average",
        "vừa", "vua", "moderate", "tầm trung", "tam trung",
        "mid range", "ổn", "ok", "oke", "okey", "oki", "okii", "okay",
    ),
    "high": (
        "sang", "luxury", "cao cấp", "cao cap", "premium",
        "expensive", "high-end", "đắt", "dat", "mắc", "mac",
        "pricey", "sang trọng", "sang trong", "đắt đỏ",
    ),
}

COMPANION_PATTERNS: dict[str, tuple[str, ...]] = {
    "solo": ("một mình", "mot minh", "alone", "solo"),
    "couple": (
        "cặp đôi", "cap doi", "couple", "người yêu", "nguoi yeu",
        "lover", "hẹn hò", "hen ho", "dating", "2 người", "hai người",
    ),
    "family": (
        "gia đình", "gia dinh", "family", "trẻ em", "tre em",
        "kids", "cha mẹ", "cha me", "parents",
    ),
    "friends": (
        "bạn bè", "ban be", "friends", "nhóm", "nhom",
        "group", "team", "hội bạn", "hoi ban", "crew",
    ),
}

TIME_PATTERNS: dict[str, tuple[str, ...]] = {
    "morning": (
        "sáng", "morning", "buổi sáng", "buoi sang", "early",
        "sáng nay", "sang nay",
    ),
    "afternoon": ("trưa", "trua", "noon", "chiều", "chieu", "afternoon"),
    "evening": (
        "tối", "evening", "đêm", "dem", "night",
        "tối nay", "toi nay", "tonight", "overnight",
        "đêm nay", "dem nay",
    ),
    "weekend": ("cuoi tuan", "cuối tuần", "weekend"),
    "tomorrow": ("ngay mai", "ngày mai", "tomorrow"),
}

DISTANCE_KEYWORDS = {
    "near": ("gần", "gan", "near", "gần đây", "gan day", "nearby"),
    "far": ("xa", "far", "xa quá", "xa qua", "far away"),
}

STOP_WORDS = {
    "cho", "toi", "tôi", "minh", "mình", "o", "ở", "tai", "tại",
    "gan", "gần", "day", "quanh", "khu", "vuc", "vực", "di", "đi",
    "choi", "chơi", "tim", "tìm", "kiem", "kiếm", "noi", "nơi",
    "nao", "nào", "giup", "giúp", "voi", "với", "va", "và",
    "the", "thể", "co", "có", "theo", "near", "around", "place",
    "places", "trên", "tren", "sao", "nay", "là", "la", "buoi",
    "ban", "muon", "mot", "gi", "do", "đo", "vui", "tron", "ven",
    "ton", "tai", "on", "dinh", "me", "for", "friendly",
    "uh", "uhm", "um",
}

# ============================================================
# FUZZY MATCHING — anchor words per category
# ============================================================
# Short representative words whose edit distance is measured against each
# query token.  Kept deliberately small and high-signal.

_FUZZY_ANCHORS: dict[str, list[str]] = {
    "cafe": [
        "coffee", "cafe", "latte", "espresso", "cappuccino",
        "matcha", "caphe", "beverage",
    ],
    "restaurant": [
        "restaurant", "food", "dining", "meal", "eat",
        "noodle", "pizza", "burger", "sushi", "kitchen",
    ],
    "park": ["park", "garden", "outdoor", "picnic", "walk"],
    "mall": ["mall", "shopping", "shop", "market"],
    "hotel": ["hotel", "resort", "hostel", "lodging"],
    "museum": ["museum", "gallery", "exhibition"],
    "movie_theater": ["cinema", "movie", "film", "theater"],
    "bar": ["bar", "pub", "club", "nightlife"],
    "spa": ["spa", "massage", "wellness", "relaxation"],
}


def _levenshtein(s1: str, s2: str) -> int:
    """Standard Levenshtein edit distance."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for c1 in s1:
        curr = [prev[0] + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def _fuzzy_category_match(normalized_text: str) -> str | None:
    """Match query tokens against anchor words via edit distance.

    Input:
    - normalized_text: accent-stripped lowercase query string.

    Output:
    - Best-matching category key, or None if no token is close enough.

    Threshold: edit distance <= max(1, len(word) // 3).
    This allows:
      length 3-5 → 1 edit  (cofee → coffee)
      length 6-8 → 2 edits (resturant → restaurant)
    """
    tokens = [t for t in normalized_text.split() if len(t) >= 3]
    if not tokens:
        return None

    best_cat: str | None = None
    best_score: float = float("inf")  # lower is better

    for token in tokens:
        max_dist = max(1, len(token) // 3)
        for cat, anchors in _FUZZY_ANCHORS.items():
            for anchor in anchors:
                dist = _levenshtein(token, anchor)
                if dist <= max_dist:
                    # normalise by word length so short words aren't penalised
                    normalised = dist / max(len(token), len(anchor))
                    if normalised < best_score:
                        best_score = normalised
                        best_cat = cat

    return best_cat


# ============================================================
# TF-IDF FALLBACK (Layer 2)
# ============================================================

_TFIDF_CORPUS: dict[str, list[str]] = {}
_IDF: dict[str, float] = {}
_CORPUS_BUILT = False


def _build_tfidf_corpus() -> None:
    global _TFIDF_CORPUS, _IDF, _CORPUS_BUILT
    if _CORPUS_BUILT:
        return
    for category, patterns in ENTERTAINMENT_PATTERNS.items():
        tokens: list[str] = []
        for phrase in patterns:
            for token in _strip_accents(phrase.lower()).split():
                if len(token) >= 2:
                    tokens.append(token)
        _TFIDF_CORPUS[category] = tokens

    num_docs = len(_TFIDF_CORPUS)
    all_tokens: set[str] = set(t for toks in _TFIDF_CORPUS.values() for t in toks)
    for token in all_tokens:
        doc_freq = sum(1 for toks in _TFIDF_CORPUS.values() if token in toks)
        _IDF[token] = math.log((num_docs + 1) / (doc_freq + 1)) + 1.0
    _CORPUS_BUILT = True


def _tfidf_vector(tokens: list[str]) -> dict[str, float]:
    tf = Counter(tokens)
    total = sum(tf.values()) or 1
    return {t: (c / total) * _IDF.get(t, 1.0) for t, c in tf.items()}


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    dot = sum(a.get(t, 0.0) * b.get(t, 0.0) for t in b)
    na = math.sqrt(sum(v * v for v in a.values())) or 1e-9
    nb = math.sqrt(sum(v * v for v in b.values())) or 1e-9
    return dot / (na * nb)


def _tfidf_category_match(normalized_text: str, threshold: float = 0.12) -> str | None:
    _build_tfidf_corpus()
    query_tokens = [t for t in normalized_text.split() if len(t) >= 2]
    if not query_tokens:
        return None
    query_vec = _tfidf_vector(query_tokens)
    best_cat: str | None = None
    best_sim: float = threshold
    for category, corpus_tokens in _TFIDF_CORPUS.items():
        sim = _cosine_similarity(query_vec, _tfidf_vector(corpus_tokens))
        if sim > best_sim:
            best_sim = sim
            best_cat = category
    return best_cat


# ============================================================
# CORE HELPERS
# ============================================================

def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _normalize_text(text: str) -> str:
    lowered = _strip_accents(text.lower().strip())
    return re.sub(r"\s+", " ", lowered)


def _match_phrase(text: str, phrase: str) -> bool:
    words, p_words = text.split(), phrase.split()
    for i in range(len(words) - len(p_words) + 1):
        if words[i : i + len(p_words)] == p_words:
            return True
    return False


def _extract_first_match(
    text: str, pattern_map: dict[str, tuple[str, ...]]
) -> str | None:
    matches = []
    for label, patterns in pattern_map.items():
        for p in patterns:
            p_clean = p.lower().strip()
            if p_clean and _match_phrase(text, p_clean):
                matches.append((label, p_clean))
    if not matches:
        return None
    matches.sort(key=lambda x: len(x[1]), reverse=True)
    return matches[0][0]


def _collect_intent_tokens(*pattern_groups: tuple[str, ...]) -> set[str]:
    tokens: set[str] = set()
    for patterns in pattern_groups:
        for phrase in patterns:
            tokens.update(t for t in phrase.split() if t)
    return tokens


def _tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^\w]+", text, flags=re.UNICODE) if len(t) >= 2]


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ============================================================
# PUBLIC API
# ============================================================

def parse_search_text(query: str) -> dict:
    """Extract structured fields and normalized search text from free-text query.

    Owner: TV3.

    Input:
    - query: raw Vietnamese/English natural-language request.

    Output:
    - dict with keys: entertainment_type, budget_level, companion_type,
      time_slot, normalized_query, local_query, external_query,
      content_terms, match_method.

    match_method values:
    - "rule"  : exact keyword phrase matched
    - "tfidf" : TF-IDF cosine similarity matched (vocabulary overlap)
    - "fuzzy" : Levenshtein edit-distance matched (typo / loanword)
    - "none"  : no category found

    Change from original:
    - Added TF-IDF (Layer 2) and fuzzy edit-distance (Layer 3) fallbacks so
      queries like 'espresso beverage', 'resturant binh dan', or novel food
      keywords still map to a category instead of returning None.
    """
    normalized_text = _normalize_text(query)

    # Layer 1 — rule-based
    entertainment_type = _extract_first_match(normalized_text, ENTERTAINMENT_PATTERNS)
    budget_level = _extract_first_match(normalized_text, BUDGET_PATTERNS)
    companion_type = _extract_first_match(normalized_text, COMPANION_PATTERNS)
    time_slot = _extract_first_match(normalized_text, TIME_PATTERNS)
    match_method = "rule" if entertainment_type else "none"

    # Layer 2 — TF-IDF (only when rule failed)
    if entertainment_type is None and normalized_text:
        tfidf_cat = _tfidf_category_match(normalized_text)
        if tfidf_cat is not None:
            entertainment_type = tfidf_cat
            match_method = "tfidf"

    # Layer 3 — fuzzy edit-distance (only when both rule and TF-IDF failed)
    if entertainment_type is None and normalized_text:
        fuzzy_cat = _fuzzy_category_match(normalized_text)
        if fuzzy_cat is not None:
            entertainment_type = fuzzy_cat
            match_method = "fuzzy"

    intent_tokens = set(STOP_WORDS)
    if entertainment_type:
        intent_tokens.update(
            _collect_intent_tokens(ENTERTAINMENT_PATTERNS[entertainment_type])
        )
    if budget_level:
        intent_tokens.update(_collect_intent_tokens(BUDGET_PATTERNS[budget_level]))
    if companion_type:
        intent_tokens.update(_collect_intent_tokens(COMPANION_PATTERNS[companion_type]))
    if time_slot:
        intent_tokens.update(_collect_intent_tokens(TIME_PATTERNS[time_slot]))

    query_tokens = _tokenize(normalized_text)
    content_tokens = [t for t in query_tokens if t not in intent_tokens]
    category_label = ENTERTAINMENT_LABELS.get(entertainment_type) if entertainment_type else None
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
        "match_method": match_method,
    }


def parse_recommendation_language_contract(query: str) -> dict:
    """Parse the full NLP contract for natural-language recommendation input.

    Owner: TV3.

    Input / Output: unchanged from original.

    Change from original:
    - Uses Gemini API (via gemini_service) for primary smart parsing.
    - Falls back to improved parse_search_text (3-layer matching) if Gemini fails.
    """
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
            "match_method": "none",
        }

    from app.services.gemini_service import parse_search_query_with_gemini
    
    # Try Gemini first
    gemini_result = parse_search_query_with_gemini(query)
    if gemini_result is not None:
        return {
            "intent": gemini_result.get("intent", "unknown"),
            "entertainment_type": gemini_result.get("entertainment_type"),
            "budget_level": gemini_result.get("budget_level"),
            "companion_type": gemini_result.get("companion_type"),
            "time_slot": gemini_result.get("time_slot"),
            "location_hint": gemini_result.get("location_hint"),
            "distance_hint_km": gemini_result.get("distance_hint_km"),
            "require_open_now": bool(gemini_result.get("require_open_now")),
            "min_rating": gemini_result.get("min_rating"),
            "keywords": gemini_result.get("keywords", []),
            "confidence": 0.95,
            "missing_fields": [],
            "match_method": "gemini",
        }

    # Fallback to local NLP rule-based parser
    base = parse_search_text(query)
    text = base.get("normalized_query", "")
    match_method: str = base.get("match_method", "none")

    def contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
        return any(re.search(rf"\b{re.escape(p)}\b", text) for p in phrases)

    def is_negated(text: str, keyword: str) -> bool:
        return any(f"khong {k}" in text for k in [keyword, f"can {keyword}", f"muon {keyword}"])

    # --- DISTANCE ---
    distance_hint_km = None
    match_km = re.search(r"(\d+)\s*km", text)
    if match_km:
        value = int(match_km.group(1))
        before = text[: match_km.start()].strip().split()
        l1 = before[-1] if before else ""
        l2 = " ".join(before[-2:]) if len(before) >= 2 else ""

        def check_mod(mods: tuple[str, ...]) -> bool:
            return any(l1 == m or l2 == m or l2.endswith(" " + m) for m in mods)

        if check_mod(("tren", "hon")):
            distance_hint_km = value + 1
        elif check_mod(("duoi", "nho hon")):
            distance_hint_km = max(0, value - 1)
        else:
            distance_hint_km = value

    if distance_hint_km is None:
        if contains_phrase(text, DISTANCE_KEYWORDS["near"]) and not is_negated(text, "gan"):
            distance_hint_km = 1
        elif contains_phrase(text, DISTANCE_KEYWORDS["far"]) and not is_negated(text, "xa"):
            distance_hint_km = 10

    # --- RATING ---
    min_rating = None
    m = re.search(r"(\d(\.\d)?)\s*sao", text)
    if m:
        try:
            min_rating = float(m.group(1))
        except ValueError:
            pass

    # --- OPEN NOW ---
    require_open_now = contains_phrase(text, ("dang mo", "mo cua", "open now", "con mo", "available"))

    # --- LOCATION ---
    location_hint = None
    mq = re.search(r"quan\s*\d+", text)
    if mq:
        location_hint = mq.group(0)
    else:
        md = re.search(r"district\s*\d+", text)
        if md:
            location_hint = md.group(0)

    # --- BUDGET ---
    budget_level = base.get("budget_level")
    if is_negated(text, "re") or is_negated(text, "dat"):
        budget_level = None

    # --- KEYWORDS ---
    keywords = list({
        k for k in base.get("content_terms", [])
        if (k not in STOP_WORDS or k in {"choi"})
        and len(k) >= 2
        and k not in {"khong", "can", "gi", "do", "xa", "gan"}
    })

    # --- CONFIDENCE (match_method affects cat_score) ---
    cat_score = {"rule": 1.0, "tfidf": 0.7, "fuzzy": 0.5, "none": 0.0}.get(match_method, 0.0)
    score = cat_score
    if budget_level:
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
    if contains_phrase(text, ("muon",)):
        score += 1
    confidence = round(min(1.0, 0.3 + score * 0.12), 2)

    # --- MISSING FIELDS ---
    missing_fields: list[str] = []
    if not base.get("entertainment_type"):
        missing_fields.append("entertainment_type")
    if distance_hint_km is None and score >= 2:
        missing_fields.append("distance")
    if not base.get("time_slot") and score >= 2:
        missing_fields.append("time")

    # --- INTENT ---
    if base.get("entertainment_type") == "restaurant":
        intent = "find_food"
    elif base.get("entertainment_type"):
        intent = "find_activity"
    elif contains_phrase(text, ("di choi", "choi", "hang out", "relax")):
        intent = "find_activity"
    elif len(text.strip()) <= 2:
        intent = "unknown"
    elif keywords:
        intent = "recommend_place"
    elif contains_phrase(text, ("tim", "cho", "goi y", "suggest", "recommend")):
        intent = "recommend_place"
    else:
        intent = "unknown"

    return {
        "intent": intent,
        "entertainment_type": base.get("entertainment_type"),
        "budget_level": budget_level,
        "companion_type": base.get("companion_type"),
        "time_slot": base.get("time_slot"),
        "location_hint": location_hint,
        "distance_hint_km": distance_hint_km,
        "require_open_now": require_open_now,
        "min_rating": min_rating,
        "keywords": keywords,
        "confidence": confidence,
        "missing_fields": missing_fields,
        "match_method": match_method,
    }


def extract_filter_fields_from_text(query: str) -> dict:
    """Extract fields that should merge with explicit UI filters.

    Owner: TV3 / TV4.  Signature and merge semantics unchanged.
    """
    if not query or not query.strip():
        return {}

    parsed = parse_recommendation_language_contract(query)

    filters: dict[str, Any] = {
        "max_distance_km": parsed.get("distance_hint_km"),
        "min_rating": parsed.get("min_rating"),
        "budget_level": parsed.get("budget_level"),
        "preferred_types": None,
        "require_open_now": parsed.get("require_open_now"),
        "companion_type": parsed.get("companion_type"),
        "time_slot": parsed.get("time_slot"),
    }
    if parsed.get("entertainment_type"):
        filters["preferred_types"] = [parsed["entertainment_type"]]

    return {k: v for k, v in filters.items() if v is not None and v is not False and v != "" and v != []}
