"""
Input validation functions for the GreenHarvest Farm Management System.

This module provides validation utilities for user registration, profile
updates, and password management. All validators return a tuple of
(is_valid, error_message) for consistent error handling across routes.
"""
import re


def validate_username(username):
    """
    Validate username format.

    Requirements:
    - 3-30 characters
    - Alphanumeric characters and underscores only

    Args:
        username: The username string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "This field is required."

    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
        return False, "Username must be 3-30 characters and contain only letters, numbers, and underscores."

    return True, None


def validate_email_format(email):
    """
    Validate email format.

    Args:
        email: The email string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "This field is required."

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Enter a valid email address."

    return True, None


def validate_password_strength(password):
    """
    Validate password strength according to security requirements.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Args:
        password: The password string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "This field is required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."

    return True, None


def validate_phone_number(phone_number):
    """
    Validate phone number format (international format).

    Args:
        phone_number: The phone number string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone_number:
        return True, None  # Phone number is optional

    if not re.match(r'^\+?[\d() -]+$', phone_number):
        return False, "Enter a valid phone number."

    return True, None
