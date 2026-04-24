import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from fastapi import HTTPException

from app.api.deps import require_completed_profile
from app.api.routes.auth import login, register, update_profile
from app.api.routes.favorites import list_favorites
from app.api.routes.reviews import create_review, list_reviews
from app.schemas.review_schema import ReviewCreateRequest
from app.schemas.user_schema import LoginRequest, RegisterRequest, UpdateProfileRequest


def build_test_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                birth_date TEXT,
                gender TEXT,
                address TEXT,
                avatar_url TEXT,
                is_virtual INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT,
                complete_address_json TEXT,
                address_text TEXT NOT NULL,
                borough TEXT,
                street TEXT,
                city TEXT,
                postal_code TEXT,
                state TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                open_hours_json TEXT NOT NULL DEFAULT '{}',
                popular_times_json TEXT NOT NULL DEFAULT '{}',
                price_range TEXT,
                price_level INTEGER,
                website TEXT,
                phone TEXT,
                descriptions TEXT,
                about_json TEXT NOT NULL DEFAULT '[]',
                status TEXT,
                place_id TEXT UNIQUE,
                cid TEXT UNIQUE
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                place_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                rating INTEGER NOT NULL,
                reviewed_at TEXT,
                is_imported INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE place_review_stats (
                place_id INTEGER PRIMARY KEY,
                average_rating REAL,
                review_count INTEGER NOT NULL DEFAULT 0,
                rating_1_count INTEGER NOT NULL DEFAULT 0,
                rating_2_count INTEGER NOT NULL DEFAULT 0,
                rating_3_count INTEGER NOT NULL DEFAULT 0,
                rating_4_count INTEGER NOT NULL DEFAULT 0,
                rating_5_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE place_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                place_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                title TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                is_primary INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE review_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                place_id INTEGER NOT NULL,
                UNIQUE (user_id, place_id)
            )
            """
        )
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()


def seed_place(db):
    db.execute(
        text(
            """
            INSERT INTO places (
                id,
                title,
                category,
                complete_address_json,
                address_text,
                open_hours_json,
                popular_times_json,
                price_range,
                price_level,
                about_json,
                status,
                place_id,
                cid
            )
            VALUES (
                1,
                'Nhà hàng thử nghiệm',
                'Nhà hàng Việt Nam',
                :complete_address_json,
                '123 Test Street',
                '{}',
                '{}',
                '₫₫',
                2,
                '[]',
                'active',
                'sample-place-id',
                'sample-cid'
            )
            """
        ),
        {"complete_address_json": json.dumps({"city": "Hồ Chí Minh"})},
    )
    db.commit()


def test_register_login_review_and_favorites_flow():
    db = build_test_session()
    seed_place(db)

    register_response = register(
        RegisterRequest(
            user_name="traveler01",
            email="test@example.com",
            password="secret12",
        ),
        db,
    )
    profile_response = update_profile(
        UpdateProfileRequest(
            first_name="Test",
            last_name="User",
            birth_date="2000-01-15",
            gender=None,
            address=None,
        ),
        {"id": 1, "email": "test@example.com"},
        db,
    )
    login_response = login(LoginRequest(identifier="traveler01", password="secret12"), db)
    email_login_response = login(LoginRequest(email="test@example.com", password="secret12"), db)

    assert register_response.user.email == "test@example.com"
    assert register_response.user.user_name == "traveler01"
    assert register_response.user.first_name is None
    assert register_response.access_token
    assert profile_response.user.first_name == "Test"
    assert profile_response.user.gender is None
    assert profile_response.user.address is None
    assert login_response.access_token
    assert login_response.user.user_name == "traveler01"
    assert email_login_response.user.email == "test@example.com"

    current_user = {"id": 1, "email": "test@example.com"}
    review_response = create_review(
        ReviewCreateRequest(place_id=1, content="Very good", rating=5, image_urls=[]),
        current_user,
        db,
    )

    assert review_response.review_count == 1
    assert review_response.average_rating == 5.0

    second_review_response = create_review(
        ReviewCreateRequest(
            place_id=1,
            content="Pretty good",
            rating=4,
            image_urls=["https://example.com/review.jpg"],
        ),
        current_user,
        db,
    )

    assert second_review_response.review_count == 2
    assert second_review_response.average_rating == 4.5

    reviews_payload = list_reviews(1, db)
    favorites_payload = list_favorites(current_user, db)

    assert reviews_payload["items"][0].content == "Pretty good"
    assert reviews_payload["items"][0].image_urls == ["https://example.com/review.jpg"]
    assert reviews_payload["items"][0].user_name == "traveler01"
    assert favorites_payload["items"][0]["id"] == 1
    assert favorites_payload["items"][0]["rating"] == 4.5

    db.close()


def test_require_completed_profile_rejects_incomplete_profile():
    db = build_test_session()
    seed_place(db)
    register(
        RegisterRequest(
            user_name="traveler02",
            email="incomplete@example.com",
            password="secret12",
        ),
        db,
    )

    try:
        require_completed_profile({"id": 1, "email": "incomplete@example.com"}, db)
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Please complete your profile before using this feature."
    else:
        raise AssertionError("Expected incomplete profile to be rejected.")

    db.close()
