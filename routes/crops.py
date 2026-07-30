from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Crop
from routes.helpers import get_current_farm, parse_date

crops_bp = Blueprint("crops", __name__, url_prefix="/api/crops")


@crops_bp.get("")
@jwt_required()
def list_crops():
    farm = get_current_farm()
    if not farm:
        return jsonify([])
    crops = Crop.query.filter_by(farm_id=farm.id).order_by(Crop.created_at.desc()).all()
    return jsonify([c.to_dict() for c in crops])


@crops_bp.post("")
@jwt_required()
def create_crop():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    crop = Crop(
        farm_id=farm.id,
        name=data["name"],
        category=data.get("category"),
        stage=data.get("stage", "planted"),
        planting_date=parse_date(data.get("planting_date")),
        expected_harvest_date=parse_date(data.get("expected_harvest_date")),
        actual_harvest_date=parse_date(data.get("actual_harvest_date")),
        yield_amount=data.get("yield_amount"),
        yield_unit=data.get("yield_unit"),
        notes=data.get("notes"),
    )
    db.session.add(crop)
    db.session.commit()
    return jsonify(crop.to_dict()), 201


@crops_bp.put("/<int:crop_id>")
@jwt_required()
def update_crop(crop_id):
    farm = get_current_farm()
    crop = Crop.query.filter_by(id=crop_id, farm_id=farm.id if farm else None).first_or_404()

    data = request.get_json() or {}
    for field in ("name", "category", "stage", "yield_amount", "yield_unit", "notes"):
        if field in data:
            setattr(crop, field, data[field])
    for field in ("planting_date", "expected_harvest_date", "actual_harvest_date"):
        if field in data:
            setattr(crop, field, parse_date(data[field]))

    db.session.commit()
    return jsonify(crop.to_dict())


@crops_bp.delete("/<int:crop_id>")
@jwt_required()
def delete_crop(crop_id):
    farm = get_current_farm()
    crop = Crop.query.filter_by(id=crop_id, farm_id=farm.id if farm else None).first_or_404()
    db.session.delete(crop)
    db.session.commit()
    return jsonify({"message": "Crop deleted"})
