function getSeverity(a) {
  const cpu = a.cpu_pct ?? 0;
  const mem = a.mem_pct ?? 0;
  if (cpu >= 80 || mem >= 80) return 'HIGH';
  if (cpu >= 70 || mem >= 70) return 'MEDIUM';
  return 'LOW';
}

function groupBySeverity(anomalies) {
  const groups = { HIGH: [], MEDIUM: [], LOW: [] };
  for (const a of anomalies) groups[getSeverity(a)].push(a);
  return groups;
}

function AnomalyCard({ a, investigating, onInvestigate }) {
  return (
    <div className="anomaly-card">
      <div className="anomaly-card-top">
        <div className="anomaly-card-name">{a.process_name}</div>
        <span className={`anomaly-type-label anomaly-type-${a.anomaly_type}`}>{a.anomaly_type}</span>
      </div>
      <div className="anomaly-card-meta">
        <span>CPU {a.cpu_pct != null ? a.cpu_pct.toFixed(1) : '—'}%</span>
        <span>MEM {a.mem_pct != null ? a.mem_pct.toFixed(2) : '—'}%</span>
        <span>{a.consecutive_count * 2}s</span>
      </div>
      <button
        className="btn btn-primary btn-sm btn-full"
        onClick={() => onInvestigate(a)}
        disabled={investigating !== null}
      >
        {investigating === a.id ? 'Investigating…' : 'Investigate'}
      </button>
    </div>
  );
}

const SEVERITY_ORDER = ['HIGH', 'MEDIUM', 'LOW'];

export default function AnomalyFeed({ anomalies, investigating, onInvestigate, onClear }) {
  const groups = groupBySeverity(anomalies);

  return (
    <div className="panel">
      <div className="panel-title-row">
        <div className="panel-title">Active Anomalies</div>
        <button className="btn btn-danger btn-sm" onClick={onClear}>Clear</button>
      </div>
      {anomalies.length === 0 && (
        <div className="empty">No anomalies detected.</div>
      )}
      {SEVERITY_ORDER.map((sev) =>
        groups[sev].length === 0 ? null : (
          <div key={sev} className="severity-group">
            <div className={`severity-label severity-${sev.toLowerCase()}`}>{sev}</div>
            {groups[sev].map((a) => (
              <AnomalyCard
                key={a.id}
                a={a}
                investigating={investigating}
                onInvestigate={onInvestigate}
              />
            ))}
          </div>
        )
      )}
    </div>
  );
}
