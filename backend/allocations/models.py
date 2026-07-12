import datetime
from django.db import models
from django.conf import settings

class AllocationStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    RETURNED = 'RETURNED', 'Returned'

class Allocation(models.Model):
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocations'
    )
    department = models.ForeignKey(
        'org.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='allocations'
    )
    allocated_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    condition_note = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AllocationStatus.choices,
        default=AllocationStatus.ACTIVE
    )

    @property
    def is_overdue(self):
        return (
            self.status == AllocationStatus.ACTIVE and 
            self.expected_return_date < datetime.date.today()
        )

    def __str__(self):
        return f"Allocation of {self.asset.tag} to {self.employee} ({self.status})"

class TransferStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Requested'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'

class TransferRequest(models.Model):
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='transfer_requests'
    )
    from_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_transfers'
    )
    to_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_transfers'
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.REQUESTED
    )

    def __str__(self):
        return f"Transfer of {self.asset.tag} from {self.from_employee} to {self.to_employee} ({self.status})"
