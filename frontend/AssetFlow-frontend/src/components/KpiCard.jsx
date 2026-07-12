import './KpiCard.css';

export default function KpiCard({ label, value, accent = false }) {
  return (
    <div className={'kpi-card' + (accent ? ' is-accent' : '')}>
      <div className="kpi-value mono">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
