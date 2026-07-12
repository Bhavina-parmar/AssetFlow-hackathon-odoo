const BASE = '/api';

function getToken() {
  return localStorage.getItem('af_token');
}

function getHeaders() {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Token ${token}` } : {}),
  };
}

async function request(endpoint, options = {}) {
  const url = `${BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: { ...getHeaders(), ...options.headers },
  });

  // Handle 204 No Content
  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw {
      status: response.status,
      error: data?.detail || data?.error || 'An error occurred',
      data,
    };
  }
  return data;
}

export const api = {
  auth: {
    login: (email, password) => request('/auth/login/', { method: 'POST', body: JSON.stringify({ email, password }) }),
    signup: (data) => request('/auth/signup/', { method: 'POST', body: JSON.stringify(data) }),
  },
  departments: {
    list: () => request('/departments/'),
    create: (data) => request('/departments/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/departments/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
    activate: (id) => request(`/departments/${id}/activate/`, { method: 'POST' }),
    deactivate: (id) => request(`/departments/${id}/deactivate/`, { method: 'POST' }),
  },
  categories: {
    list: () => request('/categories/'),
    create: (data) => request('/categories/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/categories/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id) => request(`/categories/${id}/`, { method: 'DELETE' }),
  },
  employees: {
    list: () => request('/employees/'),
    create: (data) => request('/employees/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/employees/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
    promote: (id, role) => request(`/employees/${id}/promote/`, { method: 'POST', body: JSON.stringify({ role }) }),
    toggleStatus: (id) => request(`/employees/${id}/toggle-status/`, { method: 'POST' }),
  },
  assets: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/assets/${qs ? '?' + qs : ''}`);
    },
    create: (data) => request('/assets/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/assets/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
    history: (id) => request(`/assets/${id}/history/`),
  },
  allocations: {
    list: () => request('/allocations/'),
    create: (data) => request('/allocations/', { method: 'POST', body: JSON.stringify(data) }),
    return: (id, note) => request(`/allocations/${id}/return/`, { method: 'POST', body: JSON.stringify({ condition_note: note }) }),
  },
  transfers: {
    list: () => request('/transfers/'),
    create: (data) => request('/transfers/', { method: 'POST', body: JSON.stringify(data) }),
    approve: (id) => request(`/transfers/${id}/approve/`, { method: 'POST' }),
    reject: (id) => request(`/transfers/${id}/reject/`, { method: 'POST' }),
  },
  bookings: {
    list: () => request('/bookings/'),
    create: (data) => request('/bookings/', { method: 'POST', body: JSON.stringify(data) }),
    cancel: (id) => request(`/bookings/${id}/cancel/`, { method: 'POST' }),
    resourceCalendar: (id) => request(`/resources/${id}/bookings/`),
  },
  maintenance: {
    list: () => request('/maintenance/'),
    raise: (data) => request('/maintenance/', { method: 'POST', body: JSON.stringify(data) }),
    approve: (id) => request(`/maintenance/${id}/approve/`, { method: 'POST' }),
    reject: (id) => request(`/maintenance/${id}/reject/`, { method: 'POST' }),
    assign: (id, techId) => request(`/maintenance/${id}/assign-technician/`, { method: 'POST', body: JSON.stringify({ technician: techId }) }),
    start: (id) => request(`/maintenance/${id}/start/`, { method: 'POST' }),
    resolve: (id) => request(`/maintenance/${id}/resolve/`, { method: 'POST' }),
  },
  audits: {
    listCycles: () => request('/audit-cycles/'),
    createCycle: (data) => request('/audit-cycles/', { method: 'POST', body: JSON.stringify(data) }),
    closeCycle: (id) => request(`/audit-cycles/${id}/close/`, { method: 'POST' }),
    discrepancies: (id) => request(`/audit-cycles/${id}/discrepancies/`),
    listItems: (cycleId) => request(`/audit-items/?cycle=${cycleId}`),
    markItem: (id, result) => request(`/audit-items/${id}/mark/`, { method: 'POST', body: JSON.stringify({ result }) }),
  },
  reports: {
    kpis: () => request('/dashboard/kpis/'),
    utilization: (days = 30) => request(`/reports/utilization/?idle_days=${days}`),
    maintenanceFreq: () => request('/reports/maintenance-frequency/'),
    assetStatusBreakdown: () => request('/reports/asset-status-breakdown/'),
    bookingTrend: () => request('/reports/booking-trend/'),
    bookingHeatmap: () => request('/reports/booking-heatmap/'),
  },
  logs: {
    list: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/logs/${qs ? '?' + qs : ''}`);
    },
  },
};
