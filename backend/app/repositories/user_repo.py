"""User repository.

Repository layer only talks to database.
It should not contain HTTP-specific logic.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_user(row) -> User:
        return User(
            id=int(row["id"]),
            user_name=row["user_name"],
            email=row["email"],
            password_hash=row["password_hash"],
        )

    def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by id."""
        row = (
            self.db.execute(
                text(
                    """
                    SELECT id, user_name, email, password_hash
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
                    """
                    SELECT id, user_name, email, password_hash
                    FROM users
                    WHERE email = :email
                    """
                ),
                {"email": email},
            )
            .mappings()
            .first()
        )
        return self._to_user(row) if row else None

    def create_user(self, email: str, password_hash: str, user_name: str | None = None) -> User:
        """Insert new user into database and return created record."""
        derived_user_name = user_name or email.split("@", 1)[0]
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO users (user_name, email, password_hash)
                    VALUES (:user_name, :email, :password_hash)
                    RETURNING id, user_name, email, password_hash
                    """
                ),
                {
                    "user_name": derived_user_name,
                    "email": email,
                    "password_hash": password_hash,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_user(row)
