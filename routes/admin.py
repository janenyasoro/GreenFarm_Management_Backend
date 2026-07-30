"""
Admin user management routes for GreenHarvest Farm Management System.
Provides admin-only endpoints for user management.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from models import User
from extensions import db
from routes.helpers import get_current_user, admin_required
from validators import validate_email_format, validate_phone_number


admin_bp = Blueprint("admin", __name__, url_prefix="/api")


@admin_bp.route("/admin/users/", methods=["GET"])
@admin_required
def admin_list_users():
    """
    List all users with filtering, searching, ordering, and pagination.
    Admin only.

    GET /api/admin/users/

    Query Parameters:
        role (str, optional): Filter by role (admin, owner, worker)
        is_active (str, optional): Filter by active status (true, false)
        search (str, optional): Search by username or email
        ordering (str, optional): Order by field (default: -date_joined)
        page (int, optional): Page number (default: 1)

    Returns:
        200: List of users
        403: Non-admin user
    """
    query = User.query

    # Filter by role
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)

    # Filter by active status
    is_active = request.args.get('is_active')
    if is_active is not None:
        query = query.filter_by(is_active=is_active.lower() == 'true')

    # Search by username or email
    search = request.args.get('search')
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    # Ordering
    ordering = request.args.get('ordering', '-date_joined')
    if ordering:
        if ordering.startswith('-'):
            query = query.order_by(getattr(User, ordering[1:]).desc())
        else:
            query = query.order_by(getattr(User, ordering).asc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    users = [user.to_dict() for user in pagination.items]

    return jsonify(users), 200


@admin_bp.route("/admin/users/<int:user_id>/", methods=["GET"])
@admin_required
def admin_get_user(user_id):
    """
    Get detailed information about a specific user.
    Admin only.

    GET /api/admin/users/{id}/

    Returns:
        200: User details
        403: Non-admin user
        404: User not found
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Not found.'
        }), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@admin_bp.route("/admin/users/<int:user_id>/", methods=["PUT", "PATCH"])
@admin_required
def admin_update_user(user_id):
    """
    Update a user's information.
    Admin only. Prevents self-privilege escalation.

    PUT/PATCH /api/admin/users/{id}/

    Request Body (all optional):
        first_name (str)
        last_name (str)
        phone_number (str)
        email (str)
        profile_image (str)
        role (str): Must be "admin", "owner", or "worker"
        is_active (bool)
        is_staff (bool)

    Returns:
        200: Updated user data
        400: Validation errors or self-privilege escalation attempt
        403: Non-admin user
        404: User not found
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Not found.'
        }), 404

    data = request.get_json() or {}
    errors = {}

    # Prevent self-privilege escalation
    current_user = get_current_user()
    if user.id == current_user.id and 'role' in data:
        return jsonify({
            'success': False,
            'message': 'You cannot change your own role.'
        }), 400

    # Validate email if provided
    if 'email' in data and data['email']:
        is_valid, msg = validate_email_format(data['email'])
        if not is_valid:
            errors['email'] = [msg]
        else:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user.id:
                errors['email'] = ["This email is already in use."]

    # Validate phone number if provided
    if 'phone_number' in data and data['phone_number']:
        is_valid, msg = validate_phone_number(data['phone_number'])
        if not is_valid:
            errors['phone_number'] = [msg]

    # Validate role if provided
    if 'role' in data and data['role']:
        valid_roles = [User.Role.ADMIN, User.Role.OWNER, User.Role.WORKER]
        if data['role'] not in valid_roles:
            errors['role'] = ["Invalid role."]

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
    if 'role' in data:
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'is_staff' in data:
        user.is_staff = data['is_staff']

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'User updated successfully.',
        'user': user.to_dict()
    }), 200


@admin_bp.route("/admin/users/<int:user_id>/", methods=["DELETE"])
@admin_required
def admin_deactivate_user(user_id):
    """
    Deactivate a user account (soft delete).
    Admin only. Prevents self-deactivation.

    DELETE /api/admin/users/{id}/

    Returns:
        200: User deactivated successfully
        400: Attempting to deactivate self
        403: Non-admin user
        404: User not found
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({
            'success': False,
            'detail': 'Not found.'
        }), 404

    # Prevent self-deactivation
    current_user = get_current_user()
    if user.id == current_user.id:
        return jsonify({
            'success': False,
            'message': 'You cannot deactivate your own account.'
        }), 400

    # Soft delete - set is_active to False
    user.is_active = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'User deactivated successfully.',
        'user': user.to_dict()
    }), 200
