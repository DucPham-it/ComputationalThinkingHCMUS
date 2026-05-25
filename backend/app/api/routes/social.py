"""Social feed API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_completed_profile
from app.db.session import get_db
from app.models.social import SocialComment, SocialPost, VisitedPlace
from app.repositories.social_repo import SocialRepository
from app.schemas.social_schema import (
    SocialCommentCreateRequest,
    SocialCommentResponse,
    SocialFeedResponse,
    SocialPostCreateRequest,
    SocialPostResponse,
    SocialPostUpdateRequest,
    SocialProfileResponse,
    SocialProfileStatsResponse,
    SocialProfileUserResponse,
    VisitedPlaceCreateRequest,
    VisitedPlaceResponse,
)

router = APIRouter()


def _visited_place_response(visited_place: VisitedPlace) -> VisitedPlaceResponse:
    return VisitedPlaceResponse(
        id=visited_place.id,
        user_id=visited_place.user_id,
        place_id=visited_place.place_id,
        place_name=visited_place.place_name,
        place_address=visited_place.place_address,
        place_photo_url=visited_place.place_photo_url,
        place_rating=visited_place.place_rating,
        route_origin=visited_place.route_origin,
        route_destination=visited_place.route_destination,
        distance_text=visited_place.distance_text,
        duration_text=visited_place.duration_text,
        distance_km=visited_place.distance_km,
        duration_seconds=visited_place.duration_seconds,
        travel_mode=visited_place.travel_mode,
        visited_at=visited_place.visited_at,
    )


def _comment_response(comment: SocialComment) -> SocialCommentResponse:
    return SocialCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        user_name=comment.user_name,
        user_avatar_url=comment.user_avatar_url,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        is_owner=comment.is_owner,
    )


def _post_response(post: SocialPost) -> SocialPostResponse:
    return SocialPostResponse(
        id=post.id,
        user_id=post.user_id,
        user_name=post.user_name,
        user_avatar_url=post.user_avatar_url,
        place_id=post.place_id,
        place_name=post.place_name,
        place_address=post.place_address,
        place_photo_url=post.place_photo_url,
        visited_place_id=post.visited_place_id,
        visited_at=post.visited_at,
        content=post.content,
        rating=post.rating,
        created_at=post.created_at,
        updated_at=post.updated_at,
        like_count=post.like_count,
        comment_count=post.comment_count,
        share_count=post.share_count,
        viewer_has_liked=post.viewer_has_liked,
        viewer_has_shared=post.viewer_has_shared,
        is_owner=post.is_owner,
        timeline_type=post.timeline_type,
        shared_at=post.shared_at,
        comments=[_comment_response(comment) for comment in post.comments],
    )


@router.get("/visited-places", response_model=list[VisitedPlaceResponse])
def list_visited_places(
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> list[VisitedPlaceResponse]:
    repo = SocialRepository(db)
    return [
        _visited_place_response(visited_place)
        for visited_place in repo.list_visited_places(user_id=current_user["id"])
    ]


@router.post("/visited-places", response_model=VisitedPlaceResponse, status_code=status.HTTP_201_CREATED)
def record_visited_place(
    payload: VisitedPlaceCreateRequest,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> VisitedPlaceResponse:
    repo = SocialRepository(db)
    visited_place = repo.record_visited_place(
        user_id=current_user["id"],
        place_id=payload.place_id,
        route_origin=payload.route_origin,
        route_destination=payload.route_destination,
        distance_text=payload.distance_text,
        duration_text=payload.duration_text,
        distance_km=payload.distance_km,
        duration_seconds=payload.duration_seconds,
        travel_mode=payload.travel_mode,
    )
    if visited_place is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found in the local catalog.",
        )
    return _visited_place_response(visited_place)


@router.get("/feed", response_model=SocialFeedResponse)
def list_feed(
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialFeedResponse:
    repo = SocialRepository(db)
    return SocialFeedResponse(
        items=[_post_response(post) for post in repo.list_feed(viewer_id=current_user["id"])]
    )


@router.post("/posts", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: SocialPostCreateRequest,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    repo = SocialRepository(db)
    post = repo.create_post(
        user_id=current_user["id"],
        visited_place_id=payload.visited_place_id,
        content=payload.content,
        rating=payload.rating,
    )
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Create a post from a place you have marked as visited.",
        )
    return _post_response(post)


@router.put("/posts/{post_id}", response_model=SocialPostResponse)
def update_post(
    post_id: int,
    payload: SocialPostUpdateRequest,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    repo = SocialRepository(db)
    existing_post = repo.get_post(post_id=post_id, viewer_id=current_user["id"])
    if existing_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    if not existing_post.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the post owner can edit this post.",
        )

    updated_post = repo.update_post(
        post_id=post_id,
        user_id=current_user["id"],
        content=payload.content,
        rating=payload.rating,
    )
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(updated_post)


@router.post("/posts/{post_id}/like", response_model=SocialPostResponse)
def like_post(
    post_id: int,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    post = SocialRepository(db).like_post(post_id=post_id, user_id=current_user["id"])
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(post)


@router.delete("/posts/{post_id}/like", response_model=SocialPostResponse)
def unlike_post(
    post_id: int,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    post = SocialRepository(db).unlike_post(post_id=post_id, user_id=current_user["id"])
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(post)


@router.post("/posts/{post_id}/comments", response_model=SocialPostResponse)
def add_comment(
    post_id: int,
    payload: SocialCommentCreateRequest,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    post = SocialRepository(db).add_comment(
        post_id=post_id,
        user_id=current_user["id"],
        content=payload.content,
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(post)


@router.post("/posts/{post_id}/share", response_model=SocialPostResponse)
def share_post(
    post_id: int,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    post = SocialRepository(db).share_post(post_id=post_id, user_id=current_user["id"])
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(post)


@router.delete("/posts/{post_id}/share", response_model=SocialPostResponse)
def unshare_post(
    post_id: int,
    current_user: dict = Depends(require_completed_profile),
    db: Session = Depends(get_db),
) -> SocialPostResponse:
    post = SocialRepository(db).unshare_post(post_id=post_id, user_id=current_user["id"])
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return _post_response(post)


@router.get("/profile/me", response_model=SocialProfileResponse)
def get_my_social_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SocialProfileResponse:
    return get_social_profile(current_user["id"], current_user, db)


@router.get("/profile/{user_id}", response_model=SocialProfileResponse)
def get_social_profile(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SocialProfileResponse:
    repo = SocialRepository(db)
    user, stats, items = repo.get_profile(
        profile_user_id=user_id,
        viewer_id=current_user["id"],
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return SocialProfileResponse(
        user=SocialProfileUserResponse(
            id=user.id,
            user_name=user.user_name,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            address=user.address,
        ),
        is_self=user.id == current_user["id"],
        stats=SocialProfileStatsResponse(**stats),
        items=[_post_response(post) for post in items],
    )
