from django.db import models
from django.core.exceptions import ValidationError

class AssetStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    ALLOCATED = 'ALLOCATED', 'Allocated'
    RESERVED = 'RESERVED', 'Reserved'
    UNDER_MAINTENANCE = 'UNDER_MAINTENANCE', 'Under Maintenance'
    LOST = 'LOST', 'Lost'
    RETIRED = 'RETIRED', 'Retired'
    DISPOSED = 'DISPOSED', 'Disposed'

class AssetCondition(models.TextChoices):
    NEW = 'NEW', 'New'
    GOOD = 'GOOD', 'Good'
    FAIR = 'FAIR', 'Fair'
    POOR = 'POOR', 'Poor'
    DAMAGED = 'DAMAGED', 'Damaged'

class Asset(models.Model):
    tag = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        'org.Category',
        on_delete=models.CASCADE,
        related_name='assets'
    )
    serial_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2)
    condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        default=AssetCondition.NEW
    )
    location = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(upload_to='asset_photos/', null=True, blank=True)
    is_bookable = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30,
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE
    )
    department = models.ForeignKey(
        'org.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )

    def transition(self, new_status):
        """
        Validates and transitions the status of the asset based on the allowed transitions map.
        Raises ValidationError if transition is not allowed.
        """
        if new_status not in AssetStatus.values:
            raise ValidationError(f"Invalid status: {new_status}")

        if self.status == new_status:
            return  # No change

        # Explicit allowed transitions map
        allowed = {
            AssetStatus.AVAILABLE: [
                AssetStatus.ALLOCATED, AssetStatus.RESERVED, AssetStatus.UNDER_MAINTENANCE,
                AssetStatus.LOST, AssetStatus.RETIRED, AssetStatus.DISPOSED
            ],
            AssetStatus.ALLOCATED: [
                AssetStatus.AVAILABLE, AssetStatus.UNDER_MAINTENANCE, AssetStatus.LOST,
                AssetStatus.RETIRED, AssetStatus.DISPOSED
            ],
            AssetStatus.RESERVED: [
                AssetStatus.ALLOCATED, AssetStatus.AVAILABLE, AssetStatus.LOST, AssetStatus.RETIRED
            ],
            AssetStatus.UNDER_MAINTENANCE: [
                AssetStatus.AVAILABLE, AssetStatus.LOST, AssetStatus.RETIRED, AssetStatus.DISPOSED
            ],
            AssetStatus.LOST: [
                AssetStatus.AVAILABLE, AssetStatus.RETIRED, AssetStatus.DISPOSED
            ],
            AssetStatus.RETIRED: [
                AssetStatus.DISPOSED
            ],
            AssetStatus.DISPOSED: []
        }

        if new_status not in allowed.get(self.status, []):
            raise ValidationError(f"Cannot transition asset from {self.status} to {new_status}.")

        self.status = new_status
        self.save()

    def save(self, *args, **kwargs):
        if not self.tag:
            import re
            max_num = 0
            # Look up existing assets to find the next tag sequence number
            tags = Asset.objects.filter(tag__startswith='AF-').values_list('tag', flat=True)
            for t in tags:
                match = re.match(r'^AF-(\d+)$', t)
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num
            self.tag = f"AF-{max_num + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.tag})"
