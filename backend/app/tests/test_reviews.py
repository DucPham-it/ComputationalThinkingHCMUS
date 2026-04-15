from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes.auth import login, register
from app.api.routes.favorites import list_favorites
from app.api.routes.reviews import create_review, list_reviews
from app.schemas.review_schema import ReviewCreateRequest
from app.schemas.user_schema import LoginRequest, RegisterRequest


def build_test_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        connection.exec_driver_sql(
            """
            CREATE TABLE places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                rating REAL,
                external_place_id TEXT UNIQUE,
                latitude REAL,
                longitude REAL,
                price_level INTEGER,
                open_now BOOLEAN,
                photo_url TEXT,
                contact_phone TEXT,
                primary_type TEXT
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
                rating INTEGER NOT NULL
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


def test_register_login_review_and_favorites_flow():
    db = build_test_session()

    register_response = register(RegisterRequest(email="test@example.com", password="secret12"), db)
    login_response = login(LoginRequest(email="test@example.com", password="secret12"), db)

    assert register_response.email == "test@example.com"
    assert register_response.access_token
    assert login_response.access_token

    current_user = {"id": 1, "email": "test@example.com"}
    review_response = create_review(
        ReviewCreateRequest(place_id=1, content="Very good", rating=5, image_urls=[]),
        current_user,
        db,
    )

    assert review_response.review_count == 1
    assert review_response.average_rating == 5.0

    reviews_payload = list_reviews(1, db)
    favorites_payload = list_favorites(current_user, db)

    assert reviews_payload["items"][0].content == "Very good"
    assert favorites_payload["items"][0]["id"] == 1

    db.close()
