"""Admin and place change request API schemas."""

from typing import Literal

from pydantic import BaseModel, Field


PlaceRequestType = Literal["create", "update", "delete"]
PlaceRequestStatus = Literal["pending", "approved", "rejected"]
AdminStatus = Literal["pending", "approved", "rejected"]


class AdminProfileResponse(BaseModel):
    user_id: int
    status: AdminStatus | None = None
    role: str | None = None
    approved_by: int | None = None
    approved_at: str | None = None


class AdminMemberResponse(AdminProfileResponse):
    user_name: str | None = None
    email: str | None = None


class AdminDecisionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


class PlaceChangeRequestCreate(BaseModel):
    request_type: PlaceRequestType
    place_id: int | None = None
    title: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=255)
    address_text: str | None = Field(default=None, max_length=1000)
    latitude: float | None = None
    longitude: float | None = None
    price_range: str | None = Field(default=None, max_length=50)
    price_level: int | None = Field(default=None, ge=0, le=4)
    website: str | None = Field(default=None, max_length=1000)
    phone: str | None = Field(default=None, max_length=100)
    descriptions: str | None = Field(default=None, max_length=3000)
    request_note: str | None = Field(default=None, max_length=3000)
    review_content: str | None = Field(default=None, max_length=3000)
    review_rating: int | None = Field(default=None, ge=1, le=5)
    place_image_urls: list[str] = Field(default_factory=list)
    review_image_urls: list[str] = Field(default_factory=list)


class PlaceChangeRequestResponse(BaseModel):
    id: int
    requester_user_id: int
    requester_name: str | None = None
    request_type: PlaceRequestType
    status: PlaceRequestStatus
    place_id: int | None = None
    target_place_id: int | None = None
    title: str | None = None
    category: str | None = None
    address_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    price_range: str | None = None
    price_level: int | None = None
    website: str | None = None
    phone: str | None = None
    descriptions: str | None = None
    request_note: str | None = None
    review_content: str | None = None
    review_rating: int | None = None
    place_image_urls: list[str] = Field(default_factory=list)
    review_image_urls: list[str] = Field(default_factory=list)
    admin_user_id: int | None = None
    admin_note: str | None = None
    created_at: str | None = None
    reviewed_at: str | None = None

