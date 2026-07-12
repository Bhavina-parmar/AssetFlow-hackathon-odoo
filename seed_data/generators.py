from __future__ import annotations

import random
import string
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from faker import Faker

from config import INDIAN_OFFICE_LOCATIONS

faker = Faker("en_IN")


INDIAN_FIRST_NAMES: list[str] = [
    "Aarav", "Vihaan", "Ishaan", "Aditya", "Arjun", "Reyansh", "Vivaan", "Kabir", "Rohan", "Karthik",
    "Saanvi", "Anaya", "Diya", "Ira", "Aadhya", "Myra", "Kiara", "Navya", "Riya", "Sneha",
    "Pranav", "Nikhil", "Rahul", "Siddharth", "Aniket", "Shreya", "Pooja", "Neha", "Aditi", "Tanvi",
    "Meera", "Harsh", "Dev", "Yash", "Akash", "Sakshi", "Payal", "Bhavna", "Nandini", "Ishita",
]

INDIAN_LAST_NAMES: list[str] = [
    "Sharma", "Patel", "Gupta", "Reddy", "Iyer", "Nair", "Kulkarni", "Mehta", "Verma", "Joshi",
    "Rao", "Menon", "Agarwal", "Pillai", "Khan", "Malhotra", "Bose", "Chatterjee", "Mukherjee", "Singh",
    "Das", "Saxena", "Mishra", "Trivedi", "Bhat", "Ghosh", "Jain", "Kapoor", "Srinivasan", "Banerjee",
]

ASSET_NAME_OPTIONS: list[str] = [
    "Dell Latitude 7440",
    "Lenovo ThinkPad X1 Carbon",
    "MacBook Pro 14",
    "MacBook Air 13",
    "Dell UltraSharp Monitor",
    "Cisco ISR Router",
    "HP LaserJet Pro",
    "iPhone 15",
    "iPad Air",
    "Logitech MX Keyboard",
    "Epson Projector",
    "Acer Veriton Desktop",
    "Samsung Smart Monitor",
    "Poly Conference Speaker",
    "TP-Link Managed Switch",
]

MAINTENANCE_ISSUES: list[str] = [
    "Broken Screen",
    "Battery Failure",
    "Camera Not Working",
    "Keyboard Issue",
    "WiFi Issue",
    "SSD Failure",
    "Charging Port Damage",
    "Fan Noise and Heating",
    "Frequent Random Reboots",
    "Power Adapter Fault",
]

TRANSFER_REASONS: list[str] = [
    "Project reassignment",
    "New joiner onboarding",
    "Temporary cross-team support",
    "Department resource balancing",
    "Hardware refresh request",
    "Replacement for faulty asset",
]

CONDITIONS: list[str] = ["NEW", "GOOD", "FAIR", "POOR", "DAMAGED"]
PRIORITIES: list[str] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
AUDIT_RESULTS: list[str] = ["VERIFIED", "DAMAGED", "MISSING"]


@dataclass(slots=True)
class EmployeeRecord:
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str
    address: str


@dataclass(slots=True)
class TimeWindow:
    start: datetime
    end: datetime


def _safe_username(base: str) -> str:
    clean = "".join(ch for ch in base.lower() if ch.isalnum() or ch == "_")
    clean = clean.strip("_")
    return clean[:24] if clean else f"user_{uuid.uuid4().hex[:8]}"


def random_employee(existing_usernames: set[str], existing_emails: set[str]) -> EmployeeRecord:
    while True:
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        suffix = random.randint(10, 99)
        username = _safe_username(f"{first_name}.{last_name}{suffix}")
        email = f"{first_name.lower()}.{last_name.lower()}{suffix}@assetflow.in"
        if username in existing_usernames or email in existing_emails:
            continue

        existing_usernames.add(username)
        existing_emails.add(email)

        phone = faker.phone_number()
        address = faker.address().replace("\n", ", ")
        return EmployeeRecord(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
        )


def random_asset_payload(category_id: int, department_id: int | None) -> dict[str, Any]:
    acquisition_date = faker.date_between(start_date="-5y", end_date="today")
    serial_seed = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    serial_number = f"SN-{serial_seed}-{uuid.uuid4().hex[:4].upper()}"

    cost = Decimal(str(round(random.uniform(3500, 250000), 2)))
    condition = random.choices(CONDITIONS, weights=[0.25, 0.40, 0.20, 0.10, 0.05], k=1)[0]

    payload: dict[str, Any] = {
        "name": random.choice(ASSET_NAME_OPTIONS),
        "category": category_id,
        "serial_number": serial_number,
        "acquisition_date": acquisition_date.isoformat(),
        "acquisition_cost": str(cost),
        "condition": condition,
        "location": random.choice(INDIAN_OFFICE_LOCATIONS),
        "is_bookable": random.random() < 0.55,
    }

    if department_id is not None:
        payload["department"] = department_id

    return payload


def random_expected_return() -> str:
    return faker.date_between(start_date="+15d", end_date="+180d").isoformat()


def random_booking_window(existing: list[TimeWindow]) -> TimeWindow:
    for _ in range(80):
        day_offset = random.randint(-20, 35)
        hour = random.randint(8, 18)
        minute = random.choice([0, 15, 30, 45])
        duration_hours = random.choice([1, 2, 3, 4])

        start = datetime.now(timezone.utc) + timedelta(days=day_offset)
        start = start.replace(hour=hour, minute=minute, second=0, microsecond=0)
        end = start + timedelta(hours=duration_hours)

        candidate = TimeWindow(start=start, end=end)
        if not has_overlap(candidate, existing):
            return candidate

    start = datetime.now(timezone.utc) + timedelta(days=random.randint(36, 80))
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=2)
    return TimeWindow(start=start, end=end)


def has_overlap(candidate: TimeWindow, existing: list[TimeWindow]) -> bool:
    for window in existing:
        if candidate.start < window.end and candidate.end > window.start:
            return True
    return False


def random_maintenance_payload(asset_id: int) -> dict[str, Any]:
    return {
        "asset": asset_id,
        "issue_text": random.choice(MAINTENANCE_ISSUES),
        "priority": random.choice(PRIORITIES),
    }


def random_transfer_payload(asset_id: int, to_employee: int) -> dict[str, Any]:
    return {
        "asset": asset_id,
        "to_employee": to_employee,
        "reason": random.choice(TRANSFER_REASONS),
    }


def random_audit_cycle_window(offset_days: int) -> tuple[str, str]:
    start = date.today() - timedelta(days=offset_days)
    end = start + timedelta(days=random.randint(5, 12))
    return start.isoformat(), end.isoformat()
