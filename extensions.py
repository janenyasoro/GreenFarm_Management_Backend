"""
Flask extensions for GreenHarvest Farm Management System.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

# Database instance
db = SQLAlchemy()

# JWT Manager instance
jwt = JWTManager()

# CORS instance
cors = CORS()

# Bcrypt instance for password hashing
bcrypt = Bcrypt()

# Marshmallow instance for serialization/validation
ma = Marshmallow()


def init_extensions(app):
    """Initialize all Flask extensions with the app."""
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True, origins=app.config.get('CORS_ALLOWED_ORIGINS', '*'))
    bcrypt.init_app(app)
    ma.init_app(app)
