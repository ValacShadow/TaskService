import json

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Task, TaskType, User
from .serializers import TaskSerializer, TaskAssignmentSerializer, TaskTypeSerializer, UserSerializer, TaskCreateSerializer

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role', 'executive')

        if not all([username, password, email]):
            return Response({'status': 'error', 'message': 'Username, email, and password are required.'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': 'Username already taken'}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role
        )

        login(request, user)
        serializer = UserSerializer(user)
        return Response({'status': 'success', 'message': 'User registered and logged in', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class ListUsersAPIView(IsAuthenticated, APIView):
    def get(self, request):
        users = User.objects.all().only('id', 'username', 'email', 'role')
        serializer = UserSerializer(users, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


class TaskCreateAPIView(IsAuthenticated, APIView):
    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save(created_by=request.user)
            if 'assigned_to' in request.data:
                task.assigned_to.set(serializer.validated_data.get('assigned_to', []))
            return Response({'status': 'success', 'data': TaskSerializer(task).data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TaskAssignAPIView(IsAuthenticated, APIView):
    def patch(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
            if request.user.role != 'manager' and request.user != task.created_by:
                return Response({'status': 'error', 'message': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskAssignmentSerializer(data=request.data)
            if serializer.is_valid():
                user_ids = serializer.validated_data['user_ids']
                users = User.objects.filter(id__in=user_ids)
                if len(users) != len(user_ids):
                    return Response({'status': 'error', 'message': 'Some user IDs are invalid'}, status=status.HTTP_400_BAD_REQUEST)
                task.assigned_to.set(users)
                return Response({'status': 'success', 'message': 'Task assigned successfully', 'task': TaskSerializer(task).data}, status=status.HTTP_200_OK)
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({'status': 'error', 'message': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


class UserTasksAPIView(IsAuthenticated, APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        tasks = Task.objects.filter(assigned_to=user).prefetch_related('assigned_to', 'task_type')
        paginator = Paginator(tasks, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        serializer = TaskSerializer(page_obj, many=True)
        return Response({
            'status': 'success',
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class TaskTypeAPIView(IsAuthenticated, APIView):
    def get(self, request):
        task_types = TaskType.objects.all()
        serializer = TaskTypeSerializer(task_types, many=True)
        return Response({'status': 'success', 'data': serializer.data})


class TaskListAPIView(IsAuthenticated, APIView):
    def get(self, request):
        status_filter = request.GET.get("status")
        due_date_filter = request.GET.get("due_date")
        assignee_filter = request.GET.get("assignee")
        page_number = request.GET.get("page", 1)

        tasks = Task.objects.all()

        if status_filter:
            tasks = tasks.filter(status=status_filter)

        if due_date_filter:
            due_date_parsed = parse_date(due_date_filter)
            if due_date_parsed:
                tasks = tasks.filter(due_date__date=due_date_parsed)

        if assignee_filter:
            tasks = tasks.filter(assigned_to__id=assignee_filter)

        paginator = Paginator(tasks, 10)
        page_obj = paginator.get_page(page_number)
        serializer = TaskSerializer(page_obj, many=True)

        return Response({
            "status": "success",
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "tasks": serializer.data
        }, status=status.HTTP_200_OK)


class TaskTypesAPIView(IsAuthenticated, APIView):
    def get(self, request):
        task_types = TaskType.objects.all()
        serializer = TaskTypeSerializer(task_types, many=True)
        return Response({"task_types": serializer.data}, status=status.HTTP_200_OK)


class TaskStatusUpdateAPIView(IsAuthenticated, APIView):
    def patch(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status is None:
            return Response(
                {'status': 'error', 'errors': {'status': ['This field is required.']}},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = new_status
        task.save()
        return Response(
            {'status': 'success', 'message': 'Task status updated successfully.'},
            status=status.HTTP_200_OK
        )
