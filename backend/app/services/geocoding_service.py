"""Geocoding helpers backed by database first, then OSM/Nominatim."""

from __future__ import annotations

import re
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.place_repo import PlaceRepository

import time

GEOCODING_ENDPOINT = "/search"
REVERSE_GEOCODING_ENDPOINT = "/reverse"
REQUEST_TIMEOUT_SECONDS = 10

COORDINATE_PATTERN = re.compile(
    r"^\s*(?P<lat>-?\d+(?:\.\d+)?)\s*,\s*(?P<lng>-?\d+(?:\.\d+)?)\s*$"
)

_NOMINATIM_CACHE: dict[str, dict[str, Any]] = {}
_LAST_REQUEST_TIME = 0.0

def _coerce_coordinate(value: str) -> tuple[float, float] | None:
    match = COORDINATE_PATTERN.match(value)
    if not match:
        return None

    latitude = float(match.group("lat"))
    longitude = float(match.group("lng"))
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return latitude, longitude


def _request_nominatim(path: str, *, params: dict[str, Any]) -> Any:
    global _LAST_REQUEST_TIME
    
    # 1. Caching để tránh gọi API trùng lặp
    cache_key = f"{path}?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    if cache_key in _NOMINATIM_CACHE:
        entry = _NOMINATIM_CACHE[cache_key]
        if time.time() - entry["timestamp"] < 86400:  # Cache 1 ngày
            return entry["data"]

    # 1.1 Chống tràn RAM: Xóa cache nếu quá 500 phần tử
    if len(_NOMINATIM_CACHE) > 500:
        _NOMINATIM_CACHE.clear()

    # 2. Rate Limiting: Ép hệ thống ngủ để đảm bảo tối đa 1 request / giây (Luật của OSM)
    now = time.time()
    time_since_last = now - _LAST_REQUEST_TIME
    if time_since_last < 1.1:
        time.sleep(1.1 - time_since_last)
    
    response = httpx.get(
        f"{settings.nominatim_base_url.rstrip('/')}{path}",
        params={
            **params,
            "format": "jsonv2",
            "accept-language": "vi",
        },
        headers={"User-Agent": settings.external_maps_user_agent},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    _LAST_REQUEST_TIME = time.time()
    
    response.raise_for_status()
    data = response.json()
    _NOMINATIM_CACHE[cache_key] = {"timestamp": _LAST_REQUEST_TIME, "data": data}
    return data


def _lookup_local_place(normalized_address: str, db: Session | None) -> dict | None:
    owns_session = db is None
    active_db = db or SessionLocal()
    try:
        place = PlaceRepository(active_db).get_by_name_or_address(normalized_address)
    finally:
        if owns_session:
            active_db.close()

    if place is None or place.latitude is None or place.longitude is None:
        return None

    return {
        "formatted_address": place.address,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "country_code": "vn",
    }


def is_in_vietnam(lat: float, lon: float) -> bool:
    # Cải tiến: Dùng 3 khung chữ nhật nhỏ bám sát hình chữ S để loại bỏ tối đa Lào/Campuchia
    # Miền Bắc
    if 19.0 <= lat <= 23.5 and 102.0 <= lon <= 108.0: return True
    # Miền Trung
    if 11.5 <= lat <= 19.0 and 105.0 <= lon <= 110.0: return True
    # Miền Nam
    if 8.0 <= lat <= 11.5 and 104.0 <= lon <= 108.0: return True
    return False


def geocode_address(address: str, *, db: Session | None = None) -> dict:
    normalized_address = address.strip()
    if not normalized_address:
        return {
            "formatted_address": "",
            "latitude": None,
            "longitude": None,
            "country_code": "",
        }

    coordinates = _coerce_coordinate(normalized_address)
    if coordinates is not None:
        latitude, longitude = coordinates
        
        # Bounding Box Heuristic: Nếu điểm nằm trong Việt Nam, không cần gọi OSM
        if is_in_vietnam(latitude, longitude):
            return {
                "formatted_address": normalized_address,
                "latitude": latitude,
                "longitude": longitude,
                "country_code": "vn",
            }
            
        rev = reverse_geocode_coordinates(latitude, longitude)
        country_code = rev.get("country_code", "") if rev else ""
        return {
            "formatted_address": normalized_address,
            "latitude": latitude,
            "longitude": longitude,
            "country_code": country_code,
        }

    local_match = _lookup_local_place(normalized_address, db)
    if local_match is not None:
        return local_match

    try:
        results = _request_nominatim(
            GEOCODING_ENDPOINT,
            params={
                "q": normalized_address,
                "limit": 1,
                "addressdetails": 1,
            },
        )
    except Exception:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
            "country_code": "",
        }

    if not results:
        return {
            "formatted_address": normalized_address,
            "latitude": None,
            "longitude": None,
            "country_code": "",
        }

    best_match = results[0]
    return {
        "formatted_address": best_match.get("display_name", normalized_address),
        "latitude": float(best_match["lat"]) if best_match.get("lat") is not None else None,
        "longitude": float(best_match["lon"]) if best_match.get("lon") is not None else None,
        "country_code": best_match.get("address", {}).get("country_code", ""),
    }


def reverse_geocode_coordinates(latitude: float, longitude: float) -> dict | None:
    try:
        payload = _request_nominatim(
            REVERSE_GEOCODING_ENDPOINT,
            params={
                "lat": latitude,
                "lon": longitude,
                "zoom": 18,
                "addressdetails": 1,
            },
        )
    except Exception:
        return None

    if not payload:
        return None

    display_name = payload.get("display_name") or f"{latitude},{longitude}"
    return {
        "name": payload.get("name") or display_name.split(",")[0].strip() or "Selected map point",
        "address": display_name,
        "latitude": float(payload.get("lat", latitude)),
        "longitude": float(payload.get("lon", longitude)),
        "source": "osm",
        "country_code": payload.get("address", {}).get("country_code", ""),
    }


def search_external_place(query: str, limit: int = 3) -> list[dict]:
    normalized = query.strip()
    if not normalized:
        return []
    try:
        results = _request_nominatim(
            GEOCODING_ENDPOINT,
            params={
                "q": normalized,
                "limit": limit,
                "addressdetails": 1,
            },
        )
    except Exception:
        return []
        
    places = []
    for item in results:
        display_name = item.get("display_name", "")
        name = item.get("name") or display_name.split(",")[0].strip()
        places.append({
            "id": None,
            "external_place_id": f"osm:{item.get('osm_type', 'node')}:{item.get('osm_id', '0')}",
            "name": name,
            "address": display_name,
            "latitude": float(item.get("lat", 0)),
            "longitude": float(item.get("lon", 0)),
            "rating": None,
            "review_count": 0,
            "distance_km": None,
            "price_level": None,
            "price_range": None,
            "open_now": None,
            "photo_url": None,
            "contact_phone": None,
            "primary_type": item.get("type", "point"),
            "score": 0.0,
            "can_view": False,
            "can_save": False,
            "is_local_only": True,
        })
    return places

