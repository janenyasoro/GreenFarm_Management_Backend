from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Test cases for authentication endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
    
    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post('/api/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['role'], 'owner')
    
    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password, first_name, last_name
        }
        response = self.client.post('/api/auth/register/', incomplete_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username."""
        # First registration
        self.client.post('/api/auth/register/', self.user_data)
        
        # Second registration with same username
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'different@example.com'
        response = self.client.post('/api/auth/register/', duplicate_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        # First registration
        self.client.post('/api/auth/register/', self.user_data)
        
        # Second registration with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'differentuser'
        response = self.client.post('/api/auth/register/', duplicate_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_weak_password(self):
        """Test registration with weak password."""
        weak_password_data = self.user_data.copy()
        weak_password_data['password'] = 'weak'
        weak_password_data['confirm_password'] = 'weak'
        response = self.client.post('/api/auth/register/', weak_password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_invalid_email(self):
        """Test registration with invalid email format."""
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        response = self.client.post('/api/auth/register/', invalid_email_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        mismatch_data = self.user_data.copy()
        mismatch_data['confirm_password'] = 'Different@123'
        response = self.client.post('/api/auth/register/', mismatch_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_username(self):
        """Test login using username."""
        # Register user first
        self.client.post('/api/auth/register/', self.user_data)
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'Test@123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_with_email(self):
        """Test login using email."""
        # Register user first
        self.client.post('/api/auth/register/', self.user_data)
        
        # Login with email
        login_data = {
            'username': 'test@example.com',
            'password': 'Test@123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_login_wrong_password(self):
        """Test login with wrong password."""
        # Register user first
        self.client.post('/api/auth/register/', self.user_data)
        
        # Login with wrong password
        login_data = {
            'username': 'testuser',
            'password': 'Wrong@123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data.get('success', True))
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        login_data = {
            'username': 'nonexistent',
            'password': 'Test@123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test login with deactivated user."""
        # Register user
        self.client.post('/api/auth/register/', self.user_data)
        
        # Deactivate user
        user = User.objects.get(username='testuser')
        user.is_active = False
        user.save()
        
        # Try to login
        login_data = {
            'username': 'testuser',
            'password': 'Test@123'
        }
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh."""
        # Register and login
        self.client.post('/api/auth/register/', self.user_data)
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test@123'
        })
        refresh_token = login_response.data['refresh']
        
        # Refresh token
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_logout(self):
        """Test logout with token blacklisting."""
        # Register and login
        self.client.post('/api/auth/register/', self.user_data)
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test@123'
        })
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/auth/logout/', {
            'refresh': refresh_token
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class ProfileManagementTestCase(TestCase):
    """Test cases for profile management endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        # Register and login
        self.client.post('/api/auth/register/', self.user_data)
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test@123'
        })
        self.access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_get_profile_unauthorized(self):
        """Test getting profile without authentication."""
        self.client.credentials()  # Remove authentication
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile(self):
        """Test updating user profile."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+9876543210'
        }
        response = self.client.patch('/api/auth/profile/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['first_name'], 'Updated')
        self.assertEqual(response.data['user']['last_name'], 'Name')
    
    def test_update_profile_email(self):
        """Test updating email in profile."""
        update_data = {
            'email': 'updated@example.com'
        }
        response = self.client.patch('/api/auth/profile/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'updated@example.com')
    
    def test_update_profile_duplicate_email(self):
        """Test updating profile with duplicate email."""
        # Create another user
        other_user_data = self.user_data.copy()
        other_user_data['username'] = 'otheruser'
        other_user_data['email'] = 'other@example.com'
        self.client.credentials()  # Remove auth temporarily
        self.client.post('/api/auth/register/', other_user_data)
        
        # Try to update with duplicate email
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        update_data = {
            'email': 'other@example.com'
        }
        response = self.client.patch('/api/auth/profile/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordChangeTestCase(TestCase):
    """Test cases for password change endpoint."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        # Register and login
        self.client.post('/api/auth/register/', self.user_data)
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test@123'
        })
        self.access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_change_password_success(self):
        """Test successful password change."""
        password_data = {
            'old_password': 'Test@123',
            'new_password': 'New@456',
            'confirm_password': 'New@456'
        }
        response = self.client.post('/api/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        password_data = {
            'old_password': 'Wrong@123',
            'new_password': 'New@456',
            'confirm_password': 'New@456'
        }
        response = self.client.post('/api/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_weak_new_password(self):
        """Test password change with weak new password."""
        password_data = {
            'old_password': 'Test@123',
            'new_password': 'weak',
            'confirm_password': 'weak'
        }
        response = self.client.post('/api/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatch(self):
        """Test password change with mismatched passwords."""
        password_data = {
            'old_password': 'Test@123',
            'new_password': 'New@456',
            'confirm_password': 'Different@456'
        }
        response = self.client.post('/api/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdminUserManagementTestCase(TestCase):
    """Test cases for admin user management endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='Admin@123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test@123',
            first_name='Test',
            last_name='User',
            role='owner'
        )
        
        # Login as admin
        login_response = self.client.post('/api/auth/login/', {
            'username': 'admin',
            'password': 'Admin@123'
        })
        self.admin_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    
    def test_list_users_admin(self):
        """Test listing users as admin."""
        response = self.client.get('/api/admin/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)  # Admin + regular user
    
    def test_list_users_filter_role(self):
        """Test filtering users by role."""
        response = self.client.get('/api/admin/users/?role=owner')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data:
            self.assertEqual(user['role'], 'owner')
    
    def test_list_users_filter_active(self):
        """Test filtering users by active status."""
        response = self.client.get('/api/admin/users/?is_active=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data:
            self.assertTrue(user['is_active'])
    
    def test_list_users_search(self):
        """Test searching users."""
        response = self.client.get('/api/admin/users/?search=test')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_list_users_ordering(self):
        """Test ordering users."""
        response = self.client.get('/api/admin/users/?ordering=username')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_users_non_admin(self):
        """Test listing users as non-admin (should fail)."""
        # Login as regular user
        self.client.credentials()  # Remove admin auth
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'Test@123'
        })
        user_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        
        response = self.client.get('/api/admin/users/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_admin(self):
        """Test getting a specific user as admin."""
        response = self.client.get(f'/api/admin/users/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_update_user_admin(self):
        """Test updating a user as admin."""
        update_data = {
            'first_name': 'Updated',
            'role': 'worker'
        }
        response = self.client.patch(f'/api/admin/users/{self.user.id}/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')
        self.assertEqual(response.data['user']['role'], 'worker')
    
    def test_update_user_self_role(self):
        """Test that admin cannot change their own role."""
        update_data = {
            'role': 'owner'
        }
        response = self.client.patch(f'/api/admin/users/{self.admin.id}/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_deactivate_user_admin(self):
        """Test deactivating a user as admin."""
        response = self.client.delete(f'/api/admin/users/{self.user.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['user']['is_active'])
    
    def test_deactivate_self_admin(self):
        """Test that admin cannot deactivate themselves."""
        response = self.client.delete(f'/api/admin/users/{self.admin.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_pagination(self):
        """Test pagination of user list."""
        # Create additional users
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='Test@123',
                first_name='User',
                last_name=str(i)
            )
        
        response = self.client.get('/api/admin/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if pagination is working (default page size is 20)
        self.assertTrue(len(response.data) <= 20)