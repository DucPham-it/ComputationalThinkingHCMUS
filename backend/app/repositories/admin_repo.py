"""Admin approval repository."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_profile(row) -> dict:
        return {
            "user_id": int(row["user_id"]),
            "status": row.get("status"),
            "role": row.get("role"),
            "approved_by": int(row["approved_by"]) if row.get("approved_by") is not None else None,
            "approved_at": str(row["approved_at"]) if row.get("approved_at") is not None else None,
            "user_name": row.get("user_name"),
            "email": row.get("email"),
        }

    def get_profile(self, user_id: int) -> dict | None:
        row = (
            self.db.execute(
                text(
                    """
                    SELECT
                        a.user_id,
                        a.status,
                        a.role,
                        a.approved_by,
                        a.approved_at,
                        u.user_name,
                        u.email
                    FROM admins AS a
                    LEFT JOIN users AS u ON u.id = a.user_id
                    WHERE a.user_id = :user_id
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .first()
        )
        return self._to_profile(row) if row else None

    def is_approved_admin(self, user_id: int) -> bool:
        try:
            profile = self.get_profile(user_id)
        except DBAPIError:
            self.db.rollback()
            return False
        return bool(profile and profile.get("status") == "approved")

    def request_access(self, user_id: int) -> dict:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO admins (user_id, status, role)
                    VALUES (:user_id, 'pending', 'admin')
                    ON CONFLICT (user_id)
                    DO UPDATE SET status = CASE
                        WHEN admins.status = 'rejected' THEN 'pending'
                        ELSE admins.status
                    END
                    RETURNING user_id, status, role, approved_by, approved_at
                    """
                ),
                {"user_id": user_id},
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_profile(row)

    def list_members(self) -> list[dict]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        a.user_id,
                        a.status,
                        a.role,
                        a.approved_by,
                        a.approved_at,
                        u.user_name,
                        u.email
                    FROM admins AS a
                    LEFT JOIN users AS u ON u.id = a.user_id
                    ORDER BY
                        CASE a.status
                            WHEN 'pending' THEN 0
                            WHEN 'approved' THEN 1
                            ELSE 2
                        END,
                        a.user_id
                    """
                )
            )
            .mappings()
            .all()
        )
        return [self._to_profile(row) for row in rows]

    def approve_member(self, *, user_id: int, approved_by: int) -> dict:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO admins (user_id, status, role, approved_by, approved_at)
                    VALUES (:user_id, 'approved', 'admin', :approved_by, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        status = 'approved',
                        role = COALESCE(admins.role, 'admin'),
                        approved_by = :approved_by,
                        approved_at = CURRENT_TIMESTAMP
                    RETURNING user_id, status, role, approved_by, approved_at
                    """
                ),
                {"user_id": user_id, "approved_by": approved_by},
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_profile(row)

    def reject_member(self, *, user_id: int, approved_by: int) -> dict:
        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO admins (user_id, status, role, approved_by, approved_at)
                    VALUES (:user_id, 'rejected', 'admin', :approved_by, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        status = 'rejected',
                        approved_by = :approved_by,
                        approved_at = CURRENT_TIMESTAMP
                    RETURNING user_id, status, role, approved_by, approved_at
                    """
                ),
                {"user_id": user_id, "approved_by": approved_by},
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self._to_profile(row)
