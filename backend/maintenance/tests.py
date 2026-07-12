from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole
from org.models import Category, ActivityLog
from assets.models import Asset, AssetStatus, AssetCondition
from .models import MaintenanceRequest, MaintenanceStatus, MaintenancePriority

User = get_user_model()

class AssetFlowMaintenanceTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.asset_manager = User.objects.create_user(
            username='asset_mgr', password='password123', role=UserRole.ASSET_MANAGER
        )
        self.employee = User.objects.create_user(
            username='employee', password='password123', role=UserRole.EMPLOYEE
        )
        self.technician = User.objects.create_user(
            username='technician', password='password123', role=UserRole.EMPLOYEE
        )

        # Create Category
        self.category = Category.objects.create(name='Electronics')

        # Create Asset
        self.asset = Asset.objects.create(
            name='Test Laptop',
            category=self.category,
            serial_number='SN-MAINT-TEST',
            acquisition_date='2026-01-01',
            acquisition_cost='1500.00',
            condition=AssetCondition.GOOD,
            is_bookable=False,
            status=AssetStatus.AVAILABLE
        )

    def test_workflow_ordering_validation(self):
        """Test model-level status transition constraints."""
        req = MaintenanceRequest.objects.create(
            asset=self.asset,
            raised_by=self.employee,
            issue_text='Flickering screen',
            priority=MaintenancePriority.HIGH
        )

        # 1. Try to start work immediately (PENDING -> IN_PROGRESS is blocked)
        with self.assertRaises(DjangoValidationError):
            req.transition(MaintenanceStatus.IN_PROGRESS)

        # 2. Try to resolve immediately (PENDING -> RESOLVED is blocked)
        with self.assertRaises(DjangoValidationError):
            req.transition(MaintenanceStatus.RESOLVED)

        # 3. PENDING -> APPROVED (Allowed)
        req.transition(MaintenanceStatus.APPROVED)
        self.assertEqual(req.status, MaintenanceStatus.APPROVED)

        # 4. APPROVED -> TECHNICIAN_ASSIGNED (Allowed)
        req.technician = self.technician
        req.transition(MaintenanceStatus.TECHNICIAN_ASSIGNED)
        self.assertEqual(req.status, MaintenanceStatus.TECHNICIAN_ASSIGNED)

        # 5. TECHNICIAN_ASSIGNED -> IN_PROGRESS (Allowed)
        req.transition(MaintenanceStatus.IN_PROGRESS)
        self.assertEqual(req.status, MaintenanceStatus.IN_PROGRESS)

        # 6. IN_PROGRESS -> RESOLVED (Allowed)
        req.transition(MaintenanceStatus.RESOLVED)
        self.assertEqual(req.status, MaintenanceStatus.RESOLVED)

    def test_maintenance_actions_endpoint_and_permissions(self):
        """Test API endpoints for approving, rejecting, assigning, starting, and resolving."""
        # 1. Raise request (Authenticated)
        self.client.force_authenticate(user=self.employee)
        url_list = reverse('maintenance-list')
        data_raise = {
            'asset': self.asset.id,
            'issue_text': 'Battery dies quickly',
            'priority': MaintenancePriority.MEDIUM
        }
        response = self.client.post(url_list, data_raise, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        req_id = response.data['id']

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='MAINTENANCE_RAISE', target_model='MaintenanceRequest', target_id=str(req_id)).exists())

        # 2. Try to approve as standard employee (Forbidden)
        approve_url = reverse('maintenance-approve', args=[req_id])
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Approve as Asset Manager (Allowed)
        self.client.force_authenticate(user=self.asset_manager)
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MaintenanceStatus.APPROVED)

        # Asset status should now be UNDER_MAINTENANCE
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.UNDER_MAINTENANCE)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='MAINTENANCE_APPROVE', target_model='MaintenanceRequest', target_id=str(req_id)).exists())

        # 4. Try to assign technician as standard employee (Forbidden)
        assign_url = reverse('maintenance-assign-technician', args=[req_id])
        assign_data = {'technician': self.technician.id}
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(assign_url, assign_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 5. Assign technician as Asset Manager (Allowed)
        self.client.force_authenticate(user=self.asset_manager)
        response = self.client.post(assign_url, assign_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MaintenanceStatus.TECHNICIAN_ASSIGNED)
        self.assertEqual(response.data['technician'], self.technician.id)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='MAINTENANCE_ASSIGN', target_model='MaintenanceRequest', target_id=str(req_id)).exists())

        # 6. Start work (Authenticated)
        start_url = reverse('maintenance-start-work', args=[req_id])
        self.client.force_authenticate(user=self.technician)
        response = self.client.post(start_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MaintenanceStatus.IN_PROGRESS)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='MAINTENANCE_START', target_model='MaintenanceRequest', target_id=str(req_id)).exists())

        # 7. Resolve work (Authenticated)
        resolve_url = reverse('maintenance-resolve', args=[req_id])
        response = self.client.post(resolve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MaintenanceStatus.RESOLVED)

        # Asset status should revert back to AVAILABLE
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.AVAILABLE)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='MAINTENANCE_RESOLVE', target_model='MaintenanceRequest', target_id=str(req_id)).exists())
