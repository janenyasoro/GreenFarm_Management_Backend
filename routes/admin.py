from functools import wraps
from math import isfinite
from email_validator import EmailNotValidError, validate_email

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import bcrypt, db
from models import User, Farm, Crop, Livestock, Task
from routes.helpers import get_user_id

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def normalize_role(value):
    if not isinstance(value, str):
        return None
    aliases = {"ADMIN": "ADMIN", "OWNER": "FARM_OWNER", "FARM_OWNER": "FARM_OWNER", "WORKER": "FARM_WORKER", "FARM_WORKER": "FARM_WORKER"}
    return aliases.get(value.strip().upper())


def error(message, status):
    return jsonify({"message": message, "error": message}), status


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = db.session.get(User, get_user_id())
        if not user or normalize_role(user.role) != "ADMIN" or not user.is_active:
            return error("ADMIN role is required.", 403)
        return fn(*args, **kwargs)
    return wrapper


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("A JSON object body is required.", 400)
    return data, None


def page_args():
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))
        return page, limit
    except (TypeError, ValueError):
        return None, None


def user_farm(user):
    return user.farm_id if user.role == "FARM_WORKER" else next((farm.id for farm in user.farms), None)


@admin_bp.get("/users")
@jwt_required()
@admin_required
def list_users():
    page, limit = page_args()
    if page is None:
        return error("page and limit must be integers.", 400)
    query = User.query
    role = request.args.get("role")
    search = request.args.get("search", "").strip()
    farm_id = request.args.get("farm_id")
    if role:
        normalized = normalize_role(role)
        if not normalized:
            return error("role must be ADMIN, FARM_OWNER, or FARM_WORKER.", 400)
        query = query.filter(User.role == normalized)
    if search:
        query = query.filter(db.or_(User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%")))
    if farm_id:
        try:
            farm_id = int(farm_id)
        except ValueError:
            return error("farm_id must be an integer.", 400)
        query = query.filter(db.or_(User.farm_id == farm_id, User.id.in_(db.session.query(Farm.owner_id).filter(Farm.id == farm_id))))
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    users = []
    for user in pagination.items:
        item = user.to_dict()
        item["farm_id"] = user_farm(user)
        item["role"] = normalize_role(user.role)
        users.append(item)
    return jsonify({"items": users, "users": users, "page": page, "limit": limit, "total": pagination.total, "pages": pagination.pages})


@admin_bp.post("/users")
@jwt_required()
@admin_required
def create_user():
    data, failure = json_body()
    if failure:
        return failure
    full_name = data.get("full_name", data.get("name"))
    email = data.get("email")
    if not isinstance(full_name, str) or not isinstance(email, str):
        return error("full_name and email must be strings.", 400)
    full_name = full_name.strip()
    if not full_name or len(full_name) > 120:
        return error("full_name must contain between 1 and 120 characters.", 400)
    try:
        email = validate_email(email.strip(), check_deliverability=False).normalized.lower()
    except (EmailNotValidError, TypeError):
        return error("A valid email address is required.", 400)
    if len(email) > 120:
        return error("email must be at most 120 characters.", 400)
    password = data.get("password")
    role = normalize_role(data.get("role"))
    if not isinstance(password, str) or len(password) < 6 or not role:
        return error("full_name, valid email, password (at least 6 characters), and a valid role are required.", 400)
    if User.query.filter(db.func.lower(User.email) == email).first():
        return error("A user with this email already exists.", 409)
    farm_id = data.get("farm_id")
    if farm_id is not None:
        try:
            farm_id = int(farm_id)
        except (TypeError, ValueError):
            return error("farm_id must be an integer or null.", 400)
        farm = db.session.get(Farm, farm_id)
        if not farm or not farm.is_active:
            return error("Farm not found.", 404)
    user = User(full_name=full_name, email=email, password_hash=bcrypt.generate_password_hash(password).decode("utf-8"), role=role, farm_id=None if role == "FARM_OWNER" else farm_id, is_active=True)
    db.session.add(user)
    db.session.flush()
    if role == "FARM_OWNER" and farm_id is not None:
        assigned_farm = db.session.get(Farm, farm_id)
        assigned_farm.owner_id = user.id
    db.session.commit()
    result = user.to_dict(); result["role"] = role; result["farm_id"] = user_farm(user)
    return jsonify({"user": result}), 201


@admin_bp.delete("/users/<int:user_id>")
@jwt_required()
@admin_required
def deactivate_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return error("User not found.", 404)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated.", "user": user.to_dict()})


@admin_bp.patch("/users/<int:user_id>/assign-farm")
@jwt_required()
@admin_required
def assign_farm(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return error("User not found.", 404)
    data, failure = json_body()
    if failure:
        return failure
    if "farm_id" not in data:
        return error("farm_id is required (use null to unassign).", 400)
    farm_id = data.get("farm_id")
    if farm_id is not None:
        try:
            farm_id = int(farm_id)
        except (TypeError, ValueError):
            return error("farm_id must be an integer or null.", 400)
        farm = db.session.get(Farm, farm_id)
        if not farm or not farm.is_active:
            return error("Farm not found.", 404)
    if normalize_role(user.role) == "FARM_OWNER":
        current_farms = Farm.query.filter_by(owner_id=user.id).all()
        if farm_id is None:
            for owned_farm in current_farms:
                owned_farm.owner_id = None
        else:
            farm.owner_id = user.id
        user.farm_id = None
    else:
        user.farm_id = farm_id
    db.session.commit()
    result = user.to_dict(); result["role"] = normalize_role(user.role); result["farm_id"] = user_farm(user)
    return jsonify({"user": result})


@admin_bp.patch("/users/<int:user_id>/status")
@jwt_required()
@admin_required
def set_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return error("User not found.", 404)
    data, failure = json_body()
    if failure:
        return failure
    if not isinstance(data.get("is_active"), bool):
        return error("is_active must be a boolean.", 400)
    user.is_active = data["is_active"]
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@admin_bp.get("/farms")
@jwt_required()
@admin_required
def list_farms():
    page, limit = page_args()
    if page is None:
        return error("page and limit must be integers.", 400)
    query = Farm.query
    search = request.args.get("search", "").strip()
    status = request.args.get("status")
    if search:
        query = query.filter(db.or_(Farm.name.ilike(f"%{search}%"), Farm.location.ilike(f"%{search}%")))
    if status:
        if status not in ("active", "inactive"):
            return error("status must be active or inactive.", 400)
        query = query.filter(Farm.is_active.is_(status == "active"))
    pagination = query.order_by(Farm.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)
    items = []
    for farm in pagination.items:
        item = farm.to_dict(); item["owner"] = farm.owner.to_dict() if farm.owner else None
        items.append(item)
    return jsonify({"items": items, "farms": items, "page": page, "limit": limit, "total": pagination.total, "pages": pagination.pages})


@admin_bp.post("/farms")
@jwt_required()
@admin_required
def create_farm():
    data, failure = json_body()
    if failure:
        return failure
    name = data.get("name")
    if not isinstance(name, str):
        return error("name must be a string.", 400)
    name = name.strip()
    owner_id = data.get("owner_id")
    if not name or len(name) > 120:
        return error("Farm name is required.", 400)
    owner = None
    if owner_id is not None:
        try:
            owner_id = int(owner_id)
        except (TypeError, ValueError):
            return error("owner_id must be an integer or null.", 400)
        owner = db.session.get(User, owner_id)
        if not owner or normalize_role(owner.role) != "FARM_OWNER" or not owner.is_active:
            return error("An active FARM_OWNER user is required.", 400)
    try:
        size = data.get("size", data.get("size_acres"))
        size = float(size) if size is not None else None
        if size is not None and (size < 0 or not isfinite(size)):
            raise ValueError
    except (TypeError, ValueError):
        return error("size must be a non-negative number.", 400)
    location = data.get("location")
    if location is not None and (not isinstance(location, str) or len(location) > 200):
        return error("location must be a string of at most 200 characters.", 400)
    farm = Farm(name=name, location=location, size_acres=size, owner_id=owner_id, is_active=True)
    db.session.add(farm); db.session.commit()
    return jsonify({"farm": farm.to_dict()}), 201


@admin_bp.get("/farms/<int:farm_id>")
@jwt_required()
@admin_required
def get_farm(farm_id):
    farm = db.session.get(Farm, farm_id)
    if not farm:
        return error("Farm not found.", 404)
    result = farm.to_dict(); result["owner"] = farm.owner.to_dict() if farm.owner else None
    result["workers"] = [u.to_dict() for u in User.query.filter_by(farm_id=farm.id, role="FARM_WORKER").all()]
    return jsonify({"farm": result})


@admin_bp.patch("/farms/<int:farm_id>")
@admin_bp.put("/farms/<int:farm_id>")
@jwt_required()
@admin_required
def update_farm(farm_id):
    farm = db.session.get(Farm, farm_id)
    if not farm:
        return error("Farm not found.", 404)
    data, failure = json_body()
    if failure:
        return failure
    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return error("name must be a non-empty string.", 400)
        farm.name = data["name"].strip()
    if "location" in data:
        if data["location"] is not None and (not isinstance(data["location"], str) or len(data["location"]) > 200):
            return error("location must be a string of at most 200 characters or null.", 400)
        farm.location = data["location"]
    if "size" in data or "size_acres" in data:
        try:
            size = float(data.get("size", data.get("size_acres")))
            if size < 0 or not isfinite(size): raise ValueError
            farm.size_acres = size
        except (TypeError, ValueError): return error("size must be a non-negative number.", 400)
    if "owner_id" in data:
        owner_id = data["owner_id"]
        try:
            owner_id = int(owner_id) if owner_id is not None else None
        except (TypeError, ValueError):
            return error("owner_id must be an integer or null.", 400)
        owner = db.session.get(User, owner_id) if owner_id is not None else None
        if owner_id is not None and (not owner or normalize_role(owner.role) != "FARM_OWNER" or not owner.is_active):
            return error("An active FARM_OWNER user is required.", 400)
        farm.owner_id = owner.id if owner else None
    db.session.commit()
    return jsonify({"farm": farm.to_dict()})


@admin_bp.delete("/farms/<int:farm_id>")
@jwt_required()
@admin_required
def delete_farm(farm_id):
    farm = db.session.get(Farm, farm_id)
    if not farm:
        return error("Farm not found.", 404)
    farm.is_active = False
    db.session.commit()
    return jsonify({"message": "Farm deactivated.", "farm": farm.to_dict()})


@admin_bp.get("/activity")
@jwt_required()
@admin_required
def platform_activity():
    return jsonify({"total_users": User.query.count(), "total_farms": Farm.query.filter_by(is_active=True).count(), "total_crops": Crop.query.count(), "total_livestock": Livestock.query.count(), "open_tasks": Task.query.filter(Task.status != "completed").count()})
