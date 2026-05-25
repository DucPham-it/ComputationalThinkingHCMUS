"""Create or reset the first approved admin account.

This script is intended for deployment setup. It reads admin credentials from
environment variables and upserts an approved admin user in the active database.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.repositories.admin_repo import AdminRepository
from app.repositories.user_repo import UserRepository


def _read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        raise SystemExit(1)
    return value


def main() -> None:
    email = _read_required_env("ADMIN_EMAIL")
    password = _read_required_env("ADMIN_PASSWORD")
    user_name = os.getenv("ADMIN_USER_NAME", os.getenv("ADMIN_USERNAME", "admin")).strip()
    first_name = os.getenv("ADMIN_FIRST_NAME", "Admin").strip() or None
    last_name = os.getenv("ADMIN_LAST_NAME", "User").strip() or None

    if len(password) < 6:
        print("ADMIN_PASSWORD must be at least 6 characters.", file=sys.stderr)
        raise SystemExit(1)

    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        existing_by_email = user_repo.get_by_email(email)
        existing_by_user_name = user_repo.get_by_user_name(user_name)

        if (
            existing_by_email is not None
            and existing_by_user_name is not None
            and existing_by_email.id != existing_by_user_name.id
        ):
            print(
                "ADMIN_EMAIL and ADMIN_USER_NAME already belong to different users.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        existing_user = existing_by_email or existing_by_user_name
        if existing_user is None:
            user = user_repo.create_user(
                email=email,
                password_hash=hash_password(password),
                user_name=user_name,
                first_name=first_name,
                last_name=last_name,
            )
        else:
            db.execute(
                text(
                    """
                    UPDATE users
                    SET user_name = :user_name,
                        email = :email,
                        password_hash = :password_hash,
                        first_name = COALESCE(:first_name, first_name),
                        last_name = COALESCE(:last_name, last_name),
                        is_virtual = 0
                    WHERE id = :user_id
                    """
                ),
                {
                    "user_id": existing_user.id,
                    "user_name": user_name,
                    "email": email,
                    "password_hash": hash_password(password),
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            db.commit()
            user = user_repo.get_by_id(existing_user.id)
            if user is None:
                print("Admin user disappeared after update.", file=sys.stderr)
                raise SystemExit(1)

        AdminRepository(db).approve_member(user_id=user.id, approved_by=user.id)
        print(f"Seeded approved admin: {user.user_name} <{user.email}>")
    except SQLAlchemyError as exc:
        db.rollback()
        print(f"Failed to seed admin: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    finally:
        db.close()


if __name__ == "__main__":
    main()
