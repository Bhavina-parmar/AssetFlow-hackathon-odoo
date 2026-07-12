export default function AuthSide() {
  return (
    <div className="auth-side">
      <div className="auth-side-top">
        <span className="auth-side-mark">AF</span>
        <span className="auth-side-brand">AssetFlow</span>
      </div>

      <div className="auth-side-main">
        <div className="auth-side-eyebrow">Asset &amp; resource management</div>
        <h1 className="auth-side-headline">
          Know who holds what, where it is, and its condition — always.
        </h1>
        <p className="auth-side-desc">
          Track assets through their full lifecycle, book shared resources without
          conflicts, and route maintenance and audits through clean, role-based
          workflows.
        </p>
      </div>

      <div className="auth-tags">
        <span className="auth-tag">
          <span className="status-dot" style={{ background: 'var(--status-available)' }} />
          Available
        </span>
        <span className="auth-tag">
          <span className="status-dot" style={{ background: 'var(--status-allocated)' }} />
          Allocated
        </span>
        <span className="auth-tag">
          <span className="status-dot" style={{ background: 'var(--status-reserved)' }} />
          Reserved
        </span>
        <span className="auth-tag">
          <span className="status-dot" style={{ background: 'var(--status-maintenance)' }} />
          Under Maintenance
        </span>
      </div>
    </div>
  );
}
