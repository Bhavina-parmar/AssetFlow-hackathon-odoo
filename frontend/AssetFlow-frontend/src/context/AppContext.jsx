import { createContext, useContext, useMemo, useState, useCallback, useEffect } from 'react';
import { api } from '../api';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  
  // States
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [assets, setAssets] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [transfers, setTransfers] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [audits, setAudits] = useState([]);
  const [logs, setLogs] = useState([]);

  // Fetch initial data if logged in
  const fetchAllData = useCallback(async () => {
    try {
      const [
        depts, cats, emps, asts,
        allocs, trans, books, maints,
        audts, lg
      ] = await Promise.all([
        api.departments.list().catch(() => []),
        api.categories.list().catch(() => []),
        api.employees.list().catch(() => []),
        api.assets.list().catch(() => []),
        api.allocations.list().catch(() => []),
        api.transfers.list().catch(() => []),
        api.bookings.list().catch(() => []),
        api.maintenance.list().catch(() => []),
        api.audits.listCycles().catch(() => []),
        api.logs.list().catch(() => []),
      ]);
      setDepartments(depts || []);
      setCategories(cats || []);
      setEmployees(emps || []);
      setAssets(asts || []);
      setAllocations(allocs || []);
      setTransfers(trans || []);
      setBookings(books || []);
      setMaintenance(maints || []);
      setAudits(audts || []);
      setLogs(lg || []);
    } catch (e) {
      console.error('Failed to load initial data', e);
    }
  }, []);

  // Initialize session from token
  useEffect(() => {
    const token = localStorage.getItem('af_token');
    const userStr = localStorage.getItem('af_user');
    if (token && userStr) {
      try {
        setCurrentUser(JSON.parse(userStr));
        fetchAllData();
      } catch (e) {}
    }
  }, [fetchAllData]);

  const addLog = useCallback(() => {
    api.logs.list().then(data => setLogs(data || []));
  }, []);

  // ---- Auth ----
  const login = async (email, password) => {
    try {
      const data = await api.auth.login(email, password);
      localStorage.setItem('af_token', data.token);
      localStorage.setItem('af_user', JSON.stringify(data.user));
      setCurrentUser(data.user);
      fetchAllData();
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.error || 'Login failed' };
    }
  };

  const signup = async (userData) => {
    try {
      const data = await api.auth.signup(userData);
      localStorage.setItem('af_token', data.token);
      localStorage.setItem('af_user', JSON.stringify(data.user));
      setCurrentUser(data.user);
      fetchAllData();
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.error || 'Signup failed' };
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem('af_token');
    localStorage.removeItem('af_user');
    setCurrentUser(null);
  }, []);

  // ---- Departments ----
  const addDepartment = async (dept) => {
    await api.departments.create(dept);
    const data = await api.departments.list();
    setDepartments(data || []);
  };
  const updateDepartment = async (id, patch) => {
    await api.departments.update(id, patch);
    const data = await api.departments.list();
    setDepartments(data || []);
  };
  const toggleDepartmentStatus = async (id) => {
    const d = departments.find(x => x.id === id);
    if (d?.status === 'ACTIVE') {
      await api.departments.deactivate(id);
    } else {
      await api.departments.activate(id);
    }
    const data = await api.departments.list();
    setDepartments(data || []);
  };

  // ---- Categories ----
  const addCategory = async (cat) => {
    await api.categories.create(cat);
    const data = await api.categories.list();
    setCategories(data || []);
  };
  const updateCategory = async (id, patch) => {
    await api.categories.update(id, patch);
    const data = await api.categories.list();
    setCategories(data || []);
  };
  const deleteCategory = async (id) => {
    await api.categories.delete(id);
    const data = await api.categories.list();
    setCategories(data || []);
  };

  // ---- Assets ----
  const addAsset = async (asset) => {
    await api.assets.create(asset);
    const data = await api.assets.list();
    setAssets(data || []);
  };
  const updateAsset = async (id, patch) => {
    await api.assets.update(id, patch);
    const data = await api.assets.list();
    setAssets(data || []);
  };

  // ---- Allocations ----
  const addAllocation = async (al) => {
    await api.allocations.create(al);
    const [allocs, asts] = await Promise.all([api.allocations.list(), api.assets.list()]);
    setAllocations(allocs || []);
    setAssets(asts || []);
  };
  const returnAllocation = async (id, note = '') => {
    await api.allocations.return(id, note);
    const [allocs, asts] = await Promise.all([api.allocations.list(), api.assets.list()]);
    setAllocations(allocs || []);
    setAssets(asts || []);
  };

  // ---- Transfers ----
  const addTransfer = async (tr) => {
    await api.transfers.create(tr);
    const data = await api.transfers.list();
    setTransfers(data || []);
  };
  const updateTransfer = async (id, statusStr) => {
    if (statusStr === 'Approved') await api.transfers.approve(id);
    else if (statusStr === 'Rejected') await api.transfers.reject(id);
    const [trans, allocs, asts] = await Promise.all([api.transfers.list(), api.allocations.list(), api.assets.list()]);
    setTransfers(trans || []);
    setAllocations(allocs || []);
    setAssets(asts || []);
  };

  // ---- Bookings ----
  const addBooking = async (bk) => {
    await api.bookings.create(bk);
    const data = await api.bookings.list();
    setBookings(data || []);
  };
  const cancelBooking = async (id) => {
    await api.bookings.cancel(id);
    const data = await api.bookings.list();
    setBookings(data || []);
  };

  // ---- Maintenance ----
  const addMaintenance = async (mr) => {
    await api.maintenance.raise(mr);
    const data = await api.maintenance.list();
    setMaintenance(data || []);
  };
  const updateMaintenance = async (id, patch) => {
    // Handling status changes via specific endpoints
    if (patch.status === 'Approved') await api.maintenance.approve(id);
    else if (patch.status === 'Rejected') await api.maintenance.reject(id);
    else if (patch.status === 'In Progress') await api.maintenance.start(id);
    else if (patch.status === 'Resolved') await api.maintenance.resolve(id);
    
    if (patch.assignee) {
      await api.maintenance.assign(id, patch.assignee);
    }
    
    const [maints, asts] = await Promise.all([api.maintenance.list(), api.assets.list()]);
    setMaintenance(maints || []);
    setAssets(asts || []);
  };

  // ---- Audits ----
  const addAudit = async (au) => {
    await api.audits.createCycle(au);
    const data = await api.audits.listCycles();
    setAudits(data || []);
  };
  const updateAuditItem = async (auditId, itemId, statusStr) => {
    await api.audits.markItem(itemId, statusStr);
    const data = await api.audits.listCycles(); // In reality, we might need to fetch items per cycle, but we just refresh cycles here
    setAudits(data || []);
  };
  const closeAudit = async (id) => {
    await api.audits.closeCycle(id);
    const data = await api.audits.listCycles();
    setAudits(data || []);
  };

  // ---- Employees & role promotion ----
  const updateEmployee = async (id, patch) => {
    await api.employees.update(id, patch);
    const data = await api.employees.list();
    setEmployees(data || []);
  };

  const promoteEmployee = async (id, role) => {
    await api.employees.promote(id, role);
    const data = await api.employees.list();
    setEmployees(data || []);
  };

  const toggleEmployeeStatus = async (id) => {
    await api.employees.toggleStatus(id);
    const data = await api.employees.list();
    setEmployees(data || []);
  };

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
