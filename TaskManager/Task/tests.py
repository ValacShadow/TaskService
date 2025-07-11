from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Task, TaskType

User = get_user_model()

class TaskAppTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.task_type = TaskType.objects.create(name="Bug")

        self.manager = User.objects.create_user(
            username='manager1', password='managerpass', role='manager', email='manager@example.com'
        )
        self.executive = User.objects.create_user(
            username='executive1', password='executivepass', role='executive', email='executive@example.com'
        )

        self.task = Task.objects.create(
            title="Fix Bug",
            description="Fix the login bug",
            created_by=self.manager,
            due_date="2025-07-30",
            task_type=self.task_type,
            status='pending'
        )
        self.task.assigned_to.set([self.executive])

    def test_user_registration_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'role': 'executive'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_manager_can_see_all_tasks(self):
        self.client.login(username='manager1', password='managerpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fix Bug")

    def test_executive_can_see_only_assigned_tasks(self):
        self.client.login(username='executive1', password='executivepass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fix Bug")

        # Create a second task not assigned to executive
        task2 = Task.objects.create(
            name="Unassigned Task",
            description="Should not be visible",
            created_by=self.manager,
            due_date="2025-08-10",
            task_type=self.task_type
        )
        response = self.client.get(reverse('dashboard'))
        self.assertNotContains(response, "Unassigned Task")

    def test_manager_can_create_task(self):
        self.client.login(username='manager1', password='managerpass')
        response = self.client.post(reverse('create_task'), {
            'title': 'New Task',
            'description': 'A test task',
            'due_date': '2025-08-01',
            'task_type': self.task_type.id,
            'assigned_to': [self.executive.id],
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_executive_cannot_create_task(self):
        self.client.login(username='executive1', password='executivepass')
        response = self.client.post(reverse('create_task'), {
            'title': 'Invalid Task',
            'description': 'Should not be created',
            'due_date': '2025-08-01',
            'task_type': self.task_type.id,
            'assigned_to': [self.executive.id],
            'status': 'pending'
        })
        # View should redirect or block creation
        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(title='Invalid Task').exists())

    def test_login_view_valid_and_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'manager1',
            'password': 'managerpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

        response = self.client.post(reverse('login'), {
            'username': 'manager1',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')
