"""Image upload routes.

Owner:
- TV7: Media Upload + Review Avatar.

File input:
- Multipart image files from profile, review form, and place request form.
- Authenticated user/admin from dependencies.

File output:
- Public Supabase Storage URLs and metadata for uploaded images.
- Updated user avatar_url or place image URLs when endpoint performs a DB update.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.repositories.admin_repo import AdminRepository
from app.repositories.place_repo import PlaceRepository
from app.repositories.user_repo import UserRepository
from app.schemas.upload_schema import (
    AvatarUploadResponse,
    PlaceImagesUpdateResponse,
    UploadedImageResponse,
    UploadedImagesResponse,
)
from app.schemas.user_schema import UserResponse
from app.services.upload_storage import StoredUpload, store_image_upload

router = APIRouter()


def _to_uploaded_image_response(item: StoredUpload) -> UploadedImageResponse:
    """Convert storage service result into API schema.

    Owner:
    - TV7.

    Input:
    - item: StoredUpload from upload_storage.store_image_upload.

    Output:
    - UploadedImageResponse with url, filename, content_type, size_bytes.
    """
    return UploadedImageResponse(
        url=item.url,
        filename=item.filename,
        content_type=item.content_type,
        size_bytes=item.size_bytes,
    )


def _to_user_response(user, *, db: Session) -> UserResponse:
    """Build UserResponse after avatar update.

    Owner:
    - TV7.

    Input:
    - user: database user model after update_avatar.
    - db: SQLAlchemy session, used to compute is_admin.

    Output:
    - UserResponse consumed by frontend auth/profile state.
    """
    return UserResponse(
        id=user.id,
        user_name=user.user_name,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        avatar_url=user.avatar_url,
        is_admin=AdminRepository(db).is_approved_admin(user.id),
    )


async def _store_many(
    *,
    files: list[UploadFile],
    namespace: str,
    owner_id: int | str,
    request: Request,
) -> UploadedImagesResponse:
    """Store a batch of image files in one Supabase Storage namespace.

    Owner:
    - TV7.

    Input:
    - files: UploadFile list from multipart form field.
    - namespace: avatars, places, reviews, or another configured storage bucket.
    - owner_id: user id or place-specific folder key.
    - request: FastAPI request object kept for storage service compatibility.

    Output:
    - UploadedImagesResponse:
      - items: metadata for each uploaded image.
      - urls: public URLs in the same order.

    Validation:
    - raises 422 when no real file is provided.
    - raises 422 when more than 8 files are provided.
    """
    real_files = [file for file in files if file.filename]
    if not real_files:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one image file is required.",
        )
    if len(real_files) > 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upload up to 8 images at a time.",
        )

    stored_items = [
        await store_image_upload(
            file=file,
            namespace=namespace,
            owner_id=owner_id,
            request=request,
        )
        for file in real_files
    ]
    items = [_to_uploaded_image_response(item) for item in stored_items]
    return UploadedImagesResponse(items=items, urls=[item.url for item in items])


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvatarUploadResponse:
    """Upload and save the current user's avatar.

    Owner:
    - TV7.

    Input:
    - file: multipart field named "file"; accepted image MIME types are checked
      by upload_storage.
    - current_user: authenticated user from token.
    - db: SQLAlchemy session.

    Output:
    - AvatarUploadResponse with uploaded image metadata and updated user object.
    """
    stored = await store_image_upload(
        file=file,
        namespace="avatars",
        owner_id=current_user["id"],
        request=request,
    )
    user = UserRepository(db).update_avatar(user_id=current_user["id"], avatar_url=stored.url)
    return AvatarUploadResponse(
        **_to_uploaded_image_response(stored).model_dump(),
        user=_to_user_response(user, db=db),
    )


@router.post("/place-images", response_model=UploadedImagesResponse)
async def upload_place_images(
    request: Request,
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
) -> UploadedImagesResponse:
    """Upload place images for a user-created place request.

    Owner:
    - TV7.

    Input:
    - files: multipart field named "files", up to 8 image files.
    - current_user: authenticated user; id is used as storage folder owner.

    Output:
    - UploadedImagesResponse with public URLs to include in place_image_urls.
    """
    return await _store_many(
        files=files,
        namespace="places",
        owner_id=current_user["id"],
        request=request,
    )


@router.post("/review-images", response_model=UploadedImagesResponse)
async def upload_review_images(
    request: Request,
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
) -> UploadedImagesResponse:
    """Upload review images before creating a review.

    Owner:
    - TV7.

    Input:
    - files: multipart field named "files", up to 8 image files.
    - current_user: authenticated user; id is used as storage folder owner.

    Output:
    - UploadedImagesResponse with public URLs to send in review image_urls.
    """
    return await _store_many(
        files=files,
        namespace="reviews",
        owner_id=current_user["id"],
        request=request,
    )


@router.put("/places/{place_id}/images", response_model=PlaceImagesUpdateResponse)
async def replace_place_images(
    place_id: int,
    request: Request,
    files: list[UploadFile] = File(...),
    current_admin: dict = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PlaceImagesUpdateResponse:
    """Replace the image set for an existing place.

    Owner:
    - TV7.

    Input:
    - place_id: database place id.
    - files: multipart field named "files", up to 8 image files.
    - current_admin: approved admin from dependency.
    - db: SQLAlchemy session.

    Output:
    - PlaceImagesUpdateResponse containing place_id and new public image_urls.
    - HTTP 404 when place does not exist.
    """
    del current_admin
    place_repo = PlaceRepository(db)
    if place_repo.get_by_id(place_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found.")

    uploaded = await _store_many(
        files=files,
        namespace="places",
        owner_id=f"place-{place_id}",
        request=request,
    )
    place_repo.replace_place_images(place_id, uploaded.urls)
    return PlaceImagesUpdateResponse(place_id=place_id, image_urls=uploaded.urls)
