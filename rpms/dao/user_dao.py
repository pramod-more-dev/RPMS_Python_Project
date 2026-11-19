
from datetime import datetime

from rpms.util.db_connection import get_connection


class UserDAO:

    def get_user_by_identifier(self, identifier):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT
                    u.user_id,
                    u.username,
                    u.password_hash,
                    u.full_name,
                    u.email,
                    u.role_id,
                    u.status,
                    r.role_code,
                    r.role_name,
                    r.is_active AS role_is_active
                FROM users u
                INNER JOIN roles r
                    ON u.role_id = r.role_id
                WHERE u.email = %s OR u.username = %s
                LIMIT 1
            """

            cursor.execute(query, (identifier, identifier))
            return cursor.fetchone()

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_last_login(self, user_id):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            query = """
                UPDATE users
                SET last_login_at = %s
                WHERE user_id = %s
            """

            cursor.execute(query, (datetime.now(), user_id))
            connection.commit()

            return cursor.rowcount > 0

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
