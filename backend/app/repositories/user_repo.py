"""User repository.

Repository layer only talks to database.
It should not contain HTTP-specific logic.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    USER_COLUMNS = """
        id,
        user_name,
        email,
        password_hash,
        first_name,
        last_name,
        birth_date,
        gender,
        address
    """

    def __init__(self, db: Session):
        self.db = db

    def _is_users_pkey_violation(self, exc: IntegrityError) -> bool:
        diag = getattr(exc.orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)
        return constraint_name == "users_pkey" or "users_pkey" in str(exc.orig)

    def _sync_user_id_sequence(self) -> None:
        bind = self.db.get_bind()
        if bind.dialect.name != "postgresql":
            return

        self.db.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('users', 'id'),
                    COALESCE((SELECT MAX(id) FROM users), 1),
                    (SELECT MAX(id) IS NOT NULL FROM users)
                )
                """
            )
        )
        self.db.commit()

    @staticmethod
    def _to_user(row) -> User:
        return User(
            id=int(row["id"]),
            user_name=row["user_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            birth_date=row["birth_date"],
            gender=row["gender"],
            address=row["address"],
        )

    def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by id."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {self.USER_COLUMNS}
                    FROM users
                    WHERE id = :user_id
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .first()
        )
        return self._to_user(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        """Fetch user by email for login/registration checks."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {self.USER_COLUMNS}
                    FROM users
                    WHERE LOWER(email) = LOWER(:email)
                    """
                ),
                {"email": email},
            )
            .mappings()
            .first()
        )
        return self._to_user(row) if row else None

    def get_by_user_name(self, user_name: str) -> User | None:
        """Fetch user by username for registration checks."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {self.USER_COLUMNS}
                    FROM users
                    WHERE LOWER(user_name) = LOWER(:user_name)
                    """
                ),
                {"user_name": user_name},
            )
            .mappings()
            .first()
        )
        return self._to_user(row) if row else None

    def get_by_identifier(self, identifier: str) -> User | None:
        """Fetch a user by either email or username for login."""
        row = (
            self.db.execute(
                text(
                    f"""
                    SELECT {self.USER_COLUMNS}
                    FROM users
                    WHERE LOWER(email) = LOWER(:identifier)
                       OR LOWER(user_name) = LOWER(:identifier)
                    ORDER BY CASE
                        WHEN LOWER(email) = LOWER(:identifier) THEN 0
                        ELSE 1
                    END,
                    id
                    LIMIT 1
                    """
                ),
                {"identifier": identifier},
            )
            .mappings()
            .first()
        )
        return self._to_user(row) if row else None

    def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        user_name: str,
        first_name: str | None = None,
        last_name: str | None = None,
        birth_date=None,
        gender: str | None = None,
        address: str | None = None,
    ) -> User:
        """Insert new user into database and return created record."""
        params = {
            "user_name": user_name,
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,
            "address": address,
        }
        insert_sql = text(
            """
            INSERT INTO users (
                user_name,
                email,
                password_hash,
                first_name,
                last_name,
                birth_date,
                gender,
                address
            )
            VALUES (
                :user_name,
                :email,
                :password_hash,
                :first_name,
                :last_name,
                :birth_date,
                :gender,
                :address
            )
            RETURNING
                id,
                user_name,
                email,
                password_hash,
                first_name,
                last_name,
                birth_date,
                gender,
                address
            """
        )

        try:
            row = self.db.execute(insert_sql, params).mappings().one()
            self.db.commit()
            return self._to_user(row)
        except IntegrityError as exc:
            self.db.rollback()
            if not self._is_users_pkey_violation(exc):
                raise

            self._sync_user_id_sequence()
            row = self.db.execute(insert_sql, params).mappings().one()
            self.db.commit()
            return self._to_user(row)

    def update_profile(
        self,
        *,
        user_id: int,
        first_name: str,
        last_name: str,
        birth_date,
        gender: str | None = None,
        address: str | None = None,
    ) -> User:
        """Update a user's profile fields and return the latest record."""
        row = (
            self.db.execute(
                text(
                    """
                    UPDATE users
                    SET first_name = :first_name,
                        last_name = :last_name,
                        birth_date = :birth_date,
                        gender = :gender,
                        address = :address
                    WHERE id = :user_id
                    RETURNING
                        id,
                        user_name,
                        email,
                        password_hash,
                        first_name,
                        last_name,
                        birth_date,
                        gender,
                        address
                    """
                ),
                {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "birth_date": birth_date,
                    "gender": gender,
                    "address": address,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_user(row)
