from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Income
from routes.helpers import get_current_farm, parse_date

income_bp = Blueprint("income", __name__, url_prefix="/api/income")


@income_bp.get("")
@jwt_required()
def list_income():
    farm = get_current_farm()
    if not farm:
        return jsonify([])
    records = Income.query.filter_by(farm_id=farm.id).order_by(Income.date_received.desc()).all()
    return jsonify([r.to_dict() for r in records])


@income_bp.post("")
@jwt_required()
def create_income():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    data = request.get_json() or {}
    if not data.get("source") or data.get("amount") is None or not data.get("date_received"):
        return jsonify({"error": "source, amount and date_received are required"}), 400

    record = Income(
        farm_id=farm.id,
        source=data["source"],
        description=data.get("description"),
        amount=data["amount"],
        date_received=parse_date(data["date_received"]),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@income_bp.put("/<int:income_id>")
@jwt_required()
def update_income(income_id):
    farm = get_current_farm()
    record = Income.query.filter_by(id=income_id, farm_id=farm.id if farm else None).first_or_404()

    data = request.get_json() or {}
    for field in ("source", "description", "amount"):
        if field in data:
            setattr(record, field, data[field])
    if "date_received" in data:
        record.date_received = parse_date(data["date_received"])

    db.session.commit()
    return jsonify(record.to_dict())


@income_bp.delete("/<int:income_id>")
@jwt_required()
def delete_income(income_id):
    farm = get_current_farm()
    record = Income.query.filter_by(id=income_id, farm_id=farm.id if farm else None).first_or_404()
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Income record deleted"})
