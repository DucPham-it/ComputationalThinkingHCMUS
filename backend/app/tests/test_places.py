import json

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.routes.places import get_place_detail


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
                review_rating REAL,
                review_count INTEGER NOT NULL DEFAULT 0,
                reviews_per_rating_json TEXT NOT NULL DEFAULT '{}',
                open_hours_json TEXT NOT NULL DEFAULT '{}',
                popular_times_json TEXT NOT NULL DEFAULT '{}',
                price_range TEXT,
                price_level INTEGER,
                website TEXT,
                phone TEXT,
                thumbnail TEXT,
                images_json TEXT NOT NULL DEFAULT '[]',
                descriptions TEXT,
                about_json TEXT NOT NULL DEFAULT '[]',
                status TEXT,
                place_id TEXT UNIQUE,
                cid TEXT UNIQUE
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
                review_rating,
                review_count,
                reviews_per_rating_json,
                open_hours_json,
                popular_times_json,
                price_range,
                price_level,
                phone,
                thumbnail,
                images_json,
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
                4.8,
                1,
                :reviews_per_rating_json,
                :open_hours_json,
                :popular_times_json,
                '₫₫',
                2,
                '0909000000',
                'https://example.com/pizza.jpg',
                :images_json,
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
            "reviews_per_rating_json": json.dumps({"5": 1}),
            "open_hours_json": json.dumps({"Thứ Tư": ["10:00–22:00"]}, ensure_ascii=False),
            "popular_times_json": json.dumps({}),
            "images_json": json.dumps(["https://example.com/pizza.jpg"]),
            "about_json": json.dumps([{"name": "Ăn tại chỗ", "enabled": True}], ensure_ascii=False),
        },
    ).scalar_one()
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
