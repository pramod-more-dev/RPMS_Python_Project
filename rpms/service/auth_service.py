
from werkzeug.security import check_password_hash

from rpms.dao.user_dao import UserDAO


class AuthService:

    def __init__(self):
        self.user_dao = UserDAO()

    def authenticate(self, identifier, password):
        if not identifier or not password:
            return None

        user = self.user_dao.get_user_by_identifier(
            identifier.strip()
        )

        if not user:
            return None

        if user["status"] != "ACTIVE":
            return None

        if not user["role_is_active"]:
            return None

        try:
            password_valid = check_password_hash(
                user["password_hash"],
                password
            )
        except (ValueError, TypeError):
            password_valid = False

        if not password_valid:
            return None

        self.user_dao.update_last_login(user["user_id"])

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role_id": user["role_id"],
            "role_code": user["role_code"],
            "role_name": user["role_name"]
        }
