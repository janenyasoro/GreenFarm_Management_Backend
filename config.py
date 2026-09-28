import os
import logging
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

# Load environment variables from .env file (only for local development)
load_dotenv()

logger = logging.getLogger(__name__)


def _resolve_database_uri():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return 'sqlite:///greenharvest.db'

    database_url = database_url.strip()
    if database_url.startswith('postgres://'):
        database_url = 'postgresql://' + database_url[len('postgres://'):]

    try:
        make_url(database_url)
    except Exception:
        env = os.environ.get('FLASK_ENV', 'development').lower()
        if env == 'development':
            logger.warning('Invalid DATABASE_URL detected; falling back to sqlite:///greenharvest.db')
            return 'sqlite:///greenharvest.db'
        raise RuntimeError(
            'Invalid DATABASE_URL. Set it to a valid PostgreSQL URL such as '
            'postgresql://user:password@host:5432/database_name'
        )

    return database_url

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 86400))
    
    # CORS
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', 'https://greenfarm-management-frontend.onrender.com')
    
    # Environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'