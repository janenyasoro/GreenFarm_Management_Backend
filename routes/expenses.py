# routes/expenses.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models import Expense
from routes.helpers import get_current_farm, get_user_id
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')


def parse_date(date_str):
    """
    Parse date string in various formats.
    Supports: YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY, DD/MM/YYYY
    """
    if not date_str:
        return None
    
    # If it's already a date object
    if isinstance(date_str, datetime):
        return date_str.date()
    
    # If it's already a date object from SQLAlchemy
    if hasattr(date_str, 'strftime'):
        return date_str
    
    # List of possible date formats to try
    date_formats = [
        '%Y-%m-%d',     # 2026-07-29
        '%m/%d/%Y',     # 07/29/2026
        '%m-%d-%Y',     # 07-29-2026
        '%d/%m/%Y',     # 29/07/2026
        '%d-%m-%Y',     # 29-07-2026
        '%Y/%m/%d',     # 2026/07/29
        '%b %d, %Y',    # Jul 29, 2026
        '%B %d, %Y',    # July 29, 2026
        '%d %b %Y',     # 29 Jul 2026
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    
    # If all formats fail, raise an error
    raise ValueError(f"Invalid date format: {date_str}. Please use YYYY-MM-DD format.")


@expenses_bp.route('', methods=['GET'])
@jwt_required()
def get_expenses():
    """Get all expenses for the current user's farm"""
    try:
        user_id = get_user_id()
        print(f"👤 Getting expenses for user ID: {user_id}")
        
        # Get user's farm
        farm = get_current_farm()
        
        if not farm:
            print(f"❌ No farm found for user: {user_id}")
            return jsonify([])
        
        print(f"🏠 Farm found: {farm.id} - {farm.name}")
        
        # Get expenses
        expenses = Expense.query.filter_by(farm_id=farm.id).order_by(Expense.date_incurred.desc()).all()
        print(f"📊 Found {len(expenses)} expenses")
        
        return jsonify([e.to_dict() for e in expenses]), 200
        
    except Exception as e:
        print(f"❌ Error in get_expenses: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@expenses_bp.route('', methods=['POST'])
@jwt_required()
def create_expense():
    """Create a new expense record"""
    try:
        user_id = get_user_id()
        print(f"👤 Creating expense for user ID: {user_id}")
        
        # Get the request data
        data = request.get_json()
        print(f"📥 Received data: {data}")
        
        # Check if data exists
        if not data:
            print("❌ No data provided")
            return jsonify({"error": "No data provided"}), 400
        
        # Get required fields with better error messages
        category = data.get('category')
        amount = data.get('amount')
        date_incurred = data.get('date_incurred')
        
        print(f"📋 Category: {category}, Amount: {amount}, Date: {date_incurred}")
        
        # Validate required fields
        if not category:
            print("❌ Missing category")
            return jsonify({"error": "category is required"}), 400
        
        if not amount:
            print("❌ Missing amount")
            return jsonify({"error": "amount is required"}), 400
        
        if not date_incurred:
            print("❌ Missing date_incurred")
            return jsonify({"error": "date_incurred is required"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            print(f"❌ No farm found for user: {user_id}")
            return jsonify({"error": "No farm found for this user. Please create a farm first."}), 404
        
        print(f"🏠 Using farm ID: {farm.id}")
        
        # Parse amount - handle both string and number
        try:
            if isinstance(amount, (int, float)):
                amount_value = float(amount)
            else:
                amount_value = float(str(amount).replace(',', ''))
        except (ValueError, TypeError):
            print(f"❌ Invalid amount: {amount}")
            return jsonify({"error": f"Invalid amount: {amount}. Please enter a valid number."}), 400
        
        # Parse date with flexible format
        try:
            date_parsed = parse_date(date_incurred)
            if not date_parsed:
                return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
        except ValueError as e:
            print(f"❌ Date parsing error: {str(e)}")
            return jsonify({"error": str(e)}), 400
        
        # Get description (optional)
        description = data.get('description', '')
        if description is None:
            description = ''
        
        # Create expense
        expense = Expense(
            farm_id=farm.id,
            category=category,
            description=description,
            amount=amount_value,
            date_incurred=date_parsed
        )
        
        db.session.add(expense)
        db.session.commit()
        
        print(f"✅ Expense created successfully! ID: {expense.id}")
        
        return jsonify(expense.to_dict()), 201
        
    except Exception as e:
        print(f"❌ Error creating expense: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Failed to create expense: {str(e)}"}), 500


@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """Update an expense record"""
    try:
        user_id = get_user_id()
        print(f"📝 Updating expense {expense_id} for user: {user_id}")
        
        data = request.get_json()
        print(f"📥 Update data: {data}")
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Find the expense
        expense = Expense.query.filter_by(id=expense_id, farm_id=farm.id).first()
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        
        # Update fields
        if 'category' in data:
            expense.category = data['category']
        
        if 'description' in data:
            expense.description = data['description'] if data['description'] else ''
        
        if 'amount' in data:
            try:
                if isinstance(data['amount'], (int, float)):
                    expense.amount = float(data['amount'])
                else:
                    expense.amount = float(str(data['amount']).replace(',', ''))
            except (ValueError, TypeError):
                return jsonify({"error": f"Invalid amount: {data['amount']}"}), 400
        
        if 'date_incurred' in data:
            try:
                expense.date_incurred = parse_date(data['date_incurred'])
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        
        db.session.commit()
        
        print(f"✅ Expense {expense_id} updated successfully")
        return jsonify(expense.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Error updating expense: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Failed to update expense: {str(e)}"}), 500


@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """Delete an expense record"""
    try:
        user_id = get_user_id()
        print(f"🗑️ Deleting expense {expense_id} for user: {user_id}")
        
        # Get user's farm
        farm = get_current_farm()
        if not farm:
            return jsonify({"error": "No farm found"}), 404
        
        # Find the expense
        expense = Expense.query.filter_by(id=expense_id, farm_id=farm.id).first()
        if not expense:
            return jsonify({"error": "Expense not found"}), 404
        
        db.session.delete(expense)
        db.session.commit()
        
        print(f"✅ Expense {expense_id} deleted successfully")
        return jsonify({"message": "Expense deleted successfully"}), 200
        
    except Exception as e:
        print(f"❌ Error deleting expense: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Failed to delete expense: {str(e)}"}), 500


# Debug endpoint to check what's happening
@expenses_bp.route('/debug', methods=['GET'])
@jwt_required()
def debug_expenses():
    """Debug endpoint to check farm and expenses"""
    try:
        user_id = get_user_id()
        print(f"🔍 Debug for user: {user_id}")
        
        # Check user
        from models import User
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check farm
        farm = get_current_farm()
        
        response = {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            },
            "farm_exists": bool(farm),
        }
        
        if farm:
            expenses_count = Expense.query.filter_by(farm_id=farm.id).count()
            response.update({
                "farm": {
                    "id": farm.id,
                    "name": farm.name,
                    "location": farm.location,
                    "size_acres": farm.size_acres
                },
                "expenses_count": expenses_count,
                "expenses": [e.to_dict() for e in Expense.query.filter_by(farm_id=farm.id).all()]
            })
        else:
            response["message"] = "No farm found for this user. Please create a farm first."
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500