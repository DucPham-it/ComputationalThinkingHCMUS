"""User repository.

Repository layer only talks to database.
It should not contain HTTP-specific logic.
"""


class UserRepository:
    def get_by_id(self, user_id: int):
        """Fetch user by id.

        Input:
        - user_id: internal user identifier

        Output:
        - user record or None

        TODO:
        - query SQL Server users table
        - map row to `User` model
        """
        return None

    def get_by_email(self, email: str):
        """Fetch user by email for login/registration checks."""
        return None

    def create_user(self, email: str, password_hash: str):
        """Insert new user into database and return created record.

        TODO:
        - enforce unique email
        - optionally create profile/preferences row
        """
        return None
