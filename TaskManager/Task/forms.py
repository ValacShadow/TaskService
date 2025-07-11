from django import forms
from .models import Task, TaskType, User


class TaskForm(forms.ModelForm):
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.all())
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Task
        fields = ['name', 'description', 'task_type', 'due_date', 'status', 'assigned_to']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }