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
