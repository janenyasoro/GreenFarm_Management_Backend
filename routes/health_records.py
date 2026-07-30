from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import HealthRecord, Livestock
from .helpers import get_current_farm, parse_date
from datetime import datetime

health_bp = Blueprint("health", __name__, url_prefix="/api/health")


def _verify_animal_ownership(livestock_id):
    farm = get_current_farm()
    if not farm:
        return None
    return Livestock.query.filter_by(id=livestock_id, farm_id=farm.id).first()


@health_bp.get("/livestock/<int:livestock_id>/health-records")
@jwt_required()
def list_health_records(livestock_id):
    animal = _verify_animal_ownership(livestock_id)
    if not animal:
        return jsonify({"error": "Livestock not found"}), 404
    records = HealthRecord.query.filter_by(livestock_id=animal.id).order_by(
        HealthRecord.date_administered.desc()
    ).all()
    return jsonify([r.to_dict() for r in records])


@health_bp.post("/livestock/<int:livestock_id>/health-records")
@jwt_required()
def create_health_record(livestock_id):
    animal = _verify_animal_ownership(livestock_id)
    if not animal:
        return jsonify({"error": "Livestock not found"}), 404

    data = request.get_json() or {}
    if not data.get("record_type") or not data.get("date_administered"):
        return jsonify({"error": "record_type and date_administered are required"}), 400

    record = HealthRecord(
        livestock_id=animal.id,
        record_type=data["record_type"],
        description=data.get("description"),
        date_administered=parse_date(data["date_administered"]),
        next_due_date=parse_date(data.get("next_due_date")),
        veterinarian=data.get("veterinarian"),
        notes=data.get("notes"),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@health_bp.put("/health-records/<int:record_id>")
@jwt_required()
def update_health_record(record_id):
    farm = get_current_farm()
    record = HealthRecord.query.get_or_404(record_id)
    animal = Livestock.query.filter_by(id=record.livestock_id, farm_id=farm.id if farm else None).first()
    if not animal:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json() or {}
    for field in ("record_type", "description", "veterinarian", "notes"):
        if field in data:
            setattr(record, field, data[field])
    if "date_administered" in data:
        record.date_administered = parse_date(data["date_administered"])
    if "next_due_date" in data:
        record.next_due_date = parse_date(data["next_due_date"])

    db.session.commit()
    return jsonify(record.to_dict())


@health_bp.delete("/health-records/<int:record_id>")
@jwt_required()
def delete_health_record(record_id):
    farm = get_current_farm()
    record = HealthRecord.query.get_or_404(record_id)
    animal = Livestock.query.filter_by(id=record.livestock_id, farm_id=farm.id if farm else None).first()
    if not animal:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Health record deleted"})
