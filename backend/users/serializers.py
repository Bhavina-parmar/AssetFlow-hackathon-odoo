from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Minimal serializer — used for nested references."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'role']

    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class UserDetailSerializer(serializers.ModelSerializer):
    """Full serializer for employee directory."""
    name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    # Accept department as write-only id (stored on profile separately if needed)
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'name', 'role', 'is_active', 'status', 'department',
        ]
        read_only_fields = ['is_active', 'status']

    def get_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_status(self, obj):
        return 'Active' if obj.is_active else 'Inactive'

    def get_department(self, obj):
        # Check if user heads any department
        dept = getattr(obj, 'headed_departments', None)
        if dept is not None:
            first = dept.first()
            if first:
                return {'id': first.id, 'name': first.name}
        return None
