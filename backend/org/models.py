from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class DepartmentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    status = models.CharField(
        max_length=20,
        choices=DepartmentStatus.choices,
        default=DepartmentStatus.ACTIVE
    )

    def transition(self, new_status):
        """
        Validates and performs a transition to a new status.
        Raises ValidationError if transition is not allowed.
        """
        if new_status not in DepartmentStatus.values:
            raise ValidationError(f"Invalid status: {new_status}")

        if self.status == new_status:
            return  # No change required

        # Active <-> Inactive transitions are allowed, but we explicitly validate it
        allowed = {
            DepartmentStatus.ACTIVE: [DepartmentStatus.INACTIVE],
            DepartmentStatus.INACTIVE: [DepartmentStatus.ACTIVE]
        }

        if new_status not in allowed.get(self.status, []):
            raise ValidationError(f"Cannot transition department status from {self.status} to {new_status}.")

        self.status = new_status
        self.save()

    def __str__(self):
        return f"{self.name} ({self.status})"

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    extra_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class ActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=100)  # e.g., 'CREATE', 'UPDATE', 'ACTIVATE', 'DEACTIVATE'
    target_model = models.CharField(max_length=100)  # e.g., 'Department', 'Category'
    target_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.target_model} {self.target_id} at {self.timestamp}"
