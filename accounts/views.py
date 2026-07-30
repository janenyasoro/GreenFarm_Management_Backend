from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    AdminUserSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """API view for user registration."""
    
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Registration successful.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """API view for user login."""
    
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """API view for user logout."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Successfully logged out.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """API view for retrieving and updating user profile."""
    
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UpdateProfileSerializer
    
    def get(self, request, *args, **kwargs):
        """Get user profile."""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    """API view for changing user password."""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)


class AdminUserListView(generics.ListAPIView):
    """API view for listing all users (admin only)."""
    
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Searching
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-date_joined')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for retrieving, updating, and deactivating users (admin only)."""
    
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = 'id'
    
    def get(self, request, *args, **kwargs):
        """Get user details."""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update user details."""
        user = self.get_object()
        
        # Prevent self-privilege escalation
        if user == request.user and 'role' in request.data:
            return Response({
                'success': False,
                'message': 'You cannot change your own role.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.context['user_id'] = user.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'User updated successfully.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Deactivate user (soft delete)."""
        user = self.get_object()
        
        # Prevent self-deactivation
        if user == request.user:
            return Response({
                'success': False,
                'message': 'You cannot deactivate your own account.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Soft delete - set is_active to False
        user.is_active = False
        user.save()
        
        return Response({
            'success': True,
            'message': 'User deactivated successfully.',
            'user': AdminUserSerializer(user).data
        }, status=status.HTTP_200_OK)