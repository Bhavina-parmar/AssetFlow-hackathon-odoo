import { createContext, useContext, useMemo, useState, useCallback } from 'react';
import {
  initialDepartments,
  initialCategories,
  initialEmployees,
  initialAssets,
  initialAllocations,
  initialTransfers,
  initialBookings,
  initialMaintenance,
  initialAudits,
  activityLogs as seedLogs,
} from '../data/mockData';

const AppContext = createContext(null);

let idCounter = 100;
const nextId = (prefix) => `${prefix}${idCounter++}`;

// Seeded "existing accounts" so login has something to authenticate against.
// In a real backend, passwords are never stored like this — this is mock-only.
const seedAccounts = [
  { email: 'admin@company.com', password: 'admin123', name: 'System Admin', role: 'Admin' },
  { email: 'priya.nair@company.com', password: 'password', name: 'Priya Nair', role: 'Department Head' },
  { email: 'kabir.sen@company.com', password: 'password', name: 'Kabir Sen', role: 'Asset Manager' },
  { email: 'arjun.verma@company.com', password: 'password', name: 'Arjun Verma', role: 'Employee' },
];

export function AppProvider({ children }) {
  const [accounts, setAccounts] = useState(seedAccounts);
  const [currentUser, setCurrentUser] = useState(null);

  const [departments, setDepartments] = useState(initialDepartments);
  const [categories, setCategories] = useState(initialCategories);
  const [employees, setEmployees] = useState(initialEmployees);
  const [assets, setAssets] = useState(initialAssets);
  const [allocations, setAllocations] = useState(initialAllocations);
  const [transfers, setTransfers] = useState(initialTransfers);
  const [bookings, setBookings] = useState(initialBookings);
  const [maintenance, setMaintenance] = useState(initialMaintenance);
  const [audits, setAudits] = useState(initialAudits);
  const [logs, setLogs] = useState(seedLogs);

  const addLog = useCallback((user, action, target, detail, module) => {
    setLogs((prev) => [{ id: `l${Date.now()}`, user, action, target, detail, time: new Date().toISOString().slice(0,16).replace('T',' '), module }, ...prev]);
  }, []);

  // ---- Auth ----
  const login = useCallback(
    (email, password) => {
      const account = accounts.find(
        (a) => a.email.toLowerCase() === email.toLowerCase() && a.password === password
      );
      if (!account) {
        return { ok: false, error: 'Incorrect email or password.' };
      }
      setCurrentUser(account);
      return { ok: true };
    },
    [accounts]
  );

  const signup = useCallback(
    ({ name, email, password, department }) => {
      const exists = accounts.some((a) => a.email.toLowerCase() === email.toLowerCase());
      if (exists) {
        return { ok: false, error: 'An account with this email already exists.' };
      }
      const account = { name, email, password, role: 'Employee' };
      setAccounts((prev) => [...prev, account]);
      // Signup always creates an Employee — mirrors the Employee Directory.
      setEmployees((prev) => [
        ...prev,
        {
          id: nextId('e'),
          name,
          email,
          department: department || '—',
          role: 'Employee',
          status: 'Active',
        },
      ]);
      setCurrentUser(account);
      return { ok: true };
    },
    [accounts]
  );

  const logout = useCallback(() => setCurrentUser(null), []);

  // ---- Departments ----
  const addDepartment = useCallback((dept) => {
    setDepartments((prev) => [
      ...prev,
      { id: nextId('d'), status: 'Active', head: '—', parent: null, ...dept },
    ]);
  }, []);

  const updateDepartment = useCallback((id, patch) => {
    setDepartments((prev) => prev.map((d) => (d.id === id ? { ...d, ...patch } : d)));
  }, []);

  const toggleDepartmentStatus = useCallback((id) => {
    setDepartments((prev) =>
      prev.map((d) =>
        d.id === id ? { ...d, status: d.status === 'Active' ? 'Inactive' : 'Active' } : d
      )
    );
  }, []);

  // ---- Categories ----
  const addCategory = useCallback((cat) => {
    setCategories((prev) => [...prev, { id: nextId('c'), fields: [], ...cat }]);
  }, []);

  const updateCategory = useCallback((id, patch) => {
    setCategories((prev) => prev.map((c) => (c.id === id ? { ...c, ...patch } : c)));
  }, []);

  const deleteCategory = useCallback((id) => {
    setCategories((prev) => prev.filter((c) => c.id !== id));
  }, []);

  // ---- Assets ----
  const addAsset = useCallback((asset) => {
    const tag = `AF-${String(Math.floor(Math.random()*900)+100).padStart(4,'0')}`;
    setAssets((prev) => [...prev, { id: nextId('a'), tag, status: 'Available', ...asset }]);
  }, []);
  const updateAsset = useCallback((id, patch) => setAssets((prev) => prev.map((a) => a.id === id ? { ...a, ...patch } : a)), []);

  // ---- Allocations ----
  const addAllocation = useCallback((al) => {
    setAllocations((prev) => [...prev, { id: nextId('al'), status: 'Active', ...al }]);
    setAssets((prev) => prev.map((a) => a.tag === al.asset ? { ...a, status: 'Allocated' } : a));
  }, []);
  const returnAllocation = useCallback((id) => {
    setAllocations((prev) => prev.map((al) => al.id === id ? { ...al, status: 'Returned' } : al));
  }, []);

  // ---- Transfers ----
  const addTransfer = useCallback((tr) => setTransfers((prev) => [...prev, { id: nextId('t'), status: 'Pending', ...tr }]), []);
  const updateTransfer = useCallback((id, status) => setTransfers((prev) => prev.map((t) => t.id === id ? { ...t, status } : t)), []);

  // ---- Bookings ----
  const addBooking = useCallback((bk) => setBookings((prev) => [...prev, { id: nextId('b'), status: 'Upcoming', ...bk }]), []);
  const cancelBooking = useCallback((id) => setBookings((prev) => prev.map((b) => b.id === id ? { ...b, status: 'Cancelled' } : b)), []);

  // ---- Maintenance ----
  const addMaintenance = useCallback((mr) => setMaintenance((prev) => [...prev, { id: nextId('mr'), status: 'Pending', assignee: '', ...mr }]), []);
  const updateMaintenance = useCallback((id, patch) => setMaintenance((prev) => prev.map((m) => m.id === id ? { ...m, ...patch } : m)), []);

  // ---- Audits ----
  const addAudit = useCallback((au) => setAudits((prev) => [...prev, { id: nextId('au'), status: 'In Progress', items: [], ...au }]), []);
  const updateAuditItem = useCallback((auditId, itemId, status) => {
    setAudits((prev) => prev.map((au) => au.id === auditId
      ? { ...au, items: au.items.map((it) => it.id === itemId ? { ...it, status } : it) }
      : au));
  }, []);
  const closeAudit = useCallback((id) => setAudits((prev) => prev.map((au) => au.id === id ? { ...au, status: 'Closed' } : au)), []);

  // ---- Employees & role promotion ----
  const updateEmployee = useCallback((id, patch) => {
    setEmployees((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)));
  }, []);

  const promoteEmployee = useCallback((id, role) => {
    setEmployees((prev) => prev.map((e) => (e.id === id ? { ...e, role } : e)));
  }, []);

  const toggleEmployeeStatus = useCallback((id) => {
    setEmployees((prev) =>
      prev.map((e) =>
        e.id === id ? { ...e, status: e.status === 'Active' ? 'Inactive' : 'Active' } : e
      )
    );
  }, []);

  const value = useMemo(
    () => ({
      currentUser, login, signup, logout,
      departments, addDepartment, updateDepartment, toggleDepartmentStatus,
      categories, addCategory, updateCategory, deleteCategory,
      employees, updateEmployee, promoteEmployee, toggleEmployeeStatus,
      assets, addAsset, updateAsset,
      allocations, addAllocation, returnAllocation,
      transfers, addTransfer, updateTransfer,
      bookings, addBooking, cancelBooking,
      maintenance, addMaintenance, updateMaintenance,
      audits, addAudit, updateAuditItem, closeAudit,
      logs, addLog,
    }),
    [
      currentUser, login, signup, logout,
      departments, addDepartment, updateDepartment, toggleDepartmentStatus,
      categories, addCategory, updateCategory, deleteCategory,
      employees, updateEmployee, promoteEmployee, toggleEmployeeStatus,
      assets, addAsset, updateAsset,
      allocations, addAllocation, returnAllocation,
      transfers, addTransfer, updateTransfer,
      bookings, addBooking, cancelBooking,
      maintenance, addMaintenance, updateMaintenance,
      audits, addAudit, updateAuditItem, closeAudit,
      logs, addLog,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
