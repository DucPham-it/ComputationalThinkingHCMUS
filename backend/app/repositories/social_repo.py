"""Repository for social feed posts, interactions, and visited places."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.social import SocialComment, SocialPost, VisitedPlace
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.upload_storage import default_avatar_url


class SocialRepository:
    def __init__(self, db: Session):
        self.db = db
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create social tables when the database has not been migrated yet."""
        dialect_name = self.db.get_bind().dialect.name
        id_column = "id BIGSERIAL PRIMARY KEY"
        integer_type = "BIGINT"
        timestamp_type = "TIMESTAMPTZ"
        if dialect_name == "sqlite":
            id_column = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            integer_type = "INTEGER"
            timestamp_type = "TEXT"

        statements = [
            f"""
            CREATE TABLE IF NOT EXISTS user_visited_places (
                {id_column},
                user_id {integer_type} NOT NULL,
                place_id {integer_type} NOT NULL,
                route_origin TEXT,
                route_destination TEXT,
                distance_text TEXT,
                duration_text TEXT,
                distance_km DOUBLE PRECISION,
                duration_seconds INTEGER,
                travel_mode TEXT,
                visited_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS social_posts (
                {id_column},
                user_id {integer_type} NOT NULL,
                place_id {integer_type} NOT NULL,
                visited_place_id {integer_type},
                content TEXT NOT NULL,
                rating INTEGER NOT NULL,
                created_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS social_post_likes (
                {id_column},
                post_id {integer_type} NOT NULL,
                user_id {integer_type} NOT NULL,
                created_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS social_post_comments (
                {id_column},
                post_id {integer_type} NOT NULL,
                user_id {integer_type} NOT NULL,
                content TEXT NOT NULL,
                created_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS social_post_shares (
                {id_column},
                post_id {integer_type} NOT NULL,
                user_id {integer_type} NOT NULL,
                created_at {timestamp_type} NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_user_visited_places_user
            ON user_visited_places (user_id, visited_at DESC)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_social_posts_created
            ON social_posts (created_at DESC, id DESC)
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_social_post_likes_unique
            ON social_post_likes (post_id, user_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_social_post_comments_post
            ON social_post_comments (post_id, created_at ASC)
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_social_post_shares_unique
            ON social_post_shares (post_id, user_id)
            """,
        ]
        for statement in statements:
            self.db.execute(text(statement))
        self.db.commit()

    @staticmethod
    def _to_visited_place(row) -> VisitedPlace:
        return VisitedPlace(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            place_id=int(row["place_id"]),
            place_name=row["place_name"],
            place_address=row["place_address"],
            place_photo_url=row.get("place_photo_url"),
            place_rating=float(row["place_rating"]) if row.get("place_rating") is not None else None,
            route_origin=row.get("route_origin"),
            route_destination=row.get("route_destination"),
            distance_text=row.get("distance_text"),
            duration_text=row.get("duration_text"),
            distance_km=float(row["distance_km"]) if row.get("distance_km") is not None else None,
            duration_seconds=(
                int(row["duration_seconds"]) if row.get("duration_seconds") is not None else None
            ),
            travel_mode=row.get("travel_mode"),
            visited_at=row.get("visited_at"),
        )

    @staticmethod
    def _to_comment(row, viewer_id: int | None) -> SocialComment:
        user_id = int(row["user_id"])
        return SocialComment(
            id=int(row["id"]),
            post_id=int(row["post_id"]),
            user_id=user_id,
            user_name=row.get("user_name"),
            user_avatar_url=row.get("user_avatar_url") or default_avatar_url(),
            content=row["content"],
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            is_owner=viewer_id == user_id,
        )

    @staticmethod
    def _to_post(row, viewer_id: int | None) -> SocialPost:
        user_id = int(row["user_id"])
        return SocialPost(
            id=int(row["id"]),
            user_id=user_id,
            user_name=row.get("user_name"),
            user_avatar_url=row.get("user_avatar_url") or default_avatar_url(),
            place_id=int(row["place_id"]),
            place_name=row.get("place_name"),
            place_address=row.get("place_address"),
            place_photo_url=row.get("place_photo_url"),
            visited_place_id=(
                int(row["visited_place_id"]) if row.get("visited_place_id") is not None else None
            ),
            visited_at=row.get("visited_at"),
            content=row["content"],
            rating=int(row["rating"]),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            like_count=int(row.get("like_count") or 0),
            comment_count=int(row.get("comment_count") or 0),
            share_count=int(row.get("share_count") or 0),
            viewer_has_liked=bool(row.get("viewer_has_liked") or False),
            viewer_has_shared=bool(row.get("viewer_has_shared") or False),
            is_owner=viewer_id == user_id,
            timeline_type=row.get("timeline_type") or "post",
            shared_at=row.get("shared_at"),
        )

    def _place_exists(self, place_id: int) -> bool:
        row = self.db.execute(
            text("SELECT id FROM places WHERE id = :place_id"),
            {"place_id": place_id},
        ).first()
        return row is not None

    def _visited_place_query(self, where_clause: str) -> str:
        return f"""
            SELECT
                uvp.id,
                uvp.user_id,
                uvp.place_id,
                uvp.route_origin,
                uvp.route_destination,
                uvp.distance_text,
                uvp.duration_text,
                uvp.distance_km,
                uvp.duration_seconds,
                uvp.travel_mode,
                CAST(uvp.visited_at AS TEXT) AS visited_at,
                p.title AS place_name,
                p.address_text AS place_address,
                prs.average_rating AS place_rating,
                (
                    SELECT pi.image_url
                    FROM place_images AS pi
                    WHERE pi.place_id = p.id
                    ORDER BY pi.is_primary DESC, pi.sort_order ASC, pi.id ASC
                    LIMIT 1
                ) AS place_photo_url
            FROM user_visited_places AS uvp
            JOIN places AS p ON p.id = uvp.place_id
            LEFT JOIN place_review_stats AS prs ON prs.place_id = p.id
            {where_clause}
        """

    def record_visited_place(
        self,
        *,
        user_id: int,
        place_id: int,
        route_origin: str | None = None,
        route_destination: str | None = None,
        distance_text: str | None = None,
        duration_text: str | None = None,
        distance_km: float | None = None,
        duration_seconds: int | None = None,
        travel_mode: str | None = None,
    ) -> VisitedPlace | None:
        if not self._place_exists(place_id):
            return None

        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO user_visited_places (
                        user_id,
                        place_id,
                        route_origin,
                        route_destination,
                        distance_text,
                        duration_text,
                        distance_km,
                        duration_seconds,
                        travel_mode
                    )
                    VALUES (
                        :user_id,
                        :place_id,
                        :route_origin,
                        :route_destination,
                        :distance_text,
                        :duration_text,
                        :distance_km,
                        :duration_seconds,
                        :travel_mode
                    )
                    RETURNING id
                    """
                ),
                {
                    "user_id": user_id,
                    "place_id": place_id,
                    "route_origin": route_origin,
                    "route_destination": route_destination,
                    "distance_text": distance_text,
                    "duration_text": duration_text,
                    "distance_km": distance_km,
                    "duration_seconds": duration_seconds,
                    "travel_mode": travel_mode,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self.get_visited_place(user_id=user_id, visited_place_id=int(row["id"]))

    def get_visited_place(self, *, user_id: int, visited_place_id: int) -> VisitedPlace | None:
        row = (
            self.db.execute(
                text(
                    self._visited_place_query(
                        """
                        WHERE uvp.user_id = :user_id AND uvp.id = :visited_place_id
                        """
                    )
                ),
                {"user_id": user_id, "visited_place_id": visited_place_id},
            )
            .mappings()
            .first()
        )
        return self._to_visited_place(row) if row else None

    def list_visited_places(self, *, user_id: int, limit: int = 50) -> list[VisitedPlace]:
        rows = (
            self.db.execute(
                text(
                    self._visited_place_query(
                        """
                        WHERE uvp.user_id = :user_id
                        ORDER BY uvp.visited_at DESC, uvp.id DESC
                        LIMIT :limit
                        """
                    )
                ),
                {"user_id": user_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        return [self._to_visited_place(row) for row in rows]

    def _post_select_query(self, where_clause: str) -> str:
        return f"""
            SELECT
                sp.id,
                sp.user_id,
                sp.place_id,
                sp.visited_place_id,
                sp.content,
                sp.rating,
                CAST(sp.created_at AS TEXT) AS created_at,
                CAST(sp.updated_at AS TEXT) AS updated_at,
                CAST(uvp.visited_at AS TEXT) AS visited_at,
                u.user_name,
                u.avatar_url AS user_avatar_url,
                p.title AS place_name,
                p.address_text AS place_address,
                (
                    SELECT pi.image_url
                    FROM place_images AS pi
                    WHERE pi.place_id = p.id
                    ORDER BY pi.is_primary DESC, pi.sort_order ASC, pi.id ASC
                    LIMIT 1
                ) AS place_photo_url,
                (
                    SELECT COUNT(*)
                    FROM social_post_likes AS spl
                    WHERE spl.post_id = sp.id
                ) AS like_count,
                (
                    SELECT COUNT(*)
                    FROM social_post_comments AS spc
                    WHERE spc.post_id = sp.id
                ) AS comment_count,
                (
                    SELECT COUNT(*)
                    FROM social_post_shares AS sps
                    WHERE sps.post_id = sp.id
                ) AS share_count,
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM social_post_likes AS viewer_like
                        WHERE viewer_like.post_id = sp.id
                          AND viewer_like.user_id = :viewer_id
                    )
                    THEN 1 ELSE 0
                END AS viewer_has_liked,
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM social_post_shares AS viewer_share
                        WHERE viewer_share.post_id = sp.id
                          AND viewer_share.user_id = :viewer_id
                    )
                    THEN 1 ELSE 0
                END AS viewer_has_shared,
                'post' AS timeline_type,
                NULL AS shared_at
            FROM social_posts AS sp
            JOIN users AS u ON u.id = sp.user_id
            JOIN places AS p ON p.id = sp.place_id
            LEFT JOIN user_visited_places AS uvp ON uvp.id = sp.visited_place_id
            {where_clause}
        """

    def _list_comments(
        self,
        *,
        post_id: int,
        viewer_id: int | None,
        limit: int = 3,
    ) -> list[SocialComment]:
        rows = (
            self.db.execute(
                text(
                    """
                    SELECT
                        spc.id,
                        spc.post_id,
                        spc.user_id,
                        spc.content,
                        CAST(spc.created_at AS TEXT) AS created_at,
                        CAST(spc.updated_at AS TEXT) AS updated_at,
                        u.user_name,
                        u.avatar_url AS user_avatar_url
                    FROM social_post_comments AS spc
                    JOIN users AS u ON u.id = spc.user_id
                    WHERE spc.post_id = :post_id
                    ORDER BY spc.created_at ASC, spc.id ASC
                    LIMIT :limit
                    """
                ),
                {"post_id": post_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        return [self._to_comment(row, viewer_id) for row in rows]

    def _hydrate_posts(
        self,
        rows,
        *,
        viewer_id: int | None,
        comment_limit: int = 3,
    ) -> list[SocialPost]:
        posts = [self._to_post(row, viewer_id) for row in rows]
        for post in posts:
            post.comments = self._list_comments(
                post_id=post.id,
                viewer_id=viewer_id,
                limit=comment_limit,
            )
        return posts

    def list_feed(self, *, viewer_id: int, limit: int = 30) -> list[SocialPost]:
        rows = (
            self.db.execute(
                text(
                    self._post_select_query(
                        """
                        ORDER BY sp.created_at DESC, sp.id DESC
                        LIMIT :limit
                        """
                    )
                ),
                {"viewer_id": viewer_id, "limit": limit},
            )
            .mappings()
            .all()
        )
        return self._hydrate_posts(rows, viewer_id=viewer_id)

    def get_post(self, *, post_id: int, viewer_id: int) -> SocialPost | None:
        row = (
            self.db.execute(
                text(self._post_select_query("WHERE sp.id = :post_id")),
                {"post_id": post_id, "viewer_id": viewer_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        posts = self._hydrate_posts([row], viewer_id=viewer_id)
        return posts[0] if posts else None

    def create_post(
        self,
        *,
        user_id: int,
        visited_place_id: int,
        content: str,
        rating: int,
    ) -> SocialPost | None:
        visited_place = self.get_visited_place(
            user_id=user_id,
            visited_place_id=visited_place_id,
        )
        if visited_place is None:
            return None

        row = (
            self.db.execute(
                text(
                    """
                    INSERT INTO social_posts (
                        user_id,
                        place_id,
                        visited_place_id,
                        content,
                        rating
                    )
                    VALUES (
                        :user_id,
                        :place_id,
                        :visited_place_id,
                        :content,
                        :rating
                    )
                    RETURNING id
                    """
                ),
                {
                    "user_id": user_id,
                    "place_id": visited_place.place_id,
                    "visited_place_id": visited_place.id,
                    "content": content,
                    "rating": rating,
                },
            )
            .mappings()
            .one()
        )
        self.db.commit()
        return self.get_post(post_id=int(row["id"]), viewer_id=user_id)

    def update_post(
        self,
        *,
        post_id: int,
        user_id: int,
        content: str,
        rating: int,
    ) -> SocialPost | None:
        row = (
            self.db.execute(
                text(
                    """
                    UPDATE social_posts
                    SET content = :content,
                        rating = :rating,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :post_id AND user_id = :user_id
                    RETURNING id
                    """
                ),
                {
                    "post_id": post_id,
                    "user_id": user_id,
                    "content": content,
                    "rating": rating,
                },
            )
            .mappings()
            .first()
        )
        self.db.commit()
        if row is None:
            return None
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def like_post(self, *, post_id: int, user_id: int) -> SocialPost | None:
        if self.get_post(post_id=post_id, viewer_id=user_id) is None:
            return None
        self.db.execute(
            text(
                """
                INSERT INTO social_post_likes (post_id, user_id)
                VALUES (:post_id, :user_id)
                ON CONFLICT (post_id, user_id) DO NOTHING
                """
            ),
            {"post_id": post_id, "user_id": user_id},
        )
        self.db.commit()
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def unlike_post(self, *, post_id: int, user_id: int) -> SocialPost | None:
        if self.get_post(post_id=post_id, viewer_id=user_id) is None:
            return None
        self.db.execute(
            text(
                """
                DELETE FROM social_post_likes
                WHERE post_id = :post_id AND user_id = :user_id
                """
            ),
            {"post_id": post_id, "user_id": user_id},
        )
        self.db.commit()
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def add_comment(self, *, post_id: int, user_id: int, content: str) -> SocialPost | None:
        if self.get_post(post_id=post_id, viewer_id=user_id) is None:
            return None
        self.db.execute(
            text(
                """
                INSERT INTO social_post_comments (post_id, user_id, content)
                VALUES (:post_id, :user_id, :content)
                """
            ),
            {"post_id": post_id, "user_id": user_id, "content": content},
        )
        self.db.commit()
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def share_post(self, *, post_id: int, user_id: int) -> SocialPost | None:
        if self.get_post(post_id=post_id, viewer_id=user_id) is None:
            return None
        self.db.execute(
            text(
                """
                INSERT INTO social_post_shares (post_id, user_id)
                VALUES (:post_id, :user_id)
                ON CONFLICT (post_id, user_id) DO NOTHING
                """
            ),
            {"post_id": post_id, "user_id": user_id},
        )
        self.db.commit()
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def unshare_post(self, *, post_id: int, user_id: int) -> SocialPost | None:
        if self.get_post(post_id=post_id, viewer_id=user_id) is None:
            return None
        self.db.execute(
            text(
                """
                DELETE FROM social_post_shares
                WHERE post_id = :post_id AND user_id = :user_id
                """
            ),
            {"post_id": post_id, "user_id": user_id},
        )
        self.db.commit()
        return self.get_post(post_id=post_id, viewer_id=user_id)

    def _list_user_posts(self, *, profile_user_id: int, viewer_id: int) -> list[SocialPost]:
        rows = (
            self.db.execute(
                text(
                    self._post_select_query(
                        """
                        WHERE sp.user_id = :profile_user_id
                        ORDER BY sp.created_at DESC, sp.id DESC
                        """
                    )
                ),
                {"profile_user_id": profile_user_id, "viewer_id": viewer_id},
            )
            .mappings()
            .all()
        )
        return self._hydrate_posts(rows, viewer_id=viewer_id)

    def _list_shared_posts(self, *, profile_user_id: int, viewer_id: int) -> list[SocialPost]:
        shared_query = self._post_select_query(
            """
            JOIN social_post_shares AS profile_share ON profile_share.post_id = sp.id
            WHERE profile_share.user_id = :profile_user_id
            ORDER BY profile_share.created_at DESC, profile_share.id DESC
            """
        ).replace(
            "'post' AS timeline_type,\n                NULL AS shared_at",
            "'share' AS timeline_type,\n                CAST(profile_share.created_at AS TEXT) AS shared_at",
        )
        rows = (
            self.db.execute(
                text(shared_query),
                {"profile_user_id": profile_user_id, "viewer_id": viewer_id},
            )
            .mappings()
            .all()
        )
        return self._hydrate_posts(rows, viewer_id=viewer_id)

    def get_profile(
        self,
        *,
        profile_user_id: int,
        viewer_id: int,
    ) -> tuple[User | None, dict[str, int], list[SocialPost]]:
        user = UserRepository(self.db).get_by_id(profile_user_id)
        if user is None:
            return None, {"post_count": 0, "shared_count": 0, "visited_count": 0}, []

        stats_row = (
            self.db.execute(
                text(
                    """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM social_posts
                            WHERE user_id = :profile_user_id
                        ) AS post_count,
                        (
                            SELECT COUNT(*)
                            FROM social_post_shares
                            WHERE user_id = :profile_user_id
                        ) AS shared_count,
                        (
                            SELECT COUNT(*)
                            FROM user_visited_places
                            WHERE user_id = :profile_user_id
                        ) AS visited_count
                    """
                ),
                {"profile_user_id": profile_user_id},
            )
            .mappings()
            .one()
        )
        stats = {
            "post_count": int(stats_row["post_count"] or 0),
            "shared_count": int(stats_row["shared_count"] or 0),
            "visited_count": int(stats_row["visited_count"] or 0),
        }
        own_posts = self._list_user_posts(profile_user_id=profile_user_id, viewer_id=viewer_id)
        shared_posts = self._list_shared_posts(profile_user_id=profile_user_id, viewer_id=viewer_id)
        items = own_posts + shared_posts
        items.sort(
            key=lambda post: (
                post.shared_at if post.timeline_type == "share" else post.created_at
            )
            or "",
            reverse=True,
        )
        return user, stats, items
