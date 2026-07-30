# routes/income.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Income
from routes.helpers import get_current_farm, get_user_id
from datetime import datetime

income_bp = Blueprint('income', __name__, url_prefix='/api/income')

@income_bp.route('', methods=['GET'])
@jwt_required()
def get_income():
    """Get all income records for the current user's farm"""
    try:
        user_id = get_user_id()
        farm = get_current_farm()
        
        if not farm:
            return jsonify([])
        
        income = Income.query.filter_by(farm_id=farm.id).order_by(Income.date_received.desc()).all()
        return jsonify([i.to_dict() for i in income]), 200
        
    except Exception as e:
        print(f"❌ Error in get_income: {str(e)}")
        return jsonify({"error": str(e)}), 500

@income_bp.route('', methods=['POST'])
@jwt_required()
def create_income():
    """Create a new income record"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        print(f"📥 Received income data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if not data.get('source'):
            return jsonify({"error": "source is required"}), 400
        
        if not data.get('amount'):
            return jsonify({"error": "amount is required"}), 400
        
        if not data.get('date_received'):
            return jsonify({"error": "date_received is required"}), 400
        
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found for this user"}), 404
        
        try:
            date_received = datetime.strptime(data['date_received'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        income = Income(
            farm_id=farm.id,
            source=data['source'],
            description=data.get('description', ''),
            amount=float(data['amount']),
            date_received=date_received
        )
        
        db.session.add(income)
        db.session.commit()
        
        print(f"✅ Income created: {income.id}")
        return jsonify(income.to_dict()), 201
        
    except Exception as e:
        print(f"❌ Error creating income: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@income_bp.route('/<int:income_id>', methods=['PUT'])
@jwt_required()
def update_income(income_id):
    """Update an income record"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        income = Income.query.filter_by(id=income_id, farm_id=farm.id).first()
        if not income:
            return jsonify({"error": "Income not found"}), 404
        
        if 'source' in data:
            income.source = data['source']
        if 'description' in data:
            income.description = data['description']
        if 'amount' in data:
            income.amount = float(data['amount'])
        if 'date_received' in data:
            try:
                income.date_received = datetime.strptime(data['date_received'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        db.session.commit()
        return jsonify(income.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error updating income: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@income_bp.route('/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    """Delete an income record"""
    try:
        user_id = get_user_id()
        farm = get_current_farm()
        
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        income = Income.query.filter_by(id=income_id, farm_id=farm.id).first()
        if not income:
            return jsonify({"error": "Income not found"}), 404
        
        db.session.delete(income)
        db.session.commit()
        
        return jsonify({"message": "Income deleted successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting income: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500