from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Task, TaskType, User
from .serializers import TaskSerializer, TaskAssignmentSerializer, TaskTypeSerializer, UserSerializer
from .forms import TaskForm


def home_view(request):
    return render(request, 'base.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'manager':
        task_list = Task.objects.all()
    else:
        task_list = Task.objects.filter(assigned_to=user)

    paginator = Paginator(task_list, 10) 
    page_number = request.GET.get('page')
    tasks = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {'tasks': tasks})



@login_required
def create_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            task.assigned_to.set(form.cleaned_data['assigned_to'])
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')