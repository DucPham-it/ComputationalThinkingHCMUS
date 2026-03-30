"""Internal user model.

Represents a user record retrieved from the database.
"""

from dataclasses import dataclass


@dataclass
class User:
    """User entity.

    Fields:
    - id: internal user identifier
    - email: account email used for login
    - password_hash: hashed password stored in database
    """

    id: int
    email: str
    password_hash: str
