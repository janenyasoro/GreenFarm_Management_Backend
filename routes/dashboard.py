from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import Crop, Livestock, Expense, Income, Task, Inventory
from routes.helpers import get_current_farm

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/summary")
@jwt_required()
def summary():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    total_crops = Crop.query.filter_by(farm_id=farm.id).count()
    active_livestock = Livestock.query.filter_by(farm_id=farm.id, status="active").count()
    pending_tasks = Task.query.filter_by(farm_id=farm.id, status="pending").count()

    total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter_by(
        farm_id=farm.id
    ).scalar()
    total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter_by(
        farm_id=farm.id
    ).scalar()

    low_stock_items = Inventory.query.filter_by(farm_id=farm.id).filter(
        Inventory.quantity <= Inventory.reorder_level
    ).count()

    return jsonify(
        {
            "farm_name": farm.name,
            "total_crops": total_crops,
            "active_livestock": active_livestock,
            "pending_tasks": pending_tasks,
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "profit_loss": float(total_income) - float(total_expenses),
            "low_stock_items": low_stock_items,
        }
    )


@dashboard_bp.get("/crop-yields")
@jwt_required()
def crop_yields():
    farm = get_current_farm()
    if not farm:
        return jsonify([])

    crops = Crop.query.filter_by(farm_id=farm.id).filter(Crop.yield_amount.isnot(None)).all()
    return jsonify(
        [
            {
                "crop_name": c.name,
                "stage": c.stage,
                "yield_amount": c.yield_amount,
                "yield_unit": c.yield_unit,
                "harvest_date": c.actual_harvest_date.isoformat() if c.actual_harvest_date else None,
            }
            for c in crops
        ]
    )


@dashboard_bp.get("/finance-by-category")
@jwt_required()
def finance_by_category():
    farm = get_current_farm()
    if not farm:
        return jsonify({"expenses": [], "income": []})

    expense_rows = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter_by(farm_id=farm.id)
        .group_by(Expense.category)
        .all()
    )
    income_rows = (
        db.session.query(Income.source, func.sum(Income.amount))
        .filter_by(farm_id=farm.id)
        .group_by(Income.source)
        .all()
    )

    return jsonify(
        {
            "expenses": [{"category": c, "total": float(t)} for c, t in expense_rows],
            "income": [{"source": s, "total": float(t)} for s, t in income_rows],
        }
    )
