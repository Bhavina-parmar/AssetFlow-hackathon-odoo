# AssetFlow — Frontend API Endpoints Reference

> All endpoints are prefixed with `/api/`.
> Auth: every request (except login/signup) requires `Authorization: Bearer <token>` header.
> All responses are JSON.

---

## Auth — `/api/auth/`

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/auth/login/` | Login, returns JWT tokens | `{ email, password }` |
| POST | `/api/auth/signup/` | Register new employee account | `{ name, email, password, department? }` |
| POST | `/api/auth/token/refresh/` | Refresh access token | `{ refresh }` |

**Login response:**
```json
{
  "access": "<token>",
  "refresh": "<token>",
  "user": { "id", "name", "email", "role" }
}
```

---

## Departments — `/api/departments/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/departments/` | List all departments |
| POST | `/api/departments/` | Create department |
| GET | `/api/departments/:id/` | Get single department |
| PATCH | `/api/departments/:id/` | Update department |
| DELETE | `/api/departments/:id/` | Delete department |
| POST | `/api/departments/:id/activate/` | Set status to Active |
| POST | `/api/departments/:id/deactivate/` | Set status to Inactive |

**Department object:**
```json
{
  "id", "name", "head", "parent", "status"
}
```

---

## Categories — `/api/categories/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List all categories |
| POST | `/api/categories/` | Create category |
| GET | `/api/categories/:id/` | Get single category |
| PATCH | `/api/categories/:id/` | Update category |
| DELETE | `/api/categories/:id/` | Delete category |

**Category object:**
```json
{
  "id", "name", "fields": [{ "key", "label" }]
}
```

---

## Employees — `/api/employees/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | List all employees |
| POST | `/api/employees/` | Create employee |
| GET | `/api/employees/:id/` | Get single employee |
| PATCH | `/api/employees/:id/` | Update employee |
| POST | `/api/employees/:id/promote/` | Promote employee role |
| POST | `/api/employees/:id/toggle-status/` | Toggle Active / Inactive |

**Employee object:**
```json
{
  "id", "name", "email", "department", "role", "status"
}
```

**Roles:** `Admin`, `Asset Manager`, `Department Head`, `Employee`

---

## Assets — `/api/assets/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets/` | List all assets (supports `?status=&category=&department=&search=`) |
| POST | `/api/assets/` | Register new asset |
| GET | `/api/assets/:id/` | Get single asset |
| PATCH | `/api/assets/:id/` | Update asset (including status change) |

**Asset object:**
```json
{
  "id", "tag", "name", "category", "department",
  "status", "purchaseDate", "value"
}
```

**Status values:** `Available` → `Allocated` / `Reserved` / `Maintenance` → `Lost` / `Retired` / `Disposed`

---

## Allocations — `/api/allocations/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/allocations/` | List all allocations |
| POST | `/api/allocations/` | Create allocation (also updates asset status to Allocated) |
| GET | `/api/allocations/:id/` | Get single allocation |
| POST | `/api/allocations/:id/return/` | Mark allocation as returned |

**Allocation object:**
```json
{
  "id", "asset", "assetName", "assignedTo",
  "department", "from", "to", "status"
}
```

**Status values:** `Active` → `Returned`

---

## Transfers — `/api/transfers/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transfers/` | List all transfer requests |
| POST | `/api/transfers/` | Create transfer request |
| GET | `/api/transfers/:id/` | Get single transfer |
| POST | `/api/transfers/:id/approve/` | Approve transfer |
| POST | `/api/transfers/:id/reject/` | Reject transfer |

**Transfer object:**
```json
{
  "id", "asset", "assetName", "from",
  "to", "requestedBy", "status"
}
```

**Status values:** `Pending` → `Approved` / `Rejected` → `Reallocated`

---

## Bookings — `/api/bookings/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookings/` | List all bookings (supports `?resourceTag=&date=`) |
| POST | `/api/bookings/` | Create booking — backend must validate no slot overlap |
| GET | `/api/bookings/:id/` | Get single booking |
| POST | `/api/bookings/:id/cancel/` | Cancel booking |

**Booking object:**
```json
{
  "id", "resource", "resourceTag", "bookedBy",
  "date", "from", "to", "status"
}
```

**Status values:** `Upcoming` → `Ongoing` → `Completed` / `Cancelled`

> ⚠️ **Conflict validation required on backend:** reject POST if another booking exists for same `resourceTag` + `date` with overlapping `from`/`to` and status not `Cancelled`/`Completed`.

---

## Maintenance — `/api/maintenance/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/maintenance/` | List all maintenance requests |
| POST | `/api/maintenance/` | Raise new request |
| GET | `/api/maintenance/:id/` | Get single request |
| POST | `/api/maintenance/:id/approve/` | Approve request |
| POST | `/api/maintenance/:id/reject/` | Reject request |
| POST | `/api/maintenance/:id/assign/` | Assign technician — body: `{ assignee }` |
| POST | `/api/maintenance/:id/start/` | Set status to In Progress |
| POST | `/api/maintenance/:id/resolve/` | Set status to Resolved |

**Maintenance object:**
```json
{
  "id", "asset", "assetName", "issue",
  "priority", "status", "assignee", "raised"
}
```

**Priority values:** `Low`, `Medium`, `High`

**Status machine:** `Pending` → `Approved` / `Rejected` → `In Progress` → `Resolved`

---

## Audits — `/api/audits/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/audits/` | List all audit cycles |
| POST | `/api/audits/` | Create audit cycle (auto-populate items from department assets) |
| GET | `/api/audits/:id/` | Get audit with all items |
| POST | `/api/audits/:id/close/` | Close audit cycle |
| PATCH | `/api/audits/:id/items/:itemId/` | Update audit item status |

**Audit object:**
```json
{
  "id", "name", "department", "status", "startDate",
  "items": [{ "id", "tag", "name", "status" }]
}
```

**Audit status:** `In Progress` → `Closed`

**Item status:** `Pending` → `Verified` / `Missing`

---

## Reports — `/api/reports/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/utilization/` | Asset utilization by department — `[{ dept, allocated, available }]` |
| GET | `/api/reports/maintenance-frequency/` | Maintenance requests per month — `[{ month, requests }]` |
| GET | `/api/reports/booking-heatmap/` | Booking counts by slot + day — `[{ slot, Mon, Tue, Wed, Thu, Fri }]` |
| GET | `/api/reports/asset-status-breakdown/` | Asset counts by status — `[{ name, value }]` |
| GET | `/api/reports/booking-trend/` | Bookings per day this week — `[{ day, bookings }]` |

---

## Activity Logs — `/api/logs/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/logs/` | List all activity logs (supports `?module=&search=`) |

**Log object:**
```json
{
  "id", "user", "action", "target",
  "detail", "time", "module"
}
```

**Action values:** `ALLOCATE`, `BOOK`, `TRANSFER`, `MAINTENANCE`, `OVERDUE`, `CREATE`, `CANCEL`, `AUDIT`, `VERIFY`

**Module values:** `Allocation`, `Booking`, `Transfer`, `Maintenance`, `Asset`, `Audit`

---

## Frontend Routes (for reference)

| Route | Page |
|-------|------|
| `/login` | Login |
| `/signup` | Signup |
| `/dashboard` | Dashboard |
| `/org-setup` | Organization Setup (Departments, Categories, Employees) |
| `/assets` | Asset Registry |
| `/allocations` | Allocation & Transfer |
| `/bookings` | Resource Booking |
| `/maintenance` | Maintenance |
| `/audits` | Audit Cycles |
| `/reports` | Reports & Analytics |
| `/activity` | Activity & Notifications |
