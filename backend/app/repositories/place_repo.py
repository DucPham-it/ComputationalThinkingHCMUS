"""Place repository for internal place data.

Use this for local metadata not fully covered by Google APIs,
for example festival schedules, custom descriptions, curated tags.
"""


class PlaceRepository:
    def get_by_id(self, place_id: int):
        """Fetch local place record by id."""
        return None

    def search_local_places(self, keyword: str = ""):
        """Search locally stored places.

        TODO:
        - useful when combining curated internal places with Google results
        """
        return []
