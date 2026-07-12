# AssetFlow

A full-stack enterprise asset management system built for the Odoo Hackathon. Tracks physical assets across departments — from procurement to disposal — with allocation, booking, maintenance, and audit workflows baked in.

---

## Why we built this

Most companies track assets in spreadsheets. When something goes missing, nobody knows who had it last. When a laptop needs repair, emails go back and forth for days. AssetFlow fixes that by giving every stakeholder — admins, managers, and regular employees — a purpose-built interface that matches how they actually work.

---

## What it does

**Asset Registry** — Every asset gets a unique auto-generated tag (AF-0001, AF-0002...). You can filter by status, department, or category, and see the full lifecycle of any item at a glance.

**Allocations & Transfers** — Allocate assets to employees with expected return dates. The system blocks allocation if an asset is already held. Transfer requests go through an approval workflow before ownership actually changes.

**Resource Booking** — Shared resources (conference rooms, vehicles, projectors) can be booked by timeslot. The system validates for overlaps and prevents double-booking at the database level.

**Maintenance** — Anyone can raise a request. It goes through a multi-step workflow: Pending → Approved → Technician Assigned → In Progress → Resolved. Asset status automatically flips to UNDER_MAINTENANCE on approval and back to AVAILABLE on resolution.

**Audit Cycles** — Create an audit scoped to a department. The system pulls all matching assets and creates checklist items. Auditors mark each item as Verified, Missing, or Damaged. On closing the cycle, assets marked Missing are automatically transitioned to LOST.

**Reports** — Asset utilization by frequency, maintenance requests by asset and category, booking heatmap by day and time slot, and dashboard KPIs.

**Activity Log** — Every action in the system is recorded with actor, timestamp, and target. Admins see everything; employees see logs relevant to them.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Recharts |
| Backend | Django 6, Django REST Framework |
| Auth | DRF Token Authentication |
| Database | SQLite (dev) — swap DATABASE_URL for PostgreSQL in prod |
| Styling | Vanilla CSS with custom design tokens |

No heavy frameworks were used on the frontend by choice — the codebase stays approachable without a build-time CSS framework eating into bundle size.

---

## Project structure

```
AssetFlow-hackathon-odoo/
├── backend/
│   ├── assetflow/          # Django project settings, URLs, permissions
│   ├── users/              # Custom User model, auth endpoints, employee CRUD
│   ├── org/                # Departments, Categories
│   ├── assets/             # Asset registry, tagging, history
│   ├── allocations/        # Allocations, transfer requests
│   ├── bookings/           # Resource booking with overlap validation
│   ├── maintenance/        # Maintenance request lifecycle
│   ├── audits/             # Audit cycles and item verification
│   └── activity/           # Activity logs, dashboard KPIs, reports
├── frontend/
│   └── AssetFlow-frontend/
│       └── src/
│           ├── api.js              # Central fetch wrapper (all API calls live here)
│           ├── context/AppContext  # Global state — all mutations go through here
│           ├── pages/              # One file per page
│           ├── components/         # Shared UI (Modal, StatusBadge, AppLayout...)
│           └── data/mockData.js    # Legacy seed data (no longer used by the app)
└── seed_data.py            # One-shot script to populate the database for testing
```

---

## Roles & permissions

| Role | Can do |
|---|---|
| `ADMIN` | Everything. Create departments, promote employees, full access to all data. |
| `ASSET_MANAGER` | Register assets, allocate, approve maintenance and transfers. |
| `DEPT_HEAD` | Allocate within their department, approve transfers. |
| `EMPLOYEE` | Raise maintenance, book resources, view their own allocations. |

Role is enforced on the backend on every request — frontend just hides buttons based on role, but the API rejects unauthorized calls anyway.

---

## Getting started

You need Python 3.10+ and Node 18+.

### Backend

```bash
cd backend
pip install -r requirements.txt   # or pip3
python3 manage.py migrate
python3 manage.py runserver
```

The API will be at `http://localhost:8000/api/`.

**To seed test data** (creates users, departments, assets, a booking, a maintenance request, and an audit cycle):

```bash
python3 seed_data.py
```

### Frontend

```bash
cd frontend/AssetFlow-frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`. Vite is configured to proxy all `/api` requests to port 8000, so no CORS fiddling needed in dev.

---

## Test accounts (after running seed_data.py)

| Email | Password | Role |
|---|---|---|
| admin@assetflow.com | admin123 | Admin |
| manager@assetflow.com | manager123 | Asset Manager |
| alice@assetflow.com | alice123 | Employee |
| bob@assetflow.com | bob123 | Employee |

---

## API overview

All endpoints are under `/api/` and require `Authorization: Token <your_token>` except for login and signup.

```
POST   /api/auth/login/                     Get token
POST   /api/auth/signup/                    Register account

GET    /api/departments/                    List departments
POST   /api/departments/                    Create department (Admin/Dept Head)
POST   /api/departments/{id}/activate/      Activate department
POST   /api/departments/{id}/deactivate/    Deactivate department

GET    /api/categories/                     List categories
POST   /api/categories/                     Create category (Admin)

GET    /api/employees/                      List all users
POST   /api/employees/{id}/promote/         Change user role (Admin)
POST   /api/employees/{id}/toggle-status/   Enable / disable user (Admin)

GET    /api/assets/                         List assets (filter: status, category, department)
POST   /api/assets/                         Register asset (Asset Manager+)
PATCH  /api/assets/{id}/                    Update asset
GET    /api/assets/{id}/history/            Full lifecycle history

GET    /api/allocations/                    List allocations
POST   /api/allocations/                    Allocate asset → returns 409 if asset is held
POST   /api/allocations/{id}/return/        Return asset

GET    /api/transfers/                      List transfer requests
POST   /api/transfers/                      Submit transfer request
POST   /api/transfers/{id}/approve/         Approve (closes old allocation, creates new one)
POST   /api/transfers/{id}/reject/          Reject

GET    /api/bookings/                       List bookings
POST   /api/bookings/                       Book resource (server validates overlap)
POST   /api/bookings/{id}/cancel/           Cancel booking
GET    /api/resources/{id}/bookings/        Calendar view for a specific resource

GET    /api/maintenance/                    List maintenance requests
POST   /api/maintenance/                    Raise request
POST   /api/maintenance/{id}/approve/       Approve → asset goes UNDER_MAINTENANCE
POST   /api/maintenance/{id}/reject/        Reject
POST   /api/maintenance/{id}/assign-technician/  Assign technician
POST   /api/maintenance/{id}/start/         Mark in progress
POST   /api/maintenance/{id}/resolve/       Resolve → asset goes back to AVAILABLE

GET    /api/audit-cycles/                   List audit cycles
POST   /api/audit-cycles/                   Create cycle (auto-populates items from dept)
POST   /api/audit-cycles/{id}/close/        Close cycle (MISSING assets → LOST)
GET    /api/audit-cycles/{id}/discrepancies/ Items not yet verified
GET    /api/audit-items/?cycle={id}         Items for a cycle
POST   /api/audit-items/{id}/mark/          Mark item result

GET    /api/dashboard/kpis/                 Available, allocated, maintenance counts, overdue
GET    /api/reports/utilization/            Most-used assets, idle assets
GET    /api/reports/maintenance-frequency/  Grouped by asset and category
GET    /api/reports/asset-status-breakdown/ Pie chart data
GET    /api/reports/booking-trend/          Bookings by day this week
GET    /api/reports/booking-heatmap/        Bookings by hour × weekday
GET    /api/logs/                           Activity log (filterable by module and search)
```

Full details with request/response examples are in [`backend/API_ENDPOINTS.md`](backend/API_ENDPOINTS.md).

---

## Asset status transitions

Assets follow a strict state machine. The backend enforces valid transitions and rejects invalid ones.

```
AVAILABLE ──allocate──► ALLOCATED
AVAILABLE ──book──────► RESERVED
AVAILABLE ──maintain──► UNDER_MAINTENANCE
ALLOCATED ──return────► AVAILABLE
RESERVED  ──cancel────► AVAILABLE
UNDER_MAINTENANCE ──resolve──► AVAILABLE
AVAILABLE ──write-off──► LOST | RETIRED | DISPOSED
```

---

## Maintenance lifecycle

```
PENDING
  ├── approve ──► APPROVED
  │                └── assign-technician ──► TECHNICIAN_ASSIGNED
  │                                              └── start ──► IN_PROGRESS
  │                                                                └── resolve ──► RESOLVED
  └── reject ──► REJECTED
```

---

## Known limitations / things we'd do differently with more time

- **No pagination** — the list endpoints return all records. Fine for a hackathon demo, would need cursor-based pagination in prod.
- **File uploads are stored locally** — asset photos and maintenance photos write to `backend/media/`. That needs to move to S3 or similar before production.
- **No refresh tokens** — DRF token auth doesn't expire. We'd add expiring JWT tokens in a production deployment.
- **Audit item marking** checks that the user is in `cycle.auditors` — but the seed data adds auditors properly. If you create a cycle manually via the UI, you'd need to add yourself via admin or API.
- **Department-based transfers** — the UI currently transfers to an employee directly (which matches the backend model). Department-to-department transfer routing is a planned feature.

---

## Contributing

If you're picking this up after the hackathon:

1. Fork, branch off `main`, PR back.
2. Backend changes: add migrations if you touch models, update `API_ENDPOINTS.md` if you add/change routes.
3. Frontend changes: new API calls go in `api.js` first, context mutations in `AppContext.jsx`, then consume in the page.
4. Don't add new packages without a reason. The dependency count is intentionally low.

---

## License

MIT. Built during the Odoo Hackathon 2026.
