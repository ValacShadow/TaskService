from django.urls import path
from . import views, apis

urlpatterns = [
    # Existing template URLs
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API Endpoints
    path('api/register/', apis.RegisterAPIView.as_view(), name='api-create-user'),
    path('api/users/', apis.ListUsersAPIView.as_view(), name='api-get-users'),
    path('api/tasks/add', apis.TaskCreateAPIView.as_view(), name='api-create-task'),
    path("api/tasks/", apis.TaskListAPIView.as_view(), name="api-tasks"),
    path('api/tasks/<int:task_id>/assign/', apis.TaskAssignAPIView.as_view(), name='api-assign-task'),
    path('api/users/<int:user_id>/tasks/', apis.UserTasksAPIView.as_view(), name='api-user-tasks'),
    path('api/task-types/', apis.TaskTypesAPIView.as_view(), name='api-task-types'),
    path('api/tasks/<task_id>/update-status/', apis.TaskStatusUpdateAPIView.as_view(), name='api-update-status'),

]