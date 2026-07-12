import { useNavigate } from 'react-router-dom';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import AppLayout from '../components/AppLayout';
import KpiCard from '../components/KpiCard';
import { useApp } from '../context/AppContext';
import {
  dashboardKpis,
  overdueReturns,
  upcomingReturns,
  recentActivity,
  assetStatusBreakdown,
  bookingTrend,
  maintenanceAlerts,
} from '../data/mockData';
import './Dashboard.css';

const MAINTENANCE_STATUS_STYLE = {
  'Pending':     { color: 'var(--status-reserved)',    bg: 'var(--status-reserved-bg)'    },
  'Approved':    { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  'In Progress': { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
};

export default function Dashboard() {
  const { currentUser } = useApp();
  const navigate = useNavigate();

  return (
    <AppLayout
      title={`Welcome back, ${currentUser?.name?.split(' ')[0] || ''}`}
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
        <button className="btn btn-primary" onClick={() => alert('Register Asset — coming soon.')}>
          + Register asset
        </button>
        <button className="btn btn-secondary" onClick={() => alert('Book Resource — coming soon.')}>
          + Book resource
        </button>
        <button className="btn btn-secondary" onClick={() => alert('Raise Maintenance — coming soon.')}>
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
              {assetStatusBreakdown.reduce((s, d) => s + d.value, 0)} total
            </span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={assetStatusBreakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={52}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {assetStatusBreakdown.map((entry) => (
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
              {assetStatusBreakdown.map((d) => (
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
              <th>Asset</th>
              <th>Status</th>
              <th>Assignee</th>
              <th>Due</th>
            </tr>
          </thead>
          <tbody>
            {maintenanceAlerts.map((m) => {
              const s = MAINTENANCE_STATUS_STYLE[m.status] || {};
              return (
                <tr key={m.id}>
                  <td>
                    <span className="mono asset-tag">{m.asset}</span>
                    <div className="dash-asset-name">{m.assetName}</div>
                  </td>
                  <td>
                    <span className="badge" style={{ color: s.color, background: s.bg }}>
                      {m.status}
                    </span>
                  </td>
                  <td style={{ color: 'var(--ink-soft)' }}>{m.assignee}</td>
                  <td className={m.due === 'Today' ? 'dash-overdue-date' : ''}>{m.due}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Returns tables */}
      <section className="dash-grid" style={{ marginBottom: 'var(--space-5)' }}>
        <div className="card dash-panel">
          <div className="dash-panel-header">
            <h3>Overdue returns</h3>
            <span className="badge" style={{ color: 'var(--danger)', background: 'var(--danger-soft)' }}>
              {overdueReturns.length} overdue
            </span>
          </div>
          <table className="table">
            <thead>
              <tr><th>Asset</th><th>Held by</th><th>Was due</th></tr>
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
              <tr><th>Asset</th><th>Held by</th><th>Due</th></tr>
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

      {/* Activity feed */}
      <div className="card dash-panel">
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
      </div>
    </AppLayout>
  );
}
