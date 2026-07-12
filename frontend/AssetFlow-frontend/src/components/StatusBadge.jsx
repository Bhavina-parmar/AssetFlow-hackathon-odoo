const STATUS_MAP = {
  // Asset
  Available:    { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  Allocated:    { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  Reserved:     { color: 'var(--status-reserved)',    bg: 'var(--status-reserved-bg)'    },
  Maintenance:  { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  Lost:         { color: 'var(--status-lost)',        bg: 'var(--status-lost-bg)'        },
  Retired:      { color: 'var(--status-retired)',     bg: 'var(--status-retired-bg)'     },
  Disposed:     { color: 'var(--status-disposed)',    bg: 'var(--status-disposed-bg)'    },
  // Allocation
  Active:       { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  Returned:     { color: 'var(--muted)',              bg: 'var(--surface-sunken)'         },
  // Transfer / Maintenance
  Pending:      { color: 'var(--status-reserved)',    bg: 'var(--status-reserved-bg)'    },
  Approved:     { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  Rejected:     { color: 'var(--danger)',             bg: 'var(--danger-soft)'            },
  'In Progress':{ color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  Resolved:     { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  Reallocated:  { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  // Booking
  Upcoming:     { color: 'var(--status-allocated)',   bg: 'var(--status-allocated-bg)'   },
  Ongoing:      { color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  Completed:    { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  Cancelled:    { color: 'var(--muted)',              bg: 'var(--surface-sunken)'         },
  // Audit
  'In Progress':{ color: 'var(--status-maintenance)', bg: 'var(--status-maintenance-bg)' },
  Closed:       { color: 'var(--muted)',              bg: 'var(--surface-sunken)'         },
  Verified:     { color: 'var(--status-available)',   bg: 'var(--status-available-bg)'   },
  Missing:      { color: 'var(--danger)',             bg: 'var(--danger-soft)'            },
  // Dept
  Inactive:     { color: 'var(--muted)',              bg: 'var(--surface-sunken)'         },
};

export default function StatusBadge({ status }) {
  const s = STATUS_MAP[status] || { color: 'var(--muted)', bg: 'var(--surface-sunken)' };
  return (
    <span className="badge" style={{ color: s.color, background: s.bg }}>
      {status}
    </span>
  );
}
