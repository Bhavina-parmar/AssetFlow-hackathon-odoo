// Central mock data store. Swap this module out for real API calls later —
// every consumer reads through AppContext, not this file directly.

export const initialDepartments = [
  { id: 'd1', name: 'Engineering', head: 'Priya Nair', parent: null, status: 'Active' },
  { id: 'd2', name: 'Facilities', head: 'Raj Mehta', parent: null, status: 'Active' },
  { id: 'd3', name: 'Field Support', head: '—', parent: 'd1', status: 'Active' },
  { id: 'd4', name: 'Finance', head: 'Ananya Rao', parent: null, status: 'Inactive' },
];

export const initialCategories = [
  {
    id: 'c1',
    name: 'Electronics',
    fields: [{ key: 'warrantyMonths', label: 'Warranty period (months)' }],
  },
  { id: 'c2', name: 'Furniture', fields: [] },
  {
    id: 'c3',
    name: 'Vehicles',
    fields: [{ key: 'plateNumber', label: 'Plate number' }],
  },
  { id: 'c4', name: 'Rooms & Spaces', fields: [] },
];

export const initialEmployees = [
  {
    id: 'e1',
    name: 'Priya Nair',
    email: 'priya.nair@company.com',
    department: 'Engineering',
    role: 'Department Head',
    status: 'Active',
  },
  {
    id: 'e2',
    name: 'Raj Mehta',
    email: 'raj.mehta@company.com',
    department: 'Facilities',
    role: 'Department Head',
    status: 'Active',
  },
  {
    id: 'e3',
    name: 'Ananya Rao',
    email: 'ananya.rao@company.com',
    department: 'Finance',
    role: 'Employee',
    status: 'Active',
  },
  {
    id: 'e4',
    name: 'Kabir Sen',
    email: 'kabir.sen@company.com',
    department: 'Engineering',
    role: 'Asset Manager',
    status: 'Active',
  },
  {
    id: 'e5',
    name: 'Divya Shah',
    email: 'divya.shah@company.com',
    department: 'Field Support',
    role: 'Employee',
    status: 'Active',
  },
  {
    id: 'e6',
    name: 'Arjun Verma',
    email: 'arjun.verma@company.com',
    department: 'Engineering',
    role: 'Employee',
    status: 'Inactive',
  },
];

export const dashboardKpis = [
  { key: 'assetsAvailable',  label: 'Assets available',   value: 128, trend: '+4',  up: true  },
  { key: 'assetsAllocated',  label: 'Assets allocated',   value: 214, trend: '+12', up: true  },
  { key: 'maintenanceToday', label: 'Maintenance today',  value: 6,   trend: '+2',  up: false },
  { key: 'activeBookings',   label: 'Active bookings',    value: 17,  trend: '+3',  up: true  },
  { key: 'pendingTransfers', label: 'Pending transfers',  value: 4,   trend: '-1',  up: true  },
  { key: 'upcomingReturns',  label: 'Upcoming returns',   value: 9,   trend: '+1',  up: false },
];

export const maintenanceAlerts = [
  { id: 'm1', asset: 'AF-0114', assetName: 'Dell Latitude 5440',     status: 'In Progress', assignee: 'Tech — Ravi K.',  due: 'Today' },
  { id: 'm2', asset: 'AF-0302', assetName: 'AC Unit — Floor 3',      status: 'Pending',     assignee: 'Unassigned',      due: 'Tomorrow' },
  { id: 'm3', asset: 'AF-0089', assetName: 'Canon Printer MF445',    status: 'Approved',    assignee: 'Tech — Sneha P.', due: 'Jul 18' },
];

export const overdueReturns = [
  { id: 'r1', asset: 'AF-0114', assetName: 'Dell Latitude 5440', holder: 'Priya Nair', dueDate: '2026-07-05' },
  { id: 'r2', asset: 'AF-0231', assetName: 'Projector — EPX210', holder: 'Field Support', dueDate: '2026-07-08' },
];

export const upcomingReturns = [
  { id: 'u1', asset: 'AF-0087', assetName: 'MacBook Pro 14"', holder: 'Kabir Sen', dueDate: '2026-07-16' },
  { id: 'u2', asset: 'AF-0192', assetName: 'Toyota Innova — Fleet 3', holder: 'Facilities', dueDate: '2026-07-18' },
  { id: 'u3', asset: 'AF-0055', assetName: 'Herman Miller Aeron', holder: 'Ananya Rao', dueDate: '2026-07-20' },
];

export const assetStatusBreakdown = [
  { name: 'Available', value: 128, color: '#1f9d55' },
  { name: 'Allocated', value: 214, color: '#3457d5' },
  { name: 'Maintenance', value: 6, color: '#d9622b' },
  { name: 'Reserved', value: 11, color: '#c98a1d' },
  { name: 'Retired', value: 9, color: '#6b7280' },
];

export const bookingTrend = [
  { day: 'Mon', bookings: 8 },
  { day: 'Tue', bookings: 14 },
  { day: 'Wed', bookings: 11 },
  { day: 'Thu', bookings: 17 },
  { day: 'Fri', bookings: 13 },
  { day: 'Sat', bookings: 4 },
  { day: 'Sun', bookings: 2 },
];

export const recentActivity = [
  { id: 'a1', text: 'Maintenance request for AF-0114 approved', time: '2h ago' },
  { id: 'a2', text: 'Room B2 booked by Divya Shah, 3:00–4:00 PM', time: '3h ago' },
  { id: 'a3', text: 'Transfer of AF-0231 requested by Field Support', time: '5h ago' },
  { id: 'a4', text: 'Audit cycle "Q3 Engineering Floor" closed', time: '1d ago' },
  { id: 'a5', text: 'AF-0192 flagged overdue for return', time: '1d ago' },
];

// ---- Screen 4: Assets ----
export const initialAssets = [
  { id: 'a1', tag: 'AF-0087', name: 'MacBook Pro 14"',        category: 'Electronics', department: 'Engineering',  status: 'Allocated',   purchaseDate: '2023-03-10', value: 180000 },
  { id: 'a2', tag: 'AF-0114', name: 'Dell Latitude 5440',     category: 'Electronics', department: 'Engineering',  status: 'Maintenance', purchaseDate: '2022-11-05', value: 95000  },
  { id: 'a3', tag: 'AF-0192', name: 'Toyota Innova Fleet 3',  category: 'Vehicles',    department: 'Facilities',   status: 'Allocated',   purchaseDate: '2021-06-20', value: 1500000},
  { id: 'a4', tag: 'AF-0231', name: 'Projector EPX210',       category: 'Electronics', department: 'Field Support',status: 'Available',   purchaseDate: '2023-08-14', value: 45000  },
  { id: 'a5', tag: 'AF-0055', name: 'Herman Miller Aeron',    category: 'Furniture',   department: 'Finance',      status: 'Allocated',   purchaseDate: '2022-01-30', value: 62000  },
  { id: 'a6', tag: 'AF-0302', name: 'AC Unit Floor 3',        category: 'Electronics', department: 'Facilities',   status: 'Maintenance', purchaseDate: '2020-09-01', value: 38000  },
  { id: 'a7', tag: 'AF-0410', name: 'Conference Room B2',     category: 'Rooms & Spaces', department: 'Facilities',status: 'Available',   purchaseDate: '2019-01-01', value: 0      },
  { id: 'a8', tag: 'AF-0089', name: 'Canon Printer MF445',    category: 'Electronics', department: 'Engineering',  status: 'Available',   purchaseDate: '2023-05-22', value: 28000  },
];

// ---- Screen 5: Allocations & Transfers ----
export const initialAllocations = [
  { id: 'al1', asset: 'AF-0087', assetName: 'MacBook Pro 14"',       assignedTo: 'Kabir Sen',   department: 'Engineering',  from: '2026-01-10', to: '2026-12-31', status: 'Active'   },
  { id: 'al2', asset: 'AF-0192', assetName: 'Toyota Innova Fleet 3', assignedTo: 'Raj Mehta',   department: 'Facilities',   from: '2026-03-01', to: '2026-09-01', status: 'Active'   },
  { id: 'al3', asset: 'AF-0055', assetName: 'Herman Miller Aeron',   assignedTo: 'Ananya Rao',  department: 'Finance',      from: '2025-06-01', to: '2026-06-01', status: 'Returned' },
];

export const initialTransfers = [
  { id: 't1', asset: 'AF-0231', assetName: 'Projector EPX210',  from: 'Field Support', to: 'Engineering', requestedBy: 'Priya Nair',  status: 'Pending'  },
  { id: 't2', asset: 'AF-0089', assetName: 'Canon Printer MF445', from: 'Engineering', to: 'Finance',     requestedBy: 'Kabir Sen',   status: 'Approved' },
];

// ---- Screen 6: Bookings ----
export const initialBookings = [
  { id: 'b1', resource: 'Conference Room B2', resourceTag: 'AF-0410', bookedBy: 'Divya Shah',  date: '2026-07-14', from: '15:00', to: '16:00', status: 'Upcoming'  },
  { id: 'b2', resource: 'Conference Room B2', resourceTag: 'AF-0410', bookedBy: 'Kabir Sen',   date: '2026-07-14', from: '10:00', to: '11:30', status: 'Completed' },
  { id: 'b3', resource: 'Projector EPX210',   resourceTag: 'AF-0231', bookedBy: 'Priya Nair',  date: '2026-07-15', from: '09:00', to: '10:00', status: 'Upcoming'  },
  { id: 'b4', resource: 'Conference Room B2', resourceTag: 'AF-0410', bookedBy: 'Ananya Rao',  date: '2026-07-15', from: '14:00', to: '15:00', status: 'Cancelled' },
];

// ---- Screen 7: Maintenance ----
export const initialMaintenance = [
  { id: 'mr1', asset: 'AF-0114', assetName: 'Dell Latitude 5440',  issue: 'Screen flickering',      priority: 'High',   status: 'In Progress', assignee: 'Ravi K.',  raised: '2026-07-10' },
  { id: 'mr2', asset: 'AF-0302', assetName: 'AC Unit Floor 3',     issue: 'Not cooling properly',   priority: 'Medium', status: 'Pending',     assignee: '',         raised: '2026-07-12' },
  { id: 'mr3', asset: 'AF-0089', assetName: 'Canon Printer MF445', issue: 'Paper jam recurring',    priority: 'Low',    status: 'Approved',    assignee: 'Sneha P.', raised: '2026-07-11' },
  { id: 'mr4', asset: 'AF-0192', assetName: 'Toyota Innova Fleet 3',issue: 'Engine warning light',  priority: 'High',   status: 'Resolved',    assignee: 'Ravi K.',  raised: '2026-07-01' },
];

// ---- Screen 8: Audit ----
export const initialAudits = [
  {
    id: 'au1', name: 'Q3 Engineering Floor', department: 'Engineering', status: 'In Progress', startDate: '2026-07-01',
    items: [
      { id: 'ai1', tag: 'AF-0087', name: 'MacBook Pro 14"',    status: 'Verified' },
      { id: 'ai2', tag: 'AF-0114', name: 'Dell Latitude 5440', status: 'Missing'  },
      { id: 'ai3', tag: 'AF-0089', name: 'Canon Printer MF445',status: 'Pending'  },
    ],
  },
  {
    id: 'au2', name: 'Facilities Q2 Review', department: 'Facilities', status: 'Closed', startDate: '2026-04-01',
    items: [
      { id: 'ai4', tag: 'AF-0192', name: 'Toyota Innova Fleet 3', status: 'Verified' },
      { id: 'ai5', tag: 'AF-0302', name: 'AC Unit Floor 3',        status: 'Verified' },
    ],
  },
];

// ---- Screen 9: Reports ----
export const utilizationByDept = [
  { dept: 'Engineering',  allocated: 42, available: 18 },
  { dept: 'Facilities',   allocated: 28, available: 12 },
  { dept: 'Field Support',allocated: 15, available: 8  },
  { dept: 'Finance',      allocated: 10, available: 6  },
];

export const maintenanceFrequency = [
  { month: 'Feb', requests: 4  },
  { month: 'Mar', requests: 7  },
  { month: 'Apr', requests: 5  },
  { month: 'May', requests: 9  },
  { month: 'Jun', requests: 6  },
  { month: 'Jul', requests: 11 },
];

export const bookingHeatmap = [
  { slot: '9–10',  Mon: 3, Tue: 5, Wed: 2, Thu: 4, Fri: 1 },
  { slot: '10–11', Mon: 5, Tue: 7, Wed: 6, Thu: 8, Fri: 4 },
  { slot: '11–12', Mon: 2, Tue: 3, Wed: 4, Thu: 3, Fri: 2 },
  { slot: '14–15', Mon: 6, Tue: 4, Wed: 7, Thu: 5, Fri: 3 },
  { slot: '15–16', Mon: 4, Tue: 6, Wed: 5, Thu: 7, Fri: 5 },
  { slot: '16–17', Mon: 1, Tue: 2, Wed: 3, Thu: 2, Fri: 1 },
];

// ---- Screen 10: Activity Logs ----
export const activityLogs = [
  { id: 'l1',  user: 'Kabir Sen',   action: 'ALLOCATE',    target: 'AF-0087', detail: 'Allocated to Kabir Sen',              time: '2026-07-14 09:12', module: 'Allocation'  },
  { id: 'l2',  user: 'Divya Shah',  action: 'BOOK',        target: 'AF-0410', detail: 'Booked Conference Room B2 3–4 PM',    time: '2026-07-14 09:45', module: 'Booking'     },
  { id: 'l3',  user: 'Priya Nair',  action: 'TRANSFER',    target: 'AF-0231', detail: 'Transfer request to Engineering',     time: '2026-07-13 14:20', module: 'Transfer'    },
  { id: 'l4',  user: 'System',      action: 'OVERDUE',     target: 'AF-0192', detail: 'Flagged overdue for return',          time: '2026-07-13 08:00', module: 'Allocation'  },
  { id: 'l5',  user: 'Ravi K.',     action: 'MAINTENANCE', target: 'AF-0114', detail: 'Status updated to In Progress',       time: '2026-07-12 11:30', module: 'Maintenance' },
  { id: 'l6',  user: 'Admin',       action: 'CREATE',      target: 'AF-0302', detail: 'Asset registered',                   time: '2026-07-11 10:00', module: 'Asset'       },
  { id: 'l7',  user: 'Ananya Rao',  action: 'CANCEL',      target: 'AF-0410', detail: 'Booking cancelled',                  time: '2026-07-11 09:15', module: 'Booking'     },
  { id: 'l8',  user: 'Sneha P.',    action: 'MAINTENANCE', target: 'AF-0089', detail: 'Assigned as technician',             time: '2026-07-11 08:45', module: 'Maintenance' },
  { id: 'l9',  user: 'Admin',       action: 'AUDIT',       target: 'Q3 Eng', detail: 'Audit cycle created',                time: '2026-07-01 09:00', module: 'Audit'       },
  { id: 'l10', user: 'Kabir Sen',   action: 'VERIFY',      target: 'AF-0087', detail: 'Marked verified in audit',           time: '2026-07-02 10:30', module: 'Audit'       },
];
