"""Security helpers.

Current state:
- contains only placeholder password hashing

TODO:
- replace with `passlib` or `bcrypt`
- add password verification helper
- add JWT access token creation and validation
"""


def hash_password(password: str) -> str:
    """Return hashed password string.

    Input:
    - password: plain text password from registration form

    Output:
    - hashed password string ready for database storage

    Warning:
    - current implementation is a placeholder only and is NOT secure.
    """
    return f"hashed::{password}"
