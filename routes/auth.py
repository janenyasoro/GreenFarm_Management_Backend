from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db, bcrypt
from models import User, Farm

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    farm_name = data.get("farm_name", "My Farm")

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(full_name=full_name, email=email, password_hash=password_hash, role="owner")
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    farm = Farm(name=farm_name, owner_id=user.id)
    db.session.add(farm)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict(), "farm": farm.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password or ""):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "This account has been deactivated"}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    farm = Farm.query.filter_by(owner_id=user.id).first()
    return jsonify({"user": user.to_dict(), "farm": farm.to_dict() if farm else None})
