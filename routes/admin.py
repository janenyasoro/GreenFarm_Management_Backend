from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import User, Farm, Crop, Livestock, Task

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


@admin_bp.get("/users")
@jwt_required()
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@admin_bp.put("/users/<int:user_id>/status")
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(user.to_dict())


@admin_bp.get("/activity")
@jwt_required()
@admin_required
def platform_activity():
    return jsonify(
        {
            "total_users": User.query.count(),
            "total_farms": Farm.query.count(),
            "total_crops": Crop.query.count(),
            "total_livestock": Livestock.query.count(),
            "open_tasks": Task.query.filter(Task.status != "completed").count(),
        }
    )
