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
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)()


def test_get_place_detail_reads_local_place_data():
    db = build_test_session()
    place_repo = PlaceRepository(db)
    place = place_repo.upsert_external_place(
        external_place_id="google-place-1",
        name="Pizza Corner",
        address="123 Test Street",
        rating=4.2,
        price_level=2,
        open_now=True,
        primary_type="restaurant",
    )

    db.execute(
        text(
            """
            INSERT INTO reviews (user_id, place_id, content, rating)
            VALUES (1, :place_id, 'Great', 5)
            """
        ),
        {"place_id": place.id},
    )
    db.commit()

    response = get_place_detail(place.id, db)

    assert response.id == place.id
    assert response.name == "Pizza Corner"
    assert response.address == "123 Test Street"
    assert response.review_count == 1
    assert response.rating == 5.0

    db.close()
