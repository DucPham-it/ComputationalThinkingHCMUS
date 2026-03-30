"""Review repository."""


class ReviewRepository:
    def list_by_place(self, place_id: int):
        """Return all reviews for a place."""
        return []

    def create_review(self, user_id: int, place_id: int, content: str, rating: int):
        """Insert review and return created review.

        TODO:
        - update cached average rating if you store it internally
        - auto-add favorite when rating == 5 if desired
        """
        return None
