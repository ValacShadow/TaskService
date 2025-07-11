from rest_framework import serializers
from .models import Task, TaskType, User


class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class TaskSerializer(serializers.ModelSerializer):
    task_type = TaskTypeSerializer()
    assigned_to = UserSerializer(many=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description', 'created_at', 
            'task_type', 'due_date', 'status', 'completed_at', 
            'created_by', 'assigned_to'
        ]
        read_only_fields = ['created_by', 'created_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    task_type = serializers.PrimaryKeyRelatedField(
        queryset=TaskType.objects.all(),
        required=False,
        allow_null=True 
    )

    class Meta:
        model = Task
        fields = [
            'name', 'description', 'due_date', 'status', 'task_type', 'assigned_to'
        ]



class TaskAssignmentSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )

    def validate_user_ids(self, value):
        if not User.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("Invalid user IDs provided")
        return value