# GreenFarm Management Backend

A farm management system built with Flask, Flask-SQLAlchemy, and Flask-JWT-Extended.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python run.py
```

The API will be available at `http://localhost:5000/api/`

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

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout

### Profile Management
- `GET /api/auth/profile/` - Get user profile
- `PUT/PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password

### Admin User Management
- `GET /api/admin/users/` - List users (admin only)
- `GET /api/admin/users/{id}/` - Get user details (admin only)
- `PUT/PATCH /api/admin/users/{id}/` - Update user (admin only)
- `DELETE /api/admin/users/{id}/` - Deactivate user (admin only)

## Testing

```bash
pytest tests/ -v
```

## Documentation

See [AUTH_API_DOCUMENTATION.md](AUTH_API_DOCUMENTATION.md) for complete API documentation.

## Technologies

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-JWT-Extended 6.0.0
- Flask-CORS 4.0.0
- PostgreSQL (production) / SQLite (development)