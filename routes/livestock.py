# routes/livestock.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Livestock, Farm
from .helpers import get_user_id, get_current_farm, parse_date  # Import helper functions
from datetime import datetime

livestock_bp = Blueprint('livestock', __name__, url_prefix='/api/livestock')

@livestock_bp.route('', methods=['GET'])
@jwt_required()
def get_livestock():
    """Get all livestock for the current user's farm"""
    try:
        user_id = get_user_id()  # Use helper function
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
            
        print(f"👤 User ID: {user_id}")
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            print("❌ No farm found for user")
            return jsonify([])  # Return empty list instead of error
        
        print(f"🏠 Farm ID: {farm.id}")
        
        livestock = Livestock.query.filter_by(farm_id=farm.id).all()
        print(f"🐄 Found {len(livestock)} livestock records")
        
        return jsonify([item.to_dict() for item in livestock]), 200
        
    except Exception as e:
        print(f"❌ Error in get_livestock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('', methods=['POST'])
@jwt_required()
def create_livestock():
    """Create a new livestock record"""
    try:
        user_id = get_user_id()  # Use helper function
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
            
        print(f"👤 Creating livestock for user: {user_id}")
        
        data = request.get_json()
        print(f"📥 Received data: {data}")
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check for either animal_type or type field (support both)
        animal_type = data.get('animal_type') or data.get('type')
        if not animal_type:
            return jsonify({"error": "animal_type or type is required"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            print("❌ No farm found for user")
            return jsonify({"error": "No farm found for this user. Please create a farm first."}), 404
        
        print(f"🏠 Using farm ID: {farm.id}")
        
        # Parse birth date using helper
        birth_date = parse_date(data.get('birth_date'))
        
        # Create livestock record
        livestock = Livestock(
            farm_id=farm.id,
            tag_number=data.get('tag_number', ''),
            animal_type=animal_type,
            breed=data.get('breed', ''),
            birth_date=birth_date,
            gender=data.get('gender', ''),
            status=data.get('status', 'active'),
            notes=data.get('notes', '')
        )
        
        db.session.add(livestock)
        db.session.commit()
        
        print(f"✅ Livestock created with ID: {livestock.id}")
        
        return jsonify(livestock.to_dict()), 201
        
    except Exception as e:
        print(f"❌ Error creating livestock: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('/<int:livestock_id>', methods=['GET'])
@jwt_required()
def get_livestock_by_id(livestock_id):
    """Get a specific livestock record"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Find the livestock
        livestock = Livestock.query.filter_by(id=livestock_id, farm_id=farm.id).first()
        if not livestock:
            return jsonify({"error": "Livestock not found"}), 404
        
        return jsonify(livestock.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error getting livestock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('/<int:livestock_id>', methods=['PUT'])
@jwt_required()
def update_livestock(livestock_id):
    """Update a livestock record"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Find the livestock
        livestock = Livestock.query.filter_by(id=livestock_id, farm_id=farm.id).first()
        if not livestock:
            return jsonify({"error": "Livestock not found"}), 404
        
        # Update fields
        allowed_fields = ['tag_number', 'animal_type', 'breed', 'gender', 'status', 'notes']
        for field in allowed_fields:
            if field in data:
                setattr(livestock, field, data[field])
        
        # Handle birth_date separately with helper
        if 'birth_date' in data:
            birth_date = parse_date(data['birth_date'])
            if birth_date:
                livestock.birth_date = birth_date
            elif data['birth_date'] is not None:
                return jsonify({"error": "Invalid birth_date format. Use YYYY-MM-DD"}), 400
        
        db.session.commit()
        
        return jsonify(livestock.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error updating livestock: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('/<int:livestock_id>', methods=['DELETE'])
@jwt_required()
def delete_livestock(livestock_id):
    """Delete a livestock record"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Find the livestock
        livestock = Livestock.query.filter_by(id=livestock_id, farm_id=farm.id).first()
        if not livestock:
            return jsonify({"error": "Livestock not found"}), 404
        
        db.session.delete(livestock)
        db.session.commit()
        
        return jsonify({"message": "Livestock deleted successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting livestock: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_livestock_summary():
    """Get summary statistics for livestock"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Invalid user identity"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Get total count
        total = Livestock.query.filter_by(farm_id=farm.id).count()
        
        # Get count by type
        from sqlalchemy import func
        by_type = db.session.query(
            Livestock.animal_type,
            func.count(Livestock.id).label('count')
        ).filter_by(farm_id=farm.id).group_by(Livestock.animal_type).all()
        
        # Get count by status
        by_status = db.session.query(
            Livestock.status,
            func.count(Livestock.id).label('count')
        ).filter_by(farm_id=farm.id).group_by(Livestock.status).all()
        
        return jsonify({
            "total": total,
            "by_type": [{"type": item[0], "count": item[1]} for item in by_type],
            "by_status": [{"status": item[0], "count": item[1]} for item in by_status]
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting livestock summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@livestock_bp.route('/debug', methods=['GET'])
@jwt_required()
def debug_livestock():
    """Debug endpoint to check what's happening"""
    try:
        user_id = get_user_id()
        print(f"🔍 Debug - User ID: {user_id}")
        
        # Check if user exists
        from models import User
        user = User.query.get(user_id) if user_id else None
        if user:
            print(f"👤 User found: {user.full_name} ({user.email})")
        else:
            print("❌ User not found!")
        
        # Check if farm exists
        farm = get_current_farm() if user_id else None
        if farm:
            print(f"🏠 Farm found: {farm.name} (ID: {farm.id})")
        else:
            print("❌ No farm found for this user!")
            
        # Get all livestock for debugging
        livestock_count = 0
        if farm:
            livestock_count = Livestock.query.filter_by(farm_id=farm.id).count()
            print(f"🐄 Found {livestock_count} livestock records")
        else:
            print("⚠️ Cannot fetch livestock - no farm")
        
        return jsonify({
            "user_id": user_id,
            "user_exists": bool(user),
            "farm_exists": bool(farm),
            "farm_id": farm.id if farm else None,
            "livestock_count": livestock_count
        }), 200
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        return jsonify({"error": str(e)}), 500