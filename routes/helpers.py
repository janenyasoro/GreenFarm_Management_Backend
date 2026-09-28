from flask_jwt_extended import get_jwt_identity
from flask import request
from extensions import db
from models import Farm, User


def get_user_id():
    """
    Get the current user ID from JWT identity as an integer.
    Handles both string and integer identity values.
    """
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return None


def get_current_farm():
    """Return the Farm belonging to the currently authenticated user, creating one if needed."""
    user_id = get_user_id()
    if not user_id:
        return None

    user = User.query.get(user_id)
    if not user:
        return None
    role = {"admin": "ADMIN", "owner": "FARM_OWNER", "worker": "FARM_WORKER"}.get(user.role, user.role)
    requested_farm_id = request.args.get("farm_id")
    if role == "ADMIN" and requested_farm_id:
        try:
            return Farm.query.filter_by(id=int(requested_farm_id), is_active=True).first()
        except (TypeError, ValueError):
            return None
    if role == "FARM_WORKER" and user.farm_id:
        return Farm.query.filter_by(id=user.farm_id, is_active=True).first()
    farm = Farm.query.filter_by(owner_id=user_id, is_active=True).first()
    if farm:
        return farm

    if role in ("ADMIN", "FARM_WORKER"):
        return None

    farm = Farm(
        name=f"{user.full_name}'s Farm",
        location="",
        size_acres=0,
        owner_id=user.id,
    )
    db.session.add(farm)
    db.session.commit()
    return farm


def parse_date(value):
    """Parse an ISO date string (YYYY-MM-DD) into a date object, or return None."""
    from datetime import datetime

    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
