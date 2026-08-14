import React from 'react';

const SYSTEM_PROCS = new Set([
  'svchost.exe', 'lsass.exe', 'csrss.exe', 'winlogon.exe', 'System',
  'Registry', 'smss.exe', 'wininit.exe', 'services.exe', 'explorer.exe',
  'dwm.exe', 'taskhostw.exe',
]);

const BROWSER_PROCS = new Set([
  'chrome.exe', 'firefox.exe', 'msedge.exe', 'brave.exe', 'opera.exe', 'iexplore.exe',
]);

function getCategory(name) {
  if (SYSTEM_PROCS.has(name)) return 'SYSTEM';
  if (BROWSER_PROCS.has(name)) return 'BROWSER';
  return 'USER APPS';
}

const CATEGORY_ORDER = [
  { key: 'SYSTEM',   label: 'SYSTEM PROCESSES' },
  { key: 'BROWSER',  label: 'BROWSER' },
  { key: 'USER APPS', label: 'USER APPS' },
];

function ProcessRow({ p, anomalyPids }) {
  return (
    <tr className={anomalyPids.has(p.pid) ? 'row-anomaly' : ''}>
      <td className="mono">{p.pid}</td>
      <td className="proc-name-cell">{p.name}</td>
      <td className={p.cpu_pct > 60 ? 'val-high mono' : 'mono'}>{p.cpu_pct.toFixed(1)}</td>
      <td className="mono">{p.mem_pct.toFixed(2)}</td>
    </tr>
  );
}

export default function ProcessTable({ processes, anomalyPids }) {
  const groups = { SYSTEM: [], BROWSER: [], 'USER APPS': [] };
  for (const p of processes) groups[getCategory(p.name)].push(p);

  return (
    <div className="panel">
      <div className="panel-title">Live Processes</div>
      <div className="table-scroll">
        <table className="proc-table">
          <thead>
            <tr>
              <th>PID</th>
              <th>Name</th>
              <th>CPU %</th>
              <th>MEM %</th>
            </tr>
          </thead>
          <tbody>
            {processes.length === 0 && (
              <tr>
                <td colSpan={4} className="empty-cell">Waiting for data…</td>
              </tr>
            )}
            {CATEGORY_ORDER.map(({ key, label }) =>
              groups[key].length === 0 ? null : (
                <React.Fragment key={key}>
                  <tr className="proc-category-header">
                    <td colSpan={4}>{label}</td>
                  </tr>
                  {groups[key].map((p) => (
                    <ProcessRow key={p.pid} p={p} anomalyPids={anomalyPids} />
                  ))}
                </React.Fragment>
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
