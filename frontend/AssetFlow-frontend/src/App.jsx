import { Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import OrgSetup from './pages/OrgSetup';
import Assets from './pages/Assets';
import Allocations from './pages/Allocations';
import Bookings from './pages/Bookings';
import Maintenance from './pages/Maintenance';
import Audits from './pages/Audits';
import Reports from './pages/Reports';
import ActivityLogs from './pages/ActivityLogs';

const Protected = ({ children }) => <ProtectedRoute>{children}</ProtectedRoute>;

export default function App() {
  return (
    <AppProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard"   element={<Protected><Dashboard /></Protected>} />
        <Route path="/org-setup"   element={<Protected><OrgSetup /></Protected>} />
        <Route path="/assets"      element={<Protected><Assets /></Protected>} />
        <Route path="/allocations" element={<Protected><Allocations /></Protected>} />
        <Route path="/bookings"    element={<Protected><Bookings /></Protected>} />
        <Route path="/maintenance" element={<Protected><Maintenance /></Protected>} />
        <Route path="/audits"      element={<Protected><Audits /></Protected>} />
        <Route path="/reports"     element={<Protected><Reports /></Protected>} />
        <Route path="/activity"    element={<Protected><ActivityLogs /></Protected>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AppProvider>
  );
}
