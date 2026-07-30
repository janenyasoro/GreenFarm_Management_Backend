"""
Helper functions for route handlers.
"""
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps
from models import User, Farm
from extensions import db


def get_current_user():
    """
    Get the current authenticated user from the JWT token.

    Returns:
        User object if found, None otherwise
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        # Convert string identity back to int if needed
        if isinstance(user_id, str):
            user_id = int(user_id)
        return db.session.get(User, user_id)
    except Exception:
        return None


def get_current_farm():
    """
    Get the farm associated with the currently logged-in user.

    Returns:
        Farm object if found, None otherwise
    """
    user = get_current_user()
    if not user:
        return None

    # Get the first farm owned by this user
    return Farm.query.filter_by(owner_id=user.id).first()


def parse_date(date_string):
    """
    Parse a date string in YYYY-MM-DD format to a date object.

    Args:
        date_string: String representation of a date

    Returns:
        datetime.date object or None if parsing fails
    """
    if not date_string:
        return None

    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def admin_required(fn):
    """
    Decorator to require admin role for a route.

    Usage:
        @app.route('/admin')
        @admin_required
        def admin_view():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401

        if not user.is_admin():
            return jsonify({
                'success': False,
                'message': 'You do not have permission to perform this action.'
            }), 403

        return fn(*args, **kwargs)
    return wrapper


def owner_or_admin_required(fn):
    """
    Decorator to require owner or admin role for a route.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401

        if not (user.is_admin() or user.is_owner()):
            return jsonify({
                'success': False,
                'message': 'You do not have permission to perform this action.'
            }), 403

        return fn(*args, **kwargs)
    return wrapper
