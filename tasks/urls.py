from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskStatusUpdateView, DashboardView

app_name = 'tasks'

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/status/', TaskStatusUpdateView.as_view(), name='task_status'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
