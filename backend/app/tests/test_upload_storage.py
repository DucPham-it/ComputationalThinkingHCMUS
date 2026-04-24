import asyncio
from types import SimpleNamespace

from app.core.config import settings
from app.services import upload_storage
from app.services.upload_storage import store_image_upload


class DummyUploadFile:
    def __init__(self, *, contents: bytes, content_type: str = "image/png", filename: str = "photo.png"):
        self._contents = contents
        self.content_type = content_type
        self.filename = filename

    async def read(self, size: int = -1) -> bytes:
        del size
        return self._contents


class FakeResponse:
    status_code = 200
    text = ""


class FakeAsyncClient:
    calls = []

    def __init__(self, *args, **kwargs):
        del args, kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        del exc_type, exc, traceback

    async def post(self, url, *, content, headers):
        self.__class__.calls.append(
            {
                "url": url,
                "content": content,
                "headers": headers,
            }
        )
        return FakeResponse()


def test_store_image_upload_uploads_to_supabase_storage(monkeypatch):
    FakeAsyncClient.calls = []
    monkeypatch.setattr(settings, "supabase_url", "https://project-ref.supabase.co")
    monkeypatch.setattr(settings, "supabase_service_role_key", "service-role-key")
    monkeypatch.setattr(settings, "supabase_storage_review_bucket", "review-images")
    monkeypatch.setattr(settings, "upload_max_bytes", 1024)
    monkeypatch.setattr(upload_storage.httpx, "AsyncClient", FakeAsyncClient)

    stored = asyncio.run(
        store_image_upload(
            file=DummyUploadFile(contents=b"fake-image"),
            namespace="reviews",
            owner_id=42,
            request=SimpleNamespace(base_url="http://testserver/"),
        )
    )

    assert stored.url.startswith("https://project-ref.supabase.co/storage/v1/object/public/review-images/42/")
    assert stored.filename.endswith(".png")
    assert FakeAsyncClient.calls == [
        {
            "url": f"https://project-ref.supabase.co/storage/v1/object/review-images/42/{stored.filename}",
            "content": b"fake-image",
            "headers": {
                "apikey": "service-role-key",
                "Authorization": "Bearer service-role-key",
                "Content-Type": "image/png",
                "Cache-Control": "3600",
                "x-upsert": "false",
            },
        }
    ]
