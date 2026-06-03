"""Service for integrating Gemini AI to parse natural language queries."""

import json
import logging
from typing import Any

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

def parse_search_query_with_gemini(query: str) -> dict[str, Any] | None:
    """Parses a natural language query into structured fields using Gemini API."""
    if not settings.gemini_api_key:
        logger.warning("Gemini API key is not configured. Falling back to rule-based NLP.")
        return None

    try:
        genai.configure(api_key=settings.gemini_api_key)
        # Use gemini-1.5-flash for fast and cheap parsing
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Phân tích câu truy vấn tìm kiếm du lịch, giải trí sau đây: "{query}"
        
        Nhiệm vụ của bạn là bóc tách các thông tin và trả về DUY NHẤT một chuỗi JSON hợp lệ, không giải thích gì thêm.
        
        Cấu trúc JSON yêu cầu:
        {{
            "intent": "find_food" hoặc "find_activity" hoặc "recommend_place" hoặc "unknown",
            "entertainment_type": "restaurant", "cafe", "movie_theater", "park", "mall", "hotel", "museum", "bar", "spa" (chọn 1 loại phù hợp nhất, hoặc null),
            "budget_level": "low", "medium", "high" (hoặc null),
            "companion_type": "solo", "couple", "family", "friends" (hoặc null),
            "time_slot": "morning", "afternoon", "evening", "weekend", "tomorrow" (hoặc null),
            "location_hint": "Tên khu vực, quận huyện (VD: quan 1, district 1) hoặc null",
            "distance_hint_km": Số nguyên thể hiện bán kính tìm kiếm (VD: 1, 5, 10, nếu nhắc đến "gần đây" thì mặc định 1) hoặc null,
            "require_open_now": true hoặc false (nếu có nhắc đến "đang mở cửa", "bây giờ", "open now"),
            "min_rating": Số thực thể hiện số sao tối thiểu (VD: 4.0) hoặc null,
            "keywords": [Mảng các từ khóa quan trọng còn lại như tên món ăn, tên địa danh cụ thể (VD: Núi Bà Rá), phong cách (VD: "yên tĩnh", "bún chả", "view đẹp")]
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return result
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None
