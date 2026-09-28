"""Create the initial admin account from ADMIN_* environment variables."""
import os

from app import create_app
from extensions import bcrypt, db
from models import User


def seed_admin():
    email = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD")
    name = (os.environ.get("ADMIN_NAME") or "").strip()
    if not email or not password or not name:
        raise RuntimeError("ADMIN_EMAIL, ADMIN_PASSWORD, and ADMIN_NAME must all be set.")
    if len(password) < 12:
        raise RuntimeError("ADMIN_PASSWORD must contain at least 12 characters.")

    app = create_app()
    with app.app_context():
        db.create_all()
        user = User.query.filter(db.func.lower(User.email) == email).first()
        if user:
            if user.role not in ("ADMIN", "admin"):
                raise RuntimeError("ADMIN_EMAIL already belongs to a non-admin account.")
            print("Admin account already exists; no changes made.")
            return
        user = User(full_name=name, email=email, password_hash=bcrypt.generate_password_hash(password).decode("utf-8"), role="ADMIN", is_active=True)
        db.session.add(user)
        db.session.commit()
        print(f"Created admin account for {email}.")


if __name__ == "__main__":
    from extensions import db
    seed_admin()
