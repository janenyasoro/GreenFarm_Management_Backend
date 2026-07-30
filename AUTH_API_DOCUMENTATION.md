# Authentication & User Accounts API Documentation

## Overview

This API provides comprehensive authentication and user management functionality for the GreenHarvest Farm Management System using Flask and Flask-JWT-Extended. All endpoints use JWT (JSON Web Tokens) for authentication and role-based access control.

**Base URL:** `http://localhost:5000/api/`

**Authentication:** Bearer Token (JWT) - Include token in Authorization header: `Authorization: Bearer <token>`

---

## Authentication Endpoints

### 1. Register User

Register a new user account with the system.

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "Farm@123",
  "confirm_password": "Farm@123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

**Required Fields:**
- `username` (string, 3-30 characters, alphanumeric + underscores only)
- `email` (string, valid email format)
- `password` (string, min 8 characters, must contain uppercase, lowercase, number, special character)
- `confirm_password` (string, must match password)
- `first_name` (string)
- `last_name` (string)

**Optional Fields:**
- `phone_number` (string, international format)

**Success Response:**
```json
{
  "success": true,
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_image": null,
    "role": "owner",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": null
  }
}
```

**Status Code:** `201 Created`

**Error Responses:**

- `400 Bad Request` - Missing required fields or validation errors
```json
{
  "success": false,
  "errors": {
    "username": ["Username must be 3-30 characters and contain only letters, numbers, and underscores."],
    "password": ["Password must be at least 8 characters long."]
  }
}
```

- `400 Bad Request` - Password mismatch
```json
{
  "success": false,
  "errors": {
    "password": ["Passwords do not match."]
  }
}
```

---

### 2. Login

Authenticate user and receive JWT tokens.

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "Farm@123"
}
```

**Note:** You can use either username or email in the `username` field.

**Success Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "role": "owner"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `401 Unauthorized` - Invalid credentials (generic error message)
```json
{
  "success": false,
  "detail": "Invalid credentials."
}
```

- `401 Unauthorized` - Account deactivated
```json
{
  "success": false,
  "detail": "This account has been deactivated."
}
```

---

### 3. Refresh Token

Get a new access token using a refresh token.

**Endpoint:** `POST /api/auth/token/refresh/`

**Authentication:** Required (Refresh Token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `401 Unauthorized` - Invalid or expired refresh token
```json
{
  "success": false,
  "detail": "Token is invalid or expired"
}
```

---

### 4. Logout

Logout the current user and invalidate refresh token.

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required (Access Token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Successfully logged out."
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `400 Bad Request` - Invalid token
```json
{
  "success": false,
  "message": "Invalid token."
}
```

---

## Profile Management Endpoints

### 5. Get Profile

Get the current user's profile information.

**Endpoint:** `GET /api/auth/profile/`

**Authentication:** Required (Access Token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_image": null,
    "role": "owner",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `401 Unauthorized` - Missing or invalid token
```json
{
  "success": false,
  "detail": "Authentication credentials were not provided."
}
```

---

### 6. Update Profile

Update the current user's profile information.

**Endpoint:** `PUT /api/auth/profile/` or `PATCH /api/auth/profile/`

**Authentication:** Required (Access Token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+9876543210",
  "email": "john.smith@example.com",
  "profile_image": "https://example.com/profile.jpg"
}
```

**Note:** All fields are optional. Only provided fields will be updated. Users cannot change: `role`, `password`, `is_staff`.

**Success Response:**
```json
{
  "success": true,
  "message": "Profile updated successfully.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john.smith@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+9876543210",
    "profile_image": "https://example.com/profile.jpg",
    "role": "owner",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `400 Bad Request` - Validation errors
```json
{
  "success": false,
  "errors": {
    "email": ["Enter a valid email address."],
    "phone_number": ["Enter a valid phone number."]
  }
}
```

- `400 Bad Request` - Duplicate email
```json
{
  "success": false,
  "errors": {
    "email": ["This email is already in use."]
  }
}
```

---

## Password Management Endpoints

### 7. Change Password

Change the current user's password.

**Endpoint:** `POST /api/auth/change-password/`

**Authentication:** Required (Access Token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "Farm@123",
  "new_password": "NewFarm@456",
  "confirm_password": "NewFarm@456"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Password changed successfully."
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `400 Bad Request` - Missing fields
```json
{
  "success": false,
  "errors": {
    "old_password": ["This field is required."]
  }
}
```

- `400 Bad Request` - Incorrect old password
```json
{
  "success": false,
  "errors": {
    "old_password": ["Old password is incorrect."]
  }
}
```

- `400 Bad Request` - Weak new password
```json
{
  "success": false,
  "errors": {
    "new_password": ["Password must be at least 8 characters long."]
  }
}
```

- `400 Bad Request` - Passwords don't match
```json
{
  "success": false,
  "errors": {
    "confirm_password": ["Passwords do not match."]
  }
}
```

---

## Admin User Management Endpoints

### 8. List All Users

Get a list of all registered users (Admin only).

**Endpoint:** `GET /api/admin/users/`

**Authentication:** Required (Access Token + Admin Role)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `role` (optional) - Filter by role (`admin`, `owner`, `worker`)
- `is_active` (optional) - Filter by active status (`true`, `false`)
- `search` (optional) - Search by username or email
- `ordering` (optional) - Order by field (`username`, `-username`, `date_joined`, `-date_joined`)
- `page` (optional) - Page number for pagination

**Success Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "phone_number": null,
    "profile_image": null,
    "role": "admin",
    "is_active": true,
    "is_staff": true,
    "date_joined": "2024-01-01T09:00:00Z",
    "last_login": "2024-01-20T15:30:00Z"
  },
  {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_image": null,
    "role": "owner",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
]
```

**Status Code:** `200 OK`

**Error Responses:**

- `403 Forbidden` - Non-admin user
```json
{
  "success": false,
  "message": "You do not have permission to perform this action."
}
```

---

### 9. Get User Details

Get detailed information about a specific user (Admin only).

**Endpoint:** `GET /api/admin/users/{id}/`

**Authentication:** Required (Access Token + Admin Role)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer) - The ID of the user to retrieve

**Success Response:**
```json
{
  "success": true,
  "user": {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_image": null,
    "role": "owner",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `403 Forbidden` - Non-admin user
```json
{
  "success": false,
  "message": "You do not have permission to perform this action."
}
```

- `404 Not Found` - User doesn't exist
```json
{
  "success": false,
  "detail": "Not found."
}
```

---

### 10. Update User

Update a user's information (Admin only).

**Endpoint:** `PUT /api/admin/users/{id}/` or `PATCH /api/admin/users/{id}/`

**Authentication:** Required (Access Token + Admin Role)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer) - The ID of the user to update

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+9876543210",
  "email": "john.smith@example.com",
  "profile_image": "https://example.com/profile.jpg",
  "role": "worker",
  "is_active": true,
  "is_staff": false
}
```

**Allowed Fields:**
- `first_name` (string)
- `last_name` (string)
- `phone_number` (string)
- `email` (string)
- `profile_image` (string)
- `role` (string) - Must be "admin", "owner", or "worker"
- `is_active` (boolean)
- `is_staff` (boolean)

**Success Response:**
```json
{
  "success": true,
  "message": "User updated successfully.",
  "user": {
    "id": 2,
    "username": "john_doe",
    "email": "john.smith@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+9876543210",
    "profile_image": "https://example.com/profile.jpg",
    "role": "worker",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `400 Bad Request` - Validation errors
```json
{
  "success": false,
  "errors": {
    "role": ["Invalid role."]
  }
}
```

- `400 Bad Request` - Attempting to change own role
```json
{
  "success": false,
  "message": "You cannot change your own role."
}
```

- `403 Forbidden` - Non-admin user
```json
{
  "success": false,
  "message": "You do not have permission to perform this action."
}
```

- `404 Not Found` - User doesn't exist
```json
{
  "success": false,
  "detail": "Not found."
}
```

---

### 11. Deactivate User

Deactivate a user account (Admin only). This is a soft delete.

**Endpoint:** `DELETE /api/admin/users/{id}/`

**Authentication:** Required (Access Token + Admin Role)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameters:**
- `id` (integer) - The ID of the user to deactivate

**Success Response:**
```json
{
  "success": true,
  "message": "User deactivated successfully.",
  "user": {
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "profile_image": null,
    "role": "owner",
    "is_active": false,
    "is_staff": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:45:00Z"
  }
}
```

**Status Code:** `200 OK`

**Error Responses:**

- `400 Bad Request` - Attempting to deactivate self
```json
{
  "success": false,
  "message": "You cannot deactivate your own account."
}
```

- `403 Forbidden` - Non-admin user
```json
{
  "success": false,
  "message": "You do not have permission to perform this action."
}
```

- `404 Not Found` - User doesn't exist
```json
{
  "success": false,
  "detail": "Not found."
}
```

---

## Validation Rules

### Username
- **Required:** Yes
- **Unique:** Yes
- **Length:** 3-30 characters
- **Format:** Alphanumeric characters and underscores only

### Email
- **Required:** Yes
- **Unique:** Yes
- **Format:** Valid email address (e.g., user@example.com)

### Password
- **Required:** Yes
- **Minimum Length:** 8 characters
- **Requirements:**
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- **Example:** `Farm@123`

### Phone Number
- **Required:** No
- **Format:** International format (e.g., +1234567890)

### Roles
- **Available Roles:**
  - `admin` - Full system access
  - `owner` - Farm owner access
  - `worker` - Farm worker access

---

## Token Management

### Access Token
- **Expiration:** 15 minutes
- **Usage:** Include in Authorization header for authenticated requests
- **Format:** `Authorization: Bearer <access_token>`

### Refresh Token
- **Expiration:** 7 days
- **Usage:** Use to obtain new access tokens
- **Format:** Send in request body to `/api/auth/token/refresh/`

### Token Refresh Flow
1. User logs in and receives both access and refresh tokens
2. Use access token for API requests
3. When access token expires, use refresh token to get new access token
4. If refresh token expires, user must log in again

---

## Error Response Format

All error responses follow this consistent format:

**General Error:**
```json
{
  "success": false,
  "message": "Error message"
}
```

**Validation Error:**
```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message 1", "Error message 2"]
  }
}
```

**Common HTTP Status Codes:**
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found

---

## Security Features

1. **Password Hashing** - Uses Werkzeug's password hashing (bcrypt/pbkdf2)
2. **JWT Authentication** - Token-based authentication with expiration
3. **Token Blacklisting** - Logout functionality with token invalidation
4. **CSRF Protection** - CSRF protection enabled where applicable
5. **Role-Based Access Control** - Admin, Owner, Worker roles
6. **Input Validation** - Comprehensive validation for all inputs
7. **Generic Error Messages** - Login errors don't reveal user existence
8. **Privilege Escalation Prevention** - Users cannot change their own role
9. **Self-Deactivation Prevention** - Admins cannot deactivate themselves

---

## Configuration

### Environment Variables

Set these environment variables in production:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/greenfarm
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

### Database Configuration

- **Development:** SQLite (default)
- **Production:** PostgreSQL (recommended)

### Token Configuration

- **Access Token Lifetime:** 15 minutes
- **Refresh Token Lifetime:** 7 days
- **Token Rotation:** Enabled
- **Token Blacklisting:** Enabled

---

## Testing

Run the test suite to verify all endpoints:

```bash
pytest tests/ -v
```

The test suite includes:
- **Registration Tests:** Valid registration, duplicate username/email, weak password, missing fields
- **Login Tests:** Valid username/email login, wrong password, inactive user
- **Profile Tests:** Retrieve profile, update profile, unauthorized access
- **Password Change Tests:** Correct old password, incorrect old password, weak new password, password mismatch
- **Admin Tests:** List users with filtering/searching/pagination, update user, deactivate user, non-admin access denied

---

## Integration with Other Modules

This authentication module provides the foundation for other backend modules:

- **Crops Module (Developer 2):** Use `@jwt_required()` to protect crop endpoints
- **Livestock & Health Module (Developer 3):** Integrate with authentication and check user roles
- **Finance Module (Developer 4):** Protect financial data with JWT authentication
- **Inventory Module (Developer 5):** Require authentication for inventory management
- **Tasks & Dashboard Module (Developer 6):** Use user roles for dashboard access control

### Integration Example

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from routes.helpers import get_current_user, admin_required

bp = Blueprint("crops", __name__, url_prefix="/api/crops")

@bp.route("/", methods=["GET"])
@jwt_required()
def list_crops():
    user = get_current_user()
    # Your crop management logic here

@bp.route("/admin/", methods=["GET"])
@admin_required
def admin_crops():
    # Admin-only functionality
```

---

## Project Structure

```
GreenFarm_Management_Backend/
├── app.py                  # Flask application factory
├── config.py               # Flask configuration
├── extensions.py           # Flask extensions (db, jwt, cors)
├── models.py               # SQLAlchemy models
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── Pipfile                 # Pipfile for dependency management
├── routes/
│   ├── __init__.py         # Route registration
│   ├── auth.py             # Authentication routes
│   ├── helpers.py          # Helper functions and decorators
│   ├── expenses.py         # Expense management routes
│   ├── health_records.py   # Health records routes
│   ├── income.py           # Income management routes
│   ├── inventory.py        # Inventory management routes
│   └── livestock.py        # Livestock management routes
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Test fixtures
│   └── test_auth.py        # Authentication tests
├── AUTH_API_DOCUMENTATION.md
├── DEVELOPER1_DELIVERABLES.md
└── README.md
```

---

## Future Enhancements

1. **Email Verification** - Send verification emails during registration
2. **Password Reset** - Implement forgot password functionality
3. **Two-Factor Authentication** - Add 2FA for enhanced security
4. **OAuth Integration** - Allow login with Google, Facebook, etc.
5. **Rate Limiting** - Implement rate limiting on auth endpoints
6. **Account Lockout** - Lock accounts after multiple failed attempts
7. **Profile Image Upload** - Implement image upload functionality
8. **Audit Logging** - Log all authentication events
9. **Session Management** - View and manage active sessions
10. **Email Notifications** - Send notifications for account changes

---

## Technologies Used

- **Flask 3.0.0** - Web framework
- **Flask-SQLAlchemy 3.1.1** - ORM for database operations
- **Flask-JWT-Extended 6.0.0** - JWT authentication
- **Flask-CORS 4.0.0** - CORS support
- **Werkzeug** - Password hashing
- **PostgreSQL** - Production database (SQLite for development)
- **Python 3.12** - Programming language

---

## Support

For issues or questions related to this authentication module, please contact Developer 1 or refer to the Flask and Flask-JWT-Extended documentation.