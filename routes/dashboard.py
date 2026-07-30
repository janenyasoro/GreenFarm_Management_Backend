from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Task, User
from routes.helpers import get_current_farm

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("")
@jwt_required()
def get_dashboard():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    today = date.today()
    upcoming_threshold = today + timedelta(days=7)

    farm_tasks = Task.query.filter_by(farm_id=farm.id)

    total = farm_tasks.count()
    pending = farm_tasks.filter(Task.status == "pending").count()
    in_progress = farm_tasks.filter(Task.status == "in_progress").count()
    completed = farm_tasks.filter(Task.status == "completed").count()
    overdue = farm_tasks.filter(
        Task.due_date < today,
        Task.status != "completed",
    ).count()

    upcoming_tasks = farm_tasks.filter(
        Task.due_date.between(today, upcoming_threshold),
        Task.status != "completed",
    ).order_by(Task.due_date).limit(5).all()

    recent_tasks = farm_tasks.order_by(Task.created_at.desc()).limit(5).all()

    # Livestock count — graceful fallback until teammates merge their models
    livestock_count = 0
    try:
        from models import Livestock
        livestock_count = Livestock.query.filter_by(farm_id=farm.id).count()
    except Exception:
        pass

    # Finance totals — graceful fallback
    total_income = 0
    total_expenses = 0
    try:
        from sqlalchemy import func
        from models import Income, Expense
        from extensions import db
        total_income = db.session.query(func.sum(Income.amount)).filter_by(farm_id=farm.id).scalar() or 0
        total_expenses = db.session.query(func.sum(Expense.amount)).filter_by(farm_id=farm.id).scalar() or 0
    except Exception:
        pass

    user = User.query.get(int(get_jwt_identity()))

    return jsonify({
        "farm": farm.to_dict(),
        "user": user.to_dict() if user else None,
        "tasks": {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue,
            "upcoming": [t.to_dict() for t in upcoming_tasks],
        },
        "livestock_count": livestock_count,
        "finances": {
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net": float(total_income) - float(total_expenses),
        },
        "recent_tasks": [t.to_dict() for t in recent_tasks],
    })
