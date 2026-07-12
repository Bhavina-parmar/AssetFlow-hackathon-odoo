from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import datetime

from users.models import UserRole
from org.models import Category, Department
from assets.models import Asset, AssetStatus, AssetCondition
from allocations.models import Allocation, AllocationStatus
from bookings.models import Booking, BookingStatus
from maintenance.models import MaintenanceRequest, MaintenancePriority
from .models import ActivityLog
from .utils import log_activity

User = get_user_model()

class AssetFlowActivityTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.employee = User.objects.create_user(
            username='employee', password='password123', role=UserRole.EMPLOYEE
        )
        self.other_employee = User.objects.create_user(
            username='other_employee', password='password123', role=UserRole.EMPLOYEE
        )

        # Create Category
        self.category = Category.objects.create(name='Computers')

        # Create Assets
        self.asset_avail = Asset.objects.create(
            name='Laptop Avail', category=self.category, serial_number='SN-KPI-1',
            acquisition_date='2026-01-01', acquisition_cost='1000.00',
            condition=AssetCondition.GOOD, is_bookable=True, status=AssetStatus.AVAILABLE
        )
        self.asset_alloc = Asset.objects.create(
            name='Laptop Alloc', category=self.category, serial_number='SN-KPI-2',
            acquisition_date='2026-01-01', acquisition_cost='1200.00',
            condition=AssetCondition.GOOD, is_bookable=False, status=AssetStatus.ALLOCATED
        )
        self.asset_maint = Asset.objects.create(
            name='Laptop Maint', category=self.category, serial_number='SN-KPI-3',
            acquisition_date='2026-01-01', acquisition_cost='1400.00',
            condition=AssetCondition.GOOD, is_bookable=False, status=AssetStatus.UNDER_MAINTENANCE
        )

        # Create Allocation (Overdue Return)
        self.overdue_alloc = Allocation.objects.create(
            asset=self.asset_alloc,
            employee=self.employee,
            allocated_date=datetime.date.today() - datetime.timedelta(days=10),
            expected_return_date=datetime.date.today() - datetime.timedelta(days=2),
            status=AllocationStatus.ACTIVE
        )

        # Create Booking (Ongoing Booking)
        self.ongoing_booking = Booking.objects.create(
            resource=self.asset_avail,
            start_time=timezone.now() - datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=1),
            booked_by=self.employee,
            status=BookingStatus.ONGOING
        )

        # Create Booking for other user
        self.other_booking = Booking.objects.create(
            resource=self.asset_avail,
            start_time=timezone.now() - datetime.timedelta(hours=1),
            end_time=timezone.now() + datetime.timedelta(hours=1),
            booked_by=self.other_employee,
            status=BookingStatus.UPCOMING
        )

        # Create Maintenance Request
        self.maint_req = MaintenanceRequest.objects.create(
            asset=self.asset_maint,
            raised_by=self.employee,
            issue_text='Broken keyboard',
            priority=MaintenancePriority.HIGH
        )

    def test_bridge_log_activity(self):
        """Verify the log_activity helper creates ActivityLog model records correctly."""
        log_entry = log_activity(
            self.employee, 
            'TEST_ACTION', 
            self.asset_avail, 
            description="Logged a test action."
        )

        self.assertEqual(ActivityLog.objects.count(), 1)
        self.assertEqual(log_entry.actor, self.employee)
        self.assertEqual(log_entry.action, 'TEST_ACTION')
        self.assertEqual(log_entry.target_type, 'Asset')
        self.assertEqual(log_entry.target_id, str(self.asset_avail.id))
        self.assertEqual(log_entry.meta.get('description'), "Logged a test action.")

    def test_dashboard_kpis(self):
        """Verify dashboard KPIs counts and overdue serialization matches."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('dashboard-kpis')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['available_count'], 1)
        self.assertEqual(response.data['allocated_count'], 1)
        self.assertEqual(response.data['maintenance_count'], 1)
        self.assertEqual(response.data['active_bookings_count'], 1)
        self.assertEqual(len(response.data['overdue_returns']), 1)
        self.assertEqual(response.data['overdue_returns'][0]['id'], self.overdue_alloc.id)

    def test_utilization_report(self):
        """Verify utilization report detects most-used and idle assets correctly."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('report-utilization')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.asset_avail has 1 booking, self.asset_alloc has 1 allocation.
        # self.asset_maint has 0 bookings/allocations -> should be idle.
        most_used_tags = [x['tag'] for x in response.data['most_used']]
        self.assertIn(self.asset_avail.tag, most_used_tags)
        self.assertIn(self.asset_alloc.tag, most_used_tags)

        idle_tags = [x['tag'] for x in response.data['idle']]
        self.assertIn(self.asset_maint.tag, idle_tags)

    def test_maintenance_frequency_report(self):
        """Verify maintenance request counts are grouped correctly."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('report-maintenance')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # We raised 1 request on self.asset_maint (which has category self.category)
        by_asset = response.data['by_asset']
        asset_stat = next(x for x in by_asset if x['id'] == self.asset_maint.id)
        self.assertEqual(asset_stat['maintenance_count'], 1)

        by_cat = response.data['by_category']
        cat_stat = next(x for x in by_cat if x['id'] == self.category.id)
        self.assertEqual(cat_stat['maintenance_count'], 1)

    def test_notifications_filtering(self):
        """Verify notifications are correctly filtered for admins and normal users."""
        # Create a log for self.employee
        log_activity(self.employee, 'ALLOCATE', self.overdue_alloc, "Allocated to self.")
        # Create a log for other_employee on other_booking
        log_activity(self.other_employee, 'BOOK', self.other_booking, "Booked by other.")

        # 1. Admin user request -> sees all logs (2 logs)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)

        # 2. self.employee request -> sees their own events (e.g. self.overdue_alloc allocation)
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actions = [x['action'] for x in response.data]
        self.assertIn('ALLOCATE', actions)
        # self.employee should NOT see other_employee's logs if they aren't linked to them
        self.assertNotIn('other_employee', [x.get('actor_name') for x in response.data])
