import datetime
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole
from org.models import Category, Department, ActivityLog
from assets.models import Asset, AssetStatus, AssetCondition
from .models import Allocation, AllocationStatus, TransferRequest, TransferStatus

User = get_user_model()

class AssetFlowAllocationsTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.asset_manager = User.objects.create_user(
            username='asset_mgr', password='password123', role=UserRole.ASSET_MANAGER
        )
        self.dept_head = User.objects.create_user(
            username='dept_head', password='password123', role=UserRole.DEPT_HEAD
        )
        self.employee1 = User.objects.create_user(
            username='employee1', password='password123', role=UserRole.EMPLOYEE
        )
        self.employee2 = User.objects.create_user(
            username='employee2', password='password123', role=UserRole.EMPLOYEE
        )

        # Create supporting org models
        self.category = Category.objects.create(name='Laptops')
        self.department = Department.objects.create(name='Engineering')

        # Create asset
        self.asset = Asset.objects.create(
            name='ThinkPad P15',
            category=self.category,
            serial_number='SN-ALLOC-TEST',
            acquisition_date='2026-01-01',
            acquisition_cost='2000.00',
            condition=AssetCondition.NEW,
            is_bookable=False,
            status=AssetStatus.AVAILABLE,
            department=self.department
        )

    def test_allocation_workflow(self):
        """Test creating an allocation and returning it."""
        url = reverse('allocation-list')
        data = {
            'asset': self.asset.id,
            'employee': self.employee1.id,
            'department': self.department.id,
            'expected_return_date': (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        }

        # 1. Try allocating as standard employee (Forbidden)
        self.client.force_authenticate(user=self.employee1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Allocate as Dept Head (Allowed)
        self.client.force_authenticate(user=self.dept_head)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.ALLOCATED)

        # Verify activity log
        alloc_id = response.data['id']
        self.assertTrue(ActivityLog.objects.filter(action='ALLOCATE', target_model='Allocation', target_id=str(alloc_id)).exists())

        # 3. Double Allocation check (HTTP 409 Conflict with holder details)
        new_data = {
            'asset': self.asset.id,
            'employee': self.employee2.id,
            'department': self.department.id,
            'expected_return_date': (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        }
        response = self.client.post(url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['holder']['name'], self.employee1.username)
        self.assertEqual(response.data['holder']['department'], self.department.name)

        # 4. Return workflow (capture note and revert status)
        return_url = reverse('allocation-return-asset', args=[alloc_id])
        return_data = {'condition_note': 'Slightly scratched but functioning.'}
        response = self.client.post(return_url, return_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        allocation = Allocation.objects.get(id=alloc_id)
        self.assertEqual(allocation.status, AllocationStatus.RETURNED)
        self.assertEqual(allocation.condition_note, 'Slightly scratched but functioning.')
        self.assertEqual(allocation.returned_date, datetime.date.today())

        self.asset.refresh_from_db()
        self.assertEqual(self.asset.status, AssetStatus.AVAILABLE)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='RETURN', target_model='Allocation', target_id=str(alloc_id)).exists())

    def test_overdue_logic(self):
        """Verify the is_overdue property is correctly serialized."""
        self.client.force_authenticate(user=self.dept_head)
        url = reverse('allocation-list')
        
        # 1. Future return date (Not overdue)
        data_future = {
            'asset': self.asset.id,
            'employee': self.employee1.id,
            'expected_return_date': (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        }
        response = self.client.post(url, data_future, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['is_overdue'])

        # Revert asset status to allow another allocation
        alloc_id = response.data['id']
        self.client.post(reverse('allocation-return-asset', args=[alloc_id]))

        # 2. Past return date (Overdue)
        data_past = {
            'asset': self.asset.id,
            'employee': self.employee1.id,
            'expected_return_date': (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        }
        response = self.client.post(url, data_past, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_overdue'])

    def test_transfer_request_workflow(self):
        """Test submitting, approving, and rejecting transfer requests."""
        # Setup initial allocation
        self.client.force_authenticate(user=self.dept_head)
        url_alloc = reverse('allocation-list')
        data_alloc = {
            'asset': self.asset.id,
            'employee': self.employee1.id,
            'expected_return_date': (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        }
        response_alloc = self.client.post(url_alloc, data_alloc, format='json')
        old_alloc_id = response_alloc.data['id']

        # 1. Create a transfer request as employee1 (Allowed)
        self.client.force_authenticate(user=self.employee1)
        url_transfer = reverse('transfer-list')
        data_transfer = {
            'asset': self.asset.id,
            'to_employee': self.employee2.id,
            'reason': 'Moving to new project'
        }
        response_transfer = self.client.post(url_transfer, data_transfer, format='json')
        self.assertEqual(response_transfer.status_code, status.HTTP_201_CREATED)
        transfer_id = response_transfer.data['id']
        self.assertEqual(response_transfer.data['status'], TransferStatus.REQUESTED)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='TRANSFER_REQUEST', target_model='TransferRequest', target_id=str(transfer_id)).exists())

        # 2. Try to approve as standard employee (Forbidden)
        approve_url = reverse('transfer-approve', args=[transfer_id])
        response = self.client.post(approve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Approve as Asset Manager (Allowed)
        self.client.force_authenticate(user=self.asset_manager)
        response = self.client.post(approve_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], TransferStatus.APPROVED)

        # Check that old allocation was closed
        old_alloc = Allocation.objects.get(id=old_alloc_id)
        self.assertEqual(old_alloc.status, AllocationStatus.RETURNED)
        self.assertEqual(old_alloc.returned_date, datetime.date.today())
        self.assertIn("Transferred to employee2", old_alloc.condition_note)

        # Check that new allocation was created for employee2
        new_alloc = Allocation.objects.filter(asset=self.asset, employee=self.employee2, status=AllocationStatus.ACTIVE).first()
        self.assertIsNotNone(new_alloc)

        # Verify activity logs for transfer approve
        self.assertTrue(ActivityLog.objects.filter(action='TRANSFER_APPROVE', target_model='TransferRequest', target_id=str(transfer_id)).exists())

    def test_transfer_request_rejection(self):
        """Test rejecting a transfer request."""
        # Create transfer request
        self.client.force_authenticate(user=self.employee1)
        url_transfer = reverse('transfer-list')
        data_transfer = {
            'asset': self.asset.id,
            'to_employee': self.employee2.id,
            'reason': 'Temporary swap'
        }
        response_transfer = self.client.post(url_transfer, data_transfer, format='json')
        transfer_id = response_transfer.data['id']

        # Reject as Dept Head (Allowed)
        self.client.force_authenticate(user=self.dept_head)
        reject_url = reverse('transfer-reject', args=[transfer_id])
        response = self.client.post(reject_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], TransferStatus.REJECTED)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='TRANSFER_REJECT', target_model='TransferRequest', target_id=str(transfer_id)).exists())
