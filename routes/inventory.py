from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from extensions import db
from models import Inventory
from routes.helpers import get_current_farm

inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


@inventory_bp.get("")
@jwt_required()
def list_inventory():
    farm = get_current_farm()
    if not farm:
        return jsonify([])
    items = Inventory.query.filter_by(farm_id=farm.id).order_by(Inventory.item_name.asc()).all()
    return jsonify([i.to_dict() for i in items])


@inventory_bp.post("")
@jwt_required()
def create_inventory_item():
    farm = get_current_farm()
    if not farm:
        return jsonify({"error": "No farm found for this user"}), 404

    data = request.get_json() or {}
    if not data.get("item_name"):
        return jsonify({"error": "item_name is required"}), 400

    item = Inventory(
        farm_id=farm.id,
        item_name=data["item_name"],
        category=data.get("category"),
        quantity=data.get("quantity", 0),
        unit=data.get("unit"),
        reorder_level=data.get("reorder_level", 0),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@inventory_bp.put("/<int:item_id>")
@jwt_required()
def update_inventory_item(item_id):
    farm = get_current_farm()
    item = Inventory.query.filter_by(id=item_id, farm_id=farm.id if farm else None).first_or_404()

    data = request.get_json() or {}
    for field in ("item_name", "category", "quantity", "unit", "reorder_level"):
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return jsonify(item.to_dict())


@inventory_bp.delete("/<int:item_id>")
@jwt_required()
def delete_inventory_item(item_id):
    farm = get_current_farm()
    item = Inventory.query.filter_by(id=item_id, farm_id=farm.id if farm else None).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Inventory item deleted"})
