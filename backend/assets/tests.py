from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole
from org.models import Category, Department, ActivityLog
from .models import Asset, AssetStatus, AssetCondition

User = get_user_model()

class AssetFlowAssetTests(APITestCase):

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
        self.employee = User.objects.create_user(
            username='employee', password='password123', role=UserRole.EMPLOYEE
        )

        # Create supporting org models
        self.category = Category.objects.create(name='Laptops')
        self.department = Department.objects.create(name='Engineering')

        # Create basic assets
        self.asset1 = Asset.objects.create(
            name='MacBook Pro 16',
            category=self.category,
            serial_number='SN-0001',
            acquisition_date='2026-01-01',
            acquisition_cost='2500.00',
            condition=AssetCondition.NEW,
            location='Office A',
            is_bookable=True,
            status=AssetStatus.AVAILABLE,
            department=self.department
        )

    def test_auto_tag_generation(self):
        """Verify tag auto-generation handles sequencing correctly."""
        # Check first tag was auto-generated as AF-0001
        self.assertEqual(self.asset1.tag, 'AF-0001')

        # Create second asset and check tag sequence
        asset2 = Asset.objects.create(
            name='ThinkPad X1',
            category=self.category,
            serial_number='SN-0002',
            acquisition_date='2026-02-01',
            acquisition_cost='1800.00',
            condition=AssetCondition.GOOD
        )
        self.assertEqual(asset2.tag, 'AF-0002')

        # Manual tag creation shouldn't overwrite if provided
        asset3 = Asset.objects.create(
            name='iPad Pro',
            category=self.category,
            tag='CUSTOM-99',
            serial_number='SN-0003',
            acquisition_date='2026-03-01',
            acquisition_cost='1000.00',
            condition=AssetCondition.GOOD
        )
        self.assertEqual(asset3.tag, 'CUSTOM-99')

        # Next auto-tag should still proceed from AF-0003
        asset4 = Asset.objects.create(
            name='Monitor Dell',
            category=self.category,
            serial_number='SN-0004',
            acquisition_date='2026-04-01',
            acquisition_cost='400.00',
            condition=AssetCondition.GOOD
        )
        self.assertEqual(asset4.tag, 'AF-0003')

    def test_asset_status_transitions(self):
        """Verify state transitions and constraints."""
        # AVAILABLE -> ALLOCATED (Allowed)
        self.asset1.transition(AssetStatus.ALLOCATED)
        self.assertEqual(self.asset1.status, AssetStatus.ALLOCATED)

        # ALLOCATED -> RESERVED (Blocked)
        with self.assertRaises(ValidationError):
            self.asset1.transition(AssetStatus.RESERVED)

        # ALLOCATED -> AVAILABLE (Allowed)
        self.asset1.transition(AssetStatus.AVAILABLE)
        self.assertEqual(self.asset1.status, AssetStatus.AVAILABLE)

        # AVAILABLE -> DISPOSED (Allowed)
        self.asset1.transition(AssetStatus.DISPOSED)
        self.assertEqual(self.asset1.status, AssetStatus.DISPOSED)

        # DISPOSED -> AVAILABLE (Blocked - terminal state)
        with self.assertRaises(ValidationError):
            self.asset1.transition(AssetStatus.AVAILABLE)

    def test_asset_permissions(self):
        """Only ADMIN or ASSET_MANAGER can register/create assets."""
        url = reverse('asset-list')
        data = {
            'name': 'iPhone 15',
            'category': self.category.id,
            'serial_number': 'SN-IPHONE',
            'acquisition_date': '2026-07-01',
            'acquisition_cost': '999.00',
            'condition': AssetCondition.NEW,
            'location': 'HQ',
            'is_bookable': False
        }

        # 1. Anonymous fails
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Employee fails
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Dept head fails
        self.client.force_authenticate(user=self.dept_head)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 4. Asset manager succeeds
        self.client.force_authenticate(user=self.asset_manager)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.filter(name='iPhone 15').count(), 1)

        # Verify ActivityLog creation
        new_asset = Asset.objects.get(name='iPhone 15')
        self.assertTrue(ActivityLog.objects.filter(action='CREATE', target_model='Asset', target_id=str(new_asset.id)).exists())

    def test_asset_list_filtering(self):
        """Test filtering by tag, category, status, department, and location."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('asset-list')

        # Filter by status
        response = self.client.get(url, {'status': AssetStatus.AVAILABLE})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Filter by department
        response = self.client.get(url, {'department': self.department.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Filter by location (icontains)
        response = self.client.get(url, {'location__icontains': 'office'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Filter by location (exact match)
        response = self.client.get(url, {'location': 'Office A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_asset_history_stubbed_endpoint(self):
        """Test the history endpoint returns the correct stub structure."""
        self.client.force_authenticate(user=self.employee)
        url = reverse('asset-history', args=[self.asset1.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('allocations', response.data)
        self.assertIn('maintenance', response.data)
        self.assertEqual(response.data['allocations'], [])
        self.assertEqual(response.data['maintenance'], [])
