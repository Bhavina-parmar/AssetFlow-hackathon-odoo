import { useState, useEffect } from 'react';
import AppLayout from '../components/AppLayout';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line,
} from 'recharts';
import { api } from '../api';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MAX_HEAT = 8;

const heatColor = (val) => {
  const intensity = Math.min(val / MAX_HEAT, 1);
  const r = Math.round(52 + (52 - 52) * intensity);
  const g = Math.round(87 + (87 - 87) * intensity);
  const b = Math.round(213 + (213 - 213) * intensity);
  return `rgba(52, 87, 213, ${0.1 + intensity * 0.85})`;
};

export default function Reports() {
  const [utilizationByDept, setUtilizationByDept] = useState([]);
  const [maintenanceFrequency, setMaintenanceFrequency] = useState([]);
  const [bookingHeatmap, setBookingHeatmap] = useState([]);

  useEffect(() => {
    async function loadReports() {
      try {
        const [util, maint, heat] = await Promise.all([
          api.reports.utilization(),
          api.reports.maintenanceFreq(),
          api.reports.bookingHeatmap(),
        ]);
        setUtilizationByDept(util || []);
        setMaintenanceFrequency(maint || []);
        setBookingHeatmap(heat || []);
      } catch (err) {
        console.error(err);
      }
    }
    loadReports();
  }, []);

  return (
    <AppLayout title="Reports & Analytics" subtitle="Utilization, maintenance trends, and booking patterns.">

      {/* Utilization by department */}
      <div className="card dash-panel" style={{ marginBottom: 24 }}>
        <div className="dash-panel-header">
          <h3>Asset utilization by department</h3>
        </div>
        <div style={{ padding: '16px 24px', height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={utilizationByDept} barSize={24} margin={{ left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
              <XAxis dataKey="department__name" tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid var(--line)' }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="allocated_count" name="Allocated" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="available_count" name="Available" fill="var(--status-available)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Maintenance frequency */}
      <div className="card dash-panel" style={{ marginBottom: 24 }}>
        <div className="dash-panel-header">
          <h3>Maintenance requests — last 6 months</h3>
        </div>
        <div style={{ padding: '16px 24px', height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={maintenanceFrequency} margin={{ left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: 'var(--muted)' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid var(--line)' }} />
              <Line type="monotone" dataKey="requests" stroke="var(--accent)" strokeWidth={2} dot={{ r: 4, fill: 'var(--accent)' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Booking heatmap */}
      <div className="card dash-panel">
        <div className="dash-panel-header">
          <h3>Booking heatmap — this week</h3>
          <span style={{ fontSize: 12, color: 'var(--muted)' }}>Darker = more bookings</span>
        </div>
        <div style={{ padding: '16px 24px', overflowX: 'auto' }}>
          <table style={{ borderCollapse: 'separate', borderSpacing: 4, width: '100%' }}>
            <thead>
              <tr>
                <th style={{ fontSize: 11, color: 'var(--muted)', textAlign: 'left', paddingBottom: 8, width: 60 }}>Slot</th>
                {DAYS.map((d) => (
                  <th key={d} style={{ fontSize: 11, color: 'var(--muted)', textAlign: 'center', paddingBottom: 8 }}>{d}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bookingHeatmap.map((row) => (
                <tr key={row.slot}>
                  <td style={{ fontSize: 12, color: 'var(--muted)', fontFamily: 'var(--font-mono)', paddingRight: 8 }}>{row.slot}</td>
                  {DAYS.map((d) => (
                    <td key={d} style={{ textAlign: 'center', padding: 2 }}>
                      <div style={{
                        background: heatColor(row[d] || 0),
                        borderRadius: 6,
                        padding: '10px 0',
                        fontSize: 12,
                        fontFamily: 'var(--font-mono)',
                        color: (row[d] || 0) >= 5 ? '#fff' : 'var(--ink)',
                      }}>
                        {row[d] || 0}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
              {bookingHeatmap.length === 0 && (
                <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--muted)', padding: '16px' }}>No booking data.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
}
