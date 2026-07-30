"""
Authentication and user management routes for GreenHarvest Farm Management System.
Converted from Django REST Framework views to Flask routes.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt, unset_jwt_cookies, set_access_cookies,
    set_refresh_cookies
)
from models import User
from extensions import db
from routes.helpers import get_current_user
from validators import (
    validate_password_strength, validate_email_format,
    validate_username, validate_phone_number
)
from app import revoked_tokens


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


# =============================================================================
# Authentication Endpoints
# =============================================================================

@auth_bp.route("/auth/register/", methods=["POST"])
def register():
    """
    Register a new user account.

    POST /api/auth/register/

    Request Body:
        username (str, required): 3-30 chars, alphanumeric + underscores
        email (str, required): Valid email format
        password (str, required): 8+ chars, uppercase, lowercase, number, special char
        confirm_password (str, required): Must match password
        first_name (str, required)
        last_name (str, required)
        phone_number (str, optional): International format

    Returns:
        201: Registration successful with user data
        400: Validation errors
    """
    data = request.get_json() or {}
    errors = {}

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            errors[field] = ["This field is required."]

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400

    # Validate username
    is_valid, msg = validate_username(data['username'])
    if not is_valid:
        errors['username'] = [msg]

    # Validate email
    is_valid, msg = validate_email_format(data['email'])
    if not is_valid:
        errors['email'] = [msg]

    # Validate password
    is_valid, msg = validate_password_strength(data['password'])
    if not is_valid:
        errors['password'] = [msg]

    # Validate password confirmation
    if data['password'] != data['confirm_password']:
        errors['password'] = ["Passwords do not match."]

    # Validate phone number if provided
    if data.get('phone_number'):
        is_valid, msg = validate_phone_number(data['phone_number'])
        if not is_valid:
            errors['phone_number'] = [msg]

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400

    # Check for duplicate username
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'success': False,
            'errors': {
                'username': ["A user with that username already exists."]
            }
        }), 400

    # Check for duplicate email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'success': False,
            'errors': {
                'email': ["This email is already in use."]
            }
        }), 400

    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data.get('phone_number'),
        role=User.Role.OWNER,
        is_active=True,
        is_staff=False,
        date_joined=datetime.utcnow()
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Registration successful.',
        'user': user.to_dict()
    }), 201


@auth_bp.route("/auth/login/", methods=["POST"])
def login():
    """
    Authenticate user and receive JWT tokens.

    POST /api/auth/login/

    Request Body:
        username (str, required): Username or email
        password (str, required)

    Returns:
        200: Access and refresh tokens with user info
        401: Invalid credentials
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'success': False,
            'detail': 'Invalid credentials.'
        }), 401

    # Try to find user by username or email
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first()

    if not user:
        return jsonify({
            'success': False,
            'detail': 'Invalid credentials.'
        }), 401

    if not user.check_password(password):
        return jsonify({
            'success': False,
            'detail': 'Invalid credentials.'
        }), 401

    if not user.is_active:
        return jsonify({
            'success': False,
            'detail': 'This account has been deactivated.'
        }), 401

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate tokens (use string identity for JWT)
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'refresh': refresh_token,
        'access': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    }), 200


@auth_bp.route("/auth/token/refresh/", methods=["POST"])
def token_refresh():
    """
    Get a new access token using a refresh token.

    POST /api/auth/token/refresh/

    Request Body:
        refresh (str, required): Refresh token

    Returns:
        200: New access token
        401: Invalid or expired refresh token
    """
    data = request.get_json() or {}
    refresh_token = data.get('refresh')

    if not refresh_token:
        return jsonify({
            'success': False,
            'detail': 'Token is invalid or expired'
        }), 401

    try:
        # Verify the refresh token and get the user identity
        from flask_jwt_extended import decode_token
        decoded = decode_token(refresh_token)
        user_id = int(decoded['sub'])  # Convert string back to int
        user = db.session.get(User, user_id)

        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'detail': 'Token is invalid or expired'
            }), 401

        # Check if the refresh token has been revoked
        jti = decoded['jti']
        if jti in revoked_tokens:
            return jsonify({
                'success': False,
                'detail': 'Token is invalid or expired'
            }), 401

        # Generate new access token
        new_access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'access': new_access_token
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'detail': 'Token is invalid or expired'
        }), 401


@auth_bp.route("/auth/logout/", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout the current user and invalidate the access token.

    POST /api/auth/logout/

    Returns:
        200: Successfully logged out
    """
    # Revoke the current access token
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)

    return jsonify({
        'success': True,
        'message': 'Successfully logged out.'
    }), 200


# =============================================================================
# Profile Management Endpoints
# =============================================================================

@auth_bp.route("/auth/profile/", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Get the current user's profile information.

    GET /api/auth/profile/

    Returns:
        200: User profile data
        401: Authentication required
    """
    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Authentication credentials were not provided.'
        }), 401

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route("/auth/profile/", methods=["PUT", "PATCH"])
@jwt_required()
def update_profile():
    """
    Update the current user's profile information.

    PUT/PATCH /api/auth/profile/

    Request Body (all optional):
        first_name (str)
        last_name (str)
        phone_number (str)
        email (str)
        profile_image (str)

    Returns:
        200: Updated user profile
        400: Validation errors
    """
    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Authentication credentials were not provided.'
        }), 401

    data = request.get_json() or {}
    errors = {}

    # Validate email if provided
    if 'email' in data and data['email']:
        is_valid, msg = validate_email_format(data['email'])
        if not is_valid:
            errors['email'] = [msg]
        else:
            # Check if email is already used by another user
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user.id:
                errors['email'] = ["This email is already in use."]

    # Validate phone number if provided
    if 'phone_number' in data and data['phone_number']:
        is_valid, msg = validate_phone_number(data['phone_number'])
        if not is_valid:
            errors['phone_number'] = [msg]

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400

    # Update fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone_number' in data:
        user.phone_number = data['phone_number']
    if 'email' in data:
        user.email = data['email']
    if 'profile_image' in data:
        user.profile_image = data['profile_image']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Profile updated successfully.',
        'user': user.to_dict()
    }), 200


# =============================================================================
# Password Management Endpoints
# =============================================================================

@auth_bp.route("/auth/change-password/", methods=["POST"])
@jwt_required()
def change_password():
    """
    Change the current user's password.

    POST /api/auth/change-password/

    Request Body:
        old_password (str, required)
        new_password (str, required): 8+ chars, uppercase, lowercase, number, special char
        confirm_password (str, required): Must match new_password

    Returns:
        200: Password changed successfully
        400: Validation errors
    """
    user = get_current_user()
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Authentication credentials were not provided.'
        }), 401

    data = request.get_json() or {}
    errors = {}

    # Validate required fields
    if not data.get('old_password'):
        errors['old_password'] = ["This field is required."]
    if not data.get('new_password'):
        errors['new_password'] = ["This field is required."]
    if not data.get('confirm_password'):
        errors['confirm_password'] = ["This field is required."]

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400

    # Validate old password
    if not user.check_password(data['old_password']):
        errors['old_password'] = ["Old password is incorrect."]

    # Validate new password strength
    is_valid, msg = validate_password_strength(data['new_password'])
    if not is_valid:
        errors['new_password'] = [msg]

    # Validate password confirmation
    if data['new_password'] != data['confirm_password']:
        errors['confirm_password'] = ["Passwords do not match."]

    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400

    # Update password
    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password changed successfully.'
    }), 200
