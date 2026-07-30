"""
Test configuration and fixtures for GreenHarvest Farm Management System.
"""
import pytest
from app import create_app
from extensions import db
from models import User


@pytest.fixture(scope="function")
def app():
    """Create and configure a test Flask application."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
            is_active=True,
            is_staff=True,
            date_joined=None
        )
        user.set_password('Admin@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def regular_user(app):
    """Create a regular user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role=User.Role.OWNER,
            is_active=True,
            is_staff=False,
            date_joined=None
        )
        user.set_password('Test@123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_headers(client, regular_user):
    """Get authentication headers for a regular user."""
    response = client.post('/api/auth/login/', json={
        'username': 'testuser',
        'password': 'Test@123'
    })
    access_token = response.get_json()['access']
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for an admin user."""
    response = client.post('/api/auth/login/', json={
        'username': 'admin',
        'password': 'Admin@123'
    })
    access_token = response.get_json()['access']
    return {'Authorization': f'Bearer {access_token}'}