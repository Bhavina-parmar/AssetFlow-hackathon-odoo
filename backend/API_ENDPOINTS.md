# AssetFlow API Endpoints & Fetch Definitions

This document details all the backend endpoints available in **AssetFlow** along with example JavaScript `fetch` code blocks for frontend consumption.

## Global Headers
Most endpoints require authentication. Include the Token authorization header:
```javascript
const getHeaders = (token) => ({
  "Content-Type": "application/json",
  "Authorization": `Token ${token}`
});
```

---

## 1. Authentication & Signup (`users` auth)

### User Login
* **URL:** `/api/auth/login/`
* **Method:** `POST`
* **Auth required:** No
```javascript
fetch("/api/auth/login/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    email: "employee@assetflow.com", // Supports email lookup (case-insensitive) or username
    password: "password123"
  })
})
.then(res => res.json())
.then(data => {
  // Returns: { token: "...", user: { id: 1, name: "John Doe", email: "...", role: "EMPLOYEE", username: "employee" } }
  console.log(data);
});
```

### User Signup
* **URL:** `/api/auth/signup/`
* **Method:** `POST`
* **Auth required:** No
* **Note:** Automatically provisions a unique username from the email prefix. Default role is `EMPLOYEE`.
```javascript
fetch("/api/auth/signup/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    name: "John Doe",
    email: "johndoe@assetflow.com",
    password: "securepassword"
  })
})
.then(res => res.json())
.then(data => {
  // Returns: { token: "...", user: { id: 1, name: "John Doe", email: "...", role: "EMPLOYEE", username: "johndoe" } }
  console.log(data);
});
```

---

## 2. Employee Directory (`users` management)

### List / Search Employees
* **URL:** `/api/employees/?search={query}&role={role}&is_active={bool}`
* **Method:** `GET`
```javascript
// Search for employees with name or email containing 'john'
fetch("/api/employees/?search=john", {
  method: "GET",
  headers: getHeaders(token)
})
.then(res => res.json())
.then(data => console.log(data));
```

### Create Employee Account (Admin Only)
* **URL:** `/api/employees/`
* **Method:** `POST`
```javascript
fetch("/api/employees/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    username: "jane_smith",
    email: "janesmith@assetflow.com",
    first_name: "Jane",
    last_name: "Smith",
    role: "ASSET_MANAGER", // ADMIN, ASSET_MANAGER, DEPT_HEAD, EMPLOYEE
    password: "defaultpassword123"
  })
});
```

### Promote Employee Role (Admin Only)
* **URL:** `/api/employees/{id}/promote/`
* **Method:** `POST`
```javascript
fetch("/api/employees/3/promote/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    role: "DEPT_HEAD" // Choice of ADMIN, ASSET_MANAGER, DEPT_HEAD, EMPLOYEE
  })
})
.then(res => res.json());
```

### Toggle Active Status (Admin Only)
* **URL:** `/api/employees/{id}/toggle-status/`
* **Method:** `POST`
```javascript
fetch("/api/employees/3/toggle-status/", {
  method: "POST",
  headers: getHeaders(token)
})
.then(res => res.json());
```

---

## 3. Organization Setup (`org`)

### List Departments
* **URL:** `/api/departments/`
* **Method:** `GET`
```javascript
fetch("/api/departments/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Create Department (Admin Only)
* **URL:** `/api/departments/`
* **Method:** `POST`
```javascript
fetch("/api/departments/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    name: "Engineering",
    head: 2, // User ID of Department Head
    parent: null // Parent Department ID (optional)
  })
});
```

### Activate Department (Admin Only)
* **URL:** `/api/departments/{id}/activate/`
* **Method:** `POST`
```javascript
fetch("/api/departments/1/activate/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Deactivate Department (Admin Only)
* **URL:** `/api/departments/{id}/deactivate/`
* **Method:** `POST`
```javascript
fetch("/api/departments/1/deactivate/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### List Categories
* **URL:** `/api/categories/`
* **Method:** `GET`
```javascript
fetch("/api/categories/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Create Category (Admin Only)
* **URL:** `/api/categories/`
* **Method:** `POST`
```javascript
fetch("/api/categories/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    name: "Laptops",
    extra_fields: { "ram": "16GB", "storage": "512GB SSD" }
  })
});
```

---

## 4. Assets (`assets`)

### Register Asset (Asset Manager/Admin Only)
* **URL:** `/api/assets/`
* **Method:** `POST`
```javascript
fetch("/api/assets/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    name: "MacBook Pro M3",
    category: 1,
    serial_number: "SN-MBP-1234",
    acquisition_date: "2026-07-12",
    acquisition_cost: "2500.00",
    condition: "NEW", // NEW, GOOD, FAIR, POOR
    location: "HQ-Room-301",
    is_bookable: true
  })
});
```

### List Assets with Filters
* **URL:** `/api/assets/?tag={}&serial_number={}&category={}&status={}&department={}&location={}`
* **Method:** `GET`
```javascript
// Filter by available laptops in HQ
fetch("/api/assets/?category=1&status=AVAILABLE&location=HQ", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Get Asset History
* **URL:** `/api/assets/{id}/history/`
* **Method:** `GET`
```javascript
fetch("/api/assets/1/history/", {
  method: "GET",
  headers: getHeaders(token)
});
```

---

## 5. Allocations & Transfers (`allocations`)

### Create Allocation (Asset Manager/Dept Head Only)
* **URL:** `/api/allocations/`
* **Method:** `POST`
* **Returns HTTP 409 Conflict** with holder details in body if the asset is currently allocated or reserved.
```javascript
fetch("/api/allocations/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    asset: 1,
    employee: 3, // Nullable
    department: 2, // Nullable
    expected_return_date: "2026-08-12",
    condition_note: "Given in brand new condition"
  })
})
.then(response => {
  if (response.status === 409) {
    return response.json().then(err => {
      alert(`Conflict: Currently held by ${err.current_holder.name} (${err.current_holder.department})`);
    });
  }
  return response.json();
});
```

### Return Asset
* **URL:** `/api/allocations/{id}/return/`
* **Method:** `POST`
```javascript
fetch("/api/allocations/1/return/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    condition_note: "Returned with slight scratches"
  })
});
```

### Submit Transfer Request
* **URL:** `/api/transfers/`
* **Method:** `POST`
```javascript
fetch("/api/transfers/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    asset: 1,
    to_employee: 4,
    reason: "Project reassignment"
  })
});
```

### Approve Transfer Request (Asset Manager/Dept Head Only)
* **URL:** `/api/transfers/{id}/approve/`
* **Method:** `POST`
```javascript
fetch("/api/transfers/1/approve/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Reject Transfer Request (Asset Manager/Dept Head Only)
* **URL:** `/api/transfers/{id}/reject/`
* **Method:** `POST`
```javascript
fetch("/api/transfers/1/reject/", {
  method: "POST",
  headers: getHeaders(token)
});
```

---

## 6. Resource Bookings (`bookings`)

### Create Booking
* **URL:** `/api/bookings/`
* **Method:** `POST`
```javascript
fetch("/api/bookings/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    resource: 1, // Asset ID
    start_time: "2026-07-12T14:00:00Z",
    end_time: "2026-07-12T16:00:00Z"
  })
});
```

### Cancel Booking
* **URL:** `/api/bookings/{id}/cancel/`
* **Method:** `POST`
```javascript
fetch("/api/bookings/1/cancel/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Calendar Reservations for Resource
* **URL:** `/api/resources/{id}/bookings/`
* **Method:** `GET`
```javascript
fetch("/api/resources/1/bookings/", {
  method: "GET",
  headers: getHeaders(token)
});
```

---

## 7. Maintenance Requests (`maintenance`)

### Raise Maintenance Request
* **URL:** `/api/maintenance/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    asset: 1,
    issue_text: "Camera doesn't work",
    priority: "HIGH" // LOW, MEDIUM, HIGH, CRITICAL
  })
});
```

### Approve Request (Asset Manager/Admin Only)
* **URL:** `/api/maintenance/{id}/approve/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/1/approve/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Reject Request (Asset Manager/Admin Only)
* **URL:** `/api/maintenance/{id}/reject/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/1/reject/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Assign Technician (Asset Manager/Admin Only)
* **URL:** `/api/maintenance/{id}/assign-technician/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/1/assign-technician/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    technician: 5 // User ID of technician
  })
});
```

### Start Work (Technician/Admin/Manager)
* **URL:** `/api/maintenance/{id}/start/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/1/start/", {
  method: "POST",
  headers: getHeaders(token)
});
```

### Resolve Maintenance (Technician/Admin/Manager)
* **URL:** `/api/maintenance/{id}/resolve/`
* **Method:** `POST`
```javascript
fetch("/api/maintenance/1/resolve/", {
  method: "POST",
  headers: getHeaders(token)
});
```

---

## 8. Verification & Auditing (`audits`)

### Create Audit Cycle
* **URL:** `/api/audit-cycles/`
* **Method:** `POST`
```javascript
fetch("/api/audit-cycles/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    scope_department: 2, // optional filter
    scope_location: "HQ", // optional filter
    start_date: "2026-07-12",
    end_date: "2026-07-20",
    auditors: [5, 6] // User IDs
  })
});
```

### Mark Audit Item Result (Assigned Auditor Only)
* **URL:** `/api/audit-items/{id}/mark/`
* **Method:** `POST`
```javascript
fetch("/api/audit-items/1/mark/", {
  method: "POST",
  headers: getHeaders(token),
  body: JSON.stringify({
    result: "VERIFIED" // VERIFIED, MISSING, DAMAGED
  })
});
```

### Get Discrepancies
* **URL:** `/api/audit-cycles/{id}/discrepancies/`
* **Method:** `GET`
```javascript
fetch("/api/audit-cycles/1/discrepancies/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Close Audit Cycle
* **URL:** `/api/audit-cycles/{id}/close/`
* **Method:** `POST`
```javascript
fetch("/api/audit-cycles/1/close/", {
  method: "POST",
  headers: getHeaders(token)
});
```

---

## 9. Metrics & Analytics (`activity` reports)

### Dashboard KPIs
* **URL:** `/api/dashboard/kpis/`
* **Method:** `GET`
```javascript
fetch("/api/dashboard/kpis/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Asset Status Breakdown Chart Data
* **URL:** `/api/reports/asset-status-breakdown/`
* **Method:** `GET`
* **Description:** Returns count statistics with Tailwind HSL-friendly color hexes.
* **Returns:** `[{ name: "Available", value: 5, color: "#22c55e" }, ...]`
```javascript
fetch("/api/reports/asset-status-breakdown/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Booking Trend Chart Data
* **URL:** `/api/reports/booking-trend/`
* **Method:** `GET`
* **Description:** Returns bookings count day-by-day for the current week.
* **Returns:** `[{ day: "Mon", bookings: 4 }, ...]`
```javascript
fetch("/api/reports/booking-trend/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Booking Hourly Heatmap Data
* **URL:** `/api/reports/booking-heatmap/`
* **Method:** `GET`
* **Description:** Returns booking load slots by hour and weekday.
* **Returns:** `[{ slot: "09:00", Mon: 2, Tue: 0, Wed: 3, Thu: 1, Fri: 4, Sat: 0, Sun: 0 }, ...]`
```javascript
fetch("/api/reports/booking-heatmap/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Asset Utilization Report
* **URL:** `/api/reports/utilization/?idle_days={X}`
* **Method:** `GET`
```javascript
fetch("/api/reports/utilization/?idle_days=45", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Maintenance Frequency Report
* **URL:** `/api/reports/maintenance-frequency/`
* **Method:** `GET`
```javascript
fetch("/api/reports/maintenance-frequency/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### User Notifications Feed
* **URL:** `/api/notifications/`
* **Method:** `GET`
```javascript
fetch("/api/notifications/", {
  method: "GET",
  headers: getHeaders(token)
});
```

### Paginated & Filterable Activity Logs (Admin/Auditor view)
* **URL:** `/api/logs/?module={type}&search={query}`
* **Method:** `GET`
* **Description:** Returns activity logs list. Module filter applies to target type (e.g. Asset). Search matches actor username, target type, or action string.
```javascript
// Fetch logs relating to assets with query 'reserve'
fetch("/api/logs/?module=Asset&search=reserve", {
  method: "GET",
  headers: getHeaders(token)
});
```
