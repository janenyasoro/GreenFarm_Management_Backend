from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'due_date', 'owner', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
