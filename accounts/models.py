from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for GreenHarvest Farm Management System.
    Extends Django's AbstractUser to include additional fields.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        OWNER = 'owner', 'Farm Owner'
        WORKER = 'worker', 'Farm Worker'
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OWNER
    )
    profile_image = models.URLField(blank=True, null=True)
    
    # Override timestamp fields to match specification
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN
    
    def is_owner(self):
        """Check if user is a farm owner."""
        return self.role == self.Role.OWNER
    
    def is_worker(self):
        """Check if user is a farm worker."""
        return self.role == self.Role.WORKER