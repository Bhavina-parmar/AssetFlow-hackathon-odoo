from django.db import models
from django.conf import settings

class BookingStatus(models.TextChoices):
    UPCOMING = 'UPCOMING', 'Upcoming'
    ONGOING = 'ONGOING', 'Ongoing'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Booking(models.Model):
    resource = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.UPCOMING
    )

    def __str__(self):
        return f"Booking of {self.resource.tag} by {self.booked_by} ({self.status})"
