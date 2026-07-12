from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable

from tqdm import tqdm

from api import ApiClient, ApiError
from auth import AuthContext, AuthService
from config import (
    DEFAULT_CATEGORIES,
    DEFAULT_DEPARTMENTS,
    SeedTargets,
    load_settings,
)
from generators import (
    AUDIT_RESULTS,
    EmployeeRecord,
    TimeWindow,
    random_asset_payload,
    random_audit_cycle_window,
    random_booking_window,
    random_employee,
    random_expected_return,
    random_maintenance_payload,
    random_transfer_payload,
)
from helpers import Stopwatch, log_error, log_info, log_success, log_warn, summarize_exception


@dataclass(slots=True)
class SeedState:
    auth: AuthContext | None = None
    department_ids: list[int] = field(default_factory=list)
    employee_ids: list[int] = field(default_factory=list)
    asset_manager_ids: list[int] = field(default_factory=list)
    department_head_ids: list[int] = field(default_factory=list)
    category_ids: list[int] = field(default_factory=list)
    asset_ids: list[int] = field(default_factory=list)
    bookable_asset_ids: list[int] = field(default_factory=list)
    allocated_asset_ids: list[int] = field(default_factory=list)
    allocation_ids: list[int] = field(default_factory=list)
    booking_ids: list[int] = field(default_factory=list)
    maintenance_ids: list[int] = field(default_factory=list)
    transfer_ids: list[int] = field(default_factory=list)
    audit_cycle_ids: list[int] = field(default_factory=list)


@dataclass(slots=True)
class SeedStats:
    departments_created: int = 0
    employees_created: int = 0
    categories_created: int = 0
    assets_created: int = 0
    allocations_created: int = 0
    bookings_created: int = 0
    maintenance_created: int = 0
    transfers_created: int = 0
    audit_cycles_created: int = 0


class AssetFlowSeeder:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.targets = SeedTargets()
        self.client = ApiClient(self.settings)
        self.auth_service = AuthService(self.client, self.settings)
        self.state = SeedState()
        self.stats = SeedStats()
        self._booking_windows: dict[int, list[TimeWindow]] = {}

    def run(self) -> None:
        timer = Stopwatch()
        log_info("Starting API-only AssetFlow data seeding")

        self.login()
        self.create_departments()
        self.create_employees()
        self.promote_employee_roles()
        self.assign_department_heads()
        self.create_categories()
        self.create_assets()
        self.create_allocations()
        self.create_bookings()
        self.create_maintenance_requests()
        self.create_transfer_requests()
        self.create_audit_cycles_and_mark_items()
        self.verify_dashboard_data()

        self.print_summary(timer)

    def login(self) -> None:
        self.state.auth = self.auth_service.login_admin()

    def create_departments(self) -> None:
        log_info("Creating departments")
        for name in tqdm(DEFAULT_DEPARTMENTS[: self.targets.departments], desc="Departments", unit="dept"):
            try:
                data = self.client.post(
                    "/api/departments/",
                    json={"name": name, "parent": None},
                    expected_status=(201,),
                )
                self.state.department_ids.append(int(data["id"]))
                self.stats.departments_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Department create failed", exc, {"name": name}))

        log_success(f"Departments created: {self.stats.departments_created}")

    def create_employees(self) -> None:
        log_info("Creating employees")
        usernames: set[str] = set()
        emails: set[str] = set()

        for _ in tqdm(range(self.targets.employees), desc="Employees", unit="user"):
            rec: EmployeeRecord = random_employee(usernames, emails)
            payload = {
                "username": rec.username,
                "email": rec.email,
                "first_name": rec.first_name,
                "last_name": rec.last_name,
                "role": "EMPLOYEE",
            }
            try:
                data = self.client.post("/api/employees/", json=payload, expected_status=(201,))
                self.state.employee_ids.append(int(data["id"]))
                self.stats.employees_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(
                    summarize_exception(
                        "Employee create failed",
                        exc,
                        {"username": rec.username, "email": rec.email, "phone": rec.phone, "address": rec.address},
                    )
                )

        log_success(f"Employees created: {self.stats.employees_created}")

    def promote_employee_roles(self) -> None:
        log_info("Promoting employee roles")
        if len(self.state.employee_ids) < (self.targets.asset_managers + self.targets.dept_heads):
            log_warn("Not enough employees created to fulfill role distribution")

        pool = self.state.employee_ids.copy()
        random.shuffle(pool)

        self.state.asset_manager_ids = pool[: self.targets.asset_managers]
        self.state.department_head_ids = pool[
            self.targets.asset_managers : self.targets.asset_managers + self.targets.dept_heads
        ]

        for user_id in tqdm(self.state.asset_manager_ids, desc="Promote Asset Managers", unit="user"):
            self._promote_user(user_id, "ASSET_MANAGER")

        for user_id in tqdm(self.state.department_head_ids, desc="Promote Dept Heads", unit="user"):
            self._promote_user(user_id, "DEPT_HEAD")

        log_success(
            f"Promotions done: ASSET_MANAGER={len(self.state.asset_manager_ids)}, "
            f"DEPT_HEAD={len(self.state.department_head_ids)}"
        )

    def assign_department_heads(self) -> None:
        log_info("Assigning department heads to departments")
        if not self.state.department_ids or not self.state.department_head_ids:
            log_warn("Skipping department head assignment due to missing departments or dept-head users")
            return

        total = min(len(self.state.department_ids), len(self.state.department_head_ids))
        for i in tqdm(range(total), desc="Assign Heads", unit="dept"):
            dept_id = self.state.department_ids[i]
            head_id = self.state.department_head_ids[i]
            try:
                self.client.patch(
                    f"/api/departments/{dept_id}/",
                    json={"head": head_id},
                    expected_status=(200,),
                )
            except Exception as exc:  # noqa: BLE001
                log_error(
                    summarize_exception(
                        "Assigning department head failed",
                        exc,
                        {"department_id": dept_id, "head_id": head_id},
                    )
                )

        log_success(f"Department heads assigned for {total} departments")

    def create_categories(self) -> None:
        log_info("Creating categories")
        for category in tqdm(DEFAULT_CATEGORIES[: self.targets.categories], desc="Categories", unit="cat"):
            try:
                data = self.client.post("/api/categories/", json=category, expected_status=(201,))
                self.state.category_ids.append(int(data["id"]))
                self.stats.categories_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Category create failed", exc, category))

        log_success(f"Categories created: {self.stats.categories_created}")

    def create_assets(self) -> None:
        log_info("Creating assets")
        if not self.state.category_ids:
            log_warn("Skipping asset creation because no categories were created")
            return

        for _ in tqdm(range(self.targets.assets), desc="Assets", unit="asset"):
            category_id = random.choice(self.state.category_ids)
            department_id = random.choice(self.state.department_ids) if self.state.department_ids and random.random() < 0.65 else None
            payload = random_asset_payload(category_id=category_id, department_id=department_id)

            try:
                data = self.client.post("/api/assets/", json=payload, expected_status=(201,))
                asset_id = int(data["id"])
                self.state.asset_ids.append(asset_id)
                if bool(data.get("is_bookable", payload["is_bookable"])):
                    self.state.bookable_asset_ids.append(asset_id)
                self.stats.assets_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Asset create failed", exc, payload))

        log_success(f"Assets created: {self.stats.assets_created}")

    def create_allocations(self) -> None:
        log_info("Creating allocations")
        if not self.state.asset_ids:
            log_warn("Skipping allocations because no assets exist")
            return

        available_assets = [a for a in self.state.asset_ids if a not in self.state.allocated_asset_ids]
        random.shuffle(available_assets)

        desired = min(self.targets.allocations, len(available_assets))
        for asset_id in tqdm(available_assets[:desired], desc="Allocations", unit="alloc"):
            assign_to_employee = bool(self.state.employee_ids) and random.random() < 0.7
            payload: dict[str, Any] = {
                "asset": asset_id,
                "expected_return_date": random_expected_return(),
                "condition_note": random.choice(
                    [
                        "Allocated in good working condition",
                        "Issued with charger and carry case",
                        "Assigned after routine quality check",
                    ]
                ),
            }

            if assign_to_employee:
                payload["employee"] = random.choice(self.state.employee_ids)
            elif self.state.department_ids:
                payload["department"] = random.choice(self.state.department_ids)
            else:
                payload["employee"] = random.choice(self.state.employee_ids)

            try:
                data = self.client.post("/api/allocations/", json=payload, expected_status=(201,))
                self.state.allocation_ids.append(int(data["id"]))
                self.state.allocated_asset_ids.append(asset_id)
                self.stats.allocations_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Allocation create failed", exc, payload))

        log_success(f"Allocations created: {self.stats.allocations_created}")

    def create_bookings(self) -> None:
        log_info("Creating bookings")
        if not self.state.bookable_asset_ids:
            log_warn("Skipping bookings because no bookable assets exist")
            return

        for _ in tqdm(range(self.targets.bookings), desc="Bookings", unit="booking"):
            asset_id = random.choice(self.state.bookable_asset_ids)
            windows = self._booking_windows.setdefault(asset_id, [])
            slot = random_booking_window(windows)
            windows.append(slot)

            payload = {
                "resource": asset_id,
                "start_time": slot.start.isoformat().replace("+00:00", "Z"),
                "end_time": slot.end.isoformat().replace("+00:00", "Z"),
            }
            try:
                data = self.client.post("/api/bookings/", json=payload, expected_status=(201,))
                self.state.booking_ids.append(int(data["id"]))
                self.stats.bookings_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Booking create failed", exc, payload))

        log_success(f"Bookings created: {self.stats.bookings_created}")

    def create_maintenance_requests(self) -> None:
        log_info("Creating maintenance requests")
        if not self.state.asset_ids:
            log_warn("Skipping maintenance because no assets exist")
            return

        technician_pool = self.state.asset_manager_ids or self.state.employee_ids

        for _ in tqdm(range(self.targets.maintenance), desc="Maintenance", unit="mr"):
            asset_id = random.choice(self.state.asset_ids)
            payload = random_maintenance_payload(asset_id)

            try:
                data = self.client.post("/api/maintenance/", json=payload, expected_status=(201,))
                request_id = int(data["id"])
                self.state.maintenance_ids.append(request_id)
                self.stats.maintenance_created += 1

                # Randomly move some requests through workflow.
                roll = random.random()
                if roll < 0.55:
                    self.client.post(f"/api/maintenance/{request_id}/approve/", json={}, expected_status=(200,))
                    if technician_pool:
                        self.client.post(
                            f"/api/maintenance/{request_id}/assign-technician/",
                            json={"technician": random.choice(technician_pool)},
                            expected_status=(200,),
                        )
                        self.client.post(f"/api/maintenance/{request_id}/start/", json={}, expected_status=(200,))
                        if random.random() < 0.7:
                            self.client.post(f"/api/maintenance/{request_id}/resolve/", json={}, expected_status=(200,))
                elif roll < 0.8:
                    self.client.post(f"/api/maintenance/{request_id}/reject/", json={}, expected_status=(200,))
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Maintenance flow failed", exc, payload))

        log_success(f"Maintenance requests created: {self.stats.maintenance_created}")

    def create_transfer_requests(self) -> None:
        log_info("Creating transfer requests")
        if not self.state.asset_ids or not self.state.employee_ids:
            log_warn("Skipping transfers because assets or employees are missing")
            return

        for _ in tqdm(range(self.targets.transfers), desc="Transfers", unit="transfer"):
            asset_id = random.choice(self.state.asset_ids)
            to_employee = random.choice(self.state.employee_ids)
            payload = random_transfer_payload(asset_id=asset_id, to_employee=to_employee)

            try:
                data = self.client.post("/api/transfers/", json=payload, expected_status=(201,))
                transfer_id = int(data["id"])
                self.state.transfer_ids.append(transfer_id)
                self.stats.transfers_created += 1

                # Random approval/rejection status.
                if random.random() < 0.6:
                    self.client.post(f"/api/transfers/{transfer_id}/approve/", json={}, expected_status=(200,))
                else:
                    self.client.post(f"/api/transfers/{transfer_id}/reject/", json={}, expected_status=(200,))
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Transfer flow failed", exc, payload))

        log_success(f"Transfers created: {self.stats.transfers_created}")

    def create_audit_cycles_and_mark_items(self) -> None:
        log_info("Creating audit cycles and marking items")
        if not self.state.asset_ids:
            log_warn("Skipping audits because no assets exist")
            return

        auditor_pool = self._build_auditor_pool()
        if not auditor_pool:
            log_warn("Skipping audits because no valid auditors are available")
            return

        created_cycles: list[int] = []
        for cycle_idx in tqdm(range(self.targets.audit_cycles), desc="Audit Cycles", unit="cycle"):
            start_date, end_date = random_audit_cycle_window(offset_days=(cycle_idx * 14) + 2)
            payload = {
                "scope_department": random.choice(self.state.department_ids) if self.state.department_ids and random.random() < 0.5 else None,
                "scope_location": None,
                "start_date": start_date,
                "end_date": end_date,
                "auditors": random.sample(auditor_pool, k=min(len(auditor_pool), 3)),
            }
            # ensure current authenticated user can mark items
            if self.state.auth and self.state.auth.user_id not in payload["auditors"]:
                payload["auditors"].append(self.state.auth.user_id)

            try:
                data = self.client.post("/api/audit-cycles/", json=payload, expected_status=(201,))
                cycle_id = int(data["id"])
                created_cycles.append(cycle_id)
                self.state.audit_cycle_ids.append(cycle_id)
                self.stats.audit_cycles_created += 1
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Audit cycle create failed", exc, payload))

        if not created_cycles:
            return

        all_items: list[dict[str, Any]] = []
        for cycle_id in created_cycles:
            try:
                items_raw = self.client.get("/api/audit-items/", params={"cycle": cycle_id}, expected_status=(200,))
                for item in self._extract_list(items_raw):
                    all_items.append(item)
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Fetching audit items failed", exc, {"cycle_id": cycle_id}))

        if not all_items:
            log_warn("No audit items returned from API, skipping mark step")
            return

        random.shuffle(all_items)
        to_mark = all_items[: min(self.targets.audit_marks, len(all_items))]
        for item in tqdm(to_mark, desc="Mark Audit Items", unit="item"):
            item_id = int(item["id"])
            result = random.choice(AUDIT_RESULTS)
            try:
                self.client.post(
                    f"/api/audit-items/{item_id}/mark/",
                    json={"result": result},
                    expected_status=(200,),
                )
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Mark audit item failed", exc, {"item_id": item_id, "result": result}))

        for cycle_id in created_cycles:
            try:
                if random.random() < 0.6:
                    self.client.post(f"/api/audit-cycles/{cycle_id}/close/", json={}, expected_status=(200,))
            except Exception as exc:  # noqa: BLE001
                log_error(summarize_exception("Close audit cycle failed", exc, {"cycle_id": cycle_id}))

        log_success(f"Audit cycles created: {self.stats.audit_cycles_created}")

    def verify_dashboard_data(self) -> None:
        log_info("Verifying dashboard and reporting endpoints")
        endpoints = [
            "/api/dashboard/kpis/",
            "/api/reports/asset-status-breakdown/",
            "/api/reports/booking-trend/",
            "/api/reports/booking-heatmap/",
            "/api/reports/utilization/",
            "/api/reports/maintenance-frequency/",
            "/api/notifications/",
            "/api/logs/",
        ]
        for endpoint in tqdm(endpoints, desc="Verify APIs", unit="endpoint"):
            try:
                _ = self.client.get(endpoint, expected_status=(200,))
                log_success(f"Verified {endpoint}")
            except Exception as exc:  # noqa: BLE001
                log_warn(summarize_exception("Verification failed", exc, {"endpoint": endpoint}))

    def print_summary(self, timer: Stopwatch) -> None:
        print("\n" + "=" * 62)
        print("ASSETFLOW SEED SUMMARY")
        print("=" * 62)
        print(f"Departments Created:    {self.stats.departments_created}")
        print(f"Employees Created:      {self.stats.employees_created}")
        print(f"Categories Created:     {self.stats.categories_created}")
        print(f"Assets Created:         {self.stats.assets_created}")
        print(f"Allocations Created:    {self.stats.allocations_created}")
        print(f"Bookings Created:       {self.stats.bookings_created}")
        print(f"Maintenance Created:    {self.stats.maintenance_created}")
        print(f"Transfers Created:      {self.stats.transfers_created}")
        print(f"Audit Cycles Created:   {self.stats.audit_cycles_created}")
        print(f"Total API Calls:        {self.client.call_count}")
        print(f"Execution Time:         {timer.elapsed_human()}")
        print("=" * 62)

    def _promote_user(self, user_id: int, role: str) -> None:
        try:
            self.client.post(
                f"/api/employees/{user_id}/promote/",
                json={"role": role},
                expected_status=(200,),
            )
        except Exception as exc:  # noqa: BLE001
            log_error(summarize_exception("Promotion failed", exc, {"user_id": user_id, "role": role}))

    def _build_auditor_pool(self) -> list[int]:
        pool = set(self.state.department_head_ids + self.state.asset_manager_ids + self.state.employee_ids[:6])
        if self.state.auth:
            pool.add(self.state.auth.user_id)
        return list(pool)

    @staticmethod
    def _extract_list(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if isinstance(data, dict):
            if isinstance(data.get("results"), list):
                return [x for x in data["results"] if isinstance(x, dict)]
            # Handles any ad-hoc dict response that wraps list in another key
            for value in data.values():
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]
        return []


def main() -> None:
    try:
        seeder = AssetFlowSeeder()
        seeder.run()
    except ApiError as exc:
        log_error(f"Fatal API error: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001
        log_error(f"Fatal error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
