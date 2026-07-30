from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Task
from routes.helpers import get_current_farm, parse_date

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.get("")
@jwt_required()
def list_tasks():
    farm = get_current_farm()
    if not farm:
        return jsonify([])
    tasks = Task.query.filter_by(farm_id=farm.id).order_by(Task.due_date.asc()).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.post("")
@jwt_required()
def create_task():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    data = request.get_json() or {}
    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    task = Task(
        farm_id=farm.id,
        title=data["title"],
        description=data.get("description"),
        due_date=parse_date(data.get("due_date")),
        status=data.get("status", "pending"),
        priority=data.get("priority", "medium"),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.put("/<int:task_id>")
@jwt_required()
def update_task(task_id):
    farm = get_current_farm()
    task = Task.query.filter_by(id=task_id, farm_id=farm.id if farm else None).first_or_404()

    data = request.get_json() or {}
    for field in ("title", "description", "status", "priority"):
        if field in data:
            setattr(task, field, data[field])
    if "due_date" in data:
        task.due_date = parse_date(data["due_date"])

    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.delete("/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    farm = get_current_farm()
    task = Task.query.filter_by(id=task_id, farm_id=farm.id if farm else None).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})
