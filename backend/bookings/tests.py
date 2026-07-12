from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import datetime

from users.models import UserRole
from org.models import Category, ActivityLog
from assets.models import Asset, AssetStatus, AssetCondition
from .models import Booking, BookingStatus
from .utils import update_booking_statuses

User = get_user_model()

class AssetFlowBookingsTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.employee = User.objects.create_user(
            username='employee', password='password123', role=UserRole.EMPLOYEE
        )

        # Create supporting category
        self.category = Category.objects.create(name='Meeting Rooms')

        # Create bookable asset
        self.bookable_room = Asset.objects.create(
            name='Conference Room A',
            category=self.category,
            serial_number='ROOM-A',
            acquisition_date='2026-01-01',
            acquisition_cost='50000.00',
            condition=AssetCondition.NEW,
            is_bookable=True,
            status=AssetStatus.AVAILABLE
        )

        # Create non-bookable asset
        self.non_bookable_room = Asset.objects.create(
            name='Conference Room B',
            category=self.category,
            serial_number='ROOM-B',
            acquisition_date='2026-01-01',
            acquisition_cost='40000.00',
            condition=AssetCondition.NEW,
            is_bookable=False,
            status=AssetStatus.AVAILABLE
        )

    def test_booking_non_bookable_resource_fails(self):
        """Verify bookings cannot be created on non-bookable resources."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('booking-list')
        
        now = timezone.now()
        data = {
            'resource': self.non_bookable_room.id,
            'start_time': (now + datetime.timedelta(hours=1)).isoformat(),
            'end_time': (now + datetime.timedelta(hours=2)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not marked as bookable", response.data['resource'][0])

    def test_booking_overlaps_and_boundaries(self):
        """Test that overlaps are rejected, but exact boundaries are allowed."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('booking-list')
        
        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        
        # Create base booking: 10:00 to 12:00 (base_time + 10 hours to + 12 hours)
        t10 = base_time + datetime.timedelta(hours=10)
        t12 = base_time + datetime.timedelta(hours=12)
        
        data_base = {
            'resource': self.bookable_room.id,
            'start_time': t10.isoformat(),
            'end_time': t12.isoformat()
        }
        response = self.client.post(url, data_base, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        booking_id = response.data['id']

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='BOOK', target_model='Booking', target_id=str(booking_id)).exists())

        # Test overlap: 11:00 to 13:00 (overlapping 10:00-12:00)
        t11 = base_time + datetime.timedelta(hours=11)
        t13 = base_time + datetime.timedelta(hours=13)
        data_overlap1 = {
            'resource': self.bookable_room.id,
            'start_time': t11.isoformat(),
            'end_time': t13.isoformat()
        }
        response = self.client.post(url, data_overlap1, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test overlap: 09:00 to 11:00 (overlapping 10:00-12:00)
        t9 = base_time + datetime.timedelta(hours=9)
        data_overlap2 = {
            'resource': self.bookable_room.id,
            'start_time': t9.isoformat(),
            'end_time': t11.isoformat()
        }
        response = self.client.post(url, data_overlap2, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test overlap: 10:30 to 11:30 (fully nested)
        t10_30 = base_time + datetime.timedelta(hours=10, minutes=30)
        t11_30 = base_time + datetime.timedelta(hours=11, minutes=30)
        data_overlap3 = {
            'resource': self.bookable_room.id,
            'start_time': t10_30.isoformat(),
            'end_time': t11_30.isoformat()
        }
        response = self.client.post(url, data_overlap3, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test boundary case: 08:00 to 10:00 (Ends exactly when base starts -> ALLOWED)
        t8 = base_time + datetime.timedelta(hours=8)
        data_boundary_before = {
            'resource': self.bookable_room.id,
            'start_time': t8.isoformat(),
            'end_time': t10.isoformat()
        }
        response = self.client.post(url, data_boundary_before, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test boundary case: 12:00 to 14:00 (Starts exactly when base ends -> ALLOWED)
        t14 = base_time + datetime.timedelta(hours=14)
        data_boundary_after = {
            'resource': self.bookable_room.id,
            'start_time': t12.isoformat(),
            'end_time': t14.isoformat()
        }
        response = self.client.post(url, data_boundary_after, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_resource_bookings_calendar(self):
        """Test GET /resources/{id}/bookings/ returns calendar friendly structure."""
        self.client.force_authenticate(user=self.employee)
        
        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        t10 = base_time + datetime.timedelta(hours=10)
        t12 = base_time + datetime.timedelta(hours=12)

        Booking.objects.create(
            resource=self.bookable_room,
            start_time=t10,
            end_time=t12,
            booked_by=self.employee,
            status=BookingStatus.UPCOMING
        )

        url = reverse('resource-bookings', args=[self.bookable_room.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['booked_by'], self.employee.username)
        self.assertEqual(response.data[0]['status'], BookingStatus.UPCOMING)

    def test_booking_cancellation(self):
        """Test cancellation and asset status reversion."""
        self.client.force_authenticate(user=self.employee)
        
        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        t10 = base_time + datetime.timedelta(hours=10)
        t12 = base_time + datetime.timedelta(hours=12)

        booking = Booking.objects.create(
            resource=self.bookable_room,
            start_time=t10,
            end_time=t12,
            booked_by=self.employee,
            status=BookingStatus.ONGOING
        )
        self.bookable_room.status = AssetStatus.RESERVED
        self.bookable_room.save()

        # Cancel the booking
        url_cancel = reverse('booking-cancel', args=[booking.id])
        response = self.client.post(url_cancel)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

        # Check resource reverted back to AVAILABLE
        self.bookable_room.refresh_from_db()
        self.assertEqual(self.bookable_room.status, AssetStatus.AVAILABLE)

        # Verify activity logs
        self.assertTrue(ActivityLog.objects.filter(action='BOOKING_CANCEL', target_model='Booking', target_id=str(booking.id)).exists())

    def test_flip_booking_statuses_util(self):
        """Test that the update_booking_statuses scheduler transitions work."""
        now = timezone.now()
        
        # 1. Booking starting now, ending in 1 hour -> should transition to ONGOING
        booking1 = Booking.objects.create(
            resource=self.bookable_room,
            start_time=now - datetime.timedelta(minutes=5),
            end_time=now + datetime.timedelta(hours=1),
            booked_by=self.employee,
            status=BookingStatus.UPCOMING
        )
        self.bookable_room.status = AssetStatus.AVAILABLE
        self.bookable_room.save()

        # Create another bookable asset to test completion isolation
        bookable_room_b = Asset.objects.create(
            name='Conference Room C',
            category=self.category,
            serial_number='ROOM-C',
            acquisition_date='2026-01-01',
            acquisition_cost='30000.00',
            condition=AssetCondition.NEW,
            is_bookable=True,
            status=AssetStatus.RESERVED
        )

        # 2. Booking that ended 5 minutes ago -> should transition to COMPLETED
        booking2 = Booking.objects.create(
            resource=bookable_room_b,
            start_time=now - datetime.timedelta(hours=2),
            end_time=now - datetime.timedelta(minutes=5),
            booked_by=self.employee,
            status=BookingStatus.ONGOING
        )

        update_booking_statuses()

        booking1.refresh_from_db()
        booking2.refresh_from_db()

        self.assertEqual(booking1.status, BookingStatus.ONGOING)
        self.assertEqual(booking2.status, BookingStatus.COMPLETED)

        # Check that self.bookable_room is RESERVED (due to booking1 being ongoing)
        self.bookable_room.refresh_from_db()
        self.assertEqual(self.bookable_room.status, AssetStatus.RESERVED)

        # Check that bookable_room_b is AVAILABLE (due to booking2 being completed)
        bookable_room_b.refresh_from_db()
        self.assertEqual(bookable_room_b.status, AssetStatus.AVAILABLE)
