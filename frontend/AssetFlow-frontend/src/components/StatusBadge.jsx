const STATUS_MAP = {
  Active: { color: 'var(--status-available)', bg: 'var(--status-available-bg)' },
  Inactive: { color: 'var(--muted)', bg: 'var(--surface-sunken)' },
  Available: { color: 'var(--status-available)', bg: 'var(--status-available-bg)' },
  Allocated: { color: 'var(--status-allocated)', bg: 'var(--status-allocated-bg)' },
  Reserved: { color: 'var(--status-reserved)', bg: 'var(--status-reserved-bg)' },
  'Under Maintenance': { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  Lost: { color: 'var(--status-lost)', bg: 'var(--status-lost-bg)' },
  Retired: { color: 'var(--status-retired)', bg: 'var(--status-retired-bg)' },
  Disposed: { color: 'var(--status-disposed)', bg: 'var(--status-disposed-bg)' },
};

export default function StatusBadge({ status }) {
  const style = STATUS_MAP[status] || { color: 'var(--muted)', bg: 'var(--surface-sunken)' };
  return (
    <span className="badge" style={{ color: style.color, background: style.bg }}>
      <span className="dot" style={{ background: style.color }} />
      {status}
    </span>
  );
}
