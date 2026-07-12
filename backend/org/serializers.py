from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserRole
from .models import Department, Category

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'head', 'parent', 'status']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None

        # Department head assignment validation (Admin-only)
        if 'head' in attrs:
            new_head = attrs['head']
            is_changed = False
            if self.instance:
                if self.instance.head != new_head:
                    is_changed = True
            else:
                if new_head is not None:
                    is_changed = True

            if is_changed:
                if not (user and user.is_authenticated and user.role == UserRole.ADMIN):
                    raise serializers.ValidationError({
                        "head": "Only ADMIN users can assign or change the department head."
                    })

        # Prevent a department from being its own parent
        parent = attrs.get('parent')
        if parent and self.instance and parent.id == self.instance.id:
            raise serializers.ValidationError({
                "parent": "A department cannot be its own parent."
            })

        return attrs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'extra_fields']
