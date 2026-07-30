"""
Test cases for authentication and user management endpoints.
Converted from Django TestCase to Flask pytest tests.
"""
import pytest
from extensions import db
from models import User


class TestAuthentication:
    """Test cases for authentication endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['role'] == 'owner'

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password, first_name, last_name
        })

        assert response.status_code == 400

    def test_register_duplicate_username(self, client, regular_user):
        """Test registration with duplicate username."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400

    def test_register_duplicate_email(self, client, regular_user):
        """Test registration with duplicate email."""
        response = client.post('/api/auth/register/', json={
            'username': 'differentuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400

    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/api/auth/register/', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Different@123',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400

    def test_login_with_username(self, client, regular_user):
        """Test login using username."""
        response = client.post('/api/auth/login/', json={
            'username': 'testuser',
            'password': 'Test@123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access' in data
        assert 'refresh' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'

    def test_login_with_email(self, client, regular_user):
        """Test login using email."""
        response = client.post('/api/auth/login/', json={
            'username': 'test@example.com',
            'password': 'Test@123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access' in data

    def test_login_wrong_password(self, client, regular_user):
        """Test login with wrong password."""
        response = client.post('/api/auth/login/', json={
            'username': 'testuser',
            'password': 'Wrong@123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data.get('success', True) is False

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login/', json={
            'username': 'nonexistent',
            'password': 'Test@123'
        })

        assert response.status_code == 401

    def test_login_inactive_user(self, client, app):
        """Test login with deactivated user."""
        # Create and deactivate user
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role=User.Role.OWNER,
                is_active=False
            )
            user.set_password('Test@123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/api/auth/login/', json={
            'username': 'testuser',
            'password': 'Test@123'
        })

        assert response.status_code == 401

    def test_token_refresh(self, client, regular_user):
        """Test token refresh."""
        # Login first
        login_response = client.post('/api/auth/login/', json={
            'username': 'testuser',
            'password': 'Test@123'
        })
        refresh_token = login_response.get_json()['refresh']

        # Refresh token
        response = client.post('/api/auth/token/refresh/', json={
            'refresh': refresh_token
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access' in data

    def test_logout(self, client, regular_user):
        """Test logout with token blacklisting."""
        # Login first
        login_response = client.post('/api/auth/login/', json={
            'username': 'testuser',
            'password': 'Test@123'
        })
        access_token = login_response.get_json()['access']

        # Logout
        response = client.post('/api/auth/logout/',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestProfileManagement:
    """Test cases for profile management endpoints."""

    def test_get_profile_authenticated(self, client, auth_headers):
        """Test getting profile when authenticated."""
        response = client.get('/api/auth/profile/', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['username'] == 'testuser'

    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication."""
        response = client.get('/api/auth/profile/')

        assert response.status_code == 401

    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        response = client.patch('/api/auth/profile/',
            json={
                'first_name': 'Updated',
                'last_name': 'Name',
                'phone_number': '+9876543210'
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['last_name'] == 'Name'

    def test_update_profile_email(self, client, auth_headers):
        """Test updating email in profile."""
        response = client.patch('/api/auth/profile/',
            json={'email': 'updated@example.com'},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'updated@example.com'

    def test_update_profile_duplicate_email(self, client, app, auth_headers):
        """Test updating profile with duplicate email."""
        # Create another user
        with app.app_context():
            user = User(
                username='otheruser',
                email='other@example.com',
                first_name='Other',
                last_name='User',
                role=User.Role.OWNER
            )
            user.set_password('Test@123')
            db.session.add(user)
            db.session.commit()

        # Try to update with duplicate email
        response = client.patch('/api/auth/profile/',
            json={'email': 'other@example.com'},
            headers=auth_headers
        )

        assert response.status_code == 400


class TestPasswordChange:
    """Test cases for password change endpoint."""

    def test_change_password_success(self, client, auth_headers):
        """Test successful password change."""
        response = client.post('/api/auth/change-password/',
            json={
                'old_password': 'Test@123',
                'new_password': 'New@4567',
                'confirm_password': 'New@4567'
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_change_password_wrong_old_password(self, client, auth_headers):
        """Test password change with wrong old password."""
        response = client.post('/api/auth/change-password/',
            json={
                'old_password': 'Wrong@123',
                'new_password': 'New@4567',
                'confirm_password': 'New@4567'
            },
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_change_password_weak_new_password(self, client, auth_headers):
        """Test password change with weak new password."""
        response = client.post('/api/auth/change-password/',
            json={
                'old_password': 'Test@123',
                'new_password': 'weak',
                'confirm_password': 'weak'
            },
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_change_password_mismatch(self, client, auth_headers):
        """Test password change with mismatched passwords."""
        response = client.post('/api/auth/change-password/',
            json={
                'old_password': 'Test@123',
                'new_password': 'New@4567',
                'confirm_password': 'Different@4567'
            },
            headers=auth_headers
        )

        assert response.status_code == 400


class TestAdminUserManagement:
    """Test cases for admin user management endpoints."""

    def test_list_users_admin(self, client, admin_headers):
        """Test listing users as admin."""
        response = client.get('/api/admin/users/', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1

    def test_list_users_filter_role(self, client, admin_headers):
        """Test filtering users by role."""
        response = client.get('/api/admin/users/?role=owner', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        for user in data:
            assert user['role'] == 'owner'

    def test_list_users_filter_active(self, client, admin_headers):
        """Test filtering users by active status."""
        response = client.get('/api/admin/users/?is_active=true', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        for user in data:
            assert user['is_active'] is True

    def test_list_users_search(self, client, admin_headers):
        """Test searching users."""
        response = client.get('/api/admin/users/?search=admin', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0

    def test_list_users_ordering(self, client, admin_headers):
        """Test ordering users."""
        response = client.get('/api/admin/users/?ordering=username', headers=admin_headers)

        assert response.status_code == 200

    def test_list_users_non_admin(self, client, auth_headers):
        """Test listing users as non-admin (should fail)."""
        response = client.get('/api/admin/users/', headers=auth_headers)

        assert response.status_code == 403

    def test_get_user_admin(self, client, admin_headers, regular_user):
        """Test getting a specific user as admin."""
        response = client.get(f'/api/admin/users/{regular_user.id}/', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['username'] == 'testuser'

    def test_update_user_admin(self, client, admin_headers, regular_user):
        """Test updating a user as admin."""
        response = client.patch(f'/api/admin/users/{regular_user.id}/',
            json={
                'first_name': 'Updated',
                'role': 'worker'
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['first_name'] == 'Updated'
        assert data['user']['role'] == 'worker'

    def test_update_user_self_role(self, client, app, admin_headers, admin_user):
        """Test that admin cannot change their own role."""
        response = client.patch(f'/api/admin/users/{admin_user.id}/',
            json={'role': 'owner'},
            headers=admin_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_deactivate_user_admin(self, client, admin_headers, regular_user):
        """Test deactivating a user as admin."""
        response = client.delete(f'/api/admin/users/{regular_user.id}/', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['user']['is_active'] is False

    def test_deactivate_self_admin(self, client, admin_headers, admin_user):
        """Test that admin cannot deactivate themselves."""
        response = client.delete(f'/api/admin/users/{admin_user.id}/', headers=admin_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_pagination(self, client, app, admin_headers):
        """Test pagination of user list."""
        # Create additional users
        with app.app_context():
            for i in range(25):
                user = User(
                    username=f'user{i}',
                    email=f'user{i}@example.com',
                    first_name='User',
                    last_name=str(i),
                    role=User.Role.OWNER
                )
                user.set_password('Test@123')
                db.session.add(user)
            db.session.commit()

        response = client.get('/api/admin/users/', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        # Check if pagination is working (default page size is 20)
        assert len(data) <= 20