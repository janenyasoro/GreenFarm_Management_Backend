# routes/inventory.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Inventory
from routes.helpers import get_current_farm, get_user_id

inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')

@inventory_bp.route('', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get all inventory items for the current user's farm"""
    try:
        user_id = get_user_id()
        farm = get_current_farm()
        
        if not farm:
            return jsonify([])
        
        items = Inventory.query.filter_by(farm_id=farm.id).all()
        return jsonify([i.to_dict() for i in items]), 200
        
    except Exception as e:
        print(f"❌ Error in get_inventory: {str(e)}")
        return jsonify({"error": str(e)}), 500

@inventory_bp.route('', methods=['POST'])
@jwt_required()
def create_inventory():
    """Create a new inventory item"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        print(f"📥 Received inventory data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if not data.get('item_name'):
            return jsonify({"error": "item_name is required"}), 400
        
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found for this user"}), 404
        
        inventory = Inventory(
            farm_id=farm.id,
            item_name=data['item_name'],
            category=data.get('category'),
            quantity=float(data.get('quantity', 0)),
            unit=data.get('unit'),
            reorder_level=float(data.get('reorder_level', 0))
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        print(f"✅ Inventory created: {inventory.id}")
        return jsonify(inventory.to_dict()), 201
        
    except Exception as e:
        print(f"❌ Error creating inventory: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory(item_id):
    """Update an inventory item"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        item = Inventory.query.filter_by(id=item_id, farm_id=farm.id).first()
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404
        
        if 'item_name' in data:
            item.item_name = data['item_name']
        if 'category' in data:
            item.category = data['category']
        if 'quantity' in data:
            item.quantity = float(data['quantity'])
        if 'unit' in data:
            item.unit = data['unit']
        if 'reorder_level' in data:
            item.reorder_level = float(data['reorder_level'])
        
        db.session.commit()
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error updating inventory: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory(item_id):
    """Delete an inventory item"""
    try:
        user_id = get_user_id()
        farm = get_current_farm()
        
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        item = Inventory.query.filter_by(id=item_id, farm_id=farm.id).first()
        if not item:
            return jsonify({"error": "Inventory item not found"}), 404
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({"message": "Inventory item deleted successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting inventory: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500