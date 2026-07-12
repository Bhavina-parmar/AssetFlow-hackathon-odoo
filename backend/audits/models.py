from django.db import models
from django.conf import settings

class AuditCycleStatus(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    CLOSED = 'CLOSED', 'Closed'

class AuditResult(models.TextChoices):
    VERIFIED = 'VERIFIED', 'Verified'
    MISSING = 'MISSING', 'Missing'
    DAMAGED = 'DAMAGED', 'Damaged'

class AuditCycle(models.Model):
    scope_department = models.ForeignKey(
        'org.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_cycles'
    )
    scope_location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=AuditCycleStatus.choices,
        default=AuditCycleStatus.OPEN
    )
    auditors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='audit_cycles'
    )

    def __str__(self):
        return f"Audit Cycle {self.id} (Status: {self.status})"

class AuditItem(models.Model):
    cycle = models.ForeignKey(
        AuditCycle,
        on_delete=models.CASCADE,
        related_name='items'
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='audit_items'
    )
    result = models.CharField(
        max_length=20,
        choices=AuditResult.choices,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Audit Item {self.id} - Asset: {self.asset.tag} - Result: {self.result}"
