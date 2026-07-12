from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class SeedTargets:
    departments: int = 10
    employees: int = 35
    asset_managers: int = 2
    dept_heads: int = 6
    categories: int = 10
    assets: int = 150
    allocations: int = 60
    bookings: int = 100
    maintenance: int = 40
    transfers: int = 30
    audit_cycles: int = 2
    audit_marks: int = 20


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str
    admin_email: str
    admin_password: str
    timeout_seconds: int = 30
    verify_ssl: bool = True


def load_settings() -> Settings:
    load_dotenv()

    base_url = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
    admin_email = os.getenv("ADMIN_EMAIL", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not admin_email or not admin_password:
        raise ValueError("ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env")

    return Settings(
        base_url=base_url,
        admin_email=admin_email,
        admin_password=admin_password,
    )


DEFAULT_DEPARTMENTS: list[str] = [
    "Engineering",
    "HR",
    "Finance",
    "Sales",
    "Marketing",
    "Operations",
    "IT Support",
    "Legal",
    "Administration",
    "Procurement",
]


DEFAULT_CATEGORIES: list[dict[str, object]] = [
    {"name": "Laptop", "extra_fields": {"battery": "Lithium-ion", "warranty_years": 3}},
    {"name": "Desktop", "extra_fields": {"form_factor": "Tower", "warranty_years": 3}},
    {"name": "Printer", "extra_fields": {"print_type": "Laser", "duplex": True}},
    {"name": "Monitor", "extra_fields": {"panel": "IPS", "size": "27 inch"}},
    {"name": "Networking", "extra_fields": {"type": "Router/Switch", "poe": False}},
    {"name": "Tablet", "extra_fields": {"screen_size": "11 inch", "cellular": True}},
    {"name": "Phone", "extra_fields": {"os": "Android/iOS", "dual_sim": True}},
    {"name": "Furniture", "extra_fields": {"material": "Engineered Wood", "movable": True}},
    {"name": "Conference Equipment", "extra_fields": {"audio": "Integrated", "wireless": True}},
    {"name": "Accessories", "extra_fields": {"peripheral_type": "Input/Output", "portable": True}},
]


INDIAN_OFFICE_LOCATIONS: list[str] = [
    "Bengaluru - Whitefield Campus",
    "Hyderabad - HITEC City Office",
    "Pune - Hinjawadi Tech Park",
    "Mumbai - BKC Tower 2",
    "Gurugram - Cyber City Block C",
    "Chennai - OMR Innovation Center",
    "Noida - Sector 62 Tower A",
    "Kolkata - Salt Lake IT Hub",
    "Ahmedabad - GIFT City Annex",
    "Kochi - SmartCity Building 5",
]
