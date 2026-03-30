"""SQL Server connection string builder.

Input:
- database host, port, database name, username, password from settings

Output:
- ODBC connection string for SQL Server

TODO:
- add a helper that returns a live pyodbc connection
- handle connection errors with clear logs
"""

from app.core.config import settings



def build_connection_string() -> str:
    """Build SQL Server ODBC connection string.

    Output:
    - connection string usable by pyodbc / sqlalchemy+pyodbc
    """
    return (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={settings.db_host},{settings.db_port};"
        f"DATABASE={settings.db_name};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
        "TrustServerCertificate=yes;"
    )
