"""
Seed script for AssetFlow — run with:
    python3 seed_data.py

This creates:
  - 1 Admin user (admin@assetflow.com / admin123)
  - 2 Departments (Engineering, Operations)
  - 2 Categories (Laptops, Vehicles)
  - 3 Employees (already created via signup, this adds 2 more)
  - 4 Assets
  - 1 Allocation
  - 1 Transfer Request
  - 1 Booking
  - 1 Maintenance Request
  - 1 Audit Cycle
"""

import os
import sys
import django

# ── bootstrap Django ─────────────────────────────────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetflow.settings')
django.setup()

# ── imports (after setup) ────────────────────────────────────
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from org.models import Department, Category
from assets.models import Asset, AssetStatus
from allocations.models import Allocation, AllocationStatus, TransferRequest
from bookings.models import Booking
from maintenance.models import MaintenanceRequest
from audits.models import AuditCycle, AuditItem
import datetime

User = get_user_model()

def create_user(username, email, password, first_name, last_name, role):
    if User.objects.filter(email__iexact=email).exists():
        u = User.objects.get(email__iexact=email)
        print(f"  [skip] user {email} already exists")
        return u
    u = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    Token.objects.get_or_create(user=u)
    print(f"  [+] created user {email} ({role})")
    return u

def run():
    from users.models import UserRole

    print("\n=== Creating Users ===")
    admin = create_user('admin', 'admin@assetflow.com', 'admin123', 'Admin', 'User', UserRole.ADMIN)
    manager = create_user('amanager', 'manager@assetflow.com', 'manager123', 'Asset', 'Manager', UserRole.ASSET_MANAGER)
    alice = create_user('alice', 'alice@assetflow.com', 'alice123', 'Alice', 'Johnson', UserRole.EMPLOYEE)
    bob = create_user('bob', 'bob@assetflow.com', 'bob123', 'Bob', 'Smith', UserRole.EMPLOYEE)

    print("\n=== Creating Departments ===")
    eng, c = Department.objects.get_or_create(name='Engineering', defaults={'head': manager, 'status': 'ACTIVE'})
    print(f"  [{'skip' if not c else '+'}] Engineering")
    ops, c = Department.objects.get_or_create(name='Operations', defaults={'head': alice, 'status': 'ACTIVE'})
    print(f"  [{'skip' if not c else '+'}] Operations")

    print("\n=== Creating Categories ===")
    laptops, c = Category.objects.get_or_create(name='Laptops', defaults={'extra_fields': {'RAM': '16GB', 'Storage': '512GB SSD'}})
    print(f"  [{'skip' if not c else '+'}] Laptops")
    vehicles, c = Category.objects.get_or_create(name='Vehicles', defaults={'extra_fields': {'Fuel': 'Diesel', 'Seats': '5'}})
    print(f"  [{'skip' if not c else '+'}] Vehicles")

    print("\n=== Creating Assets ===")
    def make_asset(name, category, department, cost, condition='GOOD', is_bookable=False, location='HQ'):
        if Asset.objects.filter(name=name).exists():
            a = Asset.objects.get(name=name)
            print(f"  [skip] {name}")
            return a
        a = Asset.objects.create(
            name=name,
            category=category,
            department=department,
            acquisition_date=datetime.date(2024, 1, 15),
            acquisition_cost=cost,
            condition=condition,
            location=location,
            is_bookable=is_bookable,
            status=AssetStatus.AVAILABLE,
        )
        print(f"  [+] {name} → {a.tag}")
        return a

    mbp = make_asset('MacBook Pro M3', laptops, eng, 2500.00, 'NEW', False, 'HQ-301')
    dell = make_asset('Dell XPS 15', laptops, eng, 1800.00, 'GOOD', False, 'HQ-302')
    conf_room = make_asset('Conference Room A', laptops, ops, 0.00, 'GOOD', True, 'HQ-GF-CR1')
    suv = make_asset('Toyota Fortuner', vehicles, ops, 45000.00, 'FAIR', True, 'Parking-B')

    print("\n=== Creating Allocation ===")
    if not Allocation.objects.filter(asset=mbp, employee=alice).exists():
        mbp.status = AssetStatus.ALLOCATED
        mbp.save()
        Allocation.objects.create(
            asset=mbp,
            employee=alice,
            department=eng,
            expected_return_date=datetime.date.today() + datetime.timedelta(days=30),
            status=AllocationStatus.ACTIVE,
        )
        print(f"  [+] MacBook Pro allocated to Alice")
    else:
        print(f"  [skip] allocation already exists")

    print("\n=== Creating Transfer Request ===")
    if not TransferRequest.objects.filter(asset=dell).exists():
        TransferRequest.objects.create(
            asset=dell,
            from_employee=manager,
            to_employee=bob,
            reason='Bob needs a laptop for the new project',
        )
        print(f"  [+] Transfer request: Dell XPS to Bob")
    else:
        print(f"  [skip] transfer already exists")

    print("\n=== Creating Booking ===")
    start = datetime.datetime(2026, 7, 15, 9, 0, 0, tzinfo=datetime.timezone.utc)
    end   = datetime.datetime(2026, 7, 15, 11, 0, 0, tzinfo=datetime.timezone.utc)
    if not Booking.objects.filter(resource=conf_room, start_time=start).exists():
        Booking.objects.create(
            resource=conf_room,
            booked_by=alice,
            start_time=start,
            end_time=end,
        )
        conf_room.status = AssetStatus.RESERVED
        conf_room.save()
        print(f"  [+] Conference Room A booked by Alice on 2026-07-15 09:00–11:00")
    else:
        print(f"  [skip] booking already exists")

    print("\n=== Creating Maintenance Request ===")
    from maintenance.models import MaintenanceRequest, MaintenancePriority
    if not MaintenanceRequest.objects.filter(asset=suv).exists():
        MaintenanceRequest.objects.create(
            asset=suv,
            raised_by=bob,
            issue_text='Engine check light is on, needs diagnostic',
            priority=MaintenancePriority.HIGH,
        )
        print(f"  [+] Maintenance raised for Toyota Fortuner")
    else:
        print(f"  [skip] maintenance already exists")

    print("\n=== Creating Audit Cycle ===")
    if not AuditCycle.objects.filter(scope_department=eng).exists():
        cycle = AuditCycle.objects.create(
            scope_department=eng,
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=7),
        )
        # Add auditor
        cycle.auditors.add(manager)
        # Create audit items for assets in eng dept
        for asset in Asset.objects.filter(department=eng):
            AuditItem.objects.create(cycle=cycle, asset=asset)
        print(f"  [+] Audit cycle for Engineering with {AuditItem.objects.filter(cycle=cycle).count()} items")
    else:
        print(f"  [skip] audit cycle already exists")

    print("\n✅ Seed data complete!\n")
    print("Login credentials:")
    print("  Admin:   admin@assetflow.com  / admin123")
    print("  Manager: manager@assetflow.com / manager123")
    print("  Alice:   alice@assetflow.com  / alice123")
    print("  Bob:     bob@assetflow.com   / bob123")

if __name__ == '__main__':
    run()
