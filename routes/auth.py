# routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from extensions import db, bcrypt
from models import User
from routes.helpers import get_user_id

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get fields from request
        full_name = data.get('full_name')
        email = data.get('email')
        email = email.strip().lower() if isinstance(email, str) else email
        password = data.get('password')
        role = 'FARM_OWNER'  # Public registration cannot grant elevated roles.
        
        # Validate required fields
        if not full_name:
            return jsonify({"error": "Full name is required"}), 400
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        if User.query.filter(db.func.lower(User.email) == email).first():
            return jsonify({"error": "Email already registered"}), 400
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            role=role,
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Registration error: {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({"error": "Account is deactivated. Please contact support."}), 401
        
        # Check password
        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "access_token": access_token,
            "accessToken": access_token,
            "token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict(),
            "user_id": user.id,
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_user_id()
        print(f"👤 Getting profile for user ID: {user_id}")
        
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User not found: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        print(f"✅ User found: {user.full_name} ({user.email})")
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        print(f"❌ Profile error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({"error": "Email already in use"}), 400
            user.email = data['email']
        
        # Role changes are restricted to the admin management API.
        
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Profile update error: {str(e)}")
        return jsonify({"error": f"Update failed: {str(e)}"}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({"error": "Current password and new password are required"}), 400
        
        # Verify current password
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters"}), 400
        
        # Update password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Password change error: {str(e)}")
        return jsonify({"error": f"Password change failed: {str(e)}"}), 500


@auth_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account (soft delete)"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({"message": "Account deactivated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Deactivation error: {str(e)}")
        return jsonify({"error": f"Deactivation failed: {str(e)}"}), 500


@auth_bp.route('/activate/<int:user_id>', methods=['POST'])
@jwt_required()
def activate_account(user_id):
    """Activate a user account (admin only)"""
    try:
        # Get current user to check role
        current_user_id = get_user_id()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'ADMIN']:
            return jsonify({"error": "Admin access required"}), 403
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user.is_active = True
        db.session.commit()
        
        return jsonify({
            "message": "Account activated successfully",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Activation error: {str(e)}")
        return jsonify({"error": f"Activation failed: {str(e)}"}), 500


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all users (admin only)"""
    try:
        # Get current user to check role
        current_user_id = get_user_id()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'ADMIN']:
            return jsonify({"error": "Admin access required"}), 403
        
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
        
    except Exception as e:
        print(f"❌ List users error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Debug endpoint to check user data
@auth_bp.route('/debug/user', methods=['GET'])
@jwt_required()
def debug_user():
    """Debug endpoint to check user data"""
    try:
        user_id = get_user_id()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Return raw user data for debugging
        return jsonify({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "password_hash": user.password_hash[:20] + "..." if user.password_hash else None,
            "to_dict_result": user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        return jsonify({"error": str(e)}), 500