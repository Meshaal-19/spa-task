import { useState, useEffect } from 'react';
import { getProcesses, getAnomalies, postInvestigate, clearAnomalies, clearToken } from './api';
import ProcessTable from './ProcessTable';
import AnomalyFeed from './AnomalyFeed';
import InvestigationPanel from './InvestigationPanel';
import CpuChart from './CpuChart';

export default function Dashboard({ onLogout }) {
  const [processes, setProcesses] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [investigating, setInvestigating] = useState(null);
  const [result, setResult] = useState(null);
  const [processHistory, setProcessHistory] = useState({});

  useEffect(() => {
    const tick = async () => {
      try {
        const procs = await getProcesses();
        setProcesses(procs);
        const top5 = [...procs].sort((a, b) => b.cpu_pct - a.cpu_pct).slice(0, 8);
        setProcessHistory((prev) => {
          const next = {};
          top5.forEach((p) => {
            const key = `${p.name}:${p.pid}`;
            next[key] = [...(prev[key] || []), Math.min(p.cpu_pct, 100)].slice(-30);
          });
          return next;
        });
      } catch (_) {}
    };
    tick();
    const id = setInterval(tick, 2000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const tick = async () => { try { setAnomalies(await getAnomalies()); } catch (_) {} };
    tick();
    const id = setInterval(tick, 3000);
    return () => clearInterval(id);
  }, []);

  async function handleInvestigate(anomaly) {
    setInvestigating(anomaly.id);
    setResult(null);
    try {
      const inv = await postInvestigate(anomaly.id);
      setResult({ ...inv, process_name: anomaly.process_name, pid: anomaly.pid });
    } catch (err) {
      alert(`Investigation failed: ${err.message}`);
    } finally {
      setInvestigating(null);
    }
  }

  async function handleClearAnomalies() {
    try {
      await clearAnomalies();
      setAnomalies(await getAnomalies());
    } catch (err) {
      alert(`Clear failed: ${err.message}`);
    }
  }

  function handleLogout() {
    clearToken();
    onLogout();
  }

  const anomalyPids = new Set(anomalies.map((a) => a.pid));

  return (
    <div className="dashboard">
      <header className="dash-header">
        <h1>ProcessAI</h1>
        <button className="btn btn-ghost" onClick={handleLogout}>Sign out</button>
      </header>
      <CpuChart processHistory={processHistory} />
      <div className="dash-body">
        <div className="dash-left">
          <ProcessTable processes={processes} anomalyPids={anomalyPids} />
        </div>
        <div className="dash-right">
          <AnomalyFeed
            anomalies={anomalies}
            investigating={investigating}
            onInvestigate={handleInvestigate}
            onClear={handleClearAnomalies}
          />
          {result && <InvestigationPanel result={result} />}
        </div>
      </div>
    </div>
  );
}
