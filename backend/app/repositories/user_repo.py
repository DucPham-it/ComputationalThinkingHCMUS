"""User repository."""

from __future__ import annotations

from sqlalchemy import text
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
        address,
        avatar_url,
        is_virtual
    """

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_user(row) -> User:
        return User(
            id=int(row["id"]),
            user_name=row["user_name"],
            email=row["email"],
            password_hash=row["password_hash"],
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            birth_date=row.get("birth_date"),
            gender=row.get("gender"),
            address=row.get("address"),
            avatar_url=row.get("avatar_url"),
            is_virtual=bool(row.get("is_virtual") or False),
        )

    def get_by_id(self, user_id: int) -> User | None:
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
        avatar_url: str | None = None,
        is_virtual: bool = False,
    ) -> User:
        row = (
            self.db.execute(
                text(
                    f"""
                    INSERT INTO users (
                        user_name,
                        email,
                        password_hash,
                        first_name,
                        last_name,
                        birth_date,
                        gender,
                        address,
                        avatar_url,
                        is_virtual
                    )
                    VALUES (
                        :user_name,
                        :email,
                        :password_hash,
                        :first_name,
                        :last_name,
                        :birth_date,
                        :gender,
                        :address,
                        :avatar_url,
                        :is_virtual
                    )
                    RETURNING {self.USER_COLUMNS}
                    """
                ),
                {
                    "user_name": user_name,
                    "email": email,
                    "password_hash": password_hash,
                    "first_name": first_name,
                    "last_name": last_name,
                    "birth_date": birth_date,
                    "gender": gender,
                    "address": address,
                    "avatar_url": avatar_url,
                    "is_virtual": is_virtual,
                },
            )
            .mappings()
            .one()
        )
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
        row = (
            self.db.execute(
                text(
                    f"""
                    UPDATE users
                    SET first_name = :first_name,
                        last_name = :last_name,
                        birth_date = :birth_date,
                        gender = :gender,
                        address = :address
                    WHERE id = :user_id
                    RETURNING {self.USER_COLUMNS}
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
            .first()
        )
        self.db.commit()
        if row is None:
            raise ValueError("User not found after update.")
        return self._to_user(row)
