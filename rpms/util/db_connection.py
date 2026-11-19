
import os

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.environ.get("RPMS_DB_HOST", "localhost"),
    "port": int(os.environ.get("RPMS_DB_PORT", "3306")),
    "user": os.environ.get("RPMS_DB_USER", "root"),
    "password": os.environ.get("RPMS_DB_PASSWORD", ""),
    "database": os.environ.get("RPMS_DB_NAME", "recruitment_portal")
}


def get_connection():
    try:
        if not DB_CONFIG["password"]:
            raise RuntimeError(
                "Database password is not configured. "
                "Set the RPMS_DB_PASSWORD environment variable."
            )

        return mysql.connector.connect(**DB_CONFIG)

    except Error as exc:
        raise RuntimeError(
            f"Database connection failed: {exc}"
        ) from exc
