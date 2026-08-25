function stripFences(str) {
  if (!str) return str;
  return str.replace(/^```(?:json)?\s*/m, '').replace(/\s*```\s*$/m, '').trim();
}

function parseResult(raw) {
  if (!raw) return {};
  try {
    return JSON.parse(stripFences(raw));
  } catch (_) {
    return {};
  }
}

const TRIAGE_MODEL = "meta-llama/llama-3.1-8b-instruct:free";
const DEEP_MODEL = "claude-haiku-4-5";

function modelLabel(modelUsed) {
  if (!modelUsed) return null;
  if (modelUsed === TRIAGE_MODEL) return { text: "Triage only · Llama 3.1 8B", deep: false };
  if (modelUsed === DEEP_MODEL)   return { text: "Full investigation · Claude Haiku", deep: true };
  return { text: modelUsed, deep: false };
}

export default function InvestigationPanel({ result }) {
  const parsed = parseResult(result.findings);
  const findings = parsed.findings ?? result.findings;
  const recommendation = parsed.recommendation ?? result.recommendation;
  const confidence = parsed.confidence ?? result.confidence ?? 0;
  const pct = Math.round(confidence * 100);
  const label = modelLabel(result.model_used);

  return (
    <div className="panel investigation-panel">
      <div className="panel-title">Investigation Result</div>
      {result.process_name && (
        <div className="inv-process">{result.process_name} <span className="mono">PID {result.pid}</span></div>
      )}
      {label && (
        <div className={`model-tag ${label.deep ? 'model-tag-deep' : 'model-tag-triage'}`}>{label.text}</div>
      )}
      <div className="inv-label">Findings</div>
      <div className="inv-text">{findings || 'No findings recorded.'}</div>
      <div className="inv-label">Recommendation</div>
      <div className="inv-text">{recommendation || 'No recommendation.'}</div>
      <div className="inv-label">Confidence</div>
      <div className="confidence-row">
        <span className="confidence-pct">{pct}%</span>
        <div className="bar-track">
          <div className="bar-fill" style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  );
}
