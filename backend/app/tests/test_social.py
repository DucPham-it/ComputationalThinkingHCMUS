from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.routes.social import (
    add_comment,
    create_post,
    get_my_social_profile,
    like_post,
    list_feed,
    list_visited_places,
    record_visited_place,
    share_post,
    update_post,
)
from app.schemas.social_schema import (
    RouteCompletionRequest,
    SocialCommentCreateRequest,
    SocialPostCreateRequest,
    SocialPostUpdateRequest,
)


def build_social_test_session():
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
        connection.execute(
            text(
                """
                INSERT INTO users (
                    id,
                    user_name,
                    email,
                    password_hash,
                    first_name,
                    last_name,
                    birth_date
                )
                VALUES
                    (1, 'traveler01', 'test@example.com', 'hash', 'Test', 'User', '2000-01-01'),
                    (2, 'traveler02', 'other@example.com', 'hash', 'Other', 'User', '2000-01-01')
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO places (
                    id,
                    title,
                    category,
                    address_text,
                    open_hours_json,
                    popular_times_json,
                    about_json,
                    status,
                    place_id,
                    cid
                )
                VALUES (
                    1,
                    'Museum Test',
                    'museum',
                    '1 Test Street',
                    '{}',
                    '{}',
                    '[]',
                    'active',
                    'museum-test',
                    'museum-cid'
                )
                """
            )
        )
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()


def test_social_route_completion_post_interactions_and_profile():
    db = build_social_test_session()
    current_user = {"id": 1, "email": "test@example.com"}

    visited = record_visited_place(
        RouteCompletionRequest(
            place_id=1,
            route_origin="10.0,106.0",
            route_destination="Museum Test",
            distance_text="3 km",
            duration_text="12 mins",
            distance_km=3,
            duration_seconds=720,
            travel_mode="driving",
        ),
        current_user,
        db,
    )
    visited_payload = list_visited_places(current_user, db)

    post = create_post(
        SocialPostCreateRequest(
            visited_place_id=visited.id,
            content="Great visit",
            rating=5,
        ),
        current_user,
        db,
    )
    liked = like_post(post.id, current_user, db)
    commented = add_comment(
        post.id,
        SocialCommentCreateRequest(content="Nice review"),
        current_user,
        db,
    )
    shared = share_post(post.id, current_user, db)
    feed = list_feed(current_user, db)
    profile = get_my_social_profile(current_user, db)
    updated = update_post(
        post.id,
        SocialPostUpdateRequest(content="Great visit after the route", rating=4),
        current_user,
        db,
    )

    assert visited.place_name == "Museum Test"
    assert visited_payload[0].id == visited.id
    assert post.place_id == 1
    assert liked.like_count == 1
    assert liked.viewer_has_liked is True
    assert commented.comment_count == 1
    assert commented.comments[0].content == "Nice review"
    assert shared.share_count == 1
    assert shared.viewer_has_shared is True
    assert feed.items[0].content == "Great visit"
    assert profile.stats.post_count == 1
    assert profile.stats.shared_count == 1
    assert profile.stats.visited_count == 1
    assert len(profile.items) == 2
    assert updated.content == "Great visit after the route"
    assert updated.rating == 4

    db.close()


def test_social_post_edit_requires_owner():
    db = build_social_test_session()
    owner = {"id": 1, "email": "test@example.com"}
    other_user = {"id": 2, "email": "other@example.com"}

    visited = record_visited_place(RouteCompletionRequest(place_id=1), owner, db)
    post = create_post(
        SocialPostCreateRequest(visited_place_id=visited.id, content="Owner post", rating=5),
        owner,
        db,
    )

    try:
        update_post(
            post.id,
            SocialPostUpdateRequest(content="Edited by someone else", rating=1),
            other_user,
            db,
        )
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Only the post owner can edit this post."
    else:
        raise AssertionError("Expected non-owner edit to be rejected.")

    db.close()
