"""Internal user model.

Represents a user record retrieved from the database.
"""

from dataclasses import dataclass


@dataclass
class User:
    """User entity.

    Fields:
    - id: internal user identifier
    - user_name: display name derived from registration input or email
    - email: account email used for login
    - password_hash: hashed password stored in database
    """

    id: int
    user_name: str
    email: str
    password_hash: str
