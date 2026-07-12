import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import AppLayout from '../components/AppLayout';
import KpiCard from '../components/KpiCard';
import { useApp } from '../context/AppContext';
import { api } from '../api';
import './Dashboard.css';

const MAINTENANCE_STATUS_STYLE = {
  'PENDING':     { color: 'var(--status-reserved)',    bg: 'var(--status-reserved-bg)'    },
  'APPROVED':    { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  'IN_PROGRESS': { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
};

export default function Dashboard() {
  const { currentUser } = useApp();
  const navigate = useNavigate();

  const [kpis, setKpis] = useState(null);
  const [assetStatus, setAssetStatus] = useState([]);
  const [bookingTrend, setBookingTrend] = useState([]);
  const [maintenanceAlerts, setMaintenanceAlerts] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    async function loadDash() {
      try {
        const [kpiData, statusData, trendData, maints, logs] = await Promise.all([
          api.reports.kpis(),
          api.reports.assetStatusBreakdown(),
          api.reports.bookingTrend(),
          api.maintenance.list(),
          api.logs.list()
        ]);
        
        setKpis(kpiData);
        setAssetStatus(statusData);
        setBookingTrend(trendData);
        
        const activeMaint = maints.filter(m => ['PENDING', 'APPROVED', 'IN_PROGRESS'].includes(m.status));
        setMaintenanceAlerts(activeMaint);
        setRecentActivity(logs.slice(0, 5));
      } catch (err) {
        console.error(err);
      }
    }
    loadDash();
  }, []);

  const dashboardKpis = kpis ? [
    { key: 'k1', label: 'Total available assets', value: kpis.available_count },
    { key: 'k2', label: 'Allocated assets', value: kpis.allocated_count },
    { key: 'k3', label: 'Pending transfers', value: kpis.pending_transfers_count },
    { key: 'k4', label: 'Assets in maintenance', value: kpis.maintenance_count },
  ] : [];

  const overdueReturns = kpis?.overdue_returns || [];

  return (
    <AppLayout
      title={`Welcome back, ${currentUser?.first_name || currentUser?.name?.split(' ')[0] || ''}`}
      subtitle="Here's what's happening across your organization today."
    >
      {/* KPI row */}
      <section className="kpi-grid">
        {dashboardKpis.map((kpi) => (
          <KpiCard key={kpi.key} label={kpi.label} value={kpi.value} trend={kpi.trend} up={kpi.up} />
        ))}
      </section>

      {/* Quick actions */}
      <section className="quick-actions">
        <button className="btn btn-primary" onClick={() => navigate('/assets')}>
          + Register asset
        </button>
        <button className="btn btn-secondary" onClick={() => navigate('/bookings')}>
          + Book resource
        </button>
        <button className="btn btn-secondary" onClick={() => navigate('/maintenance')}>
          + Raise maintenance request
        </button>
        <button className="btn btn-ghost" onClick={() => navigate('/org-setup')}>
          Organization setup →
        </button>
      </section>

      {/* Charts row */}
      <section className="dash-grid" style={{ marginBottom: 'var(--space-5)' }}>
        <div className="card dash-panel">
          <div className="dash-panel-header">
            <h3>Asset status breakdown</h3>
            <span className="mono" style={{ fontSize: 12, color: 'var(--muted)' }}>
              {assetStatus.reduce((s, d) => s + d.value, 0)} total
            </span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={assetStatus}
                  cx="50%"
                  cy="50%"
                  innerRadius={52}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {assetStatus.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v, n) => [v, n]}
                  contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid var(--line)' }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {assetStatus.map((d) => (
                <span key={d.name} className="legend-item">
                  <span className="legend-dot" style={{ background: d.color }} />
                  {d.name} <span className="mono">({d.value})</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="card dash-panel">
          <div className="dash-panel-header">
            <h3>Bookings this week</h3>
            <span className="mono" style={{ fontSize: 12, color: 'var(--muted)' }}>
              {bookingTrend.reduce((s, d) => s + d.bookings, 0)} total
            </span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={bookingTrend} barSize={28} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: 'var(--accent-soft)' }}
                  contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid var(--line)' }}
                />
                <Bar dataKey="bookings" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Maintenance alerts */}
      <div className="card dash-panel" style={{ marginBottom: 'var(--space-5)' }}>
        <div className="dash-panel-header">
          <h3>Maintenance alerts</h3>
          <span className="badge" style={{ color: 'var(--status-maintenance)', background: 'var(--status-maintenance-bg)' }}>
            {maintenanceAlerts.length} active
          </span>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Asset ID</th>
              <th>Status</th>
              <th>Issue</th>
            </tr>
          </thead>
          <tbody>
            {maintenanceAlerts.map((m) => {
              const s = MAINTENANCE_STATUS_STYLE[m.status] || {};
              return (
                <tr key={m.id}>
                  <td>
                    <span className="mono asset-tag">{m.asset}</span>
                  </td>
                  <td>
                    <span className="badge" style={{ color: s.color, background: s.bg }}>
                      {m.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--ink-soft)' }}>{m.issue_text}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Returns tables */}
      <section className="dash-grid" style={{ marginBottom: 'var(--space-5)' }}>
        <div className="card dash-panel" style={{ gridColumn: 'span 2' }}>
          <div className="dash-panel-header">
            <h3>Overdue returns</h3>
            <span className="badge" style={{ color: 'var(--danger)', background: 'var(--danger-soft)' }}>
              {overdueReturns.length} overdue
            </span>
          </div>
          <table className="table">
            <thead>
              <tr><th>Asset ID</th><th>Held by</th><th>Was due</th></tr>
            </thead>
            <tbody>
              {overdueReturns.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="mono asset-tag">{r.asset}</span>
                  </td>
                  <td>{r.employee}</td>
                  <td className="dash-overdue-date">{r.expected_return_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Activity feed */}
      <div className="card dash-panel">
        <div className="dash-panel-header">
          <h3>Recent activity</h3>
        </div>
        <ul className="activity-list">
          {recentActivity.map((a) => (
            <li key={a.id}>
              <span className="activity-dot" />
              <span className="activity-text">{a.meta?.description || a.action}</span>
              <span className="activity-time mono">{new Date(a.timestamp).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </div>
    </AppLayout>
  );
}
