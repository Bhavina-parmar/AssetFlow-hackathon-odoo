import { useNavigate } from 'react-router-dom';
import AppLayout from '../components/AppLayout';
import KpiCard from '../components/KpiCard';
import { useApp } from '../context/AppContext';
import {
  dashboardKpis,
  overdueReturns,
  upcomingReturns,
  recentActivity,
} from '../data/mockData';
import './Dashboard.css';

export default function Dashboard() {
  const { currentUser } = useApp();
  const navigate = useNavigate();

  return (
    <AppLayout
      title={`Welcome back, ${currentUser?.name?.split(' ')[0] || ''}`}
      subtitle="Here's what's happening across your organization today."
    >
      <section className="kpi-grid">
        <KpiCard label="Assets available" value={dashboardKpis.assetsAvailable} />
        <KpiCard label="Assets allocated" value={dashboardKpis.assetsAllocated} />
        <KpiCard label="Maintenance today" value={dashboardKpis.maintenanceToday} />
        <KpiCard label="Active bookings" value={dashboardKpis.activeBookings} />
        <KpiCard label="Pending transfers" value={dashboardKpis.pendingTransfers} />
        <KpiCard label="Upcoming returns" value={dashboardKpis.upcomingReturns} />
      </section>

      <section className="quick-actions">
        <button className="btn btn-primary" onClick={() => alert('Register Asset — coming soon in this build.')}>
          + Register asset
        </button>
        <button className="btn btn-secondary" onClick={() => alert('Book Resource — coming soon in this build.')}>
          + Book resource
        </button>
        <button className="btn btn-secondary" onClick={() => alert('Raise Maintenance Request — coming soon in this build.')}>
          + Raise maintenance request
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/org-setup')}>
          Go to organization setup →
        </button>
      </section>

      <section className="dash-grid">
        <div className="card dash-panel">
          <div className="dash-panel-header">
            <h3>Overdue returns</h3>
            <span className="badge" style={{ color: 'var(--danger)', background: 'var(--danger-soft)' }}>
              {overdueReturns.length} overdue
            </span>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Held by</th>
                <th>Was due</th>
              </tr>
            </thead>
            <tbody>
              {overdueReturns.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="mono asset-tag">{r.asset}</span>
                    <div className="dash-asset-name">{r.assetName}</div>
                  </td>
                  <td>{r.holder}</td>
                  <td className="dash-overdue-date">{r.dueDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card dash-panel">
          <div className="dash-panel-header">
            <h3>Upcoming returns</h3>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Held by</th>
                <th>Due</th>
              </tr>
            </thead>
            <tbody>
              {upcomingReturns.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="mono asset-tag">{r.asset}</span>
                    <div className="dash-asset-name">{r.assetName}</div>
                  </td>
                  <td>{r.holder}</td>
                  <td>{r.dueDate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card dash-panel" style={{ marginTop: 'var(--space-5)' }}>
        <div className="dash-panel-header">
          <h3>Recent activity</h3>
        </div>
        <ul className="activity-list">
          {recentActivity.map((a) => (
            <li key={a.id}>
              <span className="activity-dot" />
              <span className="activity-text">{a.text}</span>
              <span className="activity-time mono">{a.time}</span>
            </li>
          ))}
        </ul>
      </section>
    </AppLayout>
  );
}
