from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import UserRole
from .models import Department, Category, DepartmentStatus, ActivityLog
from .utils import log_activity

User = get_user_model()

class AssetFlowOrgTests(APITestCase):

    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='admin_user', password='password123', role=UserRole.ADMIN
        )
        self.asset_manager = User.objects.create_user(
            username='asset_manager', password='password123', role=UserRole.ASSET_MANAGER
        )
        self.dept_head = User.objects.create_user(
            username='dept_head', password='password123', role=UserRole.DEPT_HEAD
        )
        self.employee = User.objects.create_user(
            username='employee', password='password123', role=UserRole.EMPLOYEE
        )

        # Create basic categories
        self.category = Category.objects.create(
            name='Laptops', extra_fields={'warranty_period': '3 years'}
        )

        # Create a department
        self.dept1 = Department.objects.create(
            name='Engineering', head=self.dept_head, status=DepartmentStatus.ACTIVE
        )

    def test_reusable_transition_method(self):
        """Test model level transition validation rules."""
        dept = Department.objects.create(name='Marketing', status=DepartmentStatus.ACTIVE)
        
        # ACTIVE -> INACTIVE (Allowed)
        dept.transition(DepartmentStatus.INACTIVE)
        self.assertEqual(dept.status, DepartmentStatus.INACTIVE)

        # INACTIVE -> ACTIVE (Allowed)
        dept.transition(DepartmentStatus.ACTIVE)
        self.assertEqual(dept.status, DepartmentStatus.ACTIVE)

        # ACTIVE -> ACTIVE (No-op/Allowed)
        dept.transition(DepartmentStatus.ACTIVE)
        self.assertEqual(dept.status, DepartmentStatus.ACTIVE)

        # Invalid transition value
        with self.assertRaises(ValidationError):
            dept.transition('INVALID_STATUS')

    def test_log_activity_helper(self):
        """Test log_activity utility function."""
        # Unauthenticated user logging
        log1 = log_activity(None, 'TEST_ACTION', self.category, 'A test log')
        self.assertEqual(log1.action, 'TEST_ACTION')
        self.assertEqual(log1.target_model, 'Category')
        self.assertEqual(log1.target_id, str(self.category.id))
        self.assertEqual(log1.description, 'A test log')
        self.assertIsNone(log1.user)

        # Authenticated user logging
        log2 = log_activity(self.admin_user, 'CREATE', self.dept1)
        self.assertEqual(log2.user, self.admin_user)
        self.assertEqual(log2.action, 'CREATE')
        self.assertEqual(log2.target_model, 'Department')
        self.assertEqual(log2.target_id, str(self.dept1.id))

    def test_category_permissions(self):
        """Category creation is Admin-only."""
        url = reverse('category-list')
        data = {'name': 'Servers', 'extra_fields': {'ram_limit': '128GB'}}

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

        # 4. Admin succeeds
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.filter(name='Servers').count(), 1)
        
        # Verify Activity Log for Category Creation
        self.assertTrue(ActivityLog.objects.filter(action='CREATE', target_model='Category').exists())

    def test_department_permissions(self):
        """Department creation/update is DeptHeadOrAbove."""
        url = reverse('department-list')
        data = {'name': 'Sales'}

        # 1. Anonymous fails
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Employee fails
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Dept head succeeds
        self.client.force_authenticate(user=self.dept_head)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_department_head_assignment_admin_only(self):
        """Only ADMIN can assign or change the department head."""
        # Dept head attempts to create department with a head
        url = reverse('department-list')
        data = {
            'name': 'HR',
            'head': self.employee.id
        }
        self.client.force_authenticate(user=self.dept_head)
        response = self.client.post(url, data, format='json')
        # Should raise validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('head', response.data)

        # Admin attempts to create department with a head
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        dept_hr = Department.objects.get(name='HR')
        self.assertEqual(dept_hr.head, self.employee)

        # Dept head attempts to change department head
        update_url = reverse('department-detail', args=[self.dept1.id])
        update_data = {
            'name': 'Engineering V2',
            'head': self.employee.id
        }
        self.client.force_authenticate(user=self.dept_head)
        response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Admin attempts to change department head
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dept1.refresh_from_db()
        self.assertEqual(self.dept1.head, self.employee)

    def test_status_field_read_only_and_explicit_endpoints(self):
        """Status cannot be changed via PATCH/PUT directly, but works via custom action endpoints."""
        url = reverse('department-detail', args=[self.dept1.id])
        
        # Try to modify status directly via PATCH
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, {'status': DepartmentStatus.INACTIVE}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dept1.refresh_from_db()
        # Status should remain ACTIVE
        self.assertEqual(self.dept1.status, DepartmentStatus.ACTIVE)

        # Use deactivate action endpoint
        deactivate_url = reverse('department-deactivate', args=[self.dept1.id])
        response = self.client.post(deactivate_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dept1.refresh_from_db()
        self.assertEqual(self.dept1.status, DepartmentStatus.INACTIVE)

        # Verify activity log was created
        log = ActivityLog.objects.filter(action='STATUS_CHANGE', target_model='Department', target_id=str(self.dept1.id)).last()
        self.assertIsNotNone(log)
        self.assertIn("Transitioned status", log.description)

        # Use activate action endpoint
        activate_url = reverse('department-activate', args=[self.dept1.id])
        response = self.client.post(activate_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dept1.refresh_from_db()
        self.assertEqual(self.dept1.status, DepartmentStatus.ACTIVE)

    def test_filtering_and_searching(self):
        """Test search and filter endpoints using django-filter."""
        # Create extra departments
        self.client.force_authenticate(user=self.admin_user)
        dept_finance = Department.objects.create(name='Finance', head=self.dept_head, status=DepartmentStatus.INACTIVE)
        dept_support = Department.objects.create(name='Support', head=self.employee, status=DepartmentStatus.ACTIVE)

        url = reverse('department-list')

        # Filter by status
        response = self.client.get(url, {'status': DepartmentStatus.ACTIVE})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # engineering and support are active
        self.assertEqual(len(response.data), 2)

        # Filter by head
        response = self.client.get(url, {'head': self.dept_head.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # engineering and finance are headed by dept_head
        self.assertEqual(len(response.data), 2)
