from django.utils import timezone
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'owner', 'owner_name', 'assigned_to', 'assigned_to_name',
            'is_overdue', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None

    def get_is_overdue(self, obj):
        if obj.due_date and obj.status != Task.STATUS_COMPLETED:
            return obj.due_date < timezone.now().date()
        return False


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value):
        valid = [c[0] for c in Task.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid)}")
        return value
