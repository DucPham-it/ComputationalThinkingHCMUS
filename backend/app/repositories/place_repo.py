"""Place repository for the Supabase catalog database."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.place import Place
from app.utils.distance import haversine_km

PLACE_SELECT_COLUMNS = """
    p.id,
    p.title AS name,
    p.category,
    p.address_text AS address,
    p.place_id AS external_place_id,
    prs.average_rating AS rating,
    COALESCE(prs.review_count, 0) AS review_count,
    p.latitude,
    p.longitude,
    p.price_level,
    p.price_range,
    p.phone AS contact_phone,
    (
        SELECT pi.image_url
        FROM place_images AS pi
        WHERE pi.place_id = p.id
        ORDER BY pi.is_primary DESC, pi.sort_order ASC, pi.id ASC
        LIMIT 1
    ) AS photo_url,
    p.category AS primary_type,
    p.website,
    p.descriptions AS description,
    p.open_hours_json,
    p.popular_times_json,
    p.about_json,
    p.status,
    p.place_id,
    p.cid,
    p.borough,
    p.street,
    p.city,
    p.postal_code,
    p.state,
    p.country
"""

PLACE_FROM_JOIN = """
    places AS p
    LEFT JOIN place_review_stats AS prs ON prs.place_id = p.id
"""

SEARCH_STOP_WORDS = {
    "cho",
    "toi",
    "minh",
    "tim",
    "kiem",
    "gan",
    "day",
    "quanh",
    "khu",
    "vuc",
    "di",
    "choi",
    "noi",
    "nao",
    "voi",
    "trong",
    "duoi",
    "tren",
    "sao",
    "km",
    "near",
    "around",
    "place",
    "places",
}

SEARCH_CATEGORY_ALIASES = {
    "restaurant": (
        "restaurant",
        "food",
        "nha hang",
        "nhà hàng",
        "quan an",
        "quán ăn",
        "đồ ăn",
        "do an",
    ),
    "cafe": (
        "cafe",
        "coffee",
        "ca phe",
        "cà phê",
        "quán cà phê",
        "quan ca phe",
    ),
    "movie_theater": (
        "movie",
        "cinema",
        "rap",
        "rạp",
        "phim",
        "rạp chiếu phim",
        "rap chieu phim",
    ),
    "park": ("park", "cong vien", "công viên"),
    "mall": (
        "mall",
        "shopping",
        "shopping mall",
        "trung tam thuong mai",
        "trung tâm thương mại",
    ),
    "museum": ("museum", "bao tang", "bảo tàng"),
    "hotel": ("hotel", "khach san", "khách sạn"),
}


def _loads_json(raw_value, *, default):
    if not raw_value:
        return default
    if isinstance(raw_value, (dict, list)):
        return raw_value
    try:
        loaded_value = json.loads(raw_value)
    except (TypeError, ValueError):
        return default
    return loaded_value if loaded_value is not None else default


def _unique_texts(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if item is not None]


def _normalize_budget_level(value: Any) -> str | None:
    if not value:
        return None

    normalized = str(value).strip().lower()
    aliases = {
        "cheap": "low",
        "budget": "low",
        "binh dan": "low",
        "bình dân": "low",
        "re": "low",
        "rẻ": "low",
        "mid": "medium",
        "moderate": "medium",
        "average": "medium",
        "premium": "high",
        "expensive": "high",
        "luxury": "high",
        "cao cap": "high",
        "cao cấp": "high",
    }
    canonical = aliases.get(normalized, normalized)
    return canonical if canonical in {"low", "medium", "high"} else None


def _expand_search_patterns(keyword: str) -> list[str]:
    """Build database search patterns from free text and category aliases.

    Input:
    - keyword: raw or NLP-normalized search text, for example "nha hang re"
      or "cafe gan day".

    Output:
    - list of lowercase text patterns used with SQL LIKE.
    - includes category aliases so accentless NLP text can still match
      accented catalog values such as "Nhà hàng" or "Cà phê".
    """
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return []

    patterns = [normalized_keyword]
    tokens = [
        token
        for token in re.split(r"[^\w]+", normalized_keyword, flags=re.UNICODE)
        if len(token) >= 2 and token not in SEARCH_STOP_WORDS and not token.isdigit()
    ]
    patterns.extend(tokens)

    compact_keyword = f" {normalized_keyword} "
    for aliases in SEARCH_CATEGORY_ALIASES.values():
        if any(f" {alias} " in compact_keyword or alias in normalized_keyword for alias in aliases):
            patterns.extend(aliases)

    return _unique_texts(patterns)[:16]


def _build_database_filter_conditions(
    filters: dict[str, Any] | None,
    params: dict[str, object],
    *,
    latitude: float | None,
    longitude: float | None,
) -> list[str]:
    """Build SQL conditions for hard candidate filters.

    Input:
    - filters: filter_plan from recommender.py with allowed_types, min_rating,
      budget_level, max_distance_km.
    - params: mutable SQL parameter dict.
    - latitude/longitude: user location for a cheap bounding-box prefilter.

    Output:
    - SQL condition fragments. These narrow candidate fetching in the database;
      app/recommendation/filters.py still performs the final safety filter.
    """
    if not filters:
        return []

    conditions: list[str] = []

    allowed_types = _as_list(filters.get("allowed_types") or filters.get("preferred_types"))
    type_conditions: list[str] = []
    for type_index, place_type in enumerate(allowed_types):
        normalized_type = place_type.strip().lower()
        aliases = SEARCH_CATEGORY_ALIASES.get(normalized_type, (normalized_type,))
        for alias_index, alias in enumerate(aliases):
            param_name = f"filter_type_{type_index}_{alias_index}"
            params[param_name] = f"%{alias.lower()}%"
            type_conditions.append(f"LOWER(COALESCE(p.category, '')) LIKE :{param_name}")
    if type_conditions:
        conditions.append(f"({' OR '.join(type_conditions)})")

    min_rating = _as_float(filters.get("min_rating"))
    if min_rating is not None:
        params["filter_min_rating"] = min_rating
        conditions.append(
            "(prs.average_rating IS NULL OR prs.average_rating >= :filter_min_rating)"
        )

    budget_level = _normalize_budget_level(filters.get("budget_level"))
    if budget_level:
        params["filter_budget_level"] = budget_level
        if budget_level == "low":
            conditions.append(
                """
                (
                    p.price_level IS NULL
                    OR p.price_level < 2
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%rẻ%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%cheap%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%low%'
                )
                """
            )
        elif budget_level == "medium":
            conditions.append(
                """
                (
                    p.price_level IS NULL
                    OR p.price_level < 3
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%medium%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%moderate%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%tầm trung%'
                )
                """
            )
        elif budget_level == "high":
            conditions.append(
                """
                (
                    p.price_level IS NULL
                    OR p.price_level >= 2
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%premium%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%luxury%'
                    OR LOWER(COALESCE(p.price_range, '')) LIKE '%cao cấp%'
                )
                """
            )

    max_distance_km = _as_float(filters.get("max_distance_km"))
    if (
        max_distance_km is not None
        and max_distance_km > 0
        and latitude is not None
        and longitude is not None
    ):
        delta_latitude = max_distance_km / 111.0
        longitude_scale = max(0.01, abs(math.cos(math.radians(latitude))))
        delta_longitude = max_distance_km / (111.0 * longitude_scale)
        params.update(
            {
                "filter_min_latitude": latitude - delta_latitude,
                "filter_max_latitude": latitude + delta_latitude,
                "filter_min_longitude": longitude - delta_longitude,
                "filter_max_longitude": longitude + delta_longitude,
            }
        )
        conditions.append(
            """
            (
                p.latitude IS NULL
                OR p.longitude IS NULL
                OR (
                    p.latitude BETWEEN :filter_min_latitude AND :filter_max_latitude
                    AND p.longitude BETWEEN :filter_min_longitude AND :filter_max_longitude
                )
            )
            """
        )

    return conditions


def _normalize_primary_type(category: str | None) -> str | None:
    if not category:
        return None

    normalized = category.strip().lower()
    category_map = {
        "nhà hàng": "restaurant",
        "nhà hàng việt nam": "restaurant",
        "quán ăn": "restaurant",
        "cafe": "cafe",
        "quán cà phê": "cafe",
        "coffee": "cafe",
        "công viên": "park",
        "park": "park",
        "shopping mall": "mall",
        "trung tâm thương mại": "mall",
        "mall": "mall",
        "movie theater": "movie_theater",
        "rạp chiếu phim": "movie_theater",
        "museum": "museum",
        "bảo tàng": "museum",
        "hotel": "hotel",
        "khách sạn": "hotel",
    }
    for key, value in category_map.items():
        if key in normalized:
            return value
    return normalized.replace(" ", "_")


def _is_open_now(opening_hours: dict[str, list[str]]) -> bool | None:
    if not opening_hours:
        return None

    weekday_map = {
        0: "Thứ Hai",
        1: "Thứ Ba",
        2: "Thứ Tư",
        3: "Thứ Năm",
        4: "Thứ Sáu",
        5: "Thứ Bảy",
        6: "Chủ Nhật",
    }
    now = datetime.now()
    day_name = weekday_map.get(now.weekday())
    windows = opening_hours.get(day_name) or []
    if not windows:
        return None

    current_minutes = now.hour * 60 + now.minute
    for window in windows:
        try:
            start_text, end_text = window.split("–", 1)
            start_hour, start_minute = [int(item) for item in start_text.split(":", 1)]
            end_hour, end_minute = [int(item) for item in end_text.split(":", 1)]
        except (AttributeError, ValueError):
            continue

        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute
        if start_minutes <= current_minutes <= end_minutes:
            return True

    return False


class PlaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def _select_mappings(self, query: str, params: dict | None = None):
        return self.db.execute(text(query), params or {}).mappings()

    @staticmethod
    def _to_place(row) -> Place:
        opening_hours = _loads_json(row.get("open_hours_json"), default={})
        popular_times = _loads_json(row.get("popular_times_json"), default={})
        about_payload = _loads_json(row.get("about_json"), default=[])
        image_urls = [row["photo_url"]] if row.get("photo_url") else []

        return Place(
            id=int(row["id"]),
            name=row["name"],
            address=row["address"],
            category=row.get("category"),
            external_place_id=row.get("external_place_id"),
            rating=float(row["rating"]) if row.get("rating") is not None else None,
            review_count=int(row.get("review_count") or 0),
            latitude=float(row["latitude"]) if row.get("latitude") is not None else None,
            longitude=float(row["longitude"]) if row.get("longitude") is not None else None,
            price_level=int(row["price_level"]) if row.get("price_level") is not None else None,
            price_range=row.get("price_range"),
            open_now=_is_open_now(opening_hours),
            photo_url=row.get("photo_url"),
            contact_phone=row.get("contact_phone"),
            primary_type=_normalize_primary_type(row.get("primary_type")),
            website=row.get("website"),
            description=row.get("description"),
            opening_hours=opening_hours,
            popular_times=popular_times,
            images=image_urls,
            about=about_payload if isinstance(about_payload, list) else [],
            reviews_per_rating={},
            status=row.get("status"),
            place_id=row.get("place_id"),
            cid=row.get("cid"),
            borough=row.get("borough"),
            street=row.get("street"),
            city=row.get("city"),
            postal_code=row.get("postal_code"),
            state=row.get("state"),
            country=row.get("country"),
        )

    def get_by_id(self, place_id: int) -> Place | None:
        row = (
            self._select_mappings(
                f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM {PLACE_FROM_JOIN}
                    WHERE p.id = :place_id
                    """,
                {"place_id": place_id},
            )
            .first()
        )
        place = self._to_place(row) if row else None
        if place is not None:
            place.images = self.list_place_images(place.id, fallback_images=place.images)
            if place.images and not place.photo_url:
                place.photo_url = place.images[0]
        return place

    def get_by_name_or_address(self, raw_value: str) -> Place | None:
        normalized_value = raw_value.strip().lower()
        if not normalized_value:
            return None

        like_value = f"%{normalized_value}%"
        row = (
            self._select_mappings(
                f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM {PLACE_FROM_JOIN}
                    WHERE LOWER(p.title) = :value
                       OR LOWER(p.address_text) = :value
                       OR LOWER(p.title) LIKE :like_value
                       OR LOWER(p.address_text) LIKE :like_value
                       OR LOWER(COALESCE(p.descriptions, '')) LIKE :like_value
                    ORDER BY
                        CASE
                            WHEN LOWER(p.title) = :value OR LOWER(p.address_text) = :value THEN 0
                            ELSE 1
                        END,
                        COALESCE(prs.average_rating, 0) DESC,
                        COALESCE(prs.review_count, 0) DESC
                    LIMIT 1
                    """,
                {"value": normalized_value, "like_value": like_value},
            )
            .first()
        )
        return self._to_place(row) if row else None

    def search_local_places(
        self,
        keyword: str = "",
        limit: int = 50,
        *,
        filters: dict[str, Any] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[Place]:
        """Search local catalog candidates with optional database-side filters.

        Input:
        - keyword: free text or category seed query.
        - limit: maximum candidates to load before recommendation ranking.
        - filters: filter_plan from recommender.py. Supported hard filters:
          allowed_types, min_rating, budget_level, max_distance_km.
        - latitude/longitude: user location for distance bounding box.

        Output:
        - Place rows from the local database. This is a candidate fetch; final
          safety filtering still happens in app/recommendation/filters.py.
        """
        safe_limit = max(1, int(limit or 50))
        search_patterns = _expand_search_patterns(keyword)
        params: dict[str, object] = {"limit": safe_limit}
        conditions = ["COALESCE(p.status, 'active') <> 'deleted'"]
        score_parts: list[str] = []

        if search_patterns:
            match_conditions: list[str] = []
            for index, pattern in enumerate(search_patterns):
                param_name = f"pattern_{index}"
                params[param_name] = f"%{pattern}%"
                match_conditions.append(
                    f"""
                    LOWER(p.title) LIKE :{param_name}
                    OR LOWER(COALESCE(p.category, '')) LIKE :{param_name}
                    OR LOWER(p.address_text) LIKE :{param_name}
                    OR LOWER(COALESCE(p.descriptions, '')) LIKE :{param_name}
                    """
                )
                score_parts.extend(
                    [
                        f"CASE WHEN LOWER(p.title) LIKE :{param_name} THEN 4 ELSE 0 END",
                        f"CASE WHEN LOWER(COALESCE(p.category, '')) LIKE :{param_name} THEN 3 ELSE 0 END",
                        f"CASE WHEN LOWER(p.address_text) LIKE :{param_name} THEN 2 ELSE 0 END",
                        f"CASE WHEN LOWER(COALESCE(p.descriptions, '')) LIKE :{param_name} THEN 1 ELSE 0 END",
                    ]
                )
            conditions.append(" OR ".join(f"({condition})" for condition in match_conditions))

        conditions.extend(
            _build_database_filter_conditions(
                filters,
                params,
                latitude=latitude,
                longitude=longitude,
            )
        )
        select_score_sql = f", ({' + '.join(score_parts)}) AS search_score" if score_parts else ""
        order_score_sql = "search_score DESC," if score_parts else ""
        where_sql = " AND ".join(f"({condition})" for condition in conditions)
        rows = (
            self._select_mappings(
                f"""
                    SELECT {PLACE_SELECT_COLUMNS}{select_score_sql}
                    FROM {PLACE_FROM_JOIN}
                    WHERE {where_sql}
                    ORDER BY
                        {order_score_sql}
                        CASE WHEN prs.average_rating IS NULL THEN 1 ELSE 0 END,
                        COALESCE(prs.average_rating, 0) DESC,
                        COALESCE(prs.review_count, 0) DESC,
                        p.id ASC
                    LIMIT :limit
                    """,
                params,
            )
            .all()
        )
        return [self._to_place(row) for row in rows]

    def find_nearest_place(
        self,
        *,
        latitude: float,
        longitude: float,
        max_distance_km: float,
    ) -> Place | None:
        candidate_rows = (
            self._select_mappings(
                f"""
                    SELECT {PLACE_SELECT_COLUMNS}
                    FROM {PLACE_FROM_JOIN}
                    WHERE COALESCE(p.status, 'active') <> 'deleted'
                      AND p.latitude IS NOT NULL
                      AND p.longitude IS NOT NULL
                    """,
            )
            .all()
        )

        best_place: Place | None = None
        best_distance: float | None = None
        for row in candidate_rows:
            place = self._to_place(row)
            if place.latitude is None or place.longitude is None:
                continue

            distance_km = haversine_km(latitude, longitude, place.latitude, place.longitude)
            if distance_km > max_distance_km:
                continue
            if best_distance is None or distance_km < best_distance:
                best_distance = distance_km
                best_place = place

        return best_place

    def ensure_exists(
        self,
        place_id: int,
        name: str | None = None,
        address: str | None = None,
        rating: float | None = None,
    ) -> Place:
        existing_place = self.get_by_id(place_id)
        if existing_place is not None:
            return existing_place
        if not name or not address:
            raise ValueError(f"Place {place_id} does not exist in the local catalog.")
        return self.create_local_place(name=name, address=address, rating=rating)

    def list_place_images(self, place_id: int, fallback_images: list[str] | None = None) -> list[str]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT image_url
                    FROM place_images
                    WHERE place_id = :place_id
                    ORDER BY is_primary DESC, sort_order ASC, id ASC
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .all()
        )

        image_urls = [str(row["image_url"]) for row in rows if row.get("image_url")]
        return image_urls or (fallback_images or [])

    def replace_place_images(self, place_id: int, image_urls: list[str]) -> None:
        cleaned_urls = [url.strip() for url in image_urls if url and url.strip()]
        self.db.execute(text("DELETE FROM place_images WHERE place_id = :place_id"), {"place_id": place_id})
        for index, image_url in enumerate(cleaned_urls):
            self.db.execute(
                text(
                    """
                    INSERT INTO place_images (place_id, image_url, sort_order, is_primary)
                    VALUES (:place_id, :image_url, :sort_order, :is_primary)
                    """
                ),
                {
                    "place_id": place_id,
                    "image_url": image_url,
                    "sort_order": index,
                    "is_primary": index == 0,
                },
            )
        self.db.commit()

    def create_local_place(
        self,
        *,
        name: str,
        address: str,
        rating: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        price_level: int | None = None,
        open_now: bool | None = None,
        photo_url: str | None = None,
        contact_phone: str | None = None,
        primary_type: str | None = None,
    ) -> Place:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO places (
                        title,
                        category,
                        address_text,
                        latitude,
                        longitude,
                        price_range,
                        price_level,
                        website,
                        phone,
                        descriptions,
                        about_json,
                        status,
                        place_id,
                        cid,
                        borough,
                        street,
                        city,
                        postal_code,
                        state,
                        country,
                        open_hours_json,
                        popular_times_json
                    )
                    VALUES (
                        :title,
                        :category,
                        :address_text,
                        :latitude,
                        :longitude,
                        :price_range,
                        :price_level,
                        :website,
                        :phone,
                        :descriptions,
                        :about_json,
                        :status,
                        :place_id,
                        :cid,
                        :borough,
                        :street,
                        :city,
                        :postal_code,
                        :state,
                        :country,
                        :open_hours_json,
                        :popular_times_json
                    )
                    RETURNING id
                    """
                ),
                {
                    "title": name,
                    "category": primary_type,
                    "address_text": address,
                    "latitude": latitude,
                    "longitude": longitude,
                    "price_range": None,
                    "price_level": price_level,
                    "website": None,
                    "phone": contact_phone,
                    "descriptions": None,
                    "about_json": json.dumps([]),
                    "status": "active" if open_now is not False else "inactive",
                    "place_id": None,
                    "cid": None,
                    "borough": None,
                    "street": None,
                    "city": None,
                    "postal_code": None,
                    "state": None,
                    "country": None,
                    "open_hours_json": json.dumps({}),
                    "popular_times_json": json.dumps({}),
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        place_id = int(row["id"])
        if photo_url:
            self.replace_place_images(place_id, [photo_url])
        if rating is not None:
            self.upsert_review_summary(place_id, int(round(rating)), initial_average=rating, initial_count=0)
        place = self.get_by_id(place_id)
        if place is None:
            raise ValueError(f"Place {place_id} was created but could not be loaded.")
        return place

    def update_catalog_place(
        self,
        place_id: int,
        *,
        title: str | None = None,
        category: str | None = None,
        address_text: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        price_range: str | None = None,
        price_level: int | None = None,
        website: str | None = None,
        phone: str | None = None,
        descriptions: str | None = None,
        image_urls: list[str] | None = None,
    ) -> Place:
        existing_place = self.get_by_id(place_id)
        if existing_place is None:
            raise ValueError(f"Place {place_id} does not exist.")

        updates = {
            "title": title,
            "category": category,
            "address_text": address_text,
            "latitude": latitude,
            "longitude": longitude,
            "price_range": price_range,
            "price_level": price_level,
            "website": website,
            "phone": phone,
            "descriptions": descriptions,
        }
        set_clauses = [f"{column_name} = :{column_name}" for column_name, value in updates.items() if value is not None]
        if set_clauses:
            self.db.execute(
                text(
                    f"""
                    UPDATE places
                    SET {", ".join(set_clauses)}
                    WHERE id = :place_id
                    """
                ),
                {"place_id": place_id, **{key: value for key, value in updates.items() if value is not None}},
            )
            self.db.commit()

        if image_urls:
            self.replace_place_images(place_id, image_urls)

        refreshed_place = self.get_by_id(place_id)
        if refreshed_place is None:
            raise ValueError(f"Place {place_id} disappeared after update.")
        return refreshed_place

    def soft_delete_place(self, place_id: int) -> None:
        self.db.execute(
            text("UPDATE places SET status = 'deleted' WHERE id = :place_id"),
            {"place_id": place_id},
        )
        self.db.commit()

    def upsert_review_summary(
        self,
        place_id: int,
        rating: int,
        *,
        initial_average: float | None = None,
        initial_count: int | None = None,
    ) -> Place:
        place = self.get_by_id(place_id)
        if place is None:
            raise ValueError(f"Place {place_id} does not exist.")

        current_total = int(initial_count if initial_count is not None else place.review_count or 0)
        current_average = float(initial_average if initial_average is not None else place.rating or 0)
        new_total = current_total + 1
        new_average = round(((current_average * current_total) + int(rating)) / new_total, 2)
        rating_key = str(int(rating))

        existing_stats = (
            self.db.execute(
                text(
                    """
                    SELECT
                        rating_1_count,
                        rating_2_count,
                        rating_3_count,
                        rating_4_count,
                        rating_5_count
                    FROM place_review_stats
                    WHERE place_id = :place_id
                    """
                ),
                {"place_id": place_id},
            )
            .mappings()
            .first()
        )
        distribution = {
            "1": int(existing_stats["rating_1_count"] or 0) if existing_stats else 0,
            "2": int(existing_stats["rating_2_count"] or 0) if existing_stats else 0,
            "3": int(existing_stats["rating_3_count"] or 0) if existing_stats else 0,
            "4": int(existing_stats["rating_4_count"] or 0) if existing_stats else 0,
            "5": int(existing_stats["rating_5_count"] or 0) if existing_stats else 0,
        }
        distribution[rating_key] = int(distribution.get(rating_key, 0)) + 1

        if existing_stats:
            self.db.execute(
                text(
                    """
                    UPDATE place_review_stats
                    SET average_rating = :average_rating,
                        review_count = :review_count,
                        rating_1_count = :rating_1_count,
                        rating_2_count = :rating_2_count,
                        rating_3_count = :rating_3_count,
                        rating_4_count = :rating_4_count,
                        rating_5_count = :rating_5_count,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE place_id = :place_id
                    """
                ),
                {
                    "place_id": place_id,
                    "average_rating": new_average,
                    "review_count": new_total,
                    "rating_1_count": distribution["1"],
                    "rating_2_count": distribution["2"],
                    "rating_3_count": distribution["3"],
                    "rating_4_count": distribution["4"],
                    "rating_5_count": distribution["5"],
                },
            )
        else:
            self.db.execute(
                text(
                    """
                    INSERT INTO place_review_stats (
                        place_id,
                        average_rating,
                        review_count,
                        rating_1_count,
                        rating_2_count,
                        rating_3_count,
                        rating_4_count,
                        rating_5_count
                    )
                    VALUES (
                        :place_id,
                        :average_rating,
                        :review_count,
                        :rating_1_count,
                        :rating_2_count,
                        :rating_3_count,
                        :rating_4_count,
                        :rating_5_count
                    )
                    """
                ),
                {
                    "place_id": place_id,
                    "average_rating": new_average,
                    "review_count": new_total,
                    "rating_1_count": distribution["1"],
                    "rating_2_count": distribution["2"],
                    "rating_3_count": distribution["3"],
                    "rating_4_count": distribution["4"],
                    "rating_5_count": distribution["5"],
                },
            )
        self.db.commit()

        refreshed_place = self.get_by_id(place_id)
        if refreshed_place is None:
            raise ValueError(f"Place {place_id} disappeared after review update.")
        return refreshed_place

    def append_review_summary(self, place_id: int, rating: int) -> Place:
        return self.upsert_review_summary(place_id, rating)
