from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Review:
    id: int
    user_id: int
    place_id: int
    content: str
    rating: int
    user_name: str | None = None
    user_avatar_url: str | None = None
    reviewed_at: str | None = None
    image_urls: list[str] = field(default_factory=list)
    is_virtual_user: bool = False
