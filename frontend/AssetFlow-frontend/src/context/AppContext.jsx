import { createContext, useContext, useMemo, useState, useCallback } from 'react';
import {
  initialDepartments,
  initialCategories,
  initialEmployees,
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
      currentUser,
      login,
      signup,
      logout,
      departments,
      addDepartment,
      updateDepartment,
      toggleDepartmentStatus,
      categories,
      addCategory,
      updateCategory,
      deleteCategory,
      employees,
      updateEmployee,
      promoteEmployee,
      toggleEmployeeStatus,
    }),
    [
      currentUser,
      login,
      signup,
      logout,
      departments,
      addDepartment,
      updateDepartment,
      toggleDepartmentStatus,
      categories,
      addCategory,
      updateCategory,
      deleteCategory,
      employees,
      updateEmployee,
      promoteEmployee,
      toggleEmployeeStatus,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
