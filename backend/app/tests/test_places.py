import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.routes.places import get_place_detail
from app.repositories.place_repo import PlaceRepository


def build_test_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as connection:
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
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()


def test_get_place_detail_reads_local_place_data():
    db = build_test_session()
    place_id = db.execute(
        text(
            """
            INSERT INTO places (
                title,
                category,
                complete_address_json,
                address_text,
                latitude,
                longitude,
                open_hours_json,
                popular_times_json,
                price_range,
                price_level,
                phone,
                descriptions,
                about_json,
                status,
                place_id,
                cid
            )
            VALUES (
                'Pizza Corner',
                'Nhà hàng Việt Nam',
                :complete_address_json,
                '123 Test Street',
                10.8,
                106.7,
                :open_hours_json,
                :popular_times_json,
                '₫₫',
                2,
                '0909000000',
                'Fresh pizza in the local catalog.',
                :about_json,
                'active',
                'sample-place-id',
                'sample-cid'
            )
            RETURNING id
            """
        ),
        {
            "complete_address_json": json.dumps({"city": "Hồ Chí Minh"}),
            "open_hours_json": json.dumps({"Thứ Tư": ["10:00–22:00"]}, ensure_ascii=False),
            "popular_times_json": json.dumps({}),
            "about_json": json.dumps([{"name": "Ăn tại chỗ", "enabled": True}], ensure_ascii=False),
        },
    ).scalar_one()
    db.execute(
        text(
            """
            INSERT INTO place_review_stats (
                place_id,
                average_rating,
                review_count,
                rating_5_count
            )
            VALUES (:place_id, 4.8, 1, 1)
            """
        ),
        {"place_id": place_id},
    )
    db.execute(
        text(
            """
            INSERT INTO place_images (place_id, image_url, sort_order, is_primary)
            VALUES (:place_id, 'https://example.com/pizza.jpg', 0, 1)
            """
        ),
        {"place_id": place_id},
    )
    db.commit()

    response = get_place_detail(place_id, db)

    assert response.id == place_id
    assert response.name == "Pizza Corner"
    assert response.address == "123 Test Street"
    assert response.review_count == 1
    assert response.rating == 4.8
    assert response.price_range == "₫₫"
    assert response.images == ["https://example.com/pizza.jpg"]

    db.close()


def test_search_local_places_matches_tokens_and_category_aliases():
    db = build_test_session()
    db.execute(
        text(
            """
            INSERT INTO places (
                title,
                category,
                address_text,
                open_hours_json,
                popular_times_json,
                about_json,
                status
            )
            VALUES (
                'Com Tam Corner',
                'Nhà hàng Việt Nam',
                '456 Test Street',
                '{}',
                '{}',
                '[]',
                'active'
            )
            """
        )
    )
    db.execute(
        text(
            """
            INSERT INTO places (
                title,
                category,
                address_text,
                open_hours_json,
                popular_times_json,
                about_json,
                status
            )
            VALUES (
                'Quiet Coffee',
                'Quán cà phê',
                '789 Test Street',
                '{}',
                '{}',
                '[]',
                'active'
            )
            """
        )
    )
    db.commit()

    repo = PlaceRepository(db)

    restaurant_results = repo.search_local_places("nha hang gia dinh", limit=10)
    cafe_results = repo.search_local_places("quiet cafe gan day", limit=10)

    assert [place.name for place in restaurant_results] == ["Com Tam Corner"]
    assert [place.name for place in cafe_results] == ["Quiet Coffee"]

    db.close()
