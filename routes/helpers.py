from flask_jwt_extended import get_jwt_identity
from models import Farm


def get_current_farm():
    """Return the Farm belonging to the currently authenticated user, or None."""
    user_id = get_jwt_identity()
    return Farm.query.filter_by(owner_id=user_id).first()


def parse_date(value):
    """Parse an ISO date string (YYYY-MM-DD) into a date object, or return None."""
    from datetime import datetime

    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
