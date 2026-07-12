from django.utils import timezone
from django.db import transaction
from bookings.models import Booking, BookingStatus
from assets.models import AssetStatus
from org.utils import log_activity

def update_booking_statuses():
    """
    Scans bookings and transitions status:
    - UPCOMING -> ONGOING (if start_time <= now < end_time)
    - ONGOING or UPCOMING -> COMPLETED (if end_time <= now)
    Also transitions the underlying bookable asset's status:
    - AVAILABLE -> RESERVED (when booking becomes ONGOING)
    - RESERVED -> AVAILABLE (when booking becomes COMPLETED)
    """
    now = timezone.now()

    with transaction.atomic():
        # 1. UPCOMING -> ONGOING
        upcoming_to_ongoing = Booking.objects.filter(
            status=BookingStatus.UPCOMING,
            start_time__lte=now,
            end_time__gt=now
        )
        for booking in upcoming_to_ongoing:
            booking.status = BookingStatus.ONGOING
            booking.save()
            log_activity(
                None, 
                'STATUS_CHANGE', 
                booking, 
                f"Booking transitioned to ONGOING (start_time passed)."
            )

            # Try to transition resource to RESERVED
            asset = booking.resource
            if asset.status == AssetStatus.AVAILABLE:
                try:
                    asset.transition(AssetStatus.RESERVED)
                    log_activity(
                        None, 
                        'STATUS_CHANGE', 
                        asset, 
                        f"Asset transitioned to RESERVED due to ongoing booking."
                    )
                except Exception:
                    pass

        # 2. ONGOING or UPCOMING -> COMPLETED
        active_to_completed = Booking.objects.filter(
            status__in=[BookingStatus.UPCOMING, BookingStatus.ONGOING],
            end_time__lte=now
        )
        for booking in active_to_completed:
            old_status = booking.status
            booking.status = BookingStatus.COMPLETED
            booking.save()
            log_activity(
                None, 
                'STATUS_CHANGE', 
                booking, 
                f"Booking transitioned from {old_status} to COMPLETED (end_time passed)."
            )

            # Try to transition resource back to AVAILABLE
            asset = booking.resource
            if asset.status == AssetStatus.RESERVED:
                try:
                    asset.transition(AssetStatus.AVAILABLE)
                    log_activity(
                        None, 
                        'STATUS_CHANGE', 
                        asset, 
                        f"Asset transitioned to AVAILABLE due to completed booking."
                    )
                except Exception:
                    pass
