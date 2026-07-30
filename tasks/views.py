from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.filter(
            Q(owner=self.request.user) | Q(assigned_to=self.request.user)
        ).select_related('owner', 'assigned_to')

        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')

        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority_filter:
            qs = qs.filter(priority=priority_filter)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            Q(owner=self.request.user) | Q(assigned_to=self.request.user)
        ).select_related('owner', 'assigned_to')


class TaskStatusUpdateView(generics.UpdateAPIView):
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Task.objects.filter(
            Q(owner=self.request.user) | Q(assigned_to=self.request.user)
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TaskSerializer(instance).data)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        upcoming_threshold = today + timedelta(days=7)

        user_tasks = Task.objects.filter(
            Q(owner=user) | Q(assigned_to=user)
        )

        status_counts = user_tasks.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=Task.STATUS_PENDING)),
            in_progress=Count('id', filter=Q(status=Task.STATUS_IN_PROGRESS)),
            completed=Count('id', filter=Q(status=Task.STATUS_COMPLETED)),
            overdue=Count('id', filter=Q(
                due_date__lt=today,
                status__in=[Task.STATUS_PENDING, Task.STATUS_IN_PROGRESS],
            )),
        )

        upcoming_tasks = user_tasks.filter(
            due_date__range=(today, upcoming_threshold),
            status__in=[Task.STATUS_PENDING, Task.STATUS_IN_PROGRESS],
        ).order_by('due_date')[:5]

        recent_tasks = user_tasks.order_by('-created_at')[:5]

        return Response({
            'tasks': {
                **status_counts,
                'upcoming': TaskSerializer(upcoming_tasks, many=True).data,
            },
            'recent_tasks': TaskSerializer(recent_tasks, many=True).data,
            'user': {
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'role': user.role,
            },
        })
