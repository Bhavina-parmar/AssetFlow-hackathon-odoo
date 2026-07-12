from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class MaintenancePriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'

class MaintenanceStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    TECHNICIAN_ASSIGNED = 'TECHNICIAN_ASSIGNED', 'Technician Assigned'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    RESOLVED = 'RESOLVED', 'Resolved'

class MaintenanceRequest(models.Model):
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='raised_maintenance'
    )
    issue_text = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=MaintenancePriority.choices,
        default=MaintenancePriority.MEDIUM
    )
    photo = models.ImageField(upload_to='maintenance_photos/', null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )

    def transition(self, new_status):
        """
        Validates and transitions the maintenance status based on the workflow rules:
        - PENDING -> APPROVED, REJECTED
        - APPROVED -> TECHNICIAN_ASSIGNED
        - TECHNICIAN_ASSIGNED -> IN_PROGRESS
        - IN_PROGRESS -> RESOLVED
        Raises ValidationError if transition is not allowed.
        """
        if new_status not in MaintenanceStatus.values:
            raise ValidationError(f"Invalid status: {new_status}")

        if self.status == new_status:
            return  # No change

        allowed = {
            MaintenanceStatus.PENDING: [MaintenanceStatus.APPROVED, MaintenanceStatus.REJECTED],
            MaintenanceStatus.APPROVED: [MaintenanceStatus.TECHNICIAN_ASSIGNED],
            MaintenanceStatus.TECHNICIAN_ASSIGNED: [MaintenanceStatus.IN_PROGRESS],
            MaintenanceStatus.IN_PROGRESS: [MaintenanceStatus.RESOLVED],
            MaintenanceStatus.REJECTED: [],
            MaintenanceStatus.RESOLVED: []
        }

        if new_status not in allowed.get(self.status, []):
            raise ValidationError(f"Cannot transition maintenance request from {self.status} to {new_status}.")

        self.status = new_status
        self.save()

    def __str__(self):
        return f"Request for {self.asset.tag} - Status: {self.status}"
