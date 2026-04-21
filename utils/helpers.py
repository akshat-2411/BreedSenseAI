import os
import json
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if a filename has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )


def save_upload(file, upload_folder: str) -> str:
    """Save an uploaded file and return the saved path."""
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath


def load_breed_info() -> dict:
    """Load breed information from the JSON file."""
    file_path = "breed_info.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Access Denied: Administrator privileges required.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function
