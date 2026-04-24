"""Internal place model backed by the Supabase catalog database."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Place:
    id: int
    name: str
    address: str
    category: str | None = None
    external_place_id: str | None = None
    rating: float | None = None
    review_count: int = 0
    latitude: float | None = None
    longitude: float | None = None
    price_level: int | None = None
    price_range: str | None = None
    open_now: bool | None = None
    photo_url: str | None = None
    contact_phone: str | None = None
    primary_type: str | None = None
    website: str | None = None
    description: str | None = None
    opening_hours: dict[str, list[str]] = field(default_factory=dict)
    popular_times: dict[str, dict[str, int]] = field(default_factory=dict)
    images: list[str] = field(default_factory=list)
    about: list[dict] = field(default_factory=list)
    reviews_per_rating: dict[str, int] = field(default_factory=dict)
    status: str | None = None
    place_id: str | None = None
    cid: str | None = None
    borough: str | None = None
    street: str | None = None
    city: str | None = None
    postal_code: str | None = None
    state: str | None = None
    country: str | None = None
