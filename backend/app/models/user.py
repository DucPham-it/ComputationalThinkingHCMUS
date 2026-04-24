"""Internal user model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    id: int
    user_name: str
    email: str
    password_hash: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    address: str | None = None
    avatar_url: str | None = None
    is_virtual: bool = False
