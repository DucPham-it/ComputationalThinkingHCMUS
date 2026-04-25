"""Upload API schemas.

Owner:
- Legacy/completed media upload flow.
- Not part of TV7's current Review Rating Filter assignment.

File input:
- Supabase Storage upload results from upload routes/services.

File output:
- JSON response schemas consumed by frontend uploadService, Profile,
  ReviewForm, and PlaceRequestForm.
"""

from pydantic import BaseModel, Field

from app.schemas.user_schema import UserResponse


class UploadedImageResponse(BaseModel):
    """Metadata for one uploaded image.

    Owner:
    - TV7.

    Output:
    - url: public Supabase Storage URL.
    - filename: generated storage filename.
    - content_type: uploaded MIME type.
    - size_bytes: uploaded byte size.
    """

    url: str
    filename: str
    content_type: str
    size_bytes: int


class UploadedImagesResponse(BaseModel):
    """Response for batch image upload endpoints.

    Owner:
    - TV7.

    Output:
    - items: metadata for every uploaded image.
    - urls: public URLs extracted for easy frontend payload building.
    """

    items: list[UploadedImageResponse] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)


class AvatarUploadResponse(UploadedImageResponse):
    """Response for avatar upload.

    Owner:
    - TV7.

    Output:
    - uploaded image metadata.
    - user: updated user payload with avatar_url.
    """

    user: UserResponse


class PlaceImagesUpdateResponse(BaseModel):
    """Response after replacing images for an existing place.

    Owner:
    - TV7.

    Output:
    - place_id: database place id.
    - image_urls: complete replacement URL list.
    """

    place_id: int
    image_urls: list[str] = Field(default_factory=list)
