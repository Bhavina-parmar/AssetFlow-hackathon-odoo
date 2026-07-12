from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole
from org.models import Category, Department, ActivityLog
from assets.models import Asset, AssetStatus, AssetCondition
from .models import AuditCycle, AuditItem, AuditCycleStatus, AuditResult

User = get_user_model()

class AssetFlowAuditsTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.auditor = User.objects.create_user(
            username='auditor', password='password123', role=UserRole.EMPLOYEE
        )
        self.other_user = User.objects.create_user(
            username='other_user', password='password123', role=UserRole.EMPLOYEE
        )

        # Create departments
        self.dept_a = Department.objects.create(name='Dept A')
        self.dept_b = Department.objects.create(name='Dept B')

        # Create Category
        self.category = Category.objects.create(name='Electronics')

        # Create assets
        self.asset_a = Asset.objects.create(
            name='Asset A',
            category=self.category,
            serial_number='SN-A',
            acquisition_date='2026-01-01',
            acquisition_cost='1000.00',
            condition=AssetCondition.GOOD,
            is_bookable=False,
            status=AssetStatus.AVAILABLE,
            department=self.dept_a,
            location='Office East'
        )

        self.asset_b = Asset.objects.create(
            name='Asset B',
            category=self.category,
            serial_number='SN-B',
            acquisition_date='2026-01-01',
            acquisition_cost='1200.00',
            condition=AssetCondition.GOOD,
            is_bookable=False,
            status=AssetStatus.AVAILABLE,
            department=self.dept_b,
            location='Office West'
        )

    def test_cycle_creation_and_auto_populate(self):
        """Verify cycle creation auto-populates AuditItems within scope."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('auditcycle-list')

        # 1. Create cycle scoped to Dept A
        data_scoped = {
            'scope_department': self.dept_a.id,
            'start_date': '2026-07-01',
            'end_date': '2026-07-15',
            'auditors': [self.auditor.id]
        }
        response = self.client.post(url, data_scoped, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cycle_id = response.data['id']

        # Should create 1 AuditItem for Asset A (Asset B is in Dept B)
        self.assertEqual(AuditItem.objects.filter(cycle_id=cycle_id).count(), 1)
        self.assertTrue(AuditItem.objects.filter(cycle_id=cycle_id, asset=self.asset_a).exists())

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='AUDIT_CYCLE_CREATE', target_model='AuditCycle', target_id=str(cycle_id)).exists())

    def test_item_marking_permissions_and_locking(self):
        """Verify only assigned auditors can mark items, and marking is blocked on closed cycles."""
        self.client.force_authenticate(user=self.admin_user)
        url_cycle = reverse('auditcycle-list')
        
        # Create cycle
        data = {
            'start_date': '2026-07-01',
            'end_date': '2026-07-15',
            'auditors': [self.auditor.id]
        }
        response = self.client.post(url_cycle, data, format='json')
        cycle_id = response.data['id']
        item = AuditItem.objects.filter(cycle_id=cycle_id).first()

        url_mark = reverse('audititem-mark', args=[item.id])
        data_mark = {'result': AuditResult.VERIFIED}

        # 1. Non-auditor tries to mark (Forbidden)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(url_mark, data_mark, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Assigned auditor tries to mark (Allowed)
        self.client.force_authenticate(user=self.auditor)
        response = self.client.post(url_mark, data_mark, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], AuditResult.VERIFIED)

        # Verify activity log
        self.assertTrue(ActivityLog.objects.filter(action='AUDIT_ITEM_MARK', target_model='AuditItem', target_id=str(item.id)).exists())

        # 3. Close the cycle
        self.client.force_authenticate(user=self.admin_user)
        close_url = reverse('auditcycle-close-cycle', args=[cycle_id])
        response = self.client.post(close_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4. Assigned auditor tries to mark closed cycle (Blocked)
        self.client.force_authenticate(user=self.auditor)
        data_mark_new = {'result': AuditResult.DAMAGED}
        response = self.client.post(url_mark, data_mark_new, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_discrepancies_and_closure_transitions(self):
        """Test discrepancies endpoint and status transitions to LOST upon cycle closure."""
        # Create cycle
        self.client.force_authenticate(user=self.admin_user)
        url_cycle = reverse('auditcycle-list')
        data = {
            'start_date': '2026-07-01',
            'end_date': '2026-07-15',
            'auditors': [self.auditor.id]
        }
        response = self.client.post(url_cycle, data, format='json')
        cycle_id = response.data['id']

        # Get items: we have 2 items (Asset A and Asset B)
        item_a = AuditItem.objects.get(cycle_id=cycle_id, asset=self.asset_a)
        item_b = AuditItem.objects.get(cycle_id=cycle_id, asset=self.asset_b)

        # Auditor marks Item A as VERIFIED, and Item B as MISSING
        self.client.force_authenticate(user=self.auditor)
        self.client.post(reverse('audititem-mark', args=[item_a.id]), {'result': AuditResult.VERIFIED}, format='json')
        self.client.post(reverse('audititem-mark', args=[item_b.id]), {'result': AuditResult.MISSING}, format='json')

        # 1. Check discrepancies (Only Item B should be returned since A is VERIFIED)
        url_discrepancy = reverse('auditcycle-discrepancies', args=[cycle_id])
        self.client.force_authenticate(user=self.other_user) # Anyone authenticated can view
        response = self.client.get(url_discrepancy)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], item_b.id)

        # 2. Close cycle and verify transitions
        self.client.force_authenticate(user=self.admin_user)
        close_url = reverse('auditcycle-close-cycle', args=[cycle_id])
        response = self.client.post(close_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Asset B should now be LOST
        self.asset_b.refresh_from_db()
        self.assertEqual(self.asset_b.status, AssetStatus.LOST)

        # Asset A should still be AVAILABLE
        self.asset_a.refresh_from_db()
        self.assertEqual(self.asset_a.status, AssetStatus.AVAILABLE)

        # Verify activity logs
        self.assertTrue(ActivityLog.objects.filter(action='AUDIT_CYCLE_CLOSE', target_model='AuditCycle', target_id=str(cycle_id)).exists())
        self.assertTrue(ActivityLog.objects.filter(action='STATUS_CHANGE', target_model='Asset', target_id=str(self.asset_b.id)).exists())
