from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, TaskType

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'mobile')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Task)
admin.site.register(TaskType)