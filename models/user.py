from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    """
    User model class for authentication and database interactions.
    """
    def __init__(self, user_dict: dict):
        self.id = str(user_dict.get("_id"))
        self.username = user_dict.get("username")
        self.email = user_dict.get("email")
        self.password_hash = user_dict.get("password_hash")
        self.role = user_dict.get("role", "user")
        self.created_at = user_dict.get("created_at")

    def get_id(self):
        return self.id

    @staticmethod
    def find_by_id(db, user_id: str):
        try:
            user_dict = db.users.find_one({"_id": ObjectId(user_id)})
            if user_dict:
                return User(user_dict)
        except Exception:
            pass
        return None

    @staticmethod
    def find_by_email(db, email: str):
        user_dict = db.users.find_one({"email": email})
        if user_dict:
            return User(user_dict)
        return None

    @staticmethod
    def find_by_username(db, username: str):
        user_dict = db.users.find_one({"username": username})
        if user_dict:
            return User(user_dict)
        return None
