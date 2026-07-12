from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    ASSET_MANAGER = 'ASSET_MANAGER', 'Asset Manager'
    DEPT_HEAD = 'DEPT_HEAD', 'Department Head'
    EMPLOYEE = 'EMPLOYEE', 'Employee'

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
