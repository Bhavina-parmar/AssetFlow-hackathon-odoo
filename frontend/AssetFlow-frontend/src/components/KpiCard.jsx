import './KpiCard.css';

export default function KpiCard({ label, value, trend, up }) {
  return (
    <div className="kpi-card">
      <div className="kpi-value mono">{value}</div>
      <div className="kpi-bottom">
        <div className="kpi-label">{label}</div>
        {trend && (
          <span className={'kpi-trend ' + (up ? 'kpi-trend--up' : 'kpi-trend--down')}>
            {up ? '↑' : '↓'} {trend}
          </span>
        )}
      </div>
    </div>
  );
}
