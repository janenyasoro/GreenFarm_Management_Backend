from datetime import datetime

from flask_jwt_extended import get_jwt_identity

from models import Farm


def get_current_farm():
    user_id = get_jwt_identity()
    return Farm.query.filter_by(owner_id=int(user_id)).first()


def parse_date(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None
