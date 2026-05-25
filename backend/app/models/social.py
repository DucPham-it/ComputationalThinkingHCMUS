"""Internal social feed models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VisitedPlace:
    id: int
    user_id: int
    place_id: int
    place_name: str
    place_address: str
    place_photo_url: str | None = None
    place_rating: float | None = None
    route_origin: str | None = None
    route_destination: str | None = None
    distance_text: str | None = None
    duration_text: str | None = None
    distance_km: float | None = None
    duration_seconds: int | None = None
    travel_mode: str | None = None
    visited_at: str | None = None


@dataclass
class SocialComment:
    id: int
    post_id: int
    user_id: int
    content: str
    user_name: str | None = None
    user_avatar_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    is_owner: bool = False


@dataclass
class SocialPost:
    id: int
    user_id: int
    place_id: int
    content: str
    rating: int
    user_name: str | None = None
    user_avatar_url: str | None = None
    place_name: str | None = None
    place_address: str | None = None
    place_photo_url: str | None = None
    visited_place_id: int | None = None
    visited_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    viewer_has_liked: bool = False
    viewer_has_shared: bool = False
    is_owner: bool = False
    timeline_type: str = "post"
    shared_at: str | None = None
    comments: list[SocialComment] = field(default_factory=list)
