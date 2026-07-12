# AssetFlow API-Only Seeder

This seeding project populates AssetFlow **only via REST APIs**.

It does **not** use:
- Django ORM
- Direct DB access
- Fixtures
- Management commands

## What It Seeds

In dependency-safe order:

1. Login
2. Departments (10)
3. Employees (35)
4. Role promotions (2 Asset Managers, 6 Department Heads)
5. Department head assignment
6. Categories (10)
7. Assets (150)
8. Allocations (60)
9. Bookings (100, no overlap per resource)
10. Maintenance requests (40, with partial workflow progression)
11. Transfer requests (30, random approve/reject)
12. Audit cycles (2) and audit item marks (20)
13. Dashboard/report verification

## Tech Stack

- Python 3.12
- requests
- faker
- tqdm
- python-dotenv
- random, uuid, datetime (stdlib)

## Configuration

Create a `.env` file in the project root or inside `seed_data/`:

```env
BASE_URL=http://localhost:8000
ADMIN_EMAIL=admin@assetflow.com
ADMIN_PASSWORD=your_admin_password
```

## Install

```bash
cd seed_data
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

From inside `seed_data`:

```bash
python seed.py
```

Or from repository root:

```bash
python seed_data/seed.py
```

## Output Summary

At completion, it prints:

- Departments Created
- Employees Created
- Categories Created
- Assets Created
- Allocations Created
- Bookings Created
- Maintenance Created
- Transfers Created
- Audit Cycles Created
- Total API Calls
- Execution Time

## Notes

- Employee `phone` and `address` are generated for realism and traceability logs, but your current employee API schema does not persist these fields.
- The script is resilient: API calls are retried with exponential backoff and jitter.
- Failures are logged with context and the script continues wherever possible.
