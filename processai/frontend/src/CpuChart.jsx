import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

const COLORS = ['#dc2626', '#0d9488', '#d97706', '#7c3aed', '#2563eb'];

export default function CpuChart({ processHistory }) {
  const keys = Object.keys(processHistory);
  if (keys.length === 0) return null;

  const maxLen = Math.max(...keys.map((k) => processHistory[k].length));
  const data = Array.from({ length: maxLen }, (_, i) => {
    const point = { i };
    keys.forEach((k) => {
      point[k] = processHistory[k][i] ?? null;
    });
    return point;
  });

  return (
    <div className="chart-panel">
      <div className="chart-title">Live CPU Usage</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <XAxis dataKey="i" hide />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} tickLine={false} axisLine={false} />
          <Tooltip
            formatter={(value, name) => [`${value != null ? value.toFixed(1) : '—'}%`, name]}
            contentStyle={{ fontSize: 12, border: '1px solid #e2e8f0', borderRadius: 6 }}
            labelFormatter={() => ''}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            formatter={(value) => value.split(':')[0]}
          />
          {keys.map((k, i) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              name={k}
              stroke={COLORS[i % COLORS.length]}
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
