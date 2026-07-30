from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Expense
from routes.helpers import get_current_farm, parse_date

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")


@expenses_bp.get("")
@jwt_required()
def list_expenses():
    farm = get_current_farm()
    if not farm:
        return jsonify([])
    expenses = Expense.query.filter_by(farm_id=farm.id).order_by(Expense.date_incurred.desc()).all()
    return jsonify([e.to_dict() for e in expenses])


@expenses_bp.post("")
@jwt_required()
def create_expense():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    data = request.get_json() or {}
    if not data.get("category") or data.get("amount") is None or not data.get("date_incurred"):
        return jsonify({"error": "category, amount and date_incurred are required"}), 400

    expense = Expense(
        farm_id=farm.id,
        category=data["category"],
        description=data.get("description"),
        amount=data["amount"],
        date_incurred=parse_date(data["date_incurred"]),
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201


@expenses_bp.put("/<int:expense_id>")
@jwt_required()
def update_expense(expense_id):
    farm = get_current_farm()
    expense = Expense.query.filter_by(id=expense_id, farm_id=farm.id if farm else None).first_or_404()

    data = request.get_json() or {}
    for field in ("category", "description", "amount"):
        if field in data:
            setattr(expense, field, data[field])
    if "date_incurred" in data:
        expense.date_incurred = parse_date(data["date_incurred"])

    db.session.commit()
    return jsonify(expense.to_dict())


@expenses_bp.delete("/<int:expense_id>")
@jwt_required()
def delete_expense(expense_id):
    farm = get_current_farm()
    expense = Expense.query.filter_by(id=expense_id, farm_id=farm.id if farm else None).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"})
