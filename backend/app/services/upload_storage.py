"""Supabase Storage image upload helpers.

Owner:
- Legacy/completed media upload flow.
- Not part of TV7's current Review Rating Filter assignment.

File input:
- FastAPI UploadFile objects from upload routes.
- Storage namespace: avatars, places, reviews.
- Owner id used to build a safe storage folder.
- Supabase URL/service role key from settings.

File output:
- Uploaded file in Supabase Storage.
- Public URL for frontend rendering.
- Default avatar public URL for review/comment fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit
from uuid import uuid4

import httpx
from fastapi import HTTPException, Request, UploadFile, status

from app.core.config import settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


@dataclass(frozen=True)
class StoredUpload:
    """Result returned after one successful storage upload.

    Owner:
    - TV7.

    Output fields:
    - url: public Supabase Storage URL.
    - filename: generated unique filename.
    - content_type: uploaded MIME type.
    - size_bytes: uploaded byte size.
    """

    url: str
    filename: str
    content_type: str
    size_bytes: int


def _extension_for(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WEBP, and GIF images are supported.",
        )
    return ALLOWED_IMAGE_TYPES[content_type]


def _safe_path_part(raw_value: int | str) -> str:
    safe_value = "".join(char for char in str(raw_value) if char.isalnum() or char in {"-", "_"})
    if not safe_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid upload target.",
        )
    return safe_value


def _infer_supabase_url_from_database_url() -> str:
    parsed_url = urlsplit(settings.database_url)
    username = parsed_url.username or ""
    if username.startswith("postgres."):
        project_ref = username.split(".", 1)[1]
        if project_ref:
            return f"https://{project_ref}.supabase.co"

    hostname = parsed_url.hostname or ""
    hostname_parts = hostname.split(".")
    if len(hostname_parts) >= 3 and hostname_parts[-2:] == ["supabase", "co"]:
        project_ref = hostname_parts[1] if hostname_parts[0] == "db" else hostname_parts[0]
        if project_ref:
            return f"https://{project_ref}.supabase.co"

    return ""


def _supabase_url() -> str:
    configured_url = settings.supabase_url.strip().rstrip("/")
    inferred_url = _infer_supabase_url_from_database_url().rstrip("/")
    supabase_url = configured_url or inferred_url
    if not supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is required for image uploads.",
        )
    return supabase_url


def _supabase_storage_key() -> str:
    storage_key = settings.supabase_service_role_key.strip()
    if not storage_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_SERVICE_ROLE_KEY is required for image uploads.",
        )
    return storage_key


def _bucket_for(namespace: str) -> str:
    buckets = {
        "avatars": settings.supabase_storage_avatar_bucket,
        "places": settings.supabase_storage_place_bucket,
        "reviews": settings.supabase_storage_review_bucket,
    }
    bucket = buckets.get(namespace, namespace).strip()
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid upload bucket.",
        )
    return bucket


def _storage_path(*parts: str) -> str:
    return str(PurePosixPath(*parts))


def _quote_storage_path(path: str) -> str:
    return "/".join(quote(part, safe="") for part in path.split("/"))


def _public_url(*, supabase_url: str, bucket: str, path: str) -> str:
    return (
        f"{supabase_url}/storage/v1/object/public/"
        f"{quote(bucket, safe='')}/{_quote_storage_path(path)}"
    )


def public_storage_url(*, namespace: str, path: str) -> str:
    """Build a public URL for a known storage object.

    Owner:
    - TV7.

    Input:
    - namespace: logical bucket namespace, for example avatars/places/reviews.
    - path: storage object path inside the bucket.

    Output:
    - public Supabase Storage URL.
    """
    return _public_url(supabase_url=_supabase_url(), bucket=_bucket_for(namespace), path=path)


def default_avatar_url() -> str:
    """Return the default avatar URL used by review/comment fallbacks.

    Owner:
    - TV7.

    Input:
    - no function arguments. Uses Supabase Storage settings.

    Output:
    - public URL for avatars/default/default-avatar.jpg.
    - relative fallback path when Supabase URL cannot be resolved.
    """
    try:
        return public_storage_url(namespace="avatars", path="default/default-avatar.jpg")
    except HTTPException:
        return "avatars/default/default-avatar.jpg"


async def _upload_to_supabase_storage(
    *,
    bucket: str,
    path: str,
    content_type: str,
    contents: bytes,
) -> None:
    """Upload raw bytes directly to Supabase Storage.

    Owner:
    - TV7.

    Input:
    - bucket: physical Supabase bucket name.
    - path: object path inside bucket.
    - content_type: image MIME type.
    - contents: raw file bytes.

    Output:
    - no return value.
    - raises HTTP 502 when Supabase Storage rejects the upload.
    """
    supabase_url = _supabase_url()
    storage_key = _supabase_storage_key()
    upload_url = (
        f"{supabase_url}/storage/v1/object/"
        f"{quote(bucket, safe='')}/{_quote_storage_path(path)}"
    )
    headers = {
        "apikey": storage_key,
        "Authorization": f"Bearer {storage_key}",
        "Content-Type": content_type,
        "Cache-Control": settings.supabase_storage_cache_control,
        "x-upsert": "false",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(upload_url, content=contents, headers=headers)

    if response.status_code >= 400:
        detail = response.text or "Supabase Storage upload failed."
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase Storage upload failed: {detail}",
        )


async def store_image_upload(
    *,
    file: UploadFile,
    namespace: str,
    owner_id: int | str,
    request: Request,
) -> StoredUpload:
    """Validate and upload one image file to Supabase Storage.

    Owner:
    - TV7.

    Input:
    - file: FastAPI UploadFile from multipart request.
    - namespace: avatars, places, or reviews.
    - owner_id: user id or place folder key used in storage path.
    - request: kept for route/service compatibility.

    Output:
    - StoredUpload with public URL, generated filename, content type, and size.

    Validation:
    - rejects unsupported MIME types.
    - rejects empty uploads.
    - rejects files larger than settings.upload_max_bytes.
    """
    extension = _extension_for(file)
    contents = await file.read(settings.upload_max_bytes + 1)
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded image is empty.",
        )
    if len(contents) > settings.upload_max_bytes:
        max_megabytes = max(1, settings.upload_max_bytes // (1024 * 1024))
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded image must be {max_megabytes}MB or smaller.",
        )

    bucket = _bucket_for(namespace)
    owner_path = _safe_path_part(owner_id)
    filename = f"{uuid4().hex}{extension}"
    storage_path = _storage_path(owner_path, filename)
    content_type = file.content_type or "application/octet-stream"

    # Check if Supabase is configured
    configured_url = settings.supabase_url.strip().rstrip("/")
    inferred_url = _infer_supabase_url_from_database_url().rstrip("/")
    supabase_url = configured_url or inferred_url
    storage_key = settings.supabase_service_role_key.strip()

    if not supabase_url or not storage_key:
        # Local storage fallback
        storage_dir = Path(__file__).resolve().parents[2] / "storage" / namespace / owner_path
        storage_dir.mkdir(parents=True, exist_ok=True)
        local_file_path = storage_dir / filename
        with open(local_file_path, "wb") as f:
            f.write(contents)
        
        base_url = str(request.base_url).rstrip("/")
        url = f"{base_url}/storage/{namespace}/{owner_path}/{filename}"
    else:
        # Upload to Supabase
        await _upload_to_supabase_storage(
            bucket=bucket,
            path=storage_path,
            content_type=content_type,
            contents=contents,
        )
        url = _public_url(supabase_url=supabase_url, bucket=bucket, path=storage_path)

    return StoredUpload(
        url=url,
        filename=filename,
        content_type=content_type,
        size_bytes=len(contents),
    )
